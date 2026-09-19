# Phase 1 — Modelo de dados · 036 · Instrução do recurso

**Uma entidade nova, e ela é um ato.** O resto já existe: o parecer, a avaliação que o produziu, o
recurso, e o registro de auditoria que sabe anotar leitura.

---

## O que já existe, e passa a ser usado

| Coisa | Onde vive | O que a feature faz com ela |
|---|---|---|
| `parecer` da avaliação | campo de texto na Avaliação | **exibe** — ao titular e ao julgador instruído |
| `parecer` da conclusão | registro **append-only** de cada reabertura | **fonte quando houve reabertura** (`FR-523`) |
| o vínculo resultado → avaliação | um-para-um | é ele que diz **qual** parecer responde pelo resultado (`D-002`) |
| o recurso, com o resultado atacado | já carregado na tela de quem julga | **não precisa de consulta nova** (`research.md` `R-3`) |
| `motivo` do resultado | já exibido ao candidato desde a `013` | **continua onde está**, e o parecer vem ao lado (`FR-525a`) |
| o registro de auditoria | anota ato **e leitura**, com escopo e sem conteúdo | registra a instrução **e** o acesso (`FR-533`, `FR-534`) |

---

## A entidade nova: o ato de instrução

**É ato, e não configuração.** Tem autor, instante e alcance, e é **append-only** — como
`AtoAdministrativo` e `VersaoConsolidada`, que é o padrão que o próprio código nomeia.

| O que guarda | Por quê |
|---|---|
| o **recurso** que instrui | é o alcance, e ele não se estende a nenhum outro (`FR-528`) |
| **o que** foi anexado | o parecer atacado, o documento citado, ou os dois |
| **quem** instruiu e **quando** | é ato: sem autor não é ato, é estado |
| a **razão**, se houver | a mesma disciplina dos outros atos do produto |

**O que ele NÃO guarda:**

- **Não guarda cópia do documento.** A prova é alcançada por referência (`FR-531`). Copiar
  multiplicaria a superfície do dado pessoal e criaria uma segunda cópia que a Constituição depois
  proíbe apagar.
- **Não guarda o texto do parecer.** Ele já existe; duplicá-lo criaria duas verdades sobre o que o
  avaliador escreveu, e a segunda envelheceria.
- **Não guarda "quem pode ver".** O alcance é derivado — quem julga **aquele** recurso, enquanto ele
  não estiver decidido. Guardar uma lista de pessoas seria uma permissão com outro nome, que é o que
  a `FR-530` proíbe.

---

## O ciclo do alcance

```
recurso interposto
      │
      ├── nada instruído ──► quem julga lê o que falta e a quem pedir   (FR-532)
      │
      └── instrução praticada ──► quem julga alcança a prova            (FR-527)
                  │
                  └── recurso decidido ──► o alcance termina            (FR-529)
                                            o registro permanece
```

**A distinção entre as duas últimas caixas é o coração da feature.** *Nada se apaga* e *o acesso
termina* não são contraditórios: o que fica é a memória de que a instrução houve; o que termina é a
porta que ela abriu.

Sem a segunda, a instrução seria uma ampliação de acesso permanente concedida por um clique — que é a
`FR-105` da `018` violada com outro nome.

---

## Onde o parecer aparece, e onde não aparece

| Tela | Quem | Quando |
|---|---|---|
| acompanhamento, no canal do candidato | **o titular** | enquanto o prazo recursal estiver aberto (`D-001`) |
| peça do recurso, na gestão | **quem julga aquele recurso** | depois da instrução, até a decisão |
| peça do recurso, na gestão | quem preside ou audita | **como hoje** — esta feature não muda o que eles já alcançam |
| qualquer listagem | ninguém | a fundamentação e o parecer não entram em listagem, e isso já é prendido |

---

## Nenhuma migration? Não — e a diferença importa

As três features anteriores prometeram **nenhuma migration**, e cumpriram. **Esta não pode
prometer**: o ato de instrução é entidade nova, e entidade nova é tabela nova.

**O que ela promete é outra coisa**: nenhuma **capacidade** nova (`FR-530`), nenhum parecer alterado
(`FR-537`), e nada de conteúdo publicado reescrito. A tabela nova nasce **append-only**, com a mesma
proteção das outras — trigger e privilégio ausente, as duas camadas que a Constituição exige.
