# O corte emitido depois do recurso nasce obsoleto, e não há geração que o tire de lá

**Encontrado em**: 06/10/2026, no banco de demonstração `ps_apresentacao_grafico` (Edital 72/2026,
Processo PS-CICLO-2026), montado por roteiro para percorrer um certame inteiro.

**Validado em**: 06/10/2026, contra a `main` em `1d2c26ff`, por teste de integração contra
PostgreSQL —
[`test_corte_apos_recurso.py`](../backend/tests/integration/classificacao/test_corte_apos_recurso.py).

**Estado**: **corrigido em 06/10**, pela [`061`](../specs/061-corte-apos-recurso/spec.md). O usuário
escolheu a primeira saída abaixo — comparar a identidade com o que o ato congelou —, pediu a
verificação da publicação, que este registro só inferia, e separou a pergunta vizinha do fim em
[`achado-reabilitado-antes-do-marco-nao-alcanca-o-corte.md`](achado-reabilitado-antes-do-marco-nao-alcanca-o-corte.md).
Até então: confirmado, e não corrigido. O código contrariava a `FR-230` e a justificativa da `D-008`
da [`014`](../specs/014-corte-e-progressao-entre-etapas/spec.md). Este registro fica como a evidência
da validação; a fonte da decisão é a `061`.

---

## O que se viu

Nas listas de ampla concorrência dos marcos MAT e TEC, as telas de Ordenação e Corte dizem *"A faixa
emitida está obsoleta… Um participante reingressou no universo da ordem por decisão recursal
deferida"* — sobre faixas emitidas **depois** do julgamento e da ordem sucessora.

| Data | Ato |
|---|---|
| 14/09 | ordem preliminar |
| 22/09 | dois recursos deferidos: um reabilita quem a prova escrita eliminara, outro revê nota de títulos |
| 23/09 | ordens sucessoras e publicação definitiva |
| 29–30/09 | análise documental |
| 01/10 | corte e convocação |

No banco, os Resultados sucessores que a causa acusa são **exatamente** os que o ato lido pela
faixa já cita:

| Marco | Lista | Ato que o corte leu | Sucessores vigentes alcançados | Já citados em `stageResults` |
|---|---|---|---|---|
| MAT | ampla | sucessor, 23/09 | 2 | 2 |
| TEC | ampla | sucessor, 23/09 | 1 | 1 |
| MAT, TEC | reservadas | raiz, 14/09 | 0 | 0 |

Quem montou o banco relatou que emitir o corte **antes** da análise documental fazia a
consolidação recusar com `corte-obsoleto`; o roteiro contornou consolidando antes de cortar.

## A cadeia

1. `classificacao/application/corte.py::_reingressou` pergunta se existe `ResultadoEtapa` vigente,
   de um participante do ato, numa Etapa que produziu a ordem, **com `resultado_anterior`
   preenchido**.
2. A pergunta não compara nada com o ato: nem o instante, nem a identidade dos Resultados que ele
   leu. Um Resultado sucessor continua sucessor para sempre.
3. Logo, depois do primeiro deferimento numa Etapa da ordem, **toda** geração de corte daquela lista
   nasce obsoleta — inclusive a emitida sobre a ordem sucessora, que já considerou o recurso.
4. `resultados/application/prontidao.py::impedimento_do_corte` transforma a obsolescência em
   bloqueio de distribuir, concluir e consolidar na Etapa governada (`FR-228`), e a recusa diz que o
   caminho é *"emitir a geração sucessora"*.
5. A geração sucessora lê o mesmo ato, e o passo 3 a alcança também. **O caminho que a recusa
   oferece não sai do lugar** — o terceiro caso do teste o prova.

`divulgacao/domain/publicabilidade.py::_corte_obsoleto` consulta a mesma função, de modo que a
publicação que dependa da faixa (`FR-219`) fica impedida pelo mesmo motivo — `publication_cut_stale`,
com a causa *participante reingressou*. Escrito aqui primeiro como leitura; provado depois, na
`061`. No 72/2026 não apareceu porque a definitiva saiu antes do corte.

## A reprodução

O cenário de `tests/fixtures/corte.py` (`cenario`: quatro inscritos, ordem emitida, alvo de dois),
seguido de:

1. recurso deferido sobre o Resultado da Etapa pontuada de um participante — o mesmo
   `_superar_resultado` de `test_corte_obsoleto.py`;
2. ordem sucessora emitida (`emitir_ordem` com `ato_vigente` do marco);
3. corte emitido sobre ela.

| Caso | Esperado | Obtido |
|---|---|---|
| `estado_do_corte` do corte recém-emitido | em dia, sem causa | `obsoleto`, `participante_reingressou` |
| `impedimento_do_corte` da Entrevista governada | `None` | `corte-obsoleto` |
| `estado_do_corte` depois de emitir a geração sucessora | em dia | `obsoleto`, `participante_reingressou` |

O teste confere também que o ato lido pela faixa é a ordem sucessora e que o Resultado sucessor
consta do `stageResults` dela. Rodar:

```bash
cd backend && TEST_DB_ENGINE=postgresql DB_USER=$USER DB_RUNTIME_USER=$USER DB_NAME=<próprio> uv run pytest tests/integration/classificacao/test_corte_apos_recurso.py
```

## O que os testes existentes cobriam

`test_corte_obsoleto.py` exercita uma cronologia só — **corte emitido, depois o recurso** —, nos dois
sentidos: o deferimento numa Etapa da ordem obsoleta (`FR-218`), e o deferimento na Etapa governada
não obsoleta (`FR-230`). Nenhum teste emite o corte depois de uma ordem sucessora por recurso, que é
a cronologia de todo certame em que a definitiva sai antes do corte.

## O que está escrito

- **`FR-218`**: reingresso no universo **do ato de ordenação que o corte cita** torna o corte
  obsoleto.
- **`FR-230`**: reingresso que **não** alcance o ato citado não obsoleta — *"obsoletá-lo bloquearia
  trabalho para exigir uma geração sucessora idêntica à anterior"*.
- **`D-008`**: *"um ato que não muda nada não é ato, é cerimônia"*.

O ato sucessor cita o Resultado sucessor; o deferimento já está dentro dele, e não há o que
reingressar. O código produz exatamente a geração sucessora idêntica que a `FR-230` recusa — e,
diferente do caso que ela previu, nem a geração sucessora a resolve.

## As saídas

Sem decisão tomada. As que se veem:

- **Comparar a identidade com o que o ato congelou.** Obsoleta só se houver Resultado sucessor
  vigente, alcançado pelo ato, **cujo `id` não esteja no `stageResults` dele**. Uma linha:
  `.exclude(id__in=<ids citados>)` na mesma consulta, sem consulta nova. O `stageResults` é
  conferido pela trigger de proveniência do ato contra a linha append-only do Resultado, então a
  âncora é confiável. Aplicada provisoriamente e revertida: passam os três casos novos e os 33 de
  `test_corte_obsoleto.py`, `test_obsolescencia_por_recurso.py`,
  `test_publicabilidade_por_recurso.py` e `interface/test_reabilitacao.py`. Não roda a suíte
  inteira.
- **Comparar o instante.** Obsoleta só se o sucessor foi consolidado depois de `ato.emitido_em`.
  Mesma consulta, mas depende de relógio — e o projeto tem caminho legítimo de relógio atrasado
  (`seed_demo --dias-atras`). A identidade diz a mesma coisa sem essa dependência.
- **Delegar à ordem.** Perguntar a `estado_do_marco` se o ato que a faixa leu ficou para trás por
  mudança de participantes ou de Resultados. É a pergunta mais fiel à `D-008`, e recalcula a ordem
  inteira a cada leitura — `impedimento_do_corte` roda na prontidão de cada Etapa governada, sob
  orçamento de consulta verificado por teste.

## Uma pergunta vizinha, não verificada

O universo do ato inclui quem foi eliminado na Etapa do marco e **exclui** quem foi eliminado
antes dela (`calculo.py::calcular_ordem`). Reabilitado alguém eliminado numa Etapa anterior, ele
não está em `participants`, e `_reingressou` não o vê — nem hoje, nem com a primeira saída acima. A
ordem fica obsoleta por conta própria (`participantes_alterados`), mas o corte só acusa quando a
ordem sucessora for emitida (`ordem_sucedida`). Se isso contraria a `D-008` — *"superado o Resultado
que eliminava alguém… o corte vigente do marco alcançado fica obsoleto"* — é leitura a confirmar, e
não foi percorrido.

Nada foi corrigido neste registro; a correção é a `061`.
