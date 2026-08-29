"""Aplica a política de privilégios dos papéis PostgreSQL (FR-019 da 003).

Ordem de implantação: **provisionar, migrar, provisionar de novo**. Papel e privilégio default
existem antes de qualquer tabela; privilégio de tabela só pode ser concedido depois que ela existe.
A primeira passada, em banco vazio, cria os papéis e não encontra tabela para proteger; a segunda,
depois das migrations, é a que tranca. O comando diz quantas tabelas protegeu justamente para que
a segunda passada esquecida apareça agora, e não numa auditoria meses depois.

Precisa rodar com um papel que possa criar papéis — normalmente o superusuário da instalação —,
e não com o de runtime.
"""

import os
import re

from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from processo_seletivo.seguranca.papeis import (
    CONSULTA_DE_CONFERENCIA,
    TABELAS_APPEND_ONLY,
    comandos,
    conferencia,
)

SEGREDO_EM_SQL = re.compile(r"(PASSWORD\s+)'(?:[^']|'')*'", re.IGNORECASE)


def sem_segredos(sql: str) -> str:
    """Oculta senhas antes de imprimir.

    `--dry-run` existe para ser lido, colado em revisão e anexado a chamado. Imprimir a senha em
    texto puro transformaria a conferência da política num vazamento de credencial.
    """
    return SEGREDO_EM_SQL.sub(r"\1'********'", sql)


class Command(BaseCommand):
    help = "Cria os papéis de migração e de runtime e aplica seus privilégios."

    def add_arguments(self, parser):
        parser.add_argument("--migration-role", default=os.getenv("DB_MIGRATION_USER"))
        parser.add_argument("--migration-password", default=os.getenv("DB_MIGRATION_PASSWORD"))
        parser.add_argument("--runtime-role", default=os.getenv("DB_RUNTIME_USER"))
        parser.add_argument("--runtime-password", default=os.getenv("DB_RUNTIME_PASSWORD"))
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Imprime os comandos, com as senhas ocultas, sem executá-los.",
        )

    def handle(self, *args, **options):
        exigidos = {
            "migration_role": "DB_MIGRATION_USER",
            "migration_password": "DB_MIGRATION_PASSWORD",
            "runtime_role": "DB_RUNTIME_USER",
            "runtime_password": "DB_RUNTIME_PASSWORD",
        }
        faltando = [nome for nome in exigidos if not options.get(nome)]
        if faltando:
            raise CommandError(
                "Informe "
                + ", ".join(f"--{nome.replace('_', '-')}" for nome in faltando)
                + " ou as variáveis "
                + ", ".join(exigidos[nome] for nome in faltando)
                + "."
            )
        if connection.vendor != "postgresql":
            raise CommandError("O provisionamento de papéis só se aplica a PostgreSQL.")

        instrucoes = comandos(
            database=connection.settings_dict["NAME"],
            migration_role=options["migration_role"],
            migration_password=options["migration_password"],
            runtime_role=options["runtime_role"],
            runtime_password=options["runtime_password"],
        )
        if options["dry_run"]:
            for instrucao in instrucoes:
                self.stdout.write(sem_segredos(instrucao.strip()))
            return

        with connection.cursor() as cursor:
            for instrucao in instrucoes:
                cursor.execute(instrucao)
            cursor.execute(CONSULTA_DE_CONFERENCIA, conferencia(options["runtime_role"]))
            conferidas = cursor.fetchall()

        excessivas = [nome for nome, excessivo in conferidas if excessivo]
        if excessivas:
            raise CommandError(
                "O papel de runtime continua com UPDATE ou DELETE em: "
                + ", ".join(excessivas)
                + ". A política foi aplicada mas não teve efeito — verifique se o papel herda "
                "privilégio de outro (PUBLIC ou um grupo) antes de considerar o banco pronto."
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Papéis provisionados. {len(conferidas)} de {len(TABELAS_APPEND_ONLY)} tabelas "
                "append-only estão sem UPDATE nem DELETE para o runtime."
            )
        )
        if len(conferidas) < len(TABELAS_APPEND_ONLY):
            self.stdout.write(
                self.style.WARNING(
                    "As demais ainda não existem neste banco. Aplique as migrations e execute "
                    "este comando outra vez — é a segunda passada que tranca as tabelas criadas "
                    "por elas."
                )
            )
