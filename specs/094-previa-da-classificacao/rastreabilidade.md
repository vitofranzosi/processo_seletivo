# Rastreabilidade: Prévia interativa da classificação — fatia 1

Cada requisito → a tarefa que o implementa → o teste que o verifica. Escrita com a spec, antes da
implementação: as tarefas estão em [tasks.md](tasks.md), e os arquivos de teste ainda não existem. A
T036 a confere contra o que for implementado. A segunda rodada de UX (19/10) acrescentou as linhas
marcadas com *(2ª)* e revisou as tarefas de FR-2205 a FR-2214.

| Requisitos | Tarefas | Testes |
|---|---|---|
| FR-2200 a FR-2203 (acesso, painel fora do cartão, desktop e estreito, um por vez e foco) | T019, T020, T021, T032 | `tests/interface/test_previa_da_classificacao.py` (T014, T033) |
| FR-2204 a FR-2206 (candidatos fictícios; população estável e caso-limite) | T011, T046, T029 | `tests/unit/classificacao/test_cenarios_da_previa.py` (T010, T045); interface (T014, T027, T049) |
| FR-2207 a FR-2211 (quatro colunas, etiqueta curta, a explicação da partição) | T008, T016 | `tests/unit/classificacao/test_ordenar_com_trajetoria.py` (T005); interface (T015) |
| FR-2212 a FR-2219 (consequência, fluxo, recusa, desfecho não declarado, outro desfecho, alvo do quadro, marco sem corte) | T013, T025, T026 | `tests/unit/classificacao/test_previa.py` (T012); interface (T023, T040) |
| FR-2220 a FR-2222 (fronteira das vagas, suposição, nada de "tudo certo") | T013, T025 | `test_previa.py` (T012); interface (T023) |
| FR-2223 a FR-2228 (recálculo sobre o digitado, cálculo no servidor, cenários, incompleto, agrupamento) | T011, T016, T017, T029, T031 | interface (T015, T027, T030); `test_previa.py` (T012) |
| FR-2229 (comportamento pendente de decisão) | T025 | interface (T024) |
| FR-2230 a FR-2233 (o motor, a extração, resultado oficial igual, equivalência com sentinela) | T006, T007, T008, T013 | `tests/integration/classificacao/test_previa_equivale_ao_oficial.py` (T003, T034, T035); `tests/unit/classificacao/test_universo_classificavel.py` (T004); suítes existentes (T009) |
| FR-2234 e FR-2235 (sem efeito oficial, autorização) | T017, T018 | `tests/integration/classificacao/test_previa_sem_efeito.py` (T028); `tests/authorization/test_classificacao.py` e `tests/test_gramatica_das_portas.py` (T018) |
| FR-2236 e FR-2237 (acessibilidade, CSP) | T020, T021, T032 | interface (T033) |
| FR-2238 e FR-2239 *(2ª)* (manchete, fluxo de três passos com ramos) | T016, T019, T025 | interface (T040) |
| FR-2240 *(2ª)* (ocupação separada, como hipótese) | T044 | interface (T044) |
| FR-2241 e FR-2242 *(2ª)* (tabela inicial e completa a um clique; comparação dos empates) | T016, T019 | interface (T015) |
| FR-2243 e FR-2244 *(2ª)* (população estável por padrão; o que mudou) | T046, T048, T029 | `test_cenarios_da_previa.py` (T045); `test_previa.py` (T047); interface (T049) |
| FR-2245 *(2ª)* (vocabulário de D-012, "suplente" só como campo) | T022 | `tests/test_vocabulario_da_composicao.py` (T022) |
| FR-2246 *(2ª)* (faixa maior que a população) | T025, T029 | interface (T040, T049) |
| SC-840 (teste de uso) | T039 | validação humana, `validacao-de-uso.md` |
| SC-841 (até 1 s, faixa de 500) | T013, T017 | `test_previa.py` (T012, tempo); interface (T027, consultas) |
| SC-842 (equivalência em 100% da matriz) | T034 | T034, T035 |
| SC-843 (zero escritas) | — | T028 |
| SC-844 (suítes existentes e consultas iguais) | T007 | T009 |
| SC-845 (recusa e aviso sempre visíveis) | T025 | T023 |
| SC-846 (375 px) | T021 | T033 |
| SC-847 (CSP) | T021, T032 | T033 |
| FR-2247, FR-2248 e FR-2251 *(3ª)* (a jornada derivada, os estados, os casos não lineares) | T050 | `tests/unit/classificacao/test_jornada.py` (T051); interface (T052) |
| FR-2249 e FR-2250 *(3ª)* (Etapa alimentada, marcos anterior e posterior) | T050, T053 | T051, T052 |
| FR-2252 *(3ª)* (detalhe a um clique, a vista preservada) | T053, T054 | interface (T052) |
| FR-2253 *(3ª)* (linguagem administrativa, D-016) | T055 | T022 |
| FR-2254 e FR-2255 *(3ª)* (o que a prévia simula; o Perfil nomeado) | T053 | T052 |
| SC-848 *(2ª)* (as cinco perguntas sem abrir detalhes) | T039 | validação humana, nos três cenários de `prototipo/comparacao-v1-v2.md` |
| SC-849 *(2ª)* (população estável não muda) | T046 | T045 |
| SC-850 *(2ª)* (o que mudou, sempre) | T048, T029 | T047, T049 |
| SC-851 *(3ª)* (compreensão da jornada) | T039 | validação humana, `roteiro-de-compreensao.md` |
| SC-852 *(3ª)* (jornada completa e na ordem) | T050 | T051 |
| SC-853 *(3ª)* (nenhum número no indeterminado) | T050, T053 | T052 |
