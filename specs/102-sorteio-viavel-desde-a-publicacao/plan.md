# Implementation Plan: Sorteio viável desde a publicação

**Branch**: `claude/elegant-boyd-8955eb` | **Date**: 2026-10-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/102-sorteio-viavel-desde-a-publicacao/spec.md`, clarificada
em 29/10/2026 (D-005 a D-007).

## Summary

Cada adaptador de fonte passa a declarar se a fonte publica só a data (R-001). Uma regra pura, no
domínio do sorteio, calcula o **limite previsto** da ocorrência declarada (00h00 do dia de
`occurrenceAt`, no fuso institucional) e diz se ele é posterior ao congelamento mais cedo possível
(R-002). Essa regra é perguntada em quatro lugares:

- **na publicação**, contra o fim das inscrições, como achado impeditivo;
- **na Retificação**, contra o mesmo fim, como advertência com código próprio, exceto para marco já
  sorteado (R-004, R-005);
- **na tela do sorteio**, como aviso antes de congelar e como diagnóstico da relação já congelada
  (R-006);
- **na recusa por precedência**, que ganha a saída em três passos (R-007).

Uma segunda fonte de demonstração, que publica só a data, reproduz o caso sem rede (R-008).

**O risco não está na regra, que é uma comparação.** Ele está em três lugares:

1. no código da Retificação, que `advertencias_do_ato` apagaria se fosse o mesmo da publicação
   (R-004);
2. na tela, que hoje calcula a ocorrência da vez pelo método **vigente**, e não pelo que a relação
   comprometeu (R-006);
3. em não tocar a frase atual da recusa, que é da lacuna 2 e de outro PR (R-007).

## Technical Context

**Language/Version**: Python 3.13 (o `backend/pyproject.toml` do projeto)

**Primary Dependencies**: Django. Nenhuma dependência nova.

**Storage**: PostgreSQL, só leitura. Nenhuma migration, tabela ou coluna (ver
[data-model.md](data-model.md)). O `M` do `provisionar` continua 41.

**Testing**: pytest contra PostgreSQL (`make test-pg`). Regra pura em `tests/unit/sorteios/`.
Achados em `tests/unit/editais/`. Retificação, constituição e fonte em `tests/integration/`. Tela em
`tests/interface/`.

**Target Platform**: a gestão (`/gestao/`): revisão da composição, confirmação da Retificação e tela
do sorteio.

**Project Type**: monólito web Django com interface server-side.

**Performance Goals**: nenhum orçamento novo. A regra é uma comparação por método. A tela do sorteio
lê a versão citada por relação congelada, e `recortes_do_marco` já carrega essas relações; o plano
confere que não há consulta por recorte a mais (`select_related("versao")`).

**Constraints**: CSP em recusa (sem estilo nem script embutido); classes `aviso` e `erro` já
existentes; a comparação da constituição inalterada (FR-2664); a primeira frase da recusa
inalterada (R-007); sem dependência de `sorteios.domain` para `sorteios.infrastructure`.

**Scale/Scope**: um módulo novo (`sorteios/domain/viabilidade.py`), uma classe nova de adaptador,
uma função nova no vocabulário de fontes, um seletor novo, uma conferência nova em `validation.py`,
um argumento novo em `validate_for_publication`, dois blocos no template do sorteio e duas frases na
recusa.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como esta feature o cumpre | Situação |
|---|---|---|
| **I. Linguagem ubíqua** | Relação, congelamento, ocorrência, extração, fonte, Retificação, sucessão: o vocabulário da `021`. "Limite previsto" é o par, antes da observação, do "aconteceu não antes de" que a tela já mostra. | Cumpre |
| **II. Fonte única, imutabilidade, tempo** | Uma regra só para os quatro lugares (FR-2650). O fim das inscrições vem de `periodo_de_inscricoes`, a mesma leitura que o congelamento obedece (R-003). Nenhum conteúdo publicado é reconferido nem reescrito (FR-2667). O dia é tomado no fuso institucional, e os instantes novos saem nele. | Cumpre |
| **III. Negar por padrão, auditoria, LGPD** | Nenhuma permissão nova. Os avisos aparecem a quem já vê a tela, e o link para a Retificação só a quem pode retificar, como hoje. Nenhum dado pessoal é lido. Nenhum ato novo, então nenhum evento de trilha novo. | Cumpre |
| **IV. Regras explícitas, publicação como operação de domínio** | A publicação classifica o achado como impeditivo, e a Retificação como advertência, pela severidade, como o Princípio IV pede. O aviso antes do congelamento é a consequência visível "antes do ato irreversível". | Cumpre |
| **V. Rastreabilidade, simplicidade, testes** | Matriz FR→tarefa→teste em `rastreabilidade.md`, na implementação. A matriz da SC-954 é teste unitário puro. A comparação da constituição ganha teste de regressão que a fixa (FR-2664). | Cumpre |
| **VI. Jornada observável** | Os três atores alcançam a mudança pela tela que já usam: quem elabora pela revisão, quem retifica pela confirmação, quem conduz pela tela do sorteio. O [quickstart](quickstart.md) a demonstra no navegador. | Cumpre |

Sem violação, e a tabela de complexidade fica vazia. **Reavaliado depois do desenho**: o data-model
não cria tabela, o contrato não cria rota nem código de erro HTTP novo, e a segunda fonte de
demonstração fica atrás da mesma chave que produção já recusa. Nada muda.

## Project Structure

### Documentation (this feature)

```text
specs/102-sorteio-viavel-desde-a-publicacao/
├── spec.md
├── plan.md                 # este arquivo
├── research.md             # R-001 a R-009
├── data-model.md           # granularidade, limite previsto, inviabilidade, códigos
├── quickstart.md
├── contracts/
│   └── mensagens.md        # as cinco frases e onde não aparece nada
├── checklists/requirements.md
├── roteiro-de-compreensao.md  # na implementação (SC-958)
├── verificacao.md          # na implementação (SC-959)
├── rastreabilidade.md      # na implementação
└── tasks.md                # /speckit-tasks
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── sorteios/
│   ├── domain/
│   │   └── viabilidade.py               # NOVO — limite previsto e inviabilidade (puro)
│   ├── infrastructure/fontes/
│   │   ├── __init__.py                  # granularidade por nome; FONTE_DE_DEMONSTRACAO vira par de pares
│   │   └── loteria_federal.py           # atributo de granularidade; FonteDeTesteSoData
│   └── application/
│       ├── previa.py                    # recortes_do_marco: aviso do congelamento e diagnóstico da relação
│       ├── selectors.py                 # marcos sorteados em todos os recortes
│       └── sorteio.py                   # acréscimo à recusa occurrence_precedes_freeze
├── editais/domain/
│   └── validation.py                    # a conferência nova; argumento dos marcos sorteados
├── publicacoes/application/
│   └── retificacoes.py                  # passa os marcos sorteados nas duas chamadas
└── interface/templates/interface/
    └── sorteio.html                     # o aviso antes do botão e o diagnóstico antes do sorteio

backend/tests/
├── unit/sorteios/test_viabilidade.py                     # matriz da SC-954, fuso, meia-noite
├── unit/editais/test_extracao_inviavel.py                # achado, códigos, recuos da FR-2655
├── integration/sorteios/test_granularidade_das_fontes.py # FR-2649, as três fontes
├── integration/sorteios/test_recusa_diz_a_saida.py       # FR-2662–2664, comparação inalterada
├── integration/publicacoes/test_retificacao_extracao_inviavel.py  # advertência, marco sorteado
├── integration/editais/test_edital_72.py                 # SC-955
├── integration/sorteios/test_demonstracao_so_a_data.py   # FR-2665, a fonte nova ponta a ponta
├── interface/test_revisao_extracao_inviavel.py           # FR-2654, o achado na revisão
└── interface/test_sorteio_extracao_inviavel.py           # FR-2659–2661, botão disponível, CSP
```

**Structure Decision**: a regra é do sorteio e pura, e a infraestrutura de fontes responde só a
granularidade. A validação do Edital pergunta como já pergunta pelos algoritmos e regras do sorteio,
com import preguiçoso. A tela recebe o diagnóstico pronto de `recortes_do_marco`, sem conta no
template.

## Fases

### Fase 0 — Pesquisa

Concluída em [research.md](research.md). Nenhum `NEEDS CLARIFICATION` restou: as decisões de produto
são a D-005 a D-007, e as de lugar são a R-001 a R-008.

### Fase 1 — Desenho

[data-model.md](data-model.md), [contracts/mensagens.md](contracts/mensagens.md) e
[quickstart.md](quickstart.md). O quickstart registra uma restrição encontrada no desenho: o estado
que o aviso protege só se alcança por Retificação, porque a publicação recusa tanto o caso desta
feature quanto Edital com inscrições encerradas (FR-346 da `028`).

### Ordem de implementação (detalhada em tasks.md)

1. **Granularidade e fontes** (FR-2647–2649, FR-2665–2666): atributo, função por nome, segunda fonte
   de demonstração, teste de coerência. A suíte inteira precisa ficar verde sem mudança em fixture.
2. **Regra pura** (FR-2650, FR-2651): `viabilidade.py` e a matriz da SC-954.
3. **Publicação** (FR-2652–2655, FR-2657): achado impeditivo, recuos, o Edital 72 (SC-955).
4. **Retificação** (FR-2656): código próprio, seletor dos marcos sorteados, as duas chamadas em
   `retificacoes.py`.
5. **Recusa** (FR-2662–2664, FR-2668): as duas frases, e o teste que fixa a comparação.
6. **Tela do sorteio** (FR-2658–2661): diagnóstico em `recortes_do_marco` e os dois blocos no
   template.
7. **Rastreabilidade, README e `make lint check test-pg`.**

As etapas 3 a 6 dependem da 2. A 4 depende da 3, porque usa a mesma função. A 6 é independente da 3
e da 4.

## Riscos

- **A advertência da Retificação sumir em silêncio** se o código coincidir com o da publicação
  (R-004). O teste da etapa 4 a procura na confirmação, e não só na lista de achados.
- **Diagnóstico da relação calculado pelo método vigente**, repetindo o defeito que a tela já tem com
  a ocorrência da vez (R-006). O teste da FR-2661 retifica o método e confere a variante.
- **Conflito com o PR da lacuna 2**, que mexe na mesma mensagem. A primeira frase fica intocada, e o
  acréscimo vem depois dela (R-007). Quem chegar à `main` por último resolve o conflito, que fica
  restrito ao fim da mensagem.
- **Teste de tempo oscilando sob carga** (`test_ocupacao.py`, ver `CLAUDE.md`). Ele não tem relação
  com esta feature e não justifica refazer nada.

## Complexity Tracking

Sem violação da Constituição a justificar.
