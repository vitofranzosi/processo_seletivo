# Feature Specification: Polish do assistente de composição

**Feature Branch**: `claude/assistente-composicao-polish-4d8abf`

**Created**: 2026-09-30

**Status**: Draft

**Input**: o prompt de sessão autônoma `doc/prompt/056-polish-assistente-de-composicao.md`, escrito em
30/09/2026 a partir da auditoria de polish de UI (`doc/auditoria-polish-ui-2026-09-30.md`). É o
**lote 2 de 3** da proposta de execução da auditoria (§9): os itens F1, F2, F3, F4, F5 e D4, e F6
por último e dispensável. O lote 1 é a `055` (folha e componentes), já na `main`; o lote 3 (telas de
operação) terá spec própria.

> **Faixa de identificadores.** Abre em **FR-1020**, **SC-386** e **UX-137**. O teto medido em
> 30/09/2026 em todas as worktrees, com quatro dígitos, era FR-1019, SC-385 e UX-136 — todos da
> `055`, já mergeada. As decisões desta spec nascem em `D-001` e moram no [research.md](research.md);
> as nove decisões que o prompt trouxe fechadas são **entrada**, e o research as registra como
> "decisões recebidas" (1ª a 9ª) sem reaproveitar a numeração delas.

**A frase que governa:**

> Quem abre uma etapa do assistente vê o trabalho da etapa na primeira dobra, e cada item da coleção
> ocupa a altura do que ele tem a dizer.

**E a frase que mantém o corte:**

> Densidade dentro do padrão que existe. Nenhuma coleção vira tabela editável nem mestre-detalhe,
> nenhum campo sai do formulário, e nada muda no que a etapa grava.

---

## Por que esta feature existe

A auditoria de 30/09 mediu o assistente de composição a 1280 × 900, no Edital 76/2027 do banco de
demonstração, e achou a sensação de "formulário administrativo" concentrada nele:

- **O trabalho da etapa começa abaixo da metade da tela.** As nove etapas do assistente quebram em
  duas linhas (7 + 2, com as duas últimas esticadas a 613 px cada); o stepper soma 174 px, e o
  título da etapa só aparece em y = 524 de 900.
- **Cada item de coleção gasta altura com o que não diz nada.** A Etapa de Avaliação, o Documento
  exigido e a Modalidade reservam uma linha inteira só para ↑ ↓ 🗑; a legenda repete o nome da
  categoria em todo item ("Modalidade de Concorrência", "Modalidade de Concorrência") e nunca diz
  **qual** item é.
- **No Cronograma, Início e Término ficam em linhas diferentes**, e a Descrição — obrigatória e
  cortada na tela — tem 258 px, enquanto "Onde acontece", opcional e quase sempre vazio, tem 436.
- **O Conteúdo do Edital tem 4.876 px**, mais de cinco telas: dezessete seções vazias do mesmo
  tamanho das preenchidas, cinco seções geradas em caixas de 121 a 139 px só para dizer que são
  geradas, e cada caixa com a largura da página para uma área de texto de 685 px.
- **A Revisão lê "Rótulo: valor" em texto corrido** por 7.992 px: quem confere o que vai congelar
  procura o rótulo dentro da frase, linha a linha.
- **Texto longo em campo de uma linha.** A Descrição do Perfil sai cortada num campo de 386 px; no
  Retificar, Título, Descrição e Declaração do Requerimento saem cortados em 312 px — enquanto o
  Compor oferece a mesma Descrição do Edital numa área de texto.
- **Na etapa Anexos, "Avançar" fica no meio da tela** (x = 607 a 709), porque a navegação dela tem
  outra largura que a das outras oito.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Quem abre uma etapa vê o trabalho dela na primeira dobra (Priority: P1)

A pessoa que compõe um Edital passa por nove etapas, e em todas elas o stepper ocupa o topo. Ela vê
as nove etapas numa linha, cada uma com número, nome e situação, e o trabalho da etapa começa logo
abaixo.

**Why this priority**: alcança as nove etapas de uma vez, e é o item de maior impacto por esforço
da auditoria.

**Independent Test**: abrir qualquer etapa do Edital 76/2027 a 1280 × 900 e medir a altura do
stepper e a posição do título da etapa em Perfis.

**Acceptance Scenarios**:

1. **Given** qualquer etapa do assistente a 1280 px, **When** aberta, **Then** as nove etapas
   ficam numa linha só, e o stepper tem no máximo 80 px de altura.
2. **Given** a etapa Perfis a 1280 × 900, **When** aberta, **Then** o título da etapa começa em
   y ≤ 440.
3. **Given** uma etapa concluída, uma pendente, uma pronta para revisar e a atual, **When** o
   stepper é lido, **Then** a situação de cada uma continua escrita em texto, e a atual continua
   marcada como atual.
4. **Given** uma janela estreita demais para nove colunas, **When** o stepper quebra, **Then** todas
   as colunas têm a mesma largura, inclusive as da última linha.

---

### User Story 2 — Cada item da coleção diz qual é, e não gasta linha com ações (Priority: P1)

Quem compõe o Cronograma, as Etapas de Avaliação, os Documentos exigidos ou as Modalidades de um
Perfil reconhece cada item pela legenda — "Evento do Cronograma 1 de 3 · Inscrições" —, e encontra
subir, descer e remover na mesma linha da legenda, à direita, sem uma linha só para eles.

**Why this priority**: é onde a altura se perde item a item, e a legenda genérica obriga a ler os
campos para saber de qual item se trata.

**Independent Test**: abrir Cronograma, Etapas, Inscrição e o editor de um Perfil, e conferir, em
cada cartão, que as ações estão na linha da legenda e que a legenda nomeia o item.

**Acceptance Scenarios**:

1. **Given** um cartão de Evento, Etapa de Avaliação, Documento exigido ou Modalidade, **When**
   renderizado, **Then** as ações do item ficam na linha da legenda, à direita, e nenhuma linha do
   cartão contém só ações.
2. **Given** um item com identificador preenchido, **When** renderizado, **Then** a legenda diz a
   categoria, a posição "N de M" onde a coleção é ordenável, e o identificador do item.
3. **Given** um item recém-acrescentado, ainda sem identificador, **When** renderizado, **Then** a
   legenda diz a categoria e a posição, sem texto vazio nem separador solto.
4. **Given** um item movido para cima ou para baixo, **When** a ordem muda, **Then** a posição
   "N de M" da legenda acompanha, e o identificador do item continua nela.
5. **Given** a remoção de um item preenchido, **When** pedida, **Then** a pergunta de confirmação é
   a mesma de antes, e o nome de cada ação para quem usa leitor de tela também.

---

### User Story 3 — O Evento do Cronograma se lê numa linha (Priority: P1)

Quem preenche o Cronograma lê cada Evento na ordem em que se preenche — que evento é, o que é,
quando começa, quando termina — numa linha, com a Descrição larga o bastante para ser lida, e o
local logo abaixo.

**Why this priority**: o Cronograma é a etapa que mais se revisita, e datas lidas em linhas
diferentes são datas conferidas com mais esforço.

**Independent Test**: abrir o Cronograma do Edital 76/2027 a 1280 px e medir o topo dos campos de
Início e Término, a largura da Descrição e a de "Onde acontece", e a altura do cartão.

**Acceptance Scenarios**:

1. **Given** um Evento a 1280 px, **When** renderizado, **Then** Tipo, Descrição, Início e Término
   estão na mesma linha, e "Onde acontece" na linha de baixo.
2. **Given** o mesmo Evento, **When** medido, **Then** a Descrição é mais larga que "Onde acontece".

---

### User Story 4 — O Conteúdo do Edital cabe em pouco mais de três telas (Priority: P1)

Quem revisa o texto das seções vê cada seção na largura do texto, a seção vazia pequena até alguém
escrever nela, e a seção gerada numa faixa curta que diz de onde ela vem — sem perder a informação
de que a seção vazia não sai no documento.

**Why this priority**: é a maior página do assistente depois da Revisão, e a maior parte dela é
caixa vazia.

**Independent Test**: abrir o Conteúdo do Edital 76/2027 a 1280 × 900 e medir a altura da página;
conferir que toda seção vazia diz que não sai no documento.

**Acceptance Scenarios**:

1. **Given** o Conteúdo do Edital 76/2027, **When** aberto a 1280 × 900, **Then** a página tem no
   máximo 3.000 px.
2. **Given** uma seção vazia, **When** renderizada, **Then** a área de texto nasce com 2 linhas, e
   a seção continua dizendo, à vista e no nome do campo, que não sai no documento.
3. **Given** uma seção preenchida, **When** renderizada, **Then** a área de texto tem a altura de
   antes.
4. **Given** uma seção gerada, **When** renderizada, **Then** ela aparece sem caixa própria, com o
   título, a origem e o caminho para a etapa de origem.
5. **Given** que se digita numa seção vazia, **When** o texto aparece, **Then** a numeração e a
   marca de "não sai" se recalculam como antes.

---

### User Story 5 — A Revisão se confere por coluna de rótulos (Priority: P2)

Quem confere o que será congelado lê cada item com os rótulos numa coluna e os valores ao lado, e
não procura o rótulo dentro da frase.

**Why this priority**: melhora a leitura do último passo antes da submissão; não muda o que se
confere.

**Independent Test**: abrir a Revisão do Edital 76/2027 e conferir que nenhuma linha "Rótulo: valor"
sai em texto corrido, e que a altura da página não cresce mais de 10%.

**Acceptance Scenarios**:

1. **Given** um item da Revisão com linhas rotuladas, **When** renderizado, **Then** os rótulos
   formam uma coluna, e cada valor fica ao lado do seu rótulo.
2. **Given** uma linha sem rótulo — o texto de uma seção, a descrição de um Evento, a declaração do
   Requerimento —, **When** renderizada, **Then** ela continua em texto corrido, e nenhum trecho do
   texto escrito por quem elabora é tomado por rótulo.
3. **Given** a Revisão, **When** comparada com a de antes, **Then** o conteúdo e a ordem de todas
   as linhas são os mesmos.

---

### User Story 6 — Texto longo se lê inteiro onde se escreve (Priority: P2)

Quem preenche a Descrição do Perfil, a Instrução ao candidato de um Documento exigido, ou corrige
no Retificar o Título, a Descrição e a Declaração do Requerimento, lê o valor inteiro numa área de
texto de duas linhas, e não um trecho cortado.

**Why this priority**: corrigir o que não se lê inteiro é corrigir às cegas; no Retificar, é ato
publicado.

**Independent Test**: abrir o editor de um Perfil, a etapa Inscrição e o Retificar do Edital 01/2026,
e conferir que os cinco campos mostram o valor do banco de demonstração sem corte.

**Acceptance Scenarios**:

1. **Given** um desses cinco campos com o valor do banco de demonstração, **When** renderizado,
   **Then** ele é uma área de texto de 2 linhas e o valor aparece sem corte horizontal.
2. **Given** um desses campos alterado no Retificar, **When** a pessoa digita, **Then** a marca de
   campo alterado aparece como antes.

---

### User Story 7 — Na etapa Anexos, "Avançar" está onde está nas outras (Priority: P3)

Quem chega à etapa Anexos encontra "Avançar" na borda direita, como nas outras oito etapas.

**Why this priority**: incômodo de posição, sem bloqueio.

**Independent Test**: medir a posição horizontal de "Avançar" em Anexos e em outra etapa.

**Acceptance Scenarios**:

1. **Given** a etapa Anexos, **When** aberta a 1280 px, **Then** "Avançar" está na mesma posição
   horizontal que nas outras etapas.

---

### User Story 8 — O Perfil no Retificar começa pelo que o identifica (Priority: P3, dispensável)

Quem corrige um Perfil no Retificar encontra os campos na ordem em que os compôs: primeiro o que o
identifica, os Requisitos depois.

**Why this priority**: último do lote, e dispensável: só entra se couber sem risco.

**Independent Test**: comparar a ordem dos rótulos do cartão do Perfil no Retificar com a do editor
do Perfil no Compor.

**Acceptance Scenarios**:

1. **Given** o cartão de um Perfil no Retificar, **When** renderizado, **Then** Denominação vem
   antes de Requisitos, na ordem do Compor — ou o motivo de não vir está registrado.

---

### Edge Cases

Os casos-limite desta feature são requisitos, e estão escritos como tal abaixo — a seção de casos
de borda não entra na matriz de rastreabilidade, e nenhuma ferramenta a cobra:

- item recém-acrescentado sem identificador (**FR-1024**);
- item reordenado (**FR-1025**);
- legenda longa ao lado das ações em tela estreita (**FR-1026**);
- Modalidade sem "Aplicar aos demais Perfis", quando o Edital tem um Perfil só (**FR-1023**);
- seção preâmbulo e seção textual com norma acrescentada (**FR-1031**);
- texto de quem elabora que contém dois-pontos (**FR-1033**);
- janela de 375 px (**FR-1042**).

---

## Requirements *(mandatory)*

### Functional Requirements

**O stepper (F1)**

- **FR-1020**: A partir de 1280 px de janela, o stepper do assistente MUST mostrar as nove etapas
  numa linha só, cada uma com número, nome e situação.
- **FR-1021**: Abaixo da largura que comporta as nove numa linha, o stepper MAY quebrar, mas em
  colunas de largura igual em todas as linhas: nenhuma etapa da última linha estica para ocupar o
  que sobra.
- **FR-1022**: A situação de cada etapa MUST continuar escrita em texto — "concluída", "pendente",
  "pronta para revisar", "etapa atual" —, e as marcas que hoje distinguem as situações sem depender
  só de cor MUST continuar.

**As coleções em cartão (F2)**

- **FR-1023**: Nos cartões de Evento do Cronograma, Etapa de Avaliação, Documento exigido e
  Modalidade de Concorrência, as ações do item — subir, descer e remover; na Modalidade, "Aplicar aos
  demais Perfis" quando existe e "Remover esta Modalidade" — MUST ficar na linha da legenda, à
  direita. Nenhum desses cartões MUST ter uma linha que contenha só ações, em janela onde a legenda e
  as ações cabem lado a lado.
- **FR-1024**: A legenda desses cartões MUST dizer de qual item se trata: a categoria, a posição
  "N de M" onde a coleção é ordenável, e o identificador do item — o Tipo do Evento, o Nome da
  Etapa, o Nome do Documento e o Código da Modalidade. O identificador é o do item como está
  gravado ou reexibido pelo servidor. Item sem identificador MUST mostrar só a categoria e a posição.
- **FR-1025**: A reordenação MUST continuar atualizando a posição "N de M" na legenda, sem apagar
  o identificador do item.
- **FR-1026**: A legenda e as ações MUST NOT se sobrepor em janela nenhuma. Em janela estreita, onde
  as duas não cabem lado a lado, as ações MAY descer para uma linha própria, abaixo da legenda e à
  direita.
- **FR-1027**: A pergunta de confirmação da remoção, o nome acessível de cada ação e o nome
  acessível do grupo de campos MUST ser os de antes. As ações não entram no nome do grupo.
- **FR-1028**: No cartão de Evento, Tipo, Descrição, Início e Término MUST ficar na mesma linha a
  1280 px, e "Onde acontece" na linha de baixo. A Descrição MUST ser mais larga que "Onde acontece".

**O Conteúdo do Edital (F3)**

- **FR-1029**: O cartão de cada seção MUST ter a largura da medida de leitura, e não a da página.
- **FR-1030**: A área de texto de seção vazia MUST nascer com 2 linhas; a de seção preenchida, com a
  altura de antes.
- **FR-1031**: A marca de seção que não sai no documento MUST continuar visível e no nome do campo,
  e MAY ficar mais curta ou mais discreta. A de preâmbulo, também. O recálculo enquanto se digita
  MUST continuar.
- **FR-1032**: A seção gerada MUST NOT ter caixa própria: título, origem e o caminho para a etapa
  de origem numa faixa curta. O texto que explica a seção gerada MUST ser o de antes.

**A Revisão (F4)**

- **FR-1033**: Toda linha da Revisão que o sistema compõe como "Rótulo: valor" MUST ser apresentada
  como par de termo e definição numa grade que a folha já tem, com os rótulos numa coluna. Linha
  sem rótulo — inclusive todo texto escrito por quem elabora — MUST continuar em texto corrido, e
  nenhum dois-pontos dentro dele MUST ser tomado por rótulo.
- **FR-1034**: A Revisão MUST NOT mudar o conteúdo nem a ordem de linha alguma, e MUST NOT mexer em
  formato de número ou data.

**Texto longo (F5)**

- **FR-1035**: A Descrição do Perfil e a Instrução ao candidato do Documento exigido MUST ser áreas
  de texto de 2 linhas, com o mesmo nome e o mesmo valor enviado.
- **FR-1036**: No Retificar, Título do Edital, Descrição e Declaração do Requerimento de Matrícula
  MUST ser áreas de texto de 2 linhas, com o mesmo nome de campo, e a detecção de campo alterado
  MUST continuar funcionando.

**Anexos (D4)**

- **FR-1037**: A navegação e o estado vazio da etapa Anexos MUST ter as larguras das outras etapas,
  com "Avançar" na mesma posição horizontal.

**Ordem do Perfil no Retificar (F6)**

- **FR-1038**: O cartão do Perfil no Retificar SHOULD apresentar os campos na ordem do Compor —
  Denominação antes, Requisitos depois — sem mudar nome de campo. Se a ordem não puder mudar sem
  renomear campo, ou se um script ou teste depender dela, o item MUST sair do lote e virar registro.

**Limites da feature**

- **FR-1039**: O envio de "Salvar rascunho" de cada etapa MUST ser idêntico, nas chaves e nos
  valores, antes e depois da feature, no mesmo rascunho. Nenhum campo sai do formulário e nenhum
  nome de campo muda; mudar o controle de um campo (campo de linha para área de texto) é permitido.
- **FR-1040**: O HTML da tela de distribuição MUST continuar abaixo de 120.000 caracteres, com o
  tamanho antes e depois declarado. Comentário novo de folha nasce como comentário do template, e
  não do CSS; as regras que a feature torna mortas saem junto.
- **FR-1041**: A feature MUST NOT mudar texto de ajuda além da marca de seção vazia, view de
  gravação, formulário de domínio, o PDF, nem Perfis e Classificação além da Modalidade e da
  Descrição; e MUST NOT criar tabela editável, mestre-detalhe ou padrão de interação novo.
- **FR-1042**: O stepper, o Cronograma e o Conteúdo MUST continuar sem rolagem horizontal da página
  e sem controle cortado a 375 px.

### Requisitos de experiência

- **UX-137**: O trabalho da etapa MUST começar na primeira dobra: o que está acima dele é navegação
  e contexto, e não ocupa mais da metade da tela.
- **UX-138**: A altura de cada item de coleção MUST acompanhar o que ele tem a dizer: nem linha só
  para ações, nem caixa do tamanho de uma preenchida para uma seção vazia.
- **UX-139**: Um item de coleção MUST se identificar pela legenda: reconhecer o terceiro Evento não
  pode exigir ler os campos dele.

### Key Entities

Não há entidade de domínio nova nem alterada. Os elementos são desenhos do assistente:

- **Stepper** (`ol.assistente`): as nove etapas, com número, nome e situação.
- **Cartão de item** (`fieldset.linha`): legenda, ações do item e campos. Quatro espécies estão no
  escopo: Evento, Etapa de Avaliação, Documento exigido e Modalidade de Concorrência.
- **Seção do Conteúdo** (`fieldset.secao`): textual ou gerada, com número e marca de estado.
- **Item da Revisão**: título e linhas; a linha pode ser rotulada ("Rótulo: valor") ou corrida.

---

## Success Criteria *(mandatory)*

Medidos no banco `ps_056_polish` (cópia de `ps_polish_audit`, o banco da auditoria), no Edital
76/2027 em elaboração, a 1280 × 900, antes e depois; a tabela vai para [verificacao.md](verificacao.md).

### Measurable Outcomes

- **SC-386**: O stepper fica numa linha, com no máximo 80 px de altura (antes: duas linhas, 174 px).
- **SC-387**: Em Perfis, o título da etapa começa em y ≤ 440 (antes: 524).
- **SC-388**: No Cronograma, Início e Término têm o mesmo topo, e a Descrição é mais larga que
  "Onde acontece" (antes: 258 contra 436 px).
- **SC-389**: O cartão de Evento do Cronograma cai para no máximo 150 px (antes: 215).
- **SC-390**: Nenhum cartão de Evento, Etapa, Documento ou Modalidade tem linha só de ações, e toda
  legenda desses cartões diz de qual item se trata.
- **SC-391**: O Conteúdo do Edital tem no máximo 3.000 px (antes: 4.876), e toda seção vazia
  continua dizendo que não sai no documento.
- **SC-392**: Na Revisão, os rótulos formam uma coluna, e a página não cresce mais de 10% (antes:
  7.992 px; teto: 8.791).
- **SC-393**: A Descrição do Perfil, a Instrução ao candidato e os três campos longos do Retificar
  mostram o valor do banco de demonstração sem corte.
- **SC-394**: Em Anexos, "Avançar" fica na mesma posição horizontal das outras etapas (antes: 607 a
  709 px, contra 1.155 a 1.256).
- **SC-395**: O envio de "Salvar rascunho" de cada etapa é idêntico antes e depois.
- **SC-396**: A suíte (`make lint check test-pg`, com os testes de JavaScript) fica verde, e o HTML
  da distribuição continua abaixo de 120.000 caracteres, com o tamanho antes e depois registrado.
- **SC-397**: A 375 px, o stepper, o Cronograma e o Conteúdo não ganham rolagem horizontal.

### O que esta feature não cobre, deliberadamente

- a tabela editável do Cronograma (análise de 29/09, P2);
- o seletor de Modalidade agrupado por Perfil nos Documentos (P3 daquela análise);
- o tamanho do Retificar, que é estrutural e já está registrado;
- números e datas em formato pt-BR — é o lote 3.

Se um requisito acima prometer isso, está prometendo outra feature.

---

## Assumptions

- A medição "antes" foi feita sobre `a7ade983` (a `main` com a `055` e a conversão dos comentários
  da folha, PR 244), no banco `ps_056_polish`, antes de qualquer template ou folha mudar.
- "Idêntico" no envio (**FR-1039**) é medido sobre o corpo que o navegador monta para o botão
  "Salvar rascunho" de cada etapa, sem o token de CSRF, que muda a cada carga. O rascunho não é
  gravado durante a medição, para que "antes" e "depois" leiam o mesmo estado.
- As medidas são do `getBoundingClientRect` na página renderizada no navegador do aplicativo,
  arredondadas ao pixel; as de 375 px, com o viewport emulado.
- Os números-alvo (80 px, 440, 150 px, 3.000 px) vêm do prompt. Meta numérica fora de alcance dentro
  do escopo não amplia o escopo: o valor alcançado e a justificativa vão para o `verificacao.md`.
