# Rastreabilidade: Destinação da vaga reservada sem ocupante

Cada requisito da [spec](spec.md) e onde ele é verificado. Caminhos relativos a `backend/`.

| Requisito | Onde é verificado | Observação |
|---|---|---|
| FR-6300 a FR-6303 | `tests/unit/ocupacao/test_destinacao_dominio.py`, `tests/interface/test_destinacao_na_ocupacao.py`, `tests/unit/interface/test_andamento_situacoes.py` | uma conta só para ocupação, Centro e convocação |
| FR-6304 | `tests/unit/ocupacao/test_destinacao_dominio.py`, `tests/integration/ocupacao/test_condicao_do_esgotamento.py` | V-1, V-2, V-4 e V-5 da verificação |
| FR-6305 | — | **incremento F, bloqueado pela D-015**: nenhuma regra do saldo foi escrita |
| FR-6306 e FR-6307 | `tests/unit/ocupacao/test_destinacao_dominio.py`, `tests/integration/ocupacao/test_condicao_do_esgotamento.py` | resultado provisório, recurso, chamada em curso, ampla sem aceite, apuração obsoleta |
| FR-6308 a FR-6314 | `tests/integration/ocupacao/test_destinacao.py`, `tests/interface/test_destinacao_na_ocupacao.py` | ato, conferência, registro, soma, recusas, idempotência |
| FR-6315 e FR-6316 | `tests/integration/ocupacao/test_destinacao.py`, `tests/test_gravacao_da_destinacao.py` | por esgotamento a emissão não move; por saldo continua movendo até o incremento F |
| FR-6317 a FR-6319 | `tests/unit/editais/test_reversao_declarada.py`, `tests/unit/ocupacao/test_reversao.py`, `tests/unit/publicacoes/test_redacao_das_frases.py`, `tests/interface/test_retificar_reversao.py`, `tests/integration/ocupacao/test_destinacao.py` | a passagem entre cotas é declarada e não move |
| FR-6320 a FR-6327 | `tests/integration/ocupacao/test_nao_preenchida.py`, `tests/interface/test_destinacao_na_ocupacao.py` | Edital silente, linha geral, fundamento obrigatório |
| FR-6328 a FR-6331 | `tests/interface/test_lista_sem_concorrente.py`, `tests/integration/divulgacao/test_publicacao_conjunta.py` | o gesto e a publicação conjunta |
| FR-6332 e FR-6333 | `tests/integration/ocupacao/test_destinacao_no_sorteio.py` | ausência comprovada pela relação da ampla |
| FR-6334 a FR-6336 | `tests/integration/ocupacao/test_desfazimento_da_destinacao.py` | com e sem chamada dependente |
| FR-6337 a FR-6339 | `tests/portal/test_destinacao_na_selecao.py`, `tests/interface/test_relatorio_do_edital.py` | sem nome nem protocolo; o PDF do relatório não muda |
| FR-6340 | `tests/integration/convocacao/test_fundamento_da_vaga_destinada.py` | |
| FR-6341 e FR-6342 | `tests/integration/ocupacao/test_destinacao.py`, `tests/integration/ocupacao/test_nao_preenchida.py`, `tests/interface/test_destinacao_na_ocupacao.py` | permissão e reprodução |
| FR-6343 | `tests/integration/classificacao/test_previa_por_recorte_equivale_ao_oficial.py`, `tests/integration/sorteios/test_previa_do_sorteio_equivale_ao_oficial.py` | por esgotamento; o saldo fica com o incremento F |
| FR-6344 | `tests/test_vocabulario_da_ocupacao.py` | |
| UX-600 a UX-603 | `tests/interface/test_destinacao_na_ocupacao.py`, `tests/interface/test_previa_por_recorte.py` | |
| SC-2100 | `tests/interface/test_destinacao_na_ocupacao.py`; jornada do C09 no navegador (PR) | |
| SC-2101 | `tests/interface/test_destinacao_na_ocupacao.py` | |
| SC-2102 | `tests/integration/ocupacao/test_destinacao.py`, `tests/integration/ocupacao/test_nao_preenchida.py` | |
| SC-2103 | `tests/test_gravacao_da_destinacao.py` | |
| SC-2104 | `tests/integration/ocupacao/test_condicao_do_esgotamento.py` | V-1 a V-4; os S-1 a S-4 ficam com o incremento F |
| SC-2105 | `tests/interface/test_lista_sem_concorrente.py` | |
| SC-2106 | `tests/integration/ocupacao/test_destinacao.py`, `tests/integration/ocupacao/test_desfazimento_da_destinacao.py` | |
| SC-2107 | `tests/integration/ocupacao/test_destinacao.py` | |
| SC-2108 | — | roteiro com pessoas, pendente |
