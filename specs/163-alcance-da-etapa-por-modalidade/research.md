# Research: O alcance da Etapa por Modalidade

As decisões de produto estão na spec (`D-001` a `D-010`). Aqui ficam as técnicas, `T-NNN`, cada uma
com o que foi escolhido, por quê, e o que foi descartado. Os caminhos são relativos a
`backend/processo_seletivo/`.

## T-001 — Uma coluna `JSONField` anulável na Etapa, e não uma tabela

**Decisão.** `EtapaAvaliacao.alcance = JSONField(null=True, blank=True)`: `NULL` é *"todas as
inscrições"*; uma lista de códigos de Modalidade, sem repetição, é a forma restrita. Um
`CheckConstraint` recusa a lista vazia no banco, como segunda barreira da FR-6962; a primeira é
`validate_stage`.

**Por quê.** O alcance é um conjunto pequeno de textos, sem identidade própria, que só se lê junto da
Etapa. A gravação do rascunho apaga e recria as Etapas a cada `replace_draft`; uma tabela filha
precisaria ser recriada junto, como os critérios da `146`, sem ganho: ninguém endereça um item do
alcance isoladamente. `JSONField` já é a grafia de listas de texto no Perfil (`requirements`) e
funciona no SQLite de fallback.

**Descartados.** Tabela `AlcanceDaEtapa` (custo de recriação sem endereçamento); `ArrayField` (só
PostgreSQL, e a suíte ainda coleta no SQLite); coluna de texto com separador (uma segunda grafia de
lista).

## T-002 — `modalityCodes` no conteúdo publicado, degrau 22

**Decisão.** Cada item de `stages` ganha `modalityCodes`: `null` ou a lista **ordenada** dos códigos.
`SCHEMA_VERSION` vai a 22, e `elevacao.DEGRAUS[22] = {"modalityCodes": None}`.

**Por quê.** Ordenar torna o resumo canônico independente da ordem em que alguém marcou. `null` é a
verdade sobre todo Edital publicado antes do degrau: a capacidade não existia, e toda Etapa alcançava
todas. Conversão sem invenção, no molde dos degraus 17 (o `modalityCode` do Documento Exigido) e 21
(os critérios da Etapa). O nome segue o `modalityCode` da `044`, no plural, porque o conteúdo é o
mesmo — o código estrutural da Modalidade.

**Descartado.** Publicar a lista de todos os códigos quando "todas" (D-002 da spec).

## T-003 — Um módulo puro, `editais/domain/alcance.py`

**Decisão.** Funções puras sobre o conteúdo publicado (ou o rascunho, que tem a mesma forma):

- `codigos(etapa)` → `None` ou `frozenset` de códigos, aceitando a Etapa do conteúdo e a do modelo;
- `alcanca(etapa, codigo_da_modalidade)` → `bool`; `codigo` `None` (ampla) só é alcançado por `None`;
- `modalidades_alcancadas(conteudo, etapa)` → `None` ou `frozenset` de **identidades** de Modalidade,
  varrendo `profiles[].competitionModalities` pelo código;
- `restrita(etapa)` → `bool`;
- `descrever(conteudo, etapa)` → as denominações e os Perfis de cada código, para a Revisão, o
  documento e a composição.

**Por quê.** Três camadas fazem a mesma pergunta — a validação da publicação (sobre o conteúdo), a
participação (sobre a consulta) e as telas. Uma resposta só impede que divirjam. As identidades saem
do conteúdo publicado, e não do banco, porque a inscrição guarda `modality_id`, e o código é o que o
conteúdo publicado diz que aquela identidade tem.

## T-004 — A quarta regra de participação, no ponto único

**Decisão.** `restringir_a_participantes`, `participa_da_etapa` e `participacao_detalhada`
(`resultados/application/prontidao.py`) ganham a condição `modality_id IN modalidades_alcancadas`
quando a Etapa é restrita. A partição do panorama ganha o estado `FORA_DO_ALCANCE`, no molde de
`FORA_DO_CORTE`, e `motivo_de_nao_participar` ganha o motivo. Nada muda quando a Etapa alcança todas.

**Por quê.** O mapeamento dos consumidores (13/11) mostrou que distribuição, rodízio, Mesa, carga,
próxima pendente, Ocorrência, consolidação, andamento, supervisão e Minhas atividades passam todos
por essas três funções. Pôr a regra ali é o que a `014` fez com a faixa do corte, e o que garante a
FR-6973, a FR-6975, a FR-6976 e a FR-6978 sem tocar em cada superfície.

## T-005 — A habilitação da anterior, lida na anterior que alcança

**Decisão.** `_anteriores_e_gate` deixa de devolver **uma** Etapa a exigir, e passa a devolver os
**casos** da exigência: para cada Etapa anterior `E_k`, do mais próximo ao mais distante, o conjunto
de Modalidades para o qual `E_k` é a última anterior que alcança. A condição vira uma disjunção de
`Q`: `(modality_id ∈ casos_k) ∧ Exists(HABILITADA em E_k)`, só para os `E_k` cujo gate vigora (regra
pode habilitar e já há Resultado), mais o caso de quem nenhuma anterior alcança, sem exigência.
`etapa_anterior_que_alcanca` nasce em `resultados/domain/progressao.py`, pura.

Quando nenhuma Etapa anterior é restrita, há um caso só, com todas as Modalidades, e a consulta é a de
hoje — nenhum `EXISTS` a mais, e os orçamentos de consulta continuam valendo.

**Por quê.** É a FR-6972: a Etapa que não alcança a inscrição não existe na progressão dela. A
eliminação anterior (Regra 1) não precisa de mudança, porque quem não é alcançado não tem Resultado
naquela Etapa.

**Descartado.** Materializar a lista de inscrições por caso e filtrar por `id__in` — duas leituras da
população por listagem, que é o que os orçamentos de consulta da `011` e da `012` existem para
impedir.

## T-006 — O universo da ordem, pela última enumerada que alcança

**Decisão.** `classificacao/application/calculo._universo` deixa de perguntar só à última Etapa
enumerada. Percorre as enumeradas da última para a primeira: cada uma decide sobre as Modalidades
que alcança e que nenhuma posterior decidiu; a sobra (quem nenhuma alcança) entra como entraria
num marco sem Etapa — a inscrição submetida do Perfil. A união sai em uma consulta, por `Q`.

**Por quê.** FR-6985. Com a Heteroidentificação como última enumerada, a consulta de hoje
devolveria só os `PPI`, e a ordem da ampla sairia vazia.

**Consequência na spec.** A Etapa restrita **pontuada** enumerada por um marco mandaria a "sem
posição" (`universo_classificavel.py`) quem ela não alcança; a decisória é pulada, como hoje é pulada
quando não há Resultado. Daí a FR-6964 ter ganhado o caso *"pontuada e enumerada por um marco"*.

## T-007 — Os achados de publicação, um aviso de rascunho

**Decisão.** Em `editais/domain/validation.py`, achados `BLOCKING_ERROR` nos atos de publicação e de
Retificação:

| Código | Quando |
|---|---|
| `alcance_codigo_inexistente` | código do alcance que nenhum Perfil tem (FR-6963) |
| `alcance_em_papel_de_todos` | Etapa restrita classificatória, com peso, comparada por critério de desempate, pontuada e enumerada por marco, governada por corte ou de habilitação ao sorteio (FR-6964) |
| `alcance_alcanca_a_ampla` | código que algum Perfil declara como a sua ampla concorrência (FR-6968) |
| `alcance_denominacao_divergente` | mesmo código com denominações diferentes entre Perfis (FR-6965) |

A coerência de denominação reaproveita a função da `044`, estendida para os códigos referidos pelo
alcance — não se reescreve. O código inexistente vira **aviso** na gravação do rascunho
(`draft._pendencias`), porque o rascunho pode estar pela metade.

`validate_stage` recusa, na gravação, a lista vazia, o código repetido e o item que não é texto
(FR-6962).

## T-008 — A Retificação que estreita, recusada; serializada com a distribuição

**Decisão.** `publicacoes/application/retificacoes.py` ganha
`_recusar_alcance_estreitado_sobre_atribuicao`, no molde de `_recusar_corte_sobre_etapa_com_resultado`
(`048`): para cada Etapa cujo alcance perde Modalidades entre a base e o conteúdo novo, conta as
inscrições dessas Modalidades com `Atribuicao` não removida ou `ResultadoEtapa` vigente na Etapa. Se
houver, `DomainError("stage_scope_narrowed_over_assigned", ..., 422)`. A recusa roda na gravação da
Retificação **e** de novo na publicação, sob o bloqueio do Edital.

A distribuição passa a tomar `select_for_update` na linha do `Edital` antes de ler a participação
(`_edital_do_processo`). Com os dois atos bloqueando a mesma linha, vale o cenário 6 da US5: ou a
Atribuição entra primeiro e a publicação da Retificação é recusada, ou a Retificação é publicada
primeiro e a distribuição lê o alcance novo.

**Por quê.** Clarify de 13/11 (recusar). A conferência só na gravação deixaria a janela entre gravar
e publicar.

## T-009 — O campo na tela de Retificação

**Decisão.** `CAMPOS_ETAPA` (`interface/retificacao.py`) ganha `("modalityCodes", "Modalidades que a
Etapa alcança", ALCANCE)`, um tipo de campo novo que se apresenta como na composição (duas opções e
os códigos do conteúdo) e se lê de volta como `None` ou lista ordenada. O teste de contrato que guarda
`CAMPOS_ETAPA` contra o próximo campo é atualizado.

## T-010 — O documento e a Revisão

**Decisão.** Uma função, `frase_do_alcance(conteudo, etapa)`, devolve `""` para a Etapa que alcança
todas, e, para a restrita: *"Aplica-se somente aos candidatos inscritos nas modalidades Pretos e
pardos (PPI) e Pessoas com deficiência (PcD)."* A redação 1 a imprime como par *"Alcance"*; as
redações 2 e 3, como frase depois da `frase_da_etapa`. A Revisão, a página pública
(`apresentacao.py`) e a tela de Retificação usam a mesma função.

**Por quê.** SC-2310: com a frase vazia para "todas", o documento do acervo se recompõe byte a byte.

## T-011 — A publicação das inscrições e o reingresso

**Decisão.** Em `divulgacao/application/inscricoes.py`, a Etapa restrita sai das candidatas a Etapa
de análise, e a escolha explícita dela é recusada com `inscricoes_etapa_invalida` e mensagem própria
(FR-6987). Em `divulgacao/domain/publicabilidade.reingressos_pendentes`, a inscrição fora do alcance
de uma Etapa enumerada não conta como pendente nela (FR-6986).

## T-012 — O que não muda

- **Ocupação e sorteio** leem `HABILITADA` da Etapa governada e da de habilitação; a FR-6964 impede
  que sejam restritas, e por isso os leitores não mudam.
- **Portal**: `situacao_da_inscricao` mostra só Etapas com Resultado visível, e a inscrição fora do
  alcance não tem Resultado na Etapa. A FR-6982 se verifica por teste, sem código novo.
- **Recursos**: só alcançam Resultado existente.
- **Relatório do Edital**: conta Resultados existentes, sem denominador.
- **Reaproveitamento e duplicação** levam o alcance com o resto da Etapa, como levam os critérios.
