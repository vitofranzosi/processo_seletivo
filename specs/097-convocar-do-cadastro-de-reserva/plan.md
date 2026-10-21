# Implementation Plan: Convocar do cadastro de reserva, na ordem publicada

**Branch**: `claude/convocacao-cadastro-reserva-69e8a2` | **Date**: 2026-10-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/097-convocar-do-cadastro-de-reserva/spec.md`

## Summary

Uma tabela append-only nova na ocupação registra a **vaga acrescida depois da publicação** — e o ato
contrário que a desfaz —, com origem, fundamento e autor. A apuração passa a somar o saldo dela às
efetivas, congela os ids que leu e fica obsoleta pela sexta causa quando outro acréscimo chega. O
próprio ato emite a apuração seguinte, pela mesma conta, quando nada além dele mudou. A convocação não
muda: ela lê a apuração, e com efetivas maiores que zero o titular aparece e o gesto da `050` o chama.
A Revisão troca a frase de que a convocação é feita fora do sistema pela de que ela depende de vagas
acrescidas, e diz quantos a faixa publicada alcança.

As decisões técnicas estão em [research.md](research.md) (`T-001` a `T-012`); o modelo, em
[data-model.md](data-model.md); a tela e os atos, em [contracts/](contracts/); o roteiro, em
[quickstart.md](quickstart.md).

## Technical Context

**Language/Version**: Python 3.13 (o do `pyproject.toml`), Django 5.2

**Primary Dependencies**: as do projeto; nenhuma nova

**Storage**: PostgreSQL — uma tabela nova, `ocupacao_acrescimodevagas`, com gatilho e privilégio
ausente; nenhuma coluna nova em tabela existente (o congelamento vai no `universo` JSON da apuração)

**Testing**: pytest contra PostgreSQL (`make test-pg`), com unidade para a conta e a trava, integração
para os atos e a leitura, e interface para a tela

**Target Platform**: o monólito Django, gestão em `/gestao/`

**Project Type**: aplicação web, backend com templates

**Performance Goals**: `SC-924` — leitura do recorte, prévia e ato com custo de consulta constante no
número de acréscimos e no tamanho da ordem; medido como as consultas da ocupação já são, em
`tests/performance/test_ocupacao.py`

**Constraints**: CSP sem inline (`091`/`092`); vocabulário da `016` na tela da ocupação (`UX-034`); a
seta `convocacao → ocupacao` (`tests/test_dependencia_da_convocacao.py`)

**Scale/Scope**: um Edital do TMD tem dezenas de inscritos e poucas vagas acrescidas por semestre

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como o plano o atende | Situação |
|---|---|---|
| **I. Linguagem ubíqua** | "Vaga acrescida" é termo novo, distinto de Vaga publicada e de movimento de vaga (`T-001`); o vocabulário da ocupação continua o da `016` (`T-009`) | ✅ |
| **II. Imutabilidade e temporalidade** | Nada muda no Edital publicado nem na versão (`FR-2450`); o acréscimo é append-only e a apuração congela os ids que leu (`T-002`), de modo que a apuração antiga relida devolve o número dela (`SC-922`) | ✅ |
| **III. Segurança e auditoria** | A autoridade é a de quem apura, com escopo do Processo (`T-007`); cada ato vai à trilha com ator, recorte, quantidade e apuração anterior e seguinte (`FR-2466`); origem e fundamento só na gestão (`FR-2467`, `FR-2468`) — LGPD: nenhum dado pessoal novo é exigido, e a tela orienta a não nomear pessoas do outro Edital | ✅ |
| **IV. Regras explícitas e concorrência** | Recusas no domínio, dentro de `comando_de_comissao` com o Processo travado; a assinatura da prévia impede confirmar sobre leitura velha (`FR-2457`); a trava do desfazimento é avaliada sob o lock (`T-005`); o valor derivado — a apuração seguinte — é mostrado antes do ato, com autor e motivo (`FR-2456`) | ✅ |
| **V. Rastreabilidade e simplicidade** | Uma tabela, uma causa de obsolescência, um parâmetro na conta pura; nenhuma orquestração entre recortes; a matriz `rastreabilidade.md` liga FR a teste | ✅ |
| **VI. Jornada demonstrável** | O acréscimo, a conferência e o desfazimento são telas da gestão; a convocação que eles destravam é a tela que já existe (`SC-920`, `quickstart.md`) | ✅ |

Re-check depois do desenho: sem violação. A **`D-004` foi revista** ao planejar — de permissão própria
para a autoridade de quem apura —, e a revisão está escrita na própria decisão e em `T-007`.

## Project Structure

### Documentation (this feature)

```text
specs/097-convocar-do-cadastro-de-reserva/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── atos.md            # os dois comandos, as recusas e o declarado
│   └── tela.md            # rotas, campos, botões, a conferência e o que a tela diz
├── checklists/requirements.md
├── rastreabilidade.md     # escrito na implementação
└── tasks.md               # $speckit-tasks
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── ocupacao/
│   ├── models.py                         # + AcrescimoDeVagas
│   ├── migrations/0004_vaga_acrescida.py  # tabela, constraints, gatilho
│   ├── domain/nomes.py                   # espécies, causa nova, recusas
│   ├── domain/apuracao.py                # apurar(..., acrescidas=0)
│   ├── domain/acrescimo.py               # NOVO: saldo e travas, puro
│   ├── application/acrescimo.py          # NOVO: acrescentar_vagas, desfazer_acrescimo, previa
│   ├── application/emissao.py            # _apurar lê e congela os acréscimos
│   └── application/selectors.py          # sexta causa; acréscimos na leitura do recorte
├── convocacao/application/selectors.py   # + pessoas_chamadas (a trava do desfazimento)
├── seguranca/papeis.py                   # + a tabela em TABELAS_APPEND_ONLY (40 → 41)
├── editais/domain/validation.py          # a frase do aviso; o alcance; o achado das linhas
├── interface/
│   ├── urls.py                           # acrescentar-vagas, desfazer-acrescimo
│   ├── views.py                          # duas views; OPERACOES; AGREGADOS
│   └── templates/interface/
│       ├── ocupacao.html                 # publicadas · acrescidas · efetivas; formulário; lista
│       └── ocupacao_acrescimo.html       # NOVO: a conferência dos dois atos
└── auditoria/selectors.py                # o agregado novo na trilha do Edital

backend/tests/
├── unit/ocupacao/test_acrescimo.py              # conta, saldo, travas
├── unit/ocupacao/test_acrescimo_append_only.py  # modelo, lista, gatilho
├── integration/ocupacao/test_acrescimo.py       # atos, apuração seguinte, obsolescência, concorrência
├── integration/convocacao/test_reserva.py       # do acréscimo à convocação, e o desfazimento
├── interface/test_acrescimo.py                  # a tela, a conferência, recusas, quem não pode
└── unit/editais/test_reserva_convocada_fora.py  # a frase nova e o alcance
```

**Structure Decision**: o monólito como está. O registro e os dois atos moram na ocupação, porque são
fato de vaga e a tela é a dela; a convocação só ganha a pergunta que a trava do desfazimento faz
(`T-005`), passada como argumento.

## Riscos

| Risco | Sinal | Mitigação |
|---|---|---|
| A `096` muda a mesma validação e os mesmos testes | conflito em `validation.py` e em `test_reserva_convocada_fora.py` no merge | a frase muda e o código do achado não (`T-008`); quem mergear depois integra |
| A sexta causa deixa apuração antiga obsoleta | apurações sem `acrescimosLidos` acusadas | a causa só dispara com acréscimo cujo id não foi lido; sem acréscimo no recorte, nada muda |
| O titular que só a conta alcança trava o desfazimento | toda tentativa recusada | a trava conta pessoas chamadas, e não ocupantes (`T-005`); caso de teste próprio |
| A tela da ocupação ganha palavra da convocação | `test_vocabulario_da_ocupacao` reprova | o template e o módulo novos entram em `DA_016` (`T-009`) |

## Complexity Tracking

Nenhuma violação a justificar.
