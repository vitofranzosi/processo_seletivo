"""A condição de exigência do Documento Exigido, na composição e na publicação (131, US1).

O que se prova:

- a condição é texto, lido só do campo, e o vazio é ausência (FR-4452, FR-4477);
- ela cabe só no obrigatório da convocação, e a regra é uma só para o rascunho e a publicação
  (FR-4453);
- o PDF a escreve depois do nome, como os Editais da amostra, e o documento sem condição sai como
  antes (FR-4454);
- o reaproveitamento de Edital anterior a leva junto (FR-4455).
"""

import pytest

from processo_seletivo.editais.domain.documentos import (
    LIMITE_DA_CONDICAO,
    NA_CONVOCACAO,
    DocumentRequirementValidationError,
    condicao_de,
    problemas_da_condicao,
    validate_document_requirements,
)
from processo_seletivo.editais.domain.reaproveitamento import mapa_de_identidades, remapear
from processo_seletivo.editais.domain.validation import Severity, validate_for_publication
from processo_seletivo.publicacoes.infrastructure.pdf import texto_do_documento
from tests.fixtures.snapshot import rascunho_completo

CONDICAO = "no caso de candidatos do sexo masculino, maiores de 18 anos"
ALISTAMENTO = "00000000-0000-0000-0000-000000013101"


def _documento(*, momento=NA_CONVOCACAO, obrigatorio=True, condicao=CONDICAO, **extra):
    return {
        "id": ALISTAMENTO,
        "key": "alistamento",
        "name": "Certificado de alistamento militar ou de reservista",
        "required": obrigatorio,
        "order": 1,
        "moment": momento,
        "requiredWhen": condicao,
        **extra,
    }


@pytest.mark.parametrize(
    "valor, esperado",
    [
        (None, None),
        ("", None),
        ("   ", None),
        (f"  {CONDICAO}  ", CONDICAO),
        (17, None),
    ],
)
def test_a_condicao_e_o_campo_aparado_e_o_vazio_e_ausencia(valor, esperado):
    assert condicao_de({"requiredWhen": valor}) == esperado


def test_a_versao_sem_o_campo_e_incondicional_e_nada_se_infere_da_instrucao():
    """FR-4477, D-012: a instrução que diz a condição não é condição publicada."""
    antigo = {"id": ALISTAMENTO, "instructions": "Apenas para candidatos do sexo masculino."}

    assert condicao_de(antigo) is None


def test_o_obrigatorio_da_convocacao_admite_condicao():
    assert problemas_da_condicao([_documento()]) == []
    validate_document_requirements([_documento()], profiles=[])


@pytest.mark.parametrize(
    "ajuste",
    [
        {"obrigatorio": False},
        {"momento": "AT_ENROLLMENT"},
        {"condicao": "x" * (LIMITE_DA_CONDICAO + 1)},
    ],
    ids=["facultativo", "inscricao", "longa"],
)
def test_a_condicao_fora_do_lugar_e_recusada_no_rascunho(ajuste):
    documento = _documento(**ajuste)

    assert [campo for _, campo, _ in problemas_da_condicao([documento])] == ["requiredWhen"]
    with pytest.raises(DocumentRequirementValidationError) as recusa:
        validate_document_requirements([documento], profiles=[])
    assert recusa.value.campo == "requiredWhen"


def _achados_da_condicao(documento):
    conteudo = rascunho_completo()
    conteudo.update({"title": "Edital", "description": "Descrição"})
    conteudo["documentRequirements"] = [*conteudo["documentRequirements"], documento]
    return [
        achado
        for achado in validate_for_publication(conteudo)
        if achado.code == "document_requirement_condition_incoherent"
    ]


def test_a_publicacao_impede_a_condicao_no_facultativo():
    """A Retificação alcança o documento sem passar pela tela, e a publicação é onde ela para."""
    achados = _achados_da_condicao(_documento(obrigatorio=False, order=9, key="outro"))

    assert [achado.severity for achado in achados] == [Severity.BLOCKING_ERROR]
    assert achados[0].path.endswith("/requiredWhen")


def test_a_publicacao_aceita_a_condicao_no_obrigatorio_da_convocacao():
    assert _achados_da_condicao(_documento(order=9, key="outro")) == []


def test_o_pdf_escreve_a_condicao_depois_do_nome():
    texto = texto_do_documento(_documento(instructions="Frente e verso."))

    assert texto == (
        "Certificado de alistamento militar ou de reservista, no caso de candidatos do sexo "
        "masculino, maiores de 18 anos — frente e verso."
    )


def test_o_documento_sem_condicao_sai_no_pdf_como_antes():
    sem = _documento(condicao=None, instructions="Frente e verso.")
    antes = {chave: valor for chave, valor in sem.items() if chave != "requiredWhen"}

    assert texto_do_documento(sem) == texto_do_documento(antes)


def test_o_reaproveitamento_leva_a_condicao():
    conteudo = rascunho_completo()
    origem = next(d for d in conteudo["documentRequirements"] if d.get("requiredWhen"))

    copia = remapear(conteudo, mapa_de_identidades(conteudo))

    destino = next(d for d in copia["documentRequirements"] if d["key"] == origem["key"])
    assert destino["requiredWhen"] == origem["requiredWhen"]
