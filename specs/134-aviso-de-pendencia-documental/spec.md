# Feature Specification: O aviso de pendência documental por e-mail

**Feature Branch**: `claude/nostalgic-taussig-0fb16b`, sobre a `main` em `86cd0ee0`

**Created**: 2026-11-08

**Status**: Implementada em 08/11/2026, com uma migration (`avisos/0002`). PR aberto, sem merge.
Verificação em [verificacao.md](verificacao.md). As decisões têm duas origens:

- **Do usuário, em 08/11/2026**: a *1ª* à *6ª decisão*, em *Clarifications*. Não se reabrem.
- **Propostas de desenho desta spec:** D-001 a D-010, ao fim. Elas fecham o que as decisões deixaram
  aberto e estão sujeitas à revisão do PR.

**Input**: a QI-7 da `115` (aviso de pendência por e-mail), a regra do §7 do
[estudo da experiência da convocação](../../doc/estudo-experiencia-da-convocacao-2026-11-05/README.md)
(05/11/2026), a 5ª decisão daquele estudo (fora do incremento da `121`) e o cenário de Carla do
[guia dos documentos no GPS](../../doc/guia-documentos-no-gps-2026-11-06/). Repositório público: os
exemplos usam dados fictícios.

> **Faixa de identificadores.** Esta spec abre em **FR-4601**, **SC-1441** e **UX-311**. O teto foi
> medido em 08/11/2026 na `main` em `86cd0ee0`: o requisito funcional quatro mil quinhentos e
> cinquenta e nove e o critério mil quatrocentos e vinte e oito, da `133`, e o requisito de
> experiência trezentos e quatro. Há duas pastas `133` na `main`, e por isso esta é a `134`. A folga
> é a de costume. A reserva vai até o requisito quatro mil seiscentos e quarenta e o critério mil quatrocentos e cinquenta. As decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-3584 da `115`"). Uma decisão de outra feature é citada pelo assunto e pela feature,
> nunca pelo número.

---

## Por que esta feature existe

**A pendência só existe no portal, e o prazo corre do mesmo jeito.** Quando a comissão confere um
documento da convocação como *pendente*, o motivo aparece na página da convocação (FR-3584 da `115`)
e em nenhum outro lugar. A FR-3614 da `115` proibiu que a conferência disparasse mensagem, e a FR-084
da `010` admitia quatro situações de envio. Quem não volta ao portal descobre a pendência depois do
vencimento, quando a convocação já não aceita arquivo (FR-3578 da `115`) e o desfecho de não
atendimento está a um clique.

**O estudo de 05/11 fechou a política, e não a ativou.** O §7 do estudo da experiência da convocação
escreveu as regras: gesto humano em lote, um aviso por pessoa por chamada por dia, nada depois do
vencimento, do desfecho ou do reenvio, o mesmo despacho da `066`, sem reiniciar prazo. A `121` deixou
o aviso fora de propósito (5ª decisão do estudo), à espera da decisão institucional. Em 08/11 o
usuário a tomou.

### O que esta spec cobre, e o que fica fora

**Cobre:** a revisão da FR-084 da `010` para a quinta situação; o gesto *"Avisar as pessoas com
pendência nesta chamada"* na tela de condução da convocação; a seleção de quem recebe e as exclusões;
o texto da mensagem; a gravação no registro de avisos da `066` e o envio pelo despacho dela; a trilha
do gesto e de cada envio.

**Fica fora, por decisão do usuário:** aviso automático (ao registrar a pendência), lembrete de
vencimento, aviso de documento conferido ou de resultado, mudança de prazo, o *"não se aplica"* e a
concorrência concomitante.

---

## Clarifications

### Session 2026-11-08 (decisões do usuário)

- **1ª decisão — A FR-084 da `010` é revisada para uma quinta situação.** As redações anteriores
  ficam ao fim da alínea, como a `019` e a `066` fizeram. A guarda
  `backend/tests/test_situacoes_de_mensagem.py` passa a contar cinco, e a revisão datada fica numa
  constante do módulo que envia.
- **2ª decisão — O disparo é um gesto da comissão, em lote**: *"Avisar as pessoas com pendência nesta
  chamada"*, por quem pode conferir ou gerir. Não é automático. No máximo **um aviso por pessoa, por
  chamada, por dia**, e **nenhum** quando o vencimento já passou, quando a convocação já tem
  desfecho, ou quando o item já foi reenviado depois da pendência ("complementado").
- **3ª decisão — O texto traz o nome do documento**, mas os exigidos **por modalidade** (o recorte por
  `modalityId` ou `modalityCode`, como o laudo e a autodeclaração) aparecem como *"um documento da sua
  modalidade de concorrência"*. Nunca o motivo da pendência, o nome da pessoa, o CPF, a modalidade ou
  anexo. O texto diz que o prazo continua até o vencimento e traz o link da convocação. O rodapé é
  fixo: *"Este aviso não é a convocação e não altera o seu prazo."* O assunto não começa por
  "Convocação".
- **4ª decisão — Vale também na convocação por publicação** (`callForm = PUBLICATION`).
- **5ª decisão — A mesma chave `AVISOS_AOS_CANDIDATOS`** da `066`, e não uma chave própria. Ela
  continua desligada em produção até a validação de LGPD e de SPF/DKIM.
- **6ª decisão — O número da spec é `134`.**

**A 3ª decisão muda uma regra do estudo.** O §7 dizia *"sem motivo e sem nome de documento"*. O
usuário manteve o motivo fora e trouxe o nome de volta, com a ocultação dos de modalidade: o nome
diz o que fazer, e o de modalidade revelaria a cota (D-004).

---

## User Scenarios & Testing *(mandatory)*

Os exemplos usam o Edital 72/2026, fictício, com três pessoas convocadas na ampla concorrência e uma
na reserva de pessoas com deficiência.

### User Story 1 — A comissão avisa, num gesto, quem tem pendência (Priority: P1)

Carla foi convocada e enviou o comprovante de residência ilegível. A conferente o marcou como
pendente, com o motivo *"o arquivo está cortado"*. Carla não voltou ao portal.

**Por que P1**: é a razão desta feature. Sem o gesto, a pendência só existe para quem procura.

**Independent Test**: com duas pessoas com pendência e uma sem, o gesto grava dois avisos, cada um com
o nome do documento pendente da pessoa, e nenhum para a terceira; `despachar_avisos` os envia.

**Acceptance Scenarios**:

1. **Dado** um recorte com convocações em curso, comunicadas e com item pendente, **quando** quem
   pode conferir aciona *"Avisar as pessoas com pendência nesta chamada"*, **então** o sistema grava
   um aviso por pessoa e responde quantos ficaram para envio e quantos foram excluídos, por motivo.
2. **Dado** o gesto feito, **quando** a resposta volta, **então** nenhuma mensagem saiu ainda: quem
   envia é o despacho da `066`, fora da requisição.
3. **Dado** o gesto feito, **quando** se lê a trilha, **então** há um registro do gesto, com as
   contagens e sem endereço, e, depois do despacho, um registro por resultado de envio.

### User Story 2 — O aviso não insiste nem chega tarde (Priority: P1)

**Por que P1**: um aviso depois do vencimento, ou depois do desfecho, é pior que nenhum: aponta um
prazo que já não existe.

**Independent Test**: cada uma das exclusões, sozinha, tira a pessoa do gesto; o segundo gesto no
mesmo dia não grava aviso novo para quem já foi avisado.

**Acceptance Scenarios**:

1. **Dado** uma convocação com vencimento decorrido, **quando** o gesto corre, **então** ela não recebe
   aviso, e a resposta a conta como *"vencimento decorrido"*.
2. **Dado** uma convocação com desfecho, **então** ela não recebe aviso (*"desfecho registrado"*).
3. **Dado** uma pessoa cujo único item pendente já foi reenviado, **então** ela não recebe aviso
   (*"documento reenviado, aguardando conferência"*).
4. **Dado** uma pessoa com um item reenviado e outro ainda pendente, **então** o aviso nomeia só o
   pendente.
5. **Dado** uma pessoa avisada hoje nesta chamada, **quando** o gesto corre de novo, **então** ela não
   recebe outro (*"já avisada hoje"*); amanhã, se a pendência continuar, pode receber.
6. **Dado** uma convocação ainda não comunicada, **então** ela não recebe aviso (*"convocação ainda não
   comunicada"*).
7. **Dado** que ninguém do recorte pode receber, **quando** o gesto corre, **então** ele é recusado
   com explicação e nada é gravado.

### User Story 3 — O texto diz o que fazer e não revela nada (Priority: P1)

**Por que P1**: o motivo da pendência e o documento de modalidade podem revelar saúde, renda ou cota.

**Independent Test**: o aviso de quem tem o laudo pendente diz *"um documento da sua modalidade de
concorrência"*, e não o nome do laudo, nem o motivo, nem o nome da pessoa.

**Acceptance Scenarios**:

1. **Dado** um item pendente sem recorte de modalidade, **então** o aviso o cita pelo nome publicado.
2. **Dado** um item pendente exigido por `modalityId` ou `modalityCode`, **então** o aviso diz *"um
   documento da sua modalidade de concorrência"*.
3. **Dado** qualquer aviso, **então** o texto não contém o motivo da pendência, o nome, o CPF, a
   modalidade, nem anexo; o assunto não começa por "Convocação"; o rodapé diz *"Este aviso não é a
   convocação e não altera o seu prazo."*; e o corpo traz o vencimento e o link da convocação.

### User Story 4 — Também na convocação por publicação (Priority: P2)

**Acceptance Scenarios**:

1. **Dado** um Perfil que convoca por publicação, com a publicação registrada e um item pendente,
   **quando** o gesto corre, **então** o aviso é gravado como na mensagem individual.

### User Story 5 — Com a chave desligada, nada (Priority: P2)

**Acceptance Scenarios**:

1. **Dado** `AVISOS_AOS_CANDIDATOS` desligada, **então** a tela não oferece o gesto, o POST é recusado
   com `aviso_envio_desabilitado`, e nada é gravado.

### Edge Cases

- **Convocação sem vencimento** (o Edital não publicou prazo): a pessoa pode ser avisada, e o texto diz
  que o prazo continua o da convocação, sem data (D-007).
- **Pessoa sem endereço**: não recebe, e conta como *"sem endereço"* na resposta (FR-4608).
- **Convocação corrigida por sucessão no mesmo dia** do aviso: o limite é da chamada (a raiz), e não da
  convocação vigente; a sucessora não abre um segundo aviso no mesmo dia (D-003).
- **Dois gestos simultâneos**: serializam pela trava do Processo; o segundo encontra o primeiro gravado
  e não duplica (FR-4611).
- **Duplo clique**: a chave de idempotência devolve o resultado do primeiro (FR-4611).
- **Processo encerrado ou cancelado**: o gesto é recusado (FR-1244 da `066`).
- **Item de *"não se aplica"* pelo recorte**: não é pedido, não é pendente, e não entra no aviso.
- **Reenvio pela tela da `066`**: o aviso de pendência não se reenvia por ela; o caminho é um novo gesto,
  no dia seguinte (D-008).

---

## Requirements *(mandatory)*

### Functional Requirements

#### A. A quinta situação

- **FR-4601**: A FR-084 da `010` MUST ser revisada para admitir uma quinta situação: o **aviso de
  pendência documental**, por gesto de quem pode conferir, sem efeito sobre prazo, situação ou
  direito. As redações anteriores MUST ficar ao fim da alínea. A FR-3614 da `115` MUST ser revista na
  mesma medida, com a redação anterior preservada.
- **FR-4602**: A guarda `backend/tests/test_situacoes_de_mensagem.py` MUST declarar cinco situações e
  conferir a data da revisão, declarada como constante no módulo que envia, contra a FR-084 escrita.
  O envio MUST continuar num módulo só, o despacho da `066`.

#### B. O gesto

- **FR-4603**: A tela de condução da convocação de um recorte (Perfil, marco e lista) MUST oferecer o
  gesto *"Avisar as pessoas com pendência nesta chamada"* a quem pode conferir os documentos daquele
  Perfil (FR-3595 da `115`), o que inclui quem gere a comissão. Quem não pode MUST receber a recusa de
  inexistente.
- **FR-4604**: O gesto MUST ser só humano: registrar, mudar ou desfazer uma pendência MUST NOT gravar
  aviso, e nada MUST gravar aviso de pendência por relógio ou por vencimento próximo.
- **FR-4605**: Antes do gesto, a tela MUST mostrar quantas pessoas o gesto alcançaria e quantas ficam
  de fora, por motivo, lidas da mesma regra que o gesto aplica.
- **FR-4606**: O gesto MUST alcançar a pessoa cuja convocação **vigente** do recorte, ao mesmo tempo:
  - não tem desfecho;
  - tem a comunicação emitida (o prazo começou a correr);
  - não tem o vencimento decorrido, pela mesma leitura que admite o não atendimento (FR-3578 da
    `115`);
  - tem ao menos um item da lista no estado *pendente* (conferência vigente pendente, sem
    apresentação posterior a ela);
  - não foi avisada de pendência **nesta chamada** no mesmo dia local da instalação.
- **FR-4607**: Item *"complementado"* (reenviado depois da pendência, aguardando conferência) MUST NOT
  entrar no aviso. A pessoa cujos itens pendentes foram todos complementados MUST ficar de fora.
- **FR-4608**: A pessoa sem endereço MUST ficar de fora, contada à parte.
- **FR-4609**: Sem nenhuma pessoa alcançada, o gesto MUST ser recusado com
  `aviso_sem_pendencia_a_avisar` e MUST NOT gravar nada.
- **FR-4610**: O gesto MUST ser recusado com `aviso_envio_desabilitado` quando a chave
  `AVISOS_AOS_CANDIDATOS` estiver desligada (FR-1282 da `066`), e com
  `aviso_processo_em_estado_final` com o Processo encerrado ou cancelado (FR-1244 da `066`).
- **FR-4611**: O gesto MUST correr sob a trava do Processo e com chave de idempotência, de modo que
  dois gestos simultâneos não avisem a mesma pessoa duas vezes no dia e o duplo clique devolva o
  resultado do primeiro.
- **FR-4612**: O gesto MUST valer igualmente nas convocações por mensagem individual e por publicação
  (`callForm = PUBLICATION`).

#### C. O texto

- **FR-4613**: O assunto MUST ser *"‹instituição› · Edital ‹número›/‹ano›: há documento da sua
  convocação para revisar"* e MUST NOT começar por "Convocação".
- **FR-4614**: O corpo MUST nomear cada item pendente pelo nome publicado do requisito, na ordem da
  lista. O item exigido por modalidade (recorte por `modalityId` ou `modalityCode`) MUST aparecer
  como *"um documento da sua modalidade de concorrência"*, e dois ou mais como *"N documentos da sua
  modalidade de concorrência"*, numa linha só.
- **FR-4615**: O corpo MUST dizer que o prazo continua até o vencimento da convocação vigente, com o
  dia da semana, a data e a hora no fuso da instalação (FR-3873 da `121`), e MUST trazer o link da
  convocação, o mesmo da mensagem da convocação (FR-3883 da `121`).
- **FR-4616**: O corpo e o assunto MUST NOT conter o motivo da pendência, o nome da pessoa, o CPF, o
  protocolo, a modalidade nem o nome dela, e a mensagem MUST NOT ter anexo.
- **FR-4617**: A mensagem MUST terminar num rodapé fixo, não editável, que começa por *"Este aviso não
  é a convocação e não altera o seu prazo."*, diz com quem falar e quem assina, pela unidade do Edital,
  e que a mensagem é automática.

#### D. O registro e o envio

- **FR-4618**: Cada pessoa alcançada MUST gerar um aviso da `066` de origem `PENDENCIA`, com o texto
  final congelado e um destinatário, apontando a convocação vigente. O aviso de pendência MUST NOT
  gravar `ComunicacaoEmitida`, MUST NOT criar nem mover prazo, e MUST NOT alterar a convocação, a
  lista, a conferência ou o desfecho.
- **FR-4619**: O envio MUST ser o do despacho da `066` (`manage.py despachar_avisos`): fila,
  tentativa registrada antes da chamada ao servidor (FR-1266 da `066`), resultado indeterminado que
  nunca se reenvia sozinho (FR-1267 da `066`), limite por minuto, janela de despacho (FR-1283 da
  `066`) e um destinatário por mensagem (FR-1271 da `066`). O gesto MUST NOT enviar dentro da
  requisição (FR-1265 da `066`).
- **FR-4620**: A trilha MUST registrar o gesto — recorte, autor, instante, quantos avisos e quantas
  exclusões por motivo —, sem endereço nem nome (FR-1278 da `066`).
- **FR-4621**: O despacho MUST registrar na trilha cada resultado de tentativa de um aviso de
  pendência — o aviso, o número da tentativa e o resultado —, sem endereço nem nome (FR-1279 da
  `066`).
- **FR-4622**: O aviso de pendência MUST aparecer no histórico de avisos do Edital como *"Pendência
  documental"*, e a interrupção da `066` MUST valer para ele. O reenvio da `066` MUST ser recusado
  para ele com `aviso_de_pendencia_sem_reenvio`.

### Requisitos de experiência

- **UX-311**: A seção do gesto fica na tela de condução, abaixo das chamadas publicadas, e diz, antes
  do botão, que o aviso **não** muda o prazo e **não** é a convocação.
- **UX-312**: A resposta do gesto nomeia o ato praticado (*"N avisos de pendência registrados para
  envio"*) e as exclusões por motivo, e não "deu certo" (o molde da tela de condução da `019`).
- **UX-313**: Com a chave desligada, a seção diz *"envio de avisos desabilitado nesta instalação"*, a
  mesma frase das chamadas publicadas da `066`, e não oferece botão.

### Key Entities

- **Aviso de pendência** — um `Aviso` da `066` com origem `PENDENCIA`, sem publicação citada, sem
  natureza e sem referência de publicação; o texto final é da pessoa.
- **Destinatário** — o `DestinatarioDoAviso` da `066`, com a inscrição, a convocação vigente e o
  endereço congelado.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1441**: Em teste de integração, o gesto grava exatamente um aviso por pessoa alcançada e
  nenhum para cada uma das quatro exclusões da 2ª decisão e a da comunicação não emitida.
- **SC-1442**: Em teste de integração, um segundo gesto no mesmo dia não grava aviso para quem já foi
  avisado nesta chamada, e um gesto no dia seguinte grava.
- **SC-1443**: Em teste de integração, nenhum aviso de pendência contém o motivo, o nome, o CPF, o
  protocolo ou o nome da modalidade, e o do documento de modalidade não contém o nome dele.
- **SC-1444**: Em teste de integração, o gesto vale na convocação por publicação.
- **SC-1445**: Com a chave desligada, zero avisos gravados e zero mensagens enviadas.
- **SC-1446**: A guarda da FR-084 conta cinco situações e confere a data da revisão da `134`.
- **SC-1447**: Zero `ComunicacaoEmitida` e zero alterações de vencimento produzidas pelo gesto ou pelo
  despacho do aviso de pendência.
- **SC-1448**: Uma migration só, que muda duas *constraints* da tabela de avisos; zero tabelas e zero
  colunas novas; o total de tabelas append-only protegidas não muda.

---

## Assumptions

- O dia do limite é o dia local da instalação (`TIME_ZONE`), e não 24 horas corridas: *"um por dia"* é
  como a comissão e a pessoa leem.
- O link da convocação é o da `121`: sem sessão, leva ao acesso, e depois do código à convocação.
- O nome publicado do requisito é texto do Edital, público; ele não é dado pessoal. O de modalidade
  é ocultado não pelo nome em si, mas porque ele, endereçado a uma pessoa, diz a modalidade dela.

## Proteção de dados (LGPD)

- **O que vai no e-mail**: o número do Edital, o nome publicado dos documentos pendentes que não são de
  modalidade, a contagem dos de modalidade, o vencimento e o link. Nada que identifique a pessoa além
  do endereço para onde vai.
- **O que fica no portal**: o motivo da pendência (FR-3584 da `115`) e o nome dos documentos de
  modalidade.
- **O que a trilha guarda**: contagens, identificadores de aviso e resultados. O endereço fica só no
  destinatário do aviso, como na `066`.
- **A chave** continua desligada em produção até a validação de LGPD e de SPF/DKIM (5ª decisão).

## Compatibilidade com regras anteriores

| Regra | Efeito |
|---|---|
| **FR-084 da `010`** | Revisada: cinco situações (FR-4601) |
| **FR-3614 da `115`** | Revista: a conferência continua sem disparar mensagem; o aviso é gesto à parte (FR-4604) |
| **FR-3584 da `115`** | Sem mudança: o motivo continua só no portal (FR-4616) |
| **FR-3618 da `115`** | Sem mudança: dar mais prazo continua sendo corrigir a convocação (FR-4618) |
| **FR-1241 da `066`** | Sem mudança para as origens dela. O aviso de pendência aponta um ato que existe: a convocação comunicada (FR-4606) |
| **FR-1265 a FR-1283 da `066`** | Valem para a origem nova (FR-4619) |
| **`121`** | O mesmo link e a mesma apresentação do prazo (FR-4615) |

## Revisões de requisitos anteriores

- **FR-084 da `010`** — revisada pela `134` em 2026-11-08 (1ª decisão).
- **FR-3614 da `115`** — revista pela `134` em 2026-11-08.

---

## Decisões

### D-001 — "Nesta chamada" é o recorte da tela de condução

*Proposta de desenho.* O gesto mora na tela de condução, que é a de um recorte (Perfil, marco e
lista), e alcança as convocações vigentes dele. É o mesmo alcance dos gestos da `050` na mesma tela.
Por publicação, uma referência publicada também seria "uma chamada"; na mensagem individual, não há
lote. O recorte vale para as duas formas (4ª decisão).

### D-002 — Um aviso da `066` por pessoa, e não um por gesto

*Proposta de desenho.* O aviso da `066` guarda o texto final (o que saiu), e o texto do aviso de
pendência é de cada pessoa: os documentos pendentes mudam. Um aviso por pessoa mantém a regra sem
coluna nova. O gesto se reconstrói pela trilha, que lista os avisos que ele gravou.

### D-003 — O limite é da chamada da pessoa, pela raiz

*Proposta de desenho.* "Por chamada" é a chamada da pessoa: a raiz da convocação, dona da lista
(a decisão da `115` de que a lista pertence à chamada). A sucessora que corrige vencimento não é
chamada nova e não abre outro aviso no mesmo dia. A pessoa chamada de novo depois de reclassificada
tem outra raiz, e outra chamada.

### D-004 — O nome do documento, e o de modalidade como contagem

*Da 3ª decisão.* "Um documento da sua modalidade de concorrência", e "N documentos" quando há mais de
um, numa linha só. Repetir a frase N vezes diria o mesmo com mais ruído.

### D-005 — A comunicação não emitida também fica de fora

*Proposta de desenho.* Sem a comunicação, a convocação ainda não foi dirigida à pessoa, e o prazo não
corre. Um aviso ali seria a primeira notícia da convocação, chegando por mensagem que não é o ato.

### D-006 — Sem endereço, sem aviso gravado

*Proposta de desenho.* A `066` grava o universo inteiro do ato, com quem não recebe. O aviso de
pendência não tem universo publicado: só a contagem fica na trilha do gesto.

### D-007 — Convocação sem vencimento

*Proposta de desenho.* O Edital que não publicou prazo não tem vencimento a dizer. O texto diz que *"o
prazo continua o da sua convocação"*, sem data, em vez de excluir a pessoa: a pendência ainda pede
ação dela.

### D-008 — Sem reenvio pela tela da `066`

*Proposta de desenho.* O reenvio da `066` recompõe o texto do ato publicado, e o aviso de pendência
não tem ato publicado. A falha se resolve com um novo gesto no dia seguinte, que relê o que continua
pendente. A interrupção vale como na `066`.

### D-009 — A trilha de cada envio fica no despacho, e só para a origem nova

*Proposta de desenho.* A `066` registra o envio nas tabelas de tentativa e resultado, que são a
prova. A 2ª decisão pede também a trilha de cada envio, e o despacho a grava para a origem
`PENDENCIA` como um evento do sistema (`sistema:despacho-de-avisos`), sem endereço. As origens da
`066` ficam como estão: trilha nova nelas mudaria o que os testes delas contam.

### D-010 — A visão do aviso de pendência na `066` é de quem gere

*Proposta de desenho.* O gesto é de quem confere, mas o histórico e a interrupção da `066` seguem a
porta dela para a chamada: a gestão da comissão. Quem só confere vê, na tela de condução, o que o
gesto gravou.

## Pendências do usuário

- **Revisão do PR** (D-001 a D-010).
- **A validação de LGPD e de SPF/DKIM** antes de ligar a chave em produção (5ª decisão).
