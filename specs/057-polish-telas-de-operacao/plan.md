# Implementation Plan: Polish das telas de operação

**Branch**: `claude/polish-operation-screens-435f15` | **Date**: 2026-09-30 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/057-polish-telas-de-operacao/spec.md`

## Summary

Pôr a hierarquia das ações na ordem da frase que governa — a ação do dia é a mais visível, a
excepcional a mais discreta, a destrutiva nunca a mais forte — no Detalhe do Edital, na Condução do
marco e na Lista de Editais (T2, T1); recolher o glossário repetido das telas de marco e de
matrículas (D2); trocar moldura por divisor na Atenção, na Auditoria, nos documentos da inscrição e
nas fichas curtas (T3); formatar números, datas e plurais que a interface compõe para a tela (F8);
estreitar a matriz de Alocação (T4); e pôr o envio de documento do portal numa linha (D5).

O que governa o desenho é a 2ª decisão recebida: **nenhuma ação entra, sai ou muda de destino**.
Por isso a lista de destinos de cada tela é capturada antes e depois, por papel
([D-017](research.md)), e a única mudança em Python fora do F8 é uma função pura que **reparte** o
conjunto de ações que já existe ([D-002](research.md)).

## Technical Context

**Language/Version**: Python 3.12, Django 5 (templates); CSS à mão; JavaScript sem build

**Primary Dependencies**: nenhuma nova

**Storage**: N/A — nenhuma migration, nenhum modelo, nenhuma view nova

**Testing**: pytest (`make test-pg`), com os testes de JavaScript por `tests/test_javascript.py`;
guardas da folha em `test_acessibilidade.py`, `test_larguras.py` e `test_escala_da_mesa.py`; a
varredura `test_vocabulario_da_composicao.py`; um arquivo novo, `tests/interface/test_polish_da_057.py`

**Target Platform**: navegador atual; 1280 × 900 e 375 px

**Project Type**: monólito web Django (gestão e portal server-rendered)

**Performance Goals**: HTML da distribuição abaixo de 120.000 caracteres ([D-001](research.md))

**Constraints**:
- a lista de destinos de ação de cada tela tocada é idêntica, por papel;
- toda classe nova tem regra; `max-width` só em rem, ch, % ou token;
- comentário novo de folha é comentário de template;
- estilo de uma tela só vai para o `estilo_da_pagina` dela;
- texto que sai da tela (publicado, PDF, "o que mudou", registro do ato) não muda.

**Scale/Scope**: ~18 templates da gestão, um parcial do portal, as duas folhas, `acoes.py`,
`views.py` (a montagem do contexto de duas telas), `revisao.py`, `supervisao.py`,
`conducao_do_marco.py` e `retificacao.py` (só o F8)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como esta feature o cumpre |
|---|---|
| I. Linguagem ubíqua | Nenhum rótulo de ação muda. O glossário continua com o mesmo texto, recolhido. |
| II. Imutabilidade | Nada publicado é tocado; o PDF fica de fora; o texto que vai para o registro do ato fica como está ([D-015](research.md)). |
| III. Segurança e auditoria | Nenhuma view, permissão ou escopo muda; a trilha de auditoria mostra os mesmos dados. A lista de destinos por papel é idêntica ([D-017](research.md)). |
| IV. Regras explícitas | Nenhuma regra de domínio muda. A escolha da ação principal é apresentação, e mora num lugar só ([D-002](research.md)). |
| V. Qualidade, rastreabilidade e simplicidade | Sem componente novo: `como-preencher`, `ul.documentos`, `.ficha`, `.ligacao` e os filtros `pontuacao` e `plural` já existem. Cada requisito tem linha na [rastreabilidade](rastreabilidade.md). |
| VI. Completude de jornada | Antes e depois das mesmas telas, no mesmo banco, com as listas de ações comparadas ([verificação](verificacao.md)). |

**Resultado**: passa, sem violação a justificar. Re-checado depois do desenho: idem.

## Project Structure

### Documentation (this feature)

```text
specs/057-polish-telas-de-operacao/
├── spec.md
├── plan.md              # este arquivo
├── research.md          # D-001 a D-018, e as nove decisões recebidas
├── data-model.md        # os elementos das telas — não há entidade de domínio
├── contracts/
│   └── telas.md         # o contrato de cada elemento, com a medida que o prende
├── quickstart.md        # como repetir a medição
├── verificacao.md       # antes e depois, e as listas de ações
├── rastreabilidade.md
├── capturas/            # PNG antes/depois
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
backend/processo_seletivo/interface/
├── acoes.py                       # `hierarquia`; `Acao.quantidade`
├── views.py                       # detalhe e lista: o conjunto repartido
├── revisao.py                     # F8
├── supervisao.py                  # F8
├── conducao_do_marco.py           # F8
├── retificacao.py                 # F8 (só o resumo do acréscimo)
└── templates/interface/
    ├── base.html                  # grupo de ações, terminais, zerada, sinais, auditoria, ficha curta, matriz
    ├── detalhe.html               # T2
    ├── marco.html                 # T2 e D2
    ├── lista.html                 # T1
    ├── ordenacao.html, corte.html, corte_historico.html, ocupacao.html,
    │   convocacao.html, sorteio.html, matriculas.html   # D2
    ├── processo_detalhe.html, supervisao.html, _sinal.html  # T3 (só a folha, se bastar)
    ├── auditoria.html             # T3 (só a folha, se bastar)
    ├── inscricao_detalhe.html     # T3
    ├── distribuicao.html, minha_etapa.html  # T3
    └── alocacoes.html             # T4

backend/processo_seletivo/portal/templates/portal/
├── _documentos.html               # D5
└── base.html                      # D5

backend/tests/interface/test_polish_da_057.py   # novo
```

**Structure Decision**: nenhuma estrutura nova. A feature edita arquivos existentes, mais um arquivo
de teste e um registro em `doc/`.

## Orçamento de caracteres

A distribuição está em ~83.000 caracteres antes da feature, com mais de 30.000 de margem
([D-001](research.md)). O que entra na folha comum: o grupo de ações e o grupo terminal (~400), a
ação zerada (~80), a ficha curta (~35), a matriz em duas linhas (~200 líquidos); o que sai: o
cartão de sinal, o cartão de evento de auditoria e as regras dos requisitos apresentados (~600). A
Distribuição é a própria tela medida, e a ficha dela muda: o teto é medido de novo depois dessa
tarefa, e não só no fim.

## Ordem de implementação

Na ordem de entrega que o prompt dá para o caso de faltar espaço — T2, T1, D2, F8, T3, T4, D5 —,
uma tela por vez, com a lista de destinos recapturada e `test_acessibilidade` rodado depois de cada
uma.

## Fases

- **Fase 0 — pesquisa**: [research.md](research.md).
- **Fase 1 — desenho**: [data-model.md](data-model.md), [contracts/telas.md](contracts/telas.md) e
  [quickstart.md](quickstart.md).
- **Fase 2 — tarefas**: `tasks.md`, pelo `/speckit-tasks`.

## Complexity Tracking

Sem violação da Constituição a justificar.
