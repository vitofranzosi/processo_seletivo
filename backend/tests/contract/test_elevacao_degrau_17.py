"""Edital publicado antes do degrau 17 continua vivo — e a ausência do código **significa** algo.

`modalityCode: None` diz "este requisito não recorta pelo código da Modalidade", e é verdade sobre
todo documento publicado antes do degrau: a capacidade não existia (044, R-002). É o molde do
degrau 9 — aditivo, dentro de uma coleção que já existe.

O que o degrau **não** faz também é contrato: a consulta pública, o comprovante e o documento de
uma Publicação servem o conteúdo **literal**, que é o que o `content_hash` cobre (FR-725). Elevar é
coisa do fluxo de Retificação, e nada que já foi publicado muda.
"""

import copy

import pytest

from processo_seletivo.publicacoes.domain.elevacao import (
    DEGRAUS_DE_DOCUMENTO,
    elevar,
    elevar_documento,
)
from processo_seletivo.shared.canonical import SCHEMA_VERSION, canonical_sha256

pytestmark = [pytest.mark.contract]

REQUISITO = "22222222-2222-2222-2222-222222222222"


def conteudo_na_versao(versao):
    return {
        "schemaVersion": versao,
        "stages": [],
        "profiles": [],
        "attachments": [],
        "documentRequirements": [
            {
                "id": REQUISITO,
                "key": "laudo",
                "name": "Laudo médico",
                "instructions": "",
                "required": True,
                "order": 1,
                "profileId": None,
                "modalityId": None,
                "attachmentId": None,
            }
        ],
        "maxInscricoesPorCandidato": None,
    }


def test_o_degrau_17_grafa_a_ausencia_do_codigo():
    assert DEGRAUS_DE_DOCUMENTO[17] == {"modalityCode": None}
    assert SCHEMA_VERSION >= 17


def test_o_documento_anterior_eleva_sem_inventar_recorte():
    elevado = elevar(conteudo_na_versao(16))

    assert elevado["schemaVersion"] == SCHEMA_VERSION
    assert elevado["documentRequirements"][0]["modalityCode"] is None


def test_elevar_nao_toca_o_literal_e_e_idempotente():
    literal = conteudo_na_versao(16)
    antes = canonical_sha256(literal)
    copia = copy.deepcopy(literal)

    uma = elevar(literal)
    duas = elevar(uma)

    assert literal == copia, "a elevação não escreve no conteúdo que recebeu"
    assert canonical_sha256(literal) == antes
    assert uma == duas


def test_o_codigo_declarado_atravessa_a_elevacao():
    documento = {**conteudo_na_versao(17)["documentRequirements"][0], "modalityCode": "PcD"}

    assert elevar_documento(documento, de=16)["modalityCode"] == "PcD"
