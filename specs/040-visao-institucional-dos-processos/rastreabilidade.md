# Rastreabilidade — a visão institucional dos Processos Seletivos (040)

Requisito a requisito, do que a spec exige ao que o executa e ao que o prova. O guardião
`tests/test_citacoes_de_requisito.py` cobra **cada** identificador definido em `spec.md`, sem
tolerância para sufixo de letra.

**Caminhos relativos a `backend/`.** `visao_geral.py` é
`processo_seletivo/interface/visao_geral.py`; os templates ficam em
`processo_seletivo/interface/templates/interface/`.

## Requisitos funcionais

| Requisito | Onde é executado | Onde é provado |
|---|---|---|
| **FR-581** | `interface/urls.py` (rota `visao-geral`) · `views.py::visao_geral` · `visao_geral.html` | `tests/authorization/test_visao_institucional.py::test_com_a_capacidade_a_rota_abre` |
| **FR-582** | `visao_geral.py` — consome `versoes_vigentes`, `periodo_de_inscricoes` e `Inscricao`; nenhum cálculo no template | `tests/interface/test_visao_geral.py::test_sc207_a_visao_e_a_tela_de_inscricoes_dizem_o_mesmo_numero` |
| **FR-583** | `visao_geral.py::_editais_do_recorte` e `anos_disponiveis` — `institution_scope` na consulta | `tests/authorization/…::test_t19_ator_de_outro_escopo_nao_ve_processo_algum_do_escopo_alheio` |
| **FR-584** | `visao_geral.py` não lê campo pessoal algum; os templates só exibem agregados | `tests/interface/…::test_t16_nenhum_dado_pessoal_de_candidato_no_html` |
| **FR-585** | `visao_geral.py::Consolidado`, `_consolidar` e a propriedade `sem_conteudo` · `visao_geral.html` (bloco `.consolidado`) | `tests/unit/…::test_t08_o_consolidado_declara_publicados_parciais_e_fora_da_razao` · `::test_sem_conteudo_e_a_diferenca_e_nunca_negativa` · `tests/interface/…::test_o_denominador_nao_afirma_um_demais_que_nao_existe` · `::test_a_ressalva_aparece_quando_ha_ressalva` |
| **FR-586** | `visao_geral.py::contagens_por_edital` (rascunho em chave própria) · `_linha_do_edital.html` | `tests/interface/…::test_fr586_a_coluna_de_rascunhos_usa_o_termo_da_tela_dona` · `tests/unit/…::test_t04_periodo_aberto_marca_submetidas_como_parcial_e_nao_soma_rascunhos` |
| **FR-587** | `visao_geral.py::vagas_do_conteudo` — lê `profiles[].immediateVacancies` da versão vigente | `tests/unit/…::test_t07_as_vagas_sao_as_da_versao_vigente` · `::test_t01_edital_em_elaboracao_tem_vagas_e_razao_ausentes_e_nunca_zero` |
| **FR-588** | `visao_geral.py::linha_do_edital` e `_consolidar` — numerador recortado por `profile_id` | `tests/unit/…::test_t03b_edital_misto_usa_so_a_demanda_do_perfil_com_vaga` · `::test_t03c_o_consolidado_concorda_com_a_linha_no_edital_misto` · `tests/interface/…::test_sc213_o_edital_misto_declara_a_populacao_da_razao` |
| **FR-589** | `visao_geral.py::linha_do_edital` (ramo `perfis_com_vaga == 0`) | `tests/unit/…::test_t02_perfil_so_de_cadastro_reserva_tem_vagas_zero_e_razao_nao_aplicavel` |
| **FR-590** | `visao_geral.py::_consolidar` (`fora_da_razao`) · `visao_geral.html` | `tests/unit/…::test_t08_o_consolidado_declara_publicados_parciais_e_fora_da_razao` · `::test_t08b_recorte_inteiro_sem_denominador_nao_inventa_razao` |
| **FR-591** | `visao_geral.py::Numero.__post_init__` e `Numero.de` — `0` é valor | `tests/unit/…::test_numero_e_valor_ou_ausencia_nunca_os_dois_e_nunca_nenhum` · `tests/interface/…::test_sc208_edital_encerrado_sem_procura_mostra_zero_legitimo` |
| **FR-592** | Nenhum indicador de matrícula é calculado; `visao_geral.html` declara a ausência | `tests/interface/…::test_t18_a_pagina_declara_o_que_nao_mede` |
| **FR-593** | Rótulos de `visao_geral.html` e `_linha_do_edital.html` dizem *inscrições* | `tests/interface/…::test_fr593_nenhum_rotulo_de_contagem_diz_candidatos_ou_pessoas` · `tests/unit/…::test_t06_duas_inscricoes_da_mesma_pessoa_contam_duas` |
| **FR-594** | `visao_geral.py::Ausencia` (três espécies) e `Numero.parcial` · `_linha_do_edital.html` | `tests/interface/…::test_sc208_edital_sem_conteudo_publicado_mostra_ausencia_e_nao_zero` |
| **FR-595** | `visao_geral.py::linha_do_edital` (`parcial`) e `_consolidar` (`parciais`) | `tests/unit/…::test_t04_periodo_aberto_marca_submetidas_como_parcial_e_nao_soma_rascunhos` · `::test_t08_…` |
| **FR-596** | `visao_geral.html`, seção *O que esta página não mede* | `tests/interface/…::test_t18_a_pagina_declara_o_que_nao_mede` |
| **FR-597** | `visao_geral.py::recorte_de` (conjunto aceito) · `visao_geral.html` (controles) | `tests/interface/…::test_parametro_invalido_e_saneado_e_nao_derruba_a_pagina` |
| **FR-598** | `visao_geral.py::_editais_do_recorte` (relacionais) e `ler` (período **depois**) | `tests/interface/…::test_t14_o_filtro_por_situacao_do_periodo_seleciona_pelo_conteudo` · `tests/performance/test_visao_institucional.py::test_t21_o_recorte_de_um_ano_abre_so_os_snapshots_daquele_ano` |
| **FR-599** | `visao_geral.py::recorte_de` (ano corrente) e `anos_disponiveis` · `Recorte.rotulo` | `tests/interface/…::test_t11_abre_no_ano_corrente_e_declara_o_recorte` · `::test_t11b_o_seletor_oferece_todos_os_anos_como_escolha_explicita` · `tests/performance/…::test_t22_o_seletor_de_anos_nao_abre_snapshot_algum` |
| **FR-600** | `_linha_do_edital.html` — `<th scope="row">` com o link e o Processo nomeado | `tests/interface/…::test_sc207_…` (usa o link) · percurso do `quickstart.md`, passo 12 |
| **FR-601** | `visao_geral.py::_ordenar` e `_chave_de_ordem` — chave em tupla, e o sentido valendo para **todas** as ordens | `tests/unit/…::test_t09_a_ausencia_fica_ao_fim_nos_dois_sentidos` · `::test_o_sentido_vale_tambem_para_a_ordem_padrao` · `::test_toda_ordem_do_catalogo_responde_ao_sentido` |
| **FR-602** | `visao_geral.py::_marcas` e `Marca` · `_linha_do_edital.html` | `tests/unit/…::test_t05_periodo_encerrado_sem_ninguem_produz_zero_e_marca_de_atencao` · `::test_t05b_periodo_aberto_sem_ninguem_nao_produz_marca` · `tests/interface/…::test_t17_as_marcas_sao_legiveis_sem_cor` |
| **FR-603** | Nenhum score, motor de alerta ou notificação existe no módulo — `_marcas` devolve duas espécies fixas | `tests/unit/…::test_t05b_periodo_aberto_sem_ninguem_nao_produz_marca` (a ausência de marca é regra, não configuração) |
| **FR-604** | `visao_geral.py::CONSULTAR` · `identidade.py::PAPEIS["gestor"]` · `views.py` (`require_authorization_base`) | `tests/authorization/…::test_a_grafia_da_capacidade_e_a_mesma_nos_dois_lugares` · `::test_nenhum_outro_papel_recebe_a_capacidade` · `::test_t12_sem_a_capacidade_a_rota_devolve_403_explicado` |
| **FR-605** | `lista.html` (link condicionado) · `views.py::lista` (`pode_ver_visao`) · a recusa na própria view | `tests/authorization/…::test_sc211_quem_nao_tem_a_capacidade_nao_ve_o_caminho` · `::test_sc211_quem_tem_a_capacidade_ve_o_caminho` |

## Critérios de aceite

| Critério | Onde é provado |
|---|---|
| **SC-206** | `quickstart.md`, percurso de 17 passos — o cenário demonstrável do Princípio VI |
| **SC-207** | `tests/interface/test_visao_geral.py::test_sc207_a_visao_e_a_tela_de_inscricoes_dizem_o_mesmo_numero` |
| **SC-208** | `tests/interface/…::test_sc208_edital_sem_conteudo_publicado_mostra_ausencia_e_nao_zero` · `::test_sc208_edital_encerrado_sem_procura_mostra_zero_legitimo` |
| **SC-209** | `tests/performance/test_visao_institucional.py::test_t20_o_numero_de_consultas_nao_cresce_com_o_numero_de_editais` |
| **SC-210** | `tests/interface/…::test_t16_nenhum_dado_pessoal_de_candidato_no_html` |
| **SC-211** | `tests/authorization/…::test_t12_sem_a_capacidade_a_rota_devolve_403_explicado` · `::test_sc211_quem_nao_tem_a_capacidade_nao_ve_o_caminho` |
| **SC-212** | `tests/interface/…::test_t18_a_pagina_declara_o_que_nao_mede` |
| **SC-213** | `tests/unit/…::test_t03b_…` e `::test_t03c_…` (o cálculo) · `tests/interface/…::test_sc213_o_edital_misto_declara_a_populacao_da_razao` (a declaração) |
| **SC-214** | `tests/performance/…::test_t21_o_recorte_de_um_ano_abre_so_os_snapshots_daquele_ano` · `::test_t22_o_seletor_de_anos_nao_abre_snapshot_algum` |

## O que ficou registrado e não executado

| Item | Razão |
|---|---|
| `T005` — `selecoes_publicas` consumir `versoes_vigentes` | **Não executada.** `versoes_vigentes` já existia (`023`, `FR-004a`) e a `040` a consome; o que sobra é a duplicação **pré-existente** dentro de `selecoes_publicas`, que mistura *qual é a vigente* com *o que é público*. Removê-la exigiria ou uma consulta a mais na vitrine pública, ou empurrar política de visibilidade para o resolvedor compartilhado. Achado registrado, fora do escopo desta feature. |

## Os cinco defeitos da primeira entrega

Encontrados na revisão de produto de 21/09, depois de a `040` estar verde. Nenhum era requisito
novo: quatro eram texto que dizia o que não valia, e o primeiro era um controle que não obedecia.

| Defeito | Correção | Prova |
|---|---|---|
| `_ordenar` ignorava `sentido` na ordem padrão — o controle *Maior / Menor primeiro* não fazia nada | o sentido vale para as quatro ordens; a crescente é a decrescente invertida | `tests/unit/…::test_o_sentido_vale_tambem_para_a_ordem_padrao` · `::test_toda_ordem_do_catalogo_responde_ao_sentido` |
| *"em 3 de 3 Editais — os demais…"* afirmava um "demais" inexistente | três ramos, e `Consolidado.sem_conteudo` como propriedade derivada | `tests/interface/…::test_o_denominador_nao_afirma_um_demais_que_nao_existe` · `::test_a_ressalva_aparece_quando_ha_ressalva` |
| coluna **Inscrições** mostrava o período, ao lado de **Submetidas** | **Período de inscrições** | `tests/interface/…::test_a_coluna_do_periodo_nao_se_chama_inscricoes` |
| filtro **Inscrições**, o mesmo | **Situação do período** | `tests/interface/…::test_o_filtro_do_periodo_nao_se_chama_inscricoes` |
| `Edital(is)` · `Perfil(is)` · `inscrição(ões)` | `pluralize` no template, flexão em código no Python | `tests/interface/…::test_nenhuma_flexao_de_planilha_na_tela` |

**A suíte da primeira entrega passava inteira com o primeiro deles**: `T-09` exercitava uma das
quatro ordens, e era a única que **não** era a padrão. A guarda nova cobre as quatro.

