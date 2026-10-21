# Tasks: Prévia do sorteio

**Input**: Design documents from `specs/098-previa-do-sorteio/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: pedidos pela spec — a equivalência com o sorteio oficial (SC-927), a ausência de efeito
(FR-2509, SC-930), a recusa de semente forjada (FR-2483, SC-931) e o determinismo do resumo (FR-2502)
são requisitos, e a prévia só vale se a equivalência estiver escrita e com sentinela antes da tela.

**21/10/2026**: o usuário autorizou a Fase 2 (T001 a T011), e ela foi feita nesta worktree, sem tela.
`make lint test-pg`: 12828 passando, 13 pulados, e a única falha era a linha da `098` que faltava na
tabela de incrementos do README, acrescentada em seguida. **O que mudou em relação ao planejado:**

- **Os nomes chegam como função, e não como tupla** (T005): `populacao(..., nomear=...)` recebe
  `cenarios_da_previa.nome_ficticio`, a mesma `_nome` da `094` exposta com outro nome, porque o
  repertório com o sufixo de volta (`"Alice 2"`) é uma regra, e copiá-la para o sorteio faria duas.
- **A sentinela troca o material, e não a regra** (T009): com material no formato da Loteria Federal,
  `DIGITOS_EM_SEQUENCIA` e `TEXTO_LITERAL` dão a mesma semente, e a sentinela planejada não mordia.
- **A lista reservada vazia segue o caminho oficial** (T008, T009): ela não é sorteada nem apurada, e a
  vaga dela não é cedida nem "por saldo". A spec dizia o contrário; a FR-2489 foi corrigida e o achado
  está em [doc/achado-reservada-vazia-nao-reverte.md](../../doc/achado-reservada-vazia-nao-reverte.md).
- **Sem regra de corte, nenhuma apuração** (T008): a rodada devolve `sem_corte` e não chama a ocupação,
  e o resumo não repete mil vezes "não há faixa".

**21/10/2026, a interface**: o usuário mandou seguir, e as fases 3 a 8 (T012 a T034) foram feitas na
branch `claude/098-interface-da-previa`, empilhada sobre a do motor (#327). Demonstrada pela interface
real, num banco próprio com o Edital de demonstração da `094`, a 1280 e a 375 px. **O que mudou em
relação ao planejado:**

- **A prévia do sorteio não desenha a jornada do Perfil** (T019): a `jornada` da `094` é feita da
  população com notas, e reescrevê-la para o sorteio seria a maior parte da feature. O painel do sorteio
  mostra a ordem de cada lista, a ocupação e as rodadas; a jornada da `094` diz que o marco por sorteio
  tem prévia própria e oferece abri-la (FR-2480), pela mesma rota.
- **O bloco da ocupação é o da `095`, chamado com a ordem do sorteio** (T021, T022): as mesmas frases,
  inclusive a do comportamento atual da DP-1; o "caminho" que manda escolher caso-limite sai, porque o
  sorteio não tem caso-limite nem empate.
- **A medida a 375 px foi feita no navegador, e não por CSSOM no teste** (T028): o teste prende a regra
  que quebra a semente entre os grupos; a medida (`scrollWidth` igual a `clientWidth`, 375) está na
  demonstração.
- **A lista literal da varredura de vocabulário não precisou de linha** (T032): ela desce nos parciais
  de `compor_classificacao.html`, e o painel do sorteio é incluído ali como o da `094`.

**Organization**: a Fase 2 é o motor — ordem fictícia, rodada, resumo e equivalência —, puro e sem tela.
As fases das histórias são a interface, e dependem da Fase 2 inteira. A US1 é o MVP; a US2 e a US3
escrevem no mesmo template e no mesmo módulo de frases, e correm depois dela.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente)
- **[Story]**: a história da spec (US1 a US5)
- Caminhos relativos à raiz do repositório

---

## Phase 1: Setup

**Purpose**: ponto de partida conferido

- [x] T001 Conferir que a worktree está sobre a `main` atual e que `backend/.venv` existe (senão, `uv sync --extra dev` em `backend/`); rodar `specs/098-previa-do-sorteio/prototipo/medicao.py` de dentro de `backend/` e conferir a saída contra a R-001 e a R-003 de `specs/098-previa-do-sorteio/research.md` — divergência de mais de 5 pontos nas porcentagens, ou cessão diferente, é sinal de que o motor mudou desde 21/10, e a R-001 precisa ser refeita antes de seguir
- [x] T002 [P] Rodar `backend/tests/unit/sorteios/test_sem_gerador_pseudoaleatorio.py`, `backend/tests/unit/classificacao/test_previa.py`, `backend/tests/interface/test_previa_da_classificacao.py` e `backend/tests/interface/test_previa_por_recorte.py` contra a `main` e anotar quantos casos passam: é a linha de base que as Fases 2 e 6 não podem mexer, salvo o caso da R-010

---

## Phase 2: Foundational — o sorteio fictício, a rodada, o resumo e a equivalência

**Purpose**: o motor da prévia do sorteio, puro, provado igual ao oficial antes de qualquer tela.

**⚠️ CRITICAL**: nenhum arquivo de `backend/processo_seletivo/sorteios/` importa `random`, `secrets`,
`numpy` ou `os.urandom` (R-004). A T002 e a T011 provam que a varredura continua verde **sem emenda**.

- [x] T003 [P] Escrever `backend/tests/unit/sorteios/test_simulacao_ordem.py`: para cada vetor normativo de ordem em `backend/tests/contract/fixtures/sorteio/`, `ordem_do_recorte(..., relation_hash=<o do vetor>)` devolve a ordem do vetor; sem `relation_hash`, usa o resumo da relação fictícia e é determinística; a numeração da relação fictícia é 1 a N na ordem da população; a ampla tem todos e cada reservada só os da lista; o resumo fictício tem a forma da R-005 e nunca a de `projecao.conteudo_canonico`; cada item tem `inscricao_id`, `posicao`, `empate_residual: False` e `numero_publico`; `semente_da_rodada` devolve `f"{semente}:{i}"`
- [x] T004 [P] Escrever `backend/tests/unit/sorteios/test_simulacao_populacao.py`: sugestão pelo dobro das vagas da linha e dez sem linha (FR-2487); soma na ampla (FR-2488); zero numa reservada aceito (FR-2489); `id`, nome e Modalidade estáveis quando outra quantidade muda, e acréscimo só no fim da lista alterada (FR-2490); limite de 600 e de seis reservadas (FR-2491); nomes do repertório de `cenarios_da_previa`, sem código nem nome de Modalidade
- [x] T005 Implementar `backend/processo_seletivo/sorteios/domain/simulacao.py` conforme `specs/098-previa-do-sorteio/contracts/sorteio-ficticio.md` — `populacao`, `relacao_ficticia`, `ordem_do_recorte`, `semente_da_rodada` —, importando só `sorteios.domain.chave` e `shared.canonical`; os nomes chegam por parâmetro de `populacao` — quem os passa é a T008, a partir da tupla `_NOMES` de `backend/processo_seletivo/classificacao/domain/cenarios_da_previa.py`, exposta ali como `NOMES` sem mudar de valor —, para que o domínio do sorteio não importe a prévia da classificação e o repertório seja um só
- [x] T006 Tornar públicas, **sem mudar de corpo**, `_corte` → `corte_da_ordem` e `_entrada_da_rodada` → `entrada_da_rodada` em `backend/processo_seletivo/classificacao/application/previa.py`, trocando as chamadas internas; rodar a linha de base da T002 da `094`/`095` e conferir que nenhum caso mudou
- [x] T007 [P] Escrever `backend/tests/unit/sorteios/test_simulacao_resumo.py`: com a população da história 1 (20/6/4, vagas 10/3/2), as faixas e a rodada da R-001 — PPI sem ocupante 1 em média com margem, cessão por saldo igual às vagas sem ocupante, por esgotamento zero em todas as rodadas —; o resumo é a soma, rodada a rodada, dos campos de `rodada_da_previa.rodada` (FR-2504), conferido refazendo três rodadas à mão; `constante` quando todas as rodadas dão o mesmo valor; `nao_avaliado` sem linha no quadro e sem corte; mesma semente e mesma população dão o mesmo resumo (FR-2502); duas sementes diferem no máximo 5 pontos em cada porcentagem (SC-929); e `resumir` com 500 candidatos e seis reservadas em até 5 s, e a rodada em até 1 s (SC-928)
- [x] T008 Implementar `backend/processo_seletivo/sorteios/application/simulacao.py` conforme o contrato: `simular_sorteio` normaliza o material pela regra do método (ou `DIGITOS_EM_SEQUENCIA`, com `supos_regra`), ordena cada recorte, corta por `corte_da_ordem` com o alvo e os suplentes da regra do marco (no alvo do quadro, a linha de cada recorte; sem linha, `sem_linha` como em `_recorte` da `095`), monta as entradas por `entrada_da_rodada` e chama `apurar_recortes`; `resumir` repete a rodada para cada semente derivada e acumula os contadores do `data-model.md` sem guardar ordens
- [x] T009 Escrever `backend/tests/integration/sorteios/test_previa_do_sorteio_equivale_ao_oficial.py` (R-009): um Edital com marco por sorteio, PPI e PcD, alvo do quadro; inscrições submetidas por lista; relação publicada por recorte; ocorrência observada pela `FonteDeTeste` com `MATERIAL` apontando o material fictício; sorteio constituído, corte e apuração emitidos pelo caminho oficial; a prévia com os mesmos participantes, o mesmo material e os resumos oficiais injetados produz as mesmas ordens, faixas, quatro quantidades e vagas cedidas por recorte — nos casos sem reversão, por saldo e por esgotamento, e com uma reservada de zero inscritos; e a sentinela: com a regra de normalização trocada só na prévia, o teste reprova
- [x] T010 [P] Escrever em `backend/tests/unit/sorteios/test_simulacao_ordem.py` a prova de fronteira: `sorteios/domain/simulacao.py` não importa nada de `classificacao` nem de `ocupacao`, e `sorteios/application/simulacao.py` não importa `ocupacao` (a ocupação chega por parâmetro); e conferir que `backend/tests/test_dependencia_da_ocupacao.py` continua verde sem emenda
- [x] T011 Rodar `backend/tests/unit/sorteios/`, `backend/tests/integration/sorteios/`, `backend/tests/unit/classificacao/`, `backend/tests/unit/ocupacao/` e a linha de base da T002, sem alterar teste existente

**Checkpoint**: a prévia do sorteio calcula, resume e é provadamente o motor oficial — sem tela.

---

## Phase 3: User Story 1 — Simular o sorteio de cada lista com uma semente fictícia (Priority: P1) 🎯 MVP

**Goal**: o botão no cartão, a semente fictícia com selo, a ordem de cada lista na jornada e no detalhe, e
"Sortear de novo".

**Independent Test**: para um token de semente e uma população, a ordem de cada recorte no painel é a de
`ordem_do_recorte`; a ampla tem todos; "Sortear de novo" troca a semente e mudar quantidade a mantém.

- [x] T012 [P] [US1] Escrever em `backend/tests/interface/test_previa_do_sorteio.py` os cenários 1 a 7 da US1: "Simular sorteio" no cartão do marco por sorteio e "Simular classificação" ausente; a faixa da semente com cinco números de seis dígitos, o selo e a frase do certame; nenhum campo de semente no HTML; `sortear=1` troca a semente e as ordens; mudar quantidade mantém a semente e o anúncio diz "mantida"; o detalhe da PPI com posição na PPI e na ampla e a frase de listas sorteadas à parte; menos inscritos que vagas com todos com posição e a frase de que sorteia mesmo assim; Perfil sem reservada sem seletor
- [x] T013 [P] [US1] Escrever em `backend/tests/interface/test_previa_do_sorteio.py` a recusa da semente (FR-2483, SC-931): token forjado, token de outro marco e `material=`/`seed=` na query — os dois primeiros respondem o estado `semente_recusada` (200, como toda recusa de fragmento htmx da gestão) sem ordem nenhuma, e o terceiro é ignorado
- [x] T014 [US1] Criar `backend/processo_seletivo/interface/previa_do_sorteio.py`: o material por `secrets.randbelow(10**6)` cinco vezes; o token por `django.core.signing.dumps` com `salt="previa-do-sorteio"` e Edital, Perfil e marco dentro; a leitura do token com recusa; a população do formulário (`inscritos-ampla`, `inscritos-<lista_id>`) com a sugestão; o método que governa o marco (o do cartão, senão o comum do rascunho); e `contexto(...)` chamando `simular_sorteio` com `apurar_recortes_com(especie)` de `interface/previa_da_classificacao.py`
- [x] T015 [US1] Despachar o fragmento em `backend/processo_seletivo/interface/views.py::fragmento_previa_da_classificacao` pela forma do marco digitado (R-007): `POR_SORTEIO` vai para `previa_do_sorteio.contexto` e `_previa_do_sorteio.html`; o resto, como hoje
- [x] T016 [US1] Escrever as frases da US1 em `backend/processo_seletivo/interface/previa_do_sorteio.py`: o selo e a frase da semente (FR-2482), "semente mantida" e "semente nova" (FR-2485), a ampla como universo inteiro com a soma (FR-2488), as listas sorteadas à parte (FR-2494), sorteia mesmo com sobra de vaga (FR-2496), a regra de normalização suposta (D-007) e a lista da Modalidade apontada como ampla que a prévia não simula (D-005)
- [x] T017 [US1] Criar `backend/processo_seletivo/interface/templates/interface/_previa_do_sorteio.html` e `backend/processo_seletivo/interface/templates/interface/_semente_ficticia.html` — a faixa da semente, o campo oculto `semente`, o botão "Sortear de novo" com `hx-get` e `sortear=1`, a jornada e o detalhe com o seletor de recorte e `_marcas_do_recorte.html` da `095` —, e as regras de toda classe nova em `backend/processo_seletivo/interface/static/interface/telas/previa-da-classificacao.css`
- [x] T018 [US1] Acrescentar "Simular sorteio" em `backend/processo_seletivo/interface/templates/interface/_marco.html` na condição `marco.orderProduction == "POR_SORTEIO"`, com o mesmo `hx-get`, `hx-include` do cartão do Perfil e `hx-target` do painel do "Simular classificação", e o comentário de por quê no tom do que está lá
- [x] T019 [US1] Fazer a jornada em `backend/processo_seletivo/interface/previa_da_classificacao.py` aceitar o marco por sorteio simulado (FR-2480): quando ele é o simulado, o ponto do marco mostra o resumo por recorte do sorteio; quando outro marco é o simulado, o marco por sorteio diz que tem prévia própria no cartão dele, e a frase da FR-2254 da `094` perde o "sorteio" nesse caso

**Checkpoint**: a US1 funciona sozinha: o elaborador vê as ordens por lista com semente fictícia, sem bloco de ocupação.

---

## Phase 4: User Story 2 — Ver, na rodada, quem ocuparia vaga em cada lista e o efeito da reversão (Priority: P1)

**Goal**: o bloco da ocupação da rodada exibida, com as quatro quantidades, "ocuparia pela ampla" e a
reversão.

**Independent Test**: as quantidades, quem ocupa pela ampla e as cedidas no painel são as da equivalência
(T009) para a mesma semente.

- [x] T020 [P] [US2] Escrever em `backend/tests/interface/test_previa_do_sorteio.py` os cenários 1 a 6 da US2: ocupantes pela ampla e a vaga que continua reservada, sem movimento; posições da faixa tomadas e autodeclarados além, com "comportamento atual"; cessão por saldo; esgotamento sem cessão com "comportamento atual"; "o Edital não reverte" sem declaração; sem regra de corte, as ordens e a frase de que não há faixa, sem quantidades
- [x] T021 [US2] Escrever as frases da ocupação da rodada em `backend/processo_seletivo/interface/previa_do_sorteio.py`, reaproveitando as de `backend/processo_seletivo/interface/previa_da_classificacao.py` (`ocupacao_dos_recortes`, `_frase_da_reversao`) onde servem, com as hipóteses da FR-2320 da `095`, a frase da FR-2498 e a de DP-1 e DP-2 como comportamento atual (FR-2507)
- [x] T022 [US2] Incluir `_ocupacao_da_previa.html` da `095` em `backend/processo_seletivo/interface/templates/interface/_previa_do_sorteio.html`, com a marca "ocuparia pela ampla" no detalhe, e a frase de sem corte (FR-2500)

**Checkpoint**: US1 e US2 mostram a rodada inteira.

---

## Phase 5: User Story 3 — Ver o que acontece em muitas rodadas (Priority: P1)

**Goal**: o resumo das 1.000 rodadas, por recorte.

**Independent Test**: com o mesmo token e a mesma população, o resumo é o mesmo nas duas chamadas e é o
de `resumir` (T007).

- [x] T023 [P] [US3] Escrever em `backend/tests/interface/test_previa_do_sorteio.py` os cenários 1 a 5 da US3: o número de rodadas e a origem das sementes ditos; o mesmo resumo com o mesmo token; o resumo recalculado com "Sortear de novo"; Perfil sem reservada sem falar de cotas; "em todas as rodadas" em vez de porcentagem quando constante; e a frase de que as frequências são da população fictícia e não previsão (FR-2505)
- [x] T024 [US3] Chamar `resumir` em `backend/processo_seletivo/interface/previa_do_sorteio.py` e escrever as frases do resumo (FR-2503, FR-2505), com porcentagem inteira e médias com uma casa decimal, e a de DP-1/DP-2 como comportamento atual quando a cessão for sempre zero ou a sobra for frequente
- [x] T025 [US3] Criar `backend/processo_seletivo/interface/templates/interface/_rodadas_do_sorteio.html` e incluí-lo abaixo da rodada em `_previa_do_sorteio.html`, com as regras novas na folha da prévia

**Checkpoint**: as três histórias P1 entregam o critério de sucesso (SC-925).

---

## Phase 6: User Story 4 — Informar quantos se inscrevem em cada lista (Priority: P2)

**Goal**: os campos de quantidade no painel, com sugestão e limite.

**Independent Test**: uma quantidade digitada muda a soma da ampla e só acrescenta gente na lista
alterada, com a mesma semente.

- [x] T026 [P] [US4] Escrever em `backend/tests/interface/test_previa_do_sorteio.py` os cenários 1 a 4 da US4: a sugestão e a frase de como sugeriu; a soma nova na ampla e os nomes mantidos; zero numa reservada; acima de 600 com o estado `acima_do_limite` e sem cálculo; e valor inválido (texto, negativo) caindo na sugestão daquela lista, com a frase
- [x] T027 [US4] Criar `backend/processo_seletivo/interface/templates/interface/_populacao_do_sorteio.html` — um `<input type="number" min="0">` com `<label>` por lista, `hx-get` no `change` dentro do formulário do painel — e incluí-lo acima da rodada em `_previa_do_sorteio.html`; e as frases da sugestão e do limite em `backend/processo_seletivo/interface/previa_do_sorteio.py`

---

## Phase 7: User Story 5 — No celular e com leitor de tela (Priority: P3)

**Goal**: 375 px e o anúncio da semente.

**Independent Test**: sem rolagem horizontal ao sortear de novo e trocar de lista; o anúncio diz se a
semente mudou ou foi mantida.

- [x] T028 [P] [US5] Escrever em `backend/tests/interface/test_previa_do_sorteio.py` a medida por CSSOM a 375 px da faixa da semente, da população e do resumo, o anúncio da região `aria-live` com a semente mudada ou mantida e a frase de maior consequência do resumo (FR-2511), e a ausência de `style=`, `<style>`, `<script>` e `on*=` no HTML devolvido (FR-2512)
- [x] T029 [US5] Ajustar `backend/processo_seletivo/interface/static/interface/telas/previa-da-classificacao.css` (a semente quebra em grupos de seis dígitos; a população empilha abaixo de 40rem; o resumo em lista, e não em tabela, no estreito) e a frase do anúncio em `backend/processo_seletivo/interface/previa_do_sorteio.py`

---

## Phase 8: Polish & Cross-Cutting Concerns

- [x] T030 [P] Escrever em `backend/tests/interface/test_previa_do_sorteio.py` a ausência de efeito (FR-2509, SC-930): nenhuma escrita em relação, ocorrência, sorteio, ordem, corte, apuração, movimento, rascunho, sessão ou trilha ao abrir, recalcular, sortear de novo, trocar lista, mudar quantidade e fechar; nenhuma consulta a `Inscricao`
- [x] T031 Emendar a `094` (D-008, R-010): em `specs/094-previa-da-classificacao/spec.md`, a FR-2200, a FR-2251 e a FR-2254 com a redação nova e a anterior registrada, citando a FR-2477 e a FR-2480; em `backend/tests/interface/test_previa_da_classificacao.py`, `test_marco_por_sorteio_pedido_a_mao_fica_fora_da_fatia` passa a afirmar que o fragmento responde a prévia do sorteio, e `test_o_botao_nao_aparece_no_marco_por_sorteio` ganha a afirmação de que "Simular sorteio" aparece; o comentário do `_marco.html` sobre a decisão 007 da `094` atualizado
- [x] T032 [P] Passar pelos guardiões do repositório: a lista literal de `backend/tests/test_vocabulario_da_composicao.py` (os templates novos entram nela); uma regra na folha para toda classe nova (`backend/tests/interface/test_acessibilidade.py`); a varredura de vocabulário proibido ("convocado", "aprovado", "matriculado") nas frases de `previa_do_sorteio.py`; nenhum `}}` em CSS; `backend/tests/unit/sorteios/test_sem_gerador_pseudoaleatorio.py` verde sem emenda
- [x] T033 *Roteiro escrito; a validação com pessoas fica aberta até o relato do usuário.* [P] Escrever `specs/098-previa-do-sorteio/roteiro-de-compreensao.md` com as perguntas da SC-925 e da SC-926 — inclusive uma sobre a sobra frequente de vaga de PPI (R-001) —, sobre o roteiro da `094` e o da `095`
- [x] T034 Escrever `specs/098-previa-do-sorteio/rastreabilidade.md` (FR-2477 a FR-2512 e SC-925 a SC-931 → tarefa → teste), rodar o roteiro de `specs/098-previa-do-sorteio/quickstart.md` pela interface e `make lint check test-pg` em `backend/`

---

## Dependencies & Execution Order

- **Fase 1**: T001 antes de tudo; T002 em paralelo.
- **Fase 2**: T003, T004 e T007 (testes) em paralelo; T005 depois da T003 e da T004; T006 independe de
  T005 e pode correr junto; T008 depois da T005, da T006 e da T007; T009 depois da T008; T010 a qualquer
  momento depois da T005; T011 por último.
- **US1** depende da Fase 2 inteira. T012 e T013 (testes) em paralelo; T014 → T015 → T016 → T017; T018 e
  T019 depois da T015.
- **US2 → US3**: escrevem no mesmo template e no mesmo módulo de frases que a US1, e correm em sequência
  depois dela; os testes de cada uma (T020, T023) podem ser escritos em paralelo com a história anterior.
- **US4** depois da US1 (o parcial da população entra no template dela); pode correr junto da US2 ou da
  US3 se uma pessoa só não estiver nos dois arquivos de frases ao mesmo tempo.
- **US5** depois da US3 e da US4.
- **Fase 8**: T030 e T032 a qualquer momento depois da US1; T031 depois da US1 (o teste que muda é o do
  despacho); T033 a qualquer momento; T034 por último.

## Parallel Example: Fase 2

```text
T003 test_simulacao_ordem.py   ||   T004 test_simulacao_populacao.py   ||   T007 test_simulacao_resumo.py
T006 corte_da_ordem público     ||   T005 sorteios/domain/simulacao.py (depois de T003 e T004)
```

## Parallel Example: User Story 1

```text
T012 cenários da US1   ||   T013 recusa da semente
```

## Implementation Strategy

### O motor primeiro, autorizável à parte

A Fase 2 entrega valor sozinha: o motor da prévia do sorteio, provado igual ao oficial, com o resumo
medido — e sem nenhuma mudança de tela. Ela pode ser autorizada e revisada antes da interface, como a
Fase 2 da `095` foi.

### MVP: até a US1

Com a Fase 2 e a US1, o elaborador vê, numa semente fictícia, que o autodeclarado está nas duas listas e
em posições diferentes. É o primeiro fato que a composição esconde hoje.

### Incremento: US2 e US3

A US2 mostra a consequência na rodada, e a US3 a frequência dela. As duas juntas são o critério de
sucesso (SC-925). A US4 deixa o elaborador trocar a população sugerida pela procura que conhece, e a US5
fecha a acessibilidade.
