"""A validação pergunta se o Edital **funciona**, e não só se ele está preenchido (032).

Quatro achados, e o que os une é a forma do defeito que a auditoria de 16/09/2026 mediu: **a prosa
da tela afirma a regra, e a validação não a aplica**. O Edital saía publicado — ato imutável — e o
erro só aparecia meses depois, no dia de classificar ou de convocar, quando a saída já não é editar
o rascunho e sim Retificar.

**A primeira linha de toda regra desta família é o recorte por ato**, e não é polimento: a `030`
tentou recusar na gravação do rascunho e derrubou 759 testes, porque tornava ilegal todo payload
que este repositório produz. O rascunho continua podendo estar pela metade; o que não pode é o
Edital publicado.

**E os avisos recebem o mesmo recorte.** Aviso não impede publicação nenhuma, e por isso não
*precisaria* dele — mas sem ele a Retificação do Edital do acervo viria cheia de avisos sobre o que
aquele Edital já publicou e não tem como deixar de ter publicado.

As contraprovas valem tanto quanto as regras, e duas delas estão aqui por Edital real da amostra:
o **69/2026**, cuja regra de corte declara não governar Etapa alguma e é legítima, e a
grafia-armadilha da ampla concorrência, em que a Modalidade declarada não é o recorte que o ato
computado emite — o recorte da ampla é o `NULL` da linha geral.
"""

import pytest

from processo_seletivo.editais.domain.validation import (
    ATO_DE_PUBLICACAO,
    ATO_DE_RETIFICACAO,
    Severity,
    validate_for_publication,
)

PERFIL = "aaaaaaaa-0000-4000-8000-000000000321"
MARCO = "aaaaaaaa-0000-4000-8000-000000000322"
ETAPA = "aaaaaaaa-0000-4000-8000-000000000323"
EVENTO = "aaaaaaaa-0000-4000-8000-000000000324"
AMPLA = "aaaaaaaa-0000-4000-8000-000000000325"
PCD = "aaaaaaaa-0000-4000-8000-000000000326"
NEGROS = "aaaaaaaa-0000-4000-8000-000000000327"
LINHA_GERAL = "aaaaaaaa-0000-4000-8000-00000000032a"
LINHA_PCD = "aaaaaaaa-0000-4000-8000-00000000032b"
LINHA_NEGROS = "aaaaaaaa-0000-4000-8000-00000000032c"

#: O método inteiro, como a `021` o exige. Declarado aqui **completo** de propósito: o achado desta
#: feature é o da **ausência**, e um método pela metade tem achado próprio desde a `026`
#: (`draw_method_invalid`). Os dois precisam continuar distinguíveis.
METODO = {
    "algorithm": "IFES-SORTEIO-SHA256-v1",
    "source": "Loteria Federal",
    "occurrence": "5900",
    "occurrenceAt": "2026-11-20T20:00:00-03:00",
    "derivation": "a extração de sábado imediatamente anterior à data publicada",
    "normalization": {
        "rule": "DIGITOS_EM_SEQUENCIA",
        "text": "os cinco números sorteados, na ordem dos prêmios",
    },
    "substitutionRule": {
        "rule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
        "text": "não havendo extração na data, vale a extração seguinte da mesma fonte",
    },
}

#: A regra de corte que **governa uma Etapa** — o caso comum.
CORTE = {
    "targetKind": "FIXED",
    "targetCount": 10,
    "surplusCount": 0,
    "tieOutcome": "STRICT",
    "governedStage": ETAPA,
    "continuation": "NONE",
}

#: A regra do **69/2026**: declara, explicitamente, não governar Etapa alguma (`FR-224` da `014`).
#: Ela existe, a faixa nasce e a convocação alcança — e é por isso que ela não pode receber aviso.
CORTE_SEM_ETAPA = {**CORTE, "governedStage": "NONE"}


def marco(**alteracoes):
    """O marco-base, com `None` **removendo** a chave — que é como a ausência se escreve aqui."""
    base = {
        "id": MARCO,
        "code": "CLASS-TUT",
        "name": "Classificação final",
        "orderProduction": "POR_PONTUACAO",
        "stages": [ETAPA],
        "operation": "SOMA_PONDERADA",
        "normalization": "NENHUMA",
        "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
        "cutRule": dict(CORTE),
        "tiebreakers": [],
    }
    for chave, valor in alteracoes.items():
        if valor is None:
            base.pop(chave, None)
        else:
            base[chave] = valor
    return base


def de_sorteio(**alteracoes):
    """O marco que ordena por sorteio, com o método próprio declarado."""
    return marco(
        **{
            "code": "SORT-X",
            "name": "Sorteio público",
            "orderProduction": "POR_SORTEIO",
            "drawMethod": dict(METODO),
            **alteracoes,
        }
    )


def linha(identidade, modalidade_id, quantidade):
    return {"id": identidade, "modalityId": modalidade_id, "immediateVacancies": quantidade}


#: O quadro 7/1/2 da auditoria: sete na ampla — a linha de `modalityId` nulo —, uma e duas em duas
#: Modalidades reservadas.
QUADRO_7_1_2 = [
    linha(LINHA_GERAL, None, 7),
    linha(LINHA_PCD, PCD, 1),
    linha(LINHA_NEGROS, NEGROS, 2),
]


def perfil(**alteracoes):
    base = {
        "id": PERFIL,
        "code": "DOC-INFO",
        "name": "Professor de Informática",
        "immediateVacancies": 10,
        "reserveType": "NONE",
        "reserveLimit": None,
        # **A Modalidade declarada como a da ampla** (027, FR-317). Sem ela, a conferência do
        # quadro trataria a "AC" como reservada — e é justamente a confusão que a contraprova da
        # grafia-armadilha, mais abaixo, existe para travar.
        "generalCompetitionModalityId": AMPLA,
        "competitionModalities": [
            {"id": AMPLA, "code": "AC", "name": "Ampla concorrência"},
            {"id": PCD, "code": "PCD", "name": "Pessoas com deficiência"},
            {"id": NEGROS, "code": "PPI", "name": "Negros"},
        ],
        "vacancyTable": [linha(LINHA_GERAL, None, 10)],
        "classificationMilestones": [marco()],
    }
    base.update(alteracoes)
    return base


def snapshot(um_perfil=None, **raiz):
    base = {
        "title": "Edital 03/2026",
        "description": "Seleção simplificada.",
        "schedule": [{"id": EVENTO, "type": "INSCRICAO", "description": "Inscrições"}],
        "stages": [
            {
                "id": ETAPA,
                "name": "Análise curricular",
                "order": 1,
                "weight": "1.0000",
                "eliminatory": False,
                "classificatory": True,
                "minimumScore": None,
                "scheduleEventId": None,
            }
        ],
        "profiles": [perfil() if um_perfil is None else um_perfil],
    }
    base.update(raiz)
    return base


def achados(conteudo, codigo, *, ato=ATO_DE_PUBLICACAO):
    """Só os achados do código pedido.

    O snapshot montado à mão produz outros — é conteúdo parcial, e a validação confere o Edital
    inteiro. Filtrar por código é o que mantém cada teste falando de uma regra só; o que **não** se
    filtra é a severidade, porque ela é metade do que cada requisito afirma.
    """
    return [item for item in validate_for_publication(conteudo, ato=ato) if item.code == codigo]


# --- FR-457 · o Perfil que não classifica ninguém ----------------------------------------------
#
# O `ACH-49`: Edital publicado com `classificationMilestones = []`, e a Revisão respondendo
# `IMPEDE: []` sobre ele. A tela já dizia "um Perfil sem marco não classifica"; o que faltava não
# era texto, era a verificação.


def test_perfil_sem_marco_impede_a_publicacao():
    achado = achados(snapshot(perfil(classificationMilestones=[])), "profile_without_milestone")

    assert len(achado) == 1
    assert achado[0].severity == Severity.BLOCKING_ERROR


def test_a_recusa_do_perfil_sem_marco_nomeia_o_perfil_a_falta_e_a_etapa():
    """`FR-458`: a entidade, o que falta e onde se corrige — nunca apenas o sintoma."""
    achado = achados(snapshot(perfil(classificationMilestones=[])), "profile_without_milestone")[0]

    assert "Professor de Informática" in achado.message, "a entidade"
    assert "marco classificatório" in achado.message, "o que falta"
    assert "Classificação" in achado.message, "e em que etapa do assistente se corrige"
    assert achado.path == f"/profiles/id={PERFIL}/classificationMilestones"


def test_perfil_com_marco_nao_produz_achado():
    assert achados(snapshot(), "profile_without_milestone") == []


# --- FR-461 · o marco que classifica e não convoca ---------------------------------------------
#
# O `ACH-46`: a tela dizia "sem ele, a Etapa seguinte recebe todos os habilitados", que é verdade e
# é a metade menos importante. A consequência que importa — sem corte **não há convocação** — nunca
# era dita.


def test_marco_sem_regra_de_corte_e_aviso_e_nao_impedimento():
    achado = achados(
        snapshot(perfil(classificationMilestones=[marco(cutRule=None)])),
        "milestone_without_cut_rule",
    )

    assert len(achado) == 1
    assert achado[0].severity == Severity.WARNING, (
        "avisar, e não impedir: o marco sem corte é legítimo"
    )


def test_o_aviso_do_corte_nomeia_a_cadeia_inteira_ate_a_convocacao():
    """`FR-461`: corte → geração → faixa → convocação. A última é a que ninguém dizia."""
    achado = achados(
        snapshot(perfil(classificationMilestones=[marco(cutRule=None)])),
        "milestone_without_cut_rule",
    )[0]

    assert "CLASS-TUT" in achado.message, "qual marco"
    for elo in ("geração", "faixa", "convocação"):
        assert elo in achado.message, f"a cadeia precisa nomear {elo}"
    assert achado.path == (f"/profiles/id={PERFIL}/classificationMilestones/id={MARCO}/cutRule")


def test_a_regra_que_declara_nao_governar_etapa_nao_recebe_aviso():
    """A contraprova que importa, e é um Edital real: o 69/2026 (`FR-224` da `014`).

    Ele sorteia, publica, convoca e manda comparecer, sem análise documental entre a ordem e a
    chamada. A regra de corte dele **existe** e declara não governar Etapa alguma — a faixa nasce e
    a convocação alcança. Um aviso aqui dispararia no Edital mais simples e mais comum da amostra,
    e ruído treina a pessoa a ignorar a família inteira.
    """
    conteudo = snapshot(perfil(classificationMilestones=[marco(cutRule=dict(CORTE_SEM_ETAPA))]))

    assert achados(conteudo, "milestone_without_cut_rule") == []


# --- FR-459 · nada disto alcança a Retificação do acervo ---------------------------------------


@pytest.mark.parametrize(
    "codigo",
    ["profile_without_milestone", "milestone_without_cut_rule"],
)
def test_os_achados_de_us1_nao_sao_emitidos_na_retificacao(codigo):
    """`FR-459` e `FR-460`: o Edital do acervo é exatamente o que esta feature existe para evitar.

    Torná-lo irretificável trocaria um problema por outro pior — e é o que aconteceria sem o
    recorte, porque `retificacoes.py` afere o conteúdo produzido com `blocking_findings`.
    """
    sem_nada = perfil(classificationMilestones=[])

    assert achados(snapshot(sem_nada), codigo, ato=ATO_DE_RETIFICACAO) == []
    assert (
        achados(
            snapshot(perfil(classificationMilestones=[marco(cutRule=None)])),
            codigo,
            ato=ATO_DE_RETIFICACAO,
        )
        == []
    )


# --- FR-467 · o sorteio que ninguém consegue conferir ------------------------------------------
#
# O `ACH-50`: um Edital de sorteio publicado sem algoritmo, sem fonte, sem semente, sem
# normalização e sem regra de substituição. A tela dizia que *"o método é conteúdo publicado do
# Edital"*, e o documento saiu sem ele. Sem método publicado, a verificação pública que a `021`
# construiu fica sem base normativa: não há contra o que conferir o sorteio.


def test_marco_que_sorteia_sem_metodo_impede_a_publicacao():
    conteudo = snapshot(perfil(classificationMilestones=[de_sorteio(drawMethod=None)]))

    achado = achados(conteudo, "drawn_milestone_without_method")

    assert len(achado) == 1
    assert achado[0].severity == Severity.BLOCKING_ERROR
    assert "SORT-X" in achado[0].message
    assert "nem próprio, nem comum" in achado[0].message
    assert achado[0].path.endswith(f"/classificationMilestones/id={MARCO}/drawMethod")


def test_o_metodo_comum_do_edital_satisfaz_o_marco_que_o_referencia():
    """`FR-429` da `030`: o marco que não declara o próprio referencia o comum, e ele governa.

    Sem esta contraprova, a recusa leria só a chave do marco — e concluiria que sorteia sem método
    justamente o Edital que declarou o método **uma vez**, para todos os marcos, que é a forma que
    a `030` criou.
    """
    conteudo = snapshot(
        perfil(classificationMilestones=[de_sorteio(drawMethod=None)]), drawMethod=dict(METODO)
    )

    assert achados(conteudo, "drawn_milestone_without_method") == []


def test_metodo_pela_metade_continua_sendo_o_achado_antigo_e_nao_este():
    """A separação que importa: `draw_method_invalid` é da `026`, e trata da **declaração**.

    Este achado trata da **ausência**. Empilhar os dois sobre o mesmo marco esconderia o que
    resolve — e trocar um pelo outro faria o método pela metade deixar de ser acusado pelo achado
    que sabe dizer **qual** dos sete campos falta.
    """
    pela_metade = {chave: valor for chave, valor in METODO.items() if chave != "substitutionRule"}
    conteudo = snapshot(perfil(classificationMilestones=[de_sorteio(drawMethod=pela_metade)]))

    assert achados(conteudo, "drawn_milestone_without_method") == []
    antigo = achados(conteudo, "draw_method_invalid")
    assert len(antigo) == 1
    assert antigo[0].severity == Severity.BLOCKING_ERROR


def test_marco_que_ordena_por_pontuacao_nao_e_cobrado_de_metodo():
    """A contraprova mais barata, e a que uma condição larga demais quebraria primeiro."""
    assert achados(snapshot(), "drawn_milestone_without_method") == []


def test_o_sorteio_sem_metodo_nao_e_cobrado_na_retificacao():
    """`FR-459` e `FR-460`, para este achado.

    `orderProduction` vazio é o estado legítimo de **todo** marco do acervo, e um Edital que
    declarou o sorteio antes desta feature não pode ficar irretificável por não ter dito o que a
    capacidade não pedia.
    """
    conteudo = snapshot(perfil(classificationMilestones=[de_sorteio(drawMethod=None)]))

    assert achados(conteudo, "drawn_milestone_without_method", ato=ATO_DE_RETIFICACAO) == []
