# Rastreabilidade — 162 · O limite do cadastro de reserva lido do corte

**Frase que governa**: *o número do cadastro de reserva limitado é o que o corte do marco que convoca
alcança além das vagas, e nenhum outro lugar o declara.*

Cada linha aponta onde o requisito entrou e o teste que o prende **pelo nome**. Onde a linha diz
*"leitura do diff"*, a promessa é negativa — algo que não pode ter acontecido — e se confere lendo a
mudança. Abreviações dos arquivos de teste:

- **UC** — `tests/unit/editais/test_cadastro_de_reserva.py`
- **UK** — `tests/unit/editais/test_coerencia_do_cadastro.py`
- **UP** — `tests/unit/editais/test_perfis.py`
- **UD** — `tests/unit/publicacoes/test_cadastro_de_reserva_no_documento.py`
- **UN** — `tests/unit/ocupacao/test_nota_do_cadastro_legado.py`
- **UO** — `tests/unit/portal/test_cadastro_de_reserva_no_portal.py`
- **IP** — `tests/integration/editais/test_cadastro_de_reserva_na_publicacao.py`
- **IR** — `tests/integration/publicacoes/test_cadastro_de_reserva_na_retificacao.py`
- **TI** — `tests/interface/test_cadastro_de_reserva.py`
- **TC** — `tests/interface/test_compor.py`
- **TG** — `tests/interface/test_campos_que_a_escolha_governa.py`
- **JS** — `tests/javascript/perfis.test.js`, `tests/javascript/validacao.test.js`

---

## 1. Requisitos

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **FR-6929** | `editais/domain/cadastro_de_reserva.py::do_perfil`, `_numeros`, `marcos_que_convocam` | UC `test_com_alvo_do_quadro_o_numero_e_o_excedente`, `test_com_alvo_fixo_e_o_alcance_menos_as_vagas`, `test_o_marco_intermediario_nao_conta`, `test_o_marco_que_governa_etapa_que_ninguem_le_convoca`, `test_o_perfil_do_seed_demo_da_dois_em_cada_lista` |
| **FR-6930** | `cadastro_de_reserva.py` lido por `pdf.py`, `portal/views.py`, `portal/situacao.py`, `interface/revisao.py`, `relatorio_do_edital.py`, `visao_geral.py`, `retificacao.py`, `duvidas/domain/respostas.py`, `perfis.js` (pelo `data-resumo`) | UD `test_c1_limitado_sem_modalidade`; UO `test_a_oferta_diz_o_numero_do_corte`, `test_o_assistente_diz_o_numero_e_cita_de_onde_ele_vem`; TI `test_a_revisao_diz_o_cadastro_pela_regra_unica`; JS `a reserva é o resumo que o servidor escreveu` |
| **FR-6931** | `editais/domain/perfis.py::validate_profile`; `interface/forms.py::ler_perfis`; `editais/domain/reaproveitamento.py::remapear` | UP `test_rejects_typed_limit_and_says_where_it_comes_from`; IP `test_a_api_recusa_o_numero_digitado`; TC `test_reserva_limitada_se_grava_sem_numero_e_o_campo_antigo_nao_grava_nada` |
| **FR-6932** | `forms.py::cadastro_para_o_cartao`, `_perfil_para_o_cadastro`; `_perfil.html` | TI `test_a_nota_sem_corte_nao_tem_numero`, `test_a_nota_com_numero_unico`, `test_a_nota_por_lista`, `test_a_nota_ignora_o_numero_digitado_e_a_especie_marcada`; TG `test_a_origem_do_numero_mora_dentro_da_reserva_que_a_tem` |
| **FR-6933** | `cadastro_de_reserva.py::incoerencias` (`reserve_limited_with_continuation`); `validation.py::_coerencia_do_cadastro` | UK `test_limitado_com_continuacao`, `test_validate_for_publication_nao_confere_continuacao_na_retificacao` |
| **FR-6934** | idem (`reserve_unlimited_without_continuation`) | UK `test_ilimitado_sem_continuacao`, `test_na_retificacao_so_o_zero_e_a_divergencia` |
| **FR-6935** | idem (`reserve_limited_without_cut`) | UK `test_limitado_sem_corte` |
| **FR-6936** | idem (`reserve_limited_to_nobody`) | UK `test_limitado_a_ninguem`, `test_limitado_a_ninguem_nomeia_a_lista`, `test_validate_for_publication_recusa_com_o_caminho_do_perfil` |
| **FR-6937** | as frases de `incoerencias`, caminho `/profiles/id=…/reserveType` | UK `test_limitado_com_continuacao` (Perfil, marco e o que mudar), `test_validate_for_publication_recusa_com_o_caminho_do_perfil` |
| **FR-6938** | `pdf.py::frase_do_cadastro` (`admite_empate`) | UD `test_c1_empate_que_admite_excedente` |
| **FR-6939** | `incoerencias` (`reserve_limited_divergent_milestones`) | UC `test_dois_marcos_que_convocam_expoem_os_dois`; UK `test_marcos_que_convocam_com_numeros_diferentes`, `test_par_coerente_nao_e_recusado[dois-marcos-iguais]` |
| **FR-6940** | `publish_edital.py::edital_snapshot`; `draft.py::advertencias_do_numero_digitado`, `replace_draft` (preserva o digitado); `views.py::_pendencias`; `editais/0028` | IP `test_a_composicao_nunca_leva_o_numero`, `test_a_revisao_diz_o_digitado_e_o_derivado`, `test_sem_advertencia_quando_os_numeros_coincidem`, `test_regravar_por_outra_etapa_nao_apaga_o_digitado`, `test_trocar_a_especie_apaga_o_digitado` |
| **FR-6941** | `pdf.py::frase_do_cadastro`, `_numeros_do_cadastro`, `_reserva` | UD `test_c1_mesmo_numero_em_cada_lista`, `test_c1_numeros_diferentes_por_lista`, `test_c2_as_tres_formas`, `test_exemplo_4` |
| **FR-6942** | `pdf.py::SUPLENTES_DO_CADASTRO`, `frases_do_corte` | UD `test_c4_perfil_com_cadastro_e_vagas`, `test_c4_perfil_sem_cadastro_explica_mesmo_com_outro_perfil_com_cadastro`, `test_exemplo_1` |
| **FR-6943** | `pdf.py::_corte_do_cadastro` | UD `test_c3_limitado`, `test_c3_limitado_com_um_so`, `test_c3_de_cada_lista`, `test_c3_ilimitado_com_alcance`, `test_c3_ilimitado_sem_alcance`, `test_c3_com_etapa_governada`, `test_c3_so_no_marco_que_convoca`, `test_exemplo_2` |
| **FR-6944** | `cadastro_de_reserva.py` (`legado`, `numero_mostrado`); `pdf.py::frases_do_corte` (o legado compõe a unidade de antes) | UD `test_c1_o_legado_imprime_o_que_publicou`, `test_c2_redacao_1`; IP `test_o_legado_publicou_o_numero_digitado_e_o_documento_o_diz`; `tests/unit/publicacoes/test_documento_da_auditoria_depois_da_069.py::test_o_documento_sai_com_os_bytes_gravados` (cenário B, legado, byte a byte) |
| **FR-6945** | `portal/views.py::_oferta`, `_por_lista`; `portal/situacao.py::frase_da_reserva` | UO `test_a_oferta_diz_o_numero_do_corte`, `test_a_oferta_com_o_mesmo_numero_em_cada_lista`, `test_a_oferta_do_legado_diz_o_que_publicou`, `test_a_frase_do_acompanhamento_diz_o_numero_do_corte`, `test_a_frase_do_acompanhamento_por_lista`, `test_a_frase_do_acompanhamento_do_legado` |
| **FR-6946** | `duvidas/domain/respostas.py::_p03` | UO `test_o_assistente_diz_o_numero_e_cita_de_onde_ele_vem[derivado]`, `[legado]`, `test_a_explicacao_do_assistente_diz_o_numero_sem_o_ate`; `tests/unit/duvidas/test_casos_da_revisao.py::test_cadastro_de_reserva_limite_e_reversao_vem_em_palavras` (o corpus, legado) |
| **FR-6947** | `ocupacao/application/selectors.py::nota_do_cadastro_legado`; `views.py::_nota_do_cadastro`; `ocupacao.html`, `convocacao.html` | UN `test_sem_continuacao_diz_o_alcance`, `test_com_continuacao_diz_que_a_faixa_cresce`, `test_sem_corte`, `test_por_lista`, `test_sem_nota_fora_do_legado`; TI `test_a_nota_do_legado_e_nota_e_nao_alerta` |
| **FR-6948** | `incoerencias` (o legado não é conferido); `retificacao.py::_campos_do_perfil` | UK `test_o_legado_nunca_e_recusado`; IP `test_o_legado_nao_ganha_achado_novo_na_retificacao`; IR `test_o_campo_do_limite_so_existe_no_perfil_legado` |
| **FR-6949** | `nota_do_cadastro_legado` (sem condição de divergência) | UN `test_a_nota_sai_mesmo_quando_os_numeros_coincidem` |
| **FR-6950** | `retificacao.py::_campos_do_perfil`, `_cadastro_retificado` | IR `test_o_campo_do_limite_so_existe_no_perfil_legado`, `test_retificar_o_excedente_muda_o_numero_e_a_conferencia_o_diz` |
| **FR-6951** | `incoerencias` com `na_publicacao=False` | UK `test_na_retificacao_so_o_zero_e_a_divergencia`; IR `test_levar_o_numero_a_zero_e_recusado` |

## 2. Critérios de sucesso

| Identificador | O que o prende |
|---|---|
| **SC-2298** | UD `test_um_numero_so_no_perfil_do_seed_demo`; UO (portal e assistente) e TI (Revisão) sobre os mesmos Perfis montados por UC; IP `test_o_legado_publicou_o_numero_digitado_e_o_documento_o_diz` |
| **SC-2299** | UD `test_c3_nunca_abre_por_seguem_ou_passam` |
| **SC-2300** | UK `test_limitado_com_continuacao`, `test_ilimitado_sem_continuacao`, `test_limitado_sem_corte`, `test_limitado_a_ninguem`, `test_marcos_que_convocam_com_numeros_diferentes`, `test_par_coerente_nao_e_recusado` |
| **SC-2301** | IP `test_o_legado_nao_ganha_achado_novo_na_retificacao`; UN; `test_documento_da_auditoria_depois_da_069.py` (cenário B recomposto byte a byte) |
| **SC-2302** | UD `test_um_numero_so_no_perfil_do_seed_demo`, `test_exemplo_2` |
| **SC-2303** | IR `test_retificar_o_excedente_muda_o_numero_e_a_conferencia_o_diz` |
| **SC-2304** | *humano, pendente* — `verificacao.md` |

## 3. Requisitos de experiência

| Identificador | O que o prende |
|---|---|
| **UX-725** | TI `test_o_cartao_nao_tem_mais_o_campo_do_numero` (um elemento, `p.nota`, ligado por `aria-describedby`, sem link) |
| **UX-726** | UK `test_limitado_com_continuacao`, `test_ilimitado_sem_continuacao` (as frases usam "cadastro de reserva", "continuação", "corte", e não `LIMITED`) |
| **UX-727** | TI `test_a_nota_do_legado_e_nota_e_nao_alerta` |

## 4. Casos-limite

| Caso | O que o prende |
|---|---|
| Empate que admite excedente | UD `test_c1_empate_que_admite_excedente` (FR-6938) |
| Mais de um marco que convoca | UC `test_dois_marcos_que_convocam_expoem_os_dois`; UK `test_marcos_que_convocam_com_numeros_diferentes` (FR-6939) |
| Alvo fixo menor que as vagas | UC `test_com_alvo_fixo_e_o_alcance_menos_as_vagas`; UK `test_limitado_a_ninguem[1-2]` (FR-6936) |
| Rascunho que guarda número digitado | IP `test_a_revisao_diz_o_digitado_e_o_derivado`, `test_regravar_por_outra_etapa_nao_apaga_o_digitado` (FR-6940) |
| Gravação que traz o número | IP `test_a_api_recusa_o_numero_digitado`; TC `test_reserva_limitada_se_grava_sem_numero_e_o_campo_antigo_nao_grava_nada` (FR-6931) |
| Ilimitado sem corte | UK `test_par_coerente_nao_e_recusado[ilimitado-sem-corte]` |
| "Não há" com suplentes e continuação (77/2026) | UK `test_par_coerente_nao_e_recusado[nao-ha-com-suplentes-e-continuacao-o-77]` (`D-006`) |
| Edital legado retificado | UK `test_o_legado_nunca_e_recusado`; IR `test_o_campo_do_limite_so_existe_no_perfil_legado` (FR-6948) |
| Legado com o mesmo número do corte | UN `test_a_nota_sai_mesmo_quando_os_numeros_coincidem` (FR-6949) |

## 5. Decisões

`D-001` a `D-007`: decisões de produto e de desenho registradas na spec; cada uma está presa pelos
requisitos que dela decorrem (acima). A `D-007` — nenhum teto executado — é promessa negativa:
*leitura do diff* (nenhum arquivo de `classificacao/`, `ocupacao/domain/` ou `convocacao/` lê o
número para decidir).
