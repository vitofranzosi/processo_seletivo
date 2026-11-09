# Tasks: O andamento diz o que cada providência é (135)

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/andamento.md](contracts/andamento.md)

**Tests**: pedidos pela spec (SC-1460 a SC-1466); escritos antes da implementação de cada fase. Os
puros vão em `backend/tests/unit/interface/test_andamento_o_que_cada_providencia_e.py`; os de cenário
em `backend/tests/integration/treinamento/test_andamento_dos_cenarios.py`.

## Phase 1: Setup

- [x] T001 Conferir `gh pr view 440 --json state` e a base da branch (a spec no #440); `.specify/feature.json` apontando para `specs/135-correcoes-da-derivacao`; `backend/.env` com `DB_NAME=ps135`
- [x] T002 Ler os cinco cenários da `134` pelo gerador (`tests/fixtures/treinamento.py::carregar`) e anotar, em cada um, a lista PPP, a situação da ordem e a do resultado, para os testes de cenário

## Phase 2: Foundational — o dado do divulgado na condução (R-003)

- [x] T003 `_celula_da_publicacao` devolve `natureza` (`PRELIMINAR`, `DEFINITIVA` ou vazio; a da defasada mais recente no *obsoleto*) em `backend/processo_seletivo/interface/conducao_do_marco.py`
- [x] T004 Constantes `NADA`, `PRELIMINAR`, `DEFINITIVO`, a função `divulgado_da_celula` e os campos `lista_vazia` e `divulgado` de `Celula` em `backend/processo_seletivo/interface/andamento.py`; `lista_vazia` em `Providencia` e em `Providencia.da_celula` em `backend/processo_seletivo/interface/providencias.py`

## Phase 3: User Story 1 — a lista sem inscritos é dita antes da ordem (P1)

- [x] T005 [P] [US1] Testes puros: *Pendente* e *Obsoleto* com `vazia` ganham nota, ato e dado; *Depois* e *Feito* não mudam; o agrupamento não junta vazia com não vazia e põe duas vazias no plural; a providência de outro papel diz a frase (FR-4671 a FR-4676)
- [x] T006 [P] [US1] Testes de integração do critério em `backend/tests/integration/classificacao/test_listas_sem_concorrente.py`: a lista reservada sem autodeclarado é vazia; com um, não; a eliminada antes da Etapa do marco não concorre; a ampla nunca entra; igual ao `recorte_sem_ninguem` da tela da ordenação (FR-4670)
- [x] T007 [US1] `_universo` (extraído de `calcular_ordem`) e `listas_sem_concorrente` em `backend/processo_seletivo/classificacao/application/calculo.py` (R-001)
- [x] T008 [US1] `situacao_da_ordem` lê `vazia`; `_Leitor._marco` pergunta `listas_sem_concorrente` uma vez por marco por pontuação, só com ordem a emitir ou obsoleta, em `backend/processo_seletivo/interface/andamento.py` (R-001, R-002)
- [x] T009 [US1] A chave do agrupamento com `lista_vazia` e o plural ao juntar duas vazias em `backend/processo_seletivo/interface/providencias.py` (FR-4674)
- [x] T010 [US1] Testes de cenário: C08, C12 e C14 dizem "lista sem inscritos" na providência da ordem da PPP, para a presidência e para outro papel, na matriz e no "Próximo nesta lista"; C04 não diz (SC-1460, SC-1461, FR-4675)

## Phase 4: User Story 2 — o que foi divulgado é dado (P2)

- [x] T011 [P] [US2] Testes puros: `divulgado` em cada situação do resultado (nada, preliminar, definitivo, obsoleto, preliminar com ordem obsoleta); a redação das notas trocada não muda situação nem resumo (FR-4677 a FR-4680, SC-1463)
- [x] T012 [US2] `situacao_do_resultado`, `_Leitor._resultado`, `_Leitor._espera_do_corte` e `_resultado_em_palavras` decidem por `divulgado` em `backend/processo_seletivo/interface/andamento.py` (R-003, R-006)
- [x] T013 [US2] Acrescentar `natureza` (ou `divulgado`) à entrada dos testes puros da `127` e da `133` que montam a célula da publicação só com a nota, sem mudar a expectativa, em `backend/tests/unit/interface/test_andamento_situacoes.py` e `test_andamento_composicao.py`

## Phase 5: User Story 3 — a espera do definitivo não oferece o que já foi feito (P2)

- [x] T014 [P] [US3] Testes puros: com o preliminar publicado, a razão do prazo aberto e a do recurso pendente não dizem "publique como resultado preliminar", e a primeira frase é a da aferição; as outras razões não mudam; `MENSAGENS` intacto (FR-4681 a FR-4683)
- [x] T015 [US3] `MENSAGENS_COM_O_PRELIMINAR_PUBLICADO` e `mensagem_com_o_preliminar_publicado` em `backend/processo_seletivo/divulgacao/domain/publicabilidade.py` (R-004)
- [x] T016 [US3] `situacao_do_resultado` usa a segunda redação no ramo do preliminar publicado, em `backend/processo_seletivo/interface/andamento.py`
- [x] T017 [US3] Testes de cenário: C08 e C12 sem a alternativa no nível 1 e na matriz; a prévia de publicação do marco com a mensagem de antes (SC-1462)

## Phase 6: User Story 4 — cada contagem diz o que conta (P3)

- [x] T018 [P] [US4] Testes puros: o resumo diz "em aberto nos marcos" com o mesmo número; sem providência, nada (FR-4684, FR-4685)
- [x] T019 [US4] A redação em `resumo_do_perfil`, em `backend/processo_seletivo/interface/andamento.py`
- [x] T020 [US4] Teste de cenário: C06, o resumo do Perfil e o cartão com os números de antes (SC-1464)

## Phase 7: Polish

- [x] T021 Rodar a suíte; ajustar só os textos que a spec troca de propósito; conferir que nenhum caso da `127` e da `133` mede o resumo do preliminar com ordem obsoleta (R-006)
- [x] T022 O orçamento da `127` sem mudança de teto (`tests/performance/test_andamento_em_escala.py`, SC-1465)
- [x] T023 `make lint check test-pg` com `DB_NAME=ps135`; `migrate --check` sem migration nova (SC-1466)
- [x] T024 Conferir no navegador o C08 e o C12 (e o C04, o C06 e o C14), num banco próprio dos cenários, e registrar em `specs/135-correcoes-da-derivacao/verificacao.md`
- [x] T025 `specs/135-correcoes-da-derivacao/rastreabilidade.md`: cada FR- e SC- → tarefas → testes

## Dependencies

- Phase 2 antes de todas as histórias (os campos novos).
- US1, US2, US3 e US4 são independentes entre si depois da Phase 2. US3 toca o mesmo ramo de
  `situacao_do_resultado` que a US2: implementar a US2 primeiro evita conflito no mesmo trecho.
- Polish depois de todas.

## Parallel Example

```text
T005, T006 (US1), T011 (US2), T014 (US3) e T018 (US4) são testes em arquivos ou trechos diferentes,
e podem ser escritos juntos depois da Phase 2.
```

## Implementation Strategy

MVP = US1 (o gate do Centro de Controle). As outras três seguem no mesmo PR, na ordem de prioridade.
