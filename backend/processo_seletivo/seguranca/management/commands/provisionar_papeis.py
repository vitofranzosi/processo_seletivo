"""Aplica a política de privilégios dos papéis PostgreSQL (FR-019 da 003).

Executável do zero e quantas vezes for: cria os papéis que faltam, reafirma a senha do runtime e
reaplica os privilégios. Precisa rodar com um papel que possa criar papéis — normalmente o
superusuário da instalação —, e não com o de runtime.
"""

import os

from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from processo_seletivo.seguranca.papeis import TABELAS_APPEND_ONLY, comandos


class Command(BaseCommand):
    help = "Cria os papéis de migração e de runtime e aplica seus privilégios."

    def add_arguments(self, parser):
        parser.add_argument("--migration-role", default=os.getenv("DB_MIGRATION_USER"))
        parser.add_argument("--runtime-role", default=os.getenv("DB_RUNTIME_USER"))
        parser.add_argument("--runtime-password", default=os.getenv("DB_RUNTIME_PASSWORD"))
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Imprime os comandos sem executá-los.",
        )

    def handle(self, *args, **options):
        faltando = [
            nome
            for nome in ("migration_role", "runtime_role", "runtime_password")
            if not options.get(nome)
        ]
        if faltando:
            raise CommandError(
                "Informe "
                + ", ".join(f"--{nome.replace('_', '-')}" for nome in faltando)
                + " ou as variáveis DB_MIGRATION_USER, DB_RUNTIME_USER e DB_RUNTIME_PASSWORD."
            )
        if connection.vendor != "postgresql":
            raise CommandError("O provisionamento de papéis só se aplica a PostgreSQL.")

        instrucoes = comandos(
            database=connection.settings_dict["NAME"],
            migration_role=options["migration_role"],
            runtime_role=options["runtime_role"],
            runtime_password=options["runtime_password"],
        )
        if options["dry_run"]:
            for instrucao in instrucoes:
                self.stdout.write(instrucao.strip())
            return

        with connection.cursor() as cursor:
            for instrucao in instrucoes:
                cursor.execute(instrucao)

        self.stdout.write(
            self.style.SUCCESS(
                f"Papéis provisionados. O papel de runtime não recebe UPDATE nem DELETE em "
                f"{len(TABELAS_APPEND_ONLY)} tabelas append-only."
            )
        )
