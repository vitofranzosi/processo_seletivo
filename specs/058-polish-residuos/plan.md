# Implementation Plan: Polish — os resíduos dos três lotes

**Branch**: `claude/residuos-polish-c7ef91` | **Date**: 2026-10-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/058-polish-residuos/spec.md`

## Summary

Reaplicar, nas telas vizinhas que ficaram de fora, o que a `055`, a `056` e a `057` já decidiram:
os atos irreversíveis do Processo contornados e à parte, como os do Edital (R1); a tabela da Lista
e a da Condução numa moldura que rola abaixo de 60 rem, como a matriz de Alocação (R2); a seção da
Matrículas sem `.resumo`, como a Ocupação (R3); a coluna de nota dos Resultados pela regra numérica
que já existe (R4); os plurais de tela pelo filtro `plural` (R5); os campos numéricos das Etapas
sem zeros à direita (R6); a coluna de rótulos da Revisão com largura fixa (R7); o motivo de sucessão
com o mesmo controle nas quatro telas (R8); e a decisão 003 da `056` com o valor da folha (R9).

O que governa o desenho é a 2ª decisão recebida: **nenhuma ação entra, sai ou muda de destino, e
nada muda no que se grava**. As duas provas — destinos por papel e envio de "Salvar rascunho" — são
capturadas antes e depois ([D-010](research.md)); para o R6, a prova é o rascunho gravado
([D-005](research.md)).

## Technical Context

**Language/Version**: Python 3.12, Django 5 (templates); CSS à mão

**Primary Dependencies**: nenhuma nova

**Storage**: N/A — nenhuma migration, nenhum modelo, nenhuma view nova

**Testing**: pytest (`make test-pg`); guardas da folha em `test_acessibilidade.py`,
`test_larguras.py` e `test_escala_da_mesa.py`; `test_vocabulario_da_composicao.py`;
`test_citacoes_de_requisito.py`; um arquivo novo, `tests/interface/test_polish_da_058.py`

**Target Platform**: navegador atual; 1280 × 900 e 375 px

**Project Type**: monólito web Django (gestão server-rendered)

**Performance Goals**: HTML da distribuição abaixo de 120.000 caracteres (82.477 em 01/10)

**Constraints**:
- a lista de destinos de ação de cada tela tocada é idêntica, por papel;
- o envio de "Salvar rascunho" das etapas tocadas é idêntico, salvo a grafia dos três números das
  Etapas, e o rascunho gravado é idêntico;
- toda classe nova tem regra; `max-width` só em rem, ch, % ou token;
- comentário novo de folha é comentário de template, sem tag HTML na prosa;
- a moldura não pode virar contêiner de rolagem em tela larga (o cabeçalho fixo da Alocação);
- texto que sai da tela (ato, registro, documento) não muda.

**Scale/Scope**: onze templates da gestão (`processo_detalhe`, `detalhe`, `lista`, `marco`,
`matriculas`, `resultados`, `distribuicao`, `recurso`, `ocupacao`, `ocupacao_historico`,
`compor_base`, `compor_revisao`, `sorteio`), a folha comum (`base.html`), `forms.etapas_do_edital`
(o valor exibido), três testes que prendiam a grafia antiga, e o `research.md` da `056`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como esta feature o cumpre |
|---|---|
| I. Linguagem ubíqua | Nenhum rótulo muda. Os plurais passam a concordar com o número, com as mesmas palavras. |
| II. Imutabilidade | Nada publicado é tocado; o PDF fica de fora; o texto que vai para ato ou registro fica como está ([D-004](research.md)). O valor gravado das Etapas é conferido idêntico ([D-005](research.md)). |
| III. Segurança e auditoria | Nenhuma view, permissão ou escopo muda; a lista de destinos por papel é idêntica ([D-010](research.md)). |
| IV. Regras explícitas | Nenhuma regra de domínio muda. O peso de cada ato do Processo vem do que o próprio ato declara (`irreversivel`) ([D-001](research.md)). |
| V. Qualidade, rastreabilidade e simplicidade | Sem componente novo: `.terminais`, a moldura da Alocação, `.tabela td.numero`, `plural`, `contagem` e `.campo>textarea` já existem. Cada requisito tem linha na [rastreabilidade](rastreabilidade.md). |
| VI. Completude de jornada | Antes e depois das mesmas telas, no mesmo banco, com as provas comparadas ([verificação](verificacao.md)). |

**Resultado**: passa, sem violação a justificar. Re-checado depois do desenho: idem.

## Project Structure

### Documentation (this feature)

```text
specs/058-polish-residuos/
├── spec.md
├── plan.md              # este arquivo
├── research.md          # as dez decisões recebidas, e D-001 em diante
├── data-model.md        # os elementos das telas — não há entidade de domínio
├── contracts/
│   └── telas.md         # o contrato de cada elemento, com a medida que o prende
├── quickstart.md        # como repetir a medição
├── verificacao.md       # antes e depois, e as provas
├── acoes-antes.json     # destinos por papel, antes
├── acoes-depois.json    # idem, depois
├── rastreabilidade.md
├── capturas/            # PNG antes/depois
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
backend/processo_seletivo/interface/
├── forms.py                         # etapas_do_edital: o valor exibido (R6)
└── templates/interface/
    ├── base.html                    # a folha: .terminais (R1) e a moldura (R2)
    ├── detalhe.html                 # perde as regras de .terminais, que sobem para a folha
    ├── processo_detalhe.html        # R1
    ├── lista.html, marco.html       # R2
    ├── matriculas.html              # R3 e R5
    ├── resultados.html              # R4
    ├── distribuicao.html, recurso.html, ocupacao.html, ocupacao_historico.html, compor_base.html  # R5
    ├── compor_revisao.html          # R7
    └── ocupacao.html, sorteio.html  # R8
backend/tests/interface/test_polish_da_058.py   # o que prende cada item
specs/056-polish-assistente-de-composicao/research.md   # R9
```

**Structure Decision**: o monólito existente; nenhuma pasta nova fora de `specs/058-…`.

## Complexity Tracking

Sem violação a justificar.
