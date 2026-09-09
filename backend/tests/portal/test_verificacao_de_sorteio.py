"""A verificação pública: o íntegro passa, o adulterado é detectado e **nomeado** (FR-048..FR-051).

Detectar não basta: a FR-050 exige que a divergência seja nomeada, porque quem lê precisa saber o
que não confere — e não só que alguma coisa não confere.
"""

import json

import pytest
from django.urls import reverse

from processo_seletivo.sorteios.application.verificacao import CONFERIDO, DIVERGENTE, verificar
from processo_seletivo.sorteios.models import RelacaoDeHabilitados, Sorteio
from tests.unit.sorteios.test_manifesto import sorteado  # noqa: F401 — fixture compartilhada

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_o_sorteio_integro_passa_na_propria_verificacao(sorteado):  # noqa: F811
    _certame, sorteio = sorteado

    veredito = verificar(sorteio)

    assert veredito["integro"] is True
    assert {item["situacao"] for item in veredito["conferencias"]} == {CONFERIDO}
    assert str(sorteio.relacao.quantidade) in veredito["resumo"]


def test_a_pagina_abre_sem_autenticacao_e_relata_em_linguagem_de_gente(client, sorteado):  # noqa: F811
    _certame, sorteio = sorteado

    resposta = client.get(reverse("portal:verificar-sorteio", args=[sorteio.id]))
    corpo = resposta.content.decode()

    assert resposta.status_code == 200
    assert "Sorteio verificado" in corpo
    assert "ordem reproduzida integralmente" in corpo
    assert "O que foi conferido" in corpo
    assert sorteio.semente_normalizada in corpo


def test_o_resumo_da_relacao_adulterado_e_detectado_e_nomeado(sorteado):  # noqa: F811
    """A relação é o primeiro degrau: se ela não confere, o resto não importa."""
    _certame, sorteio = sorteado
    # A gravação é append-only nas três camadas; adulterar exige o caminho que a trigger recusa —
    # e é justamente por isso que a adulteração aqui é simulada em memória, sobre o objeto lido.
    sorteio.relacao.resumo = "f" * 64

    veredito = verificar(sorteio)

    assert veredito["integro"] is False
    divergentes = [i for i in veredito["conferencias"] if i["situacao"] == DIVERGENTE]
    assert any("relação" in i["nome"].lower() for i in divergentes)
    assert any("não corresponde" in i["descricao"] for i in divergentes)


def test_a_semente_adulterada_e_detectada_e_nomeada(sorteado):  # noqa: F811
    _certame, sorteio = sorteado
    sorteio.semente_normalizada = "99999"

    veredito = verificar(sorteio)

    assert veredito["integro"] is False
    nomes = [i["nome"] for i in veredito["conferencias"] if i["situacao"] == DIVERGENTE]
    assert "A semente" in nomes


def test_o_manifesto_baixado_e_o_que_o_verificador_de_terceiro_precisa(client, sorteado):  # noqa: F811
    _certame, sorteio = sorteado

    resposta = client.get(reverse("portal:manifesto-do-sorteio", args=[sorteio.id]))
    manifesto = json.loads(resposta.content.decode())

    assert resposta.status_code == 200
    assert resposta["Content-Type"] == "application/json"
    assert resposta["ETag"] == f'"{sorteio.manifesto_hash}"'
    assert manifesto["manifestHash"] == sorteio.manifesto_hash
    assert manifesto["seed"]["normalized"] == sorteio.semente_normalizada
    assert len(manifesto["participants"]) == sorteio.relacao.quantidade


def test_dois_downloads_produzem_os_mesmos_bytes(client, sorteado):  # noqa: F811
    _certame, sorteio = sorteado
    endereco = reverse("portal:manifesto-do-sorteio", args=[sorteio.id])

    assert client.get(endereco).content == client.get(endereco).content


def test_a_verificacao_nao_depende_de_video_nem_de_canal_externo(sorteado):  # noqa: F811
    """FR-051: tudo o que a verificação usa está publicado ou gravado."""
    _certame, sorteio = sorteado

    veredito = verificar(sorteio)

    assert veredito["integro"] is True
    assert Sorteio.objects.filter(pk=sorteio.pk).exists()
    assert RelacaoDeHabilitados.objects.filter(pk=sorteio.relacao_id).exists()
