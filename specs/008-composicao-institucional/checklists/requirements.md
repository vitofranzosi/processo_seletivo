# Specification Quality Checklist: Composição Institucional do Edital

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-30
**Revalidated**: 2026-08-30, após revisão externa da primeira redação
**Feature**: [spec.md](../spec.md)

## Content Quality

- [ ] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [ ] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [ ] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [ ] No implementation details leak into specification

**Situação: 12/16.** Os quatro itens abertos são o mesmo item visto de quatro ângulos, e repetem a
divergência **deliberada e declarada** que a `007` registrou — agora reduzida, ver abaixo.

**Pré-condição operacional atendida.** O contexto da feature está fixado em `.specify/feature.json`
(`specs/008-composicao-institucional`), e `check-prerequisites.sh --paths-only` resolve
`FEATURE_DIR`, `FEATURE_SPEC` e `IMPL_PLAN` corretamente. O arquivo é ignorado pelo versionamento,
como o próprio `.specify/.gitignore` determina, e por isso **não** viaja no commit: outra sessão que
retome esta feature precisa refazê-lo ou exportar `SPECIFY_FEATURE_DIRECTORY`. Sem isso o `/plan`
falha com `ERROR: Feature directory not found`, porque a resolução não tem fallback por nome de
branch — e o branch desta árvore não é `008-composicao-institucional`.

## A divergência deliberada, e por que ela é maior nesta feature

Quatro itens do template exigem uma spec livre de detalhe técnico e legível por stakeholder não
técnico. Esta spec não é isso — e, diferentemente das anteriores, **não poderia ser**.

Esta é uma feature de materialização. Seu objeto é o compositor. Uma spec que dissesse apenas "o
documento deve parecer um Edital" teria produzido exatamente o que a primeira redação produziu: sete
requisitos que descreviam comportamento já implementado, um requisito de assinatura que quebrava o
contrato de autossuficiência do snapshot sem que ninguém percebesse antes do código, e três
requisitos visuais cuja pré-condição técnica não existia e não era mencionada — centralizar,
tabular e alinhar texto num compositor que mede largura contando caracteres.

**O que ela contém que o template desaprova:** nomes de arquivo e de função do compositor, a
fixture de bytes, a nomeação do contexto do ato como entrada separada do snapshot, e instruções
dirigidas ao `/plan`.

**O que foi corrigido nesta revalidação.** A primeira redação escrevia FR-002, FR-003 e FR-004 como
autorizações de mecanismo — "função interna de cálculo de largura", "a `Composicao` pode ser
estendida", "o paginador pode reconhecer blocos". Isso era desenho na spec, e a Constituição manda
deixá-lo para o plano. Os três passaram a declarar **resultado e limite** — texto posicionado por
largura real; vocabulário visual restrito a texto, fio e contorno; quebra decidida sobre blocos —, e
o bloco abre exigindo que o `/plan` registre no `research.md` como cada limite é cumprido, com a
alternativa considerada. A evidência que motivou cada limite permanece, em itálico, porque é o que
torna o requisito contestável com o código na mão.

**Por que o resíduo permanece.** A Constituição exige rastreabilidade entre especificação, plano,
tarefas, implementação e testes, e proíbe que comportamento acidental vire regra sem decisão
documentada. Numa feature visual, a âncora técnica é o que separa um requisito verificável de uma
opinião estética: "o Perfil não deve quebrar mal" é opinião; "a paginação percorre hoje uma lista
plana de linhas, logo a regra de não partir o Perfil é inexprimível sem que a quebra passe a
enxergar blocos — e essa capacidade está limitada nominalmente a cinco regras" é um requisito que se
pode contestar com o código na mão. **A justificativa não elimina a inconformidade; ela a
registra**, que é o que a Governance exige de uma divergência assumida.

**O que isso custa e como é mitigado.** Custa legibilidade para quem não conhece o repositório. A
mitigação é estrutural, como na `007`: as âncoras vivem em blocos de racional *em itálico*, e o
requisito normativo é sempre a frase antes delas. Lendo só as frases normativas e ignorando os
itálicos, obtém-se uma spec de produto.

**O que continua proibido, e é o que o item realmente protege.** A spec não escolhe biblioteca (e
FR-005 proíbe trocar a atual), não desenha classe, não define assinatura de função — FR-035 exige que a
autoridade chegue como *contexto do ato, separado do conteúdo normativo*, e FR-036 fixa sua presença
pelo modo — nenhum dos dois desenha função —, não escolhe
estratégia de persistência e não prescreve estrutura de arquivos. As "Instruções para o `/plan`"
declaram limites, não desenho.

**Decisão registrada:** os quatro itens permanecem marcados como não atendidos, com esta
justificativa, em vez de marcados como atendidos com uma nota explicando por que não seriam. O
`/plan` prossegue.

## Notas de validação

**Sobre a ausência de `[NEEDS CLARIFICATION]`.** As seis decisões que estavam abertas foram fechadas
antes desta redação e estão registradas em `## Reconciliação com o compositor real`: origem da
autoridade signatária; ausência de assinatura na prévia; ausência de praça, data e cadastro de
pessoas; brasão fora da V1; autorização nominal da métrica de fonte e das primitivas gráficas;
evolução limitada da paginação. Nenhuma delas foi deixada para o `/plan`, porque cada uma seria uma
decisão arquitetural escondida.

**Sobre os requisitos que a primeira redação continha e esta não.** Sete requisitos descreviam
comportamento já implementado e testado: ausência de UUID no corpo, rodapé com identificação e
paginação, SHA-256 abreviado no rodapé, compositor compartilhado entre prévia e publicado, marca de
prévia, parágrafos preservados pela `006.1` e omissão de percentual inexistente. Eles migraram para
`## Invariantes de não regressão`. Reespecificá-los teria feito o `/plan` planejar código pronto e
teria inflado a contagem de requisitos sem inflar a entrega.

**Sobre a mensurabilidade dos critérios.** Três formulações da primeira redação eram subjetivas:
"reconhecível ao lado de um Edital oficial" (SC-001), espaços "distinguíveis" (SC-008) e paginação
não alterada "significativamente" (FR-043). As três foram substituídas por afirmações observáveis —
ordem e corpo tipográfico relativo; comparação ordinal de três espaços verticais; igualdade do
conjunto de quebras do corpo normativo entre prévia e publicado. Foi acrescentada a
`### Rubrica de inspeção`, com catorze itens de resposta sim/não distribuídos pelas cinco entregas,
para que a demonstração visual seja repetível por quem não escreveu a spec. Só com isso o item
"Success criteria are measurable" permanece marcado.

**Sobre as referências visuais.** O **estado inicial já está versionado** em
`referencias/estado-inicial-apos-007.pdf` — o documento que o sistema produz hoje —, e o cenário-base
do `quickstart.md` foi reescrito para descrever esse arquivo, e não o `documento2.pdf`, que não está
no repositório. **Continua pendente o alvo**: ao menos um Edital oficial do Cefor. A seção
`### Referências visuais` o exige versionado antes da entrega 1, que ele bloqueia, ou identificado
por fonte, número, ano, página e características observáveis. É o único item pendente de ação
externa, e não bloqueia o `$speckit-tasks`.

**Sobre o antigo SC-015.** Era um roteiro de conferência visual, não um critério mensurável. Virou a
seção `## Demonstração visual obrigatória`, que declara explicitamente o que é verificado por
inspeção e o que é verificado por teste automatizado — e por que teste pixel-perfect está fora.

**Sobre os dois defeitos de contrato encontrados na revisão.** O primeiro era inexequível: FR-022
exigia que um Perfil grande quebrasse apenas entre sub-blocos e que nenhum sub-bloco fosse partido,
o que nenhum compositor cumpre quando um campo de texto livre é maior que uma página. Virou cascata
de três alternativas, terminando sempre em uma que existe. O segundo era contraditório: FR-034
exigia autoridade em todo publicado, FR-035 chamava o contexto de opcional e SC-013 afirmava
determinismo "sem autoridade" — a leitura conjunta admitia emitir ato administrativo sem quem o
praticou. FR-036 passa a fixar a regra pelo modo: obrigatória no publicado, com recusa; proibida na
prévia. FR-045 e SC-015 acrescentam a consequência operacional — o gerador da fixture e os testes do
modo publicado passam autoridade fixa versionada ao lado do snapshot de referência.

**Sobre a contradição prévia × assinatura.** A primeira redação afirmava simultaneamente que a única
diferença entre prévia e publicado seria a marca de prévia e que o documento exibiria a autoridade
signatária registrada na Publicação — que a prévia não tem. FR-042 resolve nomeando as duas
diferenças admitidas, e FR-036 declara a consequência.

**Sobre a nomenclatura das entregas.** A spec usa US1–US5 e Entregas 1–5; `S0`–`S4` era
nomenclatura da proposta original e não aparece em nenhum ponto do texto vigente. O gate está
escrito na forma correta: "A entrega 1 precisa mudar visivelmente a primeira página."

**Sobre a Constituição.** O princípio VI exige cenário demonstrável de ponta a ponta pelo canal do
ator. Ele é atendido: cada entrega termina com o documento gerado pela interface administrativa —
prévia para as entregas 1 a 4, publicação para a entrega 5 — e inspecionado, conforme
`## Demonstração visual obrigatória`. O princípio II é preservado por FR-001, FR-035, SC-012 e pelo
invariante de imutabilidade do já publicado: a cadeia "dados estruturados → versão homologada → PDF publicado" continua demonstrável, o
corpo normativo continua função pura do snapshot e Publicação já praticada permanece imutável.

**Trava de escopo declarada.** A frase que governa a feature, repetida em `## Out of Scope`, é a
mesma que a `007` usou para não virar espiral. Depois desta feature, a autoria fica congelada salvo
bug bloqueante, e a próxima spec muda de ator: inscrição do candidato e documentos.
