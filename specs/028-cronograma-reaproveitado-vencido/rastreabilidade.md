# Rastreabilidade — 028 · Cronograma reaproveitado não nasce publicável

Cada requisito, onde foi feito e onde é verificado. É o Princípio V: um requisito sem linha aqui é
um requisito que ninguém sabe se entrou.

Caminhos relativos a `backend/`. Abreviações: `calendario` =
`tests/unit/editais/test_calendario.py`; `vencido` = `tests/unit/editais/test_cronograma_vencido.py`;
`selo` = `tests/interface/test_selo_do_cronograma.py`; `ato` =
`tests/integration/publicacoes/test_cronograma_vencido_no_ato.py`; `demo` =
`tests/integration/test_seed_demo.py`.

---

## A referência temporal

| Requisito | Onde foi feito | Onde é verificado |
|---|---|---|
| **FR-341** — um instante por ato | `editais/domain/validation.py`, `agora` resolvido uma vez no topo de `validate_for_publication` | `vencido::test_a_conferencia_usa_um_instante_para_o_cronograma_inteiro`, `::test_o_instante_passado_governa_e_nao_o_relogio_da_maquina` |
| **FR-342** — ano na zona institucional | `editais/domain/calendario.py::ano_do_evento` | `calendario::test_o_ano_do_ultimo_horario_do_ano_e_lido_em_vitoria`, `::test_o_ano_de_um_instante_gravado_em_utc_tambem_e_lido_em_vitoria` |

## Os três achados

| Requisito | Onde foi feito | Onde é verificado |
|---|---|---|
| **FR-343** — evento vencido adverte | `validation.py::_eventos_vencidos` | `vencido::test_o_achado_existe_na_publicacao_e_nao_existe_na_retificacao`, `::test_evento_em_curso_nomeia_o_inicio_e_nao_o_termino_futuro` |
| **FR-343a** — precedência do término | `calendario.py::instante_vencido` | `calendario::test_com_os_dois_vencidos_a_mensagem_nomeia_o_termino`, `vencido::test_com_inicio_e_termino_vencidos_a_mensagem_nomeia_o_termino`, `::test_sem_termino_declarado_a_mensagem_nomeia_o_inicio` |
| **FR-344** — ano divergente adverte | `validation.py::_ano_dos_eventos` | `vencido::test_o_edital_de_dezembro_com_eventos_do_ano_seguinte_adverte_e_nao_impede` |
| **FR-345** — uma advertência por espécie | ambos, um achado por Evento | `vencido::test_evento_no_passado_e_com_ano_divergente_produz_as_duas_advertencias`, `::test_um_achado_por_evento_e_nao_um_por_instante` |
| **FR-346** — período encerrado impede | `validation.py::_periodo_de_inscricoes_encerrado` | `vencido::test_periodo_encerrado_impede_a_publicacao`, `ato::test_a_submissao_e_recusada_com_o_periodo_ja_encerrado` |
| **FR-347** — as três não-bordas | o `>` estrito de `inscricoes/domain/periodo.py`, reusado | `vencido::test_termino_igual_ao_instante_do_ato_nao_encerra`, `::test_periodo_sem_termino_declarado_nao_encerra`, `::test_periodo_em_curso_adverte_mas_nao_impede`, `calendario::test_instante_igual_ao_do_ato_nao_venceu` |
| **FR-348** — códigos próprios | três códigos novos em `validation.py` | `vencido::test_os_achados_que_ja_existiam_sobre_o_periodo_nao_mudam` |
| **FR-349** — destino é a etapa Cronograma | caminho da entidade, nunca `/schedule` | `vencido::test_os_tres_achados_levam_a_etapa_do_cronograma_e_nao_a_da_inscricao`, `::test_o_destino_da_designacao_ausente_continua_sendo_a_etapa_de_inscricao` |
| **FR-350** — achados existentes não mudam | nada foi alterado neles | `vencido::test_os_achados_que_ja_existiam_sobre_o_periodo_nao_mudam`, `ato::test_antecipar_o_encerramento_das_inscricoes_nao_e_recusado` |

## O que a conferência não faz

| Requisito | Onde foi feito | Onde é verificado |
|---|---|---|
| **FR-351** — nenhuma data é tocada | as três verificações só leem | `selo::test_o_edital_reaproveitado_nasce_com_o_cronograma_pendente` (compara cada data da cópia com a publicada pela origem) |
| **FR-352** — sem regra de duração | nenhuma foi escrita | `vencido::test_o_cenario_do_12_2027_produz_exatamente_tres_achados` (exige que nenhuma mensagem fale de duração) |
| **FR-353** — nada entra no conteúdo publicado | nenhum campo novo; `EVENTO_PUBLICADO` intocado | **guardião existente**: `tests/contract/test_forma_publicada.py` |

## O ato

| Requisito | Onde foi feito | Onde é verificado |
|---|---|---|
| **FR-354** — nenhum achado na Retificação | `if ato != ATO_DE_PUBLICACAO: return []` nas três | `vencido::test_o_achado_existe_na_publicacao_e_nao_existe_na_retificacao`, `::test_o_impedimento_nao_existe_no_ato_de_retificacao`, `::test_a_advertencia_de_ano_nao_existe_no_ato_de_retificacao`, `ato::test_retificar_um_edital_do_acervo_nao_produz_achado_desta_feature` |
| **FR-355** — antecipar prazo não é recusado | consequência da FR-354 | `ato::test_antecipar_o_encerramento_das_inscricoes_nao_e_recusado`, `ato::test_a_retificacao_de_uma_frase_do_acervo_publica` |

## Quando a conferência roda

| Requisito | Onde foi feito | Onde é verificado |
|---|---|---|
| **FR-356** — no ponto mais cedo | `interface/views.py::_pendencias`, que já roda em cada página do assistente | `selo::test_o_edital_reaproveitado_nasce_com_o_cronograma_pendente` (primeira abertura, sem gravação) |
| **FR-357** — publicação recusa sem a Revisão | `publish_edital.py:649`, conferência independente | `ato::test_a_publicacao_e_recusada_mesmo_sem_a_revisao_ter_sido_aberta` |
| **FR-358** — o instante da publicação governa | `agora=now` nas duas chamadas, de transações distintas | `ato::test_o_prazo_que_vence_entre_a_homologacao_e_a_publicacao_impede_publicar` |

## O selo

| Requisito | Onde foi feito | Onde é verificado |
|---|---|---|
| **FR-359** — validade, não existência | `interface/views.py::_estado_do_cronograma` | `selo::test_cronograma_com_evento_no_passado_fica_pendente`, `::test_cronograma_inteiro_no_futuro_continua_concluido` |
| **FR-360** — volta sozinho | estado derivado, não persistido | `selo::test_corrigir_as_datas_devolve_o_selo_sem_gravacao_nenhuma` |
| **FR-361** — os outros oito não mudam | só a chave `cronograma` mudou | `selo::test_os_outros_oito_selos_nao_mudam_de_criterio` |
| **FR-362** — pendente não impede | o selo não alimenta gate algum | `selo::test_pendente_nao_impede_avancar_entre_etapas_nem_submeter` |

## Aplicabilidade

| Requisito | Onde foi feito | Onde é verificado |
|---|---|---|
| **FR-363** — vale para todo Edital | a conferência é do conteúdo, não da origem | `selo::test_o_edital_composto_do_zero_produz_os_mesmos_achados` |
| **FR-364** — o reaproveitamento não muda | nenhuma linha de `reaproveitamento.py` foi tocada | **guardiões existentes**: `tests/unit/editais/test_reaproveitamento.py`, `tests/integration/editais/test_reaproveitamento.py` |
| **FR-365** — nada publicado é reescrito | a feature só lê | **guardiões existentes**: `tests/integration/publicacoes/test_integridade_publicacao.py`, `test_retificacao_intocada.py` |

## A demonstração

| Requisito | Onde foi feito | Onde é verificado |
|---|---|---|
| **FR-366** — Edital reaproveitado que exercita o cenário | `seed_demo.py::_edital_reaproveitado` | `demo::test_a_demonstracao_contem_o_edital_reaproveitado_que_o_sistema_impede` |
| **FR-367** — fica em elaboração, e o resto não muda | ele não publica porque o sistema o impede | mesmo teste, mais `demo::test_duas_demonstracoes_convivem_com_codigos_distintos` |

## Apresentação

| Requisito | Onde foi feito | Onde é verificado |
|---|---|---|
| **UX-047** — instante legível na zona institucional | `validation.py::_por_extenso` | `vencido::test_nenhuma_mensagem_desta_feature_traz_iso_cru_json_pointer_ou_utc` |
| **UX-048** — o impedimento diz quando e o quê | mensagem de `registration_period_closed` | `vencido::test_a_mensagem_do_impedimento_diz_quando_encerrou_e_o_que_acontece` |
| **UX-049** — a etapa explica a pendência | `pendencias_aqui`, que já existia | `selo::test_pendente_nao_impede_avancar_entre_etapas_nem_submeter`, `::test_o_edital_reaproveitado_nasce_com_o_cronograma_pendente` |
| **UX-050** — a Revisão não diz "nada pendente" | consequência dos achados | `selo::test_a_revisao_nao_diz_que_nada_esta_pendente_com_cronograma_vencido` |
| **UX-051** — o aviso da `023` continua | nada foi alterado nele | `selo::test_o_edital_reaproveitado_nasce_com_o_cronograma_pendente` |

## Critérios de sucesso

| Critério | Onde é verificado |
|---|---|
| **SC-112** — zero Editais publicados com inscrição encerrada | `ato::test_a_submissao_e_recusada_com_o_periodo_ja_encerrado`, `::test_o_prazo_que_vence_entre_a_homologacao_e_a_publicacao_impede_publicar` |
| **SC-113** — pendente na primeira abertura | `selo::test_o_edital_reaproveitado_nasce_com_o_cronograma_pendente` |
| **SC-114** — o cenário do 12/2027 | `vencido::test_o_cenario_do_12_2027_produz_exatamente_tres_achados` |
| **SC-115** — zero achados numa Retificação do acervo | `ato::test_retificar_um_edital_do_acervo_nao_produz_achado_desta_feature` |
| **SC-116** — o rascunho não muda | `selo::test_o_edital_reaproveitado_nasce_com_o_cronograma_pendente` |
| **SC-117** — descobre antes de submeter | `selo::test_o_edital_reaproveitado_nasce_com_o_cronograma_pendente` (a pendência está na etapa, antes de qualquer submissão) |
| **SC-118** — mesmo resultado em qualquer fuso | `calendario::test_o_ano_do_ultimo_horario_do_ano_e_lido_em_vitoria`, `vencido::test_o_ultimo_horario_do_ano_em_vitoria_nao_diverge` |
| **SC-119** — a demonstração contém o caso | `demo::test_a_demonstracao_contem_o_edital_reaproveitado_que_o_sistema_impede` |

---

## Os três requisitos sem tarefa dedicada

`FR-353`, `FR-364` e `FR-365` são proibições sobre coisas que esta feature **não faz**, e por isso
não ganharam teste próprio: quem as guarda já existia, e a `T033` os exercita a cada execução da
suíte. Nomeá-los aqui é o que impede a rastreabilidade de registrar lacuna onde há cobertura — e é o
que permite, no futuro, descobrir que a proibição ficou sem guarda se algum deles for removido.

## O que mudou na suíte por causa desta feature

| | |
|---|---|
| Contagem de partida (15/09/2026) | 5644 passando, 2 pulados |
| Contagem final | **5704 passando, 2 pulados** |
| Testes novos | 60 |
| Testes existentes que mudaram de forma | 6 fixtures que publicavam Edital com a inscrição já encerrada, mais `rascunho_rico` do reaproveitamento |
| Migrations | **nenhuma** (`makemigrations --check`: *No changes detected*) |

Os seis fixtures passaram a publicar com o prazo aberto e a fechá-lo por Retificação — que é como
acontece na vida, e o que a `FR-355` autorizou por escrito. O sétimo caso, `rascunho_rico`, não
estava previsto na pesquisa: a origem dos testes de reaproveitamento era ela própria um Edital com
o período de 2025 já vencido, e passou a ter o término no futuro para poder ser publicada.
