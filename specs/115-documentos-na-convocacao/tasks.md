# Tasks: Documentos e conferência na convocação (115)

**Input**: [spec.md](spec.md), [plan.md](plan.md), [data-model.md](data-model.md),
[quickstart.md](quickstart.md)

> **Nenhuma tarefa começa antes da aprovação do usuário** (Status da spec). A T000 é o portão.

**Tests**: pedidos. Cada FR, SC e caso-limite terá teste na matriz de rastreabilidade (T049). Os
testes de cada história vêm antes da implementação dela e devem falhar primeiro.

Caminhos relativos a `backend/`. Suíte sempre contra PostgreSQL (`make test-pg`), com `DB_NAME`
próprio da worktree.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente)
- **[Story]**: US1–US8 da spec

---

## Phase 0: Portão

- [X] T000 Revisão do usuário (03/11/2026, no PR #368): aprovadas a QI-2′, a D-010, a D-012 e a D-018; ajustadas a D-011 e a D-013. Spec, plano e tarefas revistos. O merge do PR aprova a spec
- [X] T001 Revisão da FR-402 aplicada em `specs/029-requerimento-de-matricula/spec.md`, com a marca "revisada pela `115`" e a redação anterior preservada; `tests/test_citacoes_de_requisito.py` verde

## Phase 1: Setup

- [ ] T002 Linha de base: rodar `make test-pg` com o grupo `navegador` e anotar totais e pulados em `specs/115-documentos-na-convocacao/verificacao.md` (novo)

---

## Phase 2: Foundational — momento e aproveitamento (US7) 🎯 entregável sozinho

**Goal**: o Edital declara o momento; a inscrição pede só o da inscrição; o PDF ganha a seção.
**Independent Test**: US7; nenhum Edital existente muda (SC-1085).

### Tests

- [ ] T003 [P] [US7] `tests/unit/editais/test_momento_do_documento.py`: ausência lida como inscrição; `da_inscricao()` e `da_convocacao()`; validação do aproveitamento, nas recusas da FR-3566 (FR-3563, FR-3565, FR-3566, FR-3567)
- [ ] T004 [P] [US7] Estender a fixture `rascunho_completo` (`tests/fixtures/snapshot.py`) com os dois campos; `tests/contract/test_mutabilidade.py` passa sem edição; `tests/interface/test_campos_vem_do_contrato.py` continua em 84 (FR-3564, FR-3570)
- [ ] T005 [P] [US7] `tests/unit/publicacoes/test_elevacao.py`: degrau 18 (FR-3563)
- [ ] T006 [P] [US7] `tests/integration/publicacoes/test_secao_da_convocacao.py`: as duas seções, a frase do aproveitamento, sem termo proibido no título; o Edital sem documento da convocação gera o PDF de antes, comparado normalizado (FR-3569, SC-1085)
- [ ] T007 [P] [US7] `tests/integration/inscricoes/test_documento_da_convocacao_fora_da_inscricao.py`: rascunho, envio, lista exigida, Mesa e portal da inscrição ignoram o documento da convocação (FR-3568, FR-3571, SC-1084)

### Implementation

- [ ] T008 [US7] `editais/models/documentos.py` + migration `editais/0024`: `momento`, `aproveita`, check (data-model)
- [ ] T009 [US7] `editais/application/draft.py`, `editais/api/serializers.py`, `interface/forms.py`, `interface/templates/interface/_documento.html`: os campos viajam e são editáveis ("Quando é pedido", "Atendido pelo documento da inscrição")
- [ ] T010 [US7] `editais/domain/validation.py`, `editais/domain/documentos.py`: schema, regras do aproveitamento, `da_inscricao()`/`da_convocacao()`
- [ ] T011 [US7] `inscricoes/application/lista_exigida.py`, `submissao.py`, `rascunho.py`, portal da inscrição e `duvidas/domain/cobertura.py`: passam por `da_inscricao()`
- [ ] T012 [US7] `editais/domain/mutabilidade.py` (dois pares não retificáveis, com razão), `publicacoes/application/publish_edital.py`, `publicacoes/domain/elevacao.py`, `shared/canonical.py` (18), `interface/revisao.py`, `publicacoes/domain/alteracoes.py`
- [ ] T013 [US7] `editais/domain/secoes.py`, `publicacoes/infrastructure/pdf.py`, `apresentacao.py`: a seção da convocação

**Checkpoint**: Editais existentes intactos; a inscrição pede menos.

---

## Phase 3: User Story 1 + 3 — lista, apresentação e aproveitamento (P1)

**Goal**: a raiz da chamada grava a lista; o titular apresenta pelo portal; o aproveitamento é por
referência.

### Tests

- [ ] T014 [P] [US1] `tests/integration/convocacao/test_lista_da_convocacao.py`: lista na raiz (individual, lote de titulares, suplência, para regularizar); sucessora sem lista própria; Retificação posterior não altera; chamada nova grava lista nova; convocação anterior sem lista; sem exigência = sem itens (FR-3572 a FR-3575)
- [ ] T015 [P] [US3] `tests/integration/convocacao/test_aproveitamento.py`: referência sem cópia (nenhum arquivo novo no armazenamento, mesmo hash); sem documento na inscrição, a apresentar; nada entre inscrições (FR-3576, SC-1083)
- [ ] T016 [P] [US1] `tests/integration/convocacao/test_apresentacao.py`: versões, vigente, substituição da referência, recusas (FR-3577 a FR-3580, FR-3582, FR-3583)
- [ ] T017 [P] [US1] `tests/integration/convocacao/test_concorrencia_da_apresentacao.py` (transacional): idempotência, mesmo hash, duplo envio concorrente (FR-3581)
- [ ] T018 [P] [US1] `tests/integration/test_database_permissions.py` e `tests/seguranca/test_homologacao_preservada.py`: 49 tabelas; gatilhos de coerência; `PROTECT` (SC-1090)

### Implementation

- [ ] T019 [US1] `convocacao/models.py` + migration `convocacao/0005` com gatilhos; `seguranca/papeis.py` (+3); a linha do `N de M` no `CLAUDE.md`
- [ ] T020 [US1] `convocacao/application/lista.py` e chamadas em `convocar.py` e `fluxo.py` (R-002, R-003)
- [ ] T021 [US1] `convocacao/application/apresentar.py` (R-004)
- [ ] T022 [US1] `portal/views.py`, `portal/situacao.py`, `portal/templates/portal/convocacao.html`, `_documentos_da_convocacao.html`, `portal/urls.py`, `portal/static/portal/portal.css`: lista, estados, envio, modelo anexo e entrega ao titular (FR-3577, FR-3584, FR-3612, FR-3613)

**Checkpoint**: o convocado apresenta; nada mudou na gestão ainda.

---

## Phase 4: User Story 5 + 1 + 4 — autorização, conferência e desfecho (P1)

### Tests

- [ ] T023 [P] [US5] `tests/unit/comissoes/test_pode_conferir_documentos.py`: as bases, o Perfil, o escopo alheio, o membro inativado (FR-3595 a FR-3597)
- [ ] T024 [P] [US5] `tests/interface/test_permissoes_dos_documentos_da_convocacao.py`: a matriz de permissões inteira, linha a linha (FR-3598 a FR-3601, SC-1087)
- [ ] T025 [P] [US1] `tests/unit/convocacao/test_estado_documental.py`: tabelas da FR-3590 e da FR-3591, precedência
- [ ] T026 [P] [US1] `tests/integration/convocacao/test_conferencia.py`: os três resultados e os motivos; substituição; versão superada; depois do desfecho; depois do vencimento; "conforme" sem abertura (FR-3585 a FR-3589, FR-3611)
- [ ] T027 [P] [US1] `tests/integration/convocacao/test_guarda_do_aceite.py`: aceite e regularização recusados; facultativo adverte; os outros desfechos livres; desfecho sucessor que inclui também guardado (FR-3592, FR-3593, SC-1086)
- [ ] T028 [P] [US4] `tests/integration/convocacao/test_vencimento_sem_automatismo.py`: nada nasce do decurso; recusa do envio; a sucessão com vencimento novo reabre o envio e mantém a lista (FR-3593, FR-3618)

### Implementation

- [ ] T029 [US5] `comissoes/models.py` + migration, `comissoes/domain/autorizacao.py` (`pode_conferir_documentos`), `comissoes/application/alocacao.py`
- [ ] T030 [US5] `interface/views.py`, `interface/templates/interface/alocacoes.html`: alocar e revogar à conferência
- [ ] T031 [US1] `convocacao/domain/documentos.py`, `convocacao/domain/nomes.py`, `convocacao/application/conferir.py` (R-005)
- [ ] T032 [US1] `convocacao/application/desfechar.py`: a guarda (R-006)
- [ ] T033 [US1] `interface/views.py`, `interface/urls.py`, `interface/templates/interface/convocacao_documentos.html`, `interface/static/interface/telas/convocacao_documentos.css`: página filha, entrega com hash, conferir (FR-3605, FR-3606, FR-3608, FR-3609)
- [ ] T034 [US1] `interface/templates/interface/convocacao.html` e a view da condução: resumo, ordem, filtro por Perfil da alocação, "Apto para formalização", fundamento pré-redigido, recusa antecipada (FR-3594, FR-3607, FR-3610)
- [ ] T035 [US5] `specs/033-navegacao-por-capacidade/inventario-das-negativas.md`: uma linha por view nova com `raise Http404`

**Checkpoint**: US1, US3 e US5 completas.

---

## Phase 5: User Story 2 — bolsista (P1)

- [ ] T036 [P] [US2] `tests/integration/convocacao/test_cenario_do_bolsista.py`: Edital sem Requerimento, um documento com modelo anexo; aceite; varredura de termos (US2, SC-1082)
- [ ] T037 [US2] Ajustes que o teste revelar. O esperado é nenhum: a capacidade já é neutra

---

## Phase 6: User Story 6 — trilha e A-07 (P2)

- [ ] T038 [P] [US6] `tests/integration/auditoria/test_trilha_dos_documentos_da_convocacao.py`: um registro por ato, com ator e unidade, sem nome nem motivo; a trilha do Edital os mostra; a da unidade não (FR-3602, FR-3603, SC-1088)
- [ ] T039 [P] [US6] `tests/interface/test_consulta_ao_dossie.py`: abrir o dossiê grava `CONSULTAR_DOSSIE` (FR-3604)
- [ ] T040 [US6] `interface/views.py` (`inscricao_recebida`, página filha), `auditoria/selectors.py` (`_atos_da_conducao`), rótulos em `OPERACOES` e `AGREGADOS` (R-009)

---

## Phase 7: User Story 8 + 4 — aproveitamento entre chamadas e prazo da chamada no Requerimento (P2)

- [X] T052 Revisão da FR-374, da FR-408, da frase da FR-411 e do caso-limite do prazo aplicada em `specs/029-requerimento-de-matricula/spec.md`, com a marca "revisada pela `115`" e as redações anteriores preservadas (D-019, segunda rodada, 03/11/2026); `tests/test_citacoes_de_requisito.py` verde
- [ ] T053 [P] [US4] `tests/unit/requerimentos/test_disponibilidade.py` (estendido) e `tests/integration/requerimentos/test_prazo_da_chamada.py`: antes e depois do vencimento, prazo não iniciado, sem vencimento, com e sem documento na chamada, sucessor recusado nos dois momentos, correção reabrindo tudo, convocação para regularizar abrindo de novo. Antes de escrever, procurar de novo teste que presuma o requerimento aberto depois do vencimento, e listar o que mudar (FR-3622, SC-1093; FR-374 e FR-408 da `029`)
- [ ] T054 [US4] `requerimentos/domain/disponibilidade.py`, `requerimentos/application/preencher.py`, `requerimentos/application/selectors.py` (docstring), `portal/views.py`, `portal/situacao.py`: `prazo_decorrido` injetado e frase única (R-013)
- [ ] T055 [P] [US8] `tests/integration/convocacao/test_aproveitamento_entre_chamadas.py`: origem sem cópia e sem corrente; pendente não aproveitado; requisito novo; conferência não transportada; abertura por chamada; indicação de exigência retificada (FR-3619 a FR-3621, FR-3611, SC-1092)
- [ ] T056 [US8] `convocacao/application/lista.py` (precedência do R-003), gatilho de coerência da `apresentacao_de_origem`, página de documentos e portal (FR-3612, FR-3621)

---

## Phase 8: Polish & Cross-Cutting

- [ ] T041 [P] Vocabulário: incluir os templates novos nas varreduras literais, e uma varredura dos termos da FR-3610 e da FR-3589 (`tests/interface/test_vocabulario_dos_documentos_da_convocacao.py`)
- [ ] T042 [P] CSP e folha: classes com regra; nenhum inline (`test_politica_de_conteudo`, `test_acessibilidade`, `test_estaticos`)
- [ ] T043 [P] Orçamento de consultas da condução com e sem documentos (plan, *Performance Goals*)
- [ ] T044 [P] Regressão: `test_convivencia_com_o_anexo.py`, `test_situacoes_de_mensagem.py` e `test_dependencia_da_convocacao.py` inalterados e verdes (FR-3583, FR-3614, FR-3617)
- [ ] T045 [P] Encerramento: convocação em aberto de Edital encerrado aceita apresentação e conferência (FR-3616)
- [ ] T046 [P] Nada se exclui: tentativas de `delete` no modelo, no banco e no privilégio (FR-3615)
- [ ] T047 Navegador: `tests/navegador/test_jornada_dos_documentos_da_convocacao.py`, com as três jornadas obrigatórias e a da chamada nova, a 375 px e desktop, sem violação de CSP (SC-1081, SC-1089, SC-1091)
- [ ] T048 README: atualizar a linha da `115` na tabela de incrementos para "Implementada"
- [ ] T049 `specs/115-documentos-na-convocacao/rastreabilidade.md`: todo FR, SC e caso-limite → tarefa → teste
- [ ] T050 Verificação completa: `make lint check test-pg` com os dois grupos opcionais; anotar em `verificacao.md` os totais e a diferença de pulados por arquivo e motivo, em relação à T002
- [ ] T051 Percorrer o [quickstart](quickstart.md) no navegador do painel e registrar as capturas

---

## Dependencies & Execution Order

- T000 bloqueia tudo. T001 depende da decisão sobre a D-018.
- A Phase 2 bloqueia as seguintes: a lista lê o momento.
- A Phase 3 bloqueia a 4: a conferência lê a apresentação.
- As Phases 5 e 6 dependem da 4 e são independentes entre si.
- A Phase 7 depende da 4.
- A Phase 8 vem por último.

### Parallel

Dentro de cada fase, os testes [P] são de arquivos distintos. As implementações tocam
`interface/views.py` em mais de uma tarefa e por isso são sequenciais.

## Implementation Strategy

1. **MVP técnico** = Phase 2: já reduz a coleta, porque o elaborador para de pedir na inscrição. Mas
   sem a Phase 3 o documento movido não é recebido em lugar nenhum. Por isso a Phase 2 **não vai à
   `main` sozinha** sem a 3.
2. **MVP de uso** = Phases 2 a 4: os três cenários.
3. Depois: 5, 6, 7 e 8.
