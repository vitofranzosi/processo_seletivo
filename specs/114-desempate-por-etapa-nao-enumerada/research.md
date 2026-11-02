# Research: Desempate pela nota de Etapa que o marco não enumera

## R-001 — Onde a separação "pontuação × consequência" mora

- **Decision**: em `universo_classificavel.preparar`. Ele recebe os Resultados de todas as Etapas lidas e
  monta `pontuacoes` com todos; a eliminação mais recente é procurada só entre os Resultados de Etapas
  enumeradas.
- **Rationale**: é a função que o caminho oficial e a prévia já chamam (094). Separar no chamador
  (duas listas de Resultados) obrigaria a prévia e o oficial a repetir a mesma partição, e a primeira
  divergência seria silenciosa.
- **Alternatives considered**: filtrar a consequência na consulta (duas consultas, ou uma com anotação) —
  descartada por custo e por espalhar a regra; deixar `preparar` como está e acrescentar uma segunda
  lista `pontuacoes_do_desempate` ao inscrito — descartada porque `desempate._valor_do_criterio` já lê
  `pontuacoes`, e uma segunda chave criaria dois lugares onde a nota de uma Etapa pode estar.

## R-002 — Quais Etapas são "do desempate"

- **Decision**: `desempate.etapas_do_desempate(marco)` devolve os `stageId` dos critérios
  "maior pontuação numa Etapa" que o marco não enumera, sem repetição, na ordem dos critérios.
- **Rationale**: o cálculo, a prévia e a migration (em SQL) precisam da mesma resposta. Uma função só, no
  módulo que define o tipo do critério.
- **Alternatives considered**: ler todas as Etapas do Edital — descartada: o universo citaria Resultados
  que nada leu, e a conferência no banco teria de aceitar qualquer Etapa.

## R-003 — A conferência no banco

- **Decision**: migration `classificacao/0007` com `CREATE OR REPLACE FUNCTION
  check_ordering_act_provenance()`. O `NOT EXISTS` sobre `marco -> 'stages'` passa a olhar também
  `jsonb_path_query(marco, '$.tiebreakers[*] ? (@.type == "MAIOR_PONTUACAO_NA_ETAPA").parameters.stageId')`.
  A reversão restaura o texto exato da `0003`.
- **Rationale**: a `0003` não se reescreve (Constituição). A conferência continua set-based, uma vez por
  ato. O texto da `0003` é copiado, e não importado, porque módulo de migration com nome numérico não se
  importa limpo e a cópia congela o estado que a reversão precisa restaurar.
- **Alternatives considered**: remover a conferência de Etapa — descartada; ela é a garantia da `015`
  de que o universo só cita o que a regra lê.

## R-004 — A reprodução do ato

- **Decision**: `reproducao.reproduzir_ato` procura a eliminação só entre os Resultados citados de Etapas
  enumeradas pelo marco da versão histórica. As pontuações continuam vindo de todos os citados.
- **Rationale**: o ato cita a Etapa do desempate, e uma eliminação ali não pode reaparecer na
  reprodução (FR-3552). A regra é a do preparo, numa função só (`que_decidem_posicao`).
- **Alternatives considered**: reescrever a reprodução sobre `preparar` — maior e fora do que a spec
  pede; o motivo gravado (`snapshot.motivo`) é lido de outro lugar, e a troca mudaria a reprodução de
  todo ato do acervo.

## R-005 — O corte e o reingresso

- **Decision**: sem mudança de código. `corte._reingressou` deriva as "Etapas que produziram a ordem" do
  `stageResults` do ato; a Etapa do desempate passa a estar lá quando o ato cita Resultado dela.
- **Rationale**: uma nota corrigida por recurso na Etapa do desempate **move posição**, e a regra da
  `014` (FR-230 da `014`: o deferimento que não alcança o ato não obsoleta o corte) foi escrita para a
  Etapa governada que não move nada. Aqui o deferimento alcança o ato, e obsoletar a geração é o
  comportamento da regra, não exceção a ela. Quando a Etapa governada pelo corte é também a do
  desempate, o percurso é: corte emitido sem as notas → notas consolidadas → ordem obsoleta (FR-3550) →
  sucessora → geração sucessora. É a decisão D-004 da spec, aceita pelo usuário.
- **Alternatives considered**: excluir a Etapa do desempate do reingresso — deixaria uma faixa produzida
  por uma ordem que já não é a da norma sem causa nomeada.

## R-006 — A nota fictícia na prévia

- **Decision**: depois de gerar os candidatos, `cenarios_da_previa.com_notas_do_desempate` dá a cada um,
  em cada Etapa do desempate com nota, a **menor** das suas notas fictícias nas Etapas enumeradas (ou
  nada, quando alguma falta). A prévia passa a montar `etapas_do_desempate` e chama a função nos dois
  modos.
- **Rationale**: D-006 da spec. Candidatos iguais nas enumeradas ficam iguais na do desempate, e os casos
  da `094`/`095` continuam exercitando o que nomeiam. A menor, e não a soma, porque a soma de duas
  notas passaria da escala de uma Etapa de nota máxima 100, e o lado oficial da equivalência grava
  essa nota pelo caminho normal. Não depende de seed.
- **Alternatives considered**: nota sorteada por slot — desfaria o "par igual em tudo" e mudaria o
  sentido dos casos-limite; a soma — sai da escala (acima); nenhuma nota — a prévia mostraria um
  critério que nunca lê nada, o próprio defeito do A11 visto pela prévia.
- **Consequência registrada**: como os empatados de propósito são iguais também na Etapa do desempate,
  nenhum caso da prévia mostrava esse critério separando alguém. É por isso que a equivalência da
  FR-3556 compara também a nota que o desempate leu de cada classificável — e por isso a revisão de
  02/11 acrescentou o caso da R-007.

## R-007 — O caso demonstrativo da prévia (revisão de 02/11)

- **Decision**: `cenarios_da_previa.caso_do_desempate` planta, sobre a classificação sem empate, um par
  igual nas notas enumeradas **e nos fatos**, na última posição do alvo, e dá ao segundo do par três
  pontos a mais na Etapa do desempate. `com_notas_do_desempate` passa a preencher só o que falta, para
  não desfazer o par. O caso fica em `CASOS_DO_DESEMPATE` e só é oferecido quando o marco desempata por
  Etapa com nota que não enumera (`previa.etapas_do_desempate_com_nota`).
- **Rationale**: igual nos fatos, o par não é separado por nenhum critério anterior, qualquer que seja a
  ordem publicada; a vantagem no segundo inverte a ordem das linhas, e a inversão não pode vir de
  desempate oculto por posição. Sobre a classificação sem empate, é o único empate da tabela.
- **Alternatives considered**: mudar a D-006 para dar notas diferentes aos empatados dos casos que já
  existem — descartada: eles deixariam de significar o que nomeiam (FR-3558); oferecer o caso sempre —
  descartada: num marco sem o critério, o par plantado ficaria empatado e o caso diria o contrário do
  rótulo.

## R-008 — A pertinência dos recursos (revisão de 02/11)

- **Decision**: `desempate.etapas_que_a_ordem_le(marco)` — enumeradas mais as do desempate — é a
  resposta única de "esta nota alcança esta ordem?". O cálculo, o filtro da Supervisão e a pertinência
  dos recursos (`recursos.selectors._etapas_do_marco`) a chamam; a `0007` estende também a
  `check_decision_citation_coherence` da `0004`, com o mesmo `CASE` sobre `tiebreakers`.
- **Rationale**: as três pendências da definitiva — recurso, reavaliação, providência — já eram
  perguntas sobre "as Etapas do marco"; trocar a resposta num lugar só as fecha juntas. Sem a mudança na
  trigger da citação, a providência pertinente nunca se cumpriria: o ato que a cita seria recusado.
- **Alternatives considered**: todas as Etapas do Edital — descartada pelo usuário ("dependência
  efetiva, e não indiscriminadamente"); abrir também a visibilidade e a janela recursal da nota —
  decisão sobre acesso e prazo, deixada ao usuário (D-005).

## R-009 — O corte que governa a Etapa do desempate (revisão de 02/11)

- **Decision**: nenhuma regra nova. O percurso foi demonstrado em teste para o empate dentro da faixa e
  para os dois desfechos do empate na fronteira, e o conflito ficou registrado na D-007.
- **Rationale**: a obsolescência da ordem (FR-3550), a da faixa por ordem sucedida e o bloqueio de
  trabalho novo na Etapa governada já existiam e compõem o percurso; o que falta é uma decisão de
  domínio sobre o excedente, e inventá-la seria criar norma.
- **Alternatives considered**: congelar a faixa da primeira geração quando o corte governa a Etapa do
  desempate, ou recusar a geração sucessora que estreite a faixa — as duas são respostas possíveis à
  D-007, e nenhuma foi decidida.
