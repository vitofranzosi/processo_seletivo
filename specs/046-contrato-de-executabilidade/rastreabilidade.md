# Rastreabilidade — 046 · Contrato de executabilidade do Processo publicado

**Frase que governa**: *o que o sistema permite publicar não contém impossibilidade estrutural
conhecida para o que ele próprio executa depois — e o que já foi publicado não é julgado de novo como
se ainda fosse publicar.*

**Verificação final** (26/09/2026, sobre a `main` em `7f5db4a`, com a `045` mesclada): `make preparar`
em **`34 de 34`**; `make lint check` — `ruff check` e `ruff format --check` limpos, `manage.py check`
sem problemas, `makemigrations --check` sem mudança —; `make test-pg` com **7965 passando e 11
pulados**, zero falhas. O "antes" era 7882 e 11 ([antes-do-gate.md](antes-do-gate.md)); a diferença
são os casos desta feature.

Cada linha aponta o lugar do código e o teste **pelo nome**. Onde a linha diz *"leitura do diff"*, a
promessa é negativa — algo que não pode ter acontecido — e se confere lendo a mudança.

---

## 1. Requisitos

| `FR-` | Onde entrou | O que o prende |
|---|---|---|
| **FR-746** | `editais/domain/validation.py`: `_etapa_sem_resultado` e `_quem_exige_o_resultado` — `stage_result_unreachable` quando a Etapa é eliminatória, enumerada, governada por corte ou de habilitação do sorteio | `test_a_publicacao_acusa_se_e_so_se_a_consolidacao_recusaria` (24 casos), `test_a_etapa_eliminatoria_de_dupla_leitura_e_recusada_e_a_de_uma_publica`, `test_a_mesma_decisoria_enumerada_por_marco_e_recusada`, `test_a_pontuada_eliminatoria_sem_nota_minima_nao_publica` |
| **FR-747** | a função **importa** `impedimento_da_regra` e `eliminatoria` de `resultados/domain/regra.py`; nenhum predicado reescrito (leitura do diff) | a tabela-verdade é parametrizada **pela regra**: `test_a_publicacao_acusa_se_e_so_se_a_consolidacao_recusaria`; e a frase citada sem reescrita, `test_a_frase_e_a_da_regra_e_nomeia_etapa_consumidor_e_onde_corrigir` |
| **FR-748** | `stage_without_result`, aviso, quando nada exige o Resultado | `test_a_etapa_sem_efeito_decidido_e_fora_de_todo_marco_publica_com_aviso`, `test_a_decisoria_sem_efeito_fora_de_marco_avisa_e_publica`, `test_a_conferencia_mostra_o_que_a_012_acrescentou_a_etapa` |
| **FR-749** | as frases do contrato: Etapa pelo nome, a frase da regra, o consumidor (ou que nada depende do Resultado), e onde se corrige — a etapa do assistente na publicação, a Retificação da Etapa na Retificação | `test_a_frase_e_a_da_regra_e_nomeia_etapa_consumidor_e_onde_corrigir`, `test_a_eliminatoria_diz_que_ninguem_seria_eliminado`, `test_o_aviso_tambem_diz_os_quatro_elementos` (3: o aviso da publicação e os dois da Retificação), `test_a_retificacao_que_nao_toca_a_etapa_e_aceita_e_adverte_na_confirmacao` (o lugar chega à tela), `test_a_etapa_eliminatoria_de_dupla_leitura_e_recusada_e_a_de_uma_publica` |
| **FR-750** | `compor_etapas.html`, o `<dt>`/`<dd>` de *Avaliações por inscrição* no `como-preencher`; `_etapa.html` intocado | `test_o_como_preencher_explica_a_dupla_leitura_e_o_cartao_nao` |
| **FR-751** | `stage_without_result` no ato de Retificação, sempre advertência; dois códigos, e `advertencias_do_ato` intocada | `test_na_retificacao_e_sempre_advertencia`, `test_os_dois_codigos_nunca_saem_juntos_para_a_mesma_etapa`, `test_a_retificacao_que_nao_toca_a_etapa_e_aceita_e_adverte_na_confirmacao` (pela tela), `test_a_retificacao_que_volta_a_uma_avaliacao_faz_a_advertencia_sumir` |
| **FR-752** | `_perfil_sem_corte` e `_nenhum_marco_corta` — `profile_without_cut_rule`, só na publicação | `test_perfil_em_que_nenhum_marco_corta_impede_a_publicacao`, `test_a_recusa_do_perfil_sem_corte_nomeia_perfil_falta_consequencia_e_etapa`, `test_o_perfil_de_marco_unico_sem_corte_e_recusado_na_revisao_e_na_submissao`, `test_a_revisao_mostra_as_duas_pendencias_e_nao_a_primeira` |
| **FR-753** | `_marco_sem_regra_de_corte` pula o Perfil em que nenhum marco corta | `test_o_perfil_sem_corte_tem_um_relato_so`, `test_basta_um_marco_que_corte`, `test_marco_sem_regra_de_corte_e_aviso_e_nao_impedimento`, `test_o_marco_sem_corte_num_perfil_que_corta_continua_publicavel`, `test_o_corte_em_branco_passou_a_impedir_pelo_perfil` |
| **FR-754** | a função devolve `[]` fora do ato de publicação | `test_o_perfil_sem_corte_nao_e_cobrado_na_retificacao`, `test_os_achados_de_us1_nao_sao_emitidos_na_retificacao` (032) |
| **FR-755** | `interface/views.py::_pendencias`: `ANTES_DA_PUBLICACAO` decide; fora dela, `fatos_do_conteudo_publicado` (`editais/domain/validation.py`, com `FATOS_DO_CONTEUDO_PUBLICADO`) | `test_o_edital_publicado_nao_diz_impede_nem_sera_publicado`, `test_o_fato_da_etapa_sem_evento_continua_dito_no_edital_publicado`, `test_o_mesmo_conteudo_em_elaboracao_continua_impedido`, `test_encerrado_e_cancelado_se_leem_como_o_publicado` (2), `test_o_edital_publicado_diz_a_etapa_sem_evento_na_validacao_do_conteudo` (045, com a contraprova da 046), `test_edital_publicado_nao_manda_pedir_a_ninguem`, `test_edital_publicado_nao_manda_pedir_nem_a_quem_nao_tem_a_permissao` |
| **FR-756** | a lista fechada de quem consulta `validate_for_publication`; e, fora da elaboração, a validação não roda | `test_a_validacao_de_publicabilidade_so_e_consultada_por_quem_a_lista_nomeia`, `test_a_lista_nao_guarda_quem_ja_deixou_de_perguntar`, `test_a_varredura_enxerga` (quem chama); `test_o_edital_publicado_nao_executa_a_validacao_de_publicabilidade` (em que estado) |
| **FR-757** | `sorteios/infrastructure/fontes/__init__.py`: `fontes_publicadas()`; os três leitores (`forms.opcoes_do_metodo`, `perfis._validar_fonte_publicada`, `fonte_declarada`) | `test_em_producao_o_vocabulario_e_so_a_loteria_federal`, `test_em_producao_o_seletor_nao_oferece_a_demonstracao`, `test_em_producao_a_execucao_recusa_a_demonstracao`, `test_em_producao_a_publicacao_e_a_retificacao_acusam_a_demonstracao` (2), `test_em_producao_a_gravacao_recusa_a_demonstracao`, `test_em_producao_o_reaproveitamento_nao_copia_a_demonstracao` |
| **FR-758** | `config/settings/production.py`, a terceira barreira de demonstração; `base.py` falsa por padrão | `test_configuracao_insegura_impede_a_inicializacao[...SORTEIO_FONTE_DE_DEMONSTRACAO]`, `test_producao_nasce_sem_a_fonte_de_demonstracao` |
| **FR-759** | `development.py` e `test.py` a ligam pelo módulo | `test_na_suite_a_demonstracao_pertence_ao_vocabulario`; a suíte de sorteio inalterada; `seed_demo` sorteando sem rede (T017) |

## 2. Critérios de sucesso

| `SC-` | Como se mede | Resultado |
|---|---|---|
| **SC-275** | a tabela-verdade: quatro formas × seis situações, parametrizada por `impedimento_da_regra` | 24 casos, zero divergências |
| **SC-276** | `test_o_executavel_publica_sem_achado_da_046` sobre os sete rascunhos que modelam a amostra; `test_seed_demo.py` publicando pelo gate | zero achados da família |
| **SC-277** | `tests/interface/test_perfil_sem_corte.py` | marco único sem corte recusado na submissão; com o segundo marco que corta, publicado com **um** aviso |
| **SC-278** | `tests/interface/test_edital_publicado_sem_pendencias.py` — a tela e as nove etapas do assistente | zero impeditivos e zero avisos de publicabilidade no publicado, encerrado e cancelado, com a validação sem rodar; o fato da `045` dito; o impeditivo em elaboração |
| **SC-279** | `test_fonte_fora_de_producao.py` e `test_configuracao_producao.py` | zero opções em produção; recusa nos quatro atos e na execução; boot recusado; a suíte sorteia |
| **SC-280** | uma asserção por elemento da frase em cada código novo, **recusa e aviso**: `test_a_frase_e_a_da_regra_…`, `test_a_eliminatoria_diz_…`, `test_o_aviso_tambem_diz_os_quatro_elementos`, `test_a_recusa_do_perfil_sem_corte_nomeia_…` | 100% |
| **SC-281** | leitura do diff: nenhum arquivo em `*/migrations/`; `make preparar` em `34 de 34` | zero migrations, zero linhas publicadas alteradas |

## 3. Correlação com a auditoria

Ver a spec, *"Correlação com a auditoria de consolidação"*. Em resumo, pelo fluxo observável:

| Achado | Fechado por | Demonstrado em |
|---|---|---|
| `RC-29` | `FR-746` a `FR-751` | a tabela-verdade; a recusa e o aviso pela tela; a advertência na confirmação da Retificação |
| `RC-30` / `D-G1` | `FR-752` a `FR-754` | a recusa por Perfil, pela Revisão e pela submissão; o Cenário D publicando |
| `RC-32` | `FR-755`, `FR-756` | o Edital publicado sem *"Impede"*, com o fato da `045` preservado |
| `RC-72` | `FR-757` a `FR-759` | o vocabulário sob configuração de produção; a barreira de boot |

## 4. O que a implementação mudou fora do previsto

- **A tela do marco removido devolvia 404 quando o marco cortava** — corrigido em
  `views._corte_do_marco`, preso por `tests/interface/test_marco_removido.py`. Ver
  [antes-do-gate.md](antes-do-gate.md).
- **A `FR-755` ganhou a exceção dos fatos**, por decisão do usuário (`D-003`), depois de a `045`
  mesclada mostrar que a `FR-739` dela exige o aviso da Etapa sem Evento na página publicada.
- **A revisão de 26/09 corrigiu a forma da exceção**: a primeira versão validava tudo e filtrava os
  fatos depois, e o gate continuava rodando sobre o Edital publicado. Passou a derivar cada fato pela
  sua função (`fatos_do_conteudo_publicado`), e um caso prende o estado. A mesma revisão encheu a
  contraprova do ator sem permissão, que publicava sem pendência nenhuma na tela.
- **Uma segunda revisão, no mesmo dia, achou o aviso `stage_without_result` sem dizer onde se
  corrigir** — a `FR-749` o exige, e a confirmação da Retificação exibe só a frase. O aviso passou a
  dizê-lo nos dois atos, a `FR-749` passou a nomear o lugar de cada um por extenso, e os testes
  passaram a conferir os quatro elementos também no aviso.
