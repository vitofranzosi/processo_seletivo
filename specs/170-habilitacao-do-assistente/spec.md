# Feature Specification: A habilitação do assistente do Edital pela interface do sistema

**Feature Branch**: `claude/170-habilitacao-do-assistente-12c936`, sobre a `main` em `7d5c6ade`
(com a `166` mergeada)

**Created**: 2026-11-14

**Status**: Especificada em 14/11. Quatro perguntas ao usuário (Q-1 a Q-4) estão abertas, e a spec
adota a recomendação de cada uma até a resposta. Não foi planejada nem implementada.

**Input**: a decisão do usuário de 14/11/2026, ao discutir a verificação por vídeo da `166`: *"a
habilitação poderia ser via interface no sistema; o mesmo se aplica ao assistente de IA"*. Ele pediu
duas specs. A `169` é a do vídeo, e esta é a do assistente. As duas seguem o mesmo princípio: o
ambiente dá a **capacidade**, e a **decisão** institucional se registra na interface. Em 14/10, na
auditoria que gerou a `073`, o usuário já tinha recusado a conclusão "nenhuma interface" para as
configurações.

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
> a DA-10) se citam pelo nome que têm lá. Os requisitos da abertura ao público definidos aqui são
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
   institucional: custa GPU, expõe uma resposta não oficial a quem pergunta e grava texto livre. Hoje
   ela não tem autor, motivo nem data, e some quando alguém edita o arquivo. A `073` registrou isso
   ao dizer que "ligar o piloto em produção continua decisão do piloto da `071`", sem dizer onde
   essa decisão se registra.
2. **Os requisitos da abertura ao público estão espalhados.** Estão no portão da Fase C da `071`,
   nas pendências da `074`, na auditoria do assistente e na matriz de pendências de 15/10 (AS-15).
   Nenhum lugar diz quais já foram cumpridos.
3. **Não há como abrir um Edital e não outro.** A auditoria do assistente recomendou "chave global
   mais lista de Editais habilitados" (DA-10, opção b), para começar por um certame com equipe de
   plantão. A decisão nunca foi tomada (AS-17).

### O que esta feature faz

Ela separa duas coisas que a chave misturava:

- **A capacidade fica no ambiente.** O servidor *pode* oferecer o assistente quando tem o serviço de
  inferência, o modelo, o tokenizer, a credencial (se o serviço exigir) e o tempo-limite. Isso
  depende da máquina, e segredo nunca vai para o banco.
- **A decisão vai para a interface.** Habilitar, desabilitar e registrar os requisitos da abertura
  passam a ser atos na administração institucional que já existe, a mesma das Unidades (`110`). Cada
  ato tem motivo e trilha, e nada se exclui.

**A interface registra os requisitos, mas não os dispensa.** Para abrir o assistente ao público, os
requisitos que a `071` e a `074` deixaram para a implantação precisam estar registrados ou presentes
na versão do sistema. Faltando algum, a interface recusa e diz qual falta.

**Esta spec não abre o assistente ao público.** Parte dos requisitos depende de software que ainda
não existe, como o limite por visitante e o texto definitivo das falhas (`RA-8` a `RA-12`). Por
isso, em produção, a habilitação da página pública de qualquer Edital termina hoje numa recusa que
nomeia o que falta. É o resultado esperado. Quem abre é a spec da Fase C, quando entregar esses
requisitos.

### Duas frentes, que não se confundem

| | **Piloto da gestão** (`071`) | **Página pública** (`074`) |
|---|---|---|
| Quem conversa | quem tem o papel Participante do piloto e alcança o Edital na gestão | qualquer visitante da página pública da seleção |
| Hoje | `ASSISTENTE_PILOTO`, aceito em produção com o `ollama` | `ASSISTENTE_NA_PAGINA_DO_EDITAL`, recusado em produção |
| Alcance da habilitação (Q-1) | **uma por implantação** | **por Edital** |
| Requisitos da abertura (`RA-`) | não se aplicam | todos |
| Registro das conversas | `TrocaDoPiloto`, excluída 90 dias depois do relatório final | a mesma tabela hoje; a retenção própria é o `RA-12` |

### O que esta spec cobre, e o que fica fora

**Entra:**

- o que cada variável `ASSISTENTE_*` e cada recusa do `production.py` passam a ser (tabela em
  *O ambiente depois desta feature*);
- a leitura da capacidade na interface, sem valor secreto e sem chamar o serviço;
- a habilitação do piloto, uma por implantação;
- a lista fixa dos requisitos da abertura ao público, o registro e a retirada dos requisitos
  institucionais e dos requisitos de cada Edital, e a recusa nomeada;
- a habilitação da página pública por Edital, sempre condicionada aos requisitos;
- a regra de desabilitar com conversas em curso;
- o que a `071` e a `074` deixam de valer.

**Fica fora, de propósito:**

- **os requisitos de software da Fase C**: limite por visitante, proteção contra uso automatizado,
  textos definitivos, correção do documento ligado, emenda do canal da `070` e retenção dos registros
  públicos. Esta spec só os nomeia (`RA-8` a `RA-12`);
- **editar configuração pela interface**, ou guardar segredo no banco. É o que a `073` deixou fora, e
  continua fora;
- **testar a conexão ou fazer inferência a partir da página.** Esses testes ficam nos comandos da
  `073`, a pedido de quem opera (a decisão sobre os testes externos em dois níveis da `073`);
- **painel genérico de chaves**, catálogo de configurações e tela fora da administração institucional;
- **habilitação por unidade.** Para o piloto, quem participa já é decidido por unidade, ao conceder
  o papel (Q-1);
- **tela dos registros das conversas.** A FR-1461 da `071` continua valendo;
- **o SSO real do Ifes**, que segue como pendência da `106`.

---

## Clarifications

### Session 2026-11-14 (restrições do pedido)

- Não criar estruturas paralelas às que existem. Evitar overengineering. Toda abstração, papel,
  tabela ou mecanismo novo precisa resolver um problema concreto. É a regra que o usuário fixou na
  `110`.
- A decisão vai para o padrão do Administrador institucional que já existe, como a tela de Unidades
  da `110`: motivo, trilha, nada se exclui, e habilitar ou desabilitar é registro append-only.
- Negar por padrão: só o papel certo habilita, e o escopo é conferido.
- A regra de exclusão do piloto da `071` não muda sem registro (ver `D-009`).
- Governança e merge são do usuário. As perguntas abaixo têm recomendação, e a spec adota a
  recomendação até a resposta.

### Perguntas ao usuário

- **Q-1 — Qual é o alcance da habilitação?** As opções são uma por implantação, uma por unidade, uma
  por Edital, ou combinações. **Recomendação:** o piloto da gestão se habilita uma vez por
  implantação, e a página pública se habilita por Edital, desde que os requisitos institucionais
  estejam registrados. Para o piloto, a habilitação por unidade repetiria o que a concessão do papel
  já decide por unidade, porque o Administrador de acessos da unidade escolhe quem participa. E a
  GPU é uma só. Para a página pública, a habilitação por Edital é a opção (b) da DA-10 da auditoria.
  Ela permite começar por um certame com equipe de plantão, e dois requisitos só se cumprem Edital a
  Edital: a cláusula de exclusividade e a revisão das fontes. → *Adotada provisoriamente
  (`D-003`).*
- **Q-2 — Quem habilita e registra os requisitos?** As opções são o Administrador institucional ou,
  para cada Edital, o Gestor da unidade. **Recomendação:** o Administrador institucional, com uma
  permissão própria, `assistente:habilitar`, acrescentada ao papel que já existe, como a `110` fez com
  `unidade:administrar`. A decisão custa GPU de toda a instituição e expõe uma resposta não oficial.
  Os requisitos institucionais (LGPD, texto jurídico, relatório do piloto) não são da unidade. E dar
  a permissão ao Gestor ampliaria em silêncio um papel que muita gente tem. O que é da unidade, como
  a cláusula do Edital e a revisão das fontes, entra como referência ao documento dela, registrada
  pelo administrador. → *Adotada provisoriamente (`D-004`).*
- **Q-3 — Habilitado em produção, o piloto continua restrito às sessões acompanhadas?** A FR-1463 e
  a decisão sobre as sessões acompanhadas da `071` (DP-1) exigem sessões acompanhadas na máquina da
  equipe. O motivo escrito era que a gestão não autenticava em produção (B-1), e a `106` e a `107`
  resolveram isso. **Recomendação:** não. Habilitado em produção, o piloto atende quem tem o papel,
  sem acompanhamento. A orientação que a equipe dava no início de cada sessão passa a estar sempre
  na tela, e o papel continua concedido pessoa a pessoa, com trilha. → *Adotada provisoriamente
  (`D-010`).*
- **Q-4 — O que acontece com `ASSISTENTE_PILOTO`?** As opções são (a) virar chave de demonstração
  local, como a da `074`, recusada em produção, e (b) sair do código. **Recomendação:** (a). Ela
  preserva as entradas do `.claude/launch.json`, o inventário visual e o roteiro do quickstart da
  `071`, que ligam o piloto sem passar pela administração institucional. E repete um padrão que o
  projeto já tem, o do seletor de identidade e da chave da `074`. A opção (b) obrigaria todo ambiente
  de desenvolvimento a ter um registro de habilitação para abrir a tela do piloto. → *Adotada
  provisoriamente (`D-002`).*

---

## User Scenarios & Testing *(mandatory)*

**Ator principal:** o **Administrador institucional**, com sessão institucional e escopo ativo
institucional, que é o papel da `106`, renomeado na `110`. **Atores afetados:** quem participa do
piloto, quem visita a página pública da seleção e a equipe da unidade do Edital.

### User Story 1 — O administrador vê se o servidor pode oferecer o assistente (Priority: P1)

O Administrador institucional abre a página "Assistente do Edital" na administração institucional.
Ela diz, em palavras, se este servidor pode oferecer o assistente e, se não pode, o que falta. Nada
do que ela mostra é segredo, e abri-la não chama o serviço.

**Why this priority**: sem a capacidade, nenhuma habilitação faz sentido. É a fronteira entre o que
é da máquina e o que é da instituição.

**Independent Test**: num ambiente sem serviço declarado, num com serviço sem tokenizer e num
completo, abrir a página e comparar o que ela diz. Conferir que nenhum valor de credencial aparece e
que o serviço não recebeu chamada.

**Acceptance Scenarios**:

1. **Given** nenhum serviço declarado, **When** o administrador abre a página, **Then** ela diz que
   o servidor não pode oferecer o assistente, e não oferece habilitar nenhuma das frentes.
2. **Given** o serviço `ollama`, o endereço e o modelo declarados, mas sem o arquivo do tokenizer,
   **When** ele abre a página, **Then** ela diz "falta o tokenizer do modelo" e não oferece habilitar.
3. **Given** a capacidade completa e uma credencial presente, **When** ele abre a página, **Then**
   ela mostra o serviço, o modelo, o endereço e o tempo-limite, diz só "credencial: presente", e o
   serviço não recebe chamada.
4. **Given** uma pessoa com papel de unidade, ou com a sessão de demonstração, **When** ela pede o
   endereço da página, **Then** recebe a recusa, e nada é lido.

---

### User Story 2 — O administrador habilita e desabilita o piloto da gestão (Priority: P1)

A equipe vai começar a avaliação com o setor no Ollama. O administrador habilita o piloto e informa
o motivo. A partir da requisição seguinte, sem reinício, quem tem o papel Participante do piloto vê
o assistente na página dos Editais que alcança. Encerrada a avaliação, ele desabilita o piloto, e a
entrada desaparece.

**Why this priority**: é a frente que já roda em produção pela chave. Movê-la para a interface é o
centro do pedido.

**Independent Test**: com a capacidade completa, habilitar e conferir que a entrada aparece para quem
tem o papel e não para os outros. Desabilitar e conferir a negativa. Conferir os dois atos no
histórico e na trilha.

**Acceptance Scenarios**:

1. **Given** a capacidade completa e o piloto desabilitado, **When** o administrador confirma a
   habilitação com motivo, **Then** o ato é gravado com autor, instante e motivo, **and** quem tem o
   papel vê a entrada do assistente na página do Edital, na requisição seguinte.
2. **Given** o piloto habilitado, **When** uma pessoa sem o papel abre o endereço do assistente,
   **Then** recebe a mesma negativa de hoje (a FR-1460 da `071`).
3. **Given** o piloto habilitado, **When** o administrador o desabilita com motivo, **Then** a
   entrada some, **and** o endereço direto recebe a negativa, **and** nenhuma troca registrada é
   alterada.
4. **Given** a confirmação sem motivo, **When** ele confirma, **Then** a interface recusa, nada é
   gravado, e ele volta à mesma confirmação.
5. **Given** o piloto habilitado e a capacidade retirada do ambiente, **When** o administrador abre a
   página, **Then** ela diz "habilitado, mas sem capacidade: o assistente não atende", **and** quem
   tem o papel recebe a negativa.

---

### User Story 3 — O administrador registra os requisitos da abertura ao público (Priority: P2)

O encarregado de dados se manifestou sobre o texto livre de candidatos reais e fixou um prazo de
retenção. O administrador registra esse requisito com a referência do documento (número, data e
órgão) e o motivo. A página mostra a lista inteira dos requisitos da abertura. Cada um aparece como
registrado (por quem e quando), pendente ou dependente de versão do sistema.

**Why this priority**: junta num lugar só o portão que hoje está espalhado em quatro documentos, como
pediu a AS-15.

**Independent Test**: registrar um requisito institucional, conferir a referência e o autor na
lista, retirá-lo com motivo e conferir o histórico. Tentar registrar um requisito de versão por envio
montado à mão e conferir a recusa.

**Acceptance Scenarios**:

1. **Given** um requisito institucional pendente, **When** o administrador o registra com referência
   e motivo, **Then** a lista o mostra como registrado, com quem, quando e a referência.
2. **Given** um requisito de versão (`RA-8` a `RA-12`), **When** alguém tenta registrá-lo por envio
   montado à mão, **Then** recebe a recusa, e nada é gravado.
3. **Given** um requisito institucional registrado e dois Editais com a página pública habilitada,
   **When** o administrador o retira, **Then** a confirmação lista os dois Editais, **and** o ato
   retira o requisito e desabilita os dois, com o mesmo motivo, na mesma transação.

---

### User Story 4 — A página pública de um Edital só abre com todos os requisitos (Priority: P2)

O administrador escolhe um Edital publicado e pede a habilitação da página pública. A interface
confere a capacidade, os requisitos institucionais, os requisitos daquele Edital na versão vigente e
os requisitos de versão. Hoje a resposta é uma recusa que lista, pelo nome, cada requisito que falta.
Quando a Fase C entregar os requisitos de versão, o mesmo ato habilitará.

**Why this priority**: é o pedido do usuário, a habilitação pela interface, aplicada à frente que
mais expõe. Ela vem depois da US2 porque, hoje, termina em recusa.

**Independent Test**: no estado atual, pedir a habilitação de um Edital e conferir a recusa, que
nomeia os doze requisitos. Num caso de teste em que a versão declara os requisitos de versão
presentes e os demais estão registrados, habilitar e conferir que o painel aparece na página
pública. Publicar uma Retificação e conferir que o painel deixa de ser oferecido.

**Acceptance Scenarios**:

1. **Given** a versão atual do sistema, **When** o administrador pede a habilitação da página pública
   de qualquer Edital, **Then** recebe uma recusa que nomeia cada requisito que falta, separando os
   que ele pode registrar dos que dependem de versão, **and** nada é gravado.
2. **Given** todos os requisitos presentes e registrados para a versão vigente do Edital, **When** o
   administrador confirma a habilitação com motivo, **Then** a página pública da seleção oferece o
   painel da `074` na requisição seguinte, **and** outro Edital, não habilitado, não o oferece.
3. **Given** o Edital habilitado, **When** uma Retificação dele entra em vigor, **Then** os
   requisitos daquele Edital ficam vencidos, **and** o painel deixa de ser oferecido, **and** a
   página do administrador diz "vencido pela Retificação vigente desde <data>".
4. **Given** o Edital habilitado, **When** a equipe da unidade abre o Edital na gestão, **Then** vê
   que o assistente está aberto na página pública dele, desde quando e por qual ato.

---

### User Story 5 — Desabilitar com conversas em curso (Priority: P2)

Um visitante está conversando com o assistente na página de um Edital quando o administrador
desabilita a página. A pergunta que já estava com o serviço termina e é registrada. Na próxima
pergunta, o visitante vê que o assistente foi encerrado e é levado às informações oficiais. Se o
Edital for habilitado de novo, a conversa recomeça do zero.

**Why this priority**: o pedido exige uma regra explícita para esse caso, e sem ela a interface
abriria uma terceira forma de falha.

**Independent Test**: com uma conversa aberta, desabilitar, enviar outra pergunta e conferir o aviso.
Habilitar de novo, enviar e conferir que o histórico anterior não entrou no contexto.

**Acceptance Scenarios**:

1. **Given** uma pergunta com o serviço, **When** a desabilitação é confirmada, **Then** a pergunta
   termina, e a troca é registrada como hoje.
2. **Given** a desabilitação confirmada, **When** o visitante envia outra pergunta, **Then** recebe a
   página da seleção sem o painel, com o aviso de que o assistente desta seleção foi encerrado,
   **and** nada chega ao serviço.
3. **Given** o Edital desabilitado e depois habilitado de novo, **When** o mesmo visitante pergunta,
   **Then** a conversa é nova, e nenhuma troca anterior à desabilitação entra como histórico.
4. **Given** o piloto desabilitado no meio da conversa de um participante, **When** ele envia outra
   pergunta, **Then** recebe a negativa da FR-1464 da `071`.

---

### User Story 6 — A demonstração local continua sem passar pela administração (Priority: P3)

Na máquina de desenvolvimento, quem testa o piloto ou a página pública liga a chave de demonstração,
como hoje. Assim não precisa de sessão institucional nem de registro de habilitação. Em produção,
nenhuma das duas chaves sobe.

**Why this priority**: preserva o fluxo local que a `074` e a `071` construíram, sem criar um segundo
caminho de habilitação.

**Independent Test**: ligar cada chave nas configurações de desenvolvimento e conferir o piloto e o
painel. Ligar cada uma nas de produção e conferir a recusa de inicialização que nomeia a variável.

**Acceptance Scenarios**:

1. **Given** `ASSISTENTE_PILOTO=true` fora de produção e nenhum registro de habilitação, **When**
   quem tem o papel abre o assistente, **Then** ele atende, se houver capacidade.
2. **Given** `ASSISTENTE_PILOTO=true` em produção, **When** o processo inicia, **Then** a
   inicialização é recusada com uma mensagem que nomeia a variável e diz que a habilitação é um ato
   na administração institucional.
3. **Given** `ASSISTENTE_NA_PAGINA_DO_EDITAL=true` em produção, **When** o processo inicia, **Then**
   a recusa de hoje continua (a FR-1683 da `074`).

---

### Edge Cases

Cada caso aqui é requisito, e aponta o requisito que o governa.

- **Habilitação pedida sem capacidade** por envio montado à mão: o pedido é recusado, a recusa nomeia
  o que falta, e nada é gravado (FR-7501, FR-7512).
- **Capacidade retirada com o piloto habilitado**: o registro continua habilitado, nenhuma frente
  atende, e a página diz as duas coisas. Quando a capacidade volta, a frente volta a atender sem
  novo ato (FR-7504).
- **Capacidade incompleta**, com serviço sem tokenizer, sem modelo ou sem endereço: o sistema inicia
  normalmente, e o assistente não atende (FR-7503).
- **Serviço externo declarado em produção, com o piloto desabilitado**: hoje passa; depois desta
  feature, a inicialização é recusada (FR-7502).
- **Dois administradores confirmam atos contrários ao mesmo tempo**: um vale, e o outro recebe uma
  recusa que diz que o estado mudou (FR-7532).
- **Habilitar o que já está habilitado**, ou registrar de novo o requisito já registrado para a mesma
  versão: o pedido é recusado sem gravar (FR-7531).
- **Retificação em vigor depois do registro dos requisitos do Edital**: os requisitos vencem, e o
  painel deixa de ser oferecido sem novo ato (FR-7519).
- **Edital habilitado que perde a página pública**, por estar encerrado ou sem seleção pública: o
  painel não aparece, porque a página não existe. A habilitação continua no registro, e a página do
  administrador diz "sem página pública" (FR-7521).
- **Retirada de um requisito institucional com Editais abertos**: os Editais são desabilitados no
  mesmo ato (FR-7518).
- **Pergunta em curso no instante da desabilitação**: a pergunta termina e é registrada. A resposta
  não é mostrada depois, porque a próxima requisição já segue a decisão nova (FR-7525).
- **A demonstração ligada e um registro de habilitação ao mesmo tempo**, fora de produção: a
  demonstração dispensa o registro e não o altera. Com a chave desligada, vale o registro (FR-7505,
  FR-7506).
- **O relatório final do piloto registrado como requisito**: registrar não dispara a exclusão dos
  registros, que continua manual e com prazo próprio (FR-7534).
- **O papel do administrador revogado ou a pessoa suspensa** (`107`): os atos que ela praticou
  continuam valendo, e a pessoa não pratica outros (FR-7509).
- **Unidade do Edital desativada** (`110`): o Edital em curso continua, e a habilitação dele também.
  Nada muda por causa da unidade (FR-7520).

---

## Requirements *(mandatory)*

### Functional Requirements

#### A capacidade, no ambiente

- **FR-7500**: O serviço, o endereço, o modelo, o tokenizer, a credencial, o tempo-limite e os
  parâmetros e limites da inferência MUST continuar só no ambiente, nas variáveis `ASSISTENTE_*` que
  já existem (tabela em *O ambiente depois desta feature*). Nenhuma delas MUST ser gravada no banco
  nem editada pela interface. A credencial MUST NOT aparecer em página, histórico, trilha ou log.
- **FR-7501**: O servidor MUST ter a **capacidade** de oferecer o assistente quando todas estas
  condições valem:
  - o serviço declarado é um dos conhecidos;
  - o endereço e o modelo estão declarados;
  - o arquivo do tokenizer existe e pode ser lido;
  - a credencial está presente, se o serviço a exigir.

  A capacidade MUST ser conferida no servidor a cada requisição que a usa. Conferi-la MUST NOT
  contatar o serviço.
- **FR-7502**: Em produção, as recusas de serviço externo e de tempo-limite acima de 110 s MUST valer
  sempre que houver serviço declarado, independentemente de qualquer chave. Hoje elas só valem com
  `ASSISTENTE_PILOTO` ligado. A mensagem de cada uma MUST continuar nomeando a variável.
- **FR-7503**: Capacidade ausente ou incompleta MUST NOT impedir a inicialização. Um servidor sem
  assistente é legítimo, e um assistente mal configurado não pode derrubar as inscrições.
- **FR-7504**: Sem capacidade, nenhuma frente MUST atender, qualquer que seja o registro de
  habilitação. O registro MUST NOT ser alterado pela falta de capacidade. Quando a capacidade
  voltar, a frente habilitada MUST voltar a atender sem novo ato.

#### As chaves de demonstração local

- **FR-7505**: `ASSISTENTE_PILOTO` MUST passar a ser uma chave de demonstração local. Ligada fora de
  produção, ela dispensa o registro de habilitação do piloto, e só isso: o papel, o alcance do
  Edital e a capacidade continuam exigidos. Produção MUST recusar subir com ela ligada, com uma
  mensagem que diz que a habilitação é um ato na administração institucional (Q-4).
- **FR-7506**: `ASSISTENTE_NA_PAGINA_DO_EDITAL` MUST continuar a chave de demonstração da `074`, sem
  mudança, e produção MUST continuar recusando-a (a FR-1683 da `074`). Ligada fora de produção, ela
  dispensa a habilitação por Edital e os requisitos da abertura, mas não a capacidade.
- **FR-7507**: O comando de avaliação do piloto MUST exigir a capacidade, e não a habilitação nem a
  chave. A avaliação é operação da equipe, e não uso por pessoas.

#### Quem habilita

- **FR-7508**: A permissão `assistente:habilitar` MUST pertencer ao papel Administrador institucional,
  e só a ele. MUST NOT pertencer a papel de unidade nem a papel do seletor de demonstração. Nenhum
  papel, tela de designação ou mecanismo de concessão novo MUST ser criado. Antes do deploy, todo
  vínculo vigente desse papel MUST ser identificado, e a ampliação MUST NOT chegar a quem o tem sem a
  autorização expressa do usuário, como na `110` (Q-2).
- **FR-7509**: Todo ato e toda leitura desta feature MUST exigir `assistente:habilitar` com o escopo
  ativo institucional, conferidos na camada de aplicação, e a tela é só a segunda barreira. A sessão
  de demonstração MUST receber a recusa antes de qualquer leitura, como na FR-3312 da `110`. Os atos
  já praticados por quem perdeu o papel ou foi suspenso MUST continuar valendo.
- **FR-7510**: `assistente:habilitar` MUST NOT conferir nenhuma outra capacidade. Ela não dá o uso do
  piloto (`assistente:piloto`), nem ato sobre Processo, Edital ou Publicação. Para escolher o Edital,
  ela permite ler só a identificação pública dos Editais que têm página pública: número, ano,
  unidade e título.

#### O lugar na interface

- **FR-7511**: A feature MUST ter uma página só, "Assistente do Edital", na administração
  institucional, ao lado de Unidades e da administração de acessos. A barra MUST oferecê-la só a quem
  tem a permissão. A página MUST mostrar a capacidade, o estado do piloto, os requisitos da abertura,
  os Editais com a página pública habilitada e o histórico. MUST NOT existir painel genérico de
  chaves, nem edição de valores do ambiente.

#### O piloto da gestão

- **FR-7512**: O piloto MUST ter uma habilitação por implantação (Q-1). Habilitar e desabilitar MUST
  passar por uma confirmação com motivo. Sem capacidade, a habilitação MUST NOT ser oferecida, e um
  pedido montado à mão MUST ser recusado com o que falta.
- **FR-7513**: O piloto MUST atender quando valem todas estas condições:
  - há habilitação vigente, ou a chave de demonstração está ligada fora de produção;
  - há capacidade;
  - valem as duas condições da FR-1460 da `071`: o alcance do Edital e a permissão do piloto.

  A tela, a entrada na página do Edital e o protótipo da Fase C MUST aplicar a mesma regra, e a
  entrada só aparece onde a tela atenderia. A negativa da FR-1460 e da FR-1464 da `071` MUST
  continuar a mesma.
- **FR-7514**: A habilitação do piloto MUST NOT exigir os requisitos da abertura ao público. Com o
  piloto habilitado, a tela MUST mostrar sempre a orientação de perguntar só sobre Editais públicos e
  sem dado de pessoa, que até aqui era dada oralmente nas sessões acompanhadas (Q-3).

#### Os requisitos da abertura ao público

- **FR-7515**: Os requisitos da abertura ao público MUST ser os doze da tabela em *Os requisitos da
  abertura*, com a espécie de cada um: institucional, por Edital ou de versão. A lista MUST ser fixa
  no sistema. A interface MUST NOT acrescentar, editar ou dispensar requisito; isso só acontece por
  spec.
- **FR-7516**: Registrar um requisito institucional ou por Edital MUST ser um ato com estes dados: a
  referência do documento que o comprova (número, data e órgão, em texto), o motivo, o autor e o
  instante. O sistema MUST NOT avaliar o documento: o registro diz quem atestou, e com base em quê.
- **FR-7517**: Os requisitos de versão MUST NOT ser registráveis pela interface. Cada um só se
  cumpre quando a versão do sistema o implementa, e quem declara isso é a spec que o implementa. Esta
  spec MUST NOT declarar nenhum deles cumprido.
- **FR-7518**: Um requisito registrado MUST poder ser retirado por um ato com motivo. A retirada de um
  requisito institucional MUST desabilitar, no mesmo ato e com o mesmo motivo, todo Edital com a
  página pública habilitada, e a confirmação MUST listá-los antes. A retirada de um requisito por
  Edital MUST desabilitar a página daquele Edital.
- **FR-7519**: Um requisito por Edital MUST ser registrado contra a versão vigente do Edital no
  instante do ato. Quando outra versão entrar em vigor, ele MUST vencer sem ato: o painel deixa de ser
  oferecido, e a página do administrador diz por quê. Registrá-lo de novo, contra a versão vigente,
  MUST restabelecer o painel sem nova habilitação.

#### A página pública, por Edital

- **FR-7520**: A habilitação da página pública MUST ser por Edital (Q-1), e só para Edital com
  página pública. O ato MUST exigir:
  - a capacidade;
  - os requisitos institucionais registrados;
  - os requisitos daquele Edital registrados para a versão vigente;
  - os requisitos de versão cumpridos.

  Faltando qualquer um, o ato MUST ser recusado, a recusa MUST nomear cada requisito que falta, e
  nada é gravado. A situação da unidade do Edital MUST NOT entrar na conferência.
- **FR-7521**: A página pública de um Edital MUST oferecer o painel só quando há habilitação vigente,
  os requisitos continuam cumpridos e há capacidade, tudo conferido a cada requisição. Fora disso, a
  página e as rotas MUST se comportar como na `074` com a chave desligada, salvo o aviso da FR-7525.
  Um Edital habilitado sem página pública MUST aparecer assim na página do administrador.
- **FR-7522**: O painel e os envios MUST continuar os da `074` (a FR-1681 da `074`), com os limites
  da FR-1685 da `074`. Nenhuma arquitetura de conversa nova.
- **FR-7523**: A página do Edital na gestão MUST dizer, a quem a alcança, se o assistente está aberto
  na página pública daquele Edital, desde quando, ou por que não está.

#### Desabilitar com conversas em curso

- **FR-7524**: A habilitação e os requisitos MUST ser conferidos no servidor a cada requisição: ao
  mostrar a página, a cada pergunta, a cada sugestão e a cada nova conversa. A decisão MUST NOT ser
  guardada de uma requisição para outra.
- **FR-7525**: Uma chamada ao serviço já iniciada MUST terminar e ser registrada como hoje. A
  requisição seguinte MUST seguir a decisão nova:
  - o visitante da página pública recebe a página sem o painel, com o aviso de que o assistente desta
    seleção foi encerrado;
  - o participante do piloto recebe a negativa da FR-1464 da `071`.
- **FR-7526**: Depois de uma desabilitação, a habilitação seguinte MUST começar conversa nova: as
  trocas anteriores à desabilitação MUST NOT entrar como histórico.
- **FR-7527**: Desabilitar MUST NOT alterar nem excluir troca registrada.

#### O registro

- **FR-7528**: Cada ato (habilitar, desabilitar, registrar requisito e retirar requisito) MUST ser
  gravado num registro append-only, com as duas camadas independentes do projeto: o gatilho e a
  ausência de privilégio. As tabelas novas MUST entrar na contagem `N de M` do provisionamento.
- **FR-7529**: Todo ato MUST exigir motivo preenchido depois de aparados os espaços. Sem motivo, a
  interface MUST recusar sem gravar.
- **FR-7530**: Todo ato MUST gerar um evento na trilha, na mesma transação. O ato sobre um Edital MUST
  ser legível na trilha da unidade do Edital.
- **FR-7531**: Um ato que não muda nada MUST ser recusado sem gravar: habilitar o que está
  habilitado, desabilitar o que está desabilitado, ou registrar um requisito já registrado para a
  mesma versão.
- **FR-7532**: A confirmação MUST reconferir no servidor tudo o que a primeira etapa conferiu. Dois
  atos simultâneos sobre a mesma frente ou o mesmo Edital MUST ser serializados. O segundo MUST
  receber uma recusa que diz que o estado mudou.
- **FR-7533**: O estado de cada frente, de cada Edital e de cada requisito MUST ser o do último ato
  que o afeta. O histórico MUST mostrar todos os atos, do mais recente para o mais antigo, com autor
  pelo nome, instante, motivo e referência.

#### Os registros do piloto

- **FR-7534**: A exclusão dos registros do piloto 90 dias depois do relatório final (a FR-1509 da
  `071`) MUST continuar a mesma: o mesmo comando, o mesmo prazo e a mesma âncora. Desabilitar o
  piloto MUST NOT valer como relatório final. Registrar o `RA-1` MUST NOT disparar a exclusão.
- **FR-7535**: Nenhuma conversa de visitante MUST ser gravada em produção antes de existir a retenção
  própria dos registros da página pública (`RA-12`). A regra de 90 dias do piloto MUST NOT ser
  estendida a dado de candidato real.

#### Documentação

- **FR-7536**: O guia de implantação, o `CLAUDE.md`/`AGENTS.md` (as seções da `071` e da `074`), o
  `.env.example` e o roteiro do quickstart da `071` MUST dizer o que mudou: a capacidade fica no
  ambiente, a decisão é um ato na administração institucional, as chaves passam a ser de demonstração
  e são recusadas em produção, e a autorização da ampliação do papel é pedida antes do deploy.
- **FR-7537**: A implementação MUST acrescentar à `071` e à `074` uma nota em cada requisito revisto,
  apontando para esta spec, como a `074` fez na FR-1462 da `071`.

### Requisitos de experiência

- **UX-810**: A capacidade MUST ser dita em palavras de quem decide. Por exemplo: "este servidor não
  pode oferecer o assistente: falta o tokenizer do modelo". Ela MUST NOT ser dita por nome de
  variável. O nome da variável aparece só como detalhe, para quem opera.
- **UX-811**: A recusa da habilitação da página pública MUST listar cada requisito que falta, pelo
  nome, agrupado pelo que a pessoa pode fazer. Os institucionais e os do Edital aparecem como
  "registre aqui". Os de versão aparecem como "depende de uma versão do sistema que ainda não
  existe".
- **UX-812**: Toda confirmação MUST dizer a consequência antes do motivo. Para habilitar o piloto:
  "quem tem o papel Participante do piloto passa a ver o assistente na página dos Editais que
  alcança". Para desabilitar: "as conversas em curso não continuam; os registros não são apagados".
- **UX-813**: O aviso ao visitante cuja conversa foi encerrada MUST dizer que o assistente desta
  seleção foi encerrado, e levar às informações oficiais da página. MUST NOT sugerir erro do
  visitante nem pedir que ele tente de novo.
- **UX-814**: A linha da página do Edital na gestão MUST usar a mesma linguagem da página do
  administrador, para que a equipe da unidade e o administrador falem do mesmo estado.

### Os requisitos da abertura

A lista vem da `071` (o portão da Fase C e os critérios de conclusão), da `074` (as pendências para a
implantação), da auditoria do assistente de 12/10 e da matriz de pendências de 15/10. Nenhum
requisito foi acrescentado além dessas fontes. O `RA-12` explicita uma consequência delas, como diz a
coluna da origem.

| ID | Requisito | Espécie | Origem |
|---|---|---|---|
| `RA-1` | Relatório final do piloto, com os critérios da DP-3 aprovados e cumpridos | institucional | `071`, critérios de conclusão e "concluído não é aprovado para a Fase C"; AS-08 |
| `RA-2` | Revisão institucional da Fase A com o setor de seleção (a T046 da `070`) | institucional | `071`, Fase C; AS-01 |
| `RA-3` | Manifestação do encarregado de dados sobre o texto livre de candidatos reais e o prazo de retenção dos registros da página pública | institucional | `071`, LGPD; pendências da `074`; DA-09; AS-18 |
| `RA-4` | Texto aprovado que declara a natureza não oficial das respostas | institucional | `071`, Fase C; DA-01; DEP-08 da auditoria; AS-04 |
| `RA-5` | Medição da carga pública no serviço local, com a decisão sobre isolar a inferência | institucional | a decisão sobre o isolamento dos workers da `071`; DEP-06 da auditoria; AS-16 |
| `RA-6` | A cláusula "esclarecimentos exclusivamente por e-mail" resolvida neste Edital | por Edital | `071`, Fase C; DA-02; AS-03 |
| `RA-7` | A revisão das fontes deste Edital antes de abrir | por Edital | pendências da `074` ("os pontos da `070`") |
| `RA-8` | Limite por visitante que não dependa do cookie, e proteção contra uso automatizado | de versão | pendências da `074`; a decisão sobre o teto de conversas por sessão da `074`; AS-16 |
| `RA-9` | Texto definitivo das falhas e da apresentação do painel | de versão | pendências da `074`; DA-01 |
| `RA-10` | A correção do achado do documento ligado, que ainda leva à publicação de origem e não à versão vigente | de versão | `071`, Fase C; `doc/achado-documento-ligado-nao-contem-a-versao-vigente.md` |
| `RA-11` | A emenda do canal da `070` pela T046 | de versão | `071`, Fase C; DP-6 |
| `RA-12` | A retenção dos registros da página pública, separada da exclusão do piloto, pelo prazo do `RA-3` | de versão | `071` (a exclusão está ancorada no relatório do piloto); `074` ("e a retenção"); AS-18 |

A lacuna B-1, a autenticação institucional da gestão, aparecia nas pendências da `074`. Ela não
entra na lista porque esta feature já exige a sessão institucional para todo ato (FR-7509). Ela
depende da `106` e da `107`, que estão na `main`.

### O ambiente depois desta feature

| Variável ou recusa | Hoje | Depois |
|---|---|---|
| `ASSISTENTE_SERVICO`, `_ENDERECO`, `_MODELO`, `_TOKENIZER`, `_CREDENCIAL` | configuração do serviço | **capacidade** (FR-7501), sem mudança de nome nem de valor |
| `_TEMPO_LIMITE_SEGUNDOS`, `_CONTEXTO_TOKENS`, `_SAIDA_MAXIMA_TOKENS`, `_TEMPERATURA`, `_TOP_P`, `_SEMENTE`, `_RACIOCINIO`, `_TOKENS_POR_MENSAGEM`, `_TOKENS_POR_CHAMADA`, `_TOLERANCIA_DE_TOKENS`, `_QUANTIZACAO`, `_OLLAMA_SEM_CORTE`, `_PROVEDOR`, `_ZDR` | parâmetros medidos por par serviço × modelo | sem mudança: são da máquina e do modelo |
| `_TETO_SIMULTANEO`, `_TURNOS_POR_CONVERSA`, `_PERGUNTA_MAXIMA`, `_CONVERSAS_POR_SESSAO` | limites | sem mudança: dependem dos processos e da GPU (a decisão sobre o isolamento dos workers da `071`) |
| `ASSISTENTE_PILOTO` | liga o piloto em qualquer ambiente | **chave de demonstração local**, recusada em produção (FR-7505, Q-4) |
| `ASSISTENTE_NA_PAGINA_DO_EDITAL` | demonstração local, recusada em produção | **sem mudança** (FR-7506) |
| Recusa: serviço diferente de `ollama` em produção | só com o piloto ligado | **sempre que houver serviço declarado** (FR-7502) |
| Recusa: tempo-limite acima de 110 s em produção | só com o piloto ligado | **sempre que houver serviço declarado** (FR-7502) |
| Recusa: `ASSISTENTE_NA_PAGINA_DO_EDITAL` em produção | existe | **continua** |
| Recusa: `ASSISTENTE_PILOTO` em produção | não existe | **nova** (FR-7505) |

**Onde o código lê as chaves hoje**, conferido em `7d5c6ade`. São cinco pontos, e todos mudam para a
regra da FR-7513 ou da FR-7521:

- `interface/assistente.py`, `_edital_do_piloto`: a tela do piloto, e por ela o protótipo da Fase C
  (`interface/prototipo_do_assistente.py`);
- `interface/views.py`, `pode_conversar_com_o_assistente`: a entrada na página do Edital;
- `portal/assistente.py`, `_edital_com_pagina` e `painel`: as rotas e o fragmento da página pública;
- `duvidas/management/commands/avaliar_assistente.py`: passa a exigir a capacidade (FR-7507).

O `config/settings/test.py` liga o piloto e fixa o painel desligado. A suíte passa a criar o registro
de habilitação onde precisa dele, e a chave de demonstração deixa de estar ligada por padrão nos
testes. Isso é decisão do plano.

### O que a `071` e a `074` deixam de valer

| Requisito ou decisão | O que dizia | O que passa a valer |
|---|---|---|
| A FR-1464 da `071` | o piloto desligado por padrão, **por chave de configuração** | desligado por padrão, e ligado **por ato** na administração institucional (FR-7512, FR-7513). Fora de produção, também pela chave de demonstração. A negativa continua a mesma |
| A FR-1462 da `071` | nenhuma rota pública, nem na implantação | a página pública oferece o painel no Edital habilitado, com os requisitos cumpridos (FR-7520, FR-7521). Continua sem API pública e sem entrada no portal do candidato |
| A FR-1463 da `071` e a decisão das sessões acompanhadas (DP-1) | o piloto com o setor só em sessões acompanhadas, na máquina da equipe | habilitado em produção, o piloto atende quem tem o papel, com a orientação na tela (FR-7514, **Q-3**). As sessões acompanhadas continuam possíveis, mas deixam de ser obrigatórias |
| A FR-1503 da `071`, último item | produção recusa o serviço externo (aplicado só com o piloto ligado) | recusa sempre que houver serviço declarado (FR-7502) |
| A FR-1684 da `074` | os requisitos da abertura são pendências da implantação, e não bloqueiam o desenvolvimento local | passam a ser condições conferidas pela interface (FR-7515 a FR-7520). Continuam sem bloquear a demonstração local (FR-7506) |
| A FR-1680 da `074` | a chave liga o painel | continua, só como demonstração. O caminho de produção é a habilitação por Edital |
| A FR-1683 da `074` | produção recusa a chave | **continua** |
| A `073`, premissa sobre ligar o piloto | "ligar o piloto em produção continua decisão do piloto da `071`" | é um ato na administração institucional. A seção do guia que diz "ligá-la é decisão do piloto" muda (FR-7536) |

**Continuam valendo, sem mudança:** a FR-1460, a FR-1461 (nenhuma tela mostra os registros), a
FR-1499 a FR-1502 e a FR-1505 a FR-1510 da `071`. Também continuam a FR-1681, a FR-1682 e a FR-1685
da `074`, e a regra de exclusão em 90 dias (FR-7534).

### Key Entities

- **Ato de habilitação do assistente**: o ato sobre uma frente, que é o piloto (um por implantação)
  ou a página pública de um Edital. Tem o sentido (habilitar ou desabilitar), o motivo, o autor (a
  pessoa institucional), o instante e, quando houve, o ato de retirada de requisito que o provocou.
  É append-only, e o estado vigente é o último ato.
- **Ato sobre requisito da abertura**: registra ou retira um requisito institucional ou por Edital.
  Tem o requisito, o Edital e a versão vigente quando o requisito é por Edital, a referência do
  documento, o motivo, o autor e o instante. É append-only.
- **Requisito da abertura**: um dos doze da tabela, com a espécie. A lista é fixa no sistema, não é
  dado de tela e não é editável.
- **Capacidade**: não é entidade gravada. É a leitura, a cada requisição, das variáveis do ambiente
  (FR-7501).

Nenhuma das entidades guarda valor do ambiente, nem conversa, nem dado de candidato.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2450**: Em três ambientes (sem serviço, sem tokenizer e completo), a página diz corretamente
  se há capacidade e o que falta. Ela oferece habilitar em zero dos dois primeiros. O serviço recebe
  zero chamadas, e a credencial plantada aparece zero vezes na página, no histórico e no log.
- **SC-2451**: O piloto habilitado atende quem tem o papel na primeira requisição depois do ato, sem
  reinício. Depois de desabilitado, a primeira requisição recebe a negativa. As duas coisas são
  provadas em teste e no navegador.
- **SC-2452**: Todo ato da feature tem autor, instante e motivo no registro e na trilha. A aplicação
  falha nas tentativas de alterar ou excluir um ato, nas duas camadas: no gatilho e no privilégio.
- **SC-2453**: Na versão desta feature, o pedido de habilitação da página pública de qualquer Edital
  é recusado. A recusa nomeia os doze requisitos, ou os que faltarem, se alguns estiverem
  registrados, e nada é gravado.
- **SC-2454**: Num caso com todos os requisitos cumpridos, o painel aparece na página do Edital
  habilitado e não aparece em outro. Depois de uma Retificação entrar em vigor, ele deixa de aparecer
  na primeira requisição.
- **SC-2455**: Produção recusa subir em cada um destes casos, com a variável nomeada:
  `ASSISTENTE_PILOTO` ligado, serviço externo declarado, e tempo-limite acima de 110 s com o piloto
  desligado.
- **SC-2456**: Toda pessoa sem `assistente:habilitar` no escopo institucional recebe recusa em todos
  os atos e leituras da feature. Isso vale para cada papel de unidade, inclusive o Gestor, o
  Participante do piloto e o Administrador de acessos da unidade, e para a sessão de demonstração.
- **SC-2457**: Os testes de exclusão dos registros do piloto da `071` passam sem mudança. Uma
  desabilitação seguida do registro do `RA-1` não exclui nenhuma troca.
- **SC-2458**: Uma conversa interrompida por desabilitação não envia, depois de habilitar de novo,
  nenhuma troca anterior ao serviço, conferido na contagem das mensagens da chamada.

---

## Proteção de dados (LGPD)

- **O que esta feature grava** são atos de pessoas institucionais: quem, quando, por quê e com base em
  qual documento. Não grava conversa nem dado de candidato.
- **A referência do documento** é texto livre, e a tela pede só número, data e órgão. Ela não pede o
  conteúdo do documento nem nome de candidato.
- **A abertura ao público é o momento em que o texto livre de candidatos reais passa a ser gravado.**
  Por isso a manifestação do encarregado (`RA-3`) e a retenção própria (`RA-12`) são condições, e
  não sugestões. A FR-7535 impede que a regra do piloto seja aplicada a esses dados.
- **A capacidade é lida sem expor segredo** (FR-7500, SC-2450).

---

## Assumptions

- O papel Administrador institucional, a sessão institucional e a trilha por unidade existem na
  `main`, desde a `106`, a `107`, a `108` e a `110`. A administração institucional já tem a barra com
  Unidades e acessos, onde a página nova entra.
- A página pública de um Edital é a da `074`: a seleção pública vigente no instante.
- A L4 e o Ollama do Cefor ainda não estão acessíveis (AS-07). A habilitação do piloto em produção só
  tem efeito quando estiverem. Até lá, a página diz que não há capacidade.
- Os requisitos institucionais se comprovam por documentos de fora do sistema, como o relatório, o
  parecer do encarregado e o texto aprovado pela área jurídica. O sistema guarda a referência, e não
  o arquivo.
- A spec irmã `169` aplica o mesmo princípio à verificação por vídeo. Nenhum requisito aqui depende
  dela, e as duas não compartilham registro: cada capacidade tem os seus requisitos.

---

## Out of Scope

- Implementar qualquer requisito de versão (`RA-8` a `RA-12`). Isso é a spec da Fase C (AS-15).
- Editar valores do ambiente pela interface, testar a conexão pela interface ou guardar a credencial
  no banco.
- Habilitação por unidade, por Processo ou por perfil de usuário.
- Tela das conversas, exportação de registros ou mudança no relatório da avaliação.
- O prazo dos registros dos ensaios locais, que não têm relatório final (achado da AS-18).
- Juntar esta habilitação à da verificação por vídeo (`169`) num mecanismo comum.

---

## Dependências

| Spec | O que esta feature usa | Estado em 14/11/2026 |
|---|---|---|
| `071` | o piloto, a permissão `assistente:piloto`, a negativa, o registro das trocas e a exclusão | na `main` |
| `074` | o painel na página pública, a chave de demonstração e os limites | na `main` |
| `073` | os comandos que testam a conexão, que a página não substitui | na `main` |
| `106`, `107` | o papel institucional, a sessão institucional, a suspensão e a revogação | na `main` |
| `108`, `110` | a trilha por unidade, a administração institucional e o padrão dos atos com motivo | na `main` |

---

## Achados (registro, e não escopo)

- **Os ensaios do piloto não têm prazo de exclusão.** A exclusão está ancorada no relatório final, e
  o relatório não existe (AS-18). Esta spec não altera isso (`D-009`).
- **A DP-3 da `071` continua aberta.** Sem ela, o `RA-1` não pode ser registrado com verdade, e a
  interface não tem como conferir isso: o registro diz quem atestou.

---

## Decisões

### D-001 — Capacidade no ambiente, decisão na interface

**Decisão.** O ambiente diz se o servidor *pode* oferecer o assistente. Um ato na administração
institucional diz se ele *é* oferecido. A capacidade se deriva das variáveis que já existem
(FR-7501), sem chave própria.

**Por quê.** O serviço, o modelo, o tokenizer e a credencial dependem da máquina, e segredo não vai
para o banco. Usar ou não usar é decisão institucional, e precisa de autor e motivo. Derivar a
capacidade da configuração do serviço evita uma terceira chave que poderia divergir dela. Para
desligar tudo pelo ambiente, basta esvaziar o serviço.

**O custo.** Uma capacidade incompleta não derruba a inicialização (FR-7503), e só a página e os
comandos da `073` a revelam. A alternativa, recusar subir, deixaria o portal de inscrições sem
servir por causa de um assistente mal configurado.

### D-002 — As duas chaves passam a ser de demonstração local

**Decisão.** `ASSISTENTE_PILOTO` passa a ser uma chave de demonstração local, recusada em produção.
`ASSISTENTE_NA_PAGINA_DO_EDITAL` continua como está (Q-4).

**Por quê.** É o padrão do seletor de identidade e da `074`: o atalho de desenvolvimento existe e
produção o recusa. Assim o caminho de produção é um só, a habilitação, e as entradas do
`.claude/launch.json` e o inventário visual continuam funcionando.

**O custo.** A chave mantém um nome que sugere "ligar o piloto". A mensagem de recusa e o guia dizem
o que ela passou a ser.

### D-003 — O piloto se habilita por implantação, e a página pública por Edital

**Decisão.** Ver Q-1.

**Por quê.** Para o piloto, a escolha por unidade já existe na concessão do papel. Para a página
pública, dois requisitos só se cumprem Edital a Edital, e a DA-10 da auditoria recomendou começar por
um certame.

### D-004 — O Administrador institucional, com permissão própria no papel que existe

**Decisão.** Ver Q-2. A permissão `assistente:habilitar` é acrescentada ao papel, como
`unidade:administrar` na `110`, e a ampliação passa pela autorização expressa antes do deploy.

**Por quê.** Um papel novo pediria um mecanismo de designação novo, que a `110` já recusou.
Acrescentar a permissão ao Gestor ampliaria em silêncio um papel de unidade com muitos titulares. E
nenhuma das duas frentes é decisão de uma unidade só.

### D-005 — Três espécies de requisito, e a de versão não se registra

**Decisão.** Há três espécies: os requisitos institucionais e os por Edital se registram com a
referência do documento; os de versão só se cumprem pelo código.

**Por quê.** "A interface registra os requisitos, não os dispensa." Um limite por visitante que não
existe não passa a existir porque alguém o declarou numa tela. Deixá-lo registrável seria a dispensa
disfarçada que o pedido proíbe.

**O custo.** A habilitação da página pública não completa em produção até a Fase C (SC-2453).

### D-006 — O requisito por Edital vence com a Retificação

**Decisão.** O `RA-6` e o `RA-7` se registram contra a versão vigente e vencem quando outra entra em
vigor (FR-7519).

**Por quê.** A revisão das fontes e a cláusula de exclusividade são sobre um texto. Uma Retificação
muda o texto que o assistente lê (as fontes vigentes no instante da `070`), e pode reintroduzir a
cláusula.

**O custo.** O painel some sem ato, numa Retificação. A página do administrador e a do Edital dizem
por quê (FR-7523), e registrar de novo restabelece o painel sem nova habilitação.

### D-007 — Retirar um requisito institucional fecha os Editais no mesmo ato

**Decisão.** A retirada lista os Editais abertos e os desabilita na mesma transação (FR-7518).

**Por quê.** A alternativa seria recusar a retirada até alguém desabilitar cada Edital. Com ela, um
parecer de LGPD revogado poderia continuar valendo enquanto os Editais eram fechados um a um.

### D-008 — Desabilitar no meio da conversa

**Decisão.** A decisão é conferida a cada requisição. A chamada já iniciada termina e é registrada.
A requisição seguinte segue a decisão nova, e a habilitação seguinte começa conversa nova
(FR-7524 a FR-7527).

**Por quê.** Interromper uma chamada em curso não economiza a GPU, porque o serviço termina a
inferência de qualquer modo, e deixaria um registro sem resposta. Retomar o histórico depois de uma
desabilitação levaria ao modelo conversas feitas sob outra decisão, talvez sob outros requisitos.

**O custo.** A resposta da chamada em curso fica registrada e não é mostrada.

### D-009 — A regra de exclusão do piloto não muda

**Decisão.** O comando, o prazo de 90 dias e a âncora no relatório final continuam (FR-7534). A
desabilitação não é relatório final, e o dado de candidato real não entra nessa regra (FR-7535).

**Por quê.** A regra foi decidida pela DP-2 da `071` para perguntas da equipe, e não para texto
livre de candidatos. Estendê-la seria decidir a retenção de dado pessoal sem o encarregado.

### D-010 — O piloto em produção deixa de exigir sessão acompanhada

**Decisão.** Ver Q-3.

**Por quê.** A sessão acompanhada foi escolhida porque a gestão não autenticava em produção. Com a
sessão institucional e o papel concedido pessoa a pessoa, com trilha, a razão caiu. A orientação
passa da fala da equipe para a tela.

**O custo.** O uso fica espontâneo e menos observado. A avaliação da qualidade continua sendo a da
matriz e do relatório.
