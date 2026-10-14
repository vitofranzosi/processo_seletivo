# Tasks: Configurar, verificar e testar o correio e o Ollama na implantação

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[contracts/secao-do-guia.md](contracts/secao-do-guia.md), [quickstart.md](quickstart.md)

**Testes**: pedidos pela spec (SC-621, SC-622, SC-624). O teste do guia é o que impede a seção de
divergir do código.

**Branch**: `claude/073-configurar-e-verificar`, sobre as do #282 e do #281.

## Phase 1: Setup

- [ ] T001 Confirmar que a branch contém a spec (#282) e o §16.5 (#281), e rodar `uv sync --extra dev` em `backend/`

## Phase 2: Foundational

- [ ] T002 Acrescentar `EMAIL_HOST` ao `AMBIENTE_MINIMO` de `backend/tests/test_configuracao_producao.py`, antes da regra nova, para que os casos de subprocesso e de carga continuem descrevendo um ambiente que sobe (risco do plano)

**Checkpoint**: `test_configuracao_producao.py` verde sem mudança de código.

## Phase 3: User Story 1 — o correio de produção (Priority: P1) 🎯 MVP

**Goal**: a TI configura o correio e o comprova em etapas, pela §10.4.

**Independent Test**: os casos da regra nova e o teste do guia contra servidores SMTP falsos locais;
em homologação, o quickstart B.

- [ ] T003 [US1] Escrever em `backend/tests/test_configuracao_producao.py` os casos `EMAIL_HOST` ausente e só com espaços, com o backend SMTP, recusando com `EMAIL_HOST` (FR-1660)
- [ ] T004 [US1] Acrescentar a recusa em `backend/config/settings/production.py`, só quando o backend for o SMTP, depois da recusa do remetente (R-006)
- [ ] T005 [US1] Escrever a §10.4 em `doc/implantacao-em-producao-ubuntu.md`. Ela traz:
  - os passos 1 a 4, 7 e 8 do contrato;
  - o bloco `app.env` do correio;
  - o exemplo de leitura, com a ressalva do processo de diagnóstico;
  - o exemplo de conexão sem envio;
  - os dois instantes do reinício;
  - as linhas de correio da tabela, sem concluir por causa nenhuma (FR-1650 a FR-1657)
- [ ] T006 [US1] Fazer o §16.3, o §16.5, o §25 e o sumário de `doc/implantacao-em-producao-ubuntu.md` remeterem à §10.4. O §16.5 fica com o que só ele tem (R-001)
- [ ] T007 [P] [US1] Criar `backend/tests/test_guia_configurar_verificar.py`, que prende a §10.4 a partir do próprio guia:
  - variáveis dos blocos lidas pelas settings;
  - a leitura com segredos plantados não os imprime;
  - a conexão contra servidores SMTP falsos dá a última linha da tabela e não envia;
  - nenhuma linha atribui o tempo esgotado a uma causa só

**Checkpoint**: US1 completa e verificável sozinha.

## Phase 4: User Story 2 — o Ollama de produção (Priority: P1)

**Goal**: a TI configura o Ollama e o comprova em três níveis — conexão, modelo disponível e
inferência efetiva.

**Independent Test**: a mensagem do serviço desconhecido; o teste do guia contra um Ollama falso
local.

- [ ] T008 [US2] Escrever em `backend/tests/unit/duvidas/test_verificar_servico.py` os casos `Ollama` (desconhecido, com o valor e os aceitos) e vazio (nenhum serviço configurado), os dois saindo com 1 (FR-1661)
- [ ] T009 [US2] Separar as duas mensagens em `backend/processo_seletivo/duvidas/management/commands/verificar_servico_de_inferencia.py` (R-007)
- [ ] T010 [US2] Completar a §10.4 em `doc/implantacao-em-producao-ubuntu.md` com:
  - o bloco `app.env` do assistente;
  - os passos 5, 6 e 9, com a ressalva de que a versão sozinha não prova o modelo;
  - as linhas do Ollama na tabela
- [ ] T011 [US2] Estender `backend/tests/test_guia_configurar_verificar.py` com um Ollama falso local: o passo 5 imprime a versão, o 6 diz "instalado" ou "NÃO instalado", e nenhum dos dois chama `/api/chat`

**Checkpoint**: US1 e US2 completas.

## Phase 5: Polish

- [ ] T012 [P] Atualizar `README.md`, § Produção: a recusa nova na lista, e um parágrafo que aponta a §10.4 para produção e o roteiro de troca do assistente para desenvolvimento, dizendo o que difere entre os dois (FR-1658)
- [ ] T013 [P] Escrever `specs/073-configurar-e-verificar-implantacao/rastreabilidade.md`, com cada FR e SC e onde é provado
- [ ] T014 Rodar `make lint check test-pg DB_NAME=test_073` em `backend/` e registrar o resultado em `specs/073-configurar-e-verificar-implantacao/verificacao.md`

## Dependencies & Execution Order

- T001 → T002 → US1 e US2.
- US1 e US2 são independentes, mas as duas editam a §10.4: T010 vem depois de T005.
- T007 e T011 editam o mesmo arquivo de teste: T011 vem depois de T007.
- Polish por último. T014 encerra.

## Parallel Example

- Em US1: T003 e T007 tocam arquivos diferentes.
- Em US2: T008 independe da §10.4.
- No Polish: T012 e T013 rodam juntos.

## Implementation Strategy

O MVP é a US1, porque sem correio nenhum candidato entra. A US2 entra na mesma branch: o escopo é
pequeno, e o PR é um só.
