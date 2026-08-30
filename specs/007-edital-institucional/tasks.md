---

description: "Task list template for feature implementation"
---

# Tasks: Edital Institucional

**Input**: Design documents from `/specs/007-edital-institucional/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/institucional.md](./contracts/institucional.md)

**Tests**: incluídos, e não por hábito. O princípio V da Constituição exige cobertura específica para
publicação, retificação, temporalidade, cotas, documentos e autorização — e esta feature toca
publicação e retificação. As tarefas de teste ficam dentro da história que verificam, nunca em fase
própria.

**Organization**: por história de usuário, na ordem de entrega do `plan.md`. Cada fase termina em
capacidade demonstrável no navegador, como exige o princípio VI.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode correr em paralelo — arquivos distintos, sem dependência pendente
- **[Story]**: a qual história a tarefa pertence
- Caminhos de arquivo são relativos à raiz do repositório

## Path Conventions

Aplicação Django em camadas, conforme `plan.md`:
`backend/processo_seletivo/<app>/{domain,application,models,api,infrastructure}`, mais
`backend/processo_seletivo/interface/` e `backend/tests/`.

## A trava, em cada tarefa

Antes de dar uma tarefa por concluída: **isto aumentou a fidelidade do Edital real ou a fluidez da
jornada de autoria?** Achado novo encontrado no caminho **registra-se e não se corrige aqui** (P-001).

---

## Phase 1: Setup

**Purpose**: partir de base conhecida. Não há projeto a inicializar — a feature é aditiva.

- [ ] T001 Rodar a suíte na base atual com o comando de `quickstart.md` e registrar o número de testes antes de qualquer alteração

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: uma única tarefa, bloqueante por ordem temporal. A `006` já deixou a fixture de bytes e
o script que a gera; o que falta é provar que o script reproduz **exatamente** os bytes de hoje,
antes que `pdf.py` mude. Sem isso, as duas regenerações de FR-006 seriam atos de fé.

- [ ] T002 Executar `backend/scripts/gerar_fixture_documento.py` na base intocada e confirmar que o arquivo gerado é idêntico byte a byte à fixture versionada; se divergir, corrigir o script **antes** de qualquer mudança de composição

**Checkpoint**: toda regeneração posterior é verificável.

---

## Phase 3: User Story 1a — O documento se lê como um Edital, parte apresentacional (Priority: P1)

**Goal**: o documento deixa de imprimir estado interno e passa a escrever decimais em português.

**Independent Test**: publicar um Edital com Cronograma, Etapa com peso `2` e nota mínima `60`, e
modalidade com percentual `20`; abrir o documento e ler `20%`, `peso 2` e `nota mínima 60`, sem
`Situação: PLANEJADO`.

**Não toca o snapshot, não muda o hash, não depende de nenhuma outra fase.**

- [ ] T003 [P] [US1] Criar `backend/processo_seletivo/publicacoes/infrastructure/humano.py` com `decimal(valor)`: recebe a string canônica de quatro casas, devolve pt-BR com vírgula e zeros à direita descartados (`"20.0000"` → `"20"`, `"12.5000"` → `"12,5"`, `"0.5000"` → `"0,5"`). Sem dependência de locale nem de estado global — o mesmo documento tem de sair igual em qualquer ambiente (D-001)
- [ ] T004 [P] [US1] Escrever `backend/tests/unit/publicacoes/test_humano.py` cobrindo a tabela B.1 do contrato, incluindo `"7.2500"` → `"7,25"` e o caso de valor ausente
- [ ] T005 [US1] Aplicar `humano.decimal` nos três pontos que hoje escrevem o decimal cru em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`: percentual da Regra Normativa (`_modalidades`), peso e nota mínima da Etapa (`_etapas`)
- [ ] T006 [US1] Remover a composição de `Situação: {evento['status']}` de `_cronograma` em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`. **Não** introduzir mapa de tradução — o estado do Evento não é conteúdo de Edital (D-002)
- [ ] T007 [US1] Escrever teste em `backend/tests/contract/test_documento_publicado.py` afirmando que o texto extraído do documento não contém `PLANEJADO` nem nenhum decimal de quatro casas, e contém `20%`
- [ ] T008 [US1] Regenerar a fixture de bytes com `backend/scripts/gerar_fixture_documento.py` e revisar o diff do texto extraído — **primeira das duas regenerações previstas em FR-006**
- [ ] T009 [US1] Verificar que o modo de prévia continua omitindo a seção de integridade e continua não lendo `content_hash`, e que as regras B.1 e B.2 valem nos dois modos

**Checkpoint**: entrega 1 fechada e demonstrável. Pode integrar sozinha.

---

## Phase 4: User Story 2 — O Edital tem as seções que um Edital tem (Priority: P1)

**Goal**: dez seções no catálogo, com as três institucionais nas posições que a leitura pede.

**Independent Test**: abrir a etapa de Conteúdo de um Edital novo, ver dez seções na ordem
declarada, editar o texto de uma das novas e encontrá-la no documento.

> **Integração conjunta.** As fases 4, 5 e 6 formam a **entrega 2** e integram-se **num único PR**
> (FR-018). Estão separadas aqui por história, não por momento de merge.

- [ ] T010 [US2] Acrescentar três `Secao` textuais ao `CATALOGO` em `backend/processo_seletivo/editais/domain/secoes.py` — `apresentacao`, `requisitos-gerais`, `classificacao` — com `default_text` institucional genérico, renumerando `order` conforme a tabela da seção 2 de `data-model.md`
- [ ] T011 [P] [US2] Escrever teste em `backend/tests/unit/editais/test_secoes.py` afirmando as dez chaves, seus títulos, tipos e a ordem exata; e que as posições cumprem FR-008 (apresentação antes de `perfis`, requisitos gerais antes de `inscricao`, classificação depois de `etapas`)
- [ ] T012 [P] [US2] Escrever teste afirmando que `identidade(edital_id, key)` das sete seções pré-existentes **não muda** com a renumeração — a identidade deriva da chave, não da ordem (D-007)
- [ ] T013 [US2] Verificar que a etapa `Conteúdo` do assistente exibe as dez seções sem alteração de template, por ler o catálogo; ajustar `backend/processo_seletivo/interface/templates/interface/compor_conteudo.html` apenas se a leitura for posicional
- [ ] T014 [P] [US2] Escrever teste de interface em `backend/tests/interface/test_conteudo.py`: editar o texto de `apresentacao`, salvar, e encontrá-lo na prévia na posição 1
- [ ] T015 [P] [US2] Escrever teste de interface em `backend/tests/interface/test_retificacao.py` retificando `/sections/id=<chave>/content` de uma **seção nova** pela tela de Retificação, e confirmando que a alteração chega ao documento consolidado (FR-010, SC-005). *As seções novas devem entrar automaticamente, por a tela derivar do catálogo — este teste é o que prova que sim, em vez de supor*

---

## Phase 5: User Story 3 — O Edital diz o que a vaga é (Priority: P1)

**Goal**: atribuições, carga horária e remuneração no Perfil, preservados e impressos.

**Independent Test**: preencher os três em dois Perfis, salvar, ir a outra etapa, salvar, voltar e
encontrá-los intactos; publicar e lê-los no documento.

- [ ] T016 [US3] Acrescentar `duties` (`TextField(blank=True)`), `workload` e `compensation` (`CharField(max_length=255, blank=True)`) a `PerfilVaga` em `backend/processo_seletivo/editais/models/perfis.py`. Nenhum `null`, nenhuma constraint nova
- [ ] T017 [US3] Criar `backend/processo_seletivo/editais/migrations/0005_perfil_institucional.py` com três `AddField` e nenhum `RunPython`
- [ ] T018 [P] [US3] Escrever teste de migration em `backend/tests/migrations/` confirmando que a `0005` aplica e reverte sem perda
- [ ] T019 [US3] Aceitar os três campos no serializer do rascunho em `backend/processo_seletivo/editais/api/serializers.py`, como opcionais com padrão `""`
- [ ] T020 [US3] Gravar os três em `replace_draft` (`backend/processo_seletivo/editais/application/draft.py`), sem alterar a semântica de gravação
- [ ] T021 [US3] Ler e reexibir os três em `backend/processo_seletivo/interface/forms.py` e em `backend/processo_seletivo/interface/templates/interface/_perfil.html`, com `duties` como área de texto multilinha
- [ ] T022 [US3] Garantir que `perfis_persistidos` em `backend/processo_seletivo/interface/forms.py` serialize os três — sem isso, salvar o Cronograma os apagaria, que é o defeito que a `006` corrigiu para as modalidades
- [ ] T023 [P] [US3] Escrever teste de interface em `backend/tests/interface/test_perfis.py`: preencher os três com `duties` em dois parágrafos, salvar o Cronograma em seguida, recarregar e encontrar tudo intacto com os parágrafos
- [ ] T024 [US3] Compor os três no documento em `_perfis` de `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`, usando `_paragrafos` para `duties` e omitindo cada um quando vazio
- [ ] T025 [P] [US3] Escrever teste afirmando que Perfil sem os três campos não imprime rótulo vazio e que a publicação não é impedida
- [ ] T026 [US3] Acrescentar `duties`, `workload` e `compensation` a `CAMPOS_PERFIL` em `backend/processo_seletivo/interface/retificacao.py`, com `duties` como `TEXTO_LONGO` — sem isso, um campo publicado não teria como ser corrigido pela interface, e FR-016 falharia pelo mesmo motivo que o achado 03 da auditoria
- [ ] T027 [US3] Acrescentar os três a `NOVO_PERFIL` **e a `_perfil_completo`** em `backend/processo_seletivo/interface/retificacao.py`. *Esta é a parte crítica: a docstring de `_perfil_completo` diz que a forma tem de ser a que `edital_snapshot` produz, porque um subconjunto quebraria a consulta pública. Acrescentar Perfil por Retificação sem as três chaves produziria conteúdo v3 incompleto*
- [ ] T028 [P] [US3] Escrever testes em `backend/tests/interface/test_retificacao.py`: retificar `duties` de um Perfil publicado; e acrescentar Perfil por Retificação verificando que o objeto resultante tem **exatamente** as chaves da forma v3, comparando com a saída de `edital_snapshot`

---

## Phase 6: User Story 1b — A raiz canônica e a proteção da identidade (Priority: P1)

**Goal**: o documento identifica Edital e Processo institucionalmente, sem UUID no corpo — e nenhuma
Retificação pode alterar essa identidade.

**Independent Test**: publicar e ler a seção de integridade com `Edital 12/2027` e
`Processo Seletivo <código> — <título>`, com SHA-256 presente e nenhum UUID; tentar retificar
`/processoTitle` e ser recusado.

- [ ] T029 [US1] Acrescentar `processoCode` e `processoTitle` à raiz de `edital_snapshot` em `backend/processo_seletivo/publicacoes/application/publish_edital.py`, lidos de `edital.processo` — que já vem por `select_related("processo")`, sem consulta adicional
- [ ] T030 [US1] Reescrever `_integridade` em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` conforme a tabela B.3 do contrato: preservar a afirmação de derivação, a versão do schema e o SHA-256; identificar o Edital por número/ano e o Processo por código e título; **deixar de escrever os dois UUIDs**
- [ ] T031 [US1] Declarar `CAMPOS_DE_IDENTIDADE` em `backend/processo_seletivo/publicacoes/domain/colecoes.py` com `editalId`, `processoId`, `processoCode`, `processoTitle` e `schemaVersion`, ao lado de `LISTAS_DE_CONTROLE`, com o racional de D-003.1 no docstring
- [ ] T032 [US1] Estender a recusa existente em `backend/processo_seletivo/publicacoes/domain/changes.py` para consultar o conjunto novo além de `LISTAS_DE_CONTROLE`, com mensagem que nomeie o campo. **Nenhum caminho, operador ou forma nova** — é um conjunto declarado e uma condição a mais (P-005)
- [ ] T033 [P] [US1] Escrever `backend/tests/unit/publicacoes/test_identidade_imutavel.py`: cada um dos cinco campos é recusado; `/title` e `/description` continuam aceitos; `/number` e `/year` continuam aceitos, com comentário registrando que são questão aberta e não omissão
- [ ] T034 [US1] Incrementar `SCHEMA_VERSION` de `2` para `3` em `backend/processo_seletivo/shared/canonical.py`, com o comentário declarando as **três** mudanças de forma que a versão cobre (FR-017)
- [ ] T035 [US1] Acrescentar `duties`, `workload` e `compensation` à forma de `profiles` em `COLECOES_PUBLICADAS`, em `backend/processo_seletivo/editais/domain/validation.py`
- [ ] T036 [US1] Atualizar `backend/tests/contract/test_forma_publicada.py` para a forma v3 completa: os dois escalares da raiz, os três campos de `profiles` como string sempre presente com `""`, as dez seções, **e `number` como string** — `Edital.number` é `CharField(50)` e a forma preserva `"02"`
- [ ] T037 [P] [US1] Escrever teste afirmando que dois snapshots de versão 3 do mesmo conteúdo têm exatamente o mesmo conjunto de chaves em todos os níveis (SC-002a)
- [ ] T038 [P] [US1] Escrever teste afirmando que um snapshot v3 basta, sozinho, para `render_edital_pdf` compor o documento — sem consulta ao banco
- [ ] T039 [US1] Acrescentar `duties`, `workload` e `compensation` a `PerfilInput` em `specs/001-processo-seletivo-editais/contracts/openapi.yaml` (bloco `PerfilInput`, hoje em `:548`), como `type: string` opcionais — é o payload do rascunho, onde a ausência é legítima
- [ ] T040 [US1] Acrescentar os três a `PerfilPublicado` no mesmo arquivo (bloco `PerfilPublicado`, hoje em `:639`), em `properties` **e** na lista `required` — na forma publicada eles estão sempre presentes, com `""` quando vazios (FR-014). *A raiz não exige alteração de contrato: `VersaoConsolidadaResponse.content` é `type: object, additionalProperties: true` (`:954`), de modo que `processoCode` e `processoTitle` passam sem mudança — registrar isso na tarefa evita a busca de um bloco que não existe*
- [ ] T041 [P] [US1] Rodar `backend/tests/contract/test_openapi_conformance.py` e confirmar que nenhuma rota fica fora do contrato e nenhuma resposta real diverge do schema declarado
- [ ] T042 [US1] Regenerar seed (`seed_demo`) e a fixture de bytes — **segunda e última regeneração prevista em FR-006** —, revisando o diff do texto extraído
- [ ] T043 [US1] Confirmar que conteúdo-base de versão 2 é recusado na consolidação por versão divergente, sem conversão, e que a mensagem é compreensível (FR-019)

**Checkpoint**: entrega 2 fechada. **Fases 4, 5 e 6 integram juntas, num único PR** (FR-018).

---

## Phase 7: User Story 4 — A jornada administrativa não oferece becos (Priority: P2)

**Goal**: cada tela oferece o próximo passo real e nenhuma convida a caminho que será recusado.

**Independent Test**: criar Processo com Edital que repita número/ano e ler a recusa correta; ser
levado a elaborar; ver `Submeter` desabilitado com motivo; não receber `Retificar` sem permissão.

- [ ] T044 [US4] Criar `backend/processo_seletivo/interface/acoes.py` com uma função que devolve, para um Edital e um ator, o conjunto completo de ações: rótulo, rota, disponibilidade e **motivo quando indisponível**. Funde `ACOES_POR_SITUACAO`, `atos.disponiveis` e o `<li>` fixo do template, e incorpora a previsão que `praticar_ato` já calcula com `atos.impedimento` e `_pendencias` (D-006)
- [ ] T045 [US4] Passar a usar `acoes.py` na view `detalhe` de `backend/processo_seletivo/interface/views.py`, substituindo `atos`
- [ ] T046 [US4] Reescrever o cartão "O que fazer agora" em `backend/processo_seletivo/interface/templates/interface/detalhe.html`: iterar o conjunto único, remover o `<li>` fixo de `Retificar`, e derivar a mensagem de ausência do mesmo conjunto
- [ ] T047 [US4] Renderizar ação indisponível como controle desabilitado com o motivo associado por vínculo programático, mantendo contraste legível (FR-024)
- [ ] T048 [US4] Passar a usar `acoes.py` também na view `lista`, para que listagem e detalhe deixem de ter registros distintos
- [ ] T049 [US4] Mover a checagem de permissão de `retificar()` para fora do ramo POST em `backend/processo_seletivo/interface/views.py`, e apresentar a tela em leitura para quem não tem `retificacao:elaborar` (FR-026)
- [ ] T050 [US4] Ajustar `backend/processo_seletivo/interface/templates/interface/retificar.html` para o modo leitura: sem campos de edição, sem botão de envio, sem acrescentar Perfil
- [ ] T051 [US4] Promover `Elaborar o Edital <n>/<ano>` a ação primária na tela seguinte à criação do Processo, em `backend/processo_seletivo/interface/templates/interface/processo_detalhe.html`, rebaixando o impedimento de cancelar
- [ ] T052 [US4] Separar os dois `create` em blocos `try` distintos em `create_process_with_first_edital`, em `backend/processo_seletivo/processos/application/commands.py`, devolvendo `edital_identifier_conflict` para o conflito do Edital. **Nenhum código de erro novo** — o certo já existe em `create_edital`
- [ ] T053 [P] [US4] Escrever `backend/tests/unit/processos/test_conflito_identificacao.py`: conflito do Processo devolve `institutional_identifier_conflict`; conflito de `(escopo, número, ano)` do Edital devolve `edital_identifier_conflict`
- [ ] T054 [P] [US4] Escrever `backend/tests/interface/test_acoes.py` cobrindo as cinco situações de `ACOES_POR_SITUACAO` × papéis, afirmando que nunca coexistem uma ação listada e a mensagem de ausência
- [ ] T055 [P] [US4] Escrever teste de interface com ator sem `retificacao:elaborar`: o detalhe não oferece `Retificar`, e a URL direta devolve tela sem campo editável nem envio
- [ ] T056 [P] [US4] Escrever teste afirmando que `Submeter` aparece desabilitado com motivo num Edital sem dados mínimos, e que a recusa do domínio permanece independente da interface (FR-025)

**Checkpoint**: entrega 3 fechada.

---

## Phase 8: User Story 5 — Quem entrega sabe a quem entregou (Priority: P2)

**Goal**: depois de submeter e de homologar, a tela diz a situação e o papel do próximo ato.

**Independent Test**: submeter e ler quem age agora; homologar como segunda pessoa e reler.

- [ ] T057 [US5] Acrescentar a `backend/processo_seletivo/interface/acoes.py` uma função de leitura que devolve situação em português e o **papel** responsável pelo próximo ato, derivada do estado e de `ACOES_POR_SITUACAO`. Nada persistido, nada atribuído a pessoa (FR-029, FR-030)
- [ ] T058 [US5] Fazer essa função consultar também `impede_por_segregacao`: quem elaborou e homologou o mesmo Edital **não** pode ser apontado como quem publica, ainda que tenha a permissão. É o ponto delicado da entrega (FR-031)
- [ ] T059 [US5] Exibir a indicação no detalhe do Edital, em `backend/processo_seletivo/interface/templates/interface/detalhe.html`
- [ ] T060 [US5] Exibir a indicação também na confirmação do ato praticado, em `backend/processo_seletivo/interface/templates/interface/confirmar.html`
- [ ] T061 [P] [US5] Escrever `backend/tests/interface/test_bastao.py`: submetido aponta quem homologa; homologado aponta quem publica
- [ ] T062 [P] [US5] Escrever o teste do caso que separa as duas derivações: ator que elaborou **e** homologou, com permissão de publicar, **não** é apontado; o mesmo Edital homologado por outra pessoa aponta quem publica (cenários 3 e 4 da `US5`)
- [ ] T063 [P] [US5] Escrever teste afirmando a ausência: nenhum modelo, campo persistido, fila, notificação ou designação nasce nesta entrega

**Checkpoint**: entrega 4 fechada.

---

## Phase 9: User Story 6 — Os atritos de operação (Priority: P3)

**Goal**: a interface deixa de cobrar, em cada volta, o preço de informação que ela tem e não mostra.

**Independent Test**: percorrer o assistente inteiro, inclusive só por teclado com leitor de tela.

### Obrigatoriedade e recusa

- [ ] T064 [US6] Estabelecer a convenção de campo obrigatório — marca visível na etiqueta mais `aria-required` — e aplicá-la nas etapas do assistente e seus fragmentos: `compor_identificacao.html`, `compor_conteudo.html`, `_perfil.html`, `_evento.html`, `_etapa.html` e `_modalidade.html`, em `backend/processo_seletivo/interface/templates/interface/`. São os seis arquivos que hoje usam `required` sem dizê-lo a quem lê
- [ ] T065 [US6] Aplicar a mesma convenção na criação de Processo e nas três telas de confirmação: `processo_criar.html`, `confirmar.html`, `processo_confirmar.html` e `retificacao_confirmar.html`
- [ ] T066 [US6] Aplicar a mesma convenção na tela de Retificação e seus fragmentos: `retificar.html`, `_retificacao_perfil.html` e `_retificacao_evento.html`. Com estes três, a lista fechada de FR-032 está inteira
- [ ] T067 [US6] Ampliar o bloco `{% if erros %}` de `backend/processo_seletivo/interface/templates/interface/compor_base.html`, que já lista os erros, para ancorar cada item no campo correspondente e receber foco ou ser anunciado ao aparecer
- [ ] T068 [US6] Levar o mesmo resumo ancorado às telas que hoje mostram erro sem ele: `processo_criar.html`, `confirmar.html`, `processo_confirmar.html`, `retificar.html` e `retificacao_confirmar.html`
- [ ] T069 [US6] Associar cada campo recusado à sua mensagem por vínculo programático, não só por proximidade visual (FR-033)
- [ ] T070 [P] [US6] Escrever teste de interface afirmando obrigatoriedade marcada e recusa em resumo **e** junto do campo

### Aparência e ordem

- [ ] T071 [P] [US6] Estender a regra de estilo além de `input[type=text]` em `backend/processo_seletivo/interface/static/interface/`, de modo que `Ano` tenha altura, fonte e borda dos vizinhos, e que a largura declarada em `Número` tenha efeito (FR-034)
- [ ] T072 [US6] Desabilitar `↑` na primeira linha e `↓` na última em `backend/processo_seletivo/interface/static/interface/ordenacao.js`, mantendo o estado correto após cada movimento e após remoção
- [ ] T073 [US6] Exibir a posição de cada linha na legenda — "Evento 2 de 3" — atualizada pelo mesmo caminho que renumera `order`
- [ ] T074 [P] [US6] Escrever teste de JavaScript em `backend/tests/javascript/` para o estado dos botões nas pontas e para a numeração da legenda

### Etapas, remoção e escolha

- [ ] T075 [US6] Compor a opção do seletor de Evento com a data herdada — "Prova didática · 10/04/2027 14:00" — em `backend/processo_seletivo/interface/views.py` e no fragmento de Etapa (FR-036)
- [ ] T076 [US6] Agrupar Eliminatória e Classificatória sob legenda "Caráter" em `backend/processo_seletivo/interface/templates/interface/_etapa.html` (FR-037)
- [ ] T077 [US6] Implementar em `backend/processo_seletivo/interface/static/interface/` a regra de "linha tem conteúdo" — qualquer campo preenchido ou qualquer item filho — e a confirmação que dela decorre: diz o que será descartado, é operável por teclado e tem o cancelamento como ação padrão (FR-038)
- [ ] T078 [US6] Ligar a confirmação aos quatro fragmentos que hoje oferecem `Remover` sem rede — `_perfil.html`, `_evento.html`, `_etapa.html` e `_modalidade.html` — e à marcação de remoção de `retificar.html`
- [ ] T079 [P] [US6] Escrever teste de JavaScript para a confirmação: linha preenchida confirma, linha vazia não

### Autoridade signatária

- [ ] T080 [US6] Criar `backend/processo_seletivo/publicacoes/domain/autoridades.py` com catálogo declarado — chave estável, identificador institucional, nome e cargo —, no padrão de `editais/domain/secoes.py`. Sem entidade, sem migration, sem tela de gestão, sem permissão nova (FR-039)
- [ ] T081 [US6] Substituir os três campos de autoridade em `backend/processo_seletivo/interface/templates/interface/confirmar.html` por uma escolha no catálogo; nome, cargo e identificador vêm da entrada escolhida e **nenhum identificador é digitado, exibido ou impresso** (FR-044)
- [ ] T082 [US6] Resolver a escolha para `signatory_id`, `signatory_name` e `signatory_role` no caminho de publicação, sem alterar o que a `Publicacao` persiste
- [ ] T083 [P] [US6] Escrever teste afirmando que a publicação funciona pela escolha, que autoridade fora do catálogo não é aceita em novo ato, e que Publicação já praticada com autoridade depois retirada permanece íntegra (FR-046)
- [ ] T084 [US6] Aplicar a mesma escolha de autoridade em `backend/processo_seletivo/interface/templates/interface/retificacao_confirmar.html` e no ramo correspondente de `backend/processo_seletivo/interface/views.py`. **São dois fluxos de publicação** — o do Edital e o da Retificação —, e ambos pedem os três campos hoje; deixar um de fora manteria o UUID digitado exatamente onde a correção de um Edital publicado acontece
- [ ] T085 [P] [US6] Escrever teste cobrindo os **dois** fluxos: publicar Edital e publicar Retificação, ambos com autoridade escolhida em lista e nenhum identificador digitado (SC-009a)

### Estado, nomes e auditoria

- [ ] T086 [US6] Passar `_progresso` de dois para três estados em `backend/processo_seletivo/interface/views.py`: `conteudo` deixa de ser `True` fixo e passa a ser "pronta para revisar" enquanto `edital.secoes.exists()` for falso, e "concluída" depois (D-005)
- [ ] T087 [US6] Distinguir os três estados visualmente em `backend/processo_seletivo/interface/templates/interface/compor_base.html`, sem depender apenas de cor (FR-040)
- [ ] T088 [P] [US6] Escrever teste afirmando que Edital recém-criado mostra `Conteúdo` como "pronta para revisar" e que gravar a etapa a torna "concluída"
- [ ] T089 [US6] Substituir `{{ request.GET.ato|situacao }}` em `backend/processo_seletivo/interface/templates/interface/detalhe.html` pelo rótulo humano que `atos.ATOS` já declara — o filtro `situacao` mapeia **situações** e por isso devolve `submeter` cru (FR-041)
- [ ] T090 [P] [US6] Escrever teste afirmando que a faixa de confirmação diz "Submissão para revisão" e "Publicação", e nunca a chave interna
- [ ] T091 [US6] Registrar qual etapa do assistente foi gravada no evento de auditoria da gravação do rascunho, em `backend/processo_seletivo/editais/application/draft.py` e no chamador da interface. **Registrar a área, não a diferença** (FR-043)
- [ ] T092 [P] [US6] Escrever teste afirmando que quatro gravações em etapas diferentes produzem quatro registros distinguíveis na trilha

**Checkpoint**: entrega 5 fechada.

---

## Phase 10: Polish & Cross-Cutting Concerns

- [ ] T093 Rodar `ruff check` e `ruff format --check` e a suíte completa, comparando a contagem de testes com a registrada em T001
- [ ] T094 Percorrer o assistente inteiro **só por teclado, com leitor de tela**, alcançando obrigatoriedade, motivo de ato desabilitado, resumo de erros e confirmação de remoção, sem depender de cor (SC-009b)
- [ ] T095 Executar a demonstração de ponta a ponta de `quickstart.md` com **dois atores**, do painel ao documento publicado, e registrar as verificações
- [ ] T096 Conferir a tabela de rastreabilidade da spec: os dezesseis achados abertos estão cobertos, e **nenhum requisito novo entrou** durante a implementação
- [ ] T097 Registrar, sem corrigir, todo achado novo encontrado durante a implementação — inclusive a questão aberta de `/number` e `/year` na Retificação (D-003.1)

---

## Dependencies

```text
T001 → T002 → Fase 3 (US1a)
                 ↓
              Fase 4 (US2) ─┐
              Fase 5 (US3) ─┼→ integram JUNTAS, um único PR (FR-018)
              Fase 6 (US1b) ┘
                 ↓
              Fase 7 (US4) → Fase 8 (US5)     [US5 usa acoes.py, criado em T044]
                 ↓
              Fase 9 (US6)  [independente das demais]
                 ↓
              Fase 10
```

**Únicas dependências reais**:

- **T002 antes de qualquer mudança em `pdf.py`** — é a linha de base das duas regenerações.
- **Fase 3 antes da Fase 6** — as duas tocam `pdf.py` e cada uma regenera a fixture. A ordem inversa
  custaria a demonstração antecipada, não uma regeneração a menos (FR-006, FR-018).
- **T044 antes da Fase 8** — a passagem de bastão vive no módulo que a Fase 7 cria.
- **T016/T017 antes de T029** — a forma v3 precisa das colunas existindo.
- **T027 no mesmo PR que T029 a T043** — `_perfil_completo` precisa produzir **a forma v3**, e a
  forma v3 nasce na Fase 6. Acrescentar Perfil por Retificação com a forma antiga produziria conteúdo
  publicado incompleto; a integração conjunta das fases 4, 5 e 6 já garante isto, e o registro aqui
  é para que a ordem interna do PR não o inverta.

A **Fase 9 é independente de tudo** e pode correr em paralelo com as fases 7 e 8, por tocar
majoritariamente arquivos distintos. As exceções são `views.py` (T045, T049, T075, T086) e
`detalhe.html` (T046, T047, T059, T089), que devem ser sequenciados entre si.

---

## Parallel Execution Examples

**Fase 3** — T003 e T004 juntas (módulo novo e seu teste), depois T005 e T006 em sequência no mesmo
arquivo.

**Fases 4 e 5** — T011, T012 e T014 em paralelo com T018, T023 e T025: apps distintos, arquivos
distintos.

**Fase 6** — T033, T037 e T038 em paralelo; todas são testes em arquivos próprios.

**Fase 7** — T053, T054, T055 e T056 em paralelo depois que T044 a T052 estiverem prontas.

**Fase 5** — T028 depois de T026 e T027; os três tocam `retificacao.py` e devem ser sequenciados.

**Fase 9** — os quatro agrupamentos (obrigatoriedade, aparência/ordem, escolha/remoção, autoridade)
tocam conjuntos de arquivos quase disjuntos e podem correr simultaneamente; só o estado do assistente
(T086, T087) compete com `views.py`.

---

## Implementation Strategy

**MVP**: a **Fase 3 sozinha** já entrega valor visível — o documento deixa de parecer um despejo de
dados internos, sem tocar snapshot, hash ou migration. É a menor unidade integrável desta feature e
a que mais muda a percepção por hora gasta.

**Incremento seguinte**: fases 4 + 5 + 6 juntas, num PR só. É o único momento da feature em que três
histórias compartilham um merge, e a razão está declarada em FR-017 e FR-018: uma versão canônica
que admite duas formas não é uma versão canônica.

**Depois**: fases 7, 8 e 9, em qualquer ordem que a equipe prefira, respeitando `T044 → Fase 8`.

**Condição de merge de cada entrega**: a demonstração no navegador descrita em `quickstart.md`, não a
contagem de testes (princípio VI).
