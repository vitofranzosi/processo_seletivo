# Implementation Plan: O caminho do candidato até a convocação e o Requerimento de Matrícula

**Branch**: `claude/friendly-chaplygin-8884a1` | **Date**: 2026-10-06 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/059-acesso-a-convocacao/spec.md`

## Summary

Três telas do portal passam a levar a duas que já existem. "Minhas inscrições" indica a convocação
aberta e oferece **Ver convocação**; o acompanhamento ganha a seção "Convocação"; e a tela da
convocação e essa seção oferecem **Preencher Requerimento de Matrícula** quando a política da `029`
diz que ele está aberto. Uma regra de vigência só, num seletor novo da `019` lido por conjunto
(`D-001`, `D-002`); o requerimento só é consultado onde há convocação (`D-006`). Nenhuma rota,
migration, regra de domínio ou tela da gestão muda.

## Technical Context

**Language/Version**: Python 3.13 (Django, versão do `pyproject.toml`), templates Django, CSS na folha embutida em
`portal/templates/portal/base.html`

**Primary Dependencies**: as do monólito; nenhuma nova

**Storage**: PostgreSQL — só leitura, nas tabelas da `019` (`convocacao_*`) e da `029`
(`requerimentos_*`); nenhuma escrita nova

**Testing**: pytest + pytest-django contra PostgreSQL (`make test-pg`); `CaptureQueriesContext` para
o orçamento; `Client` do Django para telas e recusas

**Target Platform**: servidor Linux; navegador do candidato, inclusive 375 px

**Project Type**: monólito web (Django, server-rendered)

**Performance Goals**: custo da lista constante no número de inscrições e de convocações
(`SC-426`); zero consultas ao requerimento na lista e no acompanhamento de quem não foi convocado

**Constraints**: recusa uniforme da titularidade (`FR-071`, `FR-399`); nenhum dado pessoal no
endereço (`FR-073`, `FR-401`); leitura não move prazo nem grava trilha fora da tela da convocação
(`D-008`)

**Scale/Scope**: 3 templates alterados, 2 parciais novos, 1 seletor novo, 3 views tocadas, ~5
arquivos de teste

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como esta feature o cumpre | Situação |
|---|---|---|
| I. Linguagem ubíqua | "Convocação", "desfecho", "Requerimento de Matrícula" com o sentido da `019` e da `029`; *vigente* e *em aberto* continuam distintos (`D-001`) | ✅ |
| II. Imutabilidade | Nada escrito; leitura de atos append-only, sucessão respeitada (sucessora mostrada) | ✅ |
| III. Segurança e dados | Titularidade em toda rota, 404 uniforme testado para as quatro rotas e para a lista (`FR-1101`); nenhum dado novo exibido; nenhum dado pessoal no endereço | ✅ |
| IV. Regras no domínio | A disponibilidade do requerimento vem de `apurar` (`FR-1099`); a tela não decide; o estado de prazo vem de `estado_de` | ✅ |
| V. Rastreabilidade e simplicidade | Matriz `rastreabilidade.md`; um seletor, dois parciais, sem camada nova; custo medido em teste | ✅ |
| VI. Completude de jornada | É o princípio que o achado viola: *"uma capacidade que o domínio sustenta mas que nenhuma interface alcança NÃO DEVE ser considerada entregue"*. O cenário fim a fim é pelo canal do candidato, a partir da lista | ✅ — é a razão da feature |

Nenhuma violação; *Complexity Tracking* fica vazio.

**Re-check depois do desenho**: o seletor novo mora em `convocacao/application/selectors.py`, e o
portal o importa como já importa os outros (import tardio dentro da view). Nenhum módulo a montante
da `019` passa a importá-la (`test_dependencia_da_convocacao.py`). ✅

## Project Structure

### Documentation (this feature)

```text
specs/059-acesso-a-convocacao/
├── spec.md
├── plan.md               # este arquivo
├── research.md           # D-001 a D-012
├── data-model.md         # leituras derivadas; nenhuma tabela nova
├── quickstart.md
├── contracts/telas.md    # o que cada estado mostra em cada tela
├── checklists/requirements.md
├── tasks.md              # /speckit-tasks
├── rastreabilidade.md    # matriz requisito → teste (implementação)
└── verificacao.md        # o total da suíte e a verificação no navegador
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── convocacao/application/selectors.py      # + vigentes_por_inscricao (D-001)
└── portal/
    ├── views.py                             # inscricoes, _item_da_lista, acompanhamento, convocacao
    └── templates/portal/
        ├── inscricoes.html                  # indicação, "Ver convocação", nota da concluída
        ├── acompanhamento.html              # inclui a seção
        ├── convocacao.html                  # inclui o chamado ao requerimento
        ├── _convocacao_da_inscricao.html    # novo: a seção do acompanhamento
        ├── _chamado_do_requerimento.html    # novo: D-007
        └── base.html                        # regras das classes novas; ações acima do título (D-010)

backend/tests/
├── interface/test_portal_caminho_da_convocacao.py   # novo: US1, US2, US3
├── authorization/test_convocacao_alheia.py          # novo: US4
├── unit ou integration/convocacao/…                 # vigentes_por_inscricao
├── performance/test_area_do_candidato.py            # + lista com convocações constante
├── integration/requerimentos/test_orcamento_de_consulta.py  # + zero com convocação na lista
└── test_vocabulario_da_convocacao.py                # DA_019 + parciais novos (D-011)
```

**Structure Decision**: o monólito existente. A leitura nova é da `019` e mora no seletor dela; o
portal só traduz para a tela.

## Riscos e como são contidos

| Risco | Contenção |
|---|---|
| A lista passar a consultar por item | Teste de desempenho com 1 e 5 inscrições convocadas, igualdade estrita |
| O acompanhamento passar a ler o requerimento de quem não foi convocado | O teste da `029` continua prendendo zero, sem ser reescrito |
| Duas regras de vigência divergirem | A view da convocação passa a usar o mesmo seletor; teste com sucessão nos três lugares |
| Template novo fugir da varredura da `019` | `DA_019` estendida no mesmo commit |
| Classe nova sem regra | `test_acessibilidade` acusa; regra na folha no mesmo commit |
| Clique cair no título esticado | Medido por `elementFromPoint` antes e depois (`D-010`) |
| Suíte de outra worktree disputar o banco | `DB_NAME=test_ps_059` |

## Complexity Tracking

Vazio — nenhuma violação a justificar.
