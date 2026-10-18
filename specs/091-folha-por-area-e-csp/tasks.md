# Tasks: A folha da gestão por área, o estilo de cada tela em arquivo, e a política de segurança de conteúdo

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[quickstart.md](quickstart.md)

**Tests**: incluídos — a rastreabilidade é verificada por teste, e cada requisito tem linha em
[rastreabilidade.md](rastreabilidade.md). Caminhos relativos a `backend/`; os modelos estão em
`processo_seletivo/<app>/templates/`; "a pasta da prova" é
`doc/inventario-visual-da-gestao-2026-10-16/depois-da-091/`.

**Bloqueio, resolvido**: nada da Phase 2 em diante começava antes de o PR #307 (`090`) estar na `main` —
ele muda a regra `.salvar` da mesma folha. Mergeado em 18/10/2026 (`69c6ac1c`), e trazido para a branch
por `git merge origin/main` antes de qualquer mudança de código; o inventário de antes saiu desse
estado.

## Phase 1: Setup

- [x] T001 Conferir o merge do PR #307 (`gh pr view 307 --json state`); `git merge origin/main`; banco do inventário `ps_inventario_091` (cópia do `ps_inventario_089`, `migrate --check` limpo), banco de teste `DB_NAME=ps_091`, `uv sync --extra dev --extra assistente`. O `.claude/launch.json` não muda
- [x] T002 Medir antes (R-012): `pesar.py` para a Distribuição, a lista, Minhas Etapas e a visão geral; o `len(corpo)` do guardião de escala
- [x] T003 [P] Inventário de antes nos dois estados da barra, com `ESTILOS=1`, mais pares de ruído; `capturar_bases.py` (identificação, erro, vitrine e entrada do portal); `imprimir.py` da `088`
- [x] T004 [P] `capturar.py` ganha `VIOLACOES=1`: escuta `securitypolicyviolation` desde o início da página e lê o console; grava por variante no `resultados.json`; o `comparar.py` acusa (R-011). Exercitado contra uma página com política e um `style=""` plantados
- [x] T005 [P] `estilos.py`/`medidas.py`: as regras aplicadas comparadas também como conjunto (R-003)
- [x] T006 Classificar os 31 arquivos de teste candidatos do R-010 — o que leem, se ficam silenciosos sem repontar, a mutação de cada um — e registrar a tabela no R-010

## Phase 2: User Story 2 (parte B e C) — o estilo das telas em arquivo (P1)

**Goal**: nenhum `<style>` nem `style=""` nos modelos da gestão e da página de acesso; cada tela carrega só o seu estilo.

**Independent Test**: os guardiões de embutido e de carga por tela; o inventário sem mudança.

- [x] T007 [US2] Os cinco parciais viram `interface/static/interface/telas/{acesso,terminais,vista,lista-exigida,aviso}.css`, comentários como `/* */`; os parciais saem (FR-2095)
- [x] T008 [US2] Os blocos das 22 telas com regras próprias viram `telas/<tela>.css`; o bloco `estilo_da_pagina` passa ao `<head>`, com `<link>` pela `estatico`, parcial antes do próprio; o `<style>` sai de `base.html` e `base_de_acesso.html`; o comentário da `040` fica no modelo com a nota (FR-2096, FR-2097, R-006)
- [x] T009 [P] [US2] O fragmento do protótipo: `telas/prototipo-do-assistente.css` e `<link>` no fragmento (FR-2099)
- [x] T010 [P] [US2] `404.html`: `shared/static/shared/erro.css` (FR-2100)
- [x] T011 [US2] Os `style=""`: a classe do `<svg>` dos símbolos; `largura-0..100` e `altura-0..100`, terminadas em `%;}`, para Minhas Etapas e a série (FR-2101, D-005, R-007)
- [x] T012 [US2] `shared/estaticos.py`: a verificação de sistema confere todo `{% estatico %}` dos modelos (R-006)
- [x] T013 [US2] Testes em `tests/interface/test_folha_estatica.py`: cada arquivo de `telas/` só nas telas que o citam, toda tela que tinha bloco carrega o seu, ordem comum → grupo → próprio, o fragmento e o 404 (FR-2095, FR-2096, FR-2099, FR-2100, SC-815)
- [x] T014 [US2] As duas telas do assistente: o comum num arquivo, o que difere em cada uma, com a prova de ordem (FR-2098, D-003)

## Phase 3: User Story 2 (parte A) — a folha comum por área (P1)

**Goal**: sete arquivos por área, na ordem de carga, sem duplicadas, sem mudar o vencedor de nenhuma propriedade.

**Independent Test**: `ordem.py` e `equivalencia.py` limpos; o inventário sem mudança.

- [x] T015 [US2] `ordem.py` na pasta da prova: pares que trocam de ordem, propriedades expandidas pelo CSSOM, elementos nas páginas do inventário (R-003)
- [x] T016 [US2] `areas.py`: a área de cada regra da folha comum; gera `interface/static/interface/gestao/*.css` com os comentários junto da regra; as regras que a prova devolve ao lugar ficam fora da área e vão para o R-002 (FR-2090, FR-2091, FR-2094)
- [x] T017 [US2] `equivalencia.py` (as duplicadas, página a página, e a equivalência das regras): os pares iguais na folha comum e nos estilos de tela; a remoção de cada um com a prova de ordem; a lista no R-005 (FR-2093, SC-816)
- [x] T018 [US2] `shared/estaticos.py`: `FOLHAS_DA_GESTAO` e `{% folhas_da_gestao %}`; `base.html` usa a tag; `gestao.css` sai; `estaticos.E001` confere a lista (FR-2092, D-002)

## Phase 4: User Story 3 — os mesmos guardiões (P1)

**Goal**: cada guardião lê o arquivo novo ou a folha aplicada, e reprova a violação plantada nele.

**Independent Test**: a mutação de cada linha do R-010 reprova o guardião.

- [x] T019 [US3] `tests/interface/folha.py`: `FOLHA_COMUM` é a concatenação da lista, na ordem; um apoio para o texto do arquivo de uma tela (R-010)
- [x] T020 [US3] Repontar, um a um, os guardiões que a T006 classificou (FR-2110)
- [x] T021 [US3] `test_estaticos.py`: a varredura de sintaxe de modelo alcança `gestao/`, `telas/` e `shared/erro.css` (FR-2111)
- [x] T022 [US3] `mutacoes.py` na pasta da prova: uma mutação por linha do R-010, mais as dos guardiões novos; `mutacoes.txt` com o resultado (SC-813)

## Phase 5: User Story 1 — a política (P1)

**Goal**: a política em modo de recusa em todo HTML da gestão; em observação no resto; nada embutido.

**Independent Test**: o cabeçalho na suíte; o console de cada tela do inventário.

- [x] T023 [US1] `shared/politica_de_conteudo.py`: a constante e o `PoliticaDeConteudoMiddleware`, primeiro da lista em `config/settings/base.py` (FR-2103, FR-2104, FR-2105, FR-2108, R-008)
- [x] T024 [US1] O `<meta name="htmx-config">` em `interface/base.html` e `portal/base.html` (FR-2107, D-009)
- [x] T025 [US1] `tests/interface/test_politica_de_conteudo.py`: o cabeçalho em tela, fragmento htmx, acesso, recusa e página de erro sob `/gestao/`; `-Report-Only` no portal; nada em JSON, PDF, `/health`; nada sob `DEBUG` em 404 e 500; nenhuma diretiva `unsafe-`; o `X-Frame-Options` igual (FR-2103 a FR-2109, FR-2112)
- [x] T026 [US1] Os guardiões de embutido no mesmo arquivo: nenhum `<style>`, `style=`, `<script>` sem `src`, `on*=` ou `javascript:` nos modelos; nenhum script escreve o atributo `style` (FR-2097, FR-2101, FR-2106, SC-811)
- [x] T027 [US1] O guia de implantação: a nota de que o nginx não acrescenta política, e o `curl -I` na lista de verificação (FR-2108)

## Phase 6: User Story 4 — o portal, a página de acesso e a de erro (P2)

- [x] T028 [US4] O R-007 completo com o que o portal ainda tem (FR-2102); o inventário das bases mostra no portal só as violações previstas, em observação

## Phase 7: Polish & Cross-Cutting

- [x] T029 Medir depois (R-012) e comparar: inventário, pixels contra os pares de ruído, regras aplicadas como conjunto, impressão, bases, violações (SC-810, SC-812, SC-817)
- [x] T030 Os números na pesquisa; a linha da `091` no README; a nota da sessão na pasta compartilhada
- [x] T031 `cd backend && make lint check test-pg DB_NAME=ps_091 POSTGRES_USER=$USER` com `LC_ALL=pt_BR.UTF-8`
- [x] T032 Commit e PR contra a `main`, sem merge; `/code-review` no PR, sem `--comment`; corrigir os achados confirmados; CI verde

## Dependencies

- T001 antes de tudo; T002–T006 antes de mudar código.
- Phase 2 (B, C) antes da Phase 3 (A): as telas saem do documento primeiro, e a prova de ordem da A
  já compara a folha comum com os arquivos de tela no lugar final.
- Phase 4 acompanha as Phases 2 e 3 — cada guardião é repontado quando o que ele lê muda.
- Phase 5 depois das Phases 2 e 3: a política recusaria o que elas tiram.
- Se a Phase 5 crescer, ela vira um segundo PR, aberto a partir do primeiro (R-013).
