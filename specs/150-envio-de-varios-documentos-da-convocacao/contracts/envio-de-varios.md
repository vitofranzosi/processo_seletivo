# Contrato: o envio de vários documentos da convocação (150)

Três superfícies: a requisição de cada documento do lote, a volta à convocação e a marcação do
cartão que o script lê. **Nenhuma rota nova.**

## 1. A requisição de um documento do lote

A rota de hoje, `portal:apresentar-documento-da-convocacao` (`POST`), com titularidade e CSRF de
hoje.

**Pedido**

| Parte | Valor |
|---|---|
| corpo | `multipart/form-data` do próprio formulário do cartão: `csrfmiddlewaretoken` e `arquivo` |
| cabeçalho | `X-Envio-De-Varios: k/n` — posição (1 a n) e total do lote; inteiros, `1 ≤ k ≤ n` |

Sem o cabeçalho — sem script, ou com N = 1 —, a resposta é a de hoje: `302` para `#confirmacao` ou
para `#item-‹id›` (FR-3870, FR-3871 da `121`). Cabeçalho malformado é tratado como ausente.

**Resposta, com o cabeçalho**

`200`, `application/json`, sempre que o comando decidiu sobre o documento:

```json
{"resultado": "recebido",     "ancora": "item-<uuid>", "volta": "<url da convocação>?lote=<n>#confirmacao"}
{"resultado": "ja_recebido",  "ancora": "item-<uuid>", "volta": "…#confirmacao"}
{"resultado": "recusado",     "ancora": "item-<uuid>", "frase": "<a recusa de hoje>", "volta": "…"}
```

- `recusado` cobre o arquivo ausente (*"Escolha um arquivo PDF antes de enviar."*), o arquivo
  inválido, o prazo decorrido, a chamada fechada e o documento já conferido — as frases de hoje, sem
  mudança.
- `volta` é a âncora do resultado **acumulado até ali**: `#confirmacao` se algum documento do lote já
  foi recebido; senão, o cartão do primeiro recusado. O script usa a `volta` da **última** resposta.
- O 404 do comando continua `404` (item inexistente, convocação invisível ao candidato).

**Resposta que não é JSON** — a página de acesso (sessão sem identidade), a 404, a 403 de CSRF, a 413
do proxy, a 5xx — encerra o lote no navegador (FR-5610): o script não navega, diz o que foi recebido
e o que não foi, com a frase de hoje para o acesso expirado (404 ou página de acesso) ou para a falha
genérica, e devolve o botão para os não enviados.

**Efeito na sessão**: ver [data-model.md](../data-model.md). `k = 1` zera as listas.

## 2. A volta à convocação

`GET` da convocação, com `?lote=n` ignorado pela view. Consome as duas chaves da sessão uma vez.

- **Algum recebido** (FR-5608): a confirmação diz *"Recebemos R de N documentos"* — com N = 1 e R = 1,
  a frase de um só, a de hoje —, lista cada recebido com data e hora, e, havendo recusados, diz
  quantos não foram recebidos, com um link para `#item-‹id›` de cada um. A próxima tarefa ou a
  conclusão vêm como hoje, do estado depois do último envio. O `ja_recebido` entra como recebido,
  com a frase de hoje para ele.
- **Cada recusado**: a recusa no cartão dele, `role="alert"`, `data-recusa`. `recusa.js` foca a
  primeira da página.

## 3. A marcação que o script lê

No `<li class="cartao-do-documento">`:

| Atributo | Quando | Valor |
|---|---|---|
| `data-documento` | sempre | o nome do documento |
| `data-resumo-recebido` | há apresentação vigente | `content_hash` dela, hexadecimal minúsculo |

Dentro do formulário (`form[data-envio]`), além do que já existe:

| Elemento | Marcação | Sem script |
|---|---|---|
| Remover a escolha | `<button type="button" data-remover-escolha hidden>` com nome acessível *"Remover a escolha: ‹documento›"* | oculto |
| Aviso do arquivo repetido | `<p data-arquivo-repetido hidden>` com `id`, citado no `aria-describedby` do campo; o anúncio é por região viva da página | oculto |
| Progresso do lote | o `.progresso` de hoje, com o texto *"Enviando k de n: ‹documento›… Não feche esta página."* | — |

Na convocação, antes do primeiro cartão com envio: `<noscript><p class="instrucao">…</p></noscript>`
com a frase da FR-5612.

## 4. As frases

| Situação | Frase |
|---|---|
| rótulo com N ≥ 2 | *Enviar os N documentos escolhidos* |
| anúncio da contagem | *N documentos escolhidos para enviar.* |
| progresso | *Enviando k de n: ‹documento›… Não feche esta página.* |
| arquivo repetido, escolhido | *Atenção: este arquivo é o mesmo que você escolheu para ‹documento›.* |
| arquivo repetido, enviado | *Atenção: este arquivo é o mesmo que você já enviou para ‹documento›.* |
| confirmação | *Recebemos R de N documentos.* |
| sem script | *Os documentos se enviam um de cada vez. Ao enviar um, o arquivo escolhido nos outros cartões não é guardado: escolha e envie um de cada vez.* |

Com mais de um documento coincidente, o aviso nomeia cada um, unidos por vírgula e "e".
