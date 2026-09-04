---

description: "Task list for feature implementation"
---

# Tasks: Ordenação e Classificação

**Input**: Design documents from `/specs/015-ordenacao-e-classificacao/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/marco.md](./contracts/marco.md), [contracts/ordenacao.md](./contracts/ordenacao.md), [quickstart.md](./quickstart.md)

**Tests**: **sim, exigidos.** O Princípio V nomeia pontuação, autorização e concorrência entre o que
precisa de cobertura específica, e esta feature entrega as três. E a revisão do plano encontrou
quatro defeitos que só teste ou leitura de código denunciariam — o ato mutável numa tabela sem
privilégio de `UPDATE`, o cenário de não recomputabilidade inalcançável, o teto de tempo provado por
contagem de consultas e a reordenação de critérios sem alvo endereçável. Cada um tem tarefa própria,
nomeada pelo defeito.

**Organization**: por história de usuário, na ordem das cinco fatias da §Fases do plano. US1 e US2
são P1; US3 e US4 são P2; US5 é P3.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência)
- **[Story]**: US1 a US5, conforme a spec

## Path Conventions

Aplicação web Django. Produção em `backend/processo_seletivo/`, testes em `backend/tests/`. Um app
nasce nesta feature — `classificacao` —, e as telas ficam em `interface`.

> **⚠️ A suíte precisa de PostgreSQL, e aqui são cinco motivos.** Sem `TEST_DB_ENGINE=postgresql` ela
> cai para SQLite **sem avisar**, e deixam de ser verificadas: a unicidade parcial da raiz, a
> unicidade do sucessor, a trigger append-only, a trigger de coerência e o `select_for_update`
> herdado de `comando_de_comissao`. Rode como o [quickstart](./quickstart.md) manda, com `DB_NAME`
> próprio deste worktree.

> **⚠️ A elevação canônica sobe UMA vez, e carrega três mudanças.** Marco, fatos declarados (D-2) e
> teto (D-3) entram na mesma versão 7. Subir a versão com uma e acrescentar outra depois produziria
> snapshots de versão 7 com e sem a propriedade — é exatamente o que `canonical.py:7-10` proíbe.

> **⚠️ Nada nesta feature altera linha gravada.** O ato é append-only nas três camadas, e a política
> de papéis **revoga `UPDATE` e `DELETE`** do runtime (`seguranca/papeis.py:129`). Toda sucessão é
> linha nova. Se alguma tarefa parecer pedir um `UPDATE`, ela está errada.

> **⚠️ Uma lacuna declarada:** D-2 e D-3 entraram nesta feature pela decisão de leva, mas a spec
> **não tem história de usuário** para a jornada do candidato preenchendo fatos declarados. Elas
> estão na Foundational como pré-requisito bloqueante de US2. Se a jornada do candidato precisar ser
> demonstrável nesta entrega, a spec precisa de uma US nova antes da implementação.

---

## Phase 1: Setup

- [ ] T001 Criar o app `classificacao` com `apps.py`, `__init__.py`, `domain/` e `application/` em `backend/processo_seletivo/classificacao/`
- [ ] T002 Registrar o app em `INSTALLED_APPS` em `backend/processo_seletivo/settings.py`
- [ ] T003 [P] Criar os diretórios de teste `backend/tests/unit/classificacao/` e `backend/tests/integration/classificacao/` com `__init__.py`

---

## Phase 2: Foundational — a leva normativa (bloqueia todas as histórias)

**A elevação e as duas dependências de conteúdo. Nenhuma história começa antes daqui.**

- [ ] T004 Elevar `SCHEMA_VERSION` de 6 para 7 e registrar o incremento no bloco de história em `backend/processo_seletivo/shared/canonical.py`
- [ ] T005 Acrescentar o degrau `7` a `DEGRAUS` em `backend/processo_seletivo/publicacoes/domain/elevacao.py`, com a coleção nova elevando para lista vazia
- [ ] T006 Estender `elevar()` para descer até `profiles` em `backend/processo_seletivo/publicacoes/domain/elevacao.py` — hoje ela só reescreve `conteudo["stages"]`, e esta é a primeira elevação aninhada
- [ ] T007 Teste: conteúdo v6 publicado continua retificável depois da elevação, em `backend/tests/integration/publicacoes/test_elevacao_de_versao.py`
- [ ] T008 [P] Declarar as coleções novas em `COLECOES_COM_CHAVE` em `backend/processo_seletivo/publicacoes/domain/colecoes.py`
- [ ] T009 [P] Modelo `FatoDeclarado` (D-2) em `backend/processo_seletivo/editais/models/perfis.py`, com identidade estável e tipo restrito a data e inteiro
- [ ] T010 [P] Campo `max_inscricoes_por_candidato` (D-3), anulável, em `backend/processo_seletivo/editais/models/perfis.py`
- [ ] T011 Migration de `editais` com `FatoDeclarado`, o teto e as unicidades, em `backend/processo_seletivo/editais/migrations/`
- [ ] T012 Emitir `declaredFacts` e `maxInscricoesPorCandidato` no snapshot em `backend/processo_seletivo/publicacoes/application/publish_edital.py`
- [ ] T013 Congelar os fatos na **submissão**, contra a `versao_aceita`, em `backend/processo_seletivo/inscricoes/` — nunca na abertura do rascunho
- [ ] T014 Migration de `inscricoes` com os valores congelados, em `backend/processo_seletivo/inscricoes/migrations/`
- [ ] T015 Aplicar o teto de D-3 na submissão, serializando pelo par identidade–Edital, em `backend/processo_seletivo/inscricoes/application/`
- [ ] T016 Teste: duas submissões concorrentes de Perfis diferentes não ultrapassam o teto, em `backend/tests/integration/inscricoes/`
- [ ] T017 Teste: mudar o tipo de um fato cria fato novo, e o valor congelado permanece legível sob a norma que o governou, em `backend/tests/unit/editais/`
- [ ] T018 [P] Atualizar as fixtures de snapshot em `backend/tests/fixtures/snapshot.py` e o `rebaixar()` de `backend/tests/fixtures/legado.py`
- [ ] T019 [P] Atualizar `seed_demo` em `backend/processo_seletivo/processos/management/commands/seed_demo.py`
- [ ] T020 Atualizar os testes que travam a versão canônica com o literal `6` — `test_forma_publicada.py`, `test_contrato_de_inscricao.py`, `test_quickstart.py`, `test_elevacao.py`, `test_etapas.py`, `test_limites_de_borda.py`

**Checkpoint**: a versão 7 publica, retifica e eleva; a inscrição congela fatos; o teto vale.

---

## Phase 3: US1 — Declarar a regra do marco e o desempate (P1)

**Meta**: quem elabora declara um marco com operação, Etapas enumeradas e critérios ordenados;
publica; retifica.

**Teste independente**: elaborar um marco com dois critérios, publicar, e verificar que ele aparece
no PDF e no conteúdo canônico, endereçado por identidade.

- [ ] T021 [P] [US1] Modelo `MarcoClassificatorio` em `backend/processo_seletivo/editais/models/perfis.py`
- [ ] T022 [P] [US1] Modelo `CriterioDesempate`, com `ordem` única no marco e `quando_ausente` não anulável, em `backend/processo_seletivo/editais/models/perfis.py`
- [ ] T023 [US1] Migration de `editais` com os dois modelos e `uq_marco_perfil_code`, `uq_criterio_marco_ordem`
- [ ] T024 [US1] Validação de elaboração em `backend/processo_seletivo/editais/domain/perfis.py`
- [ ] T025 [US1] Serializer aninhado e campo em `ProfileSerializer` em `backend/processo_seletivo/editais/api/serializers.py`
- [ ] T026 [US1] Preservar identidades em `replace_draft` e estender `_identidades_aninhadas_alheias` em `backend/processo_seletivo/editais/application/draft.py`
- [ ] T027 [US1] Emitir `classificationMilestones` no laço do Perfil, com `tiebreakers` ordenados por `order`, em `backend/processo_seletivo/publicacoes/application/publish_edital.py`
- [ ] T028 [US1] Função de validação de publicação no molde de `_faixa_do_percentual`, registrada em `validate_for_publication`, em `backend/processo_seletivo/editais/domain/validation.py`
- [ ] T029 [US1] Teste: publicação recusada quando o marco enumera Etapa não classificatória, em `backend/tests/unit/editais/`
- [ ] T030 [US1] Teste: publicação recusada quando um critério não declara `whenMissing` — o defeito de inventar semântica no cálculo, em `backend/tests/unit/editais/`
- [ ] T031 [US1] Teste: Retificação que remove Etapa enumerada sem ajustar o marco é recusada — é aqui que o critério pendurado é impedido, em `backend/tests/integration/publicacoes/`
- [ ] T032 [P] [US1] Ler, renderizar e **persistir** o marco em `backend/processo_seletivo/interface/forms.py`, com prefixo composto pelo índice do Perfil
- [ ] T033 [US1] Fragmento htmx e reexibição do marco e do critério em `backend/processo_seletivo/interface/views.py`
- [ ] T034 [P] [US1] Templates `_marco.html` e `_criterio.html` em `backend/processo_seletivo/interface/templates/interface/`
- [ ] T035 [US1] `CAMPOS_MARCO` e `CAMPOS_CRITERIO` e o laço aninhado em `campos_editaveis` em `backend/processo_seletivo/interface/retificacao.py`
- [ ] T036 [US1] Teste: reordenar critérios por Retificação altera a ordem calculada e **preserva os identificadores** — o defeito de substituir a lista inteira, em `backend/tests/integration/publicacoes/`
- [ ] T037 [US1] Render do marco dentro de `_perfis` em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`
- [ ] T038 [US1] Regenerar a fixture byte-a-byte `documento_publicado_v1.pdf` na mesma tarefa que muda a composição, com o diff revisado
- [ ] T039 [P] [US1] Schemas publicados e referência em `PerfilPublicado` em `specs/001-processo-seletivo-editais/contracts/openapi.yaml`
- [ ] T040 [US1] Teste: `colecoes_nao_declaradas` e `elementos_sem_chave` vazios sobre snapshot realmente publicado — o único guarda que pega coleção aninhada esquecida, em `backend/tests/integration/publicacoes/test_enderecamento.py`

**Checkpoint**: o Edital declara e publica a regra; nada calcula ainda.

---

## Phase 4: US2 — Emitir a ordem de um marco (P1)

**Meta**: a ordem é calculada na abertura, conferida e emitida como ato imutável.

**Teste independente**: com Resultados consolidados, calcular e emitir; o snapshot é imutável e traz
posição, participante e proveniência.

- [ ] T041 [P] [US2] `combinacao.py` — pontuação combinada a partir da operação, dos `weight` publicados, da normalização e do arredondamento, em `backend/processo_seletivo/classificacao/domain/`
- [ ] T042 [P] [US2] `desempate.py` — critérios na ordem publicada, `quando_ausente`, empate residual e numeração `1, 1, 3`, em `backend/processo_seletivo/classificacao/domain/`
- [ ] T043 [P] [US2] Teste da tabela-verdade do desempate, sem banco, em `backend/tests/unit/classificacao/test_desempate.py`
- [ ] T044 [P] [US2] Teste: a numeração é sempre "quantos estão à frente mais um", e "os N primeiros" seleciona N pessoas, em `backend/tests/unit/classificacao/`
- [ ] T045 [P] [US2] Teste: ausência de pontuação nunca vira zero, em `backend/tests/unit/classificacao/`
- [ ] T046 [US2] Modelos `AtoDeOrdenacao` e `PosicaoNaOrdem` em `backend/processo_seletivo/classificacao/models.py`, com `ato_anterior` e **sem** campo `vigente`
- [ ] T047 [US2] Migration do app com `uq_ato_raiz_por_marco`, `uq_ato_sucessor_unico`, `uq_posicao_por_ato_inscricao`, `ck_posicao_ou_motivo`, `ck_sucessao_com_motivo` e as duas triggers
- [ ] T048 [US2] Registrar as duas tabelas em `TABELAS_APPEND_ONLY` em `backend/processo_seletivo/seguranca/papeis.py`
- [ ] T049 [US2] Registrar os nomes das triggers em `TRIGGERS_POR_APP` em `backend/tests/migrations/test_migrations.py` — sem isso o teste estrutural não as enxerga
- [ ] T050 [US2] Teste: alteração recusada pelo ORM **e** por SQL cru; a append-only não tem exceção alguma — o defeito do ato mutável, em `backend/tests/integration/classificacao/test_imutabilidade_do_ato.py`
- [ ] T051 [US2] `calculo.py` — leitura única, `conteudos_das_versoes` para desduplicar por versão, laço sem consulta, em `backend/processo_seletivo/classificacao/application/`
- [ ] T052 [US2] `emissao.py` sob `comando_de_comissao`, com `ctx.repetido` como primeira verificação e `resultado_declarado` no desfecho, em `backend/processo_seletivo/classificacao/application/`
- [ ] T053 [US2] Trilha: `auditar(...)` **uma vez por ato**, com `permissao=ctx.base.permissao` e sem pontuação, em `backend/processo_seletivo/classificacao/application/emissao.py`
- [ ] T054 [US2] Rotas do marco e da emissão em `backend/processo_seletivo/interface/urls.py`
- [ ] T055 [US2] Views `ordenacao` (GET) e `emitir_ordenacao` (POST) com guarda, sessão e POST-redirect-GET, em `backend/processo_seletivo/interface/views.py`
- [ ] T056 [US2] Template `ordenacao.html`, **sem** campo de posição, pontuação ou desempate no formulário, em `backend/processo_seletivo/interface/templates/interface/`
- [ ] T057 [US2] Teste: abrir a tela produz zero atos, zero gravações e zero eventos, em `backend/tests/integration/classificacao/`
- [ ] T058 [US2] Teste: duas emissões concorrentes produzem exatamente um vigente, e a segunda recebe 409, em `backend/tests/integration/classificacao/`
- [ ] T059 [US2] Teste de autorização: emitir sem base de gestão responde 404 uniforme; consultar aceita `auditoria:consultar`, em `backend/tests/authorization/`
- [ ] T060 [US2] Teste: participante eliminado na Etapa fica sem posição, e posições mais considerados fecham com o universo, em `backend/tests/integration/classificacao/`

**Checkpoint**: a ordem existe como ato, e não muda mais.

---

## Phase 5: US3 — Enxergar que a ordem vigente ficou para trás (P2)

**Meta**: a obsolescência é visível, por entrada nova e por regra alterada.

**Teste independente**: emitir, consolidar Resultado tardio, e ver o vigente marcado com a
divergência.

- [ ] T061 [US3] `universo.py` — o recorte declarado e a comparação de obsolescência, em `backend/processo_seletivo/classificacao/domain/`
- [ ] T062 [US3] `selectors.py` — ato vigente derivado de `ato_anterior`, posições paginadas e divergência, em `backend/processo_seletivo/classificacao/application/`
- [ ] T063 [US3] Divergência posição a posição na tela em `backend/processo_seletivo/interface/templates/interface/ordenacao.html`
- [ ] T064 [US3] Marca de **obsoleto e não recomputável** quando o marco não existe mais no conteúdo vigente, em `backend/processo_seletivo/classificacao/application/selectors.py`
- [ ] T065 [US3] Teste: Retificação que alcança a regra obsoleta o ato **sem nenhum Resultado novo**, em `backend/tests/integration/classificacao/`
- [ ] T066 [US3] Teste: Resultado novo fora do universo declarado produz zero marcações, em `backend/tests/integration/classificacao/`
- [ ] T067 [US3] Teste: marco removido deixa o ato obsoleto e não recomputável, **e ainda reproduzível** pela versão histórica, em `backend/tests/integration/classificacao/`
- [ ] T068 [US3] Teste de performance: a contagem de consultas não cresce entre um marco pequeno e um de 1.000 participantes, em `backend/tests/performance/test_ordenacao.py`
- [ ] T069 [US3] Teste de performance: o percurso de 1.000 participantes fica dentro do teto medido com `time.monotonic()` contra um `BUDGET_SECONDS` abaixo do limite de SC-002 — o defeito de provar tempo por contagem de consultas, em `backend/tests/performance/test_ordenacao.py`

**Checkpoint**: a divergência é observável, e o vigente não muda por leitura.

---

## Phase 6: US4 — Auditar e reproduzir uma ordem emitida (P2)

**Meta**: a proveniência é inteira na tela, e basta para reproduzir a ordem.

**Teste independente**: reproduzir um ato a partir da proveniência e comparar posição a posição.

- [ ] T070 [US4] View e template do ato, com proveniência inteira e o critério que separou cada par de vizinhas, em `backend/processo_seletivo/interface/`
- [ ] T071 [US4] Rota do ato em `backend/processo_seletivo/interface/urls.py`
- [ ] T072 [US4] `marcar_como_privada` na resposta que carrega posição, pontuação e fatos de desempate, em `backend/processo_seletivo/interface/views.py`
- [ ] T073 [US4] Teste: reproduzir a partir da proveniência devolve a mesma ordem, posição a posição, sem consultar o estado vigente, em `backend/tests/integration/classificacao/`
- [ ] T074 [US4] Teste: divergência entre reproduzido e snapshot é detectável — a garantia contra mudança silenciosa de implementação, em `backend/tests/integration/classificacao/`
- [ ] T075 [US4] Teste: não existe rota que recalcule o passado, em `backend/tests/contract/`

**Checkpoint**: a proveniência sustenta a auditoria sem operação administrativa nova.

---

## Phase 7: US5 — Suceder um ato por outro no mesmo marco (P3)

**Meta**: a sucessão é linha nova, exige recálculo confirmado e preserva o anterior.

**Teste independente**: emitir dois atos e verificar um vigente e o anterior íntegro.

- [ ] T076 [US5] Sucessão por linha nova, com `ato_anterior` e motivo, em `backend/processo_seletivo/classificacao/application/emissao.py`
- [ ] T077 [US5] `confirmacao_do_calculo` no POST e recusa 422 quando a leitura é anterior ao vigente, em `backend/processo_seletivo/interface/views.py`
- [ ] T078 [US5] Histórico da sucessão na tela do marco, em `backend/processo_seletivo/interface/templates/interface/ordenacao.html`
- [ ] T079 [US5] Teste: depois da sucessão há exatamente um vigente, e o anterior permanece **inalterado** e consultável, em `backend/tests/integration/classificacao/`
- [ ] T080 [US5] Teste: sucessão a partir de leitura anterior ao vigente é recusada, em `backend/tests/integration/classificacao/`

---

## Phase 8: Polish & Cross-Cutting

- [ ] T081 [P] Teste de aceitação do percurso inteiro do quickstart em `backend/tests/acceptance/test_ordenacao.py`
- [ ] T082 [P] Verificar 375 px sem tabela horizontal na tela do marco
- [ ] T083 [P] Rodar `test_citacoes_de_requisito.py` depois de qualquer renumeração de requisito
- [ ] T084 Rodar a suíte inteira com `TEST_DB_ENGINE=postgresql` e `DB_NAME` próprio do worktree
- [ ] T085 Conferir que nenhum teste da 013 mudou de comportamento — a 015 não altera Resultado algum

---

## Dependencies

```text
Setup (T001-T003)
   ↓
Foundational (T004-T020) ......... bloqueia tudo; a elevação sobe uma vez só
   ↓
US1 (T021-T040) .................. a regra publicada
   ↓
US2 (T041-T060) .................. o cálculo e o ato
   ↓
US3 (T061-T069) ← US4 (T070-T075) ← US5 (T076-T080)
   ↓
Polish (T081-T085)
```

US3, US4 e US5 dependem de US2 e são independentes entre si — podem ser feitas em qualquer ordem, ou
em paralelo por pessoas diferentes.

## Parallel Opportunities

- **Foundational**: T008, T009, T010 e, depois das migrations, T018 e T019
- **US1**: T021 e T022; depois T032, T034 e T039
- **US2**: T041 a T045 são domínio puro e independentes das tabelas
- **Polish**: T081, T082 e T083

## Implementation Strategy

**MVP**: Foundational + US1 + US2. É o menor conjunto que entrega a frase que governa a feature — a
ordem produzida por regra publicada e constituída por ato. US3 a US5 ampliam a jornada, e nenhuma
delas altera o que as duas primeiras entregaram.

**A fatia mais arriscada é a Foundational**, e não a última: T006 é a primeira elevação canônica que
desce abaixo de `/stages`, e enquanto ela não funcionar todo conteúdo v6 publicado fica
irretificável. Fazer T007 imediatamente depois de T006, e não no fim, é o que impede descobrir isso
tarde.
