# Contrato — superfícies

Três atores, três canais. A Constituição §VI exige que a capacidade seja alcançável pelo canal do
ator, sem shell e sem manipulação de banco.

## Interface administrativa (quem conduz o certame)

| Superfície | O que faz | Requisitos |
|---|---|---|
| `…/sorteio/` do Edital | lista os recortes, o estado de cada um e o que falta | FR-062 |
| Observar ocorrência | busca na fonte e registra o material bruto; **não** calcula nem constitui | FR-019, FR-029 |
| Publicar relação | projeta, numera, mostra a prévia **da relação**, cita o método do marco e publica congelando | FR-001..FR-009, FR-067 |
| Tela do sorteio | universo, resumo, método e semente; um botão só: **Realizar o sorteio** | FR-029, FR-030 |
| Anular | motivo obrigatório; constitui sucessor a partir de relação e ocorrência novas | FR-052..FR-055 |

**Declarar o método não é superfície do sorteio**, e saiu desta tabela: ele é conteúdo do Edital, e
mora na composição — abaixo. Quem conduz o certame **lê** o método na tela do sorteio e não o
declara ali; quem o altera está retificando o Edital, com a autorização daquele ato (D-013, R-013).

A tela de publicar a relação **exibe o método que a relação vai citar** e recusa publicar quando o
marco não declarou nenhum (FR-066): é o único ponto do fluxo em que a ausência de método é
percebida a tempo de corrigir sem custo.

A **tela do sorteio é a que a transmissão mostra**: precisa ser legível em projeção, sem menu, sem
ruído, com o universo e a semente à vista antes do ato.

**Não existe**, em superfície alguma: campo de semente, botão de simular, botão de refazer.

## Portal público (qualquer pessoa, sem autenticação)

| Superfície | O que faz | Requisitos |
|---|---|---|
| Relação de habilitados | número público, nome e protocolo de cada participante, critério de projeção e resumo | FR-005, FR-006, FR-011 |
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
| Método do sorteio, no marco | algoritmo, fonte, ocorrência, derivação, normalização, substituição — objeto do marco, retificável por identidade | FR-013, FR-014, FR-066 |

A sugestão é da tela. Nada preenche conteúdo publicado sem ato de quem elabora.
