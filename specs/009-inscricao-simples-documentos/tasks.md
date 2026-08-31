---

description: "Task list for feature implementation"
---

# Tasks: Inscrição Simples e Documentos do Candidato

**Input**: Design documents from `/specs/009-inscricao-simples-documentos/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/inscricao.md](./contracts/inscricao.md), [quickstart.md](./quickstart.md)

**Tests**: **sim, exigidos**. O princípio V da Constituição exige cobertura de regra crítica, e
nomeia documentos, elegibilidade, autorização e concorrência — que é metade desta feature. Os testes
vêm antes da implementação em cada história.

**Organization**: por história de usuário, na ordem das seis entregas da spec.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência)
- **[Story]**: US1 a US7, conforme a spec
- **Sufixo de letra** (`T053a`): tarefa acrescentada por revisão, inserida na posição de execução
  a que pertence. Mantém estáveis os identificadores já referenciados pela matriz de rastreabilidade

## Path Conventions

Aplicação web Django. Produção em `backend/processo_seletivo/`, testes em `backend/tests/`. Dois
apps nascem nesta feature — `inscricoes` (domínio) e `portal` (canal do candidato) —, e o
administrativo continua em `interface`.

> **⚠️ A base está atrás de `origin/main`.** Esta feature foi verificada contra `897b750`, e
> `origin/main` avançou para `035e555` com dois commits da `007` que tocam `editais/application/draft.py`,
> `editais/domain/perfis.py`, `interface/views.py`, `interface/templates/interface/base.html` e
> `interface/static/interface/remocao.js` — todos arquivos desta lista. Sincronizar a base **antes**
> de T008, T038 e T039; e a rubrica de acessibilidade agora tem provas em
> `backend/tests/interface/test_acessibilidade.py`, que T111 herda.
>
> **⚠️ A dependência que governa o encadeamento.** A **entrega 2** escreve em
> `publicacoes/infrastructure/pdf.py`, o mesmo arquivo onde a `008` vive inteira. A `008` **não**
> toca a camada canônica, então não há disputa de versão — há disputa de arquivo, e o compositor
> triplicou de tamanho nela. A entrega 2 parte da `008` integrada; as entregas 1, 3, 4, 5 e 6 não
> dependem dela em nada.

---

## Phase 1: Setup

**Purpose**: os dois canais existirem, com configuração e linguagem visual compartilhada.

- [X] T001 [P] Criar o esqueleto do app em `backend/processo_seletivo/inscricoes/` — `__init__.py`, `apps.py`, `models.py`, `domain/__init__.py`, `application/__init__.py`, `migrations/__init__.py`
- [X] T002 [P] Criar o esqueleto do app em `backend/processo_seletivo/portal/` — `__init__.py`, `apps.py`, `urls.py`, `views.py`, `templates/portal/`, `static/portal/`
- [X] T003 Registrar `processo_seletivo.inscricoes` e `processo_seletivo.portal` em `INSTALLED_APPS` de `backend/config/settings/base.py`
- [X] T004 Incluir o roteamento público sob `selecoes/` em `backend/config/urls.py`, fora de `gestao/` e de `api/v1/`
- [X] T005 Declarar `ARQUIVOS_CANDIDATOS_RAIZ`, `ARQUIVOS_CANDIDATOS_LIMITE_BYTES` (padrão 10 MB) e `PORTAL_IDENTIDADE_DEMO` em `backend/config/settings/base.py`, no formato das configurações existentes lidas de ambiente
- [X] T006 Acrescentar as duas guardas `_exigir` em `backend/config/settings/production.py` — raiz de arquivos declarada, absoluta e fora da árvore estática; provedor de demonstração desligado
- [X] T007 [P] Teste das guardas em `backend/tests/unit/test_configuracao_producao.py`, no padrão das que já cobrem o seletor institucional
- [X] T008 [P] Extrair o bloco de tokens de `backend/processo_seletivo/interface/templates/interface/base.html` para `backend/processo_seletivo/shared/templates/shared/_tokens.css.html` e incluí-lo no `<style>` da base administrativa, sem mudar nenhuma regra
- [X] T009 [P] Criar `backend/processo_seletivo/portal/templates/portal/base.html` incluindo a parcial de tokens, com consultas de mídia, link de pular, foco visível e nenhum elemento de gestão

**Checkpoint**: o canal público responde, ainda vazio, e as duas bases compartilham a mesma paleta.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: o que toda história do portal consome. Nenhuma história começa antes.

**⚠️ CRITICAL**: bloqueia as entregas 1 a 6.

- [X] T010 Seletor de leitura pública em `backend/processo_seletivo/publicacoes/application/selectors.py` — Editais publicamente consultáveis com a respectiva versão consolidada vigente, sem tocar tabela de elaboração
- [X] T011 [P] Decorador de resposta privada (`no-store`) em `backend/processo_seletivo/shared/http.py`, aplicável a view de template e a resposta de arquivo
- [X] T012 [P] Fixture compartilhada de Edital publicado com dois Perfis e uma modalidade reservada em `backend/tests/fixtures/`, reutilizável por integração e aceitação
- [X] T013 [P] Teste do seletor em `backend/tests/integration/publicacoes/test_selecoes_publicas.py` — Edital não publicado não aparece; alteração no rascunho não muda o que o seletor devolve (FR-011)

**Checkpoint**: fundação pronta. As entregas podem começar.

---

## Phase 3: Entrega 1 — User Story 1, parte consultável (Priority: P1) 🎯 MVP

**Goal**: a seleção publicada é encontrável e compreensível por quem não é da instituição.

**Independent Test**: em janela anônima, ler título, unidade, Perfis, vagas, localidade e requisitos
e abrir o documento oficial — sem `/gestao/` e sem identificação.

> A US1 **não se conclui aqui**: situação temporal e convite por vaga dependem da designação do
> período e chegam na entrega 2. É o que a spec declara na própria história.

### Tests for User Story 1

- [X] T014 [P] [US1] Teste de integração da vitrine em `backend/tests/integration/portal/test_vitrine.py` — lista só o publicamente consultável, sem identificação, sem dado administrativo
- [X] T015 [P] [US1] Teste do detalhe em `backend/tests/integration/portal/test_detalhe_selecao.py` — Perfis, vagas, localidade e requisitos vêm da versão vigente; alterar o rascunho não muda a página
- [X] T016 [P] [US1] Teste em `backend/tests/integration/portal/test_documento_oficial.py` — o link do documento publicado é alcançável do detalhe

### Implementation for User Story 1

- [X] T017 [US1] View e template da vitrine em `backend/processo_seletivo/portal/views.py` e `templates/portal/vitrine.html`
- [X] T018 [US1] View e template do detalhe da seleção em `backend/processo_seletivo/portal/views.py` e `templates/portal/selecao.html`
- [X] T019 [P] [US1] Regras responsivas da vitrine e do detalhe em `templates/portal/base.html` — 375 px sem rolagem horizontal
- [X] T020 [US1] Percorrer a entrega 1 do [quickstart.md](./quickstart.md) no navegador, em janela anônima

**Checkpoint**: a porta existe. Uma pessoa de fora encontra a seleção e lê o Edital.

---

## Phase 4: Entrega 2 — User Story 2, e a US1 se completa (Priority: P1)

**Goal**: o Edital passa a declarar quando as inscrições abrem e o que o candidato precisa
apresentar — no domínio, no conteúdo publicado e no documento.

**Independent Test**: declarar período e três documentos com aplicabilidades distintas, publicar,
encontrar os três no documento e no conteúdo publicado, e alcançá-los por Retificação.

> **⛔ Bloqueio**: parte da `008` integrada na base. Ver o aviso em *Path Conventions*.

### Tests for User Story 2

- [X] T021 [US2] Confirmar a base: ramo rebaseado sobre `origin/main` **e** `008` integrada, com o compositor em sua forma final — verificação de base, não código
- [X] T022 [P] [US2] Teste de contrato em `backend/tests/contract/test_forma_publicada.py` — `DocumentoExigidoPublicado` conferido contra `specs/001-processo-seletivo-editais/contracts/openapi.yaml`
- [X] T023 [P] [US2] Teste de contrato do campo `isRegistrationPeriod` em `EventoPublicado`, em `backend/tests/contract/test_forma_publicada.py`
- [X] T024 [P] [US2] Teste de endereçamento em `backend/tests/contract/test_enderecamento_api.py` — `/documentRequirements/id=<uuid>/required` e `/schedule/id=<uuid>/isRegistrationPeriod` aceitos; endereçamento por posição recusado
- [X] T025 [P] [US2] Teste em `backend/tests/unit/editais/test_validacao_inscricao.py` — dois Eventos marcados produzem achado impeditivo
- [X] T026 [P] [US2] Teste em `backend/tests/unit/editais/test_validacao_inscricao.py` — nenhum Evento marcado produz **aviso**, e a publicação segue (FR-004)
- [X] T027 [P] [US2] Teste em `backend/tests/unit/editais/test_validacao_inscricao.py` — requisito cuja modalidade não pertence ao Perfil declarado produz achado impeditivo
- [X] T028 [P] [US2] Teste da constraint parcial em `backend/tests/integration/editais/test_periodo_inscricoes.py` — o banco recusa a segunda marca no mesmo Cronograma
- [X] T029 [P] [US2] Teste de composição em `backend/tests/unit/publicacoes/test_pdf.py` — a seção enuncia os três documentos, identifica os adicionais por modalidade, e não é composta quando a coleção está vazia
- [X] T030 [P] [US2] Teste de integração da etapa do assistente em `backend/tests/integration/interface/test_compor_inscricao.py` — adicionar, editar, remover, ordenar e indicar aplicabilidade

### Implementation for User Story 2

- [X] T031 [US2] Acrescentar os esquemas `DocumentoExigidoPublicado` e o campo do Evento em `specs/001-processo-seletivo-editais/contracts/openapi.yaml`
- [X] T032 [P] [US2] Campo `is_registration_period` com `UniqueConstraint` parcial em `backend/processo_seletivo/editais/models/cronograma.py`
- [X] T033 [P] [US2] Modelo `DocumentoExigido` em `backend/processo_seletivo/editais/models/documentos.py`, exportado em `models/__init__.py`
- [X] T034 [US2] Migration em `backend/processo_seletivo/editais/migrations/` com o campo, a tabela e as constraints
- [X] T035 [P] [US2] Validação de forma e de aplicabilidade em `backend/processo_seletivo/editais/domain/documentos.py`
- [X] T036 [P] [US2] `DOCUMENTO_EXIGIDO_PUBLICADO`, `Campo("isRegistrationPeriod", bool)` e as duas conferências novas em `backend/processo_seletivo/editais/domain/validation.py`
- [X] T037 [P] [US2] Entrada `documentos-exigidos` no catálogo de `backend/processo_seletivo/editais/domain/secoes.py`, gerada, com origem em `documentRequirements`, após a seção `inscricao`
- [X] T038 [US2] `replace_draft` grava a coleção nova e recusa identidade alheia, em `backend/processo_seletivo/editais/application/draft.py`
- [X] T039 [US2] Leitura da etapa em `backend/processo_seletivo/interface/forms.py` e registro em `ETAPAS_COMPOSICAO`, `ETAPAS_GRAVAVEIS`, `COLECAO_DA_ETAPA` e `LEITURA_DA_ETAPA` de `backend/processo_seletivo/interface/views.py`
- [X] T040 [US2] Template `backend/processo_seletivo/interface/templates/interface/compor_inscricao.html` — designação do Evento e linhas de documento
- [X] T041 [US2] Fragmento de linha de documento em `interface/views.py` e `interface/urls.py`, reusando `fragmentos/remover` e `ordenacao.js`
- [X] T042 [US2] Snapshot ganha `isRegistrationPeriod` e `documentRequirements`, e `SCHEMA_VERSION` passa a 4, em `backend/processo_seletivo/publicacoes/application/publish_edital.py` e `backend/processo_seletivo/shared/canonical.py`
- [X] T043 [US2] `/documentRequirements` em `COLECOES_COM_CHAVE` de `backend/processo_seletivo/publicacoes/domain/colecoes.py`
- [X] T044 [US2] Compositor `_documentos_exigidos` e registro em `_CORPO_GERADO` de `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`
- [X] T045 [US1] Situação futura, aberta e encerrada, com data, em `backend/processo_seletivo/portal/views.py`, `templates/portal/vitrine.html` **e** `templates/portal/selecao.html` — período e situação são colunas da listagem por FR-013, não só do detalhe
- [X] T046 [P] [US1] Teste em `backend/tests/integration/portal/test_situacao_inscricoes.py` — os três estados derivam do Evento marcado, **na listagem e no detalhe**; sem marca, a seleção não recebe inscrições; e, encerrado o período, a página continua consultável (FR-017)
- [X] T047 [US2] Atualizar `backend/processo_seletivo/processos/management/commands/seed_demo.py` para declarar período e os três documentos, e regenerar as fixtures de snapshot dos testes
- [X] T048 [US2] Percorrer a entrega 2 do [quickstart.md](./quickstart.md), inclusive a Retificação sobre as duas formas novas

**Checkpoint**: o Edital governa a inscrição, e a US1 está inteira.

---

## Phase 5: Entrega 3 — User Story 3 (Priority: P1)

**Goal**: o candidato se identifica, volta para onde estava e continua de onde parou.

**Independent Test**: chegar pela vaga, identificar-se, voltar à mesma vaga com os dados
preenchidos; sair, voltar e encontrar `Continuar inscrição`.

### Tests for User Story 3

- [ ] T049 [P] [US3] Teste em `backend/tests/integration/portal/test_identidade_candidato.py` — chave de sessão própria; identidade institucional não identifica no portal, e vice-versa
- [ ] T050 [P] [US3] Teste em `backend/tests/integration/portal/test_identidade_candidato.py` — após identificar-se, o retorno é a vaga de origem
- [ ] T051 [P] [US3] Teste em `backend/tests/integration/inscricoes/test_rascunho.py` — abrir duas vezes o mesmo Perfil leva à mesma Inscrição
- [ ] T051a [P] [US3] Teste em `backend/tests/integration/inscricoes/test_rascunho.py` — não existe caminho que troque o Perfil de uma Inscrição, nem pela tela nem por POST forjado; concorrer a outro Perfil é abrir outra inscrição (FR-030). *É a decisão que dispensa reconciliação de documentos: violada em silêncio, T075 e T080 passam a ter um caso que ninguém desenhou.*
- [ ] T052 [P] [US3] Teste de constraint em `backend/tests/integration/inscricoes/test_unicidade.py` — o banco recusa a segunda Inscrição da mesma identidade no mesmo Edital e Perfil, em qualquer estado
- [ ] T053 [P] [US3] Teste em `backend/tests/authorization/test_titularidade.py` — o rascunho de outra identidade não é alcançável por endereço
- [ ] T053a [P] [US3] Teste em `backend/tests/integration/portal/test_inicio_fora_do_periodo.py` — iniciar inscrição pelo endereço direto é recusado quando o período é futuro, está encerrado ou não foi designado; conhecer a URL não contorna FR-019

### Implementation for User Story 3

- [ ] T054 [US3] `backend/processo_seletivo/portal/identidade.py` — eixo próprio, chave de sessão distinta, provedor de demonstração rotulado
- [ ] T055 [US3] Modelo `Inscricao` em `backend/processo_seletivo/inscricoes/models.py`, com as constraints e o `save()` que recusa alterar o que é imutável
- [ ] T056 [US3] Migration em `backend/processo_seletivo/inscricoes/migrations/` com a tabela `Inscricao` e suas constraints
- [ ] T057 [US3] `backend/processo_seletivo/inscricoes/domain/titularidade.py` — quem pode ver o quê
- [ ] T058 [US3] `backend/processo_seletivo/inscricoes/application/rascunho.py` — abrir ou retomar, gravar campos, construir o ator do candidato com permissões vazias, e **recusar a abertura fora do período**, no servidor, antes de qualquer escrita
- [ ] T059 [US3] View e template `Sua inscrição` com dados pessoais e bloco de concorrência condicional, em `portal/views.py` e `templates/portal/inscricao.html`
- [ ] T045a [US1] Convite `Inscrever-se nesta vaga` por Perfil em `backend/processo_seletivo/portal/templates/portal/selecao.html`, apontando para o início da inscrição — **completa a US1**. *Viaja aqui, e não na entrega 2, porque é aqui que o destino nasce: um convite para uma rota inexistente é pior do que a ausência dele.*
- [ ] T045b [P] [US1] Teste em `backend/tests/integration/portal/test_convite_por_vaga.py` — o convite aparece com o período aberto, não aparece fora dele, e leva ao início da inscrição já com aquele Perfil
- [ ] T060 [US3] `Continuar inscrição` no detalhe da seleção, em `backend/processo_seletivo/portal/views.py` e `templates/portal/selecao.html`
- [ ] T061 [US3] Auditoria da criação da Inscrição em `backend/processo_seletivo/inscricoes/application/rascunho.py`, pelo `record_event` existente
- [ ] T062 [US3] Percorrer a entrega 3 do [quickstart.md](./quickstart.md), nas duas janelas

**Checkpoint**: existe titular, existe rascunho, e os dois eixos de identidade não se confundem.

---

## Phase 6: Entrega 4 — User Story 4 (Priority: P1)

**Goal**: o candidato envia os documentos que lhe cabem, vendo quanto falta e sem perder trabalho.

**Independent Test**: com três requisitos e aplicabilidades distintas, o candidato de ampla
concorrência recebe dois pedidos, envia dois PDFs e vê `2 de 2`; um envio recusado não apaga nada.

### Tests for User Story 4

- [ ] T063 [P] [US4] Teste de unidade da aplicabilidade em `backend/tests/unit/inscricoes/test_aplicabilidade.py` — as quatro combinações, e nenhuma quinta; e um Perfil sem modalidade declarada no conteúdo publicado não faz nascer modalidade de ampla concorrência alguma (FR-039)
- [ ] T064 [P] [US4] Teste de unidade da aceitação de arquivo em `backend/tests/unit/inscricoes/test_arquivos.py` — assinatura `%PDF-`, nome físico opaco, resumo calculado, e **limite lido da configuração**: alterar `ARQUIVOS_CANDIDATOS_LIMITE_BYTES` muda o que é aceito, provando que não está fixado em código (FR-046)
- [ ] T065 [P] [US4] Teste em `backend/tests/unit/inscricoes/test_arquivos.py` — imagem renomeada para `.pdf` é recusada com mensagem que ensina a converter
- [ ] T066 [P] [US4] Teste em `backend/tests/integration/inscricoes/test_envio_de_arquivo.py` — envio válido persiste sem `Salvar`; recusa não apaga arquivo nem campo já válido
- [ ] T066a [P] [US4] Teste em `backend/tests/authorization/test_requisito_alheio.py` — envio forjado para requisito de outro Perfil ou de outra modalidade é recusado no servidor, ainda que a tela nunca o tenha oferecido (FR-044)
- [ ] T067 [P] [US4] Teste de constraint em `backend/tests/integration/inscricoes/test_envio_de_arquivo.py` — um arquivo por requisito; substituir sobrescreve e descarta o anterior
- [ ] T068 [P] [US4] Teste em `backend/tests/authorization/test_arquivo_do_candidato.py` — arquivo não é entregue por endereço, nem a outro candidato
- [ ] T069 [P] [US4] Teste em `backend/tests/integration/inscricoes/test_mudanca_de_modalidade.py` — a confirmação enumera o que será descartado, e nada some sem ela

- [ ] T069a [P] [US4] Teste em `backend/tests/javascript/portal.test.js`, registrado em `backend/tests/test_javascript.py` — o script do portal não escreve em `localStorage` nem em `sessionStorage` (FR-042). *O `rascunho.js` do elaborador cobre o caso oposto e é o precedente a não imitar aqui: com CPF e documentos, nenhum prazo compensa o risco numa máquina compartilhada.*

### Implementation for User Story 4

- [ ] T070 [US4] Armazenamento privado em `backend/processo_seletivo/inscricoes/storage.py`, com raiz configurada e nome físico derivado da Inscrição e do requisito
- [ ] T071 [US4] Modelo `DocumentoSubmetido` em `backend/processo_seletivo/inscricoes/models.py`, com a unicidade por inscrição e requisito
- [ ] T072 [US4] Migration em `backend/processo_seletivo/inscricoes/migrations/` com a tabela `DocumentoSubmetido` e sua unicidade
- [ ] T073 [P] [US4] `backend/processo_seletivo/inscricoes/domain/aplicabilidade.py` — função pura sobre o conteúdo publicado
- [ ] T074 [P] [US4] `backend/processo_seletivo/inscricoes/domain/arquivos.py` — aceitação, limite, nome físico, resumo, recusas com significado
- [ ] T075 [US4] Anexar, substituir e remover em `backend/processo_seletivo/inscricoes/application/rascunho.py`, recusando requisito que não se aplique àquela inscrição e período fechado — a aplicabilidade é conferida no servidor a cada envio, não só ao montar a tela
- [ ] T076 [US4] Bloco de documentos com contagem `n de m` em `templates/portal/inscricao.html`, listando só o aplicável
- [ ] T077 [US4] Envio por requisito em requisição própria, com fragmento de resposta, em `portal/views.py` e `portal/urls.py`
- [ ] T078 [US4] Progresso de envio e aviso de não fechar a página em `backend/processo_seletivo/portal/static/portal/envio.js`, pelo evento de progresso do htmx
- [ ] T079 [US4] Entrega do próprio documento ao titular em `backend/processo_seletivo/portal/arquivos.py` — mediada, `inline`, `no-store`, em streaming
- [ ] T080 [US4] Confirmação de descarte na mudança de modalidade, em `portal/views.py` e template próprio
- [ ] T081 [US4] Auditoria de anexar, substituir e remover antes do envio, em `backend/processo_seletivo/inscricoes/application/rascunho.py`
- [ ] T082 [US4] Percorrer a entrega 4 do [quickstart.md](./quickstart.md), inclusive com rede limitada, em 375 px e por teclado

**Checkpoint**: o arquivo chega ligado ao requisito que atende, e o trabalho do candidato não se perde.

---

## Phase 7: Entrega 5 — User Story 5 (Priority: P1)

**Goal**: revisar, aceitar as declarações, enviar e receber protocolo.

**Independent Test**: enviar uma inscrição completa e obter protocolo; repetir o envio e não
produzir a segunda; retificar o Edital com rascunho aberto e ver o aviso — uma vez.

### Tests for User Story 5

- [ ] T083 [P] [US5] Teste em `backend/tests/integration/inscricoes/test_submissao.py` — a revalidação do envio percorre os dez eixos de FR-060: período, Edital publicamente válido, versão, Perfil, modalidade, aplicabilidade dos documentos, obrigatórios presentes, formato e tamanho dos arquivos, unicidade e declarações
- [ ] T083a [P] [US5] Teste em `backend/tests/integration/inscricoes/test_submissao.py` — estado que se tornou inválido **entre o envio do arquivo e o envio da inscrição** é recusado: Edital que deixou de ser publicamente válido, requisito que deixou de ser aplicável e arquivo cujo registro não corresponde mais ao que o conteúdo vigente exige
- [ ] T084 [P] [US5] Teste em `backend/tests/integration/inscricoes/test_submissao.py` — o mesmo envio repetido produz uma única Inscrição enviada
- [ ] T085 [P] [US5] Teste de unidade em `backend/tests/unit/inscricoes/test_protocolo.py` — formato, alfabeto sem caracteres ambíguos, e unicidade sob colisão forçada
- [ ] T086 [P] [US5] Teste em `backend/tests/integration/inscricoes/test_versao_reconhecida.py` — Retificação vigente avisa e exige confirmação; confirmada, não avisa de novo; nova versão volta a avisar
- [ ] T086a [P] [US5] Teste em `backend/tests/integration/inscricoes/test_versao_reconhecida.py` — a Retificação **preserva** dados e arquivos ainda aplicáveis e **confirma** o descarte dos que deixaram de ser exigidos, pela mesma regra de FR-031; nada some em silêncio e nada é reaproveitado em silêncio
- [ ] T087 [P] [US5] Teste em `backend/tests/integration/inscricoes/test_imutabilidade.py` — enviada, a Inscrição e seus arquivos não mudam
- [ ] T088 [P] [US5] Teste de aceitação em `backend/tests/acceptance/test_jornada_do_candidato.py` — o percurso do `SC-017`, com dois atores

### Implementation for User Story 5

- [ ] T089 [P] [US5] `backend/processo_seletivo/inscricoes/domain/protocolo.py`
- [ ] T090 [US5] `backend/processo_seletivo/inscricoes/application/submissao.py` — revalidação integral, idempotência por `reserve()`, `compare_and_swap`, protocolo, versão aceita e declarações
- [ ] T091 [US5] Versão reconhecida atualizada a cada confirmação, em `application/rascunho.py`
- [ ] T092 [US5] View e template da revisão, com `Editar` por bloco, em `portal/views.py` e `templates/portal/revisao.html`
- [ ] T093 [US5] Aviso de Edital atualizado, com preservação do que continua aplicável, em `templates/portal/revisao.html`
- [ ] T094 [US5] Envio e comprovante imprimível em `portal/views.py` e `templates/portal/comprovante.html`, com `no-store`
- [ ] T095 [US5] Auditoria do envio em `backend/processo_seletivo/inscricoes/application/submissao.py` — Inscrição, Edital e versão, Perfil e instante, sem CPF completo
- [ ] T096 [US5] Percorrer a entrega 5 do [quickstart.md](./quickstart.md)

**Checkpoint**: a inscrição produz efeito administrativo, uma vez só, sob versão conhecida.

---

## Phase 8: Entrega 5 — User Story 7, voltar depois (Priority: P2)

**Goal**: quem já enviou reencontra o comprovante; quem não terminou reencontra a inscrição.

**Independent Test**: enviar, sair, voltar identificado à seleção e alcançar o comprovante.

- [ ] T097 [P] [US7] Teste em `backend/tests/integration/portal/test_retorno.py` — enviada oferece o comprovante; rascunho com período encerrado abre só para consulta
- [ ] T098 [US7] Estado do candidato no detalhe da seleção — `Continuar inscrição`, `Ver comprovante` ou nada — em `portal/views.py` e `templates/portal/selecao.html`

**Checkpoint**: o candidato reencontra o que fez, sem portal do candidato.

---

## Phase 9: Entrega 6 — User Story 6 (Priority: P1)

**Goal**: a equipe consulta o que chegou e abre cada documento dentro do sistema.

**Independent Test**: com inscrições recebidas, localizar uma candidata pela lista, abrir o detalhe e
visualizar cada documento sob o requisito que atende — sem baixar nada.

### Tests for User Story 6

- [ ] T099 [P] [US6] Teste em `backend/tests/integration/interface/test_inscricoes_recebidas.py` — total, colunas mínimas e CPF na máscara canônica `***.456.789-**`, com os dígitos ocultos ausentes do HTML
- [ ] T100 [P] [US6] Teste em `backend/tests/integration/interface/test_inscricoes_recebidas.py` — o detalhe agrupa cada documento sob o requisito, com o nome original
- [ ] T101 [P] [US6] Teste em `backend/tests/authorization/test_consulta_administrativa.py` — ator sem permissão ou de outro escopo não alcança lista, detalhe nem arquivo
- [ ] T102 [P] [US6] Teste em `backend/tests/integration/inscricoes/test_integridade_do_arquivo.py` — resumo divergente recusa a entrega como íntegra e registra o fato
- [ ] T103 [P] [US6] Teste em `backend/tests/integration/interface/test_sem_avaliacao.py` — nenhuma tela oferece deferimento, nota, parecer, classificação ou download em lote

### Implementation for User Story 6

- [ ] T104 [US6] Lista `Inscrições` no contexto do Edital, em `backend/processo_seletivo/interface/views.py`, `urls.py` e `templates/interface/inscricoes.html`
- [ ] T105 [US6] Detalhe da inscrição, com documentos agrupados por requisito e a versão aceita visível, em `templates/interface/inscricao_detalhe.html`
- [ ] T106 [US6] Entrega institucional do documento em `backend/processo_seletivo/interface/views.py` — exibição `inline` com verificação do resumo em streaming, e **baixar como ação secundária individual** (`attachment`), sem download em lote (FR-069)
- [ ] T107 [US6] Aplicar o decorador de `backend/processo_seletivo/shared/http.py` às duas telas e à entrega do arquivo em `backend/processo_seletivo/interface/views.py`
- [ ] T108 [US6] Percorrer a entrega 6 do [quickstart.md](./quickstart.md)

**Checkpoint**: o Drive e a planilha deixam de ser necessários para conferir o que chegou.

---

## Phase 10: Polish & Cross-Cutting Concerns

- [ ] T109 [P] Varredura de PII em `backend/processo_seletivo/shared/observability.py` e nos pontos de log das duas jornadas — nenhum CPF completo, nenhum nome de arquivo, nenhum conteúdo
- [ ] T110 [P] Conferir `no-store` em toda resposta com dado pessoal e sua ausência na vitrine, por teste em `backend/tests/integration/portal/test_respostas_privadas.py`
- [ ] T111 [P] Percurso do candidato por teclado e leitor de tela em 375 px, conferido contra a rubrica de `backend/tests/interface/test_acessibilidade.py`, estendida ao portal, e registrado no [quickstart.md](./quickstart.md)
- [ ] T112 [P] Registrar o gate de retenção de dados pessoais em `specs/009-inscricao-simples-documentos/quickstart.md` e no README do backend, como precondição de dados reais
- [ ] T113 Rodar a suíte contra PostgreSQL — `TEST_DB_ENGINE=postgresql` — e conferir a contagem de skips
- [ ] T114 Executar o [quickstart.md](./quickstart.md) inteiro, terminando no percurso emblemático do `SC-017`

---

## Matriz de rastreabilidade SC → verificação

| Critério | Onde é provado |
|---|---|
| SC-001, SC-003 | T014, T015, T045, T046 |
| SC-002 | T025, T026, T028, T046, T053a |
| SC-004, SC-005 | T049, T059, T063 |
| FR-030 — o Perfil não muda dentro da inscrição | T051a |
| FR-039 — nenhuma ampla concorrência artificial | T063 |
| SC-006 | T063, T066a, T076 |
| SC-007 | T065, T066 |
| SC-008 | T051, T066 |
| SC-009, SC-009a | T086, T086a |
| SC-010 | T052, T084 |
| SC-011 | T083, T083a |
| SC-012 | T085, T094 |
| SC-013, SC-014 | T099, T100 |
| SC-014a | T102 |
| SC-015 | T068, T066a, T101 |
| FR-042 — nada do candidato no navegador | T069a |
| FR-017 — consultável depois de encerrada | T046 |
| FR-069 — baixar como ação secundária | T106 |
| SC-016, SC-017 | T088, T114 |
| SC-UX-001 a SC-UX-003 | T059, T076, T092 |
| SC-UX-004, SC-UX-005 | T019, T082, T111 |
| SC-UX-006 | T078, T082 |
| SC-UX-007 | T066, T092 |
| SC-UX-008 | T111 |

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Fase 1)**: sem dependência.
- **Foundational (Fase 2)**: depende da Fase 1. Bloqueia todas as histórias.
- **Entrega 1 / US1 parte consultável (Fase 3)**: depende da Fase 2. **Não** depende da `008`.
- **Entrega 2 / US2 (Fase 4)**: depende da Fase 3 e da **`008` integrada**. Conclui a US1.
- **Entrega 3 / US3 (Fase 5)**: depende da Fase 4 — o candidato escolhe a vaga pelo convite, que
  nasce na entrega 2.
- **Entrega 4 / US4 (Fase 6)**: depende da Fase 5 — o arquivo pertence a um rascunho.
- **Entrega 5 / US5 (Fase 7)** e **US7 (Fase 8)**: dependem da Fase 6 — não se envia inscrição
  incompleta.
- **Entrega 6 / US6 (Fase 9)**: depende da Fase 7 — é preciso haver inscrição enviada para
  consultar.
- **Polish (Fase 10)**: depende de tudo.

### O grafo real

Esta feature é **mais encadeada que as anteriores**, e a honestidade sobre isso vale mais do que a
aparência de paralelismo: a jornada é sequencial por natureza — encontrar, identificar-se, preencher,
enviar, consultar. O paralelismo real está **dentro** de cada fase, entre testes e entre módulos de
domínio que vivem em arquivos distintos.

A exceção que importa: a **Fase 3 não depende da `008`** e pode correr enquanto a `008` fecha. É a
única fatia com essa propriedade, e é por isso que ela é a primeira.

### Parallel Opportunities

- Fase 1: T001, T002, T007, T008 e T009 em paralelo.
- Fase 2: T011, T012 e T013 em paralelo.
- Toda seção `Tests for User Story N`: todas as tarefas marcadas `[P]`, em arquivos distintos.
- Fase 4: T032, T033, T035, T036 e T037 tocam arquivos diferentes e estão marcadas `[P]`. T034 é a
  migration e depende dos dois modelos; T042, T043 e T044 são sequenciais entre si, porque o
  snapshot precisa existir antes de a coleção ser declarada e o compositor lê a forma final.
- Fase 6: T063 a T069a em paralelo, em arquivos distintos; T073 e T074 em paralelo; T070 a T072 são sequenciais.
- Fase 10: T109 a T112 em paralelo.

---

## Implementation Strategy

### MVP (Entrega 1)

1. Fase 1 e Fase 2.
2. Fase 3.
3. **Parar e validar**: a seleção publicada é encontrável e legível por quem é de fora, em janela
   anônima. É a primeira vez que o produto tem canal público, e ela vale sozinha.

### Entrega incremental

Cada fase seguinte termina em percurso navegável e é demonstrada antes da próxima começar. A
condição de merge é o percurso, não a contagem de testes.

A entrega 2 é a única com bloqueio externo e a única que incrementa a versão canônica. Ela é também
a que invalida os dados de demonstração publicados: T047 existe para que a demonstração seguinte não
comece quebrada.

### Notes

- `[P]` significa arquivos diferentes e nenhuma dependência pendente.
- Commitar por tarefa ou por grupo coerente; parar em cada checkpoint para validar.
- Nenhuma tarefa desta lista introduz dependência nova, motor genérico ou capacidade de comissão.
