"""Os padrões que valem também para o Edital pequeno (051, US3).

Cada padrão só preenche o vazio, e todos ficam editáveis (FR-915). O que estes casos prendem é o
nascimento — o cartão novo, o texto vazio, o instante não digitado — e a preservação do que já
estava declarado.
"""

import re

import pytest
from django.http import QueryDict
from django.urls import reverse

from processo_seletivo.editais.domain import validation
from processo_seletivo.editais.models.perfis import ModalidadeConcorrencia, RegraNormativa
from processo_seletivo.interface import forms
from processo_seletivo.sorteios.domain import prosa
from tests.fixtures.snapshot import rascunho_completo
from tests.interface.test_aplicar_a_todos import (
    P1,
    _perfis_no_formulario,
    _url,
)

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def _dados(**campos):
    dados = QueryDict(mutable=True)
    for chave, valor in campos.items():
        if isinstance(valor, list):
            dados.setlist(chave, valor)
        else:
            dados[chave] = valor
    return dados


# ---- o corte do marco único (FR-927) ------------------------------------------------------------


def _fragmento_do_marco(client, edital, **consulta):
    url = reverse("interface:fragmento-marco", args=[P1])
    return client.get(url, {"edital": str(edital.id), **consulta}).content.decode()


def test_o_marco_unico_nasce_com_o_corte_padrao(client, tres_perfis):
    corpo = _fragmento_do_marco(client, tres_perfis)

    assert re.search(r'<option value="FROM_VACANCY_TABLE" selected>', corpo)
    assert re.search(
        r'-cutGovernedStage"[^>]*>\s*<option value="">[^<]*</option>\s*'
        r'<option value="NONE" selected>',
        corpo,
    )
    # O empate e a faixa seguinte continuam perguntados: não têm padrão (014, FR-182, FR-226).
    assert re.search(r'<option value="ADMITS_SURPLUS" >|<option value="ADMITS_SURPLUS">', corpo)
    assert not re.search(r'value="(ADMITS_SURPLUS|STRICT|ALLOWED)"\s*selected', corpo)


def test_o_segundo_marco_na_tela_nasce_sem_corte(client, tres_perfis):
    corpo = _fragmento_do_marco(client, tres_perfis, **{f"marco-{P1}-0-id": "qualquer"})

    assert not re.search(r'<option value="FROM_VACANCY_TABLE" selected>', corpo)


# ---- o empate que o sorteio não tem (FR-928) ----------------------------------------------------


def _marco_de_sorteio(**corte):
    return {
        "code": "M",
        "orderProduction": "POR_SORTEIO",
        "drawMethod": None,
        "cutRule": {
            "targetKind": "FROM_VACANCY_TABLE",
            "surplusCount": 0,
            "governedStage": "NONE",
            "continuation": "ALLOWED",
            **corte,
        },
    }


def _codigos(marco):
    return {
        achado.code
        for achado in validation._regra_de_corte_do_marco(
            marco, perfil={}, etapas={}, caminho="/profiles/0/classificationMilestones/0"
        )
    }


def test_o_marco_de_sorteio_publica_sem_o_empate():
    assert "cut_rule_sem_desfecho_de_empate" not in _codigos(_marco_de_sorteio())


def test_o_marco_de_pontuacao_continua_exigindo_o_empate():
    marco = {**_marco_de_sorteio(), "orderProduction": "POR_PONTUACAO"}

    assert "cut_rule_sem_desfecho_de_empate" in _codigos(marco)


def test_o_empate_declarado_fora_do_vocabulario_continua_recusado_no_sorteio():
    assert "cut_rule_sem_desfecho_de_empate" in _codigos(_marco_de_sorteio(tieOutcome="TALVEZ"))


def test_o_cartao_de_sorteio_nao_pergunta_o_empate_e_preserva_o_declarado(client, tres_perfis):
    url = reverse("interface:fragmento-marco-recomposto", args=[P1, 0])
    corpo = client.get(
        url,
        {
            "edital": str(tres_perfis.id),
            f"marco-{P1}-0-id": "m",
            f"marco-{P1}-0-orderProduction": "POR_SORTEIO",
            f"marco-{P1}-0-cutTargetKind": "FROM_VACANCY_TABLE",
            f"marco-{P1}-0-cutTieOutcome": "STRICT",
        },
    ).content.decode()

    assert "Empate na última posição" not in corpo
    assert f'name="marco-{P1}-0-cutTieOutcome" value="STRICT"' in corpo


# ---- o instante do Evento e a prosa gerada (FR-929, FR-930) -------------------------------------


def test_a_prosa_vazia_e_gerada_da_regra_e_a_digitada_vale():
    gerado = forms.metodo_comum_do_formulario(
        _dados(
            **{
                "edital-draw-normalizationRule": "DIGITOS_EM_SEQUENCIA",
                "edital-draw-substitutionRule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
                "edital-draw-substitutionText": "A do sábado seguinte.",
            }
        )
    )

    assert gerado["normalization"]["text"] == prosa.da_regra("DIGITOS_EM_SEQUENCIA")
    assert gerado["substitutionRule"]["text"] == "A do sábado seguinte."


def test_o_instante_escolhido_no_cronograma_e_gravado_e_o_digitado_vale():
    escolhido = "2026-11-20T20:00:00-03:00"

    do_evento = forms.metodo_comum_do_formulario(
        _dados(**{"edital-draw-occurrenceEvent": escolhido})
    )
    digitado = forms.metodo_comum_do_formulario(
        _dados(
            **{
                "edital-draw-occurrenceEvent": escolhido,
                "edital-draw-occurrenceAt": "2026-11-21T20:00:00-03:00",
            }
        )
    )

    assert do_evento["occurrenceAt"] == escolhido
    assert digitado["occurrenceAt"] == "2026-11-21T20:00:00-03:00"


def test_a_classificacao_oferece_os_eventos_do_cronograma(client, tres_perfis):
    client.post(
        _url(tres_perfis, "cronograma"),
        {
            "evento-0-id": "aaaaaaaa-0000-4000-8000-000000051e01",
            "evento-0-type": "SORTEIO",
            "evento-0-description": "Sorteio eletrônico",
            "evento-0-startAt": "2026-11-20T20:00",
        },
    )

    corpo = client.get(_url(tres_perfis)).content.decode()

    assert re.search(
        r'<option value="2026-11-20T20:00:00-03:00">Sorteio eletrônico — 20/11/2026 20:00',
        corpo,
    )


# ---- a Etapa decisória (FR-931) -----------------------------------------------------------------


def test_a_etapa_nova_traz_a_decisoria_eliminatoria(client, tres_perfis):
    url = reverse("interface:fragmento-etapa", args=[tres_perfis.id])

    corpo = client.get(url).content.decode()

    assert re.search(r'name="etapa-\d+-eliminatoryDecisoria"\s*checked', corpo)
    assert not re.search(r'name="etapa-\d+-eliminatory"\s*checked', corpo)


@pytest.mark.parametrize(
    ("campos", "esperado"),
    [
        ({"etapa-0-caraterPorForma": "1", "etapa-0-eliminatoryDecisoria": "on"}, True),
        ({"etapa-0-caraterPorForma": "1", "etapa-0-eliminatory": "on"}, False),
        # Envio de antes das duas caixas: lido como sempre foi.
        ({"etapa-0-eliminatory": "on"}, True),
    ],
)
def test_a_leitura_usa_a_caixa_da_forma_escolhida(campos, esperado):
    (etapa,) = forms.ler_etapas(
        _dados(
            **{"etapa-0-id": "e", "etapa-0-name": "Análise", "etapa-0-forma": "DECISORIA"}, **campos
        )
    )

    assert etapa["eliminatory"] is esperado


# ---- o quadro sugerido e o arredondamento (FR-932, FR-933) --------------------------------------

PPI = {
    "modalidade-0-0-id": "aaaaaaaa-0000-4000-8000-000000051d21",
    "modalidade-0-0-ruleId": "aaaaaaaa-0000-4000-8000-000000051d31",
    "modalidade-0-0-code": "PPI",
    "modalidade-0-0-name": "Pretos, pardos e indígenas",
    "modalidade-0-0-percentage": "25",
    "modalidade-0-0-foundation": "Lei 12.711/2012",
    "modalidade-0-0-version": "2016-12-28",
    "modalidade-0-0-rounding": "PARA_CIMA",
    "perfil-0-immediateVacancies": "7",
}


def test_o_arredondamento_e_gravado_e_volta_na_tela(client, tres_perfis):
    resposta = client.post(_url(tres_perfis, "perfis"), _perfis_no_formulario(**PPI))

    assert resposta.status_code == 302, resposta.content
    regra = RegraNormativa.objects.get(modalidade__perfil_id=P1)
    assert regra.rounding == {"mode": "PARA_CIMA"}
    corpo = client.get(_url(tres_perfis, "perfis")).content.decode()
    assert re.search(r'<option value="PARA_CIMA" selected>A fração vira vaga', corpo)
    assert "25% de 7 = 1,75, sugestão 2" in " ".join(corpo.split())


def test_preencher_pelo_percentual_poe_a_sugestao_e_nao_grava(client, tres_perfis):
    resposta = client.post(
        _url(tres_perfis, "perfis"), {**_perfis_no_formulario(**PPI), "preencher_quadro": "1"}
    )

    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert "1 linha(s) em LP01" in " ".join(corpo.split())
    assert re.search(r'-immediateVacancies"\s+value="2"', corpo)
    assert not ModalidadeConcorrencia.objects.filter(perfil_id=P1).exists()


def test_gravar_os_perfis_preserva_os_campos_da_regra_que_a_tela_nao_desenha(client, tres_perfis):
    client.post(_url(tres_perfis, "perfis"), _perfis_no_formulario(**PPI))
    RegraNormativa.objects.filter(modalidade__perfil_id=P1).update(
        calculation={"base": "vagas"}, call_rules={"ordem": "alternada"}
    )

    resposta = client.post(_url(tres_perfis, "perfis"), _perfis_no_formulario(**PPI))

    assert resposta.status_code == 302, resposta.content
    regra = RegraNormativa.objects.get(modalidade__perfil_id=P1)
    assert regra.calculation == {"base": "vagas"}
    assert regra.call_rules == {"ordem": "alternada"}


def test_o_arredondamento_fora_da_lista_e_preservado(client, tres_perfis):
    client.post(_url(tres_perfis, "perfis"), _perfis_no_formulario(**PPI))
    RegraNormativa.objects.filter(modalidade__perfil_id=P1).update(rounding={"regra": "da API"})
    corpo = client.get(_url(tres_perfis, "perfis")).content.decode()
    assert "Declarado fora da lista — preservado" in corpo

    client.post(
        _url(tres_perfis, "perfis"),
        _perfis_no_formulario(**{**PPI, "modalidade-0-0-rounding": "FORA_DA_LISTA"}),
    )

    assert RegraNormativa.objects.get(modalidade__perfil_id=P1).rounding == {"regra": "da API"}


# ---- quem corta declara como convoca (FR-943) ---------------------------------------------------


def _codigos_da_publicacao(conteudo, **opcoes):
    return {achado.code for achado in validation.validate_for_publication(conteudo, **opcoes)}


def test_perfil_que_corta_sem_forma_de_convocacao_nao_publica():
    conteudo = rascunho_completo()
    conteudo["profiles"][0]["callForm"] = None

    assert "profile_cuts_without_call_form" in _codigos_da_publicacao(conteudo)


def test_com_a_forma_declarada_publica():
    assert "profile_cuts_without_call_form" not in _codigos_da_publicacao(rascunho_completo())


def test_a_retificacao_do_acervo_sem_forma_nao_e_recusada_por_isso():
    conteudo = rascunho_completo()
    conteudo["profiles"][0]["callForm"] = None

    assert "profile_cuts_without_call_form" not in _codigos_da_publicacao(
        conteudo, ato=validation.ATO_DE_RETIFICACAO
    )
