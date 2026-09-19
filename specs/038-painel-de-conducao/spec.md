# Feature Specification: Painel de condução do Processo vivo

**Feature Branch**: `claude/spec-038-painel`

**Created**: 2026-09-19

**Status**: Draft

**Input**: reauditoria de 2026-09-16 — `ACH-25` (S2/P2), raiz estrutural `E-6`, melhoria 13.6. Item 1 da ordem de investimento confirmada em 19/09.

> **Faixa de identificadores.** Esta spec abre em **FR-556**, **SC-196** e **UX-063**. Teto medido em
> 19/09/2026 na `main` `6f322e4` e em todas as worktrees: **FR-555 / SC-195**. O `UX-062` está
> **reservado pela `037`** e ainda não definido; esta spec não o disputa. As **decisões** reiniciam
> em `D-001`.

> **Teto proporcional.** Esta spec cabe em **três histórias** e **doze requisitos**, por decisão de
> método tomada em 19/09: a semana produziu 2496 linhas de spec para uma mudança que removeu código.
> **Requisito que existe para impedir alguém de ler errado outro requisito não é requisito** — é nota
> de tarefa, e foi escrito como tal.

---

## Por que esta feature existe

**O guia desliga quando o Edital é publicado.** A composição conduz com excelência; publicado o
Edital, a página do Processo lista Editais e oferece encerrar ou cancelar — justo quando há
inscrições chegando, comissão a compor e avaliação a organizar.

A visão global é a **pior nota do produto — 5** — e atravessou **seis** features sem ser tocada.

**E a melhoria 13.6 diz o que esta feature não é**: *"Não é fazer um dashboard: é não desligar o guia
que já existe."*

### O que já existe, medido — e é mais do que a auditoria supunha

A Supervisão tem **pulso** e **Atenção**. O pulso dá, por Edital: submetidas, rascunhos, período com
situação e restante, série e próximos marcos. A Atenção tem **seis** espécies de sinal, cada uma com
destino que resolve:

| Espécie | Cobre |
|---|---|
| `UX-001` | Etapa sem marco no cronograma |
| `UX-002` | divergência entre estado declarado e posição temporal |
| `UX-003` | **cobertura** de avaliação insuficiente — quantos avaliadores por Etapa |
| `UX-004` | ato de ordenação vigente **obsoleto** |
| `UX-005` | recurso pendente com a **comissão inteira impedida** |
| `UX-046` | acervo que declara vaga imediata sem linha do quadro |

### As três medições que mudam o desenho

**1. Duas delas parecem cobrir o que não cobrem.** O `UX-003` mede *cobertura* — se há avaliadores
suficientes —, e **não trabalho pendente**: uma Etapa bem coberta com cinquenta avaliações paradas
não produz sinal. E o `UX-005` tem mensagem que começa *"Há recurso aguardando julgamento…"*, mas sua
condição é **a comissão inteira impedida**: recurso pendente com julgador disponível não produz sinal
nenhum. *Ler a mensagem em vez da condição erra os dois.*

**2. O catálogo é fechado por requisito, e o requisito já está desatualizado.** A `FR-024` da `022`
diz que o sistema MUST apresentar *"exclusivamente os sinais definidos em `UX-001` a `UX-005`"*. A
`027` acrescentou o `UX-046` **sem revisá-la**. Hoje há **seis espécies no código e um requisito
vigente que diz cinco**.

**3. O produto não sabe quem precisa agir, e isso não é defeito.** O próprio `UX-005` registra por
escrito: *"o sistema não sabe quem a possui: os papéis vêm da sessão, e não há registro que ligue
identidade a papel"*. Um painel que prometesse **responsável** afirmaria o que os dados não
sustentam.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - O Processo diz onde cada Edital está (Priority: P1)

Quem abre o Processo vê, por Edital, o que já se sabe: quanto chegou, o que vem, e o que pede ação —
em vez de uma lista de Editais com dois atos terminais.

**Why this priority**: é a metade da melhoria que **não cria nada**. O pulso e a Atenção existem e
estão numa tela só. Entrega sozinha, e é o MVP.

**Independent Test**: abrir a página de um Processo com Editais publicados e conferir que o pulso e
os sinais aparecem ali, com os mesmos valores da Supervisão.

**Acceptance Scenarios**:

1. **Given** um Processo com Editais publicados e inscrições em curso, **When** alguém o abre,
   **Then** lê, por Edital, o pulso e os sinais que hoje só a Supervisão mostra.
2. **Given** o mesmo Processo, **When** os dois são comparados, **Then** Processo e Supervisão
   **dizem a mesma coisa** — derivam da mesma leitura, e não de duas.
3. **Given** um ator que **não alcança** o destino de um sinal, **When** a página é montada,
   **Then** o sinal não lhe oferece caminho que ele não abre.
4. **Given** um Processo sem sinal algum, **When** a página é montada, **Then** a ausência é **uma
   linha declarada**, e não uma seção vazia por espécie.

---

### User Story 2 - A Atenção alcança a cauda (Priority: P2)

O que está parado depois da avaliação passa a produzir sinal: trabalho de avaliação pendente, recurso
esperando julgamento, ato calculado e não publicado, recorte apurável e não apurado.

**Why this priority**: é onde a auditoria disse que a visão global some. Sem ela a `US1` reúne bem o
que já existe, e continua cega da avaliação em diante.

**Independent Test**: deixar trabalho parado em cada um dos quatro estados e conferir que cada um
produz sinal com destino que resolve.

**Acceptance Scenarios**:

1. **Given** uma Etapa com avaliações distribuídas e não concluídas, **When** a Atenção é montada,
   **Then** há sinal que **nomeia a Etapa e o Edital** e leva ao trabalho.
2. **Given** um recurso aguardando julgamento **com julgador disponível**, **When** a Atenção é
   montada, **Then** há sinal — hoje não há.
3. **Given** um ato de ordenação emitido e **não publicado**, **When** a Atenção é montada, **Then**
   há sinal que leva à publicação daquele resultado.
4. **Given** um recorte com ordem vigente e ocupação **não apurada**, **When** a Atenção é montada,
   **Then** há sinal que leva à ocupação daquele recorte.
5. **Given** qualquer dos quatro, **When** a mensagem é escrita, **Then** ela **não nomeia pessoa
   responsável** — o sistema não liga identidade a papel, e afirmar isso seria afirmar o que os
   dados não sustentam.

---

### User Story 3 - O catálogo volta a ser verdade (Priority: P3)

O requisito que fecha a lista de sinais passa a dizer a lista que existe.

**Why this priority**: é dívida de consistência, não de comportamento — mas é dívida que **esta
feature agrava**, porque acrescenta espécies a um catálogo que já diverge.

**Independent Test**: ler o requisito vigente e a lista de espécies do produto, e conferir que
coincidem.

**Acceptance Scenarios**:

1. **Given** o catálogo depois desta feature, **When** o requisito que o fecha é lido, **Then** ele
   nomeia **todas** as espécies vigentes, inclusive a que a `027` acrescentou.
2. **Given** a `FR-024` da `022`, **When** esta feature é aplicada, **Then** ela é **explicitamente
   substituída**, e não silenciosamente contrariada.

---

### Edge Cases

- **Processo sem Edital publicado.** O painel não inventa notícia: sem Edital vivo não há condução a
  mostrar, e a ausência é dita.
- **Edital encerrado ou cancelado.** Não produz sinal de trabalho pendente — o que parou, parou por
  ato.
- **Ator que alcança o Processo e nenhum dos destinos.** Lê o estado e não recebe caminho algum.
- **Avaliação pendente em Etapa cuja distribuição ainda não houve.** São dois sinais diferentes, e o
  `UX-003` já cobre o segundo: a feature não pode fazer os dois dispararem pelo mesmo fato.
- **Recurso pendente com comissão inteira impedida.** Continua sendo o `UX-005`, e **não** o sinal
  novo: um fato, um sinal.

---

## Requirements *(mandatory)*

### O Processo passa a conduzir

- **FR-556**: A página do Processo MUST apresentar, por Edital, o **pulso** e a **Atenção** que hoje
  existem apenas na Supervisão.
- **FR-557**: Cada indicador MUST derivar da **mesma leitura** que governa a tela de destino, e
  MUST levar a ela. *Indicador que calcula por conta própria é a segunda verdade que este projeto
  passou a semana removendo.*
- **FR-558**: Nenhum indicador MUST oferecer destino que o ator não alcança — é a garantia da `033`,
  e esta feature não a desfaz.
- **FR-559**: Sinal ausente MUST NOT ocupar espaço, e a ausência de todos MUST ser **uma linha
  declarada** (mantém a `FR-025` da `022`).

### A Atenção alcança a cauda

- **FR-560**: A Atenção MUST sinalizar **trabalho de avaliação pendente** — distribuído e não
  concluído —, nomeando Etapa e Edital. *Distinto da cobertura, que o `UX-003` já mede.*
- **FR-561**: A Atenção MUST sinalizar **recurso aguardando julgamento** quando **há julgador
  disponível**. O caso da comissão inteira impedida continua sendo o `UX-005`: **um fato, um sinal**.
- **FR-562**: A Atenção MUST sinalizar **ato emitido e não publicado**, levando à publicação daquele
  resultado.
- **FR-563**: A Atenção MUST sinalizar **recorte com ordem vigente e ocupação não apurada**, levando
  à ocupação daquele recorte.
- **FR-564**: Nenhum sinal MUST nomear **pessoa responsável**. O produto não liga identidade a papel
  — o `UX-005` já registra isso por escrito —, e nomear responsável afirmaria o que os dados não
  sustentam.

### O que esta feature corrige e o que ela não faz

- **FR-565**: A `FR-024` da `022` MUST ser **explicitamente substituída**, e o requisito sucessor
  MUST nomear todas as espécies vigentes — inclusive a que a `027` acrescentou sem revisá-la.
  *Requisito que diz cinco onde há seis não fecha catálogo nenhum.*
- **FR-566**: Nenhuma **capacidade de autorização** nova, nenhuma **ajuda instrucional** nova nos
  cartões, nenhum conteúdo publicado reescrito, e nada apagado.
- **FR-567**: Nenhum **estado novo** MUST ser calculado. Esta feature **reúne e encaminha** o que o
  produto já sabe; se um estado da cauda não for derivável hoje, ele fica **registrado como achado**,
  e não implementado às pressas.

---

## Success Criteria *(mandatory)*

- **SC-196**: Quem abre um Processo com Editais vivos lê, **na primeira tela**, onde cada um está e
  o que pede ação — percorrido pela interface, sem shell e sem banco.
- **SC-197**: **Zero** divergências entre o que o Processo e a Supervisão dizem sobre o mesmo Edital.
- **SC-198**: Os **quatro** estados da cauda produzem sinal, e cada um leva a uma tela que resolve —
  conferido clicando os quatro.
- **SC-199**: **Zero** sinais que nomeiem pessoa, e **zero** destinos oferecidos a quem não os abre.
- **SC-200**: O requisito que fecha o catálogo nomeia **exatamente** as espécies que o produto
  apresenta — conferido contando as duas listas.

---

## Assumptions

### D-001 — o painel vive no Processo, e a Supervisão não é duplicada

A melhoria não decide onde. Decidido: **a página do Processo**, porque é ela que hoje perde a
capacidade de orientar depois da publicação — a Supervisão já conduz.

**A Supervisão não ganha cópia.** As duas leem a mesma derivação; o Processo mostra por Edital, a
Supervisão mantém o recorte que já tem. *Duas telas com o mesmo número calculado duas vezes é o
defeito que a `FR-557` existe para impedir.*

### D-002 — o que é sinal e o que é pulso

A `022` separou **Pulso** de **Atenção**, e a separação é de natureza: pulso é **leitura** — quanto
chegou, quando encerra; sinal é **coisa parada que alguém resolve**, e por isso tem destino.

Os quatro estados desta feature são **sinais**: os quatro descrevem trabalho parado com tela que o
resolve. Sorteio e matrícula **ficam de fora por ora** — o primeiro é ato com momento próprio, o
segundo é superfície que ainda não teve auditoria de UX. Ficam **registrados**, não implementados.

### D-003 — o produto não afirma quem precisa agir

O relatório longitudinal pede *"trabalho pendente por tipo e responsável funcional"*. **A segunda
metade não é entregável**: papéis vêm da sessão e não há registro que ligue identidade a papel.

O painel diz **o que está parado e onde se resolve**. Quem resolve é pergunta que o produto hoje não
pode responder, e inventá-la seria a pior espécie de painel — o que parece saber.

---

## Out of Scope

Cada um com spec própria: as **sete recusas** com a fronteira `403`/`404` (`D-G2`); a **validação
cruzada** entre fontes normativas (`E-4`); o **renderizador normativo único** (`E-3`); a
**organização do trabalho por Perfil/polo** (`ACH-60`); a **`FR-461` impeditiva** (`D-G1`); a
**ocorrência externa do sorteio** (`D-G3`); a **Retificação que acrescenta Modalidade** (`D-G5`); e a
**densidade da Classificação** (`ACH-10`/`ACH-05`).

**Dependência registrada**: a `037` está em CI e altera `interface/views.py`, `acoes.py` e
`detalhe.html`. Esta spec **não mediu** essas três superfícies; se o plano precisar do cartão do
Edital, mede **depois** que a `037` entrar.
