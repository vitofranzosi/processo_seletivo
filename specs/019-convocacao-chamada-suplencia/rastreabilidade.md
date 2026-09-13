# Rastreabilidade — `019` Convocação, Chamada e Suplência

Cada requisito com o teste que o prende. A matriz é o que o Princípio V exige e o que impede a spec
de virar prosa: um requisito sem linha aqui é um requisito que ninguém verificou.

**Os caminhos são relativos a `backend/`.** Onde o teste mora em arquivo diferente do que o
`tasks.md` previu, a razão está na coluna — quase sempre a mesma: recusa de camada de aplicação
precisa de banco, e o repositório põe isso em `integration/`.

---

## Requisitos funcionais

| Requisito | O que ele exige | Teste que o prende |
|---|---|---|
| `FR-264` | registrar a convocação fundada na ordem e na faixa vigentes | `tests/integration/convocacao/test_recusas.py::TestADuplicidade` |
| `FR-265` | recusar fora da faixa; sem ordem vigente | `tests/integration/convocacao/test_recusas.py::TestAOrdem` |
| `FR-266` | recusar sem apuração e com apuração obsoleta, nomeando a causa | `tests/integration/convocacao/test_recusas.py::TestAApuracao` |
| `FR-267` | respeitar a ordem, salvo fundamento registrado no ato | `tests/integration/convocacao/test_recusas.py::TestAOrdem::test_precedencia_na_ordem_recusa_e_diz_quantos_estao_antes` |
| `FR-268` | uma convocação vigente por pessoa e recorte | `tests/integration/convocacao/test_recusas.py::TestADuplicidade::test_convocacao_vigente_existente_recusa` |
| `FR-269` | vencimento explícito informado, sem calendário | `tests/unit/convocacao/test_prazo.py` |
| `FR-269a` | falha de envio não inicia prazo nem desfaz o ato | `tests/integration/convocacao/test_comunicacao.py::TestAFalhaNaoDesfazOAto` |
| `FR-269b` | vencimento posterior ao envio | `tests/integration/convocacao/test_comunicacao.py::TestOPrazoCorreDoEnvio::test_vencimento_anterior_ao_envio_e_recusado` |
| `FR-270` | cada convocação alcança uma vaga; não move quantidade entre recortes | `tests/test_dependencia_da_convocacao.py::TestNenhumCaminhoMoveQuantidadeEntreRecortes` |
| `FR-271` | permissão explícita, escopo, ator, instante, fundamento e correlação | `tests/integration/convocacao/test_autorizacao.py` |
| `FR-272` | correção é sucessão | `tests/integration/convocacao/test_recusas.py::TestADuplicidade::test_com_motivo_a_segunda_sucede_a_primeira_sem_tocar_nela` |
| `FR-273` | um desfecho por convocação, entre os sete nomeados | `tests/integration/convocacao/test_ciclo_do_77.py::test_o_desfecho_nao_se_repete_e_a_correcao_e_sucessao` |
| `FR-274` | o decurso é observável e **não** produz desfecho | `tests/unit/convocacao/test_prazo.py::TestODecursoNaoProduzDesfecho`; `tests/unit/convocacao/test_atestado.py::TestODecursoNaoCancelaNada` |
| `FR-275` | desfecho que não ocupa libera a vaga no mesmo recorte | `tests/integration/convocacao/test_suplencia.py::test_a_desistencia_na_reservada_abre_vaga_na_mesma_lista` |
| `FR-276` | a liberação torna a apuração vigente obsoleta | `tests/integration/ocupacao/test_obsolescencia.py::test_o_efeito_posterior_obsoleta_a_apuracao` |
| `FR-277` | fato externo registrado como atestado, nunca inferido | `tests/unit/convocacao/test_atestado.py::TestAInerciaExigeAtestadoPorForma` |
| `FR-278` | o desfecho exclui na emissão seguinte, sem alterar a apuração emitida | `tests/integration/convocacao/test_ciclo_do_77.py::test_a_desistencia_registrada_nao_reescreve_a_apuracao_anterior` |
| `FR-278a` | não afirmar número diferente do apurado até a emissão nova | `tests/interface/test_convocacao.py::test_a_tela_nao_afirma_numero_de_ocupacao_diferente_do_apurado` |
| `FR-278b` | aceite e regularização **incluem** | `tests/unit/ocupacao/test_titulares.py::TestOCicloQueACC093Mede::test_a_suplente_aceita_e_o_numero_volta` |
| `FR-278c` | o efeito entra pela porta que a `016` define | `tests/test_dependencia_da_convocacao.py::test_a_porta_guarda_o_ato_de_origem_como_identidade_opaca` |
| `FR-278d` | exclusão de quem não era titular não desconta | `tests/unit/ocupacao/test_titulares.py::TestExclusaoDeQuemNaoEraTitular` |
| `FR-279` | indicar o próximo da ordem do mesmo recorte | `tests/unit/convocacao/test_fila.py::TestOEsgotamentoDaListaAlcancada` |
| `FR-280` | a chamada não atravessa recorte | `tests/unit/convocacao/test_fila.py::TestASuplenciaNaoAtravessaRecorte`; `tests/integration/convocacao/test_suplencia.py` |
| `FR-281` | respeitar o teto da faixa; dizer o esgotamento; não emitir faixa | `tests/integration/convocacao/test_recusas.py::TestODeficit::test_esgotada_a_fila_a_recusa_nomeia_o_esgotamento`; `tests/interface/test_convocacao.py::TestOsEstadosDistintos::test_a_fila_esgotada_nao_oferece_botao_que_esta_feature_nao_cumpre` |
| `FR-282` | Retificação, apuração e faixa não desfazem convocação praticada | `tests/integration/convocacao/test_ato_praticado.py` |
| `FR-283` | o reclassificado vai para o fim e não é chamável antes do esgotamento | `tests/unit/convocacao/test_reclassificacao.py` |
| `FR-284` | convocar para regularizar, na ordem, com fundamento | `tests/integration/convocacao/test_regularizacao.py::test_a_convocacao_para_regularizar_respeita_a_ordem_de_classificacao` |
| `FR-285` | a regularização ocupa sem reabrir a ordem | `tests/integration/convocacao/test_regularizacao.py::test_o_ciclo_da_regularizacao_ocupa_a_vaga_sem_reabrir_a_ordem` |
| `FR-286` | Resultado sucessor pelo mecanismo da `018`, com fonte própria | `tests/integration/resultados/test_origem_regularizacao.py` |
| `FR-286a` | a inércia é ato próprio e não supera Resultado | `tests/unit/convocacao/test_atestado.py::TestODecursoNaoCancelaNada::test_a_inercia_nao_se_mede_pelo_vencimento_da_convocacao` |
| `FR-287` | a forma de comunicar é declarada; ausência não é padrão | `tests/integration/convocacao/test_comunicacao.py::TestAFormaDeclarada::test_sem_declaracao_a_emissao_e_recusada`; `tests/contract/test_elevacao_degrau_15.py` |
| `FR-288` | emissão registrada com instante, destinatário e resultado | `tests/integration/convocacao/test_comunicacao.py::TestAFormaDeclarada` |
| `FR-288a` | nenhuma superfície afirma recebimento | `tests/test_vocabulario_da_convocacao.py`; `tests/integration/convocacao/test_comunicacao.py::test_nenhum_campo_da_comunicacao_afirma_recebimento` |
| `FR-288b` | o acesso do candidato é registrado sem mover o relógio | `tests/interface/test_portal_convocacao.py::test_ler_a_convocacao_nao_move_o_relogio` |
| `FR-289` | a mensagem individual depende da revisão da `FR-084` da `010` | `tests/test_situacoes_de_mensagem.py` |
| `FR-290` | a mensagem carrega o mínimo | `tests/unit/convocacao/test_mensagem.py` |
| `FR-291` | convocação, reclassificação, desistência e inércia não são objetos recursais | `tests/unit/convocacao/test_reclassificacao.py::TestAReclassificacaoNaoAfirmaPerdaDeHabilitacao` |
| `FR-292` | o deferimento governa o próximo ato enquanto não há convocação praticada | `tests/unit/convocacao/test_fila.py::TestOReabilitadoPorDeferimento` |
| `FR-292a` | o deferimento não desfaz convocação nem cancela matrícula | `tests/integration/convocacao/test_ato_praticado.py::test_o_deferimento_nao_desfaz_convocacao_praticada_nem_cancela_matricula` |
| `FR-292b` | o reabilitado fica em primeiro e bloqueia quem está abaixo | `tests/unit/convocacao/test_fila.py::TestOReabilitadoPorDeferimento::test_o_reabilitado_bloqueia_quem_esta_abaixo` |
| `FR-292c` | nenhuma superfície diz *"direito à vaga"* | `tests/test_vocabulario_da_convocacao.py`; `tests/unit/convocacao/test_mensagem.py::TestOQueAMensagemNaoDiz` |
| `FR-293` | a leitura mostra convocados, respondidos, faltantes e esgotamento | `tests/interface/test_convocacao.py::TestOsEstadosDistintos` |
| `FR-294` | distinguir *"nenhuma convocação"* de *"zero convocados"* | `tests/interface/test_portal_convocacao.py::TestAsDuasAusencias` |
| `FR-295` | o histórico reconstrói cada convocação com a proveniência | `tests/interface/test_convocacao.py::test_o_historico_mostra_a_reclassificacao_com_fundamento_e_posicao_nova` |
| `FR-296` | cada ato consta da trilha do Edital, em linguagem humana | `tests/interface/test_convocacao.py::test_a_trilha_do_edital_lista_os_atos_da_019_em_linguagem_humana` |

## Critérios de sucesso

| Critério | Teste |
|---|---|
| `SC-085` | `tests/integration/convocacao/test_ciclo_do_77.py::test_o_ciclo_inteiro_do_77` |
| `SC-086` | `tests/integration/convocacao/test_suplencia.py::test_a_fila_da_lista_reservada_so_tem_quem_concorre_nela` |
| `SC-087` | `tests/interface/test_convocacao.py::TestOsEstadosDistintos::test_a_fila_esgotada_nao_oferece_botao_que_esta_feature_nao_cumpre` |
| `SC-088` | `tests/performance/test_convocacao.py::test_o_historico_responde_por_conjunto` |
| `SC-089` | `tests/integration/ocupacao/test_obsolescencia.py::test_o_efeito_posterior_obsoleta_a_apuracao` |
| `SC-090` | `tests/performance/test_convocacao.py` |
| `SC-091` | `tests/interface/test_portal_convocacao.py::TestAConvocacaoDaPropriaPessoa` |
| `SC-092` | `tests/test_vocabulario_da_convocacao.py` |
| `SC-093` | `tests/unit/ocupacao/test_titulares.py::TestOCicloQueACC093Mede` |
| `SC-094` | `tests/unit/ocupacao/test_titulares.py::TestNinguemAparecComoOcupanteSemAtoQueOSustente` |

## Requisitos de interface

| Requisito | Teste |
|---|---|
| `UX-035` | `tests/test_vocabulario_da_convocacao.py::test_a_tela_da_019_nao_calcula_o_numero_que_exibe` |
| `UX-036` | `tests/interface/test_convocacao.py::TestAConfirmacaoAntesDoAtoIrreversivel` |
| `UX-037` | `tests/interface/test_convocacao.py::TestOsEstadosDistintos::test_a_fila_esgotada_nao_oferece_botao_que_esta_feature_nao_cumpre` |
| `UX-038` | `tests/interface/test_convocacao.py::TestOsEstadosDistintos::test_o_prazo_sai_em_data_e_hora_locais_dizendo_de_onde_corre` |
| `UX-039` | `tests/test_vocabulario_da_convocacao.py`; `tests/interface/test_portal_convocacao.py` |

---

## O que esta entrega deixou aberto

**A inércia depois de um aceite já registrado não tem caminho.** A `FR-273` admite um desfecho por
convocação, e a `§6` da spec diz que o cancelamento por inércia *"alcança quem já ocupava e
desapareceu"*. As duas convivem no percurso implementado — a titular ocupa desde a apuração, é
chamada, a matrícula acontece fora daqui, e a chamada só recebe desfecho quando alguém conclui, com
aceite **ou** com inércia. Não convivem quando o aceite já foi registrado: ali a chamada está
fechada, e a inércia posterior seria o segundo desfecho da mesma convocação.

Resolvê-lo é decisão de domínio, e não de implementação: suceder a convocação com motivo mostraria a
pessoa como chamada de novo, e admitir dois desfechos contrariaria a `FR-273`. A lacuna está presa
por teste em
`tests/integration/convocacao/test_inercia.py::test_a_inercia_depois_de_um_aceite_registrado_ainda_nao_tem_caminho`,
para que o dia em que ela for decidida seja um teste que falha, e não um caso descoberto em produção.
