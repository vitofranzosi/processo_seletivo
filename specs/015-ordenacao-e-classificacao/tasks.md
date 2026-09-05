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

**Organization**: por história de usuário. US1, US2 e US3 são P1; US4 e US5 são P2; US6 é P3.

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

> **⚠️ A leva D-2/D-3 está partida em dois de propósito.** O que é **esquema e conteúdo publicado**
> fica na Foundational, porque a elevação canônica precisa carregar marco, fatos e teto **de uma
> vez** — subir a versão com um e acrescentar o outro depois produziria snapshots de versão 7 com e
> sem a propriedade. O que é **jornada do candidato** — coletar, congelar, aplicar o teto — é a US2,
> com história, critérios e cenário demonstrável próprios.

---

## Phase 1: Setup

- [X] T001 Criar o app `classificacao` com `apps.py`, `__init__.py`, `domain/` e `application/` em `backend/processo_seletivo/classificacao/`
- [X] T002 Registrar o app em `INSTALLED_APPS` em `backend/config/settings/base.py` — o caminho que esta tarefa trazia (`processo_seletivo/settings.py`) não existe
- [X] T003 [P] Criar os diretórios de teste `backend/tests/unit/classificacao/` e `backend/tests/integration/classificacao/` com `__init__.py`

---

## Phase 2: Foundational — a leva normativa (bloqueia todas as histórias)

**A elevação e as duas dependências de conteúdo. Nenhuma história começa antes daqui.**

- [X] T004 Elevar `SCHEMA_VERSION` de 6 para 7 e registrar o incremento no bloco de história em `backend/processo_seletivo/shared/canonical.py`
- [X] T005 Acrescentar o degrau `7` a `DEGRAUS` em `backend/processo_seletivo/publicacoes/domain/elevacao.py`, com a coleção nova elevando para lista vazia
- [X] T006 Estender `elevar()` para descer até `profiles` em `backend/processo_seletivo/publicacoes/domain/elevacao.py` — hoje ela só reescreve `conteudo["stages"]`, e esta é a primeira elevação aninhada
- [X] T007 Teste: conteúdo v6 publicado continua retificável depois da elevação, em `backend/tests/integration/publicacoes/test_elevacao_de_versao.py`
- [X] T008 [P] Declarar as coleções novas em `COLECOES_COM_CHAVE` em `backend/processo_seletivo/publicacoes/domain/colecoes.py`
- [X] T009 [P] Modelo `FatoDeclarado` (D-2) em `backend/processo_seletivo/editais/models/perfis.py`, com identidade estável e tipo restrito a data e inteiro
- [X] T010 [P] Campo `max_inscricoes_por_candidato` (D-3), anulável, em `backend/processo_seletivo/processos/models.py` — é do **`Edital`**, e não do Perfil: no Perfil ele seria redundante com `uq_inscricao_identidade_edital_perfil`, que já existe
- [X] T011 Migration de `editais` com `FatoDeclarado` e suas unicidades, em `backend/processo_seletivo/editais/migrations/`
- [X] T012 Migration de `processos` com o teto, em `backend/processo_seletivo/processos/migrations/`
- [X] T013 Emitir `declaredFacts` dentro do laço do Perfil e `maxInscricoesPorCandidato` **na raiz** do snapshot, em `backend/processo_seletivo/publicacoes/application/publish_edital.py`
- [X] T014 [P] Atualizar as fixtures de snapshot em `backend/tests/fixtures/snapshot.py` — o `rebaixar()` de `backend/tests/fixtures/legado.py` **já foi feito** em T007, que não fecharia sem ele; falta a fixture de snapshot
- [X] T015 [P] Atualizar `seed_demo` em `backend/processo_seletivo/processos/management/commands/seed_demo.py`
- [X] T016 Atualizar os testes que travam a versão canônica com o literal `6` — `test_forma_publicada.py`, `test_contrato_de_inscricao.py`, `test_quickstart.py`, `test_elevacao.py`, `test_etapas.py`, `test_limites_de_borda.py`

**Checkpoint**: a versão 7 publica, retifica e eleva, carregando as três mudanças de forma — marco,
fatos declarados e teto. **Nada de comportamento ainda**: coletar, congelar e aplicar o teto é a US2,
e calcular é a US3.

---

## Phase 3: US1 — Declarar a regra do marco e o desempate (P1)

> **⚠️ Uma minifatia atômica, identificada pelo conteúdo e não por ID.** O par é **"acrescentar a
> forma a `COLECOES_PUBLICADAS`" + "atualizar o `openapi.yaml`"** — as duas tarefas marcadas abaixo.
> Identificá-lo por número já falhou uma vez: a renumeração move os IDs, e a nota anterior apontava
> para o teste de remoção de Etapa e para o congelamento de fatos, que não tocam nem um nem outro.
>
> A razão, medida por spike em 04/09/2026: emitir as coleções no snapshot quebra **um** teste, o de
> endereçamento, e quem o resolve é T008, que já veio antes. Mas `FORMAS`, em
> `test_forma_publicada.py`, deriva de `validation.COLECOES_PUBLICADAS` — não da emissão. No momento
> em que a forma nova entrar ali, os três testes parametrizados passam a exigir o esquema no
> contrato. Executar as duas juntas, e não manter testes de contrato deliberadamente vermelhos no
> intervalo.

**Meta**: quem elabora declara um marco com operação, Etapas enumeradas e critérios ordenados;
publica; retifica.

**Teste independente**: elaborar um marco com dois critérios, publicar, e verificar que ele aparece
no PDF e no conteúdo canônico, endereçado por identidade.

- [X] T017 [P] [US1] Modelo `MarcoClassificatorio` em `backend/processo_seletivo/editais/models/perfis.py`
- [X] T018 [P] [US1] Modelo `CriterioDesempate`, com `ordem` única no marco e `quando_ausente` não anulável, em `backend/processo_seletivo/editais/models/perfis.py`
- [X] T019 [US1] Migration de `editais` com os dois modelos e `uq_marco_perfil_code`, `uq_criterio_marco_ordem`
- [X] T020 [US1] Validação de elaboração em `backend/processo_seletivo/editais/domain/perfis.py`
- [X] T021 [US1] Serializer aninhado e campo em `ProfileSerializer` em `backend/processo_seletivo/editais/api/serializers.py`
- [X] T022 [US1] Preservar identidades em `replace_draft` e estender `_identidades_aninhadas_alheias` em `backend/processo_seletivo/editais/application/draft.py`
- [X] T023 [US1] Emitir `classificationMilestones` no laço do Perfil, com `tiebreakers` ordenados por `order`, em `backend/processo_seletivo/publicacoes/application/publish_edital.py`
- [X] T024 [US1] Função de validação de publicação no molde de `_faixa_do_percentual`, registrada em `validate_for_publication`, em `backend/processo_seletivo/editais/domain/validation.py`
- [X] T025 [US1] Teste: publicação recusada quando o marco enumera Etapa não classificatória, em `backend/tests/unit/editais/`
- [X] T026 [US1] Teste: publicação recusada quando um critério não declara `whenMissing` — o defeito de inventar semântica no cálculo, em `backend/tests/unit/editais/`
- [X] T027 [US1] Teste: Retificação que remove Etapa enumerada sem ajustar o marco é recusada — é aqui que o critério pendurado é impedido, em `backend/tests/integration/publicacoes/`
- [X] T028 [P] [US1] Ler, renderizar e **persistir** o marco em `backend/processo_seletivo/interface/forms.py`, com prefixo composto pelo índice do Perfil
- [X] T029 [US1] Fragmento htmx e reexibição do marco e do critério em `backend/processo_seletivo/interface/views.py`
- [X] T030 [P] [US1] Templates `_marco.html` e `_criterio.html` em `backend/processo_seletivo/interface/templates/interface/`
- [X] T031 [US1] `CAMPOS_MARCO` e `CAMPOS_CRITERIO` e o laço aninhado em `campos_editaveis` em `backend/processo_seletivo/interface/retificacao.py`
- [X] T032 [US1] Teste: reordenar critérios por Retificação altera a ordem calculada e **preserva os identificadores** — o defeito de substituir a lista inteira, em `backend/tests/integration/publicacoes/`
- [X] T033 [US1] Render do marco dentro de `_perfis` em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`
- [X] T034 [US1] **Nada a regenerar, e verificado:** a fixture byte-a-byte `documento_publicado_v1.pdf` na mesma tarefa que muda a composição, com o diff revisado
- [X] T035 [US1] **Minifatia, primeira metade:** acrescentar a forma de `classificationMilestones` **e** de `declaredFacts` a `COLECOES_PUBLICADAS` em `backend/processo_seletivo/editais/domain/validation.py`
- [X] T036 [US1] **Minifatia, segunda metade, imediatamente depois:** schemas publicados das **duas** coleções novas e referência em `PerfilPublicado` em `specs/001-processo-seletivo-editais/contracts/openapi.yaml`
- [X] T037 [US1] Teste: `colecoes_nao_declaradas` e `elementos_sem_chave` vazios sobre snapshot realmente publicado — o único guarda que pega coleção aninhada esquecida, em `backend/tests/integration/publicacoes/test_enderecamento.py`

**Checkpoint**: o Edital declara e publica a regra; nada calcula ainda.

---

## Phase 4: US2 — Informar os fatos que o Edital exige (P1)

**Meta**: o Edital declara os fatos que exige, e o candidato os preenche e os vê congelados na
submissão. As duas metades são desta história: FR-057 exige que o Edital **possa declarar**, e o
teste independente abaixo começa justamente por declarar.

**Teste independente**: declarar dois fatos, submeter, alterar o perfil depois e verificar que os
valores congelados não mudaram.

- [X] T038 [US2] Serializer aninhado de `declaredFacts` e campo em `ProfileSerializer`, no molde de `CompetitionModalitySerializer`, em `backend/processo_seletivo/editais/api/serializers.py`
- [X] T039 [US2] Persistir os fatos em `replace_draft` preservando o `id` recebido, e estender `_identidades_aninhadas_alheias`, em `backend/processo_seletivo/editais/application/draft.py`
- [X] T040 [US2] Validação de elaboração e de publicação do fato — código único no Perfil, tipo restrito aos dois valores — em `backend/processo_seletivo/editais/domain/perfis.py` e `domain/validation.py`
- [X] T041 [P] [US2] Ler, renderizar e **persistir** os fatos em `backend/processo_seletivo/interface/forms.py`, com prefixo composto pelo índice do Perfil
- [X] T042 [US2] Fragmento htmx e reexibição do fato em `backend/processo_seletivo/interface/views.py`, e template `_fato.html` em `templates/interface/`
- [X] T043 [US2] `CAMPOS_FATO` e o laço aninhado em `campos_editaveis` em `backend/processo_seletivo/interface/retificacao.py`
- [X] T044 [US2] Teste integrado: declarar dois fatos → publicar → retificar, com os identificadores **preservados** ao longo do percurso, em `backend/tests/integration/publicacoes/`
- [X] T045 [US2] Teste: identidade de fato pertencente a outro Perfil é recusada na gravação do rascunho, em `backend/tests/integration/editais/`
- [X] T046 [US2] `CAMPOS_NAO_RETIFICAVEIS` por **forma de caminho** em `backend/processo_seletivo/publicacoes/domain/colecoes.py`, com exceção própria traduzida para `422 invalid_change` — e a recusa **depois** de resolver o contêiner, para não roubar a precedência de caminho inexistente e seletor inválido
- [X] T047 [US2] Teste: `REPLACE` sobre `.../declaredFacts/.../type` é recusado, e remover o fato e acrescentar outro com identidade nova continua permitido, em `backend/tests/integration/publicacoes/test_fato_declarado.py`
- [X] T048 [US2] Modelo `ValorDeFato` em `backend/processo_seletivo/inscricoes/models.py`, com `fato_id` pela identidade publicada e `ck_valor_conforme_tipo`
- [X] T049 [US2] Congelar os fatos na **submissão**, contra a `versao_aceita`, em `backend/processo_seletivo/inscricoes/` — nunca na abertura do rascunho
- [X] T050 [US2] Migration de `inscricoes` com os valores congelados, em `backend/processo_seletivo/inscricoes/migrations/`
- [X] T051 [US2] Aplicar o teto de D-3 na submissão, com trava **do par identidade–Edital** — nunca da inscrição, que deixaria duas submissões concorrentes de Perfis diferentes passarem as duas pelo teto; a trava serializa as inscrições de uma pessoa num Edital, e não as de todo mundo, em `backend/processo_seletivo/inscricoes/application/`
- [X] T052 [US2] Teste: duas submissões concorrentes de Perfis diferentes não ultrapassam o teto, em `backend/tests/integration/inscricoes/`
- [X] T053 [US2] Teste: rascunho abandonado não consome direito — o teto conta só inscrições submetidas, em `backend/tests/integration/inscricoes/`
- [X] T054 [US2] Teste: Retificação que reduz o teto não invalida inscrição já submetida sob a norma que a admitia, em `backend/tests/integration/inscricoes/`
- [X] T055 [US2] Registrar `ValorDeFato` em `TABELAS_APPEND_ONLY` em `backend/processo_seletivo/seguranca/papeis.py`
- [X] T056 [P] [US2] Campos dos fatos declarados no formulário da inscrição em `backend/processo_seletivo/portal/` e no template correspondente
- [X] T057 [US2] Teste: editar o perfil depois da submissão muda zero valores congelados, em `backend/tests/integration/inscricoes/`
- [X] T058 [US2] Teste: inscrição submetida **antes** de o fato ser declarado permanece válida, e o critério que o consome a trata pelo comportamento declarado para valor ausente — a ponte entre D-2 e o desempate, em `backend/tests/integration/classificacao/`
- [X] T059 [P] [US2] Teste: Edital sem fato declarado apresenta zero campos novos na inscrição, em `backend/tests/integration/inscricoes/`
- [X] T060 [US2] Teste: rascunho aberto durante a Retificação que acrescenta fato revê a versão nova antes de confirmar, em `backend/tests/integration/inscricoes/`
- [X] T061 [US2] Teste de ciclo completo: congelar um valor, retificar removendo o fato e acrescentando outro, e provar que o valor antigo permanece ligado à **identidade e à versão anteriores** — é a metade de T046 que só é demonstrável depois de `ValorDeFato` existir, em `backend/tests/integration/inscricoes/`
- [X] T062 [US2] Teste de autorização: os valores congelados não vazam para outro candidato nem para quem não administra, em `backend/tests/authorization/`

**Checkpoint**: o desempate por idade e por experiência passa a ter valor para ler.

---

## Phase 5: US3 — Emitir a ordem de um marco (P1)

> **✅ Desbloqueada em 04/09/2026.** D-1 entrou em `main` pelo PR #35 e foi integrada aqui: o
> `ResultadoEtapa` tem `origem` e `versao`, `avaliacao` é anulável amarrada à origem por constraint,
> e os seletores leem `ResultadoEtapa.versao` **direto** — nenhum uso de `avaliacao__versao` sobrou
> em código, só menções em comentário explicando o abandono do caminho.
>
> **O que isso dá a esta fase.** A proveniência do ato lê a âncora normativa do próprio Resultado,
> sem passar pela Avaliação: a dependência que o bloqueio existia para não cimentar deixou de
> existir. E o Resultado por Ocorrência entra nos conjuntos que esta fase consome **sem uma linha de
> código aqui** — `habilitadas_em` e `eliminadas_ate` filtram por `consequencia`, e não por
> `origem`, que é o que o invariante I-1 pede.
>
> **Uma restrição para o consumidor.** A Ocorrência hoje é sempre `ELIMINADA`, mas isso é
> **política da 013**, e não constraint — o sorteio e a verificação de reserva podem produzir
> desfecho favorável por caminho não-avaliativo. Esta fase MUST ler `consequencia` e o motivo,
> **nunca** a origem, para não quebrar no dia em que houver Ocorrência favorável.
>
> Integração verificada: `ruff check` e `ruff format --check` limpos, `makemigrations --check` sem
> pendência, suíte completa com 2937 passes, 1 skip, zero falhas.

**Meta**: a ordem é calculada na abertura, conferida e emitida como ato imutável.

**Teste independente**: com Resultados consolidados, calcular e emitir; o snapshot é imutável e traz
posição, participante e proveniência.

- [ ] T063 [P] [US3] `combinacao.py` — pontuação combinada a partir da operação, dos `weight` publicados, da normalização e do arredondamento, em `backend/processo_seletivo/classificacao/domain/`
- [ ] T064 [P] [US3] `desempate.py` — critérios na ordem publicada, `quando_ausente`, empate residual e numeração `1, 1, 3`, em `backend/processo_seletivo/classificacao/domain/`
- [ ] T065 [P] [US3] Teste da tabela-verdade do desempate, sem banco, em `backend/tests/unit/classificacao/test_desempate.py`
- [ ] T066 [P] [US3] Teste: a numeração é sempre "quantos estão à frente mais um", e "os N primeiros" seleciona N pessoas, em `backend/tests/unit/classificacao/`
- [ ] T067 [P] [US3] Teste: ausência de pontuação nunca vira zero, em `backend/tests/unit/classificacao/`
- [ ] T068 [US3] Modelos `AtoDeOrdenacao` e `PosicaoNaOrdem` em `backend/processo_seletivo/classificacao/models.py`, com `ato_anterior` e **sem** campo `vigente`
- [ ] T069 [US3] Migration do app com `uq_ato_raiz_por_marco`, `uq_ato_sucessor_unico`, `uq_posicao_por_ato_inscricao`, `ck_posicao_ou_motivo`, `ck_sucessao_com_motivo` e as duas triggers
- [ ] T070 [US3] Registrar as duas tabelas em `TABELAS_APPEND_ONLY` em `backend/processo_seletivo/seguranca/papeis.py`
- [ ] T071 [US3] Registrar os nomes das triggers em `TRIGGERS_POR_APP` em `backend/tests/migrations/test_migrations.py` — sem isso o teste estrutural não as enxerga
- [ ] T072 [US3] Teste: alteração recusada pelo ORM **e** por SQL cru; a append-only não tem exceção alguma — o defeito do ato mutável, em `backend/tests/integration/classificacao/test_imutabilidade_do_ato.py`
- [ ] T073 [US3] `calculo.py` — leitura única, `conteudos_das_versoes` para desduplicar por versão, laço sem consulta, em `backend/processo_seletivo/classificacao/application/`
- [ ] T074 [US3] `emissao.py` sob `comando_de_comissao`, com `ctx.repetido` como primeira verificação e `resultado_declarado` no desfecho, em `backend/processo_seletivo/classificacao/application/`
- [ ] T075 [US3] Trilha: `auditar(...)` **uma vez por ato**, com `permissao=ctx.base.permissao` e sem pontuação, em `backend/processo_seletivo/classificacao/application/emissao.py`
- [ ] T076 [US3] Rotas do marco e da emissão em `backend/processo_seletivo/interface/urls.py`
- [ ] T077 [US3] Views `ordenacao` (GET) e `emitir_ordenacao` (POST) com guarda, sessão e POST-redirect-GET, em `backend/processo_seletivo/interface/views.py`
- [ ] T078 [US3] Template `ordenacao.html`, **sem** campo de posição, pontuação ou desempate no formulário, em `backend/processo_seletivo/interface/templates/interface/`
- [ ] T079 [US3] Teste: abrir a tela produz zero atos, zero gravações e zero eventos, em `backend/tests/integration/classificacao/`
- [ ] T080 [US3] Teste: duas emissões concorrentes produzem exatamente um vigente, e a segunda recebe 409, em `backend/tests/integration/classificacao/`
- [ ] T081 [US3] Teste de autorização: emitir sem base de gestão responde 404 uniforme; consultar aceita `auditoria:consultar`, em `backend/tests/authorization/`
- [ ] T082 [US3] Teste: participante eliminado na Etapa fica sem posição, e posições mais considerados fecham com o universo, em `backend/tests/integration/classificacao/`

- [ ] T083 [US3] Teste: a tela identifica o grupo empatado como grupo, para que ninguém infira precedência onde o Edital não a declarou (FR-027), em `backend/tests/integration/classificacao/`
- [ ] T084 [US3] Teste de autorização: os fatos do candidato usados em desempate só são alcançáveis por quem administra e audita, e nunca por outro candidato (FR-053), em `backend/tests/authorization/`
**Checkpoint**: a ordem existe como ato, e não muda mais.

---

## Phase 6: US4 — Enxergar que a ordem vigente ficou para trás (P2)

**Meta**: a obsolescência é visível, por entrada nova e por regra alterada.

**Teste independente**: emitir, consolidar Resultado tardio, e ver o vigente marcado com a
divergência.

- [ ] T085 [US4] `universo.py` — o recorte declarado e a comparação de obsolescência, em `backend/processo_seletivo/classificacao/domain/`
- [ ] T086 [US4] `selectors.py` — ato vigente derivado de `ato_anterior`, posições paginadas e divergência, em `backend/processo_seletivo/classificacao/application/`
- [ ] T087 [US4] Divergência posição a posição na tela em `backend/processo_seletivo/interface/templates/interface/ordenacao.html`
- [ ] T088 [US4] Marca de **obsoleto e não recomputável** quando o marco não existe mais no conteúdo vigente, em `backend/processo_seletivo/classificacao/application/selectors.py`
- [ ] T089 [US4] Teste: Retificação que alcança a regra obsoleta o ato **sem nenhum Resultado novo**, em `backend/tests/integration/classificacao/`
- [ ] T090 [US4] Teste: Resultado novo fora do universo declarado produz zero marcações, em `backend/tests/integration/classificacao/`
- [ ] T091 [US4] Teste: marco removido deixa o ato obsoleto e não recomputável, **e ainda reproduzível** pela versão histórica, em `backend/tests/integration/classificacao/`
- [ ] T092 [US4] Teste de performance: a contagem de consultas não cresce entre um marco pequeno e um de 1.000 participantes, em `backend/tests/performance/test_ordenacao.py`
- [ ] T093 [US4] Teste de performance: o percurso de 1.000 participantes fica dentro do teto medido com `time.monotonic()` contra um `BUDGET_SECONDS` abaixo do limite de SC-002 — o defeito de provar tempo por contagem de consultas, em `backend/tests/performance/test_ordenacao.py`

- [ ] T094 [US4] Teste: Resultado tardio **dentro** do universo faz o vigente aparecer como obsoleto (SC-008) — hoje só o caminho negativo é exercitado, em `backend/tests/integration/classificacao/`
- [ ] T095 [US4] Teste: ato obsoleto continua vigente, consultável e produzindo efeito até que outro seja emitido (FR-038), em `backend/tests/integration/classificacao/`
**Checkpoint**: a divergência é observável, e o vigente não muda por leitura.

---

## Phase 7: US5 — Auditar e reproduzir uma ordem emitida (P2)

**Meta**: a proveniência é inteira na tela, e basta para reproduzir a ordem.

**Teste independente**: reproduzir um ato a partir da proveniência e comparar posição a posição.

- [ ] T096 [US5] View e template do ato, com proveniência inteira e o critério que separou cada par de vizinhas, em `backend/processo_seletivo/interface/`
- [ ] T097 [US5] Rota do ato em `backend/processo_seletivo/interface/urls.py`
- [ ] T098 [US5] `marcar_como_privada` na resposta que carrega posição, pontuação e fatos de desempate, em `backend/processo_seletivo/interface/views.py`
- [ ] T099 [US5] Teste: reproduzir a partir da proveniência devolve a mesma ordem, posição a posição, sem consultar o estado vigente, em `backend/tests/integration/classificacao/`
- [ ] T100 [US5] Teste: divergência entre reproduzido e snapshot é detectável — a garantia contra mudança silenciosa de implementação, em `backend/tests/integration/classificacao/`
- [ ] T101 [US5] Teste: não existe rota que recalcule o passado, em `backend/tests/contract/`

- [ ] T102 [US5] Teste: para duas posições vizinhas separadas por desempate, a consulta nomeia o critério e os valores usados (FR-050, SC-010), em `backend/tests/integration/classificacao/`
**Checkpoint**: a proveniência sustenta a auditoria sem operação administrativa nova.

---

## Phase 8: US6 — Suceder um ato por outro no mesmo marco (P3)

**Meta**: a sucessão é linha nova, exige recálculo confirmado e preserva o anterior.

**Teste independente**: emitir dois atos e verificar um vigente e o anterior íntegro.

- [ ] T103 [US6] Sucessão por linha nova, com `ato_anterior` e motivo, em `backend/processo_seletivo/classificacao/application/emissao.py`
- [ ] T104 [US6] `confirmacao_do_calculo` no POST e recusa 422 quando a leitura é anterior ao vigente, em `backend/processo_seletivo/interface/views.py`
- [ ] T105 [US6] Histórico da sucessão na tela do marco, em `backend/processo_seletivo/interface/templates/interface/ordenacao.html`
- [ ] T106 [US6] Teste: depois da sucessão há exatamente um vigente, e o anterior permanece **inalterado** e consultável, em `backend/tests/integration/classificacao/`
- [ ] T107 [US6] Teste: sucessão a partir de leitura anterior ao vigente é recusada, em `backend/tests/integration/classificacao/`

---

## Phase 9: Polish & Cross-Cutting

- [ ] T108 [P] Teste de aceitação do percurso inteiro do quickstart em `backend/tests/acceptance/test_ordenacao.py`
- [ ] T109 [P] Verificar 375 px sem tabela horizontal na tela do marco
- [ ] T110 [P] Rodar `test_citacoes_de_requisito.py` depois de qualquer renumeração de requisito
- [ ] T111 [P] Teste de guarda: pesos que não somam 1 publicam normalmente (FR-012); a feature não aplica corte nem vaga (FR-055); e não existe rota que exponha a ordem a candidato ou público (FR-056), em `backend/tests/contract/`
- [ ] T112 Rodar a suíte inteira com `TEST_DB_ENGINE=postgresql` e `DB_NAME` próprio do worktree
- [ ] T113 Conferir que nenhum teste da 013 mudou de comportamento — a 015 não altera Resultado algum

---

## Dependencies

```text
Setup (T001-T003)
   ↓
Foundational (T004-T016) ......... bloqueia tudo; a elevação sobe uma vez só
   ↓
US1 (T017-T037) ..................... a regra publicada
   ↓
US2 (T038-T060) ..................... os fatos: declarados e congelados
   ↓
US3 (T061-T082) ..................... o cálculo e o ato        ← exige D-1 integrada
   ↓
   ├── US4 (T083-T093) .............. a obsolescência
   ├── US5 (T094-T100) .............. a proveniência
   └── US6 (T101-T105) .............. a sucessão
   ↓
Polish (T106-T111)
```

As três últimas pendem de US3 e **não** pendem umas das outras — a primeira redação deste grafo
desenhava `US4 ← US5 ← US6`, que dizia o contrário da frase ao lado. Elas dependem de US3 e são
independentes entre si — podem ser feitas em qualquer ordem, ou
em paralelo por pessoas diferentes. **US2 não bloqueia US3 tecnicamente**: o cálculo roda com
critérios que só leem pontuação. Ela vem antes porque, sem fato congelado, o desempate por idade e
por experiência é inexecutável — e porque o congelamento acontece na submissão, que não retroage
para quem já se inscreveu.

## Parallel Opportunities

- **Foundational**: as tarefas de declaração de coleção e de modelo, e depois as de fixture e seed
- **US1**: os dois modelos; depois formulário, templates e `openapi.yaml`
- **US2**: o formulário do portal e o teste do Edital sem fato
- **US3**: as funções de domínio puro, independentes das tabelas
- **Polish**: as três primeiras

## Implementation Strategy

**MVP**: Foundational + US1 + US2 + US3. É o menor conjunto que entrega a frase que governa a
feature — a ordem produzida por regra publicada e constituída por ato — com o desempate executável
para os Editais em vista. US4 a US6 ampliam a jornada, e nenhuma delas altera o que as três primeiras
entregaram.

**A fatia mais arriscada é a Foundational**, e não a última: T006 é a primeira elevação canônica que
desce abaixo de `/stages`, e enquanto ela não funcionar todo conteúdo v6 publicado fica
irretificável. Fazer T007 imediatamente depois de T006, e não no fim, é o que impede descobrir isso
tarde.
