"""A destinação no relatório do Edital, e o PDF que não muda (155, T043, FR-6338, FR-6339).

Os atos são os de `tests/portal/test_destinacao_na_selecao.py`, gravados direto no banco: o que se
verifica aqui é a leitura, e não o ato.
"""

import dataclasses

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.interface import relatorio_do_edital, relatorio_pdf
from processo_seletivo.ocupacao.application.selectors import DESFAZIMENTO_DA_DESTINACAO
from tests.integration.relatorio.conftest import Enderecos
from tests.interface.conftest import identificar
from tests.portal import test_destinacao_na_selecao as atos
from tests.portal.test_destinacao_na_selecao import (
    FRASE_DO_EDITAL,
    FUNDAMENTO_DA_DECLARACAO,
    MOTIVO_DO_DESFAZIMENTO,
)

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

# As mesmas fixtures da página pública: os dois lados leem o mesmo seletor, e o cenário é um só.
certame = atos.certame
com_atos = atos.com_atos


def test_a_pagina_mostra_os_mesmos_dados_e_o_desfazimento_citando(client, seletor_ligado, com_atos):
    """FR-6338: origem, destino, quantidade e fundamento; o desfazimento cita o que desfaz."""
    identificar(client, "gustavo.gestor", ["gestor"])
    resposta = client.get(reverse("interface:relatorio-do-edital", args=[com_atos["edital"].id]))
    assert resposta.status_code == 200
    corpo = resposta.content.decode()

    secao = corpo[corpo.index('id="titulo-destinacao"') :]
    secao = secao[: secao.index("</section>")]
    assert "Destinação das vagas" in secao
    assert "Pretos, pardos e indígenas (PPI)" in secao
    assert "ampla concorrência" in secao
    assert "não preenchida" in secao
    assert FRASE_DO_EDITAL in secao
    assert MOTIVO_DO_DESFAZIMENTO in secao
    assert FUNDAMENTO_DA_DECLARACAO in secao
    assert "desfaz o registro de" in secao

    lido = resposta.context["relatorio"]
    desfazimento = next(d for d in lido.destinacoes if d["especie"] == DESFAZIMENTO_DA_DESTINACAO)
    assert desfazimento["desfaz"] is lido.destinacoes[0]


def test_o_pdf_nao_muda(com_atos):
    """FR-6339: o mesmo documento, byte a byte, com e sem a destinação no relatório."""
    lido = relatorio_do_edital.ler(com_atos["edital"], agora=timezone.now(), enderecos=Enderecos())
    assert lido.destinacoes

    com = relatorio_pdf.compor(lido, emissao=1)
    sem = relatorio_pdf.compor(dataclasses.replace(lido, destinacoes=[]), emissao=1)
    assert com == sem
