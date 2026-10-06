# Rastreabilidade — 060 · Unidades institucionais e autoridades de publicação

**Frase que governa**: *o documento diz a unidade que praticou o ato, e responde por ele quem está
habilitado nela naquele dia.*

**Linha de base** (T001, 06/10/2026, sobre `879237db`, numa worktree temporária do mesmo commit):
`make test-pg` fechou em **9129 passando e 11 pulados**, em 906 s — os números que o `AGENTS.md`
registrava para a `058`. **Ao fechar** (T046, mesmo dia): **9247 passando e 11 pulados**, em 906 s —
os mesmos onze pulados, comparados por lista e não por total; os 118 a mais são os testes da `060`.

Cada linha aponta o lugar do código e o que o prende. Caminhos de teste relativos a `backend/tests/`.
**TR** = `unidades/test_registro.py`; **TS** = `unidades/test_sincronizacao.py`; **TV** =
`unidades/test_vigencia.py`; **TM** = `unidades/test_manter_autoridades.py`; **TD** =
`unidades/test_documento_da_unidade.py`; **TC** = `unidades/test_criacao_exige_unidade.py`; **TP** =
`unidades/test_publicar_com_autoridade.py`; **TQ** = `unidades/test_consulta_publica_da_unidade.py`;
**TE** = `interface/test_escolha_da_autoridade.py`; **TT** = `interface/test_tela_de_autoridades.py`;
**TA** = `authorization/test_gerir_autoridades.py`; **TU** = `acceptance/test_us_trocar_a_autoridade.py`;
**TB** = `contract/test_documento_publicado.py` (a fixture de bytes da `054`).

---

## 1. Requisitos

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **FR-1106** | `unidades/models.py`: `Unidade` | TR `test_o_codigo_da_unidade_e_unico`; TS `test_unidade_nova_e_registrada_com_trilha`, `test_entrada_malformada_e_recusada_sem_gravar_nada` |
| **FR-1107** | `Unidade.codigo` = `institution_scope`; nenhuma FK nova (`D-001`) | TC (o escopo do ator encontra a Unidade); a suíte inteira, que continua isolando, autorizando e numerando pelo escopo sem mudança |
| **FR-1108** | gatilho `unidade_codigo_imutavel`; `sincronizacao.sincronizar` com trilha | TR `test_o_codigo_da_unidade_nao_muda`, `test_o_resto_da_unidade_muda`; TS `test_mudanca_e_aplicada_com_antes_e_depois`, `test_codigo_fora_do_formato_e_recusado` |
| **FR-1109** | gatilho `unidade_nao_se_exclui`; recusa `unidade_retirada` | TR `test_nenhuma_unidade_se_exclui`; TS `test_retirar_uma_unidade_do_arquivo_e_recusado_sem_gravar_nada` |
| **FR-1110** | `processos/application/commands.py` (`exigir_unidade(…, ativa=True)`); `contexto_do_ato` e a manutenção exigem só registrada | TC (os quatro); TM `test_unidade_desativada_continua_recebendo_cadastro_correcao_e_encerramento`, `test_unidade_desativada_continua_exigindo_permissao_e_escopo` |
| **FR-1111** | `unidades/unidades.json`; `make preparar`; `scripts/docker/entrypoint.sh` | TS `test_o_arquivo_versionado_declara_o_cefor_como_o_compositor_o_imprimia` |
| **FR-1112** | `pdf.INSTITUICAO`, `UnidadeDoAto`, `linhas_do_orgao`; `divulgacao/infrastructure/documento.py`; `inscricoes/infrastructure/comprovante_pdf.py`; `views.previa_documento` | TD (os quatro); TB |
| **FR-1113** | `pdf.fecho(local, data)` | TD `test_cada_documento_diz_a_propria_unidade_e_nada_da_outra`, `test_a_retificacao_diz_a_unidade_do_dia_dela_e_o_original_a_do_seu` |
| **FR-1114** | a Unidade `cefor` com as linhas e o local que eram constantes | TB `test_o_documento_publicado_continua_byte_a_byte_o_mesmo`, **sem** `documento_publicado_v1.pdf` refeito |
| **FR-1115** | `portal/views._unidade_da_versao` (da `source_publication` da versão aceita); `portal/comprovante.html` | TD `test_o_comprovante_diz_a_unidade_da_publicacao_aceita_e_nao_a_de_agora` (página e PDF, depois de renomear a unidade) |
| **FR-1116** | `AutoridadeHabilitada` | TR `test_a_autoridade_guarda_cargo_nome_ato_e_vigencia_e_nada_alem`, `test_o_cargo_e_obrigatorio` |
| **FR-1117** | identificador gerado; o catálogo com `1111…`/`2222…`/`3333…` removido | TE `test_a_tela_oferece_so_as_vigentes_da_unidade_e_nao_mostra_o_identificador`; TT `test_a_unidade_e_dita_pelo_nome_e_o_identificador_nao_aparece` |
| **FR-1118** | registros distintos por unidade, sem unicidade por pessoa (`D-003`) | TR `test_a_mesma_pessoa_pode_estar_habilitada_em_duas_unidades` |
| **FR-1119** | `unidades/domain/vigencia.vigente`; data do ato no fuso institucional | TV `test_a_vigencia_e_inclusiva_nas_duas_pontas`; TE `test_a_recusa_e_do_dominio_e_nada_e_gravado` (futura) |
| **FR-1120** | `autoridades.encerrar` (`encerramento_retroativo`, fim inclusivo); `CHECK`s; gatilhos `autoridade_nao_se_exclui` e `autoridade_usada_imutavel` (N1) | TM `test_encerrar_com_fim_hoje_a_oferece_hoje_e_a_retira_amanha`, `test_encerramento_retroativo_e_recusado`, `test_fim_antes_do_inicio_e_recusado`; TR `test_nenhuma_autoridade_se_exclui`, `test_o_fim_nao_pode_ser_anterior_ao_inicio`, `test_o_banco_recusa_fim_antes_do_dia_do_primeiro_ato_mesmo_gravado_direto`; TV `test_encerrar_com_fim_hoje_mantem_hoje_e_retira_amanha` |
| **FR-1121** | `autoridades.corrigir` (`autoridade_ja_usada`); `usada_em`; gatilhos `autoridade_usada_imutavel` e `autoridade_unidade_imutavel` (N2) | TM `test_corrigir_antes_do_uso_grava_antes_e_depois_inclusive_o_inicio`, `test_corrigir_depois_do_uso_e_recusado_com_a_orientacao`; TR `test_a_autoridade_usada_nao_se_reescreve`, `test_a_unidade_da_autoridade_nao_muda_nem_antes_do_uso`, `test_a_autoridade_ainda_nao_usada_se_corrige`; TT `test_a_usada_nao_oferece_correcao_e_diz_por_que` |
| **FR-1122** | `autoridade:gerir` no papel `gestor`; `views.autoridades` por `require_authorization_base`; o comando procura só no escopo do ator | TA (os três); TM `test_sem_a_permissao_e_recusado`, `test_autoridade_de_outra_unidade_e_indistinguivel_de_inexistente`; TT `test_sem_a_permissao_a_recusa_nomeia_o_que_falta`, `test_autoridade_de_outra_unidade_responde_como_inexistente`, `test_so_as_da_propria_unidade` |
| **FR-1123** | `autoridades._auditar`; rótulos em `views.OPERACOES` | TM `test_cadastrar_registra_com_trilha`, `test_corrigir_antes_do_uso_grava_antes_e_depois_inclusive_o_inicio`; `interface/test_trilha_legivel.py::test_toda_operacao_auditada_tem_rotulo_na_trilha` |
| **FR-1124** | `publicacoes/domain/autoridades.py` removido; o cadastro inicial é passo de implantação (quickstart §7, `doc/pendencias-da-060.md`) | TE (substitui os testes do catálogo da `007`); `test_citacoes_de_requisito.py` (as emendas da `007` e da `054` citam a 060) |
| **FR-1125** | `selectors.autoridades_vigentes`; `views._escolha_da_autoridade`; `_escolha_da_autoridade.html` nas quatro telas | TE `test_a_tela_oferece_so_as_vigentes_da_unidade_e_nao_mostra_o_identificador`, `test_publicar_retificacao_tambem_escolhe_entre_as_da_unidade`; TP `test_o_resultado_recusa_como_o_edital` |
| **FR-1126** | `autoridades.autoridade_para_o_ato` (trava, unidade, vigência), chamada por `contexto_do_ato` nos três comandos | TE `test_a_recusa_e_do_dominio_e_nada_e_gravado`; TP `test_o_resultado_recusa_como_o_edital`, `test_encerrar_enquanto_a_publicacao_espera_e_visto_por_ela` |
| **FR-1127** | `recusa_certa` sem autoridade vigente; a frase do include; o botão desabilitado | TE `test_sem_autoridade_vigente_a_tela_diz_por_que_e_nao_oferece_o_botao` |
| **FR-1128** | `Publicacao.unidade_*` (`publicacoes/0010`); `PublicacaoResultado.unidade_*` e `signatario_ato_de_nomeacao` (`divulgacao/0004`); `conteudo_divulgado(…, unidade)` | TE `test_publicar_pela_escolha_congela_a_autoridade_e_a_unidade`; TP `test_o_resultado_congela_autoridade_ato_de_nomeacao_e_unidade`; TD `test_o_resultado_congela_a_unidade_e_o_documento_a_le_dos_bytes` |
| **FR-1129** | colunas congeladas, sem FK para o registro | TE `test_a_publicacao_nao_muda_quando_a_autoridade_e_encerrada_e_a_unidade_renomeada`; TD `test_a_retificacao_diz_a_unidade_do_dia_dela_e_o_original_a_do_seu`; TQ |
| **FR-1130** | `publish_retification` compõe com o `contexto_do_ato` do dia dela | TD `test_a_retificacao_diz_a_unidade_do_dia_dela_e_o_original_a_do_seu` |
| **FR-1131** | `PublicacaoDetalheSerializer.get_unit`; `participantes_do_edital` e `detalhe.html` | TQ `test_a_consulta_diz_a_unidade_do_dia_mesmo_depois_de_renomeada`; `contract/test_consulta_publica_api.py::test_publication_detail_matches_contract` |
| **UX-148** | `rotulos.rotulo_da_autoridade` | TV `test_o_rotulo_distingue_duas_autoridades_do_mesmo_cargo`; TE `test_a_tela_oferece_so_as_vigentes_da_unidade_e_nao_mostra_o_identificador` |
| **UX-149** | `views._autoridades_em_grupos`; `autoridades.html` | TT `test_a_lista_separa_vigentes_futuras_e_encerradas_com_o_periodo`; TV `test_a_situacao_e_derivada_da_data_de_hoje`, `test_o_periodo_diz_desde_quando_e_ate_quando` |
| **UX-150** | a unidade pela sigla e pelo nome; só o escopo sem unidade registrada, que não tem nome, pelo código | TT `test_a_unidade_e_dita_pelo_nome_e_o_identificador_nao_aparece`, `test_escopo_sem_unidade_registrada_diz_isso_e_nao_oferece_cadastro` |

## 2. Critérios de sucesso

| Identificador | O que o prova |
|---|---|
| **SC-429** | TD `test_cada_documento_diz_a_propria_unidade_e_nada_da_outra` |
| **SC-430** | TB `test_o_documento_publicado_continua_byte_a_byte_o_mesmo`, com o PDF de referência intocado |
| **SC-431** | TE `test_a_recusa_e_do_dominio_e_nada_e_gravado`; TP `test_o_resultado_recusa_como_o_edital`, `test_encerrar_enquanto_a_publicacao_espera_e_visto_por_ela` |
| **SC-432** | TU `test_trocar_a_diretora_geral_sem_mudar_o_sistema`; o tempo de três minutos é do quickstart §4 |
| **SC-433** | TU; TE `test_a_publicacao_nao_muda_quando_a_autoridade_e_encerrada_e_a_unidade_renomeada`; TD `test_a_retificacao_diz_a_unidade_do_dia_dela_e_o_original_a_do_seu`; TQ |
| **SC-434** | TR `test_nenhuma_unidade_se_exclui`, `test_nenhuma_autoridade_se_exclui`; TS `test_retirar_uma_unidade_do_arquivo_e_recusado_sem_gravar_nada` |
