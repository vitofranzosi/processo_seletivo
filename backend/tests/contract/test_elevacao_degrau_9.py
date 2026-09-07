"""Edital publicado antes do degrau 9 continua vivo — e a ausência do Anexo **significa** algo.

O degrau eleva o conteúdo sem inventar norma, e é essa a régua que este módulo declara: converter
só quando a ausência tem significado declarado e verdadeiro. Lista vazia diz "este Edital não
declarou anexo nenhum", e `attachmentId: None` diz "este requisito não fornece modelo". As duas
frases são verdadeiras sobre todo Edital publicado antes deste degrau, porque a capacidade não
existia (020, R-004).

**Não elevar seria pior do que elevar.** Conteúdo em versão diferente da vigente é recusado por
`_assert_versao_canonica`, então deixar o acervo em 8 tornaria todo Edital publicado
irretificável — um certame em curso deixaria de poder ser corrigido por causa de uma feature que
ele não usa.

É o oposto do que o degrau 3→4 decidiu para `documentRequirements`, e a diferença é o significado:
lá, escrever a coleção vazia teria afirmado que o Edital não exigia documento nenhum, o que era
falso — ele exigia, em prosa.
"""

import pytest

from processo_seletivo.publicacoes.domain.elevacao import (
    DEGRAUS_DA_RAIZ,
    DEGRAUS_DE_DOCUMENTO,
    elevar,
    elevar_documento,
    elevar_valor,
)
from processo_seletivo.shared.canonical import SCHEMA_VERSION

pytestmark = [pytest.mark.contract]

REQUISITO = "22222222-2222-2222-2222-222222222222"


def conteudo_na_versao(versao):
    """Um conteúdo mínimo na versão anterior ao degrau, com um requisito sem modelo."""
    return {
        "schemaVersion": versao,
        "stages": [],
        "profiles": [],
        "documentRequirements": [
            {
                "id": REQUISITO,
                "key": "identidade",
                "name": "Documento de identificação",
                "instructions": "",
                "required": True,
                "order": 1,
                "profileId": None,
                "modalityId": None,
            }
        ],
        "maxInscricoesPorCandidato": None,
    }


def test_o_degrau_9_existe_nos_dois_niveis_e_grafa_a_ausencia():
    assert DEGRAUS_DA_RAIZ[9] == {"attachments": []}
    assert DEGRAUS_DE_DOCUMENTO == {9: {"attachmentId": None}}
    assert SCHEMA_VERSION == 9


def test_o_edital_anterior_eleva_sem_inventar_anexo():
    elevado = elevar(conteudo_na_versao(8))

    assert elevado["schemaVersion"] == 9
    assert elevado["attachments"] == []
    assert elevado["documentRequirements"][0]["attachmentId"] is None


def test_a_elevacao_e_idempotente():
    """Elevar o que já está elevado devolve o mesmo objeto, sem pagar cópia."""
    elevado = elevar(conteudo_na_versao(8))

    assert elevar(elevado) is elevado


def test_a_elevacao_nao_reescreve_o_que_ja_foi_declarado():
    conteudo = conteudo_na_versao(8)
    conteudo["attachments"] = [{"id": "3" * 8}]
    conteudo["documentRequirements"][0]["attachmentId"] = "4" * 8

    elevado = elevar(conteudo)

    assert elevado["attachments"] == [{"id": "3" * 8}]
    assert elevado["documentRequirements"][0]["attachmentId"] == "4" * 8


def test_a_elevacao_alcanca_o_conteudo_de_uma_alteracao_que_enderece_o_requisito_inteiro():
    """O `newValue` de uma Alteração não carrega versão, então é elevado pelo caminho que endereça.

    Sem isto, uma Retificação elaborada antes do degrau substituiria o requisito por uma forma sem
    `attachmentId`, e a validação da coleção publicada recusaria a publicação dela.
    """
    valor = elevar_valor(
        f"/documentRequirements/id={REQUISITO}", conteudo_na_versao(8)["documentRequirements"][0]
    )

    assert valor["attachmentId"] is None


def test_o_campo_isolado_nao_e_elevado():
    """Quem endereça um campo escreve a forma que ele já tem — elevá-lo seria corrompê-lo."""
    assert elevar_valor(f"/documentRequirements/id={REQUISITO}/name", "Outro nome") == "Outro nome"


def test_a_colecao_inteira_e_elevada_item_a_item():
    documentos = conteudo_na_versao(8)["documentRequirements"]

    elevados = elevar_valor("/documentRequirements", documentos)

    assert [item["attachmentId"] for item in elevados] == [None]


def test_elevar_documento_e_idempotente():
    documento = elevar_documento(conteudo_na_versao(8)["documentRequirements"][0])

    assert elevar_documento(documento) is documento
