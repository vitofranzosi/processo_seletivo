---
description: "Tarefas de implementação da Integridade Normativa e Prontidão para Produção"
---

# Tasks: Integridade Normativa e Prontidão para Produção

**Input**: artefatos em `/specs/003-integridade-e-prontidao/`

**Prerequisites**: `spec.md`, `plan.md`

**Nota sobre a ordem.** As fases 1 a 3 foram implementadas antes desta lista existir, sob a
cláusula de correção emergencial justificada — um dos defeitos publicava alteração normativa que
ninguém homologou, sem erro nem aviso. As tarefas `[X]` dessas fases foram reconstruídas a partir
do que está nos commits `41e8173`, `e3a6992` e `854f216`, com o commit anotado em cada uma. As
fases 4 em diante são trabalho que resta e seguem a ordem normal.

## Formato: `[ID] [P?] [FR] Descrição`

- **[P]**: executável em paralelo sem conflito de arquivo
- **[FR]** ou **[SC]**: requisito ou critério de sucesso rastreado da `spec.md`
- **[rito]**: tarefa sobre os próprios artefatos do Spec Kit, sem requisito de produto associado

---

## Phase 1: Integridade da Retificação (P0)

- [X] T001 [FR-002] Derivar a precondição de conteúdo da base declarada em backend/processo_seletivo/publicacoes/domain/conflicts.py (`derive_preconditions`) — `41e8173`
- [X] T002 [FR-001] Verificar a precondição na Publicação contra o conteúdo vigente no início da vigência em backend/processo_seletivo/publicacoes/application/retificacoes.py — `41e8173`
- [X] T003 [FR-002a] Derivar a âncora de identidade de cada índice atravessado (`path_anchors`, `_identity`) em backend/processo_seletivo/publicacoes/domain/conflicts.py — `e3a6992`
- [X] T004 [FR-002a] Persistir a âncora em `AlteracaoNormativa.expected_anchors`, migration `0005_ancoras_de_alteracao` — `e3a6992`
- [X] T005 [FR-002b] Estender a verificação de identidade ao `ADD` com índice numérico, dispensando `/-` — `e3a6992`
- [X] T006 [FR-002c] Backfill determinístico das Retificações em curso, migration `0006_backfill_precondicoes` — `e3a6992`
- [X] T007 [FR-002c] Recusar na Publicação todo `REPLACE`/`REMOVE` sem hash do conteúdo anterior (`precondition_missing`) — `854f216`
- [X] T008 [FR-002d] Congelar a lógica da migration `0006` e recusar migration que importe domínio ou aplicação, em backend/tests/migrations/test_migrations.py — `854f216`
- [X] T009 [FR-003] Fazer o `expectedPreviousHash` declarado prevalecer sobre o derivado, mantendo a âncora não declarável — `e3a6992`
- [X] T010 [FR-004] Nomear na recusa o caminho ou o prefixo divergente e orientar a reelaboração — `41e8173`
- [X] T011 [FR-005] Exigir que a base declarada seja a vigente no início da vigência, com teste em backend/tests/integration/publicacoes/test_consulta_temporal.py — `41e8173`
- [X] T012 [FR-006] Revalidar o conteúdo consolidado com `validate_for_publication` em `_materialize_affected_versions` — `41e8173`
- [X] T013 [FR-007] Garantir que a recusa não materialize Publicação, documento ou versão, por rollback atômico — `41e8173`

---

## Phase 2: Sessão e ciclo de vida (P0)

- [X] T014 [FR-008] Pôr `CsrfViewMiddleware` na cadeia em backend/config/settings/base.py — `41e8173`
- [X] T015 [FR-009] Pôr `XFrameOptionsMiddleware` na cadeia — `41e8173`
- [X] T016 [FR-010] Confirmar que a API autenticada por cabeçalho não passa a exigir token de sessão, em backend/tests/interface/test_csrf.py — `41e8173`
- [X] T017 [FR-011] Chamar `ensure_processo_accepts_changes` em `add_edital` — `41e8173`
- [X] T018 [FR-012] Bloquear o Processo pai com `select_for_update` em `add_edital` — `41e8173`
- [X] T019 [FR-012] Cobrir as duas direções da corrida em backend/tests/integration/processos/test_finalizacao_concorrente.py — `e3a6992`

---

## Phase 3: Idempotência, auditoria e prontidão (P1)

- [X] T020 [FR-013] Honrar `Idempotency-Key` nas seis operações de Retificação em backend/processo_seletivo/publicacoes/api/views.py — `41e8173`
- [X] T021 [FR-013] Responder a repetição com o status do ato original, lido do registro, em toda a API — `e3a6992`
- [X] T022 [FR-014] Recusar a mesma chave com corpo diferente (`idempotency_conflict`) — já em `shared/idempotency.py`
- [X] T023 [FR-015] Gravar correlação e chave de idempotência na auditoria da Retificação — `41e8173`
- [X] T024 [FR-016] Criar backend/config/settings/production.py com falha de inicialização por variável — `41e8173`
- [X] T025 [FR-017] Recusar o módulo de autenticação de desenvolvimento, esquemas não institucionais e classes não importáveis — `e3a6992`
- [X] T026 [FR-018] Exercitar `check --deploy` pelo comando real em backend/tests/test_configuracao_producao.py — `e3a6992`
- [X] T027 [FR-017] Corrigir README e spec para descrever o alcance real da barreira — `e3a6992`

---

## Phase 4: Imutabilidade no banco (FR-023)

**Risco mais alto entre os abertos: a garantia dependia de disciplina da aplicação.**

- [X] T028 [FR-023] Levantar quais campos de `Retificacao` mudam legitimamente em cada estado — `AtoAdministrativo` e `RevisaoEdital` só são criados; `Retificacao` e `AlteracaoNormativa` mudam enquanto o ato está em curso
- [X] T029 [FR-023] Trigger condicional em `Retificacao` para `PUBLICADA`/`CANCELADA`, migration `0007_imutabilidade_do_historico`
- [X] T030 [FR-023] Trigger equivalente para `AlteracaoNormativa`, consultando o estado da Retificação pai
- [X] T031 [P] [FR-023] Trigger absoluta para `AtoAdministrativo`
- [X] T032 [P] [FR-023] Trigger absoluta para `RevisaoEdital`
- [X] T033 [FR-023] Cobrir `update()` e `delete()` diretos sobre registro final em backend/tests/integration/test_imutabilidade_do_historico.py
- [X] T034 [FR-023] Cobrir que o ciclo em curso não é bloqueado, e que alteração legítima **persiste** — a primeira versão da trigger devolvia `OLD` num `BEFORE UPDATE` e descartava a mudança em silêncio
- [X] T035 [FR-023] Confirmar que as quatro triggers novas sobrevivem a instalação limpa e a upgrade incremental

---

## Phase 5: Limites de borda e instantes (FR-020, FR-021)

- [X] T036 [FR-020] Limitar `targetPath` a 1000 e `expectedPreviousHash` a 64 no `ChangeSerializer`, espelhando as colunas
- [X] T037 [FR-020] Aceitar `X-Correlation-ID` só imprimível e até 100; substituir por um novo quando inutilizável, o que a resposta ecoa e o cliente enxerga
- [X] T038 [P] [FR-020] Cobrir que nenhum campo excedente produz 500, em backend/tests/contract/test_limites_de_borda.py
- [X] T039 [FR-021] Recusar instante sem fuso na consulta temporal em backend/processo_seletivo/publicacoes/api/public_views.py
- [X] T040 [P] [FR-021] Cobrir o instante ingênuo e o instante com fuso
- [X] T041 [FR-021] Documentar o deslocamento obrigatório no `openapi.yaml`

---

## Phase 6: Provisionamento de papéis (FR-019)

- [X] T042 [FR-019] Política em backend/processo_seletivo/seguranca/papeis.py e comando `provisionar_papeis`
- [X] T043 [FR-019] Idempotente e executável do zero, com `--dry-run` para revisar antes de aplicar
- [X] T044 [FR-019] Provisionar a role de conformidade **pela mesma política**, e cobrir que ela não recebe `UPDATE`/`DELETE` nas append-only e recebe onde o fluxo exige
- [X] T045 [P] [FR-019] Documentar a execução no README e no `.env.example`

---

## Phase 7: Lacunas funcionais herdadas da 002

- [X] T046 [FR-025] Criação de Processo com primeiro Edital em `views.criar_processo`, rota `processos/criar` e template `processo_criar.html`
- [X] T047 [FR-025] Cobrir criação, repetição com a mesma chave, campo ausente, identificação repetida e falta de permissão
- [X] T048 [FR-026] `validacao.js` espelha as regras do domínio pela Constraint Validation API, com `aria-invalid` acompanhando
- [X] T049 [FR-026] POST direto ao endpoint confirma que o domínio recusa as mesmas regras, com a mensagem exata
- [X] T050 [FR-027] `DESTINO_DA_PENDENCIA` roteia o `path` do achado para a etapa e a âncora que o resolvem
- [X] T051 [P] [FR-027] Cobrir o link na revisão e que cada etapa mostra só a pendência que resolve
- [X] T052 [FR-028] Decidido remover: conteúdo editorial é conteúdo normativo e exigiria fonte autoritativa, validação, vigência e presença no PDF — nada disso existe, e inventá-lo sob um campo já aceito seria decidir por omissão
- [X] T053 [FR-028] Campo removido do serializer e do contrato; campo desconhecido no rascunho passa a ser recusado em vez de ignorado

---

## Phase 8: Desempenho e higiene

- [X] T054 [FR-024] Cada fonte ordena e corta no banco em `limit + 1`; a mescla acontece sobre no máximo três vezes isso
- [X] T055 [P] [FR-024] Cobrir que nenhuma consulta do histórico varre sem limite, e que paginar de um em um reproduz a página única
- [X] T056 [FR-022] Rascunho expira em 24 h; sem carimbo de tempo utilizável é tratado como vencido
- [X] T057 [P] [FR-022] Cobrir o prazo e o descarte do que não se sabe a idade
- [X] T058 [FR-029] Fechar a conexão subjacente nas threads de teste e falhar em `ResourceWarning` — o filtro precisa incluir `PytestUnraisableExceptionWarning`, que é como o warning do coletor de lixo chega

---

## Dependências

- A Fase 4 depende da T028: sem saber o que muda legitimamente em cada estado, a trigger vira
  bloqueio de fluxo em vez de garantia.
- T044 depende da Fase 6: verificar `GRANT` exige que os papéis existam.
- A Fase 7 não depende de nenhuma anterior e pode correr em paralelo com a 4, 5 e 6.
- T053 depende da decisão em T052.

---

## Phase 9: Correções apontadas na revisão de fechamento

**A revisão reabriu a feature.** Oito achados, dois deles P0 sobre requisito marcado como
concluído. Cada um está reproduzido antes de corrigido.

- [X] T059 [FR-019] Provisionar em banco vazio sem falhar: todo comando que toca tabela passa a ser condicional à existência dela. Reproduzido: `relation "auditoria_registroauditoria" does not exist`
- [X] T060 [FR-019] Dar senha ao papel de migração e transferir a propriedade das tabelas e do schema — `GRANT ALL` deixa usar, mas `ALTER TABLE` exige ser dono, e a migration seguinte falharia no meio do deploy
- [X] T061 [FR-019] Conferir, ao fim do provisionamento, que nenhuma append-only existente deu escrita ao runtime, e informar quantas foram protegidas para que a segunda passada esquecida apareça na hora
- [X] T062 [FR-019] Ocultar as senhas em `--dry-run`. Reproduzido: `ALTER ROLE ... PASSWORD 'probe-secret'` impresso em texto puro
- [X] T063 [FR-020] Validar na tela de criação os limites que a coluna impõe, derivados de `_meta` e não copiados à mão. Reproduzido: `institutionalCode` com 101 caracteres retornava 500 `StringDataRightTruncation`
- [X] T064 [FR-030] Executar os scripts da interface em `node --test` contra um DOM mínimo, em vez de procurar string no fonte — 19 testes cobrindo as regras de `validacao.js` e a expiração de `rascunho.js`
- [X] T065 [FR-030] Declarar no `quickstart.md` o que os testes de JavaScript não cobrem — foco, leitor de tela, balão do navegador — e como conferir à mão
- [X] T066 [FR-027] Deixar de oferecer caminho para pendência que a etapa de destino não corrige; `title` e `description` só existem na criação e a Identificação é somente leitura
- [X] T067 [SC-006] Elevar a cobertura acima de 89% nas duas execuções, medida com três casas. Cobrir `seed_demo`, que estava a 0% e é caminho documentado no README
- [X] T068 [SC-007] Corrigir o `seed_demo`, quebrado pelo commit `41e8173` e nunca executado por teste algum, e remover a flag `--recriar`, que era declarada, documentada no `--help` e jamais lida — e que não poderia funcionar, porque apagar a demonstração exigiria excluir Publicações
- [X] T069 [FR-019] Devolver a propriedade dos objetos antes de derrubar os papéis de conformidade, para que o teste não leve o banco junto
- [X] T070 [rito] Produzir `research.md`, `data-model.md` e `quickstart.md`, e restaurar o bloco `Documentation` do plano — que eu havia reescrito para listar só o que produzi, apagando o lugar onde a falta apareceria
- [X] T071 [rito] Atualizar a checklist e o README, que ainda diziam "27 concluídas, 31 abertas" e "não há interface gráfica"

---

## Situação

71 de 71 tarefas concluídas.

As treze últimas nasceram da revisão de fechamento, que recusou a declaração de conclusão anterior
e estava certa: dois requisitos marcados como concluídos não funcionavam em banco novo. A lição
está registrada na análise de consistência.

Fora desta feature e ainda bloqueadores de implantação: a integração com o diretório institucional
e a `004-enderecamento-normativo-estavel`, que continua sendo apenas especificação preliminar com
cinco clarificações abertas.
