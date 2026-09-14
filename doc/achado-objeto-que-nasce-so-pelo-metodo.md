# O objeto que pode nascer, e só o método do sorteio nasce pela tela

**Encontrado em**: 14/09/2026, na revisão final do PR #114 (spec 026), ao fechar a jornada do
método do sorteio.

**Estado**: registro. **Não é prioridade**, e não deve ser derivado automaticamente em spec
seguinte — o princípio VI da Constituição é explícito: *"Limites registrados são insumo de
priorização, nunca a priorização em si."*

---

## O que é

O contrato de mutabilidade declara, em `PODE_PASSAR_A_EXISTIR`, quais objetos ausentes **podem**
nascer por Retificação, com a razão normativa de cada um. Hoje são quatro que podem e um que não:

| Objeto | Pode nascer? | A tela oferece? |
|---|---|---|
| `classificationMilestones/*/drawMethod` | sim | **sim** |
| `classificationMilestones/*/cutRule` | sim | não |
| `classificationMilestones/*/appealWindow` | sim | não |
| `profiles/*/vacancyReversion` | sim | não |
| `competitionModalities/*/normativeRule` | não | não (e não deve) |

Os três do meio têm decisão escrita dizendo que nascem, e só nascem pela API. Quem opera pela tela
não tem por onde declarar uma regra de corte, uma janela recursal ou a reversão de vagas num
Edital publicado que não as declarou.

## Por que não foi fechado junto

O método do sorteio foi um dos quatro canários da spec 026, e o caminho dele existe porque **todo
Edital publicado antes do degrau 10 da versão canônica carrega `drawMethod` nulo** — sem a tela, o
acervo inteiro dependeria da API. Os outros três não têm acervo equivalente esperando: são
declarações que o Edital simplesmente não fez.

A mecânica já é genérica. `interface/retificacao.py` monta um único `REPLACE` do objeto inteiro
sempre que os campos de um objeto ausente são oferecidos, sem lista de objetos e sem conhecer o
`drawMethod`: a detecção é pela chave relativa do campo. O que falta em cada um dos três é a
decisão de apresentação — oferecer campos em branco de um objeto que não existe muda o que a tela
diz ao servidor, e cada objeto tem consequências próprias (uma janela recursal concede prazo; uma
regra de corte muda quem é classificado).

## O que decidir, quando for a hora

Para cada um dos três, separadamente: **oferecer os campos em branco na tela**, com o rótulo do
vazio dizendo o que a ausência provoca — como o método já faz —, ou **registrar que a declaração
nasce só pela API**, com razão escrita, e protegê-la por teste. As duas são respostas legítimas ao
princípio VI; o que não é legítimo é o estado atual, em que ninguém decidiu.
