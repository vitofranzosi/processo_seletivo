"""Retira a administração institucional de uma pessoa, pela implantação (107, `FR-3147`, P3).

Fecha a lacuna da `106`: até aqui, o comando só concedia, e a aplicação recusa o papel nos dois
sentidos. Retirar a última pessoa exige `--sem-administracao` (`D-018`); para trocar de pessoa,
`substituir_administracao_institucional`, que faz as duas coisas numa operação.
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from processo_seletivo.seguranca.application import acessos
from processo_seletivo.seguranca.management.commands._pessoa_do_provedor import (
    argumentos_da_pessoa,
    pessoa_do_provedor,
)
from processo_seletivo.shared.api.problems import DomainError


class Command(BaseCommand):
    help = "Retira a administração institucional de acessos de uma pessoa."

    def add_arguments(self, parser):
        argumentos_da_pessoa(parser)
        parser.add_argument("--motivo", required=True, help="O ato que determina a retirada.")
        parser.add_argument(
            "--sem-administracao",
            action="store_true",
            help="Retira mesmo que seja a última administração institucional vigente.",
        )

    def handle(self, *args, **opcoes):
        pessoa = pessoa_do_provedor(opcoes["provedor"], opcoes["identificador"])
        try:
            vinculo = acessos.retirar_administracao_institucional(
                pessoa=pessoa,
                motivo=opcoes["motivo"],
                sem_administracao=opcoes["sem_administracao"],
                now=timezone.now(),
            )
        except DomainError as recusa:
            raise CommandError(f"{recusa.code}: {recusa.detail}") from recusa
        self.stdout.write(
            f"Administração institucional retirada de {pessoa.username}, vínculo {vinculo.pk}."
        )
