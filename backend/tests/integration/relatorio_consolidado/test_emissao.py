"""A emissão: numerada na unidade, registrada com o conjunto e o resumo, determinística (100,
FR-2566 a FR-2568, SC-943)."""

import hashlib

import pytest
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.interface import relatorio_consolidado as rc
from processo_seletivo.interface import relatorio_consolidado_pdf
from processo_seletivo.unidades.models import Unidade
from tests.integration.relatorio_consolidado.conftest import conjunto, ler
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def test_cada_emissao_e_numerada_na_unidade_com_o_conjunto(client, seletor_ligado, tres_editais):
    identificar(client, "gustavo.gestor", ["gestor"])
    url = reverse("interface:relatorio-consolidado-pdf")
    dados = {"criterio": "publicacao", "atalho": "s2", "ano": "2026"}
    primeira = client.post(url, dados)
    segunda = client.post(url, dados)
    assert primeira.status_code == segunda.status_code == 200
    assert primeira["Content-Type"] == "application/pdf"
    assert "relatorio-consolidado-cefor-emissao-1.pdf" in primeira["Content-Disposition"]
    assert "emissao-2.pdf" in segunda["Content-Disposition"]
    assert "no-store" in primeira["Cache-Control"]
    unidade = Unidade.objects.get(codigo="cefor")
    eventos = list(
        RegistroAuditoria.objects.filter(
            aggregate_type="Unidade", aggregate_id=unidade.pk, operation=rc.OPERACAO_DA_EMISSAO
        ).order_by("occurred_at")
    )
    assert [e.detalhe["numero"] for e in eventos] == [1, 2]
    assert eventos[0].detalhe["sha256"] == hashlib.sha256(primeira.content).hexdigest()
    assert eventos[1].detalhe["sha256"] == hashlib.sha256(segunda.content).hexdigest()
    detalhe = eventos[0].detalhe
    assert (
        detalhe["criterio"]["inicio"] == "2026-07-01" and detalhe["criterio"]["fim"] == "2026-12-31"
    )
    assert [i["edital"] for i in detalhe["incluidos"]] == ["61/2026", "63/2026"]
    assert eventos[0].permission == "visao:consultar"


def test_conjunto_vazio_nao_e_emitido(client, seletor_ligado, tres_editais):
    identificar(client, "gustavo.gestor", ["gestor"])
    resposta = client.post(
        reverse("interface:relatorio-consolidado-pdf"),
        {"criterio": "publicacao", "atalho": "s1", "ano": "2025"},
    )
    assert resposta.status_code == 422
    assert not RegistroAuditoria.objects.filter(operation=rc.OPERACAO_DA_EMISSAO).exists()


def test_mesmos_fatos_conjunto_e_instante_dao_os_mesmos_bytes(tres_editais):
    lido = ler(conjunto("criterio=numero&ano=2026"))
    primeira = relatorio_consolidado_pdf.compor(lido, emissao=4)
    segunda = relatorio_consolidado_pdf.compor(ler(conjunto("criterio=numero&ano=2026")), emissao=4)
    assert primeira == segunda
