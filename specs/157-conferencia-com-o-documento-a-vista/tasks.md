# Tasks: Conferência com o documento à vista

**Input**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/telas.md](contracts/telas.md), [quickstart.md](quickstart.md)

**Tests**: pedidos — a spec tem critérios de sucesso de teste (SC-2141 a SC-2148, SC-2152 a SC-2158),
e a Constituição exige testes aprovados. Caminhos relativos a `backend/`, salvo indicação.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode correr em paralelo (arquivos diferentes, sem dependência pendente)
- **[Story]**: a história da spec (US1 a US8)

---

## Phase 1: Setup

- [X] T001 Banco de teste próprio `ps_157` (`DB_NAME=ps_157`) e banco de demonstração `ps157demo` com os cenários de treinamento (`CENARIOS_DE_TREINAMENTO=true uv run python manage.py carregar_cenarios_de_treinamento --banco ps157demo`); entrada `conferencia-157` **acrescentada** a `../.claude/launch.json`, sem sobrescrever as outras (quickstart)
- [X] T002 `uv sync --extra dev` na worktree, e `manage.py migrate --check` contra `ps_157` antes da primeira suíte

---

## Phase 2: Foundational (bloqueia as histórias)

- [X] T003 [P] Teste em `tests/interface/test_conferencia_com_o_documento_a_vista.py`: `GET documento-da-convocacao` não grava `CONSULTAR_DOCUMENTO_DA_CONVOCACAO` antes de o corpo ser consumido; grava uma vez depois de `b"".join(resposta.streaming_content)`; com o gerador fechado antes do fim (`resposta.streaming_content` iterado um bloco e `resposta.close()`), não grava; o download grava com *"baixado"*; `X-Frame-Options: SAMEORIGIN`; cabeçalhos `Content-Type`, `Content-Disposition` e `Cache-Control` de hoje (FR-6500, FR-6504, FR-6544; R-001; SC-2155)
- [X] T004 `entregar_e_registrar_ao_fim(fonte, *, anexo, verificado, ao_fim)` em `processo_seletivo/portal/arquivos.py`: `StreamingHttpResponse` sobre um gerador que lê `verificado` em blocos de `BLOCO`, chama `ao_fim()` depois do último e fecha a cópia no `finally`; os cabeçalhos de `entregar` e `marcar_como_privada`; comentário dizendo por que gerador e não arquivo (o `wsgi.file_wrapper`) (R-001)
- [X] T005 `documento_da_convocacao` em `processo_seletivo/interface/views.py`: `@xframe_options_sameorigin`; a consulta sai do `command_context` de antes da entrega e vai para o `ao_fim`, em `command_context` próprio; os eventos de integridade e de indisponível continuam antes da recusa; docstring com a decisão do usuário de 11/11 (FR-6544; R-001, R-002)
- [X] T006 Os testes de hoje que afirmam a consulta logo depois do `GET` da gestão passam a consumir a resposta: `tests/interface/test_permissoes_dos_documentos_da_convocacao.py`, `tests/interface/test_recusa_da_conferencia_documental.py`, `tests/interface/test_arquivo_indisponivel.py` (R-001)
- [X] T007 [P] Teste em `tests/interface/test_conferencia_com_o_documento_a_vista.py`: com `?painel=1`, integridade divergente e arquivo indisponível respondem 409 com `data-recusa-no-painel`, a frase de hoje, `X-Frame-Options: SAMEORIGIN`, o evento de hoje e nenhuma consulta; sem `?painel=1`, a página de recusa da área; 404 de quem não alcança, com e sem o parâmetro (FR-6510; R-002; SC-2144)
- [X] T008 `interface/_recusa_no_painel.html` (documento próprio, com a folha comum e `visualizador.css`, sem barra da gestão) e o ramo `?painel=1` em `documento_da_convocacao`, que captura `ArquivoIndisponivel` e a divergência de resumo depois de gravar o evento e responde o parcial emoldurável (R-002)
- [X] T009 O cartão de cada item sai de `processo_seletivo/interface/templates/interface/convocacao_documentos.html` para `interface/_documento_da_convocacao.html`, com os `id` pelo `id` do item (`conforme-<item>`, `motivo-<item>`, `abertura-<item>`, `item-titulo-<item>`), e `_contexto_do_cartao(...)` em `views.py` com o que o parcial lê; a página o inclui no laço (R-005)
- [X] T010 [P] `mesa.js` vira `processo_seletivo/interface/static/interface/visualizador.js`, lido por atributos `data-` (R-003); `tests/javascript/mesa.test.js` vira `tests/javascript/visualizador.test.js`, com as afirmações de hoje da Mesa passando pelo script novo; `mesa_inscricao.html` passa a carregar `visualizador.js` com os atributos — o mesmo desenho e os mesmos rótulos nas duas telas (FR-6533)
- [X] T011 [P] As regras do painel saem de `processo_seletivo/interface/static/interface/gestao/telas.css` para `processo_seletivo/interface/static/interface/grupos/visualizador.css`, carregada por `mesa_inscricao.html` e `convocacao_documentos.html` pelo bloco `estilo_da_pagina`; comentário sem `}}`, `%}`, `<a>` nem *checkbox* (R-013)

**Checkpoint**: a entrega grava ao fim, a rota se deixa emoldurar, o cartão é parcial, a Mesa roda no script novo. A suíte de hoje passa.

---

## Phase 3: User Story 1 — Conferir com o arquivo ao lado, em tela larga (P1) 🎯 MVP

**Goal**: em tela larga, o arquivo no painel ao lado do formulário, com a pessoa e a versão na barra.

**Independent Test**: C09, 1280 × 800, conferir o diploma de Alice sem sair da página; a trilha tem uma consulta à versão 1.

### Testes da US1

- [X] T012 [P] [US1] Teste da página em `tests/interface/test_conferencia_com_o_documento_a_vista.py`: o contêiner `data-visualizador` com o painel antes da lista e `hidden`; cada *"Abrir"* com `data-abrir-documento`, `data-documento`, `data-versao`, `data-tamanho`, o tamanho à vista e o nome acessível *"Abrir ‹documento›, versão N"*; a barra com o lugar da identificação; *"Baixar"* mantido; `visualizador.js` e `htmx.min.js` com `defer`; nenhum `style=`, `<style>` nem `<script>` sem `src` (FR-6505 a FR-6508, FR-6531; UX-640, UX-641)
- [X] T013 [P] [US1] Teste de JavaScript em `tests/javascript/visualizador.test.js`: em tela larga, o clique em *"Abrir"* põe o endereço com `?painel=1` na moldura, preenche as duas linhas da barra, marca o link com `aria-current`, leva o foco ao título; trocar de documento troca tudo; *"Fechar"* esconde o painel, limpa a moldura e leva o foco ao primeiro campo do formulário do item; nada é pedido sem clique (FR-6501, FR-6505 a FR-6508, FR-6523)

### Implementação da US1

- [X] T014 [US1] `convocacao_documentos.html`: o contêiner de trabalho, o painel `<aside>` antes da lista com o título, a linha de identificação, a moldura com `title`, e a região viva `role="status"`; o link *"Abrir"* do parcial com os atributos e o tamanho (`tamanho_legivel` do arquivo da apresentação, em `_contexto_do_cartao`) (R-003, R-011, R-012)
- [X] T015 [US1] `visualizador.js`: abrir no painel em tela larga, com a barra de duas linhas lida dos atributos, *"Abrir em aba própria"*, *"Baixar"* e *"Fechar"*; levar o cartão do item à vista; o carregamento (*"Carregando o documento (‹tamanho›)…"*) até o `load` (FR-6505 a FR-6509, FR-6512; UX-644)
- [X] T016 [US1] Classes novas em `processo_seletivo/interface/static/interface/telas/convocacao-documentos.css` e em `grupos/visualizador.css` (a grade acima de `64rem`, o painel fixo na rolagem, a barra de duas linhas) (R-013)

**Checkpoint**: US1 funciona sozinha; registrar ainda recarrega a página.

---

## Phase 4: User Story 2 — Registrar sem recarregar a página (P1)

**Goal**: o registro troca o cartão, a situação e a confirmação no lugar.

**Independent Test**: registrar o diploma de Alice e comparar o fragmento com a página recarregada.

### Testes da US2

- [X] T017 [P] [US2] Testes em `tests/interface/test_conferencia_com_o_documento_a_vista.py`, com `HX-Request`: aceito (200, cartão com a conferência, `hx-swap-oob` da situação, das pessoas e da confirmação; chave nova no formulário); sem abertura (200, recusa no cartão com a UX-651 e o *"Abrir a versão N"*, o preenchimento mantido); versão superada (o resultado desmarcado, o motivo mantido); desfecho registrado no meio (`HX-Refresh: true`); sem identidade (`HX-Retarget: #mensagem-<item>`, frase da UX-646); duplo envio com a mesma chave (uma conferência); sem `HX-Request`, o 302 de hoje (FR-6514 a FR-6518; SC-2141, SC-2145)
- [X] T018 [P] [US2] Teste de igualdade em `tests/interface/test_conferencia_com_o_documento_a_vista.py`: depois de cada registro do C09, o texto do cartão, do resumo e da situação no fragmento é o da página recarregada (SC-2146)

### Implementação da US2

- [X] T019 [US2] `conferir_documento_view` em `views.py`: o ramo `HX-Request` (R-006) — o cartão pelo parcial com a recusa e o preenchimento, os `hx-swap-oob`; `HX-Refresh` quando a recusa não tem cartão; `HX-Retarget` sem identidade, antes de `pedir_identificacao`
- [X] T020 [US2] Parcial `interface/_confirmacao_da_conferencia.html` com o que foi registrado (UX-642), vazio ao carregar a página; a seção da situação e a navegação das pessoas com `id` estáveis e marcadas para troca (`hx-swap-oob`) (R-006)
- [X] T021 [US2] O formulário do parcial: `hx-post`, `hx-target="closest article"`, `hx-swap="outerHTML"`, o `<p id="mensagem-<item>" role="alert">` vazio; `visualizador.js` escreve a frase da falha de rede no `htmx:sendError` (UX-646) e leva o foco à recusa depois da troca (FR-6525)
- [X] T022 [US2] A recusa sem abertura com a frase da UX-651 em `_recusa_da_conferencia` e no parcial — a mesma no caminho sem script (FR-6516)

**Checkpoint**: US1 + US2 entregam o achado 10 em tela larga.

---

## Phase 5: User Story 3 — Quando o arquivo não aparece na página (P1)

**Goal**: alternativa, recusa legível, releitura da marca.

**Independent Test**: com `pdfViewerEnabled` falso, a alternativa; com a entrega recusada, a frase no painel e nenhuma abertura.

### Testes da US3

- [X] T023 [P] [US3] Teste do fragmento do cartão em `tests/interface/test_conferencia_com_o_documento_a_vista.py`: `GET .../itens/<item>/cartao` devolve o parcial com *"aberto por você"* depois de uma consulta consumida, e sem ela antes; não grava consulta; 404 fora do alcance (FR-6503; R-005)
- [X] T024 [P] [US3] Teste de JavaScript em `tests/javascript/visualizador.test.js`: com `navigator.pdfViewerEnabled === false`, o painel mostra a UX-643, sem `src` na moldura, com aba própria e download; com `undefined`, a prévia; no `load` da moldura com `data-recusa-no-painel`, a frase sobe para o painel e a aba própria e o download somem; no `load` normal, o cartão é relido, e uma segunda vez se a marca não vier (FR-6502, FR-6503, FR-6510, FR-6513)

### Implementação da US3

- [X] T025 [US3] `cartao_do_documento_da_convocacao` em `views.py` e a rota `documentos/itens/<item>/cartao` em `urls.py`, pela porta de `_convocacao_para_conferir`, sem registro (R-005)
- [X] T026 [US3] `visualizador.js`: a alternativa por `pdfViewerEnabled` (UX-643); a recusa lida da moldura (UX-654); a releitura do cartão no `load`, com uma tentativa a mais depois de um segundo, preservando o que está digitado e adiando a troca enquanto o foco está no formulário; a releitura também depois de *"Abrir em aba própria"* e de *"Baixar"*, na volta à aba (R-004, R-005; FR-6503, FR-6511)
- [X] T027 [US3] A ajuda recolhida do formulário no parcial: o arquivo que não abre (UX-645) e o significado da marca (UX-652) (FR-6513, FR-6549)

**Checkpoint**: a conferência em tela larga está completa.

---

## Phase 6: User Story 6 — Teclado e leitor de tela (P1)

**Goal**: tudo por teclado; foco previsível; anúncios.

**Independent Test**: só teclado, com leitor de tela, os dois documentos de Alice (SC-2149, humano).

- [X] T028 [P] [US6] Teste de JavaScript em `tests/javascript/visualizador.test.js`: a região viva recebe *"Carregando…"*, *"Aberto por você: ‹documento›, versão N."* e a confirmação, uma vez cada; depois da troca de um cartão com recusa, o foco está na recusa; o painel não prende o foco (FR-6523 a FR-6525)
- [X] T029 [US6] `visualizador.js` e o parcial: o `title` da moldura com documento, versão e pessoa; os anúncios; o foco depois das trocas (R-012)
- [X] T030 [US6] Teste de página em `tests/interface/test_conferencia_com_o_documento_a_vista.py`: o `<aside>` com `aria-labelledby`, a região viva, a marca e o estado por texto (FR-6524, FR-6526)

---

## Phase 7: User Story 4 — Conferir numa tela pequena (P2)

**Goal**: abaixo da tela larga, o arquivo fora da página e a volta com o formulário e o retorno.

**Independent Test**: 390 px, abrir, digitar, voltar, registrar.

- [X] T031 [P] [US4] Teste de JavaScript em `tests/javascript/visualizador.test.js`: abaixo da tela larga, o clique não é interceptado e nenhum painel é criado; o item e o preenchimento vão para `sessionStorage`; no `visibilitychange` para `visible`, o cartão é relido, o link *"Voltar à conferência do ‹documento›"* aparece e recebe o foco; com recarga (o item guardado e o formulário vazio), o preenchimento é restaurado com a frase da UX-653 e nada é enviado; o registro aceito apaga o guardado; cruzar a fronteira com o painel aberto o fecha sem perder o que foi digitado (FR-6527 a FR-6530; SC-2156)
- [X] T032 [US4] `visualizador.js`: a volta e a restauração (R-010), com o comentário sobre `sessionStorage` e a máquina compartilhada; as classes do link de retorno e da frase de restauração em `telas/convocacao-documentos.css`

---

## Phase 8: User Story 5 — Passar ao próximo documento ou à próxima pessoa (P2)

**Goal**: a confirmação oferece o passo seguinte, sem abrir nem registrar nada.

- [X] T033 [P] [US5] Testes em `tests/interface/test_conferencia_com_o_documento_a_vista.py`: depois do diploma, a confirmação oferece *"Abrir"* o comprovante, com os atributos do visualizador, e nenhuma consulta é gravada; depois do último de Alice, a próxima pessoa com documento a conferir (o critério da FR-5024 da `143`); no fim do recorte, *"Não há outro documento a conferir neste recorte."* e *"Voltar à convocação"*; nenhum gesto da confirmação grava conferência (FR-6519 a FR-6522; SC-2142)
- [X] T034 [US5] `_confirmacao_da_conferencia(...)` em `views.py` e o parcial: o próximo documento da leitura relida, a próxima pessoa de `pessoas_do_recorte`, o fim do recorte (R-007, UX-642)

---

## Phase 9: User Story 8 — A Mesa do avaliador (P2)

**Goal**: recusa legível, alternativa, *"Baixar"*, volta preservada; sem exigência de abertura.

- [X] T035 [P] [US8] Testes em `tests/interface/test_mesa_visualizador.py`: `?painel=1` com integridade e indisponível na rota da Mesa (409, `data-recusa-no-painel`, emoldurável, o evento de hoje); a lista de documentos relida pela rota nova, com *"aberto"* depois da abertura; *"Baixar"* na barra; concluir a avaliação sem abrir documento continua aceito; a gravação da abertura na Mesa continua antes da entrega (FR-6545 a FR-6548; SC-2157, SC-2158)
- [X] T036 [US8] `documento_da_mesa` em `views.py`: o ramo `?painel=1` (R-002); a docstring diz que a abertura da Mesa continua gravada antes da entrega, e por quê (FR-6548)
- [X] T037 [US8] A lista de documentos da Mesa sai para `interface/_documentos_da_mesa.html`; a rota `mesa-documentos` em `urls.py` e a view, pela porta da Mesa (R-005)
- [X] T038 [US8] `mesa_inscricao.html`: os atributos do visualizador, *"Baixar"*; `visualizador.js`: a volta na Mesa (nota, parecer, ficha do barema; *"Voltar ao documento ‹nome›"*) (FR-6546, FR-6547; UX-653)
- [X] T039 [P] [US8] Testes de JavaScript da Mesa em `tests/javascript/visualizador.test.js`: alternativa, recusa da moldura, volta e restauração na Mesa

---

## Phase 10: User Story 7 — A pendência registrada, e o aviso à vista (P3)

**Goal**: *"Pedir aviso para ‹nome›"* ao fim da pessoa; a situação em três grupos.

### Testes da US7

- [X] T040 [P] [US7] Testes em `tests/integration/avisos/test_aviso_de_uma_pessoa.py`: o pedido de uma pessoa grava o mesmo aviso, com o mesmo texto, que o lote gravaria para ela no mesmo instante — todas as pendências elegíveis; um pedido no dia em que o lote já a avisou é recusado com *"já avisada hoje"* e a data do dia seguinte, e vice-versa; as demais exclusões, com o motivo e sem data; a chave desligada; o Processo encerrado; a trilha com `"recorte": "pessoa"` e a convocação; a mesma chave para outra pessoa é outro pedido; nada agendado; registrar pendência não grava aviso (FR-6534, FR-6537 a FR-6542; FR-4603, FR-4605, FR-4620 da `134`; SC-2152, SC-2154)
- [X] T041 [P] [US7] Testes em `tests/interface/test_conferencia_com_o_documento_a_vista.py`: a confirmação da pendência diz que nenhum aviso foi pedido (UX-647); terminada a pessoa com pendência, oferece *"Pedir aviso para ‹nome›"*, ou o motivo e a data, ou a frase do envio desabilitado; a rota `aviso-de-pendencia` com e sem `HX-Request`; a situação mostrada sem recarga é a do cartão da convocação (FR-6535, FR-6536; SC-2153)
- [X] T042 [P] [US7] Testes da situação em três grupos em `tests/unit/interface/test_conducao_da_convocacao.py` (ou onde `frase_do_aviso` já é testada), um caso por estado da `066` (FR-6543; UX-649); os testes da `143` e da `134` que prendiam as frases antigas passam às novas, citando a FR-6543

### Implementação da US7

- [X] T043 [US7] `processo_seletivo/avisos/application/pendencias.py`: `convocacao_id` em `selecionar` e `avisar_pendencias` (o filtro, o `payload`, a recusa individual com o motivo, o `detalhe` e o motivo da trilha); `proximo_dia_do_pedido(agora)`; o docstring do módulo cita a revisão da FR-4603 da `134` (R-008)
- [X] T044 [US7] `pedir_aviso_de_pendencia_view` em `views.py` e a rota `aviso-de-pendencia` em `urls.py`; a oferta na confirmação (R-008; UX-648, UX-650)
- [X] T045 [US7] `frase_do_aviso` em `processo_seletivo/interface/conducao_da_convocacao.py`: três grupos (R-009; UX-649)

---

## Phase 11: Polish & cross-cutting

- [X] T046 [P] `specs/157-conferencia-com-o-documento-a-vista/rastreabilidade.md`: cada FR, SC e caso-limite com o teste que o cobre
- [X] T047 [P] Varreduras: `tests/test_vocabulario_da_convocacao.py` e os guardiões de folha e de acessibilidade com as classes novas; nenhum texto diz *viu*, *leu* ou *conferiu o arquivo* (FR-6549)
- [X] T048 Integrar a `main` atualizada (a `154` e a `152`, se tiverem entrado) e resolver os conflitos preservando os requisitos de cada incremento; anotar no PR onde os arquivos se cruzam (R-015)
- [X] T049 `cd backend && make lint check` e `DB_NAME=ps_157 make test-pg` — a suíte inteira verde é a prova de que nada mais mudou (FR-6532)
- [X] T050 Verificação no navegador pelo quickstart: tela larga e 390 px, com prévia e sem ela, a recusa no painel, a Mesa, sem script; contar os gestos por documento no C09 (SC-2140: no máximo três, sem troca de aba nem recarga); capturas em `specs/157-conferencia-com-o-documento-a-vista/capturas/`
- [X] T051 README: a linha da `157` diz que está implementada (PR sem merge), e a Visão do Sistema, se a tela mudou de forma descrita lá
- [X] T052 PR de implementação, sem merge, com as evidências, as dependências (a ordem com a `154` e a `152`) e as pendências humanas (SC-2149, SC-2150, SC-2151, SC-2159)

---

## Dependencies & Execution Order

- **Setup (1)** → **Foundational (2)** → histórias.
- **US1** depende da fase 2. **US2** depende da US1 (o parcial e a página). **US3** depende da US1
  (o painel). **US6** atravessa US1–US3. **US4** depende do `visualizador.js` da US1 e da releitura da
  US3. **US5** depende da US2 (a confirmação). **US8** depende só da fase 2. **US7** depende da US5 (a
  confirmação ao fim da pessoa) para a oferta; o comando (T043) é independente.
- **Polish** por último; T048 antes de T049 e T050.

### Dentro de cada história

Testes primeiro, falhando; depois a implementação; o checkpoint roda o arquivo de teste da história.

## Parallel Example

```text
Fase 2: T003, T007, T010, T011 em paralelo (arquivos diferentes); T004 → T005 → T006; T008 depois de T005.
US8 (T035–T039) em paralelo com US2–US5, salvo `visualizador.js`, que é um arquivo só: as tarefas de
script se fazem em sequência.
US7: T040 e T043 (o comando) em paralelo com qualquer história de tela.
```

## Implementation Strategy

**MVP**: fase 2 + US1 + US2 — o achado 10 em tela larga, com a abertura gravada ao fim da entrega.
Depois US3 e US6 (completam a conferência em tela larga), US4 e US5, US8, US7. Um commit por fase, com
a suíte da área verde; a suíte inteira uma vez, no fim (T049).
