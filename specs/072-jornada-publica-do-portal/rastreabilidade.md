# Rastreabilidade — 072

Caminhos de teste relativos a `backend/tests/`. "Navegador" é a verificação registrada em
[verificacao.md](verificacao.md); "Humana" é a validação que o agente não faz.

## Encontrar

| Requisito | Onde é provado |
|---|---|
| FR-1600 a FR-1603 | `integration/portal/test_consulta_da_vitrine.py` (grupo recolhido, `open` com filtro, busca fora); `interface/test_acessibilidade_do_portal.py` (`test_os_filtros_recolhidos_sao_um_controle_nativo_com_nome`); navegador (tela larga, sem script) |
| FR-1604 a FR-1606 | `integration/portal/test_vitrine.py` (título do Edital, Processo e sigla como apoio, número não repetido) |
| FR-1607 a FR-1609 | `portal/test_oferta_e_teto.py`; `integration/portal/test_vitrine.py` (oferta por Perfil, lugares, teto, sem lugar, sem quantidade) |
| FR-1610 | `portal/test_oferta_e_teto.py` (o que casa vem primeiro); `integration/portal/test_consulta_da_vitrine.py` (busca pelo lugar) |
| FR-1611 a FR-1613 | `integration/portal/test_vitrine.py` (título, aba, abertas agora); `integration/portal/test_consulta_da_vitrine.py` (estado vazio numa frase) |
| FR-1614 | `integration/portal/test_vitrine.py` (`test_os_blocos_do_cartao_seguem_a_mesma_ordem`) |

## Começar

| Requisito | Onde é provado |
|---|---|
| FR-1615, FR-1616 | `integration/portal/test_detalhe_selecao.py` (resumo com âncoras, ação por recebimento, teto de 5) |
| FR-1617 | `interface/test_acessibilidade_do_portal.py` (`test_a_vaga_indicada_nao_depende_so_de_cor`); navegador |
| FR-1618 | `integration/portal/test_detalhe_selecao.py` (`test_sem_consulta_a_volta_diz_todas_as_selecoes`, `test_a_volta_preserva_a_consulta_e_so_ela`) |
| FR-1619 a FR-1621 | `integration/portal/test_contexto_do_acesso.py` |
| FR-1622 a FR-1625 | `acceptance/portal/test_jornada_publica.py` |

## Preparar

| Requisito | Onde é provado |
|---|---|
| FR-1626 | `integration/portal/test_detalhe_selecao.py` (`test_o_requerimento_e_anunciado_so_quando_e_pedido_na_inscricao`) |
| FR-1627 | `integration/portal/test_contexto_do_acesso.py` (texto presente); **Humana** — validação do texto ([validacao-humana.md](validacao-humana.md), §2) |
| FR-1628 | `integration/portal/test_detalhe_selecao.py` (documentos e teto continuam) |

## Acompanhar

| Requisito | Onde é provado |
|---|---|
| FR-1629 a FR-1633 | `portal/test_resumo_do_acompanhamento.py`; `portal/test_acompanhamento_na_vitrine.py` |
| FR-1634, FR-1635 | `portal/test_acompanhamento_na_vitrine.py` (convite, cartão = página, mesmo número de consultas) |
| FR-1636 | `portal/test_vocabulario_das_telas_publicas.py`; o template só escreve fatos datados |

## Transversais

| Requisito | Onde é provado |
|---|---|
| FR-1637 | `integration/portal/test_leitura_sem_escrita.py` (`test_com_resultado_publicado_a_vitrine_e_a_selecao_continuam_sem_escrita`) |
| FR-1638 | `portal/test_vocabulario_das_telas_publicas.py` |
| FR-1639, FR-1640 | `interface/test_acessibilidade_do_portal.py`; navegador (larguras, teclado) |

## Critérios de sucesso

| Critério | Onde é provado |
|---|---|
| SC-600, SC-601 | navegador — script de medição da auditoria contra o seed |
| SC-602 | `integration/portal/test_contexto_do_acesso.py` |
| SC-603 | `acceptance/portal/test_jornada_publica.py` (`test_identidade_nova_vai_da_vaga_ao_rascunho_pelos_formularios`) |
| SC-604 | `portal/test_resumo_do_acompanhamento.py`; `portal/test_acompanhamento_na_vitrine.py` |
| SC-605 | **Humana** — percurso conduzido ([validacao-humana.md](validacao-humana.md), §1) — **pendente** |
| SC-606 | `integration/portal/test_leitura_sem_escrita.py` |
| SC-607 | navegador — larguras de 320 a 1440 |
