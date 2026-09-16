# Contrato — 028 · Cronograma reaproveitado não nasce publicável

Fase 1. **A forma não muda em lugar nenhum.** Nenhum campo é acrescentado, removido ou renomeado, no
rascunho ou no conteúdo publicado, e nenhum degrau de schema é aberto. O que este documento registra
é o que muda no **comportamento observável** do que já está contratado — que é o que
`tests/contract/test_openapi_conformance.py` verifica.

O contrato canônico continua sendo
`specs/001-processo-seletivo-editais/contracts/openapi.yaml`.

---

## 1 · Rascunho — `PUT /api/v1/editais/{id}/draft`

**Nada muda.** `schedule`, `startAt`, `endAt` e `isRegistrationPeriod` continuam com a forma que
têm, a gravação continua aceitando data no passado, e **nenhuma data enviada é alterada, deslocada,
completada ou substituída** na resposta (`FR-351`).

Gravar um cronograma vencido continua sendo uma operação bem-sucedida. É na submissão que ele para.

---

## 2 · Submissão — `POST /api/v1/editais/{id}/submeter`

| Situação | Antes | Agora |
|---|---|---|
| Evento com início ou término no passado | silêncio | advertência `schedule_event_in_past` |
| Evento cujo ano diverge do ano do Edital | silêncio | advertência `schedule_event_year_mismatch` |
| Período de inscrições com término no passado | **submetia** | `422 blocking_findings`, com `registration_period_closed` |
| Período de inscrições sem término declarado | silêncio | **continua em silêncio** |
| Período de inscrições aberto ou futuro | silêncio | **continua em silêncio** |
| Nenhum Evento marcado como período | advertência `registration_period_missing` | **inalterada**, e nenhum achado novo |
| Mais de um Evento marcado | impeditivo `registration_period_ambiguous` | **inalterado** |

As advertências chegam no mesmo envelope de achados que a operação já devolve, com a severidade que
ela já distingue. **Nada que era 200 passa a ser 4xx por causa de advertência** — só o período
encerrado fecha porta.

---

## 3 · Publicação — `POST /api/v1/editais/{id}/publicar`

A mesma conferência, no mesmo envelope, contra o instante **da publicação** — e não o da submissão.

Consequência declarada, e é a `FR-358`: um Edital cujo período estava aberto quando foi submetido e
homologado, e cujo término passou antes de a publicação ser confirmada, é **recusado na publicação**.
Não é regressão; é o único desfecho correto, porque publicá-lo produziria um certame que ninguém
poderia disputar.

O mesmo vale para quem nunca abriu a Revisão (`FR-357`): a conferência da publicação é independente
da da submissão, e já era.

---

## 4 · Retificação — `POST /api/v1/retificacoes/{id}/publicar`

**Nenhum dos três achados existe neste ato** (`FR-354`).

| Situação | Comportamento |
|---|---|
| Edital do acervo com o cronograma inteiro vencido | nenhum achado desta feature; a Retificação segue |
| Retificação que declara término de inscrições já passado | **não é recusada** (`FR-355`) |
| Retificação que move um Evento para o passado | nenhum achado desta feature |
| `registration_period_missing` / `_ambiguous` | **inalterados**, como já eram |

A razão está em [data-model.md](data-model.md) §5 e é a mesma que a `027` deixou escrita: no acervo,
evento vencido é a condição normal, e uma advertência que se repete a cada ato deixa de ser lida.

---

## 5 · Códigos de achado

Três, todos próprios, nenhum reusado:

| Código | Severidade | Caminho |
|---|---|---|
| `schedule_event_in_past` | `WARNING` | `/schedule/id=<uuid>/startAt` ou `/endAt` |
| `schedule_event_year_mismatch` | `WARNING` | `/schedule/id=<uuid>/startAt` |
| `registration_period_closed` | `BLOCKING_ERROR` | `/schedule/id=<uuid>/endAt` |

**O caminho é o do Evento, e nunca `/schedule`.** A entrada exata `/schedule` do roteamento de
pendências manda para a etapa **Inscrição**, que é onde a *designação* do período se resolve — e não
tem campo de data. Com o caminho da entidade, o roteamento existente encontra `schedule` percorrendo
os segmentos e entrega a etapa **Cronograma**, sem nenhuma entrada nova (`FR-349`,
[research.md](research.md) `T-005`).

`registration_period_closed` compartilha o prefixo dos dois códigos existentes porque fala da mesma
coisa. O teste do repositório que filtra por `startswith("registration_period")` passa a enxergá-lo,
e é o comportamento desejado.

---

## 6 · Apresentação das mensagens

Cada mensagem diz o instante em forma legível na **zona institucional** — nunca texto ISO cru, nunca
JSON Pointer, nunca instante em UTC (`UX-047`). O impedimento diz **quando** as inscrições se
encerraram e **o que acontece** se o Edital for publicado assim (`UX-048`).

É a régua que a auditoria cobrou no achado P1 *"JSON Pointer e UTC na conferência da Retificação"*, e
esta feature não é o lugar de repeti-lo.

---

## 7 · O que nenhum canal passa a fazer

- Alterar, deslocar ou sugerir data (`FR-351`).
- Conferir duração de Evento (`FR-352`).
- Acrescentar campo, marca ou estado ao conteúdo publicado (`FR-353`).
- Recusar, alterar ou reescrever conteúdo já publicado (`FR-365`).
- Mudar o que o reaproveitamento copia (`FR-364`).
