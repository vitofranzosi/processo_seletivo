# Achado — o Edital aceita uma extração que o sorteio sempre vai recusar

**Encontrado em**: 29/10/2026, no teste do sorteio do Edital 72/2026 (Curso Técnico Subsequente em
Multimeios Didáticos) no ambiente instalado no servidor. A análise do código é da `main` em
`0ff70f07`. O commit que roda no servidor não foi conferido.

> **Não é defeito da recusa, e não vira escopo por estar escrito aqui.** O sorteio recusou pelo
> motivo certo. O que se registra são duas lacunas em volta dela, o que custam e o que uma spec
> teria de decidir. Priorizar é do usuário.

## O que se viu

*"Realizar o sorteio"*, no recorte de ampla concorrência, foi recusado com:

> Não foi possível realizar o sorteio: Não é possível afirmar que a ocorrência aconteceu depois do
> congelamento da relação: a fonte a situa a partir de 28/10/2026 03:00, e a relação foi congelada
> em 28/10/2026 14:20. A semente é posterior ao compromisso do universo, e não o contrário.

Na mesma tela:

- **Relação congelada em 28/10/2026 11:20**, com 5 participantes;
- **Ocorrência da fonte**: Loteria Federal, concurso 6113, observada em 29/10/2026 09:11:35;
- **Aconteceu não antes de 28/10/2026 00:00**.

O Edital publicado (item 7.2 do PDF retificado em 29/10) diz que a ordem sai do concurso 6113 da
Loteria Federal, *"de 28/10/2026, às 20h05"*. O cronograma dele põe o fim das inscrições em
**28/10, às 9h**, e a publicação da relação em **28/10, às 12h**.

## Por que a recusa está certa

A Caixa publica `dataApuracao` como **data, sem horário**. Desde a correção registrada em
`sorteios/infrastructure/fontes/loteria_federal.py::_nao_antes_de`, essa data vale como o
**início do dia**, e não como `20:00`, que era um horário inventado. O docstring diz a consequência
com todas as letras: *"para provar precedência, a relação precisa ter sido congelada antes do dia
da extração."*

`sorteios/application/sorteio.py` compara esse limite inferior com o congelamento. Neste caso, 00:00
de 28/10 não é posterior a 11:20 de 28/10, e a recusa é a garantia funcionando. Na vida real, a
extração foi às 20h. O sistema só sabe o que a fonte diz, e a fonte não diz a hora.

## Lacuna 1 — o Edital publica um cronograma que o sorteio não consegue cumprir

**A impossibilidade era visível antes da publicação, e nada a apontou.** Três coisas o sistema já
sabia quando o Edital foi publicado:

1. a relação só se congela **depois** do fim das inscrições: `publicar_relacao` recusa antes disso
   (ver [o achado de 27/09](achado-relacao-do-sorteio-congela-com-inscricoes-abertas.md));
2. a fonte declarada publica só a data, e a data vale como o início do dia;
3. o instante declarado da extração, `drawMethod/occurrenceAt`, 28/10/2026 20h05.

Com o fim das inscrições em 28/10 às 9h, o congelamento mais cedo possível é 28/10 às 9h, que nunca
é anterior a 28/10 às 00:00. **O sorteio deste Edital estava condenado desde a publicação.**
`editais/domain/perfis.py::_validar_instante_da_ocorrencia` confere só o formato e o fuso de
`occurrenceAt`. Nenhuma regra compara o **dia** dele com o fim do período de inscrições.

**O custo.** A recusa aparece no dia do sorteio, com o certame em curso e o cronograma publicado. O
Edital 72 não tem saída barata: suceder a relação congela ainda mais tarde, e trocar de extração
mexe no método publicado, o que é Retificação. A mutabilidade diz que `drawMethod/occurrence` e
`drawMethod/occurrenceAt` são retificáveis, e diz também que *"a relação congelada carrega o seu
`metodo_hash` e não relê o vigente"*. Não foi verificado se uma relação já congelada aceita
sortear com a extração de um método retificado, ou se exige suceder a relação.

**Por que não apareceu antes.** Em desenvolvimento e na suíte, `SORTEIO_FONTE_DE_DEMONSTRACAO`
seleciona a `FonteDeTeste`, que devolve `ocorrida_nao_antes_de=timezone.now()`. Com ela, todo
congelamento é anterior à ocorrência, inclusive no mesmo dia. Só a fonte real, num ambiente que não
liga a chave, reproduz o caso. O roteiro local nunca o veria.

### O que uma spec teria de decidir

1. **Recusa ou aviso na publicação.** O caso é certo, e não provável: com fonte que publica só a
   data, extração no dia do fim das inscrições **nunca** sorteia. Isso pesa a favor de recusa. Contra:
   a regra depende de a fonte publicar ou não o horário, e uma fonte futura com horário tornaria
   válido o mesmo cronograma.
2. **Contra qual instante comparar.** O fim do período de inscrições é o limite rígido, e é o que o
   sistema já conhece. A publicação da relação no cronograma é Evento livre, e só existe quando quem
   elabora a declara.
3. **Onde mais avisar.** A tela do sorteio poderia dizer, **antes** de congelar, que congelar hoje
   torna impossível a extração declarada para hoje. O congelamento é ato append-only, e o operador
   que congela no mesmo dia não tem como desfazer.

## Lacuna 2 — a mensagem de recusa mostra os instantes em UTC

A mensagem diz **03:00** e **14:20**. A tela diz **00:00** e **11:20**. São os mesmos instantes:
`USE_TZ = True` guarda em UTC, e `sorteio.py` formata os dois `datetime` com f-string
(`{ocorrencia.ocorrida_nao_antes_de:%d/%m/%Y %H:%M}`), sem passar por `timezone.localtime`. O
template formata com o filtro `date`, que converte para `America/Sao_Paulo`.

`sorteios/application/ocorrencia.py`, na recusa `occurrence_not_due_yet`, já faz certo:
`timezone.localtime(ocorre_em).strftime(...)`.

**O custo.** A recusa é a única explicação que o operador recebe, e ela contradiz a tela logo abaixo
por três horas. Quem lê *"a fonte a situa a partir de 03:00"* conclui que a fonte informou um
horário, o que não é verdade, e passa a investigar o lado errado. É a mesma classe do
[teste com data em UTC](achado-teste-com-data-em-utc.md): instante formatado fora do fuso da tela.

Esta lacuna não pedia decisão de produto. Nenhuma outra mensagem do backend interpola um `datetime`
com f-string sem `localtime`: a busca por `:%d/%m/%Y` acha só `avaliacoes/domain/conjunto.py`, que já
converte, e `excluir_registros_do_piloto`, que formata datas.

**Corrigida em 29/10/2026**, a pedido do usuário, no mesmo PR deste registro: os dois instantes da
recusa passam por `timezone.localtime`.
`tests/integration/sorteios/test_ocorrencia_declarada.py::test_a_recusa_por_precedencia_diz_os_instantes_no_fuso_da_tela`
falhava antes da correção, com o horário em UTC, e passa depois dela.

## Observação do ensaio, não do sistema

O método publicado no Edital 72 tem campos trocados: *"Normalização"* traz *"Semente gerada no
concurso Lotofácil nº 3814 programada para o dia 26/10/2026"*, que é outra modalidade e outra data,
e *"Derivação"* traz *"Concurso LOTERIAL FEDERAL nº 6113"*. O sistema aceita texto livre nesses
campos, e a revisão humana não pegou. Num certame real, isso seria matéria de Retificação.
