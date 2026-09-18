"""`ESTADO_CIVIL` flexionado por `SEXO` — a tabela da `D-004`, e nenhuma outra regra (`FR-442`).

**Oito strings escritas à mão, e não uma regra de sufixo.** A tentação é trocar o `o` final por `a`
quando o sexo é feminino, e ela funciona para os quatro casos de hoje — até o dia em que um estado
civil novo não terminar em `o`. Uma tabela de oito entradas erra alto e na hora: o valor que não
estiver nela não é flexionado, é ausente.

**O destino escreve `Casada`; este sistema guarda `CASADO` e exibe `Casado(a)`.** As três formas são
de públicos diferentes, e é por isso que a exportação não usa `legivel()` (`FR-445`): aquela função
serve à leitura humana das telas da `029`, e `Casado(a)` num arquivo de importação é um valor que o
destino não conhece.

**A flexão é total**, e isso não é sorte: `SEXO` é binário dos dois lados — dois valores aqui, dois
lá —, de modo que não há caso sem resposta. Se um dia o sexo deixar de ser binário nesta coleta, é
esta tabela que precisa de decisão nova, e é bom que ela seja o lugar onde a falta aparece.
"""

from processo_seletivo.requerimentos.domain import nomes as requerimento

# `(estado civil, sexo)` → a palavra que o destino escreve.
FLEXOES = {
    (requerimento.SOLTEIRO, requerimento.MASCULINO): "Solteiro",
    (requerimento.SOLTEIRO, requerimento.FEMININO): "Solteira",
    (requerimento.CASADO, requerimento.MASCULINO): "Casado",
    (requerimento.CASADO, requerimento.FEMININO): "Casada",
    (requerimento.DIVORCIADO, requerimento.MASCULINO): "Divorciado",
    (requerimento.DIVORCIADO, requerimento.FEMININO): "Divorciada",
    (requerimento.VIUVO, requerimento.MASCULINO): "Viúvo",
    (requerimento.VIUVO, requerimento.FEMININO): "Viúva",
}


def flexionar(estado_civil: str, sexo: str) -> str:
    """A palavra do destino, ou `""` quando não há o que flexionar.

    **`""` quando falta qualquer um dos dois**, e não uma forma neutra: sem o sexo declarado não há
    flexão a fazer, e escolher uma das duas seria atribuir à pessoa uma palavra que ela não disse.
    """
    return FLEXOES.get((estado_civil, sexo), "")
