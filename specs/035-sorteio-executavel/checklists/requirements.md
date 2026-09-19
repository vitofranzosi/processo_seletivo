# Specification Quality Checklist: Sorteio executável

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-18
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

**Revisto em 18/09/2026, depois de o Phase 0 contradizer a spec e de uma passada de `analyze`.** A
primeira redação destas notas descrevia a spec do dia em que ela nasceu, e a medição a deixou para
trás — ela ainda listava como "a reconferir" a premissa dos **três campos sem guarda**, que o `R-2`
já tinha refutado.

### O que a medição mudou na spec, e que estas notas precisam registrar

| A spec dizia | A medição encontrou |
|---|---|
| três campos do método sem guarda | **um** — a ocorrência; os outros cinco já são conferidos ao gravar |
| "nada valida na composição" | **seis** validadores, para o método próprio **e** o comum do Edital |
| a Retificação já oferece a escolha "com o algoritmo" | com **quatro** campos, por uma função única |
| a varredura conta quantos Editais reais seriam impedidos | **nenhum** dos quatro lidos declara ocorrência externa |

### As duas cessões de "sem detalhe de implementação"

1. **A seção *Por que esta feature existe* cita módulos e campos por nome.** É a **medição do
   estado**, não o desenho da solução, e está ali porque a `033` produziu três medições erradas
   seguidas por descrever a superfície de memória, e a `034` carregou por três revisões um número que
   nunca fechou com a própria tabela. **Nesta feature ela se pagou**: foi por medir que a spec foi
   corrigida antes de o Phase 1 começar.
2. **A `FR-515` é requisito sobre o código**: a conferência da composição e a derivação do motor têm
   de responder pela **mesma** regra. A razão é observável por quem usa — a composição aceitando o
   que o sorteio recusa, com o Edital já publicado —, e o `SC-177` a verifica comparando **as duas
   respostas**, sem ler as duas implementações.

### As três decisões tomadas, em vez de adiadas

| | Onde |
|---|---|
| Método inexecutável **impede** — perguntado a quem governa o backlog | `D-001` |
| Vocabulário fechado vira **escolha** na composição, como já é na Retificação | `D-002` |
| A derivação em prosa **fica como está** — contraria a leitura da auditoria, e a medição sustenta | `D-003` |

O `D-001` sobreviveu à revisão sem mudar: **a decisão é impedir**, e o que mudou foi só **onde a
guarda vive** — de uma família nova de achados na publicação para a sexta guarda ao lado das cinco.
Onde ela mora é engenharia; que ela impeça é governança.

### A correção que esta spec faz na auditoria, e que precisa sobreviver à revisão

A reauditoria citou **dois** campos como *"texto livre que precisa ser dado computável"*. Só **um**
é. O outro — *como a ocorrência decorre da data programada* — é prosa por desenho: a varredura do
repositório inteiro achou **44 ocorrências** dele e **zero** caminhos de execução que o leiam.

Se alguém, na implementação, "corrigir" esse campo, a feature terá removido do Edital a frase que diz
a norma em português. A `FR-510` existe para impedir isso, e tem tarefa própria de **conferência** —
`T011` —, porque é o requisito mais fácil de perder de vista: ele manda **não fazer** o que a
auditoria parecia pedir.

### A pergunta de governança que fica registrada e sem resposta

Os Editais correntes do Cefor **não declaram ocorrência de fonte externa**: os quatro lidos publicam
a semente depois, para auditoria. O modelo deste sistema é deliberadamente mais forte, e é o que
entrega a verificação pública que aqueles Editais prometem e não cumprem. A diferença é real, e é de
quem governa o backlog — esta feature ensina a declarar o que o modelo pede, e não muda o modelo.

### Medições a reconferir na implementação

A tabela de *Por que esta feature existe* inteira, e em especial: que **só a ocorrência** está sem
guarda; que a regra de substituição exige referência terminada em número; que **nenhum** caminho de
execução lê a derivação em prosa — esta é a que sustenta a `FR-510` e a que mais custa se estiver
errada; e **quantos Editais do acervo têm ocorrência fora da forma**, que é o portão da `T004` e o
que decide onde a guarda vive.
