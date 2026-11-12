# Tasks: Destinação da vaga reservada sem ocupante

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/comandos-e-telas.md](contracts/comandos-e-telas.md),
[quickstart.md](quickstart.md)

**Testes**: pedidos. A Constituição e o projeto escrevem o teste antes, e cada cenário da spec e da
[verificação](verificacao-do-levantamento.md) vira caso. Caminhos relativos a `backend/`, salvo dito.

**Incrementos do plano → histórias**:
- A = US4 (passagem entre cotas);
- B = US3 + US1 (condição e destinação por esgotamento);
- C = US2 + US6 (não preenchida, silente, desfazimentos);
- D = US5 (lista vazia e sorteio);
- E = US7 (pública e relatório);
- **F = bloqueado pela D-015** (reversão por saldo).

## Formato: `[ID] [P?] [Story] Descrição`

---

## Phase 1: Setup

- [x] T001 Conferir o ambiente da worktree: `uv sync --extra dev`, `.env` com `DB_NAME` próprio (`ps_elegant_robinson_155`) e `POSTGRES_USER=$USER`, `manage.py migrate --check` limpo, em `backend/.env`
- [x] T002 Escrever `specs/155-destinacao-da-vaga-sem-concorrente/rastreabilidade.md` com **todas** as linhas desde o início, uma por FR, SC e UX da spec, a coluna do teste preenchida ao longo das tarefas: o guardião cobra a cobertura assim que o arquivo existe

## Phase 2: Foundational (bloqueia todas as histórias)

- [x] T003 Teste das constraints e do gatilho das colunas novas e da tabela nova (inserção válida, `UPDATE`/`DELETE` recusados, `ck_*` de cada regra do data-model) em `tests/unit/ocupacao/test_vaga_nao_preenchida_append_only.py` e `tests/unit/ocupacao/test_movimento_com_recorte.py`
- [x] T004 Acrescentar ao `MovimentoDeVaga` as colunas `edital`, `perfil_id`, `marco_id`, `gatilho`, `fundamento`, `versao`, `desfaz`, a espécie `DESFAZIMENTO_DA_REVERSAO`, `apuracao` nula e as constraints `ck_movimento_especie`, `ck_movimento_com_recorte` e `ck_desfazimento_cita_o_movimento`, em `processo_seletivo/ocupacao/models.py`
- [x] T005 Criar o modelo `VagaNaoPreenchida` (append-only por `save`/`delete`) e a coluna `ApuracaoDeOcupacao.nao_preenchidas`, com `ck_apuracao_ocupadas_no_limite` estendida, em `processo_seletivo/ocupacao/models.py`
- [x] T006 Escrever a migration `processo_seletivo/ocupacao/migrations/0005_destinacao_da_vaga.py`: as colunas, a tabela, o gatilho `reject_occupancy_mutation()` na tabela nova, guardado por `vendor == "postgresql"`, como a `0004`
- [x] T007 Registrar a tabela nova em `TABELAS_APPEND_ONLY`, com justificativa, em `processo_seletivo/seguranca/papeis.py`; atualizar `tests/seguranca/test_homologacao_preservada.py` (59 e o recorte final) e a contagem no `CLAUDE.md` ("são **59** com a vaga não preenchida da `155`")
- [x] T008 [P] Acrescentar a `processo_seletivo/ocupacao/domain/nomes.py`:
  - `PASSAGEM_ENTRE_COTAS` e `DECLARACOES_DE_REVERSAO`;
  - as espécies novas;
  - os códigos de recusa do contrato;
  - a causa `CAUSA_DECLARACAO_POSTERIOR`.
- [x] T009 Fazer `_movimentos_que_alcancam` e `_movimento_posterior` lerem também o recorte próprio do movimento, e acrescentar a causa `declaracao_posterior` a `causas_de_obsolescencia`, em `processo_seletivo/ocupacao/application/selectors.py`; teste de que nenhuma leitura por `apuracao__edital` ficou sem o recorte próprio em `tests/unit/ocupacao/test_leitura_do_movimento_sem_apuracao.py`
- [x] T010 Ensinar `calculo.apurar` a ler o desfazimento como movimento e `faltando` a descontar `nao_preenchidas`, em `processo_seletivo/ocupacao/domain/apuracao.py`, com casos em `tests/unit/ocupacao/test_apuracao_com_destinacao.py`

**Checkpoint**: `make test-pg` verde com as migrations novas e nenhum comportamento mudado.

---

## Phase 3: US4 — O Edital manda passar antes por outras cotas (incremento A, P2)

**Goal**: a terceira resposta é declarável, publicada, retificável, e nunca move vaga (D-016).
**Independent Test**: Perfil com a resposta nova publica; `quantidade_a_reverter` devolve 0; a
destinação e a não preenchida são recusadas com `passagem_entre_cotas`.

- [x] T011 [P] [US4] Testes da validação e da não cessão em `tests/unit/editais/test_reversao_declarada.py` e `tests/unit/ocupacao/test_reversao.py` (a resposta nova é aceita; não entra em `ESPECIES_DE_REVERSAO`; cede 0)
- [x] T012 [US4] `reversao.declarada` devolve as três respostas e `especie_que_move` só as duas, em `processo_seletivo/ocupacao/domain/reversao.py`; revisar os chamadores (`emissao.py:233`, `acrescimo.py:74`, `rodada_da_previa.py:89`, `interface/views.py:3487`)
- [x] T013 [US4] Aceitar a resposta nova em `processo_seletivo/editais/domain/validation.py::_reversao_declarada` (mensagem com as três) e nos *choices* de `processo_seletivo/editais/models/perfis.py`, com a migration nova de `editais` e o ajuste do guardião de contagem em `tests/migrations/test_migrations.py`
- [x] T014 [P] [US4] A terceira `<option>` em `processo_seletivo/interface/templates/interface/_perfil.html` e `compor_perfis.html`; leitura em `processo_seletivo/interface/forms.py`, sem palavra que a varredura da composição exija em `<dfn>`
- [x] T015 [P] [US4] As frases nos dois dicionários de `processo_seletivo/publicacoes/infrastructure/pdf.py`, contendo "de um código", e o caso em `tests/unit/publicacoes/test_redacao_das_frases.py`
- [x] T016 [P] [US4] Retificação, revisão e palavras: `processo_seletivo/interface/retificacao.py`, `aplicacao_na_retificacao.py`, `revisao.py`, `aplicacao.py::_valor_do_campo_em_palavras`; testes em `tests/interface/test_retificar_reversao.py` e `tests/interface/test_correcoes_de_norma_na_revisao.py`
- [x] T017 [P] [US4] O rótulo em `processo_seletivo/duvidas/domain/rotulos.py` e nas prévias `processo_seletivo/interface/previa_da_classificacao.py` e `previa_do_sorteio.py` ("o Edital manda passar por outras cotas; o GPS ainda não aplica"); casos em `tests/unit/duvidas/test_casos_da_revisao.py` e `tests/interface/test_previa_por_recorte.py`
- [x] T018 [P] [US4] O `enum` e a descrição em `specs/001-processo-seletivo-editais/contracts/openapi.yaml` (raiz do repositório)

**Checkpoint**: a passagem entre cotas é declarável e inerte.

---

## Phase 4: US3 — A condição de cada gatilho (incremento B, P1)

**Goal**: a condição do esgotamento (FR-6304) e os impedimentos (FR-6306), puros, lidos pela tela e
pelo comando. **O saldo fica fora** (incremento F).
**Independent Test**: os cenários 1 a 6 da US3 e o 7 por esgotamento, no caminho oficial.

- [X] T019 [P] [US3] Testes puros de `ainda_podem_ocupar`, `impedimentos` e `situacao` em `tests/unit/ocupacao/test_destinacao_dominio.py`:
  - posição vazia;
  - excluído por desfecho;
  - ocupante da ampla com e sem aceite;
  - fora da faixa com e sem continuação;
  - resultado provisório;
  - prazo recursal e recurso pendente;
  - chamada em curso;
  - apuração obsoleta.
- [X] T020 [US3] Escrever `processo_seletivo/ocupacao/domain/destinacao.py` (R-004), com `situacao` devolvendo os estados do data-model; por saldo, `aguarda_d015`
- [X] T021 [US3] Escrever `processo_seletivo/interface/destinacao_da_vaga.py`: os fatos externos de `divulgacao` (`vigente_do_marco`, `janela_aberta_ate`), `recursos` (`recursos_pendentes_do_marco`) e `convocacao` (em aberto), uma vez por marco, e a situação de cada recorte (R-008)
- [X] T022 [US3] Testes de integração V-1, V-2, V-4 e V-5 com o resultado novo (destinação oferecida; sem aceite na ampla, impedida) em `tests/integration/ocupacao/test_condicao_do_esgotamento.py`, sobre `tests/fixtures/ocupacao_sorteada.py`

---

## Phase 5: US1 — A presidência destina a vaga (incremento B, P1)

**Goal**: "Destinar à ampla concorrência" por ato próprio, por esgotamento.
**Independent Test**: a US1 com reversão por esgotamento: o registro, a soma, a idempotência, a
sucessora da origem e a ampla obsoleta.

- [X] T023 [P] [US1] Testes do comando em `tests/integration/ocupacao/test_destinacao.py`:
  - grava o movimento com as colunas novas;
  - a sucessora da origem lê o movimento;
  - a ampla fica obsoleta;
  - a soma das efetivas não muda;
  - a confirmação repetida e a simultânea dão um registro só;
  - as recusas do contrato;
  - o movimento antigo conta como destinação feita (FR-6316);
  - relido depois de uma Retificação, o ato devolve a declaração e a quantidade que leu (FR-6342).
- [X] T024 [US1] Escrever `previa_da_destinacao` e `destinar_vaga` em `processo_seletivo/ocupacao/application/destinacao.py`, no molde de `acrescimo.py` (assinatura, `comando_de_comissao`, `auditar` com `OCUPACAO_DESTINAR_VAGA`, sucessora no *savepoint*)
- [X] T025 [US1] Tirar o ramo de cessão de `_apurar` para a declaração por esgotamento — só a por saldo ainda move (R-010) — em `processo_seletivo/ocupacao/application/emissao.py`; ajustar `convocacao/application/desfechar.py::apuracao_seguinte`, que deixa de devolver `MOVERIA_VAGA` por esgotamento
- [X] T026 [US1] Rotas e views `interface:destinar-vaga` (prévia e confirmação) e a conferência `processo_seletivo/interface/templates/interface/ocupacao_destinacao.html`, no molde de `ocupacao_acrescimo.html`, com o lembrete da passagem entre cotas (FR-6309); regras de folha para toda classe nova em `processo_seletivo/interface/static/interface/gestao/` ou `interface/telas/`
- [X] T027 [US1] A situação de cada recorte e os botões em `processo_seletivo/interface/templates/interface/ocupacao.html` (parcial `_situacao_da_vaga.html`), com a frase de UX-600
- [X] T028 [US1] O Centro: o ramo `IMPEDIDO` de `situacoes_da_convocacao` lê a situação, em `processo_seletivo/interface/andamento.py`; a convocação: `_vaga_sem_chamada` cita a situação com a fila vazia, em `processo_seletivo/interface/conducao_da_convocacao.py` (anotar o conflito com o #489)
- [X] T029 [US1] As prévias e as equivalências (R-011): `processo_seletivo/ocupacao/domain/rodada_da_previa.py` usa a condição nova por esgotamento; `tests/integration/classificacao/test_previa_por_recorte_equivale_ao_oficial.py` e `tests/integration/sorteios/test_previa_do_sorteio_equivale_ao_oficial.py` leem o lado oficial pela destinação; `tests/unit/ocupacao/test_ha_quem_ocupar.py` e `test_rodada_da_previa.py`
- [X] T030 [US1] Testes de tela em `tests/interface/test_destinacao_na_ocupacao.py`:
  - a situação nas três telas;
  - a conferência;
  - a recusa a quem não pode;
  - nenhum ato que o comando recusaria (SC-2101).

**Checkpoint**: MVP — a destinação por esgotamento de ponta a ponta.

---

## Phase 6: US2 — O Edital silente e a vaga não preenchida (incremento C, P1)

**Goal**: sem reversão declarada, nada move; a declaração fundamentada, também na linha geral (D-014).
**Independent Test**: a US2 no C09.

- [X] T031 [P] [US2] Testes em `tests/integration/ocupacao/test_nao_preenchida.py`:
  - a declaração com e sem fundamento;
  - na reserva sem reversão;
  - na linha geral;
  - recusas `o_edital_manda_destinar` e `passagem_entre_cotas`;
  - `faltando` desconta;
  - a causa `declaracao_posterior`;
  - a reprodução da declaração relida depois (FR-6342).
- [X] T032 [US2] Escrever `previa_da_nao_preenchida` e `declarar_nao_preenchida` em `processo_seletivo/ocupacao/application/destinacao.py`, com o evento `OCUPACAO_DECLARAR_NAO_PREENCHIDA` e a sucessora do recorte
- [X] T033 [US2] Rota `interface:declarar-nao-preenchida`, a conferência e o campo de fundamento (área de texto, molde da `058`), em `processo_seletivo/interface/views.py` e `templates/interface/ocupacao_destinacao.html`
- [X] T034 [US2] A frase do Edital silente com os dois caminhos — o link para a Retificação, quando a fase a admite, e a declaração — em `_situacao_da_vaga.html`; teste em `tests/interface/test_destinacao_na_ocupacao.py` (o C09)

## Phase 7: US6 — Os desfazimentos (incremento C, P3)

- [X] T035 [P] [US6] Testes em `tests/integration/ocupacao/test_desfazimento_da_destinacao.py`:
  - sem chamada dependente, os dois registros e a soma de volta;
  - com chamada dependente, a recusa 409 e o evento `OCUPACAO_DESFAZIMENTO_IMPEDIDO` gravado com as chamadas;
  - o mesmo para a não preenchida.
- [X] T036 [US6] Escrever `desfazer_destinacao` e `desfazer_nao_preenchida`, com `chamadas_dependentes` injetado (R-005), em `processo_seletivo/ocupacao/application/destinacao.py`; a composição do *callable* em `processo_seletivo/interface/destinacao_da_vaga.py`
- [X] T037 [US6] Rotas `interface:desfazer-destinacao` e `interface:desfazer-nao-preenchida`, a conferência com motivo, e a recusa que nomeia "pessoa chamada para esta vaga" (sem o vocabulário que a varredura da ocupação proíbe)

---

## Phase 8: US5 — A lista vazia (incremento D, P2)

**Goal**: um gesto com conferência; a lista entra na publicação do marco; o sorteio sem relação, com
ausência comprovada.
**Independent Test**: a US5 no C09 e num sorteio com a PPI vazia.

- [X] T038 [P] [US5] Testes em `tests/interface/test_lista_sem_concorrente.py`:
  - o gesto emite a ordem vazia e o corte vazio numa conferência;
  - nenhuma posição gravada (FR-6329);
  - recusa `lista_com_concorrente`;
  - a idempotência.
- [X] T039 [US5] A view `interface:registrar-lista-sem-concorrente` e a conferência, sobre `emitir_ordem` e `emitir_corte`, em `processo_seletivo/interface/views.py` e `templates/interface/ordenacao_lista_sem_concorrente.html`; o evento `CLASSIFICACAO_LISTA_SEM_CONCORRENTE`; a providência da `135` aponta o gesto em `processo_seletivo/interface/andamento.py`
- [X] T040 [P] [US5] Testes da publicação conjunta em `tests/integration/divulgacao/test_publicacao_conjunta.py`:
  - a lista vazia publicada na mesma transação;
  - a assinatura cobre;
  - a natureza é a mesma;
  - não republica.
- [X] T041 [US5] A publicação conjunta em `processo_seletivo/divulgacao/application/publicar.py` e a prévia em `processo_seletivo/interface/views.py::publicar_resultado`; a célula do resultado da lista vazia no andamento
- [X] T042 [US5] O sorteio sem relação (R-007): a ausência comprovada em `processo_seletivo/interface/destinacao_da_vaga.py`, com o movimento sem apuração de origem; testes em `tests/integration/ocupacao/test_destinacao_no_sorteio.py` (relação da ampla congelada; não congelada não oferece)

---

## Phase 9: US7 — O candidato vê para onde a vaga foi (incremento E, P3)

- [X] T043 [P] [US7] Testes em `tests/portal/test_destinacao_na_selecao.py` e `tests/interface/test_relatorio_do_edital.py`:
  - origem, destino, quantidade e fundamento;
  - o desfazimento citando;
  - nenhum nome nem protocolo;
  - sem PDF novo.
- [X] T044 [US7] O seletor `destinacoes_publicas` em `processo_seletivo/ocupacao/application/selectors.py`, o parcial `processo_seletivo/portal/templates/portal/_destinacao_das_vagas.html`, a inclusão em `portal/selecao.html` e o contexto em `processo_seletivo/portal/views.py::selecao`; regras na folha do portal
- [X] T045 [US7] A seção "Destinação das vagas" em `processo_seletivo/interface/relatorio_do_edital.py` e no template do relatório
- [X] T046 [US7] O fundamento da chamada para vaga destinada (FR-6340), lido do `movimentosLidos` da apuração da chamada, em `processo_seletivo/convocacao/application/` (o ponto exato no T046; anotar conflito com o #489)
  - o ponto: `convocar.py`, nos dois lugares que gravam `Convocacao` (`convocar` e `convocar_em_sequencia`), e as prévias em `fluxo.py`; a citação vem de `ocupacao.application.selectors.destinacoes_lidas_por` e se escreve em `convocacao/domain/fundamento.py`;
  - sem conflito com o #489: nenhum dos três arquivos dele (`interface/conducao_da_convocacao.py`, `interface/templates/interface/convocacao.html`, `interface/views.py`) foi tocado.

---

## Phase 10: Incremento F — **BLOQUEADO pela D-015** (reversão por saldo)

> Nada desta fase se implementa antes de o usuário escolher uma opção da D-015. As tarefas descrevem o
> que muda em cada opção.

- [ ] T047 [BLOQUEADA] [US1] Escrever a condição da FR-6305 pela opção escolhida em `processo_seletivo/ocupacao/domain/destinacao.py`; na A2, também o ato de encerramento da chamada de suplentes, com requisito próprio na spec
- [ ] T048 [BLOQUEADA] [US1] Tirar o último ramo de cessão de `_apurar` (a por saldo) em `processo_seletivo/ocupacao/application/emissao.py`
- [ ] T049 [BLOQUEADA] [US3] Os cenários S-1 a S-4 da verificação como testes de integração em `tests/integration/ocupacao/test_condicao_do_saldo.py`
- [ ] T050 [BLOQUEADA] [US1] As prévias por saldo e as equivalências

---

## Phase 11: Polish

- [x] T051 [P] Varreduras:
  - `tests/test_vocabulario_da_ocupacao.py` cobre os arquivos novos da ocupação;
  - `tests/test_gramatica_das_portas.py` cobre as views novas e cada `Http404` no inventário da `033`;
  - `tests/test_citacoes_de_requisito.py`;
  - uma varredura nova, em `tests/test_gravacao_da_destinacao.py`, de que só os comandos de `ocupacao/application/destinacao.py` e o ramo por saldo de `emissao.py` criam `MovimentoDeVaga` e `VagaNaoPreenchida` (SC-2103).
- [x] T052 [P] Completar `specs/155-destinacao-da-vaga-sem-concorrente/rastreabilidade.md` e marcar no README a linha da `155`
- [x] T053 Integrar o que entrou na `main` nos mesmos arquivos (o #489 e outros) e resolver os conflitos preservando os requisitos de cada incremento
- [x] T054 `cd backend && make lint check test-pg`, com o resultado no PR
- [ ] T055 *(parcial: o C09 de ponta a ponta, a 1366 e a 390 px; o Edital por esgotamento e a passagem entre cotas ficaram nos testes de tela)* A jornada do quickstart no navegador: o C09, um Edital por esgotamento e um com a passagem entre cotas, a 1366 e a 390 px, sem violação da CSP; capturas no PR

## Dependencies

- Setup → Foundational → todas as histórias.
- **US4 (A)** sozinha, depois da Foundational.
- **US3 → US1 (B)**.
- **US2 e US6 (C)** dependem de US3.
- **US5 (D)** depende de US3 e do movimento sem apuração (T004, T009).
- **US7 (E)** depende de US1 e US2.
- **F** depende da D-015, e de B.

## Parallel

- **Na Foundational**: T008 com T003.
- **US4**: T014, T015, T016, T017 e T018, em arquivos diferentes.
- **Os testes de cada história** (T019, T023, T031, T035, T038, T040, T043) se escrevem em paralelo
  com o código da história anterior.

## Implementation Strategy

1. **MVP**: Setup + Foundational + US3 + US1 — a destinação por esgotamento como ato próprio.
2. **Depois**: US4, US2, US6, US5 e US7, cada uma com o seu *checkpoint*.
3. **F** só depois da D-015.
4. **Um PR de implementação**, sem merge, com as pendências: a D-015 (F), o conflito com o #489 e as
   capturas.
