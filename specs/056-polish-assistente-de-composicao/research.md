# Pesquisa — 056 · Polish do assistente de composição

As decisões desta feature, numeradas a partir de `D-001`. As nove que o prompt trouxe fechadas vêm
primeiro, como **entrada**, sem reaproveitar a numeração do prompt: citadas aqui como "1ª decisão
recebida" a "9ª decisão recebida".

## Decisões recebidas

| | O que decide | Critério |
|---|---|---|
| 1ª | Escopo: F1, F2, F3, F4, F5 e D4; F6 por último e dispensável; nada dos lotes 1 e 3 | Está na lista? Entra. Não está? Registro |
| 2ª | Nenhum campo sai, nenhum nome muda, nada muda no que se grava; trocar o controle é permitido | Envio de cada etapa idêntico nas chaves e nos valores |
| 3ª | Stepper numa linha a partir de 1280 px, com a situação em texto; abaixo, colunas iguais | ≤ 80 px; h2 de Perfis em y ≤ 440 |
| 4ª | Ações do cartão na linha da legenda; legenda com o identificador; nada de tabela editável | Nenhum cartão com linha só de ações; Evento ≤ 150 px |
| 5ª | Cronograma: Tipo, Descrição, Início, Término numa linha; "Onde acontece" embaixo; Descrição mais larga | Início e Término com o mesmo topo; Descrição > "Onde acontece" |
| 6ª | Conteúdo: cartão em `--leitura`; vazia com 2 ou 3 linhas; gerada numa faixa; marca curta mas visível | Página ≤ 3.000 px |
| 7ª | Revisão em `dl` de grade já existente, sem mudar conteúdo, ordem, número ou data | Rótulos numa coluna; altura ≤ +10% |
| 8ª | Texto longo em área de texto de 2 linhas (cinco campos); Anexos com as larguras das outras etapas | Sem corte; "Avançar" na mesma posição |
| 9ª | Ordem do Perfil no Retificar igual à do Compor, se sem risco | Ordem igual, ou registro |

---

## D-001 — A medida de partida

**Medido** em 30/09/2026 sobre `a7ade983`, banco `ps_056_polish` (cópia de `ps_polish_audit`), a
1280 × 900, antes de qualquer template ou folha mudar. Os números estão no
[verificacao.md](verificacao.md). Três diferem da tabela da auditoria, e a diferença é do banco e do
commit, não de método: o Conteúdo tem 4.876 px (a auditoria mediu 4.790), a Revisão 7.992 (7.987) e
o cartão de Evento 215 px (a auditoria disse "~230").

**A página da distribuição tem 83.093 caracteres**, e não os 119.884 com que a `055` fechou: o PR 244
converteu os comentários documentais da folha para comentário do template. A conversão que o prompt
põe como primeira tarefa **já está na `main`**, e a margem sob o teto é de ~36.900 caracteres. Por
isso este lote não tem orçamento a disputar (a seção correspondente do [plan](plan.md) só registra
o saldo).

## D-002 — O stepper é uma grade de colunas iguais, e a situação sai da caixa-alta

**Decisão.** `ol.assistente` passa de `flex` com `flex:1 1 160px` para grade
`repeat(auto-fit, minmax(7.5rem, 1fr))`. Dentro de cada etapa, o número fica à esquerda do nome e da
situação, e não acima deles. A situação continua escrita, em caixa normal, e não em caixa-alta com
espaçamento.

**Por quê.** A 1280 px a página tem 1.232 px de conteúdo: nove colunas de 131 px. Com `auto-fit`, as
colunas que sobram colapsam e as nove esticam por igual; abaixo, a grade quebra em linhas de colunas
iguais — é o que a 3ª decisão pede, e o que `flex-wrap` não dá (ele estica as da última linha).
Prototipado na página viva: **66 px** de stepper (antes, 174), e o h2 de Perfis em **y = 416**.

**Por que a situação sai da caixa-alta.** "PRONTA PARA REVISAR" em caixa-alta espaçada pede ~148 px e
a coluna tem ~105 livres: quebrava em três linhas e empurrava o stepper acima dos 80 px. Em caixa
normal ela cabe em duas. A palavra não muda — ela sempre foi minúscula no HTML; a caixa-alta era da
folha.

**Descartado.** Encurtar o nome da etapa ou a situação: é texto, e texto fica (FR-1041). Esconder a
situação e deixar só a cor do número: é o que a 3ª decisão proíbe.

## D-003 — As ações vão para a linha da legenda por posição, e descem em tela estreita

**Decisão.** O grupo de ações passa a ser o filho seguinte à legenda, e a folha o posiciona no canto
superior direito do cartão, centrado na borda de cima — a mesma linha em que a legenda está, do
outro lado. Abaixo de 48 rem de janela ele volta ao fluxo, numa linha própria à direita, abaixo da
legenda.

**Por quê.** A legenda de um `fieldset` é desenhada **sobre** a borda, e é isso que a torna a "linha
da legenda": nada no fluxo divide a linha com ela. As alternativas que dividem de verdade custam mais
do que resolvem:

- **as ações dentro da `legend`**: a legenda é o nome acessível do grupo, e o grupo passaria a se
  chamar "Evento do Cronograma 1 de 3 Inscrições Subir Descer Remover este Evento" (FR-1027);
- **a legenda flutuando dentro do cartão**, com as ações ao lado: vira uma linha de cabeçalho de
  40 px *dentro* do cartão — medido, o cartão de Evento ficava com 227 px, mais alto que antes.

Posicionado, o grupo não ocupa linha nenhuma. Em tela estreita não há lado para ele: a legenda
("MODALIDADE DE CONCORRÊNCIA PPI") e as ações da Modalidade ("Aplicar aos demais Perfis (1)",
"Remover esta Modalidade", ~380 px) não cabem juntas a 375 px. A partir de 48 rem cabem com folga —
o cartão de Modalidade, o mais estreito, tem ~640 px de largura útil ali. É o que a FR-1026 pede: a
legenda e as ações nunca se sobrepõem.

## D-004 — A legenda segue o desenho do Retificar, e o nome é o do servidor

**Decisão.** A legenda passa a ter as duas vozes que o Retificar já usa: `.categoria` (caixa-alta
pequena) com a posição "N de M" dentro dela, e `.nome` com o identificador. `data-rotulo` na legenda
leva só a categoria. `ordenacao.js` passa a escrever a posição num `[data-ordem]` quando a legenda o
tiver; sem ele, faz o que fazia.

**Por quê.** `ordenacao.js` reescrevia a legenda inteira por `textContent`, o que apagaria o nome; e
`remocao.js` monta a pergunta de confirmação de `data-rotulo`. Com `data-rotulo` igual à categoria,
a pergunta continua "Remover Evento do Cronograma? …", palavra por palavra (FR-1027). O ajuste do
script é de seletor: a regra — numerar pela posição — é a mesma.

**O nome não acompanha a digitação.** É o que o servidor gravou ou reexibiu. Fazê-lo acompanhar
seria script novo escutando os campos, e a 1ª decisão recebida exclui padrão de interação novo. O
custo é conhecido: quem renomeia um Evento vê a legenda antiga até salvar o rascunho — o mesmo que o
Retificar faz hoje.

**O que identifica cada item.** Evento: o Tipo. Etapa: o Nome. Documento: o Nome. Modalidade: o
Código ("Modalidade PPP", como a 4ª decisão exemplifica). Vazio, o `.nome` não é desenhado, e a
legenda fica só com a categoria e a posição.

## D-005 — "Envio idêntico" compara chaves e valores, e não a ordem

**Decisão.** O envio é comparado como conjunto de pares (chave, valor) — todos, com repetição —,
sem o token de CSRF. A ordem em que os campos aparecem no corpo pode mudar onde a feature reordena
o formulário na tela.

**Por quê.** A 5ª decisão recebida põe "Onde acontece" depois do Término; a 9ª põe a Denominação
antes dos Requisitos. Nas duas o campo muda de lugar no documento, e com ele no corpo do envio. Pôr
o campo no lugar só pela folha (`order` do flex) deixaria a ordem de leitura e de tabulação diferente
da ordem visual (WCAG 1.3.2 e 2.4.3). O servidor lê por nome (`_indices`, `QueryDict`), e a 2ª
decisão recebida fala em "chaves e valores". A medição registra, além do resultado, se a ordem
mudou.

**Como se mede.** O corpo que o navegador montaria para "Salvar rascunho" (`new FormData(form,
botão)`), sem enviar: gravar o rascunho no meio da medição mudaria o estado que o "depois" lê — o
servidor normaliza o que recebe.

## D-006 — O Evento continua uma linha de campos só; "Onde acontece" quebra por largura

**Decisão.** A marcação continua com um único `div.campos` — `test_o_evento_cabe_numa_linha` o
exige, e a razão dele continua de pé: o Evento é uma faixa, não dois blocos. "Onde acontece" passa
para o fim da faixa, e perde o `largo`: sua coluna é de até 20 rem, sem crescer. A Descrição ganha o
`largo` e fica com o que sobra da linha.

**Medido no protótipo:** Descrição 406 px, "Onde acontece" 320 px, Início e Término no mesmo topo.
A 1280 px, "Onde acontece" quebra para a linha de baixo; numa janela larga o bastante (a página vai
até 96 rem), os cinco cabem numa linha, e a Descrição continua a maior.

**A meta de 150 px não se alcança com o arranjo da 5ª decisão.** Duas linhas de campo com rótulo em
cima somam, pelo ritmo da folha, ~165 px antes do preenchimento do cartão; o Evento media 215 px
porque **já** tinha duas linhas, e as ações dividiam a segunda com o Término — não tinham linha
própria. Alcançar 150 seria pôr "Onde acontece" na primeira linha (contra a 5ª decisão) ou o rótulo
dele ao lado do campo (um desenho de campo que a folha não tem). Nenhum dos dois entra; o valor
alcançado vai para o [verificacao.md](verificacao.md), como o prompt manda.

## D-007 — A seção do Conteúdo em `--leitura`, e o estilo só nela

**Decisão.** As regras do Conteúdo vão para o `{% block estilo_da_pagina %}` de
`compor_conteudo.html`: o cartão da seção com a largura da medida de leitura mais o próprio
preenchimento; a seção gerada sem borda, sem fundo e sem preenchimento; a marca de estado sem
caixa-alta e com peso de texto. A área de texto vazia nasce com `rows="2"`; a preenchida, com os
`rows="5"` de antes.

**Por quê.** Só essa etapa desenha `fieldset.secao` — e o que só uma etapa usa não pesa na folha
comum, que vai em toda página (prompt, *Restrições*).

## D-008 — A marca de seção vazia muda de desenho, e não de texto

**Decisão.** O texto continua " (vazia — não sai no documento)". Muda o desenho: sem caixa-alta, sem
espaçamento, em corpo de texto e na cor fraca.

**Por quê.** A 6ª decisão recebida permite encurtar o texto, desde que a informação continue
visível. Mas o texto está em quatro lugares que dependem dele — o `conteudo.js`, que o recalcula
enquanto se digita; `test_conteudo_da_054.py`, `test_compor.py` e `conteudo.test.js`, que o conferem
— e é o **nome acessível** do campo (054, UX-133): "Público-Alvo (vazia — não sai no documento)". O
que a fazia longa era a caixa-alta espaçada da legenda, que dobrava a largura; em caixa normal ela
ocupa pouco mais da metade. Trocar o texto custaria quatro arquivos e o nome do campo para ganhar o
que o desenho já ganha.

## D-009 — A seção gerada mantém o texto de ajuda inteiro

**Decisão.** A seção gerada perde a caixa e passa a ter um parágrafo só — "Composta automaticamente a
partir de X. Não há texto a redigir: …" — com o link "Ir para X" no fim dele, e não num parágrafo
próprio.

**Por quê.** A 6ª decisão recebida fala em "uma linha só (título e 'composta a partir de X')", e a
FR-1041 proíbe mexer em texto de ajuda além da marca de seção vazia. As duas não cabem juntas: a
frase inteira tem ~125 caracteres e não cabe numa linha da medida de leitura. Venceu o texto: tirar a
segunda frase seria editar ajuda. O que se ganha é a caixa (121 a 139 px por seção gerada) e a linha
do link.

## D-010 — A Revisão marca o rótulo onde a linha nasce, e não adivinha pelo dois-pontos

**Decisão.** `origens.py` ganha `Rotulada`, uma `str` que carrega `rotulo` e `valor`. As linhas que
`revisao.py` (e `origens.campos_definitivos`) compõem como "Rótulo: valor" passam a nascer por ela.
Um filtro de template separa as linhas de cada item em trechos: os rotulados viram `dl` com a grade de
`.dados-da-inscricao`; os corridos continuam `span.detalhe`, na mesma ordem.

**Por quê.** Separar pelo primeiro ": " no template tomaria por rótulo o texto de quem elabora — a
descrição de um Evento ("Inscrições: pelo sistema"), o texto de uma seção, a declaração do
Requerimento. A FR-1033 proíbe isso. Marcar na origem é a única forma de saber que a linha **tem**
rótulo.

**Por que `str`.** A linha continua sendo a mesma cadeia: `"Peso: 2" == Rotulada("Peso", "2")`. Os
testes de `revisao` que comparam linhas continuam valendo sem mudar, e é isso que prova que o
conteúdo não mudou (FR-1034). `com_origem` preserva o rótulo quando acrescenta a origem ao valor.

**A grade.** `.dados-da-inscricao` — `auto 1fr` — é a que a 7ª decisão recebida nomeia. O rótulo mais
longo ("Reverter vaga reservada não preenchida para a ampla concorrência") empurraria os valores para
o meio da linha; por isso a coluna do rótulo é limitada na folha da página (`estilo_da_pagina` da
Revisão), e o rótulo longo quebra dentro dela.

## D-011 — Os três campos longos do Retificar passam a `TEXTO_LONGO`

**Decisão.** Em `CAMPOS_RAIZ`, Título do Edital, Descrição e Declaração do Requerimento passam de
`TEXTO` para `TEXTO_LONGO`. O template desenha `TEXTO_LONGO` como área de texto; esses três, com 2
linhas, e os que já eram longos com as 5 de antes.

**Por quê.** Os dois tipos são convertidos pelo mesmo caminho (`_converter` e `_para_formulario` não
distinguem um do outro): a troca muda o controle, e não o que se lê, se compara ou se grava. O nome
do campo é posicional (`g{grupo}c{campo}`) e a posição não muda.

## D-012 — Anexos: a navegação deixa de herdar a medida de leitura

**Decisão.** `.navegacao-etapa` declara `max-width:none`. Na etapa Anexos, o estado vazio da lista
também.

**Por quê.** Nas outras etapas a navegação está dentro do formulário; em Anexos — que não grava
rascunho —, ela é filha direta de `main`, e `main>p` lhe dava a medida de leitura (685 px). Por isso
"Avançar" parava no meio. Na Revisão a navegação também é filha de `main`, e passa a ter a largura das
outras; nada nela se move, porque o último link dela não é `.botao`.

## D-013 — F6 reordena na apresentação, e não na lista de campos

**Decisão.** A ordem do cartão do Perfil no Retificar muda **no template**, por um filtro que
reordena os campos do grupo de Perfil depois de a referência de cada um já ter sido atribuída.
`CAMPOS_PERFIL` fica como está.

**Por quê.** A referência do campo é posicional — `g{grupo}c{campo}`, pela posição em
`CAMPOS_PERFIL`. Reordenar a lista renomearia todo campo do Perfil, que é o que a 2ª decisão
recebida proíbe. Reordenar depois da atribuição muda só a ordem em que os campos se desenham; o nome
de cada um, o que ele envia e a conferência do que vai mudar ficam iguais. Nenhum teste nem o
`retificacao.js` dependem da ordem de desenho: `test_retificacao_numera_pelo_documento` lê o
primeiro campo de grupos de **seção**, que o filtro não toca.

**A ordem.** A do editor do Perfil: Denominação, Localidade, Descrição, Carga horária, Remuneração,
Atribuições, Requisitos, Vagas imediatas, Limite do Cadastro Reserva, Modalidade que é a ampla
concorrência, Forma de comunicar a convocação. O Código não é retificável e não aparece.
