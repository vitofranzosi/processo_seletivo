# Implementation Plan: Prévia interativa da classificação — fatia 1

**Branch**: `claude/094-previa-da-classificacao` | **Date**: 2026-10-19 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/094-previa-da-classificacao/spec.md`

## Summary

Um botão "Simular classificação" no cartão de todo marco por pontuação abre, fora do cartão, um painel
com candidatos fictícios calculados pelo motor oficial. O painel é um fragmento htmx: o servidor lê o
marco **digitado** com `forms.marco_do_formulario`, gera os candidatos do cenário escolhido, passa-os
pela mesma preparação do universo classificável que `calcular_ordem` usa — extraída para uma função
pura —, ordena com `desempate`, corta com `faixa.calcular`, confere a fronteira das vagas com
`apuracao.titulares_iniciais` e devolve a tabela com o porquê de cada linha. Nada é gravado.

O trabalho de risco não é a tela: é a **extração** (D-004) e a **irmã de `ordenar` com trajetória**
(D-011), que tocam o caminho oficial e precisam deixá-lo byte a byte igual. Por isso a ordem das
tarefas começa por elas, com a equivalência escrita antes, e só depois a interface.

O protótipo da spec (`prototipo/`, D-010) já executa o motor oficial e serve de referência visual e de
comportamento para a implementação; ele não é a implementação.

**Segunda rodada de UX (19/10).** O cálculo não mudou; mudou a apresentação e a origem dos candidatos.
O painel abre pela consequência geral, mostra o fluxo classificação → corte → Etapa seguinte, separa a
apuração das vagas como hipótese, começa a tabela pelos limites e compara os empates lado a lado
(FR-2238 a FR-2242). A população estável vira o padrão, com os casos-limite como demonstração (D-003
revista), e o estado anterior viaja no painel para dizer o que mudou (R-010). A US3 passou a P1. A
comparação com a primeira versão está em `prototipo/comparacao-v1-v2.md`.

## Technical Context

**Language/Version**: Python 3.13 (o `backend/pyproject.toml` do projeto)

**Primary Dependencies**: Django; htmx 2.0.4 servido de `interface/static/interface/htmx.min.js`. Nenhuma
dependência nova.

**Storage**: PostgreSQL — **só leitura** de Etapas, fatos declarados e quadro de vagas do rascunho. A
prévia não grava (FR-2234).

**Testing**: pytest contra PostgreSQL (`make test-pg`); unitários puros em `tests/unit/classificacao/`;
equivalência e ausência de efeito em `tests/integration/classificacao/`; interface em
`tests/interface/`; CSP em `tests/interface/test_politica_de_conteudo.py`.

**Target Platform**: a gestão (`/gestao/`), etapa Classificação da composição do Edital.

**Project Type**: monólito web Django com interface server-side e htmx.

**Performance Goals**: recálculo em até 1 s para faixa de até 500 candidatos fictícios (SC-841). A conta
é em memória: `combinar` e `ordenar` são lineares por grupo, e a única leitura de banco é a das Etapas,
dos fatos e do quadro do Edital, já feita hoje pela recomposição do cartão.

**Constraints**: CSP em recusa (`style-src 'self'`, `script-src 'self'`, sem `unsafe-inline`, sem
`hx-vals` com `js:`); `FR-428` da `030` (nenhuma ajuda visível no cartão); orçamento de consulta do
caminho oficial inalterado (SC-844); nenhuma regra no navegador (FR-2224).

**Scale/Scope**: um fragmento novo, uma rota, um template de painel, uma folha de tela, um script
estático de foco, um módulo de domínio novo (cenários e preparação do universo), uma função nova em
`desempate.py`, e a refatoração de `calcular_ordem`. Nenhuma migration.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como esta feature o cumpre | Situação |
|---|---|---|
| **I. Linguagem ubíqua** | O painel usa o vocabulário do cartão (alvo, suplentes, faixa, desfecho, Etapa governada, continuação, recorte). A divergência de leitura de `STRICT` que o achado de 19/10 aponta **não** é resolvida aqui: é registrada em DP-1 a DP-4, e o painel descreve o efeito como comportamento atual (FR-2229). | Cumpre, com pendência registrada |
| **II. Fonte única, imutabilidade** | A prévia não cria fonte paralela da regra: lê o marco digitado com o mesmo leitor da gravação e calcula com as mesmas funções. Não publica, não grava, não regenera nada do acervo. | Cumpre |
| **III. Negar por padrão, auditoria** | O fragmento exige a mesma autorização da tela de composição (`_edital_do_fragmento`), com 404 fora do escopo, classificado no inventário de negativas da `033`. Nenhum dado pessoal: os candidatos são fictícios (FR-2204). Nenhum evento de trilha, porque não há operação sensível — só leitura e cálculo. | Cumpre |
| **IV. Regras no domínio** | Toda regra fica no backend: combinação, ordem, faixa e apuração são as funções do domínio; o script estático só move o foco (FR-2224). A prévia torna visível, **antes** do ato irreversível (a publicação), a consequência da regra declarada — o que o princípio pede para valores derivados. | Cumpre |
| **V. Rastreabilidade, simplicidade, testes** | Matriz FR→tarefa→teste em `rastreabilidade.md`. A extração é a solução mais simples que evita uma segunda montagem do universo (D-004). Equivalência com sentinela que reprova quando o motor oficial muda (FR-2233). | Cumpre |
| **VI. Jornada observável** | A capacidade é alcançada pelo elaborador na tela em que ele declara a regra, e o critério de sucesso é de jornada (SC-840). | Cumpre |

Sem violação; a tabela de complexidade fica vazia.

## Project Structure

### Documentation (this feature)

```text
specs/094-previa-da-classificacao/
├── spec.md
├── plan.md                      # este arquivo
├── research.md                  # R-001 a R-009
├── data-model.md                # cenários, candidato fictício, prévia, universo classificável
├── quickstart.md                # roteiro de validação
├── contracts/
│   ├── fragmento-da-previa.md   # rota, parâmetros, respostas, negativas
│   └── universo-classificavel.md# a função pura extraída e a irmã de ordenar
├── rastreabilidade.md           # FR/SC → tarefa → teste
├── checklists/requirements.md
├── tasks.md                     # /speckit-tasks
└── prototipo/                   # D-010: servidor próprio, motor oficial de verdade
    ├── README.md
    ├── servidor.py  previa.py  pagina.py
    ├── estatico/prototipo.css  estatico/prototipo.js
    ├── comparacao-v1-v2.md      # os três cenários × as cinco perguntas, com as capturas
    └── capturas/v1/, capturas/v2/  # desktop e 375 px, das duas versões, em 19/10
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── classificacao/
│   ├── domain/
│   │   ├── universo_classificavel.py   # NOVO — preparar(...) puro, com recorte (D-004)
│   │   ├── desempate.py                # + ordenar_com_trajetoria; ordenar passa a derivar dela (D-011)
│   │   └── cenarios_da_previa.py       # NOVO — os cenários e os candidatos fictícios (D-003)
│   └── application/
│       ├── calculo.py                  # calcular_ordem chama universo_classificavel.preparar
│       └── previa.py                   # NOVO — simular(marco, etapas, fatos, vagas, cenario)
└── interface/
    ├── views.py                        # + fragmento_previa_da_classificacao
    ├── urls.py                         # + fragmentos/perfil/<indice>/marco/<sub>/previa
    ├── previa_da_classificacao.py      # NOVO — frases e linhas do painel (apresentação)
    ├── templates/interface/
    │   ├── _marco.html                 # + botão (só sob POR_PONTUACAO)
    │   ├── compor_classificacao.html   # + <aside id="painel-da-previa"> e anúncio
    │   └── _previa_da_classificacao.html  # NOVO — o painel
    └── static/interface/
        ├── telas/previa-da-classificacao.css   # NOVO — pelo bloco estilo_da_pagina
        └── previa-da-classificacao.js          # NOVO — só foco

backend/tests/
├── unit/classificacao/
│   ├── test_universo_classificavel.py
│   ├── test_ordenar_com_trajetoria.py
│   ├── test_cenarios_da_previa.py
│   └── test_previa.py                     # a matriz do achado sobre simular
├── integration/classificacao/
│   ├── test_previa_equivale_ao_oficial.py     # matriz da FR-2233 + sentinela
│   └── test_previa_sem_efeito.py              # FR-2234
└── interface/
    └── test_previa_da_classificacao.py        # botão, painel, recálculo, CSP, 375 px por CSSOM
```

**Structure Decision**: o cálculo mora em `classificacao` (domínio e aplicação), e a apresentação em
`interface`, como a recomposição do cartão. Os cenários são domínio puro — não tocam banco — porque o
teste de equivalência precisa gerá-los igual dos dois lados. As frases ficam na interface: são texto de
tela, e o vocabulário da composição é varrido lá (`test_vocabulario_da_composicao.py`).

## Fases

### Fase 0 — Pesquisa

[research.md](research.md): R-001 (a extração é o caminho certo, conferida no código), R-002 (o que
fica na consulta e o que sai), R-003 (a irmã de `ordenar`), R-004 (fragmento e alvo do troco), R-005
(população estável e casos-limite), R-006 (limites), R-007 (fronteira das vagas na prévia), R-008 (CSP e
foco), R-009 (o protótipo e o que ele prova), R-010 (o que mudou), R-011 (as linhas da tabela inicial),
R-012 (a terminologia).

### Fase 1 — Desenho

- [data-model.md](data-model.md): as quatro entidades da spec, campo a campo, sem tabela nova.
- [contracts/fragmento-da-previa.md](contracts/fragmento-da-previa.md): a rota, os parâmetros
  incluídos pelo `hx-include`, os estados da resposta e as negativas.
- [contracts/universo-classificavel.md](contracts/universo-classificavel.md): as assinaturas de
  `preparar` e de `ordenar_com_trajetoria`, e a garantia de igualdade.
- [quickstart.md](quickstart.md): como validar, com o protótipo hoje e com a feature depois.

### Ordem de implementação (detalhada em tasks.md)

1. **Equivalência primeiro**: os testes que fixam o resultado oficial de hoje sobre os cenários (ordem,
   posições, `separado_por`, sem posição, motivos, universo, número de consultas) entram **antes** da
   extração e passam contra o código atual.
2. **Extração** de `universo_classificavel.preparar` e **irmã** `ordenar_com_trajetoria`; os mesmos
   testes continuam verdes, e a suíte inteira de classificação, corte e ocupação também.
3. **Cenários e `application/previa.simular`**, puros, com a matriz do achado como teste.
4. **Fragmento, painel e botão**, com CSP, foco, anúncio e 375 px.
5. **Ausência de efeito** e sentinela da equivalência.

## Riscos

| Risco | Mitigação |
|---|---|
| A extração muda a ordem do acervo em silêncio | Equivalência escrita antes (passo 1) e `test_ordem_sem_reserva_nao_muda.py`, já existente, intocado |
| O orçamento de consulta de `calcular_ordem` sobe | A função pura não consulta; os testes de `tests/performance/test_ordenacao.py` e `test_corte.py` ficam iguais (SC-844) |
| O painel sugere ordem entre empatados | FR-2212: marca de grupo; teste de linha com dois empatados |
| A tela apresenta a leitura de `STRICT` como definitiva | FR-2229: "comportamento atual"; rótulos do cartão intocados; teste que o rótulo `A faixa para no alvo` continua igual |
| Guardiões do repositório reprovam no `test-pg` completo | Inventário de negativas da `033`, regra de folha para toda classe nova, lista literal de `test_vocabulario_da_composicao.py`, sem `}}` em CSS — tarefas próprias |

## Complexity Tracking

Sem violação da Constituição a justificar.
