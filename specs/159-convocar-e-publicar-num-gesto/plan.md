# Implementation Plan: Convocar e publicar num gesto só (159)

**Branch**: `claude/convocar-e-publicar` | **Date**: 2026-11-12 | **Spec**: [spec.md](spec.md)

## Summary

A conferência dos titulares (140) e o formulário da chamada individual passam a carregar a autoridade,
o veículo e a declaração, e o comando de convocar publica na mesma confirmação: dentro da transação,
quando o GPS é o veículo oficial; depois dos envios ou dos registros, quando a relação é informativa.
Nenhuma tabela nova, nenhuma migration.

## Constitution Check

- **Publicação é ato imutável**: a publicação continua a da `149`; nada se regrava.
- **Negar por padrão**: a mesma base de gestão da comissão; a autoridade conferida pela `060`.
- **Rastreabilidade**: trilha do ato e de cada comunicação, como na `149`.

## Estrutura

```text
backend/processo_seletivo/convocacao/application/publicar.py   # núcleo extraído; prévia por convocações; publicar_do_gesto
backend/processo_seletivo/convocacao/application/fluxo.py      # convocar_titulares, convocar_e_comunicar, emitir_pendentes publicam
backend/processo_seletivo/interface/views.py                   # conferência, convocar_view, pendentes: campos novos
backend/processo_seletivo/interface/templates/interface/
  convocacao_conferir.html, _publicacao_no_gesto.html (novo), convocacao.html, _resultado_da_comunicacao.html
backend/tests/integration/convocacao/test_convocar_e_publicar.py
backend/tests/interface/test_convocar_e_publicar_na_tela.py
```

## Ordem

1. Núcleo da publicação extraído (D-003), sem mudar o comportamento da `149`.
2. Os titulares: mensagem (D-005) e GPS (D-004); veículo externo como hoje.
3. As pendentes: publicação externa registrada e reenvio publicam (D-007).
4. A chamada individual e a correção (D-009).
5. A conferência e os formulários (FR-6802 a FR-6804); o resultado diz o que aconteceu (FR-6806, FR-6812).
6. Testes, suíte, navegador com o C10.
