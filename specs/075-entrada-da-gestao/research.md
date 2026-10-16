# Research — 075

As decisões de produto e de desenho estão na spec (`D-001` a `D-006`). Aqui ficam as questões
técnicas que o plano precisou fechar.

## T-001 — Como conferir o destino

**Decisão**: aceitar só caminho relativo que comece pelo prefixo da gestão, passe por
`url_has_allowed_host_and_scheme` com o host do pedido, e não seja a própria identificação nem a
saída.

**Por quê**: `url_has_allowed_host_and_scheme` sozinho aceita qualquer caminho do mesmo host, e o
portal é o mesmo host — a pessoa sairia da gestão para o portal depois de se identificar na gestão.
O prefixo fecha isso. A exclusão das duas rotas evita o laço.

**Alternativa descartada**: guardar o destino na sessão. Não sobrevive a duas abas e esconde o
destino de quem lê o endereço.

## T-002 — Por que um auxiliar, e não middleware

Um middleware que trocasse toda resposta de redirecionamento para a identificação acharia as 90
portas de uma vez, mas faria isso por inspeção do `Location` — e a próxima porta que montasse o
redirecionamento de outro jeito escaparia em silêncio. O auxiliar é explícito na porta, e a troca é
mecânica: `redirect(reverse("interface:identificar"))` por `identidade.pedir_identificacao(request)`.

## T-003 — Onde mora a folha das telas de acesso

O guardião `test_nenhuma_classe_citada_deixa_de_existir_na_folha` soma à folha da gestão o bloco
`estilo_da_pagina` de cada template, resolvendo `include` de dentro dele. As três telas de acesso
incluem `_estilo_do_acesso.html` nesse bloco, e o guardião continua cobrindo-as — em vez de mover
os templates para uma subpasta que ele não lê.

## T-004 — A descrição dos papéis num mapa à parte

`PAPEIS` é desestruturado como par (`for papel, (_, permissoes) in PAPEIS.items()`) em cinco
testes de autorização. Um terceiro elemento na tupla quebraria os cinco por uma razão que não é
deles. `DESCRICOES`, no mesmo módulo e com as mesmas chaves, cumpre `D-004` sem tocar o par.

## T-005 — A origem da sessão

`identificar` grava `"origem": "demonstracao"`. `ator_da_sessao` recusa — e apaga — a identidade
de origem demonstração, ou sem origem, quando o seletor está desligado. Apagar é o que impede a
sessão de voltar a valer se a chave for religada sem nova escolha.

## T-006 — A busca

Um campo `search` filtra as linhas por um atributo de texto. O script é inline no template, como o
da Mesa: menos de quarenta linhas, sem biblioteca, e a lista inteira continua enviando sem ele. As
setas não entram: na lista do conceito A cada linha é um botão, e a tabulação já os percorre.
