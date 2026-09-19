# Phase 1 — Modelo de dados · 035 · Sorteio executável

**Nenhuma entidade nova. Nenhum campo novo. Nenhuma migration. Nenhum vocabulário alargado.** Este
arquivo existe para dizer o que **já existe** e passa a ter guarda, e para registrar o que foi
medido antes de se afirmar isso.

---

## O método do sorteio, campo a campo

Ele vive no **conteúdo publicado**, e não no relacional: é norma. Existe em duas posições — o método
**comum** do Edital e o método **próprio** do marco —, e as duas passam pela mesma conferência.

| Campo | Espécie | Quem determina a forma | Guarda hoje | Depois |
|---|---|---|---|---|
| `algorithm` | vocabulário **fechado** | o conjunto de algoritmos implementados | ✅ recusa o não publicado | **escolha na tela** (`FR-507`) |
| `source` | vocabulário **fechado** | o conjunto de fontes com adaptador | ✅ recusa a sem adaptador | **escolha na tela** (`FR-507`) |
| `occurrence` | livre, **forma restrita** | a regra de substituição: precisa terminar em número | ❌ **nenhuma** | **sexta guarda** (`FR-512`) + ajuda (`FR-508`) |
| `occurrenceAt` | livre, exige fuso | o domínio do instante | ✅ recusa sem fuso | inalterado — **é o modelo da ajuda** |
| `derivation` | **prosa normativa** | ninguém: é a frase que diz a norma | — | **inalterado** (`FR-510`) |
| `normalization.rule` | vocabulário **fechado** | as regras de normalização | ✅ | já é escolha |
| `substitutionRule.rule` | vocabulário **fechado** | as regras de substituição | ✅ | já é escolha |

**Cinco guardas existem. A sexta é a única que falta**, e é a do campo que quebra o sorteio.

### A distinção que o projeto já tinha escrito, e não tinha prendido

Está no `seed_demo` e nas fixtures do sorteio, nas mesmas palavras, em dois lugares:

> *"`occurrence` é a ocorrência **concreta** — o concurso —, e `derivation` é a **prosa** que explica
> como ela foi escolhida. Se `occurrence` fosse a regra em prosa, a escolha de qual extração observar
> voltaria para a mesa no dia do sorteio."*

`FR-510` transforma isso em requisito. Sem ela, a leitura da auditoria levaria alguém a "corrigir" a
prosa e a remover do Edital a frase que diz a norma em português.

---

## Os dois vocabulários fechados, e por que eles não crescem por Edital

| Vocabulário | Como cresce |
|---|---|
| Algoritmos | publicando **implementação, vetores normativos e contrato**. Trocar qualquer regra é publicar versão nova |
| Fontes | publicando **adaptador**. O nome determina de onde a semente vem |

**Declarar fora do vocabulário não é um formulário recusado — é um manifesto que mente.** O código
registra o custo nas duas: um Edital que declarasse um algoritmo não implementado faria quem
reimplementasse a partir do publicado chegar a outra ordem, e concluir, corretamente, que o sorteio
não confere.

É isso que torna a **escolha** melhor do que o texto validado (`D-002`): as duas recusam o valor
inválido, e só a escolha impede que ele seja escrito.

---

## A forma da ocorrência

Não é vocabulário fechado, e não pode ser: a referência é do Edital e da fonte, e enumerá-la seria
enumerar o futuro.

```
prefixo?  número
───────   ──────
"        " "5900"      ✅ deriva para 5901
"Concurso " "5900"     ✅ deriva para Concurso 5901
"0099"                 ✅ deriva para 0100 — a quantidade de dígitos é preservada
"concurso 6100 da Loteria Federal"   ❌ o número não está no fim
```

**O último é a forma que uma pessoa escreve**, e é a que está em três fixtures deste próprio
repositório. Ela repete a fonte, que já é um campo à parte, e põe o número no meio.

A ajuda da `FR-508` precisa dizer **só a referência**, e que a fonte já está declarada acima.

---

## O que não entra

- **Nenhum campo estruturado para a ocorrência.** Separar prefixo e número tornaria o conteúdo
  publicado dependente de uma decomposição que o Edital não faz, e a norma passaria a ter uma forma
  que ninguém escreve.
- **Nenhum afrouxamento da regra de substituição.** Procurar o número em qualquer posição resolveria
  a fixture e criaria ambiguidade onde há mais de um número — `"concurso 6100 de 2026"` derivaria
  para 2027.
- **Nenhuma migration.** O que muda é conferência e tela.
