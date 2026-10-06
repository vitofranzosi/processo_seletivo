# Tasks: Unidades institucionais e autoridades de publicação

**Input**: Design documents from `specs/060-unidades-e-autoridades/`

**Tests**: pedidos — a rastreabilidade é verificada por teste (`test_citacoes_de_requisito.py` cobra a
matriz requisito a requisito), e cada requisito aponta o que o prende
([rastreabilidade.md](rastreabilidade.md), T048).

Caminhos relativos a `backend/` quando começam por `processo_seletivo/` ou `tests/`. **R-NNN** remete
a [research.md](research.md).

**A suíte fica verde ao fim de cada fase** (plan, *Ordem de implementação*). Nenhuma regra que leia a
Unidade ou a autoridade entra antes da fixture que as garante (T008).

## Phase 1: Setup

- [ ] T001 Banco de teste próprio (`DB_NAME=ps_060`, `.env` da worktree) e `uv sync --extra dev`; medir a linha de base com `make lint check test-pg DB_NAME=ps_060` e anotar passados e pulados no topo de [rastreabilidade.md](rastreabilidade.md) antes de qualquer mudança

## Phase 2: Foundational (bloqueia todas as histórias)

**O registro e a fixture.** Sem consumidor ainda: nada do que existe muda de comportamento nesta fase.

- [ ] T002 Criar o app `unidades` (`__init__.py`, `apps.py`, `models.py`, `domain/`, `application/`, `management/commands/`, `migrations/`) e registrá-lo em `INSTALLED_APPS` com o comentário do porquê, em processo_seletivo/unidades/ e config/settings/base.py; linha `| `unidades` |` na tabela de módulos de README.md (R-001)
- [ ] T003 Modelos `Unidade` e `AutoridadeHabilitada` com os campos, `CHECK`s e índices de [data-model.md](data-model.md) — `codigo` único, 1 a 2 linhas em `cabecalho`, `fim ≥ início`, completude do encerramento —, e a migration 0001, em processo_seletivo/unidades/models.py e processo_seletivo/unidades/migrations/0001_initial.py (FR-1106, FR-1116, FR-1120)
- [ ] T004 Migration 0002 com os cinco gatilhos de R-006 — `unidade_nao_se_exclui`, `autoridade_nao_se_exclui`, `unidade_codigo_imutavel`, `autoridade_unidade_imutavel` (sempre) e `autoridade_usada_imutavel` (campos de identidade, e fim anterior ao dia do primeiro uso no fuso `America/Sao_Paulo`, escrito por extenso) —, `RunPython` com reverso, no-op fora do PostgreSQL, constantes copiadas e não importadas, no padrão de `requerimentos/0002`, em processo_seletivo/unidades/migrations/0002_nada_se_exclui.py; o app em `APPS` e os cinco nomes em `TRIGGERS_POR_APP["unidades"]` em tests/migrations/test_migrations.py (FR-1108, FR-1109, FR-1120, FR-1121)
- [ ] T005 [P] Regras puras: `vigente(autoridade, data)` e `situacao(autoridade, hoje)` (*futura*, *vigente*, *encerrada*), em processo_seletivo/unidades/domain/vigencia.py; `GERIR = "autoridade:gerir"` e os códigos de recusa de [contracts/autoridades-e-publicacao.md](contracts/autoridades-e-publicacao.md) em processo_seletivo/unidades/domain/nomes.py; `quem_assinou` copiado de publicacoes/domain/autoridades.py (a original sai em T030) e `rotulo_da_autoridade` em processo_seletivo/unidades/domain/rotulos.py (FR-1119, UX-148)
- [ ] T006 `unidades.json` com a entrada do Cefor de [contracts/registro-de-unidades.md](contracts/registro-de-unidades.md) — as linhas e o local que `pdf.ORGAO` e `pdf.LOCAL` têm hoje —; `sincronizar(arquivo, now)` numa transação, criando, alterando, mantendo, recusando `unidade_retirada` e `unidade_malformada`, e gravando `REGISTRAR_UNIDADE`/`ALTERAR_UNIDADE` com ator `implantacao` e `detalhe` antes/depois, em processo_seletivo/unidades/unidades.json e processo_seletivo/unidades/application/sincronizacao.py; o comando com a linha de saída do contrato em processo_seletivo/unidades/management/commands/sincronizar_unidades.py; o alvo `preparar` roda o comando depois da segunda passada do provisionamento em Makefile (R-003; FR-1108, FR-1109, FR-1111)
- [ ] T007 [P] Selectors `unidade_ativa(codigo)`, `unidade(codigo)` e `autoridades_vigentes(codigo, data)` (ordem cargo, nome), em processo_seletivo/unidades/application/selectors.py (FR-1119, FR-1125)
- [ ] T008 A fixture `autouse` de R-012 em tests/conftest.py, ativa só com banco (marcador `django_db` ou fixtures `db`/`transactional_db`), que garante por `get_or_create` a Unidade `cefor` com os valores de `unidades.json` e as duas autoridades de teste; as constantes `AUTORIDADE_DA_SUITE` (id `…000000000601`, nome `Diretora`, cargo `Diretora-Geral`), `AUTORIDADE_DO_RESULTADO` (o cargo do `diretoria-cefor` de hoje, sem nome), ambas com início em 2000-01-01, `UNIDADE_DA_SUITE` (para o compositor) e um helper `registrar_unidade(codigo, **campos)` para os testes de outra unidade, em tests/fixtures/autoridades.py
- [ ] T009 Testes do registro: modelos e `CHECK`s; os cinco gatilhos (exclusão recusada nas duas tabelas, código imutável, unidade da autoridade imutável antes e depois do uso, autoridade usada imutável e encerrável, fim anterior ao dia do primeiro uso recusado pelo banco mesmo gravado direto, com `usada_em` perto da meia-noite no fuso institucional) — pulados fora do PostgreSQL —; sincronização idempotente, criação, alteração com trilha, retirada e arquivo malformado recusados sem gravar nada; vigência nos limites e no fuso; situação derivada, em tests/unidades/test_registro.py, tests/unidades/test_sincronizacao.py e tests/unidades/test_vigencia.py (FR-1106–FR-1111, FR-1119, FR-1120; SC-434)
- [ ] T010 Rótulos de `REGISTRAR_UNIDADE` e `ALTERAR_UNIDADE` em `OPERACOES` de processo_seletivo/interface/views.py (`test_trilha_legivel.py`)

**Checkpoint**: suíte verde; o registro existe, ninguém o lê ainda.

## Phase 3: User Story 1 — O documento diz a unidade que o praticou (P1) 🎯 MVP

**Goal**: cabeçalho e local de cada documento vêm da Unidade do Edital; o Cefor sai idêntico.

**Independent Test**: com duas unidades registradas, publicar um Edital em cada; cada documento traz o cabeçalho e o local da própria unidade, e a fixture de bytes da `054` passa sem ser refeita.

- [ ] T011 [US1] `INSTITUICAO` e `UnidadeDoAto(cabecalho, local)` no lugar de `ORGAO` e `LOCAL`; `_cabecalho` e `fecho` recebem a unidade; `render_edital_pdf(..., unidade)` obrigatório nos dois modos, sem padrão, em processo_seletivo/publicacoes/infrastructure/pdf.py (R-008; FR-1112, FR-1113)
- [ ] T012 [US1] A fixture de bytes passa a compor com a Unidade do Cefor, versionada em tests/contract/fixtures/unidade_publicada.json, lida por tests/contract/test_documento_publicado.py e por scripts/gerar_fixture_documento.py; **`documento_publicado_v1.pdf` não é refeito** — se divergir, o defeito está em T011 (FR-1114; SC-430)
- [ ] T013 [US1] As ~33 chamadas diretas a `render_edital_pdf` nos testes passam `unidade=UNIDADE_DA_SUITE` — tests/unit/publicacoes/test_pdf.py, test_fecho_e_normas_da_054.py, test_pdf_documentos_exigidos.py, tests/integration/publicacoes/test_publicar_edital.py e os que a suíte acusar
- [ ] T014 [US1] `Publicacao.unidade_codigo`, `unidade_sigla`, `unidade_nome`, `unidade_cabecalho` e `unidade_local`, e a migration 0010, em processo_seletivo/publicacoes/models.py e processo_seletivo/publicacoes/migrations/0010_unidade_do_ato.py; subir `publicacoes` de 9 para 10 nos dois guardiões de tests/migrations/test_migrations.py, cada um com o parágrafo *"Sobe para 10 com a 060"* (R-007; FR-1128)
- [ ] T015 [US1] `publish_edital` e `publish_retification` leem a Unidade do Edital (`unidades.application.selectors.unidade`), congelam as cinco colunas e passam `UnidadeDoAto` ao compositor; o consolidado usa a Unidade da própria Retificação, em processo_seletivo/publicacoes/application/publish_edital.py e processo_seletivo/publicacoes/application/retificacoes.py (FR-1112, FR-1113, FR-1128, FR-1130)
- [ ] T016 [US1] A prévia do Edital compõe com a Unidade registrada no momento, em `previa_documento` de processo_seletivo/interface/views.py (FR-1112)
- [ ] T017 [US1] `PublicacaoResultado` ganha as cinco colunas `unidade_*` e `signatario_ato_de_nomeacao`, com a migration 0004 e a contagem de `divulgacao` de 3 para 4 nos guardiões, em processo_seletivo/divulgacao/models.py, processo_seletivo/divulgacao/migrations/ e tests/migrations/test_migrations.py; `conteudo_divulgado(..., unidade)` põe `unidade` no `cabecalho`, em processo_seletivo/divulgacao/domain/conteudo.py; `publicar_resultado` lê a Unidade do Edital e congela as colunas, em processo_seletivo/divulgacao/application/publicar.py; `_timbre` lê `cabecalho.unidade`, em processo_seletivo/divulgacao/infrastructure/documento.py; as chamadas em tests/unit/divulgacao/test_conteudo.py, test_documento.py e tests/unit/publicacoes/test_pdf_do_sorteio.py passam a unidade (R-007, R-008; FR-1112, FR-1128)
- [ ] T018 [US1] O comprovante lê a unidade de `versao.source_publication.unidade_*`: `_dados_do_comprovante` e `_selecao` (no lugar de `institution_scope.upper()`) em processo_seletivo/portal/views.py; `_timbre(composicao, unidade)` em processo_seletivo/inscricoes/infrastructure/comprovante_pdf.py; o texto fixo de processo_seletivo/portal/templates/portal/comprovante.html sai para os dados (R-008; FR-1112, FR-1115)
- [ ] T019 [US1] Criar Processo e Edital exige Unidade ativa — `unidade_nao_registrada` (422) — em `create_process_with_first_edital` e `add_edital`, em processo_seletivo/processos/application/commands.py; o único arquivo de teste que cria pela API com outro escopo registra a unidade com `registrar_unidade` (R-011; FR-1110)
- [ ] T020 [US1] Testes da unidade no documento: duas unidades, quatro documentos, nenhum traço do Cefor no da outra; prévia com a unidade de agora; renomear a unidade entre o Edital e a Retificação e conferir cada documento com o nome do seu dia; comprovante com a unidade da Publicação mesmo depois de renomeada; criação recusada sem unidade e com unidade desativada, e atos sobre o existente na desativada continuam, em tests/unidades/test_documento_da_unidade.py e tests/unidades/test_criacao_exige_unidade.py (FR-1110, FR-1112–FR-1115, FR-1128–FR-1130; SC-429, SC-430, SC-433)

**Checkpoint**: US1 demonstrável — quickstart §3, passos 1 a 3.

## Phase 4: User Story 2 — Publicar escolhendo só quem pode responder pela unidade (P1)

**Goal**: a autoridade é conferida no domínio, sob trava, pela unidade e pela vigência; a Publicação a congela do registro.

**Independent Test**: com autoridades em duas unidades, cada publicação oferece só as da sua; a da outra unidade, a encerrada e a inexistente são recusadas sem nada gravado.

- [ ] T021 [US2] `autoridade_para_o_ato(autoridade_id, *, unidade_codigo, data_do_ato)` — `select_for_update`, unidade, vigência, `usada_em` se nula; `autoridade_indisponivel` para inexistente e de outra unidade com a mesma mensagem, `autoridade_fora_de_vigencia` com o período —, em processo_seletivo/unidades/application/autoridades.py (R-005; FR-1121, FR-1125, FR-1126)
- [ ] T022 [US2] `publish_edital(autoridade_id=…)` e `publish_retification(autoridade_id=…)` chamam T021 antes de compor e preenchem `signatory_*` da linha devolvida; o payload de idempotência guarda o identificador, em processo_seletivo/publicacoes/application/publish_edital.py e processo_seletivo/publicacoes/application/retificacoes.py (FR-1125, FR-1126, FR-1128)
- [ ] T023 [US2] `publicar_resultado(autoridade="<identificador>")` chama T021 no lugar de `escolher`, grava `signatario_ato_de_nomeacao` e o põe no `cabecalho`, em processo_seletivo/divulgacao/application/publicar.py e processo_seletivo/divulgacao/domain/conteudo.py; `conferir_natureza_e_autoridade` e `_publicar` pelo identificador, em processo_seletivo/interface/conducao_do_marco.py (FR-1125, FR-1128)
- [ ] T024 [US2] API: `SignatorySerializer` só com `authorityId`, `400` para `name`/`role`/`appointment`, em processo_seletivo/publicacoes/api/serializers.py e processo_seletivo/publicacoes/api/views.py; o `SignatorySnapshot` emendado em specs/001-processo-seletivo-editais/contracts/openapi.yaml (R-014)
- [ ] T025 [US2] Os helpers dos testes mandam o identificador: `SIGNATORY = {"authorityId": AUTORIDADE_DA_SUITE}` em tests/fixtures/publicacao.py; o padrão de `publicar_o_ato` vira o id de `AUTORIDADE_DO_RESULTADO` em tests/fixtures/divulgacao.py; à mão, as passagens explícitas de `"diretoria-cefor"`/`"reitoria"`, os dicionários de signatário por extenso e as chaves negativas (`"prefeitura-de-outro-lugar"`, `"prefeitura-alheia"` viram UUID aleatório), nos arquivos que o relatório de 06/10 lista em R-012 e nos que a suíte acusar — um a um, sem afrouxar asserção
- [ ] T026 [US2] As telas oferecem `autoridades_vigentes(unidade do Edital, hoje)` com `rotulo_da_autoridade` e o identificador como valor; sem nenhuma vigente, a frase de FR-1127 e o botão desabilitado; `_executar` e `praticar_ato_retificacao` mandam `autoridade_id`, em processo_seletivo/interface/views.py e nos templates processo_seletivo/interface/templates/interface/confirmar.html, retificacao_confirmar.html, previa_de_publicacao.html, marco.html e marco_conferir.html (R-010; FR-1125, FR-1127, UX-148)
- [ ] T027 [US2] `seed_demo` sincroniza as unidades, cadastra as autoridades de que precisa pelo ORM — o comando de aplicação chega em T033 e T034 troca — e publica com os identificadores, em processo_seletivo/processos/management/commands/seed_demo.py; tests/integration/test_seed_demo.py acompanha (R-013)
- [ ] T028 [US2] Testes da escolha e da recusa: só as vigentes da unidade aparecem, nos três fluxos e no gesto do marco; outra unidade, encerrada ontem (fim gravado pela fixture, porque o comando recusa encerramento retroativo), futura e inexistente recusadas sem Publicação gravada; encerramento concorrente entre a tela e a confirmação (trava, PostgreSQL); `usada_em` preenchida no primeiro ato e mantida no segundo; frase e botão sem autoridade vigente; API recusa `name`, em tests/unidades/test_publicar_com_autoridade.py, tests/unidades/test_concorrencia_da_autoridade.py e tests/interface/test_escolha_da_autoridade.py (FR-1125–FR-1128, UX-148; SC-431)
- [ ] T029 [US2] Testes do congelamento: a Publicação de Edital, de Retificação e de Resultado guarda nome, cargo, ato de nomeação, identificador e unidade da linha; encerrar a autoridade e renomear a unidade depois não muda a Publicação, a consulta nem o documento, em tests/unidades/test_publicacao_autocontida.py (FR-1128, FR-1129; SC-433)
- [ ] T030 [US2] O catálogo sai: publicacoes/domain/autoridades.py é removido; `selectors.participantes_do_edital` e os templates que repetiam `quem_assinou` (`publicacoes_do_marco.html`) passam a usar processo_seletivo/unidades/domain/rotulos.py; tests/interface/test_autoridades.py é **substituído** pelos testes desta fase, e as asserções sobre o catálogo saem de tests/unit/publicacoes/test_fecho_e_normas_da_054.py, ficando as do fecho (R-012; FR-1117, FR-1124)

**Checkpoint**: US1 + US2 — a publicação só aceita quem responde pela unidade.

## Phase 5: User Story 3 — Manter as autoridades da unidade sem mudar o sistema (P2)

**Goal**: o Gestor cadastra, corrige e encerra as autoridades da própria unidade, com trilha.

**Independent Test**: cadastrar, publicar com ela, tentar corrigir (recusado), encerrar, cadastrar outra, publicar de novo; a primeira Publicação não muda e a trilha registra tudo.

- [ ] T031 [US3] `autoridade:gerir` no papel `gestor`, escrita por extenso com o comentário do porquê, em processo_seletivo/interface/identidade.py; teste no molde de tests/authorization/test_visao_institucional.py — a constante de `unidades.domain.nomes` igual à do mapa, no Gestor e em nenhum outro papel —, em tests/authorization/test_gerir_autoridades.py (D-005; FR-1122)
- [ ] T032 [US3] `cadastrar`, `corrigir` e `encerrar` em processo_seletivo/unidades/application/autoridades.py: `require_permission(GERIR, institution_scope=…)`, unidade ativa do escopo, trava da linha, idempotência, recusas de [contracts/autoridades-e-publicacao.md](contracts/autoridades-e-publicacao.md) (`autoridade_ja_usada` com a orientação de encerrar e cadastrar outra), e `record_event` com `CADASTRAR_AUTORIDADE`/`CORRIGIR_AUTORIDADE`/`ENCERRAR_AUTORIDADE`, `new_state=""`, `new_revision=None` e `detalhe` antes/depois; os três rótulos em `OPERACOES` de processo_seletivo/interface/views.py (FR-1120–FR-1123)
- [ ] T033 [US3] A tela `/gestao/autoridades`: view GET/POST por `acao`, porta por `require_authorization_base` nomeando a permissão, 404 para autoridade de outra unidade, escopo sem unidade registrada; `ler_autoridade` em processo_seletivo/interface/forms.py; rota em processo_seletivo/interface/urls.py; template com os três grupos e o período (UX-149), em processo_seletivo/interface/views.py e processo_seletivo/interface/templates/interface/autoridades.html; classes novas com regra na folha de base.html; botão *"Autoridades da unidade"* sob `pode_gerir_autoridades` em processo_seletivo/interface/templates/interface/lista.html e no contexto de `views.lista` (R-009; FR-1122, UX-149, UX-150)
- [ ] T034 [US3] `seed_demo` passa a cadastrar as autoridades por `cadastrar`, com um Gestor, em processo_seletivo/processos/management/commands/seed_demo.py (R-013)
- [ ] T035 [US3] A função nova que levanta `Http404` entra em specs/033-navegacao-por-capacidade/inventario-das-negativas.md, classe *"escopo institucional ∪ inexistente"*, linha *"acrescentada pela `060`"* (`test_gramatica_das_portas.py`)
- [ ] T036 [US3] Testes de aplicação: cadastrar e encerrar com trilha; corrigir antes do uso grava antes e depois, inclusive o início da vigência; corrigir depois do uso recusado com a orientação; fim antes do início recusado; fim ontem recusado com `encerramento_retroativo` e fim hoje aceito — oferecida hoje, fora das opções amanhã, com o relógio no fuso institucional perto da meia-noite; outra unidade indistinguível de inexistente; unidade desativada continua recebendo cadastro, correção e encerramento, e continua exigindo permissão e escopo, em tests/unidades/test_manter_autoridades.py (FR-1110, FR-1120–FR-1123)
- [ ] T037 [US3] Testes da tela: sem a permissão, 403 que nomeia `autoridade:gerir`; botão só com a permissão; três grupos com período; cadastro → `?feito=cadastrar`; 404 para a de outra unidade; escopo sem unidade; a unidade pelo nome, nunca pelo código, em tests/interface/test_tela_de_autoridades.py (FR-1122, UX-149, UX-150)
- [ ] T038 [US3] Teste de percurso: cadastrar, publicar, encerrar, cadastrar outra, publicar — a primeira Publicação intacta, a segunda com a nova, a publicação seguinte oferece só a nova, em tests/acceptance/test_us_trocar_a_autoridade.py (SC-432, SC-433)

**Checkpoint**: US3 demonstrável pela interface — quickstart §4.

## Phase 6: User Story 4 — A consulta pública diz a unidade do ato (P3)

**Goal**: a consulta pública da Publicação expõe a unidade congelada.

**Independent Test**: consultar a Publicação de um Edital de cada unidade e conferir unidade, autoridade e ato de nomeação.

- [ ] T039 [US4] `unit: {code, acronym, name}` lido das colunas congeladas em `PublicacaoDetalheSerializer`, em processo_seletivo/publicacoes/api/public_serializers.py; `SignatarioRegistrado` com `unit` em specs/001-processo-seletivo-editais/contracts/openapi.yaml (R-014; FR-1131)
- [ ] T040 [US4] A tela de detalhe do Edital diz a unidade ao lado da Autoridade Signatária, por `participantes_do_edital`, em processo_seletivo/publicacoes/application/selectors.py e processo_seletivo/interface/templates/interface/detalhe.html (FR-1131, UX-150)
- [ ] T041 [US4] Testes: a consulta traz a unidade do dia mesmo depois de renomeada; sem nome, só o cargo, sem separador pendurado, em tests/contract/test_consulta_publica_api.py e tests/unidades/test_consulta_publica_da_unidade.py (FR-1131)

**Checkpoint**: todas as histórias.

## Phase 7: Polish & Cross-Cutting

- [ ] T042 [P] Notas de emenda no próprio texto: `FR-039` da specs/007-edital-institucional/spec.md (*revogada pela `060`, FR-1124*); `FR-989` e a decisão 005 em specs/054-edital-como-ato-oficial/spec.md; `FR-029` em specs/017-publicacao-de-resultados/spec.md (R-015)
- [ ] T043 [P] Varredura: nenhuma ocorrência de `ORGAO`, `LOCAL`, `CATALOGO`, `escolher(` ou `"diretoria-cefor"` em processo_seletivo/; `grep -rn "Centro de Referência\|Vitória (ES)" processo_seletivo` só em `unidades.json` e em comentários que contam a história (SC-429)
- [ ] T044 Registrar as pendências de R-016 — a marca *"Cefor/Ifes"*, as frases *"a quem administra o sistema no Cefor"*, a vitrine sem a unidade e o seletor de identidade preso ao escopo padrão — e as duas de implantação — a confirmação da base legal pelo encarregado de dados do Ifes (spec, *Assumptions*, LGPD) e o cadastro das três autoridades do Cefor (FR-1124, quickstart §7) — em doc/pendencias-da-060.md, sem implementá-las
- [ ] T045 Quickstart §3 e §6 num banco próprio (`ps_060_demo`): dois documentos lidos com `pdftotext -layout`, recusa entre unidades, exclusão recusada pelo gatilho; e §4 no preview, a 1280×900 e a 375×812
- [ ] T046 Medir a suíte com `make lint check test-pg DB_NAME=ps_060` e comparar **listas**, não totais, com a linha de base de T001 (CLAUDE.md); atualizar os números de AGENTS.md — passados, pulados, e o total de migrations (85 → 89)
- [ ] T047 Conferir o CLAUDE.md: o `34 de 34` continua valendo (as tabelas da 060 não são append-only); acrescentar o parágrafo *"`make preparar` sincroniza as unidades"* onde o CLAUDE.md descreve a preparação do banco, se a mudança de T006 o tornar necessário
- [ ] T048 [P] rastreabilidade.md: cada FR, SC e UX da 060 com o lugar do código e o teste que o prende, no formato da `054` (`test_citacoes_de_requisito.py::test_a_matriz_de_rastreabilidade_cobre_todo_requisito_da_feature`)

## Dependencies & Execution Order

- **Phase 2 bloqueia tudo.** T003 → T004; T006 depende de T003; T008 depende de T003 e T006 (os valores do Cefor); T009 depende de T004–T007.
- **US1 (Phase 3)** depende só da Phase 2. T011 → T012, T013; T014 → T015; T017 e T018 dependem de T011 e T014.
- **US2 (Phase 4)** depende de T014 e T017 (as colunas que congela) e de T008 (as autoridades de teste). T021 → T022, T023 → T025, T026; T030 por último na fase.
- **US3 (Phase 5)** depende de T021 (a trava compartilhada) e de T030 (o catálogo fora). T031 → T032 → T033 → T035.
- **US4 (Phase 6)** depende de T014; pode correr junto da US3.
- **Polish**: T046 depois de tudo; T048 depois de T046, para citar os testes com o nome final.

## Parallel Opportunities

- Phase 2: T005 e T007 com T006.
- US1: T016 com T017 e T018, depois de T011 e T014.
- US2: T024 com T023; T028 e T029 (arquivos de teste distintos).
- US3 e US4 em paralelo, depois de US2.
- Polish: T042, T043 e T048.

## Implementation Strategy

**MVP: Phase 2 + US1** — o documento deixa de dizer Cefor quando não é Cefor, e é o defeito que se
torna permanente na primeira publicação de outra unidade. Depois **US2**, que fecha a garantia de
escopo e retira o catálogo; **US3**, que torna o modelo sustentável em 26 unidades; **US4**.

Um PR só: US1 sem US2 deixaria a publicação aceitar a autoridade de qualquer unidade, e US2 sem US3
deixaria as autoridades sem quem as cadastre fora do seed. Os checkpoints existem para a suíte, e não
para entregas separadas.
