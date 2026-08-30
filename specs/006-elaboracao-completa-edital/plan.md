# Implementation Plan: Elaboração Completa do Edital

**Branch**: `006-elaboracao-completa-edital` | **Date**: 2026-08-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/006-elaboracao-completa-edital/spec.md`

## Summary

Fechar a jornada de autoria do Edital — do painel à publicação, passando pela prévia do documento —
sem tocar nos mecanismos de publicação e Retificação. O trabalho é **aditivo em três direções já
existentes**: coleções novas entram pelos três registros declarativos que a `004` e a `005`
deixaram prontos (`COLECOES_COM_CHAVE`, `COLECOES_PUBLICADAS`, e o snapshot de
`edital_snapshot`); a interface ganha etapas no assistente que já existe; e o renderizador de PDF,
que já é função pura do snapshot, ganha um modo de prévia.

Nenhum command novo é necessário para reordenar, e `replace_draft` continua sendo o único caminho
de gravação do rascunho. **Um command nasce**, e só um: alterar a identificação do Edital em
elaboração. A prévia não é command — não altera estado, não gera ato e não tem chave de
idempotência: é leitura que compõe um documento a partir do snapshot atual.

## Technical Context

**Language/Version**: Python 3.13 (`backend/pyproject.toml:8`)

**Primary Dependencies**: Django 5.2, Django REST Framework 3.16. Nenhuma dependência nova.

**Storage**: PostgreSQL. Migrations diretas; sem mecanismo de compatibilidade (spec P-002, FR-048).

**Testing**: pytest com `tests/{unit,contract,interface,integration,migrations,javascript}`. Testes
de JavaScript rodam em Node com DOM simulado, orquestrados por `backend/tests/test_javascript.py`.

**Target Platform**: servidor Linux; interface administrativa server-rendered com HTMX, consumida
em navegador.

**Project Type**: aplicação web Django em camadas por app — `domain/`, `application/`, `models/`,
`api/`, `infrastructure/` — mais o app `interface/`, que renderiza HTML e invoca a camada de
aplicação.

**Performance Goals**: nenhuma meta nova. A prévia é síncrona; o volume atual é de dezenas de
Perfis e Eventos por Edital e o renderizador já compõe o documento inteiro em memória.

**Constraints**: a prévia não pode criar registro publicado nem alterar estado (FR-011); a gramática
de endereçamento de `publicacoes/domain/changes.py` não pode mudar (P-003).

**Scale/Scope**: cinco entregas; quatro etapas novas ou revistas no assistente; duas coleções novas
no snapshot; nenhuma reescrita.

## Constitution Check

*GATE: avaliado contra a Constituição 1.1.1, antes da Fase 0 e reavaliado após a Fase 1.*

| Princípio | Portão | Situação |
|---|---|---|
| I — Linguagem ubíqua | Termos novos existem no domínio e no código com o mesmo nome | `Etapa de Avaliação` e `Seção do Edital` entram como `stages` e `sections` no snapshot e como `EtapaAvaliacao` e `SecaoEdital` no domínio. `Modalidade de Concorrência` e `Regra Normativa` já são termos da Constituição e não são renomeados. **Passa** |
| II — Integridade normativa e temporalidade | Publicado permanece imutável; alteração pós-publicação só por Retificação | Nada muda no ciclo publicado. A prévia é gerada e descartada, sem persistência (FR-011). As coleções novas entram no snapshot e ficam endereçáveis. **Passa** |
| III — Segurança e auditoria | Ato novo é autorizado e auditado | `update_edital_identification` exige permissão e registra evento, como os demais commands. A prévia é leitura autorizada e não gera ato. **Passa** |
| IV — Regras explícitas | Inconsistências classificadas e publicação bloqueada por erro impeditivo | A verificação de publicação da `005` é estendida às coleções novas por declaração em `COLECOES_PUBLICADAS`. **Passa** |
| V — Qualidade e simplicidade | Solução mais simples que preserve os requisitos | Nenhum padrão novo: sem repositório, sem DTO novo, sem serviço novo, sem event sourcing. `replace_draft` permanece. **Passa** |
| VI — Completude de jornada | Cada entrega termina em cenário demonstrável pelo canal do ator | As cinco entregas terminam no navegador; o `SC-009` é o cenário de ponta a ponta com dois atores. **Passa** |

**Restrições e Invariantes do Domínio**: a Constituição admite que "Perfis PODEM possuir Etapas
distintas". Esta feature modela Etapas por Edital, o que **não viola** a permissão — não a exerce.
A decisão e seu custo de reversão estão registrados na `Clarifications` da spec e em FR-023. Nada
está publicado; mover a coleção para dentro do Perfil depois é uma migration e um caminho de
snapshot.

**Reavaliação pós-Fase 1**: sem violações novas. Nenhuma entrada em *Complexity Tracking*.

## Project Structure

### Documentation (this feature)

```text
specs/006-elaboracao-completa-edital/
├── plan.md              # Este arquivo
├── spec.md
├── research.md          # Fase 0 — decisões e alternativas recusadas
├── data-model.md        # Fase 1 — entidades, snapshot e migrations
├── quickstart.md        # Fase 1 — como demonstrar e validar
└── contracts/
    └── elaboracao.md    # Fase 1 — forma canônica das coleções novas e do rascunho
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── editais/
│   ├── domain/
│   │   ├── etapas.py             # NOVO — invariantes da Etapa de Avaliação
│   │   ├── secoes.py             # NOVO — catálogo fixo de Seções e seus tipos
│   │   ├── perfis.py             # faixa do percentual da Regra Normativa
│   │   └── validation.py         # declara stages e sections em COLECOES_PUBLICADAS
│   ├── models/
│   │   ├── etapas.py             # NOVO — EtapaAvaliacao
│   │   ├── secoes.py             # NOVO — SecaoEdital
│   │   └── perfis.py             # inalterado em forma; ganha uso de id na criação
│   ├── application/
│   │   ├── draft.py              # preserva identidades; grava etapas e seções
│   │   └── identificacao.py      # NOVO — update_edital_identification
│   └── api/serializers.py        # payload do rascunho ganha as coleções novas
├── publicacoes/
│   ├── application/
│   │   ├── publish_edital.py     # edital_snapshot ganha stages e sections
│   │   └── retificacoes.py       # recusa conteúdo-base de outra versão canônica
│   ├── domain/colecoes.py        # declara /stages e /sections
│   └── infrastructure/pdf.py     # modo PREVIEW | PUBLISHED; imprime as seções
├── interface/
│   ├── views.py                  # etapas novas do assistente; prévia; identificação editável
│   ├── forms.py                  # lê e preserva modalidades, regras, etapas e seções
│   ├── urls.py                   # rotas da prévia e dos fragmentos novos
│   ├── templates/interface/      # compor_etapas, compor_conteudo, _etapa, botões de ordem
│   └── static/interface/         # mover linha para cima e para baixo
└── shared/canonical.py           # SCHEMA_VERSION 1 -> 2

backend/tests/
├── unit/                         # invariantes de Etapa, Seção e faixa do percentual
├── contract/                     # forma canônica das coleções novas; guarda de versão
└── interface/                    # assistente, prévia, reordenação, ida e volta sem perda
```

**Structure Decision**: mantida a estrutura existente. Nenhum app novo, nenhum diretório novo além
de arquivos de domínio e modelo dentro de `editais/`. A separação por camada já vigente é o que
permite que a interface ganhe etapas sem tocar em persistência e que o snapshot ganhe coleções sem
tocar na gramática de Retificação.

## Abordagem por entrega

A ordem é a da spec. Cada entrega é fechada e demonstrável; nenhuma depende de decisão pendente da
seguinte.

### Entrega 1 — Fluxo sem becos sem saída (US0)

Três correções de exposição e um ato de domínio.

O botão sai do bloco `{% empty %}` de `lista.html` e passa a viver no cabeçalho da listagem, sob o
mesmo `pode_criar` que a view já calcula. O detalhe do Edital publicado passa a listar **o documento
de cada Publicação**, identificado pelo ato que o produziu, apontando para
`/api/v1/public/publicacoes/{id}/documento`, que já existe e é público. Nenhum é rotulado como
vigente: a vigência é da Versão Consolidada, que não tem documento próprio, e uma Retificação pode
ser publicada com vigência futura.

A reordenação exige uma correção no parser, e não só botões. `_indices` recolhe os índices em um
conjunto e os devolve **ordenados numericamente** (`interface/forms.py:20-26`): a posição da linha
no DOM é descartada antes do `enumerate` que produz `order`. Mover a linha na tela, sozinho, não
muda nada.

A ordem passa a ser dado explícito: cada linha carrega um campo oculto `order`, que os botões
atualizam, e `ler_eventos` ordena por ele em vez de derivar da posição. É menor do que renumerar os
nomes dos campos no cliente, não depende de o DOM e o parser concordarem sobre convenção implícita,
e sobrevive a buracos de índice deixados por remoções. **Continua sem endpoint e sem command novo**
— FR-005 —, mas não sem backend: a afirmação anterior estava errada. O `id` de cada Evento viaja em
campo oculto e é preservado por `replace_draft`, o que satisfaz a exigência de identidade.

`update_edital_identification` é o único command novo desta entrega: exige status
`EM_ELABORACAO`, `expected_revision`, permissão e registro de auditoria, como os commands vizinhos
em `processos/application/commands.py`. Com ele, `DESTINO_DA_PENDENCIA` passa a marcar `title` e
`description` como corrigíveis e `MOTIVO_NAO_CORRIGIVEL` deixa de ser alcançável.

### Entrega 2 — Prévia do documento (US1)

`render_edital_pdf` ganha um parâmetro de modo. Em `PREVIEW`, a seção de integridade não é composta
e o rodapé de cada página traz a marca de prévia em vez do hash; em `PUBLISHED`, o comportamento é o
de hoje, byte a byte. A view da prévia chama `edital_snapshot(edital)` e devolve os bytes como
resposta, sem persistir nada.

A ação aparece na etapa de Revisão e no detalhe do Edital enquanto submetido ou homologado. A
origem é única: depois da submissão o rascunho não é editável, e a publicação já recusa divergência
entre rascunho e revisão homologada.

### Entrega 3 — Etapas de Avaliação (US2)

`EtapaAvaliacao` nasce no padrão de `EventoCronograma`: `id` UUID preservado na gravação, `order`
com unicidade por Edital, e ordenação declarada no modelo. A etapa do assistente reusa os fragmentos
HTMX e o mecanismo de índice de linha que os Perfis e Eventos já usam.

O snapshot ganha `stages` **e `sections`**; `colecoes.py` ganha as duas formas; `validation.py`
ganha `ETAPA_PUBLICADA` e `SECAO_PUBLICADA`. Endereçamento, proveniência e consolidação passam a
cobri-las sem código novo — mas a **verificação de forma não basta**: `Campo` confere um campo por
vez, e por isso entram aqui as duas verificações direcionadas de D-011, a topologia das seções
contra o catálogo e a existência do Evento referenciado por cada Etapa.

### Entrega 4 — Modalidades de reserva (US3)

É a entrega de fechar a ida e volta, e ela tem quatro pontas. `ModalidadeConcorrencia` **e
`RegraNormativa`** passam a ser criadas com os `id` preservados; `perfis_persistidos` passa a
serializar a modalidade inteira, regra e identificador dela incluídos;
`_reject_identifiers_of_other_editais` passa a cobrir as duas; e os serializers passam a **aceitar**
esses identificadores — sem isso o `id` nunca chega ao command pela API, e a recusa de identificador
alheio não teria o que recusar.

O formulário substitui a caixa de texto livre por linhas com campos próprios: código, nome,
percentual, fundamento e **versão do fundamento**, que é obrigatória no command desde a `001` e sem a
qual nenhuma regra nova seria gravável.

A faixa do percentual entra em `editais/domain/perfis.py`, no caminho que a interface e a API
atravessam igualmente — não no serializer.

### Entrega 5 — Edição do conteúdo textual (US4)

A **forma** das seções já entrou na Entrega 3 (ver *Encadeamento*). Esta entrega acrescenta o que
falta para o usuário: a etapa de conteúdo no assistente, o modelo `SecaoEdital` que persiste o texto
editado e a composição das seções no documento a partir do catálogo.

O catálogo é declarado em `editais/domain/secoes.py`: identidade, chave, título, ordem e tipo. Seção
gerada nomeia a coleção que a origina e **não tem campo de conteúdo**; seção textual tem conteúdo,
com texto inicial institucional vindo do catálogo. `SecaoEdital` persiste apenas o texto das
textuais que foram editadas — ausência de linha significa "texto padrão do catálogo".

### Encadeamento

**A forma canônica da versão 2 entra inteira no primeiro PR que a produz.** `stages` e `sections`
nascem juntas no snapshot, no esquema OpenAPI e nos três registros declarativos, na Entrega 3 —
junto com a guarda de versão canônica de FR-047. Na Entrega 3 as seções já existem no conteúdo
publicado, todas com o texto padrão do catálogo, porque nada ainda as edita.

Isso não é preciosismo. Subir para 2 na Entrega 3 e acrescentar `sections` na Entrega 5 produziria
snapshots de versão 2 com e sem a propriedade, e a versão canônica deixaria de identificar uma
forma. Como as entregas são integradas verticalmente e cada uma vai a produção do ponto de vista da
demonstração, a divergência seria real, não hipotética. O esquema 2 é o desta feature inteira
(FR-045); a interface de edição pode chegar depois, o contrato não.

## Complexity Tracking

Nenhuma violação constitucional a justificar. Nenhum padrão arquitetural novo introduzido.
