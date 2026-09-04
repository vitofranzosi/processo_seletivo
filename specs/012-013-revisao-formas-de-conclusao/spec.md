# Revisão de compatibilidade 012–013: a Etapa publica a forma da conclusão

**Criada em**: 2026-09-03 · **Status**: emenda aprovada, plano em execução

> **Este documento não cria requisito.** Ele delimita uma revisão que atravessa duas features já
> entregues e aponta para onde os requisitos moram. A norma está nas duas specs emendadas, e
> duplicá-la aqui criaria a segunda fonte divergente que o Princípio I proíbe.

## Onde estão os requisitos

| documento | o que ele traz |
|---|---|
| [`specs/012-mesa-de-avaliacao/spec.md`](../012-mesa-de-avaliacao/spec.md) | **D-008** no §5 e a revisão transversal — FR-116 a FR-124, SC-032 a SC-039, EC-021 e EC-022 |
| [`specs/013-consolidacao-resultado-etapa/spec.md`](../013-consolidacao-resultado-etapa/spec.md) | **D-008**, a contraparte — FR-046 a FR-050, SC-012 a SC-015 |
| [`doc/decisao-012-conclusao-decisoria.md`](../../doc/decisao-012-conclusao-decisoria.md) | a decisão de domínio e os três Editais reais que a motivaram |
| [`doc/briefing-revisao-012-013-formas-de-conclusao.md`](../../doc/briefing-revisao-012-013-formas-de-conclusao.md) | o handoff, o mapa da emenda e a pergunta que foi fechada |

## Por que a revisão tem diretório próprio

Ela não é feature nova e não recebe número de feature. É **uma mudança de requisito que atravessa
duas features já implementadas**, e o par tem de mudar junto: emendar só a 012 produziria um sistema
em que o avaliador conclui "indeferido" e a Etapa nunca produz resultado.

Os `plan.md`, `research.md`, `data-model.md`, `quickstart.md` e `tasks.md` de 012 e de 013
descrevem a construção original e continuam válidos como registro dela. Sobrescrevê-los apagaria a
história de duas entregas para acomodar uma terceira. Os artefatos desta revisão vivem aqui.

## Escopo, em uma frase

> Avaliar deixa de significar pontuar. A Etapa publica qual das duas formas de conclusão exige, e as
> duas atravessam o sistema da Mesa ao Resultado oficial, sem que nenhuma escala numérica seja
> inventada onde o Edital não publicou nenhuma.

## Mapa de execução

**Referencial, e não normativo.** Cada linha aponta para os requisitos que valem — que moram nas duas
specs — e para a jornada que a demonstra. É o que permite gerar tarefas sem reprocessar as histórias
originais de 012 e 013, que já estão entregues.

| # | História de execução | Prioridade | Requisitos | Jornada | Fase |
|---|---|---|---|---|---|
| **E1** | Elaborar e publicar uma Etapa decisória, com os rótulos que o Edital escolheu | **P1** | 012: FR-119, FR-121, SC-016, SC-038 · contrato v6 | [J1](./quickstart.md) | F1 |
| **E2** | Retificar um Edital publicado antes do salto, e retificar a forma de uma Etapa | **P1** | 012: FR-098, FR-120, FR-010, EC-021, SC-037 | J5, J6 | F2 |
| **E3** | Concluir uma avaliação sem nota, e ser recusado ao misturar as formas | **P1** | 012: FR-116, FR-117, FR-118, FR-123, SC-032 a SC-034, SC-036 | J2 | F3, F4 |
| **E4** | Ler no Edital publicado como a Etapa é concluída | **P2** | 012: FR-119, SC-016 · P-007 | J1 | F5 |
| **E5** | Oficializar o Resultado da Etapa decisória | **P1** | 013: FR-046, FR-049, FR-016, FR-025, SC-012 | J3 | F6 |
| **E6** | Não oficializar o que o Edital não publicou | **P1** | 013: FR-047, FR-048, SC-013, SC-014 | J4 | F6 |
| **E7** | Provar que nada da forma pontuada mudou, e que o salto funciona com dados | **P1** | 012: FR-124 · 013: FR-050 | garantias de banco | F7 |

As fases F1 a F7 estão em [plan.md](./plan.md); as jornadas J1 a J6, em
[quickstart.md](./quickstart.md).

**E7 não é fase de encerramento decorativa.** A revisão mexe em três tabelas com dados históricos e
em duas triggers append-only; a suíte comum roda sobre banco já migrado e por isso não demonstra o
salto. Sem E7, o que se prova é que o esquema novo funciona — não que a migração até ele funciona.

## Fora de escopo

Barema estruturado, terceira forma de conclusão (conceito ordinal), regra de combinação entre
avaliações, sorteio, progressão de fila, classificação, cotas, heteroidentificação, recurso e
convocação. A metade `documentRequirements` da lacuna E2E-004 também fica de fora — é grupo novo no
formulário de Retificação, e trabalho de outra natureza.
