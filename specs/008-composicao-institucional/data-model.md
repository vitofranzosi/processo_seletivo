# Fase 1 — Modelo de dados

**Feature**: 008 — Composição Institucional do Edital | **Data**: 2026-08-30

**Esta feature não tem modelo de dados.** Nenhuma entidade nasce, nenhuma coluna é acrescentada,
nenhuma migration é escrita, nenhum campo é removido, nenhum estado ou transição muda, e a forma
canônica do snapshot permanece na versão 3, byte a byte, com o mesmo cálculo de hash.

O que este documento descreve são as **estruturas de composição**: valores internos do compositor,
que existem apenas enquanto um documento é montado e nunca são persistidos, serializados,
endereçados por Retificação nem expostos por API.

---

## 1. O que **não** muda

| Artefato | Situação |
|---|---|
| `SCHEMA_VERSION` | permanece `3` |
| Raiz do snapshot | mesmas chaves, mesma ordem canônica, mesmo hash |
| `PerfilVaga`, `Cronograma`, `EventoCronograma`, `EtapaAvaliacao`, `Modalidade` | intocados |
| Catálogo de seções (`editais/domain/secoes.py`) | intocado — inclusive a ordem |
| Catálogo de autoridades (`publicacoes/domain/autoridades.py`) | intocado — a `008` **lê** o que a Publicação registrou, não o catálogo |
| `Publicacao`, `DocumentoPublicado`, `VersaoConsolidada`, `Retificacao` | intocados, append-only como já são |
| Gramática de `publicacoes/domain/changes.py` | intocada |
| Endpoints administrativos e públicos | intocados: mesmo caminho, mesmo tipo de conteúdo |
| Migrations | **nenhuma** |

*O bloco de autoridade que a `008` imprime não é dado novo: `Publicacao.signatory_name` e
`Publicacao.signatory_role` já existem, já são preenchidos nos dois fluxos de publicação e já são
imutáveis. A feature os materializa; não os cria.*

---

## 2. Estruturas de composição

Vivem em `publicacoes/infrastructure/pdf.py`. Nenhuma atravessa a fronteira do módulo, exceto
`AutoridadeSignataria`, que é o contexto do ato e é construída pelos dois chamadores.

### 2.1 `AutoridadeSignataria` — o contexto do ato

| Campo | Tipo | Presença | Origem |
|---|---|---|---|
| `nome` | string | sempre | `Publicacao.signatory_name`, via o `signatory` que o fluxo já resolveu |
| `cargo` | string | sempre | `Publicacao.signatory_role`, idem |

Valor congelado, sem identificador. **`signatory_id` não entra**: ele é dado de vínculo para a
auditoria, e a `007` já decidiu que nunca é digitado, exibido nem impresso (FR-044 da `007`).

**Regra de presença, validada pelo modo e não pelo chamador** (FR-036):

| Modo | `AutoridadeSignataria` | Compositor |
|---|---|---|
| publicado | obrigatória | recusa compor se ausente |
| prévia | proibida | recusa compor se presente |

*Recusar nos dois sentidos, e não apenas ignorar no modo prévia, é o que impede os dois erros: um
ato publicado sem quem o praticou, e uma prévia que parece publicada.*

### 2.2 Item de composição — união marcada

O item deixa de ser sempre texto (D-002).

| Variante | Campos | Materializa |
|---|---|---|
| `Texto` | conteúdo, fonte, corpo, recuo, espaço antes, alinhamento | uma linha de texto |
| `Traço` | geometria relativa ao bloco, resolvida após a paginação | um fio ou um contorno |

`alinhamento` é novo e assume três valores — à esquerda, centralizado, à direita —, todos
dependentes da métrica de D-001. À direita serve à coluna de percentual; centralizado, ao cabeçalho
institucional.

### 2.3 Bloco — o que a paginação passa a enxergar

| Atributo | Significado |
|---|---|
| nível | `Perfil` → `sub-bloco` → `unidade interna`, na cascata de FR-022 |
| moldura | se o bloco pede contorno (quadro de Perfil) ou não |
| coesão | se o bloco não pode ser iniciado sem que caiba, e em que nível ele pode ser aberto |

Um bloco **não** é entidade nem tem identidade: é uma marca de abertura e fechamento na sequência de
itens, e existe apenas durante a paginação.

### 2.4 Tabela — não é estrutura nova

Uma tabela é um bloco cujas unidades internas são linhas, e cuja primeira unidade é o cabeçalho com
a marca de repetição (FR-027). As larguras de coluna são calculadas por D-007 e não são
persistidas.

---

## 3. Regras de validação

Todas incidem sobre a composição, e nenhuma sobre dado persistido.

| Regra | Origem | Efeito quando violada |
|---|---|---|
| Publicado exige `AutoridadeSignataria` | FR-036 | composição recusada |
| Prévia proíbe `AutoridadeSignataria` | FR-036 | composição recusada |
| Modo desconhecido | já existente | composição recusada |
| Numeração atribuída após a filtragem das seções | FR-012 | numeração com lacuna — coberta por teste |
| Nenhuma linha ultrapassa a margem | FR-002, FR-030 | texto fora da área útil — coberta por teste |
| Cascata de quebra sempre termina em alternativa exequível | FR-022 | composição impossível — coberta por teste com sub-bloco maior que uma página |

---

## 4. Fixtures versionadas

| Arquivo | Situação | Papel |
|---|---|---|
| `tests/contract/fixtures/snapshot_publicado.json` | existente, intocado | conteúdo de referência |
| `tests/contract/fixtures/assinatura_publicada.json` | **novo** | autoridade fixa da fixture, sem a qual o documento publicado não compõe mais (D-009) |
| `tests/contract/fixtures/documento_publicado_v1.pdf` | existente, **regenerado por entrega** | bytes de referência (FR-045) |

*O arquivo novo é fixture de teste, não dado de produção: nome e cargo fictícios, versionados para
que a comparação de bytes seja reproduzível por quem não escreveu a feature.*
