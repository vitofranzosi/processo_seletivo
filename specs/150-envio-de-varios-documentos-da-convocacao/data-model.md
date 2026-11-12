# Data Model: O envio de vários documentos da convocação (150)

**Nenhuma entidade, coluna, tabela ou migration nova.** As tabelas append-only continuam 58, e a
segunda passada do provisionamento continua `58 de 58`.

Cada documento do lote é uma `ApresentacaoDeDocumento` da `115`, criada pelo comando
`convocacao.application.documentos.apresentar`, com a validação, o prazo, a trilha (`APRESENTAR`) e
o resumo (`content_hash`) de hoje. O lote não existe no banco: é uma sequência de atos independentes.

## O que se lê, sem consulta nova

| Dado | De onde | Para quê |
|---|---|---|
| `content_hash` da apresentação vigente de cada item | `item.lido.vigente`, já no *prefetch* da projeção (`portal/obrigacoes.py`) | `data-resumo-recebido` do cartão (FR-5615, R-005) |
| nome do documento | `item.nome` | `data-documento` e o texto do aviso |
| limite do arquivo | `ARQUIVOS_CANDIDATOS_LIMITE_BYTES` | `data-limite-em-bytes`, para não enviar o que passa do limite (R-009) |

A apresentação aproveitada da inscrição (`documento_da_inscricao`) ou de outra chamada
(`apresentacao_de_origem`) tem o mesmo `content_hash` da origem — o gatilho da `0005` da convocação
o exige —, e entra na comparação como qualquer vigente.

## O estado da volta, na sessão do Django

As duas chaves de hoje mudam de forma; nenhuma chave nova (R-003).

```text
confirmacao_da_convocacao = {
  "inscricao": "<uuid>",
  "total": n,                       # documentos tentados no lote; 1 no envio individual
  "envios": [                       # na ordem em que chegaram
    {"item_id": "<uuid>", "apresentacao_id": "<uuid>", "ja_recebido": bool},
    ...
  ],
}

recusa_da_convocacao = {
  "inscricao": "<uuid>",
  "recusas": [{"ancora": "item-<uuid>", "frase": "<recusa de hoje>"}, ...],
}
```

- A posição `1/n` do cabeçalho zera as duas; cada resposta acrescenta a sua.
- A leitura (`_da_inscricao`) continua consumindo **uma vez** e só na convocação da mesma inscrição.
- A forma antiga — um envio sem lista, uma recusa sem lista — é lida como lista de um, para a
  sessão aberta durante a implantação.

## O estado no navegador, só em memória

| Estado | Onde | Vida |
|---|---|---|
| arquivo escolhido em cada cartão | o `input[type=file]` | até o envio, a remoção ou a navegação |
| resumo calculado do escolhido | variável do script, por campo | idem; descartado se a escolha mudar durante o cálculo |
| progresso do lote (k de n, recebidos, recusados) | variável do script | até a navegação de volta |

Nada em `localStorage`, `sessionStorage`, IndexedDB ou cookie (FR-5611); o guardião
`tests/test_armazenamento_no_navegador.py` alcança o script novo.

## Transições do cartão, com script

```text
vazio ──escolher──▶ escolhido ──(outro cartão escolhe)──▶ escolhido, N ≥ 2
  ▲                    │  │                                   │
  └──remover a escolha─┘  └──resumo coincide──▶ escolhido com aviso (não bloqueia)
                                                              │
                         enviar (qualquer cartão escolhido) ──▼
                                          enviando k de n ──▶ recebido | recusado | não enviado (queda)
```
