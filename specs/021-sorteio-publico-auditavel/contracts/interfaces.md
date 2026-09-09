# Contrato — superfícies

Três atores, três canais. A Constituição §VI exige que a capacidade seja alcançável pelo canal do
ator, sem shell e sem manipulação de banco.

## Interface administrativa (quem conduz o certame)

| Superfície | O que faz | Requisitos |
|---|---|---|
| `…/sorteio/` do Edital | lista os recortes, o estado de cada um e o que falta | FR-062 |
| Declarar método | algoritmo, fonte, ocorrência, derivação, normalização, substituição | FR-013 |
| Publicar relação | projeta, numera, mostra a prévia **da relação** e publica congelando | FR-001..FR-009 |
| Tela do sorteio | universo, resumo, método e semente; um botão só: **Realizar o sorteio** | FR-029, FR-030 |
| Anular | motivo obrigatório; constitui sucessor a partir de relação e ocorrência novas | FR-052..FR-055 |

A **tela do sorteio é a que a transmissão mostra**: precisa ser legível em projeção, sem menu, sem
ruído, com o universo e a semente à vista antes do ato.

**Não existe**, em superfície alguma: campo de semente, botão de simular, botão de refazer.

## Portal público (qualquer pessoa, sem autenticação)

| Superfície | O que faz | Requisitos |
|---|---|---|
| Relação de habilitados | números públicos e critério de projeção | FR-005, FR-011 |
| Resultado do sorteio | a ordem completa, com identidade, algoritmo, semente e resumos | FR-045, FR-046 |
| **Verificar este sorteio** | recalcula das entradas e relata o que conferiu | FR-048..FR-051 |
| Manifesto | download em JSON | FR-047 |

A verificação responde em linguagem de gente: *"Sorteio verificado: 237 participantes; relação
íntegra; semente íntegra; ordem reproduzida integralmente."* — e, quando falha, diz **o que**
divergiu.

## Composição do Edital (quem elabora)

| Superfície | O que faz | Requisitos |
|---|---|---|
| Evento do Cronograma | campo de local, com sugestão do valor do evento anterior | FR-056..FR-061 |

A sugestão é da tela. Nada preenche conteúdo publicado sem ato de quem elabora.
