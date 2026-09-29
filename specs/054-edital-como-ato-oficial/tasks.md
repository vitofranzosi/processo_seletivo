# Tasks: O Edital do sistema como ato oficial

**Input**: Design documents from `specs/054-edital-como-ato-oficial/`

**Tests**: pedidos — a rastreabilidade é verificada por teste, e cada requisito aponta o que o prende
([rastreabilidade.md](rastreabilidade.md)).

Caminhos relativos a `backend/` quando começam por `processo_seletivo/` ou `tests/`.

## Phase 1: Setup

- [X] T001 Banco de teste próprio (`DB_NAME=ps_054`, `.env` da worktree) e `uv sync --extra dev`; a linha de base é a do AGENTS.md (8822 passando, 11 pulados, na `main` de 29/09), e não foi medida de novo

## Phase 2: Foundational (bloqueia todas as histórias)

**A topologia primeiro** (plan, *O prazo*): o catálogo novo sem ela tranca a Retificação do acervo.

- [X] T002 `validate_for_publication(..., topologia=None)` e `_topologia_das_secoes(snapshot, referencia)` conferem chave, título, ordem, espécie e origem contra a referência (padrão: o catálogo vigente), e aceitam textual com `content` texto vazio, em processo_seletivo/editais/domain/validation.py (R-002, R-004; FR-982, FR-987, FR-988)
- [X] T003 `retificacoes.py` passa a topologia do conteúdo original (`_original_version`) nos três pontos que validam com `ATO_DE_RETIFICACAO` (`_assert_well_formed` nos dois chamadores e `advertencias_do_ato`), em processo_seletivo/publicacoes/application/retificacoes.py (R-004)
- [X] T004 A mensagem de "não retificável" de título, ordem e espécie deixa de dizer "os mesmos em todo Edital do Cefor", em processo_seletivo/editais/domain/mutabilidade.py (R-004)
- [X] T005 O catálogo de 22 entradas, sem `default_text`, na ordem de FR-980, com as chaves de R-001, em processo_seletivo/editais/domain/secoes.py; o snapshot do rascunho emite `content: ""` para a textual sem linha, em processo_seletivo/publicacoes/application/publish_edital.py; `ler_secoes` grava só o texto não vazio, em processo_seletivo/interface/forms.py (FR-980, FR-981, FR-983)
- [X] T006 `_materializaveis` pula a textual vazia sem norma acrescentada; `numeracao(snapshot)` pública, derivada dela, em processo_seletivo/publicacoes/infrastructure/pdf.py (R-003; FR-982, FR-984, FR-985)
- [X] T007 Emendar os testes que prendiam o catálogo de 12, a redação padrão e a textual obrigatória — tests/unit/editais/test_secoes.py, tests/unit/editais/test_secao_de_recursos.py, tests/unit/publicacoes/test_pdf.py, tests/unit/publicacoes/test_pdf_documentos_exigidos.py, tests/contract/test_edital_draft_api.py, tests/contract/test_forma_publicada.py, tests/contract/test_enderecamento_api.py, tests/contract/test_limites_de_borda.py, tests/interface/test_compor.py, tests/interface/test_retificar.py, tests/integration/editais/test_reaproveitamento.py e os demais que a suíte acusar —, um a um, sem afrouxar invariante

**Checkpoint**: suíte verde com o catálogo novo; a fixture de bytes ainda acusa a mudança (T030).

## Phase 3: User Story 1 — Transcrever sem que norma caia em seção errada (P1) 🎯 MVP

**Independent Test**: compor o 28/2026 com as seções do original, gerar a prévia e conferir as 15, sem vazias e com numeração contínua.

- [X] T008 [P] [US1] Testes do catálogo e da numeração: ordem de FR-980 (Perfis antes da Inscrição), nenhuma textual com padrão, textual vazia fora do documento, numeração contínua com textuais e geradas vazias intercaladas, `numeracao` igual ao que o compositor imprime, em tests/unit/editais/test_catalogo_da_054.py (FR-980–FR-985; SC-361, SC-362, SC-363)
- [X] T009 [P] [US1] Testes dos avisos: Apresentação e Disposições Finais vazias avisam só no ato de publicação, e o aviso da redação padrão não existe mais, em tests/unit/editais/test_avisos_do_documento_oficial.py (FR-986)
- [X] T010 [US1] Trocar `_secao_com_redacao_padrao` por `_secao_universal_vazia` (código `section_universal_empty`) em processo_seletivo/editais/domain/validation.py; o rótulo em processo_seletivo/interface/templatetags/interface_extras.py; o destino na etapa Conteúdo em processo_seletivo/interface/views.py (R-013; FR-986)
- [X] T011 [US1] `secoes_do_edital` devolve o número (T006) e a norma acrescentada de cada seção, a partir do snapshot do rascunho, em processo_seletivo/interface/forms.py e no contexto da etapa em processo_seletivo/interface/views.py (R-014; FR-985, UX-132)
- [X] T012 [US1] A etapa Conteúdo mostra número ou *"Vazia — não sai no documento"*, sem "Redação institucional padrão", com a norma acrescentada como ajuda do campo e os atributos `data-` da numeração, em processo_seletivo/interface/templates/interface/compor_conteudo.html (UX-130, UX-131, UX-132, UX-133)
- [X] T013 [US1] `conteudo.js`: a regra pura da numeração, exportável, e o que atualiza a legenda ao digitar, em processo_seletivo/interface/static/interface/conteudo.js, com testes em tests/javascript/conteudo.test.js (UX-130)
- [X] T014 [US1] A Revisão numera a seção pelo número do documento e diz *"Vazia — não sai no documento"*, em processo_seletivo/interface/revisao.py (FR-985)
- [X] T015 [US1] Testes da tela: número igual ao do documento, estado da vazia, ausência do padrão, norma acrescentada, rótulo acessível, em tests/interface/test_conteudo_da_054.py (UX-130–UX-133; SC-363)

**Checkpoint**: US1 demonstrável pela prévia.

## Phase 4: User Story 2 — O fecho de um ato, sem inventar nome (P1)

**Independent Test**: publicar e ler o fecho; acrescentar nome e ato de nomeação ao catálogo, publicar de novo e ler.

- [X] T016 [P] [US2] `humano.data_por_extenso`, com teste de mês, dia sem zero e fuso institucional perto da meia-noite, em processo_seletivo/publicacoes/infrastructure/humano.py e tests/unit/publicacoes/test_humano_data.py (R-006)
- [X] T017 [US2] `Autoridade(chave, identificador, cargo, nome="", ato_de_nomeacao="")`, as três entradas só com o cargo, `__str__` e `quem_assinou`, em processo_seletivo/publicacoes/domain/autoridades.py (R-008, R-009; FR-992)
- [X] T018 [US2] `Publicacao.signatory_appointment` e a migration 0009, em processo_seletivo/publicacoes/models.py e processo_seletivo/publicacoes/migrations/; subir a contagem com a justificativa em tests/migrations/test_migrations.py (R-007; FR-991)
- [X] T019 [US2] `AutoridadeSignataria` com `ato_de_nomeacao`; `render_edital_pdf(..., data_do_ato=None)` com a regra de presença por modo; o fecho `LOCAL, data.` e o bloco de autoridade de FR-993, em processo_seletivo/publicacoes/infrastructure/pdf.py (R-005; FR-989, FR-990, FR-993)
- [X] T020 [US2] Os dois fluxos passam `data_do_ato` (do `now`, na zona institucional) e gravam `signatory_appointment`, em processo_seletivo/publicacoes/application/publish_edital.py e processo_seletivo/publicacoes/application/retificacoes.py; a interface monta o signatário com o ato de nomeação, em processo_seletivo/interface/views.py (FR-990, FR-991)
- [X] T021 [US2] API: `signatory.appointment` opcional na publicação e devolvido na consulta pública, em processo_seletivo/publicacoes/api/serializers.py e processo_seletivo/publicacoes/api/public_serializers.py, e no contrato specs/001-processo-seletivo-editais/contracts/openapi.yaml (`SignatorySnapshot`); `quem_assinou` em processo_seletivo/publicacoes/application/selectors.py (R-007, R-009; FR-994)
- [X] T022 [US2] Testes do fecho e da Publicação: local e data no publicado, recusa na prévia, SHA-256 do conteúdo igual em duas datas, cargo sem nome, nome e ato de nomeação quando o catálogo os tiver, registro na Publicação, telas sem separador pendurado, em tests/unit/publicacoes/test_fecho_do_ato.py e tests/integration/publicacoes/test_fecho_publicado.py (FR-989–FR-994; SC-364, SC-365)

**Checkpoint**: US2 demonstrável pela publicação.

## Phase 5: User Story 3 — O consolidado se diz retificado (P1)

**Independent Test**: publicar um Edital e uma Retificação; ler a marca no segundo documento e nenhuma no primeiro.

- [X] T023 [US3] `render_edital_pdf(..., consolidacao=None)` e a marca abaixo do anúncio, em processo_seletivo/publicacoes/infrastructure/pdf.py (R-010; FR-995)
- [X] T024 [US3] `publish_retification` monta as datas incorporadas (original + Retificações em vigor na vigência desta + esta) e a vigência, em processo_seletivo/publicacoes/application/retificacoes.py (R-010)
- [X] T025 [US3] Testes: marca com uma e com duas Retificações, vigência em outro dia, mesma data sem repetir, original sem marca, fecho com a data da Retificação, em tests/integration/publicacoes/test_consolidado_datado.py (FR-995; SC-367)

## Phase 6: User Story 4 — O publicado sob o catálogo anterior continua retificável (P1)

**Independent Test**: publicar com o catálogo de 12, trocar o catálogo, retificar o texto de uma seção.

- [X] T026 [US4] Testes: Edital publicado com a topologia anterior aceita Retificação de texto e o consolidado mantém as 12 seções; acrescentar, remover, renomear, reordenar ou trocar espécie continua recusado; dar texto a uma textual publicada vazia a faz sair; a elaboração continua conferida contra o catálogo vigente, em tests/integration/publicacoes/test_topologia_do_acervo.py (FR-987, FR-988; SC-366)

## Phase 7: User Story 5 — O candidato lê o que vai aceitar, e quantas vagas há (P2)

**Independent Test**: publicar com Requerimento e três Perfis; ler a Matrícula e a linha de total.

- [X] T027 [US5] `_norma_da_secao` para `matricula` (momento e declaração integral), e a linha `Total` em `_quadro_de_perfis`, em processo_seletivo/publicacoes/infrastructure/pdf.py (R-011, R-012; FR-984, FR-996, FR-997)
- [X] T028 [US5] Testes: declaração idêntica à do portal nos dois momentos, Matrícula composta mesmo vazia, Inscrição composta com teto e vazia, total igual à soma, sem linha com um Perfil, em tests/unit/publicacoes/test_pdf_matricula_e_total.py (FR-984, FR-996, FR-997; SC-368, SC-369)

## Phase 8: Polish & Cross-Cutting

- [X] T029 Emendas nas specs anteriores — notas ao pé da `FR-036` e da `SC-001` em specs/008-composicao-institucional/spec.md e da `FR-037` e da `FR-041` em specs/006-*/spec.md (R-017; FR-998)
- [X] T030 Refazer a fixture de bytes com o contexto do ato versionado: tests/contract/fixtures/autoridade_publicada.json, contexto_publicado.json e documento_publicado_v1.pdf, pelo scripts/gerar_fixture_documento.py; conferir a diferença com `pdftotext` — só o fecho. O `snapshot_publicado.json` fica: é o acervo do catálogo anterior (R-015; FR-999; SC-370)
- [X] T031 Verificação do 28/2026 (quickstart §2): compor, publicar e retificar num banco próprio; comparar seção a seção com o original — [verificacao-28-2026.md](verificacao-28-2026.md)
- [X] T032 A etapa Conteúdo no preview, a 1280×900 e a 375×812 (quickstart §4)
- [X] T033 [P] rastreabilidade.md: cada FR, SC e UX com o lugar do código e o teste que o prende
- [X] T034 Atualizar os números da suíte em AGENTS.md se mudarem; `make lint check test-pg DB_NAME=ps_054`

## Dependencies & Execution Order

- Phase 2 bloqueia tudo; T002–T004 antes de T005.
- US1 (Phase 3) depende só da Phase 2. US2 e US3 dependem de T019 para o compositor; US3 depende de US2 (a data do fecho). US4 depende só da Phase 2. US5 depende de T006.
- T030 depois de todas as mudanças de composição (T012 não mexe no PDF; T019, T023 e T027 mexem).
- T031 depois de T030.

## Parallel Opportunities

- T008 e T009 (arquivos de teste distintos); T016 com qualquer tarefa da US1; T026 com a US2 inteira.

## Implementation Strategy

MVP: Phase 2 + US1 — o catálogo e a topologia, que são o que tem prazo. Depois US2 e US3 (o fecho), US4
(a prova do acervo), US5. Um PR só, porque o catálogo sem a topologia não pode ir sozinho.
