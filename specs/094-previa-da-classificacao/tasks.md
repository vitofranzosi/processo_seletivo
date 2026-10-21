# Tasks: Prévia interativa da classificação — fatia 1

**Input**: Design documents from `specs/094-previa-da-classificacao/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: pedidos pela spec — a equivalência entre prévia e caminho oficial (FR-2233) e a ausência de
efeito (FR-2234) são requisitos, e a extração (FR-2232) só é segura com a linha de base escrita antes.

**Organization**: a Fase 2 é o motor — extração, irmã de `ordenar`, cenários e simulação —, e bloqueia
todas as histórias. Depois, uma fase por história, na ordem de prioridade da spec.

**O protótipo** (`prototipo/`) é a referência de comportamento e de desenho para as Fases 3 a 7: a
hierarquia, as frases, as marcas, o agrupamento e a folha foram validados nele, no navegador, em desktop
e 375 px — a segunda versão, de 19/10.

**Terceira rodada (19/10)**: a US6 (o processo inteiro) é P1 e entra no MVP; as tarefas T050 a T055 são
dela. **T003 a T009** — a extração e a equivalência — foram autorizadas à parte e estão **feitas**: PR
vitofranzosi/processo_seletivo#317, mergeado em 20/10 (`e7e22b89`). Da T034 e da T035 entrou só a
sentinela do lado oficial — com o caminho oficial alterado, a linha de base reprova —; o lado da prévia,
o `+1` na faixa e a matriz completa da equivalência dependem de `simular` (T013). A interface (Fases 3 a
8) espera a decisão do usuário.

**Segunda rodada (19/10)**: a US3 passou a P1 e vem logo depois da US2; as tarefas T040 e T044 a T049 são
da rodada de UX e estão nas fases a que pertencem, com numeração própria para não renumerar as referências
da matriz. As tarefas da primeira versão que a rodada alterou dizem isso no texto.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente)
- **[Story]**: a história da spec (US1 a US5)
- Caminhos relativos à raiz do repositório

---

## Phase 1: Setup

**Purpose**: ambiente e leitura do que já existe

- [x] T001 Preparar a worktree: `uv sync --extra dev` em `backend/`, `DB_NAME` próprio para a suíte (ver `CLAUDE.md`, "Um banco de teste por worktree"), e conferir `manage.py migrate --check` antes de qualquer teste
- [x] T002 Rodar o protótipo (`.claude/launch.json`, entrada `previa-094`) e percorrer a seção 1 de `specs/094-previa-da-classificacao/quickstart.md`, anotando as frases e marcas que a implementação reproduz

---

## Phase 2: Foundational — o motor (bloqueia todas as histórias)

**Purpose**: extrair a preparação do universo sem mudar o resultado oficial, dar a `ordenar` a irmã com
trajetória, e gerar e simular os cenários — tudo puro, testado antes da interface.

**⚠️ CRITICAL**: T003 precisa passar **contra o código de hoje**, antes de T006 e T007.

### Linha de base e testes, antes da extração

- [x] T003 Escrever a linha de base do caminho oficial em `backend/tests/integration/classificacao/test_previa_equivale_ao_oficial.py`: um apoio `persistir_cenario(edital, perfil, inscritos)` que grava os candidatos de cada cenário como `Inscricao` `SUBMETIDA`, `ResultadoEtapa` e `ValorDeFato` sobre um Edital publicado (fixtures de `backend/tests/fixtures/corte.py` e `edital.py`), chama `calcular_ordem` e congela `posicoes` (id, posição, `empate_residual`, ordem de `separado_por`), `sem_posicao` (id, `consequencia`, `motivo`) e `universo`; e um teste por cenário que compara com a tabela esperada. Deve passar no código atual
- [x] T004 [P] Testes unitários de `preparar` em `backend/tests/unit/classificacao/test_universo_classificavel.py`: eliminação mais recente pela `order` da Etapa; `SEM_PONTUACAO` com motivo nomeando as Etapas; marco só de portas (pontuação nula); `RegraIncompleta` sobe; ordem de entrada preservada; `recorte` filtra por `modalidade_id` e é idempotente sobre entrada já filtrada; `ELIMINADA` e `HABILITADA` iguais às de `ResultadoEtapa.Consequencia`
- [x] T005 [P] Testes unitários de `ordenar_com_trajetoria` em `backend/tests/unit/classificacao/test_ordenar_com_trajetoria.py`: para toda entrada da tabela-verdade de `backend/tests/unit/classificacao/test_desempate.py` e de `test_numeracao_e_ausencia.py`, `ordenar(...)` é igual à irmã sem `trajetoria` e `grupo_da_pontuacao`; a trajetória registra `nao_separou` para critério que não particiona (valores iguais e `CRITERIO_NAO_SE_APLICA` com ausente) e `separou` para o que particiona, na ordem de `order`

### Extração

- [x] T006 Criar `backend/processo_seletivo/classificacao/domain/universo_classificavel.py` com `ELIMINADA`, `HABILITADA` e `preparar(marco, etapas, inscritos, *, recorte=None)`, movendo de `classificacao/application/calculo.py` o laço de classificáveis e sem posição, `_eliminacao_mais_recente` e `_motivo_da_pontuacao_ausente`, sem mudar uma vírgula do comportamento (contrato em `contracts/universo-classificavel.md`)
- [x] T007 Refatorar `calcular_ordem` em `backend/processo_seletivo/classificacao/application/calculo.py` para montar `inscritos` (com `resultados` por inscrição, na ordem de hoje) e chamar `universo_classificavel.preparar(..., recorte=recorte)`; as consultas, o `order_by` dos `vigentes` e o filtro do recorte na consulta ficam onde estão. T003 e T004 verdes
- [x] T008 Em `backend/processo_seletivo/classificacao/domain/desempate.py`, criar `ordenar_com_trajetoria` sobre a partição de `_particionar` com o caminho registrado, e reescrever `ordenar` como a irmã sem as duas chaves novas. T005 e `test_desempate.py` verdes
- [x] T009 Rodar, sem alterar nenhum teste: `backend/tests/unit/classificacao/`, `backend/tests/integration/classificacao/`, `backend/tests/integration/ocupacao/`, `backend/tests/performance/test_ordenacao.py`, `test_corte.py`, `test_ocupacao.py` e `backend/tests/test_vigencia_do_resultado.py`. Qualquer diferença de contagem de consultas reprova a extração (SC-844)

### Cenários e simulação

- [x] T010 [P] Testes de `gerar` (os casos-limite) em `backend/tests/unit/classificacao/test_cenarios_da_previa.py`: determinismo (duas chamadas iguais); independência de pesos, operação, critérios, desfecho, Etapa governada e continuação (FR-2205); dependência de alvo, suplentes e vagas; âncoras de cada cenário (R-005); tamanho máximo 600; `modalidade_id` sempre nulo
- [x] T011 Criar `backend/processo_seletivo/classificacao/domain/cenarios_da_previa.py` com `CENARIOS` (chave, rótulo, descrição) e `gerar(...)` conforme R-005 e o `previa.cenario` do protótipo, devolvendo inscritos na forma de `preparar`
- [x] T045 [P] Testes de `populacao_estavel` em `backend/tests/unit/classificacao/test_cenarios_da_previa.py`: os mesmos candidatos e notas para as mesmas Etapas, fatos e fronteiras de montagem, **qualquer que seja a regra digitada** (SC-849); empate de dois na última vaga e na última posição da faixa, sem fusão quando as duas coincidem ou são vizinhas; trio separado só pelos fatos; os dois sem posição no fim, sem deslocar as posições plantadas; teto de 600 (FR-2205, FR-2243)
- [x] T046 Acrescentar `populacao_estavel(*, enumeradas, etapa_do_marco, alvo, faixa_total, vagas)` a `backend/processo_seletivo/classificacao/domain/cenarios_da_previa.py`, conforme R-005 e `prototipo/previa.py`; `simular` (T013) recebe `modo` e `populacao` (as fronteiras da montagem) e devolve `ancoras`, `fronteiras` e `consequencias` por candidato
- [x] T012 [P] Testes de `simular` em `backend/tests/unit/classificacao/test_previa.py`: a matriz do achado (R-007) linha a linha; desfecho não declarado devolve as duas consequências sem escolher (FR-2216); `alternativo` só quando o empate atravessa (FR-2217); `faltas` para alvo vazio, quadro sem linha geral, mais de quatro Etapas com nota, critério sem alvo e critério sem valor ausente declarado quando alguém não tem o valor (FR-2227); aviso das vagas não avaliado com corte recusado ou sem quadro (FR-2221); e `simular` com alvo 400 e 100 suplentes em todos os cenários abaixo de 1 s cada, medido com `time.perf_counter` (SC-841)
- [x] T013 Criar `backend/processo_seletivo/classificacao/application/previa.py` com `simular(marco, etapas, fatos, *, vagas, cenario)`: `faixa.normalizar`, `alvo_apurado`, `cenarios_da_previa.gerar`, `universo_classificavel.preparar`, `ordenar_com_trajetoria`, `faixa.calcular` (com o desfecho declarado e o outro), `apuracao.titulares_iniciais`; devolve a forma "Prévia" de `data-model.md`. Nenhuma consulta: quem chama entrega Etapas, fatos e vagas

- [x] T047 [P] Testes de `estado` e `comparar` em `backend/tests/unit/classificacao/test_previa.py`: a mudança de desfecho de `ADMITS_SURPLUS` para `STRICT` na população estável dá "corte: emitível → impedido na 15ª" e "progridem: 16 → 0"; suplentes de 5 a 0 sob `STRICT` dá "impedido na 15ª → impedido na 10ª" e nenhum candidato mudado; alteração sem efeito dá lista vazia; estados de populações ou modos diferentes não se comparam (FR-2244, SC-850)
- [x] T048 Acrescentar `consequencias`, `estado(prévia)` e `comparar(anterior, atual)` a `backend/processo_seletivo/classificacao/application/previa.py`, puras, com o estado serializado em texto curto (R-010)

**Checkpoint**: o motor está pronto, o caminho oficial é o mesmo de antes, e a prévia calcula sem interface.

---

## Phase 3: User Story 1 — Ver por que cada pessoa ficou onde ficou (Priority: P1) 🎯 MVP

**Goal**: o botão no cartão abre o painel fora dele, que começa pela consequência geral, mostra o
fluxo, os candidatos perto dos limites e a comparação de cada empate (segunda rodada).

**Independent Test**: com um marco por pontuação válido, o painel abre pela manchete; a tabela inicial
tem quatro colunas e as linhas de limite; cada empate tem a sua comparação; a ordem é a do caminho
oficial com os mesmos dados.

### Tests for User Story 1

- [x] T014 [P] [US1] Testes de interface em `backend/tests/interface/test_previa_da_classificacao.py`: o botão existe sob `POR_PONTUACAO` e não sob `POR_SORTEIO` nem sem forma (FR-2200); o painel é renderizado em `#painel-da-previa`, fora do `fieldset.marco` (FR-2201); o cartão não ganha texto visível além do rótulo do botão (FR-428 da `030`); o painel nomeia Perfil e marco e marca os candidatos como fictícios (FR-2204)
- [x] T015 [P] [US1] *(revista na segunda rodada)* Testes das linhas e da comparação em `backend/tests/interface/test_previa_da_classificacao.py`: a tabela inicial tem quatro colunas e nenhum parágrafo por linha (FR-2207, FR-2209); etiquetas "desempatado" e "empate não resolvido"; posição dividida "por N" e a seguinte pulada (FR-2208); linhas de limite no alvo, no fim da faixa e na última vaga, com "o empate atravessa esta linha" quando atravessa; agrupamento sem misturar consequências e com o plural certo (FR-2228); a classificação completa e a explicação técnica atrás de `<details>` (FR-2241); na comparação de um empate, os valores lado a lado, "separou: A › B = C", "não separou: valores iguais", "não se aplica: falta o valor de X" e "não chegou a ser usado" (FR-2210, FR-2242); o resultado do grupo e a linha que ele atravessa (FR-2226)
- [x] T040 [P] [US1] Testes da manchete e do fluxo em `backend/tests/interface/test_previa_da_classificacao.py`: a manchete vem antes de toda tabela, nas variantes emitível, impedido, sem desfecho, sem corte e corte que não alimenta Etapa (FR-2238); os três passos com seus estados; o ramo da continuação admitida, não admitida e não declarada; nenhum ramo quando o corte é impedido (FR-2239); "+1 além da faixa" com dois empatados na última posição (FR-2214); "a faixa passa dos N classificados" (FR-2246)

### Implementation for User Story 1

- [x] T016 [US1] *(revista na segunda rodada)* Criar `backend/processo_seletivo/interface/previa_da_classificacao.py` com a apresentação da saída de `simular`, na ordem de `prototipo/pagina.py` (`painel`): manchete, o que mudou, fluxo, ocupação, fronteira, empates, classificação completa, explicação técnica. A comparação dos empates lê a `trajetoria`, nunca reordena (FR-2211, D-014); a seleção de linhas relevantes segue R-011
- [x] T017 [US1] Acrescentar `fragmento_previa_da_classificacao` em `backend/processo_seletivo/interface/views.py` (autorização por `_edital_do_fragmento`, leitura por `forms.marco_do_formulario`, Etapas — com `weight`, `forma`, `order` e `name`, que `combinar` exige —, fatos declarados e quadro de vagas lidos do snapshot do rascunho por `publicacoes.application.publish_edital.edital_snapshot(edital)`, o mesmo que a etapa Classificação já monta em `views.py`; vagas por `classificacao.application.corte.linha_do_quadro(snapshot, perfil_id=…, lista_id=None)`. O snapshot se monta uma vez por pedido, e a contagem de consultas do fragmento fica presa por teste na T027) e as rotas `…/marco/<sub>/previa` e `…/previa/fechar` em `backend/processo_seletivo/interface/urls.py`
- [x] T018 [US1] Teste de negativa em `backend/tests/authorization/test_classificacao.py`: ator sem escopo sobre o Edital recebe a mesma recusa dos demais fragmentos da composição, e sem sessão também (FR-2235); e classificar o 404 de Edital fora do escopo do fragmento novo em `specs/033-navegacao-por-capacidade/inventario-das-negativas.md` (o guardião `backend/tests/test_gramatica_das_portas.py` varre `views.py` por AST)
- [x] T019 [US1] Criar `backend/processo_seletivo/interface/templates/interface/_previa_da_classificacao.html` (cabeça, seletor de candidatos, manchete, fluxo, ocupação, fronteira, empates, `<details>` da completa e da explicação) e acrescentar o botão "Simular classificação" ao fim do cartão em `backend/processo_seletivo/interface/templates/interface/_marco.html`, só sob `POR_PONTUACAO`, com `hx-include="closest fieldset"` e `hx-target="#painel-da-previa"`
- [x] T020 [US1] Acrescentar `<aside id="painel-da-previa">` e o `role="status"` do anúncio em `backend/processo_seletivo/interface/templates/interface/compor_classificacao.html`, irmãos da seção, fora de todo cartão
- [x] T021 [P] [US1] Criar `backend/processo_seletivo/interface/static/interface/telas/previa-da-classificacao.css` a partir de `prototipo/estatico/prototipo.css` (só as regras do painel, com os tokens de `shared/tokens.css`) e carregá-la pelo bloco `estilo_da_pagina` de `compor_classificacao.html`; toda classe do template com regra na folha; nenhuma `}}` na mesma linha (guardião de `test_estaticos`)
- [x] T022 [US1] Acrescentar `_previa_da_classificacao.html` à lista literal de `backend/tests/test_vocabulario_da_composicao.py` e conferir o vocabulário do painel contra o do cartão (FR-425 da `030`) e contra a tabela de D-012: nenhuma consequência "Suplente" nem "Dentro do alvo" em linha, e "suplentes" só como nome do campo (FR-2245)

**Checkpoint**: US1 entregue — o elaborador abre a prévia e lê o porquê de cada posição.

---

## Phase 3A: User Story 6 — O processo seletivo inteiro (Priority: P1, terceira rodada)

**Goal**: a visão principal é a jornada do Perfil, com os nomes cadastrados, o marco simulado aberto e
o resto descrito como contexto ou indeterminado; o detalhe da US1 a um clique.

**Independent Test**: num Perfil com quatro Etapas e dois marcos, a jornada lista tudo na ordem, só o
marco selecionado tem números, e nenhum ponto indeterminado mostra número.

- [x] T051 [P] [US6] Testes de `jornada` em `backend/tests/unit/classificacao/test_jornada.py`: a sequência do Perfil de quatro Etapas e dois marcos, com cada um deles selecionado; Etapa em dois marcos aparece uma vez; porta entre o corte e a Etapa alimentada; marco sem corte; marco terminal; marco por sorteio; Etapa fora de todo marco; o caso de marcos que se cruzam fora da ordem (R-013), preso como está (FR-2247, FR-2248, FR-2251, SC-852)
- [x] T050 [US6] Criar `backend/processo_seletivo/classificacao/domain/jornada.py` com `jornada(etapas, marcos, selecionado)`, pura, conforme R-013 e `prototipo/jornada.py`
- [x] T052 [P] [US6] Testes de interface em `backend/tests/interface/test_previa_da_classificacao.py`: o painel abre na jornada; os sete cenários de aceitação da US6; nenhum número em ponto indeterminado (SC-853); "até N" com porta; a nota de que a prévia dá nota fictícia a todos na Etapa alimentada por outro marco (FR-2249); a lista do que a prévia simula e do que não (FR-2254); o Perfil nomeado (FR-2255)
- [x] T053 [US6] O parâmetro `vista` (`processo` ou `detalhe`) e o `marco` no fragmento da T017, e o template `_jornada_da_classificacao.html`; os botões "Explorar classificação e desempate", "Voltar ao processo" e "Simular este marco", com o `hx-include` de cada um conforme `prototipo/pagina.py` (`ESTADO_DO_PAINEL`); o recálculo mantém a vista (FR-2252)
- [x] T054 [US6] As regras de folha da jornada em `backend/processo_seletivo/interface/static/interface/telas/previa-da-classificacao.css`, a partir de `prototipo/estatico/prototipo.css` (seção 8), e o foco no título em toda troca de vista, de volta ao botão do cartão certo ao fechar (`prototipo/estatico/prototipo.js`)
- [x] T055 [US6] O vocabulário de D-016 na jornada e no detalhe — "avança", "não avançaria nesta faixa", "poderiam participar", "posições adicionais (suplentes)", e "na faixa"/"fora da faixa" nos marcos terminais —, conferido pela T022 (FR-2253)

**Checkpoint**: o elaborador vê o processo, e aprofunda o marco quando quer.

---

## Phase 4: User Story 2 — Corte, progressão e recusas (Priority: P1)

**Goal**: situação no corte e consequência para a Etapa seguinte em cada linha; a recusa sob `STRICT`
como resultado; o aviso da fronteira das vagas.

**Independent Test**: a matriz do achado sai no painel igual ao que o motor produz.

### Tests for User Story 2

- [x] T023 [P] [US2] Testes do painel em `backend/tests/interface/test_previa_da_classificacao.py` para os oito cenários de aceitação da US2: as três linhas do achado nos dois desfechos; "a última da faixa, e não a do alvo" só com suplentes; nenhuma linha "progride" sob recusa (FR-2215); o grupo empatado com a mesma marca (FR-2212); "progride para a Entrevista", corte terminal, continuação admitida, não admitida e não declarada (FR-2213); marco sem corte (FR-2219); nenhum estado de sucesso com recusa ou aviso (FR-2222)
- [x] T024 [P] [US2] Teste de não-regressão do texto em `backend/tests/interface/test_previa_da_classificacao.py`: a opção `STRICT` do cartão continua "A faixa para no alvo" e `frases_do_corte` devolve as mesmas frases para o marco do achado (FR-2229); o painel diz "comportamento atual"

### Implementation for User Story 2

- [x] T025 [US2] *(revista na segunda rodada)* Implementar as consequências de D-012, o passo do corte no fluxo (emitível, impedido, depende do desfecho, não corta) com a comparação do outro desfecho na explicação técnica, em `backend/processo_seletivo/interface/previa_da_classificacao.py` e no template, com a cor âmbar da recusa (D-005)
- [x] T044 [US2] O bloco da apuração das vagas, separado do fluxo, tracejado, com o selo "hipótese", as três suposições e o que a prévia não simula (FR-2240, D-013); teste em `backend/tests/interface/test_previa_da_classificacao.py` de que ele nunca aparece como passo do fluxo
- [x] T026 [US2] Alvo do quadro: em `fragmento_previa_da_classificacao`, ler a linha geral por `linha_do_quadro(snapshot, perfil_id=…, lista_id=None)` sobre o `edital_snapshot` da T017 e dizer a origem; sem linha, `faltas` com "não apurável", nunca zero (FR-2218)

**Checkpoint**: US1 e US2 entregam o critério de sucesso do usuário sobre o que está digitado no clique.

---

## Phase 5: User Story 3 — Mudar um campo e ver o efeito sem salvar (Priority: P1 desde a segunda rodada)

**Goal**: recálculo a cada alteração, sobre a população estável, com o que mudou dito e marcado, e
nenhum efeito persistente.

**Independent Test**: alterar cada campo do marco recalcula sobre o digitado com os mesmos candidatos;
o quadro "O que mudou" acompanha; o banco não recebe escrita.

### Tests for User Story 3

- [x] T027 [P] [US3] Testes em `backend/tests/interface/test_previa_da_classificacao.py`: o contêiner de recálculo inclui o cartão, o cenário e as fronteiras; trocar operação, critério ou desfecho mantém os candidatos; trocar alvo, suplentes ou vagas traz a frase de reposicionamento (FR-2206); campo apagado devolve 200 com o que falta (FR-2227); o número de consultas do fragmento é constante entre recálculos e preso por `django_assert_num_queries` (SC-841)
- [x] T028 [P] [US3] Criar `backend/tests/integration/classificacao/test_previa_sem_efeito.py`: abrir, recalcular em todos os cenários, trocar cenário e fechar dentro de `CaptureQueriesContext` sem nenhum `INSERT`, `UPDATE` ou `DELETE`; contagem igual antes e depois em `Inscricao`, `ResultadoEtapa`, `ValorDeFato`, atos de ordenação, cortes, apurações e eventos de trilha; rascunho do Edital byte a byte igual (FR-2234, SC-843)

### Implementation for User Story 3

- [x] T049 [P] [US3] Testes em `backend/tests/interface/test_previa_da_classificacao.py`: o painel leva `populacao` e `anterior` ocultos; uma alteração do cartão mantém `populacao` e produz "O que mudou" com a marca "mudou" nas linhas certas; alteração sem efeito dá "a consequência não mudou para ninguém"; trocar entre população estável e caso-limite não compara; "Remontar para esta configuração" só aparece quando as fronteiras saíram da montagem, e não inclui a `populacao` antiga (FR-2243, FR-2244, FR-2246)
- [x] T029 [US3] *(revista na segunda rodada)* No template do painel, o contêiner com `hx-trigger="change from:#marco-<indice>-<sub>, input changed delay:400ms from:#marco-<indice>-<sub>"`, `hx-include` do cartão, do seletor de candidatos, da `populacao` e do `anterior`; o quadro "O que mudou"; o botão "Remontar"; e o estado "incompleto" (R-004, R-010)

---

## Phase 6: User Story 4 — Casos-limite para demonstração (Priority: P2)

**Goal**: escolher, no mesmo seletor da população estável, entre os cinco casos-limite; cada um diz o
que mostra, que acompanha a fronteira, e quando a situação não ocorre.

**Independent Test**: cada caso, na configuração de referência, produz a situação que o nomeia.

- [x] T030 [P] [US4] Testes dos cinco cenários de aceitação da US4 em `backend/tests/interface/test_previa_da_classificacao.py`, incluindo o trio sem critério por fato (dividem a posição) e "Classificação sem empate" dizendo que não houve empate em fronteira nenhuma
- [x] T031 [US4] Seletor de candidatos (população estável e o grupo "Caso-limite") com `hx-get` próprio, o aviso de que o caso acompanha a fronteira, descrição e âncora no painel, e as frases de "a situação não ocorre nesta configuração" (FR-2226) em `previa_da_classificacao.py` e no template

---

## Phase 7: User Story 5 — Celular e leitor de tela (Priority: P3)

**Goal**: 375 px sem rolagem horizontal; foco ao abrir e ao fechar; resumo anunciado.

**Independent Test**: a 375 px a jornada inteira sem rolagem horizontal; com leitor de tela, região
nomeada e resumo anunciado.

- [x] T032 [P] [US5] Criar `backend/processo_seletivo/interface/static/interface/previa-da-classificacao.js` (foco no título ao abrir pelo botão, de volta ao botão ao fechar; nada no recálculo), carregado com `defer` em `compor_classificacao.html`; acrescentá-lo onde `backend/tests/test_javascript.py` e `backend/tests/javascript/` exigem
- [x] T033 [P] [US5] Testes em `backend/tests/interface/test_previa_da_classificacao.py`: `aria-label` da região, `aria-controls` do botão, anúncio por `hx-swap-oob` fora do painel (FR-2236); nenhum `style=`, `<style>`, `<script>` inline nem `on*=` no HTML do painel e da etapa (FR-2237); a regra de 375 px pela folha, lida por CSSOM como em `backend/tests/interface/folha.py` (SC-846)

---

## Phase 8: Polish & Cross-Cutting

- [x] T034 Completar `backend/tests/integration/classificacao/test_previa_equivale_ao_oficial.py` com a matriz da FR-2233 (classificação, posições compartilhadas, critérios em ordem, valor ausente, corte com e sem suplentes, `ADMITS_SURPLUS`, recusa por `STRICT`, recusa da fronteira das vagas): o lado oficial persiste o cenário (apoio da T003), emite a ordem pelo comando de `backend/processo_seletivo/classificacao/application/emissao.py`, corta por `calcular_corte` e apura por `titulares_iniciais` sobre `progrediram_em_ordem`; o lado da prévia chama `simular` com os mesmos dados; um comparador devolve as diferenças
- [x] T035 Sentinela da equivalência no mesmo arquivo: com o caminho **oficial** alterado por `monkeypatch` — critério com sentido invertido em `calculo`, `+1` na faixa em `corte`, `ELIMINADA` trocada em `universo_classificavel` só do lado oficial —, o comparador de T034 devolve diferença em cada caso; e a tabela esperada do achado, absoluta, reprova se `faixa.calcular` mudar para os dois lados (FR-2233)
- [x] T036 [P] Escrever `specs/094-previa-da-classificacao/rastreabilidade.md` com cada FR e SC → tarefa → teste, completando a versão do PR da spec
- [x] T037 [P] Acrescentar a prévia ao `README.md` (seção da composição) e, em `CLAUDE.md`, a armadilha de que a prévia não grava nem lê inscrição real — só se a implementação a confirmar
- [x] T038 `cd backend && make lint check test-pg` verde; depois o roteiro 2 de `quickstart.md` no navegador do app, em desktop e 375 px, com captura
- [ ] T039 Validação humana: o roteiro de `specs/094-previa-da-classificacao/roteiro-de-compreensao.md` (SC-851, SC-848 e SC-840) **na interface real**, sobre o Edital de `ambiente-de-compreensao.py`, com ao menos cinco elaboradores, registrado em `specs/094-previa-da-classificacao/validacao-de-uso.md`. Não é tarefa de código, e fica pendente até o relato do usuário — testes técnicos não a substituem (autorização de 20/10)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (1)**: sem dependência.
- **Motor (2)**: depende do Setup. T003 antes de T006/T007; T004 e T005 antes de T006 e T008; T010 e
  T045 antes de T011 e T046; T011, T046 e T008 antes de T013; T012 antes de T013; T047 antes de T048.
  **Bloqueia todas as histórias.**
- **US1 (3)**: depende do motor.
- **US2 (4)**: depende de US1 (o painel e a view existem).
- **US6 (3A)**: depende de US1 (o fragmento e o detalhe existem); P1 desde a terceira rodada. T051
  antes de T050; T050 antes de T053.
- **US3 (5)**: depende de US1; é P1 desde a segunda rodada, e entra no MVP.
- **US4 (6)**, **US5 (7)**: dependem de US1; independentes entre si e da US3.
- **Polish (8)**: T034 e T035 dependem de T013; T038 depende de tudo.

### Within Each User Story

Testes primeiro, falhando; depois a implementação; o checkpoint fecha a história.

### Parallel Opportunities

- Fase 2: T004, T005, T010, T045 e T047 em paralelo (testes, arquivos distintos ou blocos distintos),
  enquanto T003 é escrito.
- US1: T014, T015, T040 e T021 em paralelo.
- Depois de US1: US3, US4 e US5 em paralelo, se houver mais de uma pessoa.
- Polish: T036 e T037 em paralelo com T034.

## Parallel Example: Fase 2

```text
Task: "T004 Testes unitários de preparar em backend/tests/unit/classificacao/test_universo_classificavel.py"
Task: "T005 Testes unitários de ordenar_com_trajetoria em backend/tests/unit/classificacao/test_ordenar_com_trajetoria.py"
Task: "T010 Testes de gerar em backend/tests/unit/classificacao/test_cenarios_da_previa.py"
```

## Implementation Strategy

### MVP

Fases 1 a 5, com a 3A — motor, US1, US6, US2 e US3. Desde a segunda rodada a US3 é P1: alterar um parâmetro e ver o
efeito sobre as mesmas pessoas é a proposta do simulador. A US2 é P1 porque sem ela o painel poderia
mostrar tudo verde onde o motor recusa — e isso é pior que nenhuma prévia (FR-2222).

### Incremental

1. Motor (Fase 2) → a suíte inteira verde, o caminho oficial igual.
2. US1 + US6 + US2 + US3 → MVP; validar no navegador com os três cenários de
   `prototipo/comparacao-v1-v2.md` e com o roteiro de `roteiro-de-compreensao.md`.
3. US4 → casos-limite; US5 → celular e leitor de tela.
4. Polish → matriz de equivalência completa, sentinela, rastreabilidade, `make lint check test-pg`.

### O que esta spec não implementa

Sorteio (D-007), recortes, concomitância, ocupação além do aviso e reversão (fatia 2, D-008),
Retificação (D-009). Nenhuma das pendências DP-1 a DP-4 é decidida por tarefa alguma.

---

## Notas da implementação (20/10)

Onde o código saiu diferente do texto da tarefa, e por quê. Nenhuma muda requisito.

- **T011, T046** — os nomes ficaram `caso_limite` e `populacao_estavel`, e o dicionário `CASOS`: desde a
  segunda rodada há população estável e casos-limite, e um `gerar` único misturava os dois.
- **T013** — a apuração das vagas chega a `simular` por parâmetro (`apurar_vagas`), e não por import:
  `tests/test_dependencia_da_ocupacao.py` proíbe `classificacao` de importar `ocupacao`. Quem a
  entrega é `interface/previa_da_classificacao.py`, que pode importar os dois.
- **T017** — a rota de fechar é `fragmentos/previa-da-classificacao/fechar`, e não uma filha da rota do
  marco: fechar não depende de Perfil nem de marco.
- **T019, T029, T053** — o `hx-include` é o cartão do **Perfil** (`#cartao-<indice>`), e não o
  `fieldset` do marco: a jornada precisa de todos os marcos do Perfil, e `marcos_do_formulario` os lê
  dali. A jornada mora no mesmo modelo do painel, e não num `_jornada_da_classificacao.html`.
- **T022** — nenhuma entrada nova na lista literal: o painel é `{% include %}` de
  `compor_classificacao.html`, que está na lista, e a varredura desce no `include`.
- **T028** — o teste ficou no arquivo de interface (`test_abrir_recalcular_e_fechar_nao_escrevem_nada`),
  com a captura de consultas e o rascunho comparado byte a byte; não há `test_previa_sem_efeito.py`.
- **T034, T035** — a equivalência roda seis casos-limite sobre Editais publicados com a regra de cada
  caso no marco (`montar_marco` ganhou `regra_de_corte`): ordem por `calcular_ordem`, ato pelo command,
  corte por `calcular_corte` e apuração por `titulares_iniciais`. As sentinelas desviam
  `calculo.ordenar`, `corte.faixa` e `ELIMINADA`. A tabela absoluta do achado, que reprova se
  `faixa.calcular` mudar para os dois lados, é a `MATRIZ` de `tests/unit/classificacao/test_previa.py`.
- **T037** — só o `README.md`. A armadilha de `CLAUDE.md` era condicional à implementação confirmá-la, e
  ela confirma o contrário: a prévia não lê inscrição real nem tem como gravar, e o teste da T028 o
  prende. Não há armadilha a registrar.
- **T038** — a suíte contra PostgreSQL acusou uma falha da prévia (moldura que rola sem posição, FR-1760
  da `083`), corrigida; os números estão na descrição do PR. No navegador, a validação real corrigiu
  três textos: o aviso das vagas no marco intermediário sem o "se" da D-006, "Linha do última vaga" e o
  espaço antes da vírgula na manchete.
