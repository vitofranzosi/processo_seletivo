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

## O que a revisão de código corrigiu

Oito achados bloqueantes e quatro adicionais entraram depois da primeira implementação. Os que
mudaram **regra**, e não só código:

| Achado | O que estava errado | Onde ficou preso |
|---|---|---|
| a promoção silenciosa sobrevivia | a janela de titulares era recortada **depois** de filtrar as habilitadas, de modo que três eliminados dentro do alvo promoviam os três seguintes sem ato — `(40, 40, 40)` onde a `R-001` manda `37` | `tests/unit/ocupacao/test_titulares.py::TestNadaMudaOndeNaoHaDesfecho` |
| `PUBLICACAO` não publicava nada | a emissão por publicação gravava `ENVIADA` sem artefato nenhum, e o prazo do 69/2026 começava a correr para uma convocação que ninguém viu | `tests/integration/convocacao/test_comunicacao.py::TestAFormaDeclarada::test_a_publicacao_sem_referencia_e_recusada` |
| transições juridicamente impossíveis | `PARA_REGULARIZAR` podia terminar em `ACEITE`; `NAO_ATENDIMENTO` antes do envio; `INERCIA` sobre quem nunca ocupou | `tests/integration/convocacao/test_recusas.py::TestODesfechoQueNaoCabeNaChamada` |
| a `US5` era estruturalmente impossível | com um desfecho por convocação, a inércia posterior ao aceite não tinha onde ser gravada — e o caminho que sobrava admitia inércia de quem nunca aceitou | `tests/integration/convocacao/test_inercia.py::test_a_inercia_sucede_o_aceite_de_quem_desapareceu_depois` |
| o reclassificado não podia ser chamado | a unicidade de raiz por pessoa tornava a segunda chamada impossível, e a saída pela sucessão pulava as guardas de ordem | `tests/integration/convocacao/test_reclassificacao_integrada.py` |
| o prazo começava sem mensagem | o retorno de `send_mail` era descartado, e um backend que engole a mensagem devolve `0` sem levantar nada | `tests/unit/convocacao/test_mensagem.py::test_o_retorno_zero_do_correio_e_falha` |
| o SMTP corria dentro da trava do Processo | envio lento paralisava o certame, e um `rollback` deixava na caixa da pessoa uma convocação que o sistema esqueceu | `tests/integration/convocacao/test_comunicacao.py::test_o_envio_acontece_fora_da_transacao_que_trava_o_processo` |
| o vencimento saía em UTC | `17:00` gravado virava `17:00` lido em São Paulo, onde vence às `14:00` — três horas de prazo que a pessoa não tem | `tests/unit/convocacao/test_mensagem.py::test_o_prazo_em_sao_paulo_sai_tres_horas_antes_do_utc` |
| a leitura do candidato só ia para o log | `FR-288b` pede trilha, e log de servidor não é auditável | `tests/interface/test_portal_convocacao.py::test_a_leitura_entra_na_trilha_do_edital` |
| redirecionamento aberto | `voltar` vinha do corpo do pedido sem conferência | `tests/interface/test_convocacao.py::test_o_atestado_nao_redireciona_para_fora_do_sistema` |
| a proveniência apontava para o ato errado | o efeito citava a **convocação**, e o rótulo dizia "desfecho de convocação" | `tests/interface/test_convocacao.py::test_o_efeito_de_ocupacao_cita_o_desfecho_que_o_produziu` |
| desfecho sem efeito era possível | o campo era anulável e nenhuma constraint o exigia — numa tabela append-only a linha divergente não teria conserto | `convocacao/0003_sucessao_do_desfecho.py` |

**Três decisões de domínio saíram daí**, e estão nos comentários dos módulos que as implementam:

1. **Titular não é ocupante.** A janela é recortada sobre a sequência que progrediu; ocupante é o
   titular **habilitado**. Quem é titular e foi eliminado não ocupa a vaga dele — ela aparece em
   `faltando`, e alguém precisa chamar o próximo, com ato.
2. **O desfecho sucede o desfecho.** A `FR-273` passa a ser lida como "um desfecho **vigente** por
   convocação", do mesmo modo que há uma apuração vigente por recorte. É o que torna o cancelamento
   por inércia registrável sobre quem havia aceitado.
3. **A chamada tem número.** A mesma pessoa é legitimamente chamada mais de uma vez no mesmo
   recorte — o reclassificado que volta —, e o número é o que torna a regra exprimível no banco sem
   confundir chamada nova com correção.

## O que esta entrega deixou aberto
**A emissão por publicação depende de declaração humana.** O sistema não publica no site do certame
— a `R-007` não lhe deu essa capacidade —, e quem emite declara onde publicou. A referência fica no
registro e o prazo corre dela, mas **nada confere** que a publicação de fato existe naquele endereço.
Fechá-lo exige a capacidade de publicar, que é incremento próprio.

**A reconciliação do portal não liga a conta à inscrição** no percurso conduzido, e é achado da
`010`: a `019` não toca identidade, credencial nem reconciliação. Registrado em
`doc/e2e/019-convocacao/relatorio.md`.
