# Tasks: A inaplicabilidade documental tem fundamento publicado

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/)

**Antes de começar:**

- a P-1 e a P-2 da spec respondidas;
- as D-001 a D-016 aceitas, ou revistas;
- o PR #425 mergeado. Esta spec acrescenta guardas depois da dele, nos mesmos arquivos.

A ordem é A → B → C. `[P]` marca tarefa sem dependência de arquivo com a anterior. Os testes vêm
antes do código que os torna verdes, dentro de cada fase.

## Fase 0 — Preparação

- [ ] T001 Conferir na `main` o teto de `FR-`/`SC-`/`UX-` e a migration mais recente da `editais`,
  e revisar a faixa e os números deste plano se mudaram
- [ ] T002 Fixtures: `ALISTAMENTO` (obrigatório na convocação, `requiredWhen`) e `LAUDO` (obrigatório
  na convocação, recorte por modalidade PcD) em `tests/fixtures/documentos_da_convocacao.py`, pelo
  `_documento(**extra)` que já existe (R-012)

## Fase 1 — Incremento A: a condição na composição (US1, FR-4451 a FR-4456, FR-4477)

- [ ] T003 [P] Testes de domínio de `problemas_da_condicao`: facultativo, inscrição, vazia, aparada,
  mais de 300 caracteres (`tests/unit/editais/`)
- [ ] T004 [P] Testes de integração `cp`: rascunho → publicação com condição; publicação impedida no
  facultativo e na inscrição; reaproveitamento (`023`) leva a condição; retificação da condição
  alcança só a chamada seguinte
- [ ] T005 Coluna `DocumentoExigido.condicao` e migration `0025`; o guardião da contagem de
  migrations por app
- [ ] T006 `requiredWhen` no serializer aninhado, em `draft.py`, em `publish_edital.py`, em
  `DOCUMENTO_EXIGIDO_PUBLICADO` e no `openapi.yaml` da `001` (R-004, linhas 2 a 6)
- [ ] T007 `CONTRATO` da mutabilidade (retificável), `rascunho_completo`, `CAMPOS_DOCUMENTO` da
  Retificação, rótulo em `alteracoes.py`, `LIDOS` da revisão (R-004, linhas 7 a 11); linha nova na
  matriz da `026` com a marca *"revista pela `131`"*
- [ ] T008 `SCHEMA_VERSION` 19, degrau 19 em `DEGRAUS_DE_DOCUMENTO`, censo da elevação com o
  parágrafo *"E muda com a `131`"*, cobertura das dúvidas na versão 19 com a linha nova (R-003)
- [ ] T009 `problemas_da_condicao` em `editais/domain/documentos.py`, chamado no rascunho e na
  publicação, código `document_requirement_condition_incoherent` (FR-4453)
- [ ] T010 Composição: campo *"Exigido somente quando"* em `_documento.html`, com a ajuda do UX-302;
  `ler_inscricao`, `documentos_do_edital`, `documentos_persistidos` (R-004, linhas 13 e 14)
- [ ] T011 PDF: `texto_do_documento` e a redação 1 acrescentam *", ‹condição›"* depois do nome; o
  snapshot publicado ganha `requiredWhen: null`, e os bytes não mudam (FR-4454)
- [ ] T012 `condicao_de(requisito)` em `editais/domain/documentos.py`: `requiredWhen` aparado, ou
  `None`; a versão sem a chave é incondicional (FR-4477)
- [ ] T013 **Rodar a suíte inteira** antes da fase 2: os guardiões de lista de campos são o risco
  deste incremento

## Fase 2 — Incremento B: a conferência (US2, US4; FR-4457 a FR-4465)

- [ ] T014 [P] Testes de domínio (`dd`): `motivo_tem_conteudo`; a tabela de resultados admitidos por
  figura (data-model §3)
- [ ] T015 [P] Testes de integração (`ic`): cenários 1, 5, 6, 7, 8, 10 e 11 de
  [cenarios.md](contracts/cenarios.md); substituição envolvendo *"não se aplica"* sem arquivo; nova
  versão recusada depois do *"não se aplica"*
- [ ] T016 `conferir`: recusa de inexistente para o item fora do recorte, antes da autorização
  (FR-4464, R-007); a abertura de apresentação, a mesma regra
- [ ] T017 `conferir`: `nao_se_aplica_sem_condicao` (FR-4457), `nao_se_aplica_sem_abertura`
  (FR-4460), `motivo_sem_conteudo` (FR-4458), motivo de substituição com *"não se aplica"*
  (FR-4462), na ordem do data-model §3
- [ ] T018 Página dos documentos: a linha *"Condição publicada"*; *"Não se aplica"* só no
  condicional; o texto do campo do motivo; o selo próprio (UX-301, UX-302; FR-4454, FR-4459)
- [ ] T019 Revisões escritas na `115`, com a marca *"revista pela `131`"* e a redação anterior
  preservada: FR-3585, FR-3586 e o caso-limite *"Obrigatório marcado 'não se aplica'"*

## Fase 3 — Incremento C: aceite, formalização, portal e transição (US3, US4, US5; FR-4466 a FR-4478)

- [ ] T020 [P] Testes de domínio (`dd`): `impede_incluir` com condicional e incondicional;
  `assinatura_das_inaplicabilidades` estável na ordem e sensível ao conjunto
- [ ] T021 [P] Testes de integração (`ic`):
  - cenários 2, 9 e 12;
  - a P-1 com uma convocação aberta e uma decidida, ambas com *"não se aplica"* em item
    incondicional gravado direto no banco;
  - regularização com e sem ciência
- [ ] T022 [P] Testes de interface (`ia`):
  - condução com contagens separadas e selo próprio;
  - bloco da confirmação com condição, motivo, autor e instante;
  - caixa de ciência e assinatura no HTML;
  - recusa e volta com a lista nova
- [ ] T023 `LeituraDocumental`: `contagens["nao_se_aplica"]`, `conformes` só conforme,
  `ItemLido.condicao`, `inaplicabilidades`, sem consulta nova (contrato `conferencia.md` §3; SC-1377)
- [ ] T024 `impede_incluir` com a condicionalidade (FR-4470, P-1 escolhida)
- [ ] T025 `desfechar`: a ciência sob a trava, depois da guarda da lista e da das pendências; as duas
  recusas; a trilha citando os `id` (FR-4468, FR-4469; R-005)
- [ ] T026 Condução e formulário de desfecho: contagens, bloco, caixa e assinatura (UX-301, UX-303;
  FR-4466, FR-4467)
- [ ] T027 Formalização: `NAO_SE_APLICA_APOS_ANALISE` e `_da_convocacao`; teste `fc` do cenário 13
  (FR-4473, R-010)
- [ ] T028 Portal: a condição no cartão e o texto do condicional *a apresentar* em
  `obrigacoes.texto_do_item` (FR-4475, UX-304); teste em `unit/portal/test_obrigacoes_da_convocacao.py`
- [ ] T029 A marca *"registrado sem condição publicada"* nas leituras da gestão (FR-4478)
- [ ] T030 Revisões escritas: FR-3592 e FR-3607 da `115`; FR-3672 da `117`; a linha nova da FR-3746
  da `118`, com a marca *"revista pela `131`"*
- [ ] T031 Orçamento de consultas da condução e da página com documento condicional (SC-1377)

## Fase 4 — Verificação

- [ ] T032 `cd backend && make lint check test-pg`, com `DB_NAME` próprio
- [ ] T033 Roteiro do [quickstart](quickstart.md) num banco de demonstração novo. A SC-1378 é humana:
  registrar quem leu e o que disse em `verificacao.md`
- [ ] T034 `verificacao.md` com a suíte, os números e as capturas sem dado real
