# Implementation Plan: Sorteio executável

**Branch**: `claude/spec-035-sorteio-executavel` | **Date**: 2026-09-18 | **Spec**: [spec.md](spec.md)

**Input**: [specs/035-sorteio-executavel/spec.md](spec.md)

## Summary

A ocorrência que fixa a semente ganha a **conferência de forma** que os outros cinco campos do método
já têm; a composição passa a **ensinar** a forma em vez de descobri-la por recusa; e a tela do
sorteio para de atribuir à fonte externa uma falha que é da declaração. Com isso, os cenários **3** e
**5** da reauditoria — que pararam na execução do sorteio — chegam ao fim.

**O Phase 0 contradisse a spec, e a spec foi revista antes deste plano.** Está em
[research.md](research.md), e vale repetir o essencial: o motor existe e é computável; **cinco dos
seis** campos do método já são conferidos ao gravar o rascunho, para o método próprio e para o comum;
e os dois padrões de tela que a feature precisa — a **escolha** montada do vocabulário e a **ajuda**
com forma, exemplo e consequência — **já são praticados pelo produto**, em outros campos.

A feature é, por isso, bem menor do que a auditoria fez parecer: **uma guarda, dois ensinos e uma
frase que já existe e é descartada.**

## Technical Context

**Language/Version**: Python 3.13

**Primary Dependencies**: Django 5.2.17; sem dependência nova

**Storage**: PostgreSQL. **Nenhuma migration** — a feature não toca esquema

**Testing**: pytest, contra PostgreSQL (`make test-pg`)

**Target Platform**: monólito Django, interface administrativa server-side

**Project Type**: web application — `backend/` único

**Performance Goals**: nenhuma meta nova. A conferência é de forma, sobre um campo, em memória

**Constraints**: publicação é ato imutável; **nenhum sorteio já realizado muda de resultado**;
nenhum vocabulário é alargado; nenhuma capacidade nova

**Scale/Scope**: um validador novo, dois campos de formulário em duas telas de composição, um ponto
de tratamento de erro, e **3 fixtures** a corrigir — contadas por nome em `research.md`, `R-6`

## Constitution Check

*GATE: passou antes da Phase 0 e foi reavaliado depois da Phase 1.*

| Princípio | Como esta feature responde | Onde |
|---|---|---|
| **II · Imutabilidade e Temporalidade** | o método é conteúdo publicado. `FR-514` impede que a guarda torne o acervo irretificável, `FR-519` que algo publicado seja reescrito, e `SC-179` prende os dois — **inclusive o resultado de sorteio já realizado**, que é ato | [forma-do-metodo.md](contracts/forma-do-metodo.md) |
| **IV · Regras Explícitas e Consistência** | `FR-515` é dele: a composição e o motor respondem pela **mesma** regra. Duas cópias divergiriam, e a divergência apareceria como a composição aceitando o que o sorteio recusa | idem |
| **VI · Completude de Jornada** | `SC-176` é o sorteio **inteiro** — congelamento, semente, execução, ordem, manifesto e verificação pública —, e não um passo dele | [quickstart.md](quickstart.md) |
| **I · Linguagem Ubíqua** | nenhum vocabulário novo. `FR-509` proíbe uma segunda maneira de ensinar a forma de um campo, e `FR-510` protege a frase em português que diz a norma | `FR-510` |
| **V · Rastreabilidade e Simplicidade** | nenhuma entidade, nenhum campo, nenhuma migration; a guarda que falta vai para junto das cinco que existem | [data-model.md](data-model.md) |
| **III · Segurança e Auditoria** | nenhuma superfície de autorização é tocada. O que a feature protege é **auditabilidade**: um método que não roda torna o manifesto uma promessa | — |

**Gate: passou.** Nenhuma violação a justificar; a seção *Complexity Tracking* fica vazia e foi
removida.

## O que a medição mudou no plano

| A spec dizia | A medição encontrou | Efeito |
|---|---|---|
| três campos sem guarda | **um** — os outros cinco já são conferidos ao gravar | a `US2` encolhe para um validador |
| "nada valida na composição" | seis validadores, para o método próprio **e** o comum | não há família nova de achados |
| criar a escolha de vocabulário | a **Retificação já a faz** com **quatro** campos, por uma função única | a `FR-507` vira *generalizar*, e a composição **reusa** a função |
| a varredura conta quantos Editais seriam impedidos | **nenhum** dos quatro que li declara ocorrência externa | o `SC-180` mudou de pergunta |

**E uma pergunta de governança ficou registrada e não respondida**: o sistema exige uma declaração
que os Editais correntes do Cefor não fazem. O modelo dele é deliberadamente mais forte — é o que
entrega a verificação pública que aqueles Editais prometem e não cumprem —, mas a diferença é real e
é de quem governa o backlog.

## Estrutura da entrega

### Documentação (esta feature)

```text
specs/035-sorteio-executavel/
├── spec.md
├── plan.md                    # este arquivo
├── research.md                # Phase 0 — a medição que revisou a spec
├── data-model.md              # Phase 1
├── quickstart.md              # Phase 1
├── contracts/
│   ├── forma-do-metodo.md
│   └── recusa-do-sorteio.md
├── checklists/requirements.md
└── tasks.md                   # produzido pelo /tasks
```

### Código (raiz do repositório)

```text
backend/processo_seletivo/
├── editais/domain/perfis.py            # a sexta guarda, ao lado das cinco
├── sorteios/domain/substituicao.py     # a regra que a guarda reutiliza — leitura, não mudança
├── sorteios/application/previa.py      # as duas causas deixam de cair no mesmo tratamento
└── interface/
    ├── retificacao.py                  # a escolha que já existe, como referência
    └── templates/interface/
        ├── _marco.html                 # escolha + ajuda, no método do marco
        └── compor_classificacao.html   # escolha + ajuda, no método comum do Edital

backend/tests/
├── unit/editais/                       # a guarda, e o acervo que continua retificável
├── unit/sorteios/                      # composição e motor respondem o mesmo
├── interface/                          # a escolha e a ajuda nas duas telas
└── unit/publicacoes/                   # as 3 fixtures a corrigir
```

**Structure Decision**: monólito Django existente. A feature não cria módulo e não inverte
dependência: a guarda vive em `editais/domain`, que é onde as outras cinco vivem, e **lê** a regra de
`sorteios/domain` — a direção que a `021` declarou por escrito.

## Riscos, e o que responde por cada um

| Risco | Por que é real | O que responde |
|---|---|---|
| **Prender o acervo** | há conteúdo publicado que nunca passou por esta conferência; a guarda no lugar errado torna um Edital irretificável | `FR-514`, e a obrigação 2 do contrato: **levantar quantos**, antes de escolher o lugar |
| **Duas cópias da mesma regra** | ela é de uma linha, e copiá-la é mais fácil do que importá-la | `FR-515`, com `SC-177` comparando **as duas respostas** |
| **"Corrigir" a derivação em prosa** | a auditoria parecia pedir, e o campo está ao lado do que muda | `FR-510`, o cenário 1 do quickstart, e a varredura que mostrou **zero** leitores |
| **Afrouxar a regra para salvar as fixtures** | é o caminho mais curto, e as três fixtures apontam para ele | `data-model`: `concurso 6100 de 2026` derivaria para **2027** |
| **Mudar resultado de sorteio já realizado** | a regra nova toca o caminho que deriva a ocorrência | `SC-179`, com o retrato gravado antes da primeira edição |
| **Ensinar de um jeito novo** | há dois padrões no produto, e inventar um terceiro é fácil | `FR-509`, com a formulação-modelo citada literalmente em `research.md` `R-5` |

## O que fica fora, e onde está dito

A spec tem a lista inteira. Os dois que mais convidam a escorregar:

- **A derivação de recortes do sorteio** — achado registrado pela `034`, cuja correção obriga a
  definir como os atos históricos do recorte excedente continuam alcançáveis.
- **A família de sorteio que o modelo não representa** — a pergunta de governança do `R-7`. Esta
  feature ensina a declarar o que o modelo pede; ela não muda o modelo.
