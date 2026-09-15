"""O Edital mudou depois do envio: a tela avisa, e não muda nada (FR-078, FR-079).

A versão aceita é peça de um ato administrativo. Reescrevê-la depois faria a inscrição passar a
valer sob regras que ninguém aceitou — e reabrir a inscrição automaticamente faria o sistema
praticar, em nome da pessoa, um ato que só ela pratica.
"""

import pytest
from django.urls import reverse

from processo_seletivo.inscricoes.application.rascunho import anexar_documento, gravar_dados
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.publicacoes.application import selectors
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, identificar, pdf
from tests.fixtures.edital import caminho_perfil
from tests.fixtures.publicacao import retify
from tests.fixtures.selecao import (
    DOCUMENTO_DE_TODOS,
    DOCUMENTO_DO_PERFIL,
    LINHA_GERAL_DO_DOCENTE,
)

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

# Endereçamento por chave, e não por posição: o índice deixou de ser forma admitida onde há chave
# (004), e a recusa do servidor é explícita quanto a isso.
VAGAS = caminho_perfil("immediateVacancies")
# **O quadro acompanha o total** (027, FR-335). O Perfil docente do `selecao` reparte 2 vagas entre
# a ampla e a PPP; levar o total a 9 sem mover as linhas publicaria um quadro que não fecha, e a
# conferência recusa dizendo os dois números. Aqui a ampla absorve as sete novas.
LINHA_GERAL = f"{caminho_perfil()}/vacancyTable/id={LINHA_GERAL_DO_DOCENTE}/immediateVacancies"

AMPLIAR_PARA_NOVE = [
    {"targetPath": VAGAS, "operation": "REPLACE", "newValue": 9},
    {"targetPath": LINHA_GERAL, "operation": "REPLACE", "newValue": 8},
]


@pytest.fixture
def enviada(inscricao_de_maria):
    inscricao = gravar_dados(
        identidade=MARIA, inscricao=inscricao_de_maria, dados={"modality_id": MODALIDADE_AC}
    )
    for requisito, nome in ((DOCUMENTO_DE_TODOS, "rg.pdf"), (DOCUMENTO_DO_PERFIL, "d.pdf")):
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
        )
    inscricao.refresh_from_db()
    return enviar_inscricao(
        identidade=MARIA,
        inscricao=inscricao,
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key="envio-aviso-versao",
    )


def acompanhar(client, inscricao):
    identificar(client, MARIA)
    return client.get(reverse("portal:acompanhamento", args=[inscricao.id])).content.decode()


def test_sem_retificacao_nao_ha_aviso(client, enviada):
    assert "foi atualizado após sua inscrição" not in acompanhar(client, enviada)


def test_depois_da_retificacao_o_aviso_aparece(client, enviada, selecao, api_client):
    retify(api_client, selecao, AMPLIAR_PARA_NOVE)

    corpo = acompanhar(client, enviada)

    assert "Este Edital foi atualizado após sua inscrição" in corpo
    assert "Ver o Edital vigente" in corpo


def test_o_aviso_nao_altera_a_versao_aceita(client, enviada, selecao, api_client):
    aceita_antes = enviada.versao_aceita_id
    retify(api_client, selecao, AMPLIAR_PARA_NOVE)

    acompanhar(client, enviada)

    enviada.refresh_from_db()
    assert enviada.versao_aceita_id == aceita_antes
    assert enviada.versao_aceita_id != selectors.selecao_publica(edital_id=selecao.id).pk


def test_o_aviso_nao_reabre_a_inscricao(client, enviada, selecao, api_client):
    antes = Inscricao.objects.values().get(pk=enviada.pk)
    retify(api_client, selecao, AMPLIAR_PARA_NOVE)

    acompanhar(client, enviada)

    assert Inscricao.objects.values().get(pk=enviada.pk) == antes


def test_a_conferencia_continua_lendo_a_versao_aceita(client, enviada, selecao, api_client):
    """Uma conferência que se reescreve depois de uma Retificação não confere coisa alguma."""
    identificar(client, MARIA)
    antes = client.get(reverse("portal:inscricao", args=[enviada.id])).content.decode()

    retify(api_client, selecao, AMPLIAR_PARA_NOVE)

    depois = client.get(reverse("portal:inscricao", args=[enviada.id])).content.decode()
    import re

    limpar = lambda corpo: re.sub(r'value="[A-Za-z0-9]{32,}"', "TOKEN", corpo)  # noqa: E731
    assert limpar(antes) == limpar(depois)
