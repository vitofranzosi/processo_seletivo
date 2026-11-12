---
description: "Tarefas da 150 — o envio de vários documentos da convocação, sem perder escolha"
---

# Tasks: O envio de vários documentos da convocação, sem perder escolha

**Input**: [spec.md](spec.md) (revista com o achado 11), [plan.md](plan.md), [research.md](research.md)
(D-001 a D-006, R-001 a R-008), [data-model.md](data-model.md),
[contracts/envio-de-varios.md](contracts/envio-de-varios.md), [quickstart.md](quickstart.md)

**Tests**: TDD. Em cada história, os testes vêm antes e **falham** antes da implementação. A suíte é
contra PostgreSQL (`make test-pg`, com `DB_NAME` próprio da worktree); os testes de script, por
`node --test`, com o shim de `tests/javascript/dom.js`.

**Organização**: por história, na ordem de prioridade da spec — US1 e US2 (P1), US3 e US5 (P2), US4
(P3). Os caminhos são relativos à raiz do repositório.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode correr em paralelo (arquivo diferente, sem dependência de tarefa aberta)
- **[Story]**: a história da spec (US1 a US5)

---

## Phase 1: Setup

**Purpose**: partir da `main` certa e saber o que as features vizinhas já mudaram.

- [ ] T001 Atualizar a worktree sobre a `main` e conferir `manage.py migrate --check`; conferir que `.specify/feature.json` aponta para `specs/150-envio-de-varios-documentos-da-convocacao`
- [ ] T002 **Cruzamento com a 154** (antes de qualquer mudança na confirmação): conferir por `gh pr view 479 --json state` e `git log origin/main -- backend/processo_seletivo/portal/obrigacoes.py` se a implementação da 154 já entrou; se entrou, reler `ConfirmacaoDoEnvio`, `confirmacao_do_envio` e o texto do cartão em `backend/processo_seletivo/portal/obrigacoes.py` e o topo de `backend/processo_seletivo/portal/templates/portal/_cartao_do_documento_da_convocacao.html` e ajustar T013/T015 ao que ela deixou; se não entrou, registrar no PR que a 150 muda só a lista da confirmação e o bloco `.envio` do cartão (tabela *Os cruzamentos* do [plan.md](plan.md))
- [ ] T003 [P] Conferir o mesmo para a 156 (frases do desfecho em `backend/processo_seletivo/portal/obrigacoes.py` e `backend/processo_seletivo/portal/templates/portal/convocacao.html`) e para a 157 (só gestão); anotar no PR o que estiver na `main`

---

## Phase 2: Foundational

**Purpose**: a forma da sessão, o ramo JSON da rota e a marcação que o script lê. Bloqueia todas as
histórias.

### Testes primeiro

- [ ] T004 [P] Em `backend/tests/interface/test_portal_documentos_da_convocacao.py`, testar o ramo do lote (contrato §1): com `X-Envio-De-Varios: 1/2`, o envio aceito responde 200 JSON `resultado=recebido`, `ancora` e `volta` terminando em `#confirmacao`; o recusado (não PDF), `resultado=recusado` com a frase de hoje; o mesmo arquivo de novo, `ja_recebido`; sem arquivo, `recusado` com "Escolha um arquivo PDF antes de enviar."; o 404 continua 404; cabeçalho malformado (`x/0`, `3/2`, `abc`) responde o 302 de hoje; sem o cabeçalho, nada muda (FR-5605, R-002)
- [ ] T005 [P] No mesmo arquivo, testar a sessão (data-model): `1/n` zera as duas chaves; `2/n` acrescenta; o envio individual grava a forma de lista com um; a forma antiga (dicionário de um envio, recusa de uma âncora) ainda é lida na volta; a volta consome uma vez e só na mesma inscrição (R-003)
- [ ] T006 [P] No mesmo arquivo, testar a marcação do cartão (contrato §3): `data-documento` em todo cartão; `data-resumo-recebido` igual ao `content_hash` da vigente em todo item com apresentação — inclusive conferido sem formulário e aproveitado da inscrição —, e ausente sem apresentação; `[data-remover-escolha]` e `[data-arquivo-repetido]` presentes com `hidden` em cada formulário (R-005, R-007)
- [ ] T007 [P] Em `backend/tests/interface/test_portal_jornada_consolidada.py` (o teste de contagem de consultas da convocação, com `CaptureQueriesContext`), confirmar que a contagem não muda com o `data-resumo-recebido` (R-005)

### Implementação

- [ ] T008 Em `backend/processo_seletivo/portal/views.py`, `apresentar_documento_da_convocacao`: ler e validar `X-Envio-De-Varios` (`k/n`, `1 ≤ k ≤ n`); com ele, responder `JsonResponse` com `resultado`, `ancora`, `frase` e `volta` (`?lote=n#confirmacao` se algum recebido no acumulado, senão `#item-‹primeiro recusado›`); manter o 404 e o 302 sem cabeçalho (R-002, R-004)
- [ ] T009 No mesmo arquivo, `_recusar_no_cartao`, a gravação da confirmação e `_da_inscricao`/`_volta_do_envio`: gravar as listas `envios`/`total` e `recusas`, zerar em `k = 1`, ler a forma antiga como lista de um (R-003)
- [ ] T010 Em `backend/processo_seletivo/portal/templates/portal/_cartao_do_documento_da_convocacao.html`: `data-documento` e `data-resumo-recebido` no `<li>`; no bloco `.envio`, o `<button type="button" data-remover-escolha hidden>` com "Remover a escolha" e `<span class="oculto">: ‹documento›</span>`, e o `<p data-arquivo-repetido hidden id="repetido-‹id›">` citado no `aria-describedby` do campo; **não** tocar o topo do cartão (selos, `item.texto`), que é da 154 (UX-503, UX-504)
- [ ] T011 [P] Criar `backend/processo_seletivo/portal/static/portal/varios.js` com o esqueleto: `(function(){…})()` sem módulo, ES5, sem armazenamento; carregar em `backend/processo_seletivo/portal/templates/portal/convocacao.html` **antes** de `envio.js`; atualizar `test_a_convocacao_carrega_os_tres_scripts_e_nenhum_outro` em `backend/tests/interface/test_portal_documentos_da_convocacao.py` para os quatro, em ordem (FR-5614, R-001)
- [ ] T012 [P] Em `backend/processo_seletivo/portal/static/portal/portal.css`, regras para as classes novas (o aviso de atenção, o botão de texto de remover, o progresso de vários), com quebra de linha a 375 px; conferir os guardiões de classe sem regra e de `}}` na folha (UX-502, UX-503, UX-504)

**Checkpoint**: a rota fala JSON com o cabeçalho, a sessão guarda listas, o cartão traz a marcação, e
nada visível mudou para quem usa a tela.

---

## Phase 3: User Story 1 — Enviar de uma vez os documentos escolhidos (P1) 🎯 MVP

**Goal**: com dois ou mais escolhidos, qualquer botão escolhido envia todos, um de cada vez, e a
volta confirma os N.

**Independent Test**: quatro documentos, quatro escolhidos, enviar por qualquer cartão; quatro
recebidos, a confirmação diz os quatro, o "Andamento" conta quatro (SC-1800).

### Testes primeiro

- [ ] T013 [P] [US1] Em `backend/tests/interface/test_portal_documentos_da_convocacao.py`, testar a volta de um lote de quatro, todos recebidos: "Recebemos 4 de 4 documentos", os quatro nomes com data e hora, a próxima tarefa ou a conclusão de hoje calculadas depois do último; com um só, a frase de hoje, sem "1 de 1" (FR-5608, contrato §2) — ajustar à confirmação da 154 se T002 a encontrou na `main`
- [ ] T014 [P] [US1] Criar `backend/tests/javascript/varios.test.js`: a contagem N conta os cartões com arquivo — de "O que falta", opcionais e "Enviar outro arquivo" — (FR-5602); com N = 1 o botão diz "Enviar" e o `submit` segue nativo; com N ≥ 2, **todo** botão escolhido diz "Enviar os N documentos escolhidos", sem o `oculto` com o nome (FR-5601, FR-5613); trocar o arquivo no mesmo cartão não muda N; o anúncio "N documentos escolhidos para enviar." vai para a região viva sem mover o foco (UX-501)
- [ ] T015 [P] [US1] No mesmo arquivo, testar o lote com `fetch` simulado: envia na ordem do DOM, um por vez, com `X-Envio-De-Varios: k/n` e o `FormData` do formulário de cada cartão; desabilita enviar, escolher e remover durante o lote; escreve "Enviando k de n: ‹documento›… Não feche esta página." no `.progresso` do cartão acionado e na região viva; ao fim, navega para a `volta` da última resposta (FR-5606, FR-5607, R-004)
- [ ] T016 [P] [US1] Criar `backend/tests/integration/portal/test_envio_de_varios.py`: pelo cliente de teste, quatro POSTs com `1/4…4/4`, depois o GET da `volta`; quatro `ApresentacaoDeDocumento`, quatro eventos `APRESENTAR` na trilha, iguais aos do envio individual (FR-5605, SC-1800)

### Implementação

- [ ] T017 [US1] Em `backend/processo_seletivo/portal/obrigacoes.py`, `confirmacao_do_envio` passa a receber a lista de envios e o total: monta a frase "Recebemos R de N documentos." e a lista (nome, data, hora) com N ≥ 2, a frase de hoje com um; `proxima`, `conclusao` e `rotulo` continuam calculados uma vez, como hoje (não reescrever o que a 154 mudar); `ConfirmacaoDoEnvio` ganha o campo da lista
- [ ] T018 [US1] Em `backend/processo_seletivo/portal/templates/portal/convocacao.html` (o bloco `#confirmacao`), renderizar a lista de recebidos quando houver
- [ ] T019 [US1] Em `backend/processo_seletivo/portal/static/portal/varios.js`: contagem, rótulo, anúncio, interceptação do `submit` no formulário (`preventDefault` e `stopPropagation` com N ≥ 2), o lote sequencial por `fetch`, o progresso e a navegação final (R-001, R-002, R-004)
- [ ] T020 [US1] No mesmo script, o `pageshow`: restaurar rótulos e progresso de uma página devolvida pelo "voltar" (Edge Cases)

**Checkpoint**: SC-1800 verde; o envio de um continua idêntico.

---

## Phase 4: User Story 2 — Saber o que não foi recebido, sem perder o que foi (P1)

**Goal**: recusa parcial, recusa total, queda de conexão e acesso expirado dizem o que chegou e o que
não chegou, e o que chegou fica.

**Independent Test**: quatro escolhidos, o segundo uma imagem; três recebidos, a confirmação aponta o
segundo, e o cartão dele traz a recusa de hoje (SC-1802).

### Testes primeiro

- [ ] T021 [P] [US2] Em `backend/tests/interface/test_portal_documentos_da_convocacao.py`, testar a volta de um lote com recusas: "Recebemos 3 de 4 documentos", "1 documento não foi recebido" com link para `#item-‹id›`, e a recusa no cartão dele (`role=alert`, `data-recusa`); lote todo recusado: a `volta` é o cartão do primeiro, e cada cartão traz a sua recusa (FR-5608, FR-5609)
- [ ] T022 [P] [US2] Em `backend/tests/javascript/varios.test.js`, testar: a recusa de um não interrompe os seguintes (FR-5606); resposta não JSON (`text/html` 200 da página de acesso, 404) para o lote, não navega, diz a frase de acesso expirado de hoje, e as escolhas não enviadas continuam; `sendError` (rejeição do `fetch`) e 5xx, a frase de conexão ou genérica de hoje; os já recebidos perdem a escolha e dizem que foram enviados; o botão volta a oferecer o envio dos restantes com o N novo (FR-5610, contrato §1)
- [ ] T023 [P] [US2] Em `backend/tests/integration/portal/test_envio_de_varios.py`, testar o prazo que vence no meio (`2/4` recebido, `3/4` com a recusa de prazo) e a chamada decidida no meio: os anteriores ficam, os seguintes recusados pela regra de hoje (Edge Cases, FR-5605)

### Implementação

- [ ] T024 [US2] Em `backend/processo_seletivo/portal/obrigacoes.py` e `backend/processo_seletivo/portal/templates/portal/_cartao_do_documento_da_convocacao.html`: a recusa passa a ser por âncora (uma por cartão), lida da lista da sessão, no lugar de `recusa_do_envio.ancora == item.ancora`; a confirmação conta os recusados e liga cada um ao cartão
- [ ] T025 [US2] Em `backend/processo_seletivo/portal/static/portal/varios.js`: o tratamento de resposta não JSON, de falha de rede e de 5xx, com as frases de hoje de `envio.js` (copiadas, não importadas: os scripts não são módulos), sem sair da página; a contagem refeita para os restantes

**Checkpoint**: SC-1801 e SC-1802 verdes.

---

## Phase 5: User Story 3 — Enviar só um, mesmo com outros escolhidos (P2)

**Goal**: "Remover a escolha" e o cartão vazio sem perda.

**Independent Test**: três escolhidos, remover dois, enviar o restante; só ele recebido.

- [ ] T026 [P] [US3] Em `backend/tests/javascript/varios.test.js`, testar: o botão de remover aparece com arquivo e some sem; remover limpa o campo, volta o nome a "Nenhum arquivo escolhido", tira o `pronta` e refaz o N dos outros (FR-5603, UX-503); `submit` num cartão sem arquivo não sai da página, escreve "Escolha um arquivo PDF antes de enviar." no cartão e mantém as escolhas (FR-5604)
- [ ] T027 [US3] Em `backend/processo_seletivo/portal/static/portal/varios.js`, revelar e ligar `[data-remover-escolha]` e tratar o cartão vazio

**Checkpoint**: US3 verde; com uma escolha restante, o envio é o de hoje.

---

## Phase 6: User Story 5 — O mesmo arquivo em dois documentos (P2) — achado 11

**Goal**: avisar no cartão, antes do envio, o arquivo idêntico ao escolhido ou ao já enviado para
outro documento da convocação, sem bloquear.

**Independent Test**: o mesmo PDF, renomeado, no "Diploma" e no "Comprovante de residência": aviso
nos dois, envio possível; depois de enviar o diploma, o mesmo PDF no comprovante avisa "já enviou"
(SC-1806).

### Testes primeiro

- [ ] T028 [P] [US5] Em `backend/tests/javascript/varios.test.js`, com `crypto.subtle` do Node: o resumo calculado é o SHA-256 hexadecimal minúsculo, igual ao de `shared.arquivos.resumo` para os mesmos bytes; dois escolhidos idênticos de nomes diferentes avisam nos dois, cada um nomeando o outro; o escolhido igual a um `data-resumo-recebido` de **outro** cartão avisa "já enviou para ‹documento›"; igual ao do **próprio** cartão, não avisa; mais de um coincidente, nomes unidos por vírgula e "e"; trocar ou remover a escolha tira o aviso dos dois cartões; nomes iguais e conteúdos diferentes não avisam (FR-5615, FR-5617, SC-1806, SC-1807)
- [ ] T029 [P] [US5] No mesmo arquivo: o aviso não muda rótulo, `pronta` nem N, e o cartão avisado entra no lote (FR-5616); sem `crypto.subtle`, ou com a leitura do arquivo rejeitada, nenhum aviso e nenhuma frase de "comparado" (FR-5619); a escolha trocada durante o cálculo descarta o resultado velho; o `submit` durante o cálculo envia sem esperar (FR-5619); nenhuma requisição sai na escolha (FR-5618)
- [ ] T030 [P] [US5] Em `backend/tests/test_vocabulario_dos_documentos_da_convocacao.py` (ou no guardião de vocabulário que cobre o portal da convocação), incluir as frases novas do contrato §4 e conferir que nenhuma diz "aceito", "aprovado" ou "conferido"

### Implementação

- [ ] T031 [US5] Em `backend/processo_seletivo/portal/static/portal/varios.js`: o cálculo do resumo por `file.arrayBuffer()` e `crypto.subtle.digest`, preso ao campo e descartado se a escolha mudar; a comparação com os outros escolhidos e com os `data-resumo-recebido` dos outros cartões; o aviso em `[data-arquivo-repetido]`, revelado, com anúncio na região viva sem mover o foco (R-008, UX-504)
- [ ] T032 [US5] Conferir o `Cache-Control` da tela da convocação (`backend/processo_seletivo/portal/views.py`, `convocacao`) e registrar em `specs/150-envio-de-varios-documentos-da-convocacao/research.md`, em R-006, o que encontrou; se não for privada, não mudar aqui — registrar como achado para o usuário

**Checkpoint**: SC-1806 e SC-1807 verdes, com e sem `crypto.subtle`.

---

## Phase 7: User Story 4 — A tela sem script continua honesta (P3)

**Goal**: sem script, envio de um por vez, com a frase que diz isso.

**Independent Test**: com o script desligado, a frase antes do primeiro cartão com envio; envio de um,
como hoje (SC-1803).

- [ ] T033 [P] [US4] Em `backend/tests/interface/test_portal_documentos_da_convocacao.py`, testar: com documento a enviar, um `<noscript>` com a frase da FR-5612 antes do primeiro cartão com envio, e nenhum sem documento a enviar; a frase não aparece fora do `<noscript>`; o envio sem cabeçalho volta como hoje (FR-5612, SC-1803)
- [ ] T034 [US4] Em `backend/processo_seletivo/portal/templates/portal/convocacao.html`, o `<noscript><p class="instrucao">…</p></noscript>` antes do primeiro cartão com envio (R-007)

---

## Phase 8: Polish & Cross-Cutting

- [ ] T035 Em `backend/tests/navegador/test_jornada_dos_documentos_da_convocacao.py`, uma jornada no navegador real, a 375 px e no desktop: quatro escolhidos, um recusado, volta com "Recebemos 3 de 4"; o mesmo PDF em dois cartões com o aviso; sem rolagem horizontal em nenhuma etapa (SC-1801, SC-1802, SC-1804, SC-1806, UX-502). Fechar as conexões do ORM ao sair, como a fixture do navegador já faz
- [ ] T036 [P] Rodar `tests/test_armazenamento_no_navegador.py`, `tests/test_citacoes_de_requisito.py` e os guardiões da CSP e das folhas contra PostgreSQL; conferir que `varios.js` não usa armazenamento e que nenhum estilo ou script foi escrito em template (FR-5611, FR-5614)
- [ ] T037 [P] Atualizar a linha da `150` no `README.md` (implementada, com o PR) e a seção do portal em `doc/` que descreve o envio da convocação, se houver
- [ ] T038 Percorrer o [quickstart.md](quickstart.md), cenários 1 a 15, no `runserver` da worktree, com o seletor de identidade e o código de acesso no terminal; registrar em `specs/150-envio-de-varios-documentos-da-convocacao/verificacao.md` o que se viu, com capturas
- [ ] T039 `cd backend && make lint check test-pg`, sozinho no cluster; registrar números no PR
- [ ] T040 [P] Registrar como pendência humana: SC-1805 (três pessoas, primeira tentativa) e o leitor de tela real do SC-1804; e, no PR, as três perguntas abertas da spec (aviso depois do recebimento sem script, a coincidência na conferência da gestão, outras chamadas)

---

## Dependencies & Execution Order

- **Setup (T001–T003)** → **Foundational (T004–T012)** → histórias.
- **US1 (T013–T020)** é o MVP e vem primeiro: o lote, o script e a confirmação de vários.
- **US2 (T021–T025)** depende de US1 (o lote e a confirmação existem); toca a recusa por âncora.
- **US3 (T026–T027)** depende só da Foundational e do esqueleto de `varios.js`; pode correr ao lado de
  US2, mas no mesmo script — em sequência se uma pessoa só.
- **US5 (T028–T032)** depende da Foundational (`data-resumo-recebido`, `[data-arquivo-repetido]`);
  independe do lote, e pode ser entregue antes de US1 se a ordem de merges pedir.
- **US4 (T033–T034)** depende só da Foundational.
- **Polish (T035–T040)** no fim.
- **A 154**: T002 decide se T013 e T017 rebaseiam sobre a confirmação dela. Se a 154 entrar depois da
  150, quem a implementa lê a lista da confirmação que a 150 acrescentou.

### Parallel Opportunities

- T004, T005, T006, T007 (testes da Foundational) juntos; T011 e T012 juntos, depois de T010.
- Em US1, T013, T014, T015 e T016 juntos — três arquivos diferentes, dois no mesmo arquivo JS de teste
  em blocos separados.
- Em US5, T028, T029 e T030 juntos.
- US4 inteira em paralelo com US2 ou US3 (arquivos diferentes: `convocacao.html` contra `varios.js`).

```text
# Foundational, testes:
T004 T005 T006 (test_portal_documentos_da_convocacao.py, blocos separados)  |  T007 (test_portal_jornada_consolidada.py)
# US1, testes:
T013 (interface)  |  T014 T015 (varios.test.js)  |  T016 (integration)
```

## Implementation Strategy

1. **MVP**: Setup, Foundational e US1 — o defeito relatado deixa de existir no caminho feliz.
2. **US2** antes de qualquer entrega ao candidato: sem ela, uma recusa no meio trocaria a perda
   silenciosa por outra (spec, *Why this priority* da US2).
3. **US3, US5, US4** em qualquer ordem; US5 (achado 11) pode ir num PR próprio, por depender só da
   marcação.
4. Cada fase fecha com o diretório tocado verde contra PostgreSQL; a suíte inteira, uma vez, em T039.
