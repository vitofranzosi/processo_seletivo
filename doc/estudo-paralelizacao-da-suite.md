# A suíte contra PostgreSQL em paralelo

**Data:** 2026-10-17
**Origem:** a queixa de 17/10 — `make test-pg` em ~22 min na máquina, o job `test` do CI em ~29 min
(1729s de pytest no run `39026104033`), num processo só.
**Natureza:** estudo com proposta. O que já está no PR é o que não muda comportamento de ninguém —
a dependência e a correção de um arquivo de teste. **`Makefile` e workflow só mudam com o "sim" do
usuário.**

## A resposta curta

Com `pytest-xdist`, **4 workers e `--dist worksteal`**, a suíte local cai de **1441s para 600s
(2,4×)**, com os mesmos **11 457 passando e 11 pulados**, a mesma lista de pulados, linha a linha, e
os mesmos 11 468 casos executados. Nenhuma garantia de banco deixou de ser provada: cada worker
tem o seu banco de teste, com os seus gatilhos e os seus privilégios, e os casos transacionais
continuam transacionais.

Para chegar lá foi preciso corrigir **um** arquivo de teste, e só ele.

## Onde vai o tempo

Suíte serial, `main` em `a41b67c0`, banco próprio, cada caso cronometrado por fase:

| Casos | Quantos | Tempo | Média |
|---|---:|---:|---:|
| transacionais | 3108 (27%) | 1131s (**79%**) | 364 ms |
| com banco, em `ROLLBACK` | 2257 (20%) | 201s (14%) | 89 ms |
| sem banco | 6103 (53%) | 96s (7%) | 16 ms |

Só o **teardown** dos transacionais custa 630s — 44% da suíte. É a limpeza do Django depois de cada
caso que não pode terminar em `ROLLBACK`, e ela faz duas coisas: `TRUNCATE` de todas as tabelas
(~125 ms por caso) e, em seguida, o `post_migrate` que recria tipos de conteúdo e permissões
(~107 ms). Não há caso isolado que domine: o arquivo mais caro, `test_migrations.py`, leva 43s de
1441. O custo é largo e uniforme, que é exatamente o perfil que se paraleliza bem.

## O que disputava recurso do cluster

Um banco de teste por worker já vem do `pytest-django` (`test_<DB_NAME>_gw0`, `_gw1`…). O que não
vem é o que é do **cluster**, e não do banco. Foi conferido um a um:

- **Os papéis de conformidade** (`tests/integration/test_database_permissions.py`). O nome era
  fixo, e quatro workers criavam e derrubavam o mesmo papel: **51 erros** em 92 casos com `-n 4`,
  os mesmos `cannot be dropped because some objects depend on it` que a memória do projeto já
  registrava entre worktrees. Agora o nome leva o worker e o `DB_NAME` — o que já separa os
  bancos —, e o arquivo passa inteiro em paralelo e em série. A correção vale também para duas
  worktrees ao mesmo tempo, que era o caso antigo.
- **`ps_runtime_teste`** (`divulgacao/test_imutabilidade.py`). Criado uma vez e nunca derrubado, só
  recebe privilégio por banco, e é um caso só: não há corrida. Ficou como está.
- **Advisory locks** do domínio são por banco no PostgreSQL. Não se cruzam entre workers.
- **A fixture `autouse` das Unidades** (060) grava o Cefor no banco do caso, e cada worker tem o
  seu. Nada a fazer.
- **Arquivos e portas**: os testes escrevem em `tmp_path` (que o pytest separa por worker) e abrem
  porta 0. Nada fixo.
- **Conexões**: oito workers ficam longe do `max_connections = 100` da instalação local.

## As medições

Todas na mesma máquina (15 núcleos), mesmo commit, um banco por rodada, uma rodada de cada vez:

| Rodada | Parede | Passando | Pulados |
|---|---:|---:|---:|
| serial (referência) | **1441s** | 11 457 | 11 |
| `-n 4`, distribuição padrão (`load`) | 1057s | 11 457 | 11 |
| `-n 4 --dist worksteal` | **600s** | 11 457 | 11 |
| `-n 8 --dist worksteal` | 549s | 11 457 | 11 |

**A distribuição decide mais que o número de workers.** Com o `load` padrão, três dos quatro workers
terminaram e ficaram ~6 minutos ociosos esperando o quarto, que tinha recebido a fila mais pesada.
Com `worksteal`, quem termina rouba da fila dos outros, e os quatro fecharam entre 577s e 590s de
trabalho.

**Mais workers rendem pouco.** De 4 para 8 o ganho é de 9%. Cada caso transacional fica ~1,8× mais
caro em paralelo do que em série (651 ms contra 364 ms com 4 workers) — os bancos são separados,
mas o disco e o WAL do cluster são um só. Oito também pesariam numa máquina menor que esta.

**A variância é grande.** A mesma fatia de 71 casos transacionais deu 67s, 36s, 37s e 29s em rodadas
seguidas, com o Bluetooth do macOS tomando um núcleo inteiro. Os números acima são de uma rodada
cada; a diferença entre 600s e 1441s está muito acima desse ruído, a entre 549s e 600s não.

## A proposta

1. **`Makefile`**: `test-pg` passa a rodar `pytest -n $(PYTEST_WORKERS) --dist worksteal`, com
   `PYTEST_WORKERS ?= 4`. `make test-pg PYTEST_WORKERS=0` volta ao serial, para depurar um caso
   que só falha em companhia.
2. **Workflow**: o passo `uv run pytest` vira `uv run pytest -n 4 --dist worksteal`. O
   `ubuntu-latest` de repositório público tem 4 vCPUs, e o PostgreSQL do serviço divide com eles.
   **A projeção — 1729s × 600/1441 ≈ 12 min — não está medida**, e a primeira execução no PR é que
   diz. Se o runner saturar, 3 workers é o próximo passo, e não 8.
3. **`AGENTS.md`**: o parágrafo do tempo da suíte e o de "um banco de teste por worktree" (o sufixo
   `_gwN` e o fim da disputa pelos papéis).

O `make test` (SQLite) fica serial: ele não é o modo confiável, e os casos dele que acoplam pela
ordem — o `~` literal do `AGENTS.md` — não ganham nada sendo embaralhados.

## O que não entrou, e fica registrado

- **`synchronous_commit = off`** por sessão de teste. Localmente não se distinguiu do ruído — o
  `fsync` do macOS não espera o disco. No Linux do CI pode valer, e se mede lá se o usuário quiser.
- **Truncar só as tabelas com linha**, e **dispensar o `post_migrate` depois de cada caso**. Somam
  ~230 ms por caso transacional, mas mexem na limpeza do Django, e a segunda pode deixar teste que
  dependa de permissão do Django sem a linha. É otimização de outra natureza e pede medição própria.
