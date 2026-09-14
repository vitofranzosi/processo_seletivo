---

description: "Tarefas de implementação — contrato de mutabilidade normativa"
---

# Tasks: Contrato de mutabilidade normativa

**Input**: artefatos de desenho em `specs/026-contrato-de-mutabilidade-normativa/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/mutabilidade.md](contracts/mutabilidade.md),
[matriz.md](matriz.md), [quickstart.md](quickstart.md)

> ## ✅ Gate: matriz aprovada em 2026-09-13
>
> [matriz.md](matriz.md) foi aprovada como proposta — 121 entradas, as 30 linhas ⚠️ e as 5 políticas
> de objeto ausente, sem emenda. Ela é **norma**, e as tarefas da fase 3 a **transcrevem**.
>
> Divergir dela durante a implementação não é ajuste: é decisão nova, e volta para o usuário.
> Natureza, razão e política de ausência afetam direitos, e não são decisão de quem implementa.

**Tests**: obrigatórios. O entregável central **é** um teste, e o princípio V faz da
rastreabilidade requisito. Em cada história os testes vêm **antes** da implementação, e precisam
falhar pela razão certa antes de qualquer código.

**Execução**: sequencial. Ver [Dependencies](#dependencies) — as histórias não são paralelizáveis.

## Format: `[ID] [P?] [Story] Descrição`

- **[P]**: pode correr em paralelo (arquivo distinto, sem dependência pendente)
- **[Story]**: US1 a US6, conforme a spec
- Caminho de arquivo exato em cada tarefa

## Path Conventions

Monólito Django. Código em `backend/processo_seletivo/`, testes em `backend/tests/`. Nenhum app
novo, **nenhuma migration**.

---

## Phase 1: Setup

**Purpose**: o Edital que a enumeração percorre, e o ambiente de onde as jornadas se verificam.

- [ ] T001 Estender `rascunho_completo()` em `backend/tests/fixtures/snapshot.py` para um **Edital
  máximo**: `classificationMilestones` com ao menos um marco declarado (`stages`, `operation`,
  `normalization`, `rounding`, `cutRule`, `tiebreakers`, `appealWindow` e `drawMethod` completos),
  `vacancyReversion` declarado, `callForm` declarado, `normativeRule` completo em ao menos uma
  Modalidade, `location` preenchido em ao menos um Evento, e **as duas espécies de seção** —
  redigida (com `content`) e gerada (com `source`). Hoje o rascunho traz
  `classificationMilestones: []` (linha 110), `vacancyReversion: None` (121) e `callForm: None`
  (125), e uma travessia sobre ele não encontraria nenhum dos dez campos do método do sorteio.
- [ ] T002 Escrever em `backend/tests/fixtures/snapshot.py` o comentário que registra **por que** o
  rascunho é máximo: enumerar sobre um Edital pobre produz guardião silenciosamente incompleto, que
  é o defeito que esta feature existe para fechar. Sem isto, a próxima pessoa a simplificar a
  fixture não tem como saber o que quebra.
- [ ] T003 Rodar `backend/tests/contract/test_forma_publicada.py` inteiro e confirmar que o Edital
  máximo **publica**. Se a publicação recusar, o rascunho novo viola coerência do domínio, e é ela
  que precisa ser satisfeita — não contornada com um rascunho menor.
- [ ] T004 [P] Acrescentar a entrada `mutabilidade-026` ao `.claude/launch.json` — **acrescentar**,
  sem reescrever o arquivo, que é versionado e carrega entradas de outras sessões. Porta 8026,
  `DB_NAME=ps_demo_026`, `INTERFACE_SELETOR_IDENTIDADE=true`, `PORTAL_IDENTIDADE_DEMO=true`, e
  `localhost` na `url`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: a enumeração e a forma do contrato. Tudo o que vem depois lê daqui.

**⚠️ CRITICAL**: nenhuma história começa antes de esta fase fechar.

### A travessia

- [ ] T005 Escrever a travessia recursiva em
  `backend/tests/contract/test_mutabilidade.py`: do `content` da `VersaoConsolidada` de um Edital
  publicado, descer por listas de entidades e objetos aninhados até o campo escalar, devolvendo
  pares `(coleção, caminho relativo)`. **Chave por caminho relativo**, e nunca pelo último segmento:
  `drawMethod/normalization/rule` e `drawMethod/substitutionRule/rule` colidiriam, e o contrato não
  representaria os dez campos do próprio canário 4.
- [ ] T006 Implementar em `backend/tests/contract/test_mutabilidade.py` a regra do **objeto opaco**:
  a travessia **não desce** nos oito objetos de forma livre listados em
  [data-model.md](data-model.md) — `classificationInformation`, `callInformation`, os quatro de
  `normativeRule`, o `rounding` do marco e o `parameters` do critério —, e o contrato classifica
  cada um **inteiro**. A lista é declarada nominalmente, nunca inferida de o valor ser `dict`:
  `appealWindow`, `drawMethod`, `cutRule`, `vacancyReversion` e `normativeRule` também são objetos,
  têm forma conhecida, e a travessia desce neles. Sem esta regra, o domínio do guardião mudaria de
  Edital para Edital, e a suíte alternaria entre falhar por FR-301 e por FR-302 conforme a fixture.
- [ ] T007 Implementar em `backend/tests/contract/test_mutabilidade.py` a regra da **união**: o
  domínio de uma coleção é a união das chaves dos seus itens, e nunca a interseção. `sections` é o
  caso concreto — `content` e `source` são mutuamente exclusivos, e exigir que todo item carregue
  todo campo faria o guardião falhar conforme a seção que a travessia visse primeiro.
- [ ] T008 Fazer a travessia de `backend/tests/contract/test_mutabilidade.py` **derivar as coleções
  sem lista nomeada** (FR-303): coleção é toda
  lista cujos itens são objetos, em qualquer profundidade. Nenhum literal com os nomes das doze.
  Acrescentar uma coleção ao conteúdo publicado passa a ser suficiente para o guardião a cobrir.
- [ ] T009 Escrever em `backend/tests/contract/test_mutabilidade.py` o teste que **mede a cobertura
  da fixture** e falha quando ela regride: toda coleção que `COLECOES_PUBLICADAS` declara, e todo
  objeto aninhado que `publish_edital.py` sabe emitir, precisa estar presente e **não vazio** no
  Edital de T001. É a resposta ao limite de U1 — uma coleção nova vazia continuaria invisível à
  travessia, e este teste é o que torna a invisibilidade impossível de passar em silêncio.
- [ ] T010 Registrar em `backend/tests/contract/test_mutabilidade.py`, como docstring do módulo, o
  **limite residual da cobertura**: campo que só aparece sob condição que a fixture não exercita
  continua fora da enumeração. T009 reduz o risco às condições que o emissor conhece; não o zera.

### O módulo do contrato

- [ ] T011 [P] Criar `backend/processo_seletivo/editais/domain/mutabilidade.py` com `Natureza`
  (`StrEnum` de quatro valores), `Mutabilidade` (dataclass congelada com `natureza` e `razao`) e
  `CONTRATO: dict[tuple[str, str], Mutabilidade]` ainda vazio.
- [ ] T012 [P] Implementar em `backend/processo_seletivo/editais/domain/mutabilidade.py` a
  validação na **carga do módulo**: `NAO_RETIFICAVEL` sem razão e qualquer outra natureza **com**
  razão levantam na importação (FR-299). Quem escreve o contrato descobre no `import`.
- [ ] T013 [P] Implementar `natureza_de(colecao, caminho) -> Mutabilidade` em
  `backend/processo_seletivo/editais/domain/mutabilidade.py`, levantando `KeyError` para par não
  declarado. **Sem valor padrão**: um padrão é a decisão implícita que D-008 proíbe.
- [ ] T014 Escrever em `backend/tests/contract/test_mutabilidade.py` o teste de T012 — construir
  `Mutabilidade(NAO_RETIFICAVEL)` sem razão falha, e `Mutabilidade(RETIFICAVEL, "…")` também.

**Checkpoint**: a travessia enumera sem lista nomeada, o módulo carrega, o contrato está vazio de
propósito, e T009 garante que a fixture exercita o que o emissor sabe emitir.

---

## Phase 3: User Story 5 — Um campo novo sem decisão quebra a suíte (P1) 🎯 MVP técnico

**Goal**: nenhum campo do conteúdo publicado existe sem natureza declarada.

**Independent Test**: acrescentar um campo ao conteúdo publicado sem tocar em `mutabilidade.py`; a
suíte falha **nomeando o campo e o caminho**. Desfazer, e a suíte volta ao verde.

**T018–T021 transcrevem [matriz.md](matriz.md); elas não decidem.** Entrada que não bater com a
matriz é erro de transcrição, e não escolha de implementação.

### Testes primeiro

- [ ] T015 [US5] Escrever em `backend/tests/contract/test_mutabilidade.py` o guardião na direção
  snapshot → contrato: todo `(coleção, caminho)` que a travessia encontra tem entrada em `CONTRATO`,
  e a falha **nomeia o campo, a coleção e o caminho absoluto onde ele apareceu** (FR-301). Mensagem
  que diga só "divergência" não atende — quem quebrou a suíte precisa ler qual decisão faltou.
- [ ] T016 [US5] Escrever em `backend/tests/contract/test_mutabilidade.py` o guardião na direção
  contrato → snapshot (FR-302). Declarar natureza para campo inexistente é a mesma omissão ao
  contrário.
- [ ] T017 [US5] Escrever em `backend/tests/contract/test_mutabilidade.py` o teste de que toda
  `NAO_RETIFICAVEL` do `CONTRATO` carrega razão não vazia (FR-299, SC-101). O teste confere
  presença; se a razão é normativa ou técnica é leitura humana, e é o trabalho de T022.

Neste ponto os três falham, porque o contrato está vazio. É a falha esperada.

### Transcrição da matriz

- [ ] T018 [US5] Transcrever para `backend/processo_seletivo/editais/domain/mutabilidade.py` as
  seções 1, 8, 9, 10, 11 e 12 da [matriz.md](matriz.md) — raiz, `schedule`, `stages`, `sections`,
  `attachments`, `documentRequirements`. 53 entradas.
- [ ] T019 [US5] Transcrever para `backend/processo_seletivo/editais/domain/mutabilidade.py` as
  seções 2, 3, 4 e 5 da [matriz.md](matriz.md) — `profiles`, `competitionModalities`,
  `vacancyTable`, `declaredFacts`. 37 entradas.
- [ ] T020 [US5] Transcrever para `backend/processo_seletivo/editais/domain/mutabilidade.py` as
  seções 6 e 7 da [matriz.md](matriz.md) — `classificationMilestones` e `tiebreakers`. 31 entradas,
  e é onde moram dez dos vinte e três campos sem decisão do Edital 26/2026.
- [ ] T021 [US5] Transcrever a **política de objeto ausente** da [matriz.md](matriz.md) para
  `backend/processo_seletivo/editais/domain/mutabilidade.py` (FR-313): cinco objetos, cada um com a
  decisão de se a declaração pode passar a existir por Retificação.
- [ ] T022 [US5] Conferir que **nenhuma razão transcrita é técnica** (FR-310). A matriz já marcou
  as candidatas: as linhas ⚠️ com natureza **N** são justamente as que hoje têm exclusão por razão
  técnica em `backend/processo_seletivo/interface/retificacao.py` — `stages` e `operation` (linha
  104), `targetKind`, `governedStage` e `continuation` (linha 117), `whenMissing`, `reserveType` e o
  arredondamento. Razão que descreva limitação de implementação reprova: ela deixa de valer quando
  a limitação some, e ninguém percebe.

### Absorção do guardião antigo

- [ ] T023 [US5] Absorver `NAO_SAO_NORMA` de `backend/tests/contract/test_retificacoes_api.py:89`
  no contrato. `id` e `order` viram `ESTRUTURAL`; `scheduleEventId` recebe a razão escrita que a
  matriz propõe — hoje ele é exclusão **sem razão nenhuma**. O literal local deixa de existir.
- [ ] T024 [US5] Reescrever `test_a_retificacao_alcanca_todo_campo_normativo_da_etapa` em
  `backend/tests/contract/test_retificacoes_api.py` para ler o contrato em vez de `NAO_SAO_NORMA`.
  Ele cobre uma coleção entre doze e continua valendo — o guardião novo o generaliza.

### Fechamento

- [ ] T025 [US5] Escrever em `backend/tests/contract/test_mutabilidade.py` o teste do Independent
  Test: com um campo experimental no conteúdo publicado e sem entrada no contrato, o guardião falha
  com mensagem que **cita o nome do campo** (SC-096). O teste afirma sobre a mensagem, e não só
  sobre o fato de falhar.
- [ ] T026 [US5] Rodar `cd backend && make lint check test-pg` e confirmar **zero campos sem
  natureza** (SC-095).

**Checkpoint**: o contrato existe e o guardião o guarda. É o MVP técnico — mas **não conclui a
spec**: o princípio VI exige jornada pelo canal do ator.

---

## Phase 4: FR-298 e FR-314 — a interface passa a ler o contrato

**Purpose**: fechar os dois requisitos que o desenho prometia e as histórias não entregavam
sozinhas. Precede as jornadas porque é a infraestrutura comum que todas usam — e é o que torna a
execução sequencial defensável em vez de conflituosa.

- [ ] T027 Escrever em `backend/tests/interface/test_campos_vem_do_contrato.py` o teste de FR-298:
  todo campo `RETIFICAVEL` do `CONTRATO` é oferecido pela tela de Retificação, e todo campo
  oferecido tem entrada no contrato. Falha nos dois sentidos.
- [ ] T028 Inverter a autoridade em `backend/processo_seletivo/interface/retificacao.py`: a
  montagem dos grupos passa a **derivar do `CONTRATO`** quais campos existem, e as tuplas `CAMPOS_*`
  passam a ser **apresentação** — rótulo, tipo de controle, opções — indexadas por
  `(coleção, caminho)`. Hoje a lista é a fonte, e um campo retificável que ninguém acrescentou
  simplesmente não existe para a tela, sem que nada acuse.
- [ ] T029 Fazer `campos_editaveis` em `backend/processo_seletivo/interface/retificacao.py:427`
  falhar alto quando um campo `RETIFICAVEL` do contrato não tem apresentação declarada. Silêncio
  aqui reabriria o defeito pelo outro lado.
- [ ] T030 Escrever em `backend/processo_seletivo/editais/domain/mutabilidade.py` o comentário de
  topo que registra a D-011: **a classificação vigente governa os atos futuros**, inclusive sobre
  Edital publicado antes dela. Reclassificar não reescreve conteúdo publicado — a Constituição já o
  torna imutável —; muda o que um ato novo pode fazer.
- [ ] T031 Escrever em `backend/tests/contract/test_mutabilidade.py` o teste de FR-314: retificar um
  Edital publicado **antes** de uma reclassificação segue a classificação **vigente**, e o conteúdo
  já publicado permanece byte a byte o mesmo.
- [ ] T032 Implementar a exigência da FR-315 em
  `backend/processo_seletivo/editais/domain/mutabilidade.py`: reclassificar de retificável para não
  retificável exige, além da razão normativa, o registro de que um caminho de correção foi fechado.
  É a única direção que retira capacidade de quem já publicou.

**Checkpoint**: a tela lê o contrato. As jornadas passam a ser **acrescentar apresentação**, e não
acrescentar campo — e é por isso que elas deixam de disputar o mesmo arquivo estruturalmente.

---

## Phase 5: User Story 1 — Corrigir o local de uma prova publicada (P1)

**Goal**: o local de um Evento publicado se corrige pela tela.

**Independent Test**: publicar um Edital com local declarado, retificá-lo pela interface, e
verificar o Cronograma público e a versão anterior.

- [ ] T033 [US1] Escrever em
  `backend/tests/integration/editais/test_mutabilidade_do_local.py` o teste que falha: Retificação
  que altera o local de um Evento publicado vigora, e a versão consolidada anterior continua
  legível com o local antigo.
- [ ] T034 [US1] Escrever em `backend/tests/interface/test_retificar_cronograma.py` o teste que
  falha: a tela oferece o campo, a conferência o exibe **em português** ("Local"), e a publicação
  vigora com o valor novo (SC-097). `backend/processo_seletivo/publicacoes/domain/alteracoes.py:63`
  já traduz `location` — conferir que o caminho de conferência passa por ali.
- [ ] T035 [US1] Declarar `location` em `EVENTO_PUBLICADO`, em
  `backend/processo_seletivo/editais/domain/validation.py`. **O campo é emitido por
  `backend/processo_seletivo/publicacoes/application/publish_edital.py:261` e não está declarado.**
  Nulabilidade: `backend/processo_seletivo/editais/models/cronograma.py:50` o define como
  `CharField(blank=True, default="")` e `backend/processo_seletivo/shared/canonical.py:97` registra
  que vazio significa "não declarado" — logo `Campo("location", str)` sem `admite_nulo`, como
  `duties` e `workload`.
- [ ] T036 [US1] Acrescentar a apresentação de `("schedule", "location")` em
  `backend/processo_seletivo/interface/retificacao.py:80` — rótulo "Local", tipo `TEXTO`.
- [ ] T037 [US1] Registrar em `backend/processo_seletivo/editais/domain/mutabilidade.py` a
  conclusão do segundo cenário de aceitação: com `location` sempre presente como `""`, informar um
  local onde não havia é **alteração de valor**, e não acréscimo de campo. Comentário na entrada
  `("schedule", "location")`.
- [ ] T038 [US1] Percorrer a jornada 1 do [quickstart.md](quickstart.md) pelo navegador, com o
  servidor da entrada `mutabilidade-026`. Teste verde sobre objeto falso não é jornada — foi o que
  deixou passar o `AttributeError` do PR #113.

**Checkpoint**: a primeira correção que hoje só se faz por API passou a se fazer pela tela. **A
spec já é concluível a partir daqui** pelo princípio VI.

---

## Phase 6: User Story 2 — Corrigir um requisito de participação publicado (P1)

**Goal**: a lista de requisitos de um Perfil publicado se corrige pela tela.

- [ ] T039 [US2] Decidir e registrar em
  `backend/processo_seletivo/editais/domain/mutabilidade.py` **como** `requirements` se retifica:
  substituição da lista inteira ou endereçamento de item. Item de lista de texto não tem identidade
  estável, e "o terceiro requisito" não é endereçar — é contar. **A decisão muda o que o ato
  registra e precisa estar escrita antes do código**; se ela não estiver na matriz aprovada, é
  pergunta para o usuário, e não escolha de quem implementa.
- [ ] T040 [US2] Escrever em `backend/tests/interface/test_retificar_requisitos.py` o teste que
  falha: a tela oferece a correção, e a conferência **nomeia o Perfil e o requisito alterado, sem
  caminho normativo em primeiro plano**.
- [ ] T041 [US2] Escrever em
  `backend/tests/integration/editais/test_mutabilidade_dos_requisitos.py` o teste que falha: a
  página pública exibe a lista corrigida e o comprovante da inscrição anterior continua apontando a
  versão aceita (SC-098).
- [ ] T042 [US2] Implementar a apresentação de `("profiles", "requirements")` em
  `backend/processo_seletivo/interface/retificacao.py`, conforme T039. `CAMPOS_PERFIL` (linha 51)
  hospeda escalares; uma coleção de texto precisa de tratamento próprio — o mecanismo de `LISTA`
  (linha 212) é o precedente mais próximo.
- [ ] T043 [US2] Renderizar o campo em
  `backend/processo_seletivo/interface/templates/interface/_retificacao_perfil.html`.
- [ ] T044 [US2] Percorrer a jornada 2 do [quickstart.md](quickstart.md) pelo navegador.

---

## Phase 7: User Story 3 — Corrigir o prazo recursal publicado (P1)

**Goal**: a janela recursal declarada no marco se corrige pela tela, com a unidade como escolha.

- [ ] T045 [US3] Escrever em
  `backend/tests/integration/editais/test_mutabilidade_da_janela_recursal.py` o teste de fronteira
  que falha: a janela nova vale para o que vier, e **a janela gravada num recurso já interposto
  permanece intacta**.
- [ ] T046 [US3] Escrever em `backend/tests/interface/test_retificar_janela_recursal.py` o teste
  que falha: unidade que o cálculo não interpreta é recusada **com a razão**, e não gravada; e
  marco que não admite recurso não aceita duração.
- [ ] T047 [US3] Escrever em `backend/tests/portal/test_prazo_recursal_retificado.py` o teste que
  falha: depois da vigência, o candidato lê a data-limite recalculada a partir da divulgação do
  resultado (SC-099).
- [ ] T048 [US3] Acrescentar a apresentação dos três campos em
  `backend/processo_seletivo/interface/retificacao.py`: `appealWindow/admits` (`BOOLEANO`),
  `appealWindow/durationDays` (`INTEIRO`) e `appealWindow/unit` — este **como escolha**, nunca como
  texto livre (FR-311). A lista fechada tem um valor só, `DIAS_CORRIDOS`, e
  `backend/processo_seletivo/editais/domain/perfis.py:475` diz por quê.
- [ ] T049 [US3] Fazer a Retificação recusar a contradição reusando `_validar_janela_recursal` em
  `backend/processo_seletivo/editais/domain/perfis.py:460` — e não reescrevendo a regra na
  interface.
- [ ] T050 [US3] Renderizar o bloco da janela em
  `backend/processo_seletivo/interface/templates/interface/_retificacao_marco.html` (novo, se ainda
  não existir).
- [ ] T051 [US3] Percorrer a jornada 3 do [quickstart.md](quickstart.md) pelo navegador, incluindo
  a tela de recurso do candidato — que exige `PORTAL_IDENTIDADE_DEMO=true`.

---

## Phase 8: User Story 6 — A tela diz o que não alcança (P2)

**Goal**: ausência deliberada deixa de parecer defeito.

- [ ] T052 [US6] Escrever em `backend/tests/interface/test_retificar_exclusoes.py` o teste que
  falha: o bloco do marco declara quais campos não se corrigem ali e a razão normativa de cada um
  (SC-102), e a mesma razão não aparece duas vezes no mesmo bloco.
- [ ] T053 [US6] Expor em `backend/processo_seletivo/interface/retificacao.py` a leitura das
  exclusões de uma coleção: os campos `NAO_RETIFICAVEL` com as respectivas razões, vindas de
  `backend/processo_seletivo/editais/domain/mutabilidade.py`.
- [ ] T054 [US6] Renderizar a declaração **uma vez por bloco de coleção**, e não sob cada campo, em
  `backend/processo_seletivo/interface/templates/interface/retificar.html`. Explicação que não muda
  de um cartão para o outro não se imprime uma vez por cartão — é a decisão que
  `backend/tests/interface/test_medida_dos_campos.py` guarda no assistente, e que reprovou a
  primeira tentativa no PR #113.
- [ ] T055 [US6] Percorrer a verificação 3 do [quickstart.md](quickstart.md) pelo navegador.

---

## Phase 9: User Story 4 — Corrigir o método do sorteio publicado (P2)

**Goal**: os dez campos do método se corrigem pela tela, e a relação congelada não é alcançada.

**Nota de prioridade**: R-005 derrubou metade da justificativa de P2 —
`RelacaoDeHabilitados.metodo_hash` já garante FR-309 estruturalmente. A outra metade continua de pé
e é o que mantém a história aqui: dez campos com interdependência, e o desenho precisava dos três
primeiros canários antes deles.

- [ ] T056 [US4] Escrever em
  `backend/tests/integration/editais/test_mutabilidade_do_metodo_de_sorteio.py` o teste de fronteira
  que falha: Retificação sobre método **não** alcança relação congelada nem sorteio realizado
  (FR-309, SC-100). A garantia já é estrutural — `backend/processo_seletivo/sorteios/models.py:48`
  grava `metodo_hash` no congelamento e `models.py:213` o copia e confere no `Sorteio`. **O teste
  declara a fronteira; ele não a constrói.**
- [ ] T057 [US4] Escrever em `backend/tests/interface/test_retificar_metodo_de_sorteio.py` o teste
  que falha: os dez campos são oferecidos, e a conferência exibe cada um em português.
- [ ] T058 [US4] Acrescentar a apresentação dos cinco escalares em
  `backend/processo_seletivo/interface/retificacao.py`: `drawMethod/algorithm`, `/source`,
  `/occurrence`, `/occurrenceAt` (`INSTANTE`) e `/derivation`.
- [ ] T059 [US4] Acrescentar `drawMethod/qualifyingStageId` como `REFERENCIA` em
  `backend/processo_seletivo/interface/retificacao.py` — é identidade de Etapa do próprio marco, e
  UUID digitado à mão mudaria em silêncio qual Etapa habilita.
- [ ] T060 [US4] Acrescentar os dois pares aninhados em
  `backend/processo_seletivo/interface/retificacao.py`: `drawMethod/normalization/rule` e `/text`,
  `drawMethod/substitutionRule/rule` e `/text`. `rule` é o identificador que a máquina aplica e o
  terceiro reimplementa; `text` é a frase que a pessoa lê — e
  `backend/processo_seletivo/editais/domain/perfis.py:283` cobra as duas chaves de cada um. Com
  T058 e T059, fecham os dez.
- [ ] T061 [US4] Fazer a Retificação recusar método declarado pela metade, reusando
  `_validar_metodo_de_sorteio` em `backend/processo_seletivo/editais/domain/perfis.py:258` —
  inclusive `_validar_algoritmo_publicado`, `_validar_fonte_publicada` e `_validar_regra_publicada`.
- [ ] T062 [US4] Renderizar o bloco do método em
  `backend/processo_seletivo/interface/templates/interface/_retificacao_marco.html`.
- [ ] T063 [US4] Verificar que a tela do sorteio deixou de contradizer-se: ela manda retificar o
  método, e agora a Retificação o oferece. Localizar o texto em
  `backend/processo_seletivo/interface/templates/interface/` e ajustá-lo se continuar apontando
  para caminho que não existe.
- [ ] T064 [US4] Percorrer a jornada 4 do [quickstart.md](quickstart.md) pelo navegador, incluindo
  a verificação pública de um sorteio já realizado sob o método anterior.

---

## Phase 10: Polish & Cross-Cutting

- [ ] T065 [P] Revisar as razões de
  `backend/processo_seletivo/editais/domain/mutabilidade.py` contra a amostra real de Editais
  (`~/Downloads`, com `pdftotext -layout`): campo que nenhum Edital da amostra jamais corrigiu é
  candidato legítimo a "não retificável"; campo que a amostra corrige e o contrato exclui é erro de
  classificação.
- [ ] T066 [P] Registrar em `doc/decisao-mutabilidade-normativa.md` que o invariante passou a ser
  verificado por teste, com o caminho do guardião — e que o quarto canário foi trocado, conforme
  D-010.
- [ ] T067 [P] Registrar como limite conhecido, em comentário no topo de
  `backend/processo_seletivo/editais/domain/mutabilidade.py`, que a **forma** das seis coleções
  aninhadas continua não declarada em `backend/processo_seletivo/editais/domain/validation.py`
  (015, T-009), e que a enumeração não depende dela (FR-300).
- [ ] T068 Rodar `cd backend && make lint check test-pg`. `lint` são dois passos — `ruff check`
  **e** `ruff format --check` —, e `test-pg` e não `test`.
- [ ] T069 Rodar `backend/tests/test_citacoes_de_requisito.py`: esta feature escreve `specs/`, e a
  varredura derruba o CI quando uma citação aponta identificador que nenhuma spec define.

---

## Dependencies

```text
⛔ matriz.md aprovada
   └─> Setup (T001–T004)
          └─> Foundational (T005–T014)
                 └─> US5 (T015–T026)       ← MVP técnico
                        └─> FR-298/314 (T027–T032)   ← a tela passa a ler o contrato
                               └─> US1 (T033–T038)   ← conclui a spec pelo princípio VI
                                      └─> US2 (T039–T044)
                                             └─> US3 (T045–T051)
                                                    └─> US6 (T052–T055)
                                                           └─> US4 (T056–T064)
                                                                  └─> Polish (T065–T069)
```

**As histórias não são paralelizáveis, e a afirmação contrária na versão anterior deste arquivo
estava errada.** US1, US2, US3, US4 e US6 tocam todas `interface/retificacao.py` e os templates de
Retificação. Quatro sessões simultâneas produziriam conflito em cada merge.

**A fase 4 é o que torna a sequência barata.** Depois que a tela deriva do contrato quais campos
existem, cada história acrescenta **apresentação** — uma linha indexada por `(coleção, caminho)` —
em vez de mexer na estrutura de montagem. O conflito que sobra é textual e local.

**Ownership de arquivo**, para quem executar em sessões distintas mesmo assim:

| Arquivo | Dono |
|---|---|
| `editais/domain/mutabilidade.py` | US5, depois fase 4 |
| `tests/contract/test_mutabilidade.py` | Foundational, depois US5 |
| `interface/retificacao.py` | fase 4; depois uma história por vez |
| `templates/interface/_retificacao_marco.html` | US3, depois US4 |
| `templates/interface/_retificacao_perfil.html` | US2 |
| `editais/domain/validation.py` | US1, e só ela |

## Parallel Execution

Pouca, e declarada honestamente:

- **Fase 1**: T004 em paralelo com T001–T003.
- **Fase 2**: T011–T013 (`mutabilidade.py`) em paralelo com T005–T010
  (`test_mutabilidade.py`) — arquivos distintos. T014 depois de T012.
- **Fase 3**: T018, T019 e T020 tocam o mesmo arquivo e **não** paralelizam.
- **Fase 10**: T065, T066 e T067 em paralelo.

Quando houver mais de uma sessão, **`DB_NAME` próprio em cada uma** — suítes paralelas disputam
`test_processo_seletivo` e se derrubam com erros que não têm nada a ver com a feature.

## Implementation Strategy

**MVP técnico**: fases 1 a 3 (T001–T026). O contrato existe e o guardião falha por omissão. É o que
a spec estrutural de vagas precisa que exista antes de começar.

**MVP entregável**: mais as fases 4 e 5 (T027–T038). O princípio VI é explícito: capacidade que
nenhuma interface alcança não é entregue. A US1 é a jornada mais barata que fecha a exigência — e o
campo dela, `location`, é o achado que a própria feature descobriu no seu canário mais simples.

**Incremento seguinte**: US2 e US3 fecham as três correções P1. US6 e US4 completam o conjunto.
