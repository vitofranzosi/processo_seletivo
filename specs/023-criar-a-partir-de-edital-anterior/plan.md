# Implementation Plan: Criar Edital a partir de Edital anterior

**Branch**: `claude/edital-template-creation-1960e2` | **Date**: 2026-09-09 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/023-criar-a-partir-de-edital-anterior/spec.md`

## Summary

Uma operação só, na composição de um Edital **vazio**: escolher um Edital publicado do escopo e
receber a configuração dele já gravada, para editar pelo assistente que já existe.

A abordagem técnica é consequência direta de três decisões da spec, e nenhuma delas cria mecanismo
novo:

- a fonte é a **versão vigente consolidada** da origem (`D-003`), lida por `effective_version` e
  elevada por `elevar` — os dois já são o idioma de leitura de conteúdo publicado neste
  repositório;
- o registro nomeia a **versão consolidada** de onde o conteúdo saiu — que é o que a Constituição
  pede de quem incorpora conteúdo reutilizável: *preservar independência **e** versão*;
- a escrita entra por **`replace_draft`**, o mesmo comando que toda gravação do assistente usa —
  segunda porta para as mesmas invariantes é o que esta feature mais evita;
- entre ler e escrever há **um mapa de identidades** e uma substituição uniforme sobre o payload. É
  o único código realmente novo, e é onde está todo o risco.

Três descobertas mudaram o desenho e valem antecipar. A primeira é que **a coerência
interna do conteúdo copiado é preservada mesmo sem remapeamento** (`T-005`): um conjunto de
identificadores da origem continua consistente consigo mesmo, atravessa a validação de gravação e só
falha na publicação — daí `FR-010a` e um teste por referência. A segunda é que **o conteúdo canônico
traz três instantes em texto ISO** e `validate_event` chama `timezone.is_aware`, que estoura em
`str` (`T-002`): a conversão não é polimento, é condição de funcionamento. A terceira veio da análise
cruzada: **a reserva da chave de idempotência precede as precondições mutáveis** (`FR-017a`), porque a
operação altera justamente a precondição que seria conferida — depois da primeira cópia o rascunho
não está mais vazio, e a repetição viraria recusa.

Nenhuma migration, nenhum modelo, nenhuma permissão, nenhum estado novo — a régua de `§2` da spec.

## Technical Context

**Language/Version**: Python 3.13

**Primary Dependencies**: Django 5.2. Nenhuma dependência nova.

**Storage**: PostgreSQL. Escrita **apenas** nas tabelas que o assistente já escreve — Perfil e
aninhados, Cronograma e Eventos, Etapas, Documentos Exigidos, Seções, Anexo e Artefato — mais um
registro de auditoria. Nenhuma tabela, nenhuma coluna, nenhuma migration.

**Testing**: pytest com pytest-django, contra PostgreSQL (`make test-pg`). Sem o par
`TEST_DB_ENGINE=postgresql` e `DB_USER` a suíte cai para SQLite e mente.

**Target Platform**: interface administrativa server-side renderizada, servida pelo monólito.

**Project Type**: monólito Django com renderização no servidor.

**Performance Goals**: a operação é interativa e única por Edital. O conteúdo de um Edital real —
sete Perfis, doze Eventos, cinco Etapas, dez Documentos, nove Anexos — cabe folgadamente numa
transação. Os Anexos são o único item de tamanho: até 5 MB cada, em coluna binária.

**Constraints**: uma transação; nenhuma escrita na origem; nenhum dado de execução no destino;
nenhuma referência do destino apontando objeto da origem; idempotência por chave; o conteúdo copiado
passa pelas mesmas validações da composição.

**Scale/Scope**: um serviço de aplicação novo, um seletor de origens, uma afordância na primeira
etapa do assistente, um aviso, um evento de auditoria. Nenhum app novo.

## Constitution Check

*GATE: aprovado antes da Fase 0 e reavaliado após a Fase 1.*

| Princípio | Exigência | Como esta feature responde |
|---|---|---|
| I — Linguagem ubíqua e integridade | Conceitos distintos; identificadores estáveis; invariantes em constraint | Nenhum conceito novo: a operação fala Edital, Perfil, Modalidade, Etapa, Evento, Documento Exigido, Seção e Anexo. **Um termo exigiu decisão** (`T-008`): *proveniência* já designa, neste domínio, a relação `caminho → Publicação` de `VersaoConsolidada.proveniencias`. O que esta feature registra é **origem**, e é assim que o código a nomeia — reusar *proveniência* criaria dois sentidos para a mesma palavra, que é exatamente o que o princípio I recusa. Identidade: toda entidade copiada nasce com identidade própria, e a da Seção é derivada de `(edital, chave)` pelo mecanismo que já existe. **Passa** |
| II — Integridade normativa e temporalidade | Fonte única; publicado imutável; estado vigente reproduzível | A origem é **lida e nunca tocada** — nem conteúdo, nem versão, nem revisão (`FR-012`). A leitura é a da versão vigente, pelo mesmo seletor que a classificação e a supervisão usam, e elevada pelo mesmo conversor: a cópia não interpreta esquema antigo por conta própria. O destino nasce em elaboração e nada entra em snapshot, hash ou `SCHEMA_VERSION` — a operação não publica nada. E não existe vínculo dinâmico: depois da cópia os dois Editais são independentes (`FR-018`). **Passa** |
| III — Segurança, dados pessoais e auditoria | Negar por padrão; menor privilégio; sem IDOR; LGPD; auditoria de ato sensível | Permissão exigida: `edital:elaborar`, que já é a do ato de elaborar (`D-001`); nenhuma permissão nova. A origem é restrita ao **escopo institucional do ator** e a Editais publicados ou encerrados (`D-008`) — conteúdo que o portal público já entrega, de modo que a leitura não concede nada de novo; origem fora disso é `404` indistinguível, como no resto da gestão. Dado pessoal: **nenhum** atravessa a operação — o que se copia é configuração, e `FR-013` proíbe todo o resto. O ato é auditado com ator, instante e origem (`FR-015`). **Passa** |
| IV — Regras explícitas e consistência | Regra no backend; estados explícitos; transação; concorrência | Toda a regra vive no serviço de aplicação; o template só oferece e recusa. Uma transação do começo ao fim (`§7.1` da spec), com os Anexos antes dos Documentos Exigidos. Concorrência pelo `compare_and_swap` que `replace_draft` já faz, e idempotência pela reserva de chave que os comandos de criação já usam (`T-009`). O estado do Evento copiado é **explicitado**, não herdado: nasce `PLANEJADO` (`FR-008a`). **Passa** |
| V — Qualidade, rastreabilidade e simplicidade | Rastreável; testado no nível certo; solução mais simples | Cada `FR` tem cenário em [quickstart.md](./quickstart.md). A solução mais simples é a escolhida: ler o conteúdo publicado, remapear, e gravar pelo comando existente. **A tentação recusada está nomeada**: extrair de `replace_draft` um núcleo interno para evitar um segundo registro de auditoria seria refatorar o comando mais sensível do sistema por cosmética (`T-004`). Cobertura específica onde a Constituição a exige — documentos, cotas, elegibilidade, classificação e autorização — porque é disso que a cópia é feita. **Passa** |
| VI — Completude de jornada e valor demonstrável | Capacidade observável pelo canal do ator | A entrega termina em jornada navegável pela interface administrativa: criar o Edital, escolher a origem, ver a configuração no assistente, alterar o que mudou, publicar. A negação faz parte da entrega — sem a recusa sobre rascunho não vazio demonstrada, a feature não entregou o que promete. **E a proveniência conta como capacidade**: guardar a versão no registro não basta se quem abre a trilha vê um identificador cru, e é por isso que `FR-014a` existe. **Passa** |

| **Restrições e Invariantes** — modelos reutilizáveis | *"Modelos reutilizáveis DEVEM ser apenas origem controlada. Alterá-los NÃO PODE modificar retroativamente instâncias incorporadas por Edital; estas DEVEM preservar independência e versão."* | É a cláusula escrita para esta feature, e nenhuma spec anterior a citou. **Origem controlada**: só Edital publicado ou encerrado do escopo serve de origem (`D-008`). **Independência**: `FR-018` e `FR-012` — nem sincronização, nem escrita na origem. **Versão**: o registro nomeia a **versão consolidada** de onde o conteúdo saiu, e não só o Edital (`FR-015a`) — sem isso, uma Retificação posterior na origem deixaria *de qual configuração partimos* sem resposta. **Passa** |

**Nenhuma exceção vai para `Complexity Tracking`.** É o resultado esperado de uma feature cuja régua
de tamanho é requisito (`§2` da spec) e cujo `SC-007` a verifica.

**Reavaliação após a Fase 1.** O desenho não introduziu violação nova, e fechou dois pontos que o
gate inicial deixava em aberto:

- o princípio **I** obrigou a trocar uma palavra: *origem*, não *proveniência* (`T-008`);
- o princípio **III** ganhou a forma exata da recusa: origem inelegível e origem fora do escopo
  respondem igual — `404` —, e é `T-007` que descreve onde cada recusa é dita.

## Project Structure

### Documentation (this feature)

```text
specs/023-criar-a-partir-de-edital-anterior/
├── spec.md
├── plan.md              # este arquivo
├── research.md          # Fase 0 — T-001 a T-009
├── data-model.md        # Fase 1 — o mapa da cópia; nenhuma entidade nova
├── quickstart.md        # Fase 1 — os cenários que provam a feature
├── contracts/
│   └── copia.md         # Fase 1 — contrato do serviço, recusas e evento de auditoria
├── checklists/
│   └── requirements.md
└── tasks.md             # Fase 2 — $speckit-tasks, ainda não criado
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── editais/
│   ├── application/
│   │   ├── draft.py            # existente — `replace_draft`, a porta de escrita
│   │   ├── anexos.py           # existente — regras do Anexo, reusadas sem os comandos
│   │   └── reaproveitamento.py # NOVO — o serviço da cópia, e o mapa de identidades
│   └── domain/
│       └── reaproveitamento.py # NOVO — remapear payload e converter instantes (funções puras)
├── publicacoes/
│   └── application/selectors.py # existente — `effective_version`
├── interface/
│   ├── views.py                # a view da escolha; a afordância; o aviso
│   ├── urls.py                 # a rota `editais/<uuid>/reaproveitar`
│   └── templates/interface/
│       ├── compor_base.html            # o aviso permanente, herdado por todas as etapas
│       ├── compor_identificacao.html   # o cartão "partir de um Edital anterior"
│       └── reaproveitar.html           # NOVO — a escolha da origem
└── tests/
    ├── unit/editais/test_reaproveitamento.py         # NOVO — as funções puras (Fase 2 inteira)
    ├── integration/editais/test_reaproveitamento.py  # NOVO — isolamento e remapeamento
    ├── authorization/test_reaproveitamento.py        # NOVO — permissão, escopo e elegibilidade
    └── interface/test_reaproveitar.py                # NOVO — a jornada e as recusas
```

**Structure Decision**: a feature mora no app `editais`, que é o dono da elaboração, e consome
`publicacoes` só como leitura. **Sem `forms.py`**: o formulário da escolha tem dois campos — a origem
e a chave de idempotência —, e `forms.py` existe para reconstruir coleções a partir de campos
indexados. Um `ler_*` para dois campos seria cerimônia; a view lê direto, como as telas de criação
já fazem. **O domínio recebe funções puras** — remapear e converter — porque são
o que se testa exaustivamente sem banco; a aplicação orquestra a transação. Nenhum app novo, nenhum
pacote novo.

## Fases de implementação sugeridas

### Faixa 1 — O serviço da cópia (`US1`, `US2`)

O serviço inteiro, na ordem obrigatória de `§7.1` da spec, com o mapa de identidades e a conversão de
instantes. Termina com o teste de isolamento e **um teste por referência que a gravação não confere**
(`FR-010a`): Anexo, `stages` do marco, critério → Etapa/fato, `drawMethod.qualifyingStageId`.

Ao fim desta faixa a capacidade existe e é exercitável por teste — mas ainda não pela tela, e por
isso ela não é entregável sozinha (Princípio VI).

### Faixa 2 — A escolha da origem (`US1`)

O seletor de origens elegíveis, a afordância na primeira etapa do assistente e a recusa sobre
rascunho não vazio. É aqui que a jornada fecha e a feature passa a ser demonstrável.

### Faixa 3 — O aviso e a trilha (`US3`)

O evento de origem — que nomeia a **versão** consolidada, não o Edital (`FR-015a`) — e o aviso
permanente montado a partir dele, nunca de texto livre.

**E a trilha, que é a metade que sobrevive.** O aviso desaparece quando o Edital sai da elaboração; a
entrada de auditoria fica. Ela precisa de rótulo em `OPERACOES` e do motivo **enriquecido** — Edital e
versão em forma legível, não o identificador cru que o registro guarda (`FR-014a`, `T-010`). Sem isso
`US3` estaria atendida no banco e não no canal do ator.

O aviso mora em `compor_base.html`, que todas as etapas do assistente estendem. **E não em
`base.html`**: mexer naquela folha já custou asserção de template quebrada neste repositório, e ela
alcançaria telas a que o aviso não pertence.

### Conferências que atravessam as três faixas

- `make lint check test-pg` — os dois passos do lint, e a suíte contra PostgreSQL.
- `makemigrations --check` limpo, que é a verificação objetiva de `SC-007`.
- A jornada de ponta a ponta pelo navegador, com um Edital de origem **retificado**, para que
  `SC-008` seja observado e não presumido.

## Complexity Tracking

Sem violações a justificar. A tabela fica vazia de propósito: se algo precisar entrar aqui, é sinal
de que a régua de `§2` foi cruzada e o desenho volta para revisão.
