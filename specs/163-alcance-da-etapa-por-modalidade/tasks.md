# Tasks: O alcance da Etapa por Modalidade

**Input**: `specs/163-alcance-da-etapa-por-modalidade/` — spec, plan, research, data-model, contracts

**Tests**: obrigatórios neste repositório (Constituição, V): cada história tem os seus, e a matriz
`rastreabilidade.md` liga cada FR e cada caso-limite a teste.

Caminhos relativos a `backend/`. `[P]` = arquivo distinto, sem dependência de tarefa aberta.

## Phase 1: Setup

- [ ] T001 Conferir o ambiente da worktree: `uv sync --extra dev`, `DB_NAME` próprio, `manage.py migrate --check` limpo (CLAUDE.md, *Subir o ambiente*)

## Phase 2: Foundational (bloqueia todas as histórias)

- [ ] T002 Acrescentar `alcance = JSONField(null=True, blank=True)` e `ck_etapa_alcance_nao_vazio` a `EtapaAvaliacao`, com o comentário do porquê, em `processo_seletivo/editais/models/etapas.py`; reescrever a docstring que adiava a mudança
- [ ] T003 Gerar `processo_seletivo/editais/migrations/0029_alcance_da_etapa.py` e atualizar a contagem de migrations por app que o guardião da `022` cobra
- [ ] T004 [P] Criar `processo_seletivo/editais/domain/alcance.py` (`codigos`, `restrita`, `alcanca`, `modalidades_alcancadas`, `descrever`, `frase_do_alcance`) — research T-003, T-010
- [ ] T005 [P] Testes de unidade de `alcance.py` em `tests/unit/editais/test_alcance_da_etapa.py`: `None` = todas; ampla nunca alcançada por restrita; código só em alguns Perfis; ordem das denominações; frase vazia para todas
- [ ] T006 `SCHEMA_VERSION = 22` com o parágrafo do degrau em `processo_seletivo/shared/canonical.py`; `DEGRAUS[22] = {"modalityCodes": None}` em `processo_seletivo/publicacoes/domain/elevacao.py`
- [ ] T007 `"modalityCodes"` (lista ordenada ou `None`) em `_stages` de `processo_seletivo/publicacoes/application/publish_edital.py`
- [ ] T008 `("stages", "modalityCodes"): retificavel()` com o comentário da D-006 em `processo_seletivo/editais/domain/mutabilidade.py`; o campo no Edital máximo da fixture do guardião, para que ele seja enumerado (SC-2314)
- [ ] T009 Ajustar os testes de elevação e de versão canônica que fixam o número 21 (`tests/**/test_elevacao_de_versao.py` e semelhantes) e confirmar que o acervo de fixture recompõe o mesmo resumo (SC-2310)

**Checkpoint**: o campo existe, viaja no conteúdo publicado e o acervo não muda.

## Phase 3: User Story 1 — Quem elabora declara a quem a Etapa se aplica (P1)

**Goal**: declarar, validar, publicar e ler o alcance. **Independent test**: compor e publicar o Edital de três Perfis; conferir conteúdo, Revisão e documento.

- [ ] T010 [P] [US1] Testes em `tests/integration/editais/test_publicacao_do_alcance.py`: gravação recusa lista vazia e código repetido (FR-6962); aviso de código inexistente no rascunho e impedimento na publicação (FR-6963); os seis papéis proibidos (FR-6964); denominação divergente (FR-6965); Etapa sem alcance publica `modalityCodes: null` (FR-6961, FR-6966)
- [ ] T011 [US1] `validate_stage` aceita e confere `modalityCodes` em `processo_seletivo/editais/domain/etapas.py` (contrato `recusas.md`)
- [ ] T012 [US1] Gravar e ler o alcance no rascunho em `processo_seletivo/editais/application/draft.py`, e o aviso de código inexistente em `_pendencias`
- [ ] T013 [P] [US1] O campo na API de rascunho em `processo_seletivo/editais/api/serializers.py` e no `openapi.yaml` da feature que o descreve
- [ ] T014 [US1] Os achados `alcance_codigo_inexistente`, `alcance_em_papel_de_todos` e `alcance_denominacao_divergente` em `processo_seletivo/editais/domain/validation.py`, reaproveitando a coerência de denominação da `044`
- [ ] T015 [P] [US1] O alcance na cópia do Edital em `processo_seletivo/editais/domain/reaproveitamento.py` (e na duplicação, se ela não passar por ali)
- [ ] T016 [US1] A composição: grupo "A quem a Etapa se aplica" no formulário e no template (`processo_seletivo/interface/forms.py`, `templates/interface/_etapa.html`), `static/interface/alcance.js` e regras em `static/interface/telas/compor-etapas.css` (UX-730, UX-731)
- [ ] T017 [US1] A linha do alcance na Revisão (`processo_seletivo/interface/revisao.py`) e na página pública (`processo_seletivo/publicacoes/infrastructure/apresentacao.py`) (FR-6984)
- [ ] T018 [US1] A frase do alcance no documento, nas três redações, em `processo_seletivo/publicacoes/infrastructure/pdf.py` (FR-6983)
- [ ] T019 [P] [US1] Testes de interface e de documento: `tests/interface/test_composicao_do_alcance.py` (opções, lista de códigos com Perfis, CSP) e a frase no PDF composto, ausente na Etapa para todas

**Checkpoint**: US1 verificável sozinha.

## Phase 4: User Story 2 — Só as inscrições alcançadas passam pela Etapa (P1)

**Goal**: a quarta regra de participação. **Independent test**: 30 inscrições, 12 `PPI`; distribuir, concluir e consolidar.

- [ ] T020 [P] [US2] Testes em `tests/integration/resultados/test_operacao_com_alcance.py`: distribuição e atribuição individual recusam `AC` (FR-6973); Ocorrência e conclusão recusam (FR-6975); panorama com `fora-do-alcance` e total de alcançadas (FR-6976); consolidação só cria Resultado para alcançadas; Etapa sem alcançados não bloqueia a Etapa seguinte nem a publicabilidade do marco que a enumera (FR-6977); concomitância lê a Modalidade declarada (FR-6969); a faixa de um marco continua restringindo uma Etapa universal posterior a uma restrita (FR-6974)
- [ ] T021 [US2] Quarta regra em `restringir_a_participantes`, `participa_da_etapa` e `participacao_detalhada`; estado `FORA_DO_ALCANCE` e motivo em `motivo_de_nao_participar`, em `processo_seletivo/resultados/application/prontidao.py` (research T-004)
- [ ] T022 [US2] "«n» inscrições alcançadas, de «m»" e "Nenhuma inscrição alcançada" no panorama da Etapa (distribuição, Mesa, andamento), em `processo_seletivo/interface/andamento.py`, nas views e nos templates que desenham o panorama (UX-732, FR-6978)
- [ ] T023 [US2] Conferir que os orçamentos de consulta da `011`, da `012` e da `015` continuam passando sem alteração

## Phase 5: User Story 3 — Quem não é alcançado atravessa a Etapa (P1)

**Goal**: progressão e universo da ordem. **Independent test**: Prova consolidada, Heteroidentificação sem Resultado; a `AC` participa da Análise documental.

- [ ] T024 [P] [US3] Testes em `tests/unit/resultados/test_participacao_por_alcance.py` e `tests/integration/classificacao/test_universo_com_alcance.py`: gate lido na anterior que alcança, com duas restritas seguidas (FR-6972, SC-2312); universo da ordem com a restrita como última enumerada (FR-6985)
- [ ] T025 [US3] `etapa_anterior_que_alcanca` em `processo_seletivo/resultados/domain/progressao.py`, e `_anteriores_e_gate` devolvendo os casos da exigência, em `prontidao.py` (research T-005)
- [ ] T026 [US3] `_universo` pela última enumerada que alcança em `processo_seletivo/classificacao/application/calculo.py` (research T-006)
- [ ] T027 [P] [US3] Testes em `tests/integration/divulgacao/test_inscricoes_com_alcance.py`: a restrita fora das candidatas a Etapa de análise e recusada se escolhida (FR-6987); reingresso fora do alcance não pendente (FR-6986)
- [ ] T028 [US3] A Etapa de análise em `processo_seletivo/divulgacao/application/inscricoes.py`; o reingresso em `processo_seletivo/divulgacao/domain/publicabilidade.py`

## Phase 6: User Story 4 — O candidato vê só os passos que são dele (P2)

- [ ] T029 [US4] Teste em `tests/integration/portal/` de que o acompanhamento da `AC` não mostra a Etapa restrita e o da `PPI` a mostra; e de que Edital sem restrita não muda (FR-6982). Código só se o teste acusar.

## Phase 7: User Story 5 — A Retificação muda o alcance (P2)

- [ ] T030 [P] [US5] Testes em `tests/integration/publicacoes/test_retificacao_do_alcance.py`: ampliar passa e cria pendentes (FR-6979); estreitar sem Atribuição passa; com Atribuição ou Resultado é recusado (FR-6980, SC-2313); "todas" → restrita com `AC` atribuída é recusado; ato histórico lido pela versão citada (FR-6981); a participação lê o alcance da versão vigente no ato, antes e depois da Retificação que amplia (FR-6970); serialização com a distribuição (cenário 6)
- [ ] T031 [US5] `_recusar_alcance_estreitado_sobre_atribuicao` na gravação e na publicação da Retificação, em `processo_seletivo/publicacoes/application/retificacoes.py` (research T-008)
- [ ] T032 [US5] `select_for_update` no Edital antes de ler a participação, em `processo_seletivo/avaliacoes/application/distribuicao.py`
- [ ] T033 [US5] `modalityCodes` em `CAMPOS_ETAPA`, com o tipo de campo `ALCANCE`, em `processo_seletivo/interface/retificacao.py` e no template da tela; atualizar o teste de contrato que guarda a lista (research T-009); as alterações de Etapa em `publicacoes/domain/alteracoes.py` e `colecoes.py`, se o campo novo pedir

## Phase 8: Polish

- [ ] T034 `rastreabilidade.md` com uma linha por FR-, SC- e UX- desta spec, inclusive os números de abertura
- [ ] T035 Varreduras: `test_citacoes_de_requisito`, `test_acessibilidade` (classe com regra), `test_estaticos`, inventário de negativas da `033` se nascer `Http404`
- [ ] T036 `make lint check test-pg`, uma suíte por vez; atualizar o CLAUDE.md só se o número de pulados ou falhas mudar
- [ ] T037 Atualizar o status da spec e as notas do checklist

## Dependencies

- Phase 2 bloqueia todas as histórias.
- US1 (Phase 3) e US2 (Phase 4) dependem só da Phase 2; US3 depende da US2 (mesmo arquivo, `prontidao.py`).
- US4 depende da US2. US5 depende da US1 (o campo) e da US2 (a participação que a recusa conta).
- Phase 8 por último.

## Parallel examples

- Phase 2: T004 e T005 em paralelo com T006–T008.
- US1: T010, T013, T015 e T019 em paralelo com T011–T012.
- US3: T024 e T027 em paralelo; T028 independe de T025–T026.

## Implementation strategy

MVP = Phase 2 + US1 + US2 + US3: sem as três, um Edital publicado com Etapa restrita trava a ampla. A
US4 é verificação, e a US5 fecha a mutabilidade. Um PR, três commits (A: Phase 2 + US1; B: US2–US4;
C: US5 + Polish), como o `plan.md` diz.
