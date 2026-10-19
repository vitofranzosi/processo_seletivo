"""Contrato exclusivo do laboratório. Não importa settings nem abre conexões."""

import os
import hashlib
import json
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


def validar_politica(politica, tabelas):
    if (politica.get("estado") != "APROVADA" or not tabelas
        or set(politica.get("tabelas", {})) != set(tabelas)):
        raise RuntimeError("Política de proteções incompleta/não aprovada")
    for gatilhos in politica["tabelas"].values():
        if not isinstance(gatilhos, dict) or not gatilhos:
            raise RuntimeError("Gatilhos esperados ausentes")
        for nome, hashes in gatilhos.items():
            if not isinstance(nome, str) or not nome or set(hashes) != {"trigger_sha256", "funcao_sha256"}:
                raise RuntimeError("Identidade de proteção incompleta")
            for valor in hashes.values():
                if (not isinstance(valor, str) or len(valor) != 64
                    or any(c not in "0123456789abcdef" for c in valor) or valor == "0" * 64):
                    raise RuntimeError("Hash de proteção inválido")


def verificar_gatilhos(linhas, esperados):
    observados = {}
    for nome, estado, definicao, funcao in linhas:
        if nome in observados or estado not in ("O", "A") or not definicao or not funcao:
            raise RuntimeError("Gatilho ausente, duplicado ou desabilitado")
        observados[nome] = {"trigger_sha256": hashlib.sha256(definicao.encode("utf-8")).hexdigest(),
                            "funcao_sha256": hashlib.sha256(funcao.encode("utf-8")).hexdigest()}
    if observados != esperados:
        raise RuntimeError("Definição de gatilho/função não corresponde à política aprovada")


def verificar_banco(conexao):
    politica = json.loads(Path(__file__).with_name("politica-protecoes.json").read_text(encoding="utf-8"))
    if politica.get("estado") != "APROVADA":
        raise RuntimeError("Política de proteções pendente; não abrir conexão")
    from processo_seletivo.seguranca.papeis import TABELAS_APPEND_ONLY
    validar_politica(politica, TABELAS_APPEND_ONLY)
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
        for tabela in TABELAS_APPEND_ONLY:
            cursor.execute(
                "SELECT has_table_privilege(current_user, %s, 'UPDATE'), "
                "has_table_privilege(current_user, %s, 'DELETE')", (tabela, tabela),
            )
            if cursor.fetchone() != (False, False):
                raise RuntimeError("Privilégios de imutabilidade não comprovados")
            cursor.execute(
                "SELECT tgname, tgenabled, pg_get_triggerdef(oid), pg_get_functiondef(tgfoid) "
                "FROM pg_trigger WHERE tgrelid = %s::regclass AND NOT tgisinternal", (tabela,),
            )
            verificar_gatilhos(cursor.fetchall(), politica["tabelas"][tabela])
    from django.db.migrations.executor import MigrationExecutor
    executor = MigrationExecutor(conexao)
    if executor.migration_plan(executor.loader.graph.leaf_nodes()):
        raise RuntimeError("Há migrations pendentes; inicialização automática é proibida")
