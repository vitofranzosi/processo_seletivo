"""A frase publicada de cada regra do sorteio, gerada da regra escolhida (051, FR-930).

O método pede duas coisas para a mesma regra: o identificador que a máquina aplica e a frase que o
documento imprime (021, FR-013). Quem compunha escrevia a regra duas vezes, uma como escolha e outra
como prosa — e a prosa podia dizer outra coisa, porque nada a conferia contra a escolha.

**A frase aqui é a que o documento imprime quando ninguém escreveu outra**: o leitor do formulário a
põe no texto vazio, e a partir daí ela é conteúdo como qualquer outro, e o documento a lê de onde
sempre leu. O digitado continua valendo — há Edital que descreve a regra com as palavras da própria
fonte, e isso não é divergência de norma.

**Mora no `sorteios`**, ao lado de quem executa as regras: uma regra nova sem frase aqui é esquecida
no mesmo lugar em que é escrita.
"""

from processo_seletivo.sorteios.domain.normalizacao import DIGITOS_EM_SEQUENCIA, TEXTO_LITERAL
from processo_seletivo.sorteios.domain.substituicao import OCORRENCIA_SEGUINTE_DA_MESMA_FONTE

FRASE_DA_REGRA = {
    DIGITOS_EM_SEQUENCIA: (
        "Os dígitos do resultado publicado pela fonte, na ordem em que aparecem."
    ),
    TEXTO_LITERAL: "O texto do resultado publicado pela fonte, tal como aparece.",
    OCORRENCIA_SEGUINTE_DA_MESMA_FONTE: (
        "Não havendo a ocorrência na data prevista, vale a ocorrência seguinte da mesma fonte."
    ),
}


def da_regra(regra) -> str:
    """A frase da regra, ou `""` para regra que o sistema não conhece — que a validação recusa."""
    return FRASE_DA_REGRA.get(regra or "", "")
