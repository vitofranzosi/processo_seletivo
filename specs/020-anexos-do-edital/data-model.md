# Fase 1 — Modelo de dados: Anexos do Edital

Duas tabelas novas, um campo novo numa tabela existente, uma coleção nova no conteúdo canônico e um
campo novo numa coleção existente. Nada além disso.

---

## Persistência

### `AnexoEdital` — `editais/models/anexos.py`

O anexo em elaboração. Muda enquanto o Edital está em elaboração; depois de publicado, o que vale é
o conteúdo canônico, e as mudanças passam por Retificação.

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID, PK, `default=uuid4` | Identidade normativa estável (FR-002). Segue `PerfilVaga`, e **não** o `uuid5` de `SecaoEdital` — a seção deriva de catálogo declarado, o anexo é criado pelo autor |
| `edital` | FK → `Edital`, `PROTECT`, `related_name="anexos"` | |
| `rotulo` | `CharField(255)` | Texto único, escrito inteiro pelo autor (FR-005). Pode nascer vazio e é impeditivo na publicação |
| `order` | `PositiveIntegerField` | Ordem editorial, campo próprio (FR-007). Único por Edital, como em `DocumentoExigido` |
| `artefato` | FK → `ArtefatoAnexo`, `PROTECT` | Obrigatório: não existe Anexo sem artefato (FR-015a) |

`Meta`: `ordering = ["order", "id"]`; `UniqueConstraint(edital, order)`.

### `ArtefatoAnexo` — `editais/models/anexos.py`

Os bytes. Sobrescrevível enquanto nenhuma versão o publicou; imutável depois disso.

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID, PK | É o **endereço público** do artefato (R-003) |
| `bytes` | `BinaryField` | R-001 |
| `content_type` | `CharField(100)`, default `application/pdf` | |
| `tamanho` | `PositiveBigIntegerField` | |
| `document_hash` | `CharField(64)`, `db_index=True` | Integridade, **nunca** unicidade (FR-011) — a mesma nota que `DocumentoPublicado.document_hash` carrega |
| `nome_original` | `CharField(255)` | Só exibição; não decide identidade nem endereço (FR-014) |
| `enviado_por` / `enviado_em` | `CharField(255)` / `DateTimeField` | Autoria e instante (FR-012) |
| `congelado_em` | `DateTimeField`, nulo | Nulo = rascunho, substituível e apagável. Não nulo = publicado, imutável **e público** (R-002) |

**Trigger** (`editais/migrations/0013`): `BEFORE UPDATE OR DELETE ... FOR EACH ROW WHEN (OLD.congelado_em IS NOT NULL)`
levanta exceção. Molde: `publicacoes/migrations/0007_imutabilidade_do_historico.py:20-58`. A tabela
**não** entra em `TABELAS_APPEND_ONLY`, pela mesma razão que `Retificacao` não entra.

### `DocumentoExigido` — campo novo

| Campo | Tipo | Regra |
|---|---|---|
| `anexo` | FK → `AnexoEdital`, nulo, `SET_NULL`, `related_name="requisitos"` | O modelo que o Edital fornece (FR-020). Anulável já é `N:1` por construção; `SET_NULL` é a forma da D-009 — remover o Anexo não remove o requisito, e o vínculo não sobrevive ao alvo |

---

## Conteúdo canônico (`schemaVersion: 9`)

### Coleção nova, na raiz

```json
"attachments": [
  {
    "id": "8f1e…",              // identidade normativa estável
    "label": "ANEXO VI — AUTODECLARAÇÃO ÉTNICO-RACIAL",
    "order": 6,
    "artifactId": "b27c…",      // endereço do artefato; resolve os bytes
    "artifactHash": "9ad4…"     // integridade da cadeia (FR-053)
  }
]
```

Ordenada por `(order, id)`, deterministicamente, como as demais (`publish_edital.py:128-130`).
`artifactId` e `artifactHash` andam juntos: um endereça, o outro prova.

### Campo novo em coleção existente

```json
"documentRequirements": [
  { "…": "…", "attachmentId": "8f1e…" }   // ou null
]
```

Aponta a **identidade do Anexo**, nunca o artefato: o vínculo é com o anexo, e o artefato é o que
aquela versão diz que ele é.

### Declarações que a coleção obriga

| Onde | O quê |
|---|---|
| `publicacoes/domain/colecoes.py:18` | `"/attachments"` em `COLECOES_COM_CHAVE` — sem isso, irretificável |
| `editais/domain/validation.py:187` | `("attachments", ANEXO_PUBLICADO)` em `COLECOES_PUBLICADAS`, com os `Campo` de forma |
| `publicacoes/domain/elevacao.py` | degrau 9: `DEGRAUS_DA_RAIZ` ganha `attachments: []`; tabela nova para o nível do `documentRequirement`, com `attachmentId: null` |
| `specs/001-…/contracts/openapi.yaml` | `AnexoPublicado` em `components.schemas` |
| `tests/contract/test_forma_publicada.py:76` | entrada em `ESQUEMA_DA_COLECAO` |
| `interface/revisao.py:115` | `attachments` em `COLECOES` |
| `interface/retificacao.py` | `CAMPOS_ANEXO`, `NOVO_ANEXO`, `_anexo_completo`, grupo `removivel=True` |
| `publicacoes/infrastructure/pdf.py:1654` | `attachments` em `_CORPO_GERADO` |
| `editais/domain/secoes.py` | `Secao(type=GERADA, source="attachments")` |

---

## Regras de validação (publicação e Retificação)

| Código | Severidade | Quando |
|---|---|---|
| `attachment_label_required` | impeditivo | Anexo sem rótulo |
| `attachment_artifact_missing` | impeditivo | Artefato indisponível ou hash divergente do registrado (FR-026) |
| `attachment_reference_dangling` | impeditivo | `attachmentId` aponta anexo que não existe naquela versão (FR-023) |
| `attachment_duplicate_label` | aviso | Dois anexos com o mesmo rótulo — rótulo não é identidade, e o autor pode ter razão |

A unicidade de `id` dentro da coleção já é verificada por `duplicate_keys`
(`publicacoes/domain/conflicts.py:86-108`), sem regra nova.

---

## Ciclo de vida do artefato

```text
                      upload no rascunho          publicação da versão
                              │                            │
   (não existe) ──────────────▶ congelado_em = NULL ────────▶ congelado_em = agora
                              │  substituível              │  imutável (trigger)
                              │  apagável                  │  público
                              │                            │
                    troca ────┘                     nenhuma transição sai daqui
```

Retificação cancelada deixa o artefato em `congelado_em = NULL` — e é por isso que ele pode ser
apagado. Artefato congelado nunca volta.
