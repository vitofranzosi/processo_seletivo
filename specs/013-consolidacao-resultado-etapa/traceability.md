# Rastreabilidade — 013, Consolidação do Resultado da Etapa

**Feature**: 013 | **Spec**: [spec.md](./spec.md) | **Tarefas**: [tasks.md](./tasks.md)

Cada requisito, onde ele vive e o que o prova. O que **não** aparece aqui é o que não foi
implementado — e a coluna "prova" distingue teste de estrutura, porque as duas garantem de formas
diferentes e confundi-las seria contar cobertura que não existe.

## Requisitos funcionais

| FR | Onde vive | Prova |
|---|---|---|
| FR-001 | `resultados/application/prontidao.py::participacao` | `acceptance/test_resultado_da_etapa.py::test_us1_*` |
| FR-002 | `resultados/domain/regra.py` consome `avaliacoes_previstas` | `unit/resultados/test_regra.py` |
| FR-003 | `resultados/domain/progressao.py::etapas_anteriores` | `acceptance::test_us3_a_eliminacao_vale_para_todas_as_etapas_seguintes` |
| FR-004 | `prontidao.py::participacao` (gate) | `acceptance::test_us3_a_exigencia_de_habilitacao_fica_dormente_ate_o_primeiro_resultado` |
| FR-005 | `avaliacoes/{domain/autorizacao,application/{distribuicao,mesa,selectors}}.py` — inclusive `_carentes`, do rodízio | `authorization/test_progressao.py`, `integration/resultados/test_progressao_no_rodizio.py`, `integration/resultados/test_carga_nas_etapas.py` |
| FR-006 | `prontidao.py::restringir_a_participantes` | `performance/test_progressao.py`, `performance/test_escala_da_mesa.py` |
| FR-007 | `distribuicao.py::_inscricoes_atribuiveis` | `contract/test_distribuicao_com_progressao.py` |
| FR-008 | `prontidao.py::panorama_da_etapa` consome `avaliacoes_elegiveis` | `integration/resultados/test_prontidao.py` |
| FR-009 | `avaliacoes/application/selectors.py::resumo_da_etapa` | `integration/resultados/test_prontidao.py::test_o_resumo_existente_recebe_as_contagens_sem_duplicar` |
| FR-010 | `prontidao.py::contagens` | `acceptance::test_us1_*` (a partição fecha) |
| FR-011 | `regra.py::impedimento_da_regra` | `unit/resultados/test_regra.py` |
| FR-012 | `prontidao.py::_estado_do_participante` | `integration/resultados/test_prontidao.py` |
| FR-013 | `resultados/domain/compatibilidade.py` | `unit/resultados/test_compatibilidade.py` |
| FR-014 | `compatibilidade.py::etapa_no_conteudo` | `unit/resultados/test_compatibilidade.py` |
| FR-015 | `regra.py` + `consolidacao.py` (erro do pedido) | `contract/test_consolidacao.py` |
| FR-016 | `consolidacao.py` + trigger `resultado_etapa_coerente` | `acceptance::test_us2_a_pontuacao_e_copia_exata_e_ninguem_a_digita` |
| FR-017 | `regra.py::consequencia` | `unit/resultados/test_regra.py`, `acceptance::test_us2_o_lote_produz_*` |
| FR-018 | `consolidacao.py::consolidar` | `acceptance::test_a_jornada_completa_pela_interface_administrativa` |
| FR-019 | `consolidacao.py` (recusa de item × erro do pedido) | `contract/test_consolidacao.py` |
| FR-020 | reúsa `resultado_declarado` da 012 | `integration/resultados/test_consolidacao_idempotente.py` |
| FR-021 | `consolidacao.py` → `auditar` por Resultado | `integration/resultados/test_consolidacao_idempotente.py` |
| FR-022 | invólucro `comando_de_comissao` | `integration/resultados/test_consolidacao_idempotente.py` |
| FR-023 | `select_for_update` do Processo + unicidade | `integration/resultados/test_consolidacao_idempotente.py::test_dois_lotes_concorrentes_*` |
| FR-024 | constraint `uq_resultado_inscricao_etapa` | `integration/resultados/test_imutabilidade_do_resultado.py` |
| FR-025 | `resultados/models.py::ResultadoEtapa` | **estrutura** (campos e checks) |
| FR-026 | `selectors.py::resultados_da_etapa` (`select_related`) | `acceptance::test_us4_a_proveniencia_sobrevive_*` |
| FR-027 | `resultados.html` (duas autorias) | `acceptance::test_us4_a_proveniencia_sobrevive_*` |
| FR-028 | ausência de coluna de estado | **estrutura** (o modelo não tem o campo) |
| FR-029 | `save`/`delete` + trigger + `TABELAS_APPEND_ONLY` | `integration/resultados/test_imutabilidade_do_resultado.py`, `integration/test_imutabilidade_do_historico.py` |
| FR-030 | `avaliacao.py::_recusar_se_fundamenta_resultado` | `integration/resultados/test_fechamento_das_entradas.py` |
| FR-031 | `impedimento.py` (aplica por inteiro) | `authorization/test_impedimento_superveniente.py` |
| FR-032 | `impedimento.py::_resultados_contestados` + `resultados.html` | `integration/resultados/test_fechamento_das_entradas.py`, `authorization/test_impedimento_superveniente.py` |
| FR-033 | frase da recusa em `avaliacao.py`, desfecho em `impedimento.py` | `integration/resultados/test_fechamento_das_entradas.py::test_a_recusa_nomeia_inscricao_etapa_e_resultado_sem_expor_a_nota` |
| FR-034 | nada recalcula Resultado | `acceptance::test_us4_a_proveniencia_sobrevive_*` |
| FR-035 | `consolidacao.py` sob `comando_de_comissao` | `authorization/test_consolidacao.py` |
| FR-036 | invólucro reavalia após o bloqueio | `authorization/test_consolidacao.py` |
| FR-037 | `views.py::resultados_da_etapa` via `_etapa_para_auditar` | `authorization/test_consulta_de_resultado.py` |
| FR-038 | 404 uniforme em todas as rotas | `authorization/test_progressao.py`, `test_consulta_de_resultado.py` |
| FR-039 | `marcar_como_privada` na consulta | `integration/resultados/test_armazenamento_da_consulta.py` |
| FR-040 | `auditar` sem parâmetro de pontuação | `integration/resultados/test_consolidacao_idempotente.py::test_cada_resultado_criado_gera_exatamente_um_evento` |
| FR-041 | uma migration, em `resultados` | **estrutura** (`makemigrations --check` limpo; nenhuma migration em `editais`/`publicacoes`) |
| FR-042 | nada altera a primeira Etapa | `integration/resultados/test_nao_regressao_012.py` |
| FR-043 | nenhuma coluna acrescentada a modelo da 012 | **estrutura** + triggers append-only de `publicacoes` |
| FR-044 | `regra.py` ignora peso e caráter classificatório | `unit/resultados/test_regra.py::test_peso_e_carater_classificatorio_nao_alteram_a_consequencia` |
| FR-045 | `resultados.html`, `distribuicao.html` | `tests/test_vocabulario_do_resultado.py` |

## Critérios de sucesso

| SC | Prova |
|---|---|
| SC-001 | `performance/test_resumo_da_etapa.py`, `acceptance::test_us1_*` |
| SC-002 | `performance/test_consolidacao_em_lote.py` — o teto de mil exercido, e a derivada em teste próprio |
| SC-003 | `acceptance::test_us2_a_pontuacao_e_copia_exata_e_ninguem_a_digita` |
| SC-004 | `unit/resultados/test_regra.py`, `acceptance::test_us2_o_lote_produz_*` |
| SC-005 | `authorization/test_progressao.py`, `acceptance::test_us3_a_eliminacao_*` |
| SC-006 | `integration/resultados/test_consolidacao_idempotente.py` |
| SC-007 | `acceptance::test_us4_a_proveniencia_sobrevive_*` |
| SC-008 | `integration/resultados/test_fechamento_das_entradas.py` |
| SC-009 | `authorization/test_impedimento_superveniente.py` |
| SC-010 | `contract/test_consolidacao.py`, `integration/resultados/test_prontidao.py` |
| SC-011 | `acceptance::test_a_jornada_completa_pela_interface_administrativa` |

## O que é garantido por estrutura, e não por asserção

Quatro requisitos — FR-025, FR-028, FR-041 e FR-043 — são propriedades da forma do código, e não
comportamentos observáveis. FR-028 é a **ausência** de uma coluna; FR-041 e FR-043 são a ausência de
migrations fora de `resultados`, checada por `makemigrations --check`; FR-025 é a lista de campos do
modelo. Registrá-los como "testados" contaria cobertura que não existe — e foi por essa distinção
que a Fase 1 do plano se recusou a afirmar que cada requisito tem cenário no quickstart.

## Arquivos da feature

| Produção | Testes |
|---|---|
| `resultados/models.py`, `migrations/0001_initial.py` | `unit/resultados/` (3 arquivos) |
| `resultados/domain/{regra,compatibilidade,progressao}.py` | `integration/resultados/` (6 arquivos) |
| `resultados/application/{prontidao,consolidacao,selectors}.py` | `acceptance/test_resultado_da_etapa.py` |
| `avaliacoes/{domain/autorizacao,application/{avaliacao,distribuicao,impedimento,mesa,selectors}}.py` | `authorization/` (4 arquivos) |
| `interface/{urls,views}.py`, `templates/interface/{distribuicao,resultados}.html` | `contract/` (2), `performance/` (3) |
| `seguranca/papeis.py`, `config/settings/base.py` | `tests/test_vocabulario_do_resultado.py` |
