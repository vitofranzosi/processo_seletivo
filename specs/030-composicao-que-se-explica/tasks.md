---
description: "Task list for 030 — a composição que se explica"
---

# Tasks: A composição que se explica

**Input**: Design documents from `/specs/030-composicao-que-se-explica/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/)

**Tests**: obrigatórios, e não opcionais. O princípio V da Constituição exige cobertura específica
para publicação, retificação e classificação — os três estão nesta feature. As tarefas de teste
vêm antes da implementação que verificam.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivo diferente, sem dependência pendente)
- **[Story]**: US1, US2 ou US3, conforme a história da spec

## Path Conventions

Monólito Django. Código em `backend/processo_seletivo/`, testes em `backend/tests/`.

**A suíte é organizada por espécie de teste, e o app é subpasta dela** — `tests/unit/editais/`,
`tests/integration/editais/`, `tests/integration/sorteios/`, `tests/interface/`. Não existe
`tests/editais/` nem `tests/sorteios/`: escrever ali criaria um diretório paralelo ao que já há.

**`Edital` mora em `processos/models.py`**, e não em `editais/`. O app `editais` guarda o conteúdo do
Edital — perfis, etapas, seções, cronograma —, não o Edital.

---

## Phase 1: Setup

**Purpose**: a worktree precisa rodar a suíte contra PostgreSQL antes de qualquer coisa

- [ ] T001 Instalar as dependências de desenvolvimento da worktree com `uv sync --extra dev` em `backend/` (worktree nova não tem `pytest`, e `make test-pg` falha com "Failed to spawn: pytest")
- [ ] T002 Criar `backend/.env` a partir de `backend/.env.example` e definir um `DB_NAME` próprio desta worktree (suítes paralelas disputam `test_processo_seletivo` e se derrubam; sem `.env`, `make check` quebra com "permission denied for table django_migrations")
- [ ] T003 Confirmar a linha de base com `cd backend && make lint check test-pg` e registrar a contagem de partida (esperado: 5402 passando, 2 pulados)

**Checkpoint**: suíte verde contra PostgreSQL. Qualquer falha aqui é ambiente, não o diff.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: o campo que carrega a forma da ordem, e o contrato de preservação do rascunho

**⚠️ Bloqueia US1 e US3.** **US2 não depende desta fase** — é microcópia em telas que já existem, e
pode começar em paralelo com a Phase 1.

### Testes que fixam a fronteira (antes da implementação)

- [ ] T004 [P] Teste de que Edital publicado antes da feature mantém o conteúdo canônico idêntico, sem `orderProduction`, em `backend/tests/unit/editais/test_forma_da_ordem.py` — ao lado de `test_marco_classificatorio.py` e `test_forma_do_snapshot.py` (SC-142)
- [ ] T005 [P] Teste de round-trip do rascunho: campo declarado e depois tornado impertinente volta no envio seguinte e não se perde, em `backend/tests/interface/test_round_trip_do_rascunho.py` (FR-418)
- [ ] T006 [P] Teste de fronteira: o valor preservado em campo oculto **não** alcança o conteúdo publicado, em `backend/tests/unit/editais/test_forma_da_ordem.py` (contrato do rascunho)

### Implementação

- [ ] T007 Acrescentar `FormaDaOrdem` e o campo `forma_da_ordem` a `MarcoClassificatorio` em `backend/processo_seletivo/editais/models/perfis.py`, com `blank=True` e default `""` (ausência é o estado legítimo do marco já publicado)
- [ ] T008 Gerar a migration do campo em `backend/processo_seletivo/editais/migrations/0021_forma_da_ordem.py`, sem percorrer linha publicada e sem escrever em tabela append-only
- [ ] T009 Ler e gravar `orderProduction` no round-trip do rascunho em `backend/processo_seletivo/editais/application/draft.py`, preservando a semântica de `{}`/`""` como "não declarado"
- [ ] T010 Publicar `orderProduction` no conteúdo canônico em `backend/processo_seletivo/editais/api/serializers.py`, **omitindo a chave** quando o campo for `""`
- [ ] T011 Acrescentar `("classificationMilestones", "orderProduction"): retificavel()` ao catálogo em `backend/processo_seletivo/editais/domain/mutabilidade.py`
- [ ] T012 Rodar a segunda passada de `manage.py provisionar_papeis` (definido em `backend/processo_seletivo/seguranca/management/commands/provisionar_papeis.py`) e conferir o `N de M` — o primeiro número vindo `0` significa que a passada pós-migration não rodou

**Checkpoint**: o marco sabe dizer como sua ordem é produzida, e o rascunho não perde o que esconde.

---

## Phase 3: User Story 1 — Compor o marco do Edital simples (Priority: P1) 🎯 MVP

**Goal**: o marco do Edital canônico exige menos de 10 perguntas, contra os 28 controles de hoje.

**Independent Test**: montar o Edital canônico — um Perfil, três vagas, uma Etapa classificatória,
sem Modalidade — até o fim da etapa de Classificação, sem abrir o disclosure de ajuda, contando os
controles apresentados.

### Testes

- [ ] T013 [P] [US1] Teste de contagem de controles do marco no Edital canônico, com o método de contagem do quickstart, em `backend/tests/interface/test_compor_classificacao.py` (SC-138)
- [ ] T014 [P] [US1] Teste de que a pergunta de entrada vem antes de qualquer campo do marco, em `backend/tests/interface/test_compor_classificacao.py` (FR-413)
- [ ] T015 [P] [US1] Teste de que combinação e normalização somem com uma Etapa e reaparecem com duas, sem invalidar o que o marco já publicava, **mais as duas contraprovas da FR-432** — marco `POR_SORTEIO` sem Etapa é aceito, marco `POR_PONTUACAO` sem Etapa continua recusado —, em `backend/tests/interface/test_campos_que_a_escolha_governa.py` (FR-415, FR-416, FR-432)
- [ ] T016 [P] [US1] Teste de que as perguntas de ampla concorrência e reversão só aparecem depois de o Perfil declarar uma Modalidade, em `backend/tests/interface/test_compor_quadro.py` (FR-417)
- [ ] T017 [P] [US1] Teste de que nenhum campo `required` é renderizado fora da tela, em `backend/tests/interface/test_acessibilidade_da_classificacao.py`
- [ ] T018 [P] [US1] Teste de que padrão e derivação não alcançam Edital existente, inclusive em Retificação, em `backend/tests/integration/editais/test_derivacao_nao_alcanca_o_declarado.py` — ao lado de `test_derivacao_persistida.py`, que afirma o caso oposto (FR-421)

### Implementação

- [ ] T019 [US1] Renderizar a pergunta de entrada da forma da ordem no topo do cartão em `backend/processo_seletivo/interface/templates/interface/_marco.html`, antes de qualquer campo do marco (FR-413)
- [ ] T020 [US1] Condicionar o bloco do método de sorteio à resposta `POR_SORTEIO` em `backend/processo_seletivo/interface/templates/interface/_marco.html`, removendo os campos do formulário em vez de escondê-los por CSS (FR-414)
- [ ] T021 [US1] Condicionar combinação e normalização a duas ou mais Etapas em `backend/processo_seletivo/interface/templates/interface/_marco.html`, e declarar ali, em texto visível, que com uma Etapa a pontuação combinada é a dela (FR-415, FR-416)
- [ ] T022 [US1] Emitir os campos impertinentes como `<input type="hidden">` com o último valor declarado em `backend/processo_seletivo/interface/templates/interface/_marco.html`, nunca como `disabled`, conforme [contracts/payload-do-rascunho.md](contracts/payload-do-rascunho.md) (FR-418)
- [ ] T023 [US1] Remover o `required` junto com cada campo que sai da tela, e transferir a cobrança para a validação da publicação em `backend/processo_seletivo/editais/domain/validation.py` — **e, no mesmo lugar, condicionar a exigência de Etapa à forma da ordem**: obrigatória em `POR_PONTUACAO`, dispensada em `POR_SORTEIO`. A regra só é escrevível porque a FR-413 criou a distinção; antes, a validação não tinha como saber quem sorteia (FR-432)
- [ ] T024 [US1] Servir o fragmento htmx que re-renderiza o cartão quando a forma da ordem muda, em `backend/processo_seletivo/interface/views.py`, seguindo o padrão de `fragmento-criterio`
- [ ] T025 [US1] Ler `orderProduction` do envio em `backend/processo_seletivo/interface/forms.py`
- [ ] T026 [P] [US1] Oferecer `scale: 2` e `mode: MEIO_PARA_CIMA` como padrão editável do marco novo em `backend/processo_seletivo/interface/views.py` (FR-419, valor confirmado em [research.md R3](research.md))
- [ ] T027 [P] [US1] Derivar código e denominação iniciais do Perfil em `backend/processo_seletivo/editais/domain/perfis.py`, desempatando quando o Perfil já tiver marco com o código derivado (`uq_marco_perfil_code`) (FR-420)
- [ ] T028 [US1] Impedir que padrão e derivação alcancem conteúdo já declarado, inclusive em Retificação, em `backend/processo_seletivo/interface/retificacao.py` (FR-421)
- [ ] T029 [US1] Condicionar as perguntas de ampla concorrência e reversão à existência de ao menos uma Modalidade declarada em `backend/processo_seletivo/interface/templates/interface/_perfil.html` — atenção à grafia-armadilha: o recorte que o sorteio usa é o `NULL`, e a Modalidade "AC" declarada é outra coisa (FR-417)

**Checkpoint**: US1 é demonstrável sozinha pelo cenário 1 do quickstart.

---

## Phase 4: User Story 2 — O conceito no ponto de uso (Priority: P2)

**Goal**: cada termo do vocabulário interno tem definição visível no primeiro uso da tela.

**Independent Test**: percorrer as **dez telas** que usam recorte, geração ou faixa em prosa visível
— `compor_classificacao`, `compor_perfis`, `corte`, `corte_historico`, `ordenacao`, `ocupacao`,
`ocupacao_historico`, `sorteio`, `convocacao`, `convocacao_historico` — verificando que cada termo do
domínio interno tem definição visível no primeiro uso, mais a tela de distribuição para a
consolidação.

**A contagem veio de varredura, não de leitura.** As três telas que a primeira escrita das tarefas
nomeava eram as que se lembra de cabeça; a varredura do texto visível, descartando `{% comment %}`,
achou dez.

**Não depende da Phase 2.** Pode ser entregue antes de US1 se a prioridade mudar.

### Testes

- [ ] T030 [P] [US2] Teste de que a tela de distribuição declara o que a consolidação produz antes de a ação ser acionada, em `backend/tests/interface/test_distribuicao.py` (FR-422)
- [ ] T031 [P] [US2] Criar `backend/tests/test_vocabulario_da_composicao.py`, **irmão** de `test_vocabulario_do_corte.py` e `test_vocabulario_da_ocupacao.py` — mesma mecânica de descartar `{% comment %}` e docstring, mas afirmando **presença** de definição em vez de ausência de termo — varrendo as dez telas que usam recorte, geração ou faixa (FR-424)
- [ ] T032 [P] [US2] Teste de que nenhuma ajuda visível entra nos cartões de composição e que o equivalente para tecnologia assistiva permanece, em `backend/tests/interface/test_acessibilidade_da_classificacao.py` (FR-428)
- [ ] T033 [P] [US2] Teste de que o bloco de ajuda da etapa não aparece sem item a que se refira, em `backend/tests/interface/test_compor_classificacao.py` (FR-426)

### Implementação

- [ ] T034 [P] [US2] Declarar o que a consolidação produz na tela de distribuição, antes da ação, em `backend/processo_seletivo/interface/templates/interface/distribuicao.html` (FR-422)
- [ ] T035 [P] [US2] Explicar, na etapa de Classificação, por que a Etapa pertence ao Edital e a ordem pertence ao Perfil, em `backend/processo_seletivo/interface/templates/interface/compor_classificacao.html` (FR-423)
- [ ] T036 [P] [US2] Definir **recorte**, **geração** e **faixa** no primeiro uso em `corte.html`, `corte_historico.html` e `ordenacao.html`, em `backend/processo_seletivo/interface/templates/interface/` (FR-424)
- [ ] T037 [P] [US2] Definir os termos usados por `ocupacao.html`, `ocupacao_historico.html` e `sorteio.html`, no mesmo diretório (FR-424)
- [ ] T038 [P] [US2] Definir os termos usados por `convocacao.html` e `convocacao_historico.html`, no mesmo diretório (FR-424)
- [ ] T039 [US2] Definir **recorte** e **faixa** no `como-preencher` de `compor_classificacao.html` e de `compor_perfis.html`, **e não** dentro de `_marco.html` e `_perfil.html` — é o que resolve a colisão entre FR-424 e FR-428 sem afrouxar nenhum dos dois (FR-424, FR-428)
- [ ] T040 [US2] Revisar as definições escritas em T034 a T039 contra a linguagem ubíqua, sem introduzir termo novo para conceito já nomeado (FR-425)
- [ ] T041 [US2] Ocultar o bloco de ajuda da etapa enquanto não existir item a que ele se refira, em `backend/processo_seletivo/interface/templates/interface/compor_classificacao.html` (FR-426)
- [ ] T042 [US2] Ligar cada item do bloco de ajuda ao campo que ele explica, em `backend/processo_seletivo/interface/templates/interface/compor_classificacao.html` (FR-427)
- [ ] T043 [US2] Conferir que nada de T034 a T042 pôs ajuda visível dentro dos cartões `_marco.html`, `_perfil.html` e `_modalidade.html` em `backend/processo_seletivo/interface/templates/interface/`; microcópia nova vai para o `como-preencher` da etapa (FR-428)

**Checkpoint**: US2 é demonstrável sozinha pelo cenário 2 do quickstart.

---

## Phase 5: User Story 3 — O método declarado uma vez (Priority: P3)

**Goal**: um Edital com sete Perfis de sorteio declara a regra uma vez, e não sete.

**Independent Test**: compor um Edital com sete Perfis e marcos de sorteio, contando quantas vezes a
mesma regra precisa ser declarada.

**Depende da Phase 2** (a forma da ordem diz quais marcos referenciam o método comum) e é o item de
maior risco: 22 arquivos Python leem `metodo_de_sorteio` ou `drawMethod`.

### Testes

- [ ] T044 [P] [US3] Teste de que sete marcos de sorteio exigem uma declaração do método, em `backend/tests/interface/test_metodo_do_marco.py` (SC-140)
- [ ] T045 [P] [US3] Teste de que o marco divergente registra a divergência explicitamente no conteúdo normativo, em `backend/tests/interface/test_metodo_do_marco.py` (FR-430)
- [ ] T046 [P] [US3] Teste de que Edital publicado antes da feature mantém o método literal em cada marco e não ganha chave no nível do Edital, em `backend/tests/integration/editais/test_metodo_comum.py` — ao lado de `test_mutabilidade_do_metodo_de_sorteio.py` (FR-431, SC-142)
- [ ] T047 [P] [US3] Teste de que o `metodo_hash` congelado de relação anterior à feature não muda, estendendo `backend/tests/integration/sorteios/test_metodo_nao_e_escolha.py` (a citação datada do método é o que impede que "qual método governa" se resolva depois da semente; a decisão é da 021, e esta feature não pode afrouxá-la)
- [ ] T048 [P] [US3] Teste de retificação do método comum pelo endereçamento novo, estendendo `backend/tests/integration/editais/test_mutabilidade_do_metodo_de_sorteio.py`

### Implementação

- [ ] T049 [US3] Acrescentar `metodo_de_sorteio_comum` a `Edital` em `backend/processo_seletivo/processos/models.py`, com `default=dict` (vazio significa não declarado)
- [ ] T050 [US3] Gerar a migration do campo em `backend/processo_seletivo/processos/migrations/`, sem tocar em dado publicado
- [ ] T051 [US3] Implementar a resolução — método do marco quando declarado, senão o do Edital — em **um lugar só**, `backend/processo_seletivo/sorteios/domain/metodo.py`, que já é o ponto de leitura do método no conteúdo versionado
- [ ] T052 [US3] Fazer os leitores perguntarem à resolução de T051, em `backend/processo_seletivo/classificacao/application/selectors.py`, `backend/processo_seletivo/classificacao/application/emissao.py`, `backend/processo_seletivo/editais/api/serializers.py` e `backend/processo_seletivo/interface/supervisao.py`
- [ ] T053 [US3] Publicar `drawMethod` no nível do Edital no conteúdo canônico, **omitindo a chave** quando vazio, em `backend/processo_seletivo/editais/api/serializers.py` e `backend/processo_seletivo/publicacoes/domain/colecoes.py`
- [ ] T054 [US3] Acrescentar as nove entradas `("edital", "drawMethod/…")` ao catálogo em `backend/processo_seletivo/editais/domain/mutabilidade.py`, mantendo as nove do marco, que endereçam a divergência
- [ ] T055 [US3] Oferecer a declaração do método comum na etapa de Classificação em `backend/processo_seletivo/interface/templates/interface/compor_classificacao.html`
- [ ] T056 [US3] Fazer o cartão do marco referenciar o método comum, e permitir divergir declarando o próprio, em `backend/processo_seletivo/interface/templates/interface/_marco.html` (FR-429, FR-430)
- [ ] T057 [US3] Ler e gravar o método comum no round-trip do rascunho em `backend/processo_seletivo/editais/application/draft.py`
- [ ] T058 [US3] Conferir o reaproveitamento de Edital anterior contra o método comum em `backend/processo_seletivo/editais/domain/reaproveitamento.py`

**Checkpoint**: US3 é demonstrável sozinha pelo cenário 3 do quickstart.

---

## Phase 6: Polish & Cross-Cutting

- [ ] T059 [P] Atualizar `backend/processo_seletivo/processos/management/commands/seed_demo.py` para semear um Edital que exercite a forma da ordem e o método comum (lembrar: são necessários dois Editais — prazo aberto e resultado divulgado não cabem no mesmo)
- [ ] T060 [P] Re-semear e conferir o documento publicado: documento publicado não se regenera, e mudou o renderizador é preciso re-semear para ver
- [ ] T061 Percorrer os quatro cenários de [quickstart.md](quickstart.md) pela interface, com o papel exato do ator (404 na gestão costuma ser autorização, não rota quebrada)
- [ ] T062 Rodar `cd backend && make lint check test-pg` e comparar com a linha de base de T003 — `lint` são dois passos, `ruff check` **e** `ruff format --check`
- [ ] T063 Escrever `specs/030-composicao-que-se-explica/rastreabilidade.md` cobrindo **os 25 requisitos** (FR-413 a FR-432, SC-138 a SC-142), no formato da `028`: por requisito, onde foi feito e onde é verificado, com **nomes reais** de função de teste — mais a comparação de contagem da suíte contra a linha de base de T003
- [ ] T064 Rodar `backend/tests/test_citacoes_de_requisito.py`: toda citação `FR-`/`SC-` desta feature precisa resolver contra a spec, e `test_a_matriz_de_rastreabilidade_cobre_todo_requisito_da_feature` passa a cobrar cada um dos 25 assim que a matriz de T063 existir

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: sem dependência
- **Phase 2 (Foundational)**: depende da Phase 1. **Bloqueia US1 e US3. Não bloqueia US2.**
- **US1 (Phase 3)**: depende da Phase 2
- **US2 (Phase 4)**: depende apenas da Phase 1
- **US3 (Phase 5)**: depende da Phase 2 e do checkpoint de US1 (a forma da ordem precisa estar de pé na tela antes de o método comum referenciá-la)
- **Phase 6 (Polish)**: depende das histórias que se quiser entregar

### Within Each Story

- Os testes vêm antes da implementação que verificam, e precisam falhar antes
- Modelo antes de serializer; serializer antes de template
- A resolução de T051 antes dos leitores de T052 — sempre, sob pena de duas respostas para a mesma pergunta

### Parallel Opportunities

- T004, T005 e T006 em paralelo: arquivos de teste diferentes
- T013 a T018 em paralelo entre si
- T030 a T033 e T034 a T038 em paralelo entre si
- T044 a T048 em paralelo entre si
- **US2 inteira em paralelo com a Phase 2 e com US1**: ela não toca em modelo, migration nem payload

**Cuidado com um paralelismo que parece seguro e não é**: editar template durante `make test-pg` dá
falha que não é do diff. Rode a suíte com a árvore parada.

---

## Implementation Strategy

### MVP — só US1

1. Phase 1 → Phase 2 → Phase 3
2. **Pare e valide**: cenário 1 do quickstart, contando os controles
3. US1 sozinha já reduz o custo do primeiro contato para a maioria dos Editais da amostra

### Entrega incremental

1. Setup + Foundational → base pronta
2. US1 → valide → entregue (MVP)
3. US2 → valide → entregue (pode vir antes de US1 se a prioridade mudar)
4. US3 → valide → entregue (maior risco, e o único que move conteúdo normativo)

---

## Notes

- **FR-424 e FR-428 colidem, e a colisão é real.** A FR-424 manda definir o termo no primeiro uso de
  cada tela; a FR-428 proíbe ajuda visível dentro dos cartões de composição. `_marco.html` usa
  **recorte** e **faixa**; `_perfil.html` usa **recorte**. A T039 resolve pela interpretação de que o
  cartão é fragmento e não tela, e por isso o termo dele se define no `como-preencher` da etapa que o
  contém. É interpretação, não requisito: se ela não for a pretendida, quem decide é o usuário, e a
  saída seria emendar a FR-424 para dizer "de cada etapa do assistente" em vez de "de cada tela".
  Nenhum teste pegaria isso sozinho — checklist, analyze e citações ficam verdes com FRs
  incompatíveis.
- **A matriz de rastreabilidade (T063) é artefato de implementação, não de planejamento.** Ela nomeia
  função de teste e local de código que ainda não existem, e a da `028` fecha comparando a contagem
  da suíte. Escrevê-la agora, com os requisitos listados e as duas colunas vazias, faria
  `test_a_matriz_de_rastreabilidade_cobre_todo_requisito_da_feature` passar sobre nada — o teste só
  confere que todo requisito tem linha, não que a linha diz alguma coisa. Um guardião que aprova
  vazio é pior que guardião nenhum, porque ninguém volta a olhar.
- Uma spec por sessão: fechada a feature, a próxima começa em outra
- Achado encontrado no meio disto vira registro, não escopo — a governança é do usuário
- **O marco de sorteio sem Etapa entrou, e a contradição sumiu.** Ele estava descrito nos casos de
  borda da spec e declarado como não-construído aqui — dois artefatos da mesma feature afirmando o
  oposto, que é o pior estado possível, porque vira o que quem lê primeiro implementar. Virou
  **FR-432**, coberto por T015 e T023. É o ACH-48, P1 na reauditoria, e a decisão de incluí-lo foi do
  usuário.
