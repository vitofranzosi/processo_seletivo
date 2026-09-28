# Revisão da 045 — condução confiável do Processo vivo (PR #187)

Revisão **somente leitura**. HEAD `717eb0c` (origin/main, 26/09/2026). Diff revisado:
`git diff 65c08133 ee894ab5` (o primeiro pai do merge é `65c08133`, então o diff é exatamente o do
PR). A `046` (#188) mexeu depois em `views.py` e `validation.py`; **as linhas citadas são do HEAD**, e
o que a 046 mudou e importa para cá está dito onde aparece. Nenhum teste foi executado: tudo abaixo
é leitura de código, de teste e de spec.

## Veredito em uma linha por RC

| RC | Veredito | Em uma frase |
|---|---|---|
| RC-78 / N-01 | **FECHADO** | a frase sai só do alcance do leitor, a mesma função serve Processo e Supervisão |
| RC-79 / N-02 | **FECHADO COM RESSALVA** | as duas fases entram no `UX-064`/`UX-005` e o contador conta pendentes; mas num Edital encerrado/cancelado a metade `UX-064` da partição continua suprimida, e a peça decidível fica invisível na Atenção |
| RC-80 / N-05+N-06 | **FECHADO** (ressalvas menores) | fase derivada na leitura, `UX-002` retirado, `UX-001` virou aviso só no ato de publicação; sobra rascunho legado publicável com fase declarada e período cancelado lido como aberto no pulso |
| RC-81 / N-04 | **FECHADO COM RESSALVA** | o `UX-046` ganhou a condução e as três telas de destino também; a prévia bloqueada por reingresso pendente continua mandando o Publicador "consolidar" sem dizer a quem pedir |
| RC-82 / N-07 | **FECHADO COM RESSALVA** | o `UX-003` passou a contar participantes e o link casa com o número; o `UX-063` conta a população certa, mas não tem lista que conte o mesmo conjunto |
| RC-84 (parte) | **FECHADO COM RESSALVA** só na unidade; **NÃO FECHADO** nas três formas de prazo | a unidade existe e nenhum teste a confere no HTML; prazo e exportação vazia ficaram fora, como a auditoria já registra |

---

## 1. Por RC

### RC-78 / N-01 — a ausência global dita a quem só vê parte — **FECHADO**

**Evidência (código atual)**

- A frase é escolhida por `frase_de_ausencia(alcancadas)`, em
  `backend/processo_seletivo/interface/supervisao.py:1328-1344`. Ela lê **só** o dicionário
  `alcance(ator, processo)` (`supervisao.py:1286-1319`): `None` se não alcança nada, a global se
  alcança tudo (`all`), senão a relativa. As duas frases estão em `supervisao.py:1324-1325`.
- A página do Processo lê o `alcancadas` uma vez e o usa para decidir a região, os sinais e a
  frase: `interface/views.py:3970-3989` (`"ausencia": ...frase_de_ausencia(alcancadas)` em `:3983`). A
  Supervisão faz o mesmo em `views.py:4051-4064`. O template usa `{{ ausencia }}`:
  `processo_detalhe.html:143`, `supervisao.html:140`.
- A entrada não depende de objeto. `alcance` usa permissões e a presidência **do próprio leitor**
  (`pode_gerir_comissao`). Não há caminho de dado entre sinal suprimido e frase. `alcance_no_edital`
  não entra, e é por isso que quem alcança tudo num Processo de Editais encerrados continua lendo a
  global, como pede o caso-limite.

**Segue a decisão?** Sim. É a `D-004` da 045 e a leitura do N-01. Nenhum papel sozinho alcança o
catálogo: o Gestor não tem `UX-005`/`UX-064`/`UX-066`, o Julgador só tem os dois de recurso, o
Publicador só o `UX-066`, o Auditor só o `UX-004` e o `UX-065`.

**Testes**: `tests/interface/test_supervisao.py:533-643`. O caso "três papéis leem a relativa"
reprova o código antigo. O caso "a frase não muda com o que o leitor não alcança" compara o trecho
**byte a byte**. Ele passaria também no código antigo, que tinha frase fixa: é guarda contra uma
implementação futura, e não prova da correção. O caso do Edital encerrado (f) é o que reprovaria uma
escolha por `alcance_no_edital`.

**Ressalvas**: nenhuma de correção.

### RC-79 / N-02 — o recurso em admissibilidade e o contador — **FECHADO COM RESSALVA**

**Evidência**

- `sinais_do_recurso` (`supervisao.py:1105-1186`) filtra as linhas de **uma** chamada a
  `recursos_do_edital` por `AGUARDANDO_DECISAO`, que é admissibilidade **e** julgamento
  (`supervisao.py:1085-1088`, filtro em `:1146-1150`). A partição travadas/soltas corre sobre a
  união, no mesmo ato (`:1156-1158`). A mensagem diz a fase pelas peças **daquele** sinal
  (`fase_das_pecas`, `:1091-1102`), com as três formas do contrato.
- A peça decidida sai porque a situação vem de `_situacao`
  (`recursos/application/selectors.py:105-110`): inadmitida → `INADMITIDO`, julgada → `DECIDIDO`.
  Nenhuma das duas está em `AGUARDANDO_DECISAO`.
- O contador passou a *"Recursos aguardando decisão (N)"* (`interface/acoes.py:126-131`), por
  `recursos_aguardando_decisao` (`acoes.py:319-334`): uma consulta com `~Exists(juízo) |
  (Exists(juízo admitido) & ~Exists(decisão))`, sem materializar peça. Semanticamente é o mesmo
  predicado de `_situacao`, e o juízo é único por peça (`uq_juizo_por_recurso`).
- O impedimento vale igual nas duas fases: `admitir` chama `exigir_elegibilidade` sem Etapa
  (`recursos/application/admitir.py:54`), e é o alcance que `impedidos_por_recurso` já usa. Não entra
  consulta nova.

**Segue a DP-02?** Sim, a opção A. O catálogo não cresceu, a fase é dita e o contador conta só as
pendentes.

**Testes**: `tests/integration/supervisao/test_sinais.py:988-1080`. Os cinco casos da US2 reprovam o
código antigo, e o `UX-005` na admissibilidade está coberto. O contador está em
`tests/interface/test_hardening_pos_auditoria.py:1117-1150`.

**Ressalvas**

1. **Num Edital encerrado ou cancelado, a metade `UX-064` da partição continua suprimida, e a outra
   metade não** (Defeito D1). A própria 045 mediu que recurso continua decidível nesse Edital
   (`research.md`, R-7). Mesmo assim a peça com julgador livre some da Atenção, enquanto a de
   comissão inteira impedida aparece como `UX-005`, e o cartão do Edital mostra *"Recursos
   aguardando decisão (1)"*.
2. **O predicado "aguardando decisão" existe em duas redações** — Python em `_situacao` e SQL em
   `acoes.py` —, e o teste do contador não exercita os ramos *sem juízo* e *julgado* (D3).

### RC-80 / N-05 + N-06 — `schedule.status` e o encaminhamento que não resolve — **FECHADO** (ressalvas menores)

**Evidência**

- **A fase é derivada na leitura.** `calendario.fase` (`editais/domain/calendario.py:76-100`) **lê**
  `vencido` e não o reescreve: planejado antes do início, concluído se vencido, em andamento entre os
  dois, `None` sem início. `fase_do_evento` (`supervisao.py:360-375`) põe o `CANCELADO` antes de
  tudo e lê o período de inscrições pela régua do período (`FASE_DO_PERIODO`, `:353-357`, sobre
  `periodo_de_inscricoes`). Os demais Eventos passam pela régua do vencido. `marcos_do_edital`
  (`:378-408`) corta pelo *concluído*, e não mais por `término or início <= agora`. O `Marco` tem
  `fase` e `em_andamento` (`:113-121`), e os dois templates marcam só *"em andamento"*
  (`processo_detalhe.html:121`, `supervisao.html:119`). *"declarado"* sumiu do repositório.
- **O `UX-002` saiu, e o `UX-001` também.** `ESPECIES` tem oito (`supervisao.py:540-549`).
  `etapas_sem_marco`, `divergencias_temporais`, `posicao_temporal`, `COERENTES` e `DECLARACOES` não
  existem mais (grep limpo).
- **O `UX-001` virou aviso.** `_etapa_sem_evento` (`editais/domain/validation.py:1242-1290`) produz
  `Severity.WARNING` com código próprio `stage_without_schedule_event`, **só** quando
  `ato == ATO_DE_PUBLICACAO`. É chamado em `validate_for_publication` (`:1481`) e, desde a 046, é o
  único "fato do conteúdo publicado" que o Edital publicado ainda mostra (`FATOS_DO_CONTEUDO_PUBLICADO`,
  `:1297`; `views.py:862-866`). O agrupamento das repetidas fica em `interface_extras.py:338-340`.
- **Nenhuma entrada declara fase ordinária.** O domínio recusa em `validate_event`
  (`editais/domain/cronograma.py:15-16`, `:32-39`), pela `validate_schedule` que `replace_draft` já
  chamava (`editais/application/draft.py:213`). O serializer anuncia só `PLANEJADO` e `CANCELADO`,
  com a mesma razão (`editais/api/serializers.py:190-199`). A tela normaliza o que só herdou
  (`interface/forms.py:1331-1341`). A Retificação grava `PLANEJADO` no Evento novo
  (`interface/retificacao.py:1495`) e o reaproveitamento reinicia em `PLANEJADO`
  (`editais/domain/reaproveitamento.py:299`).
- **Nenhuma migration.** O modelo mantém os quatro `choices` (`editais/models/cronograma.py:20-21`) e
  o `derivado()` da 026 não mudou (`mutabilidade.py:432`).

**Segue a DP-01 e a DP-03?** Sim. DP-01: opção A — a fase é derivada, `CANCELADO` continua
declaração, e não nasceu caminho de tela para declará-lo. DP-03: opção A — o aviso aparece na
composição e na Revisão, fica fora da Atenção, e `scheduleEventId` não foi para a Retificação.

**A D-004 da 022 foi substituída explicitamente?** Sim. O bloco *SUBSTITUÍDA* está em
`specs/022-supervisao-do-processo/spec.md:119-124`, com o texto de 09/09 preservado. A `FR-023` foi
riscada e aponta para a `FR-735` (`:474-477`), e a `FR-027` e o `UX-002` foram riscados e retirados
(`:526-530`, `:567-569`). As marcas "ampliada", "refinada" e "deixou de ser espécie" estão nas
`FR-026`, `FR-030`, `FR-033`, `UX-001` e `UX-005`. Na 038, a `FR-561` e a `FR-565` foram riscadas e o
`UX-064` anotado (`038/spec.md:168-171`, `:201-205`, `:216-221`).

**Testes**: `tests/unit/editais/test_calendario.py:133-161` (as três fases, o Evento pontual, o `<`
estrito, sem início); `tests/integration/supervisao/test_pulso.py:300-385` (período sem término em
andamento, Evento pontual sai, cancelado não aparece, conteúdo publicado com `EM_ANDAMENTO` lido como
não cancelado e não reescrito); `tests/contract/test_edital_draft_api.py` (recusa de
`EM_ANDAMENTO`/`CONCLUIDO`, `CANCELADO` aceito, contrato do serializer);
`tests/unit/editais/test_etapa_sem_evento.py`; `tests/interface/test_compor.py` (aviso na etapa, na
Revisão e no Edital publicado).

**Ressalvas** (nenhuma reabre o RC)

- Rascunho gravado pela API **antes** da 045 com `EM_ANDAMENTO`/`CONCLUIDO` ainda publica sem
  regravar (D5).
- O período de inscrições `CANCELADO` continua apresentado como aberto no cabeçalho do pulso (D6).
- `test_cronograma_normal_nao_produz_sinal_algum` promete no nome mais do que afirma (D7a).
- A 022 conserva texto normativo que contradiz a 045 e ficou sem marca (D8).

### RC-81 / N-04 — sinal sem caminho não dizia a quem pedir — **FECHADO COM RESSALVA**

**Evidência**

- `Sinal` ganhou `conducao` (`supervisao.py:217-220`), e `_sinal.html` a exibe no ramo `elif` —
  só sem destino.
- Depois da 045, **só o `UX-046` pode ficar sem destino**, porque `ENCAMINHAMENTOS_QUE_ALTERAM_O_EDITAL
  = {UX_046}` (`supervisao.py:1197`). Nele, `conducao = CONDUCAO_DA_RETIFICACAO` quando o destino é
  `None` (`:744-746`). A frase **mudou de casa** para `interface/conducao.py` sem ser redigida de novo:
  continua `frase_do_aviso((base_de_permissao("retificar"),), ...)`, e `views.py` a importa dali.
- **Falta de permissão ficou separada de situação que não admite.**
  `situacao_admite_retificacao` (`:1225-1237`) exige Processo fora de `PROCESSO_FINAL` e Edital
  `PUBLICADO`. Onde ela é falsa o sinal nem é montado (`sinais`, `:1391-1392`), de modo que, no
  `UX-046`, `destino is None` passa a significar só "este leitor não retifica".
- As telas de destino passaram a conduzir quem só consulta, pelo mecanismo único
  (`frase_do_aviso` + `BASES_DA_GESTAO_DA_COMISSAO`): ocupação para o Auditor
  (`views.py:6358-6369`, `ocupacao.html:20-29`), sorteio para o Auditor (`views.py:8117-8128`,
  `sorteio.html:21-30`) e prévia para o Publicador diante de ato obsoleto (`views.py:6994-6998`,
  `previa_de_publicacao.html:143-151`). O acréscimo manual *"A presidência não é papel…"* repete o
  precedente da ordenação (`ordenacao.html:248`).
- `pode_emitir` nas duas telas é `pode_gerir_comissao` (`views.py:5652`), isto é, **só permissão**.
  A frase nunca aparece para quem pode agir por um motivo de situação.

**Segue a DP-03 e a D-003?** Sim. É a separação que a `FR-741` pede, e a frase nomeia permissão,
nunca pessoa.

**Testes**: `test_sinal_do_acervo_sem_quadro.py:153-213` (frase sem caminho; caminho sem frase;
encerrado e cancelado sem sinal; Processo em estado final sem sinal), `test_ocupacao.py`,
`test_console_do_sorteio.py`, `test_marco_removido.py`. Os casos de condução reprovam o código
antigo.

**Ressalvas**

1. **A prévia bloqueada por `REINGRESSO_PENDENTE` não diz a quem pedir** (D2). A `SC-272` fica aberta
   nesse caso.
2. O `UX-065` em recorte sem quadro, o `UX-004` em Processo final e o sorteio que não mostra o ato
   obsoleto continuam como a 045 os registrou (`research.md`, R-7). São resíduos declarados, e não
   defeitos novos.
3. A matriz cita `test_as_conducoes_produzidas_seguem_a_formulacao_canonica` para a `FR-740`, mas esse
   guarda (`tests/test_gramatica_das_portas.py:327-352`) só enumera `CONDUCAO_DA_RETIFICACAO` e
   `CONDUCAO_DA_COMPOSICAO`. As três frases novas não passam por ele. São canônicas por construção,
   porque saem de `frase_do_aviso`, mas a citação promete mais do que o teste cobre.

### RC-82 / N-07 — "2 de 5" contando eliminadas — **FECHADO COM RESSALVA**

**Evidência**

- `resumo_da_etapa` (`avaliacoes/application/selectors.py:200-268`) agrega sobre a **população de
  participantes**. Com panorama, é `id__in=panorama["participantes"]` (`:231`), o mesmo conjunto da
  lista. Sem panorama, dobra as três regras por `_so_participantes(prefixo="")` (`:240-247`), com
  `vigentes` montado **do mesmo conteúdo**, sem reler a versão (a correção da revisão do PR). Não
  existe mais modo "toda inscrição".
- A Supervisão passa o conteúdo vigente que já leu (`supervisao.py:625`).
- O link do número passou a `?cobertura=carente` (`distribuicao.html:56`), um filtro novo
  `atribuidas < previstas`, inclusive zero (`selectors.py:44`, `:158-159`). A ficha e *"todas"*
  mostram participantes (`distribuicao.html:48`, `:52-53`).

**Segue a decisão?** Sim, a `FR-742` refinando a `FR-033` da 022, e a marca está na 022.

**Testes**: `tests/integration/resultados/test_progressao_com_corte.py:349-424`. As duas formas dão o
mesmo denominador, o `UX-003` do painel mostra os participantes com a unidade, e a versão não é
relida. `tests/interface/test_distribuicao.py:360-396` confere que o número e a lista têm o mesmo
tamanho, inclusive com participante sem avaliador. Os dois reprovam o código antigo.

**Ressalvas**

1. **`UX-063`**: a população agora é a certa, mas "o número e a lista para onde ele leva MUST contar o
   mesmo conjunto — mesma população e mesmo filtro" (`FR-742`) não vale para ele (D4).
2. O teste de equivalência usa o cenário `cortado`, que tem *aguardando a anterior* e *fora do corte*,
   mas **nenhuma eliminada antes** (`test_progressao_com_corte.py:86-146`). A `T034` pedia as três
   populações, e pedia também o caso "todas eliminadas → sem `UX-003`". Esse não foi escrito: a
   matriz aponta para o caso de zero inscrições (D7c).

### RC-84 (em parte) — unidade da medida e prazo em três formas — **unidade: FECHADO COM RESSALVA; prazo: NÃO FECHADO**

**Evidência**: `Medida.unidade` e `unidade_legivel` (`supervisao.py:167-191`), declaradas por
espécie: inscrição no `UX-003` (`:653`) e no `UX-063` (`:687`), recurso no `UX-064` (`:1180`),
recorte no `UX-046` (`:734`). `_sinal.html` imprime a unidade, e a mensagem do `UX-046` deixou de
repetir os números.

**Ressalvas**

- `unidade` tem `compare=False`. Todo teste que compara `Medida(numerador=…, denominador=…)` passa com
  ou sem unidade (por exemplo `test_sinais.py:1003`, `:1040`). As unidades do `UX-063` e do `UX-064`
  não são conferidas por teste nenhum, e **nenhum teste renderiza `_sinal.html`** para ver a unidade
  (ou a condução) no HTML (D7b).
- As **três formas de prazo** não foram tocadas: `supervisao.html:102` continua com
  `Encerra em {{ …|timeuntil }}`, dito também **antes** de o período abrir, porque `restante` é
  calculado sempre que `estado != ENCERRADO` (`supervisao.py:342`). A exportação vazia sem mensagem
  também ficou. A spec declara as duas fora (*Out of Scope*) e a auditoria já as marca como
  PARCIALMENTE. Se o briefing entendeu que "prazo em três formas" foi fechado, **não foi**.

---

## 2. Conferências transversais pedidas

- **Catálogo fechado (`FR-565` da 038).** Respeitado. A substituição é explícita
  (`038/spec.md:216-221`), a `FR-744` nomeia as oito espécies por extenso, e `ESPECIES` tem as mesmas
  oito. O guarda passou a ler a `FR-744` e a conferir a cadeia 022 → 038 → 045
  (`tests/acceptance/test_supervisao_do_processo.py:116-168`); o unitário diz oito
  (`tests/unit/interface/test_supervisao.py:10-35`). Os identificadores `UX-001`/`UX-002` não foram
  reaproveitados.
- **Derivação única Processo × Supervisão.** Respeitada. As duas views chamam `alcance`, `sinais`,
  `frase_de_ausencia` e `pulso` do mesmo módulo, e nenhuma template recalcula. Há **duas redações** de
  regras em outro lugar: "aguardando decisão" (Python × SQL, D3) e a participação (panorama ×
  restrição SQL). A segunda já existia desde a 013 e tem teste de equivalência, que não cobre a
  eliminada antes.
- **Autorização / segregação.** Não achei vazamento novo. A frase depende só de permissão e
  presidência do leitor. As conduções novas só aparecem a quem não emite (`pode_emitir` e
  `pode_ver_a_classificacao` são permissão pura) e nomeiam permissão, nunca pessoa. Nenhuma
  capacidade nova.
- **Custo de consulta.** Não há N+1 novo. No painel, cada Etapa ganhou no máximo **uma** consulta,
  `ha_resultado_em`, a do gate de `_anteriores_e_gate`, só quando há Etapa anterior. `faixas_que_governam`
  entra como subconsulta, sem round-trip. O sinal de recurso continua sem consulta nova, e o contador
  continua sendo uma consulta por Edital, como antes.
- **Casos-limite conferidos.**
  - `CANCELADO`: sai dos marcos, e a derivação nunca o põe em fase ordinária. Exceção: o cabeçalho do
    período, D6.
  - Evento sem término: vence pelo início; o período sem término segue *em andamento* pela régua do
    período.
  - Instante exato: `<` estrito, coerente com `periodo.py`.
  - Fuso: tudo em instantes *aware*, sem truncar dia.
  - Edital encerrado/cancelado: o `UX-046` sai. Ver D1 para o `UX-064`.
  - Zero espécies: a região não aparece (`test_supervisao.py:465`).
  - Evento sem início: sem fase. O período de inscrições sem início receberia *em andamento*, mas a
    forma publicada exige `startAt`, então o caso não é alcançável.

---

## 3. Defeitos encontrados

Ordenados por severidade. "Confiança" é sobre o **comportamento descrito**; onde o comportamento é
decisão herdada, isso vai dito ao lado.

### D1 — Edital encerrado/cancelado: o `UX-064` some e o `UX-005` fica — **média**

- **Cenário.** Um Edital `PUBLICADO` com um recurso aguardando decisão e um membro livre na comissão
  é encerrado. Nada impede encerrar com peça pendente (`processos/domain/finalizacao.py:55-60` só
  confere o estado), e nada impede interpor depois do encerramento: nem
  `recursos/application/interpor.py` nem o portal conferem o estado do Edital. O Julgador abre o
  Processo e lê *"Nenhuma condição de atenção entre as que você acompanha neste Processo."* Na mesma
  hora, o cartão do Edital e a lista de Processos dizem *"Recursos aguardando decisão (1)"*
  (`acoes.py:66`, `:126` — `ESTADOS_COM_INSCRICOES` inclui `ENCERRADO` e `CANCELADO`). Se a comissão
  inteira estiver impedida, a mesma peça **aparece**, como `UX-005`.
- **Onde.** `supervisao.py:552` (`UX_064` em `TRABALHO_PENDENTE`), `:576-580` (`alcance_no_edital`),
  `:1141-1142`, `:1171`.
- **Por que é defeito, e não só decisão da 038.** A 038 suprimiu o trabalho pendente em Edital
  parado porque *"trabalho não se retoma num Edital que parou por ato"*. A R-7 da própria 045 mediu o
  contrário para recursos: *"julgar o recurso continua possível"* ali. `admitir.py` e `julgar.py` não
  conferem estado de Edital nem de Processo. A 045 usou essa medição para absolver o `UX-005`, e não
  a estendeu ao `UX-064`, que é a outra metade da **mesma** partição. O efeito:
  - o mesmo fato aparece ou some conforme o impedimento;
  - a `SC-270` (*"aparece na Atenção do Julgador na primeira leitura seguinte"*) falha nesses Editais;
  - a frase da matriz de rastreabilidade — *"todo trabalho pendente que a Supervisão acompanha é
    visível"* — deixa de valer para eles.
- **Confiança.** Alta no comportamento. Média em classificá-lo como defeito: o caso-limite da 045
  (*"O alcance muda com o estado do Edital"*) aceita a supressão, mas sobre uma premissa que a R-7
  desmentiu. É decisão do usuário, e deve ir a registro.

### D2 — prévia bloqueada por reingresso pendente não diz a quem pedir — **média-baixa**

- **Cenário.** Um recurso deferido reabilita alguém, e o Resultado dessa pessoa ainda não foi
  consolidado na Etapa. O ato vigente não foi divulgado, então o `UX-066` dispara. O Publicador (só
  `resultado:publicar`) segue o sinal até a prévia. `aferir` devolve `REINGRESSO_PENDENTE` antes de
  olhar a natureza, e bloqueia também a preliminar (`divulgacao/domain/publicabilidade.py:300-311`).
  A mensagem manda *"Consolide o resultado dessa inscrição na Etapa e emita o ato sucessor antes de
  divulgar"* (`:85-87`). Como `ADMITE_SUCESSOR[REINGRESSO_PENDENTE]` é `False` (`:145`), o template não
  entra em nenhum dos dois ramos (`previa_de_publicacao.html:143-151`). A pessoa recebe a ordem de
  praticar um ato que não é dela, sem caminho e sem a quem pedir.
- **Por quê.** A 045 só tratou o ramo `admite_sucessor` (ato obsoleto), porque a R-7 só mediu esse
  bloqueio. A `SC-272` pede *"zero sinais cujo ato o leitor não pode praticar e que não digam, no sinal
  ou na tela a que levam, a quem pedir"*.
- **Vizinho menor.** No `CORTE_OBSOLETO` (`admite_sucessor` verdadeiro), a condução nova diz *"Emitir
  o ato sucessor depende…"*, enquanto a mensagem manda *"Emita a geração sucessora"* do corte: a
  condução nomeia o ato errado.
- **Confiança.** Alta no código. O cenário é plausível num certame com recurso deferido.

### D3 — "aguardando decisão" em duas redações, e o teste do contador cobre metade — **baixa**

- `_situacao` (`recursos/application/selectors.py:105-110`) decide a fase em Python para o sinal.
  `recursos_aguardando_decisao` (`interface/acoes.py:319-334`) reescreve a mesma regra em SQL, na
  camada de interface. Hoje as duas concordam.
- O teste do contador (`test_hardening_pos_auditoria.py:1117-1150`) só monta uma peça admitida e sem
  decisão (conta) e uma inadmitida (não conta). Os ramos `~Exists(juízo)` (recém-interposta) e
  "admitida **e** julgada" não são exercitados, e nenhum teste compara o contador com o denominador
  do `UX-064` no mesmo cenário.
- **Cenário de falha.** Uma situação nova em `_situacao` (desistência, por exemplo) move o sinal e
  deixa o contador para trás, sem nada vermelho. É a "segunda verdade" que a 038 e a 045 dizem
  remover.
- **Confiança.** Alta, mas é risco, e não falha presente.

### D4 — `UX-063`: o número não tem lista, e a `SC-273` só vale para o `UX-003` — **baixa**

- A `FR-742` exige que *"o número e a lista para onde ele leva"* contem *"o mesmo conjunto — mesma
  população e mesmo filtro"* para o `UX-003` **e** o `UX-063`.
- O `UX-063` mede *paradas* (distribuídas por inteiro e não concluídas) sobre *completas*
  (`supervisao.py:678-687`). A distribuição não tem filtro para esse conjunto: `avaliacao_pendente`
  (`selectors.py:160-161`) é `concluidas < previstas` e inclui quem nem foi distribuído. O número
  *"com avaliação pendente"* da ficha é `sem_conclusao`, outro conjunto.
- A `SC-273` diz *"para cada sinal com medida, o denominador coincide com o número de linhas da tela
  de destino"*. Isso vale para o `UX-003` (participantes = *"todas"*), e não para:
  - o `UX-063`, cujo denominador é *completas* e cujo destino é a lista inteira;
  - o `UX-064`, cujo denominador são as peças pendentes, enquanto a tela de recursos, por decisão da
    própria `FR-734`, lista todas (e o filtro `?situacao=` só aceita uma fase).
- A matriz dá a `SC-273` como fechada com testes que só olham o `UX-003`. Há tensão interna na spec
  (`FR-734` × `SC-273`).
- **Confiança.** Alta.

### D5 — rascunho legado com fase declarada ainda publica — **baixa**

- A recusa vive em `validate_event`, que só `replace_draft` chama (`draft.py:213`).
- `publish_edital` copia `event.status` da linha do rascunho para o conteúdo publicado
  (`publicacoes/application/publish_edital.py:293`), e a forma publicada aceita qualquer `str`
  (`editais/domain/validation.py:175`, `Campo("status", str)`).
- **Cenário.** Um rascunho gravado pela API antes da 045 com `EM_ANDAMENTO` e submetido sem regravar
  o Cronograma — pela API, ou pela tela sem passar pela etapa do Cronograma — publica `EM_ANDAMENTO`
  depois da 045.
- A leitura trata o valor como *não cancelado*, então nada aparece errado. Mas a `FR-737`
  (*"o campo guardado passa a responder uma pergunta só"*) não fica garantida para o que ainda está
  em elaboração.
- **Confiança.** Alta. O impacto é pequeno.

### D6 — período de inscrições `CANCELADO` apresentado como aberto no pulso — **baixa**

- `periodo_do_edital` → `periodo_de_inscricoes` → `evento_designado`
  (`inscricoes/domain/periodo.py:34-60`) não filtra `CANCELADO`.
- **Cenário.** Um período `CANCELADO` (só a API o produz) com datas em curso. O cabeçalho do pulso da
  gestão diz *"Inscrições de … a … Encerra em …"*, `algum_periodo_em_curso` fica verdadeiro, e a série
  e as últimas 24 h aparecem. Enquanto isso, `marcos_do_edital` omite o mesmo Evento
  (`supervisao.py:370-371`).
- A `FR-736` diz *"nas superfícies da gestão, Evento cancelado nunca é apresentado em fase
  ordinária"*. O portal (registrado fora) tem o mesmo defeito, e pior: recebe inscrição.
- **Confiança.** Alta no código. A alcançabilidade é baixa.

### D7 — testes que não provam o que dizem — **baixa**

- **a.** `test_cronograma_normal_nao_produz_sinal_algum` (`test_sinais.py:48-94`) promete no nome
  *"nenhum sinal"*, mas só afirma que `"UX-002"` e `"UX-001"` não estão entre as espécies —
  identificadores que o código já não consegue produzir. Qualquer sinal espúrio de Cronograma sob
  outra espécie passaria.
- **b.** `Medida.unidade` tem `compare=False`, e todo `Medida(n, d)` dos testes passa com ou sem
  unidade. Ficam sem teste nenhum:
  - as unidades do `UX-063` e do `UX-064`;
  - a renderização de `_sinal.html` com unidade e com condução;
  - o ramo `{% elif sinal.conducao %}`.

  A `SC-273` diz *"100% das medidas nomeiam a unidade"*; conferido por teste, só o `UX-003` e o
  `UX-046`, e só no domínio.
- **c.** O teste de equivalência painel × distribuição não tem *eliminada antes*, e o caso "todas
  eliminadas → sem `UX-003`" não existe. A matriz aponta para
  `test_sem_inscricao_submetida_nao_ha_cobertura_a_cobrar`, que monta zero inscrições. Não é o mesmo
  caminho: ali a população é vazia antes da restrição.
- **d.** A `FR-740` cita um guarda de formulação que não enumera as três frases novas (ver RC-81,
  ressalva 3).
- **e.** O teste do vazamento (`test_a_frase_nao_muda_com_o_que_o_leitor_nao_alcanca`) passaria também
  no código anterior à 045, que tinha frase fixa. Serve como guarda, e não como prova da correção. A
  prova é o caso dos três papéis e o do Edital encerrado.

### D8 — texto da 022 que contradiz a 045 sem marca — **baixa (documentação)**

- `specs/022-supervisao-do-processo/spec.md:93-96`, na nota da `D-002`: *"A lista vigente tem **dez**
  espécies e está na `FR-024` emendada"*. Agora são oito, na `FR-744`.
- `:264`, nas *Clarifications*: *"o `status` do Evento deixa de ser declarado? → **Não** (`D-004`)"*.
- `:343-346`: a US3, cenários 1 e 2, descrevem o `UX-001` na Supervisão e o `UX-002` apresentando
  *"as duas informações"*.
- Nenhum dos três ganhou marca. A `SC-274` fala em *requisitos*, e isso é texto normativo vizinho.
  Leitor que chega pela `D-002` ou pelos cenários lê o oposto do que o código faz.
- `backend/tests/fixtures/supervisao.py:27-60` mantém o parâmetro `status`/`status_do_periodo` com a
  docstring *"`status` viaja porque ele é metade da divergência de `UX-002`"*. A `T016` mandava tirá-lo.

### D9 — detalhes de apresentação do aviso — **baixa**

- O `UX-086` diz *"A Etapa e o Edital são nomeados"*, e a mensagem nomeia só a Etapa
  (`validation.py:1283-1288`). Nas telas o Edital é implícito; na API ele não aparece.
- O contrato, §4, diz *"Várias Etapas sem Evento viram uma linha"*. Isso vale no assistente e na
  Revisão, via `_pendencias.html` e `agrupar_repetidas`. A *"Validação do conteúdo"* da página do
  Edital (`detalhe.html:170-178`) itera sem agrupar, e N Etapas viram N linhas.
- O contrato, §2, pede no sorteio *"que o emita"*; o código diz *"Conduzir o sorteio… que o conduza"*
  (`views.py:8117-8128`). É inócuo, mas diverge do contrato, que só admitia ajuste de pontuação.

---

## 4. O que a spec prometeu e não entregou

| Promessa | Onde | O que houve |
|---|---|---|
| `SC-272`: zero sinais sem "a quem pedir" | spec | falta a prévia com `REINGRESSO_PENDENTE` (D2) |
| `SC-270` na primeira leitura | spec | não vale em Edital encerrado/cancelado com julgador livre (D1) |
| `FR-742`: número e lista com o mesmo filtro, `UX-063` incluído | spec | só o `UX-003` tem lista casada (D4) |
| `SC-273`: denominador = linhas do destino, para **cada** sinal com medida | spec | só o `UX-003`; `UX-063` e `UX-064` divergem (D4) |
| `UX-086`: Etapa **e** Edital nomeados | spec | só a Etapa (D9) |
| `T016`: tirar o `status` das fixtures, inclusive `fixtures/supervisao.py` | tasks | o arquivo não foi tocado; o parâmetro e a docstring do `UX-002` ficaram (D8) |
| `T034`: eliminada antes no cenário de equivalência; "todas eliminadas → sem `UX-003`" | tasks | nenhum dos dois (D7c) |
| `T029`: sorteio *"que o emita"* | tasks/contrato | *"que o conduza"* (D9) |
| Contrato §4: agrupar na página do Edital | contrato | só no assistente e na Revisão (D9) |
| `FR-745`: marcar o que foi substituído | spec | feito nos requisitos; a nota da `D-002`, a clarificação e os cenários da US3 da 022 ficaram sem marca (D8) |
| Rastreabilidade, `FR-740` e *"Etapa sem ninguém a avaliar"* | rastreabilidade | cita testes que não cobrem o que dizem (D7c, D7d) |

Entregue conforme prometido e conferido no diff:

- nenhuma migration, nenhuma capacidade nova;
- nenhum `choices` retirado;
- nenhum conteúdo publicado reescrito;
- `DECLARACOES` e todo o maquinário do `UX-001`/`UX-002` apagados;
- `sinais()` sem `agora`;
- a frase da Retificação extraída, e não redigida de novo;
- o guarda do catálogo lendo a `FR-744`;
- a `T003`, entregue pelo #189 (`tests/fixtures/publicacao.py:62-78`, asserção incondicional).

## 5. Resíduos que continuam abertos

1. **RC-84, a outra metade.** As três formas de prazo (`supervisao.html:102`, com `timeuntil`) e o
   *"Encerra em…"* dito antes de o período abrir (`supervisao.py:342`); a exportação vazia sem
   mensagem.
2. **Os registrados pela 045** (`research.md`, R-7, e *Out of Scope*):
   - o `UX-065` em recorte sem quadro;
   - o `UX-004` num Processo em estado final;
   - o sorteio, que não mostra o ato obsoleto;
   - a frase da ordenação para o Publicador, redigida à mão (`ordenacao.html:66`);
   - o portal com regra própria de fase (`portal/leitura.py:62`);
   - o portal e o PDF, que não filtram `CANCELADO`;
   - nenhum caminho de tela para declarar `CANCELADO`.
3. **A assimetria da 038, que a R-7 tornou discutível.**
   - O `UX-063` e o `UX-064` somem em Edital parado; o `UX-003` e o `UX-005` ficam (D1 é a parte
     grave).
   - Nenhuma espécie, além do `UX-046`, considera Processo em estado final.
   - Sem comissão ativa, o `UX-005` e o `UX-064` não disparam (`supervisao.py:1131-1137`), mas o
     contador continua mostrando N.
4. **Duas redações de regra** que dependem de disciplina para não divergir:
   - "aguardando decisão" (D3);
   - participação por panorama × restrição SQL, já existente, com equivalência testada sem a
     eliminada antes.
5. **N-08** (juntar os avisos da validação à Atenção): continua sem decisão, como a spec declara.
6. **Documentação da 022** a marcar (D8).
