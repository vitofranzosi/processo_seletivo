"""Quem **não** julga este recurso — cinco perguntas pontuais, e nenhuma taxonomia nova.

O impedimento aqui não é conceito novo: é o `Impedimento` da 012 mais quatro perguntas sobre
autoria de atos que já estão gravados. Criar um segundo conceito de impedimento — tabela própria,
ciclo de vida próprio — significaria manter dois em coerência, e a 012 já decidiu onde ele mora.

```text
avaliacao.concluida_por    == ator?   →  concluiu a Avaliação que fundamentou o Resultado
resultado.consolidado_por  == ator?   →  consolidou o Resultado, ou constatou a Ocorrência
ato.emitido_por            == ator?   →  emitiu o ato de ordenação atacado
publicacao.publicado_por   == ator?   →  praticou a publicação atacada
Impedimento(ator, inscricao) existe?  →  o impedimento declarado da 012
```

**Cinco perguntas por ato de julgamento, e nenhuma por linha de listagem.** A listagem mostra
recursos que o ator talvez não possa julgar, e é a tela da peça que nomeia o impedimento. Perguntar
na listagem custaria a consulta por linha que a 012 já recusou uma vez (T-006, FR-031).

**A mensagem nomeia qual das cinco razões.** "Você está impedido" sem dizer por quê é decisão que
ninguém consegue conferir — e, sendo a autoria de um ato o que impede, a razão é verificável.
"""

from processo_seletivo.avaliacoes.models import Impedimento

AVALIOU = "avaliou"
CONSOLIDOU = "consolidou"
EMITIU = "emitiu"
PUBLICOU = "publicou"
DECLARADO = "declarado"

RAZOES = {
    AVALIOU: "Você concluiu a Avaliação que fundamentou o resultado atacado.",
    CONSOLIDOU: "Você consolidou o resultado atacado.",
    EMITIU: "Você emitiu o ato de ordenação atacado.",
    PUBLICOU: "Você praticou a publicação atacada.",
    DECLARADO: "Há impedimento declarado seu quanto a esta inscrição.",
}

BARRADO = "appeal_judge_barred"


def impedimento(ator, recurso):
    """A razão que impede este ator de julgar esta peça, ou `None`.

    Devolve a razão em vez de um booleano porque a tela precisa nomeá-la **antes de qualquer
    botão** (FR-042): oferecer o julgamento e recusá-lo no clique seria fazer a pessoa descobrir o
    impedimento depois de escrever a motivação.
    """
    subject = getattr(ator, "subject", "")
    if not subject:
        return None

    resultado = recurso.resultado_atacado
    if resultado is not None:
        # Ocorrência não tem Avaliação, e é por isso que a pergunta é condicional: nesse ramo quem
        # **constatou** é quem consta em `consolidado_por`, e a segunda pergunta já o alcança.
        if resultado.avaliacao_id is not None and resultado.avaliacao.concluida_por == subject:
            return AVALIOU
        if resultado.consolidado_por == subject:
            return CONSOLIDOU

    publicacao = recurso.publicacao_atacada
    if publicacao is not None:
        if publicacao.ato.emitido_por == subject:
            return EMITIU
        if publicacao.publicado_por == subject:
            return PUBLICOU

    if Impedimento.objects.filter(
        identity_subject=subject, inscricao_id=recurso.inscricao_id
    ).exists():
        return DECLARADO
    return None
