# Rastreabilidade — 022 Supervisão do Processo

**Spec**: [spec.md](./spec.md) · **Plano**: [plan.md](./plan.md) · **Tarefas**: [tasks.md](./tasks.md)

Do requisito ao teste que o sustenta. A Constituição exige que requisito crítico seja rastreável
entre especificação, plano, tarefas, implementação e testes (Princípio V); esta é a última ponte.

> **Escrita antes da implementação, e é por isso que ela vale.** A `010` escreveu a sua depois, e
> duas linhas que um script abortado nunca gravou passaram despercebidas — foi esse defeito que fez
> nascer o teste que confere esta tabela. Aqui as colunas *Onde vai viver* e *Testes* apontam para
> o que as tarefas criam; a conferência de que apontam para arquivos existentes é do fechamento da
> feature, e está em `tasks.md` T055 e T056.

Caminhos são relativos a `backend/`.

---

## Alcance, autorização e fronteira

| Requisito | Onde vai viver | Testes |
|---|---|---|
| FR-001 a visão existe e parte do Processo | `interface/views.py`, `interface/urls.py` | `tests/integration/supervisao/test_autorizacao.py` (T004, T005) |
| FR-002 duas bases, cada uma suficiente | `interface/supervisao.py` → `comissoes/domain/autorizacao.py` | `tests/integration/supervisao/test_autorizacao.py` (T003, T007) |
| FR-003 recusa uniforme de não encontrado | `interface/views.py` | `tests/integration/supervisao/test_autorizacao.py` (T007) |
| FR-004 supressão silenciosa do sinal por alcance | `interface/supervisao.py` | `tests/integration/supervisao/test_autorizacao.py` (T045, T048) |
| FR-004a o Pulso não é suprimido, e não traz dado pessoal | `interface/supervisao.py` | `tests/integration/supervisao/test_autorizacao.py` (T045), `tests/integration/supervisao/test_fronteira.py` (T050) |
| FR-005 todo número reproduzível pelas donas | `interface/supervisao.py` | `tests/acceptance/test_supervisao_do_processo.py` (T009, T052) |
| FR-006 nenhuma escrita | — *ausência é o requisito* | `tests/integration/supervisao/test_fronteira.py` (T050) |
| FR-007 nenhum estado persistente próprio | — *ausência é o requisito* | `tests/migrations/test_migrations.py` (T051) |
| FR-008 não rederiva os atos do Edital | `interface/templates/interface/processo_detalhe.html` | reuso de `interface/acoes.py` (T008) |
| FR-009 instante da leitura | `interface/supervisao.py` | `tests/integration/supervisao/test_pulso.py` (T014) |

## Pulso — inscrições

| Requisito | Onde vai viver | Testes |
|---|---|---|
| FR-010, FR-011 total do Processo, desdobrado por Edital nomeado | `interface/supervisao.py` | `tests/integration/supervisao/test_pulso.py` (T010, T013) |
| FR-012 rascunho é grandeza distinta | `interface/supervisao.py` | `tests/integration/supervisao/test_pulso.py` (T011, T013) |
| FR-013 últimas 24 h, havendo período em curso | `interface/supervisao.py` | `tests/integration/supervisao/test_pulso.py` (T018a, T022) |
| FR-014, FR-015 série diária por Edital, pelo instante de submissão | `interface/supervisao.py` | `tests/integration/supervisao/test_pulso.py` (T018, T023) |
| FR-016 equivalente textual, sem rolagem horizontal | `interface/templates/interface/_serie_de_inscricoes.html` | `tests/interface/test_supervisao.py` (T019, T026); conferência manual em 375 px (T027) |
| FR-017 nenhum percentual para inscrição | — *ausência é o requisito* | `tests/interface/test_supervisao.py` (T012) |
| FR-018 ausência de período declarada | `interface/supervisao.py` | `tests/integration/supervisao/test_pulso.py` (T020, T025) |

## Pulso — cronograma

| Requisito | Onde vai viver | Testes |
|---|---|---|
| FR-019 período e tempo restante, por Edital | `interface/supervisao.py` | `tests/integration/supervisao/test_pulso.py` (T017, T021) |
| FR-020 toda data nomeia o Edital | `interface/templates/interface/supervisao.html` | `tests/integration/supervisao/test_pulso.py` (T010, T015) |
| FR-021 próximos marcos, sem os cancelados | `interface/supervisao.py` | `tests/integration/supervisao/test_pulso.py` (T017, T024) |
| FR-022 cronograma ausente é dito | `interface/supervisao.py` | `tests/integration/supervisao/test_pulso.py` (T020, T025) |
| FR-023 o estado declarado do Evento não é alterado | `interface/supervisao.py` | `tests/integration/supervisao/test_sinais.py` (T024, T034) |

## Atenção — o catálogo e os cinco sinais

| Requisito | Onde vai viver | Testes |
|---|---|---|
| FR-024 catálogo fechado em cinco espécies | `interface/supervisao.py` | `tests/unit/interface/test_supervisao.py` (T029, T030) |
| FR-025 ausência em uma linha, sem seção por sinal | `interface/supervisao.py` | `tests/integration/supervisao/test_sinais.py` (T029) |
| FR-026 Etapa sem Evento vinculado | `interface/supervisao.py` | `tests/integration/supervisao/test_sinais.py` (T031, T032) |
| FR-027 declarado incompatível com a posição temporal | `interface/supervisao.py` | `tests/integration/supervisao/test_sinais.py` (T033, T034) |
| FR-028 cobertura de avaliação insuficiente | `interface/supervisao.py` → `avaliacoes/application/selectors.py` | `tests/integration/supervisao/test_sinais.py` (T035, T036) |
| FR-029 ato vigente obsoleto, confirmado | `interface/supervisao.py` → `classificacao/application/selectors.py` | `tests/integration/supervisao/test_sinais.py` (T037, T038, T039) |
| FR-030, FR-030a comissão inteira impedida, sem afirmar impossibilidade | `interface/supervisao.py` | `tests/integration/supervisao/test_sinais.py` (T040), `tests/interface/test_supervisao.py` (T041) |
| FR-031 impedimento por conjuntos, não por par | `interface/supervisao.py` | `tests/integration/supervisao/test_sinais.py` (T042, T043) |
| FR-032 percentual sempre com numerador e denominador | `interface/templates/interface/_sinal.html` | `tests/integration/supervisao/test_sinais.py` (T028, T035) |
| FR-033 unidade não distribuída permanece no denominador | `interface/supervisao.py` | `tests/integration/supervisao/test_sinais.py` (T035) |
| FR-034 nenhuma carga nem classificação por membro | — *ausência é o requisito* | `tests/integration/supervisao/test_fronteira.py` (T050) |

## Encaminhamento

| Requisito | Onde vai viver | Testes |
|---|---|---|
| FR-035 cada sinal conduz à dona | `interface/supervisao.py` | `tests/interface/test_supervisao.py` (T044, T047) |
| FR-036 a dona recusa; a supervisão só oferece | `interface/supervisao.py` | `tests/integration/supervisao/test_autorizacao.py` (T045a, T049) |
| FR-037 a supervisão não lista o que conta | — *ausência é o requisito* | `tests/interface/test_supervisao.py` (T046) |

## Apresentação

| Requisito | Onde vai viver | Testes |
|---|---|---|
| UX-001 sem marco no cronograma | `interface/templates/interface/_sinal.html` | `tests/integration/supervisao/test_sinais.py` (T031, T032) |
| UX-002 declarado × temporal, lado a lado | `interface/templates/interface/_sinal.html` | `tests/integration/supervisao/test_sinais.py` (T033, T034) |
| UX-003 Etapa e Edital nomeados, com a medida | `interface/templates/interface/_sinal.html` | `tests/integration/supervisao/test_sinais.py` (T035, T036) |
| UX-004 marco nomeado, destino na ordenação | `interface/templates/interface/_sinal.html` | `tests/integration/supervisao/test_sinais.py` (T037, T039) |
| UX-005 a condição nomeada, sem inferência | `interface/templates/interface/_sinal.html` | `tests/interface/test_supervisao.py` (T041, T042) |
| UX-006 duas regiões; a Atenção encolhe, não some | `interface/templates/interface/supervisao.html` | `tests/integration/supervisao/test_sinais.py` (T006, T028, T029) |
| UX-007 o Edital nomeado mesmo havendo um só | `interface/templates/interface/supervisao.html` | `tests/integration/supervisao/test_pulso.py` (T010, T015) |
| UX-008 série legível sem cor e sem imagem | `interface/templates/interface/_serie_de_inscricoes.html` | `tests/interface/test_supervisao.py` (T019, T026) |

## Critérios de sucesso

| Critério | Como se verifica | Testes |
|---|---|---|
| SC-001 tudo numa tela, sem navegar | jornada de quem preside | `tests/acceptance/test_supervisao_do_processo.py` (T052) |
| SC-002 o total é a soma dos Editais | contraprova contra a tela de inscrições | `tests/integration/supervisao/test_pulso.py` (T010) |
| SC-003 rascunho nunca conta como submetida | contraprova | `tests/integration/supervisao/test_pulso.py` (T011) |
| SC-004 todo percentual com numerador e denominador | asserção sobre a forma | `tests/integration/supervisao/test_sinais.py` (T035) |
| SC-005 nenhum percentual para inscrição | ausência asseverada | `tests/interface/test_supervisao.py` (T012) |
| SC-006 não distribuída permanece no denominador | contraprova | `tests/integration/supervisao/test_sinais.py` (T035) |
| SC-007 toda data nomeia o Edital | asserção sobre a página | `tests/integration/supervisao/test_pulso.py` (T010, T017) |
| SC-008 sem marco, e nunca atrasada | ausência asseverada | `tests/integration/supervisao/test_sinais.py` (T031) |
| SC-009 as duas informações, sem arbitrar | tabela-verdade inteira | `tests/integration/supervisao/test_sinais.py` (T033) |
| SC-010 nomeia a condição; um desimpedido a desfaz | contraprova | `tests/integration/supervisao/test_sinais.py` (T040) |
| SC-011 ausência ocupa uma linha | asserção sobre a região | `tests/integration/supervisao/test_sinais.py` (T029) |
| SC-012 resposta igual à de Processo inexistente | comparação literal | `tests/integration/supervisao/test_autorizacao.py` (T007) |
| SC-013 sinal suprimido não deixa marca | ausência asseverada | `tests/integration/supervisao/test_autorizacao.py` (T045) |
| SC-014 nenhuma estrutura persistente nova | guarda por contagem de migrations | `tests/migrations/test_migrations.py` (T051) |
| SC-015 série legível por tecnologia assistiva | equivalente textual com os mesmos valores | `tests/interface/test_supervisao.py` (T019) |

---

## Requisitos cuja evidência é uma ausência

Sete requisitos proíbem em vez de exigir, e por isso não têm coluna *onde vive*: FR-006, FR-007,
FR-017, FR-034, FR-037 e, do lado da apresentação, o que FR-004a proíbe.

**Ausência não se testa por inspeção de código, e sim por asserção sobre a saída.** É por isso que
todos eles caem em `test_fronteira.py` ou em `test_supervisao.py`, e não numa revisão de diff: um
teste que lê a página e não encontra CPF continua valendo depois que alguém acrescentar um campo;
uma revisão, não.

## O que esta tabela não cobre

As decisões (`D-001` a `D-010`) e os tópicos de pesquisa (`T-001` a `T-009`) **não entram**: eles
justificam requisitos, e é o requisito que se rastreia. A varredura de decisões é outra, e cobra que
cada `D-` citado exista dentro da própria feature.
