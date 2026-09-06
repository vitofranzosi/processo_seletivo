# Quickstart — Recursos e Superação de Resultados

O roteiro que demonstra o gate da spec, inteiro pelo navegador, alternando atores. Ele não é teste
automatizado: é o percurso que a suíte de aceitação reproduz e que a auditoria exploratória repete à
mão.

## Pré-requisitos

O estado que a 017 já sabe produzir — e que `seed_demo` monta:

- Edital publicado, com Perfil, marco classificatório enumerando duas Etapas;
- inscrições submetidas, avaliadas e consolidadas nas duas Etapas, **incluindo uma eliminada na
  Etapa 1** — ela é a protagonista do primeiro passo;
- `AtoDeOrdenacao` emitido e vigente, e `PublicacaoResultado` **preliminar** publicada.

Atores: **Helena**, candidata eliminada na Etapa 1 e fora do universo do ato; **Ana**, candidata
classificada; `júlia.julgadora` (papel **Julgador**, com `recurso:julgar`); `paulo.presidente`
(presidência, que consolidou os Resultados); `paula.publicadora` (`resultado:publicar`);
`alice.avaliadora` e `otavio.avaliador`.

```bash
cd backend && uv run python manage.py seed_demo
```

```bash
cd backend && uv run python manage.py runserver
```

> A interface administrativa exige o seletor de identidade ligado; sem ele, `/gestao/` devolve 503.

---

## 1 — Helena finalmente vê o que aconteceu com ela

Como **Helena**, abrir o acompanhamento da própria Inscrição.

Antes desta feature, ela via "✓ Inscrição enviada" e o cronograma, e nada mais. Agora lê o próprio
Resultado da Etapa 1, com a consequência e o **motivo escrito** — *"parecer desfavorável na análise
documental (Indeferido)"*. Ela está fora do universo do ato, e vê assim mesmo: o fato autorizador é
a publicação vigente do marco do seu Perfil, que enumera a Etapa 1 (FR-014, FR-015, SC-001).

Conferir que ela **não** vê: Resultado de terceiro, lista de Resultados, parecer, nome de avaliador
(FR-017).

Fecha o E2E17-004 pela raiz.

## 2 — Helena recorre

No mesmo lugar, a ação **Recorrer** aparece ao lado do Resultado. Abrir, escrever a fundamentação,
confirmar.

Nasce o recurso, com protocolo `REC-2026-…`, instante e o objeto atacado nomeado (SC-002).

**Reenviar o formulário**: um recurso só (SC-003). **Recorrer de novo do mesmo Resultado**: recusado,
nomeando o protocolo da primeira peça (SC-004).

Como **Ana**, recorrer da **publicação** — o outro objeto atacável. Mesma tela, mesmo fluxo, mesma
peça: é uma capacidade com dois objetos, e não dois workflows (FR-002).

## 3 — Quem produziu o ato não julga

Como **paulo.presidente**, que consolidou o Resultado de Helena: abrir o recurso dela. Admitir e
julgar são **recusados**, e a recusa nomeia o impedimento (FR-039, SC-005).

Como **paula.publicadora**, que publicou o resultado que Ana atacou: recusada pela mesma porta no
recurso de Ana.

Como **alice.avaliadora**, sem a capacidade: não alcança recurso nenhum (SC-006).

## 4 — A admissibilidade

Como **júlia.julgadora**, abrir o recurso de Helena e **admitir**, com motivo escrito.

Tentar julgar um recurso **ainda não admitido**: recusado — receber a peça não é admiti-la (FR-036).

Como **Helena**, reabrir o acompanhamento: a admissibilidade está lá, com o motivo.

## 5 — Deferir fixando a correção

Como **júlia.julgadora**, julgar o recurso de Helena: **deferir com correção fixada**, declarando o
sentido favorável e a motivação.

O que acontece na mesma transação (SC-007):

```text
DecisaoRecurso imutável  +  ResultadoEtapa sucessor, origem RECURSO, citando a decisão
```

Conferir, como presidência, no histórico do par: os **dois** Resultados, em ordem, com motivo, autor,
instante e a decisão que autorizou a superação.

Conferir que o anterior **não** mudou — pontuação, consequência e motivo intactos.

## 6 — A cadeia a jusante reage sozinha

Como **paulo.presidente**, abrir a tela do marco: o ato vigente aparece **obsoleto**, e a divergência
nomeia a causa — **participante reingressou**, e não apenas "resultados alterados" (FR-078).

Como **paula.publicadora**, abrir a prévia de publicação: **recusada**, com o caminho nomeado —
emitir o ato sucessor (SC-010).

Nada foi recalculado e nada foi emitido automaticamente. A cascata é de bloqueio.

**A providência a jusante, quando houver.** Deferido um recurso da quarta espécie, emitir o ato
sucessor **sem citar a decisão** deixa a publicação definitiva impedida. Emitir citando-a — a tela de
emissão oferece as decisões pendentes do marco — permite publicar; e é a **publicação** desse ato que
cumpre a providência para os sucessores seguintes. Um ato sucessor emitido por razão alheia não quita
nada, e um ato que citou mas nunca foi publicado também não: nesse caso o sucessor **recita** a mesma
decisão.

## 7 — A progressão retroativa aparece

Como **paulo.presidente**, abrir a Etapa 2, que estava consolidada para todos.

Helena aparece como **pendente**, nomeada — *"reabilitada por recurso deferido em DD/MM"* (FR-077,
SC-012). Ela é distribuível, avaliável e consolidável pelas operações que já existem: nenhum estado
de reintegração foi criado.

Tentar publicar o marco antes de consolidar o Resultado dela: **recusado**, nomeando a pendência
reaberta (SC-013).

Distribuir, avaliar e consolidar. A pendência some, e a recusa correspondente também.

## 8 — A tentativa de piora

Como **júlia.julgadora**, julgar o recurso de Ana propondo **pontuação inferior** à vigente.

A operação é recusada: nenhum sucessor pior nasce, e o desfecho é indeferimento (FR-070, SC-008).

## 9 — Reavaliação determinada, e a porta de trás que continua fechada

Deferir um terceiro recurso **determinando reavaliação**. Conferir que **nenhum** Resultado sucessor
nasceu (SC-009).

Como **paulo.presidente**, abrir a Etapa: a inscrição aparece com a pendência nomeada — reavaliação
determinada, não cumprida —, e não como já consolidada.

Distribuir para **otavio.avaliador**. Conferir que **alice.avaliadora**, que concluiu a original, não
consegue concluir de novo — garantia estrutural, não regra nova.

Consolidar a nova Avaliação: nasce o sucessor, citando a decisão.

**A porta de trás**: repetir com uma reavaliação que produza resultado **pior** que o protegido. A
Avaliação é registrada; a consolidação é **recusada** nomeando a vedação, e nenhum sucessor pior
nasce (FR-073, SC-008).

## 10 — A definitividade ganha lastro

Como **paula.publicadora**, tentar publicar como **definitivo**, em cada estado:

| estado | resultado esperado |
|---|---|
| recurso pendente | recusado, com a pendência nomeada |
| reavaliação determinada não cumprida | recusado |
| providência a jusante não cumprida | recusado, publicando ato que **não cita** a decisão e sem ato citante já publicado no marco |
| janela estruturada aberta | recusado, informando quando ela fecha |
| pendência reaberta | recusado |
| tudo resolvido | **permitido** |

Em todos, publicar como **preliminar** continua possível (SC-017).

Sem janela estruturada no Edital, a definitiva exige a **declaração expressa** de encerramento do
prazo, gravada com autor, instante e texto (SC-018).

Publicada a definitiva sobre o ato corrigido, conferir que ela é apresentada **pela causa** —
*"Resultado definitivo, retificado em DD/MM em razão do julgamento do recurso…"* — sem natureza nova
no vocabulário (SC-019), e que a vigente **diz que é a vigente**.

## 11 — A janela recursal

*Requer o degrau 8 — é a última fatia, e o roteiro até aqui funciona sem ela.*

Como elaborador, compor um marco declarando **5 dias corridos**. Publicar o Edital e conferir a frase
no documento.

Publicar o resultado. Como candidato, conferir na página e na Inscrição os instantes exatos de
abertura e encerramento, na zona institucional (SC-014).

Interpor dentro do prazo: aceito, e a peça registra que estava dentro da janela.

Adiantar o relógio para depois do encerramento e tentar de novo: **recusado**, citando a norma, a
abertura e o encerramento — e a ação não é oferecida na tela.

Num Edital publicado **antes** do degrau: zero prazos exibidos, interposição aberta, e a
tempestividade decidida no juízo de admissibilidade com motivo (SC-015, SC-016).

---

## O que o roteiro prova

```text
resultado divulgado
  → Helena vê o próprio Resultado da Etapa            (1)
  → recorre e recebe protocolo                        (2)
  → quem produziu o ato é recusado                    (3)
  → a autoridade elegível admite e julga com motivo   (4, 5)
  → o Resultado é superado, sem alterar nada          (5)
  → o ato fica obsoleto e a publicação é bloqueada    (6)
  → a reabilitação aparece nomeada na Etapa seguinte  (7)
  → nenhum caminho piora a situação de quem recorreu  (8, 9)
  → a definitividade passa a ter lastro               (10)
  → e o prazo, quando declarado, é computado          (11)
```

## Nota de execução da suíte

As garantias centrais desta feature vivem no banco — as duas constraints de cadeia sob concorrência,
a trigger de coerência e a recusa de `UPDATE` pelo papel de runtime. Elas **só são exercidas com
`TEST_DB_ENGINE=postgresql` e `DB_USER`**; sem o primeiro, a suíte cai para SQLite e as pula em
silêncio. Um PR verde em SQLite não prova nada do que esta feature promete (T-014).
