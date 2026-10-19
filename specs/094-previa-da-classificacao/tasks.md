# Tasks: Prévia interativa da classificação — fatia 1

**Input**: Design documents from `specs/094-previa-da-classificacao/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: pedidos pela spec — a equivalência entre prévia e caminho oficial (FR-2233) e a ausência de
efeito (FR-2234) são requisitos, e a extração (FR-2232) só é segura com a linha de base escrita antes.

**Organization**: a Fase 2 é o motor — extração, irmã de `ordenar`, cenários e simulação —, e bloqueia
todas as histórias. Depois, uma fase por história, na ordem de prioridade da spec.

**O protótipo** (`prototipo/`) é a referência de comportamento e de desenho para as Fases 3 a 7: as
frases, as marcas, o agrupamento e a folha já foram validados nele, no navegador, em desktop e 375 px.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente)
- **[Story]**: a história da spec (US1 a US5)
- Caminhos relativos à raiz do repositório

---

## Phase 1: Setup

**Purpose**: ambiente e leitura do que já existe

- [ ] T001 Preparar a worktree: `uv sync --extra dev` em `backend/`, `DB_NAME` próprio para a suíte (ver `CLAUDE.md`, "Um banco de teste por worktree"), e conferir `manage.py migrate --check` antes de qualquer teste
- [ ] T002 Rodar o protótipo (`.claude/launch.json`, entrada `previa-094`) e percorrer a seção 1 de `specs/094-previa-da-classificacao/quickstart.md`, anotando as frases e marcas que a implementação reproduz

---

## Phase 2: Foundational — o motor (bloqueia todas as histórias)

**Purpose**: extrair a preparação do universo sem mudar o resultado oficial, dar a `ordenar` a irmã com
trajetória, e gerar e simular os cenários — tudo puro, testado antes da interface.

**⚠️ CRITICAL**: T003 precisa passar **contra o código de hoje**, antes de T006 e T007.

### Linha de base e testes, antes da extração

- [ ] T003 Escrever a linha de base do caminho oficial em `backend/tests/integration/classificacao/test_previa_equivale_ao_oficial.py`: um apoio `persistir_cenario(edital, perfil, inscritos)` que grava os candidatos de cada cenário como `Inscricao` `SUBMETIDA`, `ResultadoEtapa` e `ValorDeFato` sobre um Edital publicado (fixtures de `backend/tests/fixtures/corte.py` e `edital.py`), chama `calcular_ordem` e congela `posicoes` (id, posição, `empate_residual`, ordem de `separado_por`), `sem_posicao` (id, `consequencia`, `motivo`) e `universo`; e um teste por cenário que compara com a tabela esperada. Deve passar no código atual
- [ ] T004 [P] Testes unitários de `preparar` em `backend/tests/unit/classificacao/test_universo_classificavel.py`: eliminação mais recente pela `order` da Etapa; `SEM_PONTUACAO` com motivo nomeando as Etapas; marco só de portas (pontuação nula); `RegraIncompleta` sobe; ordem de entrada preservada; `recorte` filtra por `modalidade_id` e é idempotente sobre entrada já filtrada; `ELIMINADA` e `HABILITADA` iguais às de `ResultadoEtapa.Consequencia`
- [ ] T005 [P] Testes unitários de `ordenar_com_trajetoria` em `backend/tests/unit/classificacao/test_ordenar_com_trajetoria.py`: para toda entrada da tabela-verdade de `backend/tests/unit/classificacao/test_desempate.py` e de `test_numeracao_e_ausencia.py`, `ordenar(...)` é igual à irmã sem `trajetoria` e `grupo_da_pontuacao`; a trajetória registra `nao_separou` para critério que não particiona (valores iguais e `CRITERIO_NAO_SE_APLICA` com ausente) e `separou` para o que particiona, na ordem de `order`

### Extração

- [ ] T006 Criar `backend/processo_seletivo/classificacao/domain/universo_classificavel.py` com `ELIMINADA`, `HABILITADA` e `preparar(marco, etapas, inscritos, *, recorte=None)`, movendo de `classificacao/application/calculo.py` o laço de classificáveis e sem posição, `_eliminacao_mais_recente` e `_motivo_da_pontuacao_ausente`, sem mudar uma vírgula do comportamento (contrato em `contracts/universo-classificavel.md`)
- [ ] T007 Refatorar `calcular_ordem` em `backend/processo_seletivo/classificacao/application/calculo.py` para montar `inscritos` (com `resultados` por inscrição, na ordem de hoje) e chamar `universo_classificavel.preparar(..., recorte=recorte)`; as consultas, o `order_by` dos `vigentes` e o filtro do recorte na consulta ficam onde estão. T003 e T004 verdes
- [ ] T008 Em `backend/processo_seletivo/classificacao/domain/desempate.py`, criar `ordenar_com_trajetoria` sobre a partição de `_particionar` com o caminho registrado, e reescrever `ordenar` como a irmã sem as duas chaves novas. T005 e `test_desempate.py` verdes
- [ ] T009 Rodar, sem alterar nenhum teste: `backend/tests/unit/classificacao/`, `backend/tests/integration/classificacao/`, `backend/tests/integration/ocupacao/`, `backend/tests/performance/test_ordenacao.py`, `test_corte.py`, `test_ocupacao.py` e `backend/tests/test_vigencia_do_resultado.py`. Qualquer diferença de contagem de consultas reprova a extração (SC-844)

### Cenários e simulação

- [ ] T010 [P] Testes de `gerar` em `backend/tests/unit/classificacao/test_cenarios_da_previa.py`: determinismo (duas chamadas iguais); independência de pesos, operação, critérios, desfecho, Etapa governada e continuação (FR-2205); dependência de alvo, suplentes e vagas; âncoras de cada cenário (R-005); tamanho máximo 600; `modalidade_id` sempre nulo
- [ ] T011 Criar `backend/processo_seletivo/classificacao/domain/cenarios_da_previa.py` com `CENARIOS` (chave, rótulo, descrição) e `gerar(...)` conforme R-005 e o `previa.cenario` do protótipo, devolvendo inscritos na forma de `preparar`
- [ ] T012 [P] Testes de `simular` em `backend/tests/unit/classificacao/test_previa.py`: a matriz do achado (R-007) linha a linha; desfecho não declarado devolve as duas consequências sem escolher (FR-2216); `alternativo` só quando o empate atravessa (FR-2217); `faltas` para alvo vazio, quadro sem linha geral, mais de quatro Etapas com nota, critério sem alvo e critério sem valor ausente declarado quando alguém não tem o valor (FR-2227); aviso das vagas não avaliado com corte recusado ou sem quadro (FR-2221); e `simular` com alvo 400 e 100 suplentes em todos os cenários abaixo de 1 s cada, medido com `time.perf_counter` (SC-841)
- [ ] T013 Criar `backend/processo_seletivo/classificacao/application/previa.py` com `simular(marco, etapas, fatos, *, vagas, cenario)`: `faixa.normalizar`, `alvo_apurado`, `cenarios_da_previa.gerar`, `universo_classificavel.preparar`, `ordenar_com_trajetoria`, `faixa.calcular` (com o desfecho declarado e o outro), `apuracao.titulares_iniciais`; devolve a forma "Prévia" de `data-model.md`. Nenhuma consulta: quem chama entrega Etapas, fatos e vagas

**Checkpoint**: o motor está pronto, o caminho oficial é o mesmo de antes, e a prévia calcula sem interface.

---

## Phase 3: User Story 1 — Ver por que cada pessoa ficou onde ficou (Priority: P1) 🎯 MVP

**Goal**: o botão no cartão abre o painel fora dele, com candidatos fictícios, posições e o porquê de
cada linha.

**Independent Test**: com um marco por pontuação válido, o painel lista os candidatos com posição,
pontuação e motivo; a ordem é a do caminho oficial com os mesmos dados.

### Tests for User Story 1

- [ ] T014 [P] [US1] Testes de interface em `backend/tests/interface/test_previa_da_classificacao.py`: o botão existe sob `POR_PONTUACAO` e não sob `POR_SORTEIO` nem sem forma (FR-2200); o painel é renderizado em `#painel-da-previa`, fora do `fieldset.marco` (FR-2201); o cartão não ganha texto visível além do rótulo do botão (FR-428 da `030`); o painel nomeia Perfil e marco e marca os candidatos como fictícios (FR-2204)
- [ ] T015 [P] [US1] Testes das frases em `backend/tests/interface/test_previa_da_classificacao.py`: pontuação distinta; separado por critério com os valores comparados; critério que não separou por valores iguais e por `CRITERIO_NAO_SE_APLICA`; empate residual que divide a posição e "o sistema não escolhe"; sem posição por eliminação e por Etapa sem nota; posição dividida "por N" e a seguinte pulada (FR-2207 a FR-2210); agrupamento das linhas sem nada a dizer, nunca misturando situações (FR-2228)

### Implementation for User Story 1

- [ ] T016 [US1] Criar `backend/processo_seletivo/interface/previa_da_classificacao.py` com as linhas e as frases do painel a partir da saída de `simular` — o `porque` lê a `trajetoria`, nunca reordena (FR-2211) —, e o agrupamento de R-006
- [ ] T017 [US1] Acrescentar `fragmento_previa_da_classificacao` em `backend/processo_seletivo/interface/views.py` (autorização por `_edital_do_fragmento`, leitura por `forms.marco_do_formulario`, Etapas — com `weight`, `forma`, `order` e `name`, que `combinar` exige —, fatos declarados e quadro de vagas lidos do snapshot do rascunho por `publicacoes.application.publish_edital.edital_snapshot(edital)`, o mesmo que a etapa Classificação já monta em `views.py`; vagas por `classificacao.application.corte.linha_do_quadro(snapshot, perfil_id=…, lista_id=None)`. O snapshot se monta uma vez por pedido, e a contagem de consultas do fragmento fica presa por teste na T027) e as rotas `…/marco/<sub>/previa` e `…/previa/fechar` em `backend/processo_seletivo/interface/urls.py`
- [ ] T018 [US1] Teste de negativa em `backend/tests/authorization/test_classificacao.py`: ator sem escopo sobre o Edital recebe a mesma recusa dos demais fragmentos da composição, e sem sessão também (FR-2235); e classificar o 404 de Edital fora do escopo do fragmento novo em `specs/033-navegacao-por-capacidade/inventario-das-negativas.md` (o guardião `backend/tests/test_gramatica_das_portas.py` varre `views.py` por AST)
- [ ] T019 [US1] Criar `backend/processo_seletivo/interface/templates/interface/_previa_da_classificacao.html` (cabeça, resumo, tabela) e acrescentar o botão "Simular classificação" ao fim do cartão em `backend/processo_seletivo/interface/templates/interface/_marco.html`, só sob `POR_PONTUACAO`, com `hx-include="closest fieldset"` e `hx-target="#painel-da-previa"`
- [ ] T020 [US1] Acrescentar `<aside id="painel-da-previa">` e o `role="status"` do anúncio em `backend/processo_seletivo/interface/templates/interface/compor_classificacao.html`, irmãos da seção, fora de todo cartão
- [ ] T021 [P] [US1] Criar `backend/processo_seletivo/interface/static/interface/telas/previa-da-classificacao.css` a partir de `prototipo/estatico/prototipo.css` (só as regras do painel, com os tokens de `shared/tokens.css`) e carregá-la pelo bloco `estilo_da_pagina` de `compor_classificacao.html`; toda classe do template com regra na folha; nenhuma `}}` na mesma linha (guardião de `test_estaticos`)
- [ ] T022 [US1] Acrescentar `_previa_da_classificacao.html` à lista literal de `backend/tests/test_vocabulario_da_composicao.py` e conferir o vocabulário do painel contra o do cartão (FR-425 da `030`)

**Checkpoint**: US1 entregue — o elaborador abre a prévia e lê o porquê de cada posição.

---

## Phase 4: User Story 2 — Corte, progressão e recusas (Priority: P1)

**Goal**: situação no corte e consequência para a Etapa seguinte em cada linha; a recusa sob `STRICT`
como resultado; o aviso da fronteira das vagas.

**Independent Test**: a matriz do achado sai no painel igual ao que o motor produz.

### Tests for User Story 2

- [ ] T023 [P] [US2] Testes do painel em `backend/tests/interface/test_previa_da_classificacao.py` para os sete cenários de aceitação da US2: as três linhas do achado nos dois desfechos; "a última da faixa, e não a do alvo" só com suplentes; nenhuma linha "progride" sob recusa (FR-2215); o grupo empatado com a mesma marca (FR-2212); "progride para a Entrevista", corte terminal, continuação admitida, não admitida e não declarada (FR-2213); marco sem corte (FR-2219); nenhum estado de sucesso com recusa ou aviso (FR-2222)
- [ ] T024 [P] [US2] Teste de não-regressão do texto em `backend/tests/interface/test_previa_da_classificacao.py`: a opção `STRICT` do cartão continua "A faixa para no alvo" e `frases_do_corte` devolve as mesmas frases para o marco do achado (FR-2229); o painel diz "comportamento atual"

### Implementation for User Story 2

- [ ] T025 [US2] Implementar situação, consequência e os blocos do corte (saiu, recusado com o outro desfecho, sem desfecho, sem corte) e das vagas em `backend/processo_seletivo/interface/previa_da_classificacao.py` e no template do painel, com a cor âmbar da recusa (D-005)
- [ ] T026 [US2] Alvo do quadro: em `fragmento_previa_da_classificacao`, ler a linha geral por `linha_do_quadro(snapshot, perfil_id=…, lista_id=None)` sobre o `edital_snapshot` da T017 e dizer a origem; sem linha, `faltas` com "não apurável", nunca zero (FR-2218)

**Checkpoint**: US1 e US2 entregam o critério de sucesso do usuário sobre o que está digitado no clique.

---

## Phase 5: User Story 3 — Mudar um campo e ver o efeito sem salvar (Priority: P2)

**Goal**: recálculo a cada alteração, com os mesmos candidatos, e nenhum efeito persistente.

**Independent Test**: alterar cada campo do marco recalcula sobre o digitado; o banco não recebe escrita.

### Tests for User Story 3

- [ ] T027 [P] [US3] Testes em `backend/tests/interface/test_previa_da_classificacao.py`: o contêiner de recálculo inclui o cartão, o cenário e as fronteiras; trocar operação, critério ou desfecho mantém os candidatos; trocar alvo, suplentes ou vagas traz a frase de reposicionamento (FR-2206); campo apagado devolve 200 com o que falta (FR-2227); o número de consultas do fragmento é constante entre recálculos e preso por `django_assert_num_queries` (SC-841)
- [ ] T028 [P] [US3] Criar `backend/tests/integration/classificacao/test_previa_sem_efeito.py`: abrir, recalcular em todos os cenários, trocar cenário e fechar dentro de `CaptureQueriesContext` sem nenhum `INSERT`, `UPDATE` ou `DELETE`; contagem igual antes e depois em `Inscricao`, `ResultadoEtapa`, `ValorDeFato`, atos de ordenação, cortes, apurações e eventos de trilha; rascunho do Edital byte a byte igual (FR-2234, SC-843)

### Implementation for User Story 3

- [ ] T029 [US3] No template do painel, o contêiner com `hx-trigger="change from:#marco-<indice>-<sub>, input changed delay:400ms from:#marco-<indice>-<sub>"`, `hx-include` do cartão, do seletor de cenário e do campo oculto das fronteiras, e o estado "incompleto" (R-004)

---

## Phase 6: User Story 4 — Cenários predefinidos (Priority: P2)

**Goal**: escolher entre os cinco cenários; cada um diz o que mostra e quando não ocorre.

**Independent Test**: cada cenário, na configuração de referência, produz a situação que o nomeia.

- [ ] T030 [P] [US4] Testes dos cinco cenários de aceitação da US4 em `backend/tests/interface/test_previa_da_classificacao.py`, incluindo o trio sem critério por fato (dividem a posição) e "Classificação sem empate" dizendo que não houve empate em fronteira nenhuma
- [ ] T031 [US4] Seletor de cenário com `hx-get` próprio, descrição e âncora no painel, e as frases de "a situação não ocorre nesta configuração" (FR-2226) em `previa_da_classificacao.py` e no template

---

## Phase 7: User Story 5 — Celular e leitor de tela (Priority: P3)

**Goal**: 375 px sem rolagem horizontal; foco ao abrir e ao fechar; resumo anunciado.

**Independent Test**: a 375 px a jornada inteira sem rolagem horizontal; com leitor de tela, região
nomeada e resumo anunciado.

- [ ] T032 [P] [US5] Criar `backend/processo_seletivo/interface/static/interface/previa-da-classificacao.js` (foco no título ao abrir pelo botão, de volta ao botão ao fechar; nada no recálculo), carregado com `defer` em `compor_classificacao.html`; acrescentá-lo onde `backend/tests/test_javascript.py` e `backend/tests/javascript/` exigem
- [ ] T033 [P] [US5] Testes em `backend/tests/interface/test_previa_da_classificacao.py`: `aria-label` da região, `aria-controls` do botão, anúncio por `hx-swap-oob` fora do painel (FR-2236); nenhum `style=`, `<style>`, `<script>` inline nem `on*=` no HTML do painel e da etapa (FR-2237); a regra de 375 px pela folha, lida por CSSOM como em `backend/tests/interface/folha.py` (SC-846)

---

## Phase 8: Polish & Cross-Cutting

- [ ] T034 Completar `backend/tests/integration/classificacao/test_previa_equivale_ao_oficial.py` com a matriz da FR-2233 (classificação, posições compartilhadas, critérios em ordem, valor ausente, corte com e sem suplentes, `ADMITS_SURPLUS`, recusa por `STRICT`, recusa da fronteira das vagas): o lado oficial persiste o cenário (apoio da T003), emite a ordem pelo comando de `backend/processo_seletivo/classificacao/application/emissao.py`, corta por `calcular_corte` e apura por `titulares_iniciais` sobre `progrediram_em_ordem`; o lado da prévia chama `simular` com os mesmos dados; um comparador devolve as diferenças
- [ ] T035 Sentinela da equivalência no mesmo arquivo: com o caminho **oficial** alterado por `monkeypatch` — critério com sentido invertido em `calculo`, `+1` na faixa em `corte`, `ELIMINADA` trocada em `universo_classificavel` só do lado oficial —, o comparador de T034 devolve diferença em cada caso; e a tabela esperada do achado, absoluta, reprova se `faixa.calcular` mudar para os dois lados (FR-2233)
- [ ] T036 [P] Escrever `specs/094-previa-da-classificacao/rastreabilidade.md` com cada FR e SC → tarefa → teste, completando a versão do PR da spec
- [ ] T037 [P] Acrescentar a prévia ao `README.md` (seção da composição) e, em `CLAUDE.md`, a armadilha de que a prévia não grava nem lê inscrição real — só se a implementação a confirmar
- [ ] T038 `cd backend && make lint check test-pg` verde; depois o roteiro 2 de `quickstart.md` no navegador do app, em desktop e 375 px, com captura
- [ ] T039 Validação humana: o teste de uso da SC-840 com ao menos cinco elaboradores, registrado em `specs/094-previa-da-classificacao/validacao-de-uso.md`. Não é tarefa de código, e fica pendente até ser feita

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (1)**: sem dependência.
- **Motor (2)**: depende do Setup. T003 antes de T006/T007; T004 e T005 antes de T006 e T008; T010 antes
  de T011; T011 e T008 antes de T013; T012 antes de T013. **Bloqueia todas as histórias.**
- **US1 (3)**: depende do motor.
- **US2 (4)**: depende de US1 (o painel e a view existem).
- **US3 (5)**, **US4 (6)**, **US5 (7)**: dependem de US1; independentes entre si.
- **Polish (8)**: T034 e T035 dependem de T013; T038 depende de tudo.

### Within Each User Story

Testes primeiro, falhando; depois a implementação; o checkpoint fecha a história.

### Parallel Opportunities

- Fase 2: T004, T005 e T010 em paralelo (arquivos distintos), enquanto T003 é escrito.
- US1: T014, T015 e T021 em paralelo.
- Depois de US1: US3, US4 e US5 em paralelo, se houver mais de uma pessoa.
- Polish: T036 e T037 em paralelo com T034.

## Parallel Example: Fase 2

```text
Task: "T004 Testes unitários de preparar em backend/tests/unit/classificacao/test_universo_classificavel.py"
Task: "T005 Testes unitários de ordenar_com_trajetoria em backend/tests/unit/classificacao/test_ordenar_com_trajetoria.py"
Task: "T010 Testes de gerar em backend/tests/unit/classificacao/test_cenarios_da_previa.py"
```

## Implementation Strategy

### MVP

Fases 1, 2 e 3 (US1), mais a US2: juntas entregam o critério de sucesso do usuário sobre o que está
digitado no momento do clique. A US2 é P1 porque sem ela o painel poderia mostrar tudo verde onde o motor
recusa — e isso é pior que nenhuma prévia (FR-2222).

### Incremental

1. Motor (Fase 2) → a suíte inteira verde, o caminho oficial igual.
2. US1 + US2 → MVP; validar no navegador.
3. US3 → recálculo; US4 → cenários; US5 → celular e leitor de tela.
4. Polish → matriz de equivalência completa, sentinela, rastreabilidade, `make lint check test-pg`.

### O que esta spec não implementa

Sorteio (D-007), recortes, concomitância, ocupação além do aviso e reversão (fatia 2, D-008),
Retificação (D-009). Nenhuma das pendências DP-1 a DP-4 é decidida por tarefa alguma.
