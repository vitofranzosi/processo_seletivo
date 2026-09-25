# Rastreabilidade — o Perfil de Vaga na visão institucional (041)

Requisito a requisito. O guardião `tests/test_citacoes_de_requisito.py` cobra **cada** identificador
definido em `spec.md`, inclusive o sufixo de letra da `FR-613a`.

**Caminhos relativos a `backend/`.** `visao_geral.py` é
`processo_seletivo/interface/visao_geral.py`; os templates ficam em
`processo_seletivo/interface/templates/interface/`.

## Requisitos funcionais

| Requisito | Onde é executado | Onde é provado |
|---|---|---|
| **FR-606** | `_perfis_do_edital.html` — segunda `<tr>`, `<details>` sem `open`, e guarda `{% if linha.perfis %}` | `tests/interface/test_visao_geral.py::test_t013_a_expansao_existe_nasce_recolhida_e_traz_as_colunas` |
| **FR-607** | `visao_geral.py::perfis_do_edital` · `_perfis_do_edital.html` | `tests/unit/…::test_os_perfis_saem_da_versao_vigente_com_denominacao_e_codigo` · `::test_o_perfil_sem_denominacao_cai_no_codigo` |
| **FR-608** | `visao_geral.py::Reserva.do_perfil` — três espécies, limite só na limitada | `tests/unit/…::test_as_tres_especies_de_reserva_se_distinguem` · `::test_reserva_limitada_sem_limite_legivel_nao_inventa_numero` |
| **FR-609** | `visao_geral.py::perfis_do_edital` (`locality` como publicado) · `_perfis_do_edital.html` | `tests/unit/…::test_a_localidade_ausente_fica_vazia_e_nao_vira_nao_informada` |
| **FR-610** | `visao_geral.py::contagens_por_edital` — rascunho por Perfil, mesma consulta | `tests/unit/…::test_em_preenchimento_e_contado_por_perfil` |
| **FR-611** | `visao_geral.py::perfis_do_edital`, pela mesma função de razão do Edital | `tests/unit/…::test_o_perfil_sem_vaga_imediata_tem_razao_nao_aplicavel_e_vagas_zero` |
| **FR-612** | `visao_geral.py::linha_do_edital` — numerador recortado, razão **recalculada** | `tests/unit/…::test_a_razao_do_edital_e_recalculada_e_nunca_soma_das_razoes` · `::test_a_razao_recalculada_difere_da_media_quando_os_denominadores_diferem` · `::test_vagas_e_submetidas_reconciliam_com_a_linha` |
| **FR-613** | `visao_geral.py::perfis_do_edital` chama `_marcas` **por Perfil** | `tests/unit/…::test_t021_edital_com_razao_acima_de_1_e_perfil_vazio_recebe_marca` |
| **FR-613a** | `visao_geral.py::_fora_do_quadro` e `vagas_do_conteudo` (`todos`) · `_perfis_do_edital.html` (texto, nunca linha) | `tests/unit/…::test_inscricao_de_perfil_removido_conta_no_edital_e_e_declarada` · `::test_sem_perfil_removido_a_diferenca_e_zero` · `tests/interface/…::test_t020_a_diferenca_sem_perfil_vigente_nao_vira_linha_da_tabela` |
| **FR-614** | `visao_geral.py::_marcas_do_edital` — dois denominadores, e a mensagem do Perfil quando há um só | `tests/unit/…::test_t023_cada_especie_declara_o_seu_denominador` · `::test_t023b_com_um_perfil_so_a_mensagem_e_a_do_perfil` · `tests/interface/…::test_t023b_com_varios_perfis_a_marca_nomeia_quantos_de_quantos` |
| **FR-615** | `visao_geral.py::_marcas` — *sem procura* independe de denominador | `tests/unit/…::test_t022_sem_procura_vale_sem_denominador` |
| **FR-616** | `specs/040-visao-institucional-dos-processos/spec.md` — a `FR-602` e a §11.1 anotadas | leitura · `tests/test_citacoes_de_requisito.py` |
| **FR-617** | `_linha_do_edital.html` — a linha do Edital intacta, com as sete colunas | `tests/interface/…::test_t013b_a_linha_principal_continua_com_as_sete_colunas` |
| **FR-618** | nenhuma consulta nova: o quadro e as contagens já estão carregados | `tests/performance/test_visao_institucional.py::test_o_custo_nao_cresce_com_o_numero_de_perfis` |
| **FR-619** | `<details>`/`<summary>` — teclado e estado são do navegador | `quickstart.md`, passo 10 (`R-004` do plano: automatizá-lo testaria o navegador) |
| **FR-620** | `_perfis_do_edital.html` — o controle é o `<summary>`, na segunda `<tr>` | `tests/interface/…::test_t018_o_controle_e_o_summary_e_a_linha_continua_sendo_link` · `::test_t014_o_details_esta_dentro_de_um_td_e_nao_solto_na_tr` |
| **FR-621** | `visao_geral.py::recorte_de` e `ler` (terceiro degrau) · `visao_geral.html` | `tests/interface/…::test_t027_o_filtro_reduz_a_tabela_e_o_consolidado_acompanha` · `::test_t028_filtro_sem_nenhum_marcado_declara_recorte_vazio` · `tests/performance/…::test_o_filtro_de_atencao_nao_acrescenta_consulta` |

## Critérios de aceite

| Critério | Onde é provado |
|---|---|
| **SC-215** | `quickstart.md`, percurso de 14 passos · `tests/interface/…::test_t013_…` |
| **SC-216** | `tests/performance/…::test_o_custo_nao_cresce_com_o_numero_de_perfis` · `::test_o_filtro_de_atencao_nao_acrescenta_consulta` |
| **SC-217** | `tests/unit/…::test_as_tres_especies_de_reserva_se_distinguem` |
| **SC-218** | `tests/unit/…::test_t023_cada_especie_declara_o_seu_denominador` · `tests/interface/…::test_t023b_…` |
| **SC-219** | `quickstart.md`, passo 10 — manual **de propósito** |
| **SC-220** | `tests/unit/…::test_o_perfil_sem_vaga_imediata_tem_razao_nao_aplicavel_e_vagas_zero` |
| **SC-221** | `tests/interface/…::test_t027_o_filtro_reduz_a_tabela_e_o_consolidado_acompanha` |

## O que a implementação encontrou

| Achado | Consequência |
|---|---|
| **O gatilho append-only barrou um ajudante de teste.** A primeira versão de `publicar_com_perfis` criava a `VersaoConsolidada` e a atualizava em seguida; `reject_consolidated_mutation` recusou — *"consolidated versions are append-only"* | O ajudante publica **já** com o conteúdo certo. As duas camadas de imutabilidade estão de pé, e o teste não é exceção a elas |
| **`"1 Editais"` no primeiro indicador.** O rótulo era literal, e a revisão da `040` só alcançou os denominadores | Flexionado com `pluralize:"l,is"`, como os demais |
| **A resolução de `include` do guardião de classes precisou virar transitiva.** O parcial novo é incluído por **outro parcial**, e a versão da `040` só via inclusão direta | `_de_quem_inclui` recursiva, com guarda contra ciclo — a próxima tela nessa situação entra coberta |
