# Tasks: A data de nascimento entra no cadastro do candidato

**Estado em 17/11**: o MVP (fundação, histórias 1 e 2 e o requerimento) está implementado no PR desta branch. A história 3 (T024–T029), as guardas T033 e T034, o percurso manual (T038), a nota das Novidades (T039) e a planilha (T040) ficam para o PR seguinte. A T001 não foi necessária: a suíte cria o próprio banco, e `ps_180` foi o nome dele.

**Input**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md` desta pasta.
Caminhos de código relativos a `backend/`.

**Testes**: incluídos. O projeto prende cada requisito por teste (Princípio V), e a matriz de
rastreabilidade cobra `FR-`, `SC-` e os casos-limite.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente)
- **[Story]**: US1, US2, US3, como na spec

---

## Phase 1: Setup

- [ ] T001 Criar o banco da worktree e conferir as migrations: `make preparar DB_NAME=ps_180` e `manage.py migrate --check` (quickstart)

---

## Phase 2: Foundational (bloqueia as três histórias)

- [x] T002 [P] Acrescentar `data_nascimento = models.DateField(null=True, blank=True)` a `CandidateIdentity` em `processo_seletivo/identidade/models.py`, com comentário "declarada, nunca provada", e gerar `processo_seletivo/identidade/migrations/0005_data_nascimento.py`
- [x] T003 [P] Acrescentar `data_nascimento = models.DateField(null=True, blank=True)` a `Inscricao` em `processo_seletivo/inscricoes/models.py`, com comentário "escrita só no envio (180, R3)", e gerar `processo_seletivo/inscricoes/migrations/0009_data_nascimento.py`
- [x] T004 Subir a contagem de migrations de `identidade` e de `inscricoes` em `tests/migrations/test_migrations.py`, com o comentário da `180`
- [x] T005 [P] Escrever `ler_data_de_nascimento(texto, hoje) -> date` e as cinco recusas da R4 em `processo_seletivo/inscricoes/domain/pessoais.py`. Aceita `dd/mm/aaaa` e `aaaa-mm-dd`; recusa ano com menos de quatro dígitos, data inexistente, hoje ou depois e mais de 120 anos (FR-8305, FR-8306)
- [x] T006 [P] Testes de `ler_data_de_nascimento` em `tests/unit/identidade/test_data_de_nascimento.py`: cada recusa com a sua frase, 29/02 em ano bissexto e não bissexto, `01/02/03`, ontem aceito, hoje recusado, 120 anos no limite, menor de idade aceito, "hoje" lido em Brasília às 23h30
- [x] T007 Fixtures com data padrão: `defaults["data_nascimento"] = date(2000, 1, 1)` em `tests/fixtures/candidato.py::registrar`, e o mesmo em toda construção direta de `CandidateIdentity` em `tests/fixtures/` e no `seed_demo` (localizar com `grep -rn "CandidateIdentity.objects.create\|CandidateIdentity(" processo_seletivo tests/fixtures`) (R7)
- [x] T008 `IdentidadeDoCandidato.data_nascimento: date | None = None` em `processo_seletivo/portal/identidade.py`, preenchida em `contrato_de`

**Checkpoint**: migrations aplicadas, contagem verde, leitura da data testada.

---

## Phase 3: User Story 1 — Candidato novo informa a data junto do nome e do CPF (P1) 🎯 MVP

**Goal**: "Seus dados" pede e valida os três campos e volta à vaga.

**Independent Test**: e-mail novo → vaga → "Seus dados" com três campos; data vazia recusada sem
perder nome e CPF; data válida volta à vaga.

- [x] T009 [US1] Em `processo_seletivo/identidade/application/credenciais.py`: `falta_o_nucleo` passa a exigir `data_nascimento`; `recusas(dados, *, cpf_editavel, data_editavel, hoje)` recusa a data pela T005; `gravar_nucleo(..., data_nascimento=None)` grava a data quando editável. A docstring do módulo diz que o núcleo agora é nome, CPF e data, e por quê (FR-8300, FR-8301)
- [x] T010 [US1] Em `credenciais.py`, `data_editavel(identidade)`: verdadeira enquanto a data estiver vazia **ou** o CPF não tiver congelado (R2, FR-8309)
- [x] T011 [US1] `meus_dados` em `processo_seletivo/portal/views.py` lê, valida e grava `data_nascimento`; devolve os três valores como digitados na recusa (FR-8307)
- [x] T012 [US1] Campo "Data de nascimento" em `processo_seletivo/portal/templates/portal/meus_dados.html`: `type="text"`, `inputmode="numeric"`, `autocomplete="bday"`, a dica do contrato, `aria-invalid` e `aria-describedby` na recusa, somente leitura quando congelada com a frase de atendimento; a frase de finalidade no parágrafo de abertura (FR-8314, UX-1000)
- [x] T013 [US1] Se a T012 usar classe nova, a regra em `processo_seletivo/portal/static/portal/portal.css`, sem `style` inline (CSP) — não foi preciso: o campo usa só `campo`, `curto`, `sub` e `recusa`, que a folha já tem
- [x] T014 [P] [US1] `tests/integration/identidade/test_nascimento_no_nucleo.py`: três campos na tela; cada recusa com a frase e os outros valores preservados; válido volta à vaga; o atributo `autocomplete="bday"`; a frase de finalidade; congelada depois do envio; e (R2) cadastro com inscrição enviada e sem data pode informá-la uma vez
- [x] T015 [US1] Rodar `tests/interface/test_acessibilidade_do_portal.py`, `tests/interface/test_portal_sem_redigitar.py` e as varreduras de vocabulário do portal; ajustar o que a tela nova reprovar

**Checkpoint**: história 1 verificável sozinha.

---

## Phase 4: User Story 2 — Quem já tem cadastro informa a data na próxima inscrição (P1)

**Goal**: o cadastro antigo é levado a informar só a data, e o envio sem data é recusado com caminho.

**Independent Test**: identidade com nome e CPF e sem data → abrir vaga → "Seus dados" com nome e CPF
preenchidos e foco na data; rascunho aberto sem data → envio recusado com caminho → informa → envia.

- [x] T016 [US2] Foco na data quando nome e CPF já existem: `autofocus` no campo da data, e não no nome, em `meus_dados.html`; o título e o parágrafo continuam os de "Seus dados" (UX-1001)
- [x] T017 [US2] Recusa no comando: em `processo_seletivo/inscricoes/application/submissao.py::enviar_inscricao`, antes de `_gravar_o_ato`, ler a data do contrato `identidade` (R3) e recusar com `DomainError("birth_date_required", "Falta informar sua data de nascimento em Seus dados.", 422)` quando não houver data (FR-8303)
- [x] T018 [US2] Gravar no ato: `data_nascimento=<data do cadastro>` na `compare_and_swap` de `_gravar_o_ato` (FR-8308, R3)
- [x] T019 [US2] Revisão do portal: linha "Data de nascimento" na lista "dos seus dados" (`portal/views.py`, função dos dados da revisão, perto de "Nome" e "CPF"), com "Falta informar" quando vazia e o caminho para "Seus dados" levando a revisão como destino de volta (contrato do portal)
- [x] T020 [US2] Na view da revisão, a recusa `birth_date_required` aparece com o mesmo caminho (`portal/views.py`, onde `enviar_inscricao` é chamado)
- [x] T021 [P] [US2] `tests/integration/inscricoes/test_envio_sem_data.py`: envio recusado sem data; envio grava a data do cadastro; corrigir o cadastro antes do envio muda o que é gravado; enviada antes da `180` continua sem data e não bloqueia nada (FR-8304); `UPDATE` da data numa enviada é recusado pelo gatilho
- [x] T022 [P] [US2] `tests/integration/identidade/test_nascimento_no_nucleo.py` e `tests/integration/portal/test_revisao_com_a_data.py`: a volta do código de acesso e `portal:inscrever` levam a "Seus dados" com nome e CPF preenchidos; depois de informar, volta à vaga; a revisão mostra "Falta informar" e o caminho volta à revisão
- [x] T023 [US2] Garantir que a data não entra no comprovante: teste em `tests/integration/inscricoes/test_envio_sem_data.py` que confere o texto do comprovante sem a data

**Checkpoint**: histórias 1 e 2 juntas cumprem SC-2900, SC-2901 e SC-2902.

---

## Phase 5: User Story 3 — A equipe confere CPF e nascimento num caso de dúvida (P2)

**Goal**: ação "Conferir identidade" com motivo e trilha, sob a permissão do detalhe.

**Independent Test**: no detalhe da enviada, conferir sem motivo recusa; com motivo revela CPF e data
e grava a trilha sem os valores; papel sem consulta recebe 404.

- [ ] T024 [US3] `identidade_para_conferencia(*, actor, inscricao_id, motivo, correlation_id)` em `processo_seletivo/inscricoes/application/consulta.py`: o escopo de `inscricao_para_consulta`; 404 para rascunho; recusa de motivo vazio (`DomainError("reason_required", "Escreva o motivo da conferência.", 422)`); `record_event` com `operation="CONFERIR_IDENTIDADE"`, `permission=CONSULTAR` e `reason` com o motivo cortado em 300 caracteres; devolve nome, CPF formatado e data (FR-8312, FR-8315, FR-8316, FR-8317)
- [ ] T025 [US3] View `conferir_identidade` (`POST`) em `processo_seletivo/interface/views.py` e rota `inscricoes/<uuid:inscricao_id>/conferir-identidade` (`name="conferir-identidade"`) em `processo_seletivo/interface/urls.py`; resposta com `marcar_como_privada`; motivo vazio devolve o detalhe com a recusa em 422
- [ ] T026 [US3] Bloco "Conferir identidade" em `processo_seletivo/interface/templates/interface/inscricao_detalhe.html`, só para enviada: frase, campo Motivo com a dica, botão (contrato da gestão)
- [ ] T027 [US3] Template `processo_seletivo/interface/templates/interface/conferencia_de_identidade.html`: nome, CPF, data ou "Não informada nesta inscrição", motivo, instante e o link de volta; as regras na folha da gestão (`interface/static/interface/gestao/` ou `interface/telas/`), sem inline
- [ ] T028 [US3] Linha da negativa nova em `specs/033-navegacao-por-capacidade/inventario-das-negativas.md` e, se for o caso, o módulo na lista de `tests/test_gramatica_das_portas.py`
- [ ] T029 [P] [US3] `tests/interface/test_conferencia_de_identidade.py`: revela com motivo; recusa sem motivo, sem revelar; 404 sem permissão e fora do escopo; 404 em rascunho; a trilha tem o motivo e **não** tem CPF nem data; POST repetido grava dois eventos; o detalhe continua com o CPF mascarado; enviada antes da `180` mostra "Não informada"; a resposta é privada (`no-store`)

**Checkpoint**: SC-2906 verificável.

---

## Phase 6: D-003 — O requerimento nasce com a data (transversal a US1 e US2)

- [x] T030 Em `processo_seletivo/requerimentos/application/preencher.py::abrir_rascunho`, na criação, quando `_copiar_para_a_frente` não trouxe `data_de_nascimento`, usar a do `CandidateIdentity` do titular (FR-8313, R6)
- [x] T031 [P] `tests/integration/requerimentos/test_requerimento_com_a_data.py`: nasce preenchido; o herdado vence; alterar no requerimento não muda o cadastro; reabrir não sobrescreve a correção; cadastro sem data deixa o campo vazio
- [ ] T032 Garantir que o fato declarado "data de nascimento" do Perfil continua pedido na inscrição e não é preenchido pelo cadastro: um caso em `tests/integration/inscricoes/test_envio_sem_data.py` (FR-8318)

---

## Phase 7: Polish & Cross-Cutting

- [ ] T033 [P] Guarda de vazamento: teste que percorre a vitrine, a página do Edital e as publicações de um Edital com inscrições enviadas e confere que nenhuma data de nascimento aparece; e que nenhum `RegistroAuditoria` criado pela jornada contém a data (FR-8311, SC-2903), em `tests/integration/inscricoes/test_data_nao_vaza.py`
- [ ] T034 [P] Guarda de identidade: teste que mostra que a retomada, a reconciliação e a adição de credencial não leem `data_nascimento` (FR-8310, SC-2904), em `tests/unit/identidade/test_data_nao_decide_identidade.py`
- [x] T035 Escrever `specs/180-data-de-nascimento-no-cadastro/rastreabilidade.md`: FR-8300 a FR-8318, SC-2900 a SC-2907, UX-1000, UX-1001 e **uma linha por caso-limite**, cada um com o teste que o prende
- [x] T036 `make lint check` e `tests/test_citacoes_de_requisito.py`
- [x] T037 Suíte inteira: `make test-pg DB_NAME=ps_180`; agrupar falhas por mensagem; se forem de fixture sem data, voltar à T007
- [ ] T038 Percurso manual do `quickstart.md` no navegador, celular incluído (UX-1000), com captura das telas para o PR
- [ ] T039 Nota das Novidades em `processo_seletivo/novidades/novidades.toml`, seguindo `doc/curadoria-das-novidades.md` (só a parte da gestão: conferir identidade)
- [ ] T040 Atualizar a planilha do checklist: tarefa T10 para "Feito" e nota nos itens 3.03 e 3.04

---

## Dependencies & Execution Order

- **Phase 1 → Phase 2** → as histórias.
- **US1** depende só da fundação. **US2** depende da US1 (`falta_o_nucleo` e a tela). **US3** depende
  só da fundação e da T018 (a data gravada na inscrição) para mostrar valor; a ação pode ser feita em
  paralelo com a US2 e testada com uma data gravada à mão.
- **Phase 6** depende da fundação; independe das histórias.
- **Polish** por último; a T037 depois de tudo o que muda código.

## Parallel Opportunities

- Fundação: T002, T003, T005 e T006 juntos; T007 depois de T002.
- US1: T014 enquanto T011 e T012 são escritos.
- US2: T021 e T022 em paralelo.
- US3 inteira em paralelo com a US2, depois da T018.
- T030 e T031 em paralelo com qualquer história.

## Implementation Strategy

1. **MVP = Fundação + US1 + US2**: com elas, todo cadastro novo e todo envio passam a ter a data, que
   é a decisão da reunião e o que o checklist do TMD cobra (itens 3.03 e 3.04).
2. **US3** fecha a finalidade (a conferência). Pode sair no mesmo PR ou num segundo, sem bloquear o
   MVP.
3. **D-003** é pequeno e independente; entra com o MVP.
4. Rodar a suíte inteira **uma vez** depois de ligar a recusa do envio (T017), porque é ela que alcança
   as fixtures de toda a suíte.
