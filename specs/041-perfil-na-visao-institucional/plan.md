# Implementation Plan: O Perfil de Vaga na visão institucional

**Branch**: `claude/spec-processos-seletivos-visao-395a64` | **Date**: 2026-09-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/041-perfil-na-visao-institucional/spec.md`

## Summary

Cada linha de Edital da Visão Geral passa a **expandir os seus Perfis de Vaga**, com vagas, demanda
e razão próprias; a Atenção sai do agregado do Edital e passa a ser calculada **no Perfil**, com a
linha resumindo *quantos de quantos* — **cada espécie com o seu denominador** —; e um booleano
**Somente com atenção** reduz a tabela ao que precisa ser olhado.

A abordagem técnica cabe em duas frases: **o dado já está carregado**, e a única incógnita
estrutural era onde `<details>` cabe dentro de uma tabela — resolvida em `R-001` com uma segunda
`<tr>` e um `<td colspan>`, sem JavaScript. Nenhuma consulta nova, nenhuma migration, nenhum módulo
novo.

## Technical Context

**Language/Version**: Python 3.13 · Django 5.2 — nenhuma dependência nova.

**Storage**: PostgreSQL. **Sem migration**: a feature é leitura, como a `040`.

**Testing**: pytest + pytest-django contra PostgreSQL (`make test-pg`), nas quatro famílias que a
`040` já usa — `tests/unit/`, `tests/interface/`, `tests/authorization/`, `tests/performance/`.

**Target Platform**: a interface administrativa sob `/gestao/`.

**Project Type**: monólito Django, projeto único.

**Performance Goals**: a contagem de consultas **não cresce com o número de Perfis** — igual entre
um Edital de 1 e um de 12 — e continua não crescendo com o número de Editais (`SC-216`).

**Constraints**: zero consulta nova (`FR-618`); HTML estruturalmente válido, que nenhum teste do
repositório cobre hoje (`R-007`); operável por teclado com o estado declarado (`FR-619`); nenhum
dado pessoal, que a `040` já garante e esta não afrouxa.

**Scale/Scope**: um módulo alterado, dois templates alterados, um parcial novo, um parâmetro de
consulta novo, e a substituição escrita de um requisito da `040`. O acervo real tem Editais de 1 a 3 Perfis; o de 16 polos é hipótese, e o
limiar que obrigaria a paginar a expansão **não** é fixado aqui.

## Constitution Check

*GATE: verificado antes da Fase 0 e reavaliado após a Fase 1. Nenhuma violação.*

| Princípio | Como esta feature o atende | Verificado por |
|---|---|---|
| **I — Linguagem ubíqua** | **Perfil de Vaga** é o termo do domínio e do conteúdo publicado; a tela não inventa "oferta" nem "polo". `locality` é apresentado como publicado, e nunca lido como classificação (`FR-609`) | revisão de texto · `test_vocabulario_da_composicao.py` |
| **II — Integridade normativa** | Os Perfis são os da **versão consolidada vigente**, como as vagas já são. Nada é gravado, nada é derivado de linha de elaboração | `tests/unit/` com conteúdo explícito |
| **III — Segurança e dados pessoais** | A expansão é agregada por Perfil: nenhum dado pessoal novo entra na página. Nenhuma capacidade nova — quem vê a Visão Geral vê a expansão | varredura do HTML, estendida ao conteúdo expandido |
| **IV — Regras explícitas** | A marca muda de nível **por requisito** (`FR-613`), e o requisito da `040` é substituído por escrito (`FR-616`). Nenhuma regra nova no template | `SC-218` |
| **V — Qualidade e simplicidade** | Nenhum JavaScript, nenhuma biblioteca, nenhuma consulta. A solução mais simples que preserva os requisitos é a que o HTML já oferece | `SC-216` · `SC-219` |
| **VI — Jornada e valor** | A capacidade é *"descobrir onde, dentro do Edital, a procura faltou"* — observável pela interface administrativa, sem shell e sem banco | `quickstart.md` · `SC-215` |

**Uma observação que o gate exige registrar.** Esta feature **altera comportamento já entregue**: um
Edital que hoje não recebe marca passará a receber. Isso não é regressão — é a `FR-613` — mas é
mudança visível, e é por isso que a `FR-602` da `040` é substituída por escrito em vez de ficar
descrevendo o que o produto já não faz.

## Project Structure

### Documentation (this feature)

```text
specs/041-perfil-na-visao-institucional/
├── spec.md              # a especificação (15 FRs, 6 SCs, 7 decisões)
├── plan.md              # este arquivo
├── research.md          # Fase 0 — R-001 a R-007, e o achado que corrige a SC-216
├── data-model.md        # Fase 1 — as formas de leitura novas
├── contracts/
│   └── expansao-do-perfil.md   # o contrato da estrutura, das grafias e do que a soma declara
├── quickstart.md        # Fase 1 — o cenário de ponta a ponta
└── tasks.md             # Fase 2 — NÃO criado por este comando
```

### Source Code (repository root)

```text
backend/processo_seletivo/interface/
├── visao_geral.py                       # + PerfilDaLinha, perfis_do_edital; _marcas muda de nível
└── templates/interface/
    ├── _perfis_do_edital.html           # NOVO — a segunda <tr>, o <details> e a tabela interna
    ├── _linha_do_edital.html            # + a marca resumida; a linha continua sendo o Edital
    └── visao_geral.html                 # + o estilo da expansão, no bloco de página que a 040 criou

backend/tests/
├── unit/test_visao_institucional.py          # + os Perfis, a diferença e as marcas por Perfil
├── interface/test_visao_geral.py             # + a expansão na tela, e a estrutura válida
└── performance/test_visao_institucional.py   # + o custo não cresce com o número de Perfis
```

**Structure Decision**: a feature inteira dentro do app `interface`, e **nenhum arquivo fora dele**
— ao contrário da `040`, que precisou tocar `publicacoes`. O parcial novo existe porque a expansão é
uma estrutura própria e porque é nela que o teste de estrutura ancora; deixá-la dentro de
`_linha_do_edital.html` misturaria duas linhas de tabela num arquivo que se chama *linha*.

**O estilo vai no bloco de página**, e não na base: é a lição que a `040` pagou — 4 KB de folha que
só uma tela usa estouraram o teto de outra.

## Trilhas de implementação

> **Trilhas, e não fases** — as fases são as de `tasks.md`. Ordem de dependência.

**A. A leitura por Perfil.** `vagas_do_conteudo` passa a devolver o conjunto **completo** de Perfis;
`contagens_por_edital` acumula rascunho por Perfil; nasce `perfis_do_edital`.

**B. A diferença que não fecha.** As inscrições cujo Perfil saiu da versão vigente — contadas no
Edital, atribuídas a ninguém, e **declaradas**.

**C. A marca muda de nível.** `_marcas` passa a operar sobre os Perfis; a linha resume.

**D. A tela.** O parcial, o `<details>` dentro do `<td colspan>`, o estilo no bloco de página.

**E. O filtro.** `Somente com atenção` — terceiro degrau da ordem, depois da materialização.

**F. Os guardiões.** O custo por Perfil, a estrutura válida, e a varredura de PII estendida ao
conteúdo expandido.

## Complexity Tracking

> Sem violações constitucionais. Nada a justificar.

Duas escolhas que **parecem** complexidade e são o contrário:

| Aparência | O que de fato é |
|---|---|
| "uma segunda `<tr>` só para a expansão" | é a **única** forma estruturalmente válida de ter `<details>` numa tabela sem JavaScript (`R-001`) |
| "um parcial novo para poucas linhas de HTML" | é onde o teste de estrutura ancora, e é o que impede um arquivo chamado *linha* de conter duas |
