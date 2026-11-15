# Feature Specification: A habilitação da verificação por vídeo pela interface

**Feature Branch**: `claude/169-habilitacao-do-video-c52b1d`, nascida da `main` em `7d5c6ade` (merge da
`166`, #547)

**Created**: 2026-11-14

**Status**: Especificada em 14/11. Só spec: sem plano, sem tarefas, sem código. Quatro perguntas ao
usuário (Q-1 a Q-4), cada uma com recomendação adotada como comportamento provisório. **Nada aqui
autoriza o vídeo**: nenhum valor de P-0, P-7, P-8 ou P-10 é registrado, presumido ou semeado.

**Input**: a decisão do usuário de 14/11/2026 — "a habilitação poderia ser via interface no sistema; o
mesmo se aplica ao assistente de IA" —, com o desenho que ele aceitou como ponto de partida:
capacidade no ambiente, decisão institucional registrada na interface. A spec irmã, do assistente, é a
`170`.

> **Faixa de identificadores.** Esta spec abre em **FR-7400**, **SC-2430** e **UX-800**. Os tetos
> medidos em 14/11/2026 eram, na `main`, o requisito sete mil cento e cinquenta e três, o critério dois
> mil trezentos e setenta e sete e o requisito de experiência setecentos e setenta e quatro, todos da
> `166`; a `167` (#548) usa a faixa do requisito sete mil e duzentos, e a `168` reservou a do sete mil e
> trezentos. A faixa até o requisito sete mil quatrocentos e noventa e nove fica reservada. As decisões
> reiniciam em `D-001`; as perguntas ao usuário são `Q-`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-7101 da `166`"). Uma decisão de outra feature é citada pelo assunto e pela feature. As
> pendências do estudo da verificação (`P-0` a `P-12`) e as regras dele (`R-1` a `R-24`) são locais ao
> estudo, e se citam por extenso.

---

## Por que esta feature existe

A `166` entregou a camada B do estudo da verificação da autodeclaração — o vídeo gravado pelo
candidato, opcional, que **só confirma** — inteira e desligada. A decisão de usá-la em produção mora
hoje **no código**: as settings de produção recusam subir com a chave `VERIFICACAO_POR_VIDEO` (a
FR-7101 da `166`), e o comentário diz que a recusa "só sai por PR revisado", depois do ato do Conselho
Superior, do protocolo da CPVA e do Edital que o cite (a P-0). O prazo de guarda do arquivo, a P-10, é
uma variável de ambiente sem valor. O roteiro (P-8) e a regra do menor (P-7) são padrões provisórios
escritos no código.

Isso põe uma decisão institucional nas mãos de quem revisa um PR, e não de quem a instituição designou.
A decisão de usar o vídeo é do Conselho Superior e da CPVA; quem a **registra** no sistema deve ser uma
pessoa com papel institucional, por um ato com motivo e trilha, como já acontece com o registro de
Unidades (`110`). Em 14/10 o usuário já recusou, para as configurações, a conclusão "nenhuma interface"
(a auditoria que gerou a `073`).

**Esta spec revê, de forma explícita, a decisão da `166` de deixar a porta do piloto num PR.** Não a
contorna: a base normativa continua sendo exigida, inteira, antes de qualquer vídeo; o que muda é
**onde** ela se registra e **quem** a registra.

### O princípio, comum à `169` e à `170`

- **O ambiente diz o que o servidor pode oferecer.** A variável de ambiente declara a capacidade: a
  infraestrutura existe e está configurada. Ela sozinha não habilita nada.
- **A instituição decide se usa, pela interface.** A decisão é um ato registrado, com autor, motivo e
  trilha, por quem tem o papel, e nunca se apaga.
- **Sem capacidade, a interface não oferece a habilitação.** Sem a decisão registrada, a capacidade
  não alcança ninguém.

### O que esta spec cobre, e o que fica fora

**Cobre:**

- a variável de ambiente, que passa a dizer só a capacidade, e a recusa da produção, que passa a ser a
  da combinação incoerente;
- o registro da **base normativa do vídeo** na administração institucional, pelo Administrador
  institucional: o ato do Conselho Superior, o protocolo da CPVA, o roteiro (P-8), a regra do menor
  (P-7), o prazo de guarda (P-10) e as unidades alcançadas;
- a alteração e a revogação da base, append-only, e a regra da revogação com vídeos já enviados;
- o Edital que **cita** a base: a admissão do vídeo pela Etapa, que a `166` já publica, passa a exigir
  a base e a gravar a citação no conteúdo publicado e no documento;
- uma resposta só para "o vídeo está habilitado neste Edital", que todo ponto que hoje lê a chave
  passa a consultar;
- a porta do piloto reescrita.

**Fica fora**, como registro e não como escopo:

- **qualquer valor** de P-0, P-7, P-8 ou P-10. A spec cria o lugar onde a instituição os registra, e
  não os registra;
- o roteiro editável e a regra do menor diferente da implementada: a base escolhe entre o que o sistema
  já faz. Um protocolo que aprove outra coisa pede spec nova (FR-7407);
- um painel genérico de configurações, ou qualquer outra configuração editável pela interface;
- o assistente de IA, que é a `170`;
- a orientação da entrega 4 do estudo (`168`) e o agendamento da entrevista ao vivo (`167`);
- o aviso automático aos candidatos quando a base é revogada (Q-3).

### O que a `166` deixa de valer

A `166` continua valendo inteira no que diz sobre o candidato, a Mesa, a deliberação e a retenção. O
que esta spec revê:

| Da `166` | O que dizia | O que passa a valer |
|---|---|---|
| FR-7100 | a camada B fica atrás da chave `VERIFICACAO_POR_VIDEO` | a chave muda de nome e de sentido: diz só a capacidade; o vídeo depende da capacidade **e** da base registrada **e** do Edital que a cita (FR-7400, FR-7424) |
| FR-7101 | a produção recusa subir com a chave ligada, e esta spec não remove nem abranda a recusa | **revista por decisão do usuário**: a produção recusa só a combinação incoerente (FR-7401) |
| FR-7104 | publicação e Retificação recusam a admissão com a chave desligada | recusam sem a capacidade **ou** sem base vigente que alcance a unidade, nomeando o que falta (FR-7418) |
| FR-7109 | maioridade declarada, "padrão provisório da P-7" | o comportamento fica; a regra passa a ser a que a base registra e o Edital cita (FR-7427) |
| FR-7112 | o roteiro de referência, "padrão provisório da P-8" | o roteiro passa a ser a versão que a base registra e o Edital cita (FR-7426) |
| FR-7146 e FR-7147 | o prazo de retenção é variável de ambiente sem valor | o prazo é o que a base registra; a variável deixa de existir (FR-7402, FR-7429) |
| FR-7153 | a porta do piloto termina num PR revisado que libere a chave para um Edital | a porta termina no registro da base pela interface (FR-7434) |
| User Story 7 e SC-2376, na parte da produção | a produção recusa a chave | a produção sobe com a capacidade coerente (SC-2436) |
| a frase da composição | "O vídeo depende de protocolo institucional que ainda não existe" | a razão nomeada do que falta (FR-7422, UX-802) |

---

## Clarifications

### Session 2026-11-14 (decisões e restrições do pedido)

- A habilitação é feita pela interface, e revê a FR-7101 da `166` de forma explícita.
- A interface **registra** a P-0, e não a substitui: sem a base registrada, recusa nomeada.
- A habilitação vale **por Edital**, porque o Edital precisa citar o protocolo.
- O roteiro (P-8), o prazo de guarda (P-10) e a regra do menor (P-7) são parâmetros com valor
  registrado. Sem valor, o vídeo não se habilita.
- No padrão do Administrador institucional que já existe (a tela de Unidades da `110`): motivo,
  trilha, nada se exclui, habilitar e desabilitar são registros append-only. Desabilitar com vídeos
  enviados tem regra explícita.
- Negar por padrão: só o papel certo habilita, com verificação de escopo.
- Sem estrutura paralela e sem painel genérico; nenhum valor inventado ou presumido.

---

## User Scenarios & Testing *(mandatory)*

Os cenários usam o **Cefor** e o **Campus Vitória**, duas unidades registradas, e o **Edital 90/2026**
do Cefor, com a Etapa colegiada "Verificação da autodeclaração" da `166`. **Lúcia** é a Administradora
institucional. **Rafael**, da TI, opera o servidor. **Paula** elabora o Edital 90 no Cefor. Os números
de ato e de protocolo abaixo são fictícios, e marcados como tal: a spec não conhece os reais.

### User Story 1 — A TI declara a capacidade, e ela sozinha não habilita nada (Priority: P1)

Rafael prepara o armazenamento e os limites de envio e liga a capacidade do vídeo no ambiente de
produção. O servidor sobe. Nenhum candidato vê o vídeo, e nenhuma Etapa pode admiti-lo: a base não
está registrada. Na administração institucional, Lúcia passa a ver a habilitação oferecida.

**Why this priority**: é a separação que esta spec existe para fazer — a infraestrutura é da TI, a
decisão é da instituição.

**Independent Test**: subir as settings de produção com a capacidade ligada e coerente; conferir que o
portal, a composição e a publicação continuam sem vídeo; conferir que a tela da base oferece a
habilitação.

**Acceptance Scenarios**:

1. **Given** a capacidade ligada e o teto do vídeo coerente, **When** a produção sobe, **Then** ela
   sobe, e nenhuma rota do vídeo no portal responde com conteúdo.
2. **Given** a capacidade ligada e o teto do vídeo inteiro não positivo, **When** a produção sobe, **Then** ela recusa, nomeando a variável.
3. **Given** o ambiente com a variável de nome antigo, ou com o prazo de retenção, **When** qualquer
   ambiente sobe, **Then** ele recusa, dizendo o nome novo e que o prazo agora se registra na base.
4. **Given** a capacidade desligada, **When** Lúcia abre a tela da base, **Then** ela lê "O servidor
   não oferece a verificação por vídeo. Quem opera o servidor liga a capacidade." e nenhuma ação de
   habilitar ou alterar é oferecida.

---

### User Story 2 — A Administradora institucional registra a base normativa (Priority: P1)

Com a capacidade ligada, Lúcia abre "Verificação por vídeo" na administração institucional, ao lado de
Unidades e de Acessos. Preenche o número e a data do ato do Conselho Superior, a identificação e a data
do protocolo da CPVA, escolhe o roteiro e a regra do menor entre os que o sistema implementa — lendo
os passos e o texto de cada um —, informa o prazo de guarda em dias, marca o Cefor entre as unidades
alcançadas e escreve o motivo. A confirmação mostra tudo o que vai ser registrado. Ela confirma. A base
fica vigente, e a trilha registra quem, quando, o motivo e cada valor.

**Why this priority**: é o ato que substitui o PR revisado.

**Independent Test**: registrar com todos os valores; tentar registrar faltando cada um; conferir a
trilha e a ficha.

**Acceptance Scenarios**:

1. **Given** a capacidade ligada e nenhuma base vigente, **When** Lúcia preenche tudo e confirma,
   **Then** a base fica vigente e a trilha tem um evento com os valores e o motivo.
2. **Given** o formulário, **When** Lúcia o abre, **Then** nenhum campo vem preenchido nem
   pré-selecionado — nem o roteiro, que hoje tem uma opção só.
3. **Given** qualquer valor faltando — ato, data do ato, protocolo, data do protocolo, roteiro, regra
   do menor, prazo, unidade alcançada ou motivo —, **When** Lúcia confirma, **Then** a recusa nomeia o
   que falta e nada se grava.
4. **Given** a data do ato ou do protocolo no futuro, ou o prazo zero ou negativo, **When** Lúcia
   confirma, **Then** a recusa nomeia o campo.
5. **Given** uma base já vigente, **When** Lúcia tenta registrar outra, **Then** a recusa diz que se
   altera ou se revoga a vigente.

---

### User Story 3 — O Edital admite o vídeo e cita a base (Priority: P1)

Paula marca "Admite vídeo gravado pelo candidato" na Etapa do Edital 90. O campo está habilitado
porque a capacidade está ligada e a base vigente alcança o Cefor. Na Revisão, ela lê a citação que o
Edital vai publicar — o ato do Conselho Superior e o protocolo da CPVA, com números e datas —, e de
onde ela vem. Publica. O conteúdo publicado da Etapa guarda a citação daquela versão da base; o
documento a imprime na descrição da Etapa.

**Why this priority**: a habilitação vale por Edital, porque é o Edital publicado que dá ao candidato
o direito de escolher, e ele precisa citar a norma que o permite.

**Independent Test**: publicar com e sem base, com base de outra unidade, com capacidade desligada;
ler a citação no conteúdo publicado e no documento.

**Acceptance Scenarios**:

1. **Given** a capacidade ligada e a base vigente alcançando o Cefor, **When** Paula publica o Edital
   90 com a Etapa que admite o vídeo, **Then** o conteúdo publicado guarda a citação da versão vigente,
   e o documento cita o ato e o protocolo na descrição da Etapa.
2. **Given** nenhuma base vigente, **When** Paula abre a Etapa, **Then** o campo aparece desabilitado
   com a razão "Nenhuma base normativa do vídeo registrada. Quem registra é o Administrador
   institucional.", e a publicação de um rascunho que o marcou é recusada pela mesma razão.
3. **Given** a base vigente alcançando só o Campus Vitória, **When** Paula publica pelo Cefor, **Then** a
   recusa diz que a base não alcança o Cefor.
4. **Given** a base alterada entre a Revisão de Paula e a confirmação, **When** ela confirma, **Then** a
   publicação é recusada e a Revisão mostra a citação nova.
5. **Given** o Edital 90 publicado, **When** Lúcia altera a base para um roteiro novo, **Then** o
   documento do Edital 90, o roteiro que os candidatos dele veem e o que o envio confere continuam os
   da versão citada.

---

### User Story 4 — A base é revogada com vídeos já enviados (Priority: P1)

O Conselho Superior revoga o ato. Lúcia abre a base e escolhe "Revogar". A confirmação mostra o
alcance: o Edital 90 cita a base, tem 14 vídeos recebidos e 2 envios em andamento, e o período da Etapa
está aberto. Diz o que acontece: o portal deixa de oferecer o vídeo nos Editais que citam a base; os
envios em andamento não se concluem; os vídeos recebidos continuam na Mesa, a comissão continua os
assistindo e deliberando pela regra de que o vídeo só confirma, e nenhum arquivo é eliminado antes do
prazo; o Edital publicado não é reescrito, e a gestão de cada Edital precisa comunicar os candidatos.
Lúcia escreve o motivo e confirma.

**Why this priority**: desabilitar com vídeos já enviados é o caso que mais pode tirar direito ou
expor dado, e o pedido exige regra explícita.

**Independent Test**: com vídeos recebidos, envios em andamento e Avaliações abertas, revogar; conferir
o portal, a Mesa, os arquivos e a trilha.

**Acceptance Scenarios**:

1. **Given** a base vigente citada pelo Edital 90, **When** Lúcia revoga, **Then** na requisição
   seguinte o portal mostra a Maria "A gravação de vídeo não está mais disponível neste Edital. A
   entrevista ao vivo continua sendo o seu caminho." e nenhuma rota de envio aceita parte nem
   conclusão.
2. **Given** um envio em andamento, **When** a base é revogada antes da conclusão, **Then** a conclusão é
   recusada, o envio incompleto não produz vídeo, e o candidato fica no ao vivo.
3. **Given** 14 vídeos recebidos, **When** a base é revogada, **Then** os 14 continuam abertos à
   comissão na Mesa, os pareceres e encaminhamentos continuam possíveis, e nenhum Resultado
   desfavorável sai de parecer pelo vídeo (a FR-7139 da `166`).
4. **Given** a base revogada, **When** Lúcia tenta revogar de novo, **Then** a recusa não grava nada.
5. **Given** a base revogada, **When** o Conselho Superior edita um ato novo e Lúcia registra uma base
   nova, **Then** os Editais novos podem citá-la, e o Edital 90, que citou a revogada, continua sem
   vídeo no portal.

---

### User Story 5 — A base muda, e o que o Edital citou não muda (Priority: P2)

A CPVA aprova um protocolo novo, com outro prazo de guarda. Lúcia escolhe "Alterar", vê os valores
vigentes, muda o protocolo e o prazo, escreve o motivo. A confirmação mostra o antes e o depois, e
quais Editais citam a versão anterior. A base passa a ter uma versão nova; a anterior continua
registrada.

**Why this priority**: o protocolo vai mudar ao longo do tempo, e o Edital publicado não pode mudar
com ele.

**Independent Test**: alterar depois de um Edital publicado; conferir que o Edital mantém a citação;
alterar sem mudar nada.

**Acceptance Scenarios**:

1. **Given** a base vigente, **When** Lúcia altera o protocolo, **Then** uma versão nova fica vigente,
   a anterior fica no histórico, e a trilha tem o antes e o depois de cada valor mudado.
2. **Given** a alteração sem nenhuma mudança, **When** Lúcia confirma, **Then** a recusa diz que nada
   mudou, sem gravar.
3. **Given** a alteração que retira o Cefor das unidades alcançadas, **When** Lúcia confirma, **Then** a
   confirmação antes avisou que o portal fecha nos Editais do Cefor que citam a base, e ele fecha.

---

### User Story 6 — Só quem tem o papel vê e age (Priority: P1)

Ricardo, presidente de comissão no Cefor, tenta abrir a tela da base pelo endereço. Lúcia, com o escopo
do Cefor ativo no seletor, também. A sessão de demonstração também. Todos recebem a recusa, antes de
qualquer leitura.

**Why this priority**: negar por padrão. A base é uma autorização institucional sobre dado sensível.

**Independent Test**: cada ator, cada rota, cada ato.

**Acceptance Scenarios**:

1. **Given** Ricardo, com qualquer papel de unidade, **When** ele pede a tela ou um ato, **Then** recebe
   a recusa, e a barra não oferece o item.
2. **Given** Lúcia com o escopo de uma unidade ativo, **When** ela pede a tela, **Then** recebe a recusa;
   com o escopo institucional, a tela abre.
3. **Given** a sessão de demonstração, **When** ela pede a tela, **Then** recebe a recusa antes de
   qualquer leitura.

---

### User Story 7 — A retenção lê o prazo registrado (Priority: P3)

Rafael roda o comando de eliminação dos vídeos do Edital 90, encerrado. O comando lê o prazo da base,
confere que ele passou desde o encerramento e elimina os arquivos, como a `166` já faz. Sem base
nenhuma para o Edital, recusa, dizendo que o prazo não está registrado.

**Why this priority**: o prazo é a P-10. Esta spec só muda de onde ele vem.

**Independent Test**: o comando com base, sem base, com a base alterada depois dos vídeos.

**Acceptance Scenarios**:

1. **Given** o Edital 90 encerrado e o prazo da base vencido, **When** o comando roda com a
   confirmação, **Then** elimina e registra o prazo aplicado e a versão da base de onde ele veio.
2. **Given** um Edital cuja Etapa não cita base nenhuma, **When** o comando roda, **Then** recusa sem
   eliminar nada.

---

### Edge Cases

Cada caso-limite é requisito, e aponta o requisito que o cobre.

- **A capacidade desligada com base vigente e Editais em curso**: o portal fecha, como na revogação, e
  a Mesa continua; religada, o portal reabre, porque a base continua vigente (FR-7424, FR-7425).
- **A revogação no meio de um envio**: a conclusão é recusada e o envio incompleto descartado; o
  candidato fica no ao vivo, que nunca é ausência (FR-7431).
- **A revogação no meio do período, com candidatos que ainda não gravaram**: eles ficam no ao vivo, que
  o Edital já garante valer igual; nenhum perde direito (FR-7431, Q-3).
- **A base alterada entre a Revisão e a confirmação da publicação**: a publicação é recusada, e a
  Revisão mostra a citação nova (FR-7421).
- **A base alterada depois da publicação**: o Edital mantém a versão que citou — roteiro, regra do
  menor e citação no documento (FR-7423, FR-7426, FR-7427).
- **O prazo de guarda alterado depois de vídeos recebidos**: a eliminação usa o prazo da versão mais
  recente da base, e a confirmação da alteração mostra os Editais afetados (FR-7429, Q-2).
- **A retirada de uma unidade do alcance**: o portal fecha nos Editais dela que citam a base, como na
  revogação (FR-7424, FR-7432).
- **Uma base nova depois de uma revogada**: os Editais que citaram a revogada continuam sem vídeo no
  portal; a Retificação não troca a citação (FR-7423, FR-7424).
- **O rascunho que marcou o vídeo, e a base revogada antes da publicação**: o campo fica desabilitado
  com a razão, e a publicação recusa (FR-7418, FR-7422).
- **O Edital de unidade que a base não alcança**: a publicação recusa, nomeando a unidade (FR-7418).
- **O Edital publicado em desenvolvimento pela `166`, com o vídeo e sem citação**: é lido como sem
  habilitação; o portal fica fechado e a Mesa continua (FR-7419, FR-7424, FR-7425).
- **Duas pessoas registrando, alterando ou revogando ao mesmo tempo**: no máximo uma versão vigente;
  o segundo ato reconfere sob trava e é recusado se o estado mudou (FR-7412).
- **A Retificação que acrescenta o vídeo a outra Etapa do mesmo Edital**: a Etapa nova cita a versão
  vigente na Retificação; a que já admitia mantém a sua (FR-7423).
- **A alteração sem mudança, a revogação de base revogada, o registro com base vigente**: recusados sem
  gravar (FR-7408, FR-7409).
- **O protocolo da CPVA aprova um roteiro ou uma regra do menor que o sistema não implementa**: não há
  opção para escolher; a tela diz que a habilitação espera spec nova (FR-7407).
- **A revogação com a capacidade desligada**: é sempre oferecida; tirar a autorização não depende do
  servidor (FR-7411).
- **O Administrador institucional com escopo de unidade ativo, e a sessão de demonstração**: recusados
  antes de qualquer leitura (FR-7414).
- **A variável de nome antigo no ambiente, ou a do prazo de retenção**: o ambiente recusa subir,
  dizendo o que mudou (FR-7400, FR-7402).
- **A data do ato ou do protocolo no futuro, o prazo zero ou negativo**: recusados, nomeando o campo
  (FR-7406).
- **O Edital encerrado com a base revogada**: a eliminação continua pelo prazo; a revogação não
  elimina nada nem impede a eliminação (FR-7429, FR-7433).
- **O recurso contra Resultado da entrevista ao vivo, num Edital cuja base foi revogada**: segue a
  `165` e a `166`, sem mudança; a revogação não toca pareceres nem Resultados (FR-7433).

## Requirements *(mandatory)*

### Functional Requirements

#### A capacidade, no ambiente

- **FR-7400**: A variável `VERIFICACAO_POR_VIDEO` DEVE passar a se chamar
  `VERIFICACAO_POR_VIDEO_CAPACIDADE` e a dizer **só** que o servidor pode oferecer o vídeo, porque a
  infraestrutura que a `166` exige está configurada. Desligada por padrão. Ligada, ela sozinha NÃO DEVE
  habilitar nada. Todo ambiente DEVE recusar subir com a variável de nome antigo definida, dizendo o
  nome novo e o sentido novo.
- **FR-7401**: As settings de produção NÃO DEVEM mais recusar a capacidade ligada. DEVEM recusar só a
  combinação incoerente: a capacidade ligada com o teto do vídeo inteiro não positivo. Cada recusa DEVE nomear a variável, pelo mesmo mecanismo das
  outras recusas de produção.
- **FR-7402**: A variável do prazo de retenção (`VERIFICACAO_POR_VIDEO_RETENCAO_DIAS`) DEVE deixar de
  existir. Todo ambiente DEVE recusar subir com ela definida, dizendo que o prazo se registra na base
  normativa do vídeo.
- **FR-7403**: O guia de implantação, na seção "Configurar, verificar e testar" (a FR-1650 da `073`), e
  o `.env.example` DEVEM descrever a capacidade: o que ela exige, que ela não habilita o vídeo, e onde a
  decisão se registra.

#### A base normativa do vídeo

- **FR-7404**: O sistema DEVE manter a **base normativa do vídeo**: um registro institucional,
  append-only, em versões. Cada ato — registrar, alterar, revogar — DEVE gravar uma versão nova;
  nenhuma versão DEVE ser editada ou excluída, e nenhuma tela DEVE oferecer exclusão.
- **FR-7405**: Registrar DEVE exigir, todos preenchidos: o número e a data do ato do Conselho Superior
  (P-0); a identificação e a data do protocolo da CPVA (P-0); o roteiro (P-8); a regra do menor de
  idade (P-7); o prazo de guarda do arquivo de vídeo, em dias, contado do encerramento do Edital
  (P-10); ao menos uma unidade alcançada; e o motivo. A recusa DEVE nomear cada valor que falta, e nada
  DEVE se gravar.
- **FR-7406**: A data do ato e a do protocolo NÃO DEVEM ser futuras, e o prazo de guarda DEVE ser um
  inteiro positivo. A recusa DEVE nomear o campo.
- **FR-7407**: O roteiro e a regra do menor DEVEM ser escolhidos **só** entre os que o sistema
  implementa: hoje, o roteiro de referência da `166` e a regra "indisponível para quem declara ter menos
  de 18 anos" (a FR-7109 da `166`). A tela DEVE mostrar os passos de cada roteiro e o texto de cada
  regra, e DEVE dizer que, se o protocolo aprovou outro roteiro ou outra regra, a habilitação espera
  spec nova.
- **FR-7408**: DEVE existir no máximo **uma** base vigente. Registrar com uma vigente DEVE ser recusado,
  dizendo que se altera ou se revoga a vigente; alterar e revogar DEVEM exigir uma vigente; revogar a
  revogada DEVE ser recusado sem gravar.
- **FR-7409**: Alterar DEVE partir dos valores vigentes, exigir motivo e gravar a versão nova com todos
  os valores. A alteração sem nenhuma mudança DEVE ser recusada sem gravar.
- **FR-7410**: Nenhum valor de nenhum campo DEVE vir preenchido ou pré-selecionado ao registrar, nem
  quando há uma opção só. Nenhum caminho do sistema — migration, semente, comando de implantação ou
  `seed_demo` — DEVE criar base fora da suíte; a suíte DEVE usar valores marcados como fictícios.
- **FR-7411**: Registrar e alterar DEVEM exigir a capacidade ligada. Sem ela, a tela DEVE dizer que o
  servidor não oferece o vídeo e NÃO DEVE oferecer esses atos. Revogar DEVE ser oferecido sempre que
  houver base vigente, com ou sem capacidade. O histórico DEVE ser legível sempre.
- **FR-7412**: Atos concorrentes sobre a base DEVEM ser serializados: a confirmação DEVE reconferir,
  sob trava, o estado em que a tela se baseou, e recusar se ele mudou.

#### Quem pode

- **FR-7413**: A permissão nova `verificacao-por-video:habilitar` DEVE pertencer ao papel institucional
  que já existe, o Administrador institucional, e só a ele. Nenhum papel, tela de designação ou
  mecanismo de concessão novo DEVE ser criado. A permissão NÃO DEVE conferir nenhuma outra capacidade.
  Antes do deploy, todo vínculo vigente desse papel DEVE ser identificado, e a ampliação NÃO DEVE chegar
  a quem o tem sem autorização expressa do usuário, como na FR-3310 da `110`.
- **FR-7414**: Todo ato e toda leitura da base pela tela DEVEM exigir a permissão com o escopo
  institucional ativo, conferidos na camada de aplicação. Ator com escopo de unidade, com qualquer
  papel, DEVE receber a recusa; a sessão de demonstração DEVE receber a recusa antes de qualquer
  leitura, como na FR-3312 da `110`.
- **FR-7415**: A tela DEVE ficar na administração institucional que já existe, ao lado de Unidades e de
  Acessos, com o item da barra pela capacidade do ator. Ela NÃO DEVE editar nenhuma outra configuração.

#### Trilha

- **FR-7416**: Cada ato DEVE registrar quem o praticou, quando, o motivo e o antes e o depois de cada
  valor, na mesma transação do ato: sem evento, nada muda. A tela DEVE mostrar o histórico, mais
  recente primeiro.
- **FR-7417**: O evento de cada ato DEVE ser legível pelo auditor de cada unidade que o ato alcança ou
  deixa de alcançar, pelo mecanismo de trilha que a `110` usa.
#### O Edital cita a base

- **FR-7418**: A publicação e a Retificação que **acrescenta** a admissão do vídeo a uma Etapa (a
  FR-7102 da `166`, sem mudança no que é a admissão) DEVEM exigir a capacidade ligada **e** uma base
  vigente que alcance a unidade do Edital. A recusa DEVE nomear o que falta: o servidor não oferece o
  vídeo; nenhuma base registrada; a base foi revogada em tal data; a base não alcança tal unidade. As
  demais recusas da FR-7103 da `166` continuam.
- **FR-7419**: A publicação DEVE gravar, no conteúdo publicado de cada Etapa que admite o vídeo, a
  **citação** da versão vigente da base: o número e a data do ato do Conselho Superior, a identificação
  e a data do protocolo da CPVA, a versão do roteiro e a regra do menor. A citação é conteúdo normativo,
  imutável com a publicação. Um Edital publicado sem citação DEVE ser lido como "sem habilitação".
- **FR-7420**: O documento do Edital DEVE citar o ato e o protocolo na descrição da Etapa que admite o
  vídeo, junto da frase da FR-7106 da `166`, derivados da citação publicada.
- **FR-7421**: Quem elabora NÃO DEVE digitar a citação: ela DEVE derivar da base vigente no momento da
  publicação, e a Revisão DEVE mostrá-la e dizer de onde vem antes da confirmação. Se a base mudar entre
  a Revisão e a confirmação, a publicação DEVE ser recusada e a Revisão, refeita.
- **FR-7422**: O campo "Admite vídeo" da composição DEVE estar habilitado só com a capacidade ligada e
  uma base vigente que alcance a unidade do Edital; fora disso, desabilitado, com a razão da FR-7418.
- **FR-7423**: A citação de uma Etapa DEVE se fixar na publicação que primeiro a fez admitir o vídeo. A
  Retificação NÃO DEVE trocá-la; a Etapa que passa a admitir o vídeo numa Retificação cita a versão
  vigente naquele momento.

#### Uma resposta só para "habilitado"

- **FR-7424**: O vídeo DEVE estar habilitado para uma Etapa de um Edital se, e só se: a capacidade está
  ligada; o conteúdo vigente do Edital diz que a Etapa admite o vídeo e tem a citação; nenhuma revogação
  foi registrada depois da versão citada, ainda que uma base nova tenha vindo depois dela; e a versão
  vigente da base ainda alcança a unidade do Edital. Essa resposta DEVE ter um
  ponto só no sistema, e todo ponto que na `166` lê a chave — a página e as rotas do portal, a situação
  do titular, a composição, a publicação e a Retificação — DEVE consultá-lo. Um teste guardião DEVE
  recusar leitura direta da capacidade fora dele.
- **FR-7425**: A Mesa DEVE continuar como na `166`: os vídeos recebidos são abertos, assistidos e
  deliberados com ou sem habilitação, e a regra de que o vídeo só confirma continua valendo.

#### Os parâmetros, lidos da citação e da base

- **FR-7426**: O roteiro exibido ao candidato e conferido no envio DEVE ser a versão que a Etapa cita. O
  envio com outra versão DEVE ser recusado, como na FR-7112 e na FR-7113 da `166`.
- **FR-7427**: A regra do menor aplicada ao candidato DEVE ser a que a Etapa cita.
- **FR-7428**: A página de acolhimento do vídeo DEVE dizer ao candidato por quanto tempo o arquivo é
  guardado e contado de quando, a partir do prazo da FR-7429.
- **FR-7429**: O comando de eliminação da `166` DEVE ler o prazo da **versão mais recente** da base que
  a Etapa cita, revogada ou não (Q-2), e registrar com a eliminação a versão de onde o prazo veio. Sem
  base citada, DEVE recusar, como a FR-7146 da `166` recusa sem prazo.

#### A revogação, e a alteração que restringe

- **FR-7430**: Revogar DEVE exigir motivo e confirmação.
- **FR-7431**: A partir da requisição seguinte à revogação, ou à retirada de uma unidade do alcance, o
  portal DEVE deixar de oferecer o vídeo nos Editais afetados: o detalhe da inscrição DEVE dizer que a
  gravação não está mais disponível e que a entrevista ao vivo continua o caminho do candidato, e as
  rotas de envio DEVEM recusar parte e conclusão, inclusive na tolerância de uma hora da FR-7126 da
  `166`. O envio em andamento NÃO DEVE produzir vídeo.
- **FR-7432**: A confirmação de alterar e de revogar DEVE mostrar o alcance antes do ato: os Editais
  que citam a base, e, para cada um, se o portal vai fechar, quantos vídeos recebidos e quantos envios
  em andamento ele tem, e se o período da Etapa está aberto. A de alterar DEVE mostrar o antes e o
  depois.
- **FR-7433**: A revogação NÃO DEVE eliminar arquivo, nem alterar vídeo, abertura, parecer,
  encaminhamento ou Resultado, nem impedir a eliminação pelo prazo.

#### A porta do piloto

- **FR-7434**: A documentação da porta do piloto DEVE ser reescrita: o ato do Conselho Superior, o
  protocolo da CPVA e a matriz de navegadores com câmera real (o SC-2377 da `166`) continuam antes de
  tudo; a capacidade é ligada pela TI; a base é registrada pelo Administrador institucional; o Edital a
  cita. O passo do PR revisado DEVE sair.
- **FR-7435**: Esta spec NÃO DEVE registrar base, nem marcar P-0, P-7, P-8 ou P-10 como resolvidas.

### Requisitos de experiência

- **UX-800**: A tela da base é uma página só, no desenho da ficha de Unidades: a situação no alto —
  "Vigente desde …", "Revogada em …", "Nunca registrada" ou "O servidor não oferece a verificação por
  vídeo" —, os valores vigentes, as ações possíveis e o histórico.
- **UX-801**: Cada campo é rotulado pelo documento de onde vem — "Ato do Conselho Superior", "Protocolo
  da CPVA" —, e o prazo de guarda mostra, ao lado do número, "dias, contados do encerramento do Edital".
- **UX-802**: Na composição, a razão do campo desabilitado diz o que falta e quem resolve: "Quem opera
  o servidor" para a capacidade, "o Administrador institucional" para a base.
- **UX-803**: A mensagem ao candidato depois da revogação não fala em revogação nem em norma: diz que a
  gravação não está mais disponível neste Edital e que a entrevista ao vivo continua sendo o caminho
  dele, no tom da `166`.

### Key Entities

- **Capacidade do vídeo** (configuração, não dado): a variável de ambiente que diz que o servidor pode
  oferecer o vídeo.
- **Base normativa do vídeo** (nova): o registro institucional, append-only, em versões. Cada versão
  tem o ato do Conselho Superior (número, data), o protocolo da CPVA (identificação, data), o roteiro, a
  regra do menor, o prazo de guarda, as unidades alcançadas, a situação (vigente ou revogada), o autor,
  o instante e o motivo.
- **Citação da base** (nova, no conteúdo publicado): na Etapa que admite o vídeo, a versão da base que
  ela cita e os valores que o documento imprime.
- **Admissão do vídeo na Etapa** (existe, `166`): sem mudança no que é.
- **Papel institucional** (existe, `106`, `110`): o Administrador institucional ganha a permissão
  `verificacao-por-video:habilitar`.
- **Evento da trilha** (existe): o ato, com a pessoa, a permissão, o motivo e o antes e o depois.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2430**: Com a capacidade desligada, ou sem base vigente que alcance a unidade, o número de Etapas
  publicadas ou retificadas admitindo o vídeo é zero, em todos os caminhos testados.
- **SC-2431**: Em todas as combinações de valor faltando ou inválido, o número de bases gravadas é zero,
  e cada recusa nomeia o campo.
- **SC-2432**: Depois de uma revogação, 100% dos Editais que citam a base recusam envio na requisição
  seguinte, e 0 vídeos recebidos perdem a Mesa ou o arquivo.
- **SC-2433**: A varredura do código acha zero leituras da capacidade fora do ponto único.
- **SC-2434**: Ator sem a permissão, com escopo de unidade, ou na sessão de demonstração recebe zero
  bytes da tela e grava zero eventos, em todas as rotas.
- **SC-2435**: Depois de alterar a base, o documento, o roteiro e a regra do menor de 100% dos Editais
  publicados antes continuam os da versão citada.
- **SC-2436**: A produção sobe com a capacidade ligada e coerente, e recusa cada combinação incoerente,
  o nome antigo e a variável do prazo, nomeando a variável.
- **SC-2437**: Uma pessoa da TI e uma Administradora institucional, seguindo só a porta do piloto
  reescrita, ligam a capacidade e registram uma base fictícia num ambiente de homologação, sem ler
  código nem abrir PR. *(Humano; fora da suíte.)*

## Assumptions

- O prazo de guarda se registra em dias, como a `166` já conta, contado do encerramento do Edital, que é
  o único fim de certame que o sistema registra. Se a P-10 vier em anos ou com outro marco, a conversão
  e o marco se decidem quando ela vier.
- O armazenamento privado dos arquivos dos candidatos já é exigido pela produção; a capacidade não pede
  outro.
- A base nova e a citação são dado append-only e conteúdo publicado: as tabelas novas entram na conta
  das append-only, e a citação, no degrau seguinte do conteúdo publicado. O plano decide como.
- Os vídeos da suíte e da verificação no navegador continuam sintéticos, como na `166`.

## Out of Scope

- Qualquer valor de P-0, P-7, P-8 ou P-10.
- Roteiro editável, roteiro por unidade e regra do menor diferente da implementada.
- Painel de configurações, edição de outra configuração pela interface, guarda de segredo no banco.
- O assistente de IA (`170`), a orientação (`168`) e o agendamento (`167`).
- O aviso automático aos candidatos na revogação (Q-3).

## Dependências

- **`166`**, mergeada (#547). Esta spec revê parte dela, como registrado acima.
- **`110`** e **`107`**, mergeadas: o Administrador institucional, a administração institucional e a
  trilha da unidade.
- **P-0, P-7, P-8 e P-10**, abertas e da instituição. Esta spec cria o lugar delas; sem elas, o vídeo
  continua desligado em todo ambiente que não seja o da suíte.
- **O SC-2377 da `166`** (a matriz de navegadores com câmera real), aberto, que a porta do piloto
  continua exigindo antes do registro.

## Perguntas ao usuário

Cada pergunta tem uma recomendação, adotada como comportamento enquanto não houver resposta.

### Q-1 — Uma base institucional com unidades alcançadas, ou uma base por unidade?

O ato do Conselho Superior é do Ifes inteiro; o protocolo da CPVA pode valer para um campus piloto.
**Recomendação: uma base institucional só, com a lista das unidades alcançadas**, registrada pelo
Administrador institucional. Uma base por unidade pediria quem a registre na unidade — papel que não
existe —, e deixaria a unidade autorizar a si mesma, contra o negar por padrão. A lista resolve o piloto
num campus e a expansão depois.

### Q-2 — O prazo de guarda é o da versão que o Edital citou, ou o da mais recente?

O roteiro e a regra do menor são regra do certame, e ficam na versão citada (FR-7426, FR-7427). O prazo
de guarda é governança do dado, e não regra do certame. **Recomendação: o da versão mais recente**
(FR-7429): quando o arquivo institucional muda a guarda, ela vale para o que está guardado. A confirmação
da alteração mostra os Editais afetados (FR-7432). A alternativa — a versão citada — impede mudar a guarda
de vídeos já recebidos.

### Q-3 — A revogação depois do primeiro vídeo: como os candidatos ficam sabendo?

A revogação fecha o portal (FR-7431), mas o Edital publicado continua dizendo que o candidato pode
escolher, e a Retificação que retira a admissão depois do primeiro vídeo é recusada (a FR-7105 da
`166`). **Recomendação: manter a recusa da Retificação e comunicar pelo aviso aos candidatos da `066`**,
que a confirmação da revogação lembra a gestão de enviar. Ninguém perde direito: o Edital já garante a
entrevista ao vivo, que vale igual. O aviso automático fica fora.

### Q-4 — A base precisa nomear os Editais do piloto?

A porta do piloto da `166` previa liberar o vídeo "para aquele Edital, e não para todos". **Recomendação:
não.** O Edital que cita a base é o recorte por Edital, e as unidades alcançadas, o por campus. Nomear
Editais na base faria o Administrador institucional autorizar rascunho por rascunho, um segundo ato sobre
o Edital que nenhuma norma pede.

## Decisões

### D-001 — A variável muda de nome e de sentido

`VERIFICACAO_POR_VIDEO=true` num ambiente de produção seria lido como "o vídeo está ligado", que é
justamente o que deixa de ser verdade. Nenhum ambiente instalado a usa, porque a produção a recusava;
renomear custa só a suíte, o desenvolvimento e a documentação. O nome antigo recusa a subida, para não
desligar o vídeo em silêncio (FR-7400).

### D-002 — A produção recusa a combinação incoerente, e não a capacidade

A recusa da `166` guardava uma decisão institucional no código. A que fica guarda só o que é da TI: o
teto do vídeo, e os nomes que deixaram de existir (FR-7401).

### D-003 — A base é registro institucional append-only, com uma vigente

Registrar, alterar e revogar gravam versões; nada se edita nem se exclui, como a Constituição exige da
auditoria. Uma vigente por vez, porque duas bases simultâneas pediriam regra de qual vale (FR-7404,
FR-7408).

### D-004 — A habilitação por Edital é conteúdo normativo, e não ato operacional

O direito do candidato de escolher o vídeo é regra do certame, e regra do certame tem uma fonte só: o
Edital publicado. Por isso a habilitação por Edital é a admissão que a `166` já publica, mais a citação
da base, publicadas juntas e imutáveis. Um ato operacional sobre o Edital publicado mudaria a regra sem
Retificação (FR-7418, FR-7419).

### D-005 — Os parâmetros só têm os valores que o sistema implementa, sem pré-seleção

Um campo livre para o roteiro registraria o que o sistema não faz; um valor pré-selecionado seria o
sistema decidindo pela instituição (FR-7407, FR-7410).

### D-006 — A citação se fixa na publicação, e a Retificação não a troca

A norma de um ato é a que ele citou. O Edital em curso continua com a versão que publicou, e a mudança
da base alcança os Editais seguintes (FR-7423).

### D-007 — A revogação fecha o portal, e não a Mesa

É a regra que a `166` já tem para a chave desligada: o vídeo recebido sob base válida continua sendo
analisado, pela regra de que só confirma, e o arquivo segue o prazo. Coletar vídeo novo depois de
revogada a base não teria fundamento (FR-7425, FR-7431, FR-7433).

### D-008 — Uma resposta só para "habilitado", com guardião

A `166` lê a chave em sete pontos. Com quatro condições no lugar de uma, um ponto esquecido abriria o
vídeo sem base. Um ponto só, e um teste que recusa os outros (FR-7424).

### D-009 — A permissão nova vai no papel institucional que existe

Como o registro de Unidades na `110`: não há exigência institucional de separar quem cadastra unidade de
quem registra a base, e um papel novo pediria um mecanismo de designação novo (FR-7413).

### D-010 — O prazo de guarda sai do ambiente

Com o prazo na base, a variável seria uma segunda fonte. Ela deixa de existir, e definida recusa a
subida (FR-7402, FR-7429).
