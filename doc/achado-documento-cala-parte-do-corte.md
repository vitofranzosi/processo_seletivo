# O documento cala parte do corte e a Etapa que habilita ao sorteio

**Encontrado em**: 27/09/2026, ao corrigir o [achado da Revisão](achado-revisao-nao-mostra-a-classificacao.md),
contra a `main` em `ac5552ad`.

**Estado**: **registrado, não corrigido.** A regra daquela correção era não mexer no documento
publicado. A decisão de corrigir é do usuário, e a correção muda o que se publica daqui em diante.

---

## O que se vê

A Revisão passou a mostrar, por marco, tudo o que o marco declara. Para isso ela reusa as frases do PDF
(`backend/processo_seletivo/publicacoes/infrastructure/pdf.py`). Nessa conferência apareceram três
declarações que o conteúdo publicado carrega, que a validação exige ou consome, e que o documento não
imprime em lugar nenhum:

| Declaração | Onde mora no conteúdo | O que ela decide | No documento |
|---|---|---|---|
| Empate na última posição | `cutRule.tieOutcome` | se os empatados na última posição progridem todos ou se o corte para no alvo | ausente |
| Continuação | `cutRule.continuation` | se o Edital admite chamar além dos que o corte publicou | ausente |
| Etapa que habilita ao sorteio | `drawMethod.qualifyingStageId`, no marco | quem entra no sorteio: todas as inscrições submetidas, ou só as aprovadas numa Etapa | ausente |

`_regra_de_corte` imprime o alvo, os suplentes e a Etapa governada, e não lê `tieOutcome` nem
`continuation`. `CAMPOS_DO_METODO`, que o documento percorre, tem sete campos, e a Etapa de habilitação
é o décimo campo do método do marco: o docstring de `_publica_a_mesma_norma` a cita, e nenhum código a
imprime. Conferido por `grep` em `pdf.py`, e as seções de texto padrão do catálogo também não a
mencionam.

## Por que importa

- **A `FR-185` da [`014`](../specs/014-corte-e-progressao-entre-etapas/spec.md)**: *"A Regra de Corte
  MUST viajar no conteúdo canônico publicado e MUST constar do documento gerado"*. A regra tem seis
  campos (`faixa.CAMPOS_DA_REGRA`), e o documento imprime quatro.
- **As três mudam quem continua no certame.** Com alvo de 10 e três empatados na 10ª posição, o
  `ADMITS_SURPLUS` leva doze, e o `STRICT` recusa o corte (`EmpateAtravessaOCorte`). A habilitação decide
  quem é sorteado. Um candidato que lê só o Edital não reconstitui a regra que o sistema aplica, e é
  essa reconstituição que o Princípio IV pede.
- **Depois de publicadas, as três só se corrigem por Retificação, e uma nem assim**:
  `cutRule/continuation` é `NAO_RETIFICAVEL` no contrato da `026`.

## Um detalhe menor, na mesma frase

Com alvo fixo de 1, `_regra_de_corte` escreve *"Progridem os 1 (um) primeiros desta ordem"*: o plural
não concorda com o número. A Revisão mostra a mesma frase, porque a reusa.

## O que não se decidiu aqui

- **Se é defeito contra a `FR-185` ou decisão de apresentação.** O docstring de `_regra_de_corte`
  justifica o que omite (o alvo derivado, a Etapa terminal) e não fala do empate nem da continuação.
- **A redação.** A composição e agora a Revisão escrevem *"todos os empatados progridem"* e *"admite
  chamar além dos que o corte publicar"*. O documento pediria a forma normativa, como a que ele já usa
  para o recurso.
- **O acervo.** Corrigir muda o que se imprime em Editais publicados daqui em diante. Os já publicados
  não se regeneram, e a prévia de um Edital antigo passaria a mostrar o que o documento dele não
  mostra.

Registro, não escopo.
