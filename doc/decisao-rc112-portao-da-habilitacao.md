# Decisão — o portão da habilitação fica dormente diante de Etapa que não pode habilitar

Tomada pelo usuário em 28/09/2026, sobre o RC-112 da
[auditoria de consolidação](auditoria-de-consolidacao-2026-09-26.md), depois da validação registrada
em [`validacao-de-unidades-pre-piloto-2026-09-28.md`](validacao-de-unidades-pre-piloto-2026-09-28.md).
Das quatro leituras propostas ali, foi escolhida a **2**. Isto é registro, não implementação: nada
no código muda por causa deste documento.

## O defeito que ela resolve

A Regra 2 da `D-003` da `013` liga a exigência de habilitação na Etapa seguinte assim que a Etapa
anterior produz o **primeiro Resultado**. A Ocorrência (ausência) é Resultado e pode ser registrada
numa Etapa que não consolida, por desenho. Numa Etapa assim — de leitura múltipla, sem regra de
combinação —, uma única ausência liga o portão, e ninguém mais pode ser habilitado ali. O resultado
são todos os outros presos em *"aguardando a Etapa anterior"* para sempre. Isso foi reproduzido em
28/09 no acervo e num Edital publicável hoje: `(3, 0, 0)` participantes, eliminadas e aguardando
antes da Ocorrência, e `(0, 1, 2)` depois, sem saída.

## A decisão

**O portão deixa de perguntar só se a Etapa anterior já produziu Resultado. Ele pergunta também se
ela pode produzir habilitação.** Se não pode, a exigência de habilitação fica dormente, haja ou não
Resultado nela, e a Etapa seguinte conserva o conjunto da `012`: todas as submetidas, menos as
eliminadas.

É o propósito que a própria Regra 2 escreve — o gate existe para que *"Etapa anterior de leitura
múltipla … não deixe a Etapa seguinte permanentemente sem participantes"* — levado ao caso que a
redação não previu.

## O que ela preserva

- **A Regra 1 continua absoluta.** Quem recebeu Ocorrência é `ELIMINADA` e sai de todas as Etapas
  seguintes, como hoje. A decisão só mexe na exigência de habilitação, e não na exclusão.
- **A Ocorrência continua aceita em Etapa que não consolida** (a I-1 de
  `resultados/application/ocorrencia.py`). A leitura 4, que a recusaria, foi descartada.
- **A publicação não muda.** A precedência não passa a contar como consumidor na `D-001` da `046`.
  A leitura 3 foi descartada, e a Etapa não exigida que precede outra continua publicável.
- **Etapa que pode habilitar não muda nada.** Nela o portão continua ligando com o primeiro
  Resultado, como a Regra 2 escreve hoje.

## O que ela não decide

- **Qual é a pergunta "pode produzir habilitação".** O candidato natural é o impedimento que a
  consolidação já calcula para a Etapa inteira — o mesmo que a `046` consulta, e não uma segunda
  redação dele. Confirmar isso é trabalho do incremento que implementar.
- **A Etapa que passa a poder habilitar depois**, por exemplo porque uma Retificação lhe deu regra.
  O portão acorda, e a Regra 2 já diz o que acontece com a Atribuição criada enquanto ele dormia:
  ela é preservada e volta a autorizar quando o Resultado habilitador existir. Se isso basta, o
  incremento que implementar precisa dizer.

## Consequências

- **A letra da Regra 2 da `D-003` da `013` precisa ser emendada.** Hoje ela diz *"a partir do
  primeiro Resultado da Etapa anterior"*, e é essa frase que o código segue. Implementar sem emendar
  deixaria o requisito e o código dizendo coisas diferentes. Pela regra do repositório, a emenda e
  a correção vão juntas num incremento em `specs/`, com teste que falhe sem ela. A reprodução de
  28/09 é o ponto de partida desse teste.
- **O aviso da `046`** *"Nada neste Edital depende dele"* volta a ser verdadeiro para a Etapa não
  exigida que precede outra.
- Até a implementação, o risco continua operacional. Ele só aparece se alguém registrar uma
  Ocorrência numa Etapa que não consolida e que precede outra.

## Implementação (28/09)

Feita no PR das correções antes do piloto, sem estender a decisão:

- **A pergunta "pode produzir habilitação" é `impedimento_da_regra`** — o impedimento que a
  consolidação aplica à Etapa inteira e que a `046` consulta para publicar, sem segunda redação.
  Toda Etapa que ele não impede produz `HABILITADA` para alguém. O impedimento do corte obsoleto
  ficou fora: é transitório, e o caminho dele é emitir a geração sucessora.
- **O lugar é o gate, e só ele**: `_exige_habilitacao_da_anterior`, em
  `resultados/application/prontidao.py`, usado pela listagem e pela rota individual.
- **A letra foi emendada junto**: a Regra 2 da `D-003` e a `FR-004` da `013`, e a `FR-042` que as
  repete.
- **A Etapa que passa a poder habilitar depois** — por Retificação que lhe dê regra — acorda o gate
  na vigência da versão nova, e a Regra 2 já diz o que acontece com a Atribuição criada enquanto
  ele dormia. Isso ficou escrito na emenda; nada além foi decidido.
- **O teste** é a reprodução de 28/09, invertida
  (`tests/integration/resultados/test_ocorrencia_em_etapa_inconsolidavel.py`): os dois cenários
  falham sem a mudança, e um terceiro prende que a Etapa que pode habilitar continua acordando o
  gate.
