# Data Model: A organização da lista de Processos Seletivos

**Nenhuma entidade, tabela, coluna ou migration nova.** O que segue são as leituras e os valores de
apresentação que a página monta.

## Leituras

| O quê | De onde | Para quê |
|---|---|---|
| Processo Seletivo: `id`, `title`, `institutional_code`, `status`, `created_at`, `institution_scope` | `ProcessoSeletivo` | a linha do Processo; o grupo; a ordem |
| Edital: `id`, `processo_id`, `number`, `year`, `title`, `status` | `Edital`, da unidade inteira | a faixa (FR-4323) e as linhas da página |
| Retificações em curso | `atos_retificacao.em_curso_por_edital` | a marca na linha (FR-4318) e a faixa |
| Unidade: `nome` | `unidades.Unidade`, pelo código do escopo | o subtítulo (FR-4322) |
| Vínculos com comissão | `comissao_selectors.comissoes_da_pessoa` | o selo e "pode gerir", como hoje |

## Valores derivados (não persistidos)

### Grupo do Processo (R-1)

| Grupo | Regra |
|---|---|
| `ANDAMENTO` (0) | situação fora de Encerrado e Cancelado, **ou** algum Edital fora de Encerrado e Cancelado |
| `ENCERRADOS` (1) | situação Encerrado e todos os Editais encerrados ou cancelados (ou nenhum Edital) |
| `CANCELADOS` (2) | situação Cancelado nas mesmas condições |

Cada Processo tem exatamente um grupo (FR-4302). "Todos" é a união.

### Recorte (parâmetros do endereço)

| Campo | Valores | Inválido ou ausente |
|---|---|---|
| `situacao` | `andamento`, `encerrados`, `cancelados`, `todos` | `andamento` |
| `busca` | texto, sem espaços nas pontas, até 100 caracteres | vazio = sem busca |
| `pagina` | inteiro ≥ 1 | 1; acima da última, a última |

Com `busca`, a `situacao` não vale e nenhuma aba é a atual.

### Página

`numero`, `total_de_paginas`, `inicio`, `fim` (1-based, para "mostrando 1–20"), `anterior`, `seguinte`;
`POR_PAGINA = 20`.

### Contagens

`abas`: Processos por grupo na unidade, mais "Todos". `busca`: total encontrado e quantos estão nos
grupos encerrado ou cancelado. Uma agregação (R-3).
