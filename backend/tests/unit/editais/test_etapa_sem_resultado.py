"""A Etapa que o fluxo exige e que não se consolida (046, `FR-746` a `FR-749`, `FR-751`, `SC-275`).

**O `RC-29` da auditoria de consolidação.** Uma Etapa com duas avaliações por inscrição, ou
eliminatória e pontuada sem nota mínima, ou decisória e não eliminatória, publicava sem achado
nenhum — e a consolidação recusava a Etapa inteira depois, sobre um ato que não se desfaz.

**A tabela-verdade é a da regra, e não uma cópia dela** (`FR-747`). Cada caso abaixo pergunta a
`impedimento_da_regra` se a consolidação recusaria a Etapa, e afirma que a publicação acusa **se,
e só se**, ela recusaria e o fluxo publicado exige o Resultado. Um caso escrito à mão ("duas
avaliações impede") passaria mesmo com a publicação reescrevendo a regra — que é o defeito que
este arquivo existe para impedir.
"""

import pytest

from processo_seletivo.editais.domain.validation import (
    ATO_DE_PUBLICACAO,
    ATO_DE_RETIFICACAO,
    Severity,
    blocking_findings,
    validate_for_publication,
)
from processo_seletivo.resultados.domain.regra import impedimento_da_regra
from tests.unit.editais.test_executabilidade import CORTE, METODO, de_sorteio, marco, perfil

ETAPA = "aaaaaaaa-0000-4000-8000-0000000046e1"
OUTRA = "aaaaaaaa-0000-4000-8000-0000000046e2"
IMPEDE = "stage_result_unreachable"
AVISA = "stage_without_result"

#: As formas da Etapa, pela razão que a consolidação daria — e a consolidável, que é a contraprova.
FORMAS = {
    "consolidavel": {"forma": "PONTUADA", "eliminatory": False, "minimumScore": "60.0000"},
    "duas_avaliacoes": {
        "forma": "PONTUADA",
        "eliminatory": False,
        "minimumScore": "60.0000",
        "evaluationsPerRegistration": 2,
    },
    "pontuada_eliminatoria_sem_minima": {
        "forma": "PONTUADA",
        "eliminatory": True,
        "minimumScore": None,
    },
    "decisoria_nao_eliminatoria": {
        "forma": "DECISORIA",
        "eliminatory": False,
        "minimumScore": None,
        "rotuloFavoravel": "Apto",
        "rotuloDesfavoravel": "Inapto",
    },
}


def _etapa(identidade, nome, **declaracao):
    return {
        "id": identidade,
        "name": nome,
        "order": 1,
        "weight": "1.0000",
        "classificatory": True,
        "scheduleEventId": None,
        "maximumScore": None,
        "rotuloFavoravel": None,
        "rotuloDesfavoravel": None,
        **declaracao,
    }


def _conteudo(forma, situacao):
    """A Etapa em teste, e um Perfil que a exige — ou não — conforme a situação."""
    etapa = _etapa(ETAPA, "Prova de títulos", **FORMAS[forma])
    outra = _etapa(OUTRA, "Entrevista", forma="PONTUADA", eliminatory=False, minimumScore=None)
    raiz = {}
    # O marco que não referencia a Etapa em teste: enumera a outra e corta sem governar nada.
    marcos = [marco(stages=[OUTRA], cutRule=dict(CORTE, governedStage="NONE"))]
    if situacao == "eliminatoria":
        etapa["eliminatory"] = True
    elif situacao == "enumerada":
        marcos = [marco(stages=[ETAPA, OUTRA], cutRule=dict(CORTE, governedStage="NONE"))]
    elif situacao == "governada":
        marcos = [marco(stages=[OUTRA], cutRule=dict(CORTE, governedStage=ETAPA))]
    elif situacao == "habilitacao_propria":
        marcos = [
            de_sorteio(
                stages=[OUTRA],
                drawMethod={**METODO, "qualifyingStageId": ETAPA},
                cutRule=dict(CORTE, governedStage="NONE"),
            )
        ]
    elif situacao == "habilitacao_comum":
        marcos = [
            de_sorteio(stages=[OUTRA], drawMethod=None, cutRule=dict(CORTE, governedStage="NONE"))
        ]
        raiz["drawMethod"] = {**METODO, "qualifyingStageId": ETAPA}
    return {
        "title": "Edital 46/2026",
        "description": "Seleção simplificada.",
        "schedule": [{"id": "aaaaaaaa-0000-4000-8000-0000000046e9", "type": "INSCRICAO"}],
        "stages": [etapa, outra],
        "profiles": [perfil(classificationMilestones=marcos)],
        **raiz,
    }


def _da_etapa(conteudo, ato=ATO_DE_PUBLICACAO):
    return [
        achado
        for achado in validate_for_publication(conteudo, ato=ato)
        if achado.code in (IMPEDE, AVISA) and ETAPA in achado.path
    ]


SITUACOES = (
    "eliminatoria",
    "enumerada",
    "governada",
    "habilitacao_propria",
    "habilitacao_comum",
    "nenhuma",
)


@pytest.mark.parametrize("situacao", SITUACOES)
@pytest.mark.parametrize("forma", list(FORMAS))
def test_a_publicacao_acusa_se_e_so_se_a_consolidacao_recusaria(forma, situacao):
    """`SC-275`: impede quando a regra recusa e o Resultado é exigido; avisa quando só recusa."""
    conteudo = _conteudo(forma, situacao)
    etapa = conteudo["stages"][0]
    recusaria = impedimento_da_regra(etapa) is not None
    # Exigida pelo marco que a referencia, ou pelo próprio caráter eliminatório — que a Etapa
    # pontuada sem nota mínima tem por definição, e por isso nunca fica "sem consumidor".
    exigida = situacao != "nenhuma" or etapa["eliminatory"]

    codigos = {achado.code for achado in _da_etapa(conteudo)}

    if not recusaria:
        assert codigos == set(), "Cenário B: Etapa consolidável não recebe achado desta família"
    elif exigida:
        assert codigos == {IMPEDE}
    else:
        assert codigos == {AVISA}


def test_a_etapa_sem_efeito_decidido_e_fora_de_todo_marco_publica_com_aviso():
    """A recusa da `013` de 03/09 (`FR-047`): decisória não eliminatória não é proibida por si."""
    conteudo = _conteudo("decisoria_nao_eliminatoria", "nenhuma")

    achados = _da_etapa(conteudo)

    assert [achado.severity for achado in achados] == [Severity.WARNING]
    assert not [
        a for a in blocking_findings(validate_for_publication(conteudo)) if a.code == IMPEDE
    ]


def test_a_frase_e_a_da_regra_e_nomeia_etapa_consumidor_e_onde_corrigir():
    """`FR-749` e `SC-280`: a entidade, o que falta, por que impede, e em que etapa se corrige."""
    conteudo = _conteudo("duas_avaliacoes", "enumerada")
    _, motivo = impedimento_da_regra(conteudo["stages"][0])

    achado = _da_etapa(conteudo)[0]

    assert "Prova de títulos" in achado.message, "a entidade, pelo nome publicado"
    assert motivo in achado.message, "o que falta, na frase da consolidação e sem reescrita"
    assert "CLASS-TUT" in achado.message, "quem precisa do Resultado"
    assert "etapa Etapas" in achado.message and "Classificação" in achado.message
    assert achado.path == f"/stages/id={ETAPA}"


def test_a_eliminatoria_diz_que_ninguem_seria_eliminado():
    achado = _da_etapa(_conteudo("pontuada_eliminatoria_sem_minima", "nenhuma"))[0]

    assert achado.code == IMPEDE
    assert "ninguém é eliminado por ela" in achado.message
    assert "Classificação" not in achado.message, "a correção é da própria Etapa"


@pytest.mark.parametrize("forma", [f for f in FORMAS if f != "consolidavel"])
def test_na_retificacao_e_sempre_advertencia(forma):
    """`FR-751`: o acervo continua retificável, e quem confirma o ato lê o que a Etapa não terá."""
    for situacao in SITUACOES:
        achados = _da_etapa(_conteudo(forma, situacao), ato=ATO_DE_RETIFICACAO)
        if impedimento_da_regra(_conteudo(forma, situacao)["stages"][0]) is None:
            continue
        assert [achado.code for achado in achados] == [AVISA], situacao
        assert achados[0].severity == Severity.WARNING


def test_os_dois_codigos_nunca_saem_juntos_para_a_mesma_etapa():
    """`R-3`: dois códigos, e cada ato emite um deles — a subtração da Retificação não confunde."""
    for forma in FORMAS:
        for situacao in SITUACOES:
            for ato in (ATO_DE_PUBLICACAO, ATO_DE_RETIFICACAO):
                codigos = [achado.code for achado in _da_etapa(_conteudo(forma, situacao), ato)]
                assert len(codigos) <= 1, (forma, situacao, ato, codigos)


@pytest.mark.parametrize(
    "forma, situacao, ato, onde",
    [
        # Na publicação, só a Etapa que nada exige recebe aviso — as outras são recusa.
        ("decisoria_nao_eliminatoria", "nenhuma", ATO_DE_PUBLICACAO, "corrija-a na etapa Etapas"),
        # Na Retificação, toda Etapa que não se consolida recebe aviso, exigida ou não.
        ("decisoria_nao_eliminatoria", "nenhuma", ATO_DE_RETIFICACAO, "retifique a própria Etapa"),
        ("duas_avaliacoes", "enumerada", ATO_DE_RETIFICACAO, "retifique a própria Etapa"),
    ],
)
def test_o_aviso_tambem_diz_os_quatro_elementos(forma, situacao, ato, onde):
    """`FR-749` e `SC-280` valem para o aviso, e não só para a recusa.

    A confirmação da Retificação exibe só a frase: o caminho do achado não chega a quem lê, e um
    aviso que não diz onde se corrige deixa a pessoa com o problema e sem o caminho. Na Retificação
    não há assistente, e a enumeração do marco não se retifica — o caminho é a própria Etapa.
    """
    conteudo = _conteudo(forma, situacao)
    _, motivo = impedimento_da_regra(conteudo["stages"][0])
    avisos = [achado for achado in _da_etapa(conteudo, ato) if achado.code == AVISA]
    assert len(avisos) == 1, "a premissa: nesta combinação o ato avisa, e não recusa"

    frase = avisos[0].message
    assert "Prova de títulos" in frase, "a entidade"
    assert motivo in frase, "o que falta, na frase da consolidação"
    assert "Nada neste Edital depende dele" in frase or "CLASS-TUT" in frase, "por que importa"
    assert onde in frase, "e onde se corrige"
