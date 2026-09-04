"""As duas formas de conclusão, e o que a decisória afirma.

O que a Etapa publica é a **forma**; o que o avaliador registra na forma decisória é o **sentido**.
São dois vocabulários com papéis distintos, e um terceiro não mora aqui: o **rótulo** — "Deferido",
"Apto", "Elegível" — é dado publicado pela Etapa, e não enumeração (012, D-008).

Manter o rótulo fora deste módulo é a decisão inteira em uma linha. `Deferido/Indeferido`,
`Apto/Inapto`, `Elegível/Não elegível` e `Classificado/Desclassificado` são o mesmo juízo com o
vocabulário que cada Edital escolheu: um enum com os quatro pares teria oito valores para dois
significados e cresceria a cada Edital novo, que é hard-code de regra sujeita a legislação.

**Por que vivem em `avaliacoes`.** Os dois descrevem a conclusão, que é conceito da 012, e a direção
de dependência que já existe é `resultados` importando de `avaliacoes` — nunca o contrário.
`editais` não os importa: ele confere a string publicada contra o contrato, e não conhece o domínio
da conclusão.
"""

from django.db import models


class Forma(models.TextChoices):
    """Como a Etapa exige que a avaliação seja concluída.

    A ausência desta declaração, em conteúdo anterior à versão canônica 6, significa `PONTUADA` — e
    quem faz essa leitura é `previsao.forma_publicada`, num lugar só (012, FR-120).
    """

    PONTUADA = "PONTUADA"
    DECISORIA = "DECISORIA"


class Sentido(models.TextChoices):
    """O que o avaliador afirmou, na forma decisória.

    Binário e **neutro**, de propósito. Não se chama `decisão`: avaliar não é decidir, e duas
    análises documentais podem afirmar sentidos opostos — resolver isso é da 013 (012, P-006).
    """

    FAVORAVEL = "FAVORAVEL"
    DESFAVORAVEL = "DESFAVORAVEL"
