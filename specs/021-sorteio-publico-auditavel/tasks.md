---

description: "Task list for 021 — Sorteio público auditável"
---

# Tasks: Sorteio público auditável

**Input**: Design documents from `/specs/021-sorteio-publico-auditavel/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/](./contracts/)

**Tests**: incluídos, e não por preferência. O Princípio V da Constituição exige cobertura
específica para publicação, temporalidade, autorização e concorrência — que é exatamente o que esta
feature faz —, e a SC-002 só é verificável por duas implementações rodando os mesmos vetores.

**Organization**: por história, para que cada uma seja implementável e demonstrável sozinha.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode correr em paralelo (arquivos distintos, sem dependência pendente)
- **[Story]**: a história a que a tarefa pertence
- Caminho de arquivo exato em cada tarefa

## Path Conventions

Monólito modular: `backend/processo_seletivo/<módulo>/` para código,
`backend/tests/<nível>/` para testes. Módulo novo: `sorteios`.

---

## Phase 1: Setup

**Purpose**: o esqueleto do módulo, e nada de regra dentro dele.

- [X] T001 Criar o módulo em `backend/processo_seletivo/sorteios/` com `__init__.py`, `apps.py`, `models.py` e os pacotes `domain/`, `application/`, `api/`, `infrastructure/`, `migrations/`, no padrão dos módulos existentes
- [X] T002 Registrar `processo_seletivo.sorteios` em `INSTALLED_APPS` de `backend/config/settings/base.py`
- [X] T003 [P] Criar as pastas de teste `backend/tests/unit/sorteios/`, `backend/tests/integration/sorteios/` e `backend/tests/contract/fixtures/sorteio/`
- [X] T004 [P] Declarar em `backend/config/settings/base.py` apenas o **adaptador** da fonte externa (qual implementação, tempo limite, tentativas), com comentário dizendo que fonte, ocorrência e regra de substituição são conteúdo normativo e não moram aqui (FR-014)

---

## Phase 2: Foundational (Blocking Prerequisites)

**⚠️ CRITICAL**: nenhuma história começa antes desta fase fechar. Aqui vive o que todas consomem: a
chave, os vetores, os modelos e a constraint dividida.

### O algoritmo, antes de qualquer tela

- [X] T005 Implementar `backend/processo_seletivo/sorteios/domain/chave.py` — chave por participante sobre `canonical_bytes`, ordenação crescente pelo resumo completo e desempate por número público (FR-021, FR-022, FR-023, D-005); função pura, sem Django
- [X] T006 [P] Escrever os cinco vetores normativos em `backend/tests/contract/fixtures/sorteio/`, nas **duas formas** do contrato — de chave: `tres-participantes`, `acentos-e-nfc`, `um-participante`, `mesma-semente-recortes-distintos`; de ordenação: `desempate-por-numero-publico`, com as chaves dadas já iguais. O vetor de desempate **não** se apresenta como colisão de SHA-256: entrada válida do sistema não produz duas chaves iguais, e prometer isso deixaria a tarefa impossível de fechar (FR-028, R-004)
- [X] T073 Escrever `backend/tests/unit/sorteios/test_chave_fechada.py` — a chave recebe **apenas** os cinco campos do contrato, e nenhum valor escolhido por ator depois do congelamento a alcança: a tentativa de injetar campo extra falha, e alterar qualquer entrada muda o resumo (FR-024)
- [X] T007 Escrever `backend/tests/contract/test_vetores_de_sorteio.py`, que exercita as duas formas contra `domain/chave.py` — a de chave cobrando bytes canônicos, resumo e ordem; a de ordenação cobrando só a ordem, a partir das chaves dadas — e falha se qualquer uma divergir (FR-027, FR-028)
- [X] T008 [P] Implementar a referência em JavaScript em `backend/processo_seletivo/portal/static/portal/sorteio.js`, sem dependência externa, lendo os mesmos vetores (SC-002)
- [X] T009 [P] Escrever `backend/tests/javascript/sorteio.test.js`, que roda os vetores pela referência JS; afirmar sobre o resultado, **nunca** sobre o texto do relatório do runner
- [X] T010 [P] Implementar `backend/processo_seletivo/sorteios/domain/normalizacao.py` — material bruto da fonte → semente normalizada, pela regra publicada (FR-013)

### Persistência

- [X] T011 Escrever os modelos em `backend/processo_seletivo/sorteios/models.py` — `RelacaoDeHabilitados` (com `marco_id` e `metodo_hash`), `ParticipanteHabilitado`, `OcorrenciaDaFonte` (sem semente normalizada) e `Sorteio` (com `metodo_hash` e `semente_normalizada`, e **sem** FK de método) —, append-only por `save`/`delete`, conforme `data-model.md`. São **quatro**: o método não é entidade, é conteúdo do Edital (D-013, D-016)
- [X] T012 Gerar a migration inicial de `sorteios` com todas as constraints do `data-model.md`, inclusive `ck_relacao_nao_vazia` (FR-009), `uq_numero_por_relacao` (FR-003), `uq_ocorrencia_por_fonte`, `uq_sorteio_raiz` em `(relacao, ocorrencia)` (FR-031) e as **duas** constraints parciais de relação raiz — `uq_relacao_raiz_por_marco` e `uq_relacao_raiz_por_marco_e_lista` (FR-070, D-014)
- [X] T078 [P] Escrever `backend/tests/integration/sorteios/test_relacao_raiz_unica.py` — duas relações raiz de ampla concorrência no mesmo recorte são recusadas **pelo banco**, três de listas distintas são aceitas, e a cadeia de sucessão continua admitindo quantas sucessões o certame precisar (FR-070)
- [X] T013 Acrescentar as tabelas novas às triggers de imutabilidade e à política de privilégios em `backend/processo_seletivo/seguranca/papeis.py`, com migration própria (FR-007)
- [X] T014 Estender `backend/tests/integration/test_database_permissions.py` para provar que a role de runtime não recebe `UPDATE` nem `DELETE` nas tabelas novas

### A constraint que muda

- [X] T015 Acrescentar `origem` (default `COMPUTADO`) e `lista_id` a `AtoDeOrdenacao` em `backend/processo_seletivo/classificacao/models.py`, e substituir `uq_ato_raiz_por_marco` pelas **duas** constraints parciais do `data-model.md` (D-006, FR-034, FR-035, FR-036)
- [X] T016 Gerar a migration correspondente em `backend/processo_seletivo/classificacao/migrations/`
- [X] T079 Declarar, em `backend/processo_seletivo/classificacao/models.py`, o que `universo` recebe num ato de sorteio — `{"origem": "SORTEIO", "sorteioId", "relacaoId", "relationHash", "quantidade"}` —, com a razão escrita: `{}` passaria pela leitura sem denunciar nada e quebraria na comparação, e a forma de ato computado mentiria sobre a origem (FR-069)
- [X] T017 Escrever `backend/tests/integration/classificacao/test_ato_por_lista.py` provando as duas metades: dois atos raiz de **ampla concorrência** para o mesmo marco continuam sendo recusados, e três atos de listas distintas são aceitos (D-006)

### O método, no conteúdo do Edital

**Bloqueia a US1**: sem método declarado no marco, a relação não tem o que citar ao congelar
(FR-066, FR-067). O degrau do método é o **10**, e o do `location` é o 11 — o método é P1 e o local é
P3, e a árvore de degraus precisa ficar contígua em qualquer estado entregável (D-013).

- [X] T080 Publicar `drawMethod` no conteúdo canônico, em `backend/processo_seletivo/publicacoes/application/publish_edital.py`, como objeto do marco de classificação — `algorithm`, `source`, `occurrence`, `derivation`, `normalization`, `substitutionRule` —, e elevar `SCHEMA_VERSION` de 9 para 10 em `backend/processo_seletivo/shared/canonical.py` (FR-013, FR-014)
- [X] T081 Acrescentar o degrau 10 a `DEGRAUS_DE_MARCO` em `backend/processo_seletivo/publicacoes/domain/elevacao.py` — `{10: {"drawMethod": None}}`, ao lado do `appealWindow` do degrau 8 —, com a nota dizendo que `None` significa "não declarado" e que isso é verdadeiro sobre todo Edital publicado antes (R-009)
- [X] T082 [P] Escrever `backend/tests/contract/test_elevacao_degrau_10.py` — Edital publicado antes do degrau permanece retificável e chega com `drawMethod` nulo; nenhum método é inventado
- [X] T083 [P] Escrever o teste de Retificação de `/profiles/id=…/classificationMilestones/id=…/drawMethod/substitutionRule`, provando que a gramática existente já o alcança **sem** entrada nova em `colecoes.py` — é objeto, e não coleção (FR-014, FR-060)
- [X] T084 Acrescentar o método à composição do marco em `backend/processo_seletivo/interface/`, com os seis campos e nenhum default institucional; e **não** oferecer caminho de alteração do método na gestão do sorteio (FR-013, D-013)
- [X] T085 [P] Escrever `backend/tests/interface/test_metodo_do_marco.py` — a composição declara, a Retificação altera, e a tela do sorteio **exibe sem editar**
- [X] T086 [P] Implementar `backend/processo_seletivo/sorteios/domain/metodo.py` — localizar o `drawMethod` do marco numa `VersaoConsolidada`, calcular o seu resumo canônico e recusar marco sem método (FR-066, FR-067); função de leitura, sem escrita

### A divulgação, que ganha a dimensão da lista

**A D-015, e o que o plano anterior dizia não existir.** Três atos raiz num marco exigem três
publicações, e `uq_publicacao_raiz_por_marco` recusa a segunda.

- [X] T087 Acrescentar `lista_id` a `PublicacaoResultado` em `backend/processo_seletivo/divulgacao/models.py` e partir `uq_publicacao_raiz_por_marco` nas **duas** constraints parciais do `data-model.md`, mantendo a primeira com o nome e a garantia de hoje para a publicação sem lista (FR-068)
- [X] T088 Gerar a migration correspondente em `backend/processo_seletivo/divulgacao/migrations/`
- [X] T089 [P] Escrever `backend/tests/integration/divulgacao/test_publicacao_por_lista.py` provando as duas metades: duas publicações raiz sem lista no mesmo marco continuam sendo recusadas, e três de listas distintas são aceitas (FR-068)
- [X] T090 Despachar a leitura do vigente por lista e a aferição por origem — `ato_vigente` e `estado_do_marco` em `backend/processo_seletivo/classificacao/application/selectors.py`, consumidos por `aferir` em `backend/processo_seletivo/divulgacao/domain/publicabilidade.py`: vendo `universo["origem"] == "SORTEIO"`, a obsolescência é a da **relação** que originou o ato, e não a divergência contra um cálculo por Etapas que nunca o produziu (FR-069, R-014)
- [X] T091 Escrever `backend/tests/integration/divulgacao/test_publicabilidade_de_sorteio.py` — e, no mesmo arquivo, a **regressão que autoriza a alteração**: marco sem lista com ato computado sai com o mesmo desfecho de antes, degrau por degrau (FR-069)

### Autorização

- [ ] T018 Declarar, em `backend/processo_seletivo/seguranca/`, as permissões dos **três** comandos que a R-013 põe sob `comando_de_comissao` — observar ocorrência, publicar relação (que é congelar) e constituir sorteio, sendo a anulação a constituição de um sucessor e não comando à parte —, com a presidência como base suficiente. O quarto comando da R-013, declarar o método, **não** entra aqui: é do Edital, e segue a autorização do ato normativo que o carrega (FR-062, FR-063, R-013)
- [ ] T019 [P] Escrever `backend/tests/integration/sorteios/test_autorizacao.py` com o caminho negativo de cada comando

**Checkpoint**: a chave é reproduzível por duas implementações, os modelos existem e a constraint
nova não enfraqueceu a antiga.

---

## Phase 3: User Story 1 — A comissão publica e congela a relação (Priority: P1) 🎯 MVP

**Goal**: o universo comprometido, publicado, numerado e conferível — antes de existir semente.

**Independent Test**: publicar a relação de um Edital com inscrições submetidas e conferir, no
portal anônimo, os números públicos, o critério e o resumo. Entrega valor sozinha: uma relação
numerada e publicada já é mais do que o certame tem hoje.

- [ ] T020 [P] [US1] Implementar `backend/processo_seletivo/sorteios/domain/projecao.py` — quem entra na relação e a numeração de 1 a N por protocolo crescente (FR-002, FR-003, R-011, R-012)
- [ ] T021 [P] [US1] Escrever `backend/tests/unit/sorteios/test_projecao.py` — inclusão por lista, exclusão de rascunho, numeração determinística e estabilidade entre duas projeções idênticas
- [ ] T022 [US1] Implementar `backend/processo_seletivo/sorteios/application/relacao.py` — publicar (que **é** congelar), gravar o `metodo_hash` do marco lido pela `domain/metodo.py` e recusar marco sem método, calcular o resumo canônico **da projeção pública**, gravar quantidade, ator, instante e recorte, e suceder com motivo (FR-001, FR-006, FR-008, FR-010, FR-012, FR-066, FR-067)
- [ ] T023 [US1] Escrever `backend/tests/integration/sorteios/test_relacao.py` — publicação, imutabilidade, recusa de relação vazia, sucessão com motivo e preservação da anterior (FR-007, FR-009, FR-010)
- [ ] T024 [US1] Registrar a publicação da relação na trilha de auditoria, a partir de `backend/processo_seletivo/sorteios/application/relacao.py`, com ator, ato, estados, motivo e correlação (FR-038, Princípio III)
- [ ] T025 [US1] Criar a tela de gestão em `backend/processo_seletivo/interface/` — estado do recorte, prévia **da relação** e botão de publicar, sem qualquer caminho de edição de participante (FR-002)
- [ ] T026 [US1] Criar a página pública da relação em `backend/processo_seletivo/portal/` — número público, **nome e protocolo** de cada participante, critério de projeção e resumo (FR-005, FR-011)
- [ ] T092 [P] [US1] Escrever `backend/tests/portal/test_resumo_recalculavel.py` — o `canonical_sha256` recalculado **do que a página pública mostra** é bit a bit o resumo publicado, e nenhum campo oculto entra na conta (FR-006, R-015)
- [ ] T027 [P] [US1] Expor a relação e o seu resumo na API pública, em `backend/processo_seletivo/sorteios/api/`
- [ ] T028 [P] [US1] Escrever `backend/tests/interface/test_relacao_de_habilitados.py` — a tela publica, e **não** oferece incluir, excluir ou renumerar
- [ ] T029 [P] [US1] Escrever `backend/tests/portal/test_relacao_publica.py` — a página anônima mostra números e resumo, e não expõe CPF nem identificador interno (FR-005)

**Checkpoint**: US1 entregue e demonstrável ponta a ponta.

---

## Phase 4: User Story 2 — O sorteio acontece uma vez, e produz a ordem (Priority: P1)

**Goal**: o ato que hoje acontece fora do sistema, com semente que não é de ninguém daqui.

**Independent Test**: com relação congelada e ocorrência disponível, executar o sorteio e conferir a
ordem completa, a recusa da segunda execução e a inexistência de campo de semente.

- [ ] T031 [P] [US2] Definir a porta da fonte em `backend/processo_seletivo/sorteios/infrastructure/fontes/__init__.py` e um adaptador de referência, com falso para teste (R-005)
- [ ] T032 [US2] Implementar `backend/processo_seletivo/sorteios/application/ocorrencia.py` — observar a ocorrência e gravar **apenas** o material bruto e o instante, registrar indisponibilidade com evidência e aplicar a regra publicada de substituição. A semente normalizada **não** é gravada aqui: normalizar é regra do método, e a ocorrência é única por `(fonte, referência)` (FR-015, FR-019, D-016)
- [ ] T033 [US2] Implementar `backend/processo_seletivo/sorteios/application/sorteio.py` — comando único, atômico e idempotente que lê a ocorrência **já registrada** (sem ir à rede), resolve o método por `relacao.versao` + `relacao.marco_id`, confere o resumo dele contra `relacao.metodo_hash`, normaliza o material bruto, calcula a ordem e constitui `Sorteio` + `AtoDeOrdenacao` (`origem=SORTEIO`, `universo` na forma da T079) + `PosicaoNaOrdem`, com os valores que o `data-model.md` fixa para cada campo. **Não recebe método como parâmetro** (FR-029, FR-033, FR-034, FR-037, FR-067)
- [ ] T034 [US2] Em `backend/processo_seletivo/sorteios/application/sorteio.py`, recusar a execução quando a ocorrência é anterior ao congelamento (FR-016), quando o resumo da relação mudou depois de a ocorrência ser conhecida (FR-020), quando a relação já tem sucessora (FR-071) e quando o método da versão citada não bate com o `metodo_hash` comprometido (FR-067)
- [ ] T035 [US2] Escrever `backend/tests/integration/sorteios/test_constituicao.py` — ordem cobre todos (FR-025), segunda execução sobre a mesma tupla é recusada (FR-031), e requisições concorrentes produzem um ato (FR-032)
- [ ] T036 [P] [US2] Escrever `backend/tests/integration/sorteios/test_semente.py` — nenhuma rota aceita semente; fonte indisponível aplica a substituição e **não** abre digitação (FR-017, FR-018)
- [ ] T076 [P] [US2] Escrever `backend/tests/integration/sorteios/test_superficies_da_semente.py` — varre todas as rotas e formulários do módulo e prova que **nenhum** aceita semente como entrada, em nenhum verbo (SC-003, FR-017)
- [ ] T037 [US2] Criar a tela do sorteio em `backend/processo_seletivo/interface/` — universo, resumo, método (**lido do Edital, sem campo de edição**) e semente à vista, um botão só, legível em projeção (FR-029, FR-030)
- [ ] T093 [P] [US2] Escrever `backend/tests/integration/sorteios/test_metodo_nao_e_escolha.py` — nenhuma rota, formulário ou parâmetro do módulo aceita método; trocar o método exige Retificação, e relação congelada sob método antigo continua citando o antigo (FR-067, D-014)
- [ ] T038 [P] [US2] Escrever `backend/tests/interface/test_tela_do_sorteio.py` — não há campo de semente, não há simular, não há refazer (FR-030, FR-052)
- [ ] T039 [US2] Registrar na auditoria, a partir de `backend/processo_seletivo/sorteios/application/ocorrencia.py` e `.../sorteio.py`, toda observação de ocorrência — **inclusive a que não vira sorteio** — e a constituição do ato (R-006, Princípio III)

**Checkpoint**: US1 + US2 entregam o sorteio institucional completo, ainda sem verificação de
terceiro.

---

## Phase 5: User Story 3 — Qualquer pessoa reproduz a ordem (Priority: P1)

**Goal**: a prova que sobrevive ao vídeo, e que não depende de falar com o Ifes.

**Independent Test**: baixar o manifesto de um sorteio publicado e reproduzir a ordem com a
implementação JS, fora do sistema.

- [ ] T040 [P] [US3] Implementar `backend/processo_seletivo/sorteios/domain/manifesto.py` — derivação determinística conforme `contracts/manifesto.md`, com `manifestHash` sobre o objeto sem o próprio campo (FR-042, FR-043, R-007)
- [ ] T041 [US3] Gravar `manifesto_hash` no `Sorteio` na constituição, e servir o manifesto regenerado no download (FR-047)
- [ ] T042 [P] [US3] Escrever `backend/tests/unit/sorteios/test_manifesto.py` — dois downloads produzem bytes idênticos, e o manifesto não traz CPF, identificador interno nem dado pessoal indevido (FR-044, SC-007)
- [ ] T043 [US3] Implementar `backend/processo_seletivo/sorteios/application/verificacao.py` — recalcula **das entradas**, jamais das posições publicadas, e relata o que conferiu (FR-039, FR-040, FR-049)
- [ ] T044 [US3] Criar a página "Verificar este sorteio" em `backend/processo_seletivo/portal/`, anônima, com resposta em linguagem de gente (FR-048, FR-051)
- [ ] T045 [P] [US3] Escrever `backend/tests/portal/test_verificacao_de_sorteio.py` — sorteio íntegro passa, manifesto adulterado é detectado e nomeado (FR-050, SC-005)
- [ ] T046 [P] [US3] Escrever `backend/tests/unit/sorteios/test_reproducao_por_sorteio.py` — a reprodução usa relação, semente e método, e ignora as posições gravadas (FR-040, FR-041)
- [ ] T074 [US3] Exibir, no documento publicado do resultado — o renderizador da `017`, em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` —, a identidade do sorteio, o algoritmo e a sua versão, a semente e os resumos de integridade da relação e do manifesto (FR-046)
- [ ] T075 [P] [US3] Escrever o teste do documento publicado em `backend/tests/unit/publicacoes/test_pdf.py`, provando que os cinco dados aparecem e que o documento de um ato **computado** segue sem eles (FR-046)
- [ ] T047 [P] [US3] Publicar o verificador independente em `backend/processo_seletivo/portal/static/portal/sorteio-cli.js`, que lê um manifesto e imprime a ordem, com instrução no `quickstart.md` (SC-001)

**Checkpoint**: as três P1 estão entregues. É o MVP defensável: universo comprometido, ato único e
reprodução por terceiro.

---

## Phase 6: User Story 4 — O certame com cotas produz uma ordem por lista (Priority: P2)

**Goal**: o que 57 e 28 exigem — três relações, três sorteios, três ordens, e o cotista em duas.

**Independent Test**: compor um Edital com AC, PPI e PcD; publicar as três relações; executar os
três sorteios; conferir posições independentes e atos distintos.

- [ ] T048 [US4] Estender `backend/processo_seletivo/sorteios/domain/projecao.py` às listas de reserva — a de ampla concorrência alcança todos, a de reserva alcança quem declarou aquela modalidade (D-006, R-012)
- [ ] T049 [US4] Estender a tela de gestão para listar todos os recortes do Edital e o estado de cada um, em `backend/processo_seletivo/interface/`
- [ ] T050 [US4] Escrever `backend/tests/integration/sorteios/test_listas_de_concorrencia.py` — três atos raiz distintos, o mesmo cotista com posições independentes, numeração própria por relação (FR-004, FR-036)
- [ ] T051 [P] [US4] Escrever `backend/tests/integration/sorteios/test_fronteira_da_ocupacao.py` — nada no sistema responde quem ocupa vaga, quem é suplente ou quem sai de qual lista (FR-064)
- [ ] T052 [P] [US4] Estender a página pública em `backend/processo_seletivo/portal/` para identificar a lista de concorrência de cada ordem publicada (FR-045)
- [ ] T094 [US4] Estender a divulgação da `017` à dimensão da lista — seletor da publicação vigente, cadeia de sucessão e composição do documento, em `backend/processo_seletivo/divulgacao/` —, de modo que cada uma das três ordens do marco tenha o seu ato de divulgação (FR-045, FR-068)
- [ ] T095 [US4] Escrever `backend/tests/integration/divulgacao/test_tres_listas_publicadas.py` — as três ordens do marco são publicadas, cada uma citando o seu ato; suceder a publicação de uma lista **não** arrasta as outras (FR-068)

---

## Phase 7: User Story 5 — Anulado um sorteio, nasce outro (Priority: P2)

**Goal**: impedir que "refazer" exista, sem deixar o certame sem saída.

**Independent Test**: anular um sorteio publicado, constituir o sucessor e conferir que os dois
coexistem.

- [ ] T053 [US5] Implementar a anulação em `backend/processo_seletivo/sorteios/application/sorteio.py` — motivo obrigatório, sucessor citando o anterior, relação e ocorrência novas (FR-053, FR-054)
- [ ] T054 [US5] Criar a tela de anulação em `backend/processo_seletivo/interface/`, com o motivo em campo obrigatório e confirmação nomeando o alvo
- [ ] T055 [US5] Escrever `backend/tests/integration/sorteios/test_anulacao.py` — anulado permanece íntegro e verificável, sucessor exige motivo, e não há caminho de reexecução (FR-052, FR-055)
- [ ] T056 [P] [US5] Estender a página pública em `backend/processo_seletivo/portal/` para exibir a cadeia — sorteio anulado, motivo e sucessor

---

## Phase 8: User Story 6 — O Edital publica onde o evento acontece (Priority: P3)

**Goal**: fechar a L-6 na forma decidida na D-008 — campo único, sem default institucional.

**Independent Test**: compor um evento com local, publicar, conferir no Cronograma publicado e
retificar o campo.

- [ ] T057 [US6] Acrescentar `location` a `EventoCronograma` em `backend/processo_seletivo/editais/models/cronograma.py`, com migration (FR-056, FR-057, FR-058, FR-061)
- [ ] T058 [US6] Publicar `location` no conteúdo canônico em `backend/processo_seletivo/publicacoes/application/publish_edital.py` e elevar `SCHEMA_VERSION` para **11** em `backend/processo_seletivo/shared/canonical.py`, com a nota do degrau
- [ ] T059 [US6] Acrescentar o degrau 10 → **11** em `backend/processo_seletivo/publicacoes/domain/elevacao.py`, com ausência significando "não declarado" (R-009). O 10 é do `drawMethod`, e é P1: a numeração segue a prioridade para que qualquer estado entregável tenha a árvore contígua (D-013)
- [ ] T060 [US6] Escrever `backend/tests/contract/test_elevacao_degrau_11.py` — Edital publicado antes do degrau permanece retificável, e o campo elevado chega vazio
- [ ] T061 [US6] Exibir o local no Cronograma do documento publicado, em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`, e no portal
- [ ] T062 [US6] Acrescentar o campo à composição em `backend/processo_seletivo/interface/`, com sugestão do valor do evento anterior — sugestão que **não** preenche sozinha (FR-059)
- [ ] T063 [P] [US6] Escrever `backend/tests/interface/test_local_do_evento.py` — o campo nasce vazio, a sugestão não grava, e nenhum valor institucional aparece por padrão (FR-058)
- [ ] T064 [P] [US6] Escrever o teste de Retificação de `/schedule/id=…/location`, provando que a gramática existente já o alcança (FR-060)

---

## Phase 9: Polish & Cross-Cutting

- [ ] T065 [P] Acrescentar ao `backend/processo_seletivo/processos/management/commands/seed_demo.py` um certame de sorteio — Edital publicado **com `drawMethod` no marco**, relação publicada citando-o e sorteio constituído — para que o roteiro do `quickstart.md` rode sem montagem manual
- [ ] T066 [P] Estender `backend/tests/integration/test_seed_demo.py` ao certame novo
- [ ] T096 [P] Escrever `backend/tests/unit/sorteios/test_sem_gerador_pseudoaleatorio.py` — varredura arquitetural sobre `sorteios/domain/` e `sorteios/application/` provando que nenhum caminho da ordem importa `random`, `secrets` ou equivalente de runtime, e que nada no módulo importa, embute ou roteia canal de vídeo (FR-026, FR-065)
- [ ] T067 [P] Revisar as citações de requisito em todo o código novo, e rodar `backend/tests/test_citacoes_de_requisito.py` — citação para identificador inexistente é defeito silencioso
- [ ] T068 [P] Conferir acessibilidade e leitura em projeção da tela do sorteio, em `backend/tests/interface/test_acessibilidade.py`
- [ ] T069 [P] Conferir a leitura em 375 px das páginas públicas novas — relação, resultado e verificação —, em `backend/tests/portal/`
- [ ] T070 [P] Medir o caminho completo com 300 participantes e registrar o número no `quickstart.md` (SC-004)
- [ ] T077 Conferir os quatro recortes reais em `specs/021-sorteio-publico-auditavel/quickstart.md` — 77/2026 com uma lista, 76/2026 com uma por polo, 57/2026 e 28/2026 com três por recorte —, registrando para cada um até onde o sistema o conduz e onde ele para (SC-006)
- [ ] T071 Atualizar `README.md` com o módulo `sorteios` na tabela de módulos
- [ ] T072 Rodar `uv run ruff check .`, `uv run ruff format --check .` e `uv run python manage.py makemigrations --check --dry-run` antes de fechar

---

## Dependencies

```text
Setup (T001–T004)
      ↓
Foundational (T005–T019, T073, T078–T091)  ← nenhuma história começa antes
      ↓
US1 (T020–T029, T092)  ───────┐
      ↓                        │
US2 (T031–T039, T076, T093)    │  US6 (T057–T064) é independente das cinco
      ↓                        │  e pode correr a qualquer momento depois do Setup
US3 (T040–T047, T074–T075)  ← MVP fecha
      ↓                        │
US4 (T048–T052, T094–T095)     │
US5 (T053–T056)  ←─────────────┘
      ↓
Polish (T065–T072, T077)
```

- **T080–T086 → US1**: a relação cita o método ao congelar, e não há o que citar antes de o método
  existir no conteúdo do Edital. É a dependência que a D-013 criou, e a razão de o degrau do método
  ser Foundational enquanto o do `location` continua na US6.
- **US1 → US2**: não há o que sortear sem relação congelada.
- **US2 → US3**: não há o que verificar sem ato constituído.
- **T087–T091 → US4**: sem `lista_id` na publicação, as três ordens não se divulgam — a tarefa de
  publicar cada lista existiria sobre um agregado que recusa a segunda.
- **US4 e US5** dependem de US2, e são independentes entre si.
- **US6** só depende do Setup: é do Cronograma, e não do sorteio. O seu degrau é o 11, e o 10 é do
  método — nesta ordem, e não na inversa.

## Parallel Execution Examples

**Fase 2** — quatro frentes ao mesmo tempo, depois de T005:

```text
T006 vetores    ∥  T008 referência JS  ∥  T010 normalização  ∥  T011 modelos
```

**Fase 2, o método e a divulgação** — duas frentes independentes entre si e das quatro acima:

```text
T080→T081→(T082 ∥ T083 ∥ T084→T085)  ∥  T087→T088→(T089 ∥ T090→T091)
```

**US1** — depois de T022:

```text
T027 API pública  ∥  T028 teste de interface  ∥  T029 teste de portal
```

**US3** — depois de T041:

```text
T042 teste do manifesto  ∥  T045 teste da verificação  ∥  T046 teste da reprodução  ∥  T047 verificador CLI  ∥  T075 teste do documento
```

**Polish** — T065 a T070 e T077 são todas paralelas entre si.

## Implementation Strategy

**MVP = US1 + US2 + US3.** As três são P1 porque, juntas, entregam a frase que governa a feature:
universo comprometido antes da semente, ato único, ordem reproduzível por qualquer pessoa. Parar
antes da US3 entrega um sorteador melhor que o atual e sem a prova — que é justamente o que a
feature existe para acrescentar.

**Incremento seguinte**: US4, porque é metade da amostra de sorteio — 57 e 28 não funcionam sem ela.

**Depois**: US5, que é curta e fecha o caminho operacional da nulidade; e US6, que pode entrar a
qualquer momento e não deve atrasar nenhuma das outras.

**O que não entra em nenhuma fase**: ocupação de vagas, convocação, corte e progressão. Se aparecer
tarefa que responda "quem entrou", ela é de outra feature — e a T051 existe para denunciá-la.
