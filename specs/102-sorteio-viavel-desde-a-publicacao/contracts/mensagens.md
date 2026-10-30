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

## Como as seções 3 a 5 são escritas (revisão de 30/10/2026)

São lidas por quem conduz o sorteio, muitas vezes ao vivo. A primeira redação dizia a regra certa em
vocabulário do sistema ("extração declarada", "relação comprometida", "compromisso do universo") e
deixava a saída para o fim, com a data por calcular. A revisão, pedida pelo usuário em 30/10, fixa
quatro regras:

1. **O que fazer vem primeiro**, no título em negrito.
2. **A data vem pronta**: o primeiro dia de extração que um congelamento aceita, calculado
   (`viabilidade.primeiro_dia_possivel`). Na tela, a partir do congelamento mais cedo; na recusa e no
   diagnóstico, supondo a relação nova congelada hoje.
3. **Os nomes são os dos botões da tela**: "Publicar relação nova, sucedendo a atual", "Observar a
   ocorrência", "Realizar o sorteio".
4. **Os passos são uma lista numerada**, e não um parágrafo.

## 3. Aviso antes de congelar (FR-2659)

Na tela do sorteio, uma vez por marco, antes dos botões que congelam: "Publicar e congelar a relação"
e também "Publicar relação nova, sucedendo a atual", porque a sucessão congela na hora. Classe
`aviso`, `role="status"`. Não aparece quando todo recorte já tem o diagnóstico da seção 4.

> **Não congele a relação hoje: o sorteio seria recusado.** A extração do Edital ({referência} de
> {fonte}) é de {dia}, e essa fonte publica só a data, sem o horário. O sorteio só aceita extração de
> dia posterior ao congelamento da relação.
>
> Antes de congelar, retifique o Edital, trocando a extração por uma a partir de **{primeiro dia}**.
> [Vale também para publicar relação nova, sucedendo a atual: ela é congelada na hora.] Congelar não
> se desfaz.

Com as inscrições correndo, o título é **"A extração do Edital é cedo demais: o sorteio seria
recusado."**, a primeira frase acrescenta *"e a relação só pode ser congelada depois do fim das
inscrições"*, e a segunda começa por *"Antes do fim das inscrições"*. O primeiro dia conta do fim.

Se quem vê pode retificar, "retifique o Edital" é um link para a Retificação. Se não pode, a frase
é *"peça a quem elabora as Retificações deste Edital que o retifique"*.

## 4. Diagnóstico da relação congelada (FR-2660, FR-2661)

Antes de "Realizar o sorteio", com a classe `erro`:

> **Esta relação não pode ser sorteada com a extração do Edital.** Ela foi congelada em {data} às
> {hora}, e a extração {referência} de {fonte} é de {dia}. Essa fonte publica só a data, sem o
> horário, e o sorteio só aceita extração de dia posterior ao congelamento.
>
> Para sortear, nesta ordem:
>
> 1. Retifique o Edital, trocando a extração por uma a partir de **{amanhã}** (se a relação nova for
>    congelada hoje).
> 2. Publique a relação nova, sucedendo esta, no formulário logo abaixo.
> 3. Observe a nova ocorrência e realize o sorteio.
>
> Publicar a relação nova sem retificar antes não resolve.

Quando o método vigente já difere do comprometido (FR-2661):

> **A extração já foi trocada por Retificação, mas esta relação continua presa à extração antiga.**
> Uma relação congelada não acompanha Retificações.
>
> Para sortear, nesta ordem:
>
> 1. Publique a relação nova, sucedendo esta, no formulário logo abaixo.
> 2. Observe a nova ocorrência e realize o sorteio.

E, se a extração retificada também for cedo demais para uma relação congelada hoje:

> **Atenção:** a extração nova ({referência}, de {dia}) também é cedo demais para uma relação congelada
> hoje. Retifique de novo, para uma extração a partir de {amanhã}, antes de publicar a relação nova.

## 5. A recusa `occurrence_precedes_freeze` (FR-2662, FR-2663)

A frase inteira é desta feature desde a revisão de 30/10; o fuso dos instantes veio do PR #335
(`timezone.localtime`). A tela a precede de *"Não foi possível realizar o sorteio:"*.

> A relação foi congelada em {data hora}, e a extração {referência} de {fonte} só pode ser datada a
> partir de {data} 00:00: essa fonte publica a data da extração, sem o horário. O sorteio só vale com
> extração posterior ao congelamento: é o que prova que a lista foi fechada sem conhecer o resultado.
> Para sortear, nesta ordem: (1) retifique o Edital, trocando a extração por uma de dia posterior ao
> congelamento da relação nova — se ela for congelada hoje, a partir de {amanhã}; (2) publique a
> relação nova, sucedendo esta; (3) observe a nova ocorrência e realize o sorteio. Publicar a relação
> nova sem retificar antes não resolve.

Com fonte que publica a hora, a primeira frase é *"…e a fonte situa a extração {referência} de
{fonte} a partir de {data hora}, antes disso."*, e o passo 1 não traz data.

## Onde **não** aparece nada

- Fonte que publica a data e a hora (D-006), inclusive a `Fonte de demonstração` atual.
- Período de inscrições sem designação, sem término ou cancelado, ou com mais de um Evento marcado.
- Método com achado de forma, de fonte ou de instante.
- Ocorrência substituta: a regra de substituição não publica instante.
