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

## B — Entrada de homologação (31/10/2026)

**Base**: o incremento A (PR #350), empilhado — a spec só existe nele. Recomendação de ambiente
aceita pelo usuário em 31/10.

| Verificação | Resultado |
|---|---|
| `ruff check` e `ruff format --check` | limpos |
| `make check` | sem problema; nenhuma migration |
| `tests/homologacao`, `tests/test_configuracao_producao.py` e `tests/seguranca`, isolados | 231 passando |
| `make test-pg`, 4 workers, `DB_NAME=ps_110_escopo` | **13917 passando, 14 pulados**, 0 falhas, 829,6 s |

Os 14 pulados são os mesmos do incremento A.

**O que se provou.**

- O provedor é subclasse do simulado da `106`: a declaração de teste e o bilhete de uso único vêm
  da herança, sem criptografia própria e sem proteção nova (FR-3342).
- Produção o recusa no *boot* pelo pacote e, copiado para fora de `tests.`, pela declaração; sob a
  marca de produção, `provedor_configurado` o apaga em execução, e a entrada responde 503 (FR-3342).
- O caminho do roteiro G funciona de ponta a ponta: a pessoa cadastrada por
  `conceder_administracao_institucional --provedor homologacao` aparece na página, só ela, e
  escolhê-la entra no escopo institucional com a permissão do vínculo (FR-3343).
- O bilhete escolhido não serve de novo, e o retorno sem o estado da ida é recusado, como com
  qualquer adaptador (FR-3343, FR-3023 da `106`).
- **Simplificado depois, no mesmo dia**: saiu o descarte dos bilhetes das outras linhas da página.
  Quem está na página já escolhe qualquer pessoa, e o ambiente é local, sintético e descartável — o
  descarte não protegia nada. Medido de novo só o que essa mudança alcança:
  `tests/homologacao`, `tests/test_configuracao_producao.py`, `tests/seguranca` e os três guardiões
  de documentação, isolados contra PostgreSQL — **1346 passando**. A mudança é só de código de
  teste; a suíte inteira medida acima não foi repetida.
- A suíte de segurança da `106` e da `107` passa sem mudança (`tests/seguranca`).

**A VM de homologação não mudou**: nenhuma settings, nenhum roteiro. O ambiente novo está no §10.3
do guia de produção.

## C — Fonte oficial e administração

Não iniciado.

## Validação funcional (SC-1048, T051) — critério de aceite humano

Não realizada. Depende de B e de C.
