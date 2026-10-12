# Retificações — Edital nº 01/2026 (simulado)

Duas Retificações, publicadas no mesmo dia pelo `seed_demo` (`_retificar`): a primeira com vigência
imediata (v2), a segunda com **vigência futura** (v3).


> **Revisão da rodada 2 (2026-10-11).** Acrescentada a observação sobre a isenção de taxa (LIB-0152), que a rodada 2 tirou da descrição do Evento e tratou como regra própria; e as ligações com as [narrativas](narrativas/).

## Retificação a (v2) — vigência imediata

- **Justificativa:** “Ampliação de uma vaga imediata no perfil de docência.”
- **Alterações** ([`fonte/pub2-alteracoes.json`](fonte/pub2-alteracoes.json)): vagas imediatas do DOC-INFO
  de 2 para 3; linha geral (ampla) do quadro de 1 para 2.
- **Marca de consolidação:** “Versão consolidada. Publicado em 11 de outubro de 2026; retificado em 11 de
  outubro de 2026.”

| Linha v1 | Trecho | Antes | Depois | Unidade |
|---|---|---|---|---|
| — (nova) | marca de consolidação | — | ver acima | [LIB-0126](../../catalogo/unidades/LIB-0126.md) |
| E01-005 | 1, Tabela 1 — DOC-INFO e Total | 2 · Total 2 | 3 · Total 3 | [LIB-0013](../../catalogo/unidades/LIB-0013.md) |
| E01-006 | 1, Tabela 2 — DOC-INFO, ampla | 1 | 2 | [LIB-0014](../../catalogo/unidades/LIB-0014.md) |
| E01-053, E01-054 | verificação e rodapé | `c29f09d9…` | `c05270a3…` | LIB-0071, LIB-0072 |

**Só mudaram de página** (o texto é o mesmo): E01-012 (1 → 2), E01-030 a E01-034 (2 → 3), E01-049 e
E01-050 (3 → 4). Toda referência por página feita sobre a v1 deixa de valer na v2.

### O que não mudou no texto e deveria ser conferido

| Linha | Trecho | Observação |
|---|---|---|
| E01-017 | 1.1 › Corte — “Progridem para Análise documental os 2 (dois) primeiros desta ordem, mais 1 (um) suplente.” | **o corte é fixo em 2**, e as vagas passaram a 3. A Retificação mudou as vagas e não o corte; o documento consolidado publica as duas coisas. Com continuação não admitida (E01-019), a terceira vaga parece inalcançável pelo corte. Registrado como achado de conteúdo; não cabe à tradução resolver |
| E01-007 | 1, Tabela 3 — PPP 20% | o percentual não mudou; a reserva na Tabela 2 continua 1 |
| E01-043 | 5, Evento 1 — descrição | a isenção de taxa “até o 5º dia” (LIB-0152) fica igual; o edital não diz de quando se conta o “5º dia”, e na v3 o período é mais longo — pendência para a área |

## Retificação b (v3) — vigência futura

- **Justificativa:** “Prorrogação das inscrições, vigente a partir de 15 dias.”
- **Vigência:** 26/10/2026. **Publicada** em 11/10/2026.
- **Base:** a versão consolidada da v2 — o documento da v3 traz também a ampliação de vagas.
- **Alteração** ([`fonte/pub3-alteracoes.json`](fonte/pub3-alteracoes.json)): término do Período de
  inscrições, de 31/10/2026 para 10/11/2026.
- **Marca de consolidação:** “Versão consolidada. Publicado em 11 de outubro de 2026; retificado em 11 de
  outubro de 2026 e em 11 de outubro de 2026, com vigência a partir de 26 de outubro de 2026.”

| Linha v1 | Trecho | Antes (v2) | Depois (v3) | Unidade |
|---|---|---|---|---|
| — | marca de consolidação | uma data | duas datas e a vigência | LIB-0126 |
| E01-043 | 5, Evento 1 — término | 31/10/2026, às 09h43 | 10/11/2026, às 09h43 | [LIB-0050](../../catalogo/unidades/LIB-0050.md) |

### A vigência futura cria dois documentos válidos ao mesmo tempo

Entre 11/10 e 25/10/2026, **vale a v2** (inscrições até 31/10) e **já está publicada a v3** (inscrições
até 10/11, a partir de 26/10). A consulta pública não apresenta nenhum documento como vigente
(`interface/views.py`, l. 3515–3522): a vigência é da versão consolidada, consultada por instante
(`versao-vigente?em=…`).

Para a tradução, isso quer dizer:

1. o vídeo da v3 precisa dizer **desde quando** vale, e não só que existe;
2. durante quinze dias, quem procura “o edital vigente em Libras” precisa encontrar o da v2;
3. a marca repete “11 de outubro de 2026” duas vezes, porque as duas Retificações são do mesmo dia — é
   correto, e confunde; a tradução não deve “resumir” as duas datas numa.

## Roteiro específico das Retificações

**Retificação a:** identificação + marca (LIB-0002, LIB-0126) → justificativa (texto do ato) → vagas do
DOC-INFO (LIB-0013, LIB-0014: 3 vagas, 2 na ampla, 1 na PPP) → registro, para a área, do corte fixo em 2.

**Retificação b:** identificação + marca com vigência (LIB-0126) → justificativa → nova data de término
das inscrições (LIB-0050) → **a vigência a partir de 26/10/2026**, que é o que distingue este ato.

## Rastreabilidade

| Vídeo (futuro) | Vale para | Amarrar a |
|---|---|---|
| v1 | ato original | conteúdo `c29f09d9…`, documento `83c527b3…` |
| v2 | consolidado de 11/10 a 25/10/2026 | conteúdo `c05270a3…`, documento `bbc6f3d5…` |
| v3 | consolidado a partir de 26/10/2026 | conteúdo `f23684d2…`, documento `ab886c6b…` |

## Pendências

- Decidir como o vídeo comunica a vigência futura, e onde ele fica disponível antes dela.
- Levar à área o corte fixo em 2 diante de 3 vagas.
