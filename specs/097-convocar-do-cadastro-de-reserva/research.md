# Research: Convocar do cadastro de reserva, na ordem publicada

**Feature**: [spec.md](spec.md) · **Plan**: [plan.md](plan.md)

As questões técnicas levam `T-NNN`; as decisões de produto são as `D-` da spec, e não se repetem aqui.
Os fatos foram conferidos contra a `main` em `717fc057`.

---

## T-001 — A vaga acrescida é tabela nova, e não espécie nova de `MovimentoDeVaga`

**Decision**: uma tabela append-only nova no app `ocupacao`, `AcrescimoDeVagas`, com duas espécies —
`ACRESCIMO` e `DESFAZIMENTO` — e quantidade sempre positiva. O desfazimento cita o acréscimo que
desfaz por chave estrangeira para a mesma tabela.

**Rationale**: `MovimentoDeVaga` parece o lugar e não é. Ele nasce **com** a apuração de origem
(`apuracao` não nula, `ocupacao/models.py:157`), move quantidade **entre** recortes
(`ck_movimento_recortes_distintos`) e tem a reversão como espécie única por decisão registrada
(`ocupacao/domain/nomes.py`, *"Uma só, e a ausência da segunda é o achado"*). O acréscimo não tem
apuração de origem — ele **precede** a apuração que o lê, e pode nem produzi-la (`FR-2454`, com outra
causa de obsolescência presente) —, não tem recorte de origem, e carrega origem e fundamento em texto,
que o movimento não tem. Afrouxar as três constraints para caber nele apagaria o que elas protegem.

Uma tabela, e não duas, porque acréscimo e desfazimento são lidos juntos pela mesma conta, congelados
na mesma lista e mostrados na mesma linha do tempo do recorte. Duas tabelas exigiriam duas listas
congeladas e uma junção para ordenar a história; a espécie resolve com uma coluna e duas `CHECK`.

**Alternatives considered**: espécie nova de `MovimentoDeVaga` (recusada acima); quantidade com sinal
numa espécie só (recusada: um `-1` digitado por engano seria um desfazimento sem motivo nem citação, e
a `FR-2460` exige as duas).

## T-002 — A apuração lê os acréscimos pelo recorte exato, e os congela pelo id

**Decision**: `_apurar` (`ocupacao/application/emissao.py:116`) lê os acréscimos e desfazimentos com o
mesmo `(edital, perfil, marco, lista)` da apuração, grava os ids em `universo["acrescimosLidos"]` e
entrega a `calculo.apurar` o saldo líquido como parâmetro novo, `acrescidas`, somado às efetivas ao
lado de `recebidas - cedidas`. A reprodução de apuração antiga relê os ids congelados, como
`movimentos_lidos_por` já faz (`ocupacao/application/selectors.py:46`).

**Rationale**: é o desenho que a `016` já usa para movimentos e a `019` para efeitos (`FR-244`), e a
`SC-922` só é verificável se a conta for reproduzível pelo congelado. O recorte é o exato, e não "a
linha geral do Perfil": o Perfil pode ter a ampla em duas grafias — o recorte `NULL`, que o sorteio
usa, e a Modalidade declarada como ampla em `generalCompetitionModalityId`, que `linha_do_quadro` lê
pela mesma linha (`classificacao/application/corte.py:53`). Gravar o acréscimo "na linha" o faria
valer nos dois recortes, e somar em dobro. Ele vale no recorte em que foi registrado.

`ocupantes_pela_ampla` (`ocupacao/domain/apuracao.py`) **não** recebe o acréscimo, e não precisa: ela
só é chamada para recortes de Modalidade reservada, e a `FR-2464` recusa o acréscimo em Perfil que
tenha qualquer linha além da geral (`T-006`).

## T-003 — A obsolescência ganha a sexta causa, `acrescimo_posterior`

**Decision**: `causas_de_obsolescencia` (`ocupacao/application/selectors.py:67`) acusa
`acrescimo_posterior` quando existe, no recorte, acréscimo ou desfazimento cujo id não está em
`universo["acrescimosLidos"]` da apuração vigente.

**Rationale**: é o desenho da quarta e da quinta causas — obsolescência em vez de orquestração. A
comparação por id, e não por instante, é a que não erra na mesma transação: o ato do acréscimo grava o
registro e emite a apuração no mesmo `now`.

## T-004 — O ato do acréscimo emite a apuração seguinte pela mesma conta, num *savepoint*

**Decision**: o comando `acrescentar_vagas` (em `ocupacao/application/acrescimo.py`, novo) roda dentro
de `comando_de_comissao`, grava o registro e, se as causas de obsolescência da apuração vigente forem
só `acrescimo_posterior` — ou se o recorte ainda não tiver apuração —, chama `_apurar` com
`movimento_admitido=False` num *savepoint*. A recusa da emissão (empate na fronteira, por exemplo) não
desfaz o acréscimo: ele fica gravado, a apuração fica obsoleta, e o declarado do ato diz qual ato falta.

**Rationale**: é o padrão que o desfecho da `050` já fixou (`convocacao/application/desfechar.py:185`,
*"três condições, e cada uma protege uma coisa"*), e a `FR-2454` o pede pelo nome. No recorte da linha
geral a reversão nunca cede vaga (`cede` é zero quando `lista is None`, `emissao.py`), de modo que
`movimento_admitido=False` é guarda, e não ramo vivo.

O recorte **sem apuração** também recebe a primeira pelo ato: o caso do TMD é exatamente esse — o
Edital publicou 0 vagas, a ordem foi divulgada, e ninguém emitiu apuração porque não havia o que apurar.

## T-005 — A trava do desfazimento conta pessoas chamadas, e a convocação a responde

**Decision**: o desfazimento é recusado quando as vagas efetivas resultantes ficariam **abaixo do número
de pessoas do recorte com convocação em aberto ou atendida**. A pergunta é feita por uma função que o
comando recebe como argumento, `pessoas_chamadas(edital, perfil_id, marco_id, lista_id, at)`, avaliada
**dentro** da transação, depois do lock do Processo. A interface passa a função da convocação; o teste
de unidade passa um dublê.

**Rationale**: a redação da spec — *"menos vagas efetivas do que ocupantes somados às chamadas em
aberto"* — recusaria **todo** desfazimento depois da primeira apuração. Pela contagem da `016`, o
titular ocupa vaga desde a emissão, antes de ser chamado (`convocar.py`, `_recusar_por_deficit`): com 1
vaga acrescida e o 1º do sorteio habilitado, `ocupadas` é 1 no mesmo instante, e desfazer daria 0
efetivas contra 1 ocupada. O que o desfazimento não pode fazer é tirar a vaga de **quem já foi
chamado** para ela. Quem só está na janela de titulares sai dela, e nada se perde: ninguém lhe disse
nada. A `FR-2462` é corrigida na spec nesta medida (ver *Correções da spec*, abaixo).

A pergunta é da convocação, e a ocupação não a importa. A seta entre as duas corre da `019` para a
`016` — `convocacao` lê `ocupacao`, e não o contrário —, e a `UX-034` proíbe a `016` de conhecer o fato
da convocação. Receber a função como argumento mantém a seta e mantém a trava no backend, dentro do
lock: calculada antes, na view, ela seria um número velho no instante do ato (Princípio IV,
concorrência).

**Alternatives considered**: o comando de desfazimento morar em `convocacao` (recusado: o registro é de
vaga, e a tela é a da ocupação); a ocupação importar o seletor da convocação por import tardio (recusado:
inverte a seta que `tests/test_dependencia_da_ocupacao.py` protege em espírito, e a `UX-034` em letra).

## T-006 — "Só a linha geral" é "o quadro tem só a linha geral"

**Decision**: a `FR-2464` recusa o acréscimo quando o `vacancyTable` do Perfil, no conteúdo vigente,
tem qualquer linha de `modalityId` não nulo, ou quando o Perfil declara reversão de vaga. E recusa
quando o recorte do ato não lê a linha geral por `linha_do_quadro`.

**Rationale**: a redação da spec — *"linha de Modalidade reservada com vaga"* — deixava passar a linha
reservada com zero, e a concorrência concomitante da `FR-252` faria a vaga acrescida na ampla mudar quem
ocupa a reservada, por `ocupantes_da_ampla`, sem que o acréscimo a considerasse. Recusar o Perfil que
tem qualquer linha de Modalidade é a fronteira que a `D-003` quer, sem caso-limite dentro dela. O TMD
tem só a linha geral.

## T-007 — A autoridade é a de quem apura, e não capacidade nova

**Decision**: os dois atos rodam em `comando_de_comissao` (`comissoes/application/__init__.py`), como a
emissão da apuração: transação, `select_for_update` do Processo, `pode_gerir_comissao` (gestor com
`comissao:gerir`, ou a presidência do Processo) e reserva da chave de idempotência. As operações de
idempotência são `ocupacao:acrescentar_vagas` e `ocupacao:desfazer_acrescimo`; os códigos de auditoria,
`OCUPACAO_ACRESCENTAR_VAGAS` e `OCUPACAO_DESFAZER_ACRESCIMO`, com rótulo em `OPERACOES`
(`interface/views.py:4798`). Na view, a porta é `_edital_para_classificar(..., somente_gestao=True)`.

**Rationale**: `OCUPACAO_APURAR` não é capacidade — é código de operação de auditoria — e nenhum papel
o concede. A ocupação e a convocação são autorizadas pela comissão, e `emissao.py` registra no topo que
*"uma capacidade nova aqui inventaria autoridade que nenhum Edital distingue"*. A `D-004` da spec foi
revista nesta medida: a primeira redação pedia permissão própria, e uma capacidade em `PAPEIS`
(`interface/identidade.py:25`) seria concedida por papel, tirando o ato da presidência, que hoje apura e
convoca o próprio certame.

## T-008 — A Revisão: o texto do aviso, e o alcance da faixa

**Decision**: `_reserva_convocada_fora` (`editais/domain/validation.py:3312`) muda de mensagem — e o
código continua `reserve_only_convocation_external`, porque as Revisões já registradas o citam e a
`096` o lê. O alcance (`FR-2474`) é dito quando a regra de corte de algum marco do Perfil tiver alvo
`FIXED` e continuação `NONE`: *"a convocação poderá alcançar até N classificados"*, com N o alvo mais o
excedente. A `FR-2475` é achado novo, `reserve_only_with_reserved_lines`, advertência e só no ato de
publicação.

**Rationale**: o código é o identificador do achado em teste, em `test_advertencias_do_quadro.py` e na
`096` (que lê `reserve_only_convocation_external` em três arquivos, medido na worktree dela em 21/10).
Renomeá-lo quebraria a `096` sem ganho: o que estava errado era a frase.

## T-009 — Vocabulário e guardiões que a tela nova encontra

**Decision**: a tela do acréscimo é da ocupação, e obedece à varredura dela.

- `tests/test_vocabulario_da_ocupacao.py` — a lista `DA_016` é literal: o template novo e
  `ocupacao/application/acrescimo.py` **entram nela**, e com eles a proibição de `convoca`, `convocad`,
  `aceite`, `matrícul`, `desistênci` e `chamada de suplente` no texto visível, e de palavra sem acento.
  A recusa do desfazimento diz *"pessoas já chamadas para estas vagas"* — "chamada" sozinha é
  permitida, e é o que a pessoa vê na convocação. O texto digitado por quem registra (a origem, o
  fundamento) é dado, e a varredura não o alcança.
- `tests/test_vocabulario_da_composicao.py` — `TELAS` é literal e tem `ocupacao.html`; o template novo
  entra, e o primeiro uso visível de "recorte" vai em `<dfn>`.
- `tests/interface/test_telas_de_resultado_e_atos.py` — `BOTOES["ocupacao.html"]` é conferido em ordem e
  em quantidade; o botão novo *"Conferir o acréscimo"* entra nele, e a soma de pesos das `TELAS` sobe
  um `botao`. O acréscimo se desfaz por ato, e por isso não é `botao perigoso`.
- `tests/interface/test_acessibilidade.py`, `test_politica_de_conteudo.py`, `test_larguras.py`,
  `test_estaticos.py` — por `glob`: classe com regra na folha, nada inline, `input type="number"`
  coberto pela regra de campo, nenhum comentário de template em várias linhas.
- `tests/test_gramatica_das_portas.py` — a view nova não levanta `Http404` diretamente; usa
  `_identidade_ou_404`, `_recorte_pedido` e `_perfil_do_marco`, que já estão no inventário da `033`.
- `tests/test_dependencia_da_convocacao.py` — `ocupacao/**` não importa `convocacao`, e as migrations de
  `ocupacao` não citam o app: a `T-005` existe por causa dele.
- `tests/unit/editais/test_invariantes_da_declaracao_unica.py` — `ocupacao.html` continua contendo
  *"Retificação do Perfil"*.

## T-010 — A tela: formulário na ocupação, conferência em página própria

**Decision**: o padrão de dois passos da emissão da ordem (`emitir_ordenacao`, `views.py:7092`;
`ordenacao_confirmar.html`). No bloco do recorte da linha geral, na ocupação, um formulário com
quantidade, origem, fundamento e referência envia `POST` a `acrescentar-vagas` **sem** `confirmar`; a
view devolve `ocupacao_acrescimo.html`, com a prévia (`FR-2456`) e os mesmos campos ocultos, mais a
assinatura da leitura. Com `confirmar=1`, o ato é praticado, e o resultado volta à ocupação por
POST-redirect-GET, com a mensagem na sessão como a emissão já faz (`resultado_da_ocupacao`,
`erro_da_ocupacao`). O desfazimento tem o mesmo par, a partir da linha de cada acréscimo.

**Rationale**: a prévia depende da quantidade digitada, e por isso não pode ser calculada no `GET` da
ocupação, como a dos titulares da `050` é. A conferência em página própria é o que a ordem já faz para
um ato com prévia, e mantém a ocupação, que já tem um bloco por recorte, sem um segundo estado.

**A assinatura** é `canonical_sha256` do id da apuração vigente, dos ids dos acréscimos do recorte e
da quantidade — o molde de `convocacao/domain/alcance.py:100`. O ato recalcula sob a trava do
`comando_de_comissao` e recusa com `leitura_do_recorte_mudou` (409) quando difere (`FR-2457`).

## T-011 — O alcance que a Revisão diz

**Decision**: na `FR-2474`, com `continuation` `NONE`, N é `targetCount + surplusCount` quando o alvo é
`FIXED`, e só `surplusCount` quando o alvo é `FROM_VACANCY_TABLE` — o quadro do Perfil só de reserva é
zero. Com continuação admitida a Revisão não diz número: o alcance cresce por ato da `014`.

**Rationale**: é a faixa que `fila.alcancados` (`convocacao/domain/fila.py`) usa como teto — quem está
fora dela *"não é suplente, é quem a 014 não selecionou"*. O alvo do quadro é o caso que mais engana:
lido do quadro publicado, ele é zero, e o acréscimo não o muda — o corte já emitido não se recalcula
porque a apuração passou a ter mais vagas. Dizer *"a convocação poderá alcançar até 0 classificados"*
antes de publicar é a frase que evita descobrir isso na primeira vaga.

## T-012 — O cenário dos testes

**Decision**: `montar_cenario_da_convocacao` com `geral=0` e um parâmetro novo de
`rascunho_com_quadro`, `reserva="UNLIMITED"`, que declara o cadastro de reserva no Perfil. O corte
desse cenário é o do 14/2026 — alvo 2, governa a Entrevista, sem continuação —, de modo que a faixa
tem 2 pessoas e o caso *"mais vagas do que pessoas"* aparece com 3 acréscimos.

**Rationale**: o mecanismo não depende de como a ordem foi produzida — sorteio ou pontuação —, e o
cenário da convocação já tem Resultados, apuração e forma de comunicação. O sorteio entra na
demonstração (`quickstart.md`), e não em cada teste.

---

## Correções da spec

Encontradas ao planejar, e aplicadas na spec no mesmo commit:

- **`FR-2462`**: a trava do desfazimento passa a ser *"pessoas do recorte com convocação em aberto ou
  atendida"* (`T-005`).
- **`FR-2464`**: *"qualquer linha de Modalidade no quadro"*, e não *"linha reservada com vaga"*
  (`T-006`).
