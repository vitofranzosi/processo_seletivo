# Rastreabilidade: O barema da Etapa (146)

Cada requisito → a tarefa que o implementa → o teste que o verificará. Os testes ainda não existem:
os nomes são os que as tarefas criam. Caminhos relativos a `backend/tests/`. Abreviações:

- `el` = `contract/test_elevacao_degrau_21.py`
- `eb` = `interface/test_barema_na_elaboracao.py` — gravação, travessia, recusas
- `pdf` = `interface/test_barema_no_pdf.py` — o texto extraído
- `ba` = `unit/avaliacoes/test_barema.py` — a função do total
- `me` = `interface/test_mesa_com_barema.py`
- `im` = `integration/avaliacoes/test_imutabilidade_da_concluida.py`
- `cl` = `integration/test_barema_ate_a_classificacao.py`
- `po` = testes do portal (`interface/` ou `portal/`, conforme a tarefa)
- `js` = `javascript/barema.test.js` e `javascript/mesa_barema.test.js`
- `nv` = `navegador/test_jornada_do_barema.py`
- `rc` = testes do julgamento de recurso

A faixa abre em **FR-5200**, **SC-1620** e **UX-420**. Gastos até FR-5233, SC-1635 e UX-423; o resto
da reserva (até o requisito cinco mil duzentos e quarenta e nove, o critério mil seiscentos e trinta e
nove e o UX quatrocentos e vinte e nove) fica livre.

## Os cinco cenários do pedido

| Cenário do pedido | Critério |
|---|---|
| 1 — análise de títulos | SC-1620 |
| 2 — experiência profissional | SC-1621 |
| 3 — avaliação e revisão | SC-1622, SC-1623 |
| 4 — processo sem barema | SC-1624 |
| 5 — configuração compartilhada | SC-1625 |

## Requisitos funcionais

| Requisito | Tarefa | Teste |
|---|---|---|
| FR-5200 | T001, T024 | `eb`, regressão de T024 |
| FR-5201 | T001, T002 | testes unitários de `validate_stages` |
| FR-5202 | T016 | `ba` |
| FR-5203 | T002, T010 | `validate_stages`, `js` |
| FR-5204 | T002, T009 | `validate_stages`, `eb` |
| FR-5205 | T002 | `validate_stages` e validação de publicação |
| FR-5206 | T007, T008, T009, T014 | `eb` |
| FR-5207 | T010 | `js` |
| FR-5208 | T004 | `el` |
| FR-5209 | T013 | `pdf` |
| FR-5210 | T005, T012 | `contract/test_mutabilidade.py`, `contract/test_retificacoes_api.py` |
| FR-5211 | T011 | `unit/interface/test_revisao.py` |
| FR-5212 | T006 | `integration/editais/test_reaproveitamento.py` |
| FR-5213 | T003, T009 | teste da API, `eb` |
| FR-5214 | T019, T020 | `me` |
| FR-5215 | T016, T018 | `ba`, serviço |
| FR-5216 | T016 | `ba` |
| FR-5217 | T016, T018 | `ba`, serviço |
| FR-5218 | T016, T018, T026 | `ba` (zero sem justificativa aceito), serviço, `po` |
| FR-5219 | T017, T018 | `im`, serviço |
| FR-5220 | T023 | `cl` |
| FR-5221 | T022 | compatibilidade (máxima, descrição, documento; ordem não) |
| FR-5222 | T016, T018, T019, T034 | `ba` (reconciliar), serviço, `me`, `rc` |
| FR-5223 | T020 | `me` |
| FR-5224 | T025 | `po` |
| FR-5225 | T026 | `po` |
| FR-5226 | T032 | `rc` |
| FR-5227 | T030, T031 | `rc` |
| FR-5228 | T033 | `po` |
| FR-5229 | T018, T019 | serviço, `me` (autorização inalterada) |
| FR-5230 | T018 | serviço (trilha sem nota) |
| FR-5231 | T024 | regressão de T024 e a suíte existente |
| FR-5232 | T036, T031 | `rc` (recusa no B; removida no C) |
| FR-5233 | T019, T020, T026, T032 | `me`, `po`, `rc` |

## Requisitos de experiência

| Requisito | Tarefa | Teste |
|---|---|---|
| UX-420 | T007 | `eb` |
| UX-421 | T010 | `js` |
| UX-422 | T020, T021 | `me`, `js` |
| UX-423 | T026 | `po` |

## Critérios de sucesso

| Critério | Tarefa | Teste |
|---|---|---|
| SC-1620 | T013, T016, T023 | `pdf`, `ba`, `cl` |
| SC-1621 | T016 | `ba` |
| SC-1622 | T031, T033 | `rc`, `po` |
| SC-1623 | T034 | `rc` |
| SC-1624 | T013, T024 | `pdf`, regressão |
| SC-1625 | T006, T027 | reaproveitamento, cenário de três Perfis |
| SC-1626 | T016, T002 | `ba`, `validate_stages` |
| SC-1627 | T016 | `ba` |
| SC-1628 | T022 | compatibilidade |
| SC-1629 | T016 | `ba` |
| SC-1630 | T017 | `im` |
| SC-1631 | T026 | `po` |
| SC-1632 | T035 | conferência do diff |
| SC-1633 | T020, T026 | `me`, `po` (Retificação que renomeia critério) |
| SC-1634 | T002 | `validate_stages` e validação de publicação |
| SC-1635 | T036 | `rc` |

## Casos-limite

| Caso | Tarefa | Teste |
|---|---|---|
| Etapa sem barema | T024 | regressão |
| Mais de uma avaliação por inscrição | T023 | `cl` (continua bloqueada pela regra de combinação) |
| Quantidade maior que o necessário | T016, T021 | `ba`, `js` |
| Critério sem documento | T016, T025 | `ba`, `po` |
| Documento ligado a vários critérios | T016, T025 | `ba` (zeros sem justificativa), `po` |
| Documento ligado com aplicabilidade restrita | T002 | `validate_stages` (SC-1634) |
| Documento não apresentado | T016, T020 | `ba`, `me` |
| Retificação do barema depois de conclusões | T022 | compatibilidade |
| Retificação de nome, descrição, unidade ou documento | T022 | compatibilidade |
| Avaliação reaberta | T016, T018, T019 | `ba` (reconciliar), serviço, `me` |
| Leitura depois de Retificação | T020, T026, T032 | `me`, `po`, `rc` (SC-1633) |
| Conteúdo publicado em versão anterior | T004 | `el` |
| Reaproveitamento de Edital | T006 | reaproveitamento |
| Remover o Documento Exigido ligado | T002, T009 | `validate_stages`, `eb` |
| Soma acima do que a coluna comporta | T002 | `validate_stages` |
