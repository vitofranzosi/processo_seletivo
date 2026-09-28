# Specification Quality Checklist: Condução confiável do Processo vivo

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-26
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

## Notes

- **Referências a código ficam na evidência, e não nos requisitos.** As seções *"Por que esta feature
  existe"*, *"O que a verificação contra o código acrescentou"* e os achados registrados em *Out of
  Scope* citam arquivos e funções, como as specs anteriores deste repositório fazem: é a prova de que
  a proposta foi conferida contra a `main`. Os `FR-` e `SC-` falam de comportamento — a fase, a frase,
  a medida, a população —, e os nomes que usam (*régua do vencido*, *fonte única de participação*,
  *mecanismo único da `037`*) são conceitos que outras specs já definiram.
- **"Para leitores não técnicos" vale com o vocabulário do domínio.** A spec é lida por quem conduz
  certames do Cefor; *admissibilidade*, *Retificação* e *Etapa* são termos do Edital, não da
  implementação.
- **Nenhum marcador de clarificação.** As três perguntas que poderiam sê-lo já tinham resposta: as
  `DP-01` a `DP-03` foram decididas pelo usuário na proposta de 26/09, e a regra do Evento sem término
  já está escrita na `037` (`FR-545`, `FR-546`) e na régua do período (`FR-347`).
- **Varredura de contradições, feita à mão** (o checklist não as detecta). Um par foi encontrado e
  corrigido: a primeira redação da `FR-741` proibia em geral o sinal sem ato possível, enquanto o
  caso-limite mandava apenas registrar o `UX-004` num Edital encerrado. A `FR-741` passou a valer só
  para o destino Retificação, que é o que a `D-003` decide. Cruzados também: `FR-742` × `022` `FR-033`
  (o denominador não perde o participante sem avaliador — refinamento, não contradição); `FR-735` × a
  régua do período (a exceção está no requisito); `FR-730` × `038` `FR-559` (a linha de ausência
  continua única, com duas formas).
- **Casos-limite são requisitos.** A matriz de rastreabilidade da implementação ganha uma linha por
  caso-limite, além das de `FR-`, `SC-` e `UX-`, e as nove linhas da tabela *"Os testes de regressão
  da proposta"*.
- `tests/test_citacoes_de_requisito.py` e `tests/test_sem_dado_pessoal_da_amostra.py` passam com a
  spec e com o registro das decisões em `doc/` (736 casos, 26/09/2026).
- **O `/speckit-analyze` de 26/09 achou mais três contradições**, todas corrigidas: a `FR-735` e a
  `FR-736` afirmavam, para toda superfície, o que o portal — fora do escopo — contradiz; passaram a
  valer para a gestão, com o portal registrado. E a condução prevista para o Julgador impedido na peça
  do recurso contrariava a `037` (`FR-544`): ele tem a permissão, e *"peça a alguém com a permissão de
  julgar"* seria falso; a peça já conduz, e saiu da `T029`.
