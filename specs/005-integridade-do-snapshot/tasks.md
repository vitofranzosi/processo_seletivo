---
description: "Tarefas de implementação da Integridade do Snapshot Normativo"
---

# Tasks: Integridade do Snapshot Normativo

**Input**: Design documents from `/specs/005-integridade-do-snapshot/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/integridade.md`, `quickstart.md`

**Tests**: incluídos, e não por opção. O princípio V da Constituição exige teste automatizado para
regra crítica, nomeando publicação e retificação — que é o que esta feature altera.

**Organization**: agrupadas por história, para que cada uma seja implementável e verificável em
separado.

## Format: `[ID] [P?] [Story] Descrição`

- **[P]**: executável em paralelo — arquivo distinto, sem dependência pendente
- **[Story]**: história rastreada (`US1`, `US2`); Setup, Foundational e Polish não têm

## Path Conventions

Monólito modular existente. Código em `backend/processo_seletivo/`, testes em `backend/tests/`.

## Uma observação sobre o tamanho de US1

A Publicação **já chama** a verificação estrutural uma vez por fronteira de vigência
(`_materialize_affected_versions`). Aprofundada a verificação na Fase 2, a US1 passa a valer sem
mudança de produção: as tarefas dela são os testes que provam o portão, o rollback e o comportamento
por fronteira, que hoje não existem. Isso é resultado do desenho, não descuido — construir um segundo
laço seria a duplicação que o princípio V manda evitar.

---

## Phase 1: Setup

- [ ] T001 [P] Acrescentar construtores de snapshot malformado a backend/tests/fixtures/snapshot.py — uma variante por violação (campo ausente, tipo diferente, nulo indevido, formato inválido, fora da restrição declarada), reutilizadas pelas duas histórias

---

## Phase 2: Foundational

**⚠️ Nenhuma história funciona sem esta fase.** É a forma canônica e a verificação; tudo o mais
consome.

- [ ] T002 Acrescentar os esquemas `PerfilPublicado` e `EventoPublicado` a specs/001-processo-seletivo-editais/contracts/openapi.yaml, com os campos canônicos, tipos, nulabilidade, formatos e as restrições que os esquemas de entrada já declaram (FR-005)
- [ ] T003 Declarar a forma canônica de Perfil e Evento em backend/processo_seletivo/editais/domain/validation.py, transcrevendo os esquemas publicados (FR-005)
- [ ] T004 [P] Cobrir a transcrição contra o contrato em backend/tests/contract/test_forma_publicada.py — alterar o `openapi.yaml` sem alterar a declaração precisa fazer a suíte falhar (FR-005)
- [ ] T005 Verificar cada Perfil e cada Evento em `validate_for_publication` em backend/processo_seletivo/editais/domain/validation.py, produzindo achado impeditivo para as cinco violações — sobre o conteúdo resultante, e nunca sobre uma alteração isolada (FR-001, FR-004, FR-006)
- [ ] T006 Aplicar as restrições que o contrato já escreve — faixa e enumeração — sem acrescentar coerência entre campos, em backend/processo_seletivo/editais/domain/validation.py (FR-009)
- [ ] T007 Compor o caminho do achado na gramática da `004` — `/profiles/id=<uuid>/requirements` — e dizer na mensagem qual violação ocorreu, em backend/processo_seletivo/editais/domain/validation.py (FR-011)
- [ ] T008 [P] Cobrir as cinco violações em backend/tests/unit/editais/test_forma_do_snapshot.py, uma por dimensão, em Perfil e em Evento (FR-006)
- [ ] T009 [P] Cobrir que valor vazio admissível não é violação — lista vazia, texto vazio, objeto vazio — e que nulo onde se admite nulo passa, em backend/tests/unit/editais/test_forma_do_snapshot.py (FR-007)
- [ ] T010 [P] Cobrir que campo não declarado é aceito, em backend/tests/unit/editais/test_forma_do_snapshot.py — o conteúdo normativo pode crescer sem que isso vire quebra (FR-008)
- [ ] T011 [P] Cobrir que o achado nomeia o caminho por chave e diz a violação, em backend/tests/unit/editais/test_forma_do_snapshot.py (FR-011)
- [ ] T012 [P] Cobrir que as quatro condições de raiz que já existiam continuam valendo, em backend/tests/unit/editais/test_publicacao.py — a verificação nova não pode substituir a antiga (FR-015)

---

## Phase 3: US1 — Nenhum Edital malformado passa a vigorar (P1)

**Objetivo**: quem publica uma Retificação não consegue deixar vigente um Edital que a Publicação
original jamais teria aceitado.

**Teste independente**: partir de uma Retificação malformada já homologada, gravada diretamente,
publicá-la e verificar que é recusada, que nada é materializado e que o conteúdo vigente não muda.

**Por que gravada diretamente**: a US2 recusa o ato na elaboração, e ele não chega à Publicação pelo
caminho normal. É o padrão que a `003` usa para a linha restaurada de backup ou criada por
importação (FR-013).

- [ ] T013 [US1] Construir o cenário do ato malformado já homologado em backend/tests/integration/publicacoes/test_integridade_snapshot.py, gravando a Alteração direto e levando a Retificação a HOMOLOGADA
- [ ] T014 [US1] Cobrir a recusa na Publicação de um `REPLACE` de Perfil inteiro que omite campos obrigatórios, em backend/tests/integration/publicacoes/test_integridade_snapshot.py (SC-001)
- [ ] T015 [P] [US1] Cobrir a recusa na Publicação de um `REMOVE` de campo obrigatório, em backend/tests/integration/publicacoes/test_integridade_snapshot.py (SC-002)
- [ ] T016 [P] [US1] Cobrir que a recusa não deixa Publicação, documento nem versão consolidada materializados, e que o conteúdo vigente permanece o de antes, em backend/tests/integration/publicacoes/test_integridade_snapshot.py (FR-012)
- [ ] T017 [P] [US1] Cobrir a fronteira posterior em backend/tests/integration/publicacoes/test_integridade_snapshot.py — um Edital com Retificação de vigência futura já publicada, e um ato que deixaria malformada só a fronteira seguinte: a recusa alcança o ato inteiro e a mensagem nomeia a fronteira (FR-003, SC-005)
- [ ] T018 [P] [US1] Cobrir que uma Retificação bem formada continua publicando, com alteração de valores, acréscimo e remoção de entidades, em backend/tests/integration/publicacoes/test_integridade_snapshot.py (FR-014, SC-004)

---

## Phase 4: US2 — Quem elabora descobre antes de submeter (P2)

**Objetivo**: a recusa acontece na criação e na edição do rascunho, com o caminho e a violação, em
vez de consumir um ciclo de aprovação até a Publicação.

**Teste independente**: enviar a Retificação malformada na criação e verificar que é recusada ali,
com mensagem que nomeia o caminho do campo e diz o que há de errado com ele.

- [ ] T019 [US2] Chamar a verificação em `_apply_declared_changes` em backend/processo_seletivo/publicacoes/application/retificacoes.py, depois das precondições de conteúdo e antes da exigência de efeito prático (FR-002)
- [ ] T020 [P] [US2] Cobrir a recusa na criação da Retificação com `422 blocking_findings`, em backend/tests/integration/publicacoes/test_integridade_snapshot.py (FR-010, SC-001)
- [ ] T021 [P] [US2] Cobrir a mesma recusa na atualização do rascunho, em backend/tests/integration/publicacoes/test_integridade_snapshot.py (FR-002)
- [ ] T022 [P] [US2] Cobrir que a mensagem nomeia o caminho por chave e a violação, de modo que se identifique a entidade sem consultar a versão vigente, em backend/tests/integration/publicacoes/test_integridade_snapshot.py (FR-011, SC-003)
- [ ] T023 [P] [US2] Cobrir que corrigir o conteúdo e reenviar é aceito, sem etapa nova nem campo novo, em backend/tests/integration/publicacoes/test_integridade_snapshot.py (FR-014)
- [ ] T024 [P] [US2] Cobrir que a recusa por precondição de conteúdo continua prevalecendo quando ambas valem, em backend/tests/integration/publicacoes/test_integridade_snapshot.py — a causa serve melhor que a consequência (FR-002)

---

## Phase 5: Polish e questões transversais

- [ ] T025 Aplicar o delta do contrato em specs/001-processo-seletivo-editais/contracts/openapi.yaml — declarar `blocking_findings` nas respostas `422` que o produzem, e descrever nas operações de Retificação que a verificação alcança o conteúdo resultante e cada fronteira materializada (FR-010)
- [ ] T026 [P] Cobrir que o contrato declara `blocking_findings` e os esquemas publicados, em backend/tests/contract/test_forma_publicada.py (FR-010)
- [ ] T027 Rodar a suíte de backend/tests/interface/test_impedimentos.py e investigar qualquer mudança na lista de pendências da tela de composição — teste novo só se ela acusar regressão
- [ ] T028 Executar o roteiro de specs/005-integridade-do-snapshot/quickstart.md de ponta a ponta, incluindo a linha de base "antes" com as cinco violações, e confirmar que não sobrou caminho pelo qual uma Retificação deixe vigente um Edital que a Publicação original recusaria (SC-005)
- [ ] T029 Conferir a suíte nas duas execuções e a cobertura com ramos do código novo, conforme os critérios de entrega em specs/005-integridade-do-snapshot/plan.md

---

## Dependências

- **Fase 2 bloqueia tudo**: sem a forma canônica e a verificação, nenhuma história anda.
- **T002 precede T003 e T004**: o contrato existe antes da transcrição e antes da guarda que as compara.
- **T003 → T005 → T006 → T007**: declarar, verificar, restringir, nomear.
- **US1 e US2 são independentes entre si** e podem correr em paralelo depois da Fase 2.
- **US1 não depende de mudança de produção** além da Fase 2: o laço por fronteira já chama a verificação.
- **T025 depende de US2**, porque documenta a recusa no momento que ela introduz.
- **T027 depende da Fase 2**, que é onde o comportamento da validação muda.

## Execução em paralelo

Depois da Fase 2, duas frentes correm juntas:

```
US1  T013 → T014 → T015–T018 [P]
US2  T019    →    T020–T024 [P]
```

Dentro da Fase 2, T004 e T008–T012 são paralelos entre si depois de T003 e T007.

## Estratégia de entrega

**MVP: Fase 2 + US1.** É a garantia que a feature promete — nenhum Edital malformado passa a
vigorar — e vale mesmo que a recusa na elaboração não exista.

**US2 acompanha o mesmo release.** Ela não muda o que é impedido, muda quando: sem ela, quem elabora
descobre o problema depois de a submissão e a homologação já terem consumido o tempo de outras
pessoas. É melhoria de fluxo sobre uma garantia que já estaria de pé — daí ser P2.

**A ordem entre elas importa para os testes.** Com a US2 pronta, o ato malformado não chega mais à
Publicação pelo caminho normal, e é por isso que a US1 se testa com o ato gravado direto.

## Situação

29 tarefas, nenhuma iniciada. A implementação não começou.
