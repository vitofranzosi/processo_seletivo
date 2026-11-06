# Implementation Plan: Andamento da seleção

**Branch**: `claude/127-andamento-da-selecao-ac9d30` | **Date**: 2026-11-06 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/127-andamento-da-selecao/spec.md`, com D-001 a D-016.

## Summary

Uma derivação de leitura, `interface/andamento.py`, lê os fatos do Edital publicado com as funções que
já decidem cada tela de ato (R-001) e os entrega a regras puras que dizem a situação de cada ponto da
jornada em cada lista. A sequência de cada Perfil vem da `jornada()` da `094`, com o marco de S3
reposicionado (R-002). A expectativa de cada Etapa vem da validação (R-003). Das células saem as
providências, agrupadas e ordenadas por `interface/providencias.py` (puro).

- **B1** — o detalhe do Edital publicado troca o começo de "O que fazer agora" pelas providências,
  sem a trilha de situação, com a "Atenção" das Etapas sem efeito; e, por último, o "Próximo nesta
  lista" nas mensagens de sucesso (R-012, D-015).
- **B2** — o cartão "Classificação" vira "Andamento da seleção", com a matriz composta por Perfil.

**Onde está o risco**: a derivação dizer o que a tela não confirma (mitigado pelo teste de coerência
por papel, SC-1230) e o custo do detalhe (teste de orçamento, R-011).

## Technical Context

**Language/Version**: Python 3.13 · **Primary Dependencies**: Django; nenhuma nova

**Storage**: PostgreSQL, só leitura. Nenhuma migration; o `M` do `provisionar` continua 53.

**Testing**: pytest contra PostgreSQL (`make test-pg`, `DB_NAME=spec127`). Regras puras em
`tests/unit/interface/` (sem banco); integração e coerência em `tests/interface/`, com as fixtures de
`tests/fixtures/` (`sorteio`, `ocupacao_sorteada`, `convocacao`, `recortes`, `comissao`, `mesa`,
`corte`); custo em `tests/performance/test_andamento_em_escala.py`. Visual com Playwright sobre o
clone `ps_spec127`.

**Target Platform**: `/gestao/editais/<id>/` (detalhe); por último, as telas de corte, ordenação,
ocupação, sorteio, convocação e documentos da convocação.

**Performance Goals**: o detalhe com o mesmo número de consultas para 3 e 30 inscrições, e abaixo do
teto fixado (SC-1239); a Etapa sem efeito não paga panorama.

**Constraints**: CSP sem estilo nem script embutido; classe nova com regra na folha (os guardiões de
`test_acessibilidade`); `details` nativo; nenhum `raise Http404` novo; nenhuma regra nova em tela de
ato; a varredura de vocabulário (as telas desta feature entram nela se usarem termos dela).

**Scale/Scope**: dois módulos novos (`andamento.py`, `providencias.py`), dois parciais
(`_o_que_fazer_agora.html` com as providências, `_andamento_da_selecao.html`), uma folha
(`interface/telas/andamento.css`), edições em `views.detalhe`, `detalhe.html`,
`editais/domain/validation.py` (o nome público) e, por último, em cinco views e templates de ato.

## Constitution Check

| Princípio | Como é atendido |
|---|---|
| I. Linguagem ubíqua | Os verbos são os das telas de ato; as situações são de apresentação e dizem isso (D-007). |
| II. Imutabilidade | Nada publicado muda; nenhuma escrita nova. |
| III. Segurança | Escopo do ator na porta do detalhe; nenhuma permissão nova; o nível 2 para quem já via o cartão (D-004); o nível 1 sem candidato, nota nem convocado; o link só a quem abre a tela. |
| IV. Regras explícitas | A recusa continua do domínio; a derivação antecipa o que as funções das telas dizem (R-005 a R-007), e o teste de coerência prende as duas. |
| V. Rastreabilidade e simplicidade | Spec, plano, tarefas, matriz e verificação; nenhuma fila, estado, tabela ou notificação (FR-4123). |
| VI. Completude de jornada | É o propósito: o trabalho depois da publicação ganha porta no detalhe. |

**Resultado**: passa. Pós-desenho: passa (nenhuma violação a justificar).

## Project Structure

### Documentation (this feature)

```text
specs/127-andamento-da-selecao/
├── spec.md · plan.md · research.md · data-model.md · quickstart.md · tasks.md
├── contracts/telas.md
├── checklists/requirements.md
├── rastreabilidade.md · verificacao.md   (na implementação)
└── capturas/                               (antes e depois)
```

### Source Code

```text
backend/processo_seletivo/
├── interface/
│   ├── andamento.py                 # novo: fatos + regras puras + composição (B1 e B2)
│   ├── providencias.py              # novo: agrupamento e ordem do nível 1 (puro)
│   ├── views.py                     # detalhe; por último, as views de ato (transição)
│   ├── templates/interface/
│   │   ├── detalhe.html
│   │   ├── _providencias.html       # novo (B1)
│   │   ├── _andamento_da_selecao.html  # novo (B2)
│   │   └── _proximo_nesta_lista.html   # novo (transição, por último)
│   └── static/interface/telas/andamento.css   # novo
└── editais/domain/validation.py     # quem_exige_o_resultado público
backend/tests/
├── unit/interface/test_andamento_situacoes.py · test_andamento_composicao.py · test_providencias.py
├── interface/test_andamento_do_edital.py · test_andamento_coerencia.py · test_andamento_transicoes.py
└── performance/test_andamento_em_escala.py
```

**Structure Decision**: a camada `interface/` é a que já lê `classificacao`, `sorteios`, `ocupacao`,
`convocacao`, `divulgacao` e `resultados` juntos (a `049` e a `104` moram aqui), e a direção de
dependência entre essas apps não muda.

## Os incrementos e os PRs

| | Conteúdo | PR |
|---|---|---|
| **B1** | derivação inteira; nível 1; trilha; Atenção; testes de situação, composição, providências, coerência, autorização, transição de leitura e custo; capturas | 1º PR, com os artefatos SDD |
| **B2** | nível 2 no lugar de "Classificação"; testes de apresentação e de largura; capturas | 2º PR, empilhado sobre o 1º |
| **Transições** | "Próximo nesta lista" nas telas de ato, sobre a `126` | no PR em que couber quando a `126` estiver mergeada (ou empilhado sobre ela); registrado na verificação |

## Complexity Tracking

Nenhuma violação. A derivação lê muitas funções, e por isso o custo é medido (R-011) e não suposto.
