# Feature Specification: Área do Candidato e Acesso sem Senha

**Feature Branch**: `claude/spec-010-candidate-area-746d47`

**Created**: 2026-09-01

**Status**: Draft

**Input**: Área pessoal persistente do candidato, com autenticação sem senha por código de uso único
enviado por e-mail. Substitui o provedor de identidade de demonstração da `009`, preserva a
titularidade de tudo o que já foi submetido, e entrega a reconferência dos dados, dos documentos e do
comprovante mais o acompanhamento do certame. Redação consolidada após três rodadas de avaliação
verificadas contra o repositório em `55caa29` (`SPEC-010-DRAFT.md`, commit `cb3214a`).

## A frase que governa esta feature

> **O candidato deve conseguir entrar sem senha, reencontrar tudo o que já submeteu e entender o que
> está acontecendo em suas seleções sem redigitação desnecessária, sem procurar novamente o certame
> fora de sua área pessoal e sem reduzir a proteção dos seus dados e documentos.**

E a contrapartida institucional, que tem o mesmo peso:

> **Nenhuma inscrição já submetida muda de dono porque esta feature foi implantada, e nenhum acesso é
> concedido por afirmação — só por prova.**

Todo requisito abaixo responde a uma de duas perguntas: *isto deixa a pessoa reencontrar o que é
dela?* ou *isto impede que alguém alcance o que não é seu?* O que não responde a nenhuma das duas não
pertence a esta spec.

## Contexto

A `009` entregou a jornada de inscrição, mas não uma identidade persistente de candidato. Quem se
inscreve **declara** nome, CPF e e-mail numa tela de demonstração, e nada verifica a declaração; o
identificador estável que decide a propriedade da Inscrição é derivado do CPF por meio do segredo
geral da aplicação; o e-mail fica gravado na própria Inscrição, sem vínculo persistente com a pessoa;
e não existe tela alguma onde ela reencontre o que enviou.

Três consequências, e a terceira é a que impede a implantação:

1. Ninguém retorna meses depois. Não há login, não há lista de inscrições, não há como rever um
   documento enviado nem baixar de novo o comprovante.
2. A propriedade de tudo o que foi submetido depende da rotação de um segredo de aplicação. Trocar
   esse segredo hoje tornaria cada inscrição inalcançável pelo seu titular, em silêncio.
3. **A configuração de produção recusa a inicialização com o provedor de demonstração ligado.** O
   portal do candidato, hoje, não sobe em produção. Esta feature é o que remove esse impedimento — e
   por isso é ela que herda a responsabilidade de não reintroduzir, por outro caminho, aquilo que a
   recusa protege.

**O que já existe e será consumido, não recriado.** A Inscrição e seus dois estados, a titularidade
verificada no servidor, o Documento Exigido e o Documento Submetido, o armazenamento privado de
arquivos, o protocolo, o comprovante e suas evidências de integridade, a versão consolidada aceita no
envio, a consulta administrativa do que chegou, a trilha de auditoria e o Cronograma derivado da
versão vigente.

**O que não existe e esta feature inaugura.** Identidade persistente de candidato, credencial provada
de e-mail, sessão autenticada de candidato, área pessoal, e o canal de envio de e-mail — que o
projeto não possui em nenhuma forma.

## Precondições

- **PC-001**: A `009 — Inscrição simples e documentos do candidato` está concluída, com requisitos,
  testes e rastreabilidade fechados.
- **PC-002**: Esta feature consome e não redefine: Inscrição, seus estados, titularidade, Documento
  Exigido, Documento Submetido, comprovante, versão consolidada aceita, armazenamento privado e
  regras de submissão.
- **PC-003**: A área do candidato não entra em produção com dados reais enquanto não existir política
  institucional documentada de retenção e descarte dos dados pessoais pertinentes. Esta feature
  registra o gate; não inventa prazo jurídico nem implementa descarte arbitrário. As duas afirmações
  convivem com o item 3 do Contexto: remove-se o impedimento técnico e mantém-se o institucional.

## Princípios desta feature

### P-001 — Sem senha

Não há criação, confirmação, recuperação nem política de complexidade de senha. Controle do e-mail é
provado por código temporário. Também não há link que autentica: um link assim viaja no histórico do
navegador, no encaminhamento da mensagem e no cabeçalho de origem. O código é digitado.

### P-002 — E-mail é credencial, não identidade

Trocar de e-mail não cria uma pessoa nova. Uma mesma identidade pode ter várias credenciais de
e-mail verificadas.

### P-003 — CPF não é credencial

Conhecer um CPF não prova nada: ele está em contrato, em crachá, em vazamento. CPF nunca concede
acesso, nunca cria vínculo por afirmação e nunca é pedido no acesso recorrente. Ele confirma uma
correspondência que o sistema já encontrou por outro caminho, e nada mais.

### P-004 — Segurança não se obtém por burocracia

O fluxo normal é curto. Casos excepcionais podem exigir tratamento diferente, mas não transformam
todo acesso em "e-mail + CPF + dados pessoais + código".

### P-005 — Dados históricos não são reescritos

Adicionar ou corrigir credencial não altera o que consta de uma inscrição submetida. O sistema
continua podendo afirmar: *"esta foi a informação efetivamente submetida naquele ato."*

### P-006 — O candidato não é ator institucional

A identidade do candidato não entra em papéis institucionais, comissão, permissões de Edital nem
grupos institucionais. É um segundo eixo de identidade, como a `009` já decidiu.

### P-007 — Nenhum vínculo nasce de afirmação

Todo vínculo entre credencial e identidade nasce de prova de controle do e-mail, somada — quando há
patrimônio histórico em jogo — a uma confirmação. Vínculo que se cria porque alguém digitou um dado é
vínculo que qualquer pessoa cria.

### P-008 — A jornada da 009 permanece; muda quem alimenta seus dados

A abertura de rascunho continua recebendo identificador estável, nome, CPF e e-mail. Esta feature
troca **a origem** desses dados — do formulário declarado para a identidade persistida — e não a
jornada que os usa.

### P-009 — Nenhum caminho de credencial termina em beco sem saída

Provar o controle de um endereço sempre produz sessão. Recusa, engano ou ambiguidade levam a um
estado utilizável, nunca a uma porta trancada sem chave.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Entrar sem senha (Priority: P1)

Como candidato, quero entrar informando meu e-mail e um código recebido nele, para não precisar criar
nem lembrar uma senha, e chegar direto ao que é meu.

**Why this priority**: é a porta. Sem ela nenhuma das outras histórias é alcançável, e é ela que
remove o impedimento de produção descrito no Contexto.

**Independent Test**: informar um endereço, receber o código, digitá-lo e chegar a uma área pessoal —
mesmo que essa área esteja vazia. Entrega valor sozinha: o candidato passa a ter um lugar.

**Acceptance Scenarios**:

1. **Given** um endereço já verificado e associado a uma identidade, **When** a pessoa o informa e
   digita corretamente o código recebido, **Then** o sistema abre a sessão daquela identidade e a
   leva a "Minhas inscrições" sem passo intermediário.
2. **Given** um endereço sem participação anterior, **When** a pessoa prova o controle dele,
   **Then** cria-se uma identidade própria, sem pedir CPF, e ela entra numa área vazia que não tem
   aparência de erro.
3. **Given** um código expirado, já usado, ou tentado acima do limite, **When** a pessoa o envia,
   **Then** o sistema recusa e a mensagem não distingue "código errado" de "endereço inexistente".
4. **Given** qualquer endereço, existente ou não, **When** a pessoa solicita o código, **Then** a
   resposta, a janela de reenvio e o texto de espera são os mesmos.

---

### User Story 2 - Reencontrar a participação anterior (Priority: P1)

Como candidato que já se inscreveu antes desta feature, quero reencontrar minhas inscrições
confirmando uma única vez quem sou, sem que ninguém mais consiga alcançá-las.

**Why this priority**: sem ela, todo mundo que usou o sistema antes recomeça do zero, e o que já foi
submetido fica órfão.

**Independent Test**: com uma inscrição pré-existente, provar o endereço usado nela, confirmar o CPF,
e ver a inscrição na área — sem que nenhum dado da inscrição tenha mudado.

**Acceptance Scenarios**:

1. **Given** uma pessoa que se inscreveu antes com um CPF, um endereço e um titular estável,
   **When** ela prova o controle daquele endereço e confirma aquele CPF, **Then** o endereço vira
   credencial verificada daquela identidade e todas as inscrições dela ficam visíveis, sem que
   nenhuma tenha mudado de titular.
2. **Given** o mesmo endereço constando de inscrições de titulares diferentes, **When** a pessoa
   confirma o CPF, **Then** reconcilia-se com a identidade cujo CPF confere, e com nenhuma outra.
3. **Given** alguém que recusa o convite ou erra o CPF, **When** o fluxo termina, **Then** ela entra
   numa identidade própria e vazia, e a identidade anterior permanece intacta.
4. **Given** uma pessoa que recusou o convite por engano e ainda não abriu inscrição alguma,
   **When** ela retoma a reconciliação de dentro da área e confirma o CPF, **Then** suas credenciais
   passam à identidade anterior e a identidade vazia é descartada.
5. **Given** alguém que conhece o CPF de outra pessoa mas controla um endereço sem participação
   anterior, **When** ele entra, **Then** nenhuma inscrição alheia aparece e nenhum vínculo com
   aquele CPF é criado.

---

### User Story 3 - Minhas inscrições e continuar de onde parou (Priority: P1)

Como candidato, quero ver todas as minhas inscrições num só lugar e retomar um rascunho sem procurar
o certame de novo no site.

**Why this priority**: é a razão de existir de uma área pessoal, e é o que elimina a busca pelo
Edital a cada retorno.

**Independent Test**: entrar, ver a lista ordenada, acionar "Continuar inscrição" e cair na jornada
já existente, com o rascunho como estava.

**Acceptance Scenarios**:

1. **Given** uma identidade com rascunhos e inscrições enviadas, **When** ela abre a área, **Then**
   vê todas e somente as suas, mais recente primeiro, cada uma com Edital, Perfil, situação,
   protocolo quando houver e uma ação principal inequívoca.
2. **Given** um rascunho, **When** a pessoa aciona "Continuar inscrição", **Then** retoma a jornada
   existente com o conteúdo preservado, sem redigitar nada.
3. **Given** uma identidade sem inscrição alguma, **When** ela abre a área, **Then** lê um convite a
   consultar os processos seletivos disponíveis, sem aparência de erro.
4. **Given** a primeira inscrição de uma identidade nova, **When** a pessoa a abre, **Then** informa
   nome e CPF uma única vez, e nunca mais nas inscrições seguintes.

---

### User Story 4 - Conferir exatamente o que foi submetido (Priority: P1)

Como candidato, quero abrir uma inscrição enviada e ver exatamente o que o sistema recebeu — dados,
documentos e comprovante — para conferir sem depender de ninguém.

**Why this priority**: é a promessa central da área. Sem ela o candidato continua guardando cópias
por fora porque não confia no que enviou.

**Independent Test**: abrir uma inscrição enviada e ver protocolo, data, versão aceita, dados, a
lista de documentos e a possibilidade de visualizar, baixar e obter o comprovante.

**Acceptance Scenarios**:

1. **Given** uma inscrição enviada, **When** a pessoa a abre, **Then** vê a oportunidade, a situação,
   o protocolo, o instante do envio, a versão normativa aceita, os dados informados e todos os
   documentos efetivamente submetidos.
2. **Given** um documento submetido, **When** a pessoa o visualiza ou baixa, **Then** recebe
   exatamente o arquivo vigente naquela inscrição, e nada na inscrição se altera.
3. **Given** um identificador de inscrição ou documento de outro candidato, **When** ele é usado na
   sessão de alguém, **Then** a resposta não permite descobrir que aquele objeto existe.
4. **Given** uma inscrição enviada, **When** a pessoa pede o comprovante, **Then** recebe o mesmo
   comprovante já produzido no envio, com as evidências de integridade preservadas.

---

### User Story 5 - Acompanhar a participação e o certame (Priority: P2)

Como candidato, quero saber o que já aconteceu comigo e o que vem a seguir no processo, sem confundir
uma coisa com a outra.

**Why this priority**: entrega valor real, mas a conferência do que foi submetido resolve a
ansiedade maior. Depende das quatro anteriores para ter onde aparecer.

**Independent Test**: abrir uma inscrição enviada e distinguir, na mesma tela, os fatos da própria
participação e os eventos do cronograma do processo.

**Acceptance Scenarios**:

1. **Given** uma inscrição enviada, **When** a pessoa abre o acompanhamento, **Then** lê seus fatos
   pessoais e o cronograma do processo em blocos visualmente distintos.
2. **Given** um cronograma cuja etapa chegou à data final, **When** a pessoa acompanha, **Then** o
   sistema não afirma nada sobre a situação pessoal dela que não tenha acontecido.
3. **Given** um Edital retificado após o envio, **When** a pessoa abre a inscrição, **Then** lê um
   aviso de atualização com acesso ao texto vigente, sem que a versão aceita seja alterada e sem
   qualquer reabertura ou reenvio.

---

### User Story 6 - Cuidar das próprias credenciais (Priority: P2)

Como candidato, quero acrescentar um segundo e-mail, escolher qual deles a instituição usa, remover
um que não uso mais e corrigir um erro de digitação no meu nome.

**Why this priority**: previne a perda de acesso antes que ela aconteça — o problema real de quem
troca de provedor entre um certame e outro. Não é pré-requisito das anteriores.

**Independent Test**: autenticado, adicionar um endereço provando-o, defini-lo como principal,
remover o antigo e corrigir o nome.

**Acceptance Scenarios**:

1. **Given** uma pessoa autenticada, **When** ela adiciona um endereço e prova o controle dele,
   **Then** ele passa a autenticar aquela identidade, sem que CPF seja pedido.
2. **Given** duas credenciais verificadas, **When** ela remove uma, **Then** a remoção não altera
   inscrição alguma e a identidade nunca fica sem credencial nem sem endereço principal.
3. **Given** um erro de digitação no nome, **When** ela o corrige, **Then** os rascunhos abertos
   passam a exibir o nome corrigido e nenhuma inscrição enviada é alterada.

---

### Edge Cases

- **Endereço reciclado.** Alguém digitou por engano, anos atrás, um endereço que hoje pertence a
  outra pessoa. Quem controla a caixa hoje entra normalmente, na própria identidade, sem ver nada de
  ninguém, e a identidade anterior permanece intacta.
- **Engano no convite de reconciliação.** Quem recusa o convite sem ler pode retomá-lo enquanto não
  tiver aberto nenhuma inscrição na identidade nova.
- **Endereço de terceiro conhecendo o CPF.** Não produz vínculo algum com aquele CPF, porque o CPF
  não é pedido quando não há correspondência a confirmar.
- **Duas pessoas declarando o mesmo CPF no mesmo Perfil.** Nenhuma delas é recusada no envio; a
  coincidência é assinalada para quem conduz o certame.
- **Dados anteriores irreconciliáveis.** Um mesmo CPF cujas inscrições anteriores tenham titulares
  estáveis diferentes não gera identidade automática, e suas inscrições permanecem intactas e sem
  novo dono até tratamento operacional.
- **Inscrição enviada sem CPF utilizável nos dados anteriores.** Interrompe a implantação com
  relatório, em vez de ser contornada por escolha automática.
- **Perda de todas as credenciais.** Está fora desta versão e tem caminho institucional declarado.
- **Duas abas, dois envios, duas confirmações simultâneas.** Não produzem código consumido duas
  vezes, credencial duplicada nem identidade movida pela metade.

## Requirements *(mandatory)*

### Identidade do candidato (US1, US2)

- **FR-001**: O sistema DEVE manter uma identidade persistente de candidato, com identificador
  estável que é o único dado a decidir a propriedade de uma Inscrição.
- **FR-002**: O identificador estável de identidades novas DEVE ser opaco e próprio da identidade,
  NÃO PODE derivar de segredo rotacionável da aplicação nem de dado pessoal, e DEVE ser distinguível
  do conjunto produzido pelo provedor de demonstração.
- **FR-003**: A identidade do candidato NÃO PODE conceder permissão institucional alguma, nem
  participar de papéis, comissão ou grupos institucionais.
- **FR-004**: A identidade DEVE carregar nome e CPF normalizado, porque a Inscrição os exige e o nome
  consta do comprovante pelo qual a conferência documental é feita.
- **FR-005**: Nome e CPF DEVEM ser pedidos uma única vez, na primeira inscrição da identidade, e
  reusados nas seguintes. Quem tem participação anterior NÃO PODE ser solicitado a informá-los.
- **FR-006**: O CPF informado DEVE ser validado quanto à sua formação. A validação prova apenas que o
  número é um CPF possível: ela NÃO PODE ser tratada, em nenhum ponto, como prova de titularidade.
- **FR-007**: O CPF DEVE ser declarado pelo titular e NÃO PODE decidir propriedade nem acesso.
- **FR-008**: O titular DEVE poder corrigir o próprio nome a qualquer momento, e o próprio CPF
  enquanto a identidade não tiver nenhuma inscrição enviada. A partir da primeira inscrição enviada o
  CPF congela, e corrigi-lo passa a ser ato institucional fora desta feature.
- **FR-009**: CPF NÃO PODE aparecer em endereço de página, e NÃO DEVE ser duplicado em registros
  técnicos ou de auditoria.

### Credenciais de e-mail (US1, US6)

- **FR-010**: Uma identidade DEVE poder ter várias credenciais de e-mail verificadas.
- **FR-011**: Um endereço, na sua forma canônica, DEVE pertencer a no máximo uma identidade, e essa
  exclusividade DEVE ser garantida pela persistência — não por verificação prévia à gravação, que
  perde a corrida entre duas confirmações simultâneas.
- **FR-012**: A forma canônica DEVE ser obtida de modo conservador: caixa baixa e domínio em forma
  canônica, sem remover pontos, sem cortar sufixos e sem aplicar qualquer regra específica de
  provedor. O endereço como a pessoa o informou DEVE ser preservado para exibição e NÃO PODE decidir
  identidade.
- **FR-013**: A identidade DEVE ter um endereço principal, escolhido pelo titular, e é ele que
  alimenta a Inscrição. O primeiro endereço verificado é o principal por padrão.
- **FR-014**: Nome, CPF e endereço principal DEVEM alimentar a Inscrição segundo uma regra única:
  enquanto ela for rascunho, acompanham a identidade; no envio, congelam.
- **FR-015**: Um endereço que consta de inscrição anterior NÃO PODE ser considerado verificado por
  ter sido digitado. Só o desafio desta feature prova controle.
- **FR-016**: O candidato autenticado DEVE poder adicionar endereço, provando-o por desafio, sem que
  CPF seja pedido.
- **FR-017**: Endereço que já pertence a outra identidade NÃO PODE ser adicionado, e a recusa NÃO
  DEVE revelar a quem ele pertence.
- **FR-018**: O candidato autenticado DEVE poder remover endereço associado. O sistema NÃO PODE
  permitir remover a última credencial, nem deixar a identidade sem endereço principal.
- **FR-019**: Remover credencial NÃO PODE alterar nenhuma inscrição. Trocar qual credencial é a
  principal alcança os rascunhos abertos, e apenas eles, pela regra única da FR-014 — nunca uma
  inscrição enviada.

### Desafio de acesso (US1)

- **FR-020**: A resposta à solicitação do código DEVE ser equivalente exista ou não identidade
  associada ao endereço.
- **FR-021**: A equivalência DEVE incluir a janela de reenvio, a contagem de limite e o texto de
  espera. Um contador que só avança para endereços existentes anula a FR-020.
- **FR-022**: O código DEVE ser numérico e curto, adequado à digitação manual, com seis dígitos.
- **FR-023**: O código DEVE ser gerado por fonte criptograficamente segura, com distribuição uniforme
  sobre todo o intervalo.
- **FR-024**: O código DEVE expirar em dez minutos, contados de instante absoluto registrado no
  desafio.
- **FR-025**: O código DEVE ser de uso único, e o seu consumo DEVE ser atômico — a mesma tentativa
  não pode ser aproveitada por duas requisições simultâneas.
- **FR-026**: Um novo código DEVE invalidar os anteriores ainda utilizáveis daquele endereço.
- **FR-027**: O código NÃO PODE ser persistido em forma recuperável.
- **FR-028**: Cada desafio DEVE valer para um endereço canônico e uma finalidade declarada. Um código
  pedido para entrar NÃO PODE confirmar adição de credencial, e vice-versa.
- **FR-029**: O sistema DEVE limitar as tentativas de validação por desafio a cinco.
- **FR-030**: O sistema DEVE limitar solicitações repetidas por endereço e por origem. Os valores são
  constantes da aplicação, não configuração de usuário. NÃO DEVE existir teto global de envio: um
  teto global converte abuso distribuído em indisponibilidade para todos os candidatos, no dia em que
  ela mais custa.
- **FR-030a**: A implantação DEVE **declarar** se há proxy à frente da aplicação, e a inicialização
  em produção DEVE ser recusada enquanto isso não for declarado. Não existe padrão seguro: confiar
  no cabeçalho de proxy sem proxy torna o limite por origem contornável com um valor forjado a cada
  requisição; não confiar havendo proxy faz todas as origens colapsarem numa só, e o teto por origem
  passa a valer para a instituição inteira — recusando candidato legítimo em bloco no último dia do
  prazo. Qual dos dois acontece depende da topologia, que só quem implanta conhece.
- **FR-031**: Esgotado o limite, o desafio DEVE morrer, e a mensagem NÃO PODE distinguir código
  errado de endereço inexistente.
- **FR-039a**: A escolha de modalidade DEVE ser guardada quando é feita, e a lista de documentos
  exigidos DEVE ser recalculada na mesma resposta. Guardá-la só ao avançar fazia a tela prometer que
  "a escolha decide quais documentos serão pedidos" e não cumprir: o candidato via a lista antiga e o
  aviso de "todos enviados", e descobria o documento a mais na revisão — quando já se considerava
  pronto. Sem JavaScript, o comportamento anterior permanece válido.

- **FR-031a**: A recusa DEVE nomear a causa **relativa ao desafio** — código incorreto com o saldo
  de tentativas, tentativas esgotadas, prazo vencido, código já usado. Isso não fere a `FR-031`: o
  desafio é criado de forma idêntica exista ou não identidade, e por isso motivo e saldo são os
  mesmos nos dois casos. A frase única custava candidato de forma verificável — esgotadas as cinco
  tentativas, quem digitava o código **certo** lia a mesma recusa de quem digitava errado, e
  concluía que o sistema estava quebrado.
- **FR-031b**: Solicitação de código recusada pela janela de espera DEVE ser respondida por escrito,
  dizendo que nada foi enviado. Recarregar a tela sem mensagem é indistinguível de sucesso, e faz a
  pessoa esperar por um e-mail que não existe.
- **FR-032**: Desafios e contadores DEVEM ser guardados de forma compartilhada entre os processos que
  atendem a aplicação, de modo que os limites valham de fato.
- **FR-033**: Desafios expirados NÃO SÃO dado permanente de domínio, e o sistema DEVE permitir sua
  limpeza operacional.

### Sessão (US1)

- **FR-034**: Autenticada a pessoa, o sistema NÃO DEVE pedir novo código a cada página.
- **FR-035**: O identificador de sessão DEVE ser rotacionado no instante da autenticação.
- **FR-036**: Sessão expirada DEVE exigir novo desafio.
- **FR-037**: NÃO DEVE existir permanência indefinida do tipo "lembrar de mim" nesta versão.
- **FR-038**: Sair DEVE encerrar a sessão do candidato, e apenas a dele.
- **FR-039**: A sessão de candidato e a de ator institucional DEVEM ser contextos distintos, e uma
  NÃO PODE identificar na outra.

### Reconciliação com a participação anterior (US2)

- **FR-040**: A reconciliação com os dados anteriores DEVE ocorrer na implantação, e não no primeiro
  acesso de cada pessoa. Enquanto ela não ocorre, a propriedade das inscrições permanece dependente
  de um segredo rotacionável, e a rotação as tornaria inalcançáveis em silêncio.
- **FR-041**: A implantação DEVE materializar uma identidade para cada CPF encontrado nas inscrições
  existentes, preservando exatamente o identificador estável que elas já carregam, e trazendo o nome
  da inscrição mais recente daquele conjunto.
- **FR-042**: A implantação NÃO PODE reescrever o identificador estável de nenhuma inscrição.
- **FR-043**: A implantação NÃO PODE marcar endereço algum como verificado.
- **FR-044**: Um CPF cujas inscrições apontem para mais de um identificador estável NÃO PODE gerar
  identidade, e DEVE ser relatado para tratamento operacional.
- **FR-045**: Rascunho sem CPF utilizável DEVE ser relatado, permanecer intacto e não ser
  reconciliado.
- **FR-046**: Inscrição **enviada** sem CPF utilizável DEVE **interromper** a implantação com
  relatório do que a impediu. Prosseguir exigiria escolher um dado por conta própria, e tornaria
  inverificável a garantia da FR-063.
- **FR-047**: As inscrições de um conjunto não reconciliado DEVEM permanecer intactas — mesmo
  titular, nenhum dado escolhido para desempatar — e ficam inalcançáveis pela área pessoal até
  tratamento operacional.
- **FR-048**: Concluída a implantação, a identificação por declaração NÃO PODE seguir sendo caminho
  de autenticação, e a recusa de inicialização que hoje a impede em produção DEVE permanecer ativa.

### A primeira associação de um endereço (US1, US2)

- **FR-049**: Quando o endereço provado não tiver correspondência anterior alguma, o sistema DEVE
  criar identidade sem pedir CPF.
- **FR-050**: Quando o endereço provado constar de inscrições anteriores, o sistema DEVE oferecer a
  reconciliação como convite recusável, confirmado por CPF.
- **FR-051**: Constando o endereço de inscrições de identidades diferentes, o CPF DEVE desempatar,
  reconciliando com aquela cujo CPF confere e com nenhuma outra.
- **FR-052**: A decisão do convite DEVE ocorrer **antes** de o vínculo entre endereço e identidade
  existir. Recusa, CPF errado ou tentativas esgotadas DEVEM produzir identidade própria e sessão
  utilizável.
- **FR-052a**: As tentativas de confirmar o CPF DEVEM ser limitadas a cinco, contadas **no mesmo
  desafio** que provou o endereço — e não na sessão, que uma aba nova zeraria. O desafio permanece o
  portador da reconciliação pendente depois de consumido, até que ela seja decidida ou expire.
- **FR-052b**: A reconciliação pendente DEVE expirar dez minutos após o consumo do código, e expirar
  significa continuar com identidade própria — nunca ficar sem sessão.
- **FR-052c**: O limite DEVE incidir sobre quem tenta, e nunca sobre a identidade alvo. Um contador
  preso ao alvo permitiria a um terceiro esgotar as tentativas e impedir o titular legítimo de
  reconciliar. Quem quiser tentar de novo precisa de novo desafio, e o custo disso é o limite de
  solicitações da FR-030.
- **FR-053**: A retomada da reconciliação DEVE continuar disponível de dentro da área **enquanto a
  identidade nova não tiver nenhuma inscrição, nem rascunho**. Aceita, as credenciais passam à
  identidade anterior e a identidade vazia é descartada.
- **FR-054**: Na retomada, **todas** as credenciais verificadas da identidade vazia DEVEM passar
  junto — cada uma já foi provada, e mover só uma perderia o que a pessoa comprovou. O endereço
  principal da identidade anterior não muda por isso.
- **FR-055**: Verificar, mover e descartar DEVEM ocorrer como operação única: verificado antes e
  movido depois, um rascunho criado no intervalo tornaria falsa a premissa no instante do uso.
- **FR-056**: O sistema NÃO PODE fundir identidades. Quem já tem identidade e prova endereço novo sem
  correspondência anterior recebe identidade nova; agregar credenciais é a US6, a partir de dentro.
- **FR-057**: A existência de um endereço em inscrição anterior NÃO PODE impedir quem hoje controla
  aquela caixa de ter a própria identidade, e a identidade anterior não reconciliada permanece
  intacta.

### Minhas inscrições e continuidade (US3)

- **FR-058**: A entrada padrão após a autenticação DEVE ser a lista das inscrições da identidade,
  mais recente primeiro, com Edital, Perfil, situação, protocolo quando houver e uma ação principal.
- **FR-059**: "Continuar inscrição" DEVE reutilizar o rascunho e a jornada existentes. NÃO PODE
  existir segunda implementação do formulário de inscrição.
- **FR-060**: Uma identidade NÃO PODE visualizar inscrição pertencente a outra.
- **FR-061**: Sem inscrições, a área DEVE apresentar convite a consultar os processos seletivos
  disponíveis, sem aparência de erro.

### CPF coincidente (US3, US4)

- **FR-062**: A restrição existente de uma inscrição por identidade, Edital e Perfil, em qualquer
  estado, DEVE permanecer intacta: é ela que sustenta a idempotência de abertura de rascunho.
- **FR-063**: Uma inscrição enviada DEVE ter CPF normalizado não vazio e com onze dígitos,
  garantido por restrição de banco. A conferência dos dígitos verificadores **não** cabe numa
  restrição declarativa: ela permanece no domínio, no momento da captura (FR-006), e na verificação
  que a implantação faz antes de instalar a restrição (FR-046). Dizer que o banco garante o CPF
  "válido" seria prometer mais do que ele consegue.
- **FR-064**: Duas inscrições enviadas com o mesmo CPF no mesmo Perfil DEVEM ser aceitas. Nenhum
  candidato PODE ser recusado no envio por causa de CPF que outra identidade declarou.
- **FR-065**: A consulta administrativa existente DEVE **assinalar** as inscrições que compartilham
  CPF dentro do mesmo Perfil. Dizer apenas que a coincidência "é visível" não basta: a listagem exibe
  o CPF mascarado, e comparar máscaras a olho não é detecção.
- **FR-066**: O sistema NÃO DEVE decidir qual das inscrições coincidentes vale. Essa decisão é
  institucional, e a regra pertence à feature que vier a avaliar inscrições.

### Conferência do que foi submetido (US4)

- **FR-067**: A página da inscrição enviada DEVE apresentar a oportunidade, a situação, o protocolo,
  o instante do envio, a versão normativa aceita, os dados informados e os documentos submetidos.
- **FR-068**: O candidato DEVE acessar somente os próprios documentos.
- **FR-069**: O arquivo entregue DEVE ser exatamente o documento vigente na inscrição enviada.
- **FR-070**: Visualizar ou baixar NÃO PODE alterar a inscrição.
- **FR-071**: O acesso ao arquivo NÃO PODE depender de endereço público previsível, e DEVE reutilizar
  o armazenamento privado e a autorização já entregues.
- **FR-072**: As evidências de integridade existentes — dos anexos, do código de verificação e do
  comprovante — DEVEM ser preservadas integralmente.
- **FR-073**: A tela principal NÃO DEVE transformar evidências de integridade em conteúdo
  protagonista; pode oferecê-las sob ação própria.
- **FR-074a**: Todo instante exibido ao candidato DEVE estar no fuso da instituição, e o mesmo
  instante DEVE ser escrito igual na tela, no comprovante e no PDF. Divergência aqui não é detalhe de
  apresentação: perto do fim do prazo, três horas mudam o dia do envio no documento que a pessoa
  guarda para provar que enviou a tempo.
- **FR-074**: "Baixar comprovante" DEVE devolver o comprovante já produzido no envio. NÃO PODE
  existir segunda modalidade de comprovante.
- **FR-075**: Esta feature NÃO PODE permitir editar inscrição enviada, substituir ou excluir
  documento enviado, nem cancelar inscrição.

### Acompanhamento (US5)

- **FR-076**: A página da inscrição DEVE distinguir visualmente os fatos da participação pessoal e os
  eventos do cronograma do processo.
- **FR-077**: O sistema NÃO PODE afirmar fato pessoal que não ocorreu apenas porque o cronograma
  institucional alcançou uma data.
- **FR-078**: Divergindo a versão vigente da versão aceita, o sistema DEVE avisar da atualização e
  dar acesso ao texto vigente.
- **FR-079**: A versão aceita NÃO PODE ser modificada silenciosamente, e a inscrição NÃO PODE ser
  reaberta ou reenviada automaticamente.

### O canal de e-mail que esta feature inaugura

- **FR-080**: O envio de e-mail e o remetente DEVEM ser configuráveis por ambiente.
- **FR-081**: Em produção, a inicialização DEVE ser recusada quando o mecanismo de envio for um dos
  conhecidos por não entregar mensagem, ou quando não houver remetente definido. Subir assim
  significa registrar o código de acesso e autenticar sem prova, com aparência de autenticação. A
  recusa NÃO ALEGA provar que um servidor configurado entregue — nenhuma verificação de
  inicialização pode prová-lo.
- **FR-082**: A mensagem DEVE conter o código, o prazo de validade e a orientação de ignorá-la se não
  foi a pessoa que solicitou. NÃO PODE conter link que autentica, CPF nem dado da inscrição.
- **FR-083**: Falha de envio DEVE produzir mensagem neutra, idêntica à do caminho feliz, e registro
  técnico no servidor.
- **FR-018a**: A remoção de credencial DEVE ser confirmada numa tela que enuncia o que se perde,
  antes de acontecer. O botão ficava ao lado de "Tornar principal" e apagava no primeiro clique;
  errar o alvo custava uma via de acesso, e a pessoa só descobria na vez seguinte em que tentasse
  entrar por aquele endereço.
- **FR-018b**: Adicionar e remover credencial DEVEM avisar a credencial principal por mensagem. Sem
  senha, a lista de credenciais **é** a conta: quem consegue anexar um endereço entra por ele para
  sempre, e este aviso é o único sinal que a titular teria disso.

- **FR-082a**: A mensagem do código DEVE corresponder à finalidade do desafio. Em "adicionar
  credencial", quem obtém o código não entra na conta de quem recebeu a mensagem — anexa a caixa de
  quem recebeu à conta dele —, e repetir ali "ignore, ninguém entra sem ele" afirma o oposto do
  risco.

- **FR-084**: Além do desafio, esta feature envia **uma única** outra mensagem: a confirmação do
  envio da inscrição, endereçada à credencial que praticou o ato. O canal passar a existir não torna
  comunicação transacional escopo implícito — aviso de retificação, de resultado, lembrete e
  campanha continuam fora. A exceção é nominal porque o custo de não tê-la é nominal e concreto: sem
  ela, quem fecha a aba antes de baixar o PDF fica sem o protocolo que a própria página manda
  guardar.
- **FR-084a**: A confirmação DEVE conter protocolo, código de verificação, a oportunidade, o instante
  do envio e o que foi recebido. NÃO PODE conter CPF, telefone nem link que autentica.
- **FR-084b**: O envio da mensagem DEVE acontecer com a inscrição já gravada, e a sua falha NÃO PODE
  desfazer nem impedir o ato. Amarrar um ato administrativo à disponibilidade de um servidor de SMTP
  faria uma queda de rede custar o prazo de um candidato (Princípio IV).

### Acesso, proteção de dados e auditoria

- **FR-085**: Toda consulta a inscrição ou documento DEVE verificar a titularidade no servidor.
- **FR-086**: Tentativa de acessar objeto de outro candidato DEVE responder de forma que não permita
  descobrir que ele existe.
- **FR-087**: Nenhum caminho desta feature PODE conceder acesso a partir de dado apenas declarado.
- **FR-088**: Código inválido NÃO DEVE gerar registro de auditoria de negócio. Tentativas excessivas,
  bloqueios e autenticação bem-sucedida DEVEM ser registrados como segurança técnica, sem código,
  sem CPF completo e sem conteúdo de documento.
- **FR-089**: Associação e remoção de credencial DEVEM ser eventos auditáveis na trilha existente, e
  NÃO DEVE ser criada trilha paralela. O encaixe DEVE ser decidido explicitamente: a trilha atual
  registra escopo institucional, e um ato sobre credencial não pertence a Edital algum.
- **FR-090**: A recuperação de acesso de quem perdeu todas as credenciais está fora desta versão.
  NÃO DEVEM ser criadas perguntas pessoais, combinações de dados cadastrais nem envio de documento
  para suporte. A mensagem de recusa DEVE apontar o procedimento institucional existente — a equipe
  enxerga as inscrições pela consulta administrativa e resolve o caso com a conferência documental
  que o balcão já pratica.

### Experiência, transversal a todas as histórias

- **UX-001**: O acesso recorrente DEVE exigir apenas endereço e código.
- **UX-002**: CPF DEVE aparecer somente no convite de reconciliação, que é opcional e recusável, e
  nunca no acesso recorrente.
- **UX-003**: Código válido DEVE levar à lista de inscrições sem passo intermediário no acesso
  recorrente e no primeiro acesso de quem não tem participação anterior. Quem tem participação
  anterior vê um passo, e apenas um.
- **UX-004**: Nenhum dado ou arquivo já submetido PODE precisar ser reenviado para ser conferido.
- **UX-005**: O campo do código DEVE aceitar colagem integral e digitação natural, sem obrigar a
  navegar entre campos independentes.
- **UX-006**: Reenviar DEVE ser ação clara, informando quando a próxima tentativa é possível. A
  contagem DEVE refletir o tempo restante no instante em que é lida, e não o apurado quando a página
  foi montada.
- **UX-010a**: Toda tela que remete o candidato ao atendimento institucional DEVE dizer **qual** —
  e a implantação DEVE declarar esse canal, sob recusa de inicialização em produção. São os pontos em
  que o sistema não resolve sozinho: CPF congelado e participação anterior não confirmada.
- **UX-010b**: Todo ato do candidato DEVE produzir confirmação visível na tela em que ele cai.
  Silêncio depois de uma ação é indistinguível de falha.
- **UX-010c**: Falha em requisição de envio de documento DEVE produzir mensagem visível junto do
  documento. Sem tratamento, uma resposta de erro não troca conteúdo algum: o nome do arquivo
  continua na tela, a contagem continua igual, e a pessoa acredita ter anexado.
- **UX-010d**: Mensagem de recusa NÃO PODE afirmar mais do que o sistema confere. O CPF é validado
  pelos dígitos verificadores, e não consultado em base alguma.
- **UX-010e**: Cada item de "Minhas inscrições" DEVE identificar o Processo Seletivo, e não apenas o
  número do Edital.

- **UX-006a**: A área do candidato DEVE ser alcançável a partir de qualquer página pública: quem tem
  sessão encontra o caminho para as próprias inscrições, e quem não tem encontra a porta de entrada.
  Sem isso, a única porta é iniciar uma inscrição — e quem só quer conferir a sua não a encontra.
- **UX-007**: Erro no código NÃO PODE apagar o endereço informado nem obrigar a reiniciar o fluxo.
- **UX-008**: Mensagens de segurança NÃO DEVEM expor detalhe interno de identidade.
- **UX-009**: Todo fluxo principal DEVE funcionar em tela de 375 px sem rolagem horizontal.
- **UX-010**: Todo fluxo principal DEVE ser concluível somente pelo teclado.

### Key Entities

- **Identidade do Candidato**: quem é a pessoa para o sistema, de forma persistente. Guarda o
  identificador estável que decide propriedade, o nome e o CPF declarado. Não guarda permissão
  alguma. Relaciona-se com as inscrições pelo identificador estável, e com suas credenciais.
- **Credencial de E-mail**: um endereço cujo controle foi provado, pertencente a uma única
  identidade. Uma delas é a principal, e é ela que alimenta a Inscrição.
- **Desafio de Acesso**: uma tentativa de provar o controle de um endereço, para uma finalidade
  declarada, com validade, limite de tentativas e consumo único. Não é dado permanente de domínio.
- **Inscrição** *(existente, consumida)*: continua pertencendo a quem seu identificador estável
  aponta, e nada nesta feature altera esse vínculo.
- **Documento Submetido** *(existente, consumido)*: continua acessível apenas ao titular da inscrição
  a que pertence.

## Success Criteria *(mandatory)*

### Medidas de acesso

- **SC-001**: O acesso recorrente se completa em duas telas — informar endereço, informar código — e
  em menos de 60 segundos a partir do recebimento da mensagem.
- **SC-002**: 100% dos códigos expirados, já consumidos ou tentados acima de cinco vezes são
  recusados.
- **SC-003**: Um código só é aproveitado uma vez, mesmo quando enviado simultaneamente por duas
  requisições.
- **SC-004**: O identificador de sessão após a autenticação difere do anterior em 100% dos acessos.
- **SC-005**: A resposta à solicitação do código, a janela de reenvio e o texto de espera são
  idênticos para endereço com e sem identidade.
- **SC-006**: O CPF não é solicitado em nenhum acesso recorrente, nem no primeiro acesso de quem não
  tem participação anterior.

### Medidas de preservação do que já existe

- **SC-007**: 100% das inscrições anteriores permanecem com o mesmo titular após a implantação, e
  nenhuma tem seu identificador estável alterado.
- **SC-008**: Após a implantação, a propriedade das inscrições não depende de nenhuma configuração
  que a operação possa alterar: mudá-la não muda o titular de nenhuma delas.
- **SC-009**: Um conjunto irreconciliável é relatado, não gera identidade, e suas inscrições
  permanecem intactas.
- **SC-010**: Uma inscrição enviada com CPF inutilizável interrompe a implantação com relatório; um
  rascunho na mesma condição é relatado e fica intacto. Depois disso, o banco recusa gravar inscrição
  enviada sem onze dígitos de CPF.
- **SC-010a**: Cinco confirmações de CPF erradas encerram a reconciliação daquele desafio, e a pessoa
  segue com identidade própria; um contador não é zerado por abrir outra aba, e nenhuma tentativa de
  terceiro impede o titular legítimo de reconciliar depois.
- **SC-011**: Nenhuma alteração de credencial, nome ou CPF altera qualquer inscrição enviada.

### Medidas de proteção

- **SC-012**: 100% das tentativas de acessar inscrição ou documento de outro candidato são recusadas
  com resposta que não permite descobrir a existência do objeto.
- **SC-013**: Conhecer um CPF, sem controlar um endereço com participação anterior a ele associada,
  não dá acesso a nenhuma inscrição nem cria vínculo com aquele CPF.
- **SC-014**: Nenhuma sessão de candidato alcança qualquer ação institucional.
- **SC-015**: Duas confirmações simultâneas do mesmo endereço produzem uma única credencial.
- **SC-016**: A movimentação de credenciais da FR-053 ocorre integralmente ou não ocorre: não existe
  estado em que a identidade tenha sido descartada e alguma credencial tenha ficado para trás.
- **SC-017**: Em produção, a aplicação recusa iniciar com mecanismo de envio conhecido por não
  entregar, ou sem remetente definido; e continua recusando a identificação por declaração.
- **SC-017a**: Em produção, a aplicação recusa iniciar enquanto a topologia de proxy não for
  declarada — nem `true`, nem `false`, nem valor que não seja um dos dois.

### Medidas de valor para o candidato

- **SC-018**: A lista mostra todas e somente as inscrições do candidato autenticado.
- **SC-019**: Um rascunho é retomado pela jornada existente sem que nenhum dado precise ser
  redigitado.
- **SC-020**: Nome e CPF são informados uma única vez por identidade, e nunca por quem tem
  participação anterior.
- **SC-021**: Uma única tela informa quais documentos foram efetivamente submetidos, e cada um deles
  é visualizável e baixável pelo titular.
- **SC-022**: O comprovante e as evidências de integridade permanecem disponíveis e inalterados.
- **SC-023**: O acompanhamento distingue fato pessoal de evento geral do cronograma, e nenhuma
  afirmação sobre a situação pessoal decorre apenas de uma data alcançada.
- **SC-024**: Retificação posterior ao envio não altera a versão aceita pela inscrição.
- **SC-025**: Quem recusou o convite de reconciliação por engano e ainda não abriu inscrição alguma
  consegue retomá-lo e recuperar o acesso à participação anterior.
- **SC-026**: Todo fluxo principal se conclui em tela de 375 px, sem rolagem horizontal, e somente
  pelo teclado.
- **SC-033**: Escolher a modalidade reservada mostra o documento a mais na mesma resposta, e a
  escolha sobrevive a sair e voltar.
- **SC-034**: Remover credencial pergunta antes; adicionar e remover avisam a credencial principal.
- **SC-035**: As duas telas de atendimento nomeiam o canal, e produção não sobe sem ele declarado.
- **SC-036**: Reconciliar, corrigir dados, adicionar e remover credencial e esgotar as tentativas de
  CPF produzem, cada um, uma frase na tela seguinte.
- **SC-037**: Falha no envio de documento aparece junto do documento, com o que fazer.
- **SC-028**: Depois de esgotadas as tentativas, o código correto é recusado com uma mensagem que
  diz que o código foi cancelado — e nunca com a de código incorreto.
- **SC-029**: Pedir outro código durante a janela de espera produz resposta escrita dizendo que nada
  foi enviado.
- **SC-030**: A inscrição enviada gera uma mensagem na caixa da credencial, com protocolo e código de
  verificação, e a sua falha não impede o envio.
- **SC-031**: O instante do envio é o mesmo na tela, no comprovante e no PDF.
- **SC-032**: A área do candidato é alcançável a partir da vitrine, com e sem sessão.
- **SC-027**: Nenhum candidato é recusado no envio por causa de CPF declarado por outra identidade, e
  a coincidência aparece assinalada, e não apenas legível, para quem conduz o certame.

## Assumptions

- **A parte local do endereço é tratada como insensível a caixa.** A norma a torna sensível, mas
  nenhum provedor em uso prático distingue `Maria@` de `maria@`, e tratá-las como credenciais
  distintas multiplicaria identidades por erro de digitação — um problema frequente trocado por um
  problema teórico. Fica registrado como suposição, e não como fato.
- **Os dados anteriores existem apenas em ambientes de desenvolvimento e demonstração.** A recusa de
  inicialização em produção impediu que a jornada do candidato rodasse lá. É o que torna
  desproporcional construir fluxo de revisão para conjuntos irreconciliáveis: interromper com
  relatório basta.
- **Quem controla um endereço usado numa participação anterior e conhece o CPF correspondente alcança
  aquela identidade.** É a consequência direta de e-mail ser a credencial, e o preço de não exigir
  prova de identidade mais forte numa versão sem provedor governamental. A alternativa — bloquear o
  endereço para sempre — puniria o dono legítimo de um endereço reciclado, o que é pior e mais
  provável.
- **Não existe teto global de envio de mensagens.** Limites por endereço e por origem cobrem o abuso
  realista; um teto global converteria ataque distribuído em indisponibilidade para todos.
- **O tempo de resposta não é indistinguível.** Igualá-lo exigiria enfileirar o envio, e a
  equivalência de resposta e de janela de reenvio basta para esta versão.
- **A recuperação de acesso permanece manual e institucional**, apoiada na consulta administrativa
  existente e na conferência documental que a instituição já pratica presencialmente.
- O canal destinado ao candidato é o navegador, e as demonstrações desta feature ocorrem nele.

## Out of Scope

Desta feature inteira, e sem exceção:

- **Inscrição**: campos novos, regras documentais novas, alteração ou cancelamento de inscrição
  enviada, substituição de documento pelo candidato, lógica nova de protocolo.
- **Avaliação**: comissão, banca, notas, documentos para avaliador, resultados, recursos,
  classificação — e a decisão sobre qual de duas inscrições coincidentes vale.
- **Comunicação**: qualquer mensagem que não seja o desafio de acesso; comprovante por e-mail, aviso
  de retificação, aviso de resultado, lembrete, SMS, aplicativos de mensagem e notificação por push.
- **Identidade**: senha, provedor governamental, segundo fator adicional, recuperação por dados
  pessoais, diretório institucional, candidato como grupo institucional e fusão de identidades.
- **Portal**: perfil cadastral, endereço postal, avatar, preferências, caixa de mensagens e painel
  genérico.
- **Arquitetura**: motor genérico de autenticação multicanal, plataforma genérica de contas,
  interface vazia para provedor futuro e botão que não funciona.

> **"Área do candidato" não autoriza construir um portal genérico**, e o núcleo mínimo da FR-004 —
> dois campos que a Inscrição já exigia — não é a primeira parcela de um cadastro.

## Invariantes de não regressão

Esta feature DEVE preservar: a vitrine pública, a jornada de inscrição, os documentos exigidos, o
envio privado de arquivos, o rascunho, a revisão, a submissão, a idempotência de abertura, o
protocolo, o comprovante, as evidências de integridade, a consulta administrativa e a titularidade
pelo identificador estável. A substituição do provedor de identidade é extensão planejada da `009`,
não reimplementação da sua jornada.

## Ordem de entrega

Cada linha termina em comportamento observável no navegador — o princípio VI da Constituição não
admite fatia que só exista no banco. Por isso a identidade persistente não é entrega separada: ela
chega junto com a porta que a torna visível.

| Entrega | O que se abre no navegador | Histórias |
|---|---|---|
| 1 | Reconciliação na implantação, desafio por e-mail e sessão: informar endereço, informar código, chegar a "Minhas inscrições" — inclusive o estado vazio | US1 |
| 2 | O convite de reconciliação: quem tem participação anterior reencontra suas inscrições confirmando o CPF uma vez | US2 |
| 3 | Núcleo mínimo da identidade e "Continuar inscrição": nome e CPF uma vez, rascunho retomado pela jornada existente | US3 |
| 4 | Detalhe da inscrição enviada: dados, versão, documentos, visualizar, baixar e comprovante | US4 |
| 5 | Acompanhamento: participação, cronograma e aviso de Edital atualizado | US5 |
| 6 | Credenciais: adicionar, remover, escolher a principal, corrigir nome e CPF; e o reforço dos limites, da auditoria e das recusas de inicialização | US6 |

## Demonstração de segurança obrigatória

Condição de conclusão, porque o maior risco introduzido por esta feature não é visual: é a tomada de
identidade.

1. **Endereçamento direto.** Trocar manualmente o identificador de uma inscrição ou de um documento
   para o de outro candidato não revela que ele existe.
2. **Endereço arbitrário com CPF conhecido.** Quem controla um endereço próprio e conhece o CPF de
   outra pessoa entra numa área vazia, sem ver nada dela e sem criar vínculo com aquele CPF.
3. **Precedência.** Agir antes do titular não reserva o CPF dele; e uma inscrição enviada por
   terceiro declarando aquele CPF não impede a inscrição legítima.
4. **Endereço reciclado.** Quem hoje controla um endereço digitado por engano anos atrás entra
   normalmente, na própria identidade, e a identidade anterior permanece intacta.
5. **Engano no convite.** Quem recusou a reconciliação e ainda não abriu inscrição retoma o convite e
   recupera o acesso.
6. **Sessão conhecida.** Uma sessão obtida antes do acesso não continua válida depois dele.

## Instruções para o `/speckit-plan`

> Esta feature evolui a identidade do candidato e adiciona uma área pessoal sobre capacidades já
> entregues pela `009`.
>
> Não reimplemente Inscrição, envio de arquivo, comprovante ou armazenamento.
>
> Preserve o contrato que a abertura de rascunho consome; troque apenas quem o preenche.
>
> Preserve intacta a restrição de uma inscrição por identidade, Edital e Perfil: ela sustenta a
> idempotência de abertura.
>
> Reconcilie os dados anteriores por migração, na implantação, e nunca reescreva o identificador
> estável de uma inscrição.
>
> Não derive identidade nova de segredo rotacionável nem de dado pessoal.
>
> Não vincule CPF por afirmação em nenhum caminho, e não trate CPF como segredo nem como fator de
> autenticação.
>
> Não bloqueie envio por CPF coincidente: detecte, assinale e mostre a quem conduz o certame.
>
> Guarde desafios e contadores de forma compartilhada entre processos, com consumo atômico e rotação
> de sessão na autenticação.
>
> Garanta a exclusividade do endereço canônico pela persistência, e normalize de forma conservadora.
>
> A única movimentação de credencial permitida é a da FR-053, e só a partir de identidade sem
> inscrição alguma: verificar, mover e descartar são uma operação só. Nada mais transfere, funde ou
> abandona identidade.
>
> Trate a inauguração do canal de e-mail como parte da feature, com recusa de inicialização no estilo
> das existentes — recusando o que se sabe não entregar, sem alegar provar entrega.
>
> Não transforme a identidade do candidato em sistema genérico de contas, nem o desafio em framework
> de autenticação multicanal.
>
> Nenhum caminho de credencial termina em beco sem saída: provar um endereço sempre produz sessão, e
> a decisão de reconciliar acontece antes de o vínculo existir.
>
> Cada fatia termina em comportamento observável no navegador.
>
> Havendo escolha entre uma abstração genérica de contas e uma solução estreita para a Área do
> Candidato, escolha a estreita.
