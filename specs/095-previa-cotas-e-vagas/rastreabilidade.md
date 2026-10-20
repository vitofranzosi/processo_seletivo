# Rastreabilidade: Prévia interativa da classificação — fatia 2

Cada requisito → a tarefa que o implementa → o teste que o verifica. Escrita com a spec, antes da
implementação: as tarefas estão em [tasks.md](tasks.md), e os arquivos de teste ainda não existem. A
T032 a confere contra o que for implementado.

| Requisitos | Tarefas | Testes |
|---|---|---|
| FR-2300 (extensão do painel da `094`) | T001, T013, T015 | `tests/interface/test_previa_por_recorte.py` (T012) |
| FR-2301 a FR-2306 (os recortes, a ampla como universo, ordem por reservada, Perfil sem reservada, ordem vazia, nada por nome) | T010, T013, T014, T015, T025 | `tests/unit/classificacao/test_previa_por_recorte.py` (T009); interface (T012, T024) |
| FR-2307 a FR-2309 (corte por recorte: alvo e suplentes, sem linha, recusa por recorte) | T010, T014 | `test_previa_por_recorte.py` (T009); interface (T012) |
| FR-2310 a FR-2312 (jornada: resumo por recorte, união na Etapa, ocupação fora da sequência) | T010, T015, T023 | `test_previa_por_recorte.py` (T009); interface (T012, T022) |
| FR-2313 a FR-2315 (detalhe: seletor, posição na ampla e marca, empates por recorte) | T013, T015, T018 | interface (T012, T016) |
| FR-2316 a FR-2319 (concomitância: sempre, quem ocuparia pela ampla, suplente da ampla, faixa tomada) | T004, T010, T017, T018 | `tests/unit/ocupacao/test_ocupantes_pela_ampla.py` (T004); `tests/unit/ocupacao/test_rodada_da_previa.py` e `test_previa_por_recorte.py` (T009); interface (T016) |
| FR-2320 a FR-2325 (ocupação: quatro quantidades, uma rodada, sem linha, fronteiras e dependência, corte não emitido, invariantes) | T010, T017, T018 | `tests/unit/ocupacao/test_rodada_da_previa.py` e `test_previa_por_recorte.py` (T009); interface (T016) |
| FR-2326 a FR-2330 (reversão: lida do gravado, cedido, esgotamento como hoje, só o mesmo Perfil, nada a reverter) | T005, T010, T020, T021 | `tests/unit/ocupacao/test_ha_quem_ocupar.py` (T005); `test_previa_por_recorte.py` (T009); interface (T019) |
| FR-2331 a FR-2333 (população com Modalidades, casos-limite, uma Modalidade por candidato) | T008, T025 | `tests/unit/classificacao/test_cenarios_com_modalidade.py` (T007, T024); interface (T024) |
| FR-2334 (o que mudou por recorte) | T023 | interface (T022) |
| FR-2335 a FR-2337 (vocabulário, o que não se simula, comportamento atual) | T014, T017, T020, T029 | interface (T016, T019); guardiões (T029) |
| FR-2338 a FR-2340 (o motor, as extrações, a equivalência com sentinela) | T004, T005, T010 | `tests/integration/ocupacao/test_extracao_da_ocupacao_equivale.py` (T003, T006); `tests/integration/classificacao/test_previa_por_recorte_equivale_ao_oficial.py` (T011) |
| FR-2341 e FR-2342 (sem efeito, nenhum dado real) | T010 | `tests/interface/test_previa_por_recorte.py` (T028); `test_cenarios_com_modalidade.py` (T007) |
| FR-2343 (limite de recortes) | T010 | `test_previa_por_recorte.py` (T009) |
| FR-2344 e FR-2345 (acessibilidade, CSP) | T015, T027 | interface (T026) |
| SC-870 (compreensão) | T031 | roteiro de compreensão, com elaboradores |
| SC-871 e SC-872 (equivalência por recorte; Perfil sem reserva igual à fatia 1) | T010, T011 | T011; equivalência da `094` |
| SC-873 (população estável com as mesmas Modalidades) | T008 | T007 |
| SC-874 e SC-875 (nenhum número onde não se avalia; "não reverte" sem declaração) | T017, T020 | T009, T016, T019 |
| SC-876 (1 segundo) | T010 | `test_previa_por_recorte.py` (T009), com 500 candidatos e 7 recortes |
| SC-877 (zero escritas) | T010 | T028 |
| SC-878 (375 px, CSP) | T027 | T026 |
