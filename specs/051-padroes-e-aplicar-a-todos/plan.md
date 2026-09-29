# Implementation Plan: Padrões do Edital e "aplicar a todos"

**Branch**: `claude/nova-051-edital-patterns-499aa7` | **Date**: 2026-09-28 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/051-padroes-e-aplicar-a-todos/spec.md`

## Summary

Um gesto e um punhado de padrões, sem campo novo no conteúdo publicado. O gesto lê o que está
**digitado** na etapa, calcula numa função pura o efeito em cada Perfil — *nasce*, *substitui*, *sem
mudança*, *fora do alcance* —, devolve a mesma tela com a prévia, e, confirmado com a impressão do que
foi mostrado, grava pelo `replace_draft` de sempre e registra o gesto na trilha, na mesma transação
([research](research.md), R-001 a R-003). A Revisão diz a origem de cada valor: por comparação, para o
padrão e a derivação; pelo registro do gesto, para o materializado (R-004). Os padrões nascem no
cartão novo ou preenchem o vazio na leitura do formulário, e nunca alcançam conteúdo publicado nem
Retificação (`FR-915`).

**Entrega em dois PRs.** Este leva a P1 — US1 a US4, a composição inteira e a Revisão. A US5, o gesto
na Retificação, fica para o seguinte: reusa a função pura e a prévia, e o que muda é a tradução de cada
efeito em Alterações da `048` e a guarda de campo não retificável, que merecem revisão própria
(R-009).

## Technical Context

**Language/Version**: Python 3.12, Django 5 — o monólito existente.

**Primary Dependencies**: as do projeto; nenhuma nova. htmx já vendorizado; nenhum JavaScript novo — o
gesto é um envio de formulário, como a recusa e a restauração.

**Storage**: PostgreSQL. **Uma migration**: a coluna `detalhe` (JSON, nula) em `RegistroAuditoria`,
para o registro do gesto (R-004). Nenhuma tabela nova, nenhum campo novo no rascunho nem no conteúdo
publicado. O `rounding` da regra normativa já existe como `JSONField`; passa a ter forma lida.

**Testing**: pytest contra PostgreSQL (`make test-pg`, `DB_NAME=ps_051`).

**Target Platform**: interface Django server-rendered da gestão.

**Project Type**: web — `backend/processo_seletivo/`.

**Performance Goals**: a prévia de 66 Perfis é uma função pura sobre o formulário já lido; nenhuma
consulta por destino.

**Constraints**: `replace_draft` apaga o que não for reenviado; append-only em duas camadas (a trilha
já é); `FR-428` da `030` (nenhuma ajuda visível no cartão); `FR-421` da `030`; o contrato de
mutabilidade como fonte única; o guardião da Revisão (`LIDOS`/`NAO_MOSTRADOS`).

**Scale/Scope**: 7 Perfis no 28/2026, 16 no 140/2025, 66 na projeção multicampi.

## Constitution Check

| Princípio | Como esta feature o cumpre |
|---|---|
| I. Linguagem ubíqua | *Aplicar aos demais Perfis*, *nasce*, *substitui*, *fora do alcance*; nenhum termo técnico na tela (`UX-112`). |
| II. Imutabilidade | Nenhum padrão alcança conteúdo publicado ou Retificação (`FR-915`); nenhum valor publicado é apagado, e o que a API gravou nos campos opacos passa a sobreviver à gravação da etapa Perfis (`FR-933`). |
| III. Auditoria | Cada gesto é uma linha da trilha, append-only, com autor, instante, origem e destinos (`FR-921`). |
| IV. Regras explícitas — **o invariante da 1.2.0** | O gesto declara o alcance e o efeito por destino antes da confirmação, e a confirmação carrega a impressão do que foi mostrado (`FR-916`–`FR-919`); todo valor padrão, derivado ou materializado aparece na Revisão com a origem (`FR-934`, `FR-935`); os campos que não se corrigem depois aparecem antes da submissão (`FR-936`). A validação continua no domínio: o gesto grava pelo `replace_draft`, que valida como sempre. |
| V. Simplicidade | Uma função pura por unidade, uma prévia comum, um caminho de gravação. Sem herança, sem tabela de proveniência. |
| Nada é excluído | O gesto nunca remove Modalidade, e o marco só é criado onde falta. |

**Gate: passa.** A migration é a única estrutura nova, e é coluna nula numa tabela append-only que já
existe.

**Reavaliação depois do desenho: passa.** A `FR-943` é regra impeditiva nova, e o custo dela — Editais de
teste que cortam sem forma — é medido antes de escrever (tarefa T004), como a memória da `046` manda.

## Project Structure

### Documentation (this feature)

```text
specs/051-padroes-e-aplicar-a-todos/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── tela-da-previa.md
│   └── registro-do-gesto.md
├── rastreabilidade.md
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── editais/domain/aplicacao.py          # NOVO — a regra única, pura: unidades, efeitos, aplicação, impressão
├── editais/domain/marcos.py             # CORTE_PADRAO, corte_padrao()
├── editais/domain/quadro.py             # NOVO — sugestão pelo percentual e pelo arredondamento
├── editais/domain/validation.py         # empate não exigido em sorteio; FR-943
├── editais/domain/mutabilidade.py       # comentário do OPACOS (rounding lido pela sugestão)
├── editais/application/aplicacao.py     # NOVO — gravar o gesto: replace_draft + trilha, uma transação
├── auditoria/{models,application}.py    # coluna `detalhe`; record_event(detalhe=)
├── auditoria/migrations/0003_…          # a coluna
├── sorteios/domain/prosa.py             # NOVO — a frase canônica de cada regra
├── interface/aplicacao.py               # NOVO — a prévia em palavras, a leitura do pedido
├── interface/views.py                   # compor_etapa: prévia, confirmação, preencher quadro
├── interface/forms.py                   # prosa, instante do Evento, rounding, Etapa decisória, preservação
├── interface/revisao.py                 # origens; bloco dos campos definitivos
└── interface/templates/interface/
    ├── _previa_da_aplicacao.html        # NOVO
    ├── _marco.html, _modalidade.html, _etapa.html, _linha_do_quadro.html
    ├── compor_perfis.html, compor_classificacao.html, compor_revisao.html
backend/tests/
├── unit/editais/test_aplicacao.py       # a regra única, unidade a unidade
├── unit/editais/test_quadro_sugerido.py
├── interface/test_aplicar_a_todos.py    # prévia, exclusão, divergência, gravação, trilha
├── interface/test_padroes_da_composicao.py
└── interface/test_revisao_origem_e_definitivos.py
```

**Structure Decision**: o monólito existente. A regra mora em `editais/domain` (pura), a gravação em
`editais/application`, e a tela em `interface`, como a `043` fez com o duplicar.

## O que o teste operacional da `DP-18` poderia mudar

O teste não foi feito até 28/09 (não há resultado em `doc/`). Seguimos sem ele, pelas estimativas do
anexo A. O que ele poderia mudar, e onde:

- **Se o setor já inverte a ordem** (compõe o marco antes de duplicar), o ganho da US1 na composição
  cai de ~50 para ~0 no 28/2026; o gesto continua valendo para a correção. Nada no desenho muda.
- **Se a hesitação maior for no corte ou no sorteio**, e não na repetição, a US3 sobe de valor
  relativo — já está na P1.
- **Se a prévia for lida como obstáculo** (quatro efeitos, 66 linhas), a forma a revisar é a `UX-111`:
  agrupar *nasce* e *sem mudança* e abrir só *substitui* e *fora do alcance*. A regra não muda.
- **Se o operador não entender "fora do alcance"**, a frase do motivo é o que se ajusta.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Coluna `detalhe` na trilha | A Revisão precisa saber, depois, de onde veio o valor materializado e se ele ainda é o gravado (`FR-935`) | Só comparação (sem registro) foi a opção B da clarificação, recusada pelo usuário; uma tabela própria exigiria gatilho e privilégio novos para guardar o que a trilha já guarda |
