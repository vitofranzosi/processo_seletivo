# Contrato: recusas e achados

O vocabulário é o do documento: "Etapa", "reserva", "ampla concorrência", "desfecho desfavorável",
"não comparecimento". Os nomes entre chevrons são do conteúdo.

## Gravação do rascunho (`validate_stage`)

| Caso | Campo | Mensagem |
|---|---|---|
| valor fora das escolhas | `unfavorableOutcomeEffect` | O efeito do desfecho desfavorável da Etapa «nome» não é um dos previstos. |
| valor fora das escolhas | `absenceEffect` | O efeito do não comparecimento da Etapa «nome» não é um dos previstos. |

## Publicação e Retificação (`BLOCKING_ERROR`)

| Código | Requisito | Mensagem |
|---|---|---|
| `efeito_sem_reserva` | FR-7002 | A Etapa «nome» declara que o candidato deixa de concorrer pela reserva, mas ela «alcança todas as inscrições \| não é eliminatória». Só a Etapa eliminatória restrita a algumas Modalidades tem reserva de onde tirar alguém. |

## Retificação que muda o efeito (FR-7020)

`stage_effect_changed_after_unfavorable`, 422:

> A Retificação mudaria o efeito do desfecho da Etapa «nome», que já registrou «N» resultado(s)
> desfavorável(is), contando os superados por recurso. O efeito aplicado a alguém não muda mais
> nesta Etapa.

## Recurso (FR-7028)

`appeal_worsens_situation`, o código de hoje, com a mensagem de hoje. O que muda é a comparação:
agora ela segue a ordem de gravidade.
