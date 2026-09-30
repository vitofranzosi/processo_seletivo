# Implementation Plan: Polish da folha e dos componentes

**Branch**: `claude/polish-folha-componentes-82ee7f` | **Date**: 2026-09-30 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/055-polish-folha-e-componentes/spec.md`

## Summary

Acertar na **folha de estilo** — e não tela a tela — oito defeitos globais da auditoria de polish
(G1 a G8) e dois específicos (D1, F7). Quase tudo é CSS nas duas folhas (`interface/base.html` e
`portal/base.html`); nos templates entram só o G1 (Ocupação, Corte e histórico do Corte), as quatro
ações reclassificadas do G5, o botão do portal, a coluna de pontuação da ordem e os dois campos da
Comissão.

O que governa o desenho é um número: **a tela de distribuição estava a 47 caracteres do teto de
120.000** (medido em 30/09, [D-001](research.md)). Toda regra nova sai de regra velha, e a medida
de cada alteração entra na conta ([§ Orçamento](#orçamento-de-caracteres)).

As decisões de desenho foram **prototipadas antes de escritas**: injetadas como folha na página
viva, a 1280 × 900, e medidas. Os três números que decidem o resto — 40 px para todo botão e todo
controle, e desnível zero na barra de filtro — saíram do protótipo, e não de conta.

## Technical Context

**Language/Version**: Python 3.12, Django 5 (templates); CSS escrito à mão, sem pré-processador

**Primary Dependencies**: nenhuma nova. As folhas vivem dentro de `<style>` nos dois `base.html`, e
os tokens de cor em `shared/_tokens.css.html`

**Storage**: N/A — nenhuma migration, nenhum modelo

**Testing**: pytest (`make test-pg`); as guardas da folha em `tests/interface/test_acessibilidade.py`,
`tests/interface/test_larguras.py` e `tests/performance/test_escala_da_mesa.py`; um arquivo novo,
`tests/interface/test_polish_da_055.py`, com as guardas desta feature

**Target Platform**: navegador (Chrome, Firefox, Safari atuais); 1280 × 900 e 375 px

**Project Type**: monólito web Django (gestão server-rendered + portal do candidato)

**Performance Goals**: o HTML inteiro da tela de distribuição abaixo de 120.000 caracteres

**Constraints**:
- margem inicial de **47 caracteres** sob o teto;
- nenhum comentário removido para abrir espaço;
- `max-width` só em rem, ch, % ou token;
- toda classe citada precisa de regra;
- todo botão de envio declara o seu peso.

**Scale/Scope**: 2 folhas, ~12 templates, 1 arquivo de teste novo

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como esta feature o cumpre |
|---|---|
| I. Linguagem ubíqua | Nenhum rótulo muda: "Publicadas", "Alvo apurado", "Filtrar" continuam as mesmas palavras, só no desenho certo (**FR-1019**). |
| II. Imutabilidade | Nenhuma tabela, nenhum ato, nenhum documento publicado é tocado. O PDF fica de fora. |
| III. Segurança e auditoria | Nenhuma view, permissão ou escopo muda. |
| IV. Regras explícitas | Nenhuma regra de domínio muda. |
| V. Qualidade, rastreabilidade e simplicidade | Sem token novo, sem componente novo: os padrões que já existem (`ul.resumo`, `.botao`, a consulta da Vitrine) são reaproveitados. Cada requisito tem linha na [rastreabilidade](rastreabilidade.md) e uma guarda em teste. |
| VI. Completude de jornada | As medidas "antes" e "depois" são das mesmas telas, no mesmo banco, e vão para a [verificação](verificacao.md). |

**Resultado**: passa, sem violação a justificar. Re-checado depois do desenho: idem.

## Project Structure

### Documentation (this feature)

```text
specs/055-polish-folha-e-componentes/
├── spec.md
├── plan.md              # este arquivo
├── research.md          # D-001 a D-019, e as dez decisões recebidas
├── data-model.md        # os componentes da folha — não há entidade de domínio
├── contracts/
│   └── folha.md         # o contrato visual de cada componente, com a medida que o prende
├── quickstart.md        # como repetir a medição
├── verificacao.md       # antes e depois
├── rastreabilidade.md
├── capturas/            # PNG antes/depois do G1, da barra do assistente e das Inscrições
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── interface/templates/interface/
│   ├── base.html                 # a folha da gestão — G2 a G8, F7 (arquivo)
│   ├── ocupacao.html             # G1
│   ├── ocupacao_historico.html   # G1
│   ├── corte.html                # G1
│   ├── corte_historico.html      # G1
│   ├── ordenacao.html            # G3 — a tabela e a coluna de pontuação
│   ├── inscricoes.html           # G5 — Filtrar
│   ├── distribuicao.html         # G5 — Filtrar
│   ├── comissao.html             # G5 — Filtrar; F7 — Identificador e Nome
│   └── matriculas.html           # G5 — Ver o que sairá vazio
└── portal/templates/portal/
    ├── base.html                 # a folha do portal — G7, D1, F7
    └── requerimento.html         # G5 — Guardar e continuar depois

backend/tests/interface/
├── test_polish_da_055.py         # novo
└── test_acessibilidade.py        # a guarda de peso passa a varrer também o portal
```

**Structure Decision**: nenhuma estrutura nova. A feature só edita arquivos que já existem, mais um
arquivo de teste.

## Orçamento de caracteres

Conta feita no desenho e **refeita na implementação**, com a medida do teste isolado. Negativo é o
que sai; positivo é o que entra. Só conta o que chega ao HTML da distribuição: a folha da gestão e o
próprio `distribuicao.html`. O que vai para `{% block estilo_da_pagina %}` de outra página, para
templates de outras telas ou para a folha do portal não entra.

| Item | Onde | Saldo estimado |
|---|---|---:|
| G2 | `th,td` de `.7rem 1.25rem` para `.5rem .75rem`; saem as duas declarações que ficam iguais à global (`.conferencia-lote`, `.distribuicao`) | ≈ −45 |
| G3 | nada na folha: a tabela da ordem passa a declarar `.tabela` (D-011) | 0 |
| G4 | `.botao` com `border:1px solid transparent` e `line-height`; o secundário troca `border` por `border-color`; o destrutivo perde o `border:none`; a geometria do botão passa a ser partilhada com a ação em barra | ≈ +60 |
| G5 | "Filtrar" da distribuição de `acao` para `botao` | +1 |
| G6 | `h3` global e peso partilhado; saem cinco sobreposições de tamanho e a caixa-alta da Retificação | ≈ −105 |
| G7 | uma regra de altura para `input` e `select` | ≈ +70 |
| G8 | `flex-start`, e a margem do rótulo nos contêineres de botão | ≈ +45 |
| F7 | `input[type="file"].arquivo` com `width:auto` | ≈ +10 |
| **Total** | | **≈ +36**, contra margem de 47 |

Se o saldo real passar da margem, a ordem de corte é a da seção *Quando parar* do prompt: G1,
G2+G3, G4+G5, depois G6, G7, G8, D1, F7.

## Fases

- **Fase 0 — pesquisa**: [research.md](research.md). Medida da margem, protótipo das alturas e da
  barra, e as decisões que o prompt não previu.
- **Fase 1 — desenho**: [data-model.md](data-model.md), [contracts/folha.md](contracts/folha.md) e
  [quickstart.md](quickstart.md).
- **Fase 2 — tarefas**: `tasks.md`, pelo `/speckit-tasks`.

## Complexity Tracking

Sem violação da Constituição a justificar.
