# Implementation Plan: As telas de resultado e dos atos depois da inscrição, incremento paralelo

**Branch**: `claude/telas-de-resultado-084-48dfa6` | **Date**: 2026-10-18 | **Spec**: [spec.md](spec.md)

## Summary

Só apresentação, em onze templates, e um movimento só: a trilha sai do conteúdo e entra no bloco
`caminho_do_contexto` que a `077` criou, com o produto pelo parcial da `078` e os níveis do Edital —
Processos Seletivos, o Processo e o Edital — no começo, como o detalhe do Edital tem desde a `078`.
Nenhuma migration, nenhuma permissão, nenhum endereço, nenhuma view, nenhuma regra na folha comum,
nenhuma classe nova, nenhum texto de conteúdo; um parcial novo, com os níveis do Edital.

## Technical Context

Django 5 sobre PostgreSQL; nada de servidor muda. As onze views já entregam `processo` (de
`edital.processo`, com `select_related` na porta `_edital_para_classificar` e na da exportação) — a
trilha nova não custa consulta. A linha de base visual é o inventário refeito em 18/10 sobre
`cf6d7372`, no banco `ps_inventario_084` (cópia do `ps_inventario_telas`), nos dois estados da barra,
guardado em `doc/inventario-visual-da-gestao-2026-10-16/depois-da-084/antes/`; ele reproduz
`depois-da-080/` sem nenhuma variante diferente. A decisão de cada mudança e as alternativas
descartadas estão em [research.md](research.md). Não há entidade nem contrato externo:
`data-model.md` e `contracts/` não se aplicam.

## Constitution Check

- **Negar por padrão (III, IV)**: nenhuma condição de template muda; cada link da trilha leva a uma
  tela que já condiciona o acesso, e o novo — o Processo — abre para quem alcança o Edital no mesmo
  escopo institucional (`_processo_do_ator`).
- **Linguagem ubíqua (I)**: os rótulos da trilha são os que as telas já usavam; nenhum termo novo, e
  os termos definidos no primeiro uso continuam onde estão (D-003).
- **Imutabilidade (II)**: nenhum ato muda de rótulo, de lugar ou de peso; um guardião congela os
  botões de envio das onze telas (D-004).
- **Rastreabilidade (V)**: requisitos em `spec.md`, matriz em `rastreabilidade.md`, cobrada por
  `tests/test_citacoes_de_requisito.py`. A `FR-1803` da `080` é anotada como emendada na própria spec.
- **Simplicidade (V)**: um bloco por template. Nenhum script, nenhuma classe, nenhuma regra.
- **Completude de jornada (VI)**: o percurso é provado no navegador a 1280 e a 375 px, pelo teclado,
  e o inventário inteiro é refeito nos dois estados da barra e comparado campo a campo.

Sem violação a justificar.

## Design

| Peça | Mudança |
|---|---|
| `ordenacao.html`, `sorteio.html`, `corte.html`, `ocupacao.html`, `convocacao.html`, `matriculas.html` | o bloco `caminho_do_contexto` com a trilha do Edital e a tela no fim (R-001) |
| `ordenacao_confirmar.html` | o mesmo, terminando em *marco › Conferir*, com o marco no recorte que se confere; o comentário da `034` sobe junto (R-001) |
| `ato_ordenacao.html` | o mesmo, com o Edital, que faltava, antes de *Classificação › Ato …* (R-001) |
| `corte_historico.html` | o mesmo, terminando em *Corte de data e hora* (R-001) |
| `ocupacao_historico.html`, `convocacao_historico.html` | o mesmo, com a tela de origem antes de *Histórico* — a Convocação no mesmo recorte (R-001) |
| `_ate_o_edital_na_trilha.html` | novo: os três níveis do Edital, numa fonte só, incluídos logo depois do produto nas onze telas (R-001) |
| `tests/interface/test_telas_de_resultado_e_atos.py` | novo (R-003) |
| `doc/inventario-visual-da-gestao-2026-10-16.md` e `depois-da-084/` | o inventário de antes e o de depois nos dois estados da barra, a comparação e as capturas das telas do escopo |

## Verificação

`make lint check test-pg` com `DB_NAME=ps_084`; o percurso do [quickstart](quickstart.md) no
navegador, a 1280 e a 375 px, pelo teclado; o inventário refeito com `BARRA=expandida` e
`BARRA=recolhida`, comparado por `comparar.py` e por `medidas.py` com o de antes.
