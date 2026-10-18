# Tasks: A folha comum da gestão em arquivo estático, sem mudar regra nenhuma

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[quickstart.md](quickstart.md)

**Tests**: incluídos — a rastreabilidade deste repositório é verificada por teste, e cada requisito
tem linha em [rastreabilidade.md](rastreabilidade.md). Caminhos relativos a `backend/`; os modelos
estão em `processo_seletivo/<app>/templates/`.

**Bloqueio**: nada da Phase 2 em diante começa antes de o PR #305 (`088`) estar na `main` — ele
acrescenta uma regra `@media print` à mesma folha. Antes de começar: `gh pr view 305 --json state`
e `git merge origin/main`.

## Phase 1: Setup

- [ ] T001 Conferir o merge do PR #305; `git merge origin/main`; banco do inventário próprio (`ps_inventario_089`, cópia do `ps_inventario_087`, `migrate --check` limpo), banco de teste próprio (`DB_NAME=ps_089`) e `uv sync --extra dev --extra assistente`. O `.claude/launch.json` não muda
- [ ] T002 Medir antes (R-008): o `len(corpo)` da Distribuição do guardião de escala, e `pesar.py` (novo, em `doc/inventario-visual-da-gestao-2026-10-16/`) para a Distribuição, a lista e Minhas Etapas no banco do inventário
- [ ] T003 [P] Inventário de antes em `depois-da-089/antes/` (expandida) e `depois-da-089/antes/recolhida/`, e a linha de ruído em `depois-da-089/ruido/` (uma segunda passada expandida, mesmo código); comparar `antes` com `depois-da-087/` por `comparar.py` e `medidas.py`
- [ ] T004 [P] `capturar_bases.py` (novo): a vitrine e a entrada do portal e a página de erro, a 1280 e a 375 px, em `depois-da-089/bases/antes/` e `depois-da-089/bases/ruido/`
- [ ] T005 [P] `pixels.py` (novo): diferença por PNG, contagem e intensidade máxima, classificada contra a linha de ruído (R-007)
- [ ] T006 Contar os atributos `style="` nos modelos, por aplicação, e registrar no R-005 (FR-2037)

## Phase 2: Foundational — a folha sai do modelo

- [ ] T007 Script de conversão em `depois-da-089/`: gera `interface/static/interface/gestao.css` e `shared/static/shared/tokens.css` a partir do modelo, comentários como `/* */`, com o tratamento do comentário que cita a sintaxe (R-001, R-002; FR-2030, FR-2033)
- [ ] T008 Script de equivalência: as regras de antes (modelo + parcial, sem `{% comment %}`) e as de depois (os dois `.css`, sem `/* */`) são iguais byte a byte, na ordem; nenhum comentário convertido fecha antes do fim (FR-2030, SC-795)
- [ ] T009 `shared/estaticos.py` com a tag `estatico` (resumo do conteúdo; recalculado com `DEBUG`, memorizado sem ele; arquivo ausente é erro) e o registro em `TEMPLATES.OPTIONS.libraries`; `STATICFILES_DIRS` com `shared/static` (R-001, R-003; FR-2034, FR-2035)
- [ ] T010 Testes da tag em `tests/interface/test_folha_estatica.py`: endereço estável com o mesmo conteúdo, novo com conteúdo novo sob `DEBUG`, erro com arquivo ausente (FR-2034)
- [ ] T011 `interface/base.html`: os dois `<link>` e o `<style>` só com o bloco e o comentário da `040`; `base_de_acesso.html`, `portal/base.html`, `404.html`: o `<link>` dos tokens no lugar do `{% include %}`; `_tokens.css.html` sai (R-004; FR-2031, FR-2032, FR-2036)
- [ ] T012 Testes em `tests/interface/test_folha_estatica.py`: as quatro bases carregam os tokens antes de qualquer `<style>`; a da gestão carrega a folha comum depois dos tokens e antes do estilo da página; nenhuma base contém regra da folha comum; o parcial não existe; os tokens são definidos num lugar só (FR-2031, FR-2032, SC-795)

## Phase 3: User Story 3 — os mesmos guardiões (P1)

**Goal**: cada teste que lia a folha no modelo lê o arquivo estático, ou a folha que a página aplica.

**Independent Test**: a mutação de cada linha do R-005 reprova o guardião.

- [ ] T013 [US3] Apoio comum em `tests/interface/folha.py`: `FOLHA_COMUM` e `TOKENS` (texto dos dois `.css`) e `folha_aplicada(corpo)` — as folhas externas do `<head>`, pelos finders, sem `/* */`, na ordem, mais os `<style>` do documento como estão (R-005, D-005). Em `test_acessibilidade.py`, `FONTE` se divide em modelo (marcação) e folha
- [ ] T014 [US3] Repontar, um a um, os 22 arquivos do R-005: os de texto para `FOLHA_COMUM`/`TOKENS`; os de folha renderizada e os de corpo inteiro (20–22) para `folha_aplicada`; a varredura de molduras de `test_telas_de_quem_elabora.py` passa a incluir `gestao.css` (FR-2038, FR-2039)
- [ ] T014a [US3] `test_estaticos.py`: guardião novo — nenhuma das seis marcas de sintaxe de modelo em `gestao.css` e `tokens.css` (FR-2043)
- [ ] T015 [US3] Mutação de cada guardião do R-005: violação plantada no `.css`, reprova; desfeita, passa — o resultado na coluna da tabela (SC-793)

## Phase 4: User Story 1 — as mesmas telas, mais leves (P1) 🎯

- [ ] T016 [US1] Medir depois (R-008), com o teto de 120.000 intacto (FR-2040, SC-791)
- [ ] T017 [US1] Inventário de depois nos dois estados da barra; `comparar.py`, `medidas.py` e `pixels.py` contra o antes e o ruído (FR-2041, SC-790)
- [ ] T018 [US1] Navegador a 1280 e 375 px; o cache da segunda página (SC-792); a impressão de uma tela com trilha, antes e depois (FR-2042)

## Phase 5: User Story 2 — sem cache velho (P1)

- [ ] T019 [US2] No runserver: editar a folha, recarregar, ver o `?v=` mudar e a regra nova; desfazer e ver o `?v=` voltar (FR-2034)

## Phase 6: User Story 4 — acesso, portal e erro (P2)

- [ ] T020 [US4] `capturar_bases.py` depois; `pixels.py` contra o antes e o ruído (FR-2041, SC-790)

## Phase 7: Polish & verificação

- [ ] T021 [P] Guia de implantação: `location` de `/static/shared/`, "JS e CSS", a nota da versão, a linha da lista de verificação (R-006; FR-2035)
- [ ] T022 [P] `doc/inventario-visual-da-gestao-2026-10-16.md`: a seção da `089`; AGENTS.md, se alguma frase disser que a folha é inline
- [ ] T023 Pesquisa: R-005 com a coluna da mutação, R-008 com os números, os achados; rastreabilidade conferida
- [ ] T024 `cd backend && LC_ALL=pt_BR.UTF-8 make lint check test-pg DB_NAME=ps_089 POSTGRES_USER=$USER`
- [ ] T025 Commit, PR contra a `main`, sem merge; nota no diretório de notas da sessão

## Dependências

T001 → tudo. T002–T006 antes de T007 (o "antes" é do código sem a mudança). T007–T012 antes de T013–T015.
T016–T020 depois de T014. T024 por último.
