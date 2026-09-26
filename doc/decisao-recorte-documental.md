# Decisão — o recorte do documento exigido

**Situação: decidida em 25/09/2026 — recomendações aceitas pelo usuário.** O texto das alternativas
fica como estava: é o registro do que foi pesado. A tabela final passa a dizer o que foi decidido, e
a spec [`044-recorte-transversal-documental`](../specs/044-recorte-transversal-documental/spec.md)
a cita sem rediscuti-la.

Evidência: [estudo de esforço](estudo-esforco-de-cadastro-2026-09-21.md) §5.9,
[achado do portal](achado-documento-condicional-no-portal.md) (#160),
[conferência do envio e da análise](conferencia-envio-e-analise-documental.md) (#165).

## O problema

Nos Editais da amostra, o mesmo documento é exigido "de todo candidato PcD", em todos os Perfis. O
produto só sabe dizer "PcD **deste** Perfil": no 140/2025 isso rendeu 112 linhas para 7 documentos.
Quando o operador tentou o atalho, "Todos os Perfis" com o PcD de um só, o PDF e o portal passaram a
dizer coisas diferentes. A #161 **conteve** isso, impedindo a publicação, mas não deu o atalho.

Há ainda os documentos que dependem de um atributo do candidato, e não da modalidade: sexo e idade
para o serviço militar, vínculo de servidor. Para esses, o produto não tem forma nenhuma.

## O que já está fixado

A [Constituição](../.specify/memory/constitution.md) resolve parte da pergunta antes dela:

- **"Cotas DEVEM ser definidas por Perfil."** A Modalidade continua sendo do Perfil. Mover a
  propriedade dela para o Edital está fora de questão.
- **"Documentos Exigidos PODEM variar por Edital, Perfil, modalidade, etapa e condição normativa."**
  O documento condicional está previsto; o que falta é a forma.
- **"O sistema DEVE reproduzir os documentos exigidos para cada Inscrição."** A conferência mostrou
  que hoje ele **recalcula** a lista, e que, quando o recorte está errado, recalcula errado.
- **Dados pessoais obedecem a necessidade e minimização**, e dado de saúde é sensível.

E o que o código já garante:

- O **código** da Modalidade é único dentro do Perfil e **estrutural**: não se retifica. A
  **denominação** se retifica.
- **Nada** confere que o código "PcD" signifique a mesma coisa em dois Perfis: denominação,
  percentual e fundamento podem divergir.
- Hoje há três leituras da "mesma Modalidade": o portal usa a identidade interna, o PDF usa a
  denominação, e a validação da #161 usa a denominação com o código como reserva.

---

## D1 — A identidade transversal da Modalidade

*Como dizer "a mesma Modalidade em todos os Perfis".*

| | A. O código, com regra de coerência | B. Uma categoria declarada no Edital | C. Nada transversal; só lote |
|---|---|---|---|
| **O que é** | O documento aponta um **código**; vale para a Modalidade daquele código em cada Perfil. Na publicação, um IMPEDE exige que o mesmo código tenha a mesma denominação em todos os Perfis. | O Edital declara uma lista de categorias (PcD, PPI…); cada Modalidade de Perfil aponta a sua; o documento aponta a categoria. | Continua Perfil × Modalidade. A tela oferece "aplicar a todos os Perfis" e gera uma linha por Perfil. |
| **Autoria** | 1 linha por documento. | 1 linha por documento, mais declarar as categorias e vincular cada Modalidade. | N linhas geradas; editar depois é editar N. |
| **Portal** | Aplica por código. | Aplica por categoria. | Como hoje. |
| **PDF** | Um grupo "Dos concorrentes em PcD". | Um grupo por categoria. | Um grupo por Perfil, ou o gerador aprende a fundir grupos iguais. |
| **Análise** | Lista por código; nada muda na Mesa. | Idem, por categoria. | Como hoje. |
| **Retificação** | O código é estrutural: o recorte não se desfaz por acidente. Renomear a denominação num Perfil só esbarra na regra de coerência. | Uma entidade nova com o próprio ciclo de retificação. | N alterações para uma mudança. |
| **Custo** | Um campo no Documento Exigido e uma regra de publicação. | Uma entidade nova no conteúdo, com vínculo em cada Modalidade. | Só tela, mas não resolve o PDF nem a Retificação. |

**O que a opção A exige decidir junto:**

- **A coerência cobre só a denominação**, ou também percentual e fundamento? Pela Constituição, a
  cota é do Perfil, e o percentual pode variar legitimamente. A recomendação é cobrir **só a
  identidade** (código ⇒ denominação), nunca os parâmetros da cota.
- **A ampla concorrência.** O recorte que o sorteio e o quadro usam é a linha geral, sem Modalidade,
  e não a Modalidade "AC" declarada. Um recorte transversal por código "AC" reabriria essa
  confusão. É preciso dizer se ele é proibido, ou se significa a linha geral.

**Recomendação: A.** O código já tem as duas propriedades que uma identidade precisa: é único no
Perfil e não muda depois de publicado. Falta afirmar que ele significa o mesmo em todo o Edital, e
isso é uma regra de publicação, não uma entidade. B é mais expressiva, mas cria um cadastro que
nenhum dos cinco Editais pediu. C reduz a digitação e deixa o resto do problema onde está.

---

## D2 — O documento obrigatório sob condição

*Quem declara a condição, e o que ela produz no envio e na análise.*

Primeiro, uma separação. **Condição de modalidade** ("só para quem concorre em PcD") é recorte, e
se resolve em D1. O que sobra aqui são as **condições sobre o candidato**: sexo, idade, vínculo.

| | 1. Informativa, verificada à mão | 2. Autodeclarada pelo candidato | 3. Derivada de dado estruturado |
|---|---|---|---|
| **Envio** | A condição aparece como texto; o documento é facultativo; nada bloqueia. | O candidato responde se a condição se aplica; se sim, o documento passa a obrigatório e bloqueia. | O sistema avalia um dado que já tem; se a condição vale, o documento é obrigatório. |
| **Congelado** | Nada além do que já se guarda. | A resposta, com a versão aceita. | O dado, que já é congelado. |
| **Análise** | O analista precisa saber, de fora, se a condição valia. | O analista vê a resposta ao lado do documento. | O analista vê o dado ao lado do documento. |
| **Dados pessoais** | Nenhum dado novo. | Um dado novo por condição, declarado. | Nenhum novo, se o dado já existir. |
| **Hoje** | É o "facultativo com instrução", com o custo medido: a instrução nem chega à Mesa. | Não existe. | Não existe para condição: os fatos declarados (`declaredFacts`) só servem ao desempate. |

**Sobre os fatos declarados como veículo da opção 2 ou 3.** Eles já são dado estruturado, declarado
por Perfil, exigido na inscrição e congelado no envio. O custo de usá-los:

- só admitem DATA e INTEIRO: "sim/não" exigiria um tipo novo;
- são por Perfil, e a condição costuma valer para o Edital todo, que é o problema de D1 outra vez;
- hoje servem ao desempate. Ligá-los à exigência documental é uma segunda responsabilidade, com o
  ciclo de retificação deles;
- "sexo" e "deficiência" são dados que a minimização obriga a justificar um a um.

A alternativa é uma resposta própria, por documento, que só existe quando o Edital declara a
condição. Ela é mais estreita e não se mistura com o desempate.

**Recomendação:** tirar as condições de modalidade daqui (D1), e tratar as condições sobre o
candidato **numa spec própria, depois**, com a opção 2 como candidata e com a avaliação de LGPD que a
Constituição exige de cada especificação. Adotar agora a opção 1 como estado assumido, com duas
correções que a conferência pede de qualquer jeito: a instrução chegar à Mesa, e o facultativo não
perder a marca na Revisão.

---

## D3 — O escape por Perfil × Modalidade

O recorte exato **continua** existindo, ao lado do transversal. Quando um Perfil for diferente, o
operador declara, para ele, os recortes que valem, em vez de "todos os Perfis, menos este".

**Não se propõe exceção negativa.** Nos cinco Editais, nenhum Perfil diverge dos irmãos em
Modalidades ou percentuais (estudo, §13, E2). O escape positivo cobre o caso quando ele
aparecer.

A combinação que a #161 recusa ("Todos os Perfis" + Modalidade de um Perfil) **continua recusada**.
Com a opção A de D1, a mensagem ganha uma terceira saída: "use a modalidade em todos os Perfis".

---

## D4 — O efeito das Retificações

1. **Inscrição já enviada.** Hoje ela guarda a versão aceita, e a Mesa recalcula a lista sobre essa
   versão. A conferência mostrou o custo: o que o portal dispensou por erro some também da análise.
   **Alternativa:** gravar na inscrição, no envio, a lista de documentos exigidos com a razão de cada
   um (todos, Perfil, modalidade, condição). É o que a Constituição pede com "reproduzir os documentos
   exigidos para cada Inscrição", e é o que daria à Mesa um "não se aplica" explícito.
   **Recomendação:** gravar a lista. Sem ela, qualquer mudança de recorte de D1 muda
   retroativamente a leitura das inscrições antigas.
2. **Recorte transversal (A).** O código não se retifica. Mudar a denominação num Perfil só esbarra
   na regra de coerência, e a correção passa a ser nos Perfis todos, na mesma Retificação.
3. **O resumo público** ("O que mudou") hoje omite a mudança de recorte (conferência, achados). Isso
   é defeito independente de D1: a correção cabe na fila das diretas, qualquer que seja a decisão.

---

## D5 — Aplicar a todos os Perfis ≠ mudar a propriedade para o Edital

- **Aplicar em lote** (estudo, E1) é uma operação de **tela**: copia um conteúdo para N Perfis. O
  conteúdo publicado continua por Perfil. Serve a requisitos, carga horária, remuneração, marcos.
- **O recorte transversal** (D1, A) é **norma**: uma linha, uma exigência, lida em cada Perfil. Não
  move a Modalidade de lugar; só diz a qual Modalidade de cada Perfil ela se refere.
- **Mudar a propriedade para o Edital** (estudo, E2) é redesenhar o conteúdo comum. Para
  Modalidades, a Constituição o impede; para o resto, é decisão que esta não toma.

**Recomendação:** a primeira spec faz **só o recorte transversal do documento**, e não o lote nem
E2. O lote é outra spec, que não depende desta.

---

## O que foi decidido

Em 25/09/2026, o usuário aceitou as recomendações acima, uma a uma.

| # | Pergunta | Decisão |
|---|---|---|
| D1 | Como identificar a mesma Modalidade em todos os Perfis? | Pelo **código**, com IMPEDE de coerência que cobre só a denominação, nunca percentual ou fundamento |
| D1a | O recorte transversal alcança a ampla concorrência? | **Não**: o código da Modalidade declarada ampla não pode ser recorte transversal |
| D2 | Como tratar condição sobre o candidato? | **Opção 1** como estado assumido, com as duas correções na fila das diretas; a opção 2 fica para spec própria, depois |
| D3 | Exceção negativa? | **Não**. O recorte exato Perfil × Modalidade continua como escape; a combinação que a #161 recusa continua recusada, e a mensagem ganha a saída "use a modalidade em todos os Perfis" |
| D4 | Congelar na inscrição a lista exigida? | **Sim**: no envio, a lista com a razão de cada documento; a Mesa e a consulta administrativa passam a lê-la |
| D5 | O que entra na primeira spec? | **Só** o recorte transversal e a lista gravada; a aplicação em lote é outra spec |

Duas correções não dependem de nada disto e vão para a fila das diretas:

- "O que mudou" passar a listar a mudança de recorte do documento.
- A instrução do documento chegar à Mesa, e o facultativo manter a marca na Revisão.
