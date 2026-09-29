# Data Model: A convocação como fluxo

**Nenhuma tabela nova, nenhuma coluna nova, nenhuma migration** (`D-011`). O que muda é quem grava as
linhas que já existem, e quantas por gesto.

## O que cada gesto grava

| Gesto | `Convocacao` | `ComunicacaoEmitida` | `DesfechoDaConvocacao` | `EfeitoDeOcupacao` | `ApuracaoDeOcupacao` | Trilha |
|---|---|---|---|---|---|---|
| Convocar os titulares (N pessoas) | N | N, depois do `commit` (mensagem individual) | — | — | — | N convocações + N emissões |
| Convocar um a um | 1 | 1, depois do `commit` (mensagem individual) | — | — | — | 1 + 1 |
| Comunicações pendentes (N) | — | N | — | — | — | N |
| Não atendimento dos vencidos (N) | — | — | N | N | 0 ou 1 | N desfechos + 0 ou 1 apuração |
| Desfecho individual | — | — | 1 | 1 | 0 ou 1 | 1 + 0 ou 1 |

## Campos, e de onde cada valor vem

`Convocacao` — os campos da `019`, sem mudança de forma:

| Campo | Antes | Agora |
|---|---|---|
| `especie` | escolhido no formulário | derivado da posição (`D-008`); o informado que diverge é recusado |
| `fundamento` | digitado por pessoa | texto derivado (`D-009`) + complemento opcional, uma vez por ato |
| `vencimento` | digitado por pessoa | uma vez por ato: digitado ou fim de um Evento do Cronograma (`D-010`) |
| `apuracao`, `ato_de_ordenacao_id`, `corte_id`, `versao` | lidos no ato | iguais |
| `criado_por`, `criado_em` | o ator, o instante | iguais — o mesmo para as N do gesto |

`ApuracaoDeOcupacao` emitida por desfecho: os campos da `016`, com `apuracao_anterior` = a vigente,
`motivo_da_sucessao` derivado, `emitida_por` = o autor do desfecho, e sem movimento de vaga (`D-005`).

## Estados derivados (sem coluna)

- **Titular chamável**: na fila de chamada **e** no conjunto de ocupantes da apuração vigente.
- **Vencida**: vigente, sem desfecho, com envio e com vencimento anterior a agora — o estado
  `CONVOCADO_VENCIMENTO_DECORRIDO` que já existe.
- **Comunicação pendente**: vigente, sem desfecho, sem envio com sucesso.

## Identidade do gesto

`correlation_id = convocacao-lote-<chave>` em cada linha de trilha que o gesto produz. A chave é a da
confirmação, nascida no GET.
