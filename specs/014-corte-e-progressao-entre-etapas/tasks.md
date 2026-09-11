---

description: "Task list for feature implementation"
---

# Tasks: Corte e Progressão entre Etapas

**Input**: Design documents from `specs/014-corte-e-progressao-entre-etapas/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/corte.md](./contracts/corte.md)

**Tests**: **obrigatórios**, e não opcionais. O Princípio V exige teste no nível certo — e nomeia
publicação, elegibilidade, classificação, autorização e concorrência entre os que exigem cobertura
específica. A §9 da spec fecha a feature com a suíte verde e a não regressão do Edital sem regra de
corte verificada. Nenhuma feature anterior abriu exceção; esta não abre.

**Organization**: por user story, para que cada faixa seja demonstrável sozinha.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode correr em paralelo — arquivos distintos, sem dependência pendente
- **[Story]**: a que user story a tarefa pertence (`US1` a `US6`)
- Caminho de arquivo exato em toda tarefa

## Path Conventions

Monólito Django. Código em `backend/processo_seletivo/`, testes em `backend/tests/`, contrato de API
em `specs/001-processo-seletivo-editais/contracts/openapi.yaml`.

**Duas entidades novas, duas migrations, nenhum app novo, nenhuma permissão nova.** Se alguma tarefa
abaixo levar você a criar app, serviço ou permissão, a tarefa foi mal lida.

**Banco próprio nesta worktree**: `DB_NAME=ps_demo_014`. Suítes paralelas disputam
`test_processo_seletivo` e se derrubam.

---

## Phase 1: Setup

**Purpose**: o ambiente da worktree, antes que o primeiro erro estranho custe uma hora.

- [ ] T001 Rodar `uv sync --extra dev` em `backend/`. *Worktree nova tem `.venv` próprio e ele nasce sem o grupo dev: `make test-pg` cria o ambiente, instala o runtime e morre com `Failed to spawn: pytest`. Parece defeito do alvo; é ambiente vazio*
- [ ] T002 Preparar o banco próprio — `LC_ALL=pt_BR.UTF-8 DB_NAME=ps_demo_014 DB_USER=$USER make preparar` em `backend/` — e conferir `manage.py migrate --check`. *`preparar` são **três** passos nesta ordem: provisionar, migrar, provisionar de novo. A segunda passada concede privilégio sobre as tabelas que as migrations criaram, e é ela que dará ao papel de runtime o `INSERT` sem `UPDATE` das duas tabelas desta feature; se disser `0 de N protegidas`, ela não rodou*

**Checkpoint**: a suíte roda nesta worktree sem disputar banco com ninguém.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: a regra tem onde morar, o ato tem onde ser gravado, e o já publicado continua legível.

**⚠️ CRÍTICO**: nenhuma user story começa antes deste checkpoint.

- [ ] T003 Acrescentar `regra_de_corte = models.JSONField(default=dict, blank=True)` a `MarcoClassificatorio`, em `backend/processo_seletivo/editais/models/perfis.py:212`, ao lado de `janela_recursal` e `metodo_de_sorteio`. Docstring registrando **por quê**: vazio significa **não declarada**, e não regra padrão — o marco sem regra não corta, e a Etapa seguinte continua recebendo o que a progressão já entrega (`FR-178`, `FR-214`)
- [ ] T004 Gerar e revisar `backend/processo_seletivo/editais/migrations/0017_regra_de_corte.py`. **Aditiva**: acrescenta uma coluna com default, e não altera nem remove nada
- [ ] T005 Criar `Corte` em `backend/processo_seletivo/classificacao/models.py`, ao lado de `AtoDeOrdenacao`, com os campos de [data-model.md](./data-model.md) §2, `save()` que recusa alteração e `delete()` que levanta. Docstring registrando que **vigente é o corte que ninguém sucedeu** — vigência não é coluna, porque o papel de runtime não tem `UPDATE` nessas tabelas
- [ ] T006 Acrescentar a `Corte` as **quatro** constraints parciais e as **duas** de verificação de [data-model.md](./data-model.md) §2. *As duas de raiz não são redundantes: no PostgreSQL dois `NULL` não colidem, e uma só deixaria passar duas raízes de ampla concorrência no mesmo marco. É a mesma cirurgia de `uq_ato_raiz_por_marco` (`classificacao/models.py:90`), e pela mesma razão (`FR-201`)*
- [ ] T007 Criar `ItemDoCorte` em `backend/processo_seletivo/classificacao/models.py` com os campos de [data-model.md](./data-model.md) §3, `UNIQUE(corte, inscricao)` e os dois índices — inclusive `INDEX(inscricao)`, que é a junção que a prontidão fará. Duas consequências, e só duas: quem não tinha posição entra como `FORA_DA_FAIXA` com `posicao` nula (`FR-194`)
- [ ] T008 Gerar `backend/processo_seletivo/classificacao/migrations/0006_corte.py` com as duas tabelas, as constraints e a **trigger append-only** no padrão que a `015` estabeleceu para `ato_de_ordenacao`. *A trava é dupla e de propósito: trigger **e** privilégio ausente, duas camadas independentes, nenhuma contornável em desenvolvimento (`FR-223`)*
- [ ] T009 [P] Acrescentar `13: {"cutRule": None}` a `DEGRAUS_DE_MARCO` em `backend/processo_seletivo/publicacoes/domain/elevacao.py:107` e subir `SCHEMA_VERSION` de 12 para 13 em `backend/processo_seletivo/shared/canonical.py:116`, com o degrau narrado no comentário. *`None`, e não `{}`: os dois degraus anteriores do mesmo objeto já fixaram `None` para "não declarado", e um dicionário vazio seria uma segunda grafia da mesma ausência (`FR-186`, `R-004`)*
- [ ] T010 [P] Criar `backend/tests/contract/test_elevacao_degrau_13.py`, na convenção estrita de nome: conteúdo na versão 12 sobe para 13 com `cutRule: null` em **todo** marco, e nada mais muda
- [ ] T011 Emitir `cutRule` no dicionário do marco em `backend/processo_seletivo/publicacoes/application/publish_edital.py:151`, ao lado de `appealWindow` e `drawMethod`, com `or None`
- [ ] T012 [P] Ampliar `backend/tests/contract/test_forma_publicada.py`: o marco publicado traz `cutRule`, e traz `null` quando não declarado
- [ ] T013 Rodar `DB_NAME=ps_demo_014 make test-pg` em `backend/` e exigir verde. *Migration desaplicada contamina a sessão inteira, e o sintoma aparece longe da causa*

**Checkpoint**: a regra tem coluna, o ato tem tabela append-only, o degrau 13 lê o já publicado — e **nada mudou de comportamento ainda**.

---

## Phase 3: User Story 1 — Declarar a regra de corte no Edital (Priority: P1) 🎯 MVP

**Goal**: o marco publica como aquele Edital corta — alvo, excedente e desfecho do empate.

**Independent Test**: declarar a regra num Edital em elaboração, publicar, e vê-la no documento, no conteúdo canônico e no catálogo de Retificação, alcançável por identidade — **sem emitir corte nenhum**.

### Tests for User Story 1

- [ ] T014 [P] [US1] Teste de unidade em `backend/tests/unit/editais/test_regra_de_corte.py`: regra com `targetKind` ausente ou desconhecido é recusada; `targetCount` declarado em `FROM_VACANCY_TABLE` é recusado; `targetCount` ausente em `FIXED` é recusado (`FR-179`)
- [ ] T015 [P] [US1] Em `backend/tests/unit/editais/test_regra_de_corte.py`, `targetCount` e `surplusCount` negativos são recusados, e `surplusCount` ausente lê-se `0` — **zero é valor legítimo**, e não ausência (`FR-180`)
- [ ] T016 [P] [US1] Em `backend/tests/unit/editais/test_regra_de_corte.py`, `tieOutcome` ausente **impede a publicação**, com o marco nomeado na mensagem, e **não** é resolvido por padrão em lugar nenhum (`FR-181`, `FR-182`)
- [ ] T017 [P] [US1] Em `backend/tests/unit/editais/test_regra_de_corte.py`, `FROM_VACANCY_TABLE` num recorte sem linha no quadro impede a publicação nomeando o recorte — e linha **zerada** não é linha ausente: aquela publica (`FR-183`)
- [ ] T018 [P] [US1] Em `backend/tests/unit/editais/test_regra_de_corte.py`, dois marcos com regra de corte cujas Etapas terminam na **mesma** Etapa impedem a publicação, nomeando os dois marcos e a Etapa disputada. *É o achado da `R-006`: unir as faixas aplicaria a soma de dois alvos que ninguém publicou, e "o de maior ordem vence" inventaria precedência normativa*
- [ ] T019 [P] [US1] Teste de contrato em `backend/tests/contract/test_edital_draft_api.py`: `cutRule` é aceita no rascunho, é **opcional**, e volta do rascunho campo a campo
- [ ] T020 [P] [US1] Teste de interface em `backend/tests/interface/test_corte.py`: a **Regra de corte** aparece dentro da seção do marco, junto da janela recursal, e não em tela à parte (`UX-024`)
- [ ] T021 [P] [US1] Ampliar `backend/tests/interface/test_round_trip_do_rascunho.py` para comparar `cutRule` **campo a campo** depois de gravar **outra** etapa. *É o teste que existe para pegar "o campo de que ninguém se lembrou", e é a rede que apanha as quatro travessias da `T028`–`T031`*
- [ ] T022 [P] [US1] Ampliar `backend/tests/contract/test_documento_publicado.py`: a regra de corte sai na seção do marco do PDF. A fixture de bytes é **regenerada de propósito**

### Implementation for User Story 1

- [ ] T023 [US1] Escrever a validação do `cutRule` em `backend/processo_seletivo/editais/domain/perfis.py:243`, ao lado de `_validar_metodo_de_sorteio`, com as quatro recusas de [contracts/corte.md](./contracts/corte.md) §1. *A validação mora no domínio, e não só no serializer, pela razão que `perfis.py` já registra: a interface administrativa invoca o command diretamente e não atravessa o serializer*
- [ ] T024 [US1] Acrescentar os **três** achados impeditivos em `backend/processo_seletivo/editais/domain/validation.py`: `cut_rule_sem_desfecho_de_empate`, `cut_rule_sem_linha_de_quadro` e `cut_rule_em_dois_marcos_da_mesma_etapa`. As mensagens nomeiam o marco, o recorte e — no terceiro — os dois marcos e a Etapa (`UX-025`)
- [ ] T025 [US1] Escrever, em `backend/processo_seletivo/classificacao/domain/faixa.py`, o `etapa_governada(marco, etapas)` que responde qual Etapa o marco governa: a que sucede a **última Etapa enumerada**. Reusar `_ultima_etapa` de `backend/processo_seletivo/classificacao/application/calculo.py:189` e o `etapa_anterior`/`etapas_anteriores` de `backend/processo_seletivo/resultados/domain/progressao.py` lidos ao contrário. *É o que a `T018` e a `T024` precisam para descobrir a colisão, e é o que a `US3` vai consumir*
- [ ] T026 [US1] Acrescentar `cutRule` ao `MarcoSerializer` em `backend/processo_seletivo/editais/api/serializers.py:85`, ao lado de `appealWindow`, na forma de [contracts/corte.md](./contracts/corte.md) §1
- [ ] T027 [US1] Acrescentar `cutRule` ao `MarcoInput` e ao `MarcoPublicado` em `specs/001-processo-seletivo-editais/contracts/openapi.yaml`, **nos dois lugares**, anulável
- [ ] T028 [US1] **Travessia 1 de 4** — ler `cutRule` do formulário em `backend/processo_seletivo/interface/forms.py:235`, junto de `_janela_recursal`
- [ ] T029 [US1] **Travessia 2 de 4** — persistir `regra_de_corte` em `replace_draft`, em `backend/processo_seletivo/editais/application/draft.py:314`, junto de `janela_recursal`. *`replace_draft` apaga e recria: o que não for reenviado ao gravar outra etapa **some**, sem erro*
- [ ] T030 [US1] **Travessia 3 de 4** — reexibir a regra em `backend/processo_seletivo/interface/forms.py:836`, junto de `"appealWindow": marco.janela_recursal or None`
- [ ] T031 [US1] **Travessia 4 de 4** — conferir que a reexibição **não sobrescreve o valor bom** pelo da tentativa recusada, e que a recusa ancora no controle certo, com o `id` na profundidade do marco. *Foram dois dos seis defeitos que a `025` só encontrou percorrendo a tela*
- [ ] T032 [US1] Desenhar a **Regra de corte** dentro de `backend/processo_seletivo/interface/templates/interface/_marco.html`, com os quatro controles e rótulos que dizem o que cada um decide — nunca `FIXED`/`STRICT` crus na tela
- [ ] T033 [US1] Acrescentar `cutRule` ao catálogo de Retificação do marco em `backend/processo_seletivo/interface/retificacao.py`, endereçado por identidade — `/profiles/id=…/classificationMilestones/id=…/cutRule/targetCount` —, no padrão que `appealWindow` já usa (`FR-184`)
- [ ] T034 [US1] Escrever a regra na seção do marco do documento em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`, pelo caminho por onde a janela recursal já sai (`FR-185`)
- [ ] T035 [US1] Acrescentar a regra à tela de conferência em `backend/processo_seletivo/interface/revisao.py`, no formato que ela já usa para as demais declarações do marco
- [ ] T036 [US1] Conferir `backend/tests/interface/test_medida_dos_campos.py` e `backend/tests/interface/test_acessibilidade.py` para os controles novos: toda classe citada existe na folha, todo `aria-describedby` aponta alvo existente

**Checkpoint**: `US1` fechada. O Edital publica como corta, a Retificação alcança cada campo por identidade, e **nenhum corte foi emitido**.

---

## Phase 4: User Story 2 — Emitir o corte de um marco (Priority: P1)

**Goal**: a ordem vigente vira um ato de corte imutável que diz quem progride.

**Independent Test**: com ordem vigente e regra publicada, calcular e emitir; o ato é imutável, enumera todos os considerados e reproduz a mesma faixa a partir do universo declarado.

### Tests for User Story 2

- [ ] T037 [P] [US2] Teste de unidade em `backend/tests/unit/classificacao/test_faixa.py`: o alvo **conta pessoas, e não números de posição**. Com empate em `1, 1, 3`, alvo dez termina na posição **nove** com dez pessoas dentro. *`desempate.py:18-20` já registra a convenção e já a explica por causa desta feature; contar por número de posição entregaria nove pessoas*
- [ ] T038 [P] [US2] Em `backend/tests/unit/classificacao/test_faixa.py`, o alvo apurado sai da regra: `FIXED` lê o número publicado; `FROM_VACANCY_TABLE` lê a linha do quadro do recorte — a da Modalidade quando há `lista_id`, a **geral** quando ele é nulo (`FR-189`, `R-009`)
- [ ] T039 [P] [US2] Em `backend/tests/unit/classificacao/test_faixa.py`, empate residual atravessando a última posição **da faixa emitida** — alvo mais excedente, e não a do alvo — sob `STRICT` recusa nomeando as posições; sob `ADMITS_SURPLUS` estende e registra quantos entraram além do alvo (`FR-195`, `FR-196`)
- [ ] T040 [P] [US2] Em `backend/tests/unit/classificacao/test_faixa.py`, empate **longe** do corte não impede nada, e empate **desfeito por critério publicado** não chega à comparação — as posições já saíram distintas
- [ ] T041 [P] [US2] Em `backend/tests/unit/classificacao/test_faixa.py`, ordem com **menos** participantes que o alvo: todos progridem, e o ato registra que o alvo não foi alcançado. Alvo derivado **zero**: ninguém progride, e o ato o diz
- [ ] T042 [P] [US2] Em `backend/tests/unit/classificacao/test_faixa.py`, participante **sem posição** na ordem nunca entra na faixa, qualquer que seja o alvo (`FR-191`)
- [ ] T043 [P] [US2] Teste de unidade em `backend/tests/unit/classificacao/test_corte_append_only.py`: `save()` de linha existente levanta, `delete()` levanta, e a trigger recusa `UPDATE` e `DELETE` vindos do banco (`FR-192`, `FR-223`)
- [ ] T044 [P] [US2] Teste de integração em `backend/tests/integration/classificacao/test_emissao_do_corte.py`: emitida a faixa, **todos** os participantes considerados constam — os que progrediram e os que ficaram fora, cada um com posição e causa legível (`FR-194`)
- [ ] T045 [P] [US2] Em `backend/tests/integration/classificacao/test_emissao_do_corte.py`, emitir sem ordem vigente recusa; emitir sobre ato de ordenação **obsoleto** recusa dizendo a causa da obsolescência (`FR-197`, `FR-198`)
- [ ] T046 [P] [US2] Em `backend/tests/integration/classificacao/test_emissao_do_corte.py`, duas emissões simultâneas no mesmo recorte produzem **uma** cadeia; a segunda volta como conflito (`FR-201`)
- [ ] T047 [P] [US2] Em `backend/tests/integration/classificacao/test_emissao_do_corte.py`, sucessão exige motivo, o sucedido permanece legível e um corte tem **no máximo um** sucessor (`FR-200`)
- [ ] T048 [P] [US2] Em `backend/tests/integration/classificacao/test_emissao_do_corte.py`, a repetição com a mesma chave de idempotência devolve o desfecho anterior, e **não** um segundo ato (`R-015`)
- [ ] T049 [P] [US2] Teste de interface em `backend/tests/interface/test_corte.py`: abrir a tela **não grava nada** — nenhum `Corte`, nenhum `ItemDoCorte` (`FR-190`)
- [ ] T050 [P] [US2] Em `backend/tests/interface/test_corte.py`, a tela apresenta alvo declarado, alvo apurado **e sua origem**, excedente, quantos progridem, quantos ficam fora e a última posição alcançada (`UX-024`); e a emissão pede confirmação declarando que o ato é imutável (`UX-028`)
- [ ] T051 [P] [US2] Em `backend/tests/interface/test_corte.py`, ler o corte **não** autoriza emiti-lo, e identificador conhecido não alcança Edital fora do escopo do ator (`FR-221`)

### Implementation for User Story 2

- [ ] T052 [US2] Escrever `calcular_corte` em `backend/processo_seletivo/classificacao/application/corte.py`: lê o ato vigente do recorte, apura o alvo, forma a faixa e devolve a proposta com o resumo do universo. **Não reordena, não recalcula pontuação e não aplica desempate novo** — lê `PosicaoNaOrdem` como ela foi emitida (`FR-187`, `FR-188`)
- [ ] T053 [US2] Escrever, em `backend/processo_seletivo/classificacao/domain/faixa.py`, o alvo apurado, a fronteira da faixa e a detecção do empate que a atravessa. Puro, sem tocar em banco de norma
- [ ] T054 [US2] Escrever `emitir_corte` em `backend/processo_seletivo/classificacao/application/emissao_do_corte.py`, pelo mesmo `comando_de_comissao` de `emitir_ordem` (`classificacao/application/emissao.py:20`): idempotência por chave, desfecho anterior na repetição, autorização por `classificacao:emitir` e auditoria por `auditar`. **Sem permissão nova** (`FR-220`, `FR-222`)
- [ ] T055 [US2] Gravar o universo declarado de [data-model.md](./data-model.md) §4 — inclusive o `rowId` da linha do quadro em alvo derivado. *Sem ele, retificado o quadro, não há como dizer se **aquele** corte ficou para trás: a quantidade sozinha não identifica a linha (`FR-193`, `R-009`)*
- [ ] T056 [US2] Acrescentar as quatro rotas de [contracts/corte.md](./contracts/corte.md) §2 em `backend/processo_seletivo/interface/urls.py:205`, pendendo do marco como as da ordem e as do sorteio, e as views em `backend/processo_seletivo/interface/views.py`
- [ ] T057 [US2] Criar `backend/processo_seletivo/interface/templates/interface/corte.html` e `_linha_do_corte.html`, com a confirmação de consequências inequívocas antes de emitir (`UX-028`)
- [ ] T058 [US2] Apresentar o estado do corte de **todos os recortes** do marco numa visão só, sem exigir uma visita por recorte (`UX-029`)

**Checkpoint**: `US2` fechada. A ordem vira ato de corte, o empate na fronteira tem desfecho declarado, e a Etapa seguinte **ainda não mudou**.

---

## Phase 5: User Story 3 — Conduzir a Etapa seguinte só com quem progrediu (Priority: P1)

**Goal**: a Etapa seguinte recebe a faixa, e quem ficou fora aparece nomeado.

**Independent Test**: emitir um corte e verificar que a distribuição, a Mesa, a prontidão e a navegação "próxima pendente" alcançam exatamente quem progrediu.

### Tests for User Story 3

- [ ] T059 [P] [US3] Teste de integração em `backend/tests/integration/resultados/test_progressao_com_corte.py`: com corte vigente, participam da Etapa governada apenas as inscrições alcançadas por **alguma faixa vigente** do marco (`FR-208`)
- [ ] T060 [P] [US3] Em `backend/tests/integration/resultados/test_progressao_com_corte.py`, a condição **soma** e não revoga: eliminada em Etapa anterior continua fora **ainda que dentro da faixa** (`FR-209`)
- [ ] T061 [P] [US3] Em `backend/tests/integration/resultados/test_progressao_com_corte.py`, inscrição fora da faixa não é distribuída, não é avaliada, não conta como pendente e não é entregue pela "próxima pendente" — e **aparece nomeada** como fora do corte, com posição e faixa (`FR-210`, `UX-026`)
- [ ] T062 [P] [US3] Em `backend/tests/integration/resultados/test_progressao_com_corte.py`, Atribuição criada **antes** do corte é preservada, não autoriza trabalho, e volta a autorizar se uma faixa seguinte alcançar a inscrição (`FR-211`)
- [ ] T063 [P] [US3] Em `backend/tests/integration/resultados/test_progressao_com_corte.py`, o corte **não grava, não altera e não apaga** `ResultadoEtapa` nenhum (`FR-212`)
- [ ] T064 [P] [US3] **A não regressão**, em `backend/tests/integration/resultados/test_progressao_com_corte.py`: marco sem regra, e marco com regra e **sem corte emitido**, preservam exatamente o conjunto de hoje (`FR-214`, `SC-069`)
- [ ] T065 [P] [US3] **O orçamento de consulta**: as listagens da Etapa fazem o mesmo número de consultas que faziam antes desta feature. Ampliar os testes que já contam consultas, e não criar um paralelo (`FR-213`, `SC-068`)

### Implementation for User Story 3

- [ ] T066 [US3] Somar a condição do corte em `restringir_a_participantes`, em `backend/processo_seletivo/resultados/application/prontidao.py:127`, como **um** `Exists` correlacionado dentro da consulta que já ia acontecer — e **não** materializando ids num `__in`, que custaria duas leituras de população por listagem e é o erro que o próprio módulo já documenta ter recusado
- [ ] T067 [US3] Somar a mesma condição em `participa_da_etapa` (`prontidao.py:179`) e o estado *fora do corte* em `panorama_da_etapa` (`prontidao.py:204`), mantendo a **partição**: cada participante ocupa um estado e a soma fecha com o total
- [ ] T068 [US3] Resolver os cortes vigentes do marco governante **uma vez por listagem**, junto de `_anteriores_e_gate` (`prontidao.py:108`), que já lê o conteúdo publicado uma vez (`FR-213`)
- [ ] T069 [US3] Escrever, no topo de `backend/processo_seletivo/resultados/application/prontidao.py`, o comentário que mantém o ciclo fechado: este módulo importa `classificacao.models`, e **nunca** `classificacao.application.*`, porque `classificacao/application/calculo.py:14` já importa este arquivo. *O primeiro import desses fecha o ciclo, e o erro aparece na primeira importação de qualquer um dos dois, num arquivo sorteado, longe da causa (`R-005`)*
- [ ] T070 [US3] Desenhar a linha *fora do corte* nas superfícies da Etapa, a partir do estado que a prontidão devolve — mais um valor na partição, e **não** uma coluna nova na listagem (`UX-026`)

**Checkpoint**: `US3` fechada. O 14/2026 vai da ordem à entrevista com dez pessoas, e as três que ficaram fora sabem por quê.

---

## Phase 6: User Story 4 — Emitir a faixa seguinte (Priority: P2)

**Goal**: a faixa seguinte começa onde a anterior parou, sem revogá-la.

**Independent Test**: emitir uma faixa, depois uma segunda com motivo declarado, e verificar que as duas coexistem, que a segunda começa na posição certa e que ninguém é alcançado duas vezes.

### Tests for User Story 4

- [ ] T071 [P] [US4] Teste de integração em `backend/tests/integration/classificacao/test_faixa_seguinte.py`: a continuação começa depois da última posição alcançada, **as duas ficam vigentes**, e nenhuma inscrição é alcançada duas vezes (`FR-202`, `SC-064`)
- [ ] T072 [P] [US4] Em `backend/tests/integration/classificacao/test_faixa_seguinte.py`, **continuação não é sucessão**: a faixa anterior não ganha sucessor, e o estado do marco mostra as duas. *Trocar uma pela outra produz um sistema que parece funcionar e deixa alguém fora de uma Etapa em que deveria estar*
- [ ] T073 [P] [US4] Em `backend/tests/integration/classificacao/test_faixa_seguinte.py`, continuação sem motivo recusa; que ultrapasse alvo + excedente recusa dizendo qual limite; sobre ordem sucedida recusa (`FR-203`, `FR-204`, `FR-205`)
- [ ] T074 [P] [US4] Em `backend/tests/integration/classificacao/test_faixa_seguinte.py`, **o sistema nunca continua sozinho**: nenhum cenário exercitado produz faixa seguinte sem ato humano (`FR-206`, `SC-065`)
- [ ] T075 [P] [US4] Teste de varredura em `backend/tests/interface/test_corte.py`: nenhuma tela, mensagem, ato ou documento desta feature contém *vaga ocupada*, *vaga preenchida* ou *déficit* (`FR-207`, `SC-066`). *É assim que a fronteira com a `016` deixa de ser promessa de prosa*

### Implementation for User Story 4

- [ ] T076 [US4] Escrever `continuar_corte` em `backend/processo_seletivo/classificacao/application/emissao_do_corte.py`: motivo obrigatório, quantidade **pedida e conferida** contra alvo + excedente publicados, e recusa quando a ordem da faixa anterior não é mais a vigente. *A quantidade nunca é inferida: o sistema não sabe quantas vagas foram ocupadas, e a `D-002` da spec diz de quem é essa conta*
- [ ] T077 [US4] Acrescentar a rota `corte/continuar` e o formulário de continuação, com o motivo em campo obrigatório e a quantidade pretendida (`UX-025`)

**Checkpoint**: `US4` fechada. O ciclo do 77, do 57 e do 28 é conduzível **antes** de a `016` existir.

---

## Phase 7: User Story 5 — Enxergar que o corte ficou para trás (Priority: P2)

**Goal**: as quatro causas de obsolescência, nomeadas, sem alterar o vigente.

**Independent Test**: emitir um corte, suceder a ordem, e ver a obsolescência com a causa certa enquanto o corte vigente permanece o mesmo.

### Tests for User Story 5

- [ ] T078 [P] [US5] Teste de integração em `backend/tests/integration/classificacao/test_corte_obsoleto.py`: as **quatro** causas — ordem sucedida, regra alterada, quadro alterado e participante reingressou — aparecem **nomeadas**, e nunca como divergência genérica (`FR-215`, `FR-216`)
- [ ] T079 [P] [US5] Em `backend/tests/integration/classificacao/test_corte_obsoleto.py`, a obsolescência **não altera, não substitui e não revoga** o corte vigente (`FR-217`, `SC-062`)
- [ ] T080 [P] [US5] Em `backend/tests/integration/classificacao/test_corte_obsoleto.py`, deferimento que devolve alguém ao universo produz a causa *participante reingressou* (`FR-218`)
- [ ] T081 [P] [US5] Em `backend/tests/integration/classificacao/test_corte_obsoleto.py`, corte obsoleto **impede** publicar resultado que dele dependa, com motivo nomeado e o caminho a seguir (`FR-219`, `SC-063`)
- [ ] T082 [P] [US5] Em `backend/tests/integration/classificacao/test_corte_obsoleto.py`, Retificação que **remove** a regra de um marco com corte emitido: o ato permanece legível, a causa é *regra alterada*, e a Etapa seguinte volta a admitir todos os habilitados

### Implementation for User Story 5

- [ ] T083 [US5] Acrescentar o estado do corte ao `estado_do_marco` em `backend/processo_seletivo/classificacao/application/selectors.py:281`, com as quatro comparações de [research.md](./research.md) `R-011`. As três primeiras não custam consulta nova; a quarta reusa `_reingressos` (`selectors.py:488`), que a `018` já escreveu
- [ ] T084 [US5] Acrescentar o impedimento de corte obsoleto em `backend/processo_seletivo/divulgacao/domain/publicabilidade.py`, ao lado do que já existe para ato de ordenação obsoleto (`FR-219`)
- [ ] T085 [US5] Mostrar a obsolescência e a causa **ao abrir o marco**, sem que ninguém precise comparar nada manualmente (`UX-027`)

**Checkpoint**: `US5` fechada. Nenhum corte decide em silêncio quem está no certame.

---

## Phase 8: User Story 6 — Auditar e reproduzir (Priority: P3)

**Goal**: a prova que sustenta o ato mais contestável do certame.

**Independent Test**: a partir do universo declarado, recalcular e obter exatamente a mesma faixa, com a mesma última posição alcançada.

### Tests for User Story 6

- [ ] T086 [P] [US6] Teste de integração em `backend/tests/integration/classificacao/test_reproducao_do_corte.py`: o universo declarado reproduz faixa idêntica (`FR-199`, `SC-061`)
- [ ] T087 [P] [US6] Em `backend/tests/integration/classificacao/test_reproducao_do_corte.py`, corte antigo é lido com os **nomes da versão que congelou**, e não com os de hoje, mesmo depois de Retificação que renomeie a modalidade. Reusar `nomes_do_marco` (`classificacao/domain/nomes.py`)
- [ ] T088 [P] [US6] Em `backend/tests/integration/classificacao/test_reproducao_do_corte.py`, a continuação cita a faixa anterior e o motivo declarado
- [ ] T089 [P] [US6] Em `backend/tests/integration/classificacao/test_reproducao_do_corte.py`, a auditoria da emissão traz ator, ação, recorte, ordem citada, alvo apurado, quantidade alcançada e instante, recuperável sem acesso ao banco (`FR-222`, `SC-070`)

### Implementation for User Story 6

- [ ] T090 [US6] Escrever a reprodução em `backend/processo_seletivo/classificacao/application/corte.py`, a partir do universo declarado — e **não** do estado de hoje
- [ ] T091 [US6] Desenhar a leitura do corte histórico na rota `cortes/<corte_id>`, sucedido ou vigente, com a proveniência inteira (`UX-024`)

**Checkpoint**: todas as user stories fechadas e independentemente demonstráveis.

---

## Phase 9: Polish & Cross-Cutting Concerns

- [ ] T092 [P] Regenerar a fixture de bytes de `backend/tests/contract/test_documento_publicado.py`, **de propósito**, e registrar no commit que a regra de corte entrou no PDF
- [ ] T093 [P] Conferir o teto de abertura: 1.000 participantes por recorte em até 3 segundos, e número de consultas que **não cresce** com a população (`SC-067`)
- [ ] T094 [P] Percorrer o [quickstart.md](./quickstart.md) inteiro contra o servidor real, pela interface, e registrar o relatório em `doc/e2e/014-corte-e-progressao/relatorio.md`, com os achados numerados `E2E14-NNN` e **cada um citado na docstring do teste que o fecha**
- [ ] T095 Rodar `DB_NAME=ps_demo_014 make lint check test-pg` em `backend/` e exigir verde. *`lint` são **dois** passos — `ruff check` **e** `ruff format --check`; rodar só o primeiro declara verde local e quebra no CI*
- [ ] T096 Escrever `specs/014-corte-e-progressao-entre-etapas/rastreabilidade.md` cobrindo `FR-178` a `FR-223`, `SC-055` a `SC-070` e `UX-024` a `UX-029`. *Onde existe matriz, `tests/test_citacoes_de_requisito.py` exige que ela alcance **cada** requisito — linha perdida é invisível de outro jeito*

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Fase 1)**: sem dependência
- **Foundational (Fase 2)**: depende da Fase 1 — **bloqueia todas as user stories**
- **US1 (Fase 3)**: depende da Fase 2. É a única que mexe em conteúdo publicado
- **US2 (Fase 4)**: depende da `US1` — não há o que emitir sem regra publicada
- **US3 (Fase 5)**: depende da `US2` — não há faixa sem corte emitido
- **US4 (Fase 6)**: depende da `US2`; **independente** da `US3`
- **US5 (Fase 7)**: depende da `US2`; **independente** da `US3` e da `US4`
- **US6 (Fase 8)**: depende da `US2`
- **Polish (Fase 9)**: depende de todas

### A ordem que a spec sugere, e por quê

`US1 → US2 → US3` é a espinha, e ela entrega o 14/2026 inteiro até a entrevista. A `US4` é o que
fecha o ciclo do 77, do 57 e do 28 antes de a `016` existir. A `US5` e a `US6` são o que impedem o
corte de decidir em silêncio — e nenhuma das duas pode ser adiada para "depois", porque as duas
protegem o ato que já estará produzindo efeito desde a `US3`.

### Fases que são atômicas por dentro

- **Fase 2** — o degrau, o `SCHEMA_VERSION` e a emissão no snapshot caem **juntos**. Um
  `SCHEMA_VERSION` 13 sem degrau torna irrelegível todo conteúdo na 12.
- **T028–T031** — as quatro travessias do rascunho. Fechar três deixa o defeito vivo: o campo some
  ao gravar outra etapa, e ninguém vê erro.
- **T066–T068** — as três portas da prontidão. Deixar uma de fora abre a porta que a `013` fechou,
  e a pior delas é a "próxima pendente", que entrega a inscrição sem que ninguém peça por ela.

### Parallel Opportunities

Todos os testes marcados `[P]` de uma mesma user story correm juntos. `T009`/`T010` e `T011`/`T012`
correm em paralelo entre si dentro da Fase 2. As fases 6, 7 e 8 são independentes entre si depois da
`US2`, e podem ser distribuídas.

---

## Parallel Example: User Story 2

```bash
# Os testes de faixa, todos em arquivos distintos de implementação:
Task: "T037 o alvo conta pessoas, em tests/unit/classificacao/test_faixa.py"
Task: "T043 append-only, em tests/unit/classificacao/test_corte_append_only.py"
Task: "T044 todos os considerados constam, em tests/integration/classificacao/test_emissao_do_corte.py"
Task: "T049 abrir a tela não grava, em tests/interface/test_corte.py"
```

---

## Implementation Strategy

### MVP (`US1` + `US2` + `US3`)

1. Fases 1 e 2 — ambiente, entidades e degrau
2. Fase 3 — a regra publicada
3. Fase 4 — o corte emitido
4. Fase 5 — o efeito na Etapa seguinte
5. **PARE e VALIDE**: o 14/2026 vai da ordem à entrevista, pela interface, sem planilha

### Entrega incremental

Cada fase de user story é um incremento demonstrável, e a ordem acima é a ordem de valor. A `US4`
sozinha já muda o que é possível: o 77/2026 passa a ser conduzível inteiro.

### Sobre trabalhar em paralelo

Depois da `US2`, as fases 6, 7 e 8 não se tocam — arquivos distintos, testes distintos. A `US3` é a
que atravessa código de outra feature, e é a única que precisa de atenção a orçamento de consulta.

---

## Notes

- `[P]` = arquivos distintos, sem dependência pendente
- Commit a cada tarefa ou grupo lógico, e pare em cada checkpoint para validar a story sozinha
- **O teste de citações lê `specs/`**: escreveu tarefa nova citando `FR-`, `SC-`, `UX-` ou `D-`? Rode
  a suíte antes de empurrar
- Nenhuma tarefa desta lista cria app, permissão ou módulo novo. Se alguma levar a isso, ela foi mal
  lida — e o lugar de resolver é o [plan.md](./plan.md), não o código
