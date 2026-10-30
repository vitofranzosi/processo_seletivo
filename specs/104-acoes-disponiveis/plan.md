# Implementation Plan: Ações disponíveis

**Branch**: `claude/acoes-disponiveis-104` | **Date**: 2026-10-30 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/104-acoes-disponiveis/spec.md`, com D-001 a D-010.

## Summary

Uma derivação de leitura, `interface/trabalho.py`, monta os objetos de trabalho do ator a partir do
que as telas de detalhe já decidem (R-001). A Lista a chama uma vez e desenha a faixa "Ações
disponíveis para você" antes do inventário (R-002). Na mesma requisição, a Lista passa a ler em lote
as contagens de inscrições e recursos e a segregação dos Editais em revisão ou homologados (R-003,
R-004), troca "Submeter" e "Publicar" do Edital por "Conferir e…" (R-005) e põe o ato da Retificação
na coluna (R-006). O detalhe do Edital deixa de afirmar "Nenhum ato" quando uma Retificação espera a
pessoa (R-007). A devolvida e a reenviada passam a ser ditas a partir de `return_reason` (R-008). A
confirmação de homologar e de devolver ganha a tabela das alterações e as advertências separadas
(R-009). Minhas Etapas ganha estado vazio novo (R-010).

**Onde está o risco**: no custo da Lista, que hoje já paga duas consultas por Edital publicado, e na
coerência entre a faixa, a coluna e o detalhe — que só se garante se os três lerem a mesma função.

## Technical Context

**Language/Version**: Python 3.13 · **Primary Dependencies**: Django; nenhuma nova

**Storage**: PostgreSQL, só leitura. Nenhuma migration; o `M` do `provisionar` continua 41.

**Testing**: pytest contra PostgreSQL. Derivação em `tests/unit/interface/` (sem banco onde der) e
`tests/interface/test_acoes_disponiveis.py` (jornadas A a I por sessões `Client`); escala em
`tests/performance/test_trabalho_em_escala.py`, com `publicar_direto` da Visão Geral.

**Target Platform**: `/gestao/`: Lista, detalhe do Edital, detalhe e confirmação da Retificação,
Minhas Etapas.

**Performance Goals**: a derivação com número constante de consultas para 0, 3, 30 e 300 Editais
(SC-984); a Lista sem consulta por Edital publicado (SC-985), exceto o caso de quem exporta matrícula
(`_pede_requerimento_de_matricula`, por Edital, registrado).

**Constraints**: CSP sem estilo nem script embutido; classe nova com regra na folha; nenhum
`raise Http404` novo; a barra lateral continua sem consulta (076, FR-1715); `details` nativo, sem
script.

**Scale/Scope**: um módulo novo (`trabalho.py`), um parcial (`_acoes_disponiveis.html`), edições em
`acoes.py`, `atos_retificacao.py`, `views.py` (lista, detalhe, confirmação), `retificacoes.py`
(advertências do vigente), seis templates e duas folhas.

## Constitution Check

| Princípio | Como é atendido |
|---|---|
| I. Publicação imutável | Nada publicado muda. |
| II. Nada é excluído | Nenhuma escrita nova. |
| III. Segurança e auditoria | Escopo do ator em toda consulta; nenhuma permissão nova; a derivação só antecipa, os comandos recusam. |
| IV. A recusa é do domínio | A previsão vem de `atos.disponiveis`, `acoes._motivo_previsivel`, `atos_retificacao.ofertas` e `impede_por_segregacao`. |
| V. Rastreabilidade | Spec, plano, tarefas, matriz e verificação na pasta; citações conferidas por teste. |
| VI. Capacidade só conta com porta | É o propósito: o trabalho existente ganha porta na primeira tela. |
| Simplicidade | Nenhuma fila, estado, tabela ou notificação (FR-2829). |

**Resultado**: passa.

## Project Structure

```text
specs/104-acoes-disponiveis/
├── spec.md · plan.md · research.md · data-model.md · quickstart.md
├── contracts/telas.md
├── checklists/requirements.md · checklists/operacao.md
├── tasks.md · rastreabilidade.md · verificacao.md

backend/processo_seletivo/
├── interface/trabalho.py                       # novo: a derivação (R-001)
├── interface/acoes.py                          # contagens em lote; "Conferir e…" (R-003, R-005)
├── interface/atos_retificacao.py               # devolvida, reenviada, espera (R-008)
├── interface/views.py                          # lista, detalhe, confirmação, minhas_etapas
├── publicacoes/application/selectors.py        # participantes em lote (R-004)
├── publicacoes/application/retificacoes.py     # advertências do conteúdo vigente (R-009)
├── interface/templates/interface/
│   ├── _acoes_disponiveis.html                 # novo: a faixa
│   ├── lista.html · detalhe.html · _retificacoes_em_curso.html
│   ├── retificacao_detalhe.html · retificacao_confirmar.html · minhas_etapas.html
└── interface/static/interface/{telas/lista.css, gestao/telas.css}
backend/tests/
├── unit/interface/test_trabalho_do_ator.py
├── interface/test_acoes_disponiveis.py
└── performance/test_trabalho_em_escala.py
```

## Complexity Tracking

Nenhuma violação.
