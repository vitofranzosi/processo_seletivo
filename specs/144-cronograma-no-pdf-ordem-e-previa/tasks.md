# Tasks: O Cronograma — visibilidade no PDF, ordenação e prévia

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md)

Três incrementos, três PRs, nesta ordem. Cada um fecha com `cd backend && make lint check test-pg`
verde. Caminhos de código relativos a `backend/processo_seletivo/`; de teste, a `backend/tests/`.

## Phase 1: Incremento A — a fundação do dado e do contrato

- [x] T001 [A] `shown_in_pdf` em `editais/models/cronograma.py` e a migration
  `editais/migrations/0026_visibilidade_do_evento_no_pdf.py`; `migrations/test_migrations.py` passa a
  `editais: 26` e ganha o caso "Evento gravado antes da migração fica exibido" (FR-5100, SC-1580)
- [x] T002 [A] Degrau 20: `SCHEMA_VERSION = 20` e o parágrafo em `shared/canonical.py`;
  `DEGRAUS_DE_EVENTO[20]` em `publicacoes/domain/elevacao.py`; `contract/test_elevacao_degrau_20.py`
  no molde do 11; os testes que fixam a versão (FR-5105, D-001)
- [x] T003 [A] `shownInPdf` em `publicacoes/application/publish_edital.py`, `Campo("shownInPdf",
  bool)` em `EVENTO_PUBLICADO` (`editais/domain/validation.py`) e na fixture `fixtures/snapshot.py`
  (FR-5105)
- [x] T004 [A] `("schedule", "shownInPdf"): retificavel()` em `editais/domain/mutabilidade.py`; a linha
  na matriz da `026` e no `openapi.yaml` da `001` (FR-5113, P-1)
- [x] T005 [A] `VERSAO_DO_ESQUEMA = 20` e a exclusão do caminho em `duvidas/domain/cobertura.py`
  (FR-5112)
- [x] T006 [A] Revisão: "Não sai no PDF" em `interface/revisao.py::_evento`, a frase da seção não
  impressa no bloco do Cronograma, e o campo em `_LIDOS_POR_COLECAO` (FR-5110, D-009)
- [x] T007 [A] Retificação: o campo em `CAMPOS_EVENTO`, o Evento acrescentado nasce exibido, o rótulo
  em `publicacoes/domain/alteracoes.py`; `interface/test_campos_vem_do_contrato.py` passa a 86; um
  caso que retifica a visibilidade e confere o consolidado (FR-5100, FR-5113; P-1, decidida "sim")

## Phase 2: Incremento A — User Story 1, ocultar sem desativar (P1)

- [x] T008 [US1] A travessia: `ler_eventos`, `eventos_do_edital` e `eventos_persistidos` em
  `interface/forms.py`; `replace_draft` em `editais/application/draft.py`; `shownInPdf` no
  `EventSerializer` de `editais/api/serializers.py`, com padrão verdadeiro (FR-5104)
- [x] T009 [US1] Testes da travessia em `interface/test_cronograma_visibilidade.py`: gravar e
  recarregar; gravar Perfis, Etapas e Inscrição depois de ocultar; recusa que reexibe o digitado; API
  sem a chave; restauração do rascunho local pelo servidor (FR-5102, FR-5104, SC-1584)
- [x] T010 [US1] O cartão: campo oculto, marca "Oculto do PDF" e classe em `_evento.html`; o parâmetro
  `com_visibilidade_no_pdf` e o botão em `_acoes_da_linha.html`; `_olho.html`; as regras em
  `telas/compor-cronograma.css` (FR-5101, UX-390, UX-391)
- [x] T011 [US1] `interface/static/interface/cronograma.js` com a alternância e o `change` despachado;
  o `<script>` em `compor_cronograma.html` (FR-5101, FR-5102, D-007)
- [x] T012 [US1] `eventos_no_documento` e `numero_no_documento` em
  `publicacoes/infrastructure/pdf.py`; `_cronograma` sobre eles; `frase_do_periodo_de_inscricoes` com
  o número impresso ou sem remissão. Sem oculto, o número é o `order`, com casos de `order` `0` e com
  lacunas (FR-5106, FR-5107, FR-5108, D-002, D-003)
- [x] T013 [US1] A presença da seção pela mesma função em `_materializaveis` e em
  `apresentacao._principal_presente`; testes em `unit/publicacoes/test_cronograma_no_documento.py`:
  todos ocultos nas duas apresentações, `tabelas_do_documento`, `numeracao`, o resumo sem "Datas"
  (FR-5109, D-004)
- [x] T014 [US1] O PDF de verdade em `interface/test_cronograma_no_pdf.py`, por
  `texto_de_pdf_bytes`, **parametrizado pelas duas apresentações** (a plana e a por perguntas):
  - um oculto — a prévia e a publicação sem a descrição dele na tabela; numeração 1..k; a frase da
    Etapa com a data do Evento oculto;
  - todos ocultos — sem o título da seção Cronograma; sem "Datas: no Cronograma" no resumo (por
    perguntas); "Tabela N" e os números das seções seguintes coerentes com o que saiu;
  - a remissão do período — "(Cronograma, nº k)" com o número impresso quando exibido e um oculto
    antes dele; a frase sem remissão, e com o período, quando ele está oculto;
  - compatibilidade — conteúdo sem oculto, com `order` começando em `0` e com lacunas, igual ao texto
    de antes da feature (SC-1580, SC-1581, SC-1582, SC-1587, SC-1588, FR-5114)
- [x] T015 [US1] Integridade e canais em `interface/test_cronograma_visibilidade.py`: o oculto na lista
  de Eventos da etapa Etapas, na pendência por vencido, na validação de datas e de vínculo, como
  período que abre as inscrições; e nos **seis** canais — a página pública da seleção, o assistente
  de dúvidas, a Agenda dos Editais, o Kit de Divulgação, o relatório do Edital e a leitura pela API —
  um caso por canal, cada um encontrando o Evento oculto (FR-5103, FR-5112, SC-1589)
- [x] T016 [US1] `javascript/cronograma.test.js`: a alternância muda campo, `aria-pressed`, `title`,
  classe e marca, e despacha `change`; o botão sai revelado só com o script; somente leitura sem botão
  (FR-5101, FR-5102, UX-390)
- [x] T017 [US1] Reaproveitamento em `integration/editais/test_reaproveitamento.py`: preserva o oculto
  e o vínculo; origem de versão 19 chega toda exibida (FR-5111, D-008, SC-1586)

**Checkpoint A**: PR do incremento A; a etapa já oculta e o PDF já filtra.

## Phase 3: Incremento B — User Story 2, ordenar por início (P2)

- [ ] T018 [US2] O botão e a região viva em `compor_cronograma.html`, na linha da contagem, só quando
  editável; a regra em `compor-cronograma.css` (FR-5120, UX-392)
- [ ] T019 [US2] `ordemPorInicio` e a montagem em `cronograma.js`: reanexar na ordem nova, contar os
  que mudaram, anunciar, manter o foco, desabilitar com menos de dois (FR-5121 a FR-5125, D-005)
- [ ] T020 [US2] `javascript/cronograma.test.js`: crescente; empate estável; vazio e incompleto ao fim
  sem campo alterado; já em ordem; um só; valor com segundos; os campos de `order` renumerados pelo
  `ordenacao.js`; nada reordena ao editar data (FR-5121 a FR-5126, SC-1583)
- [ ] T021 [US2] `interface/test_cronograma_visibilidade.py`: a sequência enviada depois de ordenar é
  gravada, e identidade, vínculo de Etapa, designação e visibilidade sobrevivem à gravação e à
  recarga (FR-5126, SC-1583, SC-1584)
- [ ] T029 [US2] Mover não é acrescentar: `assistente.js` passa a ignorar, no foco, o nó acrescentado
  que também saiu na mesma entrega do observador; caso no navegador, em
  `navegador/test_jornada_do_cronograma.py`, que lê o foco **depois** do observador (aguardando a
  microtarefa) — ordenar e cada seta deixam o foco no botão; acrescentar continua focando o primeiro
  campo da linha nova; remover continua devolvendo o foco (FR-5125, FR-5127, D-010)

**Checkpoint B**: PR do incremento B.

## Phase 4: Incremento C — User Story 3, a prévia (P2)

- [ ] T022 [US3] A seção da prévia em `compor_cronograma.html`, antes de `#eventos`, com `hidden`
  (FR-5130, FR-5135, FR-5136)
- [ ] T023 [US3] `resumo` e `desenhar` em `cronograma.js`; os gatilhos — `input`, `change`, mutação da
  lista, alternância e ordenação (FR-5130 a FR-5134)
- [ ] T024 [US3] A tabela compacta e o empilhamento a 375 px em `compor-cronograma.css` (UX-393,
  UX-394)
- [ ] T025 [US3] `javascript/cronograma.test.js`: os seis gestos; cabeçalho e concordância; vazio;
  todos ocultos; sem data de início; somente leitura; sem pedido ao servidor (FR-5130 a FR-5135,
  SC-1585, SC-1587)

## Phase 5: o fechamento do incremento C

Vão no mesmo PR do C: a jornada inteira só existe com as três capacidades juntas, e é ela que decide
o merge. A verificação final inclui o grupo `navegador` com o Chromium (`uv sync --extra dev --extra
navegador`, `uv run playwright install chromium`) — sem ele os casos de navegador pulam, e o foco e a
jornada ficariam sem prova.

- [ ] T026 `navegador/test_jornada_do_cronograma.py`: a jornada inteira da spec, a 1440 e a 375 px,
  sem violação de CSP, conferindo o texto da prévia do PDF (SC-1590)
- [ ] T027 O roteiro de [quickstart.md](quickstart.md) com capturas, e `verificacao.md` com o que foi
  medido
- [ ] T028 `make lint check test-pg` com o grupo `navegador`; a contagem de migrations e o "N de M" do
  CLAUDE.md, se mudarem; a Visão do Sistema no merge

**Checkpoint C**: PR do incremento C, com T026–T028.

## Dependencies

- T001 → T002 → T003 → (T004, T005, T006, T007) → T008 → T009.
- T010 → T011 → T016. T012 → T013 → T014.
- B depende de A só pelo arquivo `cronograma.js` e pela marca de visibilidade que a ordenação
  preserva; C depende de A (a coluna PDF) e de B (o gatilho da ordenação).
- T029 vem antes de T019 terminar: sem ela, a ordenação devolve o foco ao botão e o observador o
  toma em seguida.
- T026 depende de A, B e C, e fecha o C.
