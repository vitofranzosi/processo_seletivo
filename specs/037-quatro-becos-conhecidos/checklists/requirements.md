# Specification Quality Checklist: Quatro becos que o sistema já conhece

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-19
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## As decisões desta feature, e por que elas são decisões

| Decisão | Onde | Por quê |
|---|---|---|
| A tela do corte não é reescrita | `D-001` | ela já explica; uma segunda frase sobre o mesmo estado diverge na primeira mudança |
| A condução nasce na tela, não na mensagem normativa | `D-002` | condução depende de quem lê, e o domínio não conhece o ator — *"peça a alguém com a permissão de X"* é falso para quem tem X |
| O peso continua sendo da Etapa | `D-003` | a direção literal do achado exigiria mudança de modelo; a contradição antecipa em vez de o campo se mover |

## O que a medição corrigiu antes de a spec ser escrita

| Afirmação de partida | O que a medição achou |
|---|---|
| "o link precisa levar a uma tela que explique" | a tela **já explica** — metade do requisito não precisa ser escrita (`D-001`) |
| "a régua deve olhar o término" | ao pé da letra, **silenciaria o Evento pontual**; a regra é *havendo término, o término; não havendo, o início* (`FR-546`) |
| "pedir o peso onde a Etapa é enumerada" | o peso é campo **da Etapa**, e o marco enumera por seleção múltipla — seria mudança de modelo (`D-003`) |
| "três telas calam" | são **duas**: a `033` já fechou a terceira |

## O que o Phase 0 achou depois, e que a spec não previa

| Achado | Consequência |
|---|---|
| a tela do corte anexa **um** caminho a **três** recusas, e ele serve a duas | `FR-539a` — a feature criaria um beco no fim do caminho que abre |
| o `ACH-02` já diz "o que falta", com caminho | `FR-542` reescrita e `FR-542b` — o percurso decide se ainda há o que fechar |
| a formulação existe como **mecanismo público**, não como padrão a copiar | `FR-543` — imitar o texto derrota a guarda que a `033` deixou |
| a escolha do instante da frase discordaria da régua | `FR-546a` — as duas mudam no mesmo ato |
| o canal do candidato deriva a situação por conta própria | `FR-549a` — concordância de desfecho, não de código |

## O que o `analyze` achou, e que nenhuma das contas via

A conta de cobertura deu **33/33** antes deste passo. Ela não vê requisito coberto por tarefa que
não o satisfaz.

| Achado | O que estava errado |
|---|---|
| **C1** | a `US2` prescrevia prosa no aviso ignorando `acoes.py`, que **já deriva** "pode retificar?" e **já entrega** o caminho a quem pode |
| **H1** | o caminho da `FR-539a` leva à Retificação, que quem classifica pode não alcançar — o beco da `033` dentro da correção do `ACH-46` |
| **H2** | o `plan.md` ainda dizia *"telas diferentes, nenhuma dependência"* depois de o `tasks` medir que três histórias tocam o mesmo arquivo |
| **H3** | o cenário 2 da `US2` era incondicional e a `FR-542b` autoriza a perna em que ele não se aplica |
| **H4** | a `SC-189` alcança só o cartão do Edital; o `ACH-02` ficava sem critério em qualquer das duas saídas |
| **M1** | a `T014` fala de "a tela", e o parcial é incluído por **oito** |
| **M2** | as **quatro** rotas que consomem a lista de Etapas não tinham contraprova |
| **L1** | a `FR-539` é proibição de reescrever, e nada afirmava a frase **literalmente** |

## A segunda passada do `analyze`, e o padrão que ela expôs

**Seis dos oito achados eram a mesma espécie**: a `US2` foi reescrita na primeira passada e quatro
artefatos continuaram descrevendo a versão anterior — o título da história, o resumo do plano, o
objetivo da fase, o `data-model` e o `quickstart`. Na `036` foram sete pontos; aqui, quatro.
**Emenda tardia propaga mal por natureza**, e é por isso que a segunda passada existe.

| Achado | O que estava errado |
|---|---|
| **H1** | a `FR-541` mandava o aviso nomear **sem condição**, e a `FR-541b` mandava calar — a forma exata da `FR-500 × FR-501a` da `034`, que sobreviveu a três passadas |
| **H2** | a `FR-539b` e a `FR-540` diziam "alcança" para capacidades diferentes — retificar e classificar — sem nomear nenhuma |
| **H3** | o `data-model` ainda dizia `US2 \| duas frases \| prosa`, e a `US2` mexe em derivação e pode produzir **uma** frase |
| **M1** | objetivo e teste independente da fase 4, incondicionais |
| **M2** | o cenário 2 prometia "as duas frases" e citava só a `SC-189`, reescopada |
| **M3** | o resumo do plano — o mesmo lugar onde a independência sobreviveu à primeira passada |
| **M4** | o título da `US2` prometia o que a `FR-542b` autoriza a não acontecer |
| **L1** | a `T011` produzia o desfecho da `SC-195` sem citá-la |

## A revisão externa, e as três contradições executáveis

Passaram pelas duas passadas do `analyze` porque **nenhuma delas é detectável por contagem**: as três
eram requisitos que, lidos sozinhos, faziam sentido.

| Achado | O que estava errado |
|---|---|
| **I1** | a `FR-543a` exigia a forma cheia e a `FR-543` proibia escrever à mão — e o mecanismo **não produz** a forma cheia (`R-11`) |
| **I2** | a `FR-554` proibia ajuda visível no cartão, e a `FR-551` mandava acrescentar uma frase ao cartão |
| **I3** | a `FR-553` e a `SC-194` negavam a mudança de decisão que a `US3` faz **de propósito** |
| **U1** | o marco por sorteio estava no caso de borda e em nenhuma contraprova |
| **I4** | *"nenhuma capacidade nova"* conflitava com a linguagem do princípio VI |
| **I5** | o quinto portão citava a tarefa errada da recontagem |

**As três `HIGH` têm a mesma forma**: uma promessa geral escrita antes de a feature saber o que ia
fazer, e que a feature depois desrespeita legitimamente. O remédio não é cumprir a promessa — é
**restringi-la ao que ela realmente protege**.

## Notes

- Items marked incomplete require spec updates before `$speckit-clarify` or `$speckit-plan`
- As quatro medições de partida **devem ser reconferidas pelo Phase 0 do plano**. Nas quatro
  features anteriores a medição corrigiu a spec cinco vezes, e três das correções acima já vieram
  dessa disciplina.
