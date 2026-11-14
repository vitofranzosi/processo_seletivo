# Implementation Plan: As regras de deliberação dos pareceres

**Branch**: `claude/165-regras-de-deliberacao-9f8a47`, sobre `claude/164-efeito-do-desfecho-por-lista`
| **Date**: 2026-11-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/165-regras-de-deliberacao/spec.md`

## Summary

A Etapa decisória com mais de uma avaliação por inscrição ganha a **regra de deliberação**: uma
coluna de elaboração e o campo `deliberationRule` do degrau 24 do conteúdo publicado, no caminho que a
`164` abriu para o efeito (rascunho, publicação, mutabilidade, Retificação, Revisão e documento).

Um módulo puro novo, `resultados/domain/deliberacao.py`, aplica a regra aos sentidos. `regra.py` deixa
de impedir a Etapa colegiada, a prontidão ganha o estado "aguardando pareceres", e a consolidação cria
o Resultado de origem nova, `DELIBERACAO`, ligado aos N pareceres por uma tabela append-only. A
invariante de proveniência da `013` é revista no banco, com a mesma força.

O "às cegas" é uma função do servidor aplicada aos seletores que entregam conclusões. A **exposição**
é uma tabela append-only gravada quando uma tela entrega parecer alheio, e barra a atribuição e a
reabertura. No recurso, a reavaliação colegiada é recusada antes de gravar, e o impedimento, a
instrução e o parecer ao titular aprendem a ler os pareceres da deliberação.

As decisões técnicas estão em [research.md](research.md) (`T-001` a `T-019`); o modelo, em
[data-model.md](data-model.md); as frases e recusas, em [contracts/](contracts/); o roteiro, em
[quickstart.md](quickstart.md).

## Technical Context

**Language/Version**: Python 3.13, Django 5.2; JavaScript sem build na composição das Etapas.

**Primary Dependencies**: as do projeto; nenhuma nova.

**Storage**: PostgreSQL, com três migrations:

- `editais/0031_regra_de_deliberacao`: a coluna da Etapa;
- `resultados/0008_deliberacao`: a origem, os três campos, a tabela dos pareceres e os gatilhos;
- `avaliacoes/0006_exposicao_ao_parecer`: a tabela da exposição.

Duas tabelas append-only novas: o `M` da preparação do banco vai de 59 a **61**.

**Testing**: pytest contra PostgreSQL (`make test-pg`, com `DB_NAME` próprio):

- unidade para `deliberacao.py` e `regra.py` (a tabela-verdade, SC-2351);
- integração para consolidação, gatilhos, prontidão, às cegas, exposição, distribuição, reabertura,
  recurso e Retificação;
- interface para composição, conferência, conclusões preservadas, impedimentos, julgamento, Mesa e
  portal;
- documento pelo compositor; recomposição do acervo (SC-2350).

**Target Platform**: o monólito Django: gestão em `/gestao/`, portal e documento PDF.

**Project Type**: aplicação web, backend com templates.

**Performance Goals**: nenhuma consulta nova por inscrição. A prontidão e a consolidação usam o
panorama que já lê todas as conclusões elegíveis da Etapa; os pareceres do lote são gravados em
`bulk_create`. O às cegas custa uma consulta por tela (as pendências do ator na Etapa), e a exposição,
um `INSERT` por página.

**Constraints**: a CSP sem `unsafe-inline` (estilo e script em arquivo); tudo em português; as
garantias que hoje são do banco continuam do banco.

**Scale/Scope**: Etapas de até milhares de inscrições, com três a cinco pareceres cada.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como a feature o cumpre |
|---|---|
| I. Linguagem ubíqua | regra de deliberação, parecer, deliberação, exposição: o vocabulário do estudo e da spec |
| II. Integridade normativa e imutabilidade | a regra é norma publicada (degrau 24), retificável só até o primeiro Resultado; o Resultado e os pareceres ligados são append-only; a reprodução lê a versão gravada |
| III. Segurança e auditoria | o às cegas é do servidor; a exposição é registrada sem conteúdo; a trilha não traz contagem; a autoria nunca chega ao titular |
| IV. Regras explícitas | sem regra padrão; maioria só ímpar; nenhuma deliberação antecipada; a recusa da reavaliação colegiada é explícita e antes de gravar |
| V. Rastreabilidade | cada FR- tem teste; o README e o `CLAUDE.md` registram o `M` novo |
| VI. Completude de jornada | composição, Mesa, consolidação, recurso e acompanhamento do candidato, ponta a ponta |

**Gate: aprovado.** A revisão da invariante de proveniência da `013` não é violação: a spec a declara
e dá a redação nova (FR-7065, D-006), e o banco continua a garanti-la (T-006).

**Re-check pós-desenho: aprovado.** Duas tabelas append-only novas entram no provisionamento, com
gatilho e privilégio ausente.

## Project Structure

### Documentation (this feature)

```text
specs/165-regras-de-deliberacao/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── recusas.md
│   └── frases.md
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── editais/
│   ├── models/etapas.py                      # coluna regra_de_deliberacao
│   ├── migrations/0031_regra_de_deliberacao.py
│   ├── domain/{etapas,validation,mutabilidade}.py
│   ├── application/draft.py
│   └── api/serializers.py
├── shared/canonical.py                        # SCHEMA_VERSION 24
├── publicacoes/
│   ├── domain/{elevacao,alteracoes}.py
│   ├── application/{publish_edital,retificacoes}.py
│   └── infrastructure/{pdf,apresentacao}.py
├── resultados/
│   ├── domain/{deliberacao (novo),regra}.py
│   ├── models.py                              # origem DELIBERACAO, ParecerDaDeliberacao
│   ├── migrations/0008_deliberacao.py
│   └── application/{prontidao,consolidacao,selectors}.py
├── avaliacoes/
│   ├── models.py                              # ExposicaoAoParecer
│   ├── migrations/0006_exposicao_ao_parecer.py
│   └── application/{cegas (novo),selectors,distribuicao,avaliacao}.py
├── recursos/
│   ├── domain/elegibilidade.py
│   └── application/{julgar,instruir,selectors}.py
├── seguranca/papeis.py                        # TABELAS_APPEND_ONLY
├── interface/
│   ├── forms.py, views.py, revisao.py, retificacao.py, supervisao.py
│   ├── templates/interface/{_etapa,conclusoes,impedimentos,consolidacao_confirmar,
│   │                        mesa_inscricao,julgamento…}.html
│   └── static/interface/…                     # o script e a folha da composição
└── portal/templates/portal/acompanhamento.html
backend/tests/
├── unit/resultados/test_deliberacao.py
├── integration/{resultados,avaliacoes,recursos,publicacoes}/…
└── interface/…
```

**Structure Decision**: o monólito existente; nenhum app novo. O domínio puro da regra fica em
`resultados/domain`, ao lado de `regra.py` e `efeito.py`; o às cegas e a exposição, em `avaliacoes`,
que é onde os pareceres moram.

## Ordem de implementação

1. **Fundação**: a coluna, o degrau 24, a elevação, a mutabilidade, o domínio puro (`deliberacao.py`)
   e as migrations com os gatilhos.
2. **US1**: composição, publicação, achados, documento, Revisão e Retificação (campo).
3. **US3**: `regra.py`, prontidão, consolidação, conferência e reprodução.
4. **US2**: às cegas e exposição (seletores, views, distribuição, reabertura, Mesa).
5. **US6**: as recusas da Retificação.
6. **US5**: julgamento, impedimento, instrução e supervisão.
7. **US4**: parecer ao titular e acompanhamento.
8. **Polimento**: guardiões, `CLAUDE.md`, README, Visão, suíte inteira.

## Complexity Tracking

| Violação | Por que é necessária | Alternativa mais simples descartada porque |
|---|---|---|
| Gatilho de constraint adiável | o Resultado deliberado e os pareceres nascem na mesma transação, e nenhum Resultado sem pareceres pode sobreviver ao `COMMIT` | conferir só na aplicação deixaria a FR-7065 sem a força de banco que a `013` tinha |
| Escrita num `GET` (exposição) | o fato que decide é a entrega da página | inferir da trilha não diz quais inscrições a página mostrou |
