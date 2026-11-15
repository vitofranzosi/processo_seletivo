# Contrato: o inventário de conteúdo e a comparação

*O que a jornada de fotografia grava por estado e largura, e o que `comparar.py` lê. Um arquivo
JSON por estado e largura.*

## O inventário

```json
{
  "codigo": "O-06",
  "largura": 1440,
  "papel": "quem emite",
  "commit": "c0f715c9",
  "blocos": [
    {
      "id": "b:9f1c…:1",
      "texto": "Ocupação ainda não apurada.",
      "tag": "p",
      "classes": ["aviso"],
      "visibilidade": "visivel | recolhido | escondido",
      "item": "i:recorte:Lista reservada a pretos, pardos e indígenas",
      "caixa": [280, 412, 725, 24]
    }
  ],
  "quantidades": [
    {"numero": "3", "rotulo": "Publicadas", "item": "i:recorte:Ampla concorrência"}
  ],
  "acoes": [
    {"tipo": "link", "rotulo": "Ver o histórico deste recorte", "destino": "/gestao/editais/‹id›/marcos/‹id›/ocupacao/historico?lista=‹id›"},
    {"tipo": "form", "rotulo": "Apurar a ocupação deste recorte", "metodo": "post", "destino": "/gestao/editais/‹id›/marcos/‹id›/ocupacao/apurar", "campos": ["chave", "csrfmiddlewaretoken", "lista"]}
  ],
  "ordem_documento": ["b:…:1", "b:…:1"],
  "ordem_visual": ["b:…:1", "b:…:1"],
  "linhas": [{"bloco": "b:…:1", "maior_linha": 74}],
  "dobra": {"acao_principal": "Apurar a ocupação deste recorte", "acima": true, "anunciada": false},
  "violacoes_de_csp": []
}
```

**Regras.**

- `texto` é o `innerText` do bloco com os espaços colapsados, já normalizado (UUID, data, chave).
- `item` é o item da estrutura que contém o bloco, nomeado pelo texto do título, da legenda ou do
  rótulo dele: `i:recorte:…`, `i:processo:…`, `i:campo:…`, `i:form:…`, `i:lista:…`, `i:pagina`.
- `id` é o resumo de `texto` e `item`, mais o número da ocorrência, para que o mesmo texto em dois
  recortes sejam dois blocos.
- `acoes` inclui o texto de cada botão e o rótulo de cada link, e é a lista do FR-7710. Os campos
  ocultos entram pelo nome, e o valor só quando não for chave ou token.
- `visibilidade: recolhido` é o texto dentro de `details` fechado; ele conta como presente (FR-7711
  proíbe mudar o que já está recolhido, e não o recolhido em si).

## A comparação

`comparar.py <antes> <depois> <saida>` grava, por estado e largura, `<saida>/<codigo>/<largura>.json`
com os campos do [modelo de dados](../data-model.md#comparação), e um `resumo.md` com uma linha por
estado: passou ou não, e por quê.

**Falha de comparação, e não de estado.** Estado que existe numa pasta e falta na outra é erro do
script, e não aprovação. Inventário com `violacoes_de_csp` não vazio reprova o estado.
