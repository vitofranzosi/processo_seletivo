# Relatório do Edital — modernização da diagramação (24/10/2026)

**Pedido**: levar o PDF da `099` à organização da maquete v2, com o compositor de blocos da `100`,
sem mudar regra de domínio, sem migration e sem dependência nova. Requisitos na spec da `099`:
FR-2536 revista, FR-2601 a FR-2607, SC-947 e a decisão D-009.

**Arquivos desta pasta**

- [`relatorio-61-2026-emitido-pelo-sistema.pdf`](relatorio-61-2026-emitido-pelo-sistema.pdf) — o
  Edital 61/2026 do banco da maquete (`ps_maquete_v2`), emitido pela view da gestão (`POST`,
  emissão nº 7, registrada na trilha) como em produção — host institucional, requisição HTTPS —:
  os links abrem a seleção e os resultados em `https://`.
- [`relatorio-61-2026-emitido-em-localhost.pdf`](relatorio-61-2026-emitido-em-localhost.pdf) — a
  mesma emissão feita de `localhost` (emissão nº 6): sem endereço nem link, e a frase que diz por quê.
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

## Homologação (24/10/2026)

A concepção visual foi aprovada; três verificações pontuais, sem reformulação do motor nem do
layout. O PDF desta pasta é o da emissão nº 7, já com as três.

### 1. Cronograma: o resultado publicado aparecia com traço

**Causa.** O evento do cronograma do Edital é texto livre ("Resultado preliminar"), sem ligação
estrutural com o marco nem com a publicação. A coluna "Registrado no GPS" sabia ligar só o período
de inscrições (pelos envios) e as etapas (pelo `scheduleEventId`); para os eventos de resultado
caía em "—", enquanto a linha do tempo, que lê as publicações direto, mostrava as duas datas.

**Correção.** O evento cujo nome é o rótulo que o domínio dá à natureza (`Natureza.PRELIMINAR`,
`Natureza.DEFINITIVA`; sem acento e sem caixa, com "resultado final" como sinônimo do definitivo)
recebe a publicação daquela natureza: "publicado em 25/09", ou "nenhuma publicação até a data dos
dados". A nota da seção diz que é a data da publicação, e não a da avaliação. Linha do tempo e
cronograma leem a mesma consulta — o relatório faz uma consulta a menos (118, constante nas
escalas 1 e 10). Evento de nome livre fora desse rótulo continua com "—", agora explicado.

### 2. Notas condicionais

Cada nota de tabela aparece só quando a tabela tem o caso (FR-2608): o traço de número omitido,
só com Perfil omitido; a soma entre perfis, só com mais de um; as listas que não se somam, só com
lista reservada; a legenda das datas, só com as naturezas presentes; a do cronograma, só com
"publicado" ou com traço na coluna; a das etapas, só se houver tabela de etapas.

### 3. Hyperlinks oficiais em produção

**Como a URL se forma.** `request.build_absolute_uri(reverse(...))`: o esquema é o de
`request.is_secure()` e o host é o `Host` validado por `ALLOWED_HOSTS`. Na topologia de
[`implantacao-em-producao-ubuntu.md`](../../implantacao-em-producao-ubuntu.md), o nginx repassa
`Host $host` e `X-Forwarded-Proto $scheme`, o Django confia no cabeçalho
(`DJANGO_TRUST_PROXY_SSL_HEADER=true`, obrigatória ali), `ALLOWED_HOSTS` é o domínio institucional e
o host desconhecido é recusado pelo nginx. Logo, o link sai `https://<domínio>/selecoes/<edital>/`
e `https://<domínio>/selecoes/resultados/<publicação>/`.

**Provado por teste** (`test_emissao_em_producao_aponta_https_canonico_para_cada_documento`): a
emissão com a requisição de produção traz só links HTTPS no domínio; o primeiro resolve para a
página da seleção daquele Edital; cada um dos outros resolve para a publicação cujo título está na
mesma linha da tabela, e a página pública abre sem sessão e nomeia o Perfil do título.
`localhost`, `127.0.0.1`, `::1`, `*.localhost` e `testserver` continuam sem endereço.

**O que fica para decisão** (não feito, por extrapolar o escopo). O endereço segue o host pelo qual
a gestão foi acessada. Se a operação um dia puser um segundo nome em `ALLOWED_HOSTS` — um nome
interno para a gestão, por exemplo —, o PDF emitido por ele levaria esse nome. A alternativa
recomendada é um endereço público canônico configurado (uma variável de ambiente única), usado pelo
relatório do Edital, pelo consolidado **e** pelos avisos aos candidatos (`066`), que montam o
endereço do mesmo jeito; mudar só o relatório deixaria os avisos divergentes.

### Regressão

Suíte inteira contra PostgreSQL depois das três correções — números, regras, permissões,
privacidade e auditoria da `099` e da `100` incluídos. Os bytes do consolidado da `100` nos
conjuntos de 1, 5, 12 e 60 Editais continuam os mesmos: nenhuma das três correções toca o
documento dele.

## Polish da página da gestão (25/10/2026)

Melhoria de apresentação da página que consulta e emite o relatório, sem mudar regra, número,
permissão, auditoria nem o PDF. Comparação em
[`pagina-antes-e-depois.pdf`](pagina-antes-e-depois.pdf): 1280 px (duas partes), 768 px e 375 px.

**Diagnóstico.**
- Cabeçalho em quatro blocos de texto seguidos; a espécie era um parágrafo em negrito.
- Situação no GPS e providências tinham o mesmo peso, e a pendência não se distinguia.
- O botão dizia "Baixar PDF", mas cada clique é uma emissão nova, numerada e registrada na trilha.
  Um segundo clique, de quem achou que o primeiro não pegou, era outra emissão.
- Os seis números caíam em 4 + 2, com rótulo e base em corpo pequeno e em minúscula.
- As seções seguintes à tabela de perfis não tinham espaço acima do título.
- As datas mostravam a natureza crua ("registrado"), diferente do PDF.

**O que mudou.**
- **Cabeçalho**: o título manda. A espécie virou selo neutro, com a frase dela ao lado. A natureza
  gerencial ficou em nota.
- **Painel**: situação no GPS, providências e data dos dados ficam numa superfície branca, e a
  emissão vem em seguida, separada por um fio. A providência em curso tem a marca "Em curso" em
  texto e o fio âmbar do que está em andamento; sem pendência, não há marca.
- **Emissão**: o botão agora é "Emitir e baixar PDF", e a frase ligada a ele
  (`aria-describedby`) diz que a emissão fica registrada na trilha. O script
  `relatorio-do-edital.js` cancela o segundo envio enquanto o primeiro está a caminho e diz
  "Emitindo…" numa região `role="status"`. Depois de 6 s, o botão volta com a frase do que fazer se
  o download não veio. O navegador não avisa a página quando um anexo termina de baixar; por isso
  é um prazo. A recusa do servidor troca a página, como antes.
- **Visão geral**: medida de leitura do GPS (`--leitura`, 68ch) e entrelinha 1,65. O texto é o
  mesmo.
- **Números**: são os cartões do PDF (`relatorio_pdf.cartoes`), com o mesmo valor, o mesmo "de N" e
  o traço com o motivo na ausência. Ficam em três colunas, duas abaixo de 46rem e uma abaixo de
  28rem, por *container query*: a largura que conta é a da área do relatório, e não a da janela,
  porque a barra lateral muda o espaço.
- **Seções** com espaço próprio. As datas usam os rótulos e a legenda do PDF. A nota da soma entre
  perfis só aparece com mais de um perfil.

**Reaproveitado.** Os tokens de `shared/tokens.css` (`--leitura`, `--borda`, `--branco`,
`--verde`, `--verde-claro`, `--amarelo`, `--amarelo-fundo`), `.botao`, `.nota`, `.oculto`, o foco
global e a folha da tela, que já existia. Nenhuma biblioteca nova.

**Verificado no navegador.**
- Sem rolagem horizontal a 1280, 768 e 375 px.
- Seis cartões em 3 × 2, 2 × 3 e 1 × 6, sem conteúdo cortado; com o texto a 200%, uma coluna, e nada
  cortado.
- O foco por teclado chega ao botão com o contorno do GPS. Console sem erros.
- Dois cliques seguidos geraram **uma** emissão (a trilha foi de 7 para 8 no banco da maquete), e o
  botão voltou sem trocar de página.

**Limitações.**
- A página do relatório consolidado (`100`) tem o mesmo desenho antigo — mesmos cartões em 4 + 2,
  "Baixar PDF" — e continua assim. Ficou fora do escopo desta entrega.
- A mensagem de recusa por concorrência ("Baixe o relatório de novo") é compartilhada com a `100`,
  e não foi trocada pelo mesmo motivo.
- O prazo de 6 s não sabe se o download terminou. Se a rede for mais lenta que isso, um segundo
  clique depois do prazo é outra emissão, que é o comportamento correto: emitir de novo é
  permitido, e fica registrado.

