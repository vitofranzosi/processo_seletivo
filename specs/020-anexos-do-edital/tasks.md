---

description: "Tarefas de implementação — 020 Anexos do Edital"
---

# Tasks: Anexos do Edital

**Input**: `specs/020-anexos-do-edital/` — [spec.md](./spec.md), [plan.md](./plan.md),
[research.md](./research.md), [data-model.md](./data-model.md), [contracts/](./contracts/),
[quickstart.md](./quickstart.md)

**Tests**: incluídos. Não é preferência de estilo: a Constituição exige cobertura específica para
publicação, retificação, temporalidade, documentos, autorização e concorrência (princípio V), e esta
feature toca todas.

**Organização**: as fases seguem as histórias da spec. As duas primeiras não têm história porque são
o chão de todas — a declaração da coleção e as tabelas. Os rótulos F1–F6 do plano aparecem em cada
fase, para rastrear.

## Format: `[ID] [P?] [Story] Descrição com caminho`

- **[P]**: pode correr em paralelo (arquivos distintos, sem dependência pendente)
- **[Story]**: a que história da spec a tarefa pertence
- **O identificador é estável, e não é a ordem.** Quem executa segue a fase e o grafo de
  dependências; renumerar depois de uma correção invalidaria referência já feita em revisão.

---

## Phase 1: Setup

**Propósito**: mover para o lugar certo o que já existe, antes de acrescentar qualquer coisa.

- [ ] T001 Mover `aceitar()` e `resumo()` de `backend/processo_seletivo/inscricoes/domain/arquivos.py` para `backend/processo_seletivo/shared/arquivos.py`, com `inscricoes` reimportando de lá e os testes existentes apontando para a casa nova (FR-009, R-007)
- [ ] T002 [P] Declarar `EDITAL_ANEXOS_LIMITE_BYTES` em `backend/config/settings/base.py`, lido do ambiente com **5 MB** de padrão (`5 * 1024 * 1024`), no molde de `ARQUIVOS_CANDIDATOS_LIMITE_BYTES` e com o comentário que diz por que o limite é da aplicação e não do Edital (FR-013)

---

## Phase 2: Foundational (F1 e F2 do plano) — bloqueia todas as histórias

**Propósito**: a coleção passa a existir no conteúdo canônico e as tabelas passam a existir no banco.
Nenhuma tela ainda. É a fase que mais quebra teste, e é melhor que quebre sozinha.

**⚠️ Nenhuma história começa antes de T018.**

### A coleção declarada

- [ ] T003 [P] Declarar `"/attachments"` em `COLECOES_COM_CHAVE` em `backend/processo_seletivo/publicacoes/domain/colecoes.py` — sem isto o seletor `id=` é recusado e a coleção nasce irretificável (FR-003, FR-032)
- [ ] T004 [P] Escrever a tupla `ANEXO_PUBLICADO` de `Campo` e registrá-la em `COLECOES_PUBLICADAS` em `backend/processo_seletivo/editais/domain/validation.py` (FR-001, FR-005, FR-029)
- [ ] T005 Acrescentar `attachmentId` (uuid, anulável) a `DOCUMENTO_EXIGIDO_PUBLICADO` em `backend/processo_seletivo/editais/domain/validation.py` (FR-020, FR-021)
- [ ] T006 Elevar `SCHEMA_VERSION` de 8 para 9 em `backend/processo_seletivo/shared/canonical.py`, com o degrau narrado no log do módulo, e acrescentar `attachments: []` a `DEGRAUS_DA_RAIZ` em `backend/processo_seletivo/publicacoes/domain/elevacao.py` (R-004)
- [ ] T007 Criar a tabela de degraus do nível `documentRequirement` em `backend/processo_seletivo/publicacoes/domain/elevacao.py`, com `attachmentId: null`, e o laço correspondente em `elevar()` (R-004)
- [ ] T008 Acrescentar `_e_entidade_de_documento` e o tratamento em `elevar_valor`/`elevar_alteracoes` em `backend/processo_seletivo/publicacoes/domain/elevacao.py`, para que Alteração que endereça o requisito inteiro seja elevada (R-004)
- [ ] T009 [P] Incorporar `AnexoPublicado`, `attachmentId` e `attachments` ao `specs/001-processo-seletivo-editais/contracts/openapi.yaml`, a partir de `specs/020-anexos-do-edital/contracts/anexos.yaml`
- [ ] T010 [P] Registrar a coleção em `ESQUEMA_DA_COLECAO` em `backend/tests/contract/test_forma_publicada.py`
- [ ] T011 [P] Acrescentar a coleção a `conteudo_normativo()` e `rascunho_completo()` em `backend/tests/fixtures/snapshot.py`, mantendo os guardas de coleção declarada e elemento com chave

### As tabelas

- [ ] T012 Criar `AnexoEdital` e `ArtefatoAnexo` em `backend/processo_seletivo/editais/models/anexos.py`, com os campos de [data-model.md](./data-model.md), e exportá-los em `backend/processo_seletivo/editais/models/__init__.py` (FR-002, FR-005, FR-007, FR-010, FR-011, FR-012, FR-014)
- [ ] T013 Acrescentar a referência anulável `anexo` (`SET_NULL`) a `DocumentoExigido` em `backend/processo_seletivo/editais/models/documentos.py` **e incluir o campo no `bulk_create` de `replace_draft` em `backend/processo_seletivo/editais/application/draft.py`** — as linhas do requisito são apagadas e recriadas a cada gravação de etapa, e o campo esquecido zera o vínculo em silêncio (FR-020, FR-022)
- [ ] T014 Escrever `backend/processo_seletivo/editais/migrations/0012_anexo_do_edital.py`
- [ ] T015 Escrever `backend/processo_seletivo/editais/migrations/0013_congelamento_do_artefato.py`, com a trigger condicional `WHEN (OLD.congelado_em IS NOT NULL)` no molde de `publicacoes/migrations/0007_imutabilidade_do_historico.py` (FR-010, R-002)

### As garantias

- [ ] T016 [P] Teste de migração em `backend/tests/migrations/` provando que artefato congelado recusa `UPDATE` e `DELETE` **no banco**, e que artefato não congelado aceita os dois (FR-010, FR-010a)
- [ ] T017 [P] Estender `backend/tests/unit/publicacoes/test_colecoes.py` para cobrir `/attachments` como coleção declarada com chave
- [ ] T018 [P] Escrever `backend/tests/contract/test_elevacao_degrau_9.py` no molde do degrau 8: conteúdo em versão 8 eleva para 9 com lista vazia e `attachmentId: null`, e a elevação é idempotente (R-004)
- [ ] T028 Regenerar `backend/tests/contract/fixtures/snapshot_publicado.json` e `documento_publicado_v1.pdf` com `backend/scripts/gerar_fixture_documento.py` — **fecha a Foundational**, porque o degrau 9 muda o `content_hash` e o documento o imprime (`pdf.py:1786,1897`); adiar isto deixaria a fase terminar com a suíte vermelha

---

## Phase 3: US1 — O autor publica o Edital com os seus anexos (P1) · F3 e F4

**Meta**: o autor monta a coleção, publica, e quem consulta baixa os anexos da página pública.

**Teste independente**: elaborar um Edital com três anexos pela interface administrativa, publicá-lo
e baixar os três da página pública da seleção — sem shell e sem escrita direta no banco.

- [ ] T019 [US1] Escrever `anexar`, `rotular`, `reordenar` e `remover` em `backend/processo_seletivo/editais/application/anexos.py`, com `require_permission(actor, "edital:elaborar")`, `compare_and_swap` na revisão do Edital, validação por `shared/arquivos.aceitar` e `record_event` (FR-015, FR-015a, FR-016, FR-055)
- [ ] T020 [US1] Emitir `attachments` em `edital_snapshot` em `backend/processo_seletivo/publicacoes/application/publish_edital.py`, com ordenação determinística por `(order, id)` (FR-001, FR-029, FR-030)
- [ ] T021 [US1] Acrescentar a etapa `anexos` ao assistente: rota em `backend/processo_seletivo/interface/urls.py`, tratamento em `backend/processo_seletivo/interface/views.py` e os templates `compor_anexos.html` e `_anexo.html`, com `enctype="multipart/form-data"` — é o primeiro caminho de escrita de arquivo da interface administrativa (FR-015, FR-019)
- [ ] T022 [US1] Servir o artefato de rascunho pela interface administrativa, exigindo ator no escopo institucional e autorização de elaboração, revisão ou homologação (FR-017)
- [ ] T023 [US1] Declarar `attachments` em `COLECOES` em `backend/processo_seletivo/interface/revisao.py`, com a função de leitura no padrão de `_secao` (FR-018)
- [ ] T024 [US1] Congelar, dentro da transação de `publish_edital`, todos os artefatos referenciados pela versão publicada, carimbando `congelado_em` (FR-010, FR-025)
- [ ] T025 [US1] Acrescentar as regras impeditivas `attachment_label_required` e `attachment_artifact_missing`, e o aviso `attachment_duplicate_label`, em `backend/processo_seletivo/editais/domain/validation.py`, registradas em `validate_for_publication` (FR-005, FR-026)
- [ ] T026 [P] [US1] Declarar a `Secao` gerada com `source="attachments"` no catálogo em `backend/processo_seletivo/editais/domain/secoes.py` (FR-027)
- [ ] T027 [US1] Escrever o corpo `_anexos` em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`, listando rótulo e ordem **sem endereço**, e registrá-lo em `_CORPO_GERADO` (FR-027, FR-027a)
- [ ] T029 [P] [US1] Escrever `ArtefatoPublicoView` em `backend/processo_seletivo/publicacoes/api/public_views.py` e a rota em `public_urls.py`, com `AllowAny`, `ETag`, `If-None-Match` → 304, `IMMUTABLE_CACHE`, `Content-Disposition: attachment` e 404 para artefato não congelado. O endereço é o do **artefato**, e é assim que ele resolve "o de então" e nunca "o vigente" (FR-028, FR-039, FR-041, FR-042, FR-043, FR-052, R-003)
- [ ] T030 [US1] Listar todos os anexos vigentes, na ordem editorial, na página pública da seleção em `backend/processo_seletivo/portal/views.py` e `templates/portal/selecao.html` (FR-039, FR-039a)
- [ ] T031 [P] [US1] Testes de contrato da rota pública em `backend/tests/contract/`: 200 com `ETag`, 304 com `If-None-Match`, cabeçalho de cache, 404 do não congelado
- [ ] T032 [P] [US1] Teste de autorização em `backend/tests/authorization/`: artefato de Edital não publicado devolve **404** pela rota pública, e é entregue a quem tem autorização pela interface — é a fronteira entre o regime público versionado e a raiz privada da `009` (FR-017, FR-052)
- [ ] T033 [P] [US1] Teste de interface em `backend/tests/interface/`: subir, rotular, ordenar e remover no rascunho — **e gravar outra etapa do assistente sem que os anexos sumam**, que é o modo de falha do `replace_draft` (R-006)
- [ ] T034 [P] [US1] Teste do PDF em `backend/tests/unit/publicacoes/test_pdf.py`: a seção de anexos aparece no documento, é determinística e não imprime endereço (FR-027a, FR-030)

**Checkpoint**: passos 1, 6 e 7 do quickstart passam a ser demonstráveis.

---

## Phase 4: US2 — O candidato baixa o modelo e devolve preenchido (P1) · F5

**Meta**: o requisito que tem modelo oferece o modelo, e o que voltou continua sendo julgado por
gente.

**Teste independente**: percorrer a inscrição de um Perfil cujo requisito tem modelo, baixar o modelo
pelo portal e enviar o arquivo preenchido, sem sair do fluxo.

- [ ] T035 [US2] Emitir `attachmentId` em `_document_requirements` em `backend/processo_seletivo/publicacoes/application/publish_edital.py`, a partir da referência do modelo (FR-020, FR-021)
- [ ] T036 [US2] Oferecer a escolha do modelo na etapa `inscricao` do assistente, entre os anexos do próprio Edital, em `backend/processo_seletivo/interface/forms.py` e `templates/interface/_documento.html` (FR-020, FR-024)
- [ ] T037 [US2] Acrescentar a regra impeditiva `attachment_reference_dangling` em `backend/processo_seletivo/editais/domain/validation.py`, aplicada na publicação e em cada fronteira de vigência da Retificação (FR-023)
- [ ] T038 [US2] Oferecer o modelo vigente ao lado do campo de envio, em `backend/processo_seletivo/portal/views.py` e `templates/portal/_documentos.html` (FR-044, FR-045)
- [ ] T039 [US2] Verificar que nenhum caminho de descarte alcança documento enviado quando o modelo é substituído, e cobrir o caso com teste — o aviso de versão que já existe basta (FR-046, D-012)
- [ ] T040 [P] [US2] Testes de portal em `backend/tests/portal/`: modelo oferecido, requisito sem modelo inalterado, documento preservado após substituição do modelo
- [ ] T041 [P] [US2] Teste estrutural provando que nenhum caminho lê, compara ou extrai o conteúdo do arquivo devolvido (FR-047)

---

## Phase 5: US3 — A Retificação substitui um anexo, e os dois coexistem (P1) · F6

**Meta**: o passo emblemático. Trocar o artefato sem perder o anterior.

**Teste independente**: retificar um Edital publicado substituindo o artefato de um anexo, e provar
que a publicação anterior e a vigente entregam bytes diferentes, com resumos distintos.

- [ ] T042 [US3] Acrescentar `CAMPOS_ANEXO` e o grupo correspondente em `campos_editaveis` em `backend/processo_seletivo/interface/retificacao.py` (FR-031)
- [ ] T043 [US3] Aceitar a substituição do artefato dentro do ato de Retificação: `enctype="multipart/form-data"` em `templates/interface/retificar.html`, recepção em `backend/processo_seletivo/interface/views.py`, e criação do artefato com `congelado_em` nulo (FR-034, FR-035)
- [ ] T044 [US3] Traduzir a substituição em `REPLACE` de `artifactId` e `artifactHash` em `diferencas` em `backend/processo_seletivo/interface/retificacao.py` — os bytes não viajam na alteração (FR-035)
- [ ] T045 [US3] Congelar, em `publish_retification` em `backend/processo_seletivo/publicacoes/application/retificacoes.py`, os artefatos citados pelas alterações, na mesma transação em que a `Publicacao` e o `DocumentoPublicado` nascem (FR-010, FR-025)
- [ ] T046 [US3] Escrever `backend/tests/acceptance/test_us_anexos.py` cobrindo o **ciclo inteiro** do 173/2025, no molde de `test_us6_consulta_publica.py`: publicar com os anexos-formulário, retificar substituindo um, baixar o vigente, devolver preenchido, deferir, perguntar por um instante anterior e provar que os dois artefatos coexistem com resumos distintos, ambos respondendo 200 (FR-042, SC-002, SC-005)
- [ ] T047 [P] [US3] Teste de consulta temporal: `?em=<instante anterior>` devolve o `artifactId` de então, e a publicação histórica continua entregando o artefato daquela versão (FR-028, FR-040, FR-041, SC-003)
- [ ] T048 [P] [US3] Teste de concorrência: duas Retificações sobre o mesmo anexo, a segunda recusada pelo `expected_previous_hash` já existente (FR-036)
- [ ] T049 [P] [US3] Teste de endereçamento: `/attachments/3` é recusado, `/attachments/id=<uuid>` é aceito (FR-032)
- [ ] T066 [P] [US3] Teste de autorização em `backend/tests/authorization/`: substituir, rotular, ordenar, acrescentar e remover anexo depois da publicação exige `retificacao:elaborar` e `retificacao:submeter`, e nenhum desses atos é alcançável por quem só tem `edital:elaborar` (FR-037)

---

## Phase 6: US4 — A banca abre o modelo que estava valendo (P2)

**Meta**: o modelo mostrado é o da versão aceita, e o sistema não afirma nada além disso.

**Teste independente**: abrir a mesa de avaliação de uma Inscrição enviada antes de uma Retificação e
conferir que o modelo mostrado é o daquela versão.

- [ ] T050 [US4] Resolver o artefato do requisito pela versão aceita da Inscrição e oferecê-lo na mesa, em `backend/processo_seletivo/interface/views.py`, sem gravar dado novo por submissão (FR-048, FR-050)
- [ ] T051 [P] [US4] Teste de interface: inscrição sob a versão anterior mostra o modelo daquela versão, e não o vigente (SC-007)
- [ ] T052 [P] [US4] Teste: nenhuma tela afirma qual versão do modelo o candidato usou (FR-049)

---

## Phase 7: US5 — O autor corrige a coleção sem quebrar o Edital (P2) · F6

**Meta**: acrescentar, remover, rotular e reordenar por Retificação, sem que nada disso mexa no que
não foi endereçado.

**Teste independente**: aplicar as quatro operações por Retificação e verificar rótulos, ordem,
lacuna e ausência de referência pendurada.

- [ ] T053 [US5] Acrescentar `NOVO_ANEXO` e `_anexo_completo` em `backend/processo_seletivo/interface/retificacao.py`, produzindo exatamente a forma que `edital_snapshot` emite, e o bloco `ADD` em `diferencas` (FR-031)
- [ ] T054 [US5] Marcar o grupo do anexo como `removivel=True` e traduzir a remoção em `REMOVE /attachments/id=<uuid>` (FR-031, FR-033)
- [ ] T055 [US5] Oferecer rótulo e ordem como campos editáveis, garantindo que alterar um não recalcula nem renumera nenhum outro (FR-006, FR-007, FR-008)
- [ ] T056 [US5] Desfazer o vínculo do `DocumentoExigido` no mesmo ato que remove o anexo, recusando com erro impeditivo a Retificação que deixaria referência pendurada (FR-022, FR-023)
- [ ] T065 [US5] Acrescentar `attachmentId` a `CAMPOS_DOCUMENTO` em `backend/processo_seletivo/interface/retificacao.py`, como campo `REFERENCIA` com as opções vindas dos anexos daquela versão — sem ele T056 é irrealizável pelo canal do ator, porque a tela não oferece o campo que precisa mudar (FR-022, FR-031)
- [ ] T057 [P] [US5] Testes em `backend/tests/interface/` e `backend/tests/unit/`: remover o quarto de seis deixa lacuna e não altera rótulo nenhum; retificação com vínculo pendurado é recusada nomeando o vínculo
- [ ] T058 [P] [US5] Teste: anexo removido da versão futura continua íntegro na publicação anterior (FR-033)

---

## Phase 8: Polish e transversais

- [ ] T059 [P] Acessibilidade da etapa de anexos e da lista pública, em `backend/tests/interface/test_acessibilidade*.py` e `backend/tests/portal/`
- [ ] T060 [P] Conferir a trilha de auditoria de envio, vínculo, desvínculo e substituição, com ator, ação, entidade e instante, e sem nome de arquivo desnecessário; a Retificação sobre anexo registra autoria, motivo, instante e versão pela trilha que já existe (FR-038, FR-055)
- [ ] T061 [P] Teste da cadeia `versão histórica → identidade → resumo publicado → bytes`, como garantia interna (FR-053)
- [ ] T062 [P] Teste provando que nenhuma rota expõe verificação de integridade ao usuário final (FR-054)
- [ ] T063 [P] Acrescentar anexos ao `seed_demo` em `backend/processo_seletivo/processos/management/commands/seed_demo.py`, para que a demonstração tenha o que baixar
- [ ] T064 Executar o [quickstart.md](./quickstart.md) inteiro, os sete passos e as cinco verificações negativas, e registrar o resultado

---

## Dependências

```text
Setup (T001–T002)
   ↓
Foundational (T003–T018, T028)    ← bloqueia tudo
   ↓
US1 (T019–T027, T029–T034) ───────┐
   ↓                              │
US2 (T035–T041)   US3 (T042–T049, │  US2 e US3 são independentes entre si
   ↓                    T066)     │
US4 (T050–T052)   US5 (T053–T058, │  US4 depende de US2; US5 depende de US3
                        T065)     │
   └──────────┬───────────────────┘
              ↓
        Polish (T059–T064)
```

Dentro da Foundational, a ordem que importa: T003 antes de T020 (declarar antes de emitir); T006–T008
antes de T011 e T018; T012–T013 antes de T014–T015; e **T028 por último**, porque é ela que devolve a
suíte ao verde depois do degrau 9.

## Oportunidades de paralelismo

- **Foundational**: T003, T004, T009, T010, T011 são arquivos distintos e correm juntas; T016, T017,
  T018 idem, depois das migrations. T028 não é paralelizável: ela fecha a fase.
- **US1**: T026 e T029 não dependem de T019–T025; os quatro testes T031–T034 correm juntos no fim.
- **US3 e US2** podem ser feitas por duas pessoas ao mesmo tempo, depois da US1. Dentro da US3,
  T046 é sequencial — é o ciclo inteiro e depende de tudo o que veio antes; T047, T048, T049 e T066
  correm juntas.
- **US5**: T065 precede T056 na prática, porque é ela que põe o campo na tela que T056 usa.
- **Polish**: T059–T063 são todas independentes.

## Estratégia de entrega

**MVP = Foundational + US1.** Ao fim dela o Edital publica os anexos e o público os baixa, que é a
perna que faltava. É entregável sozinha, e as demais histórias acrescentam sem reabri-la.

**Incremento 2 = US2**, que é o que o candidato recebe. **Incremento 3 = US3**, que é o que separa a
feature de um gerenciador de arquivos. US4 e US5 fecham a manutenção e a verificação.
