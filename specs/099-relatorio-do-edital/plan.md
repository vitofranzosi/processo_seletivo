# Implementation Plan: Relatório do Edital

**Branch**: `claude/gps-executive-closure-report-2d9457` | **Date**: 2026-10-24 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/099-relatorio-do-edital/spec.md`

## Summary

Uma derivação de leitura por Edital — `interface/relatorio_do_edital.py` — reúne o que as telas donas
já calculam, decide a espécie, escreve a visão geral por regras e aplica a privacidade por desenho.
Duas saídas leem a mesma derivação: a página de gestão, com a camada executiva, e o PDF, com a camada
executiva e o anexo, composto pelo compositor de blocos da `100` desde 24/10/2026 (D-009; antes, pelo
escritor do Edital). Baixar o PDF é uma emissão:
trava o Edital, numera pela trilha e grava o evento com o resumo dos bytes. A leitura inteira vê um
instante só (`REPEATABLE READ`). Sem migration, sem tabela, sem permissão e sem dependência nova.

## Technical Context

**Language/Version**: Python 3.13 (o `backend/pyproject.toml` do projeto)

**Primary Dependencies**: Django; o motor de PDF próprio (`publicacoes/infrastructure/pdf.py`). Nenhuma
dependência nova.

**Storage**: PostgreSQL — só leitura, mais um evento em `RegistroAuditoria` por emissão.

**Testing**: pytest contra PostgreSQL (`make test-pg`); fixture do cenário coerente em
`tests/fixtures/relatorio.py`; unitários da derivação em `tests/unit/interface/`; integração em
`tests/integration/relatorio/`; tela e autorização em `tests/interface/`; orçamento em
`tests/performance/`.

**Target Platform**: a gestão (`/gestao/`), a partir do detalhe do Edital.

**Project Type**: monólito web Django, interface server-side.

**Performance Goals**: número de consultas independente do número de inscrições (SC-936). Medido no
estudo: 145 consultas com 38 e com 362 inscrições, 0,12 s e 0,17 s.

**Constraints**: CSP em recusa (estilo e script só por arquivo); gramática das portas da `033`
(recusa explicada no escopo, 404 fora dele, inventário das negativas); varreduras de vocabulário;
nenhum dado pessoal no documento.

**Scale/Scope**: três módulos novos em `interface/`; duas rotas; um template e uma folha de tela; uma
ação no detalhe do Edital; a fixture do cenário; nenhuma migration.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como esta feature o cumpre | Situação |
|---|---|---|
| I. Linguagem ubíqua | "Perfil de vaga", nomes publicados, rótulos simples já existentes (D-008, FR-2545); nenhum termo novo para conceito existente | ✅ |
| II. Integridade normativa | todo número deriva da fonte estruturada vigente; o relatório não reescreve nem reconstitui norma (FR-2521) | ✅ |
| III. Segurança e dados | porta da Supervisão; recusa explicada no escopo; sem dado pessoal; fato não público só por Perfil; emissão auditada com resumo (FR-2516, FR-2549 a FR-2551) | ✅ |
| IV. Regras explícitas | espécie derivada por regra escrita, sem estado novo; nenhuma ação em lote | ✅ |
| V. Simplicidade | sem tabela, fila, migration ou dependência; reuso das derivações existentes | ✅ |
| VI. Jornada demonstrável | gestão abre o relatório e baixa o PDF pelo navegador (SC-938) | ✅ |

Re-checado depois do desenho: nenhuma violação; *Complexity Tracking* vazio.

## Project Structure

### Documentation (this feature)

```text
specs/099-relatorio-do-edital/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/relatorio.md
├── checklists/requirements.md
├── rastreabilidade.md      # na implementação
└── tasks.md
```

### Source Code (repository root)

```text
backend/processo_seletivo/interface/
├── relatorio_do_edital.py        # derivação: instante, espécie, situações, frases, indicadores, anexo
├── relatorio_pdf.py              # composição: Composicao + _arquivo_do_edital + Navegacao
├── relatorio_trilha.py          # registros depois do desfecho (lê todo Resultado: exceção declarada)
├── relatorio.py                  # views: página (GET) e emissão (POST)
├── acoes.py                      # + a ação "Relatório do Edital"
├── urls.py                       # + duas rotas
├── templates/interface/relatorio_do_edital.html
└── static/interface/telas/relatorio.css

backend/tests/
├── fixtures/relatorio.py         # o cenário coerente, parametrizado
├── unit/interface/test_relatorio_do_edital.py
├── integration/relatorio/        # números, espécie, privacidade, emissão, determinismo
├── interface/test_relatorio.py   # porta, página, recusa, ação
└── performance/test_relatorio.py # orçamento de consultas

specs/033-navegacao-por-capacidade/inventario-das-negativas.md   # + a porta nova
backend/tests/test_gramatica_das_portas.py                       # + o módulo de view
```

**Structure Decision**: derivação, composição e view em `interface/`, como a Visão Geral e a Supervisão
(R-001).

## Fases

### Fase 0 — Pesquisa

[research.md](research.md): R-001 a R-012.

### Fase 1 — Desenho

- [data-model.md](data-model.md): a forma da derivação e do evento de emissão.
- [contracts/relatorio.md](contracts/relatorio.md): rotas, respostas, a ordem das seções e as frases.
- [quickstart.md](quickstart.md): como ver e validar.

### Ordem de implementação (detalhada em tasks.md)

1. Fixture do cenário coerente.
2. Derivação, de baixo para cima: ausências, indicadores, pendências, espécie, frases, anexo,
   privacidade.
3. Composição do PDF.
4. Views, rotas, ação, template e folha; inventário e gramática das portas.
5. Testes de integração, de interface, de orçamento e de conteúdo.
6. Rastreabilidade, README, quickstart executado, PDFs de demonstração.

## Riscos

| Risco | Mitigação |
|---|---|
| Falha de serialização na emissão concorrente | resposta "tente de novo"; teste do caminho |
| Número da tela dona e do relatório divergirem | os mesmos selectors; teste que cruza os dois (SC-933) |
| A fixture custar caro na suíte | cenário de 38 inscrições (~2 s); escala 10 só no teste de orçamento |
| Texto do Edital sem grafia na fonte embutida | a emissão recusa, como o Edital (`estrito`) |

## Complexity Tracking

Nenhuma violação a justificar.
