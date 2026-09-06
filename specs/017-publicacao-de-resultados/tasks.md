---

description: "Task list for feature implementation"
---

# Tasks: Publicação de Resultados

**Input**: Design documents from `/specs/017-publicacao-de-resultados/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/publicacao.md](./contracts/publicacao.md), [contracts/conteudo.md](./contracts/conteudo.md), [contracts/publico.md](./contracts/publico.md), [quickstart.md](./quickstart.md)

**Tests**: **sim, exigidos.** O Princípio V nomeia publicação, autorização e concorrência entre o que
precisa de cobertura específica, e esta feature entrega as três. Além disso, quatro correções da
revisão do plano só são demonstráveis por teste — a fronteira que separa o divulgado do individual,
os dois resumos, o bloqueio contra a emissão concorrente e a unicidade por `(ato, natureza)`. Cada
uma tem tarefa própria, nomeada pelo que ela impede.

**Organization**: por história de usuário. US1, US2 e US3 são P1; US4 e US5 são P2.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência)
- **[Story]**: US1 a US5, conforme a spec

## Path Conventions

Aplicação web Django. Produção em `backend/processo_seletivo/`, testes em `backend/tests/`. Um app
nasce nesta feature — `divulgacao` —, a tela administrativa fica em `interface` e os dois canais
públicos ficam em `portal`.

> **⚠️ A suíte precisa de PostgreSQL, e aqui são seis motivos.** Sem `TEST_DB_ENGINE=postgresql` ela
> cai para SQLite **sem avisar**, e deixam de ser verificadas: a unicidade da raiz, a do sucessor, a
> de `(ato, natureza)`, as três triggers append-only, a trigger de coerência e o `select_for_update`
> que serializa publicar e emitir. Rode como o [quickstart](./quickstart.md) manda, com `DB_NAME`
> próprio deste worktree.

> **⚠️ Nada nesta feature altera linha gravada.** As três tabelas são append-only nas três camadas, e
> a política de papéis **revoga `UPDATE` e `DELETE`** do runtime. Toda sucessão é linha nova. Se
> alguma tarefa parecer pedir um `UPDATE`, ela está errada.

> **⚠️ O individual não mora no conteúdo publicado.** `conteudo_publico` guarda **só** o que é
> divulgado; a situação de cada participante vai para `SituacaoDivulgada`. A view pública não pode
> ganhar consulta que alcance essa tabela — a fronteira é a ausência da consulta, e não um filtro no
> template (T-010, T-013).

> **⚠️ São dois resumos, e eles não se substituem.** `confirmacao_da_previa` cobre
> `{ato, publicacao_anterior, projecao}` e **não** contém o instante; `conteudo_publico_hash` cobre o
> conteúdo final, já com `publicado_em`. Calcular um só faz a confirmação nunca conferir.

> **⚠️ A 017 não toca em `classificacao`, `resultados`, `editais` nem `publicacoes`.** Nenhuma
> migration nesses apps, nenhum campo novo, nenhuma alteração de comportamento (FR-070). Se uma
> tarefa parecer exigir isso, ela está errada — ou o achado é de outra feature.

---

## Phase 1: Setup

- [ ] T001 Criar o app `divulgacao` com `apps.py`, `__init__.py`, `domain/`, `application/` e `infrastructure/` em `backend/processo_seletivo/divulgacao/`
- [ ] T002 Registrar o app em `INSTALLED_APPS` em `backend/config/settings/base.py`
- [ ] T003 [P] Criar os diretórios de teste `backend/tests/unit/divulgacao/` e `backend/tests/integration/divulgacao/` com `__init__.py`

---

## Phase 2: Foundational

**Bloqueia todas as histórias.** É o S0 da spec: sem o agregado append-only e sua cadeia, publicar
não tem onde nascer. Não produz comportamento observável, e a spec declara isso.

- [ ] T004 Criar `PublicacaoResultado`, `SituacaoDivulgada` e `DocumentoDoResultado` em `backend/processo_seletivo/divulgacao/models.py` conforme [data-model.md](./data-model.md), com `save` e `delete` que recusam alteração (FR-001, FR-037, FR-040, FR-046)
- [ ] T005 Criar a migration `backend/processo_seletivo/divulgacao/migrations/0001_initial.py` com as três tabelas e as quatro constraints: `uq_publicacao_raiz_por_marco`, `uq_publicacao_sucessora_unica`, `uq_publicacao_por_ato_natureza` e `uq_situacao_por_publicacao_inscricao` (FR-039, FR-042)
- [ ] T006 Acrescentar a `backend/processo_seletivo/divulgacao/migrations/0001_initial.py` as quatro triggers: `publicacao_resultado_append_only`, `situacao_divulgada_append_only`, `documento_do_resultado_append_only` (absolutas) e `publicacao_resultado_coerente` — que confere, no `INSERT`, que `edital_id`, `perfil_id` e `marco_id` da publicação coincidem com os do `AtoDeOrdenacao` citado, que o predecessor é do mesmo marco, e que `PRELIMINAR` não sucede `DEFINITIVA` (FR-038), no molde de `resultado_etapa_coerente`
- [ ] T007 [P] Registrar `"divulgacao"` em `APPS` e as quatro triggers em `TRIGGERS_POR_APP` em `backend/tests/migrations/test_migrations.py` — o teste estrutural só enxerga o que foi registrado
- [ ] T008 [P] Acrescentar `divulgacao_publicacaoresultado`, `divulgacao_situacaodivulgada` e `divulgacao_documentodoresultado` a `TABELAS_APPEND_ONLY` em `backend/processo_seletivo/seguranca/papeis.py` (FR-071)
- [ ] T009 [P] Acrescentar `resultado:publicar` ao papel Publicador em `backend/processo_seletivo/interface/identidade.py` (FR-025)
- [ ] T010 [P] Criar a fixture de publicação de resultado em `backend/tests/fixtures/divulgacao.py`, no molde de `tests/fixtures/publicacao.py`
- [ ] T011 Escrever o teste de privilégio em `backend/tests/integration/divulgacao/test_imutabilidade.py`: o papel de runtime não consegue `UPDATE` nem `DELETE` nas três tabelas; e duas `SituacaoDivulgada` para a mesma Inscrição na mesma publicação são recusadas por `uq_situacao_por_publicacao_inscricao` (FR-071)
- [ ] T012 [P] Escrever o teste das três triggers absolutas em `backend/tests/integration/divulgacao/test_imutabilidade.py`: a mutação é recusada mesmo por quem tem privilégio (FR-040)
- [ ] T013 [P] Escrever o teste da trigger de coerência em `backend/tests/integration/divulgacao/test_cadeia.py`: publicação cujo `edital_id`, `perfil_id` ou `marco_id` **não** coincidem com os do ato citado é recusada — inclusive quando o eixo adulterado a faria escapar da raiz única e permitiria uma segunda raiz sobre o mesmo ato; predecessor de outro marco recusado; e `PRELIMINAR` sucedendo `DEFINITIVA` recusada (FR-038, FR-042)

**Checkpoint**: o teste estrutural de migrations enxerga as quatro triggers, e nenhuma linha destas
três tabelas pode ser alterada por nenhum caminho.

---

## Phase 3: US1 — Publicar um resultado constituído (P1)

**Meta**: a autoridade publicadora seleciona um ato emitido, confere o que será divulgado e
confirma; nasce a publicação, com autor, instante e signatário.

**Teste independente**: com um ato emitido e vigente, `paula.publicadora` publica pela interface; e
as três recusas de obsolescência aparecem nomeadas na tela quando o ato não é publicável.

- [ ] T014 [US1] Escrever `compor(ato)` em `backend/processo_seletivo/divulgacao/domain/conteudo.py`: as **duas** projeções a partir do ato, das posições, das inscrições (nome e protocolo) e dos rótulos da versão que o ato cita — incluindo `marco_codigo`, que é a ordem normativa dos marcos e não pode ser reaberto depois pela fronteira pública — a pública sem identificador, sem dado pessoal interno e sem `desempate`; a individual com a situação de cada participante considerado (FR-009, FR-012, FR-015, FR-017, FR-018)
- [ ] T015 [P] [US1] Escrever `aferir(edital, marco_id, ato)` em `backend/processo_seletivo/divulgacao/domain/publicabilidade.py`: lê `estado_do_marco` e devolve informação, aviso e impedimento, com as três formas nomeadas conforme [contracts/publicacao.md](./contracts/publicacao.md) (FR-004, FR-005, FR-006)
- [ ] T016 [US1] Escrever o comando em `backend/processo_seletivo/divulgacao/application/publicar.py`, na ordem exata do contrato: `require_permission` fora da transação; `select_for_update` no `ProcessoSeletivo`; `reserve`; aferição; composição; conferência da assinatura; gravação da publicação e das situações; `auditar`; `finish` (FR-003, FR-011, FR-027, FR-028, FR-029)
- [ ] T017 [US1] Escrever os seletores `vigente_do_marco` e `publicacao_por_id` em `backend/processo_seletivo/divulgacao/application/selectors.py` (FR-042)
- [ ] T018 [US1] Acrescentar as três rotas de [contracts/publicacao.md](./contracts/publicacao.md) em `backend/processo_seletivo/interface/urls.py`
- [ ] T019 [US1] Escrever `previa_de_publicacao` e `publicar_resultado` em `backend/processo_seletivo/interface/views.py` (FR-033)
- [ ] T020 [US1] Escrever o template da prévia em `backend/processo_seletivo/interface/templates/interface/previa_de_publicacao.html`, com natureza, autoridade, o conteúdo a divulgar, as consequências do ato e a confirmação inequívoca (FR-005, FR-034)
- [ ] T021 [US1] Oferecer a ação "Publicar resultado" na tela do ato, condicionada a `resultado:publicar`, em `backend/processo_seletivo/interface/acoes.py` e no template de `ato_de_ordenacao` (FR-069)
- [ ] T022 [P] [US1] Testar a composição em `backend/tests/unit/divulgacao/test_conteudo.py`: rótulos resolvidos, empate residual como posição compartilhada, natureza como texto, e quem não recebeu posição **fora** da projeção pública e **dentro** da individual (FR-012, FR-013, FR-014, FR-016, FR-017)
- [ ] T023 [P] [US1] Testar a publicabilidade em `backend/tests/unit/divulgacao/test_publicabilidade.py`: ato sucedido, ato divergente e marco removido — cada um com o seu código; e, recusado, o ato continua consultável na tela da 015 com a proveniência completa, inclusive o desempate e o que cada critério comparou — publicar não pode ter tornado nada menos consultável (FR-008, FR-021, SC-012, SC-023)
- [ ] T024 [P] [US1] Testar os bytes gravados em `backend/tests/contract/test_conteudo_divulgado.py`: `conteudo_publico` não contém CPF, e-mail, `identity_subject`, identificador de inscrição, valor de desempate, UUID fora de `cabecalho.ato.id` nem enum como texto (FR-019, FR-020, FR-023, SC-015)
- [ ] T025 [P] [US1] Testar o resumo em `backend/tests/contract/test_conteudo_divulgado.py`: `conteudo_publico_hash` recalculado a partir dos bytes gravados confere, e muda quando qualquer campo do conteúdo muda — é o que dá sentido à afirmação de que o divulgado é conferível (FR-011, SC-004)
- [ ] T026 [US1] Testar o comando em `backend/tests/integration/divulgacao/test_publicar.py`: nasce a publicação com autor, instante e signatário, uma `SituacaoDivulgada` por participante, e a trilha registra ator, entidade, instante e versão — na trilha existente, sem tabela de eventos própria, e sem disparar mensagem de espécie alguma (FR-066, FR-067, FR-072, SC-003, SC-017)
- [ ] T027 [US1] Testar a idempotência em `backend/tests/integration/divulgacao/test_publicar.py`: a mesma chave repetida devolve o desfecho da primeira e não cria segunda publicação (FR-030, SC-013)
- [ ] T028 [US1] Testar a unicidade por natureza em `backend/tests/integration/divulgacao/test_publicar.py`: **duas chaves diferentes** sobre o mesmo ato e a mesma natureza são recusadas pela constraint — o caso que a idempotência não pega; e o mesmo ato na outra natureza produz a segunda publicação, sucedendo a primeira (FR-039, FR-041, SC-021)
- [ ] T029 [US1] Testar a assinatura em `backend/tests/integration/divulgacao/test_publicar.py`: `confirmacao_da_previa` calculada sobre outra projeção, ou sobre outra ponta da cadeia, recusa com `409`; e a assinatura da prévia **não** contém o instante (FR-031)
- [ ] T030 [US1] Testar a serialização em `backend/tests/integration/divulgacao/test_concorrencia.py`: publicar e `emitir_ordem` concorrentes não terminam com a divulgação de um ato já sucedido — exige PostgreSQL (FR-003)
- [ ] T031 [P] [US1] Testar a autorização em `backend/tests/authorization/test_publicacao_de_resultado.py`: sem `resultado:publicar` é `403`, **inclusive** para o presidente que emitiu o ato; escopo institucional alheio é `404` (FR-025, FR-026, SC-014)
- [ ] T032 [P] [US1] Testar a interface em `backend/tests/interface/test_publicar_resultado.py`: a ação aparece para quem tem a capacidade e não aparece para quem não tem; a prévia não grava linha alguma — não há rascunho a persistir; e a **tela de cálculo do marco não oferece publicar** — a proposta não tem identidade a que apontar a ação (FR-002, FR-007, FR-035, FR-036, FR-069, SC-002)

**Checkpoint**: a jornada administrativa fecha sozinha — publicar, recusar e conferir a trilha.

---

## Phase 4: US2 — Consultar o resultado publicado (P1)

**Meta**: qualquer pessoa abre o resultado por um endereço estável, sem conta, e entende o que é, de
qual Edital, quando foi publicado e se ainda vale.

**Teste independente**: sem autenticação, abrir o endereço de uma publicação e ler a lista; e
chegar nela a partir da página pública do Edital, sem conhecer o endereço.

- [ ] T033 [US2] Acrescentar a rota `resultados/<uuid:publicacao_id>/` em `backend/processo_seletivo/portal/urls.py` — **apenas a página**; a rota do documento nasce com a view dela, na US4 (FR-047)
- [ ] T034 [US2] Escrever `resultado` em `backend/processo_seletivo/portal/views.py`: consulta a publicação e a cadeia, desserializa `conteudo_publico` e **não** alcança `Inscricao`, `PosicaoNaOrdem`, `VersaoConsolidada` nem `SituacaoDivulgada` (FR-010, FR-047)
- [ ] T035 [US2] Escrever o template em `backend/processo_seletivo/portal/templates/portal/resultado.html`, com natureza em texto, instante, autoridade, o aviso de sucessão quando houver e a lista com posições compartilhadas (FR-016, FR-044, FR-049)
- [ ] T036 [US2] Listar as publicações vigentes dos marcos do Edital em `backend/processo_seletivo/portal/views.py` (`selecao`) e em `backend/processo_seletivo/portal/templates/portal/selecao.html` (FR-050)
- [ ] T037 [P] [US2] Testar a página em `backend/tests/portal/test_resultado_publico.py`: sem autenticação, mostra posições, nomes, protocolos, rótulos institucionais e o instante; nenhum UUID como informação; a lista tem estrutura semântica de tabela ou lista; e **não** há ação de recurso (FR-049, FR-054, FR-055, SC-007)
- [ ] T038 [P] [US2] Testar o empate em `backend/tests/portal/test_resultado_publico.py`: 1º, 2º, 3º, 3º renderizados como posições compartilhadas (FR-014)
- [ ] T039 [P] [US2] Testar a sucessão em `backend/tests/portal/test_resultado_publico.py`: a publicação sucedida diz que foi sucedida em **texto**, e não só por cor, oferece o caminho para a vigente, continua acessível pelo mesmo endereço e mantém o conteúdo intacto (FR-043, FR-044, FR-048, FR-052, SC-005, SC-006)
- [ ] T040 [P] [US2] Testar a descobribilidade em `backend/tests/portal/test_resultado_publico.py`: quem abre a página pública do Edital sem conhecer o endereço da publicação chega à vigente (FR-050, SC-018)
- [ ] T041 [P] [US2] Testar que abrir não recalcula em `backend/tests/portal/test_resultado_publico.py`: com a regra do marco alterada por Retificação depois da publicação, a página histórica mostra as posições como foram divulgadas, e `calcular_ordem` não é chamada (FR-010, SC-011)
- [ ] T042 [P] [US2] Testar a fronteira em `backend/tests/portal/test_fronteira_publica.py`: nada de quem está apenas em `SituacaoDivulgada` aparece no **HTML renderizado**, e a view não emite consulta àquela tabela (FR-017)
- [ ] T043 [P] [US2] Testar a responsividade em `backend/tests/portal/test_resultado_publico.py`: `scrollWidth === 375` na página do resultado (FR-051, SC-016)
- [ ] T044 [US2] Testar o custo em `backend/tests/performance/test_resultado_publico.py`: número de consultas **igual** entre 10 e 1.000 posições, no molde de `test_public_queries.py` — a asserção é sobre consultas, não sobre tempo

**Checkpoint**: o resultado existe publicamente e é encontrável por quem só conhece o Edital.

---

## Phase 5: US3 — Encontrar o resultado na própria Inscrição (P1)

**Meta**: a publicação que diz respeito à Inscrição aparece dentro dela, e nada aparece antes.

**Teste independente**: o mesmo acompanhamento, antes e depois de publicar.

- [ ] T045 [US3] Escrever `situacoes_do_candidato(inscricao)` em `backend/processo_seletivo/divulgacao/application/selectors.py`: busca `SituacaoDivulgada` pela Inscrição e devolve **todas** as linhas cuja publicação é vigente, uma por marco divulgado, ordenadas por `cabecalho.marco_codigo` — a ordem normativa dos marcos, e não a ordem em que a instituição divulgou; um Edital pode ter vários marcos, e escolher um seria o sistema decidindo qual ato interessa à pessoa (FR-057, FR-058, FR-061)
- [ ] T046 [US3] Acrescentar a chave de contexto a `acompanhamento` em `backend/processo_seletivo/portal/views.py`, **sem alterar** `_fatos_da_participacao` — ele descreve fatos da própria inscrição, e a publicação é ato de terceiro (FR-060)
- [ ] T047 [US3] Acrescentar o bloco em `backend/processo_seletivo/portal/templates/portal/acompanhamento.html`, um por marco divulgado e **nomeado pelo marco**, com natureza, posição e pontuação, ou situação e motivo, e o caminho para o resultado completo (FR-057, FR-059)
- [ ] T048 [P] [US3] Testar a ausência em `backend/tests/portal/test_acompanhamento_resultado.py`: com ato emitido e **nenhuma** publicação, o acompanhamento não menciona resultado por nenhum caminho (FR-056, SC-008)
- [ ] T049 [P] [US3] Testar a presença em `backend/tests/portal/test_acompanhamento_resultado.py`: publicada, a candidata classificada vê natureza, posição, pontuação e o caminho (FR-057, SC-009)
- [ ] T050 [P] [US3] Testar o não classificado em `backend/tests/portal/test_acompanhamento_resultado.py`: vê a própria situação e o motivo, e o seu nome **não** está na página pública (FR-059, SC-020)
- [ ] T051 [P] [US3] Testar a sucessão em `backend/tests/portal/test_acompanhamento_resultado.py`: publicada P2, o caminho da Área leva à vigente (FR-061)
- [ ] T052 [P] [US3] Testar os dois marcos em `backend/tests/portal/test_acompanhamento_resultado.py`: publicados o marco intermediário e o final para a mesma Inscrição — **o final primeiro**, em ordem temporal inversa —, os **dois** aparecem, cada um nomeado pelo seu marco, na ordem normativa de `marco_codigo` e não na de publicação, e nenhum é escolhido em lugar do outro (FR-057, SC-022)
- [ ] T053 [P] [US3] Testar o isolamento em `backend/tests/authorization/test_publicacao_de_resultado.py`: uma candidata não alcança a situação de outra, com `404` uniforme

**Checkpoint**: o gate de produto da feature — o resultado chegou à pessoa.

---

## Phase 6: US4 — Documento oficial (P2)

**Meta**: a publicação produz um artefato imprimível com o mesmo conteúdo, e ele não é regenerado.

**Teste independente**: baixar o documento pela página pública e conferir cabeçalho, autoridade e
resumo; retificar o Edital e conferir que os bytes não mudaram.

- [ ] T054 [US4] Escrever `render_resultado_pdf(conteudo)` em `backend/processo_seletivo/divulgacao/infrastructure/documento.py`, montando uma `Composicao` e chamando `render_documento`, com `_tabela` para a lista — no molde de `inscricoes/infrastructure/comprovante_pdf.py` (FR-065)
- [ ] T055 [US4] Gravar `DocumentoDoResultado` dentro do comando, em `backend/processo_seletivo/divulgacao/application/publicar.py`, derivando **do conteúdo já composto** (FR-062)
- [ ] T056 [US4] Acrescentar a rota `resultados/<uuid:publicacao_id>/documento.pdf` em `backend/processo_seletivo/portal/urls.py` **junto com** a view `resultado_em_pdf` em `backend/processo_seletivo/portal/views.py`, que devolve os bytes gravados com `ETag` igual ao `documento_hash`, no molde de `PublishedDocumentView` — rota e view nascem na mesma tarefa, porque a rota sem a view quebra o portal no import (FR-062)
- [ ] T057 [P] [US4] Testar o conteúdo em `backend/tests/unit/divulgacao/test_documento.py`: Processo/Edital, marco, natureza, ato de origem, data e hora, autoridade signatária, a lista e o resumo criptográfico (FR-063, SC-010, SC-019)
- [ ] T058 [P] [US4] Testar o determinismo em `backend/tests/unit/divulgacao/test_documento.py`: a mesma composição produz os mesmos bytes, sem data de criação embutida
- [ ] T059 [P] [US4] Testar a correspondência em `backend/tests/unit/divulgacao/test_documento.py`: os rótulos institucionais do documento são os da página, e cada linha confere — posição, identificação pública, modalidade e pontuação (FR-064)
- [ ] T060 [P] [US4] Testar a estabilidade em `backend/tests/integration/divulgacao/test_publicar.py`: Retificação posterior do Edital não altera os bytes nem regenera o documento (FR-045)

**Checkpoint**: existe a forma documental do ato, e ela é conferível.

---

## Phase 7: US5 — Histórico e sucessão (P2)

**Meta**: a gestão e a auditoria veem o que foi divulgado, quando, por quem, e o que vale hoje.

**Teste independente**: com P1 sucedida por P2, abrir o histórico do marco.

- [ ] T061 [US5] Escrever `historico_do_marco` em `backend/processo_seletivo/divulgacao/application/selectors.py`, devolvendo a cadeia com natureza, instante, autor, autoridade e situação (FR-068)
- [ ] T062 [US5] Escrever `publicacoes_do_marco` em `backend/processo_seletivo/interface/views.py`, aberta a `resultado:publicar` **ou** `auditoria:consultar`
- [ ] T063 [US5] Escrever o template em `backend/processo_seletivo/interface/templates/interface/publicacoes_do_marco.html` (FR-068)
- [ ] T064 [US5] Oferecer, na publicação e no histórico, o caminho para o **ato de origem** — a tela da 015 — em `backend/processo_seletivo/interface/templates/interface/publicacoes_do_marco.html`, condicionado à autorização de quem lê (FR-022)
- [ ] T065 [P] [US5] Testar a listagem em `backend/tests/interface/test_publicacoes_do_marco.py`: as duas publicações, com a vigente identificada e a anterior marcada como sucedida (FR-068)
- [ ] T066 [P] [US5] Testar a autorização em `backend/tests/interface/test_publicacoes_do_marco.py`: a auditora consulta e **não** recebe a ação de publicar; o caminho para o ato de origem aparece a quem tem autorização e não aparece a quem não tem (FR-022)
- [ ] T067 [P] [US5] Testar a acessibilidade em `backend/tests/interface/test_publicacoes_do_marco.py`: a situação vigente/sucedida é legível sem depender de cor (FR-052)

**Checkpoint**: a pergunta "isto ainda vale?" tem resposta nos três canais.

---

## Phase 8: Polish

- [ ] T068 Executar o [quickstart](./quickstart.md) inteiro como teste de aceitação em `backend/tests/acceptance/test_us_publicacao_de_resultado.py`, cobrindo o gate da spec de ponta a ponta, inclusive a publicação consultável imediatamente depois de confirmada (FR-032, SC-001)
- [ ] T069 [P] Testar por teclado a prévia, a confirmação e a página pública em `backend/tests/interface/test_acessibilidade_publicacao.py` (FR-053)
- [ ] T070 [P] Escrever a guarda do protocolo em `backend/tests/authorization/test_publicacao_de_resultado.py`: nenhum caminho não autenticado resolve uma Inscrição a partir do protocolo — publicá-lo o tornou público, e ele não pode virar credencial (FR-024)
- [ ] T071 [P] Escrever a guarda de não regressão em `backend/tests/migrations/test_migrations.py`: esta feature não acrescenta migration a `classificacao`, `resultados`, `editais` nem `publicacoes` (FR-070)
- [ ] T072 [P] Acrescentar ao `seed_demo` o ator publicador com `resultado:publicar` e um resultado publicado, em `backend/processo_seletivo/processos/management/commands/seed_demo.py`
- [ ] T073 Conferir que `backend/tests/test_citacoes_de_requisito.py` continua verde e que nenhuma citação FR/SC introduzida aponta para requisito diferente do pretendido

---

## Dependencies

```text
Setup (T001–T003)
   ↓
Foundational (T004–T013)          ← bloqueia tudo
   ↓
US1 (T014–T032)                   ← bloqueia US2, US3, US4, US5
   ↓
   ├── US2 (T033–T044)  ─┐
   ├── US3 (T045–T053)  ─┤ independentes entre si
   ├── US4 (T054–T060)  ─┤ rota e view do documento na mesma tarefa (T056)
   └── US5 (T061–T067)  ─┘
   ↓
Polish (T068–T073)
```

**Por que US1 bloqueia as demais**: as quatro seguintes leem publicações, e não há publicação antes
do comando existir. Não é acoplamento evitável — é a ordem do domínio.

**Nenhuma história depende de outra além da US1.** A rota do documento nasce com a sua view em T056,
dentro da US4 — separá-las deixaria o `portal/urls.py` apontando para uma view inexistente e
quebraria o import do portal durante a US2 inteira.

**Por que US4 vem depois de US3 na ordem sugerida**: decisão da spec. O documento é
institucionalmente importante, mas a validação de produto é o resultado chegar ao candidato.

**Até a US4, publicações nascem sem documento.** `DocumentoDoResultado` é tabela própria, e a
ausência de linha representa isso sem deixar coluna a limpar.

## Parallel opportunities

- **Foundational**: T007 a T010 tocam arquivos distintos e correm juntas depois de T006; T012 e T013
  também.
- **US1**: T022 a T025, T031 e T032 são arquivos distintos. T015 é paralela a T014.
- **US2**: T037 a T043 compartilham arquivo — paralelas só se escritas em conjunto; T044 é
  independente. T042 depende de T034.
- **US3**: T048 a T052 compartilham `test_acompanhamento_resultado.py` — paralelas só se escritas
  em conjunto; T053 é arquivo distinto.
- **US4**: T057 a T060 são independentes.
- **US5**: T065 a T067 compartilham arquivo.
- **Polish**: T069 a T072 são independentes.

## Implementation Strategy

**MVP**: Setup + Foundational + US1 + US2. Nesse ponto a instituição publica e o público consulta —
é a borda institucional fechada, ainda sem a jornada do candidato.

**Incremento seguinte**: US3, que é o que transforma a feature em valor percebido, e é o que a spec
elegeu como validação de produto.

**Depois**: US4 e US5, em qualquer ordem, com US5 preferencialmente por último — a sucessão se
exerce melhor sobre publicações que já existem do que sobre fixtures.

## Notes

- [P] = arquivos diferentes, sem dependência
- [Story] mapeia a tarefa para a história, e a citação do requisito em cada tarefa é o que sustenta
  a rastreabilidade que o Princípio V cobra entre spec, plano e tarefas
- Verifique que o teste falha antes de implementar
- Commit por tarefa ou grupo lógico
- A varredura de vocabulário da 013 (`tests/test_vocabulario_do_resultado.py`) lê apenas
  `interface/templates`: os templates do `portal` desta feature afirmam classificação
  legitimamente, e a varredura **não** deve ser estendida a eles
