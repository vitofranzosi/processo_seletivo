# Research — 046 · Contrato de executabilidade do Processo publicado

**Spec**: [spec.md](spec.md) · **Plano**: [plan.md](plan.md) · Conferido contra a `main` em `aeb575a`.

As decisões de domínio estão na spec (`D-001` a `D-005`). Aqui ficam as de desenho, cada uma com a
alternativa descartada, e a medição que decidiu a ordem de entrega.

---

## R-1 — A Etapa: uma função nova na validação, que consulta a regra da consolidação

**Decisão**: uma função `_etapa_sem_resultado(snapshot, *, ato)` em
`editais/domain/validation.py`, chamada por `validate_for_publication` ao lado de
`_marco_sem_regra_de_corte`. Para cada Etapa, pergunta a `resultados.domain.regra.impedimento_da_regra`
se ela se consolida; se não, pergunta se o Resultado é exigido (`R-2`) e emite o código do
[contrato](contracts/o-gate-da-publicacao.md) conforme o ato.

**A importação é local, dentro da função**, como `validation.py` já faz com `classificacao.domain`,
`publicacoes.domain` e `ocupacao.domain` (`:592`, `:816`, `:1009`, `:1045`). `resultados/domain/regra.py`
importa só `avaliacoes/domain/formas` e `previsao`, que importam só `django.db.models`: não há ciclo.

**A tensão, registrada.** `avaliacoes/domain/formas.py:12-15` diz que *"`editais` não os importa: ele
confere a string publicada contra o contrato, e não conhece o domínio da conclusão"*. A função nova
não quebra a frase — ela não lê `Forma` nem `Sentido`, nem interpreta a forma: pergunta a quem
conhece. A alternativa que respeitaria a direção à risca era copiar os três predicados para `editais`,
e é exatamente a duplicação que a `FR-747` proíbe. A dependência nova é de **uma função pura**, e o
comentário da função nova registra por que ela existe.

**Descartadas**:

- **Mover a verificação para `publicacoes/application`** (onde `submit_edital` já orquestra). A Revisão
  do assistente lê `validate_for_publication` por `_pendencias`, e não passa por `publicacoes`: a
  recusa existiria no ato e não na tela que a antecipa — o defeito que a `032` existiu para corrigir.
- **Mover `impedimento_da_regra` para `editais`.** Ela é regra da consolidação, lida por
  `resultados/application/prontidao.py:504` e `recursos/domain/consequencia.py:71`; trazê-la para cá
  inverteria a dependência dos dois consumidores que a usam de verdade.

## R-2 — Quem exige o Resultado: quatro leituras de declaração, nenhuma de execução

**Decisão**: um conjunto de identidades de Etapa referenciadas, montado uma vez por conteúdo, a
partir dos marcos bem formados (`_perfis_bem_formados`, `_marcos_bem_formados`):

| Leitura | Função que já existe |
|---|---|
| enumerada | `marco["stages"]` |
| governada | `classificacao.domain.faixa.etapa_governada(marco["cutRule"])` — devolve `None` para `NONE` |
| habilitação do sorteio | `editais.domain.marcos.metodo_que_governa(...)["qualifyingStageId"]` — próprio ou comum |

Mais o caráter eliminatório, lido por `regra.eliminatoria(etapa)` — a mesma função que a consolidação
usa. **Nenhuma** leitura de banco, de Resultado ou de inscrição: é declaração publicada, e por isso é
invariante estrutural (spec, tabela *"O que o gate verifica"*).

**Não entra a precedência entre Etapas.** A progressão só exige habilitação na anterior depois que ela
produziu algum Resultado (`prontidao.py:150-154`); o risco que isso deixa é o `A-1`, operacional.

**Enumeração por marco de sorteio conta.** O marco de sorteio enumera Etapa sem consumi-la
(`faixa.py:93-97`), mas distinguir aqui exigiria ler a forma da ordem — mais uma leitura que a
`FR-747` não pede. Erra pelo lado que recusa, e a correção está ao alcance de quem compõe (spec,
*Edge Cases*).

## R-3 — Dois códigos, e a #117 não precisa ser tocada

**Decisão**: `stage_result_unreachable` (impeditivo, só publicação) e `stage_without_result` (aviso na
publicação quando nada exige; advertência na Retificação sempre).

**Por quê**: `advertencias_do_ato` (`retificacoes.py:583-588`) subtrai da lista da Retificação os
**códigos** que impediriam a publicação. Com um código só em duas severidades, a advertência da
Retificação cairia na subtração sempre que a mesma Etapa fosse exigida — o cenário abstrato da issue
#117 tornado concreto. Com dois códigos, `stage_result_unreachable` nunca aparece na lista da
Retificação, e `stage_without_result` nunca está no conjunto subtraído.

E há um guarda que já cobra isso: `test_invariantes_da_declaracao_unica.py:145-157` prende que, num
mesmo ato, avisos e impeditivos não compartilham código. O desenho de um código só o quebraria.

**A #117 fica aberta**, como estava: a `046` satisfaz a `FR-751` sem depender da correção dela. É o que
a `045` também concluiu para o aviso dela (`R-5` de lá). Trocar a chave da subtração por `(código,
caminho)` continua sendo a correção certa para o dia em que um código precisar das duas severidades
— e esta feature não é esse dia.

**Descartada**: corrigir a #117 filtrando `advertencias_do_ato` pela severidade do próprio ato. É
equivalente para todo código de hoje, mas muda o comportamento de uma função que a `027` e a `028`
prendem por teste, sem que nenhum requisito desta feature precise.

## R-4 — O Perfil: uma função nova, e a supressão do aviso por marco

**Decisão**: `_perfil_sem_corte(snapshot, *, ato)` ao lado de `_perfil_sem_marco`, com a mesma forma:
só no ato de publicação, só para Perfil **com** marco (o sem marco é da `FR-457` da `032`, e empilhar
duas recusas sobre a mesma causa esconde a que resolve). `_marco_sem_regra_de_corte` passa a pular o
Perfil em que nenhum marco corta.

**"Declara regra de corte"** é `bool(marco.get("cutRule"))` — a mesma truthiness que
`_marco_sem_regra_de_corte` usa. Regra que não governa Etapa é regra declarada (`FR-752`).

**Descartada**: manter os avisos por marco junto com a recusa por Perfil. Um Perfil de três marcos sem
corte produziria quatro linhas na Revisão para uma causa, e a que resolve — *"declare em ao menos
um"* — ficaria no meio.

## R-5 — O Edital publicado: um ponto, e ele é `_pendencias`

**Decisão**: `_pendencias` (`interface/views.py:816`), quando o Edital não está em `EM_ELABORACAO`,
`EM_REVISAO` ou `HOMOLOGADO`, devolve **só** os achados cujo código está numa lista fechada de fatos
do conteúdo publicado — `FATOS_DO_CONTEUDO_PUBLICADO = {"stage_without_schedule_event"}`, ao lado de
`_pendencias`. As três chamadas (`detalhe`, `compor_etapa`, `praticar_ato`) passam a respeitar a regra
sem mudança própria.

**Por que lista, e não "todo aviso"** (`D-003`): o aviso `schedule_event_in_past` diz *"o Edital será
publicado com esta data"* — é aviso, e é juízo de publicabilidade. Filtrar por severidade deixaria o
texto falso que o protótipo reproduziu. A lista nomeia o que uma spec mandou dizer na página publicada,
e cresce por decisão, não por semelhança.

**O relacional, e o que isso custa**: a página do Edital publicado continua montando o snapshot do
relacional, que guarda o estado do dia da publicação. Para o único fato da lista não faz diferença —
`scheduleEventId` é estrutural (`026`) e nenhuma Retificação o muda, como a `R-5` da `045` já
registrou. Um fato que a Retificação alcance não pode entrar na lista sem trocar a fonte para a versão
vigente.

**A varredura da `FR-756`**: um teste que percorre `backend/processo_seletivo/**/*.py` e prende a lista
fechada de quem chama `validate_for_publication(` — o do [contrato](contracts/o-gate-da-publicacao.md),
§3. Mesmo padrão de `tests/test_vigencia_do_resultado.py`. Chamador novo exige mudar a lista, e com ela
a decisão.

**Descartadas**:

- **Validar o conteúdo vigente com o ato da Retificação** na tela do Edital (a primeira saída da
  auditoria). Ver `D-003`.
- **Esconder a seção no template** por estado. A previsão de recusa (`acoes._motivo_previsivel`)
  continuaria recebendo impeditivos de um Edital publicado; hoje ela não os usa, mas a próxima tela que
  usar herdaria a informação falsa.

## R-6 — A fonte de demonstração: vocabulário por ambiente, uma leitura só

**Decisão**:

1. `config/settings/base.py`: `SORTEIO_FONTE_DE_DEMONSTRACAO`, lida do ambiente, **falsa** por padrão.
2. `config/settings/development.py` e `config/settings/test.py`: `SORTEIO_FONTE_DE_DEMONSTRACAO = True`,
   sem variável — são módulos que produção nunca carrega.
3. `config/settings/production.py`: `_exigir(not SORTEIO_FONTE_DE_DEMONSTRACAO, …)`, ao lado das duas
   barreiras de identidade.
4. `sorteios/infrastructure/fontes/__init__.py`: `FONTES` deixa de ser um dicionário fixo e passa a
   ser lido por uma função — `fontes_publicadas()` — que inclui a demonstração só quando a
   configuração a liga. Os três leitores (`interface/forms.py:318`, `editais/domain/perfis.py:534`,
   `fonte_declarada`) passam a chamá-la.

**Por que função e não dicionário montado na importação**: o dicionário seria congelado no primeiro
import, e `override_settings` — que os testes da barreira precisam para exercitar produção dentro da
suíte — não o alcançaria.

**Por que desenvolvimento liga pelo módulo, e não pelo `.env`**: o seletor de identidade exige variável
porque é segurança de acesso e o `.env.example` a traz; a fonte de demonstração é o que torna
`seed_demo` e o `quickstart` executáveis sem rede. Exigir mais uma linha de `.env` para o sorteio da
demonstração funcionar seria a armadilha que o `CLAUDE.md` descreve — *"nada carrega `backend/.env`
sozinho"*. O compose e o `manage.py` já caem em `config.settings.development`.

**A escolha do adaptador continua pelo nome publicado**, como a `021` exige: o ambiente decide só se o
nome existe no vocabulário, nunca para onde ele aponta.

**Descartadas**:

- **Só a barreira de boot** (a sugestão literal da auditoria). Sem tirar o nome do vocabulário, a
  barreira não teria o que vigiar: a fonte é escolhida no seletor, e não por variável.
- **Tirar a fonte do código de produção e mandar os testes injetarem o adaptador.** A observação já
  aceita `fonte_externa` (`ocorrencia.py:68`), mas `seed_demo` e o roteiro do `quickstart` rodam pela
  tela, onde não há injeção — e mais de trinta arquivos de teste declaram a fonte pelo nome.

## R-7 — O que a medição disse sobre a suíte

**Como se mediu.** Em 26/09, sobre `aeb575a`, um protótipo das duas regras entrou em
`validate_for_publication` **sem bloquear**: cada submissão que seria recusada gravou, num registro, o
caso de teste e a causa. O protótipo do `RC-32` entrou de verdade em `_pendencias`. A suíte inteira
rodou contra PostgreSQL — **7834 passaram, 3 falharam, 11 pulados**, em 15m38s — e o protótipo foi
revertido. (Uma primeira rodada com as regras **bloqueando** foi interrompida a 34%, com 872 erros:
confirmou o bloco, e não disse a causa.)

**1457 casos (19% da suíte), em 191 arquivos, teriam a submissão recusada.** A causa é uma só por
família, e mora em fixture — a memória *"regra impeditiva quebra a suíte em bloco"* se confirmou:

| Causa | Casos | Arquivos | Origem |
|---|---|---|---|
| Perfil sem marco que corte | 759 (571 só por ela) | 104 | marcos sem `cutRule` em `tests/fixtures/selecao.py`, `divulgacao.py`, `sorteio.py`, `supervisao.py`; e o Perfil de sorteio do `seed_demo` (`seed_demo.py:542`) |
| Etapa eliminatória, pontuada, sem nota mínima | 608 | 96 | `tests/fixtures/comissao.py::etapas` — a *Análise documental* nasce assim por padrão |
| Etapa eliminatória com duas avaliações | 210 | 30 | `etapas(avaliacoes=2)` — os testes da Mesa, da distribuição e da trilha |
| Etapa enumerada com duas avaliações | 68 | 3 | os três arquivos do reaproveitamento |

**A fixture central publica, há semanas, o Edital que esta feature recusa.** O docstring de
`comissao.etapas` já o sabia: *"a maioria dos testes fala de Etapa sem declaração, que é o caso do
Edital publicado antes do incremento"*. É acervo, e passa a ser tratado como acervo onde precisa ser.

**A estratégia, por causa**:

| Causa | O que muda | Por que não o contrário |
|---|---|---|
| Perfil sem corte | os quatro marcos de fixture ganham `cutRule` que **não governa Etapa alguma**, com alvo do quadro ou fixo; o `seed_demo` idem | é a regra que não mexe em participação (`FR-214`, `faixa.etapa_governada` devolve `None`): nenhum conjunto de participantes muda. Os casos que **precisam** de marco sem corte — os da `FR-461` e o cenário `sem_regra_de_corte` da ocupação — ganham um segundo marco que corta, que é o Cenário D |
| Eliminatória sem nota mínima | `etapas()` passa a declarar `minima="0.0000"` por padrão | nota mínima zero não elimina ninguém e não torna parecer obrigatório (`012`, `FR-033`), de modo que nada do que a Mesa e a distribuição exercitam muda. O que muda é o que **devia** mudar: a consolidação da *Análise documental* deixa de recusar |
| Duas avaliações, eliminatória ou enumerada | um ajudante de fixture — `publicar_como_acervo` — publica sem a regra desta feature, e os casos que pedem `avaliacoes=2` passam a usá-lo | depois desta feature, Etapa de dupla leitura publicada só existe no acervo; é o que estes casos exercitam. Torná-la não eliminatória mudaria a progressão que parte deles afirma |
| Os quatro arquivos que afirmam a recusa da consolidação (`test_prontidao.py`, `test_ocorrencia.py`, `contract/test_consolidacao.py`, `acceptance/test_quickstart.py`) | passam a publicar pelo mesmo ajudante, e declaram `minima=None` onde a recusa é a de nota mínima | é exatamente o Edital do acervo que continua existindo e que a consolidação continua recusando |

**`publicar_como_acervo` é o `publicar_sem_aferir` sem rebaixar a versão canônica.** O ajudante que já
existe (`tests/fixtures/legado.py:137`) degrada o conteúdo para uma versão anterior, o que estes casos
não querem. O novo publica pelo caminho normal com as duas funções desta feature neutralizadas durante
a chamada, e diz no nome e no docstring o que simula.

**As três falhas do protótipo do `RC-32`, e o que cada uma prendia**:

| Caso | O que afirmava | Destino |
|---|---|---|
| `tests/integration/portal/test_cronograma_publico.py::test_o_periodo_em_curso_e_acontecendo_agora_dos_dois_lados` | a `FR-549a` da `037` (*concordância de desfecho*) lida na **tela do Edital publicado**, com contraprova de que a conferência do Cronograma aparecia lá | o lado da gestão passa a ser a conferência sobre o **mesmo conteúdo e o mesmo instante**, lida no domínio — e, com a `045` já mesclada, a fase derivada do pulso. A tela do Edital publicado não acusa Evento nenhum, e por isso não diverge do candidato: a `SC-191` continua valendo |
| `tests/interface/test_conducao_dos_bloqueios.py::test_edital_publicado_nao_manda_pedir_a_ninguem` | a `FR-544` da `037`, com a premissa *"há pendência corrigível na tela"* de um Edital publicado | a premissa deixa de existir; o caso passa a afirmar a forma mais forte: **nenhuma** pendência, e portanto nenhuma condução |
| `tests/unit/editais/test_etapas.py::test_a_pontuada_sem_nota_nenhuma_e_legitima` | Etapa pontuada sem nota é legítima (`FR-066`), sobre uma Etapa **eliminatória** | a legitimidade vale para a não eliminatória, que é o que a `FR-066` chama de limite não declarado; a eliminatória passa a ser o caso do `FR-746`. A `T021` da `045` já troca o filtro por severidade neste mesmo caso |

**O que o protótipo não mediu, e fica para a implementação recontar**: os casos que afirmam o aviso
`milestone_without_cut_rule` sobre um Perfil de marco único (`test_executabilidade.py`,
`test_hardening_pos_auditoria.py:785-787`, `:861`, `:1100`) — o protótipo não suprimia o aviso —, e a
cláusula da `T021` da `045` (`R-8`).

## R-8 — Coordenação com a 045

A `045` está planejada e não implementada, e toca dois arquivos desta: `editais/domain/validation.py`
(o aviso `stage_without_schedule_event`, `R-5` de lá) e `interface/views.py` (`processo_detalhe`,
`supervisao`).

**Um ponto se contradiz, e é registro, não decisão desta feature**: a tarefa `T021` da `045` prende o
aviso novo dela *"em 'Validação do conteúdo' de um Edital **publicado**"*. A `FR-755` desta feature
tira a seção do Edital publicado. A `045` descreveu o que a tela faz hoje (`R-5` de lá, *"`detalhe`
chama `_pendencias` para qualquer estado"*), e a própria `D-003` de lá — *"condição sem destino
operacional não pertence à Atenção"* — e a `DP-03` — *"aviso na Revisão antes de publicar; fora da
Atenção depois"* — apontam na mesma direção desta. Quem mesclar depois ajusta.

**Decidido pelo usuário em 26/09: a `045` entra antes.** A implementação desta feature parte da `main`
com a `045` já mesclada, e a `T021` de lá terá deixado na suíte um caso que afirma o aviso
`stage_without_schedule_event` em *"Validação do conteúdo"* de um Edital publicado. **E a leitura da `045` mesclada corrigiu esta seção**: a cláusula não era de teste, era a `FR-739`
de lá, que exige o aviso na página do Edital publicado, com o veto da convergência (§21) por trás. O
usuário decidiu em 26/09 — *"fatos ficam, gate sai"* (`D-003`, `R-5`) —, e o caso da `T021` da `045`
(`test_compor.py::test_o_edital_publicado_diz_a_etapa_sem_evento_na_validacao_do_conteudo`)
**continua valendo sem mudança**. A `046` acrescenta a ele a contraprova: na mesma página, nenhum
impeditivo e nenhum aviso de publicabilidade.

O resto não conflita: as funções novas são vizinhas, e nenhuma lê o que a outra muda.
