# Feature Specification: Correções de orientação e segurança operacional depois da publicação (P0)

**Feature Branch**: `claude/126-orientacao-p0-307906`, sobre a `main` em `250efe97`

**Created**: 2026-11-06

**Status**: Draft. Corrige apresentação: nenhuma regra de negócio, migration, tabela, coluna ou
estado persistido novo. A única mudança de regra discutida, recusar a emissão da ordem sem
resultado nas Etapas (G-01), **não** é implementada: fica como pergunta ao usuário, com as opções,
em *Decisão pendente do usuário*.

**Input**: *"Correções pontuais que induzem a erro ou contradizem o domínio depois da publicação:
sucessão em destaque logo depois de um ato, 'Falta' em lista sem inscrito, rótulo de convocação sem
comunicação, aviso de congelamento fora do lugar e a ordem por pontuação emissível vazia."*

> **Faixa de identificadores.** Esta spec usa a faixa reservada para ela: os requisitos funcionais de
> quatro mil e dez a quatro mil e quarenta e nove, os critérios de mil duzentos e dez a mil duzentos
> e vinte e nove e os de experiência de duzentos e vinte e três a duzentos e vinte e nove; os não
> usados ficam livres. O teto foi medido em 06/11/2026 em `specs/` de todas as
> worktrees desta máquina: o requisito funcional quatro mil e seis, o critério mil duzentos e nove e o
> UX-222 da `097`. As pastas `123`, `124` e `125` estão tomadas por outras worktrees; a `127` (Spec
> B, em paralelo) não usa esta faixa. As decisões reiniciam em `D-001`.
>
> **Origem.** O estudo de orientação da jornada de 06/11/2026 (PR #412, `doc/estudo-orientacao-da-jornada-2026-11-06/`,
> ainda fora da `main`), achados J-06, J-07, J-08, J-10 e G-01. **A numeração dos itens aqui é a do
> pedido de abertura**, e difere da do estudo (que chama de A1 o *Não se aplica* e de A2 a sucessão):
>
> | Aqui | Estudo | Achado | Assunto |
> |---|---|---|---|
> | A1 | A2 | J-08 | A sucessão logo depois do ato |
> | A2 | A1 | J-06 | Lista sem inscrito: *Não se aplica* |
> | A3 | A3 | J-12 | Erro técnico da Caixa — **fora**: está na `124` (PR #410) |
> | A4 | A4 | J-07 | "Aguardando resposta" sem comunicação enviada |
> | A5 | A5 | J-10 | O aviso de congelamento inviável no lugar certo |
> | A6 | A6 | G-01 | A ordem por pontuação emissível sem resultado nas Etapas |

## Por que esta feature existe

O estudo concluiu que, depois da publicação, o GPS sabe o estado de cada ato e o comunica mal. Cinco
desses pontos fazem mais do que deixar de orientar: **induzem ao ato errado** ou **dizem o contrário
do domínio**. Foram todos conferidos no código da `main` em `250efe97`.

1. **Depois de emitir o corte, o botão de maior peso é outro "Emitir corte".** A tela do corte volta
   com "Corte emitido." e, logo abaixo, o formulário de sucessão aberto, com campo de motivo e o mesmo
   botão cheio "Emitir corte" (`corte.html`, captura `13b`). A ordem, a apuração e a relação do sorteio
   fazem o mesmo. Sucessão é ato imutável, com motivo: é o último que deveria estar em destaque logo
   depois do primeiro. E a mensagem de sucesso não diz em qual recorte, nem o que foi gravado.
2. **Lista sem inscrito aparece como *Falta* em tudo.** No Edital 35, o Perfil Polo Vitória não teve
   inscrição. A condução do marco mostra *Falta* nas doze células e oferece "Cortar o marco…" e
   "Apurar a ocupação do marco…" (captura `11`). Nada disso pode acontecer: congelar a relação é
   recusado (`relation_would_be_empty`), e sem relação não há sorteio, ordem, corte nem apuração. A
   condução distingue "o marco não corta" e "sem quadro de vagas", mas não "ninguém se inscreveu".
3. **A convocação da mesma lista dá duas ordens opostas** (captura `12`): "Ir para a apuração de
   ocupação" e "Não há mais quem chamar dentro da faixa que o corte alcançou… Ir para a ocupação e pedir
   a faixa seguinte". Não há corte, e a faixa seguinte seria recusada.
4. **"Aguardando resposta" de quem nunca recebeu a comunicação.** O relatório do Edital e a confirmação
   de Encerrar contam como "aguardando resposta, até 10/11" a convocação cuja comunicação não saiu
   (captura `16`). Pelo domínio (`convocacao/domain/prazo.estado`), o prazo dela **não começou**: a tela
   da convocação diz "Sem comunicação enviada". E a mesma conta faz uma convocação sem envio, com
   vencimento informado já passado, aparecer como "prazo encerrado sem registro", o que o domínio
   proíbe (`decorrido` exige que o prazo tenha corrido).
5. **"Não congele a relação hoje" quando não há o que congelar.** No 35 Cefor, com as três relações
   congeladas e sorteadas, a primeira frase dos recortes do sorteio é esse aviso (captura `08`). No
   Polo Vitória, sem inscrito, ele pede Retificação da extração. A regra da `102` (FR-2659: a sucessão
   também congela) está certa; o lugar, não.
6. **A ordem por pontuação pode ser emitida sem nenhum resultado** (G-01). No Edital 91, nenhuma Etapa
   enumerada foi avaliada, e a tela oferece "Emitir ordem", irreversível. A tela lista quem fica sem
   posição e o motivo, mas a confirmação mostra só as contagens (captura `32`). A ordem nasceria
   vazia, obsoleta assim que os resultados chegassem, e a sucessão exigiria motivo.

### O que esta spec cobre, e o que fica fora

Cobre os itens 1 a 6 acima, **na apresentação**. No item 6, cobre o que a tela diz; recusar a emissão
é mudança de regra e fica com o usuário.

Fica fora, de propósito:

- **A3 (erro técnico da Caixa)**: está na `124`, PR #410.
- **Toda orientação nova** — "Próximo nesta lista", "Ainda neste marco", as providências por papel no
  cartão "O que fazer agora", o "Andamento da seleção": são da Spec B (`127`), em paralelo. As
  mensagens de sucesso desta spec dizem **o que foi feito**, e não o que fazer depois.
- **Colunas novas na condução do marco** (relação, semente, convocação, maquete `M3` do estudo): P3.
- **Trocar *Falta* por *Depois* na condução** (D7 do estudo): P3.
- O cartão "Classificação" da página do Edital (`resumo_dos_marcos`): é presença de ato, não estado,
  e muda com a Spec B.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Depois do ato, a tela confirma o que foi feito e não convida a suceder (Priority: P1)

Quem conduz emite o corte da ampla concorrência. A tela volta dizendo que o corte da ampla foi emitido,
quantos progridem e até que posição. Abaixo, a faixa gravada. A sucessão existe, mas recolhida, sob o
nome "Suceder este corte (exige motivo)". O mesmo vale para a ordem, a apuração e a relação do sorteio.

**Why this priority**: sucessão por engano é ato imutável com motivo, e o desenho de hoje a põe como o
botão de maior peso logo depois do ato. É o risco operacional mais direto do estudo (J-08).

**Independent Test**: emitir um corte e conferir que o único botão de emissão visível sem abrir nada não
é o de sucessão, e que a mensagem nomeia o recorte e a contagem.

**Acceptance Scenarios**:

1. **Given** um recorte com ordem e sem corte, **When** quem conduz emite o corte, **Then** a tela diz
   "Corte emitido para <recorte>", quantos progridem e até que posição, e o formulário de sucessão
   aparece recolhido, rotulado "Suceder este corte (exige motivo)".
2. **Given** a mesma tela, **When** a pessoa abre o bloco recolhido e preenche o motivo, **Then** a
   sucessão funciona como hoje: mesmo campo, mesma exigência de motivo, mesmo comando.
3. **Given** um corte **obsoleto**, **When** a tela abre, **Then** o bloco de sucessão vem **aberto**:
   a sucessão é o passo esperado.
4. **Given** um recorte com ordem emitida, **When** a tela da ordem abre, **Then** a sucessão vem
   recolhida, "Suceder esta ordem (exige motivo)", salvo se a ordem estiver obsoleta.
5. **Given** a ocupação de um marco com dois recortes apurados, **When** a tela abre, **Then** cada
   recorte tem "Suceder esta apuração (exige motivo)" recolhido, salvo o recorte com apuração obsoleta.
6. **Given** uma relação congelada, **When** a tela do sorteio abre, **Then** "Suceder esta relação
   (exige motivo)" vem recolhido, e aberto se a relação nunca sortear (diagnóstico da `102`).

---

### User Story 2 — Lista sem inscrito não aparece como pendência (Priority: P1)

Quem conduz abre o marco do Polo Vitória do Edital 35, que não teve inscrito. Lê *Não se aplica* em
cada célula, com "nenhuma inscrição nesta lista", e a frase "Nada a conduzir neste marco". Nenhum gesto
é oferecido. Na convocação da mesma lista, lê que não há convocação a fazer, sem caminho para a
apuração nem para a faixa seguinte.

**Why this priority**: falsa pendência que o encerramento herda, gestos que levam a recusa e duas
orientações que se contradizem (J-06).

**Independent Test**: num marco de sorteio com uma lista sem inscrito, com inscrições encerradas,
conferir as células, os gestos e a convocação.

**Acceptance Scenarios**:

1. **Given** um marco de sorteio, inscrições encerradas e uma lista que nenhuma inscrição enviada
   declarou, **When** a condução abre, **Then** as quatro células da lista dizem *Não se aplica* com a
   nota "nenhuma inscrição nesta lista", sem link, e ela não conta nos totais.
2. **Given** o mesmo marco com outra lista com inscritos e em falta, **When** a pessoa abre a
   conferência de um gesto, **Then** a lista sem inscrito aparece *fora*, com a razão, e não *impedida*.
3. **Given** todas as listas do marco sem inscrito, **When** a condução abre, **Then** ela diz "Nada a
   conduzir neste marco" e não oferece gesto.
4. **Given** as inscrições **ainda abertas**, **When** a condução abre, **Then** a lista sem inscrito
   continua como hoje (*Falta*): alguém ainda pode se inscrever.
5. **Given** a relação da lista **congelada** (inscrições depois invalidadas, por exemplo), **When** a
   condução abre, **Then** nada muda: há ato, e a cadeia segue a regra de hoje.
6. **Given** um marco **por pontuação** com lista sem inscrito, **When** a condução abre, **Then** nada
   muda: a ordem vazia se emite e é *Feito*, "ninguém concorreu" (a decisão da `049` sobre a ordem vazia).
7. **Given** a convocação da lista sem inscrito, **When** a tela abre, **Then** ela diz que nenhuma
   inscrição declarou a lista e que não há ocupação a apurar nem quem convocar, e não oferece "Ir para
   a apuração de ocupação" nem "pedir a faixa seguinte".
8. **Given** a convocação de um recorte **sem corte** e com fila vazia, **When** a tela abre, **Then**
   ela não fala em "faixa que o corte alcançou" nem oferece pedir a faixa seguinte.
9. **Given** a convocação de um recorte **com corte** e fila esgotada, **When** a tela abre, **Then** a
   frase e o caminho da faixa seguinte continuam como hoje.

---

### User Story 3 — O relatório e o Encerrar distinguem quem não recebeu a comunicação (Priority: P1)

Quem vai encerrar o Edital 35 lê, nas advertências, "1 convocação sem comunicação enviada", e não "1
convocação aguardando resposta, até 10/11/2026". O relatório do Edital diz o mesmo.

**Why this priority**: a única lista do que falta no Edital está numa tela de ato irreversível, e ela diz
o contrário do domínio (J-07).

**Independent Test**: com uma convocação vigente sem envio bem-sucedido, conferir a frase do relatório e
a da confirmação de Encerrar.

**Acceptance Scenarios**:

1. **Given** uma convocação vigente, sem desfecho e sem comunicação enviada, **When** a confirmação de
   Encerrar abre, **Then** ela diz "1 convocação sem comunicação enviada", sem data, e não "aguardando
   resposta".
2. **Given** uma convocação com comunicação enviada e prazo correndo, **When** o relatório abre,
   **Then** ela é "aguardando resposta, até <vencimento>", como hoje.
3. **Given** uma convocação sem comunicação enviada cujo vencimento informado já passou, **When** o
   relatório abre, **Then** ela é "sem comunicação enviada", e **não** "prazo encerrado sem registro".
4. **Given** uma convocação enviada com vencimento passado e sem desfecho, **When** o relatório abre,
   **Then** ela é "com prazo encerrado sem registro de resposta", como hoje.
5. **Given** o relatório consolidado da unidade, **When** ele soma os Editais, **Then** a nova espécie
   aparece com o próprio rótulo, sem se misturar com "aguardando resposta".

---

### User Story 4 — O aviso de congelamento inviável aparece onde se congela (Priority: P2)

No sorteio do 35 Cefor, com as três relações congeladas, a lista de recortes não começa mais por "Não
congele a relação hoje". O aviso aparece dentro do bloco "Suceder esta relação", que é onde congelar
de novo ainda é possível. No Polo Vitória, sem inscrito, ele não aparece.

**Why this priority**: ensina a ignorar avisos e leva a pedir Retificação sem necessidade (J-10), mas
não grava nada errado sozinho.

**Independent Test**: com a extração declarada para hoje, conferir a tela do sorteio com todas as
relações congeladas, com uma por congelar e com lista sem inscrito.

**Acceptance Scenarios**:

1. **Given** congelar hoje condenaria o sorteio e há recorte com inscrição e relação **por congelar**,
   **When** a tela abre, **Then** o aviso aparece no topo dos recortes, como hoje.
2. **Given** a mesma condição e **todas** as relações com inscrição já congeladas, **When** a tela abre,
   **Then** o topo não traz o aviso, e ele aparece dentro do bloco de sucessão de cada relação que o
   admite.
3. **Given** as inscrições ainda correndo, **When** a tela abre, **Then** o aviso de extração cedo demais
   continua no topo: é quando ainda há tempo de retificar.
4. **Given** um recorte sem inscrito, **When** a tela abre, **Then** ele não faz o aviso aparecer.

---

### User Story 5 — A confirmação da ordem diz por que todos ficam sem posição (Priority: P1)

A presidência da comissão do Edital 91 abre a ordem do marco por pontuação antes de qualquer avaliação
e clica em "Emitir ordem". A confirmação diz que as inscrições do recorte estão sem resultado na Etapa
enumerada, quantas em cada uma, e que, consolidados os resultados, esta ordem ficará obsoleta e
sucedê-la exigirá motivo. A emissão continua possível.

**Why this priority**: ato irreversível confirmado sem a informação que o tornaria evidentemente
precoce (G-01).

**Independent Test**: com um marco por pontuação e nenhuma Etapa consolidada, abrir a confirmação e
conferir o motivo e as contagens por Etapa.

**Acceptance Scenarios**:

1. **Given** um recorte em que nenhuma inscrição considerada tem resultado nas Etapas enumeradas,
   **When** a confirmação abre, **Then** ela diz, em destaque, que nenhuma inscrição tem resultado, lista
   cada Etapa enumerada com a quantidade sem resultado nela, e diz a consequência.
2. **Given** um recorte em que só parte das inscrições está sem resultado numa Etapa, **When** a
   confirmação abre, **Then** ela diz quantas, e em qual Etapa.
3. **Given** inscrições sem posição por **eliminação**, **When** a confirmação abre, **Then** elas
   aparecem agrupadas pelo motivo da eliminação, e não contam como "sem resultado".
4. **Given** todos com resultado, **When** a confirmação abre, **Then** nenhum aviso de resultado ausente
   aparece.
5. **Given** qualquer dos casos, **When** a pessoa confirma, **Then** a ordem é emitida como hoje.

### Edge Cases

- **Edital com uma lista só** (sem reserva): a condução tem um recorte; sem inscrito, a tela diz "Nada a
  conduzir neste marco".
- **Etapa de habilitação antes do sorteio** (`qualifyingStageId`): a projeção do sorteio filtra pelos
  habilitados, e é zero enquanto a Etapa não é consolidada. Isso **não** é "sem inscrito": o critério
  olha as inscrições enviadas que declararam a lista, sem o filtro (D-002).
- **Retificação que reabre as inscrições**: a lista volta a *Falta*, porque o critério é derivado a
  cada leitura (inscrições encerradas é parte dele).
- **Inscrição enviada depois cancelada ou excluída da submissão**: conta o estado de agora — se nenhuma
  inscrição *enviada* declara a lista, ela é sem inscrito.
- **A ampla concorrência sem inscrito**: só acontece com o Perfil inteiro vazio; vale o mesmo critério,
  sobre todas as inscrições enviadas do Perfil.
- **Convocação com mais de uma comunicação, uma falha e uma enviada**: vale o envio bem-sucedido mais
  recente, como na tela da convocação (`envio_de`).
- **Ordem com sucessão e resultados ausentes**: a confirmação diz os dois — que sucede o ato vigente e
  que há inscrições sem resultado.
- **Etapa decisória enumerada** (porta, sem pontuação): conta como "com resultado" quando há
  Resultado vigente, ainda que sem pontuação.
- **Sorteio com relação obsoleta (diagnóstico da `102`)**: o bloco de sucessão vem aberto, e o
  diagnóstico continua dizendo a saída; o aviso de congelamento não se repete ali (`102`: o recorte cujo
  diagnóstico já diz a saída fica de fora).

## Requirements *(mandatory)*

### Functional Requirements

#### A1. A sucessão depois do ato

- **FR-4010**: Nas telas do corte, da ordem, da ocupação e do sorteio, quando o recorte já tem ato
  vigente do tipo que a tela emite, o formulário que o sucede MUST vir **recolhido**, num bloco com
  rótulo próprio que nomeia o ato e diz que exige motivo (UX-223).
- **FR-4011**: O bloco de sucessão MUST vir **aberto** quando o ato vigente é obsoleto: corte
  obsoleto; ordem que diverge do cálculo de agora e é recalculável; apuração obsoleta; relação cujo
  diagnóstico diz que ela nunca sorteará. A da ordem vem aberta também quando há decisão de recurso a
  citar: a ordem que a executa é a sucessora. Nos demais casos, inclusive logo depois do ato,
  recolhido (D-001).
- **FR-4012**: Recolher o formulário MUST NOT mudar o que a sucessão exige nem o que grava: o mesmo
  campo de motivo obrigatório, a mesma confirmação, o mesmo comando, a mesma trilha.
- **FR-4013**: A faixa seguinte do corte e as citações de decisão de recurso da ordem MUST continuar
  como estão: não são sucessão. As citações seguem junto do formulário da ordem que as leva.
- **FR-4014**: A mensagem de sucesso do corte MUST dizer o recorte, quantos progridem e até que
  posição, e se o ato sucedeu outro.
- **FR-4015**: A mensagem de sucesso da ordem MUST dizer o recorte, quantas inscrições receberam posição
  e quantas ficaram sem.
- **FR-4016**: A mensagem de sucesso da apuração MUST dizer o recorte apurado e os números que a
  apuração gravou: efetivas, ocupadas e a ocupar.
- **FR-4017**: A mensagem de sucesso da relação do sorteio MUST dizer o recorte, além do que já diz.
- **FR-4018**: Nenhuma mensagem de sucesso desta spec MUST dizer o próximo passo da jornada: isso é da
  Spec B (`127`).

#### A2. Lista sem inscrito: *Não se aplica*

- **FR-4019**: Um recorte de **marco de sorteio** MUST ser tratado como **sem inscrito** quando, ao mesmo
  tempo: o período de inscrições terminou, ou o Edital não designa período (não recebe inscrição
  por este sistema); nenhuma inscrição enviada do Perfil declara aquela lista (na
  ampla, nenhuma inscrição enviada do Perfil); e a relação do recorte não está congelada. A ausência de
  ato, sozinha, MUST NOT bastar (D-002).
- **FR-4020**: Na condução do marco, as quatro células de um recorte sem inscrito MUST dizer *Não se
  aplica*, com a nota "nenhuma inscrição nesta lista", sem link para tela de ato (UX-224). O recorte
  MUST NOT contar nos totais de nenhuma operação.
- **FR-4021**: Um recorte sem inscrito MUST NOT fazer a condução oferecer gesto. Na conferência de um
  gesto oferecido por outro recorte, ele MUST aparecer *fora*, com a razão "nenhuma inscrição nesta
  lista", e não *impedido*.
- **FR-4022**: Quando **todos** os recortes do marco são sem inscrito, a condução MUST dizer "Nada a
  conduzir neste marco", com a razão, no lugar da frase "Nenhum recorte deste marco está em falta…", e
  a legenda de totais MUST NOT dizer "0 de 0".
- **FR-4023**: Num **marco por pontuação**, a lista sem inscrito MUST continuar como hoje: a ordem vazia
  se emite, e emitida é *Feito*, "ninguém concorreu" (a decisão da `049` sobre a ordem vazia).
- **FR-4024**: A convocação de um recorte sem inscrito MUST dizer que nenhuma inscrição declarou a lista
  e que não há ocupação a apurar nem quem convocar, e MUST NOT oferecer "Ir para a apuração de
  ocupação", o gesto de convocar titulares nem "pedir a faixa seguinte".
- **FR-4025**: A frase "Não há mais quem chamar dentro da faixa que o corte alcançou" e o caminho para
  pedir a faixa seguinte MUST aparecer só quando o recorte tem corte vigente. Sem corte, e com a fila
  vazia, a convocação MUST dizer que não há mais quem chamar na ordem do recorte, sem falar em faixa.
- **FR-4026**: A ocupação de um recorte sem inscrito MUST dizer *Não se aplica* e MUST NOT mandar emitir
  a ordem dele (D-005).

#### A4. O rótulo da convocação

- **FR-4027**: O relatório do Edital, o relatório consolidado da unidade e a confirmação de Encerrar MUST
  classificar cada convocação vigente sem desfecho pelos estados do domínio
  (`convocacao/domain/prazo.estado`): prazo não iniciado, prazo em curso, vencimento decorrido.
- **FR-4028**: "Aguardando resposta" MUST contar só a convocação com prazo em curso, e a data "até" MUST
  sair só dessas.
- **FR-4029**: A convocação com prazo não iniciado MUST aparecer como espécie própria, "sem comunicação
  enviada", sem data (UX-225). Nas mesmas telas, com a mesma natureza das demais providências da
  convocação: advertência no Encerrar, fato não público no relatório (D-003).
- **FR-4030**: Uma convocação sem comunicação enviada MUST NOT contar como "prazo encerrado sem
  registro", qualquer que seja o vencimento informado.

#### A5. O aviso de congelamento inviável

- **FR-4031**: O aviso de congelamento inviável da `102` MUST aparecer no topo dos recortes do sorteio só
  quando há relação a congelar pela primeira vez — recorte com inscrição projetada e relação não
  congelada — ou quando as inscrições ainda correm.
- **FR-4032**: Quando congelar hoje condenaria o sorteio e uma relação congelada admite sucessão, o aviso
  MUST aparecer dentro do bloco de sucessão daquela relação (UX-226), e MUST NOT se repetir no topo
  como frase sobre a sucessão.
- **FR-4033**: Um recorte sem inscrito MUST NOT fazer o aviso aparecer.
- **FR-4034**: A condição de inviabilidade, a data sugerida e o caminho (Retificação) MUST continuar os
  da `102` (FR-2659): muda só o lugar.

#### A6. A confirmação da ordem por pontuação

- **FR-4035**: A confirmação da emissão da ordem MUST dizer, quando há inscrições consideradas sem
  resultado vigente numa Etapa que o marco enumera, quantas estão sem resultado **em cada** Etapa
  enumerada, pelo nome publicado da Etapa (UX-227).
- **FR-4036**: Quando **nenhuma** inscrição considerada tem resultado nas Etapas enumeradas, a
  confirmação MUST dizê-lo em destaque e MUST dizer a consequência: todas ficam sem posição; quando os
  resultados forem consolidados, a ordem emitida ficará obsoleta, e sucedê-la exigirá motivo.
- **FR-4037**: A confirmação MUST agrupar os participantes sem posição pelo motivo, com a quantidade e os
  protocolos de cada grupo.
- **FR-4038**: A inscrição sem posição por eliminação MUST NOT contar como "sem resultado".
- **FR-4039**: A confirmação MUST continuar permitindo a emissão. Recusar a emissão sem resultado é
  decisão do usuário, registrada em *Decisão pendente do usuário* (D-004).

#### Limites

- **FR-4040**: Esta feature MUST NOT criar migration, tabela, coluna ou estado persistido, e MUST NOT
  mudar comando, recusa ou permissão: tudo o que ela mostra é derivado no instante da leitura.
- **FR-4041**: Esta feature MUST NOT tocar o cartão "O que fazer agora" nem o cartão "Classificação" da
  página do Edital, nem a mensagem técnica da falha de acesso à fonte do sorteio.

### Experiência

- **UX-223**: O bloco recolhido da sucessão tem por rótulo "Suceder este corte (exige motivo)", "Suceder
  esta ordem (exige motivo)", "Suceder esta apuração (exige motivo)" ou "Suceder esta relação (exige
  motivo)"; abre por teclado e toque, sem script, e o formulário dentro dele é o de sempre.
- **UX-224**: A célula da lista sem inscrito diz "Não se aplica" com a nota "nenhuma inscrição nesta
  lista", sem link; a convocação e a ocupação dizem "Não se aplica." seguido da razão.
- **UX-225**: A espécie nova diz "N convocação sem comunicação enviada" / "N convocações sem comunicação
  enviada", sem data; no resumo de vagas, "N sem comunicação enviada".
- **UX-226**: Dentro do bloco de sucessão da relação, o aviso diz que a relação nova seria congelada
  hoje e o sorteio dela recusado, a data da extração, a data a partir da qual retificar e quem retifica.
- **UX-227**: A confirmação da ordem traz a seção "Inscrições sem resultado nas Etapas deste marco", com
  a frase de destaque, uma linha "<Etapa>: N sem resultado" por Etapa e a consequência; os sem posição
  aparecem agrupados por motivo.

### Key Entities

Nenhuma entidade nova. As leituras usadas:

- **Recorte sem inscrito**: derivado das inscrições enviadas do Perfil, do fim do período de inscrições e
  da relação vigente do recorte. Não é gravado.
- **Estado da convocação**: o de `prazo.estado`, já usado pela tela da convocação.
- **Resultados por Etapa enumerada**: os Resultados vigentes que o cálculo da ordem já lê.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1210**: Nas telas do corte, da ordem, da ocupação e do sorteio, logo depois de praticar o ato e
  com ele vigente e não obsoleto, **zero** botões de sucessão estão visíveis sem abrir um bloco.
- **SC-1211**: As quatro mensagens de sucesso (corte, ordem, apuração, relação) nomeiam o recorte em
  **100%** dos casos.
- **SC-1212**: Na condução do marco do Polo Vitória do Edital 35 (sem inscrito, inscrições encerradas),
  **zero** células dizem *Falta* e **zero** gestos são oferecidos.
- **SC-1213**: Na convocação de um recorte sem corte, **zero** ocorrências da frase da faixa seguinte e do
  link para pedi-la.
- **SC-1214**: Na confirmação de Encerrar do Edital 35, a convocação sem comunicação enviada aparece como
  "sem comunicação enviada" e **não** como "aguardando resposta".
- **SC-1215**: Na tela do sorteio do 35 Cefor, com todas as relações congeladas, o aviso de
  congelamento inviável **não** é a primeira frase dos recortes.
- **SC-1216**: Na confirmação da ordem de um marco por pontuação sem nenhum resultado, cada Etapa
  enumerada aparece nomeada com a sua contagem de inscrições sem resultado.
- **SC-1217**: Em **100%** dos casos de marco por pontuação com ordem vazia emitida, a condução continua
  dizendo *Feito*, "ninguém concorreu".
- **SC-1218**: **Zero** migrations novas, e a suíte contra PostgreSQL fecha sem falha nova em relação à
  linha de base da `main`.

## Assumptions

- **O Edital 35 do banco pseudonimizado** (clone de `processo_seletivo_guia`) continua com o Polo
  Vitória sem inscrito e com uma convocação sem comunicação: é nele que as capturas de antes e depois
  são feitas. O Edital 91 (ordem sem avaliação) **não** está nesse clone; a captura de A6 sai de um
  cenário montado no banco descartável ou da suíte.
- **O texto das frases** é proposta e passa pela varredura de vocabulário antes de se fixar.
- **O nome publicado das Etapas** está no conteúdo vigente que o cálculo da ordem já lê.

## Compatibilidade com regras anteriores

| Regra | O que acontece |
|---|---|
| FR-811 e FR-814 da `049` (*Não se aplica* não conta nos totais) | **estendidas** à lista sem inscrito (FR-4020) |
| A decisão da `049` sobre a ordem vazia (*Feito*, "ninguém concorreu") | continua (FR-4023) |
| FR-2659 da `102` (a sucessão também congela) | continua; muda só o lugar do aviso (FR-4034) |
| FR-332 da `027` (a causa quando a fila esgota sem quadro) | continua, dentro do ramo com corte (FR-4025) |
| FR-269a e o estado de leitura da `019` | agora também no relatório e no Encerrar (FR-4027) |
| FR-3535 da `113` (Encerrar lê as providências do relatório) | continua: a espécie nova vem do relatório |
| FR-1082 da `058` (motivo da sucessão em área de texto) | continua, dentro do bloco recolhido |

## Decisões

### D-001 — Recolhida sempre que há ato vigente, e aberta quando o ato é obsoleto

O estudo pede a sucessão recolhida "logo depois do ato". Saber o que é "logo depois" exigiria estado (a
mensagem da sessão some no recarregamento, e a tela recarregada seria a mesma de antes). O critério
derivado é o do próprio ato: vigente e íntegro, a sucessão é exceção e fica recolhida; obsoleto, ela é
o passo esperado e vem aberta. É também o que torna a tela igual antes e depois de recarregar.

### D-002 — "Sem inscrito" é o subconjunto seguro de "congelar seria recusado"

O pedido manda usar o critério que já faz o congelamento ser recusado (`relation_would_be_empty`),
lido de `previa.recortes_do_marco` (`projetados == 0`, relação não congelada), e não a ausência de ato.
Duas condições se acrescentam, para que *Não se aplica* nunca seja dito cedo demais:

- **inscrições que não chegam mais**: período encerrado, ou não designado — o Edital que não recebe
  inscrição por este sistema (`periodo_de_inscricoes`). Com o período aberto ou por abrir, alguém
  ainda pode declarar a lista, e o próprio sorteio recusa congelar nessa hora, por outra razão;
- **sem o filtro da Etapa de habilitação**: com `qualifyingStageId`, a projeção conta só os habilitados,
  e é zero enquanto a Etapa não foi consolidada. Zero por espera não é "ninguém se inscreveu".

O resultado é um subconjunto estrito de "congelar seria recusado por universo vazio": todo recorte dito
sem inscrito teria o congelamento recusado, e nenhum recorte com inscrição a habilitar é dito sem
inscrito.

### D-003 — "Sem comunicação enviada" é espécie própria, com a natureza das outras da convocação

Somá-la a "aguardando resposta" é o defeito; somá-la a "vencida" contradiz o domínio. Ela é providência
de quem conduz (emitir a comunicação), como a vencida (registrar o desfecho), e por isso entra no
Encerrar como advertência, igual às outras duas, e no relatório como fato não público, com a mesma
regra de privacidade.

### D-004 — A6 só na apresentação

Recusar a emissão da ordem sem resultado muda o que o comando aceita, e a ordem vazia emitida é
legítima em outros casos (ninguém concorreu, pela decisão da `049` sobre a ordem vazia). A spec implementa o que a confirmação diz
e leva a recusa ao usuário, abaixo.

### D-005 — A ocupação entra junto da convocação

O pedido nomeia a condução e a convocação. A ocupação da mesma lista manda "emitir a ordem deste recorte
na classificação dele", que leva à tela do sorteio, onde não há o que fazer: é o mesmo beco, pelo mesmo
critério, e corrigi-lo custa uma frase. Fica dentro, para que as três telas digam a mesma coisa.

## Decisão pendente do usuário

### G-01 — A ordem por pontuação sem resultado nas Etapas deve ser recusada?

**Hoje**: `emitir_ordem` grava a ordem mesmo quando nenhuma inscrição tem resultado nas Etapas
enumeradas. Ela nasce com todos sem posição, fica obsoleta quando os resultados chegam, e a sucessão
exige motivo. Esta spec faz a confirmação dizer isso (FR-4035 a FR-4037), e **não** recusa.

| Opção | Efeito | Custo |
|---|---|---|
| **a. Só a apresentação** (o que esta spec entrega) | Quem confirma lê o motivo e as contagens; continua podendo emitir | Nenhum além desta spec; a ordem precoce continua possível |
| b. Recusar se **nenhuma** inscrição considerada tem resultado em alguma Etapa enumerada | Fecha o caso do Edital 91; ordem parcial continua possível | Recusa nova no domínio, com teste; a ordem vazia "ninguém concorreu" não é afetada (universo vazio) |
| c. Recusar se **alguma** inscrição considerada está sem resultado | Obriga consolidar tudo antes de ordenar | Pode travar o Edital em que uma inscrição nunca terá resultado (desistência sem registro); precisa de saída |
| d. Exigir uma declaração na confirmação ("emito sabendo que N estão sem resultado") | Mantém a possibilidade e registra a ciência no ato | Campo novo no ato ou na trilha: estado persistido novo |

**Recomendação**: **b**, numa spec própria. Ela recusa o caso que não tem uso legítimo conhecido (ordem
emitida antes de qualquer avaliação) e não toca a ordem parcial nem a vazia. Até a decisão, **a**
reduz o risco sem mudar regra.
