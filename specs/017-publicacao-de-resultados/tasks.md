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

- [ ] T004 Criar `PublicacaoResultado`, `SituacaoDivulgada` e `DocumentoDoResultado` em `backend/processo_seletivo/divulgacao/models.py`, conforme [data-model.md](./data-model.md), com `save` e `delete` que recusam alteração
- [ ] T005 Criar a migration `backend/processo_seletivo/divulgacao/migrations/0001_initial.py` com as três tabelas e as três constraints: `uq_publicacao_raiz_por_marco`, `uq_publicacao_sucessora_unica` e `uq_publicacao_por_ato_natureza`
- [ ] T006 Acrescentar a `backend/processo_seletivo/divulgacao/migrations/0001_initial.py` as quatro triggers: `publicacao_resultado_append_only`, `situacao_divulgada_append_only`, `documento_do_resultado_append_only` (absolutas) e `publicacao_resultado_coerente` (confere, no `INSERT`, que o predecessor é do mesmo marco e que `PRELIMINAR` não sucede `DEFINITIVA`), no molde de `resultado_etapa_coerente`
- [ ] T007 [P] Registrar `"divulgacao"` em `APPS` e as quatro triggers em `TRIGGERS_POR_APP` em `backend/tests/migrations/test_migrations.py` — o teste estrutural só enxerga o que foi registrado
- [ ] T008 [P] Acrescentar `divulgacao_publicacaoresultado`, `divulgacao_situacaodivulgada` e `divulgacao_documentodoresultado` a `TABELAS_APPEND_ONLY` em `backend/processo_seletivo/seguranca/papeis.py`
- [ ] T009 [P] Acrescentar `resultado:publicar` ao papel Publicador em `backend/processo_seletivo/interface/identidade.py`
- [ ] T010 [P] Criar a fixture de publicação de resultado em `backend/tests/fixtures/divulgacao.py`, no molde de `tests/fixtures/publicacao.py`
- [ ] T011 Escrever o teste de privilégio em `backend/tests/integration/divulgacao/test_imutabilidade.py`: o papel de runtime não consegue `UPDATE` nem `DELETE` nas três tabelas
- [ ] T012 [P] Escrever o teste das três triggers absolutas em `backend/tests/integration/divulgacao/test_imutabilidade.py`: a mutação é recusada mesmo por quem tem privilégio
- [ ] T013 [P] Escrever o teste da trigger de coerência em `backend/tests/integration/divulgacao/test_cadeia.py`: predecessor de outro marco recusado, e `PRELIMINAR` sucedendo `DEFINITIVA` recusada

**Checkpoint**: o teste estrutural de migrations enxerga as quatro triggers, e nenhuma linha destas
três tabelas pode ser alterada por nenhum caminho.

---

## Phase 3: US1 — Publicar um resultado constituído (P1)

**Meta**: a autoridade publicadora seleciona um ato emitido, confere o que será divulgado e
confirma; nasce a publicação, com autor, instante e signatário.

**Teste independente**: com um ato emitido e vigente, `paula.publicadora` publica pela interface; e
as três recusas de obsolescência aparecem nomeadas na tela quando o ato não é publicável.

- [ ] T014 [US1] Escrever `compor(ato)` em `backend/processo_seletivo/divulgacao/domain/conteudo.py`: as **duas** projeções a partir do ato, das posições, das inscrições (nome e protocolo) e dos rótulos da versão que o ato cita — a pública sem identificador, sem dado pessoal interno e sem `desempate`; a individual com a situação de cada participante considerado
- [ ] T015 [P] [US1] Escrever `aferir(edital, marco_id, ato)` em `backend/processo_seletivo/divulgacao/domain/publicabilidade.py`: lê `estado_do_marco` e devolve informação, aviso e impedimento, com as três formas nomeadas conforme [contracts/publicacao.md](./contracts/publicacao.md)
- [ ] T016 [US1] Escrever o comando em `backend/processo_seletivo/divulgacao/application/publicar.py`, na ordem exata do contrato: `require_permission` fora da transação; `select_for_update` no `ProcessoSeletivo`; `reserve`; aferição; composição; conferência da assinatura; gravação da publicação e das situações; `auditar`; `finish`
- [ ] T017 [US1] Escrever os seletores `vigente_do_marco` e `publicacao_por_id` em `backend/processo_seletivo/divulgacao/application/selectors.py`
- [ ] T018 [US1] Acrescentar as três rotas de [contracts/publicacao.md](./contracts/publicacao.md) em `backend/processo_seletivo/interface/urls.py`
- [ ] T019 [US1] Escrever `previa_de_publicacao` e `publicar_resultado` em `backend/processo_seletivo/interface/views.py`
- [ ] T020 [US1] Escrever o template da prévia em `backend/processo_seletivo/interface/templates/interface/previa_de_publicacao.html`, com natureza, autoridade, o conteúdo a divulgar, as consequências do ato e a confirmação inequívoca
- [ ] T021 [US1] Oferecer a ação "Publicar resultado" na tela do ato, condicionada a `resultado:publicar`, em `backend/processo_seletivo/interface/acoes.py` e no template de `ato_de_ordenacao`
- [ ] T022 [P] [US1] Testar a composição em `backend/tests/unit/divulgacao/test_conteudo.py`: rótulos resolvidos, empate residual como posição compartilhada, natureza como texto, e quem não recebeu posição **fora** da projeção pública e **dentro** da individual
- [ ] T023 [P] [US1] Testar a publicabilidade em `backend/tests/unit/divulgacao/test_publicabilidade.py`: ato sucedido, ato divergente e marco removido — cada um com o seu código
- [ ] T024 [P] [US1] Testar os bytes gravados em `backend/tests/contract/test_conteudo_divulgado.py`: `conteudo_publico` não contém CPF, e-mail, `identity_subject`, identificador de inscrição, valor de desempate, UUID fora de `cabecalho.ato.id` nem enum como texto
- [ ] T025 [US1] Testar o comando em `backend/tests/integration/divulgacao/test_publicar.py`: nasce a publicação com autor, instante e signatário, uma `SituacaoDivulgada` por participante, e a trilha registra ator, entidade, instante e versão
- [ ] T026 [US1] Testar a idempotência em `backend/tests/integration/divulgacao/test_publicar.py`: a mesma chave repetida devolve o desfecho da primeira e não cria segunda publicação
- [ ] T027 [US1] Testar a unicidade por natureza em `backend/tests/integration/divulgacao/test_publicar.py`: **duas chaves diferentes** sobre o mesmo ato e a mesma natureza são recusadas pela constraint — o caso que a idempotência não pega
- [ ] T028 [US1] Testar a assinatura em `backend/tests/integration/divulgacao/test_publicar.py`: `confirmacao_da_previa` calculada sobre outra projeção, ou sobre outra ponta da cadeia, recusa com `409`; e a assinatura da prévia **não** contém o instante
- [ ] T029 [US1] Testar a serialização em `backend/tests/integration/divulgacao/test_concorrencia.py`: publicar e `emitir_ordem` concorrentes não terminam com a divulgação de um ato já sucedido — exige PostgreSQL
- [ ] T030 [P] [US1] Testar a autorização em `backend/tests/authorization/test_publicacao_de_resultado.py`: sem `resultado:publicar` é `403`, **inclusive** para o presidente que emitiu o ato; escopo institucional alheio é `404`
- [ ] T031 [P] [US1] Testar a interface em `backend/tests/interface/test_publicar_resultado.py`: a ação aparece para quem tem a capacidade e não aparece para quem não tem; e a prévia não grava linha alguma

**Checkpoint**: a jornada administrativa fecha sozinha — publicar, recusar e conferir a trilha.

---

## Phase 4: US2 — Consultar o resultado publicado (P1)

**Meta**: qualquer pessoa abre o resultado por um endereço estável, sem conta, e entende o que é, de
qual Edital, quando foi publicado e se ainda vale.

**Teste independente**: sem autenticação, abrir o endereço de uma publicação e ler a lista; e
chegar nela a partir da página pública do Edital, sem conhecer o endereço.

- [ ] T032 [US2] Acrescentar as rotas `resultados/<uuid:publicacao_id>/` e `resultados/<uuid:publicacao_id>/documento.pdf` em `backend/processo_seletivo/portal/urls.py`
- [ ] T033 [US2] Escrever `resultado` em `backend/processo_seletivo/portal/views.py`: consulta a publicação e a cadeia, desserializa `conteudo_publico` e **não** alcança `Inscricao`, `PosicaoNaOrdem`, `VersaoConsolidada` nem `SituacaoDivulgada`
- [ ] T034 [US2] Escrever o template em `backend/processo_seletivo/portal/templates/portal/resultado.html`, com natureza em texto, instante, autoridade, o aviso de sucessão quando houver e a lista com posições compartilhadas
- [ ] T035 [US2] Listar as publicações vigentes dos marcos do Edital em `backend/processo_seletivo/portal/views.py` (`selecao`) e em `backend/processo_seletivo/portal/templates/portal/selecao.html`
- [ ] T036 [P] [US2] Testar a página em `backend/tests/portal/test_resultado_publico.py`: sem autenticação, mostra posições, nomes, protocolos, rótulos institucionais e o instante — e nenhum UUID como informação
- [ ] T037 [P] [US2] Testar o empate em `backend/tests/portal/test_resultado_publico.py`: 1º, 2º, 3º, 3º renderizados como posições compartilhadas
- [ ] T038 [P] [US2] Testar a sucessão em `backend/tests/portal/test_resultado_publico.py`: a publicação sucedida diz que foi sucedida, oferece o caminho para a vigente e mantém o conteúdo intacto
- [ ] T039 [P] [US2] Testar a fronteira em `backend/tests/portal/test_fronteira_publica.py`: nada de quem está apenas em `SituacaoDivulgada` aparece no **HTML renderizado**, e a view não emite consulta àquela tabela
- [ ] T040 [P] [US2] Testar a responsividade em `backend/tests/interface/test_responsividade.py` (ou equivalente do portal): `scrollWidth === 375` na página do resultado
- [ ] T041 [US2] Testar o custo em `backend/tests/performance/test_resultado_publico.py`: número de consultas **igual** entre 10 e 1.000 posições, no molde de `test_public_queries.py` — a asserção é sobre consultas, não sobre tempo

**Checkpoint**: o resultado existe publicamente e é encontrável por quem só conhece o Edital.

---

## Phase 5: US3 — Encontrar o resultado na própria Inscrição (P1)

**Meta**: a publicação que diz respeito à Inscrição aparece dentro dela, e nada aparece antes.

**Teste independente**: o mesmo acompanhamento, antes e depois de publicar.

- [ ] T042 [US3] Escrever `situacao_do_candidato(inscricao)` em `backend/processo_seletivo/divulgacao/application/selectors.py`: busca `SituacaoDivulgada` pela Inscrição e fica com a linha cuja publicação é a vigente
- [ ] T043 [US3] Acrescentar a chave de contexto a `acompanhamento` em `backend/processo_seletivo/portal/views.py`, **sem alterar** `_fatos_da_participacao` — ele descreve fatos da própria inscrição, e a publicação é ato de terceiro
- [ ] T044 [US3] Acrescentar o bloco em `backend/processo_seletivo/portal/templates/portal/acompanhamento.html`, com natureza, posição e pontuação, ou situação e motivo, e o caminho para o resultado completo
- [ ] T045 [P] [US3] Testar a ausência em `backend/tests/portal/test_acompanhamento_resultado.py`: com ato emitido e **nenhuma** publicação, o acompanhamento não menciona resultado por nenhum caminho
- [ ] T046 [P] [US3] Testar a presença em `backend/tests/portal/test_acompanhamento_resultado.py`: publicada, a candidata classificada vê natureza, posição, pontuação e o caminho
- [ ] T047 [P] [US3] Testar o não classificado em `backend/tests/portal/test_acompanhamento_resultado.py`: vê a própria situação e o motivo, e o seu nome **não** está na página pública
- [ ] T048 [P] [US3] Testar a sucessão em `backend/tests/portal/test_acompanhamento_resultado.py`: publicada P2, o caminho da Área leva à vigente
- [ ] T049 [P] [US3] Testar o isolamento em `backend/tests/authorization/test_publicacao_de_resultado.py`: uma candidata não alcança a situação de outra, com `404` uniforme

**Checkpoint**: o gate de produto da feature — o resultado chegou à pessoa.

---

## Phase 6: US4 — Documento oficial (P2)

**Meta**: a publicação produz um artefato imprimível com o mesmo conteúdo, e ele não é regenerado.

**Teste independente**: baixar o documento pela página pública e conferir cabeçalho, autoridade e
resumo; retificar o Edital e conferir que os bytes não mudaram.

- [ ] T050 [US4] Escrever `render_resultado_pdf(conteudo)` em `backend/processo_seletivo/divulgacao/infrastructure/documento.py`, montando uma `Composicao` e chamando `render_documento`, com `_tabela` para a lista — no molde de `inscricoes/infrastructure/comprovante_pdf.py`
- [ ] T051 [US4] Gravar `DocumentoDoResultado` dentro do comando, em `backend/processo_seletivo/divulgacao/application/publicar.py`, derivando **do conteúdo já composto**
- [ ] T052 [US4] Escrever `resultado_em_pdf` em `backend/processo_seletivo/portal/views.py`, devolvendo os bytes gravados com `ETag` igual ao `documento_hash`, no molde de `PublishedDocumentView`
- [ ] T053 [P] [US4] Testar o conteúdo em `backend/tests/unit/divulgacao/test_documento.py`: Processo/Edital, marco, natureza, ato de origem, data e hora, autoridade signatária, a lista e o resumo criptográfico
- [ ] T054 [P] [US4] Testar o determinismo em `backend/tests/unit/divulgacao/test_documento.py`: a mesma composição produz os mesmos bytes, sem data de criação embutida
- [ ] T055 [P] [US4] Testar a estabilidade em `backend/tests/integration/divulgacao/test_publicar.py`: Retificação posterior do Edital não altera os bytes nem regenera o documento

**Checkpoint**: existe a forma documental do ato, e ela é conferível.

---

## Phase 7: US5 — Histórico e sucessão (P2)

**Meta**: a gestão e a auditoria veem o que foi divulgado, quando, por quem, e o que vale hoje.

**Teste independente**: com P1 sucedida por P2, abrir o histórico do marco.

- [ ] T056 [US5] Escrever `historico_do_marco` em `backend/processo_seletivo/divulgacao/application/selectors.py`, devolvendo a cadeia com natureza, instante, autor, autoridade e situação
- [ ] T057 [US5] Escrever `publicacoes_do_marco` em `backend/processo_seletivo/interface/views.py`, aberta a `resultado:publicar` **ou** `auditoria:consultar`
- [ ] T058 [US5] Escrever o template em `backend/processo_seletivo/interface/templates/interface/publicacoes_do_marco.html`
- [ ] T059 [P] [US5] Testar a listagem em `backend/tests/interface/test_publicacoes_do_marco.py`: as duas publicações, com a vigente identificada e a anterior marcada como sucedida
- [ ] T060 [P] [US5] Testar a autorização em `backend/tests/interface/test_publicacoes_do_marco.py`: a auditora consulta e **não** recebe a ação de publicar
- [ ] T061 [P] [US5] Testar a acessibilidade em `backend/tests/interface/test_publicacoes_do_marco.py`: a situação vigente/sucedida é legível sem depender de cor

**Checkpoint**: a pergunta "isto ainda vale?" tem resposta nos três canais.

---

## Phase 8: Polish

- [ ] T062 Executar o [quickstart](./quickstart.md) inteiro como teste de aceitação em `backend/tests/acceptance/test_us_publicacao_de_resultado.py`, cobrindo o gate da spec de ponta a ponta
- [ ] T063 [P] Testar os fluxos críticos por teclado — prévia, confirmação e página pública — em `backend/tests/javascript/` ou no teste de interface correspondente
- [ ] T064 [P] Acrescentar ao `seed_demo` o ator publicador com `resultado:publicar` e um resultado publicado, em `backend/processo_seletivo/processos/management/commands/seed_demo.py`
- [ ] T065 Conferir que `backend/tests/test_citacoes_de_requisito.py` continua verde e que nenhuma citação FR/SC introduzida aponta para requisito diferente do pretendido

---

## Dependencies

```text
Setup (T001–T003)
   ↓
Foundational (T004–T013)          ← bloqueia tudo
   ↓
US1 (T014–T031)                   ← bloqueia US2, US3, US4, US5
   ↓
   ├── US2 (T032–T041)  ─┐
   ├── US3 (T042–T049)  ─┤ independentes entre si
   └── US5 (T056–T061)  ─┘
   ↓
US4 (T050–T055)                   ← depende de US1; T052 depende de US2 (rota do portal)
   ↓
Polish (T062–T065)
```

**Por que US1 bloqueia as demais**: as quatro seguintes leem publicações, e não há publicação antes
do comando existir. Não é acoplamento evitável — é a ordem do domínio.

**Por que US4 vem depois de US3**: decisão da spec. O documento é institucionalmente importante, mas
a validação de produto é o resultado chegar ao candidato, e ela vem antes.

**Até a US4, publicações nascem sem documento.** `DocumentoDoResultado` é tabela própria, e a
ausência de linha representa isso sem deixar coluna a limpar.

## Parallel opportunities

- **Foundational**: T007, T008, T009, T010 tocam arquivos distintos e correm juntas depois de T006;
  T012 e T013 também.
- **US1**: T022, T023, T024, T030 e T031 são arquivos distintos. T015 é paralela a T014.
- **US2**: T036 a T040 são independentes; T041 depende de T033.
- **US3**: T045 a T049 são independentes entre si.
- **US4**: T053, T054 e T055 são independentes.
- **US5**: T059, T060 e T061 compartilham arquivo — paralelas só se escritas em conjunto.

## Implementation Strategy

**MVP**: Setup + Foundational + US1 + US2. Nesse ponto a instituição publica e o público consulta —
é a borda institucional fechada, ainda sem a jornada do candidato.

**Incremento seguinte**: US3, que é o que transforma a feature em valor percebido, e é o que a spec
elegeu como validação de produto.

**Depois**: US4 e US5, em qualquer ordem, com US5 preferencialmente por último — a sucessão se
exerce melhor sobre publicações que já existem do que sobre fixtures.

## Notes

- [P] = arquivos diferentes, sem dependência
- [Story] mapeia a tarefa para a história, e é o que sustenta a rastreabilidade do Princípio V
- Verifique que o teste falha antes de implementar
- Commit por tarefa ou grupo lógico
- A varredura de vocabulário da 013 (`tests/test_vocabulario_do_resultado.py`) lê apenas
  `interface/templates`: os templates do `portal` desta feature afirmam classificação
  legitimamente, e a varredura **não** deve ser estendida a eles
