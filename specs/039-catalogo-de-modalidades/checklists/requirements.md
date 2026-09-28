# Specification Quality Checklist: O catálogo de Modalidades do Edital

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-19 · **Reescrita**: 2026-09-20
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

## O que a reescrita mudou, e por quê

**A primeira redação estava errada no desenho, não na prosa.** Ela propunha um rótulo de família
sobre as Modalidades existentes. A medição de 20/09 mostrou três coisas que derrubaram essa escolha:
nada no produto deduz o Perfil a partir da Modalidade; a espinha guarda o identificador em par com o
Perfil e portanto não se move; e o **fundamento normativo é um-para-um com a Modalidade**, de modo
que o rótulo deixaria 32 cópias da mesma lei no lugar e colaria uma etiqueta por cima.

**A auditoria de convergência de 20/09 mudou o escopo em três pontos**, e a reescrita os incorpora:

1. **A `D-G5` deixou de ser spec própria.** Ela é o terceiro investimento recomendado, e é a única
   pendência que descreve Edital publicado sem conserto. Com a Modalidade virando coisa do Edital,
   acrescentá-la por Retificação é entrar numa lista que já existe — Perfis, Cronograma, Anexos.
   Entregar o catálogo sem ela reproduziria o beco na forma nova.
2. **A grafia dupla da ampla concorrência** deixou de ser apenas "não quebrar" e virou recusa
   declarada (`D-004`). A auditoria mediu um Edital real com três nomes para duas coisas, e esta é a
   feature em que o catálogo nasce.
3. **O alcance da Etapa saiu**, pela cláusula de escape que a redação anterior já previa e que quem
   governa o backlog manteve. A medição fez a cláusula disparar.

**O sequenciamento está registrado e não escondido.** A auditoria põe esta feature em terceiro, atrás
de fechar a `038` e de derivar o campo derivado. A spec diz isso por escrito, para que antecipá-la
seja escolha e não esquecimento.

## Notas para o planejamento

- **O degrau de elevação é mecanismo novo**: seria o primeiro que move uma coleção de nível em vez de
  acrescentar campo. O Phase 0 deve desenhá-lo antes de qualquer outra coisa.
- **A verificação nova** que a mudança de nível torna necessária: a linha do Quadro de Vagas precisa
  apontar Modalidade que o Perfil oferece. Antes isso era garantido pela estrutura.
- **A conta de tarefas vai passar das 22 da `038`**, e a causa são as fixtures: 53 arquivos de teste
  montam conteúdo com a Modalidade dentro do Perfil. Largo e raso — recontar caso a caso, porque a
  `034` previu oito e entregou doze.
