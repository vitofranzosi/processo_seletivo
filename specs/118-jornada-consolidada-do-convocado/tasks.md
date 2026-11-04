# Tasks: A jornada consolidada do candidato convocado (118)

**Input**: [spec.md](spec.md), [plan.md](plan.md), [quickstart.md](quickstart.md)

> **Nenhuma tarefa de código começa antes do merge desta spec.** O merge é do usuário, e é ele que
> aprova o desenho (D-007 a D-014) e as revisões de outras specs.

**Tests**: pedidos. Cada FR e SC terá linha na matriz de rastreabilidade (T030). Os testes de cada
história vêm antes da implementação dela e devem falhar primeiro.

Caminhos relativos a `backend/`. Suíte sempre contra PostgreSQL (`make test-pg`), com `DB_NAME`
próprio da worktree e os grupos `assistente` e `navegador` instalados.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente)
- **[Story]**: US1–US5 da spec

---

## Phase 0: Portão

- [X] T000 Spec, plano, tarefas, quickstart e checklist escritos (04/11/2026), só documentais, e revistos no mesmo dia com a revisão do PR #376 (D-015 a D-018; cenários B2, L, M, N, K2); `tests/test_citacoes_de_requisito.py` verde. O merge do PR aprova a spec
- [ ] T001 Aplicar as revisões de *Revisões de requisitos anteriores* da spec nos arquivos `specs/063-acompanhamento-pela-situacao/spec.md` (FR-1175, FR-1176, FR-1177, FR-1178), `specs/115-documentos-na-convocacao/spec.md` (FR-3577, FR-3612, User Story 2 cenário 2), `specs/059-acesso-a-convocacao/spec.md` (FR-1090, FR-1096, FR-1097) e `specs/029-requerimento-de-matricula/spec.md` (FR-405, FR-406), cada uma com a marca *"revisada pela `118` em ‹data›"* e a redação anterior preservada ao fim da alínea, no molde da FR-084 da `010`; `tests/test_citacoes_de_requisito.py` verde

## Phase 1: Setup

- [ ] T002 Linha de base: `make test-pg` com os grupos `assistente` e `navegador`; anotar totais e pulados em `specs/118-jornada-consolidada-do-convocado/verificacao.md` (novo)
- [ ] T003 [P] Acrescentar às listas literais das varreduras os arquivos que esta feature cria ou passa a usar: `tests/test_vocabulario_dos_documentos_da_convocacao.py` (`DA_115`), `tests/test_vocabulario_da_convocacao.py`, `tests/test_vocabulario_do_requerimento.py` e a varredura da `063` em `tests/portal/test_acompanhamento_pela_situacao.py` (FR-3751)
- [ ] T004 [P] Capturas "antes" dos cenários A–K pelo roteiro do PR #375, nas duas larguras, em `specs/118-jornada-consolidada-do-convocado/capturas/` (só se o PR #375 não estiver na `main`; senão, referenciar as dele)

---

## Phase 2: Foundational — a projeção (bloqueia US1–US5)

**Goal**: as obrigações da convocação, derivadas, sem consulta.
**Independent Test**: SC-1126.

### Tests

- [ ] T005 [P] `tests/unit/portal/test_obrigacoes_da_convocacao.py`: tabela de combinações estado do item × obrigatório/facultativo × os quatro momentos (aberta, encerrada pelo prazo, encerrada pelo Processo, decidida) × as seis linhas do Requerimento da FR-3725; cada combinação em exatamente uma categoria; Processo e prazo juntos dão *encerrada pelo Processo* para os documentos e *não enviado até o prazo* para o Requerimento; desfecho com o Processo aberto não reabre a escrita; o Requerimento pedido na convocação e não enviado nunca vira *não pedido* depois do desfecho, com ou sem rascunho; a ordem *pendência registrada (a corrigir, a enviar com motivo) → a enviar → Requerimento*; facultativo fora dos totais; nenhuma frase com "atendido", "enviou tudo", "aprovado" (FR-3721 a FR-3729, SC-1126)
- [ ] T006 [P] No mesmo arquivo, o texto literal de cada célula da FR-3746, nas quatro colunas, e o da frase de conclusão, com e sem opcional; com o prazo não iniciado e sem vencimento, nenhuma frase com "até" (FR-3728, FR-3746, FR-3749)
- [ ] T007 [P] Prova de zero consultas na projeção, no molde do teste de custo da situação da `063` (FR-3721)

### Implementation

- [ ] T008 Criar `processo_seletivo/portal/obrigacoes.py`: `Obrigacoes`, as categorias, `obrigacoes_da_convocacao()` e as constantes de texto (FR-3721 a FR-3729, FR-3746, FR-3749)
- [ ] T009 `convocacao/application/documentos.py`: `frase_do_prazo_decorrido` devolve o núcleo da FR-3748, com hora em `HHhMM`; as recusas de documento e de Requerimento continuam chamando-a (FR-3748)
- [ ] T010 `portal/views.py`: entregar à projeção as três leituras do Requerimento da `Disponibilidade` que `apurar` já devolve, e a causa do fechamento junto do booleano `pode_apresentar`, que continua sendo `aberta and causa is None` (o desfecho fecha antes de qualquer causa); o chamado de hoje continua derivado da mesma `Disponibilidade` (FR-3721, FR-3725, FR-1098 da `059`)

**Checkpoint**: a projeção existe e está provada; nenhuma tela mudou.

---

## Phase 3: US1 — quem tem documentos e Requerimento sabe que ainda falta (P1) 🎯 MVP

**Goal**: o acompanhamento representa o conjunto e leva à convocação.
**Independent Test**: cenários C1, C2 e B (SC-1117, SC-1118, SC-1123).

### Tests

- [ ] T011 [P] [US1] `tests/unit/portal/test_situacao_da_inscricao.py`: a tabela da FR-3730 linha a linha, inclusive a linha 2 (Processo); o enviado como linha secundária com documento; **sem documento, B e B2 exatamente como hoje**, com `REQUERIMENTO_ENVIADO` como ação principal em B2 (FR-3730, FR-3731, FR-3732)
- [ ] T012 [P] [US1] `tests/portal/test_acompanhamento_pela_situacao.py`: C1, C2, B e B2 renderizados; o link principal com documento leva à convocação; nenhum rótulo de link começa por "Enviar"; contagem de consultas com 0, 1 e 6 itens e sem convocação (FR-3730, FR-3732, FR-3734, SC-1117, SC-1123, SC-1125)
- [ ] T012a [P] [US4] `tests/unit/portal/test_situacao_da_inscricao.py` e `tests/portal/test_acompanhamento_pela_situacao.py`: G0 e N0, com e sem rascunho — a ação principal de hoje, a linha informativa sem link, nenhum link de preenchimento; B e B2 sem a linha; contagem de consultas igual à de antes; `tests/interface/test_portal_jornada_consolidada.py`: o mesmo na tela da convocação, e nenhuma linha gravada (FR-3732, FR-3743, D-019, SC-1128)

### Implementation

- [ ] T013 [US1] `portal/situacao.py`: `_acao_da_convocacao` recebe as obrigações; `Acao` ganha a linha secundária; as frases novas como constantes (FR-3730 a FR-3733, FR-1178 da `063` revista)
- [ ] T014 [US1] `portal/views.py`, `acompanhamento`: ler `leitura_da_chamada` só com convocação vigente e passar a projeção (FR-3734)
- [ ] T015 [US1] `portal/templates/portal/acompanhamento.html`: a linha secundária do Requerimento e a frase de conclusão, sem escrever frase no template (FR-3731)

**Checkpoint**: C2 não tem mais falsa conclusão no acompanhamento.

---

## Phase 4: US2 e US3 — a tela da convocação (P1)

**Goal**: cinco blocos; a pendência na primeira tela; o que está com a comissão não parece tarefa.
**Independent Test**: cenários A, D, E, F, H e J (SC-1118, SC-1119).

### Tests

- [ ] T016 [P] [US2] `tests/interface/test_portal_jornada_consolidada.py` (novo): a ordem dos títulos de segundo nível; o bloco 3 ausente sem tarefa **e** sem opcional; em L, o bloco *Documentos opcionais* com o formulário; as âncoras do bloco 1 apontam para cartões existentes; o rótulo do botão de navegação; "Envie o arquivo" em J; em K2, nenhuma data como prazo (FR-3735 a FR-3739, FR-3746, FR-3749, SC-1127)
- [ ] T017 [P] [US3] No mesmo arquivo: D, E e H sem "atendido", sem "Conforme" sozinho, sem "enviou tudo"; a frase de conclusão; o aproveitado conferido diz a origem (FR-3724, FR-3728, FR-3746, SC-1118)
- [ ] T018 [P] [US2] `tests/interface/test_portal_documentos_da_convocacao.py`, `tests/interface/test_permissoes_dos_documentos_da_convocacao.py`: as expectativas de texto da tabela do plano (FR-3746)

### Implementation

- [ ] T019 [US2] `portal/templates/portal/convocacao.html`: os cinco blocos com obrigações; a estrutura de hoje sem elas (FR-3735 a FR-3740, FR-3743)
- [ ] T020 [US2] `portal/templates/portal/_documentos_da_convocacao.html`: um cartão por *include*, com título `h3`, selo em texto, texto pronto da projeção, nome acessível dos botões e descrição acessível com a situação (FR-3744, FR-3745)
- [ ] T021 [P] [US2] `portal/static/portal/portal.css`: selos, destaque do cartão a corrigir, marcador, texto visualmente oculto; toda classe nova com regra (FR-3744)
- [ ] T022 [US2] `portal/views.py`, `convocacao`: passar a projeção; o redirecionamento do envio continua na âncora do item (FR-3736)

**Checkpoint**: F mostra a pendência no topo, com selo; D e E não parecem tarefa.

---

## Phase 5: US4 — depois do prazo e depois do resultado (P1)

**Goal**: a tela só conta o que houve.
**Independent Test**: cenários G, I1 e I2 (SC-1120).

### Tests

- [ ] T023 [P] [US4] `tests/interface/test_portal_jornada_consolidada.py`: G com "O prazo terminou", o resumo e o Requerimento não enviado, sem formulário; M com "O envio pelo portal está encerrado", sem "prazo terminou", sem "vai conferir", sem formulário de documento e com o Requerimento a preencher no bloco 3; N com "Requerimento de Matrícula: não enviado."; I1 e I2 com zero formulários e zero "Envie até", "Falta enviar", "aguardando conferência"; "Vaga aceita" e a frase do aceite nas duas telas (FR-3725, FR-3741, FR-3742, FR-3750, SC-1120, SC-1127)
- [ ] T024 [P] [US4] `tests/interface/test_portal_requerimento.py`: G sem requerimento vigente responde "O prazo terminou" sem 409, sem linha nova; N, com e sem rascunho e com e sem documento, responde "Requerimento de Matrícula não enviado", nunca "Ainda não é a hora"; quem não tem convocação continua com "Ainda não é a hora"; o enviado com "Voltar à convocação" e a explicação por momento; o aviso do envio com documento (FR-3752, FR-3754, FR-3755)
- [ ] T025 [P] [US4] `tests/integration/requerimentos/test_prazo_da_chamada.py`, `tests/integration/convocacao/test_documentos_da_convocacao.py`: o mesmo núcleo nas duas recusas por prazo; a recusa do documento com o Processo encerrado não usa o núcleo (FR-3748)
- [ ] T025a [P] `tests/interface/test_portal_jornada_consolidada.py`: garantias do novo caminho de leitura — contagem de linhas de todas as tabelas antes e depois de um GET de cada tela em cada cenário (só a leitura da convocação na trilha muda; o GET de G no Requerimento não cria rascunho); inscrição alheia e inexistente com a mesma recusa nas três telas; a página do Requerimento continua com resposta privada (FR-3756, SC-1127)

### Implementation

- [ ] T026 [US4] Templates da convocação e do acompanhamento: os estados *encerrada pelo prazo*, *encerrada pelo Processo* e *decidida*; o rótulo de `DESFECHOS` na convocação; a frase do aceite em `portal/situacao.py` (FR-3741, FR-3742, FR-3750)
- [ ] T027 [US4] `requerimentos/application/selectors.py` e `portal/views.py`, `requerimento`: explicação por momento; o vencido sem requerimento vigente antes de `abrir_rascunho`; o aviso do envio; `requerimento.html` com *"Voltar à convocação"* (FR-3752, FR-3754, FR-3755)

---

## Phase 6: US5 — o prazo é um só (P2)

**Goal**: um formato, um núcleo, e o prazo não iniciado sem data.
**Independent Test**: cenários K e G, e todas as telas (SC-1121).

- [ ] T028 [US5] Formato *"até DD/MM/AAAA, às HHhMM"* em `acompanhamento.html`, `_convocacao_da_inscricao.html`, `convocacao.html`, nos cartões e em `requerimento.html`; *"contado do envio da comunicação"* só nos dados da convocação; a frase da FR-3749 (FR-3747, FR-3749, FR-3753); ajustar `tests/integration/convocacao/test_reenvio_nao_reinicia_prazo.py` e `tests/interface/test_portal_caminho_da_convocacao.py`

---

## Phase 7: Navegador, capturas e verificação

- [ ] T029 [P] `tests/navegador/test_jornada_consolidada_do_convocado.py` (novo): os cenários A–K e B2, L, M, N, K2, G0, N0 a 375 px e em desktop; Tab linear e foco visível; nomes acessíveis únicos; sem rolagem horizontal; sem violação de CSP no console; o bloco 1 dentro da primeira tela em A, C1, C2, F e J; ajustar `tests/navegador/test_jornada_dos_documentos_da_convocacao.py` (SC-1119, SC-1121, SC-1122, SC-1127)
- [ ] T030 `specs/118-jornada-consolidada-do-convocado/rastreabilidade.md`: uma linha por FR e SC desta spec, com o teste que a prova (`tests/test_citacoes_de_requisito.py` cobra)
- [ ] T031 Capturas "depois" dos cenários A–K, B2, L, M, N, K2, G0, N0 e dos dois de controle, com o mesmo nome do relatório, em `capturas/`
- [ ] T032 `verificacao.md`: para cada cenário, as quatro perguntas respondidas com o texto literal da tela (SC-1124); a busca, nos testes, pelos **textos que saem** da lista do plano — vazia, salvo onde o teste prova a ausência —, e a confirmação de que os que **ficam** continuam presos; cada expectativa alterada justificada por cenário, com a garantia anterior ainda provada; totais da suíte contra a linha de base
- [ ] T033 `make lint check test-pg` (os dois passos do `lint`); linha do README da `118` atualizada; o `CLAUDE.md` não muda (nenhuma tabela append-only nova)

---

## Dependencies & Execution Order

- **T001 antes de tudo**: os guardiões da `063` leem as constantes, e a spec revista é a referência dos testes.
- **Phase 2 bloqueia as histórias.** US1 (Phase 3) é o MVP e pode ir sozinha; US2/US3 (Phase 4) dependem da projeção, não de US1; US4 depende de Phase 4 (os blocos); US5 toca templates de todas, e vem depois.
- **[P]** dentro de cada fase: testes em arquivos diferentes.
- **Uma entrega só** (D-001): todas as fases no mesmo PR de implementação. Separar o polish só com impedimento técnico demonstrado, registrado em `verificacao.md`.

## Notes

- Nenhuma tarefa cria migration, rota, comando ou mensagem (FR-3756). Se alguma parecer exigir, parar e registrar.
- Editar template durante a suíte falseia o resultado; rodar a suíte com a árvore parada.
- O roteiro de captura do PR #375 monta os cenários pelas fixtures; reaproveitá-lo, e não montar à mão.
