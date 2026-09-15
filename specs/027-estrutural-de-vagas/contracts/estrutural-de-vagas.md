# Contrato — 027 · Estrutural de vagas

Fase 1. **A forma não muda em lugar nenhum.** Nenhum campo é acrescentado, removido ou renomeado, no
rascunho ou no conteúdo publicado, e nenhum degrau de schema é aberto. O que este documento registra
é o que muda no **comportamento observável** do que já está contratado — que é o que
`tests/contract/test_openapi_conformance.py` verifica.

O contrato canônico continua sendo
`specs/001-processo-seletivo-editais/contracts/openapi.yaml`.

---

## 1 · Rascunho — `PUT /api/v1/editais/{id}/draft`

`vacancyTable` continua **opcional** no envio, e a `LinhaDoQuadroInput` continua com a forma que a
`025` declarou.

**O que muda:** para todo Perfil cujo conjunto de listas reservadas seja vazio — nenhuma Modalidade,
ou só a que ele declara como ampla concorrência —, a resposta passa a devolver uma **linha geral**
com `immediateVacancies` igual ao total do Perfil, mesmo que o envio não a traga.

```
envio     { "immediateVacancies": 2, "competitionModalities": [], "vacancyTable": [] }
resposta  { "immediateVacancies": 2, "competitionModalities": [],
            "vacancyTable": [ { "id": "…", "modalityId": null, "immediateVacancies": 2 } ] }
```

- O `id` enviado é preservado; sem envio, nasce um e é estável dali em diante.
- Gravar a mesma carga duas vezes produz o mesmo conteúdo — a operação é idempotente.
- **Não** há derivação quando existe lista reservada: ali a repartição é declarada.

Quem integra por API e hoje envia `vacancyTable` vazio passa a receber uma linha. É mudança de
comportamento, não de forma, e é o objeto da `FR-316`.

---

## 2 · Submissão e publicação

| Situação | Antes | Agora |
|---|---|---|
| Perfil sem linha geral | publicava | **recusado**, com `vacancy_general_row_missing` |
| Lista reservada sem linha | silêncio | advertência, não impeditiva |
| Modalidade declarada, ampla não apontada | silêncio | advertência, não impeditiva |
| Quadro completo com ampla declarada | igualdade **não era conferida** | conferida (`T-002`) |

As advertências chegam no mesmo envelope de achados que a operação já devolve, com a severidade que
ela já distingue. Nada que era 200 passa a ser 4xx por causa de advertência.

---

## 3 · Retificação

**A forma dos caminhos não muda**: a linha continua endereçada por
`/profiles/id={perfil}/vacancyTable/id={linha}`, e a linha nova continua sendo acrescentada pelo
caminho que a `025` abriu.

| Situação | Comportamento |
|---|---|
| Retificar Edital publicado **sem** quadro, em qualquer campo | continua passando. A ausência de linha geral **não** é impeditiva no ato de Retificação (`FR-323`, `T-003`) |
| Alterar o total de um Perfil publicado **com** linha geral e sem lista reservada | exige alterar a linha no mesmo ato; recusa nomeia os dois números (`FR-335`) |
| Alterar o total de um Perfil publicado **sem** linha geral | passa, com advertência que nomeia o ato que resolve (`FR-335`) |
| Acrescentar linha a Edital cuja ordem já foi emitida | permitido, e vale para o que vier (`FR-334`) |

A confirmação da Retificação passa a exibir os achados **não** impeditivos do conteúdo que o ato
produziria — informação que já é calculada e hoje é descartada (`T-006`).

---

## 4 · Leitura de conteúdo publicado

**Contrato negativo, e é o mais importante desta feature.** Nenhum leitor de conteúdo publicado
infere linha ausente: `linha_do_quadro(conteudo, perfil_id=…, lista_id=…)` continua devolvendo nada
quando o Edital não publicou a linha, e a Ocupação continua recusando apurar ali.

O que muda é a **frase**, que passa a nomear o ato que declara a quantidade (`FR-332`) — e não o
comportamento.

---

## 5 · O que não entra no contrato

- Nenhum endpoint novo.
- Nenhuma permissão nova.
- Nenhum degrau de schema, e portanto nenhuma `schemaVersion` nova no conteúdo publicado.
- Nenhuma conversão de conteúdo publicado.
