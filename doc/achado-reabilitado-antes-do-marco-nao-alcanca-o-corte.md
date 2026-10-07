# A reabilitação de quem foi eliminado antes da última Etapa do marco não alcança o corte

**Encontrado em**: 06/10/2026, ao investigar
[`achado-corte-nasce-obsoleto-apos-recurso.md`](achado-corte-nasce-obsoleto-apos-recurso.md) — lido
no código e observado no banco de demonstração `ps_apresentacao_grafico`; **não percorrido em
teste**.

**Estado**: **não validado, e não corrigido.** Separado da [`061`](../specs/061-corte-apos-recurso/spec.md)
por decisão do usuário, para não ampliar aquela correção (decisão 002 da `061`).

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
4. O que acontece em vez disso: a pessoa precisa de Resultado na Etapa seguinte (a publicabilidade
   já acusa *reingresso pendente*); depois dele, a **ordem** fica obsoleta por *participantes
   alterados*; o **corte** só acusa quando a ordem sucessora for emitida, como *ordem sucedida*.
   Entre o deferimento e a ordem sucessora, a Etapa governada segue recebendo trabalho sob uma faixa
   que talvez exclua quem teve o direito reconhecido.

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

## O que falta para validar

Um teste de integração com marco de **duas** Etapas enumeradas: eliminar alguém na primeira,
emitir ordem e corte, deferir o recurso que o reabilita, e perguntar `estado_do_corte` e
`impedimento_do_corte`. O cenário de `tests/fixtures/corte.py` não serve como está: o marco dele
enumera uma Etapa só, e nela quem é eliminado continua no universo.

## As saídas que se veem

Sem recomendação:

- **Alargar a pergunta a quem o ato excluiu.** Sucessor vigente que supere uma eliminação, de
  inscrição do recorte que **não** está em `participants`, numa Etapa até a última do marco. Uma
  consulta, mas precisa do recorte (Perfil e lista) que hoje `_reingressou` não lê.
- **Delegar à ordem.** Perguntar a `estado_do_marco` se o ato ficou para trás por participantes. É a
  saída que a `061` descartou por custo, e ela resolveria os dois casos de uma vez.
- **Manter, e dizer.** A tela da Ordenação já mostra a ordem obsoleta; a do Corte passaria a apontar
  para ela. Não bloqueia, e a `FR-228` existe para bloquear.

Nada foi corrigido. Registro, não escopo.
