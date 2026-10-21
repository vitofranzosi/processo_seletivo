# Rastreabilidade: Prévia do sorteio

Cada requisito → a tarefa que o implementa → o teste que o verifica. Conferida contra o implementado
em 21/10/2026 (T034). As tarefas estão em [tasks.md](tasks.md).

| Requisitos | Tarefas | Testes |
|---|---|---|
| FR-2477 e FR-2478 (o botão no cartão do marco por sorteio; o painel da `094`, sem ajuda no cartão) | T015, T017, T018 | `tests/interface/test_previa_do_sorteio.py::test_o_cartao_do_marco_por_sorteio_oferece_simular_sorteio`, `::test_o_marco_pela_pontuacao_continua_na_previa_da_classificacao`; `tests/interface/test_previa_da_classificacao.py::test_o_botao_nao_aparece_no_marco_por_sorteio` (emendado) |
| FR-2479 (só na composição) | T018 | por construção: o botão mora só no `_marco.html` da composição, e o fragmento responde pela etapa Classificação; a Retificação não o inclui |
| FR-2480 (a jornada da `094` diz que o sorteio tem prévia própria) | T019, T031 | `tests/interface/test_previa_da_classificacao.py::test_marco_por_sorteio_pedido_a_mao_responde_a_previa_do_sorteio`; a frase da jornada, na demonstração do `quickstart.md` |
| FR-2481 a FR-2486 (a semente fictícia: gerada, com selo, sem campo, recusada quando forjada, sortear de novo, mantida no recálculo, nunca gravada) | T005, T013, T014, T016, T017 | `tests/unit/sorteios/test_simulacao_ordem.py` (T003); `test_previa_do_sorteio.py::test_a_semente_e_ficticia_*`, `::test_sortear_de_novo_troca_a_semente`, `::test_mudar_a_quantidade_mantem_a_semente_e_diz`, `::test_token_forjado_*`, `::test_token_de_outro_marco_*`, `::test_material_e_seed_na_query_sao_ignorados`, `::test_nada_e_gravado_e_ninguem_e_lido` |
| FR-2487 a FR-2491 (a população: sugestão, soma na ampla, zero aceito, nomes estáveis, limite) | T005, T026, T027 | `tests/unit/sorteios/test_simulacao_populacao.py` (T004); `test_previa_do_sorteio.py::test_a_populacao_sugerida_*`, `::test_valor_invalido_*`, `::test_acima_do_limite_*`, `::test_reservada_sem_inscritos_*` |
| FR-2492 a FR-2496 (a ordem: recortes da ocupação, algoritmo oficial, posição na ampla, corte sem empate, sorteio com sobra de vaga) | T005, T008, T016, T017 | `test_simulacao_ordem.py` (vetores normativos, recortes à parte); `tests/integration/sorteios/test_previa_do_sorteio_equivale_ao_oficial.py` (T009); `test_previa_do_sorteio.py::test_o_painel_diz_cada_lista_*`, `::test_o_detalhe_da_reservada_*`, `::test_menos_inscritos_que_vagas_*`, `::test_perfil_sem_reserva_*` |
| FR-2497 a FR-2500 (a ocupação da rodada: quatro quantidades, faixa tomada, reversão, sem corte) | T008, T021, T022 | `tests/unit/sorteios/test_simulacao_resumo.py` (T007); equivalência (T009); `test_previa_do_sorteio.py::test_o_bloco_da_ocupacao_*`, `::test_sem_regra_de_corte_*` |
| FR-2501 a FR-2505 (o resumo: quantas rodadas, sementes derivadas, frequências, soma das rodadas, não é previsão) | T008, T024, T025 | `test_simulacao_resumo.py` (T007); `test_previa_do_sorteio.py::test_o_resumo_diz_*`, `::test_por_saldo_*`, `::test_por_esgotamento_*`, `::test_resultado_igual_*` |
| FR-2506 a FR-2508 (o que não se simula, comportamento atual, vocabulário) | T016, T021, T024, T032 | `test_previa_do_sorteio.py::test_o_resumo_diz_*` (DP-1), `::test_por_esgotamento_*` (DP-2), `::test_reservada_sem_inscritos_*` (achado), `::test_o_vocabulario_*`; `tests/test_vocabulario_da_composicao.py` |
| FR-2509 (sem efeito) | T030 | `test_previa_do_sorteio.py::test_nada_e_gravado_e_ninguem_e_lido` |
| FR-2510 a FR-2512 (375 px, anúncio, CSP) | T028, T029 | `test_previa_do_sorteio.py::test_a_semente_quebra_entre_grupos_*`, `::test_o_anuncio_*`, `::test_sem_estilo_nem_script_embutido`; `tests/interface/test_estaticos.py`, `tests/interface/test_acessibilidade.py`; a medida a 375 px na demonstração |
| SC-925 e SC-926 (compreensão) | T033 | [roteiro de compreensão](roteiro-de-compreensao.md), com elaboradores |
| SC-927 (equivalência) | T009 | `test_previa_do_sorteio_equivale_ao_oficial.py` |
| SC-928 (1 s e 5 s) | T007 | `test_simulacao_resumo.py::test_o_pior_caso_cabe_no_orcamento` |
| SC-929 (variação de amostragem) | T007 | `test_simulacao_resumo.py::test_duas_sementes_diferem_pouco_*` |
| SC-930 (zero escritas) | T030 | `test_previa_do_sorteio.py::test_nada_e_gravado_e_ninguem_e_lido` |
| SC-931 (semente forjada recusada) | T013 | `test_previa_do_sorteio.py::test_token_forjado_*`, `::test_token_de_outro_marco_*` |
