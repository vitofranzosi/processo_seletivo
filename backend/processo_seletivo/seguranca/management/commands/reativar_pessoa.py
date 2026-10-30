"""Reativa uma pessoa suspensa, pela implantação (107, `FR-3137`, decisão P2).

Voltam a valer os vínculos ainda vigentes, e nenhuma sessão anterior (`D-015`): a pessoa entra de
novo. O comando lista o que volta, como a confirmação da tela.
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
    help = "Reativa uma pessoa suspensa; nenhuma sessão anterior volta a valer."

    def add_arguments(self, parser):
        argumentos_da_pessoa(parser)
        parser.add_argument("--motivo", required=True, help="O ato que determina a reativação.")

    def handle(self, *args, **opcoes):
        pessoa = pessoa_do_provedor(opcoes["provedor"], opcoes["identificador"])
        try:
            suspensao.reativar(
                None,
                pessoa=pessoa,
                motivo=opcoes["motivo"],
                now=timezone.now(),
                por_implantacao=True,
            )
        except DomainError as recusa:
            raise CommandError(f"{recusa.code}: {recusa.detail}") from recusa
        self.stdout.write(f"{pessoa.username} reativada. Voltam a valer:")
        voltam = suspensao.acessos_que_voltam(pessoa)
        for escopo, papeis in voltam.items():
            self.stdout.write(f"  {escopo}: {', '.join(papeis)}")
        if not voltam:
            self.stdout.write("  nenhum vínculo vigente.")
