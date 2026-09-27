"""A regra de corte nasce pela tela (048, US2, FR-788).

Até a 048, o marco publicado sem regra não oferecia campo nenhum do corte: a lista de alteração só
aparecia com a regra declarada, e três dos seis campos dela não se retificam. A tela do corte
mandava esse marco para a Retificação, e o caminho terminava num beco. O nascimento tem lista
própria, com os seis campos — nascer não é alterar.

O marco sem regra só existe no acervo desde a `046`, e é por `publicar_como_acervo` que ele se
publica aqui.
"""

import pytest
from django.urls import reverse

from processo_seletivo.interface.retificacao import campos_editaveis, diferencas
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from tests.fixtures.legado import publicar_como_acervo
from tests.fixtures.publicacao import publish_original
from tests.fixtures.snapshot import MARCO, rascunho_completo
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

SEIS = [
    "targetKind",
    "targetCount",
    "surplusCount",
    "tieOutcome",
    "governedStage",
    "continuation",
]


@pytest.fixture
def sem_corte(api_client, manager_headers, process_payload):
    rascunho = rascunho_completo()
    for perfil in rascunho["profiles"]:
        for marco in perfil.get("classificationMilestones") or []:
            marco["cutRule"] = None
    edital = publicar_como_acervo(
        api_client, manager_headers, process_payload, draft=rascunho, anexos=1
    )
    return edital, VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def _base_do_marco(conteudo):
    perfil = next(p for p in conteudo["profiles"] if p.get("classificationMilestones"))
    return f"/profiles/id={perfil['id']}/classificationMilestones/id={MARCO}"


def _do_marco(vigente):
    return next(g for g in campos_editaveis(vigente.content) if g["tipo"] == "Marco")


def _do_corte(vigente):
    return [c for c in _do_marco(vigente)["campos"] if "/cutRule/" in c["caminho"]]


def _formulario(vigente, **alteracoes):
    do_formulario = [c for g in campos_editaveis(vigente.content) for c in g["campos"]]
    enviados = {"base": str(vigente.id)}
    enviados |= {f"campo:{c['referencia']}": c["valor"] for c in do_formulario}
    referencia = {c["caminho"]: c["referencia"] for c in do_formulario}
    enviados.update({f"campo:{referencia[c]}": valor for c, valor in alteracoes.items()})
    return enviados


def _regra_inteira(base, etapa="NONE"):
    return {
        f"{base}/cutRule/targetKind": "FIXED",
        f"{base}/cutRule/targetCount": "3",
        f"{base}/cutRule/surplusCount": "1",
        f"{base}/cutRule/tieOutcome": "STRICT",
        f"{base}/cutRule/governedStage": etapa,
        f"{base}/cutRule/continuation": "NONE",
    }


def test_o_marco_sem_regra_oferece_os_seis_campos(sem_corte):
    _, vigente = sem_corte
    do_corte = _do_corte(vigente)

    assert [c["caminho"].rsplit("/", 1)[-1] for c in do_corte] == SEIS
    assert all(c["valor"] == "" for c in do_corte), "nenhum campo de nascimento nasce com valor"
    por_chave = {c["caminho"].rsplit("/", 1)[-1]: c for c in do_corte}
    assert dict(por_chave["targetKind"]["opcoes"]) == {
        "FIXED": "Uma quantidade fixa, publicada abaixo",
        "FROM_VACANCY_TABLE": "Quantas vagas o quadro publicar no recorte",
    }
    assert por_chave["targetKind"]["rotulo_do_vazio"] == (
        "Não declarada — este marco continua sem cortar"
    )
    assert por_chave["governedStage"]["opcoes"][0] == ("NONE", "Não governa Etapa alguma")
    etapas = {e["id"] for e in vigente.content["stages"]}
    assert {i for i, _ in por_chave["governedStage"]["opcoes"][1:]} == etapas


def test_o_marco_com_regra_continua_com_os_tres_campos(
    api_client, manager_headers, process_payload
):
    """Cenário 5 da US2: o que já está declarado não se troca pela lista de nascimento."""
    edital = publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_completo(), anexos=1
    )
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")

    assert [c["caminho"].rsplit("/", 1)[-1] for c in _do_corte(vigente)] == [
        "targetCount",
        "surplusCount",
        "tieOutcome",
    ]


def test_nada_preenchido_nada_nasce(sem_corte):
    _, vigente = sem_corte

    assert diferencas(vigente.content, _formulario(vigente)) == ([], [])


def test_a_regra_inteira_nasce_num_replace_so(sem_corte):
    _, vigente = sem_corte
    base = _base_do_marco(vigente.content)

    alteracoes, resumo = diferencas(vigente.content, _formulario(vigente, **_regra_inteira(base)))

    assert alteracoes == [
        {
            "targetPath": f"{base}/cutRule",
            "operation": "REPLACE",
            "newValue": {
                "targetKind": "FIXED",
                "targetCount": 3,
                "surplusCount": 1,
                "tieOutcome": "STRICT",
                "governedStage": "NONE",
                "continuation": "NONE",
            },
        }
    ]
    # FR-800: uma linha por campo declarado, por extenso, e sem nada antes.
    assert [(linha["rotulo"], linha["antes"], linha["depois"]) for linha in resumo] == [
        ("Quantos progridem", "—", "Uma quantidade fixa, publicada abaixo"),
        ("Alvo (só na quantidade fixa)", "—", "3"),
        ("Suplentes alcançados na mesma faixa", "—", "1"),
        ("Empate na última posição", "—", "A faixa para no alvo"),
        ("Etapa que o corte alimenta", "—", "Não governa Etapa alguma"),
        ("Faixa seguinte", "—", "Não admite: a faixa é o que foi publicado"),
    ]


def _confirmar(client, edital, dados, chave):
    identificar(client, "ana.elaboradora", ["elaborador"])
    return client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **dados,
            "justificativa": "O Edital não declarou a regra de corte deste marco.",
            "confirmar": "1",
            "chave_idempotencia": chave,
        },
    )


def test_a_regra_pela_metade_e_recusada_com_as_mensagens_da_publicacao(
    client, seletor_ligado, sem_corte
):
    edital, vigente = sem_corte
    base = _base_do_marco(vigente.content)

    corpo = _confirmar(
        client,
        edital,
        _formulario(vigente, **{f"{base}/cutRule/targetCount": "3"}),
        "corte-pela-metade-01",
    ).content.decode()

    assert not Retificacao.objects.exists()
    assert "não declara a espécie do alvo" in corpo


def test_a_regra_inteira_e_gravada(client, seletor_ligado, sem_corte):
    edital, vigente = sem_corte
    base = _base_do_marco(vigente.content)

    resposta = _confirmar(
        client, edital, _formulario(vigente, **_regra_inteira(base)), "corte-inteiro-01"
    )

    assert resposta.status_code == 302, resposta.content.decode()
    alteracao = Retificacao.objects.get().alteracoes.get(target_path=f"{base}/cutRule")
    assert alteracao.new_value["targetKind"] == "FIXED"


def test_a_tela_do_ato_diz_a_regra_que_nasce_por_extenso(client, seletor_ligado, sem_corte):
    """FR-800 na tela em que o ato é homologado e assinado: sem nome nem código, o objeto nascido
    chegava como "—" a quem aprova."""
    edital, vigente = sem_corte
    base = _base_do_marco(vigente.content)
    _confirmar(client, edital, _formulario(vigente, **_regra_inteira(base)), "corte-detalhe-01")

    corpo = client.get(
        reverse("interface:retificacao-detalhe", args=[Retificacao.objects.get().id])
    ).content.decode()

    assert "Regra de corte" in corpo
    assert "Quantos progridem: Uma quantidade fixa, publicada abaixo" in corpo
