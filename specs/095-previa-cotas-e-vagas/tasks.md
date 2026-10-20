# Tasks: Prévia interativa da classificação — fatia 2

**Input**: Design documents from `specs/095-previa-cotas-e-vagas/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: pedidos pela spec — a equivalência por recorte (FR-2340), a preservação do resultado oficial
nas extrações (FR-2339) e a ausência de efeito (FR-2341) são requisitos, e as extrações só são seguras
com a linha de base escrita antes.

**Organization**: a Fase 2 são as duas extrações da ocupação — **independentes da interface da `094`**,
e autorizáveis à parte, como as T003 a T009 da `094` foram. A Fase 3 é o motor da prévia por recorte, e
depende da `simular` da `094` (a T013 de lá). As fases das histórias dependem da interface da `094`
inteira (D-001).

**20/10/2026**: o usuário autorizou seguir com a `095`, e a Fase 2 — a única que não depende da
interface da `094` — foi feita numa branch própria, `claude/095-extracao-da-ocupacao` (PR #319).
As fases 3 em diante foram feitas no mesmo dia, depois que a interface da `094` foi publicada no
PR #320: a branch `claude/095-previa-por-recorte` sai da dela e traz a Fase 2 junto, e o PR é
empilhado sobre o #320, sem merge.

**O que mudou em relação ao planejado, e por quê:**

- **A rodada de ocupação mora na `ocupacao`, e não em `classificacao/application/previa.py`.** A `094`
  já tinha mostrado o limite: `classificacao` não importa `ocupacao` (`tests/test_dependencia_da_ocupacao.py`).
  A rodada é `ocupacao/domain/rodada_da_previa.py`, pura, e chega a `simular` injetada em
  `apurar_recortes`, como a fronteira das vagas chega em `apurar_vagas`.
- **A T028 está em `tests/interface/test_previa_por_recorte.py`**, como a da `094` está no teste de
  interface dela: a captura de consultas é a do pedido real.
- **A T030 não foi feita**, por decisão do usuário de 20/10: nenhuma rodada nova de protótipo; a
  experiência se avalia na interface real.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente)
- **[Story]**: a história da spec (US1 a US6)
- Caminhos relativos à raiz do repositório

---

## Phase 1: Setup

**Purpose**: ponto de partida conferido

- [x] T001 Conferir que a interface da `094` está na `main` — `classificacao/application/previa.py`, `classificacao/domain/cenarios_da_previa.py`, `interface/previa_da_classificacao.py`, `interface/templates/interface/_previa_da_classificacao.html` e `interface/static/interface/telas/previa-da-classificacao.css` em `backend/processo_seletivo/` —, e ler o contrato do fragmento dela em `specs/094-previa-da-classificacao/contracts/fragmento-da-previa.md`. Sem isso, só a Fase 2 pode começar
- [x] T002 [P] Rodar `specs/095-previa-cotas-e-vagas/prototipo/reproducao.py` de dentro de `backend/` e conferir a saída contra a R-001 de `specs/095-previa-cotas-e-vagas/research.md`; divergência é sinal de que o motor mudou desde 20/10, e a R-001 precisa ser refeita antes de seguir

---

## Phase 2: Foundational — as duas extrações da ocupação (D-005)

**Purpose**: "quem ocupa pela ampla" e "há quem ocupar" passam a ser funções puras chamadas pelo caminho
oficial, sem mudar resultado nenhum. Não dependem da `094`.

**⚠️ CRITICAL**: a T003 entra verde **antes** da T004 e da T005, contra o código de hoje.

- [x] T003 Escrever a linha de base em `backend/tests/integration/ocupacao/test_extracao_da_ocupacao_equivale.py`: por cenário com reserva no banco — concomitância dentro das vagas da ampla; autodeclarado suplente da ampla; titular da ampla eliminado na Etapa governada (o achado da R-002, que **continua** excluído da reservada); reservada toda ocupando pela ampla; reservada sem ato vigente; empate não julgado na fronteira da ampla (a exceção crua, como hoje) —, fixar o valor de `ocupacao.application.selectors.ocupantes_da_ampla` e de `ocupacao.application.movimento.ha_quem_ocupar`, e o número de consultas de `ocupacao.application.emissao._apurar` e da fila em `convocacao/application/selectors.py`. Verde contra o código atual. *Feito com uma diferença: o empate na fronteira da ampla ficou no unitário da T004 — o sorteio do certame de teste não produz empate residual —, e o número de consultas foi preso nas duas funções (8 e 2), e não em `_apurar` e na fila, que as chamam sem consulta a mais; os orçamentos delas são os da suíte (T006).*
- [x] T004 Extrair `ocupantes_pela_ampla` para `backend/processo_seletivo/ocupacao/domain/apuracao.py` conforme `specs/095-previa-cotas-e-vagas/contracts/ocupacao-pura.md` — `habilitadas` em `titulares_iniciais` e **não** em `ocupantes` —, fazer `selectors.ocupantes_da_ampla` consultar e delegar, e cobrir a função pura em `backend/tests/unit/ocupacao/test_ocupantes_pela_ampla.py`
- [x] T005 [P] Extrair `ha_quem_ocupar(*, posicoes, ja_ocupadas)` para `backend/processo_seletivo/ocupacao/domain/reversao.py`, fazer `ocupacao/application/movimento.py::ha_quem_ocupar` ler as posições e delegar, e cobrir a função pura — inclusive posições de quem ocupa pela ampla contando — em `backend/tests/unit/ocupacao/test_ha_quem_ocupar.py`
- [x] T006 Rodar a T003 e as suítes de `backend/tests/unit/ocupacao/`, `backend/tests/integration/ocupacao/`, `backend/tests/unit/convocacao/`, `backend/tests/integration/convocacao/` e `backend/tests/performance/test_convocacao.py` sem alterar teste nenhum; e `make lint check test-pg` em `backend/`. *Em 20/10: 12357 passando e 12 pulados — os onze da suíte e o da contagem de tokens, sem o grupo `assistente` nesta worktree —, nenhum teste existente alterado.*

**Checkpoint**: caminho oficial igual, com as duas decisões no domínio.

---

## Phase 3: Foundational — a prévia por recorte

**Purpose**: recortes, rodada de ocupação, participantes e população com Modalidades, puros. Depende
da `simular` da `094`.

- [x] T007 [P] Escrever `backend/tests/unit/classificacao/test_cenarios_com_modalidade.py`: a atribuição da R-005 é determinística; não muda nota nem a ordem da ampla (com e sem Modalidades declaradas, a ampla é igual); cada candidato tem no máximo uma Modalidade; os plantados da fatia 1 não recebem Modalidade; nenhum nome fictício contém código ou nome de Modalidade; a falta de espaço para plantar é dita
- [x] T008 Implementar a atribuição de Modalidade em `backend/processo_seletivo/classificacao/domain/cenarios_da_previa.py`, depois da população estável da `094`, com as fronteiras de cada reservada viajando em `populacao` (R-005, contrato do fragmento)
- [x] T009 [P] Escrever `backend/tests/unit/classificacao/test_previa_por_recorte.py` com a matriz da R-001 sobre `simular`: ordem e faixa por recorte; alvo fixo e suplentes iguais em todo recorte; recorte sem linha; quem ocupa pela ampla dentro e fora das vagas; posições da faixa tomadas e autodeclarados além; as quatro quantidades; reversão ausente, por saldo e por esgotamento; efetivas da próxima apuração da ampla; empate na fronteira da ampla (reservadas dependentes) e da reservada; corte impedido na ampla e numa reservada; ordem vazia; união dos participantes; limite de recortes; e `simular` em até 1 segundo com 500 candidatos e 7 recortes (SC-876)
- [x] T010 Estender `backend/processo_seletivo/classificacao/application/previa.py`: `recortes_do_perfil` e `linha_do_quadro` sobre o snapshot; ordem, corte e trajetória por recorte; a rodada da R-004 com `apurar`, `ocupantes_pela_ampla`, `reversao.ha_quem_ocupar` e `quantidade_a_reverter`; os estados da ocupação do `data-model.md`; os participantes da R-008; o limite da R-006
- [x] T011 Escrever `backend/tests/integration/classificacao/test_previa_por_recorte_equivale_ao_oficial.py`: os casos da FR-2340 pelos dois caminhos — o oficial com ordens, cortes e apurações emitidos no banco, a prévia com os mesmos dados —, comparando ordens, faixas, quem ocupa pela ampla, quantidades e cedido por recorte; e a sentinela: com o caminho oficial alterado (`monkeypatch` em `ocupantes_pela_ampla` e em `ha_quem_ocupar`), o teste reprova

**Checkpoint**: `simular` responde por recorte, e a equivalência prova que é o motor oficial.

---

## Phase 4: User Story 1 — Ver a ordem de cada recorte e quem concorre em qual (Priority: P1) 🎯 MVP

**Goal**: o resumo por recorte na jornada e o seletor no detalhe.

**Independent Test**: num Perfil com duas reservadas, cada recorte mostra a ordem do caminho oficial; a
ampla contém todos; Perfil sem reservada fica igual à fatia 1.

- [x] T012 [P] [US1] Escrever em `backend/tests/interface/test_previa_por_recorte.py` os cenários 1 a 5 da US1: resumo por recorte no marco da jornada, seletor de recorte no detalhe com a mesma população, posição na ampla e Modalidade nas linhas, a Modalidade apontada como ampla fora dos recortes, Perfil sem reservada sem seletor, recorte vazio dito como tal, `recorte` inválido caindo na ampla com a frase
- [x] T013 [US1] Ler `recorte` no fragmento em `backend/processo_seletivo/interface/views.py` (R-007) e passá-lo a `simular`
- [x] T014 [US1] Escrever as frases dos recortes em `backend/processo_seletivo/interface/previa_da_classificacao.py`: o rótulo da ampla como universo inteiro, o resumo por recorte, a frase do recorte vazio, os dois números quando a faixa da reservada difere das vagas (FR-2307), o corte não apurável sem linha, a recusa nomeando o recorte
- [x] T015 [US1] Acrescentar o seletor de recorte (`<select>` com `<label>`, `hx-get` no `change`, dentro do formulário do painel), o resumo por recorte na jornada e as colunas da posição na ampla e da Modalidade em `backend/processo_seletivo/interface/templates/interface/_previa_da_classificacao.html`

**Checkpoint**: a US1 funciona sozinha, com o bloco da ocupação ainda o da fatia 1.

---

## Phase 5: User Story 2 — Ver onde cada um ocuparia vaga, e quantas ficariam sem ocupante (Priority: P1)

**Goal**: o bloco da ocupação com as quatro quantidades por recorte e a concomitância visível.

**Independent Test**: as quantidades e o conjunto dos que ocupam pela ampla são os da equivalência
(T011); nenhum recorte não avaliado mostra número.

- [x] T016 [P] [US2] Escrever em `backend/tests/interface/test_previa_por_recorte.py` os cenários 1 a 8 da US2: "ocuparia pela ampla" e a vaga que continua reservada, sem movimento; suplente da ampla sem a marca; a frase da faixa tomada e dos que ficaram além; a ampla parada e as reservadas dependentes, sem número; só a reservada parada; sem linha, não avaliada; as hipóteses e "uma rodada"; o Perfil sem reservada com as quatro quantidades da ampla
- [x] T017 [US2] Escrever as frases da ocupação em `backend/processo_seletivo/interface/previa_da_classificacao.py`: as quatro quantidades com "vagas sem ocupante nesta hipótese", as hipóteses da FR-2320, os estados do `data-model.md`, a frase da FR-2319 como comportamento atual (DP-1), e a concomitância como regra que vale sempre (FR-2316)
- [x] T018 [US2] Acrescentar o bloco da ocupação por recorte e a marca "ocuparia pela ampla" em `backend/processo_seletivo/interface/templates/interface/_previa_da_classificacao.html`, e as regras de toda classe nova em `backend/processo_seletivo/interface/static/interface/telas/previa-da-classificacao.css`

---

## Phase 6: User Story 3 — Ver o efeito da reversão declarada, ou da ausência dela (Priority: P1)

**Goal**: a quantidade cedida por reservada, ou a frase de que não reverte.

**Independent Test**: para cada espécie e para a ausência, o cedido é o da equivalência (T011), e sem
declaração nenhuma quantidade cedida aparece.

- [x] T019 [P] [US3] Escrever em `backend/tests/interface/test_previa_por_recorte.py` os cenários 1 a 5 da US3: "não reverte" sem declaração; cedido por saldo e as efetivas da próxima apuração da ampla, sem refazê-la; esgotamento sem cessão com a frase do comportamento atual e os dois números; nada a reverter; a espécie lida do gravado, com a origem dita
- [x] T020 [US3] Escrever as frases da reversão em `backend/processo_seletivo/interface/previa_da_classificacao.py`, com a espécie pelo rótulo do passo Perfis, o destino "a ampla concorrência deste Perfil", "seria cedida" (nunca no passado) e a frase de DP-2 como comportamento atual (FR-2328, FR-2337)
- [x] T021 [US3] Acrescentar a reversão ao bloco da ocupação em `backend/processo_seletivo/interface/templates/interface/_previa_da_classificacao.html`

**Checkpoint**: as três histórias P1 entregam o critério de sucesso.

---

## Phase 7: User Story 4 — Ver o processo seletivo com os recortes (Priority: P2)

**Goal**: a união na Etapa alimentada e a ocupação fora da sequência, na jornada.

**Independent Test**: o número de quem poderia participar é o tamanho da união por pessoa das faixas.

- [x] T022 [P] [US4] Escrever em `backend/tests/interface/test_previa_por_recorte.py` os cenários 1 a 3 da US4: a união e quantos as reservadas acrescentam, a ocupação fora da sequência, o número dependente quando o corte de uma reservada não sairia
- [x] T023 [US4] Estender a Etapa alimentada e o ponto do marco em `backend/processo_seletivo/interface/previa_da_classificacao.py` e no template da jornada em `backend/processo_seletivo/interface/templates/interface/_previa_da_classificacao.html`, e o "o que mudou" por recorte (FR-2334) em `backend/processo_seletivo/classificacao/application/previa.py`

---

## Phase 8: User Story 5 — Escolher um caso-limite de reserva (Priority: P2)

**Goal**: os seis casos-limite da FR-2332.

**Independent Test**: cada caso, com a configuração de referência, produz a situação que o nomeia.

- [x] T024 [P] [US5] Escrever em `backend/tests/unit/classificacao/test_cenarios_com_modalidade.py` e em `backend/tests/interface/test_previa_por_recorte.py` os cenários 1 a 3 da US5 e um por caso-limite, inclusive o "não ocorre e por quê"
- [x] T025 [US5] Acrescentar os seis casos-limite a `backend/processo_seletivo/classificacao/domain/cenarios_da_previa.py`, no mesmo seletor da `094`, sem regra por nome de Modalidade (D-006)

---

## Phase 9: User Story 6 — No celular e com leitor de tela (Priority: P3)

**Goal**: 375 px e o anúncio por recorte.

**Independent Test**: sem rolagem horizontal ao trocar recorte; o anúncio tem o resumo de cada recorte.

- [x] T026 [P] [US6] Escrever em `backend/tests/interface/test_previa_por_recorte.py` a medida por CSSOM a 375 px do seletor e do bloco da ocupação empilhado, o anúncio por recorte e a ausência de estilo e script no HTML devolvido
- [x] T027 [US6] Ajustar `backend/processo_seletivo/interface/static/interface/telas/previa-da-classificacao.css` (bloco empilhado abaixo de 40rem, seletor na cabeça do detalhe) e a frase do anúncio em `backend/processo_seletivo/interface/previa_da_classificacao.py`

---

## Phase 10: Polish & Cross-Cutting Concerns

- [x] T028 [P] Escrever, em `backend/tests/interface/test_previa_por_recorte.py`, nenhuma escrita em ordem, corte, apuração, movimento, efeito, rascunho ou trilha em abrir, recalcular, trocar recorte e cenário e fechar; nenhuma consulta a `Inscricao` nem a documentos (FR-2341, FR-2342)
- [x] T029 [P] Passar pelos guardiões do repositório: a lista literal de `backend/tests/test_vocabulario_da_composicao.py`, uma regra na folha para toda classe nova, a varredura de vocabulário proibido ("convocado", "aprovado", "matriculado", "cotista aprovado") nas frases de `backend/processo_seletivo/interface/previa_da_classificacao.py`, e nenhum `}}` em CSS
- [ ] ~~T030~~ *Não feita: decisão do usuário de 20/10, sem nova rodada de protótipo.* Estender o protótipo navegável da `094` (`specs/094-previa-da-classificacao/prototipo/`, depois do merge do #316) com o seletor de recorte, o bloco da ocupação e a reversão, reaproveitando `specs/095-previa-cotas-e-vagas/prototipo/reproducao.py`, e capturar desktop e 375 px em `specs/095-previa-cotas-e-vagas/prototipo/capturas/`
- [x] T031 *Roteiro escrito; a validação com pessoas fica aberta até o relato do usuário.* Estender o roteiro de compreensão da `094` com as perguntas da SC-870 em `specs/095-previa-cotas-e-vagas/roteiro-de-compreensao.md`
- [ ] T032 Conferir `specs/095-previa-cotas-e-vagas/rastreabilidade.md` contra o implementado, rodar o roteiro de `specs/095-previa-cotas-e-vagas/quickstart.md` e `make lint check test-pg` em `backend/`

---

## Dependencies & Execution Order

- **Fase 2** (T003 → T004, T005 → T006): depende só da `main` de hoje. T004 e T005 tocam arquivos
  diferentes e podem correr juntas depois da T003.
- **Fase 3**: depende da T013 da `094` (`simular`) e da Fase 2. T007 e T009 em paralelo; T008 antes da
  T010; T011 por último.
- **US1 → US2 → US3**: a US2 e a US3 escrevem no mesmo template e no mesmo módulo de frases que a US1,
  e por isso correm em sequência; os testes de cada uma podem ser escritos em paralelo.
- **US4, US5, US6**: depois da US3; US5 toca `cenarios_da_previa.py`, que a US4 não toca, e podem correr
  juntas.
- **Fase 10**: T028 e T029 a qualquer momento depois da US1; T030 depois do merge do #316; T032 por
  último.

## Parallel Example: Fase 3

```text
T007 test_cenarios_com_modalidade.py   ||   T009 test_previa_por_recorte.py
```

## Parallel Example: User Story 2

```text
T016 (testes da US2) enquanto T014 e T015 da US1 terminam
```

## Implementation Strategy

### Antes da interface — autorizável à parte

A Fase 2 entrega valor sozinha: tira do caminho oficial as duas decisões que a prévia precisa, sob
linha de base, sem mudar resultado. É o mesmo corte que a `094` fez com a T003 a T009, e pode correr
enquanto a interface da `094` espera decisão.

### MVP

Fases 3 a 6 — as três histórias P1. É o que entrega o critério de sucesso: em que lista cada um
ocuparia, quantas vagas ficariam sem ocupante, e o que a reversão faria.

### Incremental

US4 (a jornada com a união) → US5 (casos-limite) → US6 (celular) → Fase 10. Cada passo é verificável
pela matriz de rastreabilidade.
