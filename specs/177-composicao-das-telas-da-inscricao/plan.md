# Implementation Plan: A composição das telas da inscrição no portal

**Branch**: `claude/177-composicao-das-telas-da-inscricao` | **Date**: 2026-11-15 | **Spec**: [spec.md](spec.md)

## Summary

As três telas por onde o candidato volta depois de se inscrever — "Minhas inscrições", "Minha
inscrição" e "Acompanhar" — passam à coluna centrada da jornada do candidato que a `174` criou para a
verificação (`.jornada`, 44rem, botão de 48 px). O trabalho é quase todo de template e de folha: um
começo de tela comum (trilha, título, identificação), blocos na largura da coluna, um botão cheio por
tela, o cartão de inscrição reordenado com o prazo, e a grade de rótulo e valor. As views ganham dois
dados que já estavam ao alcance: o prazo do cartão e o nome do Perfil.

## Technical Context

**Language/Version**: Python 3.12, Django 5 (monólito existente)
**Primary Dependencies**: nenhuma nova
**Storage**: PostgreSQL; nenhuma migration
**Testing**: pytest contra PostgreSQL (`make test-pg`); guardiões de folha e de acessibilidade em `tests/interface`
**Target Platform**: portal do candidato, navegador do celular primeiro
**Project Type**: web, renderização no servidor
**Performance Goals**: a lista não ganha consulta (SC-2806); o laço de itens continua com zero consultas (`tests/performance/test_lista_com_convocacao.py`)
**Constraints**: CSP sem estilo nem script embutido; medida de leitura do portal mantida; toda classe nova com regra na folha
**Scale/Scope**: três templates, uma partial nova, uma seção nova na folha do portal, três funções de view

## Constitution Check

| Princípio | Como esta feature o respeita |
|---|---|
| Publicação imutável, nada excluído | não toca dado; nenhuma migration |
| Negar por padrão | as rotas e as verificações de titular são as de hoje |
| Rastreabilidade por spec | toda frase nova está em D-002 a D-006; a matriz cobre FR, SC e UX |
| Português, comentário explica por quê | os comentários novos dizem a decisão e o custo |

Sem violação.

## Project Structure

### Documentation (this feature)

```text
specs/177-composicao-das-telas-da-inscricao/
├── spec.md
├── plan.md              # este arquivo (com a pesquisa em "Decisões de implementação")
├── tasks.md
├── rastreabilidade.md
├── checklists/requirements.md
└── capturas/            # antes e depois, cinco larguras, três telas
```

### Source Code

```text
backend/processo_seletivo/portal/
├── views.py                                   # _passo_pendente_na_lista, _item_da_lista, _conferencia, acompanhamento
├── templates/portal/
│   ├── _comeco_da_inscricao.html              # novo: trilha, título e identificação
│   ├── inscricoes.html                        # coluna, começo, cartão
│   ├── inscricao_enviada.html                 # coluna, começo, faixa da situação, grade
│   └── acompanhamento.html                    # coluna, começo, ação secundária
└── static/portal/portal.css                   # seção nova da 177, no fim
backend/tests/portal/test_composicao_das_telas_da_inscricao.py   # novo
```

## Decisões de implementação

### I-1 — Reusar a `.jornada` da `174`, com uma marca própria

Cada tela embrulha o conteúdo em `<div class="jornada jornada-da-inscricao">`. A `.jornada` dá a
coluna, o `[hidden]` que vence a classe e o `.principal` de 48 px; a `.jornada-da-inscricao` é o
escopo do que é desta spec, para que nenhuma regra nova alcance a verificação nem outra tela do portal
(FR-8119).

### I-2 — A medida de leitura no parágrafo, e não no bloco

Dentro da coluna, `main>p` deixa de casar, porque o parágrafo não é mais filho de `main`. A regra comum
continua (o guardião a exige), e a seção da 177 declara `.jornada-da-inscricao p{max-width:var(--leitura)}`.
Os blocos que hoje param em `--leitura` (`.situacao-da-inscricao`, `.cartao-de-lista`,
`.resultado-da-etapa`, `.aviso`) recebem `max-width:none` sob a marca, e passam a ocupar a coluna.
Assim a borda é uma só e a linha de texto continua em 68ch (FR-8102, FR-8104).

### I-3 — O prazo do cartão sem consulta

- convocação aberta: `chamada["convocacao"].vencimento`, já lido por `vigentes_por_inscricao`;
- passo pendente: `_passo_pendente_na_lista` passa a devolver o `Passo` inteiro (com `fim`), e não só o
  nome da Etapa;
- rascunho: `periodo_de_inscricoes(conteudo, agora)`, função pura sobre o conteúdo já lido.

Só entra o prazo **futuro**: um vencimento decorrido não é prazo correndo (spec, FR-8106). A frase é a
do filtro `ate_o_prazo` da `118`, com "Prazo:" em negrito antes.

### I-4 — Os selos com classe própria

`.selo` já existe no portal (a correção do documento da `118`). O selo da inscrição é
`.selo-da-inscricao`, com três tons: `enviada` (registrado), `atencao` e o neutro. As classes de hoje
(`situacao enviada`, `situacao passo`, `situacao convocada`) ficam, porque os testes e o vocabulário as
leem; o selo é acréscimo.

### I-5 — O item da lista continua um `<li class="selecao">` sem lista dentro

Os testes recortam o item por `<li class="selecao">.*?</li>` e a ação por
`<a class="principal" href="…">…</a>`. O cartão novo não tem `li` aninhado, e a ação continua com a
classe exata `principal`.

### I-6 — A grade de rótulo e valor

`dl.campos` é comum (a convocação no Acompanhamento também o usa). A grade é um modificador,
`dl.campos.campos-em-grade`, que só "O que você informou" leva: borda e raio do cartão, e
`grid-template-columns:minmax(8rem,13rem) minmax(0,1fr)` a partir de 40rem; abaixo disso, rótulo sobre
valor, com separador entre os pares.

## Verificação

1. `tests/portal/test_composicao_das_telas_da_inscricao.py`: a coluna nas três telas, o começo comum, o
   cartão (ordem, prazo nos três casos e sem prazo vencido), um botão cheio, a grade.
2. Os guardiões existentes: `tests/interface` (folha, acessibilidade, larguras) e
   `tests/test_citacoes_de_requisito.py`.
3. O orçamento da lista: `tests/performance/test_lista_com_convocacao.py`.
4. No navegador: as três telas nas cinco larguras, com medida das margens, das bordas dos blocos e da
   rolagem horizontal por script de inspeção, e capturas antes e depois.
