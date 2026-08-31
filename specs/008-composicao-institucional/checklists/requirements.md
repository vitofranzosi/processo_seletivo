# Specification Quality Checklist: Composição Institucional do Edital

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-30
**Revalidated**: 2026-08-31, após a análise de consistência, a remoção da divergência
constitucional e a calibração editorial contra três Editais de referência
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

**Situação: 16/16.** A divergência que a `007` carregou e que as duas primeiras redações desta spec
repetiram **foi eliminada**, não justificada.

## O que mudou, e por que a justificativa anterior não bastava

As redações anteriores deixavam quatro itens desmarcados e argumentavam que a divergência era
deliberada, com precedente na `007`. O argumento estava errado em um ponto decisivo: a Constituição
usa **DEVEM** — *"Especificações DEVEM concentrar-se no que e por quê. Linguagem, framework, banco,
infraestrutura e bibliotecas DEVEM ser decididos no plano técnico, salvo restrição institucional
permanente"* —, e nada nesta feature é restrição institucional permanente. **Precedente de outra
feature não cria exceção**, e uma justificativa registra uma inconformidade sem removê-la.

O que saiu da spec e para onde foi:

| Saiu da `spec.md` | Foi para |
|---|---|
| A descrição do compositor — operadores de texto, contagem de caracteres, lista plana de linhas | `research.md`, seção "O ponto de partida" |
| `pdf.py`, `_quebrar`, `Composicao`, `_secoes`, `edital_snapshot`, `SCHEMA_VERSION`, `signatory_name`, XObject, cp1252, Helvetica | `research.md` e `plan.md` |
| FR-005 — "não substituir o mecanismo de geração, não introduzir dependência" | `plan.md`, R-T1 |
| A seção "Instruções para o `/plan`" inteira | `plan.md`, R-T2 a R-T7 |
| A mecânica da evidência de bytes — nome de script, nome de arquivo | `plan.md` e `quickstart.md` |

O que **permaneceu** e por quê: FR-002, FR-003 e FR-004 foram reescritos em linguagem de resultado
observável e limite funcional — "texto centralizado fica centralizado", "o vocabulário visual é
texto, fio e contorno", "a quebra respeita as fronteiras do conteúdo". São afirmações que um leitor
não técnico confere olhando o documento, e limites que delimitam escopo. Não dizem **como**.

**Consequência de numeração**: com a saída de FR-005, os requisitos foram renumerados e agora vão de
FR-001 a FR-044, contínuos, em todos os artefatos.

## Notas de validação

**Sobre a mensurabilidade dos critérios.** Três formulações subjetivas foram substituídas por
afirmações observáveis — ordem e forma tipográfica do cabeçalho (SC-001), comparação ordinal de três
espaços verticais (SC-008), igualdade do conjunto de quebras do corpo normativo entre prévia e
publicado (FR-042). A `### Rubrica de inspeção` dá catorze itens de resposta sim/não, e a
`## Matriz de rastreabilidade SC → verificação` de `tasks.md` mapeia os quinze SC — inclusive
SC-012, SC-013 e SC-015, que não são visuais e não poderiam ser cobertos pela rubrica.

**Sobre as referências visuais.** Resolvidas. `referencias/` traz o estado inicial
(`estado-inicial-apos-007.pdf`) e os dois alvos (`alvo-edital-62-2026.pdf`,
`alvo-edital-73-2026.pdf`). A leitura dos alvos corrigiu FR-006 — o ato é destacado por peso, caixa
alta e centralização, não por corpo grande — e nomeou três diferenças que a V1 aceita e declara:
identidade visual gráfica, numeração de item dentro da seção e corpo justificado.

**Sobre os dois defeitos de contrato.** FR-021 virou cascata de alternativas que termina sempre em
uma exequível. FR-035 fixa a presença da autoridade pelo modo: obrigatória no publicado com recusa,
proibida na prévia.

**Sobre a cobertura.** 44 FR e 15 SC contra 74 tarefas. Os requisitos que só se verificam por
ausência — FR-001, FR-008, FR-037 — são conferidos nominalmente em T073.

**Sobre a calibração editorial e a rastreabilidade.** Quatro auditorias sobre o documento gerado
produziram sete commits que o `tasks.md` não descrevia: a spec era atualizada a cada rodada e as
tarefas não. A segunda análise de consistência apanhou isso, e a fase 9 fecha a lacuna com as vinte
e uma tarefas efetivamente executadas, as decisões D-012 a D-019 e os itens R-15 a R-18 da rubrica.
**A lição não é que faltou disciplina no fim, e sim que trabalho vindo de revisão precisa voltar
para o plano na mesma passada** — senão o artefato afirma que tudo foi feito enquanto descreve menos
do que existe, que é a forma mais enganosa de a rastreabilidade quebrar.

**Trava de escopo declarada.** Depois desta feature a autoria fica congelada salvo bug bloqueante, e
a próxima spec muda de ator: inscrição do candidato e documentos.
