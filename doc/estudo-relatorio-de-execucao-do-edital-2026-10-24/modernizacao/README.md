# Relatório do Edital — modernização da diagramação (24/10/2026)

**Pedido**: levar o PDF da `099` à organização da maquete v2, com o compositor de blocos da `100`,
sem mudar regra de domínio, sem migration e sem dependência nova. Requisitos na spec da `099`:
FR-2536 revista, FR-2601 a FR-2607, SC-947 e a decisão D-009.

**Arquivos desta pasta**

- [`relatorio-61-2026-emitido-pelo-sistema.pdf`](relatorio-61-2026-emitido-pelo-sistema.pdf) — o
  Edital 61/2026 do banco da maquete (`ps_maquete_v2`), emitido pela view da gestão (`POST`,
  emissão nº 3, registrada na trilha) com host público: os links abrem a seleção e os resultados.
- [`relatorio-61-2026-emitido-em-localhost.pdf`](relatorio-61-2026-emitido-em-localhost.pdf) — a
  mesma emissão feita de `localhost` (emissão nº 4): sem endereço nem link, e a frase que diz por quê.
- [`comparacao-visual.pdf`](comparacao-visual.pdf) — maquete v2 × PDF anterior × PDF novo, página a
  página.
- Roteiro: [`../roteiro/emitir_pelo_sistema.py`](../roteiro/emitir_pelo_sistema.py).

## A. Diagnóstico

O PDF anterior era composto pelo escritor do Edital (`publicacoes/infrastructure/pdf.py`), um
paginador de texto corrido. Os números estavam certos; a forma era de outro documento.

| Aspecto | Maquete v2 | PDF anterior | Causa | Agora |
|---|---|---|---|---|
| Abertura | órgão compacto, título, espécie em azul, ficha 2 × 2 | brasão centralizado, título em caixa alta, pares empilhados | composição | a abertura da `100`: brasão de 30 pt, título de 16,5 pt, ficha de quatro pares |
| Indicadores | seis cartões, 3 × 2, na primeira página | tabela de três colunas | composição | seis cartões; ausência como "—" e o motivo |
| Pontos de atenção | faixa âmbar na primeira página | lista numerada partida entre as páginas 1 e 2 | composição | a faixa inteira na primeira página |
| Procura | barras por dia, término original tracejado, duas somas | tabela de quatro semanas | o escritor não desenha gráfico (FR-2536, redação antiga) | barras por dia; por semana quando os dias não cabem; término entre duas barras |
| Perfis | tabela larga | colunas estreitas, "Situação das vagas" em nove linhas | larguras iguais | larguras proporcionais ao conteúdo; o local abaixo do nome |
| Alterações | ao lado do gráfico | empilhadas | composição | lado a lado, ou em sequência quando não cabem |
| Datas | rótulo de natureza | natureza em texto | composição | rótulo por natureza, com "prazo em curso" |
| Documentos | página pública | endereços impressos por extenso | composição | tabela: a página pública com o endereço; resultados vigentes como links |
| Endereços | — | `http://localhost:8099/…` quando emitido localmente | ambiente | só com host público; emissão local diz que não há endereço |
| Paginação | quatro páginas | seis, com seções partidas | texto corrido | quatro, com a seção 2 e o anexo abrindo página |
| Acessibilidade | — | marcadores, sem estrutura | escritor | PDF marcado: títulos, listas, tabelas, figura com texto alternativo |

**O que vem dos dados, e não é defeito**: a maquete tem campos que a rodada 2 recusou ou mudou de
lugar — "Período" na ficha, "pessoas" e "candidatos por vaga", a prova objetiva entre as datas
principais (FR-2538 a deixa no cronograma do anexo, para não parecer que aconteceu na data). O texto
é o da derivação aprovada, e não o da maquete.

## B. Componentes compartilhados

Em `interface/diagramacao.py`, usados pelos dois documentos gerenciais:

- `abertura(...)` — órgão, título, subtítulo, natureza e ficha. A `100` passou a usá-la.
- `BarrasVerticais` — novo: série longa, barra por período, eixo com até cinco rótulos (a regra da
  Supervisão), pico escrito, marco tracejado, legenda por tom e texto alternativo com toda a série.
- `Nota` presa ao bloco anterior; cadeia título → subtítulo → tabela; tabela de até três linhas
  inteira e partes de duas linhas ao menos; parágrafo de até três linhas inteiro.
- `Ficha` mede o valor em negrito, como o desenha — o valor longo passava da margem.

Em `interface/relatorio_pdf.py`: `cartoes(indicadores, complementos)` e `PE`, que a `100` importa.

## C. O PDF emitido

Quatro páginas, como a maquete: o painel; resultados, procura × alterações, datas e documentos; o
anexo A–D; o anexo E–H. As emissões 3 e 4 do banco `ps_maquete_v2` estão na trilha.

## D. Comparação visual

[`comparacao-visual.pdf`](comparacao-visual.pdf). A organização é a da maquete; o espaçamento e as
quebras são do compositor, e não do navegador. A primeira página termina com espaço livre quando os
pontos de atenção são curtos: a seção 2 abre página por decisão (FR-2604), como na maquete.

## E. Testes e evidências

- `tests/unit/interface/test_diagramacao_do_relatorio_do_edital.py` — relatórios sintéticos em seis
  volumes (1 a 40 perfis, 10 a 400 dias, com e sem omissão): painel, grupos, títulos, notas,
  sobreposição, linha viúva, palavra partida, série diária e semanal, links, faixa de toda página,
  A4 marcado e determinismo, e as quatro regras de paginação — cada uma conferida falhando sem a
  regra.
- `tests/integration/relatorio/test_diagramacao.py` — seis cenários coerentes (encerrado com e sem
  pendência, cancelado, cancelado abaixo do limiar, aberto com Perfil pequeno, supressão
  complementar), a escala 10, e a emissão pela view em host local e em host público.
- Os testes de conteúdo da `099` passaram a ler o texto extraído do PDF, e não a composição.
- Inspeção a olho: as quatro páginas do PDF emitido, as 21 do volume sintético de 40 perfis e 400
  dias, e as cinco da emissão local com omissão.

## F. Impacto na `100`

- Os bytes do relatório consolidado ficaram **iguais** nos conjuntos de teste de 1, 5, 12 e 60
  Editais (SHA-256 conferido antes e depois de cada mudança no compositor).
- As regras novas de paginação valem para a `100` também: um conjunto que caísse no caso — nota
  sozinha no alto, tabela com uma linha numa parte, título com subtítulo no pé — passa a paginar
  melhor, e com bytes diferentes dos de antes.
- O defeito da `Ficha` era latente na `100`: um critério de conjunto longo passaria da margem.

## G. Limitações

- **A marcação continua a básica**, e não foi validada por PAC nem por leitor de tela real.
- **A página da gestão mantém a tabela por semana**; só o PDF ganhou o gráfico.
- **O gráfico ao lado das alterações passa a semanal a partir de 70 dias** de período (a barra
  ficaria mais estreita que 3,5 pt); em sequência, a partir de 144.
- **O endereço depende do host da requisição**: em produção atrás de proxy, o host público precisa
  chegar à aplicação (`ALLOWED_HOSTS` e o cabeçalho do proxy), senão a emissão sai sem links — o
  lado seguro da falha.
- **Este trabalho está empilhado sobre o PR da `100`** (#331), que ainda não foi mergeado: o
  compositor é dela. Os FR-2601 a FR-2607 e o SC-947 continuam a faixa global da `100`.
