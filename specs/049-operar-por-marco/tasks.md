---

description: "Tasks — 049 · Operar o resultado por marco"
---

# Tasks: Operar o resultado por marco, e não por recorte

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/o-gesto-do-marco.md](contracts/o-gesto-do-marco.md),
[quickstart.md](quickstart.md)

**Testes**: exigidos pela Constituição (Princípio V) para regra crítica — o gesto pratica atos
irreversíveis. Todos os casos moram em `backend/tests/interface/test_conducao_do_marco.py`, contra
PostgreSQL (`transaction=True` onde a recusa parcial depende de commit por recorte).

Caminhos relativos à raiz do repositório.

## Phase 1: Setup

- [ ] T001 Conferir que nenhuma rota `interface:marco` ou `interface:gesto-do-marco` existe e que a faixa `FR-810`–`FR-831`, `SC-300`–`SC-305`, `UX-090`–`UX-093` segue livre em `specs/*/spec.md`

## Phase 2: Foundational (bloqueia todas as histórias)

- [ ] T002 Criar `backend/processo_seletivo/interface/conducao_do_marco.py` com `recortes_do_marco(conteudo, perfil)` (pela derivação única, `FR-812`), `marco_publicado(edital, marco_id)` e a constante das quatro operações
- [ ] T003 Registrar as rotas `interface:marco` (GET) e `interface:gesto-do-marco` (POST, `<operacao>`) em `backend/processo_seletivo/interface/urls.py`
- [ ] T004 Escrever a porta da tela do marco em `backend/processo_seletivo/interface/views.py` — abre para quem classifica, audita ou publica resultado (`FR-830`, `R-7`, `R-11`) — e as linhas das negativas novas em `specs/033-navegacao-por-capacidade/inventario-das-negativas.md`
- [ ] T005 Criar a fixture de Edital com dois Perfis (ampla + duas cotas com regra de corte; só a ampla), Resultados consolidados e uma cota sem inscrito, em `backend/tests/interface/test_conducao_do_marco.py`

**Checkpoint**: rota abre, porta recusa quem não alcança.

## Phase 3: User Story 1 — Saber, por marco, quais recortes faltam (P1) 🎯 MVP

**Goal**: indicador completo na tela do marco e resumo de presença na página do Edital.
**Independent Test**: ordens emitidas em dois dos três recortes pela tela de hoje; a página do Edital diz *com ordem 2 de 3* e a tela do marco mostra cada célula.

- [ ] T006 [P] [US1] Testes do indicador: estados *feito/obsoleto/falta/não se aplica*, *ninguém concorreu*, publicação defasada, marco de sorteio levando à tela do sorteio, rótulos e ordem da derivação, marco removido ausente, recorte acrescentado por Retificação aparece como falta (`FR-810` a `FR-815`) em `backend/tests/interface/test_conducao_do_marco.py`
- [ ] T007 [P] [US1] Teste de orçamento: a página do Edital com 1 e com 4 marcos faz o mesmo número de consultas no resumo (`SC-305`) em `backend/tests/interface/test_conducao_do_marco.py`
- [ ] T008 [US1] Implementar `indicador_do_marco(edital, perfil, marco)` (estado completo por recorte, `R-6`) e `resumo_dos_marcos(edital, conteudo)` (presença, quatro consultas para o Edital inteiro) em `backend/processo_seletivo/interface/conducao_do_marco.py`
- [ ] T009 [US1] View `marco` (GET) em `backend/processo_seletivo/interface/views.py` e template `backend/processo_seletivo/interface/templates/interface/marco.html` com a tabela recorte × operação e o caminho de cada célula (`UX-091`)
- [ ] T010 [US1] Resumo por marco e destino *"conduzir o marco"* em `_marcos_publicados` de `backend/processo_seletivo/interface/views.py` e em `backend/processo_seletivo/interface/templates/interface/detalhe.html` (`UX-090`)

**Checkpoint**: US1 verificável sozinha.

## Phase 4: User Story 2 — Ordenar o marco num gesto (P1)

**Goal**: conferência do alcance e emissão das N ordens.
**Independent Test**: três recortes sem ordem → um gesto → três atos com o mesmo autor e o mesmo `correlation_id`.

- [ ] T011 [P] [US2] Testes: conferência não grava; três grupos; recorte com ordem fica fora; obsoleto fica fora com a razão da sucessão; recorte vazio entra declarado; marco de sorteio não oferece; recorte impedido pelo cálculo; botão com a quantidade; autor e trilha iguais aos do ato unitário (`SC-304`) (`FR-816` a `FR-820`, `D-002`, `D-003`, `UX-092`) em `backend/tests/interface/test_conducao_do_marco.py`
- [ ] T012 [US2] Implementar `alcance(...)` para a ordem, com `assinatura_da_proposta` por recorte (`R-3`), em `backend/processo_seletivo/interface/conducao_do_marco.py`
- [ ] T013 [US2] Implementar `praticar(...)`: laço na ordem da derivação, chave por recorte e `correlation_id` do gesto (`R-5`), `DomainError` vira *recusado* (`FR-823`), e o despacho para `emitir_ordem`, em `backend/processo_seletivo/interface/conducao_do_marco.py`
- [ ] T014 [US2] View `gesto_do_marco` (conferência e confirmação, PRG, desfecho na sessão, `R-10`) em `backend/processo_seletivo/interface/views.py` e template `backend/processo_seletivo/interface/templates/interface/marco_conferir.html`; desfecho na `marco.html` (`UX-093`)

## Phase 5: User Story 5 — Uma falha não apaga nem esconde o que deu certo (P1)

**Goal**: recusa parcial isolada, idempotência, retomada.
**Independent Test**: ordem emitida por fora entre conferência e confirmação → dois feitos, um recusado, indicador com os três.

- [ ] T015 [P] [US5] Testes (`transaction=True`): recusa parcial preserva os feitos; desfecho lista recusados primeiro; repetição do envio não pratica de novo e devolve o mesmo desfecho; nova conferência depois de parada no meio só inclui o que falta; recorte forjado no formulário é 404 antes de praticar qualquer um (`FR-821` a `FR-825`, `SC-302`, `SC-303`) em `backend/tests/interface/test_conducao_do_marco.py`
- [ ] T016 [US5] Ajustar `praticar(...)` e a view ao que os testes da T015 exigirem, em `backend/processo_seletivo/interface/conducao_do_marco.py` e `backend/processo_seletivo/interface/views.py`

## Phase 6: User Story 3 — Publicar o marco num gesto (P1)

**Goal**: natureza e autoridade uma vez; N publicações com documento próprio.
**Independent Test**: três atos vigentes → preliminar num gesto → três publicações e três documentos; definitiva com recurso pendente num → só ele recusado.

- [ ] T017 [P] [US3] Testes: alcance pela natureza; impedimentos da prévia por recorte; já publicado na natureza fica fora; preliminar sobre definitiva fica fora; declaração exigida uma vez e gravada em cada publicação; lista vazia publicada; porta: presidência sem `resultado:publicar` não vê o gesto e lê a quem pedir, quem só publica não vê os outros três (`FR-826` a `FR-829`, `D-004`) em `backend/tests/interface/test_conducao_do_marco.py`
- [ ] T018 [US3] Alcance da publicação (`aferir_publicabilidade`, `compor_divulgacao`, `assinatura_da_previa`, `R-9`) e despacho para `publicar_resultado` em `backend/processo_seletivo/interface/conducao_do_marco.py`; natureza, autoridade e declaração nos templates `marco.html` e `marco_conferir.html`; porta de publicar na view

## Phase 7: User Story 4 — Cortar e apurar o marco num gesto (P2)

**Goal**: faixas e apurações em lote.
**Independent Test**: três recortes ordenados → cortar → três faixas; apurar → três apurações, ou recusa do sem quadro em *Impedidos*.

- [ ] T019 [P] [US4] Testes: corte só com regra; recorte com faixa fica fora; sem ordem é impedido com caminho; apuração sem linha no quadro é impedida; mudança entre conferência e confirmação da apuração é recusada (`R-4`) em `backend/tests/interface/test_conducao_do_marco.py`
- [ ] T020 [US4] Alcance e despacho do corte (`calcular_corte`, `assinatura_da_proposta` do corte, `emitir_corte`) em `backend/processo_seletivo/interface/conducao_do_marco.py`
- [ ] T021 [US4] Alcance, assinatura nova e despacho da apuração sob a trava do Processo (`R-4`, `emitir_apuracao`) em `backend/processo_seletivo/interface/conducao_do_marco.py`

## Phase 8: Polish

- [ ] T022 [P] Matriz `specs/049-operar-por-marco/rastreabilidade.md`, requisito a requisito
- [ ] T023 [P] Revisar comentários: explicam por quê, citam só identificadores definidos
- [ ] T024 `cd backend && make DB_NAME=ps049 lint check test-pg`, com `ruff format --check`; a suíte existente das telas por recorte é a prova da `FR-831`
- [ ] T025 Percurso do [quickstart](quickstart.md) pelo preview, com um Edital de vários Perfis e cotas; capturas como prova, e a contagem das confirmações por marco (`SC-300`)

## Dependencies

- Phase 2 bloqueia tudo. US1 (T006–T010) não depende das outras.
- US2 cria o laço (`praticar`) e a view do gesto; US5, US3 e US4 dependem de T013–T014.
- US3 e US4 são independentes entre si.

## Parallel

- T006 e T007; T011 com T008–T010 já prontos; T017 e T019 em paralelo depois de T014.

## Implementation Strategy

MVP = US1: o indicador sozinho já tira as 64 visitas de "o que falta". Depois US2 + US5, que são o
gesto e a garantia dele; depois US3 e US4.
