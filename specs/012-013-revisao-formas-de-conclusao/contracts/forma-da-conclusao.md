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

Na forma pontuada, `forma` é o literal `"PONTUADA"` e os dois rótulos são `null`. Em conteúdo na
versão canônica 5, `forma` **não existe** e é lida como pontuada pelo leitor legado — o que **não**
autoriza `null` num snapshot v6.

`schemaVersion` da raiz passa a `6`.

### Obrigatoriedade e nulabilidade

No conteúdo publicado não há campo opcional: obrigatório significa **presente**, e não preenchido.
Os três são obrigatórios; só a nulabilidade os separa.

| campo | `required` | nulo admitido | análogo existente |
|---|---|---|---|
| `forma` | sim | **não** | `eliminatory` |
| `rotuloFavoravel` | sim | sim | `minimumScore` |
| `rotuloDesfavoravel` | sim | sim | `minimumScore` |
| `minimumScore` | sim | sim | — |
| `maximumScore` | sim | sim | — |

**"Proibido" significa `null`, e nunca ausente.** Toda chave da Etapa está sempre presente no
conteúdo publicado — `required == properties` é invariante conferida por
`test_forma_publicada.py::test_todo_campo_do_conteudo_publicado_e_obrigatorio`. O que a forma decisória
proíbe é o **valor**, não a chave.

Os literais do enum são exatamente `PONTUADA` e `DECISORIA` — maiúsculas, sem acento. Os do sentido,
em toda a superfície de escrita, são exatamente `FAVORAVEL` e `DESFAVORAVEL`.

### Entrada — `EtapaInput`

A elaboração é o único lugar em que a ausência de `forma` é aceita, e ela **não** significa a mesma
coisa que `null`:

| envio | resultado |
|---|---|
| `forma` omitida | vale `PONTUADA` — é a compatibilidade de quem já integrava com a API |
| `forma: null` | **recusado**: nulo não é uma forma, e aceitá-lo devolveria o `NULL` que o modelo proíbe |
| `forma` fora do enum | recusado |

No esquema, isso é: `forma` em `properties` de `EtapaInput` como `type: string` com `enum`, e **fora**
de `required` — que hoje é `[id, name]`. Assim a omissão é legal e o `null` é recusado pelo próprio
contrato, e não apenas pelo serializer. Os dois rótulos entram como `type: [string, 'null']`, também
fora de `required`.

O caminho de rascunho não converte ausência em `None` ao gravar; escrever `None` contornaria o
`default` do modelo pela porta dos fundos.

### Recusas do contrato

Códigos como `editais/domain/validation.py` os declara. Todas são `BLOCKING_ERROR` e carregam o
caminho do campo.

| situação | código | mensagem (forma) |
|---|---|---|
| `forma` ausente | `field_required` | aponta `/stages/<i>/forma` |
| `forma` nula | `field_null_invalid` | "O campo não admite valor nulo em …" |
| `forma` fora do conjunto | `field_constraint_violated` | "O campo admite apenas PONTUADA, DECISORIA em …" |
| `DECISORIA` sem rótulo | `field_constraint_violated` | "A Etapa decisória deve publicar os rótulos do resultado em …" |
| `PONTUADA` com rótulo | `field_constraint_violated` | "A Etapa pontuada não publica rótulos de resultado em …" |
| `DECISORIA` com `minimumScore` ou `maximumScore` | `field_constraint_violated` | "A Etapa decisória não publica nota em …" |

**Rótulo em branco não é rótulo.** String vazia ou só com espaços é recusada como ausente, e não
aceita como publicada: um Edital que publicasse `""` como rótulo do indeferimento produziria uma tela
e um PDF sem palavra nenhuma para o candidato ler. A recusa é `field_constraint_violated`, e a
normalização é a mesma que o projeto já aplica a texto publicado.

## 2. `POST .../inscricoes/<inscricao_id>/avaliacao` — rascunho

| forma da Etapa | campos aceitos | campos recusados |
|---|---|---|
| `PONTUADA` | `pontuacao`, `parecer`, `revision` | `sentido` |
| `DECISORIA` | `sentido`, `parecer`, `revision` | `pontuacao` |

O rascunho aceita o campo da forma **vazio** — quem está no meio do trabalho ainda não decidiu. O
que ele não aceita é o campo da outra forma, e a recusa é do domínio, com mensagem: ignorar em
silêncio faria a tela decidir uma regra normativa (012, FR-122).

**A forma da recusa é a que a Mesa já usa**, e não uma nova: `DomainError` com `status = 422` e
`campo` preenchido, que o canal HTML converte em aviso de erro na própria tela, preservando o que foi
digitado. Nenhum código HTTP novo entra por esta revisão; `404` continua reservado à autorização
composta, e a recusa por revisão obsoleta continua sendo a que já existe.

## 3. `POST .../inscricoes/<inscricao_id>/avaliacao/concluir`

Além do que já valia — reconhecimento explícito da versão (FR-073), revisão esperada (FR-081):

| forma | exigido | recusa quando falta |
|---|---|---|
| `PONTUADA` | `pontuacao` dentro do publicado | "Informe a pontuação." |
| `DECISORIA` | `sentido` ∈ {favorável, desfavorável} | "Informe o sentido da decisão." |
| `DECISORIA` ∧ `DESFAVORAVEL` | `parecer` não vazio | a recusa nomeia o rótulo publicado |
| `PONTUADA` ∧ eliminatória ∧ abaixo da mínima | `parecer` não vazio | inalterada (FR-034) |

O valor enviado em `sentido` é o literal `FAVORAVEL` ou `DESFAVORAVEL`; qualquer outro — inclusive o
rótulo publicado, enviado no lugar do enum — é recusado. Na tela, o par de opções é **rotulado** pelo
Edital — "Deferido" e "Indeferido" — sobre valores que continuam sendo os do domínio.

Parecer só com espaços conta como vazio, pela mesma normalização que a forma pontuada já aplica.

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
