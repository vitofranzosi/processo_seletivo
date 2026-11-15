# Tasks: O polimento das telas do candidato na verificação por vídeo

**Input**: [plan.md](plan.md), [research.md](research.md) (`T-001` a `T-016`),
[data-model.md](data-model.md), [contracts/telas.md](contracts/telas.md), [quickstart.md](quickstart.md),
[spec.md](spec.md)

**Andamento (15/11)**: implementadas no PR #568 (spec, plano e tarefas no #566). O #564 não estava na `main`, e o
T001 seguiu o caminho que a research T-009 previu: `--coluna` e `--raio-pilula` acrescentados com o
nome e o valor da `172`, mais o `--controle-g`. Abertas: T039 e T040 (leitor de tela, por pessoa), T043
(aparelhos reais) e T044 (três pessoas de fora). A suíte inteira (T047) fechou em 21 388 passando e 13 pulados, sem falha.

**Tests**: pedidos pelo plano. Cada peça vem com o seu teste, no mesmo commit. A suíte roda contra
PostgreSQL, com `DB_NAME` próprio, e por diretório enquanto se trabalha. **Nenhum arquivo de
`tests/integration/verificacao/`, `tests/unit/verificacao/test_conteiner.py`,
`tests/unit/verificacao/test_r11.py`, `tests/unit/verificacao/test_roteiro_e_intervalo.py` nem dos
testes de contrato da `166` muda**: eles são a prova da FR-7887.

Os caminhos são relativos a `backend/`, salvo os de `doc/` e de `specs/`.

## Phase 1: Setup

- [x] T001 Conferir que o #564 está na `main` de partida (os tokens `--coluna`, `--raio-pilula`, `--e-*` em `processo_seletivo/shared/static/shared/tokens.css`); se não estiver, parar e perguntar ao usuário se espera ou se acrescenta os mesmos tokens (T-009, D-007)
- [x] T002 Preparar o banco de teste da worktree (`DB_NAME=ps_174`), conferir `manage.py migrate --check`, e rodar a linha de base: `tests/portal`, `tests/unit/portal`, `tests/integration/verificacao`, `tests/unit/verificacao` e `node --test tests/javascript/gravacao.test.js`, guardando a contagem
- [x] T003 [P] Capturar as telas **antes**, pelo roteiro do quickstart (passo 4), em `doc/polimento-da-verificacao-2026-11/antes/`, a 375, 768, 1280 e 1920 px, com a câmera simulada (FR-7893)

## Phase 2: Foundational

**Purpose**: a moldura e os dados que todas as telas usam.

- [x] T004 Acrescentar `--controle-g:48px` a `processo_seletivo/shared/static/shared/tokens.css`, com o comentário da decisão (D-007)
- [x] T005 Mover `_nome_da_modalidade` de `processo_seletivo/portal/passo_da_etapa.py` para `processo_seletivo/editais/domain/alcance.py` como `nome_da_modalidade(conteudo, perfil_id, modalidade_id)`, com `passo_da_etapa` passando a importá-la (T-007)
- [x] T006 Acrescentar `modalidade: str = ""` a `Situacao` em `processo_seletivo/verificacao/application/disponibilidade.py` e preenchê-la em `envio.contexto_do_titular` (`processo_seletivo/verificacao/application/envio.py`), a partir do conteúdo que ele já carrega; teste em `tests/unit/verificacao/test_modalidade_na_situacao.py`, com a contagem de consultas igual à de hoje (data-model)
- [x] T007 [P] Criar `processo_seletivo/portal/templates/portal/_icone.html`, com os ícones relógio, confirmação, luz, rosto, documento e aviso em SVG, `aria-hidden="true"`, traço de 1,75 e cor do texto (T-008)
- [x] T008 Envolver o conteúdo de `verificacao.html` e de `verificacao_comprovante.html` em `div.jornada` com o cabeçalho de `contracts/telas.md` (voltar, `h1` com o nome publicado da Etapa, `ol.jornada-momentos` com `aria-current="step"`), e reescrever no `portal.css` o início do bloco da `166`: `.jornada` com `max-width:var(--coluna)` e `margin-inline:auto`, sem as medidas `--leitura` do bloco (FR-7850, FR-7852, T-009)
- [x] T009 Acrescentar `.verificacao [hidden]{display:none !important}` ao bloco da `166` em `processo_seletivo/portal/static/portal/portal.css`, com o comentário do A-2 (FR-7854, T-011)
- [x] T010 Trocar o texto fixo "a vaga para pessoas pretas e pardas" e o título "Verificação da autodeclaração" de `processo_seletivo/portal/templates/portal/verificacao.html` pelos nomes publicados (`situacao.modalidade`, `situacao.nome_da_etapa`), com a frase da `171` quando a modalidade vier vazia; o `{% block titulo %}` também (FR-7853)
- [x] T011 [P] Testes da moldura em `tests/portal/test_verificacao_por_video.py`: o `h1` é o nome publicado da Etapa; a página não contém "pessoas pretas e pardas" fora do roteiro; cada tela tem `.jornada`; a política de conteúdo é a de hoje, diretiva a diretiva (SC-2657)

**Checkpoint**: as três páginas centradas, com os nomes publicados; nenhuma recusa visível em repouso.

## Phase 3: User Story 1 — Gravar o vídeo inteiro no celular (Priority: P1) 🎯 MVP

**Goal**: do "Antes de gravar" ao envio no celular, sem rolar, sem alcançar o topo e sem a tela apagar.

**Independent Test**: a jornada no navegador a 375×667 com câmera simulada (T-015) e, depois, um iPhone
e um Android reais (quickstart, passo 5).

- [x] T012 [US1] Em `processo_seletivo/portal/templates/portal/verificacao.html`, juntar as seções `camera` e `gravacao` numa só, `data-tela="palco"` com `data-estado`, **um** `video.previa[data-previa]` e as camadas e o bloco de preparo de `contracts/telas.md`; tirar `data-previa-gravacao`, `data-ir-gravar`, `data-checagem-camera` e `data-passo-proximo`; o `ol.passos-do-roteiro` passa a listar só os títulos, mantendo `data-passo`, `data-texto` e `data-titulo` (FR-7866, FR-7867, T-001)
- [x] T013 [US1] Em `processo_seletivo/portal/static/portal/gravacao.js`, fazer "Continuar" (`data-continuar-acolhimento`) chamar `abrirCamera()`; abrir o palco em `data-estado="preparo"`; "Começar a gravar" trocar para `gravando` sem reabrir o fluxo; o descarte por página escondida e "Parar e recomeçar" voltarem a `preparo`; "Voltar" do palco fechar a câmera (FR-7866, FR-7875, T-001)
- [x] T014 [US1] No mesmo script, `desenharPassos()` escrever `rotuloDoPasso`, o título e a instrução nas camadas de cima, anunciar "Passo N de 4: título. instrução" no elemento `aria-live`, e devolver o foco a "Próximo"; "Próximo" passar por `aceitaAvanco` (FR-7868, FR-7869, FR-7870, T-002, T-005)
- [x] T015 [US1] No mesmo script, o pedido de tela acesa ao entrar no palco, o novo pedido ao voltar a ficar visível com o palco aberto, a soltura ao sair, e o aviso `data-aviso-tela-acesa` quando não houver suporte ou o pedido for recusado (FR-7877, T-004)
- [x] T016 [US1] No mesmo script, o medidor grande no preparo e pequeno gravando, com `ouviuFala` e as três frases de `data-estado-do-som` (FR-7873, T-006)
- [x] T017 [US1] No mesmo script, a revisão com `duracaoPorExtenso` e `megabytes`; o envio com a porcentagem por extenso e "Não feche esta página enquanto o envio não terminar." (FR-7880, FR-7881)
- [x] T018 [US1] Exportar `rotuloDoPasso`, `aceitaAvanco`, `megabytes`, `ouviuFala` e `duracaoPorExtenso` em `GravacaoDoVideo`, sem mudar as funções de hoje; testes em `tests/javascript/gravacao.test.js` (contracts/telas.md, *Funções puras novas*)
- [x] T019 [US1] Em `processo_seletivo/portal/static/portal/portal.css`, o palco: grade de uma célula, faixas sobre a prévia, a faixa da instrução com fundo escuro de opacidade 0,78 e no máximo um terço da altura com rolagem, "Próximo" com `--controle-g` no terço de baixo, "Parar e recomeçar" menor no canto de cima, e o estado decidindo o que aparece; abaixo de 40rem, `position:fixed; inset:0`, `100vh` e `100dvh`, `env(safe-area-inset-bottom)` (FR-7868, FR-7869, FR-7871, FR-7875, T-002, T-003)
- [x] T020 [US1] No mesmo bloco, o guia proporcional ao palco com a frase dele, a frase do espelho no preparo, o celular deitado (`orientation: landscape` e `max-height: 30rem`) com a sugestão do retrato, e `prefers-reduced-motion` (FR-7872, FR-7874, FR-7878, FR-7879, T-013)
- [x] T021 [US1] Criar `tests/navegador/test_jornada_do_video.py`, com fixture própria que lança o Chromium com `--use-fake-device-for-media-stream` e `--use-fake-ui-for-media-stream` e fecha as conexões ao sair; a 375×667 percorrer do acompanhamento ao comprovante e medir SC-2651, SC-2652, SC-2653, SC-2654 e SC-2656 (T-015)
- [x] T022 [US1] Rodar `tests/portal`, `tests/javascript`, os guardiões de folha (`tests/interface/test_folha_estatica.py`, a acessibilidade de classes, `tests/interface/test_larguras.py`) e a jornada nova; corrigir o que reprovar

**Checkpoint**: a gravação inteira no celular, provada no Chromium; os testes da `166` intactos.

## Phase 4: User Story 2 — Gravar pelo computador (Priority: P1)

**Goal**: a página centrada, o vídeo em paisagem na coluna, a instrução sobre o vídeo e o avanço pelo
teclado.

**Independent Test**: a mesma jornada a 1280×800; o Safari e o Firefox do computador à mão.

- [x] T023 [US2] Em `processo_seletivo/portal/static/portal/portal.css`, a partir de 40rem, o palco na largura da coluna, com `aspect-ratio:16/9` e altura máxima de 70% da janela, e o bloco de preparo abaixo da prévia (FR-7876)
- [x] T024 [US2] Estender `tests/navegador/test_jornada_do_video.py` a 1280×800: margens iguais (SC-2650), Espaço avança o passo com o foco em "Próximo" (FR-7869), a lista inteira do roteiro não aparece gravando (FR-7867)

**Checkpoint**: o problema 1 e o problema 6 resolvidos no computador.

## Phase 5: User Story 3 — Saber, no acompanhamento, o que falta e até quando (Priority: P1)

**Goal**: o selo sem tracejado, o prazo em linha própria e a ação que diz para onde leva.

**Independent Test**: o acompanhamento do C18 nos três estados do passo, a 375 e a 1280 px.

- [x] T025 [US3] Em `processo_seletivo/portal/situacao.py`, trocar `VER_COMO_FUNCIONA` por `ESCOLHER_VIDEO_OU_AO_VIVO = "Escolher entre vídeo e entrevista ao vivo"`, tirar o prazo da frase principal do passo com vídeo e passá-lo ao campo `prazo` da `Acao`, com um rótulo próprio do passo (FR-7857, FR-7858, T-008); o resto das frases da `171` intacto (FR-7859)
- [x] T026 [US3] Em `processo_seletivo/portal/templates/portal/acompanhamento.html`, o selo com o ícone de `_icone.html` (relógio no provisório, confirmação no registrado) e a linha do prazo do passo com o rótulo "Prazo:" em destaque, antes do porquê (FR-7856, FR-7857)
- [x] T027 [US3] Em `processo_seletivo/portal/static/portal/portal.css`, `.rotulo-da-situacao` em pílula com `--raio-pilula`, sem `dashed`, fundo âmbar claro no provisório e verde claro no registrado, e a regra da linha do prazo, com o comentário que cita a UX-155 da `063` e a D-008 (FR-7856)
- [x] T028 [P] [US3] Atualizar `tests/unit/portal/test_situacao_do_passo.py` e `tests/portal/test_vocabulario_do_passo.py` às frases novas; acrescentar a `tests/portal/test_verificacao_por_video.py` que o acompanhamento mostra o prazo em linha própria e o rótulo novo, e que, com a chave desligada, só o selo muda (FR-7888)

**Checkpoint**: o problema 2 resolvido; a `171` continua dizendo o mesmo.

## Phase 6: User Story 4 — Escolher a forma e preparar-se (Priority: P2)

**Goal**: dois cartões que dizem o que cada forma é; o preparo em três itens, com o documento; a idade
sem recusa em repouso.

**Independent Test**: a página da verificação nas telas de escolha, ao vivo, preparo e menor, a 375 e a
1280 px, com e sem vídeo enviado.

- [x] T029 [US4] Em `processo_seletivo/portal/templates/portal/verificacao.html`, a escolha de `contracts/telas.md`: a frase da modalidade, o prazo, o aviso de substituição acima, "As duas formas valem igual." e os dois `article.forma` com os botões de hoje (FR-7860, FR-7861, T-010)
- [x] T030 [US4] No mesmo template, o "Antes de gravar": `ul.preparo` com os três itens e ícones, o teto, a seção "Quem vê o seu vídeo" com as quatro frases de hoje, as opções grandes da idade e o `aria-describedby` da recusa (FR-7863, FR-7864, FR-7865); as telas `ao-vivo`, `menor` e `nao-consigo` com "Voltar ao acompanhamento" como principal (FR-7862)
- [x] T031 [US4] Em `processo_seletivo/portal/static/portal/gravacao.js`, ao "Continuar" sem resposta, mostrar a recusa e pôr o foco no `fieldset` (FR-7865)
- [x] T032 [US4] Em `processo_seletivo/portal/static/portal/portal.css`, `.forma` (lado a lado a partir de 40rem, mesmo desenho), `.preparo`, `.opcao-grande` com `:has(:checked)`, e a ação principal com `--controle-g` e largura cheia no celular (FR-7851, T-010, T-011)
- [x] T033 [P] [US4] Em `tests/portal/test_verificacao_por_video.py`: as seis informações de hoje continuam na página (D-010); o item do documento está no preparo; os dois cartões têm a mesma classe e os botões de hoje; a recusa nasce com `hidden`

**Checkpoint**: os problemas 3 e 4 resolvidos.

## Phase 7: User Story 5 — Conferir o comprovante e assistir ao próprio vídeo (Priority: P2)

**Goal**: a confirmação no centro; os dados para conferência no fim, visíveis; a impressão numa folha.

**Independent Test**: o comprovante nos estados recebido, em análise, encaminhado e eliminado, a 375 e
a 1280 px, e impresso.

- [x] T034 [US5] Criar o filtro `duracao_por_extenso` em `processo_seletivo/portal/templatetags/` e o teste em Python com os mesmos casos do teste em JavaScript (FR-7883, T-012)
- [x] T035 [US5] Reescrever `processo_seletivo/portal/templates/portal/verificacao_comprovante.html` na ordem de `contracts/telas.md`: a confirmação com ícone e data, a frase da eliminação logo abaixo quando houver, "E agora?", "Assistir", "Gravar outro vídeo", e "Dados para conferência" com o rótulo "Código de conferência do arquivo (SHA-256)" (FR-7882, FR-7885)
- [x] T036 [US5] A situação sem gravação de `verificacao.html` na mesma moldura, com o estado no centro e "Ver o comprovante" como principal (FR-7886)
- [x] T037 [US5] Em `processo_seletivo/portal/static/portal/portal.css`, `.confirmacao-do-envio`, os dados em texto menor e o `@media print` que esconde o reprodutor, os botões e o voltar (FR-7884)
- [x] T038 [P] [US5] Em `tests/portal/test_verificacao_por_video.py`: a confirmação vem antes de "E agora?", e os dados depois; a duração sai em minutos e segundos; o eliminado mantém a frase e não oferece assistir; e a jornada no navegador mede o primeiro quadro a 375 px (SC-2659)

**Checkpoint**: o problema 7 resolvido.

## Phase 8: User Story 6 — Gravar com leitor de tela, teclado ou em Libras (Priority: P3)

**Goal**: a gravação inteira por leitor de tela e por teclado, sem nada que apresse.

**Independent Test**: VoiceOver no iPhone e no macOS, NVDA no Windows, e só teclado.

- [ ] T039 [US6] Conferir à mão, com VoiceOver no macOS e só teclado, de "Antes de gravar" ao envio: a ordem de leitura de `contracts/telas.md`, o anúncio de cada passo (UX-875), o foco em "Próximo", o `aria-current` do momento e a recusa citada pelo `fieldset`; registrar em `doc/polimento-da-verificacao-2026-11/acessibilidade.md`
- [ ] T040 [US6] Repetir com VoiceOver no iPhone durante a validação em aparelho real (T043), e com NVDA se houver uma máquina Windows disponível; o que não puder ser feito fica registrado como pendente no mesmo arquivo

## Phase 9: Polish & verificação

- [x] T041 Rodar a varredura de vocabulário do candidato com as frases novas (FR-7891) e os guardiões de folha (`}}` e `%}` na folha, classe sem regra), e conferir no console do navegador que nenhuma tela tem violação de política de conteúdo
- [x] T042 [P] Capturar as telas **depois** em `doc/polimento-da-verificacao-2026-11/depois/` pelo mesmo roteiro do T003, com o `README.md` da comparação tela a tela (FR-7893)
- [ ] T043 Validar num iPhone (Safari) e num Android (Chrome) reais pelo quickstart, passo 5, registrando aparelho, sistema, navegador e o resultado de cada item no `README.md` das capturas (FR-7892, SC-2655); a falha de envio por rede vira registro da `166` (A-5)
- [ ] T044 Validar com três pessoas de fora da equipe técnica pelo quickstart, passo 6, registrando o resultado sem nome e sem imagem (SC-2658); apagar o banco e os arquivos do ambiente ao fim
- [x] T045 Conferir que nenhum arquivo dos testes de envio e de contrato da `166` mudou (`git diff --stat main -- tests/integration/verificacao tests/unit/verificacao/test_conteiner.py tests/unit/verificacao/test_r11.py tests/unit/verificacao/test_roteiro_e_intervalo.py tests/contract`) (FR-7887)
- [x] T046 Criar `specs/174-polimento-da-verificacao-do-candidato/rastreabilidade.md` com uma linha para cada `FR-`, `SC-` e `UX-` em negrito da spec, inclusive as reservas da faixa, e atualizar o `Status` da spec e a linha da `174` no `README.md`
- [x] T047 `make lint check test-pg` com a suíte inteira, sozinha no cluster

## Dependencies & Execution Order

- **Setup (T001–T003)** antes de tudo; o T001 pode parar a feature até o #564.
- **Foundational (T004–T011)** bloqueia todas as histórias: a moldura, a modalidade e a recusa escondida.
- **US1 (T012–T022)** é a de maior risco e a que mais muda o script; **US2 (T023–T024)** depende dela
  (mesmo palco). **US3 (T025–T028)** não depende do palco e pode correr em paralelo com a US1.
- **US4 (T029–T033)** e **US5 (T034–T038)** não dependem da US1, mas tocam o mesmo template e a mesma
  folha: em sequência, para não colidir.
- **US6 (T039–T040)** depende de US1, US2 e US4.
- **Polish (T041–T047)** no fim; o T043 e o T044 pedem o ambiente do quickstart.

```text
T001 → T002 → T004..T011 ─┬─ US1 (T012..T022) → US2 (T023..T024) ─┐
                          ├─ US3 (T025..T028) ────────────────────┤
                          └─ US4 (T029..T033) → US5 (T034..T038) ─┴→ US6 → Polish
```

## Parallel Example

```text
Depois da Foundational:
  US1, script e palco: T012 → T013 → T014..T018
  US3, acompanhamento: T025 → T026 → T027, com T028 [P]
Dentro da US1: T018 (funções puras e testes) em paralelo com T019..T020 (folha).
```

## Implementation Strategy

1. **Incremento A** — Foundational e US3: a moldura centrada, os nomes publicados, a recusa escondida e o
   acompanhamento. Já resolve os problemas 1, 2, 4 (a recusa) e 8, e é verificável sozinho.
2. **Incremento C** — US1 e US2: o palco. É o centro do pedido e o de maior risco; a jornada no
   navegador o prova antes dos aparelhos reais.
3. **Incremento B** — US4: a escolha e o preparo.
4. **Incremento D** — US5, US6 e Polish: o comprovante, a acessibilidade, as capturas, os aparelhos e as
   pessoas.

A ordem é A, C, B, D, e não a das letras nem a numeração das histórias: o palco não depende da escolha,
e adiá-lo empurraria o risco para o fim (plano, *Ordem de entrega*).
