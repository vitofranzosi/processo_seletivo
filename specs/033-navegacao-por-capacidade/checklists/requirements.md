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
decisão de governança a tomar: a doutrina certa **já está escrita no repositório**, por extenso, na
porta da divulgação — *"sem a capacidade é 403, e não 404 … o 404 fica para o que o ator não
alcança"*. A feature aplica o que o produto decidiu e não cumpriu. Onde não há escolha aberta, não se
fabrica pergunta.

**O escopo foi estimado duas vezes, e errado nas duas.** A primeira redação dizia *"a superfície real
são as quatro portas nomeadas"*, medindo só as **definições de função**. A segunda trocou por
*"apenas 4 dos 75 vivem dentro das portas"* — e também estava errada: a varredura por faixa de linhas
cobriu três intervalos e deixou `_ato_para_publicar` de fora, e essa função **não autoriza ninguém**
(recebe `edital`, `marco_id` e `ato_id`, sem `request` e sem ator). São **5** ocorrências em 4
funções, ou **4** em 3 portas propriamente autorizativas.

A terceira redação não estima: afirma os **75** do arquivo e manda o inventário contar o resto. É a
diferença entre um escopo medido e um escopo adivinhado, e foram necessárias duas revisões para
chegar lá.

**A parada de escopo virou tarefa própria** (T004), logo depois do inventário e **antes da fase 2** —
não às vésperas de uma tarefa específica. A implementação começa em T013, e um gatilho posicionado em
T028 chegaria tarde demais.

A porta que erra a gramática governa **23 telas**, e é isso que torna `SC-165` verificável hoje.

**A varredura precisou de um mecanismo diferente do que eu propus.** A primeira versão mandava
espelhar `tests/test_vocabulario_da_composicao.py`, da `030` — e aquele teste usa **lista literal**,
dizendo no próprio comentário por quê: *"uma lista calculada passaria a ignorar a tela que deixasse
de usar o termo"*. Para o problema dele isso está certo; para este é inútil, porque o que precisa ser
detectado é a porta que **aparece depois**, e lista literal nunca a vê. T036 passou a ser um
**detector de novidade ancorado no inventário**: falha quando aparece um "não encontrado" que ninguém
registrou. O custo — toda negativa nova exige uma linha no inventário — é o ponto, não o efeito
colateral.

**E `FR-486` ganhou asserção própria** (T037). Verificar a taxonomia da recusa e verificar a
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

**Citações externas conferidas contra o código, não assumidas:** `_edital_para_publicar` e
`_edital_para_classificar` foram lidas nesta sessão, e é a contradição entre os dois docstrings que
dá à feature a sua espinha. `RecusaDoDominioMiddleware` e `interface/recusa.html` também — é por
existirem que `FR-478` não precisa construir mecanismo nenhum.
