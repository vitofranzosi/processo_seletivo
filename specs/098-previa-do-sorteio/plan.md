# Implementation Plan: Prévia do sorteio

**Branch**: `claude/sorteio-funcionamento-98c99f` | **Date**: 2026-10-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/098-previa-do-sorteio/spec.md`

## Summary

O marco por sorteio ganha "Simular sorteio" no cartão e a prévia no painel da `094`. Uma semente
fictícia, gerada na interface e assinada, semeia **o algoritmo oficial** sobre uma relação fictícia de
cada recorte — a ampla com todos, cada reservada com os autodeclarados; o corte e a rodada de ocupação
são **as funções da `094` e da `095`**; e 1.000 rodadas com sementes derivadas produzem o resumo de
frequências. Nada é gravado.

**O trabalho de risco não é a tela: são duas fronteiras.** A primeira é a do gerador: o app do sorteio é
proibido de importar `random` ou `secrets` (FR-026 da `021`, varredura em
`test_sem_gerador_pseudoaleatorio.py`), e a prévia o respeita gerando a semente fora dele (R-004). A
segunda é a da equivalência: a prévia só vale se ordenar como o sorteio oficial, e a prova injeta o
resumo da relação oficial na função da prévia (R-002, R-009).

**A medição mudou o tom da feature** (R-001). Com a população da história 1, sobra vaga de PPI sem
ocupante em **72%** das rodadas e, sob reversão por esgotamento, nada é cedido **nunca**: no sorteio, a
DP-1 e a DP-2 da `095` são a regra, e não o caso-limite. O resumo vai mostrá-lo na primeira abertura, e
o painel precisa chamá-lo de comportamento atual (FR-2507).

## Technical Context

**Language/Version**: Python 3.13 (o `backend/pyproject.toml` do projeto)

**Primary Dependencies**: Django (`django.core.signing` para o token da semente); htmx 2.0.4, já servido
pela gestão. Nenhuma dependência nova.

**Storage**: PostgreSQL — **só leitura** do snapshot do rascunho, o mesmo que a `094` e a `095` leem. A
prévia não grava (FR-2509).

**Testing**: pytest contra PostgreSQL (`make test-pg`); unitários puros em `tests/unit/sorteios/`;
equivalência e ausência de efeito em `tests/integration/sorteios/`; interface em `tests/interface/`.

**Target Platform**: a gestão (`/gestao/`), etapa Classificação da composição do Edital — o painel da
`094`.

**Project Type**: monólito web Django com interface server-side e htmx.

**Performance Goals**: rodada em até 1 s e resumo em até 5 s com 500 candidatos e seis reservadas
(SC-928). Medido no protótipo: 1,6 ms e 1,39 s (R-003).

**Constraints**: CSP em recusa (sem estilo nem script embutido); nenhuma ajuda visível no cartão (FR-428
da `030`); nenhuma regra no navegador; nenhum gerador de aleatoriedade em `sorteios/`; a direção
`sorteios → classificacao`, e a ocupação injetada pela interface (`test_dependencia_da_ocupacao.py`).

**Scale/Scope**: dois módulos novos no sorteio (`domain/simulacao.py`, `application/simulacao.py`), um
na interface (`previa_do_sorteio.py`); duas funções da prévia da classificação passam de privadas a
públicas sem mudar de corpo; um despacho no fragmento existente; um template e três parciais; regras na
folha da prévia. Nenhuma migration, nenhuma rota nova.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como esta feature o cumpre | Situação |
|---|---|---|
| **I. Linguagem ubíqua** | Recorte, relação, ocorrência, semente, posição sorteada, concomitância, ocupadas, reversão — o vocabulário da `021`, da `016` e da `095`; "avançariam" da `094`. A semente é chamada de **fictícia** em todo lugar em que aparece (FR-2482). DP-1 e DP-2 da `095` aparecem como comportamento atual, sem decisão (FR-2507). | Cumpre, com pendência registrada |
| **II. Fonte única, imutabilidade** | A ordem é `chave.ordem`, a semente é `normalizar`, o corte e a ocupação são as funções que o caminho oficial usa; os recortes vêm da derivação única (`recortes_do_perfil`). Nenhuma conta paralela, nem fórmula fechada para o resumo (R-003). Nada se publica, grava ou regenera. A FR-030 da `021` — nenhuma simulação depois da semente real — fica de pé: a prévia não aceita semente de fora (D-001, R-004). | Cumpre |
| **III. Negar por padrão, auditoria, LGPD** | A autorização e as negativas são as do fragmento da `094`. Nenhum dado pessoal é lido: candidatos, Modalidades e nomes são fictícios, sem marca de grupo. O token assina só material fictício e identidades do rascunho. Nenhum evento de trilha: não há operação sobre dado de ninguém. | Cumpre |
| **IV. Regras no domínio** | Toda conta no backend. A prévia torna visível, **antes** da publicação, a consequência de regras que a composição declara sem ver: concomitância, faixa da reservada, reversão. O gerador fica fora do domínio do sorteio, que continua determinístico. | Cumpre |
| **V. Rastreabilidade, simplicidade, testes** | Matriz FR→tarefa→teste em `rastreabilidade.md`. Equivalência com o caminho oficial e sentinela (R-009). Uma rota, um despacho; nada de fila, cache ou cálculo em segundo plano (R-003). | Cumpre |
| **VI. Jornada observável** | A capacidade é alcançada no painel que o elaborador já abre na etapa Classificação; o critério de sucesso é de compreensão (SC-925, SC-926). | Cumpre |

Sem violação; a tabela de complexidade fica vazia. **Reavaliado depois do desenho**: o data-model não
cria tabela, o contrato não cria rota, a varredura do gerador continua verde sem emenda e a
equivalência tem sentinela — sem mudança.

## Project Structure

### Documentation (this feature)

```text
specs/098-previa-do-sorteio/
├── spec.md
├── plan.md                                   # este arquivo
├── research.md                               # R-001 a R-010
├── data-model.md                             # semente, população, relação fictícia, rodada, resumo
├── quickstart.md
├── contracts/
│   ├── fragmento-da-previa-do-sorteio.md     # despacho, parâmetros, estados
│   └── sorteio-ficticio.md                   # as funções puras e a garantia de igualdade
├── prototipo/
│   └── medicao.py                            # R-001 e R-003, com o motor oficial
├── checklists/requirements.md
├── roteiro-de-compreensao.md                 # na implementação (SC-925, SC-926)
├── rastreabilidade.md                        # na implementação
└── tasks.md                                  # /speckit-tasks
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── sorteios/
│   ├── domain/
│   │   └── simulacao.py           # NOVO — população, relação fictícia, ordem por recorte (puro)
│   └── application/
│       └── simulacao.py           # NOVO — rodada (ordem + corte + ocupação injetada) e resumo
├── classificacao/
│   └── application/
│       └── previa.py              # (094) _corte → corte_da_ordem, _entrada_da_rodada → entrada_da_rodada
└── interface/
    ├── previa_do_sorteio.py       # NOVO — semente (secrets + signing), população do formulário, frases
    ├── previa_da_classificacao.py # (094) jornada aceita o marco por sorteio simulado (FR-2480)
    ├── views.py                   # (094) o fragmento despacha pela forma do marco
    ├── templates/interface/
    │   ├── _marco.html                      # + "Simular sorteio"
    │   ├── _previa_do_sorteio.html          # NOVO
    │   ├── _semente_ficticia.html           # NOVO — a faixa da semente e "Sortear de novo"
    │   ├── _populacao_do_sorteio.html       # NOVO — uma quantidade por lista
    │   └── _rodadas_do_sorteio.html         # NOVO — o resumo das 1.000 rodadas
    └── static/interface/telas/
        └── previa-da-classificacao.css      # (094) + regras dos blocos novos

backend/tests/
├── unit/sorteios/
│   ├── test_simulacao_ordem.py              # vetores normativos, determinismo, numeração
│   ├── test_simulacao_populacao.py          # sugestão, limite, nomes estáveis
│   └── test_simulacao_resumo.py             # agregação = soma das rodadas; constante; não avaliado
├── integration/sorteios/
│   └── test_previa_do_sorteio_equivale_ao_oficial.py   # R-009 + sentinela
└── interface/
    └── test_previa_do_sorteio.py            # botão, despacho, semente, recusa, vocabulário, CSP, sem efeito
```

**Structure Decision**: o que é do sorteio fica no sorteio — sem gerador; o que é do corte e da ocupação
é chamado de onde já está; a aleatoriedade e a assinatura ficam na interface, que é a única camada que
pode tê-las. O fragmento é o da `094`, e a prévia do sorteio é a segunda resposta dele, e não uma rota
paralela (R-007).

## Fases

### Fase 0 — Pesquisa

[research.md](research.md): R-001 (o motor sobre a população da história, medido), R-002 (onde a ordem
fictícia se calcula), R-003 (custo e número de rodadas), R-004 (semente: quem gera, formato, prova de
origem), R-005 (população, nomes, relação fictícia), R-006 (recortes), R-007 (fragmento, botão,
painel), R-008 (o que se reaproveita), R-009 (equivalência), R-010 (o que muda na `094`). Nenhuma
pendência técnica ficou aberta.

### Fase 1 — Desenho

- [data-model.md](data-model.md): as entidades, campo a campo, sem tabela.
- [contracts/fragmento-da-previa-do-sorteio.md](contracts/fragmento-da-previa-do-sorteio.md): despacho,
  parâmetros, estados, anúncio.
- [contracts/sorteio-ficticio.md](contracts/sorteio-ficticio.md): as funções puras e a garantia de
  igualdade.
- [quickstart.md](quickstart.md): o protótipo hoje, a interface e a suíte depois.

### Ordem de implementação (detalhada em tasks.md)

1. **Ordem fictícia e equivalência primeiro**: `sorteios/domain/simulacao.py` com os vetores normativos e
   o determinismo; depois o teste de integração da R-009, com a sentinela. Nada de tela.
2. **As duas funções da prévia passam a públicas**, sem mudar de corpo; a suíte da `094`/`095` fica igual.
3. **Rodada e resumo** em `sorteios/application/simulacao.py`, com a ocupação injetada; a matriz da R-001
   vira teste (as porcentagens com margem, as cessões exatas).
4. **Interface**: semente e token, população, despacho do fragmento, template e parciais, frases,
   jornada (FR-2480), botão no cartão.
5. **Emenda da `094`** (D-008): os três requisitos e o teste que muda (R-010).
6. **Ausência de efeito, CSP, 375 px, leitor de tela**; roteiro de compreensão; matriz de
   rastreabilidade.

## Riscos

| Risco | Mitigação |
|---|---|
| Um gerador entra em `sorteios/` "só para a prévia" | R-004: a semente nasce na interface; a varredura de `test_sem_gerador_pseudoaleatorio.py` continua verde **sem emenda**, e isso é tarefa com teste |
| A prévia ordena diferente do sorteio oficial e ninguém nota | R-009: equivalência com o resumo oficial injetado, e sentinela que prova que o teste quebra |
| O resumo reimplementa a regra por fórmula "porque é mais rápido" | FR-2504; R-003 mostra que não precisa; teste que o resumo é a soma das rodadas |
| O painel apresenta 72% de sobra como norma, e o elaborador conclui que o sistema está errado — ou certo | FR-2507: "comportamento atual"; pergunta própria no roteiro de compreensão; DP-1 e DP-2 continuam do usuário |
| O token da semente vira campo de semente | FR-2483: assinatura com Edital, Perfil e marco; teste que envia `material=`, `seed=` e token forjado (SC-931) |
| A mudança no fragmento quebra a prévia da pontuação | O despacho é a primeira linha; a suíte da `094`/`095` roda inteira, e o teste que muda é só o do R-010 |
| Recortes da prévia e do sorteio oficial divergem num Perfil que aponta Modalidade como ampla | D-005 e R-006: o painel diz que não simula essa lista; a divergência fica registrada para o usuário |

## Complexity Tracking

Sem violação da Constituição a justificar.
