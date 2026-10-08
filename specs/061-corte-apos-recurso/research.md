# Research: O corte emitido depois do recurso não nasce obsoleto

**Feature**: [spec.md](spec.md) · **Plano**: [plan.md](plan.md) · **Data**: 2026-10-06

As decisões desta feature nascem em `D-001`. Decisão de outra feature é citada pela feature e pelo
número dela, por extenso.

---

## O que foi conferido antes de decidir

| Pergunta | Onde se respondeu | Resposta |
|---|---|---|
| O que a pergunta do reingresso compara? | `classificacao/application/corte.py::_reingressou` | Participante do ato, Etapa da ordem, `resultado_anterior` preenchido. Nada do que o ato leu. |
| O ato guarda o que leu? | `classificacao/application/calculo.py::_resumo_do_universo`; trigger em `classificacao/migrations/0003_ato_coerente_com_marco.py` | Sim: `stageResults`, com o `id` de cada Resultado, conferido pela trigger contra a linha append-only. |
| A ordem sucessora cita o sucessor? | `calcular_ordem`, que lê `ResultadoEtapa.vigentes` | Sim, por construção — a decisão de vigência da `018`. Provado no teste novo. |
| Quem consome a obsolescência? | `prontidao.py::impedimento_do_corte`, `publicabilidade.py::_corte_obsoleto`, `interface/conducao_do_marco.py`, `interface/supervisao.py`, `interface/views.py` | Todos por `estado_do_corte`. Nenhum tem regra própria de reingresso. |
| O que os testes cobriam? | `tests/integration/classificacao/test_corte_obsoleto.py` | Só *corte → recurso*, nos dois sentidos da `014` (Etapa da ordem obsoleta; Etapa governada não obsoleta). |
| A publicação era mesmo impedida? | teste novo, antes da correção | Sim: `publication_cut_stale`, com a causa *participante reingressou*. Até aqui era leitura do código. |
| O banco que mostrou o achado confirma o mecanismo? | `ps_apresentacao_grafico`, Edital 72/2026 | Nas duas listas de ampla, os sucessores acusados são exatamente os que o ato cita (2 de 2 no MAT, 1 de 1 no TEC). |

---

## D-001 — A identidade dos Resultados, contra o que o ato congelou

**Decisão**: o reingresso que obsoleta é o de Resultado sucessor vigente, alcançado pelo ato, cujo
`id` **não** está no `stageResults` dele. A exclusão entra na consulta que já existia.

**Por quê**: é a pergunta que a `FR-218` e a `FR-230` fazem — *o recurso alcança a ordem que a faixa
leu?* — respondida pelo registro que o próprio ato guarda do que leu. Não depende de relógio, não
acrescenta consulta, e o registro é conferido pela trigger de proveniência no instante da emissão.

**Alternativas descartadas** (as três estão no achado, e o usuário escolheu esta em 06/10/2026):

- **O instante** — obsoletar só se o sucessor foi consolidado depois de `ato.emitido_em`. Diria o
  mesmo na maioria dos casos, mas depende de relógio, e o projeto tem caminho legítimo de relógio
  atrasado no seed (`--dias-atras`). A identidade diz o mesmo sem essa dependência.
- **Delegar à ordem** — perguntar a `estado_do_marco` se o ato ficou para trás. É a pergunta mais
  larga, e recalcula a ordem inteira a cada leitura; `impedimento_do_corte` roda na prontidão de cada
  Etapa governada, sob orçamento de consulta.

---

## D-002 — Quem foi eliminado antes da última Etapa do marco fica fora

**Decisão**: esta feature não trata a reabilitação de quem foi eliminado numa Etapa anterior à
última que o marco enumera. Ela fica registrada à parte, em
[`doc/achado-reabilitado-antes-do-marco-nao-alcanca-o-corte.md`](../../doc/achado-reabilitado-antes-do-marco-nao-alcanca-o-corte.md).

**Por quê**: decisão do usuário. É outra pergunta — essa pessoa nunca esteve no universo do ato —, e
respondê-la mudaria o que *alcançar o ato* quer dizer, não só como se compara. A D-001 não a piora
nem a resolve: o comportamento ali é o mesmo de antes.

---

## D-003 — Nenhuma escrita, e os cortes já emitidos se corrigem pela leitura

**Decisão**: nenhuma migration, nenhum comando, nenhum ato de correção. O corte emitido antes desta
feature sobre ordem que já considerou o recurso aparece em dia na primeira leitura depois do deploy.

**Por quê**: a obsolescência é comparação, e não estado gravado — o módulo `classificacao/domain/universo.py`
existe para isso. Medido no banco de demonstração: as listas de ampla dos marcos MAT e TEC passam de
*obsoleta, participante reingressou* para em dia, e o impedimento da Etapa governada desaparece; as
três listas reservadas, que já estavam em dia, continuam.

---

## D-004 — A publicação é verificada nas duas cronologias

**Decisão**: dois testes de publicabilidade: o que não pode mais ser impedido (*recurso → ordem
sucessora → corte*) e o que tem de continuar sendo (*corte → recurso*).

**Por quê**: pedido do usuário — o efeito sobre a publicação estava só inferido no achado. Testar só
a cronologia corrigida deixaria a guarda da `FR-219` sem prova de que a correção não a afrouxou; a
cobertura existente dela (`test_publicar_com_o_corte_obsoleto_e_impedido_e_a_recusa_diz_o_caminho`)
usa a causa *ordem sucedida*, e não o reingresso.

---

## D-005 — Os testes novos moram num arquivo próprio e reusam o atalho do recurso

**Decisão**: `tests/integration/classificacao/test_corte_apos_recurso.py`, importando
`_superar_resultado` de `test_corte_obsoleto.py`.

**Por quê**: o arquivo existente fica sem edição — é a prova da `SC-441` —, e o atalho do recurso
passa pela interposição, admissão e decisão que as triggers exigem; duplicá-lo criaria dois caminhos
para a mesma garantia.
