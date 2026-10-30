# Checklist da jornada: Jornada operacional da Retificação

**Purpose**: Avaliar a qualidade dos requisitos de cobertura das jornadas, exceções, acessibilidade e
não regressão das garantias do servidor, antes e durante a revisão do PR.
**Created**: 2026-10-30
**Feature**: [spec.md](../spec.md)

> **Dono**: quem revisa. `[x]` significa que quem revisa julgou o critério de qualidade do requisito
> satisfeito, e não que a implementação está pronta. Gerado sem marcas; profundidade padrão.

## Requirement Completeness

- [ ] CHK001 - As nove ações da jornada (iniciar, localizar, elaborar, retomar, submeter, homologar, devolver, corrigir, publicar) têm, cada uma, um requisito que diga por qual tela ela é alcançada? [Completeness, Spec §FR-2701–FR-2729]
- [ ] CHK002 - O cancelamento tem requisito de onde é oferecido e a quem, ou fica implícito nos atos já existentes? [Gap, Spec §US5]
- [ ] CHK003 - Está especificado o que a Lista mostra a quem não tem nenhuma permissão de Retificação? [Completeness, Spec §FR-2706]
- [ ] CHK004 - A tela de Retificar diz o que acontece com a quem não pode elaborar quando há Retificação em curso (lista sem "Continuar")? [Completeness, Spec §FR-2709]

## Requirement Clarity

- [ ] CHK005 - "Quem age a seguir" está definido para todas as cinco situações, inclusive as finais? [Clarity, Spec §FR-2711]
- [ ] CHK006 - "O ato seguinte" que a marca nomeia está definido sem ambiguidade quando a situação admite dois atos (homologar e devolver)? [Ambiguity, Spec §FR-2706]
- [ ] CHK007 - "Volta ao valor vigente" na fusão está definido com a mesma comparação que a criação usa para "nada mudou"? [Clarity, Spec §FR-2718]

## Requirement Consistency

- [ ] CHK008 - A segregação antecipada (FR-2725) e a recusa do servidor usam a mesma definição de "quem elaborou" (quem submeteu)? [Consistency, Spec §FR-2731]
- [ ] CHK009 - O texto da devolução ("pode ser editada novamente") é coerente com a edição só em elaboração? [Consistency, Spec §FR-2721, §FR-2729]
- [ ] CHK010 - A seção do Edital e a marca da Lista dizem a mesma coisa para a mesma Retificação e o mesmo ator? [Consistency, Spec §FR-2702, §FR-2706, §FR-2730]

## Acceptance Criteria Quality

- [ ] CHK011 - SC-971 define o ponto de partida ("só as seções da barra") e o limite de cliques de modo verificável? [Measurability, Spec §SC-971]
- [ ] CHK012 - SC-974 fixa as cardinalidades comparadas (1 e 5 Retificações; 1 e 3 Editais)? [Measurability, Spec §SC-974]
- [ ] CHK013 - SC-978 tem roteiro e critério de sucesso suficientes para ser conduzida por outra pessoa? [Acceptance Criteria, Spec §SC-978]

## Scenario Coverage

- [ ] CHK014 - A devolução a partir de homologada tem cenário próprio, além da partir de revisão? [Coverage, Spec §FR-2729]
- [ ] CHK015 - O ciclo com duas devoluções seguidas está coberto por critério? [Coverage, Spec §SC-975]
- [ ] CHK016 - O ator com vários papéis tem cenário para cada ponto em que a segregação aparece? [Coverage, Spec §US3]
- [ ] CHK017 - A sessão interrompida e retomada por outra pessoa do mesmo escopo tem cenário? [Coverage, Spec §US2]

## Edge Case Coverage

- [ ] CHK018 - Está definido o que a edição faz com um acréscimo do rascunho que a pessoa remove? [Edge Case, Spec §Edge Cases]
- [ ] CHK019 - Está definido o que acontece se a versão vigente mudou depois da base do rascunho? [Edge Case, Spec §Edge Cases]
- [ ] CHK020 - Está definido o caso de Edital encerrado com Retificação em curso? [Edge Case, Spec §Edge Cases]

## Non-Functional Requirements

- [ ] CHK021 - Os requisitos de acessibilidade cobrem teclado, leitor de tela e largura de 375 px para cada tela nova ou alterada? [Coverage, Spec §FR-2708]
- [ ] CHK022 - O custo de consultas está especificado para as três telas que listam (Lista, Edital, Retificar)? [Completeness, Spec §FR-2705, §FR-2707]
- [ ] CHK023 - A auditoria da edição está especificada com os mesmos campos dos outros atos (ator, permissão, estados, revisões)? [Completeness, Spec §FR-2723]

## Não regressão das garantias do servidor

- [ ] CHK024 - Os requisitos preservam explicitamente 403, 404 e 409 e a conferência de revisão? [Completeness, Spec §FR-2731]
- [ ] CHK025 - Está escrito que nenhuma permissão, situação ou transição nova é criada? [Clarity, Spec §FR-2731]
- [ ] CHK026 - Está escrito que a listagem não amplia o público que já lê o detalhe? [Assumption, Spec §Assumptions]

## Notes

- `$speckit-implement` lê o estado deste arquivo, e não altera as marcas.
