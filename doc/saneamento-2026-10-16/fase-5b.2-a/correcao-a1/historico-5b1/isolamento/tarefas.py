"""Tarefas explícitas, nunca chamadas pela inicialização web. Não executar na Fase 5B.1."""

import json
import os
import sys
from datetime import datetime

from contrato import ADMIN, BANCO, IDENTIDADE, MIGRACAO, RUNTIME, exigir_selecao, verificar_banco

exigir_selecao()
if len(sys.argv) != 3 or sys.argv[2] != IDENTIDADE or sys.argv[1] not in {"esquema", "baseline", "conferir"}:
    raise SystemExit("Tarefa explícita e identidade de autorização obrigatórias")

import django

django.setup()
from django.core.management import call_command
from django.db import connection


def usar_papel(usuario, senha):
    connection.close()
    connection.settings_dict["USER"] = usuario
    connection.settings_dict["PASSWORD"] = senha


def conferir_destino(usuario):
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_database(), current_user")
        if cursor.fetchone() != (BANCO, usuario):
            raise RuntimeError("Destino ou papel não autorizado")


acao = sys.argv[1]
if acao == "esquema":
    admin = os.environ["HOM_ADMIN_PASSWORD"]
    migracao = os.environ["HOM_MIGRATION_PASSWORD"]
    usar_papel(ADMIN, admin)
    conferir_destino(ADMIN)
    with connection.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM pg_tables WHERE schemaname !~ '^pg_' AND schemaname <> 'information_schema'")
        if cursor.fetchone()[0] != 0:
            raise RuntimeError("Esquema exige banco isolado vazio; não reparar ou sobrescrever")
    argumentos = dict(migration_role=MIGRACAO, migration_password=migracao,
                      runtime_role=RUNTIME, runtime_password=os.environ["DB_RUNTIME_PASSWORD"])
    call_command("provisionar_papeis", **argumentos)
    usar_papel(MIGRACAO, migracao)
    call_command("migrate", interactive=False)
    usar_papel(ADMIN, admin)
    call_command("provisionar_papeis", **argumentos)
    with connection.cursor() as cursor:
        cursor.execute("CREATE SCHEMA homologacao_controle")
        cursor.execute("REVOKE ALL ON SCHEMA homologacao_controle FROM PUBLIC")
        cursor.execute("CREATE TABLE homologacao_controle.identidade (identidade uuid PRIMARY KEY)")
        cursor.execute("INSERT INTO homologacao_controle.identidade VALUES (%s::uuid)", (IDENTIDADE,))
        cursor.execute("CREATE TABLE homologacao_controle.execucoes (tipo text PRIMARY KEY, instante timestamptz NOT NULL)")
        cursor.execute("GRANT USAGE ON SCHEMA homologacao_controle TO ps_f4_runtime")
        cursor.execute("GRANT SELECT ON homologacao_controle.identidade TO ps_f4_runtime")
        cursor.execute("GRANT SELECT, INSERT ON homologacao_controle.execucoes TO ps_f4_runtime")
    usar_papel(RUNTIME, os.environ["DB_RUNTIME_PASSWORD"])
    verificar_banco(connection)
elif acao == "conferir":
    verificar_banco(connection)
else:
    verificar_banco(connection)
    from django.utils import timezone
    from processo_seletivo.processos.models import ProcessoSeletivo
    if ProcessoSeletivo.objects.exists():
        raise RuntimeError("Baseline exige ausência de Processos; não repetir nem excluir dados")
    instante = datetime.fromisoformat(os.environ["HOM_BASELINE_AGORA"])
    if instante.isoformat() != "2026-10-16T12:00:00-03:00":
        raise RuntimeError("Relógio sintético diverge do manifesto")
    with connection.cursor() as cursor:
        # Reserva antes da carga; falha parcial mantém reserva e evidências, sem repetição automática.
        cursor.execute("INSERT INTO homologacao_controle.execucoes VALUES ('baseline-v1', %s)", (instante,))
    original = timezone.now
    try:
        timezone.now = lambda: instante
        call_command("seed_demo", codigo="HOMOLOGACAO-F4-SINTETICA-01", numero="31", ano=2026,
                     titulo="HOMOLOGAÇÃO SINTÉTICA — SEM VALOR OFICIAL", janela_recursal="declarada", dias_atras=0)
    finally:
        timezone.now = original
    print(json.dumps({"baseline": "f4-sintetico-v1", "relogio": instante.isoformat(),
                      "identidade": IDENTIDADE, "repeticao": "proibida"}))
connection.close()
