# Implementation Plan: Instrução do recurso

**Branch**: `claude/spec-036-instrucao-do-recurso` | **Date**: 2026-09-19 | **Spec**: [spec.md](spec.md)

**Input**: [specs/036-instrucao-do-recurso/spec.md](spec.md)

## Summary

O parecer que o avaliador escreve passa a **chegar a quem ele foi escrito para servir**: ao candidato,
enquanto o prazo de recurso corre; e a quem julga, por um **ato de instrução** que anexa a prova
àquele recurso, com alcance que termina na decisão e rastro que permanece.

Fecha o `ACH-43` — **o último `P0` aberto** — e o `ACH-42`.

**O Phase 0 não contradisse a spec, e isso é a primeira vez nesta série.** Ele a **encolheu em dois
pontos** e pediu um parágrafo novo, que já entrou:

| Medição | Efeito |
|---|---|
| a auditoria **já registra leitura**, com padrão da `031` | a `FR-534` deixa de ser mecanismo novo |
| o parecer **já está carregado** na tela de quem julga | a `US2` é autorização, e não consulta |
| o candidato **já lê um motivo** | entrou a `FR-525a`: o parecer vem **ao lado**, não no lugar |

## Technical Context

**Language/Version**: Python 3.13

**Primary Dependencies**: Django 5.2.17; sem dependência nova

**Storage**: PostgreSQL. **Há migration** — o ato de instrução é entidade nova, e nasce append-only,
com trigger **e** privilégio ausente, as duas camadas que a Constituição exige

**Testing**: pytest, contra PostgreSQL (`make test-pg`)

**Target Platform**: monólito Django — portal do candidato e interface administrativa

**Performance Goals**: nenhuma meta nova, **e uma rede existente a não romper**: há teste de orçamento
de consulta na tela do recurso. Exibir o que já está carregado não o quebra; buscar de novo, sim

**Constraints**: **concede acesso a dado pessoal** — alcance de um recurso, fim na decisão, registro
do ato e do acesso, e nunca do conteúdo. Nenhuma capacidade nova. Nenhum parecer alterado

**Scale/Scope**: uma entidade nova, duas telas — uma em cada canal —, **um** caso de teste alterado

## Constitution Check

*GATE: passou antes da Phase 0 e foi reavaliado depois da Phase 1.*

| Princípio | Como esta feature responde | Onde |
|---|---|---|
| **III · Segurança, Proteção de Dados e Auditoria** | é o princípio que a governa, e a torna a mais delicada da série. `FR-528` limita o alcance a um recurso, `FR-529` o encerra com a decisão, `FR-531` evita a cópia, `FR-533`/`FR-534` registram ato **e** acesso — e nunca conteúdo | [alcance-da-instrucao.md](contracts/alcance-da-instrucao.md) |
| **II · Imutabilidade e Temporalidade** | `FR-529` faz a distinção que o princípio exige: o **registro** permanece, o **alcance** termina. E `FR-523` aplica ao parecer a doutrina do ato histórico — vale o que o ato citou | [data-model.md](data-model.md) |
| **VI · Completude de Jornada** | a jornada do recurso passa a ser percorrível **pelos dois canais**: `SC-182` pelo portal, `SC-183` pela gestão | [quickstart.md](quickstart.md) |
| **IV · Regras Explícitas** | `FR-530` escreve como **proibição** o que seria fácil fazer em silêncio: ampliar o papel de julgar | `FR-530` |
| **I · Linguagem Ubíqua** | *parecer*, *recurso*, *instrução*, *prazo recursal* são do domínio. `FR-532` reusa a formulação de pedido que o produto já pratica | `FR-532` |
| **V · Rastreabilidade e Simplicidade** | uma entidade, dois contratos, um caso de teste alterado | — |

**Gate: passou.** Nenhuma violação a justificar — a seção *Complexity Tracking* fica vazia e foi
removida.

## Os três riscos que este plano leva a sério

Esta é a primeira feature da série que **concede acesso a dado pessoal**, e os riscos mudam de
natureza: não é mais "a tela mente" ou "o número não fecha" — é "alguém passa a ver o que não devia,
e ninguém percebe".

| Risco | Por que é real | O que responde |
|---|---|---|
| **O alcance virar permissão** | guardar "quem pode ver" é o caminho mais curto, e produz exatamente uma permissão com outro nome | `FR-530`; o alcance é **derivado** do estado do recurso; cenário 3, passo 5 — o mesmo julgador em **outro** recurso |
| **O alcance sobreviver ao ato** | ninguém percebe o que continua aberto; o defeito não tem sintoma | `FR-529`, `SC-185`, cenário 4 |
| **O conteúdo vazar para a trilha** | registrar "o que foi anexado" convida a registrar o texto | `FR-533`/`FR-534` registram **espécie e escopo**; cenário 5, passo 2, é contraprova **obrigatória** |
| **Desfazer a garantia da `033`** | a feature existe para **acrescentar** o que mostrar, e a tela hoje é um beco honesto que não oferece o que não alcança | `FR-532`, e o caso que permanece em `R-6` |
| **Substituir o motivo pelo parecer** | são parecidos e ficam lado a lado | `FR-525a`, e o [contrato do que o candidato lê](contracts/o-que-o-candidato-le.md) |
| **Apagar a frase do template** | ela diz *"nenhum parecer"*, falando de **terceiro**, e emendá-la parece limpeza | o contrato manda **emendar dizendo a distinção**, e não apagar |

## Estrutura da entrega

### Documentação (esta feature)

```text
specs/036-instrucao-do-recurso/
├── spec.md
├── plan.md                        # este arquivo
├── research.md                    # Phase 0 — a medição
├── data-model.md                  # Phase 1
├── quickstart.md                  # Phase 1
├── contracts/
│   ├── alcance-da-instrucao.md
│   └── o-que-o-candidato-le.md
├── checklists/requirements.md
└── tasks.md                       # produzido pelo /tasks
```

### Código (raiz do repositório)

```text
backend/processo_seletivo/
├── recursos/
│   ├── models.py                  # a entidade nova, append-only
│   ├── migrations/                # a migration, com trigger e privilégio
│   └── application/               # o ato de instrução, e o alcance derivado
├── interface/
│   ├── views.py                   # a peça passa a expor o que foi instruído
│   └── templates/interface/recurso.html
└── portal/
    ├── views.py                   # o acompanhamento passa a trazer o parecer
    └── templates/portal/acompanhamento.html

backend/tests/
├── integration/recursos/          # o ato, o alcance, e o fim dele
├── portal/                        # o que o titular lê, e quando
└── interface/                     # o que quem julga alcança, antes e depois
```

**Structure Decision**: monólito existente. O ato vive em `recursos/`, que é o agregado que ele
instrui. O alcance é **derivado** — quem julga aquele recurso, enquanto ele não estiver decidido —, e
não persistido como lista: persistir a lista seria criar uma permissão com outro nome, que é o que a
`FR-530` proíbe.

## O que fica fora, e onde está dito

A spec tem a lista inteira. Os dois que mais convidam a escorregar:

- **As duas datas-limite contraditórias do recurso** — `ACH-41`. É a tela vizinha e a tentação é
  grande, mas a causa é outra: validação cruzada entre fontes normativas, que é o `E-4`.
- **O painel de condução** — `E-6`, a próxima da fila e a nota mais baixa do relatório.
