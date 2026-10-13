# Feature Specification: Avisos complementares aos candidatos, vinculados a ato oficial

**Feature Branch**: `claude/066-avisos-complementares`

**Created**: 2026-10-09

**Status**: Draft

**Input**: a demanda do setor responsável pelos processos seletivos, de 09/10/2026 — *"Toda a
convocação/publicação de resultado que publicarmos na página do PS o sistema poderia permitir que
fizéssemos notificação para os candidatos. Seja convocação de PPI, para entrevista de títulos,
chamada de suplentes, etc. O texto da notificação seria feito pela seleção. Se possível que o
sistema permita salvar os modelos de texto."* —, a auditoria
`doc/auditoria-notificacoes-aos-candidatos-2026-10-09.md` e, nela, a tabela **"Decisões do usuário,
de 09/10/2026"**, que prevalece sobre o restante do relatório. A norma que a admite é a `FR-084` da
`010`, revisada na mesma data, com as redações anteriores preservadas.

> **Faixa de identificadores.** Abre em **FR-1241**, **SC-481** e **UX-171**. O teto medido em
> 09/10/2026 em todas as worktrees era o da `065-conflitos-de-numeracao`, ainda em PR aberto (mil
> duzentos e vinte para os requisitos funcionais, quatrocentos e setenta para os critérios de
> sucesso, cento e sessenta e um para a experiência). A folga existe porque a `065` ainda pode
> crescer na revisão. As decisões desta spec nascem em `D-001`; as do usuário são **entrada** e
> aparecem como "decisões recebidas".

**A frase que governa:**

> O aviso aponta para um ato que já existe. Ele não é o ato, não muda o ato e não decide quem o ato
> alcançou.

---

## Por que esta feature existe

A seleção publica resultados e chamadas, e o candidato só fica sabendo se for ao portal. Os
Editais já põem nele a responsabilidade de acompanhar — o 57 (11.4) manda "acompanhar a publicação
dos resultados das fases" e "acompanhar seu e-mail"; o 90 (11.6), "acompanhar as publicações na
página do Cefor". O setor pediu um meio de avisar, com texto próprio e modelos reutilizáveis.

O sistema já tem o que torna isso seguro, e não tinha o canal:

- **A lista exata de quem cada ato alcançou.** O resultado publicado guarda, congelada, uma linha
  por inscrição considerada (`SituacaoDivulgada`, `017`), inclusive quem ficou sem posição. A chamada
  guarda cada inscrição convocada (`Convocacao`, `019`).
- **Um envio de e-mail que já foi feito com cuidado.** A comunicação da convocação reserva a chave
  antes de enviar, envia fora da transação, conta o retorno do servidor de correio e diz "enviada em",
  nunca "recebida em" (`019`, `FR-288a`).
- **O endereço provado.** A credencial verificada pelo código de acesso vem antes do endereço que a
  inscrição guardou (`010`).

O que faltava era norma — a `FR-084` da `010` excluía "aviso de resultado e de retificação", e a
`017` excluía "comunicação ativa" — e um envio que aguente centenas de pessoas sem prender a tela de
quem opera. O sistema não tem fila nem worker (`doc/implantacao-em-producao-ubuntu.md`, §2), e o
envio de hoje acontece dentro da requisição, sem timeout.

---

## Decisões recebidas (09/10/2026)

Tomadas pelo usuário ao revisar a auditoria. Não se reabrem aqui.

1. **Norma.** A `FR-084` da `010` e a exclusão da `017` são revisadas para admitir uma quarta
   situação, estritamente o **aviso complementar vinculado a ato oficial**, sem efeito sobre prazos,
   classificação, situação da inscrição ou direitos. O histórico das redações é preservado.
2. **Quem envia.** Capacidade própria, `aviso:enviar`, concedida de início ao papel publicador, ao
   papel gestor e à presidência da comissão, no escopo institucional e pelas regras de autorização
   existentes. Enviar aviso **não** autoriza publicar resultado nem praticar ato administrativo.
3. **Destinatários.** Exclusivamente os que o ato identifica. No resultado, todas as inscrições
   consideradas, inclusive as sem posição. **Nem acréscimo nem exclusão manual.** Os casos sem
   endereço são registrados à parte. Quem aparece em várias listas do mesmo marco recebe um aviso só.
4. **Modelos.** Por unidade, para criar, editar, reutilizar e inativar. O texto continua editável
   antes de cada envio, só com variáveis controladas. Há um rodapé institucional obrigatório, que
   esclarece o caráter complementar.
5. **Conteúdo.** Assunto neutro, sobretudo em procedimento ligado a reserva de vagas. Nem
   classificação, nem resultado individual, nem motivo de eliminação, nem outro dado potencialmente
   sensível no corpo.
6. **Envio.** Fora da requisição, com o banco e o systemd, sem Celery nem RabbitMQ. A spec define
   idempotência, recuperação de falha, concorrência, interrupção, timeout, limite de envio e
   tentativa de resultado indeterminado. Falha depois da aceitação pelo servidor e antes do registro
   **não pode** gerar reenvio automático. Mensagem aceita pelo servidor não é mensagem entregue.
7. **Retificação.** Permite um aviso novo, que se declara sobre publicação retificadora, sem
   afirmar que a situação individual mudou e sem reenviar a todos automaticamente.
8. **Escopo.** O MVP cobre o resultado preliminar e o definitivo, a retificação de resultado e a
   chamada de titulares e suplentes comunicada por publicação.
9. **Fora, e registrado.** A convocação para heteroidentificação (PPI), a entrevista e a avaliação de
   títulos ficam como capacidade futura, ligada à evolução dos atos respectivos
   (`doc/registro-convocacao-para-etapas-2026-10-09.md`). **Este MVP não encerra a demanda do
   setor.** Agendamento fica fora.
10. **LGPD.** A validação institucional fica registrada como pendente, e é exigida antes da entrada
    em produção.

---

## O que o domínio já fornece, ato por ato

| Origem do aviso | Ato que o fundamenta | De onde saem os destinatários | Situação |
|---|---|---|---|
| Resultado preliminar ou definitivo | `PublicacaoResultado` vigente (`017`) | `SituacaoDivulgada` da publicação, uma por inscrição considerada | **determinístico e congelado** |
| Retificação de resultado | `PublicacaoResultado` que sucede outra (`publicacao_anterior`) | `SituacaoDivulgada` da sucessora | **determinístico e congelado** |
| Chamada comunicada por publicação | `Convocacao` com `ComunicacaoEmitida` na forma `PUBLICATION`, `ENVIADA`, com referência declarada (`019`) | universo: as convocações daquela referência no recorte; envio: as que seguem em curso (`D-003`) | **determinístico** |
| Chamada comunicada por mensagem individual | a própria `ComunicacaoEmitida` **é** o ato, e o prazo corre dela | — | **fora**: a mensagem formal já existe (`D-001`) |
| Convocação para heteroidentificação, entrevista ou avaliação de títulos | nenhum ato no sistema | — | **lacuna**, registrada |

---

## Decisões desta spec

Propostas em 09/10/2026 e revistas pelo usuário no mesmo dia. `D-001`, `D-002`, `D-004` e `D-005`
foram aprovadas como estavam. `D-006` foi aprovada com dois acréscimos. `D-003`, `D-007` e `D-008`
foram reescritas pela revisão da spec. `D-009` nasceu da revisão do plano. O texto abaixo já é o
revisto.

#### D-001 — Aviso não é comunicação, e não convive com a mensagem individual

Aviso e comunicação da convocação ficam separados em registro, tela, vocabulário e permissão. A
comunicação da convocação é ato com efeito: quando o Edital comunica por mensagem individual, o
prazo corre do envio (`019`, `FR-269a`). O aviso não tem efeito nenhum.

No Perfil que declarou mensagem individual, a chamada **não** oferece aviso. A pessoa já recebeu a
mensagem que conta, e um segundo e-mail sobre a mesma chamada a faria perguntar qual dos dois vale.

#### D-002 — O aviso de resultado é por marco e natureza, sobre as publicações ainda não avisadas

Publicar o resultado de um marco produz uma publicação por lista. O aviso reúne as publicações
**vigentes** do marco **com a mesma natureza** (preliminar ou definitiva) **que nenhum aviso anterior
citou**, e deduplica por inscrição.

A regra faz três coisas de uma vez:

- **Na primeira vez**, o aviso cobre todas as listas, e quem concorre na ampla e numa reserva recebe
  um só.
- **Depois de uma retificação**, só a publicação sucessora é nova, e o aviso alcança quem ela
  considerou. Ninguém escolhe quem foi "afetado" pela retificação: é a lista do ato retificador.
- **A lista publicada depois das outras** gera aviso próprio, sem que as já avisadas entrem de novo.

Avisar de novo sobre publicação já avisada é reenvio intencional, e exige justificativa (`FR-1262`).

#### D-003 — Na chamada, o universo do ato é histórico, e a elegibilidade para o aviso é atual

*Reescrita na revisão de 09/10/2026: "não misturar a composição do ato com a elegibilidade atual
para receber um aviso".*

Na convocação por publicação, a equipe declara onde publicou, e o sistema grava essa referência em
cada comunicação (`019`). São duas coisas, e a spec as mantém separadas:

- **O universo do ato** é **fato histórico**: todas as convocações do recorte cuja comunicação por
  publicação, enviada, traz **a mesma referência**. Desfecho, sucessão ou vencimento posteriores não
  o mudam. O aviso registra cada uma delas como destinatário do universo, e a lista original
  continua rastreável no aviso.
- **A elegibilidade para receber o aviso** é **situação operacional de agora**. Só recebe a mensagem
  a convocação que **segue em curso**: vigente, sem desfecho e com vencimento não decorrido. As
  demais ficam no aviso marcadas **"não elegível para o aviso"**, com o estado atual que as tornou
  inelegíveis — desfecho registrado, sucedida ou vencimento decorrido.

A inelegibilidade é **restrição operacional**, e não reinterpretação do ato. Ela existe porque
dizer "você está entre as convocadas" a quem já desistiu, ou a quem o prazo já passou, induziria a
pessoa a crer que a convocação encerrada continua válida. A tela mostra as duas listas, com os
motivos, para que a equipe decida com o estado atual à vista. O operador não escolhe nenhum dos dois
conjuntos.

No resultado, o universo também é histórico, porque a publicação o congelou, e nele todas as
inscrições consideradas são elegíveis. Nenhum estado posterior de uma inscrição torna enganoso
avisar que um resultado foi publicado.

#### D-004 — A autorização depende da origem

- **Resultado:** quem tem `aviso:enviar` (os papéis publicador e gestor) ou a presidência ativa da
  comissão do Processo.
- **Chamada:** só quem tem base de gestão da comissão daquele Processo, que é a mesma porta da
  comunicação da convocação hoje (`019`). O papel publicador sozinho não basta. A convocação é ato da
  comissão, e avisar sobre ela sem a base de quem conduz inverteria a regra que já existe.
- **Modelos:** criar, editar e inativar exigem `aviso:enviar` **por papel**. A presidência usa os
  modelos e edita o texto antes do envio, mas não gere o acervo da unidade, que é transversal aos
  Processos.
- **Histórico:** quem pode enviar e quem tem `auditoria:consultar`.

#### D-005 — A tentativa é registrada antes de o servidor ser chamado, e o indeterminado nunca se reenvia sozinho

Cada destinatário passa por estados derivados de registros append-only, nunca de coluna alterada:

| Estado | Quando |
|---|---|
| **Pendente** | sem tentativa ainda |
| **Em envio** | a tentativa foi registrada há pouco, e o resultado ainda não |
| **Aceita pelo servidor** | o servidor de correio aceitou a mensagem |
| **Falha temporária** | o servidor **respondeu** a um comando da mensagem que não a aceitava agora (4xx); elegível a nova tentativa automática |
| **Falha definitiva** | o servidor **respondeu** que não a aceita (5xx), ou o limite de tentativas se esgotou |
| **Sem endereço** | não há endereço de destino |
| **Indeterminada** | a tentativa começou e não se sabe se o servidor aceitou: queda do processo, queda da conexão, timeout ou resposta que não se pôde ler, em qualquer ponto depois do início da mensagem |
| **Expirada sem envio** | o aviso passou da janela de despacho sem que a tentativa começasse (`D-009`) |
| **Interrompido antes do envio** | o aviso foi interrompido antes de a tentativa começar (`D-006`) |
| **Não elegível** | na chamada, a convocação não segue em curso (`D-003`); nunca recebe mensagem |

Registrar a tentativa **antes** de chamar o servidor, numa gravação própria e já confirmada, é o que
torna a queda do processo observável. Uma tentativa sem resultado é, por definição, indeterminada,
e o despacho nunca a repete. Só uma pessoa a reenvia, com justificativa. É a regra que a
comunicação da convocação já segue (`emissao_em_estado_indeterminado`), estendida ao lote.

#### D-006 — O envio confirmado pode ser interrompido

Até o último destinatário sair, quem enviou (ou quem tem a mesma porta) pode **interromper** o
aviso. Os pendentes não saem mais; as aceitas continuam aceitas, e a interrupção é registrada com
autor e motivo. É a defesa contra o engano que o usuário nomeou, "centenas de candidatos por
engano", no único momento em que ela ainda funciona: os primeiros minutos.

*Acréscimos da revisão de 09/10/2026:*

- **A interrupção é conferida antes de cada tentativa**, e não só no início de cada execução do
  despacho, inclusive com execuções concorrentes. Um despacho que lesse o aviso uma vez e enviasse o
  lote inteiro faria a interrupção valer só para o lote seguinte.
- **A tela diz que mensagem aceita pelo servidor não volta.** Interromper para o que falta, e não
  recolhe o que já saiu.

#### D-007 — Assunto neutro por construção, e não por varredura de texto

*Reescrita na revisão de 09/10/2026, que recusou o bloqueio por ocorrência textual do nome de
modalidade ou de lista: ele produziria falso positivo, e não garantiria proteção.*

A neutralidade vem de três coisas que não dependem de analisar o texto:

1. **Os modelos iniciais trazem assunto neutro**: *"Processo Seletivo Ifes — Nova publicação
   disponível"* (`D-008`).
2. **Nenhuma variável expõe modalidade, lista, posição, resultado ou motivo** (`FR-1255`). O dado
   sensível só entra se alguém o digitar.
3. **O editor mostra, junto do assunto, uma orientação fixa**: o assunto aparece na notificação do
   celular e na lista da caixa de entrada, e não deve nomear modalidade, lista ou procedimento de
   reserva de vagas.

O que a seleção escreve, ela revisa na prévia. O sistema não varre o texto em busca de termos
sensíveis.

#### D-008 — Três modelos iniciais, editáveis, criados uma vez

*Reescrita na revisão de 09/10/2026: o setor pediu modelos, e a experiência inicial precisa ser boa.*

Cada unidade dispõe de três modelos iniciais, baseados nos exemplos da auditoria (seção F):
**Divulgação de resultado**, **Publicação retificadora** e **Nova chamada publicada**. Os três têm o
assunto neutro da `D-007`.

Eles são criados **uma única vez** por unidade e, daí em diante, são modelos como os outros: a
unidade os edita, inativa e reativa. O sistema **não** os recria, **não** os sincroniza e **não** os
atualiza, e **nunca sobrescreve** texto que a unidade personalizou. A criação é idempotente: rodar a
sincronização de novo, ou duas vezes ao mesmo tempo, não cria cópia. Uma correção futura no texto de origem não alcança a unidade que já os tem. Isso é
deliberado: o texto passa a ser da seleção, e não há versionamento de modelo institucional.


#### D-009 — A chave de habilitação, e por que reativá-la não dispara o que ficou para trás

*Aprovada na revisão do plano, de 09/10/2026, com a exigência de que a reativação não produza disparo
inesperado de mensagens antigas.*

A instalação tem uma chave, `AVISOS_AOS_CANDIDATOS`, **desligada em produção** até a validação
institucional de LGPD e da infraestrutura de correio.

- **Desligada**, ninguém confirma aviso novo nem reenvio, e o despacho não inicia tentativa.
- O histórico dos avisos e a gestão dos modelos continuam disponíveis, pelas permissões de sempre.
  Assim a seleção pode preparar os textos antes da ativação.

A reativação não retoma o que ficou para trás porque **todo aviso tem janela de despacho**:
`AVISOS_JANELA_DE_DESPACHO_HORAS`, contada da confirmação, com valor inicial de 24. Destinatário
cuja tentativa não começou dentro da janela fica **expirado sem envio**, e o despacho nunca mais o
alcança. Só um aviso filho o reenvia, confirmado por uma pessoa, com prévia nova.

A mesma regra cobre o timer parado por dias. Sem ela, o despacho que volta mandaria de uma vez um
aviso de resultado já retificado, ou a chamada cujo prazo passou.

**Por que janela, e não registro do instante de ativação**: a chave é configuração do ambiente, e o
banco não vê quando ela muda. Uma tabela de "ativações" exigiria alguém que a gravasse no deploy, e
o esquecimento dela produziria justamente o disparo que se quer evitar.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Avisar que o resultado foi publicado (Priority: P1)

A operadora publica o resultado preliminar da análise documental do Perfil "Técnico em Secretaria
Escolar". O sistema a leva ao histórico de publicações do marco, como já faz, e ali ela encontra
**Avisar candidatos**. A tela mostra quem recebe e de onde veio: as 132 inscrições consideradas nas
duas listas do marco, com uma só mensagem para quem está nas duas. Mostra também quantas têm
endereço e quantas não. Ela escolhe o modelo "Divulgação de resultado", ajusta uma frase, vê a mensagem
como sairá para uma pessoa real da lista e confirma **Enviar a 128 pessoas**. A tela responde na
hora, e o histórico do aviso mostra o envio andando.

**Why this priority**: é o caso mais limpo da demanda, porque o ato já guarda a lista exata. Sozinho,
já entrega o pedido do setor para resultados.

**Independent Test**: publicar um resultado num cenário com duas listas e uma inscrição em ambas,
avisar e conferir que cada inscrição considerada recebeu exatamente uma mensagem, que ninguém fora
do ato recebeu nada, e que o histórico registra aviso, destinatários e tentativas.

**Acceptance Scenarios**:

1. **Given** um marco com publicações vigentes preliminares na ampla e numa reserva, e uma inscrição
   presente nas duas, **When** a operadora confirma o aviso, **Then** essa inscrição recebe uma
   mensagem só, e o total de destinatários é o número de inscrições distintas consideradas.
2. **Given** uma inscrição considerada sem posição (`SEM_POSICAO`), **When** o aviso é enviado,
   **Then** ela está entre os destinatários, e o corpo não diz que ela ficou sem posição.
3. **Given** uma inscrição sem credencial e sem endereço na inscrição, **When** a tela compõe os
   destinatários, **Then** ela aparece contada como "sem endereço", sai do envio e fica registrada
   no aviso com esse estado.
4. **Given** o aviso confirmado, **When** a tela de confirmação responde, **Then** ela não espera o
   envio, e o histórico mostra pendentes, aceitas pelo servidor, falhas e sem endereço.
5. **Given** um marco cuja única publicação vigente já foi avisada, **When** a operadora abre
   "Avisar candidatos", **Then** a tela diz que não há publicação nova a avisar e oferece só o
   reenvio intencional, com justificativa.

---

### User Story 2 — Avisar sobre a publicação retificadora (Priority: P1)

Um recurso foi provido e a lista de pessoas com deficiência foi republicada, sucedendo a anterior.
A operadora abre "Avisar candidatos" no marco. A tela mostra que só a publicação retificadora é nova,
e que os destinatários são as inscrições que **ela** considerou. A mensagem traz, além do texto da
seleção, uma linha fixa dizendo que se trata de publicação que retifica a de 06/10. Essa linha não
afirma que a situação de ninguém mudou.

**Why this priority**: a retificação é o momento em que o candidato mais precisa voltar ao portal.
Ela é também o caso em que um reenvio a todos, ou um texto que diga "sua situação mudou", mais
engana.

**Independent Test**: publicar, avisar, retificar uma lista, avisar de novo e conferir três coisas:
o segundo aviso alcança só quem a sucessora considerou; o primeiro aviso continua intacto; e o link
do primeiro aviso abre a publicação sucedida, que aponta para a vigente.

**Acceptance Scenarios**:

1. **Given** um aviso já enviado sobre as duas listas do marco e a retificação de uma delas,
   **When** a operadora abre "Avisar candidatos", **Then** a publicação nova é só a sucessora, e os
   destinatários propostos são os considerados nela.
2. **Given** o aviso sobre a retificadora, **When** a prévia é exibida, **Then** ela traz a linha fixa
   "esta publicação retifica a de [data]", e nenhum texto do sistema diz que a situação da pessoa
   mudou.
3. **Given** o segundo aviso enviado, **When** se consulta o primeiro, **Then** assunto, corpo,
   destinatários e tentativas dele estão como foram registrados.
4. **Given** a retificação publicada, **When** ninguém aciona o aviso, **Then** nenhuma mensagem sai.

---

### User Story 3 — Avisar os convocados de uma chamada publicada (Priority: P2)

No Perfil que convoca por publicação, a comissão chamou dois suplentes e registrou a comunicação
com a referência "Site do Cefor, 09/10/2026, 2ª chamada". No cartão da convocação aparece **Avisar
os convocados desta publicação**, com a referência e as duas pessoas. A mensagem diz que a chamada
foi publicada e que o prazo corre conforme o Edital, a partir da publicação, e não do aviso.

**Why this priority**: atende o exemplo "chamada de suplentes" do setor, que é o único dos três com
ato no sistema hoje. Depende do fluxo de convocação, que é menos usado que a publicação de resultado.

**Independent Test**: num Perfil `PUBLICATION`, convocar, comunicar com referência e avisar. O aviso
alcança exatamente as convocações vigentes sem desfecho daquela referência. No Perfil
`INDIVIDUAL_MESSAGE`, a ação não aparece e o endpoint recusa.

**Acceptance Scenarios**:

1. **Given** três convocações com a mesma referência, uma delas já com desistência registrada,
   **When** a comissão abre o aviso, **Then** a tela mostra o universo da publicação com as três, e
   a mensagem sai para as duas que seguem em curso. A terceira aparece como "não elegível para o
   aviso: desfecho registrado".
2. **Given** o aviso confirmado nesse cenário, **When** se consulta o histórico dele, **Then** as
   três convocações estão registradas — duas como destinatárias e uma como não elegível, com o
   motivo —, e nenhum registro da convocação foi alterado.
3. **Given** uma referência cujas convocações têm todas o vencimento decorrido, **When** a comissão
   abre o aviso, **Then** o universo é mostrado, a confirmação é recusada por não haver elegível, e a
   tela diz por quê.
4. **Given** um Perfil que convoca por mensagem individual, **When** se tenta avisar sobre a chamada,
   **Then** a ação não é oferecida, e a tentativa direta é recusada com motivo próprio.
5. **Given** quem tem só o papel publicador, sem base de gestão da comissão, **When** tenta avisar
   sobre a chamada, **Then** a resposta é a mesma de quem não pode gerir a comissão.

---

### User Story 4 — Modelos da unidade (Priority: P2)

A coordenação da seleção encontra três modelos prontos na unidade — "Divulgação de resultado",
"Publicação retificadora" e "Nova chamada publicada" — e os adapta ao vocabulário dela. Depois
cadastra outros, usando as variáveis da lista ao lado do campo, e cada modelo salvo passa a aparecer
no seletor de qualquer aviso da unidade. Um modelo antigo é
inativado e sai do seletor sem sumir dos avisos que o usaram. No meio de um envio, ela ajusta o texto
e marca "salvar como novo modelo".

**Why this priority**: o setor pediu "se possível". Sem modelos, o aviso funciona com texto livre.

**Independent Test**: criar, editar e inativar um modelo; usá-lo num aviso; conferir que o aviso
guarda o texto como foi enviado, e não um vínculo que mude com a edição do modelo; conferir que outra
unidade não vê o modelo.

**Acceptance Scenarios**:

1. **Given** uma unidade que nunca teve modelo, **When** a gestão de modelos é aberta pela primeira
   vez, **Then** os três modelos iniciais estão lá, ativos, com o assunto neutro.
2. **Given** a unidade que inativou os três modelos iniciais, **When** o sistema é atualizado ou
   reiniciado, **Then** eles continuam inativos, e nenhum modelo é recriado.
3. **Given** um modelo usado num aviso enviado, **When** o modelo é editado, **Then** o aviso enviado
   continua mostrando o texto original.
4. **Given** um modelo com `{posicao}` no corpo, **When** se tenta salvá-lo, **Then** ele é recusado,
   com a variável desconhecida nomeada.
5. **Given** um modelo inativo, **When** se abre um aviso, **Then** ele não aparece no seletor, e
   continua listado na gestão de modelos como inativo.
6. **Given** um operador de outra unidade, **When** procura o modelo pelo endereço, **Then** a resposta
   é a mesma de modelo inexistente.

---

### User Story 5 — Envio que sobrevive a falha, queda e engano (Priority: P1)

O despacho roda a cada minuto. No meio de um aviso de 300 pessoas, o servidor de correio passa a
recusar conexões por dez minutos; depois, o processo do despacho cai enquanto enviava uma mensagem. A
coordenação percebe no histórico que um aviso foi confirmado com o modelo errado e o interrompe.

**Why this priority**: sem isso, o MVP troca um envio que prende a tela por um envio que pode duplicar
ou sumir mensagem em silêncio. O usuário exigiu esse contrato antes de qualquer outra coisa.

**Independent Test**: com um servidor de correio simulado que falha por um período, que aceita e
derruba a conexão, e com duas execuções simultâneas do despacho, conferir quatro coisas: nenhum
destinatário recebe duas mensagens; as falhas temporárias são retentadas até o limite; a tentativa
interrompida fica indeterminada e não é repetida; e a interrupção impede os pendentes de saírem.

**Acceptance Scenarios**:

1. **Given** duas execuções do despacho ao mesmo tempo, **When** processam o mesmo aviso, **Then**
   nenhum destinatário tem duas tentativas simultâneas.
2. **Given** um servidor de correio inalcançável, **When** o despacho tenta, **Then** a tentativa é
   falha temporária, e o destinatário volta a ser tentado depois de um intervalo, até o limite de
   tentativas.
3. **Given** uma tentativa registrada cujo resultado não chegou a ser gravado, **When** o despacho
   roda de novo, **Then** ela é indeterminada, não é repetida, e a tela a mostra com o caminho do
   reenvio justificado.
4. **Given** um aviso interrompido com 200 pendentes, **When** o despacho roda, **Then** nenhum dos
   200 é tentado, e as aceitas antes da interrupção continuam aceitas.
5. **Given** uma execução do despacho no meio de um aviso, **When** o aviso é interrompido por outra
   requisição, **Then** a execução em curso não inicia nenhuma tentativa depois da interrupção.
6. **Given** a tela de interromper, **When** ela é exibida, **Then** diz quantas mensagens já foram
   aceitas pelo servidor e que elas não podem ser recuperadas.
7. **Given** o limite de envio por minuto configurado, **When** um aviso grande é despachado, **Then**
   o despacho não o excede.
8. **Given** a chave `AVISOS_AOS_CANDIDATOS` desligada, **When** alguém tenta confirmar um aviso,
   **Then** a confirmação é recusada com a explicação, e o despacho não inicia tentativa nenhuma.
9. **Given** um aviso confirmado com a chave ligada, desligada em seguida e religada depois da
   janela de despacho, **When** o despacho roda, **Then** os pendentes ficam expirados sem envio, e
   nenhuma mensagem sai.
10. **Given** um servidor que fecha a conexão depois de receber o conteúdo e antes da resposta final,
    **When** o despacho tenta, **Then** a tentativa é indeterminada, e não é repetida.

---

### Edge Cases

Os casos-limite que têm consequência estão também nos requisitos, porque esta seção não entra na
matriz de rastreabilidade.

- **A publicação é sucedida entre a prévia e a confirmação.** A prévia é assinada pelo conjunto de
  publicações e de destinatários, e a confirmação com assinatura defasada é recusada (`FR-1259`).
- **O mesmo endereço em duas inscrições distintas do aviso.** É possível em inscrições antigas, com
  endereço digitado. Cada inscrição recebe a sua mensagem, com o nome dela: são pessoas, ou fatos,
  distintos (`FR-1249`).
- **Inscrição com credencial e endereço da inscrição diferentes.** Vale a credencial principal, como
  na comunicação da convocação (`FR-1250`).
- **O despacho parado.** O timer pode estar desligado. Um aviso com pendentes há mais tempo que o
  limite configurado mostra o alerta "o despacho não está processando" (`FR-1272`).
- **Processo encerrado ou cancelado.** O aviso é recusado, pela mesma regra que recusa alteração nos
  Editais do Processo (`FR-1244`).
- **Variável sem valor.** Por exemplo `{etapa}` num aviso de chamada. A variável não é oferecida para
  aquela origem, e a prévia a recusa se aparecer (`FR-1256`).
- **Aviso com zero destinatários com endereço, ou nenhum elegível.** A confirmação é recusada: não
  há o que enviar (`FR-1252`).
- **Chave desligada com aviso em curso, e religada dias depois.** Desligada, nada começa. Religada,
  só sai o que ainda estiver dentro da janela de despacho. O resto fica expirado sem envio
  (`FR-1283`).
- **Aviso que cita uma publicação só, e o que cita várias.** O primeiro tem link da publicação. O
  segundo não tem, porque não há URL inequívoca, e usa a página do processo seletivo (`FR-1255`).
- **Interrupção durante uma execução do despacho.** A execução confere a interrupção antes de cada
  tentativa, e para (`FR-1273`).

---

## Requirements *(mandatory)*

### Functional Requirements

**O aviso e o ato**

- **FR-1241**: O sistema DEVE permitir enviar aviso aos candidatos somente a partir de um ato
  existente e vigente de uma destas origens: (a) publicações vigentes de resultado de um marco, com a
  mesma natureza; (b) chamada comunicada por publicação, identificada pela referência declarada na
  comunicação. NÃO DEVE existir aviso sem ato citado.
- **FR-1242**: O aviso NÃO DEVE produzir efeito: não inicia, não suspende nem altera prazo; não
  altera classificação, situação da inscrição, convocação, desfecho nem direito; e NÃO DEVE gravar
  nem alterar `ComunicacaoEmitida` (`D-001`).
- **FR-1243**: Publicar resultado, retificá-lo ou comunicar convocação NÃO DEVE disparar aviso. O
  aviso existe só pelo gesto de uma pessoa autorizada.
- **FR-1244**: O aviso DEVE ser recusado quando o Processo do Edital estiver em estado final, pela
  regra que já recusa alteração nos seus Editais.
- **FR-1245**: No Perfil cujo Edital declara convocação por mensagem individual, o aviso sobre chamada
  NÃO DEVE ser oferecido, e a tentativa direta DEVE ser recusada com código próprio (`D-001`).

**Destinatários**

- **FR-1246**: Os destinatários do aviso de resultado DEVEM ser todas as inscrições consideradas nas
  publicações citadas, inclusive as sem posição, e somente elas.
- **FR-1247**: As publicações citadas por um aviso de resultado DEVEM ser as vigentes do marco, com a
  mesma natureza, que nenhum aviso anterior citou (`D-002`). Havendo publicações não avisadas das
  duas naturezas no mesmo marco, DEVE haver um aviso por natureza, escolhido pelo operador.
- **FR-1248**: Quando alguma publicação citada sucede outra, o aviso DEVE se declarar sobre publicação
  retificadora, com uma linha fixa do sistema que nomeia a data de cada publicação retificada. NENHUM
  texto do sistema DEVE afirmar que a situação individual mudou.
- **FR-1249**: Os destinatários DEVEM ser deduplicados por inscrição dentro de um aviso. Inscrições
  distintas recebem mensagens distintas, ainda que compartilhem endereço.
- **FR-1250**: O endereço de cada destinatário DEVE ser a credencial principal verificada da
  identidade da inscrição e, na falta dela, o endereço gravado na inscrição. É a mesma regra da
  comunicação da convocação, e DEVE ser a mesma implementação.
- **FR-1251**: No aviso de chamada, o **universo** DEVE ser o conjunto histórico de todas as
  convocações do recorte cuja comunicação por publicação enviada traz a referência escolhida,
  independentemente de desfecho, sucessão ou vencimento posteriores. Desse universo, só DEVEM
  receber a mensagem as convocações **elegíveis**: vigentes, sem desfecho e com vencimento não
  decorrido. As demais DEVEM ser registradas no aviso como "não elegível para o aviso", com o
  estado atual que as tornou inelegíveis (`D-003`).
- **FR-1252**: O operador NÃO DEVE poder acrescentar nem excluir destinatário, nem do universo nem
  dos elegíveis. As únicas ausências de envio admitidas são as que o sistema determina, mostra e
  registra por destinatário: a falta de endereço e, na chamada, a inelegibilidade da `FR-1251`.
  Aviso sem nenhum destinatário elegível com endereço DEVE ser recusado.
- **FR-1253**: O universo, a elegibilidade de cada destinatário e o endereço de cada um DEVEM ser
  congelados na confirmação. Retificação, desfecho ou troca de credencial posteriores NÃO DEVEM
  alterar o que o aviso registrou.

**Texto, variáveis e modelos**

- **FR-1254**: O aviso DEVE ter assunto e corpo em texto simples, escritos pela seleção, com no
  máximo 150 caracteres no assunto e 5.000 no corpo.
- **FR-1255**: As únicas variáveis admitidas DEVEM ser: `{nome_do_candidato}`, `{edital}`,
  `{processo_seletivo}`, `{perfil}`, `{etapa}`, `{natureza_do_resultado}`, `{data_da_publicacao}`,
  `{link_da_publicacao}`, `{pagina_do_processo_seletivo}`, `{referencia_da_publicacao}` e
  `{area_do_candidato}`. Só `{nome_do_candidato}` varia por pessoa. NÃO DEVE existir linguagem de
  template, condicional nem laço. As três de destino têm significados distintos, e nenhuma DEVE
  valer o que outra vale:
  - `{link_da_publicacao}`: o endereço público **daquela** publicação oficial. Só existe quando o
    aviso cita **uma** publicação de resultado. Em aviso que cita várias, ou em chamada, ela não
    tem valor.
  - `{pagina_do_processo_seletivo}`: a página pública do Edital, onde as publicações vigentes estão
    listadas. Sempre tem valor.
  - `{referencia_da_publicacao}`: na chamada, a referência que a comunicação declarou, como foi
    escrita. No resultado, não tem valor.
  - `{area_do_candidato}`: a área autenticada, para a situação individual.
- **FR-1255a**: O endereço de uma publicação DEVE ser o endereço permanente dela no portal. Ele
  continua respondendo depois que a publicação é sucedida, e leva à publicação vigente, como o portal
  já faz. Aviso antigo NÃO DEVE ficar com link quebrado nem levar a uma publicação sem dizer que ela
  foi retificada.
- **FR-1256**: Variável desconhecida, ou sem valor para a origem do aviso, DEVE ser recusada ao
  salvar modelo e ao confirmar aviso, com a variável nomeada.
- **FR-1257**: Toda mensagem DEVE terminar com um rodapé institucional fixo, não editável, que: aponta
  a publicação oficial — pelo endereço dela quando houver uma só, pela página do processo seletivo
  quando houver várias, e pela referência declarada na chamada —; diz que ela é a referência para prazos e resultados, conforme o Edital; diz
  que o aviso não a substitui; informa o canal de atendimento; e diz que a mensagem é automática.
  Na chamada, o rodapé DEVE dizer também que o prazo corre conforme o Edital, e não do recebimento do
  aviso.
- **FR-1258**: O editor DEVE mostrar, junto do assunto, uma orientação fixa: o assunto aparece na
  notificação do celular e na lista da caixa de entrada, e não deve nomear modalidade, lista ou
  procedimento de reserva de vagas. O sistema NÃO DEVE varrer o texto em busca de termos sensíveis
  nem bloquear o envio por ocorrência textual (`D-007`).
- **FR-1259**: Antes da confirmação, o sistema DEVE mostrar uma prévia sem gravar nada: o ato citado,
  a origem dos destinatários por extenso, as contagens (com endereço, sem endereço e, na chamada, não
  elegíveis, com o motivo), e a mensagem completa — assunto, corpo e rodapé — preenchida para uma pessoa real
  da lista. A prévia DEVE ser assinada pelo conjunto de publicações e destinatários, e a confirmação
  com assinatura defasada DEVE ser recusada, pedindo nova prévia.
- **FR-1260**: Modelos DEVEM pertencer a uma unidade e ter nome, assunto, corpo e situação (ativo ou
  inativo). DEVEM poder ser criados, editados, inativados e reativados, e NÃO DEVEM ser excluídos. O
  seletor do aviso DEVE mostrar só os ativos da unidade.
- **FR-1260a**: Toda unidade DEVE dispor de três modelos iniciais — "Divulgação de resultado",
  "Publicação retificadora" e "Nova chamada publicada" —, todos com o assunto *"Processo Seletivo
  Ifes — Nova publicação disponível"* e corpo que orienta a consulta da situação na área do
  candidato. Eles DEVEM ser criados uma única vez por unidade, e o sistema NÃO DEVE recriá-los,
  sincronizá-los, atualizá-los nem sobrescrever o texto deles depois, ainda que a unidade os edite
  ou inative (`D-008`). A criação DEVE ser idempotente, inclusive com duas sincronizações
  simultâneas.
- **FR-1261**: O aviso DEVE guardar o assunto e o corpo como foram confirmados, e o modelo de origem,
  quando houver. A edição posterior do modelo NÃO DEVE alterar aviso confirmado. "Salvar como novo
  modelo" DEVE criar um modelo, sem tocar no de origem.

**Duplicidade e reenvio**

- **FR-1262**: Aviso sobre publicação já citada por aviso anterior, ou sobre referência de chamada já
  avisada, DEVE exigir justificativa escrita, gravada no aviso e na trilha. Sem ela, a confirmação
  DEVE ser recusada.
- **FR-1263**: A confirmação DEVE ser idempotente: repetir a mesma confirmação, por duplo clique ou
  reenvio do navegador, DEVE devolver o aviso já criado, sem criar outro.
- **FR-1264**: O reenvio DEVE ser gesto explícito, por aviso filho, e alcançar só os destinatários
  do estado escolhido:
  - **falha definitiva** e **expirada sem envio**: sem justificativa, porque a mensagem não saiu.
    O texto é o do aviso anterior;
  - **indeterminada** e **interrompido antes do envio**: com justificativa. Na indeterminada, a
    mensagem pode ter saído. Na interrompida, alguém decidiu pará-la. O texto pode ser editado, e a
    prévia é nova.

  Um aviso DEVE ter **no máximo um** reenvio de falhas. O estado dos destinatários do aviso anterior
  não muda depois do reenvio, e um segundo mandaria de novo a quem o primeiro já entregou. O que o
  reenvio não entregou se reenvia a partir dele (revisão de código de 09/10/2026).

**Envio**

- **FR-1265**: A confirmação NÃO DEVE enviar mensagem dentro da requisição. Ela DEVE gravar o aviso e
  os destinatários e responder, e o envio DEVE ser feito por um despacho periódico fora da
  requisição, sem dependência nova de fila ou worker.
- **FR-1266**: Antes de chamar o servidor de correio, o despacho DEVE registrar a tentativa numa
  gravação própria e já confirmada. O resultado DEVE ser registrado em outra gravação, depois da
  resposta do servidor (`D-005`).
- **FR-1267**: Tentativa sem resultado registrado DEVE ser tratada como indeterminada, e o despacho
  NUNCA DEVE repeti-la. Qualquer falha de transporte depois do início da mensagem DEVE ser
  registrada como indeterminada, **qualquer que seja o código** que a acompanhe: queda da conexão,
  timeout ou resposta que não se pôde ler. O código só classifica quando é a resposta do servidor a
  um comando da mensagem.
- **FR-1268**: Duas execuções simultâneas do despacho NÃO DEVEM tentar o mesmo destinatário.
- **FR-1269**: A classificação DEVE seguir a fase da conversa com o servidor:
  - **Antes da mensagem** (conexão, TLS, autenticação): falha aqui NÃO DEVE gerar tentativa. Nada
    saiu, e a execução seguinte tenta de novo.
  - **Durante a transação da mensagem** (remetente, destinatário, início do conteúdo e confirmação
    final do conteúdo): uma **resposta explícita** de recusa é falha temporária quando 4xx, e
    definitiva quando 5xx. A temporária é retentada automaticamente após intervalo crescente, até um
    limite de tentativas configurável; esgotado o limite, a falha é definitiva.
  - **Aceitação**: só a resposta positiva à confirmação final do conteúdo é aceitação.
  - Qualquer outra coisa nessa fase é indeterminada (`FR-1267`).
- **FR-1270**: O despacho DEVE respeitar um limite configurável de mensagens por minuto, com valor
  inicial de 60, sujeito à validação da infraestrutura de correio na implantação. Toda conexão ao
  servidor de correio DEVE ter timeout configurado, e o timeout DEVE valer também para os três envios
  que já existem.
- **FR-1271**: Cada mensagem DEVE ter um único destinatário, sem cópia e sem cópia oculta.
- **FR-1272**: O histórico DEVE alertar quando um aviso tiver pendentes há mais tempo que um limite
  configurável, dizendo que o despacho pode não estar processando.
- **FR-1273**: Até o último destinatário sair, o aviso DEVE poder ser interrompido, com motivo, por
  quem tem a porta de enviá-lo. A interrupção DEVE impedir novas tentativas, e NÃO DEVE alterar as
  já registradas (`D-006`). O despacho DEVE conferir a interrupção imediatamente antes de iniciar
  cada tentativa, e não só no início da execução, inclusive com execuções concorrentes.

**Autorização, escopo e registro**

- **FR-1274**: A autorização DEVE seguir a origem (`D-004`). Resultado: capacidade `aviso:enviar`, ou
  presidência ativa da comissão do Processo. Chamada: base de gestão da comissão do Processo.
  Modelos: `aviso:enviar` por papel. Histórico: quem pode enviar, ou `auditoria:consultar`.
- **FR-1275**: A capacidade `aviso:enviar` DEVE ser concedida de início aos papéis publicador e
  gestor, e NÃO DEVE conceder nenhuma outra capacidade. Quem só tem `aviso:enviar` NÃO DEVE poder
  publicar resultado, praticar convocação nem registrar desfecho.
- **FR-1276**: Toda consulta e todo gesto DEVEM filtrar pelo escopo institucional do ator. Aviso,
  modelo ou ato de outra unidade DEVE responder como inexistente.
- **FR-1277**: Aviso, publicações citadas, destinatários, tentativas, resultados de tentativa e
  interrupções DEVEM ser append-only, protegidos por gatilho e por privilégio ausente, como as demais
  tabelas append-only. Modelos são mutáveis, e cada criação, edição, inativação e reativação DEVE ser
  auditada com o estado anterior e o novo.
- **FR-1278**: A trilha DEVE registrar a confirmação (ato citado, origem, contagens, autor, instante),
  o reenvio, a justificativa e a interrupção. Ela NÃO DEVE copiar a lista de endereços, que já está
  no registro do aviso.
- **FR-1279**: O detalhe técnico de falha NÃO DEVE conter endereço nem nome de destinatário.
- **FR-1280**: A regra de contagem das situações de envio (`backend/tests/test_situacoes_de_mensagem.py`)
  DEVE passar a declarar quatro situações, com o módulo remetente do aviso, e a revisão datada da
  `FR-084` da `010` DEVE ser conferida contra o código, como a da `019` já é.
- **FR-1281**: Nenhum teste automatizado DEVE alcançar servidor de correio real. O despacho DEVE
  enviar pelo mecanismo de correio configurado do sistema, e nunca abrir conexão própria que escape
  ao mecanismo que a suíte substitui. Um guardião DEVE falhar se isso mudar.
- **FR-1282**: Com `AVISOS_AOS_CANDIDATOS` desligada, o sistema NÃO DEVE confirmar aviso nem
  reenvio, e o despacho NÃO DEVE iniciar tentativa. A ação de avisar DEVE explicar que o envio está
  desabilitado nesta instalação. O histórico e os modelos DEVEM continuar disponíveis, pelas
  permissões de sempre (`D-009`).
- **FR-1283**: Todo aviso DEVE ter janela de despacho, configurável, com valor inicial de 24 horas
  contadas da confirmação. Destinatário cuja tentativa não começou dentro dela DEVE ficar expirado
  sem envio, e o despacho NÃO DEVE alcançá-lo depois. Isso vale ainda que a chave seja religada ou
  que o despacho volte depois de parado. Só um aviso filho, confirmado com prévia nova, o reenvia.

### Experiência e linguagem

- **UX-171**: A palavra da tela e da mensagem é **aviso**, e nunca "comunicação", "notificação
  oficial" ou "convocação" para o aviso em si. A comunicação da convocação mantém o nome dela.
- **UX-172**: O resultado de cada tentativa DEVE ser dito como "aceita pelo servidor de correio",
  "falha", "sem endereço" ou "resultado indeterminado". NENHUMA superfície DEVE dizer "entregue",
  "recebida" ou "lida".
- **UX-173**: O botão de confirmação DEVE trazer o número de destinatários com endereço ("Enviar a
  128 pessoas"), e a tela DEVE dizer, antes dele, que o envio não se desfaz.
- **UX-174**: "Avisar candidatos" DEVE aparecer no histórico de publicações do marco, ao lado da
  publicação vigente, e no cartão da chamada por publicação. A publicação sucedida NÃO DEVE oferecer
  aviso.
- **UX-175**: Cada publicação e cada chamada DEVE mostrar a linha de estado do último aviso que a citou
  — "Nenhum aviso enviado" ou "Aviso de 09/10, 14:02: 128 aceitas pelo servidor, 4 sem endereço" —,
  com link para o histórico.
- **UX-176**: A lista de variáveis DEVE estar visível ao lado do corpo, com o significado de cada uma.
  O rodapé fixo DEVE estar visível no editor, marcado como não editável.
- **UX-177**: A tela de interromper e o histórico do aviso DEVEM dizer que mensagens já aceitas pelo
  servidor de correio não podem ser recuperadas, e quantas são.
- **UX-178**: No aviso de chamada, a prévia DEVE mostrar o universo da publicação e, separadamente,
  quem recebe e quem não é elegível, com o motivo de cada inelegibilidade.

### Key Entities

- **Modelo de aviso**: texto reutilizável da unidade: nome, assunto, corpo, ativo ou inativo, autoria,
  e a marca de que nasceu como modelo inicial. Mutável e auditado; nunca excluído.
- **Aviso**: um envio decidido por uma pessoa: origem, ato citado, assunto e corpo finais, modelo de
  origem, justificativa de reenvio, aviso anterior relacionado, autor e instante. Append-only.
- **Publicação citada**: cada publicação de resultado que o aviso cita. Append-only.
- **Destinatário**: inscrição do universo do ato citado, com a elegibilidade para o aviso (elegível,
  ou não elegível com o motivo), o endereço congelado ou a marca "sem endereço". Um por inscrição por
  aviso. Append-only.
- **Tentativa e resultado da tentativa**: o início, registrado antes do servidor de correio, e o
  desfecho: aceita, falha temporária, falha definitiva ou indeterminada. Append-only, e o estado do
  destinatário é derivado deles.
- **Interrupção**: o ato de parar um aviso, com autor e motivo. Append-only.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-481**: Em todos os cenários de aceitação, nenhuma mensagem sai para inscrição que o ato citado
  não alcançou, e toda inscrição alcançada com endereço recebe exatamente uma mensagem por aviso.
- **SC-482**: A confirmação de um aviso de 1.000 destinatários responde em menos de 2 segundos,
  porque não espera o envio.
- **SC-483**: Num teste controlado, com servidor de correio simulado e o limite inicial de envio, um
  aviso de 500 destinatários termina de ser despachado em até 15 minutos. Contra o servidor real, o
  tempo depende do limite que a infraestrutura validar.
- **SC-484**: Num teste de queda do despacho no meio de uma tentativa, nenhuma tentativa
  indeterminada é repetida automaticamente, e nenhum destinatário recebe mensagem duplicada por
  execuções simultâneas.
- **SC-485**: Uma operadora que nunca usou a tela compõe e confirma um aviso de resultado a partir de
  um modelo existente em até 3 minutos, no roteiro de demonstração.
- **SC-486**: Nenhuma superfície da feature contém "entregue", "recebida" ou "lida" para descrever um
  envio, conferido por varredura das telas.
- **SC-487**: Operador de uma unidade não consegue ler nem acionar aviso, modelo ou ato de outra:
  100% das tentativas respondem como inexistente.
- **SC-488**: Nenhuma execução da suíte automatizada põe mensagem em servidor de correio real.

---

## Assumptions

- **O canal é só o e-mail.** É o que os Editais nomeiam e o que o sistema já tem.
- **O servidor de correio da instituição aceita o volume.** O limite por minuto e por dia da conta
  de envio precisa ser informado pelo setor de correio, como o runbook já pede para o dia de pico. O
  valor inicial, de 60 por minuto, é parâmetro configurável, e não compromisso operacional.
- **Variáveis vêm de dados já existentes.**
  - `{link_da_publicacao}` é o endereço permanente da publicação no portal
    (`selecoes/resultados/<id>/`), que continua valendo depois da sucessão.
  - `{pagina_do_processo_seletivo}` é a página pública do Edital (`selecoes/<edital_id>/`).
  - O aviso que cobre várias listas não tem link de publicação: um link por pessoa levaria cada
    uma à página da lista dela, e o texto deixaria de ser o mesmo para todos. `{area_do_candidato}` é o
  endereço do portal, **sem token**: a entrada continua por código (P-001 da `010`).
- **O despacho é um comando periódico** num timer do systemd, como os quatro que a implantação já
  tem. É um processo novo em produção, e o plano precisa escrever a necessidade, como o Princípio V
  exige.
- **A equipe é pequena**, de duas ou três pessoas acumulando papéis. A separação entre enviar e
  publicar existe na norma, e na prática a mesma pessoa pode ter as duas.

### Precondição de produção

- **LGPD.** A base legal do uso do e-mail para aviso complementar e a retenção da lista de
  destinatários dependem de validação institucional, com o encarregado de dados, **antes da entrada
  em produção**. A política de retenção já é precondição pendente do piloto (PC-003 da `010`). Esta
  spec não presume a resposta. Se a base legal exigir direito de oposição, o descadastro entra como
  incremento.

---

## Out of Scope

- **Convocação para heteroidentificação, entrevista e avaliação de títulos.** Não há ato no sistema
  de onde tirar os destinatários. Registro em `doc/registro-convocacao-para-etapas-2026-10-09.md`.
- **Aviso de Retificação do Edital** às inscrições enviadas. O universo é amplo, e decidi-lo é
  incremento próprio.
- **Agendamento** de envio.
- **Canais além do e-mail**: SMS, WhatsApp, push.
- **Editor rico, HTML, anexo, linguagem de template, condicional.**
- **Filtro livre de destinatários**, acréscimo ou exclusão manual.
- **Situação individual no corpo** — posição, resultado, motivo de eliminação.
- **Rastreio de abertura ou clique**, processamento de devolução (bounce) e descadastro.
- **Versionamento ou sincronização de modelos**, e modelos compartilhados entre unidades. Os três
  modelos iniciais são criados uma vez e passam a ser da unidade (`D-008`).
- **Envio de teste ao próprio operador.**
- **Aviso visível no portal do candidato.** O portal já mostra situação e convocação.
- **Resíduos do achado do prazo da convocação**, investigado em 09/10 e não confirmado. A regra está
  presa por teste numa alteração isolada (`test_reenvio_nao_reinicia_prazo.py`), e a redação "contado
  do envio desta mensagem" e o "enviada em" que mostra o último envio ficam registrados em
  `doc/achado-reenvio-da-convocacao-sugere-prazo-novo.md`.
