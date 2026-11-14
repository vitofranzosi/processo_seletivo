# Contrato: telas e documento

## Composição das Etapas (UX-730, UX-731)

No cartão de cada Etapa, um grupo *"A quem a Etapa se aplica"*:

- ( ) **Todas as inscrições** — marcado por padrão
- ( ) **Só as inscrições destas Modalidades**
  - [ ] «denominação» (`«código»`) — «Perfis que a têm, ou "todos os Perfis"»

A lista de códigos é a união das Modalidades dos Perfis **do rascunho**, uma linha por código. Com
JavaScript, ela aparece só com a segunda opção marcada; sem ele, aparece sempre, e a gravação ignora
as marcas quando a primeira opção está marcada. Gravada restrita, a Etapa diz embaixo:
*"Alcança alguém em C1 e C2; em C3 nenhuma Modalidade marcada existe."* (só quando há Perfil sem
nenhum dos códigos).

## Revisão, página pública, tela de Retificação (FR-6984)

Uma linha na Etapa restrita: **Alcance** — a mesma frase do documento. Nada na Etapa que alcança
todas.

## Documento (FR-6983, T-010)

- Redação 1: par `["Alcance", "Somente candidatos inscritos em Pretos e pardos (PPI)"]`.
- Redações 2 e 3: frase depois da frase da Etapa — *"Aplica-se somente aos candidatos inscritos nas
  modalidades Pretos e pardos (PPI) e Pessoas com deficiência (PcD)."*
- Etapa com `modalityCodes` nulo: nenhum texto novo.

A denominação de cada código é a do conteúdo (coerente entre Perfis pela FR-6965), e os códigos saem
na ordem do conteúdo publicado (alfabética).

## Painéis da Etapa (UX-732)

Quando a Etapa é restrita, o cabeçalho do panorama — na distribuição, na Mesa e no andamento — diz
*"«n» inscrições alcançadas, de «m»"*, e a contagem por estado não inclui `fora-do-alcance` no total.
Etapa sem alcançados: *"Nenhuma inscrição alcançada."* (FR-6977).
