# Tasks: A detecção do giro do rosto na gravação do vídeo

**Input**: [plan.md](plan.md), [research.md](research.md) (`T-001` a `T-012`),
[data-model.md](data-model.md), [contracts/pagina.md](contracts/pagina.md), [quickstart.md](quickstart.md),
[spec.md](spec.md)

**Andamento (15/11)**: implementadas, sem merge. O motor desceu da 1.2.0 do plano à 0.10.35 (T-013: a
1.x manda telemetria). A suíte inteira, com `DB_NAME=ps_176` e os grupos `assistente` e `navegador`,
fechou em 21 450 passando, 14 pulados e 1 falha — a tabela de incrementos do README, corrigida e
conferida em seguida. Abertos: a câmera real e o celular de entrada (SC-2753, SC-2757, T027 em parte),
porque o painel do app bloqueia a câmera e o Claude in Chrome não estava conectado; e a P-13. O T028
não pediu mudança: os pulados são os mesmos 14.

**Tests**: pedidos pelo plano. Cada peça vem com o seu teste, no mesmo commit. A suíte roda contra
PostgreSQL, com `DB_NAME=ps_176`, e por diretório enquanto se trabalha. **Nenhum arquivo de
`tests/integration/verificacao/`, `tests/unit/verificacao/` nem dos testes de contrato da `166` muda**:
eles são a prova da FR-8030.

Os caminhos são relativos a `backend/`, salvo os de `doc/` e de `specs/`.

## Phase 1: Setup

- [x] T001 Preparar o banco de teste da worktree (`DB_NAME=ps_176`), conferir `manage.py migrate --check`, e rodar a linha de base: `tests/portal`, `tests/test_sem_inferencia_sobre_o_video.py`, `tests/interface/test_politica_de_conteudo.py` e `node --test tests/javascript/gravacao.test.js`, guardando a contagem
- [x] T002 Copiar do pacote `@mediapipe/tasks-vision` 0.10.35 (a 1.2.0 do plano trazia o registrador de uso, T-013), sem alteração, `vision_bundle.mjs`, `wasm/vision_wasm_internal.js` e `wasm/vision_wasm_internal.wasm` para `processo_seletivo/portal/static/portal/deteccao/tasks-vision-0.10.35/`, o texto da licença Apache 2.0 para `deteccao/LICENSE-2.0.txt`, e o `face_landmarker.task` float16/1 para `processo_seletivo/portal/static/portal/deteccao/face_landmarker-float16-1.task`, anotando o SHA-256 de cada um (T-001, T-002)

## Phase 2: Foundational

**Purpose**: a chave, o manifesto, a política e o guardião, de que todas as histórias dependem.

- [x] T003 Criar `processo_seletivo/portal/deteccao.py` com `VERSAO_DO_MOTOR`, `ARQUIVOS` (caminho estático → SHA-256), `GIRO_DO_PASSO` (`perfil-esquerdo` → `esquerda`, `perfil-direito` → `direita`) e `ligada()` (as duas chaves), com o docstring da decisão (D-001, D-004)
- [x] T004 Acrescentar `VERIFICACAO_DETECCAO_DO_GIRO` a `config/settings/base.py` (do ambiente, desligada), a recusa em `config/settings/production.py` nomeando a P-0 e a P-13, e `VERIFICACAO_DETECCAO_DO_GIRO = False` em `config/settings/test.py` (T-009, FR-8020, FR-8021)
- [x] T005 Acrescentar `compilar_wasm=False` a `com_midia_local` em `processo_seletivo/shared/politica_de_conteudo.py`, com `script-src 'self' 'wasm-unsafe-eval'` só quando `True`, e o comentário da T-004 (FR-8022)
- [x] T006 [P] Testes em `tests/portal/test_deteccao_do_giro.py`: cada arquivo do manifesto existe e tem o resumo registrado; as chaves de `GIRO_DO_PASSO` estão em `roteiro.CHAVES`; `ligada()` exige as duas chaves; a produção recusa a chave (no mesmo desenho dos testes de recusa de `production.py`); a política com `compilar_wasm` difere da de hoje só em `'wasm-unsafe-eval'` (FR-8020 a FR-8023)
- [x] T007 Ampliar `tests/test_sem_inferencia_sobre_o_video.py` com os três casos da T-011: os arquivos do motor são só os do manifesto; nenhum outro estático cita `tasks-vision`, `FaceLandmarker` ou `mediapipe`; nenhum template além de `portal/verificacao.html` carrega `deteccao.js` ou o motor; e atualizar o docstring para a revisão da D-001 (FR-8024)
- [x] T008 Rodar `tests/test_armazenamento_no_navegador.py` e `tests/interface/test_politica_de_conteudo.py`, que passam a ler o carregador copiado; se algum recusar o arquivo do pacote, registrar o motivo e decidir com o usuário antes de excluir o arquivo do guardião

**Checkpoint**: a chave existe e é recusada em produção; o motor está no lugar e conferido; nada aparece na página ainda.

## Phase 3: User Story 1 — Gravar os perfis sem tocar na tela (P1) 🎯 MVP

**Goal**: com a chave ligada e o motor carregado, os dois perfis avançam sozinhos.

**Independent Test**: a imagem de teste com a detecção simulada (T-010) e a câmera real no computador, contando os toques.

- [x] T009 [P] [US1] Criar `processo_seletivo/portal/static/portal/deteccao.js` com as funções puras da `contracts/pagina.md` — `giroDosPontos`, `caixaDosPontos`, `rostoNoOval`, `avaliarGiro`, `Orcamento`, `podeCarregar` — e as constantes no topo, no desenho de `gravacao.js` (`window.DeteccaoDoGiro` e `module.exports`) (T-005 a T-008)
- [x] T010 [P] [US1] Testes em `tests/javascript/deteccao.test.js`: o sinal do giro (esquerda da pessoa positiva, com pontos sintéticos de um rosto virado), o rosto no oval com prévia espelhada e `cover`, o relance que não conta, o lado oposto, a leitura sem rosto que interrompe, o orçamento que desliga na quinta leitura lenta, `podeCarregar` com `saveData` e sem `WebAssembly`
- [x] T011 [US1] Acrescentar a `deteccao.js` o `Vigia`: carrega o módulo por `import()` com o conjunto de arquivos explícito e `isSimdSupported`, cria o `FaceLandmarker` (`VIDEO`, um rosto, `GPU` e depois `CPU`), lê a cada `INTERVALO` só quando `observar()` pede e a página está visível, mede cada leitura no `Orcamento`, guarda no máximo 20 leituras, escreve `data-deteccao`, e `parar()` cancela o laço e fecha o motor (T-003, T-008, FR-8003, FR-8016, FR-8017)
- [x] T012 [US1] Em `processo_seletivo/portal/verificacao.py`, passar ao template `deteccao` (os quatro endereços com `estatico` e o `GIRO_DO_PASSO`) quando `deteccao.ligada()`, e chamar `com_midia_local(resposta, compilar_wasm=deteccao.ligada())`
- [x] T013 [US1] Em `processo_seletivo/portal/templates/portal/verificacao.html`, com a detecção: os `data-deteccao-*` em `[data-verificacao]`, o `data-giro` nos passos de perfil, o `[data-aviso-deteccao]` no topo de `.preparo-do-palco` (frase e "Prefiro avançar só tocando"), o `[data-ajuda-deteccao]`, o `[data-confirmacao]` dentro de `.instrucao-do-passo`, todos `hidden`, e o `<script>` de `deteccao.js` antes do de `gravacao.js`; sem a chave, o HTML de hoje (contracts/pagina.md)
- [x] T014 [US1] Em `processo_seletivo/portal/static/portal/gravacao.js`, os ganchos: depois de `entrarNoPalco`, criar o `Vigia` (se `DeteccaoDoGiro` existir e a página tiver os endereços) e observar o oval; em `desenharPassos`, observar o lado do passo ou nada; `aoRosto` muda `data-rosto` e a frase do guia; `aoGiro("visto")` mostra a confirmação, anuncia e chama `avancar()` depois de `CONFIRMACAO`; `aoGiro("outro-lado")` mostra "Para o outro lado"; o toque durante a confirmação avança na hora; sair do palco, terminar e descartar chamam `parar()` (FR-8010 a FR-8015)
- [x] T015 [US1] Mostrar "Estamos ouvindo você." no selo durante o passo de frente, quando `ouviuFala` passar, com o medidor de som que já existe, sem terminar a gravação (FR-8013)
- [x] T016 [P] [US1] Regras em `processo_seletivo/portal/static/portal/portal.css`: `.oval[data-rosto="dentro"]` com traço contínuo e mais grosso (o de fora continua tracejado), `.confirmacao-do-giro` sobre a instrução em texto grande com o ícone de confirmação, `.aviso-da-deteccao` no topo do preparo, e nada animado sob movimento reduzido (UX-921, UX-922)
- [x] T017 [US1] Testes da página em `tests/portal/test_deteccao_do_giro.py`: com a chave desligada, o HTML e a política da `174` (nenhum `data-deteccao-`, nenhum `deteccao.js`); com ela ligada, os quatro endereços, o `data-giro` só nos dois perfis, as frases do contrato, `'wasm-unsafe-eval'` só na gravação e não no comprovante nem no acompanhamento (SC-2751, SC-2756)

**Checkpoint**: com a chave e o motor, a gravação avança sozinha nos perfis.

## Phase 4: User Story 2 — Gravar como hoje, quando a detecção não serve (P1)

**Goal**: sem motor, sem giro ou por escolha, a jornada é a da `174`, sem frase de falha.

**Independent Test**: o palco com o motor bloqueado, com "Prefiro avançar só tocando" e com o vulto parado.

- [x] T018 [US2] Em `deteccao.js` e `gravacao.js`: qualquer falha de carregamento, de SIMD, de criação ou de orçamento leva a `data-deteccao="indisponivel"` ou `"desligada"`, esconde o aviso, a ajuda e a confirmação, devolve o guia do oval ao texto de hoje e não mostra frase nenhuma (FR-8016, UX-923)
- [x] T019 [US2] "Prefiro avançar só tocando": para o `Vigia`, marca `data-deteccao="recusada"`, troca o aviso por "Combinado: você avança tocando em «Próximo»." e esconde a ajuda; a escolha vale até recarregar, e nada é guardado (FR-8005, D-003)
- [x] T020 [P] [US2] Testes em `tests/javascript/deteccao.test.js`: `podeCarregar` falso com a escolha feita; o `Orcamento` desligado não volta na mesma tomada; e em `tests/javascript/gravacao.test.js` nada dos testes de hoje muda

**Checkpoint**: a detecção ausente é invisível.

## Phase 5: User Story 3 — Saber o que a tela faz com o rosto (P2)

**Goal**: o aviso e o desligamento à vista antes de começar.

**Independent Test**: o palco antes de começar, a 375 e a 1280 px.

- [x] T021 [US3] Conferir que o aviso só aparece com `data-deteccao` em `pronta` ou `simulada`, e que, a 375×667, ele fica no topo do painel do preparo, visível sem rolar (FR-8004, US3)
- [x] T022 [P] [US3] Acrescentar as frases da detecção à varredura de vocabulário do candidato (`tests/portal/test_vocabulario_do_passo.py` ou o guardião que cobre `verificacao.html`) e um teste que recusa "prova de vida", "biometria", "reconhecimento" e "verificação facial" nas páginas da verificação (FR-8006, FR-8033)

## Phase 6: User Story 4 — Verificar sem câmera, no desenvolvimento (P3)

**Goal**: a imagem de teste gira, e a detecção simulada a lê.

**Independent Test**: a jornada no navegador com a imagem de teste, sem toque nos perfis.

- [x] T023 [US4] Em `gravacao.js`, `fonteSintetica` segue o ciclo previsível da T-010 (de frente, esquerda, de frente, direita), desenha o nariz do vulto do lado do giro e expõe `giro()`; com a imagem de teste, o `Vigia` usa `simulada` e não baixa o motor (FR-8040)
- [x] T024 [US4] Dois casos em `tests/navegador/test_jornada_do_video.py`, com a chave ligada: (a) a câmera simulada do Chromium e o motor de verdade — `data-deteccao="pronta"`, nenhuma violação da política, nenhum pedido a outra origem, e a gravação pelo toque; (b) a imagem de teste (`DEBUG`) — os perfis avançam sem toque e o corpo do início do envio tem as mesmas chaves e marcas que o gravado pelo toque (SC-2750, SC-2752, SC-2754)

## Phase 7: Polish & Cross-Cutting

- [x] T025 [P] Acrescentar a entrada `verificacao-176` (porta 8177, as duas chaves) a `.claude/launch.json`, sem tocar nas outras
- [x] T026 [P] Acrescentar a P-13 e a compressão do motor no `nginx` a `doc/verificacao-por-video-porta-do-piloto.md`, e a chave à tabela de variáveis do README, se houver (FR-8042)
- [x] T027 Verificar no navegador a 375 e a 1280 px com a imagem de teste, e com câmera real no computador se possível; registrar em `doc/deteccao-do-giro-2026-11/README.md` o tempo até `pronta`, o tempo por leitura, o peso baixado e o limiar conferido (FR-8041, SC-2753, SC-2755)
- [x] T028 Atualizar a contagem de pulados e de casos no `CLAUDE.md` se a suíte mudar de forma que ele descreve, e o status da spec
- [x] T029 `make lint check` e a suíte inteira contra PostgreSQL (`DB_NAME=ps_176`), uma vez, sozinha no cluster

## Dependencies & Execution Order

- **Setup (T001–T002)** → **Foundational (T003–T008)** → **US1 (T009–T017)** → **US2 (T018–T020)** e **US3 (T021–T022)**, que dependem dos ganchos da US1 → **US4 (T023–T024)**, que depende do `Vigia` → **Polish**.
- T009/T010 e T016 podem andar em paralelo; T011 depende de T009; T014 depende de T011 e T013.
- T024 depende de toda a US1 e da T023.

## Parallel Example: User Story 1

```text
T009 deteccao.js (funções puras)   |  T016 portal.css   |  T012 verificacao.py
T010 deteccao.test.js              |                    |
```

## Implementation Strategy

MVP é a US1 com a US2: o avanço pelo giro **e** a degradação invisível precisam chegar juntos, porque
uma sem a outra viola a FR-8014. A US3 é o aviso, que a Q-3 tornou obrigatório antes de qualquer
demonstração. A US4 é o que permite provar tudo no navegador sem rosto.

## Phase 8: Emenda de 15/11 — menos texto na gravação (FR-8050 a FR-8054, D-008)

- [x] T030 Registrar a emenda na spec: o meio-termo pedido pelo usuário, FR-8050 a FR-8054, SC-2759, D-008
- [x] T031 `GESTO_DO_PASSO` em `processo_seletivo/portal/verificacao.py`, `data-gesto` nos passos e `.gesto-do-passo` em `verificacao.html`, ícones `seta-esquerda` e `seta-direita` em `_icone.html`
- [x] T032 `gravacao.js`: `data-gesto` e `data-confirmado` no palco; `portal.css`: o sinal, a frase em tamanho de leitura nos gestos, o oval fora da gravação
- [x] T033 Testes: o mapa contra o roteiro e a página com e sem a chave (`tests/portal/test_deteccao_do_giro.py`); a jornada nos quatro tamanhos confere o sinal de cada passo, o oval e o corpo da frase (`tests/navegador/test_jornada_do_video.py`)

## Phase 9: Emenda de 15/11, à noite — o documento, a frase de frente e o microfone (FR-8060 a FR-8085, D-009 a D-011)

O usuário testou com câmera real no Safari, no C19, e pediu três coisas; Q-5 e Q-6 decididas pelas
recomendações.

- [x] T034 Registrar a emenda na spec: Q-5, Q-6, US5 a US7, FR-8060 a FR-8085, UX-925 a UX-927, SC-2760 a SC-2764, D-009 a D-011; revistas a FR-8001, a FR-8004, a FR-8013, a FR-8051 e a D-002
- [x] T035 `deteccao.js`: `avaliarDocumento`, `corridaMantida`, a contagem de rostos em `lerQuadro` e o alvo `documento` no `Vigia`; `PASSO_DO_DOCUMENTO` em `portal/deteccao.py` e `data-documento` em `verificacao.html`
- [x] T036 `gravacao.js`: o alvo do documento em `observarPasso`, "na-mao" e "visto" em `aoGiro`, o cartão do documento na imagem de teste (`rostosDaImagemDeTeste`); o aviso e a ajuda revistos
- [x] T037 A frase de frente embaixo: `[data-fala-do-passo]`, `data-passo-da-fala`, `partesDaFrase`, a folha (com o palco deitado por consulta de contêiner) e a frase do "Antes de gravar"
- [x] T038 O medidor: a barra própria em decibéis com subida rápida e descida lenta, a marca de "volume bom", o indicador do selo (ícone `microfone`), a leitura em ponto flutuante e `resume()`
- [x] T039 Testes: `deteccao.test.js` (a sequência do documento e o vigia simulado), `gravacao.test.js` (o medidor, a frase, o documento da imagem de teste), `test_deteccao_do_giro.py` (as frases, o `data-documento`, a fala e o microfone) e `test_jornada_do_video.py` (a frase de frente nos quatro tamanhos, o medidor, um toque só)
- [x] T040 Registrar em `doc/deteccao-do-giro-2026-11/` as capturas e as medidas, e a P-13 ampliada na porta do piloto
- [ ] T041 *(humano)* Com câmera real e um documento de verdade, no Safari e num celular: o documento é percebido? a barra acompanha a voz? (SC-2757, SC-2764)

