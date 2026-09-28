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

**Um caso mudou de expectativa na US5, por decisão da spec.**
`test_resultado_publico.py::test_a_vitrine_do_edital_anuncia_so_a_vigente` afirmava que o endereço da
publicação sucedida não aparecia na página do Edital. A `FR-772` e a `D-007` põem a sucedida na
página, recolhida sob a vigente e dita como sucedida. O caso passou a afirmar a intenção escrita na
docstring dele: a sucedida nunca aparece entre as vigentes, e aparece no histórico. A `R-8` não
previu esta mudança, porque não leu a `017` inteira. Leu só as asserções sobre o cronograma.

**As medições de consultas (T031) não mudaram.** `test_resultado_publico.py:205` continua passando
sem as três tabelas de dado individual (`D-008`), e `test_sorteio_na_pagina_do_edital.py:138`
continua em duas consultas ao sorteio. A página do resultado custa uma consulta por degrau da cadeia
para listar as anteriores, como a `R-7` previu, e a janela já subia a mesma cadeia para achar a âncora.

## O "depois" (T037)

`ruff check`, `ruff format --check` e `make check` verdes. `make test-pg`: **1 falha, 8042
passando, 11 pulados**, em 743,96 s. A falha era `tests/performance/test_resultado_publico.py::
test_a_pagina_custa_um_numero_pequeno_e_declarado_de_consultas`, que fixava em 3 as consultas da
página do resultado e pedia justificativa para a próxima. A quarta consulta é a versão consolidada
vigente, que dá o prazo de recurso (`D-008`). O teto passou a 4, com a justificativa no teste, e o
caso passou (4 de 4 no arquivo). Com isso, a suíte fica em **8043 passando e 11 pulados**: 78 casos
a mais que o "antes" (7965), nenhum pulado a mais.

Casos existentes que mudaram, todos registrados acima: a docstring de `test_o_periodo_em_curso…`
(US2), o recorte de `test_a_ordem_e_a_publicada…` (US3), `test_a_vitrine_do_edital_anuncia_so_a_vigente`
(US5), `TABELAS_PROIBIDAS` (US4, `D-008`) e o teto de consultas acima.
