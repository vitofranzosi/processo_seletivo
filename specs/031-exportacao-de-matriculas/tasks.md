# Tasks: Exportação de matrículas

**Spec**: [spec.md](./spec.md) · **Plan**: [plan.md](./plan.md)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode correr em paralelo — arquivos distintos, sem dependência pendente
- **[Story]**: a que user story pertence (`US1` a `US4`)
- Caminho de arquivo exato em toda tarefa

## Path Conventions

Monólito Django. Código em `backend/processo_seletivo/`, testes em `backend/tests/`.

**O que esta feature acrescenta**: um app (`matriculas/`), **uma** tabela, uma permissão, uma
dependência e três campos em `requerimentos.RequerimentoDeMatricula`. **O que ela não acrescenta**:
nenhum estado novo, nenhuma etapa no assistente, nenhum acervo de arquivo.

**Banco próprio nesta worktree**: `DB_NAME=ps_demo_031`, e **como variável do Make** —
`make DB_NAME=ps_demo_031 …`, nunca `DB_NAME=ps_demo_031 make …`. O `Makefile` faz `include .env`
seguido de `export`, e `include` sobrepõe variável de ambiente.

**`TABELAS_APPEND_ONLY` muda, e este é o número.** `GeracaoDeArquivo` é registro de ato e entra na
tupla de `seguranca/papeis.py` na mesma leva da migration. O provisionamento passa a dizer
**`32 de 32`** — e o primeiro número vindo `0` continua sendo a armadilha, não o total.

**`make test-pg`, sempre.** A recusa por privilégio e a trigger de append-only não são exercidas no
modo padrão da suíte.

---

## Phase 0: O bloqueio externo

- [ ] **T001** Obter do Registro Acadêmico a resposta de `Q-1`: o importador aceita célula vazia em
  `COD_CURSO`, `COD_TURNO`, `COD_POLO` e `COD_NACIONALIDADE`? Enviar **duas linhas sintéticas** —
  nunca a linha `2` da amostra (`D-006`) — e registrar a resposta na spec
- [ ] **T002** Na mesma conversa, perguntar `Q-3` (o importador aceita protocolo opaco
  `INS-2026-K7M4Q2PX`?) e `Q-2` (`CLASSIF_CURSO_FINAL` é classificação ou numeração de linha?), e
  confirmar `R-1`: o que o destino espera para quem declarou cor **indígena**
- [ ] **T003** Registrar as respostas em [spec.md](./spec.md) §15 e mover o **Status** de *bloqueada*
  para *pronta*. **Nenhuma tarefa abaixo começa antes desta**

## Phase 1: Setup

- [ ] **T004** Acrescentar `openpyxl` a `backend/pyproject.toml` e rodar `uv sync --extra dev`,
  registrando a razão no cabeçalho de `infrastructure/planilha.py` (plan.md, *Complexity Tracking*)
- [ ] **T005** Criar o app `backend/processo_seletivo/matriculas/` — `__init__.py`, `apps.py`,
  `domain/nomes.py` — e registrá-lo em `INSTALLED_APPS`

## Phase 2: Foundational (Blocking Prerequisites)

- [ ] **T006** `[US1]` Acrescentar `titulo_eleitoral`, `zona_eleitoral` e `secao_eleitoral` a
  `backend/processo_seletivo/requerimentos/models.py`, guardados **sem pontuação** como o CEP já é,
  e a migration `requerimentos/0005_campos_eleitorais.py` (`D-007`)
- [ ] **T007** `[US1]` Estender `requerimentos/domain/declaracao.py` com o saneamento dos três —
  dígitos apenas, comprimentos 12/3/4, e a recusa **sem repetir o valor rejeitado** (`FR-401` da
  `029`)
- [ ] **T008** `[US1]` Rótulos e descritores dos três campos em `requerimentos/domain/rotulos.py` e
  `portal/requerimento.py`, no grupo *Documento de identidade* — e conferir que o ENTER continua
  percorrendo a ordem certa
- [ ] **T009** `[P]` Criar `matriculas/models.py::GeracaoDeArquivo` — Edital, população, quantidade,
  autor, instante, versão dos mapeamentos — e `migrations/0001_geracao.py` (`FR-447`)
- [ ] **T010** Acrescentar a tabela a `seguranca/papeis.py::TABELAS_APPEND_ONLY` **na mesma leva**, e
  confirmar que `make provisionar` diz `32 de 32`
- [ ] **T011** `[P]` Criar a permissão `matricula:exportar` no catálogo de permissões, sem concedê-la
  a papel nenhum por padrão (Princípio *negar por padrão*)

## Phase 3: User Story 1 — O arquivo de um Edital, sem redigitar nada (P1)

- [ ] **T012** `[P]` `[US1]` `matriculas/domain/flexao.py`: a tabela de 8 strings da `D-004`, com
  teste unitário que percorre os 4 estados × 2 sexos (`FR-442`)
- [ ] **T013** `[US1]` `matriculas/domain/colunas.py`: as **34** colunas, cada uma com nome exato do
  cabeçalho, origem, serializador e comportamento na ausência (`FR-445`). Uma função por coluna —
  **nunca** `legivel()` genérico
- [ ] **T014** `[P]` `[US1]` Teste unitário por coluna em `backend/tests/unit/matriculas/`, cobrindo
  o caso normal e o vazio. É a fase em que o erro silencioso morre
- [ ] **T015** `[US1]` `COD_FORMA_INGRESSO`: ausência de Modalidade → `AC`; com Modalidade → o `code`
  publicado, sem reescrita (`FR-443`, `D-003`)
- [ ] **T016** `[US1]` `RENDA_PER_CAPITA_PNP` recebe `renda_familiar_faixa` sem conversão (`D-002`),
  e o serializador **cita a decisão no docstring** — é a coluna que alguém vai tentar "consertar"
- [ ] **T017** `[P]` `[US1]` `TITULO_ELE`, `ZONA_ELE`, `SECAO_ELE` na forma do destino, com zeros à
  esquerda (`FR-451`)
- [ ] **T018** `[US1]` `matriculas/infrastructure/planilha.py`: `.xlsx` de uma aba
  `Import_ModeloCefor`, 34 cabeçalhos em `A1:AH1` na grafia exata — `ENDEREÇO` e `NÚMERO` acentuados
  —, dados a partir da linha 2, **tudo com formato `@`** (`FR-436`, `FR-437`)
- [ ] **T019** `[US1]` Teste de ida e volta: CPF com zero à esquerda, data e CEP sobrevivem à leitura
  do arquivo gerado (`SC-144`)
- [ ] **T020** `[US1]` `matriculas/application/populacao.py`: a população explícita, só *enviados*
  (`FR-433`, `FR-434`)
- [ ] **T021** `[US1]` `matriculas/application/exportar.py`: permissão, montagem, ordem
  determinística, registro da geração

## Phase 4: User Story 2 — O que saiu vazio, dito antes de alguém perguntar (P1)

- [ ] **T022** `[US2]` `matriculas/domain/lacuna.py`: cada lacuna com coluna, razão e quantidade
  (`FR-439`)
- [ ] **T023** `[US2]` O aviso **obrigatório** da coluna 31 em toda geração, inclusive nas sem outra
  lacuna (`FR-452`, `SC-153`)
- [ ] **T024** `[US2]` A lacuna nominal de `COR` para quem declarou **indígena** (`FR-440`,
  `SC-146`) — caso de teste próprio, e não efeito colateral
- [ ] **T025** `[US2]` A tela mostra o resumo das lacunas **antes** do download (`UX-060`)

## Phase 5: User Story 3 — A geração que se recusa a mentir (P1)

- [ ] **T026** `[US3]` Recusa quando alguém da população não tem requerimento enviado, nomeando quem
  falta (`FR-435`, `SC-149`)
- [ ] **T027** `[US3]` Recusa quando o `code` da Modalidade é desconhecido, nomeando código e Edital
  (`FR-441`, `SC-147`)
- [ ] **T028** `[US3]` A recusa diz o que falta e de quem (`UX-061`), e **a aplicação recusa mesmo
  quando a tela não oferece** — Princípio IV
- [ ] **T029** `[US3]` Recusa sem `matricula:exportar`, verificada por acesso direto ao endereço
  (`SC-150`)

## Phase 6: User Story 4 — O mesmo arquivo, duas vezes (P2)

- [ ] **T030** `[US4]` Ordem determinística e comparação célula a célula de duas gerações seguidas
  (`FR-446`, `SC-148`)
- [ ] **T031** `[US4]` Requerimento sucedido entre gerações: o arquivo traz o **vigente**, e o
  registro guarda qual era

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] **T032** `[P]` `contracts/arquivo-de-importacao.md`: as 34 colunas com o serializador nomeado,
  e a `D-001` substituindo a citação errada de `Q-3` no
  [contrato de saída da `029`](../029-requerimento-de-matricula/contrato-de-saida.md) (spec §17)
- [ ] **T033** `[P]` `quickstart.md` com um cenário por FR
- [ ] **T034** `[P]` Conferir que **nenhum** app importa `matriculas` — é a verificação de que a
  feature continua sendo ponta de leitura (plan.md, *Project Structure*)
- [ ] **T035** `[P]` Confirmar que a varredura `tests/test_sem_dado_pessoal_da_amostra.py` alcança
  os arquivos novos por `glob` (`SC-151`, `D-006`)
- [ ] **T036** Semear em `seed_demo.py` um Edital com convocados de requerimento enviado, incluindo
  **um que declarou cor indígena** — o caso do `R-1` precisa existir para ser visto
- [ ] **T037** `make lint check test-pg` verde, e `make provisionar` dizendo `32 de 32`
- [ ] **T038** **`SC-143`: gerar e importar de verdade no ambiente do Registro Acadêmico.** É o único
  critério que não se verifica neste repositório, e é o que decide se a feature funciona

## Dependencies

- **T001–T003 bloqueiam tudo.** Não é formalidade: a forma do arquivo depende da resposta
- T006–T008 (campos eleitorais) antes de T017
- T013 antes de T014, T018 e T022 — as colunas são o centro
- T009–T010 juntas: tabela e privilégio na mesma leva, ou o provisionamento reporta errado
- T038 por último, e fora deste repositório

## Parallel Execution

`[P]` em T009/T011, T012, T014, T017, T032–T035. O resto é sequencial porque passa por
`colunas.py`.

## Implementation Strategy

**MVP é US1 + US2, e as duas juntas.** Gerar o arquivo sem o relatório de lacunas entregaria
exatamente o problema que a feature existe para resolver: alguém recebe uma planilha com células
vazias e as preenche do jeito que acha. US3 vem logo atrás porque a recusa é o que separa esta
feature de uma planilha feita à mão; US4 é garantia de operação e pode esperar.
