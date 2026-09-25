# Feature Specification: O Perfil de Vaga na visão institucional

**Feature Branch**: `claude/spec-processos-seletivos-visao-395a64`

**Created**: 2026-09-21

**Status**: Draft

**Input**: Revisão de produto de 21/09, feita **sobre a `040` já funcionando**. A tela tornou visível
uma lacuna que no papel era menos evidente: *"o agregado atual diz qual Edital tem problema; o Perfil
permitirá dizer onde, dentro dele, está o problema. Para a Coordenação de Seleção, essa diferença é
enorme."*

> **Faixa de identificadores.** Abre em **FR-606** e **SC-215**. Teto medido em 2026-09-21 nesta
> árvore — `FR-605` / `SC-214` — e nas worktrees paralelas, que param abaixo dele. **Nenhum `UX-` é
> definido**: as marcas desta página continuam sendo aritmética sobre colunas apresentadas, e não
> espécies do catálogo fechado da `022`/`038`. As **decisões** reiniciam em `D-001`.

> **Teto proporcional.** Duas histórias e catorze requisitos. A feature acrescenta **uma** capacidade
> — expandir — e **muda o nível** de uma que já existe. Nada mais.

---

## 1. O problema

**O agregado por Edital esconde onde a procura faltou.**

Um Edital com 40 vagas repartidas em dois Perfis de 20 — um recebendo 7 inscrições e o outro
nenhuma — aparece na visão como:

```text
Edital 26/2026 · 40 vagas · 7 submetidas · 0,2 inscr./vaga
```

O número está certo e **a informação gerencial se perdeu**: metade da oferta não teve procura
alguma, e a linha não diz. Pior no Edital misto, onde um Perfil publica vaga e outro é só cadastro
de reserva: a demanda aparece somada e não se sabe onde ela aconteceu.

**A própria tela já denuncia a lacuna.** O consolidado diz *"sobre 3 Perfis com vaga imediata"* — e
a tabela só deixa enxergar Editais. O número cita uma granularidade que a página não oferece.

---

## 2. A evidência que decide o custo

**O dado por Perfil já está sendo lido.** Não é projeção: é o que a `040` faz hoje.

| Fato medido | Onde |
|---|---|
| As inscrições submetidas já são agregadas **por Perfil** — `values("edital_id", "profile_id", "status")` | `interface/visao_geral.py::contagens_por_edital` |
| O conteúdo publicado já é percorrido **Perfil a Perfil**, e a quantidade de cada um é **descartada** | `interface/visao_geral.py::vagas_do_conteudo` |
| Denominação, código e localidade de cada Perfil já vêm no snapshot carregado | `VersaoConsolidada.content["profiles"][]` |

A repartição por Perfil não foi escolha de conveniência: a decisão do **numerador recortado** da
`040` a obrigou, para que inscrição em Perfil sem vaga imediata não entrasse na razão.

**Consequência**: a expansão custa **zero consulta nova**, e `SC-209` da `040` continua valendo sem
esforço. Não é *"mais detalhe"* — é informação já em memória sendo jogada fora na montagem da linha.

**O que falta, e é pequeno**: os rascunhos hoje são um contador único por Edital. Para haver *Em
preenchimento* por Perfil, a mesma consulta precisa acumulá-los por Perfil também.

---

## 3. O que esta feature NÃO é

- **Não troca a linha do Edital por linhas de Perfil.** Isso perderia a visão macro, que é a razão
  de a página existir.
- **Não cria eixo novo.** O Perfil é o que o conteúdo publicado já nomeia; `locality` continua texto
  livre e é apresentado como publicado. As perguntas sobre **polo** seguem abertas onde já estavam.
- **Não acrescenta espécie ao catálogo de sinais** da `022`/`038`, fechado por `FR-565`.
- **Não antecipa o funil.** Classificados, convocados e ocupação continuam registrados e não
  apresentados.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Onde, dentro do Edital, a procura faltou (Priority: P1) 🎯 MVP

Quem coordena vê a tabela, encontra o Edital com pouca procura e **expande a linha**: os Perfis
aparecem com vagas, demanda e razão próprias, e o Perfil vazio salta à vista sem sair da página.

**Why this priority**: é a pergunta que a `040` deixou sem resposta, e a única que exige estrutura
nova na tela. Sozinha ela já entra em produção.

**Independent Test**: semear um Edital com dois Perfis de 20 vagas — um com 7 inscrições, outro com
nenhuma —, abrir a visão, expandir a linha e identificar o Perfil vazio.

**Acceptance Scenarios**:

1. **Given** um Edital com dois Perfis, **When** a linha é expandida, **Then** cada Perfil aparece
   com denominação, vagas imediatas, cadastro de reserva, submetidas, em preenchimento e razão.
2. **Given** um Perfil que publica `0` vaga imediata e cadastro reserva ilimitado, **When** ele é
   apresentado, **Then** vagas sai `0` — zero legítimo — e a razão sai **não aplicável**.
3. **Given** um Perfil com cadastro de reserva **limitado**, **When** ele é apresentado, **Then** a
   tela o distingue de *ilimitado* e de *nenhum*, e diz o limite.
4. **Given** a soma dos Perfis, **When** comparada à linha do Edital, **Then** vagas e submetidas
   reconciliam; a **razão do Edital é recalculada** dos totais elegíveis, e não sai da soma nem da
   média das razões dos Perfis.
5. **Given** qualquer Edital, **When** a página é aberta, **Then** a expansão está **recolhida**.

---

### User Story 2 — A Atenção passa a dizer quantos Perfis (Priority: P2)

A mesma pessoa lê a coluna Atenção e, em vez de *"encerrou com menos inscrições do que vagas"*,
lê **"2 de 3 Perfis com demanda abaixo das vagas"** — e ao expandir descobre quais.

**Why this priority**: depende de a expansão da `US1` existir para ser verificável, e é o que torna
a coluna acionável. Sem ela, a Atenção continua dizendo do Edital o que vale de parte dele.

**Independent Test**: um Edital com razão global **acima** de 1 e um Perfil vazio — hoje ele não
recebe marca nenhuma; sob esta história, recebe.

**Acceptance Scenarios**:

1. **Given** um Edital com razão global 2,1 e um Perfil sem nenhuma inscrição, **When** o período
   encerrou, **Then** a linha recebe marca — que hoje ela **não** recebe.
2. **Given** um Edital em que todos os Perfis têm demanda acima das vagas, **When** o período
   encerrou, **Then** não há marca.
3. **Given** uma marca de Edital, **When** ela é lida, **Then** ela nomeia **quantos Perfis de
   quantos**, com o denominador **de cada espécie** — todos os vigentes para *sem procura*, só os
   com vaga imediata para *demanda abaixo da oferta* —, e continua legível sem cor.
4. **Given** um Perfil só de cadastro de reserva e **sem nenhuma inscrição**, **When** o período
   encerrou, **Then** ele recebe *sem procura* — a marca não depende de haver denominador.

---

### User Story 3 — Ver só o que pede atenção (Priority: P3)

Numa lista longa, quem coordena marca **Somente com atenção** e a tabela fica só com os Editais que
têm algum Perfil marcado.

**Why this priority**: amplia o alcance das duas anteriores e não é precondição de nenhuma. É um
booleano sobre fato **já derivado** — não inventa dimensão, não acrescenta consulta, e só passa a
valer a pena quando o acervo deixa de ter três Editais.

**Independent Test**: com um Edital marcado e um sem marca no mesmo recorte, ligar o filtro e ver a
tabela reduzir-se a um — e o consolidado acompanhar.

**Acceptance Scenarios**:

1. **Given** um recorte com Editais marcados e não marcados, **When** o filtro é ligado, **Then** a
   tabela mostra só os marcados, e o consolidado muda **junto** com ela.
2. **Given** o filtro ligado e nenhum Edital marcado, **When** a página é lida, **Then** ela declara
   o recorte vazio sem afirmar nada sobre o acervo.
3. **Given** o filtro, **When** ele é aplicado, **Then** acontece **depois** da materialização das
   versões — a marca só existe depois de ler o conteúdo publicado.

---

### Edge Cases

- **Edital sem conteúdo publicado** — não há Perfil a expandir, e o controle não é oferecido.
- **Edital com um Perfil só** — a expansão existe e repete a linha; é o caso comum, e escondê-la
  criaria duas gramáticas para a mesma tabela (`FR-606`).
- **Perfil com `0` vaga e `0` inscrição, período aberto** — sem marca: o número ainda vai mudar.
- **Edital com dezesseis Perfis** — a expansão fica longa; recolhida por padrão é o que a mantém
  utilizável, e o limiar que obrigaria a paginar fica registrado em `G-004`.
- **Perfil publicado e depois retificado** — os Perfis são os da **versão vigente**, como as vagas
  já são.
- **Inscrição cujo `profile_id` não está na versão vigente** — acontece quando a Retificação remove
  um Perfil. Ela **conta** em *Submetidas* do Edital e **não** aparece em Perfil nenhum; a diferença
  MUST ser dita, e não escondida (`FR-613a`).

---

## Requirements *(mandatory)*

### A expansão

- **FR-606**: Cada linha de Edital com conteúdo publicado MUST permitir expandir os **Perfis de Vaga
  da versão vigente**, e a expansão MUST nascer recolhida.
- **FR-607**: A expansão MUST apresentar, por Perfil: denominação publicada, vagas imediatas,
  espécie de cadastro de reserva, inscrições submetidas, em preenchimento e inscrições por vaga. O
  **código** publicado MUST acompanhar a denominação, e MUST NOT ocupar coluna própria — ele é o que
  distingue Perfis de nome parecido, e já vem no snapshot.
- **FR-608**: O cadastro de reserva MUST distinguir as **três** espécies que o conteúdo publica —
  nenhum, **limitado** com o seu limite, e ilimitado. *Colapsar limitado em qualquer das outras duas
  apagaria o que o Edital declarou.*
- **FR-609**: A localidade, onde o Perfil a publica, MUST ser apresentada **como publicada**, sem
  interpretação — ela é texto livre, e lê-la como polo seria decidir uma classificação institucional
  lendo o que alguém digitou.
- **FR-610**: *Em preenchimento* MUST ser contado por Perfil, na mesma consulta que já conta as
  submetidas.
- **FR-611**: A razão do Perfil MUST seguir a regra do Edital: **não aplicável** onde o Perfil não
  publica vaga imediata — nunca `0`, nunca infinito.
- **FR-612**: Vagas e inscrições dos Perfis vigentes MUST reconciliar-se com os totais do Edital,
  ressalvadas as inscrições sem Perfil vigente da `FR-613a`. A **razão do Edital MUST ser
  recalculada** a partir dos totais elegíveis —

  > `Σ inscrições dos Perfis com vaga imediata ÷ Σ vagas imediatas desses Perfis`

  — e MUST NOT ser obtida por soma nem por média das razões dos Perfis. *Razão não é grandeza
  aditiva: dois Perfis de 20 vagas com `1,0` e `3,0` dão `2,0` no Edital, e nunca `4,0`. A redação
  anterior mandava a soma concordar "em vagas, submetidas **e razão**", e autorizava por escrito a
  implementação errada.*

### A Atenção muda de nível

- **FR-613**: As marcas MUST ser calculadas **no Perfil**, e não sobre o agregado do Edital.
- **FR-613a**: Inscrição cujo Perfil não existe na versão vigente MUST continuar contada no Edital,
  MUST NOT ser atribuída a Perfil algum, e a diferença entre a soma dos Perfis e o total do Edital
  MUST ser declarada **em texto**. O sistema MUST NOT criar linha, agrupamento ou rótulo que faça as
  vezes de Perfil — *"Outros"*, *"Removidos"*, *"Sem Perfil"* — para acomodá-la: isso inventaria na
  tela um Perfil que o Edital nunca publicou, e fazer a conta fechar assim é pior que não fechar.
- **FR-614**: A marca do Edital MUST resumir as dos Perfis nomeando **quantos de quantos**, e cada
  espécie MUST declarar **o seu próprio denominador**, porque eles são conceitualmente distintos:
  *sem procura* conta sobre **todos os Perfis vigentes**, e *demanda abaixo da oferta* conta apenas
  sobre os que **publicam vaga imediata** — os demais não têm denominador e não poderiam estar
  abaixo de coisa nenhuma. *"2 de 5" onde só três têm vaga é aritmeticamente verdadeiro e
  institucionalmente enganoso.* A marca MUST continuar legível sem cor.
- **FR-615**: *Sem procura* MUST valer também onde **não há denominador**: um Perfil só de cadastro
  de reserva que encerrou sem nenhuma inscrição encerrou sem procura. *Só a marca de demanda abaixo
  da oferta exige denominador.*
- **FR-616**: A **`FR-602` da `040` MUST ser explicitamente substituída**, e o requisito sucessor
  MUST nomear as **duas** espécies vigentes e **o nível em que são calculadas**. A substituição MUST
  citar o **texto** do requisito revogado — *"a tabela MUST marcar duas situações, derivadas por
  aritmética sobre os números que ela já apresenta"* —, e não apenas o número. *O guardião de
  citações fica verde porque o identificador existe; ele não sabe se é o requisito certo. Citar o
  texto é o que torna a substituição conferível por leitura.*

### O que esta feature preserva

- **FR-617**: A linha MUST continuar sendo o **Edital**. A expansão MUST NOT substituí-la por linhas
  de Perfil, e a visão macro MUST continuar legível sem expandir nada.
- **FR-618**: A expansão MUST NOT acrescentar consulta ao banco.
- **FR-619**: A expansão MUST ser operável por teclado e MUST declarar se está aberta ou recolhida.
- **FR-621**: A tabela MUST oferecer um filtro **Somente com atenção**, booleano, que reduz a
  tabela aos Editais com ao menos um Perfil marcado. Ele MUST ser aplicado **depois** da
  materialização das versões — a marca só existe depois de ler o conteúdo publicado —, e o
  consolidado MUST acompanhar, como acompanha os demais filtros. Nenhum outro filtro por espécie de
  marca entra nesta entrega.
- **FR-620**: O controle de expansão MUST ser **independente do link de navegação** para o Edital: a
  linha inteira MUST NOT alternar a expansão. *A `FR-600` da `040` manda a linha levar ao Edital e a
  `FR-606` manda a linha expandir; juntas, elas autorizam uma linha que faz as duas coisas no mesmo
  clique — e aí uma das duas se perde.* O controle MUST ter nome acessível próprio, nomeando o
  Edital, e MUST declarar o seu estado.

---

## Success Criteria *(mandatory)*

- **SC-215**: Num Edital com dois Perfis de 20 vagas — um com 7 inscrições e outro com nenhuma —
  quem abre a visão **identifica o Perfil vazio sem sair da página**, percorrido pela interface.
- **SC-216**: A expansão **não acrescenta consulta**: a contagem é igual entre um Edital de **1
  Perfil** e um de **12**, e continua igual entre recortes de 3 e de 60 Editais. *A redação anterior
  pedia "com e sem a expansão", e não descrevia medição possível — ela é renderizada no servidor e
  não tem um "sem" (`research.md`, `R-005`). A propriedade que importa, e que esta mede, é o custo
  não crescer com o número de **Perfis**.*
- **SC-217**: ~~As **três** espécies de cadastro de reserva são distinguíveis na tela, e a limitada
  diz o seu limite.~~ **Substituída pela `042`** (`FR-631` dela), pela `SC-224`: a propriedade
  continua valendo — as três espécies **seguem** distinguíveis e a limitada **segue** dizendo o seu
  limite —, mas o **lugar** mudou. Ela era medida numa **coluna** da tabela filha, e a `042` tirou
  essa coluna: cadastro de reserva caracteriza o Perfil, não se compara verticalmente entre Perfis.
  A distinção passa à **identidade** do Perfil, ao lado do código e da localidade, e é lá que a
  `SC-224` a mede. *Um critério cuja medição some não fica satisfeito por inércia: sem esta
  anotação, a `SC-217` continuaria cobrando uma coluna que a tela não tem mais, e o guardião de
  citações ficaria verde do mesmo jeito, porque o identificador existe.*
- **SC-218**: A marca do Edital nomeia **quantos Perfis de quantos**, com o denominador próprio de
  cada espécie, e o Edital com razão global acima de 1 e um Perfil vazio **recebe** marca.
- **SC-219**: A expansão abre e fecha **por teclado**, e o estado é declarado.
- **SC-220**: **Zero** ocorrências de `0` onde a razão do Perfil é não aplicável, e zero ausências
  onde o Perfil publicou `0` vaga.
- **SC-221**: Com um Edital marcado e um sem marca no mesmo recorte, **Somente com atenção** deixa a
  tabela com **um**, e o consolidado muda junto com ela.

---

## Assumptions

### D-001 — o Edital continua sendo a linha, e o Perfil é expansão

Trocar a linha por Perfis daria a granularidade e **perderia a visão macro**, que é a razão de a
página existir: com dezesseis polos, a tabela vira dezesseis linhas do mesmo certame e a leitura de
portfólio desaparece.

A hierarquia resolve as duas: o agregado responde *qual Edital*, a expansão responde *onde dentro
dele*. E é o que mantém a página limpa por padrão.

### D-002 — levar a Atenção ao Perfil é mudança de requisito, e não de apresentação

Hoje a marca é calculada sobre o agregado: um Edital com razão global 2,1 e um Perfil vazio **não
recebe marca nenhuma**. Sob esta feature, recebe.

Isso muda **quais Editais são marcados** — e por isso a `FR-602` da `040` é substituída por escrito
(`FR-616`), na forma que a `038` já usou ao fechar o catálogo da `022`. Deslizar a mudança como
refinamento visual deixaria um requisito vigente descrevendo o que o produto não faz mais.

### D-003 — o cadastro de reserva tem três espécies, e a tela mostra três

`reserveType` publica `NONE`, `LIMITED` — com `reserveLimit` — e `UNLIMITED`. A proposta de revisão
trazia duas colunas de *Não/Ilimitado*, e ela perderia a limitada.

Colapsar é o que este repositório recusa em outros lugares, e aqui apagaria uma quantidade que o
Edital **publicou**.

### D-004 — *sem procura* independe de denominador

As duas marcas não têm a mesma precondição, e a `040` as tratava igual. *Demanda abaixo da oferta* é
uma razão menor que 1, e exige denominador. *Sem procura* é a contagem em zero, e vale igualmente
num Perfil que só oferece cadastro de reserva — encerrar sem nenhuma inscrição é o fato, com vaga
imediata ou sem ela.

### D-005 — zero consulta nova é requisito, e não aspiração

O dado já está carregado, e por isso a expansão **pode** ser gratuita. Mas uma implementação que
lesse o Perfil por Edital produziria o mesmo resultado na tela e destruiria `SC-209`.

Por isso `FR-618` é requisito e `SC-216` o mede — com e sem expansão, e entre dois tamanhos de
recorte. É a mesma disciplina que fez a `040` medir igualdade em vez de teto.

### D-006 — a expansão nasce recolhida

Com dezesseis Perfis por Edital, a tabela aberta por padrão deixaria de ser tabela. Recolhida, o
portfólio continua legível e o detalhe está a um gesto — que é exatamente a informação progressiva
que a `040` adotou entre o consolidado e a tabela.

### D-007 — o Perfil não vira filtro nesta entrega

Filtrar por Perfil exigiria decidir **por qual** — denominação, código ou localidade — e as três são
texto livre no conteúdo publicado. A busca textual já alcança o que a pessoa lembra.

**Filtrar *por Perfil* e filtrar *pelo que pede atenção* são perguntas diferentes**, e só a
primeira é recusada aqui. A segunda está decidida em `D-008`.

---

### D-008 — o filtro *Somente com atenção* entra, e é o único

Decidido pelo usuário em 21/09, revendo a posição da `040`: *"a própria razão desta feature é
descobrir onde falta procura, e agora a Atenção passa a ser calculada de modo realmente útil"*.

**É booleano sobre fato já derivado.** Não inventa dimensão institucional, não lê nada de novo e não
acrescenta consulta — a marca já existe quando a linha é montada.

**É filtro pós-materialização**, como o de situação do período: a marca depende do conteúdo
publicado, e empurrá-lo para o `SQL` é impossível. Ele é o **terceiro** degrau da ordem que a
`FR-598` da `040` fixou.

**E é o único.** Filtros por espécie — *só sem procura*, *só abaixo de 1* — multiplicariam controles
sobre a mesma informação, e a `040` fechou a lista de filtros por decisão. Um booleano responde
*"o que preciso olhar?"*; a expansão responde o resto.

---

## Riscos e lacunas

| # | Lacuna | Consequência | O que esta spec faz |
|---|---|---|---|
| **G-001** | Os rascunhos são hoje um contador único por Edital | *Em preenchimento* por Perfil exige mudar a acumulação | está no escopo (`FR-610`) — mesma consulta, outro dicionário |
| **G-002** | `locality` é **texto livre**, e não polo estruturado | *"diferenças entre polos"* continua sem resposta | apresenta como publicado (`FR-609`); a pergunta segue onde já estava |
| **G-003** | Perfil removido por Retificação deixa inscrições sem Perfil vigente | a soma dos Perfis pode não fechar com o Edital | declara a diferença em vez de escondê-la (`FR-613a`) |
| **G-004** | Edital com muitos Perfis produz expansão longa | a tabela pode ficar impraticável | recolhida por padrão (`D-006`); o limiar **não** é fixado aqui. *E paginar dentro de uma linha expandida seria a **última** saída: antes dela vêm a rolagem normal, o limite visual com "mostrar todos", e — só se um dia existir dimensão real que o justifique — o agrupamento* |
| **G-005** | ~~Não há como ver só o que pede atenção~~ | — | **decidida** em `D-008`: o filtro entra, e é o único |

## Decisões ainda necessárias — governança do usuário

- **`G-004`** — **Qual é o limiar de Perfis que obriga a paginar a expansão?** Não se fixa por
  palpite: pede um Edital real de múltiplos polos, que é a mesma condição que outras perguntas de
  polo já esperam.

## Out of Scope

Classificados, convocados, ocupação e requerimentos de matrícula — registrados na `040` e ordenados
pela revisão de 21/09: **ocupação primeiro**, classificados com a cautela que a falta de definição de
classificação final impõe, requerimentos por último. A série por ano. Gráfico de qualquer espécie.
Exportação. Filtro por Perfil. Polo como dimensão. Qualquer espécie nova no catálogo de sinais.

**Dependência registrada**: a `039`, ainda não mesclada, reorganiza o catálogo de Modalidades do
Edital. Ela **não** altera `profiles[].immediateVacancies` nem `reserveType`, que é o que esta
feature lê — mas se mudar a forma do quadro, esta leitura acompanha. Medir **depois** que ela entrar.
