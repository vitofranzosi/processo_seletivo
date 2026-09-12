"""Dobra de texto para comparação de exibição — acento e caixa deixam de distinguir.

**Por que num módulo compartilhado.** A dobra já existia duas vezes na árvore, com finalidades
diferentes: `comissoes` a usa para ordenar nomes, e `sorteios/domain/normalizacao.py` para produzir
material canônico de sorteio. Uma terceira cópia era o risco real — o comentário da `comissoes`
registra que **duas** implementações no mesmo arquivo já foram o defeito.

**O que não vem para cá.** A normalização do sorteio fica onde está. Lá ela é regra auditável, com
forma canônica própria e prova pública dependendo dela; unificá-la com uma dobra de exibição
confundiria dois propósitos e mexeria em código cuja saída é verificável por terceiros.
"""

import unicodedata


def dobrar(texto: str) -> str:
    """`"Informática"` e `"informatica"` viram a mesma coisa.

    Ignora acento porque procurar por "informatica" e não achar "Informática" parece defeito de
    busca, não escolha de sistema — e quem digita no celular quase nunca acentua.
    """
    sem_acento = unicodedata.normalize("NFKD", texto or "")
    return "".join(c for c in sem_acento if not unicodedata.combining(c)).casefold()
