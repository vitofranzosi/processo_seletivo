---

description: "Task list for feature implementation"
---

# Tasks: Requerimento de Matrícula — o que a vaga exige, perguntado uma vez

**Input**: Design documents from `specs/029-requerimento-de-matricula/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md),
[contracts/requerimento-de-matricula.md](./contracts/requerimento-de-matricula.md)

**Tests**: **obrigatórios**, e não opcionais. O Princípio V exige teste no nível certo; a §20 da spec
fecha a feature em dezoito critérios verificáveis, e três deles — `SC-127`, `SC-130` e `SC-137` — são
literalmente testes. Nenhuma feature anterior abriu exceção; esta não abre.

**Organization**: por user story, para que cada uma seja demonstrável sozinha.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode correr em paralelo — arquivos distintos, sem dependência pendente
- **[Story]**: a que user story a tarefa pertence (`US1` a `US5`)
- Caminho de arquivo exato em toda tarefa

## Path Conventions

Monólito Django. Código em `backend/processo_seletivo/`, testes em `backend/tests/`.

**O que esta feature acrescenta**: um app (`requerimentos/`), duas tabelas, dois campos em
`processos.Edital`, um gatilho condicional e cinco restrições. **O que ela não acrescenta**: nenhuma
dependência, nenhuma permissão, nenhuma etapa no assistente, nenhum estado de análise
([plan.md](./plan.md), Technical Context).

**Banco próprio nesta worktree**: `DB_NAME=ps_demo_029`, e **como variável do Make** —
`make DB_NAME=ps_demo_029 …`, nunca `DB_NAME=ps_demo_029 make …`. O `Makefile` faz `include .env`
seguido de `export`, e `include` **sobrepõe** variável de ambiente: o prefixo é engolido pelo
`DB_NAME` do `.env`, e a suíte desta worktree derruba a de outra sem avisar.

**O gatilho da `FR-396` é PostgreSQL puro.** No modo padrão da suíte — sem `TEST_DB_ENGINE=postgresql`
**e** a role certa — ele não é exercido, e os testes que o provam passam sem provar nada. É
`make test-pg`, sempre, e a armadilha está no `AGENTS.md`.

**`TABELAS_APPEND_ONLY` não muda.** Se alguma tarefa abaixo levar você a acrescentar a tabela do
requerimento àquela tupla, a tarefa foi mal lida: a imutabilidade aqui é **condicional ao estado**, e
privilégio de tabela não sabe ler estado ([research.md](./research.md), `T-005`). O provisionamento
deve continuar dizendo `31 de 31`.

---

## Phase 1: Setup

**Purpose**: ter o verde de partida medido antes de mexer no que vai mudá-lo.

- [X] T001 Preparar o banco desta worktree com `cd backend && LC_ALL=pt_BR.UTF-8 make DB_NAME=ps_demo_029 POSTGRES_USER="$USER" preparar` e confirmar `migrate --check` limpo. *`preparar` são três passos nesta ordem — provisionar, migrar, provisionar de novo; se a segunda passada disser `0 de N`, ela não rodou. Migration desaplicada contamina a sessão inteira, com sintoma longe da causa. Worktree nova precisa de `uv sync --extra dev` antes, ou `make test-pg` falha com "Failed to spawn: pytest". No macOS com PostgreSQL do Homebrew, `LC_ALL` não é enfeite*
- [X] T002 Rodar `make DB_NAME=ps_demo_029 lint check test-pg` em `backend/` e **gravar a contagem de partida** (passaram, pularam) num arquivo fora do repositório. *A `T-001` prevê que três guardiões do conteúdo publicado falhem por omissão assim que o campo novo for emitido. Sem a contagem de antes, não há como distinguir a queda esperada da regressão. `lint` são **dois** passos — `ruff check` e `ruff format --check`; rodar só o primeiro declara verde local e quebra no CI*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: existir a entidade, o gatilho de banco, o vocabulário e a declaração do Edital no
conteúdo publicado. **Nenhuma user story começa antes desta fase.**

- [X] T003 [P] Criar o app em `backend/processo_seletivo/requerimentos/` com `__init__.py`, `apps.py`, `domain/`, `application/`, `infrastructure/`, `migrations/` e registrá-lo em `INSTALLED_APPS`, em `backend/config/settings/base.py`. *`config/settings` é **pacote**, e não módulo: `backend/config/settings.py` não existe. A primeira redação desta tarefa mandava editar um arquivo inexistente* *A divisão domínio/aplicação/infraestrutura é a que todo módulo deste repositório pratica; um app achatado obrigaria a próxima feature a desmontá-lo*
- [X] T004 [P] Criar `backend/processo_seletivo/requerimentos/domain/nomes.py` com os dois estados (`RASCUNHO`, `ENVIADO`), as **cinco** categorias de cor/raça do IBGE mais *não declarada* — **seis** valores ao todo —, os estados civis, as **sete** faixas de renda e as **seis** recusas próprias de runtime do contrato §2.2 — `matriculation_request_not_required`, `matriculation_request_unavailable`, `matriculation_request_closed`, `matriculation_request_already_sent`, `successor_not_authorized` e `declaration_not_accepted`. *`field_required` e `field_constraint_violated` já existem no projeto e não se redeclaram; `matriculation_request_without_declaration` não é recusa de runtime, é achado de publicação (contrato §1.2) e nasce na T017 da conferência de conteúdo.* *Os códigos vivem num módulo só porque o mesmo código aparece na aplicação, na interface e no teste que o prende — escrevê-lo três vezes é como um deles fica para trás numa renomeação. **A lista de cor/raça inclui `INDIGENA`**, e a ausência dela no formato do Registro Acadêmico é achado a levar adiante, nunca categoria a suprimir aqui (`FR-383`, `R-4`). **As faixas de renda medem a soma da família**, e o rótulo tem de dizê-lo por extenso (`FR-412`)*
- [X] T005 Criar `backend/processo_seletivo/requerimentos/models.py` com `RequerimentoDeMatricula` e `ReferenciaDeCep`, campo a campo conforme [data-model.md](./data-model.md) §1.1 e §2. Texto ausente é `""`, nunca `null`. *Não existe campo de latitude, longitude, foto, tipo sanguíneo, valor de renda, número de filhos, profissão, condição de trabalhador, composição do domicílio nem telefone residencial: a ausência é requisito (`FR-382`, `FR-391`), e quem acrescentar um deles contraria a minimização que a feature declarou*
- [X] T006 Criar `backend/processo_seletivo/requerimentos/migrations/0001_initial.py` com as duas tabelas e as **cinco** restrições de [data-model.md](./data-model.md) §1.2. **Sem importar `processo_seletivo.*`**: estados e faixas entram congelados na migration, nunca por `from …domain import nomes`. *As duas de unicidade são **parciais** pela cirurgia que a `019` documentou: no PostgreSQL dois `NULL` não colidem, e uma restrição total deixaria passar duas raízes da mesma Inscrição*
- [X] T007 Criar `backend/processo_seletivo/requerimentos/migrations/0002_imutabilidade_do_enviado.py` com o gatilho `BEFORE UPDATE OR DELETE … FOR EACH ROW WHEN (OLD.status = 'ENVIADO')`, copiando a forma de `publicacoes/migrations/0007_imutabilidade_do_historico.py`. **Com `reverse_sql`** — `DROP TRIGGER` e `DROP FUNCTION` —, e **sem importar `processo_seletivo.*`**: o literal `'ENVIADO'` vai copiado. *`test_every_migration_declares_a_reverse_path` recusa operação irreversível — *"sem reversão não há rollback de deploy"* —, e `test_migrations_do_not_import_domain_or_application_code` recusa `from processo_seletivo…` dentro de migration, porque *"importar uma função do domínio faz uma alteração futura nela mudar retroativamente o efeito de uma migration já executada"*: a duplicação do literal é o preço de a história ser fixa. A função **apenas levanta exceção** e nunca retorna linha. A migration-fonte adverte que, numa trigger `BEFORE`, devolver `OLD` num `UPDATE` descartaria a alteração em silêncio — pior que não ter trigger; aqui o risco não existe, e o registro fica para quem editar depois (`T-005`)*
- [X] T008 Acrescentar a guarda de aplicação em `save()` e `delete()` de `RequerimentoDeMatricula`, em `backend/processo_seletivo/requerimentos/models.py`, recusando quando a linha **persistida** está em `ENVIADO`, no molde de `Inscricao.save` e `DocumentoSubmetido._recusar_se_enviada`. *É a primeira camada, **nunca a única** (`FR-396`). A guarda de `Inscricao` declara, no próprio comentário, não ser garantia de banco — foi esse o achado que trouxe o gatilho da T007*
- [X] T009 [P] Teste em `backend/tests/integration/requerimentos/test_imutabilidade.py`: `UPDATE` e `DELETE` diretos sobre linha `ENVIADO`, **com a role de runtime real**, recusados; e a mesma linha em `RASCUNHO` alterável. Molde: `backend/tests/unit/ocupacao/test_efeito_append_only.py`. *É a metade da `FR-396` que a guarda de aplicação não entrega (`SC-127`). Só roda contra PostgreSQL — no modo padrão da suíte este teste passa sem exercer nada*
- [X] T010 [P] Teste em `backend/tests/integration/requerimentos/test_restricoes.py`: duas raízes para a mesma Inscrição recusadas; dois sucessores do mesmo requerimento recusados; sucessor sem convocação autorizadora recusado; `ENVIADO` sem instante, versão, resumo ou aceite recusado. *Quatro invariantes, quatro recusas de banco — e nenhuma delas confiada a promessa de código*
- [X] T011 Confirmar, rodando `make DB_NAME=ps_demo_029 preparar`, que o provisionamento continua dizendo **`31 de 31`** e que `requerimentos_requerimentodematricula` **não** foi acrescentada a `TABELAS_APPEND_ONLY` em `backend/processo_seletivo/seguranca/papeis.py`. *A tabela muda legitimamente enquanto é rascunho, exatamente como `Inscricao` e `Retificacao`, que a política exclui de propósito. Se o número virar `32`, alguém confundiu imutabilidade condicional com append-only*
- [X] T012 Acrescentar `requerimento_momento` e `requerimento_declaracao` a `processos.Edital` em `backend/processo_seletivo/processos/models.py`, ambos `CharField`/`TextField` com `blank=True, default=""`, mais a migration. *Vazio, e não nulo: é a grafia deste repositório para "o Edital não declarou", a mesma de `especie_de_reversao` e `forma_de_convocacao`. `null` daria duas formas de dizer a mesma coisa, e o `DJ001` cobra isso*
- [X] T013 Emitir `matriculationRequest` na **raiz** do snapshot, em `backend/processo_seletivo/publicacoes/application/publish_edital.py`, **sempre com a chave presente** e com `None` quando o momento não estiver declarado. *A forma é a de `vacancyReversion`, no mesmo arquivo: `{…} if declarado else None`. **Não se omite a chave** — omitir faria o mesmo fato ter duas formas conforme o Edital, e a primeira redação desta tarefa mandava omitir (`FR-368`). A raiz é onde o snapshot já guarda o que limita o certame inteiro*
- [X] T014 Elevar `SCHEMA_VERSION` de **15 para 16** em `backend/processo_seletivo/shared/canonical.py` e acrescentar o degrau correspondente em `backend/processo_seletivo/publicacoes/domain/elevacao.py`. O degrau **acrescenta** `"matriculationRequest": null` ao conteúdo v15: a chave passa a existir, com o valor que significa "este Edital não exige" (`FR-368`). Elevar **sem** a chave deixaria o acervo antigo com uma forma que o emissor de hoje não produz. *Este achado faltava inteiro nas três primeiras passadas da pesquisa: a `T-001` nomeou três guardiões do conteúdo publicado e **não** nomeou o quarto mecanismo — a versão de esquema e a elevação do acervo. Sem o degrau, conteúdo antigo e novo conviveriam sob a mesma `schemaVersion`, e a `VERSOES_ELEVAVEIS` do módulo de elevação passaria a mentir sobre o que ela sabe elevar. **Nunca `null`**: a chave ausente e a chave nula não são a mesma coisa neste contrato*
- [X] T015 [P] Teste em `backend/tests/contract/test_elevacao_do_requerimento.py`: conteúdo publicado em v15 eleva para v16 com **`matriculationRequest: null`** — chave presente, valor nulo; conteúdo v16 com o objeto o preserva; e a elevação é idempotente. *A elevação do acervo é o que impede uma feature nova de reescrever, por omissão, o que Editais antigos publicaram — e é exatamente onde um degrau esquecido só aparece meses depois, numa consulta histórica*
- [X] T016 Classificar os dois caminhos em `backend/processo_seletivo/editais/domain/mutabilidade.py::CONTRATO` — `matriculationRequest/moment` **não retificável**, com a razão escrita; `matriculationRequest/declarationText` **retificável**. *O guardião compara o que o snapshot publica com o que o dicionário classifica e **falha por omissão nos dois sentidos**. A chave é `(coleção, caminho relativo)`, e o caminho aninhado tem precedente literal em `("profiles", "vacancyReversion/kind")` (`T-001`)*
- [X] T017 Acrescentar o achado impeditivo `matriculation_request_without_declaration` em `backend/processo_seletivo/editais/domain/validation.py`, condicionado ao ato de publicação. *Condicionado porque exigência impeditiva sem esse recorte bloquearia Retificação que nada tem com o requerimento — é a lição que a `027` deixou escrita. Impeditivo, e não advertência: aceite sem texto é aceite de nada, e o resumo da `FR-393` seria resumo de string vazia (`FR-407`)*
- [X] T018 Criar `chamada_em_aberto(inscricao)` em `backend/processo_seletivo/convocacao/application/selectors.py`, construído sobre `vigentes` e `desfecho_de`. **Não escrever um segundo predicado no app do requerimento.** *Vigente ≠ em aberto: uma convocação com desfecho continua vigente. `convocar.py::_em_aberto_da_pessoa` registra o beco que a confusão produziu na `019`, e duas leituras divergiriam (`T-006`, `D-004`)*
- [X] T019 Criar `backend/processo_seletivo/requerimentos/domain/disponibilidade.py` com a política que responde, para uma Inscrição, **se o requerimento é exigível, se está disponível e se está enviado** — lendo a declaração do Edital e, no momento *na convocação*, `chamada_em_aberto`. É esta função que `abrir_rascunho`, `gravar` e `enviar` consultam. **A submissão da inscrição consulta um predicado mais estreito, que não alcança `convocacao`**: no instante da submissão só existe a pergunta *"este Edital exige na inscrição, e está enviado?"* — o ramo da convocação nunca se aplica ali. *Constituição, Princípio IV: "Regras que afetem direitos, elegibilidade, documentação (…) DEVEM residir e ser verificadas no domínio/backend. Validações no frontend PODEM melhorar a experiência, mas **NÃO são fronteira de segurança**". Uma disponibilidade que só a tela conhece é regra de domínio morando na tela — e o `POST` que chega sem passar por ela não encontra nada que o recuse (`FR-371`, `FR-372`, `FR-373`).
  **E a repartição do predicado não é estilo**: `convocacao` importa `inscricoes` — a `Convocacao` aponta a `Inscricao`. Fazer `inscricoes.submissao` alcançar `convocacao` fecharia um ciclo entre apps: `inscricoes → requerimentos → convocacao → inscricoes`. Nenhum teste o proíbe hoje — `A_MONTANTE` de `test_dependencia_da_convocacao` é `("ocupacao", "classificacao", "resultados")` —, mas este repositório mantém **duas** varreduras dedicadas a sentido de dependência, e fechar ciclo com elas por perto é escolher o defeito que elas existem para impedir*
- [X] T020 [P] Teste em **dois** arquivos — `backend/tests/unit/requerimentos/test_gatilho.py`, para a política pura, e `backend/tests/integration/requerimentos/test_chamada_em_aberto.py`, para o predicado contra convocações reais. **A divisão não é estilo**: `chamada_em_aberto` lê convocações, desfechos e sucessões, e um teste unitário só pode injetar sentinela — provaria a política e não provaria o predicado, que é o que erra. A primeira redação desta tarefa pedia os quatro cenários no arquivo unitário, e a primeira implementação os "atendeu" injetando `object()` e `None`. Cenários: convocação vigente **sem** desfecho abre; **com** desfecho não abre; sucedida não abre e a sucessora abre; as três espécies abrem igual. *É a `FR-373` e a `FR-375`, e é o teste que impede alguém de trocar `chamada_em_aberto` por `vigentes` numa refatoração distraída*
- [X] T021 Fazer o **Edital máximo** declarar o requerimento — momento e texto — na fixture `conteudo_maximo` de `backend/tests/contract/test_mutabilidade.py`. *O guardião compara o `CONTRATO` com `campos_publicados(conteudo_maximo)`, que percorre um Edital **realmente publicado** pela fixture. Classificar dois caminhos que o máximo nunca emite faz o guardião falhar pelo lado "classificado e não publicado" — e a tarefa seguinte, que atualiza os guardiões, não cobre isto: ensinar o guardião não é fazer o máximo declarar*
- [X] T022 [P] Atualizar os três guardiões que falham por omissão — `backend/tests/contract/test_forma_publicada.py`, `backend/tests/contract/test_mutabilidade.py` e o esquema que eles leem — para conhecer o objeto novo. *Falhar por omissão é o comportamento desejado deles; a tarefa é ensiná-los o campo, não silenciá-los*

**Checkpoint**: a entidade existe e é imutável depois do envio; o Edital sabe declarar; o gatilho de
disponibilidade tem **uma** fonte. Nenhuma tela mudou.

> **Atenção a quem for parar aqui.** Entre este checkpoint e a T047 o Edital tem campo publicado
> **sem caminho de escrita na interface** — exatamente o estado que o `T-002` condena no
> `maxInscricoesPorCandidato`, e que o Princípio VI chama de capacidade não entregue. A fixture
> grava os dois campos e a `US1` anda sem a tela, que é o que torna as histórias independentes; mas
> **interromper a execução na Fase 2 instala a dívida**. Quem precisar parar, pare depois da Fase 5.
> *(O [plan.md](./plan.md) põe a tela no passo 1 por esta razão; onde os dois divergirem, vale este
> arquivo — e o risco fica dito aqui, que é onde alguém o lê.)*

---

## Phase 3: User Story 1 — O candidato entrega, na inscrição, só o que falta (P1)

**Goal**: num Edital que declara *na inscrição*, a pessoa completa o que falta, aceita a declaração e
envia — sem redigitar nada que o sistema já saiba.

**Independent test**: publicar um Edital com `moment = AT_ENROLLMENT` (fixture pode gravar os campos
direto, sem depender da tela da `US3`), preencher e enviar pelo portal, e conferir que nome, CPF,
e-mail, curso, modalidade e protocolo **não aparecem como campo** (`SC-120`).

- [X] T023 [P] [US1] Criar `backend/processo_seletivo/requerimentos/domain/endereco.py` com a porta `referencia_de_cep(cep) -> EnderecoDeReferencia | None` e a normalização do CEP para oito dígitos. *O domínio **não** nomeia fornecedor (`FR-389`). A implementação concreta muda; a porta não*
- [X] T024 [P] [US1] Criar `backend/processo_seletivo/requerimentos/infrastructure/referencia_local.py` implementando a porta sobre `ReferenciaDeCep`, por chave primária, devolvendo `None` quando não houver linha. *Tabela vazia é estado válido, e não erro: a `FR-390` faz o sistema funcionar sem ela*
- [X] T025 [P] [US1] Criar `backend/processo_seletivo/requerimentos/management/commands/carregar_ceps.py`, lendo o dump JSON de `gpfconfea/banco-ceps` e gravando `cep, logradouro, bairro, municipio, uf, codigo_ibge` — **descartando latitude e longitude**. Idempotente. *A base é MIT e traz `ibge`, que é o que a `FR-388` consome. As coordenadas ficam de fora porque a **própria fonte** adverte que a confiabilidade delas é variável — a `D-008` deixou de ser preferência e virou evidência (`T-008`). **Medido em 17/09/2026**: a fonte distribui **um arquivo JSON por CEP** — 1.209.314 deles —, não um dump único; 379 MB comprimidos, 278 MB descomprimidos. Descompactar produziria 1,2 milhão de inodes para serem lidos uma vez, e por isso o comando passou a **ler o `.zip` direto, em fluxo**. A carga inteira leva **31 s** e grava 1.209.314 linhas*
- [X] T026 [US1] Criar `backend/processo_seletivo/requerimentos/application/preencher.py` com `abrir_rascunho`, `gravar` e `enviar`, com `command_context()`, `select_for_update` e `expected_revision`. **Os três consultam a política da T019 e recusam por si**: Edital que não declara (`FR-371`), e momento *na convocação* sem chamada em aberto (`FR-373`). **A política devolve a chamada concreta**, e `abrir_rascunho` a persiste em `convocacao_autorizadora` — também na raiz, e não só no sucessor: é o que torna reconstituível qual convocação abriu aquele requerimento. `abrir_rascunho` pré-preenche de **duas** origens, nesta precedência: o último requerimento **enviado** da mesma identidade, quando houver (`FR-377`); e, para o telefone celular, o da Inscrição quando o anterior não o trouxer (`FR-379`). *Cópia, nunca referência (`D-005`): editar aqui não pode alcançar o requerimento anterior, e `SC-124` verifica isso lendo o anterior depois da edição. **As duas origens são distintas de propósito**: o telefone da Inscrição congelou na submissão e pode ter meses, então ele entra como ponto de partida a confirmar — nunca como verdade*
- [X] T027 [US1] Fazer `enviar`, em `backend/processo_seletivo/requerimentos/application/preencher.py`, gravar versão consolidada vigente, resumo `sha256` do texto **exibido** — conferido contra a versão que a tela transportou —, instante e identidade; tomar **`FOR SHARE` no Edital e no Processo Seletivo** antes de ler a versão e a chamada; recusar o envio quando a versão exibida já não for a vigente, redesenhando a tela com o texto novo; recusar sem aceite; e **admitir filiação com um dos nomes ausente** (`FR-384`). *O resumo é do texto exibido, e não do texto de hoje: retificar a declaração depois não pode reescrever o que a pessoa leu (`FR-393`, `SC-129`). E a validação **não** exige os dois nomes de filiação: pai não declarado é situação comum e legítima, e travar o envio por isso seria inventar exigência que Edital nenhum faz. **E a versão exibida viaja no formulário** porque uma Retificação entre o `GET` e o `POST` faria a `FR-393` gravar uma versão que não é a do texto cujo resumo se guardou — o par ficaria incoerente e ninguém notaria. É a distinção que a `Inscricao` já carrega em duas colunas, `versao_reconhecida` e `versao_aceita`, e pela mesma razão.
  **O `FOR SHARE` no Edital foi previsto aqui e não existe — e a decisão é deliberada, medida em 17/09/2026.** Tomá-lo **junto** com o do Processo produz *deadlock* real: este repositório tem duas ordens de travamento incompatíveis — `comando_de_comissao` toma o Processo e depois o Edital, `replace_draft` e a publicação tomam o Edital com o Processo na mesma consulta —, e quem pedisse as duas linhas deadlockaria contra uma delas em qualquer ordem. O teste de corrida da T036 reproduziu o defeito nas duas ordens.

  **E ele deixou de ser necessário para o que esta tarefa protege.** O resumo passou a sair do **mesmo objeto de versão** que se grava — `declaracao_publicada(versao.content)`, e não do texto recebido no `POST` —, de modo que o par *versão aceita* + *resumo* **não tem como divergir**: publicada a Retificação antes ou depois da leitura, o que se registra é a versão que a pessoa leu, com o resumo do texto daquela versão. É mais verdadeiro do que bloquear a Retificação, e é o que a `SC-129` pede. A corrida é exercida por duas conexões reais em `test_corridas.py`, que afirma o **invariante** — e não a trava que deixou de existir.
  **O `FOR SHARE` no Processo Seletivo fecha a segunda corrida**, a do desfecho: os comandos de convocação passam por `comando_de_comissao`, que trava o Processo com `select_for_update`. Sem compartilhar essa linha, o envio lê "chamada em aberto", outra transação grava o desfecho, e o envio confirma sobre uma chamada que já não estava aberta. `FOR SHARE` é a forma certa nos dois casos: candidatos não se bloqueiam entre si, e ambos conflitam com o `FOR UPDATE` de quem muda a norma ou o desfecho*
- [X] T028 [US1] Gravar auditoria no envio, em `backend/processo_seletivo/requerimentos/application/preencher.py`, pelo mecanismo que já existe em `backend/processo_seletivo/auditoria/`: quem enviou, para qual Inscrição, para qual Edital, quando, o que foi declarado, qual declaração foi aceita, sob qual versão e — havendo — qual requerimento ele sucede e sob autorização de qual convocação. *`FR-397`, e é **MUST** do Princípio III: "Operações sensíveis DEVEM gerar auditoria com ator, ação, entidade, identificador, data e hora, estado anterior e posterior, motivo, versão e contexto". O envio é peça de ato administrativo — é nele que um indeferimento se funda —, e sem trilha o que fundamentou a decisão não é reconstituível. **Esta tarefa não envia mensagem nenhuma, e isso é regra e não omissão**: `test_situacoes_de_mensagem` percorre todo `*.py` contando chamadas de `send_mail` e prende o número à `FR-084` da `010`, que **enumera** as situações e exige revisão escrita para admitir outra. Confirmar o recebimento por e-mail é o reflexo de quem implementa — e exige revisar aquela norma **antes**, não depois. **A auditoria referencia, e não copia**: ela aponta o requerimento em vez de repetir cor/raça, filiação, documento e endereço dentro do registro, porque trilha que duplica dado sensível multiplica a superfície em vez de protegê-la (`FR-401`)*
- [X] T029 [US1] Criar a tela em `backend/processo_seletivo/portal/templates/portal/requerimento.html` e as views `GET`/`POST` em `portal/views.py`, com titularidade por `_inscricao_do_titular` e **`@resposta_privada`** (`shared/http.py`), como as outras nove views do portal. Separar *o que o sistema já sabe* de *o que falta você informar*, dizendo de onde veio cada dado conhecido. *Sem o decorador, uma tela com filiação, documento e endereço fica armazenável pelo navegador. E **a rubrica de acessibilidade alcança o template novo sozinha**: `test_acessibilidade_do_portal` é parametrizado sobre `PORTAL.glob("*.html")` e cobra controle nativo, rótulo ligado por `id`, nenhuma largura em pixel e estado que não dependa só de cor — num formulário de vinte campos, o rótulo por `id` é o que mais cobra. **E a classe nova exige conferir a folha**: `test_acessibilidade` varre os templates dos **dois** canais e as **duas** folhas de estilo, casando por **substring** — inclusive dentro de comentário CSS, o que já quebrou asserção neste repositório. Regra nova na folha se confere contra a asserção antes de entrar. Nome, CPF e e-mail entram como **informação**, com o caminho para *Meus dados* e *Conta* — nunca como campo desabilitado sem explicação (`FR-378`, `UX-053`). A recusa a quem não é titular é indistinguível de inexistente, e isso vem de graça no seletor*
- [X] T030 [US1] Acrescentar o preenchimento assistido por CEP a `backend/processo_seletivo/portal/templates/portal/requerimento.html` e a rota **`POST /requerimento/cep`** em `portal/urls.py` e `portal/views.py`, com o CEP **no corpo**, sessão de candidato exigida e proteção CSRF. Município e UF somente leitura enquanto o CEP for reconhecido; os demais campos de endereço abertos quando não for, e o código IBGE **nunca editável**, em nenhum dos dois casos. O comportamento no navegador vive em `backend/processo_seletivo/portal/static/portal/cep.js` — precedente: `telefone.js` —, com teste de comportamento no molde dos que `tests/test_javascript.py` executa. ***Nada do candidato é guardado no navegador***: `test_o_canal_do_candidato_nao_escreve_no_navegador` percorre **todo** `.js` e `.html` do portal atrás de `localStorage`, `sessionStorage`, `indexedDB` e `document.cookie`, e alcança os arquivos novos **automaticamente** — guardar CEPs já consultados é a otimização óbvia, e é exatamente o que ela existe para impedir. E `node --test` troca de relator entre a CI e o terminal: asserção sobre o resumo passa aqui e reprova lá. *`POST` com o CEP no corpo, e **não** `GET /requerimento/cep/<cep>`: a `FR-401` proíbe endereço em URL, e a varredura da T060 reprovaria a própria rota — endereço em URL viaja para log de servidor, histórico de navegador e cabeçalho de referência sem que ninguém decida isso. Rota aberta seria um serviço de terceiros hospedado por engano. E a mensagem de falha **não culpa quem digitou** (`UX-055`, `FR-388`, `FR-390`)*
- [X] T031 [US1] Acrescentar o cartão do requerimento à tela da inscrição em `backend/processo_seletivo/portal/templates/portal/inscricao.html`, e o aviso de que a submissão depende dele. Bloquear a submissão da inscrição em `backend/processo_seletivo/inscricoes/application/submissao.py`, consultando a política da T019 — **a recusa é do comando, e a tela apenas a antecipa**. O bloqueio vale **somente** quando o momento declarado é *na inscrição*: Edital que coleta *na convocação* MUST submeter inscrição normalmente, sem requerimento nenhum. *A recusa mora no comando porque a tela não é fronteira de segurança (Princípio IV); o bloqueio **anunciado antes da tentativa** (`UX-054`): descobrir no clique é o defeito que a auditoria de UX já nomeou. Sem ajuda visível no cartão — a microcópia mora na tela de preenchimento (`UX-052`)*
- [X] T032 [US1] Fazer `backend/processo_seletivo/portal/templates/portal/requerimento.html` mostrar, no estado enviado, o que o sistema recebeu e o instante, sem campo editável, no molde de `portal/views.py::_conferencia`. *`FR-406`, e é a mesma promessa que a inscrição enviada já cumpre*
- [X] T033 [P] [US1] Teste em `backend/tests/integration/requerimentos/test_preenchimento.py`: pré-preenchimento por cópia; editar não altera o anterior; envio sem aceite recusado; enviado não editável pela aplicação; **envio conclui com um dos nomes de filiação em branco**; **a aplicação recusa por si, sem passar por tela, Edital que não declara e momento *na convocação* sem chamada em aberto**; Retificação entre o `GET` e o `POST` faz o envio ser recusado em vez de gravar par incoerente; e **a submissão da inscrição** recusa em *na inscrição* sem envio, aceita com envio, e **aceita normalmente em Edital que coleta na convocação**, chamando `enviar_inscricao` **direto** — e não um predicado auxiliar, que provaria o auxiliar. *Chamar a aplicação direto é o que prova que a regra não mora na tela (Princípio IV). Cobre `SC-124`, `SC-128`, `FR-384`, `FR-371`, `FR-373`, `FR-393` e a metade de aplicação da `SC-127`*
- [X] T034 [P] [US1] Teste em `backend/tests/integration/requerimentos/test_cep.py`: CEP reconhecido preenche município, UF e IBGE sem digitação; base vazia abre os campos de endereço e o envio conclui com IBGE vazio; e **registro de referência incompleto — sem bairro, ou sem código IBGE — também não bloqueia**, com o que faltou editável e o IBGE permanecendo não editável e vazio. *`SC-125`, `SC-126` e `FR-388`. Resposta incompleta é caso distinto de base vazia, e é o mais provável dos dois — e o segundo é o que prova que serviço externo não bloqueia processo (`FR-390`)*
- [X] T035 [P] [US1] Teste em `backend/tests/integration/requerimentos/test_nao_escreve_fora.py` contando gravações: nenhuma alcança `CandidateIdentity`, `Inscricao`, `ValorDeFato` ou requerimento anterior. *`SC-130`, `FR-398` — é a prova de que a fronteira da `D-005` é real e não apenas intenção*
- [X] T036 [US1] Teste de concorrência em `backend/tests/integration/requerimentos/test_corridas.py`, contra PostgreSQL: **(a)** Retificação publicada entre a leitura da versão e o commit do aceite não produz par incoerente — o envio espera a trava e conclui sob a versão certa, ou é recusado; **(b)** desfecho gravado por outra transação entre a leitura da chamada e o commit do envio não deixa o envio confirmar sobre chamada já fechada. *As duas corridas são as que o `command_context()` sozinho **não** serializa. O molde de interleaving é o que a suíte já usa para a submissão da inscrição, e o teste precisa de duas conexões — no SQLite ele não prova nada*
- [X] T037 [P] [US1] Teste em `backend/tests/integration/requerimentos/test_auditoria.py`: o envio grava **um** evento, sobre o **requerimento** como agregado — e não sobre a Inscrição, cujo estado e revisão este ato não muda —, com ator, inscrição, Edital, instante, versão, declaração aceita e — havendo — requerimento sucedido e convocação autorizadora; e **o nome legível das duas operações existe em `interface/views.py::OPERACOES`**, conferido aqui porque a varredura global só enxerga literais e estas chegam como constante. *(A metade da **sucessão** fica na T057, com o comando que a produz: não há como gravar a trilha de um ato que a US5 ainda não implementou.)* *`test_trilha_legivel` coleta todo literal `operation="…"` passado a `record_event` em `**/application/*.py` e o confronta com aquele mapa: operação sem nome legível derruba a varredura, e a trilha fica ilegível para quem responde um questionamento. Sem asserção **positiva**, a varredura de dado sensível passaria com zero evento gravado: um teste que só afirma ausência é satisfeito pelo vazio*
- [X] T038 [P] [US1] Teste de portal em `backend/tests/interface/test_portal_requerimento.py`: titular abre; não titular recebe resposta indistinguível de inexistente; Edital sem declaração devolve 404 inclusive por rota digitada à mão; e **um identificador de requerimento de outra pessoa, na rota do anterior, é recusado como inexistente**. *`SC-123`, `SC-131` e `FR-399`. A terceira asserção é a que fecha o IDOR do segundo identificador: titularidade da Inscrição não confere o requerimento*
- [X] T039 [P] [US1] Teste de portal em `backend/tests/interface/test_portal_sem_redigitar.py`: nome, CPF, e-mail, curso, modalidade, protocolo e Edital **não aparecem como campo de entrada** em tela nenhuma desta feature, e aparecem como informação com o caminho para onde se corrigem; e a declaração aparece por extenso, com o aceite num ato explícito. *`SC-120` é o critério-manchete do MVP e era o único da §20 sem tarefa. O mesmo teste cobre a `FR-380` — perfil, modalidade, protocolo e Edital são **derivados, nunca perguntados** — e a `UX-056`. Asserção sobre **ausência** de campo é a que envelhece mal sem teste: basta alguém acrescentar um `input` "para facilitar", e a promessa inteira da feature cai sem que nada acuse*

**Checkpoint**: a `US1` é **demonstrável** sozinha — por fixture que grava a declaração do Edital. Ela
**não está entregue** enquanto a T047 não existir: até lá, o canal de quem elabora é a fixture, e o
Princípio VI diz que *"demonstrar por chamada manual aquilo que o canal do ator não oferece NÃO
satisfaz esta exigência"*. Independência de história e entrega de capacidade são coisas diferentes, e
esta linha existe para não confundi-las.

---

## Phase 4: User Story 2 — O convocado, e o suplente pelo mesmo caminho (P1)

**Goal**: num Edital que declara *na convocação*, o requerimento só existe quando há chamada em
aberto — e o suplente chega por onde o primeiro colocado chegou.

**Independent test**: convocar para vaga inicial e, depois, um suplente; verificar que o requerimento
abre para os dois sem passo administrativo próprio (`SC-121`, `SC-122`).

- [X] T040 [US2] Criar `backend/processo_seletivo/requerimentos/application/selectors.py` que **apenas traduz** a resposta da política da T019 para os cinco estados de tela: *não aplicável*, *ainda indisponível*, *disponível*, *em preenchimento*, *enviado*. **Ele não relê a declaração do Edital nem chama `chamada_em_aberto`** — recebe a resposta pronta e a converte em vocabulário de tela. *Não são coluna, de propósito — é como a ocupação e a convocação já derivam vigência (`§12`)*
- [X] T041 [US2] Ligar a tela à política, em `backend/processo_seletivo/portal/views.py`: a view chama o tradutor da T040 e renderiza o estado que ele devolver. **Nenhuma leitura de disponibilidade fora da política da T019** — nem na view, nem no template. *O vencimento do prazo **não** fecha nada: quem decide a consequência do prazo é a convocação, e duas contagens do mesmo prazo divergiriam (`FR-374`)*
- [X] T042 [US2] Fazer `backend/processo_seletivo/portal/templates/portal/requerimento.html` e o cartão em `portal/templates/portal/inscricao.html` distinguirem *"este certame não pede requerimento"* de *"ainda não chegou a sua vez"*. *Colapsá-las diria a quem ainda tem chance que ela não tem — é a mesma distinção que a tela de convocação já é obrigada a fazer (`FR-405`)*
- [X] T043 [P] [US2] Teste em `backend/tests/integration/requerimentos/test_disponibilidade.py`: sem chamada, indisponível; chamada em aberto, disponível; desfechada, legível e não enviável; suplente convocado depois abre pelo mesmo caminho. *`SC-121`, `SC-122` e `SC-134` — e o último cobre as **sete** espécies de desfecho*
- [X] T044 [P] [US2] Teste de portal em `backend/tests/interface/test_portal_requerimento_convocacao.py` afirmando que as duas ausências têm textos distintos. *A distinção é de tela, e por isso o teste é de tela*

**Checkpoint**: `US1` e `US2` entregues — as duas de P1.

---

## Phase 5: User Story 3 — Quem elabora declara a exigência, o momento e o texto (P2)

**Goal**: a declaração deixa de ser fixture e passa a ser composta por quem elabora.

**Independent test**: compor a declaração na etapa *Inscrição*, publicar, e ler o objeto no conteúdo
publicado; apagar o texto e ver a publicação recusada (`SC-136`).

- [X] T045 [US3] Criar `atualizar_requerimento_de_matricula` em `backend/processo_seletivo/editais/application/`, no molde de `update_edital_identification`: permissão `edital:elaborar`, `command_context()`, `select_for_update`, `ensure_processo_accepts_changes`, estado `EM_ELABORACAO`, `expected_revision`. *Comando próprio, e **não** `replace_draft`: aquele não carrega campo de raiz, e "substitui o rascunho inteiro — o que não for reenviado é apagado", que é um caminho que já produziu perda de dado aqui (`T-003`)*
- [X] T046 [US3] Mostrar o momento e o texto da declaração no resumo da etapa **Revisão**, em `backend/processo_seletivo/interface/revisao.py`. *`test_estaticos` varre a etapa **`revisao`** atrás de `{#`, `{%` e `{{` que cheguem ao navegador, e o defeito que ele registra já aconteceu: *"um comentário sobre FR-020 apareceu para o usuário entre os botões"*, porque `{# … #}` do Django só comenta **uma** linha. Comentário de duas linhas neste template é impresso na tela. Ela já resume campos de raiz — `title` e `description` saem do snapshot ali. Quem revisa antes de publicar um **ato imutável** precisa ver o que o Edital passou a exigir; sem isto, a única confirmação do texto seria a tela onde ele foi digitado*
- [X] T047 [US3] *(A rubrica de acessibilidade do canal administrativo — `test_acessibilidade` — é parametrizada sobre **todo** template de `interface/`, e este é um deles: controle nativo e rótulo ligado por `id` valem aqui como valem no portal.)* Acrescentar os campos à etapa **Inscrição** do assistente, em `backend/processo_seletivo/interface/templates/interface/compor_inscricao.html` e na view correspondente. **Nenhuma etapa nova.** *É onde o período e os Documentos Exigidos já são compostos — onde quem elabora decide o que se pede ao candidato (`T-003`)*
- [X] T048 [US3] Acrescentar, no `como-preencher` da etapa em `backend/processo_seletivo/interface/templates/interface/compor_inscricao.html`, a frase que diz a quem elabora que o Anexo em papel passa a ser dispensável quando há requerimento estruturado. *É a mitigação que o `R-3` pede, e ela é texto, não mecanismo. Sem ela, o risco é nenhum Edital exercer a decisão e a pessoa fazer as duas coisas — pior que hoje*
- [X] T049 [US3] Oferecer `/matriculationRequest/declarationText` na tela de Retificação, em `backend/processo_seletivo/interface/retificacao.py::CAMPOS_REGRA`. *Sem isto o texto nasce irretificável, e endereço de retificação não se conserta depois porque publicação é ato imutável (`T-001`)*
- [X] T050 [P] [US3] Teste de interface em `backend/tests/interface/test_compor_requerimento.py`: compor, publicar e ler o objeto; texto vazio com momento declarado recusa a publicação com pendência encaminhada à etapa Inscrição; Edital sem declaração publica normalmente. *`SC-136`. E é este teste que impede esta feature de repetir o `maxInscricoesPorCandidato` — campo publicado **sem caminho de escrita na interface** (`T-002`)*
- [X] T051 [P] [US3] Teste de contrato em `backend/tests/contract/test_retificar_requerimento.py`: o texto é retificável e o momento não, com a razão vindo do contrato. *A `026` governa esta feature em vez de ser alterada por ela*

**Checkpoint**: a jornada de quem elabora existe pelo canal dela.

---

## Phase 6: User Story 4 — Quem conduz lê o que a pessoa declarou (P2)

**Goal**: o requerimento aparece no dossiê da inscrição, estruturado.

**Independent test**: abrir o dossiê de uma inscrição com requerimento enviado e ler campos e
instante; sem a permissão, a recusa não revela que ele existe.

- [X] T052 [US4] Acrescentar o bloco do requerimento a `backend/processo_seletivo/interface/templates/interface/inscricao_detalhe.html` e à view correspondente em `interface/views.py`, sob `inscricao:consultar`. **Sem rota de listagem.** *Listagem seria superfície nova sobre dado pessoal sem jornada que a peça (`FR-400`). E o estado não entra em lista de inscrições: leitura por listagem é o que este repositório já reprovou (`T-009`)*
- [X] T053 [P] [US4] Teste em `backend/tests/interface/test_dossie_requerimento.py`: com a permissão, lê; sem ela, recusa que não revela existência; e **nenhuma rota de listagem de requerimentos existe**. *A terceira asserção é sobre ausência, e é a que envelhece mal sem teste*

**Checkpoint**: as quatro primeiras histórias entregues.

---

## Phase 7: User Story 5 — Correção por convocação para regularizar (P3)

**Goal**: quem foi convocado para regularizar corrige o que declarou, sem que o anterior seja apagado.

**Independent test**: indeferir, convocar para regularizar, enviar o sucessor, e ler o anterior
intacto (`SC-135`).

- [X] T054 [US5] Acrescentar `suceder` a `backend/processo_seletivo/requerimentos/application/preencher.py`: só com chamada em aberto, citando a convocação autorizadora, copiando o conteúdo do antecessor. *Fora disso é edição com outro nome (`FR-408`, `D-007`). A autorização é a porta que impede a sucessão de virar edição disfarçada — é o `R-6`*
- [X] T055 [US5] Oferecer *conferir e atualizar* em `backend/processo_seletivo/portal/templates/portal/requerimento.html` quando houver, ao mesmo tempo, requerimento enviado e chamada em aberto — e **não criar sucessor quando nada mudar** — e a comparação é do **comando** `suceder`, não do template: um `POST` montado à mão criaria histórico artificial que a tela nunca ofereceria. *`FR-410`. É também a mitigação do dado envelhecido da coleta antecipada (`R-2`), sem regra extra*
- [X] T056 [US5] Acrescentar a rota `GET /inscricoes/<uuid>/requerimento/anterior/<uuid>` em `backend/processo_seletivo/portal/urls.py` e `portal/views.py`, com o template `portal/templates/portal/requerimento_anterior.html` e o link a partir de `requerimento.html`. **O anterior é buscado já filtrado pela cadeia da Inscrição do titular** — nunca por `get(pk=…)` sobre o segundo identificador. *Sem o filtro, o segundo UUID é IDOR: a titularidade confere a Inscrição e ninguém confere o requerimento, e um identificador de outra pessoa passaria (`FR-399`). Corrigir não é apagar, e a pessoa precisa poder ver o que declarou antes (`UX-059`)*
- [X] T057 [P] [US5] Teste em `backend/tests/integration/requerimentos/test_sucessao.py`: com chamada em aberto o sucessor nasce e o anterior permanece legível; sem ela, `successor_not_authorized`; segundo sucessor recusado pela restrição; e **sucessor com conteúdo idêntico ao antecessor é recusado pelo comando**, chamado direto, sem passar por tela. *`SC-135` e `FR-410`. A última asserção é a que impede histórico artificial por `POST` montado à mão — a comparação é do comando, e a tela só evita oferecer o botão*

---

## Phase 8: Polish & Cross-Cutting Concerns

- [X] T058 [P] Criar `backend/tests/test_vocabulario_do_requerimento.py` no molde de `test_vocabulario_da_ocupacao.py`, com a lista literal dos arquivos desta feature e os termos proibidos da `UX-058` — *deferido*, *indeferido*, *homologado*, *matrícula efetivada* —, cada um com a frase que diz o que ele afirmaria indevidamente. Ler o texto **sem comentário e sem docstring**. *Explicar por que uma palavra está proibida exige escrevê-la; quem esquecer isso escreve um teste que falha pelo próprio comentário que o explica (`T-013`, `SC-132`)*
- [X] T059 [P] Criar o teste de redação em `backend/tests/test_sem_dado_pessoal_da_amostra.py`, varrendo `specs/029-*`, `doc/descoberta-029-*` **e `backend/tests/`, fixtures inclusive**, pelos identificadores da linha real da planilha — **guardados como resumos `sha256` normalizados**, nunca em claro. *O teste **não pode conter o que procura**: guardar CPF, CEP e nome em claro para varrê-los faria dele o vazamento que existe para impedir. Ele compara resumos dos valores normalizados — dígitos do CPF, CEP sem pontuação, nome sem acento e em caixa baixa —, e os originais permanecem fora do repositório. *`SC-137` nomeia quatro alvos — spec, descoberta, **teste e fixture** —, e varrer só os dois primeiros deixaria de fora justamente onde um dado de exemplo é copiado sem pensar. A regra de privacidade alcança a própria documentação da feature, e a §0 da descoberta registra a política*
- [X] T060 [P] Criar `backend/tests/test_dado_sensivel_do_requerimento.py`: nenhuma rota desta feature carrega cor/raça, filiação, documento, endereço ou faixa de renda no endereço; nenhuma mensagem de recusa os repete; nenhum registro de auditoria os grava. *`FR-401`, e é **MUST** do Princípio III — "Logs e auditoria NÃO DEVEM expor conteúdo sensível desnecessário". Hoje as duas garantias existem por construção: o endereço da rota é o da Inscrição, por convenção do portal, e a auditoria referencia em vez de copiar (T028). **É justamente por serem construção, e não mecanismo, que se perdem numa refatoração** — e este teste é o que as prende*
- [X] T061 Criar `specs/029-requerimento-de-matricula/contrato-de-saida.md` a partir da §3 de [contracts/requerimento-de-matricula.md](./contracts/requerimento-de-matricula.md), e o teste que verifica que as **34** colunas têm origem declarada ou questão aberta nomeada. *`FR-403`, `SC-133`. Onde não há regra, o mapa diz que não há — `RENDA_PER_CAPITA_PNP` sai com a divergência de significado escrita ao lado (`R-7`), e nenhuma conversão é inventada*
- [X] T062 Declarar o requerimento num Edital do `seed_demo` em `backend/processo_seletivo/processos/management/commands/seed_demo.py` — e **acrescentar ao seed a convocação que falta**. *O `seed_demo` não cria convocação nenhuma hoje — zero ocorrências de `Convocacao` no comando —, de modo que "escolher um Edital que chegue à convocação" não era escolha possível: nenhum chega. Sem a convocação semeada, a `US2` não é demonstrável e o `C8` para antes do ponto. O comando monta os Editais por caminhos distintos (`_edital_reaproveitado`, `_edital_encerrado`, `_edital_de_sorteio`); escolher o errado entrega uma demonstração que para antes do ponto (`T-010`)*
- [X] T063 [P] Criar `backend/tests/integration/requerimentos/test_orcamento_de_consulta.py` prendendo os números que o plano declara: **+2** consultas em `portal:inscricao` e `portal:acompanhamento`, **+1** no dossiê, e **zero** em `portal:inscricoes`. *O plano declara orçamento e nada o media — e orçamento sem teste é intenção. O **zero** é o que mais importa: exibir o estado do requerimento por linha de listagem é leitura por listagem, que este repositório já reprovou ([research.md](./research.md), `T-009`)*
- [X] T064 [P] Criar `backend/tests/integration/requerimentos/test_convivencia_com_o_anexo.py`: o requerimento estruturado **não** remove nem passa a exigir por conta própria o Documento Exigido do Anexo, e não cria um segundo acervo de documentos — Edital com os dois funciona, e Edital sem o Anexo também. *`FR-395` e `FR-402` são garantias de **não fazer**, e garantia de não fazer sem teste envelhece no primeiro refactor. A T048 cobre o texto de ajuda; isto cobre o comportamento*
- [X] T065 Percorrer o `C8` de [quickstart.md](./quickstart.md) inteiro na demonstração, pelo canal de cada ator, sem shell e sem banco. *É o cenário que decide se a feature está entregue (Princípio VI). O servidor local roda **da worktree**: "não vejo a mudança" costuma ser a porta errada, não o merge*
- [X] T066 Rodar `make DB_NAME=ps_demo_029 lint check test-pg` e comparar com a contagem da T002. *`lint` são dois passos. E não editar template durante a suíte: arquivo criado ou apagado no meio de `test-pg` dá falha que não é do diff*

---

## Dependencies

```text
Setup (T001–T002)
   └─ Foundational (T003–T022)   ← bloqueia todas as histórias
        ├─ US1 (T023–T039)   P1
        ├─ US2 (T040–T044)   P1   — depende de T018 a T020
        ├─ US3 (T045–T051)   P2   — **no MVP**, apesar de P2 (Princípio VI)
        ├─ US4 (T052–T053)   P2   — precisa de requerimento enviado (US1 ou US2)
        └─ US5 (T054–T057)   P3   — depende de US2 (chamada em aberto)
             └─ Polish (T058–T066)
```

**As histórias não são todas independentes, e dizer o contrário seria falso.** `US4` precisa de um
requerimento enviado por alguma das duas primeiras; `US5` precisa da chamada em aberto da `US2`. A
`US3` **é** independente: as fixtures gravam os dois campos do Edital direto, e é por isso que ela
pode vir depois sem travar nada.

## Parallel Execution

| Fase | Podem correr juntas |
|---|---|
| Foundational | T003 e T004; depois T009, T010, T015, T020 e T022 |
| US1 | T023, T024 e T025; depois T033, T034, T035, T037, T038 e T039 |
| US2 | T043 e T044 |
| US3 | T050 e T051 |
| Polish | T058, T059, T060, T063 e T064 |

## Implementation Strategy

**MVP**: Setup + Foundational + `US1` + **`US3`**. Entrega o Requerimento estruturado nos Editais que coletam na
inscrição — que são o 77 e o 58, a maioria da amostra — e já elimina a transcrição manual para eles.
**A `US3` entra no MVP, apesar de ser P2**, porque sem ela a declaração do Edital só existe por
fixture: seria capacidade sustentada pelo domínio e alcançada por canal nenhum, que é o que o
Princípio VI recusa. É a mesma razão do `T-002`.

**Incremento 2**: `US2`. Leva a feature aos Editais que coletam na convocação (69 e 46) e realiza a
fronteira entre seleção e matrícula: quem não chega à vaga não entrega dado de vínculo.

**Incremento 3**: `US3` e `US4` — a jornada de quem elabora e a leitura de quem conduz.

**Incremento 4**: `US5` — a correção, que é a minoria dos casos e a que fecha o beco do 77 (8.2).
