# Feature Specification: A data de nascimento entra no cadastro do candidato

**Feature Branch**: `claude/gps-checklist-validation-66c108`, nascida da `main` em `3afb6702` (o merge
do #585)

**Created**: 2026-11-17

**Status**: Especificada. As três perguntas foram decididas pelo usuário em 17/11 (D-001 a D-003).

**Input**: a decisão da reunião de 17/11/2026 sobre o primeiro Edital em produção, registrada no
checklist de validação (tarefa T10, decisão D01 da planilha): *"pacificada a questão da gente incluir
a data de nascimento como elemento obrigatório pra todo e qualquer cadastro"*. A razão dada na
reunião: com CPF e data de nascimento, a equipe consegue conferir manualmente no site da Receita
Federal, num caso excepcional, se nome, CPF e nascimento correspondem. Hoje isso é impossível, porque
o dado não é capturado.

> **Faixa de identificadores.** Esta spec abre em **FR-8300**, **SC-2900** e **UX-1000**, e reserva até
> o requisito oito mil trezentos e quarenta e nove, o critério dois mil novecentos e dezenove e o
> requisito de experiência mil e dezenove. Os tetos medidos em 17/11/2026, na `main` e em todas as
> worktrees, eram o requisito oito mil duzentos e trinta e dois, o critério dois mil oitocentos e
> cinquenta e o requisito de experiência novecentos e setenta e seis. As decisões desta spec recomeçam do número um.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-005 da `010`"). Uma decisão de outra feature é citada pelo assunto e pela feature.

---

## Por que esta feature existe

O cadastro do candidato foi desenhado para ter o mínimo de atrito: e-mail com código, e depois nome
completo e CPF, pedidos uma vez, na primeira inscrição (a FR-004 e a FR-005 da `010`). Isso deu
certo, e esta spec não o desfaz: acrescenta **um** campo ao mesmo momento, e não uma etapa nova.

O que falta hoje é um segundo dado que, junto do CPF, identifique a pessoa fora do sistema. O CPF
sozinho é só um número que a pessoa declarou (a FR-007 da `010`): duas identidades podem declarar o
mesmo, e o sistema aceita as duas de propósito (a FR-064 da `010`). Com a data de nascimento ao lado,
a equipe passa a ter o que a Receita pede para confirmar um CPF, e pode resolver uma dúvida sem
precisar pedir documento ao candidato.

A data de nascimento já é pedida hoje em dois lugares, e nenhum serve a essa finalidade: como fato
declarado de um Perfil, quando o Edital o configura para desempate por idade, e no requerimento de
matrícula, só para quem chega à formalização.

### O que esta spec cobre, e o que fica fora

| Cobre | Fica fora, e por quê |
|---|---|
| Pedir a data de nascimento na tela "Seus dados", junto do nome e do CPF, a todo candidato | consulta automática à Receita Federal: não há acesso, e a conferência é manual e excepcional |
| Pedir a data a quem já tem cadastro sem ela, na próxima vez que for se inscrever | recuperação de acesso ou troca de e-mail: é decisão separada (D02 da planilha), e esta spec proíbe usar a data como prova de identidade |
| Validar a data informada | idade mínima ou máxima para se inscrever: é requisito de cada Edital, e não do cadastro |
| Levar a data para a inscrição, pela mesma regra do nome e do CPF | alterar inscrição já enviada, ou preencher retroativamente inscrições antigas |
| Mostrar CPF completo e data à equipe por um ato de conferência com motivo e trilha (D-002) | assinalar CPFs coincidentes com datas diferentes: possível depois, não pedido |
| Preencher o requerimento de matrícula com a data do cadastro (D-003) | preencher o fato declarado "data de nascimento" do Perfil (D-003) |

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Candidato novo informa a data junto do nome e do CPF (Priority: P1)

Uma pessoa entra pela primeira vez, a caminho de uma vaga, e o sistema pede os dados do cadastro. Ela
informa nome completo, CPF e data de nascimento na mesma tela, e segue para a inscrição.

**Why this priority**: é o caso de quase todos os candidatos do primeiro Edital. Sem ele, a decisão
da reunião não se cumpre.

**Independent Test**: com um e-mail novo, abrir uma vaga, chegar a "Seus dados", informar os três
campos e ver a inscrição aberta. Repetir deixando a data em branco e ver a recusa.

**Acceptance Scenarios**:

1. **Given** um candidato novo a caminho de uma vaga, **When** ele chega a "Seus dados", **Then** a tela
   pede nome completo, CPF e data de nascimento, e os três são obrigatórios.
2. **Given** a data em branco, **When** ele tenta guardar, **Then** o sistema recusa e diz que a data de
   nascimento é obrigatória, sem apagar o que ele já digitou nos outros campos.
3. **Given** uma data impossível ou futura, **When** ele tenta guardar, **Then** o sistema recusa e diz
   o que conferir.
4. **Given** os três campos válidos, **When** ele guarda, **Then** volta à vaga que estava abrindo, como
   já acontece hoje.

---

### User Story 2 - Quem já tem cadastro informa a data na próxima inscrição (Priority: P1)

Uma pessoa que se cadastrou antes desta mudança abre uma vaga. O sistema percebe que falta a data de
nascimento e a pede uma vez, antes de seguir. Nome e CPF já estão lá e não são pedidos de novo.

**Why this priority**: sem isso, a regra "todo cadastro" valeria só para quem chegou depois, e a
equipe não saberia quais cadastros têm o dado.

**Independent Test**: com uma identidade que tem nome e CPF e não tem data, abrir uma vaga e ver o
pedido da data, com nome e CPF já preenchidos.

**Acceptance Scenarios**:

1. **Given** um cadastro antigo sem data, **When** a pessoa abre uma vaga, **Then** o sistema leva a
   "Seus dados" com nome e CPF preenchidos e pede só o que falta.
2. **Given** um cadastro antigo sem data e um rascunho de inscrição aberto, **When** a pessoa tenta
   enviar a inscrição, **Then** o sistema não envia, diz que falta a data de nascimento e leva até onde
   informá-la, e depois devolve ao envio.
3. **Given** um cadastro antigo sem data e uma inscrição já enviada, **When** nada mais acontece,
   **Then** a inscrição enviada continua como está: ninguém a altera nem pede a data por causa dela.

---

### User Story 3 - A equipe confere CPF e nascimento num caso de dúvida (Priority: P2)

Surge uma dúvida sobre quem é o titular de uma inscrição: por exemplo, dois cadastros com o mesmo
CPF, que a consulta já assinala (a FR-065 da `010`). Uma pessoa da equipe autorizada vê o CPF e a data
de nascimento declarados e confere, fora do sistema, no site da Receita.

**Why this priority**: é a finalidade do dado. Fica em P2 porque o caso é excepcional, e o primeiro
Edital pode funcionar sem ele enquanto o dado estiver guardado.

**Independent Test**: com uma inscrição enviada, entrar como a pessoa autorizada, pedir a conferência
da identidade informando o motivo, e ver CPF completo e data. Conferir que a trilha registrou o ato.
Entrar com outro papel e não encontrar a ação.

**Acceptance Scenarios**:

1. **Given** uma inscrição enviada com data de nascimento, **When** a pessoa autorizada abre o detalhe
   da inscrição, **Then** vê o CPF mascarado, como hoje, e uma ação para conferir a identidade.
2. **Given** a ação de conferir, **When** a pessoa informa o motivo e confirma, **Then** vê o CPF
   completo e a data como o candidato os declarou no envio, e a trilha registra quem, quando, qual
   inscrição e o motivo — sem os valores.
3. **Given** a ação de conferir, **When** a pessoa tenta confirmar sem motivo, **Then** o sistema recusa
   e nada é revelado.
4. **Given** uma pessoa sem a permissão, **When** consulta a mesma inscrição, **Then** não vê a ação.
5. **Given** uma inscrição enviada antes desta feature, **When** a pessoa confere a identidade, **Then**
   vê o CPF completo e o aviso de que a data não foi informada naquela inscrição.

---

### Edge Cases

- **Data de quem nasceu num dia que não existe**, como 31/02 ou 29/02 em ano não bissexto: recusada
  como data impossível.
- **Data no futuro, ou hoje**: recusada. Ninguém se inscreve no dia em que nasce.
- **Data muito antiga**: acima de 120 anos de idade é tratado como erro de digitação e recusado, com
  mensagem que pede para conferir o ano.
- **Pessoa menor de idade**: aceita. O cadastro não decide quem pode se inscrever; o Edital decide.
- **Ano com dois dígitos** ("01/02/03"): não é aceito. A tela pede o ano com quatro dígitos, porque
  "03" pode ser 1903 ou 2003.
- **Rascunho aberto quando a pessoa corrige a data**: o rascunho acompanha a correção, como já
  acontece com o nome (a FR-014 da `010`).
- **Inscrição enviada e depois a data corrigida no cadastro**: a inscrição enviada guarda a data do dia
  do envio, como guarda o nome e o CPF.
- **Fato declarado "data de nascimento" num Perfil**: continua existindo e continua sendo pedido onde o
  Edital o configurou. Esta spec não o tira nem o preenche sozinho (D-003).
- **Alguém que sabe CPF e data de nascimento de outra pessoa**: não ganha acesso a nada. A entrada
  continua sendo só pelo código enviado ao e-mail.

## Requirements *(mandatory)*

### Functional Requirements

#### O campo e quando ele é pedido

- **FR-8300**: O cadastro do candidato DEVE ter data de nascimento, ao lado do nome completo e do CPF,
  e os três DEVEM ser obrigatórios para abrir uma inscrição.
- **FR-8301**: A data DEVE ser pedida na mesma tela e no mesmo momento em que o nome e o CPF já são
  pedidos hoje: na primeira vez que a pessoa vai se inscrever, e não ao entrar no sistema (a FR-005
  da `010` continua valendo).
- **FR-8302**: Quem já tem cadastro sem data DEVE ser levado a informá-la na próxima vez que abrir uma
  vaga, com nome e CPF já preenchidos, sem que estes sejam pedidos de novo.
- **FR-8303**: O envio de uma inscrição DEVE ser recusado enquanto o cadastro não tiver data de
  nascimento, e a recusa DEVE levar a pessoa até onde informá-la e trazê-la de volta ao envio.
- **FR-8304**: Inscrições já enviadas antes desta mudança NÃO PODEM ser alteradas por causa dela, nem
  bloquear coisa alguma por não terem a data.

#### A validação

- **FR-8305**: A data DEVE ser uma data de calendário que existe, com ano de quatro dígitos, anterior
  ao dia de hoje e que não resulte em idade acima de 120 anos.
- **FR-8306**: A data NÃO PODE ser recusada por idade mínima. Quem pode se inscrever é decidido pelo
  Edital, e não pelo cadastro.
- **FR-8307**: Cada recusa DEVE dizer o que está errado e o que conferir, e NÃO PODE apagar o que a
  pessoa digitou nos outros campos.

#### Correção e inscrição

- **FR-8308**: A data informada DEVE alimentar a inscrição pela mesma regra do nome e do CPF (a FR-014
  da `010`): enquanto a inscrição for rascunho, acompanha o cadastro; no envio, congela na inscrição.
- **FR-8309**: O candidato DEVE poder corrigir a própria data de nascimento enquanto o cadastro não
  tiver nenhuma inscrição enviada. A partir da primeira inscrição enviada, a data congela junto do
  CPF, e corrigi-la passa a ser ato institucional, fora desta feature (D-001; a FR-008 da `010`). Quem
  ainda não tem data, mesmo com inscrição enviada antes desta feature, DEVE poder informá-la uma vez;
  informada, ela congela.

#### Uso do dado

- **FR-8310**: A data de nascimento NÃO PODE ser usada como prova de identidade em caminho nenhum do
  sistema: nem para entrar, nem para recuperar acesso, nem para trocar ou acrescentar e-mail, nem para
  decidir a quem pertence um cadastro. Quem conhece CPF e data de outra pessoa NÃO PODE, por isso,
  alcançar nada que seja dela.
- **FR-8311**: A data NÃO PODE aparecer em área pública, em endereço de página, em publicação, nem em
  registro técnico ou de auditoria — pelo mesmo cuidado que a FR-009 da `010` tem com o CPF.
- **FR-8312**: O detalhe de uma inscrição enviada DEVE oferecer, a quem já tem a permissão de abrir esse
  detalhe, uma ação de conferir a identidade, que revela o CPF completo e a data de nascimento
  congelados na inscrição (D-002). Fora dessa ação, o CPF continua mascarado e a data não aparece.
- **FR-8315**: A conferência DEVE exigir um motivo escrito, e NÃO PODE revelar nada sem ele.
- **FR-8316**: Cada conferência DEVE ficar na trilha com quem conferiu, quando, qual inscrição e o
  motivo, e NÃO PODE gravar o CPF nem a data (FR-8311).
- **FR-8317**: Quem não tem a permissão de abrir o detalhe da inscrição NÃO PODE ver a ação nem
  alcançar a conferência por endereço montado à mão.
- **FR-8313**: Ao abrir o requerimento de matrícula, o campo de data de nascimento DEVE vir preenchido
  com a data do cadastro, se o candidato ainda não o tiver preenchido ali, e o candidato DEVE poder
  alterá-lo no requerimento sem que isso mude o cadastro (D-003).
- **FR-8318**: O fato declarado "data de nascimento" de um Perfil NÃO PODE ser preenchido a partir do
  cadastro: ele continua pedido na inscrição, onde o Edital o configurou (D-003).
- **FR-8314**: A tela "Seus dados" DEVE dizer em uma frase por que a data é pedida (para a instituição
  poder confirmar a identidade em caso de dúvida), como pede a avaliação de finalidade da LGPD.

### Requisitos de experiência

- **UX-1000**: O campo DEVE aceitar a data digitada no formato dia/mês/ano e o preenchimento automático
  do navegador, e DEVE funcionar no celular sem calendário que obrigue a rolar décadas.
- **UX-1001**: O pedido a quem já tem cadastro (FR-8302) DEVE ser uma tela só, com nome e CPF à vista e
  apenas a data a preencher, e NÃO PODE parecer um recadastro.

### Key Entities

- **Identidade do candidato**: ganha a data de nascimento declarada, ao lado de nome e CPF. Declarada,
  nunca provada, como o CPF.
- **Inscrição**: guarda a data de nascimento do dia do envio, como guarda nome e CPF. Inscrições
  enviadas antes desta feature ficam sem ela.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2900**: Toda inscrição enviada depois da implantação tem data de nascimento: zero inscrições
  enviadas sem ela.
- **SC-2901**: Um candidato novo informa nome, CPF e data numa tela só, sem passo novo na jornada: o
  número de telas entre abrir a vaga e começar a inscrição não aumenta.
- **SC-2902**: Um candidato com cadastro antigo informa só a data, em uma tela, sem redigitar nome e CPF.
- **SC-2903**: Nenhuma página pública, publicação ou registro técnico contém a data de nascimento de um
  candidato.
- **SC-2904**: Nenhum caminho de acesso, recuperação ou troca de e-mail aceita CPF e data de nascimento
  como prova de quem a pessoa é.
- **SC-2905**: Na revisão do checklist do TMD, os itens 3.04 e 3.03 ficam "Conforme" nas duas passadas.
- **SC-2906**: Toda conferência de identidade feita na equipe aparece na trilha com motivo, e nenhuma
  revelação acontece sem registro.
- **SC-2907**: Um candidato convocado para a matrícula encontra a data de nascimento já preenchida no
  requerimento.

## Assumptions

- A data é **declarada**, como o CPF. O sistema confere que ela é uma data possível, e não que é a data
  verdadeira; a conferência na Receita é manual, fora do sistema, e só em caso de dúvida.
- O comprovante de inscrição não passa a mostrar a data. Ele já identifica a pessoa por nome e CPF, e
  acrescentar dado pessoal ao papel que circula vai contra a minimização (Princípio III).
- A recusa por idade acima de 120 anos é proteção contra erro de digitação, e não regra de negócio.
- Inscrições já enviadas não recebem a data retroativamente: a inscrição enviada é ato, e o que ela
  guarda é o que constava no dia.
- Esta spec não muda quem vê o CPF completo: hoje a equipe vê o CPF mascarado na consulta das
  inscrições, e a planilha de matrícula leva o CPF completo à secretaria. A conferência (D-002) é o
  único lugar novo onde o CPF completo aparece, e só por ato com motivo.

## Decisões

### D-001 — A data congela junto do CPF

Decidida pelo usuário em 17/11. O candidato corrige a data à vontade até enviar a primeira
inscrição; depois ela congela com o CPF. Razão: a data existe para conferir o CPF, e os dois
precisam andar juntos — corrigir um sem o outro desfaria a conferência. Alternativa recusada:
corrigível sempre, como o nome.

### D-002 — A equipe vê por um ato de conferência, com motivo e trilha

Decidida pelo usuário em 17/11. Quem já abre o detalhe da inscrição pede a conferência, escreve o
motivo, e vê CPF completo e data. Razão: o uso é excepcional, e a minimização (Princípio III) pede que
o dado não fique à vista o tempo todo; o motivo e a trilha mostram depois quem viu e por quê.
Alternativas recusadas: só guardar o dado agora e deixar a tela para depois (a finalidade não se
cumpriria no primeiro Edital), e mostrar sempre (expõe mais do que o caso pede).

### D-003 — O requerimento vem preenchido; o fato declarado do Perfil, não

Decidida pelo usuário em 17/11. O requerimento de matrícula pede a data de novo hoje, e passa a
vir com a do cadastro, alterável ali. O fato declarado "data de nascimento" do Perfil continua
pedido na inscrição. Razão: o fato entra na classificação e é ato da inscrição; preenchê-lo sozinho
mudaria a regra do desempate sem que o Edital dissesse. Alternativas recusadas: preencher os dois, e
não preencher nenhum.
