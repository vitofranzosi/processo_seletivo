# Rastreabilidade: Prévia interativa da classificação — fatia 1

Cada requisito → a tarefa que o implementa → o teste que o verifica. Escrita com a spec, antes da
implementação: as tarefas estão em [tasks.md](tasks.md), e os arquivos de teste ainda não existem. A
T036 a confere contra o que for implementado.

| Requisitos | Tarefas | Testes |
|---|---|---|
| FR-2200 a FR-2203 (acesso, painel fora do cartão, desktop e estreito, um por vez e foco) | T019, T020, T021, T032 | `tests/interface/test_previa_da_classificacao.py` (T014, T033) |
| FR-2204 a FR-2206 (candidatos fictícios, determinismo, reposicionamento) | T011, T029 | `tests/unit/classificacao/test_cenarios_da_previa.py` (T010); interface (T014, T027) |
| FR-2207 a FR-2211 (o que cada linha diz, a explicação da partição) | T008, T016 | `tests/unit/classificacao/test_ordenar_com_trajetoria.py` (T005); interface (T015) |
| FR-2212 a FR-2219 (corte, progressão, recusa, desfecho não declarado, outro desfecho, alvo do quadro, marco sem corte) | T013, T025, T026 | `tests/unit/classificacao/test_previa.py` (T012); interface (T023) |
| FR-2220 a FR-2222 (fronteira das vagas, suposição, nada de "tudo certo") | T013, T025 | `test_previa.py` (T012); interface (T023) |
| FR-2223 a FR-2228 (recálculo sobre o digitado, cálculo no servidor, cenários, incompleto, agrupamento) | T011, T016, T017, T029, T031 | interface (T015, T027, T030); `test_previa.py` (T012) |
| FR-2229 (comportamento pendente de decisão) | T025 | interface (T024) |
| FR-2230 a FR-2233 (o motor, a extração, resultado oficial igual, equivalência com sentinela) | T006, T007, T008, T013 | `tests/integration/classificacao/test_previa_equivale_ao_oficial.py` (T003, T034, T035); `tests/unit/classificacao/test_universo_classificavel.py` (T004); suítes existentes (T009) |
| FR-2234 e FR-2235 (sem efeito oficial, autorização) | T017, T018 | `tests/integration/classificacao/test_previa_sem_efeito.py` (T028); `tests/authorization/test_classificacao.py` e `tests/test_gramatica_das_portas.py` (T018) |
| FR-2236 e FR-2237 (acessibilidade, CSP) | T020, T021, T032 | interface (T033) |
| SC-840 (teste de uso) | T039 | validação humana, `validacao-de-uso.md` |
| SC-841 (até 1 s, faixa de 500) | T013, T017 | `test_previa.py` (T012, tempo); interface (T027, consultas) |
| SC-842 (equivalência em 100% da matriz) | T034 | T034, T035 |
| SC-843 (zero escritas) | — | T028 |
| SC-844 (suítes existentes e consultas iguais) | T007 | T009 |
| SC-845 (recusa e aviso sempre visíveis) | T025 | T023 |
| SC-846 (375 px) | T021 | T033 |
| SC-847 (CSP) | T021, T032 | T033 |
