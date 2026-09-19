---

description: "Implementation plan — 037 · Quatro becos que o sistema já conhece"
---

# Implementation Plan: Quatro becos que o sistema já conhece

**Branch**: `claude/spec-037-quatro-becos` · **Spec**: [spec.md](spec.md)
**Input**: [spec.md](spec.md) · [research.md](research.md) · [data-model.md](data-model.md) ·
[contracts/](contracts/) · [quickstart.md](quickstart.md)

## Summary

Quatro achados, uma família: **em todos o sistema já sabe, e a informação não chega ao lugar onde a
pessoa decide.** O link do corte deixa de sumir — e o caminho que a tela oferece ao lado da recusa
passa a depender de qual recusa é; dois bloqueios passam a dizer a quem pedir, pelo mecanismo único
que a `033` deixou; a régua do vencido passa a olhar o término **quando há término**; e o rótulo do
peso para de mentir, com a contradição antecipando para o momento em que a Etapa é enumerada.

**Nenhuma entidade nova. Nenhuma migration. Nenhuma capacidade nova. Nenhum conteúdo publicado
reescrito.**

## Technical Context

**Linguagem**: Python 3.13 · Django 5.2.17 · PostgreSQL. **Testes**: pytest, contra PostgreSQL.
**Superfícies tocadas**: a tela do Edital, a do corte, o cartão do marco, o cartão da Etapa, o selo
do Cronograma e a conferência de publicação.

| Pergunta | Resposta, e onde ela foi medida |
|---|---|
| Entidade nova? | **não** — `data-model.md` |
| Migration? | **não**. O total do `make preparar` continua **32** (a `036` acrescentou a 32ª) |
| Capacidade nova? | **não** (`FR-553`) |
| Regra de domínio muda o que decide? | **não** — muda *quando* e *onde* se diz, e a calibragem de um predicado |
| Testes que mudam de sentido | **4**, medidos, em 3 arquivos (`research.md` `R-4`) — **recontar** |
| A frase da condução | existe como **mecanismo público**, não como padrão a copiar (`R-6`) |

## Constitution Check

| Princípio | Como esta feature o respeita | Onde |
|---|---|---|
| **Publicação é ato imutável** | nada de conteúdo publicado é reescrito; a régua do vencido continua **advertindo e nunca recusando** | `FR-548`, `FR-555` |
| **Nada é excluído** | nenhuma migration, nenhum dado normativo tocado | `data-model.md` |
| **Negar por padrão** | nenhuma capacidade nova; o destino do corte continua oferecido só a quem o alcança | `FR-540`, `FR-553` |
| **I · Linguagem Ubíqua** | *regra de corte*, *Evento vencido*, *peso da Etapa*, *Retificação* são do domínio | `FR-538`, `FR-545`, `FR-550` |
| **VI · Completude de Jornada** | três becos fechados e um quarto registrado; a jornada da composição deixa de ter etapa impossível de concluir | `SC-190` |
| **Uma maneira de dizer cada coisa** | a condução sai do mecanismo único, e não de texto imitado | `FR-543` |

**Portões**: nenhuma violação. Nenhum desvio a justificar.

## Phase 0 — o que a medição mudou

Completa, em [research.md](research.md). Das cinco afirmações que a spec pediu para confirmar, três
se confirmaram, **uma se confirmou pela metade e produziu requisito novo** (`FR-539a`) e **uma se
mostrou parcialmente já resolvida** (`R-5`).

**Não houve contradição que impedisse a Phase 1** — ao contrário da `035`, onde a medição contradisse
a spec e a Phase 0 parou. Aqui ela **encolheu duas partes, cresceu uma e adiou uma decisão para o
percurso**, e a spec foi emendada antes de o desenho começar: `FR-539a`, `FR-542` reescrita,
`FR-542b`, `FR-543`/`FR-543a`, `FR-546a`, `FR-549a`.

## Phase 1 — desenho

| Artefato | O que decide |
|---|---|
| [data-model.md](data-model.md) | que **não há modelo a mudar**, e por que o peso fica onde está |
| [contracts/o-caminho-da-recusa.md](contracts/o-caminho-da-recusa.md) | qual recusa leva a qual caminho — as três, lado a lado |
| [contracts/a-regua-do-vencido.md](contracts/a-regua-do-vencido.md) | a tabela-verdade do predicado, antes e depois |
| [quickstart.md](quickstart.md) | cinco percursos, e o que registrar quando não houver caminho |

## Ordem de entrega

```
US1 (o corte)  ──┐
US2 (as frases) ─┼─► independentes entre si: telas diferentes, nenhuma dependência
US3 (a régua)  ──┤
US4 (o peso)   ──┘
```

**As quatro são independentes**, e é a primeira vez nesta série que isso acontece — são quatro
achados reunidos por causa comum, não por dependência técnica. Qualquer uma entrega sozinha.

**A `US3` é a mais arriscada**, e não a maior: ela muda um predicado que **duas** superfícies
consultam e que **quatro** testes prendem, dois deles defendendo o comportamento errado por escrito.

**A `US2` começa por um percurso**, e não por código (`FR-542b`).

## Riscos, medidos

| Risco | Onde | Como se fecha |
|---|---|---|
| a `FR-538` abre um beco novo | `R-1` | `FR-539a` nasce junto com ela, e não depois |
| teste que troca o que afirma sem trocar a contagem | `R-4` | conferência **caso a caso**, com o "antes" gravado |
| prosa nova quebra asserção de substring | `research.md`, fim | a varredura lê o comentário do template; rodar a suíte, não só o arquivo tocado |
| escrever a condução à mão | `R-6` | usar `frase_da_recusa`; escrever à mão derrota a guarda da `033` |
| "corrigir" o homônimo | `R-2` | o `vencido` do rascunho no navegador **não** é consumidor |
