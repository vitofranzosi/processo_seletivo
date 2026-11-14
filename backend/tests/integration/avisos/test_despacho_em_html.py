"""O despacho com a forma HTML: a mesma mensagem, o mesmo destinatário, e o texto que foi congelado.

**O texto puro continua sendo o aviso.** O HTML só o mostra na moldura comum; se ele não se compõe,
a mensagem sai com o texto sozinho, como saía antes — e o resultado registrado é o do envio, e não o
da moldura.
"""

import pytest
from django.core import mail

from processo_seletivo.avisos.application.despacho import despachar
from processo_seletivo.avisos.domain import nomes
from processo_seletivo.avisos.models import Aviso
from processo_seletivo.shared import correio
from tests.fixtures.avisos import avisar_resultado
from tests.fixtures.divulgacao import montar_ato_publicavel, publicar_o_ato

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def avisado(gestor, api_client, manager_headers, process_payload):
    cenario = montar_ato_publicavel(
        gestor, api_client, manager_headers, process_payload, pontuacoes=("90.0000", "70.0000")
    )
    publicacao = publicar_o_ato(cenario)
    mail.outbox.clear()
    cenario["aviso"] = avisar_resultado(cenario["edital"], publicacao.marco_id)
    return cenario


def _html(mensagem):
    return [conteudo for conteudo, tipo in mensagem.alternatives if tipo == "text/html"]


def test_cada_pessoa_recebe_o_texto_congelado_e_a_forma_html_dele(avisado):
    resumo = despachar()

    assert resumo.resultados == {nomes.ACEITA: 2}
    corpo_congelado = Aviso.objects.get().corpo
    for mensagem in mail.outbox:
        (html,) = _html(mensagem)
        assert len(mensagem.to) == 1 and mensagem.cc == [] and mensagem.bcc == []
        assert mensagem.extra_headers.get("Auto-Submitted") == "auto-generated"
        # O texto puro é o congelado, com o nome resolvido — exatamente o de antes.
        assert "{nome_do_candidato}" not in mensagem.body
        primeira_linha_fixa = corpo_congelado.split("\n\n")[1][:40]
        assert primeira_linha_fixa in mensagem.body
        assert mensagem.subject in html
        assert "Este aviso não substitui a publicação." in html


def test_sem_a_forma_html_o_aviso_sai_so_com_o_texto(avisado, monkeypatch):
    registrados = []
    monkeypatch.setattr(
        "processo_seletivo.avisos.application.despacho.logger.exception",
        lambda mensagem, *a, **k: registrados.append(mensagem),
    )

    def quebrar(**_):
        raise ValueError("classe sem estilo na mensagem: 'x'")

    monkeypatch.setattr(correio, "html_do_aviso", quebrar)

    resumo = despachar()

    assert resumo.resultados == {nomes.ACEITA: 2}, "a moldura não custa o aviso"
    assert len(mail.outbox) == 2
    assert all(_html(mensagem) == [] for mensagem in mail.outbox)
    assert registrados == ["O aviso saiu sem a forma HTML, que não se compôs."] * 2
