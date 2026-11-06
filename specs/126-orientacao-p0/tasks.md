# Tasks: Correções de orientação e segurança operacional depois da publicação (P0)

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/telas.md](contracts/telas.md)

**Tests**: pedidos (regressão para cada item). Escritos antes da implementação de cada história, e
vistos falhar.

Caminhos relativos a `backend/`.

## Phase 1: Setup

- [ ] T001 Confirmar a linha de base: `make lint check` verdes na worktree e `manage.py migrate --check` sem pendência, com `DB_NAME=ps_spec126` em `backend/.env` local (não versionado)

## Phase 2: Foundational

- [ ] T002 Implementar `recortes_sem_inscrito(edital, conteudo, perfil, marco, *, agora)` em `processo_seletivo/interface/conducao_do_marco.py` (R-2, D-002): vazio quando o marco não sorteia ou as inscrições correm; senão, os recortes sem elegível (sem filtro de habilitação) e sem relação vigente
- [ ] T003 [P] Acrescentar a regra `.sucessao` (details recolhido, summary com aparência de ação secundária) em `processo_seletivo/interface/static/interface/gestao/telas.css`, sem `}}` na mesma linha

**Checkpoint**: a função de sem inscrito existe e a classe tem regra na folha.

## Phase 3: User Story 1 — Sucessão recolhida e mensagens que dizem o que foi feito (P1) 🎯 MVP

**Goal**: depois do ato, a sucessão vem recolhida com nome próprio, e a mensagem nomeia o recorte e os números.

**Independent Test**: emitir corte, ordem, apuração e relação e conferir que nenhum botão de sucessão está visível fora de um `details`, e que as mensagens nomeiam o recorte.

- [ ] T004 [P] [US1] Testes de A1 em `tests/interface/test_orientacao_p0.py`: corte, ordem, ocupação e sorteio com ato vigente têm o formulário de sucessão dentro de `details.sucessao` com o rótulo do contrato; aberto quando obsoleto; primeira emissão fora do bloco; mensagens de sucesso com recorte e números
- [ ] T005 [US1] Corte: separar a primeira emissão da sucessão, envolver a sucessão em `details.sucessao` (aberto com `corte_obsoleto`), e reescrever a mensagem de sucesso (corte, sucessão, faixa seguinte) em `processo_seletivo/interface/templates/interface/corte.html`; marcar `acao` da faixa seguinte em `continuar_corte_view` de `processo_seletivo/interface/views.py`
- [ ] T006 [US1] Ordem: envolver o formulário em `details.sucessao` quando há `ato_vigente` (aberto com `obsoleto`) em `processo_seletivo/interface/templates/interface/ordenacao.html`; contar posições do ato emitido em `emitir_ordenacao` (`views.py`) e reescrever a mensagem
- [ ] T007 [US1] Ocupação: envolver "Emitir nova apuração" em `details.sucessao` (aberto com `OBSOLETE`) em `processo_seletivo/interface/templates/interface/ocupacao.html`; guardar `listaId` no resultado em `emitir_apuracao_view` e achar o rótulo em `ocupacao` (`views.py`); reescrever a mensagem
- [ ] T008 [US1] Sorteio: envolver "Publicar relação nova, sucedendo a atual" em `details.sucessao` (aberto com diagnóstico) em `processo_seletivo/interface/templates/interface/sorteio.html`; guardar `listaId` em `publicar_relacao_do_sorteio` (`views.py`) e nomear o recorte na mensagem
- [ ] T009 [US1] Atualizar as instruções da anulação que dizem "no formulário logo abaixo desta caixa" para mencionar o bloco "Suceder esta relação" em `sorteio.html`

**Checkpoint**: US1 verde isolada.

## Phase 4: User Story 2 — Lista sem inscrito não aparece como pendência (P1)

**Goal**: *Não se aplica* na condução, na conferência dos gestos, na convocação e na ocupação; a faixa seguinte só com corte.

**Independent Test**: marco de sorteio com lista sem inscrito e inscrições encerradas.

- [ ] T010 [P] [US2] Testes unitários de `recortes_sem_inscrito` em `tests/interface/test_orientacao_p0.py`: inscrições abertas; lista sem inscrito; lista com inscrito; relação congelada; marco por pontuação; Etapa de habilitação não consolidada
- [ ] T011 [P] [US2] Testes das telas em `tests/interface/test_orientacao_p0.py`: células e totais da condução, nenhum gesto, "Nada a conduzir", conferência com `fora`, convocação sem os dois caminhos, convocação sem corte sem faixa, convocação com corte com faixa, ocupação sem "emita a ordem"
- [ ] T012 [US2] Células e totais: `indicador_do_marco` recebe `agora` e marca as quatro células dos recortes sem inscrito como `NAO_SE_APLICA` com a nota, em `processo_seletivo/interface/conducao_do_marco.py`
- [ ] T013 [US2] Conferência: `alcance` (corte, apuração, publicação) põe o recorte sem inscrito em `FORA` com a razão do contrato, em `conducao_do_marco.py`
- [ ] T014 [US2] Condução: "Nada a conduzir neste marco" e a legenda sem "0 de 0" em `processo_seletivo/interface/templates/interface/marco.html`; a view `marco` passa `nada_a_conduzir` em `views.py`
- [ ] T015 [US2] Convocação: a view `convocacao` passa `sem_inscrito`; o template mostra a frase de não se aplica e omite apuração, gesto e fila; a frase da faixa seguinte fica sob `leitura.corte`, em `processo_seletivo/interface/templates/interface/convocacao.html`
- [ ] T016 [US2] Ocupação: a view `ocupacao` marca `semInscrito` em cada recorte; o template troca a nota "emita a ordem" pela frase de não se aplica, em `ocupacao.html`
- [ ] T017 [US2] Regressão: a ordem vazia emitida em marco por pontuação continua *Feito*, "ninguém concorreu" — conferir que `tests/interface/test_conducao_do_marco.py` segue verde e acrescentar o caso de lista sem inscrito por pontuação em `test_orientacao_p0.py`

**Checkpoint**: US2 verde isolada.

## Phase 5: User Story 3 — Relatório e Encerrar distinguem quem não recebeu a comunicação (P1)

**Goal**: "sem comunicação enviada" é espécie própria; "aguardando resposta" é só prazo em curso.

**Independent Test**: convocação vigente sem envio, com e sem vencimento passado.

- [ ] T018 [P] [US3] Testes em `tests/integration/relatorio/test_convocacao_sem_comunicacao.py`: sem envio → "sem comunicação enviada" no relatório, no Encerrar e no consolidado; sem envio e vencimento passado → não é "vencida"; com envio → "aguardando resposta, até …"
- [ ] T019 [US3] Acrescentar `CONVOCACAO_SEM_COMUNICACAO` em `processo_seletivo/processos/application/pendencias_do_edital.py`
- [ ] T020 [US3] Classificar por `prazo.estado` em `_convocacoes`, prefetch das comunicações, `Convocacoes.sem_comunicacao`, `texto_da_pendencia` e `_situacao_das_vagas` em `processo_seletivo/interface/relatorio_do_edital.py`
- [ ] T021 [US3] Somar a espécie nova nas advertências em `processo_seletivo/interface/encerramento.py`
- [ ] T022 [US3] Rótulos, dicionário de convocações, "outras respostas" e frase em `processo_seletivo/interface/relatorio_consolidado.py`; coluna da tabela em `processo_seletivo/interface/relatorio_consolidado_pdf.py`
- [ ] T023 [US3] Registrar o envio da comunicação na fixture `tests/fixtures/relatorio.py` (`convocar`), para que o cenário continue o de uma convocação comunicada; conferir as suítes `tests/integration/relatorio*`, `tests/unit/interface/test_relatorio*` e `tests/interface/test_confirmacao_do_encerramento.py`

**Checkpoint**: US3 verde isolada.

## Phase 6: User Story 4 — O aviso de congelamento no lugar (P2)

**Goal**: aviso no topo só com relação a congelar; dentro da sucessão nos demais casos.

**Independent Test**: extração declarada para hoje; todas congeladas; uma por congelar; lista sem inscrito.

- [ ] T024 [P] [US4] Testes em `tests/interface/test_orientacao_p0.py`: todas congeladas → aviso só dentro de `details.sucessao`; uma por congelar → aviso no topo; só lista sem inscrito por congelar → sem aviso no topo
- [ ] T025 [US4] `inclui_congelamento` em `congelar_agora_inviavel` em `processo_seletivo/sorteios/application/previa.py`
- [ ] T026 [US4] Condição do topo e aviso dentro do bloco de sucessão em `sorteio.html`

**Checkpoint**: US4 verde isolada.

## Phase 7: User Story 5 — A confirmação da ordem diz por que todos ficam sem posição (P1)

**Goal**: contagem por Etapa enumerada e grupos por motivo na confirmação.

**Independent Test**: marco por pontuação sem nenhum resultado; com resultado parcial; com eliminação.

- [ ] T027 [P] [US5] Testes unitários de `resumo` em `tests/unit/interface/test_conferencia_da_ordem.py`
- [ ] T028 [P] [US5] Teste da tela de confirmação em `tests/interface/test_orientacao_p0.py`: Etapa nomeada com a contagem, frase de nenhuma com resultado, botão de emitir presente
- [ ] T029 [US5] Criar `processo_seletivo/interface/conferencia_da_ordem.py` com `resumo(proposta)` (R-8)
- [ ] T030 [US5] Passar `resumo` à confirmação em `emitir_ordenacao` (`views.py`) e mostrar a seção e os grupos em `processo_seletivo/interface/templates/interface/ordenacao_confirmar.html`

**Checkpoint**: US5 verde isolada.

## Phase 8: Polish & Cross-Cutting

- [ ] T031 `ruff check` e `ruff format --check`; `make check`
- [ ] T032 `make test-pg` com `DB_NAME` próprio; registrar os números em `specs/126-orientacao-p0/verificacao.md`, comparando com a linha de base do CLAUDE.md
- [ ] T033 Matriz `specs/126-orientacao-p0/rastreabilidade.md` cobrindo FR-4010 a FR-4041, SC-1210 a SC-1218 e UX-223 a UX-227
- [ ] T034 Capturas antes e depois no navegador (quickstart, passo 2) em `specs/126-orientacao-p0/capturas/`
- [ ] T035 Revisão independente por subagente; corrigir os achados relevantes e registrá-los em `verificacao.md`
- [ ] T036 Conferir o PR #410 (`gh pr view 410 --json state,mergeable`) antes de cada push; abrir o PR com objetivo, requisitos, decisões, testes, capturas, riscos e a pergunta da G-01

## Dependencies & Execution Order

- Phase 2 antes de tudo: T002 alimenta US2 e US4 (o recorte sem inscrito não dispara o aviso); T003 alimenta US1 e US4.
- US1 antes de US4: o aviso da US4 mora no bloco de sucessão do sorteio criado na US1.
- US2, US3 e US5 são independentes entre si e da US1.
- Polish por último.

## Parallel Opportunities

- T003 em paralelo com T002.
- Os testes de cada história ([P]) em paralelo com os de outras.
- US3 (relatório) e US5 (ordem) tocam arquivos disjuntos dos de US1/US2, salvo `views.py`.

## Implementation Strategy

MVP é a US1 (o risco operacional maior). Depois US2, US3 e US5, todas P1. A US4 fecha. Cada história
termina com os testes dela verdes; a suíte inteira roda uma vez, no polimento.
