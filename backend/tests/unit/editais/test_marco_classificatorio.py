"""O marco só publica se o que ele aponta existir e puder ser apontado (015, D-001).

Três recusas, e as três dependem do **conteúdo inteiro** — por isso vivem em
`validate_for_publication`, e não na validação de elaboração do Perfil, que enxerga só o Perfil.

A terceira é a que mais importa para a leitura da feature: é **aqui** que o critério pendurado é
impedido. Uma Retificação que remova a Etapa enumerada sem ajustar o marco não publica, e por isso
"critério apontando Etapa removida" não é estado que alguma tela precise tratar depois — o que
sobra como caso real de não recomputabilidade é a remoção do **marco** (FR-040, FR-043).
"""

import pytest

from processo_seletivo.editais.domain.validation import blocking_findings, validate_for_publication
from tests.fixtures.snapshot import ETAPA, FATO, PERFIL, conteudo_normativo

MARCO = "00000000-0000-0000-0000-000000000541"
CRITERIO = "00000000-0000-0000-0000-000000000551"


def etapa(identificador, *, classificatory):
    return {
        "id": identificador,
        "name": "Prova",
        "order": 1,
        "weight": "1.0000",
        "eliminatory": False,
        "classificatory": classificatory,
        "minimumScore": None,
        "evaluationsPerRegistration": 1,
        "maximumScore": None,
        "forma": "PONTUADA",
        "rotuloFavoravel": None,
        "rotuloDesfavoravel": None,
        "scheduleEventId": None,
    }


def criterio(**sobrescrever):
    base = {
        "id": CRITERIO,
        "order": 1,
        "type": "MAIOR_PONTUACAO_NA_ETAPA",
        "parameters": {"stageId": ETAPA["A"]},
        "whenMissing": "ULTIMO_NO_CRITERIO",
    }
    return {**base, **sobrescrever}


def conteudo_com_marco(*, classificatory=True, criterios=None, etapas_do_marco=None):
    """Conteúdo publicável com uma Etapa e um marco que a enumera."""
    conteudo = conteudo_normativo()
    conteudo["stages"] = [etapa(ETAPA["A"], classificatory=classificatory)]
    perfil = next(item for item in conteudo["profiles"] if item["id"] == PERFIL["B"])
    perfil["classificationMilestones"] = [
        {
            "id": MARCO,
            "code": "FINAL",
            "name": "Classificação final",
            "stages": [ETAPA["A"]] if etapas_do_marco is None else etapas_do_marco,
            "operation": "SOMA_PONDERADA",
            "normalization": "NENHUMA",
            "rounding": {},
            "tiebreakers": [criterio()] if criterios is None else criterios,
        }
    ]
    return conteudo


def codigos(conteudo):
    return {achado.code for achado in blocking_findings(validate_for_publication(conteudo))}


def test_o_marco_bem_formado_publica():
    """A contraprova: sem ela, os três testes abaixo passariam por acidente."""
    assert codigos(conteudo_com_marco()) == set()


def test_a_etapa_nao_classificatoria_e_recusada():
    """O Edital declarou que ela não classifica; contá-la seria o sistema contradizendo o Edital."""
    assert "milestone_stage_not_classificatory" in codigos(conteudo_com_marco(classificatory=False))


def test_a_etapa_inexistente_e_recusada():
    assert "milestone_stage_missing" in codigos(conteudo_com_marco(etapas_do_marco=[ETAPA["B"]]))


def test_o_criterio_sem_comportamento_para_valor_ausente_e_recusado():
    """O silêncio não vira zero, não vira último lugar e não vira critério pulado (FR-018)."""
    assert "tiebreaker_missing_behaviour" in codigos(
        conteudo_com_marco(criterios=[criterio(whenMissing="")])
    )


@pytest.mark.parametrize(
    ("parametros", "esperado"),
    [
        ({"stageId": ETAPA["B"]}, "tiebreaker_stage_missing"),
        ({"factId": "00000000-0000-0000-0000-0000000005ff"}, "tiebreaker_fact_missing"),
    ],
)
def test_o_criterio_que_aponta_o_que_nao_existe_e_recusado(parametros, esperado):
    assert esperado in codigos(conteudo_com_marco(criterios=[criterio(parameters=parametros)]))


def test_o_criterio_que_aponta_fato_declarado_do_proprio_perfil_publica():
    """A contraprova do anterior: o fato existe no Perfil, e o critério o alcança."""
    conteudo = conteudo_com_marco(
        criterios=[criterio(type="MAIOR_VALOR_DE_FATO", parameters={"factId": FATO["NASCIMENTO"]})]
    )

    assert codigos(conteudo) == set()
