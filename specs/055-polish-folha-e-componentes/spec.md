# Feature Specification: Polish da folha e dos componentes

**Feature Branch**: `claude/polish-folha-componentes-82ee7f`

**Created**: 2026-09-30

**Status**: Draft

**Input**: o prompt de sessão autônoma `doc/prompt/055-polish-folha-e-componentes.md`, escrito em
30/09/2026 a partir da auditoria de polish de UI (`doc/auditoria-polish-ui-2026-09-30.md`, PR 240,
ainda aberto quando esta spec foi escrita). É o **lote 1 de 3** da proposta de execução da auditoria
(§9): os itens G1 a G8, D1 e F7. Os lotes 2 (assistente de composição) e 3 (telas de operação) terão
spec própria.

> **Faixa de identificadores.** Abre em **FR-1000**, **SC-371** e **UX-134**. O teto medido em
> 30/09/2026 em todas as worktrees, com quatro dígitos, era FR-999, SC-370 e UX-133 — todos
> definidos por specs já mergeadas na `main`. A faixa FR de três dígitos acabou na `054`. As decisões
> desta spec nascem em `D-001` e moram no [research.md](research.md); as dez decisões que o prompt
> trouxe fechadas são **entrada**, e o research as registra como "decisões recebidas" sem
> reaproveitar a numeração delas.

**A frase que governa:**

> Mesma informação, mesmo desenho, mesma altura — e nenhuma mudança que não se possa medir.

**E a que mantém o corte:**

> Esta feature acerta a folha e os componentes. Não reorganiza tela, não muda texto, não mexe em
> fluxo, e não toca o assistente de composição nem as telas de operação além do que a folha
> alcança sozinha.

---

## Por que esta feature existe

A auditoria de 30/09 mediu a interface renderizada a 1280 × 900 e achou defeitos de acabamento que
**nascem na folha de estilo**, e não em cada tela. Corrigidos na raiz, eles melhoram muitas telas de
uma vez; corrigidos tela a tela, voltariam na próxima.

- **Números soltos entre rótulos.** Na faixa calculada do Corte — tela de ato irreversível —, cada
  número fica equidistante do rótulo da esquerda e do da direita: "Alvo declarado 2 Alvo apurado 2
  Suplentes 1 …". Na Ocupação, título, números e links viram itens de uma mesma linha, e os quatro
  números se espremem numa coluna de 70 px. A Convocação mostra os mesmos quatro números da
  Ocupação do jeito certo.
- **Tabelas que não cabem.** O preenchimento de célula da gestão é quase o dobro do portal: nas
  Inscrições, sete colunas gastam 280 px só de preenchimento, protocolo e nome quebram em duas
  linhas, e cada linha fica com 70 px.
- **Três alturas de botão na mesma barra.** Na navegação do assistente, "‹ Voltar" tem 25 px,
  "Salvar rascunho" 38 px e "Avançar" 36 px — lado a lado, em toda etapa.
- **A ação principal como o elemento mais fraco.** "Filtrar" e "Ver o que sairá vazio" são a única
  ação da tela e têm o desenho de ação de linha de tabela; no portal, "Guardar e continuar depois"
  sai com o desenho nativo do navegador, ao lado do botão principal, e parece defeito.
- **Hierarquia de títulos invertida.** Não há regra de h3 na gestão: ele herda 18,72 px e fica maior
  que o h2 da mesma página.
- **Controles tortos e barras de filtro desalinhadas.** Input e select da mesma linha com 2 a 3 px de
  diferença; na Distribuição, 22 px de desnível entre os dois controles do filtro.
- **Espaço reservado para o que não existe** na página da seleção do portal, e campos de vinte
  caracteres com mais de 1.200 px de largura.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Quem emite a Ocupação ou o Corte lê cada número junto do seu rótulo (Priority: P1)

A pessoa que confere a faixa calculada antes de emitir o Corte, ou os quatro números de uma
apuração de Ocupação, lê cada número preso ao rótulo que o nomeia, no mesmo desenho que a Convocação
já usa para os mesmos números.

**Why this priority**: o Corte é ato irreversível, e hoje a leitura dos números é ambígua. É o item
de maior impacto por esforço da auditoria.

**Independent Test**: abrir o Corte de um marco com proposta e a Ocupação de um marco apurado no
banco de demonstração, e conferir que cada número está no mesmo bloco que o seu rótulo, sem número
algum entre dois rótulos.

**Acceptance Scenarios**:

1. **Given** um marco com faixa calculada, **When** a pessoa abre o Corte, **Then** cada um dos seis
   valores da faixa aparece num bloco próprio com o seu rótulo, no desenho dos blocos da Convocação.
2. **Given** um recorte apurado, **When** a pessoa abre a Ocupação, **Then** Publicadas, Efetivas,
   Ocupadas e A ocupar aparecem como quatro blocos, e o título e as notas do recorte ficam acima e
   abaixo deles, não ao lado.
3. **Given** um recorte ainda não apurado, **When** a pessoa abre a Ocupação, **Then** a quantidade
   publicada aparece sozinha no mesmo desenho de bloco, e as quantidades de apuração continuam
   ausentes.
4. **Given** o histórico do Corte ou da Ocupação, **When** a pessoa o abre, **Then** os números de
   cada geração seguem o mesmo desenho.

---

### User Story 2 — Quem confere uma lista vê mais linhas, e números comparáveis (Priority: P1)

Quem percorre as Inscrições, a ordem de um marco ou qualquer tabela da gestão vê cada linha numa
altura só, e compara números alinhados à direita.

**Why this priority**: toda tabela da gestão é alcançada, e as listas são a tela mais usada.

**Independent Test**: medir a altura de linha da tabela de Inscrições do Edital 51/2026 a 1280 px, e
a posição da pontuação na ordem calculada de um marco.

**Acceptance Scenarios**:

1. **Given** a lista de Inscrições do Edital 51/2026, **When** aberta a 1280 px, **Then** cada linha
   tem no máximo 45 px, contra 70 px antes.
2. **Given** uma tabela que declara preenchimento próprio menor que o padrão, **When** aberta,
   **Then** ela continua com o preenchimento que declarava.
3. **Given** a ordem calculada de um marco, **When** aberta, **Then** a coluna de pontuação fica
   alinhada à direita, com algarismos de largura fixa.

---

### User Story 3 — Os botões dizem a hierarquia, e na mesma barra têm a mesma altura (Priority: P1)

Quem avança no assistente, confirma um ato ou filtra uma lista vê os botões da mesma barra com a
mesma altura, e a ação principal da tela com o peso de ação principal. O candidato que guarda o
Requerimento para continuar depois vê um botão secundário, e não um controle sem estilo.

**Why this priority**: o desalinhamento aparece em toda etapa do assistente e em toda confirmação; o
botão sem estilo do portal parece defeito para quem está se inscrevendo.

**Independent Test**: medir a altura dos três botões da barra de navegação do assistente, do
"Filtrar" das Inscrições, da Distribuição e da Comissão, do "Ver o que sairá vazio" das Matrículas,
e conferir o desenho de "Guardar e continuar depois" no Requerimento do portal.

**Acceptance Scenarios**:

1. **Given** qualquer etapa do assistente de composição, **When** a pessoa olha a barra de
   navegação, **Then** Voltar, Salvar rascunho e Avançar têm a mesma altura, com diferença de 0 px.
2. **Given** um botão principal e um secundário lado a lado, **When** renderizados, **Then** têm a
   mesma altura externa, seja o botão um `button` ou um link com desenho de botão.
3. **Given** as Inscrições, a Distribuição, a Comissão e as Matrículas, **When** abertas, **Then** a
   ação única do formulário deixa de ter 25 px e passa a ter o desenho de botão.
4. **Given** o Requerimento do portal em preenchimento, **When** aberto, **Then** "Guardar e
   continuar depois" tem o desenho secundário do portal.
5. **Given** uma ação de linha dentro de uma tabela ou de um texto, **When** renderizada, **Then** ela
   continua pequena como antes.

---

### User Story 4 — A hierarquia visual dos títulos é a do documento (Priority: P2)

Quem lê a Convocação, o Processo, a Revisão ou a Retificação vê os títulos em escala: h1 maior que
h2, h2 maior que h3, e dois títulos do mesmo nível com o mesmo tamanho.

**Why this priority**: a inversão confunde a leitura, mas não bloqueia tarefa nenhuma.

**Independent Test**: medir o tamanho computado de todo h2 e h3 nas telas auditadas.

**Acceptance Scenarios**:

1. **Given** a Convocação e o Processo, **When** abertos, **Then** nenhum h3 renderiza maior que o h2
   da mesma página.
2. **Given** a Revisão, **When** aberta, **Then** os h2 irmãos têm o mesmo tamanho.
3. **Given** a Retificação, **When** aberta, **Then** os títulos das seções não estão em caixa-alta.

---

### User Story 5 — Formulários e barras de filtro alinhados (Priority: P2)

Quem preenche um formulário ou filtra uma lista vê input e select da mesma linha na mesma altura, os
rótulos no topo e o botão de filtrar da altura dos controles — sem perder o texto de ajuda do campo.

**Why this priority**: a barra de filtro é a primeira coisa que o operador usa em toda lista.

**Independent Test**: medir a altura de input e select na Visão Geral, no Requerimento do portal e na
Comissão; medir o desnível entre os controles do filtro da Distribuição.

**Acceptance Scenarios**:

1. **Given** input e select na mesma linha, **When** renderizados, **Then** têm a mesma altura.
2. **Given** o filtro da Distribuição, **When** aberto, **Then** os dois controles começam na mesma
   altura e "Filtrar" tem a altura deles.
3. **Given** um campo de filtro com texto de ajuda, **When** renderizado, **Then** a ajuda continua
   visível e associada ao campo, e não desloca os controles vizinhos.

---

### User Story 6 — Espaço proporcional ao conteúdo (Priority: P3)

O candidato que abre uma seleção sem sorteio vê o Cronograma ao lado das Vagas, sem vão. Quem
preenche a Comissão, o Requerimento do portal ou os Anexos vê campos com a largura do que se escreve
neles.

**Why this priority**: melhora percebida, sem bloqueio.

**Independent Test**: medir a posição do Cronograma na página da seleção sem sorteio, e a largura dos
campos nomeados.

**Acceptance Scenarios**:

1. **Given** uma seleção sem sorteio, **When** aberta a 1280 px, **Then** o Cronograma começa na
   altura do topo das Vagas, e não 335 px abaixo.
2. **Given** uma seleção com sorteio, **When** aberta, **Then** o sorteio continua acima do
   Cronograma, como antes.
3. **Given** a Comissão, o Requerimento do portal e os Anexos, **When** abertos, **Then** campo de
   até 20 caracteres esperados tem no máximo ~20 rem, e nome no máximo ~40 rem.

---

### Edge Cases

Os casos-limite desta feature são requisitos, e estão escritos como tal abaixo — a seção de casos
de borda não entra na matriz de rastreabilidade, e nenhuma ferramenta a cobra:

- recorte sem apuração, com um número só (**FR-1001**);
- valor da faixa que é texto e não número, e "Nenhuma" (**FR-1002**);
- link com desenho de botão ao lado de `button` (**FR-1006**);
- botão desabilitado e destrutivo na mesma barra (**FR-1006**);
- barra de filtro que quebra em duas linhas em tela estreita (**FR-1013**);
- seleção com sorteio (**FR-1015**);
- tela de 375 px (**FR-1018**).

---

## Requirements *(mandatory)*

### Functional Requirements

**Números com o seu rótulo (G1)**

- **FR-1000**: A Ocupação MUST mostrar os quatro números de cada recorte apurado — Publicadas,
  Efetivas, Ocupadas e A ocupar — como blocos no desenho que a Convocação usa para os mesmos números,
  cada número no mesmo bloco que o seu rótulo. O contêiner de cada recorte MUST deixar de dispor
  título, números, notas e links numa mesma linha.
- **FR-1001**: O recorte ainda não apurado MUST mostrar a quantidade publicada, sozinha, no mesmo
  desenho de bloco; as três quantidades de apuração continuam não desenhadas, nem como zero.
- **FR-1002**: O Corte e o histórico do Corte MUST mostrar os seis valores da faixa — Alvo declarado,
  Alvo apurado, Suplentes, Progridem, Ficam fora e Última posição alcançada — como blocos, cada valor
  no bloco do seu rótulo, inclusive quando o valor é texto ("O que o quadro de vagas publicar no
  recorte") ou ausência ("Nenhuma"), e com a nota de origem do alvo dentro do bloco dele.
- **FR-1003**: O histórico da Ocupação MUST seguir **FR-1000** e **FR-1001**.

**Tabelas (G2, G3)**

- **FR-1004**: A célula de tabela da gestão MUST ter por padrão o preenchimento que o portal já usa
  (meio rem na vertical, três quartos de rem na horizontal). Tabela que declara preenchimento próprio
  menor MUST continuar com ele.
- **FR-1005**: Coluna numérica MUST ser alinhada à direita, com algarismos de largura fixa, por uma
  única classe da folha da gestão; a pontuação da ordem calculada do marco MUST usá-la. As grafias de
  coluna numérica que já existem só são unificadas onde a unificação cabe no escopo deste lote; a
  Visão Geral, que tem estilo próprio da página, fica como está.

**Botões (G4, G5)**

- **FR-1006**: O botão principal e o secundário da gestão MUST ter a mesma altura externa: o
  principal ganha borda da cor do próprio fundo, e o secundário mantém a sua. A mesma altura MUST
  valer para o destrutivo e para o desabilitado, e para o link com desenho de botão ao lado de um
  `button`.
- **FR-1007**: Em barra de ações — a navegação do assistente, a barra de filtro e o rodapé de
  confirmação —, todo botão da linha MUST ter a mesma altura, inclusive a ação que tem desenho de
  ação de linha. Fora dessas barras, a ação de linha MUST continuar pequena: dentro de tabela e em
  contexto de texto.
- **FR-1008**: A ação principal de uma tela MUST NOT ter o desenho de ação de linha. Aplica-se às
  ações medidas pela auditoria: "Ver o que sairá vazio" (Matrículas) e "Filtrar" (Inscrições,
  Distribuição e Comissão). Nenhum outro botão é reclassificado por esta feature.
- **FR-1009**: "Guardar e continuar depois", no Requerimento do portal, MUST ter o desenho secundário
  do portal, e nenhum botão de envio do portal MUST ficar sem classe.

**Títulos (G6)**

- **FR-1010**: A gestão MUST ter regra global de h3, e a escala MUST ser h1 1,6 rem, h2 1,15 rem e h3
  1 rem, todos com peso 600.
- **FR-1011**: As regras por contêiner que **só** mudam o tamanho de um título para um valor
  equivalente a outro nível MUST ser removidas. A caixa-alta do h2 da Retificação MUST sair, salvo
  se um comentário da folha registrar o motivo dela — caso em que fica, e o motivo entra no research.

**Controles (G7) e barra de filtro (G8)**

- **FR-1012**: Cada folha — gestão e portal — MUST ter uma altura única para `input` de texto,
  busca, número, data, data e hora, telefone e e-mail, e para `select`. `textarea` e o campo de
  arquivo não entram. As duas folhas não precisam ter a mesma altura entre si.
- **FR-1013**: A barra de filtro da gestão MUST seguir o desenho da consulta da Vitrine: rótulos no
  topo, controles alinhados pelo topo, e o botão da altura dos controles, alinhado a eles. Quando a
  barra quebrar em mais de uma linha, o botão MUST continuar alinhado aos controles da linha em que
  cair.
- **FR-1014**: O texto de ajuda de um campo de filtro MUST continuar visível e ligado ao campo
  (`aria-describedby`, onde já estiver), e MUST NOT deslocar os controles vizinhos.

**Página da seleção (D1) e larguras (F7)**

- **FR-1015**: A página da seleção do portal MUST NOT reservar a área do sorteio quando não houver
  sorteio. Com sorteio, a disposição continua a de antes.
- **FR-1016**: Os campos nomeados pela auditoria MUST ter largura pelo conteúdo: na Comissão, o
  Identificador institucional e o Nome; no Requerimento do portal, o Telefone celular, a Faixa de
  renda, o Nome da mãe, o Nome do pai e a UF; nos Anexos, o Rótulo e o Arquivo. Campo com conteúdo
  esperado de até 20 caracteres MUST NOT passar de ~20 rem; nome MUST NOT passar de ~40 rem. As linhas
  de campo MUST NOT ser reorganizadas numa grade comum — isso é o registro
  `doc/achado-grade-dos-cartoes.md`, e continua registro.

**Limites da feature**

- **FR-1017**: O HTML da tela de distribuição MUST continuar abaixo de 120.000 caracteres, e o saldo
  de caracteres da feature MUST ser declarado. Comentário da folha MUST NOT ser removido para abrir
  espaço: as regras que esta feature substitui saem junto com a mudança.
- **FR-1018**: As telas que mudam de largura ou de disposição — Inscrições, Requerimento do portal,
  seleção do portal e a barra de filtro — MUST continuar sem rolagem horizontal da página e sem
  controle cortado a 375 px.
- **FR-1019**: A feature MUST NOT mudar texto de interface, view, formulário, domínio ou o PDF, e
  MUST NOT criar arquivo de tokens nem token de espaçamento: os três valores novos — escala de
  títulos, altura de controle e preenchimento de célula — moram na folha.

### Requisitos de experiência

- **UX-134**: Numa tela de ato, cada número MUST ser lido junto do seu rótulo sem depender de contar
  posições: bloco, e não fileira.
- **UX-135**: O peso visual MUST acompanhar a hierarquia: a ação principal da tela nunca é o elemento
  mais fraco dela, e na mesma barra nenhum botão parece de outra família por ter outra altura.
- **UX-136**: Ajuda de campo que explica o que se digita MUST continuar à vista enquanto se digita.

### Key Entities

Não há entidade de domínio nova nem alterada. Os "componentes" são desenhos da folha:

- **Bloco de números** (`ul.resumo`): um número em destaque e o seu rótulo, num bloco com moldura.
- **Botão principal, secundário, destrutivo e desabilitado** (`.botao` e modificadores) e **ação de
  linha** (`.acao`).
- **Barra de filtro** (`.filtro`/`.filtros`), **barra de navegação do assistente**
  (`.navegacao-etapa`) e **rodapé de confirmação** (`.salvar`).
- **Controle de formulário**: `input` dos tipos listados em **FR-1012** e `select`.

---

## Success Criteria *(mandatory)*

Medidos no mesmo banco (`ps_055_polish`, cópia de `ps_polish_audit`), a 1280 × 900, antes e depois;
a tabela vai para [verificacao.md](verificacao.md).

### Measurable Outcomes

- **SC-371**: No Corte, nenhum número da faixa calculada fica entre dois rótulos: cada um está dentro
  do bloco do seu.
- **SC-372**: Na Ocupação, os quatro números de um recorte apurado ficam em quatro blocos, como na
  Convocação, e o contêiner do recorte deixa de ser uma fileira.
- **SC-373**: A linha da tabela de Inscrições do Edital 51/2026 cai de 70 px para no máximo 45 px.
- **SC-374**: Na barra de navegação do assistente, Voltar, Salvar rascunho e Avançar têm diferença
  de 0 px de altura.
- **SC-375**: "Filtrar" (Inscrições, Distribuição, Comissão) e "Ver o que sairá vazio" (Matrículas)
  deixam de ter 25 px.
- **SC-376**: "Guardar e continuar depois" deixa de renderizar como botão nativo do navegador.
- **SC-377**: Na Convocação e no Processo, nenhum h3 é maior que o h2 da página.
- **SC-378**: Na Visão Geral, no Requerimento do portal e na Comissão, input e select da mesma linha
  têm diferença de 0 px de altura.
- **SC-379**: No filtro da Distribuição, o desnível entre os controles cai de 22 px para 0, e
  "Filtrar" tem a altura dos controles.
- **SC-380**: Na seleção sem sorteio, o Cronograma deixa de começar 335 px abaixo do topo das Vagas.
- **SC-381**: Na Comissão, o Identificador institucional deixa de ter 1.190 px e fica em no máximo
  ~20 rem.
- **SC-382**: No Requerimento do portal, o Telefone celular deixa de ter 1.232 px e fica em no máximo
  ~20 rem.
- **SC-383**: A pontuação da ordem calculada do marco fica alinhada à direita.
- **SC-384**: A suíte (`make lint check test-pg`) fica verde, e o HTML da distribuição continua abaixo
  de 120.000 caracteres, com o saldo declarado no PR.
- **SC-385**: A 375 px, Inscrições, Requerimento do portal, seleção do portal e a barra de filtro não
  ganham rolagem horizontal da página.

### O que esta feature não cobre, deliberadamente

- a altura do stepper do assistente, o tamanho do Conteúdo do Edital, a coluna de ações da Lista de
  Editais e o Detalhe do Edital — lotes 2 e 3;
- números em formato pt-BR na Revisão — lote 3.

Se um requisito acima prometer isso, está prometendo outra feature.

---

## Assumptions

- A medição "antes" repete a da auditoria no mesmo banco. O banco `ps_polish_audit` foi mantido pela
  auditoria para isso; esta feature trabalha numa cópia (`ps_055_polish`).
- "A mesma altura" é medida pelo `getBoundingClientRect` da página renderizada no Chrome do painel
  do aplicativo, arredondada ao pixel.
- O seed de demonstração não tem sorteio no Edital da seleção medida, nem avaliação em rascunho; o
  caso "com sorteio" de **FR-1015** é conferido por teste de template, e não por medida.
- Os valores "~20 rem" e "~40 rem" de **FR-1016** são teto, e não medida exata: a largura final é a do
  menor desenho que já existe na folha e cabe no teto.
