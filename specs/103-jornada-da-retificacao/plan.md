# Implementation Plan: Jornada operacional da Retificação

**Branch**: `claude/silly-cerf-78b884` | **Date**: 2026-10-30 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/103-jornada-da-retificacao/spec.md`, com as decisões
D-001 a D-008 tomadas no pedido da feature.

## Summary

Três leituras e uma escrita, todas sobre o que o domínio já tem:

1. **Uma derivação só do que a Retificação pede a seguir** (R-001). `interface/atos_retificacao.py`
   ganha o próximo responsável por situação, a previsão da recusa por segregação (chamando as duas
   funções do Edital em `publicacoes/application/selectors.py`), as ofertas de ato com motivo e o
   resumo de uma Retificação em curso. Lista, detalhe do Edital, tela de Retificar, detalhe da
   Retificação e confirmação leem daí.
2. **A descoberta** (R-002, R-003). Uma consulta por tela: `Retificacao.objects.filter(edital__in=…,
   status__in=EM_CURSO)`. O detalhe do Edital ganha a seção "Retificações em curso"; a Lista ganha a
   marca por Retificação na célula de situação do Edital; a tela de Retificar lista as em curso antes
   do formulário.
3. **O detalhe e a confirmação** (R-004). Quem age a seguir, quem já atuou, o motivo da devolução,
   "Editar a Retificação", o ato desabilitado com o motivo, a entrega do ato e o aviso de
   homologação.
4. **A edição do mesmo registro** (R-005 a R-008). Uma rota nova,
   `/gestao/retificacoes/<id>/editar`, que reaproveita o formulário de Retificar sobre o **conteúdo
   proposto**. A diferença da edição se funde com as alterações já gravadas por uma função pura,
   `publicacoes/domain/fusao.py`, conferida pelo resultado; a gravação é `edit_retification`, que
   passa a registrar `ALTERAR_RASCUNHO` na trilha.

**O risco está em dois lugares.** A fusão (R-006), que precisa reproduzir exatamente o conteúdo
conferido, e é por isso que ela se confere a si mesma. E o formulário de Retificar, extenso e cheio
de ida e volta, que não pode mudar de comportamento na criação: a view é partida em duas portas e um
miolo comum, sem mexer no que o miolo faz.

## Technical Context

**Language/Version**: Python 3.13 (o `backend/pyproject.toml` do projeto)

**Primary Dependencies**: Django. Nenhuma dependência nova.

**Storage**: PostgreSQL. Nenhuma migration, tabela ou coluna. Um tipo de evento já existente
(`ALTERAR_RASCUNHO`) passa a ser gravado também para a Retificação. O `M` do `provisionar` continua 41.

**Testing**: pytest contra PostgreSQL (`make test-pg`). A fusão em `tests/unit/publicacoes/`; a
derivação dos atos em `tests/unit/interface/`; as jornadas por sessões `Client` independentes em
`tests/interface/test_jornada_da_retificacao.py`; o orçamento de consultas com
`django_assert_max_num_queries`.

**Target Platform**: a gestão (`/gestao/`): Lista, detalhe do Edital, Retificar, detalhe e
confirmação da Retificação, e a edição nova.

**Project Type**: monólito web Django com interface server-side.

**Performance Goals**: a Lista e o detalhe do Edital leem as Retificações em curso numa consulta,
qualquer que seja o número delas (FR-2705, FR-2707). A derivação por Retificação não consulta o banco.

**Constraints**: CSP em recusa (sem estilo nem script embutido); toda classe nova com regra na folha;
nenhum `raise Http404` novo em view (a edição usa `_retificacao_do_ator`, que já está no inventário
da `033`); nenhuma permissão nova; a segregação continua no servidor e continua lendo `prepared_by`.

**Scale/Scope**: um módulo de domínio novo (`fusao.py`), funções novas em `atos_retificacao.py`, uma
view nova e a partição da view de Retificar, um parcial de template novo, edições em cinco templates,
regras em duas folhas, um evento a mais no comando de edição.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como esta feature o atende |
|---|---|
| I. Publicação imutável | Nada publicado muda. A edição só aceita Retificação em elaboração, como o comando já impõe. |
| II. Nada é excluído | A edição substitui as alterações de um ato em preparação, como o comando já fazia pela API; a trilha registra cada edição. Nenhum dado normativo publicado é tocado. |
| III. Segurança e auditoria | Negar por padrão continua: 403, 404 e 409 vêm dos comandos. A edição passa a ser auditada (D-006). A listagem mostra só o que o detalhe já mostra ao mesmo público. |
| IV. A recusa é do domínio | A tela antecipa, nunca autoriza: a segregação antecipada chama as mesmas funções do Edital, e o comando continua recusando. |
| V. Rastreabilidade | Spec, plano, tarefas, matriz em `rastreabilidade.md`, citações conferidas por `test_citacoes_de_requisito.py`. |
| VI. Capacidade só conta com porta | É o objetivo da feature: a edição e a homologação ganham caminho pela navegação. |
| Simplicidade | Nenhuma fila, nenhum estado novo, nenhum motor (FR-2732). |

**Resultado**: passa, sem violação a justificar.

## Project Structure

### Documentation (this feature)

```text
specs/103-jornada-da-retificacao/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/telas.md
├── checklists/requirements.md
├── checklists/jornada.md
├── tasks.md
├── rastreabilidade.md
└── verificacao.md
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── publicacoes/
│   ├── domain/fusao.py                       # novo: a fusão conferida (R-006)
│   └── application/retificacoes.py           # edit_retification registra ALTERAR_RASCUNHO
├── interface/
│   ├── atos_retificacao.py                   # próximo responsável, segregação, ofertas, resumo
│   ├── views.py                              # lista, detalhe, retificar partida, editar nova
│   ├── urls.py                               # retificacao-editar
│   ├── templates/interface/
│   │   ├── _retificacoes_em_curso.html       # novo: a lista em curso (Edital e Retificar)
│   │   ├── detalhe.html, lista.html
│   │   ├── retificar.html                    # modo de edição
│   │   ├── retificacao_detalhe.html, retificacao_confirmar.html, _impedimento.html
│   └── static/interface/telas/{lista,retificar}.css, gestao/…  # regras das classes novas
backend/tests/
├── unit/publicacoes/test_fusao_da_edicao.py
├── unit/interface/test_atos_da_retificacao.py
├── interface/test_jornada_da_retificacao.py
└── interface/test_auditoria_passagem_da_retificacao.py   # os quatro xfail sem a marca
```

**Structure Decision**: o monólito existente; a regra pura no domínio de publicações, a derivação de
tela em `interface/atos_retificacao.py`, como os atos do Edital em `interface/acoes.py`.

## Complexity Tracking

Nenhuma violação a justificar.
