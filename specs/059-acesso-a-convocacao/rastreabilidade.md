# Rastreabilidade — 059 · O caminho do candidato até a convocação e o Requerimento de Matrícula

**Frase que governa**: *quem foi convocado chega à convocação pelo portal, sem depender da mensagem
— e, quando o Edital pede o Requerimento de Matrícula na convocação, chega a ele pelo mesmo caminho.*

Cada linha aponta o lugar do código e o que o prende. **TC** =
`tests/interface/test_portal_caminho_da_convocacao.py`; **TA** =
`tests/authorization/test_convocacao_alheia.py`; **TV** =
`tests/integration/convocacao/test_vigentes_por_inscricao.py`; **TL** =
`tests/performance/test_lista_com_convocacao.py`; **V** = a [verificação](verificacao.md), medida no
navegador.

P = `backend/processo_seletivo/portal/`; T = P`templates/portal/`.

---

## 1. Requisitos funcionais

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **FR-1089** | P`views.py`: `_convocacoes_da_lista`, `_item_da_lista` (`convocacao_aberta`); T`inscricoes.html`: "Convocação aberta" com símbolo | TC `TestMinhasInscricoes`: `test_a_convocacao_aberta_e_indicada_e_leva_a_tela_dela`, `test_antes_do_envio_a_convocacao_ja_e_indicada`, `test_com_o_vencimento_decorrido_sem_desfecho_continua_aberta`; V |
| **FR-1090** | T`inscricoes.html`: "Ver convocação" como `a.principal`, "Acompanhar" como `a.acompanhar`; T`base.html`: as ações acima do título esticado (D-003, D-010) | TC `test_a_convocacao_aberta_e_indicada_e_leva_a_tela_dela`; V (`elementFromPoint` antes e depois) |
| **FR-1091** | P`views.py`: `convocacao_concluida`; T`inscricoes.html`: a nota "Convocação: <espécie>" (D-004) | TC `test_a_concluida_vira_nota_e_a_acao_volta_a_ser_acompanhar`, `test_sem_convocacao_o_item_fica_como_estava` |
| **FR-1092** | `convocacao/application/selectors.py::vigentes_por_inscricao`, chamado uma vez, só para as enviadas (D-002) | TV `test_o_custo_nao_cresce_com_as_inscricoes_pedidas`, `test_o_custo_nao_cresce_com_as_convocacoes`, `test_sem_inscricao_pedida_nao_consulta_nada`; TL `test_a_lista_le_a_convocacao_numa_consulta_so`, `test_a_lista_de_quem_foi_convocado_nao_toca_o_requerimento`; `test_orcamento_de_consulta.py::test_a_lista_de_inscricoes_nao_toca_a_feature` |
| **FR-1093** | P`views.py::acompanhamento`; T`_convocacao_da_inscricao.html`, incluído por T`acompanhamento.html` (D-005) | TC `TestAcompanhamento`: `test_a_secao_mostra_a_chamada_o_prazo_e_o_caminho`, `test_a_concluida_continua_consultavel`; V |
| **FR-1094** | T`_convocacao_da_inscricao.html`: as quatro situações, nos termos da tela da convocação | TC `test_antes_do_envio_diz_que_o_prazo_nao_comecou`, `test_a_secao_mostra_a_chamada_o_prazo_e_o_caminho`, `test_vencimento_decorrido_nao_decide_nada_sozinho`, `test_a_concluida_continua_consultavel` |
| **FR-1095** | T`_convocacao_da_inscricao.html`: `{% if convocacao %}` | TC `test_sem_convocacao_nao_ha_secao` |
| **FR-1096** | P`views.py`: `CHAMADO_DO_REQUERIMENTO`, `_requerimento_da_convocacao`; T`_chamado_do_requerimento.html`, incluído pela convocação e pela seção (D-007) | TC `TestRequerimentoNaConvocacao`: `test_convocada_sem_rascunho_ve_o_chamado_nas_duas_telas`, `test_com_rascunho_o_chamado_e_o_mesmo` |
| **FR-1097** | o mesmo, no ramo `"conferir"` | TC `test_enviado_ve_a_conferencia_e_nao_o_chamado`; V |
| **FR-1098** | `CHAMADO_DO_REQUERIMENTO` sem "ainda indisponível" nem "não aplicável" | TC `test_desfechada_sem_envio_nao_oferece_nada`, `test_edital_que_nao_pede_nao_oferece_nada` |
| **FR-1099** | `_requerimento_da_convocacao` pergunta a `preencher_requerimento.apurar` | TC `TestRequerimentoNaConvocacao` (as cinco situações saem da política); `test_portal_requerimento_convocacao.py` continua verde |
| **FR-1100** | `vigentes_por_inscricao`, lido pela lista, pelo acompanhamento e pela view `convocacao`; `_convocacao_para_a_tela`, a tradução única (D-001) | TV `test_a_sucessora_ocupa_o_lugar_da_sucedida`; TC `TestAcompanhamento::test_a_sucessora_ocupa_o_lugar_da_sucedida`; `test_portal_convocacao.py` sem edição |
| **FR-1101** | `_inscricao_do_titular` nas quatro rotas, inalterado | TA `test_a_rota_de_joao_responde_a_maria_como_inscricao_inexistente` (quatro rotas), `test_a_lista_e_o_acompanhamento_de_maria_nao_mostram_nada_de_joao`, `test_a_titular_alcanca_as_proprias`, `test_sem_sessao_nenhuma_rota_revela_se_a_inscricao_existe` |
| **FR-1102** | as rotas que já existiam; nenhum `href` novo com dado pessoal | TA `test_nenhum_endereco_novo_carrega_dado_pessoal` |
| **FR-1103** | nenhum `record_event` fora de `_registrar_leitura_da_convocacao` (D-008) | TC `test_so_a_tela_da_convocacao_registra_leitura` |
| **FR-1104** | nenhuma mudança em `interface/views.py` nem em `comunicar.py` (D-009) | TC `test_a_mensagem_continua_apontando_minhas_inscricoes` |
| **FR-1105** | revisão do diff: nenhuma rota em P`urls.py`, nenhum arquivo em `interface/`, nenhuma migration, nenhuma regra de domínio; o conteúdo da tela da convocação só ganha o parcial do chamado | `git diff main --stat`; `make check` (migrations) |

## 2. Requisitos de experiência

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **UX-145** | T`inscricoes.html`: "➜ Convocação aberta", com o símbolo `aria-hidden`; T`base.html`: `.situacao.convocada` por peso, e não por cor | TC `test_a_convocacao_aberta_e_indicada_e_leva_a_tela_dela` (o texto) |
| **UX-146** | nenhuma tabela nem estilo embutido nos templates tocados; `dl.campos` na seção | TC `TestTelaEstreita`; V (375 px: `scrollWidth` 375 nas três telas) |
| **UX-147** | os dois parciais novos e T`inscricoes.html` em `DA_019` (D-011) | `tests/test_vocabulario_da_convocacao.py` |

## 3. Critérios de sucesso

| Identificador | Como se mede | Resultado |
|---|---|---|
| **SC-424** | da lista à convocação | 1 clique ("Ver convocação"); TC; V |
| **SC-425** | da lista ao requerimento, no momento *na convocação* | 2 cliques ("Ver convocação" → "Preencher Requerimento de Matrícula"); TC |
| **SC-426** | consultas da leitura das convocações e da lista | TV (1 e 2 convocadas, mesmo custo); TL (uma consulta com `IN`, zero no requerimento) |
| **SC-427** | quatro rotas e a lista, alheia × inexistente | TA (status e corpo idênticos) |
| **SC-428** | `make lint check test-pg` | ver a [verificação](verificacao.md) |
