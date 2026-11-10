# Tasks: Conferência antes de convocar os titulares

**Input**: [spec.md](spec.md), [plan.md](plan.md)

## Phase 1: Foundational

- [ ] T001 Extrair `verificar_titulares` em `backend/processo_seletivo/convocacao/application/fluxo.py` e fazer `convocar_titulares` chamá-la (D-004, FR-4811)
- [ ] T002 Extrair `_renderizar` e criar `previa_das_mensagens` em `backend/processo_seletivo/convocacao/application/comunicar.py` (D-003, FR-4803)
- [ ] T003 Criar `conferencia_dos_titulares` e `gesto_ja_concluido` em `fluxo.py` (FR-4801 a FR-4806, FR-4810 a FR-4812)

## Phase 2: User Story 1 — conferir antes de convocar (P1)

- [ ] T004 [US1] Reescrever `convocar_titulares_view` em `backend/processo_seletivo/interface/views.py`: a conferência respondida ao pedido, sem sessão (FR-4800, FR-4807, FR-4813, D-002)
- [ ] T005 [US1] Criar `interface/convocacao_conferir.html` com as peças de `marco_conferir.html` e a regra da mensagem na folha da tela (FR-4801 a FR-4806, FR-4814, FR-4815, FR-4818, UX-330 a UX-332)
- [ ] T006 [US1] Testes da prévia sem efeito, da confirmação, da publicação e de quem fica de fora em `backend/tests/interface/test_conferencia_ao_convocar.py` (SC-1500, SC-1501, SC-1505)

## Phase 3: User Story 2 — uma vez só, e só sobre o conferido (P1)

- [ ] T007 [US2] Confirmação repetida pela chave, alcance mudado e texto mudado (FR-4808 a FR-4812), com testes (SC-1502, SC-1503)
- [ ] T008 [US2] Autorização: quem não emite é recusado na conferência e na confirmação (FR-4813, SC-1504)

## Phase 4: User Story 3 — a ajuda diz o que acontece (P2)

- [ ] T009 [US3] Botão e ajuda do gesto em `convocacao.html` (FR-4816), com teste

## Phase 5: Polish

- [ ] T010 Ajustar `test_convocacao_em_fluxo.py` e `test_conferencia_do_texto.py` ao gesto com conferência (FR-4817)
- [ ] T011 `rastreabilidade.md` com FR, SC, UX e casos-limite
- [ ] T012 `make lint check test-pg` com `DB_NAME` próprio
- [ ] T013 Verificação no navegador com o C10 da `134`, a 1440 e a 375 px (SC-1501)

## Dependencies

T001–T003 antes de T004; T004–T005 antes dos testes; T010 junto de T004 (os helpers mudam).
