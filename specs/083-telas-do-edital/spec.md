# Feature Specification: As telas do Edital, quinto incremento

**Feature Branch**: `claude/telas-do-edital-083-610769`, sobre a `main` em `cf6d7372`, que traz da `075` à
`080`

**Created**: 2026-10-18

**Status**: Implementada — PR aberto, merge com o usuário

**Input**: etapa 4 da sequência do [estudo da entrada na gestão](../../doc/estudo-acesso-a-gestao-2026-10-16.md)
(§7) — a modernização por tela, incremental. Quinto incremento, depois de quem avalia
([`077`](../077-telas-de-uso-diario/spec.md)), de quem elabora ([`078`](../078-telas-de-quem-elabora/spec.md)),
da presidência ([`079`](../079-telas-da-presidencia/spec.md)) e das filhas da Distribuição
([`080`](../080-telas-filhas-da-distribuicao/spec.md)). A `078` modernizou o detalhe do Edital e as nove
etapas da composição; este incremento leva o mesmo desenho às telas que se abrem a partir delas e que
ficaram com o cabeçalho da `076`: Novo Edital, Retificar, o detalhe da Retificação e a conferência de
cada ato dela, a Prévia, Partir de um Edital anterior e a conferência da troca, a Condução do marco e a
conferência do gesto, a Prévia de publicação do resultado, os Resultados divulgados e a Auditoria do
Edital. A linha de base visual é o [inventário de 16/10](../../doc/inventario-visual-da-gestao-2026-10-16.md),
refeito em 18/10/2026 sobre `cf6d7372`, nos dois estados da barra.

> **Faixa de identificadores.** Esta spec abre em FR-1850 e SC-730, faixa reservada para ela em
> 18/10/2026, quando três incrementos da etapa 4 passaram a correr em paralelo.

---

## Por que esta feature existe

**Do detalhe do Edital, um clique adiante, o caminho volta para dentro da página — e encurtado.**
Desde a `078`, o detalhe do Edital diz no cabeçalho *GPS › Processos Seletivos › PS-DEMO-2026 ›
Edital 51/2026*. Ao abrir Retificar, a Prévia, a Condução de um marco ou a Auditoria, o cabeçalho
volta a dizer só *GPS › Processos Seletivos*, e o caminho reaparece numa segunda linha, dentro do
conteúdo, sem o Processo: *Processos Seletivos › Edital 51/2026 › Retificar*. A conferência de um ato
da Retificação começa ainda mais embaixo, pelo Edital, sem "Processos Seletivos". **Medido em
18/10/2026**: das doze telas, só Novo Edital leva ao Processo pela trilha, e uma não leva à lista de
Processos.

**A Auditoria do Edital ficou sozinha.** As três auditorias dividem o modelo de página; a `080` levou a
trilha da avaliação e a da comissão ao cabeçalho e deixou a do Edital com a trilha no conteúdo, como
o próximo grupo natural (decisão 002 da `080`). Ela é este grupo.

**O resultado do último envio aparece depois da explicação.** Em Retificar, as recusas vêm depois do
aviso "Como funciona", um parágrafo de quatro linhas; na Prévia de publicação, a recusa vem depois da
frase "Esta é uma prévia". É a resposta ao clique que trouxe a pessoa de volta, e a `080` a pôs logo
abaixo do título nas telas dela.

**No detalhe da Retificação, o que fazer vem depois do que já se sabe.** O detalhe do Processo e o do
Edital têm "O que fazer agora" antes do resto desde a `078`. O da Retificação tem o mesmo cartão, à
direita do cartão da Vigência — e, a 375 px, embaixo dele.

**Em Partir de um Edital anterior, "Filtrar" tem o desenho de ação de linha.** A marcação do filtro
diz, no comentário, que é a de Inscrições; lá "Filtrar" tem o desenho de ação principal desde a `055`
(`FR-1008`), e "Limpar", o de ação secundária. Aqui ficaram os de antes.

**O que não muda, e não se negocia aqui:** nenhuma regra de negócio, permissão, semântica de papel ou
fluxo. Nenhum endereço, nenhuma view. Nenhum conteúdo normativo. Nenhuma ação que não se desfaz —
confirmar um ato da Retificação, criar a Retificação, substituir o conteúdo do Edital, praticar um
gesto do marco, publicar o resultado — muda de lugar, de rótulo ou de peso. Nenhuma explicação que
precede um ato sai de antes dele. Nenhuma tela fora destas doze.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Onde estou, dito uma vez só, em tudo o que se abre do Edital (Priority: P1)

A elaboradora abre o Edital 01/2026 e vai a Retificar. No topo, o cabeçalho diz *GPS › Processos
Seletivos › PS-DEMO-2026 › Edital 01/2026 › Retificar* — a trilha do Edital, com a tela atual no fim
—, e cada nível acima leva a ele. O conteúdo começa pelo título. O mesmo no detalhe da Retificação e
na conferência de cada ato, na Prévia, em Partir de um Edital anterior e na conferência da troca, na
Condução do marco e na conferência do gesto, na Prévia de publicação, nos Resultados divulgados e na
Auditoria do Edital; e, em Novo Edital, *GPS › Processos Seletivos › PS-DEMO-2026 › Novo Edital*.

**Why this priority**: é o que da `077` à `080` se fez nas outras telas; sem isso, quem elabora lê o
caminho no cabeçalho até o Edital e o perde um clique adiante, sem o Processo.

**Independent Test**: nas doze telas, o caminho está no cabeçalho de contexto, com um link por nível
acima da tela que quem lê alcança e a tela como página atual; o conteúdo não tem trilha; a página tem
uma trilha só.

**Acceptance Scenarios**:

1. **Given** Retificar, o detalhe da Retificação, a Prévia, a Condução do marco ou a Auditoria do
   Edital, **When** a página abre, **Then** o cabeçalho mostra *GPS › Processos Seletivos › código do
   Processo › Edital N/AAAA › nome da tela*, com os três níveis do meio como links, e o conteúdo
   começa pelo título.
2. **Given** a conferência de um ato da Retificação, **When** a página abre, **Then** a trilha termina
   em *Edital N/AAAA › Retificação › nome do ato*, com a Retificação como link.
3. **Given** a conferência da troca de origem, **When** a página abre, **Then** a trilha termina em
   *Edital N/AAAA › Compor › Partir de um Edital anterior › Confirmar* — a trilha da tela de onde ela
   se abre, com ela no fim.
4. **Given** a conferência de um gesto do marco, **When** a página abre, **Then** a trilha termina em
   *Edital N/AAAA › nome do marco › Conferir*, com o marco como link.
5. **Given** a Prévia de publicação ou os Resultados divulgados, aberta por quem não alcança a tela
   da classificação, **When** a página abre, **Then** o nível *Ato de classificação* ou
   *Classificação* continua na trilha, como texto e não como link, como antes.
6. **Given** Novo Edital, **When** a página abre, **Then** a trilha termina em *código do Processo ›
   Novo Edital*.
7. **Given** a Supervisão do Processo, que não é deste grupo, **When** a página abre, **Then** o
   cabeçalho continua o da `076`, e a trilha continua no conteúdo.

---

### User Story 2 — O que acabou de acontecer, logo abaixo do título (Priority: P2)

A elaboradora pede "Ver o que vai mudar" em Retificar, e o envio é recusado. A tela volta com a
recusa logo abaixo do título, antes de "Como funciona". Na Prévia de publicação, a recusa de um envio vem no
mesmo lugar, antes de "Esta é uma prévia".

**Why this priority**: é a ordem que a `079` e a `080` deram às telas delas — título, linha de baixo,
o que acabou de acontecer —, e a resposta ao clique é a primeira coisa que a pessoa procura.

**Independent Test**: em Retificar e na Prévia de publicação, a recusa do último envio vem logo depois
do título e da linha de baixo dele, antes do texto de ajuda, com o mesmo texto, o mesmo papel para o
leitor de tela e o mesmo foco.

**Acceptance Scenarios**:

1. **Given** Retificar com uma recusa, **When** a página abre, **Then** as recusas vêm antes do aviso
   "Como funciona", com o foco nelas.
2. **Given** a Prévia de publicação com uma recusa, **When** a página abre, **Then** a recusa vem
   antes de "Esta é uma prévia: nada foi gravado.", e o que acontece ao confirmar continua antes do
   formulário.
3. **Given** a Condução do marco depois de um gesto, **When** a página abre, **Then** o desfecho
   continua onde estava, depois de "Termos desta tela", que define o termo que ele usa (D-007).

---

### User Story 3 — No detalhe da Retificação, o que fazer primeiro (Priority: P2)

A homologadora abre a Retificação do Edital 01/2026. "O que fazer agora", com os atos que ela pode
praticar, vem antes da Vigência — à esquerda a 1280 px e em cima a 375 px.

**Why this priority**: é a ordem que a `078` deu ao detalhe do Processo e ao do Edital; o detalhe da
Retificação é o terceiro detalhe do mesmo fluxo.

**Independent Test**: a região "O que fazer agora" vem antes da região "Vigência"; os atos, o desenho
de cada um e a marca "irreversível" não mudam.

**Acceptance Scenarios**:

1. **Given** o detalhe de uma Retificação, **When** a página abre, **Then** "O que fazer agora" vem
   antes de "Vigência", e "Alterações declaradas" continua depois das duas.
2. **Given** quem não tem ato disponível, **When** a página abre, **Then** "Nenhum ato disponível
   para seus papéis nesta situação." continua no mesmo cartão, agora o primeiro.

---

### User Story 4 — Em Partir de um Edital anterior, "Filtrar" é a ação do filtro (Priority: P3)

O elaborador procura "2025" entre os Editais que podem servir de origem e aperta "Filtrar" — o botão
com o desenho de ação principal, como nas Inscrições. "Limpar" aparece ao lado, com o desenho de ação
secundária.

**Why this priority**: é a mesma marcação das Inscrições, que o próprio comentário do filtro cita, e o
desenho que a `055` e a `080` deram a "Filtrar"; a tela ficou de fora porque não foi medida.

**Independent Test**: "Filtrar" tem o desenho de ação principal; "Limpar", quando aparece, o de ação
secundária; "Usar como base" e "Substituir pelo escolhido" não mudam.

**Acceptance Scenarios**:

1. **Given** Partir de um Edital anterior, **When** a página abre, **Then** "Filtrar" tem o desenho de
   ação principal.
2. **Given** uma busca feita, **When** a página abre, **Then** "Limpar" tem o desenho de ação
   secundária, e leva à lista sem a busca, como antes.

### Edge Cases

- **Trilha longa no celular.** A da conferência da troca tem sete níveis, e o nome de um marco pode
  ser longo. A 375 px a trilha quebra a linha dentro do cabeçalho; nem ela nem "Trocar identidade"
  estouram a largura.
- **Quem só publica.** A Prévia de publicação e os Resultados divulgados abrem para quem publica e
  não alcança a classificação. O nível da classificação continua nomeado, sem link (E2E17-002); os
  outros níveis — Processo e Edital — são telas que quem publica já abre.
- **Edital sem Processo carregado.** Toda tela do grupo já lê o Edital; a trilha lê o código do
  Processo a partir dele, como o detalhe do Edital e a composição fazem desde a `078`.
- **Retificar só para leitura.** Sem a permissão de elaborar, o aviso "Somente leitura" continua antes
  do conteúdo vigente — ele é o estado da tela, e não a resposta a um envio.
- **Conferência do gesto sem recorte a praticar.** "Não há recorte a praticar neste marco." e "Voltar
  ao marco" continuam; só a trilha sobe.
- **Conferência da troca.** O aviso que enumera o que será apagado continua antes da nova origem e do
  botão "Substituir o conteúdo": é a pergunta antes do ato, e não o resultado de um envio.
- **Prévia impedida.** "Este ato não pode ser divulgado" e o caminho para a classificação, ou a quem
  pedir, continuam no mesmo lugar.
- **Auditoria do Edital sem ato.** O estado vazio continua; só a trilha sobe.
- **O link de salto.** Continua levando ao conteúdo, que agora começa pelo título.
- **Impressão.** A barra e o cabeçalho de contexto não saem no papel (`076`). O título e a linha de
  baixo dele continuam identificando o Edital impresso.

## Requirements *(mandatory)*

### Functional Requirements

#### A trilha no cabeçalho de contexto

- **FR-1850**: Em Novo Edital, Retificar, no detalhe da Retificação, na conferência de um ato da
  Retificação, na Prévia, em Partir de um Edital anterior, na conferência da troca de origem, na
  Condução do marco, na conferência de um gesto do marco, na Prévia de publicação, nos Resultados
  divulgados e na Auditoria do Edital, o cabeçalho de contexto MUST mostrar a trilha da tela, como
  navegação nomeada: o produto, cada nível acima da tela, e a própria tela como a página atual — como
  da `077` à `080` (`FR-1800` da `080`).
- **FR-1851**: Os níveis acima da tela MUST ser Processos Seletivos, o Processo e o Edital — em Novo
  Edital, Processos Seletivos e o Processo —, seguidos dos níveis que a tela já mostrava entre o Edital
  e ela, na mesma ordem; o rótulo da tela MUST ser o que ela já mostrava como página atual. Na
  conferência da troca de origem, os níveis entre o Edital e ela MUST ser os da tela de onde ela se
  abre: Compor e Partir de um Edital anterior.
- **FR-1852**: Nessas doze telas a trilha MUST NOT aparecer de novo no conteúdo: a página MUST ter uma
  trilha só, e o conteúdo MUST começar pelo título.
- **FR-1853**: As demais telas da gestão — fora das que da `077` à `080` e esta nomeiam — MUST
  continuar com o cabeçalho de contexto da `076` e a trilha no conteúdo (`FR-1803` da `080`).
- **FR-1854**: Todo nível MUST ser link para quem o lê, exceto os que já eram condicionais: o Ato de
  classificação, na Prévia de publicação, e a Classificação, nos Resultados divulgados, MUST continuar
  nomeados como texto, sem link, para quem não alcança a tela da classificação. Nenhum nível MUST
  aparecer ou sumir conforme quem lê.
- **FR-1855**: A 375 px, a trilha do cabeçalho MUST quebrar a linha dentro da largura, e "Trocar
  identidade" MUST continuar alcançável.

#### O que acabou de acontecer

- **FR-1856**: Em Retificar e na Prévia de publicação, a recusa do último envio MUST vir logo depois
  do título e da linha de baixo dele, antes do texto de ajuda, com o mesmo texto, o mesmo papel para o
  leitor de tela e o mesmo foco. O que acontece ao confirmar, na Prévia de publicação, MUST continuar
  antes do formulário. Na Condução do marco, o erro e o desfecho do gesto MUST continuar depois de
  "Termos desta tela" (D-007).

#### A ação que o fluxo pede, antes do resto

- **FR-1857**: No detalhe da Retificação, a região "O que fazer agora" MUST vir antes da região
  "Vigência"; os atos, o desenho de cada um e a marca "irreversível" MUST continuar os mesmos.

#### A hierarquia das ações

- **FR-1858**: Em Partir de um Edital anterior, "Filtrar" MUST ter o desenho de ação principal e
  "Limpar", o de ação secundária, como nas Inscrições (`FR-1008` da `055`).
- **FR-1859**: As ações que não se desfazem — "Confirmar" na conferência de um ato da Retificação,
  "Criar Retificação", "Substituir o conteúdo", o gesto confirmado na conferência do marco e "Publicar
  este resultado" — MUST continuar com o rótulo, o desenho, o lugar e as frases que as precedem.

#### O que não pode piorar

- **FR-1860**: Nenhuma variante do inventário visual MUST deixar de carregar, mudar de `status` ou
  passar a estourar a 375 ou a 1280 px, com a barra expandida e com ela recolhida; e só as telas desta
  feature MUST mudar de largura ou de altura.
- **FR-1861**: As telas tocadas MUST passar pelos guardiões de acessibilidade, larguras, vocabulário e
  folha que já varrem a gestão — o link de salto, o `main`, toda classe com regra na folha, todo botão
  de envio com classe.

### Key Entities

Nenhuma. Só apresentação.

## Decisões

### D-001 — Os níveis de cada tela, com o Processo no meio

As doze telas mostravam o caminho a partir do Edital, sem o Processo, e cada uma com os seus níveis
intermediários — a Retificação, Compor, o marco, a classificação. Esses níveis dizem de onde a tela
se abre, e ficam; o que se acrescenta é o que o detalhe do Edital já tem no cabeçalho desde a `078`:
Processos Seletivos e o Processo. A exceção é a conferência da troca, que saltava Compor: a trilha
de uma conferência é a da tela de onde ela se abre, com ela no fim (decisão 001 da `080`).

### D-002 — A Auditoria do Edital entra, e o guardião das demais telas vai à Supervisão

A `080` deixou a Auditoria do Edital com a trilha no conteúdo por ser tela de quem audita o Edital, e
a registrou como o próximo grupo (decisão 002 da `080`). Ela se abre do detalhe do Edital, como as outras
onze, e com ela o modelo de página das três auditorias passa a ter a trilha no cabeçalho em todos os
ramos. Os dois guardiões que provavam "as demais telas continuam com a `076`" sobre ela passam à
Supervisão do Processo, que nenhum incremento nomeou.

### D-003 — Nomear não é abrir

Na Prévia de publicação e nos Resultados divulgados, o nível da classificação era link só para quem
alcança aquela tela; para quem só publica, era texto, porque o link levava a 404 (E2E17-002). A
trilha sobe com a mesma condição. Ela não concede nem esconde acesso: o nível continua dizendo onde a
tela fica.

### D-004 — A Prévia de publicação e os Resultados divulgados ficam neste grupo

São telas do resultado de um marco, e a classificação, de onde se abrem, não é deste incremento. Ficam
porque moram no Edital — o endereço e a trilha passam por ele — e porque a Condução do marco, que é
deste grupo, leva a elas. A classificação e o ato dela continuam com o desenho deles.

### D-005 — "Filtrar" em Partir de um Edital anterior

O filtro desta tela é, pelo próprio comentário, a marcação de Inscrições, onde "Filtrar" tem o desenho
de ação principal e "Limpar" o de ação secundária desde a `055` (`FR-1008`). Aplicar a mesma regra
estende a decisão, como a decisão 004 da `080`, e não a reabre. "Usar como base" e "Substituir pelo
escolhido" continuam com o desenho de ação principal: a página tem duas regiões, cada uma com a sua
ação.

### D-006 — O que não muda, por governança

- **Nenhuma ação que não se desfaz ganha ou perde peso.** "Confirmar", "Substituir o conteúdo", o
  gesto confirmado e "Publicar este resultado" continuam com o desenho de perigo onde o tinham; "Criar
  Retificação" com o de ação principal.
- **A explicação do ato continua antes do ato.** As consequências da conferência de um ato, o que se
  perde na troca de origem, o alcance recorte a recorte do gesto e o que acontece ao publicar
  continuam antes dos botões; só a resposta a um envio já feito sobe.
- **A Prévia não muda de ações.** O botão de voltar continua com o desenho de ação principal: é a
  única ação da tela além de abrir o arquivo, e leva de volta a quem estava compondo ou retificando.
- **A Condução do marco não muda de ações.** O primeiro gesto continua o cheio, e os demais
  secundários (`FR-1048` da `057`).

### D-007 — Na Condução do marco, o desfecho fica depois dos termos

A resposta ao gesto poderia subir para logo abaixo do título, como em Retificar. Não sobe: o desfecho
diz "Abrir este recorte", e "Termos desta tela", recolhido logo abaixo do título, é onde *recorte* se
define. Subir o desfecho poria o primeiro uso do termo antes da definição (`FR-424` da `030`), e
tiraria o bloco do lugar que a `057` fixou para ele (`FR-1051`). O bloco é uma linha quando recolhido:
a resposta continua à vista, logo abaixo dele.

## Success Criteria *(mandatory)*

- **SC-730**: Refeito o inventário visual, **zero** variantes estouram a 375 ou a 1280 px, e
  **nenhuma** muda de `status`, nos dois estados da barra.
- **SC-731**: Fora das telas desta feature, **nenhuma** variante do inventário muda de largura ou de
  altura.
- **SC-732**: Nas doze telas, "onde estou" aparece **uma** vez por página, no cabeçalho de contexto, e
  cada nível acima da tela que quem lê alcança está a **um** clique.
- **SC-733**: Das doze telas, as que levam ao Processo pela trilha passam de **uma** para **doze**, e
  as que levam à lista de Processos, de **onze** para **doze**.
- **SC-734**: A suíte contra PostgreSQL continua sem falhas.
- **SC-735**: O percurso — do detalhe do Edital a cada tela do grupo e de volta pela trilha — é feito
  só pelo teclado, com foco visível, a 1280 e a 375 px.

## Assumptions

- "As telas do Edital que a `078` não cobriu" são as doze do pedido: as que se abrem do detalhe do
  Edital, da composição ou da Condução do marco e moram sob o Edital ou a Retificação dele. Avisos do
  Edital, Dúvidas e o assistente também se abrem do Edital, e ficam de fora porque o pedido não os
  nomeia.
- A conferência da troca de origem e a do gesto do marco não estão no inventário visual: são a
  resposta a um envio, e o inventário só abre telas pelo endereço. São provadas pelos testes e no
  navegador, como as conferências da `079` e da `080`.
- O produto no começo da trilha é a sigla GPS, como da `076` à `080`.
- A tela mais estreita que se considera é a de 375 px, a mesma do inventário.
- A validação com a equipe, recomendada desde a `075`, continua pendente; este incremento não a
  substitui.
