"""FR-020: o preenchimento sobrevive à expiração de sessão e à queda de conexão.

A preservação que já existia atua quando o domínio recusa, o que pressupõe a requisição ter
chegado. Nos dois casos que o requisito nomeia ela não chega, e sem armazenamento no navegador
o conteúdo se perde.

O comportamento em si é JavaScript e exige navegador — está verificado manualmente e descrito
em quickstart.md. O que dá para prender aqui é o contrato entre o template e o script: sem
estes atributos ele não tem como saber o que guardar, sob que chave, nem como reconstruir as
linhas.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.processos.models import Edital
from tests.interface.conftest import identificar

ETAPAS = [
    ("perfis", "#perfis", "fragmentos/perfil"),
    ("cronograma", "#eventos", "fragmentos/evento"),
]


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    return Edital.objects.get()


def corpo_da_etapa(client, edital, etapa):
    return client.get(reverse("interface:compor-etapa", args=[edital.id, etapa])).content.decode()


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.parametrize(("etapa", "lista", "fragmento"), ETAPAS)
def test_formulario_declara_o_que_o_rascunho_local_precisa(
    client, seletor_ligado, edital, etapa, lista, fragmento
):
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = corpo_da_etapa(client, edital, etapa)

    assert f'data-rascunho="{edital.id}:{etapa}:ana.elaboradora"' in corpo
    assert f'data-lista="{lista}"' in corpo
    assert f'data-fragmento="/gestao/{fragmento}"' in corpo
    assert "interface/rascunho.js" in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_a_chave_do_rascunho_separa_pessoas_no_mesmo_navegador(client, seletor_ligado, edital):
    """Sem a pessoa na chave, quem usar o mesmo computador depois veria o rascunho alheio."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    da_ana = corpo_da_etapa(client, edital, "perfis")
    identificar(client, "bruno.homologador", ["elaborador"])
    do_bruno = corpo_da_etapa(client, edital, "perfis")

    chave = re.compile(r'data-rascunho="([^"]+)"')
    assert chave.search(da_ana).group(1) != chave.search(do_bruno).group(1)


@pytest.mark.django_db
@pytest.mark.integration
def test_marcador_de_nao_enviado_nasce_oculto(client, seletor_ligado, edital):
    """O HTML recém-renderizado é, por definição, o que o servidor tem."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = corpo_da_etapa(client, edital, "perfis")

    marcador = re.search(r"<span[^>]*data-nao-enviado[^>]*>", corpo)
    assert marcador, "a tela precisa distinguir o enviado do que só existe no navegador"
    assert "hidden" in marcador.group(0)


@pytest.mark.django_db
@pytest.mark.integration
def test_tela_somente_leitura_nao_guarda_rascunho(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """Sem permissão de elaborar não há o que enviar, e guardar seria acumular sem propósito."""
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    edital = Edital.objects.get()
    identificar(client, "iris.auditora", ["auditor"])

    assert "data-rascunho=" not in corpo_da_etapa(client, edital, "perfis")


def _fonte_do_rascunho():
    from pathlib import Path

    return (
        Path(__file__).resolve().parents[2]
        / "processo_seletivo/interface/static/interface/rascunho.js"
    ).read_text(encoding="utf-8")


def test_o_rascunho_guardado_tem_prazo():
    """FR-022 da 003: `localStorage` não caduca sozinho.

    O conteúdo de um Edital em elaboração fica no computador de quem preencheu, que num órgão
    público costuma ser compartilhado. Sem prazo, o preenchimento de meses atrás continuaria lá,
    oferecido a quem sentar na máquina depois.
    """
    fonte = _fonte_do_rascunho()

    assert "VALIDADE_MS = 24 * 60 * 60 * 1000" in fonte
    assert "function vencido(" in fonte
    # A verificação precisa acontecer antes de oferecer a restauração, não depois.
    assert "if (vencido(guardado) || mesmo(guardado.dados, renderizado))" in fonte
    assert "armazem.removeItem(CHAVE)" in fonte


def test_rascunho_sem_carimbo_de_tempo_e_tratado_como_vencido():
    """O que não se sabe a idade é descartado — é o lado seguro num computador compartilhado."""
    fonte = _fonte_do_rascunho()

    assert "if (isNaN(gravado)) return true;" in fonte
