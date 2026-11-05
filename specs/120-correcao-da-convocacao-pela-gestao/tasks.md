# Tasks: A correção da convocação pela gestão (120)

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/correcao-da-convocacao.md](contracts/correcao-da-convocacao.md),
[quickstart.md](quickstart.md)

**Tests**: pedidos. Cada FR, SC e caso-limite tem linha em [rastreabilidade.md](rastreabilidade.md);
os testes de cada parte vêm antes da implementação dela e devem falhar primeiro.

Caminhos relativos a `backend/`. Suíte sempre contra PostgreSQL (`make test-pg`), com `DB_NAME`
próprio da worktree e os grupos `assistente` e `navegador` instalados.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente)
- **[Story]**: US1–US4 da spec

---

## Phase 0: Portão

- [X] T000 Spec, plano, pesquisa, modelo de dados, contrato, quickstart e matriz escritos e revistos (04/11/2026, commits `4b2bd844` e `762c012c`); plano aprovado pelo usuário em 04/11/2026; `tests/test_citacoes_de_requisito.py` verde

## Phase 1: Setup

- [X] T001 Conferências antes do código, registradas em `specs/120-correcao-da-convocacao-pela-gestao/verificacao.md` (novo): (a) se `leitura_do_recorte` expõe a ordem vigente, ou se a tela com ordem não vigente chega a montar os cartões (R-006); (b) os testes que prendem a razão da trilha de convocar por texto (`grep -rn "Motivo da sucessão" tests/`); (c) a lista literal de templates de `tests/test_vocabulario_da_convocacao.py`; (d) como `tests/test_javascript.py` descobre os arquivos de `tests/javascript/`; (e) as folhas da gestão que já têm regra para `como-preencher`, `confirmar`, `campo`, `nota`, `dados-da-inscricao` e `erro`
- [X] T002 Linha de base: `make lint check test-pg` com os grupos `assistente` e `navegador`, `DB_NAME` próprio; anotar totais e pulados em `verificacao.md`

---

## Phase 2: Foundational — o comando corrige o que foi visto (bloqueia US1–US4)

**Goal**: `convocar(correcao=...)` confere a convocação nomeada e a assinatura sob a trava, depois da
repetição; as recusas próprias da correção existem; a trilha nomeia a corrigida.
**Independent Test**: os casos de `sv` e `up` da matriz, sem tela.

### Tests

- [X] T003 [P] `tests/unit/convocacao/test_correcao_pura.py`: `especie_da_sucessora` — a da posição quando há (titular, suplente, regularizável), a da raiz quando a posição não dá; `assinatura_da_correcao` — muda com cada um dos cinco componentes, isoladamente, e não depende de nada além deles (FR-3857, R-003, R-004)
- [X] T004 [P] `tests/integration/convocacao/test_correcao_da_convocacao.py`, a convocação nomeada e as recusas próprias: sucedida no intervalo (recusa, nenhuma sucessora da sucessora); com desfecho no intervalo (recusa, **nenhuma chamada nova**); de outra inscrição e de outro recorte (`nao_encontrado`); sem vencimento (`correcao_sem_vencimento`); motivo vazio e só espaços (`motivo_da_correcao_obrigatorio`, `campo="motivo"`); sem vencimento nem Evento (`vencimento_da_correcao_obrigatorio`, `campo="vencimento"`); vencimento passado; Processo encerrado; cada recusa grava zero convocações, comunicações e eventos de trilha — parametrizado (FR-3840, FR-3841, FR-3843, SC-1143)
- [X] T005 [P] No mesmo arquivo, a prévia confirmada: apuração seguinte emitida entre a assinatura e a confirmação; Retificação publicada no intervalo; espécie mudada pela contagem nova — cada uma recusa com `previa_da_correcao_superada` e grava zero (FR-3857)
- [X] T006 [P] No mesmo arquivo, o ato: a sucessora aponta a corrigida, reaproveita a chamada e leva o vencimento novo; o complemento entra no fundamento gravado; a lista, as apresentações e as conferências da chamada não mudam de contagem; correção em cadeia; vencimento anterior ao atual e futuro admitido; chamada para regularizar corrigível sem a guarda de ordem; o desfecho depois se registra na sucessora e a pendência bloqueia o aceite; o lote continua sem sucessão; decorrido o vencimento novo, documentos e Requerimento fecham juntos (FR-3842, FR-3846, FR-3853, SC-1142, SC-1145, casos-limite)
- [X] T007 [P] No mesmo arquivo, a idempotência: dois envios com a mesma chave, por mensagem individual (uma sucessora, um evento, uma mensagem), por publicação (aguardando nas duas respostas) e com falha de envio (a falha nas duas, sem segunda tentativa); duas correções concorrentes de formulários diferentes do mesmo cartão — uma grava, a outra recusa como sucedida (FR-3848, SC-1144, R-002)
- [X] T008 [P] No mesmo arquivo, a trilha: um evento por correção, com ator, motivo, a convocação corrigida e os dois vencimentos (FR-3851, SC-1149)

### Implementation

- [X] T009 `processo_seletivo/convocacao/domain/nomes.py`: os códigos `motivo_da_correcao_obrigatorio`, `vencimento_da_correcao_obrigatorio`, `correcao_sem_vencimento`, `convocacao_corrigida_sucedida`, `convocacao_corrigida_com_desfecho` e `previa_da_correcao_superada`
- [X] T010 [P] `processo_seletivo/convocacao/domain/especie.py`: `especie_da_sucessora(inscricao, *, ocupando, alcancados, regularizaveis, anterior)` (R-004); `convocar.py` passa a usá-la no lugar da regra em linha
- [X] T011 [P] `processo_seletivo/convocacao/domain/alcance.py`: `assinatura_da_correcao(*, convocacao_id, apuracao_id, versao_id, forma, especie)` (R-003)
- [X] T012 `processo_seletivo/convocacao/application/convocar.py`: o argumento `correcao`; a ordem do contrato — repetição, impedimentos, nomeada, sem vencimento, motivo, espécie, assinatura, guardas, gravação; a versão lida uma vez antes da assinatura e reusada na gravação; `corrige` e `previa` no payload da reserva; a frase de desfecho e a de sucessão com quem e quando; o detalhe da prévia superada com os componentes que diferem (FR-3840, FR-3843, FR-3846, FR-3857, R-001, R-002)
- [X] T013 `convocar.py`, `_auditar`: *"Sucede a convocação ‹id›, de vencimento ‹instante›."* quando há anterior, com ou sem `correcao`; ajustar os testes que T001(b) encontrou, se algum prender a razão por igualdade (FR-3851)
- [X] T014 `processo_seletivo/convocacao/application/fluxo.py`, `convocar_e_comunicar`: repassa `correcao`; com `correcao` e sem vencimento resolvido, `vencimento_da_correcao_obrigatorio` ao lado da recusa de vencimento passado (FR-3841)

**Checkpoint**: T003–T008 verdes; a API da `019` e a chamada individual da `050` inalteradas — `tests/integration/convocacao/` inteiro verde.

---

## Phase 3: US1 — a comissão dá mais prazo a uma chamada em aberto (P1) 🎯 MVP

**Goal**: o cartão em aberto oferece a correção, com a prévia, e o ato acontece pela tela.
**Independent Test**: corrigir pela tela e conferir a sucessora, o cartão, o histórico e a trilha (SC-1141, SC-1145).

### Tests

- [X] T015 [P] [US1] `tests/interface/test_correcao_da_convocacao.py`, a ação: aparece com prazo em curso, com vencimento decorrido e sem comunicação enviada; ausente com desfecho, sem vencimento, com o Processo encerrado, para o membro alocado à conferência e para a auditoria; a sucedida não tem cartão (FR-3837, FR-3838)
- [X] T016 [P] [US1] No mesmo arquivo, a prévia: cada valor com a origem; *"o que reabre"* só na chamada vencida; a frase da comunicação por forma; as três regras do efeito sem vencimento; quando a espécie muda; quando o fundamento cita outra apuração ou versão; o vencimento não vem preenchido; o parágrafo de irreversibilidade; o botão com o protocolo; o nome do ato e a ausência de "prorrogação" e "reabertura de prazo" (FR-3841, FR-3844, FR-3845, FR-3856)
- [X] T017 [P] [US1] No mesmo arquivo, o ato pela tela: o POST corrige; o resultado diz estendido, antecipado e mantido, com os dois vencimentos e a comunicação; o cartão mostra a sucessora e *"Corrigida em … — ver o histórico"*; duas correções deixam três linhas no histórico; quem tem chamada em aberto continua fora da fila; a pendente da corrigida sai de *"Comunicações que ainda não saíram"* (FR-3849, FR-3852, FR-3853, SC-1145, casos-limite)
- [X] T018 [P] [US1] `tests/performance/test_convocacao.py`: `test_a_correcao_nao_custa_consulta_por_cartao` — a tela com 1 e com 20 chamadas em aberto, o mesmo número de consultas, com a folga de duas do arquivo (FR-3855, SC-1147)
- [X] T019 [P] [US1] `tests/javascript/correcao-da-convocacao.test.js`: estende, antecipa, mantém, pelo Evento, sem valor, valor apagado volta às três regras (FR-3844, R-009)

### Implementation

- [X] T020 [US1] `processo_seletivo/convocacao/application/fluxo.py`: `previa_das_correcoes(leitura, *, versao, forma, fundamentos)` — por linha em aberto e com vencimento, os campos de `data-model.md` (*O que a tela monta por cartão*), em memória; e o impedimento do recorte, conforme T001(a) (FR-3839, FR-3844, FR-3855)
- [X] T021 [US1] `processo_seletivo/interface/views.py`, `convocacao`: montar a prévia das correções para quem pode emitir, com a versão e a forma lidas uma vez, e prendê-la a cada linha (FR-3844, FR-3855)
- [X] T022 [US1] `processo_seletivo/interface/templates/interface/_vencimento_da_convocacao.html`: o parâmetro `obrigatorio` (texto de ajuda da correção), os valores preservados (`valor_vencimento`, `valor_evento`) e `data-fim` em cada `<option>` de Evento, sem mudar o que os formulários de hoje renderizam (FR-3841)
- [X] T023 [US1] `processo_seletivo/interface/templates/interface/_correcao_da_convocacao.html` (novo): a ação em `<details class="como-preencher">`, os campos ocultos, a prévia em `<dl>`, o parágrafo de irreversibilidade, o motivo, o vencimento, o complemento, a região do efeito com as três regras e o botão com o protocolo; incluído em cada cartão de `convocacao.html` depois de *"Registrar desfecho"*, e ausente nos casos da FR-3838 (FR-3837, FR-3838, FR-3844, FR-3845, FR-3856)
- [X] T024 [US1] `processo_seletivo/interface/static/interface/correcao-da-convocacao.js` (novo), carregado com `defer` em `convocacao.html`: o efeito do vencimento informado sobre o atual (R-009)
- [X] T025 [US1] `processo_seletivo/interface/views.py`, `convocar_view`: o ramo com `corrige` — monta `correcao`, repassa, e no sucesso grava `acao_da_convocacao = "correcao"` e o resultado com `protocolo`, os dois vencimentos (o anterior lido da corrigida) e o efeito (FR-3849, R-005)
- [X] T026 [US1] `convocacao.html`: o resultado `"correcao"` e, no cartão cuja vigente tem anterior, *"Corrigida em ‹data› — ver o histórico"* (FR-3849)
- [X] T027 [P] [US1] Regras de folha para toda classe nova citada nos templates, em `interface/telas/` ou na folha comum da gestão, conforme T001(e); e o parcial novo na lista literal de `tests/test_vocabulario_da_convocacao.py`

**Checkpoint**: T015–T019 verdes; corrigir pela tela funciona no `runserver` local.

---

## Phase 4: US2 — o convocado vê o prazo novo e retoma o que o prazo fechava (P1)

**Goal**: a jornada da gestão ao portal, demonstrada (condição de conclusão, FR-3854).
**Independent Test**: SC-1142, no navegador.

- [X] T028 [US2] `tests/navegador/test_jornada_da_correcao_da_convocacao.py`, no molde de `test_jornada_dos_documentos_da_convocacao.py`: `test_corrigida_na_gestao_o_convocado_complementa_e_envia` — o estado do cenário G (documento pendente, Requerimento na convocação nunca enviado, vencimento de dois segundos, comunicado, espera de três); o portal a 375 px recusa; a gestão em desktop corrige pela ação, lendo *"o que reabre"* e *"estendido"*; o portal mostra o prazo novo, aceita a complementação e o envio do Requerimento; a gestão vê a complementação aguardando conferência e o histórico; uma sucessora, um evento de trilha, lista e conferências intactas; sem violação de CSP; sem rolagem horizontal a 375 px (FR-3854, SC-1141, SC-1142)
- [X] T029 [US2] No mesmo arquivo, `test_com_a_apuracao_superada_nenhum_cartao_oferece_formulario` (FR-3839, SC-1146)
- [X] T030 [US2] Demonstração humana no navegador do app, pelo [quickstart](quickstart.md) — jornada principal, passos 1 a 11, e a correção pela tela de uma chamada com prazo em curso e de uma sem comunicação enviada, que o teste no navegador não percorre (SC-1141) —, com capturas em `specs/120-correcao-da-convocacao-pela-gestao/capturas/` e o registro em `verificacao.md`. **Se um defeito do portal impedir a jornada:** registrar em `doc/`, parar e levar ao usuário; a feature não se declara concluída (FR-3854)

**Checkpoint**: a jornada principal demonstrada, no teste e à mão.

---

## Phase 5: US3 — a correção que não pode acontecer diz por quê e o que fazer (P1)

**Goal**: o impedimento declarado antes do formulário, e cada recusa no cartão com os campos.
**Independent Test**: SC-1143, SC-1146, SC-1148.

### Tests

- [X] T031 [P] [US3] `tests/interface/test_correcao_da_convocacao.py`, o impedimento: apuração superada (todos os cartões em aberto com a limitação, a causa e *"Emitir a apuração seguinte"*, nenhum formulário), apuração ausente, ordem não vigente — conforme T001(a) (FR-3839, SC-1146)
- [X] T032 [P] [US3] No mesmo arquivo, a recusa no cartão: motivo vazio (vencimento preservado), vencimento passado (motivo preservado), sem vencimento, fora da faixa ou sem vaga (os quatro campos), prévia superada (a prévia nova e os campos), impedimento surgido no intervalo (a orientação) — a recusa junto do campo que ela nomeia, a ação aberta, o foco na recusa (FR-3850, SC-1148)
- [X] T033 [P] [US3] No mesmo arquivo, o cartão que mudou: sucedida no intervalo — a sucessora no cartão, a recusa com quem e quando, o motivo citado, o formulário da sucessora vazio; com desfecho no intervalo — o desfecho, o motivo citado, sem formulário (FR-3850, D-009, R-008)
- [X] T034 [P] [US3] No mesmo arquivo, a autorização: o POST do membro alocado à conferência recebe 403 e nada grava nem guarda na sessão; o POST com Edital de outra unidade recebe 404 e nada grava (FR-3847, SC-1143)

### Implementation

- [X] T035 [US3] `convocar_view`: na `DomainError` com `corrige`, gravar `recusa_da_correcao` com os campos de `data-model.md` (*A sessão*), em vez de `erro_da_convocacao` (FR-3850, R-007)
- [X] T036 [US3] `views.py`, `convocacao`: consumir `recusa_da_correcao` e prendê-la à linha da mesma inscrição; sem linha, cair no topo (FR-3850)
- [X] T037 [US3] `_correcao_da_convocacao.html`: o impedimento no lugar do formulário, com as frases do topo da tela num parcial comum (`_causas_de_obsolescencia.html`, extraído de `convocacao.html`); a recusa no cartão, com `role="alert"`, junto do campo; os valores preservados; o cartão que mudou, com o motivo em `<blockquote>` e o formulário vazio (FR-3839, FR-3850, R-006, R-008)

**Checkpoint**: T031–T034 verdes.

---

## Phase 6: US4 — um ato, uma vez (P2)

**Goal**: o duplo envio pela tela pratica um ato.
**Independent Test**: SC-1144, pela tela.

- [X] T038 [US4] `tests/interface/test_correcao_da_convocacao.py`: `test_o_duplo_post_corrige_uma_vez` — dois POSTs com a mesma chave, uma sucessora, o mesmo resultado na sessão; recarregada a tela, a segunda correção, com outro motivo, corrige a sucessora e o histórico mostra as duas (FR-3848, SC-1144)

---

## Phase 7: Polish & convergência

- [X] T039 `rastreabilidade.md`: acrescentar a coluna de tarefas e conferir cada nome de teste contra o que foi escrito; corrigir o que mudou de nome
- [X] T040 [P] `README.md`: a linha da `120` passa a *implementada, sem merge*; `CLAUDE.md` só se algum número citado mudar (as tabelas append-only continuam 53)
- [ ] T041 `make lint check test-pg` com os dois grupos opcionais; totais e pulados em `verificacao.md`, comparados com T002 por lista, e não por total
- [ ] T042 `/speckit-converge`: o código contra a spec, o plano e as tarefas; o que faltar vira tarefa e é feito
- [ ] T043 PR para `main`, com o resumo, a verificação e as capturas; **sem merge** (o merge é do usuário)

---

## Dependencies

- **Phase 2 bloqueia todas as histórias.** T009 antes de T012; T010 e T011 antes de T012; T012 antes de T013 e T014.
- **US1 (Phase 3)** depende de Phase 2. T020 antes de T021; T022 antes de T023; T023 antes de T024, T026 e T027; T025 depende de Phase 2.
- **US2 (Phase 4)** depende de US1 — é a jornada pela tela que a US1 cria. T030 depende de T028.
- **US3 (Phase 5)** depende de US1 (o parcial e a view). Pode correr em paralelo com US2.
- **US4 (Phase 6)** depende de US1.
- **Polish** depende de tudo; T041 antes de T042; T043 por último.

## Parallel execution

- **Phase 2:** T003–T008 juntos (dois arquivos, escritos antes do código); depois T010 e T011 juntos.
- **US1:** T015–T019 juntos; T022 e T020 juntos.
- **US3:** T031–T034 juntos.
- **US2 e US3** em paralelo, depois da US1.

## Implementation strategy

1. **MVP = Phase 2 + US1**: a comissão corrige pela tela, com a prévia e o resultado. É o que tira a
   operação do shell.
2. **US2** demonstra o efeito no portal; sem ela a feature não se conclui (FR-3854).
3. **US3** torna a recusa compreensível — sem ela, a apuração superada parece defeito.
4. **US4** prende pela tela a idempotência que o comando já garante.
5. Um PR só, com a suíte verde e a jornada demonstrada.
