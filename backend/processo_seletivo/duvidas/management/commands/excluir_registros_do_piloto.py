"""A exclusão dos registros do piloto, 90 dias depois do relatório final (071, `R-021`, `FR-1509`).

**Não contraria o "nada é excluído"** do projeto, que é sobre dado normativo. As trocas do piloto
não são ato do certame: são a evidência de uma avaliação, com perguntas de gente — mascaradas, o
que não as torna anônimas —, e a DP-2 decidiu que elas não sobrevivem ao relatório por mais de 90
dias. A tabela não é append-only, e nenhuma outra é tocada: nada referencia uma troca.

**Sem agendamento.** O relatório final é um evento, e não um calendário: é a equipe quem roda o
comando, com a data dele, e um timer para um comando que roda uma vez seria infraestrutura a mais.
"""

from datetime import date, datetime, time, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from processo_seletivo.duvidas.models import TrocaDoPiloto
from processo_seletivo.shared.tempo import ZONA

PRAZO = timedelta(days=90)


def _data(valor):
    try:
        return date.fromisoformat(valor)
    except ValueError:
        raise CommandError(f"Data inválida: {valor!r}; use AAAA-MM-DD.") from None


class Command(BaseCommand):
    help = "Exclui as trocas do piloto do assistente, 90 dias depois do relatório final."

    def add_arguments(self, parser):
        parser.add_argument("--relatorio-final-em", required=True, help="AAAA-MM-DD")

    def handle(self, *args, **opcoes):
        relatorio = _data(opcoes["relatorio_final_em"])
        liberada = relatorio + PRAZO
        if timezone.now().astimezone(ZONA).date() < liberada:
            raise CommandError(
                f"A exclusão só é permitida a partir de {liberada:%d/%m/%Y}, 90 dias depois do "
                f"relatório final de {relatorio:%d/%m/%Y}."
            )
        # As criadas até o fim do dia do relatório, no dia da zona institucional.
        fim = datetime.combine(relatorio + timedelta(days=1), time.min, tzinfo=ZONA)
        excluidas, _ = TrocaDoPiloto.objects.filter(criada_em__lt=fim).delete()
        self.stdout.write(f"{excluidas} trocas excluídas")
