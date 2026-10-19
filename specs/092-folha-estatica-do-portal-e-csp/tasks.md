# Tasks: A folha do portal em arquivo, e o portal sob a política de segurança de conteúdo

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[quickstart.md](quickstart.md)

**Tests**: incluídos — a rastreabilidade é verificada por teste, e cada requisito tem linha em
[rastreabilidade.md](rastreabilidade.md). Caminhos relativos a `backend/`; "a pasta da prova" é
`doc/inventario-visual-da-gestao-2026-10-16/depois-da-092/`.

**Dependência**: a branch parte da do PR #308 (`091`), aberto em 18/10/2026. O PR desta feature mostra
os commits da `091` até ela ser mergeada.

## Phase 1: Setup

- [x] T001 Partir da branch do PR #308 (`git merge --ff-only`); conferir a faixa FR-2130+/SC-820+ na `main` e na branch; banco `ps_inventario_092` (cópia do `ps_inventario_091`), banco de teste `DB_NAME=ps_092`
- [x] T002 `preparar_rascunhos.py`: três rascunhos com a barra de documentos em 0, 50 e 100% no banco-modelo; cópias por passada
- [x] T003 [P] `capturar_portal.py`: rastrear as telas do portal e capturá-las, com medidas, regras aplicadas e violações; `IMPRESSAO=1` para o papel
- [x] T004 Antes, por `git archive` de `2615b738`: o portal, um par de ruído, as bases e o papel

## Phase 2: User Story 1 — o portal igual, sob a barreira (P1)

**Goal**: a folha fora do documento, o atributo em classe, a política em recusa.

**Independent Test**: o inventário antes e depois; o cabeçalho; as violações.

- [x] T005 [US1] `portal/static/portal/portal.css` com o `<style>` da base, um cabeçalho e as sete grafias; `<link>` pela `estatico` no `base.html` (FR-2130, FR-2131, FR-2132)
- [x] T006 [US1] `largura-0..100` no arquivo do portal; `_documentos.html` com a classe (FR-2134, FR-2135, D-004)
- [x] T007 [US1] `portal/portal.css` em `FOLHAS` (FR-2133)
- [x] T008 [US1] `shared/politica_de_conteudo.py`: recusa em todo HTML; sai a observação; o protótipo sem `em_observacao` (FR-2136, FR-2137, FR-2138, D-003)
- [x] T009 [US1] `equivalencia.py` contra `2615b738` (FR-2131, R-002)

## Phase 3: User Story 2 — os mesmos guardiões (P1)

**Goal**: nenhum guardião da folha do portal mais fraco.

**Independent Test**: a mutação.

- [x] T010 [US2] `tests/interface/folha.py`: `PORTAL_CSS`, `FOLHA_DO_PORTAL`
- [x] T011 [US2] Repontar os guardiões do R-004: acessibilidade (os dois canais e a do portal), polish 055 e 057, comprovante, envio de arquivo, peso da vitrine, cronograma, estáticos, citações (FR-2139, FR-2140)
- [x] T012 [US2] Guardiões novos: a barra pela classe, as 101 classes do portal, a base carrega o arquivo, estilo embutido em todo modelo, todo HTML em recusa, nenhuma observação, o protótipo (FR-2134, FR-2135, FR-2136, FR-2137, FR-2141)
- [x] T013 [US2] `mutacoes.py`: uma mutação ou mais por guardião; todas reprovam, e sem mutação passam (SC-823)

## Phase 4: User Story 3 — o protótipo e as páginas fora das áreas (P2)

- [x] T014 [US3] O protótipo e a página de erro na raiz em recusa, no teste e no inventário (FR-2136, FR-2137)

## Phase 5: Polish

- [x] T015 Depois: o portal, um par de ruído, as bases e o papel; `medidas.py`, `pixels.py`, violações (FR-2142, FR-2143, SC-820, SC-822)
- [x] T016 [P] O peso, `pesar_portal.py` (FR-2144, SC-825)
- [x] T017 Pesquisa completa: R-001 a R-007; README com a linha da `092`
- [x] T018 `make lint check test-pg DB_NAME=ps_092 POSTGRES_USER=$USER` (SC-824)
- [x] T019 Commit e PR contra a `main`, sem merge; `/code-review` e correção dos achados confirmados
