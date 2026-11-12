# Rastreabilidade: A formalização na jornada guiada do Edital (153)

Cada requisito → as tarefas que o implementam → os testes que o verificam. Caminhos relativos a
`backend/tests/`. Abreviações:

- `pa` = `integration/formalizacao/test_passagem.py`: a derivação, sem tela
- `ps` = `interface/test_passagem_ao_setor.py`: o Centro, o bloco, as duas confirmações e o relatório
- `rp` = `performance/test_relatorio.py`, `performance/test_confirmacao_do_encerramento.py` e
  `performance/test_confirmacao_do_encerramento_do_processo.py`: as consultas
- `nav` = a verificação no navegador, com o cenário C12 (ver `verificacao.md`)

## Requisitos funcionais

| Requisito | Tarefas | Testes |
|---|---|---|
| FR-6100 (publicado ou encerrado) | T002 | `pa::test_o_edital_cancelado_nao_tem_passagem` |
| FR-6101 (pessoa apta pelo seletor da `117`) | T002 | `pa::test_sem_definicao_todas_as_aptas_esperam_a_definicao` |
| FR-6102 (disponibilizada: incluída em pacote) | T002 | `pa::test_a_pessoa_incluida_num_pacote_esta_disponibilizada`; `pa::test_definicao_nova_nao_reabre_quem_ja_foi_disponibilizado` |
| FR-6103 (definição gravada, inclusive vazia) | T002 | `pa::test_definicao_sem_documento_e_decisao` |
| FR-6104 (sem documento incluído) | T001, T002 | `pa::test_definicao_sem_documento_e_decisao` |
| FR-6105 (sem leitura de arquivo) | T002 | leitura de `formalizacao/application/passagem.py`, que lê só o seletor da `117` (ele também não lê arquivo) e os registros; `rp` |
| FR-6106 (uma causa por pessoa, na ordem) | T002, T003 | `pa::test_sem_definicao_todas_as_aptas_esperam_a_definicao`; `ps::test_sem_definicao_a_designacao_nao_aparece` |
| FR-6107 (designação efetiva) | T002 | `pa::test_designacao_de_quem_nao_tem_o_papel_nao_conta`; `pa::test_designacao_de_pessoa_suspensa_nao_conta`; `pa::test_designacao_de_outro_perfil_nao_cobre`; `pa::test_designacao_do_perfil_cobre` |
| FR-6108 (três providências, seus responsáveis) | T003 | `ps::test_sem_definicao_a_providencia_e_de_quem_conduz_com_o_link`; `ps::test_sem_designacao_a_providencia_e_de_quem_administra_os_acessos`; `ps::test_com_definicao_e_designacao_falta_o_setor_e_o_bloco_diz_cada_passo` |
| FR-6109 (Pendente, sem prazo) | T003 | os mesmos três de `ps`: as providências aparecem entre as ações, e não na espera |
| FR-6110 (a razão com a contagem) | T003 | `ps::test_sem_definicao_a_providencia_e_de_quem_conduz_com_o_link`; `ps::test_sem_designacao_a_providencia_e_de_quem_administra_os_acessos` |
| FR-6111 (sua só para quem pratica; link só aí) | T003 | `ps::test_quem_nao_conduz_le_o_papel_e_nao_recebe_o_link`; `ps::test_sem_designacao_a_providencia_e_de_quem_administra_os_acessos`; `ps::test_sem_definicao_a_designacao_nao_aparece` |
| FR-6112 (o Centro não se abre ao setor) | T003 | leitura de `_providencias_da_formalizacao`: nenhuma porta nova; a do detalhe não muda |
| FR-6113 (ninguém com o papel) | T003 | `ps::test_sem_designacao_a_providencia_e_de_quem_administra_os_acessos` |
| FR-6114 (os papéis novos no fim da ordem) | T003 | leitura de `andamento.ORDEM_DOS_PAPEIS`, que `providencias.ordenar` lê |
| FR-6115 (na fase Conclusão) | T004 | `ps::test_com_definicao_e_designacao_falta_o_setor_e_o_bloco_diz_cada_passo` ("(Conclusão)"); `unit/interface/test_centro_composicao.py` (toda natureza tem fase) |
| FR-6116 (só contagens) | T003, T004 | `ps::test_nada_nomeia_pessoa_nem_diz_que_o_setor_recebeu` |
| FR-6117 (conta em "Onde estamos"; continua no encerrado) | T003 | `ps::test_no_edital_encerrado_a_providencia_continua` |
| FR-6118 (o bloco e as linhas) | T004 | `ps::test_com_definicao_e_designacao_falta_o_setor_e_o_bloco_diz_cada_passo`; `ps::test_o_bloco_sem_definicao_so_oferece_a_primeira_linha` |
| FR-6119 (o ato da linha só a quem o pratica) | T004 | `ps::test_o_bloco_sem_definicao_so_oferece_a_primeira_linha` |
| FR-6120 (a frase do limite) | T004 | `ps::test_com_definicao_e_designacao_falta_o_setor_e_o_bloco_diz_cada_passo` |
| FR-6121 (tudo disponibilizado; definição vazia) | T004 | `ps::test_com_todas_disponibilizadas_o_bloco_diz_o_ultimo_pacote`; `ps::test_a_definicao_gravada_sem_documento_encerra_a_providencia` |
| FR-6122 (o andamento da Conclusão não muda) | T004 | `_fase_conclusao` intocada; os testes da `136` (`interface/test_centro_*.py`, `unit/interface/test_centro_composicao.py`) passam |
| FR-6123 (sem "encaminhado", "entregue", "recebido") | T004, T005 | `ps::test_nada_nomeia_pessoa_nem_diz_que_o_setor_recebeu` |
| FR-6124 (a advertência no encerrar) | T006 | `ps::test_a_confirmacao_de_encerrar_adverte_com_o_caminho`; `interface/test_advertencia_do_encerramento_do_processo.py::test_as_frases_sao_as_da_confirmacao_do_edital_e_do_relatorio` (a frase é a do relatório) |
| FR-6125 (a causa) | T005, T006 | `ps::test_a_confirmacao_de_encerrar_adverte_com_o_caminho`; `ps::test_o_relatorio_traz_a_mesma_pendencia` |
| FR-6126 (o caminho ou a quem pedir) | T006 | `ps::test_a_confirmacao_de_encerrar_adverte_com_o_caminho`; `ps::test_a_quem_nao_pode_definir_a_advertencia_diz_a_quem_pedir` |
| FR-6127 (no relatório) | T005 | `ps::test_o_relatorio_traz_a_mesma_pendencia`; `integration/relatorio/*` com o cenário que dispensa a formalização |
| FR-6128 (no "Encerrar Processo") | T006 | `ps::test_o_encerramento_do_processo_adverte_pela_mesma_regra` |
| FR-6129 (nada gravado, nenhuma regra muda) | T002 a T006 | `make check` (sem migration); o diff não toca comando nem modelo |
| FR-6130 (sem pessoa apta, nada) | T002, T004 | `pa::test_sem_pessoa_apta_nao_ha_passagem`; `ps::test_sem_pessoa_apta_nao_ha_bloco_nem_providencia` |

## Requisitos de experiência

| Requisito | Tarefas | Verificação |
|---|---|---|
| UX-560 (linguagem simples, 375 px) | T004 | `nav`, a 375 px |
| UX-561 (estado em texto) | T004 | `ps::test_com_definicao_e_designacao_falta_o_setor_e_o_bloco_diz_cada_passo` ("Feito ·", "Em aberto ·") |
| UX-562 (o link leva aos documentos) | T003 | `ps::test_sem_definicao_a_providencia_e_de_quem_conduz_com_o_link` (`#documentos-definidos`) |
| UX-563 (o botão de hoje fica) | T004 | o template da administração não muda; `nav` |

## Critérios de sucesso

| Critério | Verificação |
|---|---|
| SC-1950 | `nav`: a presidência acha a definição pelo "O que fazer agora", no C12 com duas pessoas aptas |
| SC-1951 | `pa` (a soma em `test_sem_definicao_todas_as_aptas_esperam_a_definicao` e `test_a_pessoa_incluida_num_pacote_esta_disponibilizada`) e as combinações de `pa` |
| SC-1952 | `ps::test_o_relatorio_traz_a_mesma_pendencia` e `ps::test_a_confirmacao_de_encerrar_adverte_com_o_caminho` contam 2, como o Centro |
| SC-1953 | `ps::test_quem_nao_conduz_le_o_papel_e_nao_recebe_o_link`; `ps::test_sem_designacao_a_providencia_e_de_quem_administra_os_acessos`; `ps::test_a_quem_nao_pode_definir_a_advertencia_diz_a_quem_pedir` |
| SC-1954 | `ps::test_nada_nomeia_pessoa_nem_diz_que_o_setor_recebeu` |
| SC-1955 | `rp`: o mesmo número de consultas com 1 e com 10 vezes as inscrições |
| SC-1956 | `ps::test_no_edital_encerrado_a_providencia_continua`; `ps::test_com_todas_disponibilizadas_o_bloco_diz_o_ultimo_pacote` |
