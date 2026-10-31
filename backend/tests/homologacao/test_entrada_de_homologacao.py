"""O provedor de homologação: quem entra, por onde, e onde ele não existe (110, FR-3342, FR-3343).

O caminho do roteiro G, de ponta a ponta: a implantação cadastra a pessoa com o provedor
`homologacao`, a página do provedor a oferece, a escolha volta pela entrada institucional de
verdade. E as recusas que já valiam para o provedor simulado valem para ele — as do *boot* estão em
`tests/test_configuracao_producao.py`, ao lado das do simulado; a de execução está aqui.
"""

import re
from html import unescape

import pytest
from django.core.management import call_command
from django.urls import reverse

from processo_seletivo.interface.identidade import CHAVE_ESTADO_INSTITUCIONAL
from processo_seletivo.seguranca.acessos import ESCOPO_INSTITUCIONAL
from processo_seletivo.seguranca.autenticacao import provedor_configurado
from processo_seletivo.seguranca.models import IdentidadeExterna
from tests.fixtures import provedor_simulado
from tests.homologacao import provedor as homologacao
from tests.seguranca.apoio import ator_do_cliente, pessoa

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def configurado(settings):
    """O provedor de homologação como o ambiente de validação o configura: seletor desligado."""
    provedor_simulado.limpar()
    settings.GESTAO_PROVEDOR_INSTITUCIONAL = homologacao.CAMINHO
    settings.INTERFACE_SELETOR_IDENTIDADE = False
    yield
    provedor_simulado.limpar()


@pytest.fixture
def validadora(db):
    """A pessoa do roteiro G, cadastrada pelo comando de implantação, como o operador fará."""
    call_command(
        "conceder_administracao_institucional",
        "--provedor",
        homologacao.NOME,
        "--identificador",
        "validadora",
        "--nome",
        "Validadora Sintética",
        "--motivo",
        "Validação funcional da 110",
    )
    return IdentidadeExterna.objects.get(provedor=homologacao.NOME, identificador="validadora")


def _pagina(client):
    resposta = client.get(reverse("interface:entrar-institucional"))
    assert resposta.status_code == 200, resposta.content
    return resposta.content.decode()


def _links(pagina):
    """Os endereços de volta da página, por nome da pessoa."""
    return {
        unescape(nome): unescape(href)
        for href, nome in re.findall(r'<li><a href="([^"]+)">([^<]+)</a>', pagina)
    }


def test_o_provedor_e_o_simulado_e_se_declara_de_teste():
    """Nenhuma proteção nova: a herança traz a declaração e o bilhete de uso único."""
    assert issubclass(homologacao.ProvedorDeHomologacao, provedor_simulado.ProvedorSimulado)
    assert homologacao.ProvedorDeHomologacao.apenas_para_testes is True
    assert homologacao.CAMINHO.startswith("tests.")


def test_a_pagina_lista_so_as_pessoas_do_provedor(client, configurado, validadora):
    pessoa("de-outro-provedor", nome="Pessoa do Simulado")

    pagina = _pagina(client)

    assert list(_links(pagina)) == ["Validadora Sintética"]
    assert "Administrador institucional de acessos (institucional)" in pagina
    assert "Pessoa do Simulado" not in pagina
    assert "não existe em produção" in pagina
    assert "<script" not in pagina and "style=" not in pagina, "a CSP recusaria"


def test_sem_pessoa_cadastrada_a_pagina_diz_como_cadastrar(client, configurado, db):
    pagina = _pagina(client)

    assert _links(pagina) == {}
    assert "Nenhuma pessoa cadastrada" in pagina
    assert "--provedor homologacao" in pagina


def test_escolher_entra_no_escopo_dos_vinculos(client, configurado, validadora):
    volta = _links(_pagina(client))["Validadora Sintética"]

    resposta = client.get(volta)

    assert resposta.status_code == 302, resposta.content
    ator = ator_do_cliente(client)
    assert ator.institution_scope == ESCOPO_INSTITUCIONAL
    assert ator.can("acesso:administrar")
    assert ator.subject == validadora.pessoa.username


def test_o_bilhete_escolhido_nao_serve_duas_vezes(client, configurado, validadora):
    """O bilhete sai do provedor no retorno, como no simulado: numa ida nova, ele não vale."""
    volta = _links(_pagina(client))["Validadora Sintética"]
    assert client.get(volta).status_code == 302
    client.post(reverse("interface:sair"))

    _pagina(client)
    estado = client.session[CHAVE_ESTADO_INSTITUCIONAL]["estado"]
    bilhete = re.search(r"bilhete=([^&]+)", volta).group(1)
    resposta = client.get(
        reverse("interface:retorno-institucional"), {"state": estado, "bilhete": bilhete}
    )

    assert resposta.status_code == 403
    assert ator_do_cliente(client) is None


def test_retorno_sem_o_estado_da_ida_e_recusado(client, configurado, validadora):
    volta = _links(_pagina(client))["Validadora Sintética"]
    sem_estado = re.sub(r"state=[^&]+&?", "", volta)

    assert client.get(sem_estado).status_code == 403
    assert ator_do_cliente(client) is None


def test_sob_a_marca_de_producao_o_provedor_nao_existe(client, configurado, settings, validadora):
    """A recusa em execução: mesmo configurado depois do *boot*, a marca de produção o apaga."""
    settings.AMBIENTE_DE_PRODUCAO = True

    assert provedor_configurado() is None
    assert client.get(reverse("interface:entrar-institucional")).status_code == 503
