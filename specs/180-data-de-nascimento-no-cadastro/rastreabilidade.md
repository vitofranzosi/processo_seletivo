# Rastreabilidade — 180 · A data de nascimento entra no cadastro do candidato

**Frase que governa**: *a data é declarada, como o CPF; serve para conferir, nunca para entrar.*

Caminhos de código relativos a `backend/processo_seletivo/`. As abreviações:

- **LD** — `tests/unit/identidade/test_data_de_nascimento.py` (a leitura da data, pura)
- **NN** — `tests/integration/identidade/test_nascimento_no_nucleo.py` (Seus dados, histórias 1 e 2)
- **ES** — `tests/integration/inscricoes/test_envio_sem_data.py` (o comando de envio)
- **RV** — `tests/integration/portal/test_revisao_com_a_data.py` (a revisão e a volta)
- **RQ** — `tests/integration/requerimentos/test_requerimento_com_a_data.py` (D-003)

**Estado em 17/11**: o MVP está implementado. O que ainda não tem prova está marcado **pendente**, com
a tarefa que o cobre.

---

## Requisitos funcionais

| Requisito | Onde | Prova |
|---|---|---|
| FR-8300 | `identidade/models.py` (`data_nascimento`), `credenciais.falta_o_nucleo` | NN: `test_sem_data_a_identidade_falta_o_nucleo`, `test_a_tela_pede_nome_cpf_e_data` |
| FR-8301 | portas existentes (`portal/views.py`: volta do código e `inscrever`) | NN: `test_os_tres_validos_sao_gravados_e_voltam_a_vaga` |
| FR-8302 | `falta_o_nucleo`; `meus_dados` (`foco_na_data`) | NN: `test_o_cadastro_antigo_vai_a_seus_dados_na_proxima_vaga`, `test_o_cadastro_antigo_ve_nome_e_cpf_preenchidos_e_o_foco_na_data`, `test_informada_a_data_o_cadastro_antigo_segue_para_a_vaga` |
| FR-8303 | `inscricoes/application/submissao.py` (passo 5b); `revisao.html`; `_destino_e_revisao` | ES: `test_sem_data_o_envio_e_recusado`; RV: `test_o_envio_pela_tela_sem_data_e_recusado_com_a_frase`, `test_informar_em_seus_dados_volta_a_revisao_e_o_envio_passa` |
| FR-8304 | coluna anulável, sem restrição de banco | ES: as enviadas da suíte inteira continuam válidas; **pendente** um caso explícito |
| FR-8305 | `inscricoes/domain/pessoais.ler_data_de_nascimento` | LD: os casos de formato, inexistente, futura e teto |
| FR-8306 | idem, sem idade mínima | LD: `test_menor_de_idade_e_aceito` |
| FR-8307 | `credenciais.recusas`; `meus_dados` | NN: `test_data_vazia_e_recusada_sem_perder_o_resto`, `test_data_impossivel_e_recusada_e_volta_como_digitada` |
| FR-8308 | `submissao._gravar_o_ato` | ES: `test_o_envio_congela_a_data_do_cadastro`, `test_corrigir_o_cadastro_antes_do_envio_muda_o_que_e_congelado`, `test_a_data_da_enviada_nao_muda_pelo_banco` |
| FR-8309 | `credenciais.data_editavel` | NN: `test_a_data_congela_com_o_cpf`, `test_quem_ja_se_inscreveu_sem_data_pode_informa_la_uma_vez` |
| FR-8310 | nenhum caminho de acesso lê a coluna | **pendente** (T034) |
| FR-8311 | o comprovante não a lê; a trilha não a recebe | ES: `test_o_comprovante_nao_mostra_a_data`; **pendente** a varredura das páginas públicas (T033) |
| FR-8312, FR-8315, FR-8316, FR-8317 | — | **pendentes**: história 3 (T024–T029) |
| FR-8313 | `requerimentos/application/preencher._nascimento_do_cadastro` | RQ: os quatro casos |
| FR-8314 | `meus_dados.html` | NN: `test_a_tela_diz_para_que_serve_a_data` |
| FR-8318 | nenhum código preenche o fato do Perfil a partir do cadastro | **pendente** um caso explícito (T032) |

## Requisitos de experiência

| Requisito | Onde | Prova |
|---|---|---|
| UX-1000 | `meus_dados.html`: `type="text"`, `inputmode="numeric"`, `autocomplete="bday"` | NN: `test_a_tela_pede_nome_cpf_e_data`; **pendente** o percurso no celular (T038) |
| UX-1001 | `meus_dados` (`foco_na_data`) | NN: `test_o_cadastro_antigo_ve_nome_e_cpf_preenchidos_e_o_foco_na_data` |

## Critérios de sucesso

| Critério | Prova |
|---|---|
| SC-2900 | ES: `test_sem_data_o_envio_e_recusado` (o comando recusa todo envio sem data) |
| SC-2901 | NN: os três campos numa tela, sem passo novo |
| SC-2902 | NN: `test_o_cadastro_antigo_ve_nome_e_cpf_preenchidos_e_o_foco_na_data` |
| SC-2903 | **pendente** (T033) |
| SC-2904 | **pendente** (T034) |
| SC-2905 | **pendente**: a dupla passada do checklist do TMD |
| SC-2906 | **pendente**: história 3 |
| SC-2907 | RQ: `test_nasce_com_a_data_do_cadastro` |

## Casos-limite

| Caso | Prova |
|---|---|
| 31/02 e 29/02 em ano não bissexto | LD: `test_data_que_nao_existe_e_recusada` |
| Hoje ou no futuro | LD: `test_hoje_e_recusado_e_ontem_e_aceito` |
| Mais de 120 anos | LD: `test_o_teto_e_cento_e_vinte_anos_completos` |
| Menor de idade | LD: `test_menor_de_idade_e_aceito` |
| Ano com dois dígitos | LD: `test_fora_do_formato_e_recusada` (`01/02/03`) |
| Rascunho aberto acompanha a correção | ES: `test_corrigir_o_cadastro_antes_do_envio_muda_o_que_e_congelado` |
| Enviada guarda a data do envio | ES: `test_a_data_da_enviada_nao_muda_pelo_banco` |
| Fato declarado do Perfil continua pedido | **pendente** (T032) |
| CPF e data de outra pessoa não dão acesso | **pendente** (T034) |
| Volta à revisão vale só para a visita | RV: `test_a_volta_a_revisao_nao_sobrevive_a_outra_visita`, `test_destino_que_nao_e_a_revisao_nao_e_guardado` |
