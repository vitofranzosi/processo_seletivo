# Tasks: A organização da lista de Processos Seletivos (129)

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/tela-da-lista.md](contracts/tela-da-lista.md)

**Tests**: pedidos pela spec (Independent Test de cada história, SC-1311 a SC-1314); escritos antes ou
junto da implementação de cada fase.

## Phase 1: Setup

- [X] T001 Conferir que a `127` está na `main` (`interface/andamento.py`, cartão "O que fazer agora" em `backend/processo_seletivo/interface/templates/interface/_providencias.html`) e que a worktree parte de `origin/main` (Assumptions)
- [X] T002 Entrada `lista-129` em `.claude/launch.json` (porta 8129, banco `ps_129_demo`, seletor ligado), sem tocar nas entradas existentes (quickstart)

## Phase 2: Foundational — o recorte e a busca no seletor (R-1, R-2, R-3)

- [X] T003 [P] Testes em `backend/tests/integration/processos/test_recorte_dos_processos.py`: o grupo de cada combinação Processo × Editais (ativo com todos encerrados; encerrado com Edital publicado; cancelado com Edital em elaboração; sem Edital); a partição das três abas; a ordem `-created_at, -id`; a busca por título, código, título de Edital, "N/AAAA", "N", número com zero à esquerda, "90/" e "/2026" como texto, só espaços; outra unidade não aparece; as contagens por grupo e as da busca numa consulta só (FR-4301, FR-4302, FR-4306 a FR-4308)
- [X] T004 `listar_processos(actor=, situacao=, busca=)`, `grupo_do_processo`, `busca_de_processos` e `contar_por_situacao(actor=, busca=)` em `backend/processo_seletivo/processos/application/selectors.py`
- [X] T005 [P] Testes puros em `backend/tests/unit/interface/test_lista_de_processos.py`: leitura dos parâmetros (aba inválida, busca com espaços, página texto/zero/negativa/além da última), o intervalo "1–20", os links de página com aba e com busca codificada, as frases do recorte e da busca no singular e no plural (FR-4309, FR-4310, FR-4312, FR-4314, FR-4315)
- [X] T006 `backend/processo_seletivo/interface/lista_de_processos.py`: `recorte_de`, `Pagina`, `paginar`, `frase_do_recorte`, `frase_da_busca`, as abas com contagem (R-4, R-10)

## Phase 3: User Story 1 — o que está em andamento, 20 por vez (P1)

- [X] T007 [US1] Testes em `backend/tests/interface/test_organizacao_da_lista.py`: o padrão abre "Em andamento" com `aria-current`; os cenários 1–6 da US1 (o ativo com Editais encerrados, o encerrado com Edital publicado e o selo real, 61 Processos → "61 Processos, mostrando 1–20" e a navegação, troca de aba volta à página 1, o endereço reproduz o recorte); aba vazia; unidade vazia; parâmetros inválidos sem erro; o subtítulo com o nome da Unidade; a ordem de leitura faixa → Novo → abas → busca → frase → Processos → paginação (FR-4300 a FR-4304, FR-4311 a FR-4316, FR-4321, FR-4322, UX-270, UX-272)
- [X] T008 [US1] A view `lista` em `backend/processo_seletivo/interface/views.py`: lê o recorte, a agregação, a página e **os Editais da unidade inteira**; agrupa os da página por Processo; tira a coluna, o resumo e o total de Editais; o subtítulo pela Unidade (FR-4321, FR-4322, R-5, R-8)
- [X] T009 [US1] As abas, a frase do recorte, a lista e a paginação em `backend/processo_seletivo/interface/templates/interface/lista.html`, e o partial `backend/processo_seletivo/interface/templates/interface/_paginacao.html` (UX-270, UX-272)
- [X] T010 [US1] Regras das classes novas em `backend/processo_seletivo/interface/static/interface/telas/lista.css`: abas com traço visível na atual, contagem, busca, frase (CSP: nada inline)

## Phase 4: User Story 2 — a faixa independe do recorte (P1)

- [X] T011 [US2] Testes na mesma `test_organizacao_da_lista.py`: recurso aguardando num Edital de Processo encerrado aparece na faixa de quem julga em "Em andamento"; a faixa idêntica (chaves, ordem, total) nas quatro abas, numa busca e em duas páginas, para julgador, elaborador e gestor; o Edital em elaboração da página 2 aparece na faixa da página 1 (FR-4323, FR-4326, SC-1312)
- [X] T012 [US2] `trabalho.do_ator` sem `contagens`, alimentado pelos Editais da unidade, em `backend/processo_seletivo/interface/trabalho.py` e na view (R-5, R-6)

## Phase 5: User Story 3 — a busca em todas as situações (P1)

- [X] T013 [US3] Testes na mesma `test_organizacao_da_lista.py`: os cenários 1–6 da US3 a partir de "Em andamento" (o cancelado por "90/2026" com o selo; "90/2026" × "90"; a ordem andamento → encerrados → cancelados e nenhuma aba marcada; a frase com a contagem dos encerrados ou cancelados e "Limpar a busca"; outra unidade; sem resultado, com o texto no campo); a paginação da busca preserva o termo; o título de Edital traz o Processo com todos os Editais; SC-1311 para cada Processo do cenário (FR-4305 a FR-4310, UX-271, UX-273)
- [X] T014 [US3] O formulário da busca e a frase da busca em `backend/processo_seletivo/interface/templates/interface/lista.html`, com regras em `telas/lista.css`

## Phase 6: User Story 4 — a linha diz fatos, e não ações (P2)

- [X] T015 [US4] Testes na mesma `test_organizacao_da_lista.py`: para cada papel de `PAPEIS`, nenhuma linha traz `class="acao` de Edital, contador, "Nenhuma ação disponível", tabela ou cabeçalho de coluna; a marca da Retificação em revisão com "aguarda quem homologa" e link; Comissão e Alocação para quem gere sem integrar; o título igual ao do Processo não se repete; a paridade nova faixa × detalhe (FR-4317 a FR-4320, FR-4329, SC-1314, UX-274, R-9, R-11)
- [X] T016 [US4] A linha compacta V1 em `lista.html` (sem `table`; `ul` de linhas de Edital; o título só quando difere; a marca com "aguarda" sempre que houver passo) e as regras da linha e do estreito em `telas/lista.css` (FR-4318, FR-4320)
- [X] T017 [US4] Sair o que só a coluna usava: `contagens_da_lista`, `para_a_lista`, `CONFERIDOS_NO_DETALHE`, `da_linha`, `FREQUENTES`, os parâmetros `contagens` e `com_relatorio` em `backend/processo_seletivo/interface/acoes.py`; `backend/processo_seletivo/interface/templates/interface/_acao_de_linha.html`; as regras `.acoes>*+.terminais`, `.acao.zerada`, `.acao.principal-da-linha` (R-6)
- [X] T018 [US4] Ajustar os testes que prendiam a coluna, conforme *Compatibilidade*: `backend/tests/interface/test_acoes.py` (paridade e Cancelar), `test_polish_da_057.py` (T1), `test_polish_da_055.py`, `test_lista.py` (contagem, permissão, estrutura, plural, ação indisponível), `test_acoes_disponiveis.py` (casos D e a coluna) (R-12)

## Phase 7: User Story 5 — a nota de cobertura antes dos itens (P2)

- [X] T019 [US5] Testes: a nota vem depois do `h2` e antes do primeiro item e nomeia as oito famílias e "O que fazer agora"; a frase vazia nomeia as mesmas, da mesma constante, em `backend/tests/unit/interface/test_trabalho_do_ator.py` e `test_organizacao_da_lista.py` (FR-4324, FR-4325)
- [X] T020 [US5] `FORA_DA_FAIXA` e `COBERTURA` em `backend/processo_seletivo/interface/trabalho.py`; a nota subida e a frase vazia em `backend/processo_seletivo/interface/templates/interface/_acoes_disponiveis.html`; a regra de `.cobertura-da-faixa` em tamanho de texto (R-7)

## Phase 8: User Story 6 — o custo constante para todo papel (P3)

- [X] T021 [US6] `backend/tests/performance/test_lista_em_escala.py`: para cada papel de `identidade.PAPEIS` e para todos juntos, as consultas da lista são as mesmas com 3, 30 e 300 Editais com inscrição, parte declarando Requerimento de Matrícula, espalhados em Processos de várias situações; e as mesmas entre duas abas, uma busca e duas páginas (FR-4327, FR-4328, SC-1313)
- [X] T022 [US6] Ajustar `backend/tests/performance/test_trabalho_em_escala.py` se a medida da lista mudar de forma, mantendo o que ele prende (104)

## Phase 9: Polish

- [X] T023 Rodar a suíte e ajustar os testes que liam a coluna, a tabela ou um Processo encerrado na página padrão; registrar cada um em `verificacao.md`
- [X] T024 `cd backend && DB_NAME=ps_129 make lint check test-pg`; `migrate --check` sem migration nova
- [X] T025 Verificação no navegador, a 1280 e a 375 px, como gestor e como julgador, com capturas em `specs/129-organizacao-da-lista-de-processos/capturas/` e a medida em telas (SC-1310)
- [X] T026 `rastreabilidade.md` (todo FR-, SC-, UX- e D- da spec), `verificacao.md` (com o SC-1315, de validação humana, como pendente) e a linha da `129` no README
- [ ] T027 Revisão independente por subagente; corrigir os achados
- [ ] T028 PR sem merge; conferir o CI

## Dependencies

- T003–T006 antes de toda história. T008 antes de T009–T018.
- US1, US2 e US3 compartilham a view e o template; fazê-las em sequência (T007 → T014).
- US4 (T015–T018) depois de US1: a linha nova substitui a tabela que US1 ainda pode ler.
- US5 é independente das demais (constante e partial da faixa).
- US6 depois de US4: a medida só fica constante sem a coluna.
- T023 depois de T018 e T020.

## Parallel opportunities

- T003 e T005 (arquivos distintos, sem dependência).
- T019–T020 (US5) em paralelo a US3 ou US4.

## Implementation strategy

MVP: Phases 1–4 (recorte, paginação e a faixa sobre a unidade). Depois US3 (busca), US4 (a linha V1 e o
código que sai), US5 (a nota) e US6 (o teste de escala). Uma branch, um PR.
