# Research: Polish — os resíduos dos três lotes

As decisões desta feature. As dez que o prompt trouxe fechadas são **entrada**: entram como
recebidas, e não como perguntas a reabrir. As que esta sessão tomou nascem em `D-001`.

## Decisões recebidas (do prompt)

| | Decisão | Critério |
|---|---|---|
| 1ª | Escopo: R1 a R9, e nada mais. Ficam fora, aceitos: a marca de CPF, o cartão de Evento, o glossário, os textos que gravam ato, a ação cheia com contador zero | Está na lista? Entra. Não está? É registro |
| 2ª | Nenhuma ação acrescentada nem removida, nenhuma permissão mudada, nada muda no que se grava. Valem a prova da `057` (ações por papel) e a da `056` (POST por etapa); a exceção é a do R6 | Diff vazio nas duas provas, nas telas tocadas |
| 3ª | R1: os atos do Processo seguem a regra do Edital — irreversíveis e interrupções contornados, à parte, por último, com "IRREVERSÍVEL"; `hierarquia()` se couber, senão a mesma regra de classe | Nenhum botão cheio entre os atos do Processo Ativo do seed |
| 4ª | R2: abaixo de 60 rem, a tabela de cada Processo da Lista numa moldura com rolagem horizontal; não empilhar; a Condução ganha a mesma moldura | A 375 px, documento com 375 na Lista e na Condução; todo botão da Lista alcançável na moldura |
| 5ª | R3: tirar `class="resumo"` da `section` da Matrículas | Título e nota empilhados |
| 6ª | R4: `class="tabela"` nos Resultados; só a célula numérica leva `numero` | Números à direita; nenhum texto à direita |
| 7ª | R5: os plurais com parênteses das telas listadas passam ao filtro `plural`, conferido antes se o texto grava; `compor_base.html` entra com o teste reescrito | Nenhum "(s)" nas telas tocadas, salvo os registrados |
| 8ª | R6: Peso, Nota mínima e Pontuação máxima sem zeros, só se o rascunho gravado continuar idêntico | Os dois juntos, ou nenhum |
| 9ª | R7: coluna de rótulos da Revisão com a mesma largura, fixa em rem. R8: o motivo da Ocupação e do Sorteio como o da Ordenação e do Corte | Valores no mesmo x; o mesmo controle e largura nas quatro telas |
| 10ª | R9: a decisão 003 da `056` passa a dizer 60 rem; o PR 246 não se edita; o total da suíte vai na `verificacao.md` desta spec | Nenhuma divergência entre o `research.md` da `056` e a folha |

---

## D-001 — Os atos do Processo se repartem pelo que cada um declara, e não por `hierarquia()`

**Decisão**: o template de `processo_detalhe.html` desenha os atos em dois grupos, pelo atributo
que o próprio ato já declara: os que **não** são irreversíveis (hoje, só "Ativar Processo") numa
`ul.lista-acoes.em-linha`, todos `botao secundario`; os irreversíveis (Encerrar e Cancelar) depois,
numa `ul.lista-acoes.em-linha.terminais`, com o desenho contornado da `057` e o marcador
"irreversível". Nenhum ato do Processo é preenchido. "Elaborar o Edital", que fica acima dos atos,
continua sendo a ação cheia do cartão quando existe — ela não é ato do Processo.

**Rationale**: `hierarquia()` reparte `Acao` do Edital e escolhe uma **principal** por uma
preferência que não tem membro entre os atos do Processo (`elaborar`, `submeter`… são do Edital).
Usá-la exigiria passar a repartição pelo contexto da view — e a feature não mexe em view — para
ganhar, de útil, só a separação das terminais, que `ato.irreversivel` já dá. A 3ª decisão prevê
exatamente isto: "se não couber, a mesma regra de classe sem forçar o helper".

**Alternativas**: chamar `hierarquia(atos)` por *duck typing* — funciona porque `AtoProcesso` tem
`chave`, mas amarra o Processo a uma constante (`TERMINAIS`) documentada como "do Edital" e pede a
view; separar por `ato.interrupcao` — deixaria Encerrar, irreversível, entre os comuns.

## D-002 — As regras das terminais vão para um parcial de estilo, incluído pelas duas telas

**Decisão**: `.lista-acoes.em-linha`, o filete `.lista-acoes+.terminais` e o contorno
`.terminais .botao` (com o `:hover`) saem do bloco de estilo de `detalhe.html` para
`_estilo_das_terminais.html`, incluído no `estilo_da_pagina` do Detalhe do Edital e do Processo.
`.colunas.ao-topo` fica no Detalhe, que é a única tela que a usa.

**Rationale**: a decisão 024 da `057` mandou as regras de uma tela só para o estilo dela, e o teste
`test_o_detalhe_desenha_as_terminais_por_ultimo_e_so_contornadas` prende que elas **não** estão na
folha comum. Com duas telas, o padrão da casa é o parcial incluído pelas duas — é o que a `044` fez
com `_estilo_da_lista_exigida.html` e a `052` com `_estilo_da_vista.html` —, e `_estilo_proprio`,
que o teste usa, resolve o `include`. Uma cópia por tela divergiria.

**Alternativas**: subir as regras para a folha comum — reverte aquela decisão, viaja em toda página
(inclusive na de distribuição) e reprova o teste da `057`; copiar as regras no Processo — duas
fontes.

## D-003 — A moldura é uma classe nova na mesma regra da Alocação

**Decisão**: a tabela da Lista (uma por Processo) e a de "Recortes deste marco" ficam dentro de
`div.rolavel-no-estreito`. A classe entra **na mesma** `@media (max-width:60rem)` que já põe
`overflow-x:auto` na `.distribuicao-moldura`, como mais um seletor da regra. Acima de 60 rem não há
regra: a moldura é um bloco comum, sem rolagem — e não pode ser contêiner de rolagem em tela larga
pela razão que o comentário da Alocação dá (o `sticky` passaria a valer contra ela).

**Rationale**: é a solução da Alocação, literalmente: o mesmo limiar, a mesma declaração, a mesma
regra. O cartão `article.processo` continua com `overflow:hidden` (é o que recorta o fundo nos
cantos arredondados); quem rola é a moldura, dentro dele.

**Alternativas**: reusar `.tabela-rolavel` — rola em qualquer largura, e a 4ª decisão limita a
rolagem da Lista a abaixo de 60 rem; reusar `.distribuicao-moldura` na Lista — o nome mentiria;
tirar o `overflow:hidden` do cartão e deixá-lo rolar — o cabeçalho do Processo rolaria junto com a
tabela; empilhar as células — a 4ª decisão o proíbe.

## D-004 — Cada plural conferido: nenhum dos listados grava

**Decisão**: os seis lugares listados pela 7ª decisão são texto que o template compõe para a tela,
e nenhum vai para ato, registro ou documento:

| Onde | Texto | Para onde vai |
|---|---|---|
| `distribuicao.html` | "N consolidada(s), M recusada(s)" | resumo da consolidação em lote, só na tela |
| `matriculas.html` (2) | "N linha(s)" | nota e marcador da prévia, só na tela; o registro da prévia é composto em `views.py` e fica |
| `recurso.html` (2) | "N ato(s) de instrução", "N ato(s)" | meta e ajuda do recurso, só na tela |
| `ocupacao.html` l. 117 | "Reversão de cota: N vaga(s) da lista reservada…" | leitura do movimento já gravado |
| `ocupacao_historico.html` l. 71 | "Reversão de cota: N vaga(s) — …" | idem, no histórico |
| `compor_base.html` l. 70 | "as N vaga(s) imediata(s) do Perfil" | aviso de rederivação, só na tela |

Os seis passam a `plural` ou `contagem` (o filtro da decisão 025 da `057`). O artigo de
`compor_base.html` acompanha ("a 1 vaga imediata", "as 80 vagas imediatas"). Fora da lista e fora
do lote: `compor_perfis.html` ("N linha(s) em LP01"), não nomeado pela 7ª decisão, e o
`reason` da prévia de exportação em `views.py`, que **grava**.

**Testes reescritos para a grafia nova, sem mudar o que verificam**: `test_compor_quadro.py` (a
7ª decisão o nomeia), `test_consolidar_todas_as_prontas.py` (duas asserções) e
`test_resultado_da_etapa.py` (uma). O texto é o próprio item, como na decisão 019 da `057`.

## D-005 — O valor exibido das Etapas sai de `etapas_do_edital`, e a prova é o banco

**Decisão**: `forms.etapas_do_edital` passa a escrever Peso, Nota mínima e Pontuação máxima sem
zeros à direita, com ponto decimal (`2`, `6`, `87.5`) — é o que o atributo `value` de um campo
numérico exige, e o navegador o mostra na grafia do lugar ("87,5"). A reexibição depois de recusa
(`_reexibir_etapas`) já devolve o que a pessoa digitou, e fica.

**A prova**: o que "Salvar rascunho" grava é a linha de cada `EtapaAvaliacao` (coluna decimal de
quatro casas) e o registro `ALTERAR_RASCUNHO` da auditoria, cujo motivo é a área ("etapas"), e não
o valor. Mede-se no mesmo banco: salvar com o formulário de antes, ler as linhas e o registro; salvar
com o de depois, ler de novo; comparar campo a campo, fora o identificador e o instante do registro
e a revisão do Edital, que avança a cada gravação.

**Alternativas**: um filtro de template — o valor já chega pronto para o campo, e a 1ª exceção da
feature (mexer em `forms`) foi prevista para isto; `pontuacao` — escreve vírgula, que o campo
numérico recusa.

## D-006 — A coluna de rótulos da Revisão: largura fixa, com piso para tela estreita

**Decisão**: `grid-template-columns` dos pares da Revisão passa de `fit-content(16rem) 1fr` para
uma largura fixa em rem, limitada a uma fração da linha em tela estreita
(`min(<N>rem, 40%) 1fr`). `N` é o menor valor que põe numa linha os rótulos comuns da Revisão do
76/2027, medido antes ([verificacao.md](verificacao.md)); o rótulo mais longo quebra dentro dela,
como já quebrava.

**Rationale**: `fit-content` dá a cada `dl` a largura do seu rótulo mais longo — é o que separa os
x. Com o mesmo valor em toda `dl` da página, e todas na mesma largura de cartão, os valores
começam no mesmo x. O `min(…, 40%)` só age abaixo de ~`N/0,4` rem de linha, e impede que, a 375 px,
a coluna de rótulos tome o cartão.

**Alternativas**: `subgrid` sobre a lista — as `dl` estão em `li` diferentes, sem grade comum;
manter `fit-content` com o mesmo teto — é o que já está.

## D-007 — O motivo de sucessão vira `p.campo` com área de texto, como na Ordenação

**Decisão**: na Ocupação, o rótulo, o campo e a ajuda de "Motivo da nova apuração" passam para
dentro de um `p.campo`, com `textarea rows="3"`; a ajuda, que era `p.ajuda`, vira `span.ajuda`
(não há `p` dentro de `p`), com o mesmo `id` e o mesmo texto. No Sorteio, o `input` de "Motivo da
sucessão", que já está num `p.campo`, vira `textarea rows="3"`. O `name`, o `id`, o `required`, o
`aria-required` e o `aria-describedby` ficam. A largura vem de `.campo>textarea`
(`max-width:var(--leitura)`), a mesma regra que dá a do motivo da Ordenação e do Corte.

**Rationale**: é o controle e a regra que já existem nas duas telas vizinhas; nada novo na folha.

## D-008 — O motivo da anulação do Sorteio fica

**Decisão**: "Motivo da anulação" continua campo de uma linha. A 9ª decisão fala do motivo **de
sucessão**, e a reavaliação, do "motivo que sucede um ato"; a anulação desfaz o sorteio e constitui
o sucessor num gesto próprio, com outros dois campos, e não tem par na Ordenação nem no Corte.

**Alternativas**: trocá-lo também — seria item novo, fora da lista (1ª decisão).

## D-009 — Os Resultados: `numero` só na nota

**Decisão**: a tabela de `resultados.html` ganha `class="tabela"`, e a célula de resultado só leva
`numero` quando a forma é pontuada. O rótulo da decisória e "não avaliada" ficam à esquerda. O
cabeçalho da coluna fica como está: ele encabeça células de número e de texto.

**Alternativas**: `numero` na célula toda — punha "favorável" à direita sozinho, o que a 6ª decisão
proíbe.

## D-010 — As duas provas, medidas como nos lotes anteriores

**Decisão**: a lista de destinos por papel segue a decisão 017 da `057` — `href` de todo link do `main`,
`action` de todo formulário, `formaction` e `name=value` de todo botão de envio, ordenada e sem
repetição —, com `ana.gestora` e `joana.avaliadora`, nas telas tocadas. É lida no HTML que o
servidor devolve, por um script no `manage.py shell` com o cliente de teste do Django sobre o banco
da medição: o conjunto é o mesmo que o JavaScript da `057` lia no DOM, e assim as duas medições
saem do mesmo código. O envio de "Salvar rascunho" segue as decisões 005 e 015 da `056`: pares de
chave e valor, sem o token de CSRF, com o `ruleId` mascarado — lido pelo `FormData` na página.

---

## Decisões tomadas na implementação

## D-011 — A chave de idempotência é mascarada na prova de destinos

**Achado na medição.** A primeira recaptura, depois do R1, acusou cinco diferenças, todas no valor do
botão `chave_idempotencia` — que nasce nova a cada render, com ou sem a feature. É o mesmo caso do
`ruleId` da decisão 015 da `056`.

**Decisão.** `capturas/acoes.py` troca o valor de todo botão cujo nome contém "chave" por
`<chave>`, e a mesma troca foi aplicada ao `acoes-antes.json` já gravado — é uma transformação do
arquivo, e não uma nova medição. O nome do botão continua na prova.

## D-012 — Na Revisão, duas posições, e não uma: a caixa dos irreversíveis tem recuo próprio

**Medido.** Com a coluna em 16 rem, os 26 blocos da conferência começam o valor em x = 313, e os 3
da caixa "o que não se corrige depois de publicado", em x = 335. A diferença (22 px) é da caixa,
não da coluna: borda esquerda de 4 px (contra 1 px do cartão) e recuo de 1,2 rem da lista dela.
Antes eram **nove** posições.

**Decisão.** A meta "mesmo x em todos os blocos" é atingida dentro de cada caixa e fica **parcial**
entre as duas. Igualar exigiria mexer no recuo da caixa de irreversíveis, que é outro desenho e não
está na lista (1ª decisão), ou compensar 22 px na coluna dela, que esconderia a causa num número
mágico. O valor alcançado e a justificativa estão na [verificação](verificacao.md).

## D-013 — Na Ocupação, o formulário da nova apuração deixa de ser fileira

**Achado na medição.** Com o motivo em `p.campo`, a fileira do `form.acoes` punha o campo e o botão
lado a lado e esticava o botão à altura da área de texto (138 px).

**Decisão.** `acoes` fica só no formulário de um botão (o recorte ainda não apurado), e o da nova
apuração passa a ter o desenho do Corte: o campo e, abaixo, o botão em `p.acoes`. Nenhum campo,
destino ou rótulo muda — a prova de destinos e o teste da Ocupação continuam iguais.

**Alternativas**: uma regra nova para o campo ocupar a linha da fileira — padrão novo, que a 1ª
decisão exclui; tirar `acoes` também do formulário de um botão — mudaria uma tela fora do item.

## D-014 — Duas asserções prendiam o valor que o item muda, e foram reescritas

**Achado na suíte.** `test_etapa_declara_avaliacoes.py::test_o_formulario_exibe_o_que_esta_gravado`
esperava `"50.0000"` de `etapas_do_edital`, e `test_polish_da_056.py::test_a_revisao_poe_os_rotulos_numa_coluna`
esperava `fit-content(16rem)` na Revisão. São exatamente o valor exibido do R6 e a regra do R7.

**Decisão.** As duas passam a esperar o valor novo (`"50"`; `min(16rem,40%)`), e o que verificam
continua o mesmo: o formulário exibe o número gravado; a Revisão põe os rótulos numa coluna com teto
de 16 rem. É o caso da decisão 019 da `057`: a condição de parada sobre "teste que exige mudar
comportamento" é sobre o que está **fora** do item, e aqui o valor é o próprio item.

## D-015 — As correções da revisão de código

A revisão do diff apontou sete pontos, todos corrigidos antes do PR:

- **a ordem dos grupos do Processo** deixa de depender da ordem de `ATOS`: o `regroup` passa a
  agrupar `atos|dictsort:"irreversivel"`, e um ato reversível declarado depois de Cancelar não
  desfaz mais a regra de "terminais por último";
- **Encerrar Processo** leva `botao secundario`, como o Encerrar do Edital: contornado pelo grupo, e
  discreto mesmo se a página perder o parcial — com `botao` puro voltaria a verde cheio;
- **a máscara da prova de destinos** vale só para `chave_idempotencia`, e não para todo botão com
  "chave" no nome (o arquivo "antes" já só tinha esse);
- **`_no_campo`** é o único lugar da normalização decimal em `forms.py`: substitui o `percentual`
  local de `_o_que_o_cartao_mostra`, que fazia a mesma coisa;
- **a Ocupação** tem dois formulários, um por estado, e não um com a classe condicional;
- **o teste da moldura** acha o bloco de 60 rem pela regra que procura, e não pela posição na folha;
- **a moldura da Condução** é focável e nomeada (`tabindex="0"`, `role="region"`,
  `aria-labelledby` do título): há células sem link, e sem foco quem usa só o teclado não rolaria
  até elas. A da Lista fica sem, porque toda célula fora da tela tem link ou botão, e o foco neles
  já rola a moldura.

As provas foram refeitas depois das correções: destinos idênticos, e os valores das Etapas os mesmos.
