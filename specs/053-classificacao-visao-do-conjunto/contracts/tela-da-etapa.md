# Contrato — o que o template entrega ao script da etapa Classificação

O `classificacao.js` só lê o que está aqui, e o `vista-do-conjunto.js` só o que está na última seção.
Mudar um destes pontos no template exige mudar o script, e `test_visao_da_classificacao.py` prende
cada um.

## A etapa (`compor_classificacao.html`)

| Elemento | O que é |
|---|---|
| `form#formulario[data-rascunho][data-lista="#classificacao-perfis"]` | O rascunho local (R-009), só para quem pode compor. |
| `.pendencias` | O bloco das pendências da etapa, logo depois do `h2` (FR-966). |
| `#visao-da-classificacao.visao-dos-perfis` (vazio, `hidden`) | Onde a tabela entra. Antes do método comum (UX-127). `data-devolvido` quando a tela volta de um envio que não gravou. |
| `details` do método comum | Entre `#visao-da-classificacao` e `#classificacao-perfis`. |
| `#classificacao-perfis` | A lista dos cartões de Perfil. Só cartões dentro dela. |

## O cartão do Perfil

| Atributo ou elemento | Valor |
|---|---|
| `fieldset.linha.perfil#cartao-<id do Perfil>` | O cartão; âncora estável. |
| `<legend>` | `legenda_do_perfil` da `052`: `Perfil <código> — <localidade ou denominação>`. |
| `data-codigo`, `data-denominacao`, `data-localidade` | A identificação da linha. Os Perfis não se editam nesta etapa, e a linha não tem campo de onde lê-los. |
| `data-pendencias="N"` | Pendências da etapa com `/profiles/id=<id>` no campo (R-008). |
| `data-origem` (ausente quando não há) | A frase da origem, da Revisão (R-004). |
| `data-nao-salvo` (presente ou ausente) | O servidor devolveu os marcos deste Perfil diferentes do gravado (R-005). |
| `fieldset.marco` | Cada marco, na ordem do cartão. |

## O cartão do marco (`_marco.html`)

| Controle | O que a linha lê |
|---|---|
| `[name$="-code"]` do marco | O código do marco; vazio, *"sem código"*. |
| `select[name$="-orderProduction"]` com `data-resumo-<valor>` (`nenhuma` para o vazio) | A forma da ordem. |
| `[data-metodo-do-marco]` (o `fieldset` do bloco do método, só sob sorteio), com `data-resumo-proprio`, `-comum` e `-nenhum` | Próprio quando algum controle com nome ali dentro tem valor; senão, comum quando algum `[name^="edital-draw-"]` tem. |
| `select[name$="-cutTargetKind"]` com `data-resumo-<valor>`, e `[name$="-cutTargetCount"]` | O corte; a quantidade entra depois da frase da quantidade fixa. |
| rádios `[name$="-appealDeclaration"]` com `data-resumo`, e `[name$="-appealDurationDays"]` | O recurso; o prazo entra depois da frase de *admite*. |
| `fieldset.criterio`, com `select[name$="-type"]` (`data-resumo-<valor>`) e `select[name$="-target"]` | Cada critério: o sentido e o rótulo da opção escolhida do alvo. |

As frases de `data-resumo-*` são as mesmas do `resumo-do-bloco` de cada bloco; o valor vai em
minúsculas no nome do atributo, como na `052`.

## O que o `vista-do-conjunto.js` recebe de cada tela

```text
VistaDoConjunto.montar({
  lugar,        // o contêiner vazio da tabela
  lista,        // o contêiner dos cartões
  item,         // o seletor do cartão dentro da lista
  contador,     // opcional: o contador de hoje, oculto quando há tabela
  noticia,      // o seletor do que a tela devolvida traz no alto, e para onde ela rola
  legenda,      // (quantos) → o texto do caption
  colunas,      // [[chave, rótulo, classe?]]
  ler,          // (cartão) → { codigo, rotulo, titulo, celulas: {chave: texto | [texto]} }
})
```

Ele cria, e nunca com `name`: a `table` dentro de `div.tabela-rolavel`, com `caption`, `th[scope=col]`,
`th[scope=row]` com o código e um `button[type=button]` *Editar* por linha; o cabeçalho do editor,
imediatamente antes da lista, com o título (`tabindex="-1"`) e três `button[type=button]`. Uma célula
cujo valor é lista recebe um `div` por item. Ele põe `hidden` nos cartões fora de vista,
`aria-current="true"` na linha em edição, e `open` no `details` fechado que contém um controle inválido.
