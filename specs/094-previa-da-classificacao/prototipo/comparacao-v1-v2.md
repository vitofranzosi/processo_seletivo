# Comparação: primeira e segunda versão do protótipo da 094

**19/10/2026.** A segunda rodada de UX foi pedida pelo usuário depois de avaliar as capturas da
primeira: *"demonstra corretamente o algoritmo, mas precisamos evoluí-lo para uma experiência que
permita ao elaborador compreender intuitivamente as consequências"*. O cálculo é o mesmo nas duas — o
motor oficial, conferido contra `desempate.ordenar` a cada pedido, e a matriz do achado sai igual linha a
linha. O que mudou foi a apresentação e a origem dos candidatos.

**Como esta comparação foi feita, e o que ela não prova.** Para cada cenário, abri as duas versões no
navegador do app, com a mesma configuração, e anotei **onde está** a resposta de cada pergunta e
**quanto é preciso ler** para chegar a ela. É uma avaliação heurística de quem escreveu o protótipo, e
não um teste de uso: a validação com elaboradores é a SC-840 e a SC-848, pela T039, e continua pendente.

## As cinco perguntas

1. Quantos candidatos avançariam?
2. Quem não avançaria?
3. Por que houve empate?
4. O que acontece depois?
5. O que muda quando altero a configuração?

## Cenário 1 — Classificação comum, sem empate

Caso-limite "Classificação sem empate", alvo 10, 5 suplentes, 10 vagas, desfecho "Todos os empatados
progridem", Entrevista, faixa seguinte admitida. 19 candidatos.

| | Primeira versão ([captura](capturas/v1/1-sem-empate-desktop.jpg)) | Segunda versão ([captura](capturas/v2/1-sem-empate-desktop.jpg)) |
|---|---|---|
| 1. Quantos avançam | "O corte sairia: 15 progridem; 0 sem posição", no 2º bloco, depois do seletor, da descrição e da faixa | Manchete, a primeira frase: **"15 de 19 candidatos progridem para a Entrevista. 4 não progridem."** |
| 2. Quem não avança | Rolar a tabela até o fim e achar "Fora da faixa" entre "Dentro do alvo" e "Suplente", linha a linha | A manchete diz quantos; na tabela, abaixo da linha tracejada "Linha do fim da faixa", a marca cinza "Não progride" |
| 3. Por que empatou | "Nenhum empate residual nesta ordem" — certo, mas é o 4º bloco | No fluxo: "nenhum empate não resolvido"; em "Empates na pontuação": "nenhum critério de desempate precisou ser usado" |
| 4. O que vem depois | "Progride para a Entrevista" repetido em cada linha; a continuação, só nas linhas de fora | Terceiro passo do fluxo, "Entrevista: 15 participam"; o ramo diz que os 4 de fora podem ser alcançados por faixa seguinte; a apuração das vagas, à parte, "seria possível" |
| 5. O que muda | Nada diz o que mudou; o painel inteiro é redesenhado | Na população estável, o quadro "O que mudou" (cenário 4, abaixo) |

## Cenário 2 — Empate residual na fronteira do corte

Caso-limite "Corte impedido: empate na última posição da faixa", alvo 10, 5 suplentes, desfecho "A
faixa para no alvo" (`STRICT`). Empate de dois na 15ª.

| | Primeira versão ([captura](capturas/v1/2-corte-impedido-desktop.jpg)) | Segunda versão ([resumo](capturas/v2/2-corte-impedido-desktop.jpg), [empates](capturas/v2/2-corte-impedido-empates-desktop.jpg)) |
|---|---|---|
| 1. Quantos avançam | Um parágrafo de seis linhas, no 2º bloco: "O corte não seria emitido. Há empate residual de 2 candidatos na 15ª posição…" | Manchete âmbar: **"O corte não seria emitido."** O passo do corte: "Impedido"; o terceiro: "Ninguém, por enquanto" |
| 2. Quem não avança | Toda linha repete "Corte não emitido — Aguarda o desempate julgado ou a Retificação do desfecho", em três linhas de texto | Todos "Aguarda desempate", agrupados quando sem empate ("1ª a 8ª: 8 candidatos sem empate — aguardam o desempate") |
| 3. Por que empatou | Em cada uma das duas linhas empatadas, um parágrafo de sete linhas com os três critérios ([375 px](capturas/v1/2-linha-empilhada-375.jpg)) | Uma tabela: Olívia e Paulo lado a lado, critério a critério, com os valores iguais; antes dela, **"Atravessa a última posição da faixa (15): é ele que impede o corte."** |
| 4. O que vem depois | "Ninguém progride até que o desempate seja julgado ou o desfecho retificado", no parágrafo; "fronteira das vagas não avaliada" à parte | O fluxo diz; a apuração das vagas, separada e marcada como hipótese, diz que não se avalia porque o corte não sai |
| 5. O que muda | Trocar os suplentes de 5 para 0 **refazia** o cenário: o empate pulava da 15ª para a 10ª, e o painel mostrava a mesma recusa — a mudança da regra ficava escondida pela dos dados | No caso-limite, o painel avisa que o caso acompanha a fronteira. Na população estável: "Corte: impedido na 15ª → impedido na 10ª" — o empate não se moveu, a regra mudou o desfecho |

## Cenário 3 — Corte emitível com impedimento posterior na fronteira das vagas

Caso-limite "Empate na fronteira das vagas", alvo 10, 5 suplentes, 10 vagas, "Todos os empatados
progridem". Empate de dois na 10ª — a primeira linha da reprodução do achado.

| | Primeira versão ([captura](capturas/v1/3-fronteira-das-vagas-desktop.jpg), [tabela](capturas/v1/3-empate-dividido-tabela-desktop.jpg)) | Segunda versão ([resumo](capturas/v2/3-fronteira-das-vagas-desktop.jpg), [empates](capturas/v2/3-fronteira-das-vagas-empates-desktop.jpg), [375 px](capturas/v2/3-resumo-375.jpg)) |
|---|---|---|
| 1. Quantos avançam | "O corte sairia: 15 progridem", e logo abaixo, no mesmo resumo, o aviso âmbar da apuração — dois resultados de naturezas diferentes lado a lado | Manchete verde: **"15 de 19 candidatos progridem para a Entrevista."** O corte é emitível, e isso não é ambíguo |
| 2. Quem não avança | Rolar a tabela; João e Karina marcados "Na faixa — empate na fronteira do alvo", rótulo que exige saber o que é a fronteira do alvo | Abaixo da linha do fim da faixa, "Não progride"; João e Karina "Progride", com a etiqueta "empate não resolvido" e a linha tracejada atravessando entre os dois |
| 3. Por que empatou | Dois parágrafos idênticos, um em cada linha | A comparação dos dois, e **"Atravessa a linha do alvo (10), dentro da faixa: não muda o corte. Atravessa a última das 10 vagas: é ele que pararia a apuração das vagas."** |
| 4. O que vem depois | O aviso da apuração junto do resultado do corte, sem dizer que é uma etapa posterior nem sob que hipótese | Fluxo: Entrevista, 15 participam. **Depois do corte**, num bloco tracejado com o selo "hipótese": "Pararia na 10ª posição", com as suposições e o que a prévia não simula |
| 5. O que muda | Nada diz | Ver o cenário 4 |

## Cenário 4 — A mesma gente, outra regra (só na segunda versão)

População estável, montada para alvo 10, faixa de 15 e 10 vagas: 23 candidatos, com um empate na 10ª,
outro na 15ª, um trio que só os fatos separam, uma candidata sem nota e um candidato eliminado. A regra
muda de 5 para 0 suplentes, **sem salvar**
([resumo](capturas/v2/4-populacao-estavel-o-que-mudou-desktop.jpg),
[tabela](capturas/v2/4-populacao-estavel-tabela-desktop.jpg)).

- **O que mudou com a sua alteração**: "Progridem: 16 → 11. 7 candidatos mudaram de situação (marcados
  na tabela)."
- João e Karina, empatados na 10ª, passam a **"Progride pelo empate"**; Lucas, Marina, Nuno, Olívia e
  Paulo passam a **"Não progride"** — cada um com a marca "mudou".
- O passo do corte diz "+1 além da faixa, pelo empate na 10ª": o número que o corte registra, e não o
  tamanho do grupo.

Na primeira versão esta pergunta não tinha resposta: o painel recalculava, mas não dizia o que tinha
mudado, e o cenário se refazia junto com a regra.

## As mudanças de UX, em resumo

| Pedido do usuário | O que mudou |
|---|---|
| 1. A consequência primeiro | Manchete de uma frase (FR-2238); fluxo Classificação → Corte → Etapa seguinte, com o ramo da continuação (FR-2239); a apuração das vagas separada, tracejada, como hipótese (FR-2240, D-013) |
| 2. Tabela simples | Quatro colunas; só as linhas perto dos limites, os empates e quem mudou; linhas tracejadas onde passam alvo, fim da faixa e última vaga; classificação completa e explicação técnica a um clique (FR-2207, FR-2241, R-011) |
| 3. Empates comparáveis | Uma tabela por grupo, critério a critério, com o critério que separou destacado e a linha que o empate atravessa (FR-2242, D-014) |
| 4. Comparação causal | População estável por padrão, fixa enquanto o painel está aberto; casos-limite como demonstração, avisando que acompanham a fronteira; "Remontar" só a pedido (FR-2243, D-003 revista) |
| 5. Progressão evidente | O fluxo de três passos, com estados "Emitível", "Impedido", "Não corta", "Nenhuma Etapa"; o quadro "O que mudou" (FR-2244) |
| 6. Terminologia | "Progride", "Progride pelo empate", "Não progride", "Aguarda desempate", "Sem posição"; "suplente" só como nome do campo, por causa da DP-4 (D-012, FR-2245) |
| 7. Prioridade | A US3 é P1, e entra no MVP |
| 8. Validação | Desktop e 375 px no navegador do app: sem rolagem horizontal na página nem nas tabelas, foco ao abrir e ao fechar, anúncio por `role="status"`, zero violações de CSP; a matriz do achado igual nos dois modos |

## O que não mudou

O motor, as regras, os rótulos do cartão e os textos publicados. As leituras pendentes do achado (DP-1 a
DP-4) continuam pendentes, e o painel descreve o desfecho como comportamento atual.
