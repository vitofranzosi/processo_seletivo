# Phase 1 — Modelo de dados · 034 · Ordem por recorte em marco computado

**Nenhuma entidade nova. Nenhum campo novo. Nenhuma migration.** Este arquivo existe para dizer o
que **já existe** e passa a ser usado, e para registrar o que foi conferido antes de se afirmar isso.

---

## O que não muda, e por que isso é a notícia

| Entidade | Campo que a feature usa | Estado | Conferido em |
|---|---|---|---|
| `AtoDeOrdenacao` | `lista_id` (UUID, anulável) | **existe desde a `021`** | `classificacao/models.py` |
| `AtoDeOrdenacao` | `origem` (`COMPUTADO` \| `SORTEIO`) | existe | idem |
| `AtoDeOrdenacao` | raiz única por `(edital, perfil, marco)` **e** por `(edital, perfil, marco, lista)` | duas constraints parciais | idem, `Meta.constraints` |
| `PosicaoNaOrdem` | `lista_id`, *"`NULL` = ampla concorrência, a mesma grafia de `AtoDeOrdenacao.lista_id`"* | existe | `classificacao/models.py` |
| `ApuracaoDeOcupacao` | `lista_id`, com a mesma grafia | existe | `ocupacao/models.py` |
| `Inscricao` | `modality_id` (UUID, anulável) | existe | `inscricoes/models.py` |

**`modality_id` é anulável, e o nulo é o caso normal.** Quem não se autodeclara em Modalidade alguma
tem modalidade nula e concorre pela ampla. Isso é o que faz `FR-492` ser barata de implementar e cara
de escrever errado: o universo da ampla é *todo mundo*, e o do recorte reservado é *quem declarou
aquela Modalidade* — não é uma partição, é uma **sobreposição**.

```
universo do Perfil ─────────────────────────────────────────────┐
│  ampla concorrência (lista NULL) = TODOS                       │
│    ├── quem não se autodeclarou                                │
│    └── quem se autodeclarou em PcD  ─┐                         │
│    └── quem se autodeclarou em PPI  ─┼─ e também estão aqui ↓  │
└───────────────────────────────────────┼────────────────────────┘
      recorte PcD (lista = id de PcD) ──┘  = só os autodeclarados de PcD
      recorte PPI (lista = id de PPI) ─────  = só os autodeclarados de PPI
```

É o `D-001`, e é o que a ocupação já pressupõe quando desconta da cota quem ocupou pela ampla.

---

## O conceito que ganha um dono: **o conjunto de recortes de um marco**

Hoje ele é derivado em três lugares que não concordam (`research.md`, `R-3`). A feature dá a ele um
lugar só para o caminho computado, e o contrato está em
[contracts/recortes-de-um-marco.md](contracts/recortes-de-um-marco.md).

**Recorte** não é entidade persistida: é o par (Perfil, Modalidade) sobre o qual se ordena, corta,
apura e convoca. O que o persiste é a coluna `lista_id` de cada ato.

| Espécie de recorte | `lista_id` | De onde vem a quantidade |
|---|---|---|
| Ampla concorrência | `NULL` | linha geral do Quadro de Vagas (`modalityId` nulo) |
| Modalidade reservada | id da Modalidade | linha própria do Quadro |
| Modalidade **declarada como ampla** | **não é recorte** | a quantidade dela **é** a da linha geral |

---

## Transições de estado de um recorte

Nenhuma é nova. O que muda é **quais recortes as percorrem**.

```
sem ordem ──emitir──► ordem vigente ──suceder──► ordem vigente (nova)
                           │
                           ├──cortar──► faixa ──apurar──► ocupação ──convocar──►
                           │
                           └──obsoletar──► ordem obsoleta
```

**A cadeia é por recorte, e não atravessa** (`FR-494`): suceder a ordem de PcD não obsoleta a da
ampla, e a constraint `uq_ato_sucessor_unico` já garante que cada ato tem no máximo um sucessor
**dentro da sua própria cadeia**.

---

## Regras de validação que passam a ter alcance diferente

| Regra | Hoje | Depois |
|---|---|---|
| `reserved_row_without_ordering` | avisa que a reserva não tem via de apuração | **aposentada** — não sobra caso que a produza (`FR-501`) |
| `emite_ordem_no_recorte` | responde não para recorte reservado de marco computado | **removida**, com o campo `apuravel` derivado dela, por deixar de variar (`FR-501a`) |
| a ação de apurar, na tela | ramifica em `apuravel` | oferecida sempre que o recorte tem ordem — e **sem instante em que deixe de ser oferecida** durante a travessia (`FR-502`) |
| assinatura da proposta | uma por marco | **uma por recorte** (`FR-495`) |

**As três primeiras decorrem da mesma linha** — a resposta de `emite_ordem_no_recorte` —, e a quarta
**não**: a assinatura por recorte vem da `FR-495` e não tem relação com o predicado. A redação
anterior dizia "as três decorrem", com três linhas na tabela, e uma delas era a assinatura: a
afirmação nunca foi verdadeira e sobreviveu porque a contagem batia.

---

## O que foi conferido e **não** entra

- **Nenhum campo `origem` novo** para distinguir "computado por recorte". `origem` já separa
  computado de sorteio, e o recorte já é `lista_id`. Um terceiro eixo não teria o que declarar.
- **Nenhuma tabela de recortes.** O conjunto é derivado do conteúdo publicado do Perfil, que é onde a
  norma vive; persistir o derivado criaria uma segunda verdade que a Retificação faria divergir.
