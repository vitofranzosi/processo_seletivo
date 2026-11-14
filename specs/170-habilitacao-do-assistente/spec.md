# Feature Specification: A habilitação do assistente do Edital pela interface do sistema

**Feature Branch**: `claude/170-habilitacao-do-assistente-12c936`, sobre a `main` em `7d5c6ade`
(com a `166` mergeada)

**Created**: 2026-11-14

**Status**: Especificada em 14/11. Revista no mesmo dia com as respostas do usuário às perguntas Q-1
a Q-4 e com o recorte da entrega. Planejada; a implementação espera a aprovação do plano.

**Input**: a decisão do usuário de 14/11/2026, ao discutir a verificação por vídeo da `166`: *"a
habilitação poderia ser via interface no sistema; o mesmo se aplica ao assistente de IA"*. Ele pediu
duas specs. A `169` é a do vídeo, e esta é a do assistente. As duas seguem o mesmo princípio: o
ambiente guarda a **configuração técnica**, e a **decisão** institucional se registra na interface.
Em 14/10, na auditoria que gerou a `073`, o usuário já tinha recusado a conclusão "nenhuma
interface" para as configurações.

**O recorte do usuário, na revisão de 14/11:** o objetivo é habilitar o assistente pela interface e
testá-lo na gestão e na página pública de um Edital. O sistema ainda não está em produção. *"A
entrega não pode terminar apenas numa tela que informa por que não é possível habilitar."* Fora de
produção, habilitar pela interface basta. Produção continua impedindo a abertura pública enquanto os
requisitos estiverem pendentes.

> **Faixa de identificadores.** Esta spec abre em FR-7500, SC-2450 e UX-810. Os tetos medidos em
> 14/11/2026 eram estes: na `main`, o requisito sete mil cento e cinquenta e três, o critério dois
> mil trezentos e setenta e sete e o requisito de experiência setecentos e setenta e quatro, todos
> da `166`. As specs abertas em paralelo reservaram as faixas delas: a `167` (#548), a `168` e a
> `169`. Fica reservada a faixa até o requisito sete mil quinhentos e noventa e nove, até o critério
> dois mil quatrocentos e sessenta e nove e até o requisito de experiência oitocentos e dezenove.
> As decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature, por exemplo "a FR-1464 da `071`". Uma decisão de outra feature é citada pelo assunto e
> pela feature. As decisões pendentes da `071` (DP-1 a DP-7) e as da auditoria do assistente (DA-01
> a DA-10) se citam pelo nome que têm lá. Os requisitos da abertura em produção definidos aqui são
> `RA-1` a `RA-12`.

---

## Por que esta feature existe

### O problema

Hoje a decisão de usar o assistente mora no ambiente e no código. Duas chaves globais decidem tudo:

- **`ASSISTENTE_PILOTO`** liga o piloto interno da gestão (`071`). Produção aceita a chave ligada só
  com o serviço local `ollama` e com tempo-limite de até 110 s.
- **`ASSISTENTE_NA_PAGINA_DO_EDITAL`** abre o painel na página pública da seleção (`074`). Produção
  recusa subir com ela, porque a abertura ao público depende de requisitos que a `074` deixou para
  a implantação (a FR-1684 da `074`).

São três defeitos, e nenhum deles é de código:

1. **Quem decide é quem edita o arquivo de ambiente.** Ligar o assistente é uma decisão
   institucional: custa GPU, expõe uma resposta não oficial a quem pergunta e grava texto livre.
   Hoje ela não tem autor, motivo nem data, e some quando alguém edita o arquivo.
2. **Não há como abrir um Edital e não outro.** A auditoria do assistente recomendou "chave global
   mais lista de Editais habilitados" (DA-10, opção b), para começar por um certame. A decisão nunca
   foi tomada (AS-17 da matriz de 15/10).
3. **Os requisitos da abertura ao público estão espalhados** pela `071`, pela `074`, pela auditoria
   do assistente e pela matriz de pendências (AS-15). Nenhum lugar os junta.

### O que esta feature faz

- **A configuração técnica fica no ambiente.** Serviço, endereço, modelo, tokenizer, credencial e
  tempo-limite dependem da máquina, e segredo nunca vai para o banco.
- **A decisão vai para a interface.** Habilitar e desabilitar passam a ser atos do Administrador
  institucional, numa página da administração institucional que já existe, a mesma das Unidades
  (`110`). Cada ato tem motivo e trilha, e nada se exclui.
- **Fora de produção, habilitar pela interface basta.** Sem chave de demonstração e sem os
  requisitos da abertura, o administrador habilita o piloto ou a página pública de um Edital. Quem
  tem o papel conversa pela gestão, e um visitante sem login conversa na página pública. Outro
  Edital continua sem o assistente. Desabilitado, nenhuma pergunta nova chega ao modelo.
- **Em produção, a página pública continua fechada.** O backend confere o ambiente pela configuração
  que o projeto já tem. A recusa nomeia os doze requisitos pendentes, e um registro gravado fora de
  produção não abre o painel em produção.

### Duas frentes, que não se confundem

| | **Piloto da gestão** (`071`) | **Página pública** (`074`) |
|---|---|---|
| Quem conversa | quem tem o papel Participante do piloto e alcança o Edital na gestão | qualquer visitante da página pública da seleção |
| Hoje | `ASSISTENTE_PILOTO`, aceito em produção com o `ollama` | `ASSISTENTE_NA_PAGINA_DO_EDITAL`, recusado em produção |
| Alcance da habilitação (Q-1) | **uma por implantação** | **por Edital** |
| Fora de produção | habilitação pela interface | habilitação pela interface |
| Em produção | habilitação pela interface; sessões acompanhadas (Q-3) | **fechada**: recusa que nomeia os requisitos |
| Registro das conversas | `TrocaDoPiloto`, excluída 90 dias depois do relatório final | o mesmo, como na `074` |

### O que esta entrega cobre, e o que fica para a abertura em produção

**Entra:**

- o que cada variável `ASSISTENTE_*` e cada recusa do `production.py` passam a ser (tabela em
  *O ambiente depois desta feature*);
- a leitura da configuração na interface, sem valor secreto e sem chamar o modelo;
- a habilitação do piloto, uma por implantação, e a da página pública, por Edital;
- a separação entre produção e o resto, conferida no backend;
- a regra de desabilitar com conversas em curso;
- a lista dos doze requisitos da abertura em produção, documentada e rastreável;
- o que a `071` e a `074` deixam de valer.

**Fica para a entrega da abertura em produção**, por decisão do usuário, para evitar
overengineering:

- o cadastro dos requisitos pela interface, a retirada deles, o vencimento dos requisitos de um Edital
  por Retificação e os efeitos de uma retirada em vários Editais;
- os requisitos de software (`RA-8` a `RA-12`): limite por visitante, textos definitivos, correção do
  documento ligado, emenda do canal da `070` e retenção dos registros públicos;
- uma política de retenção de produção para as conversas de visitantes.

**Fica fora, de propósito:**

- **editar configuração pela interface**, ou guardar segredo no banco. É o que a `073` deixou fora;
- **verificar a conexão ou chamar o modelo a partir da página.** Esses testes continuam nos comandos
  da `073`, a pedido de quem opera;
- **painel genérico de configurações**, tela fora da administração institucional, mecanismo
  compartilhado com a `169` e gestão de conversas;
- **habilitação por unidade.** Para o piloto, quem participa já é decidido por unidade, ao conceder
  o papel;
- **mudar as sessões acompanhadas do piloto** (Q-3).

---

## Clarifications

### Session 2026-11-14 (restrições do pedido)

- Não criar estruturas paralelas às que existem. Evitar overengineering. Toda abstração, papel,
  tabela ou mecanismo novo precisa resolver um problema concreto. É a regra que o usuário fixou na
  `110`.
- A decisão vai para o padrão do Administrador institucional que já existe, como a tela de Unidades
  da `110`: motivo, trilha, nada se exclui, e habilitar ou desabilitar é registro append-only.
- Negar por padrão: só o papel certo habilita, e o escopo é conferido.
- A regra de exclusão do piloto da `071` não muda.
- Governança e merge são do usuário.

### Session 2026-11-14 (respostas do usuário, na revisão do PR #553)

- Q: Qual é o alcance da habilitação (Q-1)? → A: o piloto da gestão se habilita uma vez por
  implantação, e a página pública, por Edital.
- Q: Quem habilita (Q-2)? → A: o Administrador institucional, com permissão explícita no papel que
  já existe, motivo e histórico.
- Q: Habilitado, o piloto deixa de exigir sessões acompanhadas (Q-3)? → A: **não**. As sessões
  acompanhadas ficam, por enquanto. Esta entrega não precisa alterá-las para permitir os testes.
- Q: O que acontece com `ASSISTENTE_PILOTO` (Q-4)? → A: pode continuar como atalho de demonstração
  local, mas o percurso pela interface tem de funcionar sem ele.
- Q: Os requisitos da abertura bloqueiam os testes? → A: não fora de produção. Os controles de acesso,
  a proteção da credencial e os limites de uso continuam. Produção continua impedindo a abertura
  pública enquanto os requisitos estiverem pendentes, e a separação usa a configuração de ambiente
  que o projeto já tem, conferida no backend.
- Q: O cadastro dos requisitos entra agora? → A: não. Os doze ficam documentados e rastreáveis, e o
  cadastro, a retirada, o vencimento por Retificação e os efeitos em vários Editais ficam para a
  entrega da abertura em produção.
- Q: O que a página diz sobre o serviço? → A: diz se a configuração está completa, ou o que falta.
  Ela não afirma que o serviço está disponível sem verificar a conexão, e abri-la não chama o modelo.
- Q: Como ficam as conversas da página pública fora de produção? → A: como a `074` já prevê, sem
  criar política de retenção de produção nesta entrega.

---

## User Scenarios & Testing *(mandatory)*

**Ator principal:** o **Administrador institucional**, com sessão institucional e escopo ativo
institucional, que é o papel da `106`, renomeado na `110`. **Atores afetados:** quem participa do
piloto, quem visita a página pública da seleção e a equipe da unidade do Edital.

### User Story 1 — O administrador vê se a configuração está completa (Priority: P1)

O Administrador institucional abre a página "Assistente do Edital" na administração institucional.
Ela diz se a configuração do serviço está completa e, se não estiver, o que falta. Ela não diz que o
serviço está disponível, porque não verifica a conexão. Nada do que ela mostra é segredo, e abri-la
não chama o modelo.

**Why this priority**: sem a configuração, nenhuma habilitação atende. É a fronteira entre o que é
da máquina e o que é da instituição.

**Independent Test**: num ambiente sem serviço declarado, num com serviço sem tokenizer e num
completo, abrir a página e comparar o que ela diz. Conferir que nenhum valor de credencial aparece e
que o serviço não recebeu chamada.

**Acceptance Scenarios**:

1. **Given** nenhum serviço declarado, **When** o administrador abre a página, **Then** ela diz que
   o serviço do modelo não está configurado, e não oferece habilitar nenhuma das frentes.
2. **Given** o serviço, o endereço e o modelo declarados, mas sem o arquivo do tokenizer, **When**
   ele abre a página, **Then** ela diz "falta o tokenizer do modelo" e não oferece habilitar.
3. **Given** a configuração completa e uma credencial presente, **When** ele abre a página, **Then**
   ela diz "configuração completa", mostra o serviço, o modelo e o tempo-limite, diz só
   "credencial: presente", lembra que a conexão se verifica pelo comando da `073`, **and** o serviço
   não recebe chamada.
4. **Given** uma pessoa com papel de unidade, ou com a sessão de demonstração, **When** ela pede o
   endereço da página, **Then** recebe a recusa, e nada é lido.

---

### User Story 2 — Habilitar e testar o piloto pela gestão (Priority: P1)

Num ambiente de testes, com o serviço configurado e sem nenhuma chave de demonstração ligada, o
administrador habilita o piloto, com motivo. A partir da requisição seguinte, sem reinício, quem tem
o papel Participante do piloto vê o assistente na página dos Editais que alcança, e conversa.
Depois, o administrador desabilita, e a entrada desaparece.

**Why this priority**: é o primeiro passo do percurso que o usuário pediu.

**Independent Test**: com as duas chaves de demonstração desligadas, habilitar e conferir que a
entrada aparece para quem tem o papel e não para os outros. Fazer uma pergunta. Desabilitar e
conferir a negativa. Conferir os dois atos no histórico e na trilha.

**Acceptance Scenarios**:

1. **Given** a configuração completa, o piloto desabilitado e `ASSISTENTE_PILOTO` desligado, **When**
   o administrador confirma a habilitação com motivo, **Then** o ato é gravado com autor, instante e
   motivo, **and** quem tem o papel vê a entrada do assistente na página do Edital, na requisição
   seguinte, e a pergunta chega ao modelo.
2. **Given** o piloto habilitado, **When** uma pessoa sem o papel abre o endereço do assistente,
   **Then** recebe a mesma negativa de hoje (a FR-1460 da `071`).
3. **Given** o piloto habilitado, **When** o administrador o desabilita com motivo, **Then** a
   entrada some, **and** o endereço direto recebe a negativa, **and** nenhuma pergunta nova chega ao
   modelo, **and** nenhuma troca registrada é alterada.
4. **Given** a confirmação sem motivo, **When** ele confirma, **Then** a interface recusa, nada é
   gravado, e ele volta à mesma confirmação.

---

### User Story 3 — Habilitar e testar a página pública de um Edital (Priority: P1)

No mesmo ambiente, o administrador escolhe um Edital com página pública e o habilita, com motivo. Um
visitante sem login abre a página da seleção daquele Edital, abre o painel e conversa. Na página de
outro Edital, o painel não aparece. A equipe da unidade vê, na página do Edital na gestão, que o
assistente está aberto na página pública.

**Why this priority**: é a parte do percurso que a `074` só oferecia por chave, e o centro do pedido.

**Independent Test**: com a chave de demonstração desligada, habilitar o Edital A. Como visitante sem
sessão, conversar no A e conferir que o B não traz o painel e que as rotas dele respondem 404.

**Acceptance Scenarios**:

1. **Given** a configuração completa, fora de produção e com a chave de demonstração desligada,
   **When** o administrador confirma a habilitação do Edital A com motivo, **Then** a página pública
   do A oferece o painel da `074` na requisição seguinte.
2. **Given** o A habilitado, **When** um visitante sem login escolhe uma sugestão e faz uma pergunta
   livre, **Then** recebe as respostas como na `074`, com os mesmos limites.
3. **Given** o A habilitado e o B não, **When** o visitante abre a página do B ou envia para as rotas
   do assistente do B, **Then** a página não traz o painel e as rotas respondem 404.
4. **Given** o A habilitado, **When** a equipe da unidade abre o A na gestão, **Then** vê que o
   assistente está aberto na página pública dele, desde quando e por qual ato.

---

### User Story 4 — Desabilitar com conversas em curso (Priority: P1)

Um visitante está conversando na página do Edital A quando o administrador desabilita o A. A pergunta
que já estava com o modelo termina e é registrada. Na pergunta seguinte, nada chega ao modelo: o
visitante vê que o assistente desta seleção foi encerrado e é levado às informações oficiais. Se o A
for habilitado de novo, a conversa recomeça do zero.

**Why this priority**: é o último passo do percurso, e o pedido exige a regra.

**Independent Test**: com uma conversa aberta, desabilitar, enviar outra pergunta e conferir o aviso
e a ausência de chamada. Habilitar de novo, enviar e conferir que o histórico anterior não entrou na
chamada.

**Acceptance Scenarios**:

1. **Given** uma pergunta com o modelo, **When** a desabilitação é confirmada, **Then** a pergunta
   termina, e a troca é registrada como hoje.
2. **Given** a desabilitação confirmada, **When** o visitante envia outra pergunta, **Then** recebe a
   página da seleção sem o painel, com o aviso de que o assistente desta seleção foi encerrado,
   **and** nada chega ao modelo.
3. **Given** o A desabilitado e depois habilitado de novo, **When** o mesmo visitante pergunta,
   **Then** a conversa é nova, e nenhuma troca anterior à desabilitação entra como histórico.
4. **Given** o piloto desabilitado no meio da conversa de um participante, **When** ele envia outra
   pergunta, **Then** recebe a negativa da FR-1464 da `071`, e nada chega ao modelo.

---

### User Story 5 — Produção continua fechada para o público (Priority: P1)

Em produção, o administrador pode habilitar o piloto. Se pedir a habilitação da página pública de um
Edital, recebe uma recusa que nomeia os doze requisitos da abertura pendentes, e nada é gravado.
Mesmo que o banco traga uma habilitação gravada fora de produção, o painel não aparece.

**Why this priority**: é a condição que o usuário pôs para abrir os testes sem os requisitos.

**Independent Test**: com as configurações de produção, pedir a habilitação de um Edital e conferir
a recusa. Gravar uma habilitação diretamente no banco e conferir que a página e as rotas continuam
como com o assistente desligado. Conferir as recusas de inicialização.

**Acceptance Scenarios**:

1. **Given** as configurações de produção, **When** o administrador pede a habilitação da página
   pública de um Edital, **Then** recebe a recusa que lista `RA-1` a `RA-12`, **and** nada é gravado.
2. **Given** as configurações de produção e uma habilitação de Edital no registro, **When** um
   visitante abre a página da seleção ou envia para as rotas do assistente, **Then** a página não
   traz o painel, as rotas respondem 404, e nada chega ao modelo.
3. **Given** `ASSISTENTE_PILOTO=true`, ou um serviço externo, ou um tempo-limite acima de 110 s, nas
   configurações de produção, **When** o processo inicia, **Then** a inicialização é recusada, com a
   variável nomeada.

---

### User Story 6 — A demonstração local continua (Priority: P3)

Na máquina de desenvolvimento, quem testa sem sessão institucional liga a chave de demonstração, como
hoje, e não precisa de registro de habilitação.

**Why this priority**: preserva o fluxo local da `071` e da `074` e as entradas do
`.claude/launch.json`. Não é o caminho principal desta entrega.

**Independent Test**: com cada chave ligada fora de produção e nenhum registro, conferir o piloto e
o painel.

**Acceptance Scenarios**:

1. **Given** `ASSISTENTE_PILOTO=true` fora de produção e nenhum registro, **When** quem tem o papel
   abre o assistente, **Then** ele atende, se a configuração estiver completa.
2. **Given** `ASSISTENTE_NA_PAGINA_DO_EDITAL=true` fora de produção, **When** um visitante abre a
   página de qualquer seleção, **Then** o painel aparece, como na `074`.

---

### Edge Cases

Cada caso aqui é requisito, e aponta o requisito que o governa.

- **Habilitação pedida sem configuração completa**, por envio montado à mão: o pedido é recusado com
  o que falta, e nada é gravado (FR-7501, FR-7514, FR-7517).
- **Configuração retirada com uma frente habilitada**: o registro continua habilitado, nada atende, e
  a página diz as duas coisas. Quando a configuração volta, a frente volta a atender sem novo ato
  (FR-7504).
- **Configuração incompleta**: o sistema inicia normalmente, e o assistente não atende (FR-7503).
- **Serviço externo declarado em produção, com o piloto desligado**: hoje passa; depois desta
  feature, a inicialização é recusada (FR-7505).
- **Banco de testes levado para produção com Editais habilitados**: o painel não aparece, porque
  produção é conferida a cada requisição (FR-7519).
- **Dois administradores confirmam atos contrários ao mesmo tempo**: um vale, e o outro recebe uma
  recusa que diz que o estado mudou (FR-7531).
- **Habilitar o que já está habilitado**, ou desabilitar o desabilitado: o pedido é recusado sem
  gravar (FR-7530).
- **Edital habilitado que perde a página pública**, por estar encerrado ou sem seleção pública: o
  painel não aparece, porque a página não existe. A habilitação continua no registro, e a página do
  administrador diz "sem página pública" (FR-7520).
- **Pergunta em curso no instante da desabilitação**: ela termina e é registrada. A resposta não é
  mostrada depois, porque a próxima requisição já segue a decisão nova (FR-7524).
- **Chave de demonstração ligada e frente desabilitada no registro**, fora de produção: a chave
  atende, como hoje. Ela não altera o registro, e a página do administrador diz que a demonstração
  está ligada (FR-7506, FR-7507).
- **O papel do administrador revogado, ou a pessoa suspensa** (`107`): os atos que ela praticou
  continuam valendo, e a pessoa não pratica outros (FR-7511).
- **Unidade do Edital desativada** (`110`): o Edital em curso continua, e a habilitação dele também
  (FR-7517).
- **Visitante que descarta o cookie para escapar do teto de conversas**: continua possível, como na
  `074`. O limite por visitante é o `RA-8`, da abertura em produção (FR-7521).

---

## Requirements *(mandatory)*

### Functional Requirements

#### A configuração, no ambiente

- **FR-7500**: O serviço, o endereço, o modelo, o tokenizer, a credencial, o tempo-limite e os
  parâmetros e limites da inferência MUST continuar só no ambiente, nas variáveis `ASSISTENTE_*` que
  já existem (tabela em *O ambiente depois desta feature*). Nenhuma delas MUST ser gravada no banco
  nem editada pela interface. A credencial MUST NOT aparecer em página, histórico, trilha ou log.
- **FR-7501**: A configuração do serviço MUST ser **completa** quando todas estas condições valem:
  - o serviço declarado é um dos conhecidos;
  - o endereço e o modelo estão declarados;
  - o arquivo do tokenizer existe e pode ser lido;
  - a credencial está presente, se o serviço a exigir.

  A conferência MUST ser feita no servidor a cada requisição que a usa, e MUST NOT contatar o
  serviço.
- **FR-7502**: A página MUST dizer "configuração completa" ou o que falta. MUST NOT afirmar que o
  serviço está disponível, porque não verifica a conexão. Abri-la MUST NOT chamar o modelo.
- **FR-7503**: Configuração incompleta MUST NOT impedir a inicialização. Um servidor sem assistente é
  legítimo, e um assistente mal configurado não pode derrubar as inscrições.
- **FR-7504**: Sem configuração completa, nenhuma frente MUST atender, qualquer que seja o registro.
  O registro MUST NOT ser alterado por isso. Quando a configuração voltar, a frente habilitada MUST
  voltar a atender sem novo ato.
- **FR-7505**: Em produção, as recusas de serviço externo e de tempo-limite acima de 110 s MUST valer
  sempre que houver serviço declarado, independentemente de qualquer chave. Hoje elas só valem com
  `ASSISTENTE_PILOTO` ligado. A mensagem de cada uma MUST continuar nomeando a variável.

#### As chaves de demonstração local

- **FR-7506**: `ASSISTENTE_PILOTO` MUST passar a ser um atalho de demonstração local. Ligado fora de
  produção, ele dispensa o registro de habilitação do piloto, e só isso: o papel, o alcance do Edital
  e a configuração continuam exigidos. Produção MUST recusar subir com ele ligado, com uma mensagem
  que diz que a habilitação é um ato na administração institucional.
- **FR-7507**: `ASSISTENTE_NA_PAGINA_DO_EDITAL` MUST continuar a chave de demonstração da `074`, sem
  mudança, e produção MUST continuar recusando-a (a FR-1683 da `074`).
- **FR-7508**: O percurso pela interface MUST funcionar com as duas chaves desligadas. Fora de
  produção, a habilitação registrada MUST bastar para as duas frentes.
- **FR-7509**: O comando de avaliação do piloto MUST exigir a configuração completa, e não a
  habilitação nem a chave. A avaliação é operação da equipe, e não uso por pessoas.

#### Quem habilita

- **FR-7510**: A permissão `assistente:habilitar` MUST pertencer ao papel Administrador institucional,
  e só a ele. MUST NOT pertencer a papel de unidade nem a papel do seletor de demonstração. Nenhum
  papel, tela de designação ou mecanismo de concessão novo MUST ser criado. Antes do deploy, todo
  vínculo vigente desse papel MUST ser identificado, e a ampliação MUST NOT chegar a quem o tem sem a
  autorização expressa do usuário, como na `110`.
- **FR-7511**: Todo ato e toda leitura desta feature MUST exigir `assistente:habilitar` com o escopo
  ativo institucional, conferidos na camada de aplicação, e a tela é só a segunda barreira. A sessão
  de demonstração MUST receber a recusa antes de qualquer leitura, como na FR-3312 da `110`. Os atos
  já praticados por quem perdeu o papel ou foi suspenso MUST continuar valendo.
- **FR-7512**: `assistente:habilitar` MUST NOT conferir nenhuma outra capacidade. Ela não dá o uso do
  piloto (`assistente:piloto`), nem ato sobre Processo, Edital ou Publicação. Para escolher o Edital,
  ela permite ler só a identificação pública dos Editais que têm página pública: número, ano,
  unidade e título.

#### O lugar na interface

- **FR-7513**: A feature MUST ter uma página só, "Assistente do Edital", na administração
  institucional, ao lado de Unidades e da administração de acessos. A barra MUST oferecê-la só a quem
  tem a permissão. A página MUST mostrar a configuração, o estado do piloto, os Editais com a página
  pública habilitada, a lista dos requisitos da abertura em produção e o histórico. MUST NOT existir
  painel genérico de configurações, nem edição de valores do ambiente.

#### O piloto da gestão

- **FR-7514**: O piloto MUST ter uma habilitação por implantação (Q-1). Habilitar e desabilitar MUST
  passar por uma confirmação com motivo. Sem configuração completa, a habilitação MUST NOT ser
  oferecida, e um pedido montado à mão MUST ser recusado com o que falta.
- **FR-7515**: O piloto MUST atender quando valem todas estas condições:
  - há habilitação vigente, ou o atalho de demonstração está ligado fora de produção;
  - a configuração está completa;
  - valem as duas condições da FR-1460 da `071`: o alcance do Edital e a permissão do piloto.

  A tela, a entrada na página do Edital e o protótipo da Fase C MUST aplicar a mesma regra, e a
  entrada só aparece onde a tela atenderia. A negativa da FR-1460 e da FR-1464 da `071` MUST
  continuar a mesma.
- **FR-7516**: A habilitação do piloto MUST NOT exigir os requisitos da abertura, e MUST NOT mudar a
  regra das sessões acompanhadas (a FR-1463 da `071`, Q-3).

#### A página pública, por Edital

- **FR-7517**: A habilitação da página pública MUST ser por Edital (Q-1), só para Edital com página
  pública, e MUST exigir a configuração completa. A situação da unidade do Edital MUST NOT entrar na
  conferência.
- **FR-7518**: Fora de produção, os requisitos da abertura MUST NOT ser conferidos. Em produção, a
  habilitação da página pública MUST ser recusada, a recusa MUST nomear os doze requisitos pendentes,
  e nada é gravado. A distinção MUST vir da configuração de ambiente que o projeto já tem, a de
  produção. MUST ser conferida no backend, e MUST NOT poder ser desfeita por variável de ambiente
  nem pela interface.
- **FR-7519**: Em produção, a página pública MUST NOT oferecer o painel, e as rotas do assistente MUST
  responder 404, mesmo com uma habilitação no registro. A conferência MUST acontecer a cada
  requisição.
- **FR-7520**: Fora de produção, a página pública de um Edital MUST oferecer o painel quando há
  habilitação vigente do Edital, ou a chave de demonstração ligada, e a configuração está completa,
  tudo conferido a cada requisição. Fora disso, a página e as rotas MUST se comportar como na `074`
  com a chave desligada, salvo o aviso da FR-7524. Um Edital habilitado sem página pública MUST
  aparecer assim na página do administrador.
- **FR-7521**: O painel e os envios MUST continuar os da `074` (a FR-1681 da `074`), com os limites da
  FR-1685 da `074`: tamanho da pergunta, turnos por conversa, teto de chamadas simultâneas, conversas
  por sessão e limite de gasto da credencial. Nenhuma arquitetura de conversa nova.
- **FR-7522**: A página do Edital na gestão MUST dizer, a quem a alcança, se o assistente está aberto
  na página pública daquele Edital, desde quando, ou que não está.

#### Desabilitar com conversas em curso

- **FR-7523**: A habilitação MUST ser conferida no servidor a cada requisição: ao mostrar a página, a
  cada pergunta, a cada sugestão e a cada nova conversa. A decisão MUST NOT ser guardada de uma
  requisição para outra.
- **FR-7524**: Uma chamada ao modelo já iniciada MUST terminar e ser registrada como hoje. Depois da
  desabilitação, nenhuma pergunta nova MUST ser enviada ao modelo:
  - o visitante da página pública recebe a página sem o painel, com o aviso de que o assistente desta
    seleção foi encerrado;
  - o participante do piloto recebe a negativa da FR-1464 da `071`.
- **FR-7525**: Depois de uma desabilitação, a habilitação seguinte MUST começar conversa nova: as
  trocas anteriores à desabilitação MUST NOT entrar como histórico.
- **FR-7526**: Desabilitar MUST NOT alterar nem excluir troca registrada.

#### O registro

- **FR-7527**: Cada ato de habilitar ou desabilitar MUST ser gravado num registro append-only, com as
  duas camadas independentes do projeto: o gatilho e a ausência de privilégio. A tabela nova MUST
  entrar na contagem `N de M` do provisionamento.
- **FR-7528**: Todo ato MUST exigir motivo preenchido depois de aparados os espaços. Sem motivo, a
  interface MUST recusar sem gravar.
- **FR-7529**: Todo ato MUST gerar um evento na trilha, na mesma transação. O ato sobre um Edital MUST
  ser legível na trilha da unidade do Edital.
- **FR-7530**: Um ato que não muda nada MUST ser recusado sem gravar: habilitar o que está habilitado,
  ou desabilitar o que está desabilitado.
- **FR-7531**: A confirmação MUST reconferir no servidor tudo o que a primeira etapa conferiu. Dois
  atos simultâneos sobre a mesma frente ou o mesmo Edital MUST ser serializados, e o segundo MUST
  receber uma recusa que diz que o estado mudou.
- **FR-7532**: O estado de cada frente e de cada Edital MUST ser o do último ato que o afeta. O
  histórico MUST mostrar todos os atos, do mais recente para o mais antigo, com autor pelo nome,
  instante e motivo.

#### Os requisitos da abertura em produção

- **FR-7533**: Os doze requisitos da abertura em produção MUST ficar documentados nesta spec, na
  tabela *Os requisitos da abertura em produção*, com a espécie e a origem de cada um. A página do
  administrador MUST listá-los como pendentes. A recusa de produção MUST nomeá-los (FR-7518). Nesta
  entrega, nenhum requisito MUST ser registrável, retirável ou dispensável pela interface.

#### Os registros das conversas

- **FR-7534**: A exclusão dos registros do piloto 90 dias depois do relatório final (a FR-1509 da
  `071`) MUST continuar a mesma: o mesmo comando, o mesmo prazo e a mesma âncora. Desabilitar MUST
  NOT valer como relatório final.
- **FR-7535**: Fora de produção, as conversas da página pública MUST ser registradas como a `074`
  prevê, na mesma tabela e sem a identidade de quem pergunta. Nenhuma política de retenção de produção
  MUST ser criada nesta entrega. Em produção, a página pública fechada (FR-7519) impede que conversa
  de visitante seja gravada.

#### Documentação

- **FR-7536**: O guia de implantação, o `CLAUDE.md`/`AGENTS.md` (as seções da `071` e da `074`), o
  `.env.example` e o roteiro do quickstart da `071` MUST dizer o que mudou: a configuração fica no
  ambiente, a decisão é um ato na administração institucional, os atalhos de demonstração são
  recusados em produção, a página pública continua fechada em produção, e a autorização da ampliação
  do papel é pedida antes do deploy.
- **FR-7537**: A implementação MUST acrescentar à `071` e à `074` uma nota em cada requisito revisto,
  apontando para esta spec, como a `074` fez na FR-1462 da `071`.

### Requisitos de experiência

- **UX-810**: A configuração MUST ser dita em palavras de quem decide. Por exemplo: "configuração
  completa" ou "falta o tokenizer do modelo". Ela MUST NOT ser dita por nome de variável, que aparece
  só como detalhe para quem opera. Com a configuração completa, a página MUST lembrar que a conexão se
  verifica pelo comando da `073`.
- **UX-811**: A recusa de produção MUST dizer que a página pública não abre em produção enquanto os
  requisitos da abertura estiverem pendentes, e MUST listá-los pelo nome.
- **UX-812**: Toda confirmação MUST dizer a consequência antes do motivo. Para habilitar o piloto:
  "quem tem o papel Participante do piloto passa a ver o assistente na página dos Editais que
  alcança". Para habilitar um Edital: "qualquer visitante da página pública deste Edital passa a
  conversar com o assistente". Para desabilitar: "nenhuma pergunta nova chega ao modelo; as
  conversas não continuam; os registros não são apagados".
- **UX-813**: O aviso ao visitante cuja conversa foi encerrada MUST dizer que o assistente desta
  seleção foi encerrado, e levar às informações oficiais da página. MUST NOT sugerir erro do
  visitante nem pedir que ele tente de novo.
- **UX-814**: A linha da página do Edital na gestão MUST usar a mesma linguagem da página do
  administrador.

### Os requisitos da abertura em produção

A lista vem da `071` (o portão da Fase C e os critérios de conclusão), da `074` (as pendências para a
implantação), da auditoria do assistente de 12/10 e da matriz de pendências de 15/10. Nenhum
requisito foi acrescentado além dessas fontes. O `RA-12` explicita uma consequência delas, como diz a
coluna da origem. **Nesta entrega a lista é documentação e recusa nomeada.** O cadastro fica para a
entrega da abertura em produção (FR-7533).

| ID | Requisito | Espécie | Origem |
|---|---|---|---|
| `RA-1` | Relatório final do piloto, com os critérios da DP-3 aprovados e cumpridos | institucional | `071`, critérios de conclusão e "concluído não é aprovado para a Fase C"; AS-08 |
| `RA-2` | Revisão institucional da Fase A com o setor de seleção (a T046 da `070`) | institucional | `071`, Fase C; AS-01 |
| `RA-3` | Manifestação do encarregado de dados sobre o texto livre de candidatos reais e o prazo de retenção dos registros da página pública | institucional | `071`, LGPD; pendências da `074`; DA-09; AS-18 |
| `RA-4` | Texto aprovado que declara a natureza não oficial das respostas | institucional | `071`, Fase C; DA-01; DEP-08 da auditoria; AS-04 |
| `RA-5` | Medição da carga pública no serviço local, com a decisão sobre isolar a inferência | institucional | a decisão sobre o isolamento dos workers da `071`; DEP-06 da auditoria; AS-16 |
| `RA-6` | A cláusula "esclarecimentos exclusivamente por e-mail" resolvida no Edital | por Edital | `071`, Fase C; DA-02; AS-03 |
| `RA-7` | A revisão das fontes do Edital antes de abrir | por Edital | pendências da `074` ("os pontos da `070`") |
| `RA-8` | Limite por visitante que não dependa do cookie, e proteção contra uso automatizado | de software | pendências da `074`; a decisão sobre o teto de conversas por sessão da `074`; AS-16 |
| `RA-9` | Texto definitivo das falhas e da apresentação do painel | de software | pendências da `074`; DA-01 |
| `RA-10` | A correção do achado do documento ligado, que ainda leva à publicação de origem e não à versão vigente | de software | `071`, Fase C; `doc/achado-documento-ligado-nao-contem-a-versao-vigente.md` |
| `RA-11` | A emenda do canal da `070` pela T046 | de software | `071`, Fase C; DP-6 |
| `RA-12` | A retenção dos registros da página pública, separada da exclusão do piloto, pelo prazo do `RA-3` | de software | `071` (a exclusão está ancorada no relatório do piloto); `074` ("e a retenção"); AS-18 |

A lacuna B-1, a autenticação institucional da gestão, aparecia nas pendências da `074`. Ela não
entra na lista porque esta feature já exige a sessão institucional para todo ato (FR-7511), que a
`106` e a `107` entregaram.

**Para a entrega da abertura em produção**, registrado para que não se perca: os requisitos
institucionais e por Edital se registrariam com a referência do documento que os comprova; os de
software se cumpririam só pelo código, e não por registro; os por Edital se prenderiam à versão
vigente e venceriam numa Retificação; e a retirada de um requisito institucional fecharia os Editais
abertos. Nada disso é requisito desta entrega.

### O ambiente depois desta feature

| Variável ou recusa | Hoje | Depois |
|---|---|---|
| `ASSISTENTE_SERVICO`, `_ENDERECO`, `_MODELO`, `_TOKENIZER`, `_CREDENCIAL` | configuração do serviço | a mesma; é dela que se confere a **configuração completa** (FR-7501) |
| `_TEMPO_LIMITE_SEGUNDOS`, `_CONTEXTO_TOKENS`, `_SAIDA_MAXIMA_TOKENS`, `_TEMPERATURA`, `_TOP_P`, `_SEMENTE`, `_RACIOCINIO`, `_TOKENS_POR_MENSAGEM`, `_TOKENS_POR_CHAMADA`, `_TOLERANCIA_DE_TOKENS`, `_QUANTIZACAO`, `_OLLAMA_SEM_CORTE`, `_PROVEDOR`, `_ZDR` | parâmetros medidos por par serviço × modelo | sem mudança |
| `_TETO_SIMULTANEO`, `_TURNOS_POR_CONVERSA`, `_PERGUNTA_MAXIMA`, `_CONVERSAS_POR_SESSAO` | limites | sem mudança |
| `ASSISTENTE_PILOTO` | liga o piloto em qualquer ambiente | **atalho de demonstração local**, recusado em produção (FR-7506) |
| `ASSISTENTE_NA_PAGINA_DO_EDITAL` | demonstração local, recusada em produção | **sem mudança** (FR-7507) |
| Recusa: serviço diferente de `ollama` em produção | só com o piloto ligado | **sempre que houver serviço declarado** (FR-7505) |
| Recusa: tempo-limite acima de 110 s em produção | só com o piloto ligado | **sempre que houver serviço declarado** (FR-7505) |
| Recusa: `ASSISTENTE_NA_PAGINA_DO_EDITAL` em produção | existe | **continua** |
| Recusa: `ASSISTENTE_PILOTO` em produção | não existe | **nova** (FR-7506) |
| Abertura da página pública | só pela chave, fora de produção | fora de produção, também pela habilitação; em produção, **fechada pelo backend** (FR-7518, FR-7519) |

**Onde o código lê as chaves hoje**, conferido em `7d5c6ade`. São cinco pontos, e todos mudam para a
regra da FR-7515 ou da FR-7520:

- `interface/assistente.py`, `_edital_do_piloto`: a tela do piloto, e por ela o protótipo da Fase C
  (`interface/prototipo_do_assistente.py`);
- `interface/views.py`, `pode_conversar_com_o_assistente`: a entrada na página do Edital;
- `portal/assistente.py`, `_edital_com_pagina` e `painel`: as rotas e o fragmento da página pública;
- `duvidas/management/commands/avaliar_assistente.py`: passa a exigir a configuração completa
  (FR-7509).

### O que a `071` e a `074` deixam de valer

| Requisito ou decisão | O que dizia | O que passa a valer |
|---|---|---|
| A FR-1464 da `071` | o piloto desligado por padrão, **por chave de configuração** | desligado por padrão, e ligado **por ato** na administração institucional (FR-7514, FR-7515). Fora de produção, também pelo atalho de demonstração. A negativa continua a mesma |
| A FR-1462 da `071` | nenhuma rota pública, nem na implantação | fora de produção, a página pública do Edital habilitado oferece o painel (FR-7520). Em produção, continua valendo nesta entrega (FR-7519) |
| A FR-1503 da `071`, último item | produção recusa o serviço externo (aplicado só com o piloto ligado) | recusa sempre que houver serviço declarado (FR-7505) |
| A FR-1680 da `074` | a chave liga o painel | continua, como demonstração. Fora de produção, a habilitação por Edital também liga o painel |
| A FR-1684 da `074` | os requisitos da abertura são pendências da implantação, e não bloqueiam o desenvolvimento local | continuam sem bloquear os testes fora de produção. Em produção, a página pública fica fechada pelo backend até a entrega da abertura (FR-7518, FR-7533) |
| A FR-1683 da `074` | produção recusa a chave | **continua** |
| A `073`, premissa sobre ligar o piloto | "ligar o piloto em produção continua decisão do piloto da `071`" | é um ato na administração institucional. A seção do guia que diz "ligá-la é decisão do piloto" muda (FR-7536) |

**Continuam valendo, sem mudança:** a FR-1460, a FR-1461 (nenhuma tela mostra os registros), a
FR-1463 (sessões acompanhadas, Q-3), a FR-1499 a FR-1502 e a FR-1505 a FR-1510 da `071`. Também
continuam a FR-1681, a FR-1682 e a FR-1685 da `074`, e a regra de exclusão em 90 dias (FR-7534).

### Key Entities

- **Ato de habilitação do assistente**: o ato sobre uma frente, que é o piloto (um por implantação)
  ou a página pública de um Edital. Tem o sentido (habilitar ou desabilitar), o motivo, o autor (a
  pessoa institucional) e o instante. É append-only, e o estado vigente é o último ato.
- **Requisito da abertura em produção**: um dos doze da tabela. É documentação e texto da recusa, e
  não dado gravado nesta entrega.
- **Configuração completa**: não é entidade gravada. É a leitura, a cada requisição, das variáveis do
  ambiente (FR-7501).

Nenhuma entidade guarda valor do ambiente, conversa ou dado de candidato.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2450**: Em três ambientes (sem serviço, sem tokenizer e completo), a página diz corretamente se
  a configuração está completa e o que falta. Ela oferece habilitar em zero dos dois primeiros. O
  serviço recebe zero chamadas ao abrir a página, e a credencial plantada aparece zero vezes na
  página, no histórico e no log.
- **SC-2451**: Fora de produção e com as duas chaves de demonstração desligadas, o percurso inteiro
  passa num teste de navegador, com o serviço falso da suíte:
  1. o administrador habilita o piloto e o Edital A, com motivo;
  2. quem tem o papel conversa pela gestão;
  3. um visitante sem login conversa na página do A, e a página do B não traz o painel;
  4. o administrador desabilita;
  5. a pergunta seguinte, na gestão e na página do A, faz zero chamadas ao serviço.
- **SC-2452**: Todo ato tem autor, instante e motivo no registro e na trilha. Tentar alterar ou
  excluir um ato falha nas duas camadas: no gatilho e no privilégio.
- **SC-2453**: Com as configurações de produção:
  - o pedido de habilitação da página pública é recusado, nomeando os doze requisitos, e nada é
    gravado;
  - com uma habilitação no registro, a página não traz o painel, as rotas respondem 404, e o
    serviço recebe zero chamadas;
  - a inicialização é recusada, com a variável nomeada, para `ASSISTENTE_PILOTO` ligado, para
    serviço externo e para tempo-limite acima de 110 s com o piloto desligado.
- **SC-2454**: Toda pessoa sem `assistente:habilitar` no escopo institucional recebe recusa em todos
  os atos e leituras da feature. Isso vale para cada papel de unidade, inclusive o Gestor, o
  Participante do piloto e o Administrador de acessos da unidade, e para a sessão de demonstração.
- **SC-2455**: Os testes de exclusão dos registros do piloto da `071` e os testes da página pública da
  `074` passam sem mudança de comportamento.
- **SC-2456**: Depois de habilitar de novo, a primeira chamada de uma conversa interrompida por
  desabilitação leva zero trocas anteriores, conferido na contagem das mensagens da chamada.
- **SC-2457**: Na demonstração, num ambiente de testes com o serviço real configurado e sem chave de
  demonstração, o percurso do SC-2451 é feito pela interface e registrado com capturas: habilitar,
  conversar como visitante sem login e desabilitar.

---

## Proteção de dados (LGPD)

- **O que esta feature grava** são atos de pessoas institucionais: quem, quando e por quê. Ela não
  grava conversa nem dado de candidato.
- **As conversas da página pública fora de produção** seguem a `074`: são registradas sem
  identidade, com o mascaramento da `071`, e os testes usam perguntas sintéticas. Com o OpenRouter,
  a pergunta livre sai da máquina, como a `074` já diz.
- **Em produção, a página pública continua fechada** (FR-7519), e por isso nenhum texto livre de
  candidato real é gravado. A manifestação do encarregado (`RA-3`) e a retenção própria (`RA-12`)
  ficam como condições da abertura em produção.
- **A configuração é lida sem expor segredo** (FR-7500, SC-2450).

---

## Assumptions

- O papel Administrador institucional, a sessão institucional e a trilha por unidade existem na
  `main`, desde a `106`, a `107`, a `108` e a `110`. A administração institucional já tem a barra com
  Unidades e acessos, onde a página nova entra.
- Fora de produção, o Administrador institucional entra pelo provedor de homologação da `110`, com as
  configurações de desenvolvimento. É o ambiente de testes desta entrega.
- A página pública de um Edital é a da `074`: a seleção pública vigente no instante.
- A L4 e o Ollama do Cefor ainda não estão acessíveis (AS-07). Nos testes, o serviço é o OpenRouter,
  só fora de produção, com o limite de gasto da própria credencial.
- A spec irmã `169` aplica o mesmo princípio à verificação por vídeo. As duas não compartilham
  mecanismo.

---

## Out of Scope

- O cadastro, a retirada e o vencimento dos requisitos da abertura, e os requisitos de software
  (`RA-8` a `RA-12`). São da entrega da abertura em produção.
- Uma política de retenção de produção para as conversas de visitantes.
- Editar valores do ambiente pela interface, verificar a conexão pela interface ou guardar a
  credencial no banco.
- Habilitação por unidade, por Processo ou por perfil de usuário.
- Mudar as sessões acompanhadas do piloto (Q-3).
- Tela das conversas, exportação de registros ou mudança no relatório da avaliação.
- Juntar esta habilitação à da verificação por vídeo (`169`) num mecanismo comum.

---

## Dependências

| Spec | O que esta feature usa | Estado em 14/11/2026 |
|---|---|---|
| `071` | o piloto, a permissão `assistente:piloto`, a negativa, o registro das trocas e a exclusão | na `main` |
| `074` | o painel na página pública, a chave de demonstração e os limites | na `main` |
| `073` | os comandos que verificam a conexão, que a página não substitui | na `main` |
| `106`, `107` | o papel institucional, a sessão institucional, a suspensão e a revogação | na `main` |
| `108`, `110` | a trilha por unidade, a administração institucional, o provedor de homologação e o padrão dos atos com motivo | na `main` |

---

## Achados (registro, e não escopo)

- **Os ensaios do piloto não têm prazo de exclusão.** A exclusão está ancorada no relatório final, e
  o relatório não existe (AS-18). Esta spec não altera isso (`D-007`).
- **A DP-3 da `071` continua aberta.** É o `RA-1`.

---

## Decisões

### D-001 — A configuração no ambiente, a decisão na interface

**Decisão.** O ambiente guarda a configuração técnica, e um ato na administração institucional diz
se o assistente é oferecido. A configuração completa se confere pelas variáveis que já existem
(FR-7501), sem chave própria.

**Por quê.** Serviço, modelo, tokenizer e credencial dependem da máquina, e segredo não vai para o
banco. Usar ou não usar é decisão institucional, e precisa de autor e motivo. Uma terceira chave,
"o servidor pode oferecer", poderia divergir da configuração. Para desligar tudo pelo ambiente, basta
esvaziar o serviço.

**O custo.** Configuração completa não é serviço disponível. A página diz isso e manda verificar
pela `073` (FR-7502), em vez de chamar o modelo a cada abertura.

### D-002 — Os atalhos de demonstração continuam, e o percurso não depende deles

**Decisão.** `ASSISTENTE_PILOTO` passa a ser atalho de demonstração local, recusado em produção.
`ASSISTENTE_NA_PAGINA_DO_EDITAL` continua como está. Fora de produção, a habilitação registrada basta
(FR-7508).

**Por quê.** É a resposta à Q-4. Preserva as entradas do `.claude/launch.json` e o inventário visual,
que não têm sessão institucional, e repete o padrão do seletor de identidade.

### D-003 — O piloto por implantação, a página pública por Edital

**Decisão.** É a resposta à Q-1.

**Por quê.** Para o piloto, a escolha por unidade já existe na concessão do papel, e a GPU é uma só.
Para a página pública, a DA-10 da auditoria recomendou começar por um certame, e é o que permite
testar num Edital e não em outro.

### D-004 — O Administrador institucional, com permissão própria no papel que existe

**Decisão.** É a resposta à Q-2. A permissão `assistente:habilitar` é acrescentada ao papel, como
`unidade:administrar` na `110`, e a ampliação passa pela autorização expressa antes do deploy.

**Por quê.** Um papel novo pediria um mecanismo de designação novo, que a `110` já recusou.

### D-005 — Produção fecha a página pública, e a separação é do backend

**Decisão.** Fora de produção, os requisitos da abertura não são conferidos. Em produção, a
habilitação pública é recusada, e o painel não aparece nem com registro (FR-7518, FR-7519). A
distinção vem da configuração de produção que já existe, e não de variável nova.

**Por quê.** O usuário pediu testes sem os requisitos, e produção fechada enquanto eles estiverem
pendentes. Uma variável de ambiente que liberasse a abertura poderia ser ligada em produção por
engano. Conferir a cada requisição cobre o banco de testes levado para produção.

**O custo.** A abertura em produção exige uma entrega própria, que traga o cadastro dos requisitos e
os de software. A tabela dos doze fica pronta para ela.

### D-006 — Desabilitar no meio da conversa

**Decisão.** A decisão é conferida a cada requisição. A chamada já iniciada termina e é registrada.
Nenhuma pergunta nova chega ao modelo, e a habilitação seguinte começa conversa nova (FR-7523 a
FR-7526).

**Por quê.** Interromper uma chamada em curso não economiza a GPU, porque o serviço termina a
inferência de qualquer modo, e deixaria um registro sem resposta. Retomar o histórico depois de uma
desabilitação levaria ao modelo conversas feitas sob outra decisão.

**O custo.** A resposta da chamada em curso fica registrada e não é mostrada.

### D-007 — A regra de exclusão do piloto não muda

**Decisão.** O comando, o prazo de 90 dias e a âncora no relatório final continuam (FR-7534). As
conversas da página pública fora de produção seguem a `074` (FR-7535).

**Por quê.** A regra foi decidida pela DP-2 da `071`. Uma retenção de produção para texto livre de
candidatos é decisão do encarregado (`RA-3`), e é da entrega da abertura.

### D-008 — As sessões acompanhadas do piloto ficam

**Decisão.** É a resposta à Q-3. A habilitação pela interface não muda a FR-1463 da `071`.

**Por quê.** Os testes desta entrega não dependem de mudar essa regra, e mudá-la é decisão
institucional que o usuário reservou para depois.
