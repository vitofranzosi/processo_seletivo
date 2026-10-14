# Rastreabilidade — 071 · O piloto interno do assistente conversacional do Edital

**Frase que governa**: *o modelo só fala do que recebeu, e a aplicação só mostra o que conferiu: cada
resposta vem de uma versão, cita fontes que foram entregues naquela chamada, e nada é cortado,
trocado ou repetido sem que a tela o diga.*

Cada linha aponta o lugar do código e o que o prende. Os requisitos que só se cumprem com o serviço
real ou com pessoas — a avaliação na L4, a sessão com o setor — apontam a tarefa que os cumpre, e a
[verificação](verificacao.md) diz em que pé estão.

**Caminhos de código:**

- D = `processo_seletivo/duvidas/`
- I = `processo_seletivo/interface/`
- S = `config/settings/`

**Testes**, sob `tests/`:

| Sigla | Arquivo | Sigla | Arquivo |
|---|---|---|---|
| **UM** | `unit/duvidas/test_mascara.py` | **IP** | `integration/duvidas/test_perguntar.py` |
| **UT** | `unit/duvidas/test_tokens.py` | **IC** | `integration/duvidas/test_continuacao.py` |
| **UF** | `unit/duvidas/test_fontes.py` | **IT** | `integration/duvidas/test_teto_e_orcamento.py` |
| **UC** | `unit/duvidas/test_conferencia.py` | **IL** | `integration/duvidas/test_log_do_piloto.py` |
| **UN** | `unit/duvidas/test_mensagens.py` | **IR** | `integration/duvidas/test_limites_da_resposta.py` |
| **UO** | `unit/duvidas/test_adaptador_openrouter.py` | **IO** | `integration/duvidas/test_orcamento.py` |
| **UL** | `unit/duvidas/test_adaptador_ollama.py` | **IA** | `integration/duvidas/test_avaliar_assistente.py` |
| **UV** | `unit/duvidas/test_verificar_servico.py` | **IE** | `integration/duvidas/test_exclusao.py` |
| **TT** | `interface/test_assistente.py` | **CR** | `test_credencial_do_assistente.py` |
| **AP** | `authorization/test_papel_do_piloto.py` | **CP** | `test_configuracao_producao.py` |
| **TG** | `test_gramatica_das_portas.py` | | |

---

## 1. Requisitos funcionais

### O acesso

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **FR-1460** | I`assistente.py` (`_edital_do_piloto`: o alcance da `070` **e** a permissão, a cada requisição) | TT `test_as_ausencias_tem_a_mesma_negativa_e_nenhuma_chamada`; TG |
| **FR-1461** | I`identidade.py` (papel `participante-piloto-assistente`); D`application/perguntar.py` (`PERMISSAO`) | AP |
| **FR-1462** | I`urls.py` (só sob a gestão) | TT `test_nenhuma_rota_publica_leva_ao_piloto` |
| **FR-1463** | Procedimento: a sessão acompanhada, na máquina da equipe (quickstart C) | T065, aberta — ver a verificação |
| **FR-1464** | S`base.py` (`ASSISTENTE_PILOTO`, desligado); I`assistente.py`; I`views.py` (entrada) | TT `test_com_o_piloto_desligado_a_mesma_negativa`, `test_a_entrada_so_para_quem_participa` |

### A versão e as fontes

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **FR-1465** | D`application/perguntar.py` (uma conversa, um `edital_id`); D`domain/mensagens.py` (regra de outra seleção) | IP; TT `test_cb07_o_formulario_nao_carrega_historico`; matriz `CA-20`, `CB-06` |
| **FR-1466** | D`application/perguntar.py` (`contexto` da `070` no instante de cada pergunta) | IC `test_cb04_ca19_…`, `test_cb03_ca18_…` |
| **FR-1467** | idem (uma leitura por pergunta; `versao` e `impressao_das_fontes` na troca) | IP `test_a_resposta_conferida_e_gravada_com_as_fontes`; UF `test_o_futuro_e_fonte_a_parte_e_nao_mistura_versoes` |
| **FR-1468** | I`assistente.py` (`_aviso_de_mudanca`, pela `MudancaDeVersao` da `070`) | TT `test_a_retificacao_entre_perguntas_avisa_e_marca_a_anterior` |
| **FR-1469** | D`application/perguntar.py` (`SemVersaoVigente`, nada gravado) | IP `test_edital_sem_publicacao_nao_tem_conversa` |
| **FR-1470** | D`domain/fontes.py` (`fontes_completas`, das respostas da `070`) | UF `test_todo_texto_do_edital_e_identico_ao_publicado`, `test_nenhum_caminho_aparece_com_dois_conteudos` |
| **FR-1471** | D`infrastructure/inferencia/` (a porta só envia mensagens e recebe texto) | UO; UL |
| **FR-1472** | D`domain/fontes.py` (identificador `F1…Fn`, natureza, lugar, ato, conteúdo; toda seção textual inteira) | UF `test_os_identificadores_sao_estaveis_e_sequenciais`, `test_toda_secao_textual_preenchida_esta_inteira_nas_fontes` |
| **FR-1473** | D`domain/fontes.py` (a cobertura da `070`) | UF `test_todo_campo_mostrado_pela_070_esta_nas_fontes` |
| **FR-1474** | idem (só o que a `070` dá como texto entra como texto) | UF `test_todo_texto_do_edital_e_identico_ao_publicado` |
| **FR-1475** | D`domain/fontes.py` (`CALCULADA`: situação, desfecho, futuro com `altera`, documentos por Perfil e lista) | UF `test_o_futuro_e_fonte_a_parte_e_nao_mistura_versoes`, `test_a_obrigatoriedade_e_calculada_por_perfil_e_lista` |
| **FR-1476** | idem (anexo pelo rótulo e pelo vínculo, `anexo=True`) | UC `test_divergencia_com_duas_fontes_e_anexo_com_fonte_de_anexo_passam` |
| **FR-1477** | D`domain/mensagens.py` (instruções no sistema, fontes como dado, uma linha JSON por fonte) | UN `test_cada_fonte_e_uma_linha_json_e_o_conteudo_nao_forja_outra`; IR `test_ca25_…` |
| **FR-1478** | Não implementada, por decisão: a seleção de fontes só existe depois da necessidade medida (`D-002`) | UF `test_a_montagem_do_maior_edital_e_rapida`; a medição da L4 (T060) |

### O orçamento de contexto

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **FR-1479** | D`infrastructure/tokens.py`; D`domain/mensagens.py` (`orcamento_de_entrada`) | UT; UN `test_o_orcamento_desconta_a_saida_e_a_margem`; IP `test_sem_tokenizer_nao_ha_chamada` |
| **FR-1480** | S`base.py` (`ASSISTENTE_CONTEXTO_TOKENS`); D`infrastructure/inferencia/ollama.py` (`num_ctx`) | UL `test_o_corpo_leva_o_contexto_e_os_parametros`; UV `test_contexto_menor_que_o_configurado_diverge` |
| **FR-1481** | D`application/perguntar.py` (o turno mais antigo sai primeiro; `EXCEDE_O_CONTEXTO`); I`assistente.py` (`_historico_reduzido`) | IO `test_o_historico_mais_antigo_sai_primeiro`, `test_sem_caber_nem_sem_historico_nao_ha_chamada`; TT `test_a_tela_diz_quando_o_historico_foi_reduzido` |
| **FR-1482** | D`application/perguntar.py` (`POSSIVEL_CORTE`); D`infrastructure/inferencia/ollama.py` (`truncate`/`shift` por configuração) | IO `test_o_servico_que_leu_menos_acusa_corte`, `test_dentro_da_tolerancia_nao_acusa`, `test_ler_mais_que_o_medido_nao_descarta`; UL `test_sem_corte_so_quando_configurado` |
| **FR-1483** | D`application/perguntar.py` (`INCOMPLETA`) | IO `test_a_resposta_encerrada_por_limite_e_incompleta`; UL `test_o_limite_de_saida_volta_como_termino` |
| **FR-1484** | D`application/perguntar.py` (`PERGUNTA_RECUSADA`); I`templates/interface/assistente.html` (`maxlength`, ajuda) | TT `test_cada_estado_tem_texto_e_alternativas` |

### A resposta e a conferência

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **FR-1485** | D`domain/mensagens.py` (`ESQUEMA_DA_SAIDA`); adaptadores (`format`, `json_schema` estrito) | UC `test_cada_defeito_recusa`; UO `test_o_corpo_e_explicito_e_sem_troca`; UL |
| **FR-1486** | D`domain/estruturas_do_piloto.py` (`TIPOS`, `ROTULO_DO_TIPO_NO_PILOTO`); I`assistente.py` (`CAMINHO_OFICIAL`) | UC `test_o_tipo_exige_as_fontes_que_ele_supoe`; TT |
| **FR-1487** | D`domain/conferencia.py` (`conferir`: forma, fonte inexistente, citação, valor, tipo, negativa) | UC `test_cada_defeito_recusa`, `test_saidas_certas_passam`, `test_negativa_declarada_numa_fonte_citada_passa` |
| **FR-1488** | D`application/perguntar.py` (`NAO_PASSOU_NA_CONFERENCIA`, nenhuma chamada nova); I`assistente.py` | IP `test_a_saida_invalida_nao_vira_resposta`; TT `test_a_recusa_da_conferencia_aparece_no_lugar_da_resposta` |
| **FR-1489** | D`application/perguntar.py` (`fontes_citadas` montadas da fonte, e não do modelo); o template | IP `test_a_resposta_conferida_e_gravada_com_as_fontes` |
| **FR-1490** | D`application/perguntar.py` (`avisos_da_aplicacao`) | IR `test_fr1490_a_aplicacao_acrescenta_o_futuro_da_fonte_citada`, `test_ca29_o_desfecho_vem_da_aplicacao` |
| **FR-1491** | D`domain/mensagens.py` (as instruções); I`assistente.py` (`DECISAO_NAO_TOMADA` com o caminho oficial) | Revisão humana (`FR-1513`); matriz `CA-22`, `CA-23`, `CA-26` |
| **FR-1492** | O template (texto escapado); D`application/perguntar.py` (o raciocínio descartado) | TT `test_o_texto_do_modelo_sai_escapado`; IP `test_o_raciocinio_nao_vai_a_troca` |
| **FR-1493** | I`assistente.py` (o canal da `070` em todo turno) | IR `test_dois_canais_divergentes_pedem_as_duas_fontes`, `test_cb08_…` |

### A conversa

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **FR-1494** | D`application/perguntar.py` (`historico_permitido`, da tabela); I`assistente.py` (a sessão só guarda o identificador) | TT `test_cb07_o_formulario_nao_carrega_historico`; IC `test_cb01_…` |
| **FR-1495** | `historico_permitido` (mesma versão, só conferidas, sem fontes) | IC `test_cb04_ca19_…`, `test_cb03_ca18_…`, `test_o_turno_recusado_nao_entra_no_historico` |
| **FR-1496** | D`application/limites.py` (`LIMITE_DE_USO`); I`assistente.py` (`nova_conversa`) | IT `test_o_limite_da_conversa`; TT `test_o_limite_da_conversa_na_tela`, `test_comecar_outra_conversa_zera_o_historico` |

### O serviço

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **FR-1497** | D`infrastructure/inferencia/__init__.py` (a porta, um serviço por configuração); S`base.py` | UO; UL; CP |
| **FR-1498** | `parametros_configurados`; os dois adaptadores (todo parâmetro explícito, `require_parameters`) | UO `test_o_corpo_e_explicito_e_sem_troca`; UL `test_o_corpo_leva_o_contexto_e_os_parametros` |
| **FR-1499** | D`infrastructure/inferencia/` (nenhum caminho entre os adaptadores; `allow_fallbacks: false`); D`application/perguntar.py` (`MODELO_DIFERENTE`) | UL `test_fora_do_ar_e_indisponivel_e_nada_sai_para_outro_endereco`; UO; IT `test_outro_modelo_respondeu` |
| **FR-1500** | S`base.py` (90 s); S`production.py` (≤ 110 s) | CP `test_configuracao_insegura_impede_a_inicializacao`; UO `test_cada_falha_e_um_codigo_e_uma_chamada` |
| **FR-1501** | D`domain/estruturas_do_piloto.py` (14 estados); I`assistente.py` (`TEXTO_DO_ESTADO`) | IT `test_cada_falha_e_um_estado_e_uma_chamada`; TT `test_cada_estado_tem_texto_e_alternativas` |
| **FR-1502** | S`base.py` (só do ambiente); a mensagem de erro composta sem cabeçalho; o relatório sem configuração de credencial | CR `test_a_credencial_nao_vaza`; IA `test_a_rodada_escreve_os_tres_arquivos` |
| **FR-1503** | D`application/perguntar.py` (o padrão pessoal recusado no externo); OpenRouter `data_collection: deny`, `zdr`; a faixa da tela | IT `test_cb11_…`, `test_no_servico_local_o_dado_pessoal_e_mascarado_e_sai`; TT `test_dado_pessoal_com_servico_externo_na_tela`, `test_as_faixas_do_piloto_e_do_servico_externo` |
| **FR-1504** | Dois adaptadores de algumas dezenas de linhas, e nenhum registro de provedores | UO; UL |
| **FR-1505** | Nenhuma retentativa; POST, redirecionamento, GET | UO, UL (uma chamada por falha); TT `test_o_post_redireciona_e_recarregar_nao_chama_de_novo` |
| **FR-1506** | D`application/limites.py` (`vaga_do_assistente`, travas consultivas) | IT `test_sem_vaga_no_teto_nao_ha_chamada`, `test_a_vaga_e_solta_depois_da_chamada` |
| **FR-1507** | D`application/limites.py` (só o limite da conversa); o limite de gasto na credencial, conferido por D`management/commands/verificar_servico_de_inferencia.py`; o 402 como `ORCAMENTO_ESGOTADO`; a rodada para na recusa (emenda de 14/10) | IT `test_o_limite_da_conversa`, `test_a_aplicacao_nao_conta_chamadas_externas`, `test_cada_falha_e_um_estado_e_uma_chamada`; IA `test_a_recusa_pelo_limite_de_gasto_para_a_rodada`; UO `test_cada_falha_e_um_codigo_e_uma_chamada`; UV `test_a_chave_sem_limite_de_gasto_diverge_e_nada_sai`, `test_com_limite_de_gasto_a_conversa_sintetica_sai` |

### O registro

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **FR-1508** | D`application/perguntar.py` (`_registrar`, uma linha sem texto) | IL `test_a_linha_tem_os_campos_e_nenhum_texto` |
| **FR-1509** | D`models.py` (`TrocaDoPiloto`, sem coluna de pessoa); D`domain/mascara.py`; D`management/commands/excluir_registros_do_piloto.py` | IP `test_a_troca_nao_guarda_quem_perguntou`, `test_a_pergunta_e_gravada_mascarada`; UM; IE |
| **FR-1510** | D`models.py` (as colunas do data-model, e só elas); o `rodada.json` sem tokens, tempo nem custo | IP `test_a_resposta_conferida_e_gravada_com_as_fontes`; IA `test_a_rodada_escreve_os_tres_arquivos` |

### A avaliação

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **FR-1511** | Resultado 1: a suíte; resultado 2: `avaliar_assistente` e a revisão; resultado 3: `scripts/carga_do_assistente.py` | A suíte; IA; T059 e T060, abertas |
| **FR-1512** | D`avaliacao/matriz.json` (93 casos; as doze da `070` com um Perfil por Edital) | IA (a rodada pela matriz); a rodada seca de 13/10, na verificação |
| **FR-1513** | O `revisao.csv` com as colunas do julgamento e da omissão | IA `test_a_rodada_escreve_os_tres_arquivos`; T059, aberta |
| **FR-1514** | idem (`origem_da_falha`) | IA; T059, aberta |
| **FR-1515** | A troca guarda a impressão e a versão das instruções; `--rodada-anterior` marca "outra versão da fonte" | UN `test_a_impressao_muda_com_a_fonte_e_so_com_ela`; IA `test_a_rodada_anterior_marca_a_outra_versao_da_fonte` |
| **FR-1516** | O `rodada.json` e o `resumo.md` levam o serviço, o modelo e a quantização; o resumo diz que só o Ollama da L4 conta | IA; T059, aberta |
| **FR-1517** | `scripts/carga_do_assistente.py` (1, 2 e 4 simultâneas; a carga pública lado a lado) | T060, aberta; o script verificado sem L4 (verificação) |
| **FR-1518** | O relatório datado das medições | T060, aberta |
| **FR-1519** | `sem_rede` em todo caso do pacote; a porta sem configuração levanta `NAO_CONFIGURADO` | UO `test_sem_configuracao_nenhum_pedido_sai`; `tests/fixtures/inferencia.py` (`sem_rede`) |

### A conexão com o Ollama

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **FR-1520** | D`management/commands/verificar_servico_de_inferencia.py` | UV |
| **FR-1521** | D`application/perguntar.py` (`MODELO_DIFERENTE` a cada pergunta); a verificação antes de cada rodada e sessão (DP-7 b) | IT `test_outro_modelo_respondeu`; UV `test_a_quantizacao_diferente_diverge`, `test_o_modelo_parcialmente_na_cpu_diverge`; T058, aberta |

## 2. Critérios de sucesso

| Identificador | Onde se verifica |
|---|---|
| **SC-545** | UF `test_todo_campo_mostrado_pela_070_esta_nas_fontes`, `test_toda_secao_textual_preenchida_esta_inteira_nas_fontes` |
| **SC-546** | UC `test_cada_defeito_recusa` |
| **SC-547** | IO; UL `test_o_limite_de_saida_volta_como_termino` |
| **SC-548** | IT `test_cada_falha_e_um_estado_e_uma_chamada`, `test_outro_modelo_respondeu`; UL `test_fora_do_ar_e_indisponivel_e_nada_sai_para_outro_endereco` |
| **SC-549** | CR `test_a_credencial_nao_vaza`; IA (os três arquivos) |
| **SC-550** | IC `test_cb04_ca19_…`, `test_cb03_ca18_…`; UF `test_o_futuro_e_fonte_a_parte_e_nao_mistura_versoes` |
| **SC-551 a SC-555** | A rodada no Ollama da L4 e a revisão humana (T059), contra os critérios da DP-3 — abertas |
| **SC-556 a SC-558** | As medições na L4 (T060) — abertas; o orçamento de latência é proposto pela medição e aprovado na DP-3 |
| **SC-559** | A sessão acompanhada com o setor (T065) — aberta |
| **SC-560** | UO `test_cada_falha_e_um_codigo_e_uma_chamada` (o 402); IA `test_a_recusa_pelo_limite_de_gasto_para_a_rodada`; UV `test_a_chave_sem_limite_de_gasto_diverge_e_nada_sai` |

## 3. Experiência

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **UX-210** | I`templates/interface/assistente.html` (`.piloto`) | TT `test_as_faixas_do_piloto_e_do_servico_externo` |
| **UX-211** | idem (a faixa do serviço externo) | TT `test_as_faixas_do_piloto_e_do_servico_externo` |
| **UX-212** | idem (a versão no topo do turno, o aviso antes, o tipo em palavras) | TT `test_a_retificacao_entre_perguntas_avisa_e_marca_a_anterior` |
| **UX-213** | idem (`.natureza`, os rótulos de `ROTULO_DO_TRECHO`) | TT `test_a_recusa_da_conferencia_aparece_no_lugar_da_resposta`; `interface/test_acessibilidade.py` |
| **UX-214** | I`assistente.py` (`TEXTO_DO_ESTADO`, as fontes e o canal como alternativa) | TT `test_cada_estado_tem_texto_e_alternativas` |
| **UX-215** | idem (formulário nativo, `aria-live`, foco por âncora, sem largura fixa) | TT; `interface/test_acessibilidade.py`; a verificação a 375 px no navegador |
| **UX-216** | idem (os turnos anteriores com a versão e a marca "versão anterior") | TT `test_a_retificacao_entre_perguntas_avisa_e_marca_a_anterior` |
