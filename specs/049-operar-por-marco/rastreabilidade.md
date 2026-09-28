# Rastreabilidade — 049 · Operar o resultado por marco, e não por recorte

**Frase que governa**: *um gesto humano processa os N recortes de um marco; o ato continua por
recorte, com autor; e o que foi feito, o que foi recusado e o que falta ficam à vista.*

**Verificação final** (28/09/2026, sobre a `main` em `28b3815b`): `make DB_NAME=ps049 lint check
test-pg` — `ruff check` e `ruff format --check` limpos, `manage.py check` sem problemas,
`makemigrations --check` sem mudança —; **8465 passando e 11 pulados**, zero falhas. Os 11 pulados
são os deliberados de sempre; os 101 casos a mais são os 37 desta feature e os parametrizados que
ela alcança. A primeira rodada completa pegou duas falhas que os testes da feature não viam — uma
classe sem regra na folha e a pasta fora da tabela de incrementos do README —, corrigidas antes
desta.

Cada linha aponta o lugar do código e o teste **pelo nome**. Os testes estão todos em
`backend/tests/interface/test_conducao_do_marco.py`, salvo onde outro arquivo é dito. Onde a linha
diz *"leitura do diff"*, a promessa é negativa — algo que não pode ter acontecido — e se confere
lendo a mudança.

---

## 1. Requisitos

| `FR-` | Onde entrou | O que o prende |
|---|---|---|
| **FR-810** | `interface/conducao_do_marco.py::indicador_do_marco` — uma linha por recorte, uma célula por operação | `test_a_tela_do_marco_mostra_cada_recorte_em_cada_operacao` |
| **FR-811** | `_celula_da_ordem`, `_celula_do_corte`, `_celula_da_apuracao`, `_celula_da_publicacao`: *feito*, *obsoleto*, *falta*, *não se aplica*; a natureza na publicação; *o público lê um ato anterior* | `test_ordem_obsoleta_nao_e_contada_como_feita`, `test_o_publico_lendo_um_ato_anterior_aparece_como_obsoleto`, `test_um_gesto_publica_um_resultado_por_recorte` (a nota da natureza, no percurso) |
| **FR-812** | `recortes_do_marco` lê `editais/domain/recortes.py::recortes_do_perfil`; nenhuma lista própria (leitura do diff) | `test_a_tela_do_marco_mostra_cada_recorte_em_cada_operacao` (rótulos e ordem da derivação) |
| **FR-813** | `marco_publicado` lê a versão vigente; `views._marco_do_edital` recusa o marco que ela não publica | `test_marco_que_a_norma_nao_publica_e_404`, `test_recorte_acrescentado_aparece_como_falta` |
| **FR-814** | `_totais`: *completo* é nenhum em falta e nenhum obsoleto; *não se aplica* sai da conta | `test_ordem_obsoleta_nao_e_contada_como_feita` (`ordem 0 de 3`), `test_sem_ordem_nao_ha_o_que_publicar_e_isso_conta_como_falta` |
| **FR-815** | `_celula_da_ordem`: marco de sorteio leva a `interface:sorteio`; o estado vem de `estado_do_marco`, que lê o ato sorteado | `test_marco_de_sorteio_nao_oferece_ordenar` |
| **FR-816** | `alcance`: *fora* para o recorte que já tem o ato; motivo vazio em `praticar` | `test_recorte_com_ordem_fica_de_fora_com_a_razao`, `test_corte_sem_ordem_e_impedido_e_com_faixa_fica_de_fora`, `test_ja_publicado_na_natureza_fica_de_fora`, `test_depois_de_parar_no_meio_a_conferencia_so_traz_o_que_falta` |
| **FR-817** | `views._gestos_oferecidos`; `_alcance_da_ordem` e `_alcance_do_corte` recusam o gesto inteiro | `test_marco_de_sorteio_nao_oferece_ordenar` |
| **FR-818** | `views.gesto_do_marco` sem `confirmar` compõe `marco_conferir.html`, sem gravar | `test_a_conferencia_declara_o_alcance_e_nao_grava_nada`, `test_recorte_que_o_calculo_recusa_e_impedido`, `test_recorte_sem_quadro_e_impedido_na_apuracao` |
| **FR-819** | `verbo_da_confirmacao`; o formulário só existe com recorte a praticar | `test_a_conferencia_declara_o_alcance_e_nao_grava_nada`, `test_ja_publicado_na_natureza_fica_de_fora` |
| **FR-820** | `_ordenar`, `_cortar`, `_apurar`, `_publicar` chamam `emitir_ordem`, `emitir_corte`, `emitir_apuracao`, `publicar_resultado` — nenhum caminho de gravação novo (leitura do diff) | `test_um_gesto_emite_uma_ordem_por_recorte_com_autor_e_rastro`, `test_um_gesto_emite_uma_faixa_por_recorte`, `test_um_gesto_apura_cada_recorte`, `test_um_gesto_publica_um_resultado_por_recorte` |
| **FR-821** | a assinatura de cada recorte viaja no formulário e é conferida pelo comando; a da apuração, por `_apurar` sob a trava do Processo | `test_recusa_parcial_preserva_os_feitos`, `test_apuracao_que_mudou_desde_a_conferencia_e_recusada` |
| **FR-822** | `chave_do_recorte` deriva a chave de idempotência da chave da conferência; `_apurar` não reconfere a repetição | `test_repetir_o_envio_nao_pratica_de_novo`, `test_repetir_a_apuracao_nao_recusa_nem_apura_de_novo` |
| **FR-823** | `praticar`: uma transação por recorte; `DomainError` vira *recusado* e o laço segue | `test_recusa_parcial_preserva_os_feitos`, `test_apuracao_que_mudou_desde_a_conferencia_e_recusada` |
| **FR-824** | o desfecho vai para a sessão e aparece na `marco.html`, com o caminho para o ato ou para o recorte | `test_recusa_parcial_preserva_os_feitos`, `test_um_gesto_emite_uma_ordem_por_recorte_com_autor_e_rastro` |
| **FR-825** | `correlacao_do_gesto` → `correlation_id` de cada `RegistroAuditoria` | `test_um_gesto_emite_uma_ordem_por_recorte_com_autor_e_rastro` |
| **FR-826** | `_alcance_da_publicacao`: natureza e autoridade uma vez; *fora* o já divulgado na natureza e o preliminar sobre definitivo | `test_um_gesto_publica_um_resultado_por_recorte`, `test_ja_publicado_na_natureza_fica_de_fora`, `test_preliminar_depois_da_definitiva_fica_de_fora`, `test_sem_natureza_a_conferencia_nao_e_composta` |
| **FR-827** | `exige_declaracao`; o campo na conferência; `_publicar` a transporta a cada `publicar_resultado` | `test_a_definitiva_pede_a_declaracao_uma_vez_e_a_grava_em_cada_uma` |
| **FR-828** | `aferir_publicabilidade(..., natureza=...)` por recorte, como a prévia; o impedimento vai para *Impedidos* | `test_recorte_sem_ordem_e_impedido_na_publicacao` |
| **FR-829** | `gesto_do_marco` passa por `_edital_para_publicar` ou por `_edital_para_classificar(somente_gestao=True)`; `_gestos_oferecidos`; `frase_do_aviso` | `test_quem_gere_nao_ve_publicar_e_le_a_quem_pedir`, `test_quem_publica_nao_ve_os_gestos_da_comissao` |
| **FR-830** | a porta `_marco_para_conduzir`: classificar, auditar **ou** publicar | `test_quem_so_audita_ve_o_indicador_e_nenhum_gesto`, `test_quem_nao_alcanca_nenhuma_tela_do_marco_e_recusado`; `tests/test_gramatica_das_portas.py` (a porta na lista `PORTAS`) |
| **FR-831** | nenhuma tela por recorte foi alterada (leitura do diff) | a suíte existente das telas por recorte, inteira verde |

## 2. Critérios de sucesso

| `SC-` | O que o prova |
|---|---|
| **SC-300** | o percurso do [quickstart](quickstart.md): num marco de 3 recortes, ordenar, cortar, apurar e publicar custaram **4 confirmações**, contra 12 recorte a recorte, e uma tela no lugar de ~12 |
| **SC-301** | `test_a_tela_do_marco_mostra_cada_recorte_em_cada_operacao`, `test_a_pagina_do_edital_resume_cada_marco_e_leva_a_ele` |
| **SC-302** | `test_recusa_parcial_preserva_os_feitos`, `test_apuracao_que_mudou_desde_a_conferencia_e_recusada` |
| **SC-303** | `test_recorte_forjado_e_404_antes_de_praticar_qualquer_um`, `test_repetir_o_envio_nao_pratica_de_novo`, `test_repetir_a_apuracao_nao_recusa_nem_apura_de_novo` |
| **SC-304** | `test_um_gesto_emite_uma_ordem_por_recorte_com_autor_e_rastro` (`emitido_por`), `test_um_gesto_publica_um_resultado_por_recorte` (`publicado_por`, signatário, documento) |
| **SC-305** | `test_o_resumo_nao_cresce_com_o_numero_de_marcos` (4 consultas com 1 marco e com 16) |

## 3. Experiência

| `UX-` | O que o prova |
|---|---|
| **UX-090** | `test_a_pagina_do_edital_resume_cada_marco_e_leva_a_ele`; `tests/interface/test_destinos_do_edital.py` (o destino novo na lista de cada ator) |
| **UX-091** | `test_a_tela_do_marco_mostra_cada_recorte_em_cada_operacao`, `test_marco_de_sorteio_nao_oferece_ordenar` (célula leva à tela dona) |
| **UX-092** | `test_a_conferencia_declara_o_alcance_e_nao_grava_nada`, `test_recorte_com_ordem_fica_de_fora_com_a_razao`, `test_recorte_que_o_calculo_recusa_e_impedido` |
| **UX-093** | `test_recusa_parcial_preserva_os_feitos` (contagem primeiro, recusados antes dos feitos) |

## 4. Decisões

| | Onde se cumpre |
|---|---|
| **D-001** | a rota pende do marco; `recortes_do_marco` é o Perfil dele |
| **D-002** | `alcance` põe *fora* o recorte com ato; `praticar` passa motivo vazio |
| **D-003** | `_alcance_da_ordem` e `_alcance_da_publicacao` incluem o recorte vazio, com a nota; `test_recorte_vazio_entra_declarado_e_recebe_a_ordem_vazia`, `test_o_recorte_em_que_ninguem_concorreu_esta_feito_e_diz_por_que` |
| **D-004** | `publicar_resultado` por recorte, um documento cada; `test_um_gesto_publica_um_resultado_por_recorte` |
| **D-005** | `interface:marco` e `interface:gesto-do-marco`; as telas por recorte intactas |
