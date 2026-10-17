# A limpeza depois de cada caso transacional

**Data:** 2026-10-17
**Origem:** o que ficou de fora de `doc/estudo-paralelizacao-da-suite.md` — truncar só as tabelas
com linha, e dispensar o `post_migrate` depois de cada caso.
**Natureza:** estudo com proposta. As variantes foram medidas como plugin de fora do repositório;
**a proposta 1 + 2 foi aprovada pelo usuário em 17/10** e está em `backend/tests/conftest.py`,
medida de novo em *A implementação, medida*, abaixo. A variante com `DELETE` continua só proposta.
**Base:** a branch do PR #295 (`ebdbe0f7`, paralelo `-n 4 --dist worksteal`), que ainda não está na
`main`.

## A resposta curta

| Variante | Parede | Teardown do caso transacional | Resultado |
|---|---:|---:|---|
| como hoje | **564s** (571, 556) | 428 ms | 11 627 passando, 11 pulados |
| 1. `TRUNCATE` só das sujas | 503s | 355 ms | idêntico, caso a caso |
| 2. sem `post_migrate` | 530s | 384 ms | idêntico, caso a caso |
| **1 + 2** | **452s (−20%)** | 286 ms | idêntico, caso a caso |
| `DELETE` das sujas + 2 | **226s (−60%)** (224, 227) | 20 ms | **1 falha**, nas duas rodadas |

As duas ideias, como foram pedidas, funcionam e não mudam nada no resultado: a mesma lista de
pulados, linha a linha, e o mesmo desfecho em cada um dos 11 638 casos. Juntas, tiram ~110s da
suíte local. Rendem menos do que se esperava por um motivo do PostgreSQL, explicado abaixo. Ele
aponta para uma terceira variante, que tira 60% da suíte mas expõe um teste que depende da ordem
física das linhas.

## Como foi medido

Um plugin anota cada caso: a duração de cada fase (setup, call, teardown), se é transacional e,
dentro do teardown, quanto foi para o `TRUNCATE` e quanto para o `post_migrate`. Um segundo plugin
troca o `TransactionTestCase._fixture_teardown` conforme a variante. Cada rodada é um
`make test-pg` inteiro, na mesma máquina, uma de cada vez, com banco próprio. A base e a variante
`DELETE` rodaram duas vezes; as demais, uma. As duas bases diferem em 15s, o que dá a escala do
ruído.

Os casos transacionais são 3106. Hoje o teardown deles soma **1330s de trabalho** (a soma dos
quatro workers), contra ~2200s da suíte inteira. Em paralelo, cada caso gasta ~245 ms no
`TRUNCATE` e ~52 ms no `post_migrate`. Em série, num recorte de 83 casos, os números eram 92 ms e
39 ms: a disputa pelo disco e pelo WAL do cluster pesa mais sobre o `TRUNCATE` do que sobre o
resto.

## 1. Truncar só as tabelas com linha

Antes de truncar, uma consulta com um `EXISTS` por tabela, numa ida só, descobre quais têm linha.
Das 86 tabelas de modelo, um caso deixa em média **23,5** sujas.

**O ganho é menor do que esse número promete**, porque o PostgreSQL só trunca uma tabela junto de
todas as que têm chave estrangeira para ela, **vazias ou não**. O fecho das 23,5 sujas por quem as
referencia dá **65 a 69 tabelas**, e o custo do `TRUNCATE` é por tabela, e não por linha. O
`TRUNCATE` cai de 245 para 174 ms por caso, e a suíte de 564s para 503s.

O efeito é o mesmo de hoje: as tabelas que ficam de fora já estavam vazias. Nenhuma das duas
formas reinicia sequência, porque o Django trunca sem `RESTART IDENTITY`.

## 2. Dispensar o `post_migrate`

**Ninguém depende das linhas que ele recria.** Conferido no código e em tempo de execução:

- os receptores de `post_migrate` são só os do próprio Django, `create_contenttypes` e
  `create_permissions`. O projeto não registra nenhum;
- nenhum módulo de `processo_seletivo/` nem de `tests/` usa `ContentType`, `Permission`, `Group`,
  `has_perm` ou `perms`. A autorização do sistema é a do domínio (`seguranca`), e o DRF usa só
  `IsAuthenticated`.

Mesmo assim, o protótipo não esvazia as duas tabelas: ele as **preserva**. Na primeira limpeza de
cada banco roda a do Django inteira, e em seguida tira uma impressão (`md5` das linhas, em ordem)
de `django_content_type` e de `auth_permission`. Nas seguintes, se a impressão continua igual, as
duas tabelas ficam fora do `TRUNCATE` e o sinal não é emitido. Se um caso mexer nelas, a limpeza
volta a ser a de hoje. Assim o banco continua com as linhas que a produção tem, e um teste futuro
que use permissão do Django não quebra em silêncio. A conferência custa uma consulta, e o sinal só
precisou rodar na primeira limpeza de cada worker.

Sozinha, a ideia tira 34s (564 → 530s). Somada à 1, o fecho do `TRUNCATE` perde também as duas
tabelas de referência, e a suíte vai a **452s**.

## 3. A variante que o fecho sugere: `DELETE`, e não `TRUNCATE`

O fecho só existe porque o `TRUNCATE` exige as tabelas que referenciam. Um `DELETE` apaga só as 23,5
sujas. Para isso, a limpeza roda com `SET LOCAL session_replication_role = replica`, que desliga os
gatilhos durante a transação dela: os de chave estrangeira, para a ordem não importar, e os
append-only, que recusariam o `DELETE`. O `TRUNCATE` de hoje também passa por cima dos gatilhos de
linha. O teste continua provando a garantia dentro do caso, e a limpeza acontece fora dele.

O teardown cai de 428 para **20 ms** por caso, e a suíte de 564s para **226s**. A fase de teardown
fora da limpeza também encolhe, de ~125 ms para ~3 ms por caso, e o setup dos transacionais cai
~15%. Isso é consistente com a disputa pelo disco ter acabado, mas não foi investigado.

**O custo: uma falha, a mesma nas duas rodadas.**
`tests/portal/test_acompanhamento_pela_situacao.py::TestRecursoPorLista::test_com_o_prazo_aberto_cada_lista_tem_a_sua_linha`
publica duas listas do mesmo marco com o **mesmo** `publicado_em=agora`. `situacoes_do_candidato`
(`divulgacao/application/selectors.py`) ordena só por `publicacao__publicado_em`, e depois por
`(marco_codigo, marco)`, de modo que o empate entre as duas fica com a ordem em que o PostgreSQL as
lê. Com `TRUNCATE`, o heap está sempre novo, e essa ordem coincide com a de inserção. Com `DELETE`,
o espaço que o autovacuum libera é reaproveitado, e a ordem física deixa de ser a de inserção. O
arquivo passa sozinho com `DELETE`; quebra só no meio da suíte.

Em produção o empate é improvável: cada lista se publica num ato próprio, com o seu `agora`. O
defeito é do teste, que fabrica o empate, e da consulta, que não tem desempate. Fica registrado, e
**não corrigido**.

Outros pontos a pesar antes desta variante:

- `session_replication_role` exige superusuário. O `make test-pg` e o CI conectam como
  superusuário; sem ele, a limpeza teria de voltar ao `TRUNCATE`.
- O `DELETE` deixa tuplas mortas, que o autovacuum recolhe. Nas duas rodadas não apareceu efeito
  além da falha acima, mas a ordem física deixa de ser a de inserção **em toda tabela**. Qualquer
  outra consulta sem desempate que hoje passa por sorte pode passar a falhar. Isso tanto revela
  defeito quanto pode tornar a suíte intermitente.

## A proposta

1. **Implementar 1 + 2 agora** (aprovado e feito, abaixo), num hook do `tests/conftest.py`, só para PostgreSQL e só quando o
   caso não usa `available_apps` nem `serialized_rollback`. Nos demais, a limpeza é a do Django.
   São −20% sem nenhuma diferença de resultado.
2. **Decidir à parte sobre o `DELETE`.** Ele tira 60% da suíte, mas pede antes uma de duas
   correções, e escolher entre elas é decisão de produto: dar desempate a
   `situacoes_do_candidato` (a lista, por exemplo) ou fazer o teste publicar em instantes
   distintos. Depois, rodadas repetidas para ver se outra ordem implícita aparece.

O plugin de cronometragem e o protótipo do `DELETE` estão nas notas da sessão, fora do
repositório.

## A implementação, medida

`backend/tests/conftest.py` troca o `TransactionTestCase._fixture_teardown` pela limpeza enxuta.
Ficam com a limpeza do Django os casos com `available_apps` ou `serialized_rollback` (hoje nenhum),
os bancos que não são PostgreSQL, e todos os casos quando `LIMPEZA_INTEGRAL=1` está no ambiente. A
primeira limpeza de cada banco também é a do Django, e é dela que saem a lista de tabelas, o mapa
de chaves estrangeiras e a impressão das tabelas de referência. Se a consulta de sujas falha,
porque um caso de `tests/migrations/` deixou o esquema noutro estado, a limpeza volta a ser a do
Django e o preparo se refaz.

A primeira versão tinha um defeito que o protótipo não mostrou. Depois de repovoar as tabelas de
referência, os ids mudam, e a impressão guardada ficava velha: toda limpeza seguinte daquele
worker refazia o `post_migrate`. A suíte deu 508s, e o sinal rodou em ~300 casos. A impressão agora
se refaz depois de cada repovoamento, e o sinal roda 6 vezes por suíte: uma por worker e uma em
cada um de dois casos que mexem nas tabelas de propósito.

Quatro casos novos, em `tests/integration/test_limpeza_dos_casos_transacionais.py`, chamam a
limpeza no meio do próprio corpo e conferem o banco: nenhuma linha fora das tabelas de referência;
as tabelas de referência intactas com os mesmos ids; a tabela alterada recriada; e a limpeza
seguinte sem repovoar de novo. Os quatro reprovaram contra versões sabotadas da limpeza.

| Rodada | Limpeza | Parede | Teardown transacional | Resultado |
|---|---|---:|---:|---|
| `base3` | `LIMPEZA_INTEGRAL=1` | 576s | 443 ms | 11 632 passando, 11 pulados |
| `final4`, logo em seguida | enxuta | **451s (−22%)** | 285 ms | idêntico, caso a caso |
| `final2` | enxuta | 493s | 324 ms | idêntico, caso a caso |
| `final3` | enxuta | 489s | 310 ms | 1 falha, de tempo de parede (abaixo) |

O par `base3`/`final4` rodou em sequência, nas mesmas condições da máquina, e é a comparação
justa: −22%. As outras duas rodadas, mais cedo, ficaram ~40s acima. Com as três bases (571, 556,
576) e as três rodadas enxutas, a média vai de 568s a 478s (−16%). Em todas, o mesmo desfecho em
cada um dos 11 643 casos e a mesma lista de pulados, linha a linha, exceto pela falha abaixo.

**A falha da `final3` não é da limpeza.**
`tests/performance/test_ocupacao.py::test_a_apuracao_cabe_no_dobro_do_tempo_da_emissao_da_ordem`
compara dois tempos de parede, de milissegundos, medidos um depois do outro no mesmo caso: deu
11 ms contra 4 ms, com um teto de 2×. Entre as duas medidas não há limpeza nenhuma. É a carga dos
outros três workers, e o caso pode reprovar com a limpeza de hoje do mesmo jeito. Fica registrado,
e não corrigido.
