# Research — 065, conflitos de numeração

**Data:** 2026-10-08 · **Base:** `main` `fd18add4` · **Spec:** [spec.md](spec.md)

A spec não deixou marcação aberta: as três decisões de produto são `D-001` a `D-003`. Esta pesquisa
resolve as perguntas **técnicas** que a spec delegou ao plano, e continua a numeração local em
`D-004`. Cada decisão diz o que foi escolhido, por quê e o que foi descartado.

O ponto de partida foi lido no código, e não suposto:

- a numeração do documento é `pdf.numeracao(snapshot)` (`publicacoes/infrastructure/pdf.py`), a
  regra única da `054` (`FR-985`), já lida pela etapa Conteúdo (`interface/forms.py`), pela Revisão
  (`interface/revisao.py`) e pela Retificação (`interface/retificacao.py`);
- a validação (`editais/domain/validation.py`, 3.497 linhas) **nunca** importou o compositor; os
  dois avisos de texto livre que existem — `_anexo_citado_sem_rotulo` (RC-21) e
  `_caractere_sem_grafia` — são o molde;
- `_textos_impressos(snapshot)` já enumera, com caminho e descrição, todo texto livre que o
  documento imprime — é exatamente o alcance da `D-003`;
- `advertencias_do_ato` (`publicacoes/application/retificacoes.py`), que alimenta a confirmação da
  Retificação, **descarta todo achado cujo código seria impeditivo numa publicação**; o acervo sem
  quadro (`vacancy_table_absent_in_archive`) resolve isso com código próprio, e
  `test_os_codigos_novos_nao_coincidem_com_impeditivo_nenhum` prende a convenção;
- o achado de texto de seção chega à etapa Conteúdo por `CODIGOS_DO_TEXTO_DA_SECAO`
  (`interface/views.py`), hoje com âncora no topo da etapa (`#conteudo-titulo`); a legenda de cada
  seção já tem `id="titulo-<chave>"` (`compor_conteudo.html`).

---

## D-004 — Os itens do documento vêm do compositor, e não de uma regra nova na validação

**Decisão.** `pdf.py` ganha uma função pura, ao lado de `numeracao`, que devolve os itens que o
documento imprime como identificação (`FR-1205`): o número de cada seção materializada, o das
subseções geradas (cada Perfil, cada subseção comum de atribuições da `064`, cada Etapa) e quantas
tabelas o documento terá. Ela é escrita com as mesmas peças que a composição usa —
`_materializaveis`, `numeracao`, `grupos_de_atribuicoes` — e **não muda a composição**. A validação
a lê por importação adiada, dentro da função que confere, como já faz com
`classificacao.domain.faixa`.

Um **guardião** compõe o documento de verdade (os conteúdos congelados de A e de B da auditoria, e
casos sintéticos de um Perfil, sem quadro, sem modalidade, sem Etapa) e compara os títulos de
subseção e as legendas "Tabela N" colhidos da composição com o que a função diz. Se alguém mudar a
composição sem mudar a função, ele reprova.

**Por quê.** A `054` existe para que a numeração tenha uma regra só. A contagem de tabelas depende da
composição (a tabela de Perfis só existe com mais de um Perfil; quadro e modalidades por Perfil; o
Cronograma), e escrevê-la de novo na validação seria a segunda regra.

**Descartadas.** (a) Mover a numeração para o domínio e fazer o compositor importá-la: mexe na
composição, que precisa sair com os mesmos bytes (`FR-1219`), por uma pureza de camadas que nenhum
teste do projeto cobra. (b) Colher os itens compondo o documento a cada validação: o texto composto
já vem quebrado em linhas, e distinguir começo de parágrafo de linha que começa por número
("8.112/1990" depois de uma quebra) é frágil — serve ao guardião, não à regra.

## D-005 — O reconhecimento é um módulo puro; a validação só orquestra e escreve a mensagem

**Decisão.** `editais/domain/numeracao_digitada.py`, sem banco e sem Django, com: a leitura do
número de subitem no começo de um parágrafo (`FR-1199`); a leitura do título transcrito
(`FR-1201`); a leitura das remissões de um texto (`FR-1204`). Em `validation.py`, duas funções —
uma para a numeração das seções textuais, outra para as remissões de todo texto impresso — chamam o
módulo, cruzam com os itens do documento e escrevem os achados.

**Por quê.** `validation.py` tem 3.497 linhas; a parte que mais precisa de teste — a lista de formas
legítimas — é a que menos depende de contexto, e merece um conjunto de prova próprio.

**Descartada.** Tudo em `validation.py`, como o RC-21: o RC-21 tem uma expressão; esta feature tem
três gramáticas e uma lista de exclusões.

## D-006 — Os códigos, e o da Retificação é outro

| Código | Severidade | Ato | Requisito |
|---|---|---|---|
| `typed_numbering_conflict` | impeditivo | publicação (inclui submissão) | `FR-1200`, `FR-1210`, `D-001` |
| `typed_numbering_conflict_in_retification` | aviso | Retificação | `FR-1213`, `D-002` |
| `typed_numbering_suspected_title` | aviso | os dois | `FR-1201`, `FR-1211` |
| `cross_reference_ambiguous` | aviso | os dois | `FR-1206`, `FR-1211` |
| `cross_reference_without_target` | aviso | os dois | `FR-1207`, `FR-1211` |
| `cross_reference_suspected` | aviso | os dois | `FR-1208`, `FR-1211` |

**Por quê o código próprio na Retificação.** `advertencias_do_ato` subtrai da lista mostrada na
confirmação da Retificação todo código que seria impeditivo numa publicação. Com o mesmo código, o
aviso de `D-002` sumiria da tela em silêncio — e a decisão diz que ele é a única proteção. É a
solução que o acervo sem quadro já usa.

**Descartada.** Mudar a subtração de `advertencias_do_ato`: o comportamento é prendido por testes da
`027` e da `028`, e alterá-lo mudaria o que a confirmação mostra para outros achados.

## D-007 — Um achado por seção, na ordem do documento

**Decisão.** Os parágrafos em conflito de uma seção formam **um** achado (`FR-1215`), com caminho
`/sections/id=<uuid>/content`. As duas conferências percorrem as seções na ordem do documento, e a
de remissões emite os achados de cada seção logo depois dos de numeração dela; as remissões em
outros campos (Perfis, documentos, Eventos) vêm depois, com o caminho do campo. A mesma remissão na
mesma seção ou no mesmo campo sai uma vez.

**Por quê.** É o que `UX-161` pede, e o cenário B mostra o tamanho: 15 parágrafos seriam 15 linhas
na Revisão; agrupados, são 5.

## D-008 — O link leva ao campo da seção

**Decisão.** Os códigos novos de seção entram em `CODIGOS_DO_TEXTO_DA_SECAO`, e a montagem das
pendências — que já tem o snapshot — troca a âncora do topo da etapa pela da legenda da seção
(`#titulo-<chave>`), lendo a chave pelo identificador da seção no caminho. Os códigos que já existem
(`attachment_cited_without_label`, `section_universal_empty`, o caractere sem grafia) continuam como
estão: trocar o destino deles é melhoria fora do escopo e mudaria testes de outras features. Fica
registrado como possível continuação.

**Por quê.** `UX-160` e o cenário 2 da User Story 1: a pessoa chega ao campo, cuja legenda mostra o
mesmo número que o achado nomeia.

## D-009 — Parágrafo, normalização e trecho

**Decisão.** O texto é normalizado por `grafia.normalizar` e dividido por `pdf._paragrafos`, na mesma
ordem em que o compositor faz (`_grafado` antes de compor). O ordinal do parágrafo é o desta divisão.
O trecho do achado é o começo do parágrafo normalizado, até oitenta caracteres, cortado em fim de
palavra e terminado por reticências quando cortado.

**Por quê.** É o que o documento imprime: o espaço de largura zero colado do Word depois do número
("4.1​") some na normalização, e não pode gerar conflito (*Edge Cases* da spec).

**Limite.** Num parágrafo com caractere invisível no meio das primeiras palavras, o trecho
normalizado pode não ser achado pela busca do navegador no campo, que guarda o texto cru. Os
cenários da auditoria não têm esse caso; fica nas limitações.

## D-010 — As formas reconhecidas, uma a uma

**Número de subitem** (`FR-1199`), depois de retirados espaços e marcadores ("•", "-", "–", "—",
"*") do começo do parágrafo: de dois a quatro grupos de um ou dois algarismos separados por ponto,
seguidos de um destes — espaço; ponto ou parêntese de fechamento e espaço; ponto ou parêntese no fim
do parágrafo; espaço, travessão ou hífen e espaço; o fim do parágrafo. Não é número de subitem se o
que vem logo depois for algarismo, barra, vírgula, dois-pontos, "%", "º" ou "ª" — o que já exclui
datas, números de lei, valores, CEP e números de processo, porque nenhum deles cabe em grupos de dois
algarismos —, nem se a primeira palavra depois do número estiver na lista de unidades (pontos,
ponto, pts, horas, hora, h, minutos, min, dias, dia, semanas, meses, mês, anos, ano). O primeiro
grupo é comparado como inteiro ("04.1" é da seção 4).

**Título transcrito** (`FR-1201`): um grupo de um ou dois algarismos, ponto ou hífen, espaço, e o
resto do parágrafo com ao menos três letras, todas maiúsculas.

**Remissão** (`FR-1204`): "item", "itens", "subitem" ou "subitens", em qualquer caixa, seguidos de
um número de subitem (ou de um grupo só, para o nível de seção), e de mais números ligados por
vírgula, "e", "ou" ou "a" (o "a" marca intervalo: confere-se as duas pontas). "Tabela N" e "Quadro
N", com N de até três algarismos. A remissão **não é deste documento** quando, logo depois do último
número — no máximo oito palavras adiante, sem atravessar ponto final —, o texto diz "do Edital nº",
"da Resolução", "da Portaria", "da Lei", "do Decreto", "do art.", "do artigo", "da Instrução
Normativa", "do Anexo" ou "da Nota Técnica". "Deste Edital" e "do Edital" sem número continuam
remissão interna: o 28/2026 escreve "item 5.4 do edital" para citar a si mesmo.

**Por quê.** Calibrado na amostra (nove Editais): 77 remissões "item/itens/subitem N" e 15 "Quadro
N"; datas, ordinais, horas e números de lei quebrados no começo da linha são as formas numéricas mais
frequentes que não são subitem; e o espaço invisível depois do número aparece 71 vezes.

**Erro aceito.** A unidade depois do número exclui também um subitem legítimo que comece por uma
dessas palavras ("6.1 Horas complementares…"): o erro fica do lado de não acusar, e não do de
impedir a submissão sem razão.

## D-011 — Os itens do documento e a remissão

Uma remissão a número de subitem é cruzada com a lista de itens: as subseções geradas (`D-004`) e os
números de subitem lidos no começo dos parágrafos das seções textuais — os coerentes **e** os em
conflito, porque os dois saem impressos. Dois ou mais itens com o número: ambígua (`FR-1206`), e o
achado nomeia cada um ("a Etapa «…»", "o Perfil «CÓDIGO — nome»", "a subseção comum de atribuições",
"o parágrafo N da seção «…»"). Nenhum: sem destino (`FR-1207`). Um só, e ele é um parágrafo em
conflito: suspeita (`FR-1208`). Um só, e ele não está em conflito: **nada** (`FR-1209`). Remissão a
um grupo só ("item 5"): só se o número passar do total de seções numeradas. "Tabela N": só se N
passar do total de tabelas. "Quadro N": sempre suspeita.

## D-012 — A Retificação usa o caminho que já existe

As duas chamadas de `validate_for_publication` com `ato=ATO_DE_RETIFICACAO` — a que recusa
(`_assert_well_formed`, que só olha impeditivos) e a que aconselha (`advertencias_do_ato`, que
alimenta a confirmação) — passam a receber os achados desta feature, todos como aviso. Com
`D-006`, nenhum é subtraído. Nenhuma tela nova.

## D-013 — O Edital publicado não é conferido, por construção

A página do Edital fora da elaboração lê `fatos_do_conteudo_publicado`, e não a validação inteira
(`046`, `FR-755`). Nenhuma das conferências novas entra lá. Um teste prende: Edital publicado com
conflito, página sem achado de numeração (`FR-1218`, User Story 4).

## D-014 — O documento não muda

Nenhuma linha da composição muda. A fixture de bytes do contrato do documento publicado não é
refeita, e os conteúdos congelados da auditoria (`doc/auditoria-edital-pdf-2026-10-08/snapshots/`)
produzem, com o código novo, os bytes de `pdf/A-publicado.pdf` e do documento B gravado (`FR-1219`,
`SC-466`).

## D-015 — Nenhuma consulta nova

As conferências são funções do snapshot, que a Revisão, a submissão e a publicação já montam. Os
testes de orçamento de consulta da Revisão e da etapa Conteúdo não podem mudar de contagem.

## D-016 — O resumo das repetidas

Na Revisão, `agrupar_repetidas` dobra avisos repetidos numa linha que se abre. As remissões entram
nele como as remissões a anexo já entram ("{n} remissões a conferir"); o conflito de numeração, que
é impeditivo, nunca se dobra — é a regra do próprio filtro.
