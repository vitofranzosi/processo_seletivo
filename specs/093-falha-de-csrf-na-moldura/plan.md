# Implementation Plan: A recusa da verificação anti-falsificação na moldura do sistema

**Branch**: `claude/relaxed-bartik-660e4a` | **Date**: 2026-10-18 | **Spec**: [spec.md](spec.md)

## Summary

`CSRF_FAILURE_VIEW` passa a apontar para `interface/erros.py:falha_de_csrf`, que renderiza a recusa
que cada área já tem — `interface/recusa.html` sob `/gestao/`, `portal/recusa.html` no resto —, com a
requisição, os processadores de contexto e status 403. O texto é um só (D-004); o link de reabrir vem
da origem do envio só quando ela é do próprio servidor, pela conferência que a recusa do envio grande
já fazia, agora numa função comum (D-005). O motivo do framework vai ao logger do projeto (R-003). A
recusa do portal ganha a ajuda e o link opcionais. Nenhuma política, permissão, migration ou
dependência muda.

## Technical Context

**Language/Version**: Python 3.13, Django 5.2, PostgreSQL (nada de banco muda).

**Primary Dependencies**: o `CsrfViewMiddleware` do framework; nenhuma dependência nova.

**Storage**: N/A.

**Testing**: pytest (`make test-pg`); `tests/interface/test_falha_de_csrf.py`, novo; os casos de
`tests/interface/test_csrf.py` ficam como estão. Prova no navegador pela entrada `telas-082` (R-005).

**Target Platform**: o runserver local e a produção do guia — a página é a mesma nos dois (D-003).

**Project Type**: monólito web Django, interface por modelos.

**Constraints**: política de segurança de conteúdo intocada; nenhuma isenção nova; `.claude/launch.json`
intocado; nenhum estilo ou script embutido.

**Scale/Scope**: 1 view, 1 ajuste de configuração, 2 modelos, 1 arquivo de teste.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Negar por padrão (III, IV)**: a verificação recusa exatamente o que recusava; a view só escreve a
  página. Nenhum link para origem de fora (D-005).
- **Imutabilidade e preservação (II)**: nada é gravado; a página o diz.
- **Linguagem ubíqua (I)**: nomes e texto em português (`falha_de_csrf`, `_tela_de_origem`).
- **Rastreabilidade (V)**: requisitos em `spec.md`, matriz em `rastreabilidade.md`.
- **Simplicidade (V)**: reusa as duas recusas e a conferência de origem que já existiam; um texto só.
- **Completude de jornada (VI)**: as duas áreas, nas duas larguras, no navegador.

Sem violação a justificar. Reavaliado depois do desenho: igual.

## Project Structure

### Documentation (this feature)

```text
specs/093-falha-de-csrf-na-moldura/
├── spec.md
├── plan.md
├── research.md          # R-001..R-005
├── quickstart.md
├── tasks.md
├── rastreabilidade.md
└── checklists/requirements.md
```

### Source Code (repository root)

```text
backend/
├── config/settings/base.py                              # CSRF_FAILURE_VIEW
├── processo_seletivo/interface/erros.py                 # falha_de_csrf, _tela_de_origem
├── processo_seletivo/interface/templates/interface/recusa.html   # comentário
├── processo_seletivo/portal/templates/portal/recusa.html         # ajuda e reabrir opcionais
└── tests/interface/test_falha_de_csrf.py                # novo
```

**Structure Decision**: a view mora em `interface/erros.py`, junto das outras duas traduções de
recusa em página (D-001).
