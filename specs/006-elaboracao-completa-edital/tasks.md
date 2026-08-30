---

description: "Task list template for feature implementation"
---

# Tasks: Elaboração Completa do Edital

**Input**: Design documents from `/specs/006-elaboracao-completa-edital/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/elaboracao.md](./contracts/elaboracao.md)

**Tests**: incluídos, e não por hábito. O princípio V da Constituição exige cobertura específica
para publicação, retificação, temporalidade, cotas, documentos e autorização — tudo o que esta
feature toca. As tarefas de teste estão dentro da história que verificam, nunca em fase própria.

**Organization**: por história de usuário, na ordem de entrega do `plan.md`. Cada fase termina em
capacidade demonstrável no navegador, como exige o princípio VI.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode correr em paralelo — arquivos distintos, sem dependência pendente
- **[Story]**: a qual história a tarefa pertence
- Caminhos de arquivo são relativos à raiz do repositório

## Path Conventions

Aplicação Django em camadas, conforme `plan.md`: `backend/processo_seletivo/<app>/{domain,application,models,api,infrastructure}`,
mais `backend/processo_seletivo/interface/` para a interface administrativa e `backend/tests/` para a suíte.

---

## Phase 1: Setup

**Purpose**: partir de base conhecida. Não há projeto a inicializar — a feature é aditiva.

- [ ] T001 Confirmar suíte verde na base, com o comando de `quickstart.md`, e registrar o número de testes antes de qualquer alteração

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: uma única tarefa, e ela é bloqueante por ordem temporal — precisa acontecer **antes** de
`pdf.py` mudar, ou a linha de base se perde.

- [ ] T002 Capturar fixture com os bytes do PDF publicado gerado hoje, a partir de um snapshot fixo e versionado junto dela, em `backend/tests/contract/fixtures/documento_publicado_v1.pdf`, e o teste que o compara em `backend/tests/contract/test_documento_publicado.py`. A fixture prova **uma** coisa: que a introdução do modo de prévia não alterou o documento publicado. Regenerá-la só é legítimo na mesma tarefa que mudar a composição de propósito, com o diff revisado — T075 não a toca

**Checkpoint**: a regressão byte a byte de US1 tem contra o que comparar.

---

## Phase 3: User Story 0 — A jornada principal sem becos sem saída (Priority: P0)

**Goal**: iniciar e retomar a elaboração pelo fluxo principal, sem rotas ocultas e sem pendências
declaradas incorrigíveis.

**Independent Test**: com dois Processos cadastrados, criar um terceiro pelo painel, alterar o título
de um Edital em elaboração, mover dois Eventos, salvar, recarregar, e abrir o documento de um Edital
publicado — tudo pela interface.

### Exposição de capacidades existentes

- [ ] T003 [P] [US0] Mover a ação `Novo Processo Seletivo` do bloco `{% empty %}` para o cabeçalho da listagem, sob o mesmo `pode_criar`, em `backend/processo_seletivo/interface/templates/interface/lista.html`
- [ ] T004 [US0] Expor no detalhe do Edital o acesso ao documento da **publicação vigente** — a mais recente, e não a original, para que o link acompanhe as Retificações publicadas — fornecendo o identificador da Publicação no contexto em `backend/processo_seletivo/interface/views.py` e o link em `backend/processo_seletivo/interface/templates/interface/detalhe.html`

### Alterar a identificação em elaboração

- [ ] T005 [US0] Criar `update_edital_identification` em `backend/processo_seletivo/editais/application/identificacao.py`, exigindo status `EM_ELABORACAO`, `expected_revision`, permissão e registro de auditoria, no molde de `backend/processo_seletivo/processos/application/commands.py`
- [ ] T006 [US0] Tornar a etapa `Identificação` editável e marcar `title` e `description` como corrigíveis em `DESTINO_DA_PENDENCIA`, removendo `MOTIVO_NAO_CORRIGIVEL` do caminho alcançável, em `backend/processo_seletivo/interface/views.py`
- [ ] T007 [US0] Trocar a exibição por formulário de identificação em `backend/processo_seletivo/interface/templates/interface/compor_identificacao.html`

### Ordem como dado explícito

- [ ] T008 [US0] Fazer `ler_eventos` ordenar pelo campo `order` recebido, em vez de derivar da ordem de leitura dos índices, em `backend/processo_seletivo/interface/forms.py`
- [ ] T009 [US0] Acrescentar campo oculto `order` e botões de subir e descer, com rótulo acessível, em `backend/processo_seletivo/interface/templates/interface/_evento.html`
- [ ] T010 [US0] Implementar o movimento de linha e a renumeração do campo `order` em `backend/processo_seletivo/interface/static/interface/ordenacao.js`, e carregá-lo em `compor_cronograma.html`

### Testes

- [ ] T011 [P] [US0] Botão presente na listagem com Processos cadastrados e ausente para quem não tem permissão, em `backend/tests/interface/test_lista.py`
- [ ] T012 [P] [US0] Alteração de identificação persiste, registra auditoria e é recusada fora de `EM_ELABORACAO`, em `backend/tests/interface/test_compor.py`
- [ ] T013 [P] [US0] Nenhuma pendência aparece como não corrigível quando a etapa a resolve, em `backend/tests/interface/test_impedimentos.py`
- [ ] T014 [US0] Reordenar **muda a ordem persistida** e preserva o `id` de cada Evento, em `backend/tests/interface/test_compor.py`
- [ ] T015 [P] [US0] Mover linha atualiza o campo `order` no DOM, em `backend/tests/javascript/ordenacao.test.js`, registrado em `backend/tests/test_javascript.py`
- [ ] T016 [P] [US0] Detalhe de Edital publicado oferece acesso ao documento, em `backend/tests/interface/test_fluxo.py`

**Checkpoint**: demonstrável — criar Processo, editar título, mover Eventos, abrir documento
publicado.

---

## Phase 4: User Story 1 — Ver o Edital antes de publicar (Priority: P1)

**Goal**: visualizar o documento em construção sem executar ato irreversível.

**Independent Test**: alterar o rascunho, visualizar, encontrar a alteração no documento, voltar e
continuar editando — sem que nenhum registro publicado seja criado.

**Dependency**: T002 precisa estar feita, ou a regressão de bytes não tem linha de base.

- [ ] T017 [US1] Acrescentar modo `PREVIEW | PUBLISHED` a `render_edital_pdf`, suprimindo a composição de integridade e trocando o rodapé pela marca de prévia em todas as páginas, em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`
- [ ] T018 [US1] Criar a view de prévia, que renderiza `edital_snapshot(edital)` e devolve os bytes sem persistir nada, em `backend/processo_seletivo/interface/views.py`, com rota em `backend/processo_seletivo/interface/urls.py` e nome de arquivo de prévia no `Content-Disposition`
- [ ] T019 [P] [US1] Oferecer `Visualizar Edital` na etapa de Revisão, em `backend/processo_seletivo/interface/templates/interface/compor_revisao.html`
- [ ] T020 [P] [US1] Oferecer `Visualizar Edital` no detalhe enquanto submetido ou homologado, em `backend/processo_seletivo/interface/templates/interface/detalhe.html`

### Testes

- [ ] T021 [US1] Em modo publicado, os bytes continuam idênticos à fixture de T002, em `backend/tests/contract/test_documento_publicado.py`
- [ ] T022 [P] [US1] Em modo prévia, nenhuma página contém hash ou afirmação de derivação de versão homologada, e todas contêm a marca, em `backend/tests/contract/test_documento_publicado.py`
- [ ] T023 [P] [US1] Visualizar não altera o estado do Edital e não cria `Publicacao`, `RevisaoEdital`, `VersaoConsolidada` nem `DocumentoPublicado`, em `backend/tests/interface/test_fluxo.py`
- [ ] T024 [US1] A prévia está disponível em elaboração, submetido e homologado, e é recusada a quem não pode ver o Edital, em `backend/tests/interface/test_fluxo.py`
- [ ] T025 [US1] Publicar logo após a prévia, sem alterações, produz documento de mesmo conteúdo normativo, em `backend/tests/interface/test_fluxo.py`

**Checkpoint**: demonstrável — editar, visualizar, voltar, editar de novo.

---

## Phase 5: User Story 2 — Definir as Etapas de Avaliação (Priority: P1)

**Goal**: definir as etapas do certame e vê-las compor o Edital.

**Independent Test**: criar duas Etapas, reordená-las, salvar, visualizar o documento e encontrá-las
na ordem definida com suas propriedades.

**Atenção — esta fase produz a versão 2 do esquema canônico, e a produz inteira.** `stages` e
`sections` entram juntas no snapshot, nos registros declarativos e no `openapi.yaml`, ainda que a
edição de conteúdo textual só chegue na US4. Dividir isso deixaria dois formatos distintos
declarando a mesma versão canônica.

### Domínio e persistência

- [ ] T026 [P] [US2] Criar o modelo `EtapaAvaliacao` com unicidade de `order` por Edital e restrição de nota mínima não negativa, em `backend/processo_seletivo/editais/models/etapas.py`, exportando-o em `backend/processo_seletivo/editais/models/__init__.py`
- [ ] T027 [P] [US2] Declarar o catálogo fixo de Seções — identidade determinística, chave, título, ordem, tipo, origem e texto institucional inicial — em `backend/processo_seletivo/editais/domain/secoes.py`
- [ ] T028 [P] [US2] Escrever as invariantes da Etapa — nome obrigatório, ordem sem ambiguidade, nota mínima não negativa, Evento referenciado do mesmo Edital — em `backend/processo_seletivo/editais/domain/etapas.py`
- [ ] T029 [US2] Gerar a migration de `EtapaAvaliacao` em `backend/processo_seletivo/editais/migrations/`

### Forma canônica da versão 2

- [ ] T030 [US2] Acrescentar `stages` e `sections` a `edital_snapshot`, montando as seções a partir do catálogo com identidade `uuid5` sobre `(edital.id, key)`, em `backend/processo_seletivo/publicacoes/application/publish_edital.py`
- [ ] T031 [US2] Elevar `SCHEMA_VERSION` de 1 para 2 em `backend/processo_seletivo/shared/canonical.py`
- [ ] T032 [P] [US2] Declarar `/stages` e `/sections` em `COLECOES_COM_CHAVE`, em `backend/processo_seletivo/publicacoes/domain/colecoes.py`
- [ ] T033 [US2] Declarar `ETAPA_PUBLICADA` e `SECAO_PUBLICADA` em `COLECOES_PUBLICADAS` e registrar o formato `decimal` com leitor `Decimal` em `_LEITOR_DE_FORMATO`, aplicando a `weight` e `minimumScore` `formato="decimal"` e padrão `^\d+(\.\d{1,4})?$` — sem sinal, o que já recusa nota mínima negativa vinda de Retificação — em `backend/processo_seletivo/editais/domain/validation.py`
- [ ] T034 [US2] Acrescentar as duas verificações que a forma declarada não alcança — topologia de `sections` contra o catálogo, e `stages[*].scheduleEventId` existente em `schedule` — em `backend/processo_seletivo/editais/domain/validation.py`
- [ ] T035 [US2] Recusar consolidação sobre conteúdo-base cuja `schemaVersion` difira da vigente, com código próprio, em `backend/processo_seletivo/publicacoes/application/retificacoes.py`
- [ ] T036 [US2] Aplicar o delta de **saída** do contrato — `EtapaPublicada`, `SecaoPublicada`, `schemaVersion` 2, código de versão divergente — e, na entrada, apenas `stages` em `RascunhoInput`, em `specs/001-processo-seletivo-editais/contracts/openapi.yaml`. *`sections` na entrada fica para T066: declarar entrada que a API ainda recusa publicaria contrato falso.*

### Gravação e interface

- [ ] T037 [US2] Gravar `stages` preservando identidade, no molde dos Eventos, em `backend/processo_seletivo/editais/application/draft.py`
- [ ] T038 [US2] Aceitar `stages` no payload do rascunho em `backend/processo_seletivo/editais/api/serializers.py`
- [ ] T039 [US2] Acrescentar a etapa `Etapas de Avaliação` a `ETAPAS_COMPOSICAO`, com progresso e roteamento de pendências, em `backend/processo_seletivo/interface/views.py`, e o fragmento de linha em `backend/processo_seletivo/interface/urls.py`
- [ ] T040 [P] [US2] Criar `compor_etapas.html` e `_etapa.html` em `backend/processo_seletivo/interface/templates/interface/`, com campo oculto `order`, botões de ordem e seleção de Evento do Cronograma
- [ ] T041 [US2] Ler e preservar Etapas em `ler_etapas` e `etapas_persistidas`, em `backend/processo_seletivo/interface/forms.py`
- [ ] T042 [US2] Compor o documento a partir das seções do catálogo, com as Etapas na seção que as origina, em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`
- [ ] T043 [P] [US2] Criar Etapas na demonstração navegável, em `backend/processo_seletivo/processos/management/commands/seed_demo.py`

### Testes

- [ ] T044 [P] [US2] Invariantes da Etapa, incluindo referência a Evento de outro Edital, em `backend/tests/unit/editais/test_etapas.py`
- [ ] T045 [P] [US2] Forma publicada de `stages` e `sections` conferida contra o contrato, em `backend/tests/contract/test_forma_publicada.py`
- [ ] T046 [US2] Teste de cobertura das declarações: toda **coleção-raiz de entidades** do snapshot tem forma em `COLECOES_PUBLICADAS` e esquema correspondente no `openapi.yaml`, com a correspondência derivada do nome declarado em `COLECOES_PUBLICADAS` e não de convenção de nomes — a cobertura que hoje não existe, em `backend/tests/contract/test_forma_publicada.py`
- [ ] T047 [P] [US2] Retificação aceita `/stages/id=<uuid>/name` e `ADD /stages/-`, e recusa `/stages/0/name`, em `backend/tests/contract/test_enderecamento_api.py`
- [ ] T048 [P] [US2] Retificação recusa topologia divergente de `sections` — acréscimo, remoção, troca de tipo, ordem, título, origem, textual sem conteúdo, gerada com conteúdo — em `backend/tests/contract/test_limites_de_borda.py`
- [ ] T049 [US2] Retificação recusa `scheduleEventId` inexistente e `weight` fora da forma decimal, em `backend/tests/contract/test_limites_de_borda.py`
- [ ] T050 [P] [US2] Consolidação sobre conteúdo-base de outra versão canônica é recusada, e não gravada com a versão errada, em `backend/tests/contract/test_retificacoes_api.py`
- [ ] T051 [P] [US2] Assistente: acrescentar, editar, remover e reordenar Etapas preservando identidade, e datas vindas do Evento vinculado, em `backend/tests/interface/test_compor.py`
- [ ] T052 [P] [US2] Etapas aparecem na prévia e no documento publicado, na ordem definida, em `backend/tests/interface/test_fluxo.py`

**Checkpoint**: demonstrável — duas Etapas, reordenadas, visíveis no documento.

---

## Phase 6: User Story 3 — Declarar as modalidades de reserva (Priority: P2)

**Goal**: declarar modalidades com percentual e fundamento, e vê-las no documento — sem que a
gravação as destrua.

**Independent Test**: configurar duas modalidades com regra, salvar, ir a outra etapa, salvar de
novo, recarregar e encontrar tudo intacto com as mesmas identidades.

### A ida e volta sem perda

- [ ] T053 [US3] Criar `ModalidadeConcorrencia` **e `RegraNormativa`** com os `id` recebidos, como já se faz com Perfis e Eventos, em `backend/processo_seletivo/editais/application/draft.py`
- [ ] T054 [US3] Estender `_reject_identifiers_of_other_editais` às modalidades e às regras normativas, mantendo a resposta `409` que a verificação já dá, em `backend/processo_seletivo/editais/application/draft.py`
- [ ] T055 [US3] Serializar a modalidade inteira — `id`, `description` e `normativeRule` com o `id` dela — em `perfis_persistidos`, e ler os campos estruturados em `ler_perfis`, em `backend/processo_seletivo/interface/forms.py`
- [ ] T056 [US3] Substituir a caixa de texto livre por linhas de modalidade com código, nome, percentual, fundamento e **versão do fundamento**, criando `backend/processo_seletivo/interface/templates/interface/_modalidade.html`, referenciado por `_perfil.html`, com a rota de fragmento em `backend/processo_seletivo/interface/urls.py` e a view em `backend/processo_seletivo/interface/views.py`
- [ ] T057 [US3] Validar a faixa do percentual — opcional; quando informado, maior que zero e menor ou igual a cem — em `backend/processo_seletivo/editais/domain/perfis.py`

### Testes

- [ ] T058 [P] [US3] Configurar regra com fundamento, versão e percentual, salvar o Cronograma e recarregar: regras intactas e identidades da modalidade **e da regra** preservadas — o defeito de linha de base do `quickstart.md`, em `backend/tests/interface/test_compor.py`
- [ ] T059 [US3] Faixa do percentual recusada pela interface **e** pela API, provando que a regra está no domínio, em `backend/tests/unit/editais/test_perfis.py` e `backend/tests/contract/test_edital_draft_api.py`
- [ ] T060 [US3] Identificador de modalidade ou de regra de outro Perfil ou Edital é recusado com `409`, em `backend/tests/contract/test_edital_draft_api.py`
- [ ] T061 [P] [US3] Modalidades com percentual e fundamento aparecem na prévia e no documento publicado, em `backend/tests/interface/test_fluxo.py`
- [ ] T062 [P] [US3] Retificação endereça `normativeRule/percentage` pelo caminho existente, em `backend/tests/contract/test_enderecamento_api.py`

**Checkpoint**: demonstrável — duas modalidades sobrevivem a salvamentos sucessivos e aparecem no
documento.

---

## Phase 7: User Story 4 — Estruturar o conteúdo textual do Edital (Priority: P2)

**Goal**: revisar e complementar as seções textuais sem redigir o que o sistema já conhece.

**Independent Test**: alterar o texto de uma seção institucional, salvar, visualizar e encontrar a
alteração no documento junto das seções geradas.

**Dependency**: US2, que já entregou a forma de `sections` no conteúdo publicado. Esta fase muda a
**origem** do texto das seções textuais, não a forma.

- [ ] T063 [US4] Criar o modelo `SecaoEdital`, cuja chave primária é o mesmo `uuid5` do snapshot, com unicidade de `key` por Edital, em `backend/processo_seletivo/editais/models/secoes.py`, e a migration em `backend/processo_seletivo/editais/migrations/`
- [ ] T064 [US4] Fazer `edital_snapshot` usar o conteúdo persistido quando existir, e o texto do catálogo quando não, em `backend/processo_seletivo/publicacoes/application/publish_edital.py`
- [ ] T065 [US4] Gravar as seções textuais editadas, recusando chave fora do catálogo ou de seção gerada, em `backend/processo_seletivo/editais/application/draft.py`
- [ ] T066 [US4] Aceitar `sections` no payload do rascunho em `backend/processo_seletivo/editais/api/serializers.py`, e só então declarar `sections` em `RascunhoInput` em `specs/001-processo-seletivo-editais/contracts/openapi.yaml`
- [ ] T067 [US4] Acrescentar a etapa `Conteúdo` a `ETAPAS_COMPOSICAO`, distinguindo seções geradas de textuais, em `backend/processo_seletivo/interface/views.py`
- [ ] T068 [P] [US4] Criar `compor_conteudo.html` em `backend/processo_seletivo/interface/templates/interface/`, com área de texto por seção textual e indicação de origem nas geradas
- [ ] T069 [US4] Ler e preservar as seções textuais em `backend/processo_seletivo/interface/forms.py`

### Testes

- [ ] T070 [P] [US4] Editar seção textual, salvar e encontrar a alteração no documento, em `backend/tests/interface/test_compor.py`
- [ ] T071 [P] [US4] Alterar o Cronograma reflete na seção gerada sem sincronização manual, em `backend/tests/interface/test_fluxo.py`
- [ ] T072 [P] [US4] Chave fora do catálogo ou de seção gerada é recusada na gravação, em `backend/tests/contract/test_edital_draft_api.py`
- [ ] T073 [P] [US4] Retificação aceita `REPLACE /sections/id=<uuid>/content` de seção textual e recusa a mesma operação sobre seção gerada, por caminho inexistente, em `backend/tests/contract/test_enderecamento_api.py`
- [ ] T074 [P] [US4] A identidade de uma seção é a mesma antes e depois da edição e de republicações, em `backend/tests/contract/test_forma_publicada.py`

**Checkpoint**: demonstrável — texto institucional editado aparece no documento junto do conteúdo
gerado.

---

## Phase 8: Polish & Cross-Cutting Concerns

- [ ] T075 Regenerar seeds e fixtures afetados pela versão 2 do esquema, em `backend/processo_seletivo/processos/management/commands/seed_demo.py` e `backend/tests/`
- [ ] T076 Executar o roteiro de demonstração de `quickstart.md` de ponta a ponta, com dois atores, e corrigir o que a demonstração revelar
- [ ] T077 [P] Reavaliar `specs/006-elaboracao-completa-edital/checklists/requirements.md` contra o que foi implementado
- [ ] T078 [P] Conferir `backend/tests/contract/test_openapi_conformance.py` e `test_traceability.py` verdes após o delta de contrato
- [ ] T079 Conferir que nenhuma tabela append-only ganhou escrita e que o documento publicado permanece imutável, em `backend/tests/test_configuracao_producao.py`

---

## Dependencies

```text
Setup (T001)
  └── Foundational (T002)  ← precisa vir antes de pdf.py mudar
        ├── US0 (T003–T016)   independente
        └── US1 (T017–T025)   depende de T002
              ├── US2 (T026–T052)   produz a versão 2 inteira
              │     └── US4 (T063–T074)   depende da forma de sections, entregue pela US2
              └── US3 (T053–T062)
```

**Duas dependências reais, e ambas foram subestimadas na primeira versão deste arquivo.**

**US1 antecede US2, US3 e US4** — não por conveniência, como se dizia aqui antes, mas porque os
critérios de aceite delas exigem a prévia: FR-025 pede Etapas na prévia, FR-031 pede as modalidades,
FR-038 pede as seções, e T052, T061, T070 e T071 verificam justamente isso. Sem a US1, essas
histórias não têm como ser concluídas nem demonstradas.

**US4 depende da US2**, porque a forma canônica de `sections` entra junto com `stages`, sob pena de
existirem dois formatos declarando a mesma versão. US4 acrescenta a origem do texto e a interface,
não a forma.

US0, US2 e US3 são independentes entre si. Nenhuma outra história é independente da US1.

## Parallel Execution Examples

São 34 tarefas marcadas `[P]`, e a marcação foi conferida arquivo a arquivo: **duas tarefas `[P]` da
mesma fase nunca tocam o mesmo arquivo**. Onde tocavam — testes agrupados em `test_compor.py`,
`test_fluxo.py` e `test_limites_de_borda.py` — a marcação foi retirada em vez de os arquivos serem
partidos, porque partir arquivo de teste por conveniência de paralelismo espalha o mesmo assunto.

**US0**: T003 é template isolado e corre livre. Entre os testes, T011, T012, T013, T015 e T016 correm
juntos; T014 fica atrás de T012, mesmo arquivo.

**US2**: T026, T027, T028 e T032 tocam arquivos diferentes e correm juntas. T033 e T034 são o mesmo
arquivo e ficam sequenciais. Entre os testes, T044 a T048, T050, T051 e T052 correm em paralelo;
T049 fica atrás de T048.

**US3**: T053 e T054 são o mesmo arquivo e ficam sequenciais; T055, T056 e T057 correm com elas. Nos
testes, T058, T061 e T062 correm juntos; T059 e T060 compartilham `test_edital_draft_api.py` e ficam
sequenciais.

## Implementation Strategy

**MVP**: a US0 sozinha já é entregável e muda a percepção do sistema em horas. Não é a história de
maior valor — é a de maior valor por hora, e a única sem decisão de desenho pendente.

**Primeiro salto perceptível**: US1. Depois dela o sistema deixa de parecer um gerenciador de
estados, e as três histórias seguintes ganham verificação visual imediata.

**Ordem de entrega**: US0 → US1 → US2 → US3 → US4, uma por PR, cada um com a demonstração como
condição de merge. A ordem não é preferência: da US2 em diante, os critérios de aceite exigem a
prévia entregue pela US1. Suíte verde é necessária e não é suficiente: o princípio VI exige o cenário
navegável.

**O que não fazer**: nenhuma tarefa aqui autoriza criar repositório, DTO novo, serviço novo,
mecanismo de compatibilidade entre versões de esquema, motor de cotas, modelo reutilizável ou editor
rico. Encontrar oportunidade de abstração durante a implementação não autoriza incluí-la.
