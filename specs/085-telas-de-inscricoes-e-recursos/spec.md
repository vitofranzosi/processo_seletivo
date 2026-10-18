# Feature Specification: As telas de inscrições e de recursos, sétimo incremento

**Feature Branch**: `claude/telas-de-inscricoes-085-f7ccd0`, sobre a `main` em `cf6d7372`, que traz da
`075` à `080`

**Created**: 2026-10-18

**Status**: Implementada — PR aberto, merge com o usuário

**Input**: etapa 4 da sequência do [estudo da entrada na gestão](../../doc/estudo-acesso-a-gestao-2026-10-16.md)
(§7) — a modernização por tela, incremental. Depois de quem avalia
([`077`](../077-telas-de-uso-diario/spec.md)), de quem elabora
([`078`](../078-telas-de-quem-elabora/spec.md)), da presidência
([`079`](../079-telas-da-presidencia/spec.md)) e das filhas da Distribuição
([`080`](../080-telas-filhas-da-distribuicao/spec.md)), as telas que se abrem do Edital para o que
chegou dos candidatos: as Inscrições do Edital, a Inscrição recebida, os Recursos recebidos e o
Recurso. Corre em paralelo com a `083` e a `084`, cada uma em worktree própria e com a sua faixa de
identificadores. A linha de base visual é o [inventário de 16/10](../../doc/inventario-visual-da-gestao-2026-10-16.md),
refeito em 18/10/2026 sobre `cf6d7372`, nos dois estados da barra.

> **Faixa de identificadores.** Esta spec usa FR-1910 em diante e SC-750 em diante, faixa reservada
> de antemão para ela pela sessão que coordena o paralelo — a `083` e a `084` têm as suas. Não há
> guardião de contiguidade: os dois que leem a numeração (`tests/test_citacoes_de_requisito.py`)
> cobram que a citação exista e que a matriz a cubra.

---

## Por que esta feature existe

**Do Edital às inscrições, o cabeçalho esquece onde a pessoa está.** Desde a `078`, o detalhe do Edital
diz no cabeçalho *GPS › Processos Seletivos › PS-DEMO-2026 › Edital 51/2026*. Ao abrir "Inscrições
recebidas" ou "Recursos", o cabeçalho volta a dizer só *GPS › Processos Seletivos*, e o caminho
reaparece dentro do conteúdo, numa segunda linha — e sem o Processo: *Processos Seletivos › Edital
51/2026 › Inscrições*. **Medido em 18/10/2026**: das quatro telas, nenhuma leva ao Processo pela
trilha, e todas dizem "onde estou" duas vezes, uma no cabeçalho e outra no conteúdo.

**Quem confere uma inscrição e quem julga um recurso descem um nível a mais, e a trilha cresce no
lugar errado.** A Inscrição recebida e o Recurso estão um nível abaixo da lista; a trilha do conteúdo
tem quatro níveis, e é ela, e não o título, a primeira coisa do conteúdo.

**Sem nenhuma inscrição recebida, a lista avisa como se houvesse problema.** A frase "Nenhuma
inscrição recebida até agora." sai com o desenho de aviso, o amarelo das advertências; com um filtro
sem resultado, a mesma lista usa o estado vazio comum, e a lista de Recursos, sem recurso, também. É o
estado normal de um Edital antes de as inscrições abrirem, e o desenho dizia outra coisa.

**O que não muda, e não se negocia aqui:** nenhuma regra de negócio, permissão, semântica de papel ou
fluxo. Nenhum endereço, nenhuma view. Nenhum dado pessoal novo: a trilha nomeia a inscrição e o
recurso pelo protocolo que a página já mostrava, e nenhum caminho condicionado à autorização deixa de
sê-lo. Nenhuma ação — admitir, não admitir, instruir, julgar — muda de lugar, de rótulo ou de peso.
Nenhuma tela fora destas quatro.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Onde estou, dito uma vez só, do Edital ao que chegou (Priority: P1)

O gestor abre o Edital 51/2026 e vai a "Inscrições recebidas". No topo, o cabeçalho diz *GPS ›
Processos Seletivos › PS-DEMO-2026 › Edital 51/2026 › Inscrições* — a trilha do Edital, com a tela no
fim —, e cada nível acima leva a ele. O conteúdo começa pelo título. Abrindo a inscrição de Ana Silva,
o cabeçalho acrescenta *› Inscrições › INS-2026-0001*. Do mesmo modo, a julgadora abre "Recursos" e
um recurso, e lê *… › Edital 51/2026 › Recursos › REC-2026-…*.

**Why this priority**: é o que a `077` à `080` fizeram nas outras telas de uso diário; sem isso, o
caminho do Edital é dito no cabeçalho até o Edital e perdido um clique adiante.

**Independent Test**: nas quatro telas, o caminho está no cabeçalho de contexto, com um link por nível
acima da tela e a tela como página atual; o conteúdo não tem trilha; a página tem uma trilha só.

**Acceptance Scenarios**:

1. **Given** as Inscrições de um Edital, **When** a página abre, **Then** o cabeçalho mostra *GPS ›
   Processos Seletivos › código do Processo › Edital NN/AAAA › Inscrições*, com os três níveis do meio
   como links, e o conteúdo começa pelo título.
2. **Given** uma Inscrição recebida, **When** a página abre, **Then** o cabeçalho mostra a trilha das
   Inscrições, com "Inscrições" como link e o protocolo como página atual.
3. **Given** uma inscrição ainda em preenchimento, sem protocolo, **When** a página abre, **Then** a
   página atual da trilha diz "Em preenchimento", como já dizia.
4. **Given** os Recursos de um Edital, **When** a página abre, **Then** o cabeçalho mostra *… › Edital
   NN/AAAA › Recursos*; **and given** um Recurso, *… › Recursos › protocolo do recurso*.
5. **Given** a tela de recusa e as demais telas da gestão fora da `077` à `080` e destas, **When** a
   página abre, **Then** o cabeçalho continua o da `076`.

---

### User Story 2 — Sem inscrição, o estado vazio, e não um aviso (Priority: P2)

O gestor abre as Inscrições de um Edital que ainda não recebeu nenhuma. A frase "Nenhuma inscrição
recebida até agora." aparece no estado vazio comum — o mesmo da lista filtrada sem resultado e da
lista de Recursos sem recurso —, e não no desenho de aviso.

**Why this priority**: o aviso é o desenho do que pede atenção; usá-lo para o estado normal gasta o
sinal. É a correção que a `078` fez nos Editais do Processo (`FR-1772` da `078`).

**Independent Test**: sem inscrição recebida, a frase sai no estado vazio comum, com o mesmo texto; o
aviso dos rascunhos em preenchimento continua aviso.

**Acceptance Scenarios**:

1. **Given** um Edital sem inscrição recebida, **When** as Inscrições abrem, **Then** "Nenhuma
   inscrição recebida até agora." está no estado vazio comum.
2. **Given** um Edital com rascunhos em preenchimento, **When** as Inscrições abrem, **Then** a
   advertência de que rascunho não é inscrição recebida continua com o desenho de aviso.

---

### User Story 3 — Os rascunhos como região nomeada (Priority: P3)

Quem navega pelo leitor de tela abre as Inscrições e lista as regiões da página: além da busca, há a
região "Em preenchimento — N", com a advertência e a tabela dos rascunhos — como a Comissão ganhou na
`079` a região "Membros".

**Why this priority**: não muda nada do que se vê; muda o que se alcança por região. É a parte menor do
incremento.

**Independent Test**: quando há rascunho, a seção dos rascunhos é uma região nomeada pelo título dela.

**Acceptance Scenarios**:

1. **Given** um Edital com rascunhos em preenchimento, **When** as Inscrições abrem, **Then** o título
   "Em preenchimento — N", a advertência e a tabela estão numa região nomeada por esse título.

### Edge Cases

- **Trilha longa no celular.** A da Inscrição recebida e a do Recurso têm seis níveis, e o código do
  Processo e o protocolo são longos. A 375 px a trilha quebra a linha dentro do cabeçalho; nem ela nem
  "Trocar identidade" estouram a largura.
- **Quem julga sem consultar inscrições.** A julgadora abre o Recurso e lê na trilha o Processo, o
  Edital e os Recursos. As três portas são as que ela já abre: o Processo e o Edital pedem só o escopo
  da unidade, e os Recursos pedem a mesma permissão do Recurso. Os caminhos do bloco "Conferir o que se
  contesta" continuam condicionados como antes (FR-1914).
- **Quem consulta inscrições.** A trilha da Inscrição recebida leva às Inscrições, que pedem a mesma
  permissão da Inscrição recebida.
- **O protocolo da inscrição na trilha.** É o que a página já mostrava na linha abaixo do título e na
  trilha do conteúdo. O nome, o CPF e o e-mail não entram na trilha.
- **Recurso com impedimento.** "Você não pode julgar este recurso." continua antes de qualquer botão,
  logo depois do título e do erro, se houver.
- **Recurso com erro do último envio.** O erro continua logo abaixo do título, com o mesmo papel para o
  leitor de tela.
- **Inscrições filtradas sem resultado.** "Nenhuma inscrição recebida corresponde a este filtro."
  continua no estado vazio, como antes.
- **O link de salto.** Continua levando ao conteúdo, que agora começa pelo título.
- **Impressão.** A barra e o cabeçalho de contexto não saem no papel (`076`). O título e a linha de
  baixo dele continuam identificando a inscrição e o recurso impressos; o Edital impresso fica no
  título das Inscrições e no bloco "Conferir o que se contesta" do Recurso, e sai do papel da
  Inscrição recebida e dos Recursos, como já saiu das telas da `077` à `080` (D-004).
  *Substituído pela [`088`](../088-decisoes-da-etapa-4/spec.md) em 18/10/2026, por decisão do
  usuário*: a trilha do cabeçalho de contexto sai no papel; ficam fora só a barra e "Trocar
  identidade".

## Requirements *(mandatory)*

### Functional Requirements

#### A trilha no cabeçalho de contexto

- **FR-1910**: Nas Inscrições do Edital, na Inscrição recebida, nos Recursos recebidos e no Recurso, o
  cabeçalho de contexto MUST mostrar a trilha da tela, como navegação nomeada: o produto, cada nível
  acima da tela como link, e a própria tela como a página atual — como nas telas da `077` à `080`
  (`FR-1800` da `080`).
- **FR-1911**: Os níveis acima da tela MUST ser os da trilha do Edital — Processos Seletivos, o
  Processo e o Edital (`FR-1767` e `FR-1768` da `078`) —, mais "Inscrições" na Inscrição recebida e "Recursos" no
  Recurso. O rótulo da página atual MUST ser o que a tela já mostrava: "Inscrições", "Recursos", o
  protocolo da inscrição — ou "Em preenchimento", sem protocolo — e o protocolo do recurso.
- **FR-1912**: Nessas quatro telas a trilha MUST NOT aparecer de novo no conteúdo: a página MUST ter
  uma trilha só, e o conteúdo MUST começar pelo título.
- **FR-1913**: A trilha MUST ser a mesma para todo leitor da tela, e cada nível MUST levar a uma tela
  cuja porta já é a da tela de origem ou mais larga que ela: nenhum nível MUST aparecer, sumir ou
  deixar de ser link conforme quem lê.
- **FR-1914**: A trilha MUST NOT trazer dado pessoal que a tela não mostrava: a inscrição e o recurso
  são nomeados pelo protocolo. Os caminhos do Recurso condicionados à autorização — os documentos da
  inscrição, o resultado atacado e a avaliação que o produziu — MUST continuar oferecidos só a quem a
  tela de destino deixaria entrar.
- **FR-1915**: A tela de recusa e as demais telas da gestão fora da `077` à `080` e destas MUST
  continuar com o cabeçalho de contexto da `076` (`FR-1803` da `080`).
- **FR-1916**: A 375 px, a trilha do cabeçalho MUST quebrar a linha dentro da largura, e "Trocar
  identidade" MUST continuar alcançável.
- **FR-1917**: Levar o Processo à trilha MUST NOT custar consulta a mais ao banco em nenhuma das quatro
  telas: o Processo MUST vir na mesma leitura do Edital.

#### Os estados e as regiões das Inscrições

- **FR-1918**: Nas Inscrições, sem inscrição recebida e sem filtro, "Nenhuma inscrição recebida até
  agora." MUST sair no estado vazio comum, com o mesmo texto; a advertência dos rascunhos em
  preenchimento MUST continuar com o desenho de aviso.
- **FR-1919**: Nas Inscrições, quando houver rascunho em preenchimento, o título "Em preenchimento —
  N", a advertência, a tabela e a paginação deles MUST estar numa região nomeada por esse título.

#### O que não pode piorar

- **FR-1920**: As ações do Recurso — "Admitir", "Não admitir", "Instruir o recurso" e "Registrar a
  decisão" — e o "Filtrar" das Inscrições e dos Recursos MUST continuar com o rótulo, o desenho e o
  lugar de antes; o impedimento MUST continuar antes de qualquer botão.
- **FR-1921**: Nenhuma variante do inventário visual MUST deixar de carregar, mudar de `status` ou
  passar a estourar a 375 ou a 1280 px, com a barra expandida e com ela recolhida; e só as telas desta
  feature MUST mudar de largura ou de altura.
- **FR-1922**: As telas tocadas MUST passar pelos guardiões de acessibilidade, larguras, vocabulário e
  folha que já varrem a gestão — o link de salto, o `main`, toda classe com regra na folha, todo botão
  de envio com classe.

### Key Entities

Nenhuma. Só apresentação.

## Decisões

### D-001 — A trilha é a do Edital, mais a tela

As quatro telas se abrem do detalhe do Edital, e a trilha dele, desde a `078`, passa pelo Processo. A
trilha de cada uma é a do Edital com ela no fim — o mesmo que a `080` fez com as filhas da
Distribuição (a decisão 001 da `080`). O que muda em relação à trilha do conteúdo é o Processo entre a
seção e o Edital; os rótulos da página atual são os que cada tela já usava.

### D-002 — A tela de recusa fica fora

O pedido a nomeia junto das outras quatro, mas ela não é tela de inscrições nem de recursos: é a
resposta de toda a gestão a uma operação recusada — 403, 404 e envio acima do limite —, desenhada por
`interface/erros.py` para qualquer endereço sob `/gestao/`, sem Edital, Processo nem inscrição no
contexto. Não há trilha que ela possa mostrar sem saber de onde a pessoa veio, e mudar o desenho dela
mudaria a recusa de todas as 59 telas. Fica com o cabeçalho da `076`, e registrada na pesquisa como
peça do shell, e não de um grupo de telas.

### D-003 — O Processo na mesma leitura

As Inscrições e a Inscrição recebida leem o Edital por funções de consulta da aplicação de inscrições
que não traziam o Processo; a trilha, lendo-o no template, custaria uma consulta a mais por página.
A leitura delas passa a trazer o Processo junto do Edital — a mesma junção que a leitura do Edital da
gestão (`obter_edital`) e a do Recurso já fazem. Não muda o que se lê nem quem lê: muda quantas idas ao
banco a página faz, para menos do que custaria sem isso. Os Recursos e o Recurso já o traziam.

### D-004 — O que não muda, por governança

- **Nenhum dado pessoal novo.** A trilha nomeia pelo protocolo. Nenhuma região que dependia de
  permissão deixa de depender: o bloco "Conferir o que se contesta" do Recurso, o Requerimento de
  Matrícula e os documentos da Inscrição recebida continuam saindo das mesmas variáveis da view.
- **Nenhuma ação muda de peso.** "Admitir" e "Registrar a decisão" continuam com o desenho de ação
  principal, "Não admitir" com o de secundária; "Filtrar" continua com o de ação principal nas
  Inscrições e nos Recursos (`FR-1008` da `055`).
- **A impressão perde o Edital em duas telas.** A trilha do conteúdo era a única menção ao Edital na
  Inscrição recebida e nos Recursos, e o cabeçalho de contexto não sai no papel. É a mesma troca que a
  `077` à `080` fizeram; o caso da impressão é a pergunta que a `081` registrou para o produto, e esta
  feature não a responde por conta própria.
- **O Recurso não ganha regiões.** As seções dele são títulos soltos, e embrulhá-las em regiões
  mudaria a página inteira para um ganho que o pedido não nomeia.

## Success Criteria *(mandatory)*

- **SC-750**: Refeito o inventário visual, **zero** variantes estouram a 375 ou a 1280 px, e
  **nenhuma** muda de `status`, nos dois estados da barra.
- **SC-751**: Fora das Inscrições, da Inscrição recebida, dos Recursos e do Recurso, **nenhuma**
  variante muda de largura ou de altura.
- **SC-752**: Nas quatro telas, "onde estou" aparece **uma** vez por página, no cabeçalho de contexto,
  e cada nível acima da tela está a **um** clique.
- **SC-753**: Das quatro telas, as que levam ao Processo pela trilha passam de **zero** para
  **quatro**.
- **SC-754**: Nas quatro telas, o número de idas ao banco para desenhar a página **não** cresce.
- **SC-755**: A suíte contra PostgreSQL continua sem falhas.
- **SC-756**: O percurso — do Edital às Inscrições, a uma inscrição e de volta pela trilha; do Edital
  aos Recursos, a um recurso e de volta — é feito só pelo teclado, com foco visível, a 1280 e a
  375 px.

## Assumptions

- "Telas de inscrições e recursos" são as quatro que o detalhe do Edital abre para o que chegou dos
  candidatos e a tela de cada item. A Mesa da inscrição, de quem avalia, é da `077`.
- O inventário visual tem as quatro telas — inscrições, a inscrição recebida de Ana Silva, a lista de
  recursos e dois recursos, um pendente e um admitido —, e nenhuma delas tem lista vazia: o estado
  vazio das Inscrições (FR-1918) é provado pelos testes, e não pelo inventário.
- O produto no começo da trilha é a sigla GPS, como da `076` à `080`.
- A tela mais estreita que se considera é a de 375 px, a mesma do inventário.
- A validação com a equipe, recomendada desde a `075`, continua pendente; este incremento não a
  substitui.
