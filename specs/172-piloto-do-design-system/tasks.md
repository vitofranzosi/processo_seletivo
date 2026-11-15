# Tasks: O piloto do design system em três telas

**Input**: Design documents from `/specs/172-piloto-do-design-system/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Estado em 15/11**: implementadas todas, menos a T041 (o ensaio do roteiro nas duas versões, que pede
alguém que conduza) e a T042 (as sessões com a equipe). Os desvios de cada uma estão no
[relatório](relatorio.md).

**Tests**: o aceite deste piloto é a fotografia, a comparação, o rastreio e a validação, e não
testes novos na suíte (D-009). As tarefas de teste abaixo são a jornada de fotografia (sob demanda)
e as passadas da suíte que já existe.

**Organization**: por história de usuário. A US1, a US2 e a US3 são independentes entre si depois da
fase 2, e cada uma termina com os estados dela fotografados e comparados. A US4 e a US5 dependem das
três.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode correr em paralelo (arquivos diferentes, sem dependência pendente)
- **[Story]**: a história da spec (US1 a US5)

## Path Conventions

- Produto: `backend/processo_seletivo/…`
- Testes e instrumento da fotografia: `backend/tests/…`
- Instrumento de comparação e resultados: `doc/auditoria-design-system-2026-11-14/piloto/…`
- Registros do piloto: `specs/172-piloto-do-design-system/…`

---

## Phase 1: Setup (levantamento, sem tocar o produto)

**Purpose**: saber de onde vem cada estado e o que pode quebrar, antes de escrever o instrumento.

- [x] T001 Criar `doc/auditoria-design-system-2026-11-14/piloto/README.md` com o que a pasta vai conter (antes, depois, comparação, scripts), o commit da `main` de que o piloto parte e o link para esta spec; acrescentar a linha da pasta à tabela de entregáveis de `doc/auditoria-design-system-2026-11-14/README.md`
- [x] T002 [P] Para cada um dos 63 códigos de D-004, achar a fixture ou o teste que monta o estado e o trecho literal que o prova, e registrar a tabela código → montagem → trecho → papel em `doc/auditoria-design-system-2026-11-14/piloto/README.md`; marcar os que pedem montagem nova a partir de helpers (C-07, C-08, O-03, K-01, L-08, L-12, entre os prováveis)
- [x] T003 [P] Confirmar por busca que `rascunho.js`, `remocao.js`, `visualizador.js` e `envio.js` não são carregados por `confirmar.html`, `ocupacao.html`, `ocupacao_acrescimo.html`, `ocupacao_nao_preenchida.html` e `lista.html`, e listar as classes dessas cinco telas que algum teste de `backend/tests/` procura por texto; registrar as duas listas em `doc/auditoria-design-system-2026-11-14/piloto/README.md`
- [x] T004 [P] Ler os seletores em que `backend/processo_seletivo/interface/static/interface/grupos/acesso.css` declara `--tinta`, `--linha`, `--fundo-p` e vizinhos, e como `test_contraste_atende_wcag_aa` obtém os pares; decidir se os tokens do piloto levam prefixo `--ds-` (research §3) e registrar a decisão no `README.md` da pasta do piloto

---

## Phase 2: Foundational (o instrumento, o "antes" e a fundação)

**Purpose**: a fotografia e a comparação funcionando sobre a `main`, o "antes" gravado, e a folha
vazia carregada pelos cinco templates sem diferença de conteúdo.

**⚠️ CRITICAL**: nenhuma tela muda de estilo antes do T013.

- [x] T005 Subir para `backend/tests/fixtures/ocupacao_da_tela.py` o corpo das fixtures locais que o catálogo precisa (`com_continuacao` e `sem_regra_de_corte` de `tests/interface/test_ocupacao.py`, `reserva` de `tests/interface/test_acrescimo.py`, `silente`, `reversao_que_nao_sai` e `prazo_encerrado` de `tests/interface/test_destinacao_na_ocupacao.py`), sem mudar o que montam, e fazer os arquivos de origem importá-las; rodar os três arquivos contra PostgreSQL e conferir o mesmo número de casos passando
- [x] T006 [P] Escrever o catálogo da confirmação, C-01 a C-12, em `backend/tests/navegador/piloto/confirmacao.py`, com montagem, papel, trecho de prova e ação principal de cada estado (data-model, *Estado do catálogo*)
- [x] T007 [P] Escrever o catálogo da Ocupação, O-01 a O-18 e os retornos R-01 a R-12 (com o gesto a clicar e os campos), em `backend/tests/navegador/piloto/ocupacao.py`
- [x] T008 [P] Escrever o catálogo das conferências, K-01 a K-09, em `backend/tests/navegador/piloto/conferencias.py`
- [x] T009 [P] Escrever o catálogo da Lista, L-01 a L-12, com a paginação de vinte por página e os vínculos de comissão, em `backend/tests/navegador/piloto/lista.py`
- [x] T010 Juntar os quatro catálogos em `backend/tests/navegador/piloto/estados.py` (com `__init__.py`), conferir que os 63 códigos são únicos, e medir, num banco local de rascunho, se dois cenários de ocupação montados em sequência colidem pelos identificadores fixos de linha (research §8); registrar o resultado e a saída escolhida no `README.md` da pasta do piloto
- [x] T011 Escrever a jornada `backend/tests/navegador/test_fotografia_do_piloto.py`: módulo que pula sem `PILOTO_DS_FOTOGRAFIA`; parametrizado pelos 63 códigos; entrada por `identificar` e `sessionid`, como `test_jornada_da_pagina_do_processo.py`; as cinco larguras e a dobra a 1280 × 800; a prova do estado antes de fotografar (FR-7718); o retorno praticado por clique; a captura e o inventário pela função de inventário do contrato ([contracts/inventario.md](contracts/inventario.md)), numa constante de texto do módulo; a vigia de CSP; a gravação em `<pasta>/<código>/<largura>.{png,json}` e o `fotografia.json`
- [x] T012 [P] Escrever `doc/auditoria-design-system-2026-11-14/piloto/scripts/sequencias.toml` com as sequências T-S1 a L-S5 da spec, cada termo identificado por trecho literal, e `doc/auditoria-design-system-2026-11-14/piloto/scripts/comparar.py`, que normaliza, compara e grava o resultado por estado e largura e o `resumo.md` (data-model, *Comparação*)
- [x] T013 Rodar a jornada sobre a branch sem nenhuma mudança de template ou folha (quickstart §1): os 63 casos passando; rodá-la de novo numa segunda pasta e comparar as duas com `comparar.py`, que deve dar zero diferença (valida a normalização e mede a linha de ruído das capturas); gravar os inventários e uma captura reduzida a 1440 px por estado em `doc/auditoria-design-system-2026-11-14/piloto/antes/`
- [x] T014 Acrescentar a `backend/processo_seletivo/shared/static/shared/tokens.css` os tokens da direção experimental (research §3, com o prefixo decidido no T004), sem mudar nenhum existente e sem `--t-*`; se o teste de contraste listar pares, acrescentar os novos à lista dele
- [x] T015 Criar `backend/processo_seletivo/interface/static/interface/grupos/piloto-ds.css` com o comentário de cabeçalho (o que é, por que o escopo, D-003) e a redeclaração da medida de leitura da P0 sob `.piloto-ds` (research §1, FR-7704); sem `}}` nem `%}`
- [x] T016 Abrir `<div class="piloto-ds">` logo depois de `{% block conteudo %}` e fechá-lo antes do `{% endblock %}`, e carregar a folha nova pelo `estilo_da_pagina`, em `backend/processo_seletivo/interface/templates/interface/confirmar.html`, `ocupacao.html`, `ocupacao_acrescimo.html`, `ocupacao_nao_preenchida.html` e `lista.html`; em `confirmar.html`, a folha da P0 antes da do piloto
- [x] T017 Acrescentar `interface/grupos/piloto-ds.css` com os cinco templates ao mapa de quem carrega cada folha em `backend/tests/interface/test_folha_estatica.py`, e rodar `backend/tests/interface/` contra PostgreSQL
- [x] T018 Fotografar os 63 estados de novo e comparar com o "antes": zero diferença de conteúdo, de ação e de sequência, e nenhuma linha acima de 80 nas confirmações (a medida da P0 viajou para dentro do escopo)

**Checkpoint**: o instrumento compara, o "antes" está gravado, e a fundação não mudou nada visível
além do que já era da P0.

---

## Phase 3: User Story 1 — Quem confirma um ato sabe o que vai acontecer (Priority: P1) 🎯 MVP

**Goal**: a confirmação de ato do Edital na composição centrada, com o cabeçalho de página, os avisos
como componente, as consequências em destaque e a barra de ações, nos sete atos.

**Independent Test**: os estados C-01 a C-12 passam na comparação, nas cinco larguras, e a
conferência manual de acessibilidade da confirmação está registrada.

- [x] T019 [US1] Escrever na folha `backend/processo_seletivo/interface/static/interface/grupos/piloto-ds.css` a seção da composição centrada (coluna de 44rem, prosa na medida de leitura), do cabeçalho de página, dos avisos de bloco com a marca de espécie, do cartão de consequências (irreversível e não) e da barra de ações ao pé, fixa só a 64rem ou mais e sem cobrir o foco (research §9; [contracts/escopo-da-folha.md](contracts/escopo-da-folha.md))
- [x] T020 [US1] Ajustar a marcação de `backend/processo_seletivo/interface/templates/interface/confirmar.html`: agrupar título e subtítulo no cabeçalho de página, e confirmar com prévia e "Cancelar e voltar" na barra de ações, sem mudar texto, classe existente, `role`, `id`, `name` nem a ordem C-S1 a C-S6, e sem tocar `_impedimento.html` nem `_escolha_da_autoridade.html`, que outras telas incluem (FR-7706): o escopo as estiliza de fora
- [x] T021 [US1] Fotografar C-01 a C-12 e comparar com o "antes"; corrigir a folha ou a marcação até os doze passarem nas cinco larguras (SC-2600, SC-2601, SC-2603, SC-2604)
- [x] T022 [US1] Conferir à mão, nos estados C-03, C-09, C-11 e C-12: tabulação igual à ordem visual, foco visível e não coberto, 320 px, zoom de 200% e 400%, recusa com o foco e o campo do motivo apontando para ela; registrar em `specs/172-piloto-do-design-system/relatorio.md` (FR-7724 a FR-7729)
- [x] T023 [US1] Rodar contra PostgreSQL `backend/tests/interface/test_confirmacao_do_encerramento.py` e os demais arquivos de `backend/tests/interface/` que abrem a confirmação, e corrigir o que um guardião acusar sem afrouxá-lo

**Checkpoint**: a confirmação nova está comparada e conferida, e já serve de MVP para mostrar à
equipe.

---

## Phase 4: User Story 2 — Quem apura a ocupação acha o número e o gesto (Priority: P1)

**Goal**: a Ocupação com os números em indicadores, o gesto junto do dado e, se as sequências
deixarem, o trilho; as duas conferências na composição centrada.

**Independent Test**: os estados O-01 a O-18, R-01 a R-12 e K-01 a K-09 passam na comparação, e a
conferência manual está registrada.

- [x] T024 [US2] Escrever na folha `backend/processo_seletivo/interface/static/interface/grupos/piloto-ds.css` a seção do indicador (`ul.resumo` dentro do escopo: número em destaque, rótulo embaixo, zero esmaecido), do recorte em cartão, do bloco de gesto (condição antes do botão) e da composição principal e trilho a partir de 80rem (UX-851, UX-852)
- [x] T025 [US2] Ajustar a marcação de `backend/processo_seletivo/interface/templates/interface/ocupacao.html`: cabeçalho de página, o bloco de gesto em volta de cada formulário com a ajuda dele, e o trilho só com o que passa pela O-S1 e pela O-S3 (research §9), sem tocar `_proximo_nesta_lista.html`, que outras telas incluem; se nada couber, ficar na composição cheia e registrar no `relatorio.md`
- [x] T026 [US2] Ajustar a marcação de `backend/processo_seletivo/interface/templates/interface/_situacao_da_vaga.html` (incluída só pela Ocupação, conferido em 15/11) para o bloco de gesto, sem mudar texto nem a posição dela no recorte (O-S4)
- [x] T027 [P] [US2] Ajustar a marcação de `backend/processo_seletivo/interface/templates/interface/ocupacao_acrescimo.html` para a composição centrada: os números em indicadores, a consequência em cartão e a barra de ações (K-S1 a K-S4)
- [x] T028 [P] [US2] Ajustar a marcação de `backend/processo_seletivo/interface/templates/interface/ocupacao_nao_preenchida.html` do mesmo modo, nos dois modos (declarar e desfazer) e no desfazimento que não cabe
- [x] T029 [US2] Fotografar O-01 a O-18, R-01 a R-12 e K-01 a K-09 e comparar com o "antes"; corrigir até os 39 passarem nas cinco larguras
- [x] T030 [US2] Conferir à mão, nos estados O-06, O-12, O-13, R-06 e K-01: tabulação, foco, 320 px, zoom, a recusa com o foco e os campos do acréscimo com rótulo associado; registrar no `specs/172-piloto-do-design-system/relatorio.md`
- [x] T031 [US2] Rodar contra PostgreSQL `backend/tests/interface/test_ocupacao.py`, `test_acrescimo.py`, `test_destinacao_na_ocupacao.py` e os demais arquivos que desenham a Ocupação (`07-fixtures-da-ocupacao.md` lista os treze)

**Checkpoint**: a Ocupação e as conferências comparadas e conferidas.

---

## Phase 5: User Story 3 — Quem abre a Lista acha o Processo e o trabalho dele (Priority: P2)

**Goal**: a Lista na composição cheia, com o cabeçalho de página, os segmentos, a barra de filtros e
os Processos como itens de lista num cartão, sem tabela e sem coluna nova.

**Independent Test**: os estados L-01 a L-12 passam na comparação, o orçamento de consultas da `129`
continua verde e a conferência manual está registrada.

- [x] T032 [US3] Escrever na folha `backend/processo_seletivo/interface/static/interface/grupos/piloto-ds.css` a seção da Lista: cabeçalho de página com a ação à direita, abas como segmentos com o traço que não depende de cor, a busca como barra de filtros, e o cartão com os Processos como itens de lista sem caixa por item (UX-853, D-011), sem tocar `telas/lista.css`
- [x] T033 [US3] Ajustar a marcação de `backend/processo_seletivo/interface/templates/interface/lista.html`: "Novo Processo Seletivo" no cabeçalho de página, e o cartão em volta da consulta, sem mudar a ordem L-S1 a L-S5 nem as classes da `129`; `_acoes_disponiveis.html` e `_paginacao.html` só a Lista inclui (conferido em 15/11) e podem receber marcação, e `_marca_da_retificacao.html`, que outra tela inclui, não muda (FR-7706)
- [x] T034 [US3] Rodar contra PostgreSQL `backend/tests/interface/test_lista.py` e `backend/tests/interface/test_organizacao_da_lista.py`, com o orçamento de consultas (FR-7713)
- [x] T035 [US3] Fotografar L-01 a L-12 e comparar com o "antes"; corrigir até os doze passarem nas cinco larguras
- [x] T036 [US3] Conferir à mão, nos estados L-01, L-05 e L-10: tabulação pelas abas, pela busca e pelos Processos, foco, 320 px e zoom; registrar no `specs/172-piloto-do-design-system/relatorio.md`

**Checkpoint**: as três telas prontas, comparadas e conferidas.

---

## Phase 6: User Story 5 — Nada fora do piloto mudou (Priority: P3)

**Goal**: a medida que confirma a delimitação, antes de mostrar à equipe.

**Independent Test**: o `telas.csv` da branch difere do da referência só nas linhas do piloto.

- [x] T037 [US5] Com o servidor `referencia-p0` servindo a branch sobre o `ps_p0_referencia` como ele está, rodar `doc/auditoria-design-system-2026-11-14/referencia-p0/scripts/rastrear_tudo.sh` (quickstart §3), comparar o `telas.csv` linha a linha com `doc/auditoria-design-system-2026-11-14/referencia-p0/telas.csv`, e sortear vinte telas de fora do piloto para comparar as capturas dentro da linha de ruído medida no T013; registrar no `specs/172-piloto-do-design-system/relatorio.md` (SC-2602)

---

## Phase 7: User Story 4 — A equipe faz as mesmas tarefas nas duas versões (Priority: P2)

**Goal**: a validação com a equipe, registrada por pessoa, tarefa e versão.

**Independent Test**: com as duas versões no ar, uma pessoa faz as seis tarefas nas duas, e o
registro sai preenchido.

- [x] T038 [US4] Escrever `doc/auditoria-design-system-2026-11-14/piloto/scripts/montar_banco_da_validacao.sh`: restaurar `ps_piloto_antiga` e `ps_piloto_nova` da cópia `ps_p0_referencia.dump`, acrescentar a cada um os Editais dos estados das tarefas V3 a V6 em duplicata pelas funções do catálogo, com a saída escolhida no T010, e conferir por consulta que cada um chegou ao estado (research §8, FR-7738). **Feito de outro modo:** um banco por tarefa, gravado por `tests/navegador/test_banco_da_validacao_do_piloto.py` e restaurado por este roteiro em `ps_piloto_validacao`; o banco da referência não tem os estados, e as fixtures supõem banco vazio (ver o relatório)
- [x] T039 [US4] Acrescentar ao `.claude/launch.json` as entradas `piloto-antiga` (porta 8167, de uma worktree na `main`, banco `ps_piloto_antiga`) e `piloto-nova` (porta 8168, esta branch, banco `ps_piloto_nova`), com `INTERFACE_SELETOR_IDENTIDADE=true`, sem sobrescrever as entradas existentes. **Feito nas portas 8172 e 8173** (a 8168 já era de outra entrada), as duas sobre `ps_piloto_validacao`, e a antiga numa worktree destacada da `main`, `piloto-172-antiga`
- [x] T040 [US4] Escrever `specs/172-piloto-do-design-system/validacao.md`: as seis tarefas V1 a V6 (research §11), com o Processo ou o Edital de cada versão, a identidade de entrada, as perguntas e o gabarito copiado do texto de cada tela, o roteiro de quem conduz (D-007, D-008) e a tabela de registro (data-model, *Registro da validação*)
- [ ] T041 [US4] Fazer um ensaio do roteiro nas duas versões, sem a equipe, e corrigir tarefa ambígua, gabarito que a tela não sustenta ou estado que não aparece
- [ ] T042 [US4] **Humano**: conduzir as sessões com duas ou três pessoas da equipe, metade começando por cada versão, e preencher o registro em `specs/172-piloto-do-design-system/validacao.md` com a pessoa em código (FR-7739)

---

## Phase 8: Polish & Cross-Cutting Concerns

- [x] T043 [P] Escrever `specs/172-piloto-do-design-system/levantamento-dos-guardioes.md`: para cada um dos cinco guardiões candidatos do `03-design-system.md`, o que ele acusaria nas cinco telas e na folha do piloto, hoje e depois, com as exceções que pediria (FR-7741), sem criar nenhum
- [x] T044 Escrever `specs/172-piloto-do-design-system/relatorio.md` até o fim: o resultado de cada SC, a comparação (link para `doc/auditoria-design-system-2026-11-14/piloto/comparacao/resumo.md`), a conferência manual, a ocupação da metade direita como diagnóstico (FR-7734), a validação e a resposta a cada uma das sete hipóteses do quadro *O que o piloto devolve para decisão* do `05-roadmap.md` (FR-7740, SC-2609)
- [x] T045 [P] Gravar em `doc/auditoria-design-system-2026-11-14/piloto/depois/` os inventários e a captura reduzida a 1440 px de cada estado, e em `doc/auditoria-design-system-2026-11-14/piloto/comparacao/` o resultado da comparação final
- [x] T046 Atualizar `CLAUDE.md` com o pulado a mais da jornada de fotografia (sem `PILOTO_DS_FOTOGRAFIA`) e com a nota de que o contêiner de escopo desfaz os seletores `main>` da folha da P0; atualizar a linha da `172` no `README.md`
- [x] T047 Rodar `cd backend && make lint check test-pg` e `uv run pytest tests/test_citacoes_de_requisito.py`; registrar o total de passando e de pulados no `relatorio.md` (SC-2608)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (fase 1)**: sem dependência. T002, T003 e T004 em paralelo, depois do T001.
- **Foundational (fase 2)**: depende da fase 1. Dentro dela: T005 antes de T007 e T008; T006 a T009
  em paralelo; T010 depois deles; T011 e T012 em paralelo depois do T010; **T013 antes de qualquer
  mudança de produto**; T014 a T017 depois do T013; T018 por último.
- **US1, US2 e US3 (fases 3 a 5)**: dependem da fase 2, e não umas das outras. As três escrevem na
  mesma folha, em seções separadas: em paralelo só se cada uma escrever a sua seção e o conflito de
  merge for resolvido por seção. Em série, a ordem é US1, US2, US3.
- **US5 (fase 6)**: depende das três telas. Vem antes da US4, porque não se mostra à equipe uma
  versão que vaza para fora do piloto.
- **US4 (fase 7)**: depende da US5. O T042 é humano, e o piloto espera por ele.
- **Polish (fase 8)**: o T043 pode começar com a US1; o T044 depende de tudo; o T047 é o último.

### User Story Dependencies

- **US1 (P1)**: independente, depois da fase 2. É o MVP.
- **US2 (P1)**: independente, depois da fase 2.
- **US3 (P2)**: independente, depois da fase 2.
- **US5 (P3)**: depende de US1, US2 e US3.
- **US4 (P2)**: depende de US5.

### Parallel Opportunities

- Fase 1: T002, T003, T004.
- Fase 2: T006, T007, T008, T009 (um arquivo de catálogo cada); T011 e T012.
- US2: T027 e T028 (templates diferentes).
- Polish: T043 e T045.

---

## Parallel Example: Phase 2

```bash
Task: "Catálogo da confirmação em backend/tests/navegador/piloto/confirmacao.py"
Task: "Catálogo da Ocupação em backend/tests/navegador/piloto/ocupacao.py"
Task: "Catálogo das conferências em backend/tests/navegador/piloto/conferencias.py"
Task: "Catálogo da Lista em backend/tests/navegador/piloto/lista.py"
```

## Parallel Example: User Story 2

```bash
Task: "Composição centrada em backend/processo_seletivo/interface/templates/interface/ocupacao_acrescimo.html"
Task: "Composição centrada em backend/processo_seletivo/interface/templates/interface/ocupacao_nao_preenchida.html"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Fase 1 e fase 2 inteiras: sem o "antes" gravado, nada do que vem depois é comparável.
2. Fase 3: a confirmação.
3. **Parar e conferir**: os doze estados passam, a acessibilidade está registrada. A confirmação nova
   já pode ser mostrada ao usuário.

### Incremental Delivery

1. Fundação, com o "antes" → confirmação (MVP) → Ocupação e conferências → Lista.
2. Rastreio sobre a referência → validação com a equipe → relatório.
3. Um PR por fase de tela é aceitável, desde que cada um traga a comparação dos estados dele. O
   relatório e a decisão sobre a migração são do fim.

### O que não se faz em nenhuma fase

- Mudar texto, classe existente ou seletor existente.
- Criar guardião, recolher texto, reduzir tamanho de fonte.
- Mexer nas confirmações do Processo e da Retificação, ou em `grupos/confirmacao-de-ato.css`.

---

## Rastreabilidade: requisito → tarefa

| Requisito | Tarefas |
|---|---|
| FR-7700, FR-7701 | T015, T016, T017 |
| FR-7702 | T015, T019, T024, T032, T037 |
| FR-7703 | T004, T014 |
| FR-7704 | T015, T018, T021 |
| FR-7705 | T019 |
| FR-7706 | T026, T037 |
| FR-7707 a FR-7711 | T011, T012, T018, T021, T029, T035 |
| FR-7712 | T019, T024, T032, T043 |
| FR-7713 | T034 |
| FR-7714, FR-7715 | T012, T021, T029, T035 |
| FR-7716 a FR-7720 | T011, T013, T018 |
| FR-7721 a FR-7723 | T011, T012 |
| FR-7724 a FR-7729 | T022, T030, T036 |
| FR-7730 a FR-7733 | T011, T021, T029, T035 |
| FR-7734 | T044 |
| FR-7735 | T040 |
| FR-7736, FR-7737 | T038, T039, T040, T042 |
| FR-7738 | T010, T038 |
| FR-7739 | T040, T042 |
| FR-7740 | T044 |
| FR-7741 | T043 |
| UX-850 | T019, T027, T028 |
| UX-851, UX-852 | T024, T025 |
| UX-853 | T032, T033 |
| UX-854 | T019 |
| UX-855 | T014 |
| SC-2600, SC-2601, SC-2603, SC-2604 | T021, T029, T035 |
| SC-2602 | T037 |
| SC-2605 | T022, T030, T036 |
| SC-2606, SC-2607 | T042, T044 |
| SC-2608 | T047 |
| SC-2609 | T044 |
