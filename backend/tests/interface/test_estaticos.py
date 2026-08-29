"""Os arquivos estáticos precisam ser encontráveis, não apenas existir no disco.

O HTMX ficou em `backend/static/`, que o Django não varre: o finder procura em `static/`
dentro de cada app e em STATICFILES_DIRS. O arquivo existia, o template o referenciava, e o
navegador recebia 404 — então "Acrescentar Perfil" não fazia nada.

Nenhum teste anterior alcançava isso: todos exercitavam o endpoint do fragmento diretamente,
que funciona sem HTMX. O que faltava era afirmar que a página consegue carregar o script.
"""

import re

import pytest
from django.contrib.staticfiles import finders
from django.urls import reverse

from processo_seletivo.processos.models import Edital
from tests.interface.conftest import identificar

TELAS_COM_HTMX = ["perfis", "cronograma"]


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    return Edital.objects.get()


def test_htmx_e_encontravel_pelo_finder():
    assert finders.find("interface/htmx.min.js"), (
        "o arquivo precisa estar em static/ dentro de um app ou em STATICFILES_DIRS"
    )


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.parametrize("etapa", TELAS_COM_HTMX)
def test_telas_dinamicas_carregam_um_script_que_existe(client, seletor_ligado, edital, etapa):
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(
        reverse("interface:compor-etapa", args=[edital.id, etapa])
    ).content.decode()

    scripts = re.findall(r'<script src="([^"]+)"', corpo)
    assert scripts, f"a etapa {etapa} usa HTMX e precisa carregá-lo"
    for src in scripts:
        caminho = src.removeprefix("/static/")
        assert finders.find(caminho), f"{src} não é servido: o navegador receberia 404"


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.parametrize("etapa", TELAS_COM_HTMX)
def test_botao_de_acrescentar_declara_o_que_htmx_precisa(client, seletor_ligado, edital, etapa):
    """Sem alvo e sem modo de inserção, o clique não teria efeito mesmo com a biblioteca."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(
        reverse("interface:compor-etapa", args=[edital.id, etapa])
    ).content.decode()

    assert 'hx-get="/gestao/fragmentos/' in corpo
    assert 'hx-target="#' in corpo
    assert 'hx-swap="beforeend"' in corpo
    alvo = re.search(r'hx-target="#(\w+)"', corpo).group(1)
    assert f'id="{alvo}"' in corpo, "o alvo do HTMX precisa existir na página"


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.parametrize(
    ("etapa", "alvo", "item", "rota_fragmento"),
    [
        ("perfis", "#perfis", ".perfil", "interface:fragmento-perfil"),
        ("cronograma", "#eventos", ".evento", "interface:fragmento-evento"),
    ],
)
def test_contador_declara_o_que_o_script_precisa_para_reagir(
    client, seletor_ligado, edital, etapa, alvo, item, rota_fragmento
):
    """O contador vem do servidor; sem estes atributos ele congela após o primeiro clique."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(
        reverse("interface:compor-etapa", args=[edital.id, etapa])
    ).content.decode()

    assert f'data-contador="{alvo}"' in corpo
    assert f'data-item="{item}"' in corpo
    assert "data-singular=" in corpo and "data-plural=" in corpo

    fragmento = client.get(reverse(rota_fragmento), {"indice": "7"})
    assert item.lstrip(".") in fragmento.content.decode(), (
        "o fragmento precisa carregar a classe que o contador conta"
    )


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.parametrize("etapa", TELAS_COM_HTMX + ["identificacao", "revisao"])
def test_nenhuma_sintaxe_de_template_chega_ao_navegador(client, seletor_ligado, edital, etapa):
    """`{# ... #}` do Django só comenta uma linha; em duas, ele é impresso na tela.

    Foi assim que um comentário sobre FR-020 apareceu para o usuário entre os botões.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(
        reverse("interface:compor-etapa", args=[edital.id, etapa])
    ).content.decode()

    for residuo in ("{#", "#}", "{%", "%}", "{{", "}}"):
        assert residuo not in corpo, f"sintaxe de template não interpretada na página: {residuo}"
