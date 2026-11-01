# Contrato: rotas do Kit de Divulgação

Todas as rotas ficam sob a gestão e seguem o roteiro de porta das views da gestão:

1. ator da sessão, ou pedido de identificação;
2. `obter_edital` filtrado pela unidade, ou **404** "não encontrado", no inventário da `033`;
3. base de permissão `material:gerar`, ou **403** com a recusa explicada;
4. Edital não publicado (`EM_ELABORACAO`, `EM_REVISAO`, `HOMOLOGADO`): **409** com o motivo
   "disponível depois da publicação", como o `INDISPONIVEL` da `099` (EC-1).

Toda resposta é privada (`Cache-Control: no-store`, `marcar_como_privada`). Encerrado e cancelado
passam da porta: a tela diz o motivo (EC-2, EC-3, FR-3445).

| Método | Caminho | Resposta | Registra |
|---|---|---|---|
| GET | `/gestao/editais/<uuid>/kit-de-divulgacao/` | 200 HTML, a tela (FR-3443). No modo "sem material": 200 com o motivo e a faixa da FR-3445, sem textos nem peça | Não |
| GET | `/gestao/editais/<uuid>/kit-de-divulgacao/previa.png?impressao=<sha>[&manchete=<n>]` | 200 `image/png`, `inline`. 409 se a impressão mudou (FR-3446). 404 com a peça desligada, recusada, em host local ou sem material | Não |
| POST | `/gestao/editais/<uuid>/kit-de-divulgacao/exportar/<formato>` (campos `impressao`, `manchete`) | 200, anexo (`Content-Disposition: attachment; filename="kit-NN-AAAA.<ext>"`) | Sim (FR-3436) |

**Formatos de exportação:**

| Formato | Tipo | Conteúdo |
|---|---|---|
| `png` | `image/png` | A peça |
| `svg` | `image/svg+xml` | A peça com a fonte embutida (D-021), sob `Content-Security-Policy: default-src 'none'; style-src 'unsafe-inline'; font-src data:` |
| `md` | `text/markdown; charset=utf-8` | Conferência, textos, notas |
| `txt` | `text/plain; charset=utf-8` | O mesmo, sem marcação |
| `zip` | `application/zip` | `kit.md`, `kit.txt`, `peca-feed-1080x1350.png`, `peca-feed-1080x1350.svg`, `texto-alternativo.txt`, `ficha.json`, `manifesto.json`. Sem peça (EC-21, recusa, host local), as três da peça não entram, e o manifesto diz por quê |

Todas levam `X-Content-Type-Options: nosniff`.

**Parâmetro `manchete`** (D-013): é o **índice** de uma das manchetes da lista fechada que a tela
ofereceu, e não texto. Ele é aceito só quando nenhum título oficial cabe. Índice fora da lista, ou
manchete fora desse caso, gera **422**.

**Recusas na exportação:**

| Situação | Resposta |
|---|---|
| Sem material (EC-2 a EC-4) | 409, com o motivo |
| Impressão diferente da conferida (EC-27) | 409, "o Edital mudou desde que você abriu o kit" |
| Peça pedida com a chave desligada ou em host local | 404 |
| Peça que não cabe ou com caractere sem grafia | 409, com o motivo nomeado; o ZIP sai sem a peça e diz isso |

**Host local** (FR-3447): `md`, `txt` e `zip` saem sem link absoluto, só com o caminho, e com a nota de
que o endereço público não é conhecido nesse acesso.

**O que nenhuma rota faz**: nenhuma altera Edital, Publicação, Retificação ou qualquer estado. A única
escrita é o evento da trilha.
