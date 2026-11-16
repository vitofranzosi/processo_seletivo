# Tasks: Os documentos que o GPS compõe nascem em PDF/A

**Input**: `spec.md`, `plan.md`, `research.md`
**Tests**: pedidos — a spec exige prova byte a byte por página, de texto e de conformidade.

## Format: `[ID] [P?] [Story] Description`

Caminhos relativos a `backend/`, salvo indicação.

## Phase 1: Setup

- [x] T001 Baixar o `sRGB2014.icc` do registro do ICC, conferir o cabeçalho e a licença, e versioná-lo em `processo_seletivo/publicacoes/infrastructure/cor/` com `LICENSE` e `ORIGEM.md` (FR-8156)
- [x] T002 Fixar a imagem `verapdf/cli:v1.30.4` pelo resumo e confirmar a versão

## Phase 2: Foundational

- [x] T003 Escrever `processo_seletivo/publicacoes/infrastructure/pdfa.py`: `xmp`, `objetos`, `identificador`, `ANOTACAO_IMPRIMIVEL`, `perfil` e `conferir` (FR-8152 a FR-8157)
- [x] T004 `_montar_o_arquivo(identificado=)` em `pdf.py`: o `/ID` derivado do corpo, e o trailer de antes sem ele (FR-8154)

## Phase 3: User Story 1 — Edital e Retificação (P1) 🎯 MVP

- [x] T005 [US1] `_arquivo_do_edital(pdfa=)`: perfil e metadados depois dos objetos de sempre, título e autor do `/Info` nos metadados, `/F 4` nas anotações (FR-8150, FR-8153, FR-8157)
- [x] T006 [US1] `render_edital_pdf` passa `pdfa=not previa` (FR-8162, D-003)
- [x] T007 [US1] Regravar a demonstração do cenário da auditoria em `specs/178-documentos-em-pdfa/demonstracao/` e apontar `test_itens_do_documento.py` e `test_documento_da_auditoria_depois_da_069.py` para ela
- [x] T008 [US1] Gravar `tests/contract/fixtures/documento_publicado_v2.pdf`, manter a `v1` como evidência e apontar `test_documento_publicado.py` para a `v2`
- [x] T009 [US1] Atualizar `test_arquivo_do_edital.py`: sem marcação, e com o `/ID` do conteúdo

## Phase 4: User Story 2 — Relatórios (P1)

- [x] T010 [US2] `diagramacao._arquivo`: nível A, metadados com título e autor, `/F 4`, `/ID` (FR-8151)

## Phase 5: User Story 3 — A família da divulgação (P2)

- [x] T011 [US3] `render_documento` em PDF/A: Edital Sans embutida, métrica conferida, perfil e metadados (FR-8150, FR-8158)
- [x] T012 [US3] Congelar o escritor antigo em `_documento_com_a_helvetica` e expô-lo por `render_documento(pdfa=False)` (D-002)
- [x] T013 [P] [US3] `Composicao(metrica=METRICA_DO_EDITAL)` em `divulgacao/infrastructure/documento.py`, `documento_das_inscricoes.py`, `convocacao/infrastructure/documento.py` e `agendamento/infrastructure/documento.py`
- [x] T014 [US3] Emendar a FR-1383 e o SC-522 em `specs/069-edital-linguagem-simples/spec.md`, com a redação anterior preservada (FR-8166)
- [x] T015 [US3] Reescrever `tests/contract/test_comprovante_e_divulgacao_byte_a_byte.py`: `comprovante_v1` pelo escritor antigo, `comprovante_v2` e `divulgacao_v2` pelo novo, o texto igual palavra a palavra
- [x] T016 [US3] Ajustar `tests/unit/publicacoes/test_pdf_grafia.py` à métrica da fonte embutida

## Phase 6: User Story 4 — O comprovante (P2)

- [x] T017 [US4] `Inscricao.comprovante_em_pdfa` e a migration `inscricoes/0008`, falsa nas linhas existentes e verdadeira por padrão (FR-8163, D-005)
- [x] T018 [US4] O envio grava `comprovante_em_pdfa=True` em `inscricoes/application/submissao.py`
- [x] T019 [US4] `render_comprovante_pdf(pdfa=)` e a view do portal passando o registro da inscrição na página e no download (FR-8164, FR-8165)
- [x] T020 [US4] `tests/integration/portal/test_comprovante_em_pdfa.py`: o envio novo, o rascunho de antes, a enviada de antes pela migration desfeita e refeita, e o gatilho que não dispara
- [x] T021 [US4] Contagem de migrations da `inscricoes` em `tests/migrations/test_migrations.py`

## Phase 7: User Story 5 — A verificação (P3)

- [x] T022 [US5] `tests/pdfa/exemplares.py` (um de cada um dos nove tipos, sem banco) e `tests/pdfa/leitura.py`
- [x] T023 [US5] `tests/unit/publicacoes/test_conformidade_pdfa.py`: os acréscimos em cada exemplar, sem o validador (FR-8171)
- [x] T024 [US5] `tests/unit/publicacoes/test_documento_da_auditoria_depois_da_178.py` e os exemplares de antes (composição da `main` em `619a4ae0`) e de depois em `demonstracao/` (SC-2822, SC-2824, SC-2827)
- [x] T025 [US5] `tests/pdfa/test_exemplares.py` sob `PDFA_EXEMPLARES` e `scripts/conferir_o_verapdf.py`; sabotagem local reprovada
- [x] T026 [US5] Job `pdfa` em `.github/workflows/backend.yml`, exigido pelo veredito `test` (FR-8168, FR-8169)

## Phase 8: Polish

- [x] T027 Linha da `178` no `README.md`; nota do job no `CLAUDE.md`
- [x] T028 `rastreabilidade.md`
- [x] T029 `make lint check test-pg` com `DB_NAME=ps_178`
- [x] T030 O job `pdfa` verde no CI do PR

## Dependencies

- T003–T004 antes de tudo; US1 e US2 independentes entre si; US3 antes de US4 (o comprovante usa o
  `render_documento` novo); US5 depois das quatro.
