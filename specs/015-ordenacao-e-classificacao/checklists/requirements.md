# Specification Quality Checklist: Ordenação e Classificação

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-04
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

**Histórico da validação.** A primeira passagem fechou em **13/16**, e não em 15/16: além dos três
marcadores [NEEDS CLARIFICATION], "requirements are testable and unambiguous" e "all functional
requirements have clear acceptance criteria" também falhavam, porque um requisito com pergunta
aberta dentro não é testável. A segunda passagem, depois das respostas, fecha em **16/16**.

**O que as três respostas fixaram:**

1. **Combinação (FR-008 a FR-012).** O marco enumera as Etapas; `weight` continua sendo a fonte
   autoritativa do peso; só Etapa classificatória participa; a operação nova declara também
   normalização e arredondamento; os pesos não precisam somar 1.
2. **Empate residual (FR-023 a FR-026).** Emite com posições compartilhadas, e o ato registra que
   dentro do grupo empatado não existe ordem normativa. O corte que atravessar o grupo é problema
   da 014.
3. **Eliminado na Etapa do marco (FR-007).** Permanece no snapshot como participante considerado,
   sem posição, com consequência e motivo — fechando com FR-003, FR-006 e SC-016.

**Dois ajustes que não vieram das perguntas:**

- a **regra do marco entrou no universo** (D-003, FR-003, FR-034, IO-7, SC-013): Retificação que
  alcance operação, enumeração, pesos ou critérios obsoleta o ato sem que nenhuma entrada mude;
- **valor ausente virou requisito** (FR-017), e não suposição: critério sem comportamento declarado
  para valor inexistente impede a publicação da regra.

**Terceira análise cruzada (2026-09-04).** Zero CRITICAL, zero HIGH, zero tarefas órfãs. O que
sobrou foi de duas naturezas, e as duas foram fechadas: a árvore de código do plano ainda não listava
`portal/`, embora a prosa ao lado já dissesse que ele recebe os campos dos fatos — a rodada anterior
corrigiu a frase e esqueceu o desenho; e seis requisitos estavam implementados por tarefa sem
**tarefa de verificação**, o que não é inconsistência e sim cobertura de teste.

Os seis foram distribuídos pelas fatias em que incidem, e não amontoados no fim: o grupo empatado
visível e a restrição de acesso aos fatos de desempate em US3; o Resultado tardio dentro do universo
e o obsoleto que continua produzindo efeito em US4; o critério que separou as vizinhas em US5; e os
três requisitos negativos como um teste de guarda no Polish. São 101 tarefas.

Duas observações ficaram sem ação, por escolha: a seção "2b" do contrato do marco e o título da US2,
que nomeia os fatos e cobre também o teto. As duas são de forma, nenhuma muda o que se implementa, e
a terceira passada já é o ponto em que o retorno da análise deixa de pagar o custo.

**Segunda análise cruzada (2026-09-04).** Com C1 e C2 fechados, a passada seguinte pegou o que as
próprias edições introduziram: a Structure Decision do plano ainda afirmava que nada era acrescentado
ao `portal`, e a US2 acrescenta; o quickstart não tinha entrega alguma para uma história P1, o que o
Princípio VI não admite; nenhum contrato descrevia a forma publicada de `declaredFacts` e do teto; e
`ValorDeFato` estava com `inscricao` em CASCADE numa tabela append-only cujo runtime não tem
`DELETE` — um CASCADE que nunca poderia executar, corrigido para PROTECT como em
`ResultadoEtapa.inscricao`.

Três lacunas de cobertura viraram tarefa: o teto contando só submetidas, a Retificação que reduz o
teto sem invalidar o já submetido, e a ponte entre D-2 e o desempate — inscrição anterior à
declaração do fato, tratada pelo comportamento declarado para valor ausente.

**Análise cruzada (2026-09-04).** O `speckit-analyze` encontrou uma questão CRITICAL e uma HIGH, e
as duas eram o mesmo buraco visto de dois lados: onze tarefas implementavam D-2 e D-3 sem um único
requisito na spec, e o `data-model.md` não modelava as entidades que elas criavam. A leva foi
decidida depois de a spec estar escrita, e ninguém voltou para fechá-la.

Fechado assim: história US2 nova (o candidato informa os fatos e os vê congelados), dez requisitos
(FR-057 a FR-066) e quatro critérios (SC-019 a SC-022); `FatoDeclarado`, `ValorDeFato` e o teto no
`data-model.md`; e a leva partida em duas no `tasks.md` — o que é esquema fica na Foundational,
porque a elevação canônica precisa carregar tudo de uma vez, e o que é jornada do candidato virou
fase própria com cenário demonstrável.

Os requisitos novos foram **acrescentados ao fim** da seção em vez de junto dos assuntos que
descrevem. É deliberado e está dito na spec: renumerar teria quebrado quarenta citações em plano,
contratos, quickstart e tarefas, e rastreabilidade vale mais que ordem de leitura.

Uma consequência que a modelagem revelou e que ficou escrita em vez de descoberta depois: com
`ValorDeFato` append-only, o candidato **não corrige** o que informou depois de submeter — a 009 não
tem retificação de inscrição, e esta feature não a cria.

**Revisão do plano (2026-09-04).** Quatro achados de desenho voltaram para a spec, e três deles
mudaram requisitos:

- **a sucessão passou a ser append-only de verdade** (FR-031 a FR-035). O desenho anterior virava um
  booleano `vigente`, e isso é impossível: a política de papéis roda `REVOKE UPDATE, DELETE` sobre as
  tabelas append-only (`seguranca/papeis.py:129`), e exceção em trigger não devolve privilégio. O ato
  sucessor aponta o anterior; vigente é o ato que ninguém sucedeu;
- **o "não recomputável" foi reformulado** (FR-040 a FR-043). O cenário que o disparava — critério
  apontando Etapa removida — é inalcançável, porque a publicação o recusa. O caso real é a remoção do
  **marco**, e ficou explícito que não recomputável não é irreproduzível;
- **o teto de tempo ganhou a segunda prova** (SC-002 e SC-003). Orçamento de consultas não prova
  tempo: uma consulta pode ser lenta, e mil linhas podem estourar o teto sem mudar a contagem;
- **a ordem dos critérios virou campo publicado** (FR-015), porque a Retificação endereça por
  identidade e a primeira redação não dizia como reordenar.

A quarta — a leva de D-1, D-2 e D-3 — não é ajuste de redação e está com o usuário.

**Sessão de clarificação (2026-09-04).** Cinco perguntas, cinco respostas, todas integradas: a
emissão concorrente é recusada e suceder exige recálculo com confirmação explícita (FR-029,
FR-030); a numeração segue a classificação padrão, `1, 1, 3` (FR-025, IO-9, SC-017); reprodução é
garantia interna testável e a jornada expõe a proveniência inteira (FR-039 a FR-041); ato cuja
regra deixou de ser computável fica obsoleto **e não recomputável**, dito na tela (FR-037, FR-038,
SC-014); e a tela do marco abre em até 3 segundos a 1.000 participantes (SC-002). Os 16 itens
permanecem passando depois das integrações.

A US5 deixou de depender de "Resultado revisto" — a 013 admite um Resultado imutável por Inscrição
× Etapa, e superá-lo é da 018. A sucessão passa a nascer de Resultado tardio ou de Retificação da
regra, e permanece compatível com a 018 sem pressupô-la.

Nomes citados no corpo — `SCHEMA_VERSION`, `weight`, `classificatory`, `ResultadoEtapa`,
`competitionModalities` — são referências a conteúdo normativo e a contratos já entregues,
verificados no código em 04/09/2026, e não escolha de implementação desta feature.
