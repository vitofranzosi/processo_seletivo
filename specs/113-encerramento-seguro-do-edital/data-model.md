# Data Model: Encerramento seguro do Edital (113)

**Nenhuma tabela, coluna, migration ou gatilho novo.** A feature lê o que existe e grava só o que o
encerramento e o cancelamento já gravam (`Edital.status`, `AtoAdministrativo`, `RegistroAuditoria`,
reserva de idempotência).

## Situação (derivada, não gravada)

| Campo | Tipo | Regra |
|---|---|---|
| `especie` | `IMPEDIMENTO` \| `ADVERTENCIA` | impedimento só existe ao encerrar; ao cancelar, toda situação é advertência (FR-3536) |
| `tipo` | um dos tipos abaixo | — |
| `quantidade` | inteiro ≥ 1 | recursos, reavaliações, convocações, rascunhos; 1 nos demais |
| `marco` | nome publicado | prazo recursal, resultado, reavaliação, providência |
| `ate` | instante | fim do período, fim do prazo recursal, vencimento mais distante da convocação |
| `retificacao` | id e `created_at` | Retificação homologada ou em curso |

### Tipos

| Tipo | Espécie ao encerrar | Origem | Spec |
|---|---|---|---|
| `PERIODO_EM_CURSO` | impedimento | período `ABERTO` com término | FR-3529 |
| `PERIODO_POR_ABRIR` | impedimento | período `FUTURO` | FR-3529 |
| `PRAZO_RECURSAL_EM_CURSO` | impedimento | janela computável aberta da publicação vigente | FR-3530 |
| `RECURSO_AGUARDANDO` | impedimento | sem juízo, ou admitido sem decisão | FR-3531 |
| `REAVALIACAO_PENDENTE` | impedimento | `reavaliacoes_pendentes_do_marco` | FR-3532 |
| `PROVIDENCIA_PENDENTE` | impedimento | `providencias_pendentes_do_marco` | FR-3532 |
| `RETIFICACAO_HOMOLOGADA` | impedimento | `Retificacao.HOMOLOGADA` | FR-3533 |
| `CONVOCACAO_AGUARDANDO` | advertência | `fatos_do_edital` | FR-3534, FR-3535 |
| `CONVOCACAO_VENCIDA` | advertência | `fatos_do_edital` | FR-3534, FR-3535 |
| `RESULTADO_NAO_DIVULGADO` | advertência | `fatos_do_edital` | FR-3534, FR-3535 |
| `DEFINITIVO_NAO_PUBLICADO` | advertência | `fatos_do_edital` | FR-3534, FR-3535 |
| `APURACAO_DESATUALIZADA` | advertência | `fatos_do_edital` | FR-3534, FR-3535 |
| `RETIFICACAO_EM_CURSO` | advertência | `Retificacao.EM_ELABORACAO`, `EM_REVISAO` | FR-3534 |
| `PRAZO_RECURSAL_NAO_DECLARADO` | advertência | publicação vigente sem janela computável, marco sem `admits: false` | FR-3534 |
| `PERIODO_SEM_TERMINO` | advertência | período `ABERTO` sem término | FR-3529, FR-3534 |
| `RASCUNHOS_NAO_ENVIAVEIS` | advertência, só no cancelamento | `Inscricao.RASCUNHO` com período aberto | FR-3536 |

Os tipos que já existem na `099` mantêm o nome dela e passam a ser **definidos só** em
`processos/application/pendencias_do_edital.py`; o relatório os importa. A frase da confirmação e a do
relatório nascem do mesmo tipo.

## Transições

Nenhuma nova. `PUBLICADO → ENCERRADO` passa a exigir lista de impedimentos vazia; `* → CANCELADO`
segue como está. As Retificações em curso de Edital em estado final continuam no estado em que
estavam, e passam a ser exibidas como paradas (FR-3544).
