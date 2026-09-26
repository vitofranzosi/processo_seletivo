# O "antes" da 047 (T002)

Medido em 26/09/2026, na branch `claude/047-situacao-publica-implementacao`, sobre a `main` em
`064228c` (merge da `046`, #188), com o banco próprio da worktree (`ps047`). **Nenhuma edição de
código antes desta medição.**

## A suíte

`make test-pg`: **7965 passaram, 11 pulados**, em 746,76 s.

## Casos por arquivo que a `R-8` nomeia

| Arquivo | Casos |
|---|---:|
| `tests/integration/portal/test_cronograma_publico.py` | 8 |
| `tests/integration/portal/test_acompanhamento.py` | 8 |
| `tests/interface/test_acessibilidade_do_portal.py` | 105 |
| `tests/integration/supervisao/test_pulso.py` | 15 |
| `tests/interface/test_supervisao.py` | 24 |
| `tests/portal/test_resultado_publico.py` | 13 |
| `tests/portal/test_sorteio_na_pagina_do_edital.py` | 6 |
| `tests/integration/portal/test_historico_publico.py` | 7 |
| `tests/integration/portal/test_leitura_sem_escrita.py` | 3 |

## As consultas medidas hoje

- `test_resultado_publico.py:205`: a página do resultado não consulta nenhuma das quatro tabelas de
  `TABELAS_PROIBIDAS`, e uma delas é `publicacoes_versaoconsolidada`. **A US4 emenda essa lista**,
  só nessa tabela (`D-008`).
- `test_sorteio_na_pagina_do_edital.py:138`: a página da seleção faz **duas** consultas ao sorteio.

## O fato 1 da spec, reproduzido pela tela

`seed_demo` no `ps047`, servidor local na porta 8047.

1. A página pública do Edital 01/2026 (`/selecoes/cdcfd7b5-…/`), com as inscrições abertas, dizia:
   *"ABERTA · Inscrições abertas desde 26/09/2026, até 16/10/2026 às 18h34. Faltam 19 dias."*
2. Como Gestor, pela tela de gestão, **Cancelar**, com motivo. O banco confirma `status = CANCELADO`
   e o `AtoAdministrativo` `CANCELAR` às 18:36.
3. A vitrine deixou de listar o Edital, como deve.
4. **A página pública, no mesmo endereço, continuou dizendo exatamente o mesmo texto do passo 1**:
   *"ABERTA … Faltam 19 dias"*, sem nenhuma palavra sobre o cancelamento. Só o botão de inscrição
   sumiu.

É o comportamento que a US1 corrige (`FR-760`, `FR-761`), e a comparação final (T035) é contra este
registro.

## Casos que mudaram de expectativa (T010)

**Nenhum**, como a `R-8` previa. Os nove arquivos da tabela passaram sem edição de asserção depois da
US2. Só a docstring de `test_o_periodo_em_curso_e_acontecendo_agora_dos_dois_lados` mudou, porque
dizia que a régua do portal continuava própria.

**Um caso mudou de escopo na US3, e não de expectativa.**
`test_cronograma_publico.py::test_a_ordem_e_a_publicada_e_nao_a_cronologica` procurava as
descrições dos Eventos na página inteira. Com o cabeçalho dizendo o próximo Evento (`FR-767`), a
prova passou a aparecer ali antes da lista, e `corpo.index` achava o cabeçalho. O caso agora recorta
a seção do cronograma; a ordem que ele afirma é a mesma. A `R-8` não previu isso, porque mediu só
as asserções sobre classes do cronograma, e não as buscas por texto na página inteira.
