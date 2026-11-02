# Research: Encerramento seguro do Edital (113)

*01/11/2026, sobre a árvore em `f90835e6`. O diagnóstico completo — reprodução, mapa do que cada ato lê,
contradições — está no [parecer](../../doc/parecer-a11-encerramento-do-edital-2026-11-01.md); aqui fica
só o que o plano decide.*

## R-001 — Onde mora a regra das situações

**Decisão.** Um módulo de aplicação novo, `processos/application/pendencias_do_edital.py`, com uma
função `situacoes(edital, *, agora, com_advertencias)` que devolve a lista de situações (espécie, tipo,
contagem, identificação). O command de encerramento chama com `com_advertencias=False`; a tela, com
`True`.

**Por quê.** O domínio (`processos/domain/finalizacao.py`) só recebe a lista pronta, como
`ensure_processo_can_be_closed` recebe os Editais pendentes. A interface não pode ser a dona — o
command não importa `interface` —, e a `099` (que hoje calcula os tipos em
`interface/relatorio_do_edital.py`) passa a importar daqui o que for comum.

**A direção de dependência é nova, e foi escolhida.** Hoje `processos` é a base: `recursos`,
`divulgacao` e `publicacoes` importam `processos.models`, e só o `seed_demo` importa no sentido
contrário. O módulo novo lê os três, porque é o encerramento — que mora em `processos` — quem precisa
da regra. Não há ciclo em tempo de carga (`processos.models` não importa aplicação nenhuma), mas para
que nenhum `import` de módulo de `processos` puxe as outras apps, os imports ficam **dentro das
funções**, como `recursos/application/interpor.py:288` já faz no sentido oposto. Mover a regra para
uma app de baixo obrigaria `processos/application/finalizacao.py` a importá-la de lá, que é a mesma
direção.

Os tipos da `099` passam a ser definidos aqui, e o relatório os importa: uma definição só (D-004 da
spec).

**Alternativas.** Calcular dentro de `ensure_edital_can_be_closed` (domínio fazendo consulta, contra o
padrão do arquivo); reutilizar `fatos_do_edital` no command (lê o relatório inteiro, ~0,3 s, sob trava
do Processo — custo e tempo de trava sem necessidade).

## R-002 — Cada impedimento, de que leitura existente sai

| Tipo | Leitura reaproveitada | Observação |
|---|---|---|
| `PERIODO_EM_CURSO`, `PERIODO_POR_ABRIR` | `inscricoes.domain.periodo.periodo_de_inscricoes(conteudo_vigente, agora)` — estados `ABERTO` com `fim`, e `FUTURO` | sem `fim` vira a advertência `PERIODO_SEM_TERMINO` (D-008 da spec) |
| `PRAZO_RECURSAL_EM_CURSO` | `divulgacao.domain.publicabilidade._janela_aberta` — a mesma conta que impede a publicação definitiva enquanto o prazo corre | promover a público (`janela_aberta_ate`), sem mudar a regra; percorrer os pares `(marco, lista)` com publicação de resultado do Edital |
| `RECURSO_AGUARDANDO` | `interface/acoes.py:_aguardando_decisao` | mover para `recursos/application/selectors.py` como `aguardando_decisao()`; `acoes` passa a importá-lo |
| `REAVALIACAO_PENDENTE`, `PROVIDENCIA_PENDENTE` | `recursos.application.selectors.reavaliacoes_pendentes_do_marco` e `providencias_pendentes_do_marco`, na forma de `relatorio_do_edital._pendencias_de_recurso` | mover `_pendencias_de_recurso` para o módulo novo; a `099` passa a chamá-lo |
| `RETIFICACAO_HOMOLOGADA` | `Retificacao.objects.filter(edital=, status=HOMOLOGADA)` | identificada por `created_at` |

**Advertências** (só a tela): as pendências de `fatos_do_edital` dos tipos `CONVOCACAO_AGUARDANDO`,
`CONVOCACAO_VENCIDA`, `RESULTADO_NAO_DIVULGADO`, `DEFINITIVO_NAO_PUBLICADO`, `APURACAO_DESATUALIZADA`
(FR-3535 — a mesma regra do relatório); mais `RETIFICACAO_EM_CURSO` (em elaboração ou revisão),
`PRAZO_RECURSAL_NAO_DECLARADO` (resultado vigente sem janela computável e marco que não negou recurso)
e `PERIODO_SEM_TERMINO`. No cancelamento, mais `RASCUNHOS_NAO_ENVIAVEIS` quando o período estiver
aberto.

**Por que a tela pode chamar `fatos_do_edital`.** É a regra das providências (D-004 da spec), e a
confirmação é tela rara. Custo medido pela `100`: ~0,3 s por Edital de 38 a 362 inscrições
(`doc/estudo-relatorio-consolidado-de-gestao-2026-10-24.md`), dentro do SC-1072.

## R-003 — Prazo recursal: qual janela, e qual "não declarado"

**Decisão.** Impede o par `(marco, lista)` cuja publicação vigente tem janela computável aberta
(`janela_aberta_ate` não nulo). Adverte o par cuja publicação vigente não tem janela computável e cujo
marco não declarou `admits: false`.

**Por quê.** É a janela que a interposição aplica (a decisão 005 da `047`, RC-121): uma regra, e não duas.
Sem janela declarada a interposição é aceita para sempre (`interpor._janela`: "sem norma não há prazo");
impedir por ela tornaria o encerramento impossível (D-002 da spec).

## R-004 — Ordem das travas

**Decisão.** `_finalize_edital` lê o `processo_id` do Edital sem trava, trava o `ProcessoSeletivo`
(`select_for_update`), depois o `Edital`, e só então confere situação e impedimentos. Vale para
encerrar e cancelar — o cancelamento não confere impedimentos, mas a ordem única evita duas ordens de
trava no mesmo par de linhas.

**Por quê.** Os escritores que criam ou resolvem impedimento travam o Processo — `interpor`
(`_travar_o_processo`), `admitir`/`julgar` (`porta.travar`), `publicar_resultado` (`publicar.py:113`),
`comando_de_comissao` —; os da Retificação travam Retificação, Edital e Processo num só `FOR UPDATE`
(A-09); o envio de inscrição trava o Edital `FOR SHARE`. Processo antes de Edital é a ordem de
`close_process`. Nenhum caminho da aplicação reatribui o Processo de um Edital, mas nenhum gatilho o
prende (o da `110` prende o escopo, não o vínculo); por isso, depois de travar o Edital, o command
confere que o `processo_id` relido é o do Processo travado, e recusa como conflito se não for.

**Risco.** O `FOR UPDATE` dos atos da Retificação adquire as três linhas na ordem do plano de execução.
Os dois testes de concorrência do A-09 (`test_encerramento_primeiro_a_publicacao_espera_e_recusa`,
`test_publicacao_primeiro_o_encerramento_espera_e_conclui`) cobrem o par; um teste novo cobre recurso
admitido em paralelo.

**Alternativas.** Advisory lock por Edital (trava nova, contra "nenhuma trava nova"); `SERIALIZABLE`
(muda o nível de isolamento de um command, e as recusas de serialização viriam como erro cru).

## R-005 — A recusa pela API

**Decisão.** `DomainError("pendencias_impeditivas", <frases separadas por "; ">, 409)`, como
`editais_pendentes` do Processo. O `detail` lista as frases; nenhum campo novo atravessa a API
(`DomainError` não leva extensão ao problem+json).

**Alternativa.** Campo estruturado na resposta: mudaria o contrato de problema para um caso só.

## R-006 — Os caminhos de cada situação

| Situação | Destino | Quem a tela de destino aceita | Sem acesso, a frase diz |
|---|---|---|---|
| período, prazo sem término | `interface:retificar` | `acoes.pode_retificar(edital, ator)` | "peça a quem elabora Retificações" |
| período (alternativa) | `interface:ato` cancelar | `edital:cancelar` | — |
| recurso aguardando | `interface:recursos` | `recurso:julgar` | "peça a quem julga recursos" |
| reavaliação, providência | `interface:marco` | a mesma pergunta de `_destinos_do_marco` | "peça à presidência da comissão" |
| Retificação homologada ou em curso | `interface:retificacao` | todo ator do escopo (`103`) | — |
| convocação | `interface:marco` (convocação) | idem reavaliação | idem |

Oferecer só o que a tela de destino aceita é a regra da `104`.

## R-007 — A Retificação parada

**Decisão.** `atos_retificacao.resumo` ganha `parada` quando o Edital está em `EDITAL_FINAL`; o parcial
`_retificacoes_em_curso.html` troca o bastão por "não pode mais prosseguir: o Edital foi encerrado" (ou
"cancelado") e não oferece "Continuar a elaboração".

## R-008 — Testes que chegam ao estado final por caminho que passará a ser recusado

Encerrar com período **com término** ainda por vir ou em curso, ou com prazo recursal em curso:

- `tests/integration/portal/test_desfecho_publico.py` — `test_encerrado_com_periodo_por_abrir_nunca_vai_para_as_proximas`
  (início em 5 dias, término em 15): passa a montar o estado por gravação direta do status, como
  fixture de dado anterior à regra, porque a exibição da `047` continua necessária;
- `tests/portal/test_prazo_recursal_publico.py::test_edital_encerrado_com_prazo_em_curso_continua_dizendo_o_prazo`:
  idem;
- `tests/integration/agenda/test_fonte.py::test_edital_cancelado_some_e_encerrado_so_mostra_o_que_passou`
  e `tests/fixtures/relatorio.py`: conferir na implementação; o final `pendente` encerra com convocação
  no prazo (advertência, segue válido).

O Edital padrão das fixtures declara início sem término (`tests/fixtures/edital.py:141`) — não impede
(D-008 da spec) —, e por isso os demais arquivos que encerram Edital recém-publicado não mudam.
