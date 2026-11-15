# Tasks: A orientação da verificação da autodeclaração

**Input**: [plan.md](plan.md), [research.md](research.md) (`T-001` a `T-010`),
[data-model.md](data-model.md), [contracts/frases.md](contracts/frases.md), [spec.md](spec.md)

**Tests**: pedidos pelo plano. Cada peça vem com o seu teste, no mesmo commit. A suíte roda contra
PostgreSQL, com `DB_NAME` próprio, e por diretório enquanto se trabalha.

Os caminhos são relativos a `backend/`.

## Phase 1: Setup

- [x] T001 Preparar o banco de teste da worktree (`DB_NAME=gps_168`) e conferir `manage.py migrate --check` na `main` de partida

## Phase 2: Foundational

- [x] T002 Mover a função pura `periodo` de `processo_seletivo/verificacao/application/disponibilidade.py` para `processo_seletivo/editais/domain/cronograma.py` como `periodo_da_etapa(conteudo, etapa)`, com a `166` importando-a (T-002); teste de unidade em `tests/unit/editais/test_periodo_da_etapa.py`
- [x] T003 Fazer `participa_da_etapa` aceitar `conteudo=` e `modalidade=` em `processo_seletivo/resultados/application/prontidao.py`, sem reler a versão nem a Modalidade quando dados (T-001); teste de equivalência e de contagem de consultas em `tests/integration/resultados/test_participa_com_conteudo.py`

## Phase 3: User Story 1 — o degrau (P1) 🎯 MVP

**Goal**: o acompanhamento diz ao alcançado o que falta, quando, e o que acontece se faltar.

**Independent Test**: renderizar o acompanhamento de alcançado, não alcançado e convocado, antes,
durante e depois do período.

- [x] T004 [US1] Criar `processo_seletivo/portal/passo_da_etapa.py` com `Passo` e `passos_da_inscricao(inscricao, conteudo, resultados_visiveis, agora)`, pela ordem de estados da data-model (FR-7300 a FR-7309, FR-7311)
- [x] T005 [P] [US1] Testes de unidade dos estados, da ordem entre Etapas e da ausência de consulta sem Etapa restrita em `tests/unit/portal/test_passo_da_etapa.py`
- [x] T006 [US1] Em `processo_seletivo/portal/situacao.py`, o código `PASSO`, os três rótulos, o degrau entre a eliminação e as classificadas e a linha do passo na convocação, com as frases de `contracts/frases.md` (FR-7303, FR-7304, FR-7306)
- [x] T007 [P] [US1] Testes puros do degrau, da precedência e das frases em `tests/unit/portal/test_situacao_do_passo.py`
- [x] T008 [US1] Na view do acompanhamento (`processo_seletivo/portal/views.py`), calcular os passos e passá-los a `situacao_da_inscricao`
- [x] T009 [US1] Teste de interface do acompanhamento renderizado e do custo igual sem Etapa restrita (SC-2414) em `tests/portal/test_degrau_do_passo.py`

## Phase 4: User Story 2 — o aviso do passo (P1)

**Goal**: quem conduz avisa os alcançados por e-mail, com prévia, sem a Modalidade no texto.

**Independent Test**: confirmar, despachar e ler a mensagem; conferir universo, já avisado e CHECK.

- [x] T010 [US2] Origem `PASSO` em `processo_seletivo/avisos/domain/nomes.py`; `etapa_id`, `marco_id` nulo, `chave_inicial` e os CHECKs em `processo_seletivo/avisos/models.py`; migration `processo_seletivo/avisos/migrations/0004_origem_passo.py` (T-004, T-005)
- [x] T011 [US2] `universo_do_passo` e o já avisado em `processo_seletivo/avisos/application/destinatarios.py`; `confirmar_aviso_do_passo` em `processo_seletivo/avisos/application/confirmar.py` (um Aviso por Perfil); a porta explícita em `comando.py`; os valores em `previa.py`; a variável `periodo_da_etapa` e a origem em `processo_seletivo/avisos/domain/variaveis.py` (FR-7315 a FR-7318)
- [x] T012 [US2] Quarto modelo inicial com `chave_inicial="PASSO"` em `processo_seletivo/avisos/domain/modelos_iniciais.py` e a guarda em `processo_seletivo/avisos/application/modelos.py` (FR-7319, FR-7320)
- [x] T013 [US2] Rota, view e ramos de template da confirmação: `processo_seletivo/interface/urls.py`, `processo_seletivo/interface/avisos.py`, `aviso_previa.html`, `aviso.html`, `avisos_do_edital.html`
- [x] T014 [P] [US2] Testes de integração em `tests/integration/avisos/test_aviso_do_passo.py`: universo, um Aviso por Perfil, já avisado, reenvio, CHECK no banco, chave dos avisos, e-mail sem Modalidade (SC-2412)
- [x] T015 [US2] Atualizar os testes que contam três modelos iniciais e as listas literais (`tests/test_vocabulario_do_aviso.py`, `tests/unit/avisos/test_modelos_iniciais.py`, `tests/unit/avisos/test_variaveis.py`, `tests/unidades/`, `tests/integration/avisos/test_modelos.py`), e a contagem de migrations por app

## Phase 5: User Story 3 — o Centro e Minhas atividades (P1)

**Goal**: a presidência vê o que falta e de quem; o avaliador vê o prazo.

**Independent Test**: Centro e Minhas atividades com Atribuições em estados variados; números iguais
aos da Mesa.

- [x] T016 [US3] Fatos da Etapa restrita em `_Leitor._etapas_no_edital` e células em `situacoes_da_etapa`, em `processo_seletivo/interface/andamento.py`: faltam por membro, `AVISAR`, período vencido, `ate`, e a frase do alcance da distribuição na nota da Etapa (T-006; FR-7321 a FR-7324, FR-7328)
- [x] T017 [US3] A natureza `AVISAR` em `processo_seletivo/interface/centro.py` e `processo_seletivo/interface/conceitos.py`, e nos testes que prendem as naturezas (`tests/unit/interface/test_centro_composicao.py`, `tests/interface/test_andamento_coerencia.py`)
- [x] T018 [US3] O fim do período no item da Atribuição (`processo_seletivo/comissoes/application/selectors.py`), `ate` em `processo_seletivo/interface/atividades.py` e no `_atividade.html` (T-008; FR-7326, FR-7327)
- [x] T019 [P] [US3] Testes em `tests/interface/test_pendencias_da_etapa_restrita.py`: faltam por membro igual à Mesa (SC-2413), sem sentido, AVISAR até o fim, período vencido, nenhuma pendência sem alcançado, linha de avaliar com "até"
- [x] T020 [US3] Rodar os testes de performance do Centro, do andamento e de Minhas atividades (`tests/performance/`), e ajustar só se a Etapa restrita os fizer passar do teto

## Phase 6: User Story 4 — o vídeo no degrau (P2)

**Goal**: com a chave ligada, o degrau absorve o cartão da `166`; o Centro conta quem encaminhar.

**Independent Test**: acompanhamento nos estados do vídeo, com e sem a chave; Centro com inscrição a
encaminhar.

- [x] T021 [US4] Estados do vídeo em `passo_da_etapa.py` e frases em `situacao.py` (FR-7312, FR-7313); com a chave desligada, ler o vídeo vigente sem exigir a chave, só para dar "Aguardando o resultado" a quem enviou (achado U1 do analyze); tirar o include, o contexto `verificacoes` e o template `_verificacao_por_video.html` (FR-7314)
- [x] T022 [US4] Célula "Encaminhar N inscrições à entrevista ao vivo" pelo plano da consolidação em `andamento.py` (T-007; FR-7325)
- [x] T023 [P] [US4] Ajustar `tests/portal/test_verificacao_por_video.py` e `tests/integration/verificacao/test_mesa_e_r11.py` ao degrau, e acrescentar os casos da chave desligada (SC-2415) e da célula de encaminhar

## Phase 7: User Story 5 — o cenário C18 (P3)

**Goal**: a equipe percorre a orientação num cenário.

**Independent Test**: o teste do cenário confere os quatro estados.

- [x] T024 [US5] `distribuir(avaliadores=2)` em `processo_seletivo/treinamento/construcao.py`, e `montar_c18` e o `Cenario` C18 em `processo_seletivo/treinamento/catalogo.py` (T-010; FR-7333, FR-7335)
- [x] T025 [US5] Teste do cenário em `tests/integration/treinamento/test_cenario_c18.py`, e as contagens de 17 para 18 cenários (FR-7334)

## Phase 8: Vocabulário e advertência (transversal)

- [x] T026 [P] Varredura do candidato em `tests/portal/test_vocabulario_do_passo.py`: todos os estados do degrau, com e sem a chave, e as páginas da gravação e do comprovante da `166`, com uma Etapa de nome neutro (FR-7330 a FR-7332, SC-2411)
- [x] T027 [P] A advertência `nome_da_etapa_restrita_com_termo_tecnico` em `processo_seletivo/editais/domain/validation.py`, e o teste em `tests/unit/editais/test_advertencia_do_nome.py` (T-009; FR-7336)

## Phase 9: Polish

- [x] T028 `CLAUDE.md` (a quarta linha dos modelos de aviso), `README.md`, se ele conta modelos ou cenários, e o roteiro dos cenários em `doc/cenarios-de-treinamento/`
- [ ] T029 `make lint check` e os diretórios tocados contra PostgreSQL; depois a suíte inteira, sozinha no cluster
- [x] T030 Percurso do `quickstart.md` §3 no navegador do painel, com capturas a 1280 px e a 375 px e o console sem violação de CSP (SC-2416 fica com o usuário)
- [x] T031 `rastreabilidade.md` com cada FR-, SC- e UX- apontando o teste que o prova

## Dependencies

- T002 e T003 antes de US1 e US3.
- US1 antes de US4: o degrau é o que absorve o vídeo.
- US2 antes de US3, porque a célula `AVISAR` leva à rota da confirmação e conta os avisados, e antes de
  US5.
- US5 depende de US1 a US3.
- O vocabulário (T026) depende de US1 e US4; a advertência (T027) é independente.

## Parallel Example

Dentro de cada história, os testes `[P]` se escrevem ao lado da implementação. T026 e T027 correm em
paralelo entre si.

## Implementation Strategy

O MVP é a US1: o degrau sozinho já resolve a lacuna principal. Depois vêm US2, US3, US4 e US5, cada uma
com os testes do seu diretório verdes antes da seguinte. A suíte inteira roda uma vez, no fim.

## Phase 10: Convergence

- [x] T032 Traduzir o nome do membro sem rótulo pelo nome legível da pessoa institucional em `processo_seletivo/avaliacoes/application/selectors.py` (`pendentes_por_membro`), sem consulta a mais para a demonstração, per FR-7321 (partial)
- [x] T033 Registrar em `research.md` (T-003) que o degrau com vídeo diz as duas formas no texto e leva à página da `166`, que tem os dois botões, per FR-7312 (partial)
- [ ] T034 Rodar a suíte inteira pelo CI das três fatias, já que o cluster local estava ocupado por outras duas suítes, per T029 (partial)
- [x] T035 Cenário C19, a Etapa restrita admitindo o vídeo, em `processo_seletivo/treinamento/catalogo.py` (`montar_c19`) e `processo_seletivo/treinamento/servico.py` (`exige_verificacao_por_video`), com o vídeo de treinamento em `processo_seletivo/treinamento/amostras/`, o teste em `tests/integration/treinamento/test_cenario_c19.py` e o roteiro no guia da equipe, per FR-7337
