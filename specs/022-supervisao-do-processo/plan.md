# Implementation Plan: Supervisão do Processo

**Branch**: `claude/spec-022-supervisao-do-processo` | **Date**: 2026-09-09 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/022-supervisao-do-processo/spec.md`

## Summary

Uma página de leitura por Processo Seletivo, para quem o preside, com duas regiões e nada além:
**Pulso** — inscrições somadas no Processo, desdobradas por Edital, com série diária de submissões,
prazo do período e próximos marcos — e **Atenção** — cinco sinais nomeados, e só eles.

A abordagem técnica é a consequência direta de `D-007`: **composição de leituras existentes, sem
modelo, sem migration e sem escrita.** Sete apps já persistem tudo o que a página mostra; o trabalho
é somar no nível certo, confrontar com o tempo, e formular cinco perguntas que nenhuma tela dona faz
porque nenhuma delas é dona da fronteira.

Duas decisões técnicas carregam a maior parte do risco, e as duas foram fechadas na Fase 0:
obsolescência por **filtro barato e confirmação exata** (`T-003`), e impedimento por **álgebra de
conjuntos** em vez de verificação por par (`T-004`). A segunda encontrou um limite que **estreitou um
requisito**: quem detém a permissão de julgar não é determinável, e o sinal passou a afirmar apenas
o que verifica.

## Technical Context

**Language/Version**: Python 3.13

**Primary Dependencies**: Django 5.2. Nenhuma dependência nova — a feature não introduz biblioteca
de gráfico, de agregação nem de cache.

**Storage**: PostgreSQL. **Somente leitura.** Nenhuma tabela, nenhuma coluna, nenhuma migration.

**Testing**: pytest com pytest-django, contra PostgreSQL (`make test-pg`). Sem o par
`TEST_DB_ENGINE=postgresql` e `DB_USER` a suíte cai para SQLite e mente.

**Target Platform**: interface administrativa server-side renderizada, servida pelo monólito.

**Project Type**: monólito Django com renderização no servidor; sem SPA e sem build de front-end.

**Performance Goals**: a página abre em uma leitura, com custo proporcional ao **que mudou** e não
ao tamanho do Processo. O orçamento de consulta é o assunto de `T-002`, `T-003` e `T-004`.

**Constraints**: nenhuma escrita; nenhum estado persistente derivado; nenhum percentual sem par
numerador/denominador; nenhuma data apresentada sem o Edital a que pertence; supressão silenciosa
por alcance.

**Scale/Scope**: dezenas a poucos milhares de inscrições por Edital; comissão de duas a três
pessoas; um a três Editais por Processo. Uma página nova, um módulo de leitura, um template.

## Constitution Check

*GATE: aprovado antes da Fase 0 e reavaliado após a Fase 1.*

| Princípio | Exigência | Como esta feature responde |
|---|---|---|
| I — Linguagem ubíqua e integridade | Conceitos distintos; identificadores estáveis; identificador público não autoriza; invariantes em constraint | Nenhum conceito novo: a página fala Processo, Edital, Cronograma, Evento, Etapa, Inscrição, Comissão e Recurso, todos já da Constituição. Não há invariante a levar ao banco porque não há dado novo. **Um ponto exigiu decisão e está registrado**: chamar rascunho de *rascunho* onde a tela da `009` diz *em preenchimento* criaria dois termos para o mesmo conceito — a spec registra o conflito como governança e a implementação adota o termo vigente até haver decisão. **Passa** |
| II — Integridade normativa e temporalidade | Fonte única; publicado imutável; estado vigente reproduzível | A supervisão é a definição de fonte não-autoritativa: `FR-005` exige que todo número seja reproduzível a partir dos registros das donas e proíbe que ela constitua fonte de verdade de estado algum. As Etapas vêm da versão publicada pelo resolvedor existente, e não de leitura própria do conteúdo. Nada entra em snapshot, hash ou `SCHEMA_VERSION`. **Passa** |
| III — Segurança, dados pessoais e auditoria | Negar por padrão; menor privilégio; sem IDOR; LGPD avaliada; auditoria de ato sensível | Porta única — presidência do Processo ou permissão sistêmica de gerir comissão —, com 404 uniforme para tudo o que o ator não alcança. Menor privilégio levado até o **elemento**: cada sinal só é montado para quem alcança a tela dona, e a supressão é silenciosa, porque anunciar supressão é vazamento por agregação (`T-008`). Dado pessoal: a página é **agregada por construção** — contagens e nomes de Etapa e de Edital; nenhum nome, CPF ou protocolo de candidato aparece. Não há ato a auditar: leitura de agregado do próprio Processo não é ato sensível, e nenhuma tela de leitura existente registra. **Passa** |
| IV — Regras explícitas e consistência | Regra no backend; estados explícitos; transação; concorrência | Toda derivação vive no módulo de leitura; o template não decide nada. **Não há estado a explicitar, e a ausência é decisão**: `D-003` recusa criar ciclo de vida de Etapa para alimentar uma tela, e `D-004` preserva a semântica declarada do Evento. Sem escrita não há transação nem concorrência a tratar — a página lê um instante e o declara (`FR-009`). **Passa** |
| V — Qualidade, rastreabilidade e simplicidade | Rastreável; testado no nível certo; solução mais simples | Cada `FR` e cada `UX` tem cenário em [quickstart.md](./quickstart.md), e cada `SC` tem contraprova. A solução mais simples **é** a escolhida: composição de selectors existentes. Duas exceções à simplicidade ingênua foram medidas e justificadas — `T-003` e `T-004` —, e as duas existem para **baratear**, não para generalizar. Nenhum mecanismo genérico de sinais: cinco perguntas nomeadas, catálogo fechado por `D-002` e cobrado pela varredura de citações. **Passa** |
| VI — Completude de jornada e valor demonstrável | Capacidade observável pelo canal do ator | As quatro faixas terminam em página navegável na interface administrativa, que é o canal de quem preside. A faixa 1 sozinha já entrega capacidade que hoje não existe — a soma no nível do Processo. A negação faz parte da entrega: sem o 404 e sem a supressão demonstrados, a feature não entregou o que promete. **Passa** |

**Nenhuma exceção vai para `Complexity Tracking`.** É o resultado esperado de uma feature que não
cria app, modelo, dependência nem estado — e a ausência de exceções é ela própria evidência de que a
fronteira de `D-007` foi respeitada.

**Reavaliação após a Fase 1.** O desenho não introduziu violação nova e fechou dois pontos que o
gate inicial deixava em aberto.

- O princípio **III** ganhou o que faltava: a supressão por alcance foi especificada **por sinal**,
  com a permissão da dona nomeada uma a uma (`T-008`), em vez de uma verificação genérica na porta.
- O princípio **I** obrigou a estreitar um requisito em vez de silenciar um limite. `T-004` mostrou
  que "julgador elegível" não é determinável — a titularidade da permissão de julgar não é
  persistida —, e a alternativa honesta era afirmar menos: `FR-030` passou a falar de **membro
  desimpedido**, e `FR-030a` proíbe a inferência que os dados não sustentam. Chamar de "elegível" o
  que se verifica como "desimpedido" seria o termo impreciso que o princípio I recusa.

Nenhuma dependência nova, nenhum modelo, nenhuma coluna, nenhuma migration.

## Project Structure

### Documentation (this feature)

```text
specs/022-supervisao-do-processo/
├── spec.md
├── plan.md              # este arquivo
├── research.md          # Fase 0 — T-001 a T-009
├── data-model.md        # Fase 1 — modelo de leitura, sem entidade nova
├── quickstart.md        # Fase 1 — cinco roteiros de validação
├── contracts/
│   └── supervisao.md    # Fase 1 — a rota, o que entrega e o que proíbe
├── checklists/
│   └── requirements.md
└── tasks.md             # Fase 2 — gerado por $speckit-tasks
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── interface/
│   ├── supervisao.py                  # NOVO — o módulo de leitura: Pulso e os cinco Sinais
│   ├── views.py                       # + uma view de leitura, na porta da presidência
│   ├── urls.py                        # + uma rota
│   └── templates/interface/
│       ├── supervisao.html            # NOVO — Pulso e Atenção
│       ├── _serie_de_inscricoes.html  # NOVO — a série e seu equivalente textual
│       ├── _sinal.html                # NOVO — a forma única dos cinco
│       └── processo_detalhe.html      # + o caminho até a supervisão
│
├── comissoes/application/selectors.py     # lido, não alterado
├── avaliacoes/application/selectors.py    # lido, não alterado
├── classificacao/application/selectors.py # lido, não alterado
├── recursos/                              # lido, não alterado
├── resultados/                            # lido, não alterado
├── inscricoes/                            # lido, não alterado
└── editais/                               # lido, não alterado

backend/tests/
├── integration/supervisao/            # NOVO
│   ├── test_pulso.py                  # soma, desdobramento, rascunho, série
│   ├── test_sinais.py                 # os cinco, montados e desfeitos
│   ├── test_autorizacao.py            # porta, 404 uniforme, supressão silenciosa
│   └── test_fronteira.py              # nenhuma escrita, nenhuma carga por membro
├── interface/
│   └── test_supervisao.py             # NOVO — a página, o equivalente textual, os destinos
├── unit/interface/
│   └── test_supervisao.py             # NOVO — a enumeração fechada das cinco espécies
├── acceptance/
│   └── test_supervisao_do_processo.py # NOVO — a jornada de quem preside, ponta a ponta
└── migrations/
    └── test_migrations.py             # + a guarda por contagem da 022, no formato da 017
```

**Structure Decision**: sem app novo. A feature não é dona de fato persistido, e app sem modelo
criaria a expectativa de que um dia terá — exatamente a fronteira que `D-007` proíbe atravessar
(`T-001`). O módulo de leitura mora em `interface/`, ao lado da página do Processo que ele estende,
e **importa** os selectors das donas sem reimplementar nenhum.

O arquivo `supervisao.py` fica fora de `views.py` de propósito: é onde vivem as derivações, e
mantê-las separadas da montagem de contexto é o que permite testá-las como domínio de leitura, sem
requisição.

## Fases de implementação sugeridas

Cada faixa termina em comportamento navegável e pode ser demonstrada sozinha.

### Faixa 1 — O Processo acima do Edital (`US1` parcial)

Soma de submetidas, rascunhos como grandeza distinta, desdobramento por Edital nomeado e instante da
leitura.

*Entrega, sozinha, a capacidade que hoje não existe em nível nenhum.* Não depende de cronograma nem
de sinal algum.

**O caminho a partir da página do Processo não é desta faixa**: ele é da fase Foundational, porque
toda story precisa da porta. Sem essa separação, `US3` dependeria de `US1` para ter onde aparecer.

### Faixa 2 — O tempo (`US1`, `US2`)

Período de inscrições por Edital, tempo restante, próximos marcos, últimas 24 horas, série diária
com equivalente textual, e as declarações de ausência (`FR-018`, `FR-022`).

*Fecha o Pulso.* Depende da faixa 1 pela forma `PulsoDoEdital`.

### Faixa 3 — Atenção (`US3`)

Na ordem, porque é a ordem do custo crescente:

1. `UX-001` e `UX-002` — só cronograma e Etapas; nenhuma dependência nova.
2. `UX-003` — reusa `resumo_da_etapa` como está.
3. `UX-004` — filtro barato e confirmação exata (`T-003`).
4. `UX-005` — o único que exige desenho de consulta agregada (`T-004`).

Cada sinal é uma fatia independente: implementado um, a região existe e os demais entram sem mexer
na forma.

### Faixa 4 — Encaminhamento e alcance (`US4`)

Destino por sinal, supressão silenciosa por alcance, e a conferência de que a supervisão não lista o
que conta.

*É a faixa que impede a tentação de listar*, e por isso não deve ser adiada para depois da 3 por
muito tempo.

### Conferências que atravessam todas as faixas

- `makemigrations --check` limpo ao fim de cada faixa — `SC-014`;
- ausência de `save`, `create`, `update` e `delete` no diff — `FR-006`;
- 375 px sem rolagem horizontal do corpo — `FR-016`;
- `make lint check test-pg`, e a varredura de citações por a feature tocar `specs/`.

## Complexity Tracking

> Preenchido apenas quando o Constitution Check tem violação a justificar.

**Nenhuma violação.** A feature não cria app, modelo, coluna, migration, dependência nem mecanismo
genérico. As duas decisões que poderiam parecer complexidade — a confirmação em duas passagens de
`T-003` e a álgebra de conjuntos de `T-004` — existem para **reduzir** custo e para **preservar**
decisões já tomadas por outras features, e a alternativa simples de cada uma está registrada em
`research.md` com o motivo da recusa.
