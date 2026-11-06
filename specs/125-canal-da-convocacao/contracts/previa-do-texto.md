# Contrato: o aviso e a prévia do texto que chega ao candidato

Incremento B (FR-3991 a FR-3997), com a D-004.

## Os sete campos

| # | Formulário (tela de condução, salvo indicação) | Campo | Em lote | Passo de conferência |
|---|---|---|---|---|
| 1 | Convocar os titulares | complemento do fundamento | sim | com texto |
| 2 | Convocar individualmente | complemento do fundamento | não | com texto |
| 3 | Convocar para regularizar | complemento do fundamento | não | com texto |
| 4 | Não atendimento dos vencidos | complemento do fundamento | sim | com texto |
| 5 | Registrar desfecho | fundamento | não | sempre (obrigatório) |
| 6 | Indeferir pelas pendências | fundamento do indeferimento (pré-preenchido) | não | sempre |
| 7 | Corrigir a convocação (`_correcao_da_convocacao.html`) | complemento do fundamento | não | na prévia da `120` |

## O aviso

Junto do rótulo, visível, fora de bloco recolhível, e com `id` citado no `aria-describedby` do campo:

> Este texto será mostrado ao candidato.

No formulário com fundamento derivado à vista, o derivado recebe o rótulo *"O candidato lerá este
fundamento"*.

## O passo *"Conferir o texto"*

- Aparece no lugar do formulário, na mesma tela, renderizado pelo servidor. Não usa script.
- Mostra, nesta ordem: o título *"Conferir o texto"*; a prévia, emoldurada como o portal a mostra; a
  frase *"Este texto será mostrado a N pessoas."* (*"a 1 pessoa"* no singular); o botão do ato, com o
  mesmo rótulo de hoje; e *"Voltar e corrigir o texto"*, que devolve o formulário preenchido.
- A prévia da convocação mostra *"Fundamento"* e o texto composto (derivado + complemento). A prévia do
  desfecho mostra a linha *"‹rótulo do desfecho›: ‹fundamento›"*.
- O bloco repassa `chave`, `alcance`, `lista` e as escolhas do formulário, e acrescenta
  `etapa=confirmar` e `texto_conferido`.

## A confirmação

| Situação | Resposta |
|---|---|
| `etapa=confirmar`, chave nova, alcance igual, texto igual | pratica o ato, como hoje |
| alcance mudou (lote) | recusa de hoje, nada registrado |
| texto composto diverge de `texto_conferido` | recusa com a prévia nova à vista, nada registrado |
| chave repetida | a resposta do ato original, como hoje |
| sem texto digitado (1 a 4) | pratica direto, como hoje |
