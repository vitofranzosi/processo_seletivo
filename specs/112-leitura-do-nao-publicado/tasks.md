---

description: "Tasks da 112 — leitura do conteúdo não publicado na gestão"
---

# Tasks: Leitura do conteúdo não publicado na gestão

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: pedidos pela spec (FR-3524, FR-3525, SC-1061 a SC-1065). Os testes de cada fase vêm
**antes** da implementação e devem falhar primeiro.

**Caminhos**: relativos à raiz do repositório. `V` é `backend/processo_seletivo/interface/views.py`.

**Não começar sem** as respostas das P-1 a P-4, ou sem o "ok" do usuário para seguir com o
comportamento padrão de cada uma.

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup

- [ ] T001 Conferir a base: `manage.py migrate --check`, e `tests/test_gramatica_das_portas.py`, `tests/test_citacoes_de_requisito.py` e `tests/test_sem_dado_pessoal_da_amostra.py` verdes contra PostgreSQL, num `DB_NAME` próprio da worktree (`backend/`)
- [ ] T002 Levantar os testes existentes que abrem Edital não publicado ou Retificação em curso com identidade que perde o acesso (integrante, julgador, exportador, administrador de acessos, auditor fora da trilha, comissão sem papel): `grep` em `backend/tests/` por `compor`, `previa`, `detalhe`, `retificacao-` e pelos papéis; registrar a lista em `specs/112-leitura-do-nao-publicado/rastreabilidade.md` §Testes que mudam (SC-1062)
- [ ] T003 Conferir a hipótese da `D-004`: escrever, numa cópia descartável de `V`, um `if alcance is Alcance.NENHUM: raise Http404` dentro de uma função da lista `PORTAS` e rodar `tests/test_gramatica_das_portas.py`; registrar em `research.md` §D-004 se o detector o acusa e, se acusar, a forma de declarar a porta como deliberada

---

## Phase 2: Foundational (bloqueia todas as histórias)

- [ ] T004 [P] Escrever `backend/tests/authorization/test_papel_da_leitura_do_rascunho.py`: a grafia `rascunho:ler`; exatamente `elaborador`, `homologador`, `publicador` e `gestor` a têm; nenhum papel de `PAPEIS_DE_ACESSO` nem de `PAPEIS_INSTITUCIONAIS` a tem; `DESCRICOES` e `len(PAPEIS)` inalterados (FR-3502, FR-3522, FR-3523)
- [ ] T005 Acrescentar `"rascunho:ler"` aos quatro papéis em `backend/processo_seletivo/interface/identidade.py`, com o comentário do porquê no tom do catálogo (`D-001`)
- [ ] T006 [P] Escrever `backend/tests/publicacoes/test_leitura_do_nao_publicado.py`, sem requisição: as tabelas do [data-model](data-model.md) linha a linha — Edital publicado, em elaboração, homologado, cancelado sem publicação (EC-1), publicado e cancelado (EC-2); Retificação em revisão, publicada, cancelada sem publicação (EC-3); Processo sem Edital publicado com e sem vínculo (EC-6); dois escopos (EC-8); e `editais_visiveis` em lote sem consulta além do prefetch (FR-3501, FR-3503 a FR-3505)
- [ ] T007 Criar `backend/processo_seletivo/publicacoes/application/leitura_do_nao_publicado.py` com `Alcance`, `alcance_do_edital`, `alcance_da_retificacao`, `alcance_do_processo` e `editais_visiveis` (`D-002`), até a T006 passar
- [ ] T008 Escrever as portas `_edital_para_ler`, `_retificacao_para_ler` e `_processo_para_ler` em `V`, ao lado das sete da `033`, na ordem da `D-003` e com as recusas do [contrato](contracts/recusas.md); acrescentá-las a `PORTAS` em `backend/tests/test_gramatica_das_portas.py`
- [ ] T009 [P] Escrever `backend/tests/test_rotas_do_nao_publicado.py` (FR-3525, SC-1064): resolve `interface/urls.py`, seleciona as rotas com `processo_id`, `edital_id` ou `retificacao_id` e os `fragmento-*`, exige linha no [inventário](contracts/inventario-das-rotas.md) e, nas classes C, E e P, a chamada da porta exigida na função da view (por AST, seguindo um nível de delegação, como `_edital_do_fragmento`); um caso que prova que o detector enxerga uma rota inventada. Deve falhar até o fim da US1
- [ ] T010 [P] Montar em `backend/tests/authorization/conftest.py` (ou num `conftest` próprio do arquivo da T011) os cenários da `D-008` e as doze identidades da FR-3524, com nomes fictícios (o guardião de dado pessoal)

---

## Phase 3: User Story 1 — Quem não prepara o ato não o lê (P1) 🎯 MVP

**Goal**: nenhuma identidade sem a existência alcança Edital não publicado nem Retificação em curso, por tela ou por URL direta.

**Independent Test**: as linhas `NENHUM` da matriz respondem 404, e a lista do integrante não mostra o não publicado (SC-1061, SC-1063).

### Testes

- [ ] T011 [US1] Escrever `backend/tests/authorization/test_leitura_do_nao_publicado.py`: a matriz rota × ator para as rotas C, E e P do inventário, com as identidades sem existência (integrante sem vínculo, administrador de acessos, julgador, exportador, outra unidade) — 404 em todas, com a mesma página de um UUID inventado; a lista sem o Edital não publicado e sem a marca de Retificação; o detalhe do publicado sem a seção de Retificações em curso (FR-3508, FR-3510, FR-3517, FR-3520, FR-3527)
- [ ] T012 [P] [US1] Casos de ordem (EC-4, EC-5, FR-3515): prévia de Edital não publicado pedida por quem não tem a existência responde 404, e não 409; POST em `compor-etapa` responde 404 sem mensagem; em `backend/tests/authorization/test_leitura_do_nao_publicado.py`

### Implementação

- [ ] T013 [US1] `lista` em `V`: `editais_visiveis` com os vínculos já lidos e as Publicações em prefetch; `em_curso_por_edital` só sobre os Editais alcançados (nenhum para quem não tem `rascunho:ler`); `contar_por_situacao` sobre o filtrado (FR-3508, `D-006`)
- [ ] T014 [US1] `detalhe` em `V`: porta com `exige=EXISTENCIA`; seção e cartão de Retificações em curso só com o alcance delas (FR-3509, FR-3510)
- [ ] T015 [US1] Rotas C do Edital em `V` — `compor`, `compor_etapa` (GET e POST), `reaproveitar`, `_edital_com_previa` (logo, `previa` e `previa_documento`), `anexos_acao`, `praticar_ato` — com `_edital_para_ler(exige=CONTEUDO)` antes de qualquer outra conferência (FR-3511)
- [ ] T016 [US1] Fragmentos C em `V`: `fragmento_etapa`, `fragmento_documento`, `_edital_do_fragmento` (que alcança perfil, marco, marco recomposto, critério e prévia da classificação) e `fragmento_perfil_duplicado`, com a resposta htmx do [contrato](contracts/recusas.md) (FR-3511)
- [ ] T017 [US1] Retificação em `V`: `_retificacao_do_ator` passa pela `_retificacao_para_ler`; `retificacao_detalhe`, `retificacao_editar` (porta antes da recusa de `retificacao:elaborar`) e `praticar_ato_retificacao`; em `retificar`, a lista das em curso só com o alcance delas (FR-3512)
- [ ] T018 [US1] Processo em `V`: `_processo_do_ator` passa pela `_processo_para_ler`; `processo_detalhe`, `praticar_ato_processo` e `supervisao` omitem Edital sem a existência (FR-3513, EC-6)
- [ ] T019 [US1] Rotas P, uma a uma, com `_edital_para_ler(exige=EXISTENCIA)` antes de qualquer conferência de estado: as de `V` (distribuição, marcos, ocupação, convocação, sorteio, resultado, recursos, inscrições, matrículas), `backend/processo_seletivo/interface/relatorio.py`, `avisos.py`, `assistente.py`, `duvidas.py`, `prototipo_do_assistente.py` e os três fragmentos de Retificação com `edital_id` (FR-3527). Onde houver porta da `033` que já busca o Edital (`_edital_para_classificar`, `_edital_para_publicar`, `_marco_para_conduzir`…), a porta nova entra **dentro** dela, uma vez
- [ ] T020 [US1] Inventário da `033`: as linhas novas e a reclassificação de `anexo_do_rascunho` em `specs/033-navegacao-por-capacidade/inventario-das-negativas.md`, classe "recusa de autorização — existência de ato não publicado" (FR-3519); `tests/test_gramatica_das_portas.py` verde
- [ ] T021 [US1] Ajustar os testes da lista da T002 que perderam o acesso: cada um troca de identidade ou passa a afirmar a recusa, e entra na rastreabilidade (SC-1062)

**Checkpoint**: T009, T011 e T012 verdes; a matriz `NENHUM` inteira em 404.

---

## Phase 4: User Story 2 — Quem prepara, revisa, publica ou conduz segue igual (P1)

**Goal**: nenhuma recusa nova a elaborador, homologador, publicador e gestor.

**Independent Test**: as linhas `CONTEUDO` da matriz respondem 200, e as suítes de jornada existentes passam sem mudança de expectativa (SC-1062).

- [ ] T022 [P] [US2] Linhas `CONTEUDO` da matriz em `backend/tests/authorization/test_leitura_do_nao_publicado.py`: cada papel do fluxo nas rotas da jornada dele (compor, prévia, PDF, anexo, atos, Retificação), 200; o publicador e o gestor abrindo anexo do rascunho (FR-3507)
- [ ] T023 [US2] `anexo_do_rascunho` em `V`: troca `LEITURA_DO_RASCUNHO` pela porta com `exige=CONTEUDO`; remove a constante e atualiza a docstring, que cita a FR-017 da `020` (FR-3507, P-2). **Se a P-2 for recusada**, esta tarefa sai e a constante fica, com a matriz afirmando 404 ao publicador e ao gestor no anexo
- [ ] T024 [US2] Rodar `tests/authorization/`, `tests/interface/` e `tests/navegador/` (com o grupo `navegador`) contra PostgreSQL e conferir que só mudaram os testes listados na T002

**Checkpoint**: US1 e US2 juntas são o MVP: fecham a P-2 da `111` sem perder jornada.

---

## Phase 5: User Story 3 — Comissão e auditor sabem que o Edital existe (P2)

**Goal**: existência sem conteúdo para quem tem vínculo de comissão no Processo e para o auditor.

**Independent Test**: as linhas `EXISTENCIA` da matriz — detalhe reduzido 200, rotas de conteúdo 403 explicado, Edital de outro Processo 404.

- [ ] T025 [P] [US3] Linhas `EXISTENCIA` da matriz em `backend/tests/authorization/test_leitura_do_nao_publicado.py`: presidência e membro de comissão no próprio Processo e em outro; auditor; o texto canônico da recusa (FR-3504, FR-3509, FR-3518)
- [ ] T026 [US3] O detalhe reduzido em `backend/processo_seletivo/interface/templates/interface/detalhe.html` (e o contexto em `V`): identificação, situação, ações da pessoa e o aviso; sem pendências, participantes nem Retificações; estilo só em folha (`gestao.css` ou `interface/telas/`), nunca inline — a CSP; classe nova com regra na folha (FR-3509)
- [ ] T027 [US3] Na lista, o Edital alcançado só por existência aparece sem ações de conteúdo, e o do auditor com o caminho para a trilha (`lista.html`, `acoes.do_edital` sem mudança de regra — a faixa e as ações já filtram por capacidade)
- [ ] T028 [US3] Conferir que comissão, alocações, supervisão e relatório da presidência continuam abrindo (rotas B do inventário) — casos na matriz

---

## Phase 6: Polish & Cross-Cutting

- [ ] T029 [P] `visao_geral.py`: os Editais do recorte pela mesma regra (FR-3514, EC-11), com teste em `backend/tests/authorization/test_visao_institucional.py`
- [ ] T030 [P] Testes que prendem a ausência de não publicado na Agenda, na trilha da unidade, no relatório do Edital, nas alocações e na faixa (FR-3516, EC-10, EC-12)
- [ ] T031 [P] Orçamento da lista: `django_assert_num_queries` com e sem `rascunho:ler`, igual antes e depois (FR-3526, SC-1065), junto dos testes de orçamento da `104`
- [ ] T032 Completar `specs/112-leitura-do-nao-publicado/rastreabilidade.md` com os nomes reais dos testes, conferidos contra os arquivos
- [ ] T033 Quickstart à mão (SC-1063) e a sessão de homologação com o usuário (SC-1066)
- [ ] T034 Nota na `111`: a P-2 dela aponta para esta spec mergeada (só depois do merge; edição da `111`, não desta)
- [ ] T035 `cd backend && make lint check test-pg`

---

## Dependencies & Execution Order

- Setup (T001–T003) → Foundational (T004–T010) → US1 → US2 → US3 → Polish.
- T005 depende de T004; T007 de T006; T008 de T007 e de T003.
- US1 é a base de US2 e US3: as portas são as mesmas; US2 e US3 acrescentam linhas à matriz e o
  detalhe reduzido.
- T019 é a tarefa mais longa; pode ser repartida por arquivo depois da T008.
- T020 e T021 fecham a US1; T024 só depois da T023.

## Parallel Opportunities

- T004, T006, T009 e T010 em paralelo (arquivos distintos).
- Em US1, T012 com T011 (mesmo arquivo — escrever em sequência, mas sem depender de implementação).
- T015 a T019 tocam `V` e não paralelizam entre si; T019 nos módulos fora de `V` sim.
- T029, T030 e T031 em paralelo.

## Implementation Strategy

**MVP** = US1 + US2: a regra, as portas, a matriz `NENHUM` e `CONTEUDO`. Com isso a P-2 da `111` se
fecha e nenhuma jornada do fluxo perde tela. US3 entrega o detalhe reduzido; sem ela, a comissão e
o auditor receberiam 404 no detalhe do Edital não publicado — por isso **US3 entra no mesmo PR** que
o MVP, e não depois, para não quebrar a jornada da presidência entre um merge e outro.
