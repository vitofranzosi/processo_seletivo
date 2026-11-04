# Tasks: Referência da Loteria Federal conferida antes do compromisso

**Input**: Design documents from `specs/116-referencia-da-loteria-federal/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md),
[contracts/mensagens.md](contracts/mensagens.md)

**Tests**: pedidos pela spec, e escritos antes do código que cobrem. Cada teste novo precisa falhar
antes de passar. Nenhum teste acessa a Caixa (FR-3651). As respostas gravadas em 03/11/2026 são as
fixtures.

**Organization**:

- a Fase 2 é a base: fixtures, vigia de rede, regra pura, consulta do adaptador e orquestrador.
  Nenhuma tela entra nela;
- a US1 (publicação) e a US2 (congelamento) dependem só da Fase 2, e podem correr em paralelo porque
  não tocam os mesmos arquivos;
- a US3 (Caixa fora do ar) atravessa as duas e vem depois delas;
- a US4 (Retificação) depende da US1;
- a US5 (forma) depende só da Fase 2;
- a US6 (sob demanda) depende da Fase 2 e das mensagens da US1.

**Convenções**: textos e nomes em português; comentário explica por quê; nada de `style=`, `<style>`,
`<script>` nem `onclick=` em template; `ruff check` **e** `ruff format --check`. A verificação é
`cd backend && make lint check test-pg`, com `DB_NAME` próprio desta worktree.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente)
- **[Story]**: a história da spec que a tarefa serve (US1 a US6)

---

## Phase 1: Setup

- [ ] T001 Preparar a worktree:
  - `uv sync --extra dev` em `backend/`;
  - `backend/.env` a partir do `.env.example`, com `DB_NAME=ps_116`;
  - `make preparar`, conferindo que o `provisionar` informa `46 de 46` e não `0 de 46`;
  - `make test-pg` inteiro, anotando passando e pulados como linha de base da SC-1099.
- [ ] T002 Inventário (plan, §8). Para cada um dos 18 arquivos de `backend/tests/` que declaram
  `"source": "Loteria Federal"`, anotar em `verificacao.md` se o arquivo:
  - passa por `validate_for_publication`, `submit_edital`, `publish_edital`, `publish_retification`
    ou `publicar_relacao`;
  - compara a lista inteira de achados, e por isso verá o `INFO` novo.

  Fazer o mesmo com os casos que usam a fonte de demonstração e comparam a lista inteira. **Nenhuma
  expectativa muda nesta tarefa.**

---

## Phase 2: Foundational (bloqueia todas as histórias)

**Purpose**: as situações (FR-3627 a FR-3631), a consulta fora da transação (FR-3632), a
demonstração por tabela (FR-3650) e a suíte sem rede (FR-3651).

- [ ] T003 [P] Copiar `doc/estudo-extracao-da-loteria-federal-2026-11-03/respostas/` para
  `backend/tests/fixtures/caixa/`, e anotar no `README` da pasta a data da captura e o recorte feito
  (sem lotéricas, rateio e `stackTrace`).
- [ ] T004 [P] Em `backend/tests/conftest.py`, um *autouse* que:
  - substitui `LoteriaFederal.consultar_ultimo` e `consultar_data` por uma Caixa configurável, com
    padrão "último 6114, de 01/11/2026; nenhuma referência ≤ 6114 citada pela suíte é tratada como
    realizada" (plan, §8: sete casos declaram `6113`);
  - recusa, com mensagem clara, qualquer `urlopen` para `caixa.gov.br` quando
    `SORTEIO_E2E_FONTE_REAL` não estiver ligada.

  Escrever `backend/tests/test_suite_sem_caixa.py`, que prova a recusa (SC-1099).
- [ ] T005 [P] Escrever `backend/tests/unit/sorteios/test_conferencia.py`, sem banco, a matriz da POC
  adaptada:
  - **situação**: realizado (5000, 1, 6113, 6114), ainda não realizado (6115 anunciado, 6118, 6200,
    9999, 99999), realizado sem data, e referência inválida (`6106-9`, `Concurso 6115`, `6115/2026`,
    `0`, `000`, `-1`, vazio, `6114.0`, `abc`, `1234567`);
  - **decisão por ato**: a tabela das FR-3634 a FR-3637, incluindo a forma inválida que adverte no
    congelamento;
  - **mensagens**: as partes obrigatórias de `contracts/mensagens.md` por situação e ato;
    `test_ainda_nao_realizado_nunca_diz_validado_confirmado_ou_conferido` (SC-1095); o fuso
    institucional (FR-3642);
  - **registro**: `test_o_registro_responde_as_seis_perguntas_e_nada_da_resposta_crua` (FR-3647,
    FR-3648).
- [ ] T006 Criar `backend/processo_seletivo/sorteios/domain/conferencia.py`, pura (plan, §2), com
  docstring que diga o que a fonte afirma e o que não afirma. T005 verde.
- [ ] T007 [P] Escrever `backend/tests/integration/sorteios/test_consulta_da_fonte.py`, com
  `urlopen` substituído pelas fixtures da T003:
  - o último concurso válido, e a validação de *payload*: sem bilhetes, data em outro formato,
    `numero` como texto, HTML e 503 → `None`;
  - a data de um número, e o 500 da Caixa → `None`, nunca exceção;
  - **uma** tentativa por chamada, com o tempo limite de `SORTEIO_CONFERENCIA_TIMEOUT_SEGUNDOS`;
  - `observar` inalterado: três tentativas, os mesmos desfechos
    (`test_falha_de_acesso_a_fonte.py` intocado);
  - as fontes de demonstração respondem pela tabela (5000 realizado, 9998 inconclusivo, o resto
    ainda não realizado) e não abrem conexão;
  - em produção, as fontes de demonstração continuam fora do vocabulário.
- [ ] T008 Implementar na porta (`fontes/__init__.py`) e em `fontes/loteria_federal.py` (plan, §1):
  `FORMA_DA_REFERENCIA`, `SABE_CONFERIR`, `consultar_ultimo()`, `consultar_data(n)`, a tabela das
  demonstrações e `forma_da_referencia(nome)`. Acrescentar `SORTEIO_CONFERENCIA_TIMEOUT_SEGUNDOS` em
  `config/settings/base.py`, com padrão 5. T007 verde.
- [ ] T009 [P] Escrever `backend/tests/integration/sorteios/test_conferir_referencias.py`:
  - uma consulta principal por fonte, qualquer que seja o número de referências (FR-3631);
  - uma consulta por referência realizada distinta, e nenhuma para ainda não realizada;
  - fonte que não sabe conferir não é consultada e não aparece no resultado;
  - `referencias_a_conferir`: o método comum uma vez, o marco sem sorteio a fazer fora, e com `base`
    só as introduzidas (FR-3633, D-006).
- [ ] T010 Criar `backend/processo_seletivo/sorteios/application/conferencia.py` (plan, §3). T009
  verde.

**Checkpoint**: a conferência existe, testada, e ninguém a chama. A suíte inteira continua com o
total de T001.

---

## Phase 3: User Story 1 — A publicação recusa o concurso já realizado (Priority: P1) 🎯 MVP

**Goal**: submissão e publicação conferem e recusam (FR-3634, FR-3639, FR-3647).

**Independent Test**: o 5000 é recusado na submissão e na publicação, pela tela e pela API. O 6116
passa com a informação (SC-1094).

- [ ] T011 [P] [US1] Escrever `backend/tests/unit/editais/test_concurso_realizado.py`, sobre
  `validate_for_publication(..., situacoes=...)`:
  - realizado: impeditivo `draw_occurrence_already_drawn`, um por método, com o `path` do método;
  - inconclusivo: advertência; ainda não realizado: `INFO`;
  - `situacoes=None`: nenhum achado desta feature;
  - a `102` intacta: data inviável continua impeditiva, com qualquer situação (FR-3638).
- [ ] T012 [US1] Em `editais/domain/validation.py`, o parâmetro `situacoes` e os achados (plan, §4),
  ao lado de `_extracao_inviavel`. T011 verde.
- [ ] T013 [P] [US1] Escrever `backend/tests/integration/publicacoes/test_publicacao_confere_a_referencia.py`.
  Cenários:
  - **A**: 5000 com data futura, recusado na submissão;
  - o mesmo, homologado sob "ainda não realizado" e recusado na publicação depois que a Caixa
    gravada passa a dizer realizado;
  - **B**: 6116 passa, com a informação no registro;
  - **F**: o mesmo pela API (`publicacoes/api/views.py`);
  - **G**: dois marcos (6116 e 6113) e o método comum, com uma consulta principal e um impeditivo
    só no 6113;
  - `test_cada_comando_consulta_a_fonte`: guardião contra o `situacoes=None` esquecido;
  - repetição idempotente: sem nova consulta.
- [ ] T014 [US1] Em `publicacoes/application/publish_edital.py`, `submit_edital` e `publish_edital`
  conferem antes de `command_context()` e passam `situacoes`. Dentro, a referência do conteúdo travado
  sem situação vira inconclusiva (FR-3632). O registro vai em `record_event(..., detalhe=...)`, e o
  log estruturado registra a recusa (FR-3649). T013 verde.
- [ ] T015 [US1] Mostrar a informação e a advertência depois do ato, no detalhe do Edital (`?ato=`),
  lidas do `detalhe` do último registro do ato (FR-3646). Teste:
  `backend/tests/interface/test_desfecho_da_conferencia.py`, com classes novas com regra na folha da
  gestão.

**Checkpoint**: o incidente do concurso antigo não se repete na publicação com a Caixa respondendo.

---

## Phase 4: User Story 2 — O congelamento recusa o concurso já realizado (Priority: P1)

**Goal**: FR-3636, FR-3637, a mensagem de congelamento da FR-3639.

- [ ] T016 [P] [US2] Escrever `backend/tests/integration/sorteios/test_congelamento_confere_a_referencia.py`.
  Cenários:
  - **C**: publicado sob "ainda não realizado", realizado no congelamento: recusa, sem relação
    gravada, com a mensagem de congelamento;
  - ainda não realizado: congela, com o registro;
  - declarada já indisponível: sem consulta;
  - forma do acervo (`Concurso 6100`, inserida por fixture de conteúdo publicado): congela com
    advertência;
  - **H**: depois de congelada, a Caixa gravada muda de resposta. `metodo_hash`, relação e
    ocorrência observada não mudam, e o sorteio decide pela precedência, como antes;
  - repetição idempotente: sem nova consulta.
- [ ] T017 [US2] Em `sorteios/application/relacao.py`, a conferência antes de `comando_de_comissao`,
  a recusa, `advertencias` no dicionário devolvido e o `detalhe` do registro (plan, §4). T016 verde.
- [ ] T018 [US2] Em `interface/templates/interface/sorteio.html`, mostrar `advertencias` do
  desfecho guardado por `_desfecho_do_sorteio`. Teste em
  `backend/tests/interface/test_desfecho_da_conferencia.py`.

---

## Phase 5: User Story 3 — A Caixa fora do ar não paralisa (Priority: P1)

**Goal**: FR-3641, SC-1096, SC-1097.

- [ ] T019 [US3] Escrever `backend/tests/integration/test_caixa_fora_do_ar.py`, parametrizado pelas
  oito falhas da POC (tempo esgotado, `URLError`, 500, 503, HTML, sem bilhetes, data noutro formato,
  `numero` como texto) × os quatro atos. Em cada caso:
  - o ato conclui;
  - a advertência aparece com um dos quatro motivos do contrato;
  - o registro diz `conclusiva: false`;
  - nenhuma parte da resposta crua aparece.

  Mais um caso: a data inviável da `102` continua impedindo com a Caixa fora do ar. Mais
  `test_a_espera_com_a_fonte_que_dorme_nao_passa_de_quinze_segundos`.
- [ ] T020 [US3] Ajustes que a T019 apontar. O esperado é nenhum, se as Fases 2 a 4 seguiram o
  plano.

---

## Phase 6: User Story 4 — A Retificação confere só o que muda (Priority: P2)

- [ ] T021 [P] [US4] Escrever `backend/tests/integration/publicacoes/test_retificacao_confere_a_referencia.py`.
  Cenários:
  - troca para realizado: recusa;
  - **E**: só o cronograma muda num Edital com o 5000 consolidado: publicada, **zero** consultas
    (SC-1100);
  - marco sem sorteio a fazer: fora;
  - fonte trocada de demonstração para Loteria Federal: conferida;
  - troca para forma inválida: impeditivo;
  - inconclusivo: advertência.
- [ ] T022 [US4] Em `publicacoes/application/retificacoes.py`, `publish_retification` com
  `referencias_a_conferir(..., base=..., marcos_sorteados=...)` e `_assert_well_formed` recebendo as
  situações. T021 verde.

---

## Phase 7: User Story 5 — A forma errada é recusada na gravação (Priority: P2)

- [ ] T023 [P] [US5] Escrever `backend/tests/unit/editais/test_forma_da_referencia.py` e
  `backend/tests/integration/editais/test_normalizacao_da_referencia.py`:
  - as grafias da FR-3623 recusadas com a frase da FR-3626, pela tela e por `PUT /draft`;
  - `006114` gravado `6114`;
  - a fonte de demonstração aceita `Concurso 5900`;
  - a Retificação de acervo não reconfere a forma (a FR-514 da `035`).
- [ ] T024 [US5] Forma por fonte em `perfis._validar_forma_da_ocorrencia`, e a normalização em
  `editais/application/draft.py::replace_draft` (plan, §5). T023 verde.
- [ ] T025 [US5] Rótulo e ajuda do campo em `_marco.html` e `compor_classificacao.html` (FR-3643),
  com teste de presença do texto em `backend/tests/interface/test_metodo_do_marco.py`. Conferir a
  varredura de vocabulário da composição.

---

## Phase 8: User Story 6 — Conferir antes de agir (Priority: P3)

- [ ] T026 [P] [US6] Escrever `backend/tests/interface/test_conferencia_sob_demanda.py`:
  - o botão na composição (marco e comum) e na tela do sorteio antes de congelar;
  - a resposta com a mensagem de cada situação;
  - permissão negada por padrão;
  - nada gravado;
  - **renderizar as três telas não consulta a fonte** (FR-3644, SC-1097).
- [ ] T027 [US6] A rota `POST`, a view e o fragmento htmx (plan, §6), com recusa 200 e
  `HX-Retarget` e as classes com regra na folha. T026 verde.

---

## Phase 9: Polish

- [ ] T028 `backend/tests/interface/test_sorteio_com_a_fonte_de_producao.py`: substituir a
  conferência só enquanto `recuar_o_relogio` estiver ativo (plan, §8). Rodar uma vez com
  `SORTEIO_E2E_FONTE_REAL=1` e anotar o resultado em `verificacao.md` (FR-3651).
- [ ] T029 Aplicar o inventário da T002: ajustar só as expectativas listadas lá, cada uma com o
  porquê no commit.
- [ ] T030 `cd backend && make lint check test-pg`. Comparar com a linha de base da T001 por lista,
  e não por total. Registrar em `verificacao.md`.
- [ ] T031 Atualizar [rastreabilidade.md](rastreabilidade.md) com os nomes finais dos testes, e
  rodar `tests/test_citacoes_de_requisito.py`.
- [ ] T032 Roteiro local do plano (fonte de demonstração: 5000, 9998, 6200) no navegador, com
  captura das três mensagens em `verificacao.md`.

---

## Phase 10: User Story 7 — Reaproveitar não traz o concurso (Priority: P1, emenda de 04/11/2026)

**Goal**: FR-3715 a FR-3720, SC-1115, SC-1116, D-009. A revisão está em
[revisao-do-reaproveitamento.md](revisao-do-reaproveitamento.md).

- [ ] T033 [US7] Em `backend/tests/fixtures/legado.py`, `antes_da_116()`: o único contexto que
  desliga a forma e a conferência, para reconstituir acervo. `tests/fixtures/corpus.py` e os testes
  de acervo da `116` passam a usá-lo (FR-3720).
- [ ] T034 [P] [US7] Escrever `backend/tests/unit/editais/test_metodo_sem_a_extracao.py`: a gravação
  aceita o método sem os dois campos, recusa o que tem só um, e a publicação e a Retificação recusam
  os dois com a mensagem da FR-3717 (FR-3716, FR-3717).
- [ ] T035 [P] [US7] Escrever `backend/tests/integration/editais/test_reaproveitamento_sem_a_extracao.py`,
  pelo comando real `reaproveitar_edital`, sem o mecanismo da T033 no destino:
  - origem do corpus com `Concurso 6010`; origem com `6010`; método comum; métodos próprios; sem
    sorteio (SC-1115);
  - os campos estruturais iguais e a Etapa de habilitação do destino;
  - gravar outra etapa antes de declarar a extração;
  - submeter sem a extração: recusa com a indicação; validar a publicação: impeditivo;
  - declarar extração futura, submeter, homologar e publicar (SC-1116);
  - a origem intacta e retificável (FR-3719).
- [ ] T036 [US7] `payload_do_conteudo` sem a extração; `exigir_a_extracao` em
  `_validar_metodo_de_sorteio`; a mensagem própria; `referencias_a_conferir` sem método sem
  referência. T034 e T035 verdes.
- [ ] T037 [US7] A indicação na composição depois do reaproveitamento e o item em "O que não vem"
  (FR-3718). Teste em `backend/tests/interface/test_reaproveitar.py`.
- [ ] T038 [US7] `make lint check test-pg` inteiro, comparado com a T030 por lista, e
  [verificacao.md](verificacao.md) atualizado.

## Dependencies

- Fase 1 → Fase 2 → (US1 ∥ US2 ∥ US5) → US3 → US4 (depende de US1) → US6 → Polish.
- A US7 depende da US5 (a forma na gravação) e vem depois do Polish: é a emenda de 04/11/2026.
- A T004 vem antes de qualquer teste de integração das histórias: sem o vigia, um caso esquecido
  iria à rede.
