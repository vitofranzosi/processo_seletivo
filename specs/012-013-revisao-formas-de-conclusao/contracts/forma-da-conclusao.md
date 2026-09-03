# Contrato: a forma da conclusão

**Revisão**: `012-013-revisao-formas-de-conclusao` | **Escopo**: [spec.md](../spec.md)

Não há superfície de API nova, e nenhuma rota nasce ou muda de caminho. O que este documento fixa é
o **delta de contrato**: a forma publicada nova, os corpos aceitos nas duas rotas de escrita da Mesa,
a forma das recusas, e o que o documento materializado passa a mostrar. A forma publicada é contrato
de verdade, conferido por teste contra o `openapi.yaml` da 001.

---

## 1. Forma publicada — item de `stages`

```json
{
  "id": "…", "name": "Análise documental", "order": 2,
  "weight": null,
  "eliminatory": true,
  "classificatory": false,
  "minimumScore": null,
  "maximumScore": null,
  "evaluationsPerRegistration": 1,
  "forma": "DECISORIA",
  "rotuloFavoravel": "Deferido",
  "rotuloDesfavoravel": "Indeferido",
  "scheduleEventId": "…"
}
```

Na forma pontuada, `forma` é `"PONTUADA"` e os dois rótulos são `null`. Em conteúdo na versão
canônica 5, `forma` **não existe** e é lida como `"PONTUADA"`.

`schemaVersion` da raiz passa a `6`.

### Recusas do contrato

| situação | código | mensagem (forma) |
|---|---|---|
| `forma` fora do conjunto | `FORMATO_INVALIDO` | aponta `/stages/<i>/forma` |
| `DECISORIA` sem rótulo | `RESTRICAO_VIOLADA` | "A Etapa decisória deve publicar os rótulos do resultado em …" |
| `PONTUADA` com rótulo | `RESTRICAO_VIOLADA` | "A Etapa pontuada não publica rótulos de resultado em …" |
| `DECISORIA` com `minimumScore` ou `maximumScore` | `RESTRICAO_VIOLADA` | "A Etapa decisória não publica nota em …" |

## 2. `POST .../inscricoes/<inscricao_id>/avaliacao` — rascunho

| forma da Etapa | campos aceitos | campos recusados |
|---|---|---|
| `PONTUADA` | `pontuacao`, `parecer`, `revision` | `sentido` |
| `DECISORIA` | `sentido`, `parecer`, `revision` | `pontuacao` |

O rascunho aceita o campo da forma **vazio** — quem está no meio do trabalho ainda não decidiu. O
que ele não aceita é o campo da outra forma, e a recusa é do domínio, com mensagem: ignorar em
silêncio faria a tela decidir uma regra normativa (012, FR-122).

## 3. `POST .../inscricoes/<inscricao_id>/avaliacao/concluir`

Além do que já valia — reconhecimento explícito da versão (FR-073), revisão esperada (FR-081):

| forma | exigido | recusa quando falta |
|---|---|---|
| `PONTUADA` | `pontuacao` dentro do publicado | "Informe a pontuação." |
| `DECISORIA` | `sentido` ∈ {favorável, desfavorável} | "Informe o sentido da decisão." |
| `DECISORIA` ∧ `DESFAVORAVEL` | `parecer` não vazio | a recusa nomeia o rótulo publicado |
| `PONTUADA` ∧ eliminatória ∧ abaixo da mínima | `parecer` não vazio | inalterada (FR-034) |

Na tela, o par de opções é rotulado pelo Edital — "Deferido" e "Indeferido" —, e nunca pelo enum.

## 4. `POST editais/<edital_id>/resultados/<etapa_id>` — o lote da 013

Corpo e desfecho **inalterados**. O que muda é o conjunto de recusas por Etapa:

| impedimento | quando | frase |
|---|---|---|
| `regra_de_combinacao_ausente` | previstas > 1 | inalterada |
| `regra_insuficiente` | `PONTUADA` ∧ eliminatória ∧ sem nota mínima | inalterada, **agora condicionada à forma** |
| `regra_insuficiente` | `DECISORIA` ∧ não eliminatória | "a Etapa é decisória e o Edital não publicou o efeito da decisão desfavorável" |

Os dois impedimentos de regra insuficiente são da **Etapa inteira**, e aparecem na prontidão antes
de qualquer tentativa de consolidar.

## 5. Retificação — `CAMPOS_ETAPA`

A lista da tela passa a cobrir todos os campos normativos da Etapa: os cinco atuais, os dois que o
primeiro incremento deixou para trás (`maximumScore`, `evaluationsPerRegistration`) e os três novos.
Um teste compara a lista com o contrato da Etapa publicada, para que o próximo campo normativo não
caia no mesmo buraco em silêncio.

## 6. Documento materializado

```text
PONTUADA    Peso · Nota mínima · Pontuação máxima · Avaliações por inscrição
DECISORIA   Peso · Avaliações por inscrição · Resultado: Deferido / Indeferido
```

O documento imprime os rótulos publicados. Sem isso, a fonte estruturada e o PDF divergem, e o
candidato lê um Edital que não diz como sua Etapa é concluída.

## 7. O que **não** muda

Nenhuma rota nova, nenhum caminho alterado, nenhuma permissão nova, nenhum ato administrativo novo.
`resultado:consolidar` continua sendo o nome canônico do ato da 013, e a autorização das duas
features é a que já existe.
