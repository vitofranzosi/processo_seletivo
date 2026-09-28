# Revisão da 046 — contrato de executabilidade (PR #188)

Revisão somente leitura, em 26/09/2026, sobre `HEAD = 717eb0c` (origin/main). Diff revisado:
`git diff 7f5db4a4 064228c7`. Nada foi executado além de `git`, `grep`, leitura e um `gh issue view`
(leitura); nenhum teste rodado — o CI da main está verde. Linhas citadas são do código atual
(`717eb0c`), com caminhos relativos a `backend/` salvo indicação.

## Vereditos

| RC | Veredito | Em uma linha |
|---|---|---|
| RC-29 | **FECHADO COM RESSALVA** | o gate existe, pergunta a `impedimento_da_regra` sem copiá-la, e o acervo continua retificável; mas recusa por engano a Etapa decisória não eliminatória enumerada como **porta**, que não trava nada |
| RC-30 / D-G1 | **FECHADO COM RESSALVA** | impeditivo por Perfil, só na publicação; a frase de correção recomenda o corte que "não governa Etapa", e esse corte, pelo que diz o RC-113, também não convoca ninguém |
| RC-32 | **FECHADO COM RESSALVA** | a tela do Edital e a Revisão não rodam mais o gate; mas o assistente de um Edital publicado ainda diz *"Nada pendente — o Edital pode ser submetido"*, *"O que falta para submeter"* com *"Ir para"*, e *"Corrigir as datas abaixo"* no Cronograma |
| RC-72 | **FECHADO** (ressalvas menores) | a fonte saiu do vocabulário de produção e há barreira no boot; `seed_demo` e a suíte continuam; reaproveitamento e Retificação são recusados |

---

## RC-29 — Etapa publicável que nunca consolida

**Veredito: FECHADO COM RESSALVA.**

**Evidência.**
- `editais/domain/validation.py:1491` chama `_etapa_sem_resultado`. A função
  (`validation.py:1832-1924`) importa `impedimento_da_regra` e `eliminatoria` de
  `resultados/domain/regra.py:53-97` e reusa a frase da regra sem reescrevê-la
  (`validation.py:1864-1867`, `:1888`). Os três predicados não foram copiados, como a FR-747 exige.
- "Exigido" (D-001) = eliminatória (`:1872-1877`) ou referenciada por marco
  (`_quem_exige_o_resultado`, `:1787-1830`: enumerada `:1804-1808`, governada `:1809-1814`,
  Etapa de habilitação `:1815-1826`).
- Impeditivo `stage_result_unreachable` **só** com `ato == ATO_DE_PUBLICACAO` (`:1879-1893`). Nos
  demais casos sai `stage_without_result` como WARNING (`:1894-1923`), inclusive em qualquer
  Retificação.
- **O acervo continua retificável.** `_assert_well_formed` (`publicacoes/application/retificacoes.py:531`)
  só recusa BLOCKING do ato de Retificação, e a família nova não produz BLOCKING nesse ato.
  `evaluationsPerRegistration`, `minimumScore` e `eliminatory` são retificáveis
  (`editais/domain/mutabilidade.py:450-453`).
- **A #117 não é acionada.** `advertencias_do_ato` subtrai por código os impeditivos do ato de
  publicação (`retificacoes.py:583-588`). `stage_without_result` nunca é BLOCKING em ato nenhum, então
  nunca entra no conjunto subtraído, e `stage_result_unreachable` nunca aparece na lista da
  Retificação. Isso está preso ponta a ponta em
  `tests/integration/publicacoes/test_advertencia_da_etapa_sem_resultado.py:36-56`.
- O `como-preencher` tem o texto e o cartão não ganhou nenhum (`interface/templates/interface/compor_etapas.html:42-45`;
  `tests/interface/test_etapa_sem_resultado.py:124-142`).

**D-008.** A DP-06 recomendava só **aviso** por causa da D-008. O usuário decidiu outra coisa (D-001
da 046, registrada em `doc/decisoes-pendentes-da-consolidacao.md`, "O que foi decidido"): impede
quando o Resultado é exigido. A decisória não eliminatória **fora** do fluxo continua publicável com
aviso (`tests/unit/editais/test_etapa_sem_resultado.py:145-154`), e isso respeita a D-008. **Um ramo
não respeita:** a decisória não eliminatória enumerada no marco é recusada, embora nada no fluxo dependa
do Resultado dela (Defeito D1). O próprio registro da DP-06 afirma *"nenhuma Etapa decisória precisa
ser eliminatória para publicar, desde que nada no fluxo dependa do Resultado dela"*, e o código contradiz
isso para a porta.

**Ressalvas.**
1. D1, a porta decisória recusada por engano.
2. Uma Retificação pode **introduzir** o defeito (1→2 avaliações num Edital pós-046) e recebe só
   advertência. É resíduo deliberado da spec (Edge Cases), mas significa que o "contrato" vale no ato de
   publicação e não depois.
3. O gate se satisfaz com nota mínima `0.0000` numa Etapa eliminatória, e essa Etapa não elimina
   ninguém. É o truque das fixtures (`tests/fixtures/comissao.py`, `etapas(minima="0.0000")`;
   `tests/fixtures/supervisao.py`) e o mesmo *"o Edital seguiria sem o critério que publicou"* que a
   frase nova denuncia (`validation.py:1873-1874`). Não chega a ser defeito de código, mas o gate é
   raso.
4. O RC-112 torna falso, em um cenário, o aviso *"Nada neste Edital depende dele"* (`:1903`): a Etapa
   não exigida que **precede** outra trava a seguinte assim que alguém registra uma Ocorrência nela.
   Ver a seção "RC-112 e RC-113".

---

## RC-30 / D-G1 — Perfil que não convoca

**Veredito: FECHADO COM RESSALVA.**

**Evidência.**
- `_perfil_sem_corte` (`validation.py:1938-1972`, chamada em `:1490`): BLOCKING
  `profile_without_cut_rule`, **só** no ato de publicação (`:1952`). Só entra Perfil com marco, porque
  `_nenhum_marco_corta` exige marco (`:1927-1935`) e assim não se empilha sobre `profile_without_milestone`.
- `_marco_sem_regra_de_corte` pula o Perfil sem corte (`:2006`, FR-753) e continua avisando o marco sem
  corte num Perfil que corta (Cenário D). Isso está preso em `tests/unit/editais/test_executabilidade.py`
  e em `tests/interface/test_perfil_sem_corte.py:77-114`.
- `D-G1 como impeditivo só no ato de publicação` está cumprida. O acervo sem corte continua
  retificável, e acrescentar `cutRule` por Retificação é permitido
  (`mutabilidade.py:522-526`, `PODE_PASSAR_A_EXISTIR`).
- A #117 não é tocada, e não precisava ser: o código novo existe só na publicação, e na Retificação
  nenhuma das duas funções emite achado (`:1952`, `:1999`). **A #117 continua ABERTA**
  (`gh issue view 117` → `OPEN`), como a D-005 diz.
- `seed_demo` ganhou corte para o Perfil de sorteio
  (`processos/management/commands/seed_demo.py:561-572`), e `tests/integration/test_seed_demo.py`
  roda o comando.

**Ressalvas.**
1. **Na Retificação não há aviso nenhum.** Se a leitura da D-G1 era "impeditivo na publicação, aviso
   na Retificação do acervo", o aviso não existe: nem antes da 046 (a 032 já silenciava) nem depois.
   A FR-754 escolheu o silêncio. É coerente com a 032 (FR-460), mas não é "manter aviso".
2. **A correção sugerida leva a um Perfil que também não convoca** — Defeito D2, condicionado ao
   RC-113. A frase manda *"Declare a regra em ao menos um marco… ela pode declarar que não governa
   Etapa alguma"* (`validation.py:1965-1967`, e igual em `:2018-2019`). É também a forma que o
   `seed_demo` e todas as fixtures (`tests/fixtures/edital.py:44-60`, `corte_que_nao_governa`) passaram a
   usar para se tornarem publicáveis.

---

## RC-32 — Edital publicado julgado como se fosse publicar

**Veredito: FECHADO COM RESSALVA.**

**Evidência.**
- `interface/views.py:821-823` define `ANTES_DA_PUBLICACAO` com EM_ELABORACAO, EM_REVISAO e
  HOMOLOGADO — a partição dos seis estados de `processos/models.py:36-42` está correta. Em `:862-866`,
  fora desses estados, `_pendencias` **não executa** `validate_for_publication`: chama
  `fatos_do_conteudo_publicado` (`editais/domain/validation.py:1297-1305`), que deriva só
  `stage_without_schedule_event`.
- Os três chamadores de `_pendencias` (`views.py:1291`, `:2811`, `:2989`) herdam a regra. A previsão de
  recusa (`interface/acoes.py:184-200`) não recebe mais impeditivo de Edital publicado.
- O estado está preso: `validate_for_publication` com `side_effect=AssertionError` em
  `tests/interface/test_edital_publicado_sem_pendencias.py:154-173`. Quem chama está preso numa
  varredura por arquivo (`tests/test_quem_consulta_a_publicabilidade.py`).
- Nada do acervo fica ilegível: só sai texto. De quebra, a 046 corrigiu um 404 latente na tela do marco
  removido que cortava (`views.py:5933-5939`, `_corte_do_marco` resolvendo o Perfil sem `Http404`).

**Ressalvas** (Defeito D3):
1. **A Revisão de um Edital publicado continua dizendo publicabilidade.** `compor_revisao.html:5`
   intitula a seção *"O que falta para submeter"*. `:9`, sem fatos, diz *"Nada pendente — o Edital pode
   ser submetido."* Com a Etapa sem Evento, o fato aparece como pendência com *"Ir para Etapas…"*
   (`_pendencia.html:7-10`, `corrigivel` vindo de `_destino`), num vínculo que é estrutural e não se
   retifica. A 046 torna o *"pode ser submetido"* **mais frequente**: antes, o Edital publicado típico
   mostrava o *Impede* falso; agora mostra este.
2. **O Cronograma do Edital publicado ainda manda corrigir datas.** `views.py:1296` calcula `vencidos`
   em qualquer estado, e `compor_cronograma.html:17-22` exibe, com `class="aviso"`, *"Esta etapa fica
   pendente… Corrigir as datas abaixo é o que a conclui"*. O predicado é o da conferência de publicação
   (`views.py:1063-1066`).
3. **O teste só prende três cadeias** (`test_edital_publicado_sem_pendencias.py:106-109`): "O período de
   inscrições encerrou", "O Edital será publicado" e `class="p-erro"`. As duas frases acima passam. E
   `tests/interface/test_conducao_dos_bloqueios.py` passou a **exigir** *"Ir para"* na Revisão do Edital
   publicado.
4. O percurso da T040 (`specs/046-…/antes-do-gate.md`, "Os percursos") registrou só a tela do Edital.
   O passo 3 do percurso 3 do quickstart, que manda abrir cada etapa do assistente, não foi registrado.

---

## RC-72 — Fonte de demonstração em produção

**Veredito: FECHADO.**

**Evidência.**
- `sorteios/infrastructure/fontes/__init__.py:83-117`: `FONTES` guarda só a Loteria Federal. A
  demonstração entra por `fontes_publicadas()` só quando `settings.SORTEIO_FONTE_DE_DEMONSTRACAO` é
  verdadeira, e a leitura é feita a cada chamada. `fonte_declarada` (`:120-137`) usa essa função.
- Os três leitores passaram a usá-la: `interface/forms.py:319-323` (o seletor),
  `editais/domain/perfis.py:534-545` (a gravação, e `draw_method_invalid` em `validate_for_publication`
  nos dois atos) e `fonte_declarada` (a observação). Não resta nenhum outro leitor de `FONTES` nem o nome
  literal no código de produção, fora o `seed_demo`.
- A configuração: `config/settings/base.py:164-166` deixa falso por padrão; `development.py:7` e
  `test.py:11` fixam verdadeiro; `production.py:112-117` recusa o boot. Isso está preso em
  `tests/test_configuracao_producao.py` e em `tests/integration/sorteios/test_fonte_fora_de_producao.py`
  (seletor, execução, os dois atos, gravação por API e reaproveitamento).

**Contornos examinados.**
- **Reaproveitamento** que copia a fonte: recusado na gravação (`test_fonte_fora_de_producao.py:133-154`).
- **Retificação**: recusada, porque `draw_method_invalid` é BLOCKING no ato de Retificação
  (`:84-93`). A fonte é retificável (`mutabilidade.py:216`, `:372`), então há saída: trocar a fonte no
  mesmo ato.
- **Edital já publicado com a fonte**, em produção:
  - a observação recusa (`draw_source_not_supported`);
  - **exceto** se a ocorrência já estava registrada antes da implantação, porque
    `sorteios/application/ocorrencia.py:61-66` devolve a linha existente antes de consultar o
    vocabulário, e a execução não volta a consultá-lo — `fonte_declarada` só é chamada em
    `ocorrencia.py:68`;
  - toda Retificação desse Edital, mesmo a que só corrige uma data, é recusada até trocar a fonte. É o
    oposto do princípio que a 035 escreveu para a forma da ocorrência (`perfis.py:419-425`: *"um Edital
    do qual não se sai é pior do que um método que não roda"*), mas aqui há saída e a escolha é
    deliberada (spec, Edge Cases). A consulta SQL de `data-model.md` precisa rodar na base de produção
    antes da implantação.
- **`seed_demo` e quickstart**: não quebram. O módulo de desenvolvimento liga a fonte, o `seed_demo` usa
  `fonte_externa=FonteDeTeste()` (`seed_demo.py:1207`), e `tests/integration/test_seed_demo.py` roda o
  comando.
- **Barreira**: só em `production.py`. `config/wsgi.py:5` e `asgi.py:5` caem em
  `config.settings.development` quando falta `DJANGO_SETTINGS_MODULE`. Uma implantação que esqueça a
  variável liga a fonte **e** o `DEBUG`. A barreira de identidade tem a mesma forma, mas o módulo de
  desenvolvimento não força a identidade e força a fonte. Risco baixo.

---

## Defeitos encontrados

### D1 — A porta decisória não eliminatória enumerada é recusada, embora nada dependa dela · **média** · confiança **alta** (lido, não percorrido)

- **Cenário.** Um marco POR_PONTUACAO enumera a "Prova" (pontuada) e a "Entrevista" (decisória, não
  eliminatória, uma avaliação). A consolidação recusa a Entrevista (`regra.py:77-87`). Mesmo assim, a
  combinação **pula a porta** (`classificacao/domain/combinacao.py:119-122`, `e_porta`). O universo só
  exclui quem tem ELIMINADA (`classificacao/application/calculo.py:149-160`), e todos são posicionados
  pela Prova (`:164-178`). A progressão para a Etapa seguinte fica dormente sem Resultado
  (`resultados/application/prontidao.py:150-154`). Nada trava.
- **O que o gate faz.** `validation.py:1804-1808` marca toda Etapa enumerada como exigida, e
  `:1879-1893` emite `stage_result_unreachable` com a frase *"o marco X a enumera, e ninguém é
  posicionado por ele"* — falsa para a porta.
- **Por quê.** A premissa da D-001 (spec, "O que a verificação contra o código mudou", item 1) diz que
  *"a combinação devolve SEM_PONTUACAO"*. Isso vale para a parcela pontuada e não vale para a porta. O
  erro está na spec (US1 cenário 3, quickstart 1.6) e foi preso por teste
  (`tests/interface/test_etapa_sem_resultado.py:106-121`).
- **Consequência.** Proíbe na elaboração o que executaria (D-008) e contradiz o "O que foi decidido" da
  DP-06. O mesmo vale para a decisória não eliminatória com duas avaliações enumerada. Impacto prático
  baixo, porque a correção ("retire-a do marco") está ao alcance; mas a frase está errada.

### D2 — A recusa do Perfil sem corte ensina a forma que, pelo RC-113, também não convoca · **média** · confiança **média-alta** (lido; o RC-113 não foi percorrido)

- `profile_without_cut_rule` justifica a recusa com *"a convocação não alcança ninguém deste Perfil"* e
  sugere *"ela pode declarar que não governa Etapa alguma"* (`validation.py:1963-1968`). Com `NONE`:
  - `convocacao/application/selectors.py:122-123` lê `corte.etapa_governada_id = None`;
  - `ocupacao/application/selectors.py:381-388` devolve `set()`;
  - `ocupacao/domain/apuracao.py:79-97` filtra os chamáveis por esse conjunto — ninguém é chamável;
  - `ocupacao/application/emissao.py:106-107` faz a mesma leitura na apuração.
- A fixture antiga já dizia isso por escrito: *"Sem Etapa governada não há Resultado a ler, logo ninguém
  consta ocupando"* (`tests/fixtures/ocupacao_sorteada.py:39-41`).
- **Cenário.** Quem compõe o 69/2026, recusado, segue a frase, publica, e o Perfil não convoca — a
  mesma consequência que a recusa afirma impedir. O `seed_demo` (`seed_demo.py:565-571`) e todas as
  fixtures (`corte_que_nao_governa`) adotaram exatamente essa forma; a demonstração só convoca pelo outro
  Perfil, que governa a Análise documental (`seed_demo.py:140-147`).
- A spec reconhece em A-2 que FR-752 *"deixa de ser suficiente"*, mas a frase **recomenda** a forma
  insuficiente. Se o RC-113 se confirmar, a frase e o docstring de `_marco_sem_regra_de_corte`
  (`validation.py:1978-1983`, *"o 69/2026… sorteia, publica, convoca"*) estão errados.

### D3 — O assistente do Edital publicado ainda diz publicabilidade · **baixa-média** · confiança **alta**

Ver as ressalvas do RC-32: `compor_revisao.html:5` e `:9`; `_pendencia.html:7-10`, com o *"Ir para"*
num fato não retificável; `views.py:1296` com `compor_cronograma.html:17-22`. A FR-755 e a SC-278
(*"as nove etapas do assistente exibem zero… avisos de publicabilidade"*) não se cumprem à letra. Não
bloqueia operação; é informação falsa em ato imutável, a mesma espécie do RC-32.

### D4 — As frases erram o consumidor e o lugar da correção em dois casos · **baixa** · confiança **alta**

- **Consumidor.** Etapa enumerada por marco de **sorteio**, inclusive a Etapa de habilitação, que
  precisa estar enumerada (`perfis.py:514-523`). O `setdefault` grava primeiro *"ninguém é posicionado
  por ele"* (`validation.py:1804-1808`), e a ordem do sorteio não vem de Etapas
  (`classificacao/domain/faixa.py:93-97`). O consumidor real é a relação do sorteio (`:1822-1826`), que
  nunca aparece nesse caso. O contrato manda nomear o primeiro da tabela, e é o que o código faz; o
  resultado é uma frase falsa.
- **Lugar da correção.** Para a Etapa só **governada** pelo corte, o *"onde"* diz *"retire-a do
  marco"* (`:1881-1882`), mas a correção é trocar a Etapa governada.

### D5 — A tabela-verdade da SC-275 confere a D-001 contra ela mesma · **baixa** (qualidade de teste) · confiança **alta**

- Em `tests/unit/editais/test_etapa_sem_resultado.py:133`, `exigida = situacao != "nenhuma" or
  eliminatory` é uma cópia da regra da D-001, e não uma leitura dos consumidores. O teste passa com o D1.
- Os casos `habilitacao_propria` (`:83-90`, habilitação fora das Etapas enumeradas) e `habilitacao_comum`
  (`:91-95`, `qualifyingStageId` no método comum) são conteúdos que a validação recusa: `perfis.py:514-523`
  e `validate_common_draw_method`, que usa `etapas=()` (`perfis.py:358-374`). O teste filtra só os
  códigos da 046 (`:110`) e não percebe. O "zero divergências" da rastreabilidade é contra a D-001, e não
  contra a consolidação.

### D6 — Conteúdo malformado pode virar 500 onde a regra deveria recusar com 422 · **baixa** · confiança **média**

`_quem_exige_o_resultado` faz `(metodo or {}).get("qualifyingStageId")` (`validation.py:1815-1822`) e
`faixa.etapa_governada(marco.get("cutRule"))` (`:1809`) sem conferir que são objetos. A função só roda
quando alguma Etapa não consolida. Rascunho é validado na gravação, então a exposição fica no conteúdo
produzido por Retificação: `_assert_well_formed` levantaria `AttributeError` (500) em vez do 422. Para
`cutRule`, a fragilidade já existia em `_regra_de_corte_do_marco` (`:818-822`).

---

## O que a spec prometeu e não entregou

- **SC-278 / FR-755**: *"nove etapas do assistente… zero avisos de publicabilidade"*. Não à letra (D3).
  Para ENCERRADO e CANCELADO só a tela do Edital é testada
  (`test_edital_publicado_sem_pendencias.py:138-151`).
- **T040**: o percurso 3 não registrou as etapas do assistente.
- **D-001 e DP-06**: *"nenhuma Etapa decisória precisa ser eliminatória para publicar, desde que nada no
  fluxo dependa do Resultado dela"*. Violado para a porta enumerada (D1).
- **SC-275**: *"zero divergências"* entre publicação e consolidação. Medido contra a D-001, com duas
  situações impossíveis (D5).
- **SC-279 / US4 cenário 2**: a recusa *"nos quatro atos"* foi provada na gravação (API) e no
  reaproveitamento (comando). Na submissão, na publicação e na Retificação foi provada só em
  `validate_for_publication` (`test_fonte_fora_de_producao.py:84-93`), sem passar por
  `submit_edital`/`publish_edital`/`publish_retification`. É equivalente pelo código, mas não é o que a
  frase diz.
- **Contrato §1**: *"retire-a do marco `<código>`"*. O código do marco sai só na consequência, não no
  *"onde"* (`validation.py:1882`). Trivial.
- **FR-756**: a varredura é por **arquivo**; `interface/views.py` inteiro está liberado
  (`tests/test_quem_consulta_a_publicabilidade.py:31-34`). Uma view nova em `views.py` que valide um
  Edital publicado passa. A guarda de estado cobre só `detalhe` e `compor_etapa`.
- **D-G1 "aviso na Retificação"**, se era essa a leitura: não existe aviso (ver RC-30).

Entregue como prometido: FR-746, FR-747 (a regra consultada, não copiada), FR-748, FR-750, FR-751,
FR-752, FR-753, FR-754, FR-757, FR-758, FR-759 e SC-281 — nenhuma migration no diff.

---

## RC-112 e RC-113

**RC-112** — *a Ocorrência abre o portão de uma Etapa que nunca consolida* (A-1 da spec).
- A Ocorrência de ausência é aceita em Etapa impedida de consolidar, por desenho
  (`resultados/application/ocorrencia.py:14-20`), e produz ELIMINADA.
- Um único Resultado vigente basta para `ha_resultado_em` (`resultados/application/selectors.py:20-28`)
  ligar a exigência de habilitação na Etapa **imediatamente seguinte**
  (`resultados/application/prontidao.py:150-154`). Como ninguém terá HABILITADA na anterior, todos os
  outros ficam `aguardando-anterior` para sempre.
- **Confere pelo código.** Vale para o acervo e também para a Etapa **não exigida** que a própria 046
  publica com aviso, quando ela precede outra. É o caso em que a frase *"Nada neste Edital depende dele"*
  fica falsa.
- **Classificação A `[VALIDAR]`: faz sentido.** A condição é operacional (alguém precisa registrar uma
  ausência). A precondição, porém — Etapa inconsolidável que precede outra —, é estrutural e se conhece
  na publicação. A 046 escolheu não contar a precedência como consumidor, e isso deveria constar do RC.

**RC-113** — *corte que não governa Etapa pode não convocar ninguém* (A-2 da spec).
- **Confere pelo código.** A cadeia está em D2: `convocacao/application/selectors.py:122-123`,
  `ocupacao/application/selectors.py:381-388`, `ocupacao/domain/apuracao.py:79-97`, mais o comentário da
  fixture `ocupacao_sorteada.py:39-41` que já dizia o mesmo. Não achei teste de convocação com
  `governedStage: "NONE"`.
- **Classificação A `[VALIDAR]`: a letra está certa, a prioridade está baixa.** Depois da 046, essa é a
  forma que a mensagem de recusa recomenda e que `seed_demo` e as fixtures adotaram. Deixou de ser borda
  e virou o caminho de menor resistência. Deveria ser validada por percurso antes do próximo Edital de
  sorteio (o 69/2026) — e antes de qualquer conclusão de que o RC-30 garante convocação.

---

## Resíduos abertos

- **#117 continua OPEN** (`gh issue view 117`). A auditoria diz *"não foi necessária"*, e é verdade para
  a 046; mas nenhum RC acompanha a issue, e ela volta no primeiro código com duas severidades.
- **RC-112 e RC-113**: validar por percurso. O RC-113 condiciona a eficácia do RC-30.
- **D1**: decidir se a porta decisória conta como "exigida". Pelo código, não conta.
- **D3**: tirar o juízo de publicabilidade também da Revisão e do Cronograma do Edital publicado.
- Uma Retificação pode introduzir Etapa inconsolidável exigida, com só advertência (deliberado).
- Nota mínima `0` em Etapa eliminatória satisfaz o gate e não elimina ninguém.
- **Produção, antes de implantar**: rodar a consulta de `specs/046-…/data-model.md`. A ocorrência de
  demonstração já registrada escapa à barreira (`ocorrencia.py:61-66`).
- `wsgi.py`/`asgi.py` caem em `config.settings.development` sem a variável, o que liga a fonte.
- Registrado pela própria 046, fora do escopo: o selo *CONCLUÍDA* da etapa Etapas convivendo com um
  *IMPEDE* dela (`antes-do-gate.md`).
- A regra de combinação de avaliações continua esperando Edital real (DP-06 C).
