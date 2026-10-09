# Tasks: O que se repete por Perfil sai uma vez no Edital em PDF

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/documento.md](contracts/documento.md),
[quickstart.md](quickstart.md)

**Tests**: pedidos — cada `FR-`, `SC-` e caso-limite da spec tem teste, e o teste vem **antes** do
código: cada fase de testes roda e falha contra a `main` antes da implementação dela (Constituição,
Princípio V).

**Caminhos**: relativos à raiz do repositório; `backend/` é o projeto Django.

**Testes que mudam de propósito**: os que prendem o quadro, a tabela de modalidades e os marcos dentro
de cada Perfil num documento de vários Perfis, e os bytes dos PDFs dos cenários da auditoria. Cada um
é atualizado **na tarefa que muda o comportamento**, com a razão no commit — nunca para "fazer
passar", e nunca afrouxando a asserção (plan, *Testes existentes expostos*).

**Bancos**: `DB_NAME=ps068` para a suíte; `ps_068_*` para a validação, todos novos e com dados
fictícios.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivo diferente, sem dependência pendente)
- **[Story]**: a história da spec (US1 a US4)

---

## Phase 1: Setup

- [ ] T001 Medir o ponto de partida: `uv run pytest` contra PostgreSQL (`TEST_DB_ENGINE=postgresql DB_USER=$(whoami) DB_RUNTIME_USER=$(whoami) DB_NAME=ps068`) sobre `tests/unit/publicacoes tests/unit/editais tests/contract tests/integration/publicacoes tests/interface/test_compor_quadro.py tests/acceptance/test_us1_declaracao_unica_de_vagas.py`; verde, e o total registrado num `specs/068-consolidacao-por-perfil/verificacao.md` novo, seção "Ponto de partida", com a medição da evidência 4 da spec (o roteiro `medir.py`)
- [ ] T002 [P] Gravar no scratchpad (não versionado) o texto de referência de `specs/067-correcoes-de-norma-do-edital/demonstracao/A-publicado-067.pdf` e `B-publicado-067.pdf` (`pdftotext -layout`), e conferir que `test_o_documento_da_auditoria_sai_com_os_bytes_esperados_depois_da_067` passa na `main`

---

## Phase 2: Foundational — o plano de consolidação

Bloqueia todas as histórias. Nada no documento muda nesta fase.

### Testes (primeiro; falham por `AttributeError`)

- [ ] T003 Em `backend/tests/unit/publicacoes/test_consolidacao_por_perfil.py` (novo), o plano (R-001, R-002, [data-model.md](data-model.md)): com um Perfil, "sem consolidação"; grupos de requisitos e de marcos pela identidade do bloco composto — título do Perfil fora da comparação, qualquer outra linha diferente separa (prazo de recurso, corte, critério de desempate, nome do marco, um requisito a mais, outra ordem), grupo de um não existe, bloco vazio não agrupa; grupos na ordem do primeiro Perfil; os grupos de atribuições são os de `grupos_de_atribuicoes`; números das subseções em continuação — atribuições, requisitos, marcos (FR-1359) —, e os dos Perfis e das atribuições não dependem dos outros grupos
- [ ] T004 No mesmo arquivo, a ordem das listas (R-005, FR-1345): linha geral primeiro; reservadas na ordem do primeiro quadro que as declara; as que nenhum quadro declara, na ordem do snapshot; a modalidade de ampla concorrência declarada à frente das reservadas na tabela de modalidades
- [ ] T005 No mesmo arquivo, o auxiliar de linhas por pedaços (R-008): quebra só entre códigos ("ADS - P06" inteiro); aspas em todos quando algum código tem vírgula ou " e " (regra da `064`)

### Implementação

- [ ] T006 Em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`, `plano_de_consolidacao(snapshot)` e o seu tipo (dataclass congelada): identidade por `Composicao` de rascunho (R-002), grupos, numeração (R-001), ordem das listas (R-005); docstrings com o porquê (a `064` como precedente; a remissão sai antes do item)
- [ ] T007 No mesmo arquivo, generalizar `_linhas_sem_partir` para recuo e para frase justificada (R-008), sem mudar a saída dos títulos da `064`
- [ ] T008 Rodar T003–T005 e `tests/unit/publicacoes/test_atribuicoes_consolidadas.py`: verdes

**Checkpoint**: o plano existe; a composição ainda não o lê.

---

## Phase 3: User Story 1 — As vagas numa tabela só (P1) 🎯 MVP

**Goal**: com dois ou mais Perfis, a tabela de vagas em matriz e as tabelas de modalidades agrupadas,
na mesma ordem, no lugar do quadro e da tabela de cada Perfil (`D-002`, ED-11).

**Independent Test**: compor o snapshot congelado de A; a célula INF-IUN × PPI dá 10; uma tabela de
modalidades; mesma ordem de listas nas duas.

### Testes (primeiro)

- [ ] T009 [P] [US1] Em `backend/tests/unit/publicacoes/test_consolidacao_por_perfil.py`, a tabela de vagas ([contrato §2](contracts/documento.md)): legenda, cabeçalho (código; nome sem código; "Ampla concorrência"), uma linha por Perfil com quadro e com vaga imediata, "—" na lista não declarada, nenhum Perfil imprime "Quadro de vagas —" nem "Modalidades de concorrência — <código>" no próprio bloco; Perfil sem quadro e sem vaga imediata sem linha; nenhum Perfil com quadro → nenhuma tabela de vagas; forma longa quando a matriz não cabe (dez listas de códigos longos); cabeçalho repetido na quebra (FR-1342, FR-1343, FR-1357)
- [ ] T010 [P] [US1] No mesmo arquivo, as tabelas de modalidades ([contrato §3](contracts/documento.md)): uma só, sem qualificador, quando todas são iguais; uma por grupo, com "— Perfil X" / "— Perfis X e Y", quando diferem (percentual, fundamento, conjunto); ordem das linhas = ordem das colunas da tabela de vagas (ED-11); coluna vazia omitida como hoje (FR-1344, FR-1345)
- [ ] T011 [P] [US1] No mesmo arquivo, o Edital de um Perfil: os mesmos bytes que a composição de hoje (snapshot sintético e `tests/contract/fixtures/documento_publicado_v1.pdf`), sem tabela de vagas (FR-1356, R-003)

### Implementação

- [ ] T012 [US1] Em `pdf.py`, `_tabela_de_vagas` (matriz e forma longa, R-004) e `_tabelas_de_modalidades` (R-006), compostas em `_perfis` depois de `_quadro_de_perfis`; `_tabela` aceita legenda em linhas; com dois ou mais Perfis, o bloco do Perfil deixa de chamar `_quadro_de_vagas_do_perfil` e `_modalidades`; com um, nada muda
- [ ] T013 [US1] Em `pdf.py`, `tabelas_do_documento` lê o plano (R-009); acrescentar a `CASOS` de `backend/tests/unit/publicacoes/test_itens_do_documento.py` os casos "modalidades em dois grupos", "nenhum Perfil com quadro" e "Perfil sem vaga imediata entre Perfis com vaga", e rodar o guardião
- [ ] T014 [US1] Atualizar de propósito os testes que afirmavam o quadro e as modalidades dentro de cada Perfil num documento de vários Perfis (`test_perfil_sem_vaga_imediata.py`, `test_pdf_classificacao.py`, `test_atribuicoes_consolidadas.py` e os que a suíte apontar), pela regra do plano; cada um registrado em `verificacao.md`
- [ ] T015 [US1] Rodar T009–T011, o guardião e `tests/unit/publicacoes`: verdes

**Checkpoint**: US1 entregue; o documento de A já tem a tabela de vagas.

---

## Phase 4: User Story 2 — A regra de classificação uma vez, para cada Perfil (P1)

**Goal**: marcos idênticos numa subseção comum depois do último Perfil, com a frase que os aplica a
cada Perfil separadamente; o método comum uma vez (`D-001`, FR-1346 a FR-1349).

**Independent Test**: compor A e B; uma subseção de marcos; cada Perfil remete a ela; a frase do
FR-1347 antes dos marcos; as linhas do método comum uma vez.

### Testes (primeiro)

- [ ] T016 [P] [US2] Em `test_consolidacao_por_perfil.py`, a subseção comum de marcos ([contrato §5–§6](contracts/documento.md)): título com os códigos (regra da `064`), a frase do FR-1347 logo abaixo, os marcos com o mesmo texto, linha a linha, que o Perfil imprimiria (FR-1348); a remissão "Marcos classificatórios: os descritos no item N.k." em cada Perfil do grupo e em nenhum outro (FR-1354); dois grupos → duas subseções, na ordem; marcos diferentes → nenhum grupo; Perfil sem marco fora; um bloco coeso por marco (FR-1357)
- [ ] T017 [P] [US2] No mesmo arquivo, o método comum (R-011, FR-1349): todos os marcos iguais → as sete linhas uma vez, na subseção comum, sem remissão; dois grupos de marcos governados pelo método comum → linhas no primeiro, "Método: o comum a este Edital, descrito no item N.k." e a habilitação no segundo; método próprio continua no marco; método próprio idêntico em vários Perfis → "próprio deste marco" e agrupam
- [ ] T018 [P] [US2] Em `backend/tests/unit/editais/test_remissoes.py`, a conferência de remissões sobre um Edital com subseções comuns de requisitos e de marcos: "item N.k" de uma subseção comum é destino único, com a descrição "a subseção «Marcos classificatórios comuns aos Perfis …»"; nenhum `KeyError` (R-009)

### Implementação

- [ ] T019 [US2] Em `pdf.py`, `_marcos` ganha o deslocamento de recuo, a opção de omitir o rótulo e a remissão do método comum (R-010, R-011); `_marcos_comuns(composicao, …)` com título, frase do FR-1347 e marcos; a remissão no Perfil agrupado via `_pares` com o espaço de sub-bloco
- [ ] T020 [US2] Em `pdf.py`, `itens_do_documento` lê o plano, com as naturezas `requisitos_comuns` e `marcos_comuns` (R-009); em `backend/processo_seletivo/editais/domain/validation.py`, `_DESCRICAO_DO_ITEM` ganha as duas; acrescentar a `CASOS` do guardião "marcos comuns em dois grupos" e "método comum em dois grupos"
- [ ] T021 [US2] Atualizar de propósito os testes que afirmavam os marcos dentro de cada Perfil num documento de vários Perfis com marcos iguais (`test_pdf_classificacao.py`, `test_perfil_sem_vaga_imediata.py`, `test_documento_publicado.py` e os que a suíte apontar), registrados em `verificacao.md`
- [ ] T022 [US2] Rodar T016–T018, o guardião, `tests/unit/publicacoes` e `tests/unit/editais`: verdes

**Checkpoint**: US1 e US2 entregues — o grosso das páginas.

---

## Phase 5: User Story 3 — Frases e requisitos uma vez (P2)

**Goal**: reversão abaixo da tabela de vagas e convocação depois das modalidades, com os códigos
quando não valem para todos; requisitos idênticos numa subseção comum (FR-1350 a FR-1352, `D-003`).

**Independent Test**: compor A — cada frase uma vez, sem prefixo; compor um Edital em que só dois de
três Perfis têm reversão — a frase nomeia os dois.

### Testes (primeiro)

- [ ] T023 [P] [US3] Em `test_consolidacao_por_perfil.py`, as frases ([contrato §4](contracts/documento.md)): reversão sem prefixo quando todos os Perfis da tabela de vagas têm a mesma espécie; uma por espécie, com "No Perfil X, " / "Nos Perfis X e Y, " e minúscula, quando não; Perfil fora da tabela de vagas nunca alcançado; convocação pela mesma regra sobre o Edital inteiro; Perfil sem forma declarada nunca alcançado; nenhuma frase dentro do bloco do Perfil; código "ADS - P06" não partido
- [ ] T024 [P] [US3] No mesmo arquivo, os requisitos comuns: subseção "Requisitos comuns aos Perfis …" com os itens e o marcador de hoje, remissão "Requisitos: os descritos no item N.k." no Perfil do grupo; lista vazia não agrupa; requisitos que diferem num item não agrupam; a subseção vem depois das de atribuições e antes das de marcos

### Implementação

- [ ] T025 [US3] Em `pdf.py`, as frases consolidadas (R-007, R-008) no lugar de `_reversao_declarada` e `_forma_de_convocacao_declarada` no Perfil, com o texto das frases vindo das mesmas fontes de hoje (o vocabulário do publicado para a convocação)
- [ ] T026 [US3] Em `pdf.py`, `_requisitos_comuns` e a remissão no Perfil; `itens_do_documento` com os grupos de requisitos; caso "requisitos comuns" no guardião
- [ ] T027 [US3] Rodar T023–T024, o guardião e `tests/unit/publicacoes`: verdes

**Checkpoint**: a seção de Perfis consolidada inteira.

---

## Phase 6: User Story 4 — Publicado não muda; Retificação pela mesma regra (P2)

### Testes (primeiro)

- [ ] T028 [P] [US4] Em `backend/tests/integration/publicacoes/test_retificacoes.py`, quatro Perfis de marcos iguais, publicados; Retificação que muda o prazo de recurso do marco de um deles: o documento guardado da Publicação mantém os bytes; o consolidado da Retificação agrupa os três e o quarto imprime os próprios marcos (FR-1358)
- [ ] T029 [P] [US4] Em `backend/tests/contract/test_documento_publicado.py`, prévia × publicado de um Edital consolidado: mesmas quebras de página, marca de prévia sem alterar as quebras (FR-1356)

### Implementação

- [ ] T030 [US4] Nenhum código novo esperado — a Retificação compõe pelo mesmo `render_edital_pdf`; se T028 ou T029 falharem, corrigir na composição e registrar a causa em `verificacao.md`

---

## Phase 7: Prova, evidências e polimento

- [ ] T031 Em `backend/tests/unit/publicacoes/test_equivalencia_da_consolidacao.py` (novo), a prova de equivalência (R-012, FR-1353, SC-513): para cada Perfil, o multiconjunto de linhas normativas aplicáveis no documento de depois = o do bloco dele no de antes; sobre `Composicao.itens` nos casos sintéticos de T003–T024 e sobre o texto dos PDFs nos cenários A e B (antes = `specs/067-…/demonstracao/`)
- [ ] T032 Gerar `specs/068-consolidacao-por-perfil/demonstracao/A-publicado-068.pdf` e `B-publicado-068.pdf` a partir dos snapshots congelados (o mesmo contexto do ato de `cenarios_da_auditoria.py`); apontar `ESPERADOS` de `test_itens_do_documento.py` para eles; `backend/tests/unit/publicacoes/test_documento_da_auditoria_depois_da_068.py` (novo, molde do da `067`) prende a diferença de texto do documento inteiro; o da `067` passa a comparar a auditoria com a `067` pelos PDFs dela, e não com o compositor de agora
- [ ] T033 Contar as ocorrências (SC-512) nos PDFs de T032: uma do texto dos marcos, uma tabela de modalidades, uma de cada frase, uma das linhas do método; num teste do arquivo de T032
- [ ] T034 Cenários A e B **pelo fluxo real**, antes (`git archive 2b698592`) e depois, em `ps_068_*` novos ([quickstart §2](quickstart.md)): páginas totais e da seção de Perfis (SC-510, SC-511), branco no pé das páginas da seção (SC-514), diff de texto; registrar em `verificacao.md`
- [ ] T035 Renderizar por CoreGraphics as páginas da seção de Perfis de A e de B, antes e depois; olhar cada uma — hierarquia, recuos, tabelas, brancos —; gravar as escolhidas em `demonstracao/` e registrar o que se viu em `verificacao.md`
- [ ] T036 [P] Notas de emenda nos FRs alcançados: `specs/008-composicao-institucional/spec.md` (FR-016, FR-018, FR-021), `specs/025-quadro-de-vagas-por-modalidade/spec.md` (FR-169) e `specs/064-atribuicoes-consolidadas/spec.md` (FR-1197)
- [ ] T037 [P] `specs/068-consolidacao-por-perfil/rastreabilidade.md`: uma linha por FR, SC e caso-limite, com o teste que o cobre (molde da `065`)
- [ ] T038 [P] Linha da `068` na tabela de incrementos do `README.md`; nota "tratados depois desta auditoria" na §12.2 de `doc/auditoria-edital-pdf-2026-10-08.md` (ED-04 e ED-11), sem regravar os PDFs da auditoria
- [ ] T039 `cd backend && make lint check` e `make DB_NAME=ps068 test-pg`; números (passando, pulados, tempo) em `verificacao.md`, e em `AGENTS.md` se mudarem os pulados
- [ ] T040 Registrar em `verificacao.md` os achados do caminho que não viraram escopo (spec, *O que esta feature não cobre*)

---

## Dependencies & Execution Order

- Phase 1 → Phase 2 → US1 → US2 → US3 → US4 → Phase 7.
- US2 e US3 dependem do plano (Phase 2) e da reorganização de `_perfis` de US1 (o bloco do Perfil já
  sem quadro e modalidades); entre si, US3 depende de US2 só na numeração das subseções (requisitos
  antes de marcos), que o plano já calcula — podem ser feitas em qualquer ordem depois de US1.
- US4 não tem código próprio; depende de US1–US3 para ter o que provar.
- T031–T035 dependem de todas as histórias.

## Parallel Opportunities

- T009, T010, T011 (arquivos/seções de teste independentes); T016, T017, T018; T023, T024; T028, T029;
  T036, T037, T038.

## Implementation Strategy

MVP = Phase 2 + US1 (a tabela única, que sozinha responde a pergunta mais comum e resolve o ED-11).
US2 entrega a maior parte das páginas. US3 e US4 completam. A Phase 7 é a prova pedida — equivalência,
fluxo real, páginas olhadas e suíte — e não é opcional.
