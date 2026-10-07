# Feature Specification: O corte emitido depois do recurso não nasce obsoleto

**Feature Branch**: `claude/sweet-faraday-1be5f6`

**Created**: 2026-10-06

**Status**: Implementado

**Input**: o achado [`doc/achado-corte-nasce-obsoleto-apos-recurso.md`](../../doc/achado-corte-nasce-obsoleto-apos-recurso.md),
encontrado e validado em 06/10/2026 sobre a `main` `1d2c26ff`, e a decisão do usuário na mesma data:
adotar a comparação da identidade dos Resultados com o que o ato de ordenação congelou, deixar fora
desta correção a pergunta de quem foi eliminado antes do marco, e verificar a publicação dependente
do corte, que o achado só inferia.

> **Faixa de identificadores.** Abre em **FR-1140** e **SC-440**; não há requisito de experiência.
> O teto medido em 06/10/2026 em todas as worktrees, com quatro dígitos, era de mil cento e trinta e
> um para os requisitos funcionais, quatrocentos e trinta e quatro para os critérios e cento e
> cinquenta para os de experiência — da `060`, aberta em revisão e ainda não mergeada; por isso o
> número vai por extenso, e a faixa desta deixa folga para ela crescer. As decisões desta spec nascem
> em `D-001` e moram no [research.md](research.md); decisão de outra feature é citada pela feature e
> pelo número dela, por extenso.

**A frase que governa:**

> O recurso que a ordem já considerou não torna obsoleto o corte que leu essa ordem.

**E a frase que mantém o corte:**

> Esta feature é a correção de uma pergunta. Nenhuma causa nova de obsolescência, nenhuma tela,
> nenhuma migration, nenhuma escrita; o recurso deferido **depois** do corte continua tornando-o
> obsoleto exatamente como antes.

---

## Por que esta feature existe

A `014` fez o corte ficar obsoleto quando alguém **reingressa no universo do ato de ordenação** que
ele cita (`FR-218`), e proibiu que o reingresso que **não** alcança esse ato o obsoletasse
(`FR-230`), porque isso *"bloquearia trabalho para exigir uma geração sucessora idêntica à
anterior"*. A decisão 008 da `014` resume: *"um ato que não muda nada não é ato, é cerimônia"*.

O código fazia a pergunta pela metade. Ele perguntava se algum participante do ato tinha, numa Etapa
que produziu a ordem, um Resultado vigente que **sucede** outro — e não perguntava se o ato **já
citava** esse sucessor. Um Resultado sucessor continua sucessor para sempre; logo, depois do primeiro
deferimento numa Etapa da ordem, toda geração de corte daquela lista nascia obsoleta:

| Cronologia | O que o ato que o corte leu cita | Antes desta feature |
|---|---|---|
| corte emitido → recurso deferido | o Resultado **superado** | obsoleto, com a causa *participante reingressou* — correto (`FR-218`) |
| recurso deferido → ordem sucessora → corte emitido | o Resultado **sucessor** | obsoleto também — e é a cronologia de todo certame em que a definitiva sai antes do corte |

E a obsolescência não é só aviso. Ela bloqueia distribuir, concluir e consolidar na Etapa governada
(`FR-228`) e impede publicar o resultado que dependa da faixa (`FR-219`). A recusa manda *"emitir a
geração sucessora"* — que lê o mesmo ato e nasce obsoleta pela mesma razão. Não havia saída.

O achado apareceu no banco de demonstração do Edital 72/2026, nas listas de ampla concorrência de
dois marcos, com o corte emitido oito dias depois da ordem sucessora.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — O corte emitido sobre a ordem que já considerou o recurso está em dia (Priority: P1)

A presidência julgou os recursos da preliminar, emitiu a ordem sucessora, publicou a definitiva e,
dias depois, emitiu o corte. A tela do corte e a da ordenação mostram a faixa em dia; a Etapa
governada recebe trabalho novo; a geração sucessora, se alguém a emitir por outra razão, também nasce
em dia.

**Why this priority**: sem isso, todo certame com recurso deferido numa Etapa que produz a ordem
trava a Etapa governada para sempre.

**Independent Test**: num Edital com corte, deferir recurso sobre um Resultado da Etapa que produz a
ordem, emitir a ordem sucessora e então o corte; perguntar o estado do corte e o impedimento da
Etapa governada.

**Acceptance Scenarios**:

1. **Given** um recurso deferido e a ordem sucessora emitida, **When** o corte é emitido sobre ela,
   **Then** o corte não está obsoleto e não nomeia causa nenhuma.
2. **Given** esse corte, **When** a prontidão da Etapa governada é lida, **Then** não há impedimento
   por corte obsoleto.
3. **Given** esse corte, **When** a geração sucessora é emitida sobre o mesmo ato, **Then** ela
   também está em dia.

---

### User Story 2 — A publicação que depende do corte não é impedida pelo recurso que a ordem já considerou (Priority: P1)

A ordem sucessora e o corte que a leu estão em dia; publicar o resultado que depende da faixa segue
as guardas de sempre, sem o impedimento de corte obsoleto.

**Why this priority**: o impedimento de publicação (`FR-219`) é o mais visível dos efeitos, e até
esta feature ele era só inferido pela leitura do código.

**Independent Test**: a mesma cronologia da US1, seguida da aferição de publicabilidade do ato
vigente do marco.

**Acceptance Scenarios**:

1. **Given** recurso deferido, ordem sucessora e corte emitido depois, **When** a publicabilidade do
   ato vigente é aferida, **Then** o código não é o de corte obsoleto.

---

### User Story 3 — O recurso deferido depois do corte continua tornando-o obsoleto (Priority: P1)

O corte já foi emitido; depois disso, um recurso muda um Resultado de uma Etapa que produziu a
ordem. A faixa fica obsoleta, a causa é *participante reingressou*, a Etapa governada bloqueia
trabalho novo e a publicação dependente é impedida — como sempre foi.

**Why this priority**: é a garantia que a `014` construiu, e a correção não pode afrouxá-la.

**Independent Test**: os testes existentes da `014` para essa cronologia, sem edição, e um teste
novo para a publicação dependente nessa mesma cronologia.

**Acceptance Scenarios**:

1. **Given** um corte emitido, **When** um recurso é deferido sobre Resultado de Etapa da ordem,
   **Then** o corte fica obsoleto com a causa *participante reingressou*.
2. **Given** o mesmo estado, **When** a publicabilidade do ato vigente é aferida, **Then** a
   publicação é impedida por corte obsoleto, com essa causa.
3. **Given** um corte emitido, **When** o recurso é deferido na Etapa **governada**, **Then** o corte
   não fica obsoleto (`FR-230`, inalterado).

---

### Edge Cases

- **Corte emitido antes desta correção, sobre ordem que já considerou o recurso.** Fica em dia sem
  ato nenhum: a obsolescência é comparação feita na leitura, e não estado gravado. Medido no banco de
  demonstração do 72/2026.
- **Dois deferimentos, um antes e outro depois da ordem sucessora.** O primeiro está citado, o
  segundo não: o corte fica obsoleto pelo segundo. A pergunta é "existe sucessor não citado", e não
  "todos os sucessores são não citados".
- **Sucessor de sucessor.** Só o vigente é perguntado; se o ato cita o vigente, está em dia; se cita
  um anterior a ele, não está.
- **Ato de sorteio.** Não tem Etapas que produzem a ordem, e a pergunta continua não se colocando.
- **Quem foi eliminado numa Etapa anterior à última que o marco enumera, e reabilitado.** Não está
  entre os participantes do ato e não é visto por esta pergunta, nem antes nem depois desta feature.
  Fica fora, registrado à parte (`D-002`).

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-1140**: O reingresso que torna o corte obsoleto, na forma do `FR-218`, MUST ser o de
  Resultado sucessor vigente, de participante do ato de ordenação citado, numa Etapa que produziu a
  ordem, que esse ato **não** cite entre os Resultados que congelou.
- **FR-1141**: Resultado sucessor que o ato de ordenação citado já cite MUST NOT tornar o corte
  obsoleto: o deferimento já está na ordem que a faixa leu, e a geração sucessora sairia idêntica
  (`FR-230`; decisão 008 da `014`).
- **FR-1142**: A comparação MUST ser pela identidade dos Resultados, e MUST NOT depender do instante
  da consolidação, da decisão ou da emissão.
- **FR-1143**: O bloqueio de trabalho novo na Etapa governada (`FR-228`) e o impedimento da
  publicação que dependa da faixa (`FR-219`) MUST seguir a mesma resposta, sem regra própria.
- **FR-1144**: A geração sucessora emitida sobre o mesmo ato MUST nascer em dia quando nenhuma outra
  causa a alcance: o caminho que a recusa indica MUST levar a algum lugar.
- **FR-1145**: As demais causas — ordem sucedida, regra alterada, quadro alterado — e o deferimento
  na Etapa governada MUST NOT mudar de comportamento.
- **FR-1146**: A correção MUST NOT escrever, migrar nem alterar corte emitido. Corte já emitido
  MUST ficar em dia pela leitura, sem ato novo.
- **FR-1147**: A pergunta MUST continuar sendo uma consulta só.

### Key Entities

- **Ato de ordenação**: congela, no universo, os participantes e os Resultados de Etapa que produziram
  a ordem, pela identidade de cada um. É essa lista que esta feature passa a consultar.
- **Resultado de Etapa**: append-only; o deferimento produz um sucessor que cita o superado.
- **Corte**: lê um ato de ordenação; a obsolescência dele é calculada, não gravada.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-440**: Na cronologia *recurso deferido → ordem sucessora → corte*, os quatro efeitos — estado
  do corte, bloqueio da Etapa governada, geração sucessora e publicação dependente — saem em dia.
  Antes desta feature, saíam os quatro obsoletos ou impedidos.
- **SC-441**: Na cronologia *corte → recurso deferido*, o corte continua obsoleto com a causa
  nomeada, a Etapa governada continua bloqueada e a publicação dependente continua impedida; os
  testes que já cobriam essa cronologia passam sem edição.
- **SC-442**: A suíte completa contra PostgreSQL passa, e nenhum teste existente é editado.

### O que esta feature não cobre, deliberadamente

- A reabilitação de quem foi eliminado numa Etapa anterior à última que o marco enumera (`D-002`).
- Qualquer mudança no texto das causas, nas telas ou na ordem em que a publicabilidade as afere.

---

## Assumptions

- O `stageResults` do ato é confiável como registro do que ele leu: a trigger de proveniência da
  `015` confere cada item contra a linha append-only do Resultado no momento da emissão.
- A ordem sucessora cita o Resultado **vigente**: o cálculo da ordem lê pelo gerenciador de
  vigentes, que é a garantia da `018`.
