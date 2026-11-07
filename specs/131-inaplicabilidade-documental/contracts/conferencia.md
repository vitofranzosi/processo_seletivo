# Contrato: o comando da conferência e o POST do desfecho

**Feature**: [../spec.md](../spec.md) · **Modelo**: [../data-model.md](../data-model.md)

## 1. `convocacao.application.documentos.conferir`

A assinatura não muda: `actor`, `item_id`, `apresentacao_id`, `resultado`, `motivo`,
`motivo_da_substituicao`, `idempotency_key`, `correlation_id`.

### Recusas novas

| Código | HTTP | Quando | Texto |
|---|---|---|---|
| `not_found` (existente) | 404 | item com situação *não se aplica* na lista (FR-4464) | *"Recurso não encontrado."* |
| `nao_se_aplica_sem_condicao` | 422 | *"não se aplica"* em item incondicional ou facultativo (FR-4457) | *"Este documento é exigido de toda pessoa a quem o Edital o pede. 'Não se aplica' só existe para documento que o Edital publicou com condição."* |
| `nao_se_aplica_sem_abertura` | 409 | *"não se aplica"* com apresentação vigente não aberta pelo conferente nesta chamada (FR-4460) | *"Abra o documento antes de registrar que ele não se aplica: ele pode mostrar que a condição se aplica."* |
| `motivo_sem_conteudo` | 422 | motivo do *pendente* ou do *"não se aplica"* sem nenhuma palavra (FR-4458) | *"Escreva o motivo com palavras: ele aparece para a pessoa convocada."* |
| `motivo_da_substituicao_obrigatorio` (existente) | 422 | também quando a anterior ou a nova é *"não se aplica"*, haja ou não apresentação (FR-4462) | o atual |

A ordem das recusas está no [modelo](../data-model.md), §3.

### A trilha

`CONVOCACAO_CONFERIR`, como hoje: resultado, requisito e chamada, sem o motivo (FR-3603 da `115`).

## 2. O POST do desfecho (`interface:desfechar`)

Campos novos, só lidos quando a espécie é `ACEITE` ou `REGULARIZACAO`:

| Campo | Tipo | Quando vem |
|---|---|---|
| `inaplicabilidades` | assinatura (hex) | sempre que a tela mostrou o bloco (FR-4467) |
| `ciencia_das_inaplicabilidades` | `"1"` ou ausente | a caixa de ciência |

O comando `desfechar` recebe `ciencia` como `{"assinatura": str, "marcada": bool} | None`. Sob a trava
do desfecho, depois da guarda da lista incompleta (correção da `115`, PR #425) e da guarda das pendências
(FR-3592 da `115`, revista), ele lê as conferências vigentes *"não se aplica"* de obrigatórios e:

| Situação | Resultado |
|---|---|
| conjunto vazio | segue, como hoje |
| conjunto não vazio e `marcada` falso ou ausente | 409 `ciencia_das_inaplicabilidades` — *"Para registrar este desfecho, confirme que viu os documentos obrigatórios considerados não aplicáveis."* |
| conjunto não vazio e assinatura diferente | 409 `inaplicabilidades_mudaram` — *"A conferência dos documentos mudou desde que você abriu este formulário. Nada foi gravado: confira a lista abaixo antes de confirmar."* |
| conjunto não vazio, marcada e assinatura igual | segue; a trilha do `CONVOCACAO_DESFECHAR` cita os `id` (FR-4469) |

A recusa grava nada, e a tela volta com a lista nova, como a recusa da prévia superada da correção pela
`120` faz.

## 3. A leitura documental (`LeituraDocumental`)

| Membro | Hoje | Depois |
|---|---|---|
| `contagens["conformes"]` | conforme + não se aplica | **só** conforme |
| `contagens["nao_se_aplica"]` | — | não se aplica após análise |
| `ItemLido.condicao` | — | `requiredWhen` da versão do item, ou `None` |
| `ItemLido.condicional` | — | `condicao is not None` |
| `inaplicabilidades` | — | itens obrigatórios com estado *não se aplica*, na ordem do Edital |
| `pendencias_para_incluir` | obrigatório fora de `ATENDIDOS` | obrigatório fora de `ATENDIDOS`, **ou** *não se aplica* incondicional (P-1 a) |
