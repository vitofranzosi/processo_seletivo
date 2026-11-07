# Feature Specification: A confirmação de "Encerrar Processo" adverte as providências em aberto dos Editais

**Feature Branch**: `claude/silly-engelbart-07c8f4`, sobre a `main` em `5cf5f179` (com a `126`, a `127`
e a `128`)

**Created**: 2026-11-06

**Status**: Draft. **Leitura e apresentação, sem regra de negócio nova.** A confirmação de "Encerrar
Processo" passa a dizer, por Edital, o que ainda está em aberto nele, e volta a mostrá-lo quando ele mudou
antes do envio. O comando de encerramento continua aceitando nos mesmos casos de hoje. Sem migration, tabela, coluna, permissão ou estado persistido novo; a lista de
Processos não muda.

**Input**: *"A advertência das providências em aberto na confirmação de 'Encerrar Processo' — a décima
decisão da revisão de 06/11 da página de Processos Seletivos. Hoje a confirmação mostra as
consequências, os Editais fora de estado final e o motivo; o encerramento só exige Editais finais. Com
convocação aguardando resposta ele aceita, e em seguida o convocado é recusado ao apresentar documento ou
enviar o Requerimento. A advertência lista, por Edital do Processo, as providências em aberto, com os
mesmos tipos e frases que o encerramento do Edital (`113`) já usa. É advertência, e não impedimento:
reduz o risco, não o elimina; impedir é outra decisão de domínio e fica fora. Sem migration, estado ou
permissão; a lista de Processos (`129`) não muda."*

> **Faixa de identificadores.** Esta spec usa a faixa reservada para ela: os requisitos funcionais de
> quatro mil trezentos e cinquenta a quatro mil trezentos e setenta e nove, os critérios de mil trezentos
> e vinte a mil trezentos e vinte e nove e os de experiência de duzentos e setenta e cinco a duzentos e
> setenta e nove; os não usados ficam livres. O teto foi medido em 06/11/2026 em `specs/` de todas as
> worktrees desta máquina: na `main`, o requisito quatro mil duzentos e vinte, o critério mil trezentos e
> seis e o de experiência duzentos e sessenta e dois; a `129` (PR #420, sem merge) reservou até o
> requisito quatro mil trezentos e quarenta e nove, o critério mil trezentos e dezenove e o de
> experiência duzentos e setenta e quatro. As decisões reiniciam em `D-001`.
>
> **Origem.** A revisão de 06/11/2026 do estudo da página de Processos Seletivos
> (`doc/estudo-pagina-processos-seletivos-2026-11-06-revisao.md`, seções 4, 7 e 8, PR #420), cuja
> décima decisão o usuário aceitou no mesmo dia: antecipar a advertência, em separado da `129`, com a
> ressalva de que advertir não impede o encerramento.

## Por que esta feature existe

O encerramento do Edital (`113`) já diz, antes do ato, o que fica pendente: a convocação aguardando
resposta, o resultado não divulgado, o recurso sem decisão. O do **Processo** não diz nada disso, e é
ele que corta. Encerrado o Processo, os Editais dele deixam de aceitar alteração: o convocado que ainda
está no prazo é recusado ao apresentar documento e ao enviar o Requerimento de Matrícula, a comissão não
confere mais documento e ninguém mais é convocado do cadastro de reserva. A revisão executou isso contra
PostgreSQL, com 20 casos (seção 7).

Hoje o gestor que encerra o Processo vê só se cada Edital está Encerrado ou Cancelado. Um Processo com
todos os Editais encerrados e uma convocação no meio do prazo passa por essa conferência, e a tela não
dá nenhum sinal do convocado que vai ser cortado.

**Advertir reduz o risco, e não o elimina.** O gestor que confirma mesmo assim ainda corta o convocado.
Impedir o encerramento com providência em aberto seria outra decisão de domínio, e o sistema não sabe
se ela ainda importa: a validade do cadastro de reserva é texto livre do Edital, e um Processo sem nada
em aberto pode estar a três meses de convocar o próximo. A revisão deixa essa decisão em aberto (a
primeira decisão dela), e esta spec não a toma.

### O que esta spec cobre, e o que fica fora

Cobre:

1. **A advertência na confirmação de "Encerrar Processo"**: por Edital publicado do Processo, as
   providências em aberto, com os tipos e as frases do encerramento do Edital.
2. **O caso sem nada em aberto**, dito sem afirmar que o certame acabou.
3. **A reexibição** da advertência quando o encerramento é recusado por outro motivo.
4. **A renovação da confirmação** quando a lista mudou entre a abertura da tela e o envio (decidida no
   esclarecimento de 06/11): a tela volta com a lista atual, sem encerrar.

Fica fora, de propósito:

- **Impedir o encerramento.** O comando continua exigindo só que os Editais estejam finais.
- **"Cancelar Processo".** O cancelamento também corta o convocado, e a mesma advertência caberia ali;
  o pedido nomeou só o encerramento, e estender é do usuário (registrado em *Fora de escopo*).
- **A lista de Processos**, e qualquer sinal de "pronto para encerrar" nela: é da `129` e da Frente B
  da revisão.
- **Os achados de domínio A-1 a A-6 da revisão**: recurso julgado com o Processo cancelado, recurso
  interposto depois do encerramento, designação de formalização e exportação com o Processo final,
  aviso confirmado antes e despachado depois, e o texto da decisão sobre o Processo final na `127`. O
  usuário os prioriza à parte.
- **Aviso confirmado e ainda não despachado.** A revisão o cita entre as providências possíveis, mas
  nenhum tipo do encerramento do Edital o representa, e criá-lo seria regra nova (é o A-4).
- **Registrar o que foi advertido.** O ato continua gravando o motivo e nada mais (D-006).

## Clarifications

### Session 2026-11-06

- Q: Quando a lista de providências em aberto muda entre abrir a confirmação e clicar em Confirmar, o
  encerramento deve seguir mesmo assim, ou a tela deve voltar mostrando a lista nova para o gestor
  confirmar de novo? → A: **B.** Se a lista exibida mudou em qualquer coisa, a confirmação é
  reapresentada com a lista atualizada e a frase da UX-279, sem encerrar; sem mudança, o encerramento
  prossegue. É **renovação da confirmação**, e não impedimento: nenhuma providência passa a impedir o
  encerramento por si só, e o gestor que confirma de novo diante da lista nova encerra. Fica uma janela
  entre a releitura e o comando, que esta solução não elimina (D-005).
- As decisões D-001, D-002 e D-004 foram revistas na mesma sessão contra o código e mantidas, sem
  pergunta: a D-002 se apoia em `ensure_edital_accepts_changes`, que recusa Edital Encerrado ou Cancelado
  e é chamada por todo ato da Retificação. A FR-4360 foi alinhada à D-004: a advertência só reaparece
  quando a tela reexibida ainda oferece o Confirmar.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — O gestor vê o convocado que o encerramento vai cortar (Priority: P1)

O gestor com permissão de encerrar abre "Encerrar Processo" num Processo ativo cujos Editais estão todos
Encerrados ou Cancelados. Num deles há duas convocações aguardando resposta, com prazo até 20/11/2026. Antes
do motivo, a confirmação mostra um bloco com o Edital, a frase da convocação e o que acontece com quem
está no prazo. O gestor decide: volta e espera o prazo, ou encerra assim mesmo, sabendo.

**Why this priority**: é o caso que motivou a décima decisão da revisão, e o único em que o encerramento
corta um direito em curso de candidato.

**Independent Test**: com um Processo de um Edital encerrado e uma convocação com prazo correndo, abrir a
confirmação e ler o bloco; depois confirmar e verificar que o encerramento é aceito, como hoje.

**Acceptance Scenarios**:

1. **Given** um Processo ativo com um Edital encerrado que tem 2 convocações aguardando resposta até
   20/11, **When** o gestor abre "Encerrar Processo", **Then** a confirmação mostra o bloco das
   providências em aberto, com o Edital identificado por número, ano e título, a frase "2 convocações
   aguardando resposta, até 20/11/2026." e a frase de que quem está no prazo não poderá mais apresentar
   documento nem enviar o Requerimento de Matrícula.
2. **Given** a mesma confirmação, **When** o gestor preenche o motivo e confirma, **Then** o Processo é
   encerrado, como hoje, e nada além do motivo é gravado.
3. **Given** a mesma confirmação, **When** o gestor lê o bloco, **Then** nenhum nome, CPF, e-mail ou
   protocolo de candidato aparece.

---

### User Story 2 — Todos os tipos da 113, por Edital (Priority: P1)

O Processo tem três Editais: um encerrado com resultado de um marco ainda não divulgado e um recurso
aguardando decisão, um cancelado com uma convocação vencida sem registro de resposta, e um cancelado
antes da publicação. A confirmação mostra dois grupos, na ordem do número dos Editais, cada um com as
frases dele, e não mostra o terceiro.

**Why this priority**: a advertência só reduz o risco se não omitir o que o encerramento do Edital já
sabe dizer; uma segunda lista divergiria do relatório na primeira mudança.

**Independent Test**: montar os três Editais, abrir a confirmação e comparar as frases de cada grupo com
as que o relatório do Edital e a regra do encerramento do Edital produzem para o mesmo instante.

**Acceptance Scenarios**:

1. **Given** o Edital encerrado com o resultado de "Análise curricular" não divulgado e 1 recurso
   aguardando decisão, **When** a confirmação é aberta, **Then** o grupo dele traz "Resultado de
   “Análise curricular” ainda não divulgado." e "1 recurso aguarda decisão.", esta com o caminho "Ir
   aos recursos" para quem julga recursos e, para quem não julga, "Peça a quem julga recursos.".
2. **Given** o Edital cancelado com 1 convocação vencida, **When** a confirmação é aberta, **Then** o
   grupo dele traz "1 convocação com prazo encerrado sem registro de resposta." e nenhuma frase de
   resultado — o Edital cancelado não terá resultado, como já diz o relatório.
3. **Given** o Edital cancelado antes da publicação, **When** a confirmação é aberta, **Then** ele não
   aparece no bloco.
4. **Given** um Edital encerrado sem nada em aberto ao lado de outro com providência, **When** a
   confirmação é aberta, **Then** só o segundo aparece.

---

### User Story 3 — Nada em aberto, sem prometer que acabou (Priority: P2)

Nenhum Edital do Processo tem providência em aberto. A confirmação diz isso numa frase, e diz também que
o sistema não sabe se ainda haverá convocação do cadastro de reserva.

**Why this priority**: sem a frase, a ausência do bloco não se distingue da tela antiga; com uma frase
que afirmasse conclusão, a tela induziria o encerramento justamente quando a reserva ainda vale.

**Independent Test**: Processo com um Edital encerrado e nada em aberto; abrir a confirmação e ler a
frase.

**Acceptance Scenarios**:

1. **Given** um Processo cujos Editais finais não têm providência em aberto, **When** a confirmação é
   aberta, **Then** ela diz "Nenhuma providência em aberto registrada no GPS nos Editais deste
   Processo." e, em seguida, que o GPS não sabe se ainda haverá convocação do cadastro de reserva,
   porque a validade dele está no texto do Edital.
2. **Given** a mesma confirmação, **Then** ela não diz que a seleção, o certame ou os Editais foram
   concluídos.

---

### User Story 4 — A recusa por outro motivo reexibe a advertência atual (Priority: P2)

O gestor confirma sem motivo, ou o Processo mudou de revisão entre a abertura e o envio. A tela volta
com o erro, e o bloco volta junto, lido de novo naquele instante.

**Why this priority**: perder o bloco na reexibição é perder a advertência no momento em que o gestor
está prestes a confirmar de novo.

**Independent Test**: enviar a confirmação sem motivo e conferir que o bloco reaparece; depois do 422,
criar uma convocação e conferir que o envio seguinte a mostra.

**Acceptance Scenarios**:

1. **Given** a confirmação com uma convocação aguardando, **When** o gestor envia sem motivo, **Then** a
   tela volta com "Motivo do encerramento é obrigatório." e o bloco das providências em aberto.
2. **Given** a confirmação reexibida depois de um 422 por motivo vazio, com a lista L, **When** uma
   convocação é feita e o gestor envia de novo, agora com motivo, **Then** a confirmação é reapresentada
   pela renovação (história 5), com a convocação, e o Processo continua Ativo. A mudança da lista é
   conferida antes do motivo e antes do comando (FR-4365).

---

### User Story 5 — A lista mudou depois que a tela abriu: o gestor confere antes de encerrar (Priority: P1)

O gestor abre a confirmação sem nada em aberto e a deixa aberta. Enquanto isso, a comissão convoca mais
uma pessoa num dos Editais. O gestor preenche o motivo e confirma. O Processo não é encerrado: a tela
volta com a convocação nova, a frase de que a lista mudou e o motivo que ele escreveu. Ele lê e confirma
de novo; agora o Processo é encerrado.

**Why this priority**: a confirmação pode ficar aberta por horas, e a convocação feita nesse intervalo é
justamente a que o encerramento corta sem que o gestor a tenha visto (esclarecimento de 06/11).

**Independent Test**: abrir a confirmação, criar uma convocação, enviar; conferir que nada foi gravado e
que a tela traz a lista nova; enviar de novo e conferir o encerramento.

**Acceptance Scenarios**:

1. **Given** a confirmação aberta com a lista L, **When** a lista passa a ser L′ ≠ L e o gestor confirma
   com motivo, **Then** o Processo continua Ativo, nenhum ato é gravado, e a tela reapresenta a
   confirmação com L′, a frase da UX-279 e o motivo preenchido.
2. **Given** a confirmação reapresentada com L′, **When** o gestor confirma de novo e a lista continua L′,
   **Then** o Processo é encerrado, ainda que L′ tenha providência em aberto.
3. **Given** a confirmação aberta com a lista L, **When** nada muda e o gestor confirma, **Then** o
   Processo é encerrado na primeira tentativa, como hoje.
4. **Given** a confirmação aberta com 2 convocações aguardando, **When** uma delas é respondida antes do
   envio, **Then** a confirmação também é reapresentada: qualquer diferença conta, inclusive a que reduz
   a lista.

---

### Edge Cases

- **Edital ainda publicado (fora de estado final)**: o ato já é dito recusado ("Este ato será
  recusado"), e o Confirmar não é oferecido. A advertência não é lida nem mostrada (D-004): o caminho é
  encerrar cada Edital, cuja confirmação própria já adverte.
- **Quem não pode encerrar**, ou o Processo fora de Ativo: a tela já diz o impedimento; a advertência
  não é lida — as contagens do Processo não são de quem não pratica o ato.
- **Edital encerrado antes da `113`**, com situação que hoje impediria encerrá-lo (prazo de recurso em
  curso, recurso sem decisão, reavaliação ou providência de recurso pendente): aparece como advertência,
  com a frase da `113`. Nada aqui impede (D-003).
- **Recurso interposto depois do encerramento do Edital**, num marco sem prazo de recurso declarado:
  aparece como "1 recurso aguarda decisão.", e a frase do prazo não declarado também aparece.
- **Período de inscrições**: nunca aparece. O Edital final já não recebe, e a frase "o encerramento põe
  fim ao recebimento" falaria do Edital, e não do Processo (D-002).
- **Retificação em curso ou homologada num Edital final**: não aparece. Desde a correção A-09 da
  auditoria de prontidão (#358), o Edital final recusa os atos da Retificação, e a frase da homologada
  mandaria "publique-a ou devolva-a" (D-002). A seção "Retificações em curso" do Edital continua dizendo
  que ela não pode mais prosseguir.
- **Convocação sem comunicação enviada**: aparece com a frase própria da `126`. A frase sobre quem está
  no prazo só acompanha a convocação **aguardando resposta**, que é o caso verificado (UX-276).
- **Edital com poucos inscritos**, abaixo do limiar de privacidade do relatório: as providências não
  públicas aparecem como o relatório as diz para o Edital inteiro, somadas, sem Perfil.
- **Muitos Editais** (o Processo com uma dezena): um grupo por Edital com algo em aberto, na ordem
  número/ano; o bloco não é truncado nem paginado.
- **Ato concorrente entre a abertura e o envio**: a lista é relida no envio e comparada à que foi
  mostrada; se mudou, a confirmação é reapresentada sem encerrar (FR-4365). **Fica uma janela** entre essa
  releitura e o comando: uma convocação feita nesses instantes não é vista. A solução reduz a janela de
  horas para o tempo de uma requisição, e não a elimina (D-005).
- **A lista oscila** (uma convocação feita e respondida entre a abertura e o envio, voltando à lista
  mostrada): nada mudou do ponto de vista do que o gestor viu, e o encerramento prossegue.
- **Reapresentações sucessivas**: se a lista mudar de novo a cada envio, a confirmação é reapresentada a
  cada vez; não há limite nem desistência automática, porque cada mudança é algo que o gestor não viu.
- **Envio sem o resumo da lista mostrada** (formulário antigo em cache, ou envio fabricado): tratado como
  lista diferente — a confirmação é reapresentada com a lista atual, sem encerrar.
- **Pedido repetido com a mesma chave de idempotência**: devolve o desfecho do primeiro, como hoje. A
  reapresentação não chama o comando, e por isso não consome a chave; o envio seguinte usa a mesma.
- **O Processo deixou de ser encerrável entre a abertura e o envio** (a permissão foi retirada, ou outro
  gestor encerrou o Processo): a tela reexibida já não oferece o
  Confirmar, e não há advertência nem comparação (FR-4357, FR-4360); vale a recusa de hoje.
- **Prazo que vence entre a abertura e o envio**: a convocação passa de "aguardando resposta" a "com
  prazo encerrado sem registro de resposta", ou o prazo de recurso termina, e a frase muda. A lista
  mudou, e a confirmação é reapresentada (FR-4365): o gestor vê o novo estado antes de encerrar.
- **Processo encerrado com sucesso**: o redirecionamento ao detalhe é o de hoje; nada da advertência é
  gravado nem repetido ali.

## Requirements *(mandatory)*

### Functional Requirements

#### O que se adverte

- **FR-4350**: A confirmação de "Encerrar Processo" MUST exibir, para cada Edital do Processo em estado
  final (Encerrado ou Cancelado) que tenha sido publicado, as providências em aberto nele no instante da
  leitura, agrupadas por Edital.
- **FR-4351**: As providências MUST ser as que o encerramento do Edital (`113`) já exibe, pela mesma regra
  e com a mesma frase, e não por uma segunda definição: as do relatório do Edital da `099` que a
  confirmação do Edital repete (convocação sem comunicação enviada, convocação aguardando resposta com a
  data mais distante, convocação com prazo encerrado sem registro de resposta, resultado não divulgado,
  resultado definitivo não publicado e apuração desatualizada) e as que a `113` acrescenta sobre recurso
  (prazo de recurso em curso, prazo de recurso não declarado, recurso aguardando decisão, reavaliação e
  providência determinadas em recurso e pendentes).
- **FR-4352**: As situações do período de inscrições e das Retificações MUST NOT ser exibidas (D-002).
- **FR-4353**: Todas as providências MUST ser exibidas como advertência, inclusive as que a `113` trata
  como impedimento de encerrar o Edital; nenhuma MUST impedir o encerramento do Processo (D-003).
- **FR-4354**: Para cada Edital, toda providência de convocação, de resultado e de apuração que o
  relatório do Edital listar no mesmo instante MUST aparecer na advertência, e nenhuma desses tipos que
  ele não listar MUST aparecer; no Edital cancelado, como no relatório, MUST NOT aparecer providência de
  resultado. As de recurso vêm da regra da `113`, e cada uma MUST aparecer uma vez só, ainda que o
  relatório também a liste (como a confirmação do Edital já faz).
- **FR-4355**: O caminho até a tela que resolve cada providência MUST seguir a regra da `113`: oferecido
  só a quem essa tela aceita, e a quem ela recusaria, a frase de a quem pedir (FR-3538 da `113`).
- **FR-4356**: A advertência MUST NOT exibir dado pessoal de candidato — nome, CPF, e-mail ou protocolo —,
  nem o Perfil abaixo do limiar de privacidade do relatório; diz contagens do Edital, o nome publicado do
  marco e datas (FR-3540 da `113`).

#### Onde e quando

- **FR-4357**: A advertência MUST ser lida e exibida só quando a confirmação oferece o Confirmar: ator com
  a permissão de encerrar o Processo, Processo Ativo e nenhum Edital fora de estado final (D-004).
- **FR-4358**: Editais sem providência em aberto e Editais nunca publicados MUST NOT aparecer no bloco. Os
  que aparecem MUST seguir a ordem por ano e número em que a recusa já nomeia os Editais pendentes.
- **FR-4359**: Sem nenhuma providência em aberto, a confirmação MUST dizer que nenhuma está registrada nos
  Editais do Processo, MUST dizer que o sistema não sabe se ainda haverá convocação do cadastro de
  reserva, e MUST NOT dizer que a seleção, o certame ou os Editais foram concluídos.
- **FR-4360**: Quando o encerramento é recusado ou a confirmação é reapresentada, e a tela reexibida
  ainda oferece o Confirmar, a advertência MUST ser lida de novo, no instante da reexibição; quando a
  tela reexibida não oferece o Confirmar, a advertência MUST NOT ser lida nem exibida (D-004).
- **FR-4361**: A advertência de todos os Editais MUST ser lida num mesmo instante e numa leitura
  consistente, como o relatório do Edital: dois Editais não podem ser lidos em momentos diferentes da
  mesma tela.

#### A renovação da confirmação

- **FR-4365**: O envio da confirmação MUST levar um resumo da lista de providências exibida. Antes de
  chamar o comando, quando a tela ainda ofereceria o Confirmar, a lista MUST ser relida e comparada a
  esse resumo; havendo qualquer diferença — providência nova ou resolvida, contagem ou data alterada,
  Edital que entrou ou saiu do bloco —, ou faltando o resumo, o encerramento MUST NOT ser tentado, e a
  confirmação MUST ser reapresentada com a lista atual, o resumo dela, a frase da UX-279 e o motivo já
  preenchido. Sem diferença, o encerramento MUST prosseguir.
- **FR-4366**: A renovação MUST NOT impedir o encerramento por si só: confirmada diante da lista atual,
  e sem nova mudança, o encerramento MUST prosseguir, qualquer que seja o conteúdo da lista. O resumo
  MUST NOT ser gravado (FR-4363), e a reapresentação MUST NOT gravar ato, trilha nem consumir a chave de
  idempotência.
- **FR-4367**: Nenhuma frase da confirmação MUST afirmar que o encerramento só ocorre com a lista que o
  gestor viu, nem que a lista é garantida até o ato: resta uma janela entre a releitura e o comando, na
  qual uma mudança não é vista, e a renovação reduz a concorrência sem eliminá-la (D-005).

#### O que não muda

- **FR-4362**: As regras de elegibilidade do encerramento — permissão, Processo Ativo e Editais em estado
  final — MUST continuar as de hoje, e o comando MUST aceitar e recusar exatamente nos mesmos casos. A
  única etapa nova é a renovação da confirmação na tela (FR-4365), que adia a tentativa sem recusá-la;
  esta spec MUST NOT tornar recusado nenhum ato, antes ou depois do encerramento.
- **FR-4363**: O ato de encerramento MUST NOT gravar a advertência exibida, nem exigir declaração de
  ciência; o motivo continua sendo o único texto do gestor no ato (D-006).
- **FR-4364**: As consequências anunciadas do encerramento, a confirmação de "Cancelar Processo", o
  detalhe do Processo e a lista de Processos MUST NOT mudar.

### Experiência

- **UX-275**: O bloco vem depois do aviso de recusa certa (quando houver, e então o bloco não existe) e
  antes das consequências, com o título *"Em aberto nos Editais deste Processo"* e a frase de abertura
  *"Encerrar o Processo não conclui estas providências, e os Editais dele deixam de aceitar
  alteração."* Cada grupo começa pelo Edital — *"N/AAAA — título"*, com link ao detalhe e a situação —,
  seguido das frases, uma por item, com o caminho ou a quem pedir. O bloco é uma advertência, com
  `role="status"` como o da `113`, e não um alerta de recusa.
- **UX-276**: Havendo convocação aguardando resposta em algum Edital, o bloco acrescenta, depois da frase
  de abertura: *"Quem foi convocado e ainda está no prazo não poderá mais apresentar documento nem enviar
  o Requerimento de Matrícula."*
- **UX-277**: Sem nada em aberto, no lugar do bloco: *"Nenhuma providência em aberto registrada no GPS
  nos Editais deste Processo. O GPS não sabe se ainda haverá convocação do cadastro de reserva: a
  validade dele está no texto do Edital."*
- **UX-278**: O título do bloco MUST NOT ser o da `113` ("Continuam depois do encerramento"): no Processo,
  boa parte do que está em aberto não continua — é cortado (D-001).
- **UX-279**: Na reapresentação, antes do bloco, uma mensagem que não é de erro: *"As providências em
  aberto mudaram desde que você abriu esta tela. Confira a lista atual e confirme de novo."* Ela recebe o
  foco, como a mensagem de erro de hoje, para que o leitor de tela a anuncie.

### Key Entities

Nenhuma entidade nova. A advertência lê, por Edital final publicado, o que a regra do encerramento do
Edital e o relatório do Edital já derivam: as situações pendentes e as providências, no instante da
leitura. Nada é gravado.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1320**: Em **100%** dos Processos com convocação aguardando resposta num Edital final, a
  confirmação de "Encerrar Processo" mostra a convocação, com a data, e a frase sobre quem está no prazo,
  antes do campo de motivo.
- **SC-1321**: Para **cada** tipo da FR-4351, um Edital final com aquela providência produz na
  advertência a mesma frase que a confirmação de encerrar o Edital produziria; e **zero** providências
  listadas pelo relatório de um Edital final, nos tipos da FR-4351, ficam fora da advertência.
- **SC-1322**: Em **100%** dos casos em que hoje o comando de encerramento do Processo aceita, ele
  continua aceitando, e em **100%** dos recusados continua recusando, com a mesma recusa; a única
  diferença observável é a reapresentação da SC-1327, que adia a tentativa.
- **SC-1323**: **Zero** dados pessoais de candidato na confirmação, conferido por varredura do HTML em
  cenário com nome, CPF, e-mail e protocolo conhecidos.
- **SC-1324**: **Zero** mudanças no número de leituras da lista de Processos e do detalhe do Processo;
  a leitura da confirmação cresce com o número de Editais finais publicados do Processo, com orçamento
  fixado por teste no plano.
- **SC-1325**: **Zero** migrations, permissões e estados persistidos novos; **zero** mudanças na
  confirmação de "Cancelar Processo".
- **SC-1327**: Em **100%** dos envios em que a lista mudou desde a abertura (providência nova,
  resolvida ou com contagem ou data alterada), **zero** encerramentos são gravados e a confirmação volta
  com a lista atual; em **100%** dos envios sem mudança, inclusive com providência em aberto, o
  encerramento é gravado na primeira tentativa.
- **SC-1326**: A suíte contra PostgreSQL fecha sem falha nova em relação à linha de base da `main`, e cada
  teste ajustado está nomeado na verificação.

## Proteção de dados (LGPD)

Avaliação exigida pelo princípio III da Constituição.

- **Dado tratado.** Nenhum dado pessoal novo é coletado, gravado ou derivado. A advertência lê
  convocações, recursos, resultados e apurações que já existem, e só para contar.
- **Necessidade e minimização.** A tela mostra contagens do Edital, o nome publicado do marco e datas de
  prazo (FR-4356), como a confirmação do Edital (FR-3540 da `113`). Convocação e recurso são fato não
  público: nunca aparecem por pessoa, e as providências que vêm do relatório respeitam a omissão de
  detalhe por Perfil da `099` (FR-2587 da `100`).
- **Finalidade e acesso.** A advertência só é lida para quem detém `processo:encerrar`, com o Processo
  Ativo (FR-4357). Quem quer saber *quem* segue o caminho até a tela dona, sob a permissão dela
  (FR-4355).
- **O resumo do formulário.** É um hash das frases exibidas, que não têm dado pessoal. Ele não identifica
  pessoa nem é gravado (FR-4366).
- **Registros.** A renovação não grava ato, auditoria nem trilha. O ato de encerramento grava o mesmo de
  hoje (FR-4363).
- **Retenção.** Nada novo é guardado, e por isso nada novo a reter ou descartar.

## Assumptions

- **O Processo tem poucos Editais** — a revisão fala em "poucos" —, e a confirmação é uma tela rara:
  ler o relatório de cada Edital final ali é aceitável. A lista e o detalhe não pagam essa leitura.
- **A regra e a redação da `113` e do relatório da `099` são reutilizadas como estão**: a advertência é
  uma composição delas, com a mesma frase. Se a `113` mudar uma frase, a advertência muda junto.
- **O que o encerramento corta** é o que a seção 7 da revisão verificou contra PostgreSQL (convocar,
  apresentar e conferir documento, Requerimento na convocação e confirmar aviso). A frase da UX-276 só
  afirma o que foi verificado.
- **A `129`** está em PR (#420), sem merge, e não toca a confirmação do Processo; as duas não se
  sobrepõem em arquivo de tela.
- **O texto das frases novas** (UX-275 a UX-277) é proposta e passa pela varredura de vocabulário e pela
  gramática das portas.

## Compatibilidade com regras anteriores

| Regra | O que acontece |
|---|---|
| FR-018 da `002` (o desfecho impedido diz o que o impede, com caminho a cada pendência) | continua: os Editais fora de estado final seguem como recusa certa; a advertência não aparece nesse caso (FR-4357) |
| A decisão de 28/09 sobre o RC-118 (encerrar o Processo exige Editais finais) | continua, e é a única exigência do comando (FR-4362) |
| FR-3534 e FR-3535 da `113` (advertências da confirmação do Edital, da regra do relatório) | reutilizadas, sem mudança, para os Editais finais (FR-4351, FR-4354) |
| FR-3528 a FR-3533 da `113` (o que impede encerrar o Edital) | lidas como advertência no Processo (FR-4353); continuam impedindo o encerramento do Edital |
| FR-3538 e FR-3540 da `113` (caminho a quem a tela aceita; sem dado pessoal) | aplicadas (FR-4355, FR-4356) |
| FR-3541 da `113` (sem nada, não dizer que a seleção foi concluída) | estendida ao Processo, com a ressalva do cadastro de reserva (FR-4359) |
| FR-3543 da `113` (a conferência vale no instante do ato; a recusa reexibe a lista atual) | adaptada: aqui não há recusa, e a lista é relida no envio, com renovação da confirmação (FR-4365) |
| FR-3545 da `113` (não recusar ato posterior; não mexer no encerramento do Processo) | continua: o comando não muda, e a renovação só adia a tentativa (FR-4362, FR-4366) |
| FR-4029 da `126` (convocação sem comunicação é espécie própria) | continua, com a frase dela (FR-4351) |
| A correção A-09 da auditoria de prontidão (#358: Edital final recusa os atos da Retificação) | é a razão de as Retificações ficarem fora (FR-4352) |

## Fora de escopo

- **Impedir o encerramento com providência em aberto** — a primeira decisão da revisão, em aberto.
- **A mesma advertência em "Cancelar Processo"** — o cancelamento também corta o convocado (S3 e S3b da
  revisão). Fica registrado; estender é decisão do usuário.
- **Sinal de "pronto para encerrar" ou "sem providência em aberto" na lista de Processos** — Frente B da
  revisão.
- **Aviso confirmado e ainda não despachado**, e os demais achados A-1 a A-6 da revisão.
- **Estruturar a validade do certame** (campo novo no Edital), que tornaria derivável o "pronto para
  encerrar" — modelo novo, recusado pela revisão.

## Decisões

### D-001 — O título não é o da 113, porque no Processo o que está em aberto é cortado

A confirmação do Edital diz "Continuam depois do encerramento", e lá é verdade: o Edital encerrado ainda
aceita convocação, documento e Requerimento. No Processo é o contrário, para a convocação: o
encerramento a corta. Reusar o título diria ao gestor que o convocado segue, que é o erro que esta spec
existe para evitar. O título passa a dizer onde está ("Em aberto nos Editais deste Processo"), e a frase
de abertura diz o efeito geral; a frase específica da convocação (UX-276) só afirma o que a revisão
verificou. **Alternativa descartada**: uma frase de efeito por tipo — "o recurso continua", "o resultado
não poderá ser divulgado" —, que prenderia ao texto da tela comportamentos que os achados A-1 a A-3
ainda vão decidir.

### D-002 — Período de inscrições e Retificação ficam fora

Os tipos são os da `113`, mas dois grupos não dizem nada verdadeiro num Edital já final:

- **O período**: o Edital encerrado ou cancelado já não recebe inscrição. "O encerramento põe fim ao
  recebimento" falaria de um ato que já aconteceu.
- **A Retificação**: desde a correção A-09 da auditoria de prontidão (#358), o Edital final recusa os
  atos dela, e a seção "Retificações em curso" já diz que ela não pode mais prosseguir. A frase da
  homologada mandaria "publique-a ou devolva-a", que o domínio recusa; e encerrar o Processo não muda
  nada para ela.

**Alternativa descartada**: incluir os dois com frases novas — contraria "as mesmas frases" e não
acrescenta risco que o encerramento do Processo crie.

### D-003 — O que impede encerrar o Edital é advertência no Processo

O prazo de recurso em curso, o recurso sem decisão e a reavaliação ou providência pendentes impedem
encerrar o Edital desde a `113`. Num Edital já final, eles só existem se ele foi encerrado antes da
`113`, ou se nasceram depois (o recurso interposto sem prazo declarado é aceito a qualquer tempo, achado
A-2). Em qualquer caso, aqui são advertência: impedir o Processo por eles seria a regra de domínio que a
décima decisão da revisão deixou de fora. A frase é a mesma da `113`, que já é neutra quanto à espécie.

### D-004 — Com recusa certa, nada é lido

Havendo Edital fora de estado final, o ato vai ser recusado e o Confirmar não é oferecido. Ler o relatório
dos outros Editais ali custaria a leitura mais cara da tela para mostrar algo que não decide nada: o
gestor precisa primeiro encerrar os Editais pendentes, e a confirmação de cada um já adverte o dele. O
mesmo vale para quem não pode encerrar, como na `113`, onde o impedimento esvazia o desfecho.
**Alternativa descartada**: mostrar a advertência dos Editais finais junto da recusa — informativo, mas
desvia do que falta fazer e paga a leitura em todo acesso à tela recusada.

### D-005 — A lista é conferida de novo no envio; o comando não muda

A `113` confere os impedimentos no comando, sob as travas, porque eles recusam. Aqui nada recusa, e
conferir sob as travas não teria o que fazer com o resultado. Mas a confirmação pode ficar aberta por
horas, e a convocação feita nesse intervalo é justamente a que o encerramento corta sem que o gestor a
tenha visto.

**Decidido pelo usuário no esclarecimento de 06/11 (opção B)**: o formulário leva um resumo da lista
mostrada; no envio, a tela relê a lista e, se ela mudou em qualquer coisa, reapresenta a confirmação com
a lista atual, sem tentar o encerramento (FR-4365). É **renovação da confirmação**, e não impedimento: o
gestor que confirma de novo diante da lista atual encerra, com o que estiver em aberto (FR-4366). Nada é
gravado, e as regras de elegibilidade do comando são as de hoje (FR-4362).

**Os dois nomes**: *reexibição* é a confirmação devolvida por uma recusa (do motivo ou do comando);
*reapresentação* é a confirmação devolvida pela renovação, sem chamar o comando. As duas releem a lista
(FR-4360, FR-4365).

**O limite que fica**: entre a releitura na tela e o comando há uma janela — o tempo de uma requisição —
em que uma mudança não é vista (FR-4367). A renovação a reduz de horas para isso, e não a elimina.

**Alternativas descartadas**:
- (A) a lista só da abertura, sem releitura: deixava a janela de horas;
- (C) reapresentar só quando aparece algo novo ou uma contagem sobe: menos interrupção, mas a
  comparação teria de entender cada tipo, e a lista que reduziu também é algo que o gestor não viu;
- (D) reler dentro do comando, sob as travas: fecharia a janela, mas levaria a advertência para o
  domínio e faria dela uma recusa do comando, que é o que a décima decisão da revisão deixou de fora.

### D-006 — Sem registro e sem ciência

Gravar a advertência exibida no ato, ou exigir uma caixa "estou ciente", seria estado persistido novo,
contra o pedido. A `128` recusou a declaração de ciência pelo mesmo motivo. O motivo do encerramento,
obrigatório, continua sendo onde o gestor diz por que encerra; quem quiser registrar que sabia da
convocação escreve ali.

### D-007 — Leitura em lote não é exigida agora

O relatório do Edital é lido por Edital, e a confirmação o lê para cada Edital final publicado. Com
poucos Editais por Processo e uma tela rara, isso basta; o orçamento por Edital é fixado por teste no
plano (SC-1324). A leitura em lote sobre muitos Editais é problema da Frente B da revisão, que a usaria
na lista, e não desta tela.

## Decisão do usuário

### A décima decisão da revisão — antecipar, advertindo

Decidida em 06/11/2026: a advertência sai antes da Frente B, em spec separada da `129`, como correção de
segurança operacional, com a ressalva de que advertir não impede o encerramento.
