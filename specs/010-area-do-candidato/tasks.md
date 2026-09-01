---

description: "Task list for feature implementation"
---

# Tasks: Área do Candidato e Acesso sem Senha

**Input**: Design documents from `/specs/010-area-do-candidato/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/acesso.md](./contracts/acesso.md), [contracts/area.md](./contracts/area.md), [quickstart.md](./quickstart.md)

**Tests**: **sim, exigidos**. O princípio V da Constituição exige cobertura de regra crítica e nomeia
autorização e concorrência — que é metade desta feature. Além disso, a spec faz da demonstração de
segurança do §25 **condição de conclusão**, e seus seis casos viram teste. Os testes vêm antes da
implementação em cada fase.

**Organization**: por história de usuário, na ordem das seis entregas da spec. Cada fase termina em
comportamento observável no navegador do candidato (princípio VI).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo — arquivos diferentes, sem dependência de tarefa incompleta
- **[Story]**: US1 a US6, conforme a spec
- **Sufixo de letra** (`T011a`): tarefa acrescentada por revisão, inserida na posição de execução a
  que pertence. Mantém estáveis os identificadores já referenciados

## Path Conventions

Aplicação web Django. Produção em `backend/processo_seletivo/`, testes em `backend/tests/`. O app
novo é `identidade`; o `portal` é o canal e ganha as telas; `inscricoes` recebe duas alterações
localizadas.

---

## Phase 1: Setup (Shared Infrastructure)

- [X] T001 Criar o app `identidade` com `apps.py`, `__init__.py`, `domain/`, `application/` e `migrations/` em `backend/processo_seletivo/identidade/`
- [X] T002 Registrar `processo_seletivo.identidade` em `INSTALLED_APPS`, com o comentário que explica a separação domínio/canal, em `backend/config/settings/base.py`
- [X] T003 [P] Declarar mecanismo de envio e remetente por ambiente (`DJANGO_EMAIL_BACKEND`, `DEFAULT_FROM_EMAIL`) em `backend/config/settings/base.py`
- [X] T004 [P] Criar os diretórios de teste com `__init__.py`: `backend/tests/unit/identidade/`, `backend/tests/integration/identidade/`, `backend/tests/acceptance/portal/` e `backend/tests/migrations/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**⚠️ Bloqueia todas as histórias.** Sem os modelos, as primitivas e a reconciliação, nenhuma fase
seguinte tem onde apoiar.

### Testes da fundação

- [X] T005 [P] Teste da forma canônica do endereço — caixa baixa no endereço inteiro, sem remover pontos nem cortar sufixo, endereço informado preservado — em `backend/tests/unit/identidade/test_enderecos.py`
- [X] T006 [P] Teste da geração e do resumo do código — seis dígitos, distribuição sobre todo o intervalo, resumo não recuperável — em `backend/tests/unit/identidade/test_codigo.py`
- [X] T007 [P] Teste dos invariantes dos modelos — endereço canônico único por restrição de banco, e identidade **que tenha credencial** com exatamente um principal — em `backend/tests/integration/identidade/test_modelos.py`
- [X] T007a [P] Teste de que uma identidade **sem credencial alguma** é estado válido, porque é o que a reconciliação produz, em `backend/tests/integration/identidade/test_modelos.py`
- [X] T008 [P] Teste de que o `subject` de identidade nova é opaco, prefixado e independente de `SECRET_KEY` em `backend/tests/unit/identidade/test_subject.py`
- [X] T009 [P] Teste da reconciliação: preserva o `subject`, não reescreve `identity_subject`, não marca endereço como verificado, traz o nome da inscrição mais recente — em `backend/tests/migrations/test_reconciliacao.py`
- [X] T010 [P] Teste de que a reconciliação **interrompe** com inscrição enviada sem CPF utilizável, e **relata sem interromper** tanto o grupo de CPF com mais de um `subject` quanto o rascunho sem CPF utilizável — que fica intacto e não reconciliado —, sem CPF em log, em `backend/tests/migrations/test_reconciliacao_recusas.py`
- [X] T011 [P] Teste de que produção recusa iniciar com mecanismo de envio que não entrega e sem remetente, acrescentado a `backend/tests/test_configuracao_producao.py`
- [X] T011a [P] Teste de que o **banco** recusa gravar inscrição enviada cujo `cpf_normalizado` não tenha exatamente onze dígitos, e aceita rascunho na mesma condição, em `backend/tests/integration/inscricoes/test_cpf_na_submetida.py`

### Implementação da fundação

- [X] T012 [P] Implementar a forma canônica do endereço em `backend/processo_seletivo/identidade/domain/enderecos.py`
- [X] T013 [P] Implementar geração, resumo e verificação do código em `backend/processo_seletivo/identidade/domain/codigo.py`
- [X] T014 Implementar `CandidateIdentity`, `CandidateEmail` e `DesafioDeAcesso` com **todos os campos e todas as restrições** do [data-model.md](./data-model.md) — incluindo `tentativas_cpf` e `reconciliacao_ate`, que a US2 usa e não cria — em `backend/processo_seletivo/identidade/models.py`
- [X] T015 Criar a migração das três tabelas em `backend/processo_seletivo/identidade/migrations/0001_identidade.py`
- [X] T016 Criar a migração de dados que verifica, reconcilia, interrompe e relata em `backend/processo_seletivo/identidade/migrations/0002_reconciliacao.py`
- [X] T017 Criar a restrição de CPF com onze dígitos em inscrição enviada, declarando dependência de `identidade.0002`, em `backend/processo_seletivo/inscricoes/migrations/0003_cpf_na_submetida.py`
- [X] T018 Acrescentar a recusa de inicialização para mecanismo de envio conhecido por não entregar e para remetente ausente em `backend/config/settings/production.py`

**Checkpoint**: `make check` passa, a suíte da fundação passa contra PostgreSQL, e `migrate` reconcilia
uma base com dados da `009` sem alterar nenhum `identity_subject`.

---

## Phase 3: User Story 1 - Entrar sem senha (Priority: P1) 🎯 MVP

**Entrega 1 da spec.** Informar endereço, informar código, chegar à área — inclusive vazia.

**Independent Test**: informar um endereço sem participação anterior, receber o código no terminal do
servidor, colá-lo inteiro e chegar a uma área pessoal vazia, sem que CPF seja pedido em momento algum.

### Testes da US1

- [X] T019 [P] [US1] Teste de contrato de `GET|POST /acesso` e `GET|POST /acesso/codigo`, conforme `contracts/acesso.md`, em `backend/tests/contract/portal/test_acesso.py`
- [X] T020 [P] [US1] Teste de que a resposta, o código de estado, o texto e a janela de reenvio são idênticos nos quatro casos que poderiam revelar existência — endereço com identidade, sem identidade, limite esgotado e **falha de envio** — em `backend/tests/integration/identidade/test_equivalencia.py`
- [X] T021 [P] [US1] Teste de que duas requisições simultâneas com o mesmo código produzem **um** consumo em `backend/tests/integration/identidade/test_consumo_atomico.py`
- [X] T022 [P] [US1] Teste do ciclo do desafio — expiração por instante absoluto, uso único, novo código invalidando anteriores, teto de cinco tentativas — em `backend/tests/integration/identidade/test_desafio.py`
- [X] T022a [P] [US1] Teste de finalidade cruzada: um código pedido para **entrar** não confirma adição de credencial, e um pedido para **adicionar** não autentica — em `backend/tests/integration/identidade/test_finalidade.py`
- [X] T023 [P] [US1] Teste dos limites por endereço e por origem, com origem guardada como resumo e nunca em claro, em `backend/tests/integration/identidade/test_limites.py`
- [X] T024 [P] [US1] Teste de que o identificador de sessão após a autenticação difere do anterior em `backend/tests/authorization/test_rotacao_de_sessao.py`
- [X] T025 [P] [US1] Teste de que a sessão de candidato não concede nenhuma ação institucional em `backend/tests/authorization/test_sessao_candidata.py`
- [X] T025a [P] [US1] Teste do conteúdo da mensagem — código, prazo de validade e orientação de ignorar; **sem** link que autentica, sem CPF e sem dado de inscrição — em `backend/tests/integration/identidade/test_mensagem.py`
- [X] T026 [P] [US1] Teste de aceitação do percurso endereço → código → área vazia, sem pedir CPF, em `backend/tests/acceptance/portal/test_entrar_sem_senha.py`

### Implementação da US1

- [X] T027 [US1] Implementar solicitação de desafio, com invalidação dos anteriores e limites, em `backend/processo_seletivo/identidade/application/desafio.py`
- [X] T028 [US1] Implementar validação do código com consumo atômico e contagem condicional de tentativas em `backend/processo_seletivo/identidade/application/desafio.py`
- [X] T029 [US1] Implementar o envio da mensagem — código, prazo e orientação, sem link que autentica, sem CPF, sem dado de inscrição — em `backend/processo_seletivo/identidade/application/mensagem.py`
- [X] T030 [US1] Implementar a criação de identidade sem CPF para endereço sem correspondência anterior em `backend/processo_seletivo/identidade/application/associacao.py`
- [X] T031 [US1] Reescrever `portal/identidade.py` para guardar na sessão apenas o identificador da identidade e montar `IdentidadeDoCandidato` a partir do registro, com rotação de sessão na autenticação, em `backend/processo_seletivo/portal/identidade.py`
- [X] T032 [US1] Acrescentar as rotas de acesso e de saída em `backend/processo_seletivo/portal/urls.py`
- [X] T033 [US1] Implementar as views de acesso em `backend/processo_seletivo/portal/views.py`
- [X] T034 [P] [US1] Criar o formulário de endereço em `backend/processo_seletivo/portal/templates/portal/acesso_email.html`
- [X] T035 [P] [US1] Criar o formulário do código — campo único que aceita colagem integral, endereço preservado em caso de erro, e ação de reenviar que informa quando a próxima tentativa é possível — em `backend/processo_seletivo/portal/templates/portal/acesso_codigo.html`
- [X] T036 [US1] Criar a área pessoal com o estado vazio — convite a consultar processos seletivos, sem aparência de erro — em `backend/processo_seletivo/portal/templates/portal/inscricoes.html`

**Checkpoint**: o percurso da Entrega 1 do [quickstart.md](./quickstart.md) roda no navegador.

> **Antecipadas para cá, e o motivo.** `T046`, `T048`, `T051` e `T052` — a busca de correspondência
> histórica, a confirmação por CPF e a tela do convite — foram implementadas junto com a US1. Sem
> elas, um endereço com participação anterior cairia na criação de identidade nova e **consumiria**
> a correspondência, tornando a reconciliação da US2 impossível para aquela pessoa. A US1 não é
> correta sem esse desvio; ela é apenas demonstrável. O que permanece na US2 é a retomada
> (`T042`, `T049`) e o bloqueio compartilhado (`T050`), que dependem de haver inscrição para
> proteger.

---

## Phase 4: User Story 2 - Reencontrar a participação anterior (Priority: P1)

**Entrega 2 da spec.** O convite recusável, a confirmação por CPF e a retomada limitada.

**Independent Test**: com uma inscrição criada antes da migração, provar o endereço usado nela,
confirmar o CPF e ver a inscrição — sem que nenhum dado dela tenha mudado.

### Testes da US2

- [ ] T037 [P] [US2] Teste de contrato de `GET|POST /acesso/reconciliar` e `POST /acesso/reconciliar/retomar` em `backend/tests/contract/portal/test_reconciliacao.py`
- [ ] T038 [P] [US2] Teste de que o convite aparece só com correspondência anterior, e de que o CPF desempata entre identidades distintas, em `backend/tests/integration/identidade/test_correspondencia.py`
- [ ] T039 [P] [US2] Teste de que recusa, CPF errado e tentativas esgotadas produzem identidade própria com sessão válida — nunca beco sem saída — e de que quem **já tem** identidade e prova endereço novo sem correspondência recebe outra identidade, jamais uma fusão, em `backend/tests/integration/identidade/test_sem_beco.py`
- [ ] T040 [P] [US2] Teste de que as tentativas de CPF são cinco, contadas no desafio, não zeradas por nova sessão, e de que tentativas de terceiro **não** impedem o titular legítimo de reconciliar depois, em `backend/tests/integration/identidade/test_tentativas_cpf.py`
- [ ] T041 [P] [US2] Teste de que a reconciliação pendente expira dez minutos após o consumo e leva a identidade própria em `backend/tests/integration/identidade/test_reconciliacao_expira.py`
- [ ] T042 [P] [US2] Teste da retomada — disponível enquanto a identidade estiver vazia, indisponível depois de qualquer inscrição, movendo **todas** as credenciais e descartando a identidade vazia — em `backend/tests/integration/identidade/test_retomada.py`
- [ ] T043 [P] [US2] Teste de concorrência entre a retomada e a abertura de rascunho: ou a movimentação acontece inteira, ou não acontece; nunca credencial para trás nem inscrição órfã, em `backend/tests/integration/identidade/test_retomada_concorrente.py`
- [ ] T044 [P] [US2] Teste de que nenhuma inscrição muda de `identity_subject` em qualquer desfecho da reconciliação em `backend/tests/authorization/test_titularidade_preservada.py`
- [ ] T045 [P] [US2] Teste de aceitação do percurso da Entrega 2, incluindo recusar o convite e retomá-lo, em `backend/tests/acceptance/portal/test_reencontrar_participacao.py`

### Implementação da US2

- [X] T046 [US2] Implementar a busca de correspondência histórica por endereço, sem consumir o convite, em `backend/processo_seletivo/identidade/application/associacao.py`
- [ ] T047 [US2] Implementar o porte da reconciliação pendente sobre os campos que `T014` já criou — abrir o prazo no consumo, contar as tentativas de CPF por atualização condicional e encerrar nos quatro desfechos — em `backend/processo_seletivo/identidade/application/associacao.py`
- [X] T048 [US2] Implementar a confirmação por CPF, com desempate e contagem condicional de tentativas, em `backend/processo_seletivo/identidade/application/associacao.py`
- [ ] T049 [US2] Implementar a retomada — verificar vazia, mover todas as credenciais e descartar, em uma operação única sob bloqueio de linha — em `backend/processo_seletivo/identidade/application/associacao.py`
- [ ] T050 [US2] Fazer a abertura de rascunho tomar o mesmo bloqueio de linha sobre a identidade antes de criar a Inscrição em `backend/processo_seletivo/inscricoes/application/rascunho.py`
- [X] T051 [US2] Implementar as views do convite e da retomada em `backend/processo_seletivo/portal/views.py` e as rotas em `backend/processo_seletivo/portal/urls.py`
- [X] T052 [US2] Criar o convite, sem revelar nome, CPF, protocolo ou quantidade da identidade anterior, e a recusa que aponta o procedimento institucional de recuperação em vez de um beco, em `backend/processo_seletivo/portal/templates/portal/acesso_reconciliar.html`

**Checkpoint**: o percurso da Entrega 2 roda, e a suíte prova que nenhuma inscrição mudou de titular.

---

## Phase 5: User Story 3 - Minhas inscrições e continuar de onde parou (Priority: P1)

**Entrega 3 da spec.** O núcleo mínimo da identidade, a lista e a retomada do rascunho. **É aqui que
a identificação por declaração da `009` é aposentada** — antes disso ela ainda é o único caminho para
criar rascunho com nome e CPF.

**Independent Test**: entrar, ver a lista ordenada, acionar `Continuar inscrição` e cair na jornada
existente com o rascunho como estava.

### Testes da US3

- [ ] T053 [P] [US3] Teste de que a lista mostra todas e somente as inscrições da identidade, mais recente primeiro, com a ação principal correta em `backend/tests/integration/portal/test_minhas_inscricoes.py`
- [ ] T054 [P] [US3] Teste de que nome e CPF são pedidos uma única vez e reusados nas inscrições seguintes, e nunca a quem veio da `009`, em `backend/tests/integration/identidade/test_nucleo_minimo.py`
- [ ] T055 [P] [US3] Teste de que o rascunho é alimentado pelo endereço **principal** da identidade, e não pelo endereço que autenticou a sessão, em `backend/tests/integration/identidade/test_email_do_rascunho.py`
- [ ] T056 [P] [US3] Teste de que uma identidade não enxerga inscrição de outra, com resposta que não permite descobrir existência, em `backend/tests/authorization/test_inscricao_alheia.py`
- [ ] T057 [P] [US3] Teste de que a restrição de uma inscrição por identidade, Edital e Perfil continua intacta em `backend/tests/integration/inscricoes/test_idempotencia_preservada.py`
- [ ] T058 [P] [US3] Teste de aceitação do percurso da Entrega 3 — pedir nome e CPF uma vez, não pedir de novo, retomar o rascunho — em `backend/tests/acceptance/portal/test_minhas_inscricoes.py`

### Implementação da US3

- [ ] T059 [US3] Implementar a captura única de nome e CPF, com validação de formação, em `backend/processo_seletivo/identidade/application/credenciais.py`
- [ ] T060 [US3] Fazer a abertura de rascunho consumir nome, CPF e endereço principal a partir do registro da identidade em `backend/processo_seletivo/inscricoes/application/rascunho.py`
- [ ] T061 [US3] Implementar a listagem das inscrições da identidade em `backend/processo_seletivo/portal/views.py`
- [ ] T062 [US3] Completar a lista, com Edital, Perfil, situação, protocolo e ação principal, em `backend/processo_seletivo/portal/templates/portal/inscricoes.html`
- [ ] T063 [US3] Migrar as fixtures e os testes existentes da `009` que criavam candidato pela identificação declarada para o acesso por desafio em `backend/tests/`
- [ ] T064 [US3] Remover a rota, a view e o template da identificação por declaração, e a derivação do `subject` a partir do CPF, em `backend/processo_seletivo/portal/urls.py`, `backend/processo_seletivo/portal/views.py`, `backend/processo_seletivo/portal/identidade.py` e `backend/processo_seletivo/portal/templates/portal/identificar.html`
- [ ] T065 [US3] Manter a variável e a recusa de inicialização como armadilha, com o comentário que explica por que ela sobrevive ao caminho que ela guardava, em `backend/config/settings/production.py`

**Checkpoint**: a jornada de inscrição da `009` funciona inteira sem a identificação por declaração.

---

## Phase 6: User Story 4 - Conferir exatamente o que foi submetido (Priority: P1)

**Entrega 4 da spec.** Dados, documentos e comprovante numa tela.

**Independent Test**: abrir uma inscrição enviada e ver protocolo, instante, versão aceita, dados e os
documentos, com visualizar, baixar e comprovante funcionando.

### Testes da US4

- [ ] T066 [P] [US4] Teste de contrato da página da inscrição enviada, conforme `contracts/area.md`, em `backend/tests/contract/portal/test_inscricao_enviada.py`
- [ ] T067 [P] [US4] Teste de que o arquivo entregue é o documento vigente daquela inscrição e de que visualizar ou baixar não a altera em `backend/tests/integration/portal/test_documentos_do_titular.py`
- [ ] T068 [P] [US4] Teste anti-IDOR de inscrição e de documento de outro candidato, com resposta que não enumera, em `backend/tests/authorization/test_idor_area.py`
- [ ] T069 [P] [US4] Teste de que comprovante e evidências de integridade permanecem disponíveis e inalterados em `backend/tests/integration/portal/test_comprovante_preservado.py`
- [ ] T070 [P] [US4] Teste de aceitação do percurso da Entrega 4 em `backend/tests/acceptance/portal/test_conferir_inscricao.py`

### Implementação da US4

- [ ] T071 [US4] Montar os dados de conferência — oportunidade, envio, dados informados e documentos submetidos — em `backend/processo_seletivo/portal/views.py`
- [ ] T072 [US4] Apresentar a inscrição enviada, com os documentos e a ação de integridade recolhida, em `backend/processo_seletivo/portal/templates/portal/inscricao.html`
- [ ] T073 [P] [US4] Criar o bloco de documentos submetidos, com nome de arquivo, tamanho, instante, visualizar e baixar, em `backend/processo_seletivo/portal/templates/portal/_documentos_submetidos.html`

**Checkpoint**: o percurso da Entrega 4 roda, e nada da `009` mudou de comportamento.

---

## Phase 7: User Story 5 - Acompanhar a participação e o certame (Priority: P2)

**Entrega 5 da spec.** Dois blocos que não se confundem.

**Independent Test**: abrir o acompanhamento de uma inscrição enviada e distinguir os fatos da
participação dos eventos do cronograma.

### Testes da US5

- [ ] T074 [P] [US5] Teste de que fato pessoal e evento de cronograma são distinguíveis e de que nenhuma afirmação pessoal decorre apenas de uma data alcançada em `backend/tests/integration/portal/test_acompanhamento.py`
- [ ] T075 [P] [US5] Teste de que o aviso de Edital atualizado aparece sem alterar a versão aceita e sem reabrir a inscrição em `backend/tests/integration/portal/test_aviso_de_versao.py`
- [ ] T076 [P] [US5] Teste de aceitação do percurso da Entrega 5, com retificação posterior ao envio, em `backend/tests/acceptance/portal/test_acompanhar.py`

### Implementação da US5

- [ ] T077 [US5] Derivar os fatos da participação e o cronograma da versão consolidada vigente em `backend/processo_seletivo/portal/views.py`
- [ ] T078 [US5] Acrescentar a rota do acompanhamento em `backend/processo_seletivo/portal/urls.py`
- [ ] T079 [US5] Criar a página com os dois blocos visualmente distintos e o aviso de versão em `backend/processo_seletivo/portal/templates/portal/acompanhamento.html`

**Checkpoint**: o percurso da Entrega 5 roda.

---

## Phase 8: User Story 6 - Cuidar das próprias credenciais (Priority: P2)

**Entrega 6 da spec.** Adicionar, escolher a principal, remover e corrigir.

**Independent Test**: autenticado, adicionar um endereço provando-o, torná-lo principal, remover o
antigo, e receber recusa ao tentar remover o último.

### Testes da US6

- [ ] T080 [P] [US6] Teste de contrato das rotas de conta, conforme `contracts/area.md`, em `backend/tests/contract/portal/test_conta.py`
- [ ] T081 [P] [US6] Teste de que adicionar exige desafio e não pede CPF, e de que endereço de outra identidade é recusado sem revelar a quem pertence, em `backend/tests/integration/identidade/test_adicionar_credencial.py`
- [ ] T082 [P] [US6] Teste de que duas confirmações simultâneas do mesmo endereço produzem uma única credencial, recusada pelo banco e não por consulta prévia, em `backend/tests/integration/identidade/test_credencial_concorrente.py`
- [ ] T083 [P] [US6] Teste de que trocar o principal alcança os rascunhos abertos e nunca uma enviada, e de que remover não altera inscrição alguma, em `backend/tests/integration/identidade/test_principal_e_remocao.py`
- [ ] T084 [P] [US6] Teste de que a última credencial não pode ser removida e de que uma identidade **que tenha credencial** nunca fica sem principal em `backend/tests/integration/identidade/test_ultima_credencial.py`
- [ ] T084a [P] [US6] Teste de que corrigir nome alcança os rascunhos abertos e não altera nenhuma inscrição enviada, e de que o CPF congela na primeira enviada, em `backend/tests/integration/identidade/test_correcao.py`
- [ ] T085 [P] [US6] Teste de que associação e remoção de credencial entram na trilha existente com escopo vazio, e de que código inválido **não** vira evento de negócio, em `backend/tests/integration/identidade/test_auditoria_de_credencial.py`
- [ ] T086 [P] [US6] Teste de aceitação do percurso da Entrega 6, incluindo a correção de nome refletida no rascunho, em `backend/tests/acceptance/portal/test_credenciais.py`

### Implementação da US6

- [ ] T087 [US6] Implementar adicionar, escolher principal, remover credencial **e corrigir nome e CPF** — nome sempre, CPF enquanto não houver inscrição enviada — em `backend/processo_seletivo/identidade/application/credenciais.py`
- [ ] T088 [US6] Registrar associação e remoção de credencial na trilha existente, com o comentário que explica o escopo vazio e a consequência para a consulta por escopo, em `backend/processo_seletivo/identidade/application/credenciais.py`
- [ ] T089 [US6] Implementar as views de conta e as rotas em `backend/processo_seletivo/portal/views.py` e `backend/processo_seletivo/portal/urls.py`
- [ ] T090 [US6] Criar a página de acesso à conta, com credenciais, principal e correção de nome e CPF, em `backend/processo_seletivo/portal/templates/portal/conta.html`

**Checkpoint**: o percurso da Entrega 6 roda.

---

## Phase 9: Polish & Cross-Cutting Concerns

- [ ] T091 [P] Consolidar a demonstração de segurança do §25 em seis casos executáveis — endereçamento direto, endereço arbitrário com CPF conhecido, precedência, endereço reciclado, engano no convite e sessão conhecida — em `backend/tests/authorization/test_demonstracao_de_seguranca.py`
- [ ] T092 [P] Teste de que duas inscrições enviadas com o mesmo CPF no mesmo Perfil são aceitas e aparecem **assinaladas**, e de que nenhuma é recusada no envio, em `backend/tests/integration/inscricoes/test_cpf_coincidente.py`
- [ ] T093 Marcar a coincidência de CPF por subconsulta de existência na consulta administrativa em `backend/processo_seletivo/inscricoes/application/consulta.py`
- [X] T094 [P] Implementar a limpeza operacional de desafios terminais em `backend/processo_seletivo/identidade/application/desafio.py`
- [ ] T095 [P] Teste de higiene de registro técnico — nem código, nem CPF completo, nem conteúdo de documento em log ou auditoria — em `backend/tests/integration/identidade/test_higiene_de_log.py`
- [ ] T096 [P] Verificar 375 px sem rolagem horizontal e percurso completo por teclado nas telas novas em `backend/tests/interface/test_acessibilidade_portal.py`
- [ ] T097 [P] Teste de custo de consulta da lista de inscrições e da área, marcado como `performance`, em `backend/tests/performance/test_area_do_candidato.py`
- [ ] T098 Escrever a matriz de rastreabilidade de `FR` e `SC` até os testes em `specs/010-area-do-candidato/rastreabilidade.md`
- [ ] T099 Percorrer o [quickstart.md](./quickstart.md) de ponta a ponta no navegador e registrar o que a demonstração mudou em `specs/010-area-do-candidato/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 1 (Setup)
     ↓
Phase 2 (Foundational)  ← bloqueia tudo
     ↓
Phase 3 (US1)  ← MVP: e-mail → código → área
     ↓
Phase 4 (US2)  ← depende da US1: reconciliar exige ter provado o endereço
     ↓
Phase 5 (US3)  ← depende da US1; aposenta a identificação declarada
     ↓
Phase 6 (US4) ──┐
Phase 7 (US5) ──┤ dependem da US3 (a lista é o caminho até elas)
Phase 8 (US6) ──┘ depende apenas da US1
     ↓
Phase 9 (Polish)
```

### User Story Dependencies

- **US1** não depende de nenhuma outra. É o MVP.
- **US2** depende da US1 (o convite só existe depois de um código válido) e da migração da fase 2.
- **US3** depende da US1. **T064 não pode preceder T063**: remover a identificação declarada antes de
  migrar as fixtures deixaria a suíte da `009` sem caminho para criar candidato.
- **US4** e **US5** dependem da US3 pela navegação, e da `009` pelos dados.
- **US6** depende apenas da US1, e pode ser feita em paralelo com US4 e US5.

### Within Each User Story

Testes antes da implementação. Modelos antes de serviços, serviços antes de views, views antes de
templates. Dentro de cada bloco, o que está marcado `[P]` toca arquivos diferentes.

### Parallel Opportunities

- Fase 2: T005 a T011a são nove testes em oito arquivos.
- Fase 3: T019 a T026 em paralelo, incluindo T022a e T025a; depois T034 e T035, que são templates distintos.
- Fase 4: T037 a T045 em paralelo.
- Fases 6, 7 e 8 podem correr em três frentes depois da fase 5.
- Fase 9: quase tudo é paralelo, exceto T093 — que depende do seu teste, T092 — e T098 e T099, que
  fecham.

---

## Parallel Example: User Story 1

```bash
# Os oito testes da US1, em oito arquivos distintos:
T019  tests/contract/portal/test_acesso.py
T020  tests/integration/identidade/test_equivalencia.py
T021  tests/integration/identidade/test_consumo_atomico.py
T022  tests/integration/identidade/test_desafio.py
T022a tests/integration/identidade/test_finalidade.py
T023  tests/integration/identidade/test_limites.py
T024  tests/authorization/test_rotacao_de_sessao.py
T025  tests/authorization/test_sessao_candidata.py
T026  tests/acceptance/portal/test_entrar_sem_senha.py
```

---

## Implementation Strategy

### MVP First (User Story 1)

Fases 1 a 3 entregam o que a spec chama de Entrega 1: informar endereço, informar código, chegar à
área — inclusive vazia. Já é observável no navegador, já remove o impedimento técnico de produção, e
já vale sozinha para quem nunca se inscreveu.

### Incremental Delivery

Cada fase seguinte é uma entrega da spec e termina em percurso navegável. A ordem 3 → 4 → 5 → 6 → 7 →
8 é a da spec, e a única inversão possível sem custo é adiantar a fase 8 (US6), que depende só da US1.

### Parallel Team Strategy

Depois da fase 5, três frentes: conferência (US4), acompanhamento (US5) e credenciais (US6). Elas
tocam views e templates distintos; o único ponto de encontro é `portal/urls.py`, e a colisão ali é
trivial de resolver.

---

## Notes

- **Nenhuma dependência nova.** `backend/pyproject.toml` não muda.
- **A suíte precisa de PostgreSQL.** Sem `TEST_DB_ENGINE=postgresql` as restrições que esta feature
  instala não são exercidas, e o sinal é a contagem de *skips* — ver [quickstart.md](./quickstart.md).
- **T016 pode parar a implantação, e é o comportamento correto** (`FR-046`). A tarefa inclui a
  mensagem que enumera o que precisa de tratamento.
- **T064 apaga um caminho de autenticação.** É a tarefa de maior risco da lista, e é por isso que
  T063 vem antes dela.
- **O código de acesso não vai para lugar nenhum além do e-mail**: nem log, nem auditoria, nem
  mensagem de erro, nem endereço de página.
