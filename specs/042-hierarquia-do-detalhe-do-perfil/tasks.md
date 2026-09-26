---

description: "Tarefas da 042 — a hierarquia do detalhe do Perfil"
---

# Tasks: A hierarquia do detalhe do Perfil

**Input**: Design documents from `specs/042-hierarquia-do-detalhe-do-perfil/`

**Prerequisites**: [plan.md](./plan.md) · [spec.md](./spec.md) · [research.md](./research.md) ·
[data-model.md](./data-model.md) · [contracts/](./contracts/) · [quickstart.md](./quickstart.md)

**Tests**: **incluídos**, e com uma ressalva que vale escrita: esta feature é **perceptiva**, e a
`SC-222` é julgamento humano. Os testes prendem as **consequências** — largura, colunas, ausência de
repetição, zero JavaScript —, e **não** substituem olhar a tela. Quem tratar a suíte verde como
prova de que a hierarquia melhorou não mediu a coisa.

**Organization**: uma história, e as trilhas do plano dentro dela.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode correr em paralelo — arquivo distinto, sem dependência pendente
- **[Story]**: `US1`; Setup, Foundational e Polish não têm rótulo

---

## Phase 1: Setup

**Purpose**: a linha de base. **Numa feature perceptiva ela não é formalidade** — sem as medidas de
antes, ninguém sabe se melhorou.

- [X] T001 Rodar `backend/tests/interface/test_visao_geral.py`, `backend/tests/unit/test_visao_institucional.py`, `backend/tests/interface/test_acessibilidade.py`, `backend/tests/interface/test_larguras.py` e `backend/tests/performance/test_visao_institucional.py`, e registrar a contagem
- [X] T002 Anotar as medidas de **antes** pelo trecho de console de `specs/042-hierarquia-do-detalhe-do-perfil/quickstart.md` §1 — largura da filha e da principal, os dois cabeçalhos, quantos `<tbody>`, e o recuo. *A máquina e a fonte variam; o que importa é a diferença, e ela precisa de um ponto de partida medido nesta máquina*

**Checkpoint**: linha de base verde e medida.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: o delta do módulo. Bloqueia as trilhas **C** e **D**; as demais são folha e template.

- [X] T003 [P] Acrescentar `rotulo` a `Marca` em `backend/processo_seletivo/interface/visao_geral.py` — o curto nasce junto com a mensagem, da mesma espécie, e **não** é derivado dela por corte de string (data-model §1, `R-006`)
- [X] T004 [P] Implementar `PerfilDaLinha.identidade_secundaria` em `backend/processo_seletivo/interface/visao_geral.py` — código, localidade e reserva, separados por `·`, **omitindo** o que não existe; vazia quando não há nenhum dos três (`FR-626`, `R-005`)
- [X] T005 Renomear as opções de `ORDENS` em `backend/processo_seletivo/interface/visao_geral.py` para que **nenhuma embuta direção** — *Data do Edital*, *Vagas*, *Inscrições submetidas*, *Inscr./vaga* —, **preservando as chaves** `recentes`, `vagas`, `submetidas`, `razao`: trocá-las quebraria endereços guardados sem ganho nenhum (`FR-630`, `R-007`)

**Checkpoint**: o módulo entrega o que a tela vai escrever; nada mudou na tela ainda.

---

## Phase 3: User Story 1 — O detalhe lê como aprofundamento da linha (P1) 🎯

**Goal**: a região expandida lê como subordinada ao Edital, e não como uma segunda tabela.

**Independent Test**: expandir um Edital e verificar que a região filha é recuada, mais estreita e
com cabeçalho mais leve — e que o controle tem marcador de divulgação.

### Tests for User Story 1 ⚠️

- [X] T006 [P] [US1] Testes da identidade secundária em `backend/tests/unit/test_visao_institucional.py` — a composição com os três, com dois, com um; **vazia** sem nenhum; e **sem texto de reserva** quando a espécie é nenhuma (`FR-626`, `SC-224`)
- [X] T007 [P] [US1] Teste do rótulo curto em `backend/tests/unit/test_visao_institucional.py` — cada espécie tem `rotulo` e `mensagem`, e os dois **diferem** (`FR-628`, data-model §1)
- [X] T008 [P] [US1] Teste do agrupamento em `backend/tests/interface/test_visao_geral.py` — **um `<tbody>` por Edital**, o caso vazio no seu próprio grupo, e o `<details>` continuando dentro do `<td>` (`R-002`)
- [X] T009 [P] [US1] Teste das colunas em `backend/tests/interface/test_visao_geral.py` — **seis** na região filha, uma de identidade e cinco de dado, e **nenhuma** de cadastro de reserva (`FR-627`, `SC-224`)
- [X] T010 [P] [US1] Teste da atenção em `backend/tests/interface/test_visao_geral.py` — a mesma frase **não** aparece nas duas granularidades: o Edital resume com denominador, o Perfil rotula (`FR-628`, `SC-225`)
- [X] T011 [P] [US1] Teste do controle e da legenda em `backend/tests/interface/test_visao_geral.py` — **zero** `<script>` novo, os **dois rótulos** no documento, e a legenda da tabela filha presente e **não** desenhada (`FR-622`, `FR-625`, `FR-629`, `SC-226`)
- [X] T012 [P] [US1] Teste dos controles de ordenação em `backend/tests/interface/test_visao_geral.py` — nenhum rótulo de critério embute direção, e as **chaves** `ordem` e `sentido` continuam as mesmas (`FR-630`, `SC-227`)

### Implementation for User Story 1

- [X] T013 [US1] **Trilha A** — abrir e fechar um `<tbody>` por Edital em `backend/processo_seletivo/interface/templates/interface/_linha_do_edital.html`, e dar grupo próprio à linha de recorte vazio em `backend/processo_seletivo/interface/templates/interface/visao_geral.html`
- [X] T014 [US1] **Trilha B** — régua à esquerda, recuo que deixa a região filha **mais estreita** que a principal (`FR-623`), cabeçalho da tabela filha tipograficamente **menos dominante** (`FR-624`) e legenda invisível (`FR-625`), no bloco `estilo_da_pagina` de `backend/processo_seletivo/interface/templates/interface/visao_geral.html`. *A largura menor é consequência do `padding-left` na célula, e nomeá-la é o que impede alguém de entregar a régua sem ela.* *Classe nova sem regra falha no guardião de classes órfãs — ele alcança o bloco de página e resolve `include` transitivamente desde a `041`*
- [X] T015 [US1] **Trilha B** — o comportamento em viewport estreito no mesmo bloco de `backend/processo_seletivo/interface/templates/interface/visao_geral.html`: a régua fica, o recuo encolhe, e a largura **não** é forçada (`FR-623`, `R-004`)
- [X] T016 [US1] **Trilha C** — escrever a identidade secundária e **remover as três colunas** de `backend/processo_seletivo/interface/templates/interface/_perfis_do_edital.html`. **No mesmo passo, corrigir `test_t013` em `backend/tests/interface/test_visao_geral.py`**, que afirma a coluna *"Cadastro de reserva"* — é a mesma armadilha do `tem_reserva` na `041`, e sem isto a fase quebra a linha de base que a `T001` acabou de medir
- [X] T017 [US1] **Trilha D** — o Perfil passa a usar o **rótulo curto** em `backend/processo_seletivo/interface/templates/interface/_perfis_do_edital.html`; o resumo do Edital em `backend/processo_seletivo/interface/templates/interface/_linha_do_edital.html` continua com o denominador
- [X] T018 [US1] **Trilha E** — o marcador de divulgação e os dois rótulos em `backend/processo_seletivo/interface/templates/interface/_perfis_do_edital.html` e na folha de `visao_geral.html`. *`display:inline-block` **apaga** o triângulo nativo — foi assim que o controle virou um botão de 67 px (`R-001`). O marcador é decoração e fica fora do nome acessível; o rótulo alterna por `details[open]`, e **nunca** por `content` de CSS (`R-003`)*
- [X] T019 [US1] **Trilha F** — os dois controles renomeados em `backend/processo_seletivo/interface/templates/interface/visao_geral.html`: **Ordenar por** e **Ordem**, com as chaves intactas

- [X] T020 [US1] **Anotar na `041` o critério que esta feature substitui**, em `specs/041-perfil-na-visao-institucional/spec.md`: a `SC-217`, citando o seu texto — *"as três espécies de cadastro de reserva são distinguíveis na tela, e a limitada diz o seu limite"* — e apontando para a `SC-224` desta (`FR-631`). *O requisito que manda substituir **não se autoexecuta**, e o guardião de citações fica verde do mesmo jeito, porque o identificador existe. É a terceira vez que este tipo escapa: na `041`, a substituição da `FR-602` teve tarefa e a da §11.1 não.*

**Checkpoint**: a região filha lê como filha. É a feature inteira.

---

## Phase 4: Polish & Cross-Cutting Concerns

- [X] T021 [P] Conferir que o orçamento de consulta **não mudou**, rodando `backend/tests/performance/test_visao_institucional.py`. *Esta feature não toca leitura nenhuma; número diferente ali é sinal de que o plano saiu do problema*
- [X] T022 [P] Conferir a varredura de dado pessoal de `backend/tests/interface/test_visao_geral.py` sobre o conteúdo expandido — a identidade do Perfil é conteúdo **publicado**, e nada de pessoa entra nela
- [X] T023 Conferir se a prosa visível de `backend/processo_seletivo/interface/templates/interface/_perfis_do_edital.html` usa *recorte*, *geração* ou *faixa*; usando, acrescentar a tela a `TELAS` em `backend/tests/test_vocabulario_da_composicao.py` **no mesmo commit**
- [X] T024 Medir as consequências no navegador contra o que a `T002` anotou, pelo trecho de `specs/042-hierarquia-do-detalhe-do-perfil/quickstart.md` §1 — filha **mais estreita**, cabeçalho **menor**, um `<tbody>` por Edital (`SC-223`)
- [X] T025 Percorrer os dezessete passos de `specs/042-hierarquia-do-detalhe-do-perfil/quickstart.md`, **incluindo o passo 16** — o juízo humano da `SC-222`, que nenhum teste substitui — e o **17**, no telefone
- [X] T026 Escrever `specs/042-hierarquia-do-detalhe-do-perfil/rastreabilidade.md` cobrindo **cada** `FR-622` a `FR-631` e `SC-222` a `SC-227`
- [X] T027 Rodar os alvos de `backend/Makefile` com `cd backend && make lint check test-pg` — `lint` são **dois** passos, e não editar arquivo durante a execução

---

## Dependencies & Execution Order

```text
Phase 1 (Setup)          ← T002 é medição, e é precondição da T024
   ↓
Phase 2 (Foundational)   ← T003/T004 em paralelo; T005 independente
   ↓
Phase 3 (US1)            ← T013..T019; a única história
   ↓
Phase 4 (Polish)
```

**Dentro da Fase 3**, as trilhas são quase independentes:

| Trilha | Depende de | Toca |
|---|---|---|
| **A** agrupamento | — | `_linha_do_edital.html` · `visao_geral.html` |
| **B** subordinação | **A** — a régua vive na célula que o grupo delimita | a folha |
| **C** identidade | `T004` | `_perfis_do_edital.html` |
| **D** atenção | `T003` | os dois parciais |
| **E** controle | — | `_perfis_do_edital.html` · a folha |
| **F** ordenação | `T005` | `visao_geral.html` |
| **—** a substituição | `T016` — só é verdade depois que a coluna sai | `specs/041-…/spec.md` |

**Duas ordens duras: A → B**, porque a régua vive na célula que o grupo delimita, **e T016 → T020**,
porque a substituição só é verdade depois que a coluna sai.

**As demais** podem ser feitas em qualquer sequência; **C** e **E** tocam o mesmo arquivo e não devem
correr juntas.

### Paralelismo por fase

| Fase | Podem correr juntas |
|---|---|
| 2 | `T003`, `T004` |
| 3 | `T006` a `T012` (os sete testes) |
| 4 | `T021`, `T022` |

---

## Implementation Strategy

**Uma história, e o MVP é ela.** Não há recorte menor que entregue a `SC-222`: metade da mudança —
régua sem cabeçalho leve, ou colunas reduzidas sem agrupamento — deixaria a região filha lendo como
irmã do mesmo jeito. **A hierarquia é o conjunto.**

**A ordem de risco:**

- **`T016`** é a que quebra a linha de base: remove a coluna que um teste da `041` afirma. Está
  nomeado ali, e é o mesmo tipo de armadilha que o `tem_reserva` foi.
- **`T018`** é a que erra pelo caminho oposto ao esperado: a correção de estilo mais natural —
  `display:inline-block`, para controlar a caixa — é **exatamente** o que apaga o marcador. Foi
  assim que a `041` o perdeu.
- **`T013`** muda a estrutura da tabela, e é onde um `<tbody>` mal fechado passa despercebido: o
  navegador conserta, e a suíte não olha. A `T008` existe por isso.
- **`T025`** é a que **não falha** quando esquecida: a suíte fica verde e a feature não é verificada
  no que ela existe para fazer.
