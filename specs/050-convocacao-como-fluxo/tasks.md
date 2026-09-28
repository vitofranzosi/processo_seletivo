# Tasks: A convocação como fluxo

**Input**: [spec](spec.md), [plan](plan.md), [research](research.md), [data-model](data-model.md),
[contrato](contracts/convocacao-em-fluxo.md), [quickstart](quickstart.md).

**Tests**: pedidos — o projeto verifica cada requisito por teste, e a matriz de rastreabilidade os cita.

Caminhos relativos a `backend/`. `P` = `processo_seletivo/`.

## Phase 1: Setup

- [X] T001 Conferir o ambiente da worktree: `uv sync --extra dev`, `backend/.env` com `DB_NAME=ps050`, e `manage.py migrate --check` limpo.

## Phase 2: Foundational (domínio puro e as duas mudanças que tudo usa)

- [X] T002 [P] Acrescentar os códigos novos (`alcance_mudou`, `especie_divergente_da_posicao`, `nenhum_titular_a_convocar`, `nenhuma_convocacao_vencida`, `nenhuma_comunicacao_pendente`) e os motivos de a apuração seguinte não sair (`outra_causa_de_obsolescencia`, `moveria_vaga`) em `P/convocacao/domain/nomes.py`.
- [X] T003 [P] Escrever `P/convocacao/domain/especie.py`: a espécie pela posição — regularizável e fora dos alcançados → `PARA_REGULARIZAR`; no conjunto de ocupantes → `VAGA_INICIAL`; demais → `SUPLENCIA` (`D-008`), com testes em `tests/unit/convocacao/test_especie.py`.
- [X] T004 [P] Escrever `P/convocacao/domain/fundamento.py`: o texto derivado por espécie e o acréscimo do complemento (`D-009`), sem as palavras proibidas pela varredura da `019`, com testes em `tests/unit/convocacao/test_fundamento.py`.
- [X] T005 [P] Escrever `P/convocacao/domain/alcance.py`: `titulares_do_comeco_da_fila(fila, ocupando)` devolvendo o prefixo e a parada; `vencidas(linhas)` e `pendentes(linhas)` com as exclusões nomeadas; `assinatura(...)` por `canonical_sha256` (`D-001`, `D-007`), com testes em `tests/unit/convocacao/test_alcance.py`.
- [X] T006 Derivar a espécie em `P/convocacao/application/convocar.py` (espécie opcional; divergente recusada com `especie_divergente_da_posicao`), e deixar a fixture `tests/fixtures/convocacao.py::convocar` derivar em vez de fixar `VAGA_INICIAL`; testes em `tests/integration/convocacao/test_especie_derivada.py` (`FR-867`, `FR-868`).
- [X] T007 Escrever `emitir_sucessora_por_efeito` em `P/ocupacao/application/emissao.py`: calcula como `emitir_apuracao`, **dentro** da transação de quem chama, sem `comando_de_comissao`; devolve `None` quando cederia vaga, e grava com o motivo e o autor recebidos. `emitir_apuracao` passa a usar o mesmo cálculo (`D-005`).
- [X] T008 Extrair de `P/convocacao/application/desfechar.py` o registro de um desfecho (`_registrar`) e acrescentar, no fim de `desfechar`, a tentativa da apuração seguinte num *savepoint*: só quando as causas depois do efeito são só `efeito_posterior`; o resultado declara `apuracao` ou `apuracaoPendente` (`D-005`, `D-013`).
- [X] T009 Ajustar os testes da `019` que desfechavam e esperavam obsolescência ou emitiam a apuração à mão (`tests/integration/convocacao/*`, `tests/interface/test_convocacao.py`), conferindo um a um que o comportamento mudou pela `D-005`; e escrever `tests/integration/convocacao/test_apuracao_seguinte.py`: sucessora emitida; outra causa não emite; reversão não emite nem grava movimento; recusa da emissão preserva o desfecho (`FR-882` a `FR-885`).

**Checkpoint**: suíte da convocação e da ocupação verde.

## Phase 3: User Story 1 - Convocar os titulares num ato só (P1) 🎯 MVP

**Goal**: um gesto convoca e comunica os titulares ainda não chamados. **Independent Test**: US1 da spec.

- [X] T010 [US1] Escrever `previa_dos_titulares` e `convocar_titulares` em `P/convocacao/application/fluxo.py`: leitura única do recorte, alcance pelo `alcance.py`, impedimentos (sem apuração, obsoleta, sem forma, esgotada), assinatura conferida sob a trava, N `Convocacao` com as recusas de `convocar` simuladas em sequência sobre o mesmo contexto, trilha com `correlation_id = convocacao-lote-<chave>` e a origem do vencimento; depois do `commit`, `comunicar` por pessoa com chave derivada (`FR-860` a `FR-866`, `FR-871` a `FR-873`, `FR-875`).
- [X] T011 [US1] Testes de integração em `tests/integration/convocacao/test_titulares_em_lote.py`: 5 titulares e 3 suplentes; assinatura divergente recusa sem gravar; repetição idempotente sem reenvio; falha de envio não desfaz; publicação deixa prazo não iniciado; sem forma recusa; vencimento passado recusa; reabilitado fora da contagem para o gesto; cadastro de reserva não alcança ninguém; ator sem base de comissão recebe 404 nos três gestos (`SC-320`, `SC-321`, `SC-324`, `SC-325`, `FR-887`, `FR-889`).
- [X] T012 [US1] Rota e view `convocar_titulares_view` em `P/interface/urls.py` e `P/interface/views.py`; a GET de `convocacao` passa a prévia, os Eventos do Cronograma com fim futuro e a chave; `alcance_mudou` volta com a prévia nova (`UX-104`).
- [X] T013 [US1] Seção *"Convocar os titulares"* em `P/interface/templates/interface/convocacao.html`: lista na ordem com espécie e origem, parada nomeada, vencimento (data ou Evento), fundamento por extenso, complemento, botão com o número; resultado que conta convocações, envios e falhas (`UX-100` a `UX-103`).
- [X] T014 [US1] Testes da tela em `tests/interface/test_convocacao_em_fluxo.py`: prévia sem ato, confirmação, recusa por alcance, resultado.

## Phase 4: User Story 2 - Espécie, vencimento e fundamento deixam de ser digitados (P1)

- [X] T015 [US2] Escrever `convocar_e_comunicar` em `P/convocacao/application/fluxo.py`: fundamento derivado mais complemento, vencimento com origem, espécie derivada, comunicação depois do `commit` com chave derivada; antecipa `vencimento_anterior_ao_envio` na mensagem individual (`FR-869`, `FR-870`, `FR-871`).
- [X] T016 [US2] A view `convocar_view` passa por `convocar_e_comunicar`; o formulário individual e o de regularizar em `convocacao.html` perdem o seletor de espécie e o fundamento em branco, e ganham a espécie derivada no rótulo da pessoa, o fundamento por extenso e o complemento (`UX-101`).
- [X] T017 [US2] Testes em `tests/interface/test_convocacao_em_fluxo.py` e `tests/integration/convocacao/test_especie_derivada.py` *(o arquivo `test_individual_em_fluxo.py` não foi criado: os casos couberam nesses dois)*: a tela não pergunta a espécie; o registro guarda o texto mostrado; a comunicação sai no mesmo ato.

## Phase 5: User Story 3 - O não atendimento de todos os vencidos (P2)

- [X] T018 [US3] Escrever `previa_dos_vencidos` e `registrar_nao_atendimento_dos_vencidos` em `P/convocacao/application/fluxo.py`, pelo `_registrar` de `desfechar` N vezes e uma tentativa de apuração seguinte no fim (`FR-877` a `FR-880`, `D-013`).
- [X] T019 [US3] Rota, view e seção *"Não atendimento dos vencidos"* em `urls.py`, `views.py` e `convocacao.html`: lista, exclusões contadas, fundamento derivado, botão com o número; resultado com a apuração seguinte ou o motivo de ela não sair.
- [X] T020 [US3] Testes em `tests/integration/convocacao/test_nao_atendimento_em_lote.py` e na tela: 3 vencidas, 1 em curso, 1 não iniciada; desfecho individual depois da prévia recusa; linhas iguais às do individual; correlação comum (`SC-322`).

## Phase 6: User Story 4 - A apuração seguinte deixa de ser passo à mão (P2)

- [X] T021 [US4] A tela mostra, no resultado de todo desfecho, a apuração emitida ou o motivo de não sair — com o encaminhamento à ocupação quando moveria vaga (`FR-885`); a frase de sucesso do desfecho em `convocacao.html` deixa de afirmar obsolescência.
- [X] T022 [US4] Teste de ponta a ponta — feito em `test_nao_atendimento_em_lote.py::test_o_gesto_emite_a_apuracao_seguinte_e_a_suplente_e_a_proxima` e no `test_ciclo_do_77.py` revisto, sem arquivo próprio: titulares em lote → vencimento → não atendimento em lote → suplente convocado sem visitar a ocupação (`SC-323`, `SC-327`).

## Phase 7: User Story 5 - O suplente um a um, sem formulário por dentro (P3)

- [X] T023 [US5] Comunicações pendentes (servem também aos cenários 4 e 6 da US1): `previa_das_pendentes` e `emitir_pendentes` em `fluxo.py`, rota, view e seção em `convocacao.html` — mensagem individual reemite; publicação pede uma referência (`FR-874`, `FR-876`, `D-012`), com testes em `test_titulares_em_lote.py::test_por_publicacao_o_prazo_espera_a_referencia` e `test_convocacao_em_fluxo.py::test_as_comunicacoes_que_falharam_sao_reemitidas_num_gesto`.
- [X] T024 [US5] Teste do suplente na tela: espécie *"para vaga que vagou"* derivada; único campo o vencimento; nenhum suplente na prévia do gesto.

## Phase 8: Polish

- [X] T025 [P] Teste de custo em `tests/performance/test_convocacao.py`: prévia dos titulares com 5 e com 85 pessoas no mesmo número de consultas (`SC-326`, `FR-888`).
- [X] T026 [P] Incluir `fluxo.py`, `especie.py`, `fundamento.py` e `alcance.py` na lista `DA_019` de `tests/test_vocabulario_da_convocacao.py`.
- [X] T027 [P] Registrar a decisão da `DP-16` em `doc/decisoes-pendentes-da-consolidacao.md` (bloco *"O que foi decidido"*, índice e situação).
- [X] T028 [P] Escrever `specs/050-convocacao-como-fluxo/rastreabilidade.md`, com uma linha por requisito, critério, UX e caso-limite.
- [ ] T029 `make lint check` e `make DB_NAME=ps050 test-pg`; conferir falhas e pulados contra a linha de base do `CLAUDE.md`.
- [ ] T030 Percurso no preview (quickstart), com captura de tela como prova.

## Dependencies

- Phase 2 bloqueia tudo. T006 antes de T010 e T015; T007 → T008 → T009.
- US1 e US2 compartilham `fluxo.py` e o template: fazer em sequência. US3 depende de T008. US4 depende
  de T008 e T018. US5 depende de T015.

## Parallel Opportunities

T002–T005 entre si; T025–T028 entre si.

## Implementation Strategy

MVP = Phases 1–3. Depois US2 (mesma tela), US3 e US4 (o laço dos vencidos), US5, e o polimento.
