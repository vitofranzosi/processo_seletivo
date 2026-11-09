# Implementation Plan: O andamento diz o que cada providência é

**Branch**: `claude/135-implementacao-75ef0e`, empilhada sobre `claude/135-correcoes-da-derivacao`
(PR #440, só a spec) | **Date**: 2026-11-09 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/135-correcoes-da-derivacao/spec.md`, com D-001 a D-004.

## Summary

Quatro correções de leitura na derivação da `127`, sem regra de domínio nova:

1. **A lista sem inscritos** — uma consulta por marco por pontuação diz quais listas reservadas têm o
   universo vazio, pelo mesmo critério da tela da ordenação (R-001). A célula da ordem continua com a
   situação de hoje e ganha o dado `lista_vazia` e a nota "lista sem inscritos"; a providência diz, no
   próprio ato, que a lista não tem inscritos e que emitir declara que ninguém concorreu (R-002).
2. **O que foi divulgado** — a célula da publicação da condução do marco passa a dizer a natureza
   (`PRELIMINAR`, `DEFINITIVA`) como dado, e a célula do resultado do andamento a carrega como
   `divulgado` (`nada`, `preliminar`, `definitivo`). As quatro decisões que liam a palavra
   "preliminar" ou "definitivo" na nota passam a ler o dado (R-003).
3. **A razão da espera do definitivo** — com o preliminar do ato vigente publicado, o prazo recursal
   aberto e o recurso pendente têm uma segunda redação, ao lado da primeira em `publicabilidade.py`,
   sem a alternativa "ou publique como resultado preliminar". A mensagem da aferição não muda (R-004).
4. **A contagem do Perfil** — "N providências em aberto nos marcos" (R-005).

**Onde está o risco**: mudar uma situação sem querer (as expectativas da `127` e da `133` são o
guardião), e o custo do detalhe (o teste de orçamento da `127`).

## Technical Context

**Language/Version**: Python 3.13 · **Primary Dependencies**: Django; nenhuma nova

**Storage**: PostgreSQL, só leitura. Nenhuma migration; o `M` do `provisionar` continua 53.

**Testing**: pytest contra PostgreSQL (`make test-pg`, `DB_NAME=ps135`). Regras puras em
`tests/unit/interface/`; os cinco cenários da `134` em `tests/integration/treinamento/`, pelo gerador
(`carregar`); o orçamento em `tests/performance/test_andamento_em_escala.py`, que não muda.

**Target Platform**: `/gestao/editais/<id>/` (o nível 1 e o "Andamento da seleção") e o "Próximo
nesta lista" das telas de ato.

**Performance Goals**: o detalhe com o mesmo número de consultas para 3 e 30 inscrições, abaixo dos
tetos da `127` (SC-1465). A consulta nova é uma por marco por pontuação com ordem a emitir ou
obsoleta, e só então.

**Constraints**: nenhum texto da aferição muda (D-003); nenhuma situação muda (FR-4676, FR-4678);
nenhum comando muda (FR-4687); a varredura de vocabulário e de citações; os arquivos novos da `136`
(sessão paralela) não são tocados.

**Scale/Scope**: edições em `interface/andamento.py`, `interface/providencias.py`,
`interface/conducao_do_marco.py` (um campo a mais na célula da publicação),
`classificacao/application/calculo.py` (a consulta do universo vazio, ao lado do cálculo que a tela
usa) e `divulgacao/domain/publicabilidade.py` (a segunda redação). Nenhum template muda: a frase nova
chega pelo `ato`, pela `nota` e pela `razao`, que os parciais já desenham.

## Constitution Check

| Princípio | Como é atendido |
|---|---|
| I. Linguagem ubíqua | "Ordem", "lista", "resultado preliminar", "definitivo": as palavras das telas de ato. "Ninguém concorreu" é a frase da tela da ordenação. |
| II. Imutabilidade | Nada publicado muda; nenhuma escrita. A mensagem da aferição continua a mesma na tela e no comando (D-003). |
| III. Segurança | Nenhuma permissão nova; quem vê a providência continua sendo quem a via (spec, *Edge Cases*). |
| IV. Regras explícitas | O critério da lista vazia é o da tela da ordenação, por uma função ao lado do cálculo dela (R-001); a natureza do divulgado vem do histórico que a condução já lê (R-003). |
| V. Rastreabilidade e simplicidade | Nenhum estado, tabela, coluna ou fila (SC-1466); spec, plano, tarefas, matriz e verificação. |
| VI. Completude de jornada | O andamento passa a dizer o que a tela do ato já dizia, antes de a pessoa chegar a ela. |

**Resultado**: passa. Pós-desenho: passa (nenhuma violação a justificar).

## Project Structure

### Documentation (this feature)

```text
specs/135-correcoes-da-derivacao/
├── spec.md · plan.md · research.md · data-model.md · quickstart.md · tasks.md
├── contracts/andamento.md
├── checklists/requirements.md
└── rastreabilidade.md · verificacao.md   (na implementação)
```

### Source Code

```text
backend/processo_seletivo/
├── classificacao/application/calculo.py      # listas_sem_concorrente (R-001), com o universo de calcular_ordem
├── divulgacao/domain/publicabilidade.py      # a segunda redação da espera (R-004)
└── interface/
    ├── conducao_do_marco.py                  # a célula da publicação diz a natureza (R-003)
    ├── andamento.py                          # lista_vazia, divulgado, razão, contagem
    └── providencias.py                       # o dado da lista vazia e o agrupamento
backend/tests/
├── unit/interface/test_andamento_o_que_cada_providencia_e.py   # as quatro, nas funções puras
├── integration/classificacao/test_listas_sem_concorrente.py    # o critério igual ao da tela
└── integration/treinamento/test_andamento_dos_cenarios.py      # C04, C06, C08, C12, C14
```

**Structure Decision**: o critério do universo vazio mora em `classificacao`, ao lado do cálculo que a
tela da ordenação usa, e a `interface` só o pergunta — como a `126` fez com `recortes_sem_inscrito`
em `sorteios`. As redações da aferição moram juntas em `publicabilidade.py`, para que mudar uma
lembre a outra.

## Os incrementos e os PRs

Um PR só, empilhado sobre o #440 enquanto ele não for mergeado. As quatro correções são independentes
entre si, e cada uma tem os seus testes; a ordem das tarefas é a de prioridade da spec.

## Complexity Tracking

Nenhuma violação.
