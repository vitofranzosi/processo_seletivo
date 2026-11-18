# Tasks: A confirmação da inscrição por e-mail diz o que aconteceu, uma vez, e deixa rastro

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/portal.md](contracts/portal.md)

**Estado em 18/11**: todas as tarefas feitas; a suíte inteira contra PostgreSQL e o navegador estão na `rastreabilidade.md`.

**Tests**: pedidos pelo usuário (inscrição concluída, não concluída, falha, nova tentativa sem
duplicidade, múltiplas inscrições, acesso seguro, consistência entre mensagem, tela e registro).

Caminhos relativos a `backend/`.

## Phase 1: Setup

Nenhuma: sem dependência, migration ou configuração nova.

## Phase 2: Foundational

- [x] T001 Fazer `enviar_comprovante` contar o retorno de `send()` e devolver `True`/`False`, com `inscricao_id` no log da falha e sem endereço (FR-8360, FR-8361, R3) em `processo_seletivo/inscricoes/application/mensagem.py`
- [x] T002 Criar `confirmar`, `tentativas` e `ultima`, com a trava consultiva por inscrição, a leitura da trilha antes de enviar e a gravação da tentativa num ponto de salvamento (FR-8350, FR-8351, FR-8358, FR-8359, R1, R2) em `processo_seletivo/inscricoes/application/confirmacao.py`
- [x] T003 Testar o comando: envia e registra a tentativa 1 `ENVIADA`; rascunho não envia; segunda chamada não envia; falha registra `NAO_ENVIADA` e a seguinte tenta de novo; backend que devolve 0 conta como não enviada; duas inscrições da mesma pessoa são independentes; trilha sem endereço; duas threads simultâneas produzem uma mensagem (FR-8350–FR-8361, FR-8368) em `tests/integration/inscricoes/test_confirmacao_por_email.py`

**Checkpoint**: o comando cumpre "uma vez só" e deixa rastro, sem tela nenhuma.

## Phase 3: User Story 1 — a confirmação que diz o que aconteceu (P1) 🎯 MVP

**Goal**: o envio da inscrição dispara a mensagem nova, uma vez, com link ao comprovante.

**Independent Test**: enviar uma inscrição pelo portal e ler a mensagem: assunto com o Edital,
"enviada", o que acontece agora, link ao comprovante; nenhum CPF, telefone ou anexo.

- [x] T004 [P] [US1] Reescrever o assunto e o texto puro (FR-8353–FR-8356, UX-1020, UX-1021, R6) em `processo_seletivo/inscricoes/templates/inscricoes/mensagem/comprovante.txt`
- [x] T005 [P] [US1] Reescrever o HTML na moldura da `121`, com o botão "Ver meu comprovante" em `processo_seletivo/inscricoes/templates/inscricoes/mensagem/comprovante.html`
- [x] T006 [US1] Passar `edital` a `compor_comprovante` em `processo_seletivo/inscricoes/application/mensagem.py`
- [x] T007 [US1] Fazer `_confirmar_por_email` chamar `confirmacao.confirmar` com o ator do candidato e o endereço absoluto de `portal:comprovante` (FR-8357) em `processo_seletivo/portal/views.py`
- [x] T008 [US1] Redirecionar o comprovante sem sessão ao acesso com `destino`, antes de consultar (FR-8357, R4) em `processo_seletivo/portal/views.py`
- [x] T009 [P] [US1] Ajustar os testes da apresentação e do envio em duas partes ao texto novo, e acrescentar a varredura de vocabulário e de dado pessoal da mensagem em `tests/unit/test_apresentacao_dos_emails.py` e `tests/integration/test_envios_em_duas_partes.py`
- [x] T010 [US1] Testar a jornada: envio pelo portal manda uma mensagem com o link ao comprovante; envio recusado não manda; o link sem sessão leva ao acesso e volta; identificador inventado recebe o mesmo redirecionamento em `tests/integration/portal/test_confirmacao_de_inscricao.py`

**Checkpoint**: a mensagem nova sai uma vez, e o link funciona com e sem sessão.

## Phase 4: User Story 2 — a tela diz se a mensagem saiu (P1)

**Goal**: o comprovante diz o que aconteceu e deixa a titular tentar de novo.

**Independent Test**: envio com o correio aceitando → "Enviamos a confirmação…"; com o correio
recusando → aviso e botão; o botão envia e a tela muda.

- [x] T011 [US2] Ler `confirmacao.ultima` no comprovante e criar a view `confirmar_de_novo` (POST, titular, enviada) em `processo_seletivo/portal/views.py`
- [x] T012 [US2] Registrar `portal:comprovante-confirmacao` em `processo_seletivo/portal/urls.py`
- [x] T013 [US2] Mostrar "✓ Inscrição enviada" e o aviso da confirmação, `nao-imprime`, com classes que já têm regra em `portal.css` (FR-8362, FR-8365, FR-8366, UX-1022) em `processo_seletivo/portal/templates/portal/comprovante.html`
- [x] T014 [US2] Testar a tela e a nova tentativa: aviso de enviada; aviso de falha com botão; a nova tentativa envia e registra a 2; aba antiga não envia; alheio, sem sessão e rascunho respondem 404 e nada sai; sem tentativa a tela não diz nada; o PDF não muda (FR-8362–FR-8366) em `tests/integration/portal/test_confirmacao_de_inscricao.py`

**Checkpoint**: falha visível e tratável pela própria pessoa.

## Phase 5: User Story 3 — o sistema responde se saiu (P2)

**Goal**: a trilha responde quantas tentativas, quando e com que resultado.

- [x] T015 [US3] Testar a leitura da trilha depois de uma falha e de uma nova tentativa, e o log com o identificador da inscrição e sem endereço (FR-8358, FR-8361, SC-2925) em `tests/integration/inscricoes/test_confirmacao_por_email.py`

## Phase 6: Polish

- [x] T016 Rodar os guardiões que a mudança toca: `tests/test_situacoes_de_mensagem.py`, `tests/test_citacoes_de_requisito.py`, as varreduras de vocabulário, de CSP e de classes, e o inventário de negativas da `033`
- [x] T017 Escrever a matriz `specs/181-confirmacao-da-inscricao-por-email/rastreabilidade.md`, com cada FR, SC, UX e caso-limite
- [x] T018 Atualizar a docstring de `processo_seletivo/inscricoes/application/mensagem.py`, a linha da `181` na tabela de incrementos do `README.md`, o rótulo `CONFIRMAR_POR_EMAIL` da trilha legível em `processo_seletivo/interface/views.py`, e o caso sem sessão de `tests/authorization/test_idor_area.py`. **A nota das Novidades do GPS fica para depois do merge**: `novidades.toml` só aceita nota de PR que já está na `main`
- [x] T019 `make lint check`, a suíte inteira contra PostgreSQL, e as capturas da mensagem e do comprovante pelo quickstart

## Phase 7: Revisão de código de 18/11

- [x] T020 Conter toda falha de `confirmar` no registro técnico, sem 500 depois da inscrição gravada (FR-8352) em `processo_seletivo/inscricoes/application/confirmacao.py`
- [x] T021 Trava sem espera e intervalo de um minuto entre tentativas, com a frase na tela (FR-8363) em `processo_seletivo/inscricoes/application/confirmacao.py`, `processo_seletivo/portal/views.py` e `processo_seletivo/portal/templates/portal/comprovante.html`
- [x] T022 Tirar "Por enquanto, você não precisa fazer nada" da mensagem (FR-8355) nos dois modelos de `processo_seletivo/inscricoes/templates/inscricoes/mensagem/`
- [x] T023 Não tentar a confirmação de inscrição sem endereço em `processo_seletivo/inscricoes/application/confirmacao.py`
- [x] T024 [P] Mover a trava consultiva para `processo_seletivo/shared/concurrency.py` (`travar_consultivamente`), usada também por `inscricoes/application/submissao.py`
- [x] T025 [P] Extrair `_ao_acesso_sem_sessao` em `processo_seletivo/portal/views.py`, usado pela convocação e pelo comprovante
- [x] T026 [P] Usar o servidor de correio simulado de `tests/fixtures/correio.py` nos dois arquivos de teste, no lugar de classes definidas num deles
- [x] T027 Testar o duplo clique na revisão de ponta a ponta, a trava ocupada, o intervalo, a inscrição sem endereço e a contenção em `tests/integration/inscricoes/test_confirmacao_por_email.py` e `tests/integration/portal/test_confirmacao_de_inscricao.py`

## Dependencies & Execution Order

- T001 → T002 → T003. US1 e US2 dependem de T002.
- US1: T004, T005 e T009 em paralelo; T006 → T007; T008 independente; T010 por último.
- US2 depende de T007 (é a mesma view que grava a primeira tentativa).
- US3 depende só de T002.
- Polish por último.

## Implementation Strategy

MVP = Phase 2 + US1: a mensagem certa, uma vez, com rastro. US2 torna a falha visível e tratável, e é
a que fecha o pedido do usuário; US3 é prova de leitura, sem código novo.
