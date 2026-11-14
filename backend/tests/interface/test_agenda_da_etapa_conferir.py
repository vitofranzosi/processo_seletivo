"""A conferência, a publicação e a agenda publicada na gestão (167, T047, UX-766, FR-7222, FR-7255).

A moldura da conferência da convocação com as quatro linhas de prontidão; a prévia pública igual ao
que a página pública mostrará; o assunto e o texto da mensagem; o veículo e a autoridade; o botão;
a publicação pela tela; a agenda publicada; e as portas que negam fora do escopo.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.agendamento.application import leitura
from processo_seletivo.agendamento.models import AtoDaAgenda
from tests.fixtures.agenda_da_etapa import (
    DECLARACAO,
    eliminar_na_primeira,
    montar_completa,
    publicar_agenda,
)
from tests.fixtures.autoridades import AUTORIDADE_DA_SUITE
from tests.fixtures.comissao import inscrever
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def presidente(client, seletor_ligado):
    identificar(client, "carlos", ["gestor"])
    return client


@pytest.fixture
def inscritas(edital_a):
    return inscrever(edital_a, 5)


@pytest.fixture
def completa(gestor, edital_a, etapa_a2, inscritas):
    montar_completa(gestor, edital_a, etapa_a2)
    return leitura.agenda_da_etapa(edital_a, etapa_a2)


def url(nome, edital, etapa):
    return reverse(f"interface:{nome}", args=[edital.id, etapa])


def _campo(corpo, nome):
    return re.search(rf'name="{nome}" value="([^"]*)"', corpo).group(1)


def test_a_conferencia_abre_com_a_prontidao_e_segue_a_moldura(
    presidente, edital_a, etapa_a2, completa
):
    corpo = presidente.get(url("agenda-conferir", edital_a, etapa_a2)).content.decode()

    assert "Confira antes de publicar a agenda" in corpo
    assert "telas/convocacao-conferir.css" in corpo
    inicio = corpo.index('class="lista-de-prontidao"')
    prontidao = corpo[inicio : corpo.index("</ul>", inicio)]
    assert prontidao.count("<li") == 4
    assert "5 de 5 com horário" in prontidao
    assert "Toda banca com endereço de sala" in prontidao
    assert "Autoridade signatária, escolhida no fim da página" in prontidao
    # A ordem das perguntas: prontidão, o que será publicado, o público, a mensagem, quem assina.
    ordem = [
        corpo.index(trecho)
        for trecho in (
            "lista-de-prontidao",
            "Será publicada",
            "Na página pública da seleção",
            "O que cada pessoa recebe",
            "Quem assina",
            "Publicar a agenda e avisar as pessoas",
        )
    ]
    assert ordem == sorted(ordem)
    assert "Antes de publicar, resolva" not in corpo


def test_a_previa_publica_e_igual_a_pagina_publica(
    presidente, client, gestor, edital_a, etapa_a2, inscritas, completa
):
    """FR-7222: a prévia mostra o que a página pública mostrará, sem a sala."""
    corpo = presidente.get(url("agenda-conferir", edital_a, etapa_a2)).content.decode()
    previa = corpo[corpo.index('class="previa-publica"') : corpo.index("O que cada pessoa recebe")]

    ato = publicar_agenda(gestor, edital_a, etapa_a2)
    publica = client.get(reverse("portal:agenda-da-etapa", args=[ato.agenda_id])).content.decode()

    for inscricao in inscritas:
        assert inscricao.nome in previa and inscricao.protocolo in previa
        assert inscricao.nome in publica and inscricao.protocolo in publica
    for hora in re.findall(r'class="hora">(\d\d:\d\d)<', previa):
        assert f'class="hora">{hora}<' in publica
    assert "sala.exemplo" not in previa


def test_a_mensagem_o_veiculo_e_a_autoridade(presidente, edital_a, etapa_a2, completa):
    corpo = presidente.get(url("agenda-conferir", edital_a, etapa_a2)).content.decode()

    assert "<strong>Assunto:</strong> Seu horário: Prova didática — Edital" in corpo
    assert "Ler a mensagem inteira, como sai" in corpo
    assert "Sala virtual: https://sala.exemplo/1" in corpo
    assert 'name="veiculo" value="GPS"' in corpo and 'name="veiculo" value="EXTERNO"' in corpo
    assert f'<option value="{AUTORIDADE_DA_SUITE}"' in corpo
    assert re.search(r'<button type="submit" class="botao perigoso">Publicar a agenda', corpo)


def test_com_impedimento_o_botao_fica_desligado_e_o_caminho_aparece(
    presidente, gestor, edital_a, etapa_a1, etapa_a2, inscritas, completa
):
    eliminar_na_primeira(gestor, edital_a, etapa_a1, inscritas[:1])

    corpo = presidente.get(url("agenda-conferir", edital_a, etapa_a2)).content.decode()

    assert "Antes de publicar, resolva" in corpo
    assert "tem horário, mas não participa mais da Etapa" in corpo
    assert f'href="{url("agenda-montar", edital_a, etapa_a2)}">Voltar à montagem' in corpo
    assert 'class="botao perigoso" disabled' in corpo


def test_publicar_pela_tela_leva_a_agenda_publicada(
    presidente, edital_a, etapa_a2, inscritas, completa
):
    conferencia = presidente.get(url("agenda-conferir", edital_a, etapa_a2)).content.decode()
    dados = {
        "assinatura": _campo(conferencia, "assinatura"),
        "chave_idempotencia": _campo(conferencia, "chave_idempotencia"),
        "veiculo": "GPS",
        "declaracao": DECLARACAO,
        "autoridade": str(AUTORIDADE_DA_SUITE),
    }

    resposta = presidente.post(url("agenda-publicar", edital_a, etapa_a2), dados)
    assert resposta.status_code == 302
    assert resposta.url == url("agenda-publicada", edital_a, etapa_a2)
    # O duplo clique: a mesma tela, a mesma chave, o mesmo ato.
    de_novo = presidente.post(url("agenda-publicar", edital_a, etapa_a2), dados)
    assert de_novo.status_code == 302
    assert AtoDaAgenda.objects.count() == 1

    corpo = presidente.get(resposta.url).content.decode()
    assert "Agenda publicada. A página pública e a área de cada pessoa" in corpo
    assert "5 horários publicados" in corpo
    assert "Na página pública do GPS (item 7.2 do Edital)" in corpo
    for inscricao in inscritas:
        assert inscricao.protocolo in corpo
    assert reverse("portal:agenda-da-etapa", args=[completa.id]) in corpo


def test_a_recusa_volta_a_conferencia_com_o_que_foi_escrito(
    presidente, edital_a, etapa_a2, completa
):
    conferencia = presidente.get(url("agenda-conferir", edital_a, etapa_a2)).content.decode()

    resposta = presidente.post(
        url("agenda-publicar", edital_a, etapa_a2),
        {
            "assinatura": _campo(conferencia, "assinatura"),
            "chave_idempotencia": _campo(conferencia, "chave_idempotencia"),
            "veiculo": "EXTERNO",
            "onde": "Site do campus",
            "autoridade": str(AUTORIDADE_DA_SUITE),
        },
    )

    assert resposta.status_code == 422
    corpo = resposta.content.decode()
    assert "Diga onde e quando a agenda foi publicada fora do GPS." in corpo
    assert 'value="Site do campus"' in corpo
    assert 'value="EXTERNO" checked' in corpo
    assert not AtoDaAgenda.objects.exists()


def test_a_assinatura_velha_refaz_a_conferencia(presidente, edital_a, etapa_a2, completa):
    resposta = presidente.post(
        url("agenda-publicar", edital_a, etapa_a2),
        {
            "assinatura": "velha",
            "chave_idempotencia": "ui-velha",
            "veiculo": "GPS",
            "declaracao": DECLARACAO,
            "autoridade": str(AUTORIDADE_DA_SUITE),
        },
    )

    assert resposta.status_code == 409
    corpo = resposta.content.decode()
    assert "A agenda mudou desde esta conferência. Confira de novo." in corpo
    assert _campo(corpo, "chave_idempotencia") != "ui-velha"
    assert not AtoDaAgenda.objects.exists()


def test_publicada_a_montagem_e_a_conferencia_levam_a_agenda_publicada(
    presidente, gestor, edital_a, etapa_a2, completa
):
    publicar_agenda(gestor, edital_a, etapa_a2)
    publicada = url("agenda-publicada", edital_a, etapa_a2)

    for nome in ("agenda-montar", "agenda-conferir"):
        resposta = presidente.get(url(nome, edital_a, etapa_a2))
        assert resposta.status_code == 302 and resposta.url == publicada
    distribuicao = presidente.get(
        reverse("interface:distribuicao", args=[edital_a.id, etapa_a2])
    ).content.decode()
    assert "Agenda publicada" in distribuicao and publicada in distribuicao


def test_a_agenda_publicada_nomeia_quem_saiu_depois(
    presidente, gestor, edital_a, etapa_a1, etapa_a2, inscritas, completa
):
    publicar_agenda(gestor, edital_a, etapa_a2)
    eliminar_na_primeira(gestor, edital_a, etapa_a1, inscritas[:1])

    corpo = presidente.get(url("agenda-publicada", edital_a, etapa_a2)).content.decode()

    # A Ocorrência dá Resultado à primeira Etapa: a eliminada sai, e as outras passam a aguardar o
    # Resultado delas — a partição da participação, cada uma com o seu motivo (FR-7217).
    assert "Tem horário e não participa mais (5)" in corpo
    assert "Seg., 23/11, 08:00: foi eliminada numa Etapa anterior." in corpo
    assert "aguarda o Resultado da Etapa anterior" in corpo


def test_sem_agenda_publicada_a_pagina_leva_a_conferencia(presidente, edital_a, etapa_a2, completa):
    resposta = presidente.get(url("agenda-publicada", edital_a, etapa_a2))

    assert resposta.status_code == 302
    assert resposta.url == url("agenda-conferir", edital_a, etapa_a2)


@pytest.mark.parametrize("nome", ["agenda-conferir", "agenda-publicada"])
def test_fora_do_escopo_e_inexistente(client, seletor_ligado, edital_a, etapa_a2, nome):
    identificar(client, "carlos", ["gestor"], escopo="outra")

    assert client.get(url(nome, edital_a, etapa_a2)).status_code == 404


def test_publicar_fora_do_escopo_e_inexistente(
    client, seletor_ligado, edital_a, etapa_a2, completa
):
    identificar(client, "carlos", ["gestor"], escopo="outra")

    resposta = client.post(url("agenda-publicar", edital_a, etapa_a2), {"veiculo": "GPS"})

    assert resposta.status_code == 404
    assert not AtoDaAgenda.objects.exists()


def test_sem_a_base_da_comissao_conferir_e_negado(client, seletor_ligado, edital_a, etapa_a2):
    identificar(client, "elaine", ["elaborador"])

    assert client.get(url("agenda-conferir", edital_a, etapa_a2)).status_code == 403


def test_o_horario_publicado_fora_do_periodo_vigente_e_avisado(
    presidente, gestor, edital_a, etapa_a2, completa, monkeypatch
):
    """Edge Cases, T056: o Evento retificado depois da publicação não desfaz o horário publicado."""
    from datetime import date

    publicar_agenda(gestor, edital_a, etapa_a2)
    depois = (date(2026, 11, 25), date(2026, 11, 27))
    monkeypatch.setattr(leitura, "periodo_da_etapa", lambda edital, etapa: depois)

    corpo = presidente.get(url("agenda-publicada", edital_a, etapa_a2)).content.decode()

    assert (
        "O Evento da Etapa foi retificado depois da publicação, e 5 horários publicados estão "
        "fora do período vigente. Eles continuam valendo como foram publicados."
    ) in corpo
