# Checklist de operação: Ações disponíveis

**Purpose**: Avaliar a qualidade dos requisitos da 104 em clareza semântica, ambiguidade, cobertura
de papéis, autorização, acessibilidade, estados vazios, escala, continuidade operacional e
rastreabilidade dos critérios.
**Created**: 2026-10-30
**Feature**: [spec.md](../spec.md)

> **Dono**: quem revisa. `[x]` significa que quem revisa julgou o critério de qualidade do requisito
> satisfeito, e não que a implementação está pronta. Gerado sem marcas; profundidade padrão, para a
> revisão do PR.

## Clareza semântica

- [ ] CHK001 - Os cinco termos (ação disponível, em acompanhamento, pendente no escopo, impedimento, marco previsto) estão definidos de modo que cada objeto caia em exatamente um deles? [Clarity, Spec §Key Entities]
- [ ] CHK002 - "Ato principal da situação" está definido para cada situação de Edital e de Retificação, sem depender de leitura do código? [Clarity, Spec §FR-2802, §D-003]
- [ ] CHK003 - Os rótulos da faixa evitam sugerir atribuição nominal, e isso está escrito como requisito, e não só como exemplo? [Clarity, Spec §FR-2811]
- [ ] CHK004 - "Desde quando" está definido para cada natureza, incluindo as que não têm instante? [Clarity, Spec §FR-2809, §Assumptions]

## Ambiguidade e conflito

- [ ] CHK005 - O limite de D-004 (pendência descoberta só na conferência) está compatível com a FR-2803, ou precisa de redação de exceção explícita? [Conflict, Spec §FR-2803, §D-004]
- [ ] CHK006 - "Conferir e submeter" fere a FR-2814 ("não afirmar ausência") ou a FR-2815 só troca o destino? [Ambiguity, Spec §FR-2815]
- [ ] CHK007 - A ordem dos itens está definida de forma que não pareça urgência? [Clarity, Spec §Clarifications]

## Cobertura de papéis

- [ ] CHK008 - Há requisito ou cenário para elaborador, homologador, publicador, gestor, julgador, membro de comissão e quem acumula papéis? [Coverage, Spec §User Stories]
- [ ] CHK009 - O que o gestor vê na faixa (quase nada) está declarado como resultado esperado, e não como lacuna? [Coverage, Spec §FR-2808]
- [ ] CHK010 - A presidência de comissão, que conduz marcos, tem a ausência na faixa declarada? [Coverage, Spec §D-002]

## Autorização e segregação

- [ ] CHK011 - Está escrito que a faixa não amplia o que cada pessoa já alcança pelas telas de detalhe? [Completeness, Spec §FR-2801, §FR-2805]
- [ ] CHK012 - A segregação do Edital na Lista tem a mesma regra do detalhe, por requisito? [Consistency, Spec §FR-2816]
- [ ] CHK013 - O escopo institucional está exigido para a faixa, a coluna e as contagens? [Completeness, Spec §FR-2805, §FR-2818]

## Acessibilidade e celular

- [ ] CHK014 - Teclado, ordem de leitura, independência de cor e largura de 375 px estão exigidos para a faixa e para o "Mostrar as outras N"? [Coverage, Spec §FR-2810, §FR-2813]
- [ ] CHK015 - Está exigido que a faixa não dependa da tabela, que rola para o lado no celular? [Completeness, Spec §FR-2813]

## Estados vazios

- [ ] CHK016 - A frase sem ação está definida para não negar trabalho institucional? [Clarity, Spec §FR-2808]
- [ ] CHK017 - O estado vazio de Minhas Etapas tem conteúdo e destino definidos? [Completeness, Spec §FR-2827]

## Escala

- [ ] CHK018 - Os números de Editais da medição (0, 3, 30, 300) e a exceção de quem exporta matrícula estão nos critérios? [Measurability, Spec §SC-984, §SC-985]
- [ ] CHK019 - O custo da avaliação, que cresce com as alocações da pessoa, está declarado como exceção aceita? [Assumption, Spec §FR-2806]

## Continuidade operacional

- [ ] CHK020 - O sumiço do item depois do ato está exigido para todas as pessoas com o mesmo papel? [Completeness, Spec §US1]
- [ ] CHK021 - A devolvida, a reenviada e o rascunho novo têm rótulos definidos em todas as telas? [Consistency, Spec §FR-2821, §FR-2822, §SC-987]
- [ ] CHK022 - A confirmação de homologar tem o objeto da decisão especificado sem prometer diff que o modelo não sustenta? [Clarity, Spec §FR-2824]

## Rastreabilidade

- [ ] CHK023 - Cada critério SC tem pelo menos um FR que o sustenta, e cada cenário A a I do pedido tem teste previsto? [Traceability, Spec §Success Criteria]
- [ ] CHK024 - A cobertura funcional (o que entra e o que fica fora da faixa) está num único lugar e citada pela tela? [Traceability, Spec §FR-2812, research §Inventário]

## Notes

- `$speckit-implement` lê o estado deste arquivo, e não altera as marcas.
