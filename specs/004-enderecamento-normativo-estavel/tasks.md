---
description: "Tarefas de implementação do Endereçamento Normativo por Chave Estável"
---

# Tasks: Endereçamento Normativo por Chave Estável

**Input**: Design documents from `/specs/004-enderecamento-normativo-estavel/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/enderecamento.md`, `quickstart.md`

**Escopo reduzido em 2026-08-29**: o sistema não está em produção e não há dado a preservar. Saíram
todas as tarefas de conversão de caminhos, compatibilidade entre formatos, auditoria de conversão,
devolução de Retificações, relatório por origem e migração baseada em `expected_anchors`. Saíram
também as de `before=`/`after=` e as de identificador genérico. De 57 para 36.

**Tests**: incluídos, e não por opção. O princípio V da Constituição exige teste automatizado para
regra crítica, nomeando publicação e retificação — que é o que esta feature altera.

**Organization**: agrupadas por história, para que cada uma seja implementável e verificável em
separado.

## Format: `[ID] [P?] [Story] Descrição`

- **[P]**: executável em paralelo — arquivo distinto, sem dependência pendente
- **[Story]**: história rastreada (`US1`, `US2`); Setup, Foundational, Limpeza e Polish não têm

## Path Conventions

Monólito modular existente. Código em `backend/processo_seletivo/`, testes em `backend/tests/`.

---

## Phase 1: Setup

- [ ] T001 [P] Criar construtor de snapshot de teste com coleções aninhadas — `profiles` com `competitionModalities` e `requirements`, e `schedule` — em backend/tests/fixtures/snapshot.py, reutilizado pelas duas histórias

---

## Phase 2: Foundational

**⚠️ Nenhuma história funciona sem esta fase.** É a gramática e a resolução; tudo o mais consome.

- [ ] T002 Declarar as coleções com chave e a única sem chave em backend/processo_seletivo/publicacoes/domain/colecoes.py, com o caminho de cada uma e o campo que serve de identificador (FR-011, FR-012)
- [ ] T003 [P] Cobrir a declaração contra um snapshot real em backend/tests/unit/publicacoes/test_colecoes.py — coleção nova sem identificador precisa fazer a suíte falhar, não passar em silêncio (FR-012, SC-006)
- [ ] T004 Estender `parse_path` para reconhecer o seletor `id=` em backend/processo_seletivo/publicacoes/domain/changes.py (FR-001)
- [ ] T005 Resolver o seletor em `_descend` e `resolve_path` **apenas quando o contêiner for lista** em backend/processo_seletivo/publicacoes/domain/changes.py — em objeto, `id=algo` continua nome de chave literal (FR-002)
- [ ] T006 Aplicar `REPLACE` e `REMOVE` por `id=`, e `ADD` por `-`, em `apply_change` em backend/processo_seletivo/publicacoes/domain/changes.py (FR-001, FR-006)
- [ ] T007 Exigir que o valor do seletor seja UUID, comparado como texto exato e sem normalização de caixa, em backend/processo_seletivo/publicacoes/domain/changes.py (FR-003)
- [ ] T008 [P] Cobrir a gramática em backend/tests/unit/publicacoes/test_changes_gramatica.py — as quatro formas de segmento, a regra do contêiner e a exigência de UUID (FR-001, FR-002, FR-003, FR-006)
- [ ] T009 [P] Cobrir o endereçamento aninhado `/profiles/id=…/competitionModalities/id=…/name` e o objeto `normativeRule`, que tem `id` e não é item de lista, em backend/tests/unit/publicacoes/test_changes_gramatica.py (FR-004, FR-005)

---

## Phase 3: US1 — Retificar sem ser atropelado por trabalho alheio (P1)

**Objetivo**: duas pessoas alterando Perfis diferentes do mesmo Edital publicam ambas, sem que
nenhuma precise refazer o ato.

**Teste independente**: elaborar duas Retificações sobre Perfis distintos da mesma versão, publicar
em sequência, e verificar que as duas são aceitas e cada uma atinge o seu Perfil.

- [ ] T010 [US1] Recusar na elaboração caminho com índice sobre coleção com chave, com `positional_addressing_refused`, em backend/processo_seletivo/publicacoes/application/retificacoes.py (FR-007, FR-010)
- [ ] T011 [US1] Recusar com `target_key_not_found` quando a entidade endereçada não existir, nos dois momentos — elaboração contra a base declarada, Publicação contra o vigente no início da vigência — em backend/processo_seletivo/publicacoes/application/retificacoes.py (FR-008, FR-010)
- [ ] T012 [US1] Recusar coleção que ficaria com chave repetida, com `duplicate_key_in_collection`, na elaboração e na Publicação, em backend/processo_seletivo/publicacoes/domain/conflicts.py (FR-009, FR-010)
- [ ] T013 [US1] Tratar `requirements` como valor atômico: aceitar apenas `REPLACE` da lista inteira e recusar endereçamento item a item, em backend/processo_seletivo/publicacoes/domain/changes.py (FR-011)
- [ ] T014 [US1] Recusar endereçamento de listas de controle interno, como `applied_publications`, em backend/processo_seletivo/publicacoes/domain/colecoes.py (FR-013)
- [ ] T015 [US1] Limitar a forma de `targetPath` no `ChangeSerializer` em backend/processo_seletivo/publicacoes/api/serializers.py, para que forma inválida vire recusa de borda e não erro de domínio (FR-003)
- [ ] T016 [P] [US1] Cobrir o cenário central em backend/tests/integration/publicacoes/test_enderecamento.py — duas Retificações sobre Perfis distintos da mesma versão publicam ambas (SC-001)
- [ ] T017 [P] [US1] Cobrir que duas Retificações sobre o mesmo campo do mesmo Perfil continuam sendo recusadas por `expected_hash_mismatch` em backend/tests/integration/publicacoes/test_enderecamento.py — a precondição por hash não sai junto com a âncora (FR-014)
- [ ] T018 [P] [US1] Cobrir a recusa na elaboração e a recusa na Publicação como momentos distintos, com o código de cada uma, em backend/tests/integration/publicacoes/test_enderecamento.py (SC-002, SC-003)
- [ ] T019 [P] [US1] Cobrir `requirements` substituída inteira, inclusive por lista vazia, e recusada item a item, em backend/tests/integration/publicacoes/test_enderecamento.py (FR-011)
- [ ] T020 [P] [US1] Cobrir chave repetida, `ADD` de entidade cuja chave já existe, e identificador presente em duas coleções distintas — que é irrelevante — em backend/tests/integration/publicacoes/test_enderecamento.py (FR-009)

---

## Phase 4: US2 — Compor a Retificação sem conhecer a representação (P2)

**Objetivo**: quem elabora continua editando o conteúdo vigente na tela, sem saber que existe
caminho, chave ou índice.

**Teste independente**: alterar campos de um Perfil pela tela e verificar que as Alterações emitidas
usam a chave, sem que nada tenha mudado para quem usa.

- [ ] T021 [US2] Emitir `/profiles/id=<uuid>/…` e `/schedule/id=<uuid>/…` em `campos_editaveis` e `diferencas` em backend/processo_seletivo/interface/retificacao.py (FR-019)
- [ ] T022 [US2] Emitir remoção por `id=` e acréscimo por `-` em backend/processo_seletivo/interface/retificacao.py (FR-006)
- [ ] T023 [US2] Remover a coreografia de ordem — `REPLACE` primeiro, `REMOVE` decrescente, `ADD` por último — que existia só porque índice deslocava, em backend/processo_seletivo/interface/retificacao.py (FR-019)
- [ ] T024 [US2] Garantir que nenhum caminho normativo aparece no HTML entregue pela tela de Retificação em backend/processo_seletivo/interface/templates/interface/retificar.html (FR-019)
- [ ] T025 [P] [US2] Cobrir as duas condições de FR-019 sobre a página renderizada — sem caminho no HTML, alterações por chave — em backend/tests/interface/test_retificar.py (SC-004)
- [ ] T026 [P] [US2] Cobrir que acrescentar e remover na mesma edição, em qualquer ordem, produz o mesmo ato, em backend/tests/unit/interface/test_retificacao_estrutural.py (FR-019)
- [ ] T027 [P] [US2] Atualizar os testes que dependiam da ordem de emissão em backend/tests/unit/interface/test_retificacao_estrutural.py, verificando que a garantia agora vem da chave e não da sequência (FR-019)

---

## Phase 5: Remoção da âncora da `003`

**Depende da Fase 3**: a âncora só sai depois de o endereçamento por chave estar valendo.

- [ ] T028 Remover a derivação de âncora e a verificação `ANCHOR_MISMATCH` de backend/processo_seletivo/publicacoes/domain/conflicts.py, preservando a precondição por hash intacta (FR-015, FR-014)
- [ ] T029 Remover o campo `expected_anchors` de backend/processo_seletivo/publicacoes/models_retificacao.py (FR-015)
- [ ] T030 Criar backend/processo_seletivo/publicacoes/migrations/0008_remover_ancoras.py com `RemoveField` e função inversa, sem conversão de dados (FR-016)
- [ ] T031 [P] Atualizar os testes da `003` que afirmavam `target_identity_mismatch` em backend/tests/integration/publicacoes/test_retificacoes.py, substituindo pela recusa que passa a valer (FR-015)
- [ ] T032 [P] Cobrir que nenhum código fora de migrations referencia `expected_anchors` ou `target_identity_mismatch`, em backend/tests/unit/publicacoes/test_ancora_removida.py (SC-007)

---

## Phase 6: Polish e questões transversais

- [ ] T033 Aplicar o delta do contrato em specs/001-processo-seletivo-editais/contracts/openapi.yaml — descrição de `targetPath`, forma de `ADD`, os três códigos novos e a remoção de `target_identity_mismatch` (FR-017)
- [ ] T034 [P] Cobrir que o contrato descreve a extensão, os três códigos e a forma de `ADD`, em backend/tests/contract/test_enderecamento_api.py (SC-005)
- [ ] T035 [P] Cobrir que um caminho publicado identifica a entidade alterada sem consultar a versão vigente, em backend/tests/contract/test_enderecamento_api.py (FR-018)
- [ ] T036 Executar o roteiro de specs/004-enderecamento-normativo-estavel/quickstart.md de ponta a ponta e conferir a cobertura com branches nas duas execuções, conforme a configuração de backend/pyproject.toml

---

## Dependências

- **Fase 2 bloqueia tudo**: sem gramática e resolução, nenhuma história anda.
- **T002 precede T003**: a declaração existe antes do teste que a guarda.
- **T004 → T005 → T006/T007**: reconhecer o seletor, resolver, aplicar.
- **US1 e US2 são independentes entre si** e podem correr em paralelo depois da Fase 2.
- **Fase 5 depende da Fase 3**: remover a âncora antes de o endereçamento por chave valer deixaria
  um intervalo sem proteção alguma contra deslocamento.
- **T033 depende de US1**, porque documenta os códigos que ela introduz.

## Execução em paralelo

Depois da Fase 2, duas frentes correm juntas:

```
US1  T010–T015 (sequenciais, mesmo arquivo)  →  T016–T020 [P]
US2  T021–T024                                →  T025–T027 [P]
```

A Fase 5 entra quando US1 fechar. Dentro dela, T031 e T032 são paralelos.

## Estratégia de entrega

**MVP: Fase 2 + US1.** É o que entrega o ganho que a `003` não podia dar — duas pessoas em Perfis
diferentes publicam ambas — e o que fecha a causa do defeito.

**US2 acompanha o mesmo release.** Sem ela a interface continuaria emitindo forma posicional, que
US1 recusaria na elaboração: a tela quebraria. A prioridade P2 reflete o risco, não a sequência.

**A Fase 5 pode ficar para depois** sem prejuízo de correção — a âncora sobrando é redundância, não
defeito. Mas deixá-la é manter mecanismo sem função, que é como alguém volta a preenchê-lo achando
que protege algo.

## Situação

36 tarefas, nenhuma iniciada. A implementação não começou.
