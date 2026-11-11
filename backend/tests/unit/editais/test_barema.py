"""As regras do barema da Etapa, na gravação e na conferência de publicação (146, T002).

Uma regra, duas leituras: `validate_stages` recusa o primeiro problema do rascunho, e
`validate_for_publication` lista todos sobre o conteúdo publicado — que é também o consolidado da
Retificação. Os casos daqui passam pelas duas, para que nenhuma divirja da outra.
"""

from decimal import Decimal

import pytest

from processo_seletivo.editais.domain.etapas import (
    StageValidationError,
    problemas_do_barema,
    validate_stages,
)
from processo_seletivo.editais.domain.validation import (
    BAREMA_INCOERENTE,
    blocking_findings,
    validate_for_publication,
)

ETAPA = "00000000-0000-0000-0000-000000014601"
DOUTORADO = "00000000-0000-0000-0000-000000014611"
ESPECIALIZACAO = "00000000-0000-0000-0000-000000014612"
TITULOS = "00000000-0000-0000-0000-000000014621"
LAUDO = "00000000-0000-0000-0000-000000014622"
PERFIL = "00000000-0000-0000-0000-000000014631"


def documento(identificador=TITULOS, **campos):
    return {
        "id": identificador,
        "key": f"doc-{identificador[-4:]}",
        "name": "Títulos acadêmicos",
        "required": False,
        "order": 1,
        "moment": "AT_ENROLLMENT",
        **campos,
    }


def criterio(identificador=DOUTORADO, **campos):
    return {
        "id": identificador,
        "name": "Diploma de Doutorado",
        "description": "",
        "maximumScore": Decimal("20"),
        "pointsPerUnit": Decimal("20"),
        "unitLabel": "diploma",
        "documentRequirementId": None,
        **campos,
    }


def _soma(criterios):
    """A máxima que a tela derivaria; `None` sem critério ou com máxima que não é `Decimal`."""
    maximas = [c["maximumScore"] for c in criterios]
    if not maximas or not all(isinstance(m, Decimal) for m in maximas):
        return None
    return sum(maximas, Decimal("0"))


def etapa(criterios, **campos):
    return {
        "id": ETAPA,
        "name": "Prova de Títulos",
        "order": 1,
        "forma": "PONTUADA",
        "maximumScore": _soma(criterios),
        "criteria": criterios,
        **campos,
    }


def recusa(etapa_, documentos=()):
    with pytest.raises(StageValidationError) as erro:
        validate_stages([etapa_], schedule=[], document_requirements=list(documentos))
    return erro.value


# --- o que passa ---------------------------------------------------------------------------------


def test_etapa_sem_barema_continua_valida():
    """FR-5200: sem critério, a Etapa é a de antes — sem a chave e com a lista vazia."""
    validate_stages([{"id": ETAPA, "name": "Prova", "order": 1}], schedule=[])
    validate_stages([etapa([])], schedule=[])


def test_o_barema_do_14_2026_e_valido():
    """O quickstart §1: cinco critérios, dois documentos, soma 100."""
    declaracao = documento(LAUDO, name="Declaração de exercício de docência", order=2)
    barema = [
        criterio(documentRequirementId=TITULOS),
        criterio(
            "00000000-0000-0000-0000-000000014613",
            name="Diploma de Mestrado",
            maximumScore=Decimal("15"),
            pointsPerUnit=Decimal("15"),
            documentRequirementId=TITULOS,
        ),
        criterio(
            ESPECIALIZACAO,
            name="Especialização",
            maximumScore=Decimal("10"),
            pointsPerUnit=Decimal("5"),
            unitLabel="certificado",
            documentRequirementId=TITULOS,
        ),
        criterio(
            "00000000-0000-0000-0000-000000014614",
            name="Curso de formação de orientadores",
            maximumScore=Decimal("15"),
            pointsPerUnit=Decimal("15"),
            unitLabel="certificado",
        ),
        criterio(
            "00000000-0000-0000-0000-000000014615",
            name="Exercício de docência em EaD",
            maximumScore=Decimal("40"),
            pointsPerUnit=Decimal("1"),
            unitLabel="mês",
            documentRequirementId=LAUDO,
        ),
    ]
    assert etapa(barema)["maximumScore"] == Decimal("100")

    validate_stages([etapa(barema)], schedule=[], document_requirements=[documento(), declaracao])


def test_pontuacao_direta_nao_tem_pontos_nem_unidade():
    """FR-5202: a ficha de entrevista por faixas é pontuação direta, com as faixas na descrição."""
    direta = criterio(
        name="Entrevista",
        description="Fracos: 0 a 5; Bons: 6 a 10.",
        maximumScore=Decimal("10"),
        pointsPerUnit=None,
        unitLabel="",
    )
    validate_stages([etapa([direta])], schedule=[])


def test_a_mesma_regra_le_o_decimal_publicado():
    """O conteúdo publicado traz `"20.0000"`; o rascunho, `Decimal`. A leitura é uma só."""
    publicado = etapa(
        [criterio(maximumScore="20.0000", pointsPerUnit="20.0000")], maximumScore="20.0000"
    )

    assert problemas_do_barema(publicado, []) == []


# --- cada recusa (FR-5201, FR-5203, FR-5204, FR-5205, SC-1626, SC-1634) ----------------------


@pytest.mark.parametrize("nome", ["", "   "])
def test_criterio_sem_nome_e_recusado(nome):
    erro = recusa(etapa([criterio(name=nome)]))
    assert (erro.campo, erro.identidade) == ("name", DOUTORADO)
    assert "precisa de nome" in str(erro)


def test_nome_repetido_na_etapa_e_recusado():
    outro = criterio(ESPECIALIZACAO, name="diploma de doutorado ")
    erro = recusa(etapa([criterio(), outro]))
    assert (erro.campo, erro.identidade) == ("name", ESPECIALIZACAO)
    assert "se chamam" in str(erro)


@pytest.mark.parametrize("maxima", [None, Decimal("0"), Decimal("-5")])
def test_maxima_ausente_zero_ou_negativa_e_recusada(maxima):
    barema = [criterio(maximumScore=maxima, pointsPerUnit=None, unitLabel="")]
    erro = recusa(etapa(barema, maximumScore=Decimal("1")))
    assert erro.campo == "maximumScore"


def test_maxima_com_mais_de_quatro_casas_e_recusada():
    barema = [criterio(maximumScore=Decimal("1.00001"), pointsPerUnit=None, unitLabel="")]
    erro = recusa(etapa(barema))
    assert erro.campo == "maximumScore"
    assert "quatro casas" in str(erro)


def test_pontos_acima_da_maxima_sao_recusados():
    erro = recusa(etapa([criterio(pointsPerUnit=Decimal("25"))]))
    assert erro.campo == "pointsPerUnit"
    assert "uma unidade só já passaria do teto" in str(erro)


def test_pontos_sem_unidade_sao_recusados():
    erro = recusa(etapa([criterio(unitLabel="  ")]))
    assert erro.campo == "unitLabel"


def test_unidade_sem_pontos_e_recusada():
    """A unidade sozinha não diz como se pontua: o texto manda escolher uma das duas formas."""
    erro = recusa(etapa([criterio(pointsPerUnit=None, unitLabel="certificado")]))
    assert erro.campo == "pointsPerUnit"
    assert "apague a unidade" in str(erro)


def test_soma_diferente_da_maxima_da_etapa_e_recusada():
    """D-003, FR-5203, SC-1626: a máxima da Etapa é a soma — e a mensagem diz quanto deve ser."""
    erro = recusa(etapa([criterio()], maximumScore=Decimal("100")))
    assert (erro.campo, erro.identidade) == ("maximumScore", ETAPA)
    assert "a soma das máximas dos critérios do barema, 20" in str(erro)


def test_maxima_da_etapa_ausente_com_barema_e_recusada():
    erro = recusa(etapa([criterio()], maximumScore=None))
    assert erro.campo == "maximumScore"


def test_soma_acima_do_que_a_coluna_comporta_e_recusada():
    grandes = [
        criterio(
            f"00000000-0000-0000-0000-00000001461{indice}",
            name=f"Critério {indice}",
            maximumScore=Decimal("600"),
            pointsPerUnit=None,
            unitLabel="",
        )
        for indice in range(2)
    ]
    erro = recusa(etapa(grandes))
    assert erro.campo == "criteria"
    assert "999,9999" in str(erro)


def test_identidade_de_criterio_repetida_e_recusada_na_gravacao():
    """Sem isto, a linha repetida chegava ao `bulk_create` e o banco a recusava com erro cru."""
    repetido = criterio(ESPECIALIZACAO, name="Especialização")
    outra_etapa = {
        **etapa([criterio(ESPECIALIZACAO, name="Especialização")]),
        "id": "00000000-0000-0000-0000-000000014602",
        "name": "Entrevista",
        "order": 2,
    }
    for etapas_ in ([etapa([criterio(), repetido, repetido])], [etapa([repetido]), outra_etapa]):
        with pytest.raises(StageValidationError, match="repete a identidade") as erro:
            validate_stages(etapas_, schedule=[])
        assert erro.value.campo == "criteria"


def test_barema_em_etapa_decisoria_e_recusado():
    """FR-5204: a decisória não produz nota."""
    erro = recusa(etapa([criterio()], forma="DECISORIA", maximumScore=None))
    assert (erro.campo, erro.identidade) == ("criteria", ETAPA)
    assert "concluída com decisão, sem nota" in str(erro)


def test_documento_inexistente_e_recusado():
    erro = recusa(etapa([criterio(documentRequirementId=TITULOS)]), documentos=[])
    assert (erro.campo, erro.identidade) == ("documentRequirementId", DOUTORADO)
    assert "não está entre os Documentos Exigidos" in str(erro)


def test_documento_da_convocacao_e_recusado():
    erro = recusa(
        etapa([criterio(documentRequirementId=TITULOS)]),
        documentos=[documento(moment="AT_CALL")],
    )
    assert "pedido na convocação" in str(erro)


@pytest.mark.parametrize(
    "restricao",
    [
        {"profileId": PERFIL},
        {"modalityCode": "PCD"},
        {"profileId": PERFIL, "modalityId": "00000000-0000-0000-0000-000000014641"},
        {"modalityId": "00000000-0000-0000-0000-000000014641"},
        {"requiredWhen": "no caso de quem declarou experiência"},
    ],
    ids=["perfil", "modalidade-transversal", "perfil-e-modalidade", "modalidade", "condicao"],
)
def test_documento_com_aplicabilidade_restrita_e_recusado(restricao):
    """D-010, SC-1634: o barema vale para toda inscrição, e o documento também precisa valer."""
    erro = recusa(
        etapa([criterio(documentRequirementId=TITULOS)]),
        documentos=[documento(**restricao)],
    )
    assert erro.campo == "documentRequirementId"
    assert "não é pedido a toda inscrição" in str(erro)


# --- a conferência de publicação ------------------------------------------------------------------


def publicado(criterios, documentos, **campos_da_etapa):
    return {
        "stages": [
            {
                **etapa([], **campos_da_etapa),
                "criteria": criterios,
            }
        ],
        "documentRequirements": documentos,
    }


def criterio_publicado(**campos):
    return {
        "id": DOUTORADO,
        "name": "Diploma de Doutorado",
        "description": "",
        "maximumScore": "20.0000",
        "pointsPerUnit": "20.0000",
        "unitLabel": "diploma",
        "documentRequirementId": TITULOS,
        **campos,
    }


def achados_do_barema(snapshot):
    return [
        achado
        for achado in blocking_findings(validate_for_publication(snapshot))
        if "/criteria" in achado.path or achado.code == BAREMA_INCOERENTE
    ]


def test_a_publicacao_aceita_o_barema_coerente():
    snapshot = publicado([criterio_publicado()], [documento()], maximumScore="20.0000")

    assert achados_do_barema(snapshot) == []


def test_a_restricao_acrescentada_depois_do_vinculo_impede_a_publicacao():
    """SC-1634: a Retificação do documento não passa pela gravação; a conferência a pega."""
    snapshot = publicado(
        [criterio_publicado()], [documento(profileId=PERFIL)], maximumScore="20.0000"
    )

    achados = achados_do_barema(snapshot)
    assert [achado.code for achado in achados] == [BAREMA_INCOERENTE]
    assert achados[0].path == f"/stages/id={ETAPA}/criteria/id={DOUTORADO}/documentRequirementId"


def test_a_publicacao_recusa_a_soma_divergente():
    """FR-5203: o conteúdo que chega por outro caminho que não a tela."""
    snapshot = publicado([criterio_publicado()], [documento()], maximumScore="100.0000")

    achados = achados_do_barema(snapshot)
    assert [achado.path for achado in achados] == [f"/stages/id={ETAPA}/maximumScore"]
    assert "a soma das máximas" in achados[0].message


def test_a_publicacao_confere_a_forma_de_cada_criterio():
    """`CRITERIO_PUBLICADO`: a chave ausente é achado de forma, e a regra não é lida por cima."""
    incompleto = criterio_publicado()
    del incompleto["unitLabel"]
    snapshot = publicado([incompleto], [documento()], maximumScore="20.0000")

    achados = achados_do_barema(snapshot)
    assert [achado.code for achado in achados] == ["field_required"]
    assert achados[0].path.endswith(f"/criteria/id={DOUTORADO}/unitLabel")


def test_a_publicacao_recusa_identidade_de_criterio_repetida():
    """A Retificação poderia acrescentar um critério com o id de outro: a mesma regra pega."""
    snapshot = publicado(
        [criterio_publicado(), criterio_publicado(name="Mestrado")],
        [documento()],
        maximumScore="40.0000",
    )

    achados = achados_do_barema(snapshot)
    assert any("repete a identidade" in achado.message for achado in achados)


def test_a_etapa_publicada_sem_a_lista_e_achado_de_forma():
    """Degrau 21: `criteria` é sempre presente no conteúdo publicado."""
    snapshot = {"stages": [{"id": ETAPA, "name": "Prova", "order": 1}]}

    caminhos = [achado.path for achado in blocking_findings(validate_for_publication(snapshot))]
    assert f"/stages/id={ETAPA}/criteria" in caminhos
