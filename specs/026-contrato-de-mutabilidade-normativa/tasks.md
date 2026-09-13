---

description: "Tarefas de implementação — contrato de mutabilidade normativa"
---

# Tasks: Contrato de mutabilidade normativa

**Input**: artefatos de desenho em `specs/026-contrato-de-mutabilidade-normativa/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/mutabilidade.md](contracts/mutabilidade.md),
[quickstart.md](quickstart.md)

**Tests**: obrigatórios, e não opcionais. O entregável central **é** um teste — o guardião — e as
seis histórias têm critério de aceitação verificável. O princípio V da Constituição faz da
rastreabilidade requisito, não preferência.

**Organization**: uma fase por história, na ordem em que cada uma passa a valer sozinha.

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
  máximo**: `classificationMilestones` com ao menos um marco declarado (com `stages`, `operation`,
  `rounding`, `cutRule`, `tiebreakers`, `appealWindow` e `drawMethod` completos), `vacancyReversion`
  declarado, `callForm` declarado, e `location` preenchido em ao menos um Evento. **É a tarefa mais
  importante da fase 1**: hoje o rascunho traz `classificationMilestones: []`,
  `vacancyReversion: None` e `callForm: None` (linhas 110, 121 e 125), e uma travessia sobre ele
  não encontraria nenhum dos dez campos do método do sorteio — que são dez dos vinte e três sem
  decisão. Enumerar sobre um Edital pobre produz guardião silenciosamente incompleto, que é o mesmo
  defeito que a feature existe para fechar.
- [ ] T002 [P] Verificar que o Edital máximo de T001 **publica**: rodar
  `backend/tests/contract/test_forma_publicada.py` inteiro. Se a publicação recusar, o rascunho
  novo viola alguma coerência do domínio, e é ela que precisa ser satisfeita — não contornada com
  um rascunho menor.
- [ ] T003 [P] Acrescentar a entrada `mutabilidade-026` ao `.claude/launch.json` — **acrescentar**,
  sem reescrever o arquivo, que é versionado e carrega entradas de outras sessões. Porta 8026,
  `DB_NAME=ps_demo_026`, `INTERFACE_SELETOR_IDENTIDADE=true`, `PORTAL_IDENTIDADE_DEMO=true`, e
  `localhost` na `url`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: a enumeração e a forma do contrato. Tudo o que vem depois lê daqui.

**⚠️ CRITICAL**: nenhuma história começa antes de esta fase fechar.

- [ ] T004 Escrever a travessia recursiva do conteúdo canônico em
  `backend/tests/contract/test_mutabilidade.py`: a partir do `content` da `VersaoConsolidada` de um
  Edital publicado, descer por listas de entidades e objetos aninhados até o campo escalar,
  devolvendo pares `(coleção, campo)`. Campo aninhado — `cutRule/targetCount`,
  `normativeRule/percentage` — entra pelo **último segmento**, e pertence à coleção da entidade que
  o carrega, conforme [data-model.md](data-model.md).
- [ ] T005 Escrever um teste que fixe o alcance da travessia: ela precisa encontrar as **doze**
  coleções da tabela de [data-model.md](data-model.md) — seis na raiz, `competitionModalities`,
  `vacancyTable`, `declaredFacts`, `classificationMilestones`, `tiebreakers`, e os campos soltos da
  raiz. Falhar aqui é o sintoma de o Edital de T001 não ser máximo.
- [ ] T006 Criar `backend/processo_seletivo/editais/domain/mutabilidade.py` com `Natureza`
  (`StrEnum` de quatro valores), `Mutabilidade` (dataclass congelada com `natureza` e `razao`) e
  `CONTRATO: dict[tuple[str, str], Mutabilidade]` ainda vazio. Chave `(coleção, campo)` e nunca o
  nome sozinho — `name` existe em cinco coleções e `order` em três, e é a colisão que o PR #113 já
  pagou no rótulo em português.
- [ ] T007 Implementar em `mutabilidade.py` a validação na **carga do módulo**:
  `NAO_RETIFICAVEL` sem razão e qualquer outra natureza **com** razão levantam na importação, e não
  na execução de um teste. Quem escreve o contrato descobre no `import` (FR-299).
- [ ] T008 Implementar `natureza_de(colecao, campo) -> Mutabilidade` em `mutabilidade.py`,
  levantando `KeyError` para par não declarado. **Sem valor padrão**: um padrão é a decisão
  implícita que D-008 proíbe, e seria o estado de hoje com outro nome.
- [ ] T009 [P] Escrever em `backend/tests/contract/test_mutabilidade.py` o teste que prova T007 —
  construir `Mutabilidade(NAO_RETIFICAVEL)` sem razão falha, e `Mutabilidade(RETIFICAVEL, "…")`
  também.

**Checkpoint**: a travessia enumera, o módulo carrega, e o contrato está vazio de propósito.

---

## Phase 3: User Story 5 — Um campo novo sem decisão quebra a suíte (P1) 🎯 MVP

**Goal**: nenhum campo do conteúdo publicado existe sem natureza declarada, e o vigésimo quarto
campo não nasce sem decisão como `maximumScore` nasceu na 012.

**Independent Test**: acrescentar um campo ao conteúdo publicado sem tocar em `mutabilidade.py`; a
suíte falha **nomeando o campo e o caminho**. Desfazer, e a suíte volta ao verde.

- [ ] T010 [US5] Escrever o guardião em `backend/tests/contract/test_mutabilidade.py`, direção
  snapshot → contrato: todo `(coleção, campo)` que a travessia encontra tem entrada em `CONTRATO`,
  e a falha **nomeia o campo, a coleção e o caminho onde ele apareceu** (FR-301). Uma mensagem que
  diga só "divergência" não atende — quem quebrou a suíte precisa ler qual decisão faltou.
- [ ] T011 [US5] Escrever o guardião na direção contrato → snapshot: toda entrada de `CONTRATO`
  corresponde a campo que a travessia encontra (FR-302). Declarar natureza para campo inexistente é
  a mesma omissão ao contrário.
- [ ] T012 [US5] Escrever o teste de que toda `NAO_RETIFICAVEL` do `CONTRATO` carrega razão não
  vazia (FR-299, SC-101). O teste confere a presença; se a razão é normativa ou técnica é leitura
  humana, e é o trabalho de T019.
- [ ] T013 [US5] Classificar em `mutabilidade.py` as **seis coleções-raiz** — `profiles`,
  `schedule`, `stages`, `sections`, `attachments`, `documentRequirements` — mais os campos soltos
  da raiz (`title`, `description`, `maxInscricoesPorCandidato`). Nominalmente, campo a campo
  (D-008), sem inferência por nome, tipo ou coleção.
- [ ] T014 [US5] Classificar as coleções sob `profiles`: `competitionModalities`, `vacancyTable`,
  `declaredFacts` e os campos escalares de `classificationMilestones`.
- [ ] T015 [US5] Classificar os objetos aninhados do marco — `cutRule`, `rounding`, `appealWindow`,
  `drawMethod`, `normativeRule`, `vacancyReversion` — e a coleção `tiebreakers`. É onde moram dez
  dos vinte e três campos sem decisão do Edital 26/2026.
- [ ] T016 [US5] Absorver `NAO_SAO_NORMA` de `backend/tests/contract/test_retificacoes_api.py:89`
  no contrato: `id` e `order` viram `ESTRUTURAL`, e `scheduleEventId` recebe natureza com razão
  escrita. O literal local deixa de existir; o que era exclusão sem nome passa a ser natureza
  nomeada.
- [ ] T017 [US5] Reescrever
  `test_a_retificacao_alcanca_todo_campo_normativo_da_etapa` em
  `backend/tests/contract/test_retificacoes_api.py` para ler o contrato em vez de `NAO_SAO_NORMA`.
  Ele cobre **uma** coleção entre doze e continua valendo — o guardião novo o generaliza, não o
  substitui por outro mecanismo.
- [ ] T018 [US5] Escrever o teste que prova o Independent Test da história: com um campo
  experimental no conteúdo publicado e sem entrada no contrato, o guardião falha com mensagem que
  **cita o nome do campo** (SC-096). O teste afirma sobre a mensagem, e não só sobre o fato de
  falhar.
- [ ] T019 [US5] Reexaminar toda exclusão cuja razão registrada é técnica (FR-310), uma a uma, e
  reclassificar ou reescrever a razão em termos normativos. As candidatas estão nomeadas nos
  comentários de `backend/processo_seletivo/interface/retificacao.py`: `stages` e `operation` do
  marco (linha 104), `targetKind`, a Etapa governada e a política de continuação do corte
  (linha 117), `whenMissing` do critério de desempate, `reserveType` e o arredondamento. Razão que
  descreva limitação de implementação — "publicaria valor que o cálculo não interpreta" — reprova:
  ela deixa de valer quando a limitação some, e ninguém percebe.
- [ ] T020 [US5] Declarar em `mutabilidade.py`, para cada objeto normativo que pode estar ausente
  do conteúdo (`cutRule: None`, `drawMethod: None`, `appealWindow: None`, `vacancyReversion: None`,
  `callForm: None`), se a declaração pode passar a existir por Retificação e por qual caminho
  (FR-313). Ausência de objeto não é campo sem natureza: é declaração que não foi feita.
- [ ] T021 [US5] Rodar `cd backend && make lint check test-pg` e confirmar **zero campos sem
  natureza** (SC-095).

**Checkpoint**: o contrato existe, o guardião o guarda, e a suíte fecha verde. É o MVP técnico —
mas **não conclui a spec**: o princípio VI exige jornada pelo canal do ator, e a primeira é a US1.

---

## Phase 4: User Story 1 — Corrigir o local de uma prova publicada (P1)

**Goal**: o local de um Evento publicado se corrige pela tela de Retificação.

**Independent Test**: publicar um Edital com local declarado, retificá-lo pela interface, e
verificar o Cronograma público e a versão anterior.

- [ ] T022 [US1] Declarar `location` em `EVENTO_PUBLICADO`, em
  `backend/processo_seletivo/editais/domain/validation.py`. **O campo é emitido no conteúdo
  publicado por `backend/processo_seletivo/publicacoes/application/publish_edital.py:261` e não
  está declarado** — nenhum teste acusa, porque o guardião de hoje confere coleções e não campos.
  Cuidado com a nulabilidade: `editais/models/cronograma.py:50` o define como `CharField(blank=True,
  default="")`, e `shared/canonical.py:97` registra que **vazio significa "não declarado"** — logo
  `Campo("location", str)` sem `admite_nulo`, como `duties` e `workload` já são.
- [ ] T023 [US1] Acrescentar `("location", "Local", TEXTO)` a `CAMPOS_EVENTO` em
  `backend/processo_seletivo/interface/retificacao.py:80`.
- [ ] T024 [US1] Escrever o teste de integração em
  `backend/tests/integration/editais/test_mutabilidade_do_local.py`: Retificação que altera o local
  de um Evento publicado vigora, e a versão consolidada anterior continua legível com o local
  antigo.
- [ ] T025 [US1] Escrever o teste de interface em
  `backend/tests/interface/test_retificar_cronograma.py`: a tela oferece o campo, a conferência o
  exibe **em português** ("Local"), e a publicação passa a vigorar com o valor novo (SC-097).
  `publicacoes/domain/alteracoes.py:63` já traduz `location` como "Local" — conferir que o caminho
  de conferência realmente passa por ali.
- [ ] T026 [US1] Resolver o segundo cenário de aceitação: Evento **sem** local declarado que recebe
  um por Retificação. O contrato precisa dizer se o acréscimo é admitido, e a tela precisa dizer
  qual dos dois é. Com `location` sempre presente como `""`, isto é alteração de valor e não
  acréscimo de campo — registrar a conclusão como comentário na entrada `("schedule", "location")`
  de `backend/processo_seletivo/editais/domain/mutabilidade.py`.
- [ ] T027 [US1] Percorrer a jornada 1 do [quickstart.md](quickstart.md) pelo navegador, com o
  servidor da entrada `mutabilidade-026`. Teste verde sobre objeto falso não é jornada — foi
  exatamente o que deixou passar o `AttributeError` do PR #113.

**Checkpoint**: a primeira correção administrativa que hoje só se faz por API passou a se fazer
pela tela. **A spec já é concluível a partir daqui** pelo princípio VI.

---

## Phase 5: User Story 2 — Corrigir um requisito de participação publicado (P1)

**Goal**: a lista de requisitos de um Perfil publicado se corrige pela tela.

**Independent Test**: publicar, retificar a lista, conferir a página pública e o acompanhamento de
uma inscrição anterior à Retificação.

- [ ] T028 [US2] Decidir e registrar em `mutabilidade.py` **como** `requirements` se retifica:
  substituição da lista inteira ou endereçamento de item. Item de lista de texto não tem identidade
  estável, e "o terceiro requisito" não é endereçar — é contar. A decisão muda o que o ato registra
  e precisa estar escrita antes do código.
- [ ] T029 [US2] Implementar o campo em `backend/processo_seletivo/interface/retificacao.py`,
  conforme T028. `CAMPOS_PERFIL` (linha 51) hospeda os escalares; uma coleção de texto precisa de
  tratamento próprio — ver `CAMPOS_DA_LINHA` e o mecanismo de `LISTA` (linha 212) como precedente
  mais próximo.
- [ ] T030 [US2] Renderizar o campo em
  `backend/processo_seletivo/interface/templates/interface/_retificacao_perfil.html`.
- [ ] T031 [US2] Escrever o teste de interface em
  `backend/tests/interface/test_retificar_requisitos.py`: a tela oferece a correção, e a
  conferência **nomeia o Perfil e o requisito alterado, sem caminho normativo em primeiro plano**.
- [ ] T032 [US2] Escrever o teste de integração em
  `backend/tests/integration/editais/test_mutabilidade_dos_requisitos.py`: a página pública exibe a
  lista corrigida e o comprovante da inscrição anterior continua apontando a versão aceita
  (SC-098).
- [ ] T033 [US2] Percorrer a jornada 2 do [quickstart.md](quickstart.md) pelo navegador.

---

## Phase 6: User Story 3 — Corrigir o prazo recursal publicado (P1)

**Goal**: a janela recursal declarada no marco se corrige pela tela, com a unidade como escolha.

**Independent Test**: publicar um resultado, retificar o prazo, e verificar o que a tela de recurso
do candidato passa a dizer.

- [ ] T034 [US3] Acrescentar os três campos da janela em
  `backend/processo_seletivo/interface/retificacao.py`: `appealWindow/admits` (`BOOLEANO`),
  `appealWindow/durationDays` (`INTEIRO`) e `appealWindow/unit` — este **como escolha**, nunca como
  texto livre (FR-311). Hoje a lista fechada tem um valor só, `DIAS_CORRIDOS`, e
  `editais/domain/perfis.py:475` diz por quê: dias úteis exigiriam o calendário de dias sem
  expediente, que o Edital não publica.
- [ ] T035 [US3] Fazer a Retificação recusar a contradição pelo mesmo critério da elaboração: marco
  que declara não admitir recurso não tem duração a declarar, e duração precisa ser inteiro maior
  que zero. `_validar_janela_recursal` em `backend/processo_seletivo/editais/domain/perfis.py:460`
  é a regra — reusá-la, e não reescrevê-la na interface.
- [ ] T036 [US3] Renderizar o bloco da janela no template do marco em
  `backend/processo_seletivo/interface/templates/interface/`, junto dos demais campos do marco.
- [ ] T037 [US3] Escrever o teste de fronteira em
  `backend/tests/integration/editais/test_mutabilidade_da_janela_recursal.py`: a janela nova vale
  para o que vier, e **a janela gravada num recurso já interposto permanece intacta**.
- [ ] T038 [US3] Escrever o teste de interface em
  `backend/tests/interface/test_retificar_janela_recursal.py`: unidade que o cálculo não interpreta
  é recusada **com a razão**, e não gravada.
- [ ] T039 [US3] Escrever o teste do portal: depois da vigência, o candidato lê a data-limite
  recalculada a partir da divulgação do resultado (SC-099).
- [ ] T040 [US3] Percorrer a jornada 3 do [quickstart.md](quickstart.md) pelo navegador, incluindo
  a tela de recurso do candidato — que exige `PORTAL_IDENTIDADE_DEMO=true`.

**Checkpoint**: os três canários P1 fecharam. O desenho já atravessou escalar, coleção de texto e
objeto composto com valor fechado — que é o que a US4 precisava esperar.

---

## Phase 7: User Story 6 — A tela diz o que não alcança (P2)

**Goal**: ausência deliberada deixa de parecer defeito.

**Independent Test**: abrir a Retificação de um Edital com marco declarado e verificar que o bloco
do marco nomeia o que não se corrige ali e por quê.

- [ ] T041 [US6] Expor em `backend/processo_seletivo/interface/retificacao.py` a leitura das
  exclusões de uma coleção: para `(coleção)`, os campos `NAO_RETIFICAVEL` com as respectivas
  razões, vindas de `mutabilidade.py`.
- [ ] T042 [US6] Renderizar a declaração **uma vez por bloco de coleção**, e não sob cada campo, em
  `backend/processo_seletivo/interface/templates/interface/retificar.html`. Explicação que não muda
  de um cartão para o outro não se imprime uma vez por cartão — é a decisão que
  `backend/tests/interface/test_medida_dos_campos.py` já guarda no assistente, e foi ela que
  reprovou a primeira tentativa no PR #113.
- [ ] T043 [US6] Escrever o teste de interface em
  `backend/tests/interface/test_retificar_exclusoes.py`: o bloco do marco declara quais campos não
  se corrigem ali e a razão normativa de cada um (SC-102), e a mesma razão não aparece duas vezes
  no mesmo bloco.
- [ ] T044 [US6] Percorrer a verificação 3 do [quickstart.md](quickstart.md) pelo navegador.

---

## Phase 8: User Story 4 — Corrigir o método do sorteio publicado (P2)

**Goal**: os dez campos do método se corrigem pela tela, e a relação congelada não é alcançada.

**Independent Test**: publicar um Edital de sorteio, retificar a ocorrência antes do congelamento
da relação, e verificar o que a tela do sorteio e a verificação pública passam a exibir.

**Nota de prioridade**: R-005 mostrou que metade da justificativa de P2 caiu —
`RelacaoDeHabilitados.metodo_hash` já garante FR-309 estruturalmente, e não há trabalho de domínio
a fazer. A outra metade continua de pé e é o que mantém a história aqui: são dez campos com
interdependência, e o desenho precisava dos três primeiros canários antes de enfrentá-los.

- [ ] T045 [US4] Acrescentar os cinco escalares do método em
  `backend/processo_seletivo/interface/retificacao.py`: `drawMethod/algorithm`, `/source`,
  `/occurrence`, `/occurrenceAt` (`INSTANTE`) e `/derivation`.
- [ ] T046 [US4] Acrescentar `drawMethod/qualifyingStageId` como `REFERENCIA` — é identidade de
  Etapa do próprio marco, e digitar UUID à mão faria um erro de digitação mudar em silêncio qual
  Etapa habilita.
- [ ] T047 [US4] Acrescentar os dois pares aninhados: `normalization/rule` + `normalization/text` e
  `substitutionRule/rule` + `substitutionRule/text`. `rule` é o identificador que a máquina aplica
  e o terceiro reimplementa; `text` é a frase publicada que a pessoa lê — e
  `editais/domain/perfis.py:283` cobra as duas chaves de cada um. Com T045 e T046, fecham os dez.
- [ ] T048 [US4] Fazer a Retificação recusar método declarado pela metade, reusando
  `_validar_metodo_de_sorteio` em `backend/processo_seletivo/editais/domain/perfis.py:258` —
  inclusive `_validar_algoritmo_publicado`, `_validar_fonte_publicada` e
  `_validar_regra_publicada`, que já conferem cada valor contra o que o motor executa.
- [ ] T049 [US4] Renderizar o bloco do método no template do marco.
- [ ] T050 [US4] Escrever o teste de fronteira em
  `backend/tests/integration/editais/test_mutabilidade_do_metodo_de_sorteio.py`: Retificação sobre
  método **não** alcança relação congelada nem sorteio realizado (FR-309, SC-100). A garantia já é
  estrutural — `backend/processo_seletivo/sorteios/models.py:48` grava `metodo_hash` no
  congelamento e `models.py:213` o copia e confere no `Sorteio`, e a relação congelada não relê o
  método vigente. **O teste declara a fronteira; ele não a constrói.**
- [ ] T051 [US4] Escrever o teste de interface em
  `backend/tests/interface/test_retificar_metodo_de_sorteio.py`: os dez campos são oferecidos, e a
  conferência exibe cada um em português.
- [ ] T052 [US4] Verificar que a tela do sorteio deixou de contradizer-se: ela manda retificar o
  método, e agora a Retificação o oferece. Localizar o texto em
  `backend/processo_seletivo/interface/templates/interface/` e ajustá-lo se ele continuar apontando
  para caminho que não existe.
- [ ] T053 [US4] Percorrer a jornada 4 do [quickstart.md](quickstart.md) pelo navegador, incluindo
  a verificação pública de um sorteio já realizado sob o método anterior.

---

## Phase 9: Polish & Cross-Cutting

- [ ] T054 Escrever o teste que prova FR-304 de forma geral: todo campo `RETIFICAVEL` do contrato é
  oferecido pela tela de Retificação. É o guardião da direção que falta — hoje ele vale só para a
  Etapa, por `test_retificacoes_api.py`.
- [ ] T055 [P] Revisar as razões escritas em `mutabilidade.py` uma última vez contra a amostra real
  de Editais (`~/Downloads`, com `pdftotext -layout`): um campo que nenhum Edital da amostra jamais
  corrigiu é candidato legítimo a "não retificável"; um que a amostra corrige e o contrato exclui é
  erro de classificação.
- [ ] T056 [P] Registrar em `doc/decisao-mutabilidade-normativa.md` que o invariante passou a ser
  verificado por teste, com o caminho do guardião.
- [ ] T057 [P] Registrar como limite conhecido — em comentário no topo de `mutabilidade.py` — que a
  **forma** das seis coleções aninhadas continua não declarada em `validation.py` (015, T-009), e
  que a enumeração não depende dela (FR-300).
- [ ] T058 Rodar `cd backend && make lint check test-pg` e confirmar a suíte inteira verde. `lint`
  são dois passos — `ruff check` **e** `ruff format --check` —, e `test-pg` e não `test`.
- [ ] T059 Rodar `backend/tests/test_citacoes_de_requisito.py`: esta feature escreve `specs/`, e a
  varredura derruba o CI quando uma citação aponta identificador que nenhuma spec define.

---

## Dependencies

```text
Setup (T001–T003)
   └─> Foundational (T004–T009)
          └─> US5 (T010–T021)  ← MVP técnico; sem ele não há contrato a ler
                 ├─> US1 (T022–T027)  ← primeira jornada; conclui a spec pelo princípio VI
                 ├─> US2 (T028–T033)
                 ├─> US3 (T034–T040)
                 ├─> US6 (T041–T044)
                 └─> US4 (T045–T053)   ← depois de US1, US2 e US3, por desenho
                        └─> Polish (T054–T059)
```

**T001 bloqueia tudo.** Um Edital que não declara marco, reversão nem local faz a travessia
enumerar um subconjunto, e o guardião nasce incompleto sem que nada acuse.

**US1, US2, US3 e US6 são independentes entre si** depois da US5 — arquivos distintos, campos
distintos, testes distintos.

**US4 depende das três primeiras por desenho, e não por arquivo.** É o que a própria spec dá como
razão de a história ser P2, e é a metade da justificativa que R-005 não derrubou.

## Parallel Execution

- **Fase 1**: T002 e T003 em paralelo, depois de T001.
- **Fase 2**: T006–T008 (`mutabilidade.py`) em paralelo com T004–T005 (`test_mutabilidade.py`) —
  são arquivos distintos. T009 fica por último: ele escreve no mesmo arquivo de T004.
- **Fase 3**: T013, T014 e T015 tocam o mesmo arquivo e **não** paralelizam; T019 pode correr em
  paralelo com elas, porque é leitura e escrita de razão, não de estrutura.
- **Fases 4 a 7**: as quatro histórias correm em paralelo entre si, uma por sessão. Cada uma com
  **`DB_NAME` próprio** — suítes paralelas disputam `test_processo_seletivo` e se derrubam com
  erros que não têm nada a ver com a feature.
- **Fase 9**: T055, T056 e T057 em paralelo.

## Implementation Strategy

**MVP técnico**: fases 1 a 3 (T001–T021). O contrato existe, o guardião falha por omissão, e
nenhum campo novo nasce sem decisão. É o que impede a regressão estrutural — e é o que a spec
estrutural de vagas precisa que exista antes de começar.

**MVP entregável**: MVP técnico **mais a US1** (T022–T027). O princípio VI é explícito: capacidade
que nenhuma interface alcança não é entregue, e demonstrar por chamada manual não satisfaz. A US1 é
a jornada mais barata que fecha essa exigência — e o campo dela, `location`, é o achado que a
própria feature descobriu no seu canário mais simples.

**Incremento seguinte**: US2 e US3 fecham as três correções administrativas P1. US6 e US4 completam
o conjunto.
