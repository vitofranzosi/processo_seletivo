"""Suspende uma pessoa em todas as unidades, pela implantação (107, `FR-3137`, decisão P1).

O único caminho que alcança quem tem administração institucional, e serve também a qualquer outra
pessoa. Grava sob o ator `implantacao`, exige o motivo, e encerra todas as sessões da pessoa
(`D-015`).
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from processo_seletivo.seguranca.application import suspensao
from processo_seletivo.seguranca.management.commands._pessoa_do_provedor import (
    argumentos_da_pessoa,
    pessoa_do_provedor,
)
from processo_seletivo.shared.api.problems import DomainError


class Command(BaseCommand):
    help = "Suspende uma pessoa em todas as unidades, encerrando todas as sessões dela."

    def add_arguments(self, parser):
        argumentos_da_pessoa(parser)
        parser.add_argument("--motivo", required=True, help="O ato que determina a suspensão.")

    def handle(self, *args, **opcoes):
        pessoa = pessoa_do_provedor(opcoes["provedor"], opcoes["identificador"])
        try:
            suspensao.suspender(
                None,
                pessoa=pessoa,
                motivo=opcoes["motivo"],
                now=timezone.now(),
                por_implantacao=True,
            )
        except DomainError as recusa:
            raise CommandError(f"{recusa.code}: {recusa.detail}") from recusa
        self.stdout.write(f"{pessoa.username} suspensa; todas as sessões dela terminam.")
