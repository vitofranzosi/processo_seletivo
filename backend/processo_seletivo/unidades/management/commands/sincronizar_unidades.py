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
        # **Os modelos iniciais dos avisos nascem aqui, uma vez por unidade** (066, `R-012`): é o
        # único ponto que já percorre todas as unidades com autor e trilha, e data migration não
        # pode importar `application`. A linha diz quantos foram criados — zero, depois da primeira
        # sincronização, e para sempre: a unidade que inativou os três continua com os dela.
        from processo_seletivo.avisos.application.modelos import garantir_modelos_iniciais

        self.stdout.write(f"Modelos de aviso: {garantir_modelos_iniciais()} criados.")
