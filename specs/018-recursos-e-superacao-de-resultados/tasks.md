---

description: "Task list for feature implementation"
---

# Tasks: Recursos e Superação de Resultados

**Input**: Design documents from `/specs/018-recursos-e-superacao-de-resultados/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/recurso.md](./contracts/recurso.md), [contracts/julgamento.md](./contracts/julgamento.md), [contracts/janela.md](./contracts/janela.md), [quickstart.md](./quickstart.md)

**Tests**: **sim, exigidos.** O Princípio V nomeia recursos, autorização, concorrência e
classificação entre o que precisa de cobertura específica, e esta feature entrega as quatro. Além
disso, o defeito mais perigoso da 018 **não produz erro**: sem filtro de vigência, o cálculo
classificatório colapsa dois Resultados do mesmo par e devolve ordem errada em silêncio. Um teste
que o denuncie é a primeira tarefa que importa.

**Organization**: por história de usuário. US1 a US4 são P1; US5, US6 e US7 são P2; US8 é P3.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência)
- **[Story]**: US1 a US8, conforme a spec

## Path Conventions

Aplicação web Django. Produção em `backend/processo_seletivo/`, testes em `backend/tests/`. Um app
nasce nesta feature — `recursos` —, as telas administrativas ficam em `interface` e as do candidato
em `portal`.

> **⚠️ A suíte precisa de PostgreSQL, e aqui são cinco motivos.** Sem `TEST_DB_ENGINE=postgresql`
> **e** `DB_USER` ela cai para SQLite **sem avisar**, e deixam de ser verificadas: a unicidade da
> raiz por par, a do sucessor, as triggers de imutabilidade, as três de coerência e o
> `select_for_update` que serializa julgar com emitir, publicar e consolidar. Rode como o
> [quickstart](./quickstart.md) manda, com `DB_NAME` próprio deste worktree. **Um PR verde em SQLite
> não prova nada do que esta feature promete** (T-014).

> **⚠️ Nada nesta feature altera linha gravada.** Superado e superador são igualmente imutáveis, e a
> política de papéis revoga `UPDATE` e `DELETE` do runtime. **Se alguma tarefa parecer pedir que
> `resultado_etapa_append_only` seja desligada, ela está errada** — é sinal de que alguém está
> corrigindo com `UPDATE` o que esta feature manda corrigir com linha nova (T-002).

> **⚠️ A ordem das migrations não é preferência, é dependência.**
> `resultados/0004 → recursos/0001 → resultados/0005`, com `classificacao/0004` depois de
> `recursos/0001`. A sucessão do Resultado cita `DecisaoRecurso`: os modelos de `recursos` **têm de
> existir antes**. É por isso que a fundação do app está na Phase 2, e não na história que o usa.

> **⚠️ `reproducao.py` não recebe filtro de vigência.** Ela lê os Resultados por `pk__in` dos ids
> gravados na proveniência, e é isso que mantém a IO-5 da 015 verdadeira. Acrescentar `vigentes` ali
> quebraria a reprodução histórica (T-004).

> **⚠️ A quarta espécie de decisão não se cumpre sozinha.** Só o ato de ordenação que **cita** a
> decisão quita a providência. "Publicar ato diferente" era a redação anterior, e quitava por
> acidente (T-015).

---

## Phase 1: Setup

- [ ] T001 Criar o app `recursos` com `apps.py`, `__init__.py`, `domain/` e `application/` em `backend/processo_seletivo/recursos/`
- [ ] T002 Registrar `"processo_seletivo.recursos"` em `INSTALLED_APPS` em `backend/config/settings/base.py`
- [ ] T003 [P] Criar os diretórios de teste `backend/tests/unit/recursos/` e `backend/tests/integration/recursos/` com `__init__.py`

---

## Phase 2: Foundational — a fundação persistente

**Bloqueia todas as histórias.** É a F0 do plano, e é a maior fatia da feature sem entregar nada
visível: a fundação de `recursos` e a sucessão do `ResultadoEtapa` precisam nascer juntas, porque a
chave estrangeira as amarra. Aqui também mora o risco silencioso — o filtro de vigência.

**Não entrega**: telas, comandos, autorização ou o papel `julgador`. Isso é das histórias seguintes.

### 2.1 Os modelos e as migrations

- [ ] T004 Criar `Recurso`, `JuizoDeAdmissibilidade` e `DecisaoRecurso` em `backend/processo_seletivo/recursos/models.py` conforme [data-model.md](./data-model.md) §2–§4, com `save` e `delete` que recusam alteração (FR-003, FR-031, FR-044, FR-046)
- [ ] T005 Criar `backend/processo_seletivo/recursos/migrations/0001_initial.py` com as três tabelas e as **12** constraints de [data-model.md](./data-model.md) §9 — incluindo `ck_recurso_objeto_unico`, que é a FR-001 e a FR-003 no banco, e `uq_recurso_por_publicacao`/`uq_recurso_por_resultado`, que são a FR-011 (FR-001, FR-006, FR-011, FR-044, FR-047)
- [ ] T006 Acrescentar a `backend/processo_seletivo/recursos/migrations/0001_initial.py` as **cinco** triggers de [data-model.md](./data-model.md) §10: três de imutabilidade e **duas** de coerência — `recurso_coerente` na tabela do `Recurso` e `decisao_recurso_coerente` na da `DecisaoRecurso`, porque uma trigger não valida outra tabela. Uma função SQL dedicada por trigger, no molde de `divulgacao/0001` (T-013, FR-046)
- [ ] T007 Acrescentar `resultado_anterior`, `motivo_da_superacao`, `decisao` e o valor `RECURSO` de `origem` a `ResultadoEtapa` em `backend/processo_seletivo/resultados/models.py`, com a FK declarada como *string* `"recursos.DecisaoRecurso"` — referência tardia, sem import circular (T-001, FR-051, FR-054)
- [ ] T008 Escrever `ck_resultado_origem` e `ck_resultado_completo_por_forma` em `backend/processo_seletivo/resultados/models.py` conforme a matriz de [data-model.md](./data-model.md) §6.1. **O ramo `AVALIACAO` não menciona `decisao`** — foi essa menção que tornou o sucessor por reavaliação impossível; quem amarra a decisão ao sucessor é `ck_sucessor_cita_decisao` (FR-052, FR-054, FR-057)
- [ ] T009 Criar `backend/processo_seletivo/resultados/migrations/0005_superacao.py` com `RemoveConstraint uq_resultado_inscricao_etapa` e as quatro constraints novas, **sem backfill e sem desligar `resultado_etapa_append_only`**; declarar a dependência de `recursos/0001` (FR-052, FR-053, FR-063)
- [ ] T010 Recriar a trigger `resultado_etapa_coerente` em `backend/processo_seletivo/resultados/migrations/0005_superacao.py`, por inteiro e com o nome preservado, com os ramos de [data-model.md](./data-model.md) §6.2 — inclusive a espécie da decisão citada: `CORRECAO_FIXADA` no sucessor por recurso, `REAVALIACAO_DETERMINADA` no sucessor por avaliação (FR-058, FR-060)
- [ ] T011 Criar `CumprimentoDeProvidencia` em `backend/processo_seletivo/classificacao/models.py` e a migration `backend/processo_seletivo/classificacao/migrations/0004_cumprimento.py`, com `UNIQUE(decisao)` e as duas triggers (T-015, FR-089)
- [ ] T012 Acrescentar `prazo_encerrado_declarado_em`, `prazo_encerrado_declarado_por` e `prazo_encerrado_fundamento` a `PublicacaoResultado` em `backend/processo_seletivo/divulgacao/models.py`, e a migration `backend/processo_seletivo/divulgacao/migrations/0002_declaracao.py` com `ck_declaracao_completa` (FR-085)

### 2.2 O filtro de vigência — o trabalho real, e o que quebra em silêncio

- [ ] T013 Criar o manager `vigentes` em `backend/processo_seletivo/resultados/managers.py` e ligá-lo em `ResultadoEtapa`, ao lado de `objects` — nomeado, e nunca substituindo o default, porque a reprodução histórica precisa ver os superados (T-004, FR-061)
- [ ] T014 Escrever o teste que denuncia o colapso em `backend/tests/unit/classificacao/test_calculo_vigencia.py` **antes** de corrigir: com dois Resultados do mesmo par, `calcular_ordem` produz ordem errada sem erro. É o teste de regressão mais importante da 018 (FR-061)
- [ ] T015 Corrigir `backend/processo_seletivo/classificacao/application/calculo.py`: filtro de vigência **e** `order_by` determinístico no queryset de Resultados, para que a ausência futura do filtro não volte a produzir ordem arbitrária em silêncio (FR-061)
- [ ] T016 Aplicar vigência aos quatro `Exists` da progressão em `backend/processo_seletivo/resultados/application/prontidao.py`, dobrando-a nas subconsultas correlacionadas já existentes, sem round-trip adicional (FR-061, FR-075)
- [ ] T017 Aplicar vigência a `habilitadas_em`, `eliminadas_ate`, `inscricoes_com_resultado`, `ha_resultado_em` e `resultados_da_etapa` em `backend/processo_seletivo/resultados/application/selectors.py` — consumindo o manager, sem redeclará-lo (FR-061)
- [ ] T018 Corrigir `contestacoes_supervenientes` em `backend/processo_seletivo/resultados/application/selectors.py`: a chave `(identity_subject, inscricao_id)` colide entre dois Resultados da mesma inscrição por avaliadores distintos, e um perde a marcação (FR-061)
- [ ] T019 [P] Aplicar vigência em `backend/processo_seletivo/avaliacoes/application/impedimento.py` (FR-061)
- [ ] T020 [P] Escrever o teste estrutural em `backend/tests/test_vigencia_do_resultado.py`: varre `ResultadoEtapa.objects` no código de aplicação e falha em uso não declarado, com duas exceções explícitas — `classificacao/application/reproducao.py` e a consulta do histórico do par (T-004, FR-062)
- [ ] T021 [P] Testar que a reprodução histórica não regrediu em `backend/tests/integration/classificacao/test_reproducao.py`: ato emitido antes do deferimento reproduz a ordem que constituiu, com as entradas de então (FR-062, SC-011)

### 2.3 Registros fora do app, e as provas de banco

- [ ] T022 [P] Acrescentar `recursos_recurso`, `recursos_juizodeadmissibilidade`, `recursos_decisaorecurso` e `classificacao_cumprimentodeprovidencia` a `TABELAS_APPEND_ONLY` em `backend/processo_seletivo/seguranca/papeis.py` (FR-063)
- [ ] T023 [P] Registrar `"recursos"` em `APPS`, as cinco triggers em `TRIGGERS_POR_APP["recursos"]` e as duas do cumprimento em `TRIGGERS_POR_APP["classificacao"]` em `backend/tests/migrations/test_migrations.py` — o teste estrutural só enxerga o que foi registrado (T-013)
- [ ] T024 [P] Criar as fixtures de recurso, admissibilidade e decisão em `backend/tests/fixtures/recursos.py`, no molde de `tests/fixtures/divulgacao.py` (T-014)
- [ ] T025 Testar as constraints de cadeia em `backend/tests/integration/resultados/test_superacao.py`: dois sucessores do mesmo superado são recusados por `uq_resultado_sucessor_unico`; duas raízes do mesmo par, por `uq_resultado_raiz_por_par`; sucessor sem decisão e raiz com decisão, por `ck_sucessor_cita_decisao` — exige PostgreSQL (FR-052, FR-053, FR-054)
- [ ] T026 Testar a matriz de origem em `backend/tests/integration/resultados/test_superacao.py`: as **quatro** linhas legítimas de [data-model.md](./data-model.md) §6.1 são aceitas — inclusive **o sucessor por avaliação, que é o caso que a redação anterior tornava impossível** — e as duas que não existem, raiz por recurso e sucessor por ocorrência, são recusadas (FR-055, FR-057, FR-068)
- [ ] T027 [P] Testar a imutabilidade nas **três camadas** em `backend/tests/integration/recursos/test_imutabilidade.py`: `save`/`delete` do modelo recusam; a trigger recusa mesmo quem tem privilégio; e o papel de runtime não consegue `UPDATE` nem `DELETE` nas quatro tabelas novas (FR-046, FR-063, SC-023)
- [ ] T028 [P] Testar a trigger de coerência do Resultado em `backend/tests/integration/resultados/test_superacao.py`: sucessor de outro par, sucessor cuja decisão é de espécie errada, sucessor anterior no tempo ao superado, e sucessor de quem já tem sucessor — cada um recusado (FR-053, FR-058, FR-060)

**Checkpoint**: as quatro migrations aplicam do zero e a partir da anterior; o teste estrutural
enxerga as sete triggers novas; o cálculo classificatório não colapsa; e a suíte inteira continua
verde em PostgreSQL.

---

## Phase 3: US1 — Ver o próprio Resultado da Etapa (P1)

**Meta**: o candidato consulta, dentro da própria Inscrição, o Resultado que a instituição registrou
para ele em cada Etapa cujo marco já foi divulgado.

**Teste independente**: publicado o marco que enumera a Etapa 1, a candidata eliminada nela — e
**fora** do universo do ato — vê a consequência e o motivo escritos, e não vê Resultado de terceiro.

- [ ] T029 [US1] Escrever `resultados_visiveis(inscricao)` em `backend/processo_seletivo/resultados/application/selectors.py`: publicações vigentes de marcos do Perfil, as Etapas que cada marco enumera **na versão que o ato cita**, e os Resultados vigentes da Inscrição nelas — em três consultas, usando `conteudos_das_versoes` (T-009, FR-014, FR-015, FR-018)
- [ ] T030 [US1] Acrescentar o bloco do Resultado da Etapa em `backend/processo_seletivo/portal/views.py::acompanhamento` e no template `backend/processo_seletivo/portal/templates/portal/acompanhamento.html`, com consequência, motivo e pontuação quando houver (FR-014, FR-016)
- [ ] T031 [US1] Exibir a correção quando o vigente for sucessor — que corrigiu o anterior, por qual decisão e quando — em `backend/processo_seletivo/portal/templates/portal/acompanhamento.html`, porque mostrar a nota nova sem explicar transforma a correção em erro aparente (FR-016)
- [ ] T032 [P] [US1] Testar a visibilidade em `backend/tests/portal/test_resultado_da_etapa.py`: sem publicação, nada aparece; com publicação vigente do marco, a eliminada na Etapa 1 vê o próprio Resultado; Etapa que nenhum marco publicado enumera não aparece (FR-014, FR-015, FR-018, SC-001)
- [ ] T033 [P] [US1] Testar a fronteira em `backend/tests/portal/test_resultado_da_etapa.py`: nenhum Resultado de terceiro, nenhuma Avaliação, nenhum parecer e nenhum nome de avaliador alcançáveis por caminho algum; e identificador manipulado devolve 404 uniforme (FR-017, FR-104, SC-021, SC-022)
- [ ] T034 [P] [US1] Testar o orçamento de consultas em `backend/tests/performance/test_resultado_da_etapa.py`: número constante entre 1 e N marcos (T-009)

**Checkpoint**: o E2E17-004 está fechado pela raiz — quem foi eliminado cedo deixa de receber
silêncio absoluto.

---

## Phase 4: US2 — Interpor recurso, receber protocolo e acompanhar (P1)

**Meta**: o candidato contesta o resultado divulgado ou o próprio Resultado de Etapa, e recebe um
protocolo que prova que interpôs.

**Teste independente**: a partir dos dois objetos visíveis, interpor com fundamentação, conferir o
protocolo, e verificar que a segunda interposição equivalente é recusada nomeando a primeira.

- [ ] T035 [P] [US2] Escrever o gerador de protocolo em `backend/processo_seletivo/recursos/domain/protocolo.py`, reusando o alfabeto de `inscricoes/domain/protocolo.py` com prefixo `REC-` — **sem duplicar a constante**, que divergiria em silêncio (T-012, FR-008)
- [ ] T036 [US2] Escrever o comando `interpor` em `backend/processo_seletivo/recursos/application/interpor.py`: titularidade, fundamentação obrigatória, revalidação da assinatura do objeto lido, reserva de idempotência, gravação da peça com a versão vigente e a janela quando computável (FR-004, FR-006, FR-009, FR-010, FR-024)
- [ ] T037 [US2] Escrever os seletores do titular em `backend/processo_seletivo/recursos/application/selectors.py`: recursos da Inscrição e a situação derivada de cada um, conforme [data-model.md](./data-model.md) §12 (FR-093, D-010)
- [ ] T038 [US2] Acrescentar as duas rotas de [contracts/recurso.md](./contracts/recurso.md) em `backend/processo_seletivo/portal/urls.py`
- [ ] T039 [US2] Escrever as views `recorrer` e `recurso` em `backend/processo_seletivo/portal/views.py`, atrás de `exigir_titularidade` (FR-004, FR-104)
- [ ] T040 [US2] Escrever os templates do formulário e do acompanhamento do recurso em `backend/processo_seletivo/portal/templates/portal/`, com a espécie da decisão em texto institucional e sem enum nem identificador técnico (FR-048, FR-093, SC-021)
- [ ] T041 [US2] Oferecer a ação **Recorrer** ao lado do objeto no acompanhamento, e **não** oferecê-la quando a interposição não é possível, em `backend/processo_seletivo/portal/templates/portal/acompanhamento.html` (FR-013)
- [ ] T042 [P] [US2] Testar a interposição em `backend/tests/integration/recursos/test_interpor.py`: nasce a peça com protocolo, instante, objeto atacado, versão e janela; fundamentação vazia é recusada; e a peça registra o ato que era vigente naquele instante (FR-006, FR-008, FR-024, SC-002)
- [ ] T043 [P] [US2] Testar a idempotência e a duplicidade em `backend/tests/integration/recursos/test_interpor.py`: a mesma chave devolve o desfecho da primeira; e a segunda interposição do mesmo titular contra o mesmo objeto — **pendente ou já decidida** — é recusada nomeando o protocolo, pela constraint; e a mesma chave com conteúdo diferente é conflito (FR-010, FR-011, FR-012, FR-097, FR-098, SC-003, SC-004)
- [ ] T044 [P] [US2] Testar a revalidação em `backend/tests/integration/recursos/test_interpor.py`: objeto superado entre a leitura e a confirmação recusa com `409` e informa o objeto vigente (FR-009, FR-100)
- [ ] T045 [P] [US2] Testar a autorização em `backend/tests/authorization/test_recurso_do_candidato.py`: quem não é titular recebe 404 uniforme na interposição e na consulta; o protocolo não confere acesso (FR-004, FR-104)
- [ ] T046 [P] [US2] Testar os dois objetos em `backend/tests/integration/recursos/test_interpor.py`: recurso contra a publicação e recurso contra o `ResultadoEtapa` percorrem o **mesmo** fluxo e produzem a mesma espécie de peça (FR-002)

**Checkpoint**: o candidato tem por onde recorrer, e o Edital deixa de prometer o que o produto não
entrega.

---

## Phase 5: US3 — Admitir ou inadmitir, e julgar com imparcialidade (P1)

**Meta**: a autoridade com capacidade própria vê os recursos recebidos, decide a admissibilidade e
julga o mérito com motivação — e quem produziu o ato atacado não decide sobre ele.

**Teste independente**: conceder a capacidade a duas pessoas, uma delas a que consolidou o Resultado
atacado; verificar que a segunda é recusada nas duas operações.

- [ ] T047 [P] [US3] Acrescentar o papel `julgador` com a capacidade `recurso:julgar` em `backend/processo_seletivo/interface/identidade.py` — papel próprio, porque cada papel existente concederia julgamento a quem tende a estar impedido (T-005, FR-037, FR-038)
- [ ] T048 [US3] Escrever as cinco perguntas do impedimento em `backend/processo_seletivo/recursos/domain/elegibilidade.py`, conforme [contracts/julgamento.md](./contracts/julgamento.md) §1 — reusando o `Impedimento` da 012, sem criar segundo conceito (T-006, FR-039, FR-040)
- [ ] T049 [US3] Escrever o comando `admitir` em `backend/processo_seletivo/recursos/application/admitir.py`: `require_permission` fora da transação, `select_for_update` no Processo, autorização e impedimento reavaliados **depois** do bloqueio, reserva, gravação do juízo motivado (FR-032, FR-041, FR-043, FR-096)
- [ ] T050 [US3] Escrever os seletores administrativos em `backend/processo_seletivo/recursos/application/selectors.py`: recursos por Edital com a situação derivada e a tempestividade, **sem consulta de impedimento por linha** (T-006, FR-031)
- [ ] T051 [US3] Acrescentar as quatro rotas de [contracts/julgamento.md](./contracts/julgamento.md) em `backend/processo_seletivo/interface/urls.py`
- [ ] T052 [US3] Escrever as views da lista e da peça em `backend/processo_seletivo/interface/views.py`, com a proveniência da FR-092 e o impedimento nomeado antes de qualquer botão (FR-042, FR-092)
- [ ] T053 [US3] Escrever os templates da lista e da tela do recurso em `backend/processo_seletivo/interface/templates/interface/`, com confirmação que declara o alcance antes do ato
- [ ] T054 [P] [US3] Testar o impedimento em `backend/tests/authorization/test_julgamento_de_recurso.py`: quem concluiu a Avaliação fonte, consolidou o Resultado, constatou a Ocorrência, emitiu o ato ou publicou o resultado é recusado nas duas operações; e quem tem `Impedimento` na Inscrição também (FR-039, FR-040, FR-041, SC-005)
- [ ] T055 [P] [US3] Testar a capacidade em `backend/tests/authorization/test_julgamento_de_recurso.py`: sem `recurso:julgar` é 403 — **inclusive** para o presidente da comissão —, e a lista não é alcançável (FR-037, FR-038, SC-006)
- [ ] T056 [P] [US3] Testar a admissibilidade em `backend/tests/integration/recursos/test_admitir.py`: o juízo nasce motivado nas duas direções, com autor e instante; motivo vazio é recusado; o segundo juízo é recusado pela constraint; julgar o não admitido é recusado; e a mesma chave repetida devolve o desfecho da primeira (FR-031, FR-032, FR-036, FR-097)
- [ ] T057 [P] [US3] Testar a tempestividade em `backend/tests/integration/recursos/test_admitir.py`: sem janela estruturada, ela é juízo humano no motivo; com janela estruturada, ela **não** é matéria de admissibilidade, porque a interposição já a impediu (FR-033, FR-034, FR-035)

- [ ] T058 [P] [US3] Testar a proveniência administrativa em `backend/tests/interface/test_proveniencia_do_recurso.py`: a partir da tela do recurso, a administração reconstrói **em uma única jornada** a lista inteira da FR-092 — quem interpôs, qual Inscrição, qual objeto, qual era o ato vigente, sob qual versão, quando, se dentro da janela, quem admitiu e por quê, quem decidiu e por quê, qual efeito, qual ato superado e qual sucessor nasceu — sem banco e sem shell (FR-092, SC-020)

**Checkpoint**: a instituição julga com autoridade própria, e a imparcialidade deixa de ser promessa.

---

## Phase 6: US4 — Deferir fixando a correção (P1)

**Meta**: o julgador defere declarando a consequência e, quando aplicável, a conclusão corrigida; o
Resultado sucessor nasce na mesma transação, e o anterior permanece íntegro.

**Teste independente**: deferir sobre um Resultado que eliminava a inscrição; conferir que o
anterior permanece, que o sucessor é o vigente, que o ato ficou obsoleto e que a publicação passou a
ser recusada com o caminho nomeado.

- [ ] T059 [US4] Escrever a derivação da consequência em `backend/processo_seletivo/recursos/domain/consequencia.py`, a partir da conclusão fixada e da regra publicada da Etapa, sob a versão que a decisão cita — **nunca digitada livremente**, que permitiria declarar `HABILITADA` com nota abaixo da mínima (FR-059)
- [ ] T060 [US4] Escrever a comparação de piora em `backend/processo_seletivo/recursos/domain/pejus.py`: consequência e pontuação, **nunca posição** (FR-070, FR-071, FR-074)
- [ ] T061 [US4] Escrever o comando `julgar` em `backend/processo_seletivo/recursos/application/julgar.py`, na ordem exata de [contracts/julgamento.md](./contracts/julgamento.md) §5, com as quatro espécies e a superação do `CORRECAO_FIXADA` **na mesma transação**; a quarta espécie **nomeia** a providência na motivação e não a executa (FR-044, FR-045, FR-047, FR-049, FR-056)
- [ ] T062 [US4] Escrever a view e o template do julgamento em `backend/processo_seletivo/interface/`, com as quatro espécies, a motivação obrigatória e a assinatura do Resultado vigente lido (FR-045, FR-100)
- [ ] T063 [US4] Escrever a consulta do histórico do par em `backend/processo_seletivo/resultados/application/selectors.py` — a segunda exceção declarada do teste estrutural de T020 —, com os dois Resultados em ordem, motivo, autor, instante e a decisão que autorizou (FR-064, T-004)
- [ ] T064 [US4] Nomear a causa `participante reingressou` na divergência de obsolescência em `backend/processo_seletivo/classificacao/domain/universo.py` e na tela do marco (FR-078)
- [ ] T065 [P] [US4] Testar a atomicidade em `backend/tests/integration/recursos/test_julgar.py`: decisão e sucessor nascem juntos; qualquer invariante que falhe derruba a transação inteira — não fica decisão sem efeito nem efeito sem decisão (FR-056, SC-007)
- [ ] T066 [P] [US4] Testar o sucessor em `backend/tests/integration/recursos/test_julgar.py`: origem em recurso, sem citar Avaliação, citando a decisão; o anterior permanece com pontuação, consequência e motivo intactos (FR-051, FR-057, FR-058, SC-007)
- [ ] T067 [P] [US4] Testar o desfecho sem grandeza em `backend/tests/integration/recursos/test_julgar.py`: recurso contra Ocorrência deferido produz sucessor sem forma, sem pontuação e sem sentido (FR-059)
- [ ] T068 [P] [US4] Testar a vedação de piora em `backend/tests/integration/recursos/test_pejus.py`: correção que baixaria a pontuação ou eliminaria resulta em indeferimento, e **nenhum** sucessor nasce; e a queda de posição por ato alheio **não** é piora (FR-070, FR-071, FR-072, SC-008)
- [ ] T069 [P] [US4] Testar a concorrência em `backend/tests/integration/recursos/test_concorrencia.py`: dois deferimentos sobre o mesmo Resultado produzem **um** sucessor, resolvidos pela constraint e não por leitura prévia; dois julgadores no mesmo recurso produzem **uma** decisão; e o Resultado alterado entre leitura e confirmação recusa com `409` — tudo por revisão otimista, idempotência e constraint, sem mecanismo novo; exige PostgreSQL (FR-047, FR-099, FR-100, FR-101)
- [ ] T070 [P] [US4] Testar a cadeia a jusante em `backend/tests/integration/classificacao/test_obsolescencia_por_recurso.py`: superado o Resultado, o ato fica obsoleto com a causa nomeada, a publicação daquele ato é recusada com o caminho, e **nenhum** ato ou publicação é emitido ou alterado automaticamente (FR-080, FR-108, SC-010)
- [ ] T071 [P] [US4] Testar a trilha em `backend/tests/integration/recursos/test_julgar.py`: interposição, admissibilidade, decisão e superação aparecem na trilha existente, com ator, entidade, instante e versão, **sem** copiar fundamentação nem pontuação (FR-094, FR-095)

**Checkpoint**: o ciclo central fecha — recorrer, julgar, corrigir sem reescrever, e a cadeia a
jusante reage sozinha.

---

## Phase 7: US5 — Deferir determinando reavaliação (P2)

**Meta**: a decisão registra a determinação sem antecipar um resultado que ainda não existe, e a
consolidação posterior produz o sucessor.

**Teste independente**: deferir determinando reavaliação; conferir que nenhum sucessor nasceu, que a
Etapa mostra a pendência nomeada, e que a consolidação da nova Avaliação produz o sucessor citando a
decisão.

- [ ] T072 [US5] Escrever a pendência derivada de reavaliação em `backend/processo_seletivo/recursos/application/selectors.py`: decisão dessa espécie sem sucessor do par posterior a ela — **derivada, nunca coluna** (FR-066, D-010)
- [ ] T073 [US5] Acrescentar o estado `reavaliação determinada` à prontidão em `backend/processo_seletivo/resultados/application/prontidao.py`, de modo que a inscrição apareça como pendência nomeada e **não** como já consolidada (FR-067)
- [ ] T074 [US5] Escrever a exceção única em `backend/processo_seletivo/resultados/application/consolidacao.py`: a consolidação praticada em cumprimento de decisão que determinou reavaliação cria o **sucessor**, citando a decisão; fora dela, consolidar continua recusando o par que já tem Resultado vigente (FR-055, FR-068)
- [ ] T075 [US5] Aplicar a vedação de piora na consolidação em cumprimento, em `backend/processo_seletivo/resultados/application/consolidacao.py`: a nova Avaliação é **registrada**, e o seu Resultado não é consolidado como sucessor quando pior que o `resultado_protegido` (FR-073)
- [ ] T076 [P] [US5] Testar que a decisão não antecipa em `backend/tests/integration/recursos/test_reavaliacao.py`: deferida a reavaliação, zero sucessores existem até a consolidação (FR-065, FR-069, SC-009)
- [ ] T077 [P] [US5] Testar a pendência e a distribuição em `backend/tests/integration/resultados/test_reavaliacao.py`: a Etapa mostra a pendência nomeada, e a inscrição é distribuível, avaliável e consolidável pelas operações que já existem (FR-067)
- [ ] T078 [P] [US5] Testar a garantia estrutural em `backend/tests/integration/resultados/test_reavaliacao.py`: quem concluiu a Avaliação original **não** consegue concluir a reavaliação, por `uq_avaliacao_concluida_por_pessoa` — é garantia que já existe, e o teste a registra como comportamento correto (FR-068)
- [ ] T079 [P] [US5] Testar a porta de trás em `backend/tests/integration/recursos/test_pejus.py`: reavaliação que produziria resultado pior é registrada como Avaliação e **recusada** na consolidação, nomeando a vedação; nenhum sucessor pior nasce por caminho algum (FR-073, SC-008)

**Checkpoint**: a *non reformatio in pejus* é íntegra — não é contornável pela reavaliação ordenada.

---

## Phase 8: US8 — A reabilitação aparece na operação (P3)

**Meta**: uma inscrição reabilitada por recurso aparece nomeada nas Etapas seguintes, e a publicação
do marco é impedida enquanto ela estiver pendente.

**Teste independente**: deferir recurso que reabilita uma inscrição eliminada na Etapa 1, com a
Etapa 2 já consolidada para todos; abrir a Etapa 2, a tela do marco e a prévia de publicação.

> **Fora da ordem de prioridade, e por dependência.** A US8 é P3, mas entra antes das US7 e US6
> porque a pendência reaberta é **um dos seis fatos** que a definitividade apura (FR-082): sem ela,
> a US7 nasceria incompleta.

- [ ] T080 [US8] Escrever a derivação `reabilitada por recurso` em `backend/processo_seletivo/resultados/application/selectors.py`: Resultado vigente que é sucessor, com consequência habilitante — derivada, sem estado de reintegração (FR-076, D-010)
- [ ] T081 [US8] Nomear a linha reaberta na Mesa e no painel da Etapa em `backend/processo_seletivo/interface/templates/interface/`, com a data do deferimento (FR-077)
- [ ] T082 [US8] Acrescentar o impedimento `publication_reentry_pending` em `backend/processo_seletivo/divulgacao/domain/publicabilidade.py`, com o caminho nomeado (FR-079)
- [ ] T083 [P] [US8] Testar a progressão retroativa em `backend/tests/integration/resultados/test_progressao_retroativa.py`: removida a eliminação vigente, a inscrição reaparece como pendente em **todas** as Etapas seguintes, e é distribuível, avaliável e consolidável (FR-075, FR-076, SC-012)
- [ ] T084 [P] [US8] Testar a guarda em `backend/tests/integration/divulgacao/test_publicabilidade_por_recurso.py`: enquanto houver pendência reaberta que afete o marco, publicar é recusado com a causa nomeada; consolidado o Resultado, o impedimento desaparece (FR-079, SC-013)
- [ ] T085 [P] [US8] Testar os avisos em `backend/tests/interface/test_reabilitacao.py`: a linha aparece nomeada na Mesa e no painel, e a divergência do marco diz `participante reingressou` (FR-077, FR-078)

**Checkpoint**: o efeito da progressão retroativa deixa de ser descoberto por acaso.

---

## Phase 9: US7 — Publicar como definitivo com lastro (P2)

**Meta**: o sistema impede chamar de definitivo um resultado ainda em disputa, e exige declaração
expressa quando o prazo não é computável.

**Teste independente**: tentar publicar como definitivo em cada um dos casos impeditivos; resolver
cada um e conferir que a publicação passa a ser permitida.

- [ ] T086 [US7] Fazer `aferir()` receber a **natureza pretendida** em `backend/processo_seletivo/divulgacao/domain/publicabilidade.py` e em `backend/processo_seletivo/divulgacao/application/publicar.py` (FR-081)
- [ ] T087 [US7] Escrever os fatos 1, 2 e 3 em `backend/processo_seletivo/divulgacao/domain/publicabilidade.py`: recurso pendente pertinente, reavaliação não cumprida e providência não cumprida, com os códigos e caminhos de [contracts/janela.md](./contracts/janela.md) §3 (FR-082, FR-084)
- [ ] T088 [US7] Escrever a pertinência ao marco em `backend/processo_seletivo/recursos/application/selectors.py`: alcança o recurso contra a publicação **e** o recurso contra `ResultadoEtapa` de Etapa que o marco enumera — sem a segunda, o recurso individual é a porta por onde a definitiva escapa (FR-084)
- [ ] T089 [US7] Oferecer as decisões pendentes do marco na emissão do ato e gravar a citação em `backend/processo_seletivo/classificacao/application/emissao.py`, na mesma transação do ato (T-015, FR-089)
- [ ] T090 [US7] Exigir e gravar a declaração expressa em `backend/processo_seletivo/divulgacao/application/publicar.py` e no template da prévia — **somente** quando não há janela computável, e recusada quando há (FR-085, FR-086)
- [ ] T091 [US7] Apresentar a definitiva que corrige outra pela causa, e a vigente como vigente, em `backend/processo_seletivo/portal/templates/portal/resultado.html` e no documento (FR-088, FR-090)
- [ ] T092 [P] [US7] Testar os seis fatos em `backend/tests/integration/divulgacao/test_definitividade.py`: cada um recusa a `DEFINITIVA` com o código próprio, e a `PRELIMINAR` continua possível em todos (FR-082, FR-083, SC-017)
- [ ] T093 [P] [US7] Testar o cumprimento por citação em `backend/tests/integration/divulgacao/test_definitividade.py`: ato sucessor que **não** cita a decisão deixa a pendência aberta; ato que a cita cumpre; um ato cita duas decisões; e `UNIQUE(decisao)` garante que ela é cumprida uma vez (FR-089, SC-017)
- [ ] T094 [P] [US7] Testar a declaração em `backend/tests/integration/divulgacao/test_definitividade.py`: sem janela computável ela é exigida e gravada com autor, instante e texto; com janela computável ela é recusada (FR-085, FR-086, SC-018)
- [ ] T095 [P] [US7] Testar que a publicação histórica não é tocada em `backend/tests/integration/divulgacao/test_definitividade.py`: nenhuma publicação anterior é alterada e nenhum documento é regenerado pela 018 (FR-091)
- [ ] T096 [P] [US7] Testar o vocabulário em `backend/tests/portal/test_definitiva_retificada.py`: a definitiva que corrige outra é apresentada pela causa, **sem natureza nova**, e a vigente diz que é a vigente (FR-087, FR-088, FR-090, SC-019)

**Checkpoint**: o E2E17-005 está fechado — "definitivo" deixa de ser escolha livre de um seletor.

---

## Phase 10: US6 — Declarar, exibir e aplicar a janela recursal (P2)

**Meta**: o Edital declara que um marco admite recurso e por quanto tempo; o candidato vê o prazo e
o sistema o aplica — e, não declarando, ninguém inventa prazo.

**Teste independente**: declarar a janela num marco, publicar, interpor dentro e depois do prazo; e
repetir tudo num Edital publicado antes do incremento.

> **Última fatia, de propósito.** É a única com custo de conteúdo publicado, e a única que pode ser
> adiada sem desmontar as demais: sem ela, a tempestividade continua sendo juízo de admissibilidade
> motivado, que é a degradação que a decisão institucional declara.

- [ ] T097 [US6] Subir `ZONA` de `interface/forms.py` e `interface/retificacao.py` para `backend/processo_seletivo/shared/tempo.py`, e fazer os dois importá-la — a contagem é domínio, e domínio não importa de `interface` (T-008)
- [ ] T098 [US6] Elevar `SCHEMA_VERSION` para 8 em `backend/processo_seletivo/shared/canonical.py`, com o comentário que declara o que a ausência significa (FR-029)
- [ ] T099 [US6] Escrever `DEGRAUS_DE_MARCO` e `elevar_marco` em `backend/processo_seletivo/publicacoes/domain/elevacao.py` — o terceiro nível, simétrico a `elevar_etapa` e `elevar_perfil` —, e alcançar o endereço do marco em `elevar_alteracoes` (T-007, FR-029)
- [ ] T100 [US6] Escrever `janela.py` em `backend/processo_seletivo/recursos/domain/`: função pura que devolve abertura e encerramento a partir da publicação âncora e da norma, excluindo o dia do começo e incluindo o do vencimento, na zona institucional (FR-022, FR-023, FR-024)
- [ ] T101 [US6] Escrever a âncora e a reabertura em `backend/processo_seletivo/recursos/domain/janela.py`: a publicação que divulgou **pela primeira vez** o ato que publica; comparação por identidade do ato, e não por hash do conteúdo (FR-025)
- [ ] T102 [US6] Validar `appealWindow` na publicação em `backend/processo_seletivo/editais/domain/perfis.py`: unidade fora de `DIAS_CORRIDOS`, `admits` sem duração e duração não positiva, cada uma com a mensagem de [contracts/janela.md](./contracts/janela.md) §1 (FR-020, FR-021)
- [ ] T103 [US6] Escrever os três campos da janela no assistente do marco em `backend/processo_seletivo/interface/forms.py` e no template correspondente (FR-030)
- [ ] T104 [US6] Imprimir a frase normativa da janela no documento publicado em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` (FR-030)
- [ ] T105 [US6] Verificar o endereçamento por Retificação de `appealWindow` em `backend/processo_seletivo/publicacoes/domain/colecoes.py`; recusando `changes.py` o objeto aninhado, declará-lo em `COLECOES_ATOMICAS` (T-007, FR-030)
- [ ] T106 [US6] Aplicar a janela na interposição em `backend/processo_seletivo/recursos/application/interpor.py`, e exibir os dois instantes ao candidato em `backend/processo_seletivo/portal/templates/portal/` (FR-026, FR-024)
- [ ] T107 [US6] Acrescentar o fato 4 — janela aberta — em `backend/processo_seletivo/divulgacao/domain/publicabilidade.py` (FR-082)
- [ ] T108 [P] [US6] Testar a contagem em `backend/tests/unit/recursos/test_janela.py`: exclui o dia do começo, inclui o do vencimento, fecha ao fim do último dia na zona institucional, e não prorroga (FR-023, SC-014)
- [ ] T109 [P] [US6] Testar a reabertura em `backend/tests/unit/recursos/test_janela.py`: publicação de ato diferente abre janela nova; publicação que só muda a natureza do mesmo ato **não** abre (FR-025)
- [ ] T110 [P] [US6] Testar a retrocompatibilidade em `backend/tests/contract/test_elevacao_degrau_8.py`: Edital publicado antes do degrau eleva sem inventar janela, continua retificável e publicável, e a ausência significa **janela não declarada** (FR-029, SC-016)
- [ ] T111 [P] [US6] Testar a aplicação em `backend/tests/integration/recursos/test_janela.py`: dentro do prazo a interposição é aceita e registra que estava dentro; depois do prazo é recusada citando a norma, a abertura e o encerramento; e a ação não é oferecida na tela (FR-026, SC-014)
- [ ] T112 [P] [US6] Testar os vários marcos em `backend/tests/integration/recursos/test_janela.py`: enumerando dois marcos a mesma Etapa, a interposição é possível enquanto **qualquer** janela estiver aberta (FR-027)
- [ ] T113 [P] [US6] Testar a ausência em `backend/tests/integration/recursos/test_janela.py`: sem declaração, zero prazos exibidos ou aplicados, e a interposição permanece possível enquanto o objeto for vigente (FR-028, SC-015)

**Checkpoint**: a tempestividade passa a ser regra reproduzível onde a norma a declarou, e continua
sendo juízo humano onde ela não a declarou.

---

## Phase 11: Polish & Cross-Cutting

- [ ] T114 [P] Testar os limites declarados em `backend/tests/integration/recursos/test_limites.py`: nenhuma superfície aceita terceiro interessado, procurador ou representação; a peça **não** aceita anexos; nenhum ato de divulgação de `ResultadoEtapa` nasce; e nenhuma espécie, estado ou taxonomia além das declaradas existe (FR-005, FR-007, FR-019, FR-050)
- [ ] T115 [P] Testar que a 018 não altera agregado existente em `backend/tests/integration/recursos/test_limites.py`: conteúdo, autoria e estado de Avaliação, Atribuição, Impedimento, `AtoDeOrdenacao`, `PosicaoNaOrdem` e `PublicacaoResultado` permanecem intactos (FR-107)
- [ ] T116 [P] Melhorar a recusa de reabertura de Avaliação em `backend/processo_seletivo/avaliacoes/application/avaliacao.py`: a mensagem deixa de prometer uma "anulação" que não existe e passa a nomear o ato que existe (FR-111)
- [ ] T117 [P] Registrar a não regressão por identidade de teste em `specs/018-recursos-e-superacao-de-resultados/tasks.md` e na descrição do PR: toda asserção alterada da 013, 015 e 017 enumerada uma a uma, e nenhum teste removido (FR-110)
- [ ] T118 [P] Verificar os orçamentos de consulta da 011, 012 e 015 em `backend/tests/performance/`: o filtro de vigência não pode ter acrescentado round-trip (FR-061)
- [ ] T119 [P] Testar a proteção de dados em `backend/tests/portal/test_recurso_privacidade.py`: fundamentação e decisão acessíveis ao titular, ao julgador e à auditoria, e a mais ninguém; respostas não armazenáveis pelo navegador (FR-102, FR-103, FR-105)
- [ ] T120 [P] Testar que nada é notificado em `backend/tests/integration/recursos/test_julgar.py`: nenhuma mensagem é disparada em interposição, admissibilidade ou decisão (FR-109)
- [ ] T121 Executar o roteiro do [quickstart.md](./quickstart.md) de ponta a ponta pelo navegador, alternando os atores, e registrar as evidências (FR-106, SC-024)

---

## Dependencies

```text
Setup (T001–T003)
   └─▶ Foundational (T004–T028)          ← bloqueia TUDO
          ├─▶ US1 (T029–T034)            independente
          ├─▶ US2 (T035–T046)            independente
          ├─▶ US3 (T047–T058)            precisa de US2 (há peça a julgar)
          │      └─▶ US4 (T059–T071)     precisa de US3 (há juízo de admissibilidade)
          │             ├─▶ US5 (T072–T079)   precisa de US4 (a espécie existe)
          │             └─▶ US8 (T080–T085)   precisa de US4 (há sucessor habilitante)
          │                    └─▶ US7 (T086–T096)  precisa de US5 e US8 (dois dos seis fatos)
          │                           └─▶ US6 (T097–T113)
          └─▶ Polish (T114–T121)
```

**A Foundational é indivisível.** T004–T012 formam uma unidade: `resultados/0005` cita
`DecisaoRecurso`, e as migrations aplicam na ordem do grafo. Tentar fatiar isso reproduz o defeito
que a revisão do plano encontrou.

**T014 vem antes de T015**, e é deliberado: o teste que denuncia o colapso precisa falhar antes de o
filtro existir. É a única prova de que ele estava lá.

**US6 por último** é decisão do plano, e não dependência técnica — ela só depende da Foundational.
Adiantá-la é possível; adiá-la é o que permite fatiar a feature.

## Parallel opportunities

- **Foundational**: T019–T024 tocam arquivos distintos; T025–T028 compartilham arquivos de teste por
  agregado, e são paralelas entre agregados
- **US1**: T032, T033 e T034 são arquivos distintos
- **US2**: T042 a T046 — T042, T043 e T044 compartilham `test_interpor.py`, paralelas só se escritas
  em conjunto; T045 e T046 são independentes
- **US3**: T054 e T055 compartilham arquivo; T056 e T057 compartilham outro; T047 e T058 são
  independentes
- **US4**: T065 a T071 — T065, T066, T067 e T071 compartilham `test_julgar.py`; T068, T069 e T070 são
  arquivos distintos
- **US5**: T076 a T079 são três arquivos distintos
- **US8**: T083, T084 e T085 são independentes
- **US7**: T092 a T095 compartilham `test_definitividade.py`; T096 é independente
- **US6**: T108 e T109 compartilham arquivo; T110 é independente; T111, T112 e T113 compartilham
  outro
- **Polish**: T114 a T120 são independentes

## Implementation Strategy

**MVP**: Setup + Foundational + US1 + US2 + US3 + US4. Nesse ponto o ciclo central fecha — o
candidato vê, recorre, a instituição julga com imparcialidade, e a correção produz efeito sem
reescrever nada. É a resposta à pergunta que a feature existe para responder.

**Incremento seguinte**: US5 e US8. A primeira torna a *non reformatio* íntegra; a segunda torna o
efeito da progressão retroativa visível, e sem ela ele é descoberto por acaso.

**Depois**: US7, que fecha o E2E17-005.

**Por último**: US6, que é a única com custo de conteúdo publicado.

**Se a feature precisar ser fatiada**, o corte é antes da US6, e a degradação está declarada na
spec: a tempestividade continua sendo juízo de admissibilidade motivado.

## Notes

- [P] = arquivos diferentes, sem dependência
- [Story] mapeia a tarefa para a história, e a citação do requisito em cada tarefa é o que sustenta
  a rastreabilidade que o Princípio V cobra entre spec, plano e tarefas
- Verifique que o teste falha antes de implementar — em T014 isso não é hábito, é o requisito
- Commit por tarefa ou grupo lógico
- **A suíte precisa de PostgreSQL.** T025, T026, T027, T028 e T069 verificam garantias que só
  existem lá, e são puladas em silêncio sob SQLite
