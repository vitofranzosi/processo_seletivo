# Implementation Plan: A composição que se explica

**Branch**: `030-composicao-que-se-explica` | **Date**: 2026-09-17 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/030-composicao-que-se-explica/spec.md`

## Summary

A feature **remove perguntas** da composição do marco classificatório e do Perfil de Vaga, nomeia os
conceitos onde a decisão acontece, e deixa o método do sorteio ser declarado uma vez por Edital.

O caminho técnico é o oposto do que a leitura do enunciado sugere. Quase nada aqui é trabalho de
template: o cartão do marco já sabe esconder bloco (`<details class="bloco-do-marco">`), e esconder
mais campos seria uma tarde de trabalho. O custo real está em três lugares que a interface não
mostra — `replace_draft`, que apaga o que não for reenviado; o catálogo de mutabilidade, que
endereça `drawMethod` sob `classificationMilestones`; e a ausência, no modelo, de um campo que diga
**como a ordem daquele marco é produzida**, hoje inferido da presença de `metodo_de_sorteio`.

Por isso o plano separa: P1 e P2 são entregáveis por si, P3 move conteúdo normativo e carrega o
risco da feature.

## Technical Context

**Language/Version**: Python 3.12, Django 5.x

**Primary Dependencies**: Django templates + htmx (fragmentos do assistente), sem framework de front

**Storage**: PostgreSQL. Tabelas append-only protegidas por trigger e por privilégio ausente

**Testing**: pytest + pytest-django. `make test-pg` (nunca `make test` — cai para SQLite)

**Target Platform**: monólito Django servido por Gunicorn; interface administrativa e portal público

**Project Type**: web (backend único, templates server-side)

**Performance Goals**: orçamento de consulta por tela já vigente no projeto; condição de
participação sai de coluna e de SQL, nunca de leitura do conteúdo publicado

**Constraints**:

- **Nenhum campo `required` pode ser ocultado.** É regra já escrita em `_marco.html`: campo
  obrigatório invisível é submissão que o navegador recusa sem conseguir mostrar o que falta. Toda
  revelação progressiva de FR-413 a FR-417 precisa remover o `required` junto com o campo, e
  transferir a cobrança para a validação da publicação.
- **`replace_draft` apaga e recria.** O rascunho não é atualizado campo a campo: o payload substitui
  o conteúdo inteiro. Campo não reenviado é campo perdido — e é exatamente o que a revelação
  progressiva produz se for feita só no template.
- **Valor publicado é intocável.** Padrão de FR-419 e derivação de FR-420 não podem alcançar Edital
  já publicado, nem durante Retificação.

**Scale/Scope**: 3 histórias, 19 FRs (FR-413 a FR-431), 5 SCs (SC-138 a SC-142). Superfície medida:
`_marco.html` (400 linhas), `_perfil.html` (261), `compor_classificacao.html` (86),
`distribuicao.html` (462), `corte.html`, `ocupacao`, `sorteio.html`, mais `draft.py`,
`mutabilidade.py`, `forms.py` e os serializers.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Veredito | Como a feature se sustenta |
|---|---|---|
| **I — Linguagem Ubíqua** | ✅ passa | FR-425 proíbe termo novo. A feature torna visível o significado do que já existe; não renomeia marco, recorte, geração nem faixa. |
| **II — Integridade Normativa** | ⚠️ **gate crítico** | FR-429 move o método do sorteio para o Edital. `MarcoClassificatorio.metodo_de_sorteio` documenta, no próprio modelo, **por que** ele mora no marco. Resolver em Phase 0 (R2) antes de qualquer código. |
| **III — Segurança e Auditoria** | ✅ passa | Nada muda em autorização ou escopo. A feature não cria caminho novo de escrita. |
| **IV — Regras Explícitas** | ⚠️ **gate** | FR-416 declara que, com uma Etapa, a pontuação combinada é a dela. Isso é regra **derivada**, e precisa ser derivada em um lugar só — não no template e no cálculo. |
| **V — Simplicidade e Rastreabilidade** | ✅ passa | A feature remove perguntas; o critério de aceitação é contagem que só cai. Nenhuma complexidade nova de arquitetura. |
| **VI — Completude de Jornada** | ✅ passa | Demonstrável pela interface administrativa, ponta a ponta, sem shell nem banco: compor o Edital canônico respondendo menos perguntas. |

**Duas travas antes de Phase 1**: R2 (onde mora o método do sorteio) e R5 (como preservar o que foi
declarado sob `replace_draft`). Sem elas resolvidas, P3 e FR-418 não têm plano — têm intenção.

## Constitution Check — reavaliação após Phase 1

*Os dois gates que travavam Phase 1 estão resolvidos. Nenhum novo apareceu.*

| Gate | Estado | Onde se resolveu |
|---|---|---|
| **II — o método do sorteio sai do marco** | ✅ liberado | [research.md R2](research.md). O método comum vira conteúdo normativo do **Edital** — mesmo snapshot, mesma autoridade signatária, endereçável por Retificação. São as quatro propriedades que o modelo cobrava; a objeção escrita era contra tabela operacional, não contra o Edital. |
| **IV — a regra derivada de FR-416** | ✅ liberado | [data-model.md](data-model.md) e [contracts/conteudo-normativo.md](contracts/conteudo-normativo.md). `operation` e `normalization` continuam **publicados**; deixam de ser **perguntados**. A derivação mora em um lugar só. |

**O que a Phase 1 acrescentou ao risco**, e que `$speckit-tasks` precisa ordenar: a fronteira do
campo oculto. FR-418 exige que o declarado não se perca; SC-142 exige que ele não alcance o
publicado. As duas coisas ao mesmo tempo só se sustentam com teste de fronteira, e ele é
pré-requisito de P3 — não consequência dele.

## Project Structure

### Documentation (this feature)

```text
specs/030-composicao-que-se-explica/
├── spec.md
├── checklists/requirements.md
├── plan.md              # este arquivo
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── contracts/           # Phase 1
│   ├── conteudo-normativo.md
│   └── payload-do-rascunho.md
├── quickstart.md        # Phase 1
└── tasks.md             # $speckit-tasks — não criado aqui
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── editais/
│   ├── models/perfis.py          # MarcoClassificatorio: campo novo da forma da ordem (P1)
│   ├── models/…                  # Edital: método comum do sorteio (P3)
│   ├── application/draft.py      # replace_draft — a trava de FR-418
│   ├── domain/mutabilidade.py    # catálogo de Retificação: endereçamento do drawMethod (P3)
│   ├── domain/perfis.py          # derivação de código e denominação (FR-420)
│   ├── domain/reaproveitamento.py
│   ├── api/serializers.py        # conteúdo canônico publicado
│   └── migrations/               # campo novo, sem tocar em dado publicado
├── interface/
│   ├── views.py                  # contexto das telas de composição e condução
│   ├── forms.py                  # leitura do payload do marco
│   └── templates/interface/
│       ├── _marco.html           # revelação progressiva (FR-413 a FR-418)
│       ├── _perfil.html          # Modalidade: perguntas condicionadas (FR-417)
│       ├── compor_classificacao.html  # ajuda ancorada (FR-426, FR-427)
│       ├── distribuicao.html     # o que a consolidação produz (FR-422)
│       ├── corte.html            # recorte, geração, faixa (FR-424)
│       └── sorteio.html
├── classificacao/                # leitores do marco: cálculo, universo, reprodução
└── sorteios/

backend/tests/
├── interface/                    # test_compor_classificacao.py, test_metodo_do_marco.py,
│                                 # test_round_trip_do_rascunho.py
├── editais/                      # mutabilidade, retificação, publicação
└── test_citacoes_de_requisito.py # varre specs/ — roda em PR de documentação também
```

**Structure Decision**: monólito Django existente, sem módulo novo. A feature age em três camadas já
estabelecidas — modelo e migração em `editais`, apresentação em `interface`, e o catálogo de
mutabilidade em `editais/domain`. Nenhum app novo se justifica: o conceito é o mesmo, muda **quando**
ele é apresentado e **onde** ele é declarado.

## Complexity Tracking

| Violação | Por que é necessária | Alternativa simples recusada porque |
|---|---|---|
| Campo novo no modelo para a forma da ordem (FR-413) | Hoje "este marco sorteia" é **inferido** da presença de `metodo_de_sorteio`. Uma pergunta de entrada que não se persiste volta a ser inferência, e a inferência é o que produz o campo obrigatório sem valor. | Derivar da presença do bloco mantém a ambiguidade entre "não sorteia" e "sorteia e ainda não declarei o método" — que é justamente o estado que FR-414 precisa distinguir. |
| Método do sorteio no Edital, com divergência por marco (FR-429, FR-430) | Sete Perfis de sorteio declaram hoje a mesma regra sete vezes (ACH-61). | Deixar como está contraria SC-140. Mas a alternativa **não** pode ser tabela operacional de sorteio: o modelo já recusou isso por escrito (sem versão consolidada, sem autoridade signatária, fora do snapshot). Ver R2. |
