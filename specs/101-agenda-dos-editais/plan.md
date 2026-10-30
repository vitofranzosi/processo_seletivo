# Implementation Plan: Agenda dos Editais

**Branch**: `claude/calendario-processos-seletivos-217bea` | **Date**: 2026-10-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/101-agenda-dos-editais/spec.md`

## Summary

Uma página de leitura na gestão, `/gestao/agenda`, que projeta o cronograma da versão consolidada
**vigente** de cada Edital publicado ou encerrado do escopo do ator em **marcos** — Evento pontual,
abertura e encerramento de período — e os apresenta em duas visualizações: a grade do **Mês**
(inicial) e a lista de **Próximos marcos** (7 ou 30 dias), mais a consulta de um dia. As duas leem
a mesma projeção, com os mesmos filtros, em consultas fixas.

A abordagem é a do estudo
([`doc/estudo-calendario-institucional-2026-10-29.md`](../../doc/estudo-calendario-institucional-2026-10-29.md)):
o carregador em lote `versoes_vigentes` e a régua de fase existentes alimentam funções puras
(`marcos_do_conteudo`, `na_janela`, `semanas_do_mes`, `sintese`), num módulo só de leitura,
`interface/agenda.py`. Nenhuma migration, modelo, cache, endpoint de API ou dependência.

## Technical Context

**Language/Version**: Python 3.13 (`backend/pyproject.toml`)

**Primary Dependencies**: Django (templates renderizados no servidor). O módulo `calendar` da
biblioteca padrão para as semanas do mês. Nenhuma dependência nova; nenhum JavaScript novo.

**Storage**: PostgreSQL — **só leitura**. Lê `Edital` (com `Processo`) e `VersaoConsolidada`.

**Testing**: pytest contra PostgreSQL (`make test-pg`); funções puras testadas sem banco; o ciclo
real de publicação e de Retificação pelos ajudantes `tests/fixtures/publicacao.py`; orçamento de
consultas com `CaptureQueriesContext`, no padrão de `tests/portal/test_consultas_da_vitrine.py`.

**Target Platform**: a gestão (`/gestao/`), na barra lateral, grupo *Trabalho*.

**Project Type**: monólito web Django, interface server-side.

**Performance Goals**: número fixo de consultas — quatro —, igual com 1 e com N Editais e nas duas
visualizações (FR-2646, SC-950). O custo de materializar o conteúdo inteiro de cada versão é medido
na implementação (research R-004).

**Constraints**: CSP em recusa (estilo só por arquivo em `interface/telas/`, sem `style=""`,
`<style>`, `<script>`); classe no template exige regra na folha; contraste pelos pares existentes;
375 px sem rolagem horizontal; vocabulário que nunca diga executado o que é previsto (FR-2642).

**Scale/Scope**: um módulo novo (`interface/agenda.py`), uma view, uma rota, uma entrada na barra,
um símbolo SVG, um template com cinco parciais, uma folha de tela. Dezenas de Editais × 4 a 18
Eventos por unidade.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como esta feature o cumpre | Situação |
|---|---|---|
| I. Linguagem ubíqua | Edital, Evento, Retificação, vigência, período de inscrições; "marco" já é termo da supervisão (`022`) para o Evento que vem; nenhum termo novo para conceito existente | ✅ |
| II. Integridade normativa e temporalidade | lê só a versão vigente no instante da leitura, pelo resolvedor existente; dia na zona institucional; nenhuma segunda fonte de datas (FR-2612 a FR-2616, D-001) | ✅ |
| III. Segurança, dados, auditoria | escopo pelo filtro da consulta; identificador alheio ignorado sem distinção (FR-2610); só dado já público; leitura não é ato auditável — nada grava | ✅ |
| IV. Regras explícitas | a fase é a régua existente; marco × período, cancelado, encerrado, espécie e concentração por regra escrita (D-002, D-005, D-007, D-009, D-010) | ✅ |
| V. Qualidade e simplicidade | sem tabela, fila, migration, cache ou dependência; funções puras testadas sem banco; orçamento de consultas testado | ✅ |
| VI. Jornada demonstrável | a pessoa abre a barra, vê o mês, escolhe o dia e chega ao cronograma publicado pelo navegador (quickstart) | ✅ |

Re-checado depois do desenho (Fase 1): nenhuma violação; *Complexity Tracking* vazio.

## Project Structure

### Documentation (this feature)

```text
specs/101-agenda-dos-editais/
├── spec.md
├── plan.md              # este arquivo
├── research.md          # Fase 0
├── data-model.md        # Fase 1 — as formas derivadas
├── contracts/agenda.md  # Fase 1 — a rota, os parâmetros, os estados, os ganchos
├── quickstart.md        # Fase 1 — validação de ponta a ponta
├── checklists/          # requirements.md (specify) e o do checklist
├── rastreabilidade.md   # requisito → tarefa → teste (na implementação)
└── tasks.md             # speckit-tasks
```

### Source Code (repository root)

```text
backend/processo_seletivo/interface/
├── agenda.py                              # NOVO — projeção, janelas, grade, síntese, leitura
├── views.py                               # + view `agenda`
├── urls.py                                # + path("agenda", ...)
├── navegacao.py                           # + Secao("Agenda", ...)
├── templates/interface/
│   ├── base.html                          # + <symbol id="i-calendario">
│   ├── agenda.html                        # NOVO — página, abas, síntese, filtros, avisos
│   ├── _agenda_mes.html                   # NOVO — grade e períodos do mês
│   ├── _agenda_dia.html                   # NOVO — a relação de um dia
│   ├── _agenda_proximos.html              # NOVO — em curso e dias
│   ├── _agenda_marcos.html                # NOVO — os marcos de um dia, agrupados acima de oito
│   └── _agenda_marco.html                 # NOVO — o item, comum a dia e próximos
└── static/interface/telas/agenda.css      # NOVO

backend/tests/
├── unit/interface/test_agenda.py          # NOVO — funções puras (sem banco)
├── integration/agenda/test_fonte.py       # NOVO — publicação, Retificação, estados, escopo
└── interface/test_agenda.py               # NOVO — tela, filtros, abas, consultas, guardiões
backend/tests/interface/test_folha_estatica.py  # + agenda.css em QUEM_CARREGA
```

**Structure Decision**: derivação e leitura em `interface/agenda.py`, como `visao_geral.py` e
`supervisao.py` — módulos de leitura da gestão. A régua de fase continua no domínio
(`editais/domain`), e não é copiada. Quando um segundo leitor da projeção existir (o `.ics` da fase
2), as funções puras descem para `editais/domain/`, como a `028` e a `047` fizeram com as réguas
delas.

## Fases

### Fase 0 — Pesquisa

[research.md](research.md): R-001 a R-014. Sem `NEEDS CLARIFICATION` remanescente.

### Fase 1 — Desenho

- [data-model.md](data-model.md): `Marco`, `Periodo`, `Janela`, `Dia` da grade, `Sintese`,
  `AvisoDeRetificacao`, `Filtros`, `Leitura`.
- [contracts/agenda.md](contracts/agenda.md): a rota, os parâmetros e seus padrões, os estados da
  página, os links de saída e as classes que os testes leem.
- [quickstart.md](quickstart.md): a verificação de ponta a ponta.

### Ordem de implementação (detalhada em tasks.md)

1. Funções puras de projeção (marcos, períodos, fase, espécie) com testes unitários.
2. Janelas, grade do mês e síntese, com testes unitários.
3. Leitura (`ler`): consultas, filtros, avisos, próximo marco; testes de integração com o ciclo real
   de publicação e Retificação.
4. View, rota, barra, templates e folha; testes de tela, de consultas e dos guardiões.
5. Medição do custo do conteúdo inteiro; prova visual; rastreabilidade; README.
6. Revisão de 29/10 (indicador de períodos, FR-2669 a FR-2671): a pertinência `Periodo.abrange`, a
   contagem por célula em `semanas_do_mes` sobre os períodos já projetados (research R-013), o dia
   consultado com todos os períodos que o abrangem, a forma do indicador (R-014) e o vocabulário
   temporal. Nenhuma consulta nova.

## Riscos

| Risco | Mitigação |
|---|---|
| A régua chamar de *concluído* o que só tem data passada | D-006: a agenda traduz a fase para *data passada*, e um teste de vocabulário reprova as palavras proibidas (FR-2642) |
| O conteúdo inteiro de dezenas de versões pesar | R-004: medido na implementação; a saída é materializar só o cronograma, sem tabela |
| A grade estourar a 375 px | sete colunas de ~45 px, nomes ocultos abaixo de 60rem; verificado no navegador e pelo guardião de larguras |
| Retificação de vigência futura confundir | D-008: anunciada, nunca aplicada; testado antes e depois da vigência com `agora` explícito |
| Classe sem regra, ou par de cor novo, reprovar a suíte | só pares de `PARES` já existentes; toda classe do template com regra em `agenda.css` |

## Complexity Tracking

Nenhuma violação a justificar.
