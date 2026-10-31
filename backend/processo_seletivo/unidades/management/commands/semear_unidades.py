"""Semeia o registro de Unidades num banco vazio, e garante os modelos iniciais (110, `D-003`).

Roda no `make preparar`, no `entrypoint.sh` do compose e no `ps-migrar`, depois da segunda passada
do provisionamento. Num banco novo, registra as unidades do `unidades.json`; num banco que já tem
unidade, não lê o arquivo e não grava unidade nenhuma — o registro é da aplicação (`D-001`). A
primeira linha da saída diz qual dos dois aconteceu, para que o roteiro de implantação a leia.

`--exportar` imprime o registro atual no formato do arquivo, sem gravar: serve só à reversão
(`D-016`, `migracao.md` da 110).
"""

import json

from django.core.management.base import BaseCommand, CommandError

from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.unidades.application import semente


class Command(BaseCommand):
    help = "Semeia o registro de Unidades num banco vazio (unidades/unidades.json)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--arquivo",
            default=str(semente.ARQUIVO),
            help="Outra semente — para um banco novo de teste ou homologação, e nunca em produção.",
        )
        parser.add_argument(
            "--exportar",
            action="store_true",
            help="Imprime o registro atual no formato da semente, sem gravar (para reverter).",
        )

    def handle(self, *args, **opcoes):
        if opcoes["exportar"]:
            self.stdout.write(json.dumps(semente.exportar(), ensure_ascii=False, indent=2))
            return
        try:
            resultado = semente.semear(opcoes["arquivo"])
        except DomainError as recusa:
            raise CommandError(f"{recusa.code}: {recusa.detail}") from recusa
        if resultado.semeadas:
            self.stdout.write(f"Unidades: {resultado.semeadas} semeadas.")
        else:
            self.stdout.write(
                f"Unidades: registro com {resultado.registradas} unidades; a semente não se aplica."
            )
        # **Os modelos iniciais dos avisos nascem aqui, uma vez por unidade** (066, `R-012`): é o
        # único ponto que percorre todas as unidades na implantação. A linha diz quantos foram
        # criados — zero, depois da primeira vez, e para sempre: a unidade que inativou os três
        # continua com os dela. A unidade cadastrada pela tela nasce com os dela (110, FR-3319).
        from processo_seletivo.avisos.application.modelos import garantir_modelos_iniciais

        self.stdout.write(f"Modelos de aviso: {garantir_modelos_iniciais()} criados.")
