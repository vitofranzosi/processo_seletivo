# Implementation Plan: Prévia interativa da classificação — fatia 2

**Branch**: `claude/095-previa-cotas-e-vagas` | **Date**: 2026-10-20 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/095-previa-cotas-e-vagas/spec.md`

## Summary

A prévia da `094` passa a calcular **um recorte por Modalidade**: a ampla, que é o universo inteiro, e
cada reservada, só com os autodeclarados. Para cada recorte, a mesma ordem, o mesmo corte e a mesma
comparação de empates da fatia 1; depois do corte, uma **rodada de ocupação** — a ampla com as vagas
publicadas, cada reservada sem quem ocuparia pela ampla, a reversão declarada —, num bloco de hipótese.
A jornada mostra todos os recortes e a união das faixas na Etapa seguinte; o detalhe ganha um seletor
de recorte. Nada é gravado.

O trabalho de risco, de novo, não é a tela: são as **duas extrações** (D-005) — quem ocupa pela ampla
e se a reservada tem quem ocupar —, que tocam o caminho oficial da ocupação e precisam deixá-lo igual,
inclusive nos comportamentos que esta spec registra como pendentes (DP-1, DP-2) e nos achados da R-002.
Por isso as tarefas começam por elas, com a equivalência escrita antes, e podem ser autorizadas à parte
da interface, como as T003 a T009 da `094` foram.

O protótipo desta spec é de cálculo (D-008): `prototipo/reproducao.py` roda o motor oficial sobre
populações com Modalidade e produz as tabelas da R-001.

## Technical Context

**Language/Version**: Python 3.13 (o `backend/pyproject.toml` do projeto)

**Primary Dependencies**: Django; htmx 2.0.4, já servido pela gestão. Nenhuma dependência nova.

**Storage**: PostgreSQL — **só leitura** do snapshot do rascunho (Modalidades, ampla apontada, linhas do
quadro, espécie de reversão), o mesmo que a fatia 1 lê. A prévia não grava (FR-2341).

**Testing**: pytest contra PostgreSQL (`make test-pg`); unitários puros em `tests/unit/ocupacao/` e
`tests/unit/classificacao/`; equivalência e ausência de efeito em `tests/integration/ocupacao/` e
`tests/integration/classificacao/`; interface em `tests/interface/`.

**Target Platform**: a gestão (`/gestao/`), etapa Classificação da composição do Edital — o painel da
`094`.

**Project Type**: monólito web Django com interface server-side e htmx.

**Performance Goals**: recálculo em até 1 s para 500 candidatos fictícios e até 7 recortes (SC-876,
R-006). Cada recorte reordena um subconjunto da mesma população; a ampla domina.

**Constraints**: os mesmos da `094` — CSP em recusa, nenhuma ajuda visível no cartão (`FR-428` da
`030`), nenhuma regra no navegador —, e o orçamento de consulta da apuração e da convocação
inalterado depois das extrações.

**Scale/Scope**: duas funções puras novas no domínio da ocupação e a troca das duas chamadas oficiais
por elas; a rodada de ocupação em `classificacao/application/previa.py`; a atribuição de Modalidade em
`cenarios_da_previa.py`; o parâmetro `recorte` no fragmento da `094`; blocos novos no painel. Nenhuma
migration, nenhuma rota nova.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como esta feature o cumpre | Situação |
|---|---|---|
| **I. Linguagem ubíqua** | Recorte, Modalidade, ampla concorrência, reservada, concomitância, efetivas, ocupadas, reversão — o vocabulário da `016` e da `034`; a espécie de reversão pelo rótulo do passo Perfis. "Avançaria" segue a decisão 016 da `094`. As duas leituras de norma que a medição levantou não são resolvidas: DP-1 e DP-2, com o painel descrevendo comportamento atual (FR-2337). | Cumpre, com pendência registrada |
| **II. Fonte única, imutabilidade** | Os recortes vêm da derivação única (`FR-491` da `034`); a ocupação, das funções da apuração; nenhuma conta paralela (D-005). Nada se publica, grava ou regenera. | Cumpre |
| **III. Negar por padrão, auditoria, LGPD** | Mesma autorização e negativa do fragmento da `094`. Autodeclaração e deficiência são dados sensíveis: a prévia não lê nenhuma, as Modalidades são fictícias e os nomes não carregam marca de grupo (FR-2342, Assumptions). Nenhum evento de trilha: não há operação sobre dado de ninguém. | Cumpre |
| **IV. Regras no domínio** | Toda conta fica no backend; as duas decisões hoje presas a consultas saem para o domínio, e o caminho oficial passa a chamá-las. A prévia torna visível, **antes** da publicação, a consequência de regras que a composição declara sem ver (alvo, suplentes, reversão). | Cumpre |
| **V. Rastreabilidade, simplicidade, testes** | Matriz FR→tarefa→teste em `rastreabilidade.md`. Equivalência escrita antes das extrações, com sentinela. Uma rodada, e não um ponto fixo (D-002): o mais simples que o produto também faz. | Cumpre |
| **VI. Jornada observável** | A capacidade é alcançada no painel que o elaborador já abre na etapa Classificação, e o critério de sucesso é de compreensão (SC-870). | Cumpre |

Sem violação; a tabela de complexidade fica vazia. **Reavaliado depois do desenho**: o data-model não
cria tabela, os contratos não criam rota, e a extração preserva o resultado oficial — sem mudança.

## Project Structure

### Documentation (this feature)

```text
specs/095-previa-cotas-e-vagas/
├── spec.md
├── plan.md                         # este arquivo
├── research.md                     # R-001 a R-009
├── data-model.md                   # recorte, candidato com Modalidade, prévia do recorte, rodada
├── variaveis-simuladas.md          # o que a fatia 2 passa a ler e a simular, sobre a matriz da 094
├── quickstart.md
├── roteiro-de-compreensao.md      # T031, extensão do roteiro da 094 (SC-870)
├── contracts/
│   ├── fragmento-da-previa.md      # o parâmetro recorte e os estados novos da resposta
│   └── ocupacao-pura.md            # as duas funções extraídas e a garantia de igualdade
├── rastreabilidade.md              # FR/SC → tarefa → teste
├── checklists/requirements.md
├── tasks.md                        # /speckit-tasks
└── prototipo/                      # D-008: cálculo, sem tela
    ├── README.md
    └── reproducao.py
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── ocupacao/
│   ├── domain/
│   │   ├── apuracao.py            # + ocupantes_pela_ampla (D-005, R-003)
│   │   └── reversao.py            # + ha_quem_ocupar (D-005, R-003)
│   └── application/
│       ├── selectors.py           # ocupantes_da_ampla consulta e chama a função pura
│       └── movimento.py           # ha_quem_ocupar lê as posições e chama a função pura
├── classificacao/
│   ├── domain/
│   │   └── cenarios_da_previa.py  # (094) + atribuição de Modalidade (R-005)
│   └── application/
│       └── previa.py              # (094) + recortes e rodada de ocupação (R-004)
└── interface/
    ├── previa_da_classificacao.py # (094) + frases dos recortes, da ocupação e da reversão
    ├── views.py                   # (094) fragmento lê `recorte`
    ├── templates/interface/
    │   └── _previa_da_classificacao.html   # (094) + seletor, resumo por recorte, bloco da ocupação
    └── static/interface/telas/
        └── previa-da-classificacao.css     # (094) + regras dos blocos novos

backend/tests/
├── unit/ocupacao/
│   ├── test_ocupantes_pela_ampla.py
│   └── test_ha_quem_ocupar.py
├── unit/classificacao/
│   ├── test_cenarios_com_modalidade.py
│   └── test_previa_por_recorte.py          # a matriz da R-001 sobre simular
├── integration/ocupacao/
│   └── test_extracao_da_ocupacao_equivale.py   # linha de base antes, igualdade depois
├── integration/classificacao/
│   ├── test_previa_por_recorte_equivale_ao_oficial.py   # FR-2340 + sentinela
│   └── test_previa_por_recorte_sem_efeito.py            # FR-2341
└── interface/
    └── test_previa_por_recorte.py          # seletor, blocos, vocabulário, CSP, 375 px
```

**Structure Decision**: o que decide ocupação fica na ocupação (`ocupacao/domain`), e a prévia o
chama — a mesma direção que a classificação já tem com `apuracao.titulares_iniciais`. Os arquivos
marcados "(094)" são os que a fatia 1 cria; esta spec os estende e não os duplica (D-001).

## Fases

### Fase 0 — Pesquisa

[research.md](research.md): R-001 (o que o motor faz com recortes, medido), R-002 (achados fora do
escopo), R-003 (as duas extrações), R-004 (a rodada passo a passo), R-005 (a população com
Modalidades), R-006 (limites), R-007 (o seletor e o fragmento), R-008 (participantes da Etapa
seguinte), R-009 (o que o protótipo prova). Nenhuma pendência técnica ficou aberta.

### Fase 1 — Desenho

- [data-model.md](data-model.md): as entidades da spec, campo a campo, sem tabela nova.
- [contracts/fragmento-da-previa.md](contracts/fragmento-da-previa.md): o parâmetro `recorte`, os
  estados novos e as negativas, sobre o contrato da `094`.
- [contracts/ocupacao-pura.md](contracts/ocupacao-pura.md): as assinaturas das duas funções e a
  garantia de igualdade.
- [variaveis-simuladas.md](variaveis-simuladas.md): as linhas da matriz da `094` que mudam.
- [quickstart.md](quickstart.md): como validar, com o protótipo hoje e com a feature depois.

### Ordem de implementação (detalhada em tasks.md)

1. **Equivalência da ocupação primeiro**: a linha de base de `ocupantes_da_ampla` e de
   `ha_quem_ocupar` sobre cenários com reserva — inclusive o titular eliminado e a reservada toda
   ocupando pela ampla —, escrita antes e verde contra o código atual.
2. **Extração** das duas funções; a mesma linha de base, a suíte de ocupação e de convocação e os
   orçamentos de consulta continuam iguais. Os passos 1 e 2 não dependem da interface da `094`.
3. **Rodada e recortes na prévia** (`simular`), puros, com a matriz da R-001 como teste.
4. **População com Modalidades** e casos-limite.
5. **Painel**: jornada, seletor, blocos, "o que mudou", vocabulário, CSP e 375 px — depois da
   interface da `094`.
6. **Ausência de efeito**, sentinela da equivalência, extensão visual do protótipo da `094`.

## Riscos

| Risco | Mitigação |
|---|---|
| A extração "corrige" de passagem um dos achados da R-002 ou um comportamento de DP-1/DP-2 | Linha de base escrita antes, com os dois casos nomeados; o contrato manda preservá-los (D-005) |
| O orçamento de consulta da apuração ou da convocação sobe | As funções puras não consultam; os testes de orçamento da `016` e da `019` ficam iguais |
| O painel apresenta o comportamento de DP-1 ou DP-2 como norma | FR-2337: "comportamento atual"; teste de vocabulário sobre as frases da reversão e da faixa da reservada |
| A Modalidade fictícia sugere grupo por nome | FR-2342: nomes sem marca; teste que nenhum nome fictício contém o código ou o nome de Modalidade |
| A ampla da prévia muda num Perfil que só ganhou uma Modalidade | D-003: Modalidade atribuída, sem candidato novo; teste de que a ordem da ampla é a mesma com e sem Modalidades declaradas |
| A interface da `094` muda antes desta começar | D-001: as tarefas de painel dependem da conclusão da `094`; as de domínio não |

## Complexity Tracking

Sem violação da Constituição a justificar.
