# Rastreabilidade — 050 · A convocação como fluxo

**Frase que governa**: *o que é formalização vira gesto por recorte, com um registro por pessoa e o
alcance declarado antes; o que é decisão sobre uma pessoa continua por pessoa.*

**Verificação final**: ver a seção 5.

Cada linha aponta o lugar do código e o teste **pelo nome**. Onde a linha diz *"leitura do diff"*, a
promessa é negativa — algo que não pode ter acontecido — e se confere lendo a mudança. Os testes novos
estão em `tests/integration/convocacao/test_titulares_em_lote.py` (**TL**),
`test_nao_atendimento_em_lote.py` (**NA**), `test_apuracao_seguinte.py` (**AS**),
`test_especie_derivada.py` (**ED**), `tests/interface/test_convocacao_em_fluxo.py` (**TF**) e
`tests/unit/convocacao/test_alcance.py`, `test_especie.py`, `test_fundamento.py`.

---

## 1. Requisitos

| `FR-` | Onde entrou | O que o prende |
|---|---|---|
| **FR-860** | `convocacao/application/fluxo.py::convocar_titulares`; `convocar.py::convocar_em_sequencia` | TL `test_a_confirmacao_convoca_cada_titular_e_comunica_cada_um` |
| **FR-861** | `convocacao/domain/alcance.py::titulares_do_comeco_da_fila` | `test_alcanca_os_titulares_e_para_no_primeiro_suplente`, `test_nunca_pula_ninguem`; TL `test_so_um_titular_e_a_suplente_de_fora` |
| **FR-862** | `fluxo.py::previa_dos_titulares`; `convocacao.html`, seção *"Convocar os titulares num ato só"* | TL `test_a_previa_declara_os_titulares_e_para_na_suplente_sem_praticar_nada`; TF `test_a_previa_declara_o_alcance_antes_do_botao_e_nao_pratica_nada` |
| **FR-863** | `alcance.py::assinatura`; `fluxo.py::_conferir`, sob a trava | TL `test_o_alcance_que_mudou_recusa_sem_gravar_nada`; `test_a_ordem_entra_na_assinatura`, `test_apuracao_nova_muda_a_assinatura` |
| **FR-864** | `convocar_em_sequencia` passa cada pessoa por `_recusar_por_ordem` e `_recusar_por_deficit`, sobre o mesmo contexto; uma recusa desfaz o ato inteiro (leitura do diff) | TL `test_o_alcance_que_mudou_recusa_sem_gravar_nada`, `test_vencimento_passado_recusa_antes_de_gravar` |
| **FR-865** | a chave do gesto em `comando_de_comissao`; a chave derivada por pessoa em `comunicar_cada` | TL `test_repetir_a_confirmacao_nao_convoca_nem_comunica_de_novo` |
| **FR-866** | `fluxo.py::resolver_vencimento`, `eventos_do_cronograma`; `_vencimento_da_convocacao.html`; a origem na razão da trilha | TL `test_a_trilha_tem_uma_linha_por_pessoa_com_a_correlacao_do_gesto` (a origem), `test_a_confirmacao_convoca_cada_titular_e_comunica_cada_um` (o mesmo vencimento) |
| **FR-867** | `convocacao/domain/especie.py::derivada`; `convocar.py` deriva quando não vem | `test_especie.py` (5); ED `test_sem_especie_informada_o_titular_e_chamado_para_vaga_inicial`; TF `test_a_chamada_individual_nao_pergunta_a_especie_e_ja_comunica` |
| **FR-868** | `convocar.py`, recusa `especie_divergente_da_posicao` depois das recusas de ordem e vaga | ED `test_o_suplente_chamado_para_vaga_inicial_e_recusado` |
| **FR-869** | `convocacao/domain/fundamento.py`; `com_complemento` | `test_fundamento.py` (8); TL `test_a_confirmacao_convoca_cada_titular_e_comunica_cada_um` |
| **FR-870** | `fluxo.py::convocar_e_comunicar`, `fundamentos_por_especie`; `convocar(fundamento_por_especie=…)` deriva sob a trava | TF `test_a_chamada_individual_nao_pergunta_a_especie_e_ja_comunica` |
| **FR-871** | `convocar_titulares` e `convocar_e_comunicar` chamam `comunicar_cada` depois do `commit` | TL `test_a_confirmacao_convoca_cada_titular_e_comunica_cada_um`; TF `test_a_chamada_individual_nao_pergunta_a_especie_e_ja_comunica` |
| **FR-872** | `comunicar_cada` usa o `comunicar` da `019`, sem mudança: chave reservada antes, envio fora da transação, estado indeterminado recusado (leitura do diff) | TL `test_a_falha_de_um_envio_nao_desfaz_nem_impede_os_outros`, `test_repetir_a_confirmacao_nao_convoca_nem_comunica_de_novo` |
| **FR-873** | `comunicar_cada` conta enviadas, falhas e recusas; `_resultado_da_comunicacao.html` | TL `test_a_falha_de_um_envio_nao_desfaz_nem_impede_os_outros`; TF `test_o_gesto_convoca_e_conta_o_que_a_comunicacao_fez` |
| **FR-874** | `fluxo.py::previa_das_pendentes`, `emitir_pendentes`; seção *"Comunicações que ainda não saíram"* | TF `test_as_comunicacoes_que_falharam_sao_reemitidas_num_gesto`; `test_pendente_e_sem_desfecho_e_sem_envio` |
| **FR-875** | `fluxo.py::_impedimento` | TL `test_edital_sem_forma_declarada_impede_o_gesto` |
| **FR-876** | `comunicar_cada` não emite por publicação sem referência; `emitir_pendentes` a exige | TL `test_por_publicacao_o_prazo_espera_a_referencia` |
| **FR-877** | `fluxo.py::registrar_nao_atendimento_dos_vencidos` | NA `test_o_gesto_registra_um_desfecho_por_pessoa_com_efeito_e_trilha`; TF `test_o_gesto_dos_vencidos_aparece_e_registra_um_por_pessoa` |
| **FR-878** | `alcance.py::vencidas` | `test_so_o_vencimento_decorrido_entra_e_as_outras_sao_contadas`; NA `test_so_o_vencido_com_envio_entra_e_o_nao_iniciado_e_contado`, `test_sem_vencida_o_gesto_nao_acontece` |
| **FR-879** | `previa_dos_vencidos` com assinatura; seção *"Não atendimento das convocações vencidas"* | NA `test_desfecho_individual_depois_da_previa_muda_o_alcance` |
| **FR-880** | `desfechar.py::registrar`, o mesmo para os dois caminhos; a correlação do gesto na trilha | NA `test_o_gesto_registra_um_desfecho_por_pessoa_com_efeito_e_trilha` |
| **FR-881** | nenhum gesto para as outras espécies; o formulário individual do desfecho não mudou (leitura do diff) | NA `test_as_outras_especies_continuam_individuais`; os testes da `019` (`test_recusas.py`, `test_inercia.py`, `test_regularizacao.py`) |
| **FR-882** | `desfechar.py::apuracao_seguinte`; `ocupacao/application/emissao.py::emitir_sucessora_por_efeito` | AS `test_o_desfecho_sucede_a_apuracao_e_ela_nao_fica_obsoleta`; NA `test_o_gesto_emite_a_apuracao_seguinte_e_a_suplente_e_a_proxima`; `test_ciclo_do_77.py::test_o_ciclo_inteiro_do_77` |
| **FR-883** | a sucessora é ato append-only com autor, pela mesma conta (`_apurar`); `convocar` continua recusando apuração obsoleta | AS `test_o_desfecho_sucede_a_apuracao_e_ela_nao_fica_obsoleta`; `test_recusas.py` (apuração obsoleta) |
| **FR-884** | `apuracao_seguinte` só emite quando as causas são só `efeito_posterior` | AS `test_outra_causa_de_obsolescencia_nao_e_varrida` |
| **FR-885** | `_apurar(movimento_admitido=False)` devolve `None` sem gravar; `apuracao_seguinte` o diz como `moveria_vaga` | AS `test_a_conta_que_moveria_vaga_nao_e_gravada`; `test_dependencia_da_convocacao.py` (nenhum módulo da convocação grava movimento) |
| **FR-886** | só `INSERT`: nenhuma tabela, coluna ou migration nova (leitura do diff) | `test_append_only.py`, `test_database_permissions.py` |
| **FR-887** | os gestos passam por `comando_de_comissao` ou `exigir_base_de_comissao` | TL `test_quem_nao_tem_base_de_comissao_recebe_404` |
| **FR-888** | as prévias saem da leitura do recorte; as versões das pendentes, por conjunto; `convocar_em_sequencia` lê o contexto uma vez | `performance/test_convocacao.py::test_as_previas_da_050_nao_crescem_com_as_convocacoes_do_recorte` |
| **FR-889** | nada muda na recusa `sem_deficit`; o gesto só alcança quem ocupa pela contagem (leitura do diff) | `test_fila_so_de_titulares_alcanca_todos_sem_parada`, `test_deficit.py` |

## 2. Critérios de sucesso

| `SC-` | O que o prova |
|---|---|
| **SC-320** | TL `test_a_confirmacao_convoca_cada_titular_e_comunica_cada_um` — uma confirmação, N convocações e N comunicações |
| **SC-321** | TF `test_a_chamada_individual_nao_pergunta_a_especie_e_ja_comunica` e o formulário do gesto: o único campo por ato é o vencimento |
| **SC-322** | NA `test_o_gesto_registra_um_desfecho_por_pessoa_com_efeito_e_trilha` |
| **SC-323** | NA `test_o_gesto_emite_a_apuracao_seguinte_e_a_suplente_e_a_proxima`; `test_ciclo_do_77.py::test_o_ciclo_inteiro_do_77` sem a emissão manual depois da desistência |
| **SC-324** | TL `test_a_confirmacao_convoca_cada_titular_e_comunica_cada_um`, `test_a_trilha_tem_uma_linha_por_pessoa_com_a_correlacao_do_gesto` |
| **SC-325** | TL `test_o_alcance_que_mudou_recusa_sem_gravar_nada`; NA `test_desfecho_individual_depois_da_previa_muda_o_alcance`; TF `test_a_recusa_por_alcance_mudado_mostra_o_alcance_de_agora` |
| **SC-326** | `performance/test_convocacao.py::test_as_previas_da_050_nao_crescem_com_as_convocacoes_do_recorte` (5 e 85) |
| **SC-327** | estimativa por custo unitário; os gestos que a sustentam estão nas linhas acima |

## 3. A tela

| `UX-` | O que o prende |
|---|---|
| **UX-100** | TF `test_a_previa_declara_o_alcance_antes_do_botao_e_nao_pratica_nada` (*"2 pessoas serão convocadas"*, *"Convocar as 2"*); `test_o_gesto_dos_vencidos_aparece_e_registra_um_por_pessoa` (*"… das 2"*) |
| **UX-101** | TF `test_a_previa_declara_o_alcance_antes_do_botao_e_nao_pratica_nada` (*"da posição na fila"*, *"derivado do Edital…"*) |
| **UX-102** | TF `test_a_previa_declara_o_alcance_antes_do_botao_e_nao_pratica_nada` (a suplente de fora, com a razão); `test_o_reabilitado_que_nao_ocupa_para_o_gesto_com_a_razao_dele` |
| **UX-103** | TF `test_o_gesto_convoca_e_conta_o_que_a_comunicacao_fez`; `test_vocabulario_da_convocacao.py` sobre os arquivos novos |
| **UX-104** | TF `test_a_recusa_por_alcance_mudado_mostra_o_alcance_de_agora` |

## 4. Casos-limite

| Caso | O que o prende |
|---|---|
| O gesto nunca pula ninguém | `test_nunca_pula_ninguem` |
| Reabilitado por deferimento à frente | `test_o_reabilitado_que_nao_ocupa_para_o_gesto_com_a_razao_dele` |
| Reclassificado | nada novo: o reclassificado não ocupa e está no fim da fila, e o gesto para antes dele (`test_reclassificacao_integrada.py`) |
| Pessoa com chamada em aberto | TL `test_o_alcance_que_mudou_recusa_sem_gravar_nada` — ela já não está na fila |
| Sem apuração, obsoleta, sem ordem ou esgotada | `fluxo.py::_impedimento`; TL `test_edital_sem_forma_declarada_impede_o_gesto` (a mesma forma de impedimento) |
| Cadastro de reserva sem vagas | `FR-889` acima |
| Forma por publicação | TL `test_por_publicacao_o_prazo_espera_a_referencia` |
| Evento do Cronograma sem data de fim | `fluxo.py::eventos_do_cronograma` não o oferece (leitura do diff) |
| Titular eliminado | a vaga dele é de suplente, e o gesto não a alcança: `test_alcanca_os_titulares_e_para_no_primeiro_suplente` |
| Vencimento anterior ao envio | TL `test_vencimento_passado_recusa_antes_de_gravar` |
| Convocação sem vencimento | `test_so_o_vencimento_decorrido_entra_e_as_outras_sao_contadas` (*semVencimento*) |
| Prazo não iniciado | NA `test_so_o_vencido_com_envio_entra_e_o_nao_iniciado_e_contado` |
| Envio que falha no meio do gesto | TL `test_a_falha_de_um_envio_nao_desfaz_nem_impede_os_outros` |
| Estado indeterminado de envio | o `comunicar` da `019`, sem mudança; `comunicar_cada` conta a recusa (`test_comunicacao.py`) |
| Desfecho registrado durante a prévia | NA `test_desfecho_individual_depois_da_previa_muda_o_alcance` |
| Retificação entre a prévia e a confirmação | a versão e a forma entram na assinatura (`alcance.py::assinatura`) |
| Recorte grande | `test_as_previas_da_050_nao_crescem_com_as_convocacoes_do_recorte` |

## 5. Verificação final

Preenchida na entrega (T029), com os números da execução.
