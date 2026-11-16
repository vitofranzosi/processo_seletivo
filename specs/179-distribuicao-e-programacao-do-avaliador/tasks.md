# Tasks: A distribuição coerente com a agenda e a programação de quem avalia

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/telas.md](contracts/telas.md),
[contracts/validacao.md](contracts/validacao.md), [quickstart.md](quickstart.md)

**Dois incrementos, dois PRs.** O **Incremento 1** (Fases 1 a 6: US1, US2, US3) é a primeira entrega.
O **Incremento 2** (Fases 7 a 10: US4, US5) começa **depois do merge** do primeiro, numa branch nova a
partir da `main`, e não altera nada do que o primeiro entregou: lê a mesma programação.

**Testes**: obrigatórios. O Princípio V exige cobertura de autorização, concorrência e avaliação, e o
plano fixa os casos em `contracts/validacao.md` §4. Em cada história, os testes vêm antes da
implementação e falham primeiro. Cada tarefa cita, entre parênteses, os requisitos que ela realiza
ou verifica.

**Como rodar enquanto trabalha**: só o diretório que a mudança toca, com `DB_NAME` próprio
(`make test-pg DB_NAME=ps_178 PYTEST_ADDOPTS="…"`); a suíte inteira, uma vez, no fechamento de cada
incremento (o `CLAUDE.md`, *Várias sessões rodando a suíte*).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode correr em paralelo (arquivo diferente, sem depender de tarefa incompleta)
- **[Story]**: US1 a US5 da spec
- Caminhos relativos à raiz do repositório

---

# Incremento 1 — distribuição coerente e programação no GPS

## Phase 1: Setup

- [X] T001 Conferir a base: `cd backend && uv sync --extra dev`, `make preparar DB_NAME=ps_178`, `manage.py migrate --check`, e rodar verde, antes de mudar nada, `tests/interface/test_distribuicao.py tests/interface/test_minha_etapa.py tests/interface/test_minhas_atividades.py tests/integration/resultados/test_progressao_no_rodizio.py tests/performance/test_escala_da_mesa.py tests/performance/test_minhas_atividades_em_escala.py tests/interface/test_agenda_da_etapa_publicada.py` com `make test-pg DB_NAME=ps_178`
- [X] T002 Criar o cenário de teste compartilhado "Etapa de entrevista com agenda e comissão" — Edital publicado com prazo encerrado, uma Etapa com agenda de N bancas × D dias, M membros alocados, e helpers `publicar_agenda(...)`, `atribuir(membro, inscricoes)` — em `backend/tests/fixtures/avaliacoes_com_agenda.py`, reaproveitando os helpers das suítes da `167` (`tests/interface/test_agenda_da_etapa_publicada.py`) e da `012`

---

## Phase 2: Foundational (bloqueia US1, US2 e US3)

**Propósito**: o conflito, o horário e a programação, que as três histórias leem (research T-001 a
T-003).

- [X] T003 [P] Testes puros do conflito em `backend/tests/unit/avaliacoes/test_conflito.py`: sobreposição igual, contida, parcial; horários que só se tocam não conflitam; intervalo entre atendimentos fora da conta; dias diferentes; `cabe()`; `passado=True` quando as duas terminaram; ordem determinística da saída (FR-8202)
- [X] T004 [P] Implementar `backend/processo_seletivo/avaliacoes/domain/conflito.py`: `Compromisso` (inicio, fim, inscricao_id, etapa_id, banca_nome), `conflitos(compromissos_por_pessoa, agora)` por varredura ordenada e `cabe(compromissos, inicio, fim)` (research T-003), com docstring no tom do repositório (FR-8202, FR-8203)
- [X] T005 Testes de leitura em `backend/tests/integration/agendamento/test_horarios_do_edital.py`: fonte `MONTAGEM` antes da publicação e `PUBLICADO` depois; remarcação devolve o vigente com `remarcado_em`; cancelado não aparece; duas agendas no mesmo Edital; `so_publicados=True`; quatro consultas fixas com 5 e com 200 agendamentos (FR-8201)
- [X] T006 Implementar `horarios_do_edital(edital, *, so_publicados=False)` e o dataclass `Horario` em `backend/processo_seletivo/agendamento/application/leitura.py` (research T-002), reaproveitando `_vigentes`; `agendamento` continua sem importar `avaliacoes` (FR-8201)
- [X] T007 Testes da aplicação em `backend/tests/integration/avaliacoes/test_programacao.py`: compromissos por `identity_subject` (duas linhas de membro da mesma pessoa somam); conflito entre duas Etapas do mesmo Edital; não entre Editais; programação de uma pessoa numa Etapa só com `PUBLICADO`, agrupada por dia, com as sem horário à parte; `coerencia(edital, etapa_id)` com "menos avaliadores do que a Etapa prevê" e os conflitos; nada gravado; consultas fixas (FR-8200, FR-8202, FR-8203)
- [X] T008 Implementar `backend/processo_seletivo/avaliacoes/application/programacao.py`: `compromissos(edital, subjects=None)`, `programacao(ator, edital, etapa_id)`, `coerencia(edital, etapa_id)`, `proximas(ator)` e `conflitos_no_horario(edital, etapa_id, inscricao_id, inicio, fim)` (research T-003, T-006, T-007, T-009, T-010), sobre `horarios_do_edital` e `conflito.py` (FR-8200, FR-8202)

**Checkpoint**: o conflito e a programação existem e são testados sem tela.

---

## Phase 3: User Story 1 — A comissão distribui uma sessão inteira sem conflito (P1) 🎯 MVP

**Goal**: o lote e o rodízio nunca criam conflito; a comissão atribui "dia × banca" num gesto.

**Independent Test**: 43 pessoas, 3 bancas, 2 dias, 6 avaliadores, dupla avaliação: seis submissões
filtradas distribuem tudo, sem conflito (SC-2841).

### Tests for User Story 1

- [X] T009 [P] [US1] Testes puros do rodízio com agenda em `backend/tests/unit/avaliacoes/test_rodizio_com_agenda.py`: sem `horario`, saída idêntica à de hoje (mesmos pares, mesma assinatura); com agenda, ordem dia–horário–banca; par em conflito inelegível; conflito interno da proposta evitado; motivo "Todas as pessoas selecionadas têm entrevista neste horário"; a simulação 43 × 6 × 3 em dez ordens de protocolo com zero conflito; impedimento, exposição, menor carga e desempate continuam valendo (FR-8207, SC-2842)
- [X] T010 [P] [US1] Testes de integração do lote em `backend/tests/integration/avaliacoes/test_distribuicao_com_agenda.py`: linha em conflito recusada com a frase de `contracts/telas.md` §9 e o resto criado; duas linhas simultâneas no mesmo lote (a mais tarde é recusada); inscrição sem horário aceita; distribuição antes da montagem válida; horários que se tocam aceitos; resultado declarado agrupado; a trilha só com as criadas (FR-8205, FR-8206, FR-8232, UX-971)
- [X] T011 [P] [US1] Teste transacional de concorrência em `backend/tests/integration/avaliacoes/test_distribuicao_concorrente_com_agenda.py`: dois lotes simultâneos dando à mesma pessoa horários que se sobrepõem — uma atribuição vale, a outra é recusada como conflito; usar o padrão de threads dos testes de concorrência da `167` (FR-8205, SC-2840)
- [X] T012 [P] [US1] Testes de tela em `backend/tests/interface/test_distribuicao_por_sessao.py`: filtros `dia` e `banca` só numa Etapa com agenda; coluna Horário; ordem de horário e sem paginação até 200 com os dois filtros; aviso "Horários da agenda em montagem" antes da publicação; o caso de SC-2841 em seis POSTs; sem a base da gestão da comissão, a recusa de hoje com os parâmetros novos (FR-8204, FR-8230, UX-970, SC-2841)

### Implementation for User Story 1

- [X] T013 [US1] Estender `propor(...)` em `backend/processo_seletivo/avaliacoes/domain/rodizio.py` com `horario=None` e `compromissos=None` (research T-005), mantendo menor carga, desempate e `assinar(pares)` intactos; atualizar o docstring do módulo ("a regra do rodízio, dita por extenso") (FR-8207)
- [X] T014 [US1] Em `backend/processo_seletivo/avaliacoes/application/distribuicao.py`: em `_plano_do_rodizio`, ler `horarios_do_edital` e `programacao.compromissos` e passá-los a `propor`; em `distribuir`, depois da trava, o teste `CONFLITO` por par, os compromissos crescendo dentro do lote, e as inscrições percorridas na ordem da agenda (research T-004); a constante da frase ao lado de `EXPOSTO` (FR-8205, FR-8206, FR-8207)
- [X] T015 [US1] Em `backend/processo_seletivo/interface/views.py` (view `distribuicao`) e `backend/processo_seletivo/avaliacoes/application/selectors.py`: parâmetros `dia` e `banca`, a coluna Horário, a ordem e o limite de 200 sem paginação (research T-011); as opções do filtro a partir de `horarios_do_edital` (FR-8204, UX-970)
- [X] T016 [US1] Em `backend/processo_seletivo/interface/templates/interface/distribuicao.html`: os dois campos no formulário de filtros existente, a coluna Horário com a marca textual de conflito (`contracts/telas.md` §1.2), a frase da proposta do rodízio (§1.5); as regras novas na folha comum da gestão (`backend/processo_seletivo/interface/static/interface/gestao/telas.css`), sem estilo no template (FR-8204, UX-976)

**Checkpoint**: US1 testável sozinha; a Distribuição já não cria conflito.

---

## Phase 4: User Story 2 — O avaliador entra no GPS e encontra a própria programação (P1)

**Goal**: a Mesa abre na Programação; Minhas atividades diz a próxima entrevista.

**Independent Test**: com agenda publicada e Atribuições feitas (por qualquer caminho), Ana acha a
próxima entrevista e a programação dos dois dias, sem ver ninguém que não é dela (SC-2843).

### Tests for User Story 2

- [X] T017 [P] [US2] Testes de tela em `backend/tests/interface/test_programacao_na_mesa.py`: Programação como visão padrão só com agenda publicada; agrupada por dia, ordem de início, início e fim, nome e protocolo, banca, botão da sala no remoto e local no presencial, "remarcada em", situação da avaliação; bloco "Sem horário publicado"; antes da publicação, a frase da FR-8212; "Por inscrição" intacta com os filtros; filtros-contagem valendo nas duas (FR-8211, FR-8212, UX-973, SC-2843)
- [X] T018 [P] [US2] Testes de autorização e dados em `backend/tests/interface/test_programacao_na_mesa_acesso.py`: Bruno não vê entrevista nem sala de Ana; sem alocação, a recusa de hoje; resposta privada sem cache; a sala só aparece ao avaliador autenticado e atribuído (FR-8213, FR-8230, FR-8231, `D-006`)
- [X] T019 [P] [US2] Casos novos em `backend/tests/performance/test_escala_da_mesa.py` (a Programação paga o mesmo com 5 e com 500 Atribuições) e em `backend/tests/performance/test_minhas_atividades_em_escala.py` (a próxima entrevista não muda o custo com uma e com onze comissões) (research T-007, T-009)
- [X] T020 [P] [US2] Testes de Minhas atividades em `backend/tests/interface/test_minhas_atividades.py`: "próxima entrevista dd/mm às HH:MM, Banca" na linha da Etapa; ignora as passadas; ausente sem entrevista futura; o link leva à Mesa (FR-8214)

### Implementation for User Story 2

- [X] T021 [US2] Em `backend/processo_seletivo/avaliacoes/application/selectors.py` e na view `minha_etapa` de `backend/processo_seletivo/interface/views.py`: parâmetro `visao`, padrão `programacao` com agenda publicada, a leitura de `programacao.programacao(...)` com uma consulta a mais e fixa (research T-007, T-008) (FR-8211, FR-8212, FR-8213, FR-8231)
- [X] T022 [US2] Em `backend/processo_seletivo/interface/templates/interface/minha_etapa.html`: a escolha Programação / Por inscrição, os blocos por dia como lista (`contracts/telas.md` §5.2), "Hoje" aberto e passados recolhidos, o botão "Entrar na sala" com o endereço no `href`; as regras na folha que a Mesa já carrega — e, se ela não carregar folha de tela, em `backend/processo_seletivo/interface/static/interface/telas/minhas-etapas.css` pelo bloco `estilo_da_pagina` (FR-8211, UX-972, UX-973, UX-976)
- [X] T023 [US2] Em `backend/processo_seletivo/interface/atividades.py` (`linhas_de_avaliacao`) e na view de Minhas atividades: `programacao.proximas(ator)` numa consulta agregada, e o trecho "próxima entrevista …" no `lugar` (research T-009; `contracts/telas.md` §6) (FR-8214)

**Checkpoint**: US2 testável sozinha; o avaliador sai da planilha.

---

## Phase 5: User Story 3 — A comissão vê o que a agenda mudou depois da distribuição (P2)

**Goal**: a agenda pode criar conflito, mas nunca em silêncio (Q-A); a coerência aparece na gestão e
nunca no público.

**Independent Test**: remarcar para um horário em que um avaliador está ocupado: a confirmação o diz,
o POST confere, o conflito aparece na agenda publicada e na Distribuição, e some quando a atribuição
é trocada.

### Tests for User Story 3

- [X] T024 [P] [US3] Testes da remarcação e inclusão em `backend/tests/interface/test_agenda_e_avaliadores.py`: "Avaliam esta pessoa"; marca de ocupado nos horários livres; o item "passa a ter duas entrevistas" no painel Ao confirmar; a remarcação com conflito acontece; Atribuição intacta; a trilha do ato leva os avaliadores em conflito; sem a função injetada, o comportamento da `167` (FR-8209, FR-8232, SC-2845)
- [X] T025 [P] [US3] Teste transacional em `backend/tests/integration/agendamento/test_remarcacao_e_conflitos.py`: uma distribuição entre o GET e o POST da remarcação muda os conflitos → `conflitos_mudaram` (409), sem ato; sem mudança, a remarcação passa (research T-006) (FR-8209)
- [X] T026 [P] [US3] Testes da coerência na gestão em `backend/tests/interface/test_coerencia_na_gestao.py`: coluna Avaliam e "Sem avaliador" na agenda publicada; a linha de coerência com os links filtrados, numa linha só quando em ordem; cartão Agenda da Distribuição; "Quem está alocado" com o conflito; cancelamento tira a pessoa dos conflitos; conferência da agenda com a seção de aviso que não impede a publicação (FR-8208, FR-8210, FR-8215, UX-974, SC-2845)
- [X] T027 [P] [US3] Varredura de exposição em `backend/tests/interface/test_avaliadores_fora_do_publico.py`: com nomes de avaliador semeados, a página pública da agenda, o PDF do ato (texto extraído), a área do candidato e o corpo do aviso de agenda ao candidato não contêm nenhum (FR-8215, SC-2846)

### Implementation for User Story 3

- [X] T028 [US3] Em `backend/processo_seletivo/agendamento/application/atos_individuais.py`: `remarcar` e `incluir` aceitam `assinatura_dos_conflitos` e a função injetada `conflitos_no_horario` (research T-006); chamada dentro da transação, depois de `comando_de_comissao` e da trava da agenda; recusa `conflitos_mudaram` (409) se a assinatura diferir; os avaliadores em conflito no `reason` do evento do ato; sem a função, nada muda; o código e a frase em `backend/processo_seletivo/agendamento/domain/recusas.py` (FR-8209, FR-8232)
- [X] T029 [US3] Em `backend/processo_seletivo/interface/agenda_da_etapa.py` (views `remarcar` e `cancelar`) e `backend/processo_seletivo/interface/templates/interface/agenda_remarcar.html`: "Avaliam esta pessoa", a marca de ocupado no rótulo de cada horário livre, o item do painel Ao confirmar com a frase do Incremento 1, o campo oculto da assinatura, e a injeção de `programacao.conflitos_no_horario` (`contracts/telas.md` §2) (FR-8209, FR-8210)
- [X] T030 [US3] Em `backend/processo_seletivo/agendamento/application/conferir.py` e `backend/processo_seletivo/interface/templates/interface/agenda_conferir.html`: os conflitos como aviso, fora da assinatura da conferência (research T-012); a interface os calcula por `programacao.coerencia` e os passa (FR-8208)
- [X] T031 [US3] Em `backend/processo_seletivo/interface/agenda_da_etapa.py` (view `publicada`) e `backend/processo_seletivo/interface/templates/interface/agenda_publicada.html`: a coluna Avaliam e a seção Avaliadores do Incremento 1 (`contracts/telas.md` §4.1, §4.2 "em ordem" e "com o que resolver"), lidas de `programacao.coerencia` (FR-8208, FR-8215, UX-974)
- [X] T032 [US3] Em `backend/processo_seletivo/interface/templates/interface/distribuicao.html` e na view `distribuicao`: a linha de coerência no cartão Agenda e o conflito em "Quem está alocado" (`contracts/telas.md` §1.4) (FR-8208)

**Checkpoint**: as três histórias do Incremento 1 funcionam juntas e sozinhas.

---

## Phase 6: Fechamento do Incremento 1

- [X] T033 Revisar a FR-085 e a FR-107 em `specs/012-mesa-de-avaliacao/spec.md` e a FR-7229 e a FR-7240 em `specs/167-agendamento-da-etapa/spec.md`, datadas de 2026-11-16 "pela `179`", com a redação anterior preservada em citação (research T-013)
- [X] T034 [P] Rodar e ajustar as varreduras que o texto e as telas novas podem ferir: `tests/interface/test_vocabulario_da_agenda_da_etapa.py` e as listas literais da varredura de vocabulário; `tests/interface/test_acessibilidade*.py` (classe com regra na folha); `tests/interface/test_politica_de_conteudo.py`; `tests/interface/test_larguras.py` e `tests/interface/test_agenda_da_etapa_no_estreito.py`, com casos novos a 375 px para a Distribuição filtrada, a remarcação com conflito, a agenda publicada e a Mesa na Programação; `tests/test_citacoes_de_requisito.py` (SC-2850, UX-976)
- [X] T035 [P] Atualizar a linha da `179` no `README.md` (Incremento 1 implementado) e, se a seção de avaliação for tocada, a Visão do Sistema
- [X] T036 `make lint check` (`ruff check` **e** `ruff format --check`) e a suíte inteira uma vez, `make test-pg DB_NAME=ps_178`; anotar a contagem no PR
- [X] T037 Percorrer o quickstart do Incremento 1 pela tela (cenário C20), com captura da Distribuição filtrada, da Mesa a 375 px e da remarcação com conflito; SC-2844 fica como validação humana, registrada no PR
- [ ] T038 Abrir o PR do Incremento 1; o merge é do usuário

---

# Incremento 2 — o aviso por e-mail ao avaliador

**Começa depois do merge do PR do Incremento 1**, numa branch nova a partir da `main` atualizada.

## Phase 7: Foundational do Incremento 2 (bloqueia US4 e US5)

- [ ] T039 Testes do modelo em `backend/tests/integration/avisos/test_destinatario_membro.py`: `ck_destinatario_inscricao_ou_membro` (os dois, nenhum), `ck_destinatario_resumo_so_do_membro`, `uq_destinatario_membro`, as três constraints da origem `PROGRAMACAO`; as origens de hoje continuam aceitas; append-only nas três camadas (`save`, gatilho, privilégio) (data-model §3)
- [ ] T040 Acrescentar `PROGRAMACAO` em `backend/processo_seletivo/avisos/domain/nomes.py` (`ORIGENS`, `ORIGEM_POR_EXTENSO`) e as mudanças de `backend/processo_seletivo/avisos/models.py` (data-model §3; research T-014) (FR-8227)
- [ ] T041 Escrever `backend/processo_seletivo/avisos/migrations/0005_origem_programacao.py`; conferir aplicar e reverter; atualizar o guardião da contagem de migrations por app (`backend/tests/migrations/test_migrations.py`); conferir que `provisionar` continua com o mesmo `M` (69)
- [ ] T042 Varrer os leitores de `destinatario.inscricao` em `backend/processo_seletivo/avisos/application/` e tratar o nulo ou filtrar `inscricao__isnull=False` em cada um; escrever a guarda `backend/tests/unit/avisos/test_leitores_do_destinatario.py`, no molde de `backend/tests/test_leitores_da_consequencia.py`, que lista os leitores e o que cada um faz com a origem nova (research T-015) (FR-8227)
- [ ] T043 Em `backend/processo_seletivo/avisos/application/despacho.py`: `select_related` com `membro`, ordenação com `nulls_last`, `nome_do_candidato` vazio sem inscrição; testes em `backend/tests/integration/avisos/test_despacho_do_aviso_de_programacao.py` (despacha, retenta, respeita o limite por minuto, registra falha; as origens de hoje inalteradas na mesma fila) (FR-8227)
- [ ] T044 Estender o cenário de treinamento C20 (`backend/processo_seletivo/treinamento/catalogo.py` e `construcao.py`) com a comissão da Entrevista: membros `treino.avaliacao.N` alocados à Etapa, cada um com conta (`User`, senha inutilizável, e-mail de exemplo), no molde da conta da Formalização do C16 e do C17, idempotente e resistente a duas cargas; os atores fora das sugestões da página de acesso; testes no arquivo da suíte de treinamento que já cobre o C20 (research T-020; Princípio VI)

---

## Phase 8: User Story 4 — A comissão avisa os avaliadores quando a programação está pronta (P1)

**Goal**: um gesto, um aviso por avaliador, sem lista, com o link para a Mesa.

**Independent Test**: confirmar o aviso de seis, despachar, ver seis mensagens sem dado de candidato,
cada uma com o link para a Programação (SC-2847, SC-2848).

### Tests for User Story 4

- [ ] T045 [P] [US4] Testes puros da mensagem em `backend/tests/unit/avaliacoes/test_mensagem_da_programacao.py`: assunto e corpo do primeiro aviso e do "mudou"; Edital, Etapa, contagem, primeiro e último dia, bancas, link; sem nome, protocolo, CPF, e-mail ou telefone de candidato, Modalidade nem sala; rodapé comum (FR-8223, SC-2848)
- [ ] T046 [P] [US4] Testes da aplicação em `backend/tests/integration/avaliacoes/test_aviso_da_programacao.py`: destinatários (conta com e-mail; sem conta; sem e-mail; suspensa; subject inventado); estados na ordem do data-model §4; o gesto cria um aviso por pessoa elegível, com o endereço congelado e o resumo; `alcance_mudou` sob a trava; habilitação desligada recusa; sem a permissão de gerir a comissão, recusa no servidor; trilha com contagem e identificadores, sem e-mail (FR-8220, FR-8221, FR-8226, FR-8227, FR-8230, FR-8232)
- [ ] T047 [P] [US4] Testes de tela em `backend/tests/interface/test_avisar_os_avaliadores.py`: a seção Avaliadores nos estados de `contracts/telas.md` §4.2; o botão só com quem avisar, com a contagem; com a habilitação desligada, a frase no lugar do botão; a confirmação (§4.3) mostra alcance, quem fica fora e a mensagem, e não grava; o POST cria; reenvio do não entregue; 375 px; política de conteúdo (FR-8222, FR-8227, FR-8228, UX-975, SC-2850)

### Implementation for User Story 4

- [ ] T048 [P] [US4] Implementar `backend/processo_seletivo/avaliacoes/domain/mensagem_da_programacao.py` (research T-018) (FR-8223)
- [ ] T049 [US4] Implementar `backend/processo_seletivo/avaliacoes/application/aviso_da_programacao.py`: destinatários (research T-016), `resumo` (T-017), estados por avaliador, a assinatura do alcance e `avisar_os_avaliadores(...)` dentro de `comando_de_comissao`, gravando `Aviso` + `DestinatarioDoAviso` (membro, endereço, resumo) e o evento da trilha (T-019) (FR-8220, FR-8221, FR-8224, FR-8226, FR-8228, FR-8232)
- [ ] T050 [US4] Rota `interface:agenda-avisar-avaliadores` (GET confirmação, POST) em `backend/processo_seletivo/interface/urls.py` e `backend/processo_seletivo/interface/agenda_da_etapa.py`; template `backend/processo_seletivo/interface/templates/interface/agenda_avisar_avaliadores.html`; a seção Avaliadores com o gesto e o "Ver por avaliador" em `agenda_publicada.html`; o reenvio de não entregue em `agenda_da_etapa.reenviar`; a frase da remarcação ganha "e ela não recebe o aviso de programação" (FR-8220, FR-8222, FR-8227, FR-8228, UX-975)

**Checkpoint**: o primeiro aviso funciona de ponta a ponta, pela tela, com o C20.

---

## Phase 9: User Story 5 — Quem teve a programação mudada é avisado, e só ele (P2)

**Goal**: "mudou depois do aviso" por comparação de estado; um aviso por gesto.

**Independent Test**: depois do aviso de seis, remarcar uma pessoa avaliada por Ana e Bruno; "Avisar
as mudanças (2)"; duas mensagens, e nenhuma aos outros quatro.

- [ ] T051 [P] [US5] Testes em `backend/tests/integration/avaliacoes/test_aviso_das_mudancas.py`: remarcação, inclusão distribuída, cancelamento e troca de avaliador marcam só os afetados; três mudanças, um aviso; mudança desfeita desfaz a marca; quem entrou em conflito fica fora, nomeado; repetir sem mudança cria zero (FR-8224, FR-8225, SC-2847)
- [ ] T052 [US5] Em `backend/processo_seletivo/avaliacoes/application/aviso_da_programacao.py` e `agenda_publicada.html`: o rótulo "Avisar as mudanças (N)", a variante "Sua programação mudou em dd/mm" e o estado "Mudou depois do aviso de dd/mm"; a frase de sucesso da remarcação dizendo quantas programações de avaliadores mudaram, em `backend/processo_seletivo/interface/agenda_da_etapa.py` (FR-8224, FR-8225, UX-975)

---

## Phase 10: Fechamento do Incremento 2

- [ ] T053 Revisar a FR-084 em `specs/010-area-do-candidato/spec.md` para oito situações, com a redação anterior preservada (texto em *Requisitos de outras features afetados* da spec); `REVISAO_DA_FR_084_PELA_179 = "2026-11-16"` em `backend/processo_seletivo/avisos/application/despacho.py`; o par "o aviso de programação ao avaliador (179)" em `backend/tests/test_situacoes_de_mensagem.py` (FR-8229, SC-2849)
- [ ] T054 [P] Varreduras (vocabulário, acessibilidade, política de conteúdo, larguras, citações) e a linha da `179` no `README.md` (Incremento 2 implementado); a nota do `CLAUDE.md` sobre os avisos, se o despacho ganhar comportamento que alguém precise saber (SC-2850)
- [ ] T055 `make lint check` e a suíte inteira uma vez; quickstart do Incremento 2 pela tela, com o C20 e `despachar_avisos` à mão
- [ ] T056 Abrir o PR do Incremento 2; o merge é do usuário

---

## Dependencies & Execution Order

```text
Incremento 1
  T001–T002 (Setup)
      ↓
  T003–T008 (Foundational: conflito, horários, programação)
      ↓
  ┌───────────────┬───────────────┬───────────────┐
  US1 (T009–T016) US2 (T017–T023) US3 (T024–T032)   ← independentes entre si
  └───────────────┴───────────────┴───────────────┘
      ↓
  T033–T038 (Fechamento, PR 1)  ── merge do usuário ──┐
                                                       ↓
Incremento 2                                  T039–T044 (Foundational)
                                                       ↓
                                              US4 (T045–T050) → US5 (T051–T052)
                                                       ↓
                                              T053–T056 (Fechamento, PR 2)
```

- **US1, US2 e US3** dependem só da Fase 2. Arquivos compartilhados: `distribuicao.html` (T032 depois
  de T016) e `agenda_publicada.html` (T050 depois de T031).
- **US5** depende da US4 (o estado "avisado" precisa existir).
- **Dentro de cada história**: testes → domínio → aplicação → interface.

## Parallel Example: Incremento 1, depois da Fase 2

```text
T009 test_rodizio_com_agenda.py    T017 test_programacao_na_mesa.py      T024 test_agenda_e_avaliadores.py
T010 test_distribuicao_com_agenda  T018 …_acesso.py                      T025 test_remarcacao_e_conflitos.py
T011 …_concorrente_com_agenda      T019 performance (dois arquivos)      T026 test_coerencia_na_gestao.py
T012 test_distribuicao_por_sessao  T020 test_minhas_atividades.py        T027 test_avaliadores_fora_do_publico
```

## Implementation Strategy

1. **MVP = Incremento 1 com a US1 e a US2**: a Distribuição deixa de criar conflito e o avaliador acha
   a programação. A US3 fecha o Incremento 1, porque sem ela a remarcação criaria conflito em silêncio
   — o que o usuário recusou — e por isso entra no mesmo PR.
2. **Incremento 2** só depois do merge, e sem tocar o que o primeiro entregou.
3. Em cada fase, a suíte do diretório tocado; a suíte inteira, uma vez por incremento.
