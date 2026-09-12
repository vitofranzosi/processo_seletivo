"""A regra de corte na elaboração e na publicação (014).

**Dois momentos, e a divisão não é arbitrária.** A forma do alvo é o que o Perfil sozinho consegue
responder, e mora em `validate_profiles`. O que depende do conteúdo inteiro — a Etapa governada
existir, o quadro ter linha para cada recorte, dois marcos não governarem a mesma Etapa — é achado
da operação de publicar, pela mesma razão que a coerência dos marcos já está lá.

**Quatro dos seis campos não têm padrão**, e é por isso que metade deste arquivo testa recusa de
ausência: resolver o silêncio por conta própria afirmaria norma que ninguém escreveu.
"""

import uuid

import pytest

from processo_seletivo.editais.domain.perfis import ProfileValidationError, validate_profiles
from processo_seletivo.editais.domain.validation import blocking_findings, validate_for_publication

PERFIL = str(uuid.uuid4())
MARCO = str(uuid.uuid4())
OUTRO_MARCO = str(uuid.uuid4())
ETAPA_1 = str(uuid.uuid4())
ETAPA_2 = str(uuid.uuid4())
PCD = str(uuid.uuid4())
PPI = str(uuid.uuid4())

METODO_DE_SORTEIO = {
    "algorithm": "IFES-SORTEIO-SHA256-v1",
    "source": "Loteria Federal",
    "occurrence": "5900",
    "occurrenceAt": "2026-11-20T20:00:00-03:00",
    "derivation": "a extração de sábado imediatamente anterior",
    "normalization": {"rule": "DIGITOS_EM_SEQUENCIA", "text": "os cinco números, na ordem"},
    "substitutionRule": {
        "rule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
        "text": "não havendo extração, vale a seguinte",
    },
}


def regra(**overrides):
    dados = {
        "targetKind": "FIXED",
        "targetCount": 10,
        "surplusCount": 0,
        "tieOutcome": "STRICT",
        "governedStage": ETAPA_2,
        "continuation": "NONE",
    }
    dados.update(overrides)
    return {chave: valor for chave, valor in dados.items() if valor is not ...}


def marco(identidade=MARCO, *, etapas=(ETAPA_1,), cut=..., **overrides):
    dados = {
        "id": identidade,
        "code": f"M-{identidade[:4]}",
        "name": "Marco",
        "stages": list(etapas),
        "operation": "SOMA_PONDERADA",
        "normalization": "NENHUMA",
        "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
        "tiebreakers": [],
        "appealWindow": None,
        "drawMethod": None,
        "cutRule": regra() if cut is ... else cut,
    }
    dados.update(overrides)
    return dados


def modalidade(identidade, code):
    return {"id": identidade, "code": code, "name": code}


def linha(quantidade, modalidade_id=None):
    return {
        "id": str(uuid.uuid4()),
        "modalityId": modalidade_id,
        "immediateVacancies": quantidade,
    }


def perfil(*marcos, modalidades=(), quadro=()):
    return {
        "id": PERFIL,
        "code": "C1",
        "name": "Curso",
        "immediateVacancies": 40,
        "reserveType": "NONE",
        "reserveLimit": None,
        "competitionModalities": list(modalidades),
        "vacancyTable": list(quadro),
        "classificationMilestones": list(marcos),
    }


def etapa(identidade, ordem):
    return {
        "id": identidade,
        "name": f"Etapa {ordem}",
        "order": ordem,
        "weight": "1.0000",
        "eliminatory": False,
        "classificatory": True,
        "minimumScore": None,
        "forma": "PONTUADA",
    }


def snapshot(*perfis, etapas=None):
    return {
        "title": "Edital",
        "description": "…",
        "schedule": [{"id": str(uuid.uuid4()), "type": "X", "description": "…"}],
        "stages": list(etapas if etapas is not None else [etapa(ETAPA_1, 1), etapa(ETAPA_2, 2)]),
        "profiles": list(perfis),
    }


#: Os prefixos que esta feature acrescentou. O snapshot destes casos é mínimo de propósito — o que
#: se verifica é a regra de corte, e não a forma publicada inteira, que tem catálogo próprio.
DA_014 = ("cut_rule_", "general_competition_")


def impeditivos(*perfis, etapas=None):
    findings = blocking_findings(validate_for_publication(snapshot(*perfis, etapas=etapas)))
    return {item.code for item in findings if item.code.startswith(DA_014)}


def mensagens(*perfis, etapas=None):
    findings = blocking_findings(validate_for_publication(snapshot(*perfis, etapas=etapas)))
    return " ".join(item.message for item in findings if item.code.startswith(DA_014))


# --- T014 · a espécie do alvo, e o alvo com uma fonte só (FR-179) ----------------------------


def test_a_regra_sem_especie_de_alvo_e_recusada():
    with pytest.raises(ProfileValidationError, match="espécie do alvo"):
        validate_profiles([perfil(marco(cut=regra(targetKind=None)))])


def test_a_regra_com_especie_desconhecida_e_recusada():
    with pytest.raises(ProfileValidationError, match="espécie do alvo"):
        validate_profiles([perfil(marco(cut=regra(targetKind="POR_PERCENTUAL")))])


def test_o_alvo_derivado_que_tambem_declara_quantidade_fixa_e_recusado():
    with pytest.raises(ProfileValidationError, match="uma fonte só"):
        validate_profiles(
            [perfil(marco(cut=regra(targetKind="FROM_VACANCY_TABLE", targetCount=10)))]
        )


def test_o_alvo_fixo_sem_quantidade_nao_derruba_o_rascunho():
    """Quem escolhe a espécie no seletor ainda não digitou o número (achado da revisão de código).

    Recusar aqui derrubaria o rascunho inteiro do Perfil — inclusive o que nada tem a ver com o
    corte —, e os outros quatro campos da mesma regra gravam em branco. Quem cobra é a publicação.
    """
    validate_profiles([perfil(marco(cut=regra(targetCount=None)))])

    assert "cut_rule_sem_alvo" in impeditivos(perfil(marco(cut=regra(targetCount=None))))


def test_a_regra_ausente_nao_e_recusada():
    """Marco que não corta é a maioria, e o rascunho legitimamente não a traz."""
    validate_profiles([perfil(marco(cut=None))])


# --- T015 · as quantidades, e o zero que é valor (FR-180) ------------------------------------


@pytest.mark.parametrize("campo", ["targetCount", "surplusCount"])
def test_quantidade_negativa_e_recusada(campo):
    with pytest.raises(ProfileValidationError, match="inteiros não negativos"):
        validate_profiles([perfil(marco(cut=regra(**{campo: -1})))])


@pytest.mark.parametrize("valor", [2.5, "10", True])
def test_quantidade_que_nao_e_inteiro_e_recusada(valor):
    with pytest.raises(ProfileValidationError, match="inteiros não negativos"):
        validate_profiles([perfil(marco(cut=regra(surplusCount=valor)))])


def test_excedente_zero_e_valor_legitimo():
    """Zero suplentes é declaração, e não ausência: a faixa é igual ao alvo."""
    validate_profiles([perfil(marco(cut=regra(surplusCount=0)))])
    assert impeditivos(perfil(marco())) == set()


# --- T016 · o desfecho do empate, que não tem padrão (FR-181, FR-182) ------------------------


def test_o_desfecho_do_empate_ausente_impede_a_publicacao():
    assert "cut_rule_sem_desfecho_de_empate" in impeditivos(
        perfil(marco(cut=regra(tieOutcome=None)))
    )


def test_o_desfecho_do_empate_desconhecido_impede_a_publicacao():
    assert "cut_rule_sem_desfecho_de_empate" in impeditivos(
        perfil(marco(cut=regra(tieOutcome="O_MAIS_VELHO")))
    )


@pytest.mark.parametrize("desfecho", ["ADMITS_SURPLUS", "STRICT"])
def test_as_duas_grafias_do_desfecho_publicam(desfecho):
    assert impeditivos(perfil(marco(cut=regra(tieOutcome=desfecho)))) == set()


# --- T018a · a Etapa governada, declarada e nunca inferida (FR-224, FR-225) ------------------


def test_a_etapa_governada_ausente_impede_e_a_mensagem_diz_que_nao_se_infere():
    perfis = perfil(marco(cut=regra(governedStage=None)))

    assert "cut_rule_sem_etapa_governada" in impeditivos(perfis)
    assert "não é inferida" in mensagens(perfis)


def test_a_etapa_governada_inexistente_impede_a_publicacao():
    assert "cut_rule_com_etapa_inexistente" in impeditivos(
        perfil(marco(cut=regra(governedStage=str(uuid.uuid4()))))
    )


def test_a_ausencia_declarada_publica_e_o_corte_nao_governa_etapa_alguma():
    """`NONE` é palavra, e não `null`: a ausência precisa ser afirmada."""
    from processo_seletivo.classificacao.domain import faixa

    regra_terminal = regra(governedStage="NONE")

    assert impeditivos(perfil(marco(cut=regra_terminal))) == set()
    assert faixa.etapa_governada(regra_terminal) is None


# --- T018b · a política de continuação (FR-226) ----------------------------------------------


def test_a_continuacao_nao_declarada_impede_a_publicacao():
    assert "cut_rule_sem_politica_de_continuacao" in impeditivos(
        perfil(marco(cut=regra(continuation=None)))
    )


@pytest.mark.parametrize("politica", ["ALLOWED", "NONE"])
def test_as_duas_politicas_de_continuacao_publicam(politica):
    assert impeditivos(perfil(marco(cut=regra(continuation=politica)))) == set()


# --- a forma do alvo **também** na publicação: a Retificação não passa pela elaboração ---------


def test_a_especie_invalida_impede_a_publicacao():
    """A Retificação afere só por `validate_for_publication`, e sem isto publicaria o inválido."""
    assert "cut_rule_sem_especie_de_alvo" in impeditivos(
        perfil(marco(cut=regra(targetKind="POR_PERCENTUAL")))
    )


def test_a_quantidade_negativa_impede_a_publicacao():
    assert "cut_rule_com_quantidade_invalida" in impeditivos(
        perfil(marco(cut=regra(targetCount=-5)))
    )


def test_o_alvo_duplicado_impede_a_publicacao():
    assert "cut_rule_com_alvo_duplicado" in impeditivos(
        perfil(marco(cut=regra(targetKind="FROM_VACANCY_TABLE", targetCount=10)))
    )


# --- T018c · alvo derivado e a linha geral (FR-183) ------------------------------------------


def quadro_completo():
    return [linha(28), linha(2, PCD), linha(10, PPI)]


def perfil_de_tres_listas(quadro):
    return perfil(
        marco(cut=regra(targetKind="FROM_VACANCY_TABLE", targetCount=None)),
        modalidades=[modalidade(PCD, "PCD"), modalidade(PPI, "PPI")],
        quadro=quadro,
    )


def test_o_alvo_derivado_com_as_tres_linhas_publica():
    assert impeditivos(perfil_de_tres_listas(quadro_completo())) == set()


def test_a_falta_da_linha_geral_impede_a_publicacao():
    quadro = [item for item in quadro_completo() if item["modalityId"]]

    assert "cut_rule_sem_linha_de_quadro" in impeditivos(perfil_de_tres_listas(quadro))


@pytest.mark.parametrize("faltando", [0, 1, 2])
def test_a_falta_de_linha_em_qualquer_recorte_impede_a_publicacao(faltando):
    """A `D-014` inteira: **todo** recorte que o marco ordena precisa de linha."""
    quadro = [item for indice, item in enumerate(quadro_completo()) if indice != faltando]

    assert "cut_rule_sem_linha_de_quadro" in impeditivos(perfil_de_tres_listas(quadro))


def test_a_mensagem_nomeia_o_recorte_que_ficou_sem_linha():
    quadro = [item for item in quadro_completo() if item["modalityId"] != PPI]

    assert "PPI" in mensagens(perfil_de_tres_listas(quadro))
    quadro_sem_geral = [item for item in quadro_completo() if item["modalityId"]]
    assert "ampla concorrência" in mensagens(perfil_de_tres_listas(quadro_sem_geral))


# --- a ampla concorrência declarada, e o formato normal de Edital (D-014) --------------------


def perfil_com_ampla_declarada(quadro, ampla=PCD):
    dados = perfil_de_tres_listas(quadro)
    dados["generalCompetitionModalityId"] = ampla
    return dados


def test_a_modalidade_declarada_como_ampla_nao_exige_linha_propria():
    """É o formato normal de Edital, e é o que destrava a conferência nele.

    O 57 e o 28 declaram **também** uma Modalidade chamada "Ampla concorrência", e a `FR-176` da
    `025` proíbe dar linha reservada a ela: a quantidade dela mora na linha geral. Sem a declaração,
    exigir linha de toda Modalidade os tornaria impublicáveis; com ela, a exigência vale inteira
    para as demais. Identificá-la casando o nome é o que a `R-006` daquela feature recusou.
    """
    quadro = [linha(28), linha(10, PPI)]

    assert impeditivos(perfil_com_ampla_declarada(quadro)) == set()


def test_as_demais_modalidades_continuam_exigindo_linha():
    """A declaração dispensa **uma**, e não afrouxa a regra para as outras."""
    quadro = [linha(28), linha(2, PCD)]

    assert "cut_rule_sem_linha_de_quadro" in impeditivos(
        perfil_com_ampla_declarada(quadro, ampla=PCD)
    )


def test_a_ampla_declarada_com_linha_propria_impede_a_publicacao():
    """A quantidade dela já está na linha geral: duas linhas para o mesmo recorte é contradição."""
    quadro = [linha(28), linha(0, PCD), linha(10, PPI)]

    assert "general_competition_modality_with_row" in impeditivos(
        perfil_com_ampla_declarada(quadro)
    )


def test_declarar_como_ampla_uma_modalidade_que_o_perfil_nao_publica_impede():
    quadro = [linha(28), linha(2, PCD), linha(10, PPI)]

    assert "general_competition_modality_unknown" in impeditivos(
        perfil_com_ampla_declarada(quadro, ampla=str(uuid.uuid4()))
    )


def test_linha_zerada_nao_e_linha_ausente():
    """Zero vaga naquele recorte é declaração legítima; o que impede é a ausência."""
    quadro = [linha(28), linha(0, PCD), linha(10, PPI)]

    assert impeditivos(perfil_de_tres_listas(quadro)) == set()


def test_o_alvo_fixo_nao_exige_quadro_nenhum():
    assert impeditivos(perfil(marco(), modalidades=[modalidade(PCD, "PCD")])) == set()


# --- T018d · a guarda é de circularidade, e não de ordem (FR-229) ----------------------------


def test_o_marco_computado_nao_governa_etapa_que_alimenta_a_propria_ordem():
    circular = marco(etapas=(ETAPA_1, ETAPA_2), cut=regra(governedStage=ETAPA_2))

    assert "cut_rule_com_etapa_circular" in impeditivos(perfil(circular))


def test_o_marco_de_sorteio_governa_a_etapa_que_enumera_e_isso_e_o_caso_normal():
    """É a forma do 77/2026, e uma guarda de ordem o tornaria impublicável.

    Lá não existe Etapa avaliada antes do sorteio: quem envia inscrição completa entra na relação
    de habilitados, sorteia-se, e só então os documentos dos primeiros são analisados. A única Etapa
    é a análise documental — que o marco **tem de enumerar**, porque o domínio exige ao menos uma, e
    que é justamente a que o corte governa. Não há laço: a ordem vem da relação, e não da Etapa.
    """
    sorteio = marco(
        etapas=(ETAPA_1,),
        cut=regra(governedStage=ETAPA_1),
        drawMethod=METODO_DE_SORTEIO,
    )

    assert impeditivos(perfil(sorteio), etapas=[etapa(ETAPA_1, 1)]) == set()


def test_o_marco_computado_governando_etapa_posterior_publica():
    assert impeditivos(perfil(marco(etapas=(ETAPA_1,), cut=regra(governedStage=ETAPA_2)))) == set()


# --- dois marcos do mesmo Perfil não governam a mesma Etapa (R-006) --------------------------


def test_dois_marcos_que_declaram_governar_a_mesma_etapa_impedem_a_publicacao():
    primeiro = marco(MARCO, etapas=(ETAPA_1,), cut=regra(governedStage=ETAPA_2))
    segundo = marco(OUTRO_MARCO, etapas=(ETAPA_1,), cut=regra(governedStage=ETAPA_2))

    assert "cut_rule_em_dois_marcos_da_mesma_etapa" in impeditivos(perfil(primeiro, segundo))


def test_dois_marcos_terminais_nao_colidem():
    """`NONE` não é Etapa: dois marcos que não governam nada não disputam coisa alguma."""
    primeiro = marco(MARCO, cut=regra(governedStage="NONE"))
    segundo = marco(OUTRO_MARCO, cut=regra(governedStage="NONE"))

    assert impeditivos(perfil(primeiro, segundo)) == set()


# --- a recusa nomeia o marco (FR-182, UX-025, E2E14-002) -------------------------------------


def test_as_recusas_da_regra_de_corte_nomeiam_o_marco():
    """Sem o código do marco, a recusa não diz qual dos três abrir (E2E14-002).

    O percurso E2E encontrou as recusas mudas: a Revisão mostrava "a regra de corte não declara o
    desfecho do empate" e um atalho para a tela dos Perfis, e ali podia haver três marcos. A
    `FR-182` pede achado que **nomeia** o marco e a `UX-025` proíbe fazê-lo por identificador
    interno — o `code` é o que quem elabora digitou e o que o documento publica.
    """
    mudo = marco(MARCO, cut=regra(tieOutcome=None, continuation=None, governedStage=None))

    texto = mensagens(perfil(mudo))

    assert texto.count(f"marco M-{MARCO[:4]}") == 3, texto
    assert MARCO not in texto, "o identificador interno não aparece na recusa"
