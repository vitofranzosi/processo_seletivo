# Feature Specification: O sorteio de cada vaga no cartão dela, na página pública do Edital

**Feature Branch**: `claude/vaga-card-participants-access-e55d90`, sobre a `main` em `8b18343e`

**Created**: 2026-11-10

**Status**: Implementada na mesma sessão. A direção foi escolhida pelo usuário entre três
alternativas prototipadas e medidas, e refinada numa segunda rodada; o registro está em
[research.md](research.md).

**Uma coisa só muda, e é de apresentação.** As relações de habilitados continuam as mesmas, nos
mesmos endereços, publicadas pelas mesmas regras; o que a página pública do Edital diz sobre o
sorteio continua dito. Muda **onde**: o que é de uma vaga vai para o cartão dela, e o bloco "Sorteio
público" passa a dizer só o que é do Edital inteiro.

**Input**: *"Um usuário pediu que o link «Ver quem vai participar, e com que número» ficasse no
cartão da vaga, perto dos documentos. Avaliar a arquitetura da informação da página pública do
Edital antes de acrescentar um link; comparar alternativas com prévias; refinar a escolhida para o
celular; especificar e implementar com alteração mínima na camada de apresentação, sem rotas,
modelos ou endpoints novos."*

> **Faixa de identificadores.** Esta spec usa:
>
> - os requisitos funcionais de cinco mil cento e cinquenta a cinco mil cento e sessenta e nove;
> - os critérios de sucesso de mil e seiscentos a mil seiscentos e nove;
> - os requisitos de experiência de quatrocentos a quatrocentos e nove.
>
> Gastos até FR-5162, SC-1603 e UX-402; o resto da reserva fica livre.

## Por que esta feature existe

A `021` trouxe o sorteio para a página que qualquer pessoa abre (FR-011, FR-048): a relação de
habilitados é pública antes de o sorteio acontecer, e a página passou a dizê-lo. Ela o disse num
bloco por lista, ao lado do Cronograma. Cada relação é de um recorte **vaga × marco × lista**, e a
conta cresce depressa: num Edital de três vagas por sorteio e três listas de concorrência são nove
blocos, cada um repetindo o nome inteiro da vaga e o mesmo parágrafo.

Medido sobre o modelo real da página, com a folha real, num Edital de quatro vagas e nove relações:

| | Largura 1280 | Largura 375 |
|---|---|---|
| Altura do bloco "Sorteio público" | 4.235 px | 3.544 px |
| Altura de um cartão de vaga | 242 px | 436 px |
| Do título da segunda vaga até a relação dela | 1.506 px | 2.801 px |

O candidato pergunta pela vaga, e a resposta estava em outra região da página, a duas telas e meia
de celular. O pedido do usuário — levar o link para o cartão — era o sintoma; a causa é a página
repartir por módulo do sistema o que a pessoa lê como uma coisa só.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Achar o sorteio da minha vaga na minha vaga (Priority: P1)

Quem se inscreveu numa vaga abre a página do Edital, encontra o cartão da vaga e vê ali em que ponto
o sorteio dela está e por onde consultar quem participa, e com que número.

**Why this priority**: é o relato que originou a feature, e a medida que ela existe para mudar.

**Independent Test**: publicar a relação de uma vaga e abrir a página; o endereço da relação está
dentro do cartão da vaga, uma única vez na página.

**Acceptance Scenarios**:

1. **Given** uma vaga com uma relação vigente e sem sorteio, **When** a página é aberta, **Then** o
   cartão diz "Aguardando o sorteio", a data e a hora em que a lista foi fechada, e oferece "Ver
   quem vai participar, e com que número" para o endereço da relação.
2. **Given** a mesma vaga depois do sorteio, **When** a página é aberta, **Then** o cartão diz
   "Sorteio realizado", com data e hora, o acesso passa a "Ver quem participou", e há "Como este
   sorteio foi feito" para a verificação.
3. **Given** uma vaga com três listas de concorrência, **When** a página é aberta, **Then** o cartão
   diz o estado uma vez e oferece um controle "Ver quem vai participar, e com que número — 3
   listas", que abre as três, a ampla concorrência primeiro.
4. **Given** uma vaga que não classifica por sorteio, ou cuja relação ainda não foi publicada,
   **When** a página é aberta, **Then** o cartão dela não tem bloco de sorteio nem frase de ausência.

### User Story 2 — Saber em que ponto está o sorteio do Edital (Priority: P2)

Quem chega à página quer saber, antes de procurar a vaga, se o sorteio já aconteceu.

**Why this priority**: é a função que a `021` deu ao bloco lateral, e ela continua — menor.

**Independent Test**: com relações publicadas, o bloco "Sorteio público" vem antes das vagas no
documento, diz o andamento em uma frase e a garantia uma vez, e não nomeia vaga nem lista.

**Acceptance Scenarios**:

1. **Given** relações publicadas e nenhum sorteio, **When** a página é aberta, **Then** o bloco diz
   "Aguardando o sorteio" e que a lista de cada sorteio fecha antes de existirem os números.
2. **Given** três relações e um sorteio realizado, **When** a página é aberta, **Then** o bloco diz
   "1 de 3 sorteios realizados".
3. **Given** nenhuma relação publicada, **When** a página é aberta, **Then** o bloco não existe.

### Edge Cases

- **Listas da mesma vaga em pontos diferentes** (uma sorteada, duas não): o cartão diz "Sorteio em
  andamento", quantas foram sorteadas, e cada linha diz o estado da sua lista.
- **Listas fechadas ou sorteadas em instantes diferentes**: a frase única não leva data; cada linha
  leva a sua.
- **Vaga com mais de um marco por sorteio**: cada marco é um grupo com o nome dele; com um marco só,
  o nome não aparece.
- **Relação de vaga que o conteúdo vigente já não lista** (retirada por Retificação): continua
  alcançável, pelo bloco do Edital.
- **Lista que o conteúdo vigente já não nomeia**: o nome é o da versão que a relação citou.
- **Relação sucedida**: não é anunciada; continua no endereço dela, como na `021`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-5150**: O cartão de uma vaga MUST apresentar o sorteio dela quando a vaga tiver ao menos uma
  relação de habilitados vigente, e MUST NOT apresentar bloco nem frase de ausência quando não tiver.
- **FR-5151**: O sorteio da vaga MUST ser agrupado por marco e, dentro do marco, por lista; o nome
  do marco MUST aparecer apenas quando a vaga tiver relação vigente em mais de um marco.
- **FR-5152**: As listas MUST vir com a ampla concorrência primeiro e as demais na ordem em que o
  Perfil as declara no conteúdo vigente; a lista que o vigente não conhece vai para o fim.
- **FR-5153**: A relação sem lista MUST ser nomeada "Ampla concorrência", que é o nome que a página
  da própria relação lhe dá; a lista que o vigente não nomeia MUST levar o nome da versão que a
  relação citou.
- **FR-5154**: O estado MUST ser dito uma vez por marco quando as listas dele estão no mesmo ponto —
  aguardando, com a data e a hora do fechamento, ou realizado, com a data e a hora do sorteio —, e
  por lista, também com data e hora, quando não estão; neste caso o marco MUST dizer quantas
  listas foram sorteadas.
- **FR-5155**: Cada lista MUST oferecer o acesso à sua relação, no endereço que já existe, com a
  quantidade de habilitados; o tempo do verbo MUST acompanhar o fato (vai participar; participou).
- **FR-5156**: Realizado o sorteio de uma lista, ela MUST oferecer também o acesso à verificação
  dele, no endereço que já existe.
- **FR-5157**: O marco com uma lista só MUST oferecer o acesso diretamente; o marco com duas ou mais
  MUST reuni-las sob um controle nativo de abrir e fechar, cujo rótulo diz o que ele abre e quantas
  listas são.
- **FR-5158**: Havendo relação vigente no Edital, a página MUST ter um bloco "Sorteio público" que
  diz o andamento do Edital inteiro em uma frase e, uma única vez, que a lista de cada sorteio é
  fechada antes de existirem os números; o bloco MUST NOT repetir vaga, lista nem acesso que já
  esteja num cartão, e MUST NOT mandar procurar no cartão quando nenhuma vaga tem sorteio a mostrar.
- **FR-5159**: O bloco do Edital MUST vir antes das vagas na ordem do documento, que é a ordem de
  leitura em tela estreita; em tela larga ele ocupa a coluna lateral, acima do Cronograma.
- **FR-5160**: A relação vigente de uma vaga que o conteúdo vigente já não lista MUST continuar
  alcançável a partir desta página, pelo bloco do Edital, com o nome da lista dela.
- **FR-5161**: A reorganização MUST NOT acrescentar consulta ao banco: o sorteio continua custando à
  página duas consultas, qualquer que seja o número de vagas, marcos e listas — inclusive quando o
  nome de uma lista precisa ser lido da versão que a relação citou.
- **FR-5162**: A feature MUST NOT criar rota, modelo, migration, estado de publicação nem regra de
  visibilidade; só o vigente é anunciado, e a tabela de participantes continua fora desta página.

### Requisitos de experiência

- **UX-400**: A 375 px de largura a página MUST NOT ter rolagem horizontal, com qualquer número de
  listas e com nomes de vaga de três linhas.
- **UX-401**: Cada acesso MUST ter nome acessível único na página: o texto oculto leva a lista, o
  marco quando houver mais de um, e a vaga.
- **UX-402**: O bloco MUST funcionar sem script e sem estilo embutido; o controle de abrir e fechar
  é o elemento nativo, o mesmo do "documentos" do cartão.

### Key Entities

Nenhuma nova. A feature lê `RelacaoDeHabilitados` e `Sorteio` como a `021` os lê, e o conteúdo
vigente do Edital.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1600**: O acesso à relação de uma vaga está dentro do cartão dela: do título da vaga até o
  acesso, a distância nunca passa da altura do próprio cartão. No Edital de referência (quatro
  vagas, nove relações), a 375 px, são 508 px — eram 2.801, fora do cartão. Num Edital real com
  atribuições, carga horária e remuneração declaradas, medido no preview, são 608 px: o bloco vem
  depois de todo o argumento da vaga, e a distância cresce com ele.
- **SC-1601**: Cada relação vigente tem exatamente um acesso na página.
- **SC-1602**: A página lê as tabelas do sorteio em duas consultas, com uma lista ou com três.
- **SC-1603**: Os seis casos que a `021` fixou para esta página continuam passando sem mudança de
  expectativa.

## Decisões

As decisões desta feature estão em [research.md](research.md), de D-001 a D-008.

## Assumptions

- As listas de um mesmo marco costumam ser fechadas e sorteadas juntas (122); o caso misto existe e
  é tratado, mas não é o que o desenho otimiza.
- O cabeçalho da página já lista as vagas com âncora (072, FR-1615); é por ele que se navega até
  uma vaga, e não pelo bloco do sorteio.

## Fora do escopo

- A seção "Resultados divulgados", que tem a mesma separação por vaga. Ela convive com os cartões
  novos sem mudança; reorganizá-la é estudo próprio.
- Qualquer bloco no cartão para outro método de classificação. A área do cartão é da classificação
  (D-007), e hoje só o sorteio tem o que dizer antes do resultado.
- As páginas da relação e da verificação do sorteio.
