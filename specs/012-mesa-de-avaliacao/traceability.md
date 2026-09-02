# Rastreabilidade — 012: Mesa de Avaliação

**Feature**: [spec.md](./spec.md) | **Tarefas**: [tasks.md](./tasks.md) | **Data**: 2026-09-02

O princípio V da Constituição exige que requisito crítico seja rastreável entre especificação,
plano, tarefa, implementação e teste. Esta é a ponta final: para cada requisito, **o teste que
falharia se ele fosse quebrado** — e não o teste que passa perto.

## Cobertura

| | |
|---|---:|
| Requisitos funcionais (FR) | 106 |
| Critérios de sucesso (SC) | 31 |
| Edge cases (EC) | 20 |
| Testes na suíte, ao fim da 012 | 1858 |
| Verificações do quickstart, executadas em 2026-09-02 | 34, sem divergência |

## Onde procurar

Os testes citam o identificador na docstring ou no comentário, então a busca é direta:

```bash
cd backend && grep -rn "FR-092" tests/
```

| Grupo | Onde vive |
|---|---|
| O incremento normativo e a forma publicada | `tests/contract/test_forma_publicada.py`, `tests/integration/editais/test_etapa_declara_avaliacoes.py` |
| A elevação de versão canônica | `tests/unit/avaliacoes/test_elevacao.py`, `tests/integration/publicacoes/test_elevacao_de_versao.py` |
| A leitura da ausência | `tests/unit/avaliacoes/test_previsao.py` |
| A precondição em duas grafias | `tests/unit/avaliacoes/test_precondicao_de_grafia.py` |
| As garantias de banco | `tests/integration/avaliacoes/test_constraints.py` |
| Distribuição, teto e lote | `tests/integration/avaliacoes/test_distribuicao.py`, `test_idempotencia_distribuicao.py` |
| A Mesa e a revogação computada | `tests/interface/test_mesa.py`, `tests/authorization/test_mesa.py`, `tests/integration/avaliacoes/test_revogacao_computada.py` |
| O documento como instrumento de trabalho | `tests/authorization/test_documento_da_mesa.py`, `tests/integration/avaliacoes/test_documento.py` |
| A avaliação | `tests/integration/avaliacoes/test_avaliacao.py`, `test_versao_da_avaliacao.py` |
| Impedimento, reabertura e conjunto elegível | `tests/integration/avaliacoes/test_impedimento.py`, `test_reabertura.py`, `test_conjunto_elegivel.py` |
| Concorrência | `test_primeira_gravacao_concorrente.py`, `test_corrida_conclusao_e_remocao.py` |
| Trilha | `tests/integration/avaliacoes/test_trilha_completa.py`, `tests/interface/test_trilha_da_012.py` |
| Preservação consultável | `tests/interface/test_conclusoes_preservadas.py` |
| Escala | `tests/performance/test_escala_da_mesa.py`, `tests/authorization/test_listagem_em_lote.py` |
| Não-regressão | `tests/integration/comissoes/test_011_intocada.py`, `tests/integration/publicacoes/test_retificacao_intocada.py` |

## Os requisitos que sustentam a feature

Nem todo requisito tem o mesmo peso. Estes são os que, se quebrarem, tornam a 012 outra coisa —
e cada um tem um teste que falha primeiro.

| Requisito | O que ele impede | Teste que falha |
|---|---|---|
| **FR-092** | que remover atribuição vire modo de escolher quais notas contam | `test_conjunto_elegivel.py::test_a_sequencia_que_fr_092_impede` |
| **FR-104** | o mesmo, por concorrência em vez de por decisão | `test_corrida_conclusao_e_remocao.py` |
| **FR-098** | que o incremento torne irretificável Edital já publicado | `test_elevacao_de_versao.py` (oito cenários) |
| **FR-100** | que a 012 mude o comportamento do pipeline de Retificação | `test_retificacao_intocada.py` |
| **FR-074** | segunda conclusão da mesma pessoa via remover-e-readicionar | `test_identidade_estavel.py`, `test_constraints.py` |
| **FR-099** | contornar impedimento saindo e voltando à comissão | `test_identidade_estavel.py` |
| **FR-096** | Avaliação que afirma obedecer a regra contra a qual não foi verificada | `test_versao_da_avaliacao.py` |
| **FR-069** | revogação desnormalizada, com custo por atribuição | `test_revogacao_computada.py`, `test_escala_da_mesa.py` |
| **FR-023** | negar a Etapa a quem a 011 concedeu | `tests/authorization/test_mesa.py` |
| **FR-055** | avaliador alcançando o acervo do Edital | `test_consulta_administrativa_intocada.py` |
| **FR-054** | trilha virando segunda fonte da avaliação | `test_trilha_da_avaliacao.py` |
| **FR-037** | a 012 produzir resultado | `tests/acceptance/test_mesa_de_avaliacao.py::test_a_vertical_nao_produz_resultado` |
| **FR-106** | confirmar um alcance e executar outro | `test_impedimento.py::test_o_ato_recusa_quando_o_alcance_mudou_desde_a_confirmacao` |
| **FR-091** | preservação que só o banco enxerga | `test_conclusoes_preservadas.py::test_o_que_foi_concluido_antes_da_reabertura_continua_legivel` |

## Requisitos sem teste, e por quê

Cinco. Nenhum deles é omissão.

| Requisito | Por que não há teste |
|---|---|
| **FR-017**, **FR-018**, **FR-019** | Proíbem construir distribuição automática. O que os sustenta é a ausência de código — `test_distribuicao.py::test_o_conjunto_que_nao_cabe_e_recusado_inteiro` chega perto, ao provar que o sistema **não escolhe**, mas o requisito em si é uma decisão de escopo. |
| **FR-057** | Retenção e descarte do acervo: gate institucional, registrado no quickstart. Não há código a testar, e inventar um prazo seria pior que não ter. |
| **FR-058** | Identidade institucional confiável: gate herdado da 011, também registrado. O que o sistema pode fazer — recusar o seletor em produção — já é testado em `tests/test_configuracao_producao.py`. |

## Os critérios de sucesso

| SC | Onde se demonstra |
|---|---|
| SC-001 distribuir em lote | `test_distribuicao.py`, quickstart E2 |
| SC-002 todas e somente as suas | `test_mesa.py::test_a_mesa_nao_mostra_inscricao_de_outro_avaliador` |
| SC-003 alocado sem atribuição | `tests/authorization/test_mesa.py`, quickstart E3 |
| SC-004 abre a dele e nenhuma outra | `test_documento_da_mesa.py` |
| SC-005 toda abertura registrada | `test_documento.py` |
| SC-006 rascunho e conclusão distintos | `test_avaliacao.py`, quickstart E5 |
| SC-007 pontuação fora do publicado | `test_avaliacao.py::test_pontuacao_acima_da_maxima_publicada_e_recusada` |
| SC-008 concluída imutável | `test_avaliacao.py::test_concluida_e_imutavel_para_o_avaliador` |
| SC-009 reabertura com motivo | `test_reabertura.py` |
| SC-010 remover alocação revoga | `tests/authorization/test_mesa.py` |
| SC-011 remover atribuição preserva | `test_impedimento.py::test_a_concluida_e_preservada_e_tornada_inelegivel` |
| SC-012 impedimento nomeia o motivo | `test_impedimento.py` |
| SC-013 não produz resultado | `test_mesa_de_avaliacao.py` |
| SC-014 mil sem mil interações | `test_escala_da_mesa.py` |
| SC-015 Mesa sem verificação por linha | `test_listagem_em_lote.py`, `test_escala_da_mesa.py` |
| SC-016 documento materializado declara | `test_etapa_declara_avaliacoes.py`, `pdf.py` |
| SC-017 as duas direções da fronteira | `test_consulta_administrativa_intocada.py` |
| SC-018 a versão da conclusão | `test_versao_da_avaliacao.py` |
| SC-019 excedente recusado | `test_distribuicao.py` |
| SC-020 a SC-023 impedimento e vaga | `test_impedimento.py` |
| SC-024 Retificação anunciada | `test_versao_da_avaliacao.py` |
| SC-025 a SC-028 conjunto elegível e reabertura | `test_conjunto_elegivel.py`, `test_reabertura.py` |
| SC-029 Edital anterior retificável | `test_elevacao_de_versao.py` |
| SC-030 resultado do lote declarado | `test_distribuicao.py`, `tests/interface/test_distribuicao.py` |
| SC-031 fora do período avisa | `test_avaliacao.py`, `mesa_inscricao.html` |

## Os edge cases

EC-001 a EC-020 têm teste, com três exceções deliberadas:

- **EC-006** (retirada de inscrição) não é alcançável: o estado não existe, e a 012 não o cria
  (D-006). O que existe é o registro da pergunta.
- **EC-009** (Etapa que declara duas e só tem um alocado) é estado válido e visível, coberto pela
  contagem de déficit de `test_distribuicao.py`; não há recusa a testar, porque não há recusa.
- **EC-010** (reabertura de avaliação já usada pela 013) depende da 013 existir. A 012 registra a
  pendência no gate.

## A revisão de `origin/main...f5bcaba`

Sete achados, cinco deles funcionais, todos encontrados por leitura do código depois de a Phase 8
fechar com a suíte verde. Vale registrar **por que a suíte não os pegou**, que é a parte útil.

| achado | por que passava despercebido | o teste que agora o prende |
|---|---|---|
| a trilha exigia presidência **e** auditoria | a fixture usava `["gestor", "auditor"]` — testava exatamente o usuário híbrido, o único que passava | `test_trilha_da_012.py::test_a_porta_da_trilha_e_a_presidencia_ou_a_auditoria` |
| a abertura de documento não nomeava a Etapa | o teste de FR-053 conferia a Etapa em atribuir e concluir, e não nos sete atos | `test_documento.py::test_cada_abertura_registra_ator_etapa_inscricao_e_requisito`, `test_trilha_da_012.py::test_a_trilha_de_uma_etapa_nao_mostra_a_abertura_feita_em_outra` |
| a paginação da trilha perdia registros | nenhum teste folheava a trilha; todos cabiam na primeira página | `test_trilha_da_012.py::test_a_paginacao_alcanca_todos_os_atos_do_filtro` |
| a preservação não era consultável | os testes liam o banco diretamente, e não a interface — a preservação existia, e ninguém a alcançava | `test_conclusoes_preservadas.py` (cinco cenários) |
| a confirmação do impedimento não era conferida | o teste chamava o comando direto, sem passar pelos dois passos da tela | `test_impedimento.py::test_o_ato_recusa_quando_o_alcance_mudou_desde_a_confirmacao` |
| identificador malformado virava 500 | nenhum teste digitava errado | `test_impedimento.py::test_identificador_malformado_e_recusa_de_formulario_nos_dois_passos` e os dois de filtro |
| a suíte em SQLite não fechava verde | a execução padrão do projeto é PostgreSQL, e os testes de corrida não estavam marcados | `postgresql_only` nos dois arquivos de corrida |

Os quatro primeiros têm em comum a mesma forma: **o teste exercitava justamente o caso que
escondia o defeito**. É o modo de falha que a contraprova por reversão pega e a leitura do
resultado verde não pega — e cada correção acima foi verificada assim, quebrando o conserto e
conferindo que o teste falha.

## A segunda rodada, sobre as próprias correções

Três achados, e os três sobre código que a primeira rodada ainda não tinha para ler.

| achado | consequência | o teste que agora o prende |
|---|---|---|
| a confirmação do impedimento aceitava envio **sem** alcance declarado | FR-106 desligável por quem monta o formulário — e um teste da própria suíte fazia exatamente esse envio | `test_impedimentos.py::test_confirmar_sem_declarar_o_alcance_refaz_a_confirmacao` |
| a página de conclusões preservadas não paginava | o maior acervo da feature — uma linha por conclusão, mais uma a cada reabertura — numa página só | `test_escala_da_mesa.py::test_as_conclusoes_preservadas_sao_paginadas_e_lidas_em_custo_constante` |
| a trilha resolvia os agregados por lista de identificadores | 43 mil caracteres de SQL, com mil atribuições, para montar vinte linhas | `test_escala_da_mesa.py::test_a_trilha_da_etapa_nao_carrega_a_etapa_inteira_para_montar_uma_pagina` |

O primeiro merece nota: **a suíte continha o ataque**. `test_a_tela_mostra_o_ato_e_o_motivo_ao_lado_da_inelegivel` postava `confirmar=1` sem a assinatura do alcance, e passava — o teste documentava como pular a confirmação. Ele agora percorre os dois passos, lendo o alcance da própria tela.

## O gate da 013

Os seis itens do §27 da spec, e onde cada um está demonstrado:

1. **Atribuição inequívoca** — `test_constraints.py`, `test_distribuicao.py`
2. **Avaliação com autoria, pontuação, parecer e instante** — `test_avaliacao.py`
3. **A versão que governou cada Avaliação** — `test_versao_da_avaliacao.py`
4. **Qual Avaliação a 013 considera** — `test_conjunto_elegivel.py::test_o_conjunto_elegivel_e_exatamente_o_que_a_013_herda`
5. **Sair do conjunto exige ato nomeado** — `test_conjunto_elegivel.py`, `test_impedimento.py`
6. **Nada disso produziu resultado** — `test_mesa_de_avaliacao.py::test_a_vertical_nao_produz_resultado`

O contrato herdado é `avaliacoes_elegiveis(edital, etapa_id, inscricao_id=None)`, em
`avaliacoes/application/selectors.py`.
