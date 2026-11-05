# Contrato: o recorte excedente

O que a feature promete a quem chama os comandos e a quem lê as telas. As frases são proposta, e o
plano as passa pela varredura de vocabulário antes de fixá-las (Assumptions da spec).

## 1. A recusa (FR-3897 a FR-3899, D-003)

Uma recusa só, para os três comandos.

| Campo | Valor |
|---|---|
| código | `list_is_general_competition_alias` |
| status | 422 |
| quando | o `lista_id` do pedido tem papel `EXCEDENTE` na versão vigente, lida **dentro** da trava do comando |
| efeito | nada se grava: nem registro, nem trilha de ato |
| mensagem | *"A Modalidade «{nome}» é a que este Perfil aponta como a ampla concorrência, e não tem recorte próprio: a ampla já reúne todos os inscritos, inclusive quem a declarou. Use o recorte da ampla concorrência."* |

| Comando | Sobre o quê se pergunta |
|---|---|
| `sorteios.application.relacao.publicar_relacao` | o `lista_id` pedido, na versão relida |
| `sorteios.application.sorteio.constituir_sorteio` | o `lista_id` da relação, na versão vigente |
| `divulgacao.application.publicar.publicar_resultado` | o `lista_id` do ato, na versão vigente |

**Ordem**: depois de `ctx.repetido`, porque o pedido repetido devolve o desfecho anterior, e antes de
qualquer projeção ou consulta externa que a recusa torne inútil.

**A emissão computada não recusa**: normaliza para a ampla, como desde a `034` (FR-3900).

## 2. As frases do histórico (FR-3903, FR-3904)

Compostas por `origem` ([data-model.md](../data-model.md)).

| Origem | Frase |
|---|---|
| `NASCIDO` | *"Produzido quando o sorteio dava lista própria à Modalidade apontada como a ampla concorrência. A ocupação das vagas não usa esta lista, e ela fica preservada como foi feita."* |
| `TORNADO` | *"Produzido quando esta Modalidade tinha recorte próprio. A Retificação nº {N} passou a apontá-la como a ampla concorrência, e desde então a ocupação das vagas não usa esta lista. O registro fica preservado como foi feito."* |

Onde aparecem: a seção de histórico da tela do sorteio, a tela do ato, a lista de resultados divulgados
do marco e a prévia de um ato excedente, onde a frase substitui o botão de publicar.

## 3. A causa de obsolescência (FR-3912)

| Campo | Valor |
|---|---|
| `tipo` | `papel_do_recorte` |
| `descricao` | *"O papel deste recorte mudou na Retificação nº {N}: o ato foi produzido para outro universo e não vale para o recorte de hoje."* |
| onde | `estado_do_marco`, nos dois ramos (computado e sorteado) |

## 4. A página do Edital (FR-3906, FR-3907)

| Destino | Quando | Para onde |
|---|---|---|
| *conduzir o marco* | como hoje | `interface:marco` |
| *divulgar o resultado* | o ator divulga e o marco tem ao menos um recorte operacional com ordem | `interface:marco` + `#divulgacao` |

No máximo **um** *divulgar o resultado* por marco.

## 5. O quadro de recortes (FR-3908)

| Estado da célula de divulgação | Ator divulga | Link |
|---|---|---|
| falta (há ato) | sim | prévia do ato vigente |
| obsoleto (o público lê um ato anterior) | sim | prévia do ato vigente |
| feito | sim | Resultados divulgados |
| qualquer | não | nenhum |

## 6. O que não muda

- As páginas públicas de verificação de relação, sorteio e resultado (FR-3905, D-005).
- O portal do candidato e os avisos (FR-3915).
- As rotas: nenhuma nova, nenhuma removida.
