# Contrato: as mensagens da conferência

As frases que quem opera lê, por situação e por ato (FR-3626, FR-3639 a FR-3642). Os testes conferem
as partes marcadas como **obrigatórias**. O resto é redação e pode ser polido sem mudar o contrato.

Notação: `{N}` é a referência, `{D}` a data em que ela foi realizada, `{L}` o último concurso,
`{DL}` a data dele, `{X}` a data declarada, `{T}` o instante da consulta (`DD/MM/AAAA às HH:MM`, no
fuso institucional), `{K}` a distância em concursos, `{J}` a distância em dias.

## Referência inválida — gravação e atos do Edital (impeditivo)

> O concurso da Loteria Federal deve ser informado só pelo número, como 6106 — sem dígito
> verificador, texto ou ano. "{valor}" não é um número de concurso que a Caixa aceita.

Obrigatório: o valor recusado entre aspas; "só pelo número".

## Referência inválida — congelamento (advertência; conteúdo do acervo)

> O Edital declara a ocorrência "{valor}", e a Caixa só aceita o número do concurso. A relação foi
> publicada, mas a observação da extração vai falhar com essa referência. Retifique o método antes
> do dia do sorteio.

## Realizado — submissão, publicação e Retificação (impeditivo)

> O concurso {N} da Loteria Federal já foi realizado, em {D}. A semente precisa vir de uma extração
> que ainda não aconteceu quando a relação de participantes for congelada. O último concurso
> realizado é o {L}, de {DL}: declare um concurso posterior a ele, que ocorra depois do fim das
> inscrições, conferindo o número e a data no calendário oficial da Caixa.

Sem a data do próprio concurso (FR-3629): "já foi realizado (data não informada pela Caixa)".

Obrigatório: `{N}`, "já foi realizado", `{D}` ou "data não informada pela Caixa", `{L}`, `{DL}`,
"posterior".

## Realizado — congelamento (recusa)

> Não é possível congelar a relação: o concurso {N} da Loteria Federal, declarado no Edital, já foi
> realizado, em {D}. Uma relação congelada depois da extração nunca poderá ser sorteada. Para
> sortear, retifique o método declarando um concurso posterior ao {L}, de {DL}, e só então publique a
> relação.

Obrigatório: "não é possível congelar", `{N}`, `{D}`, "retifique", "só então".

## Ainda não realizado — todos os atos e a conferência sob demanda (informação)

> Concurso {N}: ainda não realizado na consulta de {T}. O último concurso realizado é o {L}, de {DL};
> o declarado está {K} concurso(s) adiante, e a data declarada, {X}, {J} dia(s) depois. A data
> prevista não é verificada pela Caixa: confira no calendário oficial que o concurso {N} é o de {X}.

Quando `{N}` é o próximo anunciado pela Caixa, acrescenta-se "(o próximo anunciado pela Caixa)"
depois de `{N}`.

Obrigatório: "ainda não realizado na consulta de", `{T}`, `{L}`, `{K}`, "não é verificada pela
Caixa".

**Proibido** (SC-1095), em qualquer forma e em qualquer texto desta situação: "validad", "confirmad",
"conferid".

## Inconclusivo — todos os atos e a conferência sob demanda (advertência)

> Não foi possível verificar na Caixa se o concurso {N} já foi realizado: {motivo}. Isso não confirma
> nem recusa o concurso. Confira no resultado oficial da Loteria Federal que ele ainda não foi
> realizado.

`{motivo}` é um destes, e nada além (FR-3641, FR-3648):

- "a Caixa não respondeu a tempo";
- "não foi possível falar com a Caixa";
- "a Caixa respondeu sem o último concurso";
- "a Caixa respondeu com um erro".

Proibido: código HTTP, nome de exceção, corpo da resposta, endereço.

No congelamento, acrescenta-se: "A relação foi publicada." Nos atos do Edital, nada se acrescenta: a
advertência aparece junto das outras.
