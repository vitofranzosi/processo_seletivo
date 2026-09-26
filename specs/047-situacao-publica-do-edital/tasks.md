---

description: "Task list — 047 · Situação pública e histórico oficial do Edital em execução"
---

# Tasks: Situação pública e histórico oficial do Edital em execução

**Input**: [spec.md](spec.md) · [plan.md](plan.md) · [research.md](research.md) ·
[data-model.md](data-model.md) · [contracts/](contracts/) · [quickstart.md](quickstart.md)

**Tests**: **sim.** A spec exige uma linha de rastreabilidade por caso-limite, além das de `FR-` e de
`SC-`. A US2 é refatoração de uma régua que duas superfícies leem, e mover uma régua sem teste de
equivalência é o modo de criar a terceira.

## Format: `[ID] [P?] [Story] Descrição — e o arquivo`

- **[P]**: arquivos diferentes, nenhuma dependência aberta. **Se o arquivo passar a ser
  compartilhado, o `[P]` sai.**
- **NOVO / EXISTENTE**: onde diz existente, **acrescente; não reescreva** o que a tarefa não manda
  mudar.

---

## Os cinco portões

1. **`T002` roda ANTES de qualquer edição**: a contagem da suíte e a dos arquivos que a `R-8` nomeia.
   A `R-8` diz *"nenhum teste muda de expectativa"*, e isso é hipótese a medir, não fato.
2. **Esta feature NÃO tem migration nem escrita.** O `make preparar` continua **`N de 34`**, com N
   diferente de zero, e `tests/integration/portal/test_leitura_sem_escrita.py` continua passando
   sem mudança.
3. **A US2 vem antes da US3.** O agora e o próximo são leitores da régua que a US2 põe no domínio.
4. **O `[P]` da US1 e o da US3 não se misturam.** As duas tocam `portal/leitura.py`,
   `portal/views.py` e `selecao.html`: se forem feitas em paralelo, o `[P]` sai.
5. **Nada de `make test`.** `make test-pg` com `DB_NAME` próprio da worktree; `lint` são **dois**
   passos (`ruff check` **e** `ruff format --check`); e não edite template durante a suíte.

---

## Phase 1: Setup e medição do "antes"

- [ ] T001 Preparar a worktree em `backend/`:
  - copiar `backend/.env` do checkout principal (**gitignorado**, ausente aqui);
  - trocar `DB_NAME` e `POSTGRES_DB` por nome próprio desta worktree;
  - `uv sync --extra dev`;
  - `make preparar`, conferindo **`N de 34`** com N diferente de zero;
  - `manage.py migrate --check`.
- [ ] T002 Medir e gravar o "antes" em `specs/047-situacao-publica-do-edital/antes-da-047.md` (**NOVO**), **antes de qualquer edição**:
  - a contagem da suíte (`make test-pg`);
  - o número de casos de cada arquivo que a `R-8` nomeia: `tests/integration/portal/test_cronograma_publico.py`, `tests/integration/portal/test_acompanhamento.py`, `tests/interface/test_acessibilidade_do_portal.py`, `tests/integration/supervisao/test_pulso.py`, `tests/interface/test_supervisao.py`, `tests/portal/test_resultado_publico.py`, `tests/portal/test_sorteio_na_pagina_do_edital.py`, `tests/integration/portal/test_historico_publico.py`, `tests/integration/portal/test_leitura_sem_escrita.py`;
  - o número de consultas que `test_resultado_publico.py:212` e `test_sorteio_na_pagina_do_edital.py:143` medem hoje;
  - o que a página pública do Edital de inscrições abertas do `seed_demo` diz **depois de cancelado pela gestão**. É a reprodução do fato 1 da spec, e vale como prova do "antes".

**Checkpoint**: o "antes" está gravado, e o fato 1 está reproduzido pela tela.

---

## Phase 2: Foundational — a régua no domínio

O que a US2 e a US3 leem. Nenhum comportamento muda nesta fase.

- [ ] T003 Criar `backend/processo_seletivo/editais/domain/fase_do_evento.py` (**NOVO**) com `eventos_do_conteudo`, `instantes_do_evento`, `descricao_do_evento`, `FASE_DO_PERIODO` e `fase_do_evento`, **movidos** de `backend/processo_seletivo/interface/supervisao.py:272-275, 353-375, 411-419`. As assinaturas são as mesmas. A docstring do módulo diz por que ele saiu da gestão (`research.md`, `R-1`), no tom de `editais/domain/calendario.py`.
- [ ] T004 Acrescentar a `fase_do_evento.py` a função `marcos_pendentes(conteudo, agora)`: os Eventos de fase não concluída e não cancelados, na ordem de `marcos_do_edital`, como tuplas `(evento, inicio, fim, fase)`. Reescrever `marcos_do_edital` em `backend/processo_seletivo/interface/supervisao.py` sobre ela, montando `Marco` como hoje (`research.md`, `R-4`).
- [ ] T005 Fazer `backend/processo_seletivo/interface/supervisao.py` reimportar os nomes movidos pela T003, para que `supervisao.fase_do_evento` e os demais continuem respondendo, e apagar as definições locais. Rodar `tests/integration/supervisao/test_pulso.py` e `tests/interface/test_supervisao.py`: **devem continuar verdes sem edição**.
- [ ] T006 [P] Criar `backend/tests/unit/editais/test_fase_do_evento.py` (**NOVO**) com a tabela-verdade da régua, cada caso em três instantes (antes, durante, depois):
  - Evento com término;
  - Evento sem término (concluído a partir do **instante** de início, `D-004`);
  - período de inscrições sem término (em andamento);
  - cancelado (`None`);
  - sem início (`None`).

  E `marcos_pendentes`: exclui concluído e cancelado; ordena por início; mantém o em curso.

**Checkpoint**: a régua da `045` mora no domínio, e a gestão lê de lá sem mudar de comportamento.

---

## Phase 3: US2 — O cronograma público diz a fase que a gestão diz (P1) 🎯 MVP

**Goal**: uma régua só para o portal e a gestão; o cancelado é dito cancelado (`FR-765`, `FR-766`).

**Independent Test**: quickstart, percurso 3.

- [ ] T007 [P] [US2] Escrever os testes em `backend/tests/integration/portal/test_fase_do_cronograma.py` (**NOVO**), publicando pelo helper `publicar_selecao` de `tests/fixtures/selecao.py`:
  - o Evento sem término iniciado há uma hora sai `class="marco concluido"`;
  - o Evento com término em curso sai `class="marco em_curso"` com *Acontecendo agora*;
  - o Evento com `status: "CANCELADO"`, declarado pelo rascunho da API, sai `class="marco cancelado"`, com *cancelado* em texto e sem *Acontecendo agora*;
  - **para os quatro tipos, a classe do portal corresponde a `supervisao.fase_do_evento`** no mesmo `agora` (`SC-283`);
  - o mesmo, no acompanhamento do candidato.
- [ ] T008 [US2] Em `backend/processo_seletivo/portal/leitura.py` (**EXISTENTE**):
  - apagar `_situacao_do_evento` (linhas 62-89);
  - fazer `cronograma(conteudo, agora)` chamar `fase_do_evento`, traduzindo `PLANEJADO→futuro`, `EM_ANDAMENTO→em_curso`, `CONCLUIDO→concluido` e o cancelado para `cancelado`. O Evento sem início fica sem classe de fase;
  - reescrever a docstring do módulo: a régua deixou de ser dele.
- [ ] T009 [US2] Em `backend/processo_seletivo/portal/templates/portal/_cronograma.html` (**EXISTENTE**), acrescentar o estado `cancelado`:
  - rótulo em texto *cancelado*, nunca só por cor (UX-019);
  - sem `aria-current`;
  - o nome do Evento e as datas publicadas continuam.

  Em `backend/processo_seletivo/portal/templates/portal/base.html`, acrescentar a regra CSS de `.marco.cancelado`, sem alterar as demais.
- [ ] T010 [US2] Rodar `test_cronograma_publico.py`, `test_acompanhamento.py`, `test_acessibilidade_do_portal.py` e `test_fase_do_cronograma.py`. Se algum caso existente mudar de expectativa, registrar em `antes-da-047.md` qual e por quê **antes** de editá-lo. A `R-8` previu zero.

**Checkpoint**: portal e gestão leem a mesma fase, e o cancelado não se anuncia.

---

## Phase 4: US1 — O Edital que acabou diz que acabou (P1)

**Goal**: o desfecho vence a marca do período, na página e no cartão (`FR-760` a `FR-764`).

**Independent Test**: quickstart, percursos 1 e 2.

- [ ] T011 [P] [US1] Escrever os testes em `backend/tests/integration/portal/test_desfecho_publico.py` (**NOVO**). Finalizar por `processos/application/finalizacao.py` (`cancel_edital`, `close_edital`, `close_process`), como `tests/integration/processos/test_finalizacao_concorrente.py` faz. Casos:
  - Edital cancelado com período em curso: a página diz *cancelado* e a data do ato, sem *Aberta* nem *Faltam* (`FR-760`, `FR-761`);
  - cancelado com período por abrir: sem *Em breve* nem *começam em*;
  - Edital encerrado: página e cartão da vitrine dizem *encerrado*, e o cartão está no grupo *Inscrições encerradas* mesmo com o período declarado ainda em curso (`FR-763`, `R-3`);
  - Processo encerrado com Edital publicado: a página diz o encerramento do Processo (`FR-762`);
  - precedência: o Edital encerrado de um Processo depois cancelado diz o desfecho do **Edital** (`D-003`);
  - o motivo digitado no ato **não** aparece no HTML (`FR-764`);
  - o `actor_subject` do ato **não** aparece no HTML (`FR-776`);
  - o cancelado continua fora da vitrine e responde 200 pelo endereço;
  - cronograma, documentos e resultados continuam na página com desfecho.
- [ ] T012 [US1] Em `backend/processo_seletivo/processos/application/selectors.py` (**EXISTENTE**), criar `desfechos(editais)`. Recebe Editais com `processo` carregado e devolve `{edital_id: Desfecho | None}` pela precedência de `data-model.md`. A data vem do `AtoAdministrativo` mais recente de operação `ENCERRAR`/`CANCELAR` do agregado aplicável, lido numa **única** consulta, e só quando algum estado é final. Sem ato encontrado, `em=None` (`research.md`, `R-2`). Definir `Desfecho` como dataclass congelada no mesmo módulo.
- [ ] T013 [P] [US1] Criar `backend/tests/unit/processos/test_desfechos.py` (**NOVO**), ou acrescentar ao teste de selectors existente se houver:
  - uma consulta para N Editais finais e zero para N Editais publicados;
  - a precedência;
  - o ato ausente devolve `em=None`.
- [ ] T014 [US1] Em `backend/processo_seletivo/portal/leitura.py`, criar `situacao_publica(periodo, desfecho)`, que devolve `(chave, rotulo)`. Com desfecho, as chaves são `cancelado`, `encerrado_edital` e `encerrado_processo`; sem desfecho, a marca de `SITUACAO_DO_CARTAO`, inalterada. Fazer `agrupar_por_situacao` mandar o Edital com desfecho para o grupo `ENCERRADO`.
- [ ] T015 [US1] Em `backend/processo_seletivo/portal/views.py`:
  - `selecao`: calcular `desfechos([versao.edital])`, usar `situacao_publica` para `situacao_rotulo` e para a classe da marca, e zerar `dias_restantes` quando houver desfecho;
  - `vitrine` e `_selecao_da_vitrine`: calcular `desfechos` **uma vez** para todos os Editais listados, e usar o resultado no rótulo, na classe e no grupo.
- [ ] T016 [US1] Nos templates, dizer o desfecho **com a data**, na zona institucional, e nenhuma frase de prazo quando ele existir:
  - `backend/processo_seletivo/portal/templates/portal/selecao.html`: a classe da marca passa a vir da situação pública, e não de `periodo.estado`;
  - `backend/processo_seletivo/portal/templates/portal/_periodo.html`;
  - `backend/processo_seletivo/portal/templates/portal/_cartao_da_selecao.html`.

  CSS das três chaves novas em `base.html`.
- [ ] T017 [P] [US1] Em `backend/tests/portal/` (**EXISTENTE**, arquivo de consultas da vitrine; criar `test_consultas_da_vitrine.py` se não houver), medir que a vitrine com 1 e com 5 Editais encerrados emite o **mesmo** número de consultas (`R-7`).

**Checkpoint**: nenhuma página de Edital com desfecho afirma inscrição aberta.

---

## Phase 5: US3 — A página diz o que acontece agora e o que vem depois (P2)

**Goal**: agora e próximo derivados do cronograma vigente (`FR-767`, `FR-768`). **Depende da Phase 2.**

**Independent Test**: quickstart, percurso 4.

- [ ] T018 [P] [US3] Escrever os testes em `backend/tests/integration/portal/test_agora_e_proximo.py` (**NOVO**):
  - inscrições encerradas e três Eventos futuros: o próximo é o de início mais próximo;
  - dois Eventos empatados no início: os dois aparecem, na ordem publicada;
  - um Evento com término em curso: aparece como em andamento;
  - nenhum Evento pendente: nenhum bloco, e o HTML não contém *em análise*;
  - o Evento cancelado nunca é próximo;
  - Edital com desfecho: nenhum bloco;
  - Retificação publicada com vigência **futura** que antecipa um Evento: o próximo é o da versão vigente, e não o da Retificação (edge case).
- [ ] T019 [US3] Em `backend/processo_seletivo/portal/leitura.py`, criar `agora_e_proximo(conteudo, agora)` sobre `marcos_pendentes`. Devolve `{"em_andamento": [...], "proximos": [...]}` com nome e início. O período de inscrições **não** entra em `em_andamento`, porque a marca e a faixa já o dizem (contrato).
- [ ] T020 [US3] Em `backend/processo_seletivo/portal/views.py`, `selecao`: pôr `agora_e_proximo` no contexto, e só quando não houver desfecho.
- [ ] T021 [US3] Em `backend/processo_seletivo/portal/templates/portal/selecao.html`, acrescentar o bloco no cabeçalho, depois do `_periodo.html`. Omitir o bloco inteiro quando as duas listas forem vazias (a decisão *ausência nunca vira afirmação*, da `024`).

**Checkpoint**: a página responde *"o que acontece agora ou depois"* sem rolar até o cronograma.

---

## Phase 6: US4 — Quem chega ao resultado sabe até quando pode recorrer (P2)

**Goal**: o prazo público é o que a interposição aplica (`FR-769` a `FR-771`).

**Independent Test**: quickstart, percurso 5.

- [ ] T022 [P] [US4] Escrever os testes em `backend/tests/portal/test_prazo_recursal_publico.py` (**NOVO**), com `rascunho_com_marco(janela_recursal={"admits": True, "durationDays": 5, "unit": "DIAS_CORRIDOS"})` e `publicar_o_ato` de `tests/fixtures/divulgacao.py`. Casos:
  - preliminar vigente com prazo em curso: a página do resultado diz abertura, encerramento e *aberto*, sem se identificar;
  - a lista de vigentes da página do Edital diz *recurso até* a data;
  - **a data é igual à de `recursos/application/interpor.py`** (`situacao_do_prazo`/`_fecha_em`) para uma inscrição daquele ato (`SC-284`);
  - com o relógio depois do encerramento (fixture de `tests/fixtures/clock.py`): *encerrado* e a data; a lista de vigentes não diz nada;
  - definitiva do **mesmo** ato, publicada depois do encerramento (a definitiva com prazo aberto é recusada pela `018`): o prazo dito é o da primeira publicação;
  - marco sem janela, e com `admits: false`: nenhuma menção a recurso;
  - publicação sucedida: nenhuma menção a prazo;
  - nenhuma ação de recorrer em caso algum. O teste existente `test_a_pagina_nao_oferece_acao_de_recurso` continua.
- [ ] T023 [US4] Em `backend/processo_seletivo/recursos/application/selectors.py` (**EXISTENTE**), criar `janela_da_publicacao_divulgada(publicacao)`: o conteúdo vigente do Edital, `declaracao_do_marco(conteudo, publicacao.marco_id)` e `janela_da_publicacao(publicacao, declaracao)`. Devolve `(abre, fecha)` ou `None`. A docstring diz que ela é **a** conta da interposição, e por que a norma é a vigente (`research.md`, `R-5`; `D-005`).
- [ ] T024 [US4] Em `backend/processo_seletivo/recursos/application/interpor.py` (**EXISTENTE**, `_janelas_pertinentes`, linhas 164-205), fazer o ramo `publicacao is not None` chamar `janela_da_publicacao_divulgada`. O ramo do `ResultadoEtapa` não muda. Rodar os testes de `tests/portal/test_parecer_do_titular.py` e os de interposição (`grep -rl interpor tests/`): **devem continuar verdes sem edição**.
- [ ] T025 [US4] Em `backend/processo_seletivo/portal/views.py`:
  - `resultado`: quando `not foi_sucedida`, pôr no contexto a janela e se ela está aberta no instante da leitura;
  - `selecao`: anotar cada item de `resultados_divulgados` com `fecha_em` só quando o prazo estiver aberto.
- [ ] T026 [US4] Em `backend/processo_seletivo/portal/templates/portal/resultado.html` e no trecho de resultados divulgados de `selecao.html`, dizer o período em texto, com dia, mês, ano e hora do encerramento na zona institucional. Pode dizer, sem link de ação, que a interposição é feita na área do candidato (`FR-771`, MAY). Comentário no template: o prazo é o da interposição, e a página não o recalcula.

**Checkpoint**: a mesma data na página pública, no acompanhamento e na recusa da interposição.

---

## Phase 7: US5 — Todo resultado divulgado continua alcançável pela página do Edital (P3)

**Goal**: o histórico dos resultados é alcançável e rotulado como histórico (`FR-772`, `FR-773`).

**Independent Test**: quickstart, percurso 6.

- [ ] T027 [P] [US5] Escrever os testes em `backend/tests/portal/test_historico_de_resultados.py` (**NOVO**):
  - preliminar sucedido por definitivo: a página do Edital lista o definitivo como vigente e, em *Publicações anteriores* do mesmo marco e lista, o preliminar com natureza, data e link para o endereço dele;
  - a página do definitivo lista o preliminar como anterior;
  - cadeia de três: ordem, e só a última vigente;
  - duas listas no mesmo marco (fixture de `tests/fixtures/recortes.py` ou `sorteio.py`, conforme a que produz duas listas divulgadas): o histórico de uma não aparece sob a outra;
  - definitivo que corrigiu por recurso (`deferir_corrigindo` de `tests/fixtures/recursos.py`): a causa continua dita, sem natureza nova;
  - nenhum identificador de ator no HTML (`FR-776`);
  - **no máximo duas navegações** da página do Edital até o preliminar (`SC-285`), afirmado pela presença do link na primeira página.
- [ ] T028 [US5] Em `backend/processo_seletivo/divulgacao/application/selectors.py` (**EXISTENTE**), criar `historico_publico_do_edital(edital)`: todas as publicações do Edital, `prefetch_related("sucessoras")`, agrupadas por `(marco_id, lista_id)`, com natureza, data, `_rotulos` e `vigente`. Sem `ato` e sem autor (`research.md`, `R-6`). Criar também `anteriores_da_cadeia(publicacao)`, que sobe `publicacao_anterior` e devolve a lista ordenada.
- [ ] T029 [US5] Em `backend/processo_seletivo/portal/views.py`, fazer `selecao` montar os vigentes **e** o histórico a partir de `historico_publico_do_edital`, com uma consulta só, em lugar da consulta de `vigentes_do_edital`, sem mudar o que a seção de vigentes mostra. Fazer `resultado` pôr `anteriores_da_cadeia` no contexto.
- [ ] T030 [US5] Em `selecao.html`, sob cada vigente com anteriores, acrescentar `<details>` *Publicações anteriores*, com a sucedida rotulada em texto (FR-052 da `017`: não só por cor). Em `resultado.html`, acrescentar a lista *Publicações anteriores deste resultado*, quando houver.
- [ ] T031 [P] [US5] Atualizar a medição de consultas de `tests/portal/test_resultado_publico.py:212` e `tests/portal/test_sorteio_na_pagina_do_edital.py:143` **somente** se o número mudar, com a justificativa no comentário do teste. O número tem de ser constante no tamanho da cadeia (`R-7`).

**Checkpoint**: o preliminar sucedido está a um clique da página do Edital.

---

## Phase 8: Polish, legado e fechamento

- [ ] T032 [P] Escrever `backend/tests/integration/portal/test_legado_da_projecao.py` (**NOVO**):
  - Edital com conteúdo publicado sem `appealWindow` e sem `location`: a página abre, e nenhum prazo é inventado (`FR-775`);
  - Edital com Evento cujo `status` publicado é `EM_ANDAMENTO`, aceito pela API antes da `045`: a fase vem das datas;
  - Evento sem início: sem fase e não é próximo.

  Usar o padrão de `tests/fixtures/legado.py` para produzir o conteúdo antigo.
- [ ] T033 Rodar `tests/integration/portal/test_leitura_sem_escrita.py`, `manage.py migrate --check` e `make preparar` (`N de 34`): nada escrito e nada migrado (`SC-286`).
- [ ] T034 Escrever `specs/047-situacao-publica-do-edital/rastreabilidade.md` (**NOVO**):
  - uma linha por `FR-760` a `FR-776`, por `SC-282` a `SC-287` e **por caso-limite da spec**, cada uma com o teste que a prende;
  - uma linha para cada identificador em negrito do cabeçalho *Faixa de identificadores*;
  - as decisões `D-001` a `D-007` com onde se verificam.
- [ ] T035 Percorrer os sete percursos do `quickstart.md` pelo navegador, com `PORTAL`/`INTERFACE` locais em `localhost`, e registrar o resultado e as capturas em `rastreabilidade.md`: o percurso 1 contra o "antes" da T002. **Use preset desktop para agir** (viewport emulado desalinha cliques).
- [ ] T036 Em `doc/auditoria-de-consolidacao-2026-09-26.md`:
  - marcar o RC-48 como resolvido pela 047;
  - registrar a parte do portal do RC-80;
  - registrar os dois achados que esta investigação acrescentou (Edital cancelado *"Aberta"* e resultado sucedido sem caminho público), com o PR.

  Em PR **separado** de documentação, como os #182, #184 e #186 fizeram.
- [ ] T037 `cd backend && make lint check test-pg DB_NAME=<banco-da-worktree>`: `ruff check` **e** `ruff format --check`. Comparar a contagem com a do "antes" da T002, e explicar a diferença caso a caso em `antes-da-047.md`.

---

## Dependencies & Execution Order

```text
T001 → T002 ─► Phase 2 (T003 → T004 → T005; T006 [P])
                 ├─► US2 (T007 [P], T008 → T009 → T010)   🎯 MVP
                 │     └─► US3 (T018 [P], T019 → T020 → T021)
                 ├─► US1 (T011 [P], T012 → T013 [P], T014 → T015 → T016, T017 [P])
                 ├─► US4 (T022 [P], T023 → T024 → T025 → T026)
                 └─► US5 (T027 [P], T028 → T029 → T030, T031)
All ─► Phase 8 (T032 [P], T033, T034 → T035, T036, T037)
```

- **US1, US4 e US5** dependem só da Phase 1, mas compartilham `portal/views.py` e `selecao.html`:
  em paralelo, só com arquivos resolvidos na ordem acima.
- **US4** toca `recursos/`, e é a única história com risco de regressão fora do portal. A T024 existe
  para medir isso.

## Parallel Examples

- Na abertura de cada história, os testes `[P]` (T007, T011, T018, T022, T027) podem ser escritos
  juntos, porque cada um é arquivo novo.
- T006, T013 e T017 são arquivos de teste próprios, e rodam em paralelo com a implementação da
  história a que pertencem.

## Implementation Strategy

1. **MVP = Phase 2 + US2 + US1.** É a parte que tira do portal afirmações falsas: o *"Aberta"* do
   cancelado e o Evento cancelado *"acontecendo agora"*. Pode ser entregue sozinha.
2. **Depois, US4**, o RC-48 da auditoria, que está na onda do candidato.
3. **US3 e US5** por último: evolução sobre registros que já existem e respondem.
4. Cada história fecha com o próprio percurso do quickstart antes da seguinte.
