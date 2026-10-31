"""O nome anterior de `semear_unidades`, mantido como apelido (110, `D-003`, EC-17).

Um `ps-migrar` ou um `entrypoint.sh` instalado antes da 110 chama este nome. O deploy de uma versão
nova não pode falhar por isso: o apelido faz exatamente o que a semente faz, com a mesma saída e o
mesmo código de saída, e escreve no *stderr* — e não no *stdout*, cuja primeira linha o guia
ensina a ler — que o roteiro deve ser atualizado. Sai quando nenhum *log* de implantação tiver mais
o aviso.
"""

from processo_seletivo.unidades.management.commands.semear_unidades import Command as Semente

AVISO = (
    "sincronizar_unidades é o nome anterior de semear_unidades; atualize o roteiro que o chamou."
)


class Command(Semente):
    help = "Nome anterior de semear_unidades, mantido como apelido."

    def handle(self, *args, **opcoes):
        self.stderr.write(AVISO)
        return super().handle(*args, **opcoes)
