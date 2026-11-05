# Data Model: Os mesmos recortes no sorteio, na divulgação, na ocupação e na Supervisão

**Nenhuma tabela, coluna, constraint ou migration** (FR-3914). Tudo abaixo é **derivado** de dados que
já existem. O `M` do provisionamento (53 tabelas append-only) não muda.

## Fontes que já existem

| Registro | Tabela | Recorte | Versão de origem |
|---|---|---|---|
| Relação de habilitados | `RelacaoDeHabilitados` | `lista_id` | `versao` |
| Sorteio | `Sorteio` | `lista_id` (cópia da relação) | `relacao.versao` |
| Ato de ordenação | `AtoDeOrdenacao` | `lista_id` | `versao` |
| Publicação de resultado | `PublicacaoResultado` | `lista_id` | `ato.versao` |
| Versão consolidada | `VersaoConsolidada` | — | `content` → `profiles[].generalCompetitionModalityId`; número pela `source_publication.publication_order` |

## Conceitos derivados

### Papel do recorte

`papel_do_recorte(conteudo, perfil_id, lista_id)` → um de:

| Papel | Quando |
|---|---|
| `OPERACIONAL` | `lista_id` nulo (ampla), ou Modalidade do Perfil que **não** é a apontada |
| `EXCEDENTE` | `lista_id` igual ao `generalCompetitionModalityId` do Perfil |
| `AUSENTE` | `lista_id` que não é Modalidade do Perfil naquela versão |

O papel depende **só** do apontamento (FR-3894), e nunca de nome ou código.

### Registro excedente

Um registro das quatro espécies cujo papel **na versão vigente** é `EXCEDENTE` (FR-3911).

| Atributo derivado | Regra |
|---|---|
| `origem` | `NASCIDO` se o papel na versão de origem também é `EXCEDENTE`; `TORNADO` se era `OPERACIONAL` |
| `retificacao_que_tornou` | só para `TORNADO`: a primeira versão posterior à de origem com papel `EXCEDENTE`; exibida como *Retificação nº N* |
| `frase` | a do contrato, por `origem` ([contracts/recorte-excedente.md](contracts/recorte-excedente.md)) |

### Ato de papel mudado

Um ato cujo papel na versão de origem difere do papel na vigente, **com papel vigente `OPERACIONAL`**
(FR-3912). Aparece no recorte operacional como **obsoleto**, com a divergência
`tipo="papel_do_recorte"`. Não é registro excedente.

## Transições

O papel não se grava, e por isso não tem transição. O que muda é a **versão vigente**, por Retificação,
e cada registro é relido contra ela:

```text
                      Retificação aponta a Modalidade
   OPERACIONAL  ─────────────────────────────────────▶  EXCEDENTE (origem TORNADO)
        ▲                                                      │
        │      Retificação retira ou troca o apontamento       │
        └──────────────────────────────────────────────────────┘
              o ato reaparece no recorte, OBSOLETO (papel_do_recorte),
              e o trabalho segue por relação, sorteio e ato novos (D-004)
```

O registro **nascido** excedente que volta a ser operacional segue a mesma seta de baixo: aparece
obsoleto, e nunca vigente por si.

## Invariantes

1. Nenhum registro muda de `lista_id`, nem é sucedido, anulado ou ocultado por esta feature (FR-3902).
2. Nenhum comando grava relação, sorteio ou publicação em recorte de papel vigente `EXCEDENTE`
   (FR-3897 a FR-3899). A emissão computada normaliza o apelido para a ampla (FR-3900).
3. Toda superfície que conta recortes os conta pela derivação canônica (FR-3893, FR-3916).
4. A frase de um registro depende só da versão dele e das versões posteriores até a vigente, nunca de
   estado de sessão.
