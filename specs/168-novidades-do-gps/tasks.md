# Tasks: Novidades do GPS

**Input**: [spec.md](spec.md), [plan.md](plan.md)

## Fase 1 — Fundação

- [x] T001 App `novidades`, registrado em `INSTALLED_APPS`, com `LeituraDasNovidades` e a migration `0001_inicial` (FR-7419)
- [x] T002 `catalogo.py`: leitura do TOML, forma de cada nota, ordem e identificadores únicos (FR-7420, FR-7421)
- [x] T003 `leitura.py`: disponibilidade por configuração e capacidade, contagem da sessão e registro da visita (FR-7409 a FR-7411, FR-7414 a FR-7417)

## Fase 2 — US1: quem volta entende o que mudou (P1)

- [x] T004 [US1] Item Novidades na barra, no grupo Ajuda, com a contagem e o ícone (FR-7413, FR-7414, UX-805)
- [x] T005 [US1] `ao_entrar()` na entrada de demonstração, na institucional e na troca de unidade (FR-7415)
- [x] T006 [US1] Página com "Desde sua última visita", primeira visita e "nada novo" (FR-7401, FR-7417, FR-7418)
- [x] T007 [US1] Testes da contagem, do teto, da sessão antiga e do bloco que dura a sessão (`tests/interface/test_novidades.py`)

## Fase 3 — US2 e US3: a nota certa para a pessoa certa (P1)

- [x] T008 [US2] Cartão compacto: categoria, data, título, resumo, benefício, "Como usar" recolhido, link e "Saiba mais" (FR-7403, FR-7404, UX-801 a UX-803)
- [x] T009 [US3] Link só a quem alcança a seção; nota escondida por configuração e por capacidade (FR-7410 a FR-7412)
- [x] T010 [US2] Validação do arquivo na suíte: rotas, âncoras, configurações, capacidades, specs, vocabulário e PR único (FR-7407, FR-7422; `tests/novidades/test_catalogo.py`)
- [x] T011 [US2] Conteúdo inicial de 18/10 a 13/11, conferido contra a Documentação do Sistema e contra o GitHub (FR-7423, FR-7426)

## Fase 4 — US4: filtrar e voltar no tempo (P2)

- [x] T012 [US4] Filtro por categoria com contagem e paginação de 12 (FR-7405, FR-7406)
- [x] T013 [US4] Rodapé das datas (FR-7408)

## Fase 5 — US5: publicar a próxima nota (P2)

- [x] T014 [US5] `scripts/rascunhar_novidades.py` e os testes dele (FR-7424; `tests/novidades/test_rascunho.py`)
- [x] T015 [US5] Guia `doc/curadoria-das-novidades.md` (FR-7425)

## Fase 6 — Fechamento

- [x] T016 Guardiões: mapa das folhas, módulos de view, regex da barra
- [x] T017 Verificação no navegador a 375, 1.280 e 1.440 px, com a barra recolhida (UX-804, SC-2504; [verificacao.md](verificacao.md))
- [x] T018 Suíte inteira contra PostgreSQL (SC-2503)
- [ ] T019 Validação humana com alguém da comissão (SC-2501)
