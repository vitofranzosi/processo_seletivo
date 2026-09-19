# Specification Quality Checklist: Painel de condução do Processo vivo

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
- [x] Success criteria are technology-agnostic
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## O teto proporcional, conferido

| | Alvo | Real |
|---|---|---|
| Linhas de spec | ~400 | **249** |
| Histórias | ≤ 3 | **3** |
| Requisitos | ~15 | **12** |
| Passadas de `analyze` previstas | **1** | — |

**Nenhum requisito existe para impedir a leitura errada de outro.** Os avisos dessa espécie — *ler a
mensagem do `UX-005` em vez da condição*, *não fazer dois sinais dispararem pelo mesmo fato* — estão
em **casos de borda** e em **itálico dentro do requisito que já existia**, não como requisito próprio.

## O que a medição corrigiu antes de a spec ser escrita

| Afirmação de partida | O que a medição achou |
|---|---|
| "o `UX-005` cobre recursos pendentes" | cobre **comissão inteira impedida**; a mensagem engana, a condição não |
| "o `UX-003` cobre avaliação em aberto" | cobre **cobertura**; Etapa bem coberta com trabalho parado não sinaliza |
| "a lista de sinais é fechada" | é fechada por requisito que diz **cinco**, e o produto tem **seis** |
| "o painel mostra quem precisa agir" | **não é entregável** — o produto não liga identidade a papel, e o `UX-005` já registra isso |

## A passada única do `analyze`, e o que ela achou

| Achado | O que estava errado |
|---|---|
| **C1** | a feature acrescentava quatro espécies a um catálogo **indexado por identificador** e não definia identificador nenhum — a `T017` não teria o que nomear, e a emenda ficaria ao gosto de quem implementa |
| **H1** | a espécie do **recorte** acrescenta consulta, e três artefatos diziam que não |
| **H2** | a `SC-198` exigia **quatro** espécies, e a `T014` autoriza entregar **três** |
| **H3** | a spec ainda chamava a `US1` de **MVP** depois de o `tasks` inverter a ordem |

### Uma correção ao próprio relatório do `analyze`

O `C1` afirmou que, se alguém inventasse `UX-063` a `UX-066`, o teste de citações reprovaria.
**Está errado, e a medição do remédio é que mostrou.**

`tests/test_citacoes_de_requisito.py` define `DEFINICAO = re.compile(r"\*\*(…)\*\*")`: **qualquer
ocorrência em negrito numa spec conta como definição**. Foi assim que o `UX-062` da `037` passou —
ele aparece só no blockquote da faixa, em negrito, e nunca foi definido como espécie.

**O defeito do `C1` era real e continua corrigido** — as quatro espécies agora têm identificador com
condição escrita. O que não era real é a rede: **a guarda não teria pegado.**

### Achado registrado, e fora do escopo desta feature

**A guarda de citações aceita como definição qualquer identificador em negrito.** Um blockquote que
reserva faixa "define" o identificador; uma citação enfática também. A guarda protege contra
identificador **inventado**, não contra identificador **anunciado e não especificado**.

Isso é governança e é achado desta passada, **não escopo da `038`** — segue para quem decide o
backlog.

## Notas

- As quatro medições acima **devem ser reconferidas pelo Phase 0**. Eu errei duas delas em cinco
  minutos lendo mensagem em vez de condição.
- A `037` está em CI e altera três superfícies que esta spec **deliberadamente não mediu**. A
  dependência está registrada no fim da spec.
