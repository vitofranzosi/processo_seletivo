# Implementation Plan: Integridade do Snapshot Normativo

**Branch**: `005-integridade-do-snapshot` | **Date**: 2026-08-29 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/005-integridade-do-snapshot/spec.md`

## Summary

Nenhuma Retificação pode deixar vigente um Edital que a Publicação original recusaria.

A verificação incide sobre o **snapshot resultante**, e não sobre cada alteração (FR-001): `REMOVE`
não tem valor a validar, e alterações individualmente plausíveis podem compor um resultado inválido.
Ela acontece na elaboração, sobre o resultado de aplicar tudo à base declarada (FR-002), e de novo na
Publicação, sobre cada versão consolidada que o ato materializa (FR-003).

O que se confere em cada Perfil e Evento (FR-004) são quatro dimensões que o contrato da `001` já
declara:
campo obrigatório presente, tipo JSON correto, nulo só onde admitido, formato satisfeito. Campo
desconhecido é aceito. Faixa de valor e enumeração ficam de fora por decisão explícita.

**A feature é menor do que parece, e uma descoberta a encolhe mais.** O laço que materializa as
versões já chama a verificação estrutural uma vez por fronteira de vigência. FR-003 não pede laço
novo — pede que a verificação chamada ali seja mais funda.

## Technical Context

**Language/Version**: Python 3.13 — o mesmo do backend

**Primary Dependencies**: nenhuma nova. `jsonschema` existe no projeto, mas como dependência de
**desenvolvimento**, usada pelos testes de conformidade; o domínio não pode depender dela. As quatro
dimensões são verificadas em código próprio, e são quatro

**Storage**: nenhuma mudança. Nenhuma coluna, nenhuma migração

**Testing**: pytest e pytest-django, nas duas execuções — SQLite e PostgreSQL

**Target Platform**: mesmo processo Django do backend

**Project Type**: monólito modular existente; nenhuma estrutura nova

**Performance Goals**: nenhuma meta própria. A verificação percorre dezenas de Perfis e Eventos por
fronteira, e uma Publicação materializa poucas fronteiras. Medir antes de haver sintoma seria ruído

**Constraints**: a recusa na Publicação não pode deixar Publicação, documento ou versão
materializados; nenhum código de erro novo entra no contrato; nenhuma etapa nova para quem elabora

**Scale/Scope**: o mesmo da `001`. Um Edital tem dezenas de Perfis e Eventos

**Questões em aberto**: nenhuma. As três da revisão foram resolvidas em `$speckit-clarify`.

## Constitution Check

| Princípio | Situação |
| --- | --- |
| I — Linguagem ubíqua e integridade do domínio | **Atendido.** A verificação mora no domínio, junto da que já existe, e fala de Perfil, Evento e Edital. |
| II — Integridade normativa, imutabilidade e temporalidade | **Atendido, e é o ponto.** A verificação alcança **cada fronteira de vigência** materializada, e não só a que passa a vigorar de imediato — a temporalidade do conteúdo é parte do que se verifica. |
| III — Segurança, proteção de dados e auditoria | **Neutro, com avaliação registrada.** Nenhum endpoint, permissão ou consulta nova. A avaliação de LGPD está na spec: não aplicável, sem dado pessoal e sem acesso novo. |
| IV — Regras explícitas e consistência operacional | **É a exigência que a feature cumpre.** *"A operação DEVE validar inconsistências, classificá-las como informação, aviso ou erro impeditivo e bloquear a publicação diante de erro impeditivo."* A exigência valia; o que faltava era ela alcançar o conteúdo que uma Retificação faz vigorar, e não só a raiz do Edital. |
| V — Qualidade, rastreabilidade e simplicidade | **Atendido.** Rastreabilidade nos dois sentidos na spec. A solução mais simples que preserva os requisitos: um validador mais fundo no lugar que já é chamado, em vez de um mecanismo paralelo. |
| Fluxo de desenvolvimento | **Atendido, sem exceção.** Especificação, clarificação, portão de qualidade, plano. Nenhuma linha de código escrita. |

## Decisões técnicas

### Decisão 1 — A autoridade é o contrato; a declaração mora no domínio

`PerfilInput` e `EventoInput` no `openapi.yaml` da `001` já dizem quais campos são obrigatórios, de
que tipo, quais admitem nulo e que formato têm. É a autoridade, e a spec a nomeia (FR-005).

O domínio **não pode lê-lo em tempo de execução**: o arquivo vive em `specs/`, não é distribuído com
o pacote, e fazer o domínio depender de um artefato de especificação inverteria a relação entre os
dois. Então a forma é **declarada no domínio e verificada por teste** contra o contrato — o mesmo
padrão que a `004` usa para as coleções com chave, onde a declaração explícita substituiu uma
detecção que acertava hoje e falharia calada amanhã.

O teste de guarda compara a declaração com o contrato **apenas nas quatro dimensões**. Comparar
tudo faria a guarda exigir o que a Decisão 2 deixa de fora.

### Decisão 2 — Quatro dimensões, e o que o contrato declara e não se verifica

O contrato diz mais do que as quatro dimensões:

```yaml
immediateVacancies: { type: integer, minimum: 0 }
reserveType:        { type: string, enum: [NONE, LIMITED, UNLIMITED] }
reserveLimit:       { type: [integer, 'null'], minimum: 0 }
```

`minimum` e `enum` são **regra de negócio**, e FR-009 as mantém fora. Um Perfil com
`immediateVacancies: -3` continua publicável depois desta feature.

Isso é deliberado e precisa estar escrito, porque "a autoridade é o contrato" convida a implementar
o contrato inteiro. Decidir se um Perfil pode ter vagas negativas é discussão normativa; esta
feature responde outra pergunta — se o conteúdo tem a **forma** de um Edital.

### Decisão 3 — A Publicação já verifica cada fronteira

`_materialize_affected_versions` percorre as fronteiras de vigência afetadas e chama
`_assert_structurally_publishable(content, boundary)` **dentro do laço**, antes de materializar cada
versão. A mensagem já nomeia a fronteira.

FR-003 está estruturalmente satisfeito. O que falta é a verificação chamada ali ser mais funda —
e testes que provem o comportamento por fronteira, que hoje não existem.

**Consequência**: quem implementar não deve construir um segundo laço. Um mecanismo paralelo ao que
já existe seria a duplicação que o princípio V manda evitar.

### Decisão 4 — Onde a verificação entra na elaboração, e em que ordem

Em `_apply_declared_changes`, que serve tanto à criação quanto à edição do rascunho. A ordem das
recusas ali passa a ser:

1. o caminho resolve e a alteração é aplicável — recusas da `004`;
2. as precondições de conteúdo se verificam — recusas da `003`;
3. **o resultado tem forma de Edital** — esta feature (FR-002);
4. o ato tem efeito prático.

Nenhuma das três primeiras muda de comportamento: FR-015 mantém intactos o endereçamento da `004` e
as precondições da `003`, e FR-014 exige que a Retificação bem formada siga publicável sem etapa
nova.

A malformação vem **depois** da precondição porque quando as duas valem a precondição é mais
acionável: ela diz "outra pessoa publicou no intervalo, refaça sobre a versão atual", enquanto a
malformação diz "o que você mandou está incompleto". Quando a segunda é consequência da primeira,
mostrar a causa serve melhor.

E vem **antes** do efeito prático porque "não muda nada" é queixa mais fraca que "deixaria um Perfil
sem denominação".

### Decisão 5 — Nenhum código de erro novo, e um que o contrato esqueceu de declarar

A recusa usa `blocking_findings` com `422` (FR-010) — o código que o sistema já emite em nove pontos
para erro impeditivo de publicação. Passa a valer também na elaboração. A recusa na Publicação
continua sem deixar Publicação, documento ou versão materializados (FR-012), porque a operação já é
transacional.

Um código novo diria a mesma coisa com outro nome. O que muda é **quando** a recusa acontece e **o
que** ela alcança, não a sua natureza.

**Achado ao conferir esta decisão**: o `openapi.yaml` **não nomeia** `blocking_findings` em lugar
nenhum. Ele nomeia `expected_hash_mismatch`, `target_already_present`, `inconsistent_consolidation` e
os três da `004`, mas o código mais antigo de todos ficou de fora — junto com `precondition_missing` e
`no_effective_change`. O schema `Problem` declara `code` como texto livre, então nada quebrou; o
cliente é que nunca soube o que esperar.

Esta feature declara `blocking_findings` no contrato, porque passa a produzi-lo num momento novo e
seria estranho documentar o momento sem documentar o código. Os outros dois ficam anotados como
lacuna anterior, e não são desta feature.

### Decisão 6 — O caminho no achado usa a gramática da `004`

`ValidationFinding` já carrega `path`, hoje com `"title"` ou `"profiles"`. Os achados novos passam a
carregar `/profiles/id=<uuid>/name` — a forma que a `004` estabeleceu, que nomeia a entidade sem
consultar a versão vigente (FR-011).

**Consequência a vigiar**: a tela de composição usa `validate_for_publication` para listar
pendências e mapeia `path` → etapa por `DESTINO_DA_PENDENCIA`. Caminho desconhecido cai em "não
corrigível". Na prática os achados novos não aparecem lá, porque o snapshot de um Edital em
composição é montado do ORM e sempre traz as entidades completas — mas isso é pressuposto, e vira
teste.

### Decisão 7 — Modalidades ficam opacas

O contrato declara `competitionModalities: { type: array, items: { type: object } }`. Sob a Decisão
1, a verificação confere que é lista de objetos e nada mais.

É o próprio contrato traçando o limite, e não uma omissão nossa. Se um dia as Modalidades ganharem
forma declarada, esta verificação passa a alcançá-las sem mudança de desenho.

### Decisão 8 — Entidade sem identificador utilizável

Sem `id` não há como montar o caminho por chave. A `004` já recusa isso no momento em que a
alteração é aplicada, então o caso não chega aqui pela Retificação — mas `validate_for_publication`
também roda no caminho da Publicação original e na tela.

O achado então nomeia a posição — `/profiles/2/name` — em vez de não nomear nada. É recuo de
legibilidade num caso que não deve ocorrer, e é melhor que um achado mudo.

## Project Structure

### Documentation (this feature)

```text
specs/005-integridade-do-snapshot/
├── spec.md              # 15 requisitos, 5 critérios, 2 histórias
├── plan.md              # este documento
├── research.md          # Fase 0: alternativas de autoridade, de local e de momento
├── data-model.md        # Fase 1: a forma declarada, campo a campo
├── quickstart.md        # Fase 1: como validar, com o resultado esperado de cada passo
├── contracts/
│   └── integridade.md   # Fase 1: as quatro dimensões, os achados e o delta do openapi
└── checklists/
    └── requirements.md  # portão de qualidade da spec, com as notas da reavaliação
```

### Source Code (repository root)

```text
backend/
├── processo_seletivo/
│   ├── editais/domain/
│   │   └── validation.py          # a forma declarada e a verificação por entidade
│   └── publicacoes/application/
│       └── retificacoes.py        # a chamada na elaboração; a da Publicação já existe
└── tests/
    ├── unit/editais/              # a forma declarada, as quatro dimensões, os achados
    ├── contract/                  # a declaração conferida contra o openapi.yaml
    ├── integration/publicacoes/   # os dois momentos, e a recusa por fronteira posterior
    └── interface/                 # a tela de composição não regride
```

**Structure Decision**: monólito modular existente, sem estrutura nova e sem módulo novo. A forma
declarada fica em `validation.py`, junto da verificação que ela aprofunda: são as duas metades da
mesma pergunta — o que torna um Edital publicável —, e separá-las obrigaria a ler dois arquivos para
responder uma coisa só.

## Fases

| Fase | Conteúdo | Situação |
| --- | --- | --- |
| — | Especificação | Concluída |
| — | Clarificação — três decisões da revisão | Concluída |
| — | Portão de qualidade dos requisitos | Concluído, 16/16 |
| 0 | Pesquisa: autoridade, local e momento da verificação | Concluída |
| 1 | Desenho: forma declarada, contrato dos achados, validação | Concluída |
| 2 | Tarefas | Não iniciada |
| 3 | Análise de consistência | Não iniciada |
| 4 | Implementação | Não iniciada |

## Critérios de entrega recolhidos da checklist

O critério de cobertura saiu dos critérios funcionais na reavaliação da spec, por ser métrica de
entrega e não resultado observável por quem usa. Fica aqui, que é o lugar dele:

- suíte verde nas duas execuções, SQLite e PostgreSQL;
- cobertura com ramos **integral** do código escrito nesta feature;
- cada recusa nova verificada removendo-a, para confirmar que o teste discrimina o defeito.

## Complexity Tracking

| Desvio | Por quê | Alternativa descartada |
| --- | --- | --- |
| A forma é declarada no domínio e não lida do contrato | O `openapi.yaml` vive em `specs/` e não é distribuído com o pacote; fazer o domínio depender de um artefato de especificação inverteria a relação entre os dois | Ler o contrato em tempo de execução. Descartada por acoplar domínio a artefato de processo, e por transformar um arquivo de documentação em dependência de produção |
| Duas fontes sobre a mesma forma | A declaração no domínio e o contrato dizem a mesma coisa, e duplicação é o que o princípio V manda evitar | Aceitar a divergência silenciosa. Descartada: o teste de guarda transforma a divergência em falha de suíte, que é o preço já pago na `004` pelo mesmo motivo |
| `minimum` e `enum` declarados e não verificados | FR-009 mantém regra de negócio fora, e implementá-las aqui decidiria por antecipação o que um Perfil deve exigir | Verificar o contrato inteiro. Descartada por exceder o escopo acordado e misturar duas perguntas diferentes |
