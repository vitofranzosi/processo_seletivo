# Tasks: Novidades do GPS

**Input**: [spec.md](spec.md), [plan.md](plan.md)

## Fase 1 — Fundação

- [x] T001 App `novidades`, registrado em `INSTALLED_APPS`, com `LeituraDasNovidades` e a migration `0001_inicial` (FR-7419)
- [x] T002 `catalogo.py`: leitura do TOML, forma de cada nota, ordem e identificadores únicos (FR-7420, FR-7421)
- [x] T003 `leitura.py`: disponibilidade por configuração e capacidade, contagem da sessão e registro da visita (FR-7409 a FR-7411, FR-7414 a FR-7417)

## Fase 2 — US1: quem volta entende o que mudou (P1)

- [x] T004 [US1] Item Novidades na barra, no grupo Ajuda, com a contagem e o ícone (FR-7413, FR-7414, UX-805)
- [x] T005 [US1] `ao_entrar()` na entrada de demonstração e na institucional, e `recontar()` na troca de unidade, pela camada de identidade (FR-7415, FR-7417)
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
- [x] T019 Achados da revisão de código de 14/11: testes sem teto de data nem título fixo, troca de unidade que preserva o bloco, público com várias capacidades, contagem na camada de identidade, falha do arquivo guardada, roteiro que não confunde número solto com spec e avisa a lista cortada
- [x] T020 Segunda revisão de 14/11: registro `curadoria.toml` e roteiro pela data do merge (FR-7424); 17 notas novas e 9 PRs acrescentados a notas existentes, sem PR de produto da janela sem destino (FR-7426); os caminhos institucionais por teste (`tests/seguranca/test_novidades_na_entrada_institucional.py`)
- [x] T021 Período do histórico (P-4, respondida em 14/11: estender): 47 notas de 15/09 a 16/10, curadas em três frentes, e 26 PRs a mais no registro
- [x] T022 A diretriz do anúncio (`D-011`, FR-7427, UX-806): o campo `exemplo` ("Na prática"), os limites e o vocabulário na suíte, o guia reescrito com antes e depois, a convenção no `AGENTS.md`; as 109 notas reescritas e reunidas em 90
- [x] T024 Revisão editorial (`D-012`, `D-013`, FR-7601 a FR-7606, UX-821, UX-822): matriz das capacidades (`capacidades.md`), relevância em toda nota, `[[capacidade]]` e a vitrine, "faz parte de", a linha enxuta do incremental, o "Desde sua última visita" pela maior relevância, as "Pequenas melhorias" desfeitas, o kit separado, e as notas dos PRs de 14/11
- [x] T026 A vitrine retirada (`D-014`): a seção, os cartões, `[[capacidade]]` e o "faz parte de" saem; o arquivo só aceita `[[nota]]`; a primeira visita aponta "Comece por aqui" na Documentação do Sistema; a matriz e os textos dos cartões ficam em `capacidades.md` como estudo
- [ ] T023 Validação humana com alguém da comissão (SC-2501)
- [ ] T025 Decidir quem renumera a faixa repetida com a 169 (P-5)
