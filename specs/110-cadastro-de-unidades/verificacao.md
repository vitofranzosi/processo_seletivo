# Verificação: Cadastro de unidades administrado pela aplicação (110)

Três seções, uma por incremento (D-019), e uma quarta, separada, para a validação funcional por
pessoas — critério de aceite humano, que nenhum resultado de suíte substitui (SC-1048, T051).

## A — Integridade do escopo (31/10/2026)

**Base**: `main` em `81ce6e94`, com a `108` e a `109` integradas.

| Verificação | Resultado |
|---|---|
| `ruff check` e `ruff format --check` | limpos |
| `make check` (inclui `makemigrations --check`) | sem problema; nenhuma migration pendente |
| Os casos novos e o guardião das migrations, isolados (`test_escopo_imutavel`, `test_isolamento_entre_unidades`, `agenda/test_fonte`, `migrations/test_migrations`) | 31 passando, nenhum pulado |
| `make test-pg`, 4 workers, `DB_NAME=ps_110_escopo` | **13905 passando, 14 pulados**, 0 falhas, 549,9 s |

**Os 14 pulados** são os 12 deliberados do `CLAUDE.md` mais dois de grupo opcional ausente nesta
worktree — o tokenizer (`assistente`) e as jornadas do navegador (`navegador`). Nenhum caso desta
feature foi pulado: os gatilhos só se testam no PostgreSQL, e a suíte rodou nele.

**O que se provou.**

- Os dois gatilhos recusam a mudança do escopo de Processo e de Edital por `update()`, por `save()`
  e por SQL direto, com a conexão superusuária da suíte; o `save()` completo que regrava o mesmo
  escopo passa, e as outras colunas mudam (FR-3333). Os gatilhos da `060` continuam (FR-3334).
- O único teste que mudava o escopo, o da agenda, passou a criar o Edital da Serra pelos atores da
  Serra, e verifica o mesmo que verificava (FR-3335, EC-15).
- As quatro áreas sem segunda unidade (D-014) respondem como inexistente ao ator de `campus-a`, cada
  uma depois de um controle em que o ator do Cefor alcança o objeto, e nada grava — nem evento de
  trilha (FR-3336). **Nenhum vazamento.**

**Achado registrado, sem correção.** A API administrativa valida o corpo antes de conferir o
escopo: um corpo inválido recebe 422 tanto para objeto alheio quanto para inexistente. Não revela
existência — a resposta é a mesma nos dois casos —, e por isso não é vazamento. O teste manda corpos
válidos para chegar à conferência do escopo.

**Migrations.** `processos` passou de 4 para 5 no guardião da `022`, com justificativa; os dois
gatilhos entraram em `TRIGGERS_POR_APP["processos"]`, o que exercita a reversão. Nenhuma tabela
append-only nova: o `M` do provisionamento continua 46.

## B — Entrada de homologação

Não iniciado: espera o usuário aceitar a recomendação de ambiente (D-017, D-018).

## C — Fonte oficial e administração

Não iniciado.

## Validação funcional (SC-1048, T051) — critério de aceite humano

Não realizada. Depende de B e de C.
