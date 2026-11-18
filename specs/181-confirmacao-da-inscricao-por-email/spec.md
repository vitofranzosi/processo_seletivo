# Feature Specification: A confirmação da inscrição por e-mail diz o que aconteceu, uma vez, e deixa rastro

**Feature Branch**: `claude/gps-auto-confirmation-email-85c434`, nascida da `main` em `31d93c47` (o
merge do #586)

**Created**: 2026-11-18

**Status**: Especificada e implementada. As quatro decisões (D-001 a D-004) foram tomadas nesta spec, a
pedido do usuário, que pediu que as alternativas do comprovante fossem avaliadas e a solução mais
simples fosse escolhida. A revisão de código de 18/11 acrescentou o intervalo entre tentativas, a
trava que não espera e a contenção de toda falha da confirmação (FR-8352, FR-8355, FR-8363).

**Input**: pedido do usuário em 18/11/2026 — *"ao concluir a inscrição, o candidato recebe uma
comunicação clara, profissional e confiável, confirmando o que aconteceu e orientando seus próximos
passos"* —, com a instrução expressa de não presumir que a confirmação não existia antes de investigar.

> **Faixa de identificadores.** Esta spec abre em **FR-8350**, **SC-2920** e **UX-1020**, e reserva até
> o requisito oito mil trezentos e noventa e nove, o critério dois mil novecentos e trinta e nove e o
> requisito de experiência mil e trinta e nove. Os tetos medidos em 18/11/2026, na `main` e em todas as
> worktrees, eram os da `180`, que reservou até o requisito oito mil trezentos e quarenta e nove. As
> decisões desta spec recomeçam do número um.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-084a da `010`"). Uma decisão de outra feature é citada pelo assunto e pela feature.

---

## Por que esta feature existe

**A hipótese do pedido não se confirmou: a confirmação já existe.** Desde a `010` (a FR-084, a
FR-084a e a FR-084b), o envio da inscrição dispara uma mensagem à pessoa, com o protocolo, o código de
verificação, o Perfil, a concorrência, o instante do envio, a lista dos documentos recebidos e a
ressalva de que receber não é aceitar. Ela sai depois de a inscrição estar gravada, e a falha dela não
desfaz o envio. Desde a `121`, a mensagem tem a moldura institucional comum a todos os e-mails do GPS,
em texto puro e em HTML.

O que falta é o que se vê quando algo dá errado, e o que a mensagem diz quando dá certo:

1. **A falha não deixa rastro útil.** Ela vai ao registro técnico do servidor sem dizer de qual
   inscrição, e nada mais. Nem a pessoa nem a equipe sabem que a confirmação não saiu, e não há como
   tentar de novo.
2. **A mesma inscrição pode receber duas confirmações.** Quando o botão de envio é apertado duas vezes
   ao mesmo tempo, a segunda requisição recebe de volta a mesma inscrição — o envio é idempotente —, e
   manda a mensagem de novo.
3. **A mensagem usa uma palavra que, no portal, quer dizer outra coisa.** O assunto diz "Inscrição
   recebida" e o título "Recebemos a sua inscrição". Na área do candidato, desde a `148`, "Inscrição
   recebida" é um degrau **posterior**: a relação publicada pela comissão a lista como recebida. A
   situação de quem acabou de enviar é "Inscrição enviada". E a tela do comprovante diz uma terceira:
   "Inscrição realizada".
4. **O assunto não diz de qual seleção.** Quem se inscreve em mais de um Edital recebe mensagens de
   assunto igual, distintas só pelo protocolo.
5. **O botão leva à vitrine**, e não à inscrição: a pessoa entra e ainda precisa procurar o
   comprovante.
6. **A tela do comprovante não fala da mensagem.** A pessoa não sabe se deve esperar um e-mail, para
   qual endereço, nem o que fazer se ele não chegar.

### O que esta spec cobre, e o que fica fora

| Cobre | Fica fora, e por quê |
|---|---|
| Registrar cada tentativa de envio da confirmação, e o resultado | fila, tabela ou serviço novo de envio: a confirmação continua saindo na requisição (D-002) |
| Uma confirmação aceita por inscrição, no máximo | nova tentativa automática em segundo plano: quem pode repetir é a própria pessoa, na tela (D-003) |
| Assunto e situação na mesma palavra do portal | o texto do comprovante como documento — o que se imprime e o PDF não mudam (D-004) |
| Link ao comprovante, que leva ao acesso quando falta sessão | link que autentica sozinho: a FR-084a da `010` o proíbe |
| A tela do comprovante dizer o que aconteceu com a mensagem | o comprovante em PDF anexado à mensagem (D-001) |
| Nova tentativa pela titular, quando a última falhou | tela da equipe com o estado da confirmação: fica registrado como recomendação |

**O que o GPS não tem, e por isso não entra**: taxa de inscrição ou pagamento, cancelamento de
inscrição pelo candidato, e outro caminho que leve uma inscrição a enviada além do envio pelo portal.
As demais comunicações — avisos de resultado, chamada, pendência, agenda e convocação — têm cada uma a
sua feature e não mudam aqui.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A pessoa envia a inscrição e recebe uma confirmação que diz o que aconteceu (Priority: P1)

Uma pessoa confirma o envio da inscrição. O sistema grava o ato, mostra o comprovante e, na mesma
hora, manda uma mensagem ao e-mail da inscrição. O assunto diz que a inscrição foi enviada e em qual
Edital; o corpo diz o protocolo, o que foi enviado, a situação com a mesma palavra que o portal usa, o
que acontece agora, e leva ao comprovante.

**Why this priority**: é o caso de toda inscrição. A mensagem é o registro que fica na caixa de
entrada, e uma palavra trocada nela — "recebida" no lugar de "enviada" — diz à pessoa que ela já passou
de um degrau que ainda não alcançou.

**Independent Test**: enviar uma inscrição e ler a mensagem que sai: assunto com o Edital, a palavra
"enviada" para o ato, os próximos passos e o link ao comprovante; e nenhum CPF, telefone ou anexo.

**Acceptance Scenarios**:

1. **Given** um rascunho pronto para envio, **When** a pessoa confirma o envio, **Then** sai uma
   mensagem ao e-mail da inscrição, com assunto "Sua inscrição foi enviada — Edital 72/2026".
2. **Given** a mensagem, **When** a pessoa a lê, **Then** encontra o protocolo, o código de verificação,
   o Processo Seletivo, o Edital, o Perfil, a concorrência, o dia e a hora do envio, que a inscrição
   foi enviada, os documentos enviados e o que acontece agora.
3. **Given** a mensagem, **When** a pessoa procura dado pessoal, **Then** não encontra CPF, telefone
   nem data de nascimento, e a mensagem não traz anexo.
4. **Given** a pessoa sem sessão aberta no portal, **When** ela segue o link da mensagem, **Then** vai à
   tela de acesso e, depois do código, ao comprovante daquela inscrição.
5. **Given** o mesmo rascunho, **When** o envio é confirmado duas vezes ao mesmo tempo, **Then** sai uma
   mensagem só.
6. **Given** um rascunho que o sistema recusa enviar (prazo encerrado, documento faltando, Edital
   retificado), **When** a pessoa tenta enviar, **Then** nenhuma mensagem sai.

---

### User Story 2 - A pessoa sabe, na tela, se a mensagem saiu (Priority: P1)

Logo depois do envio, o comprovante diz se a confirmação foi enviada e para qual endereço. Se o envio
falhou, diz que a inscrição vale do mesmo jeito, que o comprovante está ali, e oferece tentar de novo.

**Why this priority**: sem isto, a falha é invisível para quem mais precisa saber. A pessoa espera um
e-mail que não vem, e não sabe se a inscrição foi feita.

**Independent Test**: enviar uma inscrição com o servidor de correio respondendo e ver "Enviamos a
confirmação para …"; repetir com o servidor recusando e ver o aviso de que não foi possível enviar, a
inscrição enviada do mesmo jeito, e o botão de tentar de novo.

**Acceptance Scenarios**:

1. **Given** a confirmação aceita pelo servidor de correio, **When** o comprovante abre, **Then** a tela
   diz para qual endereço e em que dia e hora a confirmação foi enviada, e lembra de olhar a caixa de
   spam.
2. **Given** a confirmação recusada ou o servidor fora do ar, **When** o comprovante abre, **Then** a
   tela diz que não foi possível enviar a confirmação, que a inscrição foi enviada do mesmo jeito e que o
   comprovante da tela vale como prova, e oferece enviar de novo.
3. **Given** a última tentativa falhou, **When** a pessoa pede para enviar de novo e o servidor aceita,
   **Then** a mensagem sai, a tela passa a dizer que foi enviada, e a trilha registra a segunda
   tentativa.
4. **Given** a confirmação já aceita, **When** chega um pedido de enviar de novo (por exemplo, de uma
   aba antiga), **Then** nada sai, e a tela continua dizendo que a confirmação foi enviada.
5. **Given** uma tentativa que falhou há menos de um minuto, **When** a pessoa pede para enviar de novo,
   **Then** nada sai, e a tela pede que ela espere um minuto.
6. **Given** uma inscrição enviada antes desta feature, **When** o comprovante abre, **Then** a tela não
   diz nada sobre a confirmação: o sistema não sabe o que aconteceu com ela, e não afirma.
7. **Given** o comprovante, **When** a pessoa o imprime ou baixa o PDF, **Then** o aviso sobre a
   mensagem não aparece no papel.

---

### User Story 3 - O sistema responde se a confirmação de uma inscrição saiu (Priority: P2)

Alguém da equipe recebe a pergunta "eu não recebi o e-mail da inscrição". O registro do sistema diz,
para aquela inscrição, quantas tentativas houve, quando, e se o servidor de correio aceitou.

**Why this priority**: é o que torna a falha tratável fora da tela da pessoa. Fica em P2 porque a
pessoa já tem, na própria tela, o que precisa (história 2).

**Independent Test**: enviar uma inscrição com o servidor recusando, pedir de novo com o servidor
aceitando, e consultar o registro da inscrição: duas tentativas, a primeira não enviada e a segunda
enviada, sem endereço, nome nem protocolo.

**Acceptance Scenarios**:

1. **Given** uma inscrição enviada, **When** se consulta o registro dela, **Then** cada tentativa de
   confirmação aparece com o número, o instante e o resultado.
2. **Given** uma falha de envio, **When** se lê o registro técnico do servidor, **Then** ele diz de qual
   inscrição foi a falha, pelo identificador, sem endereço de e-mail.

---

### Edge Cases

- **O servidor de correio aceita a conexão e não aceita a mensagem**, sem erro: conta como não enviada.
  Contar como enviada seria a falha mais silenciosa possível — tudo indicaria sucesso.
- **O servidor de correio demora a responder**: a pessoa espera até o limite de tempo configurado do
  correio, e então vê o comprovante com o aviso de falha. A inscrição já estava gravada antes.
- **O registro da tentativa falha depois de a mensagem sair**: a mensagem já saiu, e o registro técnico
  diz que a trilha não foi gravada. A tela, sem registro, não afirma nada.
- **A pessoa troca o e-mail principal depois de enviar**: a confirmação, e a nova tentativa, vão ao
  e-mail gravado na inscrição, que é o que a FR-013 da `010` congela no envio.
- **Duas inscrições da mesma pessoa** — em Perfis do mesmo Edital ou em Editais diferentes —: cada uma
  tem a sua confirmação, a sua contagem e a sua tela. A confirmação de uma não impede nem conta para a
  outra.
- **Pedido de enviar de novo em inscrição alheia, ou em rascunho**: a resposta é a mesma de inscrição
  inexistente, e nada sai.
- **Pedido de enviar de novo enquanto outra tentativa da mesma inscrição está em curso**: não espera nem
  envia; a outra registra o que acontecer, e a tela mostra. Esperar empilharia requisições atrás de um
  servidor de correio lento.
- **Dois cliques no envio, e a primeira tentativa falhou**: o segundo encontra a falha de menos de um
  minuto e não tenta (FR-8363); a pessoa vê o aviso e pode tentar depois.
- **Inscrição sem endereço**: não deveria existir. Se existir, a confirmação não é tentada nem
  registrada, o registro técnico diz qual inscrição, e a tela do comprovante não diz nada — em vez de
  um aviso de falha com um botão que falharia sempre.
- **Edital retificado depois do envio**: a confirmação diz o que a inscrição aceitou, como o
  comprovante (a versão aceita), e nenhuma mensagem nova sai por causa da Retificação.
- **Os cenários de treinamento da `134`** criam inscrições enviadas sem passar pela tela: não mandam
  confirmação, e o comprovante delas não diz nada sobre ela.
- **A chave dos avisos da `066` desligada**: não afeta a confirmação, que é outra situação da FR-084 da
  `010`.

## Requirements *(mandatory)*

### Functional Requirements

#### Quando a confirmação sai

- **FR-8350**: A confirmação DEVE sair somente depois de o envio da inscrição estar gravado, e somente
  para a inscrição que passou a enviada; rascunho e envio recusado NÃO PODEM disparar mensagem.
- **FR-8351**: Uma inscrição NÃO PODE receber mais de uma confirmação aceita pelo servidor de correio. O
  mesmo envio repetido — duplo clique, duas abas, a repetição idempotente do ato — e o pedido de enviar
  de novo depois de uma tentativa aceita NÃO PODEM produzir segunda mensagem.
- **FR-8352**: A falha da confirmação NÃO PODE desfazer nem impedir o envio da inscrição: a pessoa DEVE
  chegar ao comprovante do mesmo jeito (reafirma a FR-084b da `010`). Isso vale para qualquer falha no
  caminho da confirmação — o servidor de correio, o banco, um dado que falte para montar a mensagem —,
  que vai ao registro técnico e nunca chega à pessoa como erro.

#### O que a mensagem diz

- **FR-8353**: O assunto DEVE dizer que a inscrição foi enviada e nomear o Edital.
- **FR-8354**: A mensagem DEVE nomear o ato com a mesma palavra que a área do candidato usa para a
  situação de quem acabou de enviar ("enviada"), e NÃO PODE apresentar a inscrição como recebida,
  aceita, confirmada, deferida ou homologada. A situação atual NÃO PODE ser fixada na mensagem: ela é a
  da área do candidato, para onde a mensagem leva — uma nova tentativa dias depois a diria velha.
- **FR-8355**: A mensagem DEVE conter o que a FR-084a da `010` exige — protocolo, código de
  verificação, a oportunidade (Processo Seletivo, Edital, Perfil e concorrência), o instante do envio e
  os documentos enviados — e, além disso, o que acontece agora: que enviada não quer dizer aceita, que
  o resultado sai conforme o Edital, e que a situação e qualquer passo pedido à pessoa aparecem na área
  do candidato. Pela razão da FR-8354, NÃO PODE dizer que não há nada a fazer: uma nova tentativa
  semanas depois chegaria a quem já tem um passo pendente.
- **FR-8356**: A mensagem NÃO PODE conter CPF, telefone, data de nascimento, anexo nem link que
  autentica (FR-084a da `010`). O comprovante em PDF NÃO PODE ir anexado (D-001).
- **FR-8357**: O link da mensagem DEVE levar ao comprovante da inscrição. Quem o abre sem sessão DEVE ir
  à tela de acesso e, depois do código, voltar ao comprovante, onde a titularidade é conferida. A
  resposta sem sessão NÃO PODE depender de a inscrição existir nem de quem é o titular.

#### O registro de cada tentativa

- **FR-8358**: Cada tentativa de envio da confirmação DEVE ficar registrada na trilha da inscrição, com
  o número da tentativa, o instante e o resultado — enviada ou não enviada —, e NÃO PODE registrar
  endereço, nome, protocolo nem a mensagem de erro do servidor.
- **FR-8359**: "Enviada" DEVE querer dizer aceita pelo servidor de correio, e NÃO PODE ser apresentada,
  na tela ou no registro, como entregue, recebida ou lida.
- **FR-8360**: Um servidor de correio que não aceita a mensagem DEVE resultar em "não enviada", tenha ou
  não levantado erro.
- **FR-8361**: A falha DEVE ir também ao registro técnico do servidor com o identificador da inscrição,
  sem endereço de e-mail.

#### A tela do comprovante

- **FR-8362**: A tela do comprovante DEVE dizer o que aconteceu com a confirmação, pela última tentativa
  registrada: enviada, com o endereço e o dia e a hora; ou não enviada, com a garantia de que a
  inscrição foi enviada do mesmo jeito e de que o comprovante da tela vale como prova. Sem tentativa
  registrada, NÃO PODE dizer nada sobre a confirmação.
- **FR-8363**: Quando a última tentativa não foi enviada, a tela DEVE oferecer à titular enviar a
  confirmação de novo. A nova tentativa obedece à FR-8351, à FR-8358 e à FR-8360, e vai ao e-mail
  gravado na inscrição. Entre duas tentativas da mesma inscrição DEVE haver ao menos um minuto: o
  pedido antes disso não chega ao servidor de correio, e a tela diz que é preciso esperar. Cada
  tentativa pode levar até o limite de tempo do correio, e sem o intervalo os cliques de quem espera um
  servidor fora do ar viram carga sobre o portal inteiro.
- **FR-8364**: Só a titular de uma inscrição enviada PODE pedir nova tentativa. Pedido de outra pessoa,
  sem sessão ou sobre rascunho DEVE ter a mesma resposta de inscrição inexistente, e nada sai (FR-085 e
  FR-086 da `010`).
- **FR-8365**: A situação no topo do comprovante DEVE usar o mesmo rótulo da área do candidato e da
  mensagem ("Inscrição enviada").
- **FR-8366**: O aviso sobre a confirmação e o botão de enviar de novo NÃO PODEM aparecer no comprovante
  impresso nem no PDF, e o texto do comprovante como documento NÃO PODE mudar (D-004).

#### Abrangência

- **FR-8367**: Estas regras DEVEM valer para toda inscrição enviada pelo portal, qualquer que seja o
  Processo Seletivo, o Perfil ou a concorrência.
- **FR-8368**: Cada inscrição DEVE ter a sua confirmação, a sua contagem de tentativas e o seu aviso na
  tela, independentes das outras inscrições da mesma pessoa.

### Requisitos de experiência

- **UX-1020**: Na mensagem, o protocolo e o código de verificação DEVEM vir em destaque, logo depois do
  título; os dados e os documentos, em seguida; e o que acontece agora, antes do botão.
- **UX-1021**: A mensagem e o aviso da tela DEVEM falar com a pessoa ("você", "sua inscrição"), em frases
  curtas, sem termo do sistema (protocolo é palavra dela; deferimento, homologação e versão aceita não
  são).
- **UX-1022**: O botão de enviar de novo DEVE ser secundário: a ação principal do comprovante continua
  sendo baixá-lo em PDF.

### Key Entities

- **Inscrição**: a enviada passa a ter, na trilha, as tentativas de confirmação. Nenhum campo novo,
  nenhum estado novo.
- **Tentativa de confirmação**: o número, o instante e o resultado (enviada ou não enviada). É um
  registro da trilha de auditoria que já existe, e não uma tabela.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2920**: Toda inscrição enviada pelo portal depois da implantação tem pelo menos uma tentativa de
  confirmação registrada.
- **SC-2921**: Nenhuma inscrição tem mais de uma confirmação aceita pelo servidor de correio.
- **SC-2922**: Nenhuma confirmação contém CPF, telefone, data de nascimento, anexo ou link que
  autentica.
- **SC-2923**: A mensagem, a tela do comprovante e a área do candidato usam a mesma palavra para a
  situação de uma inscrição recém-enviada.
- **SC-2924**: Quem segue o link da mensagem sem sessão chega ao comprovante da própria inscrição
  informando só o e-mail e o código, sem procurar a inscrição na lista.
- **SC-2925**: Para toda inscrição enviada depois da implantação, o sistema responde se a confirmação foi
  aceita pelo servidor de correio, quando, e em quantas tentativas.

## Assumptions

- O servidor de correio é o mesmo das outras mensagens do GPS, com o limite de tempo que o ambiente já
  configura. Quando ele demora, a pessoa espera até esse limite antes de ver o comprovante (D-002).
- "Enviada" é o que o sistema sabe: que o servidor de correio aceitou a mensagem. Entrega, caixa de
  spam e leitura estão fora do alcance dele, como já está escrito para os avisos da `066`.
- A nova tentativa é a mesma situação da FR-084 da `010` — a confirmação do envio da inscrição,
  endereçada à credencial que praticou o ato —, e por isso não exige revisar aquela regra.
- O comprovante como documento — a página imprimível e o PDF — continua dizendo que a inscrição foi
  "recebida pelo sistema". É verdade naquele sentido, e mudar o texto mudaria o código de verificação
  de quem ainda vai baixar o comprovante. A ambiguidade entre esse "recebida" e o degrau "Inscrição
  recebida" da `148` fica registrada como achado (D-004).
- A equipe não tem, hoje, tela que mostre a trilha de uma inscrição. Mostrar o estado da confirmação no
  detalhe da inscrição, na gestão, fica como recomendação, e não como escopo.

## Decisões

### D-001 — O comprovante vai por link, e não anexado

Tomada nesta spec, a pedido do usuário, entre três alternativas: (A) anexar o PDF, (B) levar ao
comprovante por link, (C) as duas. **Escolhida a B.**

- **A norma proíbe a A.** O comprovante traz CPF, e-mail e telefone, e a FR-084a da `010` proíbe CPF e
  telefone na mensagem: eles viajam para onde ela for encaminhada.
- **O comprovante do sistema é a prova, e o anexo seria cópia.** A página e o PDF são gerados da
  inscrição a cada pedido, com o código de verificação e o resumo de cada arquivo. Um PDF parado numa
  caixa de entrada não ganha nada com isso, e mensagem com anexo cai mais em filtro de spam.
- **Nada novo para manter.** O link usa o comprovante que existe e o caminho de acesso por código que a
  `121` já abriu para a convocação.

Alternativa C recusada pelos dois motivos da A.

### D-002 — A confirmação continua saindo na requisição, e o registro é a trilha

Tomada nesta spec. A confirmação já sai na requisição do envio, depois do commit, e continua assim. O
que muda é que cada tentativa passa a ser registrada na trilha de auditoria da inscrição, e que o envio
acontece sob uma trava da inscrição, depois de conferir que nenhuma tentativa anterior foi aceita.

- **Recusado: o despacho dos avisos da `066`.** Ele tem fila, tentativa gravada antes do envio e
  execução por minuto, mas o aviso é, por definição, decisão de uma pessoa da equipe sobre um ato
  publicado: exige marco e Perfil, aparece na tela de avisos da comissão — um por inscrição —, e só sai
  no minuto seguinte, quando a tela já teria dito à pessoa o que aconteceu.
- **Recusado: tabela nova de envios.** A trilha já é append-only, já é indexada por inscrição, e a
  `134` já registra nela o resultado de cada envio do aviso de pendência.
- **O custo aceito:** quando o servidor de correio demora, a pessoa espera até o limite configurado
  antes de ver o comprovante — o que já acontece hoje.

### D-003 — Quem tenta de novo é a pessoa, na tela

Tomada nesta spec. A falha é mostrada à titular no comprovante, com um botão para enviar de novo; não há
nova tentativa automática em segundo plano. A pessoa está na tela no momento da falha, já tem o
comprovante, e é quem sabe se a mensagem chegou. Uma tentativa automática exigiria a fila recusada na
D-002, e repetiria em silêncio o envio para uma caixa que a pessoa talvez tenha digitado errado.

### D-004 — "Inscrição enviada" na mensagem e no topo da tela; o documento não muda

Tomada nesta spec. A palavra da situação passa a ser a da área do candidato, que é a que acompanha a
pessoa até o resultado. O texto do comprovante como documento — "recebida pelo sistema" e a ressalva do
deferimento — fica como está, porque mudá-lo mudaria o PDF e o código de verificação de inscrições já
enviadas. Fica registrado como **achado**, para decisão do usuário: o GPS usa "recebida" em dois
sentidos — chegou ao sistema (o comprovante) e consta da relação publicada (a `148`).
