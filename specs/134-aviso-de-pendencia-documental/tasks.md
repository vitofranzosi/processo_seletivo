# Tasks: O aviso de pendência documental por e-mail (134)

**Input**: [spec.md](spec.md), [plan.md](plan.md). T001–T015 concluídas em 08/11/2026; T016–T019, da
revisão do PR, em 09/11/2026.

## Fase 1 — A norma

- [x] T001 Revisar a FR-084 da `010` para cinco situações, com as três redações anteriores ao fim
  (`specs/010-area-do-candidato/spec.md`) — FR-4601
- [x] T002 Rever a FR-3614 da `115`, a linha do "fica fora" e a QI-7, com a redação anterior — FR-4601
- [x] T003 Guarda da FR-084 a pares, cinco situações, `REVISAO_DA_FR_084_PELA_134` no despacho
  (`backend/tests/test_situacoes_de_mensagem.py`, `avisos/application/despacho.py`) — FR-4602
- [x] T004 Ajustar o SC-1161 da `121` à contagem nova
  (`backend/tests/integration/convocacao/test_mensagem_da_convocacao.py`) — FR-4602

## Fase 2 — O registro

- [x] T005 Origem `PENDENCIA`, recusas e operações em `avisos/domain/nomes.py` — FR-4618
- [x] T006 *Constraint* do ato por origem e migration `avisos/0002` — FR-4618, SC-1448

## Fase 3 — O texto

- [x] T007 `avisos/domain/pendencia.py`: assunto, corpo, documentos, modalidade, prazo, rodapé —
  FR-4613 a FR-4617
- [x] T008 Testes de unidade do texto (`tests/unit/avisos/test_texto_da_pendencia.py`)

## Fase 4 — O gesto

- [x] T009 `avisos/application/pendencias.py`: `selecionar`, `previa`, `avisar_pendencias` —
  FR-4603 a FR-4612, FR-4618, FR-4620
- [x] T010 Trilha de cada resultado no despacho, só para a origem nova — FR-4621
- [x] T011 Porta da `066` para a origem nova, reenvio recusado — FR-4622
- [x] T012 View, rota e seção na tela de condução; histórico e detalhe do aviso — FR-4603, FR-4605,
  UX-311 a UX-313
- [x] T013 Testes de integração (`tests/integration/avisos/test_aviso_de_pendencia.py`) — SC-1441 a
  SC-1447

## Fase 5 — Fechamento

- [x] T014 README (tabela de incrementos) e `test_vocabulario_do_aviso` com o texto novo
- [x] T015 `make lint check test-pg`, registro em [verificacao.md](verificacao.md)

## Fase 6 — Revisão do PR (09/11/2026)

- [x] T016 O despacho relê a pendência antes de cada tentativa e interrompe o aviso que chegaria tarde;
  o interrompido pelo despacho não conta no dia (`pendencias.motivo_para_nao_enviar`,
  `despacho._iniciar`) — FR-4623, SC-1449, D-011
- [x] T017 A trilha do envio num ponto de salvamento: a falha dela não desfaz o resultado — FR-4621
- [x] T018 A unidade lida uma vez por gesto, os avisos em lote, a raiz por `documentos.raizes_das`, e a
  prévia sobre a leitura que a condução já fez — FR-4605, FR-4618
- [x] T019 Testes: a órfã auditada, a trilha que falha e o Processo em estado final — FR-4610, FR-4621
