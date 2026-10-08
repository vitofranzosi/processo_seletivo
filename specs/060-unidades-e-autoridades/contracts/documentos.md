# Contrato — o que os documentos dizem da unidade

Complementa o contrato da `054` ([documento-publicado.md](../../054-edital-como-ato-oficial/contracts/documento-publicado.md)).

## O cabeçalho, nos quatro documentos

```text
<brasão>
Ministério da Educação
Instituto Federal do Espírito Santo
<cabecalho[0] da Unidade>
[<cabecalho[1] da Unidade>]
```

As duas primeiras linhas são as mesmas para toda Unidade. As seguintes vêm da Unidade, na ordem e na
quebra em que foram registradas.

| Documento | De onde vem a Unidade |
|---|---|
| Edital publicado | Unidade do Edital no ato, congelada em `Publicacao.unidade_*` |
| Prévia do Edital | Unidade do Edital **registrada no momento** — não é ato |
| Consolidado da Retificação | Unidade congelada **na Retificação** (FR-1130) |
| Documento de resultado | `conteudo_publico.cabecalho.unidade` |
| Comprovante de inscrição (PDF e página) | `Publicacao.unidade_*` da `source_publication` da versão aceita (FR-1115) |

## O fecho, só no publicado

```text
<Unidade.local>, <data do ato por extenso>.
```

Emenda o item 7 do contrato da `054`, que trazia *"Vitória (ES)"* fixo. O resto do fecho e o bloco
da autoridade não mudam.

## O Cefor não muda

Para a Unidade `cefor` de `unidades.json`, o documento é idêntico, byte a byte, ao que o compositor
produzia com as constantes `ORGAO` e `LOCAL` (FR-1114). `documento_publicado_v1.pdf` não é refeito.
