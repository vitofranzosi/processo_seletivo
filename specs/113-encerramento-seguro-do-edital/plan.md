# Implementation Plan: Encerramento seguro do Edital

**Branch**: `claude/a11-edital-encerramento-diagnostico-a392fa` | **Date**: 2026-11-01 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/113-encerramento-seguro-do-edital/spec.md`

## Summary

Encerrar o Edital passa a conferir, sob a trava do Processo e depois a do Edital, cinco impedimentos —
período com término por vir ou em curso, prazo recursal computável em curso, recurso aguardando
decisão, reavaliação ou providência de recurso pendente, Retificação homologada — e recusa com 409
`pendencias_impeditivas`. A confirmação de encerrar e a de cancelar passam a listar impedimentos (só no
encerrar) e advertências, a partir de uma função de aplicação nova que reaproveita leituras existentes
(`periodo_de_inscricoes`, a janela da publicabilidade, a contagem de recursos da gestão, as pendências
de recurso e as providências da `099`). Nenhuma tabela nova. Detalhe em [research.md](research.md).

## Technical Context

**Language/Version**: Python 3.13, Django (monólito do repositório)
**Primary Dependencies**: as do projeto; nenhuma nova
**Storage**: PostgreSQL; nenhuma migration
**Testing**: pytest contra PostgreSQL (`make test-pg`), casos transacionais para trava e concorrência,
`como_producao` para privilégio de runtime
**Target Platform**: servidor Linux (produção), macOS (desenvolvimento)
**Project Type**: aplicação web (gestão em templates Django + API REST)
**Performance Goals**: confirmação de encerrar < 1 s com 400 inscrições (SC-1072), provada por
orçamento de consultas na suíte e por medição isolada (T030); o command confere sem ler o relatório
inteiro (R-001)
**Constraints**: imports de `recursos`, `divulgacao` e `publicacoes` dentro das funções do módulo
novo (R-001); CSP sem inline (estilo em arquivo, classe com regra na folha); nada de dado pessoal na
tela; nenhuma trava nova; nenhum ato posterior ao encerramento muda de comportamento (FR-3545)
**Scale/Scope**: um command, um módulo de aplicação novo, uma view, dois templates, um texto de
consequências; ~4 arquivos de teste novos e 3 ajustados

## Constitution Check

| Princípio | Como a feature o respeita |
|---|---|
| I. Linguagem ubíqua | Encerrado e Cancelado continuam distintos (FR-006 da `001`); "conclusão regular" deixa de ser afirmada sem ser conferida; os tipos da `099` mantêm o nome |
| II. Integridade normativa e imutabilidade | Nenhuma Publicação ou Retificação muda; A-09 intacto; Retificação homologada impede em vez de ser desfeita (D-003 da spec) |
| III. Segurança, proteção de dados, auditoria | Avaliação de LGPD na spec; contagens sem pessoa (FR-3540); caminhos só a quem a tela de destino aceita (R-006); recusa sem gravar ato, com o registro de recusa de domínio existente |
| IV. Regras explícitas e consistência | A regra está no domínio e no command, não só na tela; serializada pela trava do Processo (R-004); a tela antecipa o que o command recusaria (`recusa_certa`) |
| V. Qualidade, rastreabilidade, simplicidade | Reaproveita leituras existentes; uma regra para confirmação e relatório (D-004 da spec); matriz `rastreabilidade.md` com FR, SC e casos-limite |
| VI. Completude de jornada | Cada impedimento diz a ação e leva à tela que resolve, ou a quem pedir |

**Gates**: sem violação. Reavaliado depois do desenho: sem violação; nenhuma entrada em *Complexity
Tracking*.

## Project Structure

### Documentation (this feature)

```text
specs/113-encerramento-seguro-do-edital/
├── spec.md
├── plan.md              # este arquivo
├── research.md          # R-001 a R-008
├── data-model.md        # a Situação derivada e os tipos
├── quickstart.md
├── contracts/
│   └── encerramento.md  # serviço, tela e frases
├── checklists/
│   └── requirements.md
└── tasks.md             # /speckit-tasks
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── processos/
│   ├── domain/finalizacao.py                 # ensure_edital_can_be_closed(edital, impedimentos)
│   └── application/
│       ├── finalizacao.py                    # trava Processo → Edital; confere impedimentos
│       └── pendencias_do_edital.py           # NOVO: situacoes(edital, agora, com_advertencias)
├── recursos/application/selectors.py         # aguardando_decisao() (movido de interface/acoes.py)
├── divulgacao/domain/publicabilidade.py      # janela_aberta_ate (promovida, mesma regra)
└── interface/
    ├── acoes.py                              # importa aguardando_decisao
    ├── atos.py                               # consequências de encerrar
    ├── atos_retificacao.py                   # resumo: parada em Edital final
    ├── encerramento.py                       # NOVO: situação → frase, caminho, a quem pedir
    ├── relatorio_do_edital.py                # _pendencias_de_recurso passa a vir do módulo novo
    ├── views.py                              # praticar_ato monta pendencias para encerrar/cancelar
    ├── templates/interface/confirmar.html    # blocos, títulos, caminho por item
    ├── templates/interface/_retificacoes_em_curso.html
    └── static/interface/gestao/*.css         # regra para toda classe nova

backend/tests/
├── integration/processos/test_encerramento_seguro.py      # NOVO: FR-3528–3533, 3536, 3543, 3545
├── integration/processos/test_encerramento_concorrente.py # NOVO: SC-1070
├── performance/test_confirmacao_do_encerramento.py        # NOVO: SC-1072 (orçamento de consultas)
├── interface/test_confirmacao_do_encerramento.py          # NOVO: FR-3534–3542, 3544, SC-1069/1071/1072
├── unit/processos/test_pendencias_do_edital.py            # NOVO: cada tipo e cada caso-limite
├── integration/portal/test_desfecho_publico.py            # ajuste (R-008)
├── portal/test_prazo_recursal_publico.py                  # ajuste (R-008)
└── integration/publicacoes/test_retificacao_de_edital_encerrado.py  # deve seguir verde sem mudança
```

**Structure Decision**: o monólito existente; a regra nasce em `processos/application`, ao lado do
command que a aplica, e a interface só a redige.

## Fases

1. **Leituras reaproveitadas** — mover `aguardando_decisao`, `_pendencias_de_recurso`; promover
   `janela_aberta_ate`. Sem mudança de comportamento: a suíte da `099`, da `104` e da publicabilidade
   devem seguir verdes.
2. **Regra e command** — `pendencias_do_edital.situacoes`; `ensure_edital_can_be_closed` com
   impedimentos; travas em `_finalize_edital`. Testes de command e concorrência.
3. **Tela** — `interface/encerramento.py`, `praticar_ato`, `confirmar.html`, consequências, CSS.
4. **Retificação parada** — `resumo` e parcial.
5. **Ajustes de testes (R-008)** e suíte inteira; rastreabilidade.

## Complexity Tracking

Nenhuma entrada.
