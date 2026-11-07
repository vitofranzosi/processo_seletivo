# Implementation Plan: A organização da lista de Processos Seletivos

**Branch**: `claude/interesting-antonelli-d15d99`, sobre a `main` em `ffde747b` | **Date**: 2026-11-06 |
**Spec**: [spec.md](spec.md)

**Input**: a spec desta pasta; a Frente A da
[revisão de 06/11](../../doc/estudo-pagina-processos-seletivos-2026-11-06-revisao.md), seções 1, 5, 6,
7 e 9; a variante V1, decidida pelo usuário em 06/11/2026.

## Summary

Leitura e apresentação, em quatro lugares, sem estado novo:

- **O recorte e a busca** (`processos/application/selectors.py`): `listar_processos` passa a receber o
  recorte (aba ou busca) e devolve a consulta anotada com o **grupo** do Processo — em andamento,
  encerrado, cancelado — derivado da situação dele e da existência de Edital não final (FR-4301, D-001).
  `contar_por_situacao` passa a contar **Processos** por grupo, e os da busca, numa só agregação
  condicional (R-3). A busca casa título, código, título de Edital e número de Edital, com "N/AAAA"
  tratado à parte (R-2).
- **A montagem da página** (`interface/lista_de_processos.py`, novo): lê os parâmetros do endereço
  (aba, busca, página), pagina sem `Paginator` (R-4) e monta as frases do recorte e da busca. Funções
  puras sobre o que o seletor devolveu, testáveis sem requisição — o mesmo desenho de `visao_geral.py`.
- **A view `lista`**: lê **os Editais da unidade inteira uma vez** (R-5). Eles alimentam a faixa (FR-4323)
  e, agrupados por Processo, as linhas da página. As Retificações em curso são lidas para a unidade e
  servem à marca e à faixa. A coluna de ações sai: a view deixa de chamar `acoes.do_edital` por Edital,
  e o custo do exportador sai por construção (D-007).
- **A tela** (`lista.html`, `_acoes_disponiveis.html`, `_paginacao.html` novo, `telas/lista.css`): abas
  como navegação, busca com rótulo, a frase do recorte, a linha compacta V1 sem tabela, a paginação, a
  nota de cobertura antes dos itens da faixa e a mesma fonte na frase vazia (FR-4324, FR-4325).

O que só a coluna usava sai junto (R-6): `acoes.contagens_da_lista`, `acoes.para_a_lista`,
`CONFERIDOS_NO_DETALHE`, `acoes.da_linha`, `FREQUENTES`, `_acao_de_linha.html` e três regras da folha.

## Technical Context

**Language/Version**: Python 3.13, Django (monólito do repositório)

**Primary Dependencies**: as do projeto; nenhuma nova

**Storage**: PostgreSQL. **Sem migration**, tabela, coluna, permissão ou estado em sessão

**Testing**: pytest contra PostgreSQL (`make test-pg`, `DB_NAME` próprio da worktree); verificação no
navegador num banco descartável, a 1280 e a 375 px

**Target Platform**: a gestão, em navegador, renderizada no servidor

**Project Type**: aplicação web

**Performance Goals**: o número de consultas da lista é o mesmo com 3, 30 e 300 Editais, em toda aba,
busca e página, para todo papel de `identidade.PAPEIS` e para a combinação deles (FR-4327, SC-1313)

**Constraints**: CSP sem `inline`; classe citada no template exige regra na folha (guardião de
acessibilidade); a folha é lida como texto pelos guardiões (`}}` numa linha reprova); o vocabulário
das telas; os testes que prendem a coluna mudam conforme *Compatibilidade* da spec

**Scale/Scope**: um seletor, um módulo de montagem novo, uma view, três templates e um partial, uma
folha; um arquivo de teste de comportamento, um de seletor, um de escala; ajustes nos testes da coluna

## Constitution Check

| Princípio | Leitura | Situação |
|---|---|---|
| I — linguagem ubíqua | "Processo", "Edital", "Encerrado", "Cancelado", "Retificação em curso" são os termos do domínio; "Em andamento" nomeia o recorte, e não um estado novo (D-001) | ✅ |
| II — imutabilidade e temporalidade | nada é gravado; a lista lê o estado corrente, como hoje | ✅ |
| III — negar por padrão | nenhuma permissão nova; o escopo continua no filtro da consulta, também na busca (FR-4307); os links Comissão e Alocação continuam atrás da mesma porta | ✅ |
| IV — regra explícita | o recorte é uma função do seletor; a faixa continua sendo a derivação da `104`, sem cópia; a garantia lista × detalhe muda de forma e continua testada (FR-4329) | ✅ |
| V — simplicidade e rastreabilidade | sai o código que só a coluna usava (R-6); testes ajustados nomeados em `verificacao.md`; `rastreabilidade.md` cobre cada identificador | ✅ |
| VI — jornada demonstrável | captura da lista antes e depois, a 1280 e a 375 px (quickstart) | ✅ |

Nenhuma entrada em *Complexity Tracking*. Reavaliado depois do desenho: sem mudança.

## Project Structure

### Documentation (this feature)

```text
specs/129-organizacao-da-lista-de-processos/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/tela-da-lista.md
├── tasks.md
├── rastreabilidade.md
├── verificacao.md
├── capturas/
└── checklists/requirements.md
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── processos/application/selectors.py         # recorte, busca, grupo, contagem por grupo
├── interface/lista_de_processos.py            # novo: parâmetros, página, frases (puro)
├── interface/views.py                         # a view `lista`
├── interface/trabalho.py                      # FORA_DA_FAIXA e COBERTURA; do_ator sem `contagens`
├── interface/acoes.py                         # sai o que só a coluna usava (R-6)
├── interface/templates/interface/lista.html
├── interface/templates/interface/_acoes_disponiveis.html
├── interface/templates/interface/_paginacao.html   # novo
├── interface/templates/interface/_acao_de_linha.html  # sai
└── interface/static/interface/telas/lista.css

backend/tests/
├── integration/processos/test_recorte_dos_processos.py   # novo: o seletor
├── interface/test_organizacao_da_lista.py                # novo: a tela
├── performance/test_lista_em_escala.py                   # novo: todo papel, abas e páginas
└── (ajustes) interface/test_acoes.py, test_lista.py, test_polish_da_057.py,
    test_polish_da_055.py, test_acoes_disponiveis.py, unit/interface/test_trabalho_do_ator.py
```

**Structure Decision**: o monólito Django existente. A montagem nova vai para um módulo próprio da
interface, como `visao_geral.py`, para que a view continue sendo só montagem de contexto.
