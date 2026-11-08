# Implementation Plan: A jornada não aponta o ato errado

**Branch**: `claude/133-jornada-sem-ato-errado`, sobre a `main` em `da566ff2` | **Date**: 2026-11-08 |
**Spec**: [spec.md](spec.md)

**Input**: a spec desta pasta, com as clarificações de 07/11 (R1, R2, R4) e de 08/11 (definição
estreita; a correção da convocação é recusada). Evidência: o
[estudo de convergência](../../doc/estudo-convergencia-ux-2026-11-07/README.md), PR #431.

## Summary

Uma regra de domínio nova e quatro correções de derivação, todas lidas de funções que já decidem as
telas.

- **A regra do marco intermediário** (D-001, R-001). Uma função pura,
  `classificacao/domain/marco_intermediario.py`, recebe o Perfil do conteúdo vigente e responde se o
  marco é intermediário e qual marco lê a Etapa governada.
  `classificacao/application/marco_intermediario.py` monta dela o impedimento (frase, marco que apura)
  e a recusa `apuracao_em_marco_intermediario`. É a mesma forma da `128`.
- **Os comandos** (FR-4532 a FR-4536, R-002) chamam a recusa sob a trava, antes de gravar:
  - `ocupacao.application.emissao._apurar`, que é a conta única da tela e do efeito de desfecho;
  - `acrescimo.acrescentar_vagas`;
  - `causar_faixa.causar_faixa_seguinte`;
  - `convocacao.application.convocar.convocar`, que é a porta da chamada individual, do lote e da
    correção da `120`.

  O desfecho, a conferência, a comunicação e o atestado ficam intocados (D-002). O desfecho já
  transforma a recusa da apuração seguinte em `apuracaoPendente` (R-003).
- **A previsão nas telas** (FR-4538, R-004):
  - a célula da apuração em `conducao_do_marco._celula_da_apuracao` passa a *Não se aplica*, com a
    nota;
  - por ela, a condução do marco, o resumo e a convocação do andamento deixam o marco intermediário
    de fora, sem regra repetida (FR-4539);
  - a conferência do gesto "Apurar" põe o recorte entre os impedidos;
  - as views da ocupação e da convocação levam o impedimento ao template, que troca os formulários
    pelo aviso com o link do marco que apura.
- **O corte em espera** (CV-02, FR-4541 a FR-4546, R-005):
  - uma função pura, `andamento.espera_do_corte`, lê a aferição da definitiva (a mesma que a célula
    do resultado já lê) e diz se o corte espera, até quando e por quê;
  - `situacao_do_corte` a recebe e devolve *Aguarda*, com a marca de recomendação (campo novo
    `recomendacao` na `Celula`, só de apresentação);
  - `da_lista` passa a preferir o que se pratica (*Pendente*, *Obsoleto*) ao que espera;
  - a tela do corte lê a mesma função e mostra a consequência antes do botão, que continua lá.
- **A próxima da fila** (CV-03, FR-4547 a FR-4549, R-006): em `_convocacao`, `em_aberto` passa a contar
  só as convocações sem desfecho cuja espécie não é `VAGA_INICIAL`.
- **A divulgação com ordem obsoleta** (CV-04, FR-4550 a FR-4552, R-007): em `situacao_do_resultado`, a
  ordem obsoleta dá *Depois* antes de olhar a publicação. O corte obsoleto já sai *Impedido* pela
  aferição, com a razão e quem resolve.
- **A frase do corte fixo** (CV-10, FR-4553 a FR-4556, R-008):
  - `pdf.frases_do_corte` ganha o parâmetro `com_reservadas`;
  - os três leitores passam o valor do Perfil: o compositor plano, o de perguntas da `069` e a
    Revisão;
  - o inventário que a FR-1398 da `069` exige está em [research.md](research.md), R-008.

## Technical Context

**Language/Version**: Python 3.13, Django (monólito do repositório)

**Primary Dependencies**: as do projeto; nenhuma nova

**Storage**: PostgreSQL. **Sem migration**, tabela, coluna nem estado persistido (SC-1428)

**Testing**: pytest contra PostgreSQL (`make test-pg`, com `DB_NAME` próprio). Testes puros para a
regra e para as `situacao_*`; testes de comando com a recusa sem gravação nem comunicação;
regressão dos quatro instantes do Edital 900 por um cenário de fixture (R-009); demonstração no
navegador pelos bancos de fase do estudo.

**Target Platform**: a gestão, renderizada no servidor

**Project Type**: aplicação web

**Performance Goals**:

- A regra lê o conteúdo que cada caminho já tem: **nenhuma consulta nova** nos comandos nem no
  andamento.
- A tela do corte ganha **uma** aferição de publicabilidade por lista exibida (R-005), que a prévia de
  publicação já faz. O orçamento da tela do corte (`tests/performance/`, se houver) é conferido na
  implementação.

**Constraints**:

- CSP sem inline: a marca de recomendação e os avisos usam classes com regra na folha.
- Toda classe citada em template precisa de regra na folha (`test_acessibilidade`).
- O vocabulário passa pela varredura.
- A recusa nova com código próprio precisa de linha no inventário de negativas (033), se for 404, e
  não é: é 409.

**Scale/Scope**:

- um módulo de domínio e um de aplicação novos;
- quatro comandos;
- três funções da derivação e a leitura delas;
- três views e três templates;
- a frase do corte em três leitores;
- testes.

## Constitution Check

| Princípio | Leitura | Situação |
|---|---|---|
| I. Linguagem ubíqua | "marco intermediário" é termo novo de domínio, definido na spec (FR-4530) e usado igual na regra, na recusa, na tela e no teste. "Não se aplica" e "Aguarda" são as situações da `127` | ✅ |
| II. Imutabilidade e temporalidade | Nada do acervo é tocado (FR-4540). A regra lê só campos não retificáveis, então a qualidade é a mesma em todo instante. Os documentos publicados ficam com os bytes, e a Revisão e o consolidado usam a frase vigente, como a FR-1397 da `069` admite (R-008) | ✅ |
| III. Negar por padrão | Uma recusa a mais, nenhuma permissão nova, e a recusa vale para qualquer caminho, inclusive a URL direta (R1) | ✅ |
| IV. Regra no backend | A regra é de domínio, chamada pelos comandos. As telas e a derivação preveem com a **mesma** função (FR-4531). A recusa acontece sob a trava, antes de gravar (FR-4536). A consequência do corte aparece antes do ato (princípio IV, decisões derivadas) | ✅ |
| V. Simplicidade e rastreabilidade | Sem estado. A espera do corte é apresentação de uma aferição que já existe (FR-4546). A matriz `rastreabilidade.md` liga cada FR a teste | ✅ |
| VI. Jornada demonstrável | Pelo navegador, nos bancos de fase do Edital 900: o cartão em 10/12, 13/12, 29/12 e 05/01, e a tela da ocupação e da convocação do marco 1 sem formulário ([quickstart.md](quickstart.md)) | ✅ |

**Depois do desenho:** sem violação. Nada em *Complexity Tracking*.

## Project Structure

### Documentation (this feature)

```text
specs/133-jornada-sem-ato-errado/
├── spec.md
├── plan.md               # este arquivo
├── research.md           # R-001 a R-010
├── data-model.md         # os conceitos derivados (sem persistência)
├── quickstart.md         # a demonstração e a verificação
├── contracts/
│   ├── recusas.md        # o código, a frase e onde cada recusa acontece
│   └── telas.md          # o que cada tela e a derivação mostram
├── checklists/requirements.md
├── tasks.md              # /speckit-tasks
└── rastreabilidade.md    # na implementação
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── classificacao/
│   ├── domain/marco_intermediario.py          # NOVO — a regra, pura (FR-4530, FR-4531)
│   └── application/marco_intermediario.py     # NOVO — impedimento e recusa (FR-4536, FR-4537)
├── ocupacao/application/
│   ├── emissao.py                             # _apurar chama a recusa (FR-4532)
│   ├── acrescimo.py                           # acrescentar_vagas (FR-4533)
│   └── causar_faixa.py                        # causar_faixa_seguinte (FR-4533)
├── convocacao/application/convocar.py         # convocar, também lote e correção (FR-4534)
├── interface/
│   ├── conducao_do_marco.py                   # célula e alcance da apuração (FR-4538, FR-4539)
│   ├── andamento.py                           # espera do corte, em_aberto, resultado, da_lista
│   ├── views.py                               # ocupacao, convocacao, corte: o impedimento e a espera
│   ├── templates/interface/{ocupacao,convocacao,corte,_providencia}.html
│   └── static/interface/...                   # regra da marca de recomendação e do aviso
├── publicacoes/infrastructure/{pdf,apresentacao}.py   # frases_do_corte(com_reservadas=)
└── interface/revisao.py                       # o terceiro leitor da frase
backend/tests/
├── unit/classificacao/test_marco_intermediario.py           # NOVO
├── unit/interface/test_andamento_*.py                        # casos novos nas situacao_*
├── integration/ocupacao|convocacao/test_*_marco_intermediario.py  # NOVO — recusa sem gravação
├── integration/interface/test_jornada_do_edital_900.py       # NOVO — os quatro instantes (R-009)
└── unit/publicacoes/test_redacao_das_frases.py               # a frase "de cada lista"
```

**Structure Decision**: o monólito existente. A regra mora em `classificacao`, porque fala de marco,
corte e Etapa governada. `ocupacao` e `convocacao` já importam `classificacao`, e a direção não muda
(a `R-002` da `016`).

## Complexity Tracking

Nenhuma violação a justificar.
