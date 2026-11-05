# Tasks: A experiência da convocação, incremento 1 (121)

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md) (R-001 a R-009),
[data-model.md](data-model.md), [contracts/mensagem-da-convocacao.md](contracts/mensagem-da-convocacao.md),
[contracts/acesso-com-destino.md](contracts/acesso-com-destino.md), [quickstart.md](quickstart.md)

**Tests**: pedidos. As SC-1150 a SC-1163 e a SC-1172 são verificadas pela suíte, e a SC-1164 é humana.
Os testes de cada parte vêm antes da implementação dela e devem falhar primeiro. Cada FR, SC e
caso-limite ganha linha em `rastreabilidade.md` (T003).

Caminhos relativos a `backend/`. A suíte roda sempre contra PostgreSQL (`make test-pg`), com
`DB_NAME` próprio da worktree e os grupos `assistente` e `navegador` instalados.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente)
- **[Story]**: US1–US5 da spec

---

## Phase 0: Portão

- [ ] T000 Plano aprovado e mergeado pelo usuário (PR #399). Spec revista na FR-3889, na FR-3891 e na D-009, com a SC-1172. `tests/test_citacoes_de_requisito.py` verde

## Phase 1: Setup

- [ ] T001 Conferências antes do código, registradas em `specs/121-experiencia-da-convocacao/verificacao.md` (novo):
  - (a) as listas literais de templates em `tests/test_vocabulario_da_convocacao.py` (`DA_019`), `tests/test_vocabulario_dos_documentos_da_convocacao.py` (`DA_115`) e `tests/portal/test_vocabulario_das_telas_publicas.py`;
  - (b) o guardião da contagem de migrations por app, da `022` (`grep -rn "0001_initial\|len(migra" tests/`);
  - (c) como `tests/test_javascript.py` descobre `tests/javascript/*.test.js`, e o *shim* de DOM que eles usam;
  - (d) a última migration de `convocacao/migrations/`;
  - (e) se `get_template(...).template.source` existe com o carregador com cache das settings de produção (R-009);
  - (f) os testes que prendem por igualdade o texto de `CORPO`, `COM_PRAZO`, `ASSUNTO` e *"Documento recebido. A comissão vai conferir."* (`grep -rn`)
- [ ] T002 Linha de base: `make lint check test-pg` com os dois grupos opcionais e `DB_NAME` próprio. Anotar totais e pulados em `verificacao.md`
- [ ] T003 [P] `specs/121-experiencia-da-convocacao/rastreabilidade.md` (novo): uma linha por FR-3858–FR-3892, por SC-1150–SC-1164 e pela SC-1172, e por caso-limite da spec, cada uma com o teste que a cobre. A coluna do teste começa vazia e se preenche a cada fase

---

## Phase 2: Foundational — o prazo apresentado (bloqueia US1, US2, US4, US5)

**Goal**: uma função pura dá a data, a hora, o dia da semana e a contagem no fuso das settings, para
o portal e o e-mail (FR-3873 a FR-3875, R-003).
**Independent Test**: `tests/unit/convocacao/test_prazo_apresentado.py`, sem banco.

### Tests

- [ ] T004 [P] `tests/unit/convocacao/test_prazo_apresentado.py`:
  - o dia da semana nos 365 dias de 2027, contra `calendar.weekday`;
  - vencimento às 23h30 locais (02h30 UTC do dia seguinte): a data, o dia e a contagem do dia local;
  - vencimento à meia-noite local: a data, o dia da semana e a contagem do instante no fuso, e não do dia anterior;
  - a contagem às 23h59 e às 00h01 locais, e a uma hora do vencimento, nunca arredondando para cima;
  - *"termina hoje, às HHhMM"*, *"‹dia› · termina amanhã"*, *"‹dia› · faltam N dias"* e vencido sem linha;
  - `HHhMM`, nunca `HH:MM`;
  - o mesmo resultado com `TZ` do processo trocado para `UTC` e `Asia/Tokyo`, com `settings.TIME_ZONE` fixo (SC-1154, SC-1155)
- [ ] T005 [P] `tests/unit/portal/test_obrigacoes_da_convocacao.py`: `data`, `hora` e `ate` de `portal/obrigacoes.py` devolvem o mesmo que antes (o caso de `:640`, *"até 09/11/2026, às 13h27"*), agora pela função nova

### Implementation

- [ ] T006 `processo_seletivo/convocacao/domain/prazo_apresentado.py` (novo): `apresentar(vencimento, agora, fuso)` → valor imutável com `data`, `hora`, `dia_da_semana`, `data_curta`, `contagem`, `vencido`, e a tabela própria dos dias da semana em português (data-model, R-003)
- [ ] T007 `processo_seletivo/portal/obrigacoes.py`: `data`, `hora` e `ate` delegam a `apresentar`, com `ZoneInfo(settings.TIME_ZONE)`. Os chamadores não mudam

**Checkpoint**: T004 e T005 verdes; `tests/unit/portal/` e `tests/interface/test_portal_*` verdes.

---

## Phase 3: US1 — quem abre a convocação entende o que aconteceu e o que fazer (P1) 🎯 MVP

**Goal**: a chamada na ordem da FR-3859, com o título por estado, a etapa, o cartão do prazo, o
resumo, a ação, a consequência, a ressalva e o andamento (FR-3858 a FR-3868).
**Independent Test**: os cenários A, C1, C2, F, G, I1 e J da `118`, pela projeção e pela tela.

### Tests

- [ ] T008 [P] [US1] `tests/unit/portal/test_obrigacoes_da_convocacao.py`, por cenário:
  - `titulo` das quatro linhas da FR-3858;
  - `etapa` das quatro linhas da FR-3860, igual antes e depois de um envio;
  - `ressalva` com e sem o Requerimento (D-003);
  - `andamento` só com obrigatórios, sem o Requerimento e sem frase de conclusão (D-004);
  - `acao`: *"Ver o que preciso fazer"* com a âncora da primeira tarefa da FR-3726 — a pendente em F e J, a primeira a enviar em C1, o Requerimento quando ele é a única;
  - sem tarefa, sem ação;
  - prazo não iniciado (cenário K): título *"Você foi convocado!"*, cartão só com a frase da FR-3749 da `118`, sem contagem;
  - chamada só com documento facultativo: a etapa da FR-3860 e o bloco *O que falta* da `118` (SC-1150, SC-1151)
- [ ] T009 [P] [US1] `tests/interface/test_portal_convocacao.py`:
  - o `h1` por estado, e nenhum `h2` que repita o título no bloco 1 (D-005);
  - a ordem do documento: contexto, título, etapa, cartão do prazo, resumo, ação, consequência e ressalva, andamento;
  - a consequência da FR-1177 uma vez só por estado;
  - o ramo sem documento sem *"Você foi convocada(o)"* e com o cartão do prazo (FR-3868);
  - encerrada pelo prazo, encerrada pelo Processo e com desfecho: o título por estado e os textos do bloco 1 da FR-3741 ou da FR-3742, e **nenhuma** etapa, contagem, ação principal, consequência, ressalva ou andamento (FR-3867);
  - com a chamada aberta, os blocos *O que falta*, *O que você já apresentou* e *Sobre esta convocação* depois do andamento, com o conteúdo da `118` (FR-3866);
  - estado aguardando e não convocado: o título e o texto de hoje, sem a chamada (caso-limite);
  - o caso existente de `:107` reescrito para o texto novo, citando a FR-3868 e a FR-3861
- [ ] T010 [P] [US1] `tests/interface/test_portal_jornada_consolidada.py`: a contagem de consultas da convocação continua a mesma com 1 e com 6 itens (`:679`)

### Implementation

- [ ] T011 [US1] `processo_seletivo/portal/obrigacoes.py`: na projeção, os campos `titulo`, `etapa`, `ressalva`, `andamento` e `acao`. `primeira_ancora` passa a devolver a âncora do Requerimento quando ele é a única tarefa. A chamada deixa de usar `rotulo_do_botao` e `titulo_do_fechamento` como título (plano, seção 1)
- [ ] T012 [US1] `processo_seletivo/portal/templates/portal/_chamada_da_convocacao.html` (novo): contexto curto *"‹Perfil› · Edital ‹NN/AAAA›"*, `h1`, etapa, cartão do prazo (data como maior texto; linha *"‹dia› · ‹contagem›"*; FR-3749 e FR-3737 da `118` nos casos sem linha), resumo, ação, consequência e ressalva
- [ ] T013 [US1] `processo_seletivo/portal/templates/portal/convocacao.html`: o `h1` fixo sai, os dois ramos incluem `_chamada_da_convocacao.html`, e o ramo sem documento perde a frase e a linha do prazo escrita à mão (`:48`, `:54-60`)
- [ ] T014 [US1] `processo_seletivo/portal/templates/portal/_obrigacoes_da_convocacao.html`: bloco 1 sem `h2` de título; a consequência sai do bloco *Prazo* (`:67`); o bloco *Andamento*, com `h2`, entre a chamada e *O que falta*
- [ ] T015 [US1] `processo_seletivo/portal/views.py`, `convocacao`: o Perfil legível (`_perfil_legivel`) e o prazo apresentado no contexto
- [ ] T016 [P] [US1] `processo_seletivo/portal/static/portal/portal.css`: regras para toda classe nova da chamada, do cartão do prazo e do andamento. Nada encolhe em tela estreita (FR-3861)

**Checkpoint**: T008–T010 verdes; as varreduras de vocabulário e de acessibilidade do portal verdes.

---

## Phase 4: US2 — a correção diz qual prazo vale (P1)

**Goal**: a correção no cartão do prazo e a linha *"Convocação substituída"* (FR-3869, R-008).
**Independent Test**: o cenário corr (A comunicada, sucessora B), e as variantes publicação e não
comunicada.

### Tests

- [ ] T017 [P] [US2] `tests/interface/test_portal_convocacao.py`:
  - *"Convocação corrigida: este é o prazo válido."* no cartão, só com a chamada aberta;
  - a linha *"Convocação substituída"* nos três textos da FR-3869 — comunicada, por publicação e não comunicada — em todos os estados;
  - zero ocorrências do motivo, de *"novo prazo"* e de *"prorrogação"*;
  - com A enviada, B falhada e C vigente, a linha descreve **B**, como *"Não comunicada"* (D-008)
- [ ] T018 [P] [US2] `tests/interface/test_portal_jornada_consolidada.py`: a contagem de consultas com 1 e com 6 itens continua igual com a vigente sucedendo outra

### Implementation

- [ ] T019 [US2] `processo_seletivo/convocacao/application/selectors.py`, `vigentes_por_inscricao`: `convocacao_anterior` e as comunicações dela no mesmo *prefetch* (R-008)
- [ ] T020 [US2] `processo_seletivo/portal/obrigacoes.py`: `corrigida` e a linha substituída (texto e datas pelo prazo apresentado), da imediatamente anterior
- [ ] T021 [US2] `_chamada_da_convocacao.html` e `_obrigacoes_da_convocacao.html` (*Sobre esta convocação*): a frase da correção e a linha substituída

**Checkpoint**: T017 e T018 verdes; `tests/navegador/test_jornada_da_correcao_da_convocacao.py` verde.

---

## Phase 5: US3 — o link leva direto à convocação, com ou sem sessão (P1)

**Goal**: sem sessão, o redirecionamento antes de qualquer consulta; o destino por lista fechada e
reconstruído; as telas de acesso dizem para onde a pessoa vai (FR-3876 a FR-3881,
[contracts/acesso-com-destino.md](contracts/acesso-com-destino.md)).
**Independent Test**: os percursos de sessão vencida, primeiro acesso e reconciliação, e os destinos
hostis.

### Tests

- [ ] T022 [P] [US3] `tests/authorization/test_convocacao_alheia.py`:
  - sem sessão, identificador real, inventado e alheio dão o mesmo `302`, para `acesso?destino=<caminho>`, com o mesmo corpo;
  - com `CaptureQueriesContext`, zero consultas às tabelas de `Inscricao`, `Edital` e `Convocacao` antes da resposta, com os nomes lidos de `Modelo._meta.db_table`, e não escritos à mão (o Edital mora em `processos`);
  - só o e-mail na sessão, sem código provado, dá a mesma resposta;
  - a sessão alheia continua com o 404 de inexistente;
  - o caso `:148` reescrito, citando a FR-3876 (SC-1157)
- [ ] T023 [P] [US3] `tests/integration/portal/test_destino_da_convocacao.py` (novo):
  - depois do código, a chegada é a convocação, sem passar pela lista, nos três percursos — sessão vencida, primeiro acesso e reconciliação (SC-1156);
  - outro host, esquema estranho, rota fora da lista, consulta e fragmento acrescentados: a chegada é "Minhas inscrições" ou o caminho reconstruído, nunca o recebido (SC-1158);
  - o POST de envio e o GET do arquivo, sem sessão, respondem como hoje (D-002);
  - destino guardado de outra visita: um destino antigo na sessão leva só à rota que ele nomeia, e a convocação de outra pessoa nele continua recusada como inexistente depois do código (FR-3879, `S4`);
  - pessoa com duas inscrições convocadas: o link de cada uma leva à convocação daquela inscrição, e não à outra nem à lista;
  - abrir a convocação não move prazo e só registra a leitura com sessão titular (FR-3881)
- [ ] T024 [P] [US3] `tests/integration/portal/test_contexto_do_acesso.py`: com destino na convocação, *"Entre para ver a sua convocação"* e *"Depois do código, você vai direto para a convocação."*; o mesmo texto para identificador real, inventado e alheio; nenhum nome de Edital ou de pessoa (FR-3880)
- [ ] T025 [P] [US3] `tests/portal/test_resultados_por_perfil.py`: `_de_volta_a_vaga` com a convocação, ao lado dos casos do Edital e da vaga (`:590`, `:600`)

### Implementation

- [ ] T026 [US3] `processo_seletivo/portal/views.py`, `convocacao`: a primeira linha pergunta `identidade_da_sessao(request)` e, sem identidade, redireciona com `destino` em `urlencode`, antes de `_inscricao_do_titular` (R-004)
- [ ] T027 [US3] `processo_seletivo/portal/views.py`, `_de_volta_a_vaga`: o ramo `portal:convocacao`, que reconstrói pela rota, sem consulta nem fragmento. A docstring passa a dizer que a lista tem três rotas (R-005)
- [ ] T028 [US3] `processo_seletivo/portal/views.py`, `acesso` e `acesso_codigo`: `destino_e_convocacao` pelo nome da rota resolvida (contrato)
- [ ] T029 [P] [US3] `processo_seletivo/portal/templates/portal/acesso_email.html`, `acesso_codigo.html` e `_vaga_do_destino.html`: o título e a frase da FR-3880

**Checkpoint**: T022–T025 verdes; `tests/integration/identidade/` e `tests/acceptance/portal/` verdes.

---

## Phase 6: US4 — a mensagem diz o que a chamada pede, e é reconhecível (P1)

**Goal**: HTML e texto, inicial e da correção. A correção cita a última mensagem enviada com sucesso
(D-008), e a versão do modelo fica gravada na comunicação (D-009, opção A). Ver FR-3882 a FR-3890,
[contracts/mensagem-da-convocacao.md](contracts/mensagem-da-convocacao.md), R-002 e R-009.
**Independent Test**: os envios pelo `locmem` e as cadeias da R-002.

### Tests

- [ ] T030 [P] [US4] `tests/unit/convocacao/test_escolha_da_mensagem.py` (novo): as sete linhas da tabela da R-002 — A→C enviada; **A enviada, B falhada, C cita A**; A e B enviadas, C cita B; **A e B falhadas, C inicial**; A sem comunicação; A por publicação; B falhada e depois enviada. Também as quatro variantes de obrigação da FR-3884, com e sem vencimento, e os itens gravados depois do envio, que não contam (SC-1160)
- [ ] T031 [P] [US4] `tests/unit/convocacao/test_escolha_da_mensagem.py`: `identificacao_do_modelo` é determinística. O mesmo par dá o mesmo valor; trocar um caractere de qualquer arquivo muda o valor; mover um texto do HTML para o texto puro muda o valor; o formato é `<nome>:sha256:<64 hex>` (R-009)
- [ ] T032 [P] [US4] `tests/integration/convocacao/test_mensagem_da_convocacao.py` (novo):
  - as duas partes, com o texto puro contendo cada frase do HTML;
  - zero `src=`, zero endereço fora do link e do canal, zero nome, CPF ou nome de documento da fixture;
  - o assunto e a frase das quatro variantes, e zero `HH:MM`;
  - o link para a convocação da inscrição, absoluto com base e relativo sem ela;
  - a identificação institucional da unidade;
  - a repetição com a mesma chave não envia;
  - todos os documentos obrigatórios aproveitados: a mensagem diz o que a chamada **pede** (*"pede documentos"*), e não o estado (caso-limite) (SC-1155, SC-1159, SC-1161)
- [ ] T033 [P] [US4] No mesmo arquivo, os cenários da D-008 pela gestão de teste, com o *backend* que devolve `0` para provocar a falha:
  1. A enviada, B falhada, C: o assunto e o título da correção, e o quadro com o `enviado_em` e o `vencimento` de A;
  2. A e B falhadas, C: a inicial, sem quadro, sem *"corrigida"*, sem *"Prazo válido"*;
  3. A e B enviadas, C: cita B;
  4. C reenviada depois de falhar: as duas tentativas citam A;
  5. A por publicação, C: a inicial.

  Em todos, *"enviamos"*, e zero *"recebeu"*, *"recebida"*, motivo, *"novo prazo"* e *"prorrogação"* (SC-1160)
- [ ] T034 [P] [US4] No mesmo arquivo, a reconstrução: depois de cada envio de T033, `escolha_da_mensagem` chamada só com os registros relidos do banco devolve o mesmo modelo, a mesma variante e a mesma citada (FR-3889)
- [ ] T035 [P] [US4] `tests/integration/convocacao/test_versao_do_modelo.py` (novo), SC-1172:
  - **gravação**: `ENVIADA`, `FALHA` pelo *backend* e `FALHA` por destinatário ausente gravam `inicial:sha256:…` ou `correcao:sha256:…`, com o nome da escolha. A publicação grava `""`;
  - **correspondência**: o valor gravado é igual ao recalculado, por implementação independente da R-009 no próprio teste, das fontes que o carregador entregou e dos arquivos lidos do disco;
  - **preservação**: com `override_settings(TEMPLATES=…)` e um diretório temporário com cópia alterada do HTML à frente do app, o envio seguinte grava outro valor, e o anterior, relido, não muda;
  - **sem retroatividade**: a linha criada sem a coluna lê `""`;
  - **repetição**: não grava identificação nova
- [ ] T036 [P] [US4] No mesmo arquivo, **recuperável pelo Git**: os quatro arquivos de `convocacao/templates/convocacao/mensagem/` estão no índice (`git ls-files --error-unmatch`) e não são ignorados (`git check-ignore`) (FR-3889)
- [ ] T037 [P] [US4] `tests/unit/convocacao/test_mensagem.py`: os casos `:151` e `:170` passam a esperar `HHhMM`, citando a FR-3875; `tests/interface/test_portal_caminho_da_convocacao.py:221` passa a esperar o link da convocação, citando a FR-1104, revista
- [ ] T038 [P] [US4] `tests/interface/test_correcao_da_convocacao.py`: a prévia da forma individual diz que a mensagem sai de novo com o prazo válido e que corrige a anterior (FR-3890)

### Implementation

- [ ] T039 [US4] `processo_seletivo/convocacao/models.py`: `ComunicacaoEmitida.modelo_da_mensagem = CharField(max_length=100, blank=True, default="")`, com o comentário de por quê (D-009, FR-3889)
- [ ] T040 [US4] `processo_seletivo/convocacao/migrations/00NN_modelo_da_mensagem.py`: só `AddField`, sem `RunPython`. Atualizar o guardião da contagem de migrations (T001(b)). Conferir que `provisionar_papeis` continua `53 de 53` e que `test_database_permissions.py` passa sem mudança
- [ ] T041 [US4] `processo_seletivo/convocacao/domain/mensagem.py` (novo): `escolha_da_mensagem` (R-002, a regra da cadeia da D-008) e `identificacao_do_modelo` (R-009), as duas puras
- [ ] T042 [P] [US4] `processo_seletivo/convocacao/templates/convocacao/mensagem/inicial.html`, `inicial.txt`, `correcao.html` e `correcao.txt` (novos): a ordem da FR-3883, o quadro e o rótulo da FR-3885, a tabela da FR-3884 e o rodapé. Estilo só inline, sem `src=` e sem fonte remota, com a instituição e a unidade vindas do contexto
- [ ] T043 [US4] `processo_seletivo/convocacao/application/comunicar.py`, nesta ordem:
  1. carrega a cadeia;
  2. escolhe a mensagem;
  3. renderiza o par;
  4. calcula a identificação;
  5. confere o destinatário;
  6. envia por `EmailMultiAlternatives`, contando o retorno;
  7. grava a identificação na `ComunicacaoEmitida`, em `ENVIADA` e em `FALHA`.

  `CORPO`, `COM_PRAZO` e `SEM_PRAZO` saem. A reserva da chave e a repetição não mudam (FR-3888)
- [ ] T044 [US4] `processo_seletivo/interface/templates/interface/_correcao_da_convocacao.html`: a frase da prévia (FR-3890)
- [ ] T045 [P] [US4] `tests/test_vocabulario_da_convocacao.py` e `tests/test_vocabulario_dos_documentos_da_convocacao.py`: os quatro modelos e os templates novos do portal nas listas literais (FR-3892)

**Checkpoint**: T030–T038 verdes; `tests/test_situacoes_de_mensagem.py` verde **sem mudança** (SC-1161).

---

## Phase 7: US5 — depois do envio, o que foi recebido e o próximo passo (P2)

**Goal**: a volta em `#confirmacao`, com foco sem script; a recusa no cartão; os três scripts (FR-3870
a FR-3872, R-006, R-007).
**Independent Test**: o envio aceito, o mesmo arquivo de novo e a recusa, pela tela e no navegador.

### Tests

- [ ] T046 [P] [US5] `tests/interface/test_portal_documentos_da_convocacao.py`:
  - o envio aceito redireciona para `#confirmacao`;
  - a confirmação é o primeiro elemento da chamada, com `id="confirmacao" tabindex="-1"`, a frase da FR-3870 com o nome do documento, a data e *"O arquivo aguarda a conferência da comissão."*, e a próxima tarefa ou a conclusão;
  - o mesmo arquivo de novo dá *"Este arquivo já tinha sido recebido."*;
  - a recusa (sem arquivo, não PDF, acima do limite, fora do prazo) redireciona para `#item-<id>`, com `data-recusa` no cartão e sem confirmação;
  - zero *"aceito"*, *"aprovado"*, *"conferido"* e *"atendido"*;
  - cada volta mostra só o seu envio;
  - o caso `:94` reescrito, citando a FR-3870
- [ ] T047 [P] [US5] `tests/javascript/envio.test.js` (novo): com htmx, o percentual como hoje; sem `hx-post`, no `submit`, o `.progresso` aparece e o botão desabilita
- [ ] T048 [P] [US5] `tests/javascript/arquivo.test.js` (novo): escolhido o arquivo, `[data-nome-do-arquivo]` diz o nome, e zero *"Nenhum arquivo escolhido"* (SC-1163)
- [ ] T049 [P] [US5] `tests/interface/test_portal_convocacao.py`: a convocação carrega `arquivo.js`, `envio.js` e `recusa.js` por `{% static %}`, e nenhum outro script; `tests/interface/test_politica_de_conteudo.py` verde

### Implementation

- [ ] T050 [US5] `processo_seletivo/portal/views.py`, `apresentar_documento_da_convocacao`: os registros de sessão `confirmacao_da_convocacao` e `recusa_da_convocacao`, e os dois destinos (plano, seção 4). `_avisar` e `_recusar` saem desta rota
- [ ] T051 [US5] `processo_seletivo/portal/views.py`, `convocacao`: consome os dois registros e monta a confirmação pela projeção depois do envio
- [ ] T052 [US5] `_chamada_da_convocacao.html` e `_cartao_do_documento_da_convocacao.html`: a confirmação em primeiro, e a recusa no cartão com `role="alert" tabindex="-1" data-recusa`
- [ ] T053 [US5] `processo_seletivo/portal/static/portal/envio.js`: o ramo sem htmx (R-007). `convocacao.html` carrega os três scripts no fim

**Checkpoint**: T046–T049 verdes.

---

## Phase 8: Polish e verificação

Os dois achados do plano (a convocação sem `@resposta_privada` e o `_dias_ate`) ficam **fora** do
escopo, registrados só na seção *Registrado, sem desenvolver* do plano.


- [ ] T054 [P] `tests/navegador/test_jornada_da_convocacao_121.py` (novo):
  - a 375 × 812, a ação dentro da primeira tela com folga de uma linha (SC-1152);
  - a 320 px, com a fonte a 150 % e com zoom de 200 %, sem rolagem horizontal (SC-1153);
  - do link ao código à convocação nos três percursos (SC-1156);
  - com o JavaScript desligado, o foco na confirmação; com ele ligado, o foco na recusa (SC-1162);
  - o nome do arquivo escolhido (SC-1163)
- [ ] T055 [P] `tests/navegador/test_jornada_dos_documentos_da_convocacao.py:154`: o heading pelo título por estado, e não mais *"Convocação"*
- [ ] T056 Preencher `rastreabilidade.md` com o teste de cada linha. Nenhuma linha sem teste, salvo a SC-1164, marcada como humana
- [ ] T057 `make lint check test-pg` com os dois grupos, `DB_NAME` próprio, 4 workers. Comparar com a linha de base de T002 por lista de pulados e de falhas, e não por total, e registrar em `verificacao.md`
- [ ] T058 Jornada do [quickstart.md](quickstart.md) no navegador, com capturas a 375 px e a 1280 px em `specs/121-experiencia-da-convocacao/capturas/`, e a conferência de uma comunicação contra o Git pelo roteiro do quickstart
- [ ] T059 `CLAUDE.md`: atualizar as contagens que a migration muda, se alguma estiver escrita. As tabelas append-only continuam 53

---

## Dependencies

- **Phase 0 → Phase 1 → Phase 2**: tudo depende do prazo apresentado (T006, T007).
- **US1** (Phase 3) depende da Phase 2.
- **US2** depende da US1, porque usa `_chamada_da_convocacao.html` (T012).
- **US3** depende só da Phase 2, e pode correr em paralelo com a US1.
- **US4** depende só da Phase 2: a cadeia da mensagem é carregada por `comunicar.py`, e não pelo *prefetch* do portal. Pode correr em paralelo com US1 e US3.
- **US5** depende da US1 (o parcial da chamada) e da projeção com `acao` (T011).
- **Phase 8** depende de todas.

Dentro de cada fase, os testes vêm antes da implementação, e as tarefas `[P]` de teste podem ser
escritas juntas.

## Parallel Example

```text
Depois da Phase 2:
  US1: T008, T009, T010  →  T011 → T012 → T013 → T014 → T015 (+ T016)
  US3: T022, T023, T024, T025  →  T026 → T027 → T028 (+ T029)
  US4: T030, T031, T032, T033, T034, T035, T036, T037, T038  →  T039 → T040 → T041 → T042 → T043 → T044 (+ T045)
```

A US4 não toca `portal/obrigacoes.py`. US1 e US3
tocam `portal/views.py` em funções diferentes, mas o mesmo arquivo, e por isso as duas não rodam em
paralelo na **mesma** worktree sem integração.

## Implementation Strategy

1. **MVP = Phase 2 + US1.** A chamada na ordem nova, com o prazo exato, já responde à pergunta
   central do estudo.
2. **Depois, US4 e US3**: a mensagem que diz o que a chamada pede e leva direto à convocação, com a
   versão gravada.
3. **Depois, US2 e US5**: a correção no portal e a volta do envio.
4. **Phase 8** por último, com a suíte inteira e a jornada no navegador.

Cada fase termina num checkpoint verde, e pode virar commit próprio.
