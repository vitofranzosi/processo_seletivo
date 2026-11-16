# A Distribuição da Etapa não foi recomposta pela migração do design system

**Data:** 2026-11-16
**Origem:** a revisão visual que o usuário fez das capturas da `179` ("não gostei da UI/UX desta
tela; olha os desalinhamentos, campos ocupando espaço desnecessário"). Medido a 1280 px, no cenário de
treinamento C20, sobre a branch da `179` com a `main` em `dc758944`.
**Natureza:** composição de tela; nada aqui é defeito de comportamento.
**Situação:** **registrado, sem escopo**, por decisão do usuário em 16/11. O que era da `179` — o
conflito numa caixa dentro do cartão "Agenda" e a mesma frase repetida em "Quem está alocado" — foi
corrigido no #583. O resto depende das pendências P-1 a P-3 da `175`, que são do usuário.

## O que se vê

Largura útil do conteúdo: 976 px.

| Bloco | Medida | Problema |
|---|---|---|
| Ficha "Avaliações por inscrição · Participantes desta Etapa" (`dl.ficha.curta`) | 446 px de largura, 78 de altura | dois números ocupam um bloco inteiro, com ~530 px vazios à direita; rótulo em caixa alta acima do valor |
| Indicadores de cobertura e de consolidação (`nav.filtros-da-mesa`, dois) | 1ª linha: 120, 166, 177, 177 px; 2ª: 174, 175, 124 px | cada um tem a largura do próprio texto; as colunas não se alinham entre as linhas (a segunda começa em x=152 numa e em x=206 na outra), e nenhuma das duas linhas chega à borda |
| "Quem está alocado" (`.tabela-rolavel.tabela-estreita`) | 608 de 976 px | a tabela termina antes do resto da tela, e a coluna do nome fica apertada para a marca "em dois lugares" |
| "Distribuir o que falta" (`fieldset` "Entre quem distribuir")¹ | 908 px, em duas colunas: os dois nomes começam em x=41 e x=490 | dois nomes separados por meia tela; com dez pessoas a grade funciona, com duas não |
| Filtros de "Inscrições, uma a uma"¹ | grade de 2 × 2, cada campo com 416 px | quatro campos curtos (cobertura, dia, banca, identificador) em duas linhas, onde caberiam numa |

¹ Medidos com a largura do próprio painel, e não a 1280 px; a proporção é a mesma.

O cartão "Agenda" (976 px) e os blocos de baixo (976 px) usam a largura inteira; a ficha e os
indicadores, não. É a mistura das duas regras que dá a impressão de desalinhamento.

## Por que a migração da `175` não corrigiu

1. **A `175` mudou as folhas comuns, e não as telas.** A decisão D-001 dela levou os padrões às três
   folhas comuns da gestão, de uma vez, em vez do roteiro "família por família" (a P2 do estudo de
   14/11). Tela que usa componente próprio ficou como era.
2. **A Distribuição usa componentes próprios.** Os indicadores dela são `nav.filtros-da-mesa` — links
   de filtro com número —, e não o componente de indicadores que a `175` passou a dividir a linha em
   partes iguais. A ficha é `dl.ficha.curta`; a tabela, `.tabela-estreita`.
3. **A conferência foi medida, e não olhada.** O instrumento compara o antes e o depois de 123 telas:
   pega rolagem lateral, quebra e conteúdo que sumiu, e não composição ruim que já existia antes.
4. **As pendências que cobrem estes casos estão abertas:** a P-1 (indicadores no celular), a P-2
  (fichas com o rótulo em caixa alta acima do valor) e a P-3 (larguras de coluna em `rem`). A
  validação com a equipe, prevista na `172`, também não aconteceu.

## Rascunho do que a tela poderia ser

Registrado como direção, e não como proposta fechada — as escolhas dependem de P-1 a P-3:

```text
Entrevista · Edital SIM20/2026
[Impedimentos] [Registrar ocorrência] [Resultados] [Trilha]

Agenda ─ publicada em 16/11 · Ver a agenda publicada
│ 1 conflito de horário: treino.avaliacao1, às 08:00 de 14/12 (Banca 01 e Banca 02).

1 avaliação por inscrição · 20 participantes                      ← a ficha vira uma linha

Cobertura   [ 20 todas ][ 13 sem nenhum ][ 13 sem o suficiente ][ 20 pendentes ]   ← 4 colunas iguais
Consolidação[  0 prontas ][ 20 ainda não ][  0 já consolidadas ][               ]   ← mesma grade

Quem está alocado                       (largura inteira, nome com espaço para a marca)
Distribuir o que falta                  (os nomes em grade compacta, e não nas pontas)
Inscrições: [Cobertura ▾] [Dia ▾] [Banca ▾] [Avaliador ____] [Filtrar]   ← numa linha
```

## O que decidir

1. Se os indicadores de filtro (`.filtros-da-mesa`, também na Mesa) passam ao padrão de indicadores
   da `175` — partes iguais —, e como ficam no celular (P-1).
2. Se a ficha de dois números vira uma linha de texto, ou "rótulo e valor" na mesma linha (P-2).
3. Se `.tabela-estreita` continua existindo, ou as tabelas da gestão ocupam a largura do conteúdo
   (P-3).
4. Se isso entra como a primeira tela de uma revisão família por família — a da avaliação: a
   Distribuição, a Mesa e a Alocação, que compartilham os componentes —, ou numa revisão das
   pendências da `175` para o sistema inteiro.

## Referências

- `interface/templates/interface/distribuicao.html` — a tela.
- `interface/static/interface/gestao/telas.css` e `componentes.css` — `.filtros-da-mesa`,
  `.ficha.curta`, `.tabela-estreita`.
- `specs/175-migracao-do-design-system/spec.md` — D-001 e as pendências P-1 a P-5.
- `specs/172-piloto-do-design-system/spec.md` — o piloto e a validação com a equipe.
