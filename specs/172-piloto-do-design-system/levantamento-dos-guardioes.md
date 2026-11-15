# Levantamento dos guardiões candidatos

*FR-7741 e T043. **Nenhum guardião foi criado** (D-009). Quais nascem é a decisão 7 do roadmap do
estudo, e é do usuário. Este documento diz o que cada um dos cinco candidatos do
`doc/auditoria-design-system-2026-11-14/03-design-system.md` (§6.2) acusaria nas folhas que as cinco
telas do piloto carregam, antes e depois dele, e que exceções ele pediria.*

**Como foi medido (15/11).** As regras de cada candidato rodaram como leitura, sem teste, sobre as
três folhas próprias das cinco telas, com os comentários retirados: `telas/lista.css` (a Lista),
`grupos/confirmacao-de-ato.css` (a da P0, que a confirmação divide com o Processo e a Retificação) e
`grupos/piloto-ds.css` (a do piloto). A Ocupação e as conferências não têm folha própria: usam só a
comum da gestão, que os candidatos não alcançam.

## O resultado

| Candidato | O que recusa | `lista.css` | `confirmacao-de-ato.css` | `piloto-ds.css` |
|---|---|---|---|---|
| Cor só por token | `#hex`, `rgb()`, `hsl()` fora de `tokens.css` | 0 | 0 | 0 |
| Escala de fonte | `font-size` que não seja `var(--t-*)` | **9 usos, 5 valores** (`.8125rem`, `.85rem`, `.9rem`, `1rem`, `1.05rem`) | 0 | 0 |
| Escala de raio | `border-radius` que não seja `var(--raio*)`, `50%` ou `0` | **2 valores** (`4px`, `6px`) | 0 | 0 |
| Pontos de quebra | `@media` de largura fora dos quatro | 2 (`max-width:40rem`, que é o "celular" da proposta) | 0 | 0 |
| Caixa nova | regra com `border`, `border-radius` e `background` juntos | **2** (`.acoes-disponiveis`, `.processo`) | 0 | **2** (o recorte da Ocupação, a consulta da Lista) |

## O que cada linha diz

- **Cor só por token.** Nenhuma das três folhas tem cor literal, e a do piloto foi escrita sob essa
  regra. O candidato nasceria verde aqui. É o de contrato mais claro, como o estudo já dizia: a
  única falha de contraste medida veio de cor literal (a Visão Geral, corrigida na P0).
- **Escala de fonte.** É o que mais acusaria, e o piloto **não** o resolve de propósito: a redução
  tipográfica ficou fora (decisão 4). A folha do piloto não declara tamanho nenhum. O guardião só
  faz sentido depois que a escala `--t-*` existir, e ela não entrou em `tokens.css`.
- **Escala de raio.** A folha do piloto usa só `--raio-p` e `--raio`. `lista.css` continua com `4px`
  e `6px`, porque o piloto sobrepõe as regras dela no escopo em vez de mudá-las (FR-7702). Numa
  migração, os dois valores viram os dois tokens.
- **Pontos de quebra.** O piloto não precisou de nenhum `@media` próprio: as composições se resolveram
  por largura máxima e quebra natural. As três telas não informam se os quatro pontos da proposta
  bastam, porque nenhuma precisou de um.
- **Caixa nova.** **O candidato acusaria a própria folha do piloto duas vezes**: o recorte da
  Ocupação em cartão e a consulta da Lista em cartão desenham caixa por regra própria, e não pela
  classe `.cartao`. É o achado mais útil deste levantamento: o componente "cartão" da proposta não
  existe como classe aplicável fora do escopo, e por isso o piloto o escreveu duas vezes. Se o
  guardião nascer, nasce com estas duas na lista, ou depois de um `.cartao` comum que elas usem.

## O que se recomenda decidir, e com que exceções

| Candidato | Leitura deste levantamento | Exceções que pediria |
|---|---|---|
| Cor só por token | pronto para nascer | a sombra em `tokens.css`; a impressão |
| Escala de fonte | só depois da decisão 4 | a impressão (`pt`) |
| Escala de raio | pronto, com a lista de hoje | `lista.css` (`4px`, `6px`) até a migração da Lista |
| Pontos de quebra | sem evidência do piloto | as 19 condições de hoje, em lista que só diminui |
| Caixa nova | útil, mas pede antes o `.cartao` comum | o recorte da Ocupação e a consulta da Lista (piloto), `.acoes-disponiveis` e `.processo` (`lista.css`) |

É leitura de quem implementou o piloto, e não decisão.
