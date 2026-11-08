# Tasks: A jornada não aponta o ato errado

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: pedidos pela spec (FR-4557 a FR-4559). Cada história começa pelo teste que falha.

**Caminhos**: relativos à raiz do repositório. `PS` = `backend/processo_seletivo`, `T` =
`backend/tests`.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [ ] T001 Rodar a linha de base da suíte na branch, antes de qualquer mudança (`DB_NAME=ps_133 make test-pg` a partir de `backend/`), e registrar totais, pulados e falhas em `specs/133-jornada-sem-ato-errado/verificacao.md`
- [ ] T002 [P] Migrar os bancos de fase do estudo (`ps_conv_t2`, `ps_conv_t3`, `ps_conv_t5`, `ps_conv_t6`, `ps_conv_ux`) para a branch com `manage.py migrate --check`, para a demonstração do quickstart

---

## Phase 2: Foundational (bloqueia as histórias)

- [ ] T003 Escrever os testes puros da regra em `T/unit/classificacao/test_marco_intermediario.py`, de modo que falhem antes da implementação:
  - o marco 1 do 900 é intermediário, e o marco que lê é o 2;
  - o marco 2 não é;
  - o sorteio com Etapa de habilitação que nenhum marco lê não é;
  - o marco sem `cutRule`, ou com `governedStage` vazio, seguido de outro, não é (D-001);
  - três marcos em cadeia: os dois primeiros são, o último não;
  - um marco por sorteio cujo corte governa uma Etapa que outro marco lê é intermediário;
  - um Perfil sem marcos não quebra.
- [ ] T004 Implementar `PS/classificacao/domain/marco_intermediario.py`: `marco_que_le(perfil, marco_id)` devolve o marco ou `None`, e `e_intermediario(perfil, marco_id)`. Usar `faixa.etapa_governada`, sem consulta (FR-4530, R-001)
- [ ] T005 Implementar `PS/classificacao/application/marco_intermediario.py`, com `CODIGO = "apuracao_em_marco_intermediario"`. `impedimento(conteudo, perfil_id, marco_id)` devolve `None` ou `{frase, nota, marco_que_le_id, nome_do_marco_que_le}`, e `recusar(...)` levanta `DomainError(CODIGO, frase, 409, campo="marco")`. Frase e nota conforme R-010 e [contracts/recusas.md](contracts/recusas.md), sem identificador interno (FR-4537). Testes da frase em `T/unit/classificacao/test_marco_intermediario.py`
- [ ] T006 Criar a fixture do Edital 900 reduzido, `T/fixtures/marco_intermediario.py` (R-009). Usar os comandos de `reproduzir.py` do estudo e o relógio `tests.fixtures.relatorio.em`:
  - o Perfil: Prova, o marco 1 (fixo 2 por lista, governa a Entrevista, recurso de 3 dias), a Entrevista e o marco 2 (pelo quadro + 1 suplente), com ampla 2 e PcD 1;
  - de 6 a 8 inscrições;
  - funções de parada: `ate_a_ordem_m1`, `ate_a_preliminar_m1`, `ate_o_recurso_deferido`, `ate_a_apuracao_m2`, `ate_a_desistencia_com_titular_pendente`. Cada uma devolve o Edital e o instante.

**Checkpoint**: a regra e a fixture existem; as histórias podem começar.

---

## Phase 3: User Story 1 — O marco intermediário não apura nem convoca (P1) 🎯 MVP

**Goal**: recusa nos comandos, previsão nas telas, *Não se aplica* no andamento (FR-4530 a FR-4540).

**Independent Test**: na fixture, depois da apuração do marco 2: as providências não têm o marco 1, e
apurar ou convocar o marco 1 pelo comando recusa sem gravar nada.

### Testes da US1

- [ ] T007 [P] [US1] Teste de comando em `T/integration/ocupacao/test_apuracao_em_marco_intermediario.py`:
  - `emitir_apuracao` no marco 1, nas duas listas, recusa com `apuracao_em_marco_intermediario`;
  - nenhuma `ApuracaoDeOcupacao`, `MovimentoDeVaga` ou evento de trilha `OCUPACAO_APURAR` é criado;
  - repetir com a mesma chave recusa de novo (FR-4532, FR-4536, SC-1420);
  - `acrescentar_vagas` e `causar_faixa_seguinte` no marco 1 recusam (FR-4533);
  - a apuração do marco 2 continua aceita.
- [ ] T008 [P] [US1] Teste de comando em `T/integration/convocacao/test_convocacao_em_marco_intermediario.py`:
  - `convocar` no marco 1 recusa, e nenhuma `Convocacao` nem comunicação (correio em memória) é
    gravada;
  - o lote ("Convocar titulares") e a correção (`correcao=`) recusam (FR-4534);
  - uma convocação legada, gravada por `bulk_create` no marco 1, ainda recebe desfecho e conferência,
    e o desfecho grava `apuracaoPendente` com o código, sem erro (FR-4535, D-002, R-003);
  - a apuração legada continua legível (FR-4540).
- [ ] T009 [P] [US1] Teste da derivação em `T/unit/interface/test_andamento_marco_intermediario.py`, sobre a fixture:
  - depois da apuração do marco 2, o nível 1 da presidência tem só convocações do marco 2;
  - as células de apuração e convocação do marco 1 são `NAO_SE_APLICA`, com a nota;
  - o resumo do Perfil não conta essas células (FR-4539, SC-1421);
  - com as vagas todas ocupadas, nada em aberto no marco 1.
- [ ] T010 [P] [US1] Teste das telas em `T/interface/test_telas_do_marco_intermediario.py`:
  - a ocupação e a convocação do marco 1 mostram o aviso com o link do marco que apura, sem `<form>`
    de apurar, suceder, acrescentar, faixa, convocar ou corrigir;
  - o gesto "Apurar" da condução põe os recortes entre os impedidos (FR-4538);
  - um POST direto às rotas de emitir apuração e de convocar do marco 1 volta com a recusa, e nada é
    gravado (SC-1420, "pela tela").

### Implementação da US1

- [ ] T011 [US1] Chamar `marco_intermediario.recusar` em `PS/ocupacao/application/emissao.py`, `_apurar`, logo depois de `effective_version` e antes de ler o corte (R-002)
- [ ] T012 [US1] Chamar a recusa em `PS/ocupacao/application/acrescimo.py`, `acrescentar_vagas`, sob a trava e antes de `_previa`, e em `PS/ocupacao/application/causar_faixa.py`, `causar_faixa_seguinte`, no início, com o conteúdo vigente (R-002)
- [ ] T013 [US1] Chamar a recusa em `PS/convocacao/application/convocar.py`, `convocar`, sob a trava e antes de montar o contexto do recorte (cobre o lote e a correção, R-002)
- [ ] T014 [US1] Em `PS/interface/conducao_do_marco.py`:
  - `_celula_da_apuracao` devolve `nao_se_aplica` com a nota da recusa e sem URL quando o marco é
    intermediário;
  - `_alcance_da_apuracao` marca os recortes `IMPEDIDO`, com a frase (R-004).
- [ ] T015 [US1] Nas views `ocupacao` e `convocacao` de `PS/interface/views.py`, levar `marco_intermediario` (frase, nome e URL do marco que apura) ao contexto. Em `PS/interface/templates/interface/ocupacao.html` e `convocacao.html`, trocar os formulários pelo aviso, com o que existe ainda legível. A classe do aviso precisa ter regra na folha da tela
- [ ] T016 [US1] Conferir que `PS/interface/andamento.py` não precisa de regra própria: `situacao_da_apuracao` e `situacoes_da_convocacao` já seguem a célula. Ajustar só se o T009 falhar, e registrar em `research.md`

**Checkpoint**: US1 verde (T007 a T010); o MVP pode ser demonstrado no `ps_conv_t5`.

---

## Phase 4: User Story 2 — O corte espera o prazo recursal, como recomendação (P2)

**Goal**: FR-4541 a FR-4546.

**Independent Test**: na fixture, depois da preliminar do marco 1: o corte em espera, sem "SUA"; a tela
do corte com o aviso e o botão; o comando aceita.

### Testes da US2

- [ ] T017 [P] [US2] Testes puros de `espera_do_corte` e de `situacao_do_corte` em `T/unit/interface/test_andamento_situacoes.py` (R-005):
  - sem recurso declarado: nenhuma espera;
  - não divulgado: espera sem data;
  - `JANELA_ABERTA` e `RECURSO_PENDENTE`: espera com a data;
  - prazo encerrado sem pendência e definitiva não publicada: nenhuma espera (D-003);
  - a célula sai `AGUARDA`, com `recomendacao=True` e sem responsável.
- [ ] T018 [P] [US2] Teste da derivação na fixture, em `T/unit/interface/test_andamento_marco_intermediario.py`:
  - na parada da ordem, o "Próximo nesta lista" é "Publicar o resultado", e o corte está em espera
    (FR-4543);
  - na parada da preliminar, nenhuma providência "sua" de corte, e a espera tem a data (SC-1422).
- [ ] T019 [P] [US2] Teste da tela em `T/interface/test_corte.py`: com o prazo aberto, o aviso da consequência aparece antes do formulário de emissão, e o botão continua; emitir é aceito (FR-4544, FR-4545)

### Implementação da US2

- [ ] T020 [US2] Em `PS/interface/andamento.py`:
  - acrescentar `recomendacao: bool = False` a `Celula`;
  - criar `espera_do_corte(marco, *, divulgado, definitiva)`, pura;
  - fazer `situacao_do_corte` receber `espera`.
- [ ] T021 [US2] Em `PS/interface/andamento.py`:
  - `_resultado` passa a devolver também a aferição lida;
  - `_marco` deriva o resultado antes do corte e passa a espera;
  - `da_lista` prefere o que é da pessoa, depois o que se pratica, e só então o que espera (R-005).
- [ ] T022 [US2] Em `PS/interface/templates/interface/_providencia.html`, desenhar a marca "recomendação" quando `recomendacao`, com a regra de estilo na folha da gestão
- [ ] T023 [US2] Na view `corte` de `PS/interface/views.py`, aferir a definitiva ou a primeira publicação da ordem vigente da lista e passar por `espera_do_corte`. Em `PS/interface/templates/interface/corte.html`, mostrar o aviso da consequência antes do formulário de emissão

**Checkpoint**: US2 verde; demonstrável no `ps_conv_t2`.

---

## Phase 5: User Story 3 — A próxima da fila aparece quando há vaga a ocupar (P2)

**Goal**: FR-4547 a FR-4549.

**Independent Test**: na fixture, na parada da desistência com titular pendente, "Chamar a próxima da
fila" aparece, como na tela da convocação.

- [ ] T024 [P] [US3] Testes em `T/unit/interface/test_andamento_situacoes.py` (a conta) e `T/unit/interface/test_andamento_marco_intermediario.py`, na parada da desistência:
  - "Chamar a próxima da fila" é providência de quem conduz;
  - a resposta do titular está em espera;
  - com chamada aberta para a vaga que vagou, "Chamar a próxima" não aparece (FR-4547 a FR-4549,
    SC-1423);
  - a tela da convocação e o andamento apontam a mesma próxima ação na mesma parada (FR-4549).
- [ ] T025 [US3] Em `PS/interface/andamento.py`, `_Leitor._convocacao`: `em_aberto` passa a contar só as linhas sem desfecho com `especie != nomes.VAGA_INICIAL` (R-006)

---

## Phase 6: User Story 5 — O Edital diz "de cada lista" (P2)

**Goal**: FR-4553 a FR-4556.

**Independent Test**: a frase com e sem reservada; o documento publicado com o mesmo resumo; a
Retificação sem alteração do corte.

- [ ] T026 [P] [US5] Testes em `T/unit/publicacoes/test_redacao_das_frases.py`:
  - alvo fixo com reservada: "de cada lista de concorrência";
  - alvo 1 com reservada;
  - alvo fixo só com a ampla: frase de hoje;
  - alvo do quadro: inalterado (FR-4553, FR-4554).
- [ ] T027 [P] [US5] Testes de preservação:
  - um Edital publicado antes da mudança mantém os bytes e o resumo do documento (FR-4555, SC-1425);
  - uma Retificação que não mexe no corte não aponta alteração do corte (FR-4556, SC-1426).

  Ficam em `T/integration/publicacoes/test_frase_do_corte_por_lista.py`.
- [ ] T028 [US5] Em `PS/publicacoes/infrastructure/pdf.py`, `frases_do_corte(..., com_reservadas=False)` (R-008). Passar o valor do Perfil em `pdf.py:2538`, `PS/publicacoes/infrastructure/apresentacao.py:1133` e `PS/interface/revisao.py:607`
- [ ] T029 [US5] Rodar os testes de documento e de redação. Atualizar cada expectativa de texto que mudou por causa da frase, e listar cada uma, com o motivo, em `specs/133-jornada-sem-ato-errado/verificacao.md` (risco da R-008)

---

## Phase 7: User Story 4 — Ninguém é mandado publicar o que o comando recusa (P3)

**Goal**: FR-4550 a FR-4552.

**Independent Test**: na fixture, na parada do recurso deferido: a definitiva da lista com ordem
obsoleta não é *Pendente*.

- [ ] T030 [P] [US4] Testes:
  - em `T/unit/interface/test_andamento_situacoes.py`: ordem obsoleta com preliminar feita dá
    `DEPOIS`;
  - na fixture, na parada do recurso deferido: a definitiva da ampla não é *Pendente* para quem
    publica (SC-1424);
  - corte obsoleto com preliminar feita dá *Impedido*, com a razão.
- [ ] T031 [US4] Em `PS/interface/andamento.py`, `situacao_do_resultado`: a ordem obsoleta dá `DEPOIS` antes de olhar o estado da publicação (R-007)

---

## Phase 8: Polish & Cross-Cutting

- [ ] T032 [P] Teste de coerência na fixture (FR-4552, SC-1424): nenhuma célula *Pendente* do andamento corresponde a comando que recusaria. Para cada célula *Pendente* de apuração, convocação e publicação, chamar o comando numa transação desfeita e conferir que não recusa por motivo que a derivação conhece
- [ ] T033 [P] Confirmar que os casos da `127` e da `016` para marco sem sucessor que o leia passam sem mudança de expectativa (FR-4559, SC-1427): rodar `T/unit/interface/test_andamento_*.py`, `T/integration/ocupacao/` e `T/integration/convocacao/`
- [ ] T034 Escrever `specs/133-jornada-sem-ato-errado/rastreabilidade.md`, com cada FR-4530 a FR-4559 e SC-1420 a SC-1428 ligados a um teste ou à verificação
- [ ] T035 `make lint check`, `manage.py makemigrations --check --dry-run` (SC-1428) e `DB_NAME=ps_133 make test-pg` a partir de `backend/`. Comparar com a linha de base do T001, por lista, e não por total; anotar o resultado dos testes de desempenho da tela do corte (uma aferição a mais por lista); registrar em `verificacao.md`
- [ ] T036 Demonstrar no navegador, conforme o [quickstart](quickstart.md), nos bancos de fase. Gravar as capturas antes e depois em `specs/133-jornada-sem-ato-errado/capturas/` e o resultado em `verificacao.md` (princípio VI)
- [ ] T037 [P] Atualizar a linha da `133` no `README.md` (estado) e, se o número de tabelas append-only ou de migrations não mudou, nada no `CLAUDE.md`

---

## Dependencies & Execution Order

- **Setup (T001, T002)**: primeiro. O T002 é independente.
- **Foundational (T003 a T006)**: bloqueia tudo. T003 → T004 → T005; o T006 pode correr ao lado.
- **US1 (T007 a T016)**: depende da Foundational. É o MVP.
- **US2 (T017 a T023)**, **US3 (T024, T025)**, **US5 (T026 a T029)**, **US4 (T030, T031)**: dependem
  da Foundational (a fixture). Entre si, US2, US3 e US4 tocam `andamento.py`, então são sequenciais
  nesse arquivo: US2, depois US3, depois US4. A US5 toca outros arquivos e pode correr ao lado.
- **Polish (T032 a T037)**: depois de todas.

### Parallel Opportunities

- T007, T008, T009 e T010: arquivos de teste diferentes.
- A US5 inteira, ao lado das US2 a US4.
- T032, T033 e T037.

## Implementation Strategy

1. **MVP:** Setup + Foundational + US1. Isso já fecha o único risco de erro administrativo, e é
   demonstrável no `ps_conv_t5`.
2. Depois US2, US3 e US4, em sequência no `andamento.py`, com a US5 em paralelo.
3. Polish, com a suíte inteira e a demonstração.
