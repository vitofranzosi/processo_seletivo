# Tasks: O efeito do desfecho da Etapa por lista

**Input**: `specs/164-efeito-do-desfecho-por-lista/`, com spec, plan, research, data-model e
contracts.

**Tests**: obrigatórios neste repositório (Constituição, V). Cada história tem os seus, e a matriz
`rastreabilidade.md` liga cada FR e cada caso-limite a teste.

Os caminhos são relativos a `backend/`. `[P]` marca arquivo distinto, sem dependência de tarefa
aberta. A base é a branch da `163` (`claude/163-alcance-da-etapa`).

## Phase 1: Setup

- [x] T001 Conferir o ambiente da worktree (CLAUDE.md, *Subir o ambiente*):
  - `uv sync --extra dev`;
  - `DB_NAME` próprio;
  - PostgreSQL com o par `TEST_DB_ENGINE` e `DB_USER`;
  - `manage.py migrate --check` limpo sobre a base da `163`.

## Phase 2: Foundational (bloqueia todas as histórias)

- [x] T002 Acrescentar `efeito_desfavoravel` e `efeito_da_ausencia` a `EtapaAvaliacao`, com
  `choices`, `default=""`, as duas `CheckConstraint` e o comentário do porquê, em
  `processo_seletivo/editais/models/etapas.py` (data-model; FR-7000, FR-7004).
- [x] T003 Acrescentar `Consequencia.RETIRADA_DA_RESERVA` e ampliar `ck_resultado_consequencia` em
  `processo_seletivo/resultados/models.py`. Ampliar `ck_decisao_consequencia` em
  `processo_seletivo/recursos/models.py`.
- [x] T004 Gerar as três migrations e atualizar a contagem por app do guardião da `022`:
  - `processo_seletivo/editais/migrations/0030_efeito_do_desfecho.py`;
  - `processo_seletivo/resultados/migrations/0007_retirada_da_reserva.py`;
  - `processo_seletivo/recursos/migrations/0004_retirada_da_reserva.py`.
- [x] T005 [P] Criar `processo_seletivo/resultados/domain/efeito.py` (research T-003): `efeito_desfavoravel`,
  `efeito_da_ausencia`, `consequencia_do_efeito`, `GRAVIDADE`, `mais_grave`, `desfavoravel`,
  `frase_do_efeito` e `frase_da_reserva`.
- [x] T006 [P] Testes de unidade de `efeito.py` em `tests/unit/resultados/test_efeito_do_desfecho.py`:
  - acervo nulo lido como elimina (FR-7001, D-002);
  - Etapa para todas e Etapa não eliminatória sem efeito (FR-7002);
  - ausência "o mesmo" (FR-7004);
  - gravidade;
  - as quatro frases do contrato.
- [x] T007 Subir o degrau do conteúdo publicado:
  - `SCHEMA_VERSION = 23` em `processo_seletivo/shared/canonical.py`;
  - `DEGRAUS[23]` em `processo_seletivo/publicacoes/domain/elevacao.py`;
  - os dois campos em `_stages` de `processo_seletivo/publicacoes/application/publish_edital.py`,
    com o valor explícito só na Etapa restrita e eliminatória (research T-002).
- [x] T008 (FR-7006) Os dois campos como `retificavel()` em `processo_seletivo/editais/domain/mutabilidade.py`,
  e no Edital máximo da fixture do guardião de mutabilidade.
- [x] T009 Ajustar os testes que fixam a versão 22 e confirmar que o acervo de fixture recompõe o
  mesmo resumo e o mesmo documento (SC-2330).

**Checkpoint**: os campos existem, viajam no conteúdo publicado, a consequência nova é aceita pelo
banco e o acervo não muda.

## Phase 3: User Story 1 — Quem elabora declara o que o desfecho desfavorável produz (P1)

**Goal**: declarar, validar, publicar e ler o efeito. **Independent test**: compor e publicar o
Edital da spec; conferir o conteúdo, a Revisão e o documento.

- [x] T010 [P] [US1] Testes em `tests/integration/editais/test_publicacao_do_efeito.py`:
  - o padrão gravado na Etapa restrita e eliminatória (FR-7001);
  - `efeito_sem_reserva` na Etapa para todas e na não eliminatória (FR-7002);
  - o valor inválido recusado na gravação;
  - `null` nas Etapas sem declaração (FR-7005).
- [x] T011 [US1] Receber, conferir e gravar os dois campos:
  - `validate_stage` em `processo_seletivo/editais/domain/etapas.py`;
  - gravação e leitura no rascunho em `processo_seletivo/editais/application/draft.py`;
  - os campos em `processo_seletivo/editais/api/serializers.py`.
- [x] T012 [US1] O achado `efeito_sem_reserva` em `processo_seletivo/editais/domain/validation.py`
  (contrato `recusas.md`).
- [x] T013 [P] [US1] O efeito na cópia do Edital em `processo_seletivo/editais/domain/reaproveitamento.py`.
- [x] T014 [US1] A composição (UX-740, UX-741):
  - o grupo do efeito no formulário e no template (`processo_seletivo/interface/forms.py`,
    `templates/interface/_etapa.html`);
  - mostrá-lo e escondê-lo em `static/interface/alcance.js`;
  - as regras na folha da tela.
- [x] T015 [US1] A frase do efeito (FR-7023):
  - no documento, nas três redações, em `processo_seletivo/publicacoes/infrastructure/pdf.py`;
  - na Revisão (`processo_seletivo/interface/revisao.py`);
  - na página pública (`processo_seletivo/publicacoes/infrastructure/apresentacao.py`).
- [x] T016 [P] [US1] Testes de interface e de documento em `tests/interface/test_composicao_do_efeito.py`:
  - o grupo só na Etapa restrita e eliminatória, sem estilo inline;
  - a frase no PDF;
  - nenhum texto novo na Etapa sem declaração.

## Phase 4: User Story 2 — O desfecho desfavorável tira da reserva e deixa na ampla (P1)

**Goal**: o Resultado de retirada, e o que cada lista faz com ele. **Independent test**: consolidar
um `PPI` desfavorável e conferir a ordem dos dois recortes, a participação na Análise documental, a
ocupação e a fila.

- [x] T017 [P] [US2] Testes em `tests/integration/resultados/test_retirada_da_reserva.py`:
  - consolidação com cada efeito (FR-7007), e o motivo com a reserva (FR-7008);
  - a Regra 2 aceita a retirada (FR-7011);
  - a faixa só pela ampla (FR-7013): coberta pela T047, com cenário próprio de corte;
  - elimina igual a hoje (SC-2332);
  - a eliminação posterior prevalece;
  - um efeito por Etapa, qualquer que seja o motivo da avaliação (FR-7003).
- [x] T018 [US2] A regra da consequência e o motivo:
  - `regra.consequencia` lê o efeito em `processo_seletivo/resultados/domain/regra.py`;
  - a consolidação completa o motivo com a reserva da inscrição em
    `processo_seletivo/resultados/application/consolidacao.py`.
- [x] T019 [US2] A progressão e a faixa em `processo_seletivo/resultados/application/prontidao.py`:
  - a Regra 2 com `consequencia__in` nas três funções;
  - `_dentro_da_faixa` com a retirada anterior (research T-006, T-007).
- [x] T020 [P] [US2] Testes em `tests/integration/classificacao/test_ordem_com_retirada.py`:
  - Etapa anterior à última enumerada, fora do universo reservado;
  - Etapa na última enumerada, sem posição na reservada;
  - Etapa posterior, sem efeito;
  - ampla intacta;
  - `listas_sem_concorrente`;
  - a reprodução do ato (FR-7012);
  - a Etapa restrita a `PPI` e `PcD`, cada inscrição só na sua (FR-7010);
  - a parte pública da ordem reservada sem a inscrição e sem o motivo, e a individual com ele
    (FR-7017).
- [x] T021 [US2] A ordem:
  - o universo reservado sem a retirada anterior em `processo_seletivo/classificacao/application/calculo.py`
    (inclusive `listas_sem_concorrente`);
  - o sem posição por retirada em `processo_seletivo/classificacao/domain/universo_classificavel.py`;
  - a mesma regra em `processo_seletivo/classificacao/application/reproducao.py`.
- [x] T022 [P] [US2] Testes em `tests/integration/ocupacao/test_ocupacao_com_retirada.py`:
  - habilitada pela ampla e não contada na reserva (FR-7014);
  - a fila da reserva não a oferece;
  - a situação da vaga da `155`;
  - o horizonte, com a retirada posterior sem efeito (FR-7027);
  - a faixa não reabre (FR-7015).
- [x] T023 [US2] A subtração da reserva em `habilitadas_pelo_corte`, em
  `processo_seletivo/ocupacao/application/selectors.py` (research T-009).
- [x] T024 [P] [US2] Testes em `tests/integration/sorteios/test_relacao_com_retirada.py`: a relação da
  reserva sem a retirada, a da ampla com ela, e sem Etapa de habilitação nada muda (FR-7030).
- [x] T025 [US2] O sorteio: `lista_id` em `processo_seletivo/sorteios/application/habilitacao.py`,
  passada por `relacao.py` e `previa.py` (research T-010).

## Phase 5: User Story 3 — O candidato entende que perdeu a reserva (P1)

**Goal**: o acompanhamento sem "Eliminado" para a retirada. **Independent test**: abrir o
acompanhamento de Maria sob cada efeito.

- [x] T026 [P] [US3] Testes em `tests/unit/portal/test_situacao_com_retirada.py`:
  - a retirada não é eliminação;
  - a linha da reserva perdida;
  - o cartão da lista reservada;
  - a eliminação continua "Eliminado" (FR-7024, UX-742).
- [x] T027 [US3] O que o acompanhamento recebe e mostra:
  - `"retirada"` em `resultados_das_etapas`, em `processo_seletivo/resultados/application/selectors.py`;
  - a precedência e a linha em `processo_seletivo/portal/situacao.py`;
  - o cartão em `portal/templates/portal/acompanhamento.html` e na folha do portal.

## Phase 6: User Story 4 — O recurso devolve a reserva sem mecanismo novo (P2)

**Goal**: recurso contra retirada, e a gravidade na vedação de piora. **Independent test**: deferir
contra retirada; reavaliar contra ausência.

- [x] T028 [P] [US4] Testes em `tests/integration/recursos/test_recurso_da_retirada.py`:
  - deferido devolve à reserva (FR-7019);
  - a retirada não vira eliminação (FR-7028);
  - a ausência que elimina vira retirada pela reavaliação (FR-7029);
  - a retirada por ausência não vira eliminação;
  - a correção contra Ocorrência habilita;
  - o deferimento torna obsoleta a ordem emitida que leu a retirada (FR-7016).
- [x] T029 [US4] A gravidade em `piora` (`processo_seletivo/recursos/domain/pejus.py`), com o
  docstring revisto. Conferir que a consolidação em cumprimento de reavaliação herda a regra.

## Phase 7: User Story 5 — A Retificação do efeito não muda a regra no meio do caminho (P2)

**Goal**: o impedimento histórico. **Independent test**: retificar antes e depois do primeiro
desfavorável, e depois de todos superados.

- [x] T030 [P] [US5] Testes em `tests/integration/publicacoes/test_retificacao_do_efeito.py`:
  - passa sem desfavorável;
  - recusada com desfavorável vigente;
  - recusada com todos superados (FR-7020, SC-2334);
  - a volta a "todas" recusada;
  - a ampliação do alcance passa (FR-7021);
  - a consolidação depois da gravação da Retificação faz a publicação dela ser recusada, e o
    Resultado leva o efeito vigente no ato (FR-7022).
- [x] T031 [US5] `_recusar_efeito_mudado_apos_desfavoravel` em
  `processo_seletivo/publicacoes/application/retificacoes.py`, na gravação e na publicação (research
  T-012). Registrar a exceção nomeada de `objects` em `tests/test_vigencia_do_resultado.py`.
- [x] T032 [US5] Os dois campos em `CAMPOS_ETAPA` (`processo_seletivo/interface/retificacao.py`) e o
  teste de contrato que os guarda.

## Phase 8: User Story 6 — O ausente segue o efeito que o Edital declarou para a ausência (P2)

**Goal**: a Ocorrência aplica o efeito da ausência. **Independent test**: efeitos diferentes, uma
ausência e um desfavorável.

- [x] T033 [P] [US6] Testes no mesmo `tests/integration/resultados/test_retirada_da_reserva.py`:
  - a ausência com "o mesmo";
  - a ausência que elimina com o desfavorável que retira;
  - o desfavorável nunca aplica o efeito da ausência (FR-7009).
- [x] T034 [US6] O efeito da ausência e o motivo em `processo_seletivo/resultados/application/ocorrencia.py`.

## Phase 9: Polish & Cross-Cutting

- [x] T035 O guardião da FR-7018 em `tests/test_leitores_da_consequencia.py`, com o inventário
  classificado (research T-016, SC-2335).
- [x] T036 [P] A gestão (FR-7025, UX-743):
  - retiradas à parte no relatório do Edital (`processo_seletivo/interface/relatorio_do_edital.py`);
  - rótulo e filtro em `templates/interface/resultados.html`;
  - contagem na confirmação da consolidação (`templates/interface/consolidacao_confirmar.html`, a view em
    `processo_seletivo/interface/views.py`);
  - rótulo na conferência da ordem.
  
  Os testes vão em `tests/interface/test_telas_da_retirada.py`.
- [x] T037 [P] O vocabulário: os textos novos na varredura de vocabulário, se a tela entrar na lista
  literal.
- [x] T038 Escrever `specs/164-efeito-do-desfecho-por-lista/rastreabilidade.md`, ligando cada FR, SC,
  UX e caso-limite a teste.
- [x] T039 Atualizar o README (linha da `164`) e a contagem `N de M` no CLAUDE.md, se mudar (não
  deve mudar).
- [x] T040 Verificar: `make lint check test-pg` com `DB_NAME` próprio. A equivalência da prévia
  (FR-7026) é guardada pelos testes de equivalência que já existem, que precisam continuar verdes.
- [x] T041 Fazer a jornada do candidato no navegador (quickstart, *Pela interface*), pelo canal do
  candidato.

## Dependencies & Execution Order

- **Setup (T001)**, depois **Foundational (T002–T009)**: bloqueiam tudo.
- **US1 (T010–T016)**: depende só da fundação.
- **US2 (T017–T025)**: depende da fundação.
  - T018 vem antes de T019 a T025, porque eles precisam de Resultado de retirada.
- **US3 (T026–T027)**: depende de T018.
- **US4 (T028–T029)**: depende de T018.
- **US5 (T030–T032)**: depende de T007 e T018.
- **US6 (T033–T034)**: depende de T005.
- **Polish**: depois de todas. T035 depois de todo leitor mudado.

## Parallel Opportunities

- T005 e T006 em paralelo com T002 a T004.
- Os testes `[P]` de cada história se escrevem em paralelo com a implementação da história anterior.
- T020, T022 e T024 são arquivos distintos.

## Implementation Strategy

- **MVP**: Fundação, US1 e US2. Só com elas a Etapa publicada produz o efeito declarado.
- **Ordem dos commits**: a do plano, com os incrementos A a D:
  - A: Fundação, US1 e US5;
  - B: US2, US6 e T035;
  - C: US4;
  - D: US3 e T036.
- **Uma suíte inteira por vez.** Enquanto trabalha, rode o diretório que a mudança toca, e a suíte
  inteira só no fim (CLAUDE.md).

## Jornada de 14/11 (T041)

Banco próprio (`ps164dev`), cenário montado pelos helpers dos testes num shell:
- Edital com a Heteroidentificação restrita a `PPI` e o marco por pontuação enumerando a Prova;
- Maria (`PPI`) retirada, Ana (`PPI`) confirmada, Bia da ampla;
- as ordens da ampla e da `PPI` emitidas e publicadas.

O que se viu:
- **Ordem da ampla:** Maria em 1º, Ana em 2º, Bia em 3º.
- **Ordem da `PPI`:** só Ana; Maria saiu do universo dela.
- **Acompanhamento de Maria, no navegador:** *"Aguardando resultado definitivo"*, *"Ampla
  concorrência: 1º lugar"*, nenhum *"Eliminado"*.
- **Também nenhuma palavra sobre a reserva perdida.** A Etapa restrita nunca é enumerada por
  marco (o marco só enumera Etapa classificatória, e a `163` impede a restrita classificatória),
  então o Resultado dela não é visível ao titular. Registrado em *Achados* da spec, para decisão
  do usuário.

## Phase 10: A visibilidade da Etapa restrita (decisão do usuário de 14/11, depois da jornada)

- [x] T042 [US3] `etapas_lidas_pelo_marco` em `processo_seletivo/resultados/domain/efeito.py`. O
  marco lê as Etapas que enumera e a Etapa restrita anterior à última enumerada (FR-7031, D-012).
- [x] T043 [US3] Usar a função para ver e para recorrer:
  - a visibilidade em `resultados_visiveis` (`processo_seletivo/resultados/application/selectors.py`);
  - o prazo em `_janelas_pertinentes` (`processo_seletivo/recursos/application/interpor.py`)
    (FR-7032).
- [x] T044 [US3] O cartão do Resultado da Etapa no acompanhamento dizia "Eliminada" para a retirada;
  agora diz "Deixou de concorrer pela reserva" (`portal/templates/portal/acompanhamento.html`). Foi
  achado na jornada refeita.
- [x] T045 [P] [US3] Testes em `tests/integration/portal/test_retirada_visivel_ao_titular.py`: antes
  da publicação, depois dela, o recurso e o acompanhamento pelo canal do candidato.
- [x] T046 Refazer a jornada no navegador: a linha da reserva perdida no topo, e o cartão da
  Heteroidentificação com "Deixou de concorrer pela reserva" e o motivo.

## Phase 11: O caso de integração da FR-7013

- [x] T047 [US2] O teste em `tests/integration/resultados/test_faixa_com_retirada.py`:
  - **Cenário.** Um marco que enumera a Análise documental, com corte de alvo 1 por lista que governa
    a Prova; a Heteroidentificação fica no meio. Maria (`PPI`) está só na faixa da `PPI`.
  - **Retirada:** ela não participa da Prova.
  - **Confirmada:** participa.
- [x] T048 [US2] `fora_do_corte` passa as Etapas que retiram a `_dentro_da_faixa`, como a participação
  (`processo_seletivo/resultados/application/prontidao.py`). Sem isso, a recusa e as telas diriam
  que a retirada não está fora do corte enquanto a participação a excluía. Foi o teste da T047 que
  achou a divergência.
