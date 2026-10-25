# Implementation Plan: Relatório consolidado da unidade

**Branch**: `claude/relatorio-consolidado-gps-b036c0` | **Date**: 2026-10-24 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/100-relatorio-consolidado/spec.md`

## Summary

A derivação do relatório do Edital (`099`) se separa em **fatos** — números por Perfil, pendências como
tipos, espécie — e **redação**, sem mudar o documento individual. O consolidado chama os fatos Edital a
Edital, numa leitura só, e os soma por uma função pura que não conhece o banco. Duas saídas leem a
mesma soma: a página de gestão, aberta a partir da Visão Geral, e o PDF, composto pelo escritor do
Edital. Baixar o PDF é uma emissão auditada na Unidade, numerada pela trilha. Na `099` entram três
correções autorizadas: supressão complementar por Perfil, marco de Perfil sem inscrição fora das
pendências e a trilha dita pelo que ela é. Sem migration, sem tabela, sem permissão e sem dependência
nova.

## Technical Context

**Language/Version**: Python 3.13 (o `backend/pyproject.toml` do projeto)

**Primary Dependencies**: Django; o motor de PDF próprio (`publicacoes/infrastructure/pdf.py`). Nenhuma
dependência nova.

**Storage**: PostgreSQL — só leitura, mais um evento em `RegistroAuditoria` por emissão.

**Testing**: pytest contra PostgreSQL (`make test-pg`); o cenário coerente da `099`
(`tests/fixtures/relatorio.py`), parametrizado por número e data de publicação para montar vários
Editais; unitários da soma em `tests/unit/interface/`; integração em
`tests/integration/relatorio_consolidado/`; tela e porta em `tests/interface/`; orçamento em
`tests/performance/`.

**Target Platform**: a gestão (`/gestao/`), a partir da Visão Geral.

**Project Type**: monólito web Django, interface server-side.

**Performance Goals**: consultas proporcionais ao número de Editais e independentes do de inscrições
(SC-942); emissão do conjunto do tamanho do limite no tempo de resposta da gestão. Medido no estudo:
120 consultas e ~0,3 s por Edital de dois Perfis.

**Constraints**: CSP em recusa (estilo e script só por arquivo); gramática das portas da `033`;
varreduras de vocabulário; nenhum dado pessoal no documento; documento individual da `099` inalterado
pela separação (SC-940).

**Scale/Scope**: dois módulos novos em `interface/` (derivação e composição); três rotas; dois
templates e uma folha de tela; um link na Visão Geral; refatoração interna de
`interface/relatorio_do_edital.py`; parametrização da fixture; nenhuma migration.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como esta feature o cumpre | Situação |
|---|---|---|
| I. Linguagem ubíqua | "Perfil de vaga", "inscrição", "cadastro", "convocação aceita"; nenhum termo novo para conceito existente; matrícula só como fato não registrado (FR-2583) | ✅ |
| II. Integridade normativa | todo número deriva da fonte estruturada vigente pela derivação da `099`; nada se reconstitui (FR-2565) | ✅ |
| III. Segurança e dados | porta da Visão Geral; escopo do ator; sem dado pessoal; fato não público nunca por Perfil ou lista; supressão complementar e exclusão do Edital pequeno; emissão auditada com resumo (FR-2554 a FR-2556, FR-2566, FR-2585 a FR-2588, FR-2592) | ✅ |
| IV. Regras explícitas | universo, soma e ausência por regra escrita; nenhum estado novo | ✅ |
| V. Simplicidade | sem tabela, fila, migration ou dependência; uma derivação somada, e não uma segunda | ✅ |
| VI. Jornada demonstrável | gestão escolhe o semestre, vê e baixa pelo navegador (SC-944) | ✅ |

Re-checado depois do desenho: nenhuma violação; *Complexity Tracking* vazio.

## Project Structure

### Documentation (this feature)

```text
specs/100-relatorio-consolidado/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/relatorio-consolidado.md
├── checklists/requirements.md
├── rastreabilidade.md      # na implementação
└── tasks.md
```

### Source Code (repository root)

```text
backend/processo_seletivo/interface/
├── relatorio_do_edital.py        # + Pendencia, FatosDoEdital, fatos_do_edital, redação separada,
│                                 #   supressão complementar, Perfil sem inscrição
├── relatorio_pdf.py              # + a frase da trilha
├── relatorio_consolidado.py      # novo: conjunto, leitura, soma (pura), frases, privacidade
├── relatorio_consolidado_pdf.py  # novo: composição do documento consolidado
├── relatorio.py                  # + escolha, página e emissão do consolidado
├── urls.py                       # + três rotas
├── templates/interface/relatorio_consolidado_escolha.html
├── templates/interface/relatorio_consolidado.html
├── templates/interface/visao_geral.html   # + o link
└── static/interface/telas/relatorio-consolidado.css

backend/tests/
├── fixtures/relatorio.py                          # + número e data de publicação parametrizados
├── unit/interface/test_relatorio_consolidado.py   # soma, universos, ausências, privacidade
├── integration/relatorio/                         # + supressão complementar, Perfil vazio, trilha
├── integration/relatorio_consolidado/             # conjunto, números × fontes, emissão, instante
├── interface/test_relatorio_consolidado.py        # porta, escopo, páginas, link
└── performance/test_relatorio_consolidado.py      # consultas por Edital; tempo no limite

backend/tests/test_gramatica_das_portas.py         # + as views novas, se a gramática pedir
```

**Structure Decision**: derivação, composição e views em `interface/`, como a Visão Geral e o relatório
do Edital, de onde vêm as leituras (R-010).

## Fases

### Fase 0 — Pesquisa

[research.md](research.md): R-001 a R-012.

### Fase 1 — Desenho

- [data-model.md](data-model.md): fatos do Edital, conjunto, consolidado, evento de emissão.
- [contracts/relatorio-consolidado.md](contracts/relatorio-consolidado.md): rotas, parâmetros,
  respostas, a ordem das seções e as frases fixas.
- [quickstart.md](quickstart.md): como ver e validar.

### Ordem de implementação (detalhada em tasks.md)

1. **Separação na `099`**, com a prova de composição idêntica nos quatro estados do cenário (SC-940).
2. **Correções na `099`**: supressão complementar, Perfil sem inscrição, frase da trilha — cada uma com
   teste próprio, e a composição mudando só nos cenários que elas alcançam.
3. **Fixture** parametrizada por número e data de publicação.
4. **Soma pura** e seus unitários: universos, razão, ausências, cancelados, privacidade.
5. **Conjunto e leitura**: critérios, escolha manual, escopo, limite, instante único.
6. **Composição do PDF**, views, rotas, templates, folha e link na Visão Geral.
7. **Integração, interface e orçamento**; medição do limite.
8. **Rastreabilidade, README, quickstart executado, PDF demonstrativo.**

## Riscos

| Risco | Mitigação |
|---|---|
| A separação mudar o documento individual | composição normalizada comparada nos quatro estados antes e depois (R-001) |
| Soma do consolidado divergir das fontes | testes que cruzam cada número com os fatos de cada Edital e com a Visão Geral (SC-939) |
| Emissão lenta com conjunto grande | limite medido, e não chutado (R-006); recusa explicada acima dele |
| Diferença entre emissões revelar Edital pequeno | Edital pequeno fora de todo número não público (R-007) |
| Falha de serialização na emissão concorrente | a mesma resposta "tente de novo" da `099` |

## Complexity Tracking

Nenhuma violação a justificar.
