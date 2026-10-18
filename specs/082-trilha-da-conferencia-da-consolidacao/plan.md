# Implementation Plan: A trilha da conferência da consolidação no cabeçalho de contexto

**Branch**: `claude/interesting-sammet-da84d5` | **Date**: 2026-10-17 | **Spec**: [spec.md](spec.md)

## Summary

Só apresentação, num template. `consolidacao_confirmar.html` sobrescreve o bloco `caminho_do_contexto`
que a `077` criou com a trilha da Distribuição e "Conferir" no fim — a mesma `nav` nomeada, com o
produto pelo parcial da `078`, que a conferência da retirada usa desde a `080` — e a tira do `main`.
Nenhuma migration, permissão, endereço, view, regra na folha ou classe nova.

## Technical Context

Django 5 sobre PostgreSQL; nada de servidor muda. A view `consolidar_resultados` já entrega `processo`
(de `edital.processo`) à conferência, e nenhum template a usava: a trilha nova não pede consulta a
mais. A tela é a resposta a um POST sem `confirmar=1`, e por isso não está no
[inventário visual](../../doc/inventario-visual-da-gestao-2026-10-16.md); como nenhum outro template
muda, o inventário não é refeito, e a prova visual é o percurso do [quickstart](quickstart.md), a
1280 e a 375 px, no banco `ps_inventario_082` (cópia do `ps_inventario_081`). Não há entidade nem
contrato externo: `data-model.md` e `contracts/` não se aplicam.

## Constitution Check

- **Negar por padrão (III, IV)**: a porta da conferência continua a da gestão da comissão; cada link
  da trilha leva a uma tela que já condiciona o acesso, e a trilha é a mesma que a Distribuição mostra
  a quem chega até ela.
- **Linguagem ubíqua (I)**: os níveis são os da Distribuição, e "Conferir" é o rótulo que a tela já
  usava (D-001).
- **Rastreabilidade (V)**: requisitos em `spec.md`, matriz em `rastreabilidade.md`, cobrada por
  `tests/test_citacoes_de_requisito.py`. A `FR-1803` da `080`, que deixava as demais telas com o
  cabeçalho da `076`, é anotada como emendada.
- **Simplicidade (V)**: um bloco de template. Nenhum script, classe ou regra nova.
- **Completude de jornada (VI)**: percurso no navegador, pelo teclado, a 1280 e a 375 px.

Sem violação a justificar.

## Design

| Peça | Mudança |
|---|---|
| `interface/templates/interface/consolidacao_confirmar.html` | o bloco `caminho_do_contexto` com a trilha; a `nav.trilha` sai do conteúdo (R-001) |
| `specs/080-*` (spec e rastreabilidade) | `FR-1803` anotada como emendada pela `082` |
| `README.md` | a linha da `082` na tabela das features |

## Testes

Novos em `tests/interface/test_trilha_da_conferencia_da_consolidacao.py`, com cenário próprio (R-002).
Nenhum teste existente muda (R-003).

## Verificação

`make lint check test-pg` com `DB_NAME` próprio; o percurso do quickstart no navegador.
