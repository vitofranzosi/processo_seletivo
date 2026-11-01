# Rastreabilidade: Kit de Divulgação do Edital

Cada requisito leva à regra existente que ele reaproveita, à tarefa que o implementa e ao teste que o
verifica. **A matriz é de planejamento**: os testes são os que as [tarefas](tasks.md) criam, e a
T036 a confere contra o implementado. Caminhos relativos a `backend/`.

## Requisitos funcionais

| Requisitos | Regra existente reaproveitada | Tarefas | Testes |
|---|---|---|---|
| FR-3401 (ação no detalhe, pelo estado) | `interface/acoes.py` (`_navegacao`, `Acao.motivo`), padrão da `099` | T011 | `tests/interface/test_kit_de_divulgacao.py::test_a_acao_aparece_so_com_a_capacidade`, `::test_antes_da_publicacao_a_acao_e_indisponivel_com_motivo` |
| FR-3402 (404, recusa explicada, 409) | `obter_edital`; `require_authorization_base`; `INDISPONIVEL` da `099`; inventário da `033` | T010, T011 | `tests/authorization/test_kit_de_divulgacao.py`; `tests/test_gramatica_das_portas.py` |
| FR-3403 (capacidade própria, papel restrito, nada além) | `PAPEIS`/`DESCRICOES` (`interface/identidade.py`); precedentes `exportador` e piloto | T004, T010 | `tests/authorization/test_papel_da_comunicacao.py`; `test_kit_de_divulgacao.py::test_a_capacidade_nao_abre_ato_nenhum`; `tests/seguranca/test_vinculos.py` |
| FR-3404 (só vigente; nada de elaboração ou futuro) | `effective_version`; `retificacoes_a_vigorar` (movida) | T002, T006, T010 | `tests/integration/kit/test_ficha.py::test_versao_futura_nunca_e_aplicada`; `test_kit_de_divulgacao.py::test_retificacao_em_elaboracao_nao_aparece` |
| FR-3405 (sem acoplamento com a publicação) | as leituras movidas, sem mudança (D-002) | T002, T015 | suítes da `070`, `099` e `101` inalteradas; `tests/integration/kit/test_exportacao.py::test_o_kit_nao_grava_nada_alem_do_evento` |
| FR-3406 (conteúdo da ficha) | `periodo_de_inscricoes`, `desfechos`, `situacao_publica`, `quantidade_da_oferta`, `TIPOS_COM_RESERVA`, `vagas_do_conteudo`, `do_ato`, numeração das Retificações | T002, T006 | `test_ficha.py::test_campos_da_ficha_por_cenario`, `::test_vagas_saneadas_e_reserva_pela_regra_do_portal` |
| FR-3407 (equivalência com a vitrine e a página) | `portal/views._selecao_da_vitrine`, `portal/views._selecao` | T005 | `test_ficha.py::test_a_ficha_diz_o_que_a_vitrine_e_a_pagina_dizem` |
| FR-3408 (proveniência pela regra da `070`) | `origens`, `acrescimos` (movidos para `publicacoes/domain/origem.py`) | T002, T006 | `test_ficha.py::test_o_termino_prorrogado_vem_da_retificacao`, `::test_perfil_substituido_inteiro`, `::test_evento_substituido_inteiro`, `::test_perfil_acrescentado` |
| FR-3409 (sem inferência de curso/campus) | FR-1365 da `069`; FR-1609 da `072` | T006, T008 | `test_ficha.py::test_nome_e_localidade_literais`; `tests/unit/kit/test_textos.py::test_localidades_so_com_localidade_em_todas` |
| FR-3410 (modo) | FR-761 da `047`; FR-149 da `024` | T006 | `test_ficha.py::test_modo_por_cenario` |
| FR-3411 (impressão por campo, com identidade, sem host nem ordem) | — (D-004, D-018) | T006 | `test_ficha.py::test_impressao_igual_para_dados_iguais`, `::test_impressao_nao_inclui_instante_versao_host_nem_ordem` |
| FR-3412 e FR-3413 (textos, formas fechadas) | `avisos/domain/variaveis.py` (precedente de lista fechada) | T008 | `test_textos.py::test_formas_por_modo` |
| FR-3414 (vocabulário nas frases; valor literal apontado) | `PROIBIDAS` (`tests/portal/test_acompanhamento_pela_situacao.py`); FR-1366 da `069` | T009, T027 | `tests/test_vocabulario_do_kit.py`; `test_ficha.py::test_termo_em_valor_oficial_e_apontado` |
| FR-3415 (datas absolutas no fuso) | `shared/tempo.ZONA`; o formato de `_periodo.html` | T006, T008 | `test_textos.py::test_prazo_em_data_e_hora_absolutas` |
| FR-3416 (neutro sem inscrição) | FR-149 da `024` | T008, T009, T027 | `test_vocabulario_do_kit.py::test_modo_neutro_sem_inscricao` |
| FR-3417 (prorrogação comprovada, com hora se preciso) | `prorrogacao` (extraída da `099` sem mudança) | T002, T008 | `tests/unit/publicacoes/test_prorrogacao.py` (regressão da regra); `test_textos.py::test_prorrogacao_com_as_duas_pontas`, `::test_prorrogacao_so_de_hora` |
| FR-3418 (legenda com busca e sigla; mensagem com link) | busca por número da vitrine (`portal/leitura.py`) | T008 | `test_textos.py::test_legenda_sem_link_com_busca_e_sigla` |
| FR-3419 (ressalva) | rodapé fixo dos avisos (`avisos/domain/mensagem.py`) | T008 | `test_textos.py::test_ressalva_em_todo_texto_publicavel` |
| FR-3420 (copiar; exportar md e txt) | — | T012, T015 | `tests/javascript/kit-de-divulgacao.test.js`; `test_exportacao.py::test_md_e_txt_registram` |
| FR-3421 (notas sem promessa) | — | T008 | `test_textos.py::test_notas_sem_validade_prometida` |
| FR-3422 (um template, PNG e SVG com a fonte) | `fonte.py` (Edital Sans, OFL) | T022, T023, T025 | `tests/unit/kit/test_peca.py::test_svg_e_png_da_mesma_composicao`; `tests/unit/kit/test_svg.py::test_fonte_embutida` |
| FR-3423 (peça ⊂ ficha ⊂ textos) | — (POC, `kit/coerencia.py`) | T020, T023 | `test_peca.py::test_peca_contida_na_ficha`, `::test_peca_contida_nos_textos` |
| FR-3424 (período em destaque; selo; neutro) | — | T023 | `test_peca.py::test_destaque_por_modo` |
| FR-3425 (teto de quatro; contagem; "N vagas em K opções") | `leitura.os_primeiros`; exceção declarada à FR-1607 da `072` | T008, T023 | `test_peca.py::test_oferta_por_quantidade_de_opcoes`; `test_textos.py::test_total_sempre_com_o_numero_de_opcoes` |
| FR-3426 (ordem dos títulos; sem truncamento) | — | T023 | `test_peca.py::test_ordem_dos_titulos`, `::test_titulo_nunca_truncado` |
| FR-3427 (manchete em lista fechada) | varredura da FR-3414 | T021, T023 | `tests/unit/kit/test_manchete.py` |
| FR-3428 (24 px, AA, margem de 80 px) | contraste AA de `tests/interface/test_acessibilidade.py` | T020, T023 | `test_peca.py::test_legibilidade_minima` |
| FR-3429 (sem colisão nem palavra partida; recusa) | `diagramacao.py` (recusa fora da área útil) | T020, T023 | `test_peca.py::test_nenhuma_caixa_fora_nem_sobreposta`, `::test_palavra_partida_nao_cabe` |
| FR-3430 (caractere sem grafia; texto medido = desenhado) | `publicacoes/domain/grafia.py` | T023 | `test_peca.py::test_caractere_sem_grafia_recusa_nomeando`, `::test_texto_desenhado_e_o_normalizado` |
| FR-3431 (rodapé medido, selo) | — | T023 | `test_peca.py::test_rodape_medido_e_selo` |
| FR-3432 (marca oficial; chave de ambiente) | `AVISOS_AOS_CANDIDATOS` (`066`) | T017, T018, T033 | `tests/test_settings_do_kit.py`; `test_kit_de_divulgacao.py::test_peca_desligada_mantem_os_textos` |
| FR-3433 (texto alternativo) | — | T023 | `test_peca.py::test_texto_alternativo_em_frases_do_que_aparece` |
| FR-3434 (espaço livre: 35% da folga) | — | T023 | `test_peca.py::test_espaco_livre_distribuido` |
| FR-3435 (formatos; o que registra) | `interface/relatorio.py` (`emitir`, POST) | T015, T025, T029 | `test_exportacao.py::test_abrir_e_copiar_nao_registram`, `::test_cada_formato_registra` |
| FR-3436 (evento com detalhe; não é transição; rótulo) | `record_event`; `OPERACOES`; `OPERACOES_QUE_NAO_CONTAM` | T015, T016 | `test_exportacao.py::test_detalhe_do_evento`, `::test_o_evento_nao_e_transicao`; `tests/test_trilha_legivel.py` |
| FR-3437 (manifesto com três instantes) | — | T029 | `tests/integration/kit/test_pacote.py::test_manifesto_sem_validade` |
| FR-3438 (determinismo em dois níveis) | — | T026, T029 | `test_pacote.py::test_mesma_peca_e_textos_em_instantes_diferentes`, `::test_mesmo_zip_no_mesmo_instante`; `tests/integration/kit/test_referencias.py` |
| FR-3439 (desatualização por impressão, todas as exportações) | `APLICAR_A_TODOS` (leitura do `detalhe`) | T015 | `test_exportacao.py::test_prorrogacao_gera_a_faixa`, `::test_exportacao_antiga_continua_listada`, `::test_retificacao_de_secao_nao_gera_faixa` |
| FR-3440 (Retificação a vigorar) | `retificacoes_a_vigorar` (`101`, movida) | T015 | `test_exportacao.py::test_retificacao_a_vigorar_antes_e_depois` |
| FR-3441 (nada guardado; sem aprovação por peça) | — | T029 | `test_pacote.py::test_nenhum_arquivo_guardado` |
| FR-3442 (cabeçalhos; política do SVG) | `shared/http.marcar_como_privada` | T015, T022, T025 | `test_kit_de_divulgacao.py::test_cabecalhos_de_cada_formato`; `test_svg.py::test_politica_do_anexo` |
| FR-3443 (tela única) | moldura da `076` | T012 | `test_kit_de_divulgacao.py::test_tela_por_modo` |
| FR-3444 (CSP, acessibilidade, 375 px, teclado) | `test_politica_de_conteudo.py`, `test_acessibilidade.py`, `test_folha_estatica.py` | T012, T013, T031 | os três guardiões; a verificação pelo navegador (T031) |
| FR-3445 (desfecho depois da exportação) | `desfechos` | T015 | `test_exportacao.py::test_desfecho_depois_da_exportacao` |
| FR-3446 (impressão conferida; 409) | — (D-019) | T012, T015, T025 | `test_exportacao.py::test_edital_mudado_entre_tela_e_exportacao` |
| FR-3447 (host local sem link nem peça) | `HOSTS_LOCAIS`, `_host_local` (`interface/relatorio.py`) | T011, T025 | `test_kit_de_divulgacao.py::test_host_local_sem_link_nem_peca` |
| FR-3448 (impressão versionada) | — (D-018) | T006, T015 | `test_ficha.py::test_impressao_versionada`; `test_exportacao.py::test_impressao_de_versao_anterior` |

## Casos-limite

| Caso | Tarefas | Testes |
|---|---|---|
| EC-1 (não publicado) | T010, T011 | `test_kit_de_divulgacao.py::test_antes_da_publicacao_a_acao_e_indisponivel_com_motivo`; `tests/authorization/test_kit_de_divulgacao.py::test_nao_publicado_409` |
| EC-2 (desfecho, mesmo dentro do período) | T006, T015 | `test_ficha.py::test_modo_por_cenario[cancelado]`; `test_exportacao.py::test_desfecho_depois_da_exportacao` |
| EC-3 (período encerrado ou cancelado) | T006 | `test_ficha.py::test_modo_por_cenario[encerrado]` |
| EC-4 (Processo encerrado, Edital publicado; P-8) | T006 | `test_ficha.py::test_processo_encerrado_sem_material_enquanto_p8` |
| EC-5 (sem período designado) | T006, T008 | `test_vocabulario_do_kit.py::test_modo_neutro_sem_inscricao` |
| EC-6 (sem término) | T006, T008 | `test_textos.py::test_periodo_sem_termino` |
| EC-7 (atravessa o ano) | T006 | `test_ficha.py::test_periodo_curto_repete_o_ano_so_se_muda` |
| EC-8 (Retificação a vigorar) | T006, T015 | `test_ficha.py::test_versao_futura_nunca_e_aplicada`; `test_exportacao.py::test_retificacao_a_vigorar_antes_e_depois` |
| EC-9 (Retificação que não toca o material) | T015 | `test_exportacao.py::test_retificacao_de_secao_nao_gera_faixa` |
| EC-10 (Perfil retirado, acrescentado, renomeado, reordenado) | T015 | `test_exportacao.py::test_perfil_retirado_acrescentado_renomeado_e_reordenado` |
| EC-11 (só cadastro reserva entre Perfis com vaga) | T006, T023 | `test_ficha.py::test_total_so_com_vaga_em_todas` |
| EC-12 (opções indistintas) | T008, T023 | `test_textos.py::test_opcoes_indistintas_contam`; `test_peca.py::test_oferta_por_quantidade_de_opcoes` |
| EC-13 (título que repete o número) | T006 | `test_ficha.py::test_titulo_sem_numero` |
| EC-14 (nenhum título cabe) | T021, T023 | `test_peca.py::test_ordem_dos_titulos`; `test_manchete.py` |
| EC-15 (caractere sem grafia) | T023 | `test_peca.py::test_caractere_sem_grafia_recusa_nomeando` |
| EC-16 (endereço longo) | T023 | `test_peca.py::test_rodape_medido_e_selo` (sintético); `::test_palavra_partida_nao_cabe` |
| EC-17 (esquema antigo; Publicação sem sigla) | T006 | `test_ficha.py::test_conteudo_de_esquema_antigo`, `::test_publicacao_sem_sigla_gravada` |
| EC-18 (unidade renomeada) | T006 | `test_ficha.py::test_unidade_congelada` |
| EC-19 (vagas acrescidas não entram) | T006 | `test_ficha.py::test_vaga_acrescida_nao_entra` |
| EC-20 (sem exportação anterior) | T015 | `test_exportacao.py::test_sem_exportacao_sem_faixa` |
| EC-21 (peça desligada) | T017, T028 | `test_kit_de_divulgacao.py::test_peca_desligada_mantem_os_textos`; `test_pacote.py::test_zip_sem_peca` |
| EC-22 (sem script) | T012, T013 | `test_kit_de_divulgacao.py::test_exportacoes_por_formulario`; `kit-de-divulgacao.test.js` |
| EC-23 (60 ou mais Perfis) | T008, T023 | `test_textos.py::test_legenda_conta_acima_de_quatro`; `test_peca.py` (sintético de 66) |
| EC-24 (mesmo número em outra unidade) | T003, T008 | `test_textos.py::test_legenda_sem_link_com_busca_e_sigla`; o cenário de duas unidades da fixture |
| EC-25 (prorrogação só de hora) | T002, T008 | `tests/unit/publicacoes/test_prorrogacao.py::test_adiamento_so_da_hora_ja_e_prorrogacao`; `test_textos.py::test_prorrogacao_so_de_hora` |
| EC-26 (termo da lista em valor oficial) | T006, T009 | `test_ficha.py::test_termo_em_valor_oficial_e_apontado`; `test_vocabulario_do_kit.py::test_valor_literal_nao_reprova` |
| EC-27 (Edital mudou entre abrir e exportar) | T015 | `test_exportacao.py::test_edital_mudado_entre_tela_e_exportacao` |
| EC-28 (host local) | T011, T025 | `test_kit_de_divulgacao.py::test_host_local_sem_link_nem_peca` |

## Critérios de sucesso

| Critério | Tarefas | Verificação |
|---|---|---|
| SC-1051 (três minutos, sem o PDF) | T035 | **humana**, com a comunicação |
| SC-1052 (nada não comprovado; neutro) | T009, T020, T027 | `test_vocabulario_do_kit.py`; `test_peca.py::test_peca_contida_na_ficha` |
| SC-1053 (desatualização exata; desfecho; futuro não aplicado) | T014, T015 | `test_exportacao.py` |
| SC-1054 (template aprovado com a marca) | T030, T033, T034 | **humana**, sobre a galeria |
| SC-1055 (geometria) | T020, T023 | `test_peca.py::test_nenhuma_caixa_fora_nem_sobreposta` |
| SC-1056 (determinismo) | T024, T026, T029 | `test_pacote.py`; `test_referencias.py`; `verificacao-do-motor.md` |
| SC-1057 (2 s num lote de 20) | T024, T032 | `verificacao-do-motor.md` |
| SC-1058 (Edital real sem correção) | T035 | **humana**, com a comunicação |
