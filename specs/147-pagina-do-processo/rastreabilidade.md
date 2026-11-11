# Rastreabilidade: A página do Processo Seletivo (147)

Cada requisito → a tarefa que o implementa → o teste que o verifica. Caminhos relativos a
`backend/tests/`. Abreviações:

- `pp` = `interface/test_pagina_do_processo.py` — a página por situação e por papel
- `un` = `unit/interface/test_pagina_do_processo.py` — a composição pura
- `tr` = `integration/interface/test_trabalho_no_processo.py` — o recorte da faixa
- `or` = `performance/test_orcamento_da_pagina_do_processo.py`
- `nv` = `navegador/test_jornada_da_pagina_do_processo.py`

A faixa abre em **FR-5300**, **SC-1660** e **UX-440**. Gastos até FR-5323, SC-1666 e UX-444; o resto
da reserva (até o requisito cinco mil trezentos e trinta e nove, o critério mil seiscentos e setenta e
nove e o UX quatrocentos e quarenta e nove) fica livre.

## Requisitos funcionais

| Requisito | Tarefa | Teste |
|---|---|---|
| FR-5300 | T004 | `pp` |
| FR-5301 | T001, T004 | `un`, `pp` |
| FR-5302 | T004 | `pp` |
| FR-5303 | T001, T003, T004 | `un`, `pp` |
| FR-5304 | T003 | `pp` |
| FR-5305 | T004 | `pp` |
| FR-5306 | T004 | `pp` |
| FR-5307 | T001, T004 | `un`, `pp` |
| FR-5308 | T004 | `pp` |
| FR-5309 | T002 | `tr`, `or` |
| FR-5310 | T001, T004 | `un`, `pp` |
| FR-5311 | T001, T004 | `un`, `pp` |
| FR-5312 | T004 | `pp` |
| FR-5313 | T001, T004 | `un`, `pp` |
| FR-5314 | T004 | `pp` |
| FR-5315 | T005 | `nv` |
| FR-5316 | T004 | `pp` |
| FR-5317 | T001, T004 | `un`, `pp` |
| FR-5318 | T004 | `pp` |
| FR-5319 | T001, T004 | `un`, `pp` |
| FR-5320 | T001, T004 | `un`, `pp` |
| FR-5321 | T004 | `pp` |
| FR-5322 | T001 | `un` |
| FR-5323 | T009, T010 | os testes revistos da 038, 058 e 078 |

## Requisitos de experiência

| Requisito | Tarefa | Teste |
|---|---|---|
| UX-440 | T004, T005 | `pp` (ordem), `nv` (estreito) |
| UX-441 | T004 | `pp` |
| UX-442 | T004, T005 | `pp` |
| UX-443 | T005 | `nv` |
| UX-444 | T005 | `pp` |

## Critérios de sucesso

| Critério | Tarefa | Verificação |
|---|---|---|
| SC-1660 | T008, T012 | `nv`, captura de `ps_ux_147` |
| SC-1661 | T008, T012 | `nv`, captura |
| SC-1662 | T008, T012 | `nv`, capturas nas cinco larguras |
| SC-1663 | T007 | `or` |
| SC-1664 | T006 | `pp` |
| SC-1665 | T006, T009 | `pp`, testes revistos |
| SC-1666 | T006 | `pp` |

## Casos-limite

| Caso | Teste |
|---|---|
| Processo sem Edital (legado) | `pp` |
| Quem não alcança espécie alguma | `pp` |
| Quem alcança parte das espécies | `pp` (linha relativa) |
| Edital encerrado com condição de atenção | `un` |
| Muitos Editais com atenção (recolhidos) | `pp` |
| Mais de seis marcos | `un` |
| Sem cronograma ou sem período | `un` |
| Período cancelado | `un` |
| Título longo | `nv` |
| Elaborador sem Edital em elaboração | `pp` |
| "Aguardando quem elabora" | `pp` |
| Ato recém-registrado | `pp` |
