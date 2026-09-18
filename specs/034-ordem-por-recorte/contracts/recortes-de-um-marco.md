# Contrato — o conjunto de recortes de um marco

**O que este contrato prende**: dado um Perfil e um marco do conteúdo publicado, **quais recortes
existem** — e que a resposta seja **uma só** para quem ordena e para quem apura (`FR-491`,
`SC-172`).

---

## A regra

```
recortes(perfil) =
    [ (NULL, "ampla concorrência") ]
  + [ (id, nome) para cada Modalidade declarada no Perfil
        EXCETO aquela que o Perfil aponta como sendo a ampla concorrência ]
```

**A exclusão não é detalhe de apresentação.** A quantidade da Modalidade declarada como ampla **é** a
da linha geral do Quadro de Vagas. Dar-lhe recorte próprio declararia duas vezes o mesmo número — e
emitiria uma ordem que a apuração não tem linha para consumir.

## Por que é esta regra, e não a outra que existe

Três módulos tratam a Modalidade declarada como ampla, e **não concordam**:

| Módulo | Trata como | Consequência |
|---|---|---|
| Ocupação | **não é recorte** | a linha geral responde por ela |
| Corte | é recorte, **e é apelido** — pedir por ela devolve a linha geral | mesma quantidade, dois nomes |
| Sorteio | **recorte próprio** | oferece um recorte que a ocupação não consome |

A regra acima é a da **ocupação**, e ela foi escolhida por um motivo verificável: **é a cauda que
consome a ordem**. Emitir para um recorte que a apuração não enxerga produz ato publicado que não
leva a lugar nenhum — uma versão pior do `ACH-47`, com a aparência de conserto.

O corte é compatível com ela: ele **aceita** o apelido se alguém o pedir, e nunca o **oferece**.

> **O sorteio fica como está, e a divergência fica registrada.** Alinhá-lo mudaria telas de uma
> feature que funciona e que esta spec declarou fora de escopo. É parada de escopo — `T004` — e não
> decisão de quem implementa.

---

## O que o contrato exige

1. **Uma função, um resultado.** Classificação e ocupação MUST obter o conjunto de recortes do mesmo
   lugar. Duas listas iguais hoje e derivadas em dois lugares divergem na primeira Retificação.
2. **A ordem é estável.** A ampla concorrência vem primeiro; as reservadas, na ordem em que o Perfil
   as declara. Ordem instável faz a navegação entre recortes trocar de lugar entre dois cliques.
3. **O rótulo diz o que o recorte é.** O da ampla diz que é a linha geral; cada reservada carrega o
   código que o Edital publica. É a lição que a `021` pagou: dois blocos homônimos e ninguém sabendo
   em qual agir.
4. **Modalidade que não está no Perfil não é recorte.** Pedir por ela é objeto inexistente
   (`FR-499`), e não recorte vazio — a diferença entre "não existe" e "existe e está vazio" é a
   mesma que a ordem vazia carrega, e confundi-las esconde erro de digitação.

## Como se verifica

Comparando **as duas listas**, para o mesmo marco, sem inspecionar como cada uma é produzida:

```
recortes derivados pela classificação  ==  recortes derivados pela ocupação
```

É o `SC-172`, e é verificação de igualdade — não de implementação.
