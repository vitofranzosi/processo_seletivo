# Tasks: Convocar do cadastro de reserva, na ordem publicada

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/atos.md](contracts/atos.md),
[contracts/tela.md](contracts/tela.md), [quickstart.md](quickstart.md)

**Tests**: pedidos. Cada `FR-` e `SC-` tem teste, e o teste vem **antes** do código: cada fase de
testes roda e falha contra o código anterior antes da implementação dela (Constituição, Princípio V).

**Caminhos**: relativos à raiz do repositório; `backend/` é o projeto Django.

**Banco**: `DB_NAME=ps_097` para a suíte (`TEST_DB_ENGINE=postgresql DB_USER=$(whoami)
DB_RUNTIME_USER=$(whoami)`); `ps_097_demo` para a demonstração, novo e com dados fictícios.

**Testes que mudam de propósito**: `test_reserva_convocada_fora.py` (a frase do aviso),
`BOTOES` e a soma de pesos em `test_telas_de_resultado_e_atos.py`, e as listas literais `DA_016` e
`TELAS` das varreduras de vocabulário. Cada um muda na tarefa que muda o comportamento, com a razão.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivo diferente, sem dependência pendente)
- **[Story]**: a história da spec (US1 a US3)

---

## Phase 1: Setup

- [X] T001 Medir o ponto de partida contra PostgreSQL (variáveis acima) sobre `backend/tests/unit/ocupacao backend/tests/integration/ocupacao backend/tests/integration/convocacao backend/tests/interface/test_ocupacao.py backend/tests/interface/test_convocacao_em_fluxo.py backend/tests/unit/editais/test_reserva_convocada_fora.py backend/tests/test_vocabulario_da_ocupacao.py backend/tests/test_dependencia_da_convocacao.py`; verde, e o total registrado em `specs/097-convocar-do-cadastro-de-reserva/verificacao.md` (novo), seção "Ponto de partida"
- [X] T002 [P] Em `backend/tests/fixtures/ocupacao.py`, `rascunho_com_quadro(..., reserva=None)`: com `reserva` em `LIMITED`/`UNLIMITED`, declara `reserveType` (e `reserveLimit` quando limitado) no Perfil; sem ele, nada muda. Conferir que `montar_cenario_da_convocacao(..., geral=0, reserva="UNLIMITED")` publica (`T-012`)

---

## Phase 2: Foundational — o registro, a conta e a sexta causa

Bloqueia as três histórias.

### Testes (primeiro)

- [X] T003 [P] Em `backend/tests/unit/ocupacao/test_acrescimo_append_only.py` (novo), no molde de `test_efeito_append_only.py`: `AcrescimoDeVagas` recusa `save` de linha existente e `delete`, com *"append-only"*; `ocupacao_acrescimodevagas` está em `TABELAS_APPEND_ONLY` e no texto de `comandos_de_privilegios` com `REVOKE UPDATE, DELETE`; no PostgreSQL, `QuerySet.update()` e `.delete()` são recusados pelo gatilho com `match="immutable"`; e as cinco `CHECK` de [data-model.md](data-model.md) recusam — *feito: o gatilho e as `CHECK` precisam de linha gravada, com Edital e versão, e foram para `backend/tests/integration/ocupacao/test_acrescimo.py`, classe `TestAsGarantiasDoBanco`* — quantidade zero, espécie desconhecida, acréscimo sem origem, desfazimento sem citação e fundamento vazio
- [X] T004 [P] Em `backend/tests/unit/ocupacao/test_acrescimo.py` (novo), a conta pura: `calculo.apurar(..., acrescidas=2)` soma 2 às efetivas com 0 publicadas, e os titulares passam a ser os 2 primeiros da sequência; `acrescidas` padrão zero não muda nenhum resultado; `acrescimo.saldo(lidos)` soma acréscimos e subtrai desfazimentos; `acrescimo.restante(acrescimo, desfazimentos)` (`FR-2462`); `acrescimo.recusa_do_desfazimento(efetivas, quantidade, chamadas)` devolve o código quando `efetivas − quantidade < chamadas`, e nada quando o titular só está na conta (`FR-2462`, `T-005`)
- [X] T005 [P] Em `backend/tests/integration/ocupacao/test_acrescimo.py` (novo), a leitura: um `AcrescimoDeVagas` gravado à mão no recorte torna a apuração vigente obsoleta com `acrescimo_posterior` (`FR-2453`); a emissão seguinte o lê, congela o id em `universo["acrescimosLidos"]` e soma às efetivas (`FR-2452`); a apuração antiga, relida, continua com o número dela (`SC-922`); acréscimo de **outro** recorte não a torna obsoleta (`T-002`); apuração emitida antes desta feature, sem `acrescimosLidos`, só fica obsoleta se houver acréscimo no recorte
- [X] T006 Rodar T003 a T005: falham por `ImportError`/`AttributeError`/`TypeError`, e nenhum por outra razão

### Implementação

- [X] T007 Em `backend/processo_seletivo/ocupacao/domain/nomes.py`: `ACRESCIMO`, `DESFAZIMENTO`, `ESPECIES_DE_ACRESCIMO`, `CAUSA_ACRESCIMO_POSTERIOR` e os códigos de recusa de [contracts/atos.md](contracts/atos.md), com o comentário de por que a vaga acrescida não é movimento (`T-001`)
- [X] T008 Em `backend/processo_seletivo/ocupacao/models.py`, `AcrescimoDeVagas` com os campos, as `CHECK`, o índice e o `save`/`delete` que recusam, como em [data-model.md](data-model.md); docstring com a decisão e o custo dela
- [X] T009 `backend/processo_seletivo/ocupacao/migrations/0004_vaga_acrescida.py`: a tabela, as constraints e o gatilho `acrescimo_de_vagas_imutavel` pela função `reject_occupancy_mutation()`, com `proteger`/`desproteger` só no PostgreSQL e o `RunPython` por último; docstring com as duas travas, *"de 40 para 41"* e o aviso de rodar o provisionamento de novo; nenhuma menção a `convocacao` (`tests/test_dependencia_da_convocacao.py`)
- [X] T010 Em `backend/processo_seletivo/seguranca/papeis.py`, `ocupacao_acrescimodevagas` em `TABELAS_APPEND_ONLY`, no bloco da ocupação, com o comentário do porquê
- [X] T011 [P] `backend/processo_seletivo/ocupacao/domain/acrescimo.py` (novo, puro): `saldo`, `restante`, `recusa_do_desfazimento`; e `calculo.apurar(..., acrescidas=0)` em `backend/processo_seletivo/ocupacao/domain/apuracao.py`, com a soma ao lado de `recebidas − cedidas`
- [X] T012 Em `backend/processo_seletivo/ocupacao/application/emissao.py`, `_apurar` lê os acréscimos do recorte exato em `(registrado_em, id)`, entrega o saldo a `calculo.apurar` e congela os ids em `universo["acrescimosLidos"]`; em `backend/processo_seletivo/ocupacao/application/selectors.py`, `acrescimos_do_recorte`, `_acrescimo_posterior` e a sexta causa em `causas_de_obsolescencia`, com a descrição de [data-model.md](data-model.md); `ocupacao_do_recorte` passa a devolver `acrescimos` e `acrescidas`
- [X] T013 Rodar T003 a T005: verdes; rodar `backend/tests/unit/ocupacao backend/tests/integration/ocupacao backend/tests/migrations/test_migrations.py backend/tests/integration/test_database_permissions.py backend/tests/integration/test_imutabilidade_do_historico.py`: verdes

**Checkpoint**: a vaga acrescida existe e a apuração a conta; nenhuma tela a alcança ainda.

---

## Phase 3: User Story 1 — Registrar a vaga que o Edital regular liberou, e chamar o próximo (P1) 🎯 MVP

**Goal**: pela ocupação, quem apura acrescenta 1 vaga com origem e fundamento, confere quem a ordem
alcança, confirma, e a convocação passa a oferecer o 1º da ordem.

**Independent Test**: [quickstart.md](quickstart.md), passos 2 a 8.

### Testes (primeiro)

- [X] T014 [P] [US1] Em `backend/tests/integration/ocupacao/test_acrescimo.py`, o ato: `acrescentar_vagas` grava o acréscimo e emite a apuração seguinte com o autor do ato e o motivo que cita a vaga acrescida (`FR-2450`, `FR-2454`); no recorte sem apuração, emite a primeira (`T-004`); com outra causa de obsolescência presente, grava e devolve `apuracaoPendente` com `outra_causa_de_obsolescencia`, sem emitir (`FR-2454`); recusa da emissão (empate na fronteira) não desfaz o acréscimo; as recusas `quantidade_invalida`, `origem_obrigatoria`, `fundamento_obrigatorio`, `acrescimo_sem_cadastro_de_reserva` (Perfil `NONE`), `acrescimo_fora_da_linha_geral` (Perfil com linha de Modalidade com 0 vaga; com reversão declarada; recorte de Modalidade), `ordem_nao_vigente`, `sem_quadro_publicado` (`FR-2451`, `FR-2459`, `FR-2463`, `FR-2464`) — cada uma sem gravar nada; a mesma chave devolve o mesmo acréscimo (`FR-2458`); assinatura velha recusa com `leitura_do_recorte_mudou` (`FR-2457`); quem não gere a comissão recebe a recusa da comissão (`FR-2465`); a trilha tem `OCUPACAO_ACRESCENTAR_VAGAS` e `OCUPACAO_APURAR`, com o mesmo ator (`FR-2466`); o conteúdo publicado e as versões do Edital não mudam (`FR-2450`)
- [X] T015 [P] [US1] Em `backend/tests/integration/ocupacao/test_acrescimo.py`, `previa_do_acrescimo`: efetivas depois, alcançados nominalmente na ordem, `faltamPessoas` com 3 vagas e faixa de 2, os acréscimos anteriores com origem, e a forma da emissão (`FR-2456`); nada é gravado
- [X] T016 [P] [US1] Em `backend/tests/integration/convocacao/test_reserva.py` (novo), a cadeia: cenário `geral=0, reserva="UNLIMITED"` — antes do acréscimo, convocar o 1º é recusado como hoje; depois de 1 acrescida, `previa_dos_titulares` alcança o 1º, `convocar_titulares` o convoca (`FR-2455`); o não atendimento devolve a vaga e o 2º é chamável como suplente sem novo acréscimo (Acceptance 4 da US1); o fundamento derivado da convocação cita a apuração e não contém a origem nem o fundamento do acréscimo (`FR-2467`); da vaga liberada à convocação, dois atos confirmados e nenhuma apuração à mão (`SC-921`)
- [X] T017 [P] [US1] Em `backend/tests/interface/test_acrescimo.py` (novo): a ocupação mostra publicadas, acrescidas e efetivas e a lista dos acréscimos (`UX-220`); o formulário só para quem gere a comissão, e o auditor vê a lista sem formulário (`FR-2465`); o `POST` sem `confirmar` devolve a conferência com os alcançados pelo nome, a frase de vagas sem pessoa e o botão com o número (`UX-221`, `UX-222`), e nada é gravado; com `confirmar=1`, grava e volta à ocupação com a mensagem; a recusa volta à ocupação com a frase do domínio; `leitura_do_recorte_mudou` volta à conferência recalculada; Perfil sem reserva mostra a frase da recusa no lugar do formulário; a página pública do Edital e o portal continuam com as vagas publicadas (`FR-2468`)
- [X] T018 [US1] Rodar T014 a T017: falham pelas razões esperadas — *feito fora de ordem: o módulo de aplicação foi escrito junto dos testes de T014, e eles já rodaram verdes; o registro está em `verificacao.md`*

### Implementação

- [X] T019 [US1] `backend/processo_seletivo/ocupacao/application/acrescimo.py` (novo): `previa_do_acrescimo`, `acrescentar_vagas` e a emissão da seguinte num *savepoint*, como em [contracts/atos.md](contracts/atos.md); as recusas na ordem do contrato; razão da trilha com recorte, quantidade, origem e apurações; nenhum import de `convocacao`; vocabulário da `016`
- [X] T020 [US1] Em `backend/processo_seletivo/ocupacao/application/emissao.py`, a porta da emissão que o acréscimo usa — `_apurar` com `movimento_admitido=False` e auditoria —, extraída de `emitir_sucessora_por_efeito` sem mudar o que ela faz para o desfecho — *feito sem extração: `emitir_sucessora_por_efeito` já é essa porta, e o acréscimo a chama como o desfecho chama*
- [X] T021 [US1] Em `backend/processo_seletivo/interface/urls.py`, `acrescentar-vagas`; em `backend/processo_seletivo/interface/views.py`, `acrescentar_vagas_view` (conferência sem `confirmar`, ato com `confirmar=1`, POST-redirect-GET), a ocupação passando a cada recorte `acrescimos`, `acrescidas` e se o Perfil aceita, e `OPERACOES`/`AGREGADOS` com *"Acréscimo de vagas"*
- [X] T022 [US1] Em `backend/processo_seletivo/interface/templates/interface/ocupacao.html`, o número das acrescidas, a lista e o formulário de [contracts/tela.md](contracts/tela.md); `backend/processo_seletivo/interface/templates/interface/ocupacao_acrescimo.html` (novo), a conferência, com a trilha no `caminho_do_contexto`, `<dfn>` no primeiro "recorte" e nenhum texto inline; regras novas na folha comum em `backend/processo_seletivo/interface/static/interface/gestao/` só se nenhuma classe existente servir
- [X] T023 [US1] Em `backend/processo_seletivo/auditoria/selectors.py`, `_atos_da_conducao` reúne os acréscimos do Edital, para que a trilha os mostre
- [X] T024 [US1] As varreduras: `ocupacao_acrescimo.html` e `ocupacao/application/acrescimo.py` em `DA_016` de `backend/tests/test_vocabulario_da_ocupacao.py`; `ocupacao_acrescimo.html` em `TELAS` de `backend/tests/test_vocabulario_da_composicao.py`; o botão *"Conferir o acréscimo"* em `BOTOES["ocupacao.html"]` e a soma de pesos em `backend/tests/interface/test_telas_de_resultado_e_atos.py`
- [X] T025 [US1] Rodar T014 a T017 e `backend/tests/interface backend/tests/test_vocabulario_da_ocupacao.py backend/tests/test_vocabulario_da_composicao.py backend/tests/test_gramatica_das_portas.py backend/tests/test_dependencia_da_ocupacao.py backend/tests/test_dependencia_da_convocacao.py`: verdes

**Checkpoint**: o MVP — o TMD convoca pelo sistema.

---

## Phase 4: User Story 2 — A Revisão diz a verdade sobre essa família (P1)

**Goal**: o aviso deixa de dizer que a convocação é feita fora, diz quantos a faixa alcança, e o
Perfil só de reserva com linha de Modalidade é avisado de que o acréscimo não o alcança.

**Independent Test**: levar à Revisão um rascunho com Perfil só de reserva e ler os avisos.

- [X] T026 [P] [US2] Em `backend/tests/unit/editais/test_reserva_convocada_fora.py`, trocar a frase esperada: o aviso diz que a convocação depende de vagas acrescidas depois da publicação e **não** contém *"fora"* (`FR-2474`, `SC-923`); com corte `FIXED` 20 + 0 e sem continuação, diz *"até 20 classificados"*; com `FROM_VACANCY_TABLE` e excedente 3, *"até 3"*; com continuação admitida, nenhum número (`T-011`); continua advertência, só na publicação (`FR-2476`); e o achado novo `reserve_only_with_reserved_lines` no Perfil só de reserva com linha de Modalidade (`FR-2475`)
- [X] T027 [US2] Rodar T026: falha pela frase e pelo achado ausente
- [X] T028 [US2] Em `backend/processo_seletivo/editais/domain/validation.py`, `_reserva_convocada_fora` com a frase nova, o alcance pela regra de corte (`T-011`) e o docstring revisto — a `DP-05` voltou a A em 21/10, e o código do achado continua o mesmo (`T-008`); `_reserva_com_linhas_reservadas` ao lado
- [X] T029 [US2] Rodar T026, `backend/tests/unit/editais` e `backend/tests/interface/test_advertencias_do_quadro.py`: verdes

---

## Phase 5: User Story 3 — O acréscimo errado se desfaz por outro ato (P2)

**Goal**: desfazer, com motivo, a vaga acrescida que ninguém chamou; recusar quando alguém foi chamado.

**Independent Test**: [quickstart.md](quickstart.md), passos 9 e 10.

- [X] T030 [P] [US3] Em `backend/tests/integration/ocupacao/test_acrescimo.py`, `desfazer_acrescimo`: com o titular só na conta, aceito, e o 1º deixa de ser titular (Acceptance 3); a apuração seguinte emitida pelo ato, com o desfazimento congelado e descontado (`FR-2461`); as duas linhas continuam na leitura do recorte; recusas `motivo_obrigatorio`, `quantidade_invalida`, `acrescimo_inexistente` (de outro Edital), `desfazimento_alem_do_acrescimo` (inclusive somando dois desfazimentos), `desfazimento_com_pessoas_chamadas` com um dublê de `pessoas_chamadas` que devolve 1 (`FR-2460`–`FR-2462`); a função é chamada dentro da transação, depois da trava; trilha `OCUPACAO_DESFAZER_ACRESCIMO`
- [X] T031 [P] [US3] Em `backend/tests/integration/convocacao/test_reserva.py`: `pessoas_chamadas` conta em aberto e atendidos e não conta encerrados nem reclassificados; desfazer a vaga depois de convocar quem a ocupa é recusado de verdade, pelo seletor real (Acceptance 2)
- [X] T032 [P] [US3] Em `backend/tests/interface/test_acrescimo.py`: o formulário de desfazimento na linha de cada acréscimo com saldo, a conferência, o ato, e a recusa com a frase
- [X] T033 [US3] Rodar T030 a T032: falham pelas razões esperadas
- [X] T034 [US3] Em `backend/processo_seletivo/convocacao/application/selectors.py`, `pessoas_chamadas(*, edital, perfil_id, marco_id, lista_id=None, at=None)` sobre `_situacoes`; em `backend/processo_seletivo/ocupacao/application/acrescimo.py`, `previa_do_desfazimento` e `desfazer_acrescimo(..., pessoas_chamadas)`
- [X] T035 [US3] Rota `desfazer-acrescimo`, `desfazer_acrescimo_view` passando o seletor da convocação, o formulário em `ocupacao.html`, o modo de desfazimento em `ocupacao_acrescimo.html`, o rótulo em `OPERACOES`; o botão *"Conferir o desfazimento"* em `BOTOES` e na soma de pesos
- [X] T036 [US3] Rodar T030 a T032 e as varreduras de T025: verdes

---

## Phase 6: Polish & Cross-Cutting

- [ ] T037 [P] Em `backend/tests/performance/test_ocupacao.py`, a leitura da ocupação, a conferência e o ato com 1 e com 10 acréscimos no recorte têm o mesmo número de consultas (`SC-924`)
- [ ] T038 [P] Em `AGENTS.md`, *"são **41** desde as vagas acrescidas da `097`"* no parágrafo do `N de M`; em `README.md`, a linha da `097` passa a *"Implementada"* com o que a interface faz
- [ ] T039 [P] `specs/097-convocar-do-cadastro-de-reserva/rastreabilidade.md` (novo): cada `FR-`, `SC-` e `UX-` desta spec com o teste que o prova; e, em `specs/050-convocacao-como-fluxo/rastreabilidade.md`, a nota de que a `FR-889` foi revista pela `FR-2455`
- [ ] T040 `cd backend && make lint check` e a suíte inteira contra PostgreSQL com `DB_NAME=ps_097`: verde, com os números em `verificacao.md`
- [ ] T041 Demonstração pela interface, num banco `ps_097_demo` novo, dos passos 1 a 11 do [quickstart.md](quickstart.md), com captura; o registro em `verificacao.md` (`SC-920`)
- [ ] T042 `/speckit-converge`: o que faltar vira tarefa nova neste arquivo

---

## Dependencies & Execution Order

- **Setup (1)** → **Foundational (2)** → **US1 (3)** → **US3 (5)**.
- **US2 (4)** depende só do Setup: mexe em `validation.py`, que nenhuma outra fase toca, e pode correr
  ao lado da Foundational.
- **US3** depende da US1: o desfazimento usa a conferência, a rota e o módulo de aplicação dela.
- **Polish** depois de tudo; T041 depois de T040.

## Parallel Opportunities

- T003, T004 e T005 entre si; T014 a T017 entre si; T030 a T032 entre si.
- A US2 inteira em paralelo com a Phase 2.
- T037, T038 e T039 entre si.

## Implementation Strategy

**MVP**: Phases 1 a 3 — o TMD convoca pelo sistema. Ele é demonstrável sozinho, mas não é entregável
sozinho: sem a US3, um acréscimo registrado por engano não tem saída, e a equipe recorreria à
Retificação que esta spec existe para evitar. A US2 é pequena e entra no mesmo PR, para que a Revisão
não diga coisa falsa no dia em que a US1 chegar à `main`. Um PR só, com as três.
