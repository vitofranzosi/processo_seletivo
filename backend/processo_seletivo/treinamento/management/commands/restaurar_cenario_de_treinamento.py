"""Restaura um cenário de treinamento ao estado inicial, em rodada nova (134, FR-4620 a FR-4626)."""

from django.core.management.base import CommandError

from processo_seletivo.treinamento import servico
from processo_seletivo.treinamento.management.commands._base import ComandoDeTreinamento


class Command(ComandoDeTreinamento):
    help = (
        "Cria a rodada seguinte de UM cenário, no estado inicial, e cancela a rodada anterior "
        "pelos comandos de cancelamento. Nada é excluído. Exige --confirmar com o código."
    )
    escrita = True

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--confirmar",
            default="",
            help="repita o código do cenário (por exemplo C07) para autorizar a restauração",
        )

    def executar(self, *, escreve, unidade, cenario, confirmar, autoridade, **_):
        if len(cenario) != 1:
            raise CommandError("Restaure um cenário por vez: informe exatamente um --cenario.")
        codigo = cenario[0].strip().upper()
        plano = servico.plano_de_restauracao(codigo, unidade)
        anterior = plano["manifesto"]
        self.stdout.write(f"{codigo} — {plano['cenario'].nome}")
        self.stdout.write(
            f"  Rodada em uso: {anterior.rodada}, Processo {anterior.processo.institutional_code}."
        )
        if plano["mudancas"]:
            self.stdout.write("  Exercitada desde a criação (o histórico fica preservado):")
            for mudanca in plano["mudancas"]:
                self.stdout.write(f"    {mudanca}")
        self.stdout.write(f"  Será criada a rodada {plano['rodada_nova']}, no estado inicial.")
        for edital in plano["a_cancelar"]:
            self.stdout.write(
                f"  Será cancelado o Edital {edital.number}/{edital.year} ({edital.status})."
            )
        self.stdout.write(
            "  Um Edital que entrar no Processo até a gravação também será cancelado."
        )
        if plano["designacoes_a_revogar"]:
            self.stdout.write(
                f"  Serão revogadas, com motivo, {plano['designacoes_a_revogar']} designação(ões) "
                "para a formalização nos Editais deste Processo; as pessoas e os papéis delas "
                "ficam como estão."
            )
        if plano["processo_a_cancelar"] is not None:
            self.stdout.write(
                f"  Será cancelado o Processo {anterior.processo.institutional_code}."
            )
        self.stdout.write(
            "  Nenhum registro será excluído; outros cenários e os Editais reais não são tocados."
        )
        if not escreve:
            self.stdout.write("Pré-visualização: nada foi gravado.")
            return
        if confirmar.strip().upper() != codigo:
            raise CommandError(
                f"Recusado: confirme a restauração repetindo o código, com --confirmar {codigo}."
            )
        anterior, novo = servico.restaurar(
            plano, unidade, saida=self.stdout, autoridade=autoridade or None
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"{codigo} restaurado: rodada {novo.rodada}, Processo "
                f"{novo.processo.institutional_code}. A rodada {anterior.rodada} foi cancelada."
            )
        )
