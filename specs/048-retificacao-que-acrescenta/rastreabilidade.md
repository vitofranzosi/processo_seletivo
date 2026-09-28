# Rastreabilidade — 048 · A Retificação acrescenta o que o contrato já permite

**Frase que governa**: *o que o domínio sustentava e nenhuma interface alcançava passa a ser
alcançável pela tela de Retificação — sem mecanismo novo, e sem que o que nasce valha menos do que a
composição exigiria.*

**Verificação final** (26/09/2026, sobre a `main` em `6b9f8d7`, com a `047` mesclada): `make preparar` em
**`34 de 34`**; `make lint check` — `ruff check` e `ruff format --check` limpos, `manage.py check`
sem problemas, `makemigrations --check` sem mudança —; `make test-pg` com **8173 passando e 11
pulados**, zero falhas.

Cada linha aponta o lugar do código e o teste **pelo nome**. Onde a linha diz *"leitura do diff"*, a
promessa é negativa — algo que não pode ter acontecido — e se confere lendo a mudança. **O 783 dos
requisitos e o 293 dos critérios ficaram sem uso** (spec, *Faixa de identificadores*): eram da
guarda genérica de objeto inteiro, que o parecer de 26/09 tirou do escopo (achado A-6).

---

## 1. Requisitos

| `FR-` | Onde entrou | O que o prende |
|---|---|---|
| **FR-777** | `interface/retificacao.py`: `NOVA_MODALIDADE`, `opcoes_da_modalidade_nova`, `_modalidade_nova`; `views.fragmento_retificacao_modalidade`; `_retificacao_modalidade.html` | `test_a_frase_antiga_saiu_e_o_botao_chegou`, `test_o_fragmento_oferece_os_perfis_vigentes`, `test_a_cota_acrescentada_com_vagas_leva_a_propria_linha` |
| **FR-778** | `editais/domain/perfis.py::validar_modalidade`, chamada ao conferir (`_modalidade_nova`) e no ato (`retificacoes._recusar_modalidade_que_a_composicao_recusaria`) | `test_ao_conferir_a_recusa_e_a_da_composicao` (6 casos, `test_retificar_modalidade.py`), `test_codigo_repetido_e_recusado_com_a_frase_da_composicao`, `test_a_forma_que_o_serializer_exigia_e_exigida` (4), `test_o_percentual_fora_da_faixa_tem_a_frase_da_regra_normativa` |
| **FR-779** | `_modalidade_nova`: declaração da ampla (`REPLACE generalCompetitionModalityId`) ou linha da cota (`ADD vacancyTable`), e a recusa da ampla com vagas | `test_a_ampla_acrescentada_emite_a_modalidade_e_a_declaracao`, `test_a_cota_acrescentada_com_vagas_leva_a_propria_linha`, `test_ao_conferir_a_recusa_e_a_da_composicao` (o caso da ampla com vagas), `test_confirmada_a_ampla_pela_tela_as_duas_alteracoes_sao_gravadas` |
| **FR-780** | nada novo: `_assert_well_formed` sobre o conteúdo retificado, como sempre (leitura do diff) | `test_a_cota_sem_linha_confirma_com_o_aviso_da_publicacao`, `test_a_cota_sem_linha_e_recusada_quando_o_corte_deriva_do_quadro` |
| **FR-781** | nada novo em inscrição, ordem, relação, sorteio: a garantia é de construção, e agora é provada | `test_modalidade_acrescentada_depois_nao_obsoleta_a_ordem_da_ampla` (retifica de fato), `test_a_ampla_acrescentada_recebe_o_nao_cotista_e_nao_mexe_em_quem_ja_enviou` |
| **FR-782** | `retificar.html`: a frase sai; a ajuda do Perfil diz que as Modalidades dele entram na Retificação seguinte | `test_a_frase_antiga_saiu_e_o_botao_chegou` |
| **FR-784** | o mecanismo `nascendo` de `diferencas`, com o complemento do registro; a validação de publicação sobre o objeto nascido | `test_a_regra_inteira_nasce_num_replace_so`, `test_o_prazo_informado_faz_nascer_a_janela_inteira`, `test_escolhida_a_especie_a_reversao_nasce_inteira`, `test_a_regra_pela_metade_e_recusada_com_as_mensagens_da_publicacao`, `test_zero_dias_e_recusado_pela_regra_que_ja_existe`, `test_sem_quadro_a_reversao_que_nasce_e_recusada` |
| **FR-785** | o complemento entra só depois de `_declarou_algo`; nenhum campo de nascimento é booleano; `_linhas_novas` ignora a identidade oculta | `test_retificar_so_um_texto_emite_so_um_texto` (POST lido da marcação), `test_nada_preenchido_nada_nasce`, `test_em_branco_nenhuma_janela_nasce`, `test_deixado_em_nenhum_nada_nasce`, `test_a_linha_deixada_em_branco_nao_acrescenta_nada` (2) |
| **FR-786** | `CAMPOS_DO_NASCIMENTO_DA_JANELA` e a entrada em `NASCIMENTOS` | `test_sem_janela_a_tela_oferece_so_o_prazo`, `test_a_janela_nascida_pela_tela_e_gravada`, `test_o_ato_divulgado_depois_da_retificacao_abre_o_prazo_que_ela_declarou` |
| **FR-787** | `publicacoes/domain/changes.py::recusar_janela_que_nasce_sem_recurso`, chamada pelo ato e **não** por `apply_changes` | `test_a_janela_que_nasce_sem_admitir_e_recusada` (4), `test_a_janela_que_nasce_sem_admitir_e_recusada_na_elaboracao`, `test_um_nascimento_anterior_a_guarda_nao_impede_a_retificacao_seguinte`, `test_a_janela_existente_alterada_nao_e_desta_guarda` |
| **FR-788** | `CAMPOS_DO_NASCIMENTO_DO_CORTE`, com os três campos que depois não se trocam | `test_o_marco_sem_regra_oferece_os_seis_campos`, `test_o_marco_com_regra_continua_com_os_tres_campos` |
| **FR-789** | `retificacoes._recusar_corte_sobre_etapa_com_resultado`, na elaboração e na publicação | `test_governando_etapa_com_resultado_e_recusado_na_elaboracao`, `test_resultado_registrado_depois_da_elaboracao_e_recusado_na_publicacao`, `test_a_regra_que_nao_governa_etapa_nasce_mesmo_com_resultado`, `test_governando_etapa_ainda_sem_resultado_a_regra_nasce` |
| **FR-790** | o destino do caminho da tela do corte passa a oferecer a regra; o endereço não mudou | `test_o_caminho_da_regra_termina_na_regra_daquele_marco`, `test_o_marco_por_sorteio_tambem_chega_a_regra` |
| **FR-791** | `CAMPOS_DA_REVERSAO` sempre oferecida | `test_o_campo_aparece_onde_o_objeto_nao_existe`, `test_com_a_linha_acrescentada_no_mesmo_ato_a_reversao_nasce` |
| **FR-792** | `NOVO_CRITERIO`, `opcoes_do_criterio_novo`, `_criterio_novo`; `views.fragmento_retificacao_criterio`; `_retificacao_criterio.html` | `test_o_botao_e_o_fragmento_existem`, `test_o_criterio_completo_vira_um_add_com_a_identidade_do_fragmento`, `test_confirmado_pela_tela_o_criterio_e_gravado` |
| **FR-793** | `perfis.validar_criterio`, ao conferir e no ato (`_recusar_criterio_que_a_composicao_recusaria`) | `test_ao_conferir_a_recusa_e_a_da_composicao` (4, `test_retificar_criterio.py`), `test_o_fato_de_outro_perfil_e_recusado`, `test_remover_um_e_acrescentar_outro_na_mesma_ordem_passa`, `test_o_criterio_acrescentado_pela_api_vale_o_que_a_composicao_exigiria`, `test_ordem_repetida_tem_a_frase_da_composicao` |
| **FR-794** | nada novo: `recorte_da_regra` já compara o marco inteiro (leitura do diff) | `test_acrescentar_criterio_obsoleta_a_ordem_como_a_remocao_ja_fazia` |
| **FR-795** | a tela de Retificação e os dois caminhos de acréscimo que já existiam; nenhuma API nova (leitura do diff) | os percursos 1 a 7 de [percursos.md](percursos.md) |
| **FR-796** | nada novo: a Versão Consolidada anterior é append-only | `test_a_ampla_acrescentada_recebe_o_nao_cotista_e_nao_mexe_em_quem_ja_enviou` (a versão anterior, pela API pública) |
| **FR-797** | nada novo: as leituras já partem de `effective_version` | `test_a_ampla_acrescentada_recebe_o_nao_cotista_e_nao_mexe_em_quem_ja_enviou` (inscrição e página pública), `test_o_ato_divulgado_depois_da_retificacao_abre_o_prazo_que_ela_declarou` (recurso), `test_governando_etapa_ainda_sem_resultado_a_regra_nasce` (corte) |
| **FR-798** | nada novo no PDF: ele é composto do conteúdo retificado | `test_o_documento_da_retificacao_mostra_as_seis` |
| **FR-799** | `rotulos_do_vazio` dos campos de nascimento; `_retificacao_linha.html` passa a dizer o vazio do campo que não é `select` | `test_sem_janela_a_tela_oferece_so_o_prazo`, `test_o_marco_sem_regra_oferece_os_seis_campos`, `test_o_campo_aparece_onde_o_objeto_nao_existe` |
| **FR-800** | o resumo de `diferencas`; `objeto_legivel` e os nomes dos objetos em `CAMPO_EM_PORTUGUES`, para a tela do ato (T039) | `test_a_regra_inteira_nasce_num_replace_so`, `test_o_prazo_informado_faz_nascer_a_janela_inteira`, `test_escolhida_a_especie_a_reversao_nasce_inteira`, `test_o_criterio_completo_vira_um_add_com_a_identidade_do_fragmento`, `test_a_ampla_acrescentada_emite_a_modalidade_e_a_declaracao`, `test_a_tela_do_ato_diz_a_regra_que_nasce_por_extenso`, `test_a_tela_do_ato_diz_a_linha_do_quadro_acrescentada` |
| **FR-801** | as frases de `_modalidade_nova`, `_criterio_novo`, `recusar_janela_que_nasce_sem_recurso` e `_recusar_corte_sobre_etapa_com_resultado` | os casos de recusa de FR-778, FR-787, FR-789 e FR-793, que conferem a frase |
| **FR-802** | dois fragmentos no molde da linha do quadro; o nascimento pelo `nascendo` que já existia (leitura do diff) | `test_a_retificacao_nao_acrescenta_marco_e_por_isso_nao_deriva_nada` (o conjunto exato de fragmentos) |
| **FR-803** | `NASCIMENTOS` e `_problemas_do_nascimento`, conferidos na carga do módulo | `test_o_registro_de_nascimento_recusa_o_que_o_contrato_nao_deixa_nascer`, `test_o_registro_de_nascimento_recusa_campo_fora_do_contrato_ou_do_objeto` (2) |

## 2. Critérios de sucesso

| `SC-` | Como se mede | Resultado |
|---|---|---|
| **SC-288** | inscrição de não-cotista pela ampla acrescentada, sem cancelar, sem API e sem banco | `test_a_ampla_acrescentada_recebe_o_nao_cotista_e_nao_mexe_em_quem_ja_enviou`; percurso 1 de [percursos.md](percursos.md) |
| **SC-289** | 0 inscrições mudam, 0 ordens de outro recorte ficam obsoletas, retificando de fato | `test_modalidade_acrescentada_depois_nao_obsoleta_a_ordem_da_ampla`, `test_a_ampla_acrescentada_recebe_o_nao_cotista_e_nao_mexe_em_quem_ja_enviou` |
| **SC-290** | 4 de 4 objetos que podem nascer com caminho pela tela (era 1) | `test_todo_objeto_que_pode_nascer_tem_caminho_pela_tela` — foi `xfail` estrito até a T015 |
| **SC-291** | o caminho da tela do corte chega à regra em todo marco sem regra | `test_o_caminho_da_regra_termina_na_regra_daquele_marco`, `test_o_marco_por_sorteio_tambem_chega_a_regra` |
| **SC-292** | 0 Retificações publicam o que a composição recusaria no que acrescentam | os casos de FR-778 e FR-793, ao conferir e pela API |
| **SC-294** | uma Retificação só de texto emite exatamente uma alteração | `test_retificar_so_um_texto_emite_so_um_texto` — e uma mutação que oferecia o booleano da janela para objeto ausente o fez reprovar |

## 3. Casos-limite

| Caso-limite | O que o prende |
|---|---|
| Perfil acrescentado no mesmo ato | leitura do diff: `_perfil_completo` continua nascendo sem Modalidade, e a ajuda de `retificar.html` diz que elas entram na Retificação seguinte |
| Documento Exigido para a Modalidade nova | leitura do diff: `opcoes_de_aplicabilidade` continua lendo o vigente, e nada nesta feature cria documento |
| Período de inscrições encerrado | leitura do diff: nada reabre o período |
| Rascunho de inscrição aberto | `test_o_rascunho_de_modalidade_unica_nao_envia_em_silencio` — *corrigido na implementação*: a assumida fica gravada, e a spec foi corrigida junto |
| Janela que nasce depois da divulgação | leitura do diff: a âncora (`recursos/domain/janela.py`) não foi tocada |
| Regra de corte que não governa Etapa | `test_a_regra_que_nao_governa_etapa_nasce_mesmo_com_resultado` |
| Resultado registrado entre a conferência e a publicação | `test_resultado_registrado_depois_da_elaboracao_e_recusado_na_publicacao` |
| Nada preenchido | `test_retificar_so_um_texto_emite_so_um_texto`, `test_nada_preenchido_nada_nasce`, `test_em_branco_nenhuma_janela_nasce` |
| Modalidade acrescentada com regra normativa | `test_a_cota_acrescentada_com_vagas_leva_a_propria_linha` (regra inteira, opacos vazios) |

## 4. Correlação com a auditoria

| | Situação depois da `048` |
|---|---|
| `RC-37` (`D-G5`) | **resolvido**: a Modalidade se acrescenta pela tela, e o percurso do não-cotista fecha. As linhas da auditoria ficam para depois do merge (T037) |
| `RC-38` | **resolvido**: janela, corte e reversão nascem pela tela; o critério se acrescenta; a tela do corte deixa de terminar num beco |
| `RC-111` | **não tocado, e ampliado**: o *"O que mudou"* público cala os nascimentos (achado A-4) |

## 5. O que a implementação mudou fora do previsto

- **`validate_profile` não chama as funções extraídas** (T002). Parte das exigências da composição
  mora no serializer da API; chamá-las de lá mudaria a composição pela tela. As frases são
  compartilhadas por constante.
- **A guarda de objeto inteiro saiu** antes da implementação (parecer de 26/09); ficou só a da janela.
- **`advertencias_do_ato` não chama a guarda** (T006): impeditivo é assunto do ato, como o docstring
  dela já dizia.
- **O critério aponta Etapa classificatória do Edital**, e não "do marco" (T020): é o que a
  composição oferece, e o `FR-793` foi corrigido para a regra da composição.
- **O caso-limite do rascunho** dizia que a escolha passaria a ser exigida; a Modalidade assumida
  fica gravada, e o envio só é barrado pelo reconhecimento da versão (T032).
- **A tela do ato** passou a dizer o objeto que nasce por extenso (T039), porque dizia "—"; e, achado
  do percurso pela tela, a linha do quadro acrescentada também, que chegava como "—" desde a `025`.
- **`_linhas_novas` ignora a identidade oculta** ao decidir se a linha está em branco: sem isso, a
  linha de critério ou de Modalidade deixada em branco pareceria declarada. Vale também para o Anexo.
