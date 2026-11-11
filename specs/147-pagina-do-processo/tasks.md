# Tasks: A página do Processo Seletivo

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md)

Um PR, com um commit por fase. Fecha com `cd backend && make lint check test-pg` verde. Caminhos de
código relativos a `backend/processo_seletivo/`; de teste, a `backend/tests/`.

## Phase 1: Composição e dados

- [X] T001 `interface/pagina_do_processo.py`: `compor`, `LinhaDoEdital`, grupos, frase de "Onde
  estamos", marcos consolidados, administração com impedimento; testes unitários puros em
  `unit/interface/test_pagina_do_processo.py` (FR-5301, FR-5307, FR-5310, FR-5311, FR-5313, FR-5317,
  FR-5319, FR-5320, FR-5322)
- [X] T002 `trabalho.do_ator(..., processo=None)` e `_das_avaliacoes(ator, processo=None)`: recorte
  das atribuições antes da carga; teste de que a Lista não muda e de que o recorte vale (FR-5309)
- [X] T003 `views.processo_detalhe`: contexto de `compor`, faixa sem o Edital do próximo passo,
  `aguardando_elaboracao` só para quem gere; remover o gancho e os arquivos do protótipo (FR-5303,
  FR-5304)

## Phase 2: Template e folha

- [X] T004 `interface/templates/interface/processo_detalhe.html` reescrito: topo, grade, Editais,
  série, Administração (FR-5300 a FR-5308, FR-5310 a FR-5321, UX-440 a UX-444)
- [X] T005 `interface/static/interface/telas/processo.css` (UX-440 a UX-444, FR-5315)

## Phase 3: Testes da regra nova

- [X] T006 `interface/test_pagina_do_processo.py`: por situação (em elaboração, ativo, encerrado,
  cancelado) e por papel (gestor, elaborador, homologador, publicador, julgador, auditor, comunicação,
  presidência, avaliação) — o que vê e o que não vê; impedimento desabilitado; grupos; linha do
  Edital; série só em curso; Atenção ausente para quem não alcança (FR-5300 a FR-5321, SC-1664,
  SC-1665, SC-1666)
- [X] T007 `performance/test_orcamento_da_pagina_do_processo.py`: as consultas da composição com 1 e
  com 8 Editais, para gestor, elaborador, homologador, publicador e julgador; o avaliador fica no
  teste do recorte, `integration/interface/test_trabalho_no_processo.py` (SC-1663, FR-5309)
- [X] T008 `navegador/test_jornada_da_pagina_do_processo.py`: 1366 e 390 px, sem rolagem lateral,
  grupo recolhido abre por teclado (SC-1660, SC-1661, SC-1662)

## Phase 4: Revisão do que mudou

- [X] T009 Rever os testes que ancoravam a forma antiga — `test_telas_de_quem_elabora.py`,
  `test_polish_da_058.py`, `test_supervisao.py`, `acceptance/test_supervisao_do_processo.py`,
  `test_processo.py`, `test_hardening_pos_auditoria.py` e os demais que abrem a página —, cada caso
  reescrito para a regra da 147 (FR-5323)
- [X] T010 Marcar como substituídos, nas specs de origem: `FR-1764`, `FR-1771` e a moldura de
  `FR-1773` da `078`; `FR-1069` e `FR-1070` da `058`; a série de `FR-556` da `038` (FR-5323)
- [X] T011 `doc/estudo-pagina-do-processo-2026-11-11.md`: o relatório da rodada 1 em texto, com o
  link para as capturas

## Phase 5: Verificação

- [X] T012 `make lint check test-pg`; capturas do banco `ps_ux_147` a 390, 1366, 1440, 1920 e 3440;
  medidas de SC-1660 a SC-1663 anotadas aqui

## Medidas (11/11/2026)

- **SC-1660**: PS-UAB-2026 (31 Editais), 3.663 px a 1366 × 768 no banco `ps_ux_147` (antes, 10.369).
- **SC-1661**: `navegador/test_jornada_da_pagina_do_processo.py` — "O que fazer agora" e o título de
  "Precisa de atenção" na primeira dobra a 1366 × 768.
- **SC-1662**: nenhuma rolagem lateral em 390, 1366 (barra aberta e recolhida), 1440, 1920 e 3440,
  nos sete Processos do banco de demonstração.
- **SC-1663**: a composição custa o mesmo com 1 e 8 Editais para gestor, elaborador, homologador,
  publicador e julgador (`performance/test_orcamento_da_pagina_do_processo.py`); na página inteira,
  +1 consulta por papel no PS-UAB-2026; a avaliadora, 72 → 128 pelas alocações dela neste Processo
  (no protótipo, sem o recorte, 195).
- `make lint check` verde; `make test-pg`: 18.343 passando, 12 pulados e 3 falhas, duas corrigidas
  depois (a linha da 147 no README e a quarta porta da Retificação em
  `test_auditoria_passagem_da_retificacao.py`) e a terceira o teste de tempo da ocupação, que passou
  cinco de cinco isolado — o ruído descrito na CLAUDE.md.

## Revisão do PR #466 (11/11/2026)

Oito achados do code review, todos corrigidos: o período sem término ("sem término declarado"); a
data com ano e o término nos marcos e na linha; o marco em curso "até" o término, e não "Próximo" com
data passada; o ato impedido na ordem do Tab; os atos comuns pela marca do ato, e não "o primeiro";
`pending_editais` sobre a lista já lida, sem consulta a mais; a marca da Retificação num parcial comum
à Lista e ao Processo (`_marca_da_retificacao.html`); as marcas da linha com a `cc-marca` do mapa do
Edital. `make test-pg` depois: 18.357 passando, 12 pulados e 1 falha, de navegador, na convocação da
121 (`net::ERR_ABORTED` sob carga), que passou 15 de 15 isolada.
