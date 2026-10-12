# Tasks: A fonte de consulta do Edital vigente (Fase A do assistente de dúvidas)

**Input**: Design documents from `specs/070-fonte-de-consulta-do-edital/`
**Prerequisites**: plan.md, spec.md, research.md (R-001 a R-020), data-model.md,
contracts/resposta.md, contracts/tela.md, quickstart.md

**Tests**: pedidos pela Constituição (V) e pelos cenários de aceitação da spec. Abreviações:

| Sigla | Testes | Onde |
|---|---|---|
| **TU** | unitários, sem banco | `backend/tests/unit/duvidas/` |
| **TI** | integração contra PostgreSQL | `backend/tests/integration/duvidas/` |
| **TT** | tela | `backend/tests/interface/test_duvidas.py` |

Caminhos abreviados:

- **D** = `backend/processo_seletivo/duvidas/`
- **I** = `backend/processo_seletivo/interface/`
- **T** = `backend/tests/`

**Regras de toda tarefa:**

- Português no código, e comentário que explica o porquê.
- **Nenhuma escrita** no banco (`FR-1449`).
- **Nenhuma chamada externa** (`FR-1447`).
- **Nenhuma importação** de `publicacoes.infrastructure.pdf`, `publicacoes.domain.vocabulario_da_regra`
  ou `sorteios.domain.prosa` dentro de D (`R-009`).
- **Nenhum byte de PDF ou anexo** lido do banco (`R-019`).
- As suítes rodam com `TEST_DB_ENGINE=postgresql`, o usuário do banco e `DB_NAME=ps_070`
  (quickstart.md, A).

---

## Phase 1: Setup

- [X] T001 Conferir o ambiente da worktree.
  - `cd backend && uv sync --extra dev`, e `backend/.env` com o `POSTGRES_USER` desta máquina;
  - `manage.py migrate --check`, sem pipe;
  - os guardiões verdes **antes** de mudar qualquer coisa: T`test_gramatica_das_portas.py`,
    T`test_citacoes_de_requisito.py`, T`test_readme_acompanha_o_codigo.py`,
    T`interface/test_acessibilidade.py`, T`interface/test_estaticos.py`,
    T`test_vocabulario_da_composicao.py`, T`migrations/test_migrations.py`;
  - `git worktree list` e `gh pr list`, para medir de novo o teto de FR, SC e UX: a `069` pode ter
    crescido para dentro da faixa da `070`.

---

## Phase 2: Foundational — pacote, corpus, estruturas, origem, catálogo, leitura e a porta da tela

**⚠️ Nenhuma história começa antes desta fase.** É onde mudam os guardiões globais (`R-018`) e
onde se decide, por ensaio, como o corpus entra nos testes de integração (`R-016`).

- [X] T002 Criar o pacote D, com `__init__.py`, `apps.py`, `domain/__init__.py` e
  `application/__init__.py`, sem `models.py` (`R-001`).
  - Registrá-lo em `INSTALLED_APPS` de `backend/config/settings/base.py`, com o comentário do porquê:
    o nome `duvidas` e as recusas de `consulta` e de `assistente`.
  - Acrescentar a linha de `duvidas` à tabela de módulos de `README.md`; T`test_readme_acompanha_o_codigo.py::test_todo_app_aparece_na_tabela_de_modulos`
    a exige.
  - Rodar `manage.py makemigrations --check --dry-run`: nada a gerar.
- [X] T003 [P] Copiar o corpus para T`fixtures/corpus_070/` (`R-016`).
  - Os arquivos: `edital-01-2026/pub{1,2,3}-canonico.json`, `pub{2,3}-alteracoes.json`,
    `edital-91-2026/pub{1,2}-canonico.json`, `pub2-alteracoes.json`,
    `edital-92-2026/pub{1,2}-canonico.json` e `pub2-alteracoes.json`, todos de
    `docs/libras/editais/*/fonte/`.
  - Um `LEIA-ME.md`, com a origem, o commit `a79ce463` e o SHA-256 de cada arquivo.
  - Os PDFs **não** entram.
  - Rodar T`test_sem_dado_pessoal_da_amostra.py`: a varredura alcança fixtures.
- [X] T004 Ensaio do `R-016`, que decide a integração.
  - Em T`fixtures/corpus.py`, `publicar_do_corpus(nome, deslocamento)`:
    1. cria Processo e Edital;
    2. grava o rascunho com `replace_draft` usando o `pub1-canonico.json`, com todas as datas
       deslocadas para o futuro do relógio de teste (perfis, cronograma, etapas, seções, documentos e
       método do sorteio);
    3. grava teto e Requerimento pelos comandos deles;
    4. cria os anexos com `tests.fixtures.anexos.criar_anexo`, pelo rótulo e pela ordem;
    5. publica pelos comandos de aplicação, como `doc/auditoria-edital-pdf-2026-10-08/cenarios/comum.py`;
    6. aplica cada `pubN-alteracoes.json` como Retificação, com a vigência deslocada pelo mesmo
       intervalo.
  - TI em T`integration/duvidas/test_corpus_pelo_fluxo_real.py`: para os três Editais, o conteúdo da
    versão vigente é igual ao do corpus, **exceto** datas deslocadas, identificadores de anexo e hashes.
  - **Se falhar**: registrar a causa no `R-016` de research.md e aplicar o plano B, com Editais
    mínimos por caso de integração. As tarefas TI abaixo dizem a variante de cada uma.
- [X] T005 [P] D`domain/estruturas.py`: as dataclasses congeladas do data-model §2 (`Consulta`,
  `VersaoConsultada`, `Resposta`, `Referencia`, `Origem`, `ValorFuturo`, `MudancaDeVersao`, `Aviso`,
  `SituacaoDeCalendario`, `Canal`, `PontoParaRevisao`).
  - Os enumerados de natureza, tipo, aviso e ponto, com os nomes de contracts/resposta.md.
  - `como_dict()` determinístico, na forma de contracts/resposta.md §6.
  - TU em T`unit/duvidas/test_estruturas.py`: a ordem das chaves é fixa; `Referencia` de natureza
    `EXPLICACAO` não aceita origem; `TEXTO` e `DADO` exigem ao menos uma.
- [X] T006 [P] D`domain/origem.py`: `origens(caminho, proveniencias, atos)` (`R-004`).
  - Fica o ancestral ou o próprio caminho; vence o último ato pela ordem `(effective_at,
    publication_order)`; sem registro, vale a original.
  - Para valor composto com descendentes alterados por atos diferentes, uma origem por valor.
  - TU em T`unit/duvidas/test_origem.py`:
    - caminho sem proveniência;
    - proveniência no próprio caminho;
    - em ancestral;
    - Perfil substituído inteiro **depois** de outra Retificação mudar um campo dele — vence a
      substituição;
    - descendentes por atos diferentes;
    - ordem de vigência diferente da de publicação.
- [X] T007 [P] D`domain/leitura.py`: do conteúdo às referências `TEXTO` e `DADO`, por caminho da
  `004` (`R-010`).
  - O texto é o valor de `resolve_path`, sem `strip`; o parágrafo é a linha de `\n`.
  - A localização é dita pelo título, pelo Perfil, pelo Evento, pelo documento ou pela modalidade;
    nunca por número impresso (`FR-1431`).
  - O dado leva o rótulo de domínio e a forma legível, por `publicacoes.infrastructure.humano`, na
    zona institucional (`FR-1435`).
  - Tolerância a esquema anterior: campo ausente é "não informado", e o conteúdo não é convertido
    (`FR-1416`).
  - TU em T`unit/duvidas/test_literal.py` (`SC-534`): sobre os seis conteúdos do corpus, toda
    referência `TEXTO` é idêntica a `resolve_path(conteudo, caminho)` ou à linha dele.
- [X] T008 [P] D`domain/catalogo.py`: o catálogo `P-01` a `P-12` da `FR-1417`.
  - A condição de oferta de cada pergunta.
  - Os parâmetros (`FR-1418`): Perfil; para a `P-05`, "sem modalidade" mais as modalidades do Perfil
    (`R-008`).
  - A tabela de pertinência da `D-007`, separando "trata do assunto" de "acompanha"
    (contracts/resposta.md §1).
  - TU em T`unit/duvidas/test_catalogo.py`: as perguntas oferecidas em cada Edital do corpus, com
    contagem esperada. No 01/2026 não há `P-09`; no 91/2026, há.
- [X] T009 [P] Guardião de importação, em T`unit/duvidas/test_importacoes.py` (`R-009`). Por AST,
  nenhum módulo de D importa:
  - `publicacoes.infrastructure.pdf`;
  - `publicacoes.domain.vocabulario_da_regra`;
  - `sorteios.domain.prosa`;
  - qualquer módulo de `portal`.

  O teste prova que enxerga, com um módulo sintético que importa.
- [X] T010 D`application/consultar.py`: `consultar(*, edital_id, instante, pergunta, parametros,
  versao_anterior=None)` e `pontos_para_revisao(*, edital_id, instante)` (`R-017`), por enquanto só
  com a leitura.
  1. o Edital;
  2. `effective_version(at=instante)` uma vez, com proveniências;
  3. as versões futuras;
  4. as publicações aplicadas, com Retificação, por `.only()`. Na mesma consulta, a publicação de
     origem da versão traz `retificacao__base_snapshot` com `.only("applied_publications")`, e
     nunca o `content` da base (`R-005`, data-model §1);
  5. o desfecho (`R-003`, `R-019`).

  A leitura dos documentos por identificador, que era o passo 5, saiu na implementação: a
  publicação já traz o que o cartão precisa (verificacao.md §4).

  `no_effective_version` vira estado "sem versão vigente". O contexto vai ao domínio já resolvido.
  Nenhum `request`, sessão ou setting de tela.
- [X] T011 TI em T`integration/duvidas/test_orcamento_da_consulta.py`.
  - No máximo oito consultas por resposta (`R-019`, corrigido na implementação).
  - O número não cresce de um para três Perfis, nem de uma para duas Retificações.
  - Na revisão de código de 12/10, o teste passou a prender os números exatos — cinco fixas, mais
    uma por condição —, porque o teto com folga deixava passar uma consulta por Retificação.
  - Nenhuma consulta seleciona `bytes`.
- [X] T012 TI em T`integration/duvidas/test_fronteira_de_leitura.py`, no padrão de
  T`portal/test_fronteira_publica.py`. Durante `consultar`, nenhuma consulta toca tabela de:
  - `inscricoes`, `divulgacao`, `resultados`, `classificacao`, `sorteios`, `convocacao`, `recursos`,
    `requerimentos`, `identidade`;
  - elaboração (`editais_*`);
  - `publicacoes_revisaoedital`, `publicacoes_homologacao` ou `publicacoes_alteracaonormativa` de
    Retificação não publicada (`FR-1412`).
- [X] T013 A porta da tela (`R-018`, contracts/tela.md).
  - Em I`duvidas.py`, a view `respostas_do_assistente` e a rota `editais/<uuid:edital_id>/duvidas/`
    em I`urls.py`. A identidade e o alcance seguem `interface/views.py:3541-3549` (`detalhe`), sem capacidade nova (`D-010`): fora do
    escopo, `Http404`.
  - Em T`test_gramatica_das_portas.py`, acrescentar I`duvidas.py` a `MODULOS_DE_VIEW`, com o
    comentário no idioma do arquivo.
  - Em `specs/033-navegacao-por-capacidade/inventario-das-negativas.md`, uma linha "acrescentada pela
    `070`", classificada como escopo institucional.
  - Rodar T`test_gramatica_das_portas.py` verde.
  - *Feito assim (12/10/2026):* a recusa fora do escopo é o `not_found` do domínio, como nas telas
    dos avisos, e não `Http404`. Por isso **não houve linha nova no inventário da `033`**; o módulo
    entrou em `MODULOS_DE_VIEW` para que uma porta futura não escape.

**Checkpoint**: o pacote existe, o corpus entra nos testes, a consulta lê o que deve em até oito
consultas, e a porta da tela está inventariada.

---

## Phase 3: User Story 1 — A equipe confere a resposta a uma pergunta sugerida, com a versão e as fontes (P1) 🎯 MVP

**Goal**: as doze perguntas respondem pelos dados, com versão, tipo, explicação e cartões de origem
(`FR-1411`, `FR-1417` a `FR-1420`, `FR-1425` a `FR-1438`).

**Independent Test**: o 91/2026 pelo fluxo real; `P-05` para `INF-BJN` com PcD; conferir
documentos, instruções literais, seções pertinentes inteiras, versão e o link de cada cartão para
o documento do ato de origem.

- [X] T014 [P] [US1] D`domain/explicacao.py`: as formas de contracts/resposta.md §4, só com valores
  dos cartões (`FR-1425`). Os textos começam com a revisão do setor pendente (T046).
  - TU em T`unit/duvidas/test_explicacao.py`:
    - todo número e toda data da explicação estão em alguma referência da mesma resposta;
    - nenhuma explicação contém "você pode", "será aceito" ou "Edital completo";
    - nenhuma diz "não cabe", "não há" ou "não é permitido" sem negativa declarada (`FR-1422`).
- [X] T015 [US1] D`domain/respostas.py`: uma função por pergunta, com o caminho "Respondida pelos
  dados" e as referências na ordem da tabela de pertinência.
  - `P-03` segue o `FR-1427` e o `FR-1428`: ampla concorrência pela linha nula; modalidade sem linha
    fora do quadro; Perfil só de reserva.
  - `P-05` usa `aplicabilidade`.
  - `P-07` traz Etapas e marcos em cartões de dado, e desempate com a regra de ausência.
  - `P-09` traz o método do marco ou o comum.
  - `P-12` traz cada documento pelo ato e pelo que contém (contracts/resposta.md §1.1).
  - Todo texto livre de entidade usada vai literal (`FR-1426`), e toda seção pertinente preenchida vai
    inteira (`FR-1420`).
  - A lista literal pedida pela pergunta é dado, e a prosa sobre o assunto é leitura (`R-013`).
  - TU de determinismo em T`unit/duvidas/test_determinismo.py` (`FR-1446`). Para toda pergunta
    aplicável dos seis conteúdos do corpus:
    - duas chamadas com a mesma entrada dão `como_dict()` idêntico;
    - embaralhar a ordem das proveniências e das publicações recebidas pelo domínio não muda a
      resposta. A ordem vem do conteúdo e da tabela da pergunta, nunca da ordem em que o banco
      devolve as linhas.
- [X] T016 [US1] Ligar origem e links às referências, em D`domain/respostas.py` e
  D`application/consultar.py`.
  - Cada referência `TEXTO` e `DADO` recebe `origens` (T006) e o link `public-document` do ato de
    origem (`FR-1437`).
  - Os links da página pública vão para `portal:selecao`, com `#vaga-<id>`, `#cronograma-titulo` ou
    `#documentos-titulo`, e os anexos para `public-anexo` (`FR-1438`).
  - Nenhum link usa `source_publication` da versão como "documento do Edital" (`D-004`).
- [X] T017 [P] [US1] TU da matriz, casos de US1, em T`unit/duvidas/test_matriz_da_auditoria.py`,
  sobre os conteúdos do corpus.
  - **`CA-01`**: `P-03` `INF-BJN` na v2 dá 45 = 33 + 10 + 2.
  - **`CA-03`**: `P-03` `INF-IUN`. A ampla concorrência tem 28, e nenhuma lista aparece com 0.
  - **`CA-04`**: `P-05` com modalidade traz a seção `inscricao` inteira, com o 3º parágrafo.
  - **`CA-05`**: a mesma `P-05` traz `verificacao-autodeclaracao` inteira.
  - **`CA-06`**: 92/2026 PPIQ, PTT e PcD, com os documentos a mais e as instruções literais.
  - **`CA-07`**: 92/2026. O comprovante de residência só no `TP-01`.
  - **`CA-08`**: 92/2026 `P-07`, com os três critérios na ordem e a regra de ausência.
  - **`CA-09`**: 01/2026 v2 `P-07` `DOC-INFO`. O corte fixo em 2 e mais 1 suplente, com 3 vagas, sem
    conciliar.
  - **`CA-16`**: nenhuma localização contém número de seção.

  Cada caso diz no nome o `CA-` que prende.
- [X] T018 [US1] TI em T`integration/duvidas/test_origem_dos_valores.py`, pelo fluxo real (T004) ou
  pelo plano B.
  - **US1, cenário 1**: as vagas do `INF-BJN` vêm da Retificação, e as linhas PPI e PcD, da original.
  - **Os dois cenários do achado**: o cartão da descrição leva ao documento de R1, e o do local, ao de
    R2.
  - Para cada link, o documento do ato contém o valor citado, conferido no `canonical_content` da
    publicação (`SC-535`).
- [X] T019 [US1] Template I`templates/interface/duvidas.html`, na ordem de contracts/tela.md:
  - título e aviso de validação interna (`UX-205`);
  - identificação e instante;
  - formulário `GET` com as perguntas aplicáveis e os seletores nativos;
  - a resposta em região `aria-live`, com versão (`UX-201`), tipo (`UX-202`), explicação rotulada
    (`FR-1436`) e uma `<section class="referencia">` por cartão, com o rótulo da natureza em palavras
    (`UX-200`), a localização, o conteúdo em `<details>` sem truncar, a origem e os links.

  Regras das classes novas em I`templates/interface/base.html`, com `flex-wrap` no `fieldset` das
  perguntas (contracts/tela.md, *Acessibilidade*) e sem `}}` numa linha.
- [X] T020 [US1] Em I`duvidas.py`, montar a consulta a partir de `pergunta`, `perfil` e `modalidade`.
  - Pergunta fora do catálogo ou não aplicável, e parâmetro inexistente, reapresentam o formulário
    com o motivo, em 200 (contracts/tela.md, *Portas e negativas*).
  - Edital sem publicação: "Só Edital publicado tem respostas" (`FR-1413`).
- [X] T021 [US1] O link de entrada em I`templates/interface/detalhe.html`, no bloco dos documentos
  publicados, só com publicação: "Ver as respostas do assistente de dúvidas (validação interna)".
- [X] T022 [P] [US1] TT em T`interface/test_duvidas.py`.
  - Fora do escopo, 404; sem identidade, redireciona.
  - A entrada aparece só com publicação.
  - Os três rótulos em palavras; o `aria-live`; o foco no título da resposta.
  - Nenhum "Edital completo" na página.
  - A pergunta não aplicável é recusada em 200 com motivo.
  - Edital sem publicação mostra a mensagem.
  - Rodar T`interface/test_acessibilidade.py` e T`interface/test_estaticos.py`, e conferir se o
    template entra na lista de T`test_vocabulario_da_composicao.py` (`R-018`).
  - *Conferido (12/10/2026):* o texto fixo da tela não usa "recorte", "geração" nem "faixa", e ela
    não entra na lista. O rótulo de dado da continuação dizia "faixa" e foi reescrito.

**Checkpoint**: US1 sozinha já é o MVP. O setor confere as doze perguntas no caminho "Respondida
pelos dados", com origem e links corretos.

---

## Phase 4: User Story 2 — A resposta é sempre a da versão vigente no instante, e nunca mistura versões (P1)

**Goal**: versão no instante, Retificação futura, mudança de versão, Retificação não publicada,
instante de referência e desfecho (`FR-1410`, `FR-1411`, `FR-1414`, `FR-1415`, `FR-1429`, `FR-1451`).

**Independent Test**: o 01/2026 com a v3 vigente a partir da fronteira; `P-01` antes e depois dela,
com a versão anterior informada.

- [X] T023 [US2] D`domain/respostas.py` e D`application/consultar.py`: o aviso `RETIFICACAO_FUTURA`
  (`R-003`).
  - Para cada referência, o valor é resolvido nas versões futuras.
  - O que diverge vira `ValorFuturo`, com `vigente_desde` e a origem da versão futura.
  - Ato não publicado nunca é antecipado.
- [X] T024 [US2] Mudança de versão (`FR-1415`): com `versao_anterior` diferente da vigente, a
  resposta recebe `MudancaDeVersao`, com os atos de `applied_publications` que separam as duas.
  `versao_anterior` de outro Edital é ignorada.
- [X] T025 [US2] Situação de calendário e desfecho (`R-006`, `R-007`).
  - `periodo_de_inscricoes` e `fase_publica_do_evento` no instante.
  - `desfechos([edital])`, valendo só com `em <= instante`.
  - O aviso `DESFECHO`. O desfecho do Edital prevalece sobre o período (`FR-1429`).
- [X] T026 [US2] Em I`duvidas.py` e no template:
  - o parâmetro `em`, na zona institucional, com o instante sempre exibido e a mensagem de instante
    inválido (`R-020`);
  - o parâmetro `versao`, carregado escondido pelo formulário;
  - o aviso de mudança antes de tudo (`UX-201`);
  - os valores futuros em cada cartão.
- [X] T027 [P] [US2] TU em T`unit/duvidas/test_matriz_da_auditoria.py`, casos de US2, sobre o corpus.
  - **`CA-02`**: 91/2026, `P-01` na v1 e na v2. O término muda, e a versão é dita.
  - **`CA-17`**: 01/2026 em 20/10/2026, com a v2 vigente e a v3 futura. Diz 31/10/2026 e "prorroga
    para 10/11/2026 a partir de 26/10/2026". Em 27/10/2026, sobre a v3, diz 10/11/2026.
  - **`CA-28`**: 91/2026 em 20/10/2026. "Abertas até 04/11/2026, às 23h59", com o instante.
- [X] T028 [US2] TI em T`integration/duvidas/test_versao_no_instante.py`, pelo fluxo real ou plano B.
  - **`CA-17`** pelo banco: o instante antes e depois da fronteira deslocada.
  - **`CA-18`**: publica-se a Retificação entre duas consultas, e vem o aviso com o ato.
  - **`CA-19`**: só a fronteira passa, sem ato novo, e vem o aviso mesmo assim.
  - **`SC-532`**: uma Retificação em elaboração e outra homologada e não publicada, e as respostas não
    mudam.
  - **US2, cenário 5**: Edital sem publicação.
  - **`SC-531` (varredura)**: todas as perguntas aplicáveis × parâmetros × os três Editais × instantes
    antes e depois de cada fronteira; em toda resposta, todo cartão e a explicação estão na mesma
    versão.
  - **`SC-536` e `FR-1447` (na mesma varredura)**: `socket.socket.connect`, `socket.create_connection`
    e `urllib.request.urlopen` substituídos por um dublê que registra e falha. Ao fim, zero chamadas
    registradas. O dublê é provado por um caso que chama `urlopen` de propósito e é registrado.
- [X] T029 [US2] TI em T`integration/duvidas/test_desfecho_no_instante.py`.
  - **`CA-29`**: com o Edital cancelado, `P-01` diz o desfecho e "não está em curso".
  - Com instante anterior ao ato de cancelamento, o desfecho não aparece.
  - O desfecho do Processo é dito como fato e não fecha o período (`Desfecho.do_edital`).
- [X] T030 [P] [US2] TT em T`interface/test_duvidas.py`.
  - `em` inválido consulta no presente, com a mensagem.
  - O aviso de mudança aparece antes da versão.
  - O formulário carrega `versao`.

**Checkpoint**: a resposta é sempre de uma versão só, a certa no instante, e a mudança é dita.

---

## Phase 5: User Story 3 — O que o Edital não diz, diz em texto, ou diz de modos diferentes aparece como tal (P1)

**Goal**: os tipos, os avisos de anexo e de redação, e as negativas certas (`FR-1421` a `FR-1424`,
`FR-1430`).

**Independent Test**: os casos `CA-10`, `CA-11`, `CA-13`, `CA-14` e `CA-15` sobre o corpus.

- [X] T031 [US3] D`domain/respostas.py`: a tabela de decisão de contracts/resposta.md §2 (`R-013`).
  - "Respondida", "Depende da leitura" e "O Edital não informa" por pergunta.
  - Na `P-08`, os Eventos com a raiz `recurs` (`R-014`), e a negativa declarada (`admits: false`) como
    dado.
  - Na `P-05`, o veredito `divergente` dá "Depende da leitura" e o aviso `REDACAO_ALCANCA_MAIS`
    (`R-008`).
- [X] T032 [P] [US3] D`domain/anexos.py` (`R-012`).
  - Pelo vínculo `attachmentId`, e pela citação `\banexo\s+([ivxlcdm]+|\d+)\b` nos textos mostrados,
    comparada ao início do rótulo.
  - O aviso `DETALHE_EM_ANEXO`, com o link `public-anexo`.
  - Citação sem anexo correspondente devolvida para o ponto para revisão (T040).
  - Nada sobre o conteúdo do anexo.
  - TU em T`unit/duvidas/test_anexos.py`:
    - 92/2026, o Anexo IV citado no nome da Etapa e na instrução;
    - 91/2026, o Anexo I na instrução da autodeclaração;
    - uma citação sintética a um "Anexo IX" inexistente;
    - "anexo" sem identificador, que não é citação.
- [X] T033 [P] [US3] TU em T`unit/duvidas/test_matriz_da_auditoria.py`, casos de US3.
  - **`CA-10`**: 01/2026, `P-08` `TEC-LAB`. "Depende da leitura", com o Evento "Resultado final e
    abertura do prazo recursal" inteiro, sem "não cabe", com o canal (spec, US3, cenário 1a, emenda
    de 12/10). E a ausência pura, em conteúdo sintético sem janela, sem seção e sem Evento de
    recurso: "O Edital não informa", sem "não cabe", com o canal.
  - **`CA-11`**: 91/2026, `P-08` `INF-BJN`. "Depende da leitura", com a janela do marco, a seção "Dos
    Recursos" e o Evento de recurso, inteiros e sem escolha.
  - **`CA-12`**: 91/2026, `P-09`. A seção `classificacao` inteira, com "Havendo mais inscritos que
    vagas", e a explicação não afirma o que o sistema fará.
  - **`CA-13`**: 92/2026, `P-07`. O aviso de detalhe no Anexo IV, com o link, e nenhum número de
    pontuação ausente do conteúdo.
  - **`CA-14`**: 01/2026, `P-01`. A descrição do Evento literal, com "isenção de taxa até o 5º dia",
    e a explicação sem taxa.
  - **`CA-15`**: 92/2026 v2, `P-05` PcD. Sem o texto retirado, e sem afirmar que o atendimento acabou.
  - Um marco sintético com `admits: false`, que dá "Respondida pelos dados", com a negativa como dado.
- [X] T034 [P] [US3] TT em T`interface/test_duvidas.py`: o tipo em palavras para cada um dos quatro
  tipos produzidos, e o aviso de anexo com o link.

**Checkpoint**: nenhuma resposta afirma o que o dado não sustenta.

---

## Phase 6: User Story 4 — O canal de atendimento vem do Edital, e as contradições ficam para revisão (P2)

**Goal**: a `P-11` e o canal de todas as respostas que encaminham (`FR-1439` a `FR-1442`).

**Independent Test**: o 91/2026 (um canal, com exclusividade), o 92/2026 (um canal) e um Edital de
teste com dois canais.

- [X] T035 [P] [US4] D`domain/canal.py` (`R-011`).
  - O parágrafo de dúvida pelas raízes depois de `dobrar()`.
  - Os contatos: e-mail, endereço e telefone.
  - A normalização do canal distinto.
  - A exclusividade.
  - A origem `EDITAL` ou `INSTITUCIONAL`, por `settings.PORTAL_ATENDIMENTO`, lido pela aplicação e
    passado ao domínio.
  - TU em T`unit/duvidas/test_canal.py`:
    - 91/2026, um canal com exclusividade;
    - 92/2026, um canal sem exclusividade, e o 11.1 dos recursos fora;
    - 01/2026, institucional;
    - dois e-mails distintos;
    - o mesmo e-mail em dois parágrafos;
    - "Informações Gerais" com endereço do certame, fora;
    - telefone com e sem DDD;
    - sem Edital e sem implantação.
- [X] T036 [US4] Em D`domain/respostas.py`:
  - a `P-11`: "Respondida" com o parágrafo literal, ou "Fontes divergentes" com todos os parágrafos e
    sem escolha (`FR-1440`), ou o canal institucional rotulado (`FR-1441`);
  - o canal nas explicações que encaminham (`FR-1423`, `FR-1422`).
- [X] T037 [P] [US4] TU em T`unit/duvidas/test_matriz_da_auditoria.py`: **`CA-27`** no 91/2026 e no
  92/2026, mais o caso dos dois canais.
- [X] T038 [P] [US4] TT em T`interface/test_duvidas.py`: o rótulo "canal institucional", e não
  "canal do Edital", no Edital sem canal; com `PORTAL_ATENDIMENTO` vazio, "não há canal informado".

**Checkpoint**: o encaminhamento é sempre para o canal certo, e nunca para um escolhido.

---

## Phase 7: User Story 5 — A equipe vê, por Edital, o que precisa ser revisto antes da abertura pública (P2)

**Goal**: os pontos para revisão da versão vigente (`FR-1443`, `FR-1444`).

**Independent Test**: os três Editais do corpus e os dois cenários do achado.

- [X] T039 [P] [US5] D`domain/revisao.py`: `pontos_para_revisao(contexto)`, com os cinco tipos de
  contracts/resposta.md §5.
  - O documento de origem incompleto é calculado pela diferença de conjuntos de atos (`R-005`), e
    recebe da aplicação o `base_snapshot.applied_publications` da Retificação de origem.
  - Nada é gravado (`FR-1444`).
- [X] T040 [US5] Ligar em D`application/consultar.py`, em `pontos_para_revisao(...)`, e mostrar o
  bloco em I`templates/interface/duvidas.html`, separado das respostas (`UX-203`), com "Nenhum ponto
  para revisão." quando vazio.
- [X] T041 [P] [US5] TU em T`unit/duvidas/test_revisao.py`:
  - 91/2026, exclusividade;
  - um Edital com dois canais;
  - um "Anexo IX" citado sem anexo;
  - 01/2026 v2 com a v3 futura, que dá Retificação futura;
  - um Edital sem nenhuma condição.
- [X] T042 [US5] TI em T`integration/duvidas/test_documento_de_origem_incompleto.py`.
  - Os dois cenários do achado acusam `DOCUMENTO_DE_ORIGEM_INCOMPLETO`, com R1 entre os atos
    faltantes.
  - Uma Retificação só não acusa.
  - A `P-12` diz o mesmo.

**Checkpoint**: a prontidão de cada Edital para a abertura pública está visível.

---

## Phase 8: Polish & Cross-Cutting Concerns

- [X] T043 D`domain/cobertura.py` e TU em T`unit/duvidas/test_cobertura.py` (`R-015`).
  - A tabela `COBERTURA`: padrão de caminho → perguntas, ou `EXCLUIDO` com motivo.
  - **Conteúdo**: todo caminho folha dos seis conteúdos do corpus e de uma fixture que preenche todo
    campo opcional está na tabela.
  - **Esquemas**: todo campo dos esquemas declarados em `editais/domain/validation.py` está na tabela.
  - **Versão**: `SCHEMA_VERSION == 17`, com a mensagem que manda classificar o campo novo (`SC-533`).
- [X] T044 [P] Medir o `SC-537`: o tempo de resposta do 92/2026 publicado pelo ajudante de T004,
  vinte consultas por pergunta. Registrar o p95 na verificação (T047), sem teste de tempo na suíte
  (`R-019`).
- [X] T045 Criar `specs/070-fonte-de-consulta-do-edital/rastreabilidade.md`.
  - Uma linha por FR, SC e UX, de `FR-1410` a `FR-1451`, de `SC-530` a `SC-539` e de `UX-200` a
    `UX-205`.
  - Cada linha aponta o lugar no código e o teste que a prende
    (T`test_citacoes_de_requisito.py::test_a_matriz_de_rastreabilidade_cobre_todo_requisito_da_feature`).
- [ ] T046 Revisão com o setor de seleção, **que é do usuário, e não do agente**.
  *Conferência documental feita pelo agente em 12/10 (verificacao.md §7); a manifestação do setor
  continua pendente, e a tarefa fica aberta.*
  - O que se revisa: a tabela de pertinência (`D-007`), as listas de termos de dúvida e de
    exclusividade (`R-011`) e as formas da explicação (contracts/resposta.md §4).
  - O agente prepara o roteiro e registra o resultado em `verificacao.md`.
  - Mudança na `D-007` ou num requisito é emenda da spec, feita antes da implementação final, e não
    ajuste silencioso.
- [X] T047 Criar `specs/070-fonte-de-consulta-do-edital/verificacao.md`.
  - O roteiro B do quickstart.md pela interface do ator, com o `seed_demo` num banco próprio, e
    capturas a 1280 × 900 e a 375 px (Princípio VI, `SC-538`).
  - O p95 de T044.
  - A conferência de que nenhum link se chama "Edital completo".
- [X] T048 `README.md`: a linha da `070` passa de "Só especificada e planejada" para o que foi
  entregue, e a linha do módulo `duvidas` fica conferida.
- [X] T049 `cd backend && make lint check test-pg DB_NAME=ps_070`.
  - `ruff check` **e** `ruff format --check`.
  - Sem editar nada durante a suíte.
  - Registrar passando, pulados e tempo.
  - **Os pulados não mudam.** Esta feature não acrescenta teste que só o PostgreSQL verifica, salvo
    os TI, que rodam lá. Qualquer pulado novo é conferido um a um.
- [X] T050 `AGENTS.md`: os números da suíte medidos em T049, com falhas e pulados juntos, e o tempo.
  Nada mais muda ali: a `070` não cria tabela append-only nem passo de preparação.
- [X] T051 Antes de integrar:
  - `gh pr list` e `git worktree list`;
  - medir de novo o teto de FR, SC e UX em todas as worktrees; se a `069` tiver alcançado a faixa da
    `070`, renumerar antes do merge;
  - se a `069` tiver sido mergeada antes, fazer a revisão de vocabulário da *Compatibilidade com a
    069* da spec;
  - conferir que a linha do inventário da `033` e a de `MODULOS_DE_VIEW` não colidem com outra feature
    integrada.

---

## Dependencies & Execution Order

- **Setup (T001)** → **Foundational (T002–T013)** → as histórias.
- **T004 decide a variante das integrações.** T018, T028, T029 e T042 esperam por ele.
- **US1 (T014–T022)** é a base das outras: o template, a view e as funções por pergunta.
- **US2 (T023–T030)** depende da US1 e é independente da US3, da US4 e da US5.
- **US3 (T031–T034)** depende da US1. T032 pode começar assim que T007 existir.
- **US4 (T035–T038)** depende da US1 pela `P-11` e pelo encaminhamento. T035 pode começar logo depois
  da Foundational.
- **US5 (T039–T042)** depende de T032 (anexo citado inexistente), de T035 (canais) e de T023
  (Retificação futura).
- **Polish (T043–T051)**:
  - T043 depois de todas as perguntas existirem;
  - T046 pode começar em paralelo à US3, com as formas iniciais;
  - T049 depois de T043 a T048 escritos;
  - T050 recebe os números de T049.

Dentro de cada história: domínio → aplicação → view e template → testes de tela. Os TU de domínio
vêm junto da função que testam.

## Parallel Opportunities

- **Foundational**, depois de T002: T003, T005, T006, T007, T008 e T009, um arquivo cada. T010 a T013
  dependem de T005 e T007.
- **US1**: T014 e T017 em paralelo a T015; T022 depois de T019 a T021.
- **US3 × US4**: T032 e T035 são módulos independentes e podem correr juntos.
- **US5**: T039 e T041 em paralelo.
- **Polish**: T044, T045 e T047, menos os números de T049.

```text
# Exemplo — Foundational, depois do pacote criado:
T003 corpus   T005 estruturas   T006 origem   T007 leitura   T008 catálogo   T009 importações
```

## Implementation Strategy

- **MVP = Setup + Foundational + US1.** O setor já confere as doze perguntas com origem e links
  corretos — sem a versão futura, os tipos e o canal.
- **Incremento 2: US2 e US3, que são P1.** A versão certa no instante e os limites ditos como limites.
  É o mínimo para a validação interna ser confiável.
- **Incremento 3: US4 e US5, que são P2.** Canal e prontidão por Edital.
- **Fecho: Polish.** Cobertura, rastreabilidade, verificação pelo ator, suíte completa.

**O que esta lista não faz, por decisão** (spec, *Fases posteriores*):

- nenhuma rota pública;
- nenhum modelo de linguagem;
- nenhuma correção do achado do "Edital completo";
- nenhuma gravação.
