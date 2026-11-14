"""*Non reformatio in pejus* — o recurso não pode piorar a situação de quem recorre.

**Consequência e pontuação, nunca posição** (FR-070, FR-071, FR-074). A distinção é a substância da
garantia, e confundi-la a inverteria:

```text
piora    a consequência deixa de habilitar, ou a pontuação cai
não é    a posição na ordem cai porque OUTRA pessoa foi corrigida
```

A posição é **relativa**: ela muda quando o resultado alheio muda, e a instituição não pode deixar
de corrigir o erro de A porque isso desloca B. Tratar queda de posição como piora tornaria a
vedação uma trava contra o próprio deferimento — e, no limite, congelaria a ordem no primeiro
recurso deferido.

A comparação é **decimal**, e nunca de ponto flutuante: a igualdade exata importa aqui tanto quanto
na nota mínima da 013, e é justamente no empate que o arredondamento binário decidiria errado.
"""

from processo_seletivo.resultados.domain import efeito as efeito_do_desfecho
from processo_seletivo.resultados.models import ResultadoEtapa

PIORA = "appeal_worsens_situation"

HABILITANTES = {ResultadoEtapa.Consequencia.HABILITADA}

MENSAGEM = (
    "A correção proposta pioraria a situação de quem recorreu, e o recurso não pode agravá-la. "
    "Nenhum resultado sucessor foi criado."
)


def habilita(consequencia):
    return str(consequencia) in {str(item) for item in HABILITANTES}


def piora(*, protegido, consequencia, pontuacao):
    """A correção proposta piora o que o `resultado_protegido` já dizia?

    Duas perguntas, e cada uma basta: a consequência **mais grave**, qualquer que seja a pontuação,
    e a **pontuação menor**, qualquer que seja a consequência (FR-070 da `018`). Mudar a
    consequência para uma menos grave não dispensa a segunda: um sucessor habilitado com nota
    abaixo da do superado continua sendo piora na nota.

    **A gravidade tem três degraus desde a 164** (FR-7028): habilitada, retirada da reserva e
    eliminada. Perder a habilitação continua piora; e a retirada que viraria eliminação também,
    embora nenhuma das duas "habilite" — a pergunta antiga, binária, deixava passar essa.

    Sem grandeza dos dois lados — o ramo da Ocorrência —, resta a consequência, e ela basta: é o
    caso em que só existem "eliminada" e "habilitada" a comparar.
    """
    if efeito_do_desfecho.mais_grave(consequencia, protegido.consequencia):
        return True
    if protegido.pontuacao is None or pontuacao is None:
        return False
    return pontuacao < protegido.pontuacao
