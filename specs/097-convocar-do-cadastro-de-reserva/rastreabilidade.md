# Rastreabilidade — 097 · Convocar do cadastro de reserva, na ordem publicada

**Frase que governa**: *a vaga que o Edital regular libera entra aqui como fato registrado, com
origem e autor, e daí em diante o certame é o de um Edital com vaga publicada.*

Cada linha aponta onde o requisito entrou e o teste que o prende **pelo nome**. Onde a linha diz
*"leitura do diff"*, a promessa é negativa — algo que não pode ter acontecido — e se confere lendo a
mudança. Abreviações dos arquivos de teste:

- **UA** — `tests/unit/ocupacao/test_acrescimo.py`
- **UB** — `tests/unit/ocupacao/test_acrescimo_append_only.py`
- **IA** — `tests/integration/ocupacao/test_acrescimo.py`
- **IR** — `tests/integration/convocacao/test_reserva.py`
- **TA** — `tests/interface/test_acrescimo.py`
- **RV** — `tests/unit/editais/test_reserva_convocada_fora.py`
- **PA** — `tests/performance/test_acrescimo.py`

---

## 1. Requisitos

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **FR-2450** | `ocupacao/models.py::AcrescimoDeVagas`; `ocupacao/application/acrescimo.py::acrescentar_vagas` | IA `test_no_recorte_sem_apuracao_grava_e_emite_a_primeira`, `test_o_edital_publicado_nao_muda`, `test_os_campos_sao_conferidos` |
| **FR-2451** | `acrescimo.py::conferir_campos`; `ck_acrescimo_com_origem`, `ck_acrescimo_com_fundamento` | IA `test_os_campos_sao_conferidos`, `test_as_constraints_recusam_o_acrescimo_malformado`; TA `test_a_recusa_volta_a_ocupacao_com_a_frase_do_dominio` |
| **FR-2452** | `ocupacao/application/emissao.py::_apurar` lê e congela; `domain/apuracao.py::apurar(acrescidas=)` | UA `test_zero_publicada_com_duas_acrescidas_da_duas_efetivas`; IA `test_a_emissao_seguinte_le_congela_e_soma`, `test_acrescimo_de_outro_recorte_nao_alcanca_este`, `test_o_corte_sucedido_nao_o_desfaz_nem_o_duplica` |
| **FR-2453** | `ocupacao/application/selectors.py::_acrescimo_posterior`, a sexta causa | IA `test_acrescimo_posterior_torna_a_apuracao_obsoleta`, `test_apuracao_sem_a_lista_congelada_so_e_obsoleta_com_acrescimo` |
| **FR-2454** | `acrescimo.py::_emitir_seguinte`, pela porta `emitir_sucessora_por_efeito`, num *savepoint* | IA `test_sobre_a_apuracao_vigente_emite_a_sucessora_com_o_autor_e_o_motivo`, `test_com_outra_causa_presente_grava_e_nao_emite` |
| **FR-2455** | nada muda na convocação: ela lê a apuração (leitura do diff); a `FR-889` da `050` revista nesta medida | IR `test_sem_acrescimo_a_chamada_continua_recusada`, `test_a_vaga_acrescida_faz_do_primeiro_da_ordem_um_titular_chamavel`, `test_o_desfecho_devolve_a_vaga_e_o_seguinte_e_chamado_sem_novo_acrescimo` |
| **FR-2456** | `acrescimo.py::previa_do_acrescimo`; `ocupacao_acrescimo.html` | IA `test_diz_as_vagas_depois_e_quem_a_ordem_alcanca`, `test_mostra_os_acrescimos_anteriores_com_a_origem`; TA `test_a_conferencia_diz_quem_a_ordem_alcanca_e_nao_grava_nada` |
| **FR-2457** | a assinatura em `_previa`; `_conferir_leitura` sob a trava; a view volta à conferência | IA `test_leitura_velha_e_recusada_sem_gravar`; TA `test_a_leitura_mudada_volta_a_conferencia_recalculada` |
| **FR-2458** | a chave em `comando_de_comissao` | IA `test_a_mesma_chave_devolve_o_mesmo_acrescimo` |
| **FR-2459** | `acrescimo.py::conferir_recorte` | UA `test_sem_ordem_vigente`, `test_sem_linha_no_quadro`, `test_o_impedimento_do_perfil_vem_antes` |
| **FR-2460** | `acrescimo.py::desfazer_acrescimo`; `ck_desfazimento_cita_o_acrescimo` | IA `test_com_o_titular_so_na_conta_e_aceito_e_ele_sai_da_conta`, `test_o_desfazimento_sem_citacao_e_recusado`; TA `test_o_desfazimento_tem_porta_na_lista_e_conferencia_com_motivo` |
| **FR-2461** | o desfazimento é lido pela mesma conta (`domain/acrescimo.py::saldo`) | UA `test_acrescimos_somam_e_desfazimentos_subtraem`; IA `test_o_desfazimento_e_descontado`, `test_com_o_titular_so_na_conta_e_aceito_e_ele_sai_da_conta` |
| **FR-2462** | `domain/acrescimo.py::restante`, `recusa_do_desfazimento`; `acrescimo.py::conferir_desfazimento`; `convocacao/application/selectors.py::pessoas_chamadas` | UA `test_quem_so_esta_na_conta_nao_impede`, `test_quem_foi_chamado_impede`; IA `test_quem_foi_chamado_trava_o_desfazimento`, `test_nao_passa_do_que_resta_do_acrescimo`, `test_a_pergunta_e_feita_dentro_do_ato_depois_da_trava`; IR `test_pessoas_chamadas_conta_quem_espera_e_quem_atendeu`, `test_desfazer_a_vaga_de_quem_foi_chamado_e_recusado_pela_trava_real`; TA `test_desfazer_a_vaga_de_quem_foi_chamado_e_recusado_com_a_frase` |
| **FR-2463** | `acrescimo.py::impedimento`; `versao` gravada no registro | UA `test_sem_reserva_recusa`; IA `test_perfil_sem_cadastro_de_reserva_e_recusado`; TA `test_perfil_sem_cadastro_de_reserva_nao_oferece_o_acrescimo` |
| **FR-2464** | `acrescimo.py::impedimento`; o recorte exato no registro | UA `test_linha_de_modalidade_ate_com_zero_recusa`, `test_reversao_declarada_recusa`, `test_a_modalidade_declarada_como_ampla_le_a_linha_geral`; IA `test_linha_de_modalidade_ate_com_zero_e_recusada`, `test_recorte_de_modalidade_e_recusado` |
| **FR-2465** | `comando_de_comissao`; `_edital_para_classificar(..., somente_gestao=True)` | IA `test_quem_nao_gere_a_comissao_e_recusado`; TA `test_quem_apura_ve_o_formulario_e_quem_audita_nao` |
| **FR-2466** | `auditar` com `OCUPACAO_ACRESCENTAR_VAGAS` e `OCUPACAO_DESFAZER_ACRESCIMO`; `OPERACOES`, `AGREGADOS`; `auditoria/selectors.py::_atos_da_conducao` | IA `test_a_trilha_registra_o_acrescimo_e_a_apuracao_com_o_mesmo_ator`, `test_a_trilha_registra_o_desfazimento` |
| **FR-2467** | a ajuda do formulário; nenhum leitor fora da gestão; o fundamento derivado da convocação não muda | TA `test_quem_apura_ve_o_formulario_e_quem_audita_nao`, `test_nada_fora_da_gestao_le_a_vaga_acrescida`; IR `test_o_fundamento_da_convocacao_nao_carrega_a_origem_do_acrescimo` |
| **FR-2468** | nenhum leitor no portal, na publicação, na divulgação, nas dúvidas nem nos avisos (prova de import) | TA `test_nada_fora_da_gestao_le_a_vaga_acrescida` |
| **FR-2474** | `editais/domain/validation.py::_reserva_convocada_fora`, `_alcance_da_faixa` | RV `test_zero_vaga_com_reserva_e_advertido`, `test_alvo_fixo_diz_alvo_mais_excedente`, `test_alvo_do_quadro_diz_so_o_excedente_que_aqui_e_tudo`, `test_com_continuacao_admitida_nao_diz_numero`; `tests/interface/test_advertencias_do_quadro.py::test_a_revisao_diz_como_a_reserva_e_convocada` |
| **FR-2475** | `validation.py::_reserva_com_linhas_reservadas` | RV `test_e_advertido_que_o_acrescimo_nao_o_alcanca`, `test_so_a_linha_geral_nao_e_advertido` |
| **FR-2476** | os dois avisos só no ato de publicação | RV `test_a_retificacao_nao_repete_o_aviso`, `test_a_retificacao_nao_repete` |
| **UX-220** | `ocupacao.html`: a linha *"Acrescidas depois da publicação"* com link para a lista | TA `test_confirmar_grava_e_volta_a_ocupacao_com_o_numero_e_a_lista` |
| **UX-221** | `ocupacao_acrescimo.html`, *"Quem a ordem alcança"* | TA `test_a_conferencia_diz_quem_a_ordem_alcanca_e_nao_grava_nada`, `test_com_mais_vagas_do_que_a_faixa_a_conferencia_diz_quantas_ficam_sem_pessoa` |
| **UX-222** | os botões *"Acrescentar N vaga(s)"* e *"Desfazer N vaga(s)"* | TA `test_com_mais_vagas_do_que_a_faixa_a_conferencia_diz_quantas_ficam_sem_pessoa`, `test_o_desfazimento_tem_porta_na_lista_e_conferencia_com_motivo` |

## 2. Critérios de sucesso

| Identificador | Como se mede | Onde |
|---|---|---|
| **SC-920** | o cenário do TMD pela interface | [verificacao.md](verificacao.md), *Demonstração*; a cadeia em IR |
| **SC-921** | dois atos confirmados e nenhuma apuração à mão | IR `test_a_vaga_acrescida_faz_do_primeiro_da_ordem_um_titular_chamavel` |
| **SC-922** | efetivas menos publicadas é o saldo congelado, também na apuração antiga relida | IA `test_a_apuracao_antiga_relida_continua_com_o_numero_dela`, `test_o_desfazimento_e_descontado` |
| **SC-923** | a frase do fora do sistema saiu da Revisão | RV `test_zero_vaga_com_reserva_e_advertido`; `tests/interface/test_advertencias_do_quadro.py::test_a_revisao_diz_como_a_reserva_e_convocada` |
| **SC-924** | o mesmo número de consultas com 1, 10 e 20 acréscimos | PA `test_a_previa_custa_o_mesmo_com_um_e_com_dez`, `test_a_tela_custa_o_mesmo_com_um_e_com_dez`, `test_o_ato_custa_o_mesmo_com_um_e_com_dez` |

## 3. Garantias do banco

| Garantia | Onde | O que a prende |
|---|---|---|
| Gatilho `acrescimo_de_vagas_imutavel` | `ocupacao/migrations/0004_vaga_acrescida.py` | IA `test_o_gatilho_recusa_alteracao_e_exclusao_por_queryset` |
| Privilégio ausente | `seguranca/papeis.py::TABELAS_APPEND_ONLY` (de 40 para 41) | UB `test_a_tabela_esta_declarada_como_append_only`; `tests/integration/test_database_permissions.py`, parametrizado |
| `save`/`delete` que recusam | `ocupacao/models.py::AcrescimoDeVagas` | UB `test_recusa_alteracao_pelo_orm`, `test_recusa_exclusao_pelo_orm` |
