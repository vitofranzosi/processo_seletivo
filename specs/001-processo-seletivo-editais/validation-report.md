# Relatório de Validação do Quickstart: Processo Seletivo e Editais

**Feature**: `001-processo-seletivo-editais` | **Tarefa**: T094 | **Data**: 2026-08-28

**Fonte**: [quickstart.md](./quickstart.md) — 15 cenários e 6 asserções transversais.

**Ambiente de execução**: macOS 15 (arm64), Python 3.13, Django 5.2.17, PostgreSQL 16.14 local em
`localhost:5432`, banco `processo_seletivo_test`. O quickstart pede PostgreSQL 18; a execução usou
16.14, o que está registrado como [D1](#desvios-de-ambiente). A CI em
[.github/workflows/backend.yml](../../.github/workflows/backend.yml) executa a mesma suíte contra
`postgres:18`.

**Resultado**: os 15 cenários e as 6 asserções transversais foram executados. **13 cenários passam
integralmente**, **2 passam com ressalva** por dependerem do documento publicado, que ainda não
reproduz o conteúdo normativo completo. Nenhum cenário falha.

A execução encontrou e corrigiu dois defeitos: rascunho reusando identificador de outro Edital
devolvia HTTP 500, e os status de erro divergiam do contrato. Ver
[Defeitos encontrados](#defeitos-encontrados-durante-a-execução).

## Comandos executados

O quickstart trazia comandos em PowerShell com `venv` e `pip install -e`, incompatíveis com o `uv`
adotado em T001/T002. A execução usou os equivalentes do [Makefile](../../backend/Makefile) e o
quickstart foi corrigido para refletir os comandos reais — ver [D2](#desvios-de-ambiente).

| Comando | Resultado |
|---|---|
| `uv sync --extra dev --locked` | `Resolved 24 packages` / `Checked 22 packages` |
| `uv run ruff check .` | `All checks passed!` |
| `uv run python manage.py check` | `System check identified no issues (0 silenced).` |
| `uv run python manage.py makemigrations --check --dry-run` | `No changes detected` |
| `uv run pytest` (PostgreSQL) | **202 passed** |
| `uv run pytest -m acceptance` | 24 passed, 178 deselected |
| `uv run pytest -m contract` | 42 passed, 160 deselected |
| `uv run pytest -m integration` | 46 passed, 156 deselected |
| `uv run pytest -m authorization` | 31 passed, 171 deselected |
| `uv run pytest` (SQLite) | 182 passed, 20 skipped |

Os 20 testes ignorados em SQLite são os que exigem locks reais, triggers e privilégios de role —
exatamente os que o quickstart determina que não sejam substituídos por SQLite. Eles executam na
suíte PostgreSQL.

## Cenários

| # | Cenário | Evidência executada | Resultado |
|---|---|---|---|
| 1 | Criar Processo e primeiro Edital atomicamente | `tests/integration/processos/test_creation.py::test_process_and_first_edital_are_atomic`, `tests/acceptance/test_quickstart.py::test_quickstart_s1_invalid_payload_leaves_no_partial_process` | Passa |
| 2 | Segundo Edital independente | `tests/acceptance/test_quickstart.py::test_quickstart_s2_editing_the_second_edital_does_not_touch_the_first`, `tests/integration/editais/test_cronograma.py::test_each_edital_has_an_independent_schedule` | Passa |
| 3 | Elaborar Perfis, vagas e Cronograma | `tests/acceptance/test_quickstart.py::test_quickstart_s3_draft_cannot_reuse_identifiers_from_another_edital`, `tests/integration/editais/test_perfis.py::test_database_rejects_incompatible_reserve_limit`, `tests/integration/editais/test_cronograma.py::test_database_rejects_event_with_end_before_start` | Passa após correção |
| 4 | Submeter e homologar | `tests/acceptance/test_quickstart.py::test_quickstart_s4_revoked_homologation_returns_the_edital_to_review`, `tests/authorization/test_publicacao.py::test_one_actor_cannot_prepare_homologate_and_publish` | Passa com ressalva — ver R1 |
| 5 | Publicar Edital original | `tests/acceptance/test_us4_publicacao.py::test_us4_complete_publication_flow`, `tests/integration/publicacoes/test_publicar_edital.py::test_database_trigger_rejects_publication_update` | **Ressalva** — ver R2 |
| 6 | Retificação imediata | `tests/acceptance/test_quickstart.py::test_quickstart_s6_immediate_retification_takes_effect_on_publication` | Passa |
| 7 | Retificação futura | `tests/acceptance/test_quickstart.py::test_quickstart_s7_retroactive_effective_date_is_rejected`, `tests/integration/publicacoes/test_consulta_temporal.py::test_future_retification_only_takes_effect_from_its_declared_instant` | Passa |
| 8 | Publicações fora da ordem de vigência | `tests/integration/publicacoes/test_consulta_temporal.py::test_out_of_order_publications_compose_by_validity_not_by_publication_order` | Passa |
| 9 | Mesma vigência sem conflito | `tests/acceptance/test_quickstart.py::test_quickstart_s9_same_effective_time_without_conflict_accumulates` | Passa |
| 10 | Mesma vigência com conflito | `tests/acceptance/test_quickstart.py::test_quickstart_s10_same_effective_time_with_conflict_is_decided_by_publication_order` | Passa |
| 11 | Reconstrução histórica | `tests/acceptance/test_quickstart.py::test_quickstart_s11_recomputed_temporal_function_matches_the_materialized_snapshot`, `tests/integration/publicacoes/test_consulta_temporal.py::test_twenty_retifications_recompose_every_requested_version` | **Ressalva** — ver R2 |
| 12 | Encerramento regular do Edital | `tests/acceptance/test_us7_finalizacao.py::test_us7_closing_an_edital_is_not_treated_as_cancellation` | Passa |
| 13 | Cancelamento inválido do Processo | `tests/acceptance/test_us7_finalizacao.py::test_us7_cancelling_a_process_is_blocked_until_every_edital_is_final` | Passa |
| 14 | Segregação de funções e autorização | `tests/authorization/test_publicacao.py::test_one_actor_cannot_prepare_homologate_and_publish`, `tests/authorization/test_processos.py::test_cross_scope_process_is_not_revealed` | Passa |
| 15 | Concorrência e repetições | `tests/integration/test_foundation.py::test_compare_and_swap_rejects_stale_revision`, `tests/integration/publicacoes/test_publicar_edital.py::test_concurrent_publications_create_exactly_one`, `tests/authorization/test_foundation.py::test_idempotency_replays_and_rejects_changed_payload`, `tests/integration/processos/test_finalizacao_concorrente.py::test_process_cancellation_waits_for_a_concurrent_edital_transition` | Passa |

### Detalhamento dos cenários temporais

O cenário 8 do quickstart usa datas absolutas (01/09, 05/09, 08/09, 10/09). A execução usa deslocamentos
relativos ao instante do teste, porque `Date.now` fixo tornaria a suíte dependente do calendário. A
propriedade verificada é a mesma: com A publicada antes de B mas vigente depois, a consulta na vigência
de B devolve só B, e na vigência de A devolve a composição A+B.

O cenário 9 exige provar que a ordem física dos dados não afeta o resultado. O teste consolida a mesma
lista de atos em ordem direta e invertida e compara os hashes canônicos — iguais — e confronta o
resultado com o `contentHash` devolvido pela API.

O cenário 11 recomputa a função temporal a partir do snapshot original e dos atos publicados, e compara
o hash com o da `VersaoConsolidada` materializada. Confere.

## Asserções transversais

| Asserção | Evidência executada | Resultado |
|---|---|---|
| Auditoria na mesma transação, com correlation ID | `tests/authorization/test_finalizacao.py::test_final_act_audits_actor_reason_and_state_transition`, `tests/integration/publicacoes/test_publicar_edital.py::test_pdf_failure_rolls_back_entire_publication` | Passa |
| Publicação, snapshot, documento e auditoria recusam update/delete | `tests/integration/test_database_permissions.py::test_trigger_rejects_mutation_even_for_a_privileged_role`, `tests/integration/test_database_permissions.py::test_runtime_role_has_no_update_or_delete_privilege` | Passa |
| Erros em `application/problem+json`, sem stack trace | `tests/contract/test_openapi_conformance.py::test_problem_responses_conform_to_the_contract` | Passa |
| Consultas públicas nunca retornam draft, revisão ou auditoria | `tests/authorization/test_consulta_publica.py::test_public_projection_never_exposes_elaboration_identifiers`, `tests/authorization/test_consulta_publica.py::test_public_projection_never_exposes_audit_trail` | Passa |
| Migrations aplicáveis do zero, sem reescrever aplicada | `tests/migrations/test_migrations.py::test_migrations_apply_from_scratch_and_recreate_the_triggers`, `tests/migrations/test_migrations.py::test_upgrade_from_the_previous_version_applies_only_the_new_migrations` | Passa |
| Rastreabilidade dos 38 FRs e 29 cenários; diferidos registrados | `tests/contract/test_traceability.py::test_every_referenced_test_exists`, `tests/contract/test_traceability.py::test_matrix_marks_the_deferred_items_as_deferred`, [traceability.md](./traceability.md) | Passa |

## Medições

SC-005 exige recuperar a versão vigente e qualquer versão histórica em até 10 segundos por consulta,
para uma sequência de até 20 Retificações. Medição em ambiente local, 20 Retificações publicadas e 21
fronteiras de vigência consultadas:

| Métrica | Valor | Limite |
|---|---|---|
| Consultas de versão por instante | 21 | — |
| Tempo máximo por consulta | 1,0 ms | 10 s |
| p95 por consulta | 0,7 ms | 10 s |
| Média por consulta | 0,6 ms | 10 s |
| Histórico paginado, 100 itens | 9,7 ms | — |

A margem é de quatro ordens de grandeza, mas o número não representa produção: banco local, sem
concorrência, sem latência de rede e com volume mínimo.

T092 acrescentou duas camadas. A suíte `tests/performance/` mede **custo por consulta**, não tempo:
verifica que o número de consultas ao banco não cresce com o histórico, que é a degradação que
importa e a única mensurável de forma determinística em CI. Ela encontrou e corrigiu um N+1 — a
proveniência de cada versão consolidada virava uma consulta própria, levando o histórico de 8 para
25 consultas entre 3 e 20 Retificações; hoje são 5, constantes.

O SLO de p95 ≤ 2 s e pico de 500 consultas por segundo do [plan.md](./plan.md) exige serviço
implantado, e continua **não verificado**. O harness `backend/scripts/carga_publica.py` mede-o
quando houver ambiente. Execução local contra `runserver`, 8 workers, 3 segundos, dataset mínimo:

| Cenário | Throughput | p50 | p95 | p99 |
|---|---|---|---|---|
| `versao-vigente` | 748 req/s | 10,4 ms | 14,0 ms | 17,0 ms |
| `historico` | 546 req/s | 14,3 ms | 18,8 ms | 23,8 ms |

Esses números **não** validam o SLO: `runserver` não é servidor de produção, o dataset é mínimo e
não há latência de rede. Servem para mostrar que o harness funciona e que não há gargalo evidente
na ordem de grandeza errada.

## Defeitos encontrados durante a execução

### Corrigido — rascunho com identificador de outro Edital devolvia HTTP 500

O cenário 3 exige "confirmar rejeição de ... Evento de outro Edital". Não havia cobertura
comportamental. Ao executar, um `PUT /admin/editais/{id}/rascunho` reusando o `id` de um Perfil ou
Evento já vinculado a outro Edital produzia `IntegrityError` não tratado e HTTP 500, em vez de
rejeição de domínio. FR-017 exige rejeitar inconsistências determináveis, e a Constituição exige
falhas diagnosticáveis sem exposição indevida.

`replace_draft` passou a verificar os identificadores antes de apagar o rascunho vigente e responde
`409 identifier_belongs_to_another_edital` nomeando os identificadores em conflito. Coberto por
`tests/acceptance/test_quickstart.py::test_quickstart_s3_draft_cannot_reuse_identifiers_from_another_edital`.

### Corrigido — status de erro divergentes do contrato

A avaliação do repositório encontrou duas divergências de status. Corpo semanticamente inválido
devolvia `400` (padrão do DRF), mas o contrato declara `422` para essas operações e o cenário 1 do
quickstart pede `422`; o handler passou a mapear `ValidationError` para `422 invalid_payload`, com as
violações achatadas preservando o caminho do campo. Na direção oposta, `400` por metadado malformado
— `Idempotency-Key` fora do tamanho, `If-Match` inválido, `em` ou `limit` inaceitáveis — era
devolvido sem estar declarado; o contrato passou a declarar `400` nas 21 operações que validam header
ou query string, com o componente `BadRequest`.

`tests/contract/test_openapi_conformance.py::test_error_statuses_returned_are_declared_in_the_contract`
e `tests/contract/test_openapi_conformance.py::test_query_parameter_errors_are_declared_and_conform`
travam essa classe de divergência.

### Aberto — Retificação sem efeito prático devolve HTTP 500

Publicar uma Retificação cujo conteúdo consolidado é idêntico ao já publicado gera bytes de PDF
idênticos e viola a constraint única `document_hash`, resultando em 500. Fora do escopo do
quickstart, registrado aqui por afetar a mesma asserção transversal de falhas diagnosticáveis.
Também consta em [traceability.md](./traceability.md).

## Ressalvas

### R1 — Publicação de homologação divergente não foi exercitada por caminho próprio

O cenário 4 pede "alterar o draft depois da revisão e confirmar que a Publicação da homologação
antiga é rejeitada". A defesa existe: `publish_edital` recomputa o snapshot e compara com
`revisao.content_hash`, respondendo `409 homologated_revision_changed`.

Esse caminho **não pôde ser exercitado pela API**, porque `replace_draft` só aceita Edital em
`EM_ELABORACAO`: uma vez submetido, o rascunho fica inacessível pela rota administrativa. A
divergência só ocorreria por escrita fora dos commands, que a Constituição já proíbe. A verificação
executada foi a revogação de homologação e a recusa de publicar sem homologação vigente.

**Recomendação**: reescrever o passo do quickstart para descrever o que é observável, ou cobrir a
guarda por teste de unidade que monte a divergência diretamente na persistência.

### R2 — Documento publicado não reproduz o conteúdo normativo

Os cenários 5 e 11 pedem confirmar que "snapshot = revisão homologada e PDF = bytes preservados" e
que "original, atos, consolidados e PDFs permanecem públicos e imutáveis".

O que foi verificado e confere: o snapshot publicado é idêntico à revisão homologada; o PDF é
determinístico, deriva do snapshot, carrega seu SHA-256, é servido byte a byte pelo endpoint público
e é imutável no banco.

O que **não** confere: o PDF contém apenas título, número/ano e o hash. Perfis, vagas, modalidades e
Cronograma não são renderizados. FR-023 exige correspondência integral com os dados estruturados e o
conteúdo editorial homologado.

Esta é a mesma lacuna L2 de [traceability.md](./traceability.md). Enquanto existir, **um Edital
publicado não pode ser divulgado apenas pelo PDF**.

## Desvios de ambiente

### D1 — PostgreSQL 16 na execução local

O quickstart e o [plan.md](./plan.md) especificam PostgreSQL 18. A execução local usou 16.14, versão
disponível na estação. Nenhum recurso exclusivo de 17 ou 18 é utilizado: as construções empregadas
são `CREATE TRIGGER`, `SELECT ... FOR UPDATE`, `gen_random_uuid()` e `GRANT/REVOKE`, todas presentes
em 16. A CI executa a mesma suíte contra `postgres:18` e é a referência de conformidade.

### D2 — Comandos adaptados de PowerShell/pip para uv — resolvido

O quickstart foi escrito antes da escolha de ferramentas. T001 e T002 adotaram `uv` e um Makefile, e
a seção "Planned verification commands" ficou descrevendo um fluxo que não executa. Ela foi
substituída pelos comandos efetivamente usados, incluindo a variável `TEST_DB_ENGINE` que separa a
execução em SQLite da execução completa em PostgreSQL.

## Conclusão

A validação do quickstart executa por completo e sem falhas. Pelo critério de conclusão da
[Constituição](../../.specify/memory/constitution.md) — requisitos e invariantes atendidos,
autorização validada, migrations aplicáveis, testes aprovados, contratos atualizados, auditoria
implementada, sem regressões conhecidas e artefatos consistentes — **a feature ainda não pode ser
declarada concluída**, por dois motivos:

1. **FR-023 não está atendido** (R2 / L2): o documento publicado não corresponde integralmente ao
   conteúdo homologado. É o único item que impede a conclusão por mérito, e exige um incremento
   próprio para o renderizador de PDF.
2. **O SLO de carga não foi verificado**: T091 e T092 estão concluídas, mas o p95 ≤ 2 s sob pico de
   500 consultas por segundo depende de ambiente implantado. O harness existe em
   `backend/scripts/carga_publica.py` e a medição precisa ser feita em homologação.

Fora esses pontos, US1 a US7 estão implementadas, cobertas e rastreadas, com 202 testes aprovados em
PostgreSQL e conformidade verificada contra o contrato OpenAPI 3.1.
