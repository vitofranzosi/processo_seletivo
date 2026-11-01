# Implementation Plan: Leitura do conteúdo não publicado na gestão

**Branch**: `claude/112-leitura-do-nao-publicado` | **Date**: 2026-11-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/112-leitura-do-nao-publicado/spec.md`

## Summary

Uma permissão nova, `rascunho:ler`, nos quatro papéis que preparam, revisam, publicam ou conduzem
Editais (`D-001`); uma regra única, na camada de aplicação de `publicacoes`, que devolve o alcance
de um ator sobre um Edital, uma Retificação ou um Processo — nenhum, existência ou conteúdo
(`D-002`); duas portas na interface que a aplicam antes de qualquer leitura e de qualquer
conferência de estado, com 404 para quem não tem a existência e a recusa explicada da `033` para
quem só a tem (`D-003`, `D-004`); a lista filtrada em lote, sem consulta nova (`D-006`). Uma matriz
rota × ator por URL direta e um guardião que lê o [inventário das rotas](contracts/inventario-das-rotas.md)
fecham a feature e a rota escrita amanhã (`D-008`).

## Technical Context

**Language/Version**: Python 3.13, Django (o do `pyproject.toml`)

**Primary Dependencies**: as do projeto; nenhuma nova

**Storage**: PostgreSQL; **nenhuma migration** ([data-model](data-model.md))

**Testing**: pytest contra PostgreSQL (`make test-pg`), com `tests/authorization/`,
`tests/interface/` e os guardiões de `tests/`

**Target Platform**: o monólito Django de sempre

**Project Type**: aplicação web (monólito com templates)

**Performance Goals**: a lista com o mesmo número de consultas, com e sem a permissão (SC-1065); as
demais portas sem consulta além da que já lê o Edital e as Publicações

**Constraints**: Princípio III (negar por padrão, menor privilégio, IDOR); a gramática das recusas e
o inventário das negativas da `033`; a CSP sem `unsafe-inline` (o detalhe reduzido não ganha estilo
inline); a varredura de citações

**Scale/Scope**: 99 rotas classificadas no inventário; ~17 views com porta nova ou trocada; 12
identidades na matriz

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como esta feature o cumpre | Situação |
|---|---|---|
| I. Linguagem ubíqua | "Edital não publicado" se define pela Publicação, que é o conceito do domínio, e não pela situação (FR-3501) | ✅ |
| II. Imutabilidade | Nada se grava; a Publicação append-only é a âncora do alcance | ✅ |
| III. Segurança | Negar por padrão: só quatro papéis leem; verificação no backend, rota a rota, antes do estado; IDOR coberto por matriz de URL direta; nenhuma recusa vaza existência | ✅ — é o propósito da feature |
| IV. Regras explícitas | Uma regra (FR-3506), uma permissão própria, recusas pela gramática da `033` | ✅ |
| V. Rastreabilidade | Matriz FR → D → T → teste; guardião do inventário; nenhuma citação inventada | ✅ |
| VI. Completude de jornada | As jornadas dos papéis do fluxo, da comissão e do auditor ficam inteiras (US2, US3, SC-1062, SC-1066) | ✅ com as P- respondidas |

**Reavaliado depois do desenho**: sem violação. A única tensão é a P-2 (emenda à FR-017 da `020`),
que é decisão de produto, e não de implementação; enquanto não respondida, o plano segue a spec.

## Project Structure

### Documentation (this feature)

```text
specs/112-leitura-do-nao-publicado/
├── spec.md
├── plan.md
├── research.md            # D-001 a D-008 e o inventário de 01/11
├── data-model.md          # a permissão, o Alcance e a regra
├── quickstart.md          # a verificação à mão
├── contracts/
│   ├── inventario-das-rotas.md   # lido pelo guardião
│   └── recusas.md
├── rastreabilidade.md
├── checklists/requirements.md
└── tasks.md
```

### Source Code

```text
backend/processo_seletivo/
├── interface/
│   ├── identidade.py              # PAPEIS: rascunho:ler em quatro papéis
│   ├── views.py                   # _edital_para_ler, _retificacao_para_ler, _processo_para_ler;
│   │                              # lista, detalhe, compor*, previa*, anexo_do_rascunho, praticar_ato,
│   │                              # retificar, retificacao_*, processo_*, supervisao, _edital_do_fragmento,
│   │                              # e as rotas P
│   ├── relatorio.py, avisos.py, assistente.py, duvidas.py, prototipo_do_assistente.py   # rotas P
│   ├── atos_retificacao.py        # em_curso_por_edital recebe só os Editais alcançados
│   ├── visao_geral.py             # FR-3514
│   └── templates/interface/detalhe.html   # o detalhe reduzido (FR-3509)
└── publicacoes/application/
    └── leitura_do_nao_publicado.py   # Alcance e a regra (D-002)

backend/tests/
├── publicacoes/test_leitura_do_nao_publicado.py          # a regra, sem requisição
├── authorization/test_leitura_do_nao_publicado.py        # a matriz rota × ator (FR-3524)
├── authorization/test_papel_da_leitura_do_rascunho.py    # grafia e conjunto fechado (FR-3502, FR-3523)
├── test_rotas_do_nao_publicado.py                        # o guardião do inventário (FR-3525)
└── performance/ (ou interface/) test_lista_*             # o orçamento da lista (SC-1065)

specs/033-navegacao-por-capacidade/inventario-das-negativas.md   # linhas novas (FR-3519)
```

**Structure Decision**: o monólito existente. A regra na aplicação de `publicacoes`, as portas na
interface, junto das sete que a `033` já nomeia.

## Ordem de implementação

1. **A regra e a permissão** (US1/US2 dependem): `rascunho:ler` no catálogo, `Alcance`, a regra e os
   testes dela, sem tocar em view.
2. **As portas e as rotas C e E** (US1, US2, US3): as três portas, depois cada view; a lista por
   último, com o orçamento medido antes e depois.
3. **As rotas P**: a porta de existência, uma a uma.
4. **A matriz e o guardião**: escritos **antes** do passo 2, falhando, e verdes no fim.
5. **Inventário da `033`, documentação** (CLAUDE.md não muda; o quickstart e a nota do papel da
   `111` sim).

## Riscos

| Risco | Mitigação |
|---|---|
| Uma jornada perde uma tela que ninguém lembrou | A matriz cobre as rotas que cada papel usa; SC-1062 exige zero mudança de expectativa fora das listadas |
| O detector da `033` acusa a guarda de 404 como recusa vestida de inexistência | `D-004`: conferir antes; se acusar, a porta entra no inventário como deliberada, sem afrouxar o detector |
| A lista ganha consulta (prefetch das Publicações) | `D-006`: medir com `django_assert_num_queries` antes e depois; o prefetch troca a consulta das Retificações em curso, que o ator sem a permissão deixa de fazer |
| Testes existentes usam integrante ou papel sem a permissão para abrir Edital em elaboração | Levantados na T005; cada um muda de papel ou passa a afirmar a recusa, e entra na rastreabilidade |
| A `111` mergeia antes e dá `material:gerar` a um papel novo | FR-3523 e o guardião de conjunto fechado; a P-2 da `111` já proíbe atribuir o papel antes desta |

## Complexity Tracking

Sem violação a justificar.
