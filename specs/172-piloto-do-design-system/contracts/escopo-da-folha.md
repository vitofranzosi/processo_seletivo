# Contrato: o escopo da folha do piloto

*O que `interface/grupos/piloto-ds.css` pode e não pode fazer. Serve à revisão de código. Nenhum
teste novo o cobra (D-009). A medida que o confere é o SC-2602.*

## Pode

- Declarar regras cujo seletor **começa** por `.piloto-ds` (o contêiner) e só alcançam descendentes
  dele.
- Usar os tokens de `tokens.css`, os existentes e os acrescidos pelo piloto.
- Desfazer, sob o escopo, as medidas de leitura da `main` e a da P0 na confirmação, para que a prosa
  ocupe a largura do conteúdo (FR-7704 e FR-7730, revistas pela D-012).
- Dar ao `.acao` e ao `.botao` **dentro do escopo** a altura única (40 e 32 px) e o
  `display:inline-flex` (FR-7705).
- Usar `@media` e `@container` para as composições, a partir das larguras do `03-design-system.md`.

## Não pode

- Seletor sem `.piloto-ds` no início, inclusive `:root`, `html`, `body`, `main` e `*`.
- Valor literal de cor (`#`, `rgb(`, `hsl(` ou nome de cor): cor só por token.
- `font-family`, `font-size` ou `line-height` diferentes dos que o elemento já tem (FR-7712). A
  altura de linha fixa do botão é a única exceção, e só nele.
- Esconder texto: `display:none`, `visibility:hidden`, `clip`, `font-size:0`, `opacity:0`, altura
  zero com `overflow:hidden` ou recolhimento, sobre qualquer elemento com texto (FR-7711).
- `content:` com texto, porque o texto gerado não está no template e não seria igual antes e depois.
- `order`, `flex-direction: *-reverse` ou `grid` com posições que invertam uma sequência declarada na
  ordem visual sem invertê-la no documento (FR-7714). Mudar a ordem visual fora das sequências é
  permitido, e fica registrado.
- `position:fixed` ou `sticky` que cubra o foco (FR-7725).
- `}}` ou `%}` em qualquer lugar da folha, nem em comentário: o guardião de estáticos os lê como
  sintaxe de template.

## Os templates

- O contêiner é `<div class="piloto-ds">`, aberto logo depois de `{% block conteudo %}` e fechado
  antes do `{% endblock %}`.
- Nenhum `style=`, `<style>`, `<script>` nem `on*=`.
- Toda classe nova citada tem regra na folha do piloto, no mesmo commit.
- Nenhuma classe que já existe sai do elemento em que está.
