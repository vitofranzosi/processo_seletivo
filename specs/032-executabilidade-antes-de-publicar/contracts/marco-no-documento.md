# Contrato — a seção do marco no documento publicado

O documento do Edital é o que a candidata lê. Este contrato registra o que a feature acrescenta à
seção "Marcos classificatórios" e o que ela promete não tocar.

## Regra que governa tudo abaixo

**Documento publicado não se regenera.** Ele é composto no ato da publicação e guardado; mudar o
renderizador não alcança documento algum que já exista. Por isso `FR-469` é **conferência**, e o
risco real que ela cobre não é o renderizador — é um degrau de elevação acrescentado por engano, que
reescreveria conteúdo do acervo. **Nenhum degrau é acrescentado.**

**O conteúdo canônico não muda.** Esta feature lê `orderProduction` e `drawMethod`, que a `030` já
publica. Nenhuma chave nova entra no snapshot.

---

## A seção hoje

```text
CLASS-TUT — Classificação final
  Combinação:      soma ponderada da Etapa Análise Curricular (peso 1)
  Normalização:    nenhuma
  Arredondamento:  2 casas decimais, meio para cima
  Recurso:         admite, prazo de 5 dias corridos
  Corte:           quantidade fixa de 10, governa a Etapa Entrevista
  Critérios de desempate:
    1º maior pontuação na Etapa Análise Curricular
```

## A seção depois, num marco que ordena por pontuação

Um par novo, e nada mais. **Marco do acervo que não declara `orderProduction` não ganha o par
`Ordem` e sai exatamente como hoje.**

```text
CLASS-TUT — Classificação final
  Ordem:           pela pontuação combinada das Etapas
  Combinação:      soma ponderada da Etapa Análise Curricular (peso 1)
  …
```

## A seção depois, num marco que ordena por sorteio

`Combinação` e `Normalização` **desaparecem** — aquela ordem não vem de nota, e imprimi-las era o
que fazia o documento afirmar um método falso (`ACH-50`).

```text
SORT-X — Sorteio público
  Ordem:           por sorteio
  Arredondamento:  2 casas decimais, meio para cima
  Sorteio
    Método:        comum a este Edital
    Algoritmo:     IFES-SORTEIO-SHA256-v1
    Fonte:         Loteria Federal
    Ocorrência:    concurso 6100 da Loteria Federal
    Quando:        20/11/2026, às 20h
    Derivação:     o primeiro concurso realizado após a data programada do sorteio
    Semente:       os dígitos das cinco dezenas, em sequência
    Se faltar:     a ocorrência seguinte da mesma fonte
  Recurso:         admite, prazo de 5 dias corridos
  …
```

### `Método:` — as três grafias, e só três

| Situação | O que o documento imprime |
|---|---|
| o marco não declara método próprio, e o Edital declara o comum | `comum a este Edital` |
| o marco declara método próprio **diferente** do comum do Edital | `próprio deste marco — diverge do comum deste Edital` |
| o marco declara método próprio, e o Edital não declara comum | `próprio deste marco` |
| o marco declara método próprio **idêntico** ao comum | `próprio deste marco` |

**A quarta linha entrou na implementação** (18/09/2026), e o contrato estava errado: ele mandava
nomear a divergência sempre que houvesse os dois. A `FR-466` diz outra coisa — *"quando o marco
declara método próprio **divergente** do comum"* —, e um marco cujo próprio é igual ao comum não
diverge de nada. Escrever que diverge seria o documento afirmando uma diferença que ninguém
publicou.

A quarta situação — nem próprio, nem comum — **não chega ao documento**: `FR-467` a recusa na
publicação.

**A resolução é uma só.** O método impresso vem de `marcos.metodo_que_governa`, que é o ponto único
desde a `030`. Reimplementar a resolução no renderizador criaria a segunda leitura que a `030`
existe para não ter — e a divergência entre as duas apareceria como documento publicado dizendo uma
coisa e sorteio fazendo outra.

---

## Os rótulos

Saem de `CAMPOS_DO_METODO`, em `editais/domain/perfis.py`, onde os sete campos já estão nomeados em
português. O documento e a tela de composição dizem a mesma coisa com as mesmas palavras — é o
Princípio I, e é o que impede o documento de inventar um oitavo nome para a mesma coisa.

**A constante passou a trinca na implementação** (18/09/2026), e o contrato se contradizia sem que
ninguém percebesse: ele mostrava rótulos curtos no bloco acima e, três parágrafos abaixo, dizia que
eles saíam de `CAMPOS_DO_METODO` — cujas entradas eram frases de sessenta caracteres, escritas para
completar uma recusa (*"o método não declara `o algoritmo e a sua versão`"*). Como `_pares` alinha o
valor pela largura do rótulo, usá-las como rótulo desmontaria o bloco.

A saída não foi escolher um dos dois: foi acrescentar a terceira posição, `(campo, o_que_é,
rótulo)`. A frase continua completando a recusa, o rótulo encabeça a linha do documento, e os dois
saem do **mesmo lugar** — que é o que a frase acima promete e o que o Princípio I pede. Um oitavo
campo acrescentado ali aparece no documento sem ninguém precisar lembrar de acrescentá-lo aqui, e
um teste afirma que os sete rótulos aparecem.

**E a ocorrência saiu em dois pares, e não num.** O bloco de exemplo os fundia — `Ocorrência:
concurso 6100, de 20/11/2026 às 20:00` —, e a `FR-465` os lista separados. Separados, cada um dos
sete campos tem rótulo próprio e nenhum fica sem uso.

**O documento publica a norma, não o resultado.** Ele imprime a ocorrência que **fixará** a semente,
e nunca a semente: no dia da publicação ela ainda não existe. Quem publica a semente é o documento
do resultado do sorteio, que já o faz (`Algoritmo`, `Semente`), e a verificação pública compara os
dois.
