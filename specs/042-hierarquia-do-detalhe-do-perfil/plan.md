# Implementation Plan: A hierarquia do detalhe do Perfil

**Branch**: `claude/spec-processos-seletivos-visao-395a64` | **Date**: 2026-09-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/042-hierarquia-do-detalhe-do-perfil/spec.md`

## Summary

A região expandida passa a ler como **subordinada** à linha do Edital: um `<tbody>` por Edital
agrupando as duas linhas, régua e recuo na célula da expansão, cabeçalho filho mais leve, e código,
localidade e cadastro de reserva saindo das colunas para a **identidade** do Perfil.

Junto vão três acertos da mesma tela: o controle de expansão recupera o **marcador de divulgação**
que `display:inline-block` apagou, a atenção deixa de repetir a mesma frase nas duas granularidades,
e os controles de ordenação separam **critério** de **direção**.

**Nenhum número muda.** Fórmulas, fontes, denominadores e consultas são os da `041`.

## Technical Context

**Language/Version**: Python 3.13 · Django 5.2 — nenhuma dependência nova.

**Storage**: PostgreSQL. **Sem migration**, e **sem consulta nova**.

**Testing**: pytest + pytest-django contra PostgreSQL (`make test-pg`), nas famílias que a `041` já
usa.

**Target Platform**: a interface administrativa sob `/gestao/`.

**Project Type**: monólito Django, projeto único.

**Performance Goals**: **nenhuma mudança** — a contagem de consultas é a da `041`, e o teste dela
continua valendo sem alteração.

**Constraints**: **zero JavaScript** (`FR-622`); o nome acessível da tabela filha preservado
(`FR-625`); a leitura das métricas no telefone **não pode piorar** (`FR-623`); e os cinco sinais de
que o plano saiu do problema, que a spec registrou.

**Scale/Scope**: um módulo, dois templates e uma folha. Dez requisitos, uma história.

## Constitution Check

*GATE: verificado antes da Fase 0 e reavaliado após a Fase 1. Nenhuma violação.*

| Princípio | Como esta feature o atende | Verificado por |
|---|---|---|
| **I — Linguagem ubíqua** | Nenhum termo novo. *Cadastro de reserva*, *Perfil*, *vagas imediatas* são os do domínio, e apenas mudam de lugar na tela | revisão de texto |
| **II — Integridade normativa** | Nada é gravado, nada é derivado de linha de elaboração, e **nenhuma fórmula muda**. A ausência de reserva passa a ser dita pela ausência do metadado — a mesma grafia que `especie_de_reversao` e `requerimento_momento` já usam | `tests/unit/` |
| **III — Segurança e dados pessoais** | Nenhuma capacidade nova, nenhum dado novo na página. A identidade do Perfil é conteúdo **publicado** | varredura de PII da `040`, que continua valendo |
| **IV — Regras explícitas** | A `SC-217` da `041` é substituída por escrito (`FR-631`), citando o texto. A composição da identidade mora no módulo, e não no template | `SC-224` |
| **V — Qualidade e simplicidade** | Folha de estilo, agrupação de linhas e composição de texto. **Nenhum JavaScript, nenhum componente novo** | `SC-226` |
| **VI — Jornada e valor** | A capacidade é perceptiva: *continuar percebendo que se lê a mesma linha, aprofundada*. `SC-222` é humana de propósito | `quickstart.md` |

**Uma observação que o gate exige registrar.** Esta feature **não amplia capacidade** — ela corrige
a forma de uma já entregue. O Princípio VI admite isso: a `041` entregou a capacidade, e a `042`
torna-a utilizável. O que ela **não** pode fazer é virar trabalho técnico sem jornada, e por isso a
`SC-222` é escrita como leitura humana e não como medida de pixel.

## Project Structure

### Documentation (this feature)

```text
specs/042-hierarquia-do-detalhe-do-perfil/
├── spec.md              # 10 FRs, 6 SCs, 4 decisões, 3 lacunas
├── plan.md              # este arquivo
├── research.md          # Fase 0 — R-001 a R-007, e o triângulo que sumiu
├── data-model.md        # Fase 1 — o delta, que é pequeno de propósito
├── contracts/
│   └── detalhe-do-perfil.md    # a estrutura, as colunas e as grafias
├── quickstart.md        # Fase 1 — o percurso, com as medidas de antes
└── tasks.md             # Fase 2 — NÃO criado por este comando
```

### Source Code (repository root)

```text
backend/processo_seletivo/interface/
├── visao_geral.py                       # + Marca.rotulo · PerfilDaLinha.identidade_secundaria
│                                        #   + ORDENS renomeadas (chave inalterada)
└── templates/interface/
    ├── _linha_do_edital.html            # abre e fecha o <tbody> do Edital
    ├── _perfis_do_edital.html           # identidade composta, cinco colunas, rótulo do controle
    └── visao_geral.html                 # a folha da página: régua, recuo, marcador, cabeçalho leve
                                         #   + os dois controles de ordenação renomeados

backend/tests/
├── unit/test_visao_institucional.py     # + a identidade secundária e o rótulo curto
└── interface/test_visao_geral.py        # + a estrutura agrupada, as colunas e o marcador
```

**Structure Decision**: tudo dentro do app `interface`, e **nenhum arquivo novo**. A feature é
folha, agrupação e composição — criar um parcial a mais para a linha de identidade seria estrutura
sem regra que a consuma, que é o que este repositório recusa desde a `007`.

**O estilo continua no bloco de página** que a `040` criou. É a lição que já foi paga uma vez: 4 KB
de folha de uma tela viajando em todas estourou o teto de outra.

## Trilhas de implementação

> **Trilhas, e não fases** — as fases são as de `tasks.md`.

**A. O agrupamento.** Um `<tbody>` por Edital, com a linha principal e a expansão dentro — e o caso
vazio no seu próprio grupo.

**B. A subordinação.** Régua, recuo, cabeçalho filho mais leve, legenda invisível, e o
comportamento no telefone.

**C. A identidade.** `identidade_secundaria` no módulo; três colunas saem da tabela filha.

**D. A atenção.** `Marca.rotulo`; o Edital resume, o Perfil rotula.

**E. O controle.** Marcador de divulgação de volta, e o rótulo que muda por `details[open]`.

**F. A ordenação.** Critério e direção separados, com a chave de consulta preservada.

## Complexity Tracking

> Sem violações constitucionais. Nada a justificar.

Duas escolhas que **parecem** complexidade e são o contrário:

| Aparência | O que de fato é |
|---|---|
| "um `<tbody>` por Edital" | é o significado do elemento — *grupo de linhas* — e é o que permite régua e separador **sem** posicionamento nem `:has()` (`R-002`) |
| "dois rótulos no mesmo `<summary>`" | é o que troca o texto por estado **sem JavaScript**; `content` de CSS não é texto do documento e não serve para rótulo de ação (`R-003`) |
