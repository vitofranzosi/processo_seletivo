---

description: "Task list — 046 · Contrato de executabilidade do Processo publicado"
---

# Tasks: Contrato de executabilidade do Processo publicado

**Input**: [spec.md](spec.md) · [plan.md](plan.md) · [research.md](research.md) ·
[data-model.md](data-model.md) · [contracts/](contracts/) · [quickstart.md](quickstart.md)

**Tests**: **sim.** A spec pede demonstração por fluxo observável para cada achado da auditoria
(*"Correlação com a auditoria de consolidação"*), e a `SC-275` é uma tabela-verdade que só se prova
por teste. E a feature muda fixture de 191 arquivos (`R-7`): mudar sem contar é o modo de perder
guarda sem perceber.

## Format: `[ID] [P?] [Story] Descrição — e o arquivo`

- **[P]**: arquivos diferentes, nenhuma dependência aberta. **Ganhou arquivo em comum depois, o `[P]`
  sai.**
- **NOVO / EXISTENTE**: onde diz existente, **acrescente; não reescreva** o que a tarefa não manda
  mudar. Onde a tarefa manda reescrever, ela nomeia o caso.

---

## Os cinco portões

1. **A `045` está na `main` antes da `T001`** (decisão de 26/09, `R-8`). Se não estiver, pare: esta
   lista pressupõe o `stage_without_schedule_event`, a `T021` de lá e o filtro por severidade em
   `test_etapas.py`.
2. **Em cada história que muda fixture, a fixture muda ANTES da regra.** Com a regra primeiro, a suíte
   cai em bloco com causa enganosa — 872 erros a 34% na primeira rodada do protótipo (`R-7`).
3. **Esta feature NÃO tem migration.** O `make preparar` continua **`N de 34`**, com N diferente de
   zero.
4. **A regra da consolidação não é copiada.** Nenhuma tarefa reescreve os três predicados de
   `resultados/domain/regra.py` fora dele (`FR-747`); quem precisar deles importa a função.
5. **Nada de `make test`.** `make test-pg`, com `DB_NAME` próprio da worktree; `lint` são **dois**
   passos (`ruff check` **e** `ruff format --check`); e não edite arquivo durante a suíte.

---

## Phase 1: Setup e medição do "antes"

- [X] T001 Preparar a worktree em `backend/`: rebasear sobre a `main` com a `045` mesclada; copiar `backend/.env` do checkout principal (**gitignorado**), trocar `DB_NAME` e `POSTGRES_DB` por nome próprio desta worktree; `uv sync --extra dev`; `make preparar` — conferir **`N de 34`** — e `manage.py migrate --check`
- [X] T002 Gravar o "antes" em `specs/046-contrato-de-executabilidade/antes-do-gate.md` (**NOVO**): a contagem da suíte (`make test-pg`); a tabela do `R-7` refeita sobre a `main` com a `045` — as quatro causas, com casos e arquivos — pelo mesmo método do protótipo (registrar sem bloquear, reverter); e o número de casos de `tests/unit/editais/test_executabilidade.py`, `tests/interface/test_hardening_pos_auditoria.py`, `tests/interface/test_ocupacao.py`, `tests/integration/resultados/test_prontidao.py` e `tests/unit/resultados/test_regra.py`. **Antes de qualquer edição**

**Checkpoint**: o "antes" está gravado, e a tabela de causas bate com a do `R-7` ou a diferença está explicada.

---

## Phase 2: Foundational — o ajudante do acervo

- [X] T003 Criar `publicar_como_acervo` em `backend/tests/fixtures/legado.py` (**EXISTENTE** — acrescente, ao lado de `publicar_sem_aferir`): publica pelo caminho normal (`publish_original` / `levar_a_publicacao`) com `_etapa_sem_resultado` e `_perfil_sem_corte` de `processo_seletivo.editais.domain.validation` neutralizadas **só durante a chamada** (`mock.patch` que devolve `[]`), **sem** rebaixar a versão canônica. Docstring: *simula o Edital publicado antes da `046`, que existe no acervo e que a consolidação continua recusando* (`R-7`). Enquanto as duas funções não existirem, o `patch` usa `create=True`; a `T031` o remove
- [X] T004 Acrescentar a `publicar_processo_com_etapas`, em `backend/tests/fixtures/comissao.py` (**EXISTENTE**), o parâmetro `como_acervo=False`, que troca `publish_original` por `publicar_como_acervo`. Rodar `make test-pg` — **deve continuar verde**: nada chama o parâmetro ainda

**Checkpoint**: existe um caminho declarado, e só um, para publicar o que esta feature vai recusar.

---

## Phase 3: US3 — O Edital publicado não se julga como se fosse publicar (P3)

**Goal**: nenhuma pendência de publicação em Edital publicado, encerrado ou cancelado; nada muda antes.

**Independent Test**: [quickstart.md](quickstart.md), percurso 3.

**Primeira por ser a menor e não depender de fixture** (`plan.md`, *Ordem de entrega*).

- [X] T005 [US3] Em `backend/processo_seletivo/interface/views.py` (**EXISTENTE**), `_pendencias` (~linha 816): quando `edital.status` não está em `EM_ELABORACAO`, `EM_REVISAO` ou `HOMOLOGADO`, devolver **só** os achados cujo código está em `FATOS_DO_CONTEUDO_PUBLICADO = {"stage_without_schedule_event"}` (`R-5`). Comentário: por que o ponto é este e não o template — a previsão de recusa dos atos também lê daqui —, e por que lista e não severidade (`FR-755`, `D-003`)
- [X] T006 [US3] Prender a regra em `backend/tests/interface/test_edital_publicado_sem_pendencias.py` (**NOVO**): Edital publicado com o período de inscrições designado e relógio (`agora` de `_pendencias`, ou `timezone.now` só da view) depois do término — zero *"Impede"* e zero `registration_period_closed`/`schedule_event_in_past` na tela do Edital e nas nove etapas do assistente; o mesmo conteúdo em elaboração exibe `registration_period_closed` nas duas superfícies; Edital `ENCERRADO` e `CANCELADO` idem ao publicado; e, com uma Etapa sem Evento, o aviso da `045` **continua** na página publicada (`SC-278`, `FR-739` da `045`)
- [X] T007 [US3] Reescrever o lado da gestão de `backend/tests/integration/portal/test_cronograma_publico.py::test_o_periodo_em_curso_e_acontecendo_agora_dos_dois_lados` (**EXISTENTE**, ~285-330): a conferência passa a ser lida no domínio — `validate_for_publication` sobre o conteúdo publicado, com o **mesmo** `agora` — e, com a `045`, pela fase derivada que a página do Processo exibe; manter a contraprova (*Homologação* acusada, *Período de inscrições* não) nessa leitura. Acrescentar a afirmação de que a tela do Edital publicado não acusa Evento nenhum. Docstring: por que a `SC-191` continua valendo (`R-7`)
- [X] T008 [US3] Reescrever `backend/tests/interface/test_conducao_dos_bloqueios.py::test_edital_publicado_nao_manda_pedir_a_ninguem` (**EXISTENTE**, ~250-270): a premissa *"há pendência corrigível na tela"* deixa de existir; afirmar **zero** pendências e zero condução na Revisão do Edital publicado. Conferir o caso vizinho `test_edital_publicado_nao_manda_pedir_nem_a_quem_nao_tem_a_permissao` pela mesma razão
- [X] T009 [US3] Em `backend/tests/interface/test_compor.py::test_o_edital_publicado_diz_a_etapa_sem_evento_na_validacao_do_conteudo` (**EXISTENTE**, da `T021` da `045`): **não retirar nada** — o caso continua valendo (`D-003`, `R-8`). Acrescentar a contraprova: na mesma página publicada, nenhum *"Impede"* e nenhum aviso cujo código não esteja em `FATOS_DO_CONTEUDO_PUBLICADO`
- [X] T010 [US3] Varredura da `FR-756` em `backend/tests/test_quem_consulta_a_publicabilidade.py` (**NOVO**): percorrer `backend/processo_seletivo/**/*.py` e prender a lista fechada de arquivos que chamam `validate_for_publication(` — `publicacoes/application/publish_edital.py`, `publicacoes/application/retificacoes.py`, `interface/views.py` e a própria definição —, com o padrão de `tests/test_vigencia_do_resultado.py` e uma prova de que a varredura enxerga (arquivo com chamada inventada, em memória)
- [X] T011 [US3] `make test-pg` — verde; o total muda só pelos casos novos

**Checkpoint**: o `RC-32` fecha, com as duas superfícies e a `FR-549a` preservada.

---

## Phase 4: US4 — A semente de demonstração não chega a um Processo real (P4)

**Goal**: fora do vocabulário em produção; disponível em desenvolvimento e nos testes.

**Independent Test**: [quickstart.md](quickstart.md), percurso 4.

- [ ] T012 [P] [US4] Configuração em `backend/config/settings/base.py`, `development.py`, `test.py` e `production.py` (**EXISTENTES**): `SORTEIO_FONTE_DE_DEMONSTRACAO` lida do ambiente e falsa por padrão na base; `True` fixo em `development.py` e `test.py`; em `production.py`, `_exigir(not SORTEIO_FONTE_DE_DEMONSTRACAO, "SORTEIO_FONTE_DE_DEMONSTRACAO", ...)` ao lado das duas barreiras de identidade, com a frase dizendo que a semente é fixa e o sorteio seria previsível (`R-6`, `FR-758`)
- [ ] T013 [US4] Em `backend/processo_seletivo/sorteios/infrastructure/fontes/__init__.py` (**EXISTENTE**): `fontes_publicadas()` devolve o vocabulário do ambiente — `Loteria Federal` sempre, `Fonte de demonstração` só com a configuração ligada, lida na chamada; `fonte_declarada` passa a usá-la; `FONTES` sai de `__all__` (`FR-757`). Comentário: por que função e não dicionário (`override_settings`), e que o ambiente decide se o nome existe, nunca para onde ele aponta (`021`, `FR-076`)
- [ ] T014 [US4] Trocar os leitores de `FONTES` por `fontes_publicadas()`: `backend/processo_seletivo/interface/forms.py` (~318-322) e `backend/processo_seletivo/editais/domain/perfis.py` (`_validar_fonte_publicada`, ~534-541); e `backend/tests/integration/sorteios/test_ocorrencia_declarada.py` (~247-255), que importa `FONTES`
- [ ] T015 [P] [US4] Prender a barreira em `backend/tests/test_configuracao_producao.py` (**EXISTENTE**): acrescentar `({"SORTEIO_FONTE_DE_DEMONSTRACAO": "true"}, "SORTEIO_FONTE_DE_DEMONSTRACAO")` à lista parametrizada (~99), e um caso que carrega o módulo de produção sem a variável e confere o valor falso
- [ ] T016 [US4] Prender o vocabulário em `backend/tests/integration/sorteios/test_fonte_fora_de_producao.py` (**NOVO**), com `override_settings(SORTEIO_FONTE_DE_DEMONSTRACAO=False)`: o seletor de fonte da etapa *Classificação* oferece só a Loteria Federal; a gravação do rascunho recusa a fonte de demonstração; `validate_for_publication` a acusa (`draw_method_invalid`) nos dois atos; `fonte_declarada("Fonte de demonstração")` recusa com `draw_source_not_supported`. E o reaproveitamento: criar Edital a partir de um publicado cujo método declara a fonte de demonstração e conferir que a gravação do conteúdo copiado a recusa (US4, cenário 2). E a contraprova com a configuração ligada: as quatro aceitam (`SC-279`, `FR-759`)
- [ ] T017 [US4] `make test-pg` — verde, com a suíte de sorteio **inalterada**; e `manage.py seed_demo` num banco próprio roda sem rede

**Checkpoint**: o `RC-72` fecha, e o `seed_demo` continua.

---

## Phase 5: US2 — Um Perfil que não convoca ninguém não é publicado como completo (P2)

**Goal**: Perfil sem marco que corte é impeditivo; marco sem corte num Perfil que corta continua publicável.

**Independent Test**: [quickstart.md](quickstart.md), percurso 2.

### a. As fixtures, antes da regra (portão 2)

- [ ] T018 [US2] Dar regra de corte que **não governa Etapa alguma** — `targetKind: "FIXED"`, `targetCount` igual às vagas do Perfil, `surplusCount: 0`, `tieOutcome: "STRICT"`, `governedStage: "NONE"`, `continuation: "NONE"` — a todo marco de fixture que publica sem `cutRule`: `backend/tests/fixtures/selecao.py` (~62, ~94), `backend/tests/fixtures/divulgacao.py` (~125), `backend/tests/fixtures/sorteio.py` (~55) e qualquer outra que a `T002` tenha contado. Comentário em cada: por que é a regra que não mexe em participação (`FR-214`; `faixa.etapa_governada` devolve `None`)
- [ ] T019 [US2] O mesmo no marco do Perfil de sorteio de `backend/processo_seletivo/processos/management/commands/seed_demo.py` (~542), com alvo igual às vagas do quadro daquele Perfil; conferir `backend/tests/integration/test_seed_demo.py`
- [ ] T020 [US2] `make test-pg` — **deve continuar verde**. Se algum caso quebrar, é porque exercitava marco sem corte de propósito: ele vai para a `T023`, e não se afrouxa a fixture

### b. A regra

- [ ] T021 [US2] Em `backend/processo_seletivo/editais/domain/validation.py` (**EXISTENTE**): `_perfil_sem_corte(snapshot, *, ato)` ao lado de `_perfil_sem_marco`, chamada em `validate_for_publication` — só no ato de publicação; só Perfil **com** marco bem formado; `profile_without_cut_rule`, impeditivo, caminho `/profiles/id=<perfil>/classificationMilestones`, rótulo `code` antes de `name`, frase do [contrato](contracts/o-gate-da-publicacao.md) §1 (`FR-752`, `R-4`)
- [ ] T022 [US2] Em `_marco_sem_regra_de_corte`, no mesmo arquivo: pular o Perfil em que nenhum marco declara `cutRule` (`FR-753`). Atualizar o docstring: a `D-G1` foi substituída pela `D-002` da `046`, e o aviso fica para o marco sem corte num Perfil que corta

### c. Os casos

- [ ] T023 [US2] Reescrever em `backend/tests/unit/editais/test_executabilidade.py` (**EXISTENTE**) os casos da `FR-461` que usam Perfil de marco único — `test_marco_sem_regra_de_corte_e_aviso_e_nao_impedimento` (~217), `test_o_aviso_do_corte_nomeia_a_cadeia_inteira_ate_a_convocacao` (~229) e o parametrizado de ~262 —: o marco sem corte passa a ter um vizinho que corta (Cenário D). Acrescentar: Perfil de marco único sem corte → `profile_without_cut_rule` impeditivo e **nenhum** `milestone_without_cut_rule`; regra que não governa Etapa → nada; Perfil sem marco → só `profile_without_milestone`; ato de Retificação → nada (`FR-754`); a frase nomeia Perfil, falta, consequência e etapa (`SC-280`)
- [ ] T024 [US2] Ajustar `backend/tests/interface/test_hardening_pos_auditoria.py` (**EXISTENTE**): ~785-787 (o conjunto de achados passa a ter `profile_without_cut_rule` no lugar do aviso, se o cenário é de marco único), ~861 (o destino do código novo é a *Classificação*) e ~1100 (o aviso continua `WARNING` num Perfil que corta; o impeditivo é novo). Registrar no docstring de cada caso alterado o que mudou e por quê
- [ ] T025 [US2] O cenário `sem_regra_de_corte` de `backend/tests/interface/test_ocupacao.py` (~445-470) publica marco único sem corte: passar a publicar por `publicar_como_acervo` — é o Edital do acervo que a `032` descreveu, e a `FR-463` continua valendo sobre ele
- [ ] T026 [US2] Interface em `backend/tests/interface/test_perfil_sem_corte.py` (**NOVO**): pela composição, Perfil de marco único em *"Este marco não corta"* → *"Impede"* na Revisão, na *Classificação*, e a submissão recusada; com o segundo marco que corta → publica, com **um** aviso (`SC-277`)
- [ ] T027 [US2] `make test-pg` — verde; recontar contra a `T002`

**Checkpoint**: o `RC-30` fecha pela regra do Perfil, e o Cenário C continua coberto pelos casos de `tests/unit/editais/test_regra_de_corte.py`, intocados.

---

## Phase 6: US1 — A Etapa que o fluxo não consegue concluir não atravessa a publicação (P1) 🎯

**Goal**: impeditivo quando a regra da consolidação recusa e o Resultado é exigido; aviso quando não é; advertência na Retificação.

**Independent Test**: [quickstart.md](quickstart.md), percurso 1.

### a. As fixtures, antes da regra (portão 2)

- [ ] T028 [US1] Em `backend/tests/fixtures/comissao.py` (**EXISTENTE**), `etapas()`: `minima` passa a ter padrão `"0.0000"` (continua sendo descartada no ramo decisório). Docstring: por que zero — não elimina, não obriga parecer (`012`, `FR-033`) —, e que `minima=None` com `como_acervo=True` é o caminho do Edital que a consolidação recusa (`R-7`). Conferir as outras fixtures que publicam Etapa eliminatória pontuada — `tests/fixtures/corte.py` (~51), `tests/fixtures/supervisao.py` (~101), `tests/fixtures/snapshot.py` (~324) — e dar-lhes nota mínima onde faltar
- [ ] T029 [US1] Passar para `como_acervo=True` todo caso que publica `avaliacoes` maior que 1 em Etapa eliminatória ou enumerada — os 30 arquivos e os 3 do reaproveitamento que a `T002` contou (entre eles `tests/interface/test_mesa_modelo_exigido.py`, `test_acessibilidade_da_012.py`, `test_trilha_da_012.py`, `test_mesa_lista_exigida.py`, `tests/integration/avaliacoes/test_avaliacao.py`, `test_distribuicao.py`, `test_trilha_completa.py`, `test_versao_da_avaliacao.py`, `tests/integration/editais/test_reaproveitamento.py`, `tests/interface/test_reaproveitar.py`, `tests/authorization/test_reaproveitamento.py`). Onde o caso publica por outro ajudante que não `publicar_processo_com_etapas`, usar `publicar_como_acervo` diretamente
- [ ] T030 [US1] Os quatro arquivos que afirmam a recusa da consolidação — `backend/tests/integration/resultados/test_prontidao.py`, `backend/tests/integration/resultados/test_ocorrencia.py`, `backend/tests/contract/test_consolidacao.py`, `backend/tests/acceptance/test_quickstart.py` —: publicar como acervo, com `minima=None` explícito onde a recusa é a da nota mínima. `make test-pg` — **deve continuar verde**

### b. A regra

- [ ] T031 [US1] Em `backend/processo_seletivo/editais/domain/validation.py` (**EXISTENTE**): `_etapa_sem_resultado(snapshot, *, ato)`, chamada em `validate_for_publication`. Importação **local** de `impedimento_da_regra` e `eliminatoria` de `processo_seletivo.resultados.domain.regra`; conjunto das Etapas referenciadas montado uma vez — `stages` dos marcos, `faixa.etapa_governada(cutRule)`, `marcos.metodo_que_governa(...)["qualifyingStageId"]`; `stage_result_unreachable` (impeditivo, só publicação, exigida) e `stage_without_result` (aviso na publicação sem exigência; advertência na Retificação sempre); caminho `/stages/id=<etapa>`; frases do [contrato](contracts/o-gate-da-publicacao.md) §1, com a frase da regra **sem reescrita** (`FR-746`, `FR-748`, `FR-749`). Comentário: a tensão com `avaliacoes/domain/formas.py:12-15` e por que ela não é violada (`R-1`); por que dois códigos (`R-3`). Retirar o `create=True` da `T003`
- [ ] T032 [US1] Tabela-verdade em `backend/tests/unit/editais/test_etapa_sem_resultado.py` (**NOVO**): as três razões × as cinco situações (eliminatória; enumerada; governada por corte; Etapa de habilitação de sorteio, própria e comum; nenhuma), parametrizada **a partir de `impedimento_da_regra`** — o caso afirma que a publicação acusa se, e só se, a regra recusa (`FR-747`, `SC-275`). Mais: Etapa consolidável → nada (Cenário B); os dois códigos nunca no mesmo ato para a mesma Etapa; o invariante de `test_invariantes_da_declaracao_unica.py` continua verde; a frase nomeia Etapa, falta, consumidor e etapa (`SC-280`)
- [ ] T033 [US1] Corrigir `backend/tests/unit/editais/test_etapas.py::test_a_pontuada_sem_nota_nenhuma_e_legitima` (~162-164): a legitimidade da `FR-066` vale para a Etapa **não** eliminatória; tornar a Etapa do caso não eliminatória e acrescentar o caso irmão — eliminatória, pontuada, sem nota → `stage_result_unreachable`

### c. A tela e a Retificação

- [ ] T034 [US1] `como-preencher` da etapa *Etapas* em `backend/processo_seletivo/interface/templates/interface/compor_etapas.html` (**EXISTENTE**, ~30-43): um par `<dt>`/`<dd>` para *Avaliações por inscrição* dizendo que mais de uma exige regra de combinação que o sistema não publica, e que a Etapa assim não se consolida. **Nada** no cartão `_etapa.html` (`FR-750`; memória *ajuda visível é proibida nos cartões*). Conferir `tests/test_vocabulario_da_composicao.py`
- [ ] T035 [US1] Interface em `backend/tests/interface/test_etapa_sem_resultado.py` (**NOVO**): pela composição, a Etapa eliminatória com duas avaliações → *"Impede"* na Revisão, na etapa *Etapas*, e a submissão recusada com a frase; trocar para uma → publica; a Etapa decisória não eliminatória fora de marco → *"Aviso"* e publica (`FR-748`); enumerada → *"Impede"*; o `como-preencher` traz a explicação
- [ ] T036 [US1] Retificação em `backend/tests/integration/publicacoes/test_advertencia_da_etapa_sem_resultado.py` (**NOVO**): Edital publicado como acervo com Etapa eliminatória de duas avaliações; uma Retificação que muda só uma data → aceita, e `advertencias_do_ato` traz `stage_without_result` — **na confirmação**, pela tela da Retificação, e não só na função (`FR-751`, `R-3`); uma Retificação que troca para uma avaliação → a advertência some
- [ ] T037 [US1] `make test-pg` — verde; recontar contra a `T002`

**Checkpoint**: o `RC-29` fecha; a consolidação continua recusando o acervo, e o gate recusa o novo.

---

## Phase 7: Fecho

- [ ] T038 A `SC-276` em `backend/tests/unit/editais/test_executaveis_continuam_publicaveis.py` (**NOVO**): caso parametrizado que roda `validate_for_publication`, no ato de publicação, sobre os rascunhos executáveis das fixtures — as três famílias da amostra real (as fixtures que a `T002` identificar para os Editais 35, 57 e o de 3 famílias), o sorteio do 77/2026 (`tests/fixtures/sorteio.py`) e o corte sem Etapa governada do 69/2026 (`complete_draft`, `tests/fixtures/edital.py`) — e afirma **zero** `stage_result_unreachable`, `stage_without_result` e `profile_without_cut_rule` (Cenário B)
- [ ] T039 [P] `specs/046-contrato-de-executabilidade/rastreabilidade.md` (**NOVO**): uma linha por requisito, `FR-746` a `FR-759` e `SC-275` a `SC-281`, com arquivo e caso — o `test_citacoes_de_requisito.py` cobra requisito a requisito
- [ ] T040 Percorrer pela tela os percursos 1 a 3 do [quickstart.md](quickstart.md), com as identidades segregadas, e registrar o resultado em `specs/046-contrato-de-executabilidade/antes-do-gate.md`
- [ ] T041 Registrar o fechamento: em `doc/auditoria-de-consolidacao-2026-09-26.md`, as linhas de `RC-29`, `RC-30`, `RC-32` e `RC-72` ganham a nota *"resolvido pela `046`"* com o PR — sem apagar o texto de 26/09; e a `D-G1`, em `doc/reavaliacao-ux-2026-09-18.md` §14-bis, ganha a nota de substituição pela `D-002` da `046`
- [ ] T042 `make lint check test-pg` — `ruff check` **e** `ruff format --check`; o total de passados maior que o da `T002`, os **11** pulados de sempre, `make preparar` em `34 de 34`

---

## Dependencies & Execution Order

```
T001 → T002 → T003 → T004
                       │
                       ├─► US3 (T005–T011)
                       ├─► US4 (T012–T017)          ← independente da US3 em arquivo
                       ▼
                    US2 (T018–T027)                  ← T018–T020 antes de T021 (portão 2)
                       ▼
                    US1 (T028–T037)                  ← T028–T030 antes de T031 (portão 2)
                       ▼
                    Fecho (T038–T042)
```

**US2 antes de US1, contra a prioridade**: as duas tocam `validation.py` e a suíte inteira; a `US2`
muda quatro fixtures, a `US1` muda uma fixture central e 33 arquivos. Entrar com a menor primeiro
deixa a recontagem da maior limpa.

### Dentro das fases

- **T005 → T006**; **T007**, **T008**, **T009** e **T010** são arquivos diferentes, mas todas
  dependem da T005.
- **T012** e **T015** levam `[P]`: configuração e o teste dela não encostam em `fontes/`.
- **T013 → T014 → T016**.
- **T018 → T019 → T020 → T021 → T022 → T023…T026**.
- **T028 → T029 → T030 → T031 → T032, T033** e **T034 → T035**; **T036** depois da T031.
- **T039** leva `[P]` contra a T040 e a T041.

### Oportunidades de paralelismo

Poucas, e é o esperado: três funções no mesmo arquivo e fixtures compartilhadas pela suíte inteira.
**US3 e US4** podem correr juntas em sessões separadas — não compartilham arquivo —, mas numa worktree
só, e com um banco de teste por sessão.

---

## Estratégia de entrega

**MVP**: a `US3` e a `US4` — pequenas, independentes, e cada uma fecha um achado (`RC-32`, `RC-72`)
sem tocar fixture.

**Depois**: a `US2` e a `US1`, nessa ordem, cada uma com as fixtures antes da regra e `make test-pg`
verde no fim.

**O que não se faz**:

- copiar os três predicados de `impedimento_da_regra` para `editais` — há uma regra, e ela é
  consultada;
- afrouxar a regra para a suíte passar — se um caso quebra, ou a fixture muda, ou o caso publica como
  acervo, e a razão fica escrita;
- corrigir a issue #117 — a `046` não precisa dela (`R-3`);
- apagar caso para ficar verde sem linha na `rastreabilidade.md`.
