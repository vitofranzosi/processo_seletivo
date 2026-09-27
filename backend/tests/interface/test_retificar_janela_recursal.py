"""O prazo recursal publicado se corrige pela tela (026, US3, FR-307, FR-311).

Governa um **direito com prazo**, e é objeto composto: dois escalares e um valor de lista fechada.
É o canário que obriga o desenho a tratar objeto aninhado e valor fechado — as duas formas que a
justificativa técnica vencida usava como motivo de exclusão.
"""

import pytest
from django.urls import reverse

from processo_seletivo.interface.retificacao import campos_editaveis, diferencas
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from tests.fixtures.publicacao import publish_original
from tests.fixtures.snapshot import MARCO, rascunho_completo
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    return publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_completo(), anexos=1
    )


@pytest.fixture
def vigente(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def _base_do_marco(conteudo):
    perfil = next(p for p in conteudo["profiles"] if p.get("classificationMilestones"))
    return f"/profiles/id={perfil['id']}/classificationMilestones/id={MARCO}"


def campos(vigente, **alteracoes):
    grupos = campos_editaveis(vigente.content)
    do_formulario = [campo for grupo in grupos for campo in grupo["campos"]]
    enviados = {"base": str(vigente.id)}
    enviados |= {f"campo:{campo['referencia']}": campo["valor"] for campo in do_formulario}
    referencia = {campo["caminho"]: campo["referencia"] for campo in do_formulario}
    enviados.update({f"campo:{referencia[c]}": valor for c, valor in alteracoes.items()})
    return enviados


def test_a_tela_oferece_os_tres_campos_da_janela(client, seletor_ligado, edital, vigente):
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(reverse("interface:retificar", args=[edital.id])).content.decode()

    assert "Admite recurso" in corpo
    assert "Prazo em dias" in corpo
    assert "Contagem do prazo" in corpo
    assert "appealWindow" not in corpo, "o caminho normativo não chega ao HTML (FR-019)"


def test_a_unidade_e_escolha_conferida_e_nunca_texto_livre(client, seletor_ligado, edital, vigente):
    """FR-311. Caixa de texto publicaria contagem que o cálculo não interpreta — e o candidato
    leria um prazo que ninguém sabe contar."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    client.get(reverse("interface:retificar", args=[edital.id]))

    grupos = campos_editaveis(vigente.content)
    do_marco = next(g for g in grupos if g["tipo"] == "Marco")
    unidade = next(c for c in do_marco["campos"] if c["caminho"].endswith("/appealWindow/unit"))

    assert unidade["tipo"] == "referencia"
    assert [identificador for identificador, _ in unidade["opcoes"]] == ["DIAS_CORRIDOS"]
    assert unidade["valor"] == "DIAS_CORRIDOS"


def test_corrigir_o_prazo_pela_tela_vira_replace_por_identidade(
    client, seletor_ligado, edital, vigente
):
    """SC-099 — o Edital publicou três dias e a norma institucional exige cinco."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    caminho = f"{_base_do_marco(vigente.content)}/appealWindow/durationDays"

    resposta = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente, **{caminho: "10"}),
            "justificativa": "A norma institucional exige dez dias.",
            "confirmar": "1",
            "chave_idempotencia": "retificar-janela-000001",
        },
    )
    assert resposta.status_code in (200, 302), resposta.content

    alteracao = Retificacao.objects.get().alteracoes.get(target_path=caminho)
    assert alteracao.new_value == 10


def test_unidade_que_o_calculo_nao_interpreta_e_recusada_com_a_razao(
    client, seletor_ligado, edital, vigente
):
    """Um POST fabricado não passa pelo `select`: a tela não é fronteira.

    A conferência acontece na conversão do campo de referência, que já recusa opção fora da lista
    — e a recusa nomeia o campo, em vez de gravar prazo incontável.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    caminho = f"{_base_do_marco(vigente.content)}/appealWindow/unit"

    corpo = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente, **{caminho: "DIAS_UTEIS"}),
            "justificativa": "Tentativa de contar em dias úteis.",
            "confirmar": "1",
            "chave_idempotencia": "retificar-janela-000002",
        },
    ).content.decode()

    assert not Retificacao.objects.exists(), "a unidade inválida foi gravada"
    assert "Contagem do prazo" in corpo


# --------------------------------------------------------------------------------------------
# A janela que nasce (048, US3, FR-786, FR-787, D-003)
# --------------------------------------------------------------------------------------------


@pytest.fixture
def sem_janela(api_client, manager_headers, process_payload):
    rascunho = rascunho_completo()
    for perfil in rascunho["profiles"]:
        for marco in perfil.get("classificationMilestones") or []:
            marco["appealWindow"] = None
    edital = publish_original(
        api_client, manager_headers, process_payload, draft=rascunho, anexos=1
    )
    return edital, VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def _do_marco(vigente):
    return next(g for g in campos_editaveis(vigente.content) if g["tipo"] == "Marco")


def test_sem_janela_a_tela_oferece_so_o_prazo(sem_janela):
    """Cenário 2 da US3: a tela não pergunta se admite — a janela que nasce concede.

    A recusa de *"não admite"* é da API, e está em
    `tests/integration/publicacoes/test_janela_que_nasce_pela_api.py`.
    """
    _, vigente = sem_janela
    da_janela = [c for c in _do_marco(vigente)["campos"] if "/appealWindow/" in c["caminho"]]

    assert [c["caminho"].rsplit("/", 1)[-1] for c in da_janela] == ["durationDays"]
    assert da_janela[0]["valor"] == ""
    assert da_janela[0]["rotulo_do_vazio"] == "Em branco — este marco continua sem prever recurso"


def test_o_prazo_informado_faz_nascer_a_janela_inteira(sem_janela):
    _, vigente = sem_janela
    base = _base_do_marco(vigente.content)

    alteracoes, resumo = diferencas(
        vigente.content, campos(vigente, **{f"{base}/appealWindow/durationDays": "3"})
    )

    assert alteracoes == [
        {
            "targetPath": f"{base}/appealWindow",
            "operation": "REPLACE",
            "newValue": {"admits": True, "unit": "DIAS_CORRIDOS", "durationDays": 3},
        }
    ]
    # FR-800: antes não havia prazo nenhum.
    assert [(linha["antes"], linha["depois"]) for linha in resumo] == [("—", "3")]


def test_em_branco_nenhuma_janela_nasce(sem_janela):
    _, vigente = sem_janela

    assert diferencas(vigente.content, campos(vigente)) == ([], [])


def test_zero_dias_e_recusado_pela_regra_que_ja_existe(client, seletor_ligado, sem_janela):
    edital, vigente = sem_janela
    identificar(client, "ana.elaboradora", ["elaborador"])
    caminho = f"{_base_do_marco(vigente.content)}/appealWindow/durationDays"

    client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente, **{caminho: "0"}),
            "justificativa": "Prazo zero.",
            "confirmar": "1",
            "chave_idempotencia": "retificar-janela-000003",
        },
    )

    assert not Retificacao.objects.exists()


def test_a_janela_nascida_pela_tela_e_gravada(client, seletor_ligado, sem_janela):
    edital, vigente = sem_janela
    identificar(client, "ana.elaboradora", ["elaborador"])
    base = _base_do_marco(vigente.content)

    resposta = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente, **{f"{base}/appealWindow/durationDays": "3"}),
            "justificativa": "O Edital não previu recurso da classificação.",
            "confirmar": "1",
            "chave_idempotencia": "retificar-janela-000004",
        },
    )

    assert resposta.status_code == 302, resposta.content.decode()
    alteracao = Retificacao.objects.get().alteracoes.get(target_path=f"{base}/appealWindow")
    assert alteracao.new_value == {"admits": True, "unit": "DIAS_CORRIDOS", "durationDays": 3}


def test_com_janela_os_tres_campos_continuam(vigente):
    """Cenário 4 da US3: alterar janela que existe segue a regra de hoje."""
    da_janela = [c for c in _do_marco(vigente)["campos"] if "/appealWindow/" in c["caminho"]]

    assert [c["caminho"].rsplit("/", 1)[-1] for c in da_janela] == [
        "admits",
        "durationDays",
        "unit",
    ]
