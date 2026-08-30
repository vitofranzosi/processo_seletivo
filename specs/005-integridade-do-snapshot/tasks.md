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

- **[P]**: executável em paralelo. Só onde o arquivo é distinto de toda outra tarefa `[P]` pendente —
  duas tarefas no mesmo arquivo nunca são paralelas, por mais independentes que pareçam.
- **[Story]**: história rastreada (`US1`, `US2`); Setup, Foundational e Polish não têm

## Path Conventions

Monólito modular existente. Código em `backend/processo_seletivo/`, testes em `backend/tests/`.

## Duas observações sobre o tamanho

**US1 não tem tarefa de produção.** A Publicação já chama a verificação estrutural uma vez por
fronteira de vigência (`_materialize_affected_versions`). Aprofundada a verificação na Fase 2, a
garantia passa a valer sem tocar em `retificacoes.py`: as tarefas da US1 são os testes que provam o
portão, o rollback e o comportamento por fronteira, que hoje não existem. É resultado do desenho, e
não descuido — construir um segundo laço seria a duplicação que o princípio V manda evitar.

**A mudança de produção mora em três tarefas**: T002, T003 e T012. O resto é teste, contrato e
verificação.

---

## Phase 1: Setup

- [X] T001 [P] Acrescentar construtores de snapshot malformado a backend/tests/fixtures/snapshot.py — uma variante por violação (campo ausente, tipo diferente, nulo indevido, formato inválido, fora da restrição declarada), reutilizadas pelas duas histórias

---

## Phase 2: Foundational

**⚠️ Nenhuma história funciona sem esta fase.** É a forma canônica e a verificação; tudo o mais
consome.

- [X] T002 Acrescentar os esquemas `PerfilPublicado` e `EventoPublicado` a specs/001-processo-seletivo-editais/contracts/openapi.yaml, com os campos canônicos, tipos, nulabilidade, formatos e as restrições que os esquemas de entrada já declaram (FR-005)
- [X] T003 Transcrever a forma canônica e verificar cada Perfil e Evento do conteúdo em backend/processo_seletivo/editais/domain/validation.py — as cinco violações como erro impeditivo, aplicando as restrições já escritas e sem inventar coerência entre campos, com o achado nomeando o caminho na gramática da `004` e dizendo qual violação ocorreu (FR-001, FR-004, FR-005, FR-006, FR-009, FR-011)
- [X] T004 [P] Cobrir a transcrição contra o contrato em backend/tests/contract/test_forma_publicada.py — alterar o `openapi.yaml` sem alterar a declaração precisa fazer a suíte falhar (FR-005)
- [X] T005 [P] Cobrir as cinco violações em backend/tests/unit/editais/test_forma_do_snapshot.py, uma por dimensão, em Perfil e em Evento (FR-006)
- [X] T006 Cobrir o que **não** é violação em backend/tests/unit/editais/test_forma_do_snapshot.py — valor vazio admissível, nulo onde se admite nulo, campo não declarado — e que o achado nomeia o caminho por chave e diz a violação (FR-007, FR-008, FR-011)
- [X] T007 [P] Cobrir que as quatro condições de raiz que já existiam continuam valendo em backend/tests/unit/editais/test_publicacao.py — a verificação nova não substitui a antiga (FR-015)

---

## Phase 3: US1 — Nenhum Edital malformado passa a vigorar (P1)

**Objetivo**: quem publica uma Retificação não consegue deixar vigente um Edital que a Publicação
original jamais teria aceitado.

**Teste independente**: partir de uma Retificação malformada já homologada, gravada diretamente,
publicá-la e verificar que é recusada, que nada é materializado e que o conteúdo vigente não muda.

**Por que gravada diretamente**: a US2 recusa o ato na elaboração, e ele não chega à Publicação pelo
caminho normal. É o padrão que a `003` usa para a linha restaurada de backup ou criada por
importação (FR-013).

- [X] T008 [P] [US1] Construir o cenário do ato malformado já homologado em backend/tests/integration/publicacoes/test_integridade_publicacao.py — a Alteração gravada direto, a Retificação levada a HOMOLOGADA — e cobrir a recusa da Publicação de um `REPLACE` de Perfil que omite campos obrigatórios, com o conteúdo vigente inalterado e sem Publicação, documento ou versão materializados (FR-012, FR-013, SC-001)
- [X] T009 [US1] Cobrir a mesma recusa para um `REMOVE` de campo obrigatório em backend/tests/integration/publicacoes/test_integridade_publicacao.py (SC-002)
- [X] T010 [US1] Cobrir a fronteira posterior em backend/tests/integration/publicacoes/test_integridade_publicacao.py — um Edital com Retificação de vigência futura já publicada, e um ato que deixaria malformada só a fronteira seguinte: a recusa alcança o ato inteiro e a mensagem nomeia a fronteira (FR-003, SC-005)
- [X] T011 [US1] Cobrir que uma Retificação bem formada continua publicando em backend/tests/integration/publicacoes/test_integridade_publicacao.py — alteração de valores, acréscimo e remoção de entidades, campos vazios e nulos admitidos (FR-014, FR-015, SC-004)

---

## Phase 4: US2 — Quem elabora descobre antes de submeter (P2)

**Objetivo**: a recusa acontece na criação e na edição do rascunho, com o caminho e a violação, em
vez de consumir um ciclo de aprovação até a Publicação.

**Teste independente**: enviar a Retificação malformada na criação e verificar que é recusada ali,
com mensagem que nomeia o caminho do campo e diz o que há de errado com ele.

- [X] T012 [US2] Chamar a verificação em `_apply_declared_changes` em backend/processo_seletivo/publicacoes/application/retificacoes.py, depois das precondições de conteúdo e antes da exigência de efeito prático (FR-002)
- [X] T013 [P] [US2] Cobrir a recusa com `422 blocking_findings` na criação da Retificação e na atualização do rascunho, em backend/tests/integration/publicacoes/test_integridade_elaboracao.py (FR-002, FR-010, SC-001)
- [X] T014 [US2] Cobrir que a mensagem nomeia o caminho por chave e a violação, de modo que se identifique a entidade sem consultar a versão vigente, e que corrigir e reenviar é aceito sem etapa nova, em backend/tests/integration/publicacoes/test_integridade_elaboracao.py (FR-011, FR-014, SC-003)
- [X] T015 [US2] Cobrir que a recusa por precondição de conteúdo continua prevalecendo quando ambas valem, em backend/tests/integration/publicacoes/test_integridade_elaboracao.py — a causa serve melhor que a consequência (FR-002)

---

## Phase 5: Polish e questões transversais

- [X] T016 Aplicar o delta do contrato em specs/001-processo-seletivo-editais/contracts/openapi.yaml — declarar `blocking_findings` nas respostas `422` que o produzem, e descrever nas operações de Retificação que a verificação alcança o conteúdo resultante e cada fronteira materializada (FR-003, FR-010)
- [X] T017 Cobrir que o contrato declara `blocking_findings` e os esquemas publicados, em backend/tests/contract/test_forma_publicada.py (FR-010)
- [X] T018 Rodar backend/tests/interface/test_impedimentos.py e investigar qualquer mudança na lista de pendências da tela de composição — teste novo só se ela acusar regressão
- [X] T019 Executar o roteiro de specs/005-integridade-do-snapshot/quickstart.md de ponta a ponta, conferindo os cenários que a spec enumera — os dois portões, a fronteira posterior e o que continua publicando — e a cobertura com ramos do código novo (SC-005)

---

## Dependências

- **Fase 2 bloqueia tudo**: sem a forma canônica e a verificação, nenhuma história anda.
- **T002 precede T003 e T004**: o contrato existe antes da transcrição e antes da guarda que as compara.
- **T005 precede T006**: mesmo arquivo, e a matriz de violações vem antes do que não é violação.
- **T008 precede T009–T011**: mesmo arquivo, e é ele que constrói o cenário do ato gravado direto.
- **T013 precede T014 e T015**: mesmo arquivo.
- **US1 e US2 são independentes** e correm em paralelo depois da Fase 2 — arquivos de teste distintos.
- **T016 e T017 dependem de US2**, porque documentam a recusa no momento que ela introduz.
- **T017 depende de T004**: mesmo arquivo.
- **T018 depende da Fase 2**, que é onde o comportamento da validação muda.

## Execução em paralelo

Dentro da Fase 2, depois de T003: `T004`, `T005` e `T007` — três arquivos distintos.

Depois da Fase 2, as duas histórias correm juntas:

```
US1  T008 → T009 → T010 → T011      (test_integridade_publicacao.py)
US2  T012 → T013 → T014 → T015      (test_integridade_elaboracao.py)
```

Dentro de cada história as tarefas são sequenciais, porque compartilham arquivo. Separar os testes
das duas histórias em arquivos distintos é o que torna as histórias paralelas de verdade.

## Estratégia de entrega

**MVP: Fase 2 + US1.** É a garantia que a feature promete — nenhum Edital malformado passa a
vigorar — e vale mesmo que a recusa na elaboração não exista.

**US2 acompanha o mesmo release.** Ela não muda o que é impedido, muda quando: sem ela, quem elabora
descobre o problema depois de a submissão e a homologação já terem consumido o tempo de outras
pessoas. É melhoria de fluxo sobre uma garantia que já estaria de pé — daí ser P2.

**A ordem entre elas importa para os testes.** Com a US2 pronta, o ato malformado não chega mais à
Publicação pelo caminho normal, e é por isso que a US1 se testa com o ato gravado direto.

## Situação

19 tarefas, todas concluídas.

Suíte verde nas duas execuções — 711 passando com 43 ignorados no SQLite, 753 com 1 ignorado no
PostgreSQL. `validation.py` com cobertura de linhas e de ramos integral; as linhas descobertas em
`retificacoes.py` são anteriores a esta feature e estão fora dos trechos alterados.

Cada recusa nova foi verificada removendo-a: sem a verificação na elaboração, 9 testes falham; sem
o portão da Publicação, 4; sem a restrição de faixa, 4; sem a de enumeração, 1.
