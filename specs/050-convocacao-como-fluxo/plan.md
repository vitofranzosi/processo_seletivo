# Implementation Plan: A convocação como fluxo

**Branch**: `claude/convocacao-fluxo-unificado-11e7a3` | **Date**: 2026-09-28 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/050-convocacao-como-fluxo/spec.md`

## Summary

Três laços por pessoa viram gestos por recorte, sem tabela nova e sem migration. Um comando convoca os
titulares ainda não chamados, com uma `Convocacao` por pessoa, e a comunicação de cada uma sai depois do
`commit`, pelo `comunicar` que já existe, com chave derivada. Espécie e fundamento são derivados no
domínio; o vencimento é informado uma vez por ato, digitado ou tirado de um Evento do Cronograma. Um
segundo comando registra o não atendimento de todos os vencidos, reusando o registro do desfecho
individual. E todo desfecho passa a emitir a apuração seguinte na mesma transação, quando a única causa
de obsolescência é ele e a conta não move vaga ([research](research.md), `D-005`). As prévias carregam a
assinatura do alcance, conferida sob a trava.

## Technical Context

**Language/Version**: Python 3.12, Django 5 — o monólito existente.

**Primary Dependencies**: as do projeto; nenhuma nova.

**Storage**: PostgreSQL. Nenhuma tabela nova, nenhuma coluna nova, nenhuma migration. As tabelas
tocadas são as append-only que já existem: `Convocacao`, `ComunicacaoEmitida`, `DesfechoDaConvocacao`,
`EfeitoDeOcupacao`, `ApuracaoDeOcupacao`, e a trilha.

**Testing**: pytest contra PostgreSQL (`make test-pg`, com `DB_NAME` próprio).

**Target Platform**: servidor Linux; interface Django server-rendered da gestão.

**Project Type**: web — `backend/processo_seletivo/`.

**Performance Goals**: prévia de recorte com leitura em número constante de consultas (`SC-326`); o ato
em lote grava N linhas numa transação, e o envio acontece fora dela.

**Constraints**: append-only em duas camadas; negar por padrão; nenhum módulo da convocação grava
movimento de vaga (`test_dependencia_da_convocacao.py`); vocabulário da `019` verificado por varredura.

**Scale/Scope**: o maior recorte do 28/2026 tem ~85 pessoas; o Edital, 21 recortes e 280 titulares.

## Constitution Check

| Princípio | Como esta feature o cumpre |
|---|---|
| I. Publicação imutável | Não toca conteúdo publicado; lê a versão vigente e a cita em cada ato. |
| II. Fonte única | Nenhuma entidade de lote (`D-011`); espécie e fundamento derivados de uma função só; o registro do desfecho em lote é o mesmo do individual (`D-013`). |
| III. Negar por padrão | Os gestos passam por `comando_de_comissao`, com a mesma base; nenhuma permissão nova (`FR-887`). |
| IV. Regras explícitas | Recusas nomeadas, com código; o alcance é declarado e assinado antes da confirmação; a apuração seguinte só é emitida onde a regra é inequívoca (`D-005`). **O invariante da 1.2.0** (28/09, `DP-17`): o que é derivado — espécie, fundamento, vencimento, forma — aparece com a origem antes do ato (`UX-101`); o alcance de cada gesto é declarado e assinado (`FR-862`, `FR-863`, `FR-879`); cada registro tem autor (`FR-880`); e a apuração que o desfecho materializa é anunciada na confirmação (`FR-890`). A projeção numérica da apuração seguinte não é mostrada antes do ato: a forma escolhida é a frase, e o número aparece no resultado. |
| Nada é excluído / append-only | Só `INSERT`; corrigir continua sendo suceder, pessoa a pessoa. |
| Auditoria | Uma linha de trilha por registro, com o autor do gesto e a correlação do gesto. |

**Gate: passa.** Nenhuma violação a justificar.

## Project Structure

### Documentation (this feature)

```text
specs/050-convocacao-como-fluxo/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── convocacao-em-fluxo.md
├── rastreabilidade.md
├── checklists/requirements.md
└── tasks.md
```

### Source Code

```text
backend/processo_seletivo/
├── convocacao/
│   ├── domain/
│   │   ├── nomes.py            # códigos novos: alcance_mudou, especie_divergente_da_posicao, forma…
│   │   ├── especie.py          # NOVO: a espécie pela posição (puro)
│   │   ├── fundamento.py       # NOVO: o texto do fundamento (puro)
│   │   └── alcance.py          # NOVO: titulares do começo da fila; vencidos; assinatura (puro)
│   └── application/
│       ├── convocar.py         # espécie derivada; divergente recusada
│       ├── desfechar.py        # registro extraído; apuração seguinte no fim
│       ├── fluxo.py            # NOVO: prévias e os gestos — titulares, vencidos, pendentes, individual
│       └── selectors.py        # a leitura ganha o que as prévias precisam
├── ocupacao/application/
│   └── emissao.py              # NOVO: emitir_sucessora_por_efeito — dentro da transação, sem movimento
└── interface/
    ├── views.py                # quatro POSTs novos; convocar individual passa pelo fluxo
    ├── urls.py
    └── templates/interface/convocacao.html

backend/tests/
├── unit/convocacao/            # espécie, fundamento, alcance
├── integration/convocacao/     # os gestos, a apuração seguinte, a assinatura
├── interface/                  # a tela
└── performance/                # a prévia com 5 e com 85
```

**Structure Decision**: o monólito existente; a feature mora no app `convocacao`, com uma função nova
na `ocupacao`, que continua sem importar a convocação.

## Fases

1. **Domínio puro** — espécie, fundamento, alcance e assinatura, com testes unitários.
2. **Espécie derivada no comando** (`D-008`), com a fixture ajustada; medir quantos testes existentes
   passavam espécie errada.
3. **A apuração seguinte** (`D-005`): a função na `016`; o registro extraído de `desfechar` (`D-013`);
   os testes existentes que esperavam obsolescência depois de desfecho passam a esperar a sucessora.
4. **Os gestos** (`fluxo.py`): titulares, vencidos, pendentes e o individual que comunica.
5. **A tela**: prévias, formulários, resultados; o individual sem espécie e com fundamento derivado.
6. **Documentação**: a `DP-16` decidida; rastreabilidade.
7. **Verificação**: `make lint check test-pg`; percurso no preview.

## Riscos

- **Testes da `019` que desfecham e emitem a apuração à mão.** Depois da `D-005`, a apuração já foi
  sucedida pelo desfecho, e a emissão manual seguinte exige motivo. O ajuste é nos testes, e cada um
  será conferido: o comportamento que eles prendiam — obsolescência depois de desfecho — mudou por
  decisão, e não por acidente.
- **Espécie errada gravada por testes.** A recusa nova os revela; o conserto é deixar derivar.
- **A `049` em paralelo** mexe na tela do marco e não na da convocação; a faixa de identificadores não
  colide. O merge das duas pode exigir resolver `views.py`.

## Complexity Tracking

Nenhuma violação.
