---

description: "Implementation plan — 038 · Painel de condução do Processo vivo"
---

# Implementation Plan: Painel de condução do Processo vivo

**Branch**: `claude/spec-038-painel` · **Spec**: [spec.md](spec.md)

## Summary

O guia não desliga quando o Edital é publicado. A página do Processo passa a mostrar o **pulso** e a
**Atenção** que hoje só existem na Supervisão, e a Atenção ganha **quatro espécies** que alcançam a
cauda: avaliação parada, recurso com julgador disponível, recorte sem ocupação e ato não publicado.

**Nenhuma entidade nova, nenhuma migration, nenhuma capacidade de autorização nova, nenhum estado
novo calculado.** A feature **reúne e encaminha**.

## Technical Context

Python 3.13 · Django 5.2.17 · PostgreSQL. Superfícies: a página do **Processo** e o módulo de
**Supervisão**. O total do `make preparar` continua **`N de 33`**.

| Pergunta | Resposta, medida |
|---|---|
| Entidade nova? | **não** |
| Migration? | **não** |
| Estado novo calculado? | **não** — três espécies saem de leitura existente, a quarta de extração (`R-6`) |
| Consulta nova? | **uma por recorte** (terceira espécie) e o que a extração da quarta trouxer |
| Casos que cercam a Supervisão | **34**, em 4 arquivos (`R-7`) — recontar |

## Constitution Check

| Princípio | Como se respeita | Onde |
|---|---|---|
| **Negar por padrão** | nenhuma capacidade nova; sinal não oferece destino que o ator não abre | `FR-558`, `FR-566` |
| **Nada é excluído** | nenhuma migration, nenhum dado normativo tocado | `data-model.md` |
| **Publicação é ato imutável** | a feature **lê** estado de publicação; não a pratica nem a altera | `FR-566` |
| **Uma maneira de dizer cada coisa** | indicador deriva da mesma leitura que governa o destino | `FR-557`, `R-6` |
| **VI · Completude de Jornada** | o Processo passa a dizer onde cada Edital está | `SC-196` |

**Nenhuma violação.** Nenhum desvio a justificar.

## Phase 0 — o que a medição decidiu

Completa em [research.md](research.md). As quatro premissas da spec se confirmam, e a medição
**repartiu as quatro espécies em duas classes**:

- **duas saem de leitura que já existe, sem consulta nova** — `resumo_da_etapa` já é chamado pelo
  `UX-003`, e o recurso com julgador é a **negação** da condição do `UX-005`, do mesmo cálculo;
- **uma custa consulta**: o recorte sem ocupação precisa de `apuracao_vigente`, que a Supervisão
  **não lê hoje** — uma leitura por recorte, e o orçamento precisa acomodá-la (`R-5`);
- **uma custa extração**: a derivação de *ato emitido e não publicado* existe **só dentro de
  `interface/views.py`**, e a `FR-557` obriga a extraí-la em vez de reescrevê-la.

**Nenhuma inventa estado**, de modo que a `FR-567` não precisou tirar nada do escopo.

## Ordem de entrega, e a dependência da `037`

```
US2a — três espécies, só em supervisao.py     ← primeiro entregável, não espera ninguém
   │
   ├──► US1  — o Processo recebe pulso e Atenção   ← views.py: ESPERA a 037
   │
   └──► US2b — a quarta, por extração             ← views.py: ESPERA a 037
                │
                └──► US3 — o catálogo volta a ser verdade
```

**A `US2` se parte em duas por medição, e não por conveniência.** A `037` altera
`interface/views.py`, e a quarta espécie exige mexer exatamente nele.

**E a ordem das fases não é a das prioridades.** O `tasks` obrigou a encarar o que este plano tinha
deixado implícito: a **`US1` também vive em `interface/views.py`** — é lá que está `processo_detalhe`
—, de modo que a única fase que não espera a `037` é a `US2a`. Ela é `P2` e vai primeiro; é **ordem
de integração, não de valor**.

**Se a `037` demorar**, a `US2a` e a `US3` já entregam — três dos quatro estados e a dívida do
catálogo fechada —, e a quarta espécie fica registrada, que é o que a `FR-567` manda.

## Riscos, medidos

| Risco | Onde | Como se fecha |
|---|---|---|
| quebrar o orçamento de consulta dos sinais | `R-7` — há guarda com nome | **duas** espécies não acrescentam consulta; a do recorte acrescenta **uma por recorte**, e o orçamento é remedido com a razão escrita |
| os dois sinais de recurso divergirem | `R-4` | nascem do **mesmo** cálculo, partido em dois desfechos |
| reescrever a derivação da divulgação | `R-6` | **extrair**, nunca reescrever — é a `FR-557` |
| contar os casos alterados pelo nome do arquivo | `R-7` | 34 casos em 4 arquivos; recontar caso a caso |

## Phase 1 — desenho

| Artefato | O que decide |
|---|---|
| [data-model.md](data-model.md) | que não há modelo a mudar, e de onde cada espécie lê |
| [contracts/as-quatro-especies.md](contracts/as-quatro-especies.md) | condição, mensagem e destino de cada uma — e o que **não** se afirma |
| [quickstart.md](quickstart.md) | quatro percursos, um por espécie, mais o do Processo |
