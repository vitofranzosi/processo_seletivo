---

description: "Tarefas da 041 — o Perfil de Vaga na visão institucional"
---

# Tasks: O Perfil de Vaga na visão institucional

**Input**: Design documents from `specs/041-perfil-na-visao-institucional/`

**Prerequisites**: [plan.md](./plan.md) · [spec.md](./spec.md) · [research.md](./research.md) ·
[data-model.md](./data-model.md) · [contracts/](./contracts/) · [quickstart.md](./quickstart.md)

**Tests**: **incluídos**. A Constituição exige cobertura específica, a §18 da `040` estabeleceu o
padrão, e esta feature tem uma garantia que **nenhum teste do repositório cobre hoje** — a validade
estrutural do HTML (`R-007`).

**Organization**: por jornada, nas duas prioridades da spec.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode correr em paralelo — arquivo distinto, sem dependência pendente
- **[Story]**: `US1` · `US2`; Setup, Foundational e Polish não têm rótulo

---

## Phase 1: Setup

**Purpose**: partir de uma linha de base conhecida. A `040` já está de pé; nada se instala aqui.

- [X] T001 Conferir as dependências de desenvolvimento de `backend/pyproject.toml` com `uv sync --extra dev`, e o banco pelos alvos de `backend/Makefile` — a contagem `N de M` **não** pode começar em `0`
- [X] T002 Rodar `backend/tests/unit/test_visao_institucional.py`, `backend/tests/interface/test_visao_geral.py`, `backend/tests/performance/test_visao_institucional.py` e `backend/tests/interface/test_acessibilidade.py` e registrar a contagem — é contra ela que as regressões desta feature aparecem

**Checkpoint**: linha de base verde e contada.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: a leitura por Perfil. **Nenhuma jornada começa antes desta fase** — as duas leem os
mesmos Perfis.

- [X] T003 [P] Implementar a forma `Reserva` — três espécies, e `limite` obrigatório em `LIMITADO` — em `backend/processo_seletivo/interface/visao_geral.py` (`FR-608`, data-model §2.2)
- [X] T004 Fazer `vagas_do_conteudo` devolver também o **conjunto completo** dos Perfis da versão vigente, e a quantidade de cada um, em `backend/processo_seletivo/interface/visao_geral.py` — hoje ela guarda só os ids dos que publicam vaga, e por isso *"Perfil sem vaga"* e *"Perfil que não existe mais"* caem no mesmo ramo (`R-003`)
- [X] T005 Fazer `contagens_por_edital` acumular **rascunho por Perfil** em `backend/processo_seletivo/interface/visao_geral.py` — a consulta já traz `profile_id` e o valor é descartado; é a mesma consulta, outro dicionário (`FR-610`, `R-002`)
- [X] T006 [P] Implementar a forma `PerfilDaLinha` em `backend/processo_seletivo/interface/visao_geral.py`, reusando `Numero`, `Ausencia` e `Marca` da `040` — tipos paralelos divergiriam na primeira mudança (data-model §2.1)
- [X] T007 Implementar `perfis_do_edital(conteudo, contagem, periodo)` em `backend/processo_seletivo/interface/visao_geral.py`, com a razão do Perfil saindo da **mesma** função que a do Edital usa (`FR-611`)
- [X] T008 Acrescentar `perfis`, `submetidas_sem_perfil` e `rascunhos_sem_perfil` a `LinhaDoEdital`, e **remover `tem_reserva`**, em `backend/processo_seletivo/interface/visao_geral.py` — ele era a resposta grosseira que a expansão substitui, e manter os dois criaria duas formas de dizer a mesma coisa com precisões diferentes (data-model §2.3). **No mesmo passo, atualizar `assert linha.tem_reserva` em `backend/tests/unit/test_visao_institucional.py`**, que o lê hoje: sem isso a Fase 2 quebra a linha de base que a `T002` acabou de medir, e a falha aparece longe da causa

**Checkpoint**: os Perfis são deriváveis sem requisição; nada mudou na tela ainda.

---

## Phase 3: User Story 1 — Onde, dentro do Edital, a procura faltou (P1) 🎯 MVP

**Goal**: expandir a linha e ver os Perfis com vagas, demanda e razão próprias — e o Perfil vazio
saltando à vista.

**Independent Test**: um Edital com dois Perfis de 20 vagas — um com 7 inscrições, outro com
nenhuma —, expandir a linha e identificar o vazio sem sair da página.

### Tests for User Story 1 ⚠️

- [X] T009 [P] [US1] Testes dos Perfis em `backend/tests/unit/test_visao_institucional.py` — saem da versão vigente, com denominação e as **três** espécies de reserva, a limitada com o seu limite (`SC-217`); e o **código** ao lado da denominação e nunca em coluna própria (`FR-607`); e a localidade **como publicada**, com o caso **ausente** afirmado: Perfil sem `locality` não escreve *"não informada"*, porque isso afirmaria uma omissão que o Edital pode nunca ter tido (`FR-609`)
- [X] T010 [P] [US1] Testes da gramática no Perfil em `backend/tests/unit/test_visao_institucional.py` — vagas `0` é zero legítimo, e a razão é **não aplicável** sem vaga imediata (`FR-611`, `SC-220`)
- [X] T011 [P] [US1] Teste da reconciliação em `backend/tests/unit/test_visao_institucional.py` — `Σ perfis.vagas` e `Σ perfis.submetidas` batem com a linha; e a **razão do Edital é recalculada** dos totais elegíveis, com um caso que a soma e a média das razões dos Perfis **não** produziriam: dois Perfis de 20 vagas com `1,0` e `3,0` dão `2,0` no Edital, nunca `4,0` nem `2,0` por média (`FR-612`)
- [X] T012 [P] [US1] Teste do Perfil removido por Retificação em `backend/tests/unit/test_visao_institucional.py` — a inscrição conta no Edital, não é atribuída a Perfil algum, e a diferença é contada (`FR-613a`)
- [X] T013 [P] [US1] Teste da expansão na tela em `backend/tests/interface/test_visao_geral.py` — ela existe, nasce **recolhida**, e traz as colunas do contrato (`FR-606`, `FR-607`); **e a linha principal continua com as sete colunas do Edital** (`FR-617`), porque quem a substituísse por linhas de Perfil passaria por `T014` sem nada acusar
- [X] T014 [P] [US1] **Teste de estrutura** em `backend/tests/interface/test_visao_geral.py` — o `<details>` está dentro de um `<td>`, e **não** solto na `<tr>`. *Nenhum teste deste repositório cobre estrutura de tabela hoje (`R-007`): sem este caso, o HTML inválido passa por toda a suíte*

### Implementation for User Story 1

- [X] T015 [US1] Criar `backend/processo_seletivo/interface/templates/interface/_perfis_do_edital.html` — a segunda `<tr>`, o `<td colspan>`, o `<details>` recolhido e a tabela interna com `<caption>` e `<th scope="col">` (`R-001`)
- [X] T016 [US1] **Tornar transitiva a resolução de `include` em `folha_da_pagina`**, em `backend/tests/interface/test_acessibilidade.py` — ela hoje só enxerga inclusão **direta**, e o parcial novo é incluído por outro parcial: sem isso, as classes dele seriam acusadas de órfãs, ou — pior — a próxima tela escaparia do guardião em silêncio
- [X] T017 [US1] Incluir o parcial e **remover `tem_reserva`** de `backend/processo_seletivo/interface/templates/interface/_linha_do_edital.html`, mantendo a linha do Edital com as sete colunas
- [X] T018 [US1] Garantir em `backend/processo_seletivo/interface/templates/interface/_perfis_do_edital.html` que **o controle é o `<summary>`, e não a linha** — com nome acessível nomeando o Edital e o estado declarado —, e acrescentar o caso em `backend/tests/interface/test_visao_geral.py`: o link do Edital continua navegando, e a linha **não** alterna a expansão (`FR-620`)
- [X] T019 [US1] Acrescentar o estilo da expansão ao bloco `estilo_da_pagina` de `backend/processo_seletivo/interface/templates/interface/visao_geral.html` — **na página, nunca na base**: a `040` pagou 4 KB de folha de uma tela viajando em todas, e a tela de distribuição estourou o teto
- [X] T020 [US1] Escrever a declaração da diferença **em texto** em `backend/processo_seletivo/interface/templates/interface/_perfis_do_edital.html` — presente só quando há diferença, como a ressalva do denominador da `040`; e **nenhuma linha, agrupamento ou rótulo** fazendo as vezes de Perfil — *Outros*, *Removidos*, *Sem Perfil* — para acomodá-las (`FR-613a`)

**Checkpoint**: a `US1` entra em produção sozinha. É o MVP.

---

## Phase 4: User Story 2 — A Atenção passa a dizer quantos Perfis (P2)

**Goal**: as marcas calculadas no Perfil, e a linha resumindo *quantos de quantos*.

**Independent Test**: um Edital com razão global **acima** de 1 e um Perfil vazio — hoje sem marca
nenhuma, e sob esta história marcado.

### Tests for User Story 2 ⚠️

- [X] T021 [P] [US2] Teste da mudança de nível em `backend/tests/unit/test_visao_institucional.py` — o Edital com razão global 2,1 e um Perfil vazio **recebe** marca, e hoje não recebe (`FR-613`, `SC-218`)
- [X] T022 [P] [US2] Teste de `sem procura` sem denominador em `backend/tests/unit/test_visao_institucional.py` — um Perfil só de cadastro de reserva que encerrou sem nenhuma inscrição é marcado; só *demanda abaixo da oferta* exige denominador (`FR-615`)
- [X] T023 [P] [US2] Teste do resumo em `backend/tests/unit/test_visao_institucional.py` — *"N de M Perfis…"* por espécie, **cada uma com o seu denominador**: *sem procura* sobre todos os vigentes, *demanda abaixo* só sobre os com vaga imediata. Num Edital de 5 Perfis com 3 publicando vaga e 2 abaixo, a frase é *"2 de 3"* e **nunca** *"2 de 5"*; e com `M == 1`, a mensagem do próprio Perfil, sem *"1 de 1"* (`FR-614`, `R-004`)

### Implementation for User Story 2

- [X] T024 [US2] Fazer `_marcas` operar sobre os Perfis, e não sobre o agregado, em `backend/processo_seletivo/interface/visao_geral.py` (`FR-613`)
- [X] T025 [US2] Implementar o resumo da linha em `backend/processo_seletivo/interface/visao_geral.py`, por espécie, com o caso de Perfil único (`FR-614`)
- [X] T026 [US2] **Anotar na `040` o que esta feature substitui**, em `specs/040-visao-institucional-dos-processos/spec.md`: a `FR-602`, apontando para a `FR-613` e a `FR-614` (`FR-616`); **e a §11.1**, cuja coluna *Vagas* descreve *"a marca de cadastro de reserva quando houver"* — que a `T008` remove. Duas frases vigentes descrevendo o que o produto já não faz, e a segunda é fácil de esquecer justamente por não ser requisito

**Checkpoint**: a coluna Atenção responde *onde*, e não só *se*.

---

## Phase 5: User Story 3 — Ver só o que pede atenção (P3)

**Goal**: um booleano que reduz a tabela aos Editais com algum Perfil marcado.

**Independent Test**: com um Edital marcado e um sem marca no recorte, ligar o filtro e ver a tabela
reduzir-se a um — e o consolidado acompanhar.

### Tests for User Story 3 ⚠️

- [X] T027 [P] [US3] Teste do filtro em `backend/tests/interface/test_visao_geral.py` — a tabela reduz aos marcados e **o consolidado muda junto**, como nos demais filtros da `040` (`FR-621`, `SC-221`)
- [X] T028 [P] [US3] Teste do recorte vazio pelo filtro em `backend/tests/interface/test_visao_geral.py` — nenhum Edital marcado declara recorte vazio, sem afirmar nada sobre o acervo (`FR-621`)

### Implementation for User Story 3

- [X] T029 [US3] Implementar o filtro `atencao` em `backend/processo_seletivo/interface/visao_geral.py`, saneado como os demais, aplicado **depois** da materialização — a marca só existe depois de ler o conteúdo publicado, e empurrá-lo para o `SQL` é impossível, não caro (`FR-621`, `R-009`)
- [X] T030 [US3] Acrescentar o controle **Somente com atenção** ao formulário de `backend/processo_seletivo/interface/templates/interface/visao_geral.html`, com rótulo associado

**Checkpoint**: numa lista longa, a Coordenação vê só o que precisa olhar.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T031 [P] Teste do orçamento por Perfil em `backend/tests/performance/test_visao_institucional.py` — contagem **igual** entre um Edital de 1 Perfil e um de 12, e a igualdade entre 3 e 60 Editais preservada (`FR-618`, `SC-216`)
- [X] T032 [P] Estender a varredura de dado pessoal ao conteúdo **expandido** em `backend/tests/interface/test_visao_geral.py` — a expansão é agregada por Perfil e não pode trazer nome, CPF, e-mail nem protocolo (`SC-210` da `040`)
- [X] T033 [P] Teste de legibilidade sem cor em `backend/tests/interface/test_visao_geral.py` — as marcas do Perfil e o resumo da linha aparecem no texto visível (`FR-614`)
- [X] T034 Conferir se a prosa visível de `backend/processo_seletivo/interface/templates/interface/_perfis_do_edital.html` usa *recorte*, *geração* ou *faixa*; usando, acrescentar a tela a `TELAS` em `backend/tests/test_vocabulario_da_composicao.py` **no mesmo commit** — a lista é literal, e a tela escapa da regra em silêncio
- [X] T035 Conferir a largura de telefone de `backend/processo_seletivo/interface/templates/interface/_perfis_do_edital.html` — a tabela interna rola **dentro da moldura**, e `documentElement.scrollWidth` não passa da janela
- [X] T036 Percorrer os **catorze** passos de `specs/041-perfil-na-visao-institucional/quickstart.md` pela interface — é o cenário do Princípio VI (`SC-215`). **A `SC-219` é verificada só aqui, e de propósito**: abrir e fechar por teclado é comportamento nativo de `<details>`, e automatizá-lo testaria o navegador, não o produto
- [X] T037 Escrever `specs/041-perfil-na-visao-institucional/rastreabilidade.md` cobrindo **cada** `FR-606` a `FR-619` e `SC-215` a `SC-220` — inclusive o sufixo de letra da `FR-613a`, que o guardião cobra à parte
- [X] T038 Rodar os alvos de `backend/Makefile` com `cd backend && make lint check test-pg` — `lint` são **dois** passos, e não editar arquivo durante a execução — **7579 passaram, 11 puladas, 0 falharam** (12m44s, 2ª execução). A primeira acusou uma classe sem regra na folha, pega pelo guardião de classes órfãs.

---

## Dependencies & Execution Order

```text
Phase 1 (Setup)
   ↓
Phase 2 (Foundational)   ← T004 e T005 são a mesma leitura; T003/T006 em paralelo
   ↓
Phase 3 (US1) 🎯 MVP
   ↓
Phase 4 (US2)            ← depende da US1: as marcas operam sobre os Perfis que ela deriva
   ↓
Phase 5 (US3)            ← depende da US2: filtra pela marca que ela passa a calcular
   ↓
Phase 6 (Polish)
```

**A `US2` depende da `US1`**, e não é independente dela: as marcas por Perfil precisam dos Perfis. É
diferente da `040`, onde as três jornadas eram paralelas — e registrar a diferença é o que impede
alguém de tentar a `US2` primeiro.

**Uma dependência dura dentro da Fase 3**: `T015` antes de `T016`. O guardião só pode ser estendido
depois que existir o parcial que prova a extensão.

### Paralelismo por fase

| Fase | Podem correr juntas |
|---|---|
| 2 | `T003`, `T006` |
| 3 | `T009` a `T014` (os seis testes) |
| 4 | `T021`, `T022`, `T023` |
| 5 | `T027`, `T028` |
| 6 | `T031`, `T032`, `T033` |

---

## Implementation Strategy

**MVP = Phase 1 + Phase 2 + Phase 3.** Vinte tarefas — `T001` a `T020` —, e a página passa a
responder *onde, dentro do Edital, a procura faltou*.

**As duas seguintes são uma cadeia, e não alternativas.** A `US2` muda onde `_marcas` opera, sobre
Perfis que a `US1` já deriva; a `US3` filtra pela marca que a `US2` passa a calcular. Nenhuma pede
retrabalho, e nenhuma pode pular a anterior.

**A ordem de risco**, para quem escolher por onde começar:

- **`T015`** é a que erra de um jeito que nenhum teste pega: `<details>` fora de um `<td>` é HTML que
  cada navegador conserta à sua maneira, e a suíte inteira passa. É por isso que `T014` existe.
- **`T016`** é a que **não falha** quando esquecida: o guardião de classes continua verde e para de
  cobrir a tela nova, em silêncio. Foi o mesmo buraco que a `040` abriu ao escopar o estilo — e que
  a segunda execução da suíte dela pegou por sorte de ordem.
- **`T024`** é a que muda comportamento já entregue: Editais que hoje não recebem marca passarão a
  receber. É a feature, e é por isso que `T026` existe.
- **`T004`/`T005`** são a mesma consulta lida de duas maneiras; quem mexer numa sem a outra produz um
  total que não fecha com as partes.
