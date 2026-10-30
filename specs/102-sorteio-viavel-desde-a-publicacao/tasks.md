# Tasks: Sorteio viável desde a publicação

**Input**: Design documents from `specs/102-sorteio-viavel-desde-a-publicacao/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/mensagens.md](contracts/mensagens.md),
[quickstart.md](quickstart.md)

**Tests**: pedidos pela spec. A matriz da SC-954 sem falso positivo nem falso negativo, a comparação
da constituição inalterada (FR-2664, SC-957) e a coerência entre a granularidade declarada e o
adaptador (FR-2649) são requisitos. Cada teste é escrito antes do código que ele cobre, e precisa
falhar antes de passar.

**Organization**: a Fase 2 é a base de tudo: granularidade das fontes e regra pura, sem tela. A US1
(publicação e Retificação) e a US2 (tela do sorteio) dependem só dela, e podem correr em paralelo
porque não tocam os mesmos arquivos. A US3 (recusa) depende só da Fase 2. A US4 (demonstração)
depende da Fase 2 para a fonte, e da US2 e da US3 para o roteiro.

**29/10/2026, a implementação** (T001 a T027, nesta worktree). `make lint check test-pg` com 4
workers: **13255 passando, 13 pulados, nenhuma falha**, em 577s. A medição anterior desta mesma
árvore deu 2 falhas, ambas da `102`: `advertencias_do_ato` passou a ler os marcos sorteados em toda
confirmação, e o teste unitário da subtração, sem banco, acusou. Agora o seletor só roda quando a
advertência da extração inviável aparece. **O que mudou em relação ao planejado:**

- **O diagnóstico da relação congelada é bloco próprio, e não ramo da cadeia de botões** (T018):
  como ramo, ele escondia "Realizar o sorteio", o que a spec não pede.
- **A demonstração "congelar ontem" virou "sortear amanhã"** (T021): o Edital da suíte só vigora
  desde hoje, e congelar com o relógio de ontem recusava por falta de versão vigente.
- **A Retificação lê os marcos sorteados só quando precisa** (T013), pelo motivo acima.
- **O PR #335 passou a trazer a lacuna 2**, na mesma mensagem que a T020 estende. O conflito fica no
  fim da recusa: a primeira frase vem do #335, e o acréscimo vem daqui.

**Convenções**: textos e nomes em português; comentário explica por quê; nada de `style=`, `<style>`,
`<script>` nem `onclick=` em template; `ruff check` **e** `ruff format --check`. A verificação é
`cd backend && make lint check test-pg`, com `DB_NAME` próprio desta worktree.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente)
- **[Story]**: a história da spec que a tarefa serve (US1 a US4)

---

## Phase 1: Setup

- [X] T001 Preparar a worktree: `uv sync --extra dev` em `backend/`, `backend/.env` a partir de
  `backend/.env.example` com `DB_NAME=ps_102`, e `make preparar` (três passos; conferir que o
  `provisionar` informa `41 de 41` e não `0 de 41`). Rodar
  `PYTEST_ADDOPTS="tests/integration/sorteios" make test-pg` e anotar o total de passando como
  linha de base da SC-957.

---

## Phase 2: Foundational (bloqueia todas as histórias)

**Purpose**: a granularidade declarada por fonte (FR-2647–FR-2649), a segunda fonte de demonstração
(FR-2665, FR-2666) e a regra pura do limite previsto (FR-2650, FR-2651).

- [X] T002 [P] Escrever `backend/tests/unit/sorteios/test_viabilidade.py`, só com a regra pura (sem
  banco). Casos:
  - a matriz da SC-954: para "só a data", a extração no dia anterior ao fim, no mesmo dia antes do
    fim, no mesmo dia depois do fim, às 00h00 do dia seguinte e às 20h05 do dia seguinte. Inviável
    exatamente nos três primeiros;
  - para "data e hora", nenhum limite previsto;
  - `occurrenceAt` com deslocamento `-02:00` e `+00:00` que muda o dia no fuso institucional;
  - `occurrenceAt` ilegível ou sem fuso, que dá nenhum limite;
  - a borda: limite igual ao congelamento é inviável, e limite um microssegundo depois é viável.
- [X] T003 Criar `backend/processo_seletivo/sorteios/domain/viabilidade.py` com duas funções puras: o
  limite previsto (recebe o texto de `occurrenceAt` e se a fonte publica só a data, e devolve
  00h00 do dia em `ZONA` ou `None`) e a inviabilidade (limite e instante mais cedo de congelamento;
  `None` em qualquer um dá falso). Usar `shared.tempo.ZONA` e a mesma forma de
  `loteria_federal._nao_antes_de` (`datetime.combine(dia, time.min)`). Docstring com o porquê: a
  regra é uma só para quatro lugares (FR-2650). Sem import de `sorteios.infrastructure`. T002 verde.
- [X] T004 [P] Escrever `backend/tests/integration/sorteios/test_granularidade_das_fontes.py`. Casos:
  - para cada nome de `fontes_publicadas()`, a granularidade declarada bate com o `observar` do
    adaptador. Para a Loteria Federal, substituir `request.urlopen` por uma resposta com
    `dataApuracao: "28/10/2026"`: o limite é meia-noite exatamente quando a fonte se declara "só a
    data" (FR-2649);
  - `Fonte de demonstração (só a data)` devolve o material fixo da atual e o início do dia corrente
    no fuso institucional;
  - a função por nome responde `None` para nome fora do vocabulário;
  - em produção (`override_settings(SORTEIO_FONTE_DE_DEMONSTRACAO=False)`) o vocabulário continua
    `{"Loteria Federal"}`, como em `test_fonte_fora_de_producao.py` (FR-2666).
- [X] T005 Em `backend/processo_seletivo/sorteios/infrastructure/fontes/loteria_federal.py`:
  - atributo de classe de granularidade em `FonteExterna` (padrão: data e hora), em `LoteriaFederal`
    (só a data) e em `FonteDeTeste` (data e hora, explícito);
  - classe nova `FonteDeTesteSoData(FonteDeTeste)`, com o mesmo material e o limite inferior no
    início do dia corrente em `ZONA`.

  O docstring diz por que ela existe (D-007) e que, por construção, um congelamento feito hoje é
  sempre recusado com ela.
- [X] T006 Em `backend/processo_seletivo/sorteios/infrastructure/fontes/__init__.py`:
  - `FONTE_DE_DEMONSTRACAO` vira uma tupla de dois pares, a atual e
    `("Fonte de demonstração (só a data)", ".../loteria_federal.FonteDeTesteSoData")`, e
    `fontes_publicadas` acrescenta as duas sob a mesma chave;
  - nova função `publica_so_a_data(nome)`, que devolve `True`, `False` ou `None` para nome fora do
    vocabulário, e importa a classe com `import_string` sem instanciá-la (R-001). Exportar em
    `__all__`.

  Ajustar `backend/tests/integration/sorteios/test_fonte_fora_de_producao.py` só se ele desmontar o
  par antigo. T004 verde.
- [X] T007 Rodar `PYTEST_ADDOPTS="tests/integration/sorteios tests/interface/test_metodo_do_marco.py tests/interface/test_retificar_metodo_de_sorteio.py" make test-pg`.
  Esperado: nenhuma fixture alterada, e o mesmo total de T001 mais os casos novos (SC-957, D-006).

**Checkpoint**: a regra e as fontes estão prontas. As histórias podem começar.

---

## Phase 3: User Story 1 — A publicação é impedida, e a Retificação adverte (Priority: P1) 🎯 MVP

**Goal**: o Edital com a extração inviável não publica, e a Retificação o adverte (FR-2652–FR-2657).

**Independent Test**: o Edital 72/2026 reproduzido tem a publicação impedida; com a extração em
29/10, publica (SC-955).

### Tests for User Story 1

- [X] T008 [P] [US1] Escrever `backend/tests/unit/editais/test_extracao_inviavel.py` sobre
  `validate_for_publication`, com snapshots montados à mão. Casos:
  - o código `draw_occurrence_not_after_registration` com `BLOCKING_ERROR` no ato de publicação;
  - os trechos da seção 1 de [mensagens.md](contracts/mensagens.md): nome do marco, fonte, dia da
    extração, fim por extenso no fuso institucional e a frase de 00h00;
  - o método comum acusado uma vez, com o caminho `/drawMethod`;
  - dois marcos com métodos próprios, cada um com o seu achado e o seu caminho;
  - os recuos da FR-2655, sem achado: período não designado, sem `endAt`, cancelado, dois Eventos
    marcados, fonte fora do vocabulário (só `draw_method_invalid`);
  - fonte com horário (`Fonte de demonstração`) e extração em 2020, sem achado (D-006);
  - no ato de Retificação, o código `draw_occurrence_not_after_registration_on_retification` como
    `WARNING`, com a última frase da seção 2;
  - marco listado em `marcos_sorteados`, sem achado na Retificação;
  - método comum que governa dois marcos, com um só em `marcos_sorteados`: a advertência continua.
    Com os dois, ela some (FR-2656).
- [X] T009 [P] [US1] Escrever `backend/tests/integration/editais/test_edital_72.py`: o cronograma e o
  método do achado (inscrições até 28/10/2026 às 9h; Loteria Federal, concurso 6113, extração em
  28/10/2026 às 20h05) pelo caminho real de publicação (`publicacoes/application/publish_edital.py`),
  com `agora` antes de 28/10. A publicação é recusada com o código novo. Com a extração em 29/10, o
  Edital publica (SC-955). Sem rede: a conferência não chama a fonte.
- [X] T010 [P] [US1] Escrever `backend/tests/integration/publicacoes/test_retificacao_extracao_inviavel.py`.
  Casos:
  - Edital publicado com extração viável; Retificação que prorroga as inscrições até o dia da
    extração. A advertência aparece em `advertencias_do_ato` (não só na lista bruta: R-004), e a
    Retificação publica;
  - a mesma Retificação com sorteio constituído em todos os recortes do marco, sem advertência;
  - com sorteio em só um de dois recortes, a advertência continua (R-005).

### Implementation for User Story 1

- [X] T011 [US1] Em `backend/processo_seletivo/editais/domain/validation.py`:
  - nova conferência `_extracao_inviavel(snapshot, *, ato, marcos_sorteados)`. Ela percorre o método
    comum e os marcos bem formados por `marcos.metodo_que_governa`, como
    `_metodo_do_sorteio_publicavel`. O fim das inscrições vem de `periodo_de_inscricoes`, com o mesmo
    recuo de `_periodo_de_inscricoes_encerrado` para dois Eventos marcados e o período cancelado
    (R-003). A granularidade vem de `publica_so_a_data`, com import preguiçoso, e `None` cala (FR-2655).
    A regra vem de `sorteios.domain.viabilidade`. Instantes por `_por_extenso`;
  - recuo quando a fonte não está no vocabulário ou o `occurrenceAt` não se lê, porque esses têm
    achado próprio;
  - dois códigos, um por ato (R-004);
  - o método comum é excluído na Retificação só quando todos os marcos que ele governa estão em
    `marcos_sorteados` (R-005);
  - registrar a conferência em `validate_for_publication`, que ganha o argumento
    `marcos_sorteados: frozenset = frozenset()`, documentado como `topologia` (só a Retificação o
    passa). T008 verde.
- [X] T012 [US1] Em `backend/processo_seletivo/sorteios/application/selectors.py`: nova função
  `marcos_sorteados_em_todos_os_recortes(edital, conteudo)`. Ela deriva os recortes de cada marco por
  sorteio com `editais.domain.recortes.recortes_do_perfil`, a mesma derivação da tela do sorteio, e
  devolve o conjunto de identidades de marco em que todo recorte tem um `Sorteio` sem sucessor. Uma
  consulta para os sorteios do Edital, e não uma por recorte.
- [X] T013 [US1] Em `backend/processo_seletivo/publicacoes/application/retificacoes.py`, passar
  `marcos_sorteados=marcos_sorteados_em_todos_os_recortes(...)` nas três chamadas de
  `validate_for_publication`: a conferência do ato (~l. 692) e as duas de `advertencias_do_ato`
  (~l. 757 e ~l. 761). Com isso, a subtração e a lista mostrada partem do mesmo conjunto. Comentário
  com o porquê (D-003). T010 verde.
- [X] T014 [US1] Conferir na revisão da composição que o achado leva à etapa Classificação: escrever
  `backend/tests/interface/test_revisao_extracao_inviavel.py`, que abre a revisão do rascunho do
  Edital 72 e encontra a frase e o link da etapa. Se o caminho `/drawMethod` do método comum não
  tiver etapa mapeada, mapear no mesmo lugar em que `common_draw_method_invalid` é mapeado
  (FR-2654). T009 verde.

**Checkpoint**: US1 completa e demonstrável pelo cenário 1 do [quickstart](quickstart.md).

---

## Phase 4: User Story 2 — O aviso antes de congelar e o diagnóstico da relação congelada (Priority: P1)

**Goal**: a tela do sorteio avisa antes do congelamento condenado e diz, para a relação já
congelada, que ela não sorteia e qual é a saída (FR-2658–FR-2661).

**Independent Test**: com a extração declarada hoje, a fonte "só a data" e as inscrições encerradas,
o aviso aparece antes de "Publicar e congelar a relação", e o botão continua lá.

### Tests for User Story 2

- [X] T015 [P] [US2] Escrever `backend/tests/interface/test_sorteio_extracao_inviavel.py`. O Edital é
  levado ao estado pelo caminho real: publicado viável e depois retificado, como no
  [quickstart](quickstart.md). `timezone.now` é substituído por `mock.patch`, como em
  `tests/interface/test_convocacao_em_fluxo.py`. Casos:
  - aviso com os trechos da seção 3, antes do botão, e o botão presente (D-005);
  - **com as inscrições ainda correndo** e terminando no dia da extração: o aviso aparece junto do
    aviso de inscrições em curso, embora a hora atual, sozinha, fosse viável (FR-2651);
  - sem aviso com a extração amanhã, e sem aviso com a `Fonte de demonstração` atual;
  - sem aviso quando a ocorrência da vez é a substituta (FR-2659);
  - o link para a Retificação só para quem tem `retificacao:elaborar`;
  - relação congelada inviável, com o diagnóstico da seção 4 antes de "Realizar o sorteio";
  - método retificado depois do congelamento, com a variante "o método já foi retificado" (FR-2661);
  - relação sucedida depois da Retificação, sem diagnóstico;
  - nenhum `style=`, `<style>` nem `<script>` no HTML da resposta.

### Implementation for User Story 2

- [X] T016 [US2] Em `backend/processo_seletivo/sorteios/application/previa.py::recortes_do_marco`:
  - acrescentar ao estado do marco `congelar_agora_inviavel`: `None`, ou fonte e dia da extração,
    quando a ocorrência da vez é a declarada (não a substituta), a fonte do método vigente publica só
    a data e `viabilidade` diz inviável contra o mais tarde entre `at or timezone.now()` e o fim de
    `periodo_de_inscricoes(versao.content, ...)` (FR-2651, R-006);
  - acrescentar a cada recorte congelado `diagnostico_da_relacao`: `None`, ou fonte, dia, data do
    congelamento e `metodo_retificado`. O cálculo usa o método da versão que a relação cita
    (`metodo_declarado(relacao.versao.content, ...)`) e o compara com `relacao.publicada_em`.
    `metodo_retificado` é verdadeiro quando `resumo_do_metodo` do vigente difere de
    `relacao.metodo_hash` (R-006).

  Conferir que `relacao.versao` já vem com `select_related`, e acrescentar se não vier. Comentário
  com o porquê de não usar o método vigente para a relação congelada.
- [X] T017 [US2] Em `backend/processo_seletivo/interface/views.py::sorteio`, passar
  `congelar_agora_inviavel` ao contexto. O diagnóstico de cada recorte já viaja em `recortes`.
- [X] T018 [US2] Em `backend/processo_seletivo/interface/templates/interface/sorteio.html`:
  - o aviso da seção 3, uma vez por marco, logo depois do aviso de inscrições em curso (o método é
    do marco, e vale para todos os recortes), com `class="aviso" role="status"`. Ele **não** fica
    dentro do `{% if pode_emitir and ... not inscricoes_em_curso %}` do formulário: precisa aparecer
    também enquanto as inscrições correm. O link de Retificação
    usa o mesmo padrão `pode_retificar` que a tela já usa para o método indefinido;
  - no recorte congelado, antes do formulário "Realizar o sorteio", o diagnóstico da seção 4 com
    `class="erro"`, e a variante quando `metodo_retificado`.

  Comentários de template com o porquê, sem `<a>` nem `%}` na prosa: a varredura lê o comentário.
  T015 verde.

**Checkpoint**: US2 completa. O cenário 2 do quickstart, até o passo 5, se demonstra no navegador.

---

## Phase 5: User Story 3 — A recusa diz o que fazer (Priority: P2)

**Goal**: `occurrence_precedes_freeze` diz a granularidade e a saída em três passos, sem mudar a
comparação nem a primeira frase (FR-2662–FR-2664, FR-2668, R-007).

**Independent Test**: uma relação congelada no dia da extração, com fonte "só a data", recebe a recusa
com os dois acréscimos da seção 5.

- [X] T019 [P] [US3] Escrever `backend/tests/integration/sorteios/test_recusa_diz_a_saida.py`, no
  padrão de `test_ocorrencia_declarada.py` (fonte falsa injetada em `observar_ocorrencia`). Casos:
  - fonte "só a data", com a recusa contendo a primeira frase de hoje, a frase de 00h00 e a de "suceder
    a relação sem retificar não resolve";
  - fonte com horário, com a recusa sem a frase de 00h00 e com a da saída;
  - **a comparação fixada (FR-2664)**: limite igual a `publicada_em` recusa, e limite um microssegundo
    depois constitui.
- [X] T020 [US3] Em `backend/processo_seletivo/sorteios/application/sorteio.py::_recusar_o_que_nao_pode_sortear`,
  acrescentar à mensagem de `occurrence_precedes_freeze`, **depois** da frase existente e sem alterá-la,
  as duas frases da seção 5. A granularidade vem de `publica_so_a_data(ocorrencia.fonte)`. A condição
  `ocorrida_nao_antes_de <= relacao.publicada_em` não muda. Comentário dizendo que a primeira frase é
  da lacuna 2 e fica para aquele PR. T019 verde.

**Checkpoint**: US3 completa.

---

## Phase 6: User Story 4 — O caso se reproduz em desenvolvimento (Priority: P3)

**Goal**: sem rede, o roteiro local mostra o aviso e a recusa na mesma sessão (FR-2665, SC-959).

**Independent Test**: o cenário 2 do [quickstart](quickstart.md), executado no navegador.

- [X] T021 [P] [US4] Escrever `backend/tests/integration/sorteios/test_demonstracao_so_a_data.py`. Com
  a `Fonte de demonstração (só a data)`, congelar e sortear no mesmo dia dá
  `occurrence_precedes_freeze`. Com o congelamento feito com `timezone.now` substituído por ontem
  (`mock.patch`), o sorteio é constituído. A `seed_demo` roda sem erro e não declara a fonte nova.
- [X] T022 [US4] Demonstrar os cenários 1, 2 e 3 do [quickstart](quickstart.md) no navegador do
  painel, num banco próprio (`DB_NAME=ps_demo_102`) sem `seed_demo`. O código de acesso do portal sai
  no terminal do `runserver`. Registrar em `specs/102-sorteio-viavel-desde-a-publicacao/verificacao.md`
  o que se viu em cada passo, com o horário, e qualquer divergência do esperado.
- [X] T023 [US3] Escrever `specs/102-sorteio-viavel-desde-a-publicacao/roteiro-de-compreensao.md`
  para a SC-958, no formato da `098`. Mostra-se a quem conduz o certame só a recusa da seção 5 e,
  numa segunda rodada, só o diagnóstico da seção 4. Depois pergunta-se, sem ajuda, o que fazer e em
  que ordem. Acerto é dizer retificar e depois suceder. A aplicação com as pessoas é do usuário; a
  tarefa entrega o roteiro e a folha de registro.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [X] T024 [P] Escrever `specs/102-sorteio-viavel-desde-a-publicacao/rastreabilidade.md`: uma linha
  para **todo** identificador em negrito da spec, FR-2647 a FR-2668 e SC-954 a SC-959, com tarefa e
  teste. A SC-958 é humana e fica com o roteiro do T023, e a SC-959 com a `verificacao.md`. Rodar
  `uv run pytest tests/test_citacoes_de_requisito.py`.
- [X] T025 [P] Atualizar a linha da `102` na tabela de incrementos do `README.md` para o estado
  implementado, e o parágrafo da fonte de demonstração em `CLAUDE.md`, se a fonte nova pedir aviso
  para quem chega. Só se pedir: a regra do `CLAUDE.md` é registrar o que não se descobre lendo o
  código.
- [X] T026 Rodar `cd backend && make lint check test-pg` (4 workers, `DB_NAME` próprio) e registrar o
  total em `tasks.md`, comparando com a última medição do `CLAUDE.md`. Uma falha do teste de tempo da
  ocupação se confere isolada antes de qualquer conclusão (ver *Um teste de tempo oscila sob carga*).
- [X] T027 Preparar o PR: `git merge origin/main`, conferir se a lacuna 2 já chegou (conflito no fim
  da mensagem de `occurrence_precedes_freeze`, R-007) e se o PR #335 (o achado citado no `Input` da
  spec) já foi mergeado. O link para o achado só resolve depois dele. **O merge é do usuário.**

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Fase 1)**: sem dependência.
- **Foundational (Fase 2)**: depende da Fase 1, e bloqueia todas as histórias. T003 depende de T002;
  T005 e T006 dependem de T004; T007 depende de T003, T005 e T006.
- **US1 (Fase 3)**: depende da Fase 2. T011 depende de T008; T012 é independente de T011; T013
  depende de T011 e T012; T014 depende de T011.
- **US2 (Fase 4)**: depende da Fase 2. T016 depende de T015; T017 e T018 dependem de T016.
- **US3 (Fase 5)**: depende da Fase 2 (T006).
- **US4 (Fase 6)**: T021 depende da Fase 2. T022 depende da US1, da US2 e da US3. T023 (roteiro da US3) depende de T018 e T020, e mora nesta fase porque usa as telas prontas.
- **Polish (Fase 7)**: depende de todas as histórias.

### User Story Dependencies

- **US1** e **US2** não compartilham arquivo: `validation.py`, `selectors.py` e `retificacoes.py` de
  um lado; `previa.py`, `views.py` e `sorteio.html` do outro. Podem correr em paralelo.
- **US3** toca só `sorteio.py` e pode correr junto das duas.
- **US4** é a demonstração do conjunto.

### Parallel Opportunities

- Fase 2: T002 e T004 juntas (testes em arquivos distintos); depois T003 junto de T005/T006.
- Depois da Fase 2: T008, T009, T010, T015 e T019 juntas, por serem só testes. Depois T011/T012 (US1),
  T016 (US2) e T020 (US3) em paralelo.
- Fase 7: T024 e T025 juntas.

## Parallel Example: depois da Fase 2

```text
Task: "T008 [US1] test_extracao_inviavel.py"
Task: "T015 [US2] test_sorteio_extracao_inviavel.py"
Task: "T019 [US3] test_recusa_diz_a_saida.py"
```

## Implementation Strategy

### MVP First (US1)

1. Fases 1 e 2.
2. Fase 3 (US1): a publicação impedida fecha a lacuna para todo Edital publicado daqui em diante. É o
   valor principal.
3. **Parar e validar**: cenário 1 do quickstart e o caso do Edital 72 (SC-955).

### Incremental Delivery

1. US1: nenhum Edital novo nasce condenado.
2. US2: os Editais já publicados, e os que uma Retificação condenou, são avisados antes do ato
   irreversível.
3. US3: quem chega à recusa sabe a saída.
4. US4 e Polish: o caso é demonstrável sem rede, e a matriz fecha.

Um PR só, com as quatro histórias. São pequenas, e a US2 só se demonstra com a US1, que é o que leva
o Edital ao estado do aviso pela Retificação.
