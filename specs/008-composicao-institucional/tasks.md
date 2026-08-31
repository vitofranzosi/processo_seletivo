# Tasks: Composição Institucional do Edital

**Input**: Design documents from `/specs/008-composicao-institucional/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/composicao.md](./contracts/composicao.md), [quickstart.md](./quickstart.md)

**Tests**: **sim, exigidos**. A Constituição (princípio V) exige cobertura de regra crítica, e a spec
exige testes de propriedade semântica ao lado da demonstração visual. Os testes vêm antes da
implementação em cada história.

**Organization**: por história de usuário, na ordem de entrega da spec.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência)
- **[Story]**: US1 a US5, conforme a spec

## Path Conventions

Aplicação web Django. A feature vive quase inteira em
`backend/processo_seletivo/publicacoes/infrastructure/pdf.py`.

> **⚠️ Sobre `[P]` nesta feature.** Quase toda tarefa de implementação toca **o mesmo arquivo**, e
> por isso **não** é paralelizável. Os `[P]` estão concentrados nos testes e nas fixtures, que vivem
> em arquivos distintos. Marcar implementação como paralela aqui produziria conflito garantido — a
> escassez de `[P]` é a realidade desta feature, não um descuido do plano.

---

## Phase 1: Setup

**Purpose**: ter contra o que comparar. Concluída durante o planejamento.

- [x] T001 Versionar o estado inicial em `specs/008-composicao-institucional/referencias/estado-inicial-apos-007.pdf`
- [x] T002 Versionar os alvos em `specs/008-composicao-institucional/referencias/alvo-edital-62-2026.pdf` e `alvo-edital-73-2026.pdf`
- [x] T003 Registrar as características observáveis dos alvos e as três diferenças aceitas na seção `### Referências visuais` de `specs/008-composicao-institucional/spec.md`

**Checkpoint**: a rubrica de inspeção tem alvo. A entrega 1 está desbloqueada.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: o que toda história precisa e nenhuma pode construir sozinha.

**⚠️ CRITICAL**: nenhuma história começa antes desta fase.

- [X] T004 Classificar cada teste de `backend/tests/unit/publicacoes/test_pdf.py` e `backend/tests/contract/test_documento_publicado.py` como **invariante** ou **forma da apresentação**, registrando a classificação em comentário no topo de cada arquivo, conforme D-010 de `specs/008-composicao-institucional/research.md`
- [X] T005 Escrever, **antes** de T006, o teste de equivalência entre prévia e publicado em `backend/tests/contract/test_documento_publicado.py`, afirmando as três coisas: (a) o corpo normativo e o conjunto de suas quebras são iguais nos dois modos para o mesmo snapshot; (b) removidas as diferenças permitidas — marca de prévia, bloco de autoridade e bloco de verificação —, as composições são equivalentes; (c) a mudança da marca **não altera os bytes do documento publicado**, comparando com a fixture vigente **sem regenerá-la** (FR-041, FR-042)
- [X] T006 Tirar a marca de prévia do fluxo normativo em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` e emiti-la em região fixa, junto do rodapé, em todas as páginas, com T005 passando a verde (D-011, FR-042)
- [X] T007 [P] Criar o cenário **sem Etapas de Avaliação** em `backend/tests/unit/publicacoes/test_pdf.py`, para provar numeração sem lacuna (FR-011)
- [X] T008 [P] Criar o cenário **de dois Perfis**, dimensionado para o segundo não caber no espaço restante da primeira página, em `backend/tests/unit/publicacoes/test_pdf.py` (FR-020)
- [X] T009 [P] Criar o cenário **extremo** — Perfil cujas atribuições passam de uma página inteira — em `backend/tests/unit/publicacoes/test_pdf.py` (FR-021)

**Checkpoint**: a suíte sabe o que é invariante, a prévia deixa de deslocar o conteúdo e os três
cenários de demonstração existem.

---

## Phase 3: User Story 1 - O documento se identifica como ato institucional (Priority: P1) 🎯 MVP

**Goal**: cabeçalho institucional, hierarquia do ato e seções numeradas. Carrega a métrica de
largura, que as histórias seguintes consomem.

**Independent Test**: gerar a prévia do cenário-base e conferir R-01 a R-03 contra
`referencias/alvo-edital-62-2026.pdf`; gerar o cenário sem Etapas e conferir que a numeração não tem
lacuna.

### Tests for User Story 1

- [ ] T010 [P] [US1] Teste da métrica em `backend/tests/unit/publicacoes/test_pdf.py`: larguras de referência de glifos conhecidos e a linha mais larga do cenário-base não ultrapassa a margem (FR-002)
- [ ] T011 [P] [US1] Teste do cabeçalho em `backend/tests/unit/publicacoes/test_pdf.py`: órgão, instituição e unidade centralizados em corpo menor que o texto; ato em negrito e caixa alta; ordem antes de qualquer conteúdo normativo (FR-005, FR-006, SC-001)
- [ ] T012 [P] [US1] Teste de numeração contínua sobre o cenário sem Etapas em `backend/tests/unit/publicacoes/test_pdf.py` (FR-010, FR-011)
- [ ] T013 [P] [US1] Teste de numeração de subseção em `backend/tests/unit/publicacoes/test_pdf.py`: as Etapas aparecem como `6.1`, `6.2`, derivadas do número da seção-mãe **já resolvido após a filtragem**, e num Edital em que a seção-mãe mude de número as subseções acompanham (FR-013)
- [ ] T014 [P] [US1] Teste de que o número não está no conteúdo da seção em `backend/tests/unit/publicacoes/test_pdf.py` (FR-012)

### Implementation for User Story 1

- [ ] T015 [US1] Acrescentar a tabela de larguras indexada por byte cp1252 para Helvetica e Helvetica-Bold em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` (D-001)
- [ ] T016 [US1] Implementar a função de largura de cadeia e o atributo de alinhamento — esquerda, centro, direita — no item de composição de `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` (D-001)
- [ ] T017 [US1] Substituir a contagem de caracteres de `_quebrar` pela largura real e remover `FATOR_LARGURA` de `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` (FR-032)
- [ ] T018 [US1] Reescrever `_cabecalho` em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`: `MINISTÉRIO DA EDUCAÇÃO`, `INSTITUTO FEDERAL DO ESPÍRITO SANTO` e a unidade, centralizados; ato em negrito, caixa alta e centralizado; Processo e título (FR-005 a FR-007, D-008)
- [ ] T019 [US1] Definir os seis níveis tipográficos como constantes nomeadas em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` e aplicá-los, substituindo os tamanhos literais espalhados (FR-009)
- [ ] T020 [US1] Reescrever `_secoes` em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` em dois passos — selecionar as seções que serão materializadas, depois enumerar (FR-010 a FR-012, D-006)
- [ ] T021 [US1] Numerar as Etapas a partir do número da seção-mãe já resolvido em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` (FR-013)
- [ ] T022 [US1] Regenerar `backend/tests/contract/fixtures/documento_publicado_v1.pdf` com `backend/scripts/gerar_fixture_documento.py` e revisar o diff do documento no mesmo commit (FR-044)
- [ ] T023 [US1] Gerar a prévia pela interface administrativa e conferir R-01, R-02 e R-03 da rubrica contra os alvos, conforme `specs/008-composicao-institucional/quickstart.md`

**Checkpoint**: a primeira página mudou visivelmente e as seções estão numeradas. **Este é o MVP.**

---

## Phase 4: User Story 2 - O Perfil de Vaga se lê como quadro de vaga (Priority: P1)

**Goal**: Perfis em quadro delimitado e paginação que não parte Perfil pequeno. Carrega as
primitivas gráficas e a paginação por bloco.

**Independent Test**: gerar o cenário de dois Perfis e verificar que o segundo passa inteiro para a
página seguinte; gerar o cenário extremo e verificar que a composição conclui quebrando dentro do
sub-bloco.

**Depende de**: US1 — a identificação tabular e a moldura usam a métrica de T015/T016.

### Tests for User Story 2

- [ ] T024 [P] [US2] Teste do cenário de dois Perfis em `backend/tests/unit/publicacoes/test_pdf.py`: o segundo Perfil não começa no fim da página 1 (FR-020)
- [ ] T025 [P] [US2] Teste do cenário extremo em `backend/tests/unit/publicacoes/test_pdf.py`: a composição conclui e a quebra ocorre dentro do sub-bloco, por parágrafo (FR-021)
- [ ] T026 [P] [US2] Teste de que nenhum título de Perfil fica isolado no fim de página em `backend/tests/unit/publicacoes/test_pdf.py` (FR-022)
- [ ] T027 [P] [US2] Teste do quadro de modalidades em `backend/tests/unit/publicacoes/test_pdf.py`: sem percentual não inventa célula, e versão e vigência da Regra Normativa continuam no documento (FR-018, FR-019)
- [ ] T028 [P] [US2] Testes dos seis modos de falha silenciosa da tabela de interações de D-004, em `backend/tests/unit/publicacoes/test_pdf.py`

### Implementation for User Story 2

- [ ] T029 [US2] Transformar o item de composição em união marcada `Texto | Traço` e fazer `_fluxo_da_pagina` emitir os traços antes dos textos em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` (D-002, FR-003)
- [ ] T030 [US2] Acrescentar abertura e fechamento de bloco à `Composicao` em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`, com os três níveis da cascata (D-004)
- [ ] T031 [US2] Reescrever `Composicao.paginar` em duas passadas — medir o bloco, decidir, colocar — implementando os cinco degraus da cascata em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` (FR-004, FR-020 a FR-022, D-004)
- [ ] T032 [US2] Resolver a moldura após a paginação, uma por página de continuação, em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` (D-003, FR-014)
- [ ] T033 [US2] Reescrever `_perfis` em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`: bloco com moldura, identificação tabular, descrição e atribuições como sub-blocos, requisitos em lista (FR-014 a FR-017)
- [ ] T034 [US2] Reescrever `_modalidades` em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` como tabela com modalidade, percentual, fundamento, versão e vigência, eliminando a frase `Regra Normativa — fundamento: …` (FR-018, FR-019)
- [ ] T035 [US2] Regenerar a fixture e revisar o diff no mesmo commit (FR-044)
- [ ] T036 [US2] Gerar a prévia e conferir R-04, R-05 e R-06 da rubrica

**Checkpoint**: Perfis em quadro, sem quebra ruim. US1 e US2 funcionam juntas.

---

## Phase 5: User Story 3 - Cronograma e Etapas se leem como informação estruturada (Priority: P1)

**Goal**: Cronograma em tabela com cabeçalho repetido, Etapas em pares rótulo-valor.

**Independent Test**: gerar o cenário-base e conferir que os Eventos estão em tabela com colunas
alinhadas, que o Evento pontual não exibe término e que a Etapa não traz a frase corrida.

**Depende de**: US1 (métrica) e US2 (primitivas e blocos).

### Tests for User Story 3

- [ ] T037 [P] [US3] Teste do Cronograma em tabela com colunas alinhadas em `backend/tests/unit/publicacoes/test_pdf.py` (FR-023)
- [ ] T038 [P] [US3] Teste de Evento pontual sem término em `backend/tests/unit/publicacoes/test_pdf.py` (FR-024)
- [ ] T039 [P] [US3] Teste de cabeçalho de tabela repetido na continuação e nunca isolado no fim da página em `backend/tests/unit/publicacoes/test_pdf.py` (FR-026)
- [ ] T040 [P] [US3] Reescrever `test_etapas_aparecem_com_caracter_peso_e_nota_minima` em `backend/tests/unit/publicacoes/test_pdf.py` para afirmar pares rótulo-valor em vez da frase corrida (FR-027, D-010)

### Implementation for User Story 3

- [ ] T041 [US3] Implementar o cálculo de largura de coluna — mínimo por coluna, folga na coluna de texto livre, célula que quebra em mais de uma linha — em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` (D-007)
- [ ] T042 [US3] Modelar a tabela como bloco cujas unidades internas são linhas, com o cabeçalho marcado para repetição, em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` (FR-026)
- [ ] T043 [US3] Reescrever `_cronograma` como tabela com ordem, evento, início e término em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` (FR-023 a FR-025)
- [ ] T044 [US3] Reescrever `_etapas` em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` com pares rótulo-valor alinhados, mantendo a data derivada do Evento vinculado (FR-027, FR-028)
- [ ] T045 [US3] Regenerar a fixture e revisar o diff no mesmo commit (FR-044)
- [ ] T046 [US3] Gerar a prévia e conferir R-07 a R-10 da rubrica

**Checkpoint**: as três seções geradas estão estruturadas.

---

## Phase 6: User Story 4 - O documento se lê sem acidentes editoriais (Priority: P2)

**Goal**: órfãos, espaçamento semântico e corpo de texto refinados.

**Independent Test**: percorrer todas as páginas do cenário longo procurando título sozinho no pé de
página e espaço vertical sem causa.

**Depende de**: US2 (blocos).

### Tests for User Story 4

- [ ] T047 [P] [US4] Teste de que nenhum título — de seção, Perfil ou Etapa — fecha página sem conteúdo abaixo, em `backend/tests/unit/publicacoes/test_pdf.py` (FR-030, SC-008)
- [ ] T048 [P] [US4] Teste ordinal do espaçamento — antes de seção > antes de bloco > antes de parágrafo — em `backend/tests/unit/publicacoes/test_pdf.py` (FR-031, SC-008)
- [ ] T049 [P] [US4] Teste de que nenhuma linha ultrapassa a margem em nenhuma página do cenário longo, em `backend/tests/unit/publicacoes/test_pdf.py` (FR-029)
- [ ] T050 [P] [US4] Teste de que o conjunto de quebras do corpo normativo é idêntico entre prévia e publicado, em `backend/tests/contract/test_documento_publicado.py` (FR-042)

### Implementation for User Story 4

- [ ] T051 [US4] Aplicar keep-together de título com a primeira parte do conteúdo em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` (FR-030)
- [ ] T052 [US4] Definir a escala de espaçamento semântico como constantes nomeadas e aplicá-la em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` (FR-031)
- [ ] T053 [US4] Ajustar largura de linha, entrelinha e distância entre parágrafos do corpo normativo em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` (FR-029)
- [ ] T054 [US4] Regenerar a fixture e revisar o diff no mesmo commit (FR-044)
- [ ] T055 [US4] Gerar a prévia do cenário longo e conferir R-06 e R-11 em **todas** as páginas

**Checkpoint**: o documento está composto, não apenas estruturado.

---

## Phase 7: User Story 5 - O documento termina como ato, não como relatório (Priority: P1)

**Goal**: autoridade signatária no publicado, integridade discreta ao final, prévia sem nenhuma das
duas.

**Independent Test**: publicar escolhendo a autoridade e conferir que ela aparece ao final; gerar a
prévia do mesmo Edital e conferir que não aparece; tentar compor publicado sem autoridade e obter
recusa.

**Depende de**: nada estruturalmente — poderia ser feita antes das outras. Vem por último porque
depende do resto estar composto para o fechamento ter onde ficar.

### Tests for User Story 5

- [ ] T056 [P] [US5] Teste de que compor em modo publicado sem autoridade é recusado, em `backend/tests/contract/test_documento_publicado.py` (FR-035)
- [ ] T057 [P] [US5] Teste de que oferecer autoridade em modo prévia é recusado, em `backend/tests/contract/test_documento_publicado.py` (FR-035)
- [ ] T058 [P] [US5] Teste do bloco de autoridade — nome e cargo da Publicação, sem praça e sem data — em `backend/tests/unit/publicacoes/test_pdf.py` (FR-033, FR-036)
- [ ] T059 [P] [US5] Teste do bloco de verificação — após a autoridade, sem `Versão do schema` no corpo, com SHA-256 completo e abreviado no rodapé — em `backend/tests/unit/publicacoes/test_pdf.py` (FR-038 a FR-040)
- [ ] T060 [P] [US5] Teste de determinismo com a mesma autoridade e de que o corpo normativo continua composto sem consulta ao banco, em `backend/tests/unit/publicacoes/test_pdf.py` (SC-013)

### Implementation for User Story 5

- [ ] T061 [US5] Criar o valor congelado `AutoridadeSignataria` com nome e cargo, e a validação de presença por modo, em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` (D-005, FR-034, FR-035)
- [ ] T062 [US5] Compor o bloco de autoridade após o conteúdo normativo em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` (FR-033)
- [ ] T063 [US5] Reescrever `_integridade` em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`: bloco discreto após a autoridade, sem `Versão do schema` no corpo normativo (FR-038 a FR-040)
- [ ] T064 [US5] Passar a autoridade ao compositor em `backend/processo_seletivo/publicacoes/application/publish_edital.py`, a partir do `signatory` já resolvido
- [ ] T065 [US5] Passar a autoridade ao compositor em `backend/processo_seletivo/publicacoes/application/retificacoes.py`, a partir do `signatory` da Publicação da Retificação (FR-043)
- [ ] T066 [US5] Criar `backend/tests/contract/fixtures/autoridade_publicada.json` e fazer `backend/scripts/gerar_fixture_documento.py` usá-la (D-009, FR-044)
- [ ] T067 [US5] Regenerar a fixture e revisar o diff no mesmo commit (FR-044)
- [ ] T068 [US5] Publicar um Edital e uma Retificação pela interface administrativa e conferir R-12, R-13 e R-14, e que o documento consolidado tem a mesma composição (FR-043)

**Checkpoint**: o documento termina como ato administrativo.

---

## Phase 8: Polish & Cross-Cutting Concerns

- [ ] T069 Conferir a rubrica de catorze itens inteira sobre o cenário-base, o cenário longo e o cenário sem Etapas, comparando com os dois alvos
- [ ] T070 Percorrer a `## Matriz de rastreabilidade SC → verificação` deste arquivo e confirmar que cada um dos quinze SC tem sua verificação executada e verde
- [ ] T071 Confirmar que **todos** os invariantes de não regressão da spec seguem verdes — determinismo, acentuação, ausência de UUID, suficiência do snapshot, prévia sem integridade, parágrafos preservados, rodapé, omissão de dado inexistente
- [ ] T072 Conferir nominalmente os requisitos de proibição, que só se verificam por ausência: FR-001 (nada do conteúdo publicado, da versão canônica, do hash ou do endereçamento foi alterado), FR-008 (nenhuma imagem embutida e nenhum recurso binário novo no documento), FR-037 (nenhum certificado, assinatura digital, QR code ou carimbo) e R-T1 do plano (nenhuma dependência de renderização introduzida)
- [ ] T073 Rodar a suíte completa com PostgreSQL e `ruff check`, conforme `specs/008-composicao-institucional/quickstart.md`
- [ ] T074 Registrar em `specs/008-composicao-institucional/quickstart.md` as diferenças remanescentes observadas contra os alvos, para que a próxima decisão sobre o documento parta de fato, não de memória

---

## Matriz de rastreabilidade SC → verificação

*Cada critério de sucesso da spec e onde ele é verificado. Os três últimos não são visuais e não
poderiam ser cobertos pela rubrica — é por isso que esta matriz existe e não basta acrescentar a
coluna SC à rubrica.*

| SC | Verificado por | Natureza |
|---|---|---|
| SC-001 | T011 + rubrica R-01, R-02 | teste e inspeção |
| SC-002 | T012 | teste |
| SC-003 | T014 | teste |
| SC-004 | T024 + rubrica R-04 | teste e inspeção |
| SC-005 | T024, T026 + rubrica R-05 | teste e inspeção |
| SC-006 | T037, T038, T039 + rubrica R-07, R-08, R-09 | teste e inspeção |
| SC-007 | T040 + rubrica R-10 | teste e inspeção |
| SC-008 | T047, T048 + rubrica R-06, R-11 | teste e inspeção |
| SC-009 | T058 + rubrica R-12 | teste e inspeção |
| SC-010 | T005, T057 + rubrica R-14 | teste e inspeção |
| SC-011 | T059 + rubrica R-13 | teste e inspeção |
| **SC-012** | **T072** — nenhuma alteração do conteúdo publicado, da versão canônica, do hash ou do endereçamento | conferência de ausência |
| **SC-013** | **T060** — determinismo com a mesma autoridade; corpo normativo sem consulta ao banco | teste |
| SC-014 | T068 | demonstração |
| **SC-015** | **T005(c), T022, T035, T045, T054, T067** — evidência refeita só junto de mudança intencional, e documentos publicados anteriores conservam seus bytes | disciplina de revisão |

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Fase 1)**: concluída
- **Foundational (Fase 2)**: bloqueia todas as histórias
- **US1 (Fase 3)**: depende da Fase 2 — **carrega a métrica**
- **US2 (Fase 4)**: depende de US1 — **carrega primitivas e blocos**
- **US3 (Fase 5)**: depende de US1 e US2
- **US4 (Fase 6)**: depende de US2
- **US5 (Fase 7)**: depende apenas da Fase 2
- **Polish (Fase 8)**: depende de todas

### Grafo real

```text
Fase 2 ──┬── US1 ── US2 ──┬── US3
         │                └── US4
         └── US5
```

**As histórias desta feature não são todas independentes, e fingir que são seria erro de plano.**
US2, US3 e US4 consomem capacidades que US1 e US2 entregam. A independência que existe é a de
**demonstração**: cada história termina num documento que se abre e se confere sozinho, que é o que
o princípio VI exige. **US5 é a única verdadeiramente independente** — pode ser antecipada se houver
razão para isso.

### Within Each User Story

- Testes primeiro, falhando, antes da implementação
- Capacidade antes do uso que a consome
- Regeneração da fixture **no mesmo commit** da mudança de composição
- Demonstração visual antes do checkpoint

### Parallel Opportunities

- T007, T008 e T009 (cenários) em paralelo
- Todos os testes de uma mesma história em paralelo entre si
- **Nenhuma tarefa de implementação é paralelizável**: todas tocam `pdf.py`

---

## Parallel Example: User Story 1

```bash
# Os quatro testes da US1 podem ser escritos em paralelo — arquivos e casos distintos:
Task: "T010 Teste da métrica em backend/tests/unit/publicacoes/test_pdf.py"
Task: "T011 Teste do cabeçalho em backend/tests/unit/publicacoes/test_pdf.py"
Task: "T012 Teste de numeração contínua em backend/tests/unit/publicacoes/test_pdf.py"
Task: "T013 Teste de numeração de subseção em backend/tests/unit/publicacoes/test_pdf.py"
Task: "T014 Teste de número ausente do conteúdo em backend/tests/unit/publicacoes/test_pdf.py"

# T015 a T022 são sequenciais: todas tocam pdf.py
```

---

## Implementation Strategy

### MVP (US1)

1. Fase 2 completa
2. Fase 3 completa
3. **Parar e validar**: gerar a prévia, conferir R-01 a R-03 contra os alvos
4. A primeira página mudou visivelmente — é a condição de merge da entrega 1

### Entrega incremental

Fase 2 → US1 (demonstra) → US2 (demonstra) → US3 (demonstra) → US4 (demonstra) → US5 (demonstra).
Cada uma gera o PDF e o inspeciona. **Nenhuma entrega é preparatória**: a métrica viaja dentro do
cabeçalho centralizado, as primitivas dentro do quadro de Perfil, os blocos dentro da paginação que
para de partir Perfil.

### Notes

- `[P]` = arquivos diferentes, sem dependência
- Commit a cada tarefa ou grupo lógico; a regeneração da fixture vai **no commit da mudança**
- Regenerar a fixture para fazer um teste passar continua sendo erro
- Um teste classificado como invariante em T004 que falhe indica entrega errada, não teste velho
