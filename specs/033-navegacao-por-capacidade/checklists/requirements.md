# Specification Quality Checklist: Navegação por capacidade

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

**Nenhum marcador de clarificação, e a ausência é achado.** Ao contrário da `032`, aqui não havia
decisão de governança a tomar: a doutrina certa **já está implementada no repositório**, na camada de
segurança, para capacidade e escopo. A feature completa o eixo que ficou de fora. Onde não há escolha
aberta, não se fabrica pergunta.

**O Phase 0 foi refeito por medição, na terceira passada — e foi a medição que faltava desde o
início.** As duas primeiras versões descreviam a superfície lendo definições de função; uma varredura
por AST levou dois minutos e desmentiu as duas.

| O que as versões anteriores diziam | O que a medição mostra |
|---|---|
| "a superfície são quatro portas" | os 75 `raise Http404` vivem em **59 funções**; **53** recebem `request`; **32** consultam ator, escopo ou vínculo |
| "quatro portas nomeadas" | são **seis** helpers autorizativos, e `_ato_para_publicar` — que eu listava — **não autoriza ninguém** |
| "a porta do marco é a do `ACH-35`" | a tela de distribuição passa por **`_etapa_para_distribuir`**, que nenhuma versão anterior mencionava |
| "uma porta discorda da outra" | **quatro** portas erram, e todas **no mesmo eixo**: negativa por vínculo vira "não encontrado" |
| "a gramática certa está num docstring" | está **implementada** em `seguranca/application/authorization.py::require_permission`, e usada por duas portas |

**Isso mudou a espinha da spec, para melhor.** A feature deixa de ser "aplicar a doutrina de uma
porta às outras" e passa a ser: **o produto trata dois dos três eixos e não tem tratamento para o
terceiro**. Não há gramática a inventar — há um ponto único de recusa por vínculo a criar, ao lado do
que já existe para capacidade.

**E a medição corrigiu uma regra que eu mesmo havia escrito no contrato.** Ele mandava avaliar escopo
**antes** de capacidade e vínculo. A porta da divulgação faz o oposto — 403 antes de tocar no banco —
e **não vaza**. O que protege é o **filtro por escopo na consulta**, uniforme nas seis portas.
`FR-487` passou a fixar a invariante certa, e `FR-488` a tratar da porta que decide escopo e vínculo
no mesmo `if` — que não admite troca de status sem separação prévia.

**Uma tarefa nasceu dessa descoberta e tem ordem obrigatória:** T027 cria o ponto único, T028 separa
as condições na porta travada, T029 faz as quatro portas consumirem o ponto. Inverter T028 e T029
responde recusa explicada para Edital de outra unidade.

**`FR-486` ganhou asserção própria** (T039). Verificar a taxonomia da recusa e verificar a
**formulação** são coisas diferentes; a varredura da taxonomia cobre `SC-165`, `SC-166` e `FR-481`, e
não fecha a `FR-486`.

**A garantia mais importante é `SC-168`**, e ela existe porque a feature toca superfície de
segurança: o conjunto de pares (ator, tela) que abre tem de ser **idêntico** antes e depois. Sem ela,
"melhorar a navegação" é indistinguível de "afrouxar autorização". `FR-482` e `FR-483` são as duas
metades da mesma promessa — a verificação continua no servidor, e retirar um link nunca substitui a
recusa.

**Uma tensão declarada, e não escondida:** trocar 404 por recusa explicada **revela** que o objeto
existe. Isso é aceitável precisamente porque `FR-480` mantém o "não encontrado" para outro escopo
institucional — quem recebe a recusa explicada já está dentro do escopo, e já sabe que o Edital
existe por outras telas. Se na implementação aparecer um caso em que a existência não deveria ser
revelada nem dentro do escopo, ele é achado para registrar, não para resolver em silêncio.

**Faixa de identificadores medida em todas as worktrees, em 18/09/2026:** teto `FR-472 / SC-163 /
UX-061`, ocupado pela `032`. Esta spec abre em **FR-473** e **SC-164**, e não define `UX-`.

**Tudo conferido contra o código, e desta vez por varredura.** As seis portas foram lidas uma a uma;
`require_permission`, `RecusaDoDominioMiddleware`, `interface/recusa.html` e `_pode_auditar_a_etapa`
também. É por `_pode_auditar_a_etapa` existir que a `FR-473` tem precedente no próprio produto: ela é
o predicado extraído da porta para que a tela possa consultá-lo **antes** de oferecer o caminho —
exatamente o que falta na tela do Edital.

**O que ainda não foi medido, e é tarefa:** as **26** funções autorizativas fora dos seis helpers.
Três tentativas de estimar a repartição já erraram; o inventário conta, e T004 decide o que fazer com
o que ele encontrar.
