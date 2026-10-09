# Tasks: Correções de norma do Edital em PDF — recurso com objeto, sorteio sem conta e Perfil sem vaga imediata

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/frase-de-recurso.md](contracts/frase-de-recurso.md),
[contracts/aviso-de-conferencia-de-recurso.md](contracts/aviso-de-conferencia-de-recurso.md),
[contracts/documento-sob-sorteio-e-sem-vaga.md](contracts/documento-sob-sorteio-e-sem-vaga.md),
[quickstart.md](quickstart.md)

**Tests**: pedidos — cada `FR-`, `SC-`, `UX-` e caso-limite da spec tem teste, e o teste vem
**antes** do código: cada fase de testes roda e falha contra a `main` antes da implementação dela
(Constituição, Princípio V).

**Caminhos**: relativos à raiz do repositório; `backend/` é o projeto Django.

**Testes que mudam de propósito**: os que prendem a frase sem objeto, o arredondamento sob sorteio, o
quadro zerado e os bytes dos PDFs da auditoria. Cada um é atualizado **na tarefa que muda o
comportamento**, com a razão no commit — nunca para "fazer passar".

**Bancos**: `DB_NAME=ps067` para a suíte; `ps_067_*` para a validação, todos novos e com dados
fictícios.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivo diferente, sem dependência pendente)
- **[Story]**: a história da spec (US1 a US5)

---

## Phase 1: Setup

- [X] T001 Medir o ponto de partida: `uv run pytest` contra PostgreSQL (`TEST_DB_ENGINE=postgresql DB_USER=$(whoami) DB_RUNTIME_USER=$(whoami) DB_NAME=ps067`) sobre `tests/unit/editais tests/unit/publicacoes tests/unit/interface tests/contract tests/integration/publicacoes tests/interface/test_compor_quadro.py`; verde, e o total registrado num `specs/067-correcoes-de-norma-do-edital/verificacao.md` novo, seção "Ponto de partida"
- [X] T002 [P] Gravar o texto de referência dos PDFs da auditoria para a comparação: `pdftotext -layout` de `doc/auditoria-edital-pdf-2026-10-08/pdf/A-publicado.pdf` e `B-publicado.pdf` no scratchpad (não versionado); conferir que `test_o_documento_publicado_na_auditoria_sai_com_os_mesmos_bytes` passa na `main`

---

## Phase 2: Foundational — os dois predicados

Bloqueiam US3, US4 e o aviso de US2. Independentes entre si.

### Testes (primeiro; falham por `ImportError`/`AttributeError`)

- [X] T003 [P] Em `backend/tests/unit/editais/test_predicados_da_067.py` (novo), `declara_sorteio` ([contracts/documento-sob-sorteio-e-sem-vaga.md](contracts/documento-sob-sorteio-e-sem-vaga.md), `D-004`): verdadeiro só com `orderProduction == "POR_SORTEIO"`; falso com `"POR_PONTUACAO"`, `""`, ausente, e com forma ausente e `drawMethod` próprio declarado (acervo)
- [X] T004 [P] No mesmo arquivo, `sem_vaga_imediata` (`FR-1320`, `D-007`): verdadeiro com total 0 e todas as linhas em 0; falso com total 6 e uma linha em 0; falso com total 0 e uma linha positiva (incoerente); falso sem quadro (`vacancyTable` ausente ou `[]`); falso com `immediateVacancies` `False` (booleano) ou ausente; verdadeiro com total 0 e `reserveType` `NONE` (caso-limite: a regra é a mesma)

### Implementação

- [X] T005 [P] Em `backend/processo_seletivo/editais/domain/marcos.py`, `declara_sorteio(marco)`, ao lado de `ordena_por_sorteio`, com docstring do porquê da forma declarada (`D-004`: o acervo sem forma sai como sempre saiu)
- [X] T006 [P] Em `backend/processo_seletivo/editais/domain/quadro.py`, `sem_vaga_imediata(perfil)`, com docstring (`D-007`: o incoerente continua com quadro para que o erro se veja)
- [X] T007 Rodar T003 e T004: verdes

**Checkpoint**: os predicados existem; nada os usa ainda.

---

## Phase 3: User Story 1 — O candidato sabe de qual resultado recorre (P1) 🎯 MVP

**Goal**: a frase de recurso nomeia o resultado pelo nome do marco entre aspas (`D-001`), em todas
as superfícies.

**Independent Test**: compor o snapshot congelado de A e conferir as 4 frases com o nome; nenhuma
frase de marco termina em "contados da divulgação do resultado".

### Testes

- [X] T008 [P] [US1] Em `backend/tests/unit/publicacoes/test_frase_de_recurso.py` (novo), a tabela de [contracts/frase-de-recurso.md](contracts/frase-de-recurso.md) (`FR-1300`, `FR-1301`, `FR-1302`, `FR-1303`): afirmativa com nome (2 e 1 dia; 11 dias sem extenso), negativa com nome, sem nome com código, sem nome e sem código (frases de hoje), silêncio (`""`), prazo inválido (0, negativo, booleano, ausente) → `""`; nome com aspas próprias sai como foi escrito; nome com espaços nas pontas é aparado; `prazo_do_recurso` devolve `2 (dois) dias corridos` e `1 (um) dia corrido` (`FR-1300` a `FR-1303`)
- [X] T009 [P] [US1] No mesmo arquivo, a frase no **documento composto**: o snapshot congelado de A (`doc/auditoria-edital-pdf-2026-10-08/snapshots/A-conteudo-publicado.json`) renderizado tem 4 ocorrências de "Caberá recurso contra o resultado de “Classificação por sorteio eletrônico”, no prazo de 2 (dois) dias corridos, contados da divulgação desse resultado." no texto corrido, e nenhuma de "contados da divulgação do resultado"; o nome longo (255 caracteres) quebra sem truncar; o modo prévia imprime a mesma frase (`FR-1304`)
- [X] T010 [P] [US1] Em `backend/tests/unit/interface/test_revisao.py` (acréscimo), a Revisão do marco mostra a mesma frase que `_janela_recursal` devolve, com o resultado dito "deste marco" abaixo da denominação (`FR-1304`, `D-012` — achado na implementação: o nome na frase desfazia o agrupamento por Perfil)
- [X] T011 [US1] Rodar T008 a T010 contra a `main`: falham por `ImportError` (`prazo_do_recurso`) ou pela frase antiga, e nenhum por outra razão

### Implementação

- [X] T012 [US1] Em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`, extrair `prazo_do_recurso(marco)` e reescrever `_janela_recursal(marco)` pela tabela do contrato; a docstring cita ED-02, `D-001` (por que aspas: o nome não tem gênero) e mantém os parágrafos do silêncio e da negativa
- [X] T013 [US1] Atualizar de propósito `backend/tests/unit/publicacoes/test_pdf.py` (as duas asserções da frase, linhas ~1639 e ~1655) e `backend/tests/integration/publicacoes/test_documento_da_retificacao_que_acrescenta.py` ("Caberá recurso no prazo de 3 (três)") para a frase nova, com o nome do marco do teste
- [X] T014 [US1] Rodar T008 a T010 e os testes de T013: verdes

**Checkpoint**: a frase tem objeto no documento, na prévia e na Revisão.

---

## Phase 4: User Story 3 — Marco por sorteio sem arredondamento e sem empate no corte (P1)

**Goal**: ED-03 inteiro — validação, documento, Revisão, tela, Retificação e emissão juntos.

**Independent Test**: marco por sorteio sem arredondamento publica; documento e Revisão sem
"Arredondamento" e sem "Empate no corte" sob ele; marco por pontuação sem arredondamento continua
recusado.

### Testes

- [X] T015 [P] [US3] Em `backend/tests/unit/editais/test_arredondamento_sob_sorteio.py` (novo), a tabela de validação do contrato (`FR-1311`, `FR-1312`): sob `POR_SORTEIO`, `rounding` ausente, `None`, `{}` e `{"scale": None, "mode": None}` não geram `milestone_rounding_invalid`; `{"scale": 9, "mode": "X"}` gera; sob `POR_PONTUACAO` e sob forma ausente (mesmo com `drawMethod` próprio), `rounding` ausente continua gerando; na Retificação (`ato=ATO_DE_RETIFICACAO`), a mesma coisa
- [X] T016 [P] [US3] Em `backend/tests/unit/publicacoes/test_documento_sob_sorteio.py` (novo), a tabela do marco do contrato (`FR-1313`, `FR-1314`): sob sorteio declarado com `rounding` e `tieOutcome` declarados, o texto do bloco do marco não tem "Arredondamento" nem "Empate no corte", e mantém "Ordem", "Sorteio", "Recurso", "Corte", "Continuação"; sob pontuação, "Arredondamento" e "Empate no corte" saem; sob forma ausente (acervo) com `drawMethod` próprio, saem como hoje; o snapshot congelado de A não tem nenhuma das duas linhas
- [X] T017 [P] [US3] Em `backend/tests/interface/test_correcoes_de_norma_na_revisao.py` (novo), Revisão e tela (`FR-1315`, `FR-1316`, `UX-193`): a Revisão do marco por sorteio não lista "Arredondamento" nem "Empate no corte", e a do marco por pontuação lista; o cartão do marco por sorteio não tem os controles visíveis `-scale`/`-mode` (só ocultos), e o por pontuação tem; salvar um marco por sorteio pela etapa Classificação grava `arredondamento == {}`; o fragmento recomposto com `orderProduction=POR_PONTUACAO` a partir de um cartão por sorteio traz os campos visíveis com 2 e `MEIO_PARA_CIMA`; a ajuda do marco diz que o arredondamento é da ordem por pontuação
- [X] T018 [P] [US3] No mesmo arquivo, a tela da Retificação (`FR-1317`): para marco por sorteio sem arredondamento, a dica de vazio de `rounding/mode` não diz "a publicação será impedida"; para marco por pontuação, continua dizendo
- [X] T019 [P] [US3] Em `backend/tests/integration/classificacao/test_emissao_de_marco_por_sorteio.py` (novo, ou acréscimo ao teste da recusa existente — procurar `ordering_milestone_is_drawn` em `backend/tests/`), `FR-1318`: Edital publicado com marco por sorteio sem arredondamento que enumera uma Etapa classificatória, inscrições com pontuação consolidada nessa Etapa; emitir a ordem pelo comando de emissão responde com a recusa `ordering_milestone_is_drawn`, e não com exceção
- [X] T019a [P] [US3] Em `backend/tests/integration/classificacao/test_emissao_de_marco_por_sorteio.py`, `FR-1319`: com o marco por sorteio sem arredondamento, o sorteio é constituído e realizado pelo caminho de hoje, o resultado é divulgado e a reprodução confere — as posições e o conteúdo divulgado são os mesmos de um marco idêntico com arredondamento declarado (procurar o roteiro de sorteio já usado em `backend/tests/integration/sorteios/` e reaproveitá-lo). *Feito:* o sorteio constituído pelo roteiro de `test_constituicao.py`, com o marco publicado sem arredondamento, produz a ordem do algoritmo publicado, posições 1 a 5; a divulgação, por `_escala`, cai na escala padrão sem arredondamento — o marco por sorteio não tem pontuação a formatar
- [X] T020 [US3] Rodar T015 a T019a contra a `main`: falham pelo comportamento antigo (recusa do arredondamento, linhas impressas, campos visíveis, `RegraIncompleta`), e nenhum por outra razão

### Implementação

- [X] T021 [US3] Em `backend/processo_seletivo/editais/domain/validation.py`, `_arredondamento_do_marco` (chamado em `_coerencia_dos_marcos`): sob `declara_sorteio`, arredondamento vazio não gera achado; declarado, continua conferido pela mesma `arredondamento_publicado`; comentário no tom do arquivo (ED-03; por que a forma declarada; o paralelo com `FR-928`)
- [X] T022 [US3] Em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py::_marcos`, não acrescentar "Arredondamento" nem "Empate no corte" quando `declara_sorteio(marco)`; atualizar o comentário que hoje explica o `sorteia` e o de `EMPATE_NO_CORTE`
- [X] T023 [US3] Em `backend/processo_seletivo/interface/revisao.py::_leitura_do_marco`, a mesma omissão pela forma declarada (`D-004`), mantendo o `sorteia` resolvido para a combinação e o bloco do sorteio
- [X] T024 [US3] Tela do marco (`D-008`): em `backend/processo_seletivo/interface/templates/interface/_marco.html`, os campos de arredondamento visíveis só fora do sorteio declarado, e ocultos com os valores do marco ou do `ARREDONDAMENTO_PADRAO` sob sorteio; em `backend/processo_seletivo/interface/forms.py`, gravar `rounding: {}` quando `orderProduction == POR_SORTEIO`; o contexto do cartão (`interface/views.py`, `_reexibir_marco`/`_marco_novo` e `forms._marco_para_o_formulario`) fornece o padrão para os ocultos; ajuda em `_como_preencher_o_marco.html` (`UX-193`). Respeitar a regra da folha de estilo (classe nova exige regra em `base.html`)
- [X] T025 [US3] Em `backend/processo_seletivo/interface/retificacao.py`, a dica de vazio de `rounding/mode` (e de `rounding/scale`, se houver) condicionada a `declara_sorteio`: sob sorteio, "Não declarado — a ordem é sorteada, e não há nota a arredondar"
- [X] T026 [US3] Em `backend/processo_seletivo/classificacao/application/emissao.py`, a recusa do marco por sorteio antes de `calcular_ordem` (`D-009`): ler o conteúdo da versão vigente no instante do comando e chamar a mesma conferência; ajustar o comentário "O cálculo vem antes da busca do vigente" para dizer por que a recusa do sorteio vem antes do cálculo
- [X] T027 [US3] Atualizar de propósito os testes que prendiam o comportamento antigo — `backend/tests/unit/editais/test_marco_classificatorio.py` se algum caso exigir arredondamento sob sorteio declarado, e qualquer teste de `tests/unit/publicacoes/test_pdf_classificacao.py` ou `tests/unit/interface/test_revisao.py` que espere "Arredondamento"/"Empate no corte" sob sorteio declarado — e rodar T015 a T019 e esses arquivos: verdes

**Checkpoint**: ED-03 fechado nos dois lados.

---

## Phase 5: User Story 4 — Perfil sem vaga imediata sem quadro zerado nem reversão (P2)

**Goal**: ED-12 com `D-003` — omitir quadro e reversão, sem regra nova.

**Independent Test**: o snapshot congelado de B composto tem 2 quadros e 2 reversões.

### Testes

- [X] T028 [P] [US4] Em `backend/tests/unit/publicacoes/test_perfil_sem_vaga_imediata.py` (novo), a tabela do Perfil do contrato (`FR-1321` a `FR-1323`): Perfil sem vaga imediata não tem "Quadro de vagas" nem frase de reversão, e tem a tabela de Modalidades com percentual e fundamento, a forma de convocação e os marcos; Perfil com 6 vagas e uma linha em 0 tem quadro com a linha em 0 e a reversão; as legendas "Tabela N" saem sem lacuna; nenhuma frase nova sobre cadastro (`FR-1322`); Perfil incoerente (total 0, linha positiva) tem quadro; Perfil sem vaga e sem cadastro (`reserveType` `NONE`) também não tem quadro nem reversão; a tabela de Perfis continua sem a linha de total quando o total do Edital é 0
- [X] T029 [P] [US4] No mesmo arquivo, o snapshot congelado de B: exatamente 2 legendas "Quadro de vagas" (TD-ADM, TD-INFO-EDU) e 2 frases de reversão; 18 tabelas de Modalidades; e `tabelas_do_documento(B)` igual ao número de legendas "Tabela N" do documento composto (o guardião da `065` em `test_itens_do_documento.py` cobre o geral; este prende o caso)
- [X] T030 [P] [US4] Em `backend/tests/interface/test_correcoes_de_norma_na_revisao.py`, a Revisão do Perfil sem vaga imediata mostra a reversão declarada seguida de "não sai no documento: o Perfil não tem vaga imediata", e a do Perfil com vaga não (`UX-192`)
- [X] T031 [P] [US4] Em `backend/tests/unit/editais/test_predicados_da_067.py` ou arquivo de validação existente, `FR-1324`: o conteúdo de B continua com o mesmo conjunto de achados de validação de antes desta história (a reversão declarada aceita; `reserve_only_convocation_external` 16 vezes na publicação)
- [X] T032 [US4] Rodar T028 a T031 contra o código da fase anterior: falham pelo quadro e pela reversão impressos e pela nota ausente; T031 passa (é guarda)

### Implementação

- [X] T033 [US4] Em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`, `_quadro_de_vagas_do_perfil` retorna sem tabela e sem reversão quando `sem_vaga_imediata(perfil)`; `tabelas_do_documento` conta o quadro só quando ele sai; docstrings com ED-12 e `D-003` (por que nenhuma frase substitui o quadro)
- [X] T034 [US4] Em `backend/processo_seletivo/interface/revisao.py`, a nota da reversão do Perfil sem vaga imediata (`UX-192`)
- [X] T035 [US4] Rodar T028 a T031, `tests/unit/publicacoes/test_itens_do_documento.py` (o guardião da `065`, exceto o de bytes, que muda em US5) e `tests/interface/test_compor_quadro.py`: verdes

**Checkpoint**: ED-12 fechado.

---

## Phase 6: User Story 2 — Quem elabora confere os prazos de recurso contra o Cronograma (P1)

**Goal**: o aviso de conferência de [contracts/aviso-de-conferencia-de-recurso.md](contracts/aviso-de-conferencia-de-recurso.md) (`D-002`, `D-006`).

**Independent Test**: as Revisões de A e de B mostram o aviso uma vez; os dois publicam.

### Testes

- [X] T036 [P] [US2] Em `backend/tests/unit/editais/test_conferencia_do_recurso.py` (novo), `FR-1305` a `FR-1310`: Evento de recurso pela tabela do contrato (inclusive "Concurso", "percurso", "Discurso" → não); emitido com marco que admite e com marco que nega; **não** emitido sem regra de recurso em marco algum, com Eventos de recurso no Cronograma (`FR-1308`); um achado só, `WARNING`, código `appeal_schedule_review`, caminho `schedule`; agrupamento por nome e regra (4 Perfis de A numa linha; mesmo nome e prazos diferentes em duas); "N Perfis" acima de seis; Evento sem término "em {início}"; Cronograma sem Evento de recurso → "O Cronograma não tem Evento de recurso."; mensagem sem código interno, caminho ou nome de campo (`UX-190`); severidade de aviso também com `ato=ATO_DE_RETIFICACAO` (`FR-1309`); a orientação final está presente e nenhuma frase afirma correspondência, falta ou sobra (`FR-1307`); o snapshot não é alterado (`FR-1310`)
- [X] T037 [P] [US2] No mesmo arquivo, os cenários: o snapshot congelado de A produz a mensagem com “Classificação por sorteio eletrônico” (INF-BJN, INF-IUN, INF-SMT, INF-VAL) — 2 (dois) dias corridos e o Evento "Prazo para interposição de recurso — de 26/11/2026, às 00h, a 27/11/2026, às 23h59"; o de B, com 18 Perfis e os 4 Eventos na ordem do Cronograma
- [X] T038 [P] [US2] Em `backend/tests/interface/test_correcoes_de_norma_na_revisao.py`, a Revisão de um rascunho com marco que admite recurso mostra o aviso, com link para a etapa Cronograma (`UX-191`), e a submissão segue possível
- [X] T039 [P] [US2] Em `backend/tests/integration/publicacoes/test_correcoes_de_norma_na_publicacao.py` (novo), submissão, homologação e publicação com o aviso não são impedidas; a conferência da Retificação (`advertencias_do_ato`) mostra o aviso e a Retificação publica (`FR-1309`); a página do Edital publicado não exibe o aviso (`FR-1328`)
- [X] T040 [US2] Rodar T036 a T039 contra o código da fase anterior: falham por falta do aviso, e nenhum por outra razão

### Implementação

- [X] T041 [US2] Em `backend/processo_seletivo/editais/domain/validation.py`, `_conferencia_do_recurso(snapshot)` registrada em `validate_for_publication`, pelo contrato; a importação de `prazo_do_recurso` e `_instante` do compositor adiada, com o comentário do porquê (a grafia é uma só; `065`, decisão 004); docstring com ED-02, `D-002` e o que o aviso não afirma
- [X] T042 [US2] Conferir que o destino na interface já leva `schedule` ao Cronograma (`interface/views.py::DESTINO_DA_PENDENCIA`) e, se o título dos avisos depender de mapa por código, acrescentar o de `appeal_schedule_review` ("Prazos de recurso a conferir"); rodar T036 a T039: verdes
- [X] T043 [US2] Atualizar de propósito os testes de interface e integração que contam avisos exatos de um rascunho com marco que publica recurso (procurar asserções de lista completa de códigos de aviso em `backend/tests/`), um a um, com o motivo. *Feito:* nenhum precisou — a suíte das áreas (6200 passados) não tem asserção de lista completa de avisos que o novo alcance

**Checkpoint**: ED-02 fechado nos dois lados.

---

## Phase 7: User Story 5 — O que já foi publicado não muda, e os bytes (P2)

**Goal**: `FR-1325` a `FR-1327`, `SC-505`, `SC-506` e `D-010`.

### Testes

- [X] T044 [P] [US5] Em `backend/tests/integration/publicacoes/test_correcoes_de_norma_na_publicacao.py`, o acervo: um `DocumentoPublicado` gravado com bytes do renderizador anterior (os de `doc/auditoria-edital-pdf-2026-10-08/pdf/A-publicado.pdf`, associados a uma publicação do teste) é servido pela view com os mesmos bytes e o mesmo hash (`FR-1325`); uma Retificação publicada depois sai pelas regras novas — sem "Arredondamento" sob sorteio, com o recurso nomeado (`FR-1326`); o conteúdo canônico publicado tem a mesma `schemaVersion` (`FR-1327`)
- [X] T045 [US5] Em `backend/tests/unit/publicacoes/test_itens_do_documento.py`, o guardião de bytes passa a comparar com `specs/067-correcoes-de-norma-do-edital/demonstracao/A-publicado-067.pdf` e `B-publicado-067.pdf` (docstring: por que os PDFs da auditoria não são regravados, `D-010`); e um teste novo, `test_a_diferenca_para_a_auditoria_e_so_a_pretendida`, que extrai o texto (o `texto_de` dos testes de contrato) do PDF da auditoria e do composto agora, descarta cabeçalho e rodapé de página, **junta as linhas em parágrafos** (a frase nova quebra em outro lugar, e a paginação muda) e normaliza a numeração "Tabela N", e exige que os trechos removidos e acrescentados sejam exatamente: em A, as 4 frases de recurso trocadas, 4 "Arredondamento" e 4 "Empate no corte" removidos; em B, as 18 frases de recurso trocadas, 16 quadros (legenda, cabeçalho e 4 linhas cada) e 16 reversões removidos
- [X] T046 [US5] Gerar `specs/067-correcoes-de-norma-do-edital/demonstracao/A-publicado-067.pdf` e `B-publicado-067.pdf` pela mesma chamada do guardião (snapshots congelados, unidade, autoridade e data fixas) e rodar T044 e T045: verdes; `tests/contract/test_documento_publicado.py` verde **sem** tocar a fixture (`SC-505`)

**Checkpoint**: o documento só mudou onde devia, e isso está preso por teste.

---

## Phase 8: Polish, cenários reais e verificação

- [X] T047 Cenários A e B pelo fluxo real (`SC-500`, `SC-501`, `SC-503`, `SC-504`), antes e depois ([quickstart.md](quickstart.md) §2): extrair a `main` com `git archive` para o scratchpad; adaptar os roteiros da auditoria por variáveis de caminho (sem mudar o conteúdo dos cenários); publicar em `ps_067_a_antes`/`ps_067_b_antes` com o código antigo e em `ps_067_a_depois`/`ps_067_b_depois` com o novo; registrar os achados da submissão (o aviso; nenhum impeditivo) e o caso de A sem arredondamento
- [X] T048 Diff de texto (`pdftotext -layout`) dos PDFs do fluxo real contra os da auditoria; conferir que só mudou o pretendido (`SC-502`) e que os bytes do "depois" são os de `demonstracao/` (mesmo snapshot → mesmo documento); registrar contagens em `verificacao.md`. *Feito com uma correção ao plano:* os bytes do fluxo real não são os de `demonstracao/` — o conteúdo de cada banco tem identificadores próprios, e o resumo de verificação muda —; a comparação é de texto, com o resumo neutralizado
- [X] T049 Páginas por CoreGraphics (`qrender_all.py`), antes e depois: A p. 3; B pp. 4, 7 e 8 (e as que a repaginação mover); olhar cada uma; gravar as escolhidas em `specs/067-correcoes-de-norma-do-edital/demonstracao/`
- [X] T050 Interface pelo navegador (quickstart §4) num banco de validação: o aviso na Revisão com link para o Cronograma; a tela do marco por sorteio sem arredondamento e a volta para pontuação com os campos preenchidos; a nota da reversão no Perfil TP-01; capturas em `demonstracao/`
- [X] T051 [P] `specs/067-correcoes-de-norma-do-edital/rastreabilidade.md`: cada `FR-`, `SC-`, `UX-`, decisão e caso-limite com o teste que o prende (modelo da `065`)
- [X] T052 [P] `specs/067-correcoes-de-norma-do-edital/verificacao.md` completo: ponto de partida, testes da feature (com a falha antes do código), cenários, diff, páginas, suíte; e o status da spec para "Implementado"
- [X] T053 [P] Registrar no fim da auditoria (`doc/auditoria-edital-pdf-2026-10-08.md`, nota curta abaixo da §12.1) que ED-02, ED-03 e ED-12 foram tratados pela `067`, e o que ficou aberto (RC-58; a conferência humana do objeto do recurso)
- [ ] T054 (`SC-507`) `cd backend && make lint check` e a suíte completa contra PostgreSQL com `DB_NAME=ps067`; registrar o total e os pulados em `verificacao.md`; se os números do `AGENTS.md` mudarem, atualizá-los

---

## Dependencies & Execution Order

- **Setup (1)** → **Foundational (2)** → histórias.
- **US1 (3)** depende só do Setup; é o MVP.
- **US3 (4)** depende de `declara_sorteio` (T005).
- **US4 (5)** depende de `sem_vaga_imediata` (T006).
- **US2 (6)** depende de `prazo_do_recurso` (T012, US1).
- **US5 (7)** depende de US1, US3 e US4 (o documento final) — os bytes esperados só se geram depois das três.
- **Polish (8)** depende de tudo.

US1, US3 e US4 tocam `pdf.py` em funções diferentes; em sequência, para que cada commit tenha um
documento coerente.

## Parallel Example

```text
# Fase 2: T003 e T004 juntos; T005 e T006 juntos.
# US3: T015, T016, T017, T018, T019 juntos (arquivos diferentes), depois T021–T026.
# US2: T036–T039 juntos.
# Polish: T051, T052, T053 juntos.
```

## Implementation Strategy

1. **MVP**: Setup + Foundational + US1 — o único P0 restante já sai com objeto.
2. US3 (ED-03, P1), US4 (ED-12), US2 (o aviso), cada uma com seu commit e a suíte das áreas verde.
3. US5 fecha os bytes depois que o documento final existe.
4. Polish: cenários reais, páginas, rastreabilidade, suíte completa.

**Por que US2 vem depois de US3 e US4, sendo P1:** ela só depende de US1 (o prazo), e qualquer ordem
funcionaria; vem depois para que os testes de aviso e as contagens de avisos atualizadas em T043
sejam escritos sobre o documento e a validação finais, e não refeitos duas vezes.
