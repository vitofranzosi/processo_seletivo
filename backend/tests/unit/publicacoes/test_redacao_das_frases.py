"""A redação 2 das frases geradas, variante por variante (069, FR-1360, FR-1361, R-008).

Um caso por linha de `specs/069-edital-linguagem-simples/contracts/redacao.md`. Cada caso diz três
coisas:

- **a frase da redação 2, exata** — a que os documentos compostos depois desta feature imprimem;
- **a frase da redação 1, inalterada** — a de antes, que os atos já publicados continuam dizendo
  (FR-1397) e que as provas da história da `067` e da `068` leem;
- **a nota de equivalência**, na docstring: o que a frase nova preserva da antiga — condição,
  exceção, alcance e consequência —, ou que ela é nova e depende de aprovação (SC-517).

A frase é testada pela função que o compositor usa, e não por uma cópia: a Revisão, a página do ato
e o portal leem as mesmas funções (FR-1364).
"""

from datetime import datetime

import pytest

from processo_seletivo.publicacoes.domain import vocabulario_da_regra as vocabulario
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import (
    REDACAO_1,
    REDACAO_2,
    REDACAO_VIGENTE,
    criterio_com_a_ausencia,
    criterio_por_extenso,
    frase_da_convocacao,
    por_identificador,
)
from processo_seletivo.publicacoes.infrastructure import pdf

ETAPAS = por_identificador(
    [
        {
            "id": "p",
            "name": "Prova de títulos",
            "forma": "PONTUADA",
            "weight": "1.0000",
            "eliminatory": False,
            "classificatory": True,
            "maximumScore": "100.0000",
            "minimumScore": None,
            "evaluationsPerRegistration": 1,
            "scheduleEventId": "ev-p",
        },
        {
            "id": "q",
            "name": "Entrevista",
            "forma": "PONTUADA",
            "weight": "2.0000",
            "eliminatory": True,
            "classificatory": True,
            "maximumScore": "100.0000",
            "minimumScore": "60.0000",
            "evaluationsPerRegistration": 2,
            "scheduleEventId": None,
        },
        {
            "id": "d",
            "name": "Análise documental",
            "forma": "DECISORIA",
            "weight": None,
            "eliminatory": True,
            "classificatory": False,
            "rotuloFavoravel": "Deferida",
            "rotuloDesfavoravel": "Indeferida",
            "scheduleEventId": "ev-d",
        },
    ]
)
FATOS = por_identificador(
    [
        {"id": "nasc", "code": "NASCIMENTO", "type": "DATA", "label": "Data de nascimento"},
        {
            "id": "exp",
            "code": "EXPERIENCIA",
            "type": "INTEIRO",
            "label": "Meses de experiência em tutoria",
        },
    ]
)
METODO = {
    "source": "Loteria Federal",
    "algorithm": "IFES-SORTEIO-SHA256-v1",
    "derivation": "A extração de sábado imediatamente anterior à data publicada do sorteio.",
    "occurrence": "Concurso 6010",
    "occurrenceAt": "2026-11-14T19:00:00-03:00",
    "normalization": {
        "rule": "DIGITOS_EM_SEQUENCIA",
        "text": "Os cinco números sorteados, na ordem dos prêmios, separados por espaço.",
    },
    "substitutionRule": {
        "rule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
        "text": "Não havendo extração na data prevista, vale a extração seguinte da mesma fonte.",
    },
}


def _marco(**campos):
    base = {
        "id": "m",
        "code": "FINAL",
        "name": "Classificação final",
        "orderProduction": "POR_PONTUACAO",
        "operation": "SOMA_PONDERADA",
        "normalization": "NENHUMA",
        "stages": ["p"],
        "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
        "tiebreakers": [],
        "cutRule": None,
        "appealWindow": None,
        "drawMethod": None,
    }
    return {**base, **campos}


def _sorteio(**campos):
    return _marco(
        **{
            "code": "SORTEIO",
            "name": "Classificação por sorteio eletrônico",
            "orderProduction": "POR_SORTEIO",
            "stages": [],
            **campos,
        }
    )


def _corte(**campos):
    return {
        "targetKind": "FIXED",
        "targetCount": 10,
        "surplusCount": 0,
        "tieOutcome": "STRICT",
        "continuation": "NONE",
        "governedStage": "d",
        **campos,
    }


def _snapshot(*marcos, metodo=METODO):
    perfil = {"id": "perfil", "code": "TP-01", "classificationMilestones": list(marcos)}
    return {"drawMethod": metodo, "profiles": [perfil], "stages": list(ETAPAS.values())}, perfil


def test_a_redacao_vigente_e_a_2():
    """O que se compõe a partir desta feature usa a redação 2; a 1 continua alcançável (R-004)."""
    assert (REDACAO_1, REDACAO_2, REDACAO_VIGENTE) == (1, 2, 2)


# ---------------------------------------------------------------------------
# 1. Classificação
# ---------------------------------------------------------------------------


def test_c1_separacao_por_perfil():
    """C1 — o alcance por Perfil se preserva: cada Perfil tem a sua classificação e o seu resultado.

    Sai "marcos", que é palavra do sistema; fica a regra inteira.
    """
    assert pdf.CLASSIFICACAO_SEPARADA == (
        "A classificação é feita separadamente em cada Perfil: cada Perfil tem a sua própria "
        "classificação e o seu próprio resultado."
    )
    assert pdf.MARCOS_SEPARADAMENTE == (
        "Os marcos abaixo se aplicam a cada um desses Perfis separadamente, sobre as inscrições do "
        "próprio Perfil: cada Perfil tem a sua própria classificação e o seu próprio resultado."
    )


def test_c2_ordem_por_sorteio_nao_vira_frase():
    """C2 — a forma da ordem continua dita: pelo título da subseção ("Sorteio") e pela C4."""
    snapshot, perfil = _snapshot(_sorteio())

    assert pdf.frase_da_forma_da_ordem(_sorteio()) == ""
    assert pdf.FORMA_DA_ORDEM["POR_SORTEIO"] == "por sorteio"
    assert pdf.frases_da_ordem(snapshot, perfil, _sorteio()) == [
        "Participam do sorteio todas as inscrições enviadas."
    ]


def test_c3_ordem_por_pontuacao():
    """C3 — a forma da ordem continua dita, agora como frase."""
    assert pdf.frase_da_forma_da_ordem(_marco()) == "A ordem de classificação segue a nota final."
    assert pdf.FORMA_DA_ORDEM["POR_PONTUACAO"] == "pela pontuação combinada das Etapas"


def test_c3_marco_do_acervo_sem_forma_declarada_nao_ganha_a_frase():
    """Marco anterior à `030` não declara a forma; a ausência é a afirmação (032, FR-464)."""
    assert pdf.frase_da_forma_da_ordem(_marco(orderProduction=None)) == ""


def test_c4_todas_as_inscricoes_participam_do_sorteio():
    """C4 — "enviada" é "submetida", na palavra que o teto já usa; quem participa é o mesmo."""
    snapshot, perfil = _snapshot(_sorteio())

    assert pdf.frase_da_habilitacao(snapshot, perfil, _sorteio(), ETAPAS) == (
        "Participam do sorteio todas as inscrições enviadas."
    )
    assert pdf._habilitacao_ao_sorteio(snapshot, perfil, _sorteio(), ETAPAS) == (
        "participam todas as inscrições submetidas"
    )


def test_c5_so_as_habilitadas_na_etapa_participam():
    """C5 — a condição se preserva: só as habilitadas na Etapa declarada."""
    marco = _sorteio(drawMethod={**METODO, "qualifyingStageId": "d"})
    snapshot, perfil = _snapshot(marco)

    assert pdf.frase_da_habilitacao(snapshot, perfil, marco, ETAPAS) == (
        "Participam do sorteio só as inscrições habilitadas na Etapa “Análise documental”."
    )
    assert pdf._habilitacao_ao_sorteio(snapshot, perfil, marco, ETAPAS) == (
        "participam apenas as inscrições habilitadas na Etapa Análise documental"
    )


def test_c6_nota_de_uma_etapa_de_peso_um():
    """C6 — a conta é a mesma: soma de uma parcela de peso 1, sem normalização."""
    marco = _marco()

    assert pdf.frases_da_combinacao(marco, ETAPAS) == [
        "A nota final é a pontuação obtida na Etapa “Prova de títulos”."
    ]
    assert pdf._combinacao(marco, ETAPAS) == "soma ponderada da Etapa Prova de títulos (peso 1)"


def test_c7_soma_ponderada_de_duas_etapas():
    """C7 — a mesma operação, dita: cada pontuação multiplicada pelo seu peso, e somadas."""
    marco = _marco(stages=["p", "q"])

    assert pdf.frases_da_combinacao(marco, ETAPAS) == [
        "A nota final é a soma das pontuações nas Etapas “Prova de títulos” (peso 1) e "
        "“Entrevista” (peso 2), cada uma multiplicada pelo seu peso."
    ]
    assert pdf._combinacao(marco, ETAPAS) == (
        "soma ponderada das Etapas Prova de títulos (peso 1) e Entrevista (peso 2)"
    )


def test_c7_soma_ponderada_de_uma_etapa_de_outro_peso():
    """C7, uma Etapa só: o peso continua dito, porque a conta o usa."""
    marco = _marco(stages=["q"])

    assert pdf.frases_da_combinacao(marco, ETAPAS) == [
        "A nota final é a pontuação obtida na Etapa “Entrevista” (peso 2), multiplicada pelo seu "
        "peso."
    ]


def test_c8_media_ponderada():
    """C8 — a mesma operação, dita."""
    marco = _marco(stages=["p", "q"], operation="MEDIA_PONDERADA")

    assert pdf.frases_da_combinacao(marco, ETAPAS) == [
        "A nota final é a média ponderada das pontuações nas Etapas “Prova de títulos” (peso 1) e "
        "“Entrevista” (peso 2)."
    ]
    assert pdf._combinacao(marco, ETAPAS) == (
        "média ponderada das Etapas Prova de títulos (peso 1) e Entrevista (peso 2)"
    )


def test_c9_normalizacao_pela_soma_dos_pesos():
    """C9 — o passo da normalização se preserva, depois da operação."""
    marco = _marco(stages=["p", "q"], normalization="PELA_SOMA_DOS_PESOS")

    assert pdf.frases_da_combinacao(marco, ETAPAS)[1:] == [
        "Depois, o resultado é dividido pela soma dos pesos."
    ]
    assert pdf.NORMALIZACAO_DO_MARCO["PELA_SOMA_DOS_PESOS"] == "pela soma dos pesos"


def test_c9_peso_um_com_normalizacao_nao_e_a_c6():
    """A C6 é só a de peso 1 **sem** normalização: com ela, os dois passos continuam ditos."""
    marco = _marco(normalization="PELA_SOMA_DOS_PESOS")

    assert pdf.frases_da_combinacao(marco, ETAPAS) == [
        "A nota final é a pontuação obtida na Etapa “Prova de títulos” (peso 1), multiplicada pelo "
        "seu peso.",
        "Depois, o resultado é dividido pela soma dos pesos.",
    ]


def test_c10_etapa_decisoria_na_lista_do_marco():
    """C10 — a Etapa que não pontua continua dita como fora da conta."""
    marco = _marco(stages=["p", "d"])

    assert pdf.frases_da_combinacao(marco, ETAPAS) == [
        "A nota final é a pontuação obtida na Etapa “Prova de títulos”.",
        "A Etapa “Análise documental” não entra na conta: ela não dá pontos.",
    ]
    assert pdf._combinacao(marco, ETAPAS) == (
        "soma ponderada das Etapas Prova de títulos (peso 1) e Análise documental (não pontua)"
    )


@pytest.mark.parametrize(
    ("arredondamento", "redacao_2", "redacao_1"),
    [
        (
            {"scale": 2, "mode": "MEIO_PARA_CIMA"},
            "A nota final é arredondada para 2 casas decimais; a partir da metade, arredonda-se "
            "para cima.",
            "2 casas decimais, meio para cima",
        ),
        (
            {"scale": 2, "mode": "MEIO_PARA_PAR"},
            "A nota final é arredondada para 2 casas decimais; na metade exata, arredonda-se para "
            "o algarismo par mais próximo.",
            "2 casas decimais, meio para par",
        ),
        (
            {"scale": 3, "mode": "TRUNCAR"},
            "A nota final é arredondada para 3 casas decimais, desprezando-se as demais.",
            "3 casas decimais, truncamento",
        ),
        (
            {"scale": 1, "mode": "MEIO_PARA_CIMA"},
            "A nota final é arredondada para 1 casa decimal; a partir da metade, arredonda-se para "
            "cima.",
            "1 casa decimal, meio para cima",
        ),
        (
            {"scale": 0, "mode": "MEIO_PARA_CIMA"},
            "A nota final é arredondada para um número inteiro; a partir da metade, arredonda-se "
            "para cima.",
            "sem casas decimais, meio para cima",
        ),
        (
            {"scale": 0, "mode": "TRUNCAR"},
            "A nota final é arredondada para um número inteiro, desprezando-se as casas decimais.",
            "sem casas decimais, truncamento",
        ),
        (
            {"scale": 2},
            "A nota final é arredondada para 2 casas decimais.",
            "2 casas decimais",
        ),
    ],
    ids=["C11", "C12", "C13", "C14-uma", "C14-inteiro", "C13-inteiro", "sem-modo-na-previa"],
)
def test_c11_a_c14_arredondamento(arredondamento, redacao_2, redacao_1):
    """C11 a C14 — a escala e o modo se preservam; o modo é dito pelo efeito na metade (L7)."""
    marco = _marco(rounding=arredondamento)

    assert pdf.frase_do_arredondamento(marco) == redacao_2
    assert pdf._arredondamento(marco) == redacao_1


def test_c15_sob_sorteio_nao_ha_arredondamento_nem_combinacao():
    """C15 — inalterado: sob sorteio não há nota a combinar nem a arredondar (067, ED-03)."""
    marco = _sorteio(stages=["p"])
    snapshot, perfil = _snapshot(marco)

    assert pdf.frases_da_ordem(snapshot, perfil, marco) == [
        "Participam do sorteio todas as inscrições enviadas."
    ]


def test_frases_da_ordem_por_pontuacao_na_ordem_do_contrato():
    """A forma, a combinação, a normalização, a Etapa fora da conta e o arredondamento, em ordem."""
    marco = _marco(stages=["p", "q", "d"], normalization="PELA_SOMA_DOS_PESOS")
    snapshot, perfil = _snapshot(marco)

    assert pdf.frases_da_ordem(snapshot, perfil, marco) == [
        "A ordem de classificação segue a nota final.",
        "A nota final é a soma das pontuações nas Etapas “Prova de títulos” (peso 1) e "
        "“Entrevista” (peso 2), cada uma multiplicada pelo seu peso.",
        "Depois, o resultado é dividido pela soma dos pesos.",
        "A Etapa “Análise documental” não entra na conta: ela não dá pontos.",
        "A nota final é arredondada para 2 casas decimais; a partir da metade, arredonda-se para "
        "cima.",
    ]


# ---------------------------------------------------------------------------
# 2. Corte — a unidade indivisível
# ---------------------------------------------------------------------------

K9 = "Depois, poderão ser chamados outros candidatos, além desses, seguindo a mesma ordem."
K7 = (
    "Os suplentes são chamados, na ordem, para as vagas deste Edital que não forem preenchidas "
    "pelos primeiros classificados."
)


def test_k1_alvo_pelo_quadro_de_vagas_com_suplentes():
    """K1 — "recorte" é Perfil × lista (`faixa.py`): "cada lista de concorrência", "dessa lista".

    K9: a continuação sai **sem** condição — a primeira redação da amostra acrescentava "se ainda
    sobrarem vagas", que a norma não tem (achado 1 da conferência).
    """
    marco = _sorteio(
        cutRule=_corte(
            targetKind="FROM_VACANCY_TABLE",
            targetCount=None,
            surplusCount=15,
            continuation="ALLOWED",
        )
    )

    assert pdf.frases_do_corte(marco, ETAPAS, sem_cadastro=False) == [
        "Passam para a Etapa “Análise documental” os primeiros classificados de cada lista de "
        "concorrência, em número igual ao das vagas dessa lista, mais 15 (quinze) suplentes.",
        K9,
    ]
    assert pdf._regra_de_corte(marco, ETAPAS) == (
        "Progridem para Análise documental os primeiros desta ordem, até o número de vagas "
        "ofertadas no recorte, mais 15 (quinze) suplentes."
    )
    assert pdf._continuacao_do_corte(marco) == (
        "Poderá haver chamada, nesta ordem, além dos que este corte publicar."
    )


def test_k9_nao_acrescenta_condicao():
    """K9 — nenhuma condição acrescentada: nem "se", nem "sobrarem", nem "vagas"."""
    frase = pdf.frase_da_continuacao({"cutRule": _corte(continuation="ALLOWED")})

    assert frase == K9
    palavras = frase.lower().replace(",", " ").replace(".", " ").split()
    for proibida in ("se", "sobrarem", "vagas"):
        assert proibida not in palavras


def test_k2_alvo_fixo_com_suplentes_e_empate_que_admite_excedente():
    """K2 e K5 — o alvo, os suplentes e o desfecho do empate se preservam (L2)."""
    marco = _marco(
        cutRule=_corte(
            targetCount=10, surplusCount=5, tieOutcome="ADMITS_SURPLUS", continuation="ALLOWED"
        )
    )

    assert pdf.frases_do_corte(marco, ETAPAS, sem_cadastro=False) == [
        "Passam para a Etapa “Análise documental” os 10 (dez) primeiros classificados, mais 5 "
        "(cinco) suplentes.",
        "Se houver empate na última posição, passam todos os empatados, mesmo que ultrapassem "
        "esse número.",
        K9,
    ]
    assert pdf._empate_no_corte(marco) == (
        "Havendo empate na última posição, progridem todos os empatados, ainda que excedam essa "
        "quantidade."
    )


def test_k3_alvo_de_um_sem_suplentes():
    """K3 — o singular se preserva: "passa … o 1 (um) primeiro classificado"."""
    marco = _marco(cutRule=_corte(targetCount=1))

    assert pdf.frases_do_corte(marco, ETAPAS, sem_cadastro=True)[0] == (
        "Passa para a Etapa “Análise documental” o 1 (um) primeiro classificado."
    )
    assert pdf._regra_de_corte(marco, ETAPAS) == (
        "Progride para Análise documental o 1 (um) primeiro desta ordem."
    )


def test_k4_marco_terminal_nao_nomeia_etapa():
    """K4 — como hoje, a frase não nomeia Etapa quando o marco não governa nenhuma."""
    marco = _marco(cutRule=_corte(targetCount=3, governedStage=None))

    assert pdf.frases_do_corte(marco, ETAPAS, sem_cadastro=True)[0] == (
        "Seguem no processo os 3 (três) primeiros classificados."
    )
    assert pdf._regra_de_corte(marco, ETAPAS) == "Progridem os 3 (três) primeiros desta ordem."


def test_k6_empate_estrito_sob_pontuacao():
    """K6 — o número não é ultrapassado, dito do mesmo jeito que o K5."""
    marco = _marco(cutRule=_corte())

    assert pdf.frases_do_corte(marco, ETAPAS, sem_cadastro=False) == [
        "Passam para a Etapa “Análise documental” os 10 (dez) primeiros classificados.",
        "Se houver empate na última posição, esse número não é ultrapassado.",
        "Não serão chamados candidatos além desses.",
    ]
    assert pdf._empate_no_corte(marco) == (
        "Havendo empate na última posição, essa quantidade não é excedida."
    )


def test_k6_sob_sorteio_o_empate_nao_sai():
    """A ordem sorteada é total, e o empate na última posição não acontece (067, FR-1314)."""
    marco = _sorteio(cutRule=_corte())

    assert pdf.frases_do_corte(marco, ETAPAS, sem_cadastro=False) == [
        "Passam para a Etapa “Análise documental” os 10 (dez) primeiros classificados.",
        "Não serão chamados candidatos além desses.",
    ]


def test_k7_suplentes_sem_cadastro_de_reserva_em_nenhum_perfil():
    """K7 — **frase nova** (D-004, FR-1362): descreve a regra de convocação do sistema.

    O suplente só é chamado para a vaga imediata que não foi preenchida (019, 050). A frase depende
    de aprovação no SC-517, e sai depois do empate e antes da continuação — dentro da unidade.
    """
    marco = _sorteio(
        cutRule=_corte(
            targetKind="FROM_VACANCY_TABLE",
            targetCount=None,
            surplusCount=15,
            continuation="ALLOWED",
        )
    )

    frases = pdf.frases_do_corte(marco, ETAPAS, sem_cadastro=True)

    assert frases[1:] == [K7, K9]


def test_k8_suplentes_com_cadastro_de_reserva_nao_ganham_a_explicacao():
    """K8 — com cadastro de reserva, a relação com os suplentes é a DP-05: o documento não a diz."""
    marco = _marco(cutRule=_corte(surplusCount=5))

    assert K7 not in pdf.frases_do_corte(marco, ETAPAS, sem_cadastro=False)


def test_k7_sem_suplentes_nao_ha_o_que_explicar():
    marco = _marco(cutRule=_corte(surplusCount=0))

    assert K7 not in pdf.frases_do_corte(marco, ETAPAS, sem_cadastro=True)


def test_k10_continuacao_vedada():
    """K10 — a vedação se preserva."""
    assert pdf.frase_da_continuacao({"cutRule": _corte(continuation="NONE")}) == (
        "Não serão chamados candidatos além desses."
    )
    assert pdf._continuacao_do_corte({"cutRule": _corte(continuation="NONE")}) == (
        "Não haverá chamada além dos que este corte publicar."
    )


def test_marco_sem_corte_nao_tem_unidade():
    assert pdf.frases_do_corte(_marco(), ETAPAS, sem_cadastro=True) == []


# ---------------------------------------------------------------------------
# 3. Desempate
# ---------------------------------------------------------------------------


def _criterio(tipo, quando="ULTIMO_NO_CRITERIO", **parametros):
    return {"id": "c", "type": tipo, "order": 1, "parameters": parametros, "whenMissing": quando}


@pytest.mark.parametrize(
    ("criterio", "redacao_2", "redacao_1"),
    [
        (
            _criterio("MENOR_VALOR_DE_FATO", factId="nasc"),
            "data de nascimento mais antiga, informada na inscrição; quem não a informar fica em "
            "último lugar neste critério",
            "menor valor declarado em Data de nascimento; sem o valor, fica por último neste "
            "critério",
        ),
        (
            _criterio("MAIOR_VALOR_DE_FATO", factId="nasc"),
            "data de nascimento mais recente, informada na inscrição; quem não a informar fica em "
            "último lugar neste critério",
            "maior valor declarado em Data de nascimento; sem o valor, fica por último neste "
            "critério",
        ),
        (
            _criterio("MAIOR_VALOR_DE_FATO", factId="exp"),
            "maior número de meses de experiência em tutoria, informado na inscrição; quem não o "
            "informar fica em último lugar neste critério",
            "maior valor declarado em Meses de experiência em tutoria; sem o valor, fica por "
            "último neste critério",
        ),
        (
            _criterio("MENOR_VALOR_DE_FATO", factId="exp"),
            "menor número de meses de experiência em tutoria, informado na inscrição; quem não o "
            "informar fica em último lugar neste critério",
            "menor valor declarado em Meses de experiência em tutoria; sem o valor, fica por "
            "último neste critério",
        ),
        (
            _criterio("MAIOR_PONTUACAO_NA_ETAPA", "CRITERIO_NAO_SE_APLICA", stageId="p"),
            "maior pontuação na Etapa “Prova de títulos”; para quem não a tiver, o critério não se "
            "aplica",
            "maior pontuação na Etapa Prova de títulos; sem o valor, o critério não se aplica",
        ),
        (
            _criterio("MAIOR_PONTUACAO_NA_ETAPA", stageId="p"),
            "maior pontuação na Etapa “Prova de títulos”; quem não a tiver fica em último lugar "
            "neste critério",
            "maior pontuação na Etapa Prova de títulos; sem o valor, fica por último neste "
            "critério",
        ),
        (
            _criterio("MENOR_VALOR_DE_FATO", "CRITERIO_NAO_SE_APLICA", factId="nasc"),
            "data de nascimento mais antiga, informada na inscrição; para quem não a tiver, o "
            "critério não se aplica",
            "menor valor declarado em Data de nascimento; sem o valor, o critério não se aplica",
        ),
        (
            _criterio("MAIOR_VALOR_DE_FATO", "CRITERIO_NAO_SE_APLICA", factId="exp"),
            "maior número de meses de experiência em tutoria, informado na inscrição; para quem "
            "não o tiver, o critério não se aplica",
            "maior valor declarado em Meses de experiência em tutoria; sem o valor, o critério não "
            "se aplica",
        ),
    ],
    ids=["T1-T6", "T2-T6", "T3-T6", "T4-T6", "T5-T7", "T5-T6", "T1-T7", "T3-T7"],
)
def test_t1_a_t7_criterios_de_desempate(criterio, redacao_2, redacao_1):
    """T1 a T7 — o sentido da comparação e o efeito da ausência se preservam (L5).

    Menor data é a anterior: "mais antiga". A ausência concorda com o dado: "a" para a data e a
    pontuação, "o" para o número.
    """
    assert criterio_com_a_ausencia(criterio, ETAPAS, FATOS) == redacao_2
    assert criterio_com_a_ausencia(criterio, ETAPAS, FATOS, redacao=REDACAO_1) == redacao_1


def test_t1_forma_generica_sem_deduzir_idade_pelo_rotulo():
    """D-006: o rótulo é texto do Elaborador; o sistema não troca a regra por "maior idade"."""
    for tipo in ("MENOR_VALOR_DE_FATO", "MAIOR_VALOR_DE_FATO"):
        frase = criterio_por_extenso(_criterio(tipo, factId="nasc"), ETAPAS, FATOS)
        assert "idade" not in frase
        assert frase.startswith("data de nascimento mais ")


def test_o_rotulo_que_comeca_por_sigla_nao_perde_a_caixa():
    fatos = por_identificador(
        [{"id": "n", "type": "INTEIRO", "label": "CPF do responsável pela inscrição"}]
    )

    assert criterio_por_extenso(
        _criterio("MAIOR_VALOR_DE_FATO", factId="n"), ETAPAS, fatos
    ).startswith("maior número de CPF do responsável")


def test_o_alvo_que_nao_resolve_continua_dito_como_ausente():
    """O identificador não sai em nenhuma hipótese, nem na redação 2 (E2E15-004)."""
    assert criterio_por_extenso(
        _criterio("MAIOR_PONTUACAO_NA_ETAPA", stageId="x"), ETAPAS, FATOS
    ) == ("maior pontuação na Etapa não identificada neste Edital")
    assert (
        "x"
        not in criterio_por_extenso(
            _criterio("MAIOR_VALOR_DE_FATO", factId="x"), ETAPAS, FATOS
        ).split()
    )


def test_t8_cabecalho_e_ordem_dos_criterios():
    """T8 — a ordem declarada se preserva, e o cabeçalho diz que ela é a ordem de aplicação."""
    marco = _marco(
        tiebreakers=[
            {**_criterio("MAIOR_VALOR_DE_FATO", factId="exp"), "order": 2},
            {**_criterio("MENOR_VALOR_DE_FATO", factId="nasc"), "order": 1},
        ]
    )

    assert pdf.CABECALHO_DO_DESEMPATE == "Critérios de desempate, nesta ordem:"
    frases = pdf.frases_do_desempate(marco, ETAPAS, FATOS)
    assert [frase[:3] for frase in frases] == ["1º ", "2º "]
    assert frases[0].startswith("1º data de nascimento mais antiga")


# ---------------------------------------------------------------------------
# 4. Recurso
# ---------------------------------------------------------------------------


def _janela(dias=5, admite=True):
    return {"unit": "DIAS_CORRIDOS", "admits": admite, "durationDays": dias}


def test_r1_recurso_admitido_contra_marco_com_nome():
    """R1 — o objeto e o prazo se preservam; nome entre aspas e **sem artigo** (decisão 001 da
    `067`); o canal não é gerado (FR-1363) — é o texto do Elaborador que o diz."""
    marco = _marco(appealWindow=_janela())

    assert pdf.frase_do_recurso(marco) == (
        "Contra o resultado de “Classificação final”: no prazo de 5 (cinco) dias corridos, "
        "contados da divulgação desse resultado."
    )
    assert pdf._janela_recursal(marco) == (
        "Caberá recurso contra o resultado de “Classificação final”, no prazo de 5 (cinco) dias "
        "corridos, contados da divulgação desse resultado."
    )


def test_r2_prazo_de_um_dia():
    """R2 — o singular se preserva."""
    assert "no prazo de 1 (um) dia corrido, contados" in pdf.frase_do_recurso(
        _marco(appealWindow=_janela(1))
    )


def test_r3_recurso_vedado():
    """R3 — inalterado: a negativa é norma, e sai."""
    marco = _marco(appealWindow=_janela(admite=False))

    assert (
        pdf.frase_do_recurso(marco)
        == "Não caberá recurso contra o resultado de “Classificação final”."
    )
    assert pdf._janela_recursal(marco) == pdf.frase_do_recurso(marco)


def test_r4_sem_nome_so_na_previa_de_rascunho():
    """R4 — o prazo se preserva; "cabe" no presente, como o resto da redação 2."""
    marco = _marco(appealWindow=_janela(), name="", code="")

    assert pdf.frase_do_recurso(marco) == (
        "Cabe recurso no prazo de 5 (cinco) dias corridos, contados da divulgação do resultado."
    )


def test_r5_silencio_nao_vira_negativa():
    """R5 — o marco que nada declara não imprime frase de recurso."""
    assert pdf.frase_do_recurso(_marco()) == ""


def test_r_a_revisao_diz_deste_marco():
    """Na Revisão, que agrupa marcos de nomes diferentes, o objeto é "deste marco" (067, D-012)."""
    assert pdf.frase_do_recurso(_marco(appealWindow=_janela()), objeto="deste marco") == (
        "Contra o resultado deste marco: no prazo de 5 (cinco) dias corridos, contados da "
        "divulgação desse resultado."
    )


# ---------------------------------------------------------------------------
# 5. Sorteio — os dados para conferir
# ---------------------------------------------------------------------------


def test_s1_a_s7_metodo_comum():
    """S1 a S7 — os sete campos continuam todos impressos (FR-465, FR-1376).

    Fonte, ocorrência e quando na abertura; algoritmo, derivação, semente e substituição nos pares.
    A fonte e a ocorrência vão entre aspas, sem artigo — o nome não tem gênero conhecido, como o do
    marco (decisão 001 da `067`).
    """
    marco = _sorteio()
    snapshot, perfil = _snapshot(marco)

    abertura, pares = pdf.dados_do_sorteio(snapshot, perfil, marco)

    assert abertura == (
        "A ordem será definida a partir do resultado de “Concurso 6010”, da fonte “Loteria "
        "Federal”, de 14/11/2026, às 19h. Com os dados abaixo, qualquer pessoa pode refazer o "
        "sorteio e conferir o resultado."
    )
    assert pares == [
        ["Método", "comum a este Edital; algoritmo IFES-SORTEIO-SHA256-v1."],
        ["Qual concurso", METODO["derivation"]],
        [
            "Semente",
            "o número usado no sorteio: os cinco números sorteados, na ordem dos prêmios, "
            "separados por espaço.",
        ],
        ["Se faltar", METODO["substitutionRule"]["text"]],
    ]


def test_s3_metodo_proprio_igual_ao_comum():
    marco = _sorteio(drawMethod=dict(METODO))
    snapshot, perfil = _snapshot(marco)

    _, pares = pdf.dados_do_sorteio(snapshot, perfil, marco)

    assert pares[0] == ["Método", "próprio deste sorteio; algoritmo IFES-SORTEIO-SHA256-v1."]


def test_s4_metodo_proprio_divergente():
    """S4 — a divergência continua nomeada quando existe (032, FR-466)."""
    marco = _sorteio(drawMethod={**METODO, "algorithm": "OUTRO-v2"})
    snapshot, perfil = _snapshot(marco)

    _, pares = pdf.dados_do_sorteio(snapshot, perfil, marco)

    assert pares[0] == [
        "Método",
        "próprio deste sorteio, diferente do comum deste Edital; algoritmo OUTRO-v2.",
    ]
    assert pdf._origem_do_metodo(snapshot, marco) == (
        "próprio deste marco — diverge do comum deste Edital"
    )


def test_s_sem_metodo_nao_ha_dados():
    marco = _sorteio()
    snapshot, perfil = _snapshot(marco, metodo=None)

    assert pdf.dados_do_sorteio(snapshot, perfil, marco) is None


# ---------------------------------------------------------------------------
# 6. Vagas, convocação, inscrição, matrícula
# ---------------------------------------------------------------------------


def test_v1_e_v2_reversao():
    """V1 e V2 — o gatilho e o destino se preservam; "a respectiva" vira "a do mesmo código"."""
    assert pdf.frase_da_reversao("ON_EXHAUSTION") == (
        "Se não houver candidatos aprovados para as vagas reservadas de um código, essas vagas "
        "passam para a ampla concorrência do mesmo código."
    )
    assert pdf.frase_da_reversao("ON_BALANCE") == (
        "As vagas reservadas de um código que não forem preenchidas passam para a ampla "
        "concorrência do mesmo código."
    )
    assert pdf.frase_da_reversao("ON_BALANCE", redacao=REDACAO_1) == (
        "Na hipótese do não preenchimento total das vagas reservadas, o quantitativo não "
        "preenchido será destinado à respectiva ampla concorrência."
    )
    assert pdf.frase_da_reversao("OUTRA") == ""


def test_v4_e_v5_convocacao():
    """V4 — o lugar da publicação é texto do Elaborador; V5 — o canal se preserva."""
    assert (
        frase_da_convocacao("PUBLICATION")
        == "A convocação dos classificados será feita por publicação."
    )
    assert frase_da_convocacao("INDIVIDUAL_MESSAGE") == (
        "A convocação será feita por mensagem individual à pessoa convocada."
    )
    assert frase_da_convocacao("PUBLICATION", redacao=REDACAO_1) == (
        "A convocação dos classificados será feita por publicação no endereço eletrônico do "
        "certame."
    )
    assert frase_da_convocacao(None) == ""


def test_v6_forma_nao_declarada():
    """V6 — inalterada: só a prévia a mostra."""
    assert vocabulario.forma_de_convocacao_por_extenso(None) == (
        "forma de convocação não declarada neste Edital"
    )


def test_a_forma_por_extenso_do_portal_e_da_revisao():
    """A forma sozinha, para quem a encaixa na sua frase (o portal, a Revisão)."""
    assert vocabulario.forma_de_convocacao_por_extenso("PUBLICATION") == "por publicação"
    assert vocabulario.forma_de_convocacao_por_extenso("PUBLICATION", redacao=REDACAO_1) == (
        "por publicação no endereço eletrônico do certame"
    )


@pytest.mark.parametrize(
    ("teto", "redacao_2", "redacao_1"),
    [
        (
            1,
            "Cada candidato pode enviar apenas 1 (uma) inscrição neste Edital.",
            "Cada candidato poderá ter apenas 1 inscrição enviada neste Edital.",
        ),
        (
            2,
            "Cada candidato pode enviar no máximo 2 (duas) inscrições neste Edital.",
            "Cada candidato poderá ter no máximo 2 inscrições enviadas neste Edital.",
        ),
        (
            3,
            "Cada candidato pode enviar no máximo 3 (três) inscrições neste Edital.",
            "Cada candidato poderá ter no máximo 3 inscrições enviadas neste Edital.",
        ),
        (
            12,
            "Cada candidato pode enviar no máximo 12 inscrições neste Edital.",
            "Cada candidato poderá ter no máximo 12 inscrições enviadas neste Edital.",
        ),
    ],
    ids=["V7", "V8-duas", "V8-tres", "V8-sem-extenso"],
)
def test_v7_e_v8_teto(teto, redacao_2, redacao_1):
    """V7 e V8 — conta só a inscrição enviada, como antes (FR-064); o número ganha o extenso."""
    snapshot = {"maxInscricoesPorCandidato": teto}

    assert pdf.teto_de_inscricoes(snapshot) == redacao_2
    assert pdf.teto_de_inscricoes(snapshot, redacao=REDACAO_1) == redacao_1
    assert pdf.teto_de_inscricoes({}) is None


def test_v9_periodo_de_inscricoes():
    """V9 — **frase nova, gerada** do Evento de inscrição, com a remissão ao Cronograma."""
    evento = {
        "order": 3,
        "startAt": "2026-11-03T08:00:00-03:00",
        "endAt": "2026-11-10T23:59:00-03:00",
        "isRegistrationPeriod": True,
    }

    assert pdf.frase_do_periodo_de_inscricoes(evento) == (
        "Período de inscrições: de 03/11/2026, às 08h, a 10/11/2026, às 23h59 (Cronograma, nº 3)."
    )


def test_v10_dados_declarados():
    """V10 — os mesmos dados, ditos uma vez e sem o tipo entre parênteses (FR-1366)."""
    fatos = list(FATOS.values())

    assert pdf.ANUNCIO_DOS_DADOS_DECLARADOS == "Na inscrição, informe também:"
    assert pdf.itens_dos_dados_declarados(fatos) == [
        "a data de nascimento;",
        "o número de meses de experiência em tutoria.",
    ]
    assert pdf.frase_do_uso_no_desempate("8.1") == "Esses dados são usados no desempate (item 8.1)."


@pytest.mark.parametrize(
    ("momento", "redacao_2", "redacao_1"),
    [
        (
            "AT_ENROLLMENT",
            "O Requerimento de Matrícula é enviado no ato da inscrição. Ao enviá-lo, o candidato "
            "declara:",
            "O Requerimento de Matrícula será enviado no ato da inscrição.",
        ),
        (
            "AT_CALL",
            "O Requerimento de Matrícula é enviado quando o candidato for convocado. Ao enviá-lo, "
            "o candidato declara:",
            "O Requerimento de Matrícula será enviado quando o candidato for convocado.",
        ),
    ],
    ids=["V11", "V12"],
)
def test_v11_e_v12_requerimento(momento, redacao_2, redacao_1):
    """V11 e V12 — o momento e a declaração se preservam; a declaração, transcrita inteira."""
    snapshot = {"matriculationRequest": {"moment": momento, "declarationText": "Declaro X.\nE Y."}}

    assert pdf.requerimento_de_matricula(snapshot) == [
        (redacao_2, 0.0),
        ("Declaro X.", pdf.RECUO_DA_DECLARACAO),
        ("E Y.", pdf.RECUO_DA_DECLARACAO),
    ]
    assert pdf.requerimento_de_matricula(snapshot, redacao=REDACAO_1)[:2] == [
        (redacao_1, 0.0),
        ("Ao enviá-lo, o candidato declarará:", 0.0),
    ]


def test_v11_sem_declaracao_nao_anuncia_o_que_nao_ha():
    snapshot = {"matriculationRequest": {"moment": "AT_ENROLLMENT", "declarationText": ""}}

    assert pdf.requerimento_de_matricula(snapshot) == [
        ("O Requerimento de Matrícula é enviado no ato da inscrição.", 0.0)
    ]


def test_v13_lembrete_do_requerimento():
    """V13 — **frase nova** (ED-18): remete ao item da matrícula, sem repetir a declaração."""
    assert pdf.lembrete_do_requerimento("11") == (
        "Além destes documentos, a inscrição inclui o Requerimento de Matrícula (item 11)."
    )
    assert pdf.lembrete_do_requerimento("11", na_inscricao=True) == (
        "A inscrição inclui o Requerimento de Matrícula (item 11)."
    )


# ---------------------------------------------------------------------------
# 7. Etapas, documentos, atributos, fecho
# ---------------------------------------------------------------------------

EVENTOS = {
    "ev-p": {
        "id": "ev-p",
        "startAt": "2026-11-17T08:00:00-03:00",
        "endAt": "2026-11-24T17:00:00-03:00",
    },
    "ev-d": {"id": "ev-d", "startAt": "2026-11-17T08:00:00-03:00", "endAt": None},
}


def test_e1_etapa_decisoria():
    """E1 — o caráter, os dois resultados e o período se preservam; a hora com dois dígitos."""
    etapa = {**ETAPAS["d"], "scheduleEventId": "ev-p"}

    assert pdf.frase_da_etapa(etapa, EVENTOS) == (
        "Etapa eliminatória: o resultado é “Deferida” ou “Indeferida”. Será feita de 17/11/2026, "
        "às 08h, a 24/11/2026, às 17h."
    )


def test_e2_etapa_pontuada():
    """E2 — só o que está declarado: caráter, máximo, mínimo, peso e avaliações por inscrição."""
    assert pdf.frase_da_etapa(ETAPAS["p"], EVENTOS) == (
        "Etapa classificatória, com pontuação máxima de 100 e peso 1. Cada inscrição recebe "
        "1 (uma) avaliação. Será feita de 17/11/2026, às 08h, a 24/11/2026, às 17h."
    )
    assert pdf.frase_da_etapa(ETAPAS["q"], EVENTOS) == (
        "Etapa eliminatória e classificatória, com pontuação máxima de 100, nota mínima de 60 e "
        "peso 2. Cada inscrição recebe 2 (duas) avaliações."
    )


def test_e3_evento_de_um_instante():
    """E3 — o instante único continua dito."""
    etapa = {**ETAPAS["d"], "scheduleEventId": "ev-d"}

    assert pdf.frase_da_etapa(etapa, EVENTOS).endswith("Será feita em 17/11/2026, às 08h.")


def test_e_etapa_sem_nada_declarado_nao_inventa_frase():
    assert pdf.frase_da_etapa({"name": "X", "forma": "PONTUADA"}, {}) == ""


def _documentos_snapshot():
    modalidade = {"id": "ppi", "code": "PPI", "name": "Pessoas pretas, pardas e indígenas"}
    perfil = {
        "id": "tp1",
        "code": "TP-01",
        "name": "Tutor presencial",
        "competitionModalities": [modalidade],
    }
    return {"profiles": [perfil]}


@pytest.mark.parametrize(
    ("perfil_id", "modalidade_id", "codigo", "redacao_2", "redacao_1"),
    [
        (None, None, None, "De todos os candidatos:", "De todos os candidatos:"),
        (
            "tp1",
            None,
            None,
            "Também, de quem concorre ao Perfil TP-01 — Tutor presencial:",
            "Dos candidatos ao perfil TP-01 — Tutor presencial:",
        ),
        (
            None,
            "ppi",
            None,
            "Também, de quem concorre às vagas para pessoas pretas, pardas e indígenas (PPI):",
            "Dos candidatos concorrentes na modalidade Pessoas pretas, pardas e indígenas:",
        ),
        (
            None,
            None,
            "PPI",
            "Também, de quem concorre às vagas para pessoas pretas, pardas e indígenas (PPI):",
            None,
        ),
        (
            "tp1",
            "ppi",
            None,
            "Também, de quem concorre ao Perfil TP-01 — Tutor presencial nas vagas para pessoas "
            "pretas, pardas e indígenas (PPI):",
            "Dos candidatos ao perfil TP-01 — Tutor presencial concorrentes na modalidade Pessoas "
            "pretas, pardas e indígenas:",
        ),
    ],
    ids=["D1", "D2", "D3", "D3-codigo", "D4"],
)
def test_d1_a_d4_a_quem_o_documento_e_pedido(
    perfil_id, modalidade_id, codigo, redacao_2, redacao_1
):
    """D1 a D4 — o alcance se preserva: todos, o Perfil, a lista, o Perfil e a lista."""
    snapshot = _documentos_snapshot()
    perfis, modalidades = pdf._nomes_do_alcance(snapshot)

    assert (
        pdf._titulo_do_grupo(perfil_id, modalidade_id, perfis, modalidades, codigo, snapshot)
        == redacao_2
    )
    if redacao_1 is not None:
        assert (
            pdf._titulo_do_grupo(
                perfil_id, modalidade_id, perfis, modalidades, codigo, snapshot, redacao=REDACAO_1
            )
            == redacao_1
        )


def test_d5_instrucao_do_documento():
    """D5 — o documento e a instrução se preservam; a instrução segue o travessão em minúscula."""
    documento = {"name": "Diploma", "instructions": "Frente e verso.", "required": True}

    assert pdf.texto_do_documento(documento) == "Diploma — frente e verso."
    assert pdf.texto_do_documento({**documento, "instructions": "PDF único."}) == (
        "Diploma — PDF único."
    )
    assert pdf.texto_do_documento({**documento, "required": False}) == (
        "Diploma (facultativo) — frente e verso."
    )


@pytest.mark.parametrize(
    ("tipo", "limite", "redacao_2"),
    [
        ("NONE", None, "não há cadastro de reserva"),
        ("LIMITED", 15, "cadastro de reserva de até 15 (quinze) classificados por Perfil"),
        ("UNLIMITED", None, "cadastro de reserva sem limite de classificados"),
    ],
    ids=["P2-nao-ha", "P2-limitado", "P2-ilimitado"],
)
def test_p2_cadastro_de_reserva(tipo, limite, redacao_2):
    """P2 — o cadastro dito por extenso (FR-1371); o limite é o mesmo."""
    assert pdf.frase_do_cadastro({"reserveType": tipo, "reserveLimit": limite}) == redacao_2


def test_p1_atributos_iguais_em_todos_os_perfis():
    """P1 — o que é igual em todos sai uma vez (FR-1374); o que difere não entra."""
    perfis = [
        {
            "code": f"TP-0{indice}",
            "name": "Tutor presencial",
            "description": "Atua no polo de apoio presencial.",
            "workload": "20 horas semanais",
            "compensation": "Bolsa de R$ 1.100,00",
            "reserveType": "LIMITED",
            "reserveLimit": 15,
            "locality": local,
        }
        for indice, local in ((1, "Aracruz"), (2, "Serra"))
    ]

    assert pdf.frase_dos_atributos_comuns(perfis) == (
        "Em todos os Perfis: Tutor presencial — atua no polo de apoio presencial; carga horária de "
        "20 horas semanais; remuneração: bolsa de R$ 1.100,00; cadastro de reserva de até 15 "
        "(quinze) classificados por Perfil."
    )
    perfis[1]["workload"] = "30 horas semanais"
    assert "carga horária" not in pdf.frase_dos_atributos_comuns(perfis)
    # O Edital de um Perfil não tem "todos os Perfis", e a frase diz o Perfil: sem ela, o corpo
    # calava o nome, a descrição, a carga, a remuneração e o cadastro do único Perfil.
    assert pdf.frase_dos_atributos_comuns(perfis[:1]) == (
        "Perfil TP-01: Tutor presencial — atua no polo de apoio presencial; carga horária de "
        "20 horas semanais; remuneração: bolsa de R$ 1.100,00; cadastro de reserva de até 15 "
        "(quinze) classificados por Perfil."
    )


def test_f1_autenticidade():
    """F1 — L17: "deriva" vira "corresponde"; os dados da identificação são os de hoje."""
    assert pdf.FRASE_DE_AUTENTICIDADE == (
        "Autenticidade — este documento corresponde integralmente à versão homologada do Edital "
        "identificada abaixo."
    )


# ---------------------------------------------------------------------------
# 8. Rótulos gerados com "Marcos classificatórios"
# ---------------------------------------------------------------------------


def test_g1_a_g3_regras_de_classificacao():
    """G1 a G3 (D-007) — só o rótulo muda; o número e o destino são os mesmos (FR-1399)."""
    assert pdf.ROTULO_DAS_REGRAS[REDACAO_2] == "Regras de classificação"
    assert pdf.ROTULO_DAS_REGRAS[REDACAO_1] == "Marcos classificatórios"
    assert pdf.remissao_as_regras("5.6") == (
        "Regras de classificação",
        "as descritas no item 5.6.",
    )
    assert pdf.remissao_as_regras("5.6", redacao=REDACAO_1) == (
        "Marcos classificatórios",
        "os descritos no item 5.6.",
    )
    assert pdf.titulo_da_subsecao_comum(pdf.MARCOS) == "Regras de classificação comuns aos Perfis"
    assert pdf.titulo_da_subsecao_comum(pdf.MARCOS, redacao=REDACAO_1) == (
        "Marcos classificatórios comuns aos Perfis"
    )


def test_a_hora_mantem_dois_digitos():
    """A paridade com o portal (`humano.instante`): "às 08h", e não "às 8h" (L14 contrariava)."""
    assert pdf._instante(datetime(2026, 11, 3, 8, 0).isoformat()).endswith("às 08h")
