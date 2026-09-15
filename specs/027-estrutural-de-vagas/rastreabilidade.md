# Rastreabilidade — 027 Estrutural de vagas

Cada identificador definido em [spec.md](spec.md), com onde ele foi implementado e onde é
verificado. O teste `tests/test_citacoes_de_requisito.py` cobra esta matriz inteira: um requisito
sem linha aqui reprova o CI.

Caminhos relativos a `backend/`.

## Requisitos funcionais

### A declaração única

| Requisito | Implementação | Verificação |
|---|---|---|
| **FR-316** | `interface/forms.py` (`_quadro_para_o_formulario`, `quadro_do_formulario`), `interface/templates/interface/_linha_do_quadro.html` (`linha.derivada`), `editais/application/draft.py` | `tests/interface/test_compor_quadro.py`, `tests/acceptance/test_us1_declaracao_unica_de_vagas.py`, `tests/contract/test_edital_draft_api.py` |
| **FR-317** | `editais/domain/perfis.py` (`listas_reservadas`), `interface/forms.py` (`_listas_reservadas_do_modelo`), `interface/views.py` (`_tem_lista_reservada_no_formulario`) | `tests/unit/editais/test_derivacao_da_linha_geral.py`, `tests/unit/editais/test_quadro_de_vagas.py` |
| **FR-318** | `editais/domain/perfis.py` (`derivar_linha_geral`), `editais/application/draft.py` | `tests/unit/editais/test_derivacao_da_linha_geral.py`, `tests/integration/editais/test_derivacao_persistida.py` |
| **FR-319** | `editais/domain/perfis.py` (a derivação lê só `immediateVacancies`) | `tests/unit/editais/test_derivacao_da_linha_geral.py`, `tests/unit/editais/test_invariantes_da_declaracao_unica.py` |
| **FR-320** | `editais/domain/perfis.py` (a projeção tem uma direção só) | `tests/unit/editais/test_derivacao_da_linha_geral.py`, `tests/interface/test_compor_quadro.py` |
| **FR-321** | `interface/views.py` (`fragmento_modalidade`), `interface/templates/interface/_modalidade_com_linha.html`, `_secao_do_quadro.html` | `tests/interface/test_compor_quadro.py`, `tests/acceptance/test_us1_declaracao_unica_de_vagas.py` |
| **FR-322** | `editais/domain/perfis.py` (reafirma a cada gravação), `interface/views.py` (`_linhas_gerais_rederivadas`), `interface/templates/interface/compor_base.html` | `tests/interface/test_compor_quadro.py`, `tests/integration/editais/test_derivacao_persistida.py` |
| **FR-323** | `editais/domain/validation.py` (`_linha_geral_exigida`, `vacancy_general_row_missing`), `publicacoes/application/retificacoes.py` (`ATO_DE_RETIFICACAO`) | `tests/unit/editais/test_quadro_de_vagas.py`, `tests/integration/editais/test_acervo_sem_quadro_continua_retificavel.py` |

### O que o sistema diz antes de publicar

| Requisito | Implementação | Verificação |
|---|---|---|
| **FR-324** | `editais/domain/validation.py` (`_listas_reservadas_sem_linha`) | `tests/interface/test_advertencias_do_quadro.py`, `tests/unit/editais/test_invariantes_da_declaracao_unica.py` |
| **FR-325** | `editais/domain/validation.py` (`_ampla_por_declarar`) | `tests/interface/test_advertencias_do_quadro.py` |
| **FR-326** | `interface/revisao.py` (`_vagas_e_quadro`, `_listas_sem_linha`) | `tests/interface/test_advertencias_do_quadro.py`, `tests/unit/interface/test_revisao.py` |
| **FR-327** | `interface/views.py` (`_pendencias` classifica o aviso), `interface/templates/interface/compor_revisao.html` (`{% if pendencias %}`) | `tests/interface/test_advertencias_do_quadro.py` |
| **FR-328** | `interface/templates/interface/confirmar.html` (bloco de aviso) | `tests/interface/test_advertencias_do_quadro.py` |
| **FR-329** | `editais/application/draft.py` (a linha é persistida e viaja no snapshot), `publicacoes/application/publish_edital.py` | `tests/acceptance/test_us1_declaracao_unica_de_vagas.py`, `tests/integration/editais/test_derivacao_persistida.py` |

### O acervo publicado

| Requisito | Implementação | Verificação |
|---|---|---|
| **FR-330** | `classificacao/application/corte.py` (`linha_do_quadro`, sem inferência) | `tests/unit/classificacao/test_leitura_do_quadro_sem_inferencia.py`, `tests/unit/editais/test_invariantes_da_declaracao_unica.py` |
| **FR-331** | `interface/supervisao.py` (`acervo_sem_quadro`, `_recortes_do_perfil`, espécie `UX_046`) | `tests/integration/supervisao/test_sinal_do_acervo_sem_quadro.py` |
| **FR-332** | `interface/templates/interface/ocupacao.html`, `convocacao.html`, `ocupacao/application/emissao.py`, `interface/supervisao.py` (`destino_de`) | `tests/integration/supervisao/test_sinal_do_acervo_sem_quadro.py`, `tests/unit/editais/test_invariantes_da_declaracao_unica.py` |
| **FR-333** | ausência de migration e de degrau; `editais/domain/validation.py` (nada reescreve conteúdo) | `tests/integration/editais/test_acervo_sem_quadro_continua_retificavel.py`, `tests/unit/editais/test_invariantes_da_declaracao_unica.py` |
| **FR-334** | `ocupacao/application/emissao.py` (`effective_version` no instante do ato, efeitos congelados) | `tests/integration/ocupacao/test_acervo_ganha_quantidade_por_ato.py` |
| **FR-335** | `editais/domain/validation.py` (`vacancy_sum_mismatch` com a frase do Perfil sem lista reservada, `_acervo_sem_quadro`) | `tests/integration/editais/test_acervo_sem_quadro_continua_retificavel.py` |
| **FR-336** | `publicacoes/application/retificacoes.py` (`advertencias_do_ato`), `interface/templates/interface/retificacao_confirmar.html` | `tests/integration/editais/test_acervo_sem_quadro_continua_retificavel.py` |
| **FR-337** | nenhum campo novo no conteúdo publicado; `editais/domain/mutabilidade.py` inalterado | `tests/contract/test_contrato_governa_a_retificacao.py`, `tests/contract/test_mutabilidade.py` |

### A demonstração

| Requisito | Implementação | Verificação |
|---|---|---|
| **FR-338** | `processos/management/commands/seed_demo.py` (`perfis`, `perfil_de_sorteio`, `_retificar`) | `tests/integration/test_seed_demo.py` |
| **FR-339** | `processos/management/commands/seed_demo.py` (DOC-INFO reparte, TEC-LAB deriva, TEC-EAD reparte) | `tests/integration/test_seed_demo.py` |

### O corte

| Requisito | Implementação | Verificação |
|---|---|---|
| **FR-340** | ausência de caminho: nenhuma tela desta feature atribui pessoa a linha | `tests/unit/editais/test_invariantes_da_declaracao_unica.py` |

## Requisitos de apresentação

| Requisito | Implementação | Verificação |
|---|---|---|
| **UX-040** | `interface/templates/interface/_perfil.html`, `_linha_do_quadro.html` | `tests/interface/test_compor_quadro.py`, `tests/acceptance/test_us1_declaracao_unica_de_vagas.py` |
| **UX-041** | `interface/templates/interface/_secao_do_quadro.html` (`<p class="explicacao">`), `base.html` (`.explicacao`) | `tests/interface/test_compor_quadro.py` |
| **UX-042** | `interface/templates/interface/_linha_do_quadro.html` (`<span class="ajuda">`), `base.html` (`.ajuda`) | `tests/interface/test_compor_quadro.py` |
| **UX-043** | `interface/revisao.py` (`_vagas_e_quadro`) | `tests/interface/test_advertencias_do_quadro.py` |
| **UX-044** | `editais/domain/validation.py` (as duas advertências dizem os números) | `tests/interface/test_advertencias_do_quadro.py` |
| **UX-045** | `interface/templates/interface/ocupacao.html`, `convocacao.html` | `tests/interface/test_ocupacao.py`, `tests/unit/editais/test_invariantes_da_declaracao_unica.py` |
| **UX-046** | `interface/supervisao.py` (espécie, detecção, rótulo e destino) | `tests/integration/supervisao/test_sinal_do_acervo_sem_quadro.py`, `tests/unit/interface/test_supervisao.py` |

## Critérios de sucesso

| Critério | Onde é demonstrado |
|---|---|
| **SC-104** | `tests/acceptance/test_us1_declaracao_unica_de_vagas.py` — o percurso `A1`–`A5` declara a quantidade uma vez |
| **SC-105** | `tests/acceptance/test_us1_declaracao_unica_de_vagas.py`, `tests/integration/editais/test_derivacao_persistida.py` |
| **SC-106** | `tests/interface/test_advertencias_do_quadro.py` — a advertência em números, na Revisão e na confirmação |
| **SC-107** | `tests/integration/test_seed_demo.py` |
| **SC-108** | `tests/integration/supervisao/test_sinal_do_acervo_sem_quadro.py` |
| **SC-109** | `tests/integration/ocupacao/test_acervo_ganha_quantidade_por_ato.py` — o ciclo do acervo numa sessão |
| **SC-110** | `tests/integration/editais/test_acervo_sem_quadro_continua_retificavel.py` — nada publicado é reescrito |
| **SC-111** | `tests/acceptance/test_us1_declaracao_unica_de_vagas.py` — o percurso não exige saber que existiram dois campos |
