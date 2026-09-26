---

description: "Tarefas da 044 — recorte transversal do documento exigido"
---

# Tasks: Recorte transversal do documento exigido

**Input**: Design documents from `specs/044-recorte-transversal-documental/`

**Prerequisites**: [plan.md](./plan.md) · [spec.md](./spec.md) · [research.md](./research.md) ·
[data-model.md](./data-model.md) · [contracts/](./contracts/) · [quickstart.md](./quickstart.md)

**Tests**: **incluídos**. A Constituição exige cobertura específica para documentos, publicação,
retificação e concorrência. As garantias da lista moram no banco, e os testes que as provam são
`transaction=True`. Teste antes da implementação em cada fase: ele deve falhar primeiro.

**Organization**: por história. A US4 não tem fase de gravação própria: a reconstrução entra com a
lista (US2), porque sem ela as inscrições existentes quebrariam a Mesa no primeiro deploy
(`plan.md`, *Ordem de construção*).

**Caminhos**: relativos à raiz do repositório. `B/` = `backend/processo_seletivo/`, `T/` =
`backend/tests/`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode correr em paralelo, porque o arquivo é distinto e não há dependência pendente
- **[Story]**: `US1`…`US4`. Setup, Foundational e Polish não têm rótulo

---

## Phase 1: Setup

**Purpose**: a linha de base, e o ambiente que não engana.

- [X] T001 Conferir `uv run python manage.py migrate --check` com o `DB_NAME` da worktree, e rodar as famílias que esta feature toca: `T/unit/inscricoes/test_aplicabilidade.py`, `T/unit/editais/test_validacao_inscricao.py`, `T/unit/publicacoes/test_pdf_documentos_exigidos.py`, `T/interface/test_compor_inscricao.py`, `T/interface/test_retificar_documentos.py`, `T/interface/test_mesa.py`, `T/interface/test_mesa_modelo_exigido.py`, `T/integration/interface/test_inscricoes_recebidas.py`, `T/integration/interface/test_inscricoes_em_escala.py`, `T/integration/inscricoes/test_submissao.py`, `T/migrations/test_migrations.py`. Registrar a contagem
- [X] T002 Conferir o estado do PR #167 (`claude/instrucao-e-facultativo`). Se já estiver na `main`, trazer a `main` para o branch antes da Fase 5, porque ele mexe em `B/avaliacoes/application/mesa.py` e `B/interface/templates/interface/mesa_inscricao.html`

**Checkpoint**: linha de base verde, e a posição do PR #167 conhecida.

---

## Phase 2: Foundational — a aplicabilidade que devolve o veredito

**Purpose**: a regra única (`FR-705`). Bloqueia as quatro histórias. Nenhum comportamento muda
ainda: nenhum conteúdo tem `modalityCode`.

### Testes

- [X] T003 [P] Em `T/unit/inscricoes/test_aplicabilidade.py`, testes de `aplicabilidade(conteudo, profile_id=…, modality_id=…)`: um veredito por documento, na ordem declarada; `OBRIGATORIO`/`FACULTATIVO`/`NAO_SE_APLICA`; a forma e os parâmetros do recorte para as quatro formas existentes; candidato sem modalidade; e `aplicaveis(conteudo, …)` igual ao filtro dos não-`NAO_SE_APLICA` (`data-model.md` §3, `research.md` R-003)
- [X] T004 [P] No mesmo arquivo, testes do recorte por código: se aplica quando a Modalidade escolhida, **no Perfil da inscrição**, tem o código; não se aplica em Perfil sem aquele código; não se aplica sem modalidade (`FR-701`). E o código presente num Perfil só: equivale ao recorte exato, e nada é acusado
- [X] T005 [P] No mesmo arquivo, testes do predicado da divergência: "Todos os Perfis" + Modalidade do C1, com o C2 tendo Modalidade de mesma denominação, marca `divergente_do_publicado` para a inscrição que concorre, no C2, na Modalidade daquela denominação, e não para a AC do C2 nem para as do C1 (`FR-727`, `D-007`, `R-004`)

### Implementação

- [X] T006 Em `B/editais/domain/documentos.py`, criar `Recorte`, `Veredito` e as constantes de situação e de forma. Implementar `aplicabilidade(conteudo, *, profile_id, modality_id)`, que lê `modalityCode` resolvendo o código da Modalidade escolhida no Perfil da inscrição. Reescrever `aplicaveis(conteudo, *, profile_id, modality_id)` como filtro sobre ela. Atualizar o docstring do módulo: são cinco formas (`R-003`)
- [X] T007 Extrair para `B/editais/domain/documentos.py` o predicado de `_recorte_que_o_documento_publicado_alarga` (`B/editais/domain/validation.py`): os Perfis cuja Modalidade tem a mesma denominação da Modalidade apontada. Fazer a validação e `aplicabilidade` usarem o mesmo predicado, sem mudar a mensagem ainda (`R-004`)
- [X] T008 Em `B/editais/domain/documentos.py`, implementar `razao_legivel(veredito, conteudo)` com as cinco frases de `data-model.md` §3, o prefixo "Não se aplica:" e o acréscimo da divergência (`UX-081`). Testes em `T/unit/inscricoes/test_aplicabilidade.py`
- [X] T009 Trocar os chamadores de `aplicaveis` para a assinatura nova, passando o conteúdo: `B/inscricoes/application/rascunho.py` (`requisitos_da_inscricao`, `_documentos_inaplicaveis`, `descartes_por_mudanca_de_modalidade`), `B/inscricoes/application/submissao.py` (`documentos_que_a_retificacao_invalida`) e `B/portal/views.py` (`_documentos_anunciados`). Rodar as famílias de T001

**Checkpoint**: a regra devolve o veredito completo, e tudo que existia continua igual.

---

## Phase 3: User Story 1 — Exigir um documento de toda a modalidade, numa linha só (P1) 🎯 MVP

**Goal**: quem compõe declara "PcD em todos os Perfis" numa linha. O PDF, o cartão e a inscrição
dizem o mesmo.

**Independent Test**: `quickstart.md`, cenário A, passos 1 a 6.

### Testes

- [X] T010 [P] [US1] Criar `T/contract/test_elevacao_degrau_17.py` no molde de `T/contract/test_elevacao_degrau_9.py`. Conteúdo da versão 16 elevado ganha `modalityCode: null` em cada documento; o conteúdo literal não muda; elevar duas vezes é idempotente (`R-002`, `FR-725`)
- [X] T011 [P] [US1] Em `T/unit/editais/test_validacao_inscricao.py`, testes dos achados. Um para cada:
  - `document_requirement_scope_conflict`;
  - `document_requirement_modality_code_unknown`;
  - `document_requirement_modality_code_general`, com a ampla declarada em um Perfil só;
  - `modality_code_name_divergent`: **um** achado com 16 Perfis e 1 divergente, e com 8 contra 8; nenhum com as denominações iguais; nenhum com código repetido e sem documento transversal (`D-001`); diferença de maiúscula acusa, espaço nas pontas não (`D-005`); percentual diferente não acusa (`FR-707`).

  Mais a mensagem da #161 com as três saídas (`FR-706`, `FR-707`, `FR-708`, `SC-266`, `contracts/recorte-transversal.md` §3 e §4)
- [X] T012 [P] [US1] Criar `T/unit/editais/test_documentos_recusas.py`, com as recusas na gravação: `modalityCode` com Perfil, com Modalidade exata, código inexistente, código da ampla. Cada recusa tem `campo="modalityCode"` (`FR-702` a `FR-704`). E a recusa vinda da **etapa Perfis**: declarar ampla, ou remover de todos os Perfis, a Modalidade de um código referido é recusado com mensagem que nomeia o documento. Seguir o precedente de `modalityId` ao reportar na tela (`FR-724`, `D-010`)
- [X] T013 [P] [US1] Em `T/unit/publicacoes/test_pdf_documentos_exigidos.py`: dois documentos com o mesmo código saem num grupo só, *"Dos candidatos concorrentes na modalidade {denominação}:"*, sem Perfil; o facultativo leva *"(facultativo)"*; os grupos exatos não mudam (`FR-712`, `FR-713`)
- [X] T014 [P] [US1] Em `T/interface/test_compor_inscricao.py`, testes do seletor:
  - o grupo "Em todos os Perfis" vem antes dos pares, com o rótulo de `UX-080` e a contagem "n de N";
  - a ampla declarada não aparece;
  - o valor `codigo:PcD` grava `modalityCode="PcD"` e `modalityId=None`;
  - Perfil + código é recusado com a mensagem ancorada no campo, preservando o que foi digitado;
  - o fragmento de linha nova conhece os códigos
- [X] T015 [P] [US1] Em `T/integration/inscricoes/test_submissao.py` (ou num arquivo novo vizinho, se ele passar de tamanho razoável), com um Edital publicado de C1 e C2 e o laudo em "PcD em todos os Perfis": o PcD do C2 é recusado sem o laudo (`missing_required_documents`) e envia com ele; o AC não recebe o pedido; o cartão público dos dois Perfis anuncia o laudo; trocar a modalidade do rascunho de PcD para AC descarta o laudo anexado, e de AC para PcD passa a pedi-lo; um Perfil C3 com PcD, acrescentado por Retificação, passa a pedir o laudo sem linha nova (`FR-709` a `FR-711`, `SC-262`)
- [X] T016 [P] [US1] Em `T/unit/editais/test_reaproveitamento.py`: `modalityCode` atravessa o `remapear` sem mudança; e, num Edital novo sem Perfil com aquele código, a publicação acusa `document_requirement_modality_code_unknown` (`R-012`)

### Implementação

- [X] T017 [US1] Em `B/editais/models/documentos.py`, acrescentar `modalidade_codigo` (`CharField(max_length=100, null=True, blank=True)`) e a restrição `ck_documento_recorte_exclusivo`. Criar `B/editais/migrations/0022_documento_modalidade_codigo.py` (`data-model.md` §1 e §5)
- [X] T018 [US1] Em `T/migrations/test_migrations.py`, subir `"editais": 21 → 22` nos guardiões da `017` e da `022`, com a justificativa ao lado, no tom das existentes (`R-013`)
- [X] T019 [US1] Em `B/editais/domain/documentos.py`, `_validate_aplicabilidade` recusa as quatro situações de T012 na gravação. Para a ampla, lê `generalCompetitionModalityId` dos Perfis do payload
- [X] T020 [US1] Em `B/editais/application/draft.py`, persistir `modalidade_codigo` em `replace_draft` e relê-lo onde o rascunho vira dicionário. Em `B/editais/api/serializers.py`, `DocumentRequirementSerializer` ganha `modalityCode = CharField(required=False, allow_null=True, max_length=100)`
- [X] T021 [US1] Versão canônica: `SCHEMA_VERSION = 17` em `B/shared/canonical.py`; `DEGRAUS_DE_DOCUMENTO[17] = {"modalityCode": None}` em `B/publicacoes/domain/elevacao.py`; `Campo("modalityCode", str, admite_nulo=True)` em `DOCUMENTO_EXIGIDO_PUBLICADO` (`B/editais/domain/validation.py`); `_document_requirements` em `B/publicacoes/application/publish_edital.py` escreve o campo. Rodar T010 e as famílias `T/contract/test_elevacao_degrau_*.py`
- [X] T022 [US1] Em `B/editais/domain/validation.py`, `_coerencia_dos_documentos_exigidos` emite os quatro achados de `research.md` R-007. A coerência de denominação sai numa passada à parte, que agrupa por código referido e emite um achado por código com o caminho em `/profiles`. A mensagem de `_recorte_que_o_documento_publicado_alarga` ganha a terceira saída (`contracts/recorte-transversal.md` §4)
- [X] T023 [US1] Em `B/interface/views.py`, `DESTINO_POR_CODIGO` manda `modality_code_name_divergent` para a etapa Perfis; os outros três seguem o destino de `documentRequirements` — *feito sem linha nova: o achado aponta `/profiles`, e o roteamento por coleção já o leva a Perfis*
- [X] T024 [P] [US1] Em `B/publicacoes/infrastructure/pdf.py`, a chave do grupo em `_documentos_exigidos` passa a `(profileId, modalityId, modalityCode)`, e `_titulo_do_grupo` escreve o título por código com a denominação de qualquer Perfil que o tem (`R-008`)
- [X] T025 [P] [US1] Em `B/interface/revisao.py`, `_alcance` descreve o recorte por código com a mesma frase do PDF
- [X] T026 [US1] Em `B/interface/forms.py`:
  - `alcance_da_aplicabilidade` devolve também os códigos (rótulo, "n de N", fora a ampla, pela coluna `PerfilVaga.modalidade_ampla_concorrencia`);
  - `ler_inscricao` separa `codigo:` de UUID;
  - `documentos_do_edital` e `documentos_persistidos` passam `modalityCode` nos dois sentidos (`R-009`)
- [X] T027 [US1] Em `B/interface/templates/interface/_documento.html`, os dois `<optgroup>` ("Em todos os Perfis", depois "Modalidade de um Perfil"), com a opção selecionada restaurada a partir de `modalityCode` ou `modalityId`, e `{% recusa_de %}` para `modalityCode`. Conferir que o fragmento de linha nova (`B/interface/views.py`, `fragmento_documento`) recebe o mesmo alcance
- [X] T028 [US1] Rodar T010 a T016 e as famílias de T001. Demonstrar pela interface os passos 1 a 6 do cenário A de `quickstart.md`

**Checkpoint**: a US1 está completa e demonstrável sozinha. O MVP.

---

## Phase 4: User Story 2 — Quem analisa vê o que foi pedido, e o que não se aplicava (P1)

**Goal**: a inscrição grava, no envio, o veredito de cada documento, e as telas de inscrição enviada
leem essa lista.

**Independent Test**: `quickstart.md`, cenário A, passos 7 e 8, sem depender do recorte transversal: com recortes exatos, enviar, retificar a obrigatoriedade de um documento, e conferir que a Mesa e a consulta mostram o que foi pedido no envio.

### Testes

- [X] T029 [P] [US2] Criar `T/integration/inscricoes/test_lista_exigida.py` (`transaction=True` onde a garantia é do banco):
  - o envio grava **uma linha por documento** da versão aceita, inclusive os `NAO_SE_APLICA`, com forma e parâmetros;
  - `versao` = `versao_aceita`, `gravada_em` = `submitted_at`;
  - o reenvio com a mesma chave não grava de novo;
  - uma Retificação publicada depois não muda as linhas, e duas Retificações seguidas, com envios entre elas, deixam cada inscrição com a lista do seu envio;
  - **o teste que discrimina:** gravar para uma inscrição uma linha cuja situação difere do que `aplicabilidade` calcula hoje sobre a mesma versão, e provar que a Mesa, a consulta e o portal mostram a linha gravada. Sem isso, o teste passaria sem a feature, porque os leitores já usam a `versao_aceita` (`research.md`, R-006) (`FR-714` a `FR-717`, `FR-723`, `SC-264`)
- [X] T030 [P] [US2] Criar `T/integration/inscricoes/test_lista_exigida_imutavel.py`, só-PostgreSQL no molde de `T/integration/test_database_permissions.py`, que prova, cada uma na sua camada:
  - `UPDATE` e `DELETE` recusados pelo gatilho, como superusuário;
  - recusados pelo privilégio, como runtime;
  - `save()` fora da adição e `delete()` recusados no modelo;
  - `INSERT` recusado para inscrição em rascunho, para versão diferente da aceita e para `gravada_em` diferente de `submitted_at`;
  - **o que o gatilho não prova, a aplicação prova** (`D-004`, `research.md` R-005): migrar sobre um banco com inscrições enviadas cria zero linhas; e uma varredura do código confirma que só `B/inscricoes/application/submissao.py` e `B/processos/management/commands/seed_demo.py` chamam `gravar_lista_exigida`
- [X] T031 [P] [US2] Em `T/integration/inscricoes/test_lista_exigida_concorrencia.py` (`transaction=True`, só-PostgreSQL, no molde das threads de `T/integration/inscricoes/test_teto_por_candidato.py`): um envio e a publicação de uma Retificação que muda o recorte, concorrentes. A lista gravada é da `versao_aceita` que o envio registrou, ou o envio é serializado atrás da publicação e recusa com `edital_updated`. Nunca uma lista de uma versão com a inscrição apontando outra (caso-limite do envio concorrente, `FR-714`)
- [X] T032 [P] [US2] Em `T/interface/test_mesa.py` e `T/integration/interface/test_inscricoes_recebidas.py`: o analista a quem a inscrição **não** foi distribuída não vê a lista na Mesa (a mesma recusa de hoje, por identificador fabricado inclusive); o envio produz um único evento `SUBMETER`, e nenhum registro de auditoria contém o conteúdo da lista (`FR-728`, `FR-729`)
- [X] T033 [P] [US2] Em `T/interface/test_mesa.py` (ou `T/interface/test_mesa_lista_exigida.py`, novo): os três estados, a marca *facultativo*, a razão de `UX-081`, a seção "Não se aplicam a esta inscrição" depois dos pedidos, sem depender de cor (`UX-082`); nada some (`FR-718`, `SC-263`); a instrução do documento continua aparecendo, se o PR #167 já estiver no branch
- [X] T034 [P] [US2] Em `T/integration/interface/test_inscricoes_recebidas.py`: na lista, "recebidos de esperados" sai da lista gravada; no detalhe, os três estados e a razão; a seção "em preenchimento" não muda (`FR-719`). Em `T/integration/interface/test_inscricoes_em_escala.py`, a asserção de consultas iguais para 5 e 300 continua valendo, com as inscrições **enviadas pelo caminho que grava a lista**
- [X] T035 [P] [US2] Em `T/integration/portal/test_comprovante_preservado.py` e `T/integration/portal/test_conferir_inscricao.py`: a inscrição enviada e o comprovante tiram as linhas da lista; o comprovante imprime o mesmo e o código de verificação não muda; um documento enviado continua na tela depois de uma Retificação que mudaria o recorte dele (`FR-720`)
- [X] T036 [P] [US2] Em `T/integration/inscricoes/test_lista_exigida.py`, a reconstrução: inscrição enviada sem linhas devolve `reconstruida=True` com os vereditos da versão aceita (`FR-726`)

### Implementação

- [X] T037 [US2] Em `B/inscricoes/models.py`, criar `ItemDaListaExigida` com os campos, as restrições e as guardas de `save`/`delete` de `data-model.md` §2. Docstring no tom do arquivo: por que PROTECT, por que duas camadas quando `ValorDeFato` tem uma (`R-005`)
- [X] T038 [US2] Criar `B/inscricoes/migrations/0005_item_da_lista_exigida.py`, com a tabela e os dois gatilhos via `RunPython(proteger, desproteger)`, com guarda de vendor e caminho reverso, no molde de `B/recursos/migrations/0002_ato_de_instrucao.py`:
  - `item_da_lista_exigida_append_only`: `BEFORE UPDATE OR DELETE`;
  - `item_da_lista_exigida_coerente`: `BEFORE INSERT`, que confere status, versão e instante.

  Sem importar domínio nem aplicação
- [X] T039 [US2] Em `B/seguranca/papeis.py`, acrescentar `"inscricoes_itemdalistaexigida"` a `TABELAS_APPEND_ONLY`, com o comentário de feature e razão
- [X] T040 [US2] Em `T/migrations/test_migrations.py`: `"inscricoes": 4 → 5` no guardião da `022`, com justificativa; `inscricoes` em `APPS`; os dois gatilhos em `TRIGGERS_POR_APP`. Em `T/integration/requerimentos/test_nao_escreve_fora.py`, acrescentar a tabela às que o requerimento não escreve (`R-013`)
- [X] T041 [US2] Criar `B/inscricoes/application/lista_exigida.py` com:
  - `gravar_lista_exigida(inscricao, versao, agora)`: `bulk_create` dos vereditos;
  - `lista_exigida(inscricao, conteudo) → ListaExigida`: lê as linhas ou reconstrói;
  - `listas_exigidas(inscricoes, conteudos)`: uma consulta para a página (`R-006`, `contracts/lista-exigida.md` §2)
- [X] T042 [US2] Em `B/inscricoes/application/submissao.py`, `enviar_inscricao` chama `gravar_lista_exigida` logo depois de `_congelar`, com a mesma `versao` e o mesmo `agora`, na mesma transação
- [X] T043 [US2] Em `B/avaliacoes/application/mesa.py`, `inscricao_para_avaliar` monta `documentos` a partir de `lista_exigida` sobre a versão aceita, com situação, razão legível e o sinal `reconstruida`. Preservar `modelo` e, se já presente, `instrucoes` (PR #167)
- [X] T044 [US2] Em `B/interface/templates/interface/mesa_inscricao.html`, a seção de pedidos (com *obrigatório*/*facultativo*, a razão, *apresentado*/*não apresentado*), depois a de "Não se aplicam a esta inscrição", e o aviso de lista reconstruída acima (`contracts/lista-exigida.md` §3). Ajustar `B/interface/views.py` (`inscricao_da_mesa`) se a contagem de "abertos" depender da lista antiga
- [X] T045 [US2] Em `B/inscricoes/application/consulta.py`, `_linhas` (seção recebidas) usa `listas_exigidas` para "recebidos de esperados", e `inscricao_para_consulta`, para inscrição enviada, usa `lista_exigida`. Em `B/interface/templates/interface/inscricao_detalhe.html`, os três estados, a razão e o aviso
- [X] T046 [US2] Em `B/portal/views.py`, `_documentos` lê de `lista_exigida` quando a inscrição está `SUBMETIDA`, e de `requisitos_da_inscricao` quando está em rascunho. O filtro "só enviados" de `_conferencia` e do comprovante continua, e o portal não traz aviso de reconstrução (`FR-726`)
- [X] T047 [US2] Rodar T029 a T036, `T/integration/test_database_permissions.py`, `T/integration/test_imutabilidade_do_historico.py` e as famílias de T001. Rodar `provisionar_papeis` duas vezes no banco da worktree, depois de migrar, e conferir "34 de 34". Demonstrar os passos 7 e 8 do cenário A de `quickstart.md`

**Checkpoint**: as US1 e US2 juntas fecham o caso do 903: o que o PDF exige é o que o portal pede e o
que a Mesa mostra.

---

## Phase 5: User Story 3 — Retificar o recorte sem perder o que já foi pedido (P2)

**Goal**: o recorte transversal se retifica, e o resumo público o nomeia.

**Independent Test**: `quickstart.md`, cenário B.

### Testes

- [X] T048 [P] [US3] Em `T/interface/test_retificar_documentos.py`:
  - o campo "Modalidade em todos os Perfis" aparece com as opções do conteúdo publicado, fora a ampla;
  - escolher código gera `REPLACE` em `/documentRequirements/id=…/modalityCode`;
  - trocar de exato para transversal no mesmo ato publica;
  - código fabricado é recusado;
  - documento continua não removível (`FR-722`, `D-009`)
- [X] T049 [P] [US3] Em `T/unit/editais/test_validacao_inscricao.py`, no conteúdo **resultante** de uma Retificação:
  - renomear PcD em um Perfil impede, e em todos passa;
  - declarar ampla a Modalidade do código impede;
  - remover o código de todos os Perfis impede, e de alguns passa (`FR-704`, `FR-706`, `FR-724`)
- [X] T050 [P] [US3] Em `T/unit/publicacoes/test_alteracoes_legiveis.py`, as três operações sobre `modalityCode` (passar a recortar, deixar de recortar, trocar o código) chegam da tela como `REPLACE` e viram, as três, a linha *Documento exigido "X" — Modalidade em todos os Perfis — alterado*, sem valor e sem identificador (`FR-721`, `SC-267`, `D-008`)

### Implementação

- [X] T051 [US3] Em `B/editais/domain/mutabilidade.py`, `("documentRequirements", "modalityCode"): retificavel()`, com comentário que dá a razão de `D-002`
- [X] T052 [US3] Em `B/interface/retificacao.py`:
  - `CAMPOS_DOCUMENTO` ganha `("modalityCode", "Modalidade em todos os Perfis", REFERENCIA)`;
  - `opcoes_de_aplicabilidade` devolve os códigos do conteúdo publicado, fora a ampla, com o rótulo de `UX-080`;
  - `ROTULO_DO_VAZIO` do campo diz "Não recorta por código".

  Rodar `T/interface/test_campos_vem_do_contrato.py`
- [X] T053 [US3] Em `B/publicacoes/domain/alteracoes.py`, `CAMPOS["documentRequirements"]["modalityCode"] = "Modalidade em todos os Perfis"`. `profileId` e `modalityId` continuam fora (fila das diretas)
- [X] T054 [US3] Rodar T048 a T050. Demonstrar o cenário B de `quickstart.md` pela interface

**Checkpoint**: um Edital já publicado com "facultativo para todos" passa a exigir o laudo do PcD por
Retificação, e as inscrições anteriores não mudam.

---

## Phase 6: User Story 4 — Edital e inscrição anteriores à feature (P2)

**Goal**: a inscrição antiga se lê, com a lista reconstruída e a divergência nomeada; o publicado
antigo não muda.

**Independent Test**: `quickstart.md`, cenário D.

### Testes

- [X] T055 [P] [US4] Em `T/interface/test_mesa.py` (ou o arquivo de T033), com fixture de versão publicada com "Todos os Perfis" + "C1 · PcD" e inscrição PcD no C2 **sem** linhas: o aviso de reconstrução uma vez, acima da lista (`UX-083`); o laudo em "Não se aplica", com o acréscimo *"o Edital publicado o exigia de todo candidato em Pessoas com Deficiência"* (`FR-727`, `SC-265`)
- [X] T056 [P] [US4] No mesmo cenário, mas com a inscrição enviada **depois** da feature sob a mesma versão: a linha gravada tem `divergente_do_publicado=True`, e a Mesa mostra o mesmo acréscimo, sem o aviso de reconstrução (`FR-727`, segunda frase)
- [X] T057 [P] [US4] Em `T/unit/publicacoes/test_identidade_imutavel.py` (ou vizinho): o documento e o `content_hash` de uma publicação da versão 16 são os mesmos depois da feature; a consulta pública serve o literal, sem `modalityCode` (`FR-725`, `SC-265`)

### Implementação

- [X] T058 [US4] Conferir que T043 a T046 cobrem a reconstrução e a divergência nas três telas, e completar o que faltar em `B/interface/templates/interface/mesa_inscricao.html` e `B/interface/templates/interface/inscricao_detalhe.html`
- [X] T059 [US4] Rodar T055 a T057. Se o banco do estudo estiver disponível, demonstrar o cenário D de `quickstart.md` com a inscrição `INS-2026-WTBAMDBH`

**Checkpoint**: nenhuma inscrição antiga some da Mesa, e a do C2 do 903 deixa de ser lida em silêncio.

---

## Phase 7: Polish & Cross-Cutting

- [X] T060 [P] Em `B/processos/management/commands/seed_demo.py`, as inscrições postas em `SUBMETIDA` gravam a lista por `gravar_lista_exigida`, com `gravada_em = submitted_at` (`R-012`). Re-semear um banco de demonstração e abrir uma inscrição na Mesa: nenhum aviso de reconstrução
- [X] T061 [P] Em `specs/001-processo-seletivo-editais/contracts/openapi.yaml`, `DocumentoExigidoPublicado` ganha `modalityCode` **dentro** de `required`, como `attachmentId`, e a descrição passa às cinco formas. Rodar `T/contract/test_forma_publicada.py`, que exige `required == properties` (`contracts/recorte-transversal.md` §1)
- [X] T062 [P] Em `AGENTS.md`, "eram 18, são **33**" passa a **34**
- [X] T063 Criar `specs/044-recorte-transversal-documental/rastreabilidade.md`: uma linha para **cada** identificador em negrito da spec (`FR-700` a `FR-729`, `UX-080` a `UX-083`, `SC-260` a `SC-268`), **e uma para cada caso-limite** da seção Edge Cases, com o teste que o prende. `SC-260` e `SC-261` são demonstração (`quickstart.md`, cenário C), e a linha diz isso
- [X] T064 Rodar `cd backend && uv run pytest tests/test_citacoes_de_requisito.py tests/test_sem_dado_pessoal_da_amostra.py` e corrigir antes de empurrar
- [ ] T065 Demonstrar o cenário C de `quickstart.md` (o 140/2025) e anotar no PR as contagens de `SC-260` e `SC-261` — **não feito nesta sessão**: recompor 16 Perfis pela interface não cabia no percurso; ver `rastreabilidade.md`, SC-260 e SC-261
- [X] T066 Rodar `cd backend && make lint check test-pg POSTGRES_USER=<superusuário> DB_NAME=<banco da worktree>`, sem editar nada durante a suíte. Registrar passando/pulados no PR — *7747 passando, 11 pulados, em 26/09/2026*
- [X] T067 Registrar, fora do escopo, o achado de `research.md` R-014 que continua aberto: `ValorDeFato` sem gatilho. O filtro de concorrência da consulta, que repetia a modalidade por Perfil, saiu desta tarefa: foi registrado e corrigido à parte (`doc/achado-filtro-de-concorrencia-sem-perfil.md`)

---

## Dependencies & Execution Order

- **Setup (T001–T002)** → **Foundational (T003–T009)** → histórias.
- **US1 (T010–T028)** depende só da Foundational.
- **US2 (T029–T047)** depende da Foundational. **Não** depende da US1: a lista grava vereditos das
  quatro formas existentes. Ela só prova o caso transversal (`SC-262`, Mesa do C2) depois da US1.
- **US3 (T048–T054)** depende da US1, porque retifica o campo que ela cria.
- **US4 (T055–T059)** depende da US2, porque a reconstrução é a leitura dela, e da Foundational, pelo
  predicado.
- **Polish** depende das quatro.

Dentro de cada história: testes → modelo e migration → domínio e aplicação → telas → demonstração.

### Paralelismo

- Na Foundational, T003, T004 e T005 correm juntos (mesmo arquivo de teste, casos distintos: escreva-os
  em sequência se o editor não comportar).
- Na US1, os testes T010 a T016 correm juntos. T024 (PDF) e T025 (Revisão) correm juntos, depois de
  T021.
- US1 e US2 podem correr em paralelo depois da Foundational, em mãos diferentes. Os pontos de
  encontro são `B/editais/domain/documentos.py` (já estável na Foundational) e `T/migrations/test_migrations.py`
  (T018 e T040 tocam linhas diferentes do mesmo arquivo).
- Na US2, os testes T029 a T036 correm juntos. T043 (Mesa), T045 (consulta) e T046 (portal) correm
  juntos, depois de T041.

## Implementation Strategy

**MVP = Foundational + US1.** Com ela, um Edital novo declara "PcD em todos os Perfis" numa linha, e o
PDF, o cartão e o envio concordam. Isso fecha o caso do 903 para os Editais publicados daqui em diante.

**Incremento 2 = US2 (+ reconstrução).** A Mesa passa a mostrar o que foi pedido, e o "não se aplica"
deixa de sumir. É o que a Constituição pede com *reproduzir os documentos exigidos*.

**Incremento 3 = US3.** Os Editais já publicados com "facultativo para todos" podem ser corrigidos
por Retificação.

**Incremento 4 = US4 + Polish.** A leitura das inscrições antigas com a divergência nomeada, a
semente, os contratos e a matriz.

Cada incremento fecha verde e demonstrável. Nenhum deixa a Mesa quebrada para as inscrições que já
existem.
