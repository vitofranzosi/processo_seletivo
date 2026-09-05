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


def etapa(identificador, *, classificatory, weight="1.0000"):
    return {
        "id": identificador,
        "name": "Prova",
        "order": 1,
        "weight": weight,
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


ARREDONDAMENTO = {"scale": 2, "mode": "MEIO_PARA_CIMA"}


def conteudo_com_marco(
    *, classificatory=True, criterios=None, etapas_do_marco=None, rounding=None, peso="1.0000"
):
    """Conteúdo publicável com uma Etapa e um marco que a enumera."""
    conteudo = conteudo_normativo()
    conteudo["stages"] = [etapa(ETAPA["A"], classificatory=classificatory, weight=peso)]
    perfil = next(item for item in conteudo["profiles"] if item["id"] == PERFIL["B"])
    perfil["classificationMilestones"] = [
        {
            "id": MARCO,
            "code": "FINAL",
            "name": "Classificação final",
            "stages": [ETAPA["A"]] if etapas_do_marco is None else etapas_do_marco,
            "operation": "SOMA_PONDERADA",
            "normalization": "NENHUMA",
            "rounding": ARREDONDAMENTO if rounding is None else rounding,
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


# --- a regra precisa estar completa na publicação, e não no cálculo ----------------------------


def test_a_etapa_enumerada_sem_peso_e_recusada():
    """Quem enumera declara o peso: ausência não é equivalência, e o cálculo não a interpreta."""
    assert "milestone_stage_without_weight" in codigos(conteudo_com_marco(peso=None))


@pytest.mark.parametrize(
    "rounding",
    [
        None,
        {},
        {"scale": 2},
        {"mode": "MEIO_PARA_CIMA"},
        {"scale": -1, "mode": "MEIO_PARA_CIMA"},
        {"scale": 7, "mode": "MEIO_PARA_CIMA"},
        {"scale": "2", "mode": "MEIO_PARA_CIMA"},
        {"scale": 2, "mode": "ROUND_HALF_UP"},
        {"scale": 2, "mode": "PARA_CIMA"},
    ],
    ids=[
        "ausente",
        "vazio",
        "sem-modo",
        "sem-escala",
        "escala-negativa",
        "escala-acima-do-teto",
        "escala-texto",
        "grafia-da-biblioteca",
        "modo-inexistente",
    ],
)
def test_o_arredondamento_mal_declarado_e_recusado_na_publicacao(rounding):
    """A recusa é aqui, e não no dia em que alguém executa o marco.

    Se o cálculo escolhesse um padrão, o padrão seria do código e não do Edital. E a grafia da
    biblioteca é recusada de propósito: `ROUND_HALF_UP` é detalhe de implementação, e publicá-lo
    faria a norma depender de como o sistema por acaso arredonda hoje.
    """
    assert "milestone_rounding_invalid" in codigos(
        conteudo_com_marco(rounding={} if rounding is None else rounding)
    )


@pytest.mark.parametrize("escala", [0, 6])
def test_as_escalas_das_pontas_do_intervalo_publicam(escala):
    """Zero porque há Edital que classifica por inteiro; seis é a precisão que a pontuação tem."""
    assert codigos(conteudo_com_marco(rounding={"scale": escala, "mode": "TRUNCAR"})) == set()
