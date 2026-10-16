# Feature Specification: A entrada da gestão

**Feature Branch**: `claude/redesign-acesso-entrada-f8c894`, sobre a `main` `6fc3a85a`

**Created**: 2026-10-16

**Status**: Implementada — validação com o setor pendente

**Input**: etapa 1 do [estudo da entrada na gestão](../../doc/estudo-acesso-a-gestao-2026-10-16.md),
com o conceito A (Institucional) escolhido pelo responsável pelo produto em 16/10/2026 — *"siga para
etapa 1, caminho A"* —, mais a busca do conceito B sobre a lista de identidades. Duas decisões do
responsável pelo produto, no mesmo dia: o link da gestão no portal só aparece onde existe método de
entrada, e o produto passa a se chamar **Gestão de Processos Seletivos (GPS)**.

> **Faixa de identificadores.** Esta spec abre em FR-1690 e SC-650, acima da faixa da `074`.

---

## Por que esta feature existe

A gestão está escondida. A raiz leva ao portal, o portal só oferece "Entrar" — que é do candidato —,
e quem gere precisa saber de cor o endereço `/gestao/`. Quando chega, encontra uma tela técnica:
um campo de nome, oito caixas de seleção e, ao lado de cada papel, os códigos internos de permissão.
Depois de identificar-se, cai sempre na lista de Processos, mesmo que tenha aberto o link de um
Edital: são 90 pontos que mandam para a identificação, e nenhum guarda o destino.

O estudo de 16/10 mapeou isso, propôs três direções e prototipou as três. Esta feature implementa a
escolhida **só na entrada**: a página de acesso, a escolha de identidades de demonstração, o retorno
ao destino, a saída e a porta no portal. As telas operacionais da gestão não mudam.

**O que não muda, e não se negocia aqui:** nenhuma regra de negócio, permissão ou semântica de
papel. Presidir e avaliar continuam vindo do vínculo com a comissão, conferido objeto a objeto. A
demonstração continua existindo só onde o seletor de identidade está ligado, e produção continua
recusando subir com ele. A autenticação institucional não é implementada.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Quem gere encontra a gestão pelo portal e entra (Priority: P1)

Uma pessoa da equipe abre o endereço do sistema, vê no cabeçalho do portal "Área de gestão" ao lado
de "Minhas inscrições", clica, e chega a uma página que apresenta o produto e oferece um caminho
para entrar. No desenvolvimento, esse caminho é o ambiente de demonstração.

**Why this priority**: é o problema que motivou a feature — a gestão não tem porta.

**Independent Test**: com o seletor ligado, a vitrine traz os dois acessos; o de gestão leva à página
de acesso; a página de acesso leva à escolha de identidades.

**Acceptance Scenarios**:

1. **Given** o seletor ligado, **When** alguém abre a vitrine, **Then** o cabeçalho traz "Minhas
   inscrições" e "Área de gestão", e o nome "Gestão de Processos Seletivos".
2. **Given** a página de acesso, **When** ela é aberta, **Then** mostra o nome do produto, a frase
   de apresentação, o ciclo do certame, "Bem-vindo à gestão", o selo de ambiente de demonstração e
   uma ação para acessar o ambiente de demonstração.
3. **Given** um candidato que chegou à página de acesso por engano, **When** ele a lê, **Then**
   encontra o caminho para as próprias inscrições no portal.

---

### User Story 2 — A escolha de identidade é compreensível (Priority: P1)

Quem entra na demonstração vê as identidades agrupadas: as que têm vínculo com comissão — com a
responsabilidade (presidência, avaliação), o Processo e as Etapas atribuídas — e as
responsabilidades da unidade, cada uma com uma frase do que faz. Escolhe uma e entra. Quem precisa
de uma combinação que nenhuma entrada pronta oferece abre as opções avançadas, informa um nome e
marca as responsabilidades.

**Why this priority**: sem isso a página nova seria a tela técnica com outra roupa.

**Independent Test**: a página de escolha lista as identidades do banco e nenhum código de
permissão; escolher uma identifica com o nome e as responsabilidades daquela entrada.

**Acceptance Scenarios**:

1. **Given** um ambiente com uma pessoa que preside a comissão de um Processo, **When** a escolha é
   aberta, **Then** ela aparece em *Comissões*, como presidência, com o código do Processo.
2. **Given** a escolha aberta, **When** alguém entra pela presidência, **Then** a sessão não recebe
   papel nenhum — a presidência continua vindo do vínculo.
3. **Given** a escolha aberta, **When** alguém entra por "Gestor", **Then** a sessão recebe o papel
   Gestor e só ele.
4. **Given** as opções avançadas, **When** o envio vem sem nome, **Then** a página volta com a
   recusa visível junto do campo, as opções abertas e o foco no campo.
5. **Given** mais de oito identidades na lista, **When** a pessoa digita no campo de busca, **Then**
   a lista mostra só as que correspondem; sem script, a lista inteira continua disponível.

---

### User Story 3 — O link aberto volta ao seu destino (Priority: P2)

Alguém recebe o link de um Edital e o abre sem estar identificado. Passa pela página de acesso,
escolhe a identidade e chega ao Edital — e não à lista de Processos.

**Why this priority**: é a mudança de maior efeito prático depois da porta, e é invisível até faltar.

**Independent Test**: abrir uma página protegida sem identidade leva ao acesso com o destino;
identificar-se leva ao destino; um destino de outro site é ignorado.

**Acceptance Scenarios**:

1. **Given** nenhuma identidade, **When** alguém abre uma página da gestão, **Then** é levado à
   página de acesso com aquele endereço como destino.
2. **Given** um destino na própria gestão, **When** a pessoa se identifica, **Then** vai ao destino.
3. **Given** um destino em outro domínio, ou fora da gestão, **When** a pessoa se identifica,
   **Then** vai ao lugar padrão de hoje — a lista com papel, Minhas Etapas sem papel.

---

### User Story 4 — Sem método de entrada, a página diz isso (Priority: P2)

Em produção, enquanto a autenticação institucional não existir, não há como entrar. A página de
acesso diz que a entrada ainda não está configurada, com o mesmo desenho, e o portal não oferece a
porta.

**Independent Test**: com o seletor desligado, a página de acesso responde 503 com a mensagem de
entrada não configurada, a escolha de identidades não existe e a vitrine não traz "Área de gestão".

**Acceptance Scenarios**:

1. **Given** o seletor desligado, **When** alguém abre a página de acesso, **Then** ela responde 503
   e explica que a entrada não está configurada, sem nenhuma ação de entrar.
2. **Given** o seletor desligado, **When** alguém envia uma identidade, **Then** a resposta é 503 e
   nada é gravado na sessão.
3. **Given** o seletor desligado, **When** alguém abre a vitrine, **Then** o cabeçalho traz "Minhas
   inscrições" e não traz "Área de gestão".

---

### User Story 5 — Sair e trocar de identidade (Priority: P3)

Quem está na gestão sai e volta à página de acesso. Quem abre a página de acesso já identificado vê
com quem está e pode continuar ou trocar.

**Acceptance Scenarios**:

1. **Given** uma identidade na sessão, **When** a pessoa sai, **Then** a sessão perde a identidade e
   a pessoa chega à página de acesso.
2. **Given** uma identidade na sessão, **When** a pessoa abre a página de acesso, **Then** vê o nome
   com que está e as ações de continuar e de trocar.

### Edge Cases

- **Sessão aberta pela demonstração quando o seletor é desligado depois**: a identidade é recusada —
  a gestão a trata como ausente —, e a sessão não volta a valer se o seletor for religado sem nova
  escolha (achado A4 do estudo).
- **Sessão gravada antes desta feature**, sem a origem: tratada como de demonstração, que é a única
  origem que existe hoje.
- **Destino que aponta para a própria página de acesso ou para a saída**: ignorado, para não haver
  laço.
- **Ambiente sem comissão nenhuma**: o grupo *Comissões* não aparece; as responsabilidades sim.
- **Responsabilidade que ninguém exerceu na trilha**: a entrada usa um nome de demonstração que se
  denuncia como tal na auditoria (`demo.<papel>`).
- **Celular**: a coluna institucional vira uma faixa curta no topo; nada exige rolagem horizontal a
  375 px.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-1690**: A página de acesso à gestão MUST substituir a tela de identificação atual, no mesmo
  endereço, com duas áreas: a institucional — o nome do produto, a frase de apresentação e o ciclo
  do certame — e a de acesso, com "Bem-vindo à gestão", o selo do ambiente e um lugar para o método
  de entrada. A página MUST oferecer ao candidato o caminho para as próprias inscrições.
- **FR-1691**: O método de entrada MUST ser decidido no servidor, por uma lista de métodos
  disponíveis. Nesta feature o único método é a demonstração, disponível só com o seletor ligado.
  Sem método disponível, a página MUST responder 503 com a mensagem de entrada não configurada e
  MUST NOT oferecer ação de entrar.
- **FR-1692**: A escolha de identidades de demonstração MUST ser uma etapa própria, com dois grupos:
  *Comissões*, uma entrada por pessoa com vínculo ativo — a responsabilidade (presidência, avaliação
  ou membro), o código dos Processos, as Etapas atribuídas e as avaliações pendentes, quando houver
  —; e *Responsabilidades da unidade*, uma entrada por papel, com o rótulo e uma descrição do que
  ele faz. A interface MUST NOT mostrar códigos de permissão.
- **FR-1693**: Entrar por uma entrada de comissão MUST identificar sem papel nenhum; entrar por uma
  responsabilidade MUST identificar com aquele papel e só ele. O nome de cada responsabilidade MUST
  ser o de quem mais a exerceu na trilha de auditoria do escopo, ou `demo.<papel>` quando ninguém a
  exerceu.
- **FR-1694**: As opções avançadas de demonstração — nome livre e qualquer combinação de
  responsabilidades, com as descrições — MUST continuar disponíveis, fechadas por padrão. O envio
  sem nome MUST voltar com status 422, a recusa junto do campo, as opções abertas e o foco no campo.
- **FR-1695**: Com mais de oito entradas, a escolha MUST oferecer um campo de busca que filtra a
  lista pelo nome, pela responsabilidade e pelo Processo. Sem script, a lista inteira MUST continuar
  utilizável.
- **FR-1696**: Toda página da gestão que hoje manda para a identificação quem não tem identidade
  MUST mandar com o próprio endereço como destino; depois de identificar-se, a pessoa MUST ir ao
  destino. Destino que não seja um caminho da própria gestão, no mesmo host — ou que seja a página
  de acesso ou a saída —, MUST ser ignorado, e a pessoa vai ao lugar padrão de hoje.
- **FR-1697**: Sair MUST encerrar a identidade e levar à página de acesso. Com identidade na sessão,
  a página de acesso MUST mostrar o nome atual e as ações de continuar e de trocar de identidade.
- **FR-1698**: A sessão MUST gravar a origem da identidade. Identidade de origem demonstração — e a
  sessão anterior a esta feature, que não tem origem — MUST ser tratada como ausente quando o
  seletor estiver desligado.
- **FR-1699**: O cabeçalho do portal MUST trocar "Entrar" por "Minhas inscrições", com o mesmo
  destino de hoje — a área com sessão, o acesso sem ela —, e MUST oferecer "Área de gestão" **só**
  quando houver método de entrada na gestão.
- **FR-1700**: Os cabeçalhos do portal e da gestão MUST nomear o produto como "Gestão de Processos
  Seletivos", com a sigla GPS onde o espaço não comportar o nome por extenso.
- **FR-1701**: Cada papel de responsabilidade MUST ter descrição, e um guardião MUST reprovar papel
  sem ela.
- **FR-1702**: Os protótipos do estudo (`/gestao/prototipos/acesso/`) MUST sair junto com esta
  feature.

### Key Entities

Nenhuma nova. A identidade da sessão ganha o campo *origem*; os papéis ganham descrição.

## Success Criteria *(mandatory)*

- **SC-650**: Partindo da raiz, uma pessoa da equipe chega à gestão identificada em três cliques —
  "Área de gestão", "Acessar ambiente de demonstração", a identidade —, provado no navegador.
- **SC-651**: Nenhum código de permissão aparece na página de acesso nem na escolha de identidades.
- **SC-652**: Um link de página da gestão aberto sem identidade termina na própria página depois da
  identificação; um destino externo nunca é seguido.
- **SC-653**: Com o seletor desligado, nenhuma rota de entrada identifica alguém, a vitrine não
  oferece a gestão e uma sessão de demonstração anterior deixa de valer.
- **SC-654**: A página de acesso e a escolha não têm rolagem horizontal a 375 px e são percorríveis
  só pelo teclado, com foco visível.
- **SC-655**: A suíte contra PostgreSQL continua sem falhas, e as telas operacionais da gestão não
  mudam além do nome do produto no cabeçalho.

## Decisões

### D-001 — O endereço e o nome da rota continuam os de hoje

A página nova responde em `/gestao/identificar`, pela rota `interface:identificar`. Mudar o
endereço custaria um redirecionamento e a edição das 90 chamadas por um motivo que a pessoa não vê;
o nome da rota é o que o código e os testes conhecem.

### D-002 — Um auxiliar só para mandar à identificação

As 90 chamadas a `redirect(reverse("interface:identificar"))` passam a um auxiliar em
`identidade.py`, que acrescenta o destino. A conferência do destino mora num lugar só, e uma porta
escrita amanhã usa o auxiliar em vez de repetir a conferência.

### D-003 — O que é só da demonstração fica num módulo próprio

As entradas de comissão, os nomes sugeridos pela trilha e a busca saem para
`interface/demonstracao.py`. Quando o diretório institucional chegar, o módulo sai inteiro; o que
fica — o método de entrada, a sessão e os papéis — é o que a autenticação real também usa.

### D-004 — A descrição mora junto do papel

A descrição vai para a fronteira de identidade, num mapa com as mesmas chaves do de papéis, e não
para a tela: é o mesmo módulo onde o papel nasce, e o guardião de `FR-1701` compara os dois mapas.
Um mapa à parte, e não um terceiro elemento na tupla do papel, porque cinco testes de autorização
leem a tupla como par (`T-004`).

### D-005 — Sessão sem origem conta como demonstração

Hoje a demonstração é a única origem que existe. Tratar a sessão antiga como válida com o seletor
desligado reabriria exatamente a lacuna que `FR-1698` fecha.

### D-006 — A sigla só onde o nome não cabe

"Gestão de Processos Seletivos" por extenso nos cabeçalhos; "GPS" no celular, com o nome inteiro
como nome acessível. A sigla sozinha não diz o que é a quem chega pela primeira vez.

## Assumptions

- O símbolo do produto na página de acesso é um marcador de lugar; a marca oficial do Ifes depende
  do manual de identidade visual da Rede Federal e fica fora desta feature.
- A autenticação institucional (LDAP, escolhido em 28/08) virá como outro método na mesma lista; o
  desenho da área de acesso comporta tanto um botão quanto um formulário de duas linhas.
- O shell da gestão (barra lateral) é a etapa 2 do estudo, em feature própria.
