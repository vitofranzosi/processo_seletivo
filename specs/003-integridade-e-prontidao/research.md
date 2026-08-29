# Research: Integridade Normativa e Prontidão para Produção

**Feature**: `003-integridade-e-prontidao` | **Fase**: 0 | **Data**: 2026-08-29

Este documento registra o que foi investigado antes de decidir, e o que foi descartado. As
decisões resultantes estão em [plan.md](./plan.md); aqui ficam as alternativas e o porquê de não
terem sido escolhidas.

## Q1 — Como conter o endereçamento por índice sem trocar o modelo de dados

**Investigado**: como `AlteracaoNormativa` resolve caminho (`publicacoes/domain/changes.py`), o que
`content_conflicts` já verificava, e em que condições a verificação era pulada.

**Achado**: `requires_content_check` retornava falso quando nenhuma alteração declarava
`expectedPreviousHash`, e nem a interface nem os testes o declaravam. `REPLACE` e `REMOVE` passavam
sem verificação alguma.

| Alternativa | Por que não |
| --- | --- |
| Trocar já para chave estável | Muda `data-model`, contrato público e exige migrar Retificações existentes. Acumular isso com uma correção emergencial esconderia a segunda dentro da primeira. Virou a `004`. |
| Exigir `expectedPreviousHash` do cliente no contrato | Quebra clientes existentes e transfere a responsabilidade para quem não tem obrigação de saber. O servidor já conhece a base declarada em `baseSnapshotId`. |
| Bloquear Retificações concorrentes por lock no Edital | Serializa trabalho que não conflita e não resolve o caso de vigências fora de ordem, em que o conflito não é temporal. |

**Escolhido**: precondição derivada pelo servidor. Detalhe em `plan.md`, Decisão 1 e 2.

## Q2 — Hash de conteúdo basta?

**Investigado**: se a precondição por hash cobre todos os deslocamentos de índice.

**Achado**: **não**. Reproduzido com dois Perfis de denominação idêntica: depois do deslocamento, o
hash do valor em `/profiles/1/name` continua conferindo, e o ato altera o Perfil errado com a
precondição satisfeita. `ADD` posicional é pior — não tem valor anterior algum a comparar, e
deslocar a posição de inserção muda a ordem normativa publicada.

| Alternativa | Por que não |
| --- | --- |
| Hash do elemento inteiro em vez do valor no caminho | Faria duas Retificações sobre campos diferentes do mesmo Perfil conflitarem entre si, sem necessidade. |
| Proibir `ADD` com índice numérico, aceitando só `/-` | Remove a capacidade de inserir em posição, que é ato administrativo legítimo. |

**Escolhido**: âncora de identidade por índice atravessado, derivada pelo servidor e não
declarável. `id` quando a entidade tem um; hash do elemento inteiro quando não tem.

## Q3 — O que fazer com as Retificações já persistidas

**Investigado**: se a precondição é reconstruível a partir do que está gravado.

**Achado**: é. A derivação é função determinística de `base_snapshot.content` e da sequência
ordenada de alterações — exatamente o que a elaboração passa a calcular.

| Alternativa | Por que não |
| --- | --- |
| Deixar como está e pedir reenvio do rascunho | Não vale para Retificação já homologada, que precisaria ser devolvida antes. Foi a suposição inicial, e estava errada. |
| Backfillar também as Publicadas | Reescrever ato normativo já produzido. A Constituição proíbe. |

**Escolhido**: migração determinística sobre as Retificações **em curso**, mais recusa na
Publicação para qualquer `REPLACE`/`REMOVE` que chegue sem precondição.

## Q4 — Imutabilidade no banco sem travar o fluxo

**Investigado**: quais campos de cada tabela mudam legitimamente e em que estados.

**Achado**: `AtoAdministrativo` e `RevisaoEdital` só são criados, nunca alterados — trigger
absoluta serve. `Retificacao` transita de estado e `AlteracaoNormativa` é apagada e recriada a cada
edição de rascunho — trigger absoluta quebraria o fluxo.

**Descoberto durante a implementação**: numa trigger `BEFORE`, o valor devolvido é a linha que
segue adiante. Devolver `OLD` num `UPDATE` **descarta a alteração em silêncio** — o comando
responde sucesso e nada muda. É pior do que não ter trigger. A primeira versão tinha esse defeito e
foi um teste de outro cenário que o denunciou.

**Escolhido**: trigger condicional a `OLD.status` para as duas primeiras, absoluta para as duas
últimas, com `RETURN NEW` em `UPDATE` e `RETURN OLD` em `DELETE`.

## Q5 — Ordem de provisionamento dos papéis PostgreSQL

**Investigado**: se a política pode ser aplicada de uma vez em banco vazio.

**Achado**: **não**. Privilégio de tabela só existe depois que a tabela existe, e a tabela é criada
por migration, que precisa do papel de migração. A primeira versão falhava com
`relation "auditoria_registroauditoria" does not exist`.

`ALTER DEFAULT PRIVILEGES` resolve tabela futura, mas não distingue append-only de ordinária.

| Alternativa | Por que não |
| --- | --- |
| Rodar só depois das migrations | Não há papel de migração antes de provisionar; a ordem não fecha. |
| Migrar como superusuário e depois provisionar | Deixa as tabelas com dono errado, e `ALTER TABLE` de migration futura falha — no meio de um deploy. |

**Escolhido**: provisionar → migrar → provisionar. Todo comando que toca tabela é condicional à
existência dela, e o comando informa quantas protegeu para que a segunda passada esquecida apareça
na hora, não numa auditoria.

## Q6 — Como verificar comportamento de JavaScript sem toolchain de JavaScript

**Investigado**: como provar as regras de `validacao.js` e a expiração de `rascunho.js`.

**Achado**: buscar string no fonte prova que a mensagem foi escrita, não que ela aparece na
situação certa. Era o que os primeiros testes faziam.

| Alternativa | Por que não |
| --- | --- |
| jsdom via npm | Acrescenta `package.json`, `node_modules` e uma etapa de CI a um projeto Python. É decisão de toolchain, que pertence ao plano. |
| Playwright | Muito mais peso do que o problema pede, e a CI passaria a depender de navegador. |
| Não testar | Deixaria dois requisitos com implementação plausível e nenhuma verificação. |

**Escolhido**: `node --test` com shim de DOM mínimo, escrito à mão e limitado às APIs que os dois
scripts usam. Node não é dependência: quando ausente, os testes são ignorados. Cobre as **regras**;
foco, anúncio por leitor de tela e o balão do navegador continuam verificação manual, registrada em
[quickstart.md](./quickstart.md).

## Q7 — Semântica da repetição idempotente

**Investigado**: o que o contrato documenta para cada operação.

**Achado**: um único código de sucesso por operação. O padrão `201 if created else 200` respondia
fora do contrato em toda a API, não só nas Retificações.

**Escolhido**: a repetição responde com o status registrado do ato original, e o recurso é
devolvido no estado atual — que é o que o cliente obteria relendo-o. Replay literal exigiria
persistir o corpo da resposta; a diferença importa pouco com o `ETag` acompanhando o estado, e está
registrada como decisão em `plan.md`, Decisão 5.
