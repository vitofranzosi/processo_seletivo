# Rastreabilidade: Publicação e homologação das inscrições

Caminhos relativos a `backend/`. Testes de integração rodam contra PostgreSQL.

| Requisito | Implementação | Verificação |
|---|---|---|
| FR-5400, FR-5401 | `divulgacao/models.py` (`PublicacaoDasInscricoes`, três naturezas); nenhum leitor existente o exige | `tests/integration/divulgacao/test_publicacao_das_inscricoes.py`; suíte completa sem regressão |
| FR-5402 | `divulgacao/application/inscricoes.py::aferir` (`recusa_por_inscricoes_em_curso`) | `test_periodo_em_curso_e_recusado_dizendo_ate_quando` |
| FR-5403, FR-5404 | `aferir`, `_enviadas` (só `SUBMETIDA`) | `test_edital_sem_inscricao_enviada_e_recusado`, `test_a_relacao_de_recebidas_congela_conteudo_linhas_e_documento` |
| FR-5405 | `dominio.regride`; gatilho `publicacao_das_inscricoes_coerente` | `test_a_natureza_nao_regride_nem_pela_aplicacao_nem_pelo_banco`, `test_a_ordem_das_naturezas_nao_regride` |
| FR-5406 | `uq_publicacao_das_inscricoes_raiz`, `uq_publicacao_das_inscricoes_sucessor` | `test_mesma_natureza_e_correcao_e_exige_motivo`, `test_a_mesma_chave_devolve_o_mesmo_ato_e_a_previa_obsoleta_e_recusada` |
| FR-5407 | `publicar_inscricoes` (`inscricoes_motivo_obrigatorio`) | `test_mesma_natureza_e_correcao_e_exige_motivo` |
| FR-5408, FR-5409 | `dominio.etapas_de_analise`, `_etapa_escolhida`, `etapa_da_cadeia` | `test_so_etapa_decisoria_e_eliminatoria_e_analise`, `test_o_preliminar_nomeia_deferidas_conta_indeferidas_e_congela_o_prazo` |
| FR-5410, FR-5411 | `dominio.projetar` (resultado vigente; pendentes) | `test_o_preliminar_le_o_resultado_e_so_conta_a_indeferida`, `test_o_preliminar_espera_a_analise_inteira` |
| FR-5412 | `_etapa_escolhida` (sem análise só sem Etapa decisória) | `test_sem_etapa_decisoria_a_homologacao_contempla_todas`, `test_com_etapa_decisoria_a_homologacao_espera_a_analise` |
| FR-5413, FR-5414 | `_prazo`, `dominio.eventos_de_recurso` | `test_o_preliminar_exige_o_prazo_e_recusa_evento_vencido`, `test_evento_de_recurso_so_com_termino_por_vir` |
| FR-5415 | `resultados/application/selectors.py::resultados_visiveis` (+ `_etapas_das_publicacoes_das_inscricoes`) | `tests/integration/divulgacao/test_jornada_das_inscricoes.py::test_antes_do_preliminar_o_indeferido_nao_ve_nem_recorre`, `test_a_jornada_inteira_do_indeferimento_a_homologacao` |
| FR-5416, FR-5417 | `recursos/application/interpor.py::_janela_da_publicacao_das_inscricoes` | `test_a_jornada_inteira_do_indeferimento_a_homologacao`, `test_preliminar_sem_recurso_nega_a_interposicao`, `test_homologacao_direta_e_definitiva` |
| FR-5418 | `_disputa_em_aberto`; `recursos/application/selectors.py::recursos_pendentes_da_etapa` | `test_a_jornada_inteira_do_indeferimento_a_homologacao` |
| FR-5419 a FR-5422 | `dominio.projetar`, `dominio.conteudo_publico`, `dominio.chave_de_ordem` | `test_o_conteudo_publico_tem_so_protocolo_e_nome`, `test_a_ordem_ignora_caixa_e_acento_e_desempata_pelo_protocolo`, `test_a_pagina_publica_mostra_quem_consta_e_nenhum_dado_pessoal` |
| FR-5423, FR-5424 | `publicar_inscricoes`; `divulgacao/infrastructure/documento_das_inscricoes.py` | `test_a_relacao_de_recebidas_congela_conteudo_linhas_e_documento`, `test_o_documento_nao_carrega_cpf_nem_email`, `test_o_pdf_sai_dos_bytes_gravados` |
| FR-5425 | `save`/`delete`; gatilhos da `divulgacao/0005`; `seguranca/papeis.py` | `test_o_ato_e_append_only_na_aplicacao_e_no_banco`; `tests/integration/test_database_permissions.py` (parametrizado) |
| FR-5426 | colunas de signatário e unidade; `contexto_do_ato` | `test_a_relacao_de_recebidas_congela_conteudo_linhas_e_documento` |
| FR-5427 | `divergencia_do_vigente`, `dominio.divergencia` | `test_a_divergencia_conta_novas_saidas_e_mudancas`, `test_resultado_corrigido_depois_da_homologacao_aparece_como_divergencia`, `test_a_divergencia_do_vigente_aparece_e_a_correcao_pede_motivo` |
| FR-5428 | `portal/views.py::publicacao_das_inscricoes`, `_inscricoes_publicadas`; `portal/publicacao_das_inscricoes.html`, `selecao.html` | `tests/portal/test_publicacao_das_inscricoes.py` |
| FR-5429 | `require_permission("resultado:publicar")`; `_edital_para_publicar(consulta=True)` | `test_sem_capacidade_e_403_e_fora_do_escopo_e_404`, `test_a_auditoria_consulta_e_nao_publica`, `test_quem_nao_divulga_nao_abre_e_outra_unidade_nao_encontra` |
| FR-5430 | trava do Processo, `reserve`/`finish`, `assinatura_da_previa` | `test_a_mesma_chave_devolve_o_mesmo_ato_e_a_previa_obsoleta_e_recusada`, `test_a_previa_obsoleta_volta_com_409_e_nada_e_gravado` |
| FR-5431 | `auditar` com narrativa sem dado pessoal | revisão do código (`_narrativa`) |
| FR-5432, FR-5433 | `interface/inscricoes_publicadas.py`; `interface/publicacoes_das_inscricoes.html` | `tests/interface/test_publicacoes_das_inscricoes.py` |
| FR-5434 a FR-5436 | `portal/situacao.py` (`_nao_aceita_na_analise`, `_publicada`); `portal/views.py::_inscricao_publicada` | `test_o_candidato_le_que_a_inscricao_foi_recebida_e_o_que_isso_nao_quer_dizer`, `test_o_indeferido_le_que_nao_foi_aceito_ve_o_parecer_e_pode_recorrer`, `test_homologada_le_aceita_e_que_isso_nao_e_classificacao` |
| FR-5437 | migration só cria tabelas | `tests/migrations/test_migrations.py`; `test_a_inscricao_enviada_continua_imutavel_depois_do_ato`; suíte completa |
| FR-5438 | nenhuma mudança em `sorteios/` | `test_a_homologacao_e_a_relacao_do_sorteio_leem_a_mesma_fonte`; suíte do sorteio sem regressão |
| UX-460 | tela única; link nas ações do Edital e na tela de Inscrições | `test_o_edital_oferece_o_caminho_a_quem_publica`, `test_o_publicador_ve_a_previa_e_publica_pela_tela` |
| UX-461, UX-462 | rótulos de `dominio.ROTULOS`; frase da tela e `frase_da_natureza` | `test_a_pagina_publica_mostra_quem_consta_e_nenhum_dado_pessoal`; [verificacao.md](verificacao.md) |
| UX-463 | frases de `portal/situacao.py` | testes de situação do portal, com a varredura de vocabulário da 063 |
| UX-464, UX-465 | classes da página do resultado; `telas/publicacoes-das-inscricoes.css` | [verificacao.md](verificacao.md) (375 px); guardiões de estáticos e de CSP da suíte |
| SC-1700 | tela da gestão de ponta a ponta | [verificacao.md](verificacao.md) |
| SC-1701 | nenhum leitor exige o ato | suíte completa sem regressão |
| SC-1702 | fronteira pública por construção | `test_o_conteudo_publico_tem_so_protocolo_e_nome`, `test_o_documento_nao_carrega_cpf_nem_email` |
| SC-1703 | três camadas | `test_o_ato_e_append_only_na_aplicacao_e_no_banco` |
| SC-1704 | visibilidade e janela | `test_a_jornada_inteira_do_indeferimento_a_homologacao`, `test_o_indeferido_le_que_nao_foi_aceito_ve_o_parecer_e_pode_recorrer` |
| SC-1705 | bytes preservados | `test_a_jornada_inteira_do_indeferimento_a_homologacao` |
| SC-1706 | mesma fonte | `test_a_homologacao_e_a_relacao_do_sorteio_leem_a_mesma_fonte` |
| SC-1707 | idempotência e prévia | `test_a_mesma_chave_devolve_o_mesmo_ato_e_a_previa_obsoleta_e_recusada` |
| SC-1708 | 375 px e CSP | [verificacao.md](verificacao.md); `test_a_pagina_publica_mostra_quem_consta_e_nenhum_dado_pessoal` |
