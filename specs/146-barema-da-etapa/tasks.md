# Tasks: O barema da Etapa

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md)

Três incrementos, três PRs, nesta ordem: A → B → C. Cada um fecha com
`cd backend && make lint check test-pg` verde. Caminhos de código relativos a
`backend/processo_seletivo/`; de teste, a `backend/tests/`. `[P]` = pode correr em paralelo com a
anterior (arquivos distintos, sem dependência).

## Phase 1: Incremento A — o dado e o contrato

- [X] T001 [A] `CriterioAvaliacao` em `editais/models/etapas.py` e
  `editais/migrations/0027_criterios_de_avaliacao.py`, com os CHECKs do data-model;
  `migrations/test_migrations.py` passa a `editais: 27` (FR-5200, FR-5201)
- [X] T002 [A] `validate_stages` em `editais/domain/etapas.py`: nome obrigatório e único, máxima > 0,
  pontos por unidade ≤ máxima, unidade obrigatória com pontos, soma = máxima da Etapa, critério em
  decisória, documento do Edital e da inscrição, documento com restrição de Perfil, modalidade ou
  condição (pela leitura de aplicabilidade existente), soma acima de 999,9999; a mesma conferência do
  documento na validação de publicação, com o caso da restrição acrescentada depois do vínculo; testes
  unitários de cada recusa (FR-5201, FR-5203, FR-5204, FR-5205, SC-1634) — depende de T001
- [X] T003 [A] `replace_draft` cria os critérios depois das Etapas (molde dos critérios de desempate);
  `CriterionSerializer` em `editais/api/serializers.py` com `default=list`; ids de outro Edital
  recusados; teste da API com e sem a chave (FR-5213) — depende de T002
- [X] T004 [A] Degrau 21: `SCHEMA_VERSION = 21` e o parágrafo em `shared/canonical.py`; `criteria` em
  `publish_edital.py::_stages`; `DEGRAUS[21]` e `diz_o_mesmo_que_a_ausencia` em
  `publicacoes/domain/elevacao.py`; `CRITERIO_PUBLICADO` em `editais/domain/validation.py`; fixture
  `fixtures/snapshot.py`; `contract/test_elevacao_degrau_21.py` no molde do 20 (FR-5208) — depende de
  T003
- [X] T005 [A] [P] Contrato: os pares de `stages/criteria` em `editais/domain/mutabilidade.py`;
  `"/stages/*/criteria"` em `publicacoes/domain/colecoes.py`; nome e rótulos em
  `publicacoes/domain/alteracoes.py`; `VERSAO_DO_ESQUEMA = 21` e caminhos em
  `duvidas/domain/cobertura.py`; os guardiões `test_mutabilidade.py` (treze coleções,
  `conteudo_maximo` com critérios), `test_colecoes.py`, `test_cobertura.py` (FR-5210) — depende de T004
- [X] T006 [A] [P] Reaproveitamento: ids novos e `documento` remapeado em
  `editais/domain/reaproveitamento.py`; caso em `integration/editais/test_reaproveitamento.py`
  (FR-5212, SC-1625) — depende de T003

## Phase 2: Incremento A — User Story 1, configurar e publicar (P1)

- [X] T007 [US1] Seção Barema em `interface/templates/interface/_etapa.html`, linha em
  `_criterio_de_avaliacao.html`, `fragmento_criterio_de_avaliacao` em `interface/views.py` e a rota;
  a máxima vira leitura com critérios; regras na folha de `compor-etapas` (FR-5206, UX-420)
- [X] T008 [US1] Travessia: `ler_etapas` (prefixo `criterio-etapa-<i>-<n>-`), `etapas_do_edital`,
  `etapas_persistidas` em `interface/forms.py`; `interface/aplicacao.py` (FR-5206) — depende de T007
- [X] T009 [US1] Testes da travessia em `interface/test_barema_na_elaboracao.py`: gravar e recarregar;
  gravar Perfis, Cronograma e Inscrição depois e conferir que o barema ficou; recusa que reexibe o
  digitado; troca para decisória (FR-5204, FR-5206, FR-5213) — depende de T008
- [X] T010 [US1] `interface/static/interface/barema.js`: prévia, soma e máxima derivada ao vivo,
  acrescentar/remover/mover pelo `ordenacao.js`; `javascript/barema.test.js` (FR-5203, FR-5207,
  UX-421) — depende de T007
- [X] T011 [US1] [P] Conferência: `criteria` em `_LIDOS_POR_COLECAO["stages"]` e o bloco em
  `interface/revisao.py`; `unit/interface/test_revisao.py` (FR-5211)
- [X] T012 [US1] [P] Retificação: `CAMPOS_CRITERIO_DE_AVALIACAO` em `interface/retificacao.py`;
  `contract/test_retificacoes_api.py` e `interface/test_campos_vem_do_contrato.py`; caso que
  acrescenta critério e altera máxima, e outro que quebra a soma e é recusado (FR-5210) — depende de
  T005
- [X] T013 [US1] PDF: `_tabela_do_barema` em `publicacoes/infrastructure/pdf.py`, chamada por `_etapas`
  e pela redação em prosa, e em `apresentacao.py`; `interface/test_barema_no_pdf.py` com o texto
  extraído do 14/2026 e a igualdade do texto de um Edital sem barema antes e depois (FR-5209, SC-1620,
  SC-1624) — depende de T004
- [X] T014 [US1] Guardiões de tela: varredura de vocabulário (lista literal) e acessibilidade para as
  classes novas (FR-5206)
- [X] T015 [A] Checkpoint: `make lint check test-pg`; o quickstart §1 à mão; PR do incremento A

## Phase 3: Incremento B — User Story 2, pontuar na Mesa (P1)

- [ ] T016 [US2] `avaliacoes/domain/barema.py` (`calcular`, `barema_da_versao`, `reconciliar`) e
  `unit/avaliacoes/test_barema.py`: cenários 1 e 2, limite, quantidade além do teto, pontos acima da
  máxima, quatro casas, pendentes nomeados, critério desconhecido ou repetido, ordem indiferente, zero
  sem justificativa aceito, reconciliação com critério mantido, removido e novo (FR-5202, FR-5215,
  FR-5216, FR-5217, FR-5218, FR-5222, SC-1620, SC-1621, SC-1626, SC-1627, SC-1629)
- [ ] T017 [US2] `criterios` em `Avaliacao` e `ConclusaoAvaliacao`;
  `avaliacoes/migrations/0005_detalhamento_por_criterio.py` recriando a função do gatilho com a coluna;
  teste de SQL direto recusado em `integration/avaliacoes/test_imutabilidade_da_concluida.py` (FR-5219,
  SC-1630) — depende de T016
- [ ] T018 [US2] `gravar`, `concluir` e `reabrir` em `avaliacoes/application/avaliacao.py`: total do
  servidor, `pontuacao` do cliente recusada com barema, `criterios` recusado sem barema, cópia para a
  Conclusão, trilha sem nota; reabrir e concluir de novo depois de uma Retificação do barema; testes
  de serviço (FR-5215, FR-5217, FR-5218, FR-5219, FR-5222, FR-5229, FR-5230) — depende de T017
- [ ] T019 [US2] `mesa.py::inscricao_para_avaliar` entrega, no rascunho, o barema vigente com o
  detalhamento reconciliado e, na concluída, o barema de `avaliacao.versao`, com o documento ligado
  resolvido; `forms.ler_avaliacao` lê as linhas; autorização inalterada (FR-5214, FR-5222, FR-5229,
  FR-5233) — depende de T018
- [ ] T020 [US2] `_ficha_do_barema.html` em `mesa_inscricao.html`; a leitura da ficha na concluída e em
  `conclusoes.html`, cada conclusão com o barema da versão dela; regras na folha da Mesa;
  `interface/test_mesa_com_barema.py`, com o caso da Retificação que renomeia critério entre duas
  conclusões preservadas (FR-5214, FR-5223, FR-5233, UX-422, SC-1633) — depende de T019
- [ ] T021 [US2] [P] `interface/static/interface/mesa_barema.js` e `javascript/mesa_barema.test.js`:
  total ao vivo, "limitada ao máximo", pendentes em texto (UX-422) — depende de T020
- [ ] T022 [US2] [P] Barema inteiro, menos a ordem, em
  `resultados/domain/compatibilidade.py::CAMPOS_COMPARADOS`; testes: versão mudada recusa concluir;
  conclusão antiga não consolida depois de mudar a máxima, e também depois de mudar só a descrição ou o
  documento; reordenar consolida (FR-5221, SC-1628) — depende de T018
- [ ] T023 [US2] Integração de ponta a ponta sem tocar a jusante: concluir pela ficha, consolidar,
  emitir a ordem e publicar o preliminar; `integration/test_barema_ate_a_classificacao.py` (FR-5220,
  SC-1620) — depende de T022
- [ ] T024 [US2] [P] Regressão: Mesa de Etapa sem barema com o campo único; Edital de sorteio publicado
  com conteúdo idêntico salvo `criteria: []` (FR-5200, FR-5231, SC-1624)

## Phase 4: Incremento B — User Story 3, o candidato (P2)

- [ ] T025 [US3] "Comprova: …" em `portal/templates/portal/_documentos.html`, lido do barema
  publicado; teste do portal (FR-5224)
- [ ] T026 [US3] Detalhamento em `resultados_visiveis` e em `acompanhamento.html`, lido com o barema de
  `resultado.versao`, com as justificativas escritas; titular vê, outro candidato e Resultado não
  divulgado não veem; Retificação posterior que renomeia critério não muda o que o titular lê (FR-5218,
  FR-5225, FR-5233, UX-423, SC-1631, SC-1633) — depende de T023
- [ ] T027 [US3] Cenário 5: Edital com três Perfis e uma Etapa com barema, inscrições dos três
  pontuadas pela mesma ficha (SC-1625) — depende de T023
- [ ] T028 [US2] [US3] Jornada no navegador `navegador/test_jornada_do_barema.py`: configurar,
  publicar, inscrever com documento, pontuar, consolidar, ver no portal — depende de T026
- [ ] T036 [US4] Recusa temporária em `recursos/application/julgar.py`: correção fixada contra Resultado
  de Etapa com barema responde 409 com a frase que orienta a reavaliação determinada; teste de que
  nenhum Resultado de Etapa com barema nasce sem detalhamento e de que a reavaliação continua (FR-5232,
  SC-1635) — depende de T018. Fica nesta fase, e não na 5, porque é ela que torna o B seguro sozinho
- [ ] T029 [B] Checkpoint: `make lint check test-pg` e `make test-navegador`; quickstart §2–§3; PR do
  incremento B. **B não sobe para produção antes do C** (D-009); T036 é a rede se subir

## Phase 5: Incremento C — User Story 4, recurso (P2)

- [ ] T030 [US4] `criterios` em `DecisaoRecurso` e `recursos/migrations/0003_detalhamento_da_correcao.py`
  (FR-5227)
- [ ] T031 [US4] `recursos/domain/consequencia.py::derivar` com barema chama `barema.calcular` contra o
  barema de `decisao.versao`; vedação de piora sobre o total; remove a recusa de T036 e inverte o teste
  dela; testes do julgamento (FR-5227, FR-5232, SC-1622) — depende de T030
- [ ] T032 [US4] Tela de julgamento: detalhamento do Resultado atacado, com o barema da versão dele, e a
  ficha pré-preenchida na correção fixada, com o barema vigente (FR-5226, FR-5233) — depende de T031
- [ ] T033 [US4] Portal: detalhamento da decisão, critérios alterados marcados; ordem desatualizada e
  reemitida com o total novo (FR-5228, SC-1622) — depende de T031
- [ ] T034 [US4] [P] Reavaliação determinada cumprida pela ficha e consolidada como sucessora (FR-5222,
  SC-1623) — depende de T031
- [ ] T035 [C] Checkpoint: `make lint check test-pg`; quickstart §4; conferir no diff que nenhuma rota de
  área nova, permissão, tabela append-only ou módulo em `classificacao/` foi criado (SC-1632); README e
  Visão do Sistema; PR do incremento C
