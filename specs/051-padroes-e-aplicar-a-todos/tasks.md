# Tasks: Padrões do Edital e "aplicar a todos"

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/)

**Tests**: pedidos. Cada requisito tem teste que falha sem o código (é o que a
[rastreabilidade](rastreabilidade.md) prende). Caminhos relativos a `backend/`.

**Entrega**: o #226 levou as Fases 1 a 7 (P1). A Fase 8 (US5, P2) é do segundo PR (R-009).

## Phase 1: Setup

- [X] T001 Conferir o ambiente: `.env` com `DB_NAME=ps_051`, `uv sync --extra dev`, `make check`

## Phase 2: Foundational

- [X] T002 Coluna `detalhe` (JSONField nula) em `processo_seletivo/auditoria/models.py`, migration `processo_seletivo/auditoria/migrations/0003_registroauditoria_detalhe.py`, parâmetro `detalhe=None` em `record_event` (`processo_seletivo/auditoria/application.py`); subir a contagem de `auditoria` com a justificativa em `tests/migrations/test_migrations.py`
- [X] T003 [P] `CORTE_PADRAO` e `corte_padrao()` em `processo_seletivo/editais/domain/marcos.py`
- [X] T004 Medir quantos testes publicam Perfil com corte e sem `callForm` (grep em `tests/` e rodar `validate_for_publication` sobre as fixtures) antes de escrever a `FR-943`

## Phase 3: User Story 1 — o marco aplicado aos demais (P1) 🎯 MVP

**Goal**: aplicar o marco de um Perfil aos demais, com prévia e exclusão, na etapa Classificação.

**Independent Test**: 7 Perfis sem marco; compor o do primeiro; prévia com 6 *nasce*; confirmar; 7 marcos independentes com código derivado e critérios nos fatos do próprio Perfil.

- [X] T005 [P] [US1] Testes unitários da regra única para o marco (FR-910–914, FR-917, FR-922, FR-923) em `tests/unit/editais/test_aplicacao.py`: nasce (código/denominação derivados; critério remapeado por código e tipo), substitui (campos; id/code/name mantidos; lista de critérios inteira), sem mudança, fora (dois marcos; fato ausente; fato de outro tipo; método próprio na origem ou no destino), quantidade fixa destacada, ausência aplicada como ausência, impressão estável
- [X] T006 [US1] `processo_seletivo/editais/domain/aplicacao.py`: `Efeito`, `unidade_do_marco`, `impressao`, `efeitos_do_marco(perfis, *, origem, sub)`, `aplicar(perfis, efeitos, incluidos)`, `assinatura(efeitos)`
- [X] T007 [US1] (FR-920, FR-921) `processo_seletivo/editais/application/aplicacao.py::gravar_aplicacao`: `replace_draft` + `record_event(operation="APLICAR_A_TODOS", reason, detalhe)` numa transação
- [X] T008 [US1] (UX-112) `processo_seletivo/interface/aplicacao.py`: a prévia em palavras (mudanças com os rótulos da Revisão, frase do alcance), leitura de `aplicar`/`confirmar_aplicacao`/`aplicar_destino`/`aplicar_impressao`
- [X] T009 [US1] (FR-916, FR-918–FR-920, SC-343) `compor_etapa` em `processo_seletivo/interface/views.py`: prévia, cancelar, confirmar (impressão, nenhum destino, recusa do domínio), redirecionamento com `aplicado`
- [X] T010 [US1] (UX-110, UX-111, UX-113) `processo_seletivo/interface/templates/interface/_previa_da_aplicacao.html` (novo), botão no `_marco.html`, inclusão em `compor_classificacao.html`, confirmação de `aplicado` em `compor_base.html` (ou onde o `salvo` aparece)
- [X] T011 [US1] (SC-341, SC-342, SC-343) Testes de interface em `tests/interface/test_aplicar_a_todos.py`: a prévia não grava; confirmar grava e registra na trilha; excluído intocado; divergência recusa sem gravar; Edital de um Perfil não oferece o botão; sem permissão, recusa

## Phase 4: User Story 2 — o que o Edital declara uma vez (P1)

**Goal**: Modalidade pelo código (com a ampla), forma de convocação e reversão no controle do Edital.

**Independent Test**: 7 Perfis sem PcD; aplicar a PcD do primeiro; 6 *nasce* com as Modalidades de cada destino listadas; quadro intocado.

- [X] T012 [P] [US2] (FR-924, FR-925, FR-926) Testes unitários em `tests/unit/editais/test_aplicacao.py`: Modalidade nasce/substitui/sem mudança; nunca remove; linha do quadro intocada; ampla substituída e desmarcada; forma de convocação; reversão fora sem lista reservada
- [X] T013 [US2] `efeitos_da_modalidade`, `efeitos_do_campo_do_perfil` em `processo_seletivo/editais/domain/aplicacao.py`
- [X] T014 [US2] Etapa Perfis em `views.py`/`interface/aplicacao.py`: o gesto sobre `ler_perfis`, gravando pelo caminho da etapa Perfis
- [X] T015 [US2] Controle do Edital em `compor_perfis.html` (forma de convocação, reversão, botão), botão no `_modalidade.html`; o Perfil novo nasce com a forma e a reversão comuns (`fragmento_perfil`)
- [X] T016 [US2] Testes de interface em `tests/interface/test_aplicar_a_todos.py`: Modalidade e controle do Edital, ponta a ponta

## Phase 5: User Story 3 — padrões (P1)

**Goal**: corte padrão, empate fora do sorteio, instante do Evento, prosa gerada, Etapa decisória eliminatória, quadro sugerido com o arredondamento da regra, `FR-943`.

**Independent Test**: marco de sorteio único publica sem empate, sem instante e sem prosa digitados, com o corte do padrão.

- [X] T017 [P] [US3] (FR-915, FR-927) `_marco_novo` com o corte padrão quando o Perfil não tem marco na tela; o fragmento inclui os cartões do Perfil (`_marco.html`/`compor_classificacao.html` `hx-include`)
- [X] T018 [P] [US3] (FR-928) Empate: `_marco.html` não desenha o campo sob sorteio (mantém oculto o valor declarado); `_regra_de_corte_do_marco` em `validation.py` não o exige sob sorteio
- [X] T019 [P] [US3] (FR-929, FR-930) `processo_seletivo/sorteios/domain/prosa.py` (frase por regra); `forms._metodo_de_sorteio` preenche o texto vazio; lista de Eventos no método comum e no do marco, com o instante como valor
- [X] T020 [P] [US3] (FR-931) `_etapa.html` e `forms.ler_etapas`: *"Eliminatória"* no bloco da decisória, marcado na Etapa nova
- [X] T021 [P] [US3] (FR-932, FR-933) `processo_seletivo/editais/domain/quadro.py::sugestao`; `rounding` na Modalidade (`_modalidade.html`, `forms._modalidades`, `_modalidade_para_o_formulario`); `placeholder` e descrição na linha do quadro; gesto *Preencher pelo percentual*; preservação dos opacos da regra na gravação da etapa Perfis (R-007); comentário de `OPACOS`
- [X] T022 [US3] `FR-943` em `validation.py` (`profile_cuts_without_call_form`), com a âncora da pendência na etapa Perfis; ajustar as fixtures medidas em T004
- [X] T023 [US3] (SC-344, SC-345) Testes em `tests/interface/test_padroes_da_composicao.py` e `tests/unit/editais/test_quadro_sugerido.py`; um teste de que nenhum padrão alcança conteúdo publicado (`SC-344`)

## Phase 6: User Story 4 — a Revisão (P1)

**Goal**: origem de cada valor e o bloco dos campos definitivos.

**Independent Test**: marco aplicado a 6 Perfis e padrões; a Revisão diz a origem; editar um marco à mão tira a atribuição; o bloco lista os campos não retificáveis e estruturais.

- [X] T024 [US4] (FR-934, FR-935, UX-114) `revisao.blocos(snapshot, contexto=None)`: origens por comparação e pelo registro do gesto; a view passa Eventos e linhas `APLICAR_A_TODOS`
- [X] T025 [US4] (FR-936, FR-937, UX-115) Bloco *"O que não se corrige depois de publicado"*, derivado do `CONTRATO`, em `revisao.py` e `compor_revisao.html` antes do botão de submeter
- [X] T026 [US4] Guardiões de `LIDOS`/`NAO_MOSTRADOS` (o `rounding` da regra passa a ser lido); testes em `tests/interface/test_revisao_origem_e_definitivos.py`, inclusive o guardião de completude do bloco contra o contrato (`SC-346`)

## Phase 7: Polish

- [X] T027 `rastreabilidade.md` requisito a requisito, com FR-938–FR-942 e SC-347 marcados *PR seguinte*; README (tabela de specs); `make lint check test-pg DB_NAME=ps_051`
- [X] T028 (SC-340) Percurso no preview com a estrutura do 28/2026 e a contagem de interações antes e depois (`quickstart.md`)

## Phase 8: User Story 5 — Retificação (P2) — segundo PR

**Goal**: o gesto na Retificação, campo a campo, num ato só, com a conferência agrupada e as
consequências; o destino que alcança campo não retificável fica inteiro fora.

**Independent Test**: Edital publicado de 7 Perfis; retificar a janela do primeiro de 2 para 3 dias,
*Aplicar a janela recursal aos demais Perfis (6)*; a conferência mostra 6 *mudam* e os marcos com
resultado divulgado; *Criar Retificação*; 7 Alterações num ato só.

- [ ] T029 [P] [US5] (FR-938, FR-939, FR-940, SC-342) Testes unitários da regra na Retificação em `tests/unit/publicacoes/test_aplicacao_na_retificacao.py`, unidade a unidade (R-012): nasce, substitui, sem mudança e fora; o campo não retificável diferente deixa o destino **inteiro** fora e nomeia o campo; a janela que nasce só concedendo; o corte que nasceria sobre Etapa com Resultado; a regra normativa que não nasce; a ausência na origem recusada (R-013); o destino já alterado no ato fica fora (R-014); critérios por remoção e acréscimo, com o fato pelo código e pelo tipo; identidades derivadas e impressão estável
- [ ] T030 [US5] `processo_seletivo/publicacoes/domain/aplicacao.py`: `efeitos(conteudo, unidade=, perfil=, alvo=, …)` devolvendo, por destino, o efeito e as Alterações; natureza de cada campo lida de `mutabilidade.CONTRATO`; a leitura da `FR-802` no docstring (FR-942, R-017)
- [ ] T031 [US5] `processo_seletivo/interface/aplicacao_na_retificacao.py`: os gestos declarados no formulário, os botões por cartão (UX-110), o bloco da conferência em palavras (FR-916, FR-918, UX-111 a UX-113), as consequências do ato (FR-941, R-015)
- [ ] T032 [US5] `views.retificar`, `retificar.html`, `_retificacao_linha.html` e `_gesto_na_retificacao.html` (novo): declarar, desfazer, conferir e confirmar com a impressão (FR-919); criar **um** ato com as Alterações digitadas e as dos gestos, e registrar cada gesto na mesma transação (FR-921, FR-941, R-016) em `processo_seletivo/editais/application/aplicacao.py`
- [ ] T033 [US5] (SC-343, SC-347) Testes de integração em `tests/interface/test_aplicar_a_todos_na_retificacao.py`: a janela em N Perfis vira N+1 Alterações num ato; o critério trocado vira remoção e acréscimo por destino (FR-792); o destino com campo não retificável diferente fica fora e nada dele entra no ato; as guardas da `048`; o destino desmarcado fica intocado; a divergência entre conferência e confirmação é recusada sem criar; as consequências nomeadas; o registro na trilha; publicar dá uma versão e um documento
- [ ] T034 [US5] (SC-347) Percurso no preview — Edital publicado de vários Perfis, prazo recursal e forma de convocação num ato só, e um destino fora por campo não retificável — com a contagem de interações antes (`main`) e depois; `rastreabilidade.md` com FR-938 a FR-942 e SC-347; `make lint check test-pg DB_NAME=ps_051p2`

## Dependencies & Execution Order

- Fase 2 antes de tudo; T004 antes de T022.
- US1 (Fase 3) antes de US2 (Fase 4): US2 reusa `Efeito`, a prévia e a gravação.
- US3 é independente de US1/US2, salvo T021 (etapa Perfis, junto de T014–T015 no mesmo template).
- US4 depende de US1–US3 (lê o registro e os padrões).
- US5 depende de US1–US2: reusa `Efeito`, a correspondência pelo código, o fato pelo código e pelo tipo, a impressão e a assinatura.
- Na US5, T029 antes de T030; T030 antes de T031; T031 antes de T032; T033 e T034 por último.

## Parallel Opportunities

- T003 ‖ T002; T005 ‖ T012 (mesmo arquivo de teste, seções separadas — em sequência, na prática).
- Na US3, T017–T021 tocam arquivos diferentes e podem andar juntos.

## Implementation Strategy

MVP = US1: sozinha, derruba a Classificação do 140/2025 de ~400 para ~30. Depois US3 (vale para o
Edital pequeno), US2, e a US4 fecha a P1, porque a Constituição 1.2.0 não deixa a P1 sair sem a origem na
Revisão.
