# Tasks: Avisos complementares aos candidatos, vinculados a ato oficial

**Input**: Design documents from `specs/066-avisos-complementares/`
**Prerequisites**: plan.md, spec.md, research.md (R-001 a R-016), data-model.md,
contracts/telas.md, contracts/despacho.md, contracts/mensagem.md, quickstart.md

**Tests**: pedidos pela Constituição (V) e pelos cenários de aceitação da spec. Abreviações:

- **TU**: testes unitários sem banco, em `backend/tests/unit/avisos/`.
- **TI**: testes de integração contra PostgreSQL, em `backend/tests/integration/avisos/`.
- **TT**: testes de tela, em `backend/tests/interface/test_avisos.py`.

Caminhos:

- **A** = `backend/processo_seletivo/avisos/`
- **I** = `backend/processo_seletivo/interface/`
- **T** = `backend/tests/`

**Regra de toda tarefa**: português no código; comentário explica o porquê; nenhum
`select_for_update` sobre tabela append-only (`R-002`); nenhum envio dentro da requisição
(`FR-1265`). As suítes rodam com `TEST_DB_ENGINE=postgresql` e `DB_NAME=ps_066`.

## Phase 1: Setup

- [X] T001 Conferir o ambiente da worktree:
  - `uv sync --extra dev` e `backend/.env` com `DB_NAME=ps_066`;
  - `manage.py migrate --check` sem pipe;
  - os guardiões verdes **antes** de mudar qualquer coisa: T`test_situacoes_de_mensagem.py`, T`migrations/test_migrations.py`, T`integration/test_database_permissions.py`, T`test_gramatica_das_portas.py`, T`test_citacoes_de_requisito.py`, T`test_readme_acompanha_o_codigo.py`, T`test_vocabulario_da_convocacao.py`, T`interface/test_polish_da_056.py` e T`integration/convocacao/`.

  Conferir também `gh pr view 266 --json state`, porque a `065` define o teto dos identificadores globais.

## Phase 2: Foundational — app, tabelas, guardiões, timeout, endereço, chave e janela

**⚠️ Nenhuma história começa antes desta fase terminar.** É onde os guardiões globais de `R-015`
mudam, para que nenhum deles seja descoberto no fim da suíte de 15 minutos.

- [X] T002 [P] Em `backend/config/settings/base.py`, `EMAIL_TIMEOUT = int(os.getenv("EMAIL_TIMEOUT", "20"))`, com comentário: gap I-4, os quatro envios, os 120 s do gunicorn (`R-006`). Teste em T`unit/test_configuracao_de_correio.py`: o setting existe, é inteiro e chega ao backend SMTP do Django (`get_connection().timeout`)
- [X] T003 [P] Mover `destinatario_de` de `backend/processo_seletivo/convocacao/application/comunicar.py` para `backend/processo_seletivo/identidade/application/endereco.py`, sem mudar comportamento (data-model §3):
  - `comunicar.py` importa de lá e mantém o nome no `__all__` por reexportação;
  - rodar T`integration/convocacao/test_comunicacao.py` verde, sem edição
- [X] T004 [P] Settings da feature:
  - em `backend/config/settings/base.py`: `AVISOS_AOS_CANDIDATOS` (`== "true"`, padrão `"false"`), `AVISOS_LIMITE_POR_MINUTO=60`, `AVISOS_MAX_TENTATIVAS=3`, `AVISOS_INTERVALOS_DE_RETENTATIVA="5,15"`, `AVISOS_ALERTA_DE_PENDENTE_MIN=10`, `AVISOS_JANELA_DE_DESPACHO_HORAS=24`;
  - em `backend/config/settings/development.py` e `backend/config/settings/test.py`, a chave ligada;
  - acrescentar as variáveis comentadas a `backend/.env.example` (`R-005`, `R-013`, `R-016`)
- [X] T005 Criar o app A (`apps.py`, `__init__.py`, `models.py`, `domain/`, `application/`, `management/commands/`) e registrá-lo em `INSTALLED_APPS` de `backend/config/settings/base.py`
- [X] T006 Modelos em A`models.py`, conforme data-model §1:
  - `ModeloDeAviso`, mutável, com `delete()` que recusa;
  - `Aviso`, `PublicacaoDoAviso`, `DestinatarioDoAviso`, `TentativaDeEnvio`, `ResultadoDaTentativa` e `InterrupcaoDoAviso`, com `save()` que recusa linha existente e `delete()` que recusa sempre, no padrão de `convocacao/models.py:75-81`;
  - os `CHECK` e `UNIQUE` do data-model: `(aviso, inscricao)`, `(destinatario, numero)`, OneToOne do resultado e da interrupção, e nome do modelo único por escopo sem caixa;
  - o índice em `PublicacaoDoAviso.publicacao`
- [X] T007 Migration A`migrations/0001_initial.py`:
  - as tabelas;
  - gatilho `BEFORE UPDATE OR DELETE` nas seis append-only, e `BEFORE DELETE` em `ModeloDeAviso`, no padrão de `convocacao/migrations/0001_initial.py:27-47`;
  - sem importar `domain` nem `application` (`test_migrations_do_not_import_domain_or_application_code`)
- [X] T008 Em `backend/processo_seletivo/seguranca/papeis.py`, acrescentar as seis tabelas append-only a `TABELAS_APPEND_ONLY`. `ModeloDeAviso` fica fora (data-model §1.1). Rodar `provisionar_papeis`, `migrate` e `provisionar_papeis` e conferir **`40 de 40`**. T`integration/test_database_permissions.py` passa a cobrir as seis pela parametrização existente
- [X] T009 Em T`migrations/test_migrations.py`:
  - subir a contagem com o app `avisos` e a justificativa escrita, no idioma do arquivo;
  - acrescentar os sete gatilhos a `TRIGGERS_POR_APP["avisos"]` (memória "migrations têm contagem por app")
- [X] T010 [P] TU e TI de imutabilidade, em T`unit/avisos/test_append_only.py`, no padrão de T`unit/convocacao/test_append_only.py`:
  - `save` de linha existente e `delete` recusam nas seis;
  - `delete` de `ModeloDeAviso` recusa;
  - `UPDATE`/`DELETE` direto em SQL recusado pelo gatilho
- [X] T011 [P] A`domain/nomes.py`:
  - os códigos de recusa de contracts/telas.md, inclusive `aviso_envio_desabilitado`;
  - os resultados de tentativa (`ACEITA`, `FALHA_TEMPORARIA`, `FALHA_DEFINITIVA`, `INDETERMINADA`);
  - os estados derivados (data-model §2), as origens, os motivos e as elegibilidades
- [X] T012 [P] A`domain/variaveis.py`:
  - a lista fechada da `FR-1255`, com a coluna por origem de contracts/mensagem.md;
  - `{link_da_publicacao}` só com uma publicação citada;
  - a sintaxe `{nome}`, com `{{ }}` literal;
  - a validação que devolve a variável desconhecida ou sem valor, nomeada.

  TU em T`unit/avisos/test_variaveis.py`, com um caso por linha e por coluna da tabela, `{posicao}` e `{modalidade}` recusadas, e `{link_da_publicacao}` com duas publicações recusada
- [X] T013 [P] A`domain/mensagem.py`, composição pura (contracts/mensagem.md):
  - assunto e corpo resolvidos;
  - linha de retificação com as datas;
  - rodapé com `{destino_oficial}`, na ordem link → referência → página;
  - frase do prazo na chamada;
  - `PORTAL_ATENDIMENTO`;
  - só `{nome_do_candidato}` por resolver no texto congelado;
  - a mensagem final com um `To`, sem `Cc`/`Bcc`, e `Auto-Submitted: auto-generated`.

  TU em T`unit/avisos/test_mensagem.py`
- [X] T014 [P] A`domain/estado.py`, derivação pura do estado do destinatário e do aviso (data-model §2), inclusive a janela de despacho (`R-016`), a chave desligada (ninguém elegível ao despacho) e o aviso concluído. TU em T`unit/avisos/test_estado.py`, com um caso por linha da tabela e o limite exato da janela
- [X] T015 [P] A`domain/resposta.py`, classificação pela fase SMTP (`R-004`). TU em T`unit/avisos/test_resposta.py`, com um caso por linha da tabela de `R-004`:
  - `SMTPSenderRefused` e `SMTPRecipientsRefused` 4xx e 5xx;
  - `SMTPDataError` no `DATA` e na confirmação final;
  - código `-1`, código 999 e código 250 em `SMTPDataError`, todos `INDETERMINADA`;
  - `SMTPServerDisconnected`, `socket.timeout` e `OSError`;
  - `ValueError` na preparação, `FALHA_DEFINITIVA`;
  - retorno 0
- [X] T016 Em I`identidade.py`, `aviso:enviar` nos papéis publicador e gestor, com comentário (`D-004`, `FR-1275`). Teste em T`authorization/test_papel_do_aviso.py`, junto dos de `test_visao_institucional.py`: `aviso:enviar` não traz `resultado:publicar`, `comissao:gerir` nem outra capacidade, e o papel julgador não a tem
- [X] T017 A`application/comando.py`, `comando_de_aviso` (`R-009`):
  - `command_context`;
  - `ProcessoSeletivo.select_for_update()` filtrado pelo escopo, que responde 404 para outra unidade;
  - autorização pela origem: resultado = `actor.can("aviso:enviar")` ou `pode_gerir_comissao`; chamada = `pode_gerir_comissao`;
  - `ensure_processo_accepts_changes`, que vira `aviso_processo_em_estado_final`;
  - recusa `aviso_envio_desabilitado` com a chave desligada (`FR-1282`);
  - `reservar` da idempotência.

  TI em T`integration/avisos/test_autorizacao.py`, por papel × origem × escopo, com a presidência ativa, a inativa e o publicador na chamada
- [X] T018 [P] Em T`test_gramatica_das_portas.py`, `VIEWS` passa a varrer também I`avisos.py`, com comentário: a varredura literal deixaria as views novas escaparem (`R-015`). Criar I`avisos.py` vazio, com docstring, para que o guardião o encontre desde já
- [X] T019 [P] (`FR-1280`) Criar A`application/despacho.py` só com a docstring da 4ª situação e a constante `REVISAO_DA_FR_084_PELA_066 = "2026-10-09"`. Em T`test_situacoes_de_mensagem.py`:
  - `SITUACOES` ganha o módulo;
  - `test_sao_tres_situacoes…` vira quatro, renomeado;
  - a conferência da spec exige "revisada pela `066`", a data e "quatro" no trecho da `FR-084`, e continua exigindo a redação anterior

**Checkpoint**: o app existe, as tabelas estão protegidas em duas camadas, `provisionar_papeis` diz
`40 de 40`, e todo guardião global já conhece a feature. Nenhuma tela mudou.

## Phase 3: User Story 1 — Avisar que o resultado foi publicado (P1) 🎯 MVP

**Goal**: FR-1241 a FR-1250, FR-1252 a FR-1257, FR-1259, FR-1261, FR-1263, FR-1265 a FR-1272,
FR-1274, FR-1276 a FR-1279, FR-1282, FR-1283, UX-171 a UX-176. **Independent Test**: resultado
publicado em duas listas, com uma inscrição nas duas; avisar e despachar; cada inscrição considerada
recebe exatamente uma mensagem.

- [X] T020 [US1] A`application/destinatarios.py`, `universo_do_resultado(edital, marco_id, natureza)`:
  - publicações vigentes da natureza que nenhum `PublicacaoDoAviso` de aviso `PRIMEIRO_AVISO` citou (`D-002`);
  - `SituacaoDivulgada` distinta por inscrição;
  - o endereço por `identidade.application.endereco.destinatario_de` em lote, sem N+1;
  - `retificadora` quando alguma publicação tem `publicacao_anterior`
- [X] T021 [US1] A`application/previa.py`, prévia sem gravar nada:
  - o ato citado e a origem por extenso;
  - as contagens com e sem endereço;
  - a mensagem composta para a primeira pessoa da lista, com "ver outra";
  - a assinatura `canonical_sha256` de `R-010`, sem o texto
- [X] T022 [US1] A`application/confirmar.py`, `confirmar_aviso_do_resultado`, dentro de `comando_de_aviso`:
  - confere a assinatura, que vira `aviso_previa_defasada`;
  - valida as variáveis pela origem;
  - recusa `aviso_sem_publicacao_nova` e `aviso_sem_elegivel`;
  - congela o texto com links absolutos passados pela view (`R-007`);
  - grava `Aviso`, `PublicacaoDoAviso` e `DestinatarioDoAviso` em `bulk_create`;
  - `auditar` com ato citado, origem, contagens e `correlation_id`, sem endereços (`FR-1278`);
  - `finish` da idempotência
- [X] T023 [US1] A`application/despacho.py`, completar pelo contrato `contracts/despacho.md`:
  - passos 0 a 6, com a chave, a trava global (`pg_try_advisory_lock`) e as órfãs;
  - a seleção dentro da janela, ordenada e limitada;
  - a abertura da conexão por `get_connection()`;
  - por destinatário, a trava do aviso (`pg_advisory_xact_lock`), a conferência da interrupção, a `TentativaDeEnvio` confirmada, a preparação antes da rede, `send_messages`, o `ResultadoDaTentativa` por `domain/resposta.py` e a parada na indeterminada;
  - o resumo sem dado pessoal
- [X] T024 [US1] A`management/commands/despachar_avisos.py`, com `--limite`. A saída é diferente de 0 só quando a conexão não abre
- [X] T025 [US1] A`application/selectors.py`:
  - o histórico do aviso, com contagens por estado em consultas constantes e destinatários paginados;
  - a linha de estado do último aviso por publicação e natureza (`UX-175`);
  - o alerta de pendente antigo (`FR-1272`);
  - a lista de avisos do Edital
- [X] T026 [US1] Views em I`avisos.py` e rotas em I`urls.py`, para `aviso-do-resultado` (GET prévia, POST confirmação), `aviso` e `avisos-do-edital` (contracts/telas.md):
  - POST-redirect-GET;
  - `marcar_como_privada` na prévia;
  - links absolutos por `request.build_absolute_uri`;
  - com a chave desligada, a prévia só com a explicação (`FR-1282`)
- [X] T027 [US1] Acrescentar a `specs/033-navegacao-por-capacidade/inventario-das-negativas.md` uma linha por função de I`avisos.py` com `raise Http404`, classificada. *Na implementação, nenhuma view de I`avisos.py` levanta `Http404`: as recusas são `DomainError`, que o middleware traduz em página, e o inventário não ganhou linha. O guardião (T018) passa a acusar a primeira que aparecer.*
- [X] T028 [US1] Templates em I`templates/interface/`:
  - `aviso_previa.html`: origem, contagens, `<ol class="consequencias">`, assunto com a orientação fixa (`FR-1258`), corpo com as variáveis ao lado (`UX-176`), rodapé visível e não editável, aviso de irreversibilidade e "Enviar a N pessoas" (`UX-173`);
  - `aviso.html` e `avisos_do_edital.html`;
  - em `publicacoes_do_marco.html`, o botão "Avisar candidatos" e a linha de estado por natureza, e nenhum botão na publicação sucedida (`UX-174`)
- [X] T029 [US1] Na folha da gestão, as regras de toda classe nova (memória "classe no template exige regra na folha"), com `@media` em linhas separadas (T`interface/test_polish_da_056.py`). 375 px sem rolagem horizontal
- [X] T030 [US1] Criar T`test_vocabulario_do_aviso.py`, com lista literal dos templates da feature:
  - nenhum "entregue", "recebida", "lida", "notificação oficial" (`UX-171`, `UX-172`);
  - "aceita pelo servidor de correio" presente no histórico;
  - rodar T`test_vocabulario_da_convocacao.py`, que a Phase 5 vai tocar.

  A varredura de acessibilidade (T`interface/test_acessibilidade.py`) usa `glob` sobre os templates da gestão e alcança os novos sem edição: rodá-la (SC-486)
- [X] T031 [US1] TI em T`integration/avisos/test_aviso_do_resultado.py`, cenários 1 a 5 da US1:
  - deduplicação AC + reserva;
  - `SEM_POSICAO` incluído, sem dizê-lo no corpo;
  - sem endereço registrado e fora do envio;
  - confirmação que não envia nada, com zero mensagens no `mail.outbox` antes do despacho;
  - "nenhuma publicação nova", e o reenvio sem justificativa recusado (`FR-1262`);
  - nenhuma mensagem para fora do ato, e uma só por inscrição (SC-481);
  - prévia defasada;
  - idempotência no duplo POST;
  - publicar não dispara aviso (`FR-1243`)
- [X] T032 [US1] TI em T`integration/avisos/test_despacho.py`, caminho feliz pelo comando:
  - uma mensagem por destinatário elegível;
  - um `To` só;
  - o texto confirmado com o nome resolvido;
  - `ACEITA` registrada;
  - a chave desligada sem tentativa;
  - a janela vencida que expira sem envio (`FR-1283`)
- [X] T033 [US1] TT em T`interface/test_avisos.py`:
  - o botão na publicação vigente e não na sucedida;
  - o rótulo "Enviar a N pessoas";
  - a orientação do assunto;
  - o rodapé não editável;
  - escopo de outra unidade com 404;
  - a chave desligada com explicação e sem formulário
- [X] T034 [US1] TI em T`integration/avisos/test_orcamento_do_aviso.py`, no padrão de T`integration/requerimentos/test_orcamento_de_consulta.py`: o histórico do aviso com 50 e com 500 destinatários faz o mesmo número de consultas; a confirmação com 1.000 responde sem envio e em menos de 2 s, medido no teste (SC-482)

**Checkpoint**: o pedido do setor para resultados funciona de ponta a ponta, com o correio de
desenvolvimento.

## Phase 4: User Story 2 — Avisar sobre a publicação retificadora (P1)

**Goal**: FR-1248, FR-1255a, FR-1243, D-002 na retificação. **Independent Test**: avisar, retificar
uma lista, avisar de novo.

- [X] T035 [US2] Em A`application/confirmar.py` e A`domain/mensagem.py`, garantir a linha fixa de retificação com as datas das publicações retificadas (`FR-1248`), e nenhum texto do sistema que afirme mudança de situação
- [X] T036 [US2] TI em T`integration/avisos/test_aviso_da_retificacao.py`, cenários 1 a 4 da US2:
  - só a sucessora é nova, e os destinatários são os dela;
  - a linha fixa presente;
  - o primeiro aviso intacto (assunto, corpo, destinatários e tentativas);
  - retificação sem gesto não envia nada;
  - **link histórico** (`FR-1255a`): o aviso que cita uma publicação só traz o link dela, a publicação é sucedida, e o GET do link congelado responde e aponta a vigente

**Checkpoint**: a retificação de resultado é avisada sem reenvio geral e sem afirmar mudança.

## Phase 5: User Story 3 — Avisar os convocados de uma chamada publicada (P2)

**Goal**: FR-1245, FR-1251, FR-1252, D-003, D-004 (chamada), UX-178. **Independent Test**: num
Perfil `PUBLICATION`, três convocações com a mesma referência, uma com desistência.

- [X] T037 [US3] Em A`application/destinatarios.py`, `universo_da_chamada(edital, marco_id, lista_id, comunicacao_id)`:
  - a referência da comunicação âncora;
  - todas as convocações do recorte com `ComunicacaoEmitida(PUBLICATION, ENVIADA)` daquela referência, inclusive sucedidas, desfechadas e vencidas;
  - a elegibilidade pelos seletores existentes (`desfecho_de`, `estado_de`, a vigência), com o motivo;
  - a recusa `aviso_chamada_por_mensagem_individual` pela `forma_declarada` da versão citada
- [X] T038 [US3] Em A`application/previa.py` e A`application/confirmar.py`, a origem `CHAMADA`:
  - a assinatura cobre recorte, referência e elegibilidades;
  - `DestinatarioDoAviso` grava todo o universo com `convocacao` e `elegibilidade`;
  - recusa `aviso_sem_elegivel`
- [X] T039 [US3] View e rota `aviso-da-chamada` em I`avisos.py` e I`urls.py`, com a linha no inventário de negativas. Em I`templates/interface/convocacao.html`, no cartão da chamada por publicação, "Avisar os convocados desta publicação", só com `PUBLICATION`. *Na implementação, a ação fica numa seção própria da tela, uma linha por referência publicada, e não um botão por cartão: quarenta chamadas de um mesmo gesto são uma publicação só.* Na prévia, o universo e, à parte, quem recebe e quem não é elegível, com o motivo (`UX-178`)
- [X] T040 [US3] Rodar e adaptar T`test_vocabulario_da_convocacao.py` (lista literal `DA_019`, que inclui `convocacao.html`) sem afrouxar. Se o texto novo colidir com termo proibido ali, trocar o texto, e não a regra
- [X] T041 [US3] TI em T`integration/avisos/test_aviso_da_chamada.py`, cenários 1 a 5 da US3:
  - universo de três, envio a dois, um não elegível com o motivo;
  - histórico com os três e nenhum registro de convocação alterado;
  - todas vencidas, recusado com explicação;
  - `INDIVIDUAL_MESSAGE` sem ação e recusado;
  - publicador sem base de comissão respondido como inexistente

**Checkpoint**: o exemplo "chamada de suplentes" do setor está atendido.

## Phase 6: User Story 4 — Modelos da unidade (P2)

**Goal**: FR-1260, FR-1260a, FR-1261, FR-1277 (modelos), D-008. **Independent Test**: os três
iniciais presentes; editar, inativar e reativar; o aviso enviado não muda.

- [X] T042 [P] [US4] A`domain/modelos_iniciais.py` com os três textos de contracts/mensagem.md, assunto "Processo Seletivo Ifes — Nova publicação disponível". TU: os três passam pela validação de variáveis, e o terceiro só usa variáveis da chamada
- [X] T043 [US4] A`application/modelos.py`:
  - criar, editar, inativar e reativar, com `record_event` do estado anterior e do novo (`FR-1277`);
  - `garantir_modelos_iniciais(unidade)`, que **só insere**, só se a unidade não tiver modelo inicial, e nunca relê nem atualiza texto (`R-012`).

  Chamá-la de `backend/processo_seletivo/unidades/application/sincronizacao.py`, dentro da transação que já trava as unidades. Fazer a linha impressa do `make preparar` dizer `Modelos de aviso: C criados`. ~~Chamá-la também em `garantir_o_cefor`~~ — **desvio deliberado na implementação**: a fixture é autouse em todo caso que toca o banco, e gravar três modelos e três eventos de trilha em cada um derrubaria os testes que contam registros de auditoria. Os casos que precisam dos modelos iniciais chamam `garantir_modelos_iniciais()` explicitamente
- [X] T044 [US4] Views, rotas e templates `modelos-de-aviso`, `modelo-de-aviso-novo`, `modelo-de-aviso` e `modelo-de-aviso-situacao`:
  - em I`avisos.py`, I`urls.py`, I`templates/interface/modelos_de_aviso.html` e `modelo_de_aviso.html`;
  - porta `aviso:enviar`;
  - linhas no inventário de negativas;
  - "Salvar como novo modelo" na confirmação do aviso (`FR-1261`), sem tocar no modelo de origem;
  - o seletor da prévia só com os ativos
- [X] T045 [US4] TI em T`integration/avisos/test_modelos.py`, cenários 1 a 6 da US4:
  - os três iniciais na primeira sincronização;
  - inativados e ressincronizados, continuam inativos e sem cópia;
  - **duas sincronizações simultâneas**, por thread, sem duplicata;
  - texto editado preservado depois de nova sincronização;
  - edição sem efeito no aviso enviado;
  - `{posicao}` recusada;
  - inativo fora do seletor;
  - outra unidade respondida como inexistente (SC-487, com T017 e T033);
  - presidência usa os modelos e não os administra

**Checkpoint**: o "salvar os modelos de texto" do setor está atendido.

## Phase 7: User Story 5 — Envio que sobrevive a falha, queda e engano (P1)

**Goal**: FR-1264, FR-1266 a FR-1273, FR-1281, FR-1282, FR-1283, D-005, D-006, D-009, UX-177.
**Independent Test**: servidor simulado que falha, aceita e derruba, devolve 0, e duas execuções
simultâneas.

- [X] T046 [US5] A`application/interromper.py`, numa transação com `pg_advisory_xact_lock(aviso)`. Grava `InterrupcaoDoAviso` com motivo, e recusa `aviso_concluido`. View `aviso-interromper` e template `aviso_interromper.html` em I, com quantas já foram aceitas e "não podem ser recuperadas" (`UX-177`), e a linha no inventário de negativas
- [X] T047 [US5] Reenvio como aviso filho (`R-011`, `FR-1262`, `FR-1264`), em A`application/confirmar.py`:
  - `REENVIO_DE_FALHAS`, com os destinatários em falha definitiva e em expirada sem envio, sem justificativa e com o texto do anterior;
  - `REENVIO_JUSTIFICADO`, com indeterminadas, interrompidos antes do envio ou a publicação inteira já avisada, com justificativa obrigatória e texto editável numa prévia nova.

  View `aviso-reenviar` em I`avisos.py`, com prévia, confirmação e a linha no inventário. Recusa com a chave desligada. TI em T`integration/avisos/test_reenvio.py`, com um caso por linha da tabela de `R-011` e o caso "interrompi com o modelo errado e mando o certo a todos"
- [X] T048 [US5] Backends de correio simulados em T`fixtures/correio.py`, no padrão de `tests.unit.convocacao.test_mensagem.CorreioQueFalha`:
  - um que recusa a abertura;
  - um que levanta cada exceção de `R-004`;
  - um que devolve 0;
  - um que "aceita e derruba", com `SMTPServerDisconnected` depois do conteúdo
- [X] T049 [US5] TI em T`integration/avisos/test_despacho_falhas.py`, cenários 2, 3, 7 e 10 da US5:
  - abertura recusada, sem tentativa e com saída diferente de 0;
  - falha temporária retentada só depois do intervalo e definitiva no limite;
  - recusa 5xx definitiva;
  - aceita-e-derruba indeterminada, que para a execução;
  - órfã encontrada pela execução seguinte marcada como indeterminada e não repetida;
  - limite por minuto respeitado;
  - **500 destinatários com o limite 60 concluem em 9 execuções** (≤ 15 min de timer), contra servidor simulado (SC-483);
  - `detalhe_tecnico` sem endereço nem nome em todo resultado de falha (`FR-1279`);
  - nenhuma tentativa indeterminada repetida e nenhuma duplicada, nos cenários desta tarefa e de T050 (SC-484)
- [X] T050 [US5] TI `transaction=True` em T`integration/avisos/test_despacho_concorrencia.py`, cenários 1, 4 e 5 da US5:
  - duas execuções em threads, uma sai pela trava, sem tentativa duplicada;
  - a inserção concorrente da mesma `(destinatario, numero)` barrada pelo `UNIQUE`;
  - aviso interrompido com 200 pendentes, nenhum tentado;
  - **interrupção durante a execução**, por um backend que interrompe o aviso ao receber a 2ª mensagem: nenhuma tentativa começa depois
- [X] T051 [US5] TI em T`integration/avisos/test_chave_e_janela.py`, cenários 8 e 9 da US5:
  - chave desligada: confirmação recusada, reenvio recusado, despacho sem tentativa, histórico e modelos acessíveis;
  - religada dentro da janela, o pendente sai;
  - religada fora dela, expira sem envio;
  - timer "parado" (relógio adiantado), expira sem envio
- [X] T052 [US5] Guardião da `FR-1281` em T`test_avisos_sem_correio_real.py`. Varre por `tokenize` (a varredura lê o código, não a prosa) os módulos de A e falha se algum:
  - importar `smtplib` para abrir conexão;
  - passar `backend=` a `get_connection`;
  - instanciar backend de correio diretamente.

  Incluir um caso que prova que a varredura enxerga o padrão (SC-488)
- [X] T053 [US5] TT em T`interface/test_avisos.py`:
  - interromper diz quantas foram aceitas e que não voltam;
  - o histórico mostra "resultado indeterminado" com o caminho do reenvio justificado;
  - o alerta de despacho parado aparece depois do limite

**Checkpoint**: o contrato de envio que o usuário exigiu está provado contra PostgreSQL.

## Phase 8: Polish & Cross-Cutting Concerns

- [ ] T054 [P] `doc/implantacao-em-producao-ubuntu.md`:
  - `ps-avisos.service` e `ps-avisos.timer`, da contracts/despacho.md, na §21;
  - `EMAIL_TIMEOUT` na §16, com o gap I-4 resolvido;
  - `AVISOS_AOS_CANDIDATOS` desligada até a validação de LGPD e do correio;
  - conferência de `systemctl list-timers`, porque o timer desabilitado não alerta (risco do plano);
  - o limite da conta de envio a obter do setor de correio
- [ ] T055 [P] `AGENTS.md`:
  - `40 de 40` no parágrafo do `provisionar_papeis`, e "o `M` continua 34" vira 40;
  - a linha `Modelos de aviso` do `make preparar`;
  - a chave `AVISOS_AOS_CANDIDATOS` em *Subir o ambiente*;
  - os números da suíte, medidos em T058, com falhas e pulados juntos
- [ ] T056 [P] Atualizar a linha da `066` em `README.md`, de "especificada e planejada" para o que foi entregue
- [ ] T057 Criar `specs/066-avisos-complementares/rastreabilidade.md`, com uma linha por FR, SC e UX, inclusive `FR-1255a` e `FR-1260a`, apontando o lugar no código e o teste que o prende (T`test_citacoes_de_requisito.py::test_a_matriz_de_rastreabilidade_cobre_todo_requisito_da_feature`)
- [ ] T058 `cd backend && make lint check test-pg DB_NAME=ps_066`, com `ruff check` **e** `ruff format --check`, sem editar nada durante a suíte. Registrar passando, pulados e tempo. Os pulados não mudam, e qualquer pulado novo é conferido um a um
- [ ] T059 Criar `specs/066-avisos-complementares/verificacao.md`: o roteiro de quickstart.md §1 a §5a pela interface do ator, com o correio de desenvolvimento, e capturas a 1280 × 900 e 375 px (Princípio VI). Medir e registrar o tempo de compor e confirmar um aviso de resultado a partir de um modelo, no roteiro §1 (SC-485, meta de 3 minutos)
- [ ] T060 Antes de integrar:
  - `gh pr view 266 --json state`;
  - medir de novo o teto de FR, SC e UX em todas as worktrees;
  - se a `065` tiver crescido para dentro da faixa da 066, renumerar antes do merge;
  - conferir que o `M` e a contagem de migrations não colidem com a 065 mergeada

---

## Dependencies & Execution Order

- **Setup (T001)** → **Foundational (T002–T019)** → as histórias.
- **US1 (T020–T034)** é a base das outras. US2, US3 e US5 usam o despacho, a confirmação e as telas
  da US1.
- **US2 (T035–T036)** depende só da US1.
- **US3 (T037–T041)** depende da US1, porque reusa prévia, confirmação e despacho. É independente da
  US2.
- **US4 (T042–T045)** depende da Foundational. A parte de "salvar como novo modelo" depende da
  confirmação da US1 (T022, T026). O resto pode correr em paralelo à US1.
- **US5 (T046–T053)** depende da US1. Ela prova e completa o despacho; T048 pode começar assim que
  T023 existir.
- **Polish (T054–T060)** depois de todas. T058 roda depois de T055 a T057 estarem escritos, e T055
  recebe os números de T058.

Dentro de cada história: domínio → aplicação → views e rotas → templates e folha → testes de tela.
Os testes TU de domínio da Foundational vêm junto da função que testam.

## Parallel Opportunities

- **Foundational**: T002, T003 e T004 em arquivos distintos. Depois de T005–T007, correm em paralelo
  T010, T011, T012, T013, T014 e T015 (um módulo de domínio cada), T018 e T019.
- **US4 × US1**: T042 e T043 podem correr enquanto a US1 faz as telas.
- **US5**: T048 em paralelo a T046 e T047.
- **Polish**: T054, T055 (exceto os números) e T056.

```text
# Exemplo — Foundational, depois da migration:
T011 nomes.py   T012 variaveis.py   T013 mensagem.py   T014 estado.py   T015 resposta.py
T018 guardião das portas   T019 guardião das situações
```

## Implementation Strategy

- **MVP = Setup + Foundational + US1.** Já atende o pedido do setor para resultado preliminar e
  definitivo, com o envio robusto do contrato. As falhas são classificadas desde T023. A US5 prova
  os casos difíceis e acrescenta interrupção e reenvio.
- **Incremento 2**: US2 e US5, que são P1.
- **Incremento 3**: US3 e US4, que são P2.
- **Integração**: só depois de T060, com a `065` resolvida.

**A chave fica desligada em produção** até a validação institucional de LGPD e da infraestrutura de
correio (`D-009`). Implantar a 066 não liga o envio.
