# Fase 1 — Modelo de dados

**Feature**: 007 — Edital Institucional | **Data**: 2026-08-30

Esta feature **não cria entidade**. Ela acrescenta três colunas a uma entidade existente, três
entradas a um catálogo declarado, um catálogo declarado novo e dois escalares à raiz do snapshot.

---

## 1. `PerfilVaga` — três colunas novas

`backend/processo_seletivo/editais/models/perfis.py`

| Campo | Tipo | Nulo | Padrão | Racional |
|---|---|---|---|---|
| `duties` | `TextField(blank=True)` | não | `""` | Atribuições são vários parágrafos, e o documento os preserva pelo caminho que a `006.1` abriu para as seções textuais. `TextField` porque não há limite sensato a impor |
| `workload` | `CharField(max_length=255, blank=True)` | não | `""` | "20 horas semanais", "40h com dedicação exclusiva". É uma frase, não uma quantidade |
| `compensation` | `CharField(max_length=255, blank=True)` | não | `""` | "R$ 4.200,00 mensais, acrescidos de auxílio-alimentação". FR-013 proíbe objeto de moeda |

**Todos são `blank=True` e nunca `null`.** É a convenção já vigente na entidade: `description` é
`TextField(blank=True)` e `locality` é `CharField(blank=True)`; o único campo opcional com `null` é
`reserve_limit`, que é numérico. Um texto ausente é a string vazia — introduzir `null` para texto
criaria duas formas de dizer "não informado" na mesma linha.

**Nenhuma constraint nova.** Os três são descritivos e opcionais (FR-012); não há invariante a
proteger. As duas constraints existentes de `PerfilVaga` — unicidade de `(edital, code)` e a
compatibilidade de `reserve_limit` com `reserve_type` — permanecem intocadas.

**Migration**: `editais/migrations/0005_perfil_institucional.py`. Três `AddField`, sem `RunPython`,
sem dado a converter. É a migration direta que a precondição de implantação autoriza.

---

## 2. Catálogo de Seções — três entradas novas

`backend/processo_seletivo/editais/domain/secoes.py` — declarado em código, **não persistido**.

Ordem final do catálogo, com as novas em destaque:

| `order` | `key` | Título | Tipo | Origem |
|---|---|---|---|---|
| 1 | **`apresentacao`** | **Apresentação** | **TEXTUAL** | — |
| 2 | `disposicoes-preliminares` | Disposições Preliminares | TEXTUAL | — |
| 3 | **`requisitos-gerais`** | **Requisitos Gerais de Participação** | **TEXTUAL** | — |
| 4 | `inscricao` | Da Inscrição | TEXTUAL | — |
| 5 | `perfis` | Perfis de Vaga | GERADA | `profiles` |
| 6 | `etapas` | Etapas de Avaliação | GERADA | `stages` |
| 7 | **`classificacao`** | **Critérios de Classificação** | **TEXTUAL** | — |
| 8 | `cronograma` | Cronograma | GERADA | `schedule` |
| 9 | `recursos` | Dos Recursos | TEXTUAL | — |
| 10 | `disposicoes-finais` | Disposições Finais | TEXTUAL | — |

As posições cumprem FR-008: a apresentação **antes** dos Perfis, os requisitos gerais **antes** da
inscrição, os critérios de classificação **depois** das Etapas de Avaliação.

**Identidade não muda com a ordem.** `identidade(edital_id, key) = uuid5(NAMESPACE, f"{edital_id}:{key}")`
deriva da chave. Renumerar `order` não move identidade nem quebra endereçamento (D-007).

**Cada nova traz `default_text`** — redação institucional inicial genérica, editável antes da
publicação, no mesmo registro das sete existentes. Adequá-la à redação do Cefor é trabalho
editorial, não desta feature.

**`SecaoEdital` não muda.** Continua persistindo apenas o texto das textuais **editadas**; ausência
de linha significa "texto padrão do catálogo". É esse fato que dá o sinal de FR-040.

---

## 3. Catálogo de Autoridades Signatárias — novo, declarado

`backend/processo_seletivo/publicacoes/domain/autoridades.py` — **não é entidade, não é tabela.**

```text
Autoridade(chave: str, identificador: UUID, nome: str, cargo: str)
CATALOGO: tuple[Autoridade, ...]
POR_CHAVE: dict[str, Autoridade]
```

**Sobre o `identificador`.** Ele é necessário e não contradiz FR-044: `Publicacao` exige
`signatory_id` (`UUIDField`, não nulo) além de `signatory_name` e `signatory_role`
(`publicacoes/models.py:63-65`), e é por ele que a auditoria responde quem assinou. O catálogo não
o **introduz** — ele já era exigido, e era digitado à mão, que foi o achado 12. O que muda é a
origem. Ele **nunca é digitado, exibido ao operador nem impresso no documento**: é dado de vínculo,
não de leitura.

| Regra | Onde |
|---|---|
| Contém nome, cargo e identificador institucional — nada além | FR-044 |
| O identificador não é digitado, exibido nem impresso | FR-044 |
| Não contém CPF, matrícula, endereço, telefone, e-mail nem foto | FR-044 |
| Incluir ou retirar é alteração do catálogo, não operação de usuário | FR-039 |
| Autoridade retirada não é oferecida em novos atos | FR-039 |
| Autoridade retirada **não** afeta Publicação já praticada | FR-039, FR-046 |

O último item não exige trabalho: a `Publicacao` **já persiste** nome, cargo e identificador da
autoridade no ato, e o ato é imutável. O catálogo é a origem da escolha, não a fonte de verdade do
que foi assinado.

A tela de confirmação (`confirmar.html:50-53`) substitui o campo de texto que hoje pede um UUID por
uma escolha; nome e cargo deixam de ser redigitados a cada publicação porque vêm da entrada
escolhida.

---

## 4. Forma canônica v3 do snapshot

`SCHEMA_VERSION`: **2 → 3**, uma única vez (FR-017).

### Raiz — dois escalares novos

```text
{
  "schemaVersion": 3,
  "editalId":      "<uuid>",
  "processoId":    "<uuid>",
  "processoCode":  "<string>",     ← NOVO
  "processoTitle": "<string>",     ← NOVO
  "number":        "<string>",     ← string, não inteiro: CharField(50), preserva "02"
  "year":          <int>,
  "title":         "<string>",
  "description":   "<string>",
  "profiles":      [...],
  "schedule":      [...],
  "stages":        [...],
  "sections":      [...]
}
```

`processoCode` vem de `ProcessoSeletivo.institutional_code` e `processoTitle` de
`ProcessoSeletivo.title`. Ambos são strings sempre presentes. O dado já está carregado por
`select_related("processo")`; não há consulta a mais.

`processoId` e `editalId` **permanecem** — FR-004 rege o que o documento imprime, não o que o
conteúdo carrega.

### `profiles[*]` — três campos novos

```text
{
  "id": "<uuid>", "code": "...", "name": "...", "description": "...",
  "requirements": [...], "immediateVacancies": <int>,
  "reserveType": "...", "reserveLimit": <int|null>, "locality": "...",
  "duties":       "<string>",   ← NOVO — "" quando ausente
  "workload":     "<string>",   ← NOVO — "" quando ausente
  "compensation": "<string>",   ← NOVO — "" quando ausente
  "classificationInformation": {...}, "callInformation": {...},
  "competitionModalities": [...]
}
```

**String sempre presente, `""` quando ausente — nunca `null`, nunca chave omitida** (FR-014). É a
convenção do próprio objeto: `description` e `locality` são strings; `reserveLimit` é `null` por ser
numérico.

### `sections` — dez entradas em vez de sete

A forma de cada item não muda. Muda a quantidade e o `order`, conforme a tabela da seção 2.

### Registros declarativos

| Registro | Muda? |
|---|---|
| `COLECOES_COM_CHAVE` | **Não.** Nenhuma coleção-raiz nova (FR-020) |
| `COLECOES_ATOMICAS` | **Não** |
| `LISTAS_DE_CONTROLE` | **Não** |
| `COLECOES_PUBLICADAS` | **Sim** — a forma de `profiles` ganha os três campos textuais |
| **`CAMPOS_DE_IDENTIDADE`** (novo) | `editalId`, `processoId`, `processoCode`, `processoTitle`, `schemaVersion` — recusados pela Retificação, no mesmo ponto que já recusa o controle interno (FR-004, D-003.1) |

O teste de anti-deriva que a `006` criou continua valendo sem alteração: ele exige que toda
coleção-raiz de entidades do snapshot esteja declarada, e nenhuma nasce aqui.

---

## 5. Transições de estado

**Nenhuma.** Esta feature não altera a máquina de estados do Edital, do Processo, da Publicação nem
da Retificação. FR-028 **lê** o estado para dizer quem age a seguir; não o move.

O único "estado" novo é de apresentação: o progresso do assistente passa de dois valores para três —
`pendente`, `pronta para revisar`, `concluida`. Vive no cálculo da view (`views.py:314-338`), não em
persistência.

---

## 6. Impacto sobre dados existentes

| Dado | Efeito |
|---|---|
| Editais **em elaboração** | Ganham as três seções novas com texto padrão na próxima leitura. Nenhuma perda |
| Perfis existentes | Ganham três colunas vazias. Nenhuma perda |
| Editais **publicados** na versão 2 | Tornam-se irretificáveis, por topologia de seções **e** por versão canônica. É o comportamento correto, e é o que a precondição de implantação admite |
| Seed e fixtures | Regenerados |
| Fixture de bytes do documento | Regenerada em cada entrega que altera a composição — a 1 e a 2 (FR-006) |

Nenhum caminho de conversão é construído (FR-019).
