# Tasks: O Edital oficial em linguagem simples — redação, organização, tipografia e navegação (lote 1)

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/documento.md](contracts/documento.md),
[contracts/redacao.md](contracts/redacao.md), [quickstart.md](quickstart.md)

**Tests**: pedidos. Cada `FR-`, `SC-` e caso-limite da spec tem teste, e o teste vem **antes** do
código: cada fase de testes roda e falha contra a `main` antes da implementação dela (Constituição,
Princípio V).

**Caminhos**: relativos à raiz do repositório; `backend/` é o projeto Django.

**Testes que mudam de propósito**: os que afirmam a frase, o título, a numeração ou os bytes de hoje.
Cada um é atualizado **na tarefa que muda o comportamento**, com a razão no commit, pela regra do plano:

- afirma a forma nova com a mesma força, ou fixa a redação 1 quando prova a história;
- nunca é afrouxado;
- fica registrado em `verificacao.md`.

**Bancos**: `DB_NAME=ps069` para a suíte; `ps_069_*` para a validação, todos novos e com dados
fictícios.

**Aprovação do usuário**: T030 baixa o arquivo da fonte do release oficial. A tarefa pede aprovação
antes, dizendo o nome do arquivo, a origem e o tamanho.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivo diferente, sem dependência pendente)
- **[Story]**: a história da spec (US1 a US6)

---

## Phase 1: Setup

- [X] T001 Medir o ponto de partida: `uv run pytest` contra PostgreSQL (`TEST_DB_ENGINE=postgresql DB_USER=$(whoami) DB_RUNTIME_USER=$(whoami) DB_NAME=ps069`) sobre `tests/unit/publicacoes tests/unit/editais tests/unit/interface tests/contract tests/integration/publicacoes tests/interface tests/integration/portal tests/unit/divulgacao`; verde, e o total registrado num `specs/069-edital-linguagem-simples/verificacao.md` novo, seção "Ponto de partida"
- [X] T002 [P] Gravar no scratchpad (não versionado) o texto de referência (`pdftotext -layout`) de `specs/068-consolidacao-por-perfil/demonstracao/A-publicado-068.pdf` e `B-publicado-068.pdf`, e a lista de enunciados de `doc/analise-edital-linguagem-simples-2026-10-12/equivalencia.md`, para a conferência final

---

## Phase 2: Foundational — guardas e parâmetros, sem mudar documento algum

Bloqueia todas as histórias. Ao fim desta fase, **todo documento continua com os mesmos bytes**.

### Testes (primeiro)

- [X] T003 [P] Em `backend/tests/contract/test_comprovante_e_divulgacao_byte_a_byte.py` (novo), com fixtures novas em `backend/tests/contract/fixtures/` (`comprovante_v1.pdf`, `divulgacao_v1.pdf` e os conteúdos JSON que os produzem), compostos **pela `main`**: compor o mesmo comprovante (`inscricoes/infrastructure/comprovante_pdf.py`) e o mesmo documento de divulgação (`divulgacao/infrastructure/documento.py`) dá exatamente esses bytes (FR-1383, SC-522, R-005). A docstring diz que a fixture **não** se regenera nesta feature
- [X] T004 [P] Em `backend/tests/unit/publicacoes/test_extrator_de_texto.py` (novo), o guarda dos extratores: `texto_de` de `tests/unit/publicacoes/test_pdf.py`, o de `tests/contract/test_documento_publicado.py` e `texto_de_pdf_bytes` de `tests/interface/test_fluxo.py` devolvem texto não vazio, com uma frase conhecida, para um Edital composto, para a prévia, para o comprovante e para a divulgação (R-006). Um extrator que passe a devolver vazio derruba o teste, em vez de deixar passar os "não contém"
- [X] T005 [P] Em `backend/tests/unit/publicacoes/test_metrica_do_documento.py` (novo): `Composicao()` sem métrica mede como hoje (`largura` da Helvetica, M = 833, i = 222, espaço = 278); `Composicao(metrica=…)` usa a métrica dada em `escrever`, `_quebrar`, `_espacamento` e `_x`; os bytes de `render_edital_pdf` para os snapshots da auditoria e para a fixture de contrato não mudam com o parâmetro padrão

### Implementação

- [X] T006 Em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`, a métrica como parâmetro de `Composicao` (padrão: a Helvetica de hoje), passada a `_quebrar`, `_espacamento`, `_x`, `_x_na_celula` e `_larguras_das_colunas` pela composição. `render_documento`, `largura` e as tabelas `_ASCII_*` ficam como estão (R-005)
- [X] T007 Rodar T003–T005, `tests/contract`, `tests/unit/publicacoes` e `tests/unit/divulgacao`: verdes, e as fixtures de T003 iguais às da `main`

**Checkpoint**: comprovante e divulgação presos por bytes; extratores guardados; a métrica é parâmetro.

---

## Phase 3: User Story 1 — O candidato lê a regra em palavras dele, e a regra é a mesma (P1) 🎯 MVP

**Goal**: a redação 2 das frases geradas, variante por variante ([contrato](contracts/redacao.md)), no
documento, na prévia, na Revisão, no portal e na proposta de ordenação. A redação 1 continua existindo.

**Independent Test**: compor A e B. Nenhum termo da FR-1366; cada variante com a frase do contrato; a
Revisão mostra a mesma frase.

### Testes (primeiro)

- [X] T008 [P] [US1] Em `backend/tests/unit/publicacoes/test_redacao_das_frases.py` (novo), um caso por linha das seções 1 a 4 de [contracts/redacao.md](contracts/redacao.md) (C1–C15, K1–K10, T1–T8, R1–R6). Para cada um, a frase da redação 2 exata, a da redação 1 inalterada e a nota de equivalência como docstring do caso. Inclui:
  - K9: nenhuma condição acrescentada (o texto não contém "se", "sobrarem" nem "vagas");
  - K7 e K8: a frase dos suplentes só sai sem cadastro de reserva em nenhum Perfil (FR-1362);
  - R1: aspas sem artigo (decisão 001 da `067`) e sem canal (FR-1363);
  - T1 e T2: forma genérica sempre ("«f» mais antiga/recente, informada na inscrição"); um fato DATA com rótulo "Data de nascimento" **não** produz "idade" — nenhuma dedução pelo rótulo (D-006).
- [X] T009 [P] [US1] No mesmo arquivo, as seções 5 a 7 do contrato (S1–S7, V1–V13, E1–E3, D1–D5, P1–P2, F1–F2), com os mesmos três itens por caso; a hora com dois dígitos
- [X] T010 [P] [US1] Em `backend/tests/unit/publicacoes/test_redacao_no_documento.py` (novo) (FR-1360, FR-1366, SC-518, FR-1395):
  - compor os snapshots congelados de A e B e um sintético com todas as variantes;
  - zero ocorrências de cada termo da FR-1366 **na redação gerada**, nas duas apresentações — a plana inclusive, onde G1–G3 de [contracts/redacao.md](contracts/redacao.md) trocam "Marcos classificatórios" por "Regras de classificação";
  - um texto livre com "marcos classificatórios" sai literal, e não conta como ocorrência (o teste separa o gerado do redigido pelo item da composição);
  - cada frase do contrato presente onde a variante existe.
- [X] T011 [P] [US1] Em `backend/tests/unit/interface/test_revisao.py` e `backend/tests/interface/test_correcoes_de_norma_na_revisao.py`: a Revisão de um rascunho mostra as frases da redação 2 iguais às do documento composto do mesmo snapshot (FR-1364). Atualizar de propósito as asserções de frase de hoje (linhas 180, 323-424 do primeiro)
- [X] T012 [P] [US1] Em `backend/tests/portal/test_acompanhamento_pela_situacao.py`, `backend/tests/unit/portal/test_situacao_da_inscricao.py` e `backend/tests/integration/portal/test_teto_no_portal.py`: o canal de convocação (V4, V5) e o teto (V7, V8) na redação 2, para Edital publicado antes e depois (FR-1397 permite)

### Implementação

- [X] T013 [US1] Em `backend/processo_seletivo/publicacoes/domain/vocabulario_da_regra.py`, a redação versionada: as tabelas da redação 1 congeladas com esse nome; as da redação 2; `criterio_por_extenso`, `criterio_com_a_ausencia` e `forma_de_convocacao_por_extenso` com o parâmetro `redacao` (padrão: a vigente, 2) e o tipo do fato para T1/T2 (R-004). Docstring com o porquê (o ato publicado lê a sua)
- [X] T014 [US1] Em `pdf.py`, as frases do marco, do sorteio, das Etapas, dos documentos, da reversão, da convocação, do teto, do Requerimento e da integridade na redação 2, pelas funções com o parâmetro `redacao`. As da redação 1 continuam alcançáveis para as provas históricas. Rótulos "Ordem:", "Combinação:", "Normalização:", "Habilitação:", "Corte:", "Continuação:" fora do documento; os pares viram frases (contrato §1-§7). Os rótulos gerados G1–G3 (contrato §8) dizem "Regras de classificação" na redação 2, nas duas apresentações, sem mudar o número nem o destino da remissão (D-007)
- [X] T015 [US1] Em `backend/processo_seletivo/interface/revisao.py`, `interface/aplicacao.py`, `portal/situacao.py` e `portal/views.py`, ler as frases da redação 2 pelas mesmas funções. Rótulos de campo da equipe ficam (R-004)
- [X] T016 [US1] Rótulos de `callForm` na redação 2: `backend/processo_seletivo/editais/models/perfis.py:88-89` com migration `AlterField` em `backend/processo_seletivo/editais/migrations/`; `interface/retificacao.py:353-356`; `interface/templates/interface/compor_perfis.html:135-136`, `_perfil.html:265-266`, `convocacao.html:138`. Justificativa da migration no guardião da `022` (R-015)
- [X] T017 [US1] Atualizar de propósito os testes de PDF que afirmam frases de hoje (`test_pdf.py`, `test_pdf_classificacao.py`, `test_frase_de_recurso.py`, `test_documento_sob_sorteio.py`, `test_perfil_sem_vaga_imediata.py`, `test_pdf_documentos_exigidos.py`, `test_fecho_e_normas_da_054.py`, `tests/contract/test_documento_publicado.py` nas asserções de texto, `tests/integration/publicacoes/*`). Os testes de história da `067` e da `068` (`test_documento_da_auditoria_depois_da_067.py`, `_068.py`, `test_equivalencia_da_consolidacao.py`) passam a usar a redação 1 explicitamente. Cada caso em `verificacao.md`
- [X] T018 [US1] Rodar T008–T012 e `tests/unit/publicacoes`, `tests/unit/interface`, `tests/portal`, `tests/integration/portal`: verdes

**Checkpoint**: a redação 2 em todo lugar onde a regra se diz; a redação 1 preservada no código.

---

## Phase 4: User Story 6 — O que foi publicado não muda, e o resto do sistema também não (P1)

**Goal**:

- a `Publicacao` registra a redação;
- a página do ato de ordenação já publicado mostra a redação dele;
- documentos publicados, comprovante e divulgação ficam intocados;
- o hash do conteúdo já submetido não muda.

**Independent Test**: [quickstart §2, §6 e §7](quickstart.md).

### Testes (primeiro)

- [X] T019 [P] [US6] Em `backend/tests/integration/publicacoes/test_redacao_da_publicacao.py` (novo): a Publicação de Edital e a de Retificação gravam `redacao_do_documento = 2`; uma Publicação criada com o modelo anterior à migration (padrão do banco) lê `1`; a coluna não muda depois (append-only: `save` recusa; gatilho, contra PostgreSQL)
- [X] T020 [P] [US6] Em `backend/tests/integration/classificacao/test_redacao_do_ato_publicado.py` (novo): um ato de ordenação cuja versão vem de Publicação com redação 1 mostra, na página (`interface/templates/interface/ato_ordenacao.html`, view de `interface/views.py:7914`), "menor valor declarado em Data de nascimento; sem o valor, fica por último neste critério"; um ato sobre versão de redação 2 mostra "data de nascimento mais antiga, informada na inscrição…"; a proposta de ordenação (`ordenacao.html`) mostra a redação 2 (FR-1397, R-004)
- [X] T021 [P] [US6] Em `backend/tests/integration/publicacoes/test_acervo_da_069.py` (novo):
  - um Edital publicado com o catálogo e o compositor anteriores (o molde de `test_topologia_do_acervo.py`) é servido com os mesmos bytes;
  - o hash do conteúdo homologado antes não muda;
  - um Edital homologado antes da troca é recusado na publicação com `homologated_revision_changed` e volta à elaboração (premissa da spec, FR-1393, FR-1394, SC-523).

### Implementação

- [X] T022 [US6] `backend/processo_seletivo/publicacoes/models.py`: `Publicacao.redacao_do_documento` (`PositiveSmallIntegerField`, padrão 1), com comentário no molde das colunas da `060`; migration `backend/processo_seletivo/publicacoes/migrations/0011_redacao_do_documento.py`; justificativa no guardião da `022`; a tabela segue em `TABELAS_APPEND_ONLY` sem mudança de privilégio (R-015)
- [X] T023 [US6] `backend/processo_seletivo/publicacoes/application/publish_edital.py` e `retificacoes.py` gravam a redação vigente na Publicação
- [X] T024 [US6] `backend/processo_seletivo/classificacao/application/selectors.py` (`nomear_criterios`, :266-289): lê a redação de `ato.versao.source_publication.redacao_do_documento` e a passa a `criterio_por_extenso`; `criterios_do_desempate` (:391-414) usa a vigente
- [X] T025 [US6] Rodar T019–T021, T003, `tests/interface/test_legibilidade_da_classificacao.py` (atualizar de propósito as linhas 196 e 229 para ato de redação 2) e `tests/integration/publicacoes`: verdes

**Checkpoint**: FR-1397 cumprido no único leitor que reconstrói frase de ato publicado.

---

## Phase 5: User Story 3 — O documento é o mesmo em qualquer leitor (P1)

**Goal**: a Liberation Sans embutida e medida pelas próprias larguras, só no Edital; a hierarquia nova.

**Independent Test**: [quickstart §4](quickstart.md) e os testes abaixo.

### Testes (primeiro)

- [X] T026 [P] [US3] Em `backend/tests/unit/publicacoes/test_fonte_embutida.py` (novo):
  - o documento do Edital declara duas fontes `/TrueType` com `/FontFile2` (com `/Filter /FlateDecode` e `/Length1`), `/Encoding /WinAnsiEncoding` e recursos `F1` e `F2`;
  - o subconjunto cobre todo caractere que `publicacoes/domain/grafia.py` aceita;
  - o SHA-256 dos arquivos versionados confere com o registrado;
  - a licença OFL acompanha os arquivos (FR-1380, R-007).
- [X] T027 [P] [US3] No mesmo arquivo, a medição:
  - nenhuma linha justificada de A, B e de um sintético com muitos "í", "ª" e "º" passa da margem pela métrica da fonte embutida (FR-1381, SC-519);
  - a Helvetica de hoje continua medindo "í" como 222 para o comprovante, que não muda;
  - os streams de página continuam sem `/Filter` (R-006).
- [X] T028 [P] [US3] Em `backend/tests/unit/publicacoes/test_hierarquia_do_documento.py` (novo), contra os itens da composição:
  - título de seção em 12,5 pt, negrito, seguido de fio;
  - subseção em 11 pt;
  - rótulo de grupo em negrito no corpo do texto;
  - lista com marcador na margem e continuação no recuo pendente (ED-16);
  - bloco destacado com fundo 0,95 e contorno para o resumo, os dados do sorteio e a declaração;
  - nenhuma cor além de cinza (FR-1382).

### Implementação

- [X] T029 [US3] Roteiro de desenvolvimento `backend/scripts/gerar_subconjunto_da_fonte.py` (`uv run --with fonttools`): gera o subconjunto WinAnsi com `recalcTimestamp=False`, grava os arquivos em `backend/processo_seletivo/publicacoes/infrastructure/fontes/` e imprime o SHA-256 da origem e do resultado (R-007)
- [X] T030 [US3] **Com aprovação do usuário** (nome do arquivo, origem e tamanho): baixar a Liberation Sans 2.1.x do release oficial `liberationfonts/liberation-fonts`, conferir a licença (OFL 1.1) **no arquivo distribuído**, rodar T029 e versionar o subconjunto, o texto da licença em `fontes/LICENSE` e um `fontes/ORIGEM.md` com versão, URL e SHA-256 (D-002)
- [X] T031 [US3] `backend/processo_seletivo/publicacoes/infrastructure/fonte.py` (novo): lê o subconjunto, expõe as larguras WinAnsi como métrica e produz os objetos `/TrueType`, `/FontDescriptor` e `/FontFile2`
- [X] T032 [US3] Em `pdf.py`, o perfil de arquivo do Edital: `render_edital_pdf` compõe com `Composicao(metrica=fonte)` e escreve por um escritor do Edital que embute as fontes nos recursos `F1` e `F2`. `render_documento` continua o do comprovante e da divulgação (R-005)
- [X] T033 [US3] Em `pdf.py`, a hierarquia ([contrato §6](contracts/documento.md)): corpo do título de seção, fio, subseção, rótulo de grupo, item de lista com recuo pendente, bloco destacado (caixa de fundo desenhada no próprio fluxo, antes dos fios)
- [X] T034 [US3] Ajustar de propósito os testes de largura e de margem (`test_pdf.py` ~608, 1116, 1268, 1414, ~978; `test_pdf_classificacao.py:360`; `test_tabela_do_documento.py`) para usar a métrica do documento que medem (R-014); rodar T026–T028, T003 e `tests/unit/publicacoes`: verdes

**Checkpoint**: fonte embutida só no Edital; comprovante e divulgação ainda com os bytes de T003.

---

## Phase 6: User Story 2 — O candidato acha a resposta pela pergunta que tem (P1)

**Goal**: o *Catálogo apresentado*, as duas apresentações, o resumo, o sumário, as seções reunidas, as
regras na seção certa, o agrupamento seguro e o aviso de remissão textual.

**Independent Test**: [quickstart §3, §5 e §9](quickstart.md).

### Testes (primeiro)

- [X] T035 [P] [US2] Em `backend/tests/unit/editais/test_catalogo_apresentado.py` (novo):
  - ordem e títulos do catálogo pelo *Catálogo apresentado* da spec, com "Informações gerais" para `informacoes-gerais`;
  - chaves, tipos, fontes e identidade uuid5 iguais aos de hoje;
  - `APRESENTACAO` com os grupos da spec;
  - a assinatura do catálogo novo registrada; uma assinatura desconhecida cai na plana (FR-1367, R-001, R-002).

  Atualizar de propósito `test_secoes.py` (`ORDEM_ESPERADA`) e `test_catalogo_da_054.py` (`_titulos_numerados` sem o filtro de caixa alta).
- [X] T036 [P] [US2] Em `backend/tests/unit/publicacoes/test_numeracao_apresentada.py` (novo):
  - `numeracao`, `numeracao_impressa`, `itens_do_documento` e `tabelas_do_documento` devolvem "N" e "N.k" na apresentação por perguntas, e os números de hoje na plana;
  - seção textual vazia não sai, e a de norma do sistema sai;
  - o `_DESCRICAO_DO_ITEM` cobre a natureza nova (FR-1368, R-003).

  Acrescentar casos a `CASOS` de `test_itens_do_documento.py`.
- [X] T037 [P] [US2] Em `backend/tests/unit/editais/test_numeracao_apresentada_nas_conferencias.py` (novo):
  - a regra de conflito da `065` compara o prefixo apresentado ("3.1" digitado dentro da subseção 3.1 é conflito);
  - remissões a "item 8.2" e "item 6.1" se resolvem pela apresentação;
  - na plana, os números são os do original (FR-1399).

  Atualizar de propósito `test_conflito_de_numeracao.py`, `test_remissoes.py`, `test_numeracao_digitada.py`, `tests/integration/publicacoes/test_numeracao_na_publicacao.py` e `tests/interface/test_numeracao_na_revisao.py` onde os números mudam com a ordem nova.
- [X] T038 [P] [US2] Em `backend/tests/unit/publicacoes/test_apresentacao_por_perguntas.py` (novo), sobre os snapshots de A e B levados ao catálogo novo (helper em `tests/unit/publicacoes/cenarios_da_auditoria.py`), a [§1–§5 do contrato](contracts/documento.md):
  - seções reunidas como subseções N.k (FR-1368);
  - recurso em "Como recorrer?", convocação em "Como será a convocação?", requisitos em "Quem pode se inscrever?", período e dados declarados em "Como se inscrever?" (FR-1369);
  - Requerimento lembrado em Documentos e em Inscrição;
  - descrição fora do ato (FR-1378);
  - siglas preservadas no anúncio (FR-1377);
  - "Autenticidade" (FR-1379);
  - **texto livre literal** (FR-1395): cada parágrafo de cada seção textual do snapshot, inclusive dentro das seções reunidas, aparece literalmente no documento, sem palavra trocada, acrescentada ou tirada;
  - **prévia** (FR-1393, caso-limite "Prévia"): a prévia de um rascunho do catálogo novo compõe pela apresentação por perguntas e pela redação 2, com resumo, sumário e fonte embutida, a marca de prévia e sem autoridade nem integridade; a prévia e o publicado do mesmo conteúdo têm as mesmas seções, frases e quebras de página.
- [X] T039 [P] [US2] Em `backend/tests/unit/publicacoes/test_resumo_do_edital.py` (novo) (FR-1370, FR-1371, R-010):
  - em A, "160 vagas em quatro localidades: …" com os nomes, e "Cadastro de reserva: não há";
  - em B, vagas imediatas com os códigos e "os demais formam cadastro de reserva";
  - acima de 5 localidades, só a contagem;
  - seleção pela forma e pelas Etapas, com nome curto (A: "Análise documental") ou natureza (B);
  - cada linha com "(item N)" certo;
  - a nota de não substituição;
  - o resumo só repete dado do snapshot.
- [X] T040 [P] [US2] Em `backend/tests/unit/publicacoes/test_agrupamento_seguro.py` (novo) (FR-1373 a FR-1375, R-009, SC-524):
  - matriz única quando todo Perfil tem vaga;
  - tabelas separadas e Perfis de mesmo nome agrupados com o nome na legenda (B);
  - "Em todos os Perfis: …" só com o igual;
  - tabela de reserva sem a linha da ampla concorrência e com "—" sem percentual;
  - faixa de códigos só se contígua (TP-01, TP-03, TP-04 saem enumerados);
  - partilha parcial na variante de B: comum uma vez, unidade do corte inteira em cada grupo, desempate inteiro;
  - Edital de um Perfil sem "Em todos os Perfis" nem faixa;
  - dois marcos no mesmo Perfil;
  - método próprio de um marco com os dados próprios;
  - **vocabulário pelo dado** (FR-1365): o Perfil é referido pelo código e a localidade pelo rótulo "Localidade"; o documento composto só escreve "polo", "turma" ou "curso" onde o dado os traz (nome, localidade, descrição, texto livre) — um snapshot sintético sem essas palavras no dado não as tem no documento; os títulos gerados são os genéricos do catálogo.
- [X] T041 [P] [US2] Em `backend/tests/integration/publicacoes/test_retificacao_de_edital_antigo.py` (novo), [quickstart §5](quickstart.md): Edital publicado com o catálogo anterior e retificado depois. O consolidado:
  - tem a ordem, os títulos (em caixa alta), a numeração e a divisão do original;
  - tem a redação 2, a fonte embutida e o sumário;
  - não tem resumo nem reunião de seções;
  - os rótulos gerados G1–G3 dizem "Regras de classificação", e cada remissão trocada aponta para **o mesmo número e o mesmo destino** do original (FR-1366, FR-1399, SC-518, D-007);
  - a tela de Retificação (`interface/retificacao.py:1562`) mostra os números do PDF original (FR-1394, FR-1399, D-003, R-016).
- [X] T042 [P] [US2] Em `backend/tests/unit/editais/test_remissao_pelo_titulo.py` (novo), o leitor e o aviso (FR-1400, R-013):
  - "conforme o método publicado na seção Perfis de Vaga" dá aviso não impeditivo, com o trecho, "repartida" e os destinos possíveis;
  - título com destino único sugere a seção;
  - título que existe no documento não avisa;
  - só no ato de publicação;
  - o texto não muda.

  Em `backend/tests/interface/test_aviso_de_remissao_na_revisao.py` (novo): o aviso aparece na Revisão e na etapa Conteúdo, com âncora na seção.

### Implementação

- [X] T043 [US2] `backend/processo_seletivo/editais/domain/secoes.py`: ordem e títulos do *Catálogo apresentado*; `APRESENTACAO`; a assinatura e o registro de apresentações; o mapa congelado dos títulos anteriores para os destinos (R-001, R-002, R-013). Docstrings com o porquê (as chaves são a identidade; o snapshot guarda o catálogo em que nasceu)
- [X] T044 [US2] Em `pdf.py`, `numeracao`, `numeracao_impressa`, `itens_do_documento`, `tabelas_do_documento` e `plano_de_consolidacao` conscientes da apresentação (R-003)
- [X] T045 [US2] Telas na numeração apresentada:
  - `interface/forms.py:817-848` (`secoes_do_edital`, com o título de grupo);
  - `interface/templates/interface/compor_conteudo.html:53-58`;
  - `interface/static/interface/conteudo.js:27-34` (lê o número do servidor);
  - `interface/revisao.py` (`_secoes_do_documento`, `_secao`);
  - `interface/retificacao.py:1562-1585`.

  **Classes de estilo**: o título de grupo na etapa Conteúdo reusa uma classe que já tem regra na folha de `base.html`. Se for preciso classe nova, a regra entra na folha na mesma tarefa — o guardião de `test_acessibilidade` reprova classe sem regra — e a regra não pode ter `}}` numa linha só (`test_estaticos`). Rodar `tests/interface/test_acessibilidade*.py` e `test_estaticos`.
- [X] T046 [US2] `backend/processo_seletivo/editais/domain/validation.py`: `_DESCRICAO_DO_ITEM` com a natureza nova; o conflito da `065` pelo prefixo apresentado (`_secoes_impressas`, `_numeracao_digitada`, `_itens_impressos`)
- [X] T047 [US2] Em `pdf.py`, a apresentação por perguntas ([contrato §2–§5](contracts/documento.md)):
  - resumo (R-010);
  - sumário em duas passadas, coeso;
  - seções reunidas;
  - regras geradas na seção que trata delas;
  - a seção de vagas (FR-1373, FR-1374), a seleção, o recurso, a convocação e a matrícula;
  - a descrição fora do ato e as siglas preservadas.

  A apresentação plana é a da `068` com a redação 2 e o sumário (R-016).
- [X] T048 [US2] Em `pdf.py`, o agrupamento seguro (R-009): unidades indivisíveis, partilha parcial, faixa de códigos contígua, Perfis de mesmo nome em tabela própria, atributos comuns numa frase
- [X] T049 [US2] `backend/processo_seletivo/editais/domain/numeracao_digitada.py`: o leitor puro de remissão por título; `validation.py`: `_remissao_a_secao_pelo_titulo` (WARNING, código novo, ato de publicação, caminho `/sections/id=…/content`), chamado junto das conferências da `065`; `interface/views.py`: o código em `CODIGOS_DO_TEXTO_DA_SECAO` e nas âncoras (R-013)
- [X] T050 [US2] Atualizar de propósito os testes que afirmam títulos, ordem e numeração de hoje (lista da R-014: `test_pdf.py` — ordem das seções, "ETAPAS DE AVALIAÇÃO", "1. DISPOSIÇÕES PRELIMINARES", `count("EDITAL")`, o `b"Do"` das páginas seguintes —, `test_fecho_e_normas_da_054.py`, `test_consolidacao_por_perfil.py`, `test_itens_do_documento.py` e os de validação), aplicando a forma nova na apresentação por perguntas e a antiga na plana; cada caso em `verificacao.md`
- [X] T051 [US2] Rodar T035–T042 e `tests/unit/editais`, `tests/unit/publicacoes`, `tests/interface`, `tests/integration/publicacoes`: verdes

**Checkpoint**: a estrutura por perguntas nos Editais novos; os antigos intocados na estrutura.

---

## Phase 7: User Story 5 — A paginação não separa o que vai junto (P2)

**Goal**: as regras da FR-1389 a FR-1392, com os parâmetros da R-011.

**Independent Test**: o teste de forma de T052 sobre A, B e a variante.

### Testes (primeiro)

- [X] T052 [P] [US5] Em `backend/tests/unit/publicacoes/test_paginacao_do_edital.py` (novo), varrendo as páginas compostas de A, B, a variante e sintéticos ([contrato §7](contracts/documento.md), SC-521). Zero:
  - título, subseção, rótulo ou legenda no pé sem a linha seguinte;
  - linha de tabela partida;
  - continuação sem cabeçalho;
  - tabela que cabia inteira deixando uma linha na página seguinte;
  - página só com o fecho;
  - página, salvo a última, com mais de 50% da área útil em branco quando o bloco seguinte podia dividir-se.

  Também: item de lista maior que a área útil se parte; o cronograma de 18 linhas quebra com o cabeçalho repetido.

### Implementação

- [X] T053 [US5] Em `pdf.py`, as regras e os parâmetros nomeados da R-011: o `junto` estendido a subseções, rótulos de grupo e legendas; tabela coesa até o limite, com no mínimo duas linhas de cada lado acima dele; bloco relacionado coeso até o limite, com divisão em ponto seguro; item de lista atômico salvo maior que a área; última seção com o fecho; regra de equilíbrio na cascata de `Composicao.paginar`
- [X] T054 [US5] Calibrar os parâmetros em A, B e na variante, olhando as páginas (CoreGraphics), e registrar os valores e a razão em `verificacao.md`; rodar T052 e `tests/unit/publicacoes`: verdes

**Checkpoint**: nenhum dos defeitos de paginação nas três composições.

---

## Phase 8: User Story 4 — O candidato navega no arquivo (P2)

**Goal**: título, idioma, marcadores, links e nome do arquivo no download.

**Independent Test**: [quickstart §7](quickstart.md) e os testes abaixo.

### Testes (primeiro)

- [X] T055 [P] [US4] Em `backend/tests/unit/publicacoes/test_arquivo_do_edital.py` (novo), lendo os objetos do PDF sem biblioteca externa (o guardião de `test_leitura_do_documento_submetido.py` proíbe `pypdf` no produto, e o teste lê pela própria gramática):
  - `/Info` com `/Title` (anúncio em caixa mista) e `/Author`, sem data;
  - `/Lang (pt-BR)`, `/DisplayDocTitle`, `/PageMode /UseOutlines`;
  - `/Outlines` com toda seção e subseção, em dois níveis, cada uma apontando para a página em que começa (SC-520);
  - links do sumário para as seções;
  - **o número impresso em cada linha do sumário é o da página em que a seção começa**, conferido contra as páginas reais da composição, em A, B e na variante (FR-1372, SC-520);
  - `/URI` para o e-mail e para endereço `http(s)` escrito no texto, e nenhum endereço acrescentado;
  - sem `/ID`;
  - os mesmos bytes em duas composições (SC-523);
  - sem `/StructTreeRoot` (FR-1384 a FR-1386, FR-1388).
- [X] T056 [P] [US4] Em `backend/tests/integration/publicacoes/test_nome_do_arquivo.py` (novo): o documento publicado servido por `public-document` tem `Content-Disposition: inline; filename="edital-«n»-«ano».pdf"`; o de Retificação, `edital-«n»-«ano»-retificado-«AAAA-MM-DD».pdf` com a data no fuso institucional; a prévia mantém o nome de hoje (FR-1387, R-012)

### Implementação

- [X] T057 [US4] No escritor do Edital (`pdf.py`): `/Info`, `/Lang`, `/ViewerPreferences`, `/PageMode`, `/Outlines` a partir da lista de itens que numera o documento, anotações `/Link` do sumário e `/URI` das linhas impressas, numeração de objetos determinística (R-012)
- [X] T058 [US4] `backend/processo_seletivo/publicacoes/api/views.py` (`PublishedDocumentView`, :120-133): `Content-Disposition` com o nome da R-012, a partir do Edital e de `Publicacao.published_at`
- [X] T059 [US4] Rodar T055, T056 e `tests/contract`, `tests/integration/publicacoes`: verdes

**Checkpoint**: navegação completa; a limitação de marcação declarada.

---

## Phase 9: Prova, evidências e polimento

- [X] T060 Gerar `specs/069-edital-linguagem-simples/demonstracao/A-publicado-069.pdf`, `B-publicado-069.pdf` e `B-variante-069.pdf` a partir dos snapshots congelados levados ao catálogo novo, no contexto do ato de `cenarios_da_auditoria.py`. Apontar `ESPERADOS` de `test_itens_do_documento.py` para eles. Criar `backend/tests/unit/publicacoes/test_documento_da_auditoria_depois_da_069.py` (molde do da `068`), que prende a diferença de texto. Regenerar `tests/contract/fixtures/documento_publicado_v1.pdf` pela regra da própria docstring, com o diff revisado
- [X] T061 Conferência por enunciado refeita sobre o texto final (FR-1396, SC-517): `specs/069-edital-linguagem-simples/demonstracao/equivalencia.md`, no molde da amostra, para A, B e a variante. Cada regra classificada como =, ≈, → ou + e as frases novas (K7, o resumo, V9, V10, V13) listadas para aprovação do responsável pelo produto
- [X] T062 Cobertura de fatos (SC-516) num teste do arquivo de T060: datas, horas, números com extenso, percentuais, documentos, fundamentos, códigos, localidades, anexos, e-mail e hash de antes, todos presentes depois em A e B
- [X] T063 Cenários A e B **pelo fluxo real**, antes (`main`) e depois, em `ps_069_*` novos ([quickstart §3](quickstart.md)); páginas, diff de texto e medidas em `verificacao.md`
- [X] T064 Três motores ([quickstart §4](quickstart.md)): renderizar título e parágrafo justificado de A e de B em CoreGraphics, poppler e PDFium; olhar as páginas de A, B e da variante (hierarquia, recuos, tabelas, brancos); gravar a comparação e as páginas escolhidas em `demonstracao/` e o que se viu em `verificacao.md` (SC-519)
- [X] T065 Retificação de Edital antigo, ato de ordenação já publicado, acervo e Edital homologado antes da troca, pelo fluxo real ([quickstart §5–§8](quickstart.md)); resultados em `verificacao.md`
- [X] T066 **Jornada pelo navegador, nos canais dos atores** (Constituição, Princípio VI; [quickstart §10](quickstart.md)), num banco de validação novo e no runserver da worktree com o seletor de identidade e a identidade demo do portal:
  1. o Elaborador compõe pelo assistente e confere a prévia (apresentação por perguntas, redação 2, resumo, sumário, fonte);
  2. vê, na Revisão, o aviso de remissão textual de um texto que cita "a seção Perfis de Vaga";
  3. o Homologador homologa e o Publicador publica pela interface;
  4. o candidato baixa o Edital pelo portal e confere o nome `edital-«n»-«ano».pdf`, o título, os marcadores e os links;
  5. a presidência abre a página de um ato de ordenação de redação 1 — publicado e emitido antes, pela interface, com o runserver rodando o código da `main` sobre o mesmo banco — e a de um de redação 2.

  **Um servidor de cada vez** ([quickstart §10](quickstart.md)): o da `main` prepara o ato de redação 1 e é parado; o banco é migrado com esta branch; só então sobe o desta branch, depois de conferir com `lsof` que nenhum outro runserver ocupa `localhost`. Cookie de `localhost` não separa porta, e dois servidores juntos derrubam a sessão da gestão. Se os dois tiverem de ficar no ar, o segundo usa settings no scratchpad com `SESSION_COOKIE_NAME` e `CSRF_COOKIE_NAME` próprios, pela linha de comando, sem editar o `.claude/launch.json`.

  Capturas, o PDF baixado e um `README.md` (passo, ator, canal, o que se viu, a porta e a ordem dos servidores) em `specs/069-edital-linguagem-simples/demonstracao/jornada/`. Os roteiros de T063–T065 medem e não substituem esta jornada; nenhum passo usa shell ou banco
- [X] T067 [P] Notas de emenda nos FRs alcançados:
  - `specs/054-edital-como-ato-oficial/spec.md` (catálogo, FR-981, FR-985);
  - `specs/067-correcoes-de-norma-do-edital/spec.md` (frase de recurso no lugar novo);
  - `specs/068-consolidacao-por-perfil/spec.md` (subseções comuns na apresentação por perguntas; FR-1347);
  - `specs/064-atribuicoes-consolidadas/spec.md`.
- [X] T068 [P] `specs/069-edital-linguagem-simples/rastreabilidade.md`: uma linha por FR, SC e **caso-limite**, com o teste que o cobre, a partir do *Mapeamento requisito → tarefa* abaixo, trocando a tarefa pelo teste efetivamente escrito. Inclui o número de abertura da faixa (molde da `068`)
- [X] T069 [P] Linha da `069` na tabela de incrementos do `README.md`; nota "tratados depois desta auditoria" na §12 de `doc/auditoria-edital-pdf-2026-10-08.md` (ED-05, ED-07 parte P, ED-08, ED-14, ED-16, ED-18, ED-22, ED-24, ED-25), sem regravar os PDFs da auditoria; nota em `doc/analise-edital-linguagem-simples-2026-10-12.md` apontando a entrega
- [X] T070 Registrar a limitação de acessibilidade (FR-1388) em `verificacao.md` e na seção *O que esta feature não cobre*, com o que foi medido (título, idioma, marcadores, links, fonte embutida) e o que não foi (marcação, leitor de tela)
- [X] T071 `cd backend && make lint check` e `make DB_NAME=ps069 test-pg`; números (passando, pulados, tempo) em `verificacao.md`, e em `AGENTS.md` se mudarem os pulados; `tests/test_citacoes_de_requisito.py` e `tests/test_sem_dado_pessoal_da_amostra.py` verdes
- [X] T072 Registrar em `verificacao.md` os achados do caminho que não viraram escopo (os dois da análise já estão em `doc/`)

---

## Mapeamento requisito → tarefa

A base da `rastreabilidade.md` (T068). Cada requisito, critério e caso-limite tem ao menos uma tarefa
de teste e uma de implementação. As tarefas que só verificam estão marcadas com *(v)*.

### Requisitos funcionais

| Requisito | Teste | Implementação |
|---|---|---|
| FR-1360 (redação 2, todas as variantes) | T008, T009, T010 | T013, T014 |
| FR-1361 (equivalência por variante) | T008, T009 (nota por caso); T061 *(v)* | T013, T014 |
| FR-1362 (suplentes só sem cadastro) | T008 (K7, K8) | T014 |
| FR-1363 (recurso sem canal, aspas sem artigo) | T008 (R1–R6) | T014 |
| FR-1364 (mesma frase em todo lugar) | T011, T012 | T015, T016 |
| FR-1365 (código, Localidade, sem "polo" fora do dado) | T040 | T047, T048 |
| FR-1366 (termos internos na redação gerada, nas duas apresentações) | T010, T041 | T014, T047 |
| FR-1367 (catálogo apresentado) | T035 | T043 |
| FR-1368 (seções reunidas) | T036, T038 | T044, T047 |
| FR-1369 (regra na seção que trata dela) | T038 | T047 |
| FR-1370 (resumo) | T039 | T047 |
| FR-1371 (resumo nas palavras do candidato) | T039 | T047 |
| FR-1372 (sumário com página) | T055 | T047, T057 |
| FR-1373 (vagas pelo dado) | T040 | T047, T048 |
| FR-1374 (atributos comuns uma vez) | T040 | T048 |
| FR-1375 (agrupamento por identidade, unidades, faixa) | T040 | T048 |
| FR-1376 (dados do sorteio inteiros) | T009 (S1–S7), T040 | T014, T047 |
| FR-1377 (siglas no anúncio) | T038 | T047 |
| FR-1378 (descrição fora do ato) | T038 | T047 |
| FR-1379 (autenticidade) | T009 (F1), T038 | T014 |
| FR-1380 (fonte embutida e licença) | T026 | T029, T030, T031, T032 |
| FR-1381 (medição pela fonte) | T027 | T031, T032, T034 |
| FR-1382 (hierarquia) | T028 | T033 |
| FR-1383 (comprovante e divulgação intocados) | T003 | T006, T032 |
| FR-1384 (título e idioma) | T055 | T057 |
| FR-1385 (marcadores) | T055 | T057 |
| FR-1386 (links, nenhum endereço acrescentado) | T055 | T057 |
| FR-1387 (nome do arquivo) | T056 | T058 |
| FR-1388 (sem promessa de acessibilidade) | T055 (sem `/StructTreeRoot`) | T070 |
| FR-1389 (sem título órfão) | T052 | T053 |
| FR-1390 (linha de tabela, cabeçalho, sem linha só) | T052 | T053 |
| FR-1391 (blocos relacionados, divisão segura) | T052 | T053, T054 |
| FR-1392 (equilíbrio) | T052 | T053, T054 |
| FR-1393 (hash do já submetido; bytes; prévia) | T021, T038, T055 | T022, T047 |
| FR-1394 (publicado intocado; plana nos antigos) | T021, T041 | T023, T047 |
| FR-1395 (texto livre literal) | T010, T038, T042 | T047, T049 |
| FR-1396 (conferência por enunciado) | T061 *(v)* | T061 |
| FR-1397 (redação histórica do ato publicado) | T019, T020 | T022, T023, T024 |
| FR-1398 (inventário dos leitores) | research R-004 *(v)* | T013, T015, T024 (cada leitor tratado) |
| FR-1399 (remissões intocadas) | T037, T041 | T044, T045, T046 |
| FR-1400 (aviso de remissão textual) | T042 | T049 |

### Critérios de sucesso

| Critério | Tarefas |
|---|---|
| SC-516 (fatos) | T062 |
| SC-517 (equivalência por enunciado; frases novas aprovadas) | T061 |
| SC-518 (termos internos) | T010, T041 |
| SC-519 (três motores; margem) | T027, T064 |
| SC-520 (sumário e marcadores) | T055 |
| SC-521 (paginação) | T052, T054 |
| SC-522 (comprovante e divulgação byte a byte) | T003, T007, T034 *(v)* |
| SC-523 (bytes determinísticos; hash do já submetido) | T021, T055 |
| SC-524 (nome comum e atributos uma vez) | T040 |

### Casos-limite

| Caso-limite da spec | Tarefa |
|---|---|
| Edital de um Perfil só | T040 |
| Todos os Perfis sem vaga imediata | T039, T040 |
| Lista sem percentual (PTT) | T040 |
| Códigos não contíguos | T040 |
| Dois marcos no mesmo Perfil | T040 |
| Método de sorteio próprio | T040, T009 (S3, S4) |
| Recurso vedado; silêncio | T008 (R3, R5) |
| Nome de marco sem gênero | T008 (R1) |
| Texto livre que cita seção pelo título antigo | T042, T066 |
| Termo interno escrito pelo Elaborador | T010 |
| Remissão gerada na apresentação plana | T041 |
| Texto livre que repete regra gerada | T038 (literal) |
| Texto livre que diverge do sistema (achado) | T038 (literal), T072 *(v)* |
| Requisito sem comprovante (achado) | T040 (reproduz o dado), T072 *(v)* |
| Caractere sem grafia na fonte | T026 |
| Prévia | T038 |
| Item de lista maior que uma página | T052 |
| Sigla no título | T038 |
| Endereço escrito no texto livre | T055 |

### Decisões

| Decisão | Teste | Implementação |
|---|---|---|
| D-001 (ordem e títulos do catálogo) | T038 | T043 |
| D-002 (fonte embutida, licença verificada) | T026 | T029, T030, T031 |
| D-003 (Edital antigo mantém a estrutura) | T041 | T044 |
| D-004 (frase dos suplentes condicionada) | T008 (K7, K8) | T014 |
| D-005 (resumo derivado) | T039 | T047; T061 *(v)* |
| D-006 (desempate por data, forma genérica) | T008 (T1, T2) | T013 |
| D-007 ("Regras de classificação" na plana) | T010, T041 | T014 |

## Dependencies & Execution Order

- Phase 1 → Phase 2 → US1 → US6 → US3 → US2 → US5 → US4 → Phase 9.
- **Phase 2 bloqueia tudo:** as fixtures do comprovante e da divulgação têm de existir antes de qualquer
  mudança no escritor ou na métrica.
- **US6 depende de US1:** a redação 2 tem de existir para a página do ato distinguir as duas, e o par
  das duas fases entrega o FR-1397 junto com a redação nova.
- **US3 depende de Phase 2** (a métrica como parâmetro) e de T030, que pede aprovação.
- **US2 depende de US1** (as frases que ela posiciona) e de US3 (a hierarquia que ela usa). A Retificação
  de Edital antigo (T041) depende de US2, que cria a distinção entre as apresentações.
- **US5 depende de US2:** pagina a forma final.
- **US4 depende de US2:** os marcadores e o sumário leem a numeração apresentada. O nome do arquivo
  (T056, T058) é independente e pode vir antes.
- **T060 a T066** dependem de todas as histórias. A jornada (T066) vem depois da implementação completa e antes das notas finais.

## Parallel Opportunities

- Phase 2: T003, T004, T005.
- US1: T008 a T012.
- US6: T019, T020, T021.
- US3: T026, T027, T028.
- US2: T035 a T042.
- US4: T055, T056.
- Phase 9: T067, T068, T069.
- **Entre fases:** T056 e T058 (nome do arquivo) podem ser feitas a qualquer momento depois da Phase 2.

## Implementation Strategy

**MVP = Phase 2 + US1 + US6**: a redação 2 com a redação histórica preservada. Sozinha, ela resolve a
pior nota da auditoria — clareza das frases —, e sem quebrar ato publicado.

Depois:

- **US3** corrige a aparência entre leitores.
- **US2** entrega a organização por perguntas, a maior mudança de leitura.
- **US5 e US4** completam.

A Phase 9 é a prova pedida — equivalência por enunciado, fluxo real, três motores, páginas olhadas e
suíte — e não é opcional.
