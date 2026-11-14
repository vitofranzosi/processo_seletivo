# Rastreabilidade — 163 · O alcance da Etapa por Modalidade

**Frase que governa**: *a Etapa que não alcança a inscrição não existe para ela — nem na
participação, nem na progressão, nem na ordem, nem no que o candidato lê.*

Cada linha aponta onde o requisito entrou e o teste que o prende **pelo nome**. Onde a linha diz
*"por construção"*, a garantia vem de uma leitura que já existia e que o alcance não precisou tocar;
o teste citado é o que a exercita. Abreviações dos arquivos de teste:

- **UA** — `tests/unit/editais/test_alcance_da_etapa.py`
- **TC** — `tests/interface/test_composicao_do_alcance.py`
- **TP** — `tests/interface/test_alcance_no_pdf.py`
- **IO** — `tests/integration/resultados/test_operacao_com_alcance.py`
- **IU** — `tests/integration/classificacao/test_universo_com_alcance.py`
- **ID** — `tests/integration/divulgacao/test_inscricoes_com_alcance.py`
- **IR** — `tests/integration/publicacoes/test_retificacao_do_alcance.py`
- **G** — os guardiões que o campo novo atravessou: `tests/contract/test_forma_publicada.py`,
  `tests/contract/test_mutabilidade*`, `tests/contract/test_retificacoes_api.py`,
  `tests/unit/interface/test_revisao.py`, `tests/unit/publicacoes/test_alteracoes_legiveis.py`,
  `tests/unit/duvidas/test_cobertura.py`, `tests/unit/avaliacoes/test_elevacao.py`

---

## 1. Requisitos

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **FR-6960** | `EtapaAvaliacao.alcance`, `editais/0029`; `draft.py`; `serializers.py`; `forms.py::_alcance` | TC `test_so_estas_modalidades_grava_os_codigos_marcados`; UA `test_o_codigo_alcanca_a_modalidade_em_todos_os_perfis_que_o_tem` |
| **FR-6961** | `alcance.codigos` (`None` = todas); migration sem preenchimento | UA `test_sem_alcance_declarado_e_todas_as_inscricoes`, `test_a_etapa_para_todas_ocupa_qualquer_papel`; TC `test_a_etapa_nasce_alcancando_todas_as_inscricoes`; IO `test_a_etapa_para_todas_continua_como_antes` |
| **FR-6962** | `etapas._validate_alcance`; `ck_etapa_alcance_nao_vazio` | UA `test_a_gravacao_recusa_o_alcance_mal_formado`; TC `test_so_estas_sem_nenhuma_marcada_e_recusada_junto_do_campo` |
| **FR-6963** | `validation._coerencia_do_alcance` (`alcance_codigo_inexistente`); a pendência da elaboração mostra o achado | UA `test_a_gravacao_aceita_codigo_que_nenhum_perfil_tem`, `test_codigo_que_nenhum_perfil_tem_impede_a_publicacao` |
| **FR-6964** | `validation._papeis_das_etapas` (`alcance_em_papel_de_todos`) | UA `test_a_etapa_restrita_nao_compoe_a_ordem`, `test_a_etapa_restrita_nao_decide_por_todas_as_listas`, `test_a_restrita_pontuada_nao_e_medida_por_marco`, `test_a_decisoria_restrita_pode_ser_enumerada_por_marco` |
| **FR-6965** | `validation._coerencia_do_alcance` (`alcance_denominacao_divergente`) | UA `test_denominacao_divergente_do_codigo_alcancado_impede` |
| **FR-6966** | `publish_edital._stages` (`modalityCodes`); `canonical.SCHEMA_VERSION = 22`; `elevacao.DEGRAUS[22]`; `diz_o_mesmo_que_a_ausencia` | G `test_elevacao.py` (os quatro casos da Etapa vigente); TP `test_a_etapa_para_todas_compoe_o_texto_de_antes` |
| **FR-6967** | `mutabilidade.CONTRATO[("stages", "modalityCodes")]`; `retificacao.CAMPOS_ETAPA` (tipo `ALCANCE`); `alteracoes.py` | G `test_a_retificacao_alcanca_todo_campo_normativo_da_etapa`, `test_todo_campo_retificavel_do_contrato_vira_linha`; UA `test_a_caixa_vazia_da_retificacao_e_todas_as_inscricoes` |
| **FR-6968** | `alcance.alcanca`; `validation` (`alcance_alcanca_a_ampla`); `forms.modalidades_para_o_alcance` não oferece a ampla | UA `test_a_etapa_restrita_nunca_alcanca_a_inscricao_sem_modalidade`, `test_o_codigo_da_ampla_nao_restringe_etapa` |
| **FR-6969** | `prontidao.participacao_detalhada` lê `modality_id` da inscrição | IO `test_so_as_alcancadas_participam_e_a_particao_fecha` (as PCD e a ampla, que concorrem por concomitância, ficam fora) |
| **FR-6970** | a participação lê o conteúdo vigente no ato (`conteudo_vigente`) | IR `test_ampliar_passa_e_acrescenta_pendentes` (antes e depois da publicação) |
| **FR-6971** | `prontidao.restringir_a_participantes`, `participa_da_etapa`, `participacao_detalhada` | IO `test_so_as_alcancadas_participam_e_a_particao_fecha` |
| **FR-6972** | `prontidao._casos_da_progressao` | IO `test_quem_nao_e_alcancado_atravessa_a_etapa_sem_esperar_por_ela`, `test_o_desfecho_desfavoravel_tira_so_quem_foi_avaliado` |
| **FR-6973** | a distribuição já recusa não participante; `motivo_de_nao_participar` com `FORA_DO_ALCANCE_RECUSA` | IO `test_atribuir_quem_esta_fora_do_alcance_e_recusado` |
| **FR-6974** | a faixa continua a terceira regra de `restringir_a_participantes`, e o alcance entra como quarta, sem substituí-la. Nesta entrega as duas não incidem sobre a mesma Etapa (FR-6964) | por construção; os testes da `014` (`tests/integration/resultados/test_progressao_com_corte.py`) passam inalterados |
| **FR-6975** | `ocorrencia.py` (via `motivo_de_nao_participar`); a conclusão já pergunta `participa_da_etapa` | IO `test_registrar_ocorrencia_de_quem_esta_fora_do_alcance_e_recusado` |
| **FR-6976** | `prontidao.FORA_DO_ALCANCE`, `panorama_da_etapa`, `contagens`; `consolidacao._inscricoes_da_selecao` | IO `test_so_as_alcancadas_participam_e_a_particao_fecha`, `test_o_desfecho_desfavoravel_tira_so_quem_foi_avaliado` |
| **FR-6977** | a Etapa sem alcançados tem zero participantes e não é anterior de ninguém (`_casos_da_progressao`) | IO `test_a_etapa_sem_nenhum_alcancado_nao_trava_a_seguinte` |
| **FR-6978** | por construção: andamento, supervisão, carga, Mesa e Minhas atividades contam os participantes do panorama; a distribuição ganhou a frase e o filtro | IO `test_so_as_alcancadas_participam_e_a_particao_fecha` (as contagens que as telas leem) |
| **FR-6979** | a Retificação aceita ampliar; a participação lê a versão nova | IR `test_ampliar_passa_e_acrescenta_pendentes`, `test_devolver_a_etapa_a_todas_passa` |
| **FR-6980** | `retificacoes._recusar_alcance_estreitado_sobre_atribuicao`; `distribuicao._edital_do_processo(travar=True)` | IR `test_estreitar_sobre_atribuicao_e_recusado_na_elaboracao`, `test_restringir_a_etapa_para_todas_e_estreitar`, `test_atribuicao_feita_depois_da_elaboracao_recusa_a_publicacao`, `test_estreitar_sem_atribuicao_passa` |
| **FR-6981** | o Resultado é append-only e guarda a versão; nada o reescreve | IR `test_ampliar_depois_de_consolidar_nao_muda_o_resultado_feito` |
| **FR-6982** | por construção: o acompanhamento mostra só Etapas com Resultado visível, e quem não é alcançado nunca tem Resultado na Etapa | IO `test_registrar_ocorrencia_de_quem_esta_fora_do_alcance_e_recusado`, `test_o_desfecho_desfavoravel_tira_so_quem_foi_avaliado` (nenhum Resultado para os não alcançados) |
| **FR-6983** | `alcance.frase_do_alcance`; `pdf._etapas` (redações 1, 2 e 3); `apresentacao._parte` | TP `test_a_redacao_vigente_diz_o_alcance_em_frase`, `test_a_redacao_1_diz_o_alcance_no_par`, `test_a_etapa_para_todas_compoe_o_texto_de_antes`; UA `test_a_frase_do_documento_so_existe_na_etapa_restrita` |
| **FR-6984** | `revisao._etapa` (linha "Alcance"); a tela de Retificação mostra o campo. A página pública do Edital não descreve Etapas: ela entrega o documento, que já diz | G `test_todo_campo_do_contrato_tem_destino_na_conferencia` |
| **FR-6985** | `calculo._universo_por_alcance` | IU `test_a_restrita_por_ultima_nao_esvazia_a_ordem_da_ampla`, `test_cada_inscricao_e_decidida_pela_ultima_enumerada_que_a_alcanca`, `test_sem_restrita_por_ultima_a_leitura_e_a_de_antes` |
| **FR-6986** | `publicabilidade.reingressos_pendentes`, `_alcances_das_enumeradas` | ID `test_o_reingresso_nao_cobra_resultado_da_etapa_que_nao_alcanca`, `test_sem_restrita_o_reingresso_e_o_de_antes` |
| **FR-6987** | `divulgacao/domain/inscricoes.etapas_de_analise`; a mensagem de `inscricoes_etapa_invalida` | ID `test_a_restrita_nao_e_candidata_a_analise_das_inscricoes`, `test_a_mesma_etapa_para_todas_continua_candidata` |

## 2. Experiência

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **UX-730** | `_etapa.html` (grupo "A quem a Etapa se aplica"); `telas.css` (`.so-restrita` escondida sob "Todas") | TC `test_a_etapa_nasce_alcancando_todas_as_inscricoes`, `test_a_marca_esquecida_nao_restringe_a_etapa_para_todas`, `test_a_folha_esconde_a_lista_so_quando_todas_esta_marcada` |
| **UX-731** | `forms.modalidades_para_o_alcance`; `interface_extras.opcoes_do_alcance` | TC `test_a_etapa_nasce_alcancando_todas_as_inscricoes` ("— todos os Perfis"); UA `test_o_codigo_que_so_alguns_perfis_tem_alcanca_onde_existe` |
| **UX-732** | `distribuicao.html` (frase e filtro); `contagens["alcancadas"]`, `["fora_do_alcance"]` | IO `test_so_as_alcancadas_participam_e_a_particao_fecha` |

## 3. Critérios de sucesso

| Identificador | Como se verifica |
|---|---|
| **SC-2310** | TP `test_a_etapa_para_todas_compoe_o_texto_de_antes`; G os testes de elevação e de resumo canônico do acervo, inalterados no resultado |
| **SC-2311** | IO `test_so_as_alcancadas_participam_e_a_particao_fecha`, `test_atribuir_quem_esta_fora_do_alcance_e_recusado`, `test_registrar_ocorrencia_de_quem_esta_fora_do_alcance_e_recusado` |
| **SC-2312** | IO `test_quem_nao_e_alcancado_atravessa_a_etapa_sem_esperar_por_ela` |
| **SC-2313** | IR `test_estreitar_sobre_atribuicao_e_recusado_na_elaboracao` (a contagem de Atribuições não muda), `test_atribuicao_feita_depois_da_elaboracao_recusa_a_publicacao` |
| **SC-2314** | G `tests/contract/test_mutabilidade*` e `test_forma_publicada.py` passam com o campo novo |
| **SC-2315** | TC `test_a_etapa_nasce_alcancando_todas_as_inscricoes`: um código por linha, com os Perfis que o têm. O minuto é medida humana, a fazer na homologação |
| **SC-2316** | *(humano, pendente)* leitura do documento publicado por pessoa da CPS ou da comissão |
