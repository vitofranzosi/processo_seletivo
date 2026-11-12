# Feature Specification: Minhas atividades

**Feature Branch**: `claude/strange-williamson-c2de4b`, sobre a `main` em `18e64c8c`

**Created**: 2026-11-12

**Status**: Especificada, com plano e tarefas. As três decisões do estudo que estavam abertas foram
tomadas pelo usuário em 12/11/2026 (ver *Clarifications*). Falta só a autorização para implementar,
que é do usuário, depois de ler o [plano](plan.md).

**Input**: estudo [`doc/estudo-minhas-atividades-2026-11-12/`](../../doc/estudo-minhas-atividades-2026-11-12/README.md),
rodadas 1 a 4 e o §6a, com a validação nos cenários de treinamento. Em 12/11/2026 o usuário aprovou a
direção do estudo, em três entregas:
1. *Minhas atividades*: o que eu executo;
2. *Quem faz o quê*, no Centro: como a comissão se organiza;
3. responsabilidade por frente, sem conceder permissão: coordenar, só com evidência da comissão real.

Ele pediu para avançar com a primeira e a segunda. **Esta spec é só a primeira.**

> **Faixa de identificadores.** Esta spec abre em **FR-6851**, **SC-2271** e **UX-711**. O teto
> medido em 12/11/2026, na `main`, em todas as worktrees desta máquina e nas branches locais e
> remotas, era o requisito seis mil oitocentos e dezoito, o critério dois mil duzentos e cinquenta e
> seis e o requisito de experiência setecentos e dois. A pasta `159` é a última tomada. O intervalo até
> a abertura fica livre para specs paralelas. As decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-2806 da `104`"). Uma decisão de outra feature é citada pelo assunto e pela feature. As
> decisões do estudo são citadas pela ordem ("a 2ª decisão do estudo"), porque o estudo as numera no
> mesmo formato das decisões desta spec.

---

## Por que esta feature existe

O GPS já sabe, Edital por Edital, o que falta fazer, de quem é cada ato, por que algo espera e para
onde levar. Isso é a derivação do andamento (`127`), que o Centro de Controle mostra (`136`, `138`,
`139`) com a marca **SUA** no que é da pessoa que olha. Falta **ler junto**, para a pessoa, o que já
está marcado como seu em cada Edital.

Medido nos cenários de treinamento, a presidência tem **20 atos seus em 11 Editais**. A faixa "Ações
disponíveis para você", da Lista (`104`), mostra **zero**: ela exclui por custo justamente o trabalho
da comissão depois da publicação. Para saber o que fazer, a presidência abre os onze Editais, um por um:

> Minhas Etapas → Processo → Edital → "O que fazer agora" → ato

A página "Minhas Etapas" é o lugar escolhido: já é pessoal, já lista as comissões da pessoa e já é a
entrada da presidência na demonstração. Ela passa a se chamar **Minhas atividades** (1ª decisão do
estudo). O ganho que decide o lugar é o **custo**: na Lista, todo papel pagaria a derivação a cada
abertura; aqui paga só quem abre a própria página, e quem não preside não paga nada.

### O que esta spec cobre, e o que fica fora

**Cobre:**
- a troca do nome visível de "Minhas Etapas" para "Minhas atividades", com o mesmo endereço;
- três seções: "Para fazer agora", "Em espera nos seus Editais" e "Suas Etapas de avaliação";
- os atos da presidência nos Editais que a pessoa preside, a avaliação pelas alocações à Etapa e a
  conferência pela alocação à conferência;
- o agrupamento do mesmo ato entre Editais, a marca de base de cada linha e a nota de cobertura;
- o Edital que não pôde ser lido, dito;
- a nota da faixa da Lista apontando para a página, sem número;
- a leitura da versão vigente uma vez por Edital na requisição, que pode ser um segundo incremento.

**Fica fora:**
- a formalização (7ª decisão do estudo: fica fora, dito na página);
- o que é da pessoa só por papel na unidade: publicar o resultado e julgar recursos, inclusive nos
  Editais que ela preside (D-004);
- "Quem faz o quê" no Centro: é a segunda entrega, com spec própria;
- a responsabilidade por frente: é a terceira entrega, só com evidência da comissão real;
- prazo, tarefa persistida, contador na barra lateral e página nova (4ª decisão do estudo);
- o pouso do login institucional, que continua na Lista (6ª decisão do estudo);
- os atos que hoje são só acesso, e não providência: a publicação das inscrições (`148`) e das
  convocações (`149`), os avisos (`066`), o Requerimento de Matrícula e o encerramento.

## Clarifications

### Session 2026-11-12 (decisões do estudo aceitas pelo usuário)

- Q: Onde mora a visão pessoal? → A: **Em "Minhas Etapas", renomeada "Minhas atividades", no mesmo
  endereço** (1ª decisão do estudo, revista na rodada 2). Na Lista, a faixa da `104` continua, sem
  número, e aponta para a página.
- Q: O que a permissão sistêmica de gerir comissões põe na lista do Gestor? → A: **Nada.** O Gestor não
  vê a condução como sua; o Centro de cada Edital continua mostrando-a (2ª decisão do estudo). A rodada
  3 a realiza pela escolha dos Editais por presidência (D-002).
- Q: Distribuir a condução entre membros? → A: **Não agora.** Nenhuma designação nova; a primeira
  entrega lê só as alocações que já existem (3ª decisão do estudo). A responsabilidade sem base é a
  terceira entrega.
- Q: Mostrar prazo da comissão? → A: **Não.** A data da derivação é o fim de uma espera, e não um
  prazo de quem age; "atrasado" não entra em entrega nenhuma (4ª decisão do estudo e §6a da rodada 4).
- Q: O GPS diz "feito" para trabalho fora dele? → A: **Não.** Só o que ele observa: um ato praticado
  no GPS aparece como feito porque a derivação o lê (§6a da rodada 4).
- Q: A visão vale como norte? → A: **Sim**: gestão operacional orientada do processo seletivo, em três
  entregas (9ª decisão do estudo).

- Q: Para onde vai quem entra pelo login institucional (6ª decisão do estudo)? → A: **"Lista, como
  hoje".** O pouso não muda; a nota da faixa da Lista aponta para a página (FR-6881). Era a sugestão do
  estudo: mudar a entrada custa um clique por dia a quem só consulta (a decisão de entrada da `104`), e
  pousar quem tem vínculo em "Minhas atividades" fica para depois de medir com a comissão real.
- Q: A formalização entra nesta entrega (7ª decisão do estudo)? → A: **"Fica fora, dito na página".**
  A família inteira, inclusive o que é da presidência (definir os documentos, designar), fica fora, e
  a nota de cobertura a nomeia, com o lugar dela ("Formalização", na barra) (FR-6872). A pessoa
  designada para o setor sem integrar a comissão não tem linha aqui.
- Q: Como a página trata quem preside muitos Editais (8ª decisão do estudo)? → A: **"Uma requisição,
  teto por Edital".** A página carrega tudo numa requisição, sem carregamento por Edital depois da
  primeira tela, e o teste fixa o custo **por Edital presidido** (FR-6878). Se a comissão real
  presidir dezenas de Editais ao mesmo tempo, o carregamento por bloco volta como decisão nova.
- Q: Até onde vai esta rodada? → A: **"Até tasks e analyze, sem implementar".**

## User Scenarios & Testing *(mandatory)*

### User Story 1 — A presidência vê o que é dela em todos os Editais (Priority: P1)

A presidente de onze comissões abre "Minhas atividades". Em "Para fazer agora" ela lê os atos que são
dela em cada Edital, com o mesmo texto do Centro: "Conferir os documentos de 3 convocações", "Convocar 3
titulares", "Congelar a relação". Cada linha diz o Edital, o Perfil e a lista, diz por que o ato é
dela ("Presidência") e leva ao ponto exato da tela do ato. O mesmo ato em sete Editais é uma linha só,
com os sete.

**Why this priority**: é a pessoa com mais trabalho, e hoje a faixa da Lista não mostra nada dela.

**Independent Test**: nos cenários de treinamento, com a identidade da presidência, a página lista
cada ato que o Centro de cada Edital marca como SUA, sem abrir Edital nenhum, e o primeiro link leva
à tela que oferece o ato.

**Acceptance Scenarios**:

1. **Given** a presidência de onze Editais publicados com atos seus, **When** ela abre a página,
   **Then** "Para fazer agora" tem uma linha por ato (ou grupo de atos iguais), com o texto, o lugar,
   a marca "Presidência" e o link de cada célula SUA do Centro daquele Edital.
2. **Given** o mesmo ato "Emitir a ordem que declara que ninguém concorreu nesta lista" em sete
   Editais, **When** a página é lida, **Then** ele é uma linha só, que diz "7 Editais" e abre a lista
   dos sete, cada um com o seu link.
3. **Given** um ato praticado no Centro ou na tela do ato, **When** a página é aberta de novo, **Then**
   a linha não está mais lá, sem ação nenhuma na página.
4. **Given** um Edital presidido cuja leitura falha, **When** a página é aberta, **Then** ela diz que
   aquele Edital não pôde ser lido agora, com o link para ele, e nunca diz "nada para fazer" sem
   nomeá-lo.

---

### User Story 2 — O avaliador vê o que avaliar, e a página não paga a derivação por ele (Priority: P1)

O avaliador é membro de onze comissões e está alocado a 27 Etapas. Ele abre "Minhas atividades" e lê
"Avaliar 5 inscrições · Edital SIM05/2026 · Prova objetiva", com "Abrir a mesa". Abaixo, os cartões de
hoje, com o medidor de quanto falta. A página não roda a derivação do andamento em Edital nenhum para
ele.

**Why this priority**: é o papel mais numeroso. Sem a redução, a página custaria a ele ~1700 consultas
para achar um item.

**Independent Test**: com a identidade de um membro que não preside nem está alocado à conferência, a
página mostra a avaliação pendente e o número de consultas não depende de quantas comissões ele
integra.

**Acceptance Scenarios**:

1. **Given** um membro alocado com inscrições pendentes numa Etapa, **When** ele abre a página,
   **Then** "Para fazer agora" tem "Avaliar N inscrições" com a marca "Alocação" e o link da Mesa, e
   o texto é o mesmo da célula de avaliação do Centro daquele Edital.
2. **Given** o mesmo membro em onze ou em uma comissão, **When** a página é aberta, **Then** o número
   de consultas é o mesmo, e a derivação do andamento não é chamada.
3. **Given** um membro sem inscrição pendente, **When** ele abre a página, **Then** ela diz que nada
   depende dele agora **no que ela cobre**, e a nota de cobertura diz o que fica de fora.

---

### User Story 3 — O Gestor que preside vê o dele; o que não preside, não (Priority: P1)

O Gestor tem a permissão sistêmica de gerir comissões, e por ela pode intervir em toda comissão da
unidade. Isso não faz da condução de todos os Editais trabalho dele. Na página, ele vê só os atos dos
Editais que **preside**, com a marca "Presidência". Nos outros, a página não mostra condução nenhuma, e
a nota de cobertura diz que o que ele pode fazer por permissão de gestão fica no Centro de cada Edital.

**Why this priority**: sem isso, a lista do Gestor vira o inventário da unidade (22 atos em 12
Editais, medido), e o Gestor que também preside perderia o trabalho dele, porque a base de autorização
devolvida a ele é a sistêmica, e não a presidência.

**Independent Test**: dois Gestores, um que preside um dos Processos e outro que não preside nenhum;
o primeiro vê os atos daquele Processo, e o segundo não vê ato de condução nenhum.

**Acceptance Scenarios**:

1. **Given** um Gestor que preside um Processo, **When** ele abre a página, **Then** vê os atos de
   condução dos Editais desse Processo, com a marca "Presidência", e nenhum dos outros Processos.
2. **Given** um Gestor que não preside nada, **When** ele abre a página, **Then** não vê ato de
   condução nenhum, e a derivação não roda em Edital nenhum por causa da permissão sistêmica.
3. **Given** um Gestor alocado à conferência de um Perfil, sem presidir, **When** ele abre a página,
   **Then** vê só a conferência dos documentos daquele Perfil, e nenhum outro ato do Edital.

---

### User Story 4 — O que espera, dito pelo que é (Priority: P2)

Nos Editais que preside, a presidência vê, recolhido, o que espera o mundo: a resposta do candidato,
o fim do prazo de recurso, a extração da loteria. Cada espera diz de onde vem a data: "o prazo de
recurso aberto pela publicação corre até 17/11", "o prazo do candidato corre até 12/12". Nunca "seu
prazo", nunca "atrasado".

**Why this priority**: a espera explica por que algo não está em "Para fazer", mas não é ação; aberta,
ela pesaria como trabalho.

**Independent Test**: num Edital com o prazo de recurso em curso, a seção recolhida tem a espera com a
data e a origem dela; "Para fazer agora" não a tem.

**Acceptance Scenarios**:

1. **Given** cinco Editais com o resultado definitivo esperando o prazo de recurso, **When** a
   presidência abre a seção, **Then** lê uma linha que agrupa os cinco, com a data e a frase da
   derivação.
2. **Given** uma célula *Impedido* num Edital presidido, **When** a página é lida, **Then** ela
   aparece nesta seção, com a razão da derivação e quem a resolve, e nunca em "Para fazer agora".

---

### User Story 5 — O nome muda, e o caminho continua (Priority: P2)

A barra lateral, o título da página, a trilha e a trilha da Mesa dizem "Minhas atividades". Quem tem
o endereço antigo salvo, os links da Mesa e o pouso da demonstração continuam funcionando, porque o
endereço é o mesmo.

**Independent Test**: nenhuma tela da gestão diz "Minhas Etapas"; `/gestao/minhas-etapas` responde a
página; a Mesa de uma Etapa diz "Minhas atividades › …" na trilha.

**Acceptance Scenarios**:

1. **Given** qualquer identidade, **When** ela abre a gestão, **Then** a barra diz "Minhas
   atividades", no mesmo grupo e com o mesmo ícone.
2. **Given** a Mesa de uma Etapa, **When** o avaliador a abre, **Then** a trilha diz "Minhas atividades"
   e leva ao mesmo endereço de hoje.

---

### User Story 6 — Na Lista, a faixa aponta para a página (Priority: P3)

A faixa "Ações disponíveis para você" continua como está, com os itens que ela já deriva barato. A
nota de cobertura deixa de mandar a presidência "ao detalhe de cada Edital" e aponta para "Minhas
atividades". A faixa não ganha número de atividades.

**Independent Test**: a nota da faixa, com itens e vazia, tem o link para a página; o número de
consultas da Lista continua o mesmo.

**Acceptance Scenarios**:

1. **Given** a presidência na Lista, **When** a faixa está vazia, **Then** a frase vazia diz que os
   atos de quem preside ou está alocado estão em "Minhas atividades", com o link, e que o restante
   fica no detalhe de cada Edital.
2. **Given** a Lista com qualquer número de Editais, **Then** a faixa não mostra contagem de
   atividades da página, e a Lista não roda a derivação do andamento.

### Edge Cases

- **A pessoa preside e está alocada à conferência no mesmo Edital.** A linha é uma só, com a marca
  "Presidência": a conferência já é dela pela presidência.
- **A presidência também avalia.** A avaliação aparece uma vez, com a marca "Alocação", e o cartão da
  Etapa continua na terceira seção.
- **Processo encerrado ou cancelado.** Nenhum ato da comissão é aceito, e nada dele é seu: o Processo
  não é lido.
- **Edital ainda não publicado num Processo presidido.** Não é lido. O trabalho dele é da elaboração,
  que a faixa da Lista já mostra a quem elabora, homologa ou publica.
- **Vínculo inativo.** A comissão de que a pessoa saiu não conta, nem como presidência nem como
  alocação.
- **Outra unidade.** Só as comissões do escopo da identidade, como hoje.
- **Retificação em curso.** Não vira linha: é trabalho sobre o documento, e a Lista já a mostra (a
  decisão de Retificação da `127`). A derivação relê a versão vigente, e o que a Retificação tornou
  obsoleto aparece como *Obsoleto*.
- **Espera sem data.** É dita sem data, pela frase da derivação, e não com data inventada.
- **Todos os Editais presididos falham na leitura.** A página diz quantos e quais, e não diz "nada
  para fazer".
- **O mesmo ato com contagem** ("Convocar 3 titulares" e "Convocar 2 titulares", ou "Convocar 3
  titulares" em dois Editais). São linhas diferentes: só se junta o ato sem número, como no Centro.
- **Avaliação numa Etapa com inscrição sem avaliador suficiente.** O Centro pode dizer "Avaliar 3"
  onde a Mesa da pessoa tem 5, porque desconta o que ainda depende da distribuição. A linha diz 5, o
  número da Mesa a que ela leva (D-010).
- **A fase Conclusão.** O encerramento nunca é linha: a derivação não diz "pode encerrar", de
  propósito.
- **Membro que só integra comissões, sem alocação nem presidência.** A página diz que nada depende
  dele agora no que ela cobre, e continua listando as comissões que ele integra.
- **Pessoa sem papel, sem vínculo e sem alocação.** Continua a orientação de hoje, para quem não tem
  nada (a FR-028 da `002`).

## Requirements *(mandatory)*

### Functional Requirements

#### A. O nome e o endereço

- **FR-6851**: O nome visível de "Minhas Etapas" MUST passar a ser **"Minhas atividades"** na barra
  lateral, no título da página, no título da janela, na trilha da página, na trilha da Etapa e na
  trilha da Mesa, e em toda frase de interface que nomeie a página.
- **FR-6852**: O endereço `/gestao/minhas-etapas`, o nome da rota e as rotas da Mesa que pendem dele
  MUST NOT mudar. A seção ativa da barra para a Etapa aberta pela gestão (a FR-1752 da `077`), o pouso
  da demonstração e o link "Ver minhas atribuições" da Lista MUST continuar levando à mesma página.
- **FR-6853**: O guia da equipe dos cenários de treinamento e o manual MUST passar a dizer "Minhas
  atividades". As specs e os estudos anteriores MUST NOT ser reescritos: são registro.

#### B. Quais Editais a página lê

- **FR-6854**: Os Editais de condução MUST ser escolhidos pela **presidência lida no vínculo ativo de
  comissão** da pessoa, e MUST NOT ser escolhidos pela base de autorização de gerir comissões, que
  devolve a permissão sistêmica antes da presidência (D-002).
- **FR-6855**: A página MUST ler, para condução, só os Editais publicados (ou encerrados) dos Processos
  ativos que a pessoa preside. Processo encerrado ou cancelado e Edital não publicado MUST NOT ser
  lidos.
- **FR-6856**: Para quem não preside, a derivação do andamento MUST NOT rodar em Edital nenhum por
  causa da avaliação. A avaliação MUST sair da mesma conta de carga que a página já faz (D-003).
- **FR-6857**: A conferência dos documentos MUST entrar quando houver alocação ativa à conferência:
  a página lê os Editais em que a pessoa está alocada à conferência e, neles, só a conferência dos
  Perfis que a alocação alcança, ainda que a pessoa tenha a permissão sistêmica.
- **FR-6858**: A página MUST NOT ler Edital em que a pessoa não preside nem está alocada à
  conferência, qualquer que seja a permissão sistêmica dela.

#### C. As linhas: uma fonte só

- **FR-6859**: Toda linha de "Para fazer agora" MUST ser uma célula que o Centro de Controle daquele
  Edital mostra com a marca SUA à mesma pessoa, no mesmo instante, com o mesmo ato, o mesmo lugar e o
  mesmo link com âncora (D-005). A página MUST NOT escrever frase própria para um ato da derivação.
- **FR-6860**: Toda célula SUA do Centro cuja base seja a presidência ou uma alocação MUST ter linha
  na página (sozinha ou dentro de um grupo), nos Editais que a página lê, exceto as famílias que a
  nota de cobertura nomeia como fora.
- **FR-6861**: Toda linha MUST dizer **por que é da pessoa**: "Presidência" ou "Alocação". A marca é
  texto, e não só cor nem ícone.
- **FR-6862**: Nos Editais que a pessoa preside, o que é dela só por papel na unidade (publicar o
  resultado, julgar recursos) MUST NOT entrar em "Para fazer agora", e a nota de cobertura MUST
  dizê-lo (D-004).
- **FR-6863**: "Para fazer agora" MUST ter só o que a pessoa pode praticar agora (*Pendente* e
  *Obsoleto*). Nenhuma linha que ela não possa executar MUST entrar nessa seção.
- **FR-6864**: A avaliação MUST aparecer uma vez por Etapa, com a frase da célula de avaliação do
  Centro ("Avaliar N inscrições"), a marca "Alocação" e o link da Mesa, pelo caminho que for (com
  ou sem a derivação). O N MUST ser o da Mesa, o mesmo do cartão da Etapa e da faixa da `104`
  (D-010).

#### D. Ordem e agrupamento

- **FR-6865**: O mesmo ato, com o mesmo texto **sem contagem**, em vários Editais MUST ser **uma
  linha**, que diz quantos Editais e abre a lista deles, cada um com o seu link (D-006). O ato cujo
  texto tem número ("Convocar 3 titulares") MUST NOT se juntar, nem com o mesmo número: é a regra com
  que o Centro já agrupa dentro de um Edital.
- **FR-6866**: A ordem MUST ser: primeiro o *Obsoleto*, depois o *Pendente*; dentro de cada um, o
  Edital mais antigo primeiro e, no mesmo Edital, a ordem em que a derivação emite as células (a do
  Perfil e a da jornada). A data da derivação MUST NOT ordenar a lista, embora o nível 1 do Centro
  ponha à frente, entre as suas, as que têm data (D-007).
- **FR-6867**: Toda linha MUST levar o nome da fase do Centro a que o ato pertence, pela mesma
  classificação de fases do Centro, sem taxonomia nova.

#### E. As esperas

- **FR-6868**: "Em espera nos seus Editais" MUST ter as células *Aguarda* e *Impedido* dos Editais que
  a pessoa preside, qualquer que seja o papel de quem age depois da espera (o resultado definitivo que
  espera o prazo de recurso entra), com a frase e a razão da derivação. Nos Editais lidos só pela alocação à
  conferência, a seção MUST NOT mostrar espera.
- **FR-6869**: A data de uma espera MUST ser dita pelo que ela é, com a origem: "o prazo de recurso
  aberto pela publicação corre até …", "o prazo do candidato corre até …", "a extração da loteria é
  em …". Uma data MUST NOT ser chamada de prazo da pessoa, e nenhuma linha da página MUST dizer
  "atrasado" (D-007).
- **FR-6870**: As esperas com o mesmo ato e a mesma razão, **inclusive a mesma data**, MUST se agrupar
  entre Editais numa linha, como na FR-6865. A data não impede a junção; a contagem no ato impede.
  Esperas com datas diferentes são linhas diferentes.

#### F. Cobertura e falha

- **FR-6871**: A página MUST ter uma nota de cobertura que diz o que ela reúne (os atos da presidência
  nos Editais que a pessoa preside, a avaliação e a conferência pelas alocações) e o que fica fora, com
  onde está cada coisa.
- **FR-6872**: A nota MUST nomear como fora, enquanto não entrarem: a formalização, que tem lista
  própria (7ª decisão do estudo); publicar o resultado e julgar recursos; os atos de
  Edital e de Retificação, que estão na Lista; a publicação das inscrições e das convocações; os avisos
  aos candidatos; o Requerimento de Matrícula; e o encerramento. Ao Gestor, ela MUST dizer que o que
  ele pode fazer por permissão de gestão fica no Centro de cada Edital.
- **FR-6873**: Sem linha em "Para fazer agora", a página MUST dizer que nada depende da pessoa agora
  **no que esta página cobre**, e MUST NOT dizer que ela não tem nada a fazer no GPS.
- **FR-6874**: O Edital cuja leitura falhou MUST ser dito na página ("1 Edital não pôde ser lido
  agora"), com o link para ele. A falha MUST NOT virar silêncio nem "nada para fazer", e MUST NOT
  derrubar a página.

#### G. A página

- **FR-6875**: A página MUST ter três seções, nesta ordem: "Para fazer agora", aberta; "Em espera nos
  seus Editais", recolhida; e "Suas Etapas de avaliação", com os cartões de hoje (medidor, "Abrir" e o
  estado de alocação sem distribuição). O bloco "Comissões que você integra" MUST continuar, depois
  das três.
- **FR-6876**: Os estados vazios MUST falar com quem lê: quem preside e não avalia lê que presidir não
  atribui avaliação; quem não tem papel, vínculo nem alocação lê a orientação de hoje. O texto da
  FR-2827 da `104` MUST ser revisto para dizer o que a página passa a cobrir.

#### H. O custo

- **FR-6877**: Para quem não preside nem está alocado à conferência, o número de consultas da página
  MUST NOT crescer com o número de comissões ou de Editais da pessoa.
- **FR-6878**: Para quem preside, o número de consultas MUST crescer, no máximo, linearmente com o
  número de Editais presididos lidos, com um teto **por Edital** fixado no plano a partir da medição
  (no molde de `test_andamento_em_escala.py`). A página carrega numa requisição só, sem teto de
  Editais presididos e sem carregamento por Edital (8ª decisão do estudo).
- **FR-6879**: A versão vigente de um Edital MUST ser lida **uma vez por requisição**, e reaproveitada
  pelas leituras da derivação daquele Edital, sem estado entre requisições (D-009). Este requisito pode
  sair num segundo incremento; quando sair, MUST valer também para o Centro de Controle, sem mudar
  item nenhum.

#### I. A Lista

- **FR-6880**: A faixa "Ações disponíveis para você" MUST continuar com os itens que já deriva, e MUST
  NOT ganhar contagem nem item de "Minhas atividades" (D-008).
- **FR-6881**: A nota de cobertura da faixa (a constante de famílias fora, que a frase vazia também
  lê, pelas FR-4324 e FR-4325 da `129`) MUST apontar para "Minhas atividades", com o link, para o que
  é da presidência ou de alocação, e MUST continuar apontando para o detalhe de cada Edital o que a
  página não cobre. Ela MUST NOT prometer na página o que a página não mostra.
- **FR-6882**: O custo da Lista MUST continuar o da FR-2806 da `104`: a Lista MUST NOT rodar a
  derivação do andamento.

#### J. O que se preserva para as próximas entregas

- **FR-6883**: As seções MUST ser nomeadas pela relação da pessoa com o trabalho ("para fazer", "em
  espera"), e não pela natureza do ato, para que a terceira entrega acrescente "Para acompanhar" sem
  mudar as existentes.
- **FR-6884**: A página MUST NOT gravar nada: nem tarefa, nem estado, nem marca de visto. Ela MUST NOT
  conceder nem verificar permissão nova: o link leva à tela do ato, que verifica pela porta de sempre.

### Requisitos de experiência

- **UX-711**: A contagem MUST ir no título de cada seção ("Para fazer agora · 20 atos em 11 Editais"),
  e MUST NOT haver contadores soltos no alto da página nem abas.
- **UX-712**: "Em espera nos seus Editais" MUST ser recolhida por elemento nativo, sem script, e o
  título dela MUST dizer quantas esperas há.
- **UX-713**: Cada linha MUST ter o ato como texto principal, e o Edital, o lugar, a fase e a marca de
  base como texto secundário, nessa ordem. O botão MUST usar o verbo da tela de destino.
- **UX-714**: A 375 px, a página MUST caber sem rolagem horizontal, e "Para fazer agora" MUST começar
  na primeira tela.
- **UX-715**: O sinal de situação (●, ↺, ◷, ⊘) MUST ser o do Centro, e MUST vir acompanhado da palavra:
  a situação não é dita só por símbolo nem por cor.

### Key Entities

Nenhuma entidade nova, nenhuma tabela, nenhuma migration. A página lê:
- **Vínculo de comissão** (`MembroComissao`): a presidência escolhe os Editais de condução.
- **Alocação à Etapa e atribuição**: a avaliação, pela carga.
- **Alocação à conferência** (`115`): a conferência, pelo Perfil que ela alcança.
- **Providência** (`127`): a célula do andamento, com o ato, a situação, o lugar, o link e a marca
  SUA. A linha da página é uma providência, ou um grupo de providências iguais, e não existe fora da
  leitura.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2271**: **Coerência com o Centro**, que estende o SC-1230 da `127`: nos cenários de
  treinamento, para a presidência, o avaliador, o Gestor que preside, o Gestor que não preside e um
  membro alocado à conferência, 100% das linhas de "Para fazer agora" são células SUA do Centro
  daquele Edital, com o mesmo texto e o mesmo link (a avaliação, pela D-010); e 100% das células SUA
  de base presidência ou alocação estão na página, sozinhas ou num grupo.
- **SC-2272**: **Quem só é membro não dispara a derivação**: para um membro sem presidência nem
  alocação à conferência, a página não chama a derivação do andamento, e o número de consultas é o
  mesmo com 1 e com 11 comissões.
- **SC-2273**: **O Gestor**: o Gestor que preside um Processo vê os atos de condução dos Editais
  desse Processo com a marca "Presidência"; o Gestor que não preside nada vê zero atos de condução, e
  a derivação não roda em Edital nenhum para ele.
- **SC-2274**: **Teto por Edital presidido**: o número de consultas da página da presidência é a base
  da página mais, no máximo, o teto do plano vezes o número de Editais presididos lidos, verificado
  com dois tamanhos de escopo.
- **SC-2275**: **Agrupamento**: nos cenários de treinamento, cada ato repetido com o mesmo texto em N
  Editais é uma linha só com N Editais; a presidência lê os seus atos em menos linhas do que atos.
- **SC-2276**: **Falha dita**: com a leitura de um Edital presidido forçada a falhar, a página nomeia
  esse Edital, os demais continuam listados, e a frase de "nada para fazer" não aparece se nenhum
  outro tiver ato.
- **SC-2277**: **Espera com origem**: toda data da seção "Em espera" vem com a origem dela, e nenhuma
  tela da página diz "atrasado" nem "seu prazo".
- **SC-2278**: **Nome**: nenhuma tela da gestão diz "Minhas Etapas"; o endereço `/gestao/minhas-etapas`
  e as rotas da Mesa respondem como antes.
- **SC-2279**: **Lista**: a nota da faixa, com itens e vazia, tem o link para "Minhas atividades"; a
  faixa não tem contagem da página; o teste de custo da Lista passa sem mudar o orçamento.
- **SC-2280**: **Versão vigente uma vez**: com a FR-6879 implementada, a versão vigente de cada Edital
  é lida uma vez por requisição, os itens da página e do Centro são os mesmos de antes, e o custo da
  presidência cai (o estudo mediu cerca de 19%).
- **SC-2281**: **Validação com pessoas**, humana e pendente: com os cenários de treinamento e,
  quando houver, a comissão real, a tarefa "sem abrir nenhum Edital, diga o que você tem a fazer e faça
  o primeiro" é cumprida mais depressa que pelo percurso de hoje, medida pelo método de tarefas do
  estudo do Centro de Controle.

## Assumptions

- **A derivação da `127` não muda.** A página filtra e agrupa o que ela emite; nenhuma regra de "sua"
  é reescrita. Se a coerência falhar, o defeito é da página.
- **As bases de vínculo hoje são três**: presidência, alocação à Etapa e alocação à conferência. O
  membro que não preside só pratica avaliar e conferir. A designação para a formalização é a quarta,
  e fica fora desta entrega (7ª decisão do estudo).
- **Equipe inicial de 2–3 pessoas, acumulando papéis.** O ganho está quase todo na presidência.
- **O custo medido é a referência do plano**: cerca de 80 consultas por Edital presidido sem a
  FR-6879 e cerca de 65 com ela, nos cenários de treinamento; para o membro, de ~1700 para ~56.
- **Os cenários de treinamento não usam alocação à conferência nem designação para a formalização.**
  Os testes desses casos montam o próprio cenário.

## Decisões

### D-001 — "Minhas Etapas" vira "Minhas atividades", e só o nome visível muda

Revê a decisão da `104` de não renomear "Minhas Etapas", e a FR-2828 da `104`, que mantinha a função
da página: ela passa a reunir o trabalho, e não só a avaliação. Respeita a decisão de entrada da
`104`: nenhuma página nova. O endereço fica porque as rotas da Mesa pendem dele, de propósito, e
porque 28 arquivos de teste, o pouso da demonstração e o link da Lista o usam. "Atividade" não colide
com termo nenhum da gestão.

### D-002 — Os Editais de condução vêm da presidência no vínculo, e não da base de autorização

A base de gerir comissões verifica a permissão sistêmica antes da presidência, e devolve a sistêmica
ao Gestor que também preside. Escolher os Editais por ela daria ao Gestor a unidade inteira, ou tiraria
dele o que é dele. Lida no vínculo, a presidência resolve as duas coisas, e realiza a 2ª decisão do
estudo sem mudar o `Alcance` da `127`: nos Editais que a pessoa preside, todo ato de condução é dela
por vínculo.

### D-003 — Quem não preside não paga a derivação

Fora da presidência, só três coisas podem ser da pessoa: avaliar, conferir e a formalização. Avaliar
sai da carga que a página já calcula; conferir, só onde há alocação à conferência. O avaliador dos
cenários cai de ~1700 consultas para ~56, com o mesmo item.

### D-004 — Só as bases de vínculo, mesmo nos Editais presididos

A presidente que também publica resultado veria "Publicar o resultado" nos Editais que preside, e não
nos outros onde é igualmente a Publicadora. Uma cobertura parcial de um papel da unidade ensina a
pessoa a confiar numa lista incompleta. O papel da unidade inteira é outro incremento (o caso caro do
estudo, sem fronteira de comissão), e até lá a nota de cobertura diz que ele fica fora.

### D-005 — Uma fonte só: a linha é a célula

A página não tem regra própria. O teste de coerência é a guarda: uma página que escrevesse frases
próprias para os mesmos atos voltaria a ter duas fontes, e divergiria na primeira mudança.

### D-006 — O mesmo ato agrupa entre Editais

Nos cenários, sete "ordens de lista vazia" escondiam a convocação. O agrupamento da `127` vale dentro
de um Edital; aqui vale entre Editais, pelo mesmo ato e o mesmo texto.

### D-007 — A data é o fim de uma espera, e não um prazo

A derivação tem o fim das inscrições, a extração, o fim do prazo de recurso e o prazo do candidato.
Nenhuma é prazo da comissão. Ordenar por elas misturaria quatro significados, e chamar qualquer uma de
prazo inventaria um atraso. A Agenda (`101`) mostra o prazo de recurso do cronograma, e esta página o
aberto pela publicação; por isso a frase diz a origem, e as duas não se contradizem.

### D-008 — A Lista fica sem número

"Você tem 12 atividades" na Lista custaria a derivação inteira na página de todos, e desfaria a razão
de a visão morar fora dela.

### D-009 — Reler dentro da requisição não é cache

A versão vigente é relida cerca de 25 vezes por Edital, por funções de outras features. Lê-la uma vez
por requisição não cria estado, e por isso não é a segunda fonte de verdade que um cache entre
requisições seria. Rende cerca de 19% para a presidência, e vale também para o Centro.

### D-010 — A avaliação conta pela Mesa

Na célula de avaliação, o Centro limita o número às inscrições que não dependem mais da distribuição.
Numa Etapa com inscrição sem avaliador suficiente, isso pode dar menos do que a Mesa da pessoa
mostra. Reproduzir o limite fora da derivação exigiria ler o resumo de cada Etapa alocada, e desfaria
a D-003. A linha leva à Mesa e diz o número dela, o mesmo do cartão e da faixa da `104`. O teste de
coerência compara a Etapa e o link sempre, e o número onde a Etapa não tem inscrição sem avaliador
suficiente.
