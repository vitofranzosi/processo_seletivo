# D. Proposta do GPS Design System

*Proposta, sem nada implementado no produto. A folha [`prototipos/gps-ds.css`](prototipos/gps-ds.css)
traz cada token e cada componente descritos aqui, e a
[folha de componentes](prototipos/componentes.html) mostra todos numa página.*

## 0. O que é direção, e o que é hipótese

Depois da revisão de 14/11 ([registro](06-revisao.md)), a proposta se divide em duas partes.

| Parte | O que contém | Situação |
|---|---|---|
| **Direção experimental**, para o piloto | os neutros da tela de entrada; a hierarquia (cabeçalho de página, composições de largura); os componentes (botão, indicador, aviso, cartão) | recomendada para aprovação, como experimento |
| **Hipóteses**, para decidir depois do piloto | a redução tipográfica (seis tamanhos, tabela em 14 px); o recolhimento e o deslocamento de explicações; os limites rígidos (um botão cheio por tela, quatro pontos de quebra, um aviso por tom, um nível de caixa); os guardiões novos | ficam descritas aqui, sem valer como regra |

Onde este documento diz "sempre", "no máximo" ou "um só", leia-se convenção de partida. Vira regra o
que o piloto confirmar com a equipe.

## 1. Três decisões de partida

1. **Consolidar, e não substituir.** O produto já tem tokens num lugar só, moldura única, política
   de conteúdo e guardiões. A proposta mantém os nomes de classe que existem (`.botao`, `.acao`,
   `.cartao`, `.aviso`, `.situacao`, `.codigo`, `.campo`, `.tabela`, `.sub`) e reduz as variantes.
   Nenhuma biblioteca nova: a pilha continua sendo template do Django, CSS em arquivo e htmx.
2. **Cada componente passa a ter contrato.** O que ele é, quais variantes tem e quando se usa,
   escrito num lugar só e acompanhado de um mecanismo de adoção. O contrato pode ser firmado por
   CSS, por parcial de template ou pelos dois, conforme a peça: o cabeçalho de página pede parcial,
   porque é estrutura; o botão se resolve em CSS. Criar parciais, sozinho, não resolve.
3. **A largura é decidida pelo tipo de conteúdo.** Tabela ocupa a página; formulário tem medida
   própria; prosa tem medida de leitura; contexto vai para um trilho ao lado.

## 2. Fundamentos

### 2.1 Cor

Os valores de hoje ficam. Mudam duas coisas: os neutros da tela de entrada viram oficiais, e o azul
ganha token.

| Papel | Token | Valor | De onde vem |
|---|---|---|---|
| Marca, preenche | `--verde` | `#15803d` | `tokens.css`, sem mudança |
| Marca, escreve | `--verde-texto` | `#146c37` | idem |
| Marca, barra e selo | `--verde-escuro` | `#0b5a2a` | idem |
| Fundo de destaque | `--verde-claro`, `--verde-50`, `--verde-100` | `#e7f5ec`, `#eef7f1`, `#d9eee0` | os dois últimos só existem em `acesso.css` |
| Texto | `--tinta` | `#0f1a14` | `acesso.css`; `--texto` passa a apontar para ele |
| Rótulo | `--tinta-2` | `#36433b` | `acesso.css` |
| Apoio | `--tinta-3` | `#5f6b64` | `acesso.css`; `--texto-fraco` aponta para ele |
| Borda de caixa | `--linha` | `#e3e7e4` | `acesso.css` |
| Borda de controle | `--linha-forte` | `#cfd6d1` | `acesso.css`; `--borda` aponta para ele |
| Fundo da página | `--fundo-p` | `#f6f7f6` | `acesso.css`; `--fundo` aponta para ele |
| Atenção | `--amarelo`, `--amarelo-fundo` | `#8a5300`, `#fdf5e5` | sem mudança |
| Perigo | `--vermelho`, `--vermelho-fundo` | `#a91b1b`, `#fbe9e9` | sem mudança |
| Informação | `--azul`, `--azul-fundo` | `#1d4f91`, `#e8f0fb` | hoje literal, em 15 usos |

Contraste dos pares novos sobre branco: `--tinta` 17,8:1, `--tinta-2` 10,4:1, `--tinta-3` 5,6:1,
`--azul` 8,1:1. `--tinta-3` sobre `--fundo-p` dá 5,2:1, e `--azul` sobre `--azul-fundo`, 7,1:1.
**Um par reprova e fica proibido:** `--tinta-3` sobre `--linha` dá 4,46:1; sobre fundo cinza o texto
de apoio usa `--tinta-2`. *Valores calculados pela fórmula do WCAG; entram no
`test_contraste_atende_wcag_aa` antes de valerem.*

**Regra.** Nenhuma cor literal fora de `tokens.css`. As 41 de hoje somem por substituição: 15 viram
`--azul`, a paleta da Visão Geral volta aos neutros, e o resto é variação de um tom existente.

### 2.2 Tipografia

*Hipótese, para decidir depois do piloto. No piloto as telas mantêm os tamanhos de hoje.*

Seis tamanhos, no lugar dos onze que hoje têm mais de 1% do texto cada.

| Token | Tamanho | Uso | O que absorve |
|---|---:|---|---|
| `--t-24` | 24 px | título da página | 25,6 e 28 |
| `--t-18` | 18 px | título de seção | 16,8, 17, 17,6 e 18,4 |
| `--t-16` | 16 px | corpo, campos, prosa, `h3` | 15 em parágrafo |
| `--t-14` | 14 px | interface densa: tabela, botão, lista | 14,4, 14,72 e 15 em tabela |
| `--t-13` | 13 px | ajuda, rótulo de campo, segunda linha | 12,8, 13,12 e 13,6 |
| `--t-12` | 12 px | rótulo de seção, selo, cabeçalho de tabela | 11 e 11,2 |

- Pesos: 400 e 600. O 700 fica só para a marca em caixa alta.
- Título com `letter-spacing:-.011em` e altura de linha 1,25; corpo com 1,5.
- **Fonte.** Declarar a pilha do sistema (`--fonte`) como a fonte do produto: é o que a maioria já
  vê, e remove a dependência de ter Open Sans instalada. Se a instituição quiser Open Sans, embarcar
  o arquivo (`font-src 'self'` já permite) e medir o peso. É decisão de identidade, e fica com o
  usuário (ver o [roadmap](05-roadmap.md), decisão 3).

### 2.3 Espaço

Base 4: `--e-1` 4, `--e-2` 8, `--e-3` 12, `--e-4` 16, `--e-5` 20, `--e-6` 24, `--e-8` 32, `--e-10` 40.
Os vizinhos de hoje caem no degrau mais próximo (0,35 e 0,4rem viram 8 px; 0,6 e 0,7 viram 12; 0,85
e 0,9 viram 16).

| Relação | Espaço |
|---|---|
| Rótulo e controle | 4 |
| Itens de um grupo | 8 a 12 |
| Campos de um formulário | 16 |
| Dentro de um cartão | 20 |
| Entre cartões | 16 |
| Entre seções | 32 |
| Margem da página | 24 (16 no celular) |

### 2.4 Forma

| Token | Valor | Uso |
|---|---|---|
| `--raio-p` | 6 px | controle, aviso, segmento |
| `--raio` | 10 px | cartão, indicador |
| `--raio-pilula` | 999 px | situação |
| `--sombra-1` | sutil | cartão |
| `--sombra-2` | elevada | o que flutua: a barra lateral no celular |

A borda continua sendo o separador principal. A sombra é discreta e existe para o cartão se soltar
do fundo, e não para decorar. Hoje há 24 valores de raio, com 6 px e 4 px dominando.

### 2.5 Controles

| Token | Altura | Uso |
|---|---:|---|
| `--controle` | 40 px | botão e campo na gestão |
| `--controle-p` | 32 px | ação de linha, filtro, segmento |
| `--controle-g` | 48 px | ação principal do candidato no portal |

O `.acao` passa a ter 32 px sempre, com `line-height:1` e `display:inline-flex`, e a diferença entre
`a` e `button` deixa de existir.

### 2.6 Ícones

Um conjunto só: o de traço de 1,75 que a barra lateral já usa, estendido para as ações (mais, seta,
subir, descer, remover, arquivo). Os glifos de texto (✓ ◐ ○ ▸) saem aos poucos; onde carregam
estado, continuam acompanhados de palavra.

### 2.7 Pontos de quebra

*Hipótese. Quatro é ponto de partida, e não teto: a tela cujo conteúdo quebra em outro lugar
justifica o próprio ponto.*

Quatro, no lugar de dezenove:

| Nome | Largura | O que muda |
|---|---|---|
| celular | abaixo de 40rem | tabela empilha ou rola; botões de página ocupam a linha |
| médio | 40rem a 64rem | uma coluna; a barra lateral é gaveta |
| largo | 64rem | barra lateral fixa |
| com trilho | 80rem | o trilho de contexto aparece ao lado |

`@container` continua valendo para o componente que precisa se adaptar ao espaço que recebeu, e não
à janela (a ficha do conjunto, os números do relatório).

### 2.8 Acessibilidade (WCAG 2.2 AA)

| Critério | Regra do sistema |
|---|---|
| 1.4.3 Contraste | todo par de token passa de 4,5:1; nenhuma cor literal |
| 1.4.1 Uso de cor | aviso e situação levam ícone ou marca, além da cor |
| 1.4.10 Refluxo | nenhuma tela transborda a 320 px de CSS; tabela larga rola dentro da moldura |
| 2.4.7 e 2.4.11 Foco | o contorno de 3 px de hoje, mantido; nada fixo pode cobrir o elemento em foco |
| 2.5.8 Tamanho do alvo | controle de 32 px no mínimo; caixa de seleção e rádio de 18 px com rótulo clicável |
| 3.3.2 Rótulos | rótulo visível em todo campo; ajuda abaixo, ligada por `aria-describedby` |
| 2.3.3 Movimento | transição só de cor e de borda, desligada em `prefers-reduced-motion` |

## 3. Larguras: a regra por tipo de conteúdo

| Conteúdo | Medida | Por quê |
|---|---|---|
| Tabela, matriz, mapa de fases, calendário | a página (`--pagina`, 96rem) | cada coluna a mais é informação |
| Formulário de uma coluna | `--formulario` (46rem) | campo esticado não ajuda a preencher, e afasta o rótulo do erro |
| Formulário com campos curtos | grade de 12 colunas dentro de `--formulario` | dois ou três campos por linha, e não cinco |
| Prosa, ajuda, consequência | `--leitura` (68ch) | 65 a 75 caracteres por linha |
| Contexto e apoio | `--trilho` (21rem) | situação, definições, pendências e histórico ao lado do trabalho |
| Página de um gesto só | `--coluna` (44rem), centrada | confirmação de ato, jornada do candidato, acesso |

**Três composições de página** resolvem todas as telas:

1. **Cheia.** Cabeçalho e uma área de largura total. Para lista, matriz e relatório.
2. **Principal e trilho.** Coluna de trabalho mais 21rem de contexto, a partir de 80rem de janela;
   abaixo disso o trilho desce para o fim. É a resposta para a metade direita vazia: o que hoje é
   parágrafo explicativo acima do trabalho passa a ser apoio ao lado dele.
3. **Centrada.** Uma coluna de 44rem no meio. Para confirmar, para o candidato e para entrar.

Em monitor muito largo, a página para em 96rem e fica centralizada. Nada estica além disso.

**O trilho no celular é ponto aberto.** Abaixo de 80rem ele desce para o fim da página. Onde carrega
pendência ou ajuda de preenchimento, isso o põe depois da ação de avançar, que é a ordem errada
para quem preenche: é o que acontece no protótipo de Compor a 375 px. A posição no estreito precisa
ser decidida por conteúdo (pendência antes do formulário, ajuda junto do campo), e não por uma
regra única.

**O critério destas composições é a tarefa, e não a largura preenchida.** Vale a composição em que a
ação fica perto do dado de que depende, o contexto fica à vista sem empurrar o trabalho, e a prosa
não passa da medida de leitura. Ocupar a metade direita não é objetivo.

## 4. Componentes

Para cada um: o que existe, o que fica e quantas formas somem.

| Componente | Variantes propostas | Hoje |
|---|---|---|
| **Cabeçalho de página** | título, selos, subtítulo, ações à direita, abas opcionais | 71 aberturas em 89 telas |
| **Botão** | primário, secundário, discreto, perigoso; 40 e 32 px | `.acao` com 4 alturas |
| **Campo** | texto, seleção, área, escolha, arquivo; rótulo, ajuda, recusa | 12 assinaturas |
| **Cartão** | plano, sem recuo (para tabela), calculado (tracejado), destaque | 63 regras, 37 combinações |
| **Indicador** | padrão, zero, ativo, compacto | 7 desenhos |
| **Selo** | situação (pílula), código (mono), marca (caixa alta) | 26 assinaturas |
| **Aviso** | atenção, informação, sucesso, erro; bloco e em linha | 28 regras |
| **Tabela** | padrão e densa; sempre em `.tabela-rolavel`, dentro de cartão | 7 molduras |
| **Barra de filtros** | busca e seleções em linha, "Filtrar" secundário | 6 classes |
| **Abas e segmentos** | abas para vistas, segmentos para recortes | 3 desenhos |
| **Passos** | feito, atual, atenção, pendente | 4 desenhos |
| **Lista de itens** | linha com corpo e ação, sem caixa por item | caixa por item na Lista, na Comissão e nas Autoridades |
| **Barra de ações** | fixa ao pé; voltar à esquerda, primária à direita | 3 convenções |
| **Estado vazio** | texto e a ação seguinte | `.vazio`, ausente em 2 telas |
| **Paginação** | contagem à esquerda, anterior e próxima à direita | 1 forma; fica |
| **Envio de arquivo** | botão secundário com ícone, nome do arquivo, situação | 2 formas (gestão e portal) |

**O que não entra.** Diálogo modal: o produto confirma ato em página própria, sem script, e isso é
decisão de segurança (prevenção nos atos irreversíveis). A proposta padroniza a *página de
confirmação* e não cria modal. Também não entram menu suspenso, notificação flutuante e tema escuro:
nenhuma tela de hoje pede.

### Convenções de partida

São hipóteses úteis, e não limites absolutos. Cada uma admite exceção justificada, e todas esperam o
piloto.

- **Um botão cheio por tela ou por cartão, como regra geral.** O resto é secundário ou discreto. A
  tela com dois gestos de igual peso é exceção legítima.
- **Perigo só no ato irreversível**, e sempre com a marca "Irreversível" ao lado.
- **Caixa dentro de caixa, no máximo um nível.** Dentro de um cartão, separa-se por linha ou por
  espaço.
- **Aviso em bloco, de preferência um por tom, no topo.** O que acompanha um controle é aviso em
  linha. Dois impeditivos distintos continuam sendo dois avisos.
- **Texto explicativo permanente pode ir para o trilho ou para um recolhido.** É a hipótese mais
  sensível: cada frase de tela de operação foi decidida em spec, e recolher muda o que a pessoa lê
  antes do ato. No piloto nada é recolhido nem cortado.
- **Número com rótulo é sempre indicador.** Zero esmaece; o que pede ação fica ativo.

## 5. Padrões de página

| Arquétipo | Rotas | Composição | Cabeçalho | Onde ficam as ações | Referência interna |
|---|---:|---|---|---|---|
| Lista administrativa | 10 | cheia | título e contagem | criar, à direita do título; filtros acima da tabela; ação de linha à direita | Inscrições recebidas |
| Página de entidade | 7 | principal e trilho | título, situação, código | atos da entidade à direita; "o que fazer agora" no topo do principal | Centro de Controle |
| Formulário de configuração | 14 | principal e trilho | título, situação, passos | barra de ações fixa ao pé | assistente de composição |
| Operação com etapas | 10 | principal e trilho | título, recorte em segmentos | o gesto num cartão de destaque; indicadores acima | Corte e progressão |
| Central de trabalho | 8 | cheia, ou principal e trilho | título e filtro de escopo | cada item leva a sua ação | Minhas atividades |
| Avaliação ou conferência | 7 | duas colunas iguais | título e posição na fila | decisão ao pé da ficha; "próxima" no cabeçalho | Mesa de avaliação |
| Confirmação de ato | 35 | centrada | o nome do ato | impede, continua, não se desfaz; primária e "Cancelar" ao pé | Encerrar o Edital |
| Registro e histórico | 12 | cheia, com prosa na medida de leitura | título e período | filtros; sem ação primária | Trilha de auditoria |
| Portal público | 7 | cheia até 76rem | título e situação | a ação de inscrever no cartão da vaga | Página da seleção |
| Jornada do candidato | 13 | centrada | onde estou e o prazo | uma ação grande por tela | Convocação do candidato |
| Acesso | 8 | centrada (portal) ou dividida (gestão) | sem moldura | uma ação | Entrada da gestão |

**Ordem dentro da página**, igual em todos os arquétipos: trilha de navegação, cabeçalho da página,
aviso em bloco (se houver), indicadores (se houver), filtros ou segmentos, conteúdo principal, barra
de ações. O retorno de um gesto ("salvo", "recusado") aparece logo abaixo do cabeçalho, com foco.

**Layouts semelhantes seguem a mesma convenção; layouts diferentes são aceitos quando a tarefa pede.**
A matriz de Alocação e o calendário da Agenda ocupam a página inteira; a Mesa divide a tela ao meio
com o documento. Nenhum deles precisa do trilho.

## 6. Governança

### 6.1 Onde cada coisa mora

| O quê | Onde | Regra |
|---|---|---|
| Tokens | `shared/static/shared/tokens.css` | o único lugar com valor literal de cor, tamanho, espaço, raio e sombra |
| Componentes | `interface/static/interface/gestao/componentes.css`, `formularios.css`, `tabelas.css` | um componente, uma regra-base e variantes por classe |
| Composição de página | `interface/gestao/moldura.css` | as três composições e o cabeçalho de página |
| Parciais | `interface/templates/interface/componentes/` | cabeçalho de página, indicadores, aviso, barra de filtros, barra de ações, estado vazio |
| Estilo de uma tela | `interface/telas/<tela>.css` | só o que é da tela: grade própria, largura de coluna. Nunca cor, fonte, raio ou caixa nova |
| Portal | `portal/static/portal/portal.css` | os mesmos tokens e os mesmos nomes de componente, com `--controle-g` |

### 6.2 Guardiões novos

*Para decidir depois do piloto. Nenhum nasce antes de a escala que ele protege ser confirmada.*

Um guardião protege um contrato que importa e admite exceção justificada. **Contar propriedade de
CSS não garante consistência:** uma folha pode usar só tokens e ainda compor mal a tela. Os testes
abaixo fecham a porta por onde a variação entra; a consistência em si se confere pelo que foi
renderizado (§6.5) e pela revisão de tela nova (§6.4).

O projeto já prova regra de interface por teste. Cinco candidatos, que leem as folhas como texto,
como os que existem:

| Guardião | O que recusa | Lista de exceções |
|---|---|---|
| Cor só por token | `#hex`, `rgb()` e `hsl()` fora de `tokens.css` | sombra em `tokens.css`; impressão |
| Escala de fonte | `font-size` que não seja `var(--t-*)` | impressão (`pt`) |
| Escala de raio | `border-radius` que não seja `var(--raio*)`, `50%` ou `0` | nenhuma |
| Pontos de quebra | `@media` de largura fora dos quatro | começa com as 19 de hoje e só diminui |
| Caixa nova | regra de tela com `border`, `border-radius` e `background` juntos | lista fechada, que só diminui |

Os dois de contrato mais claro são o primeiro, porque a cor literal já produziu a única falha de
contraste medida, e o último, que leva a tela nova a usar `.cartao` ou a pedir exceção por escrito.
Os de fonte e de ponto de quebra dependem de as escalas saírem do piloto como estão.
**Cada guardião nasce com a lista do que existe hoje e proíbe crescer.** É o mesmo desenho do teto
de caracteres da distribuição e da contagem de migrations: a convergência tira itens da lista, e
nada novo entra.

### 6.3 Quando a exceção é justificável

- O conteúdo tem forma própria que nenhum componente descreve: a matriz de alocação, o calendário, o
  visualizador de documento, o mapa de fases.
- A norma exige: o documento oficial e a impressão seguem regra própria.
- A medida prova: um componente não cabe a 375 px e a alternativa foi medida.

Em todos os casos a exceção fica na folha da tela, com comentário que diz por quê, e entra na lista
do guardião.

### 6.4 Revisão de tela nova

Antes do merge, quem escreve a tela responde:

1. Qual é o arquétipo, e qual das três composições ela usa?
2. O cabeçalho é o parcial? As ações estão onde o arquétipo manda?
3. Há algum valor literal na folha da tela? Alguma caixa, botão ou aviso com classe nova?
4. Quantos botões cheios há na tela?
5. Passa a 375, 768, 1280 e 1920 px sem transbordo e sem linha acima de 80 caracteres?

### 6.5 Verificação visual no fluxo de desenvolvimento

O instrumento desta auditoria fica no repositório e serve de verificação contínua. Ele não compara
pixel (duas capturas do mesmo código já diferem); compara **medida**:

- `medicoes/rastrear.py` e `medicoes/larguras.py` percorrem as telas dos cenários de treinamento e
  gravam, por tela, transbordo, linha mais longa, assinaturas de botão, de caixa e de fonte.
- Um alvo novo, `make auditoria-visual`, rodaria os dois num banco de cenários e compararia com o
  `telas.csv` da `main`: a tela que ganhou uma assinatura nova de caixa, um tamanho de fonte fora da
  escala ou um transbordo aparece na diferença.
- Fica fora do `test-pg`, como as jornadas no navegador: pede o grupo `navegador`, e roda sob
  demanda e no PR que toca folha ou template.

Nesta auditoria, as duas passadas levaram alguns minutos para as 131 telas.
