# Tasks: A confirmação de "Encerrar Processo" adverte as providências em aberto dos Editais (130)

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/confirmacao-do-processo.md](contracts/confirmacao-do-processo.md),
[quickstart.md](quickstart.md)

**Tests**: a spec os pede (SC-1320 a SC-1327). Em cada fase, os testes vêm antes da implementação e
devem falhar primeiro. Toda a suíte roda contra PostgreSQL, com `DB_NAME=ps_130` (CLAUDE.md).

**Convenções**: caminhos relativos à raiz do repositório. `encerramento.py` é
`backend/processo_seletivo/interface/encerramento.py`. A view é `praticar_ato_processo`, em
`backend/processo_seletivo/interface/views.py`. O template é
`backend/processo_seletivo/interface/templates/interface/processo_confirmar.html`.

## Phase 1: Setup

- [X] T001 Conferir que a branch está atualizada com a `main` (`gh pr view 421 --json state,mergeable`; se preciso, sincronizar) e que `uv run python backend/manage.py migrate --check` não acusa migration pendente com `DB_NAME=ps_130`
- [X] T002 Medir e anotar, antes de qualquer mudança, o número de consultas do GET do detalhe do Processo (`interface:processo-detalhe`) e da lista de Processos (`interface:lista`) com `CaptureQueriesContext`, sobre `montar_cenario(final="pendente")`, para o T023. Rodar também a linha de base de `backend/tests/interface/test_processo.py`, `backend/tests/interface/test_confirmacao_do_encerramento.py` e `backend/tests/performance/test_confirmacao_do_encerramento.py` contra PostgreSQL e anotar o resultado, para o `verificacao.md`

## Phase 2: Foundational — a composição (R-1, R-2, R-3, R-5)

**Bloqueia todas as histórias.**

- [X] T003 [P] Testes unitários em `backend/tests/unit/interface/test_advertencia_do_processo.py`:
  - o guardião exaustivo, em que toda constante de tipo de `pendencias_do_edital` (os nomes em maiúsculas cujo valor é igual ao nome, menos as espécies `IMPEDIMENTO` e `ADVERTENCIA`) está em exatamente um de `TIPOS_NO_PROCESSO`, `TIPOS_FORA_DO_PROCESSO` e `DA_099`;
  - o resumo: a mesma lista dá o mesmo resumo, uma mensagem diferente dá outro, a ordem dos Editais muda o resumo, a lista vazia tem resumo e os URLs não entram;
  - `convocado_no_prazo` só com item `CONVOCACAO_AGUARDANDO` (R-2, R-5, UX-276).
- [X] T004 Em `encerramento.py`:
  - acrescentar `tipo: str = ""` ao `Item`;
  - fazer `_item` preencher `tipo=situacao.tipo` e `_providencias_da_099` preencher `tipo=pendencia.tipo`, sem mudar mensagem, URL nem rótulo;
  - conferir que `backend/tests/interface/test_confirmacao_do_encerramento.py` continua passando (o `Item` não é comparado por igualdade fora do módulo; confirmar com `grep`).
- [X] T005 Em `encerramento.py`:
  - declarar `TIPOS_NO_PROCESSO` e `TIPOS_FORA_DO_PROCESSO` (data-model, *As constantes de tipo*), com um comentário que cita a D-002 e a D-003;
  - declarar os dataclasses congelados `GrupoDoEdital(edital, itens)` e `AdvertenciaDoProcesso(grupos, convocado_no_prazo, resumo)`, este com a propriedade `vazia`.
- [X] T006 `do_processo(processo, ator, *, agora)` em `encerramento.py`:
  - os Editais do Processo com `status__in=EDITAL_FINAL` e `Exists(Publicacao)`, ordenados por `year`, `number`, `id` (R-3);
  - para cada um, os itens de `p.situacoes(edital, agora=agora, ato="encerrar", com_advertencias=True)` filtrados por `TIPOS_NO_PROCESSO` e redigidos por `_item(..., "encerrar")`, seguidos de `_providencias_da_099(edital, agora)`;
  - grupo só quando há item (FR-4358);
  - o resumo por `hashlib.sha256` sobre `json.dumps([[str(edital.id), [mensagens]] ...], ensure_ascii=False, separators=(",", ":"))` (R-5);
  - docstring explicando que a função supõe `leitura_consistente` aberta, como `fatos_do_edital` (FR-4350, FR-4351, FR-4353).
- [X] T007 Fazer T003 passar.

**Checkpoint**: a composição existe e é testada sem tela.

## Phase 3: User Story 1 — o gestor vê o convocado que o encerramento vai cortar (P1) 🎯 MVP

**Goal**: na confirmação de "Encerrar Processo", o bloco com o Edital, a convocação e a frase da UX-276.

**Independent Test**: Processo Ativo com um Edital Encerrado e uma convocação no prazo
(`tests/fixtures/relatorio.montar_cenario(final="pendente")`); o GET mostra o bloco, e o POST com o
resumo encerra.

- [X] T008 [US1] Testes transacionais em `backend/tests/interface/test_advertencia_do_encerramento_do_processo.py`, com `seletor_ligado` e um gestor com `processo:encerrar`:
  - o GET mostra o título da UX-275, a frase de abertura, o grupo "N/AAAA — título" com link ao detalhe, a frase "… convocação aguardando resposta, até …." e a frase da UX-276, nesta ordem e antes de "Este ato não pode ser desfeito";
  - o POST com o resumo do contexto e um motivo dá 302, e o Processo fica Encerrado;
  - o único `AtoAdministrativo` novo é o de hoje, com o motivo e nada mais (FR-4350, FR-4363, UX-275, UX-276, SC-1320).
- [X] T009 [US1] Na view (GET), quando `acao == "encerrar"` e não há `recusa_certa`: chamar `encerramento.do_processo` dentro de `relatorio_do_edital.leitura_consistente()` e pôr `advertencia` no contexto. O bloco fecha antes de qualquer outra coisa (R-4, FR-4357, FR-4361).
- [X] T010 [US1] No template:
  - o bloco depois do aviso de recusa certa e antes de `consequencias`, só com `aviso`, `impedimentos` e `situacao s-…` (contrato, *O bloco*; R-8);
  - os itens como na tela do Edital: mensagem, e o link ou o a quem pedir;
  - o `<input type="hidden" name="resumo_das_providencias" value="{{ advertencia.resumo }}">` dentro do formulário, só quando há `advertencia`;
  - não mexer na linha do `<button>`.
- [X] T011 [US1] Fazer T008 passar. Conferir que `backend/tests/interface/test_paineis_e_telas_de_apoio.py` e `backend/tests/interface/test_politica_de_conteudo.py` passam (classes e CSP).

**Checkpoint**: o caso que motivou a feature está coberto.

## Phase 4: User Story 2 — todos os tipos da 113, por Edital (P1)

**Goal**: a advertência diz o que a confirmação do Edital diria, Edital a Edital, e nada além.

**Independent Test**: três Editais — encerrado com resultado não divulgado e recurso aguardando,
cancelado publicado com convocação vencida, cancelado antes de publicar —; os grupos e as frases
batem com as funções da `113` e da `099`.

- [X] T012 [US2] Testes em `backend/tests/interface/test_advertencia_do_encerramento_do_processo.py`:
  - a paridade (SC-1321): para cada grupo, as mensagens são exatamente as de `_item` sobre as situações de `TIPOS_NO_PROCESSO` mais as de `_providencias_da_099`, no mesmo `agora`;
  - toda providência de `fatos_do_edital(...).pendencias` nos tipos do `DA_099` aparece (FR-4354);
  - o Edital cancelado não tem frase de resultado;
  - o Edital nunca publicado não aparece, e o Edital final sem nada também não (FR-4358);
  - a ordem dos grupos é ano, número;
  - "Ir aos recursos" para quem julga e "Peça a quem julga recursos." para quem não julga (FR-4355);
  - nenhuma frase de período nem de Retificação, mesmo com o período sem término no conteúdo e uma Retificação em elaboração anterior ao encerramento do Edital (FR-4352, D-002);
  - um Edital encerrado por `tests/fixtures/encerramento.encerrar_antes_da_113` com recurso aguardando aparece como advertência, e o Confirmar continua oferecido (FR-4353, D-003);
  - um Processo com três Editais finais com providência mostra os três grupos, sem truncar (caso-limite *Muitos Editais*);
  - o título "Continuam depois do encerramento" não aparece na confirmação do Processo (UX-278);
  - o GET de "Cancelar Processo" no mesmo Processo não tem o título da UX-275 nem o campo `resumo_das_providencias` (FR-4364, SC-1325).
- [X] T013 [US2] Ajustar `do_processo` ou os cenários até T012 passar, sem mudar `pendencias_do_edital` nem `relatorio_do_edital` (FR-4364). Se um caso exigir mudar uma das duas, parar e registrar como achado.

## Phase 5: User Story 5 — a lista mudou depois que a tela abriu (P1)

**Goal**: o envio com a lista diferente reapresenta a confirmação sem encerrar (opção B).

**Independent Test**: abrir, criar uma convocação, enviar → 409, nada gravado; enviar de novo com o
resumo novo → 302.

- [X] T014 [US5] Testes em `backend/tests/interface/test_advertencia_do_encerramento_do_processo.py`:
  - a lista muda entre GET e POST (nova convocação, ou uma resposta registrada) → 409, Processo Ativo, nenhum `AtoAdministrativo` novo, a mensagem da UX-279, a lista atual, o resumo novo no formulário, o motivo de volta no `<textarea>` e a mesma `chave_idempotencia`;
  - o reenvio com o resumo novo → 302 e Processo Encerrado, mesmo com providência em aberto (FR-4366);
  - POST sem `resumo_das_providencias` → 409;
  - lista que muda e volta ao que era → 302 na primeira tentativa;
  - lista mudada e motivo vazio → 409 da renovação, e não 422;
  - um prazo de convocação que vence entre o GET e o POST (vencimento ajustado no banco para depois do GET e antes do POST) → 409, e a frase passa a "com prazo encerrado sem registro de resposta" (caso-limite *Prazo que vence*);
  - o "Cancelar Processo" com resumo ausente segue como hoje (FR-4365, FR-4366, UX-279, SC-1327).
- [X] T015 [US5] Na view (POST): quando `acao == "encerrar"` e a tela é confirmável, reler a advertência como em T009 e comparar com `request.POST.get("resumo_das_providencias")`. Se diferente ou ausente, renderizar com status 409, `renovada=True` e `motivo`, **sem** chamar o comando. A comparação vem antes da validação do motivo (R-6). Comentário citando a D-005 e a janela que fica; nenhuma frase da tela promete o contrário (FR-4367).
- [X] T016 [US5] No template: a mensagem da UX-279 com `class="aviso" role="status" tabindex="-1" autofocus`, antes do bloco, só com `renovada`; o `<textarea>` com `{{ motivo }}`.
- [X] T017 [US5] Ajustar o helper `ato()` em `backend/tests/interface/test_processo.py` para ler `context["advertencia"]` do GET e enviar o resumo quando existir (R-7); rodar o arquivo inteiro.

## Phase 6: User Story 3 — nada em aberto, sem prometer que acabou (P2)

**Goal**: a frase da UX-277 quando nenhum Edital tem providência.

**Independent Test**: `montar_cenario(final="sem-pendencia")`; abrir a confirmação.

- [X] T018 [US3] Testes: a frase da UX-277 inteira; ausência de "concluíd", "encerrad… a seleção" e "certame foi"; o resumo da lista vazia no formulário; o POST encerra na primeira tentativa (FR-4359, UX-277).
- [X] T019 [US3] No template: a frase da UX-277 no lugar do bloco quando `advertencia.vazia`, com `class="aviso" role="status"`.

## Phase 7: User Story 4 — a recusa por outro motivo reexibe a advertência atual (P2)

**Goal**: na recusa do comando ou do motivo, a lista volta relida, e só quando ainda confirmável.

**Independent Test**: enviar sem motivo; enviar com revisão vencida; enviar depois de retirar a permissão.

- [X] T020 [US4] Testes:
  - motivo vazio com o resumo certo → 422, "Motivo do encerramento é obrigatório." e o bloco;
  - depois de um 422, uma convocação nova faz o envio seguinte, já com motivo, voltar pela renovação (409), e não encerrar (história 4, cenário 2);
  - revisão vencida (outro ato no Processo entre GET e POST) → a recusa de hoje, com o bloco relido;
  - Processo já encerrado por outra sessão → sem bloco e sem Confirmar (FR-4357, FR-4360).
- [X] T021 [US4] No `except DomainError` da view: recalcular `pendentes`, `impedimento`, `recusa_certa` e, se confirmável, a advertência, dentro de `leitura_consistente()` (FR-4360, D-004).

## Phase 8: Polish & Cross-Cutting

- [X] T022 [P] Privacidade (SC-1323): no cenário `pendente`, varrer o HTML da confirmação contra o nome, o CPF, o e-mail e o protocolo de cada inscrição do cenário (FR-4356).
- [X] T023 [P] Desempenho em `backend/tests/performance/test_confirmacao_do_encerramento_do_processo.py`:
  - as consultas de `do_processo` com `montar_cenario(escala=1)` e `escala=10` são iguais, e o orçamento medido fica como constante, com a data;
  - com dois Editais, o número cresce pelo custo de um Edital (SC-1324, D-007);
  - o detalhe do Processo e a lista de Processos fazem o mesmo número de consultas que antes, comparado aos números anotados em T002.
- [X] T024 [P] Os textos novos (UX-275 a UX-277, UX-279) pela varredura de vocabulário. Se `processo_confirmar.html` não estiver na lista literal de nenhuma varredura, registrar no `verificacao.md` (memória *Varredura de vocabulário tem lista literal*).
- [X] T025 `cd backend && DB_NAME=ps_130 make lint check test-pg`; `migrate --check` sem migration nova (SC-1325, SC-1326). Se o teste de tempo da ocupação oscilar, medir isolado (CLAUDE.md).
- [X] T026 Capturas dos passos (a), (c) e (e) do quickstart em `specs/130-advertencia-no-encerramento-do-processo/capturas/`, num banco descartável montado pelos helpers dos testes.
- [X] T027 `specs/130-advertencia-no-encerramento-do-processo/rastreabilidade.md`, cobrindo FR-4350 a FR-4367, SC-1320 a SC-1327 e UX-275 a UX-279, e `verificacao.md`, com a linha de base, o teste ajustado (T017), os orçamentos e o resultado da suíte. Rodar `backend/tests/test_citacoes_de_requisito.py`.
- [X] T028 A linha da `130` no `README.md` passa a "Implementada"; rodar `backend/tests/test_readme_acompanha_o_codigo.py`.
- [X] T029 Revisão independente por subagente, com o diff e a spec, e não com as conclusões; corrigir os achados confirmados.
- [X] T030 Atualizar a descrição do PR #421 (conferir antes `gh pr view 421 --json state`) e conferir o CI.

## Dependencies & Execution Order

- **Phase 1 → Phase 2 → histórias.** T004 a T006 antes de qualquer tarefa de história.
- **US1 (Phase 3) antes de US5, US3 e US4**: as três mexem na mesma view e no mesmo template que T009 e T010 criam.
- **US2 (Phase 4)** só depende da Phase 2 e de T009 e T010, para ler pela tela. Pode correr em paralelo a US5 se ficar só no arquivo de teste.
- **US5 antes de US4**: T021 reaproveita a releitura de T015.
- **T017 junto de T015**: sem ele, `test_processo.py` cai assim que a renovação entra.
- **Polish** depois de todas as histórias. T022 a T024 são independentes entre si.

## Parallel Opportunities

- T003 (testes unitários) em paralelo a T004 e T005.
- T012, T014, T018 e T020 **não** são paralelos: são testes no mesmo arquivo, escritos em sequência, cada um antes da implementação da sua fase.
- T022, T023 e T024 em paralelo.

## Implementation Strategy

1. **MVP = Phase 2 + US1**: a convocação no prazo aparece antes do encerramento. Já reduz o risco que motivou a feature.
2. **+ US2**: a paridade com a `113` e a `099` impede que a advertência minta por omissão.
3. **+ US5**: a renovação fecha a janela de horas (esclarecimento de 06/11).
4. **+ US3, US4**: o caso vazio sem promessa e a reexibição.
5. **Polish**: privacidade, orçamento, suíte, capturas e documentos.

Commits por fase, com `ruff check` **e** `ruff format --check` antes de cada um.
