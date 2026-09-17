# Contrato — payload do rascunho

`replace_draft` **apaga e recria**: o payload substitui o conteúdo inteiro do rascunho. Este contrato
existe porque a revelação progressiva (FR-413 a FR-417) esconde campos, e campo escondido que não
volta no envio é campo perdido em silêncio — que é o que FR-418 proíbe.

## A regra

**Todo campo já declarado volta no envio, pertinente ou não.** O campo impertinente sai da tela e do
alcance do teclado; ele não sai do payload. Vai como `<input type="hidden">` com o último valor
declarado.

```html
<!-- marco POR_PONTUACAO que já foi POR_SORTEIO: o método sai da tela e fica no envio -->
<input type="hidden" name="marco-0-0-draw-algorithm" value="IFES-SORTEIO-SHA256-v1">
<input type="hidden" name="marco-0-0-draw-source"    value="Loteria Federal">
```

**`disabled` está proibido aqui.** Campo `disabled` não é submetido pelo navegador — usá-lo
reproduziria exatamente a perda que este contrato existe para impedir.

**`required` sai junto com o campo.** Campo obrigatório fora da tela é submissão que o navegador
recusa sem conseguir mostrar o que falta. A cobrança passa para a validação da publicação, que é
onde ela já mora para as Etapas do marco.

## A fronteira que precisa de teste

O valor guardado em campo oculto **não pode alcançar o conteúdo publicado**. Um marco que era de
sorteio e virou de pontuação guarda o método no rascunho e **não o publica**.

| Momento | O método impertinente |
|---|---|
| Rascunho gravado | **presente** — FR-418 exige que não se perca |
| Rascunho relido na tela | **presente e oculto** — reaparece se a forma voltar a ser sorteio |
| Conteúdo publicado | **ausente** — a validação da publicação o descarta |

Fechar só o primeiro caminho deixa o defeito vivo: é a lição que o assistente já aprendeu uma vez,
quando a perda tinha duas portas e só uma foi fechada.

## Campos novos no envio

| Nome | Origem | Obrigatório |
|---|---|---|
| `marco-{i}-{s}-orderProduction` | a pergunta de entrada de FR-413 | sim, em marco novo |

A resposta a FR-413 governa quais campos o fragmento seguinte renderiza. Ela viaja no envio como
qualquer outra declaração — sem ela, o marco recém-acrescentado não sabe o que perguntar.
