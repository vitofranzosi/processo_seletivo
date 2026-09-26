# O "antes" — medido em 26/09/2026, sobre a `main` em `ee894ab` (a `045` mesclada)

## A suíte

`make test-pg`, com o protótipo que **registra sem bloquear** ligado (`research.md`, `R-7`): **7882
passaram, 11 pulados, zero falhas**, em 12m11s. O protótipo só acrescenta avisos com código próprio, e
nenhum caso afirma a lista exata de avisos de um conteúdo — de modo que o total é o da `main`. O
protótipo foi revertido antes de qualquer edição (`git checkout` dos dois arquivos).

## As causas, refeitas

| Causa | Casos | Arquivos | Em 26/09 sobre `aeb575a` (`R-7`) |
|---|---|---|---|
| Perfil sem marco que corte | 767 (578 só por ela) | 104 | 759 (571) · 104 |
| Etapa eliminatória, pontuada, sem nota mínima | 612 | 97 | 608 · 96 |
| Etapa eliminatória com duas avaliações | 210 | 30 | 210 · 30 |
| Etapa enumerada com duas avaliações | 68 | 3 | 68 · 3 |
| **Total de casos distintos** | **1468** | **192** | 1457 · 191 |

A diferença é a `045` e o #189, que trouxeram casos novos sobre as mesmas fixtures. Nenhuma causa nova.

## Os arquivos que esta feature reescreve, contados caso a caso (`pytest --co`)

| Arquivo | Casos |
|---|---|
| `tests/unit/editais/test_executabilidade.py` | 23 |
| `tests/interface/test_hardening_pos_auditoria.py` | 61 |
| `tests/interface/test_ocupacao.py` | 26 |
| `tests/integration/resultados/test_prontidao.py` | 6 |
| `tests/unit/resultados/test_regra.py` | 15 |
| `tests/unit/editais/test_etapas.py` | 19 |
| `tests/interface/test_compor.py` | 51 |
| `tests/integration/portal/test_cronograma_publico.py` | 8 |
| `tests/interface/test_conducao_dos_bloqueios.py` | 13 |

## O que a leitura da `045` mesclada mudou no plano

A `FR-739` da `045` **exige** o aviso da Etapa sem Evento na página do Edital publicado (`UX-086`), e a
convergência de 20/09 (§21) vetou silenciá-lo. O `R-8` o tratava como uma cláusula de teste — era
requisito. Levado ao usuário em 26/09, que escolheu *"fatos ficam, gate sai"*: ver `D-003` na spec,
a `FR-755` e o `R-5`.

## Os percursos (T040)

*Preenchido no fecho.*
