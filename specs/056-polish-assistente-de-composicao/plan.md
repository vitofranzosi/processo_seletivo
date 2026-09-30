# Implementation Plan: Polish do assistente de composição

**Branch**: `claude/assistente-composicao-polish-4d8abf` | **Date**: 2026-09-30 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/056-polish-assistente-de-composicao/spec.md`

## Summary

Dar densidade ao assistente de composição **dentro do padrão que existe**: o stepper numa linha
(F1), as ações do cartão na linha da legenda e a legenda com o nome do item (F2), o Evento lido numa
faixa (F2), o Conteúdo do Edital compacto (F3), a Revisão em grade de rótulo e valor (F4), texto
longo em área de texto (F5), a navegação de Anexos na largura das outras etapas (D4) e, por último,
a ordem do Perfil no Retificar (F6).

O que governa o desenho é a 2ª decisão recebida: **nenhum campo sai, nenhum nome muda**. Por isso
toda mudança de template é de lugar e de controle, nunca de `name`; e o envio de "Salvar rascunho" de
cada etapa é capturado antes e depois ([D-005](research.md)).

As duas decisões de desenho arriscadas — o stepper e as ações na legenda — foram **prototipadas na
página viva antes de escritas**, a 1280 × 900: 66 px de stepper e o h2 de Perfis em y = 416
([D-002](research.md)); ações no canto da legenda sem linha própria ([D-003](research.md)).

## Technical Context

**Language/Version**: Python 3.12, Django 5 (templates); CSS à mão; JavaScript sem build

**Primary Dependencies**: nenhuma nova

**Storage**: N/A — nenhuma migration, nenhum modelo, nenhuma view de gravação

**Testing**: pytest (`make test-pg`), com os testes de JavaScript por `tests/test_javascript.py`
(`node --test`); guardas da folha em `test_acessibilidade.py`, `test_larguras.py` e
`test_escala_da_mesa.py`; um arquivo novo, `tests/interface/test_polish_da_056.py`

**Target Platform**: navegador atual; 1280 × 900 e 375 px

**Project Type**: monólito web Django (gestão server-rendered)

**Performance Goals**: HTML da distribuição abaixo de 120.000 caracteres (hoje 83.093, [D-001](research.md))

**Constraints**:
- nenhum nome de campo muda; o envio de cada etapa é o mesmo conjunto de pares;
- toda classe nova tem regra; `max-width` só em rem, ch, % ou token;
- comentário novo de folha é comentário de template;
- estilo de uma etapa só vai para o `estilo_da_pagina` dela.

**Scale/Scope**: ~14 templates, a folha da gestão, `ordenacao.js`, `revisao.py`, `origens.py`,
`retificacao.py` (três tipos de campo), uma tag de template

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como esta feature o cumpre |
|---|---|
| I. Linguagem ubíqua | Nenhum rótulo muda. A legenda ganha o nome do item com o vocabulário que ele já tem. |
| II. Imutabilidade | Nada publicado é tocado; o PDF fica de fora; nenhuma gravação muda. No Retificar muda o controle de três campos, e não o que o ato registra ([D-011](research.md)). |
| III. Segurança e auditoria | Nenhuma view, permissão ou escopo muda. |
| IV. Regras explícitas | Nenhuma regra de domínio muda. A Revisão mostra as mesmas linhas, na mesma ordem ([D-010](research.md)). |
| V. Qualidade, rastreabilidade e simplicidade | Sem componente novo: a grade de `dl` de "Dados da inscrição", as duas vozes da legenda do Retificar, o grupo de ações que já existe. Cada requisito tem linha na [rastreabilidade](rastreabilidade.md). |
| VI. Completude de jornada | Antes e depois das mesmas telas, no mesmo banco, e o envio de cada etapa comparado ([verificação](verificacao.md)). |

**Resultado**: passa, sem violação a justificar. Re-checado depois do desenho: idem.

## Project Structure

### Documentation (this feature)

```text
specs/056-polish-assistente-de-composicao/
├── spec.md
├── plan.md              # este arquivo
├── research.md          # D-001 a D-013, e as nove decisões recebidas
├── data-model.md        # os elementos do assistente — não há entidade de domínio
├── contracts/
│   └── assistente.md    # o contrato de cada elemento, com a medida que o prende
├── quickstart.md        # como repetir a medição
├── verificacao.md       # antes e depois, e o envio de cada etapa
├── rastreabilidade.md
├── capturas/            # PNG antes/depois
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
backend/processo_seletivo/interface/
├── templates/interface/
│   ├── base.html                  # stepper (F1); ações na legenda (F2); navegação (D4)
│   ├── _acoes_da_linha.html       # sai a reserva de rótulo
│   ├── _evento.html               # F2 — legenda, ações, ordem da faixa
│   ├── _etapa.html                # F2 — legenda, ações
│   ├── _documento.html            # F2 — legenda, ações; F5 — Instrução
│   ├── _modalidade.html           # F2 — legenda, ações
│   ├── _perfil.html               # F5 — Descrição
│   ├── compor_conteudo.html       # F3
│   ├── compor_revisao.html        # F4
│   ├── compor_anexos.html         # D4
│   └── _retificacao_linha.html    # F5 (linhas do texto longo); F6
├── templatetags/interface_extras.py  # o filtro dos trechos da Revisão; o da ordem do Perfil
├── static/interface/ordenacao.js  # escreve a posição em `[data-ordem]`
├── origens.py                     # `Rotulada`; `com_origem` preserva o rótulo
├── revisao.py                     # as linhas rotuladas nascem por `Rotulada`
└── retificacao.py                 # três campos de `CAMPOS_RAIZ` para `TEXTO_LONGO`

backend/tests/
├── interface/test_polish_da_056.py   # novo
└── javascript/ordenacao.test.js      # o caso da legenda com `[data-ordem]`
```

**Structure Decision**: nenhuma estrutura nova. A feature edita arquivos existentes, mais um arquivo
de teste.

## Orçamento de caracteres

Com 83.093 caracteres na distribuição, a margem é de ~36.900 ([D-001](research.md)). O que entra na
folha comum: a grade do stepper (saem o `flex` e a base de 160 px), o posicionamento das ações na
legenda e a sua queda em tela estreita (saem as duas regras de `.campos>.acoes-da-linha` e a reserva
de rótulo), e o `max-width:none` da navegação. Estimativa: **≈ +300**. O Conteúdo e a Revisão vão
para o `estilo_da_pagina` de cada uma e não contam. O saldo real é medido pelo teste isolado e vai
para o [verificacao.md](verificacao.md) e para o PR.

## Ordem de implementação

Uma etapa do assistente por vez, com o envio recapturado e `test_acessibilidade` rodado depois de
cada uma. Na ordem de entrega que o prompt dá para o caso de faltar espaço — F1, F3, F2, F4, F5, D4,
F6 —, que também é a ordem de risco crescente, salvo o F2, que mexe em script.

## Fases

- **Fase 0 — pesquisa**: [research.md](research.md).
- **Fase 1 — desenho**: [data-model.md](data-model.md), [contracts/assistente.md](contracts/assistente.md)
  e [quickstart.md](quickstart.md).
- **Fase 2 — tarefas**: `tasks.md`, pelo `/speckit-tasks`.

## Complexity Tracking

Sem violação da Constituição a justificar.
