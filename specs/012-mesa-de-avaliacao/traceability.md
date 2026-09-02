# Rastreabilidade — 012: Mesa de Avaliação

**Feature**: [spec.md](./spec.md) | **Tarefas**: [tasks.md](./tasks.md) | **Data**: 2026-09-02

O princípio V da Constituição exige que requisito crítico seja rastreável entre especificação,
plano, tarefa, implementação e teste. Esta é a ponta final: para cada requisito, **o teste que
falharia se ele fosse quebrado** — e não o teste que passa perto.

## Cobertura

| | |
|---|---:|
| Requisitos funcionais (FR) | 105 |
| Critérios de sucesso (SC) | 31 |
| Edge cases (EC) | 20 |
| Testes na suíte, ao fim da 012 | 1837 |
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
