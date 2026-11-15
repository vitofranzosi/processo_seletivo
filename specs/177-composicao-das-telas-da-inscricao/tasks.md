# Tasks: A composição das telas da inscrição no portal

**Input**: [spec.md](spec.md), [plan.md](plan.md)

**Tests**: pedidos pela spec (SC-2801 a SC-2806) e pelos guardiões do portal; escritos antes da
implementação de cada história.

## Phase 1: Setup

- [x] T001 Banco próprio `ps_177` (migrate, `semear_unidades`, `seed_demo`) e entrada `composicao-177` em `.claude/launch.json`, sem tocar nas outras
- [x] T002 Capturas **antes** das três telas a 375, 768, 1280, 1440 e 1920 px em `specs/177-composicao-das-telas-da-inscricao/capturas/antes/` (FR-8122)

## Phase 2: Foundational

- [x] T003 Partial `backend/processo_seletivo/portal/templates/portal/_comeco_da_inscricao.html`: trilha "Minhas inscrições › {Processo} · Edital {n}/{ano}", título e "Perfil de Vaga: {nome}" (FR-8110, UX-953)
- [x] T004 Seção da 177 no fim de `backend/processo_seletivo/portal/static/portal/portal.css`: `.jornada-da-inscricao`, a medida no parágrafo, os blocos na largura da coluna, a trilha, o selo, a faixa de ações (FR-8100 a FR-8104, FR-8119, FR-8121)

## Phase 3: User Story 1 — Minhas inscrições (P1)

- [x] T005 [US1] Testes em `backend/tests/portal/test_composicao_das_telas_da_inscricao.py`: título do cartão é o Processo, linha Edital · Perfil, prazo nos três casos, sem prazo vencido, "Acesso à conta" fora do subtítulo, coluna
- [x] T006 [US1] `_passo_pendente_na_lista` devolve o `Passo`; `_item_da_lista` acrescenta `prazo` sem consulta (FR-8106) em `backend/processo_seletivo/portal/views.py`
- [x] T007 [US1] `inscricoes.html`: coluna, começo com "Acesso à conta", cartão na ordem da FR-8105, selos (FR-8107), prazo, ação com a largura do rótulo (FR-8108, FR-8109)

## Phase 4: User Story 2 — Acompanhar (P1)

- [x] T008 [US2] Testes: começo comum, coluna, "Ver o que enviei" secundário, um botão cheio, ordem dos blocos
- [x] T009 [US2] View `acompanhamento` passa o nome do Perfil (FR-8110)
- [x] T010 [US2] `acompanhamento.html`: coluna, começo, mensagem logo depois, "Ver o que enviei" secundário (FR-8111 a FR-8114)

## Phase 5: User Story 3 — Minha inscrição (P2)

- [x] T011 [US3] Testes: começo comum, faixa situação e protocolo, grade, ações
- [x] T012 [US3] `_conferencia` passa o nome do Perfil; `inscricao_enviada.html` com a grade `campos-em-grade` e a faixa de ações (FR-8115 a FR-8117)

## Phase 6: Polish

- [x] T013 Conferência no navegador nas cinco larguras e a 320 px: margens, bordas dos blocos, rolagem horizontal, altura das ações (SC-2800 a SC-2805, SC-2807)
- [x] T014 Capturas **depois** em `capturas/depois/` (FR-8122, SC-2808)
- [x] T015 `rastreabilidade.md` cobrindo todo FR, SC e UX
- [x] T016 `make lint check`; `tests/portal`, `tests/interface`, `tests/integration/portal`, `tests/performance/test_lista_com_convocacao.py` e `tests/test_citacoes_de_requisito.py` contra PostgreSQL
- [x] T017 PR para a `main`, sem merge, com as capturas

## Dependencies

T001 → T002 → (T003, T004) → US1, US2, US3 (independentes entre si) → T013 → T014 → T016 → T017.
