---

description: "Task list for feature implementation"
---

# Tasks: Quadro de Vagas por Modalidade

**Input**: Design documents from `specs/025-quadro-de-vagas-por-modalidade/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/quadro-de-vagas.md](./contracts/quadro-de-vagas.md)

**Tests**: **obrigatórios**, e não opcionais. O Princípio V exige teste no nível certo — e nomeia
cotas, publicação e retificação entre os que exigem cobertura específica. A §9 da spec fecha a
feature em "os oito invariantes da §5 verificáveis por teste". Nenhuma feature anterior abriu
exceção; esta não abre.

**Organization**: por user story, para que cada faixa seja demonstrável sozinha.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode correr em paralelo — arquivos distintos, sem dependência pendente
- **[Story]**: a que user story a tarefa pertence (`US1` a `US4`)
- Caminho de arquivo exato em toda tarefa

## Path Conventions

Monólito Django. Código em `backend/processo_seletivo/`, testes em `backend/tests/`, contrato de API
em `specs/001-processo-seletivo-editais/contracts/openapi.yaml`.

**Um modelo novo, uma migration, nenhum app novo, nenhum módulo novo.** Se alguma tarefa abaixo levar
você a criar pacote ou serviço, a tarefa foi mal lida.

**Banco próprio nesta worktree**: `DB_NAME=ps_demo_025`. Suítes paralelas disputam
`test_processo_seletivo` e se derrubam.

---

## Phase 1: Setup

**Purpose**: liberar o nome do domínio antes que alguém escreva o quadro de verdade.

- [X] T001 Renomear `_quadro_de_vagas` para `_quadro_de_perfis` em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py:1332` e na chamada em `_perfis`, **sem alterar uma linha da lógica**. *A `R-011` encontrou o nome do domínio ocupado por outro artefato: aquela função tabula **Perfis** (`Perfil`, `Localidade`, `Vagas`, `Cadastro reserva`, `Carga horária`), e não o quadro de vagas do Edital. O Princípio I proíbe o mesmo termo nomear dois conceitos*
- [X] T002 Rodar `uv run pytest tests/contract/test_documento_publicado.py` em `backend/` e exigir verde. *É função privada: o PDF sai byte a byte idêntico, e `test_o_documento_publicado_continua_byte_a_byte_o_mesmo` prova de graça que a `T001` não mudou nada*

**Checkpoint**: o nome `quadro de vagas` está livre para significar o que o domínio diz que ele significa.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: a entidade existe, e a coleção já é endereçável antes de existir conteúdo publicado com ela.

**⚠️ CRÍTICO**: nenhuma user story começa antes deste checkpoint.

- [X] T003 Criar o modelo `LinhaDoQuadroDeVagas` em `backend/processo_seletivo/editais/models/perfis.py`, ao lado de `ModalidadeConcorrencia`: `id` UUID, `perfil` FK `CASCADE` com `related_name="quadro_de_vagas"`, `modalidade` FK `ModalidadeConcorrencia` **`null=True`, `PROTECT`**, `vagas_imediatas` `PositiveIntegerField`, `ordem` `PositiveIntegerField`, `Meta.ordering = ["ordem", "id"]`. Docstring registrando **por quê**: `NULL` na modalidade **é** a ampla concorrência e não ausência (`D-002`, `D-004`), e `PROTECT` é a `D-008` escrita no banco
- [X] T004 Acrescentar a `LinhaDoQuadroDeVagas`, em `backend/processo_seletivo/editais/models/perfis.py`, as **duas** constraints parciais: `UniqueConstraint(["perfil", "modalidade"], name="uq_linha_por_modalidade", condition=Q(modalidade__isnull=False))` e `UniqueConstraint(["perfil"], name="uq_linha_geral_por_perfil", condition=Q(modalidade__isnull=True))`. *Uma só seria **mais fraca**: no PostgreSQL dois `NULL` não colidem, e duas linhas gerais passariam. É a mesma cirurgia de `classificacao/models.py:86-100` (`FR-154`, `FR-155`)*
- [X] T005 Gerar e revisar `backend/processo_seletivo/editais/migrations/0016_quadro_de_vagas.py`. **Aditiva**: cria tabela e constraints, e não altera nem remove coluna alguma. *A `FR-174` proíbe depreciar, remover ou alterar qualquer campo da `RegraNormativa`, e a Constituição proíbe migration que apague dado normativo*
- [X] T006 [P] Declarar `"/profiles/*/vacancyTable"` em `COLECOES_COM_CHAVE`, em `backend/processo_seletivo/publicacoes/domain/colecoes.py:19`, com comentário dizendo por que a declaração vem **antes** da emissão. *É a razão que a `015` registrou na `T-007` e que `colecoes.py:25-30` guarda: sem ela, `changes.py` recusa o seletor `id=`, sobra o endereçamento por posição — que o sistema proíbe —, e o primeiro Edital publicado com quadro nasce **irretificável**. Endereço de retificação não se conserta depois (`FR-170`)*
- [X] T007 [P] Em `backend/tests/unit/publicacoes/test_colecoes.py`, afirmar `colecoes.tem_chave("/profiles/*/vacancyTable")` e que ela **não** é atômica (`FR-170`)
- [X] T008 Rodar `DB_NAME=ps_demo_025 make test-pg` em `backend/` e exigir verde. *Migration desaplicada contamina a sessão inteira, e o sintoma aparece longe da causa*

**Checkpoint**: a linha existe no banco, a coleção é endereçável, e nada mudou de comportamento ainda.

---

## Phase 3: User Story 1 — Declarar o quadro que o Edital publica (Priority: P1) 🎯 MVP

**Goal**: quem compõe escreve, ao lado de cada Modalidade, quantas vagas ela tem — mais a linha da ampla concorrência.

**Independent Test**: compor um Perfil com três Modalidades, declarar o quadro, e ver as quatro quantidades gravadas e recuperáveis — **sem publicar nada**.

### Tests for User Story 1

- [X] T009 [P] [US1] Teste de unidade em `backend/tests/unit/editais/test_quadro_de_vagas.py`: três linhas declaradas, cada uma com identidade própria, gravadas e recuperáveis (`FR-153`)
- [X] T010 [P] [US1] Em `backend/tests/unit/editais/test_quadro_de_vagas.py`, segunda linha geral no mesmo Perfil é recusada, e a mensagem diz que a ampla concorrência tem uma linha só (`FR-154`)
- [X] T011 [P] [US1] Em `backend/tests/unit/editais/test_quadro_de_vagas.py`, segunda linha para a mesma Modalidade é recusada (`FR-155`); quantidade negativa e não inteira são recusadas (`FR-156`)
- [X] T012 [P] [US1] Em `backend/tests/unit/editais/test_quadro_de_vagas.py`, linha que aponta Modalidade de **outro Perfil** recusa com `"não pertence ao Perfil declarado"`, e Modalidade de Perfil nenhum recusa com `"não é de nenhum Perfil deste Edital"` — **as duas frases literais** (`FR-158`)
- [X] T013 [P] [US1] Em `backend/tests/unit/editais/test_quadro_de_vagas.py`, quadro **completo** cuja soma diverge do total recusa a submissão, e a mensagem traz os **três** números — o que soma, o que foi declarado e a diferença (`FR-161`, `UX-023`, `SC-054`)
- [X] T014 [P] [US1] Em `backend/tests/unit/editais/test_quadro_de_vagas.py`, quadro **parcial** não dispara a conferência, e Perfil **sem quadro** permanece submetível (`FR-160`, `D-006`, `D-007`). Cobrir os dois casos de borda da spec: linha geral sozinha, e só reservadas sem linha geral
- [X] T015 [P] [US1] Em `backend/tests/unit/editais/test_quadro_de_vagas.py`, um quadro **parcial** cuja soma **excede** o total é recusado, e a mensagem traz os três números — o quadro parcial que soma **menos** continua aceito (`FR-177`, `D-006`)
- [X] T016 [P] [US1] Em `backend/tests/unit/editais/test_quadro_de_vagas.py`, Perfil com total zero e quadro completo: a soma tem de dar zero, ou é recusada
- [X] T017 [P] [US1] Em `backend/tests/unit/editais/test_quadro_de_vagas.py`, o total de vagas imediatas do Perfil **não** é sobrescrito pela soma (`FR-162`)
- [X] T018 [P] [US1] Teste de interface em `backend/tests/interface/test_compor_quadro.py`: a seção do quadro aparece **dentro do cartão do Perfil**, e não em tela à parte (`UX-020`)
- [X] T019 [P] [US1] Em `backend/tests/interface/test_compor_quadro.py`, as linhas são oferecidas a partir das Modalidades já declaradas — só os campos de quantidade são editáveis, e nenhum rótulo, código ou denominação é redigitado (`UX-021`, `SC-048`)
- [X] T020 [P] [US1] Em `backend/tests/interface/test_compor_quadro.py`, a linha geral é distinguível das reservadas **sem depender de cor** e diz na tela que é a da ampla concorrência (`UX-022`)
- [X] T021 [P] [US1] Em `backend/tests/interface/test_compor_quadro.py`, quantidade em branco **não grava linha**, e a ausência não vira zero (`FR-159`, `D-006`)
- [X] T022 [P] [US1] Ampliar `backend/tests/interface/test_round_trip_do_rascunho.py` para comparar a coleção `vacancyTable` **inteira**, campo a campo, depois de gravar **outra** etapa. *É o teste que existe para pegar "o campo de que ninguém se lembrou" — nasceu do `E2E17-001`, e é a rede que apanha as quatro travessias da `T031`–`T034`*
- [X] T023 [P] [US1] Teste de contrato em `backend/tests/contract/test_edital_draft_api.py`: `vacancyTable` é aceita no rascunho e **opcional**; `id` de linha de outro Edital responde `409 identifier_belongs_to_another_edital` (`FR-160`)

### Implementation for User Story 1

- [X] T024 [US1] Escrever a validação da linha em `backend/processo_seletivo/editais/domain/perfis.py`, chamada de `validate_profile`: linha geral única, uma linha por Modalidade, quantidade inteira ≥ 0, e a referência cruzada com as **mesmas frases** de `editais/domain/documentos.py:85-89`. Recusa é `ProfileValidationError` com `campo="modalityId"` ou `"immediateVacancies"` e `identidade=<id da linha>`. *A validação mora no domínio, e não só no serializer, pela razão que `perfis.py:29-31` já registra: a interface administrativa invoca o command diretamente e não atravessa o serializer (`FR-154`–`FR-158`)*
- [X] T025 [US1] Escrever a conferência da soma em `backend/processo_seletivo/editais/domain/validation.py`, em **duas metades**: `vacancy_sum_mismatch` (impeditivo) quando o quadro é **completo** e a soma diverge — completude = linha geral presente **e** nenhuma Modalidade declarada sem linha —, e `vacancy_sum_exceeds_total` (impeditivo) quando a soma **excede** o total, em quadro completo **ou parcial** (`FR-161`, `FR-177`, `FR-162`). *A segunda metade não espera pela completude porque não precisa: nenhum Edital reserva mais vagas do que oferece, e é ela que alcança o Edital que declara Modalidade "Ampla concorrência" e por isso nunca fica completo. Calcular o total a partir das linhas segue recusado pela `D-007`*
- [X] T026 [US1] Acrescentar o finding de **aviso** `vacancy_row_percentage_divergence` em `backend/processo_seletivo/editais/domain/validation.py`, comparando a quantidade com o percentual da Regra Normativa da Modalidade. **Nunca entra em `blocking_findings`** e **nunca escreve** na quantidade. *`FR-157` proíbe derivar, calcular ou recalcular quantidade a partir de percentual; a `D-003` autoriza advertir e nada além (`FR-163`). A mesma classificação serve à segunda metade da `FR-176`: declarar linha reservada para uma Modalidade que o Edital use como ampla concorrência é **advertido, e não recusado**, porque o sistema não decide qual Modalidade é essa — a primeira metade, essa sim, é recusada pela `T004` e pela `T024` (`FR-176`, `D-004`)*
- [X] T027 [US1] Acrescentar `VacancyTableRowSerializer` e o campo `vacancyTable` (opcional) a `ProfileSerializer` em `backend/processo_seletivo/editais/api/serializers.py:93`, na forma de `contracts/quadro-de-vagas.md` §1
- [X] T028 [US1] Acrescentar `vacancyTable` e `LinhaDoQuadroInput` ao `PerfilInput` em `specs/001-processo-seletivo-editais/contracts/openapi.yaml:630`, com `required: [id, immediateVacancies]` e `modalityId` anulável. *`id` obrigatório pela razão que `ModalidadeInput` já documenta: opcional, ele reabriria o defeito que a estabilidade veio fechar*
- [X] T029 [US1] Criar as linhas em `replace_draft`, em `backend/processo_seletivo/editais/application/draft.py:218`, **preservando o `id` recebido** — como Perfil, Modalidade e Regra já fazem
- [X] T030 [US1] Acrescentar a linha ao mapa de `_identidades_aninhadas_alheias` em `backend/processo_seletivo/editais/application/draft.py:34`, conferida contra o Perfil. *Sem ela, um `id` de linha de outro Edital seria aceito na gravação e o `409` que o contrato promete não aconteceria para esta coleção — defeito silencioso (`R-008`)*
- [X] T031 [US1] **Travessia 1 de 4** — `_linhas(dados, prefixo)` e a chave `vacancyTable` em `ler_perfis`, em `backend/processo_seletivo/interface/forms.py:338`, no padrão de prefixo composto de `_modalidades`. *`_indices` (`forms.py:27`) só enxerga a linha que envia um campo `…-id`*
- [X] T032 [US1] **Travessia 2 de 4** — `perfis_persistidos` em `backend/processo_seletivo/interface/forms.py:598` passa a **reenviar** o quadro. *`replace_draft` apaga e recria tudo: o que não for reenviado ao gravar outra etapa **some**, sem erro*
- [X] T033 [US1] **Travessia 3 de 4** — `perfis_do_edital` em `backend/processo_seletivo/interface/forms.py:543` passa a reexibir o quadro na tela
- [X] T034 [US1] **Travessia 4 de 4** — conferir que a `T029` fecha a gravação, e que o quadro **não** entra em `PRESERVADO_DA_ETAPA["perfis"]` (`backend/processo_seletivo/interface/views.py:1153`). *Aquela tupla é para o que a tela não desenha, e esta tela desenha o quadro*
- [X] T035 [US1] Criar `backend/processo_seletivo/interface/templates/interface/_linha_do_quadro.html` e a seção `<section class="quadro">` dentro de `backend/processo_seletivo/interface/templates/interface/_perfil.html`, com `<h3>Quadro de vagas</h3>`. A linha geral traz rótulo textual dizendo que é a da ampla concorrência (`UX-020`, `UX-022`)
- [X] T036 [US1] Em `backend/processo_seletivo/interface/templates/interface/_perfil.html` e `backend/processo_seletivo/interface/forms.py`, derivar as linhas das Modalidades declaradas **no formulário**, e não das gravadas no banco. *Quem acrescenta uma Modalidade por htmx e digita a quantidade antes de gravar precisa ver a linha aparecer — é o mesmo comportamento que a seção de Modalidades já tem (`R-009`)*
- [X] T037 [US1] Acrescentar o fragmento htmx da linha em `backend/processo_seletivo/interface/views.py` e a rota em `backend/processo_seletivo/interface/urls.py`, no padrão de `fragmento_modalidade` (`views.py:1408`), com o índice nascendo no **servidor** via `_indice_de_linha` (`views.py:1247`). *A CSP não admite `hx-vals='js:'`, e `tests/interface/test_estaticos.py` reprova quem tentar*
- [X] T038 [US1] Acrescentar o quadro à tela de conferência em `backend/processo_seletivo/interface/revisao.py:31`, no formato que ela já usa para as demais coleções
- [X] T039 [US1] Acrescentar a asserção de largura/agrupamento em `backend/tests/interface/test_medida_dos_campos.py` para a linha do quadro, e conferir `backend/tests/interface/test_acessibilidade.py` — toda classe citada existe na folha, e todo `aria-describedby` aponta alvo existente. *`CLASSES_SEM_DESENHO` em `tests/interface/conftest.py:60` pode precisar da classe nova*

**Checkpoint**: `US1` fechada. Quatro números digitados viram três linhas gravadas, as recusas aparecem ancoradas na linha certa, e **nada foi publicado**.

---

## Phase 4: User Story 2 — Publicar o quadro como conteúdo do Edital (Priority: P1)

**Goal**: o quadro viaja no conteúdo publicado — legível por máquina, com identidade por linha — e sai no documento.

**Independent Test**: publicar um Edital com quadro declarado e ler o quadro no conteúdo publicado e no documento; publicar um Edital sem quadro e ver a seção omitida.

**⚠️ Esta fase é atômica em quatro arquivos**: emissão, `SCHEMA_VERSION`, degrau e `PERFIL_PUBLICADO` **têm de entrar juntos**. Emitir a chave antes de o degrau existir faz todo conteúdo publicado anterior falhar a verificação de forma.

### Tests for User Story 2

- [X] T040 [P] [US2] Criar `backend/tests/contract/test_elevacao_degrau_12.py` — convenção **estrita** de nome, no molde de `test_elevacao_degrau_11.py`: afirmar `DEGRAUS_DE_PERFIL[12] == {"vacancyTable": []}` e `SCHEMA_VERSION >= 12` (`FR-167`)
- [X] T041 [P] [US2] Em `backend/tests/contract/test_elevacao_degrau_12.py`, conteúdo na versão 11 eleva com `vacancyTable == []` e **nada mais do Perfil é tocado**; o Perfil que já declara quadro **não** é reescrito (idempotência); versão futura atravessa intacta (`D-005`)
- [X] T042 [P] [US2] Em `backend/tests/contract/test_elevacao_degrau_12.py`, confirmar que `elevar_valor` **não** precisa de predicado novo — a coleção nasce no degrau 12, logo não existe Alteração anterior a ela. *É o mesmo argumento que `elevacao.py:440-445` escreve para os Anexos, e vale confirmar por teste e não por leitura (`R-004`)*
- [X] T043 [P] [US2] Ampliar `backend/tests/unit/editais/test_forma_do_snapshot.py`: `vacancyTable` sai no dicionário do Perfil com `id`, `modalityId` (nulo na geral) e `immediateVacancies`, na ordem declarada (`FR-164`)
- [X] T044 [P] [US2] Teste em `backend/tests/integration/publicacoes/`: dois conteúdos publicados idênticos produzem o **mesmo** resumo canônico, com o quadro incluído nele (`FR-168`, `SC-049`)
- [X] T045 [P] [US2] Teste em `backend/tests/contract/test_documento_publicado.py`: o documento exibe o quadro na ordem declarada, com a linha geral em primeiro lugar; Perfil sem quadro **omite a seção inteira**, sem título e sem frase de ausência (`FR-169`)
- [X] T046 [P] [US2] Teste em `backend/tests/integration/publicacoes/`: um quadro cujas quantidades percentual nenhum gera — `Q 1`, `PCD 1` — é publicado e lido de volta **idêntico** (`SC-051`)
- [X] T047 [P] [US2] Teste com a fixture `backend/tests/fixtures/legado.py`: Edital publicado **antes** do degrau continua legível, `vacancyTable` é `[]`, e **nenhuma tela afirma zero vaga** — conferir vitrine, página da seleção e documento (`SC-050`)
- [X] T048 [P] [US2] Teste em `backend/tests/integration/publicacoes/`: a publicação recusa quadro cuja linha aponte Modalidade que não existe no Perfil (`FR-166`)
- [X] T049 [P] [US2] Teste em `backend/tests/unit/editais/`: uma linha copiada por `reaproveitamento` aponta a Modalidade **nova**, e não a do Edital anterior; `modalityId` nulo atravessa intocado (`R-012`)

### Implementation for User Story 2

- [X] T050 [US2] Emitir `vacancyTable` no dicionário do Perfil em `backend/processo_seletivo/publicacoes/application/publish_edital.py:169-193`, depois de `competitionModalities`, ordenando por `("ordem", "id")`. *A determinização é feita **no emissor** e não no resumo — é o que `publish_edital.py:128-130` já registra (`FR-164`, `FR-168`)*
- [X] T051 [US2] Subir `SCHEMA_VERSION` de 11 para 12 em `backend/processo_seletivo/shared/canonical.py:105`, acrescentando ao bloco de comentário a narrativa do degrau — o que a ausência significa, e por que escrevê-la não inventa nada
- [X] T052 [US2] Acrescentar `12: {"vacancyTable": []}` a `DEGRAUS_DE_PERFIL` em `backend/processo_seletivo/publicacoes/domain/elevacao.py:57`. *`elevar_perfil` já existe e já aplica; nenhuma função nova. A lista vazia diz "este Edital não publicou quadro", e é verdade sobre todos eles porque a capacidade não existia (`D-005`, `FR-167`)*
- [X] T053 [US2] Acrescentar `Campo("vacancyTable", list, tipo_do_item=dict)` a `PERFIL_PUBLICADO` em `backend/processo_seletivo/editais/domain/validation.py:90`. *Sem isto, os guardas de `tests/fixtures/snapshot.py:275` e `:301` acusam coleção não declarada. `COLECOES_PUBLICADAS` só percorre coleções de **raiz**, e o quadro é aninhado no Perfil*
- [X] T054 [US2] Declarar a forma **interna** da linha em `backend/processo_seletivo/editais/domain/validation.py` — `id`, `modalityId` anulável, `immediateVacancies` inteiro ≥ 0. *O quadro **não** herda a folga de `competitionModalities`, cuja forma de dentro não é declarada (`validation.py:88-90`): a linha carrega um número que a conferência vai somar, e somar campo não verificado é somar o que ninguém garantiu ser inteiro (`R-013`)*
- [X] T055 [US2] Criar o finding impeditivo `vacancy_row_modality_missing` em `backend/processo_seletivo/editais/domain/validation.py`, ao lado de `milestone_stage_missing` (`:638`) e `attachment_reference_dangling` (`:995`), com mensagem que **nomeia a linha**. *Ele é aplicado sem orquestração nova: `publish_edital.py:376` e `:594` já chamam `validate_for_publication` (`FR-166`)*
- [X] T056 [US2] Acrescentar `vacancyTable` e `LinhaDoQuadroPublicada` ao `PerfilPublicado` em `specs/001-processo-seletivo-editais/contracts/openapi.yaml:735`, em `properties` **e** em `required`. *`required` no publicado é a `D-005` no contrato: depois do degrau 12 todo conteúdo publicado tem a chave — vazia nos anteriores. Opcional, ela admitiria duas grafias para a ausência*
- [X] T057 [US2] Compor o bloco do quadro em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`, dentro da subseção de cada Perfil e **antes** de `_modalidades` (`:1289`): duas colunas — `Lista de concorrência`, `Vagas imediatas` —, linha geral primeiro rotulada `Ampla concorrência`, reservadas no formato `f"{name} ({code})"`, e o bloco **omitido inteiro** quando `vacancyTable` é vazia (`FR-169`)
- [X] T058 [US2] Não acrescentar coluna à tabela de `_modalidades` em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py:1289`. *Tentador e barato — ela já omite coluna sem valor (`pdf.py:1315-1318`) —, mas ela é tabela de **Modalidades**, e a linha geral não é Modalidade nenhuma: o `AC 56` não teria onde morar, que é o defeito que a `D-002` recusou no modelo de dados (`R-011`)*
- [X] T059 [US2] Threading do reaproveitamento em `backend/processo_seletivo/editais/domain/reaproveitamento.py`, nos **dois** passos: registrar o `id` da linha (`:56-67`) **e** trocar o `id` e o `modalityId` (`:95-111`). *Esquecer o segundo é o defeito silencioso da feature: a linha copiada continuaria apontando a Modalidade do Edital anterior, e nada acusa (`R-012`)*
- [X] T060 [US2] Regenerar a fixture de bytes do documento por `uv run python backend/scripts/gerar_fixture_documento.py`, e o `backend/tests/contract/fixtures/snapshot_publicado.json` se ele precisar da chave nova. *Só nesta tarefa, que é a que muda a composição **de propósito** — a asserção de bytes existe para impedir a mudança acidental de documento publicado*
- [X] T061 [US2] Rodar `DB_NAME=ps_demo_025 make test-pg` em `backend/`. *É o ponto de maior risco de regressão da feature: o degrau toca todo conteúdo publicado do acervo*

**Checkpoint**: `US2` fechada. O quadro é norma — está no conteúdo publicado, no resumo canônico e no documento —, e nenhum Edital anterior afirma zero vaga.

---

## Phase 5: User Story 3 — Retificar o quadro por identidade (Priority: P1)

**Goal**: quem retifica alcança **aquela linha**, pela identidade dela, e as demais não são tocadas.

**Independent Test**: retificar uma linha de um Edital publicado e verificar que só ela mudou, e que a versão anterior permanece legível.

**Depende de**: `US2` — não há o que retificar antes de haver conteúdo publicado com quadro.

### Tests for User Story 3

- [X] T062 [P] [US3] Criar `backend/tests/integration/publicacoes/test_quadro_na_retificacao.py`: `REPLACE /profiles/id=…/vacancyTable/id=…/immediateVacancies` altera **só aquela linha**, e o conteúdo anterior permanece legível (`FR-170`, `FR-173`, `SC-049`)
- [X] T063 [P] [US3] Em `backend/tests/integration/publicacoes/test_quadro_na_retificacao.py`, `ADD /profiles/id=…/vacancyTable/-` acrescenta linha com identidade própria, alcançável na Retificação seguinte (`FR-171`)
- [X] T064 [P] [US3] Em `backend/tests/integration/publicacoes/test_quadro_na_retificacao.py`, `REMOVE` da linha funciona, e remover a **única** linha geral é aceito — o quadro passa a ser parcial e a conferência deixa de rodar
- [X] T065 [P] [US3] Em `backend/tests/integration/publicacoes/test_quadro_na_retificacao.py`, **a recusa da `D-008`**: Retificação que remove **só** a Modalidade `PPI` é recusada nomeando a linha que a impede; a que remove a Modalidade **e** a linha no mesmo ato **passa** (`FR-172`)
- [X] T066 [P] [US3] Em `backend/tests/integration/publicacoes/test_quadro_na_retificacao.py`, endereçar `/profiles/id=…/vacancyTable/0` responde `422 positional_addressing_refused` (`FR-170`)
- [X] T067 [P] [US3] Em `backend/tests/integration/publicacoes/test_quadro_na_retificacao.py`, a conferência da soma **roda na Retificação**: alterar só a linha da `PPI` de `20` para `18`, deixando o total em `80`, é recusado com soma `78`, declarado `80`, diferença `2`; o mesmo ato contendo **também** o `REPLACE` do total passa (`FR-161`, `UX-023`). *Verificar o resultado e não a operação é o mesmo mecanismo da `T069`, e vale para os dois pares de movimentos que a feature exige — o da `D-008` e este*
- [X] T068 [P] [US3] Teste de interface em `backend/tests/interface/`: a tela de Retificação oferece a coleção do quadro, e `modalityId` aparece como **escolha entre Modalidades**, não como UUID digitado (`FR-170`, `FR-171`)

### Implementation for User Story 3

- [X] T069 [US3] Verificar em `backend/processo_seletivo/publicacoes/application/retificacoes.py` que o finding `vacancy_row_modality_missing` da `T055` já cobre a `FR-172` **sem código novo**: `_assert_well_formed` (`:515`) (`_assert_well_formed`) e `:555` (`_assert_structurally_publishable`) já chamam `validate_for_publication` sobre o conteúdo que a Retificação **produziria**. *Verificar o **resultado**, e não a operação, é o que faz "remover as duas no mesmo ato" passar e "remover só a Modalidade" ser recusado — que é literalmente o que a `D-008` pede*
- [X] T070 [US3] **NÃO** emitir alteração automática que remova a linha em `backend/processo_seletivo/interface/retificacao.py`. *Ao remover um Anexo, `interface/retificacao.py:920-966` emite sozinha o `REPLACE …/attachmentId → None`. É o padrão que se copiaria sem pensar, e aqui está proibido: lá a emissão automática **desfaz um vínculo**; aqui **apagaria uma quantidade publicada** como efeito colateral de outro movimento — a alternativa que a `D-008` recusou por escrito. A recusa é a resposta certa*
- [X] T071 [US3] Criar `CAMPOS_DA_LINHA` em `backend/processo_seletivo/interface/retificacao.py`, ao lado de `CAMPOS_MODALIDADE` (`:73`): `immediateVacancies` como `INTEIRO` e `modalityId` como `REFERENCIA`. *`REFERENCIA` oferece as Modalidades como opções — a razão está em `retificacao.py:34-41`: digitar UUID à mão faria um erro de digitação mudar em silêncio o que a linha significa*
- [X] T072 [US3] Acrescentar `"vacancyTable": []` ao `NOVO_PERFIL` (`backend/processo_seletivo/interface/retificacao.py:140`) e ao gabarito de Perfil novo (`:714-726`), ao lado de `"competitionModalities": []`
- [X] T073 [US3] Ligar o quadro ao `diferencas` de `backend/processo_seletivo/interface/retificacao.py:772-979`, para que acrescentar, alterar e remover linha na tela virem `ADD`/`REPLACE`/`REMOVE` (`FR-171`)

**Checkpoint**: `US3` fechada. A `FR-172` foi entregue **sem mecanismo novo**, e a coleção é alcançável pelo canal do ator — que é o que o Princípio VI exige.

---

## Phase 6: User Story 4 — Declarar quadro em Edital com muitos Perfis (Priority: P2)

**Goal**: o Edital de 7 polos tem quadro declarado numa sessão, sem redigitar rótulo nenhum.

**Independent Test**: compor um Edital com 7 Perfis de 3 Modalidades, declarar os 7 quadros, e **contar os campos digitados**.

**Depende de**: só da `US1`.

### Tests for User Story 4

- [X] T074 [P] [US4] Teste de interface em `backend/tests/interface/test_compor_quadro.py`: 7 Perfis × 3 Modalidades produzem **no máximo 28** campos digitáveis no total — 7 × (1 geral + 3 reservadas) —, e nenhum campo de rótulo, código ou denominação (`SC-052`, `UX-021`)
- [X] T075 [P] [US4] Em `backend/tests/interface/test_compor_quadro.py`, gravar os 7 quadros numa submissão só e recuperar as 28 quantidades intactas
- [X] T076 [P] [US4] Em `backend/tests/interface/test_compor_quadro.py`, com 7 Perfis, deixar **uma** quantidade em branco e conferir que só aquela linha deixa de existir — as outras 27 permanecem (`FR-159`, `D-006`)

### Implementation for User Story 4

- [X] T077 [US4] Conferir a ordem de tabulação através dos 7 cartões de `backend/processo_seletivo/interface/templates/interface/_perfil.html`, com asserção em `backend/tests/interface/test_acessibilidade.py`: a seção do quadro de um Perfil é atravessada inteira antes da do seguinte, e nenhum campo fica inalcançável pelo teclado. *A Constituição exige teclado e prevenção de erro, e o Edital grande é onde isso deixa de ser detalhe*
- [X] T078 [US4] Conferir que a página com 7 Perfis não regride em `backend/tests/interface/test_estaticos.py` — índices de fragmento distintos, nenhum `hx-vals='js:'`, nenhuma sintaxe de template vazando
- [X] T079 [US4] Medir o número de consultas ao gravar e ao emitir com 7 Perfis, e conferir que o quadro entra no `prefetch_related` de `backend/processo_seletivo/publicacoes/application/publish_edital.py:99` — **sem consulta nova por Perfil**

**Checkpoint**: `US4` fechada. O Edital grande é suportável, e a medida está num teste em vez de numa impressão.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [X] T080 [P] Escrever os testes dos **oito invariantes** da §5 da spec em `backend/tests/unit/editais/test_invariantes_do_quadro.py`, cada um nomeando o invariante que verifica. Os **três** que precisam de teste de **ausência**: nenhum caminho deriva quantidade de percentual (`FR-157`); nenhum caminho oferece o quadro como anexo binário — nem na composição, nem na Retificação, nem no documento (`FR-165`, `D-001`); e nenhuma tela atribui pessoa a linha (`FR-175`)
- [X] T081 [P] Ampliar `backend/tests/acceptance/test_us2_perfis.py` com o ciclo completo do `57/2026`: declarar `AC 56`, `PcD 4`, `PPI 20`, publicar, e retificar `PPI 20 → 18` **junto com o total do Perfil, 80 → 78**, sem que nenhuma outra linha mude e sem recálculo (`SC-049`, `SC-053`)
- [X] T082 [P] Criar `specs/025-quadro-de-vagas-por-modalidade/rastreabilidade.md`. *`tests/test_citacoes_de_requisito.py::test_a_matriz_de_rastreabilidade_cobre_todo_requisito_da_feature` exige que, **onde a matriz existir**, ela cubra `FR-153`–`FR-177`, `SC-048`–`SC-054` e `UX-020`–`UX-023`. Intervalos são aceitos; sufixo de letra, não*
- [X] T083 Acrescentar a entrada `quadro-025` ao `.claude/launch.json` — **acrescentar**, sem reescrever o arquivo, que é versionado e carrega entradas de outras sessões. Porta 8025, `DB_NAME=ps_demo_025`, `INTERFACE_SELETOR_IDENTIDADE=true`, e `localhost` na `url`
- [X] T084 Percorrer o [quickstart.md](./quickstart.md) inteiro contra o servidor real, montando o Edital à mão pela interface. *`seed_demo` **não** produz este certame — o elenco dele colide com o que o percurso precisa*
- [X] T085 Escrever `doc/e2e/025-quadro-de-vagas/relatorio.md` com as capturas em `screenshots/`. Cada achado ganha identificador `E2E25-NNN`, citado na docstring do teste que o fecha. *Esses identificadores não casam com a varredura de citações e podem ser usados livremente*
- [X] T086 Rodar `cd backend && DB_NAME=ps_demo_025 make lint check test-pg`. *`lint` são **dois** passos — `ruff check` **e** `ruff format --check`; rodar só o primeiro declara verde local e quebra no CI. `test-pg` e não `test`: sem `TEST_DB_ENGINE=postgresql` **e** `DB_USER` a suíte cai para SQLite, 21 falham, 182 são pulados, e nada avisa*
- [X] T087 Rodar `uv run pytest tests/test_citacoes_de_requisito.py` em `backend/`. *A varredura lê `specs/` e `backend/**`: qualquer `FR-`, `SC-`, `UX-` ou `D-` citado em comentário, docstring ou template tem de existir em alguma spec*

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (T001–T002)**: sem dependência. Libera o nome antes que alguém o use
- **Foundational (T003–T008)**: depende do Setup. **Bloqueia todas as user stories**
- **US1 (T009–T039)**: depende da Foundational
- **US2 (T040–T061)**: depende da Foundational. **Não** depende da `US1` para existir, mas o percurso só faz sentido com ela
- **US3 (T062–T073)**: depende da **US2** — não há o que retificar antes de haver conteúdo publicado com quadro
- **US4 (T074–T079)**: depende só da **US1**
- **Polish (T080–T087)**: depende de todas

```text
Setup ──▶ Foundational ──┬──▶ US1 ──┬──▶ US4 ──┐
                         │          │          ├──▶ Polish
                         └──▶ US2 ──┴──▶ US3 ──┘
```

### A ordem que a spec sugere, e por quê

`US1` → `US2` → `US3` → `US4`. A **1** entrega a lacuna e demonstra valor sem publicar; a **2** é o
que torna o quadro norma; a **3** é o passo emblemático; a **4** torna o Edital grande suportável.

A **3** concentra o risco de projeto — é onde o precedente errado está à mão. A **2** concentra o
risco de regressão — o degrau toca todo o acervo publicado.

### Fases que são atômicas por dentro

- **T050–T054** entram **juntas**. Emitir a chave sem o degrau faz todo conteúdo publicado anterior
  falhar a verificação de forma; subir o degrau sem emitir deixa a chave existindo só na conversão.
- **T031–T034** entram **juntas**. Uma travessia sozinha não faz o quadro sobreviver à gravação da
  etapa seguinte, e o sintoma aparece longe da causa.

### Parallel Opportunities

- `T006` e `T007` correm juntas
- Todos os testes de uma mesma user story marcados `[P]` correm juntos — arquivos distintos
- `T009`–`T023` (os quinze testes da `US1`) correm todos em paralelo
- `T040`–`T049` (os dez testes da `US2`) correm todos em paralelo
- `T080`, `T081` e `T082` correm juntas
- As tarefas de implementação **dentro** de uma story são majoritariamente sequenciais: `forms.py`,
  `validation.py` e `pdf.py` são tocados por mais de uma tarefa cada

---

## Parallel Example: User Story 1

```bash
# Os testes de domínio, todos no mesmo arquivo novo — escrever juntos, rodar juntos:
Task: "T009 três linhas com identidade própria"
Task: "T010 segunda linha geral recusada"
Task: "T011 segunda linha por Modalidade recusada; quantidade inválida recusada"
Task: "T012 as duas frases literais da referência cruzada"
Task: "T013 a divergência dita em três números"

# Os testes de interface, em arquivo distinto — em paralelo com os de cima:
Task: "T018 a seção mora dentro do cartão do Perfil"
Task: "T019 só quantidades são digitadas"
Task: "T020 a linha geral é distinguível sem cor"
```

---

## Implementation Strategy

### MVP (US1 apenas)

1. Setup (`T001`–`T002`) — libera o nome
2. Foundational (`T003`–`T008`) — a entidade e o endereçamento
3. `US1` (`T009`–`T039`)
4. **PARE E VALIDE**: componha um Perfil de três Modalidades, declare o quadro, grave outra etapa,
   volte, e confira que as quatro quantidades continuam lá
5. É entregável: quem compõe passa a ter onde escrever o número que separa o certame de existir

### Entrega incremental

1. Setup + Foundational → a fundação está posta, e nada mudou de comportamento
2. `US1` → declarar (**MVP**)
3. `US2` → publicar; é aqui que o quadro vira norma, e é aqui que mora o risco de regressão
4. `US3` → retificar; é o passo que separa esta feature de uma coluna a mais numa tabela
5. `US4` → o Edital grande deixa de ser insuportável

### Sobre trabalhar em paralelo

`US2` pode começar junto com `US1` — arquivos distintos, e a emissão não depende da tela. `US3` não
pode: ela precisa de conteúdo publicado com quadro. `US4` só precisa da `US1`.

---

## Notes

- `[P]` = arquivos distintos, sem dependência pendente
- **Um achado encontrado durante a implementação vira registro, não escopo.** A governança é do
  usuário, e a `R-006` já é um exemplo: a conferência da `FR-161` não roda no Edital que declara uma
  Modalidade chamada "Ampla concorrência", e o plano deliberadamente não escolheu a saída
- **Nada aqui deprecia campo algum da `RegraNormativa`** (`D-003`, `FR-174`). Se alguma tarefa levar
  você a remover `percentage`, `calculation`, `rounding` ou `distribution`, a tarefa foi mal lida
- **Nada aqui ocupa vaga, convoca ou corta** (`FR-175`). É o corte que a spec repete duas vezes, e o
  mais tentador de violar
- Commit por tarefa ou grupo lógico; parar em qualquer checkpoint valida a story sozinha
