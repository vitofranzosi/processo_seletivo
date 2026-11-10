# Feature Specification: A ordem sucessora e o corte esperam a avaliação do reabilitado

**Feature Branch**: `claude/141-sucessora-espera-reabilitado-af020a`, sobre a `main` em `4ae78556`

**Created**: 2026-11-10

**Status**: Draft.

**Nenhuma regra de domínio nova.** Esta spec corrige a derivação do andamento da `127`, que o Centro
de Controle da `136` mostra. Não há migration, tabela, coluna, permissão, estado persistido nem
mudança no que um comando aceita ou recusa.

**Input**: *"A ordem sucessora e o corte esperam a avaliação do reabilitado (achado F-2 do estudo de
continuidade operacional de 10/11). Correção na derivação: com a ordem obsoleta e Etapa que ela lê
por fazer, a sucessora não é providência; o corte não é providência enquanto houver reingresso
pendente no marco, pelo predicado da publicação; a Etapa governada já espera o corte; opcionalmente
a tela do corte avisa do reingresso pendente. O serviço não muda: a ordem parcial continua aceita
(128). Testes: a cadeia inteira em integração, e o caso legítimo de correção de nota sem reabilitar,
que continua oferecendo a sucessora na hora."*

> **Faixa de identificadores.** Esta spec usa:
>
> - os requisitos funcionais de quatro mil oitocentos e trinta a quatro mil oitocentos e cinquenta e
>   nove;
> - os critérios de mil quinhentos e dez a mil quinhentos e dezenove;
> - as regras de experiência de trezentos e quarenta a trezentos e quarenta e nove.
>
> Os números não usados ficam livres. As decisões reiniciam em `D-001`.
>
> A faixa vem depois das reservadas pelas duas sessões irmãs que correm em paralelo: a `139` (até o
> requisito quatro mil setecentos e noventa e nove) e a `140` (até quatro mil oitocentos e vinte e
> nove). O teto medido nas `specs/` da `main` em 10/11 era o requisito quatro mil setecentos e
> quarenta e oito, o critério mil quatrocentos e oitenta e a regra de experiência trezentos e
> dezoito.
>
> **Como esta spec cita outras.**
> - Requisito de outra feature: pelo identificador e pela feature ("a FR-4068 da `127`").
> - Decisão de outra feature: pelo assunto e pela feature.
>
> **Origem.** O estudo de continuidade operacional do GPS, de 10/11/2026
> (`doc/estudo-continuidade-operacional-2026-11-10/`), e a triagem que o seguiu
> (`07-triagem-f1-f3.md`, seção 2, PR #446). A triagem classificou o F-2 como **falha confirmada na
> derivação**, e o usuário priorizou a correção.

## Por que esta feature existe

No C08 dos cenários de treinamento (`134`), o candidato 08 é eliminado na Prova objetiva (5,0, com
mínima 6,0). Ele recorre, e o recurso é deferido: a nota vai a 6,0, e ele volta ao universo do marco.
Falta a Análise de títulos dele.

Daí em diante, o Centro conduz o operador por quatro atos, e três deles nascem para ser sucedidos:

1. Oferece, lado a lado, "Distribuir 1 inscrição — Análise de títulos" e "Emitir a ordem sucessora".
2. Emitida a sucessora, ela é parcial: 7 com posição e o reabilitado sem posição. A conferência da
   ordem avisa que ela ficará obsoleta. O Centro passa a oferecer o corte.
3. O corte é aceito sem aviso: 6 progridem, e o reabilitado fica fora, porque está sem posição.
4. O Centro passa a oferecer a Análise documental dos 6.

**Para a primeira ordem, a mesma derivação já diz *Depois*** enquanto as Etapas que ela lê não estão
feitas (a FR-4068 da `127`): emiti-la antes grava uma ordem que envelhece quando os resultados
chegam, e a sucessão exige motivo. A sucessora não tem essa espera: o ramo da ordem obsoleta devolve
"Emitir a ordem sucessora" antes de olhar as Etapas por fazer.

A publicação continua protegida. Ela recusa o reingresso pendente, e o resultado oficial não sai
errado. **Mesmo assim, não é só retrabalho.** Os atos intermediários têm efeito operacional: um corte
incompleto distribui avaliações da Etapa seguinte a quem talvez não progrida, e tira dela quem talvez
progrida.

### O que esta spec cobre, e o que fica fora

**Cobre:**
- a ordem sucessora com Etapa por fazer, que deixa de ser providência;
- o corte com reingresso pendente no marco, que deixa de ser providência, nas suas duas formas
  (emitir e emitir a geração sucessora);
- a Etapa governada pelo corte, avaliada e mantida como está (D-004);
- um aviso na tela do corte, quando há reingresso pendente (P3).

**Fica fora:**
- qualquer mudança no que os comandos aceitam. A ordem parcial continua aceita, pela decisão da
  `128`, com o aviso que a conferência já dá; o corte também;
- o sorteio e a observação da semente. A quinta decisão do estudo de continuidade foi tomada em
  10/11 pela alternativa (d), sem regra nova;
- a URL da célula, que é da `139`;
- os achados F-1 e F-3 da triagem, que não pedem correção.

## Clarifications

Nenhuma pergunta aberta. A triagem deixou à spec uma escolha — *Depois* ou *Obsoleta* sem ato para a
sucessora —, e ela está em D-001. As demais escolhas estão em *Decisões* e em *Assumptions*.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — A sucessora espera a Etapa do reabilitado (Priority: P1)

Quem conduz a seleção acabou de cumprir um recurso deferido que reabilita um candidato. A Etapa que
falta a ele está por fazer. O Centro deve mandar fazer essa Etapa, e não emitir a ordem sucessora.

**Why this priority**: é a origem da cascata. Sem a sucessora oferecida, o corte sobre a ordem
incompleta também não é oferecido, pela regra que já existe.

**Independent Test**: no C08, deferido o recurso que reabilita o 08, o andamento não tem a
providência "Emitir a ordem sucessora" para nenhum papel. A célula da ordem diz *Depois* e por quê.
Consolidada a Análise de títulos do 08, a providência aparece.

**Acceptance Scenarios**:

1. **Given** a ordem vigente obsoleta e uma Etapa que ela lê ainda por fazer no Perfil, **When** o
   andamento é derivado, **Then** a célula da ordem é *Depois*, sem ato a praticar, e a razão diz que
   a sucessora lê aquela Etapa, ainda não feita, e que a vigente continua produzindo efeito.
2. **Given** o mesmo estado, **When** quem conduz abre o Centro ou o detalhe do Edital, **Then** a
   providência da Etapa ("Distribuir 1 inscrição…") continua lá, e a da sucessora não.
3. **Given** a Etapa consolidada, **When** o andamento é derivado de novo, **Then** a célula da ordem
   é *Obsoleto*, com "Emitir a ordem sucessora", como hoje.
4. **Given** uma lista em que ninguém concorre (a `135`), com a ordem obsoleta e sem Etapa por fazer,
   **When** o andamento é derivado, **Then** a providência é a de hoje: a sucessora que declara que
   ninguém concorreu.
5. **Given** o mesmo estado do cenário 1, **When** a célula do resultado é derivada, **Then** ela é a
   de hoje para a ordem obsoleta: *Depois*, porque a ordem vigente está para trás.
6. **Given** o mesmo estado, **When** quem conduz abre o Centro, **Then** a Classificação aparece em
   curso, e não como ainda não começada.

---

### User Story 2 — O corte espera o reingresso (Priority: P1)

Quem conduz pode ter emitido a sucessora parcial por conta própria — a tela aceita, com aviso — ou ter
um corte anterior ao recurso, que o reingresso tornou obsoleto. Enquanto o reabilitado não tem
resultado numa Etapa que o marco enumera, o Centro não deve oferecer o corte.

**Why this priority**: é o ato com efeito fora do marco. O corte decide quem participa da Etapa
seguinte, e cortar sem o reabilitado distribui avaliações a quem talvez não progrida.

**Independent Test**: no C08, com o reingresso pendente e a sucessora parcial emitida pela tela, o
andamento não oferece "Emitir o corte". A célula do corte diz *Depois* e nomeia o reingresso.

**Acceptance Scenarios**:

1. **Given** reingresso pendente no marco e a ordem vigente feita, **When** o andamento é derivado,
   **Then** a célula do corte é *Depois*, sem ato a praticar, e a razão diz que há inscrição
   reabilitada por recurso ainda sem resultado numa Etapa do marco.
2. **Given** reingresso pendente e o corte vigente obsoleto (o reingresso de quem estava no universo
   da ordem), **When** o andamento é derivado, **Then** a célula do corte é *Depois*, e a geração
   sucessora não é providência.
3. **Given** um corte emitido antes do recurso, e o reabilitado fora do universo da ordem, **When** o
   recurso é deferido, **Then** o corte continua *Feito*, a sucessora espera a Etapa do reabilitado,
   e só emitida a sucessora o corte pede a geração sucessora.
4. **Given** nenhum reingresso pendente, **When** o andamento é derivado, **Then** o corte segue a
   regra de hoje, inclusive a espera do prazo recursal da `133`.
5. **Given** reingresso pendente num marco por sorteio, **When** o andamento é derivado, **Then** nada
   muda: o reingresso é pergunta sobre Etapas, e a ordem do sorteio não vem de Etapa.

---

### User Story 3 — A cadeia inteira, na ordem certa (Priority: P1)

Quem conduz segue o Centro do recurso deferido até a Etapa seguinte, sem praticar ato que nasça para
ser sucedido.

**Why this priority**: é a exigência do usuário para a prova. A célula certa sozinha não basta, porque
a falha era a cadeia.

**Independent Test**: um teste de integração percorre, no C08:
recurso deferido que reabilita → Análise de títulos pendente → consolidada → ordem sucessora → corte
→ Análise documental.

**Acceptance Scenarios**:

1. **Given** o recurso deferido e a Análise de títulos do reabilitado por fazer, **When** o andamento é
   derivado, **Then** nem a sucessora nem o corte são providência, e a Análise documental está
   *Depois*, sem distribuição a fazer.
2. **Given** a Análise de títulos consolidada, **When** o andamento é derivado, **Then** a sucessora é
   providência, e o corte ainda não.
3. **Given** a sucessora emitida, **When** o andamento é derivado, **Then** o corte segue a regra de
   hoje: espera o prazo recursal, se aberto, e é providência depois dele.
4. **Given** o corte emitido, **When** o andamento é derivado, **Then** a Análise documental é
   providência, para os que a faixa alcançou — o reabilitado entre eles, se a posição dele o
   alcançar.

---

### User Story 4 — A correção de nota não espera nada (Priority: P1)

Um recurso deferido corrige a nota de quem já tinha posição, e nenhuma avaliação fica pendente. A
ordem fica obsoleta, e a sucessora é o próximo ato legítimo.

**Why this priority**: é a exigência do usuário de não bloquear o que é legítimo.

**Independent Test**: no C08, um recurso do candidato 07 corrige a Prova objetiva de 6,5 para 7,5. Na
mesma leitura, o andamento oferece "Emitir a ordem sucessora". Emitida, o corte segue o curso normal.

**Acceptance Scenarios**:

1. **Given** um recurso deferido que corrige a nota de quem tinha posição, sem Etapa por fazer,
   **When** o andamento é derivado, **Then** a sucessora é providência na hora, de quem conduz.
2. **Given** a sucessora emitida, **When** o andamento é derivado, **Then** o corte está à espera do
   prazo recursal, como recomendação da `133`, e é providência depois dele.

---

### User Story 5 — A tela do corte avisa do reingresso (Priority: P3)

Quem abre a tela do corte por outro caminho — um link guardado, a tela da ordem — e há reingresso
pendente, precisa ler o que a conferência da ordem já diz: emitido agora, o corte deixa o reabilitado
fora da faixa.

**Why this priority**: é prevenção, e opcional no pedido. A derivação já para de oferecer o corte.

**Independent Test**: no C08, com a sucessora parcial emitida, a tela do corte mostra o aviso antes do
botão; o botão continua lá, e a emissão continua aceita.

**Acceptance Scenarios**:

1. **Given** reingresso pendente no marco, **When** quem pode emitir abre a tela do corte, **Then** um
   aviso diz quantas inscrições reabilitadas estão sem resultado e qual é a consequência de emitir
   agora.
2. **Given** nenhum reingresso pendente, **When** a pessoa abre a tela, **Then** o aviso não aparece.
3. **Given** o aviso na tela, **When** a pessoa emite o corte, **Then** o comando aceita, como hoje.

---

### Edge Cases

- **Reavaliação determinada pendente numa Etapa que a ordem lê**, com a ordem obsoleta. A Etapa não
  está feita, e a sucessora espera, pela mesma regra: emiti-la agora leria o resultado que a
  reavaliação vai substituir.
- **A Etapa por fazer é de outro Perfil.** Não conta: o predicado é o do Perfil do marco, o mesmo da
  primeira ordem.
- **A Etapa por fazer é de outra pessoa, e não do reabilitado.** Conta, como para a primeira ordem: a
  sucessora leria o resultado que falta.
- **A ordem foi emitida parcial pela tela, e a Etapa ainda está em curso.** A ordem é *Feito* até os
  resultados chegarem, como hoje; quando ficar obsoleta, a Etapa já estará feita, e a sucessora é
  providência.
- **O marco enumera uma Etapa que a ordem não lê no desempate.** O reingresso é perguntado nas Etapas
  que o marco enumera, como na publicação; as Etapas por fazer, nas que a ordem lê. As enumeradas
  estão entre as que a ordem lê, de modo que todo reingresso pendente já deixa uma Etapa por fazer.
- **Reingresso pendente e corte feito**, emitido pela tela depois da reabilitação. O corte continua
  *Feito*: é ato vigente. A Etapa governada segue a regra de hoje (D-004).
- **O corte emitido antes do recurso, de quem foi eliminado antes da ordem.** É o caso do C08: o 08
  não estava no universo que a ordem congelou, e o reingresso dele não torna o corte obsoleto (a
  FR-218 da `014` mede o reingresso no ato, de propósito). O corte continua *Feito* até a sucessora
  ser emitida; só então fica para trás e pede a geração sucessora. A sucessora, essa sim, espera a
  Etapa do reabilitado. O corte obsoleto com reingresso pendente, o da FR-4836, é o de quem estava
  no universo da ordem.
- **Reingresso pendente, corte obsoleto e Etapa governada com o bloqueio do corte obsoleto.** A Etapa
  continua *Impedida* pela regra dela, como hoje. Fica registrado fora do escopo.
- **Vários marcos no Perfil.** Cada marco pergunta o reingresso nas Etapas que ele enumera.
- **Recurso deferido que elimina** (o reverso da reabilitação). Não há reingresso, e a sucessora segue
  a regra de hoje.

## Requirements *(mandatory)*

### Functional Requirements

**A ordem sucessora**

- **FR-4830**: Com a ordem vigente obsoleta e alguma Etapa que ela lê ainda por fazer no Perfil, a
  célula da ordem MUST ser *Depois*, sem ato a praticar e sem responsável. "Etapa por fazer" MUST ser
  o mesmo predicado que já decide a primeira ordem (a FR-4068 da `127`).
- **FR-4831**: A razão dessa célula MUST dizer quais Etapas a sucessora lê e não estão feitas, e que
  a ordem vigente continua produzindo efeito (UX-340).
- **FR-4832**: Sem Etapa por fazer, a ordem obsoleta MUST continuar *Obsoleto*, com "Emitir a ordem
  sucessora", ou com a frase da lista em que ninguém concorre (a FR-4671 da `135`).
- **FR-4833**: A célula da FR-4830 MUST carregar, como dado, que existe ordem vigente e que ela está
  para trás. Quem lia a ordem obsoleta MUST continuar lendo assim: a célula do resultado MUST ser a de
  hoje para a ordem obsoleta, em situação e razão.
- **FR-4834**: As células do corte e da apuração que leem a ordem MUST continuar *Depois*, com a razão
  de hoje, quando a ordem está na situação da FR-4830.
- **FR-4845**: No Centro de Controle (`136`), a fase cuja célula é a da FR-4830 MUST ser lida como em
  curso, e não como ainda não começada: há ordem vigente, e ela produz efeito. A primeira ordem com
  Etapa por fazer continua "ainda não começou".

**O corte**

- **FR-4835**: Enquanto houver reingresso pendente no marco, a célula do corte MUST NOT ser
  providência. O predicado MUST ser o mesmo que impede a publicação (a inscrição reabilitada por
  recurso sem resultado numa Etapa que o marco enumera), lido da mesma função.
- **FR-4836**: A FR-4835 MUST valer para as duas formas do ato: emitir o corte e emitir a geração
  sucessora do corte obsoleto. A situação MUST ser *Depois*, e a razão MUST dizer que há inscrição
  reabilitada sem resultado numa Etapa do marco (UX-341).
- **FR-4837**: Sem reingresso pendente, a célula do corte MUST seguir a regra de hoje, inclusive a
  espera recomendada do prazo recursal (a FR-4541 da `133`).
- **FR-4838**: Num marco por sorteio, o reingresso MUST NOT ser perguntado, como na publicação.

**A Etapa seguinte**

- **FR-4839**: A Etapa governada pelo corte MUST continuar *Depois* enquanto não houver corte vigente,
  pela regra de hoje. Esta spec MUST NOT acrescentar outra espera a ela (D-004).

**A tela do corte (P3)**

- **FR-4840**: Com reingresso pendente no marco, a tela do corte MUST mostrar, a quem pode emitir e
  antes do botão, um aviso com o número de inscrições reabilitadas sem resultado e a consequência de
  emitir agora (UX-342). O predicado MUST ser o da FR-4835.
- **FR-4841**: O aviso MUST NOT impedir a emissão. Sem reingresso pendente, ele MUST NOT aparecer.

**Restrições**

- **FR-4842**: Nenhum comando MUST mudar o que aceita ou recusa. A ordem parcial continua aceita, com
  o aviso da conferência (a decisão da `128`).
- **FR-4843**: A pergunta do reingresso MUST ter custo fixo por marco, e só MUST ser feita quando o
  corte poderia ser providência. O custo do detalhe do Edital MUST continuar fixo por Edital (a
  FR-4120 da `127`).
- **FR-4844**: A derivação MUST continuar nunca dizendo *Pendente* para a ordem que o comando recusa
  (a FR-4218 da `128`).

### Regras de experiência

- **UX-340**: A razão da sucessora à espera diz, em linguagem simples: *"a ordem sucessora lê
  [Etapas], que ainda não está feita; a vigente continua produzindo efeito"*, no singular ou no
  plural. Sem identificador interno.
- **UX-341**: A razão do corte à espera diz: *"há inscrição reabilitada por recurso sem resultado numa
  Etapa deste marco: o corte espera a consolidação e a ordem sucessora"*. O texto exato é do plano.
- **UX-342**: O aviso da tela do corte segue o da conferência da ordem: quantas inscrições, por que
  ficam fora da faixa (estão sem posição) e o que acontece quando o resultado chegar (a ordem e o
  corte ficam para trás, e suceder exige motivo).

### Key Entities

- **Célula do andamento** (`127`). Ganha um dado de leitura: a ordem *Depois* que tem vigente para
  trás. Nada é persistido.
- **Reingresso pendente** (o da publicação do resultado). Lido, e não definido de novo.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1510**: No C08, deferido o recurso que reabilita o 08 e antes da consolidação da Análise de
  títulos dele, **zero** providências de ordem sucessora e **zero** de corte, para qualquer papel; a
  Análise documental sem distribuição a fazer.
- **SC-1511**: No mesmo teste, cada passo seguinte da cadeia — consolidar, emitir a sucessora, emitir
  o corte — faz aparecer **exatamente** o ato seguinte: a sucessora, o corte, a Análise documental.
- **SC-1512**: No C08, um recurso que corrige a nota de quem tinha posição, sem avaliação pendente,
  oferece a sucessora **na mesma leitura** que segue o julgamento; emitida, o corte segue a regra de
  hoje.
- **SC-1513**: Em todo estado do SC-1510, a célula do resultado é idêntica à que a derivação de antes
  dava.
- **SC-1514**: Os testes de orçamento da `127` passam com os tetos de antes.
- **SC-1515**: **Zero** migrations, comandos ou permissões alterados. A suíte contra PostgreSQL fecha
  sem falha nova; o caso de coerência com a `128` e a lista vazia da `135` passam sem mudança de
  expectativa.
- **SC-1516**: No navegador, num banco descartável com o C08 carregado, o Centro segue a cadeia do
  SC-1510 e do SC-1511.

## Assumptions

- A triagem de 10/11 é a evidência; o C08 da `134` é o roteiro de teste e de navegador.
- O recurso é cumprido pelo comando de julgamento, com correção fixada da nota. É o caminho que a tela
  do julgador usa.
- O texto exato das razões e do aviso é do plano, em linguagem simples.
- `make lint check test-pg` e a verificação no navegador fazem parte da entrega.

## Compatibilidade com regras anteriores

| Regra | O que esta spec faz com ela |
|---|---|
| FR-4068 da `127` (*Depois* com Etapa por fazer) | Estende à sucessora, pelo mesmo predicado (D-002) |
| A decisão da `128` de aceitar a ordem parcial | Mantém (FR-4842) |
| FR-4218 da `128` (nunca *Pendente* para o que o comando recusa) | Mantém (FR-4844) |
| A lista vazia da `135` (FR-4671) | Mantém, sem Etapa por fazer (FR-4832) |
| A espera do corte pelo prazo recursal (FR-4541 da `133`) | Mantém, sem reingresso (FR-4837) |
| A apuração que espera o corte, da `127` | Mantém |
| O reingresso pendente da publicação | Reaproveitado como predicado do corte (D-003) |
| O resultado com a ordem obsoleta (FR-4550 da `133`) | Mantém (FR-4833) |

## Achado fora do escopo (registro)

- **A Etapa governada com o corte obsoleto e reingresso pendente.** A Etapa fica *Impedida*, e a
  frase dela nomeia a geração sucessora do corte, que a célula do corte agora diz *Depois*. A
  situação é a de hoje, e nenhum ato inválido é oferecido como "seu", porque *Impedido* não é a
  praticar. Alinhar a frase pediria levar o reingresso, que é por marco, à leitura da Etapa, que é do
  Edital.
- **"Resultado e recursos — Ainda não começou", com o preliminar publicado.** No Centro, depois do
  recurso deferido, a fase do resultado diz "Ainda não começou · Resultado publicado em 1 de 2
  listas". A célula do resultado é *Depois* porque a ordem vigente está para trás — como antes desta
  spec (a FR-4550 da `133`) —, e a agregação do Centro lê só *Depois*. A FR-4845 corrige a
  Classificação, que é desta spec; a fase do resultado é da `136`.
- **A apuração obsoleta com o corte à espera.** O ramo da apuração obsoleta olha a Etapa governada, e
  não o corte. Com o corte obsoleto, hoje o andamento oferece as duas sucessoras ao mesmo tempo, com
  ou sem reingresso. Mudar isso muda o fluxo normal da sucessão, e não é deste achado.

## Decisões

### D-001 — A sucessora à espera é *Depois*, e não *Obsoleta* sem ato

**Alternativas.**
- (a) *Obsoleto*, sem ato e sem responsável.
- (b) *Depois*, com a razão e com o dado de que há vigente para trás.

**Escolha: (b).** *Obsoleto* é situação em aberto e a praticar: entraria no nível 1 como providência
sem ato, e o Centro a desenharia como coisa a fazer. *Depois* é o que a derivação já diz para a
primeira ordem com Etapa por fazer, e para a apuração obsoleta que espera a Etapa governada (*"a
apuração está para trás, e a sucessora espera…"*).

O corte e a apuração dizem o mesmo com as duas, porque leem só "a ordem não está feita". O resultado
distingue a ordem obsoleta, e é por ele que a célula carrega o dado da FR-4833: com ele, o resultado
continua dizendo que a ordem vigente está para trás, e não que não há ordem a divulgar.

### D-002 — A sucessora espera as Etapas por fazer, e não só o reingresso

**Alternativas.**
- (a) O predicado do reingresso pendente, só para quem foi reabilitado.
- (b) O predicado da primeira ordem: as Etapas que a ordem lê e que ainda não estão feitas no Perfil.

**Escolha: (b).** É o predicado que já decide a primeira ordem, e o pedido é estender a regra da
`127` à sucessora. Todo reingresso pendente deixa uma Etapa por fazer, de modo que (b) cobre o caso do
F-2. Cobre também a reavaliação determinada pendente, em que emitir a sucessora leria o resultado que
vai ser substituído.

Não bloqueia o legítimo: a correção de nota sem avaliação pendente não deixa Etapa por fazer.

### D-003 — O corte espera pelo predicado da publicação

O pedido manda reaproveitar o predicado da publicação, e não escrever outro. É a mesma pergunta — há
inscrição reabilitada sem resultado numa Etapa que o marco enumera? —, lida pela mesma função. A
publicação já dá a razão: emitir sucessor ali *"produziria o mesmo ato incompleto"*.

O corte não usa o predicado das Etapas por fazer, porque o corte lê a ordem, e não as Etapas. A
espera dele pela ordem já existe. O que faltava é o caso em que a ordem está feita — a sucessora
parcial, emitida pela tela — ou em que o corte já existia e ficou obsoleto pelo reingresso.

### D-004 — A Etapa seguinte não ganha espera própria

A Etapa governada já é *Depois* sem corte vigente. Com as duas esperas acima, o Centro não leva mais
ao corte com o reabilitado pendente, e a Etapa seguinte não fica distribuível por esse caminho.

Se o corte for emitido pela tela, apesar do aviso, ele é ato vigente: a Etapa distribui pela faixa
dele, como o comando permite. Fazê-la esperar seria contradizer um ato vigente na leitura, e não
evitar o ato.

### D-005 — O aviso da tela do corte usa o predicado do reingresso

A conferência da ordem avisa a partir da proposta, que a tela do corte não tem. A tela do corte
pergunta o reingresso pendente, que é o mesmo predicado da derivação: assim a tela e o Centro
concordam sobre quando o corte espera.
