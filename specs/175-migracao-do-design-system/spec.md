# Feature Specification: A migração do design system para toda a gestão

**Feature Branch**: `claude/173-migracao-ds-antes-e-depois` (o nome da branch é anterior à numeração;
a pasta é a `175`), empilhada sobre a branch do piloto (`claude/172-piloto-implementacao`, PR #564)

**Created**: 2026-11-15

**Status**: **Implementada antes de especificada**, e esta spec existe para corrigir isso. O usuário
pediu, em 15/11, para seguir com a migração e ver o antes e o depois; a branch levou os padrões do
piloto a toda a gestão e mediu o resultado (PR #565). A revisão de código apontou que a mudança
alcança a base de toda a gestão sem pasta em `specs/`, contra a regra do projeto ("Cada incremento é
uma pasta em `specs/`"), e o usuário aprovou a correção. Esta spec registra como requisito o que a
branch fez, com a medida, e diz o que ela **não** tem: **a validação com a equipe não aconteceu, e a
aprovação da migração depende do usuário.** O merge é do usuário.

**A exceção à ordem dos artefatos foi aceita pelo usuário em 15/11/2026.** O `/speckit-analyze` acusou
um crítico que não se corrige por edição: a implementação veio antes da spec e do plano, contra a
Constituição ("Implementação substancial NÃO DEVE começar antes de especificação clara e plano
aprovado"). Perguntado *"Você aceita a exceção da spec 175 escrita depois da migração?"*, o usuário
respondeu: *"Aceito a exceção"*. **O aceite cobre só a ordem dos artefatos.** A validação com a equipe
e a aprovação da migração (FR-7911, SC-2704) continuam pendentes.

**Input**: a decisão do usuário em 15/11, depois do piloto da `172`: *"seguir com a migração. Mostre o
antes e depois da migração."* A base é o que o usuário aprovou no piloto: o texto na largura do
conteúdo e os três padrões da segunda leitura (a decisão do usuário sobre a largura do texto, na `172`).

> **Faixa de identificadores.** Esta spec abre em **FR-7900**, **SC-2700** e **UX-900**, e reserva até
> o requisito sete mil novecentos e noventa e nove. Os tetos medidos em 15/11/2026, somando as
> worktrees e os PRs abertos, eram o requisito sete mil oitocentos e noventa e três, o critério dois mil
> seiscentos e cinquenta e nove e o requisito de experiência oitocentos e setenta e sete, da `174`
> (PR #566), que reserva até o requisito sete mil oitocentos e noventa e nove. As decisões reiniciam
> em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-7702 da `172`"). Uma decisão de outra feature é citada pelo assunto e pela feature.

---

## Por que esta feature existe

O piloto da `172` pôs a direção experimental do estudo de 14/11 em cinco telas, sob a classe
`.piloto-ds`, e o usuário a julgou em duas leituras. Recusou a primeira, com a prosa em 80 caracteres e
a coluna centrada ("o piloto está pior"), e aprovou a segunda: **o texto ocupa a largura do
conteúdo**, os indicadores dividem a linha em partes iguais, o campo de texto ocupa a largura do
formulário e o rótulo e o valor ficam na mesma linha. Depois, decidiu seguir com a migração para todas
as telas da gestão, e pediu para ver o antes e o depois.

O roadmap do estudo previa a migração família por família, cada uma com a sua spec (a P2). A branch
fez outra coisa, mais curta: levou os padrões às folhas **comuns** da gestão, de uma vez, e mediu as
123 telas que o instrumento do estudo alcança. Esta spec registra essa escolha (D-001), e o que fica
para decidir depois de o usuário ver o resultado.

### O que esta spec cobre, e o que fica fora

| Cobre | Fica fora |
|---|---|
| As folhas comuns da gestão (`gestao/componentes.css`, `gestao/formularios.css`, `gestao/telas.css`) e as medidas de leitura das folhas de grupo e de tela | o portal do candidato, que não carrega as folhas da gestão |
| O antes e o depois das 123 telas que o instrumento alcança | o portal autenticado, fora do rastreio |
| A retirada de `grupos/confirmacao-de-ato.css`, que ficou sem regra | a redução tipográfica, que continua adiada |
| A folha do piloto reduzida ao que é só dele | desfazer a folha do piloto (pendência P-4) |
| Os guardiões que prendiam as medidas antigas, reescritos para prender as novas | guardiões novos |

---

## Clarifications

### Session 2026-11-15 (decisões do usuário)

- Q: Seguir com a migração? → A: **sim**, e mostrar o antes e o depois antes de qualquer outra coisa.
- Q: Corrigir os sete achados da revisão de código do #564 e do #565? → A: **sim, os sete**. Entre
  eles: os dois-pontos gerados pela folha depois do rótulo saem (D-002); a migração ganha esta spec; e
  a folha do piloto deixa de repetir a comum.
- A tela de um notebook citada pelo usuário no piloto foi só exemplo, e não critério de medida.
- Q: Você aceita a exceção da spec 175 escrita depois da migração? → A: **"Aceito a exceção"**
  (15/11/2026). Cobre só a ordem dos artefatos; a validação com a equipe e a aprovação da migração
  (FR-7911, SC-2704) continuam pendentes.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Quem opera a gestão lê o texto na largura da tela, em qualquer tela (Priority: P1)

Em qualquer tela da gestão, o parágrafo, a ajuda, a nota, o aviso, as consequências de um ato e o
campo de texto ocupam a largura do conteúdo, e não param em 68 caracteres com a direita vazia.

**Why this priority**: é o que o usuário aprovou no piloto e pediu para toda a gestão.

**Independent Test**: abrir a mesma tela na `main` e na branch, sobre o mesmo banco, e comparar a
largura do texto e a altura da página.

**Acceptance Scenarios**:

1. **Given** a confirmação de Encerrar de um Edital com impedimentos, **When** ela abre a 1440 px,
   **Then** o aviso, a lista do que impede e as consequências vão até a largura do conteúdo, e a página
   não fica mais alta que na `main`.
2. **Given** um formulário com área de texto, **When** ele abre, **Then** a área ocupa a largura do
   formulário, e o campo de número continua do tamanho do número.

### User Story 2 — Os mesmos componentes em toda a gestão (Priority: P1)

Os indicadores de quantidade dividem a linha em partes iguais; a lista de definição põe o rótulo e o
valor na mesma linha, o rótulo em peso maior; o aviso, o cartão das consequências e os botões têm o
desenho do piloto em todas as telas.

**Why this priority**: a consistência entre telas é o que o estudo de 14/11 mostrou faltar.

**Independent Test**: abrir três telas de famílias diferentes e conferir que o indicador, a lista de
definição e o botão têm o mesmo desenho.

**Acceptance Scenarios**:

1. **Given** a Ocupação e a conferência do acréscimo, **When** elas abrem, **Then** os indicadores
   dividem a linha em partes iguais nas duas.
2. **Given** uma lista de definição cujo rótulo é pergunta (o Sorteio, "Volta atrás?"), **When** ela
   abre, **Then** o rótulo aparece como está no template, sem pontuação acrescentada.

### User Story 3 — Nada some e o portal não muda (Priority: P2)

Nenhum texto, link, formulário ou ação muda em tela nenhuma, e as telas do portal saem idênticas.

**Why this priority**: é a condição para a migração ser só de composição.

**Independent Test**: o rastreio das 123 telas compara pixels e medidas, e as telas públicas e de
acesso saem idênticas.

**Acceptance Scenarios**:

1. **Given** as oito telas do portal público, **When** são rastreadas na `main` e na branch, **Then**
   saem idênticas pixel a pixel.

### User Story 4 — A equipe valida antes da aprovação (Priority: P3)

As pessoas da equipe de seleção fazem as tarefas do roteiro do piloto nas duas versões, e o usuário
decide com o que elas disserem.

**Why this priority**: é o passo que falta, e não é desta entrega; é registrado para não ser perdido.

**Independent Test**: o roteiro de `specs/172-piloto-do-design-system/validacao.md`, nas duas versões.

**Acceptance Scenarios**:

1. **Given** o roteiro e as duas versões no ar, **When** a equipe faz as tarefas, **Then** o registro
   sai preenchido por pessoa, tarefa e versão.

### Edge Cases

- **A lista que agrupa cada par num `div`** (o "Quem atuou" do Centro do Edital) não é grade de duas
  colunas: posta em grade, ela fazia a página rolar de lado a 768 px. Ela fica em bloco, e o par em
  linha dentro do grupo (FR-7903).
- **A lista com desenho próprio** (as fichas com o rótulo em caixa alta acima do valor) continua com o
  dela: a regra comum tem a especificidade de um elemento (`:where(main)`).
- **A lista da Revisão escreve os dois-pontos no texto do rótulo** ("Início:"), e eles continuam:
  são texto do template, e não pontuação gerada.
- **O portal também carrega `tokens.css`**, e nenhum token mudou de valor: o portal não muda.
- **Os indicadores no celular** ficam um por linha com o mínimo de 9rem (pendência P-1).

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-7900**: Nenhuma folha da gestão PODE limitar a prosa por `--leitura`. Saem as declarações
  `max-width:var(--leitura)` das folhas comuns, de grupo e de tela, e os 44rem de `.ajuda` e de
  `.explicacao`.
- **FR-7901**: Os indicadores de um grupo (`.resumo`) DEVEM dividir a linha em partes iguais, em grade,
  e quebrar em menos colunas no estreito. O tamanho da letra não muda.
- **FR-7902**: O campo de texto, a área de texto e a seleção DEVEM ocupar a largura do formulário. O
  campo de número e o de data continuam do tamanho do que recebem.
- **FR-7903**: A lista de definição DEVE pôr o rótulo e o valor na mesma linha, o rótulo em peso maior,
  **sem texto gerado pela folha** (D-002). A lista que agrupa cada par num `div` fica em bloco, com o
  par em linha. Toda lista com desenho próprio continua com o dela. No celular, o valor desce.
- **FR-7904**: O aviso, o cartão das consequências, o botão (`.botao`, 40 px) e a ação (`.acao`, 32
  px, e 40 px na barra de gravação) DEVEM ter o desenho que o usuário aprovou no piloto, com o respiro
  menor da barra de gravação e do subtítulo.
- **FR-7905**: O portal do candidato NÃO PODE mudar.
- **FR-7906**: Nenhum texto, link, formulário, nome de campo ou ação PODE mudar em tela nenhuma. A
  migração é de folha de estilo.
- **FR-7907**: `grupos/confirmacao-de-ato.css`, que ficou sem regra, DEVE sair, com o `<link>` das três
  confirmações e a entrada no mapa de quem carrega cada folha.
- **FR-7908**: A folha do piloto (`grupos/piloto-ds.css`) DEVE conter só o que a folha comum não tem: o
  respiro que o contêiner desfaz, a busca da Lista na largura do cartão, o recorte da Ocupação em cartão
  e a consulta da Lista num cartão só.
- **FR-7909**: Nenhum guardião PODE ser afrouxado. Os que prendiam as medidas antigas DEVEM ser
  reescritos para prender as novas, e os do portal continuam prendendo a medida dele.
- **FR-7910**: **Esta migração contraria a FR-7702 da `172`**, que proibia mudar valor ou seletor das
  folhas comuns da gestão. Aquela regra delimitava o piloto, para que nada fora dele mudasse; a
  migração existe para mudar tudo fora dele. A contradição é deliberada, e a FR-7702 continua valendo
  como regra do piloto, e não da gestão depois dele (D-003).
- **FR-7911**: A aprovação da migração DEVE esperar a validação com a equipe e a decisão do usuário. O
  que esta branch mede não substitui uma nem outra.

### Requisitos de experiência

- **UX-900**: O rótulo de uma lista de definição se distingue do valor pelo peso e pela coluna, e nunca
  por pontuação que o template não tem.
- **UX-901**: Nenhuma tela da gestão fica mais alta que na `main` por causa da migração, salvo pelo
  padrão de altura do botão, que é deliberado.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2700**: Das 123 telas rastreadas, mudam só as da gestão; as oito do portal público, as quatro de
  acesso e o guia incorporado saem idênticas (medido em 15/11: mudaram 110, todas da gestão).
- **SC-2701**: A altura somada das telas a 1440 px não cresce (medido em 15/11: −3,4%, de 221.200 a
  213.786 px; uma tela mais alta, a configuração da agenda da etapa, +12 px, pela altura do botão).
- **SC-2702**: Nenhuma tela rola de lado a 375 nem a 768 px, nenhum elemento novo passa da borda, e
  nenhum nó cai abaixo do contraste (medido em 15/11, na segunda passada).
- **SC-2703**: `make lint check test-pg` verde, com os guardiões reescritos e nenhum afrouxado.
- **SC-2704**: **Pendente**: a validação com a equipe, pelo roteiro do piloto, nas duas versões.

---

## Assumptions

- O rastreio das 123 telas sobre a cópia migrada da referência da P0 representa as telas da gestão; os
  estados que só a fotografia do piloto monta (os 64 da `172`) não foram fotografados nesta branch.
- A preferência do usuário pelo aproveitamento da tela, firmada no piloto, vale para a gestão inteira.
- As medidas de 15/11 (SC-2700 a SC-2702) são da branch antes das correções da revisão. As correções
  tiram os dois-pontos gerados, as cópias da folha do piloto e uma folha sem regra, e não mudam a
  composição de nenhuma tela além do sinal de pontuação.

## Out of Scope

- O portal do candidato, autenticado ou não.
- A redução tipográfica e os guardiões novos.
- A comparação de conteúdo estado a estado, que o piloto fez com a fotografia.

## Dependências

- A `172` (PR #564), sobre a qual esta branch está empilhada.
- O instrumento do estudo de 14/11 e a cópia da referência da P0 (`REFERENCIA_DUMP`).

## Pendências, para o usuário decidir

- **P-1, os indicadores no celular.** Com o mínimo de 9rem, ficam um por linha a 375 px, e dez telas
  cresceram mais de 40 px no celular (até +182 px na Ocupação). Um mínimo menor no estreito daria duas
  colunas.
- **P-2, as fichas com o rótulo em caixa alta acima do valor** (o Centro do Edital, a peça do recurso):
  ficam como estão, ou passam a "rótulo e valor" na linha, uma regra por ficha.
- **P-3, as larguras de coluna em rem** que ainda limitam texto (`.conducao`, `.definicao-da-formalizacao`,
  `.lista-da-mesa`, a entrada): são colunas, e não prosa, e a branch não as tocou.
- **P-4, desfazer a folha do piloto**: o que é de tela vai para `telas/` (a Ocupação e a Lista), e a
  classe `.piloto-ds` sai.
- **P-5, a fotografia e a comparação de conteúdo** do piloto, para as telas que têm estado.

---

## Decisões

### D-001 — A migração é por padrão, nas folhas comuns, e não família por família

O roadmap do estudo previa uma spec por família de tela (a P2). Os padrões aprovados no piloto são de
componente, e não de tela: valem iguais em todas, e moram nas folhas comuns. Levá-los de uma vez, e
medir as 123 telas, deu ao usuário o antes e o depois que ele pediu sem cinco specs na frente. O
preço é a revisão de 110 telas de uma vez, que o rastreio e a suíte cobrem, e a validação com a equipe
ainda não.

### D-002 — Sem dois-pontos gerados depois do rótulo

A primeira versão da migração punha ":" depois de todo rótulo de lista de definição por `dt::after`. Era
texto que o template não tem, fora do alcance da comparação de conteúdo, e na gestão inteira escrevia
"Volta atrás?:" nos rótulos do Sorteio que são pergunta e "E o Anexo em papel?:" na Inscrição. Saiu na
revisão de código, aprovada pelo usuário. O rótulo se distingue pelo peso e pela grade. Pôr os
dois-pontos no texto dos templates seria mudança de conteúdo, e fica para quando o usuário a pedir.

### D-003 — A FR-7702 da `172` vale para o piloto, e não para a gestão depois dele

A regra de que nenhuma folha comum muda delimitava o experimento. Com o experimento julgado e a
migração decidida pelo usuário, ela deixa de valer fora do piloto. A contradição fica escrita (FR-7910),
para que ninguém leia a `172` como proibição vigente.
