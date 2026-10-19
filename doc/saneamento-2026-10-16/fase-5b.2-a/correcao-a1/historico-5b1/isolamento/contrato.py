"""Contrato exclusivo do laboratório. Não importa settings nem abre conexões."""

import os
from pathlib import Path

IDENTIDADE = "5dadcc37-7015-4a5a-b1a1-727dd7e3d901"
PROJETO = "cefor_homologacao_f4_20261016"
BANCO = "ps_homologacao_f4_20261016"
HOST = "banco-homologacao"
RUNTIME = "ps_f4_runtime"
ADMIN = "ps_f4_admin"
MIGRACAO = "ps_f4_migration"
LABEL = "br.edu.ifes.cefor.identidade"


def exigir_selecao():
    esperadas = {
        "HOMOLOGACAO_SELECIONADA": "SIM",
        "HOMOLOGACAO_ID": IDENTIDADE,
        "DJANGO_SETTINGS_MODULE": "settings_homologacao",
        "DB_HOST": HOST,
        "DB_PORT": "5432",
        "DB_NAME": BANCO,
        "DB_RUNTIME_USER": RUNTIME,
        "DJANGO_EMAIL_BACKEND": "django.core.mail.backends.console.EmailBackend",
        "ASSISTENTE_PILOTO": "false",
        "ASSISTENTE_NA_PAGINA_DO_EDITAL": "false",
    }
    for chave, esperado in esperadas.items():
        if os.environ.get(chave) != esperado:
            raise RuntimeError(f"Isolamento não comprovado: {chave}")
    for chave in ("ASSISTENTE_SERVICO", "ASSISTENTE_ENDERECO", "ASSISTENTE_CREDENCIAL",
                  "ASSISTENTE_TOKENIZER", "EMAIL_HOST", "EMAIL_HOST_USER", "EMAIL_HOST_PASSWORD"):
        if os.environ.get(chave):
            raise RuntimeError(f"Integração proibida: {chave}")
    if not os.environ.get("DB_RUNTIME_PASSWORD"):
        raise RuntimeError("Configuração sintética obrigatória ausente")
    if any(c.name != ".env.example" for c in Path("/app/backend").glob(".env*")):
        raise RuntimeError("Imagem contém .env proibido")


def verificar_banco(conexao):
    with conexao.cursor() as cursor:
        cursor.execute("SHOW server_version_num")
        if not 180000 <= int(cursor.fetchone()[0]) < 190000:
            raise RuntimeError("Versão PostgreSQL não autorizada")
        cursor.execute("SELECT current_database(), current_user")
        if cursor.fetchone() != (BANCO, RUNTIME):
            raise RuntimeError("Banco ou papel inesperado")
        cursor.execute("SELECT identidade::text FROM homologacao_controle.identidade")
        if cursor.fetchall() != [(IDENTIDADE,)]:
            raise RuntimeError("Marcador de propriedade do banco inválido")
        from processo_seletivo.seguranca.papeis import TABELAS_APPEND_ONLY
        for tabela in TABELAS_APPEND_ONLY:
            cursor.execute(
                "SELECT has_table_privilege(current_user, %s, 'UPDATE'), "
                "has_table_privilege(current_user, %s, 'DELETE')", (tabela, tabela),
            )
            if cursor.fetchone() != (False, False):
                raise RuntimeError("Privilégios de imutabilidade não comprovados")
            cursor.execute(
                "SELECT count(*) FROM pg_trigger WHERE tgrelid = %s::regclass "
                "AND NOT tgisinternal AND tgenabled IN ('O', 'A')", (tabela,),
            )
            if cursor.fetchone()[0] == 0:
                raise RuntimeError("Trigger habilitada não comprovada")
    from django.db.migrations.executor import MigrationExecutor
    executor = MigrationExecutor(conexao)
    if executor.migration_plan(executor.loader.graph.leaf_nodes()):
        raise RuntimeError("Há migrations pendentes; inicialização automática é proibida")
