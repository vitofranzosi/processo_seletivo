# Data model: 154

**Nada se grava** (FR-6216): nenhum modelo, coluna, migration, estado gravado ou tabela append-only.
O provisionamento de papéis continua protegendo as mesmas 58 tabelas. Tudo abaixo é **derivação de
leitura**, sobre o que a projeção da `118` e a política do Requerimento da `029` já trazem.

## Derivações novas na projeção — `portal/obrigacoes.py`, `Obrigacoes`

| Nome | Definição | Requisito |
|---|---|---|
| `providencia_pendente` | `aberta and bool(tarefas)` — as tarefas da FR-3726 da `118`: obrigatório *a corrigir*, obrigatório *a enviar*, Requerimento *a preencher* | FR-6200, D-001 |
| `conferencia_terminada` | `aberta and not tarefas and obrigatórios != [] and all(i.categoria == CONFERIDO for i in obrigatórios)` | FR-6205, D-002 |
| `frase_de_conclusao` (campo que já existe) | sem tarefa: `FRASE_DA_CONFERENCIA_TERMINADA` se `conferencia_terminada`, senão `FRASE_DE_CONCLUSAO`; com tarefa: `""` | FR-6204, FR-6205 |
| `titulo` (propriedade que já existe) | `TITULO_SEM_PROVIDENCIA` se `aberta and not providencia_pendente`; senão `TITULOS[momento]` | FR-6202, FR-6203 |
| `resumo_do_que_falta` (que já existe) | `frase_das_tarefas(totais) or frase_de_conclusao` | FR-6204, FR-6205 |
| `cabe_a_consequencia` | `aberta and bool(prazo) and providencia_pendente` | FR-6209 |

`prazo` já é `""` com o prazo não iniciado e sem vencimento (FR-3749 da `118`), e `aberta` já exclui
desfecho, Processo encerrado e vencimento decorrido. `cartao`, `etapa`, `ressalva` e `andamento` não
mudam de condição (FR-6208, FR-6210; Assumptions da spec).

## Função nova — `portal/obrigacoes.py`

| Nome | Definição | Requisito |
|---|---|---|
| `providencia_pendente_sem_documento(disponibilidade)` | `not (requerimento_na_chamada(d) and d.enviado)` | FR-6201, D-006 |

Ela só é chamada no ramo **sem projeção** (a chamada não pede documento). `requerimento_na_chamada`
é *exigido e declarado na convocação*; o Requerimento pedido **na inscrição** não a desfaz (R-005).

## Constantes

| Onde | Nome | Texto |
|---|---|---|
| `portal/obrigacoes.py` | `TITULO_SEM_PROVIDENCIA` | *Acompanhe sua convocação* |
| `portal/obrigacoes.py` | `FRASE_DA_CONFERENCIA_TERMINADA` | *A conferência dos documentos obrigatórios terminou. Aguarde o registro do resultado desta convocação.* |
| `convocacao/domain/vocabulario_dos_documentos.py` (novo) | `REENVIADO` | *Reenviado — aguardando nova conferência* |
| idem | `reenviado_em_frase()` | *reenviado — aguardando nova conferência* |
| idem | `reenviados(n)` | *1 reenviado — aguardando nova conferência* · *2 reenviados — aguardando nova conferência* |
| `avisos/application/pendencias.py` | `COMPLEMENTADA` (texto revisto) | *documento reenviado — aguardando nova conferência* |

O travessão é U+2014. Os textos que **não** mudam: `FRASE_DE_CONCLUSAO`, `NADA_POR_ENQUANTO`,
`NAO_ATENDIMENTO_PODE_SER_REGISTRADO`, as duas ressalvas, `TITULOS` (quatro momentos), os selos.

## O estado do item reenviado — sem mudança de identidade

| Camada | Identificador | Muda? |
|---|---|---|
| domínio (`convocacao/domain/nomes.py`) | `ITEM_COMPLEMENTADO = "COMPLEMENTADO"` | não (R-007) |
| contagens da `115` | chave `"complementados"` | não |
| condução (`conducao_da_convocacao.py`) | passo `REENVIADO` | não |
| avisos | constante `COMPLEMENTADA` | o nome fica; o **texto** muda (R-011) |

## A tabela de decisão da chamada aberta (portal, com documento pedido)

| Cenário | tarefas | obrigatórios | título | resumo | advertência (prazo correndo) |
|---|---|---|---|---|---|
| C1 — nada enviado | sim | algum a enviar | *Você foi convocado!* | *Você ainda precisa enviar…* | sim |
| F — Requerimento a preencher, docs com a comissão | sim (Requerimento) | com a comissão | *Você foi convocado!* | *Você ainda precisa preencher o Requerimento…* | sim |
| T — tudo enviado, nada conferido | não | com a comissão | *Acompanhe sua convocação* | frase de conclusão | não |
| T + opcional não enviado | não | com a comissão | *Acompanhe sua convocação* | frase de conclusão + linha do opcional | não |
| meio conferido, meio com a comissão | não | misto | *Acompanhe sua convocação* | frase de conclusão | não |
| Tc — todo obrigatório conferido | não | todos `CONFERIDO` | *Acompanhe sua convocação* | frase da conferência terminada | não |
| Tc + opcional enviado, não conferido | não | todos `CONFERIDO` | *Acompanhe sua convocação* | frase da conferência terminada | não |
| só facultativo, nada enviado | não | nenhum | *Acompanhe sua convocação* | frase de conclusão + linha do opcional | não |
| pendência nova depois de T | sim (a corrigir) | algum a corrigir | *Você foi convocado!* | *Você ainda precisa corrigir 1 documento.* | sim |

Sem a comunicação enviada ou sem vencimento, a coluna da advertência é sempre *não* (como hoje), e
o título segue as mesmas linhas. Fora da chamada aberta, nada desta tabela vale: os títulos e textos
da FR-3858 da `121` para vencido, encerrado e decidido não mudam.

## A chamada aberta sem documento pedido (D-006)

| Cenário | `providencia_pendente_sem_documento` | título | advertência no acompanhamento (prazo correndo) |
|---|---|---|---|
| só o Requerimento na chamada, não enviado | `True` | *Você foi convocado!* | sim |
| só o Requerimento na chamada, enviado | `False` | *Acompanhe sua convocação* | não |
| Requerimento na inscrição, enviado | `True` | *Você foi convocado!* | sim |
| nada pedido pelo portal | `True` | *Você foi convocado!* | sim |

A página da convocação sem documento **nunca** mostra a advertência, em nenhuma linha: o parcial da
chamada só a põe com a projeção, que esse ramo não tem. Fica como hoje (D-007).
