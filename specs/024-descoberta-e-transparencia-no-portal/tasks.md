---

description: "Task list for feature implementation"
---

# Tasks: Descoberta e Transparência no Portal Público

**Input**: Design documents from `specs/024-descoberta-e-transparencia-no-portal/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/portal-publico.md](./contracts/portal-publico.md)

**Tests**: **obrigatórios**, e não opcionais. O Princípio V exige teste no nível certo, e a §9 da
spec fecha a feature em "os sete invariantes verificáveis por teste". Nenhuma feature anterior abriu
exceção; esta não abre.

**Organization**: por user story, para que cada faixa seja demonstrável sozinha.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode correr em paralelo — arquivos distintos, sem dependência pendente
- **[Story]**: a que user story a tarefa pertence (`US1` a `US5`)
- Caminho de arquivo exato em toda tarefa

## Path Conventions

Monólito Django. Código em `backend/processo_seletivo/`, testes em `backend/tests/`.

**Nenhum app novo, nenhum modelo, nenhuma migration** — `D-001`. Se alguma tarefa abaixo levar você
a escrever `models.py` ou `makemigrations`, a tarefa foi mal lida.

---

## Phase 1: Setup

**Purpose**: o lugar onde mora o que passa a servir duas telas.

- [X] T001 [P] Criar `backend/processo_seletivo/portal/leitura.py` com docstring declarando o que ele guarda: o que **duas** telas do portal leem, e o saneamento da consulta pública. *Módulo nomeado, e não função solta em `views.py`: a `T-003` existe porque duplicar a situação do Evento criaria duas verdades sobre "em curso"*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: o cronograma deixa de pertencer a uma tela só — sem quebrar a tela que já o tem.

**⚠️ CRÍTICO**: `US1` não começa antes deste checkpoint. E este é o ponto da feature com maior risco
de regressão em código alheio.

- [X] T002 Mover `_cronograma` de `backend/processo_seletivo/portal/views.py` para `backend/processo_seletivo/portal/leitura.py` como função pública `cronograma(conteudo, agora)`, **sem alterar uma linha da lógica**, e fazer `acompanhamento` chamá-la de lá (`T-003`)
- [X] T003 Extrair a lista de Eventos de `backend/processo_seletivo/portal/templates/portal/acompanhamento.html` para `backend/processo_seletivo/portal/templates/portal/_cronograma.html`, **preservando a marcação exatamente** — `class="marco {{ evento.situacao }}"`, o `✓` do concluído, `.rotulo`, `.quando`, `.onde`. *`tests/integration/portal/test_acompanhamento.py` afirma sobre a substring `class="marco em_curso"`: quebrar ali é quebrar teste que nada tem a ver com esta feature*
- [X] T004 Deixar o caso vazio **fora** do parcial: `acompanhamento.html` mantém `O Edital não publicou cronograma.` no próprio arquivo. *A `FR-128` proíbe essa frase na página pública, e a `T-003` explica por que não é inconsistência: quem já se inscreveu está numa tela sobre a própria inscrição; quem decide, numa página sobre o Edital*
- [X] T005 Rodar `uv run pytest tests/integration/portal/test_acompanhamento.py` em `backend/` e exigir verde **antes** de seguir. *Regressão zero é o contrato desta fase: nada do que ela faz deveria mudar comportamento nenhum*

**Checkpoint**: o cronograma é chamável pelas duas views e renderizável pelas duas telas, e a área do candidato continua idêntica.

---

## Phase 3: User Story 1 — Saber quando as coisas acontecem (Priority: P1) 🎯 MVP

**Goal**: o cronograma publicado passa a ser legível por quem ainda não se identificou.

**Independent Test**: abrir a página de uma seleção com cronograma publicado, sem sessão, e ver cada Evento com data e situação, na ordem publicada.

### Tests for User Story 1

- [X] T006 [P] [US1] Teste de integração em `backend/tests/integration/portal/test_cronograma_publico.py`: sem sessão, os Eventos aparecem na ordem publicada, com o período declarado e a situação do Evento (`FR-125`, `FR-126`, `FR-150`)
- [X] T007 [P] [US1] Em `backend/tests/integration/portal/test_cronograma_publico.py`, o Evento com local declarado traz o local, e o sem local não gera linha (`FR-127`)
- [X] T008 [P] [US1] Em `backend/tests/integration/portal/test_cronograma_publico.py`, Edital sem cronograma publicado **não** desenha seção nem frase de ausência (`FR-128`, `D-009`)
- [X] T009 [P] [US1] Em `backend/tests/integration/portal/test_cronograma_publico.py`, nenhuma frase da seção fala de quem lê — a asserção é sobre o vocabulário da situação, que descreve o Evento (`FR-126`)

### Implementation for User Story 1

- [X] T010 [US1] Acrescentar `cronograma` ao contexto da view `selecao` em `backend/processo_seletivo/portal/views.py`, chamando `leitura.cronograma` (`FR-125`)
- [X] T011 [US1] Incluir `_cronograma.html` em `backend/processo_seletivo/portal/templates/portal/selecao.html`, dentro de uma seção com título próprio, **e envolver a seção inteira na condição de haver Evento** (`FR-128`)
- [X] T012 [P] [US1] Acrescentar a `backend/tests/interface/test_acessibilidade_do_portal.py` a asserção de que a seção do cronograma é anunciada como seção, e a situação não depende só de cor (`UX-019`)

**Checkpoint**: `US1` completa e demonstrável sozinha. É o MVP — maior valor da feature, e nenhum código de regra novo.

---

## Phase 4: User Story 3 — Entender a vaga sem abrir o PDF (Priority: P1)

**Goal**: os campos publicados que descrevem o trabalho aparecem, e cadastro reserva deixa de ser lido como ausência de vaga.

**Independent Test**: abrir uma seleção cujos Perfis declaram atribuições, carga horária e remuneração e ver os três; abrir um Perfil com zero vagas imediatas e reserva e ver a oferta como leitura principal.

### Tests for User Story 3

- [X] T013 [P] [US3] Teste em `backend/tests/integration/portal/test_detalhe_selecao.py`: atribuições, carga horária e remuneração aparecem quando declaradas (`FR-134`)
- [X] T014 [P] [US3] Em `backend/tests/integration/portal/test_detalhe_selecao.py`, campo não declarado (`""` no conteúdo publicado) **não** gera rótulo nem "não informado" (`FR-135`, `D-009`)
- [X] T015 [P] [US3] Em `backend/tests/integration/portal/test_detalhe_selecao.py`, Perfil com zero vagas imediatas e cadastro reserva: a oferta é a leitura principal, o número continua dito, e o convite continua disponível (`FR-136`, `D-007`)
- [X] T016 [P] [US3] Teste em `backend/tests/unit/publicacoes/test_pdf.py` (ou arquivo vizinho) provando que **o texto do documento publicado sobre cadastro reserva não mudou** (`T-010`, Princípio II)

### Implementation for User Story 3

- [X] T017 [US3] Estender `_perfil` em `backend/processo_seletivo/portal/views.py` para extrair `duties`, `workload` e `compensation` do conteúdo publicado, com `""` significando não declarado (`FR-134`, `FR-135`)
- [X] T018 [US3] Exibir os três em `backend/processo_seletivo/portal/templates/portal/selecao.html`, junto dos requisitos, cada um sob condição própria (`FR-134`, `FR-135`)
- [X] T019 [US3] Derivar `oferta` em `backend/processo_seletivo/portal/views.py` a partir de `immediateVacancies` e `reserveType`, nas três formas da §2.2 do [data-model.md](./data-model.md) (`FR-136`)
- [X] T020 [US3] Reescrever o bloco `.lateral-vaga` de `backend/processo_seletivo/portal/templates/portal/selecao.html` para que o destaque tipográfico caia na oferta quando não há vaga imediata (`FR-136`, `D-007`). **Não tocar** em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` nem em `backend/processo_seletivo/interface/revisao.py`
- [X] T021 [US3] Acrescentar, junto do convite de inscrição em `backend/processo_seletivo/portal/templates/portal/selecao.html`, o aviso de que inscrever-se exige identificação (`FR-137`). *O convite, o destino e os três estados dele permanecem intactos: este aviso é a **única** coisa que a feature acrescenta ali, e a §7 da spec diz isso explicitamente*

**Checkpoint**: `US1` e `US3` completas e independentes.

---

## Phase 5: User Story 2 — Saber se o que estou lendo ainda vale (Priority: P1)

**Goal**: o histórico normativo passa a ser visível, dito em linguagem do domínio.

**Independent Test**: retificar um Edital publicado e abrir a página pública — a retificação aparece com data e justificativa, e o conteúdo exibido é o vigente.

**⚠️ É a faixa que concentra o risco da feature**: o único código substancialmente novo está aqui.

### Tests for User Story 2

- [X] T022 [P] [US2] Teste unitário em `backend/tests/unit/publicacoes/test_alteracoes_legiveis.py`: uma tabela de caminho → (`onde`, `campo`) cobrindo **cada** coleção do conteúdo publicado — Perfil, Evento, Etapa, Documento Exigido, Anexo, Seção — e o campo de topo do Edital (`FR-130`)
- [X] T023 [P] [US2] Em `backend/tests/unit/publicacoes/test_alteracoes_legiveis.py`, caminho não reconhecido **não produz linha** — e a asserção é sobre a ausência, não sobre um rótulo genérico (`D-009`)
- [X] T024 [P] [US2] Em `backend/tests/unit/publicacoes/test_alteracoes_legiveis.py`, nenhuma saída contém `/`, `id=` ou dígito hexadecimal de 64 caracteres. *É a prova mecânica da `D-005`: endereçamento estrutural e resumo criptográfico não atravessam para a tela*
- [X] T025 [P] [US2] Teste em `backend/tests/integration/publicacoes/test_atos_publicados.py` do novo selector: a abertura e as Retificações **publicadas** entram; em elaboração, em revisão, homologada e cancelada **não** (`FR-129`)
- [X] T026 [P] [US2] Teste de integração em `backend/tests/integration/portal/test_historico_publico.py`, com a fixture `retify` de `backend/tests/fixtures/publicacao.py`: os atos aparecem com data, a Retificação traz justificativa e o que mudou em português, e o documento de cada ato é alcançável (`FR-129`, `FR-130`, `FR-132`)
- [X] T027 [P] [US2] Em `backend/tests/integration/portal/test_historico_publico.py`, **Retificação com vigência futura**: o ato aparece como publicado, com a data em que passa a valer, e o conteúdo da página continua sendo o que vale hoje (`FR-131`). *É o caso que o `seed_demo` produz sozinho, e o que separa "publicado" de "vigente"*
- [X] T028 [P] [US2] Em `backend/tests/integration/portal/test_historico_publico.py`, Edital com **um único** ato publicado não desenha seção de histórico nem frase de negação (`FR-133`, `D-009`)

### Implementation for User Story 2

- [X] T029 [US2] Criar `backend/processo_seletivo/publicacoes/domain/alteracoes.py` com o tradutor `target_path` → (`onde`, `campo`, `operacao`), lendo o rótulo da entidade no conteúdo-base e devolvendo **nada** para caminho não reconhecido (`FR-130`, `D-005`, `D-009`). *Sem valor anterior nem novo: quem quer o texto do ato abre o documento da Retificação, que está na mesma linha*
- [X] T030 [US2] Acrescentar o selector `atos_publicados(edital_id)` a `backend/processo_seletivo/publicacoes/application/selectors.py`, devolvendo Publicações e Retificações publicadas em ordem cronológica, sem cursor, com `select_related` do documento e `prefetch_related` das alterações (`T-001`)
- [X] T031 [US2] Acrescentar `atos` e `vigente_desde` ao contexto da view `selecao` em `backend/processo_seletivo/portal/views.py` (`FR-129`, `FR-131`)
- [X] T032 [US2] Criar `backend/processo_seletivo/portal/templates/portal/_historico.html`: uma linha por ato, com natureza, data de publicação, vigência quando distinta, justificativa da Retificação, o que mudou, e o documento daquele ato (`FR-129`, `FR-130`, `FR-132`)
- [X] T033 [US2] Incluir `_historico.html` em `backend/processo_seletivo/portal/templates/portal/selecao.html` sob a condição de haver **mais de um** ato, e identificar o conteúdo exibido como vigente (`FR-131a`, `FR-133`)

**Checkpoint**: as três P1 completas. A feature já entrega o que a motivou.

---

## Phase 6: User Story 5 — As quatro situações (Priority: P2)

**Goal**: a vitrine para de fundir três situações num grupo só.

**Independent Test**: publicar seleções nas quatro situações e ver cada uma anunciada com marca própria.

### Tests for User Story 5

- [X] T034 [P] [US5] Teste em `backend/tests/integration/portal/test_vitrine.py`: **sem consulta ativa**, as quatro situações aparecem em grupos distintos, e futuras não caem junto de encerradas (`FR-145`, `FR-146`)
- [X] T035 [P] [US5] Em `backend/tests/integration/portal/test_vitrine.py`, a seleção aberta traz data-limite exata **e** prazo restante (`FR-147`)
- [X] T036 [P] [US5] Em `backend/tests/integration/portal/test_vitrine.py`, a encerrada tem caminho visível para consulta (`FR-148`), e a sem período designado **não** é chamada de encerrada nem recebe frase de prazo (`FR-149`)
- [X] T037 [P] [US5] Em `backend/tests/integration/portal/test_vitrine.py`, seleção cancelada não aparece na vitrine e continua alcançável pelo endereço (`FR-152`)

### Implementation for User Story 5

- [X] T038 [US5] Substituir `abertas`/`outras` por agrupamento nas quatro situações em `backend/processo_seletivo/portal/views.py`, preservando a ordem de urgência dentro de cada grupo, e cair numa lista única quando há consulta ativa (`FR-146`, `FR-146a`, `FR-140a`, `T-009`)
- [X] T039 [US5] Reescrever os grupos em `backend/processo_seletivo/portal/templates/portal/vitrine.html`, cada um com título próprio — e **suprimir os cabeçalhos** quando há consulta ativa, deixando uma lista única (`FR-146`, `FR-146a`)
- [X] T040 [US5] Dar ao cartão, em `backend/processo_seletivo/portal/templates/portal/_cartao_da_selecao.html`, a marca explícita de situação e o caminho visível para a seleção sem inscrição aberta (`FR-145`, `FR-148`, `UX-016`)
- [X] T041 [US5] Rodar `uv run pytest tests/portal/test_peso_da_vitrine.py` em `backend/`. *Aquele arquivo afirma sobre a **folha de estilo** da vitrine — que `.situacao.aberto` mantém a cor de estado e que a regra da lista de inscrições não vence por ordem na folha. Regra nova quebra asserção de substring, e o defeito que ele prende é exatamente o que a `FR-145` pede*

**Checkpoint**: a vitrine diz a situação sem que ninguém precise interpretar o agrupamento.

---

## Phase 7: User Story 4 — Encontrar sem ler todas (Priority: P2)

**Goal**: busca, filtros, ordenação, contagem — e a consulta preservada na volta.

**Independent Test**: com o catálogo publicado, localizar uma seleção por termo e por filtro, conferir a contagem, e voltar da seleção com a consulta aplicada.

### Tests for User Story 4

- [X] T042 [P] [US4] Teste unitário em `backend/tests/unit/test_dobra_de_texto.py`: acento, caixa e combinantes dobram; a função é idempotente (`T-005`)
- [X] T043 [P] [US4] Teste em `backend/tests/integration/portal/test_consulta_da_vitrine.py`: busca devolve só as seleções cujo **texto do cartão** contém o termo, a contagem confere e é **um número só** — não um por grupo (`FR-138`, `FR-141`, `T-011`)
- [X] T044 [P] [US4] Em `backend/tests/integration/portal/test_consulta_da_vitrine.py`, filtros por unidade, situação e Perfil se somam à busca — `E`, nunca `OU` (`FR-139`)
- [X] T045 [P] [US4] Em `backend/tests/integration/portal/test_consulta_da_vitrine.py`, `ordem=prazo` é o padrão e `ordem=recentes` ordena pelo início de vigência **do conteúdo exibido** — uma Retificação publicada hoje e vigente semana que vem não muda a posição hoje —, e a ordem vale dentro do grupo quando há agrupamento e sobre a lista inteira quando há consulta (`FR-140`, `FR-140a`, `T-006`)
- [X] T046 [P] [US4] Em `backend/tests/integration/portal/test_consulta_da_vitrine.py`, consulta sem resultado diz o que foi procurado e oferece a volta, **sem** status de erro (`FR-142`)
- [X] T047 [P] [US4] Em `backend/tests/integration/portal/test_consulta_da_vitrine.py`, valor irreconhecível em qualquer parâmetro é lido como ausência do filtro, sem 4xx e sem mensagem de erro (`T-004`)
- [X] T048 [P] [US4] Em `backend/tests/integration/portal/test_consulta_da_vitrine.py`, a consulta está inteira no endereço e reproduz a mesma lista noutra sessão (`FR-143`, `SC-045`)
- [X] T049 [P] [US4] Teste em `backend/tests/integration/portal/test_detalhe_selecao.py`: o caminho de volta preserva a consulta, e **só** os cinco parâmetros declarados atravessam — um endereço externo injetado não sobrevive (`FR-144`, `T-007`)

### Implementation for User Story 4

- [X] T050 [P] [US4] Criar `backend/processo_seletivo/shared/texto.py` com a dobra NFKD + remoção de combinantes + `casefold` (`T-005`)
- [X] T051 [US4] Fazer `backend/processo_seletivo/comissoes/application/selectors.py` delegar a dobra dele a `shared.texto`, sem mudar comportamento. **Não tocar** em `backend/processo_seletivo/sorteios/domain/normalizacao.py` — é regra auditável do sorteio, com prova pública dependendo dela (`T-005`)
- [X] T052 [US4] Implementar o saneamento da consulta em `backend/processo_seletivo/portal/leitura.py`: os cinco parâmetros da §2.6 do [data-model.md](./data-model.md), valor irreconhecível lido como ausência (`T-004`)
- [X] T053 [US4] Aplicar busca, filtros e ordenação na view `vitrine` de `backend/processo_seletivo/portal/views.py`, **sobre o conjunto que a página já carrega** — sem consulta nova ao banco (`FR-138`, `FR-139`, `FR-140`, `D-003`)
- [X] T054 [US4] Criar `backend/processo_seletivo/portal/templates/portal/_consulta.html` com `<form method="get" role="search">`, campo de busca rotulado e os três seletores, no molde de `backend/processo_seletivo/interface/templates/interface/inscricoes.html` (`FR-138`, `FR-139`, `UX-017`)
- [X] T055 [US4] Exibir a contagem — total encontrado, um número só —, o caminho para limpar e o estado vazio com o que foi procurado, em `backend/processo_seletivo/portal/templates/portal/vitrine.html` (`FR-141`, `FR-142`)
- [X] T056 [US4] Fazer a consulta viajar no link de cada cartão em `backend/processo_seletivo/portal/templates/portal/_cartao_da_selecao.html`, e a view `selecao` devolvê-la no caminho de volta (`FR-143`, `FR-144`). *A gestão já registrou o defeito a evitar: "foi como o cartão acabou perdendo a busca que o formulário preservava"*
- [X] T057 [P] [US4] Acrescentar a `backend/tests/interface/test_acessibilidade_do_portal.py` a asserção de que o campo de busca tem rótulo associado e a região tem `role="search"` (`UX-017`, `UX-018`)

**Checkpoint**: as cinco stories completas.

---

## Phase 8: Polish & Cross-Cutting Concerns

- [X] T058 [P] Escrever `specs/024-descoberta-e-transparencia-no-portal/rastreabilidade.md` cobrindo **cada** identificador definido na spec — `FR-125`–`FR-152`, `UX-016`–`UX-019`, `SC-040`–`SC-047`, **e os três de sufixo de letra citados um a um**: `FR-131a`, `FR-140a` e `FR-146a`. *`tests/test_citacoes_de_requisito.py` cobra a matriz inteira assim que o arquivo existe, e **não** aceita intervalo cobrindo sufixo de letra — foi assim que duas linhas da `010` passaram batido*
- [X] T059 [P] Conferir a legibilidade em 375 px das duas telas, inclusive o formulário de consulta e a tabela do histórico (`UX-018`)
- [X] T060 [P] Teste em `backend/tests/integration/portal/test_leitura_sem_escrita.py`: sob `CaptureQueriesContext`, um `GET` da vitrine e um da página da seleção não emitem `INSERT`, `UPDATE` nem `DELETE`, e não criam `RegistroAuditoria` (`FR-151`, `SC-047`). *É o invariante 2 da §5, e o único da feature que hoje só se confere à mão. Afirmar sobre a **consulta emitida** — e não sobre contagem de linhas — é o que faz a garantia sobreviver ao próximo refactor; o padrão é o de `tests/unit/divulgacao/test_conteudo.py`. **Pode ser escrita já na Phase 2** e fica verde o percurso inteiro*
- [X] T061 Percorrer [quickstart.md](./quickstart.md) inteiro, **em janela anônima**, incluindo as contraprovas de cada roteiro. *Sessão aberta é o jeito mais fácil de um percurso passar sem provar `FR-150`*
- [X] T062 Conferir, um a um, os sete invariantes da §5 de [spec.md](./spec.md) ao fim do percurso
- [X] T063 Rodar `cd backend && make lint check test-pg`. *`test-pg` e não `test`: sem `TEST_DB_ENGINE=postgresql` **e** a role certa a suíte cai para SQLite e 21 casos falham. E `lint` são **dois** passos — `ruff check` e `ruff format --check`*

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependência
- **Foundational (Phase 2)**: depende do Setup — **bloqueia `US1`**, e só ela
- **Phase 3 (`US1`)**: depende da Foundational
- **Phases 4 a 7 (`US3`, `US2`, `US5`, `US4`)**: dependem apenas do Setup
- **Polish (Phase 8)**: depende de todas as stories desejadas

### User Story Dependencies

Nenhuma story depende de outra. É consequência da natureza da feature — cinco leituras
independentes do mesmo conteúdo publicado —, e é o que torna qualquer subconjunto entregável.

- **`US1` (P1)**: depende da Phase 2 (o cronograma compartilhado)
- **`US3` (P1)**: independente
- **`US2` (P1)**: independente
- **`US5` (P2)**: independente
- **`US4` (P2)**: independente; toca os mesmos arquivos que `US5` (`vitrine.html`, `_cartao_da_selecao.html`), então **não** convém executá-las em paralelo por pessoas diferentes

### Parallel Opportunities

- T001 é o único do Setup
- Dentro de cada story, todo bloco de testes marcado `[P]` corre junto
- `US3` e `US2` podem correr em paralelo com `US1`: arquivos distintos, exceto `views.py` e `selecao.html`, que pedem coordenação
- `US5` e `US4` disputam os dois arquivos da vitrine — sequenciais, `US5` primeiro

### Parallel Example: User Story 2

```bash
# Os testes da US2, juntos:
Task: "Tradutor, coleção por coleção, em tests/unit/publicacoes/test_alteracoes_legiveis.py"
Task: "Selector dos atos publicados em tests/integration/publicacoes/test_atos_publicados.py"
Task: "Histórico na tela em tests/integration/portal/test_historico_publico.py"
```

---

## Implementation Strategy

### MVP (só `US1`)

1. Phase 1 → Phase 2 → Phase 3.
2. **Pare e valide**: o cronograma publicado está legível sem sessão.
3. É o melhor MVP possível desta feature: entrega o dado publicado mais consultado e mais escondido,
   e não escreve regra nenhuma — a Phase 2 move código, e a Phase 3 renderiza.

### Entrega incremental

1. Setup + Foundational → base pronta
2. `US1` → cronograma público → **demonstrável** (MVP)
3. `US3` → a vaga inteira → demonstrável
4. `US2` → histórico normativo → demonstrável *(a de maior peso constitucional)*
5. `US5` → quatro situações → demonstrável
6. `US4` → descoberta → demonstrável

Parar em qualquer ponto deixa o portal melhor do que estava, e nenhuma etapa deixa a seguinte
obrigatória.

---

## Notes

- `[P]` = arquivos distintos, sem dependência pendente
- Cada story é completável e testável sozinha
- Commit por tarefa ou grupo lógico
- **Duas armadilhas de regressão, ambas em código alheio à feature**: `test_acompanhamento.py`
  afirma sobre a marcação do cronograma (T005), e `test_peso_da_vitrine.py` afirma sobre a folha de
  estilo da vitrine (T041). As duas tarefas existem para que a quebra apareça na hora, e não três
  fases depois
- **Nenhuma tarefa grava dado.** Se alguma levar a `models.py`, `makemigrations` ou a um contador de
  navegação, ela foi mal lida — `D-001`, `D-008`, `FR-151`
