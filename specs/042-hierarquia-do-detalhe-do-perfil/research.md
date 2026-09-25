# Phase 0 — Pesquisa: a hierarquia do detalhe do Perfil

**Feature**: `042-hierarquia-do-detalhe-do-perfil` · **Data**: 2026-09-21

**Método**: medição no navegador, contra a `041` rodando. Nenhum `NEEDS CLARIFICATION` ficou aberto.

---

## R-001 — O controle não tem triângulo, e é por isso que lê como botão

> **A causa mecânica do que a revisão descreveu como *"`2 Perfis` parece um botão solto"*.**

**Medido**: `display: inline-block` no `<summary>`; `list-style-type` computado como
`disclosure-closed`; largura de **67 px**, com borda e fundo.

**O `display` trocado tira o elemento de `list-item`, e o marcador de divulgação simplesmente não é
desenhado.** A própria folha deste projeto já documenta a armadilha noutra regra: *"`display:flex`
no `summary` **apaga o triângulo** que o navegador desenha"*. A `041` caiu nela por copiar o padrão
de `.como-preencher>summary`, que é um bloco de ajuda — ali um botão é o que se quer.

**Decisão**: o controle volta a ter marcador. Duas saídas, e a escolhida é a segunda:

| Saída | Por que |
|---|---|
| Devolver `display: list-item` | recupera o triângulo nativo e perde o controle sobre a caixa; o marcador nativo varia muito entre navegadores |
| **Manter `inline-block` e desenhar o marcador**, com `▸`/`▾` em `::before` girando por `details[open]` | aparência estável, e é a que permite o rótulo relacional da `FR-629` |

**O marcador é decorativo e fica fora do nome acessível**: quem ouve a tela recebe o estado por
`open`, não pelo caractere.

---

## R-002 — Como ligar duas `<tr>` sem quebrar a tabela

> A incógnita estrutural desta feature, como o `<details>` dentro do `<td>` foi da `041`.

**Medido**: a tabela principal tem **um** `<tbody>` para todos os Editais, e a célula da expansão
tem `padding-left: 8px` — recuo nenhum, na prática.

**Decisão**: **um `<tbody>` por Edital.**

**Racional.** `<table>` admite vários `<tbody>`, e o significado deles é exatamente este: *grupo de
linhas*. Um Edital e a sua expansão **são** um grupo. Com a agrupação:

- o **separador** entre Editais passa a ser a borda do `<tbody>`, e não a da linha;
- **dentro** do grupo não há borda, e as duas linhas leem como um bloco;
- a régua vertical é `border-left` na célula da expansão, e o recuo é `padding-left` — **sem
  posicionamento, sem pseudo-elemento que precise alcançar a linha de cima**.

**As alternativas foram consideradas e recusadas.** Um `::before` posicionado com `top` negativo,
para a régua subir até a linha do Edital, funciona e é frágil: depende da altura da linha, que varia
com o título do Processo. E remover a borda da linha principal *condicionalmente* — só quando há
expansão — exigiria `:has()`, e deixaria o Edital sem conteúdo publicado sem separador nenhum.

**O caso vazio acompanha**: a linha de *"Nenhum Edital no período selecionado"* ganha o seu próprio
`<tbody>`, como qualquer grupo.

---

## R-003 — O rótulo que muda com o estado, sem JavaScript

**Decisão**: dois rótulos no `<summary>`, e `details[open]` alterna qual aparece.

```text
<summary><span class="ao-abrir">Mostrar</span><span class="ao-fechar">Ocultar</span> 2 Perfis de vaga</summary>
```

com `details[open] .ao-abrir{display:none}` e o simétrico. **Nenhum JavaScript** — é o que a
`FR-622` exige e o que a `G-003` da spec já antecipava.

**O que não fazer**: `summary::after { content: "Mostrar" }`. Conteúdo gerado por CSS **não é texto
do documento** e chega de forma inconsistente a leitor de tela; um rótulo de ação não pode depender
disso. O marcador `▸` pode, porque é decoração.

---

## R-004 — O que "parentesco perceptível" significa no telefone

**Decisão**: em largura estreita, **a régua fica e o recuo encolhe**.

**Racional**. A `FR-623` separa os dois casos de propósito, e a razão é medida: em 375 px a tabela
filha já rola dentro da moldura que a `040` criou. Cada pixel de recuo sai da leitura das métricas.

| | Desktop | Telefone |
|---|---|---|
| Régua à esquerda | sim | **sim** — custa 3 px e carrega o parentesco sozinha |
| Recuo | sim, confortável | **mínimo** |
| Mais estreita que a principal | **sim**, exigido | não exigido — a moldura já governa a largura |

**É o que impede a feature de melhorar o monitor piorando o telefone**, que foi a quarta correção da
revisão de 21/09.

---

## R-005 — A linha de identidade do Perfil

**Decisão**: uma linha secundária única, com os presentes separados por `·`, e **nada** quando não
há nenhum.

```text
Professor de Informática
DOC-INFO · Campus Serra · CR limitado a 6
```

**A composição mora no módulo, e não no template** (`FR-582` da `040`): decidir *quais* partes
existem e *como* se separam é regra, e regra em template é a segunda verdade que aquele requisito
proíbe. O template escreve o que receber.

**A ausência de reserva não produz texto** (`FR-626`): é a grafia que este repositório usa em
`especie_de_reversao` e em `requerimento_momento` — o vazio **é** a declaração de que não há.

---

## R-006 — A atenção nas duas granularidades

**Decisão**: `Marca` ganha um **rótulo curto** ao lado da mensagem. O Edital usa a frase com
denominador; o Perfil usa o rótulo.

| Onde | O que aparece |
|---|---|
| Edital | *"1 de 2 Perfis sem nenhuma inscrição"* — resumo **com** denominador |
| Perfil | *"Sem procura"* — rótulo curto |

**Dois campos, e não um derivado do outro.** Derivar o curto do longo por corte de string seria
frágil e ilegível; derivar o longo do curto perderia o denominador, que é a regra da casa. Os dois
nascem juntos, da mesma espécie.

---

## R-007 — Os dois controles de ordenação

**Decisão**: **critério** e **direção**, com o critério deixando de embutir direção.

| Controle | Opções |
|---|---|
| **Ordenar por** | Data do Edital · Vagas · Inscrições submetidas · Inscr./vaga |
| **Ordem** | Decrescente · Crescente |

**O defeito de hoje**: a primeira caixa oferece *"Mais recentes"*, que já é uma direção; combinada
com *"Menor primeiro"*, significa *"mais antigos"* — e ninguém lê assim.

**O select único foi considerado e recusado**: oito opções hoje, e dez quando a ocupação entrar.
Dois controles escalam; um cresce por multiplicação.

**A chave de consulta não muda** — `ordem=recentes` continua valendo, e o que muda é o **rótulo**.
Trocar a chave quebraria endereços que alguém já tenha guardado, sem ganho nenhum.

---

## O que esta pesquisa **não** encontrou

Nenhuma necessidade de JavaScript, de componente novo, de mudança de fórmula, de consulta nova ou de
reestruturar a tabela principal — os cinco sinais que a spec registrou como *"o plano saiu do
problema"*. A feature é folha de estilo, agrupação de linhas e composição de texto.
