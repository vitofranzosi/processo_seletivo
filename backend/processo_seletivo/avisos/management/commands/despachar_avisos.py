"""`manage.py despachar_avisos` — uma execução do despacho, pelo timer do systemd (066).

**A saída é diferente de 0 só quando a conexão com o servidor de correio não abre** (contracts/
despacho.md). É isso que aciona o `OnFailure=ps-alerta@%n.service` do runbook: chave desligada, nada
a fazer e outra execução em curso são estados normais, e alertar por eles ensinaria a ignorar o
alerta.
"""

from django.core.management.base import BaseCommand, CommandError

from processo_seletivo.avisos.application.despacho import ConexaoNaoAbriu, despachar


class Command(BaseCommand):
    help = "Despacha os avisos aos candidatos pendentes (066): uma execução, com limite por minuto."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limite",
            type=int,
            default=None,
            help="Teto de destinatários nesta execução (padrão: AVISOS_LIMITE_POR_MINUTO).",
        )

    def handle(self, *args, limite=None, **options):
        try:
            resumo = despachar(limite=limite)
        except ConexaoNaoAbriu as erro:
            raise CommandError(
                f"Despacho de avisos: {erro}. Nada saiu; a próxima execução tenta."
            ) from erro
        self.stdout.write(f"Despacho de avisos: {resumo}.")
