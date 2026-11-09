"""Acrescenta ao banco os cenários de treinamento que ainda não existem (134, FR-4611)."""

from processo_seletivo.treinamento import servico
from processo_seletivo.treinamento.management.commands._base import ComandoDeTreinamento, linha


class Command(ComandoDeTreinamento):
    help = (
        "Cria os cenários de treinamento que ainda não existem nesta unidade. Não altera os que "
        "existem, nem nada que o gerador não tenha criado."
    )
    escrita = True

    def executar(self, *, escreve, unidade, cenario, autoridade, **_):
        if not escreve:
            self.stdout.write("Pré-visualização: nada será gravado.")
            for item, decisao, motivos in servico.planejar(cenario, unidade):
                linha(self.stdout, item.codigo, decisao, [item.nome, *motivos])
            return
        resultados = servico.carregar(
            cenario, unidade, saida=self.stdout, autoridade=autoridade or None
        )
        self.stdout.write("\nResumo:")
        for item, decisao, motivos in resultados:
            linha(self.stdout, item.codigo, decisao, [item.nome, *motivos])
        falhas = [item for item, decisao, _ in resultados if decisao in ("FALHOU", "RECUSAR")]
        if falhas:
            self.stderr.write(
                f"{len(falhas)} cenário(s) não foram criados; os demais ficaram como estão."
            )
