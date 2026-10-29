# Contrato: as mensagens da extração inviável

**Feature**: [spec.md](../spec.md) | **Modelo**: [data-model.md](../data-model.md)

As frases abaixo são o contrato: os testes casam trechos delas, e a implementação pode ajustar a
pontuação, mas não o conteúdo. Os instantes saem por extenso no fuso institucional, no formato
`dd/mm/aaaa às HH:MM` que `_por_extenso` já usa (FR-2668). Entre chaves, o que é interpolado.

## 1. Achado de publicação, impeditivo (FR-2652, FR-2653)

Código `draw_occurrence_not_after_registration`. `{alvo}` é "O marco {nome do marco}" ou "O método
comum a este Edital".

> {alvo} declara a extração de {fonte} em {dia da extração}, e as inscrições terminam em {fim por
> extenso}. {fonte} publica só a data da extração, sem o horário, e a data vale a partir de 00h00:
> a relação de participantes precisaria ser congelada antes de {dia da extração}, mas ela só pode ser
> congelada depois do fim das inscrições. Com este cronograma, o sorteio será sempre recusado.
> Declare uma extração de dia posterior a {dia do fim}, ou encerre as inscrições antes de {dia da
> extração}.

## 2. Advertência na Retificação (FR-2656)

Código `draw_occurrence_not_after_registration_on_retification`. É a mesma frase, com a última
sentença trocada por:

> Se a relação ainda não foi congelada, esta Retificação pode declarar uma extração de dia posterior
> ao congelamento. Se já foi, a saída é retificar o método e depois publicar relação nova, sucedendo
> a atual.

## 3. Aviso antes de congelar (FR-2659)

Na tela do sorteio, uma vez por marco, antes dos botões "Publicar e congelar a relação" dos
recortes, com a classe `aviso` e `role="status"`. Enquanto as inscrições correm, ele aparece logo
depois do aviso de inscrições em curso, e "hoje" vira "depois do fim das inscrições" (FR-2651):

> **Congelar a relação hoje impede o sorteio com a extração declarada.** {fonte} publica só a data da
> extração ({dia da extração}), e a data vale a partir de 00h00. Uma relação congelada hoje nunca
> será anterior a ela, e o sorteio será recusado. Antes de congelar, retifique o método para uma
> extração de dia posterior ao do congelamento. Congelar não se desfaz.

Se quem vê pode retificar, "retifique o método" é um link para a Retificação, como o que a tela já
oferece para o método indefinido. Se não pode, a frase diz a quem pedir, como a tela já faz.

## 4. Diagnóstico da relação congelada (FR-2660, FR-2661)

Antes de "Realizar o sorteio", com a classe `erro`:

> **Esta relação não pode ser sorteada com a extração que o método dela declara.** Ela foi congelada
> em {publicada_em por extenso}, e {fonte} situa a extração a partir de 00h00 de {dia da extração}. A
> saída tem três passos, nesta ordem: (1) retificar o método para uma extração de dia posterior ao
> congelamento da relação nova; (2) publicar relação nova, sucedendo esta; (3) observar a ocorrência
> nova e realizar o sorteio. Suceder a relação sem retificar não resolve.

Quando o método vigente já difere do comprometido (FR-2661), a frase começa dizendo o que já foi
feito:

> **O método já foi retificado, e esta relação continua comprometida com o anterior.** Uma relação
> congelada não lê o método vigente. Falta publicar relação nova, sucedendo esta, e então observar a
> ocorrência nova.

## 5. Acréscimo à recusa `occurrence_precedes_freeze` (FR-2662, FR-2663)

A primeira frase da recusa não muda (R-007). Depois dela, nesta ordem:

- só quando a fonte publica só a data:

  > {fonte} publica só a data da extração, sem o horário: a data vale a partir de 00h00.

- sempre:

  > Suceder a relação sem retificar não resolve: a relação nova seria congelada ainda mais tarde.
  > A saída é retificar o método para uma extração de dia posterior, publicar relação nova sucedendo
  > esta, e então observar a ocorrência nova.

## Onde **não** aparece nada

- Fonte que publica a data e a hora (D-006), inclusive a `Fonte de demonstração` atual.
- Período de inscrições sem designação, sem término ou cancelado, ou com mais de um Evento marcado.
- Método com achado de forma, de fonte ou de instante.
- Ocorrência substituta: a regra de substituição não publica instante.
