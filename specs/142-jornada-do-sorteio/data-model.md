# Data Model: A tela do sorteio como a jornada de quem o conduz (142)

**Nenhuma entidade persistida nova, nenhuma migration.** O que segue é o modelo de apresentação que a
view entrega ao template.

## Passo (apresentação, não se grava)

| Campo | O que é | De onde vem |
|---|---|---|
| `numero` | 1 a 4 | a ordem da jornada |
| `chave` | `relacao`, `semente`, `sorteio`, `ordem_sorteada` | as naturezas da `127`; a quarta é da tela |
| `simples`, `termo`, `curta`, `porque` | os nomes e as frases | `conceitos.CONCEITOS` nos três primeiros; o quarto, do módulo da tela |
| `ancora` | a seção do passo | `titulo-recortes`, `titulo-ocorrencia`, `titulo-execucao`, `titulo-resultado` |
| `listas` | `[(rótulo, Celula)]` nos passos por lista | as células do andamento |
| `celula` | a do marco, no passo 2 | a célula da semente |
| `contagem` | "1 de 2 listas fixadas" | conta as células `FEITO` sobre as listas que não são *Não se aplica* |
| `situacao` | a mais urgente | `URGENCIA`, ordem de apresentação (D-003) |
| `agora` | a tarefa da vez | o primeiro passo com célula em `A_PRATICAR`, só para quem conduz |

## Ordem gravada (por lista sorteada)

`[{posicao, numero, nome, protocolo, motivo}]` — `PosicaoNaOrdem` do ato do sorteio, com o número
público da `ParticipanteHabilitado` da relação que o sorteio consumiu.

## Transições

Nenhuma. Os passos não têm estado próprio: abrir a tela de novo lê a derivação de novo.
