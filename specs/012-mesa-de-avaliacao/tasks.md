---

description: "Task list for feature implementation"
---

# Tasks: Mesa de Avaliação

**Input**: Design documents from `/specs/012-mesa-de-avaliacao/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/mesa.md](./contracts/mesa.md), [quickstart.md](./quickstart.md)

**Tests**: **sim, exigidos**, e por três razões que a spec já fixou. O princípio V da Constituição
nomeia autorização e concorrência entre o que precisa de cobertura específica, e a 012 entrega as
duas. Metade do que ela promete só se prova pela recusa. E os oito cenários e três contraprovas de
elevação de T-001 são a condição para que Editais já publicados continuem retificáveis — se falharem, a feature quebra o
que já existe.

**Organization**: por história de usuário, na ordem das seis fatias da §24 da spec — e não em ordem
de camada. US1 a US4 são P1; US5 é P2.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência)
- **[Story]**: US1 a US5, conforme a spec

## Path Conventions

Aplicação web Django. Produção em `backend/processo_seletivo/`, testes em `backend/tests/`. Um app
nasce nesta feature — `avaliacoes` —, o incremento normativo mora onde conteúdo normativo sempre
morou, e as telas ficam em `interface`.

> **⚠️ A suíte precisa de PostgreSQL, e aqui o motivo tem três partes.** Sem
> `TEST_DB_ENGINE=postgresql` a suíte cai para SQLite **sem avisar**, e deixam de ser verificados: o
> índice único parcial de FR-074, a trigger append-only de `ConclusaoAvaliacao`, e o
> `select_for_update` herdado de `comando_de_comissao`. Rode como o [quickstart](./quickstart.md)
> manda, com `DB_NAME` próprio deste worktree.

> **⚠️ Todos os quatro modelos nascem na Foundational, numa migration só.** As histórias recebem
> comandos, telas e comportamento — nunca esquema. Foi assim que a primeira versão desta lista
> errou: pedia que a US1 verificasse impedimento e conclusão antes de as duas tabelas existirem.

> **⚠️ `comando_de_comissao` não audita.** Ele abre transação, bloqueia, reautoriza e reserva
> idempotência; quem grava a trilha é uma chamada explícita, como a 011 faz em `auditar()`. Os
> **sete** atos de FR-052 precisam de emissão própria, e nenhum deles põe pontuação ou parecer no
> evento (FR-054).

> **⚠️ Nenhuma tarefa desta lista escreve em linha gravada de `publicacoes`.** A elevação é leitura.
> Se alguma precisar de `UPDATE` em `VersaoConsolidada`, `Publicacao` ou `AlteracaoNormativa`, a
> decisão D-002 foi violada.

> **⚠️ Nenhuma tarefa desta lista chama `pode_atuar_na_etapa` dentro de laço.** Listagem usa
> `etapas_autorizadas`. Se aparecer uma, FR-048 foi violado.

---

## Phase 1: Setup

**Purpose**: o app novo existe, e o vocabulário deixa de colidir.

- [X] T001 Criar o app em `backend/processo_seletivo/avaliacoes/` com `__init__.py`, `apps.py`, `models.py`, `domain/`, `application/` e `migrations/`
- [X] T002 Registrar `processo_seletivo.avaliacoes` em `backend/config/settings/base.py`, com o comentário que diz por que é app próprio e não parte de `comissoes` (T-003)
- [X] T003 [P] Criar `backend/tests/unit/avaliacoes/` e `backend/tests/integration/avaliacoes/` com `__init__.py`
- [X] T004 [P] Renomear a rota da 011 em `backend/processo_seletivo/interface/urls.py` e `views.py`: `atribuicao` → `minha_etapa`, mantendo o caminho `minhas-etapas/<edital>/<etapa>` intacto, e ajustar as referências em `backend/processo_seletivo/interface/templates/interface/` (T-012)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: o incremento normativo, a elevação, **os quatro modelos** e as duas funções que todas
as histórias usam — autorização composta e emissão de trilha. **Nenhuma história começa antes.**

**⚠️ Esta fase toca conteúdo publicado. É a única que toca.**

### O incremento canônico

- [X] T005 [P] Acrescentar `evaluations_per_registration` e `maximum_score` a `EtapaAvaliacao` em `backend/processo_seletivo/editais/models/etapas.py`, com os dois `CheckConstraint` de faixa, e gerar a migration em `backend/processo_seletivo/editais/migrations/`
- [X] T006 [P] Acrescentar as duas propriedades a `EtapaPublicada` e `EtapaInput` em `specs/001-processo-seletivo-editais/contracts/openapi.yaml`, e atualizar a descrição da versão canônica que elas carregam
- [X] T007 Transcrever as duas em `ETAPA_PUBLICADA` em `backend/processo_seletivo/editais/domain/validation.py` (depende de T006: o teste de contrato falha se divergirem)
- [X] T008 [P] Aceitar os dois campos no serializer em `backend/processo_seletivo/editais/api/serializers.py` e na gravação do rascunho em `backend/processo_seletivo/editais/application/draft.py`
- [X] T009 Emitir os dois em `_stages()` em `backend/processo_seletivo/publicacoes/application/publish_edital.py` e subir `SCHEMA_VERSION` para 5 em `backend/processo_seletivo/shared/canonical.py`, com o comentário do incremento no padrão dos anteriores
- [X] T010 [P] Imprimir as duas linhas na Etapa do documento materializado em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`
- [X] T011 Verificar a coerência `minimumScore ≤ maximumScore` na validação de publicação em `backend/processo_seletivo/editais/domain/validation.py`, junto das outras faixas de Etapa

### A elevação (T-001, T-015)

- [X] T012 Criar `backend/processo_seletivo/publicacoes/domain/elevacao.py` com `elevar(conteudo)` e `elevar_alteracoes(changes)`, implementando a tabela de classificação de caminho de T-001 — `/stages/-`, `/stages/id=<uuid>`, `/stages`, `/stages/id=<uuid>/<campo>`, demais, `REMOVE`
- [X] T013 Aplicar a elevação nas fronteiras do fluxo de Retificação em `backend/processo_seletivo/publicacoes/application/retificacoes.py`: conteúdo-base em `create_retification`, `edit_retification` e `publish_retification`; `_original_version`; `_content_in_force`; e `_changes_payload`, que cobre `_acts` e a publicação de uma vez (depende de T012)
- [X] T014 Servir a projeção elevada à superfície de autoria (T-015): `campos_editaveis` e `diferencas` em `backend/processo_seletivo/interface/retificacao.py`, e as leituras de `base_snapshot.content` em `backend/processo_seletivo/interface/views.py` (depende de T012)
- [X] T015 Aceitar `expectedPreviousHash` nas **duas grafias** da mesma Etapa — literal e elevada — em `backend/processo_seletivo/publicacoes/domain/conflicts.py`, para os caminhos que a elevação alcança e **somente enquanto as duas denotarem a mesma norma**: a grafia literal só é candidata quando os campos novos da entidade atual ainda exprimem os valores legados — `evaluationsPerRegistration` igual a `1` ou ausente, e `maximumScore` nulo ou ausente. Declarada máxima ou quantidade, vale só o hash da forma vigente. Sem essa condição, remover os campos e comparar aceitaria o hash antigo depois de uma Retificação ter declarado a máxima, mascarando alteração normativa real (T-017) (depende de T012)

### Os quatro modelos, numa migration só

- [X] T016 Criar `Atribuicao` em `backend/processo_seletivo/avaliacoes/models.py`, com a unicidade parcial sobre ativo, o check de completude de inativação e os dois índices de §2 do data-model
- [X] T017 Criar `Avaliacao` e `ConclusaoAvaliacao` em `backend/processo_seletivo/avaliacoes/models.py`: `OneToOne` com a Atribuição, a tripla `identity_subject`/`etapa_id`/`inscricao_id`, o índice único parcial de FR-074, o check de completude de `CONCLUIDA`, e o `save`/`delete` append-only da conclusão
- [X] T018 Criar `Impedimento` em `backend/processo_seletivo/avaliacoes/models.py`, ancorado em `identity_subject`, com `motivo` obrigatório e **sem** coluna de estado (FR-099, T-009)
- [X] T019 Gerar a migration única de `avaliacoes` em `backend/processo_seletivo/avaliacoes/migrations/0001_initial.py`, com os quatro modelos e a trigger append-only de `ConclusaoAvaliacao` no estilo de `publicacoes/migrations/0007_imutabilidade_do_historico.py` (depende de T016, T017, T018)

### As duas funções que todas as histórias usam

- [X] T020 Criar `backend/processo_seletivo/avaliacoes/domain/previsao.py` com `avaliacoes_previstas()` e `pontuacao_maxima()` — o único lugar onde a ausência é interpretada (T-002)
- [X] T021 Criar `backend/processo_seletivo/avaliacoes/domain/autorizacao.py` com `pode_avaliar_inscricao()`, compondo `pode_atuar_na_etapa` da 011 com a existência de Atribuição ativa — **sem** reimplementar a primeira metade (depende de T016)
- [X] T022 Criar `auditar()` em `backend/processo_seletivo/avaliacoes/application/trilha.py` — módulo próprio, porque a 012 não traz invólucro de comando novo e o `__init__.py` da 011 existe para guardar o dela —, no molde de `comissoes/application/comissao.py`: grava `record_event` com a base efetivamente usada, `new_state=""` e `new_revision=None` para agregados sem ciclo, e grava `AtoAdministrativo` quando o ato exige motivo. **Nunca recebe pontuação nem parecer** (FR-054)

### Os testes que esta fase obriga

- [X] T023 [P] Teste de contrato da forma publicada nova em `backend/tests/contract/test_forma_publicada.py`, conferindo a transcrição contra o `openapi.yaml`
- [X] T024 [P] Testes unitários da elevação em `backend/tests/unit/avaliacoes/test_elevacao.py`: idempotência, `null` preservado, escalar intocado e cada linha da tabela de caminhos
- [X] T025 [P] Testes unitários da leitura da ausência em `backend/tests/unit/avaliacoes/test_previsao.py`: ausente, nulo e declarado
- [X] T026 Os **oito cenários e as três contraprovas** de T-001 em `backend/tests/integration/publicacoes/test_elevacao_de_versao.py` — quatro de histórico misto (sem retificação; `ADD` por `/stages/-`; `REPLACE` de Etapa inteira; `REPLACE` de campo) e quatro de deploy (v4 em elaboração; v4 homologada; criada depois sobre base v4; a mesma com `expectedPreviousHash` declarado nas duas grafias — projeção e literal —, **ambas aceitas**). Mais **três contraprovas**, cada uma exigindo `HASH_MISMATCH`: Retificação publicada no intervalo declarou `maximumScore`; declarou `evaluationsPerRegistration` diferente de 1; e alterou um campo que já existia em v4. Em todos, afirmar que o `content_hash` de toda `Publicacao` e `VersaoConsolidada` anterior permanece idêntico
- [X] T027 [P] Teste de regressão em `backend/tests/integration/publicacoes/test_leitura_publica_literal.py`: consulta pública, comprovante e documento de Publicação existente continuam servindo o conteúdo literal, não elevado (T-002)
- [X] T028 [P] Testes das garantias de banco em `backend/tests/integration/avaliacoes/test_constraints.py`, marcados `postgresql_only`: a unicidade parcial da Atribuição ativa; o índice único parcial de FR-074; e a trigger de `ConclusaoAvaliacao` recusando `UPDATE` e `DELETE` **direto no banco**, além do `save`/`delete` do modelo

**Checkpoint**: o Edital declara e publica as duas propriedades, Editais antigos continuam
retificáveis, as quatro tabelas existem com suas garantias, e a autorização composta responde.
Nenhuma tela nova ainda.

---

## Phase 3: User Story 1 — Distribuir as inscrições (P1)

**Goal**: a presidência distribui, em lote, as inscrições submetidas entre quem está alocado à
Etapa, e vê o que falta.

**Independent Test**: distribuir 400 inscrições entre dois avaliadores em poucas submissões;
recusar a excedente nomeando o número publicado; reenviar o lote e não criar nada.

- [X] T029 [US1] Implementar `distribuir()` em `backend/processo_seletivo/avaliacoes/application/distribuicao.py`, sobre `comando_de_comissao` da 011, com os seis invariantes de §2 do data-model
- [X] T030 [US1] Implementar a recusa de duas naturezas de FR-085 em `backend/processo_seletivo/avaliacoes/application/distribuicao.py`: regra sobre a linha acumula e relata; erro sobre o pedido levanta e desfaz o lote
- [X] T031 [US1] Implementar `remover_atribuicao()` em `backend/processo_seletivo/avaliacoes/application/distribuicao.py`, alcançando **apenas** Atribuição sem Avaliação concluída, também sobre `comando_de_comissao` (a recusa nomeada de FR-092 entra na Phase 7)
- [X] T032 [US1] Emitir a trilha de **atribuir** e de **remover atribuição** em `backend/processo_seletivo/avaliacoes/application/distribuicao.py`, via `auditar()`, um evento por Atribuição — inclusive no lote (FR-016, FR-052)
- [X] T033 [P] [US1] Implementar os seletores da organização do trabalho em `backend/processo_seletivo/avaliacoes/application/selectors.py`: carga por pessoa, déficit por inscrição e totais — por agregação, nunca por laço —, **paginados e filtráveis** por avaliador e por estado de cobertura (FR-049)
- [X] T034 [US1] Criar as views `distribuicao` e `remover_atribuicao` em `backend/processo_seletivo/interface/views.py`, autorizadas por `pode_gerir_comissao`, e os formulários do lote e da remoção em `backend/processo_seletivo/interface/forms.py`, com `idempotency_key` e o resultado declarado de FR-097
- [X] T035 [US1] Criar `backend/processo_seletivo/interface/templates/interface/distribuicao.html`, com **paginação e filtro** — mil inscrições não cabem numa tela (FR-049) —, e as três rotas de distribuição em `backend/processo_seletivo/interface/urls.py`
- [X] T036 [P] [US1] Testes de integração em `backend/tests/integration/avaliacoes/test_distribuicao.py`: teto recusado nomeando o número; impedimento e já-atribuída não derrubam o lote; Etapa inexistente derruba; um evento por atribuição; e a tela pagina e filtra com mil inscrições (FR-049)
- [X] T037 [P] [US1] Teste de idempotência e reautorização em `backend/tests/integration/avaliacoes/test_idempotencia_distribuicao.py`: reenvio devolve o desfecho sem criar Atribuição nem evento; chave repetida com conteúdo diferente é conflito; quem perdeu a presidência durante a transação não conclui o ato
- [X] T038 [P] [US1] Teste de autorização em `backend/tests/authorization/test_distribuicao.py`: quem não gere a comissão recebe 404; escopo divergente idem

**Checkpoint**: existe distribuição com autoria, em lote, auditada e idempotente.

---

## Phase 4: User Story 2 — A Mesa (P1)

**Goal**: cada avaliador abre sua lista de trabalho e vê todas e somente as inscrições que lhe foram
atribuídas.

**Independent Test**: avaliador com atribuições vê a lista paginada com contagens; alocado sem
atribuição abre a Mesa **vazia**; inscrição de outro responde 404.

- [X] T039 [US2] Implementar `mesa()` em `backend/processo_seletivo/avaliacoes/application/selectors.py`: uma chamada a `etapas_autorizadas`, uma consulta paginada com `select_related`, uma de contagens
- [X] T040 [US2] Ligar a Mesa à view em `backend/processo_seletivo/interface/views.py`: `minha_etapa` passa a chamar `mesa()`, aplicar filtro e paginação, e marcar a resposta com `marcar_como_privada` (FR-056)
- [X] T041 [US2] Substituir o aviso da 011 pela lista em `backend/processo_seletivo/interface/templates/interface/minha_etapa.html`, com filtro de pendentes/concluídas, contagens e o período previsto da Etapa (FR-078)
- [X] T042 [US2] Implementar o estado vazio de FR-023 em `backend/processo_seletivo/interface/templates/interface/minha_etapa.html` — explicando que ainda não há inscrições distribuídas, e nunca como falta de permissão
- [X] T043 [P] [US2] Teste de interface em `backend/tests/interface/test_mesa.py`: contagem, filtro, paginação, estado vazio e o cabeçalho `no-store`
- [X] T044 [P] [US2] Teste de autorização em `backend/tests/authorization/test_mesa.py`: alocado sem atribuição recebe a Mesa vazia com 200; sem alocação recebe 404; remover a alocação faz a Mesa sumir e devolvê-la restaura as mesmas atribuições
- [X] T045 [P] [US2] Teste em `backend/tests/integration/avaliacoes/test_revogacao_computada.py`: alocar, desalocar e remover membro **não escrevem em nenhuma linha de `Atribuicao`** (FR-069); e Atribuição cuja Etapa não está na Versão Consolidada vigente não concede acesso, pela mesma regra da alocação órfã (EC-011)

**Checkpoint**: o avaliador enxerga o seu trabalho, e só o dele.

---

## Phase 5: User Story 3 — A inscrição como instrumento de trabalho (P1)

**Goal**: o avaliador abre os documentos da inscrição atribuída, cada um sob o Documento Exigido que
atende, e cada abertura fica registrada.

**Independent Test**: abrir documento de inscrição atribuída funciona e deixa rastro; trocar o UUID
na URL responde 404; arquivo corrompido é recusa registrada.

- [X] T046 [US3] Criar a view da inscrição em `backend/processo_seletivo/interface/views.py`, autorizada por `pode_avaliar_inscricao`, montando os documentos por `requisitos_da_inscricao` sobre o conteúdo da **versão que a inscrição aceitou** (T-006), e marcando a resposta com `marcar_como_privada` — a página carrega dado pessoal, e não só o arquivo (FR-056)
- [X] T047 [US3] Criar a view do documento em `backend/processo_seletivo/interface/views.py`, reutilizando `copia_verificada`, `entregar`, `marcar_como_privada` e o registro de `CONSULTAR_DOCUMENTO`/`INTEGRIDADE` — **sem** chamar `inscricao:consultar` (D-005)
- [X] T048 [P] [US3] Criar `backend/processo_seletivo/interface/templates/interface/mesa_inscricao.html`, com identificação mínima e o CPF mascarado (FR-030)
- [X] T049 [US3] Acrescentar as duas rotas em `backend/processo_seletivo/interface/urls.py`
- [X] T050 [P] [US3] Teste de autorização em `backend/tests/authorization/test_documento_da_mesa.py`: inscrição não atribuída 404; alocação removida revoga; escopo divergente 404
- [X] T051 [P] [US3] Teste de integração em `backend/tests/integration/avaliacoes/test_documento.py`: a trilha registra ator, inscrição e requisito; hash divergente é recusa registrada; não há rota de lote; **as duas respostas — página e arquivo — trazem `no-store`**
- [X] T052 [P] [US3] Teste de regressão em `backend/tests/integration/inscricoes/test_consulta_administrativa_intocada.py`, nas **duas** direções de SC-017: a porta da 009 continua exatamente como era, e a autorização da Mesa não abre a consulta administrativa — avaliador com atribuição não lista as inscrições do Edital

**Checkpoint**: o documento é instrumento de trabalho, mediado e auditado.

---

## Phase 6: User Story 4 — Registrar a avaliação (P1) 🎯 **MVP**

**Goal**: o avaliador grava rascunho, é validado contra o que o Edital publicou, e conclui em ato
distinto.

**Independent Test**: a vertical inteira da §24 — presidente distribui, avaliador abre a Mesa, abre a
inscrição, registra e conclui, e quem não recebeu aquela inscrição não a alcança.

- [X] T053 [P] [US4] Criar `backend/processo_seletivo/avaliacoes/domain/pontuacao.py`: `normalizar()` para a **forma** — finitude, não-negatividade, escala e capacidade da coluna — e `validar()`, que acrescenta a máxima publicada. O rascunho cobra a primeira; a conclusão, as duas. **A nota mínima não recusa nada** (FR-033, FR-103)
- [X] T054 [US4] Implementar `gravar()` em `backend/processo_seletivo/avaliacoes/application/avaliacao.py`, com `compare_and_swap` sobre `revision` e a autorização composta verificada no servidor
- [X] T055 [US4] Implementar `concluir()` em `backend/processo_seletivo/avaliacoes/application/avaliacao.py`: lê a Versão Consolidada **dentro da transação**, valida contra ela, grava-a na Avaliação e escreve a `ConclusaoAvaliacao` (FR-071, FR-096)
- [X] T056 [US4] Implementar em `backend/processo_seletivo/avaliacoes/application/avaliacao.py` o parecer obrigatório quando a Etapa for eliminatória e a nota ficar abaixo do mínimo (FR-034), lendo o caráter da versão lida na mesma transação
- [X] T057 [US4] Implementar em `backend/processo_seletivo/avaliacoes/application/avaliacao.py` o reconhecimento explícito da mudança de versão entre a última gravação e a conclusão, **obrigatório no comando** — ausente, a conclusão é recusada, senão o cliente desligaria o requisito omitindo o campo (FR-073)
- [X] T058 [US4] Emitir a trilha de **gravar** e de **concluir** em `backend/processo_seletivo/avaliacoes/application/avaliacao.py`, via `auditar()`, **sem pontuação e sem parecer no evento** (FR-038, FR-054)
- [X] T059 [US4] Criar as views `avaliacao_gravar` e `avaliacao_concluir` em `backend/processo_seletivo/interface/views.py`, autorizadas por `pode_avaliar_inscricao`, e o formulário em `backend/processo_seletivo/interface/forms.py` com `expected_revision`
- [X] T060 [US4] Acrescentar o formulário e o aviso de conclusão fora do período previsto (FR-095) em `backend/processo_seletivo/interface/templates/interface/mesa_inscricao.html`, com as duas rotas em `backend/processo_seletivo/interface/urls.py`
- [X] T061 [P] [US4] Testes de integração em `backend/tests/integration/avaliacoes/test_avaliacao.py`: rascunho persistido; pontuação acima da máxima recusada; abaixo da mínima aceita com parecer obrigatório; concluída imutável para o avaliador; forma impossível recusada com mensagem — infinito, indefinido, expoente fora da coluna; rascunho aceitando acima da máxima e a conclusão recusando (FR-103); conclusão sem versão reconhecida recusada; duas abas do **mesmo** avaliador gravando com revisão obsoleta; e dois avaliadores **diferentes** concluindo a mesma inscrição ao mesmo tempo sem interferir um no outro (EC-007)
- [X] T062 [P] [US4] Teste realmente simultâneo em `backend/tests/integration/avaliacoes/test_primeira_gravacao_concorrente.py`, com duas threads e `transaction=True`: duas primeiras gravações na mesma Atribuição produzem uma gravação e uma recusa por revisão obsoleta — nunca `IntegrityError` por colisão do `OneToOne` (FR-081)
- [X] T063 [P] [US4] Teste em `backend/tests/integration/avaliacoes/test_versao_da_avaliacao.py`: Retificação consolidada no intervalo produz aviso, e a versão validada é a gravada; e Retificação que **remove a Etapa** com avaliações registradas não as apaga — elas permanecem como registro do que foi afirmado, e a Etapa deixa de conceder acesso (EC-004)
- [X] T064 [P] [US4] Teste em `backend/tests/integration/avaliacoes/test_trilha_da_avaliacao.py`: gravar e concluir geram evento, e **nenhum evento da 012 contém pontuação ou parecer** (FR-054)
- [X] T065 [US4] Teste de aceitação da vertical completa em `backend/tests/acceptance/test_mesa_de_avaliacao.py`, com três atores — inclusive a recusa de quem não recebeu a inscrição

**Checkpoint**: **MVP**. A vertical que a §24 declarou como primeira entrega significativa está de
pé, e nada nela produz resultado.

---

## Phase 7: User Story 5 — Impedimento, reabertura e a proteção do conjunto elegível (P2)

**Goal**: a presidência registra impedimento e reabre avaliação, e nenhum caminho comum consegue
escolher quais avaliações contam.

**Independent Test**: retirar pela via comum a Atribuição de quem já concluiu é recusado; o
impedimento inativa a Atribuição no mesmo ato e preserva a conclusão como inelegível; reabrir
preserva o que havia sido concluído.

- [X] T066 [US5] Implementar `registrar_impedimento()` em `backend/processo_seletivo/avaliacoes/application/impedimento.py`, sobre `comando_de_comissao`: cria a linha e inativa as Atribuições ativas do par
- [X] T067 [US5] Implementar em `backend/processo_seletivo/avaliacoes/application/impedimento.py` a contagem prévia que a confirmação declara — quantas Atribuições serão inativadas — antes de o ato ser confirmado (FR-041)
- [X] T068 [US5] Implementar a recusa de FR-092 em `remover_atribuicao()`, em `backend/processo_seletivo/avaliacoes/application/distribuicao.py`: retirar Atribuição sob Avaliação concluída pela via comum é recusado, nomeando os atos que teriam esse efeito e o que cada um exige
- [X] T069 [US5] Implementar `reabrir()` em `backend/processo_seletivo/avaliacoes/application/avaliacao.py`, sobre `comando_de_comissao`, partindo apenas de `CONCLUIDA`, com motivo obrigatório e `expected_revision`
- [X] T070 [US5] Emitir a trilha de **impedir** e de **reabrir** em `backend/processo_seletivo/avaliacoes/application/impedimento.py` e `avaliacao.py`, via `auditar()`, gravando também o `AtoAdministrativo` com motivo — um por Atribuição inativada. **Impedimento sem Atribuição ativa também é auditado**, e ali o agregado é o próprio `Impedimento`, porque não há Atribuição a que ancorar (FR-052, FR-093, T-016)
- [X] T071 [P] [US5] Implementar em `backend/processo_seletivo/avaliacoes/application/selectors.py` os três seletores do conjunto: `avaliacoes_elegiveis()`, que é o contrato herdado pela 013; as **inelegíveis**, com o ato, o autor e o motivo ao lado; e as **órfãs** (FR-093, EC-003, contrato §6)
- [X] T072 [US5] Criar as views de impedimento e reabertura em `backend/processo_seletivo/interface/views.py` e os formulários com motivo e `idempotency_key` em `backend/processo_seletivo/interface/forms.py`
- [X] T073 [US5] Criar `backend/processo_seletivo/interface/templates/interface/impedimentos.html`, acrescentar os controles de reabertura e as listas de inelegíveis e órfãs a `distribuicao.html`, e as duas rotas em `backend/processo_seletivo/interface/urls.py`
- [X] T074 [P] [US5] Testes de integração em `backend/tests/integration/avaliacoes/test_impedimento.py`: bloqueia atribuição nova nomeando o motivo; inativa a ativa; preserva a concluída e a torna inelegível; libera a vaga para uma substituta
- [X] T075 [P] [US5] Teste em `backend/tests/integration/avaliacoes/test_conjunto_elegivel.py`: **a sequência que FR-092 existe para impedir** — dois concluem, a presidência tenta remover uma Atribuição para trocar a nota, e é recusada. Mais: `avaliacoes_elegiveis()` devolve exatamente as concluídas sob Atribuição ativa, e nada além
- [X] T076 [P] [US5] Teste em `backend/tests/integration/avaliacoes/test_reabertura.py`: reabrir preserva a conclusão anterior de forma consultável; concluir numa aba aberta desde antes é recusado; reabrir o que não está concluído é transição inválida
- [X] T077 [P] [US5] Teste em `backend/tests/integration/avaliacoes/test_identidade_estavel.py`: remover e readicionar a pessoa **não** libera segunda conclusão nem apaga o impedimento (FR-074, FR-099)
- [X] T078 [P] [US5] Teste realmente concorrente em `backend/tests/integration/avaliacoes/test_corrida_conclusao_e_remocao.py`: concluir e remover disputam a mesma Atribuição, e nunca existe Avaliação concluída sob Atribuição inativada pela via comum — as duas serializam pela linha e reavaliam o estado depois da trava (FR-092, FR-104)
- [X] T079 [P] [US5] Teste em `backend/tests/integration/avaliacoes/test_idempotencia_dos_atos.py`: remover, impedir e reabrir repetem sem criar registro nem evento; chave repetida com conteúdo diferente é conflito; os três recusam quem perdeu a presidência durante a transação (FR-084, FR-086)

**Checkpoint**: o conjunto que a 013 vai consumir é inequívoco, e sair dele exige ato com nome.

---

## Phase 8: Polish & Cross-Cutting Concerns

- [X] T080 [P] Testes de escala em `backend/tests/performance/test_escala_da_mesa.py`, contando consultas: Mesa com 500 atribuições em três consultas; organização do trabalho de 1000 inscrições por agregação; retirar pessoa de Etapa com 500 atribuições em uma escrita
- [X] T081 [P] Teste em `backend/tests/authorization/test_listagem_em_lote.py`: nenhuma listagem da 012 chama `pode_atuar_na_etapa`, e as duas formas de autorização nunca divergem
- [X] T082 [P] Teste em `backend/tests/integration/avaliacoes/test_trilha_completa.py`: os **sete** atos de FR-052 — atribuir, remover atribuição, abrir documento, gravar, concluir, reabrir, impedir — produzem evento com ator, inscrição, Etapa, operação e instante (FR-053)
- [X] T083 [P] Acessibilidade e responsividade das cinco telas em `backend/processo_seletivo/interface/templates/interface/` — 375 px sem tabela horizontal, foco visível, rótulos associados
- [X] T084 Criar `trilha_da_avaliacao()` em `backend/processo_seletivo/auditoria/selectors.py`, resolvendo os sete atos **pelas relações**, como `trilha_da_comissao` já fazia: por inscrição e por avaliador, os agregados relacionados (`Atribuicao`, `Avaliacao`, `Impedimento`). ~~Acrescentar o parâmetro opcional `actor_subject` a `consultar()`~~ — corrigido em T093: a exceção que exigia o parâmetro era a abertura de documento ancorada na `Inscricao`, e ancorar ali era o defeito
- [X] T085 Acrescentar a tela da trilha da 012 em `backend/processo_seletivo/interface/views.py`, `urls.py` e `backend/processo_seletivo/interface/templates/interface/auditoria.html`, com os três filtros de FR-050 — inscrição, avaliador e operação — e as sete operações novas na lista
- [X] T086 [P] Teste em `backend/tests/interface/test_trilha_da_012.py`: cada um dos **sete** atos aparece sob o filtro por inscrição e sob o filtro por avaliador, isolados e combinados; um ato praticado pela presidência sobre a atribuição de alguém aparece no filtro **daquele avaliador**, e não no de quem o praticou; **dois avaliadores abrindo a mesma inscrição** aparecem cada um sob o seu filtro, e nenhum sob o do outro; e **impedimento registrado sem Atribuição ativa** — o caso preventivo — aparece nos dois filtros, porque o agregado é o próprio `Impedimento`
- [X] T087 [P] Teste de não-regressão em `backend/tests/integration/comissoes/test_011_intocada.py`: comissão, alocação e guard da 011 seguem idênticos
- [X] T088 [P] Teste de não-regressão do pipeline de Retificação em `backend/tests/integration/publicacoes/test_retificacao_intocada.py`, exigido por FR-100: para Edital **inteiramente na versão vigente**, a precondição, a detecção de conflito, a consolidação, a verificação de efeito prático e a materialização produzem o mesmo resultado que produziam antes desta feature. É a guarda sobre a superfície que a 012 passou a tocar em quatro módulos
- [X] T089 Executar `specs/012-mesa-de-avaliacao/quickstart.md` inteiro, as seis entregas, e registrar o que divergiu
- [X] T090 Registrar os dois gates de implantação do quickstart em `specs/012-mesa-de-avaliacao/quickstart.md` — identidade institucional (FR-058) e retenção/descarte do acervo (FR-057) —, com o estado de cada um. **FR-057 não tem tarefa de implementação de propósito**: a resposta é institucional, e o que a 012 entrega é a pergunta registrada
- [X] T091 Escrever `specs/012-mesa-de-avaliacao/traceability.md`, fechando os 113 FR e os 31 SC contra tarefa e teste — os 37 demonstrados pelo quickstart e os demais cobertos por suíte

---

## Phase 9: Correções das revisões e do percurso em escala

Cinco defeitos funcionais e dois menores na primeira rodada (`origin/main...f5bcaba`), e mais três
na segunda, sobre as próprias correções. Nenhum era visível pela suíte que existia — quatro
passavam porque o teste exercitava exatamente o caso que escondia o defeito, e os três da segunda
rodada eram sobre código novo que a primeira ainda não tinha lido.

E mais sete do **percurso de um Processo de 600 inscritos**, que é onde a escala aparece: nenhum
deles é visível numa Etapa de três inscrições, e dois eram bloqueadores de uso — a tela que crescia
com o trabalho já feito, e as cerca de 700 marcações para distribuir uma Etapa.

E mais dois de uma avaliação de percurso e navegação: a feature inteira estava **inalcançável por
link**, e o caminho de quem avalia custava três cliques por inscrição que não decidiam nada.

- [X] T092 Separar a porta da trilha em `_etapa_para_auditar()`, em `backend/processo_seletivo/interface/views.py`: presidência **ou** `auditoria:consultar`, e 404 para quem não é nenhum dos dois (FR-091). A rota exigia as duas coisas ao mesmo tempo — o presidente lia 403, o auditor puro lia 404 —, e a fixture `["gestor", "auditor"]` escondia isso por testar justamente o híbrido
- [X] T093 Ancorar a abertura de documento na `Atribuicao`, em `_registrar_na_mesa()`, e desfazer a consulta composta de T-084 em `backend/processo_seletivo/auditoria/selectors.py` (FR-053, T-016). Sobre a `Inscricao`, o registro não nomeava a Etapa e não se distinguia da consulta administrativa da 009 — a trilha de uma Etapa exibia as aberturas de outra e as consultas do gestor
- [X] T094 Corrigir a paginação da trilha: uma consulta, um cursor (T093 já a torna única) e o link da página seguinte carregando os três filtros, por `pagina_seguinte` em `backend/processo_seletivo/interface/templatetags/interface_extras.py`. Duas páginas somadas em memória não têm cursor comum, e sob filtro de abertura de documento a segunda ficava inalcançável
- [X] T095 Tornar a preservação consultável: `conclusoes_preservadas()` em `backend/processo_seletivo/avaliacoes/application/selectors.py`, a rota e a tela `conclusoes.html`, com pontuação, parecer, versão, instante e a situação de cada conclusão (FR-091, FR-094). Depois de uma reabertura, o histórico existia só na tabela append-only — e a trilha, corretamente, não guarda nota nem parecer
- [X] T096 Conferir o alcance confirmado sob trava em `registrar_impedimento()`, por assinatura do conjunto e não por contagem (FR-041, FR-106). O primeiro POST calculava as contagens e o segundo não as comparava: entre os dois, uma conclusão nova tornava inelegível o que ninguém confirmou
- [X] T098 Paginar `conclusoes_preservadas()` em `backend/processo_seletivo/avaliacoes/application/selectors.py` e a tela em `conclusoes.html` (FR-049), calculando a última ordem de cada Avaliação **por agregação**, porque a conclusão que vale pode estar na página seguinte
- [X] T099 Recusar a confirmação do impedimento sem alcance declarado em `backend/processo_seletivo/interface/views.py` (FR-106): sem isso a garantia era desligável por quem monta o formulário
- [X] T100 Trocar a lista de identificadores por `aggregate_filter` de subconsultas em `trilha_da_avaliacao()` (FR-050), com o teste de escala que mede o texto da consulta em `backend/tests/performance/test_escala_da_mesa.py`
- [X] T127 Varrer as telas restantes pelo mesmo critério, e prender a varredura em teste: `.oculto` passa a existir (cinco legendas escritas para quem ouve a tela apareciam impressas), os nove botões de envio sem classe ganham peso, `.paginacao` e `.motivos` ganham desenho, `select` ganha o mesmo teto de largura que o `textarea` já tinha, o campo do motivo da reabertura passa a caber, os dois `fieldset` de escolha vão a colunas, `.filtros` passa a ser cartão como `.filtro`, e a trilha diz o nome do requisito em vez do UUID dele
- [X] T126 Polir a Comissão do Processo em `comissao.html` e `base.html`: `.s-PRESIDENTE` e `.s-MEMBRO` passam a existir na folha (quatro telas escreviam as classes e nenhuma tinha cor), a marca de filtrar deixa de herdar `width:100%` dos campos de texto, a ação vai ao rodapé do cartão para as fileiras pararem de terminar em degraus, o seletor de função para de ocupar o cartão inteiro, remover ganha separação do que é rotineiro, e o identificador some quando repete o nome
- [X] T125 Polir a matriz de alocação em `alocacoes.html` e `base.html`: pastilhas do cabeçalho voltam a abraçar o próprio conteúdo (o `display:block` herdado as esticava à largura da coluna), a contagem ganha unidade, as ações ganham hierarquia — "Distribuir" sai da tela, "Todos/Nenhum" mexem na coluna abaixo —, a caixa da marca não herda mais a versalete de `thead th`, a célula inteira vira alvo, a folga vai para as colunas de marca em vez de a última, e o identificador some quando repete o nome
- [X] T124 Dar ao cartão da Etapa o percentual concluído e a barra, com os extremos reservados aos extremos, e separar os quatro estados que três se pareciam (FR-115) — em `minhas_etapas.html` e `avaliacoes/application/selectors.py`, sem consulta a mais: a agregação já trazia os dois números. E desfazer os dois empréstimos de classe que tornavam o cartão ilegível — `.corpo`, que só tem regra sob `.auditoria`, e `.salvar`, que trazia filete e rodapé morto
- [X] T123 Tirar o instante da linha e da frase do cursor, deixando-o ao alcance no `title` (FR-113, FR-114): para quem avalia dezenas por dia, "já vi este?" é sim ou não, e a hora competia em largura com o nome do documento. E dar ao campo de pontuação a largura do que ele recebe — `.curto` só encolhia dentro de `.campos`, e solto a caixa de quatro dígitos ia a 1.350 px ao lado de um parecer limitado à medida de leitura
- [X] T122 Marcar, em cada documento, quando **esta pessoa** o abriu, e contar quantos dos entregues já foram abertos (FR-114). A marca é de leitura, e não de veredito: a Avaliação é uma só por inscrição, e marcar "avaliado" por documento inventaria um julgamento que o domínio não tem. O instante vem da trilha, filtrada pela Atribuição e pelo ator — a consulta administrativa da 009 abre o mesmo arquivo e não marca a lista de quem avalia
- [X] T121 Dizer o estado da leitura nas duas direções, com o instante vindo da trilha (FR-113); devolver a marca de obrigatório ao seu tamanho, pondo-a numa célula em vez de ser item de grade direto; e levar o limite de largura da inscrição do formulário para a página, que é o que desfaz a borda direita irregular
- [X] T120 Revisar as telas restantes pelo mesmo critério: os números da distribuição viram o filtro de cobertura e as avaliações por inscrição vão para a ficha; a carga por avaliador ganha largura própria e números alinhados à direita; "retirar atribuições" vai a colunas; os cartões de comissão e de Etapa viram grade; e "Você integra a comissão" deixa de ser faixa de sucesso
- [X] T119 Levar o foco ao primeiro documento por abrir, e à nota só quando já houve leitura ou não há o que ler (FR-113), com a linha que diz o que a trilha sabe; e pôr a marca de obrigatório em coluna própria, com a grade na lista e `display:contents` nas linhas — com a grade em cada `li`, cada linha formava a sua e as colunas não se falavam
- [X] T118 Desenhar a Mesa pelo mesmo critério da tela da inscrição: ficha em linha no lugar do `dl` padrão, "alocado nesta Etapa" deixando de ser faixa de sucesso, contagens que fecham com o total (não iniciadas + em rascunho + concluídas), filtros como controle com número, lista com a largura do que mostra, e as atribuições retiradas em linhas. E alinhar as duas colunas da inscrição pela barra do painel
- [X] T117 Desenhar a tela da inscrição, que era a menos desenhada do sistema e a mais usada por quem avalia: ficha do candidato em linha, um requisito por linha com a ação à direita, `pontuacao` como filtro de exibição, e o estado concluído deixando de ser faixa verde de sucesso. E corrigir o painel do documento, que aparecia vazio no alto de toda inscrição porque `display` de autor vence o `hidden` do navegador
- [X] T116 Separar a largura do texto da largura da página em `shared/_tokens.css.html` e nas duas bases: `--leitura` para texto corrido e campos que se escrevem, `--pagina` para tabelas, matriz e painéis, com a vitrine em duas colunas. O limite único media 84 caracteres por linha no portal e 147 na gestão, contra 65–75 confortáveis, e ao mesmo tempo deixava 412 px de tela vazios
- [X] T115 Pôr o documento ao lado do formulário em tela larga — `mesa.js`, o painel em `mesa_inscricao.html` e as duas colunas em `base.html` —, com `xframe_options_sameorigin` apenas na entrega da Mesa (FR-112). Abaixo de 64rem e sem JavaScript, o link continua abrindo em aba própria
- [X] T113 Oferecer as identidades com trabalho de comissão no seletor, por `identidades_com_trabalho()` em `backend/processo_seletivo/comissoes/application/selectors.py` e `identificar.html`, dizendo o que cada uma alcança (FR-111)
- [X] T114 Reordenar o cartão de vagas do portal em `portal/templates/portal/selecao.html` e `portal/base.html`: requisitos antes da ação, dados em linha, contagem nos documentos, e números e ação na coluna da direita em tela larga
- [X] T111 Ligar a Etapa à sua distribuição na matriz de alocação (`alocacoes.html`) e oferecer Comissão e Alocação a quem tem `comissao:gerir` sem integrar a comissão (`lista.html`), com teste que percorre o caminho **só por links** em `backend/tests/interface/test_caminho_ate_a_mesa.py` (FR-109)
- [X] T112 Cortar os três cliques de navegação da Mesa (FR-110): documento em aba própria, foco inicial na pontuação, e concluir levando à próxima pendente com o aviso nomeando a inscrição concluída
- [X] T104 Tirar a reabertura da tela de distribuição e levá-la à página de conclusões preservadas, com o formulário de motivo por linha em vigor (FR-036, FR-049) — a seção sem paginação media 679 KB e 605 formulários com 601 conclusões
- [X] T105 Criar `backend/processo_seletivo/avaliacoes/domain/rodizio.py` e os comandos `propor_rodizio`/`confirmar_rodizio` em `application/distribuicao.py`, com a conferência da assinatura sob trava (FR-107)
- [X] T106 Acrescentar a proposta de rodízio à tela de distribuição em `distribuicao.html`, com o plano por pessoa e o que fica de fora, e `selecao.js` para marcar todas as inscrições da página (FR-049, FR-107)
- [X] T107 Distinguir rascunho de não iniciada na Mesa, com filtro próprio (FR-021), e mostrar as atribuições retiradas com o ato e o motivo (FR-108) em `selectors.py` e `minha_etapa.html`
- [X] T108 Aceitar protocolo onde se digita inscrição — filtro da trilha, filtro das conclusões e formulário de impedimento (FR-050) — e nomear quem e qual inscrição na confirmação do impedimento (FR-041)
- [X] T109 Acrescentar o filtro por progresso à distribuição e a coluna de concluídas (FR-049), a contagem por Etapa na tela inicial de quem avalia e o atalho para a próxima pendente
- [X] T110 [P] Corrigir a comunicação: lote inteiramente recusado deixa de ser anunciado em verde e os motivos vêm agrupados (FR-097); o ato aparece por extenso na tabela de inelegíveis; uma faixa só ao concluir; Perfil vazio diz "não informado"; e a tela da 011 passa a se chamar Alocação por Etapa, desfazendo a colisão com a Distribuição da 012
- [X] T101 Escopar o impedimento na trilha pela **alocação** da pessoa na Etapa, em `trilha_da_avaliacao()` (FR-050): sem critério de pertinência ele aparecia na trilha de toda Etapa do Edital, e escopá-lo pela Atribuição apagaria o caso preventivo
- [X] T102 Nomear o alvo de cada ato na trilha por `rotulos_dos_agregados()` em `backend/processo_seletivo/avaliacoes/application/selectors.py` — três consultas, uma por tipo de agregado, e não uma por linha (FR-048, FR-050)
- [X] T103 Paginar `avaliacoes_inelegiveis()` e a sua tabela em `impedimentos.html` (FR-049)
- [X] T097 [P] Recusar identificador malformado como erro de formulário — `identificador_de_inscricao()` no impedimento e `_tem_forma_de_identificador()` nos filtros da trilha e das conclusões —, e marcar `postgresql_only` os dois testes de corrida da 012, que quebravam em SQLite por "database table is locked" e vazavam conexões

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (1)**: sem dependências.
- **Foundational (2)**: depende de 1 e **bloqueia todas as histórias**. Dentro dela: T006 antecede
  T007 (teste de contrato); T012 antecede T013, T014 e T015; T016–T018 antecedem T019; T016 antecede
  T021.
- **US1 (3)**: depende de 2.
- **US2 (4)**: depende de 2; lê o que a US1 grava, mas é testável com Atribuições de fixture.
- **US3 (5)**: depende de 2 e da tela da US2 para ser alcançada por navegação.
- **US4 (6)**: depende de 5 — avaliar pressupõe ver o que se avalia.
- **US5 (7)**: depende de 6, porque FR-092, FR-093 e a reabertura só têm sentido quando há Avaliação
  concluída. **As tabelas já existem desde a fase 2**; o que falta aqui é comportamento.
- **Polish (8)**: depende das histórias que se quer medir.

### Parallel Opportunities

- T003 e T004 no Setup.
- Na Foundational: T005, T006, T008 e T010 em paralelo. **T016, T017 e T018 não são paralelas** —
  as três editam `models.py`, e a marca estava errada. Depois, T023,
  T024, T025, T027 e T028 em paralelo.
- Dentro de cada história, todos os testes marcados `[P]` são de arquivos distintos.
- US1 e US2 podem ser tocadas por pessoas diferentes assim que a Foundational fechar; US3, US4 e US5
  são encadeadas por navegação e por dependência de dado.

---

## Implementation Strategy

### MVP — as fases 1 a 6

A vertical que a §24 da spec declara: presidente distribui → avaliador abre a Mesa → abre a
inscrição → registra e conclui → quem não recebeu não alcança. Pare em T065, rode o quickstart das
entregas 1 a 5 e valide.

### Entrega incremental

1. Fases 1–2 → o Edital declara e publica as duas propriedades, o que já estava publicado continua
   retificável, e as quatro tabelas existem com suas garantias. **É a única fase que toca conteúdo
   normativo, e a que mais pode quebrar o que já existe** — os oito cenários e as três contraprovas
   de T026, mais a regressão de T089, são a condição para seguir.
2. Fase 3 → distribuição com autoria, auditada.
3. Fases 4–5 → a Mesa e o documento.
4. Fase 6 → **MVP**.
5. Fase 7 → a proteção do conjunto elegível, que é o gate da 013.
6. Fase 8 → escala medida, trilha completa, acessibilidade, rastreabilidade.

### Notas

- Commit por tarefa ou grupo lógico, no padrão de mensagem da casa.
- Todo comando da presidência passa por `comando_de_comissao` **e** chama `auditar()` — o invólucro
  não audita sozinho.
- "Invalidar" não entra em nome de campo, mensagem ou tela: o par é **preservada** e **inelegível**.
- Nenhuma tarefa produz média, quórum, divergência, desempate ou situação. Se aparecer, é da 013.
