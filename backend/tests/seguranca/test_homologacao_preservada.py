"""A homologação continua exatamente como hoje (106, US1; testes 1, 11 e 12 do pedido).

O teste 12 — os funcionais existentes continuam passando — é a suíte inteira, sem mudança de
resultado esperado; o que fica aqui é o que ela não afirmava por si.
"""

import ast
import pathlib

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from processo_seletivo.interface.identidade import CHAVE_SESSAO
from processo_seletivo.seguranca.models import IdentidadeExterna, Vinculo
from tests.interface.conftest import identificar
from tests.seguranca.apoio import ator_do_cliente, entrar, vincular

pytestmark = pytest.mark.django_db

RAIZ = pathlib.Path(__file__).resolve().parents[2] / "processo_seletivo"


# --- Teste 1: o acesso atual funciona em homologação controlada ----------------------------------


def test_o_seletor_identifica_como_antes(client, seletor_ligado):
    identificar(client, "ana.gestora", ["gestor", "auditor"])

    assert client.session[CHAVE_SESSAO] == {
        "subject": "ana.gestora",
        "escopo": "cefor",
        "papeis": ["gestor", "auditor"],
        "origem": "demonstracao",
    }
    assert client.get(reverse("interface:autoridades")).status_code == 200


def test_sem_provedor_a_pagina_de_acesso_e_a_de_antes(client, seletor_ligado):
    pagina = client.get(reverse("interface:identificar")).content.decode()

    assert "Acessar ambiente de demonstração" in pagina
    assert "A autenticação institucional ainda não foi integrada." in pagina
    assert "conta institucional" not in pagina


def test_com_provedor_o_seletor_continua_e_nao_cria_identidade(client, seletor_ligado, provedor):
    pagina = client.get(reverse("interface:identificar")).content.decode()
    assert "Entrar com a conta institucional" in pagina
    assert "Acessar ambiente de demonstração" in pagina

    identificar(client, "ana.gestora", ["gestor"])

    assert client.get(reverse("interface:autoridades")).status_code == 200
    assert not get_user_model().objects.exists()
    assert not Vinculo.objects.exists() and not IdentidadeExterna.objects.exists()


def test_a_identidade_de_demonstracao_nao_se_converte_em_institucional(
    client, seletor_ligado, provedor
):
    """O provedor que devolve o mesmo texto de um `subject` de demonstração cria outra pessoa."""
    identificar(client, "ana.gestora", ["gestor"])
    client.post(reverse("interface:sair"))

    entrar(client, "ana.gestora")

    criada = get_user_model().objects.get()
    assert criada.username != "ana.gestora"
    assert criada.username.startswith("pessoa-")


def test_so_com_a_entrada_institucional_o_envio_do_seletor_nao_vale(client, settings, provedor):
    settings.INTERFACE_SELETOR_IDENTIDADE = False
    resposta = client.post(
        reverse("interface:identificar"), {"subject": "ana.gestora", "papeis": ["gestor"]}
    )

    assert resposta.status_code == 503
    assert CHAVE_SESSAO not in client.session
    assert client.get(reverse("interface:identificar-demonstracao")).status_code == 503


def test_a_sessao_de_demonstracao_e_a_institucional_nao_se_misturam(
    client, seletor_ligado, provedor
):
    """Quem entra pelo provedor depois do seletor perde a identidade escolhida, e vice-versa."""
    from tests.seguranca.apoio import pessoa

    vincular(pessoa("ana-inst"), "cefor", "auditor")
    identificar(client, "ana.gestora", ["gestor"])

    entrar(client, "ana-inst")
    assert ator_do_cliente(client).permissions == {"auditoria:consultar"}

    identificar(client, "joao", ["elaborador"])
    ator = ator_do_cliente(client)
    assert (ator.subject, ator.institution_scope) == ("joao", "cefor")


# --- Teste 11: registros históricos e documentos íntegros ----------------------------------------


def _chamadas_da_migration():
    arvore = ast.parse((RAIZ / "seguranca" / "migrations" / "0001_initial.py").read_text())
    return [
        no.func.attr
        for no in ast.walk(arvore)
        if isinstance(no, ast.Call)
        and isinstance(no.func, ast.Attribute)
        and isinstance(no.func.value, ast.Name)
        and no.func.value.id == "migrations"
    ]


def test_a_migration_da_106_so_cria_tabelas_e_gatilhos():
    """Nenhuma alteração, remoção ou reescrita de tabela, linha ou documento (`FR-3030`)."""
    assert set(_chamadas_da_migration()) == {"CreateModel", "AddIndex", "RunPython"}
    from importlib import import_module

    migration = import_module("processo_seletivo.seguranca.migrations.0001_initial")
    sql = migration.PROTEGER.upper()
    for proibido in ("UPDATE ", "DELETE FROM", "INSERT ", "ALTER TABLE", "DROP TABLE", "TRUNCATE"):
        assert proibido not in sql.replace("BEFORE UPDATE", "").replace("OR DELETE", "")
    # As tabelas novas, e só a `auth_user` além delas — sem linha nenhuma a reescrever: os gatilhos
    # olham para a escrita futura.
    alvos = {
        linha.split(" ON ")[1].strip()
        for linha in migration.PROTEGER.splitlines()
        if " ON " in linha
    }
    assert alvos == {
        "seguranca_identidadeexterna",
        "seguranca_vinculo",
        "seguranca_revogacaodevinculo",
        "auth_user",
    }


def test_as_tabelas_append_only_anteriores_continuam_todas():
    from processo_seletivo.seguranca.papeis import TABELAS_APPEND_ONLY

    novas = ("seguranca_identidadeexterna", "seguranca_vinculo", "seguranca_revogacaodevinculo")
    assert TABELAS_APPEND_ONLY[-3:] == novas
    assert len(TABELAS_APPEND_ONLY) == 44
    assert len(set(TABELAS_APPEND_ONLY)) == 44
