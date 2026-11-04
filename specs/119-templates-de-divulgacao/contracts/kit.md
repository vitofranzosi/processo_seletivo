# Contrato: o que muda nas rotas do kit

As rotas da `111` continuam, com os mesmos nomes, métodos, cabeçalhos e ordem de recusa (porta,
capacidade, estado, impressão). Muda o que elas aceitam.

## `GET /gestao/editais/<id>/kit-de-divulgacao/`

Aceita na consulta, todos opcionais: `familia`, `variante`, `imagem`, `manchete`. Sem eles, a
pré-escolha da última exportação (FR-3806).

Responde a tela com:

- o formulário de escolha (`GET` para a própria tela; funciona sem script);
- para cada formato da família: a prévia, o texto alternativo e os botões de exportação; ou o motivo
  da indisponibilidade ("em aprovação pela comunicação", recusa da composição);
- as faixas da `111`, mais "o título oficial não coube em: …" e "o contato não coube em: …".

Escolha fora da lista: a tela abre com a pré-escolha e diz que a escolha não está disponível; nada é
gerado.

## `GET /gestao/editais/<id>/kit-de-divulgacao/previa.png`

Acrescenta à consulta: `familia`, `variante`, `imagem`, `formato_da_peca` (D-012). Escolha fora da
lista, template não liberado ou composição recusada: 404, como hoje. Impressão divergente: 409.

## `POST /gestao/editais/<id>/kit-de-divulgacao/exportar/<formato>`

`<formato>` continua sendo o tipo de arquivo. Para `png` e `svg`, o corpo leva `familia`,
`variante`, `imagem`, `formato_da_peca`, `manchete` e `impressao`.

| Situação | Resposta | Registra |
|---|---|---|
| Escolha fora da lista (EC-9) | 400 com "a escolha não está disponível; abra o kit de novo" | não |
| Template não liberado (EC-7) | 409 com o motivo | não |
| Composição recusada | 409 com o motivo da recusa | não |
| Impressão divergente | 409 `kit_desatualizado` | não |
| Sucesso | anexo com o tipo e a CSP da `111` | sim, com o `detalhe` do data-model |

`zip`: leva a peça de cada formato liberado da família escolhida (FR-3829); formato recusado é
listado no manifesto com o motivo.

O inventário de negativas da `033` ganha a linha do 400 da escolha fora da lista.
