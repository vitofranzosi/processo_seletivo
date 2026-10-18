# Feature Specification: A folha da gestão por área, o estilo de cada tela em arquivo, e a política de segurança de conteúdo

**Feature Branch**: `claude/folha-por-area-e-csp-091-cce475`, sobre a `main` em `21e36bd4` (com a `089`);
a implementação espera o PR #307 (`090`), que muda uma regra da mesma folha

**Created**: 2026-10-18

**Status**: Especificada — implementação depois do merge do PR #307

**Input**: passos 2 e 3 de três, pedidos pelo usuário em 18/10/2026, depois de a `089` tirar a folha
comum da gestão do HTML: dividir a folha comum por área e tirar as regras duplicadas; levar os cinco
parciais de estilo e os blocos de estilo por tela para arquivos, carregados só nas telas que os usam;
tirar os atributos `style=""` que restam; e ligar a política de segurança de conteúdo (CSP), sem
dependência nova, com o portal do candidato decidido e registrado.

> **Faixa de identificadores.** Esta spec usa FR-2090 a FR-2116 e SC-810 a SC-817, da faixa reservada
> a ela (FR-2090–2129, SC-810–819). Nenhum dos dois aparecia na `main` (`21e36bd4`) nem na branch do
> PR #307 em 18/10/2026; a faixa da `090` termina antes desta.

---

## Por que esta feature existe

**A folha comum é um arquivo só de 106 KB, em ordem de chegada.** A `089` a tirou do HTML na ordem em
que as regras foram escritas ao longo de oitenta features: a regra do cabeçalho impresso da `088` está
entre as da barra lateral, a da tabela de alterações da Retificação entre as de texto corrido, os
campos de formulário em quatro trechos distantes. Quem procura "onde está o estilo das tabelas" lê o
arquivo inteiro. E a mesma regra aparece mais de uma vez — escrita de novo por quem não a achou.

**O estilo de 27 telas ainda viaja no HTML de cada uma.** O ponto de extensão da `040` — o estilo
"daquela tela, e não de todas" — continua num `<style>` no documento, e cinco parciais de modelo
repetem o mesmo estilo em até cinco telas. A visão geral leva 12 KB de regras em cada resposta, sem
cache. As duas telas do assistente repetem regras quase iguais, cada uma no seu bloco.

**Sem isso, a CSP não liga.** A defesa padrão contra injeção de estilo e de marcação é a política que
recusa estilo e script embutidos. Ela não pode ser ligada enquanto houver um `<style>` ou um
`style=""` nas páginas: o navegador recusaria o estilo legítimo junto com o injetado. A `089` tirou o
maior obstáculo; restam os 27 blocos por tela, os cinco parciais, quatro `style=""` na gestão, o
`<style>` da página de erro e o que o htmx injeta por conta própria. O guia de implantação (M-1) e a
auditoria de 15/10 (GO-04) registram a falta da política desde a `002`.

**O que não muda, e não se negocia aqui:** nenhum pixel de nenhuma tela; nenhuma regra de negócio,
permissão, endereço de tela, view, consulta ao banco, texto ou conteúdo normativo. A folha própria do
portal do candidato fica onde está, no documento (D-007).

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Quem trabalha na gestão vê as mesmas telas, com uma barreira a mais (Priority: P1)

A avaliadora abre a lista de Processos, Minhas Etapas, a Distribuição, a visão geral e a Mesa. Cada tela
é idêntica à de ontem, pixel a pixel, com a barra expandida ou recolhida, a 1280 e a 375 px. Se alguém
conseguisse plantar um estilo ou um script no meio de um texto exibido pela gestão, o navegador se
recusaria a aplicá-lo.

**Why this priority**: é a razão do passo 3 — a barreira — com a condição que o usuário pôs: nada muda
de aparência.

**Independent Test**: refazer o inventário visual antes e depois e comparar; abrir cada tela do
inventário no navegador e ler o console; plantar um estilo embutido numa página e ver o navegador
recusá-lo.

**Acceptance Scenarios**:

1. **Given** qualquer tela do inventário visual, nos dois estados da barra, a 1280 e a 375 px, **When**
   ela é capturada antes e depois, **Then** as duas imagens só diferem no ruído conhecido, nenhuma
   estoura a largura e nenhuma muda de `status`.
2. **Given** qualquer tela do inventário, **When** ela é aberta no navegador com a política ligada,
   **Then** o console não registra nenhuma violação da política.
3. **Given** uma resposta HTML da gestão, **When** um estilo ou um script embutido é acrescentado a
   ela, **Then** o navegador não o aplica nem o executa.

---

### User Story 2 — Quem mantém a folha acha a regra pela área, e cada tela leva só o seu estilo (Priority: P1)

O desenvolvedor precisa mudar o desenho das tabelas: abre o arquivo das tabelas, e não um de 1.471
linhas. Precisa mudar o estilo da visão geral: abre o arquivo da visão geral, e a mudança não viaja para
nenhuma outra tela. Ao procurar uma regra, acha uma — não duas iguais.

**Why this priority**: é a razão do passo 2; sem ela, a CSP poderia ser ligada com os estilos por tela
num arquivo comum, mas o motivo da `040` — o estilo de uma tela não viaja em todas — se perderia.

**Independent Test**: conferir que cada arquivo de estilo de tela é carregado só pelas telas que o
usam; que a folha comum não tem duas regras idênticas; e que a ordem em que as regras se aplicam não
mudou onde mudar alteraria o resultado.

**Acceptance Scenarios**:

1. **Given** a folha comum dividida, **When** se procura uma regra de tabela, de formulário, da
   moldura ou de impressão, **Then** ela está no arquivo daquela área, salvo onde mover a regra mudaria
   a cascata — e a pesquisa registra essas exceções.
2. **Given** uma tela com estilo próprio, **When** outra tela da gestão é aberta, **Then** o estilo da
   primeira não é carregado.
3. **Given** a folha comum e os estilos por tela, **When** se procura duas regras com o mesmo seletor,
   as mesmas declarações e a mesma condição de mídia, **Then** não há nenhum par.

---

### User Story 3 — Quem mantém a folha continua protegido pelos mesmos guardiões (Priority: P1)

O desenvolvedor acrescenta, por engano, uma largura em pixels no estilo da visão geral, ou uma classe
sem regra no estilo de uma tela. Os testes que reprovavam o engano quando o estilo estava no modelo
continuam reprovando com ele num arquivo estático. E quem escreve um script embutido, um `onclick` ou
um `style=""` num modelo da gestão vê um teste reprovar antes de o navegador recusar.

**Why this priority**: a `089` mostrou que mover a folha deixa afirmações negativas passando sem
examinar nada (R-005 da `089`); este passo move de novo, e para mais lugares.

**Independent Test**: para cada guardião que lê a folha ou o estilo de uma tela, plantar no arquivo
novo uma violação da regra dele e ver o teste reprovar.

**Acceptance Scenarios**:

1. **Given** cada guardião que lia a folha comum, um parcial de estilo ou o bloco de uma tela, **When**
   uma violação é plantada no arquivo estático correspondente, **Then** ele reprova.
2. **Given** um modelo da gestão, **When** ganha um `<style>`, um `style=""`, um script embutido ou um
   atributo de evento, **Then** um guardião reprova.

---

### User Story 4 — O portal, a página de acesso e a página de erro (Priority: P2)

A pessoa que entra pela página de identificação da gestão e quem cai numa página inexistente veem as
mesmas cores e medidas, sob a política. O candidato vê o portal como hoje; a política vale para ele em
modo de observação — o navegador acusa o que recusaria, sem recusar —, até o portal ter os próprios
estilos fora do documento.

**Why this priority**: a página de acesso é da gestão e entra sob a política; o portal tem 70 KB de
folha própria no documento, e tirá-la é um passo do tamanho da `089` inteira (D-007).

**Independent Test**: capturar antes e depois a página de identificação e duas telas do portal; ler o
cabeçalho das respostas.

**Acceptance Scenarios**:

1. **Given** a página de identificação e duas telas do portal, **When** capturadas antes e depois a
   1280 e a 375 px, **Then** só diferem no ruído conhecido.
2. **Given** uma resposta HTML do portal, **When** se lê o cabeçalho, **Then** ela traz a política em
   modo de observação, e não em modo de recusa.
3. **Given** um endereço inexistente sob a gestão, **When** a página de erro é servida, **Then** ela
   está sob a política e aparece com as cores de hoje.

### Edge Cases

- **Uma folha da área não carrega.** Cada arquivo é conferido pela verificação de sistema da `089`
  antes de o serviço atender alguém; um arquivo citado num modelo e ausente é erro, e não `<link>`
  quebrado em silêncio.
- **Mover uma regra muda o vencedor.** Duas regras com a mesma especificidade que alcançam o mesmo
  elemento e declaram a mesma propriedade não trocam de ordem. Quando a área pediria a troca, a regra
  fica onde está, e a exceção é registrada.
- **Remover a segunda cópia de uma regra muda o vencedor.** Se entre as duas cópias há outra regra que
  a primeira perde e a segunda vence, a segunda não é duplicada de fato: ela fica.
- **Largura que vem do dado.** A barra de progresso de Minhas Etapas e as barras da série de
  inscrições têm a medida calculada por linha; sem `style=""`, a medida vem de uma classe, e o valor
  aplicado é o mesmo, de 0 a 100%.
- **Estilo que o script escreve.** Script que muda a propriedade de estilo de um elemento não é estilo
  embutido para a política e continua funcionando; script que escreve o atributo `style` ou marcação
  com ele seria recusado, e não pode existir.
- **O htmx.** A biblioteca injeta um `<style>` próprio ao carregar e pode avaliar expressões; as duas
  coisas são desligadas por configuração declarada na página, sem script embutido.
- **A Mesa e a prévia.** O documento do candidato abre num quadro e o PDF da prévia num objeto, ambos da
  própria origem; a política os permite, e a proteção contra ser emoldurado por outra origem continua
  com o cabeçalho que já a faz.
- **Página de depuração do servidor local.** As páginas de erro do próprio framework, com depuração
  ligada, trazem estilo e script embutidos; elas ficam fora da política, e só elas (D-010).
- **Impressão.** As regras de impressão continuam valendo no papel como antes.
- **O fragmento do protótipo do assistente.** Ele é acrescentado à página pública da seleção, que é do
  portal; o estilo dele vai para arquivo como o das telas, e a página o carrega junto do fragmento.

## Requirements *(mandatory)*

### Functional Requirements

#### A folha comum por área

- **FR-2090**: As regras da folha comum da gestão MUST passar a arquivos estáticos por área — ao menos
  a moldura (o shell), a base e a tipografia, os componentes comuns, os formulários, as tabelas, as
  telas e a impressão —, sem mudança de seletor, propriedade ou valor, salvo a remoção de duplicadas
  do FR-2093.
- **FR-2091**: A ordem relativa de duas regras MUST NOT mudar quando as duas declaram ao menos uma
  propriedade em comum e alcançam algum elemento em comum; mudar a ordem de regras sem propriedade em
  comum é livre. Toda troca de ordem MUST ser provada assim, e toda regra que fica fora da sua área por
  essa razão MUST ser registrada na pesquisa.
- **FR-2092**: As bases MUST carregar os arquivos da folha comum na ordem da cascata, cada um com a
  versão do conteúdo no endereço; a lista dos arquivos e a ordem MUST ter uma fonte só, e a verificação
  de sistema MUST conferir cada arquivo. A forma de carregar é a do D-002.
- **FR-2093**: Uma regra MUST sair por duplicada só quando outra, com o mesmo seletor, as mesmas
  declarações e a mesma condição de mídia, continuar valendo para todo elemento que ela alcançava; a
  pesquisa MUST listar cada uma que saiu e a prova.
- **FR-2094**: Cada comentário explicativo MUST acompanhar a regra que explica para o arquivo da área,
  como comentário de CSS (D-002 da `089`); o comentário de uma duplicada que saiu MUST ficar junto da
  regra que fica.

#### O estilo de cada tela em arquivo

- **FR-2095**: Os cinco parciais de estilo da gestão MUST virar arquivos estáticos, um por parcial, e
  os parciais MUST sair.
- **FR-2096**: O estilo próprio de cada tela que preenche o ponto de extensão da `040` MUST virar arquivo
  estático, por tela ou por grupo de telas que dividem as mesmas regras, carregado só pelas telas que o
  usam, depois da folha comum e na ordem de hoje — parcial antes do estilo próprio. O ponto de extensão
  MAY continuar existindo para os `<link>`.
- **FR-2097**: Nenhum modelo da gestão e da página de acesso MUST conter `<style>`.
- **FR-2098**: As regras que as duas telas do assistente repetem MUST ficar num arquivo só, carregado
  pelas duas; o que difere entre elas MUST ficar no arquivo de cada uma, provado pelo FR-2091 e pelo
  FR-2093.
- **FR-2099**: O estilo do fragmento do protótipo do assistente MUST ir para arquivo estático,
  carregado pelo próprio fragmento.
- **FR-2100**: O estilo da página de erro MUST ir para arquivo estático do diretório comum, como os
  tokens.

#### Os atributos de estilo

- **FR-2101**: Nenhum modelo da gestão e da página de acesso MUST conter atributo `style`. As medidas que
  vêm do dado MUST vir de classe, com o mesmo valor aplicado.
- **FR-2102**: A pesquisa MUST listar o que o portal ainda tem de estilo e de atributo de estilo no
  documento, por arquivo, como entrada do passo que o trará para a política.

#### A política de segurança de conteúdo

- **FR-2103**: Toda resposta HTML sob a gestão — telas, fragmentos, página de acesso e página de erro —
  MUST trazer a política em modo de recusa, com estilo e script só da própria origem, sem permissão a
  estilo ou script embutido e sem permissão a avaliação de texto como código.
- **FR-2104**: Toda outra resposta HTML do sistema — o portal do candidato e a página pública da
  seleção — MUST trazer a mesma política em modo de observação; a decisão e a condição para passar a
  modo de recusa MUST estar registradas (D-007).
- **FR-2105**: A política MUST NOT exigir dependência nova; o cabeçalho MUST ter uma definição só, e as
  respostas que não são HTML MUST NOT recebê-lo.
- **FR-2106**: Nenhum modelo MUST conter script embutido, atributo de evento ou endereço `javascript:`;
  nenhum script da interface MUST escrever o atributo `style` nem marcação com ele (D-008).
- **FR-2107**: O htmx MUST NOT injetar estilo nem avaliar texto como código nas páginas que o carregam,
  por configuração declarada sem script embutido (D-009).
- **FR-2108**: A página de depuração do framework, no servidor local, MUST ficar fora da política; toda
  outra resposta HTML, no servidor local e em produção, MUST trazer o mesmo cabeçalho. O guia de
  implantação MUST registrar que o servidor web não acrescenta outra política (D-010).
- **FR-2109**: A proteção contra a gestão ser emoldurada por outra origem MUST continuar como está; a
  política MUST permitir o quadro da Mesa e o objeto da prévia, que são da própria origem.

#### Os guardiões

- **FR-2110**: Todo teste que lia a folha comum, um parcial de estilo ou o bloco de estilo de uma tela
  MUST passar a ler o arquivo estático, ou a folha que a página aplica; nenhum MUST ficar mais fraco, e
  cada um MUST ser provado por mutação no arquivo novo.
- **FR-2111**: Os arquivos estáticos novos MUST NOT conter sintaxe de modelo, e o guardião da `089` MUST
  alcançá-los todos.
- **FR-2112**: Um teste MUST conferir o cabeçalho da política nos dois modos e a ausência dele fora do
  HTML; outro MUST conferir que cada arquivo de estilo de tela é carregado só pelas telas que o citam.

#### O que não pode piorar

- **FR-2113**: Nenhuma variante do inventário visual MUST mudar de aparência além do ruído conhecido,
  deixar de carregar, mudar de `status` ou passar a estourar a 375 ou a 1280 px, com a barra expandida e
  com ela recolhida; o mesmo MUST valer para a página de identificação, a página de erro e duas telas do
  portal.
- **FR-2114**: As regras de impressão MUST continuar valendo no papel como antes.
- **FR-2115**: O guardião de peso da Distribuição MUST continuar com o teto de 120.000 bytes; a pesquisa
  MUST registrar o tamanho da resposta HTML da Distribuição, da lista e de Minhas Etapas, antes e depois.
- **FR-2116**: Nenhuma regra de negócio, permissão, endereço, view, consulta ou texto MUST mudar.

### Key Entities

Nenhuma. Só apresentação, entrega de arquivos estáticos e um cabeçalho de resposta.

## Decisões

### D-001 — Áreas por arquivo, e a ordem só muda onde não importa

A folha da `089` está na ordem de chegada. Cortá-la em fatias contíguas daria arquivos com nome de
área e conteúdo misturado; reordená-la à vontade mudaria a cascata. A regra é a do FR-2091: duas regras
só trocam de ordem quando não disputam propriedade nenhuma em elemento nenhum. A prova tem duas
partes, da mais barata à mais cara: (1) as propriedades declaradas, expandidas dos atalhos, não se
cruzam — então a ordem não importa em lugar nenhum; (2) quando se cruzam, nenhum elemento de nenhuma
página do inventário é alcançado pelas duas — e, se algum é, a regra fica onde está. A regra que fica
fora da área por isso é registrada, e não forçada.

### D-002 — Vários `<link>`, de uma lista só, e não um arquivo que importa os outros

Um arquivo de entrada com `@import` seria um `<link>` só nas bases, mas cobra duas coisas. O navegador
só descobre os importados depois de baixar o de entrada — uma ida e volta a mais antes de desenhar, na
primeira visita. E os endereços dentro de um `.css` não passam pelo modelo: os importados não levariam
a versão do conteúdo, e o cache que a `089` resolveu voltaria a servir folha velha. Os `<link>` saem de
uma lista só, a mesma que a verificação de sistema confere, cada um com a versão; o navegador os
descobre todos ao ler o cabeçalho do documento e os baixa em paralelo.

### D-003 — Duplicada é a regra igual que não muda nada ao sair

Igual é seletor, declarações e mídia iguais. "Quase igual" não é duplicada: as regras das duas telas do
assistente que diferem numa declaração ficam no arquivo de cada tela, e só a parte igual vai para o
arquivo comum das duas. Sair não pode mudar o vencedor (FR-2093): se uma regra entre as duas cópias
disputa com elas, a segunda fica.

### D-004 — O estilo da tela num arquivo por tela, ou por grupo

Os parciais já são grupos — o do aviso serve a três telas, o do acesso a cinco —, e viram um arquivo
cada. O estilo próprio de cada tela vira um arquivo com o nome da tela. O ponto de extensão da `040`
continua no cabeçalho do documento, agora com `<link>`, depois da folha comum: a ordem da cascata é a
de hoje. A primeira visita a uma tela com estilo próprio paga um pedido a mais; daí em diante ele vem
do cache, e o HTML da tela não o carrega mais.

### D-005 — A medida que vem do dado vira classe

As duas medidas calculadas — o percentual concluído de Minhas Etapas e a altura de cada barra da série
— são inteiros de 0 a 100. Uma classe por valor dá a mesma medida sem atributo de estilo e sem script.
Descartados: medir por script, que deixaria a barra vazia sem ele; trocar o desenho por um elemento de
progresso do navegador, que muda a aparência; e variável de CSS no atributo, que continua sendo
atributo de estilo. O `style` do contêiner dos símbolos vira regra.

### D-006 — Uma política, escrita por quem responde

O cabeçalho sai do servidor da aplicação, por um middleware do próprio projeto — o framework, na versão
em uso, não traz a política —, e não do servidor web: assim ele é testável na suíte, igual no servidor
local e em produção, e muda junto com as páginas que protege. A política permite à página só a própria
origem, e nada embutido.

### D-007 — O portal fica em observação, até a folha dele sair do documento

O portal tem uma folha própria de 70 KB no documento e um `style=""`; recusar estilo embutido nele hoje
o deixaria sem desenho. Tirá-la é uma `089` do portal, com os guardiões dele repontados e provados — um
passo próprio. Até lá, a mesma política vale para o portal em modo de observação: o navegador acusa no
console o que recusaria, sem recusar, e quem mexer no portal vê o que falta. O passo seguinte é tirar a
folha e o atributo do portal e trocar o modo; a pesquisa lista o que falta (FR-2102).

### D-008 — Script só de arquivo, sem nonce e sem resumo

Nenhum modelo tem script embutido nem atributo de evento hoje. Um nonce exigiria um valor novo por
resposta e passá-lo a cada modelo; um resumo por script prenderia cada mudança de texto a um número.
Os dois só servem a quem tem script embutido. A política permite script só da própria origem, e um
guardião impede o primeiro script embutido de nascer.

### D-009 — O htmx configurado pela página

O htmx, ao carregar, injeta um `<style>` com as regras do indicador de carregamento — que nenhuma tela
usa — e pode avaliar expressões de atributos — que nenhuma tela escreve. As duas coisas se desligam por
uma configuração declarada num `<meta>` da base, que não é script e que a política não recusa.

### D-010 — Igual no servidor local e em produção, menos a página de depuração

O mesmo cabeçalho sai nos dois lugares, porque sai da aplicação. A exceção é a página de erro que o
próprio framework monta com a depuração ligada, que só existe no servidor local e traz estilo e script
embutidos: sob a política, ela perderia o desenho e o que se expande nela. Em produção a depuração não
liga, e a página de erro é a do sistema, sob a política. O servidor web do guia não acrescenta
política — duas políticas se somam, e a mais restrita venceria em silêncio. Os estáticos não levam o
cabeçalho, que não tem efeito numa folha ou num script. A proteção contra moldura por outra origem
continua com o cabeçalho que já a faz, porque a prévia do PDF depende de uma exceção dele por tela.

## Success Criteria *(mandatory)*

- **SC-810**: Refeito o inventário visual nos dois estados da barra, **zero** variantes diferem pixel a
  pixel além do ruído conhecido, **zero** estouram, e **nenhuma** muda de `status`; o mesmo na página
  de identificação, na página de erro e em duas telas do portal.
- **SC-811**: **Zero** `<style>` e **zero** atributos `style` nos modelos da gestão e da página de
  acesso; **zero** scripts embutidos e atributos de evento em todos os modelos.
- **SC-812**: Abertas no navegador todas as telas do inventário, o console registra **zero** violações
  da política na gestão e na página de acesso; no portal, só as previstas pela pesquisa, em modo de
  observação.
- **SC-813**: **Todos** os guardiões que liam a folha comum, um parcial ou o bloco de uma tela reprovam
  diante de uma violação plantada no arquivo novo, um a um.
- **SC-814**: A suíte contra PostgreSQL continua sem falhas.
- **SC-815**: **Nenhum** arquivo de estilo de tela é carregado por uma tela que não o usa, e **nenhuma**
  tela deixa de carregar o que usava.
- **SC-816**: **Zero** pares de regras com o mesmo seletor, as mesmas declarações e a mesma mídia entre a
  folha comum e os estilos de tela.
- **SC-817**: A resposta HTML da visão geral diminui pelo menos o tamanho do estilo que ela deixou de
  carregar (≈ 12 KB); a da Distribuição, da lista e de Minhas Etapas cresce **no máximo 1 KB** — o
  custo dos `<link>` da divisão —, e a Distribuição continua abaixo do teto.

## Assumptions

- A folha comum é a do `gestao.css` da `089`, com a regra que o PR #307 muda; a implementação começa
  depois do merge dele.
- O inventário visual de 16/10 (`doc/inventario-visual-da-gestao-2026-10-16/`), com as ferramentas de
  captura, comparação, medida, pixels e regras aplicadas da `089`, é a linha de base; "ruído conhecido"
  é o que duas capturas do mesmo código já diferem.
- "Alcançar o mesmo elemento" (D-001) é medido nas páginas do inventário; uma regra cujo elemento só
  existe fora delas — criado por script, ou num fragmento que o inventário não captura — não troca de
  ordem com quem disputa propriedade com ela.
- Sem endereço de relatório: as violações do modo de observação só aparecem no console de quem abre a
  página. Receber relatórios no servidor é um passo possível, e registrado.
- O guia de implantação é recomendação, não configuração versionada.
