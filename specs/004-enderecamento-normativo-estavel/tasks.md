---
description: "Tarefas de implementação do Endereçamento Normativo por Chave Estável"
---

# Tasks: Endereçamento Normativo por Chave Estável

**Input**: Design documents from `/specs/004-enderecamento-normativo-estavel/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/enderecamento.md`, `quickstart.md`

**Tests**: incluídos, e não por opção. O princípio V da Constituição exige teste automatizado para
regra crítica, nomeando publicação, retificação, temporalidade e concorrência — que é exatamente o
que esta feature altera. Correção relevante DEVE incluir teste de regressão.

**Organization**: agrupadas por história, para que cada uma seja implementável e verificável em
separado.

## Format: `[ID] [P?] [Story] Descrição`

- **[P]**: executável em paralelo — arquivo distinto, sem dependência pendente
- **[Story]**: história rastreada (`US1` a `US4`); Setup, Foundational e Polish não têm

## Path Conventions

Monólito modular existente. Código em `backend/processo_seletivo/`, testes em `backend/tests/`.

---

## Phase 1: Setup

- [ ] T001 [P] Criar construtor de snapshot de teste com coleções aninhadas — `profiles` com `competitionModalities` e `requirements`, e `schedule` — em backend/tests/fixtures/snapshot.py, reutilizado pelas quatro histórias
- [ ] T002 [P] Acrescentar ao construtor um Edital com Retificações nos três estados não finais, para os testes da migração, em backend/tests/fixtures/snapshot.py

---

## Phase 2: Foundational

**⚠️ Nenhuma história funciona sem esta fase.** É a gramática e a resolução; tudo o mais consome.

- [ ] T003 Declarar as coleções com chave e a única sem chave em backend/processo_seletivo/publicacoes/domain/colecoes.py, com o caminho de cada uma e o campo que serve de identificador
- [ ] T004 [P] Cobrir a declaração contra um snapshot real em backend/tests/unit/publicacoes/test_colecoes.py — coleção nova sem identificador precisa fazer a suíte falhar, não passar em silêncio (FR-004c)
- [ ] T005 Estender `parse_path` para reconhecer os seletores `id=`, `before=` e `after=` em backend/processo_seletivo/publicacoes/domain/changes.py, sem interpretá-los ainda
- [ ] T006 Resolver o seletor em `_descend` e `resolve_path` **apenas quando o contêiner for lista** em backend/processo_seletivo/publicacoes/domain/changes.py — em objeto, `id=algo` continua nome de chave literal (FR-001a)
- [ ] T007 Aplicar `REPLACE` e `REMOVE` por `id=` em `apply_change` em backend/processo_seletivo/publicacoes/domain/changes.py (FR-001)
- [ ] T008 Aplicar `ADD` por `before=` e `after=` em `apply_change`, preservando `-` para acréscimo ao fim e recusando índice numérico em backend/processo_seletivo/publicacoes/domain/changes.py (FR-001e)
- [ ] T009 Comparar o valor do seletor como texto exato, sem normalização de caixa, e honrar o escape `~0`/`~1` do RFC 6901 em backend/processo_seletivo/publicacoes/domain/changes.py (FR-001h)
- [ ] T010 [P] Cobrir a gramática em backend/tests/unit/publicacoes/test_changes_gramatica.py — as cinco formas de segmento, a regra do contêiner, o escape e a comparação exata
- [ ] T011 [P] Cobrir o endereçamento aninhado `/profiles/id=…/competitionModalities/id=…/name` e o objeto `normativeRule`, que tem `id` e não é item de lista, em backend/tests/unit/publicacoes/test_changes_gramatica.py (FR-001f, FR-001g)

---

## Phase 3: US1 — Retificar sem ser atropelado por trabalho alheio (P1)

**Objetivo**: duas pessoas alterando Perfis diferentes do mesmo Edital publicam ambas, sem que
nenhuma precise refazer o ato.

**Teste independente**: elaborar duas Retificações sobre Perfis distintos da mesma versão, publicar
em sequência, e verificar que as duas são aceitas e cada uma atinge o seu Perfil.

- [ ] T012 [US1] Recusar na elaboração caminho com índice numérico sobre coleção com chave, com `positional_addressing_refused`, em backend/processo_seletivo/publicacoes/application/retificacoes.py (FR-001c)
- [ ] T013 [US1] Verificar na Publicação que a entidade endereçada existe no conteúdo vigente no início da vigência, com `target_key_not_found`, em backend/processo_seletivo/publicacoes/application/retificacoes.py (FR-002)
- [ ] T014 [US1] Verificar que a referência de um `before=`/`after=` ainda existe, com `position_reference_not_found`, nos dois momentos, em backend/processo_seletivo/publicacoes/application/retificacoes.py (FR-002)
- [ ] T015 [US1] Recusar coleção que ficaria com chave repetida, com `duplicate_key_in_collection`, na elaboração e na Publicação, em backend/processo_seletivo/publicacoes/domain/conflicts.py (FR-004)
- [ ] T016 [US1] Tratar `requirements` como valor atômico: aceitar apenas `REPLACE` da lista inteira e recusar endereçamento item a item, em backend/processo_seletivo/publicacoes/domain/changes.py (FR-004a)
- [ ] T017 [US1] Recusar endereçamento de listas de controle interno, como `applied_publications`, em backend/processo_seletivo/publicacoes/domain/colecoes.py (FR-004b)
- [ ] T018 [US1] Limitar a forma de `targetPath` no `ChangeSerializer` em backend/processo_seletivo/publicacoes/api/serializers.py, para que forma inválida vire recusa de borda e não erro de domínio
- [ ] T019 [P] [US1] Cobrir o cenário central em backend/tests/integration/publicacoes/test_enderecamento.py — duas Retificações sobre Perfis distintos da mesma versão publicam ambas (SC-001)
- [ ] T020 [P] [US1] Cobrir que duas Retificações sobre o mesmo campo do mesmo Perfil continuam sendo recusadas por `expected_hash_mismatch` em backend/tests/integration/publicacoes/test_enderecamento.py — a precondição por hash não saiu junto com a âncora (FR-003)
- [ ] T021 [P] [US1] Cobrir a recusa na elaboração e a recusa na Publicação como momentos distintos, com os códigos de cada uma, em backend/tests/integration/publicacoes/test_enderecamento.py (SC-004, SC-005)
- [ ] T022 [P] [US1] Cobrir `requirements` substituída inteira, inclusive por lista vazia, e recusada item a item, em backend/tests/integration/publicacoes/test_enderecamento.py (FR-004a)
- [ ] T023 [P] [US1] Cobrir chave repetida, identificador presente em duas coleções distintas — que é irrelevante — e `ADD` cuja referência foi removida no intervalo, em backend/tests/integration/publicacoes/test_enderecamento.py

---

## Phase 4: US2 — Ler o histórico sem ambiguidade (P1)

**Objetivo**: a trilha identifica qual entidade cada ato alterou, inclusive nos atos anteriores a
esta mudança, sem recalcular posições.

**Teste independente**: consultar versão vigente e histórico de um Edital com Retificações
publicadas antes da feature, e comparar com o que produziam antes.

- [ ] T024 [US2] Garantir que consolidação, consulta histórica e proveniência continuam resolvendo caminho posicional, sem prazo, em backend/processo_seletivo/publicacoes/domain/consolidation.py (FR-001d)
- [ ] T025 [US2] Registrar em `ProvenienciaConteudo.target_path` o caminho tal como o ato o declarou, sem converter, em backend/processo_seletivo/publicacoes/application/retificacoes.py (FR-010)
- [ ] T026 [P] [US2] Cobrir que o hash canônico de cada Versão Consolidada existente é idêntico antes e depois da mudança, em backend/tests/integration/publicacoes/test_historico_duas_formas.py (SC-002)
- [ ] T027 [P] [US2] Cobrir a consulta temporal sobre o conjunto definido de instantes — cada fronteira de vigência, um segundo antes e um depois — em backend/tests/integration/publicacoes/test_historico_duas_formas.py (SC-003)
- [ ] T028 [P] [US2] Cobrir a coexistência das duas formas no **mesmo** Edital, com atos antigos posicionais e novos por chave compondo juntos, em backend/tests/integration/publicacoes/test_historico_duas_formas.py (FR-006)

---

## Phase 5: US4 — Atravessar a virada com trabalho em curso (P1)

**Objetivo**: Retificações não publicadas no dia da mudança são convertidas, ou devolvidas com
motivo — nunca publicam instáveis, nunca são convertidas por inferência.

**Teste independente**: preparar Retificações em cada estado não final, rodar a migração e verificar
o desfecho de cada uma.

- [ ] T029 [US4] Criar backend/processo_seletivo/publicacoes/migrations/0008_converter_caminhos.py com a lógica de conversão **congelada dentro dela**, como a `0006` da `003` (FR-002d da 003)
- [ ] T030 [US4] Implementar o critério de inequivocidade na `0008` — âncora existe, é única, corresponde à mesma entidade no snapshot-base — em backend/processo_seletivo/publicacoes/migrations/0008_converter_caminhos.py (FR-005c)
- [ ] T031 [US4] Converter o `target_path` das Alterações de Retificações em estado não final, preservando o estado da Retificação, em backend/processo_seletivo/publicacoes/migrations/0008_converter_caminhos.py (FR-005a)
- [ ] T032 [US4] Devolver para elaboração, com `return_reason` que nomeia a alteração e a condição que falhou, o que não resolver inequivocamente, em backend/processo_seletivo/publicacoes/migrations/0008_converter_caminhos.py (FR-005c, FR-011)
- [ ] T033 [US4] Registrar na auditoria cada conversão com caminho antes, caminho depois, momento e a identificação da migração — não uma pessoa — em backend/processo_seletivo/publicacoes/migrations/0008_converter_caminhos.py (FR-005b)
- [ ] T034 [US4] Relatar convertidas e devolvidas **por origem**, para que ato fora das duas origens previstas apareça em vez de passar como sucesso, em backend/processo_seletivo/publicacoes/migrations/0008_converter_caminhos.py (FR-005d)
- [ ] T035 [US4] Escrever a função inversa da `0008`, exigida pela regra permanente do projeto, em backend/processo_seletivo/publicacoes/migrations/0008_converter_caminhos.py
- [ ] T036 [P] [US4] Cobrir a conversão nos três estados não finais, preservando o estado, em backend/tests/migrations/test_converter_caminhos.py (SC-006)
- [ ] T037 [P] [US4] Cobrir cada uma das quatro falhas de inequivocidade — ausência, duplicidade, divergência, âncora incompleta — levando a devolução com motivo, em backend/tests/migrations/test_converter_caminhos.py (FR-005c, SC-010)
- [ ] T038 [P] [US4] Cobrir que Retificação em estado final não é tocada, e que a leitura do caminho posicional dela continua resolvendo, em backend/tests/migrations/test_converter_caminhos.py (FR-005)
- [ ] T039 [P] [US4] Cobrir o no-op sobre Edital sem Retificação em curso, relatando zero e zero sem falhar, em backend/tests/migrations/test_converter_caminhos.py
- [ ] T040 [P] [US4] Cobrir que a cópia congelada da `0008` produz o mesmo que a regra viva, sobre várias formas de caminho, em backend/tests/migrations/test_converter_caminhos.py
- [ ] T041 [US4] Criar backend/processo_seletivo/publicacoes/migrations/0009_remover_ancoras.py, que **comprova** a condição de SC-007 e falha em vez de apagar se houver caso pendente (FR-009)
- [ ] T042 [P] [US4] Cobrir que a `0009` recusa aplicar quando resta Retificação não final com `expected_anchors`, em backend/tests/migrations/test_remover_ancoras.py (SC-007)
- [ ] T043 [US4] Parar de derivar âncora em `derive_preconditions` e remover a verificação `ANCHOR_MISMATCH`, mantendo a precondição por hash intacta, em backend/processo_seletivo/publicacoes/domain/conflicts.py (FR-009, FR-003)
- [ ] T044 [P] [US4] Atualizar os testes da `003` que afirmavam `target_identity_mismatch`, substituindo pela recusa que passa a valer, em backend/tests/integration/publicacoes/test_retificacoes.py

---

## Phase 6: US3 — Compor a Retificação sem conhecer a representação (P2)

**Objetivo**: quem elabora continua editando o conteúdo vigente na tela, sem saber que existe
caminho, chave ou índice.

**Teste independente**: alterar campos de um Perfil pela tela e verificar que as Alterações emitidas
usam a chave, sem que nada tenha mudado para quem usa.

- [ ] T045 [US3] Emitir `/profiles/id=<uuid>/…` e `/schedule/id=<uuid>/…` em `campos_editaveis` e `diferencas` em backend/processo_seletivo/interface/retificacao.py (FR-007)
- [ ] T046 [US3] Emitir remoção por `id=` e acréscimo por `-`, em backend/processo_seletivo/interface/retificacao.py (FR-001e)
- [ ] T047 [US3] Remover a coreografia de ordem — `REPLACE` primeiro, `REMOVE` decrescente, `ADD` por último — que existia só porque índice deslocava, em backend/processo_seletivo/interface/retificacao.py (R5 do research.md)
- [ ] T048 [US3] Garantir que nenhum caminho normativo aparece no HTML entregue pela tela de Retificação em backend/processo_seletivo/interface/templates/interface/retificar.html (FR-007)
- [ ] T049 [P] [US3] Cobrir as duas condições de FR-007 sobre a página renderizada — sem caminho no HTML, alterações por chave — em backend/tests/interface/test_retificar.py (SC-008)
- [ ] T050 [P] [US3] Cobrir que acrescentar e remover na mesma edição, em qualquer ordem, produz o mesmo ato, em backend/tests/unit/interface/test_retificacao_estrutural.py (US3 cenário 2)
- [ ] T051 [P] [US3] Atualizar os testes que dependiam da ordem de emissão em backend/tests/unit/interface/test_retificacao_estrutural.py, verificando que a garantia agora vem da chave e não da sequência

---

## Phase 7: Polish e questões transversais

- [ ] T052 Aplicar o delta do contrato no specs/001-processo-seletivo-editais/contracts/openapi.yaml — descrição de `targetPath`, formas de `ADD`, e os quatro códigos novos nas respostas 409 e 422 (FR-008, FR-001b)
- [ ] T053 [P] Cobrir que o contrato descreve a extensão, os quatro códigos e a forma de `ADD`, em backend/tests/contract/test_enderecamento_api.py (SC-009)
- [ ] T054 [P] Cobrir que um caminho publicado identifica a entidade alterada sem consultar a versão vigente, em backend/tests/contract/test_enderecamento_api.py (FR-001i)
- [ ] T055 Atualizar a seção de Retificação no README.md com a forma nova e a ordem de implantação da migração
- [ ] T056 [P] Verificar a cobertura com branches nas duas execuções — SQLite e PostgreSQL —, exigida em ao menos 89% com três casas, conforme a configuração de backend/pyproject.toml
- [ ] T057 Executar o roteiro de specs/004-enderecamento-normativo-estavel/quickstart.md de ponta a ponta, incluindo o que ele marca como verificação manual

---

## Dependências

- **Fase 2 bloqueia tudo**: sem gramática e resolução, nenhuma história funciona.
- **T003 precede T004**: a declaração existe antes do teste que a guarda.
- **T005 → T006 → T007/T008**: reconhecer o seletor, resolver, aplicar — nessa ordem.
- **US1 e US2 são independentes entre si** e podem correr em paralelo depois da Fase 2.
- **US4 depende de US1**: a conversão produz caminhos que a resolução precisa aceitar.
- **T043 depende de T031**: parar de derivar âncora antes de converter tiraria o insumo da conversão.
- **T041 depende de T036 a T040**: a `0009` só faz sentido com a conversão comprovada.
- **US3 depende da Fase 2**, não das demais histórias.
- **T052 depende de US1**, porque documenta os códigos que ela introduz.

## Execução em paralelo

Depois da Fase 2, três frentes correm juntas:

```
US1  T012–T018 (sequenciais, mesmo arquivo)  →  T019–T023 [P]
US2  T024–T025                                →  T026–T028 [P]
US3  T045–T048                                →  T049–T051 [P]
```

US4 entra quando US1 fechar. Dentro dela, T036 a T040 e T042 são paralelos entre si.

## Estratégia de entrega

**MVP: Fase 2 + US1.** É o que entrega o ganho que a `003` não podia dar — duas pessoas em Perfis
diferentes publicam ambas — e o que fecha a causa do defeito. Sozinho já é incremento defensável.

**US2 vem junto ou logo depois**, porque sem ela a leitura do histórico quebra: são atos publicados
que nenhuma migração pode reescrever.

**US4 é o que torna a implantação segura** e não pode faltar no mesmo release: sem ela, os atos em
curso atravessam a virada e publicam instáveis depois de a cura existir.

**US3 pode ficar para depois** sem prejuízo de correção — a interface continuaria emitindo forma
posicional, que US1 recusaria na elaboração. Mas isso deixaria a tela quebrada, então na prática ela
acompanha o mesmo release; a prioridade P2 reflete o risco, não a sequência.

## Situação

57 tarefas, nenhuma iniciada. A implementação não começou.
