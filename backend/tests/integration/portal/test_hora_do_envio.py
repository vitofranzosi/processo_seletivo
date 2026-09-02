"""A hora do envio é uma só, em toda parte.

O percurso no navegador encontrou a mesma inscrição enviada "às 16h03" no comprovante e "às 19h03"
na tela de conferência, com os documentos datados "às 16:01" três linhas abaixo — na mesma página.
Três horas: o comprovante em HTML passa pelo filtro `date`, que localiza; a conferência e o PDF
liam `comprovante_pdf.instante`, que formatava o valor cru do banco, e o banco devolve UTC.

Não é detalhe de apresentação. Perto do fim do prazo, um envio às 23h50 vira 02h50 do dia seguinte
no documento que a pessoa guarda para provar que enviou a tempo.
"""

import re
from datetime import UTC, datetime, timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.inscricoes.application.rascunho import anexar_documento, gravar_dados
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from processo_seletivo.inscricoes.infrastructure import comprovante_pdf
from processo_seletivo.inscricoes.models import DocumentoSubmetido, Inscricao
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, identificar, pdf
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

# 23h50 em São Paulo é 02h50 do dia seguinte em UTC — a virada de dia é o caso que mais custa.
PERTO_DA_MEIA_NOITE = datetime(2026, 9, 12, 2, 50, tzinfo=UTC)


@pytest.fixture
def enviada(inscricao_de_maria):
    inscricao = gravar_dados(
        identidade=MARIA, inscricao=inscricao_de_maria, dados={"modality_id": MODALIDADE_AC}
    )
    for requisito, nome in ((DOCUMENTO_DE_TODOS, "rg.pdf"), (DOCUMENTO_DO_PERFIL, "diploma.pdf")):
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
        )
    inscricao.refresh_from_db()
    registro = enviar_inscricao(
        identidade=MARIA,
        inscricao=inscricao,
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key="envio-hora",
    )
    Inscricao.objects.filter(pk=registro.pk).update(submitted_at=PERTO_DA_MEIA_NOITE)
    # Os arquivos foram entregues minutos antes do envio, e no mesmo dia: é o par que a tela
    # mostra lado a lado, e era ali que a divergência aparecia sem sair da página.
    DocumentoSubmetido.objects.filter(inscricao=registro).update(
        uploaded_at=PERTO_DA_MEIA_NOITE - timedelta(minutes=5)
    )
    registro.refresh_from_db()
    return registro


def hora(corpo, rotulo):
    trecho = corpo.split(rotulo, 1)[1][:200]
    achado = re.search(r"(\d{2}/\d{2}/\d{4})\D{0,8}?(\d{1,2})[h:](\d{2})", trecho, re.S)
    return achado.group(1), f"{int(achado.group(2))}h{achado.group(3)}"


def test_o_comprovante_e_a_conferencia_dizem_a_mesma_hora(client, enviada):
    identificar(client, MARIA)

    comprovante = client.get(reverse("portal:comprovante", args=[enviada.id])).content.decode()
    conferencia = client.get(reverse("portal:inscricao", args=[enviada.id])).content.decode()

    assert hora(comprovante, "Enviada em") == hora(conferencia, "Enviada em")


def test_a_hora_e_a_do_fuso_da_instituicao_e_nao_a_do_banco(client, enviada):
    """23h50 do dia 11, e não 02h50 do dia 12."""
    identificar(client, MARIA)

    conferencia = client.get(reverse("portal:inscricao", args=[enviada.id])).content.decode()

    assert hora(conferencia, "Enviada em") == ("11/09/2026", "23h50")


def test_a_data_do_documento_acompanha_a_do_envio(client, enviada):
    """Na mesma página, os documentos vinham do filtro do template — já localizados — e o envio
    não. Era a divergência visível numa tela só."""
    identificar(client, MARIA)

    conferencia = client.get(reverse("portal:inscricao", args=[enviada.id])).content.decode()
    dia_do_envio, _ = hora(conferencia, "Enviada em")
    dia_do_documento, _ = hora(conferencia, "rg.pdf")

    assert dia_do_envio == dia_do_documento


def test_instante_converte_o_que_vem_do_banco():
    """O ponto exato do defeito, sem passar por tela nenhuma."""
    momento = datetime(2026, 9, 12, 2, 50, tzinfo=UTC)

    assert comprovante_pdf.instante(momento) == "11/09/2026, às 23h50"
    assert comprovante_pdf.instante(None) == "—"
    # Naive não explode: quem já entregou no fuso certo continua atendido.
    assert comprovante_pdf.instante(timezone.localtime(momento).replace(tzinfo=None)) == (
        "11/09/2026, às 23h50"
    )
