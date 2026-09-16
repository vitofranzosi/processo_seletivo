# O `seed_demo` promete degradar com `--numero` não numérico, e não degrada

**Data:** 2026-09-15
**Origem:** revisão da `028`, que encontrou um `UnboundLocalError` no caminho não numérico e, ao
cobri-lo com teste, descobriu que o caminho já não chegava lá.
**Natureza:** defeito anterior à `028`, no comando de demonstração. O guarda que a revisão pediu
foi aplicado; o defeito de fundo fica registrado.

> **Não vira escopo por estar escrito aqui.** Este documento mede o que acontece e enumera saídas.
> Qual delas se toma — e se se toma alguma — é decisão do usuário.

## O que o comando promete

`_numero_do_segundo_edital` devolve `None` quando o número não é numérico, e a razão está escrita
na própria docstring:

> *"o segundo Edital é conveniência da demonstração, e inventar um identificador a partir de texto
> arbitrário produziria UUID inválido — melhor não criá-lo e dizê-lo do que falhar no meio."*

O `handle` obedece: imprime *"Número do Edital não é numérico: o segundo Edital, com resultado
divulgado, não foi criado"* e segue.

## O que acontece

O **primeiro** Edital já falha, antes de a mensagem poder ser impressa:

```
django.core.exceptions.ValidationError:
  ['O valor “00000000-0000-0000-00XY-0000000000b1” não é um UUID válido']
```

`perfis(numero)` — e também `etapas`, `documentos_exigidos` e `cronograma` — embutem o número no
identificador publicado, com a mesma forma `00000000-0000-0000-00<numero>-…`. O `--numero` não
numérico é inválido para **todos** os Editais da demonstração, e não só para o segundo.

Medido em 15/09/2026: `seed_demo --numero XY` não cria nada, e a saída é um traceback.

## Por que passou despercebido

Nenhum teste percorre o caminho. `tests/integration/test_seed_demo.py` sempre passa `--numero` de
dois dígitos, e o ramo `segundo is None` nunca foi exercitado — o que também explica por que o
`UnboundLocalError` que a `028` introduziu no mesmo ramo não derrubou a suíte.

## Saídas possíveis

| Saída | Custo | O que se perde |
|---|---|---|
| Recusar `--numero` não numérico no `add_argument`, com mensagem | pequeno | nada; a promessa da docstring deixa de existir, e o comando passa a dizer a verdade na entrada |
| Derivar os identificadores de um contador estável em vez do número | médio | a legibilidade dos UUID da demonstração, que hoje deixam ler o Edital de origem no identificador |
| Deixar como está | zero | a opção continua documentada e inoperante |

A primeira é a que menos promete. A `028` não a tomou porque o defeito é anterior a ela e a decisão
não é dela.

## O que a `028` fez

Inicializou `concluido = None` junto de `publicacao`, no mesmo ramo — o quarto Edital parte do
segundo e precisava saber que ele pode não existir. O guarda está correto e é barato, e permanece
válido para o dia em que o caminho não numérico funcionar.
