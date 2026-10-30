"""A exclusão dos registros do piloto, 90 dias depois do relatório final (071, `R-021`, `FR-1509`).

**Não contraria o "nada é excluído"** do projeto, que é sobre dado normativo. As trocas do piloto
não são ato do certame: são a evidência de uma avaliação, com perguntas de gente — mascaradas, o
que não as torna anônimas —, e a DP-2 decidiu que elas não sobrevivem ao relatório por mais de 90
dias. A tabela não é append-only, e nenhuma outra é tocada: nada referencia uma troca.

**A exclusão fica na trilha**, com a contagem e a data do relatório. O que se apaga é evidência de
uma avaliação, e quem audita precisa poder dizer quando ela saiu e sob qual relatório — a saída do
comando some com o terminal (auditoria de administração institucional, 30/10). Um evento por
unidade, porque a trilha é lida por unidade e a troca pertence à do Edital sobre o qual se
perguntou; o ator é `implantacao`, como na sincronização das Unidades, porque quem roda o comando é
quem tem o acesso à máquina, e não um papel conferido. Sem troca a excluir, nada se grava: não há
unidade a que atribuir o nada.

**Sem agendamento.** O relatório final é um evento, e não um calendário: é a equipe quem roda o
comando, com a data dele, e um timer para um comando que roda uma vez seria infraestrutura a mais.
"""

from datetime import date, datetime, time, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.duvidas.models import TrocaDoPiloto
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.shared.tempo import ZONA
from processo_seletivo.unidades.domain import nomes
from processo_seletivo.unidades.models import Unidade

PRAZO = timedelta(days=90)
OPERACAO = "EXCLUIR_REGISTROS_DO_PILOTO"


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
        excluidas = 0
        with command_context() as agora:
            alvo = TrocaDoPiloto.objects.filter(criada_em__lt=fim)
            escopos = sorted(set(alvo.values_list("edital__institution_scope", flat=True)))
            for escopo in escopos:
                quantas, _ = alvo.filter(edital__institution_scope=escopo).delete()
                excluidas += quantas
                record_event(
                    actor=Actor(nomes.IMPLANTACAO, escopo),
                    permission=nomes.IMPLANTACAO,
                    operation=OPERACAO,
                    aggregate=Unidade.objects.get(codigo=escopo),
                    now=agora,
                    correlation_id="",
                    new_state="",
                    new_revision=None,
                    detalhe={
                        "trocas_excluidas": quantas,
                        "relatorio_final_em": relatorio.isoformat(),
                    },
                )
        self.stdout.write(f"{excluidas} trocas excluídas")
