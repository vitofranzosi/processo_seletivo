# Tasks: Detecção de conflitos de numeração no Edital

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/achados-de-numeracao.md](contracts/achados-de-numeracao.md),
[contracts/itens-do-documento.md](contracts/itens-do-documento.md), [quickstart.md](quickstart.md),
[insumos-para-o-plano.md](insumos-para-o-plano.md)

**Tests**: pedidos — cada `FR-`, `SC-` e caso-limite da spec tem teste, e o teste vem **antes** do
código: cada fase de testes roda e falha contra a `main` antes da implementação dela (Constituição,
Princípio V).

**Caminhos**: relativos à raiz do repositório; `backend/` é o projeto Django.

**Produção**: cinco arquivos e nada além —
`backend/processo_seletivo/editais/domain/numeracao_digitada.py` (novo),
`backend/processo_seletivo/editais/domain/validation.py`,
`backend/processo_seletivo/publicacoes/infrastructure/pdf.py` (só uma função nova; **nenhuma linha da
composição muda**, `D-014`), `backend/processo_seletivo/interface/views.py` e
`backend/processo_seletivo/interface/templatetags/interface_extras.py`.

**Cenários**: nenhum dado pessoal real em teste nem em `doc/` (`test_sem_dado_pessoal_da_amostra.py`
varre os dois). Os casos legítimos são sintéticos, escritos nas formas da amostra.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivo diferente, sem dependência pendente)
- **[Story]**: a história da spec (US1 a US4)

---

## Phase 1: Setup

- [ ] T001 Preparar a worktree: `cd backend && uv sync --extra dev`; conferir `pg_isready` e criar o banco de base da validação `ps_065_base` com `migrate` (comandos do [quickstart.md](quickstart.md), *Pré-requisitos*)
- [ ] T002 Medir o ponto de partida: `make test-pg` só sobre `tests/unit/editais tests/unit/publicacoes tests/contract tests/interface/test_caractere_sem_grafia.py tests/integration/publicacoes` com `DB_NAME` próprio da worktree; verde, e o total registrado num `specs/065-conflitos-de-numeracao/verificacao.md` novo, na seção "Ponto de partida"

---

## Phase 2: Foundational — reconhecimento puro e itens do documento

Bloqueia todas as histórias: as quatro usam o reconhecimento (`D-005`, `D-010`) e os itens do
documento (`D-004`). As duas metades são independentes entre si.

### Testes (escritos primeiro; falham por falta do módulo e da função)

- [ ] T003 [P] Em `backend/tests/unit/editais/test_numeracao_digitada.py` (novo), testes do **número de subitem no começo do parágrafo** (`FR-1199`, `D-010`): reconhece "4.1 A…", "4.1. A…", "4.1) A…", "4.1 – A…", "4.1 - A…", "4.1" sozinho, "4.2.1 …", "4.2.1.3 …", "• 4.1 …", "  4.1 …", "04.1 …" (primeiro grupo 4); devolve o texto do número, o primeiro grupo como inteiro e o resto
- [ ] T004 [P] No mesmo arquivo, o **conjunto de prova de casos legítimos** (`SC-464`, tabela de *Edge Cases* da spec), parametrizado, com ao menos 40 parágrafos sintéticos e ao menos dois por linha da tabela: datas ("20/10/2026, às 9h…", "24.08.2026 — …"), números de lei ("13.146/2015, que…", "8.112/1990 …", "12.711/2012"), valores ("1.000,00 …", "R$ 1.500,00"), horas e carga horária ("30h", "1.000 horas", "14h30", "08:00"), percentual ("25% das vagas"), ordinais ("1º …", "2ª chamada"), decimal com unidade ("7.5 pontos", "6.0 (seis) pontos", "10.5 horas"), processo, CEP e telefone ("23185.000123/2026-11", "29.000-000", "(27) 3198-0925"), ano ("2026. Fica…"), listas de um nível ("1. Ler o Edital", "1) …", "I – …", "a) …"): nenhum é número de subitem
- [ ] T005 [P] No mesmo arquivo, o **título transcrito** (`FR-1201`): "11. DA CONVOCAÇÃO" e "6 - DA VERIFICAÇÃO DA AUTODECLARAÇÃO" são; "11. Da convocação", "1. Ler o Edital", "4.1 DA INSCRIÇÃO" e "11. CPF" (menos de três letras) não são
- [ ] T006 [P] No mesmo arquivo, as **remissões** (`FR-1204`, `D-010`): "item 8.1", "Item 8.1", "subitem 4.2", "itens 4.1, 4.2 e 4.3", "itens 4.1 a 4.5" (duas pontas), "itens 4.1 ou 4.2", "item 5" (nível de seção), "Tabela 3", "Quadro 2"; são internas "item 5.4 deste Edital" e "item 5.4 do edital"; **não** são remissões deste documento "item 4.1 do Edital nº 28/2026", "item 4.1 da Resolução CS nº 10/2017", "inciso II do art. 3º", "item 2.3 do Anexo II", "Quadro 2 do Anexo III", "item 7 da Portaria", e a exclusão não atravessa ponto final ("…item 4.1. A Lei…" é interna); devolve o literal e os números de cada remissão
- [ ] T007 [P] Em `backend/tests/unit/publicacoes/test_itens_do_documento.py` (novo), o **guardião** de `D-004` e de `FR-1205` ([contracts/itens-do-documento.md](contracts/itens-do-documento.md)): para os conteúdos de `doc/auditoria-edital-pdf-2026-10-08/snapshots/A-conteudo-publicado.json` e `B-conteudo-publicado.json` e para casos sintéticos (um Perfil só; Perfil sem quadro; Perfil sem modalidade; Edital sem Etapa; Perfis com atribuições comuns; seção gerada cuja coleção está vazia), compõe o documento (`Composicao` + `_secoes` sobre o snapshot normalizado) e colhe dos itens desenhados os títulos de subseção numerados (`^\d+\.\d+ `, em negrito) e as legendas `^Tabela (\d+) — `; os números colhidos e o total de tabelas são os da função nova
- [ ] T008 Rodar T003 a T007 contra a `main`: falham por `ImportError`/`AttributeError`, e nenhum por outra razão

### Implementação

- [ ] T009 [P] Criar `backend/processo_seletivo/editais/domain/numeracao_digitada.py`, sem Django e sem banco, com três funções puras e a lista de unidades de `D-010`: o número de subitem no começo de um parágrafo (retira espaços e marcadores iniciais; dois a quatro grupos de um ou dois algarismos; os separadores e as exclusões de `D-010`; primeiro grupo como inteiro); o título transcrito; e as remissões de um texto (formas, listas, intervalos, exclusão de outro ato ou Anexo até oito palavras sem atravessar ponto final). Docstring no tom do repositório: o achado ED-01, por que a forma é estreita (`D-001` torna o conflito impeditivo), o erro aceito da unidade
- [ ] T010 [P] Em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`, logo depois de `numeracao`, a função pura dos itens do documento ([contracts/itens-do-documento.md](contracts/itens-do-documento.md)): números das seções materializadas, das subseções de Perfis (`N.1…N.k` e as comuns de `grupos_de_atribuicoes`), das Etapas (`N.1…N.m`), com natureza e descrição, e o total de tabelas (tabela de Perfis com mais de um Perfil; por Perfil, quadro se houver linha e modalidades se houver alguma; Cronograma se houver Evento — sempre só em seção materializada). **Nenhuma linha da composição muda**
- [ ] T011 Rodar T003 a T007: verdes; e `tests/contract/test_documento_publicado.py` verde sem refazer a fixture

**Checkpoint**: o reconhecimento e os itens existem e estão provados; nada os usa ainda.

---

## Phase 3: User Story 1 — Quem elabora descobre o subitem com número de outra seção (Priority: P1) 🎯 MVP

**Goal**: o conflito comprovado aparece na etapa Conteúdo e na Revisão, agrupado por seção, com
parágrafo, número digitado e trecho, e leva ao campo da seção.

**Independent Test**: o rascunho do cenário B mostra 5 achados para as 5 seções em conflito e nenhum
para as 2 coerentes (`SC-462`).

### Testes

- [ ] T012 [P] [US1] Em `backend/tests/unit/editais/test_conflito_de_numeracao.py` (novo), sobre conteúdos montados como `_conteudo` de `backend/tests/unit/editais/test_avisos_do_documento_oficial.py` (catálogo inteiro, textuais vazias onde nada foi escrito): seção que sai como 4 com parágrafos "3.1…3.4" → **um** achado `typed_numbering_conflict`, impeditivo, caminho `/sections/id=…/content`, mensagem com "comprovado", o título da seção, "4", os ordinais 1 a 4, "3.1"…"3.4" e o trecho de cada um (`FR-1200`, `FR-1214`, `FR-1215`, `FR-1217`); seção que sai como 2 com "2.1…2.4" → nada; preâmbulo com "1.1" → conflito que diz "o preâmbulo" (`FR-1200`)
- [ ] T013 [P] [US1] No mesmo arquivo, os casos-limite de numeração da spec: seção misturada (sai como 11 com "12.1", "8.1" e "11.1" → conflito nos dois primeiros, não no terceiro); "04.1" em seção 4 → nada; "4.1​ A inscrição…" em seção 4 → nada (normalização, `D-009`); seção vazia → não conferida; a seção da Inscrição com a frase do teto acrescentada pelo sistema → só o texto do autor é lido; texto com uma linha em branco entre parágrafos → o ordinal ignora a linha em branco; trecho de parágrafo longo cortado em fim de palavra, com reticências, até oitenta caracteres
- [ ] T014 [P] [US1] No mesmo arquivo, a numeração **refeita** (`FR-1202`): o mesmo texto "4.1…" sem conflito quando a seção sai como 4, e com conflito quando uma seção textual anterior é esvaziada e ela passa a sair como 3; e o título transcrito "11. DA CONVOCAÇÃO" numa seção que sai como 12 → `typed_numbering_suspected_title`, aviso, com "suspeita" (`FR-1201`)
- [ ] T015 [P] [US1] Em `backend/tests/unit/editais/test_conflito_de_numeracao.py`, o cenário B (`SC-462`): sobre `doc/auditoria-edital-pdf-2026-10-08/snapshots/B-conteudo-publicado.json`, exatamente 5 achados de conflito — "Da Inscrição" (4: 3.1–3.4), "Da Verificação da Autodeclaração" (6: 4.1–4.3), "Dos Recursos" (11: 8.1–8.3), "Da Convocação" (12: 11.1–11.2), "Disposições Finais" (15: 14.1–14.3) —, 15 parágrafos ao todo, nenhum para "Disposições Preliminares" e "Requisitos Gerais"; cada trecho de cada parágrafo acusado aparece literalmente no texto cru da seção, para que a busca no campo o encontre (`SC-468`, 5 de 5 achados); e sobre `A-conteudo-publicado.json`, nenhum achado desta feature (`SC-464`)
- [ ] T016 [P] [US1] Em `backend/tests/interface/test_numeracao_na_revisao.py` (novo), pelo caminho real (`identificar`, `compor_rascunho` de `tests/interface/conftest.py`, e o formulário da etapa Conteúdo): texto "3.1 A inscrição…" em "Da Inscrição" → o achado aparece no topo da etapa Conteúdo e na Revisão; o link do achado aponta para a etapa Conteúdo com âncora `#titulo-inscricao`; a legenda dessa seção mostra o mesmo número que o achado nomeia (`FR-1212`, `UX-160`); a mensagem não contém código, caminho nem nome de campo (`UX-159`); a página do Edital em elaboração também mostra o achado (`FR-1212`); o texto gravado é o mesmo que foi enviado (`FR-1203`)
- [ ] T017 [US1] Rodar T012 a T016 contra o código da Phase 2: falham por ausência das conferências, e nenhum por outra razão

### Implementação

- [ ] T018 [US1] Em `backend/processo_seletivo/editais/domain/validation.py`, a conferência da numeração digitada (`D-006`, `D-007`, `D-009`): percorre `_secoes_textuais` na ordem do documento, normaliza com `grafia.normalizar`, divide com `pdf._paragrafos`, lê o número da seção por `pdf.numeracao` (importação adiada, como a de `classificacao.domain.faixa`, com o porquê no comentário — `D-004`), e emite um achado por seção: `typed_numbering_conflict` (impeditivo) quando `ato` é publicação, `typed_numbering_conflict_in_retification` (aviso) quando é Retificação; e `typed_numbering_suspected_title` (aviso) nos dois. Mensagem nos termos de [contracts/achados-de-numeracao.md](contracts/achados-de-numeracao.md) §3 e dos *Exemplos de mensagem* da spec. Constantes de código exportadas. Registrar em `validate_for_publication`
- [ ] T019 [US1] Em `backend/processo_seletivo/interface/views.py`, acrescentar os três códigos de numeração a `CODIGOS_DO_TEXTO_DA_SECAO`, e, na montagem das pendências, trocar a âncora do topo da etapa pela da legenda da seção (`#titulo-<chave>`) **só para os códigos desta feature**, lendo a chave pelo identificador da seção no caminho, a partir do snapshot já montado (`D-008`); os códigos que já existiam mantêm `#conteudo-titulo`
- [ ] T020 [US1] Rodar T012 a T016: verdes

**Checkpoint**: o MVP — quem elabora vê o conflito, com o trecho, e chega à seção.

---

## Phase 4: User Story 2 — Quem elabora descobre a remissão que não aponta para um item só (Priority: P1)

**Goal**: a remissão ambígua, a sem destino e a suspeita viram avisos, em todo texto livre impresso,
e nenhuma remissão é dada como correta.

**Independent Test**: no cenário B, "item 8.1" sai ambígua nomeando a Etapa 8.1 e o parágrafo digitado
8.1 (`SC-463`).

### Testes

- [ ] T021 [P] [US2] Em `backend/tests/unit/editais/test_remissoes.py` (novo) — todos os achados de remissão e de suspeita são avisos, e nunca impeditivos (`FR-1211`): remissão a número com dois itens → `cross_reference_ambiguous`, aviso, que nomeia os dois e diz que o sistema não sabe qual foi citado (`FR-1206`, `FR-1216`); sem item → `cross_reference_without_target`, que ensina a explicitar outro ato (`FR-1207`); "Quadro 2" → `cross_reference_suspected` (`FR-1208`); único destino em parágrafo em conflito → `cross_reference_suspected` (`FR-1208`); "item 5" com 5 seções numeradas ou menos → nada, e acima do total → sem destino; "Tabela 3" com três tabelas ou mais → nada, e acima → sem destino; remissão a outro ato ou a Anexo → nada; a mesma remissão duas vezes na mesma seção → um achado
- [ ] T022 [P] [US2] No mesmo arquivo, **nada afirma correção** (`FR-1209`, `SC-467`): remissão a número com exatamente um item coerente → nenhum achado; e nenhuma mensagem de nenhum código desta feature contém "correta", "conferida", "verificada" ou "válida" aplicadas à remissão (varredura sobre os achados de todos os testes do arquivo)
- [ ] T023 [P] [US2] No mesmo arquivo, o **alcance** de `D-003` (`FR-1204`): a remissão sem destino é acusada também nas atribuições e nos requisitos de um Perfil, na instrução de um documento exigido e na descrição de um Evento, com o caminho do campo e o lugar como `_textos_impressos` o descreve; e o cenário B (`SC-463`): sobre `B-conteudo-publicado.json`, exatamente uma remissão ambígua, "item 8.1" em "Dos Recursos", nomeando a Etapa «Prova de títulos…» e o parágrafo 1 da mesma seção
- [ ] T024 [P] [US2] Em `backend/tests/interface/test_numeracao_na_revisao.py`: a remissão ambígua aparece na Revisão junto dos achados de numeração da mesma seção, depois deles (`UX-161`, `D-007`); três remissões repetidas se dobram numa linha que se abre, e o conflito impeditivo nunca se dobra (`D-016`)
- [ ] T025 [US2] Rodar T021 a T024 contra o código da Phase 3: falham por ausência da conferência, e nenhum por outra razão

### Implementação

- [ ] T026 [US2] Em `backend/processo_seletivo/editais/domain/validation.py`, a conferência das remissões (`D-011`): itens do documento = função de T010 + os números de subitem lidos nas seções textuais (coerentes e em conflito, com seção e parágrafo); percorre `_textos_impressos`, lê as remissões, cruza e emite os três códigos de aviso, com a descrição de cada item ("a Etapa «…»", "o Perfil «CÓDIGO — nome»", "a subseção comum de atribuições", "o parágrafo N da seção «…»"); a remissão a um item único coerente não emite nada. Ordem: os achados de remissão de cada seção logo depois dos de numeração dela, e os dos demais campos ao fim (`D-007`). Registrar em `validate_for_publication`
- [ ] T027 [US2] Em `backend/processo_seletivo/interface/views.py`, acrescentar os três códigos de remissão a `CODIGOS_DO_TEXTO_DA_SECAO` (com a âncora por seção de T019 quando o caminho é de seção); em `backend/processo_seletivo/interface/templatetags/interface_extras.py`, os códigos de remissão em `RESUMO_DAS_REPETIDAS` ("{n} avisos de remissão")
- [ ] T028 [US2] Rodar T021 a T024: verdes

**Checkpoint**: numeração e remissões completas na elaboração.

---

## Phase 5: User Story 3 — Quem homologa e quem publica não deixam passar o conflito (Priority: P2)

**Goal**: o conflito impede a submissão e a publicação; os avisos não.

**Independent Test**: o rascunho do cenário B tem a submissão recusada pelos 5 conflitos (`SC-469`).

### Testes

- [ ] T029 [P] [US3] Em `backend/tests/integration/publicacoes/test_numeracao_na_publicacao.py` (novo), pela API administrativa (`levar_a_publicacao` de `tests/fixtures/publicacao.py`, com `draft=` que carrega as seções): rascunho com conflito → submissão `422 blocking_findings`, a mensagem com a seção, os parágrafos e os números (`FR-1210`, `FR-1212`); rascunho só com remissão sem destino → submissão aceita (`SC-469`) — e, **antes de escrever a asserção**, conferir no código da submissão (`submit_edital` e a view da API) se os avisos voltam na resposta de sucesso: voltando, afirmar o aviso nela; não voltando, afirmá-lo pela Revisão do Edital submetido, e registrar a escolha no teste; e a publicação: como o rascunho não muda entre a homologação e a publicação, não há como produzir pela API um conflito que só a publicação veja; o teste prende a regra pela mesma chamada que `publish_edital` faz — `validate_for_publication(snapshot, ato=ATO_DE_PUBLICACAO)` sobre um snapshot com conflito devolve o impeditivo
- [ ] T030 [P] [US3] Em `backend/tests/interface/test_numeracao_na_revisao.py`: pela interface, tentar submeter com conflito → recusa com a mesma mensagem da Revisão; corrigir para o número da seção e salvar → o achado some e a submissão passa (`quickstart.md` §6)
- [ ] T031 [US3] Rodar T029 e T030: verdes sem código novo (a submissão e a publicação já bloqueiam impeditivos); se algum falhar, a correção é no texto da recusa, e não em regra nova

**Checkpoint**: o impeditivo vale nas portas que já existem.

---

## Phase 6: User Story 4 — O que já foi publicado não muda (Priority: P2)

**Goal**: Edital publicado intocado; Retificação só com avisos, mesmo os que ela cria.

**Independent Test**: a Retificação que esvazia uma seção é publicada, com os conflitos que cria
mostrados como aviso na confirmação (`SC-470`).

### Testes

- [ ] T032 [P] [US4] Em `backend/tests/integration/publicacoes/test_numeracao_na_publicacao.py`: Edital publicado com conflito — gravado antes da regra, montando a Publicação pelo helper com a conferência desligada por `monkeypatch` só no momento de publicar — tem o documento com os mesmos bytes e a página dele na gestão sem achado de numeração (`FR-1218`, `D-013`)
- [ ] T033 [P] [US4] No mesmo arquivo, a Retificação (`FR-1213`, `D-002`, `SC-470`): sobre um Edital publicado sem conflito, uma Retificação que esvazia uma seção textual anterior a seções com subitens → `advertencias_do_ato` devolve `typed_numbering_conflict_in_retification` (o código **não** é subtraído, `D-006`), a tela de confirmação da Retificação o mostra, e `publish_retification` publica; uma Retificação sobre Edital que já tinha conflito também publica, com o aviso
- [ ] T034 [P] [US4] Em `backend/tests/unit/editais/test_avisos_do_documento_oficial.py`, estender `test_os_codigos_novos_nao_coincidem_com_impeditivo_nenhum` (ou um teste irmão no arquivo novo de T012) para os cinco códigos de aviso desta feature: nenhum coincide com o código de um impeditivo de publicação (contrato G1)
- [ ] T035 [US4] Rodar T032 a T034 contra o código da Phase 4; implementar o que faltar — se a Retificação não receber os achados, conferir que as duas chamadas de `validate_for_publication(ato=ATO_DE_RETIFICACAO)` em `backend/processo_seletivo/publicacoes/application/retificacoes.py` já os trazem (`D-012`), sem mudar a subtração de `advertencias_do_ato`; verdes

**Checkpoint**: imutabilidade e Retificação provadas.

---

## Phase 7: Polish, validação com os PDFs reais e fechamento

- [ ] T036 [P] Bytes do documento (`FR-1219`, `SC-466`): teste em `backend/tests/unit/publicacoes/test_itens_do_documento.py` que renderiza os dois conteúdos congelados com **o contexto do ato de cada cenário** — unidade Cefor e data de 08/10/2026 nos dois; autoridade "Fulana de Tal", cargo de Diretora-Geral do Cefor e ato de nomeação fictício em A; **só o cargo** em B — e compara byte a byte com `doc/auditoria-edital-pdf-2026-10-08/pdf/A-publicado.pdf` e `B-publicado.pdf`; e `tests/contract/test_documento_publicado.py` verde sem fixture refeita
- [ ] T037 Validação com os cenários da auditoria ([quickstart.md](quickstart.md) §1 a §5), registrada em `specs/065-conflitos-de-numeracao/verificacao.md`: B sem correção recusado, com as 5 mensagens copiadas; B corrigido só pelas mensagens publicado (`SC-465`), com o script de conferência dos parágrafos numerados, 44 páginas, diff de texto contra `B-publicado.pdf` só nos números, e as pp. 39–44 renderizadas por CoreGraphics e `pdftoppm` e olhadas; A e A-retificado sem achado; bytes de A e de B iguais aos da auditoria; Retificação que esvazia "Do Atendimento à Pessoa com Deficiência" publicada com aviso. Roteiros novos (B corrigido, Retificação que desloca) em `doc/auditoria-edital-pdf-2026-10-08/cenarios/`
- [ ] T038 Exploratório, sem versionar texto: rodar a conferência sobre o texto dos nove Editais reais da amostra em `~/Downloads` (extraídos por `pdftotext` para o scratchpad, um parágrafo por linha) e revisar à mão cada achado; registrar em `verificacao.md` só as contagens e a classificação (conflito verdadeiro × limitação já escrita), sem trecho de texto real
- [ ] T039 Demonstração pelo canal de quem elabora (Princípio VI, [quickstart.md](quickstart.md) §6): num banco copiado da base, com `INTERFACE_SELETOR_IDENTIDADE=true` e uma entrada **acrescentada** ao `.claude/launch.json` (desfeita no fim com `git checkout -- .claude/launch.json`), escrever "3.1" em "Da Inscrição", ver o achado, seguir o link, ter a submissão recusada, corrigir e ver o achado sumir; captura de tela registrada em `verificacao.md`
- [ ] T040 [P] `specs/065-conflitos-de-numeracao/rastreabilidade.md`: uma linha por `FR-1198` a `FR-1220`, `SC-462` a `SC-470`, `UX-159` a `UX-161`, `D-001` a `D-016` e por **caso-limite** da spec, cada uma com o teste que a prende
- [ ] T041 [P] README: a linha da `065` passa de "(especificada)" ao que foi entregue; e a seção de números da suíte do `AGENTS.md`, se a contagem de pulados ou o total mudarem de natureza (não mudam por teste novo que passa)
- [ ] T042 `cd backend && make lint check test-pg` com `DB_NAME` próprio da worktree (`ruff check` **e** `ruff format --check`); registrar o total em `verificacao.md`
- [ ] T043 Atualizar o *Status* de `spec.md` para "Implementado", e marcar as tarefas

---

## Dependencies & Execution Order

- **Setup (T001–T002)** → **Foundational (T003–T011)** → as histórias.
- **US1 (T012–T020)** depende da Foundational. **US2 (T021–T028)** depende da US1, porque a
  remissão suspeita lê os parágrafos em conflito e a ordem dos achados é por seção.
- **US3 (T029–T031)** e **US4 (T032–T035)** dependem da US2 (os avisos de remissão entram nos testes
  de submissão e de Retificação) e são independentes entre si.
- **Polish (T036–T043)** depois de todas.

## Parallel Opportunities

- T003–T007: cinco testes em quatro arquivos, em paralelo.
- T009 e T010: o módulo puro e a função do compositor, em paralelo.
- Dentro de cada história, os testes marcados [P] em paralelo; as implementações tocam
  `validation.py` e `views.py` e são sequenciais.
- US3 e US4 em paralelo depois da US2.
- T036, T040 e T041 em paralelo no fechamento.

### Exemplo — Foundational

```text
T003 + T004 + T005 + T006  (test_numeracao_digitada.py, um de cada vez no mesmo arquivo, ou em blocos)
T007                        (test_itens_do_documento.py)
T009 ‖ T010                 (numeracao_digitada.py ‖ pdf.py)
```

## Implementation Strategy

- **MVP = US1**: com ela, o defeito do ED-01 — subitem fora da seção — já aparece para quem elabora e
  impede a submissão (o impeditivo nasce em T018, e as portas de submissão e publicação já existem).
- **Incremento 2 = US2**: remissões.
- **Incremento 3 = US3 + US4**: as provas das portas, da Retificação e da imutabilidade.
- **Fechamento**: os cenários reais da auditoria, os bytes e a suíte inteira.
