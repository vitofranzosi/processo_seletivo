# Pesquisa — Supervisão do Processo

**Fase 0 do planejamento.** O que foi investigado no código antes de desenhar, o que foi decidido, e
o que foi descartado. As decisões de produto estão na spec (`D-001` a `D-010`); aqui ficam as
técnicas, e uma delas **estreitou um requisito**.

Ponto de partida: `doc/inventario-supervisao-do-processo.md`. Esta pesquisa não repete o
levantamento — ela responde às perguntas de implementação que o inventário deixou abertas.

---

## T-001 — Onde a supervisão mora, e por que não é um app novo

**Decisão.** Um módulo de leitura em `interface/`, sem app próprio, sem modelo e sem migration.

**Racional.** A regra do repositório é que app é dono de fato persistido; a `011` abriu app novo
porque trouxe `MembroComissao` e `AlocacaoEtapa`. A supervisão não traz nenhum: por `D-007` ela é
composição de leituras que já existem. Um app sem modelo criaria a expectativa de que um dia terá,
que é exatamente a fronteira que a spec proíbe atravessar.

O lugar natural é ao lado da página do Processo, que a supervisão estende — não um segundo endereço
concorrente.

**Alternativas descartadas.** App `supervisao` com `application/selectors.py` próprio — rejeitado
pela ausência de agregado. Módulo em `processos/` — rejeitado porque a supervisão lê de sete apps e
ficaria com dependência de todos eles no app do agregado mais central do sistema.

---

## T-002 — O que já existe pronto, e o orçamento de consulta de cada peça

Levantado função a função. Nada aqui é reimplementado.

| Necessidade | Função existente | Custo |
|---|---|---|
| Cobertura de avaliação por Etapa | `avaliacoes.selectors.resumo_da_etapa` | **1 agregação por Etapa** |
| Avaliações previstas na Etapa | `avaliacoes.domain.previsao` | leitura do conteúdo |
| Etapas do Edital publicado | resolvedor já usado pela `011` | 1 leitura de versão |
| Ato de ordenação vigente | `classificacao.selectors.ato_vigente` | 1 consulta |
| Obsolescência do ato | `classificacao.selectors.estado_do_marco` | **recalcula a ordem inteira** |
| Recursos do Edital e situação | `recursos.selectors.recursos_do_edital` | 1 consulta |
| Impedimento do julgador | `recursos.domain.elegibilidade.impedimento` | 5 perguntas **por par** |
| Comissão ativa do Processo | `comissoes.selectors.membros` | 1 consulta |
| Presidência deste Processo | `comissoes.domain.autorizacao.pode_gerir_comissao` | 1 consulta |

Duas linhas desta tabela são caras e viram tópico próprio: `estado_do_marco` (T-003) e `impedimento`
(T-004). As demais entram como estão.

---

## T-003 — Obsolescência sem recalcular tudo: filtro barato, confirmação exata

**O problema.** `estado_do_marco` chama `calcular_ordem` e compara universos. É o desenho certo para
**abrir um marco**; chamá-lo para todos os marcos de todos os Editais de um Processo a cada abertura
da supervisão repete o erro que a `018` recusou em `T-006` — usar a verificação do ponto como
varredura de listagem.

**Decisão.** Duas passagens, e a segunda só onde a primeira acusar:

```text
1. barata    candidato ⇔  ato.versao ≠ versão vigente do Edital
                       ∨  ∃ ResultadoEtapa vigente nas Etapas do marco
                             com consolidado_em > ato.emitido_em
               → nenhuma das duas: o ato não pode estar obsoleto; nada a confirmar
2. exata     `estado_do_marco` apenas nos candidatos → `obsoleto` verdadeiro ou falso
```

**As duas condições são as causas das quatro divergências que `comparar` produz**, e não uma
heurística escolhida por conveniência:

| Divergência | Causa | Alcançada por |
|---|---|---|
| `regra_ausente` | o marco sumiu da versão vigente | versão diferente da citada pelo ato |
| `regra_alterada` | Retificação mudou o recorte do marco | idem |
| `participantes_alterados` | o universo mudou | Resultado vigente mais novo que o ato |
| `resultados_alterados` | Resultado oficial trocado, inclusive por recurso | idem — a superação grava sucessor, e o sucessor é mais novo |

Os campos existem e são os que o filtro compara: `AtoDeOrdenacao.emitido_em` e `.versao`, e
`ResultadoEtapa.consolidado_em`.

**O filtro é conservador por construção**, e a assimetria é deliberada: ele admite candidato que a
confirmação depois descarta, e nunca o contrário. Errar para mais custa uma chamada que devolve
falso; errar para menos **perde o sinal em silêncio**, que é o defeito que ninguém descobre.

**Por que não parar na primeira.** Fato posterior **não** implica divergência: nem todo Resultado
novo obsoleta toda ordem emitida, porque o ato declara o universo sobre o qual foi calculado. Exibir
o candidato como sinal produziria alarme falso, e um painel que erra uma vez deixa de ser lido.

**Por que não usar só a segunda.** Seria correto e caro. A primeira passagem é o que mantém o custo
proporcional ao que mudou, e não ao tamanho do Processo.

**Alternativa descartada.** Apresentar *"pode estar obsoleto"*. É a saída que evita a conta e
transfere a dúvida para quem lê — o oposto do que a feature promete.

---

## T-004 — Elegibilidade por conjuntos, e o limite que ela encontrou

**O problema.** `impedimento(ator, recurso)` responde por par, com cinco perguntas. A pergunta da
supervisão é outra: *existe alguém?* Iterar o guardião sobre `recursos × membros` reintroduziria o
custo por linha que `T-006` da `018` recusou (`D-008`).

**Decisão.** Calcular o conjunto de **impedidos** por álgebra sobre autorias já persistidas, e
compará-lo com a comissão ativa. As cinco perguntas viram cinco origens de `subject`:

```text
impedidos(recurso) = { avaliacao.concluida_por  dos Resultados alcançados }
                   ∪ { resultado.consolidado_por dos Resultados alcançados }
                   ∪ { publicacao.ato.emitido_por }          quando ataca publicação
                   ∪ { publicacao.publicado_por }            quando ataca publicação
                   ∪ { subjects com Impedimento declarado na Inscrição }

sinal ⇔ existe recurso pendente com  membros_ativos − impedidos(recurso) = ∅
```

O alcance dos Resultados é o mesmo que o domínio já define para leitura de listagem — o Resultado
atacado quando existe —, e não a cadeia histórica do par. O custo é um punhado de consultas sobre o
conjunto de pendentes, independente do número de membros.

**O limite, e ele mudou o requisito.** Julgar exige também a permissão sistêmica `recurso:julgar`, e
**o sistema não sabe quem a possui**: `Actor.permissions` é derivado dos papéis declarados na
sessão, e não existe registro que ligue identidade a papel — a autenticação institucional ainda é
tarefa aberta da `002`.

Consequência aceita: o sinal afirma **o que é verificável** — nenhum membro ativo da comissão está
desimpedido — e **não** afirma impossibilidade de julgamento, porque alguém de fora da comissão pode
deter a permissão. A spec foi ajustada (`FR-030`, `FR-030a`, `UX-005`, `SC-010`).

**Alternativa descartada.** Persistir papéis para tornar a pergunta completa. É feature de
identidade, não de supervisão, e violaria `D-007` de saída.

---

## T-005 — Divergência temporal: o que se compara, e o que não se compara

**Decisão.** A divergência é entre o `status` **declarado** do Evento e a posição do instante de
leitura em relação a `start_at` e `end_at`. Nenhum dos dois é corrigido.

Casos que produzem sinal:

**A tabela é fechada**: as quatro posições temporais possíveis contra os quatro estados
declarados, e nenhuma combinação fica implícita. Combinação omitida é a que ninguém testa.

| Declarado | Antes de `start_at` | Dentro do intervalo | Depois de `end_at` |
|---|---|---|---|
| `PLANEJADO` | não — coerente | **sim** — em curso e não declarado | **sim** — encerrado e não concluído |
| `EM_ANDAMENTO` | **sim** — em curso antes de começar | não — coerente | **sim** — encerrado e não concluído |
| `CONCLUIDO` | **sim** — concluído antes de começar | **sim** — concluído com prazo em curso | não — coerente |
| `CANCELADO` | não | não | não — sai da leitura temporal |

E duas exclusões que valem para a tabela inteira:

| Condição | Sinal |
|---|---|
| `end_at` ausente | **não** — sem término não há "depois"; só *antes* e *dentro* são determináveis, e nenhum dos dois basta sozinho |
| `CANCELADO` | **não** — o Evento saiu do cronograma efetivo, e cobrar coerência temporal dele seria cobrar de quem já foi cancelado |

`end_at` é anulável no domínio, e Evento sem término é legítimo: marco instantâneo. A ausência não é
divergência, e tratá-la como tal encheria o painel de sinal sobre a forma normal do dado.

---

## T-006 — Etapa sem Evento: por que é sinal e não erro de validação

**Constatado.** A validação de publicação recusa Etapa que referencia Evento inexistente, mas o
campo é **anulável**: Etapa sem referência publica normalmente. É permissão deliberada.

**Decisão.** Vira sinal de supervisão, com a redação de `UX-001` — *sem marco no cronograma* —, e
**não** vira achado de prontidão. Transformá-lo em impeditivo de publicação mudaria o que o sistema
aceita publicar, o que é decisão normativa e não cabe a um painel.

---

## T-007 — Inscrições: nível, série e o que o banco já garante

**A soma é do Processo; as datas são do Edital.** `Cronograma` é `OneToOne` com `Edital`, e o Evento
que marca o período de inscrições é único por cronograma, garantido por constraint parcial. Não há
período do Processo a computar, e inventar um seria escolher arbitrariamente entre os Editais.

**A série é segura por construção.** O estado submetido é inalcançável sem instante de submissão —
`CheckConstraint` que exige instante, versão aceita, aceite das declarações e protocolo. Agrupar por
esse instante não tem como produzir buraco silencioso.

**Agrupamento por dia, no fuso da aplicação.** Uma agregação por Edital, com recorte no período
declarado. Rascunho fica fora da série por `FR-015`, e fora do total por `FR-012`.

**Descartado: separar rascunho ativo de abandonado.** `Inscricao` não guarda instante de última
edição. O fato existe na trilha de auditoria — as edições de rascunho gravam evento —, mas usar a
trilha como fonte de indicador operacional é decisão de fronteira que a spec não toma.

---

## T-008 — Autorização, e o que a supressão por alcance significa

**Decisão.** A porta é `pode_gerir_comissao(ator, processo)`, que já aceita **duas bases** — a
permissão sistêmica de gerir comissão ou a presidência deste Processo — e é a mesma que governa a
página do Processo. Recusa devolve a resposta uniforme de não encontrado.

**A supressão por alcance é por sinal, e é silenciosa** (`FR-004`, `SC-013`). Cada sinal declara a
permissão da tela dona:

| Sinal | Permissão da dona |
|---|---|
| `UX-001`, `UX-002` | a própria porta da supervisão |
| `UX-003` | quem alcança a distribuição da Etapa |
| `UX-004` | quem alcança a ordenação do marco |
| `UX-005` | quem alcança os recursos do Edital |

Anunciar que existe um sinal suprimido diria a quem não pode ver que **há** algo para ver, que é
vazamento por agregação.

---

## T-009 — O que a supervisão faz quando o Processo não tem o que supervisionar

Levantado porque é o estado inicial de todo Processo, e o que a `007` chama de beco.

| Situação | Comportamento |
|---|---|
| Nenhum Edital publicado | Pulso declara que não há período de inscrições; nenhum sinal de Etapa |
| Edital publicado, zero inscrições | zero é resposta, apresentado como tal |
| Nenhum marco classificatório | `UX-004` não se aplica; nada é dito |
| Processo cancelado | leitura preservada; encaminhamentos que a situação não admite não são oferecidos |

---

## Resumo das decisões técnicas

| # | Decisão | Consequência |
|---|---|---|
| T-001 | módulo de leitura, sem app e sem modelo | nenhuma migration |
| T-003 | filtro barato + confirmação exata | custo proporcional ao que mudou |
| T-004 | impedidos por conjuntos | `D-008` preservado; requisito estreitado |
| T-005 | cancelado e sem término não divergem | menos alarme falso |
| T-006 | Etapa sem Evento é sinal, não impeditivo | publicação inalterada |
| T-007 | soma no Processo, datas no Edital | `D-005` implementável |
| T-008 | porta única, supressão silenciosa por sinal | sem vazamento por agregação |
