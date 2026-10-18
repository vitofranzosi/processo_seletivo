# Feature Specification: As telas dos avisos aos candidatos, quinto grupo da etapa 4

**Feature Branch**: `claude/wizardly-hermann-1b3a8b`, sobre a `main` em `cf6d7372`, que traz da `075` à
`080`

**Created**: 2026-10-18

**Status**: Implementada — PR aberto, merge com o usuário

**Input**: etapa 4 da sequência do [estudo da entrada na gestão](../../doc/estudo-acesso-a-gestao-2026-10-16.md)
(§7) — a modernização por tela, incremental. Depois de quem avalia
([`077`](../077-telas-de-uso-diario/spec.md)), de quem elabora
([`078`](../078-telas-de-quem-elabora/spec.md)), da presidência
([`079`](../079-telas-da-presidencia/spec.md)) e das filhas da Distribuição
([`080`](../080-telas-filhas-da-distribuicao/spec.md)), as seis telas dos avisos aos candidatos da
[`066`](../066-avisos-complementares/spec.md): os Avisos aos candidatos de um Edital, o histórico de um
aviso, a prévia que confirma um aviso (de resultado, de chamada ou de reenvio), a conferência da
interrupção, os Modelos de aviso da unidade e a edição de um modelo. A linha de base visual é o
[inventário de 16/10](../../doc/inventario-visual-da-gestao-2026-10-16.md), refeito em 18/10/2026 sobre
`cf6d7372`, nos dois estados da barra.

> **Faixa de identificadores.** Esta spec usa FR-1940 a FR-1952 e SC-760 a SC-765, do começo da faixa
> reservada para ela — trinta números de FR a partir de FR-1940 e dez de SC a partir de SC-760 —
> quando a `083`, a `084` e a `085` foram abertas em paralelo, em 18/10/2026.

---

## Por que esta feature existe

**Nas telas dos avisos, "onde estou" aparece duas vezes, e diferente em cada uma.** O cabeçalho diz só
*GPS › Processos Seletivos*; o caminho reaparece no conteúdo, numa segunda linha. Das quatro telas que
pendem de um Edital, **nenhuma** leva ao Processo pela trilha — todas saltam de "Processos Seletivos"
direto para o Edital —, quando o detalhe do Edital diz *GPS › Processos Seletivos › código › Edital*
desde a `078`. E a conferência da interrupção salta também os Avisos aos candidatos: vai do Edital ao
aviso.

**Uma trilha diz um nome e leva a outro lugar.** Na prévia do reenvio — "Tentar de novo as que não
saíram" ou "Reenviar, com justificativa" —, o nível acima da tela se chama *Avisos aos candidatos* e
leva ao aviso anterior, e não à lista dos avisos. **Medido em 18/10/2026**: um link de trilha, nas seis
telas, cujo rótulo não nomeia o destino.

**Nos modelos, o cabeçalho e a trilha se contradizem.** Os Modelos de aviso são uma seção da barra, no
grupo Unidade, desde a `076`: a barra os marca e o cabeçalho diz *GPS › Modelos de aviso*. Logo abaixo,
a trilha do conteúdo diz *Processos Seletivos › Modelos de aviso* — a seção de outro grupo. É a
contradição que a `077` tirou da Etapa (`FR-1752` da `077`), nas duas telas dos modelos.

**"Aqui não há nada" tem três desenhos na gestão, e estas telas usam o menor.** Sem aviso confirmado,
sem resultado publicado ou sem modelo, a frase sai em letra pequena e esmaecida — o desenho das
pendências de uma linha —, quando as telas que a `078`, a `079` e a `080` tocaram dizem o mesmo na
caixa tracejada do estado vazio.

**Os botões do formulário ficam soltos.** Na edição de um modelo e na conferência da interrupção,
"Salvar o modelo"/"Cancelar" e "Interromper o envio"/"Voltar sem interromper" vêm logo depois do último
campo, sem o rodapé que separa o ato do formulário nas conferências da `079` e da `080`. E "Novo
modelo", a única ação da lista dos modelos, está num parágrafo comum, e não na faixa de ações da lista
de Processos.

**O que não muda, e não se negocia aqui:** nenhuma regra de negócio, permissão, semântica de papel ou
fluxo. Nenhum endereço, nenhuma view. **O aviso não sai no clique**: a confirmação grava, e quem envia é
o despacho, a cada minuto — nada disso muda. Nenhuma ação que não se desfaz — "Enviar a N pessoas",
"Interromper o envio" — muda de lugar, de rótulo, de peso ou das frases que a precedem. Nenhum texto que
a `066` decidiu — a frase de que o aviso não é o ato, o rodapé fixo, as consequências do envio — muda.
Nenhuma tela fora destas seis.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Onde estou, dito uma vez só, nas telas dos avisos de um Edital (Priority: P1)

O gestor abre o detalhe do Edital 51/2026 e vai a "Ver e enviar avisos". No topo, o cabeçalho diz
*GPS › Processos Seletivos › PS-DEMO-2026 › Edital 51/2026 › Avisos aos candidatos*, e cada nível acima
leva a ele. O conteúdo começa pelo título. Ao abrir um aviso confirmado, a trilha ganha *› Aviso de
18/10/2026*; ao ir a "Interromper o envio", *› Interromper*, com os Avisos aos candidatos e o aviso a
um clique.

**Why this priority**: é o que a `077` à `080` fizeram nas outras telas de uso diário; sem isso, o
gestor lê o caminho no cabeçalho até o Edital e o perde um clique adiante, sem o Processo.

**Independent Test**: nas quatro telas, o caminho está no cabeçalho de contexto, com um link por nível
acima da tela e a tela como página atual; o conteúdo não tem trilha; a página tem uma trilha só.

**Acceptance Scenarios**:

1. **Given** os Avisos aos candidatos de um Edital, **When** a página abre, **Then** o cabeçalho mostra
   *GPS › Processos Seletivos › código do Processo › Edital N/AAAA › Avisos aos candidatos*, com os três
   níveis do meio como links, e o conteúdo começa pelo título.
2. **Given** o histórico de um aviso, **When** a página abre, **Then** a trilha é a dos Avisos aos
   candidatos, com eles como link, terminando em *Aviso de DD/MM/AAAA*.
3. **Given** a conferência da interrupção, **When** a página abre, **Then** a trilha é a do aviso, com
   ele como link, terminando em *Interromper*.
4. **Given** a conferência da interrupção recusada — motivo vazio —, **When** a página volta, **Then** a
   trilha é a mesma, e o erro vem logo abaixo do título, com o foco nele, como antes.

---

### User Story 2 — A prévia diz de onde veio, e cada nível leva aonde diz (Priority: P1)

A gestora abre "Avisar candidatos — resultado preliminar" nos Avisos aos candidatos. O cabeçalho diz
*… › Edital 51/2026 › Avisos aos candidatos › Avisar candidatos*. Pela Convocação de um marco, "Avisar
os convocados desta publicação" abre a mesma tela com *… › Edital 51/2026 › Convocação › Avisar
candidatos*. E pelo histórico de um aviso, "Tentar de novo as que não saíram" a abre com *… › Avisos aos
candidatos › Aviso de 18/10/2026 › Avisar candidatos* — os Avisos aos candidatos levam à lista dos
avisos, e o aviso, ao aviso de onde ela veio.

**Why this priority**: é a mesma tela para três portas; a trilha é o que diz por qual se chegou, e hoje
um dos níveis leva a lugar diferente do que nomeia.

**Independent Test**: nas três variantes da prévia, o nível acima da tela é a tela de onde ela se abre,
com o rótulo dela; todo link da trilha leva à tela que o rótulo nomeia.

**Acceptance Scenarios**:

1. **Given** a prévia de um aviso de resultado, **When** a página abre, **Then** o nível acima é *Avisos
   aos candidatos*, e leva à lista dos avisos do Edital.
2. **Given** a prévia de um aviso de chamada, **When** a página abre, **Then** o nível acima é
   *Convocação*, e leva à Convocação do marco, no mesmo recorte de lista a que "Cancelar" leva.
3. **Given** a prévia de um reenvio, de falhas ou justificado, **When** a página abre, **Then** os
   níveis acima são *Avisos aos candidatos* — a lista — e *Aviso de DD/MM/AAAA* — o aviso anterior.
4. **Given** qualquer das três, **When** a página abre, **Then** a frase de que esta é uma prévia e de
   que o aviso não é o ato continua a primeira coisa depois do título, e "Enviar a N pessoas" continua
   depois das consequências do envio, no mesmo desenho.

---

### User Story 3 — Os modelos falam como a seção da barra a que pertencem (Priority: P2)

O gestor abre "Modelos de aviso" na barra, no grupo Unidade. O cabeçalho diz *GPS › Modelos de aviso*,
e não há outra trilha no conteúdo. Abre um modelo: *GPS › Modelos de aviso › Resultado preliminar
publicado*, com os Modelos de aviso a um clique. "Novo modelo" está na faixa de ações, como "Novo
Processo Seletivo" na lista de Processos.

**Why this priority**: tira a contradição entre a barra e a trilha; a P1 e a P2 cobrem o fluxo de
avisar, esta cobre o de preparar o texto.

**Independent Test**: na lista dos modelos, a trilha tem um nível, a própria seção, sem link; na edição,
dois; nenhuma das duas diz *Processos Seletivos*.

**Acceptance Scenarios**:

1. **Given** os Modelos de aviso, **When** a página abre, **Then** o cabeçalho mostra *GPS › Modelos de
   aviso* como página atual, e a barra marca a mesma seção.
2. **Given** a edição de um modelo, ou um modelo novo, **When** a página abre, **Then** o cabeçalho
   mostra *GPS › Modelos de aviso › nome do modelo* (ou *Novo modelo*), com os Modelos de aviso como
   link.
3. **Given** os Modelos de aviso, **When** a página abre, **Then** "Novo modelo" vem na faixa de ações
   da lista, com o desenho de ação principal, e "Inativar"/"Reativar" continuam como ação de linha.

---

### User Story 4 — O estado vazio e o rodapé do formulário, no desenho comum (Priority: P3)

Num Edital sem aviso confirmado, "Nenhum aviso foi confirmado neste Edital." vem na caixa do estado
vazio, como "Esta comissão ainda não tem membros." na Comissão. Na edição de um modelo e na conferência
da interrupção, os botões vêm no rodapé do formulário, separados dos campos, como na conferência da
inclusão na comissão.

**Why this priority**: é consistência de desenho; não muda o que se alcança nem o ato.

**Independent Test**: os três estados vazios das telas usam o desenho comum, com o mesmo texto; os
botões das duas telas vêm no rodapé comum, com os mesmos rótulos, desenhos e ordem.

**Acceptance Scenarios**:

1. **Given** um Edital sem resultado publicado ou sem aviso confirmado, ou uma unidade sem modelo,
   **When** a página abre, **Then** a frase vem no desenho do estado vazio, com o texto de antes.
2. **Given** a edição de um modelo, **When** a página abre, **Then** "Salvar o modelo" e "Cancelar" vêm
   no rodapé do formulário, no desenho de antes.
3. **Given** a conferência da interrupção, **When** a página abre, **Then** "Interromper o envio", com o
   desenho de perigo, e "Voltar sem interromper" vêm no rodapé do formulário, depois do motivo.

### Edge Cases

- **Trilha longa no celular.** A da prévia do reenvio tem sete níveis. A 375 px a trilha quebra a linha
  dentro do cabeçalho; nem ela nem "Trocar identidade" estouram a largura.
- **A prévia do resultado aberta pelas publicações do marco.** O resultado também se avisa a partir da
  tela das publicações do marco. A trilha continua a dos Avisos aos candidatos, que é aonde "Cancelar"
  leva desde a `066`: a trilha e "Cancelar" dizem o mesmo lugar.
- **A prévia recusada.** Assinatura vencida, texto com variável proibida, envio desabilitado: a prévia
  volta com o erro no mesmo lugar — depois da frase de que é uma prévia, com o foco nele (D-003) — e a
  mesma trilha.
- **Envio desabilitado na instalação.** A frase que o diz continua onde está, nos Avisos aos candidatos
  e na prévia; a trilha e os estados vazios não dependem dela.
- **Quem consulta e não avisa.** Os Avisos aos candidatos e o histórico abrem para quem consulta o
  Processo sem poder avisar. A trilha é a mesma; a seção "Resultados publicados" e as ações continuam
  dependendo do que a pessoa pode.
- **Aviso interrompido ou concluído.** O histórico não oferece "Interromper o envio"; a trilha não muda.
- **Modelo novo recusado.** Nome repetido ou variável proibida: a tela volta com o erro abaixo do título,
  o foco nele, e a trilha termina em *Novo modelo*.
- **O link de salto.** Continua levando ao conteúdo, que agora começa pelo título.
- **Impressão.** A barra e o cabeçalho de contexto não saem no papel (`076`). O título e a linha de baixo
  dele continuam identificando o Edital e o aviso impressos.

## Requirements *(mandatory)*

### Functional Requirements

#### A trilha no cabeçalho de contexto

- **FR-1940**: Nos Avisos aos candidatos, no histórico de um aviso, na prévia de um aviso, na
  conferência da interrupção, nos Modelos de aviso e na edição de um modelo, o cabeçalho de contexto
  MUST mostrar a trilha da tela, como navegação nomeada: o produto, cada nível acima da tela como link,
  e a própria tela como a página atual — como nas telas da `077` à `080` (`FR-1800` da `080`).
- **FR-1941**: Nas quatro telas que pendem de um Edital, os níveis acima da tela MUST começar pelos da
  trilha do detalhe do Edital — Processos Seletivos, o Processo e o Edital (`FR-1767` da `078`). No
  histórico de um aviso, o nível seguinte MUST ser os Avisos aos candidatos; na conferência da
  interrupção, os Avisos aos candidatos e o aviso. Os rótulos da página atual MUST ser os que cada tela
  já mostrava: *Avisos aos candidatos*, *Aviso de DD/MM/AAAA*, *Interromper*.
- **FR-1942**: Na prévia de um aviso, o nível acima da tela MUST ser a tela de onde ela se abre — os
  Avisos aos candidatos, no aviso de resultado; a Convocação do marco, no mesmo recorte de lista a que
  "Cancelar" leva, no aviso de chamada; os Avisos aos candidatos e o aviso anterior, no reenvio —, e a
  página atual MUST ser *Avisar candidatos*.
- **FR-1943**: Em toda trilha destas telas, cada link MUST levar à tela que o rótulo nomeia.
- **FR-1944**: Nos Modelos de aviso, a trilha MUST ter um nível, a própria seção, como página atual e
  sem link (`FR-1746` da `077`); na edição de um modelo, a seção como link e o nome do modelo — ou *Novo
  modelo* — como página atual. Nenhuma das duas MUST dizer uma seção diferente da que a barra marca.
- **FR-1945**: Nessas seis telas a trilha MUST NOT aparecer de novo no conteúdo: a página MUST ter uma
  trilha só, e o conteúdo MUST começar pelo título.
- **FR-1946**: A trilha MUST ser a mesma para quem avisa e para quem só consulta: nenhum nível MUST
  aparecer, sumir ou deixar de ser link conforme quem lê.
- **FR-1947**: A 375 px, a trilha do cabeçalho MUST quebrar a linha dentro da largura, e "Trocar
  identidade" MUST continuar alcançável.

#### O desenho comum

- **FR-1948**: "Nenhum resultado foi publicado neste Edital ainda.", "Nenhum aviso foi confirmado neste
  Edital." e "A unidade ainda não tem modelos de aviso." MUST vir no desenho do estado vazio das demais
  telas da gestão (`FR-1772` da `078`), com o mesmo texto.
- **FR-1949**: Na edição de um modelo e na conferência da interrupção, os botões do formulário MUST vir
  no rodapé comum dos formulários, o das conferências da `079` e da `080`, depois do último campo, com
  os mesmos rótulos, desenhos e ordem.
- **FR-1950**: Nos Modelos de aviso, "Novo modelo" MUST vir na faixa de ações da lista, como "Novo
  Processo Seletivo" na lista de Processos (`FR-1741` da `077`), com o desenho de ação principal.

#### O que não muda

- **FR-1951**: As ações que não se desfazem — "Enviar a N pessoas" na prévia e "Interromper o envio" no
  histórico e na conferência — MUST continuar com o rótulo, o desenho de perigo, o lugar e as frases que
  as precedem; os reenvios, "Usar este modelo", "Atualizar a prévia", "Ver a mensagem de outra pessoa",
  "Avisar candidatos" e "Inativar"/"Reativar" MUST continuar com o desenho de antes. A frase de que o
  aviso não é o ato MUST continuar a primeira coisa depois do título, nos Avisos aos candidatos e na
  prévia (a decisão 001 da `066`).

#### O que não pode piorar

- **FR-1952**: Nenhuma variante do inventário visual MUST deixar de carregar, mudar de `status` ou passar
  a estourar a 375 ou a 1280 px, com a barra expandida e com ela recolhida; só as telas desta feature
  MUST mudar de largura ou de altura; e as telas tocadas MUST passar pelos guardiões de acessibilidade,
  larguras, vocabulário e folha que já varrem a gestão.

### Key Entities

Nenhuma. Só apresentação.

## Decisões

### D-001 — A trilha da prévia é a da porta por onde se chegou

A prévia é uma tela só para três portas, e a `066` já a fazia dizer a de resultado e a de chamada. A do
reenvio herdava o rótulo da de resultado com o endereço do aviso anterior. A trilha passa a ser a da
tela de onde a prévia se abre, com ela no fim — o mesmo que a `080` fez com as filhas da Distribuição
(a decisão 001 da `080`) —, e o reenvio ganha os dois níveis que tem: a lista e o aviso.

### D-002 — Os modelos são uma seção da barra, e a trilha começa nela

Desde a `076`, os Modelos de aviso são um lugar da barra, no grupo Unidade, e a lista dos modelos é a
raiz dessa seção, como a lista de Processos e Minhas Etapas são as das suas. A trilha deles começa no
produto e na seção, sem *Processos Seletivos*.

### D-003 — A frase de que é uma prévia continua antes do erro

A `080` subiu o resultado do último envio para logo abaixo do título (`FR-1806` da `080`). Na prévia, a
`066` decidiu que a frase que diz o que o aviso é vem "antes de qualquer outra coisa" (a decisão 001 da `066`),
e a prévia recusada é ainda uma prévia: nada foi gravado. O erro continua logo depois dela, antes de
tudo o mais, com o foco nele. No histórico, na conferência da interrupção e nos modelos, o resultado do
último envio já vem logo abaixo do título, e nada muda.

### D-004 — "Avisar candidatos" continua ação de linha

Nos Avisos aos candidatos, cada marco com resultado publicado oferece "Avisar candidatos — resultado
preliminar" (ou definitivo), uma por natureza pendente — tantas quantas houver. São ações de cada linha
da lista, e não a ação da tela; e levam à prévia, que é quem confirma. Ficam com o desenho de ação de
linha.

### D-005 — O que não muda, por governança

- **Nenhuma ação que não se desfaz ganha ou perde peso.** "Enviar a N pessoas" e "Interromper o envio"
  continuam com o desenho de perigo, no mesmo lugar, depois das frases que declaram o alcance.
- **O aviso não sai no clique.** A confirmação grava; quem envia é o despacho. Nenhuma frase que o diz
  muda.
- **Os textos da `066` não mudam**: a frase de que o aviso não é o ato, o rodapé fixo, as variáveis,
  as consequências do envio e da interrupção.

## Success Criteria *(mandatory)*

- **SC-760**: Refeito o inventário visual, **zero** variantes estouram a 375 ou a 1280 px, e **nenhuma**
  muda de `status`, nos dois estados da barra.
- **SC-761**: Fora dos Avisos aos candidatos, do histórico, da prévia, da interrupção e dos dois modelos,
  **nenhuma** variante muda de largura ou de altura.
- **SC-762**: Nas seis telas, "onde estou" aparece **uma** vez por página, no cabeçalho de contexto, e
  cada nível acima da tela está a **um** clique.
- **SC-763**: Das quatro telas que pendem de um Edital, as que levam ao Processo pela trilha passam de
  **zero** para **quatro**; os links de trilha cujo rótulo não nomeia o destino, de **um** para **zero**;
  e as telas cuja trilha diz outra seção que a da barra, de **duas** para **zero**.
- **SC-764**: A suíte contra PostgreSQL continua sem falhas.
- **SC-765**: O percurso — do detalhe do Edital aos Avisos aos candidatos, a um aviso, à interrupção e de
  volta pela trilha; da barra aos Modelos de aviso e a um modelo — é feito só pelo teclado, com foco
  visível, a 1280 e a 375 px.

## Assumptions

- "Telas de avisos aos candidatos" são as seis do pedido. A prévia é uma tela com três variantes —
  resultado, chamada e reenvio —, e as três estão no escopo; o inventário visual captura a de resultado e
  a de reenvio, e a de chamada pede uma comunicação por publicação que o seed não emite: ela é provada
  pelos testes.
- A conferência da interrupção e a prévia são capturadas pelo inventário por endereço, sem envio.
- O produto no começo da trilha é a sigla GPS, como da `076` à `080`.
- A tela mais estreita que se considera é a de 375 px, a mesma do inventário.
- A validação com a equipe, recomendada desde a `075`, continua pendente; este incremento não a
  substitui.
