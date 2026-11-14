# Contrato: frases da regra

`F` é o rótulo favorável publicado e `D` o desfavorável; sem rótulo, *favorável* e *desfavorável*.
`N` é o número de pareceres previsto.

## A regra, na composição (UX-750)

| Regra | Opção |
|---|---|
| `MAJORITY` | Resultado «F» quando a maioria dos pareceres for «F» |
| `UNANIMOUS_FOR_FAVORABLE` | Resultado «F» só quando todos os pareceres forem «F» |
| `UNANIMOUS_FOR_UNFAVORABLE` | Resultado «D» só quando todos os pareceres forem «D» |

Sem rótulo digitado, a opção diz *favorável* e *desfavorável* sem aspas: "Resultado favorável quando a
maioria dos pareceres for favorável". Os rótulos entram nas opções quando o cartão é relido.

Pergunta: *Como a comissão chega ao resultado?* Ao lado da maioria, com `N` par: *exige número
ímpar de pareceres*.

## A regra, no documento, na Revisão e na Retificação (FR-7075)

> Cada inscrição recebe «N» pareceres, registrados por membros da comissão sem conhecer o dos
> demais. «Frase da regra».

| Regra | Frase da regra |
|---|---|
| `MAJORITY` | O resultado é «F» quando a maioria dos pareceres é «F», e «D» nos demais casos. |
| `UNANIMOUS_FOR_FAVORABLE` | O resultado é «F» só quando todos os pareceres são «F», e «D» nos demais casos. |
| `UNANIMOUS_FOR_UNFAVORABLE` | O resultado é «D» só quando todos os pareceres são «D», e «F» nos demais casos. |

Na Revisão, a linha se chama *Deliberação*.

## O motivo do Resultado deliberado (FR-7066)

```text
a comissão deliberou «desfecho» «por maioria | por unanimidade»: «k» de «N» pareceres «desfecho»
```

- maioria: *por maioria*;
- unanimidade que exige todos no sentido do desfecho: *por unanimidade*;
- desfecho no sentido oposto ao da unanimidade exigida: *por não haver unanimidade «F|D»*. Exemplo:
  sob `UNANIMOUS_FOR_FAVORABLE`, dois «F» e um «D» dão *a comissão deliberou «D» por não haver
  unanimidade «F»: 1 de 3 pareceres «D»*.

Na retirada da reserva, a `164` acrescenta `; deixa de concorrer pela reserva … e continua na ampla
concorrência`.

## Conferência da consolidação (UX-752)

```text
«desfecho» — «k» de «N» pareceres «desfecho», «por maioria | por unanimidade | por não haver unanimidade»
```

## Mesa (UX-751, UX-754)

- *Os demais membros não veem o seu parecer, e você não vê o deles.*
- Junto do parecer, na colegiada: *Se o parecer for «D», o candidato o lê sem o seu nome. Não escreva
  nele o seu nome, a sua assinatura nem outro dado que identifique você.*

## Julgamento

Na Etapa colegiada, no lugar da opção de reavaliação: *A reavaliação determinada não está disponível
contra o Resultado de uma Etapa colegiada. Decida por correção fixada, informando o desfecho.*
