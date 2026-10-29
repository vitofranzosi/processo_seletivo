# Tasks: Agenda dos Editais

**Input**: Design documents from `specs/101-agenda-dos-editais/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/agenda.md, quickstart.md

**Tests**: obrigatórios — a autorização do usuário de 29/10/2026 enumera dezessete frentes de
validação, e o estudo os critérios de aceitação. Em cada fase, o teste vem antes da implementação.

**Caminhos**: relativos à raiz do repositório; código em `backend/processo_seletivo/`, testes em
`backend/tests/`.

## Phase 1: Setup

- [ ] T001 Preparar a worktree — `uv sync --extra dev --extra assistente`, `backend/.env` com `DB_NAME=ps101` e o superusuário local — e registrar a linha de base verde de `backend/tests/interface/test_shell_da_gestao.py` e `backend/tests/interface/test_folha_estatica.py` antes de tocar a barra e as folhas

## Phase 2: Foundational — a projeção pura e a leitura

**Purpose**: todas as histórias leem a mesma projeção (D-001, FR-2612). Nada aqui toca template.

- [ ] T002 Criar `backend/processo_seletivo/interface/agenda.py` com a docstring "Este módulo só lê" e as formas de `data-model.md` (`EditalDaAgenda`, `Marco`, `Periodo`, `Janela`, `DiaDaGrade`, `Sintese`, `AvisoDeRetificacao`, `Filtros`, `Leitura`)
- [ ] T003 [P] Escrever os unitários da projeção — pontual com e sem término no mesmo dia, meia-noite sem hora, período com abertura e encerramento e nada nos dias do meio, período sem término só com abertura, cancelado, espécie (inscrições > etapa > demais), fase traduzida (por vir, em curso pelo cronograma, data passada), Evento sem descrição, 31/12 às 23:30 na zona institucional — em `backend/tests/unit/interface/test_agenda.py` (FR-2616 a FR-2622, FR-2642)
- [ ] T004 Implementar `marcos_do_conteudo(edital, conteudo, agora)` e `periodos_do_conteudo(edital, conteudo, agora)` sobre `editais/domain/fase_do_evento.py` e `editais/domain/calendario.py`, sem regra nova, em `backend/processo_seletivo/interface/agenda.py`
- [ ] T005 [P] Escrever os unitários de janela, ordem, filtro e síntese — janela de 7 e 30 dias a partir do começo do dia, mês, dia; ordem instante → Edital → nome; filtros de Edital e espécie; síntese sem cancelados, Editais distintos, encerramentos, dias com vários, dia mais carregado; Edital sem Evento fora das opções; Edital encerrado só com o que passou — em `backend/tests/unit/interface/test_agenda.py` (FR-2615, FR-2631, FR-2632, FR-2634, FR-2637)
- [ ] T006 Implementar `janela_do_mes`, `janela_proxima`, `janela_do_dia`, `na_janela`, `ordenar`, `filtrar`, `sintese` e `periodos_que_tocam` em `backend/processo_seletivo/interface/agenda.py`
- [ ] T007 [P] Escrever os testes de integração da fonte com o ciclo real de publicação e Retificação — Edital em elaboração ausente; publicado presente; Retificação vigente que muda data; Evento acrescentado por Retificação; Retificação de vigência futura antes e depois de `valid_from`, com o aviso; Edital cancelado ausente; Edital de outro escopo ausente, inclusive pelo filtro — em `backend/tests/integration/agenda/test_fonte.py` (FR-2610, FR-2612 a FR-2615, SC-949, SC-952)
- [ ] T008 Implementar `ler(ator, parametros, *, agora=None, hoje=None)` — a consulta dos Editais do escopo (publicados e encerrados, com o Processo), `versoes_vigentes`, a consulta agregada das versões futuras, a leitura dos parâmetros com padrão para valor inválido, as opções de filtro, o próximo marco depois da janela e os endereços de navegação — em `backend/processo_seletivo/interface/agenda.py` (FR-2610, FR-2614, FR-2638, FR-2644, R-002, R-003, R-009)

**Checkpoint**: `ler` devolve a `Leitura` completa, testada sem template.

## Phase 3: User Story 1 — o mês (Priority: P1) 🎯 MVP

**Goal**: a grade do mês com contagem, destaque, nomes e períodos.

**Independent Test**: três Editais com marcos em novembro; abrir a Agenda em novembro e conferir
contagens, destaque, nomes e a lista de períodos.

- [ ] T009 [P] [US1] Escrever os unitários de `semanas_do_mes` — 4 semanas (fevereiro de 2026), 5 (novembro de 2026), 6 (agosto de 2026), domingo primeiro, dias de fora vazios, destaque a partir de 2, até dois nomes na ordem do dia e *mais N*, hoje marcado, soma das células igual à síntese — em `backend/tests/unit/interface/test_agenda.py` (FR-2624 a FR-2626, FR-2635, SC-951)
- [ ] T010 [US1] Implementar `semanas_do_mes(ano, mes, marcos, hoje)` sobre `calendar.Calendar(firstweekday=6)` em `backend/processo_seletivo/interface/agenda.py`
- [ ] T011 [US1] Acrescentar a view `agenda` (identidade da sessão ou `pedir_identificacao`; nenhuma recusa por capacidade; nenhum `Http404`) em `backend/processo_seletivo/interface/views.py` e a rota `path("agenda", ...)` em `backend/processo_seletivo/interface/urls.py` (FR-2609, FR-2611)
- [ ] T012 [US1] Acrescentar `Secao("Agenda", "interface:agenda", TRABALHO, _toda_identidade, "i-calendario")` depois de *Visão Geral* em `backend/processo_seletivo/interface/navegacao.py` e o `<symbol id="i-calendario">` em `backend/processo_seletivo/interface/templates/interface/base.html` (FR-2609)
- [ ] T013 [US1] Criar `backend/processo_seletivo/interface/templates/interface/agenda.html` (título, proveniência, instante, abas, avisos, síntese, filtros, legenda de previsto × efetivo, estados vazios) e `_agenda_mes.html` (navegação do mês, tabela com `caption` e `th scope`, células, períodos no mês), conforme `contracts/agenda.md` (FR-2623 a FR-2627, FR-2640, FR-2641, FR-2643, FR-2644)
- [ ] T014 [US1] Criar `backend/processo_seletivo/interface/static/interface/telas/agenda.css` com regra para toda classe dos templates, nomes ocultos abaixo de 60rem, `table-layout:fixed`, destaque pelo par `--verde-escuro`/`--verde-claro`, e registrá-la em `QUEM_CARREGA` de `backend/tests/interface/test_folha_estatica.py` (FR-2626, FR-2645, SC-953, R-011)
- [ ] T015 [US1] Escrever os testes de tela do mês — o mês corrente como padrão, grade de 7 colunas com `caption`, destaque do dia com vários, nomes e *mais N*, navegação para o mês anterior e o seguinte, períodos no mês, cancelado fora da grade, nome acessível do acesso ao dia, mês inválido cai no corrente — em `backend/tests/interface/test_agenda.py` (FR-2621, FR-2623 a FR-2627, FR-2645, SC-953)

**Checkpoint**: a Agenda abre no mês, pela barra, para toda identidade.

## Phase 4: User Story 2 — o dia (Priority: P1)

**Goal**: a relação completa de um dia, com os dois links.

**Independent Test**: um dia com cinco marcos de três Editais; escolher o dia e conferir os cinco.

- [ ] T016 [US2] Criar `backend/processo_seletivo/interface/templates/interface/_agenda_dia.html` e `_agenda_marco.html` (hora ou *Abre*/*Encerra*, nome, Edital, Processo, local, intervalo, *Edital encerrado*, *Cancelado*, fase, links para `interface:detalhe` e `portal:selecao#cronograma-titulo`), e o agrupamento por Edital acima de oito marcos (FR-2628 a FR-2630)
- [ ] T017 [US2] Escrever os testes de tela do dia — os cinco marcos com os dois links, cancelado identificado, dia sem marco dentro de um período, volta ao mês com os filtros, agrupamento acima de oito, dia inválido ignorado — em `backend/tests/interface/test_agenda.py` (FR-2628 a FR-2630, SC-951)

## Phase 5: User Story 5 — confiar no publicado e vigente (Priority: P1)

**Goal**: a tela nunca diz mais do que o cronograma publicado diz.

**Independent Test**: os cenários de T007 vistos pela página.

- [ ] T018 [US5] Escrever os testes de tela da confiabilidade — aviso de Retificação a vigorar com o Edital e a data; proveniência e legenda presentes; nenhuma das palavras proibidas (*concluído*, *cumprido*, *realizado*, *pendente*, *atrasado*) no texto visível de nenhuma visualização; marco de data passada dito *data passada*; Edital de outra unidade ausente pela tela — em `backend/tests/interface/test_agenda.py` (FR-2610, FR-2614, FR-2636, FR-2640 a FR-2642)

## Phase 6: User Story 3 — próximos marcos (Priority: P2)

**Goal**: a lista dos próximos 7 ou 30 dias, com o bloco *em curso*.

**Independent Test**: marcos espalhados por 40 dias; conferir as janelas de 7 e 30.

- [ ] T019 [US3] Criar `backend/processo_seletivo/interface/templates/interface/_agenda_proximos.html` (bloco *em curso* com o tempo que falta ou *sem término declarado*; um `section` por dia com marco; atalho para 30 dias) (FR-2631 a FR-2633)
- [ ] T020 [US3] Escrever os testes de tela de Próximos marcos — janela de 7 e de 30, período aberto antes de hoje só no bloco *em curso*, *encerra hoje*, cancelado identificado e fora da síntese, janela vazia com o próximo marco, síntese com o dia mais carregado — em `backend/tests/interface/test_agenda.py` (FR-2621, FR-2631 a FR-2634, FR-2644)

## Phase 7: User Story 4 — filtrar e trocar sem perder (Priority: P2)

**Goal**: os filtros valem nas três telas e sobrevivem a toda navegação.

**Independent Test**: filtrar um Edital no mês, trocar para Próximos e para um dia.

- [ ] T021 [US4] Completar o formulário de filtros em `agenda.html` (Edital e espécie, `visao`, `mes`/`janela` ocultos, *Limpar filtros*) e propagar `edital` e `especie` em todo link montado por `ler` (FR-2637 a FR-2639)
- [ ] T022 [US4] Escrever os testes de tela dos filtros — o filtro de Edital nas abas, no dia, na navegação do mês e na janela de 30; espécie; filtro sem resultado com *Limpar filtros*; identificador de outro escopo ignorado; nenhuma opção de unidade, modalidade ou categoria — em `backend/tests/interface/test_agenda.py` (FR-2610, FR-2637 a FR-2639)

## Phase 8: Polish & Cross-Cutting Concerns

- [ ] T023 Escrever o teste de orçamento — mesmas consultas com um e com cinco Editais publicados, nas duas visualizações e no dia — em `backend/tests/interface/test_agenda.py` (FR-2646, SC-950)
- [ ] T024 Escrever o roteiro de demonstração `doc/estudo-calendario-institucional-2026-10-29/semear_demonstracao.py` (Editais publicados pelo ajudante de publicação dos testes, marcos concentrados num dia, período atravessando o mês, Evento cancelado, Retificação de vigência futura), só com dado fictício, e a entrada `agenda-101` em `.claude/launch.json`, sem tocar as demais
- [ ] T025 Medir o custo do conteúdo inteiro com 30 Editais publicados — consultas, tempo da página e volume de `content` — e registrar em `specs/101-agenda-dos-editais/quickstart.md`, seção *Desempenho*; se houver problema mensurável, aplicar a menor otimização da research R-004 (SC-950)
- [ ] T026 Prova visual no navegador: o mês com concentração, o dia, Próximos marcos, a 1280 px e a 375 px, sem rolagem horizontal (SC-953); capturas na conversa, e nenhuma afirmação de validação humana (SC-948 fica pendente)
- [ ] T027 Escrever `specs/101-agenda-dos-editais/rastreabilidade.md` — cada FR-/SC- da spec → tarefa → teste — e atualizar a linha da `101` no `README.md`
- [ ] T028 Rodar `cd backend && make lint check test-pg DB_NAME=ps101` — que inclui `tests/test_sem_dado_pessoal_da_amostra.py` sobre o roteiro em `doc/` — e registrar o resultado
- [ ] T029 `/speckit-converge` contra spec, plan e tasks; corrigir lacunas e repetir até não restar nenhuma

## Dependencies & Execution Order

- **Setup (T001)** → **Foundational (T002–T008)** → histórias.
- **US1 (T009–T015)** depende de T008; ela cria a view, a rota, a barra, a página e a folha, e por
  isso vem antes das demais histórias de tela.
- **US2 (T016–T017)**, **US5 (T018)**, **US3 (T019–T020)** e **US4 (T021–T022)** dependem de US1
  (página e folha) e não dependem entre si, exceto que todas editam `agenda.css` e
  `test_agenda.py` — por isso correm em sequência nesta entrega, de um autor só.
- **Polish (T023–T029)** depois de todas as histórias; T028 e T029 por último.

## Parallel Opportunities

- T003, T005 e T007 são arquivos de teste independentes, escritos antes das implementações T004,
  T006 e T008.
- T009 (unitários da grade) pode ser escrito junto de T005.
- T024 (roteiro de demonstração) não depende de template e pode correr junto da Phase 3.

## Implementation Strategy

1. **MVP**: Phases 1–3 — a projeção e o mês. Já responde à pergunta que motivou a feature.
2. **Incremento 1**: Phase 4 (o dia) e Phase 5 (confiabilidade pela tela) — sem elas o número da
   célula não se explica, e a promessa de previsto × efetivo não está provada.
3. **Incremento 2**: Phases 6–7 — a lista e os filtros.
4. **Fechamento**: Phase 8 — orçamento, medição, prova visual, rastreabilidade, suíte e convergência.
