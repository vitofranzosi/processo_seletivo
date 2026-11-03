"""O momento do Documento Exigido e o aproveitamento, como regra de domínio (115, US7).

O que se prova é que **toda leitura da inscrição continua pedindo só o da inscrição** sem saber que
a convocação também pede documento, e que o aproveitamento só existe da convocação para a inscrição,
num passo só (FR-3563, FR-3566, FR-3568).
"""

import pytest

from processo_seletivo.editais.domain.documentos import (
    NA_CONVOCACAO,
    NA_INSCRICAO,
    DocumentRequirementValidationError,
    aplicabilidade,
    aplicaveis,
    do_momento,
    momento_de,
    problemas_do_momento,
    validate_document_requirements,
)

PERFIL = "00000000-0000-0000-0000-0000000115a1"


def _documento(identidade, *, momento=None, aproveita=None, ordem=1, nome=None):
    documento = {
        "id": identidade,
        "key": f"chave-{identidade[-2:]}",
        "name": nome or f"Documento {identidade[-2:]}",
        "required": True,
        "order": ordem,
    }
    if momento is not None:
        documento["moment"] = momento
    if aproveita is not None:
        documento["reusesRequirementId"] = aproveita
    return documento


INSCRICAO = "00000000-0000-0000-0000-000000011501"
CONVOCACAO = "00000000-0000-0000-0000-000000011502"


def _conteudo(*documentos):
    return {
        "profiles": [{"id": PERFIL, "competitionModalities": []}],
        "documentRequirements": list(documentos),
    }


def test_a_ausencia_do_momento_e_a_inscricao():
    assert momento_de({"id": INSCRICAO}) == NA_INSCRICAO
    assert momento_de({"id": INSCRICAO, "moment": None}) == NA_INSCRICAO


def test_do_momento_separa_os_dois_conjuntos():
    a = _documento(INSCRICAO)
    b = _documento(CONVOCACAO, momento=NA_CONVOCACAO, ordem=2)

    assert do_momento([a, b], NA_INSCRICAO) == [a]
    assert do_momento([a, b], NA_CONVOCACAO) == [b]


def test_a_aplicabilidade_padrao_nao_ve_o_documento_da_convocacao():
    """FR-3568: o cartão, o rascunho, o envio, a lista e a Mesa leem daqui, e só pela inscrição."""
    conteudo = _conteudo(
        _documento(INSCRICAO), _documento(CONVOCACAO, momento=NA_CONVOCACAO, ordem=2)
    )

    vereditos = aplicabilidade(conteudo, profile_id=PERFIL, modality_id=None)
    assert [v.requisito["id"] for v in vereditos] == [INSCRICAO]
    assert [r["id"] for r in aplicaveis(conteudo, profile_id=PERFIL, modality_id=None)] == [
        INSCRICAO
    ]


def test_a_aplicabilidade_da_convocacao_ve_so_o_documento_da_convocacao():
    conteudo = _conteudo(
        _documento(INSCRICAO), _documento(CONVOCACAO, momento=NA_CONVOCACAO, ordem=2)
    )

    vereditos = aplicabilidade(conteudo, profile_id=PERFIL, modality_id=None, momento=NA_CONVOCACAO)
    assert [(v.requisito["id"], v.situacao) for v in vereditos] == [(CONVOCACAO, "OBRIGATORIO")]


def test_o_aproveitamento_valido_nao_tem_problema():
    """O caso do 89/2026: facultativo na inscrição, obrigatório na convocação (FR-3567)."""
    inscricao = {**_documento(INSCRICAO), "required": False}
    convocacao = _documento(CONVOCACAO, momento=NA_CONVOCACAO, aproveita=INSCRICAO, ordem=2)

    assert problemas_do_momento([inscricao, convocacao]) == []


@pytest.mark.parametrize(
    "documentos, campo",
    [
        # o da inscrição não aproveita
        (
            [
                _documento(INSCRICAO, aproveita=CONVOCACAO),
                _documento(CONVOCACAO, momento=NA_CONVOCACAO, ordem=2),
            ],
            "reusesRequirementId",
        ),
        # aproveita documento que não é deste Edital
        (
            [
                _documento(
                    CONVOCACAO,
                    momento=NA_CONVOCACAO,
                    aproveita="00000000-0000-0000-0000-0000000115ff",
                )
            ],
            "reusesRequirementId",
        ),
        # aproveita a si mesmo
        (
            [_documento(CONVOCACAO, momento=NA_CONVOCACAO, aproveita=CONVOCACAO)],
            "reusesRequirementId",
        ),
        # aproveita outro da convocação: sem cadeia
        (
            [
                _documento(INSCRICAO, momento=NA_CONVOCACAO),
                _documento(CONVOCACAO, momento=NA_CONVOCACAO, aproveita=INSCRICAO, ordem=2),
            ],
            "reusesRequirementId",
        ),
        # momento que não existe
        ([_documento(INSCRICAO, momento="AT_INTERVIEW")], "moment"),
    ],
)
def test_o_aproveitamento_incoerente_e_recusado(documentos, campo):
    problemas = problemas_do_momento(documentos)

    assert problemas and problemas[0][1] == campo
    with pytest.raises(DocumentRequirementValidationError) as recusa:
        validate_document_requirements(documentos, profiles=[])
    assert recusa.value.campo == campo
