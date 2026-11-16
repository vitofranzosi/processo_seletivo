# Implementation Plan: Os documentos que o GPS compõe nascem em PDF/A

**Branch**: `claude/pdfa-documentos-gerados-6d77eb` | **Date**: 2026-11-16 | **Spec**: [spec.md](spec.md)

## Summary

O escritor de PDF próprio do GPS (`publicacoes/infrastructure/pdf.py`) passa a escrever, nos
documentos que são ato ou relatório, os quatro objetos que a ISO 19005-2 cobra e que o estudo de 16/11
mediu: o `/ID` derivado do corpo, os metadados XMP com `pdfaid`, a condição de saída sRGB com um perfil
ICC versionado, e `/F 4` nas anotações. Um módulo novo, `pdfa.py`, escreve esses objetos; os três
pontos de montagem — `_arquivo_do_edital`, `render_documento` e `diagramacao._arquivo` — os acrescentam
**depois** dos objetos de sempre, de modo que nenhum número de objeto e nenhum fluxo de página mude no
Edital e nos relatórios. A família de `render_documento` passa a embutir a Edital Sans e a ser medida
por ela. O escritor antigo fica congelado para o comprovante das inscrições enviadas antes, escolhido
por uma coluna que a inscrição grava no envio. O veraPDF valida um exemplar de cada tipo num job de CI.

## Technical Context

**Language/Version**: Python 3.13, Django 5 (monólito existente)
**Primary Dependencies**: nenhuma nova em produção. O veraPDF 1.30.4 (`verapdf/cli`, presa pelo
resumo) só no CI
**Storage**: PostgreSQL; uma migration, `inscricoes/0008` (uma coluna booleana)
**Testing**: pytest contra PostgreSQL (`make test-pg`); o lote do veraPDF sob demanda
(`PDFA_EXEMPLARES`), como a fotografia do piloto da `172`
**Target Platform**: servidor Linux; os arquivos são lidos em qualquer leitor de PDF
**Project Type**: web, renderização no servidor
**Performance Goals**: composição sem custo perceptível — os objetos novos são constantes (3 KB de
perfil, ~1 KB de XMP) e um SHA-256 do corpo; a família ganha ~58 KB por arquivo pela fonte embutida
**Constraints**: determinismo (mesmo conteúdo, mesmos bytes); atos gravados não mudam; o comprovante
antigo continua byte a byte; nenhuma biblioteca de PDF no backend
**Scale/Scope**: três pontos de montagem, cinco chamadores, um modelo, uma view; nove tipos de documento

## Constitution Check

| Princípio | Como esta feature o respeita |
|---|---|
| Publicação é ato imutável | nenhum documento gravado é recomposto ou convertido (FR-8161); a conformidade vale para o que se compõe depois |
| Nada é excluído | a migration só acrescenta uma coluna; a enviada não é tocada (ADD COLUMN por catálogo, sem disparar o gatilho da `0007`) |
| Negar por padrão | nenhuma rota nova; o comprovante continua pela titularidade |
| Rastreabilidade por spec | `rastreabilidade.md` cobre FR-8150 a FR-8171 e SC-2820 a SC-2827; a emenda da `069` preserva a redação anterior |
| Assinatura digital proibida (FR-037 da `008`) | nenhum objeto de assinatura; o `/ID` não é certificado (FR-8167) |

Sem violação.

## Project Structure

### Documentation (this feature)

```text
specs/178-documentos-em-pdfa/
├── spec.md
├── plan.md               # este arquivo
├── research.md           # as decisões técnicas, com o que foi medido
├── tasks.md
├── rastreabilidade.md    # requisito → código → prova
├── checklists/requirements.md
└── demonstracao/
    ├── A-*-178.pdf, B-*-178.pdf   # o cenário da auditoria, regravado
    ├── antes/                     # um exemplar de cada tipo, composto pela main em 619a4ae0
    └── exemplares/                # os mesmos, compostos pela 178 e validados no veraPDF
```

### Source Code (repository root)

```text
backend/processo_seletivo/publicacoes/infrastructure/
├── pdfa.py                 # novo: XMP, condição de saída, /ID, a marca de imprimível
├── cor/                    # novo: sRGB2014.icc, LICENSE, ORIGEM.md
└── pdf.py                  # _arquivo_do_edital(pdfa=), _montar_o_arquivo(identificado=),
                            # render_documento PDF/A e _documento_com_a_helvetica congelado
backend/processo_seletivo/interface/diagramacao.py        # relatórios em PDF/A-2a
backend/processo_seletivo/{divulgacao,convocacao,agendamento}/infrastructure/documento*.py
backend/processo_seletivo/inscricoes/
├── infrastructure/comprovante_pdf.py   # render_comprovante_pdf(pdfa=)
├── models.py                           # Inscricao.comprovante_em_pdfa
├── migrations/0008_comprovante_em_pdfa.py
└── application/submissao.py            # o envio grava o escritor
backend/processo_seletivo/portal/views.py                 # página e download, mesmo escritor
backend/scripts/conferir_o_verapdf.py                     # relatório do veraPDF × manifesto
backend/tests/pdfa/                                       # exemplares, leitor mínimo, lote
.github/workflows/backend.yml                             # job pdfa; o veredito `test` o exige
```

**Structure Decision**: tudo dentro do escritor existente. Os objetos da conformidade moram num módulo
próprio porque três montagens os usam, e porque a regra de cada um (por que sem data, por que sem
filtro, por que derivado do corpo) é da norma e não de um documento.

## Fases

1. **Incremento A — Edital, Retificação e relatórios** (D-001). `pdfa.py`, o perfil, os acréscimos em
   `_arquivo_do_edital` e em `diagramacao._arquivo`; a prévia fica de fora; fixtures regravadas com a
   prova de que nenhuma página mudou.
2. **Incremento B — a família e o comprovante.** `render_documento` em PDF/A com a fonte embutida e a
   recusa da métrica errada; o escritor antigo congelado; a coluna da inscrição; a emenda da FR-1383.
3. **Verificação.** Os exemplares, o conferidor e o job; os testes de conformidade sem o validador.

Os dois incrementos estão no mesmo PR; a ordem acima é a das tarefas.

## Complexity Tracking

| Acréscimo | Por que é preciso | Alternativa mais simples rejeitada porque |
|---|---|---|
| Dois escritores em `render_documento` | o comprovante antigo tem resumo prometido (D-002) | um escritor só quebraria o resumo de quem já se inscreveu |
| Coluna na inscrição | o corte precisa ser fato gravado (D-005) | uma data de corte no código não se conhece quando o código é escrito |
| Job novo no CI | a conformidade precisa de leitura independente (FR-8168) | validar no próprio teste exigiria implementar a norma, ou Java na suíte |
