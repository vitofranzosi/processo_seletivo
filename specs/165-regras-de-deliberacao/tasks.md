# Tasks: As regras de deliberação dos pareceres

**Input**: Design documents from `specs/165-regras-de-deliberacao/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: sim. Cada SC e cada recusa do contrato tem teste, contra PostgreSQL, como em toda feature
deste repositório. Os caminhos são relativos a `backend/`.

**Organization**: por história da spec. As histórias P1 (US1, US2, US3) dependem da fundação; as P2
(US4, US5, US6) dependem da US3, porque leem o Resultado deliberado.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [X] T001 Criar o banco de teste próprio da worktree (`DB_NAME=gps_165`) e conferir `manage.py migrate --check` limpo antes de mexer, registrando a linha de base da suíte de `tests/unit/resultados` e `tests/integration/resultados`

---

## Phase 2: Foundational (bloqueia todas as histórias)

- [X] T002 [P] Criar o domínio puro em `processo_seletivo/resultados/domain/deliberacao.py`: `REGRAS`, `PUBLICADO`, `para_coluna`, `da_coluna`, `regra_publicada(etapa)`, `colegiada(etapa)`, `deliberar(regra, sentidos)`, o valor `Deliberacao` (forma, sentido, pontuacao, favoraveis, desfavoraveis, pareceres, versao_id), `motivo(etapa, deliberacao)`, `frase_da_regra(etapa)`, `opcoes_da_regra(etapa)` e `publicar(item, coluna)`, com as frases de `contracts/frases.md` (T-007)
- [X] T003 [P] Testes unitários da tabela-verdade em `tests/unit/resultados/test_deliberacao.py`: três e cinco pareceres, todas as combinações, as três regras; o motivo de cada caminho; a frase da regra com e sem rótulos; `publicar` só na colegiada (SC-2351, FR-7050, FR-7061, FR-7066, FR-7075)
- [X] T004 Acrescentar `regra_de_deliberacao` a `EtapaAvaliacao` em `processo_seletivo/editais/models/etapas.py`, com `ck_etapa_regra_de_deliberacao`, e gerar `processo_seletivo/editais/migrations/0031_regra_de_deliberacao.py` (T-001)
- [X] T005 Subir `SCHEMA_VERSION` para 24 em `processo_seletivo/shared/canonical.py` e acrescentar `DEGRAUS[24] = {"deliberationRule": None}` em `processo_seletivo/publicacoes/domain/elevacao.py` (T-001, FR-7054)
- [X] T006 Acrescentar `("stages", "deliberationRule"): retificavel()` em `processo_seletivo/editais/domain/mutabilidade.py`, e o rótulo em `processo_seletivo/publicacoes/domain/alteracoes.py` (FR-7055)
- [X] T007 Acrescentar a origem `DELIBERACAO`, `regra_de_deliberacao`, `favoraveis`, `desfavoraveis`, `ck_resultado_deliberacao` e o modelo `ParecerDaDeliberacao` em `processo_seletivo/resultados/models.py` (T-005)
- [X] T008 Escrever `processo_seletivo/resultados/migrations/0008_deliberacao.py`: campos, constraint, tabela, os gatilhos `parecer_da_deliberacao_append_only`, `parecer_da_deliberacao_coerente`, a reescrita de `resultado_etapa_coerente` e o `CONSTRAINT TRIGGER` adiável `resultado_deliberado_completo` (T-006)
- [X] T009 Acrescentar o modelo `ExposicaoAoParecer` em `processo_seletivo/avaliacoes/models.py` e `processo_seletivo/avaliacoes/migrations/0006_exposicao_ao_parecer.py`, com o gatilho append-only (T-014)
- [X] T010 Acrescentar as duas tabelas a `TABELAS_APPEND_ONLY` em `processo_seletivo/seguranca/papeis.py` e atualizar a contagem por app e os gatilhos esperados em `tests/migrations/test_migrations.py` (T-018)
- [X] T011 Testes dos gatilhos em `tests/integration/resultados/test_gatilhos_da_deliberacao.py`: Resultado deliberado sem pareceres recusado no `COMMIT`; contagem divergente recusada; parecer de outra inscrição ou Etapa recusado; Avaliação já citada por Resultado recusada nos dois sentidos; `UPDATE`/`DELETE` recusados nas duas tabelas novas (FR-7065)

**Checkpoint**: a fundação está pronta; o banco recusa toda deliberação incoerente.

---

## Phase 3: User Story 1 — Quem elabora declara como a comissão decide (P1) 🎯 MVP

**Goal**: a regra entra na composição, no conteúdo publicado e no documento, com os achados de
publicação.

**Independent Test**: compor a Etapa com cada regra, publicar, conferir o conteúdo, a Revisão e o
documento; conferir as recusas sem regra, com maioria par e em Etapa não colegiada.

### Tests for User Story 1

- [X] T012 [P] [US1] Testes da composição em `tests/interface/test_composicao_da_deliberacao.py`: a pergunta só na decisória, nenhuma opção marcada, a regra gravada e relida pelo cartão e por `etapas_persistidas`, a escolha ignorada com uma avaliação (UX-750, FR-7050, FR-7053)
- [X] T013 [P] [US1] Testes dos achados em `tests/unit/editais/test_deliberacao_na_publicacao.py`: `regra_invalida`, `regra_sem_colegiado`, `maioria_com_numero_par` e `deliberacao_sem_regra`, este só no ato de publicação (FR-7051 a FR-7053, contracts/recusas.md)
- [X] T014 [P] [US1] Testes do documento em `tests/interface/test_composicao_da_deliberacao.py` (o plano previa um arquivo próprio): a frase nos dois modos do PDF, na apresentação plana e na Revisão; as demais Etapas sem frase; recomposição do acervo com o mesmo resumo canônico (FR-7075, SC-2350)

### Implementation for User Story 1

- [X] T015 [US1] Validar a forma de `deliberationRule` na gravação em `processo_seletivo/editais/domain/etapas.py`, e levá-la em `processo_seletivo/editais/api/serializers.py` e `processo_seletivo/editais/application/draft.py`
- [X] T016 [US1] Publicar `deliberationRule` por `deliberacao.publicar` em `processo_seletivo/publicacoes/application/publish_edital.py` (T-002)
- [X] T017 [US1] Acrescentar o `Campo` publicado e `_coerencia_da_deliberacao` em `processo_seletivo/editais/domain/validation.py`, com `deliberacao_sem_regra` só no ato de publicação (T-003)
- [X] T018 [US1] Ler e reler o campo em `processo_seletivo/interface/forms.py` (`ler_etapas`, `etapas_do_edital`, `etapas_persistidas`), e desenhar o grupo de rádios em `processo_seletivo/interface/templates/interface/_etapa.html`, com a classe `so-colegiada` alternada pelo script da composição e a regra na folha (T-015)
- [X] T019 [US1] Escrever a frase da regra em `processo_seletivo/publicacoes/infrastructure/pdf.py` (os dois modos), `processo_seletivo/publicacoes/infrastructure/apresentacao.py` e `processo_seletivo/interface/revisao.py` (linha "Deliberação", e `_LIDOS_POR_COLECAO`) (T-016)
- [X] T020 [US1] Acrescentar o campo e as opções da regra em `CAMPOS_ETAPA` de `processo_seletivo/interface/retificacao.py` (T-016)

**Checkpoint**: um Edital com a Heteroidentificação colegiada é composto e publicado com a regra.

---

## Phase 4: User Story 3 — A deliberação aplica a regra publicada (P1)

**Goal**: a Etapa colegiada deixa de ser impedida; a prontidão espera os N pareceres; a consolidação
cria o Resultado deliberado.

**Independent Test**: consolidar a mesma combinação de pareceres sob cada regra e comparar sentido,
consequência, motivo, pareceres citados e versão.

### Tests for User Story 3

- [X] T021 [P] [US3] Testes de `regra.py` em `tests/unit/resultados/test_regra.py` (acrescentar): a colegiada não é impedida; a pontuada com N>1 e a decisória com N>1 sem regra continuam com `REGRA_DE_COMBINACAO_AUSENTE`; a consequência da `Deliberacao` com o efeito da `164` (FR-7064)
- [X] T022 [P] [US3] Testes de integração em `tests/integration/resultados/test_consolidacao_deliberada.py`: aguardando pareceres com "faltam k de N"; nenhuma antecipação; pronta com N; não consolidável com mais de N e com parecer incompatível; o Resultado `DELIBERACAO` com os N pareceres, a regra, a contagem, a versão vigente e o motivo; retirada da reserva completada como na `164`; a reprodução chega à mesma consequência; o evento da trilha diz a consequência sem regra nem contagem (FR-7060); a Etapa de uma avaliação inalterada; a prévia da classificação sem deliberação e com a equivalência de hoje (FR-7061 a FR-7068, FR-7080, SC-2351, SC-2353)
- [X] T023 [P] [US3] Teste da conferência em `tests/interface/test_conferencia_da_deliberacao.py`: a linha "«desfecho» — k de N pareceres …" e o total por desfecho; a contagem "aguardando pareceres" no resumo da Etapa (UX-752, FR-7079)

### Implementation for User Story 3

- [X] T024 [US3] Aceitar a Etapa colegiada em `impedimento_da_regra` e a `Deliberacao` em `consequencia` de `processo_seletivo/resultados/domain/regra.py` (T-007)
- [X] T025 [US3] Acrescentar `AGUARDANDO_PARECERES`, o ramo colegiado de `_estado_do_participante` e a contagem `aguardando_pareceres` em `processo_seletivo/resultados/application/prontidao.py`, e mostrar a contagem no resumo da Etapa (T-008)
- [X] T026 [US3] Montar a `Deliberacao` em `_planejar` e criar o Resultado `DELIBERACAO` e os `ParecerDaDeliberacao` em `consolidar`, em `processo_seletivo/resultados/application/consolidacao.py`, com a versão vigente lida uma vez (T-009)
- [X] T027 [US3] Acrescentar `resultados_por_avaliacao_registrados` e `pareceres_da_deliberacao` em `processo_seletivo/resultados/application/selectors.py`, e a reprodução `reproduzir_deliberacao(resultado)` (FR-7065)
- [X] T028 [US3] Mostrar a contagem por inscrição na conferência, em `processo_seletivo/interface/views.py` (`consolidar_resultados`) e no template da confirmação (T-017)

**Checkpoint**: a Heteroidentificação colegiada produz Resultados; o efeito da `164` se aplica.

---

## Phase 5: User Story 2 — Cada membro dá o parecer sem ver o dos outros (P1)

**Goal**: o servidor nega o parecer alheio a quem tem parecer pendente; a exposição barra a atribuição
e a reabertura.

**Independent Test**: com um ator presidência e membro pendente, percorrer conclusões preservadas,
impedimentos, conferência, link direto e fragmento; depois tentar atribuir a uma pessoa exposta e
reabrir parecer de autor exposto.

### Tests for User Story 2

- [X] T029 [P] [US2] Testes em `tests/integration/avaliacoes/test_parecer_as_cegas.py`: pendentes; ocultação nos seletores de conclusões preservadas e inelegíveis; nenhuma contagem por sentido para a inscrição pendente; as outras inscrições como hoje; registro da exposição só de conclusões de outro autor; a Etapa de uma avaliação sem ocultação nem exposição (FR-7056, FR-7082, SC-2352)
- [X] T030 [P] [US2] Testes de interface em `tests/interface/test_parecer_as_cegas_na_gestao.py`: as views de conclusões preservadas e impedimentos, com HTML e fragmento, para o ator pendente; a frase "Oculto: …"; a Mesa sem nada de outros membros, antes e depois de concluir, e com as frases da UX-751 e da UX-754; a Mesa continua mostrando os dados do candidato (FR-7056, FR-7057, FR-7059, UX-751, UX-754)
- [X] T031 [P] [US2] Testes em `tests/integration/avaliacoes/test_exposicao.py`: distribuição e rodízio recusam o exposto com o motivo do contrato; a reabertura de parecer de autor exposto é recusada e a de autor não exposto volta à pendência (FR-7058, FR-7082, FR-7083)

### Implementation for User Story 2

- [X] T032 [US2] Criar `processo_seletivo/avaliacoes/application/cegas.py`: `pendentes`, `ocultar`, `registrar_exposicao`, `expostos` (T-013, T-014)
- [X] T033 [US2] Aplicar o às cegas em `conclusoes_preservadas` e `avaliacoes_inelegiveis` de `processo_seletivo/avaliacoes/application/selectors.py`, recebendo o `subject` do ator e só na Etapa colegiada
- [X] T034 [US2] Passar o ator, registrar a exposição e desenhar a linha oculta nas views de conclusões preservadas, impedimentos e consolidação em `processo_seletivo/interface/views.py`, e em `processo_seletivo/interface/templates/interface/conclusoes.html` e `impedimentos.html`
- [X] T035 [US2] Recusar o membro exposto em `distribuir` e no rodízio, em `processo_seletivo/avaliacoes/application/distribuicao.py`, e a reabertura de parecer de autor exposto em `processo_seletivo/avaliacoes/application/avaliacao.py`, com a oferta da inativação na tela
- [X] T036 [US2] Escrever as frases da UX-751 e da UX-754 na Mesa da Etapa colegiada, em `processo_seletivo/interface/templates/interface/mesa_inscricao.html` e na view que a monta

**Checkpoint**: a independência dos pareceres é garantida no servidor.

---

## Phase 6: User Story 6 — A Retificação da regra não muda a decisão no meio do caminho (P2)

**Goal**: as três recusas da Retificação.

**Independent Test**: retificar a regra e o número antes e depois do primeiro Resultado; compor uma
Etapa colegiada sem regra por Retificação; reduzir o número abaixo das conclusões.

### Tests for User Story 6

- [X] T037 [P] [US6] Testes em `tests/integration/publicacoes/test_retificacao_da_deliberacao.py`: a troca passa antes do primeiro Resultado e os pareceres continuam; recusada depois, contando superados; a redução abaixo das conclusões recusada com a contagem; a Etapa colegiada composta sem regra recusada; a Retificação que não toca a Etapa do acervo sem regra passa; a Retificação que declara a regra destrava o acervo (FR-7051, FR-7054, FR-7073, FR-7074, SC-2354)

### Implementation for User Story 6

- [X] T038 [US6] Acrescentar `_recusar_colegiada_sem_regra`, `_recusar_deliberacao_mudada_apos_resultado` e `_recusar_reducao_abaixo_das_conclusoes` em `processo_seletivo/publicacoes/application/retificacoes.py` (T-003, T-004)

---

## Phase 7: User Story 5 — O recurso corrige o desfecho, e não refaz a votação (P2)

**Goal**: a correção fixada contra o Resultado deliberado; a reavaliação recusada; o impedimento e a
instrução com os pareceres.

**Independent Test**: julgar recursos contra um Resultado deliberado com cada espécie.

### Tests for User Story 5

- [X] T039 [P] [US5] Testes em `tests/integration/recursos/test_recurso_da_deliberacao.py`: correção fixada cria o sucessor `RECURSO` sem tocar os pareceres; reavaliação recusada sem gravar decisão nem reserva; indeferimento como hoje; vedação de piora; impedidos os autores dos pareceres e quem tem parecer pendente; a Etapa de uma avaliação com reavaliação como hoje; a instrução com todos os pareceres e a autoria (FR-7069 a FR-7072, FR-7081)

### Implementation for User Story 5

- [X] T040 [US5] Recusar `REAVALIACAO_DETERMINADA` na Etapa colegiada antes de `_gravar`, em `processo_seletivo/recursos/application/julgar.py`, e esconder a espécie na tela de julgamento com a frase do contrato (T-010)
- [X] T041 [US5] Ler os pareceres da deliberação e as pendências em `processo_seletivo/recursos/domain/elegibilidade.py`, `processo_seletivo/recursos/application/instruir.py` e `processo_seletivo/interface/supervisao.py` (T-011)

---

## Phase 8: User Story 4 — O candidato entende como a comissão decidiu (P2)

**Goal**: o titular lê a regra, a contagem e os pareceres desfavoráveis sem autoria; a parte pública,
nada disso.

**Independent Test**: abrir o acompanhamento e a publicação do marco sob cada regra, dentro e fora das
condições da `036`.

### Tests for User Story 4

- [X] T042 [P] [US4] Testes em `tests/integration/recursos/test_recurso_da_deliberacao.py` (o plano previa `tests/integration/portal/test_deliberacao_ao_titular.py`; o seletor do titular é de `recursos`, e o teste ficou ao lado dos do recurso): a linha com regra e contagem; os textos desfavoráveis, sem autoria e à parte do motivo; os favoráveis só na contagem; as condições de prazo e de recurso pendente; o texto da conclusão que fundamentou; a publicação do marco sem regra, contagem nem pareceres; o texto diz "a comissão decidiu", nunca "o avaliador" (FR-7076 a FR-7078, FR-7081, UX-753)

### Implementation for User Story 4

- [X] T043 [US4] Devolver a lista de textos desfavoráveis do Resultado deliberado em `pareceres_do_titular`, em `processo_seletivo/recursos/application/selectors.py`, e desenhá-la em `processo_seletivo/portal/templates/portal/acompanhamento.html` (T-012)
- [X] T044 [US4] Estender `_recusar_se_fundamenta_resultado` em `processo_seletivo/avaliacoes/application/avaliacao.py` aos pareceres ligados a Resultado deliberado (T-012)

---

## Phase 9: Polish & Cross-Cutting Concerns

- [X] T045 [P] Conferir o inventário de `tests/test_leitores_da_consequencia.py` e acrescentar os leitores novos, se houver (T-018)
- [X] T046 [P] Atualizar o `M` de 59 para 61 no `CLAUDE.md` (a lista dos degraus), e a linha da `165` no `README.md`
- [X] T047 [P] Atualizar a matriz `specs/165-regras-de-deliberacao/rastreabilidade.md` (requisito → teste)
- [X] T048 Rodar `make lint check` e a suíte inteira contra PostgreSQL com `DB_NAME=gps_165`, e corrigir o que quebrar
- [X] T049 Validar o roteiro de `quickstart.md`
- [X] T050 [P] Registrar na nota de faixas da família de sessões que a Visão do Sistema documenta a `165` no merge, e não na branch

---

## Dependencies & Execution Order

- **Setup (T001)** → **Fundação (T002–T011)** → histórias.
- **US1** e **US3** dependem só da fundação. **US2** depende da US3 (a conferência é uma das telas
  ocultas). **US6** depende da US3 (conta Resultados deliberados). **US5** e **US4** dependem da US3.
- Dentro de cada história: testes primeiro, depois a implementação.

### Parallel Opportunities

- T002 e T003 com T004–T009 (arquivos diferentes).
- Os testes de cada história (marcados [P]) entre si.
- US5 e US4 em paralelo depois da US3.

## Implementation Strategy

1. **MVP**: Fundação + US1 + US3. A Heteroidentificação colegiada é composta, publicada e consolidada.
2. **Independência**: US2.
3. **Norma e recurso**: US6, US5.
4. **Candidato**: US4.
5. **Polimento**: guardiões, documentação e a suíte inteira.
