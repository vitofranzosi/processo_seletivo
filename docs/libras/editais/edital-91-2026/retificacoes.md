# Retificações — Edital nº 91/2026 (simulado)

Uma Retificação, publicada em 11/10/2026 com vigência imediata (v2). Roteiro de origem:
`cenario_a2.py` da auditoria do PDF de 08/10/2026.


> **Revisão da rodada 2 (2026-10-11).** A linha E91-045 dizia que uma tradução que concretizasse o número “estaria errada”; a frase decidia, pela tradução, uma questão que é dela. Passou a registrar a consequência de manutenção das duas escolhas.

## O ato

- **Justificativa publicada:** “Prorrogação das inscrições e ampliação de vagas no polo Bom Jesus do Norte.”
- **Alterações** ([`fonte/pub2-alteracoes.json`](fonte/pub2-alteracoes.json)):

| # | Caminho | Operação | Valor novo |
|---|---|---|---|
| 1 | `/schedule/id=…/endAt` (Período de inscrições) | REPLACE | 04/11/2026, 23h59 |
| 2 | `/profiles/id=…/immediateVacancies` (INF-BJN) | REPLACE | 45 |
| 3 | `/profiles/id=…/vacancyTable/id=…/immediateVacancies` (INF-BJN, ampla) | REPLACE | 33 |

- **Documento produzido:** o Edital inteiro, consolidado ([`fonte/pub2.pdf`](fonte/pub2.pdf)), com a
  marca “Versão consolidada. Publicado em 11 de outubro de 2026; retificado em 11 de outubro de 2026.”
  logo abaixo do anúncio. **Não existe documento só das alterações** (ver
  [`../../auditoria-sistema.md`](../../auditoria-sistema.md), §7).
- **O que o candidato vê no portal:** a justificativa e três linhas “alterado — <entidade> — <campo>”,
  sem valores (`publicacoes/domain/alteracoes.py`).

## O que mudou no documento

Comparação trecho a trecho da v2 com a v1, com as mesmas âncoras de cobertura.

| Linha v1 | Trecho | Antes | Depois | Unidade |
|---|---|---|---|---|
| — (nova) | Marca de consolidação | — | “Versão consolidada. Publicado em …; retificado em ….” | [LIB-0126](../../catalogo/unidades/LIB-0126.md) |
| E91-018 | 5, Tabela 1 — INF-BJN e Total | 40 · Total 160 | 45 · Total 165 | [LIB-0013](../../catalogo/unidades/LIB-0013.md) |
| E91-019 | 5, Tabela 2 — INF-BJN, ampla | 28 | 33 | [LIB-0014](../../catalogo/unidades/LIB-0014.md) |
| E91-073 | 11, Evento 1 — término | 30/10/2026, às 23h59 | 04/11/2026, às 23h59 | [LIB-0050](../../catalogo/unidades/LIB-0050.md) |
| E91-100 | Verificação de integridade | SHA-256 `083468eb…` | SHA-256 `d0186c03…` | [LIB-0071](../../catalogo/unidades/LIB-0071.md) |
| E91-101 | Rodapé (todas as páginas) | `083468eb97dfa584…` | `d0186c039d8f02c4…` | [LIB-0072](../../catalogo/unidades/LIB-0072.md) |

Nenhum trecho mudou de página.

## O que não mudou no texto e mudou no efeito

**Este é o ponto em que traduzir só o trecho alterado não basta.**

| Linha | Trecho | Por que é afetado |
|---|---|---|
| E91-045 | 5.6 › Corte — “até o número de vagas ofertadas no recorte, mais 15 (quinze) suplentes” | o texto é o mesmo, mas no polo BJN a ampla concorrência passou de 28 para 33: progridem mais pessoas para a análise documental. Se a tradução da v1 tiver explicitado o número, precisa ser atualizada; se tiver remetido às tabelas, a remissão continua certa e o que mudou está nelas |
| E91-070 | 10, §2 — “até o número de vagas do polo e da lista, mais os suplentes previstos” | mesmo caso, em texto livre |
| E91-048 | 6, §1 — “no período previsto no Cronograma” | a remissão continua certa, e o período a que ela remete mudou |
| E91-073 → E91-074 | Eventos 1 e 2 | as inscrições terminam em 04/11 e a relação do sorteio sai em 10/11: a sequência continua coerente, mas o intervalo entre os dois Eventos encolheu — conferir se algum texto livre dependia dele (não há, neste edital) |
| E91-012 | 2, §2 — carga horária | não afetada; registrada porque o mesmo dado também está na Tabela 1, e uma Retificação poderia mudar um sem o outro |

## Roteiro específico da Retificação

Na ordem em que um vídeo da Retificação precisaria comunicar. Recomendação documental, não solução
linguística.

1. **Identificação do ato retificado e da natureza do documento** — LIB-0002 (anúncio) + LIB-0126
   (marca de consolidação): é o Edital 91/2026, versão consolidada, retificado em 11/10/2026, com
   vigência imediata.
2. **Justificativa** — texto publicado no ato (não está no PDF; está em
   `GET /api/v1/public/retificacoes/<id>`). Tradução nova: a justificativa é texto livre de cada ato.
3. **Alteração 1 — prorrogação das inscrições** — LIB-0050: período de 13/10/2026, às 09h, a
   **04/11/2026, às 23h59**. Gravar de novo a linha do Evento, ou só a variável de data, depende de a
   unidade ter sido gravada de forma parametrizada.
4. **Alteração 2 — vagas do polo Bom Jesus do Norte** — LIB-0013 e LIB-0014: 45 vagas, 33 na ampla
   concorrência, PPI e PcD sem mudança; total do Edital 165.
5. **Efeito no corte** — LIB-0029: a regra não mudou; o número de pessoas que ela alcança no polo BJN,
   sim. Dizer isso é decisão de conteúdo (o ato não o diz), e por isso fica como pendência para a área.

As narrativas de [inscrição](narrativas/inscricao.md) e de [classificação](narrativas/classificacao.md)
registram o efeito da Retificação nos enunciados INS-91-03 e CLA-91-05.

## Rastreabilidade

| Vídeo (futuro) | Vale para | Amarrar a |
|---|---|---|
| tradução da v1 | o ato original, sempre | Publicação v1, conteúdo `083468eb…`, documento `0c69fb0f…` |
| tradução da v2 | a versão consolidada desde 11/10/2026 | Publicação v2, conteúdo `d0186c03…`, documento `47c9c120…` |
| trechos reaproveitados da v1 na v2 | só se o trecho e o seu efeito forem os mesmos | a linha de cobertura e o hash das duas versões |

A tradução da v1 **não se apaga** quando a v2 sai: o original continua sendo ato publicado (a
Constituição proíbe excluir dado normativo).

## Pendências

- Decidir se o vídeo da Retificação comunica efeitos não escritos no ato (o corte do polo BJN).
- Decidir se a tradução da v2 é um vídeo inteiro novo, ou a v1 com os trechos 3 e 4 regravados e a
  marca de consolidação acrescentada.
