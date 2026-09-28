"""Um Perfil publicado ganha a Modalidade que faltava (048, US1, FR-777 a FR-782, a `D-G5`).

Até a 048 a tela dizia que Modalidades "ainda não são definidas por aqui", e o domínio já aceitava o
acréscimo pela API: faltava a porta. A Modalidade entra com os campos da composição e com as duas
decisões que só se tomam no mesmo ato — ser a ampla do Perfil, ou, sendo cota, ter as suas vagas —,
e a validação é a da composição, ao conferir e de novo no ato.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.interface.retificacao import campos_editaveis, diferencas
from processo_seletivo.publicacoes.application.retificacoes import advertencias_do_ato
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from tests.fixtures.publicacao import publish_original
from tests.fixtures.snapshot import rascunho_completo
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

NOVA = "00000000-0000-4000-8000-000000048101"


def _publicar(api_client, manager_headers, process_payload, rascunho=None):
    edital = publish_original(
        api_client,
        manager_headers,
        process_payload,
        draft=rascunho or rascunho_completo(),
        anexos=1,
    )
    return edital, VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


@pytest.fixture
def publicado(api_client, manager_headers, process_payload):
    return _publicar(api_client, manager_headers, process_payload)


def _perfil(conteudo):
    """O Perfil principal da fixture máxima: o que declara Modalidades."""
    return next(p for p in conteudo["profiles"] if p.get("competitionModalities"))


def _formulario(vigente, **linha):
    grupos = campos_editaveis(vigente.content)
    enviados = {"base": str(vigente.id)}
    enviados |= {f"campo:{c['referencia']}": c["valor"] for g in grupos for c in g["campos"]}
    enviados |= {f"novo-modalidade-0-{chave}": valor for chave, valor in linha.items()}
    return enviados


def _linha(vigente, **alteracoes):
    return {
        "id": NOVA,
        "profileId": _perfil(vigente.content)["id"],
        "code": "EP",
        "name": "Escola pública",
        **alteracoes,
    }


def test_a_frase_antiga_saiu_e_o_botao_chegou(client, seletor_ligado, publicado):
    edital, _ = publicado
    identificar(client, "ana.elaboradora", ["elaborador"])
    destino = reverse("interface:fragmento-retificacao-modalidade", args=[edital.id])

    tela = client.get(reverse("interface:retificar", args=[edital.id])).content.decode()
    fragmento = client.get(destino)

    assert "ainda não são definidas por aqui" not in tela
    assert "Acrescentar Modalidade de Concorrência" in tela
    assert destino in tela
    assert fragmento.status_code == 200
    corpo = fragmento.content.decode()
    assert re.search(r'type="checkbox"[^>]*name="novo-modalidade-[^"]+-general"', corpo, re.S)
    assert "competitionModalities" not in corpo, "o caminho normativo não chega ao HTML (FR-019)"


def test_o_fragmento_oferece_os_perfis_vigentes(publicado):
    from processo_seletivo.interface.retificacao import opcoes_da_modalidade_nova

    _, vigente = publicado

    assert {valor for valor, _ in opcoes_da_modalidade_nova(vigente.content)["profileId"]} == {
        perfil["id"] for perfil in vigente.content["profiles"]
    }


def test_a_ampla_acrescentada_emite_a_modalidade_e_a_declaracao(publicado):
    _, vigente = publicado
    perfil = _perfil(vigente.content)["id"]
    dados = _formulario(vigente, **_linha(vigente, code="AMP", name="Ampla", general="1"))

    primeira, resumo = diferencas(vigente.content, dados)
    segunda, _ = diferencas(vigente.content, dados)

    assert primeira == segunda, "conferir e confirmar produzem o mesmo ato"
    assert [(a["operation"], a["targetPath"]) for a in primeira] == [
        ("ADD", f"/profiles/id={perfil}/competitionModalities/-"),
        ("REPLACE", f"/profiles/id={perfil}/generalCompetitionModalityId"),
    ]
    assert primeira[0]["newValue"] == {
        "id": NOVA,
        "code": "AMP",
        "name": "Ampla",
        "description": "",
        "normativeRule": None,
    }
    assert primeira[1]["newValue"] == NOVA
    # FR-800
    assert [(linha["rotulo"], linha["antes"], linha["depois"]) for linha in resumo] == [
        ("Acréscimo", "—", "AMP — Ampla"),
        ("Ampla concorrência do Perfil", "—", "Ampla"),
    ]


def test_a_cota_acrescentada_com_vagas_leva_a_propria_linha(publicado):
    _, vigente = publicado
    perfil = _perfil(vigente.content)["id"]
    dados = _formulario(
        vigente,
        **_linha(
            vigente,
            foundation="Lei 12.711/2012",
            version="2023",
            percentage="10",
            immediateVacancies="0",
        ),
    )

    primeira, resumo = diferencas(vigente.content, dados)
    segunda, _ = diferencas(vigente.content, dados)

    assert primeira == segunda, "as identidades derivadas não mudam entre as fases"
    modalidade, linha = primeira
    assert modalidade["targetPath"] == f"/profiles/id={perfil}/competitionModalities/-"
    regra = modalidade["newValue"]["normativeRule"]
    assert regra["foundation"] == "Lei 12.711/2012"
    assert regra["percentage"] == "10.0000"
    # Os quatro parâmetros opacos nascem vazios, como o modelo os cria na composição.
    assert all(regra[c] == {} for c in ("calculation", "rounding", "distribution", "callRules"))
    assert linha == {
        "targetPath": f"/profiles/id={perfil}/vacancyTable/-",
        "operation": "ADD",
        "newValue": {
            "id": linha["newValue"]["id"],
            "modalityId": NOVA,
            "immediateVacancies": 0,
        },
    }
    assert [linha_["depois"] for linha_ in resumo] == ["EP — Escola pública", "0 vaga(s)"]


@pytest.mark.parametrize(
    ("alteracoes", "trecho"),
    [
        ({"general": "1", "immediateVacancies": "2"}, "não tem linha própria"),
        ({"code": "AC"}, "não podem se repetir"),
        ({"name": ""}, "informe a denominação"),
        ({"foundation": "Lei 12.711/2012"}, "precisa da versão"),
        ({"version": "2023", "percentage": "150"}, "fundamento"),
        ({"profileId": ""}, "a que Perfil"),
    ],
)
def test_ao_conferir_a_recusa_e_a_da_composicao(publicado, alteracoes, trecho):
    _, vigente = publicado
    codigos = {m["code"] for m in _perfil(vigente.content)["competitionModalities"]}
    assert "AC" in codigos, "a contraprova: a fixture tem a Modalidade AC"

    with pytest.raises(ValueError, match=trecho):
        diferencas(vigente.content, _formulario(vigente, **_linha(vigente, **alteracoes)))


def test_a_linha_deixada_em_branco_nao_acrescenta_nada(publicado):
    _, vigente = publicado

    assert diferencas(vigente.content, _formulario(vigente, id=NOVA)) == ([], [])


def _confirmar(client, edital, dados, chave):
    identificar(client, "ana.elaboradora", ["elaborador"])
    return client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **dados,
            "justificativa": "O Edital não publicou esta Modalidade.",
            "confirmar": "1",
            "chave_idempotencia": chave,
        },
    )


def test_a_cota_sem_linha_confirma_com_o_aviso_da_publicacao(client, seletor_ligado, publicado):
    """Cenário 6 da US1: a mesma validação da publicação vale sobre o conteúdo retificado."""
    edital, vigente = publicado

    resposta = _confirmar(client, edital, _formulario(vigente, **_linha(vigente)), "mod-048-01")

    assert resposta.status_code == 302, resposta.content.decode()
    avisos = {item.code for item in advertencias_do_ato(Retificacao.objects.get())}
    assert "vacancy_reserved_list_without_row" in avisos


def test_a_cota_sem_linha_e_recusada_quando_o_corte_deriva_do_quadro(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    rascunho = rascunho_completo()
    for perfil in rascunho["profiles"]:
        for marco in perfil.get("classificationMilestones") or []:
            marco["cutRule"] = {**marco["cutRule"], "targetKind": "FROM_VACANCY_TABLE"}
            marco["cutRule"]["targetCount"] = None
    edital, vigente = _publicar(api_client, manager_headers, process_payload, rascunho)

    corpo = _confirmar(
        client, edital, _formulario(vigente, **_linha(vigente)), "mod-048-02"
    ).content.decode()

    assert not Retificacao.objects.exists()
    assert "deriva o alvo do quadro de vagas, e não há linha" in corpo
    assert "Escola pública" in corpo


def test_confirmada_a_ampla_pela_tela_as_duas_alteracoes_sao_gravadas(
    client, seletor_ligado, publicado
):
    edital, vigente = publicado
    perfil = _perfil(vigente.content)["id"]

    resposta = _confirmar(
        client,
        edital,
        _formulario(vigente, **_linha(vigente, code="AMP", name="Ampla", general="1")),
        "mod-048-03",
    )

    assert resposta.status_code == 302, resposta.content.decode()
    caminhos = set(Retificacao.objects.get().alteracoes.values_list("target_path", flat=True))
    assert caminhos == {
        f"/profiles/id={perfil}/competitionModalities/-",
        f"/profiles/id={perfil}/generalCompetitionModalityId",
    }


def test_a_tela_do_ato_diz_a_linha_do_quadro_acrescentada(client, seletor_ligado, publicado):
    """Achado do percurso pela tela (048): a linha do quadro acrescentada chegava como "—" a quem
    homologa e assina."""
    edital, vigente = publicado
    _confirmar(
        client,
        edital,
        _formulario(vigente, **_linha(vigente, immediateVacancies="0")),
        "mod-048-04",
    )

    corpo = client.get(
        reverse("interface:retificacao-detalhe", args=[Retificacao.objects.get().id])
    ).content.decode()

    assert "0 vaga(s)" in corpo
