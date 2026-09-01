---

description: "Task list for feature implementation"
---

# Tasks: Mesa de Avaliação

**Input**: Design documents from `/specs/012-mesa-de-avaliacao/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/mesa.md](./contracts/mesa.md), [quickstart.md](./quickstart.md)

**Tests**: **sim, exigidos**, e por três razões que a spec já fixou. O princípio V da Constituição
nomeia autorização e concorrência entre o que precisa de cobertura específica, e a 012 entrega as
duas. Metade do que ela promete só se prova pela recusa. E os oito cenários de elevação de T-001
são a condição para que Editais já publicados continuem retificáveis — se falharem, a feature
quebra o que já existe.

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
> `TEST_DB_ENGINE=postgresql` a suíte cai para SQLite **sem avisar**, e deixam de ser verificados:
> o índice único parcial de FR-074, a trigger append-only de `ConclusaoAvaliacao`, e o
> `select_for_update` herdado de `comando_de_comissao`. Rode como o [quickstart](./quickstart.md)
> manda, com `DB_NAME` próprio deste worktree.

> **⚠️ Nenhuma tarefa desta lista escreve em linha gravada de `publicacoes`.** A elevação é leitura.
> Se alguma tarefa precisar de `UPDATE` em `VersaoConsolidada`, `Publicacao` ou `AlteracaoNormativa`,
> a decisão D-002 foi violada e o problema é de desenho, não de implementação.

> **⚠️ Nenhuma tarefa desta lista chama `pode_atuar_na_etapa` dentro de laço.** Listagem usa
> `etapas_autorizadas`. Se aparecer uma, FR-048 foi violado.

---

## Phase 1: Setup

**Purpose**: o app novo existe, e o vocabulário deixa de colidir.

- [ ] T001 Criar o app em `backend/processo_seletivo/avaliacoes/` com `__init__.py`, `apps.py`, `models.py`, `domain/`, `application/` e `migrations/`
- [ ] T002 Registrar `processo_seletivo.avaliacoes` em `backend/config/settings/base.py`, com o comentário que diz por que é app próprio e não parte de `comissoes` (T-003)
- [ ] T003 [P] Criar `backend/tests/unit/avaliacoes/` e `backend/tests/integration/avaliacoes/` com `__init__.py`
- [ ] T004 [P] Renomear a rota da 011 em `backend/processo_seletivo/interface/urls.py` e `views.py`: `atribuicao` → `minha_etapa`, mantendo o caminho `minhas-etapas/<edital>/<etapa>` intacto, e ajustar as referências em `backend/processo_seletivo/interface/templates/interface/` (T-012)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: o incremento normativo, a elevação e a base de autorização. **Nenhuma história começa
antes desta fase**, porque todas leem a Etapa publicada e todas compõem a mesma autorização.

**⚠️ Esta fase toca conteúdo publicado. É a única que toca.**

### O incremento canônico

- [ ] T005 [P] Acrescentar `evaluations_per_registration` e `maximum_score` a `EtapaAvaliacao` em `backend/processo_seletivo/editais/models/etapas.py`, com os dois `CheckConstraint` de faixa, e gerar a migration em `backend/processo_seletivo/editais/migrations/`
- [ ] T006 [P] Acrescentar as duas propriedades a `EtapaPublicada` e `EtapaInput` em `specs/001-processo-seletivo-editais/contracts/openapi.yaml`, e atualizar a descrição da versão canônica que elas carregam
- [ ] T007 Transcrever as duas em `ETAPA_PUBLICADA` em `backend/processo_seletivo/editais/domain/validation.py` (depende de T006: o teste de contrato falha se divergirem)
- [ ] T008 [P] Aceitar os dois campos no serializer em `backend/processo_seletivo/editais/api/serializers.py` e na gravação do rascunho em `backend/processo_seletivo/editais/application/draft.py`
- [ ] T009 Emitir os dois em `_stages()` em `backend/processo_seletivo/publicacoes/application/publish_edital.py` e subir `SCHEMA_VERSION` para 5 em `backend/processo_seletivo/shared/canonical.py`, com o comentário do incremento no padrão dos anteriores
- [ ] T010 [P] Imprimir as duas linhas na Etapa do documento materializado em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`
- [ ] T011 Verificar a coerência `minimumScore ≤ maximumScore` na validação de publicação em `backend/processo_seletivo/editais/domain/validation.py`, junto das outras faixas de Etapa

### A elevação (T-001, T-015)

- [ ] T012 Criar `backend/processo_seletivo/publicacoes/domain/elevacao.py` com `elevar(conteudo)` e `elevar_alteracoes(changes)`, implementando a tabela de classificação de caminho de T-001 — `/stages/-`, `/stages/id=<uuid>`, `/stages`, `/stages/id=<uuid>/<campo>`, demais, `REMOVE`
- [ ] T013 Aplicar a elevação nas fronteiras do fluxo de Retificação em `backend/processo_seletivo/publicacoes/application/retificacoes.py`: conteúdo-base em `create_retification`, `edit_retification` e `publish_retification`; `_original_version`; `_content_in_force`; e `_changes_payload`, que cobre `_acts` e a publicação de uma vez (depende de T012)
- [ ] T014 Servir a projeção elevada à superfície de autoria (T-015): `campos_editaveis` e `diferencas` em `backend/processo_seletivo/interface/retificacao.py`, e as leituras de `base_snapshot.content` em `backend/processo_seletivo/interface/views.py` (depende de T012)

### A leitura da ausência

- [ ] T015 Criar `backend/processo_seletivo/avaliacoes/domain/previsao.py` com `avaliacoes_previstas()` e `pontuacao_maxima()` — o único lugar onde a ausência é interpretada (T-002)

### Os modelos-base e a autorização composta

- [ ] T016 [P] Criar `Atribuicao` em `backend/processo_seletivo/avaliacoes/models.py`, com a unicidade parcial sobre ativo, o check de completude de inativação e os dois índices de §2 do data-model
- [ ] T017 Criar `backend/processo_seletivo/avaliacoes/domain/autorizacao.py` com `pode_avaliar_inscricao()`, compondo `pode_atuar_na_etapa` da 011 com a existência de Atribuição ativa — **sem** reimplementar a primeira metade (depende de T016)
- [ ] T018 Gerar a migration inicial de `avaliacoes` em `backend/processo_seletivo/avaliacoes/migrations/`

### Os testes que esta fase obriga

- [ ] T019 [P] Teste de contrato da forma publicada nova em `backend/tests/contract/test_forma_publicada.py`, conferindo a transcrição contra o `openapi.yaml`
- [ ] T020 [P] Testes unitários da elevação em `backend/tests/unit/avaliacoes/test_elevacao.py`: idempotência, `null` preservado, escalar intocado e cada linha da tabela de caminhos
- [ ] T021 [P] Testes unitários da leitura da ausência em `backend/tests/unit/avaliacoes/test_previsao.py`: ausente, nulo e declarado
- [ ] T022 Os **oito cenários** de T-001 em `backend/tests/integration/publicacoes/test_elevacao_de_versao.py` — quatro de histórico misto (sem retificação; `ADD` por `/stages/-`; `REPLACE` de Etapa inteira; `REPLACE` de campo) e quatro de deploy (v4 em elaboração; v4 homologada; criada depois sobre base v4; a mesma com `expectedPreviousHash` declarado). Em todos, afirmar que o `content_hash` de toda `Publicacao` e `VersaoConsolidada` anterior permanece idêntico
- [ ] T023 [P] Teste de regressão em `backend/tests/integration/publicacoes/test_leitura_publica_literal.py`: consulta pública, comprovante e documento de Publicação existente continuam servindo o conteúdo literal, não elevado (T-002)

**Checkpoint**: o Edital declara e publica as duas propriedades, Editais antigos continuam
retificáveis, e a autorização composta existe. Nenhuma tela nova ainda.

---

## Phase 3: User Story 1 — Distribuir as inscrições (P1)

**Goal**: a presidência distribui, em lote, as inscrições submetidas entre quem está alocado à
Etapa, e vê o que falta.

**Independent Test**: distribuir 400 inscrições entre dois avaliadores em poucas submissões;
recusar a excedente nomeando o número publicado; reenviar o lote e não criar nada.

- [ ] T024 [US1] Implementar `distribuir()` em `backend/processo_seletivo/avaliacoes/application/distribuicao.py`, sobre `comando_de_comissao` da 011, com os seis invariantes de §2 do data-model e um `AtoAdministrativo`/`record_event` por Atribuição criada
- [ ] T025 [US1] Implementar a recusa de duas naturezas de FR-085 em `backend/processo_seletivo/avaliacoes/application/distribuicao.py`: regra sobre a linha acumula e relata; erro sobre o pedido levanta e desfaz o lote
- [ ] T026 [US1] Implementar `remover_atribuicao()` em `backend/processo_seletivo/avaliacoes/application/distribuicao.py`, alcançando **apenas** Atribuição sem Avaliação concluída, também sobre `comando_de_comissao` (a recusa de FR-092 entra na Phase 7, quando a Avaliação existir)
- [ ] T027 [P] [US1] Implementar os seletores da organização do trabalho em `backend/processo_seletivo/avaliacoes/application/selectors.py`: carga por pessoa, déficit por inscrição e totais — por agregação, nunca por laço
- [ ] T028 [US1] Criar a view `distribuicao` e o formulário do lote em `backend/processo_seletivo/interface/views.py` e `forms.py`, com `idempotency_key` e o resultado declarado de FR-097
- [ ] T029 [US1] Criar `backend/processo_seletivo/interface/templates/interface/distribuicao.html` e as três rotas de distribuição em `urls.py`
- [ ] T030 [P] [US1] Testes de integração em `backend/tests/integration/avaliacoes/test_distribuicao.py`: teto recusado, impedimento e já-atribuída não derrubam o lote, Etapa inexistente derruba, reenvio idempotente sem evento novo, um evento por atribuição
- [ ] T031 [P] [US1] Teste de autorização em `backend/tests/authorization/test_distribuicao.py`: quem não gere a comissão recebe 404; escopo divergente idem

**Checkpoint**: existe distribuição com autoria, em lote, auditada e idempotente.

---

## Phase 4: User Story 2 — A Mesa (P1)

**Goal**: cada avaliador abre sua lista de trabalho e vê todas e somente as inscrições que lhe
foram atribuídas.

**Independent Test**: avaliador com atribuições vê a lista paginada com contagens; alocado sem
atribuição abre a Mesa **vazia**; inscrição de outro responde 404.

- [ ] T032 [US2] Implementar `mesa()` em `backend/processo_seletivo/avaliacoes/application/selectors.py`: uma chamada a `etapas_autorizadas`, uma consulta paginada com `select_related`, uma de contagens
- [ ] T033 [US2] Substituir o aviso da 011 pela Mesa em `backend/processo_seletivo/interface/templates/interface/minha_etapa.html`, com filtro de pendentes/concluídas e o período previsto da Etapa (FR-078)
- [ ] T034 [US2] Implementar o estado vazio de FR-023 em `backend/processo_seletivo/interface/templates/interface/minha_etapa.html` — explicando que ainda não há inscrições distribuídas, e nunca como falta de permissão
- [ ] T035 [P] [US2] Teste de interface em `backend/tests/interface/test_mesa.py`: contagem, filtro, paginação e estado vazio
- [ ] T036 [P] [US2] Teste de autorização em `backend/tests/authorization/test_mesa.py`: alocado sem atribuição recebe a Mesa vazia com 200; sem alocação recebe 404; remover a alocação faz a Mesa sumir e devolvê-la restaura as mesmas atribuições
- [ ] T037 [P] [US2] Teste em `backend/tests/integration/avaliacoes/test_revogacao_computada.py`: alocar, desalocar e remover membro **não escrevem em nenhuma linha de `Atribuicao`** (FR-069)

**Checkpoint**: o avaliador enxerga o seu trabalho, e só o dele.

---

## Phase 5: User Story 3 — A inscrição como instrumento de trabalho (P1)

**Goal**: o avaliador abre os documentos da inscrição atribuída, cada um sob o Documento Exigido
que atende, e cada abertura fica registrada.

**Independent Test**: abrir documento de inscrição atribuída funciona e deixa rastro; trocar o UUID
na URL responde 404; arquivo corrompido é recusa registrada.

- [ ] T038 [US3] Criar a view da inscrição em `backend/processo_seletivo/interface/views.py`, autorizada por `pode_avaliar_inscricao`, montando os documentos por `requisitos_da_inscricao` sobre o conteúdo da **versão que a inscrição aceitou** (T-006)
- [ ] T039 [US3] Criar a view do documento em `backend/processo_seletivo/interface/views.py`, reutilizando `copia_verificada`, `entregar`, `marcar_como_privada` e o registro de `CONSULTAR_DOCUMENTO`/`INTEGRIDADE` — **sem** chamar `inscricao:consultar` (D-005)
- [ ] T040 [P] [US3] Criar `backend/processo_seletivo/interface/templates/interface/mesa_inscricao.html`, com identificação mínima e o CPF mascarado (FR-030)
- [ ] T041 [US3] Acrescentar as duas rotas em `backend/processo_seletivo/interface/urls.py`
- [ ] T042 [P] [US3] Teste de autorização em `backend/tests/authorization/test_documento_da_mesa.py`: inscrição não atribuída 404; alocação removida revoga; escopo divergente 404
- [ ] T043 [P] [US3] Teste de integração em `backend/tests/integration/avaliacoes/test_documento.py`: a trilha registra ator, inscrição e requisito; hash divergente é recusa registrada; não há rota de lote
- [ ] T044 [P] [US3] Teste de regressão em `backend/tests/integration/inscricoes/test_consulta_administrativa_intocada.py`: a porta da 009 continua exatamente como era

**Checkpoint**: o documento é instrumento de trabalho, mediado e auditado.

---

## Phase 6: User Story 4 — Registrar a avaliação (P1) 🎯 **MVP**

**Goal**: o avaliador grava rascunho, é validado contra o que o Edital publicou, e conclui em ato
distinto.

**Independent Test**: a vertical inteira da §24 — presidente distribui, avaliador abre a Mesa, abre
a inscrição, registra e conclui, e quem não recebeu aquela inscrição não a alcança.

- [ ] T045 [P] [US4] Criar `Avaliacao` e `ConclusaoAvaliacao` em `backend/processo_seletivo/avaliacoes/models.py`, com o `OneToOne`, a tripla `identity_subject`/`etapa_id`/`inscricao_id`, o índice único parcial de FR-074, o check de completude de `CONCLUIDA` e a proteção append-only da conclusão
- [ ] T046 [US4] Acrescentar a trigger append-only de `ConclusaoAvaliacao` na migration em `backend/processo_seletivo/avaliacoes/migrations/`, no estilo de `publicacoes/migrations/0007`
- [ ] T047 [P] [US4] Criar `backend/processo_seletivo/avaliacoes/domain/pontuacao.py`: validação contra a máxima publicada, a forma decimal e a não-negatividade — **a nota mínima não recusa nada** (FR-033)
- [ ] T048 [US4] Implementar `gravar()` em `backend/processo_seletivo/avaliacoes/application/avaliacao.py`, com `compare_and_swap` sobre `revision`
- [ ] T049 [US4] Implementar `concluir()` em `backend/processo_seletivo/avaliacoes/application/avaliacao.py`: lê a Versão Consolidada **dentro da transação**, valida contra ela, grava-a na Avaliação e escreve a `ConclusaoAvaliacao` (FR-071, FR-096)
- [ ] T050 [US4] Implementar em `backend/processo_seletivo/avaliacoes/application/avaliacao.py` o parecer obrigatório quando a Etapa for eliminatória e a nota ficar abaixo do mínimo (FR-034), lendo o caráter da versão lida na mesma transação
- [ ] T051 [US4] Implementar em `backend/processo_seletivo/avaliacoes/application/avaliacao.py` o reconhecimento explícito da mudança de versão entre a última gravação e a conclusão (FR-073)
- [ ] T052 [US4] Acrescentar o formulário de avaliação com `expected_revision` e o aviso de conclusão fora do período previsto (FR-095) em `backend/processo_seletivo/interface/templates/interface/mesa_inscricao.html` e `forms.py`, com as duas rotas em `backend/processo_seletivo/interface/urls.py`
- [ ] T053 [P] [US4] Testes de integração em `backend/tests/integration/avaliacoes/test_avaliacao.py`: rascunho persistido, pontuação acima da máxima recusada, abaixo da mínima aceita com parecer obrigatório, concluída imutável para o avaliador, duas abas gravando com revisão obsoleta
- [ ] T054 [P] [US4] Teste em `backend/tests/integration/avaliacoes/test_versao_da_avaliacao.py`: Retificação consolidada no intervalo produz aviso, e a versão validada é a gravada
- [ ] T055 [US4] Teste de aceitação da vertical completa em `backend/tests/acceptance/test_mesa_de_avaliacao.py`, com três atores — inclusive a recusa de quem não recebeu a inscrição

**Checkpoint**: **MVP**. A vertical que a §24 declarou como primeira entrega significativa está de
pé, e nada nela produz resultado.

---

## Phase 7: User Story 5 — Impedimento, reabertura e a proteção do conjunto elegível (P2)

**Goal**: a presidência registra impedimento e reabre avaliação, e nenhum caminho comum consegue
escolher quais avaliações contam.

**Independent Test**: retirar pela via comum a Atribuição de quem já concluiu é recusado; o
impedimento inativa a Atribuição no mesmo ato e preserva a conclusão como inelegível; reabrir
preserva o que havia sido concluído.

- [ ] T056 [P] [US5] Criar `Impedimento` em `backend/processo_seletivo/avaliacoes/models.py`, ancorado em `identity_subject` e sem coluna de estado (FR-099, T-009)
- [ ] T057 [US5] Implementar `registrar_impedimento()` em `backend/processo_seletivo/avaliacoes/application/impedimento.py`, sobre `comando_de_comissao`: cria a linha, inativa as Atribuições ativas do par e grava um `AtoAdministrativo` por Atribuição inativada
- [ ] T058 [US5] Implementar em `backend/processo_seletivo/avaliacoes/application/impedimento.py` a contagem prévia que a confirmação declara — quantas Atribuições serão inativadas — antes de o ato ser confirmado (FR-041)
- [ ] T059 [US5] Implementar a recusa de FR-092 em `remover_atribuicao()`, em `backend/processo_seletivo/avaliacoes/application/distribuicao.py`: retirar Atribuição sob Avaliação concluída pela via comum é recusado, nomeando os atos que teriam esse efeito e o que cada um exige
- [ ] T060 [US5] Implementar `reabrir()` em `backend/processo_seletivo/avaliacoes/application/avaliacao.py`, sobre `comando_de_comissao`, partindo apenas de `CONCLUIDA`, com motivo obrigatório e `expected_revision`
- [ ] T061 [P] [US5] Implementar os seletores das **inelegíveis** e das **órfãs** em `backend/processo_seletivo/avaliacoes/application/selectors.py`, com o ato, o autor e o motivo ao lado de cada uma (FR-093, EC-003)
- [ ] T062 [US5] Acrescentar a tela de impedimentos e os controles de reabertura em `backend/processo_seletivo/interface/templates/interface/impedimentos.html` e na organização do trabalho, com as duas rotas em `urls.py`
- [ ] T063 [P] [US5] Testes de integração em `backend/tests/integration/avaliacoes/test_impedimento.py`: bloqueia atribuição nova nomeando o motivo; inativa a ativa; preserva a concluída e a torna inelegível; libera a vaga para uma substituta
- [ ] T064 [P] [US5] Teste em `backend/tests/integration/avaliacoes/test_conjunto_elegivel.py`: **a sequência que FR-092 existe para impedir** — dois concluem, a presidência tenta remover uma Atribuição para trocar a nota, e é recusada
- [ ] T065 [P] [US5] Teste em `backend/tests/integration/avaliacoes/test_reabertura.py`: reabrir preserva a conclusão anterior de forma consultável; concluir numa aba aberta desde antes é recusado; reabrir o que não está concluído é transição inválida
- [ ] T066 [P] [US5] Teste em `backend/tests/integration/avaliacoes/test_identidade_estavel.py`: remover e readicionar a pessoa **não** libera segunda conclusão nem apaga o impedimento (FR-074, FR-099)

**Checkpoint**: o conjunto que a 013 vai consumir é inequívoco, e sair dele exige ato com nome.

---

## Phase 8: Polish & Cross-Cutting Concerns

- [ ] T067 [P] Testes de escala em `backend/tests/performance/test_escala_da_mesa.py`, contando consultas: Mesa com 500 atribuições em três consultas; organização do trabalho de 1000 inscrições por agregação; retirar pessoa de Etapa com 500 atribuições em uma escrita
- [ ] T068 [P] Teste em `backend/tests/authorization/test_listagem_em_lote.py`: nenhuma listagem da 012 chama `pode_atuar_na_etapa`, e as duas formas de autorização nunca divergem
- [ ] T069 [P] Acessibilidade e responsividade das cinco telas em `backend/processo_seletivo/interface/templates/interface/` — 375 px sem tabela horizontal, foco visível, rótulos associados
- [ ] T070 [P] Acrescentar as operações novas ao filtro de operações da tela de auditoria da 011, em `backend/processo_seletivo/interface/templates/interface/auditoria.html` e `auditoria/selectors.py`
- [ ] T071 [P] Teste de não-regressão em `backend/tests/integration/comissoes/test_011_intocada.py`: comissão, alocação e guard da 011 seguem idênticos
- [ ] T072 Executar `specs/012-mesa-de-avaliacao/quickstart.md` inteiro, as seis entregas, e registrar o que divergiu
- [ ] T073 Escrever `specs/012-mesa-de-avaliacao/traceability.md`, fechando os 99 FR contra tarefa e teste — os 37 demonstrados pelo quickstart e os 62 cobertos por suíte

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (1)**: sem dependências.
- **Foundational (2)**: depende de 1 e **bloqueia todas as histórias**. Dentro dela, T006 antecede
  T007 (teste de contrato), T012 antecede T013 e T014, e T016 antecede T017.
- **US1 (3)**: depende de 2.
- **US2 (4)**: depende de 2; lê o que a US1 grava, mas é testável com Atribuições criadas por fixture.
- **US3 (5)**: depende de 2 e da tela da US2 para ser alcançada por navegação.
- **US4 (6)**: depende de 5 — avaliar pressupõe ver o que se avalia.
- **US5 (7)**: depende de 6, porque FR-092, FR-093 e a reabertura só existem quando há Avaliação
  concluída.
- **Polish (8)**: depende das histórias que se quer medir.

### Parallel Opportunities

- T003 e T004 no Setup.
- Na Foundational: T005, T006, T008 e T010 em paralelo; depois T019, T020, T021 e T023 em paralelo.
- Dentro de cada história, todos os testes marcados `[P]` são de arquivos distintos.
- US1 e US2 podem ser tocadas por pessoas diferentes assim que a Foundational fechar; US3, US4 e
  US5 são encadeadas por navegação e por dependência de dado.

---

## Implementation Strategy

### MVP — as fases 1 a 6

A vertical que a §24 da spec declara: presidente distribui → avaliador abre a Mesa → abre a
inscrição → registra e conclui → quem não recebeu não alcança. Pare em T055, rode o quickstart das
entregas 1 a 5 e valide.

### Entrega incremental

1. Fases 1–2 → o Edital declara e publica as duas propriedades, e o que já estava publicado
   continua retificável. **É a única fase que toca conteúdo normativo, e a que mais pode quebrar o
   que já existe** — os oito cenários de T-022 são a condição para seguir.
2. Fase 3 → distribuição com autoria, auditada.
3. Fases 4–5 → a Mesa e o documento.
4. Fase 6 → **MVP**.
5. Fase 7 → a proteção do conjunto elegível, que é o gate da 013.
6. Fase 8 → escala medida, acessibilidade, rastreabilidade.

### Notas

- Commit por tarefa ou grupo lógico, no padrão de mensagem da casa.
- Toda tarefa de comando da presidência passa por `comando_de_comissao`; se alguma precisar abrir
  transação própria, o desenho de T-010 foi abandonado.
- "Invalidar" não entra em nome de campo, mensagem ou tela: o par é **preservada** e **inelegível**.
- Nenhuma tarefa produz média, quórum, divergência, desempate ou situação. Se aparecer, é da 013.
