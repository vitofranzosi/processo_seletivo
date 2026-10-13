# Retificações — Edital nº 92/2026 (simulado)

Uma Retificação, publicada em 11/10/2026 com vigência imediata (v2). Roteiro de origem:
`cenario_b_corrigido.py` (parte final) da auditoria do PDF.


> **Revisão da rodada 2 (2026-10-11).** As unidades citadas passaram às sucessoras dos desdobramentos (LIB-0060 → LIB-0148; LIB-0061 → LIB-0149; LIB-0062 → LIB-0150; LIB-0007 → LIB-0151). O item 3 de *O que isso significa* dizia que a v2 “tira essa regra do Edital”, o que podia ser lido como fim do direito; passou a distinguir a cláusula do edital do direito previsto em lei. O item 1 dizia que a tradução “fica errada”; passou a dizer que precisa ser revista.

## O ato

- **Justificativa publicada:** “Retirada da seção de atendimento à pessoa com deficiência.”
- **Alteração** ([`fonte/pub2-alteracoes.json`](fonte/pub2-alteracoes.json)): uma só —
  `/sections/id=…/content` (seção `atendimento-pcd`), `REPLACE` por texto vazio.
- **Documento produzido:** o Edital inteiro, consolidado ([`fonte/pub2.pdf`](fonte/pub2.pdf)), com a marca
  de consolidação.
- **Avisos que o sistema deu na Retificação, e que não impediram a publicação**
  (`advertencias_do_ato`; `validation.py`, `typed_numbering_conflict_in_retification`):
  - conflito de numeração **comprovado** em «Dos Recursos», que passa a sair como seção 10 com três
    parágrafos começando por “11.”;
  - remissão **suspeita** «item 11.1» no 3º parágrafo da mesma seção;
  - conflito comprovado em «Da Convocação» (sai como 11, parágrafos “12.”);
  - conflito comprovado em «Disposições Finais» (sai como 14, parágrafos “15.”).

## Uma alteração de uma linha, e o documento inteiro se move

Esvaziar uma seção a retira do documento (`_materializaveis`), e a numeração é posicional
(`numeracao`). O efeito:

| Linha v1 | Trecho | v1 | v2 | Unidade |
|---|---|---|---|---|
| E92-178 | título da seção | 7. DO ATENDIMENTO À PESSOA COM DEFICIÊNCIA | **removido** | [LIB-0005](../../catalogo/unidades/LIB-0005.md) |
| E92-179 | 7, §1 | “O candidato com deficiência que necessitar de atendimento especializado…” | **removido** | [LIB-0107](../../catalogo/unidades/LIB-0107.md) |
| E92-180 | título | 8. ETAPAS DE AVALIAÇÃO | 7. ETAPAS DE AVALIAÇÃO | LIB-0005 |
| E92-181, E92-182 | itens gerados | 8.1, 8.2 | 7.1, 7.2 | [LIB-0108](../../catalogo/unidades/LIB-0108.md), [LIB-0046](../../catalogo/unidades/LIB-0046.md) |
| E92-183 | título | 9. CRITÉRIOS DE CLASSIFICAÇÃO | 8. … | LIB-0005 |
| E92-186 | título | 10. CRONOGRAMA | 9. … | LIB-0005 |
| E92-206 | título | 11. DOS RECURSOS | 10. … | LIB-0005 |
| E92-207 a E92-209 | subitens **digitados** | 11.1, 11.2, 11.3 | **continuam 11.1, 11.2, 11.3**, agora sob a seção 10 | [LIB-0148](../../catalogo/unidades/LIB-0148.md), [LIB-0118](../../catalogo/unidades/LIB-0118.md), [LIB-0149](../../catalogo/unidades/LIB-0149.md) |
| E92-209 | remissão digitada | “da prevista no item 11.1” | igual — e o item 11.1 já não é o dos recursos | LIB-0149 |
| E92-210 a E92-212 | título e subitens | 12. / 12.1, 12.2 | 11. / **12.1, 12.2** | LIB-0005, [LIB-0119](../../catalogo/unidades/LIB-0119.md), [LIB-0150](../../catalogo/unidades/LIB-0150.md) |
| E92-213, E92-215 | títulos | 13., 14. | 12., 13. | LIB-0005 |
| E92-217 a E92-220 | título e subitens | 15. / 15.1–15.3 | 14. / **15.1–15.3** | LIB-0005, [LIB-0121](../../catalogo/unidades/LIB-0121.md), [LIB-0068](../../catalogo/unidades/LIB-0068.md), [LIB-0151](../../catalogo/unidades/LIB-0151.md) |
| — (nova) | marca de consolidação | — | “Versão consolidada. …” | [LIB-0126](../../catalogo/unidades/LIB-0126.md) |
| E92-223, E92-224 | verificação e rodapé | `34bc1a9f…` | `b695a0e1…` | LIB-0071, LIB-0072 |

As quebras de página também mudam a partir da página 11.

**Não foram afetadas** as remissões geradas aos itens 3.19, 3.20 e 3.21 (seção 3 não muda de número) nem
os subitens digitados das seções 1, 2, 4 e 6, que estão antes da seção removida.

## O que isso significa para a tradução

1. **Toda tradução que sinalize um número de seção ou de item das seções 7 a 15 precisa ser revista na
   v2**, inclusive onde o texto não mudou uma letra. São oito títulos, dois itens gerados e oito subitens
   digitados.
2. **A remissão digitada passa a apontar para lugar errado.** Na v2, “item 11.1” não é mais o item dos
   recursos. Uma tradução fiel da v2 reproduziria o erro do ato; uma tradução “corrigida” deixaria de
   ser fiel. É decisão jurídica, não linguística, e não cabe ao tradutor.
3. **A cláusula retirada é de acessibilidade.** O atendimento especializado à pessoa com deficiência é a
   cláusula que alcança, entre outros, quem precisa de intérprete de Libras para participar das etapas. A
   v2 a retira **do edital**; isso não suprime direitos previstos em lei. Para ingresso em curso, a LBI,
   art. 30, prevê medidas de acessibilidade no processo seletivo; para concurso e seleção da Lei nº
   8.745/1993, o Decreto nº 9.508/2018, art. 4º. Qual norma alcança uma seleção de bolsistas como esta é
   questão jurídica ([`../../auditoria-sistema.md`](../../auditoria-sistema.md), §13). A tradução da v2
   comunica que a cláusula saiu do edital — e não que o direito deixou de existir; a da v1 continua sendo
   a do ato original.

## Roteiro específico da Retificação

1. **Identificação** — LIB-0002 + LIB-0126: Edital 92/2026, versão consolidada, retificada em 11/10/2026.
2. **Justificativa** — texto do ato (API pública da Retificação). Tradução nova.
3. **A alteração** — a seção “Do Atendimento à Pessoa com Deficiência” sai do edital (LIB-0107 sai).
   Não há texto novo a traduzir; há uma retirada a comunicar, sem afirmar o que a lei garante ou não.
4. **A consequência estrutural** — as seções seguintes mudam de número. Se o vídeo navega por número,
   todos os marcadores de navegação das seções 7 a 15 precisam ser refeitos; se navega por título, não.
5. **A inconsistência remanescente** — os subitens digitados e a remissão “item 11.1” não acompanham.
   Registrar para a área; não resolver no vídeo.

## Rastreabilidade

| Vídeo (futuro) | Vale para | Amarrar a |
|---|---|---|
| tradução da v1 | o ato original | conteúdo `34bc1a9f…`, documento `8795882f…` |
| tradução da v2 | a versão consolidada desde 11/10/2026 | conteúdo `b695a0e1…`, documento `a78c9342…` |
| trechos da v1 reaproveitados | só os que não carregam número de seção ou item das seções 7–15 | linha de cobertura + hashes |

## Pendências

- Decidir a política de navegação dos vídeos: por número (frágil a Retificação) ou por título (estável).
- Levar à área a inconsistência de numeração que a v2 publicou com aviso.
