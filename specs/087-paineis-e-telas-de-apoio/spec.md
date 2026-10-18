# Feature Specification: Os painéis e as telas de apoio da gestão, nono incremento

**Feature Branch**: `claude/funny-cohen-c98a85`, sobre a `main` em `cf6d7372`, que traz da `075` à `080`

**Created**: 2026-10-18

**Status**: Implementada — PR aberto, merge com o usuário

**Input**: etapa 4 da sequência do [estudo da entrada na gestão](../../doc/estudo-acesso-a-gestao-2026-10-16.md)
(§7) — a modernização por tela, incremental. Último grupo da etapa, depois de quem avalia
([`077`](../077-telas-de-uso-diario/spec.md)), de quem elabora ([`078`](../078-telas-de-quem-elabora/spec.md)),
da presidência ([`079`](../079-telas-da-presidencia/spec.md)), das filhas da Distribuição
([`080`](../080-telas-filhas-da-distribuicao/spec.md)) e dos grupos do Edital, do resultado, das
inscrições e dos avisos, que correm em paralelo (`083` a `086`). São os dois painéis — a Visão Geral e
a Supervisão do Processo — e as telas de apoio: as Autoridades da unidade, as Respostas do assistente
de dúvidas, o Assistente do Edital (piloto), Criar Processo Seletivo e as duas conferências de ato, a
do Processo e a do Edital. A linha de base visual é o
[inventário de 16/10](../../doc/inventario-visual-da-gestao-2026-10-16.md), refeito em 18/10/2026
sobre `cf6d7372`, nos dois estados da barra.

> **Faixa de identificadores.** Esta spec usa FR-1970 a FR-1979 e SC-770 a SC-776, da faixa reservada
> a ela (FR-1970–1999, SC-770–779) na divisão da etapa 4 em paralelo. Nenhum dos dois aparecia na
> `main` nem nas worktrees das `081` a `086` em 18/10/2026.

---

## Por que esta feature existe

**Os dois painéis não dizem onde a pessoa está; dizem só a seção.** A Visão Geral e as Autoridades da
unidade são seções da barra, como a lista e Minhas Etapas. Desde a `077`, a lista e Minhas Etapas se
anunciam no cabeçalho como trilha — *GPS › Processos Seletivos*, a seção como página atual. A Visão
Geral e as Autoridades ainda mostram a mesma frase como texto solto, que não é navegação nem marca a
página: o leitor de tela não ouve "trilha", e quem navega por marcos não a encontra.

**Nas outras seis, o caminho aparece duas vezes, e de dois jeitos.** O cabeçalho diz *GPS › Processos
Seletivos*, e o conteúdo começa por uma segunda trilha. **Medido em 18/10/2026**: das seis, as três que
se abrem a partir do Edital — as Respostas do assistente de dúvidas, o Assistente do Edital e a
conferência dos atos do Edital — saltam de "Processos Seletivos" direto para o Edital, sem o Processo
no meio; desde a `078`, o próprio Edital diz *Processos Seletivos › código do Processo › Edital*.

**No Assistente do Edital, a ação da tela tem o desenho de ação de linha.** "Perguntar" é a razão de a
tela existir, e tem o desenho de "Começar outra conversa", a ação de recomeçar, logo abaixo dele. A
`055` deu a "Filtrar" o desenho de ação principal nas telas que mediu (`FR-1008`), e a `080` estendeu a
decisão às consultas que faltavam; o mesmo vale para a pergunta.

**O que não muda, e não se negocia aqui:** nenhuma regra de negócio, permissão, semântica de papel ou
fluxo. Nenhum endereço, nenhuma view, nenhuma consulta ao banco. Nenhum conteúdo normativo. **Nenhum
número novo nos painéis**: a Visão Geral e a Supervisão continuam mostrando o que o banco tem, com os
mesmos denominadores e as mesmas ausências escritas — nenhum indicador, contagem, percentual ou
tendência entra ou sai. Nenhuma ação que não se desfaz — encerrar ou cancelar o Processo, os atos do
Edital, encerrar a vigência de uma autoridade — muda de lugar, de rótulo ou de peso. Nenhuma tela fora
destas oito.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Onde estou, dito uma vez só, nos painéis e nas telas de apoio (Priority: P1)

A gestora abre o Edital 01/2026 e, dele, as Respostas do assistente de dúvidas. No topo, o cabeçalho
diz *GPS › Processos Seletivos › PS-DEMO-2026 › Edital 01/2026 › Respostas do assistente de dúvidas* — a
trilha do Edital, com a tela no fim —, e cada nível acima leva a ele. O conteúdo começa pelo título. O
mesmo no Assistente do Edital e na conferência de um ato do Edital, que termina no nome do ato; na
Supervisão e na conferência de um ato do Processo, *GPS › Processos Seletivos › PS-DEMO-2026 ›
Supervisão*; em Criar Processo Seletivo, *GPS › Processos Seletivos › Criar*. Na Visão Geral e nas
Autoridades da unidade, a trilha tem um nível — a seção, como página atual —, como a lista.

**Why this priority**: é o que a `077` a `080` fizeram nas outras telas; sem isso, o fim da etapa 4
deixa os painéis e as telas de apoio dizendo o caminho de um jeito diferente do resto da gestão.

**Independent Test**: nas oito telas, o caminho está no cabeçalho de contexto, como navegação nomeada,
com um link por nível acima da tela e a tela como página atual; o conteúdo não tem trilha; a página
tem uma trilha só.

**Acceptance Scenarios**:

1. **Given** a Visão Geral ou as Autoridades da unidade, **When** a página abre, **Then** o cabeçalho
   mostra *GPS ›* e a seção como página atual, sem link — como a lista e Minhas Etapas.
2. **Given** a Supervisão de um Processo, ou a conferência de encerrar, cancelar ou ativar um
   Processo, **When** a página abre, **Then** o cabeçalho mostra *GPS › Processos Seletivos › código do
   Processo ›* e a tela, com os dois níveis do meio como links.
3. **Given** as Respostas do assistente de dúvidas, o Assistente do Edital ou a conferência de um ato
   do Edital, **When** a página abre, **Then** o cabeçalho mostra *GPS › Processos Seletivos › código do
   Processo › Edital número/ano ›* e a tela, com os três níveis do meio como links.
4. **Given** Criar Processo Seletivo, **When** a página abre, **Then** o cabeçalho mostra *GPS ›
   Processos Seletivos › Criar*.
5. **Given** qualquer das oito, **When** a página abre, **Then** o conteúdo começa pelo título, e a
   barra marca a mesma seção de antes.

---

### User Story 2 — No Assistente do Edital, "Perguntar" é a ação principal (Priority: P2)

O participante do piloto abre o Assistente do Edital, escreve a pergunta e aperta "Perguntar" — o
botão com o desenho de ação principal. "Começar outra conversa" continua logo abaixo, com o desenho de
antes.

**Why this priority**: é a hierarquia que a `055` e a `080` deram às ações principais das consultas; a
pergunta é a única ação da tela que não recomeça nada.

**Independent Test**: no Assistente do Edital, "Perguntar" tem o desenho de ação principal, e "Começar
outra conversa" não.

**Acceptance Scenarios**:

1. **Given** o Assistente de um Edital publicado, **When** a página abre, **Then** "Perguntar" tem o
   desenho de ação principal, e "Começar outra conversa" o de ação secundária, num formulário próprio.
2. **Given** as Respostas do assistente de dúvidas, **When** a página abre, **Then** "Ver a resposta"
   continua a ação principal, e "Consultar neste instante" continua secundária.

---

### User Story 3 — Os painéis continuam dizendo só o que o banco tem (Priority: P1)

O gestor abre a Visão Geral e a Supervisão do PS-DEMO-2026 e lê os mesmos números de antes, com os
mesmos denominadores e as mesmas frases de ausência — só a trilha subiu.

**Why this priority**: o painel é onde a pressa de "modernizar" costuma inventar indicador. Esta
feature não acrescenta nenhum, e diz isso como requisito, para que a revisão o cobre.

**Independent Test**: nos dois painéis, as regiões de números têm os mesmos itens, na mesma ordem, e o
inventário só mostra a diferença de altura da trilha que saiu do conteúdo.

**Acceptance Scenarios**:

1. **Given** a Visão Geral, **When** a página abre, **Then** os quatro indicadores, a tabela dos Editais
   e "O que esta página não mede" são os de antes.
2. **Given** a Supervisão, **When** a página abre, **Then** o Pulso e a Atenção são os de antes, com o
   instante da leitura.

### Edge Cases

- **Trilha longa no celular.** A das telas do Edital tem cinco níveis, e o rótulo da tela pode ser
  longo ("Respostas do assistente de dúvidas", "Confirmar: Revogar homologação"). A 375 px a trilha
  quebra a linha dentro do cabeçalho; nem ela nem "Trocar identidade" estouram a largura.
- **Autoridades sem unidade registrada.** O aviso de que a unidade não está registrada continua; a
  trilha é a mesma.
- **Assistente ou dúvidas de Edital não publicado.** O aviso continua; a trilha é a mesma, com o
  Edital como link.
- **Conferência com recusa certa.** O impedimento e a ausência de "Confirmar" continuam; "Cancelar e
  voltar" continua levando ao Processo ou ao Edital; só a trilha sobe.
- **Conferência depois de um envio recusado.** O erro continua logo depois do título, com o foco nele.
- **Criar Processo Seletivo com recusa.** As recusas continuam no topo do formulário e junto de cada
  campo; o foco continua no primeiro campo.
- **Visão Geral sem Edital no período.** O estado vazio da tabela continua, com a frase que diz que
  não é afirmação sobre o acervo.
- **Supervisão sem período em curso.** O aviso continua no lugar da contagem recente.
- **O link de salto.** Continua levando ao conteúdo, que agora começa pelo título.
- **Impressão.** A barra e o cabeçalho de contexto não saem no papel (`076`). O título e a linha de
  baixo dele continuam identificando o Processo ou o Edital impressos.

## Requirements *(mandatory)*

### Functional Requirements

#### A trilha no cabeçalho de contexto

- **FR-1970**: Na Visão Geral, nas Autoridades da unidade, na Supervisão, nas Respostas do assistente
  de dúvidas, no Assistente do Edital, em Criar Processo Seletivo e nas conferências dos atos do
  Processo e do Edital, o cabeçalho de contexto MUST mostrar a trilha da tela, como navegação nomeada:
  o produto, cada nível acima da tela como link, e a própria tela como a página atual — como nas telas
  da `077` à `080` (`FR-1800` da `080`).
- **FR-1971**: Na Visão Geral e nas Autoridades da unidade, a trilha MUST ter só a seção, como página
  atual, com o rótulo que a barra lhe dá — como a lista e Minhas Etapas (`FR-1746` da `077`).
- **FR-1972**: Na Supervisão e na conferência dos atos do Processo, o nível acima da tela MUST ser o
  Processo; nas Respostas do assistente de dúvidas, no Assistente do Edital e na conferência dos atos
  do Edital, MUST ser o Processo e o Edital, nessa ordem; em Criar Processo Seletivo, nenhum além da
  seção. O rótulo da tela MUST ser o que ela já mostrava como página atual.
- **FR-1973**: Nessas oito telas a trilha MUST NOT aparecer de novo no conteúdo: a página MUST ter uma
  trilha só, e o conteúdo MUST começar pelo título.
- **FR-1974**: As telas da gestão fora das da `077` à `080`, das das features que correm em paralelo e
  destas MUST continuar com o cabeçalho de contexto da `076`; a barra MUST marcar, nas oito, a mesma
  seção de antes.
- **FR-1975**: A 375 px, a trilha do cabeçalho MUST quebrar a linha dentro da largura, e "Trocar
  identidade" MUST continuar alcançável.

#### A hierarquia das ações

- **FR-1976**: No Assistente do Edital, "Perguntar" MUST ter o desenho de ação principal; "Começar
  outra conversa" MUST continuar com o desenho de antes. Nas Respostas do assistente de dúvidas, "Ver a
  resposta" MUST continuar a ação principal, e "Consultar neste instante" a secundária.
- **FR-1977**: As ações que não se desfazem — "Confirmar" nas conferências dos atos do Processo e do
  Edital, com o desenho de perigo quando o ato interrompe, e "Encerrar a vigência" nas Autoridades —
  MUST continuar com o rótulo, o desenho, o lugar e as frases que as precedem; nenhuma MUST ganhar ou
  perder peso.

#### O que não pode piorar

- **FR-1978**: Na Visão Geral e na Supervisão, nenhum número, indicador, contagem, percentual ou
  tendência MUST entrar ou sair; os que existem MUST continuar com os mesmos rótulos, denominadores,
  frases de ausência e ordem. Nenhuma das oito telas MUST passar a fazer consulta ao banco que antes
  não fazia.
- **FR-1979**: Nenhuma variante do inventário visual MUST deixar de carregar, mudar de `status` ou
  passar a estourar a 375 ou a 1280 px, com a barra expandida e com ela recolhida; só as telas desta
  feature MUST mudar de largura ou de altura; e as telas tocadas MUST passar pelos guardiões de
  acessibilidade, larguras, vocabulário e folha que já varrem a gestão.

### Key Entities

Nenhuma. Só apresentação.

## Decisões

### D-001 — A trilha das telas do Edital é a do Edital, mais a tela

Nas Respostas do assistente de dúvidas, no Assistente do Edital e na conferência dos atos do Edital, a
trilha do conteúdo pulava o Processo. O Edital diz *Processos Seletivos › código do Processo › Edital*
desde a `078` (`FR-1767` da `078`). A trilha destas telas é a da tela de onde elas se abrem, com elas
no fim — a regra da `080` para as filhas da Distribuição (D-001 da `080`). O código do Processo vem
do Edital que a view já carrega com o Processo; nenhuma consulta a mais.

### D-002 — A Visão Geral e as Autoridades são raiz de seção

As duas são itens da barra, e não telas abaixo de outra. A trilha delas é a da lista e de Minhas
Etapas: um nível, a seção como página atual, sem link. O rótulo é o da barra — "Visão Geral",
"Autoridades da unidade" —, o mesmo que o cabeçalho da `076` já mostrava como texto, e sai de onde a
barra e o cabeçalho da `076` o tiravam, e não de uma cópia: renomear a seção renomeia a trilha.

### D-003 — "Perguntar" é a ação principal; "Consultar neste instante" não

A `055` (`FR-1008`) e a `080` (D-004) deram o desenho de ação principal à ação que é a razão da
tela. No Assistente do Edital, essa ação é perguntar; "Começar outra conversa" recomeça, e fica como
está. Nas Respostas do assistente de dúvidas, a ação principal já é "Ver a resposta"; "Consultar
neste instante" troca o instante de referência da página inteira, é um ajuste de leitura, e
continua secundária — dois botões principais na mesma tela desfariam a hierarquia que a regra
existe para dar.

### D-004 — O que não muda, por governança

- **Nenhum número novo nos painéis.** A Visão Geral e a Supervisão já declaram o que não medem
  (`FR-596` da `040`; `FR-017` e `FR-018` da Supervisão). Modernizar a tela não é ocasião de
  acrescentar indicador: um número que o banco não tem seria métrica fictícia, e um que o banco tem
  e a tela não mostra é decisão de produto, e não de apresentação.
- **Nenhuma ação que não se desfaz ganha ou perde peso.** "Confirmar" continua `botao`, com o
  desenho de perigo quando o ato interrompe; "Encerrar a vigência" continua com o de perigo.
- **A recusa da pergunta sugerida continua junto da resposta.** Nas Respostas do assistente de
  dúvidas, a recusa ocupa o lugar da resposta que não veio, depois do formulário que a pediu: é o
  resultado da consulta, e não de um ato. Subi-la para o título a separaria do formulário que
  precisa ser corrigido.
- **A folha comum não muda.** A trilha do cabeçalho usa a regra que a `077` criou, e "Perguntar" a
  classe que toda ação principal já usa.

### D-005 — O fechamento da etapa 4 é uma contagem, e não uma afirmação

O pedido fecha a etapa 4 contando as telas que estendem o modelo comum da gestão e ainda não têm a
trilha no cabeçalho. A contagem é sobre os modelos de página, por texto, e não sobre o que se vê:
a Auditoria do Edital divide o modelo com a Trilha da avaliação, que tem a trilha no cabeçalho, e
continua com a trilha no conteúdo (D-002 da `080`); ela entra na conta como sem trilha, embora o
modelo tenha o bloco. A conta é refeita na `main` de quando o PR for aberto, e o PR lista as telas
que sobrarem, com a feature que as cobre, se alguma das que correm em paralelo cobrir.

## Success Criteria *(mandatory)*

- **SC-770**: Refeito o inventário visual, **zero** variantes estouram a 375 ou a 1280 px, e
  **nenhuma** muda de `status`, nos dois estados da barra.
- **SC-771**: Fora das oito telas desta feature, **nenhuma** variante muda de largura ou de altura.
- **SC-772**: Nas oito telas, "onde estou" aparece **uma** vez por página, no cabeçalho de contexto, e
  cada nível acima da tela está a **um** clique.
- **SC-773**: Das três telas que se abrem a partir do Edital, as que levam ao Processo pela trilha
  passam de **zero** para **três**.
- **SC-774**: A suíte contra PostgreSQL continua sem falhas.
- **SC-775**: O percurso — da lista à Visão Geral e às Autoridades pela barra, do Processo à
  Supervisão e à conferência de um ato, do Edital às duas telas do assistente e à conferência de um
  ato, e de volta pela trilha — é feito só pelo teclado, com foco visível, a 1280 e a 375 px.
- **SC-776**: Das telas que estendem o modelo comum da gestão, as que não têm a trilha no cabeçalho
  caem de **43** para **35** nesta branch — as 42 sem o bloco e a Auditoria do Edital, menos as oito
  —, e o PR lista as que sobram.

## Assumptions

- "Painéis" são a Visão Geral e a Supervisão do Processo, as duas telas da gestão que só mostram
  números e sinais; "telas de apoio" são as outras seis do pedido.
- As conferências dos atos são `processo_confirmar` (ativar, encerrar e cancelar o Processo) e
  `confirmar` (os atos do Edital: submeter, homologar, devolver, revogar a homologação, publicar,
  encerrar e cancelar). A conferência dos atos da Retificação é outra tela, e fica fora.
- A tela do protótipo do assistente não estende o modelo comum da gestão, e fica fora.
- O produto no começo da trilha é a sigla GPS, como da `076` à `080`.
- A tela mais estreita que se considera é a de 375 px, a mesma do inventário.
- A validação com a equipe, recomendada desde a `075`, continua pendente; este incremento não a
  substitui.
