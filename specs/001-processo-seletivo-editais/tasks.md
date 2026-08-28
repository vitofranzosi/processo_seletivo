---
description: "Tarefas de implementação de Processo Seletivo e Editais"
---

# Tasks: Processo Seletivo e Editais

**Input**: artefatos em `/specs/001-processo-seletivo-editais/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/openapi.yaml` e `quickstart.md`

**Tests**: obrigatórios para regras críticas conforme a Constituição e os 29 cenários de aceitação.

**Organization**: tarefas agrupadas por história, com testes escritos antes da implementação e caminhos exatos.

## Formato: `[ID] [P?] [Story] Descrição`

- **[P]**: executável em paralelo sem conflito de arquivo ou dependência incompleta
- **[Story]**: história rastreada (`US1` a `US7`)

## Phase 1: Setup

**Purpose**: inicializar o backend Python/Django e a disciplina de qualidade.

- [X] T001 Criar projeto Python 3.13 e dependências Django 5.2 LTS, DRF, psycopg, pytest e pytest-django em backend/pyproject.toml
- [X] T002 Criar comandos reprodutíveis de lint, testes e validação OpenAPI em backend/Makefile
- [X] T003 [P] Configurar Ruff, cobertura e markers pytest em backend/pyproject.toml
- [X] T004 [P] Criar variáveis documentadas para desenvolvimento e teste em backend/.env.example
- [X] T005 Criar projeto Django e configurações por ambiente em backend/manage.py e backend/config/settings/
- [X] T006 [P] Configurar rotas raiz, Problem Details e correlation ID em backend/config/urls.py e backend/processo_seletivo/shared/api/
- [X] T007 [P] Criar apps processos, editais, publicacoes, seguranca e auditoria em backend/processo_seletivo/
- [X] T008 Configurar PostgreSQL, UTC, America/Sao_Paulo e credenciais separadas de runtime/migration em backend/config/settings/base.py
- [X] T009 [P] Criar fixtures de atores, relógio controlável e fábrica de IDs em backend/tests/fixtures/
- [X] T010 Criar pipeline de checks, migrations e testes PostgreSQL em .github/workflows/backend.yml

---

## Phase 2: Foundational

**Purpose**: infraestrutura bloqueadora comum a todas as histórias.

**⚠️ CRITICAL**: nenhuma história começa antes desta fase.

- [X] T011 Criar tipos de ator, escopo institucional, permissões e política deny-by-default em backend/processo_seletivo/seguranca/domain.py
- [X] T012 [P] Implementar autenticação adaptável ao provedor institucional em backend/processo_seletivo/seguranca/api/authentication.py
- [X] T013 Implementar autorização contextual e filtragem anti-IDOR em backend/processo_seletivo/seguranca/application/authorization.py
- [X] T014 [P] Implementar exceções de domínio e mapeamento application/problem+json em backend/processo_seletivo/shared/api/problems.py
- [X] T015 [P] Implementar ETag/If-Match e compare-and-swap de revision em backend/processo_seletivo/shared/concurrency.py
- [X] T016 [P] Implementar Idempotency-Key persistente com hash de request em backend/processo_seletivo/shared/idempotency.py
- [X] T017 Implementar base de commands com transaction.atomic(), instante único e on_commit em backend/processo_seletivo/shared/application/commands.py
- [X] T018 [P] Implementar serialização canônica versionada e SHA-256 em backend/processo_seletivo/shared/canonical.py
- [X] T019 Criar RegistroAuditoria append-only e serviço de gravação transacional em backend/processo_seletivo/auditoria/models.py e backend/processo_seletivo/auditoria/application.py
- [X] T020 Criar migration inicial de auditoria com trigger anti-update/delete e grants da role runtime em backend/processo_seletivo/auditoria/migrations/0001_initial.py
- [X] T021 [P] Criar testes de autorização, Problem Details, ETag e idempotência em backend/tests/authorization/test_foundation.py
- [X] T022 Criar testes PostgreSQL de CAS, rollback, trigger append-only e migrations em backend/tests/integration/test_foundation.py

**Checkpoint**: fundação pronta; histórias podem avançar conforme as dependências abaixo.

---

## Phase 3: User Story 1 — Estruturar Processo Seletivo e Edital (P1) 🎯 MVP

**Goal**: criar Processo e primeiro Edital atomicamente, adicionar Editais independentes e praticar ativação.

**Independent Test**: criar Processo + primeiro Edital, adicionar o segundo e ativar o Processo, provando identidades, vínculos e revisões independentes e rollback integral em entrada inválida.

### Tests for User Story 1

- [X] T023 [P] [US1] Criar testes de domínio para estados e invariantes Processo/Edital em backend/tests/unit/processos/test_domain.py
- [X] T024 [P] [US1] Criar testes de contrato para criação e commands de Processo em backend/tests/contract/test_processos_api.py
- [X] T025 [P] [US1] Criar testes de integração para atomicidade, unicidade e Editais independentes em backend/tests/integration/processos/test_creation.py
- [X] T026 [P] [US1] Criar testes de autorização e anti-IDOR da US1 em backend/tests/authorization/test_processos.py

### Implementation for User Story 1

- [X] T027 [P] [US1] Implementar modelos ProcessoSeletivo, Edital e AtoAdministrativo em backend/processo_seletivo/processos/models.py
- [X] T028 [US1] Criar constraints, índices e migration inicial de Processo/Edital em backend/processo_seletivo/processos/migrations/0001_initial.py
- [X] T029 [US1] Implementar commands criar processo, adicionar edital e ativar processo em backend/processo_seletivo/processos/application/commands.py
- [X] T030 [US1] Implementar serializers, views e rotas administrativas da US1 em backend/processo_seletivo/processos/api/
- [X] T031 [US1] Integrar auditoria, idempotência, ETag e autorização nos commands da US1 em backend/processo_seletivo/processos/application/commands.py
- [X] T032 [US1] Rastrear US1 e FR-001–FR-008 nos testes de aceitação em backend/tests/acceptance/test_us1_processos_editais.py

**Checkpoint**: MVP funcional e testável de forma independente.

---

## Phase 4: User Story 2 — Configurar Perfis, Vagas e Concorrência (P1)

**Goal**: estruturar Perfis, vagas, Cadastro Reserva e modalidades sem misturar Editais.

**Independent Test**: salvar múltiplos Perfis com reservas distintas e rejeitar cardinalidades, limites e vínculos inválidos sem alterar outro Edital.

### Tests for User Story 2

- [X] T033 [P] [US2] Criar testes de domínio de Perfil, vagas, reserva e modalidades em backend/tests/unit/editais/test_perfis.py
- [X] T034 [P] [US2] Criar testes de contrato do rascunho estruturado em backend/tests/contract/test_edital_draft_api.py
- [X] T035 [P] [US2] Criar testes PostgreSQL de constraints e isolamento entre Editais em backend/tests/integration/editais/test_perfis.py

### Implementation for User Story 2

- [X] T036 [P] [US2] Implementar PerfilVaga, ModalidadeConcorrencia e RegraNormativa em backend/processo_seletivo/editais/models/perfis.py
- [X] T037 [US2] Criar constraints e migration de Perfis, vagas e modalidades em backend/processo_seletivo/editais/migrations/0001_perfis.py
- [X] T038 [US2] Implementar validação e substituição transacional do rascunho de Perfis em backend/processo_seletivo/editais/application/draft.py
- [X] T039 [US2] Implementar serializers de Perfil, reserva e modalidades em backend/processo_seletivo/editais/api/serializers.py
- [X] T040 [US2] Integrar Perfis ao endpoint PUT de rascunho com ETag em backend/processo_seletivo/editais/api/views.py
- [X] T041 [US2] Rastrear US2 e FR-009–FR-014 nos testes de aceitação em backend/tests/acceptance/test_us2_perfis.py

---

## Phase 5: User Story 3 — Definir Cronograma Independente (P1)

**Goal**: manter Cronograma próprio e Eventos válidos para cada Edital.

**Independent Test**: configurar datas diferentes em dois Editais e rejeitar período invertido ou Evento vinculado ao Edital errado.

### Tests for User Story 3

- [X] T042 [P] [US3] Criar testes de domínio para Evento pontual, período, ordem e fuso institucional em backend/tests/unit/editais/test_cronograma.py
- [X] T043 [P] [US3] Criar testes de integração de isolamento e constraints do Cronograma em backend/tests/integration/editais/test_cronograma.py
- [X] T044 [P] [US3] Criar testes de contrato dos Eventos no rascunho em backend/tests/contract/test_cronograma_api.py

### Implementation for User Story 3

- [X] T045 [P] [US3] Implementar Cronograma e EventoCronograma em backend/processo_seletivo/editais/models/cronograma.py
- [X] T046 [US3] Criar constraints, índices e migration do Cronograma em backend/processo_seletivo/editais/migrations/0002_cronograma.py
- [X] T047 [US3] Implementar política temporal e validação de vínculos em backend/processo_seletivo/editais/domain/cronograma.py
- [X] T048 [US3] Integrar Cronograma ao command e serializers do rascunho em backend/processo_seletivo/editais/application/draft.py e backend/processo_seletivo/editais/api/serializers.py
- [X] T049 [US3] Rastrear US3 e FR-015–FR-018 nos testes de aceitação em backend/tests/acceptance/test_us3_cronograma.py

---

## Phase 6: User Story 4 — Validar e Publicar Edital (P1)

**Goal**: revisar, homologar e publicar somente conteúdo consistente, segregado e imutável.

**Independent Test**: bloquear erro impeditivo, manter avisos, exigir participante distinto e publicar atomicamente snapshot, PDF, hashes e auditoria da revisão homologada.

### Tests for User Story 4

- [X] T050 [P] [US4] Criar testes de domínio da máquina de estados e validation findings em backend/tests/unit/editais/test_publicacao.py
- [X] T051 [P] [US4] Criar testes de contrato das rotas explícitas de submissão, homologação, revogação e publicação, incluindo Autoridade Signatária obrigatória, em backend/tests/contract/test_publicacao_edital_api.py
- [X] T052 [P] [US4] Criar testes de autorização para segregação de funções e escopo em backend/tests/authorization/test_publicacao.py
- [X] T053 [P] [US4] Criar testes PostgreSQL de rollback, imutabilidade e publicação concorrente em backend/tests/integration/publicacoes/test_publicar_edital.py

### Implementation for User Story 4

- [X] T054 [P] [US4] Implementar RevisaoEdital, Homologacao, Publicacao e DocumentoPublicado em backend/processo_seletivo/publicacoes/models.py
- [X] T055 [US4] Criar migration de publicação, unicidade e triggers append-only em backend/processo_seletivo/publicacoes/migrations/0001_initial.py
- [X] T056 [P] [US4] Implementar validador de completude e severidades em backend/processo_seletivo/editais/domain/validation.py
- [X] T057 [P] [US4] Implementar porta e renderizador inicial de PDF determinístico em backend/processo_seletivo/publicacoes/infrastructure/pdf.py
- [X] T058 [US4] Implementar commands submeter, homologar, revogar e publicar com locks e revalidação em backend/processo_seletivo/publicacoes/application/publish_edital.py
- [X] T059 [US4] Implementar rotas administrativas explícitas de submissão, homologação, revogação, publicação e download imutável em backend/processo_seletivo/publicacoes/api/
- [X] T060 [US4] Rastrear US4 e FR-019–FR-024, FR-032–FR-033, FR-036 e FR-038 em backend/tests/acceptance/test_us4_publicacao.py

---

## Phase 7: User Story 5 — Retificar sem Reescrever o Passado (P1)

**Goal**: elaborar e publicar Retificações cumulativas com vigência e consolidação determinísticas.

**Independent Test**: publicar Retificações imediatas, futuras, fora de ordem e empatadas, preservando original, deltas, consolidados, PDFs e proveniência.

### Tests for User Story 5

- [X] T061 [P] [US5] Criar testes puros da composição temporal, conflitos e canonicalização em backend/tests/unit/publicacoes/test_consolidacao.py
- [X] T062 [P] [US5] Criar testes de contrato das rotas explícitas de criação, edição, submissão, homologação, publicação e cancelamento de Retificação em backend/tests/contract/test_retificacoes_api.py
- [X] T063 [P] [US5] Criar testes PostgreSQL de sequência, locks, append-only e Retificação obsoleta em backend/tests/integration/publicacoes/test_retificacoes.py
- [X] T064 [P] [US5] Criar testes de autorização e segregação de Retificação em backend/tests/authorization/test_retificacoes.py

### Implementation for User Story 5

- [X] T065 [P] [US5] Implementar Retificacao, AlteracaoNormativa, VersaoConsolidada e ProvenienciaConteudo em backend/processo_seletivo/publicacoes/models_retificacao.py
- [X] T066 [US5] Criar migration de Retificações, snapshots, proveniência e índices temporais em backend/processo_seletivo/publicacoes/migrations/0002_retificacoes.py
- [X] T067 [P] [US5] Implementar aplicação determinística de alterações por caminho normativo em backend/processo_seletivo/publicacoes/domain/changes.py
- [X] T068 [US5] Implementar consolidador por effectiveAt/publishedAt/publicationOrder em backend/processo_seletivo/publicacoes/domain/consolidation.py
- [X] T069 [US5] Implementar commands criar, editar, submeter, homologar, publicar e cancelar Retificação em backend/processo_seletivo/publicacoes/application/retificacoes.py
- [X] T070 [US5] Implementar API administrativa de Retificações com ETag e idempotência em backend/processo_seletivo/publicacoes/api/views.py e backend/processo_seletivo/publicacoes/api/urls.py
- [X] T071 [US5] Rastrear US5 e FR-025–FR-030 e FR-039 nos testes de aceitação em backend/tests/acceptance/test_us5_retificacoes.py

---

## Phase 8: User Story 6 — Consultar Conteúdo Vigente e Histórico (P2)

**Goal**: expor somente conteúdo publicado, vigente ou histórico, com proveniência e documentos exatos.

**Independent Test**: consultar antes, nas fronteiras e depois dos atos e obter versão, histórico e PDF corretos sem qualquer rascunho ou dado administrativo.

### Tests for User Story 6

- [X] T072 [P] [US6] Criar testes de contrato de versão vigente, histórico paginado e consultas diretas de Publicação, Retificação e versão consolidada em backend/tests/contract/test_consulta_publica_api.py
- [X] T073 [P] [US6] Criar testes temporais de fronteira e recomposição de até 20 Retificações em backend/tests/integration/publicacoes/test_consulta_temporal.py
- [X] T074 [P] [US6] Criar testes de não exposição de drafts, auditoria e dados internos em backend/tests/authorization/test_consulta_publica.py

### Implementation for User Story 6

- [X] T075 [P] [US6] Implementar selectors de versão vigente e histórico paginado em backend/processo_seletivo/publicacoes/application/selectors.py
- [X] T076 [P] [US6] Implementar projeções públicas versionadas e proveniência em backend/processo_seletivo/publicacoes/api/public_serializers.py
- [X] T077 [US6] Implementar endpoints públicos de versão vigente, histórico, Publicação, Retificação, versão consolidada e documento com cache HTTP em backend/processo_seletivo/publicacoes/api/public_views.py e backend/processo_seletivo/publicacoes/api/public_urls.py
- [X] T078 [US6] Rastrear US6 e FR-028–FR-031 e FR-039 nos testes de aceitação em backend/tests/acceptance/test_us6_consulta_publica.py

---

## Phase 9: User Story 7 — Cancelar ou Encerrar com Preservação (P2)

**Goal**: encerrar regularmente ou cancelar por ato explícito, preservando todo o histórico.

**Independent Test**: encerrar Edital concluído, bloquear cancelamento do Processo com Edital não final e permitir o ato após todos estarem encerrados/cancelados, inclusive sob concorrência.

### Tests for User Story 7

- [X] T079 [P] [US7] Criar testes de domínio de encerramento, cancelamento e estados finais em backend/tests/unit/processos/test_finalizacao.py
- [X] T080 [P] [US7] Criar testes de contrato dos atos de encerramento e cancelamento em backend/tests/contract/test_finalizacao_api.py
- [X] T081 [P] [US7] Criar testes PostgreSQL do protocolo de locks Processo→Editais e TOCTOU em backend/tests/integration/processos/test_finalizacao_concorrente.py
- [X] T082 [P] [US7] Criar testes de autorização, motivo e auditoria dos atos finais em backend/tests/authorization/test_finalizacao.py

### Implementation for User Story 7

- [X] T083 [US7] Implementar política de estados finais e bloqueios em backend/processo_seletivo/processos/domain/finalizacao.py
- [X] T084 [US7] Implementar commands de encerramento/cancelamento com locks ordenados e auditoria em backend/processo_seletivo/processos/application/finalizacao.py
- [X] T085 [US7] Integrar atos finais às rotas e responses administrativas em backend/processo_seletivo/processos/api/finalizacao.py e backend/processo_seletivo/processos/api/urls.py
- [X] T086 [US7] Rastrear US7 e FR-005–FR-006 e FR-034–FR-035 nos testes de aceitação em backend/tests/acceptance/test_us7_finalizacao.py

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: concluir rastreabilidade, operação, segurança e validação integral.

- [ ] T087 [P] Implementar consulta administrativa tipada e paginada de auditoria em backend/processo_seletivo/auditoria/api.py
- [ ] T088 [P] Criar teste de conformidade runtime da role sem UPDATE/DELETE em backend/tests/integration/test_database_permissions.py
- [ ] T089 [P] Criar teste de migrations do zero e upgrade da versão anterior em backend/tests/migrations/test_migrations.py
- [ ] T090 Validar comportamento contra OpenAPI 3.1 e impedir operações divergentes em backend/tests/contract/test_openapi_conformance.py
- [ ] T091 [P] Implementar logs estruturados, health/readiness e métricas de conflitos em backend/processo_seletivo/shared/observability.py
- [ ] T092 [P] Criar testes de carga para consultas públicas e consolidação de 20 Retificações em backend/tests/performance/test_public_queries.py
- [ ] T093 Criar matriz dos 38 FRs ativos e 29 cenários, registrando FR-037 e SC-002/009/010 como diferidos, em specs/001-processo-seletivo-editais/traceability.md
- [ ] T094 Executar e registrar toda a validação do quickstart em specs/001-processo-seletivo-editais/validation-report.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup** → **Foundational** → histórias.
- **US1** é o MVP e fornece Processo/Edital para as demais histórias.
- **US2** e **US3** dependem de US1 e podem avançar em paralelo.
- **US4** depende de US1, US2 e US3 para publicar um Edital completo.
- **US5** depende de US4 porque toda Retificação parte de Publicação existente.
- **US6** depende de US4 para o original e de US5 para cobrir consolidação histórica completa.
- **US7** depende de US1; seus cenários completos integram US4/US5, mas sua máquina de estados pode começar após a fundação.
- **Polish** depende das histórias incluídas no incremento.

### User Story Graph

```text
Setup → Foundational → US1 ─┬→ US2 ─┐
                            ├→ US3 ─┴→ US4 → US5 → US6
                            └────────────────────→ US7
```

### Within Each User Story

1. Escrever os testes marcados para a história e confirmar falha pelo motivo esperado.
2. Criar models e migrations antes dos serviços que os persistem.
3. Implementar domínio e aplicação antes da API.
4. Integrar autorização, auditoria, ETag, idempotência e Problem Details.
5. Executar o teste independente e a regressão das histórias anteriores.

### Parallel Opportunities

- T003–T004, T006–T007 e T009 podem avançar paralelamente após suas entradas existirem.
- T012, T014–T016 e T018 são fundações independentes; T021 pode ser preparado em paralelo.
- Testes `[P]` de cada história podem ser escritos juntos antes da implementação.
- US2 e US3 podem ser implementadas em paralelo após US1.
- US7 pode avançar em paralelo a US2/US3, preservando a integração final.

## Parallel Examples

### US1

```text
T023 domínio Processo/Edital | T024 contrato HTTP | T025 persistência | T026 autorização
```

### US4

```text
T050 workflow/validação | T051 contrato | T052 segregação | T053 transação/concorrência
T056 validador | T057 porta de PDF
```

### US5

```text
T061 consolidação pura | T062 contrato | T063 PostgreSQL | T064 autorização
T065 models | T067 alterações normativas
```

### US6 e US7

```text
T072 contrato público | T073 temporalidade | T074 não exposição
T079 domínio finalização | T080 contrato | T081 locks | T082 autorização
```

## Implementation Strategy

### MVP First

1. Concluir Setup e Foundational.
2. Implementar somente US1.
3. Executar T023–T032 e demonstrar criação atômica, segundo Edital e ativação.
4. Parar e validar antes de ampliar o escopo.

### Incremental Delivery

1. US1: estrutura institucional utilizável.
2. US2 + US3: rascunho normativo completo.
3. US4: primeira Publicação íntegra.
4. US5: Retificações e temporalidade.
5. US6: consulta pública histórica.
6. US7: encerramento e cancelamento preservados.
7. Polish: conformidade integral e evidências operacionais.

## Notes

- Tarefas `[P]` não alteram o mesmo arquivo nem dependem de tarefa incompleta no mesmo grupo.
- Nenhuma migration aplicada pode ser reescrita; correções usam nova migration.
- Testes de locks e concorrência usam PostgreSQL, transações e conexões independentes, nunca SQLite.
- Django Admin não pode contornar commands normativos; registros imutáveis permanecem somente leitura.
- Cada tarefa deve manter linguagem ubíqua e rastreabilidade com a especificação vigente.
