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


def test_a_expiracao_do_rascunho_e_verificada_executando_o_script():
    """FR-022: o prazo e o descarte estão em tests/javascript/rascunho.test.js.

    Procurar a constante no fonte provava que ela foi escrita, não que o rascunho velho é
    descartado. O ponteiro fica aqui para que quem procurar a cobertura do requisito a encontre.
    """
    from pathlib import Path

    suite = Path(__file__).resolve().parents[1] / "javascript/rascunho.test.js"

    assert suite.exists()
    assert "mais velho que um dia é descartado" in suite.read_text(encoding="utf-8")
