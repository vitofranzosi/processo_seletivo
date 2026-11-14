# C. Relatório de evidências

*Base: `main` em `37ed0ad0`, 14/11/2026. Banco próprio da auditoria (`ps_auditoria_visual`), com o
`seed_demo` e os 17 cenários de treinamento. Nada no produto foi alterado.*

Três dimensões, avaliadas em separado, como o pedido exige:

| Dimensão | Pergunta | Onde está neste documento |
|---|---|---|
| Design system | Os elementos e os padrões são consistentes? | §2, S3 a S10 |
| Layout e composição | A informação está bem distribuída e dimensionada? | §2, S1 e S2; §3 |
| Experiência operacional | Dá para fazer a tarefa com clareza e pouco esforço? | §4 |

## 1. Como foi medido

| Item | Valor |
|---|---|
| Navegador | Chromium 156 sem janela, dirigido pelo Playwright do grupo `navegador` |
| Rastreio | 647 visitas com resposta 200, **131 variações de tela**, só por GET; o único POST é o da entrada |
| Identidades | presidência com todos os papéis da demonstração (em dois Processos), avaliador, setor da formalização, quatro candidatos fictícios e visitante |
| Medida por tela | [`medicoes/metricas.js`](medicoes/metricas.js): moldura, cabeçalhos, assinatura de cada botão, campo, selo, aviso, caixa e tabela, tamanhos de fonte por volume de texto, contraste, alvos e rótulos |
| Larguras | 375, 768, 1280, 1440 e 1920 px, em 116 telas ([`medicoes/largura.js`](medicoes/largura.js)) |
| Folhas | leitura estática dos 55 arquivos CSS ([`medicoes/css_metrics.py`](medicoes/css_metrics.py)) |
| Resultado por tela | [`medicoes/telas.csv`](medicoes/telas.csv) |

**Duas medidas pedem explicação.**

- *Assinatura* é a combinação de valores que o navegador de fato aplicou a um elemento: altura,
  fonte, raio, padding e cor. Duas regras diferentes que dão o mesmo resultado contam uma vez; uma
  regra que rende resultados diferentes conta várias.
- *Metade direita ocupada* é a fração da altura do conteúdo em que existe algum texto ou controle
  além do meio da área útil. Uma tela com 14% tem a metade direita vazia em 86% da altura.

**O que não foi medido.** As 44 rotas marcadas no [inventário](01-inventario.md) como não vistas no
navegador. As conferências que só nascem de um POST (conferir a convocação, emitir a ordem, emitir o
corte, acrescentar vaga) não foram abertas, porque o rastreio não pratica gesto. Os estados de aviso
enviado, publicação de convocados e publicação das inscrições não existem nos cenários. O PDF do
Edital ficou de fora: é o ato oficial, e não interface.

## 2. Problemas sistêmicos

Cada um explica vários sintomas ao mesmo tempo. A severidade considera alcance e efeito; o esforço é
relativo (P, M, G).

### S1. Não existe um cabeçalho de página

**Evidência.** As 89 telas da gestão abrem de **71 jeitos diferentes**, contando só os quatro
primeiros elementos do conteúdo. A sequência mais comum (`h1 → p.sub → p.erro → p.sucesso`) aparece
em 6 telas. O `interface/base.html` oferece dois blocos, `caminho_do_contexto` e `conteudo`, e cada
template escreve o próprio `h1`, o subtítulo, as mensagens e as ações. O único bloco de construção
compartilhado é a trilha de navegação (`_produto_na_trilha.html`, em 90 inclusões).

**Consequência.** A ação da página aparece em quatro lugares, conforme a tela:

| Onde fica a ação de página | Exemplo |
|---|---|
| Abaixo do subtítulo, contornada e pequena | Distribuição ([captura](capturas/g-distribuicao.jpg)) |
| À direita dos selos, contornada e pequena | Página do Processo ([folha 1](capturas/folha-1-centro-processo-atividades.jpg)) |
| Abaixo de um painel, cheia | Lista: "Novo Processo Seletivo" ([captura](capturas/g-lista.jpg)) |
| Abaixo do subtítulo, contornada e grande | Visão Geral: "Relatório consolidado" ([captura](capturas/g-visao-geral.jpg)) |

O tamanho do `h1` é o mesmo em todas (25,6 px), e toda tela tem um `h1` só. O que varia é a
composição ao redor dele.

**Causa.** O sistema de design existe como classes de CSS, e não como componentes de template.
**Abrangência:** todas as telas. **Severidade:** alta. **Esforço:** M (um parcial e a migração por
família). **Risco:** baixo; os guardiões de acessibilidade já exigem um `h1` e a ordem dos títulos.

### S2. A largura não tem regra por tipo de conteúdo

**Evidência.** O produto tem duas medidas, `--pagina` (96rem) para a estrutura e `--leitura` (68ch)
para o texto, e a decisão está certa. Falta a composição intermediária: quase toda tela tem prosa,
indicadores pequenos e um formulário curto, e tudo isso se alinha à esquerda dentro de uma página
larga.

| Largura da janela | Metade direita ocupada (mediana, 92 telas da gestão) | Telas abaixo de 50% | Terço direito (mediana) |
|---|---:|---:|---:|
| 1280 px | 30,5% | 89 de 92 | 20% |
| 1440 px | 27% | 90 de 92 | 12% |
| 1920 px | 14% | 92 de 92 | 9% |

A 1920 px, na tela mediana, a metade direita está vazia em 86% da altura
([Ocupação a 1920 px](capturas/w1920-g-ocupacao.jpg)). As telas que melhor ocupam a largura são o
Centro de Controle (46% a 1440 px) e as etapas de formulário do assistente (37% a 57%).

No portal o efeito é maior, e há um segundo defeito. A 1440 px, 9 das 20 telas têm **0%** da metade
direita ocupada. A 1920 px o `main` é centralizado em 96rem, mas o conteúdo continua encostado à
esquerda dele: sobram 216 px de um lado e entre 995 e 1.192 px do outro
([convocação do candidato a 1920 px](capturas/w1920-p-convocacao.jpg)). Só o cartão de acesso é
centralizado.

**O contrário também acontece.** Onde a prosa escapou da medida de leitura, a linha fica longa
demais: 195 caracteres por linha na Trilha de auditoria a 1920 px, 176 nas confirmações de Encerrar
e Cancelar, 173 na Revisão, 178 na página do recurso do candidato a 1440 px. O confortável fica
entre 65 e 75.

**Causa.** `main{max-width:var(--pagina)}` sem um contêiner por arquétipo.
**Abrangência:** todas as telas com mais de 1280 px de janela. **Severidade:** alta: é a percepção
mais citada no pedido. **Esforço:** M. **Risco:** médio: `tests/interface/test_larguras.py` prende
as duas medidas e precisa aprender a terceira e a quarta.

### S3. A escala tipográfica tem degraus demais

**Evidência.** As folhas da gestão declaram **33 valores de `font-size`**; a do portal, 29.
Renderizado, 93% do texto da gestão sai em oito tamanhos entre 12 e 16 px:

| Tamanho | 16 | 14 | 12 | 15 | 13 | 14,4 | 13,6 | 12,8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Fração do texto | 24,7% | 23,0% | 13,4% | 12,8% | 7,6% | 7,3% | 3,0% | 1,5% |

Aparecem ainda 13,12 e 14,72 px. O `h2` sai em **cinco tamanhos** (16, 16,8, 17, 17,6 e 18,4 px) e o
`h3` em quatro (12, 13, 15 e 16).

**Um problema à parte: a fonte depende da máquina.** A pilha é `"Open Sans","Segoe UI",system-ui`, e
o produto não embarca fonte nenhuma (nenhum `@font-face`). Quem tem Open Sans instalada vê uma
fonte; no Windows sem ela, Segoe UI; no macOS, a do sistema. A tela de entrada da gestão usa outra
pilha, `--fonte`, declarada em `grupos/acesso.css`.

**Consequência.** Diferenças de 0,4 a 1 px não criam hierarquia, criam ruído: é o que faz duas telas
vizinhas parecerem de produtos diferentes sem que se saiba dizer por quê.
**Severidade:** média. **Esforço:** M. **Risco:** médio: mexe em toda tela, pede comparação de
capturas.

### S4. A caixa tem 37 formas

**Evidência.** Nas folhas da gestão há **63 regras** que desenham uma caixa (borda, raio, fundo e
padding), em **37 combinações** de raio e padding. Renderizadas, são 36 assinaturas. A dominante
(6 px, 16×20 px, fundo branco) aparece em 38 telas; as outras 35 dividem o resto.

O caso mais visível é o **indicador**, o número com rótulo, que tem sete desenhos:

| Tela | Como é o indicador |
|---|---|
| Visão Geral | número de 26 px, rótulo em negrito, nota ([captura](capturas/g-visao-geral.jpg)) |
| Distribuição | caixa pequena que abraça o conteúdo; a selecionada tem borda verde ([captura](capturas/g-distribuicao.jpg)) |
| Convocação, "Neste recorte, agora" | número e rótulo na mesma linha, com filete à esquerda ([captura](capturas/g-convocacao.jpg)) |
| Convocação, "Pela apuração" | grade de caixas dentro de um painel tracejado |
| Corte | número em cima, rótulo pequeno, selecionado com fundo verde ([captura](capturas/g-corte.jpg)) |
| Relatório do Edital | caixa com filete verde no topo ([captura](capturas/g-relatorio-do-edital.jpg)) |
| Agenda | rótulo em cima, número embaixo ([captura](capturas/g-agenda.jpg)) |

**Caixa dentro de caixa.** 9 telas chegam a dois níveis de borda e 3 chegam a três (Convocação,
Documentos da convocação, Classificação do assistente).

**Causa.** `.cartao` existe em `componentes.css`, mas cada folha de tela declarou a própria caixa
(`.painel-do-relatorio`, `.neste-recorte`, `.sintese-da-agenda`, `.consolidado`, `.secao-do-kit`).
**Severidade:** média. **Esforço:** M. **Risco:** baixo.

### S5. O botão pequeno tem quatro alturas, e a barra de ações, três convenções

**Evidência.** Há duas famílias: `.botao` (40 px, 15 px de fonte, raio 4) e `.acao` (13 px, raio 3).
A primeira é estável. A segunda rende **25, 26, 30 e 40 px** conforme a etiqueta e o contexto:

| Elemento | Altura | Telas |
|---|---:|---:|
| `a.acao` | 30 px | 17 |
| `button.acao` | 25 px | 13 |
| `a.acao` | 26 px | 5 |
| `a.acao` e `button.acao` promovidos por contexto | 40 px | até 17 |

A diferença de 5 px entre `a.acao` e `button.acao` vem do `line-height`: o link herda 1,5 do `body`,
e o botão usa o do navegador. Lado a lado, os dois ficam desalinhados.

A barra de ações do formulário segue três convenções:

| Convenção | Onde |
|---|---|
| Secundária à esquerda, primária à direita | assistente de composição, criar Processo ([captura](capturas/g-criar-processo.jpg)) |
| Primária à esquerda, "Cancelar" ao lado | publicar resultado ([captura](capturas/g-publicar-resultado.jpg)) |
| Primária à esquerda, sozinha | instruir recurso, filtros |

No portal o botão tem 42 ou 48 px e o campo tem 42, 48 ou 56 px; na gestão o campo tem 40.
**Severidade:** média. **Esforço:** P para a altura (uma regra), M para a barra de ações.
**Risco:** baixo.

### S6. O aviso tem 28 regras

**Evidência.** Na gestão há **28 regras** de faixa (fundo com filete à esquerda) e 24 assinaturas
renderizadas; no portal, 21 regras. `.aviso` cobre 28 telas e `.imutavel` 14; as outras 26 regras
são de uma tela só (`.atencao-do-andamento`, `.providencia-do-corte`, `.confirmacao-da-conferencia`,
`.situacao-da-convocacao`, `.piloto`). O tom verde tem três nomes (`.imutavel`, `.sucesso`,
`.bastao`) para o mesmo desenho.

**Consequência.** Numa confirmação como Encerrar empilham-se três blocos coloridos seguidos
([captura](capturas/g-ato-encerrar.jpg)), e o que é impeditivo pesa o mesmo que o que é informativo.
O tom só se distingue pela cor: não há ícone nem rótulo de espécie.
**Severidade:** média; toca o critério 1.4.1 do WCAG (uso de cor). **Esforço:** M. **Risco:** baixo.

### S7. Há dois conjuntos de tokens, e cor fora deles

**Evidência.**

- `shared/tokens.css` define 18 tokens, e 94% das cores da gestão passam por eles (1.166 usos de
  `var()`). A base é boa.
- `interface/grupos/acesso.css` define **outros 14** (`--tinta`, `--linha`, `--fundo-p`, `--raio`,
  `--raio-p`, `--sombra-1`, `--fonte`), usados só na entrada da gestão.
- Sobram **41 cores literais em 78 usos**. As mais repetidas: `#1d4f91`, o azul da prévia da
  classificação (11 usos, sem token), e a paleta cinza-azulada da Visão Geral (`#5a6470`, `#d7dce2`,
  `#9aa3ad`).

**Consequência mensurável.** A única tela que reprova em contraste é a que saiu dos tokens: a Visão
Geral tem **155 trechos de texto abaixo de 4,5:1**, a maior parte em `#9aa3ad` sobre `#f8f8f8`
(2,41:1). Nas demais telas medidas nenhum trecho reprova; o guia incorporado é caso à parte (E11). O teste `test_contraste_atende_wcag_aa` confere
os pares de tokens, e por isso não vê a cor literal.
**Severidade:** alta na Visão Geral (acessibilidade), média no resto. **Esforço:** P. **Risco:**
baixo.

### S8. Os pontos de quebra são 19

**Evidência.** As folhas da gestão usam 19 condições de `@media` distintas (34, 36, 40, 44, 46,
47,99, 48, 56, 60, 64, 75 e 96rem, mais 900 px e 1180 px) e 7 de `@container`; o portal, mais 8
(inclusive 520 px e 600 px).

**O resultado no celular é bom, e isso é mérito do que já existe.** Nenhuma das 116 telas medidas
transborda a 375 px; 26 delas usam moldura rolável para a tabela
([folha de celular](capturas/folha-8-celular.jpg)).

**Há um defeito a 768 px:** a Visão Geral transborda (880 px de largura de documento). A tabela dela
tem moldura própria (`.rolagem-da-tabela`) e não a comum.
**Severidade:** média. **Esforço:** P para o defeito, M para a convenção. **Risco:** baixo.

### S9. Estilo de uma tela só

**Evidência.** Das 1.214 classes definidas nas folhas da gestão, **576 (47%)** são citadas por um
único template; no portal, 190 de 438 (43%). A folha `telas.css`, comum a toda a gestão, tem 828
linhas de regras que em boa parte servem a uma tela.

**Leitura.** Não é desleixo: é o custo de cada tela ter sido resolvida sozinha, com o guardião
exigindo regra para toda classe citada. O que falta é o caminho inverso, um conjunto pequeno de
componentes que dispense a classe nova.
**Severidade:** média (custo de manutenção e origem das demais). **Esforço:** G, diluído na
convergência. **Risco:** médio: 34 arquivos de teste leem as folhas como texto, e renomear classe
quebra guardião.

### S10. Selos, passos, filtros e molduras de tabela repetidos

| Peça | Quantas formas | Exemplos |
|---|---:|---|
| Selo | 26 assinaturas na gestão, 13 no portal | `.situacao` (pílula), `.codigo`, `.marca-irreversivel`, `.marca-sua`, `.selo-da-especie`, `.marca-das-providencias`, `.marca-agora` |
| Passos | 4 desenhos | assistente de composição, mapa de fases do Centro, passos do sorteio, `.etapas` com pontos |
| Barra de filtros | 6 classes | `.filtro`, `.filtros`, `.filtros-da-agenda`, `.filtros-da-visao`, `.filtros-da-mesa`, `.filtro-da-retificacao` |
| Moldura de tabela | 7 nomes | `.tabela-rolavel`, `.rolagem`, `.rolavel-no-estreito`, `.rolagem-da-tabela`, `.moldura-da-grade`, `.moldura-do-andamento`, `.distribuicao-moldura` |
| Botão "Filtrar" | 2 pesos | cheio em Inscrições e Recursos, contornado em Agenda e Minhas atividades |
| Ícone | 2 sistemas | o conjunto de traço da barra lateral, e glifos de texto (✓ ◐ ○ ▸ ↑ ↓) no resto |

A tabela em si é consistente: célula de 8×12 px e cabeçalho de 12 px em caixa alta em quase todas
as telas com tabela; as exceções são as matrizes do Centro, da Agenda e da Visão Geral. O que varia
é a moldura e se ela está ou não dentro de um cartão.
**Severidade:** baixa a média. **Esforço:** M. **Risco:** baixo.

### S11. Espaçamento sem escala

As folhas da gestão têm 141 valores distintos de `padding`, 104 de `margin` e 55 de `gap`. Os mais
usados já formam uma escala implícita (0,25, 0,5, 0,75, 1, 1,25, 1,5rem); o resto são vizinhos de
um ou dois décimos (0,35, 0,4, 0,45, 0,6, 0,7, 0,85, 0,9rem).
**Severidade:** baixa. **Esforço:** M. **Risco:** baixo.

## 3. Problemas específicos

Não se resolvem só com o design system: pedem decisão de composição da tela.

| # | Tela | Evidência | Recomendação | Sev. | Esf. |
|---|---|---|---|---|---|
| E1 | Visão Geral | transborda a 768 px; paleta própria; 155 trechos abaixo do contraste; 9 tamanhos de fonte | voltar aos tokens, usar a moldura comum de tabela | alta | P |
| E2 | Lista de Processos | 3.210 px para 19 Processos; cada Processo são duas caixas e dois botões repetidos; a ação de criar fica abaixo de um painel de texto | tabela com o Edital como linha filha, e "ações disponíveis" no trilho ([protótipo](04-prototipos.md)) | alta | M |
| E3 | Convocação | 4.325 px, 30 caixas, três níveis de borda, 5 assinaturas de botão, a mesma contagem em dois desenhos | indicadores no topo, o gesto principal num cartão, contexto no trilho ([protótipo](04-prototipos.md)) | alta | G |
| E4 | Retificar | 11.631 px e 168 campos numa página | seções recolhidas por área, com índice fixo; é decisão de fluxo, fora deste estudo | média | G |
| E5 | Revisão do assistente | 8.904 px; linha de 173 caracteres a 1920 px | medida de leitura nos blocos de texto; índice das seções no trilho | média | M |
| E6 | Alocação por Etapa | troca a moldura inteira: a barra lateral vira barra no topo ([captura](capturas/g-alocacoes.jpg)) | manter a barra lateral, recolhida, e dar a página cheia à matriz | média | P |
| E7 | Portal, "Minhas inscrições" e "Recorrer" | um cartão e uma área de texto estreitos, encostados à esquerda numa página de 1440 px ([captura](capturas/p-minhas-inscricoes.jpg)) | página centrada | média | P |
| E8 | Confirmações de ato | três faixas coloridas seguidas; linha de 176 caracteres | página centrada, um aviso por tom, impeditivo antes do informativo | média | M |
| E9 | Formalização (lista) e Kit de divulgação | estado vazio sem o componente `.vazio`; a página fica 69% preenchida | usar `.vazio` com a ação seguinte | baixa | P |
| E10 | Agenda, "próximos marcos" | 6.748 px; 69 alvos menores que 24 px | agrupar por semana e paginar | baixa | M |
| E11 | Documentação do Sistema | linguagem visual própria (`h1` de 34 px, estilo embutido), 144 trechos abaixo do contraste | herdar os tokens; é guia, e pode ter medida de leitura própria | baixa | M |
| E12 | Requerimento de Matrícula (portal) | cinco campos por linha a 1440 px, na largura toda ([captura](capturas/p-requerimento.jpg)) | medida de formulário, dois ou três campos por linha | média | P |

## 4. Experiência operacional

São leituras de quem percorreu as telas com os cenários, e não resultado de teste com usuário. Valem
como hipótese a confirmar com a equipe de seleção.

**O1. A explicação ocupa o lugar do trabalho.** Várias telas de operação abrem com parágrafos
permanentes ("Abrir esta tela não apura nada", "Ocupada na apuração não quer dizer convocada",
"Consolidar transforma as avaliações…") antes do primeiro dado. O texto é correto e necessário na
primeira vez; na décima, é o que se rola para chegar ao botão. A Ocupação tem quatro blocos
explicativos para quatro números. *É falha de composição, e não de fluxo:* o conteúdo fica, e muda
de lugar, para o trilho ou para um recolhido.

**O2. A ação principal nem sempre é a mais visível.** Na Distribuição, "Consolidar as 3 prontas" é
contornada, e "Propor distribuição", mais abaixo, é cheia. A Comissão, a Distribuição e a Convocação têm três ou
mais botões cheios ao mesmo tempo.

**O3. O mesmo número em dois desenhos na mesma tela.** A Convocação mostra "titulares a convocar" na
faixa "Neste recorte, agora" e as vagas em duas grades logo abaixo. Quem lê precisa descobrir que
são contagens de coisas diferentes (vagas e pessoas). A tela já explica isso em prosa; a composição
pode fazê-lo antes da prosa.

**O4. A passagem entre telas consecutivas muda de linguagem.** Do Centro de Controle (grade de dois
painéis, mapa de fases) para a Convocação (coluna única, seções com filete verde) e daí para os
Documentos (cartões e faixas), três composições em três cliques.

**O5. O que funciona, e deve ser preservado.** "O que fazer agora" no Centro diz de quem é a ação e
por que ela é a próxima. "Minhas atividades" lista o trabalho sem caixa nenhuma. A confirmação de ato
irreversível separa o que impede, o que continua e o que não se desfaz. A convocação do candidato
põe o prazo acima de tudo. Nenhuma dessas é problema visual.

## 5. O que os números dizem de bom

| Medida | Resultado |
|---|---|
| Telas com um `h1` e só um | todas as medidas |
| Campos sem rótulo acessível | 0 |
| Telas que transbordam a 375 px | 0 de 116 |
| Telas que reprovam em contraste | 1 da gestão (Visão Geral) e o guia incorporado |
| Cor por token | 94% dos usos na gestão; 3 literais no portal |
| Foco visível | regra global, 3 px, em todo elemento |
| Estilo ou script embutido | nenhum; a política de conteúdo recusa |

A fragmentação é de composição e de escala, e não de fundação. É por isso que a proposta é
consolidar, e não refazer.
