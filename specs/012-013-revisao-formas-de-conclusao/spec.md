# Revisão de compatibilidade 012–013: a Etapa publica a forma da conclusão

**Criada em**: 2026-09-03 · **Status**: emenda aprovada, plano em execução

> **Este documento não cria requisito.** Ele delimita uma revisão que atravessa duas features já
> entregues e aponta para onde os requisitos moram. A norma está nas duas specs emendadas, e
> duplicá-la aqui criaria a segunda fonte divergente que o Princípio I proíbe.

## Onde estão os requisitos

| documento | o que ele traz |
|---|---|
| [`specs/012-mesa-de-avaliacao/spec.md`](../012-mesa-de-avaliacao/spec.md) | **D-008** no §5 e a revisão transversal — FR-116 a FR-124, FR-119 a FR-121, SC-032 a SC-039, EC-021 e EC-022 |
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

## Fora de escopo

Barema estruturado, terceira forma de conclusão (conceito ordinal), regra de combinação entre
avaliações, sorteio, progressão de fila, classificação, cotas, heteroidentificação, recurso e
convocação. A metade `documentRequirements` da lacuna E2E-004 também fica de fora — é grupo novo no
formulário de Retificação, e trabalho de outra natureza.
