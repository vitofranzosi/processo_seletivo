"""O que os quatro comandos de cenários de treinamento têm em comum (134)."""

from django.core.management.base import BaseCommand, CommandError

from processo_seletivo.treinamento import ambiente
from processo_seletivo.treinamento.servico import Recusa

UNIDADE_PADRAO = "cefor"


class ComandoDeTreinamento(BaseCommand):
    escrita = False

    def add_arguments(self, parser):
        parser.add_argument(
            "--unidade",
            default=UNIDADE_PADRAO,
            help=f"a unidade (escopo) dos cenários; padrão: {UNIDADE_PADRAO}",
        )
        parser.add_argument(
            "--cenario",
            action="append",
            default=[],
            help="código do cenário (C01 a C15); repetível. Sem ele, todos.",
        )
        if self.escrita:
            parser.add_argument(
                "--banco",
                default="",
                help="o nome do banco de destino, por extenso — confirma onde se vai gravar",
            )
            parser.add_argument(
                "--autoridade",
                default="",
                help=(
                    "identificador da autoridade que assina os atos fictícios; sem ele, a "
                    "primeira vigente já usada da unidade"
                ),
            )
            parser.add_argument(
                "--dias-atras",
                type=int,
                default=0,
                help=(
                    "monta o cenário como se ele tivesse ocorrido há N dias; serve para que o "
                    "prazo recursal de cinco dias já nasça encerrado (N de 6 em diante)"
                ),
            )
            parser.add_argument(
                "--dry-run",
                action="store_true",
                help="mostra o que seria feito, sem gravar nada",
            )

    def cabecalho(self):
        destino = ambiente.descrever()
        self.stdout.write(
            f"Banco {destino['banco']} em {destino['servidor']} ({destino['motor']}), "
            f"configuração {destino['configuracao'] or '—'}, "
            f"chave {ambiente.CHAVE}={'ligada' if destino['chave'] else 'desligada'}."
        )

    def handle(self, *args, **opcoes):
        escreve = self.escrita and not opcoes.get("dry_run")
        ambiente.exigir(banco_informado=opcoes.get("banco"), escrita=escreve)
        self.cabecalho()
        try:
            self.executar(escreve=escreve, **opcoes)
        except Recusa as recusa:
            raise CommandError(f"Recusado: {recusa}") from recusa


def linha(saida, codigo, rotulo, detalhes):
    saida.write(f"  {codigo:4} {rotulo:13} {'; '.join(str(d) for d in detalhes)}")
