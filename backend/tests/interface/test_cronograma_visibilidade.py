"""O olho no cartão do Evento, e o caminho do campo até o PDF (144, incremento A).

**O que se prende aqui são as travessias** (FR-5104). `replace_draft` apaga e recria o Cronograma a
cada gravação, e campo que falte num dos caminhos volta ao padrão sem aviso — foi assim que a
designação do período de inscrições morria no passo seguinte (E2E17-001). A visibilidade tem cinco
caminhos: a própria etapa, as etapas seguintes, a recusa, a linha nova e a API.

O rascunho de partida é o da fixture `com_etapas`: o Evento de inscrições vinculado à Etapa "Prova
didática". Ele é o que se oculta — o caso em que ocultar mais "parece" desativar.
"""

import pytest
from django.template.loader import render_to_string
from django.urls import reverse

from processo_seletivo.editais.models.cronograma import EventoCronograma
from processo_seletivo.editais.models.etapas import EtapaAvaliacao
from tests.interface.conftest import ETAPA_CLASSIFICATORIA, identificar
from tests.interface.test_compor import EVENTO
from tests.interface.test_fluxo import texto_do_pdf

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

VISIVEL = "aaaaaaaa-0000-4000-8000-000000014410"


def formulario(*, oculto=True, **extra):
    """O Cronograma inteiro: o Evento vinculado à Etapa, e um segundo, exibido."""
    return {
        "evento-0-id": EVENTO,
        "evento-0-type": "INSCRICAO",
        "evento-0-description": "Período de inscrições",
        "evento-0-startAt": "2026-10-01T09:00",
        "evento-0-endAt": "2026-10-20T23:59",
        "evento-0-order": "1",
        "evento-0-shownInPdf": "false" if oculto else "true",
        "evento-1-id": VISIVEL,
        "evento-1-type": "RESULTADO",
        "evento-1-description": "ResultadoFinalDoEdital",
        "evento-1-startAt": "2027-01-10T14:00",
        "evento-1-order": "2",
        "evento-1-shownInPdf": "true",
        **extra,
    }


def gravar(client, edital, dados):
    return client.post(reverse("interface:compor-etapa", args=[edital.id, "cronograma"]), dados)


def visibilidade(edital):
    return dict(
        EventoCronograma.objects.filter(cronograma__edital=edital).values_list("id", "shown_in_pdf")
    )


def esperado(oculto=False):
    from uuid import UUID

    return {UUID(EVENTO): not oculto, UUID(VISIVEL): True}


@pytest.fixture
def oculto(client, com_etapas):
    resposta = gravar(client, com_etapas, formulario())
    assert resposta.status_code == 302, resposta.content
    com_etapas.refresh_from_db()
    return com_etapas


# --- a gravação e as travessias (FR-5102, FR-5104, SC-1584) -------------------------------------


def test_ocultar_e_gravar_persiste(oculto):
    assert visibilidade(oculto) == esperado(oculto=True)


def test_recarregar_a_etapa_mostra_o_oculto(client, oculto):
    corpo = client.get(reverse("interface:compor-etapa", args=[oculto.id, "cronograma"]))
    html = corpo.content.decode()

    assert 'name="evento-0-shownInPdf" value="false"' in html
    assert 'name="evento-1-shownInPdf" value="true"' in html
    assert 'class="linha evento oculto-do-pdf"' in html
    assert html.count('aria-pressed="true"') == 1


@pytest.mark.parametrize(
    ("etapa", "dados"),
    [
        ("identificacao", {"title": "Outro título", "description": "Qualquer."}),
        ("inscricao", {"periodo": EVENTO}),
    ],
)
def test_gravar_outra_etapa_preserva_o_oculto(client, oculto, etapa, dados):
    """O quarto campo de `eventos_persistidos` (E2E17-001): sem ele, o oculto voltava a sair."""
    resposta = client.post(reverse("interface:compor-etapa", args=[oculto.id, etapa]), dados)

    assert resposta.status_code in (200, 302), resposta.content
    assert visibilidade(oculto) == esperado(oculto=True)


def test_recusa_reexibe_o_oculto(client, com_etapas):
    """Caso-limite: a recusa devolve o digitado, e a visibilidade é digitado."""
    antes = visibilidade(com_etapas)
    resposta = gravar(
        client,
        com_etapas,
        formulario(**{"evento-0-endAt": "2026-09-01T09:00"}),  # término antes do início
    )

    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert 'name="evento-0-shownInPdf" value="false"' in html
    assert visibilidade(com_etapas) == antes, "nada gravado na recusa"


def test_campo_ausente_no_formulario_vale_exibido(client, com_etapas):
    """O rascunho local guardado antes do campo existir não oculta nada."""
    dados = formulario()
    del dados["evento-0-shownInPdf"], dados["evento-1-shownInPdf"]

    assert gravar(client, com_etapas, dados).status_code == 302
    assert visibilidade(com_etapas) == esperado(oculto=False)


def test_evento_acrescentado_nasce_exibido(client, seletor_ligado):
    identificar(client, "ana.elaboradora", ["elaborador"])
    html = client.get(reverse("interface:fragmento-evento"), {"indice": "7"}).content.decode()

    assert 'name="evento-7-shownInPdf" value="true"' in html
    assert 'aria-pressed="false"' in html
    assert "data-marca-pdf hidden" in html


# --- o cartão (FR-5101, UX-390, UX-391) ---------------------------------------------------------


def test_o_olho_sai_escondido_e_so_no_cartao_do_evento(client, oculto):
    """Sem o script, o botão não faria nada: sai com `hidden`, e o `cronograma.js` o revela."""
    cronograma = client.get(reverse("interface:compor-etapa", args=[oculto.id, "cronograma"]))
    perfis = client.get(reverse("interface:compor-etapa", args=[oculto.id, "perfis"]))

    html = cronograma.content.decode()
    assert html.count("data-visibilidade-no-pdf hidden") == 2
    assert html.count('aria-label="Ocultar do PDF"') == 2
    assert 'title="Oculto do PDF — exibir"' in html
    assert 'title="Exibido no PDF — ocultar"' in html
    assert "interface/cronograma.js" in html
    assert "data-visibilidade-no-pdf" not in perfis.content.decode()


def test_somente_leitura_mostra_a_marca_sem_o_olho():
    html = render_to_string(
        "interface/_evento.html",
        {"evento": {"id": EVENTO, "type": "INSCRICAO", "shownInPdf": False}, "indice": 0,
         "somente_leitura": True},
    )  # fmt: skip

    assert "data-visibilidade-no-pdf" not in html
    assert '<span class="marca-pdf" data-marca-pdf>Oculto do PDF</span>' in html


# --- o oculto continua Evento (FR-5103, SC-1582, SC-1589) ---------------------------------------


def test_a_etapa_continua_vinculada_ao_oculto(oculto):
    etapa = EtapaAvaliacao.objects.get(id=ETAPA_CLASSIFICATORIA)

    assert str(etapa.evento_id) == EVENTO


def test_a_etapa_etapas_oferece_o_oculto(client, oculto):
    etapas = reverse("interface:compor-etapa", args=[oculto.id, "etapas"])
    html = client.get(etapas).content.decode()

    assert f'<option value="{EVENTO}"' in html


def test_o_oculto_conta_entre_os_vencidos(client, oculto):
    """O Evento de 2026-10 já passou, oculto ou não, e a etapa fica pendente por ele."""
    resposta = client.get(reverse("interface:compor-etapa", args=[oculto.id, "cronograma"]))

    assert [str(evento.id) for evento in resposta.context["cronograma_vencidos"]] == [EVENTO]


def test_o_oculto_continua_conferido_pela_validacao_de_datas(client, oculto):
    resposta = gravar(client, oculto, formulario(**{"evento-0-endAt": "2026-09-01T09:00"}))

    assert resposta.status_code == 200
    assert "O início do Evento não pode ser posterior ao término." in resposta.content.decode()


# --- a Revisão e a prévia do PDF (FR-5110, FR-5106, FR-5108, SC-1588) --------------------------


def test_revisao_diz_que_nao_sai_no_pdf(client, oculto):
    html = client.get(reverse("interface:compor-etapa", args=[oculto.id, "revisao"])).content
    texto = html.decode()

    assert "Não sai na tabela do Cronograma do PDF" in texto
    assert "a seção Cronograma não será impressa" not in texto


def test_revisao_com_todos_ocultos_diz_que_a_secao_nao_sai(client, com_etapas):
    gravar(client, com_etapas, formulario(**{"evento-1-shownInPdf": "false"}))

    texto = client.get(
        reverse("interface:compor-etapa", args=[com_etapas.id, "revisao"])
    ).content.decode()

    assert "a seção Cronograma não será impressa" in texto


def test_a_previa_do_pdf_nao_imprime_o_oculto_e_a_etapa_diz_quando(client, oculto):
    linhas = texto_do_pdf(
        client.get(reverse("interface:previa-documento", args=[oculto.id]))
    ).splitlines()

    assert "Período de inscrições" not in linhas
    posicao = linhas.index("ResultadoFinalDoEdital")
    assert linhas[posicao - 1] == "1"
    corrido = " ".join(" ".join(linhas).split())
    assert "01/10/2026" in corrido, "a Etapa vinculada ao oculto continua com as datas dele"


def test_o_evento_acrescentado_por_retificacao_nasce_exibido():
    """FR-5100, FR-5113: a forma publicada exige a chave, e a tela não a oferece no acréscimo."""
    from processo_seletivo.interface.retificacao import CAMPOS_EVENTO, _evento_completo

    assert _evento_completo({"type": "Prova", "description": "Prova"}, 3)["shownInPdf"] is True
    assert ("shownInPdf", "Sai na tabela do Cronograma do PDF") in [c[:2] for c in CAMPOS_EVENTO]
