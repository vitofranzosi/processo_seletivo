"""A Revisão de um Edital publicado e retificado lê a norma vigente (ED-07 da auditoria de 15/10).

A Retificação não reescreve as tabelas do Edital, que ficam no dia da publicação — o único escritor
delas é o rascunho. A Revisão lia dali, e quem a abria depois de uma Retificação conferia a norma
revogada, sem aviso: no 91/2026 do corpus, "40 vagas imediatas" no polo Bom Jesus do Norte, onde a
Retificação publicou 45, e o fim das inscrições de antes da prorrogação.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.processos.models import Edital
from tests.fixtures.corpus import publicar_do_corpus
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

#: O Perfil que a Retificação do 91/2026 alterou: 40 vagas na publicação, 45 depois dela.
BOM_JESUS = "INF-BJN — Especialização em Informática na Educação"


def _revisao(client, edital):
    identificar(client, "gestora", ["gestor"])
    resposta = client.get(reverse("interface:compor-etapa", args=[edital.id, "revisao"]))
    assert resposta.status_code == 200
    return re.sub(r"\s+", " ", resposta.content.decode())


def _perfil(texto, titulo):
    """O trecho da conferência de um Perfil: do título dele até o título do Perfil seguinte."""
    return texto.split(titulo, 1)[1].split("— Especialização", 1)[0]


def test_retificado_a_revisao_mostra_o_que_vigora(client, seletor_ligado, api_client):
    edital, _ = publicar_do_corpus(api_client, "91", chave="revisao91")

    texto = _revisao(client, edital)

    assert "45 vagas imediatas" in _perfil(texto, BOM_JESUS)
    assert "40 vagas imediatas" not in _perfil(texto, BOM_JESUS), "a norma revogada"
    assert "O conteúdo vigente" in texto, "e a tela diz de que conteúdo fala"
    assert "O que será congelado na submissão" not in texto


def test_publicado_sem_retificacao_tambem_e_o_vigente(client, seletor_ligado, api_client):
    """O critério é haver versão vigente, e não haver Retificação: os dois conteúdos coincidem."""
    edital, _ = publicar_do_corpus(api_client, "91", ate=1, chave="revisao91-pub")

    texto = _revisao(client, edital)

    assert "40 vagas imediatas" in _perfil(texto, BOM_JESUS)
    assert "O conteúdo vigente" in texto


def test_em_elaboracao_a_revisao_continua_sendo_a_da_submissao(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """A contraprova: sem publicação não há versão vigente, e o rascunho é o que se confere."""
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])

    texto = _revisao(client, edital)

    assert "O que será congelado na submissão" in texto
    assert "O conteúdo vigente" not in texto
