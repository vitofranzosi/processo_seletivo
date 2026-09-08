# Achado — o Anexo publicado não diz a quem serve

Encontrado em 08/09/2026, olhando a página pública da seleção com a `020` já na `main`.

> **Não é defeito, e não vira escopo por estar escrito aqui.** O que se registra é o que a tela
> não diz, por que isso é uma pergunta legítima, e as decisões que uma spec teria de tomar.
> Priorizar é do usuário.

## O que se observou

Em `/selecoes/<id>/`, o Edital 01/2026 lista dois anexos:

```
Anexos do Edital
  ANEXO I — AUTODECLARAÇÃO ÉTNICO-RACIAL          (PDF, baixar)
  ANEXO II — DECLARAÇÃO DE ANUÊNCIA DA CHEFIA IMEDIATA  (PDF, baixar)
```

Mais abaixo, nos cartões das vagas, o **ANEXO I** reaparece: ele é o modelo do Documento Exigido
"Autodeclaração étnico-racial", pedido de quem concorre em Pessoas pretas, pardas e indígenas.

O **ANEXO II não reaparece em lugar nenhum.** Nenhuma vaga o exige, nenhum requisito o cita.

## Por que isso não é defeito

Anexo e Documento Exigido são coisas diferentes, e nenhuma implica a outra:

| | O que é | Direção |
|---|---|---|
| **Anexo do Edital** | documento em forma própria que o Edital publica | o Edital entrega ao candidato |
| **Documento Exigido** | arquivo que a inscrição pede | o candidato entrega ao Edital |

Um requisito **pode** apontar um anexo como modelo (`documentRequirements[].attachmentId`), e é o
que o ANEXO I faz. Mas as quatro combinações são todas legítimas, e o Edital 01/2026 exibe três:

- anexo que é modelo de requisito — ANEXO I;
- anexo que não é modelo de nada — ANEXO II;
- requisito sem forma própria — diploma, identidade, que é o caso mais comum de todos.

O `seed_demo` cria os dois anexos exatamente para demonstrar as duas primeiras
(`seed_demo.py:441`). Um Edital real publica anexos que ninguém devolve o tempo todo: modelo de
recurso, formulário de solicitação de atendimento especial, tabela de pontuação de títulos. Eles
existem **à disposição de quem for o caso**, e o caso pode nem ocorrer.

## O que a tela pública não diz

Ela lista os anexos e para por aí. Quem lê não tem como saber, sem abrir cada PDF:

- se aquele anexo é o formulário de algo que **vai lhe ser cobrado**, ou
- se está ali à disposição para uma situação que talvez não seja a dele, ou
- se quem elaborou o Edital **esqueceu** de vinculá-lo ao requisito que o cita.

Os três estados se parecem na tela. A elaboração já os distingue — cada anexo mostra "Modelo de: …"
ou "Não é modelo de nenhum documento exigido", introduzido no polish da `020` —, mas essa
informação não atravessa para o lado público.

## O que uma spec teria de decidir

1. **O que dizer do anexo que é modelo.** "Modelo do documento *Autodeclaração étnico-racial*,
   exigido de quem concorre em Pessoas pretas, pardas e indígenas" é derivável do conteúdo
   publicado — o vínculo e o alcance do requisito já estão lá.

2. **O que dizer do anexo que não é modelo de nada.** Aqui não há informação a derivar: o sistema
   sabe que não há vínculo, e não sabe **por quê**. Escrever "não é modelo de nenhum documento
   exigido" na página pública seria expor vocabulário interno e sugerir defeito onde pode haver
   escolha editorial. As saídas plausíveis são um campo novo de finalidade — que é conteúdo
   normativo, e portanto Retificável e congelado — ou simplesmente não dizer nada.

3. **Se a ausência de vínculo merece aviso na elaboração.** Não na tela pública, mas na Revisão:
   "o ANEXO II não é citado por nenhum requisito — confira se é intencional". Seria um aviso, e
   nunca um impedimento, porque o estado é legítimo.

A decisão 2 é a que dá o tamanho: se a resposta for "campo novo de finalidade", isto deixa de ser
acabamento e vira alteração do conteúdo publicado, com elevação de `SCHEMA_VERSION` e degrau.

## O que não muda por enquanto

Nada. A `020` entregou o que prometeu, o comportamento observado é o correto, e a página pública
lista os anexos que o Edital publica — que é o que FR-039 pede.
