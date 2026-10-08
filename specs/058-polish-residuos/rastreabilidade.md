# Rastreabilidade — 058 · Polish: os resíduos dos três lotes

**Frase que governa**: *o que já foi decidido para uma tela vale para a tela vizinha que ficou de
fora, e nenhuma ação fica fora de alcance em tela estreita.*

Cada linha aponta o lugar do código e o que o prende. **TP** = `tests/interface/test_polish_da_058.py`;
**TA** = `tests/interface/test_acessibilidade.py`; **TE** = `tests/performance/test_escala_da_mesa.py`;
**V** = a linha da [verificação](verificacao.md), medida na página renderizada; **AÇ** = o diff das
listas de destinos ([acoes-antes.json](acoes-antes.json) × [acoes-depois.json](acoes-depois.json)).

F = `interface/templates/interface/`.

---

## 1. Requisitos funcionais

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **FR-1069** | F`processo_detalhe.html`: os atos por `regroup` sobre `irreversivel`, os irreversíveis em `ul.lista-acoes.em-linha.terminais`; F`_estilo_das_terminais.html`, incluído por F`detalhe.html` e F`processo_detalhe.html` (D-001, D-002) | TP `test_as_terminais_moram_num_parcial_das_duas_telas`, `test_o_processo_ativo_nao_tem_ato_cheio_fora_do_grupo`; `test_polish_da_057.py`; V 1 |
| **FR-1070** | F`processo_detalhe.html`: "Ativar" `botao secundario` com a ajuda; a frase de ausência; o aviso depois dos atos | TP `test_o_processo_em_elaboracao_tem_ativar_secundario_e_cancelar_a_parte`, `test_sem_ato_o_cartao_diz_que_nao_ha`; `test_processo.py`; AÇ |
| **FR-1071** | F`base.html`: `.rolavel-no-estreito` na `@media (max-width:60rem)` da `.distribuicao-moldura`; F`lista.html`: a tabela de cada Processo na moldura (D-003) | TP `test_a_moldura_rola_so_abaixo_de_60_rem_na_mesma_regra_da_alocacao`, `test_a_tabela_mora_na_moldura`; V 2, 3 |
| **FR-1072** | a moldura sem regra acima de 60 rem; a `.distribuicao-moldura` intocada | TP `test_a_moldura_rola_so_abaixo_de_60_rem_na_mesma_regra_da_alocacao`; V 5 |
| **FR-1073** | F`marco.html`: "Recortes deste marco" na moldura | TP `test_a_tabela_mora_na_moldura`; V 4 |
| **FR-1074** | F`matriculas.html`: a `section` sem `.resumo` | TP `test_a_secao_das_matriculas_nao_e_fileira_de_numeros`; V 6 |
| **FR-1075** | F`resultados.html`: `table.tabela`, `numero` só na nota pontuada (D-009) | TP `test_nos_resultados_so_a_nota_vai_a_direita`; V 7 |
| **FR-1076** | `plural` e `contagem` em F`distribuicao.html`, F`matriculas.html`, F`recurso.html`, F`ocupacao.html`, F`ocupacao_historico.html`, F`compor_base.html` (D-004) | TP `test_os_plurais_da_tela_concordam_com_o_numero` (seis casos), `test_a_previa_das_matriculas_escreve_linha_no_numero_dela`; V 8 |
| **FR-1077** | a frase que grava (F`ocupacao.html`, o déficit) fica; três asserções reescritas: `test_compor_quadro.py`, `test_consolidar_todas_as_prontas.py`, `test_resultado_da_etapa.py` | TP `test_os_plurais_da_tela_concordam_com_o_numero` (`FICA`) |
| **FR-1078** | `forms._no_campo` em `forms.etapas_do_edital` (D-005) | TP `test_os_numeros_das_etapas_chegam_ao_campo_sem_zeros_a_direita`; V 9 |
| **FR-1079** | o mesmo; a reexibição (`views._reexibir_etapas`) intocada | [rascunho-antes.json](rascunho-antes.json) × [rascunho-depois.json](rascunho-depois.json); V 10 |
| **FR-1080** | o estilo próprio de F`compor_revisao.html`: `min(16rem,40%) 1fr` (D-006, D-012) | TP `test_a_coluna_de_rotulos_da_revisao_tem_uma_largura_so`; V 11 |
| **FR-1081** | o `min(…, 40%)`; o rótulo mais longo quebra na coluna | TP `test_a_coluna_de_rotulos_da_revisao_tem_uma_largura_so`; V 11 (375 px) |
| **FR-1082** | F`ocupacao.html` e F`sorteio.html`: `textarea rows="3"` em `p.campo` (D-007, D-013) | TP `test_o_motivo_de_sucessao_tem_o_mesmo_controle_nas_quatro_telas` (quatro casos); V 12 |
| **FR-1083** | F`sorteio.html`: "Motivo da anulação" intocado (D-008) | TP `test_o_motivo_da_anulacao_fica_como_esta` |
| **FR-1084** | `specs/056-…/research.md` (decisão 003), `contracts/assistente.md` e `tasks.md` da `056`: 60 rem | `git diff` do PR; o total da suíte na [verificação](verificacao.md) |
| **FR-1085** | nenhuma ação, `href`, `action` ou `formaction` mudou | AÇ (62 telas, duas identidades): vazio |
| **FR-1086** | só a grafia dos três números das Etapas | [envio-etapas-antes.json](envio-etapas-antes.json) × [envio-etapas-depois.json](envio-etapas-depois.json); V 13 |
| **FR-1087** | nenhuma view, permissão, domínio ou PDF no diff; texto só nos plurais | `git diff` do PR; AÇ |
| **FR-1088** | uma classe nova (`.rolavel-no-estreito`), com regra; o parcial resolvido pelo `_estilo_proprio` | TA; TE (82.477 → 82.498); V 14 |

## 2. Requisitos de experiência

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **UX-143** | os atos do Processo como os do Edital; o motivo com um controle; a nota pela regra numérica | TP (R1, R4, R8); V 1, 7, 12 |
| **UX-144** | a moldura que rola abaixo de 60 rem | TP (R2); V 2, 3, 4 |

## 3. Critérios de sucesso

| Identificador | Medida | Onde |
|---|---|---|
| **SC-411** | nenhum ato cheio no Processo Ativo | V 1 |
| **SC-412** | Lista a 375: documento 375, moldura alcança o último botão | V 2, 3 |
| **SC-413** | Condução a 375: documento 375 | V 4 |
| **SC-414** | Alocação: cabeçalho fixo | V 5 |
| **SC-415** | Matrículas: nota abaixo do título | V 6 |
| **SC-416** | Resultados: notas à direita, texto à esquerda | V 7 |
| **SC-417** | nenhum "(s)" nas telas tocadas | V 8 |
| **SC-418** | Etapas "2", "6"; rascunho idêntico | V 9, 10 |
| **SC-419** | Revisão: o mesmo x — parcial, D-012 | V 11 |
| **SC-420** | o mesmo controle e largura do motivo | V 12 |
| **SC-421** | destinos e envio idênticos | AÇ; V 13 |
| **SC-422** | suíte verde; distribuição < 120.000 | V 14, 15 |
| **SC-423** | a `056` diz 60 rem | o diff do PR |
