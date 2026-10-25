# Tasks: Relatório do Edital

**Input**: Design documents from `specs/099-relatorio-do-edital/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/relatorio.md](contracts/relatorio.md)

**Tests**: pedidos pelo usuário em 24/10/2026 (dez cenários obrigatórios), e exigidos pela Constituição
(princípio V). Caminhos relativos a `backend/`.

## Phase 1: Setup

- [x] T001 Criar o pacote de testes `tests/integration/relatorio/__init__.py` e conferir `.specify/feature.json` apontando para `specs/099-relatorio-do-edital`

---

## Phase 2: Foundational

- [x] T002 Escrever a fixture do cenário coerente em `tests/fixtures/relatorio.py`: `montar_cenario(escala=1, final="pendente"|"sem-pendencia"|"aberto"|"cancelado")`, pelos commands da aplicação com o relógio na data de cada ato, a partir de `doc/estudo-relatorio-de-execucao-do-edital-2026-10-24/roteiro/cenario_coerente.py` (R-011)
- [x] T003 Escrever o esqueleto da derivação em `processo_seletivo/interface/relatorio_do_edital.py`: `Numero`, `Ausencia` (tipos da `040` + "não registrado pelo GPS" + "omitido por privacidade"), `Relatorio`, `LinhaDoPerfil`, `Pendencia`, `Data`, e `ler(edital, *, agora, enderecos)` dentro da transação `REPEATABLE READ` (R-002); as grafias de ausência (FR-2548) e o vigente no instante, sem reconstituir o passado (FR-2521)

**Checkpoint**: a fixture monta o Edital 61/2026 e `ler` devolve a identificação.

---

## Phase 3: User Story 1 — Entender a seleção sem conhecer o sistema (P1) 🎯 MVP

**Goal**: página e PDF com a camada executiva, números iguais aos das telas donas.

**Independent Test**: com a fixture, abrir `/gestao/editais/<id>/relatorio` e baixar o PDF; conferir indicadores, tabela por Perfil, visão geral e ausência de termos internos.

- [x] T004 [US1] Indicadores e tabela por Perfil em `processo_seletivo/interface/relatorio_do_edital.py`: vagas por lista, inscrições, razão (FR-2529), classificadas, habilitadas nas vagas, cadeia das convocações, rascunhos e cadastros distintos, com os nomes publicados e os rótulos importados de `portal/situacao.py` e `recursos/application/selectors.py` (FR-2528 a FR-2533, FR-2535, FR-2545, FR-2547)
- [x] T005 [US1] Procura diária, prorrogação e envios no período acrescentado em `processo_seletivo/interface/relatorio_do_edital.py` (FR-2536)
- [x] T006 [US1] Retificações com antes e depois, recursos por Perfil, datas principais e documentos com endereço público em `processo_seletivo/interface/relatorio_do_edital.py`; extrair `_alteracoes_legiveis` de `processo_seletivo/interface/views.py` para uso comum (FR-2537 a FR-2539)
- [x] T007 [US1] Privacidade por desenho em `processo_seletivo/interface/relatorio_do_edital.py`: fato não público só por Perfil, e omitido em Perfil com menos de 5 enviadas (FR-2549 a FR-2551, D-006)
- [x] T008 [US1] Visão geral por regras em `processo_seletivo/interface/relatorio_do_edital.py`, cada frase com condição e fonte (FR-2527)
- [x] T009 [US1] Composição do PDF em `processo_seletivo/interface/relatorio_pdf.py`: camada executiva e anexo (FR-2540 a FR-2544), rodapé com instante e natureza, marcadores e links (FR-2552, R-004)
- [x] T010 [US1] Views em `processo_seletivo/interface/relatorio.py` (página GET, emissão POST), rotas em `processo_seletivo/interface/urls.py`, ação em `processo_seletivo/interface/acoes.py` e no template do detalhe (FR-2513 a FR-2515, FR-2518)
- [x] T011 [US1] Template `processo_seletivo/interface/templates/interface/relatorio_do_edital.html` e folha `processo_seletivo/interface/static/interface/telas/relatorio.css` (FR-2553)
- [x] T012 [US1] Inventário da porta nova em `specs/033-navegacao-por-capacidade/inventario-das-negativas.md` e o módulo em `MODULOS_DE_VIEW` de `tests/test_gramatica_das_portas.py` (FR-2514)
- [x] T013 [P] [US1] Testes de unidade da derivação em `tests/unit/interface/test_relatorio_do_edital.py`: ausências, razão "não se aplica", frases com condição verdadeira e falsa
- [x] T014 [US1] Testes de integração dos números em `tests/integration/relatorio/test_numeros.py`: cada indicador igual ao da tela dona; múltiplos Perfis e listas; recursos, retificação e resultado substituído; Retificação não descrita automaticamente (SC-933)
- [x] T015 [US1] Testes de conteúdo e privacidade em `tests/integration/relatorio/test_conteudo.py`: sem nome, CPF, e-mail ou protocolo no texto do PDF; termos proibidos ausentes; fato não público por Perfil; Perfil pequeno omitido (SC-934, FR-2546)
- [x] T016 [US1] Testes da tela em `tests/interface/test_relatorio.py`: ação no detalhe, página, 404 fora do escopo, recusa explicada no escopo, Edital não publicado (FR-2513, FR-2514)

---

## Phase 4: User Story 2 — Saber se a seleção terminou (P1)

**Goal**: duas situações, espécie derivada, pendências e registros posteriores.

**Independent Test**: a fixture nos quatro finais (aberto, pendente, sem pendência, cancelado) produz a espécie esperada.

- [x] T017 [US2] Pendências, espécie e situações em `processo_seletivo/interface/relatorio_do_edital.py` (FR-2522 a FR-2525, R-006)
- [x] T018 [US2] Registros posteriores ao desfecho em `processo_seletivo/interface/relatorio_do_edital.py` (FR-2526, R-008), e os pontos de atenção (FR-2534)
- [x] T019 [US2] Testes em `tests/integration/relatorio/test_especie.py`: inscrições abertas, encerrado com pendência, encerrado sem pendência, cancelado, registros posteriores, marco sem resultado, convocação com prazo vencido (SC-935)

---

## Phase 5: User Story 3 — Conferir números, documentos e regras (P2)

**Goal**: anexo verificável, links e integridade.

**Independent Test**: os resumos do anexo coincidem com os dos documentos publicados; os links do PDF apontam para o portal.

- [x] T020 [US3] Testes em `tests/integration/relatorio/test_anexo.py`: resumos iguais aos de `DocumentoPublicado` e `DocumentoDoResultado`; anotações `/URI` com os endereços públicos; etapas por Perfil sem presença; frase de integridade (FR-2540 a FR-2544)

---

## Phase 6: User Story 4 — Emissão rastreável (P2)

**Goal**: cada PDF numerado e auditado; composição determinística; leitura num instante só.

**Independent Test**: duas emissões geram dois eventos com resumos dos bytes e números 1 e 2.

- [x] T021 [US4] Emissão em `processo_seletivo/interface/relatorio.py`: trava do Edital, número pela trilha, evento `EMITIR_RELATORIO` com o resumo, resposta 409 em falha de serialização e recusa de texto sem grafia (FR-2516, FR-2517, R-003)
- [x] T022 [US4] Testes em `tests/integration/relatorio/test_emissao.py`: evento com resumo dos bytes entregues, numeração, determinismo, `REPEATABLE READ` emitido no bloco de fora (FR-2516, FR-2517, FR-2519, FR-2520, SC-937)

---

## Phase 7: Polish & Cross-Cutting

- [x] T023 [P] Orçamento de consultas em `tests/performance/test_relatorio.py`: escala 1 e escala 10 com o mesmo número de consultas (SC-936)
- [x] T024 [P] Matriz `specs/099-relatorio-do-edital/rastreabilidade.md`: todo FR, SC e caso-limite com o teste que o prende
- [x] T025 Atualizar o roteiro `doc/estudo-relatorio-de-execucao-do-edital-2026-10-24/roteiro/cenario_coerente.py` com `FINAL`, e o README (linha da `099`)
- [x] T026 `make lint check test-pg` verde
- [x] T027 Cenário demonstrável pelo navegador e os dois PDFs de demonstração — acompanhamento e encerramento — em `doc/estudo-relatorio-de-execucao-do-edital-2026-10-24/` (SC-938)
- [ ] T028 SC-932: conversa com destinatários reais — **do usuário**

## Phase 8: Modernização da diagramação (24/10/2026)

- [x] T029 Peças comuns em `processo_seletivo/interface/diagramacao.py` (`abertura`, `BarrasVerticais`) e `relatorio_pdf.cartoes`; a `100` passa a usá-las (FR-2601)
- [x] T030 Regras de paginação compartilhadas: nota presa, cadeia de títulos, linha viúva, parágrafo curto; a `Ficha` mede o valor em negrito (FR-2604, FR-2607)
- [x] T031 `processo_seletivo/interface/relatorio_pdf.py` reescrito sobre os blocos, na organização da maquete v2: painel, resultados, procura × alterações, datas, documentos, anexo A–H (FR-2536, FR-2602, FR-2605, FR-2606)
- [x] T032 Endereço só em host público na emissão (`interface/relatorio.py`, `_Enderecos`) e nos roteiros de demonstração (FR-2603)
- [x] T033 [P] Testes: `tests/unit/interface/test_diagramacao_do_relatorio_do_edital.py` e `tests/integration/relatorio/test_diagramacao.py`; o texto dos testes de conteúdo passa a ser o extraído do PDF
- [x] T034 PDF emitido pelo sistema e comparação visual em `doc/estudo-relatorio-de-execucao-do-edital-2026-10-24/modernizacao/` (SC-947)
- [x] T035 Homologação: o cronograma registra a publicação dos resultados; uma consulta de publicações para a linha do tempo e o cronograma (FR-2542)
- [x] T036 Homologação: notas só com o caso que explicam; links conferidos na topologia de produção (FR-2603, FR-2608)

---

## Dependencies & Execution Order

- Phase 2 bloqueia tudo. US1 entrega a derivação e as saídas; US2 e US4 acrescentam à derivação e à
  view, e dependem da US1; US3 é só teste sobre o que a US1 compõe.
- T013 e T023 e T024 são paralelos ao resto da própria fase.

## Implementation Strategy

MVP = Phases 1–4 (US1 + US2): sem a espécie, o relatório repetiria o defeito que motivou a feature.
US3 e US4 completam a confiança e a rastreabilidade antes do PR.
