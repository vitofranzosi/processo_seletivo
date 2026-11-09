"""Confere propriedade, integridade e prazos dos cenários de treinamento (134, FR-4617)."""

from processo_seletivo.treinamento import servico
from processo_seletivo.treinamento.management.commands._base import ComandoDeTreinamento, linha


class Command(ComandoDeTreinamento):
    help = (
        "Verifica, para cada cenário, se o Processo é comprovadamente do gerador, se foi "
        "exercitado desde a criação e se o prazo do estado inicial ainda vale."
    )

    def executar(self, *, unidade, cenario, **_):
        problemas = 0
        for item in servico.escolher(cenario):
            atual = servico.situacao(item, unidade)
            detalhes = [item.nome]
            if atual.vestigios:
                detalhes.append(
                    "Processo com código reservado e sem manifesto: "
                    + ", ".join(p.institutional_code for p in atual.vestigios)
                )
            detalhes += atual.problemas + atual.avisos
            linha(self.stdout, item.codigo, atual.estado, detalhes)
            for mudanca in atual.mudancas:
                self.stdout.write(f"         {mudanca}")
            problemas += bool(atual.problemas or atual.vestigios)
        if problemas:
            self.stderr.write(f"{problemas} cenário(s) com problema de propriedade.")
