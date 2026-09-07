"""O manager que separa o vigente do superado — e por que ele não é o `objects`.

**Duas leituras deste sistema quebram em silêncio** quando existem dois Resultados do mesmo par, e
nenhuma das duas levanta exceção:

1. `classificacao/application/calculo.py` monta `{etapa_id: pontuacao}` por inscrição. Dois
   Resultados da mesma Etapa **colapsam**, e o último do queryset vence — sem `order_by`, sem erro,
   sem log. Ordem classificatória errada, e ninguém fica sabendo.
2. Os quatro `Exists` da progressão em `prontidao.py` continuariam excluindo quem teve a eliminação
   **superada**, tornando o deferimento inofensivo exatamente onde ele deveria valer.

Por isso o filtro não é "lembrar de filtrar": é um manager nomeado, um `order_by` determinístico no
cálculo, e um teste estrutural que falha em uso não declarado de `ResultadoEtapa.objects`.

**Nomeado, e nunca substituindo o `objects`.** A reprodução histórica **precisa** ver os superados:
`reproducao.py` lê os Resultados por `pk__in` dos ids gravados na proveniência do ato, e é isso que
mantém a IO-5 da `015` verdadeira — a mesma proveniência reproduz a mesma ordem. Um default que
escondesse os superados faria o caminho correto ser o exótico, e quebraria a reprodução no dia em
que o primeiro recurso fosse deferido (018, T-004).
"""

from django.db import models


class VigentesManager(models.Manager):
    """Só os Resultados que ninguém sucedeu.

    Vigência é **derivada da cadeia**, e não coluna: `sucessor` é o `related_name` reverso de
    `resultado_anterior`, e não ter sucessor é a definição. É a mesma forma que `AtoDeOrdenacao` e
    `PublicacaoResultado` já usam, pela mesma razão — não há estado a manter coerente porque não há
    estado.
    """

    def get_queryset(self):
        return super().get_queryset().filter(sucessor__isnull=True)
