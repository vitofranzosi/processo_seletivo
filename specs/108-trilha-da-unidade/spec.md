# Feature Specification: Trilha da unidade

**Feature Branch**: `claude/108-trilha-da-unidade`, sobre a `main` em `ca1e53ed` (depois da `106` e
da `107`).

**Created**: 2026-10-30

**Status**: Implementada nesta branch; merge não autorizado.

**Input**: o item 3 da sequência que o usuário adotou no parecer de 30/10/2026, no topo da
[auditoria da administração institucional](../../doc/auditoria-administracao-institucional-2026-10-30.md):
"Trilha administrativa por unidade — spec pequena, só leitura". Resolve M-14, M-22, J-8 e R-4 da
auditoria (§1, item 1; §7, item 2; §8, grupo 2 do backlog).

> **Faixa de identificadores.** Esta spec abre em **FR-3152** e **SC-1021**. O teto medido em
> 30/10/2026 na `main` e em todas as worktrees era o requisito três mil cento e cinquenta e um e o
> critério mil e vinte, os dois da `107`. **Nenhum `UX-` é aberto aqui.** As decisões técnicas
> reiniciam em `D-001` e moram no `research.md`.
>
> **Como esta spec cita outras.** Requisito de outra feature pelo identificador e pela feature ("a
> FR-3150 da `107`"); decisão de outra feature pelo assunto e pelo número por extenso.

---

## Por que esta feature existe

A trilha append-only grava os atos administrativos da unidade — o registro e a alteração dela, as
autoridades que assinam, os modelos de aviso, os avisos confirmados e interrompidos e, desde a
`106`, as concessões e revogações de acesso. **Nenhuma tela os mostra.** A trilha do Edital reúne
os atos do certame, a da comissão os da comissão, e a da avaliação os da Mesa; um ato que não é de
Edital nem de comissão não tem leitor. O guia de implantação manda consultá-los pelo `psql`
(`doc/implantacao-em-producao-ubuntu.md`, §20.3).

A auditoria ensaiou a pergunta "quem cadastrou ou encerrou esta autoridade?" (J-8): o registro
existe, e o Auditor, pela interface, encontrou **zero** ocorrências de "autoridade" na trilha do
Edital. É o inverso do que a trilha deveria permitir: o fiscal depende do administrador de banco, e
esse acesso direto não é auditado (R-4).

Esta feature dá a esses eventos um leitor: uma página da gestão, só de leitura, que mostra a trilha
administrativa da unidade a quem audita a unidade.

### O que foi conferido em 30/10/2026, antes de especificar

Lido no código da `main` em `ca1e53ed`. Cada linha é um evento que já se grava hoje, e nada aqui
muda o que se grava.

| Assunto | Operações | Agregado | Escopo gravado | Quem pratica |
|---|---|---|---|---|
| Unidade | registro, alteração (060); exclusão dos registros do piloto (071, gravada desde o grupo 0) | Unidade | a unidade | a implantação |
| Autoridades | cadastro, correção, encerramento (060) | AutoridadeHabilitada | a unidade | quem tem `autoridade:gerir` |
| Modelos de aviso | criação, edição, inativação, reativação; os três modelos iniciais (066) | ModeloDeAviso | a unidade | quem tem `aviso:enviar`; a implantação, nos iniciais |
| Avisos | confirmação (066) | Aviso | a unidade | quem tem `aviso:enviar` |
| Avisos | interrupção (066) | InterrupcaoDoAviso | a unidade | quem tem `aviso:enviar` |
| Acessos | concessão e revogação de papel operacional (106, 107) | Vínculo | a unidade | quem tem `acesso:gerir` |
| Acessos | concessão e revogação do Administrador de acessos **de uma unidade** (106, 107) | Vínculo | **o institucional** — o escopo do ator, e não o do vínculo | quem tem `acesso:administrar` |
| Acessos | administração institucional (106, 107) | Vínculo | o institucional | a implantação |
| Pessoa | suspensão, reativação (107) | SuspensaoDePessoa | o institucional | o administrador institucional; a implantação |
| Sessão | entrada, troca de unidade, saída, término por prazo (106, 107) | IdentidadeExterna | a unidade ativa, ou o institucional | a própria pessoa |
| Credencial do candidato | troca de credencial (010) | — | **vazio** | o candidato |

Três fatos pesam no desenho:

- **O escopo de um evento é o do ator**, e não o do objeto. A concessão do Administrador de acessos
  do `cefor` pelo administrador institucional fica no escopo institucional, e só o detalhe do
  registro diz que o vínculo é do `cefor`. Uma leitura só pelo escopo a perderia — e ela é a
  concessão que mais importa a quem fiscaliza a unidade.
- **O histórico de acessos da `107` não é a trilha.** Ele é lido dos próprios vínculos e
  revogações (a FR-3107 da `107`), exige `acesso:consultar` e é a ferramenta de trabalho de quem
  concede. O Auditor não tem essa permissão.
- **As credenciais do candidato têm escopo vazio** (a decisão doze da `010`), e por isso nenhuma
  consulta de unidade as alcança. Ficam fora por construção.

### O que esta spec cobre, e o que fica fora

**Cobre:** a página "Trilha da unidade", paginada, filtrável por assunto, para quem tem
`auditoria:consultar` na unidade ativa; o item correspondente na barra; o nome de quem praticou cada
ato; e a atualização do guia de implantação, que deixa de mandar ao `psql` o que a página mostra.

**Fora, de propósito:**

- exportação da trilha (M-23): espera a demanda do controle interno (Q-6 da auditoria);
- retenção e descarte (B-2);
- mudar o que se grava, ou como — nenhum evento novo, nenhum campo novo, nenhuma migration;
- a trilha do Edital, a da comissão e a da avaliação, que já existem e não mudam;
- uma leitura no nível institucional (`D-003`, pendência P1);
- as entradas, trocas e saídas de sessão (`D-004`, pendência P2).

---

## Clarifications

### Session 2026-10-30

Respostas tiradas do pedido, da auditoria e do código — nenhuma é decisão institucional nova. As
três que tocam governança estão abertas em §Decisões pendentes, e a spec adota, para cada uma, a
saída que não concede nada a ninguém.

- Q: Qual permissão abre a página? → A: `auditoria:consultar`, a do Auditor, na unidade ativa
  (`D-001`). É a permissão de "consultar a trilha de auditoria dos atos praticados", e o Auditor já
  lê, com ela, toda a trilha do certame da unidade. Uma permissão nova exigiria decidir a quem
  concedê-la, e isso é governança.
- Q: Os eventos de acesso entram, ou ficam só no histórico da `107`? → A: Entram (`D-002`). O
  histórico da `107` continua como está e não é copiado: ele serve a quem concede, e a trilha da
  unidade serve a quem fiscaliza quem concede. A pergunta "quem deu este acesso, e por quê" precisa
  de um leitor que não seja o próprio concedente.
- Q: Entra a concessão do Administrador de acessos da unidade, gravada no escopo institucional? → A:
  Entra, e só ela do escopo institucional (`D-002`): o vínculo é da unidade.
- Q: Há leitura no nível institucional? → A: Não nesta spec (`D-003`, pendência P1). O único papel
  institucional, o Administrador institucional de acessos, tem só `acesso:administrar`. Dar-lhe a
  trilha de todas as unidades lhe daria visão das autoridades, dos avisos e dos papéis operacionais
  que a `107` lhe recusou; dar-lhe só o escopo institucional seria ele ler os próprios atos, que o
  histórico da `107` já lhe mostra.
- Q: Entradas e saídas de sessão entram? → A: Não nesta spec (`D-004`, pendência P2). Não são atos
  administrativos, e uma por pessoa por dia soterraria os poucos atos que a página existe para
  mostrar.
- Q: O Gestor lê a página? → A: Não, por negar por padrão (pendência P3). Ele pratica a maior parte
  destes atos, e ganhar `auditoria:consultar` lhe abriria também a trilha de todo Edital.
- Q: O que aparece de cada evento? → A: o que responde "quem, quando, o quê, sobre o quê e por quê",
  e nada do conteúdo do aviso ou do modelo, nem dado de candidato (`D-005`).

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — O Auditor lê os atos administrativos da unidade (Priority: P1)

O Auditor do `cefor` abre "Trilha da unidade" na barra. Vê, do mais recente para o mais antigo, cada
ato administrativo da unidade: quando, o ato em palavras, sobre o quê, quem praticou, a situação e o
motivo registrado. Encontra quem cadastrou a autoridade que assina os Editais, e quando a anterior
foi encerrada.

**Why this priority**: é a jornada que tira o fiscal da dependência do administrador de banco
(J-8, R-4).

**Independent Test**: com uma autoridade cadastrada e encerrada pela tela, os modelos iniciais e um
aviso confirmado, o Auditor abre a página e lê os quatro atos, com autor, data e motivo, sem
terminal.

**Acceptance Scenarios**:

1. **Given** uma autoridade cadastrada por uma pessoa, **When** o Auditor abre a trilha da unidade,
   **Then** a linha diz "Cadastro de autoridade", o nome e o cargo da autoridade, quem a cadastrou e
   quando.
2. **Given** a unidade registrada pela sincronização, **When** o Auditor abre a trilha, **Then** o
   registro aparece como praticado pela "Implantação".
3. **Given** uma alteração da unidade, **When** o Auditor a lê, **Then** a linha diz quais dados
   mudaram, com o valor de antes e o de depois.
4. **Given** um modelo de aviso editado, **When** o Auditor lê a linha, **Then** ela nomeia o modelo
   e diz que foi editado, e **não** mostra o assunto nem o corpo.
5. **Given** um aviso confirmado e depois interrompido, **When** o Auditor lê as duas linhas,
   **Then** cada uma diz o Edital a que o aviso pertence e o motivo registrado, e nenhuma mostra
   endereço de e-mail.
6. **Given** mais de vinte atos, **When** o Auditor chega ao fim da primeira página, **Then** um
   botão leva aos anteriores, sem repetir nem pular nenhum.

---

### User Story 2 — A página só mostra a unidade de quem lê (Priority: P1)

A página lê a unidade ativa do ator e nada mais. Quem não tem `auditoria:consultar` não a alcança, e
nenhum endereço montado à mão a faz mostrar outra unidade.

**Why this priority**: uma trilha que vaza o escopo é pior que nenhuma (Princípio de negar por
padrão).

**Independent Test**: com atos no `cefor` e na fictícia `campus-a`, o Auditor do `cefor` vê só os do
`cefor`, em qualquer combinação de parâmetros; o Elaborador recebe a recusa explicada.

**Acceptance Scenarios**:

1. **Given** uma pessoa sem `auditoria:consultar`, **When** abre o endereço da página, **Then** a
   recusa diz o que falta, e a barra não oferecia o item.
2. **Given** atos na `campus-a`, **When** o Auditor do `cefor` abre a página, com ou sem parâmetros
   que nomeiem a `campus-a`, **Then** nenhum deles aparece.
3. **Given** uma troca de credencial de candidato, **When** o Auditor abre a página, **Then** ela não
   aparece.
4. **Given** a publicação de um Edital da unidade, **When** o Auditor abre a página, **Then** ela não
   aparece: é da trilha do Edital.
5. **Given** um cursor de paginação adulterado, **When** a página o recebe, **Then** a resposta é a
   recusa de cursor inválido, e nada é mostrado.

---

### User Story 3 — Quem deu e quem tirou acesso na unidade (Priority: P2)

No modo institucional, o Auditor do `cefor` lê, na mesma linha do tempo, cada concessão e cada
revogação de acesso no `cefor`: a quem, qual papel, por quem e por quê — inclusive a do
Administrador de acessos da unidade, concedido pelo administrador institucional.

**Why this priority**: o histórico da `107` só é lido por quem concede; sem esta história, quem
concede não teria fiscal.

**Independent Test**: com uma concessão de Elaborador pelo Administrador de acessos do `cefor` e a
concessão do próprio Administrador de acessos pelo administrador institucional, o Auditor do `cefor`
lê as duas, com o nome das pessoas.

**Acceptance Scenarios**:

1. **Given** uma concessão de papel operacional no `cefor`, **When** o Auditor lê a linha, **Then**
   ela diz "Concessão de acesso", o nome de quem recebeu, o papel pelo nome, quem concedeu e o
   motivo.
2. **Given** a concessão do Administrador de acessos do `cefor` pelo administrador institucional,
   **When** o Auditor do `cefor` abre a página, **Then** ela aparece.
3. **Given** a concessão do Administrador de acessos da `campus-a`, **When** o Auditor do `cefor` abre
   a página, **Then** ela não aparece.
4. **Given** uma suspensão de pessoa ou uma entrada de sessão, **When** o Auditor abre a página,
   **Then** elas não aparecem (`D-003`, `D-004`).

---

### User Story 4 — Filtrar por assunto (Priority: P2)

O Auditor escolhe um assunto — Unidade, Autoridades, Modelos de aviso, Avisos ou Acessos — e a
página mostra só os atos dele, e o filtro continua nas páginas seguintes.

**Why this priority**: os avisos se acumulam a cada resultado publicado; sem filtro, a autoridade
encerrada há seis meses fica na décima página.

**Independent Test**: com atos dos cinco assuntos, cada filtro mostra só os do assunto, e "Todos"
mostra os cinco.

**Acceptance Scenarios**:

1. **Given** o filtro "Autoridades", **When** o Auditor filtra, **Then** só os cadastros, correções e
   encerramentos aparecem.
2. **Given** um filtro e mais de uma página, **When** o Auditor avança, **Then** a página seguinte
   continua filtrada.
3. **Given** um filtro sem atos, **When** o Auditor filtra, **Then** a página diz que nenhum ato
   corresponde ao filtro, e oferece limpá-lo.

---

### User Story 5 — Demonstrável pelo seletor (Priority: P3)

Na homologação, quem entra pelo seletor de identidade com o papel Auditor alcança a página e lê os
atos do banco de demonstração; quem os praticou aparece pelo identificador escolhido no seletor, e
a implantação como "Implantação".

**Why this priority**: a página precisa ser vista antes de a identidade institucional existir em
produção.

**Independent Test**: no banco de demonstração, o Auditor do seletor abre a página pela barra e lê o
registro da unidade, os modelos iniciais e as autoridades do `seed_demo`.

**Acceptance Scenarios**:

1. **Given** o seletor com o papel Auditor, **When** a pessoa entra, **Then** a barra oferece
   "Trilha da unidade".
2. **Given** o seletor com os outros sete papéis e sem o Auditor, **When** a pessoa entra, **Then**
   a barra não oferece o item.

---

### Edge Cases

- **Unidade sem nenhum ato administrativo** (banco novo antes da sincronização): a página diz que
  não há ato registrado, sem erro.
- **Pessoa institucional sem nome informado**: aparece como o FR-3103 da `107` manda — o e-mail
  institucional, ou "pessoa sem nome informado"; nunca o identificador interno.
- **O autor de um ato é um identificador que não é pessoa institucional nem implantação** (atos da
  demonstração): aparece como foi gravado.
- **O nome da autoridade ou do modelo mudou depois do ato**: a linha mostra o nome registrado no
  momento do ato, e não o de hoje.
- **O aviso de um Edital cancelado**: a linha continua dizendo o Edital; a página não abre o Edital,
  só o nomeia.
- **Uma operação nova num dos assuntos incluídos, sem rótulo**: o guardião da feature reprova; a
  página não mostra o código cru.
- **Dois atos no mesmo instante**: a ordem é estável e a paginação não repete nem pula, porque o
  cursor desempata pelo identificador do evento.
- **Filtro com valor desconhecido** (endereço montado à mão): a página mostra todos os assuntos, e
  o seletor do filtro mostra "Todos" — nada aparece filtrado sem que se diga.
- **O vínculo é de pessoa suspensa depois**: a linha da concessão continua com o nome dela; a
  suspensão não aparece (`D-003`).

---

## Requirements *(mandatory)*

### Functional Requirements

**Acesso à página**

- **FR-3152**: A gestão MUST oferecer a página "Trilha da unidade", só de leitura, que lista os atos
  administrativos da unidade ativa de quem a abre. A página MUST NOT ter ação que grave.
- **FR-3153**: A página MUST exigir `auditoria:consultar` na unidade ativa, conferida no servidor.
  Sem ela, a resposta MUST ser a recusa explicada da `033` (403), nomeando o que falta.
- **FR-3154**: A unidade lida MUST ser a unidade ativa do ator. Ela MUST NOT vir do endereço, do
  formulário nem de outro parâmetro, e nenhum parâmetro MUST fazer a página ler outra unidade.
- **FR-3155**: A barra da gestão MUST oferecer "Trilha da unidade", no grupo da unidade, a quem tem
  `auditoria:consultar`, e só a essa pessoa, tanto na demonstração quanto no modo institucional.
- **FR-3156**: O seletor de demonstração MUST continuar com os mesmos oito papéis, e o Auditor dele
  MUST alcançar a página.

**O que entra**

- **FR-3157**: A página MUST incluir os eventos gravados no escopo da unidade sobre: a unidade
  (registro, alteração, exclusão dos registros do piloto); as autoridades (cadastro, correção,
  encerramento); os modelos de aviso (criação, edição, inativação, reativação e os modelos
  iniciais); os avisos (confirmação e interrupção); e os vínculos de acesso (concessão e
  revogação).
- **FR-3158**: A página MUST incluir também as concessões e revogações de vínculo **desta unidade**
  gravadas no escopo institucional, e MUST NOT incluir nenhum outro evento do escopo institucional.
- **FR-3159**: A página MUST NOT incluir eventos de outra unidade, eventos de escopo vazio, eventos
  de sessão (entrada, troca de unidade, saída, término por prazo), suspensões e reativações de
  pessoa, nem os atos de Processo, Edital, Retificação, inscrição, comissão, avaliação, resultado,
  recurso, ocupação e convocação, que têm trilha própria.

**O que se mostra de cada ato**

- **FR-3160**: Cada ato MUST mostrar: a data e a hora; o ato em palavras; sobre o quê; quem o
  praticou; a situação, de antes para depois, quando o evento a registrar; e o motivo registrado,
  quando houver.
- **FR-3161**: Quem praticou MUST aparecer pelo nome da pessoa institucional, pela mesma tradução
  das demais telas (a FR-3150 da `107`); como foi escolhido no seletor, na demonstração; e como
  "Implantação" quando o ator for o comando de implantação. A página MUST NOT mostrar
  `pessoa-<uuid>`.
- **FR-3162**: "Sobre o quê" MUST dizer: para a unidade, o nome dela registrado no ato; para a
  autoridade, o nome e o cargo registrados no ato; para o modelo de aviso, o nome registrado no ato;
  para o aviso e a interrupção, o Edital do aviso, por número e ano, e a origem do aviso (resultado
  ou chamada); para o vínculo, o nome da pessoa que recebeu ou perdeu o acesso e o papel pelo nome do
  catálogo.
- **FR-3163**: A alteração da unidade e a correção ou o encerramento da autoridade MUST dizer quais
  dados mudaram, pelo nome do dado e com o valor de antes e o de depois. São dados institucionais
  públicos: os do cabeçalho dos atos publicados e os de quem os assina.
- **FR-3164**: A página MUST NOT mostrar: endereço de e-mail ou qualquer outro dado de candidato; o
  assunto ou o corpo de aviso ou de modelo; o identificador interno da pessoa ou o do provedor; a
  correlação, a chave de idempotência ou o detalhe técnico do registro.
- **FR-3165**: Toda operação dos assuntos incluídos MUST ter rótulo em palavras, e toda situação
  registrada por elas MUST ter tradução; a página MUST NOT mostrar código de operação cru.

**Paginação, filtro e custo**

- **FR-3166**: Os atos MUST vir do mais recente para o mais antigo, em páginas de vinte, com um botão
  para os anteriores. A paginação MUST ser estável: um ato gravado enquanto se lê não repete nem
  esconde outro.
- **FR-3167**: A página MUST oferecer o filtro por assunto — Todos, Unidade, Autoridades, Modelos de
  aviso, Avisos e Acessos —, e o filtro MUST continuar nas páginas seguintes. Um valor desconhecido
  MUST valer como "Todos", com o seletor mostrando "Todos".
- **FR-3168**: O número de consultas ao banco para montar uma página MUST NOT crescer com o número de
  atos exibidos nem com o tamanho da trilha.

**Integridade e documentação**

- **FR-3169**: A página MUST NOT gravar nada — nem evento, nem idempotência — e MUST NOT alterar
  nenhum registro da trilha.
- **FR-3170**: O estilo da página MUST estar em arquivo estático; toda classe nova MUST ter regra na
  folha.
- **FR-3171**: O guia de implantação MUST apontar a página como o caminho para os atos
  administrativos da unidade, e deixar o `psql` só para o que ela não mostra.

### Key Entities

- **Ato administrativo da unidade**: um registro da trilha de auditoria cujo assunto é a unidade,
  uma autoridade, um modelo de aviso, um aviso ou um vínculo de acesso, e cujo escopo é a unidade —
  ou, para o vínculo, o institucional com a unidade como escopo do vínculo. Nasce e não muda.
- **Assunto**: o agrupamento oferecido ao filtro, derivado do tipo do registro. Não é gravado.

---

## Avaliação LGPD

A Constituição (Princípio III) pede que cada especificação avalie os requisitos aplicáveis da LGPD.
Esta feature **não coleta, não grava e não retém** dado nenhum. Ela exibe dados já gravados a um
leitor novo, e a avaliação é sobre essa exibição.

| Aspecto | Avaliação |
|---|---|
| **Titulares alcançados** | servidores que praticaram ato administrativo, ou que receberam ou perderam acesso na unidade. **Nenhum candidato**: as credenciais têm escopo vazio, e os avisos aparecem sem destinatário (FR-3159, FR-3164) |
| **Dados exibidos** | o nome do servidor (ou, sem nome, o e-mail institucional, como manda o FR-3103 da `107`); o nome e o cargo da autoridade signatária, que já são publicados nos atos; os dados da unidade, que são públicos |
| **Finalidade** | a fiscalização dos atos administrativos da unidade, que é a finalidade com que a trilha já é gravada (Princípio III: "permitir investigação e reconstrução histórica") |
| **Necessidade e minimização** | só o que responde "quem, quando, o quê, sobre o quê e por quê". Fora: o assunto e o corpo de aviso e de modelo, que podem citar candidatos; o identificador interno e o do provedor; a correlação, que liga o ato ao log de acesso (FR-3164) |
| **Quem lê** | só quem tem `auditoria:consultar` na unidade, e só a unidade dele (FR-3153, FR-3154); o Auditor já lê, com a mesma permissão, a trilha do certame, que expõe mais |
| **Retenção** | a da trilha, que é permanente e não muda aqui. A política de retenção é o B-2, fora desta spec |
| **Risco residual** | o motivo é texto livre de quem praticou o ato, e pode citar uma pessoa. É o mesmo risco da trilha do Edital, que mostra o motivo como foi gravado; nenhuma tela o reescreve, porque a trilha é prova |

---

## Decisões pendentes (do usuário)

Cada uma tem a saída adotada nesta spec, que é a que não concede nada. Mudar qualquer uma é decisão
de governança, e custa pouco no código: o mapa dos assuntos, uma permissão no catálogo de papéis.

### P1 — Quem audita o nível institucional?

Os eventos do escopo institucional — administração institucional concedida, retirada e substituída;
suspensões e reativações; sessões de quem não tem unidade — continuam sem leitor de fiscalização.

| Opção | O que significa |
|---|---|
| **A (adotada)** | Ninguém, por ora; o administrador institucional vê o histórico da `107`, que é o dos próprios atos |
| B | Um papel institucional de auditoria, com `auditoria:consultar` no escopo institucional, que leria os atos institucionais e os de todas as unidades — concedido pela implantação, como o administrador institucional |
| C | O Administrador institucional de acessos lê a trilha de acessos de todas as unidades (a alternativa G1 do estudo de 30/10), sem autoridades nem avisos |

### P2 — Entradas e saídas de sessão entram na trilha da unidade?

| Opção | O que significa |
|---|---|
| **A (adotada)** | Não; continuam gravadas e sem leitor |
| B | Entram, num assunto próprio ("Sessões"), fora do "Todos" |
| C | Ficam para uma página de "quem atua nesta unidade", com o histórico de entrada por pessoa |

### P3 — O Gestor lê a trilha da unidade?

| Opção | O que significa |
|---|---|
| **A (adotada)** | Não; só quem tem `auditoria:consultar` |
| B | Sim, por uma permissão própria (`trilha-da-unidade:consultar`), dada ao Gestor e ao Auditor, para que o Gestor não ganhe a trilha dos Editais |

---

## Achados registrados (fora de escopo)

- **A confirmação do aviso grava o identificador do marco no motivo** ("chamada do marco `<uuid>`"),
  e a trilha o mostra como foi gravado. Mudar o texto do motivo é mudar o que se grava, que esta spec
  não faz. A linha nomeia o Edital ao lado, e isso basta para a leitura.
- **Ler a trilha pela aplicação não vai à trilha.** É o mesmo da trilha do Edital e da comissão: a
  leitura é de quem tem o papel, e não é ato. O `psql` continua não auditado (R-4), e o guia manda
  restringi-lo.
- **A API `GET /api/v1/admin/auditoria` continua fechada em produção** até a identidade
  institucional. Esta spec não a abre.
- **A interrupção do aviso grava na trilha um identificador que não é o dela.** `InterrupcaoDoAviso`
  tem chave inteira, e `RegistroAuditoria.aggregate_id` é UUID: o campo converte o inteiro em
  `UUID(int=pk)` sem acusar (`00000000-0000-0000-0000-000000000001` para a primeira). O registro
  continua único dentro do tipo, e a página o lê de volta pelo `.int`, mas o identificador gravado
  não é o de objeto nenhum, e uma consulta pela trilha que o procure como UUID de verdade não o
  acha. Encontrado ao implementar; a correção seria mudar o que se grava, fora desta spec.
- **A suspensão de uma pessoa que atua na unidade não aparece na trilha da unidade** (`D-003`): ela
  é global. Quem fiscaliza a unidade vê a concessão e a revogação, e não a suspensão.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1021**: Em 100% dos casos exercitados, todo ato administrativo dos cinco assuntos gravado para
  a unidade aparece na página, e a contagem da página é igual à dos registros do mesmo critério no
  banco.
- **SC-1022**: Zero atos de outra unidade, de escopo vazio, de sessão ou de suspensão aparecem, em
  qualquer combinação de parâmetros exercitada.
- **SC-1023**: Uma página com um ato e uma com vinte atos, dos cinco assuntos, custam o mesmo número
  de consultas ao banco.
- **SC-1024**: Zero ocorrências de `pessoa-<uuid>`, de endereço de e-mail de candidato e de texto de
  aviso ou de modelo na página.
- **SC-1025**: O Auditor responde "quem cadastrou e quem encerrou esta autoridade, e quando" a
  partir da barra, em no máximo duas telas, sem terminal.
- **SC-1026**: A suíte existente passa contra PostgreSQL sem mudar resultado esperado.

## Assumptions

- A `106` e a `107` estão na `main` (`ca1e53ed`); esta feature não muda nada delas.
- As unidades dos testes de duas unidades são o `cefor` e a fictícia `campus-a`, como na `106`.
- O nome e o e-mail institucional de um servidor são dados que os servidores já veem uns dos outros
  no Ifes (premissa da `107`); o Auditor os vê como quem concede os vê.
- O volume da trilha administrativa de uma unidade é de dezenas a poucos milhares de eventos por ano;
  o índice existente da trilha e o filtro por escopo bastam para a página de vinte.
- Na homologação, a página se demonstra pelo seletor; os eventos de acesso, que só nascem no modo
  institucional, se demonstram pelos testes, como as telas da `107`.
