"""O campo nasce vazio, a sugestão não grava, e nenhum valor institucional aparece (FR-056..FR-059).

**Vazio significa "não declarado"**, e é o que todo Edital publicado antes deste degrau afirma. A
tentação que este teste bloqueia tem nome: preencher o campo com o local do evento anterior "porque
é quase sempre o mesmo". Sugerir é da tela; presumir é do conteúdo publicado, e um default
aplicaria ao Edital um dado que ninguém escreveu — a mesma degradação que os rótulos da Etapa já
recusaram.
"""

import pytest
from django.urls import reverse

from processo_seletivo.editais.models.cronograma import EventoCronograma
from processo_seletivo.shared.tempo import ZONA
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

LOCAL = "Auditório do Cefor e canal institucional no YouTube"


def _formulario(edital, *, local=None):
    """O Cronograma **inteiro**, com o local no primeiro Evento.

    Reenviar só o evento novo faria a validação recusar — o Edital perderia o Evento marcado como
    período de inscrições —, e o teste estaria medindo outra coisa. `replace_draft` substitui o
    rascunho inteiro, e o formulário do assistente sempre reenvia todos os eventos.
    """
    campos = {}
    for indice, evento in enumerate(edital.cronograma.eventos.order_by("order")):
        campos.update(
            {
                f"evento-{indice}-id": str(evento.id),
                f"evento-{indice}-type": evento.type,
                f"evento-{indice}-description": evento.description,
                f"evento-{indice}-startAt": evento.start_at.astimezone(ZONA).strftime(
                    "%Y-%m-%dT%H:%M"
                ),
                f"evento-{indice}-endAt": (
                    evento.end_at.astimezone(ZONA).strftime("%Y-%m-%dT%H:%M")
                    if evento.end_at
                    else ""
                ),
                f"evento-{indice}-order": str(evento.order),
            }
        )
        if local is not None and indice == 0:
            campos[f"evento-{indice}-location"] = local
    return campos


def _compor(client, edital, *, local=None):
    return client.post(
        reverse("interface:compor-etapa", args=[edital.id, "cronograma"]),
        _formulario(edital, local=local),
    )


def test_a_tela_oferece_o_campo_e_ele_nasce_vazio(client, com_etapas):
    identificar(client, "ana.elaboradora", ["elaborador"])

    corpo = client.get(
        reverse("interface:compor-etapa", args=[com_etapas.id, "cronograma"])
    ).content.decode()

    assert 'name="evento-0-location"' in corpo
    assert "Onde acontece" in corpo
    assert 'name="evento-0-location" value=""' in corpo


def test_o_local_declarado_chega_ao_rascunho(client, com_etapas):
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = _compor(client, com_etapas, local=LOCAL)

    assert resposta.status_code == 302, resposta.content
    assert EventoCronograma.objects.filter(location=LOCAL).exists()


def test_o_campo_nao_e_validado_como_endereco_eletronico(client, com_etapas):
    """FR-061: *"Página da chamada pública"* não é URL, e recusá-lo obrigaria a mentir."""
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = _compor(client, com_etapas, local="Página da chamada pública")

    assert resposta.status_code == 302, resposta.content
    assert EventoCronograma.objects.filter(location="Página da chamada pública").exists()


def test_nenhum_valor_institucional_aparece_por_padrao(client, com_etapas):
    """O campo omitido do formulário não vira um local: fica vazio, e vazio afirma a ausência."""
    identificar(client, "ana.elaboradora", ["elaborador"])

    _compor(client, com_etapas)

    for evento in EventoCronograma.objects.all():
        assert evento.location == ""


def test_gravar_outro_passo_nao_apaga_o_local_declarado(client, com_etapas):
    """O segundo caminho de perda, o mesmo da janela recursal e do método (E2E17-001)."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    _compor(client, com_etapas, local=LOCAL)

    client.post(
        reverse("interface:compor-etapa", args=[com_etapas.id, "identificacao"]),
        {"title": "Título alterado depois do local", "description": "Qualquer."},
    )

    assert EventoCronograma.objects.filter(location=LOCAL).exists()


def test_a_sugestao_nao_preenche_o_campo(client, com_etapas):
    """FR-059: ela chega como `placeholder`, e o `value` de um evento novo continua vazio."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    _compor(client, com_etapas, local=LOCAL)

    corpo = client.get(
        reverse("interface:compor-etapa", args=[com_etapas.id, "cronograma"])
    ).content.decode()
    fragmento = client.get(reverse("interface:fragmento-evento") + "?indice=9").content.decode()

    assert 'placeholder="Sugestão: ' in corpo
    assert 'name="evento-9-location" value=""' in fragmento
