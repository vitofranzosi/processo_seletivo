"""Ocultar do PDF não oculta de mais nada (144, FR-5112, P-2).

A visibilidade é da tabela do Cronograma do PDF, e só dela. Os outros canais que mostram o
Cronograma continuam mostrando todos os Eventos — decisão do usuário de 10/11/2026: a página pública
é onde o candidato confere o calendário, e esconder lá um Evento que o sistema executa é outra
decisão de norma.

**A prova é a saída idêntica**, com e sem a marca: mais forte do que procurar o Evento no resultado,
porque pega também o canal que mudasse a ordem, a contagem ou a frase por causa dela. Estes são os
canais que leem o conteúdo por função pura — a página pública da seleção, o assistente de dúvidas, a
Agenda e o relatório do Edital. Os que pedem Edital publicado no banco — a leitura pela API e o Kit
de Divulgação — estão em `integration/editais/test_cronograma_visibilidade.py`.
"""

import copy
from dataclasses import replace
from datetime import datetime
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest

from processo_seletivo.duvidas.domain import cobertura
from processo_seletivo.duvidas.domain.respostas import responder
from processo_seletivo.interface import agenda, relatorio_do_edital
from processo_seletivo.portal import leitura
from tests.fixtures.corpus import contexto_do_corpus
from tests.unit.duvidas.conftest import em
from tests.unit.publicacoes.cenarios_da_auditoria import congelado

AGORA = datetime(2026, 10, 20, 12, tzinfo=ZoneInfo("America/Sao_Paulo"))


def com_todos_ocultos(conteudo):
    oculto = copy.deepcopy(conteudo)
    for evento in oculto["schedule"]:
        evento["shownInPdf"] = False
    return oculto


@pytest.fixture
def conteudo():
    return congelado("A")["content"]


def test_pagina_publica_da_selecao_mostra_o_oculto(conteudo):
    assert leitura.cronograma(com_todos_ocultos(conteudo), AGORA) == leitura.cronograma(
        conteudo, AGORA
    )
    assert len(leitura.cronograma(com_todos_ocultos(conteudo), AGORA)) == len(conteudo["schedule"])


def test_assistente_ve_o_oculto():
    """A pergunta do recurso cita o Evento do prazo recursal, oculto ou não."""
    contexto = contexto_do_corpus("01", em("2026-10-20T12:00:00-03:00"))
    oculto = replace(contexto, conteudo=com_todos_ocultos(contexto.conteudo))

    assert responder(oculto, "P-08", perfil="DOC-INFO") == responder(
        contexto, "P-08", perfil="DOC-INFO"
    )
    assert cobertura.COBERTURA["/schedule/*/shownInPdf"][0] == "EXCLUIDO"


def test_agenda_mostra_o_oculto(conteudo):
    edital = SimpleNamespace(encerrado=False)

    assert agenda.marcos_do_conteudo(
        edital, com_todos_ocultos(conteudo), AGORA
    ) == agenda.marcos_do_conteudo(edital, conteudo, AGORA)
    assert agenda.marcos_do_conteudo(edital, com_todos_ocultos(conteudo), AGORA)


def test_relatorio_do_edital_mostra_o_oculto(conteudo):
    def linhas(vigente):
        return relatorio_do_edital._cronograma(
            vigente, vigente, [], {}, {}, vigente.get("stages") or []
        )

    assert linhas(com_todos_ocultos(conteudo)) == linhas(conteudo)
    assert len(linhas(com_todos_ocultos(conteudo))) == len(conteudo["schedule"])
