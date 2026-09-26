# Contrato — o recorte transversal

**Feature**: `044-recorte-transversal-documental` · **Data**: 2026-09-25

> **O que é público aqui:** um campo no conteúdo publicado e na API de rascunho, cinco códigos de
> achado da publicação, e as grafias que a composição, a Retificação, o portal e o documento
> publicado mostram. Nenhum endpoint novo.

---

## 1. O campo

### Conteúdo publicado — `DocumentoExigidoPublicado`

```yaml
modalityCode: { type: [string, 'null'] }
```

- **Obrigatório no esquema, como todo campo do conteúdo publicado.** `required` o inclui:
  `tests/contract/test_forma_publicada.py` exige que não haja campo opcional no conteúdo publicado, e
  o `attachmentId` do degrau 9 entrou do mesmo jeito. Obrigatório quer dizer presente, com `null`
  quando não recorta.
- **O literal antigo.** A consulta pública serve o conteúdo **literal** de cada versão, e as versões
  publicadas antes da versão canônica 17 não têm o campo, como já não têm `attachmentId` as de antes
  da 9. Quem lê trata ausente e `null` do mesmo modo: não recorta por código.
- `specs/001-processo-seletivo-editais/contracts/openapi.yaml` ganha a propriedade, e a descrição do
  esquema passa de "quatro combinações" para as cinco formas.

### API de rascunho — `DocumentRequirementSerializer`

```text
modalityCode   texto, até 100, opcional, anulável
```

Recusas, todas `400` com `invalid_document_requirements` e `campo="modalityCode"`:

| Situação | Mensagem (essência) |
|---|---|
| com `profileId` ou `modalityId` | o documento recorta pela modalidade em todos os Perfis **ou** por Perfil; não pelos dois |
| código que nenhum Perfil tem | nenhum Perfil deste Edital tem modalidade de código "X" |
| código declarado ampla em algum Perfil | "X" é a ampla concorrência no Perfil "C1", e a ampla não recorta documento |

---

## 2. A aplicabilidade

Um documento com `modalityCode = X` **se aplica** a uma inscrição se, e somente se, a Modalidade que
ela escolheu, lida no **Perfil dela**, tem código `X`. Sem modalidade escolhida: não se aplica.

Essa regra é a única. O cartão público, o rascunho, o bloqueio do envio, a gravação da lista e a
reconstrução a leem da mesma função (`FR-705`).

---

## 3. Os achados da publicação e da Retificação

Todos com severidade **IMPEDE**. O caminho aponta o documento, salvo onde dito.

| Código | Quando | Destino na Revisão |
|---|---|---|
| `document_requirement_scope_conflict` | `modalityCode` junto de `profileId` ou `modalityId` | Documentos |
| `document_requirement_modality_code_unknown` | nenhum Perfil tem o código, inclusive depois de uma Retificação que o removeu de todos | Documentos |
| `document_requirement_modality_code_general` | algum Perfil declara ampla a Modalidade do código | Documentos |
| `modality_code_name_divergent` | o código, referido por algum documento, tem mais de uma denominação entre os Perfis. **Um achado por código.** A mensagem nomeia cada denominação e os Perfis de cada uma | **Perfis** |
| `document_requirement_modality_scope_ambiguous` | inalterado (#161), com a mensagem nova (§4) | Documentos |

A comparação de denominações apara as pontas, e mais nada (`D-005`). Percentual, fundamento e
descrição não entram (`FR-707`).

---

## 4. A mensagem da #161, com a terceira saída

> O Documento Exigido '{nome}' vale para todos os Perfis, mas está restrito à modalidade
> '{denominação}' do Perfil '{perfil}'. O Edital publicado o exigiria de todo candidato em
> '{denominação}', e a inscrição o pediria só no Perfil '{perfil}'. Declare o Perfil '{perfil}' no
> documento, ou use a modalidade '{denominação}' ({código}) em todos os Perfis — ou, para exigi-lo
> em Perfis escolhidos, repita-o com a modalidade de cada um.

A saída nova vem em segundo lugar porque é a que o Edital da amostra quer dizer: "todo candidato
PcD".

---

## 5. As grafias

### Composição e Retificação — a opção (`UX-080`)

```text
Exigido apenas da modalidade
  Todas as modalidades
  ── Em todos os Perfis ──
  Pessoas com Deficiência (PcD) — em todos os Perfis que a têm (16 de 16)
  Pretos, Pardos, Indígenas e Quilombolas (PPIQ) — em todos os Perfis que a têm (16 de 16)
  ── Modalidade de um Perfil ──
  LP01 — Letras · PcD — Pessoas com Deficiência
  …
```

- A ampla declarada não aparece no grupo "Em todos os Perfis" (`FR-704`).
- Na composição, o valor da opção transversal é `codigo:<código>`. Na Retificação, o código é um
  campo próprio, "Modalidade em todos os Perfis", com as mesmas opções e rótulos.

### Documento publicado e Revisão (`FR-712`, `FR-713`)

```text
Dos candidatos concorrentes na modalidade Pessoas com Deficiência:
    a) Laudo médico
    b) Autodeclaração para pessoa com deficiência (facultativo)
```

Um grupo por código, sem nome de Perfil. Os grupos de recorte exato continuam como estão.

### Cartão público da vaga (`FR-709`)

Inalterado na forma: *"Se concorrer em Pessoas com Deficiência, também: Laudo médico…"*. A diferença
é que ele aparece no cartão de **todo** Perfil que tem a Modalidade do código.

### Resumo público "O que mudou" (`FR-721`, `D-008`)

```text
Documento exigido “Laudo médico” — Modalidade em todos os Perfis — alterado
```

Sem valor anterior nem novo, como toda linha desse resumo.
