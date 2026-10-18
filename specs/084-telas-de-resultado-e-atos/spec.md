# Feature Specification: As telas de resultado e dos atos depois da inscrição, incremento paralelo

**Feature Branch**: `claude/telas-de-resultado-084-48dfa6`, sobre a `main` em `cf6d7372`, que traz da
`075` à `080`

**Created**: 2026-10-18

**Status**: Implementada — PR aberto, merge com o usuário

**Input**: etapa 4 da sequência do [estudo da entrada na gestão](../../doc/estudo-acesso-a-gestao-2026-10-16.md)
(§7) — a modernização por tela, incremental. Depois de quem avalia
([`077`](../077-telas-de-uso-diario/spec.md)), de quem elabora
([`078`](../078-telas-de-quem-elabora/spec.md)), da presidência
([`079`](../079-telas-da-presidencia/spec.md)) e das filhas da Distribuição
([`080`](../080-telas-filhas-da-distribuicao/spec.md)), as telas em que o certame produz resultado e
os atos que vêm depois da inscrição: Classificação, a conferência da emissão, o Ato de classificação,
Sorteio, Corte, o corte histórico, Ocupação de vagas e o histórico dela, Convocação e o histórico
dela, e Exportar para matrícula. A linha de base visual é o
[inventário de 16/10](../../doc/inventario-visual-da-gestao-2026-10-16.md), refeito em 18/10/2026
sobre `cf6d7372`, nos dois estados da barra.

> **Faixa de identificadores.** FR-1880 a FR-1889 e SC-740 a SC-745, no começo das faixas reservadas
> a esta spec em 18/10/2026 — trinta requisitos e dez critérios a partir desses —, enquanto a `083` e
> a `085` correm em paralelo com faixas próprias.

---

## Por que esta feature existe

**No Edital, a gestão lê "onde estou" no cabeçalho; um clique adiante, no conteúdo.** Desde a `078`, o
detalhe do Edital diz no cabeçalho *GPS › Processos Seletivos › PS-DEMO-2026 › Edital 51/2026*. Ao
abrir a Classificação, o Corte, a Ocupação, a Convocação ou o Sorteio de um marco — destinos que o
próprio Edital oferece —, o cabeçalho volta a dizer só *GPS › Processos Seletivos*, e o caminho
reaparece dentro do conteúdo, numa segunda linha, sem o Processo. **Medido em 18/10/2026**: das onze
telas, nenhuma leva ao Processo pela trilha, e uma — o Ato de classificação — nem ao Edital: a trilha
dele salta de "Processos Seletivos" para "Classificação".

**São as telas dos atos que não se desfazem.** Emitir a ordem, realizar o sorteio, emitir o corte,
apurar a ocupação, convocar e registrar o desfecho são atos imutáveis e, quase todos, publicados. É
nelas que a pessoa mais precisa saber em que Processo e em que Edital está antes de agir — e é nelas
que o caminho tem menos níveis.

**O que não muda, e não se negocia aqui:** nenhuma regra de negócio, permissão, semântica de papel —
presidir é vínculo com a comissão, e não papel — ou fluxo. Nenhum endereço, nenhuma view. Nenhum
texto normativo nem do vocabulário canônico: os termos definidos no primeiro uso (`FR-424` da `030`)
continuam onde estão. Nenhuma ação que não se desfaz muda de lugar, de rótulo ou de peso. Nenhuma
tela fora destas onze.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Onde estou, dito uma vez só, nos atos do resultado (Priority: P1)

O presidente abre o detalhe do Edital 51/2026 e vai à Convocação do marco final. No topo, o cabeçalho
diz *GPS › Processos Seletivos › PS-DEMO-2026 › Edital 51/2026 › Convocação* — a trilha do Edital, com
a tela no fim —, e cada nível acima leva a ele. O conteúdo começa pelo título. O mesmo na
Classificação, no Sorteio, no Corte, na Ocupação e em Exportar para matrícula; nos históricos, o nível
da tela de origem fica entre o Edital e o histórico (*… › Edital 51/2026 › Ocupação de vagas ›
Histórico*); e, no Ato de classificação, *… › Edital 51/2026 › Classificação › Ato …*.

**Why this priority**: é o que a `077` à `080` fizeram nas outras telas; sem isso, o fluxo do resultado
diz o caminho no cabeçalho até o Edital e o perde um clique adiante.

**Independent Test**: nas onze telas, o caminho está no cabeçalho de contexto, com um link por nível
acima da tela e a tela como página atual; o conteúdo não tem trilha; a página tem uma trilha só.

**Acceptance Scenarios**:

1. **Given** a Classificação, o Sorteio, o Corte, a Ocupação, a Convocação ou Exportar para
   matrícula de um Edital, **When** a página abre, **Then** o cabeçalho mostra *GPS › Processos
   Seletivos › código do Processo › Edital N/AAAA › nome da tela*, com os três níveis do meio como
   links, e o conteúdo começa pelo título.
2. **Given** o histórico da Ocupação ou da Convocação de um recorte, **When** a página abre, **Then** a
   trilha passa pela tela de origem — e, na Convocação, volta ao mesmo recorte — antes de "Histórico".
3. **Given** a conferência da emissão de uma ordem, **When** a página abre, **Then** a trilha termina
   em *nome do marco › Conferir*, e o marco leva de volta ao recorte que se está conferindo.
4. **Given** o Ato de classificação, **When** a página abre, **Then** a trilha passa pelo Processo e
   pelo Edital antes de *Classificação › Ato …*.
5. **Given** o corte histórico, **When** a página abre, **Then** a trilha termina em *Corte de
   data e hora*, abaixo do Edital, como antes.
6. **Given** quem audita, e não preside, ou quem só exporta, **When** abre uma destas telas, **Then**
   a trilha é a mesma que a presidência lê.

---

### User Story 2 — O ato continua com o peso que tinha (Priority: P1)

A presidente abre a conferência da emissão. "Emitir a ordem" continua com o desenho de perigo, no
mesmo lugar, depois das mesmas frases; "Cancelar e voltar" continua ao lado. No Sorteio, "Realizar o
sorteio", "Publicar e congelar a relação" e "Anular e constituir o sucessor" continuam como estavam. Só
o cabeçalho mudou.

**Why this priority**: são atos imutáveis e publicados; um incremento de apresentação que mexesse no
peso deles estaria decidindo governança.

**Independent Test**: o rótulo, o desenho e a posição de cada botão de envio das onze telas são os
mesmos antes e depois.

**Acceptance Scenarios**:

1. **Given** qualquer das onze telas, **When** a página abre, **Then** cada botão de envio tem o mesmo
   rótulo, o mesmo desenho e a mesma ordem de antes.
2. **Given** uma tela com o resultado de um envio, **When** a página abre, **Then** a mensagem vem no
   mesmo lugar — logo depois do título, do contexto e dos termos da tela —, com o mesmo texto, o
   mesmo papel para o leitor de tela e o mesmo foco.

### Edge Cases

- **Trilha longa no celular.** O nome do marco e o do recorte podem ser longos, e o Ato de
  classificação se identifica pelo identificador do ato. A 375 px a trilha quebra a linha dentro do
  cabeçalho; nem ela nem "Trocar identidade" estouram a largura.
- **Ato de um marco que a Retificação removeu.** O Ato continua legível pela versão que congelou; a
  trilha leva à Classificação do marco como antes, e a porta daquela tela continua a dela.
- **Marco de sorteio.** A Classificação de um marco de sorteio redireciona ao Sorteio; a trilha que se
  lê é a do Sorteio.
- **Recorte reservado.** A navegação entre os recortes continua no conteúdo, abaixo dos termos da
  tela: é a escolha do recorte, e não o caminho até a tela.
- **Quem audita sem presidir, ou quem só exporta.** A trilha é a mesma: o Processo e o Edital abrem
  para quem alcança o Edital, e a porta de cada destino continua a dela — a trilha não concede nem
  esconde acesso.
- **Sem população a exportar.** O estado vazio de Exportar para matrícula continua; só a trilha sobe.
- **Impressão.** A barra e o cabeçalho de contexto não saem no papel (`076`), e a trilha sai com eles.
  Na conferência da emissão e no Ato, a linha abaixo do título nomeia o Edital; nas outras nove, o
  título e a linha de baixo nomeiam o marco, o Perfil ou a tela, e a folha impressa deixa de dizer de
  que Edital ela é (D-005).
- **O link de salto.** Continua levando ao conteúdo, que agora começa pelo título.

## Requirements *(mandatory)*

### Functional Requirements

#### A trilha no cabeçalho de contexto

- **FR-1880**: Na Classificação, na conferência da emissão, no Ato de classificação, no Sorteio, no
  Corte, no corte histórico, na Ocupação de vagas e no histórico dela, na Convocação e no histórico
  dela e em Exportar para matrícula, o cabeçalho de contexto MUST mostrar a trilha da tela, como
  navegação nomeada: o produto, cada nível acima da tela como link, e a própria tela como a página
  atual — como nas telas da `077` à `080` (`FR-1800` da `080`).
- **FR-1881**: Os níveis acima da tela MUST começar pelos da trilha do Edital — Processos Seletivos, o
  Processo e o Edital — e seguir pelos que a tela já mostrava entre o Edital e ela; o rótulo da tela
  MUST ser o que ela já mostrava como página atual. Os links que a tela já tinha MUST levar ao mesmo
  destino, inclusive ao mesmo recorte.
- **FR-1882**: Nessas onze telas a trilha MUST NOT aparecer de novo no conteúdo: a página MUST ter uma
  trilha só, e o conteúdo MUST começar pelo título.
  *Emenda a `FR-1803` da `080`*: "as demais telas", que continuam com o cabeçalho da `076`, deixam de
  incluir estas onze. A anotação fica só aqui, e não na spec da `080`, porque a `083`, em paralelo,
  emenda a mesma linha.
- **FR-1883**: A trilha MUST ser a mesma para quem preside, para quem audita e para quem exporta:
  nenhum nível MUST aparecer, sumir ou deixar de ser link conforme quem lê.
- **FR-1884**: A 375 px, a trilha do cabeçalho MUST quebrar a linha dentro da largura, e "Trocar
  identidade" MUST continuar alcançável.

#### O que não muda

- **FR-1885**: As mensagens do último envio, os avisos de estado, os termos da tela e a navegação
  entre recortes MUST continuar no mesmo lugar e com o mesmo texto, o mesmo papel para o leitor de
  tela e o mesmo foco.
- **FR-1886**: Nenhum botão de envio das onze telas MUST mudar de rótulo, de desenho ou de lugar; em
  particular, nenhuma ação que não se desfaz MUST ganhar o desenho de ação principal, e as que têm o
  desenho de perigo MUST mantê-lo.
- **FR-1887**: Nenhum texto do conteúdo MUST mudar: o diff de cada tela MUST ser só a trilha que sai
  do conteúdo e entra no cabeçalho.

#### O que não pode piorar

- **FR-1888**: Nenhuma variante do inventário visual MUST deixar de carregar, mudar de `status` ou
  passar a estourar a 375 ou a 1280 px, com a barra expandida e com ela recolhida; e só as telas desta
  feature MUST mudar de largura ou de altura.
- **FR-1889**: As telas tocadas MUST passar pelos guardiões de acessibilidade, larguras, vocabulário e
  folha que já varrem a gestão — o link de salto, o `main`, toda classe com regra na folha, todo botão
  de envio com classe.

### Key Entities

Nenhuma. Só apresentação.

## Decisões

### D-001 — A trilha destas telas é a do Edital, mais os níveis que cada uma já tinha

As onze telas pendem do Edital, e dez delas já diziam *Processos Seletivos › Edital › tela*. Faltava o
Processo, que a trilha do Edital mostra desde a `078`. A trilha de cada uma é a do Edital, com os
níveis que ela já tinha depois dele — o marco na conferência, a Ocupação e a Convocação nos
históricos, a Classificação no Ato —, como a decisão 001 da `080` fez com as filhas da Distribuição.
O Ato de classificação, que pulava o Edital, ganha o nível que as outras dez já tinham.

**Alternativa descartada**: *o marco como nível entre o Edital e a tela* (Edital › marco › Corte).
Seria um nível que estas telas não mostravam, e o destino dele — a condução do marco — não é a tela de
onde a pessoa chegou: ao Corte, à Ocupação e à Convocação chega-se pelo detalhe do Edital.

### D-002 — Os rótulos da página atual não mudam, nem o do Ato

O Ato de classificação se identifica pelo identificador do ato, e o corte histórico pela data e hora
da emissão. São longos, e no cabeçalho ficam mais à vista. Trocá-los — por "Ato" ou pelo nome do
marco — seria mudar como o ato é citado, e o identificador é o que o link guardado e a auditoria
citam. Ficam; a 375 px a trilha quebra a linha (FR-1884), e o inventário prova que não estoura.

### D-003 — As mensagens não sobem acima dos termos

Na `080`, o resultado do último envio subiu para logo abaixo do título, antes da explicação do ato
(`FR-1806` da `080`). Aqui ele já está logo depois do título, do contexto e dos termos recolhidos da
tela — e os termos precisam vir antes: definem *recorte*, *faixa* e *geração* no primeiro uso
(`FR-424` da `030`), e a mensagem e a navegação entre recortes os usam. A ordem fica.

### D-004 — O que não muda, por governança

- **Nenhuma ação que não se desfaz muda de peso.** "Emitir a ordem" e "Anular e constituir o sucessor"
  continuam com o desenho de perigo; "Realizar o sorteio", "Publicar e congelar a relação", "Emitir
  corte", "Emitir faixa seguinte", "Apurar a ocupação deste recorte", "Emitir nova apuração", "Pedir a
  faixa seguinte com este déficit", "Convocar", "Registrar desfecho", "Registrar atestado" e "Emitir a
  comunicação" continuam com o de ação principal, que já tinham; "Publicar relação nova, sucedendo a
  atual" e "Emitir a comunicação de novo" continuam com o de ação secundária.
- **O desenho que estas ações já têm não se reabre aqui.** Que vários desses atos saiam de um botão de
  ação principal, sem conferência, é decisão das features que os criaram; revê-la é governança, e fica
  registrada como achado na pesquisa.
- **Nenhum texto muda.** Nem os títulos, nem os termos, nem as mensagens; o vocabulário destas telas é
  varrido por listas literais.

### D-005 — A impressão fica como a folha comum a desenha, e a pergunta, com o produto

Antes, a trilha morava no conteúdo e saía no papel com "Edital N/AAAA"; no cabeçalho, ela não sai,
porque a `076` tira o cabeçalho de contexto da impressão. Achado pela revisão do PR, em 18/10: das
onze telas, nove deixam de dizer, impressas, de que Edital são. Corrigir pede uma de duas coisas, e
nenhuma cabe aqui: imprimir a trilha do cabeçalho é regra da folha comum, que vale para todas as
telas modernizadas, e é a mesma pergunta sobre impressão que a `081` deixou com o produto; e
acrescentar o Edital à linha abaixo do título muda texto, que a `FR-1887` proíbe. Fica registrado,
com a contagem, na pesquisa.

### D-006 — No Ato, "Classificação" continua levando à ampla concorrência

O link "Classificação" da trilha do Ato leva à Classificação do marco sem o recorte do ato: num ato da
lista PPI, ele abre a ordem da ampla concorrência — o desvio que a `FR-497` da `034` fechou na
conferência. É anterior a esta feature; ela só o levou ao cabeçalho. Levar o recorte muda o destino
de um link, e a `FR-1881` pede o mesmo destino de antes. Fica registrado como achado, para uma feature
que possa mudar o destino.

## Success Criteria *(mandatory)*

- **SC-740**: Refeito o inventário visual, **zero** variantes estouram a 375 ou a 1280 px, e
  **nenhuma** muda de `status`, nos dois estados da barra.
- **SC-741**: Fora das dez telas do escopo que o inventário abre, **nenhuma** variante muda de largura
  ou de altura.
- **SC-742**: Nas onze telas, "onde estou" aparece **uma** vez por página, no cabeçalho de contexto, e
  cada nível acima da tela está a **um** clique.
- **SC-743**: Das onze telas, as que levam ao Processo pela trilha passam de **zero** para **onze**, e
  as que levam ao Edital, de **dez** para **onze**.
- **SC-744**: A suíte contra PostgreSQL continua sem falhas.
- **SC-745**: O percurso — do Edital a cada tela e de volta pela trilha — é feito só pelo teclado, com
  foco visível, a 1280 e a 375 px.

## Assumptions

- "Telas de resultado e dos atos depois da inscrição" são as onze do pedido; todas pendem do Edital e
  fazem sentido juntas. Exportar para matrícula é a última delas — o destino dos convocados —, e não é
  ato, mas tem a mesma trilha.
- A conferência da emissão não está no inventário visual: ela é a resposta a um envio, e o inventário
  só abre telas pelo endereço. É provada pelos testes e no navegador, como a conferência da retirada
  na `080`.
- O produto no começo da trilha é a sigla GPS, como da `076` à `080`.
- A tela mais estreita que se considera é a de 375 px, a mesma do inventário.
- A validação com a equipe, recomendada desde a `075`, continua pendente; este incremento não a
  substitui.
