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

## O que a implementação encontrou

- **A tela do marco removido devolvia 404 quando o marco cortava** (US2, T020). `ordenacao` passa o
  marco **histórico** a `_corte_do_marco`, que resolvia o Perfil pela norma vigente — onde o marco
  removido já não existe. A tela do ato histórico (`015`, `E2E15-010`) quebrava justamente para o
  marco com regra de corte, e nenhuma fixture o exercitava, porque nenhuma declarava corte. A `046`
  torna o corte obrigatório em todo Perfil, e com isso o caso comum: corrigido em
  `interface/views.py::_corte_do_marco` — marco fora da norma vigente não tem faixa vigente a
  mostrar —, e `tests/interface/test_marco_removido.py` passou a prendê-lo, com o marco agora
  cortando.
- **As fontes de Perfil sem corte eram mais que as quatro fixtures do `R-7`**: além de
  `divulgacao.py` e `sorteio.py`, sete arquivos de teste declaram o marco no próprio corpo
  (`test_calculo`, `test_imutabilidade_do_ato`, `test_calculo_vigencia`, `test_marco_na_retificacao`,
  `authorization/test_classificacao`, `performance/test_ordenacao`, `acceptance/test_ordenacao`) e
  `unit/editais/test_marco_classificatorio`. `selecao.py` e `supervisao.py`, que o `R-7` suspeitava,
  já usavam `marco_minimo`, que corta. O ajudante `corte_que_nao_governa` (em
  `tests/fixtures/edital.py`) é a fonte única dessa regra nas fixtures.
- **Cinco casos exercitam a ausência de propósito**, e publicam como acervo: o marco de sorteio sem
  corte e o marco sem regra de `test_corte.py`, o cenário sem regra de `test_ocupacao.py`, a emissão
  recusada de `test_emissao_do_corte.py` e a não regressão da `FR-214` em
  `test_progressao_com_corte.py`.

## Os percursos (T040)

*Preenchido no fecho.*
