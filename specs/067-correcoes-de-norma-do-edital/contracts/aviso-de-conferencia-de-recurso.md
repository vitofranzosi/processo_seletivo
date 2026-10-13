# Contrato — o aviso de conferência de recurso (`FR-1305` a `FR-1310`, `D-002`, `D-006`)

## Achado

| Campo | Valor |
|---|---|
| severidade | aviso (`WARNING`), em todo ato |
| código | `appeal_schedule_review` |
| caminho | `schedule` — a etapa Cronograma |
| quantidade | no máximo um por conteúdo |

## Quando é emitido

Quando ao menos um marco de algum Perfil declara regra de recurso: `appealWindow.admits` verdadeiro
com prazo inteiro positivo, ou `appealWindow.admits` falso. Nenhuma outra condição — a presença ou a
ausência de Eventos de recurso não decide se o aviso existe, só o que ele diz.

## Evento de recurso

Evento do Cronograma cujo `type` ou `description` casa `\brecurs\w*`, sem distinguir maiúsculas.

| Texto | É Evento de recurso? |
|---|---|
| "Recurso" | sim |
| "Prazo para interposição de recursos" | sim |
| "Prazo recursal" | sim |
| "RECURSO CONTRA O RESULTADO" | sim |
| "Concurso", "percurso", "Discurso" | não |

## Mensagem

Três partes, nesta ordem:

1. **Os marcos.** `Os marcos publicam recurso: ` + as regras separadas por `; ` + `.` Cada regra:
   `“{nome}” ({Perfis}) — {prazo}, contados da divulgação desse resultado` ou
   `“{nome}” ({Perfis}) — não cabe recurso`. Marcos de mesmo nome e mesma regra são uma regra só;
   `{Perfis}` são os códigos na ordem do conteúdo, separados por vírgula, ou `N Perfis` acima de seis.
2. **O Cronograma.** `O Cronograma tem N Evento(s) de recurso: ` + cada Evento como
   `{descrição ou tipo} — de {início}, a {término}` (ou `— em {início}` sem término), separados por
   `; `, na ordem do Cronograma, + `.` — ou `O Cronograma não tem Evento de recurso.`
3. **A orientação.** `O sistema não relaciona o Cronograma aos marcos: confira se há período de
   recurso para o resultado de cada marco e se os demais períodos são contra outros atos, ditos assim
   no texto do Edital.`

O título que a interface mostra antes da mensagem é o de todos os avisos; a mensagem não usa código,
caminho nem nome de campo (`UX-190`).

Instantes com a grafia do documento (`26/11/2026, às 00h`).

## Onde aparece

Revisão do rascunho, submissão, homologação, publicação, conferência e confirmação da Retificação —
onde os demais avisos já aparecem. Nunca na página de Edital publicado fora de uma Retificação.
