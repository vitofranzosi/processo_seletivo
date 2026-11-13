# Tasks: O limite do cadastro de reserva lido do corte

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/documento.md](contracts/documento.md),
[contracts/telas.md](contracts/telas.md), [quickstart.md](quickstart.md)

**Tests**: pedidos. Cada `FR-`, cada `SC-` e cada caso-limite tem teste, e o teste vem **antes** do
código: cada fase de testes roda e falha contra o código anterior antes da implementação dela
(Constituição, Princípio V).

**Caminhos**: relativos à raiz do repositório; `backend/` é o projeto Django.

**Banco**: `DB_NAME=ps_162` para a suíte (`TEST_DB_ENGINE=postgresql DB_USER=$(whoami)
DB_RUNTIME_USER=$(whoami)`), `ps_162_demo` para a demonstração.

**Testes que mudam de propósito**: os que esperam o número digitado em conteúdo **novo** —
`test_perfis.py` (unidade e integração), `test_campos_que_a_escolha_governa.py`,
`test_round_trip_do_rascunho.py`, `test_duplicar_perfil.py`, `test_cadastro_de_reserva_como_cr.py`,
`test_perfil_sem_vaga_imediata.py`, `test_redacao_das_frases.py`, `test_reserva_convocada_fora.py`,
`validacao.test.js`. Os que leem conteúdo **já publicado** — o corpus da `070`,
`contract/fixtures/snapshot_publicado.json` — **não** mudam: são o legado (T-012). Cada um muda na
tarefa que muda o comportamento, com a razão escrita no teste.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivo diferente, sem dependência pendente)
- **[Story]**: a história da spec (US1 a US5)

---

## Phase 1: Setup

- [X] T001 Medir o ponto de partida contra PostgreSQL (variáveis acima) sobre `backend/tests/unit/editais backend/tests/unit/publicacoes backend/tests/integration/editais backend/tests/integration/publicacoes backend/tests/interface backend/tests/portal backend/tests/unit/portal backend/tests/unit/test_visao_institucional.py`, e `node --test backend/tests/javascript`; verde, com o total registrado em `specs/162-limite-da-reserva-pelo-corte/verificacao.md` (novo), seção "Ponto de partida"
- [X] T002 [P] Em `backend/tests/fixtures/snapshot.py` (e no que `fixtures/selecao.py` e `fixtures/ocupacao.py` reusam), dois construtores: `perfil_com_cadastro(especie, *, vagas, alvo, excedente, continuacao, empate, quadro=None)`, que monta Perfil e marco que convoca coerentes, sem `reserveLimit`; e `perfil_legado(limite, ...)`, que monta o mesmo Perfil com `reserveLimit` digitado, para representar conteúdo publicado antes da feature

---

## Phase 2: Foundational — a derivação (T-001, T-002, T-005, T-006)

Bloqueia as cinco histórias.

### Testes (primeiro)

- [X] T003 [P] Em `backend/tests/unit/editais/test_cadastro_de_reserva.py` (novo), `do_perfil`:
  - alvo do quadro, excedente 3, 2 vagas → `por_lista` com 3, `numero_unico == 3` (FR-6929);
  - alvo fixo 4 + excedente 2, 0 vaga → 6; alvo fixo 2 + excedente 0, 2 vagas → 0; alvo fixo 1, 2 vagas → −1 (os dois últimos, para a FR-6936);
  - ampla 2, PcD 1, PPI 1, alvo fixo 3 → 1, 2, 2 com nomes e códigos, e `numero_unico is None` (FR-6941, `D-004`);
  - Perfil sem quadro: uma lista, a geral, com `immediateVacancies`;
  - marco intermediário ignorado: o corte que governa uma Etapa lida por outro marco não conta (FR-6929, a FR-4531 da `133`); o marco que governa Etapa que ninguém lê conta (o `seed_demo`);
  - dois marcos que convocam: a tupla do primeiro, e as divergências expostas (FR-6939);
  - `alcance_cresce` e `admite_empate` quando **algum** marco que convoca admite (T-005);
  - sem marco que convoca com corte → `por_lista` vazio (FR-6935);
  - `legado` com `LIMITED` + `reserveLimit` inteiro, `publicado` igual ao número, `por_lista` ainda calculado (T-002); `reserveLimit: 0` digitado também é legado
- [X] T004 [P] No mesmo arquivo, `descricao_curta` em todas as linhas da tabela D de [contracts/telas.md](contracts/telas.md), em algarismos, e `resumo_limitado` nas três formas de P

### Implementação

- [X] T005 Criar `backend/processo_seletivo/editais/domain/cadastro_de_reserva.py`, a regra única da FR-6930: `Cadastro` (dataclass congelada, campos da T-001), `do_perfil(perfil)`, `numero_unico`, `descricao_curta()`, `resumo_limitado()`; importa só `classificacao.domain.faixa` e `classificacao.domain.marco_intermediario`. Docstring de módulo no tom do repositório: o defeito (duas fontes, o exemplo de 13/11), a fonte única (`D-001`) e o legado pelo conteúdo (T-002)
- [X] T006 `_alcance_da_faixa` em `backend/processo_seletivo/editais/domain/validation.py` passa a ler o `Cadastro` (T-006), sem mudar a frase da FR-2474 da `097`; `backend/tests/unit/editais/test_reserva_convocada_fora.py` continua verde

**Checkpoint**: T003 e T004 verdes.

---

## Phase 3: User Story 1 — Quem elabora declara o limitado, e o número vem do corte (P1) 🎯 MVP

**Goal**: o número não se digita, a Revisão o mostra, e a publicação recusa o par incoerente.

**Independent Test**: o da US1 na spec — rascunho com 2 vagas, limitado, alvo do quadro, excedente 3: sem campo de número, Revisão com "Limitado: até 3"; com continuação, recusa.

### Testes (primeiro)

- [X] T007 [P] [US1] Em `backend/tests/unit/editais/test_coerencia_do_cadastro.py` (novo), `validate_for_publication`:
  - os cinco códigos da tabela R de [contracts/telas.md](contracts/telas.md), `BLOCKING_ERROR`, com Perfil e marco na frase, vocabulário do documento e caminho `/profiles/id={id}/reserveType` (FR-6933 a FR-6937, FR-6939, UX-726);
  - nenhum par coerente recusado: limitado sem continuação e número > 0; ilimitado com continuação; ilimitado sem corte; não há (SC-2300);
  - o 77/2026: "não há" com suplentes e continuação não é recusado (`D-006`);
  - recorte pelo ato: com `ATO_DE_RETIFICACAO`, só `reserve_limited_to_nobody` e `reserve_limited_divergent_milestones`, e nenhum dos cinco num Perfil legado (FR-6948, FR-6951)
- [X] T008 [P] [US1] Em `backend/tests/unit/editais/test_perfis.py`, `validate_profile` recusa `LIMITED` com número, com a frase de G e `campo="reserveLimit"`, e aceita `LIMITED` sem número (FR-6931); os casos atuais que exigiam número no limitado mudam, com a razão
- [X] T009 [P] [US1] Em `backend/tests/integration/editais/test_cadastro_de_reserva_na_publicacao.py` (novo):
  - `edital_snapshot` publica `reserveLimit: None` em `LIMITED` mesmo com `PerfilVaga.reserve_limit` preenchido (FR-6940, T-003);
  - a Revisão de rascunho com número digitado traz `reserve_limit_typed_in_draft` com o digitado e o derivado quando diferem, e nada quando coincidem (FR-6940);
  - duplicar (`043`) e reaproveitar (A-10) um Perfil legado gravam rascunho sem número, e a gravação não é recusada (FR-6931, T-003);
  - a API de rascunho com número em `LIMITED` responde a recusa de G (FR-6931)
- [X] T010 [P] [US1] Em `backend/tests/interface/test_cadastro_de_reserva.py` (novo), Etapa Perfis: sem `perfil-N-reserveLimit` no HTML; a linha de ajuda de P nos três casos (sem corte, número único, por lista) (FR-6932, UX-725); o POST do formulário com o campo antigo não o grava; a Revisão mostra "Cadastro Reserva" com `descricao_curta`; a publicação incoerente fica indisponível com a frase de R
- [X] T011 [P] [US1] Em `backend/tests/javascript/validacao.test.js` e `backend/tests/javascript/perfis.test.js`, `LIMITED` sem número é válido, e o resumo do cartão é o `data-resumo` da opção marcada (`limitado: até 3`), sem ler campo de número; rodar `node --test`

### Implementação

- [X] T012 [US1] `Cadastro.incoerencias(ato, rotulo)` em `cadastro_de_reserva.py` e a chamada em `validate_for_publication` (`backend/processo_seletivo/editais/domain/validation.py`), por Perfil, com o recorte da T-004
- [X] T013 [US1] `validate_profile` em `backend/processo_seletivo/editais/domain/perfis.py`: recusa de G (T-003)
- [X] T014 [US1] `edital_snapshot` em `backend/processo_seletivo/publicacoes/application/publish_edital.py`: `reserveLimit` sempre `None` em `LIMITED`, com o comentário do porquê (T-002, T-003)
- [X] T015 [US1] A advertência `reserve_limit_typed_in_draft`: `advertencias_do_numero_digitado(edital)` em `backend/processo_seletivo/editais/application/draft.py`, lida das linhas `PerfilVaga` do rascunho, com a frase de R; chamada por `_pendencias` em `backend/processo_seletivo/interface/views.py` (linha 1123), só antes da publicação, junto dos achados de `validate_for_publication` — *`replace_draft` também preserva o número digitado do Perfil que continua limitado, para a advertência não sumir na primeira regravação; a constraint `ck_perfil_reserve_limit_compatible` foi afrouxada na `editais/0028`*
- [X] T016 [P] [US1] `backend/processo_seletivo/editais/domain/duplicacao.py` e `backend/processo_seletivo/editais/domain/reaproveitamento.py`: a cópia zera `reserveLimit`
- [X] T017 [US1] Etapa Perfis: `backend/processo_seletivo/interface/forms.py` deixa de ler o campo (linhas 605, 637, 1068, 1298, 1397); `backend/processo_seletivo/interface/templates/interface/_perfil.html` troca o campo pela linha de ajuda de P, com a classe de ajuda que o fieldset já usa; o contexto da etapa entrega o `Cadastro` de cada Perfil; `backend/processo_seletivo/interface/views.py` e `templatetags/interface_extras.py` perdem a referência ao campo
- [X] T018 [P] [US1] `backend/processo_seletivo/interface/static/interface/validacao.js` deixa de exigir o número; `perfis.js` deixa de ler o campo e usa só o `data-resumo` da opção marcada, que `_perfil.html` escreve com `Cadastro.resumo_limitado()` (a tabela da etapa, `052`; FR-6930)
- [X] T019 [US1] A linha "Cadastro Reserva" de `backend/processo_seletivo/interface/revisao.py` (linha 98) usa `descricao_curta`
- [X] T020 [US1] `backend/processo_seletivo/processos/management/commands/seed_demo.py`: `DOC-INFO` sem `reserveLimit`; `TEC-LAB` com `continuation: "ALLOWED"`, com comentário do porquê (FR-6934, T-012)
- [X] T021 [US1] Corrigir as fixtures que **publicam** Perfil incoerente (rodar `backend/tests/unit/editais`, `backend/tests/unit/publicacoes`, `backend/tests/integration/editais`, `backend/tests/integration/publicacoes`, `backend/tests/interface`, `backend/tests/portal`), usando os construtores da T002; nunca afrouxar a regra; listar em `verificacao.md` cada arquivo mudado e o porquê

**Checkpoint**: T007 a T011 verdes; o `seed_demo` publica num banco vazio.

---

## Phase 4: User Story 2 — O documento não se contradiz (P1)

**Goal**: uma resposta só para "quantos podem ser chamados".

**Independent Test**: o da US2 na spec; os quatro exemplos de [contracts/documento.md](contracts/documento.md).

### Testes (primeiro)

- [X] T022 [P] [US2] Em `backend/tests/unit/publicacoes/test_cadastro_de_reserva_no_documento.py` (novo):
  - C1 em todas as linhas, inclusive o singular e o empate (FR-6938, FR-6941);
  - C2 nas três formas, e a redação 1 (T-007);
  - C3: limitado, limitado com N = 1, ilimitado com e sem alcance, e com Etapa governada (FR-6943); nenhuma abertura começa por "Seguem no processo" ou "Passam para" (SC-2299);
  - C4: as duas frases, e a de sem cadastro sai num Perfil sem cadastro mesmo com outro Perfil do Edital com cadastro (FR-6942);
  - os quatro exemplos de aceitação, frase por frase;
  - o legado: `perfil_legado(6)` imprime "até 6 (seis)" e a recomposição de um documento legado reproduz os bytes do número (FR-6944)
- [X] T023 [P] [US2] Em `backend/tests/unit/publicacoes/test_cadastro_de_reserva_no_documento.py`, o SC-2302: o documento composto dos Perfis do `seed_demo` e do Perfil só de reserva do exemplo de 13/11 tem **um** número para cada Perfil — nenhuma frase do corte com número diferente do cadastro, e nenhum "poderão ser chamados outros" num limitado

### Implementação

- [X] T024 [US2] `frase_do_cadastro` e `_reserva` em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` leem o `Cadastro` (C1, C2)
- [X] T025 [US2] `frases_do_corte(..., cadastro=None)` em `pdf.py`: a abertura de C3 e a frase de C4; `sem_cadastro` passa a ser do Perfil; atualizar o docstring (a DP-05 decidida) e a constante nova `SUPLENTES_DO_CADASTRO`; o texto de `SUPLENTES_SEM_CADASTRO` ("as vagas deste Edital") fica igual de propósito, para não mudar o documento de quem não tem cadastro, e o comentário diz isso
- [X] T026 [US2] Os três chamadores passam o `Cadastro` só no marco que convoca: `pdf.py` (linha 2594), `backend/processo_seletivo/publicacoes/infrastructure/apresentacao.py` (linhas 922 e 1142) e `backend/processo_seletivo/interface/revisao.py` (linha 643)
- [X] T027 [US2] Atualizar, com a razão, os testes de documento que esperavam o número digitado ou a omissão da frase dos suplentes (`test_cadastro_de_reserva_como_cr.py`, `test_perfil_sem_vaga_imediata.py`, `test_redacao_das_frases.py`, `test_redacao_no_documento.py`, `test_consolidacao_por_perfil.py`, `test_itens_do_documento.py`, `test_resumo_do_edital.py`, `test_pdf.py`)

**Checkpoint**: T022 e T023 verdes.

---

## Phase 5: User Story 3 — Todas as telas dizem o mesmo número (P2)

**Goal**: portal, relatório, visão institucional e assistente pela mesma regra.

**Independent Test**: o da US3 na spec; o SC-2298 sobre as fixtures e os cenários de treinamento.

### Testes (primeiro)

- [X] T028 [P] [US3] Em `backend/tests/unit/portal/test_situacao_da_inscricao.py` e `backend/tests/integration/portal/test_detalhe_selecao.py`, as linhas de O, inclusive o legado (FR-6945)
- [X] T029 [P] [US3] Em `backend/tests/interface/test_visao_geral.py`, `backend/tests/unit/test_visao_institucional.py` e `backend/tests/interface/test_relatorio.py`, `descricao_curta` nos três lugares, inclusive números por lista e o legado
- [X] T030 [P] [US3] Em `backend/tests/unit/duvidas/test_casos_da_revisao.py` (as respostas) e `backend/tests/unit/duvidas/test_cobertura.py`, o cartão de A: número derivado citando o `cutRule` do marco que convoca, e o legado citando `reserveLimit`; a cobertura reconhece o caminho novo (FR-6946)
- [X] T031 [US3] Em `backend/tests/unit/editais/test_cadastro_de_reserva.py`, o SC-2298 e a FR-6930: para cada Perfil limitado das fixtures da T002, o número do documento (C1), do portal (O), da Revisão, do relatório, da visão institucional e do assistente coincidem — *feito em partes: UD `test_um_numero_so_no_perfil_do_seed_demo` e os testes de UO e TI montam os mesmos Perfis; a comparação num só caso, pelas oito telas, não foi escrita*

### Implementação

- [X] T032 [P] [US3] `_oferta` em `backend/processo_seletivo/portal/views.py` e `frase_da_reserva` em `backend/processo_seletivo/portal/situacao.py` (O)
- [X] T033 [P] [US3] `_reserva` em `backend/processo_seletivo/interface/relatorio_do_edital.py` e `Reserva.do_perfil` em `backend/processo_seletivo/interface/visao_geral.py` (D)
- [X] T034 [P] [US3] `backend/processo_seletivo/duvidas/domain/respostas.py` (linha 229) e `backend/processo_seletivo/duvidas/domain/cobertura.py` (A)

**Checkpoint**: T028 a T031 verdes.

---

## Phase 6: User Story 4 — O legado não é reavaliado, e a ocupação não finge (P2)

**Goal**: a nota da FR-6947 nas duas telas da condução; nada publicado muda.

**Independent Test**: o da US4 na spec.

### Testes (primeiro)

- [X] T035 [P] [US4] Em `backend/tests/unit/ocupacao/test_nota_do_cadastro_legado.py` (novo), `nota_do_cadastro_legado`: as três frases de N, com número por lista; `None` no não legado e no ilimitado; a frase também quando o publicado coincide com o alcance (FR-6947, FR-6949)
- [X] T036 [P] [US4] Em `backend/tests/interface/test_cadastro_de_reserva.py`, a nota aparece como `<p class="nota">` na ocupação e na convocação do Perfil legado, e não aparece no não legado (UX-727) — *feito pela leitura do template (`test_a_nota_do_legado_e_nota_e_nao_alerta`) e pelo seletor (UN); a tela renderizada com Edital legado fica para o roteiro manual*
- [X] T037 [P] [US4] Em `backend/tests/integration/editais/test_cadastro_de_reserva_na_publicacao.py`, o SC-2301: um Edital legado publicado antes não recebe achado novo na Revisão de Retificação, não é republicado, e o documento recomposto é igual (FR-6944, FR-6948)

### Implementação

- [X] T038 [US4] `nota_do_cadastro_legado(conteudo, perfil_id)` em `backend/processo_seletivo/ocupacao/application/selectors.py` (T-009)
- [X] T039 [US4] As views da ocupação e da convocação em `backend/processo_seletivo/interface/views.py` entregam a nota; `backend/processo_seletivo/interface/templates/interface/ocupacao.html` e `convocacao.html` a desenham; a convocação a lê pela seta `convocacao → ocupacao` (`tests/test_dependencia_da_convocacao.py` verde)

**Checkpoint**: T035 a T037 verdes.

---

## Phase 7: User Story 5 — A Retificação muda o número pelo corte (P3)

**Goal**: o campo só no legado, a linha derivada, e a recusa do zero.

**Independent Test**: o da US5 na spec.

### Testes (primeiro)

- [X] T040 [P] [US5] Em `backend/tests/integration/publicacoes/test_cadastro_de_reserva_na_retificacao.py` (existe): no Perfil não legado, o campo do limite não é desenhado e não é aceito; no legado, continua retificável e a Retificação não é recusada pela regra nova (FR-6948, FR-6950)
- [X] T041 [P] [US5] No mesmo arquivo: retificar o excedente de 3 para 5 mostra a linha `Cadastro de reserva` com `Limitado: até 3` → `Limitado: até 5`, e o documento retificado diz 5 (FR-6950, SC-2303); levar o número a zero é recusado com `reserve_limited_to_nobody` (FR-6951)
- [X] T042 [P] [US5] O Perfil acrescentado por Retificação não tem o campo do limite e nasce sem número (T-003)

### Implementação

- [X] T043 [US5] `backend/processo_seletivo/interface/retificacao.py`: o campo de `CAMPOS_PERFIL` só no legado; `NOVO_PERFIL` e `_perfil_completo` sem ele; a linha derivada na conferência (T-010)

**Checkpoint**: T040 a T042 verdes.

---

## Phase 8: Polish & Cross-Cutting

- [X] T044 [P] `specs/162-limite-da-reserva-pelo-corte/rastreabilidade.md`: uma linha por `FR-`, `SC-`, `UX-` e caso-limite, com o teste que o prende; `**FR-6929**`, `**SC-2298**` e `**UX-725**` da faixa também
- [X] T045 [P] Atualizar a linha da `162` no `README.md` (de "Especificada" para o estado real) e o `Status` da spec
- [ ] T046 Rodar `quickstart.md` passos 2 a 5 num banco `ps_162_demo` novo, e registrar em `verificacao.md` o que se viu (PDF do `seed_demo`, recusa, nota, Retificação)
- [X] T047 `cd backend && make lint check test-pg` com `DB_NAME=ps_162`, uma suíte só no cluster; registrar o total em `verificacao.md` e comparar com o ponto de partida da T001, por lista e não por total
- [X] T048 Registrar em `verificacao.md` o que fica para o merge: a Visão do Sistema (`docs/visao-sistema/`) — o item da seção "O que ainda precisa evoluir" e as linhas "Onde ele aparece" do cadastro de reserva — e o SC-2304, humano

---

## Dependencies & Execution Order

- **Setup (T001–T002)** → **Foundational (T003–T006)** → as histórias.
- **US1** vem primeiro: as recusas mudam as fixtures (T021), e todas as outras fases rodam sobre fixtures coerentes.
- **US2** depende só da fundação, mas compartilha `revisao.py` com a US1 (T019, T026): fazer depois da US1.
- **US3**, **US4** e **US5** dependem da fundação e da US1; entre si são independentes.
- **Polish** por último.

## Parallel Opportunities

- T003 e T004; T007 a T011; T022 e T023; T028 a T030; T035 a T037; T040 a T042: arquivos diferentes, testes antes do código.
- T016 e T018 dentro da US1; T032 a T034 dentro da US3.
- Depois da US1, US3, US4 e US5 podem andar em paralelo.

## Implementation Strategy

**MVP = Foundational + US1 + US2.** É o que fecha as duas fontes e tira a contradição do documento: o
número deixa de ser digitado, a publicação recusa o incoerente, e o PDF diz um número só. US3 alinha as
telas que repetem o número; US4 é a honestidade com o acervo; US5 é a Retificação. Cada fase termina com
o diretório dela verde contra PostgreSQL, uma suíte de cada vez no cluster.
