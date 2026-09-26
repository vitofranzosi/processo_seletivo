# Data Model — Recorte transversal do documento exigido

Fase 1 do plano. O delta sobre o que existe: **um campo** no Documento Exigido, **uma tabela** na
inscrição, **um degrau** na versão canônica. Nada muda na Modalidade nem no Perfil.

---

## 1. Documento Exigido — o campo `modalityCode`

### No conteúdo publicado (`documentRequirements[]`, versão canônica 17)

| Campo | Tipo | Nulo | Significado |
|---|---|---|---|
| `modalityCode` | texto | sim | O código da Modalidade, em todos os Perfis que a têm. `null` = não recorta por código |

Os demais campos não mudam. O conteúdo publicado na versão 16 ou anterior é lido com
`modalityCode: null` pela elevação (`research.md`, R-002), e só dentro do fluxo de Retificação.

### No rascunho relacional (`editais.DocumentoExigido`)

| Coluna | Tipo | Nulo |
|---|---|---|
| `modalidade_codigo` | `varchar(100)` | sim |

Restrição nova, `ck_documento_recorte_exclusivo`: `modalidade_codigo IS NULL OR (perfil_id IS NULL
AND modalidade_id IS NULL)`. É o `D-006` no banco. A recusa da aplicação vem antes, com mensagem
ancorada no campo, e a restrição é a segunda barreira.

### As cinco formas do recorte

Lidas por presença de campo, sem linguagem de condição:

| Forma | `profileId` | `modalityId` | `modalityCode` | Publicável |
|---|---|---|---|---|
| `TODOS` | — | — | — | sim |
| `PERFIL` | ✓ | — | — | sim |
| `PERFIL_E_MODALIDADE` | ✓ | ✓ (do Perfil) | — | sim |
| `MODALIDADE_EM_TODOS_OS_PERFIS` | — | — | ✓ | sim, sob `R-007` |
| `TODOS_COM_MODALIDADE_DE_UM_PERFIL` | — | ✓ | — | só se nenhum outro Perfil tem Modalidade de mesma denominação (#161) |

`modalityCode` junto de `profileId` ou `modalityId` não é forma: é recusa.

### Regras

| Regra | Onde vale | Requisito |
|---|---|---|
| exclusivo com Perfil e Modalidade exata | gravação, publicação, banco | `FR-702` |
| algum Perfil tem o código | gravação, publicação, Retificação | `FR-703`, `FR-724` |
| nenhum Perfil declara ampla a Modalidade do código | gravação, publicação, Retificação | `FR-704` |
| uma denominação só por código referido | publicação, Retificação | `FR-706`, `FR-707`, `D-001`, `D-005` |

### Mutabilidade

`("documentRequirements", "modalityCode")`: **retificável** (`D-002`). O código que ele aponta
(`competitionModalities.code`) já é estrutural.

---

## 2. A lista exigida — `inscricoes.ItemDaListaExigida` (nova, append-only)

Uma linha por Documento Exigido da versão aceita, gravada no ato do envio.

| Campo | Tipo | Nulo | Nota |
|---|---|---|---|
| `id` | UUID | não | PK |
| `inscricao` | FK `Inscricao`, `PROTECT` | não | `related_name="lista_exigida"` |
| `versao` | FK `publicacoes.VersaoConsolidada`, `PROTECT` | não | igual a `inscricao.versao_aceita` (gatilho) |
| `requisito_id` | UUID | não | o `id` publicado do Documento Exigido |
| `chave` | `varchar(100)` | não | o `key` publicado, que não se retifica |
| `situacao` | `varchar(16)` | não | `OBRIGATORIO`, `FACULTATIVO` ou `NAO_SE_APLICA` |
| `forma_do_recorte` | `varchar(40)` | não | uma das cinco formas da §1 |
| `perfil_id` | UUID | sim | parâmetro do recorte, quando houver |
| `modalidade_id` | UUID | sim | idem |
| `modalidade_codigo` | `varchar(100)` | sim | idem |
| `divergente_do_publicado` | bool | não | `D-007` |
| `gravada_em` | timestamptz | não | igual a `inscricao.submitted_at` (gatilho) |

### Restrições

- `uq_item_da_lista_por_requisito`: `UNIQUE (inscricao, requisito_id)`.
- `ck_item_da_lista_situacao`: `situacao` no conjunto.
- `ck_item_da_lista_forma`: `forma_do_recorte` no conjunto, e os parâmetros coerentes com a forma
  (`TODOS` sem nenhum, `PERFIL` só com `perfil_id`, e assim por diante).
- `ck_item_da_lista_divergencia`: `divergente_do_publicado` só com a forma
  `TODOS_COM_MODALIDADE_DE_UM_PERFIL`.

### As duas camadas, mais a de modelo

| Camada | O quê |
|---|---|
| Privilégio | entrada em `TABELAS_APPEND_ONLY`; o runtime não tem `UPDATE` nem `DELETE` |
| Gatilho | `item_da_lista_exigida_append_only`: `BEFORE UPDATE OR DELETE` recusa |
| Gatilho | `item_da_lista_exigida_coerente`: `BEFORE INSERT` exige inscrição `SUBMETIDA`, `versao_id = versao_aceita_id` e `gravada_em = submitted_at` |
| Modelo | `save` recusa fora da adição; `delete` recusa, com "append-only" na mensagem |

### O que ela não guarda

Nome, instrução e obrigatoriedade **textual** do documento. A versão aceita é imutável e está na
linha, e ler o nome dela não é recalcular recorte (`research.md`, R-005). A lista não guarda arquivo
nem resumo: os arquivos continuam em `DocumentoSubmetido`.

### Ciclo de vida

Não tem estados. Nasce inteira no envio, na mesma transação do ato, e não muda. A inscrição em
rascunho não tem lista. A inscrição enviada antes desta feature também não, e **não ganha** (`D-004`).

---

## 3. Os valores de leitura (sem persistência)

### `Veredito` (domínio, `editais/domain/documentos.py`)

O que `aplicabilidade(conteudo, *, profile_id, modality_id)` devolve, um por Documento Exigido:

| Campo | Conteúdo |
|---|---|
| `requisito` | o documento, como está no conteúdo |
| `situacao` | `OBRIGATORIO`, `FACULTATIVO`, `NAO_SE_APLICA` |
| `recorte` | `Recorte(forma, perfil_id, modalidade_id, modalidade_codigo)` |
| `divergente_do_publicado` | bool |

É a mesma forma que a linha gravada, e é o que a gravação escreve: um veredito, uma linha.

### `ListaExigida` (aplicação, `inscricoes/application/lista_exigida.py`)

| Campo | Conteúdo |
|---|---|
| `itens` | os vereditos, lidos das linhas gravadas ou reconstruídos |
| `reconstruida` | `True` quando a inscrição não tem linhas (`FR-726`, `UX-083`) |

### A razão legível (`UX-081`)

Composta a partir do recorte e dos nomes da versão aceita:

| Forma | Frase |
|---|---|
| `TODOS` | pedido de todos os candidatos |
| `PERFIL` | pedido de quem concorre ao Perfil {Perfil} |
| `PERFIL_E_MODALIDADE` | pedido de quem concorre ao Perfil {Perfil} em {Modalidade} |
| `MODALIDADE_EM_TODOS_OS_PERFIS` | pedido de quem concorre em {denominação}, em todos os Perfis |
| `TODOS_COM_MODALIDADE_DE_UM_PERFIL` | pedido de quem concorre ao Perfil {Perfil} em {Modalidade} |

No "não se aplica", a frase vem precedida de *"Não se aplica:"*, e diz a quem o documento era
pedido. Com `divergente_do_publicado`, acrescenta-se *"— o Edital publicado o exigia de todo
candidato em {denominação}"*.

---

## 4. A versão canônica

| | Antes | Depois |
|---|---|---|
| `SCHEMA_VERSION` | 16 | **17** |
| `DEGRAUS_DE_DOCUMENTO` | `9: {"attachmentId": None}` | `+ 17: {"modalityCode": None}` |
| `DOCUMENTO_EXIGIDO_PUBLICADO` | 9 campos | **10** |

---

## 5. Migrations

| App | Migration | Conteúdo |
|---|---|---|
| `editais` | `0022_documento_modalidade_codigo` | a coluna e `ck_documento_recorte_exclusivo` |
| `inscricoes` | `0005_item_da_lista_exigida` | a tabela, as restrições e os dois gatilhos, com o caminho reverso e a guarda de vendor |

Nenhuma migration apaga dado. Nenhuma preenche a lista de inscrição antiga.
