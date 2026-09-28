# O documento cala parte do corte e a Etapa que habilita ao sorteio

**Encontrado em**: 27/09/2026, ao corrigir o [achado da Revisão](achado-revisao-nao-mostra-a-classificacao.md),
contra a `main` em `ac5552ad`.

**Estado**: **corrigido em 27/09/2026**, antes da spec do passo 1, por decisão do usuário. Ver
[a correção](#a-correção-2709), no fim. Até aqui, o texto é o registro como foi feito.

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

---

## A correção (27/09)

**Os requisitos.**

- **Empate e continuação**: a `FR-185` da [`014`](../specs/014-corte-e-progressao-entre-etapas/spec.md),
  que pede a Regra de Corte *"no documento gerado, na seção do marco a que pertence"*. Os dois campos
  são os que a `FR-181` e a `FR-226` mandam declarar.
- **A Etapa que habilita ao sorteio**: nenhum FR a enumera — a `FR-465` da
  [`032`](../specs/032-executabilidade-antes-de-publicar/spec.md) lista os sete campos do método, e ela
  é o décimo. O que a sustenta é a Constituição, §VI: *"O PDF DEVE [...] corresponder exatamente à
  versão homologada"*, e o documento calava quem participa do sorteio que ele publica. O `R-012` da
  [`021`](../specs/021-sorteio-publico-auditavel/research.md) chama a Etapa de *"declarada no Edital"*.
- **O plural** de *"os 1 (um) primeiros"*, na mesma frase da `FR-185`.

Nenhum requisito novo, nenhuma chave nova no conteúdo canônico.

**O que o documento passou a imprimir** (`backend/processo_seletivo/publicacoes/infrastructure/pdf.py`),
na seção do marco:

```text
  Corte:            Progridem os 10 (dez) primeiros desta ordem.
  Empate no corte:  Havendo empate na última posição, progridem todos os empatados, ainda que
                    excedam essa quantidade.        ← ou: essa quantidade não é excedida.
  Continuação:      Poderá haver chamada, nesta ordem, além dos que este corte publicar.
                                                    ← ou: Não haverá chamada além dos que …
```

E, no bloco *Sorteio*, depois dos sete campos do método:

```text
    Habilitação:    participam apenas as inscrições habilitadas na Etapa Prova didática
                                                    ← ou: participam todas as inscrições submetidas
```

- **O empate e a continuação só saem com a frase do corte**, porque *"essa quantidade"* é a dela. A
  regra sem alvo não imprime nenhuma das três.
- **A habilitação é lida do método que governa** (`marcos.metodo_que_governa`), que é o que
  `sorteios/application/relacao.py` lê ao projetar a relação. O marco que referencia o método comum
  sorteia todas as submetidas, e o documento o diz. Ela continua **fora** da comparação que nomeia a
  divergência entre o método próprio e o comum (`_publica_a_mesma_norma`).
- **Alvo de um**: *"Progride o 1 (um) primeiro desta ordem."*; com suplentes, o verbo volta ao plural.

**Um lugar só.** As frases moram em `pdf.py` (`_empate_no_corte`, `_continuacao_do_corte`,
`_habilitacao_ao_sorteio`), e a Revisão as importa, como já importava `_regra_de_corte`. A redação
própria que a Revisão tinha (*"todos os empatados progridem"*, *"admite chamar além…"*,
*"Etapa que habilita a participar do sorteio"*) saiu. Os rótulos também passaram a ser os do documento:
*Empate no corte*, *Continuação*, *Habilitação*. O que a Revisão ainda mostra e o documento não é o que
ele cala de propósito: *"Etapa que o corte alimenta: nenhuma"* e o silêncio dito como silêncio.

**O acervo.** Documento publicado não se regenera (Princípio II, `FR-469` da `032`): os Editais já
publicados continuam com o documento que tinham. A prévia de um Edital antigo, se gerada de novo,
mostra as linhas novas. Para ver pelo navegador, re-semeie o banco.

**Testes**: `backend/tests/unit/publicacoes/test_pdf_classificacao.py` (bloco *"O documento dizia parte
do corte"*) e as asserções da Classificação em `backend/tests/unit/interface/test_revisao.py`.
