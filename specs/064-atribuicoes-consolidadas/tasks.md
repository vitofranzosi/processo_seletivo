# Tasks: As atribuições idênticas saem uma vez no documento do Edital

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/documento.md](contracts/documento.md),
[quickstart.md](quickstart.md)

**Tests**: pedidos — cada `FR-`, `SC-` e caso-limite da spec tem teste, e o teste vem **antes** do
código: cada fase de teste roda e falha contra a `main` antes da fase de implementação dela.

**Caminhos**: relativos à raiz do repositório. `backend/` é o projeto Django. O arquivo de teste
novo é `backend/tests/unit/publicacoes/test_atribuicoes_consolidadas.py`, chamado abaixo de
**o arquivo novo**.

**Produção**: um arquivo só, `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`. Nenhuma
outra tarefa toca código de produção.

**Cenários**: todo texto de atribuições dos testes **que compõem o documento** usa só caracteres
que o documento representa — nada de `●`, `≥` ou marcador colado de editor —, para que o defeito de
codificação, tratado fora desta feature, não entre em nenhum resultado (D-006). **A exceção é a
T003**, que testa a regra de identidade sem compor PDF: ali o símbolo que o documento não representa
é justamente o caso a provar (o caso-limite "Caractere que o documento não representa").

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivo diferente, sem dependência pendente)
- **[Story]**: a história da spec (US1 a US3)

---

## Phase 1: Setup

- [X] T001 Preparar a worktree: `cd backend && uv sync --extra dev`, e conferir `uv run python manage.py migrate --check` contra o banco local
- [X] T002 Medir o ponto de partida contra PostgreSQL (comando do [quickstart.md](quickstart.md), §1, com `tests/unit/publicacoes tests/contract`): verde, e o total guardado em `specs/064-atribuicoes-consolidadas/verificacao.md`. A contagem de 52 casos expostos citada no [plan.md](plan.md) foi medição única da análise, com instrumento descartável, e **não** é refeita aqui: quem a substitui como prova é a T020, que roda esses mesmos diretórios depois da mudança

---

## Phase 2: Foundational — a regra de identidade e a leitura do documento

Bloqueia todas as histórias: a regra (FR-1187, FR-1188) é usada pelas três, e a leitura do documento
é a ferramenta de todos os testes de forma e de integridade.

### Testes (escritos primeiro; falham por falta da função)

- [X] T003 No arquivo novo, testes da função de agrupamento sobre listas de Perfis em forma de snapshot (D-002): textos idênticos agrupam; espaço repetido, espaço no fim da linha e uma ou várias linhas em branco entre parágrafos não impedem; quebra de linha a mais ou a menos impede; pontuação, maiúscula, acento e símbolo impedem; mesmos parágrafos em outra ordem impedem; subconjunto impede; e o caso-limite do caractere que o documento não representa — `"● Conhecer a proposta"` contra `"▪ Conhecer a proposta"`, e `"● …"` contra `"• …"`, **não** agrupam, porque a comparação é sobre o texto registrado e não sobre o "?" que os dois imprimiriam (FR-1187)
- [X] T004 No arquivo novo, testes do que nunca agrupa (FR-1188): texto vazio em vários Perfis; Edital de um Perfil; mesma denominação com textos diferentes; e o contrário — denominações diferentes com o mesmo texto **agrupam**
- [X] T005 No arquivo novo, testes da ordem e da numeração dos grupos (D-003, data-model): dois grupos saem na ordem do primeiro Perfil de cada um; os Perfis de cada grupo na ordem do snapshot; números contíguos a partir de `N+1`; cada Perfil em no máximo um grupo
- [X] T006 No arquivo novo, o auxiliar de leitura dos testes, `atribuicoes_no_documento(pdf, snapshot)`: para cada Perfil do snapshot, acha a subseção dele no texto desenhado (`texto_de`/`linhas_desenhadas` de `backend/tests/unit/publicacoes/test_pdf.py`), lê o bloco próprio ou o número da remissão, segue até a subseção comum e devolve `{código: (fonte, [parágrafos])}`, em que `fonte` é `"própria"` ou o número do item (D-006). **Delimitação**, pelo recuo de `linhas_desenhadas`: o bloco próprio são as linhas depois do rótulo "Atribuições" (negrito, recuo 18) até a primeira linha com recuo menor que 32 — os requisitos (`• …`) também saem com recuo 32, mas vêm depois do rótulo "Requisitos", com recuo 18, que encerra o bloco; a remissão é a linha cujo texto começa por "Atribuições:", e o número é o que vem depois de "item "; a subseção comum são as linhas depois do título dela até o próximo título de subseção (`{s}.` seguido de número) ou de seção (`n. `), ou o fim do texto. Os cenários usam itens de uma linha cada, para que cada linha desenhada seja um parágrafo; o item de várias linhas só aparece na T022, que compara palavras
- [X] T007 Rodar o arquivo novo contra a `main`: T003 a T005 falham por `ImportError`/`AttributeError`, e nenhum por outra razão

### Implementação

- [X] T008 Em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`, o auxiliar puro de agrupamento logo depois de `_paragrafos`: chave = tupla de `" ".join(p.split())` sobre `_paragrafos(duties)`; grupos de dois ou mais Perfis com chave não vazia, na ordem do snapshot; nada quando há um Perfil só. Docstring no tom do módulo: por que a chave reusa `_paragrafos` (chave e impressão não divergem), por que compara o texto registrado e não o impresso, e a emenda aos FR-016 e FR-021 da `008`
- [X] T009 Rodar T003 a T005: verdes

**Checkpoint**: a regra existe e está provada; o documento ainda não a usa.

---

## Phase 3: User Story 1 — Quem elabora vê, na prévia, as atribuições comuns uma vez só (Priority: P1) 🎯 MVP

**Goal**: o documento imprime o texto comum uma vez, em subseção ao fim da seção de Perfis, e o
Perfil agrupado traz a remissão (FR-1186, FR-1189, FR-1190, FR-1192 a FR-1194, FR-1197).

**Independent Test**: compor a prévia de um Edital com Perfis de texto idêntico e Perfis de texto
próprio, e ler onde cada texto aparece.

### Testes (escritos primeiro; falham contra a `main`)

- [X] T010 [US1] No arquivo novo, cenários 1 a 4 da US1: dois Perfis iguais → uma subseção `{s}.3` intitulada *"Atribuições comuns aos Perfis A e B"*, o texto uma vez, e cada Perfil com **"Atribuições:"** *as descritas no item {s}.3.* ([contrato](contracts/documento.md)); textos diferentes → nenhuma subseção comum; subconjunto → nenhuma, e os dois textos inteiros; mesma denominação e textos diferentes → nenhuma
- [X] T011 [P] [US1] No arquivo novo, os casos-limite de forma: dois grupos → duas subseções, cada Perfil remetendo à sua; todos os Perfis num grupo → uma subseção nomeando todos os códigos; três Perfis agrupados com um de texto próprio entre eles → o de texto próprio intacto e no lugar; texto vazio → nenhum "Atribuições" e nenhuma subseção (FR-1188)
- [X] T012 [P] [US1] No arquivo novo, `SC-457`: dez Perfis de mesmo texto, com itens de uma linha cada (para servir também à T021) → o texto aparece uma vez, há dez remissões e todas apontam o mesmo item
- [X] T013 [P] [US1] No arquivo novo, `FR-1192`/`SC-459`: para o mesmo snapshot, compor com Perfis agrupados e com os mesmos Perfis de textos tornados distintos, e comparar as listas de títulos de subseção de Perfil (`{s}.1` a `{s}.N`), de títulos de seção de topo e de legendas `Tabela n — …`, que devem ser idênticas; e `pdf.numeracao(snapshot)` igual nos dois. Conferir também que a subseção comum não abre tabela
- [X] T014 [P] [US1] No arquivo novo, `FR-1197`: no cenário agrupado, Requisitos, Remuneração, quadro de vagas, modalidades e marcos continuam impressos em cada Perfil, na mesma quantidade que no cenário sem agrupamento
- [X] T015 [P] [US1] No arquivo novo, `FR-1193`: uma subseção comum com texto maior que uma página quebra entre parágrafos e a composição conclui; o título dela nunca é a última linha de uma página (`paginas_de` de `test_pdf.py`); e, quando ela cabe inteira na página seguinte, não começa no rodapé da anterior
- [X] T016 [P] [US1] No arquivo novo, `FR-1194`: o Edital de um Perfil só não tem subseção comum nem remissão, e `test_o_documento_publicado_continua_byte_a_byte_o_mesmo` (`backend/tests/contract/test_documento_publicado.py`, Perfil único) continua verde sem regenerar a fixture
- [X] T017 [US1] Rodar T010 a T016 contra a `main`: falham T010 a T015 pela forma, e T016 passa (é a garantia que não pode mudar)

### Implementação

- [X] T018 [US1] Em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py::_perfis`: calcular os grupos antes do laço; no Perfil agrupado, trocar o bloco de atribuições pelo par **"Atribuições:"** *as descritas no item {s}.{N+k}.* com `_pares` (D-004); depois do laço, uma subseção por grupo num `composicao.bloco()` **coeso** — nunca `coeso=False`, que impediria o salto inteiro de página que o FR-1193 pede —, título em negrito com `CORPO_BLOCO`, `ANTES_DE_BLOCO + 4` e `junto=True`, códigos com `_enumerar`, e cada parágrafo num `bloco()` próprio, justificado, recuo 18 (D-005). Perfil sem grupo e Edital de um Perfil seguem o caminho de hoje sem alteração. Comentário do porquê no tom do módulo, citando a emenda aos FR-016 e FR-021 da `008`
- [X] T019 [US1] Rodar o arquivo novo inteiro: verde
- [X] T020 [US1] Rodar `uv run pytest tests/unit/publicacoes tests/contract -q`. Conferir em especial `test_a_medicao_de_um_bloco_atravessa_os_quadros_que_ele_contem` (`backend/tests/unit/publicacoes/test_pdf.py`), cujos dois Perfis têm o mesmo texto: se falhar, dar ao segundo Perfil um texto próprio, para que o cenário volte a medir o bloco de atribuições, e **nunca** afrouxar a asserção — registrando a edição em `verificacao.md`. A fixture `documento_publicado_v1.pdf` **não** é regerada: se `test_o_documento_publicado_continua_byte_a_byte_o_mesmo` falhar, a implementação está errada

**Checkpoint**: a prévia de quem elabora já mostra o texto comum uma vez. MVP.

---

## Phase 4: User Story 2 — O candidato encontra as atribuições do seu Perfil, sem ambiguidade (Priority: P1)

**Goal**: cada Perfil tem exatamente uma fonte de atribuições, equivalente às da versão (FR-1191).

**Independent Test**: para cada Perfil do documento, reconstruir as atribuições pelo bloco próprio ou
pela remissão, e comparar com as da versão.

### Testes

- [X] T021 [US2] No arquivo novo, o teste de integridade (`FR-1191`, `SC-458`), parametrizado sobre os cenários de T010 a T012 e um misto de três grupos com dois Perfis de texto próprio: com o auxiliar de T006, para cada Perfil do snapshot, (a) há exatamente uma fonte; (b) os parágrafos lidos, reduzidos pela chave do FR-1187, são **iguais** aos do snapshot — mesmo conteúdo, mesma ordem, nenhum acrescentado, omitido ou trocado; (c) a remissão aponta subseção que existe no mesmo documento e cujo título nomeia o código do Perfil; (d) cada subseção comum é apontada por todos os Perfis que o título dela nomeia, e por nenhum outro. Perfil de texto vazio: nenhuma fonte e nenhum texto
- [X] T022 [P] [US2] No arquivo novo, um cenário com um item de várias linhas num grupo: a sequência de palavras lida na subseção comum é a do snapshot, palavra a palavra
- [X] T023 [P] [US2] No arquivo novo, a US2/cenário 3: uma seção textual do snapshot que cita *"item 11.2"* e *"Tabela 3"* — os números de seção e de tabela que essas remissões apontam são os mesmos com e sem agrupamento (reusa a comparação de T013)
- [X] T024 [US2] Rodar T021 a T023: verdes. Se T021 reprovar, o defeito é de composição e se corrige em `_perfis`, nunca no auxiliar de leitura

**Checkpoint**: a integridade versão → documento está demonstrada por teste.

---

## Phase 5: User Story 3 — O que já foi publicado não muda, e o que se publicar depois é coerente (Priority: P2)

**Goal**: documentos guardados intactos; o documento da Retificação reagrupa pela versão retificada
(FR-1195, FR-1196).

**Independent Test**: publicar, retificar as atribuições de um Perfil agrupado e comparar os dois
documentos guardados.

### Testes

- [X] T025 [US3] Em `backend/tests/integration/publicacoes/test_retificacoes.py`, marcado `django_db(transaction=True)` e `integration` (D-007): publicar com `publish_original(..., draft=...)` um Edital de três Perfis de mesmo texto. **Como montar o rascunho**: partir de `complete_draft()` (`backend/tests/fixtures/edital.py`), que é o Edital mínimo publicável, com marco; dar ao Perfil dele o texto de atribuições do cenário; e criar o segundo e o terceiro com `duplicar_perfil` (`backend/processo_seletivo/editais/domain/duplicacao.py`, da `043`), passando `codigo`, `localidade` e `etapas_do_edital` com os `id` das Etapas do rascunho — é ela que dá identidade nova a Perfil, modalidades, linhas do quadro e marcos e remapeia as referências internas, e a montagem à mão é o que costuma deixar referência apontando a origem. Conferir que a forma de entrada é a mesma do rascunho, como em `duplicar` de `backend/tests/unit/editais/test_duplicacao.py`; se a publicação recusar, a mensagem do achado impeditivo diz o que falta. Guardar os bytes do documento original; retificar `duties` de um deles (caminho por `id` do Perfil, como `caminho_perfil`); publicar. Conferir: o documento original continua com os mesmos bytes; o da Retificação agrupa só os dois iguais (`texto_de`), e o terceiro traz o próprio texto; `alteracoes_legiveis` nomeia o Perfil e "Atribuições", e nunca a subseção
- [X] T026 [P] [US3] No arquivo novo, os casos-limite de Retificação compondo o conteúdo depois da mudança, sem banco: Perfil acrescentado com o mesmo texto de um grupo entra no grupo; grupo reduzido a um Perfil se desfaz e ele volta a trazer o próprio texto
- [X] T027 [P] [US3] No arquivo novo, `FR-1195`: compor não altera o snapshot recebido (cópia profunda antes e depois, iguais) e `canonical_sha256` do snapshot é o mesmo antes e depois de compor
- [X] T028 [US3] Rodar T025 a T027 contra PostgreSQL com banco próprio (ver [quickstart.md](quickstart.md)): verdes

**Checkpoint**: o passado está protegido e a Retificação é coerente.

---

## Phase 6: Polish & Cross-Cutting

- [X] T029 [P] Em `backend/tests/contract/test_documento_publicado.py`: parametrizar `test_o_corpo_normativo_quebra_nas_mesmas_paginas_na_previa_e_no_publicado` e `test_removidas_as_diferencas_permitidas_as_composicoes_sao_equivalentes` com um segundo snapshot — o `SNAPSHOT` com três Perfis, dois de mesmo texto — mantendo o `SNAPSHOT` original como primeiro caso (`FR-1194`, `SC-460`). A fixture byte a byte fica como está
- [X] T030 [P] Escrever `specs/064-atribuicoes-consolidadas/rastreabilidade.md`: uma linha por `FR-1186` a `FR-1197`, por `SC-457` a `SC-461` e por cada caso-limite da spec, com o teste que o prende; conferir com `uv run pytest tests/test_citacoes_de_requisito.py`
- [X] T031 Lint em **dois** passos: `cd backend && uv run ruff check . && uv run ruff format --check .`; e `make check`
- [X] T032 Suíte completa: `cd backend && make test-pg DB_NAME=test_ps_064`, **sem editar arquivo durante a execução**; total, pulados e diferenças contra a medição de T002 em `verificacao.md`. Antes, confirmar que nenhuma outra suíte usa o mesmo banco
- [X] T033 Quickstart §2 pela interface (`INTERFACE_SELETOR_IDENTIDADE=true`, prévia de um Edital com dois Perfis de mesmo texto e um próprio), com captura em `verificacao.md`
- [ ] T034 **Depois do merge da `063`** (PR #263): atualizar a branch com a `main`, resolver a linha do `README.md` pondo a `064` depois da `063`, medir de novo o teto de `FR-`/`SC-` em todas as worktrees e confirmar que `FR-1186` e `SC-457` continuam livres; rodar `tests/test_citacoes_de_requisito.py` e `tests/test_readme_acompanha_o_codigo.py`

---

## Dependencies & Execution Order

- **Phase 1 → Phase 2 → Phase 3**: a regra (T008) antes do documento (T018).
- **Phase 4** depende de T018 (lê o documento composto) e de T006 (o auxiliar de leitura).
- **Phase 5** depende de T018; T025 é o único teste transacional da feature.
- **T029 e T030** podem correr junto com a Phase 5. **T031 e T032** por último, nessa ordem.
- **T034** só quando a `063` estiver na `main`; se ela entrar antes do PR desta feature, roda antes
  de T032.
- T008 e T018 são as duas únicas tarefas de produção, no mesmo arquivo, em sequência.

## Parallel Example

```text
Depois de T018:
  T011, T012, T013, T014, T015 (mesmo arquivo de teste, casos independentes — [P] por não dependerem um do outro)
  T026, T027 enquanto T025 roda contra PostgreSQL
  T029 em test_documento_publicado.py
```

## Implementation Strategy

1. **MVP = Phases 1 a 3.** Ao fim de T020 a prévia já mostra o texto comum uma vez, e a garantia de
   um Perfil só está provada.
2. **Phase 4** é a prova de integridade que o 4º ajuste pede, e entra no mesmo PR: sem ela a
   consolidação não está demonstrada.
3. **Phase 5 e 6** fecham o histórico, a paginação de prévia × publicado e a rastreabilidade.
4. Um PR só, depois da aprovação: spec, plano, tarefas, uma alteração em `pdf.py` e os testes.
