# Phase 0 — Pesquisa: o Perfil de Vaga na visão institucional

**Feature**: `041-perfil-na-visao-institucional` · **Data**: 2026-09-21

**Método**: leitura do código e do HTML contra a spec. Nenhum `NEEDS CLARIFICATION` ficou aberto.
Um achado **corrige a redação de um critério** e está em `R-005`.

---

## R-001 — Onde `<details>` cabe dentro de uma tabela

> A única incógnita estrutural desta feature. As demais são aritmética.

**Decisão**: a expansão é uma **segunda `<tr>` por Edital**, com um `<td colspan>` único, e o
`<details>` vive dentro dessa célula. Sem JavaScript.

**O problema.** `<details>` **não é filho válido** de `<tr>` nem de `<tbody>`: os filhos de `<tr>`
são `<td>` e `<th>`, e nada mais. Pôr o `<details>` direto na linha produziria HTML que o navegador
reparenteia, e o resultado depende do navegador — exatamente a classe de defeito que não aparece em
teste de template e aparece em uma máquina só.

**Por que `<details>`, e não outra coisa.** Ele já é o padrão desta base — dez telas o usam —, e a
razão está escrita na própria folha: *"`details` abre por teclado e por toque"*. Ele satisfaz a
`FR-619` inteira de graça: operável por teclado, e o estado declarado no próprio elemento (`open`),
que é o que leitor de tela anuncia.

**As três alternativas, e por que não.**

| Alternativa | Por que não |
|---|---|
| `<details>` dentro da **primeira célula** da linha | é HTML válido, e o conteúdo fica preso numa coluna estreita; a expansão precisa da largura da tabela |
| Um `<tbody>` por Edital, com a segunda `<tr>` alternada por **checkbox + `:checked ~`** | funciona e é hack: exige controle escondido e rótulo falso, e a semântica que chega ao leitor de tela é pior que a de `<details>`, que o repositório escolheu de propósito |
| Abandonar a tabela e fazer um `<details>` por Edital | perde o alinhamento de colunas entre Editais, que é o que torna a tabela um instrumento de portfólio (`D-001` da spec) |

**O `colspan` já é vocabulário desta base** — `alocacoes.html`, `supervisao.html` e a própria
`visao_geral.html` o usam para a linha vazia.

**A tabela interna é tabela mesmo**, com `<caption>` nomeando o Edital e `<th scope="col">`: o dado
é genuinamente tabular — seis colunas por Perfil —, e transformá-lo em lista perderia o cabeçalho
que dá sentido a cada número.

---

## R-002 — *Em preenchimento* por Perfil

**Decisão**: `contagens_por_edital` passa a acumular rascunho **por Perfil**, na mesma consulta.

**Racional**. Hoje o `else` do laço soma tudo num contador só: `por_edital["rascunhos"] += …`. A
consulta **já traz** `profile_id` em cada linha — foi a decisão do numerador recortado da `040` que
a obrigou —, de modo que o dado está ali e é descartado. Passa a ser dicionário, e o total do Edital
é a soma dos valores.

**Nenhuma consulta nova, e nenhuma linha nova**: o `values(...).annotate(...)` é o mesmo.

---

## R-003 — A inscrição cujo Perfil não existe na versão vigente

**Decisão**: `vagas_do_conteudo` passa a devolver também o **conjunto de todos os Perfis** da versão
vigente, e não só o dos que publicam vaga; a diferença entre o total do Edital e a soma dos Perfis é
calculada e apresentada.

**Racional**. A Retificação remove Perfil, e a `Inscricao` guarda `profile_id` da identidade
**publicada** — que sobrevive à remoção. Sem o conjunto completo não há como distinguir *"Perfil sem
vaga imediata"* de *"Perfil que não existe mais"*: hoje o código só conhece `ids_com_vaga`, e as
duas situações caem no mesmo `else`.

**A diferença é declarada, e não escondida** (`FR-613a`). É a mesma disciplina das quatro ausências
da `040`: um total que não fecha com as partes, sem explicação, é pior que qualquer um dos dois
números sozinho.

---

## R-004 — A mensagem da marca do Edital

**Decisão**: a marca do Edital nomeia **quantos Perfis de quantos**, por espécie, **com o
denominador de cada uma** — e com **um** Perfil só ela usa a mensagem do próprio Perfil.

**Os dois denominadores são diferentes, e essa é a parte que se perde.** *Sem procura* conta sobre
**todos os Perfis vigentes**; *demanda abaixo da oferta* conta só sobre os que **publicam vaga
imediata**, porque os demais não têm denominador e não poderiam estar abaixo de coisa alguma. Num
Edital de cinco Perfis, três com vaga, dois dos quais abaixo: *"2 de 5"* é aritmeticamente
verdadeiro e institucionalmente enganoso — o certo é *"2 de 3 Perfis com vaga imediata"*.

**A síntese sem denominador foi considerada e recusada.** *"2 Perfis requerem atenção · 1 sem
procura · 1 abaixo da oferta"* lê melhor e esconde os dois denominadores — o que anda para trás numa
página cuja tese é que todo número traz o seu denominador dito.

**Racional**. *"2 de 3 Perfis com demanda abaixo das vagas"* é o que a revisão pediu e é acionável.
Mas *"1 de 1 Perfil sem nenhuma inscrição"* é aritmética falando com quem quer português: num Edital
de um Perfil só — o caso mais comum do acervo — a contagem não acrescenta nada ao que a mensagem já
diz.

**As duas espécies contam separado.** Um Edital pode ter um Perfil sem procura e dois com demanda
abaixo da oferta; colapsá-las numa contagem só perderia qual é qual, que é justamente o que a
expansão existe para responder.

---

## R-005 — O orçamento: a `SC-216` mede o que não pode ser medido como está escrita

> **Este achado corrige a spec.**

**O que a `SC-216` diz**: *"mesma contagem com e sem ela, e igual entre recortes de 3 e de 60
Editais"*.

**O problema**: a expansão é renderizada no servidor e **não tem um "sem"**. Não há requisição de
abertura — é `<details>`, não HTMX —, então o dado é computado sempre. A primeira metade do critério
não descreve uma medição possível.

**A propriedade que de fato importa é outra**, e é mais forte: *o custo não cresce com o número de
**Perfis***. Um Edital de 16 polos precisa custar o mesmo que um de 1.

**A redação correta**, que substitui a atual:

> A expansão **não acrescenta consulta**: a contagem é igual entre um Edital de **1 Perfil** e um de
> **12**, e continua igual entre recortes de 3 e de 60 Editais.

A segunda metade fica como está — ela já é medível e já tem teste na `040`.

---

## R-006 — Onde as derivações moram

**Decisão**: tudo em `interface/visao_geral.py`, que continua sendo o módulo de leitura da página.

Nasce uma forma — `PerfilDaLinha` — e uma derivação — `perfis_do_edital(conteudo, contagem)`. A
`LinhaDoEdital` ganha a coleção e a contagem da diferença; `_marcas` muda de nível.

**Nenhum módulo novo, nenhum app novo, nenhuma migration.** A feature é leitura, como a `040`.

---

## R-007 — Não há guardião de estrutura de tabela

**Medido**: `tests/interface/test_acessibilidade.py` tem vinte casos, e nenhum sobre aninhamento de
tabela, `colspan` ou validade de `<tr>`.

**Consequência para o plano**: o HTML inválido de `R-001` **não seria pego por teste nenhum**. Por
isso a escolha é a estruturalmente válida, e não a que "funciona no meu navegador" — e por isso o
plano prevê um caso que afirma que o `<details>` está dentro de um `<td>`, e não solto na linha.

*Não é guardião genérico de HTML: é a afirmação estreita sobre a estrutura que esta feature
introduz, no molde dos demais casos daquele arquivo.*

---

## R-008 — O controle de expansão não pode ser a linha

**Decisão**: o controle é elemento próprio, com nome acessível e `aria-expanded`; a linha inteira
**não** alterna a expansão.

**Racional**. Há um conflito normativo entre features: a `FR-600` da `040` manda a linha **levar ao
Edital**, e a `FR-606` desta manda a linha **expandir**. Juntas, autorizam uma linha que tenta as
duas coisas no mesmo clique — e aí o link some, ou a expansão exige um alvo que compete com ele.

**O desenho de `R-001` já separa os dois** — o `<summary>` vive na segunda `<tr>`, e o link do Edital
na primeira. O que faltava era o **requisito** que proíbe a implementação contrária, e é a `FR-620`.

---

## R-009 — Onde o filtro *Somente com atenção* entra na ordem

**Decisão**: é o **terceiro** degrau — depois dos relacionais e depois da situação do período.

**Racional**. A `FR-598` da `040` fixou dois degraus: relacionais antes de materializar, período
depois. A marca depende de razão e de contagem **por Perfil**, que só existem depois de ler o
conteúdo publicado: empurrá-la para o `SQL` é impossível, não caro.

Ela pode vir depois do período sem prejuízo — os dois operam sobre o mesmo conjunto já reduzido, e
nenhum depende do outro. A ordem entre eles é indiferente; o que **não** é indiferente é os dois
virem depois da materialização.

---

## Orçamento de consulta projetado

Igual ao da `040` — **cinco leituras, nenhuma nova**:

| # | Leitura | Muda com a `041`? |
|---|---|---|
| 0 | anos disponíveis | não |
| 1 | Editais do recorte | não |
| 2–3 | versão vigente por Edital | não |
| 4 | inscrições por Edital, Perfil e estado | **não** — a mesma consulta passa a acumular rascunho por Perfil |

O conteúdo publicado de cada Edital **já está em memória**, e é dele que saem denominação, vagas,
espécie de reserva e localidade de cada Perfil.
