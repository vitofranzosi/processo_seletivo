# Implementation Plan: A visão institucional dos Processos Seletivos

**Branch**: `claude/spec-processos-seletivos-visao-395a64` | **Date**: 2026-09-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/040-visao-institucional-dos-processos/spec.md`

## Summary

Uma página de leitura em `/gestao/visao-geral`, **acima do nível do Processo**, que responde
dimensão e demanda do conjunto de certames do escopo: quatro números consolidados, uma tabela de
sete colunas por Edital, e quatro filtros — o de ano recortando pelo **corrente** por omissão.

A abordagem técnica é a que a `022` já provou e a `024` já mediu: **um módulo de derivação que só
lê**, consumindo os selectors donos de cada fato, e **uma extração compartilhada** do resolvedor de
versão vigente que o portal já tem. Nenhuma migration, nenhuma entidade, nenhum estado novo — e um
orçamento de consulta **constante no número de Editais**, que é a única propriedade desta feature
que exige teste próprio.

## Technical Context

**Language/Version**: Python 3.13 (`requires-python = ">=3.13,<3.14"`)

**Primary Dependencies**: Django 5.2 · nenhuma dependência nova. Sem JavaScript — a ordenação é do
servidor (`R-008`) e não há gráfico nesta entrega (`D-013`).

**Storage**: PostgreSQL. **Sem migration**: a feature não cria, altera nem remove tabela, coluna ou
índice.

**Testing**: pytest + pytest-django, contra PostgreSQL (`make test-pg`). Quatro famílias já
existentes: `tests/interface/`, `tests/authorization/`, `tests/unit/`, `tests/performance/`.

**Target Platform**: aplicação web servida por Django; a interface administrativa sob `/gestao/`.

**Project Type**: monólito Django — aplicação web de projeto único, sem frontend separado.

**Performance Goals**: **contagem de consultas constante** no número de Editais do recorte, medida
entre 3 e 60 (`SC-209`); e **um snapshot aberto por Edital do recorte**, nunca do acervo
(`SC-214`). Não há meta de tempo de parede: o repositório já decidiu que tempo em suíte é ruidoso e
que contagem determinística é o que detecta a degradação que importa.

**Constraints**: nenhum dado pessoal na página (`FR-584`); nenhuma escrita no módulo de leitura;
nenhuma infraestrutura analítica (`§15` da spec); a gramática da ausência e do zero legítimo
(`FR-591`, `FR-594`) verificada em tela.

**Scale/Scope**: uma rota, uma view, um módulo de derivação, um template, uma extração compartilhada
e uma linha no mapa de papéis. O acervo real é de dezenas de Editais; o limiar que obriga a revisar
é o herdado da `024` — *"quando o catálogo passar de algumas centenas"*.

## Constitution Check

*GATE: verificado antes da Fase 0 e reavaliado após a Fase 1. Nenhuma violação; nenhuma linha em
Complexity Tracking.*

| Princípio | Como esta feature o atende | Verificado por |
|---|---|---|
| **I — Linguagem ubíqua** | Nenhum conceito novo. Os termos da tela são os do domínio: *Edital*, *Perfil*, *inscrições submetidas*, *Em preenchimento* — este último adotado da tela dona, e não inventado (`FR-586`). A §3.1 da spec reconstruiu a terminologia antes de desenhar. **Riscos nomeados**: *recorte* é palavra de spec e não entra na prosa visível (`R-006`) | `test_vocabulario_da_composicao.py` · revisão de texto |
| **II — Integridade normativa** | Vagas saem da **versão consolidada vigente**, nunca da linha de elaboração (`FR-587`, `D-003`). A página não grava nada, não reescreve publicação e não deriva norma. A leitura aceita o instante como argumento, de modo que o número de um instante é reproduzível | `tests/unit/` sobre as derivações, com `agora=` explícito |
| **III — Segurança e dados pessoais** | Capacidade **própria**, negada por padrão (`FR-604`), pelo ponto único `require_permission`. Escopo institucional aplicado na camada de aplicação (`FR-583`). **Zero PII** por construção: todos os números são agregados (`FR-584`). Sem auditoria porque não há operação sensível — `R-009` mede a fronteira contra o precedente que audita | `tests/authorization/` · varredura do HTML em `SC-210` |
| **IV — Regras explícitas** | Nenhuma regra de domínio nova. Todo número vem do selector dono (`FR-582`); o template não calcula. A recusa é do servidor, e esconder o link não a substitui (`FR-482` da `033`) | `SC-207` · `SC-211` |
| **V — Qualidade e simplicidade** | A solução é a mais simples que preserva os requisitos: quatro consultas relacionais e uma extração compartilhada. **Recusados explicitamente** na spec: warehouse, ETL, índice de busca, *materialized view*, tabela de indicadores, cache. Rastreabilidade por `rastreabilidade.md` na fase de tarefas | `SC-209` · revisão |
| **VI — Jornada e valor** | A capacidade é observável pelo canal do ator — a interface administrativa —, sem shell e sem banco. O cenário de ponta a ponta é `SC-206`, e o `quickstart.md` o torna executável | `quickstart.md` |

**Duas observações que o gate exige registrar.**

**A feature é leitura, e o Princípio VI proíbe que infraestrutura substitua capacidade.** Ela não é
trabalho técnico: a capacidade de produto é *responder como está o conjunto dos certames*, hoje
inexistente, e a `E-6` da auditoria de 20/09 a classifica como 🟡 parcial.

**O recorte desta entrega é normativo, e não uma intenção.** `D-011` fez os `MUST` obrigarem apenas
o primeiro incremento. As proibições — PII, *matriculados*, motor de alerta, gramática da ausência —
continuam `MUST` aqui, porque guarda-corpo que sai com a capacidade falta quando ela volta.

## Project Structure

### Documentation (this feature)

```text
specs/040-visao-institucional-dos-processos/
├── spec.md              # a especificação revisada (987 linhas)
├── plan.md              # este arquivo
├── research.md          # Fase 0 — R-001 a R-010, e o achado que corrige a spec
├── data-model.md        # Fase 1 — as formas de leitura (nenhuma entidade persistente)
├── contracts/
│   └── pagina-visao-geral.md   # o contrato da rota, dos parâmetros e das grafias
├── quickstart.md        # Fase 1 — o cenário de ponta a ponta, executável
└── tasks.md             # Fase 2 — NÃO criado por este comando
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── interface/
│   ├── visao_geral.py           # NOVO — as derivações, só leitura, no padrão de supervisao.py
│   ├── views.py                 # + view `visao_geral`, montagem de contexto apenas
│   ├── urls.py                  # + rota "visao-geral"
│   ├── identidade.py            # + "visao:consultar" no papel `gestor` (uma linha)
│   └── templates/interface/
│       ├── visao_geral.html     # NOVO — filtros, consolidado, tabela
│       ├── _linha_do_edital.html# NOVO — a linha, extraída para caber no teste de fragmento
│       ├── base.html            # + regras de estilo no <style> existente (R-007)
│       └── lista.html           # + o caminho, condicionado à capacidade
└── publicacoes/application/
    └── selectors.py             # versoes_vigentes(...) extraída; selecoes_publicas passa a usá-la

backend/tests/
├── unit/test_visao_institucional.py          # NOVO — as derivações, sem requisição (T-01..T-10)
├── interface/test_visao_geral.py             # NOVO — a tela (T-11..T-18)
├── authorization/test_visao_institucional.py # NOVO — capacidade, escopo, grafia (T-12, T-19)
└── performance/test_visao_institucional.py   # NOVO — orçamento e snapshots (T-20..T-22)
```

**Structure Decision**: monólito Django de projeto único, com a feature inteira dentro do app
`interface` — que é onde a gestão mora — mais **uma** alteração fora dele, em
`publicacoes/application/selectors.py`, para extrair o resolvedor de versão vigente que o portal já
implementa (`R-003`). Não nasce app novo: não há entidade, não há migration e não há comando; um app
seria pasta vazia com um módulo de leitura dentro.

## Trilhas de implementação

> **Trilhas, e não fases** — a palavra é deliberada. As **fases** são as de
> [tasks.md](./tasks.md) (`Phase 1` a `Phase 6`), organizadas por jornada, e são elas que governam a
> execução. Estas cinco trilhas são o corte por **camada**, e servem para enxergar a dependência
> técnica; numerá-las como "fase" faria `Fase 1` significar duas coisas diferentes nos dois
> documentos, que foi um defeito real deste plano.
>
> Ordem de dependência, não de esforço. A trilha A é a única que toca código fora do `interface`, e
> corresponde a `T004`/`T005` da `Phase 2`.

**A. A extração compartilhada.** `versoes_vigentes(*, editais=None, at=None)` em `publicacoes`, e
   `selecoes_publicas` reescrita sobre ela, **com a suíte do portal verde antes de seguir**. É a
   única mudança que pode quebrar superfície existente.
**B. As derivações.** `interface/visao_geral.py` com as formas de leitura do `data-model.md`, sem
   requisição, testáveis com `agora=` e `hoje=` explícitos.
**C. A capacidade.** `visao:consultar` no mapa de papéis, `require_permission` na view, e o teste
   que prende a grafia.
**D. A tela.** Template, estilo no `base.html`, e o caminho em `lista.html` condicionado à
   capacidade.
**E. Os guardiões.** Orçamento de consulta, contagem de snapshots, varredura de PII no HTML.

## Complexity Tracking

> Sem violações constitucionais. Nada a justificar.

Três decisões que **pareceriam** complexidade e são o oposto, registradas para a revisão não as
reabrir:

| Aparência | O que de fato é |
|---|---|
| "um módulo novo para uma página" | é o padrão que `supervisao.py` estabeleceu, e a razão é testabilidade sem cliente HTTP |
| "mexer em `publicacoes` por uma feature de `interface`" | é a recusa da segunda verdade: copiar o resolvedor divergiria na primeira mudança (`FR-582`) |
| "agrupar inscrições por Perfil custa mais linhas" | continua **uma** consulta, e é o que impede o número correto e institucionalmente falso de `D-012` |
