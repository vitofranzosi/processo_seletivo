"""Os documentos da convocação no PDF do Edital (115, FR-3569, SC-1085).

Título próprio e neutro, depois dos da inscrição, e só quando há algum: o Edital que não pede
documento na convocação sai exatamente como saía.
"""

import pytest

from processo_seletivo.editais.domain import secoes as catalogo
from tests.unit.publicacoes.test_pdf import documento, secoes, snapshot, texto_de

IDENTIDADE = "00000000-0000-0000-0000-000000011511"
CERTIDAO = "00000000-0000-0000-0000-000000011512"
CERTIFICADO = "00000000-0000-0000-0000-000000011513"
CERTIFICADO_NA_CONVOCACAO = "00000000-0000-0000-0000-000000011514"

DA_INSCRICAO = [
    {
        "id": IDENTIDADE,
        "key": "identidade",
        "name": "Documento de identificação",
        "instructions": "",
        "required": True,
        "order": 1,
        "profileId": None,
        "modalityId": None,
        "attachmentId": None,
        "modalityCode": None,
    },
    {
        "id": CERTIFICADO,
        "key": "certificado",
        "name": "Certificado do curso de formação",
        "instructions": "",
        "required": False,
        "order": 2,
        "profileId": None,
        "modalityId": None,
        "attachmentId": None,
        "modalityCode": None,
    },
]
DA_CONVOCACAO = [
    {
        **DA_INSCRICAO[0],
        "id": CERTIDAO,
        "key": "certidao",
        "name": "Certidão de nascimento ou casamento",
        "order": 3,
        "moment": "AT_CALL",
        "reusesRequirementId": None,
    },
    {
        **DA_INSCRICAO[1],
        "id": CERTIFICADO_NA_CONVOCACAO,
        "key": "certificado-na-convocacao",
        "required": True,
        "order": 4,
        "moment": "AT_CALL",
        "reusesRequirementId": CERTIFICADO,
    },
]

TERMOS_DE_VINCULO = ("matrícula", "Matrícula", "bolsa", "vinculação", "contratação")


@pytest.mark.parametrize("catalogo_", [catalogo.CATALOGO_DA_054, catalogo.CATALOGO_DA_069])
def test_os_da_convocacao_saem_sob_titulo_proprio_depois_dos_da_inscricao(catalogo_):
    texto = texto_de(
        documento(
            snapshot(
                documentRequirements=DA_INSCRICAO + DA_CONVOCACAO,
                sections=secoes(catalogo_=catalogo_),
            )
        )
    )

    titulo = texto.index("Documentos exigidos na convocação")
    assert texto.index("Documento de identificação") < titulo
    assert titulo < texto.index("Certidão de nascimento ou casamento")
    assert "Quem enviou Certificado do curso de formação na inscrição" in texto


def test_o_titulo_da_secao_e_neutro():
    from processo_seletivo.publicacoes.infrastructure.pdf import (
        TITULO_DOS_DOCUMENTOS_NA_CONVOCACAO,
    )

    assert not any(termo in TITULO_DOS_DOCUMENTOS_NA_CONVOCACAO for termo in TERMOS_DE_VINCULO)


def test_sem_documento_na_convocacao_o_pdf_e_o_de_antes():
    """SC-1085: o documento sem o campo novo e o com `moment` da inscrição são o mesmo texto."""
    sem_campo = texto_de(documento(snapshot(documentRequirements=DA_INSCRICAO, sections=secoes())))
    com_campo = texto_de(
        documento(
            snapshot(
                documentRequirements=[
                    {**item, "moment": "AT_ENROLLMENT", "reusesRequirementId": None}
                    for item in DA_INSCRICAO
                ],
                sections=secoes(),
            )
        )
    )

    assert sem_campo == com_campo
    assert "Documentos exigidos na convocação" not in sem_campo


@pytest.mark.parametrize("catalogo_", [catalogo.CATALOGO_DA_054, catalogo.CATALOGO_DA_069])
def test_a_frase_do_aproveitamento_nao_dobra_o_ponto_da_instrucao(catalogo_):
    """A instrução que termina em ponto — a maioria — não ganha um segundo antes da frase."""
    com_instrucao = [
        DA_CONVOCACAO[0],
        {**DA_CONVOCACAO[1], "instructions": "Frente e verso, em arquivo único."},
    ]
    texto = texto_de(
        documento(
            snapshot(
                documentRequirements=DA_INSCRICAO + com_instrucao,
                sections=secoes(catalogo_=catalogo_),
            )
        )
    )

    assert "arquivo único. Quem enviou Certificado do curso de formação" in " ".join(texto.split())
    assert ".." not in texto
