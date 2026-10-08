"""Aplica `unidades/unidades.json` ao banco, com trilha (060, R-003).

Roda no `make preparar`, depois da segunda passada do provisionamento, e é idempotente: sem mudança
no arquivo, não grava nada. A linha de saída diz quantas foram criadas, alteradas e mantidas, para
que uma sincronização que não aplicou nada apareça agora — e não no primeiro documento com o
cabeçalho errado.
"""

from django.core.management.base import BaseCommand, CommandError

from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.unidades.application import sincronizacao


class Command(BaseCommand):
    help = "Aplica o registro declarado de Unidades (unidades/unidades.json)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--arquivo",
            default=str(sincronizacao.ARQUIVO),
            help="Outro arquivo de registro — para conferência, e nunca em produção.",
        )

    def handle(self, *args, **opcoes):
        try:
            criadas, alteradas, mantidas = sincronizacao.sincronizar(
                sincronizacao.ler(opcoes["arquivo"])
            )
        except DomainError as recusa:
            raise CommandError(f"{recusa.code}: {recusa.detail}") from recusa
        self.stdout.write(
            f"Unidades: {criadas} criadas, {alteradas} alteradas, {mantidas} sem mudança."
        )
