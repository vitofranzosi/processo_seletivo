# Tasks: Acompanhamento pela situação do candidato

**Input**: Design documents from `specs/063-acompanhamento-pela-situacao/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/bloco-de-situacao.md, quickstart.md

**Tests**: pedidos pela Constituição (V). A matriz de estados tem caso em
`backend/tests/unit/portal/test_situacao_da_inscricao.py` (**TU**, sem banco), e os cenários de
aceitação e as invariantes do [contrato](contracts/bloco-de-situacao.md) §3 em
`backend/tests/portal/test_acompanhamento_pela_situacao.py` (**TA**, com banco).

P = `backend/processo_seletivo/portal/`; T = `backend/tests/`.

## Phase 1: Setup

- [X] T001 Conferir o ambiente da worktree: `backend/.env` presente, `uv sync --extra dev`, `DB_NAME=ps_063` nas rodadas; rodar T`portal/test_acompanhamento_resultado.py`, T`interface/test_portal_caminho_da_convocacao.py`, T`integration/portal/test_acompanhamento.py` e T`integration/requerimentos/test_orcamento_de_consulta.py` verdes **antes** de mudar qualquer coisa, para separar regressão de adaptação (D-012); listar, com `grep`, todo teste que lê as frases que mudam ("Resultado divulgado", "Você não foi classificado", "Situação registrada", "não decide nada sozinho", "quando uma vaga vagar")

## Phase 2: Foundational — a situação e os cartões

**⚠️ Nenhum template muda antes desta fase terminar.**

- [X] T002 Em `backend/processo_seletivo/divulgacao/application/selectors.py`, `situacoes_do_candidato` devolve também `lista` (`nome_da_lista(cabecalho)`) e `lista_id` (`publicacao.lista_id`), com comentário do porquê (D-006)
- [X] T003 Criar P`situacao.py` com: os rótulos do conjunto fechado (data-model §1.1) e a tabela de desfechos da FR-1172; as frases neutras da FR-1177, as de canal (reusando `FORMA_DE_CONVOCACAO_POR_EXTENSO`) e as de cadastro reserva (D-004, D-005); a ordenação dos cartões (`marco_codigo`, depois `_chave_da_lista` de P`leitura.py`) (D-006); e `situacao_da_inscricao(*, inscricao, perfil, cartoes, resultados_das_etapas, convocacao, desfecho, estado, enviada_em, requerimento, recorriveis, recursos, agora)` devolvendo `Situacao` (dataclasses `Situacao`, `Linha`, `Acao`) com a precedência de D-002; sem consulta ao banco e sem ler relógio; docstrings que digam por que corte e apuração **não** são entradas (FR-1169, FR-1171)
- [X] T004 Testes TU, com objetos em memória (`SimpleNamespace`): um caso por degrau da precedência e um por par de degraus vizinhos (o de cima vence); `provisoria` em cada estado; a função não aceita argumento de corte nem de apuração (assinatura); nenhum rótulo é "Classificado"/"Aprovado"; classificada numa lista e sem posição noutra → "Aguardando chamada", com as duas listas no porquê; recurso em análise → a situação não muda, e o porquê ganha a linha do recurso com o protocolo; a consequência do convocado em cada estado de prazo (com envio e vencimento em curso, sem envio, com falha, decorrido, sem vencimento)

**Checkpoint**: a situação existe e está provada sem banco; a página ainda é a antiga.

## Phase 3: User Story 1 — A pessoa em duas listas (P1) 🎯 MVP

**Goal**: FR-1166, FR-1167, FR-1173, FR-1174, FR-1181, FR-1183, UX-155, UX-157. **Independent Test**: inscrição classificada na ampla (8º) e numa reserva (2º), definitivas, sem convocação.

- [X] T005 [US1] Em P`views.py`, na view `acompanhamento`: localizar o Perfil da inscrição em `versao.content["profiles"]`, ordenar os cartões e chamar `situacao.situacao_da_inscricao` com o que a view já lê; passar `situacao` e `cartoes` ao contexto, mantendo as chaves que os outros blocos usam (D-001, D-007)
- [X] T006 [US1] Em P`templates/portal/acompanhamento.html`, conforme o contrato §1: `section.situacao` logo depois do subtítulo (h2 "Sua situação", rótulo, h3 "Por quê", h3 "O que fazer"); depois o aviso de retificação, a convocação, "Classificação por lista" com um `section.cartao-de-lista` por cartão (h3 "{lista} — {marco}", natureza e data, posição oficial ou "Sem posição nesta lista" com o motivo, prazo recursal, "Ver o resultado completo"), e os blocos de etapas, recursos, participação e cronograma na ordem da FR-1183; reescrever os comentários de template que descreviam o bloco por marco (D-009, FR-1182)
- [X] T007 [US1] Na folha do portal (P`templates/portal/base.html` ou o CSS em P`static/portal/`, onde as regras de `.resultado-divulgado` moram hoje), as regras de `.situacao`, `.rotulo-da-situacao` e `.cartao-de-lista`, substituindo as de `.resultado-divulgado` que perderem uso; nenhuma classe no template sem regra (memória "classe no template exige regra na folha"); `@media` em linhas separadas (memória do `}}`)
- [X] T008 [US1] Testes TA: duas listas → topo "Aguardando chamada", porquê com "Ampla concorrência" e o nome da reserva, cada um com a posição oficial, e a frase de mais de uma lista; dois cartões de `h3` distinto; o bloco de situação antes de qualquer cartão e de "Resultado das etapas"; hierarquia h1 → h2 → h3 sem salto (US1 cenários 1–2, SC-450, SC-451)
- [X] T009 [US1] Adaptar T`portal/test_acompanhamento_resultado.py` à marcação nova sem afrouxar: "Classificação final" continua presente por cartão; "uma linha por marco" vira "um cartão por lista e marco"; a ordem normativa dos marcos continua provada; o caminho continua sendo a vigente (D-012)

**Checkpoint**: o defeito que motivou a feature está corrigido e provado.

## Phase 4: User Story 2 — Classificação sem ocupação definida (P1)

**Goal**: FR-1169, FR-1170, FR-1177 (aguardando), FR-1178, FR-1179. **Independent Test**: classificada sem convocação, com e sem forma de convocação declarada, preliminar e definitiva.

- [X] T010 [US2] Testes TA: só preliminar → "Aguardando resultado definitivo" e "pode mudar", com o prazo de recurso quando aberto; Perfil `callForm=PUBLICATION` → a frase de publicação e nenhuma de e-mail/mensagem; sem `callForm` → só a frase neutra; definitiva sem convocação mas com apuração de ocupação emitida → continua "Aguardando chamada" (a apuração não é lida) (US2 cenários 1–3)

## Phase 5: User Story 3 — Cadastro reserva sem pertença (P2)

**Goal**: FR-1180. **Independent Test**: Perfil com `reserveType` `LIMITED`, `UNLIMITED` e `NONE`.

- [X] T011 [P] [US3] Testes TU das três frases de cadastro reserva e do Perfil ausente do vigente (nenhuma frase); teste TA com `LIMITED` de limite N: a frase do Edital aparece, e "você está no cadastro reserva" não (US3 cenários 1–2)

## Phase 6: User Story 4 — Convocação aberta (P1)

**Goal**: FR-1175, FR-1176, FR-1177 (convocado), FR-1183, D-008. **Independent Test**: convocada com Requerimento disponível e vencimento futuro.

- [X] T012 [US4] Em P`templates/portal/_convocacao_da_inscricao.html`, deixar só os dados (espécie, comunicação enviada em, prazo) e "Ver convocação"; as frases de estado e o chamado ao requerimento passam a sair do topo (D-008); atualizar o comentário
- [X] T013 [US4] Testes TA com `tests/fixtures/convocacao.py`: Requerimento disponível → "Convocado", "Preencher o Requerimento de Matrícula", prazo com data e hora, "a comissão poderá registrar o não atendimento desta convocação"; comunicação não enviada **e** comunicação com falha → "o prazo ainda não começou" e nenhuma frase de consequência; vencimento decorrido sem desfecho → situação "Convocado", a data em que o prazo terminou, "ainda não foi registrado", nenhuma frase de consequência; convocação sem vencimento → nenhuma frase de consequência; em nenhum cenário "perderá"; Requerimento enviado → "conferir", sem "deferido"/"homologado"/"matrícula efetivada"; Edital sem Requerimento → "Siga as instruções do Edital para esta convocação" e sem "matrícula"/"contratação" no topo; o porquê nomeia a lista da convocação e o número da chamada (US4 cenários 1–6)
- [X] T014 [US4] Adaptar T`interface/test_portal_caminho_da_convocacao.py` (e o que T001 tiver listado) às frases no topo, sem afrouxar: cada asserção que lia o parcial passa a ler o topo e continua provando o mesmo estado (D-012)

## Phase 7: User Story 5 — O desfecho registrado (P2)

**Goal**: FR-1172. **Independent Test**: convocação com cada desfecho.

- [X] T015 [P] [US5] Testes TU: os sete desfechos → os sete rótulos da tabela; desfecho sucedido → vale o vigente; nenhum rótulo "matriculado"/"contratado"
- [X] T016 [US5] Teste TA: desfecho *Aceite* registrado com `desfechar` → "Vaga aceita", fundamento e data no porquê, "Nada por enquanto" (US5 cenários 1–2)

## Phase 8: User Story 6 — Eliminada, sem posição, ou sem resultado (P2)

**Goal**: FR-1168 (degraus 3, 6, 7), FR-1182, FR-1185. **Independent Test**: três inscrições.

- [X] T017 [US6] Testes TA: Resultado de Etapa eliminada visível → "Eliminado", etapa e motivo no porquê, recurso quando aberto; sem posição em todas as listas → "Não classificado" e o cartão "Sem posição nesta lista" com motivo; inscrição recém-enviada → "Inscrição enviada", data do envio, "Nada por enquanto", e nenhum bloco de resultado (FR-056 preservada) (US6 cenários 1–3)

## Phase 9: Polish & cross-cutting

- [X] T018 Em P`templates/portal/convocacao.html`, trocar "quem está na lista pode ser chamado quando uma vaga vagar" pela constante neutra de P`situacao.py` passada pelo contexto da view `convocacao` (FR-1184, D-011); teste TA da frase nova e da ausência da antiga
- [X] T019 [P] Acrescentar P`situacao.py` e P`templates/portal/acompanhamento.html` às listas literais de T`test_vocabulario_da_convocacao.py` e T`test_vocabulario_do_requerimento.py`; nesta segunda, uma tabela `PERMITIDOS` por arquivo, com o motivo, retira de P`situacao.py` só a cadeia exata "Indeferido na convocação" antes da varredura, e um teste prova que qualquer outra ocorrência de `deferid` no módulo ainda reprova (D-010, Clarifications). *Ao fazê-lo, corrigido nas duas varreduras o padrão de comentário de linha e de docstring, que apagava quase todo arquivo com comentário — achado A-2 da spec*
- [X] T020 Teste TA de vocabulário renderizado: para cada cenário da matriz, o HTML do acompanhamento não contém as palavras da UX-158 (SC-452); no cenário do desfecho Indeferimento, só a cadeia exata "Indeferido na convocação" é retirada antes de procurar `deferid`, que continua proibido no resto do HTML; teste de que as únicas frases de consequência do HTML são as constantes de P`situacao.py` e de que nenhuma diz "perderá" (SC-453); e o texto do `section.situacao` renderizado, em todos os cenários, não contém "marco", "faixa", "apuração" nem "homologação" (UX-156)
- [X] T021 Teste TA de custo: a derivação (`ordenar_cartoes`, `situacao_da_inscricao`) roda com zero consultas, com seis cartões em dois marcos (SC-454, D-007); conferir que T`integration/requerimentos/test_orcamento_de_consulta.py` continua verde. *A primeira versão comparava a página inteira e mediu 23 × 38 consultas, custo anterior à feature — achado A-1 da spec*
- [X] T022 Linha da `063` no `README.md` (tabela de specs, depois da `062`) — o guardião `test_readme_acompanha_o_codigo.py` cobra
- [ ] T023 `cd backend && make lint check test-pg DB_NAME=ps_063`; atualizar no `AGENTS.md` o número de passando e conferir que os pulados continuam os onze
- [ ] T024 Demonstração (quickstart §3, SC-455, SC-456) em `ps_063_demo`: os cinco casos pelo portal a 1280 × 900 e a 375 px, com o *Aceite* de Ana Silva registrado pela gestão; registrar o que se mediu em `specs/063-acompanhamento-pela-situacao/verificacao.md`, com capturas
- [X] T025 Matriz de rastreabilidade `specs/063-acompanhamento-pela-situacao/rastreabilidade.md`: cada FR-, SC- e UX- desta spec com a tarefa e o teste que o prova

## Dependencies & Execution Order

- Phase 1 → Phase 2 → Phase 3 (US1). US1 entrega o template e a view, de que todas as outras dependem.
- Depois de US1: US2, US3, US5 e US6 são independentes entre si (só testes, sobre a mesma função);
  US4 mexe no parcial da convocação e em testes da `059`.
- Polish depois de todas; T023 depois de T018–T022; T024 e T025 por último.

## Parallel Opportunities

- T011 e T015 (unidade, arquivo TU) podem andar juntas depois de T003.
- T019 é independente de qualquer template.

## Implementation Strategy

MVP = Phases 1–3: a pessoa em duas listas lê a situação e cartões distintos. Cada fase seguinte
acrescenta um estado provado, sem mudar o que a anterior provou.
