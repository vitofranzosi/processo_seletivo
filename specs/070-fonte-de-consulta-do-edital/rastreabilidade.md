# Rastreabilidade — 070 · A fonte de consulta do Edital vigente

**Frase que governa**: *cada resposta diz de qual versão do Edital ela vem, de qual ato publicado vem
cada informação, e o que é texto do Edital, o que é dado e o que é explicação — e nunca diz mais do
que o Edital publicado diz.*

Cada linha aponta o lugar do código e o que o prende.

**Caminhos de código:**

- D = `processo_seletivo/duvidas/`
- I = `processo_seletivo/interface/`

**Testes**, sob `tests/`:

| Sigla | Arquivo | Sigla | Arquivo |
|---|---|---|---|
| **UM** | `unit/duvidas/test_matriz_da_auditoria.py` | **IV** | `integration/duvidas/test_versao_no_instante.py` |
| **UL** | `unit/duvidas/test_literal.py` | **ID** | `integration/duvidas/test_desfecho_no_instante.py` |
| **UE** | `unit/duvidas/test_explicacao.py` | **IA** | `integration/duvidas/test_documento_de_origem_incompleto.py` |
| **UC** | `unit/duvidas/test_catalogo.py` | **IO** | `integration/duvidas/test_orcamento_da_consulta.py` |
| **UO** | `unit/duvidas/test_origem.py` | **IF** | `integration/duvidas/test_fronteira_de_leitura.py` |
| **UN** | `unit/duvidas/test_canal.py` | **IC** | `integration/duvidas/test_corpus_pelo_fluxo_real.py` |
| **UA** | `unit/duvidas/test_anexos.py` | **TT** | `interface/test_duvidas.py` |
| **UR** | `unit/duvidas/test_revisao.py` | **UI** | `unit/duvidas/test_importacoes.py` |
| **UD** | `unit/duvidas/test_determinismo.py` | **UV** | `unit/duvidas/test_cobertura.py` |
| **US** | `unit/duvidas/test_estruturas.py` | **TG** | `test_gramatica_das_portas.py` |
| **UK** | `unit/duvidas/test_casos_da_revisao.py` | | |

---

## 1. Requisitos funcionais

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **FR-1410** | D`application/consultar.py` (`contexto`, `effective_version`) | IV `test_ca17_pelo_banco_antes_e_depois_da_fronteira`; UM `test_ca17_…` |
| **FR-1411** | D`application/consultar.py`; D`domain/estruturas.py` (`Resposta.versao`, uma leitura) | IV `test_sc531_e_sc536_…` |
| **FR-1412** | D`application/consultar.py` (só versão, publicações, proveniência, desfecho) | IF; IV `test_sc532_…` |
| **FR-1413** | D`application/consultar.py` (`SemVersaoVigente`); I`duvidas.py` | IV `test_edital_sem_versao_vigente_nao_tem_consulta`; TT `test_edital_sem_publicacao_…` |
| **FR-1414** | D`domain/respostas.py` (`_futuro`, `_diferencas`); D`application/consultar.py` (futuras já materializadas no instante) | UM `test_ca17_…`; IV `test_ca17_…`, `test_retificacao_publicada_depois_do_instante_…`; UK `test_o_valor_futuro_…`, `test_requisito_acrescentado_…`, `test_evento_acrescentado_…` |
| **FR-1415** | D`domain/respostas.py` (`_mudanca`, nos dois sentidos); D`application/consultar.py` (versão anterior) | UM `test_ca18_…`; IV `test_ca18_…`, `test_ca19_…`; TT `test_o_formulario_carrega_a_versao_…`; UK `test_a_versao_anterior_mais_nova_…` |
| **FR-1416** | D`domain/leitura.py` (campo ausente é "não declarado"); D`domain/respostas.py` (`_sim_ou_nao`) | UK `test_vagas_imediatas_ausentes_…`, `test_carater_da_etapa_ausente_…`; UV |
| **FR-1417** | D`domain/catalogo.py` (`PERGUNTAS`, `oferecidas`, `aplicavel_ao_perfil`) | UC `test_as_perguntas_oferecidas_dependem_do_conteudo`; UK `test_sorteio_de_um_perfil_…`, `test_perfil_sem_marco_…` |
| **FR-1418** | D`domain/catalogo.py` (`resolver`, `opcoes_de_modalidade`) | UC `test_modalidade_de_outro_perfil_…`; TT `test_perfil_inexistente_…` |
| **FR-1419** | D`domain/catalogo.py` (parâmetros só de listas) | UC `test_o_catalogo_nao_tem_pergunta_de_texto_livre` |
| **FR-1420** | D`domain/catalogo.py` (`trata`, `acompanha`); D`domain/respostas.py` (`_secoes`) | UM `test_ca04_e_ca05_…` |
| **FR-1421** | D`domain/estruturas.py` (tipos); D`domain/respostas.py` (tabela de decisão) | UM US3; TT `test_o_tipo_vem_em_palavras` |
| **FR-1422** | D`domain/explicacao.py` (`nao_informa`) | UM `test_ca10_ausencia_pura_…`, `test_negativa_declarada_…`; UE `test_negativa_so_aparece_…` |
| **FR-1423** | D`domain/explicacao.py` (`depende_da_leitura`, `varias_fontes`); D`domain/respostas.py` (`_p05`, documento divergente) | UM `test_ca11_…`, `test_ca10_tec_lab_…`; UK `test_o_documento_divergente_…` |
| **FR-1424** | D`domain/respostas.py` (`_p11`); D`domain/canal.py` | UM `test_ca27_dois_canais_…`; TT `test_dois_canais_…` |
| **FR-1425** | D`domain/explicacao.py` | UE `test_todo_numero_…`, `test_a_explicacao_nao_avalia_…` |
| **FR-1426** | D`domain/respostas.py` (descrição e local do Evento, instruções, requisitos, fundamento, textos do sorteio) | UM `test_ca14_…`, `test_ca06_as_instrucoes_saem_literais` |
| **FR-1427** | D`domain/respostas.py` (`_p03`, linha sem modalidade) | UM `test_ca03_…` |
| **FR-1428** | D`domain/respostas.py` (`_p03`, cadastro de reserva e reversão) | UK `test_cadastro_de_reserva_limite_e_reversao_…`; verificação, passo 5 |
| **FR-1429** | D`domain/respostas.py` (`_p01`, `_p02`); D`application/consultar.py` (`_desfecho`) | UM `test_ca28_…`, `test_o_desfecho_do_edital_prevalece_…`; ID; UK `test_o_desfecho_do_edital_prevalece_sobre_o_cronograma`, `test_o_desfecho_do_processo_…`, `test_desfecho_sem_data_…` |
| **FR-1430** | D`domain/anexos.py`; D`domain/respostas.py` (`_aviso_de_anexos`) | UA, inclusive `test_a_citacao_pede_romano_valido_…`; UM `test_ca13_…`; TT `test_o_aviso_de_anexo_leva_ao_anexo` |
| **FR-1431** | D`domain/leitura.py` (`onde_*`) | UL `test_nenhuma_localizacao_usa_numero_impresso`; UM `test_ca16_…` |
| **FR-1432** | D`domain/estruturas.py` (`Referencia`, `ROTULO_DA_NATUREZA`) | US |
| **FR-1433** | D`domain/leitura.py` (`texto`, sem tratamento) | UL `test_todo_texto_do_edital_e_identico_ao_publicado` |
| **FR-1434** | D`domain/explicacao.py`, D`domain/rotulos.py`; nenhum import do compositor | UI; UL |
| **FR-1435** | D`domain/leitura.py` (`instante_legivel`, `numero_legivel`); D`domain/rotulos.py` | UM `test_ca02_…` |
| **FR-1436** | I`templates/interface/duvidas.html` (rótulo da explicação) | TT `test_a_resposta_traz_versao_tipo_e_os_tres_rotulos_…` |
| **FR-1437** | D`domain/origem.py` (`origens`, `acrescimos`); D`application/consultar.py` (`_atos`, a original sempre) | UO; IA `test_cada_cartao_leva_…`, `test_valor_que_nunca_mudou_…`; UM `test_ca01_…`; UK `test_o_perfil_acrescentado_…` |
| **FR-1438** | D`domain/respostas.py` (`_link`, âncoras da página pública, anexos) | verificação, passo 7 |
| **FR-1439** | D`domain/canal.py` (`canal`, termos, contatos) | UN |
| **FR-1440** | D`domain/canal.py` (`divergente`); D`domain/revisao.py` | UN `test_dois_emails_…`; UR `test_dois_canais_…` |
| **FR-1441** | D`domain/canal.py` (institucional); D`domain/respostas.py` (`_p11`) | UN `test_01_…`; TT `test_sem_canal_no_edital_…`, `test_sem_canal_nenhum_…` |
| **FR-1442** | D`domain/canal.py` (`exclusivo`); D`domain/revisao.py` | UN `test_91_…`; UR `test_91_…` |
| **FR-1443** | D`domain/revisao.py`; D`domain/respostas.py` (`documento_de_origem_incompleto`) | UR; IA `test_o_ponto_para_revisao_nomeia_…` |
| **FR-1444** | D`domain/revisao.py` (derivado, sem gravação) | IF (nenhuma escrita); D sem `models.py` |
| **FR-1445** | I`duvidas.py`, I`urls.py` (só na gestão) | TT `test_fora_do_escopo_…`, `test_sem_identidade_…`; TG |
| **FR-1446** | D`domain/respostas.py` (ordem do conteúdo e da tabela) | UD |
| **FR-1447** | nenhum cliente de rede em D | IV `test_sc531_e_sc536_…`, `test_a_guarda_de_rede_…` |
| **FR-1448** | D`application/consultar.py` (função sem requisição) | IO, IV (chamam `consultar` sem tela) |
| **FR-1449** | D sem `models.py`; nenhuma escrita | IF; `makemigrations --check` |
| **FR-1450** | `tests/fixtures/corpus_070/`, `tests/fixtures/corpus.py` | UM; IC; IV; ID |
| **FR-1451** | I`duvidas.py` (`em`, `_instante`, inclusive o instante que transborda em UTC) | TT `test_instante_invalido_…`; verificação, passo 4 |

## 2. Critérios de sucesso

| Identificador | Onde se verifica |
|---|---|
| **SC-530** | UM (camada de conteúdo), IV, ID (camada de banco) |
| **SC-531** | IV `test_sc531_e_sc536_…` |
| **SC-532** | IV `test_sc532_…` |
| **SC-533** | UV |
| **SC-534** | UL |
| **SC-535** | IA `test_sc535_…` |
| **SC-536** | IV `test_sc531_e_sc536_…` |
| **SC-537** | [verificacao.md](verificacao.md), "Tempo de resposta" |
| **SC-538** | [verificacao.md](verificacao.md), roteiro pelo ator |
| **SC-539** | UR; TT `test_dois_canais_…` |

## 3. Experiência

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **UX-200** | I`templates/interface/duvidas.html` (`.natureza`) | TT `test_a_resposta_traz_versao_tipo_e_os_tres_rotulos_…` |
| **UX-201** | idem (versão no topo, mudança antes) | TT `test_o_formulario_carrega_a_versao_e_o_aviso_de_mudanca_vem_antes_…` |
| **UX-202** | idem (`.tipo`) | TT `test_o_tipo_vem_em_palavras` |
| **UX-203** | idem (bloco de pontos para revisão) | TT `test_a_tela_se_declara_interna_…` |
| **UX-204** | idem (`aria-live`, `autofocus`, `flex-wrap`, `<details>`) | TT; `interface/test_acessibilidade.py`; verificação a 375 px |
| **UX-205** | idem (aviso de validação interna) | TT `test_a_tela_se_declara_interna_…` |
