# Modelo — o que muda de sentido, e o que não muda de forma

## Nenhuma entidade, nenhuma migration

A feature não persiste nada novo, não muda coluna e não reescreve linha. O total do `make preparar`
continua **`N de 34`**. Se a saída disser outro número, a worktree está atrás da `main` — ou alguém
acrescentou migration, e esta feature não acrescenta.

**Nada é apagado.** O `choices` de `EventoCronograma.status` continua com os quatro valores: há
conteúdo publicado que carrega `PLANEJADO` para sempre, e pode haver, por API, algum com
`EM_ANDAMENTO` ou `CONCLUIDO`. Tirar os valores do modelo tornaria esse conteúdo ilegível ao ORM sem
ganhar nada — a leitura já deixa de considerá-los (`FR-735`).

## O que muda de sentido

| Onde | Antes | Depois |
|---|---|---|
| `EventoCronograma.status` (linha e conteúdo publicado) | declaração de fase que ninguém fazia; nascia `PLANEJADO` e ficava | responde **uma** pergunta: cancelado ou não. `PLANEJADO`, `EM_ANDAMENTO` e `CONCLUIDO` são lidos como *não cancelado* (`FR-736`) |
| `status` na entrada da API do rascunho | aceita os quatro valores | aceita `PLANEJADO` e `CANCELADO`; os outros dois são recusados com a razão (`FR-737`) |
| Fase exibida do Evento | `declarado <status>` | derivada na leitura (`FR-735`, `R-3`) |
| `Medida` do sinal | par numerador/denominador | par **com unidade** (`FR-743`, `UX-087`) |
| `Sinal` | espécie, alvo, mensagem, medida, destino | o mesmo, mais a **condução** — a frase de a quem pedir, quando o ato não é do leitor (`FR-740`) |
| Achados da validação do conteúdo | nenhum para Etapa sem Evento | um **aviso** novo, com código próprio (`FR-739`, `R-5`) |

## A fase derivada

Não é campo, não é coluna, não é cache. É uma função pura dos instantes e do relógio, e o relógio é
o **mesmo** que a leitura inteira já usa (`agora` recebido, como o pulso e os sinais recebem hoje):

| Evento | Fase | Regra de onde sai |
|---|---|---|
| `status == CANCELADO` | *cancelado* | a declaração, que prevalece |
| é o período de inscrições | *planejado* · *em andamento* · *concluído* conforme o período esteja futuro · aberto · encerrado | `inscricoes/domain/periodo.py`, `periodo_de_inscricoes` — a regra que decide se o sistema recebe inscrição |
| qualquer outro | *planejado* antes do início; *concluído* se vencido; *em andamento* entre os dois | `editais/domain/calendario.py`, `vencido` — a régua única da `037` |
| sem início | nenhuma | a conferência de forma já o acusa; a fase não é inventada |

## De onde cada medida passa a ler

| Espécie | Numerador | Denominador | Unidade |
|---|---|---|---|
| `UX-003` | participantes com menos avaliadores que o previsto | **participantes da Etapa** — antes, toda inscrição submetida | inscrições |
| `UX-063` | participantes distribuídos e não concluídos | participantes com distribuição completa | inscrições |
| `UX-064` | peças com membro desimpedido | peças **aguardando decisão** — antes, só as admitidas | recursos |
| `UX-046` | recortes sem linha do quadro | recortes | recortes — e a frase deixa de repetir os dois números |

A população de participantes é a de `resultados/application/prontidao.py` — `participacao_detalhada`
na tela de distribuição, que já a materializa no panorama, e `restringir_a_participantes` no painel,
que dobra as mesmas três regras na consulta agregada. Ver `R-6`.

## O que a feature não modela, de propósito

**Prazo de resposta ao recurso.** Não existe no domínio, e o sinal não o inventa (spec, fato 6).
**Responsável.** O produto não liga identidade a papel (`038`, `D-003`); a condução nomeia a
permissão.
