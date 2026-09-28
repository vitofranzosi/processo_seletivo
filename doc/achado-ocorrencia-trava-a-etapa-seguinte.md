# A Ocorrência numa Etapa que nunca consolida trava a Etapa seguinte

**Encontrado em**: 26/09/2026, pela [`046`](../specs/046-contrato-de-executabilidade/spec.md), como
achado `A-1` — lido no código, não percorrido. Registrado na
[auditoria de consolidação](auditoria-de-consolidacao-2026-09-26.md) como **RC-112**, grupo A,
`[VALIDAR]`.

**Validado em**: 28/09/2026, contra a `main` em `d65f0136`, por teste de integração
([`test_ocorrencia_em_etapa_inconsolidavel.py`](../backend/tests/integration/resultados/test_ocorrencia_em_etapa_inconsolidavel.py)).

**Estado**: **confirmado, e não corrigido.** O comportamento é o que o `FR-004` da `013` manda ao pé
da letra; o que ele contraria é a justificativa da `D-003`, não um requisito. Corrigir é escolher entre
os dois textos, e a escolha é do usuário.

**Decidido depois, no mesmo dia:** o usuário escolheu a leitura em que o portão da habilitação fica
dormente diante de Etapa que não pode habilitar. A decisão, o que ela preserva e o que ela não
decide estão em [`decisao-rc112-portao-da-habilitacao.md`](decisao-rc112-portao-da-habilitacao.md),
que passa a ser a fonte. Este registro fica como a evidência da validação.

---

## O que se viu

Três inscrições submetidas. A primeira Etapa não se consolida: a consolidação a recusa por inteiro.
A presidência registra que uma das três não compareceu. A partir daí, as outras duas ficam
*aguardando a Etapa anterior* na segunda Etapa, e não há ato no sistema que as tire de lá.

| Momento | Etapa seguinte: participantes | aguardando | eliminadas |
|---|---|---|---|
| antes da Ocorrência | as 3 | nenhuma | nenhuma |
| consolidar a anterior para quem compareceu | **recusado** | | |
| registrar a Ocorrência de 1 | aceito — `ELIMINADA` | | |
| depois da Ocorrência | **nenhuma** | as 2 que compareceram | a que faltou |

Provado nos dois cenários em que a primeira Etapa é inconsolidável:

- **Edital novo** — Etapa *decisória e não eliminatória*, que nenhum marco cita. A `046` a publica com
  aviso (`FR-748`), porque nada no fluxo publicado exige o Resultado dela. A consolidação recusa com
  `regra_insuficiente`. **É por este cenário que o achado não ficou restrito ao acervo.**
- **Acervo** — Etapa eliminatória de *leitura múltipla* (duas avaliações por inscrição, sem regra de
  combinação), publicada antes da `046`. A consolidação recusa com `regra_de_combinacao_ausente`.

## A cadeia

1. A Ocorrência não consulta o mecanismo avaliação, por desenho: o item 6 da `D-1`, na
   [`013`](../specs/013-consolidacao-resultado-etapa/spec.md), diz que *"uma Etapa impedida de
   consolidar continua podendo registrar que alguém não compareceu"*
   (`resultados/application/ocorrencia.py`, docstring do módulo).
2. A consequência da Ocorrência é sempre `ELIMINADA` (item 7 da mesma `D-1`).
3. O gate da habilitação pergunta só se a Etapa anterior **tem algum** Resultado
   (`resultados/application/selectors.py::ha_resultado_em`), e a Ocorrência é um Resultado.
4. Acordado o gate, participa da seguinte só quem tem `HABILITADA` na anterior
   (`resultados/application/prontidao.py`, `participacao_detalhada`).
5. `HABILITADA` só nasce da consolidação, e a consolidação continua recusando a Etapa inteira.

## O que está escrito, e onde os textos se separam

**O `FR-004` da `013`** — *"Etapa posterior cuja Etapa imediatamente anterior já possua ao menos um
Resultado DEVE exigir, além disso, Resultado `HABILITADA` nessa Etapa imediatamente anterior."* É o
que o código faz. Nenhuma palavra distingue a origem do Resultado.

**A `D-003` da mesma spec**, que o `FR-004` implementa, justifica o gate assim: *"sem ele, Etapa
anterior de leitura múltipla, que D-001 não consolida, deixaria a Etapa seguinte permanentemente sem
participantes, e nenhum Edital de segunda leitura passaria da primeira Etapa."* É exatamente o que
acontece aqui — com o gate, depois de uma ausência.

A `D-1` — o Resultado sem Avaliação, de onde vem a Ocorrência — foi tomada em 04/09 em
[`decisoes-pre-vertical.md`](decisoes-pre-vertical.md) e entrou na `013` como extensão, depois do
`FR-004`; os dois nunca foram confrontados. A `046` viu o encontro e o deixou fora do gate de publicação por ser condição
operacional: depende de alguém registrar uma ausência.

**Nenhum requisito diz que a Etapa seguinte não pode travar.** Por isso não há o que corrigir sem
decisão.

## Por que importa antes do piloto

A ausência é o caso comum, e não o de borda: a `013` cita três Editais que produzem desfecho por
não comparecimento. Num Edital com Análise documental decisória e não eliminatória antes de uma
Entrevista, basta uma Ocorrência na primeira para a Entrevista não ter participante nenhum. Nada
avisa: a tela da Etapa seguinte mostra quem está aguardando, e não diz que a espera não termina.

## O que não se decidiu aqui

As saídas que se veem, sem recomendação de nenhuma:

- **O gate conta só Resultado por avaliação.** Ocorrência continua eliminando (a Regra 1 da `D-003`
  não tem gate), mas não acorda a exigência de habilitação. Reescreve o `FR-004`.
- **O gate não acorda em Etapa que a consolidação recusa por inteiro.** É a justificativa da
  `D-003` tornada regra: se a anterior não pode produzir `HABILITADA`, exigi-la é impossível por
  construção. Reescreve o `FR-004`, e lê a mesma regra que a `046` já lê para publicar.
- **Recusar a Ocorrência em Etapa inconsolidável.** Contraria o item 6 da `D-1` e os Editais
  que a motivaram — quem faltou precisa de desfecho.
- **Manter, e dizer.** A tela da Etapa seguinte explica que a espera não termina, e o caminho é
  Retificar a anterior para que ela consolide. A Retificação como saída foi lida, não percorrida.

Nada foi corrigido. Registro, não escopo.
