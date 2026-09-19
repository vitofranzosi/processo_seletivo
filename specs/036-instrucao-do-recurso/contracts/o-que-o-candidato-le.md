# Contrato — o que o candidato lê, e quando

**O que este contrato prende**: que o titular leia a razão da própria eliminação enquanto puder
recorrer, sem que nada de terceiro atravesse a tela (`FR-522` a `FR-526`, `FR-535`).

---

## As duas frases, e por que são duas

A tela **já** mostra uma. A feature acrescenta a segunda.

| | Exemplo | Origem |
|---|---|---|
| **motivo** | *"pontuação inferior à nota mínima da Etapa (45,0000 < 60,0000)"* | derivado da norma pelo sistema |
| **parecer** | *"o currículo não comprova os seis meses de experiência exigidos"* | escrito por quem avaliou |

**O motivo diz que a nota não bastou. O parecer diz o que faltou.** Um recurso se escreve contra o
segundo — ninguém contesta a aritmética.

**As duas ficam** (`FR-525a`). Substituir o motivo pelo parecer tiraria da tela o número que sustenta
a contestação; substituir o parecer pelo motivo é o estado de hoje.

## Quando aparece

```
desfavorável + prazo aberto            →  o parecer aparece
desfavorável + recurso NÃO decidido    →  o parecer aparece, mesmo com o prazo fechado
prazo fechado E sem recurso pendente   →  some, E a tela diz por quê
resultado favorável                    →  nada muda
sem parecer escrito                    →  a tela diz que não há
```

**A segunda linha é a que o `analyze` acrescentou.** Prender só ao prazo tirava o parecer de quem
recorreu enquanto o recurso dela corria — a pessoa que esta feature existe para servir, no momento em
que ela mais precisa.

**O terceiro caso é o que separa esta feature de um defeito.** Sumir em silêncio faria a pessoa
pensar que perdeu algo, ou que o sistema falhou. `FR-524` obriga a frase.

**O quarto existe de verdade**: a obrigatoriedade do parecer depende do caráter da Etapa e da forma
da avaliação. Calar sobre a ausência é pior do que declará-la (`FR-525`).

## Qual parecer

O da avaliação que **fundamenta o resultado contestável** — e não o estado de hoje de uma avaliação
reaberta depois. Quando houve reabertura, vale o que o ato citou, que é a doutrina que o produto já
aplica a ato histórico (`FR-523`).

## O que não atravessa

Nenhum nome, nenhuma nota alheia, nenhum parecer de terceiro, nenhuma avaliação de outra pessoa
(`FR-535`).

> **Atenção a uma frase que já está no código.** O comentário do bloco do acompanhamento diz *"Nada
> aqui é de terceiro: nenhum nome, nenhuma nota alheia, nenhum parecer, nenhuma avaliação."* O
> sujeito dela é **de terceiro** — e é isso que ela proíbe. Emendá-la faz parte desta feature, e a
> emenda MUST dizer a distinção entre **parecer de terceiro**, que continua proibido, e **parecer do
> próprio titular**, que é o que a feature entrega. Apagar a frase seria perder a regra.
