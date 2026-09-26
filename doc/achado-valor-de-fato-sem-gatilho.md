# Achado — `ValorDeFato` é append-only por uma camada só

Encontrado em 25/09/2026, a partir do que a `044` registrou em `research.md` (R-005 e R-014) ao
decidir as camadas da lista exigida gravada no envio.

> **Não vira escopo por estar escrito aqui.** O que se registra é uma tabela histórica protegida
> por menos do que o projeto diz proteger, o que isso custa, e o que corrigir exigiria. Priorizar é
> do usuário.

## O que se observou

`inscricoes_valordefato` guarda os fatos que a inscrição declarou e congelou no envio (015, D-2): o
valor que entra na classificação tem de ser o do momento da inscrição. A tabela está em
`TABELAS_APPEND_ONLY` (`seguranca/papeis.py:39`), e o docstring do modelo o diz
(`inscricoes/models.py:144`).

Das três camadas que o repositório usa para o que "nasce e não muda mais", ela tem **uma**:

| camada | onde deveria estar | estado |
|---|---|---|
| privilégio ausente | `TABELAS_APPEND_ONLY` → `provisionar_papeis` | **presente** — o runtime não tem `UPDATE` nem `DELETE` |
| gatilho `BEFORE UPDATE OR DELETE` | `inscricoes/migrations/0004_valor_de_fato.py` | **ausente** — a migration é um `CreateModel` puro |
| recusa em `save`/`delete` | `ValorDeFato` em `inscricoes/models.py` | **ausente** — o modelo não sobrescreve nenhum dos dois |

O `CLAUDE.md` descreve as tabelas append-only como protegidas "por trigger *e* por privilégio
ausente — duas camadas independentes", e o docstring de `papeis.py` chama o privilégio de "a
segunda camada da imutabilidade, independente das triggers". Para esta tabela a primeira não existe.

**E o documento que a descreve está errado.** `doc/descoberta-018-decisao-c-superacao-de-resultado.md:138`
põe `ValorDeFato` na linha "papel + modelo". O papel existe; o modelo, não. A linha é de 06/09 e
também envelheceu para as outras quatro que lista — `ConclusaoAvaliacao`, `RegistroAuditoria`,
`AtoAdministrativo` e `VersaoConsolidada` ganharam gatilho desde então —, mas só `ValorDeFato`
está errado para menos.

## O que a camada que resta cobre, e o que não cobre

O privilégio recusa quem conecta como a role de runtime, que é a aplicação em serviço. Não recusa
quem conecta como a role de migração ou como superusuário: uma migration de dados, um `manage.py
shell` num ambiente com as credenciais de migração, uma correção manual pelo `psql`. É exatamente o
caminho que o gatilho existe para fechar — "a trigger recusa a mutação mesmo de quem tem
privilégio", nas palavras de `papeis.py`.

Na suíte contra PostgreSQL, que o `make test-pg` roda como o superusuário de `POSTGRES_USER`,
**nada** recusa: um
`ValorDeFato.objects.filter(...).update(...)` num teste ou num comando passa em silêncio.

**O que a mutação alteraria.** O valor congelado é a entrada da classificação (idade, tempo de
serviço, o que o Edital declarou como fato). Reescrevê-lo depois do envio muda uma ordem histórica
sem deixar rastro de que mudou — o `AtoDeOrdenacao`, que é append-only com as três camadas, passaria
a citar entradas que já não são as que ele leu.

**Hoje ninguém escreve nela fora do lugar.** A única escrita é o `bulk_create` do envio
(`inscricoes/application/submissao.py:368`). Não há `update`, `delete` nem `save` sobre a tabela em
código de produção nem em teste. O achado é de garantia ausente, não de dano observado.

## Por que nenhum guardião viu

`test_as_tabelas_append_only_sao_exatamente_as_que_recusam_mutacao_no_modelo`
(`tests/integration/test_imutabilidade_do_historico.py:200`) confere só uma direção: toda tabela que
recusa no modelo está em `TABELAS_APPEND_ONLY`. A volta foi deixada de fora de propósito, por causa
de `RevisaoEdital` — e é por essa mesma porta que `ValorDeFato` passa sem guarda de modelo.

`tests/migrations/test_migrations.py` confere os gatilhos que `TRIGGERS_POR_APP` declara, e
`inscricoes` não está em `APPS` nem em `TRIGGERS_POR_APP`. Não há lista que diga "toda tabela
append-only tem gatilho", de modo que a falta não reprova nada.

`tests/integration/test_database_permissions.py` é parametrizado sobre `TABELAS_APPEND_ONLY` e
cobre o privilégio — a única camada presente.

## Não é a única assimetria — é a única de uma camada só

Cruzando as 33 tabelas de `TABELAS_APPEND_ONLY` com os gatilhos das migrations e os `save`/`delete`
dos modelos, em `235d148`:

| tabela | privilégio | gatilho `UPDATE OR DELETE` | modelo |
|---|---|---|---|
| `inscricoes_valordefato` | sim | **não** | **não** |
| `classificacao_posicaonaordem` | sim | **não** — só o `BEFORE INSERT` de coerência (`posicao_coerente`, `classificacao/0001`) | sim |
| `publicacoes_revisaoedital` | sim | sim | **não** — assimetria declarada no próprio guardião |
| `matriculas_geracaodearquivo` | sim | sim | **não** |
| as outras 29 | sim | sim | sim |

As três de baixo têm duas camadas de três. `ValorDeFato` é a única com uma. Registram-se aqui porque
a mesma varredura as mostrou; se entram na mesma correção é decisão à parte.

## O que corrigir exigiria

O molde existe e é recente: `recursos/migrations/0002_ato_de_instrucao.py` — função e gatilho em SQL,
`RunPython` que só executa no PostgreSQL, e caminho reverso que derruba os dois. A `044`
(`inscricoes/migrations/0005_item_da_lista_exigida.py`, na branch dela) repete o molde para a lista
exigida, com gatilho e guarda de modelo.

1. **Migration nova em `inscricoes`** com o gatilho `BEFORE UPDATE OR DELETE` sobre
   `inscricoes_valordefato`, recusando com "append-only" na mensagem. Nenhum dado se altera, e nada
   hoje atualiza ou apaga a tabela, de modo que o gatilho não tem o que quebrar em produção.
2. **`save`/`delete` no modelo** recusando fora da criação, com "append-only" na mensagem — o que põe
   a tabela no conjunto que `_recusa_mutacao` reconhece. O `bulk_create` do envio não passa por
   `save` e segue funcionando.
3. **Os guardiões**: `"inscricoes": 4 → 5` no guardião da `022`, com justificativa ao lado;
   `inscricoes` em `APPS` e o gatilho novo em `TRIGGERS_POR_APP`; um caso em
   `test_imutabilidade_do_historico.py` que ataque por `update()` e `delete()` diretos no QuerySet.
4. **A linha 138 da descoberta-018** corrigida, ou anotada como envelhecida.

## A ordem com a `044` é o que precisa de decisão

A `044` está em PR aberto (#168). O PR publica por ora só spec, plano e tarefas, mas a implementação
já está escrita na branch local dela, com a `inscricoes/0005_item_da_lista_exigida`
— que move `"inscricoes": 4 → 5` e põe `inscricoes` em `APPS` e em `TRIGGERS_POR_APP`, os três
pontos que esta correção também tocaria.

Uma correção feita agora, a partir da `main`, criaria **outra** `0005` em `inscricoes`: duas folhas
no grafo de migrations, e quem fosse mergeado depois teria de renumerar a sua e refazer a contagem.
As saídas:

- **Esperar a `044` entrar** e corrigir como `0006`, sobre a `main` que já tem `inscricoes` nos
  guardiões. É a que não gera conflito, e a espera não custa nada que já não esteja custando: a
  tabela está assim desde a `015`.
- **Corrigir agora como `0005`** e deixar a `044` renumerar a dela para `0006` quando for mergeada.
- **Pôr a correção dentro da `044`.** A própria R-005 a declarou fora de escopo — "registro para a
  fila, não escopo daqui".

## Decisão

Em 25/09/2026, o usuário: **corrigir depois que a `044` for mergeada, como `inscricoes/0006`.** A
correção é a dos quatro itens acima, sobre `ValorDeFato`.

As outras três tabelas da seção anterior — `PosicaoNaOrdem` sem gatilho de mutação,
`RevisaoEdital` e `GeracaoDeArquivo` sem recusa no modelo — **ficam só registradas**, fora da
correção.
