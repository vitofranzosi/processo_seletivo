# Tasks: O agendamento dos participantes da Etapa

**Input**: Design documents from `specs/167-agendamento-da-etapa/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: sim. Cada SC e cada recusa do contrato tem teste, contra PostgreSQL, como em toda feature
deste repositório. Os caminhos são relativos a `backend/`, salvo os de `specs/`.

**Organization**: por **entrega**, cada uma um PR, e dentro dela por história da spec:

| Entrega | Histórias | PR |
|---|---|---|
| **A** — configurar e montar | US1, US2 | o primeiro, empilhado sobre a spec |
| **B** — conferir, publicar e mostrar | US3 | sobre o A |
| **C** — avisar e remarcar | US4, US5 | sobre o B |
| D — orientação *(opcional)* | — | sobre o B |

Cada entrega termina com a jornada dela no navegador e a suíte inteira, uma de cada vez.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode correr em paralelo (arquivos diferentes, sem dependência de tarefa aberta)
- **[Story]**: a história da spec (US1 a US5)

---

# Entrega A — Configurar e montar

## Phase 1: Setup

- [x] T001 Criar o banco de teste próprio da worktree (`DB_NAME=gps_167`), rodar `uv sync --extra dev`, conferir `manage.py migrate --check` limpo e registrar a linha de base de `tests/interface` e `tests/integration` antes de mexer
- [x] T002 Criar o app `processo_seletivo/agendamento/` (`__init__.py`, `apps.py`, `models.py`, `domain/__init__.py`, `application/__init__.py`, `migrations/__init__.py`) e acrescentá-lo a `INSTALLED_APPS` em `config/settings/base.py`, com o comentário de fronteira no tom dos vizinhos: lê `editais`, `comissoes`, `resultados`, `inscricoes`, e nenhum deles o conhece (T-001)
- [x] T003 [P] Acrescentar `"agendamento"` a `APPS` em `tests/migrations/test_migrations.py`, com o comentário do que o app cria (T-022)

---

## Phase 2: Foundational (bloqueia US1 e US2)

- [x] T004 [P] Criar `processo_seletivo/agendamento/domain/nomes.py`: `REMOTA`, `PRESENCIAL`, `FORMAS`; `MANUAL`, `AUTOMATICA`, `ORIGENS`; e os códigos de recusa de `contracts/recusas.md` §1 e §3
- [x] T005 [P] Criar `processo_seletivo/agendamento/domain/horarios.py`: os valores `Configuracao` e `Horario`, `derivar(configuracao)` e `sobras(configuracao)`, com a data e a hora locais em `America/Sao_Paulo` convertidas uma vez em instante, e a ordem `(inicio, banca.ordem)` (T-003, T-004, FR-7203, FR-7206)
- [x] T006 [P] Testes de unidade em `tests/unit/agendamento/test_horarios.py`: os números do teste independente da US1 (32 com 23/11 em duas janelas de 10 + 5 e uma banca; 64 com 24/11), os 16 com duas bancas em 08–12 de 20 + 10, a sobra informada e a não informada (o intervalo final), uma a três bancas, durações e intervalos variados, o instante na zona institucional (SC-2391, FR-7203, FR-7205, FR-7206)
- [x] T007 [P] Criar `processo_seletivo/agendamento/domain/recusas.py` com `Recusa(codigo, frase)` e as frases de `contracts/recusas.md` §1 e §3, e `processo_seletivo/agendamento/domain/configuracao.py::problemas(configuracao, *, periodo)` com os oito casos da FR-7204 e os três de forma, na ordem do contrato; `periodo=None` para a Etapa sem Evento (T-005, T-008)
- [x] T008 [P] Testes de unidade em `tests/unit/agendamento/test_configuracao.py`: cada um dos oito casos recusado com a frase do contrato, a frase literal do cenário 4 da US1 ("A janela 12:00–12:05 não comporta…"), o dia fora do período com a menção à Retificação, o par nomeado na sobreposição e no nome repetido (sem distinção de caixa), a Etapa sem Evento sem `dia_fora_do_periodo`, a configuração válida sem problema (SC-2391, FR-7204, UX-766)
- [x] T009 Criar em `processo_seletivo/agendamento/models.py` `AgendaDaEtapa`, `JanelaDaAgenda`, `BancaDaAgenda` e `Agendamento`, com os campos e as constraints do data-model (`uq_agenda_por_etapa`, `ck_agenda_duracao_positiva`, `ck_agenda_intervalo_nao_negativo`, `uq_janela_inicio`, `ck_janela_inicio_antes_do_fim`, `ck_banca_com_nome`, `uq_banca_nome` com `Lower`, `uq_agendamento_inscricao`, `uq_agendamento_horario`), e gerar `processo_seletivo/agendamento/migrations/0001_agenda_da_etapa.py` (FR-7200, FR-7202, FR-7211, FR-7216)
- [x] T010 Criar `processo_seletivo/agendamento/application/leitura.py`: a agenda da Etapa com janelas e bancas; a Etapa e o Evento vigentes por `etapa_vigente` e `evento_vigente` (T-002); a participação por `participacao_detalhada` (seis valores, T-007), lida uma vez por requisição; os agendamentos com inscrição e banca, com `ORDER BY` completo; e o recorte "sem horário" × "não participa mais", com o motivo de `motivo_de_nao_participar` (FR-7210, FR-7217)
- [x] T011 Em `leitura.py`, o fato "lista ainda aberta" — a Etapa tem Etapa anterior sem Resultado —, pela leitura que `resultados/application/prontidao.py` já usa para não aplicar a habilitação, sem criar outra (T-007, FR-7207, US1 cenário 7)
- [x] T012 Extrair a guarda de `_etapa_para_distribuir` (`processo_seletivo/interface/views.py:6676`) para uma função comum que as views da Distribuição e da agenda chamam: escopo do Edital, base da gestão da comissão, Etapa vigente (T-021, FR-7255)
- [x] T013 [P] Testes de integração em `tests/integration/agendamento/test_leitura.py`: a participação da Etapa é a de `participacao_detalhada`; quem sai por eliminação aparece em "não participa mais" com o motivo; a Etapa acrescentada por Retificação, sem linha em `EtapaAvaliacao`, tem agenda (FR-7201, FR-7210, FR-7217); a agenda de uma Etapa não altera Edital, Etapa nem cronograma (FR-7200)

**Checkpoint**: o domínio deriva, valida e lê; o banco guarda as duas unicidades.

---

## Phase 3: User Story 1 — A comissão configura a agenda e vê se cabe todo mundo (P1) 🎯 MVP

**Goal**: configurar a agenda de uma Etapa e ver a capacidade enquanto digita.

**Independent Test**: numa Etapa com 43 participantes e período de 23 a 25/11, configurar 23/11 com
08:00–12:00 e 13:00–17:00, 10 + 5 e uma banca mostra 32 e "faltam 11"; acrescentar 24/11 mostra 64 e
"cabem as 43".

### Tests for User Story 1

- [x] T014 [P] [US1] Testes de unidade em `tests/unit/agendamento/test_capacidade.py`: o veredito "Faltam 11 horários para as 43 pessoas" e "Cabem todas as 43 pessoas. Sobram 21 horários."; a conta "16 atendimentos por banca × 1 banca" por janela e dia; o ganho de cada atalho (+32 pelo dia, +32 pela banca, +16 sem o intervalo; com duas bancas, +16, +8, +8) e o destaque no que resolve sozinho (FR-7205, UX-760)
- [x] T015 [P] [US1] Testes de integração em `tests/integration/agendamento/test_configuracao.py`: salvar grava as três tabelas e sobe a `revision`; configuração recusada não grava nada; a insuficiência não impede salvar; configurar com a Etapa anterior sem Resultado é aceito com a frase de lista aberta; a Etapa sem Evento é aceita; o registro de trilha `agenda.configuracao_salva` sem `acesso` (FR-7204, FR-7205, FR-7207, FR-7256)
- [x] T016 [P] [US1] Testes de interface em `tests/interface/test_agenda_da_etapa_configurar.py`: a seção "Agenda" vazia na Distribuição diz para que serve e que pode ser configurada antes de a lista fechar (UX-765, US1 cenário 1); o fragmento `capacidade` responde ao formulário sem gravar e devolve 200 com `HX-Retarget` na recusa (UX-760); os atalhos devolvem o formulário acrescido sem gravar; a recusa lista todos os problemas com o que fazer (UX-766); as views negam fora do escopo e sem a base (FR-7255)

### Implementation for User Story 1

- [x] T017 [US1] Criar `processo_seletivo/agendamento/domain/capacidade.py`: `Capacidade` (horários, por janela, participantes, falta, sobra, sobras, lista aberta) e `atalhos(configuracao, participantes, periodo)` com o ganho de cada um, pela mesma `derivar` (T-006)
- [x] T018 [US1] Criar `processo_seletivo/agendamento/application/configurar.py::salvar(*, actor, edital, etapa_id, configuracao, agora)`: `exigir_base_de_comissao`, trava da `AgendaDaEtapa`, `problemas` contra o Evento vigente, gravação das janelas e das bancas com os `id` estáveis, `revision` + 1, e a trilha (T-005, T-009, T-019)
- [x] T019 [US1] Criar `processo_seletivo/interface/agenda_da_etapa.py` com as views `configurar` (GET, POST, `atalho`) e `capacidade` (fragmento), e as rotas de `contracts/telas.md` em `processo_seletivo/interface/urls.py`; uma linha por `Http404` novo em `specs/033-navegacao-por-capacidade/inventario-das-negativas.md`
- [x] T020 [US1] Criar `processo_seletivo/interface/templates/interface/agenda_configurar.html` e `_agenda_capacidade.html` como `configurar.html` do protótipo: controle segmentado da forma, uma linha por dia com os pares de horas e "+ janela", uma linha por banca com o cabeçalho das colunas uma vez, as orientações, e o simulador ao lado (abaixo no estreito) com veredito, medidor, conta numa linha, sobras e atalhos; o botão "Calcular" para quem não tem script (UX-760, UX-766)
- [x] T021 [US1] Acrescentar a seção "Agenda" a `processo_seletivo/interface/templates/interface/distribuicao.html`: o estado vazio de `etapa.html` do protótipo e "Configurar a agenda"; com agenda, o resumo e o caminho para montar (UX-765)
- [x] T022 [P] [US1] Acrescentar a `processo_seletivo/interface/static/interface/gestao/componentes.css` o controle segmentado e o veredito, e criar `processo_seletivo/interface/static/interface/telas/agenda-da-etapa.css` com a linha de dia, as janelas compactas e o simulador, só com os tokens de `shared/tokens.css`; toda classe citada com regra na folha, nada de `}}` nem `%}` na folha (UX-767, 04-redesign §4.2)

**Checkpoint**: a US1 funciona sozinha: configurar, ver a capacidade, salvar.

---

## Phase 4: User Story 2 — A comissão monta a agenda sem planilha (P1)

**Goal**: montar a agenda com prévia e preenchimento automático, e ajustar à mão sem arrastar.

**Independent Test**: com 64 horários e 43 participantes, o preenchimento dá horário a todos na ordem
por nome; agendar à mão uma pessoa às 08:15 de 24/11 antes de preencher a mantém ali.

### Tests for User Story 2

- [x] T023 [P] [US2] Testes de unidade em `tests/unit/agendamento/test_preenchimento.py`: a ordem por nome normalizado e protocolo no empate, horários do mais cedo ao mais tarde, bancas lado a lado; 32 recebem e 11 sobram; quem já tem horário não entra e o horário dele não é dado a outra; a distribuição por dia × banca (FR-7213, FR-7214, SC-2392)
- [x] T024 [P] [US2] Testes de integração em `tests/integration/agendamento/test_montagem.py`: agendar, mudar de horário (inclusive de dia), liberar; a prévia não grava; a aplicação grava como `AUTOMATICA` com autor e instante; a aplicação com assinatura velha é recusada com a prévia nova, inclusive quando só a participação mudou (T-010, FR-7215); a mesma pessoa com duas inscrições na Etapa (dois Perfis) recebe dois horários, um por inscrição (Edge Cases); salvar uma configuração que remove uma janela devolve as pessoas a "sem horário" e diz quem; agendar quem não participa é recusado; a trilha de cada gesto (FR-7208, FR-7212, FR-7214 a FR-7216, FR-7256, US2 cenários 1 a 7 e 9)
- [x] T025 [P] [US2] Testes de concorrência em `tests/integration/agendamento/test_concorrencia_da_montagem.py`, com duas conexões: dois agendamentos no mesmo horário — um ocupa, o outro recebe `horario_ocupado`; a mesma pessoa em dois horários — um vale; preenchimento simultâneo a um agendamento à mão — nenhuma pessoa com dois horários, nenhum horário com duas (FR-7211, SC-2392, US2 cenário 8)
- [x] T026 [P] [US2] Testes de interface em `tests/interface/test_agenda_da_etapa_montar.py`: um resumo único com o `.medidor`; uma aba por dia com "ocupados/total"; nenhum texto de ação repetido na grade (a célula é o botão); o painel da pessoa e o do horário livre por `hx-get`; a ação principal é "Preencher automaticamente" enquanto há gente sem horário e horário livre, e "Conferir e publicar" depois, sem botão duplicado; o fluxo inteiro só com botões e formulários, sem arrastar (UX-761, UX-762, UX-764)

### Implementation for User Story 2

- [x] T027 [US2] Criar `processo_seletivo/agendamento/domain/preenchimento.py::propor(sem_horario, livres)` com a `Proposta` e a frase da ordem (T-011)
- [x] T028 [US2] Criar `processo_seletivo/agendamento/application/montar.py`: `agendar`, `mudar`, `liberar`, `previa_do_preenchimento` e `aplicar_preenchimento`, sob `exigir_base_de_comissao` e a trava da agenda, com a assinatura de T-010, e a tradução dos dois `IntegrityError` em `atomic()` próprio (T-009, FR-7211 a FR-7216, FR-7215); a recusa `agenda_publicada` só existe na B, com o ato (T057)
- [x] T029 [US2] Em `processo_seletivo/agendamento/application/configurar.py`, a devolução a "sem horário" de quem perdeu o horário na configuração salva antes da publicação, com a lista de quem foi devolvido para a frase da montagem (FR-7208, US2 cenário 9)
- [x] T030 [US2] Acrescentar a `processo_seletivo/interface/agenda_da_etapa.py` as views `montar`, `painel`, `preencher`, `agendar` e `liberar`, e as rotas e linhas de inventário correspondentes
- [x] T031 [US2] Criar `processo_seletivo/interface/templates/interface/agenda_montar.html`, `_agenda_grade.html` e `_agenda_painel.html` como `montar.html` do protótipo: grade horário × banca com linhas de 42 px e a célula como botão, abas por dia, painel `aria-live` com a pessoa (seletor de horário de qualquer dia, "Mudar de horário", "Liberar"), o horário livre (quem está sem horário, com busca), a prévia (veredito, tabela dia × banca, sobras, ordem, relação recolhida) e as listas "Pessoas sem horário" e "Não participa mais" (UX-761, UX-762, FR-7217)
- [x] T032 [P] [US2] Acrescentar a `gestao/componentes.css` o seletor de horário e o painel de ação, e a `telas/agenda-da-etapa.css` a grade compacta e a transformação dela em lista cronológica abaixo de 64rem, com a banca dentro de cada horário, só por CSS sobre a mesma marcação (UX-763, 04-redesign §4.2)

**Checkpoint**: US1 e US2 completas — a entrega A está pronta para demonstrar.

---

## Phase 5: Fechamento da Entrega A

- [x] T033 [P] Criar `tests/interface/test_vocabulario_da_agenda_da_etapa.py` com a lista literal dos templates da A (e acrescentá-la nas entregas seguintes), no molde de `tests/test_vocabulario_da_convocacao.py`
- [x] T034 [P] Testes do estreito em `tests/interface/test_agenda_da_etapa_no_estreito.py`: nenhum `style=`, `<style>`, `<script>` ou `on…=` nos templates novos; toda classe com regra; a regra do estreito dentro do `@media` (SC-2397, UX-767)
- [ ] T035 Jornada no navegador, em 1440 × 900, 1366 × 768 e 375 × 812: configurar o cenário A, resolver a falta pelo atalho, montar, preencher, mover uma pessoa para outro dia; console sem violação de CSP e sem rolagem horizontal no celular; capturas em `specs/167-agendamento-da-etapa/capturas/a/` (SC-2397)
- [ ] T036 `cd backend && make lint check` e a suíte inteira com `DB_NAME=gps_167 make test-pg`, uma de cada vez; atualizar a linha da `167` no README e abrir o PR da A

---

# Entrega B — Conferir, publicar e mostrar

## Phase 6: Foundational da B (bloqueia a US3)

- [ ] T037 Criar em `processo_seletivo/agendamento/models.py` a classe `_AppendOnly` do app e os modelos `AtoDaAgenda` e `HorarioPublicado`, com os campos e as constraints do data-model (`uq_ato_da_agenda_uma_publicacao` parcial, `ck_ato_da_agenda_motivo`, `ck_ato_da_agenda_veiculo`, `ck_ato_da_agenda_signatario`, `uq_horario_publicado_por_ato`, `uq_horario_publicado_substituido_uma_vez`, `uq_horario_publicado_aviso`, `ck_horario_publicado_forma`); `HorarioPublicado.aviso` já existe na B, sempre nulo até a C (FR-7224, FR-7241)
- [ ] T038 Escrever `processo_seletivo/agendamento/migrations/0002_atos_da_agenda.py` com o SQL dos gatilhos `ato_da_agenda_append_only`, `horario_publicado_append_only` e `horario_publicado_coerente` (data-model), por `RunPython` só em PostgreSQL, como `convocacao/migrations/0007_publicacao_de_convocados.py` (T-022)
- [ ] T039 Acrescentar as duas tabelas a `TABELAS_APPEND_ONLY` em `processo_seletivo/seguranca/papeis.py` (61 → 63), `TRIGGERS_POR_APP["agendamento"]` em `tests/migrations/test_migrations.py`, e o `M` novo no `CLAUDE.md` ("eram **61** … são **63** com os atos da agenda da `167`") (T-022)
- [ ] T040 [P] Testes em `tests/integration/agendamento/test_atos_imutaveis.py`: `UPDATE` e `DELETE` recusados pelo gatilho nas duas tabelas e pela falta de privilégio da role de runtime; `save` de linha existente e `delete` recusados pela classe; o gatilho de coerência recusa `substitui` de outra inscrição ou outra agenda, `banca` de outra agenda e `CANCELADO` fora de ato de cancelamento (FR-7224, FR-7241)
- [ ] T041 [P] Criar `processo_seletivo/agendamento/domain/conteudo.py::compor(...)` com o formato de T-014: `NOME_E_PROTOCOLO`, ou `PROTOCOLO` quando `editais.domain.alcance.restrita(etapa)`; banca por horário só com mais de uma; local só na forma presencial; nada de sala, CPF, e-mail, telefone, Modalidade ou desfecho (FR-7225, FR-7226, `D-009`)
- [ ] T042 [P] Testes de unidade em `tests/unit/agendamento/test_conteudo.py`: as duas identificações; a banca com uma e com duas; o local presencial e o vazio remoto; para as fixtures, nenhum endereço de sala, CPF inteiro ou parcial, e-mail, telefone ou código de Modalidade nos `canonical_bytes` (SC-2394, FR-7225, FR-7226)

---

## Phase 7: User Story 3 — A comissão confere e publica, e cada pessoa vê o próprio horário (P1)

**Goal**: conferir sem efeito, publicar como ato imutável com veículo e autoridade, e mostrar o horário
na página pública e na área do candidato.

**Independent Test**: com as 43 pessoas agendadas, publicar, encontrar o horário de uma pessoa pelo
protocolo na página pública, e ver na área dela o dia, a hora, a banca, a sala e as orientações.

### Tests for User Story 3

- [ ] T043 [P] [US3] Testes de integração em `tests/integration/agendamento/test_conferencia.py`: a conferência não grava, não envia e não reserva chave (contar linhas e `IdempotencyRecord` antes e depois); cada impedimento — pessoa sem horário (com a lista), agendada que não participa, configuração recusada contra o Evento retificado, banca sem local ou sala, nenhuma autoridade vigente — nomeado e com o caminho; a Etapa sem Evento só com aviso; o caso completo sem impedimento (FR-7220, FR-7221, FR-7222, SC-2393, US3 cenários 1 a 4)
- [ ] T044 [P] [US3] Testes de integração em `tests/integration/agendamento/test_publicacao.py`: a publicação grava o ato com autor, autoridade congelada, instante, conteúdo e resumo, e um `HorarioPublicado` por pessoa; o veículo `GPS` sem declaração e o `EXTERNO` sem onde ou quando recusados sem gravar; a assinatura velha recusa e refaz a conferência; a confirmação repetida, com a mesma chave e com outra, devolve o mesmo ato (SC-2396); depois, montar não preenche nem libera, e a configuração recusa remover ou mudar o que foi publicado e aceita acrescentar dia, janela ou banca (FR-7208); a trilha `agenda.publicacao` (FR-7223, FR-7224, FR-7240, FR-7256, US3 cenários 5 e 6)
- [ ] T045 [P] [US3] Testes de portal em `tests/portal/test_agenda_publica.py`: a seção "Agendas" na seleção; a agenda por dia; a busca pelo protocolo e pelo nome, e só pelo protocolo na Etapa restrita por Modalidade (`D-009`); o HTML sem endereço de sala, CPF, e-mail, telefone ou Modalidade; sem `<table>`; número fixo de consultas (FR-7225 a FR-7227, SC-2394, US3 cenário 7)
- [ ] T046 [P] [US3] Testes de portal em `tests/portal/test_horario_na_area_do_candidato.py`: publicado, o dia e a hora em destaque, a duração, a banca, o local ou o botão da sala, as orientações; o endereço da sala só para a própria pessoa identificada e nunca para outra inscrição; antes da publicação, "ainda não foi publicado" com o período; número fixo de consultas (FR-7228, FR-7229, US3 cenários 8 e 9)
- [ ] T047 [P] [US3] Testes de interface em `tests/interface/test_agenda_da_etapa_conferir.py`: a moldura da conferência com as quatro linhas de prontidão, a prévia pública igual ao que a página pública mostrará, o assunto e o texto da mensagem, o veículo e a autoridade; o botão "Publicar a agenda e avisar as pessoas"; as views negam fora do escopo (UX-766, FR-7222, FR-7255)

### Implementation for User Story 3

- [ ] T048 [US3] Criar `processo_seletivo/agendamento/application/conferir.py::conferencia(...)`: os impedimentos de `contracts/recusas.md` §4, com `problemas` relido contra o Evento vigente, as autoridades vigentes, os fatos, o conteúdo de `compor`, a mensagem de exemplo e a assinatura (T-010); sem gravar nada (FR-7220 a FR-7222)
- [ ] T049 [US3] Criar `processo_seletivo/agendamento/application/publicar.py::publicar(...)` dentro de `comando_de_comissao`: assinatura, impedimentos, autoridade por `contexto_do_ato`, veículo, `canonical_bytes`/`canonical_sha256`, `AtoDaAgenda` e `HorarioPublicado` em `bulk_create`, `revision` + 1, trilha, e a devolução do ato existente na repetição (T-012, FR-7223, FR-7224)
- [ ] T050 [US3] Criar em `processo_seletivo/agendamento/application/leitura.py` `vigentes_da_agenda(agenda)` (não substituídos e `AGENDADO`, com a marca "remarcado em") e `horarios_da_inscricao(inscricao)`, em número fixo de consultas (data-model, *Vigente*; T-016, T-017; FR-7245)
- [ ] T051 [US3] Acrescentar a `processo_seletivo/interface/agenda_da_etapa.py` as views `conferir`, `publicar` e `publicada` (a lista vigente, "Passou a participar depois da publicação" e "Tem horário e não participa mais"; os avisos ficam para a C), com as rotas, a escolha de autoridade de `_escolha_da_autoridade` e as linhas do inventário
- [ ] T052 [US3] Criar `processo_seletivo/interface/templates/interface/agenda_conferir.html` na moldura de `convocacao_conferir.html` (com `telas/convocacao-conferir.css`), como `conferir.html` do protótipo, com o veículo da `159` (`D-008`), e `agenda_publicada.html` como `publicada.html` (UX-766)
- [ ] T053 [US3] No portal, a rota `agendas/<uuid:agenda_id>/` em `processo_seletivo/portal/urls.py` e a view em `processo_seletivo/portal/views.py`; os templates `portal/agenda_da_etapa.html` (como `publica.html` do protótipo, busca por `GET ?busca=`) e `portal/_agendas_da_selecao.html`, incluído em `portal/selecao.html` ao lado das convocações (T-016, FR-7227)
- [ ] T054 [US3] Na área do candidato, o bloco `portal/_horario_da_inscricao.html` na página `portal:inscricao`, como `candidato.html` do protótipo, com o botão "Entrar na sala virtual" só ali (T-017, FR-7228, FR-7229)
- [ ] T055 [P] [US3] As regras novas do portal em `processo_seletivo/portal/static/portal/portal.css`, sem reusar a classe `.protocolo` (o achado do protótipo) e sem deixar o `display` vencer o `hidden`
- [ ] T056 [US3] Na montagem e na página publicada, o aviso de horário publicado fora do período vigente, quando o Evento foi retificado depois da publicação (Edge Cases)
- [ ] T057 [US3] Depois da publicação: `agendar`, `liberar` e `preencher` em `processo_seletivo/agendamento/application/montar.py` recusam `agenda_publicada`; a montagem publicada fica só de leitura e leva à agenda publicada; e `processo_seletivo/agendamento/application/configurar.py` recusa `horario_publicado_removido` e `parametro_publicado_alterado`, aceitando só acrescentar dia, janela ou banca (T-015, FR-7208, FR-7240)

---

## Phase 8: Fechamento da Entrega B

- [ ] T058 [P] Acrescentar os templates da B a `tests/interface/test_vocabulario_da_agenda_da_etapa.py` e a `tests/portal/test_vocabulario_das_telas_publicas.py`; e a `tests/interface/test_agenda_da_etapa_no_estreito.py` (SC-2397)
- [ ] T059 [P] Testes do que a agenda não faz, em `tests/integration/agendamento/test_fronteira.py`: nenhuma operação da agenda grava `ResultadoEtapa`, `Ocorrencia`, `Avaliacao` ou prazo; as orientações são só texto; nenhum campo de presença (FR-7250, FR-7251, FR-7252)
- [ ] T060 Provisionamento: `make preparar` num banco vazio informa "63 de 63"; `tests/integration/test_database_permissions.py` passa com as duas tabelas novas
- [ ] T061 Jornada no navegador do cenário A até a publicação e do cenário B (duas bancas, Etapa restrita a `PPI`, página pública só com protocolo), em 1440, 1366 e 375 px; capturas em `specs/167-agendamento-da-etapa/capturas/b/` (SC-2397)
- [ ] T062 `make lint check` e a suíte inteira; README (a linha da `167` e o `M`) e o PR da B

---

# Entrega C — Avisar e remarcar

## Phase 9: Foundational da C (bloqueia US4 e US5)

- [ ] T063 Acrescentar `AGENDA` a `processo_seletivo/avisos/domain/nomes.py` e escrever `processo_seletivo/avisos/migrations/0003_origem_agenda.py`: as escolhas, `ck_aviso_origem_conhecida` e `ck_aviso_ato_da_origem` refeitos com o ramo da agenda, `marco_id` anulável e `ck_aviso_marco_da_origem` (T-018, data-model)
- [ ] T064 Revisar a FR-084 em `specs/010-area-do-candidato/spec.md`: **sete** situações, a sétima o aviso de agenda como origem do aviso complementar, sem envio novo, com a frase de que a decisão humana é a confirmação da publicação, da remarcação ou da inclusão; preservar a redação da revisão da `156` como as anteriores foram preservadas (`D-010`, FR-7230)
- [ ] T065 Reler `tests/test_situacoes_de_mensagem.py` no dia, acrescentar o par do despacho para a agenda a `SITUACOES`, a constante `REVISAO_DA_FR_084_PELA_167` em `processo_seletivo/avisos/application/despacho.py` e o teste da revisão, de acordo com o que a `156` já tiver implementado (T-018)
- [ ] T066 [P] Criar `processo_seletivo/agendamento/domain/mensagem.py`: o assunto e o corpo por pessoa — publicação e remarcação, como `email.html` do protótipo: dia, hora, duração, banca quando há mais de uma, local ou endereço da sala, orientações, protocolo, a frase de que vale a agenda publicada, e na remarcação que o horário anterior não vale mais (FR-7231, FR-7244)
- [ ] T067 [P] Testes de unidade em `tests/unit/agendamento/test_mensagem.py`: os campos da FR-7231 nos dois textos; a sala da pessoa e de nenhuma outra (US4 cenário 4); sem CPF, e-mail ou Modalidade

---

## Phase 10: User Story 4 — Cada pessoa recebe um aviso, e a falha não desfaz nada (P2)

**Goal**: um aviso por pessoa por ato, enviado pelo despacho, com as falhas à vista e o reenvio.

**Independent Test**: publicar a agenda de 43 pessoas, rodar o despacho, e ver 43 avisos de origem
"agenda", um por pessoa, cada um citando a publicação.

### Tests for User Story 4

- [ ] T068 [P] [US4] Testes de integração em `tests/integration/agendamento/test_avisos_da_agenda.py`: a publicação cria um `Aviso` e um `DestinatarioDoAviso` por pessoa, ligados ao `HorarioPublicado`; a confirmação não envia; `despachar` envia uma mensagem por pessoa e nenhuma pessoa recebe duas; a confirmação repetida não cria aviso; a falha de envio deixa o ato intacto; com `AVISOS_AOS_CANDIDATOS` desligada, a publicação acontece sem aviso; o reenvio da `066` aceita a origem nova (FR-7230, FR-7232, FR-7233, SC-2395, SC-2396, US4 cenários 1 a 3)
- [ ] T069 [P] [US4] Testes de interface em `tests/interface/test_agenda_da_etapa_publicada.py`: o resumo dos avisos num número só, "na fila", "não entregue" com a pessoa, a frase de que a agenda vale e o caminho do reenvio; com a chave desligada, a frase dos avisos desligados (FR-7233, UX-766)

### Implementation for User Story 4

- [ ] T070 [US4] Em `processo_seletivo/agendamento/application/publicar.py`, criar os avisos em lote na mesma transação, com `perfil_id` da inscrição e `referencia_da_publicacao` do ato, e gravar `HorarioPublicado.aviso`, só com a chave da `066` ligada (T-018, precedente de `avisos/application/pendencias.py:436`)
- [ ] T071 [US4] Em `processo_seletivo/avisos/application/despacho.py` e `confirmar.py`, o estado visual "informacao" da origem nova no correio e o reenvio que a aceita, sem que a `avisos` importe a `agendamento`
- [ ] T072 [US4] Em `agenda_publicada.html` e na view `publicada`, o resumo dos avisos (enviados, na fila, não entregues), lido pelo estado dos destinatários da `066`, e o caminho para o reenvio de cada falha (FR-7233)

---

## Phase 11: User Story 5 — Depois de publicada, só se muda uma pessoa de cada vez (P2)

**Goal**: remarcação, inclusão e cancelamento como atos individuais, com motivo, um aviso só, e o
anterior no histórico.

**Independent Test**: remarcar uma pessoa de 23/11 09:30 para 24/11 14:00 com "falha de conexão
comprovada"; ver um aviso só, o horário novo com "remarcado em" na página pública, e na trilha o
anterior, o novo, o autor e o motivo.

### Tests for User Story 5

- [ ] T073 [P] [US5] Testes de integração em `tests/integration/agendamento/test_atos_individuais.py`: a remarcação cria o ato, o `HorarioPublicado` que substitui o anterior e um aviso só, e atualiza o `Agendamento`; sem motivo recusada com a frase do contrato; a inclusão de quem passou a participar, sem `substitui`; o cancelamento de quem deixou de participar, sem aviso, libera o horário e mantém o publicado; o cancelamento de quem ainda participa recusado; a trilha de cada um, com o motivo e sem e-mail nem sala; o motivo ausente do conteúdo público e da área do candidato (FR-7240 a FR-7244, com a inclusão da FR-7242 e o cancelamento da FR-7243; FR-7246, FR-7256, SC-2395, US5 cenários 2 a 6)
- [ ] T074 [P] [US5] Testes de concorrência em `tests/integration/agendamento/test_concorrencia_dos_atos.py`: duas remarcações para o mesmo horário — só a primeira vale, a segunda recebe `horario_ocupado`; duas remarcações da mesma pessoa — a segunda vê o horário já trocado (FR-7247, US5 cenário 7)
- [ ] T075 [P] [US5] Testes de interface em `tests/interface/test_agenda_da_etapa_remarcar.py`: a montagem publicada sem "Preencher" nem "Liberar", com "Remarcar" por linha; o seletor de horário com "de → para" à vista; sem horário livre, a frase que leva à configuração, onde só se acrescenta (FR-7240, US5 cenários 1 e 8)
- [ ] T076 [P] [US5] Testes de portal em `tests/portal/test_agenda_publica.py` e `test_horario_na_area_do_candidato.py`: o horário novo com "remarcado em" e a data na página pública e na área; "Seu horário mudou" na área; o horário anterior livre (FR-7245, US5 cenário 3)

### Implementation for User Story 5

- [ ] T077 [US5] Criar `processo_seletivo/agendamento/application/atos_individuais.py`: `remarcar`, `incluir` e `cancelar` dentro de `comando_de_comissao`, com a trava da agenda, as recusas de `contracts/recusas.md` §5, o `AtoDaAgenda` com motivo e conteúdo da linha, o `HorarioPublicado` com `substitui`, a atualização do `Agendamento` na mesma transação e o aviso da pessoa (FR-7241 a FR-7244, FR-7247)
- [ ] T078 [US5] Acrescentar a `processo_seletivo/interface/agenda_da_etapa.py` as views `remarcar` (que é também a inclusão) e `cancelar`, com as rotas e o inventário; criar `agenda_remarcar.html` como `remarcar.html` do protótipo e `agenda_cancelar.html` na mesma moldura; "Agendar esta pessoa" e "Cancelar o agendamento" em `agenda_publicada.html`

---

## Phase 12: Fechamento da Entrega C

- [ ] T079 [P] Acrescentar os templates da C à varredura de vocabulário e ao teste do estreito (SC-2397)
- [ ] T080 Jornada no navegador: publicar, `manage.py despachar_avisos` à mão, ver os e-mails no terminal do comando, remarcar com motivo, despachar de novo e ver um e-mail só, no celular; capturas em `specs/167-agendamento-da-etapa/capturas/c/`
- [ ] T081 Escrever `specs/167-agendamento-da-etapa/rastreabilidade.md` com uma linha para cada identificador em negrito da spec — FR-7200 a FR-7256, SC-2390 a SC-2398, UX-760 a UX-767 —, cada uma com a tarefa e o teste; os SC-2390 e SC-2398, humanos, marcados como pendentes de validação
- [ ] T082 `make lint check` e a suíte inteira; README e Visão do Sistema; o PR da C

---

# Entrega D — Orientação *(opcional)*

## Phase 13: Orientação

- [ ] T083 [P] "Montar a agenda" e "Publicar a agenda" como pendência da Etapa com agenda em montagem, em `processo_seletivo/interface/centro.py` (`136`) e `processo_seletivo/interface/atividades.py` (`160`), com testes em `tests/interface/test_agenda_nas_pendencias.py` (T-023)
- [ ] T084 [P] O horário publicado da pessoa, como informação, em `processo_seletivo/interface/templates/interface/ocorrencia.html`, sem nenhum efeito na Ocorrência, com teste em `tests/interface/test_horario_na_ocorrencia.py` (R-23, FR-7250)
- [ ] T085 `make lint check`, a suíte inteira e o PR da D

---

## Dependencies & Execution Order

### Entre entregas

- **A** não depende de nada além da spec. **B** depende da A (o `Agendamento` e a montagem). **C**
  depende da B (o ato e o `HorarioPublicado`). **D** depende da B.
- Cada entrega é um PR empilhado sobre o anterior, e só começa com o anterior verde.

### Dentro de cada entrega

- Setup (T001–T003) → Foundational da A (T004–T013) → US1 (T014–T022) → US2 (T023–T032) → fechamento.
- US2 depende da US1 para ter configuração; os testes de cada história podem ser escritos antes da
  implementação dela.
- Foundational da B (T037–T042) → US3 (T043–T057) → fechamento.
- Foundational da C (T063–T067) → US4 (T068–T072) e US5 (T073–T078), que podem correr em paralelo
  depois de T070, porque a US5 usa a criação de aviso dela.

### Paralelo

- Na fundação da A, T004 a T008 são arquivos de domínio puro e testes independentes: em paralelo.
- Os testes de cada história marcados [P] são arquivos distintos.
- T022 e T032 (folhas) correm ao lado das views.
- Na B, T040 a T042 em paralelo depois de T037–T039.

## Parallel Example: Foundational da A

```text
T005 domain/horarios.py          T006 tests/unit/agendamento/test_horarios.py
T007 domain/configuracao.py      T008 tests/unit/agendamento/test_configuracao.py
T004 domain/nomes.py
```

## Parallel Example: User Story 3

```text
T043 test_conferencia.py   T044 test_publicacao.py   T045 test_agenda_publica.py
T046 test_horario_na_area_do_candidato.py            T047 test_agenda_da_etapa_conferir.py
```

## Implementation Strategy

### MVP

A entrega A (US1 + US2): a comissão sai de uma lista para uma agenda montada, sem planilha e sem
publicar. É o que o pedido mede no SC-2390, até a conferência.

### Incremental

1. **A** → demonstrar configurar e montar → PR.
2. **B** → demonstrar publicar e o candidato encontrar o horário → PR. O `M` vai a 63.
3. **C** → demonstrar avisar e remarcar → PR. A FR-084 revista.
4. **D**, quando a comissão de uso pedir.

### Armadilhas a lembrar em cada sessão

- `make test-pg` com `DB_NAME` próprio; uma suíte de cada vez no cluster.
- `lint` são dois passos.
- Nenhum `style=`, `<style>`, `<script>` ou `onclick=`: a CSP os recusa em silêncio.
- Toda consulta da agenda com `ORDER BY` completo: a limpeza por `DELETE` muda a ordem física.
- O htmx não troca 4xx: recusa de fragmento é 200 com `HX-Retarget`.
- `D-NNN` nos `.md` desta spec só cita decisão desta spec; as de outras se citam pelo assunto.
