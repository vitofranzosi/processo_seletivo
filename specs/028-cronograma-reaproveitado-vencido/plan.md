# Implementation Plan: Cronograma reaproveitado não nasce publicável

**Branch**: `claude/cronograma-datas-vencidas-196da2` | **Date**: 2026-09-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/028-cronograma-reaproveitado-vencido/spec.md`

---

## Summary

Um Edital cujo período de inscrições já venceu deixa de ser publicável, e um cronograma vencido
deixa de se anunciar concluído. Três achados novos entram na conferência de conteúdo — evento no
passado e ano divergente como **advertência**, período de inscrições encerrado como **erro
impeditivo** —, todos condicionados ao ato, todos endereçando o Evento, e nenhum deles tocando uma
data. O selo da etapa Cronograma passa a considerar validade em vez de existência.

**A abordagem técnica cabe numa frase: quase tudo já está no repositório, e o trabalho é ligar.** A
pesquisa mediu três coisas que mudaram o formato do plano:

- **A leitura "o período está encerrado" já existe**, em `inscricoes/domain/periodo.py`, lendo o
  mesmo dicionário que a validação lê e já recebendo `agora` por injeção. É a mesma que o portal
  obedece — e tem de ser, ou o sistema recusaria publicar um Edital que em seguida aceitaria
  inscrição ([research.md](research.md), `T-002`).
- **A conferência já roda no ponto mais cedo.** `interface/views.py` já chama `_pendencias` em
  **cada** página do assistente e já entrega a cada etapa só o que se resolve nela; a
  `FR-356` custa zero linha de interface (`T-004`).
- **O instante único por ato já é praticado.** `command_context()` rende um `timezone.now()` por
  transação, e `submit_edital` e `publish_edital` já o distribuem. A `FR-341` é passá-lo adiante
  (`T-001`).

Isso decide o formato: **nenhuma migration, nenhum degrau de schema, nenhuma permissão nova, nenhum
campo no conteúdo publicado.** O que se escreve é um módulo de calendário com um predicado, três
achados em `validation.py`, um parâmetro, e um critério de selo.

**O custo real está num lugar só, e a pesquisa o mediu.** Seis lugares do repositório publicam hoje
um Edital com as inscrições já encerradas, porque nada os impede: cinco fixtures de teste e o
segundo Edital da demonstração. Eles passam a publicar com o período aberto e a fechá-lo por
Retificação — que é o que acontece na realidade, e que a `FR-355` autorizou por escrito (`T-008`).

**Uma correção de leitura, declarada.** A primeira passada desta pesquisa apontava a suíte como o
custo principal, estimando ~11 asserções a ajustar. A medição arquivo a arquivo desmentiu:
**nenhuma** asserção da suíte lê lista não filtrada de achados, e a advertência nova não quebra uma
sequer (`T-007`).

---

## Technical Context

**Language/Version**: Python 3.13

**Primary Dependencies**: Django 5.2, Django REST Framework 3.16. **Nenhuma dependência nova** — e a
recusa é explícita: congelar o relógio na suíte exigiria `freezegun` ou `time-machine`, e a troca foi
avaliada e rejeitada (`T-008`, `T-010`)

**Storage**: PostgreSQL 16. **Nenhuma migration.** Nenhuma coluna acrescentada, alterada ou
removida; nenhum campo novo no conteúdo canônico; nenhum degrau de esquema

**Testing**: pytest + pytest-django, contra PostgreSQL (`make test-pg`). Unidade em
`tests/unit/editais/`; interface em `tests/interface/`; integração em `tests/integration/`;
aceitação em `tests/acceptance/`

**Target Platform**: servidor web; interface administrativa server-side com htmx, sem SPA e sem build
de front

**Project Type**: monólito Django conduzido por especificação

**Performance Goals**: a conferência dos três achados é uma passada sobre o `schedule` do snapshot,
que já é percorrido pela conferência de forma. O selo troca um `.exists()` por um `.all()` sobre a
mesma relação. **Nenhuma consulta nova**

**Constraints**: nenhuma data é lida, escrita ou sugerida pelo sistema; nenhum byte de conteúdo
publicado muda; nenhuma leitura de calendário fora da zona institucional; nenhum achado desta feature
num ato de Retificação

**Scale/Scope**: um Cronograma tem uma dezena de Eventos. O alvo é o Edital em elaboração, um por vez

---

## Constitution Check

*GATE: verificado antes da Fase 0 e reavaliado depois da Fase 1. Ambas as passadas: aprovado.*

| Princípio | Como a feature se posiciona | Veredito |
|---|---|---|
| **I — Linguagem ubíqua** | Nenhum termo novo. "Cronograma", "Evento", "período de inscrições" e "advertência" são os que a tela, o domínio e os Editais já usam. O único conceito acrescentado — *vencido* — é predicado, e não entidade | ✅ |
| **II — Integridade normativa e imutabilidade** | É o princípio que **motiva** a feature por dois lados. O de calendário, literal: *"Regras de calendário DEVEM usar a zona temporal institucional"* e *"operações relacionadas DEVEM compartilhar referência temporal consistente na mesma transação"* — é a `FR-341` e a `FR-342`. E o da fonte única: a leitura do período encerrado é a **mesma** que o portal obedece (`T-002`). Nada publicado é reescrito (`FR-365`), e nenhum campo entra no conteúdo (`FR-353`) | ✅ |
| **III — Segurança e proteção de dados** | Nenhuma permissão nova, nenhum ator novo, nenhum dado pessoal. Os achados são leitura de datas de um Edital em elaboração, por quem já compõe | ✅ |
| **IV — Regras explícitas e consistência** | Os três achados vivem no domínio, e a interface só os apresenta — é o que faz a regra valer para a API tanto quanto para a tela. *"A operação DEVE validar inconsistências, classificá-las como informação, aviso ou erro impeditivo e bloquear a publicação diante de erro impeditivo"* é exatamente a `D-004` | ✅ |
| **V — Qualidade, rastreabilidade e simplicidade** | Cada FR tem cenário no [quickstart.md](quickstart.md). A simplicidade é o eixo: **zero migration, zero módulo de aplicação novo, zero dependência**. O que se acrescenta de estrutura é um módulo de domínio com um predicado | ✅ |
| **VI — Completude de jornada** | O quarto Edital da demonstração percorre a jornada **até onde ela para**, com o motivo dito — e para pela mesma porta pela qual uma pessoa passaria (`FR-366`, `T-009`) | ✅ |

### Invariantes do domínio tocados

| Invariante da Constituição | Efeito |
|---|---|
| "Regras de calendário DEVEM usar a zona temporal institucional definida pelo domínio" | passa a valer para a conferência do Cronograma, que hoje não tem regra de calendário nenhuma |
| "operações relacionadas DEVEM compartilhar referência temporal consistente na mesma transação" | a conferência passa a usar o `now` do `command_context`, o mesmo que a publicação registra |
| "Cada informação normativa estruturada DEVE possuir uma única fonte autoritativa" | a resposta "as inscrições estão encerradas" continua tendo **uma** fonte, e a validação passa a consultá-la em vez de reescrevê-la |
| "Um Edital publicado NÃO PODE ser sobrescrito, apagado ou silenciosamente modificado" | nenhuma data é tocada (`FR-351`), nenhum conteúdo publicado muda (`FR-365`) |
| "A operação DEVE validar inconsistências, classificá-las [...] e bloquear a publicação diante de erro impeditivo" | é a `FR-346`, pelo mecanismo que já existe |
| "APIs DEVEM ter contratos explícitos" | a forma publicada não muda; o comportamento sim, e está em [contracts/cronograma-vencido.md](contracts/cronograma-vencido.md) |

**Sem violações. A tabela de Complexity Tracking fica vazia.**

---

## Project Structure

### Documentation (this feature)

```text
specs/028-cronograma-reaproveitado-vencido/
├── plan.md              # Este arquivo
├── research.md          # Fase 0 — T-001 a T-010
├── data-model.md        # Fase 1
├── quickstart.md        # Fase 1
├── contracts/
│   └── cronograma-vencido.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Fase 2 — do $speckit-tasks, não deste comando
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── editais/domain/
│   ├── calendario.py           # NOVO — o predicado `vencido` e a leitura do ano (T-003, T-006)
│   └── validation.py           # o parâmetro `agora`, os três achados (T-001, T-002, T-005)
├── publicacoes/application/
│   └── publish_edital.py       # passa o `now` da transação nas duas conferências (T-001)
├── interface/
│   └── views.py                # o selo do Cronograma por validade (FR-359)
└── processos/management/commands/
    └── seed_demo.py            # o segundo Edital retifica para fechar; o quarto, reaproveitado (T-008, T-009)

backend/tests/
├── unit/editais/
│   ├── test_calendario.py              # NOVO — o predicado e o ano, sem banco
│   └── test_cronograma_vencido.py      # NOVO — os três achados, por ato
├── interface/
│   └── test_selo_do_cronograma.py      # NOVO — o selo, e o cenário do 12/2027 na composição
├── integration/
│   ├── avaliacoes/test_conjunto_fechado.py     # publica aberto, retifica para fechar (T-008)
│   ├── portal/test_vitrine.py                  # idem
│   ├── portal/test_situacao_inscricoes.py      # idem
│   ├── portal/test_cronograma_publico.py       # idem
│   ├── supervisao/test_pulso.py                # idem
│   └── test_seed_demo.py                       # o quarto Edital
└── acceptance/
    └── test_cronograma_reaproveitado.py # NOVO — o percurso do quickstart
```

**Structure Decision**: monólito Django existente, com **um** módulo de domínio novo e nenhum
diretório novo. `editais/domain/calendario.py` existe para que o predicado tenha um lugar só — a
alternativa era escrevê-lo duas vezes, uma para o snapshot e outra para o ORM, e é a divergência que
a feature inteira existe para não produzir.

---

## Ordem de execução

A ordem importa porque três passos, feitos fora de lugar, produzem defeito silencioso.

**1. O predicado, no domínio.** `editais/domain/calendario.py`: `vencido(inicio, termino, *, agora)` e
a leitura do ano na zona institucional. Função pura, sem Django, testável sem banco. É o passo de que
os dois lados — conferência e selo — dependem para concordar.

**2. O instante de referência.** O parâmetro `agora` em `validate_for_publication`, resolvido **uma
vez** no topo, com `None` lendo o relógio. Os dois comandos passam o `now` que já têm.

> **Armadilha 1 — o relógio lido a cada Evento.** Resolver `agora` dentro de cada verificação faria
> dois Eventos do mesmo cronograma serem julgados contra instantes diferentes, e um cronograma cujo
> Evento vence no meio da passada produziria um relatório que não corresponde a estado nenhum. É a
> `FR-341` ao pé da letra, e o teste que a fixa entra **junto** com o parâmetro.

**3. As duas advertências** — evento no passado e ano divergente —, endereçando o Evento.

> **Armadilha 2 — o ano lido em UTC.** Um Evento em 31/12 às 23:30 em Vitória é 1º de janeiro em
> UTC. Lido sem converter, um Edital correto seria acusado de divergir de si mesmo — e só nos
> últimos horários do ano, que é a forma mais cara de defeito que existe, porque não reproduz quando
> alguém vai olhar. A classe já cobrou uma vez no CI do PR #102
> ([doc/achado-teste-com-data-em-utc.md](../../doc/achado-teste-com-data-em-utc.md)), e a `SC-118` é
> o que a guarda daqui em diante.

**4. O impedimento**, reusando `periodo_de_inscricoes`.

> **Armadilha 3 — o caminho `/schedule`.** `DESTINO_DA_PENDENCIA` tem uma entrada por caminho exato
> para `/schedule`, que manda para a etapa **Inscrição** — e está certa, porque é lá que a
> *designação* do período se resolve. Mas a **data** se corrige na etapa Cronograma. Escrever o
> impedimento em `/schedule` casaria com a chave exata e mandaria quem lê para uma tela sem campo de
> data nenhum: é a `FR-349`, e é o defeito que a auditoria já registrou uma vez em outra tela. O
> achado endereça `/schedule/id=<uuid>/endAt`, e aí o roteamento existente acerta sozinho.

**5. O selo**, em `_progresso`, chamando o predicado do passo 1.

**6. Os seis lugares que publicam com a inscrição encerrada.** Passam a publicar abertos e a fechar
por Retificação, com o ajudante `retify` que já existe. É aqui que a suíte volta ao verde, e cada
queda é lida — não silenciada.

**7. A demonstração.** O quarto Edital, criado pelo serviço de reaproveitamento a partir do segundo,
deixado em elaboração. Por último, porque é quem prova que os seis anteriores se encontram.

**8. A suíte inteira**, `make lint check test-pg`.

---

## O que este plano deliberadamente não faz

- **Não move `inscricoes/domain/periodo.py` para `editais/domain/`.** Seria a arrumação mais correta
  por camada, e fica registrada em `T-002` com a condição que a torna devida: um segundo consumidor
  em `editais`.
- **Não torna os fixtures de base relativos a `agora`.** Eles nasceram no futuro e hoje estão no
  passado; a advertência nova não quebra nada, e mudar o instante deles mudaria os bytes canônicos
  de todo conteúdo publicado por eles. Fica registrado em `T-007`.
- **Não usa nem remove `REFERENCE_NOW`**, a constante morta de `tests/fixtures/clock.py`. Congelar o
  relógio da suíte foi avaliado e recusado em `T-010`; o achado fica, e o que fazer com ele é
  decisão de quem governa o escopo.

---

## Complexity Tracking

> Sem violações da Constituição. Nada a justificar.
