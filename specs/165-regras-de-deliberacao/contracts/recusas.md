# Contrato: recusas e achados

As frases são o contrato: os testes as conferem por trecho. `«…»` é substituído pelo nome da Etapa,
pelos rótulos publicados ou pelos números.

## Gravação do rascunho

| Código | Campo | Frase |
|---|---|---|
| `StageValidationError` | `deliberationRule` | A regra de deliberação da Etapa «nome» não é uma das previstas. |

## Publicação e Retificação (achados impeditivos)

| Código | Ato | Frase |
|---|---|---|
| `regra_invalida` | ambos | A regra de deliberação da Etapa «nome» não é uma das previstas. |
| `regra_sem_colegiado` | ambos | A Etapa «nome» declara regra de deliberação, mas ela «é pontuada \| prevê uma avaliação por inscrição». Só a Etapa decisória com mais de uma avaliação por inscrição declara como a comissão chega ao resultado. |
| `maioria_com_numero_par` | ambos | A Etapa «nome» decide por maioria com «N» pareceres por inscrição. A maioria exige número ímpar, porque o empate não tem regra publicada; com número par, escolha uma das regras de unanimidade. |
| `deliberacao_sem_regra` | publicação | A Etapa «nome» prevê «N» pareceres por inscrição e não declara como a comissão chega ao resultado. Escolha uma das três regras. |

## Retificação (recusas de comando, 422)

| Código | Frase |
|---|---|
| `stage_deliberation_without_rule` | A Retificação compõe a Etapa «nome» com «N» pareceres por inscrição e sem regra de deliberação. Escolha uma das três regras. |
| `stage_deliberation_changed_after_result` | A Retificação mudaria a regra de deliberação ou o número de pareceres da Etapa «nome», que já registrou «1 resultado \| k resultados» por avaliação, contando os superados por recurso. A regra aplicada a alguém não muda mais nesta Etapa. |
| `stage_evaluations_below_concluded` | A Retificação reduziria a Etapa «nome» a «N» pareceres por inscrição, e «1 inscrição já tem \| k inscrições já têm» mais pareceres concluídos que isso. |

## Prontidão e consolidação (motivo de linha)

| Estado | Frase |
|---|---|
| `NAO_CONSOLIDAVEL` (menos de N, contada em `aguardando_pareceres`) | faltam «k» de «N» pareceres |
| `NAO_CONSOLIDAVEL` (mais de N) | há «k» pareceres concluídos onde o Edital prevê «N», e o sistema não escolhe quais contam |

## Julgamento (422)

| Código | Frase |
|---|---|
| `reavaliacao_colegiada_indisponivel` | A reavaliação determinada não está disponível contra o Resultado de uma Etapa colegiada. O recurso pode ser decidido por correção fixada, informando o desfecho. |

## Distribuição e reabertura

| Código | Onde | Frase |
|---|---|---|
| `exposto_aos_pareceres` | recusa de linha da distribuição | «membro» já teve acesso aos pareceres dos colegas sobre a inscrição «protocolo» nesta Etapa, e não pode avaliá-la. |
| `parecer_exposto` | reabertura (422) | O parecer não pode ser reaberto: quem o deu já teve acesso aos pareceres dos colegas sobre esta inscrição. Para corrigi-lo, inative a Atribuição e atribua a inscrição a outro membro. |

## Às cegas (texto da tela)

| Onde | Frase |
|---|---|
| linha oculta | Oculto: você ainda tem parecer pendente sobre esta inscrição. |
