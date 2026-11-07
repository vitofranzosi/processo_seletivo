# Rastreabilidade: Cinco ajustes de leitura dos Documentos Exigidos (132)

Cada requisito → as tarefas que o implementam → os testes que o verificam. Caminhos relativos a
`backend/tests/`. Abreviações:

- `ad` = `interface/test_ajustes_dos_documentos.py` — a Revisão, o somente leitura e a ajuda
- `an` = `integration/portal/test_anuncio_dos_documentos.py` — a página pública
- `fp` = `unit/convocacao/test_fundamento_das_pendencias.py` — o fundamento
- `sl` = `javascript/somente-leitura.test.js` — a regra do script da D-004, por `test_javascript.py`
- `vf` = [verificacao.md](verificacao.md)

A faixa abre em **FR-4501** e **SC-1401**; foram gastos FR-4501 a FR-4516 e SC-1401 a SC-1407.

## Requisitos funcionais

| Requisito | Tarefas | Testes |
|---|---|---|
| FR-4501 — dois blocos por momento, com a contagem e a volta à Inscrição | T001 | `ad::test_a_revisao_separa_os_documentos_por_momento`, `ad::test_a_tela_da_revisao_mostra_os_dois_blocos_com_a_contagem` |
| FR-4502 — o da convocação só quando há; o da inscrição sempre | T001 | `ad::test_sem_documento_da_convocacao_a_revisao_tem_um_bloco_so` |
| FR-4503 — sem a linha "Pedido"; as demais e o número continuam | T001, T002 | `ad::test_o_item_perde_a_linha_pedido_e_guarda_as_demais`, `ad::test_a_revisao_separa_os_documentos_por_momento`; `unit/interface/test_revisao.py::test_a_conferencia_mostra_o_documento_exigido_e_de_quem` (revisto: o título do bloco) |
| FR-4504 — todo campo desabilitado nas cinco etapas | T003, T004, T005 | `ad::test_fora_de_elaboracao_nenhum_campo_aceita_digitacao` (cinco etapas), `ad::test_sem_permissao_de_elaborar_tambem_e_leitura` |
| FR-4505 — sem setas, lixeira, acrescentar, remover, aplicar, duplicar | T006 | `ad::test_fora_de_elaboracao_a_lista_nao_oferece_mudar` (cinco etapas) |
| FR-4506 — Voltar e Avançar por link | T007 | `ad::test_fora_de_elaboracao_avancar_e_link` (sete etapas) |
| FR-4507 — simular e conferir na Caixa continuam, com os valores do cartão | T005, T008 | `ad::test_a_classificacao_somente_leitura_ainda_simula`; `sl` (cinco casos); o navegador em `vf` |
| FR-4508 — a recusa do servidor continua | — | `ad::test_a_recusa_do_servidor_continua` |
| FR-4509 — a composição editável não muda | T003 | `ad::test_a_composicao_editavel_nao_muda` (três etapas); a suíte da composição, inalterada |
| FR-4510 — os quatro itens na ajuda dos documentos | T010 | `ad::test_a_ajuda_dos_documentos_explica_momento_aproveitamento_e_obrigatoriedade` |
| FR-4511 — a frase do campo, palavra por palavra | T010 | o mesmo caso, comparando com a descrição de cada campo |
| FR-4512 — o cartão sem ajuda nova | T011 | `ad::test_o_cartao_do_documento_nao_ganha_ajuda`; `interface/test_medida_dos_campos.py` |
| FR-4513 — a conta dos obrigatórios a todos, e o resumo que a diz | T012, T013 | `an::test_a_conta_e_a_dos_obrigatorios_a_todos_na_inscricao`, `an::test_o_resumo_diz_o_criterio_da_conta`; `integration/portal/test_detalhe_selecao.py` (três casos revistos: a frase do resumo) |
| FR-4514 — "(facultativo)" em todo grupo | T012, T013 | `an::test_todo_facultativo_leva_a_marca_e_o_obrigatorio_nao` |
| FR-4515 — o resumo não diz zero | T013 | `an::test_sem_obrigatorio_a_todos_o_resumo_nao_diz_zero`, `an::test_so_a_convocacao_pede_e_o_resumo_diz_isso` |
| FR-4516 — o fundamento sem ".." | T015, T016 | `fp` (seis casos); `integration/convocacao/test_documentos_da_convocacao.py::test_o_fundamento_do_indeferimento_vem_das_pendencias` (revisto: o motivo sem o ponto) |

## Critérios de sucesso

| Critério | Como se verifica |
|---|---|
| SC-1401 | `ad::test_a_revisao_separa_os_documentos_por_momento` |
| SC-1402 | `ad::test_fora_de_elaboracao_nenhum_campo_aceita_digitacao`, `ad::test_fora_de_elaboracao_a_lista_nao_oferece_mudar`, `ad::test_fora_de_elaboracao_avancar_e_link` |
| SC-1403 | `ad::test_a_classificacao_somente_leitura_ainda_simula`; no navegador, em `vf` |
| SC-1404 | `ad::test_a_ajuda_dos_documentos_explica_momento_aproveitamento_e_obrigatoriedade`, `ad::test_o_cartao_do_documento_nao_ganha_ajuda` |
| SC-1405 | `an::test_a_conta_e_a_dos_obrigatorios_a_todos_na_inscricao`, `an::test_todo_facultativo_leva_a_marca_e_o_obrigatorio_nao` |
| SC-1406 | `fp::test_o_ponto_final_do_motivo_cede_a_pontuacao_da_frase`; a tela, em `vf` |
| SC-1407 | [capturas/](capturas/), descritas em `vf` — sem teste automático |

## Decisões

D-001 a D-008 estão na [spec](spec.md). Cada uma é citada na tarefa que a aplica.
