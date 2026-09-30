# Rastreabilidade — 054 · O Edital do sistema como ato oficial

**Frase que governa**: *o documento só publica o que alguém escreveu, e fecha como um ato.*

Cada linha aponta o lugar do código e o que o prende. **TC** = `tests/unit/editais/test_catalogo_da_054.py`;
**TF** = `tests/unit/publicacoes/test_fecho_e_normas_da_054.py`; **TA** =
`tests/unit/editais/test_avisos_do_documento_oficial.py`; **TT** =
`tests/integration/publicacoes/test_topologia_do_acervo.py`; **TD** =
`tests/integration/publicacoes/test_consolidado_datado.py`; **TP** =
`tests/integration/publicacoes/test_fecho_publicado.py`; **TV** = `tests/interface/test_conteudo_da_054.py`;
**TJ** = `tests/javascript/conteudo.test.js`; **28** = a verificação do Edital 28/2026 do quickstart §2,
com a comparação seção a seção em [verificacao-28-2026.md](verificacao-28-2026.md).

---

## 1. Requisitos

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **FR-980** | `editais/domain/secoes.py`: `CATALOGO` de 22 | `test_secoes.py::test_o_catalogo_tem_as_secoes_declaradas_na_ordem`, `::test_as_posicoes_cumprem_a_leitura_de_um_edital`; TC `test_as_quinze_secoes_do_28_2026_tem_lugar_no_catalogo`; 28 |
| **FR-981** | as 12 chaves de antes mantidas | `test_secoes.py::test_a_identidade_deriva_da_chave_e_nao_muda_com_a_renumeracao`; `test_compor.py::test_secao_textual_editada_e_gravada_e_reexibida` |
| **FR-982** | `pdf._materializaveis`; `validation._topologia_das_secoes` (texto vazio aceito); `publish_edital._sections` (`content: ""`) | TC `test_a_textual_vazia_nao_sai_e_a_numeracao_nao_abre_buraco`; `test_limites_de_borda.py::test_esvaziar_o_conteudo_de_secao_textual_e_aceito` |
| **FR-983** | `Secao` sem `default_text`; `forms.ler_secoes`; `secoes.texto_redigido` no reuso (`reaproveitamento.payload_do_conteudo`) | `test_reuso_das_secoes_da_054.py` (os quatro); `test_secoes.py::test_nenhuma_secao_tem_redacao_padrao`; TC `test_o_edital_intocado_nao_publica_texto_que_ninguem_escreveu`; `test_compor.py::test_salvar_conteudo_sem_editar_nada_nao_cria_linha` |
| **FR-984** | `pdf._norma_da_secao` → `_materializaveis` | TF `test_a_matricula_publica_o_momento_e_a_declaracao_mesmo_vazia`, `test_a_inscricao_vazia_com_teto_sai_com_a_frase_do_teto`, `test_o_texto_do_autor_vem_antes_da_norma_da_matricula` |
| **FR-985** | `pdf.numeracao`; `forms.secoes_do_edital`; `revisao._secoes_do_documento`; `retificacao._nome_da_secao` | `test_retificacao_numera_pelo_documento.py::test_a_secao_leva_o_numero_do_documento_e_a_vazia_diz_que_nao_sai`; TC `test_a_numeracao_das_telas_e_a_que_o_documento_imprime`; TV `test_cada_secao_mostra_o_numero_do_documento_ou_que_nao_sai`; `test_revisao.py::test_a_conferencia_mostra_cota_etapa_e_texto` |
| **FR-986** | `validation._secao_universal_vazia` (`section_universal_empty`); rótulo e destino na interface | TA `test_apresentacao_e_disposicoes_finais_vazias_recebem_um_aviso_cada`, `test_as_demais_vazias_nao_avisam`, `test_a_secao_universal_vazia_nunca_impede_e_so_e_dita_na_publicacao`, `test_o_aviso_da_redacao_padrao_nao_existe_mais`; `test_revisao_do_pr_221.py::test_os_dois_avisos_do_texto_da_secao_levam_ao_conteudo` |
| **FR-987** | `validate_for_publication(topologia=None)` | TT `test_o_edital_novo_continua_conferido_contra_o_catalogo_vigente` |
| **FR-988** | `retificacoes.topologia_publicada`, passada nos três pontos | TT `test_o_acervo_diverge_do_catalogo_vigente`, `test_retificar_o_texto_de_uma_secao_do_acervo_e_aceito`, `test_mexer_na_topologia_do_acervo_continua_recusado`, `test_acrescentar_ao_acervo_uma_secao_do_catalogo_novo_e_recusado` |
| **FR-989** | `pdf.fecho`, `LOCAL`, `_autoridade`; `humano.data_por_extenso` | TF `test_o_publicado_traz_local_e_data_antes_da_autoridade`; TP `test_o_documento_publicado_traz_a_data_da_publicacao_no_fuso_institucional`; `test_humano_data.py` |
| **FR-990** | `render_edital_pdf(data_do_ato=…)`, a regra por modo | TF `test_a_previa_recusa_data_e_consolidacao`, `test_o_publicado_sem_data_e_recusado`, `test_o_mesmo_conteudo_em_duas_datas_tem_o_mesmo_hash_e_so_o_fecho_muda` |
| **FR-991** | `Publicacao.signatory_appointment` (`publicacoes/0009`); os dois fluxos; API | TP `test_o_ato_de_nomeacao_e_registrado_na_publicacao_e_impresso`, `test_sem_ato_de_nomeacao_a_publicacao_o_registra_vazio` |
| **FR-992** | `autoridades.Autoridade` (cargo; nome e ato opcionais) | TF `test_o_catalogo_nao_traz_designacao_no_lugar_do_nome` |
| **FR-993** | `pdf._autoridade` | TF `test_sem_nome_o_fecho_diz_o_cargo_e_nada_no_lugar_do_nome`, `test_com_nome_e_ato_de_nomeacao_o_fecho_os_imprime` |
| **FR-994** | `autoridades.quem_assinou`; `selectors.participantes`; os templates de escolha e de resultado; a API aceita o nome vazio | TP `test_a_api_publica_com_o_nome_vazio_como_a_interface`; TF `test_quem_assinou_nao_deixa_separador_pendurado`; TP `test_quem_assinou_nas_telas_nao_deixa_separador_pendurado` |
| **FR-995** | `pdf.Consolidacao`, `marca_de_consolidacao`; `retificacoes._consolidacao` (pela versão-base) | TD `test_a_marca_lista_so_o_que_a_versao_base_incorpora`; TF `test_a_marca_diz_a_publicacao_original_e_cada_retificacao`, `test_a_marca_sai_logo_abaixo_do_anuncio_e_so_quando_ha_consolidacao`; TD (os três) |
| **FR-996** | `pdf.requerimento_de_matricula`, seção `matricula` | TF `test_a_matricula_publica_o_momento_e_a_declaracao_mesmo_vazia`; TV `test_a_matricula_diz_o_que_o_documento_acrescentara`; 28 |
| **FR-997** | `pdf._quadro_de_perfis` (`rodape`), `_total_de_vagas`; `_tabela(rodape=)` | TF `test_com_mais_de_um_perfil_a_tabela_termina_no_total`, `test_com_um_perfil_nao_ha_linha_de_total`; 28 |
| **FR-998** | nota de emenda na `SC-001` da `008` | leitura do diff (`specs/008-composicao-institucional/spec.md`) |
| **FR-999** | `scripts/gerar_fixture_documento.py`; `fixtures/contexto_publicado.json`, `autoridade_publicada.json`, `documento_publicado_v1.pdf` | `test_documento_publicado.py::test_o_documento_publicado_continua_byte_a_byte_o_mesmo`; a diferença conferida por `pdftotext`: só o fecho |
| **UX-130** | `compor_conteudo.html` (legenda com número e estado); `conteudo.js` | TV `test_cada_secao_mostra_o_numero_do_documento_ou_que_nao_sai`; TJ (os quatro); preview, quickstart §4 |
| **UX-131** | `compor_conteudo.html`: a ajuda da etapa | TV `test_a_tela_nao_fala_em_redacao_padrao` |
| **UX-132** | `forms.secoes_do_edital` (`norma`); `compor_conteudo.html` | TV `test_a_matricula_diz_o_que_o_documento_acrescentara` |
| **UX-133** | número e estado dentro da `<legend>`, que nomeia o campo | TV `test_o_numero_e_o_estado_sao_lidos_com_o_titulo` |

## 2. Critérios de sucesso

| Identificador | Situação | Como se mede |
|---|---|---|
| **SC-361** | Coberto | TC `test_as_quinze_secoes_do_28_2026_tem_lugar_no_catalogo`; 28 |
| **SC-362** | Coberto | TC `test_o_edital_intocado_nao_publica_texto_que_ninguem_escreveu` |
| **SC-363** | Coberto | TC `test_a_numeracao_das_telas_e_a_que_o_documento_imprime`; TV |
| **SC-364** | Coberto | TF `test_o_mesmo_conteudo_em_duas_datas_tem_o_mesmo_hash_e_so_o_fecho_muda`; TP |
| **SC-365** | Coberto | TF `test_sem_nome_o_fecho_diz_o_cargo_e_nada_no_lugar_do_nome`, `test_com_nome_e_ato_de_nomeacao_o_fecho_os_imprime` |
| **SC-366** | Coberto | TT `test_retificar_o_texto_de_uma_secao_do_acervo_e_aceito` |
| **SC-367** | Coberto | TD `test_o_original_nao_tem_marca_e_o_consolidado_tem_as_duas_datas` |
| **SC-368** | Coberto | TF `test_a_matricula_publica_o_momento_e_a_declaracao_mesmo_vazia`; 28 |
| **SC-369** | Coberto | TF `test_com_mais_de_um_perfil_a_tabela_termina_no_total`; 28 |
| **SC-370** | Coberto | `test_pdf.py` e `test_documento_publicado.py` inteiros, com a fixture refeita no mesmo commit |
