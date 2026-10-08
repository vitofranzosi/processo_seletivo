# A reabilitação de quem foi eliminado antes da última Etapa do marco não alcança o corte

**Encontrado em**: 06/10/2026, ao investigar
[`achado-corte-nasce-obsoleto-apos-recurso.md`](achado-corte-nasce-obsoleto-apos-recurso.md) — lido
no código e observado no banco de demonstração `ps_apresentacao_grafico`.

**Validado em**: 07/10/2026, contra PostgreSQL, sobre a `main` em `5afdfa5a` (a `061` já mergeada),
em
[`test_corte_reabilitado_antes_do_marco.py`](../backend/tests/integration/classificacao/test_corte_reabilitado_antes_do_marco.py).

**Estado**: **confirmado, e não corrigido.** Separado da [`061`](../specs/061-corte-apos-recurso/spec.md)
por decisão do usuário, para não ampliar aquela correção (decisão 002 da `061`). A escolha da saída
é do usuário; o teste prende o comportamento de hoje, e os casos marcados como *achado* são os que
mudam se a saída escolhida mudar o comportamento.

---

## A pergunta

Quem foi eliminado numa Etapa **anterior à última** que o marco enumera, e depois reabilitado por
recurso deferido, torna obsoleto o corte que já tinha sido emitido?

Pela leitura, **não** — e a pessoa é justamente o caso que a `014` descreve ao justificar o bloqueio.

## A cadeia, lida

1. O universo do ato de ordenação é o das inscrições que **participam da última Etapa** do marco
   (`classificacao/application/calculo.py::calcular_ordem`, com `_ultima_etapa` e
   `restringir_a_participantes`). A Regra 1 da decisão 003 da `013` tira desse conjunto quem foi eliminado em
   qualquer Etapa anterior, inclusive uma que o próprio marco enumera.
2. `classificacao/application/corte.py::_reingressou` só pergunta por inscrições que estão em
   `participants` do ato que o corte leu. Quem foi eliminado antes nunca esteve lá.
3. Logo, a reabilitação dessa pessoa não produz a causa *participante reingressou*, e
   `impedimento_do_corte` não bloqueia trabalho novo na Etapa governada.
4. O que acontece em vez disso: a **ordem** fica obsoleta **no deferimento**, por *participantes
   alterados* (causa *participante reingressou*), e a publicação dela é recusada por *reingresso
   pendente* enquanto a pessoa não tiver Resultado na Etapa seguinte. O **corte** só acusa quando a
   ordem sucessora for emitida, como *ordem sucedida*. Entre o deferimento e a ordem sucessora, a
   Etapa governada segue recebendo trabalho sob uma faixa que talvez exclua quem teve o direito
   reconhecido.

   *(A redação de 06/10 dizia que a ordem só ficava obsoleta depois do Resultado na Etapa seguinte.
   O teste mostrou que não: a Regra 1 deixa de excluir a pessoa e o gate da Regra 2 passa a admiti-la
   no instante do deferimento, e a proposta de agora já a conta, sem posição.)*

A `061` não muda nada disso: ela estreitou a pergunta para os sucessores ainda não citados, e esta
pessoa continua fora do conjunto em que a pergunta é feita.

## O que se observou no banco de demonstração

No marco MAT do Edital 72/2026, lista de ampla concorrência, a ordem sucessora tem **um**
participante a mais que a preliminar. É a pessoa reabilitada na prova escrita: Resultado `ELIMINADA`
por avaliação na Etapa `79d13534`, sucedido por `HABILITADA` por recurso, e depois avaliada na Etapa
`e50044f3`. As duas Etapas são enumeradas pelo marco; a prova escrita não é a última.

Ali o caso não apareceu como defeito porque o corte foi emitido **depois** da ordem sucessora. Na
cronologia *corte → recurso*, ele apareceria.

## O que está escrito

- **`FR-218`** (`014`): reingresso *"no universo do **ato de ordenação** que o corte cita"* obsoleta.
  A pessoa não estava nesse universo — lida ao pé da letra, a regra não a alcança.
- **A decisão 008 da `014`**: *"Superado o Resultado que eliminava alguém, a pessoa volta ao
  fluxo… o corte vigente do marco alcançado **fica obsoleto**"*. Aqui a regra a alcança.
- **A docstring de `impedimento_do_corte`**: *"O caso que obriga a bloquear é o reingresso.
  Deferido o recurso que devolve alguém ao universo da ordem, continuar trabalhando sob a faixa
  antiga é exatamente excluir quem teve o direito reconhecido."*

Os textos se separam no que *universo do ato* quer dizer: o conjunto que o ato congelou, ou o
conjunto a que a pessoa teria pertencido sem a eliminação superada.

## A validação

O cenário de `tests/fixtures/corte.py` não servia — o marco dele enumera uma Etapa só —, e o teste
monta o próprio: o marco enumera a *Análise documental* (pontuada, eliminatória, mínima 60) e a
*Prova didática*, e o corte (alvo 2, estrito) governa a *Entrevista*.

```text
Análise documental   601: 90   602: 85   603: 80   604: 50 → ELIMINADA
Prova didática       601: 90   602: 80   603: 70   (604 fora)
ordem preliminar     601 (180) · 602 (165) · 603 (150)      corte   601, 602
recurso deferido     604 HABILITADA, 75, na Análise documental
```

O que se mediu, caso a caso:

| Pergunta, depois do deferimento | Resposta | Caso |
|---|---|---|
| `estado_do_corte` | **em dia, sem causa** | `test_achado_a_reabilitacao_antes_da_ultima_etapa_nao_obsoleta_o_corte` |
| `impedimento_do_corte` na Entrevista | **nenhum**; a faixa antiga segue mandando 601 e 602 | `test_achado_a_etapa_governada_segue_recebendo_trabalho` |
| `estado_do_marco` | obsoleta, *participantes alterados*, `reingressaram = [604]` | `test_a_ordem_ja_acusa_a_reabilitacao_antes_mesmo_da_prova_didatica` |
| publicação da ordem | recusada, *reingresso pendente* | `test_a_publicacao_da_ordem_ja_e_impedida` |
| o mesmo deferimento, de 603 (que **estava** no ato) | corte obsoleto, *participante reingressou*, e bloqueio | `test_o_contraste_quem_estava_no_ato_e_acusado` |
| 604 avaliada na Prova didática (95) | corte **ainda** em dia | `test_o_corte_so_acusa_depois_da_ordem_sucessora` |
| ordem sucessora emitida | corte obsoleto, só *ordem sucedida*; a ordem nova é 601 · **604** · 602 · 603 | idem |

A última linha é o dano, em números: a faixa antiga mandou **602** à Entrevista, e a geração
sucessora, com o mesmo alvo, a deixaria de fora e levaria **604**. Tudo o que a Entrevista distribuiu,
concluiu e **consolidou** para 602 nessa janela é o que a `FR-228` existe para impedir.

**E o achado é mais largo do que o título.** A Regra 1 exclui quem foi eliminado em **qualquer**
Etapa anterior à última do marco, enumerada ou não. Com o marco enumerando só a Prova didática — a
Análise documental elimina sem produzir a ordem —, a reabilitação nela obsoleta a ordem e não alcança
o corte do mesmo jeito (`test_achado_o_mesmo_quando_a_etapa_anterior_nao_e_enumerada`). É o arranjo
mais comum do acervo, e a frase "Etapa que o marco enumera" do título o esconderia.

**O que não está em risco.** A publicação da ordem (`FR-219`) já é recusada por *reingresso
pendente* e por obsolescência da própria ordem, e `calcular_corte` recusa emitir sucessora ou
continuação sobre ordem obsoleta (`FR-198`). A brecha é só a do trabalho novo na Etapa governada, e a
da tela do Corte, que mostra a faixa em dia.

## As saídas, com o que custam

Sem recomendação. Custos medidos no cenário do teste, com `CaptureQueriesContext`, numa sonda que não
ficou no repositório: hoje `estado_do_corte` faz **7** consultas e `impedimento_do_corte`, por raiz de
corte que governa a Etapa, **10**.

- **Alargar a pergunta a quem o ato excluiu.** Na mesma consulta de `_reingressou`, um segundo ramo
  em `OR`: Resultado vigente que suceda um `ELIMINADA` e não seja `ELIMINADA`, de inscrição do
  recorte **fora** de `participants`. A sonda confirmou **uma consulta**, igual à de hoje (`FR-1147`
  continua de pé). O recorte não custa leitura: `perfil_id` e `lista_id` estão na linha do `Corte`,
  que a geração já trouxe — a redação de 06/10 dizia o contrário. **Sem** filtro de Etapa, e de
  propósito: é o que cobre a Etapa não enumerada. O que ela não distingue é o falso positivo raro de quem
  tinha duas eliminações vigentes antes da última Etapa e teve só uma superada — continua fora, e o
  corte acusaria. A pergunta é uma aproximação das duas regras da decisão 003 da `013`, e não elas.
  - `FR-218` precisa de redação nova, ou de leitura declarada: *"universo do ato"* passa a ser
    *o conjunto que o ato congelou, mais quem nele estaria sem a eliminação superada*.
  - `FR-228` passa a valer na janela; `FR-230` fica intacta (o ramo novo exige estar **fora** de
    `participants`, e quem é julgado na Etapa governada estava dentro).
  - A decisão 008 da `014` é a que se cumpre: é o texto dela.
- **Delegar à ordem.** `estado_do_corte` pergunta a `estado_do_marco` se a ordem ficou para trás.
  `estado_do_marco` custou **13** consultas, e recalcula a ordem inteira do recorte — população e
  Resultados em memória —, **por raiz de corte**, a cada leitura da prontidão (`panorama_da_etapa`,
  na tela da Etapa e na consolidação). Um marco com ampla e duas reservadas são três cálculos
  completos por tela. É a saída que a `061` descartou por esse custo, entre as alternativas da decisão 001 dela.
  - Resolve este caso e o da Etapa não enumerada, e também o que a `061` resolveu — mas **alarga** a
    `FR-228` para além do reingresso: qualquer obsolescência da ordem — uma Retificação que alcance a regra do marco, por
    exemplo — passaria a bloquear a Etapa governada.
    Isso é decisão nova, e não leitura da `014`; a `FR-237` cuida do sentido inverso e não deste.
  - `FR-218` e `FR-230` ficam como estão no texto; a decisão 008 da `014` se cumpre.
- **Manter, e dizer.** Nenhuma consulta nova. A tela do Corte passaria a apontar para a ordem obsoleta
  do mesmo recorte — a tela da Ordenação já a mostra. Não bloqueia: a `FR-228` fica descumprida na
  janela, e a decisão 008 da `014` passa a ter exceção que precisa ser escrita. `FR-218` lida ao pé da
  letra é cumprida. O dano da tabela acima continua possível.

## Se virar correção

Vai para spec nova. Medido em 07/10/2026 em todas as 13 worktrees e em todas as branches locais e
remotas: a `062` (*Resultados divulgados*, `claude/062-resultados-por-perfil-etapa-lista`) é a mais
alta, e chega a **FR-1165** e **SC-449**. A próxima seria a **063**, a partir de **FR-1166** e
**SC-450** — medir de novo antes de abrir, porque a `062` ainda pode crescer.

Nada foi corrigido. Registro, não escopo.
