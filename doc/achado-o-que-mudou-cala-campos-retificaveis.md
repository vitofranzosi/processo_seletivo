# Achado — o "O que mudou" cala a maior parte dos campos retificáveis

Encontrado em 26/09/2026, ao corrigir o RC-39 da
[auditoria de consolidação](auditoria-de-consolidacao-2026-09-26.md). O RC-39 era um caso só: a
Retificação que restringiu o laudo ao Perfil C1 não aparecia no resumo público. Ao conferir o
dicionário do resumo contra o contrato de mutabilidade, que era a próxima ação que a auditoria
sugeria, apareceu a classe inteira.

> **Não vira escopo por estar escrito aqui.** A correção feita em 26/09 cobre só os dois campos do
> RC-39. O que se registra é o resto da classe, o que ela custa e o que corrigi-la exigiria.
> Priorizar é do usuário.

## O que se observou

O resumo público de cada Retificação, "O que mudou (N)" no portal, sai de
`publicacoes/domain/alteracoes.py`. O módulo traduz o caminho de cada `AlteracaoNormativa` por dois
dicionários, `COLECOES` e `CAMPOS`, e **cala** o caminho que não conhece. O silêncio é deliberado e
está escrito no módulo (D-009 da 024): uma linha a menos é honesta, e uma linha que diz a coisa
errada não é.

O custo do silêncio é que o dicionário precisa acompanhar o contrato. Ele não acompanhou.
`editais/domain/mutabilidade.py` declara quais campos publicados se retificam. Cruzando os
retificáveis com o dicionário, depois da correção do RC-39, **45 dos 84 campos retificáveis** não
produzem linha:

| Onde | Campos retificáveis sem linha |
|---|---|
| Edital (raiz) | `maxInscricoesPorCandidato`; `matriculationRequest/declarationText`; `drawMethod/…` (9: algoritmo, fonte, ocorrência, instante, derivação, normalização e regra de substituição) |
| Perfil | `generalCompetitionModalityId` (a ampla declarada), `vacancyReversion/kind`, `callForm` |
| Modalidade de concorrência | `description`; `normativeRule/foundation`, `/version`, `/percentage`, `/effectiveFrom` |
| Linha do quadro de vagas | `modalityId`, `immediateVacancies` — a coleção inteira não está em `COLECOES` |
| Fato declarado | `label` |
| Marco de classificação | 22: `name`, `orderProduction`, `operation`, `normalization`, `rounding/…`, `appealWindow/…` (3), `drawMethod/…` (10) e `cutRule/…` (3) |
| Critério de desempate | `order` |

A contagem é a do cruzamento em `8e7c698` (a `main` depois do #183). Foram conferidas por
`alteracao_legivel` oito amostras — vagas do quadro, percentual da cota, prazo recursal, fonte do
sorteio, rótulo do fato, ampla declarada, teto por candidato e sorteio comum —, e as oito devolvem
`None`.

**Já está na suíte, sem que ninguém tenha notado.** `mais_uma_vaga`, em
`tests/integration/portal/test_historico_publico.py`, retifica duas coisas no mesmo ato: as vagas do
Perfil e a linha geral do quadro. O portal lista uma, "O que mudou (1)". O teste confere que a
primeira aparece e não confere o contador.

## O que isso custa

A FR-130 da 024 diz que cada Retificação exibida MUST trazer "a identificação do que foi alterado,
dita em termos do Edital". O que foi omitido é, em boa parte, o que mais pesa para quem se inscreve:

- **o percentual da cota** e o fundamento dela;
- **as vagas por lista de concorrência**, que são o quadro de vagas;
- **o prazo recursal** do marco;
- **o método do sorteio**, que a D-G3 tornou declaração pública;
- **a regra de corte**, que decide quem prossegue.

O documento da Retificação continua completo e alcançável na mesma linha do histórico. O que falha
é o resumo, e ele falha em silêncio: o contador diz "(1)" onde o ato alterou dois campos, e nada na
tela avisa que há mais.

## Por que nenhum guardião viu

`tests/unit/publicacoes/test_alteracoes_legiveis.py` confere uma linha por coleção e confere o
silêncio para o caminho inventado. Não há teste que ligue o dicionário ao contrato. O guardião do
contrato, `tests/contract/test_mutabilidade.py`, cobra que todo campo publicado tenha natureza
declarada, e não que o campo retificável tenha tradução. Um campo novo entra no contrato, passa na
Retificação e some do resumo, e nenhuma das duas pontas reprova.

## O que corrigir exigiria

1. **Rótulos para os 45 campos**, com o vocabulário da tela da Retificação da gestão
   (`interface/retificacao.py`), para que quem retifica e quem se inscreve leiam o mesmo nome. As
   coleções que faltam — a linha do quadro de vagas — entram em `COLECOES`.
2. **Os campos compostos** (`normativeRule/percentage`, `appealWindow/durationDays`,
   `drawMethod/source`) pedem que o tradutor leia mais de um segmento depois da entidade. Hoje ele
   lê um só (`resto[2]`), e `normativeRule` sozinho não diz qual das quatro partes mudou.
3. **O guardião que faltava**: para cada par retificável do contrato, sintetizar um caminho e exigir
   linha. Com ele, campo novo no contrato sem tradução reprova no dia em que nasce.
4. **O contador do teste de histórico**: `mais_uma_vaga` passaria a afirmar "O que mudou (2)".

## O que foi feito em 26/09

Só o RC-39. `profileId` ("Exigido apenas do Perfil") e `modalityId` ("Exigido apenas da
modalidade") do Documento Exigido entraram em `CAMPOS`, com os rótulos da tela da gestão. Há um
teste de unidade e um de integração no portal, com contraprova.
