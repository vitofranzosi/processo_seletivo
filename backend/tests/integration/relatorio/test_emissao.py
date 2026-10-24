"""A emissão: numerada, registrada com o resumo dos bytes, determinística e num instante só (099).

FR-2516, FR-2517, FR-2519, FR-2520, SC-937.
"""

import hashlib

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.interface import relatorio_do_edital as rel
from processo_seletivo.interface import relatorio_pdf
from tests.fixtures.relatorio import montar_cenario
from tests.integration.relatorio.conftest import ler
from tests.interface.conftest import identificar

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_cada_emissao_e_numerada_e_registrada_com_o_resumo_do_que_saiu(
    client, seletor_ligado, pendente
):
    identificar(client, "gustavo.gestor", ["gestor"])
    url = reverse("interface:relatorio-do-edital-pdf", args=[pendente.edital.id])

    primeira = client.post(url)
    segunda = client.post(url)

    assert primeira.status_code == segunda.status_code == 200
    assert primeira["Content-Type"] == "application/pdf"
    assert "emissao-1.pdf" in primeira["Content-Disposition"]
    assert "emissao-2.pdf" in segunda["Content-Disposition"]
    assert "no-store" in primeira["Cache-Control"]
    eventos = list(
        RegistroAuditoria.objects.filter(
            aggregate_id=pendente.edital.id, operation=rel.OPERACAO_DA_EMISSAO
        ).order_by("occurred_at")
    )
    assert [e.detalhe["numero"] for e in eventos] == [1, 2]
    assert eventos[0].detalhe["sha256"] == hashlib.sha256(primeira.content).hexdigest()
    assert eventos[1].detalhe["sha256"] == hashlib.sha256(segunda.content).hexdigest()
    assert eventos[0].actor_subject == "gustavo.gestor"
    assert eventos[0].permission == "comissao:gerir"


@pytest.mark.django_db
def test_mesmos_fatos_e_mesmo_instante_dao_os_mesmos_bytes(pendente):
    relatorio = ler(pendente)
    assert relatorio_pdf.compor(relatorio, emissao=1) == relatorio_pdf.compor(
        ler(pendente), emissao=1
    )
    assert relatorio_pdf.compor(relatorio, emissao=1) != relatorio_pdf.compor(relatorio, emissao=2)


@pytest.mark.django_db
def test_texto_sem_grafia_recusa_a_emissao(pendente):
    """Caso-limite: como o Edital, o documento não troca caractere por "?" (achado de 08/10)."""
    from processo_seletivo.publicacoes.infrastructure.pdf import CaractereSemGrafia

    relatorio = ler(pendente)
    relatorio.frases = [*relatorio.frases, "Um sinal sem grafia: ☃."]
    with pytest.raises(CaractereSemGrafia):
        relatorio_pdf.compor(relatorio, emissao=1)


@pytest.mark.django_db(transaction=True)
def test_a_leitura_inteira_ve_um_instante_so():
    """FR-2519, R-002: a transação de fora começa em `REPEATABLE READ`.

    O caso é transacional porque, dentro de um `TestCase`, a transação já está aberta e o nível não
    pode mais ser trocado — é exatamente o caso em que `leitura_consistente` não o emite.
    """
    cenario = montar_cenario(final="sem-pendencia")
    with CaptureQueriesContext(connection) as consultas:
        ler(cenario)
    comandos = [consulta["sql"] for consulta in consultas.captured_queries]
    # O `BEGIN` é a abertura da transação; o nível tem de vir antes de qualquer leitura.
    assert comandos[:2] == ["BEGIN", "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"]
