# S-00 — Piloto editorial: o que ficou decidido

**Sessão de 08/09/2026.** Executa `§I.0` do documento de arquitetura
(`doc/manual/00-arquitetura-do-manual.md`, commit `152a57c`). Este relatório é o entregável de
maior valor da sessão: as dezenove sessões seguintes aplicam o que está aqui sem reabrir a
discussão.

**O que a sessão produziu**

| Entregável | Onde |
|---|---|
| Esqueleto HTML provisório navegável | `doc/manual/piloto/` — `manual.css`, `manual.js`, `index.html` |
| C-03 · O ciclo completo em um mapa | `c-03-o-ciclo-em-um-mapa.html` |
| C-12 · Inscrever-se | `c-12-inscrever-se.html` |
| C-18 · Divulgar o resultado | `c-18-divulgar-o-resultado.html` |
| Bloco-espécime de C-08 | `c-08-especimen-desempate.html` |
| 12 capturas de um certame reduzido | `doc/manual/piloto/capturas/` |
| As nove respostas de design | este documento, §1 |
| Revisão do inventário do §F | `doc/manual/01-inventario-de-capturas-revisado.md` |

Os sete callouts do §G.2 foram usados ao menos uma vez cada, em contexto real. As capturas são
descartáveis, inclusive as que ficaram boas.

---

## 1 · As nove respostas

### 1. Qual é a anatomia padrão de uma página?

Ordem fixa, e nenhum elemento troca de lugar entre capítulos: **breadcrumb** → **código e parte** →
**título** → **resumo de duas a três linhas** → **quadro "onde estou"** (só na Parte 2) →
**`👤 Quem faz isto`** → **`🕒 Quando fazer`**, quando houver → **corpo em seções `<h2>`, cada uma
começando por prosa e só depois por passos numerados** → **`✅ Você terminou quando…`** →
**rodapé de progressão** com "Depois disto, normalmente vem…" e os dois vizinhos.

O exemplo é C-18: `Publicar resultado` abre com Paula nomeada e com a pré-condição
("ato de classificação emitido e vigente"), atravessa quatro passos, e fecha com um teste que o
leitor aplica sozinho — abrir a página pública num navegador sem sessão. Um capítulo que não caiba
nessa ordem é sinal de que ele são dois.

### 2. Quanto texto existe entre duas capturas?

**Mínimo 4 linhas, máximo 20.** Abaixo de 4 as duas capturas são a mesma e devem virar uma; acima
de 20 ou falta uma captura, ou sobra explicação que pertence ao bloco "por trás disto".

Dentro de um passo com captura a régua é mais apertada: **uma frase imperativa (1–2 linhas), a
captura, a legenda (1–3 linhas) e o resultado esperado (1–2 linhas)** — entre 3 e 8 linhas de texto
por captura, fora a legenda. O passo 2 de C-18 é o limite superior aceitável; o passo 1 é o
inferior.

Medido nas quatro páginas: 860 a 1 150 palavras por página, 1 a 5 capturas, 3 a 4 passos numerados,
5 a 7 caixas. Daí a segunda régua: **no máximo uma caixa a cada 100 palavras, e nunca duas caixas
seguidas sem texto entre elas.** O piloto violou essa regra uma vez, em C-12 (`⛔` seguido de `⚠️`
logo depois do envio), e a correção foi uma frase-ponte — não a remoção de uma das caixas.

### 3. Quando usar tela inteira e quando usar recorte?

**Recorte, por padrão. Tela inteira só quando o assunto é a tela, e não o que está nela.**

O critério não é o gosto, é este: uma captura mostra **uma** afirmação. Se a legenda precisa de
"e também", é recorte demais. Três casos de tela inteira, e só eles: o comprovante do candidato
(o assunto é o documento inteiro), a página pública do resultado (o assunto é como o público a vê),
e a barra dos nove passos do assistente (o assunto é a barra).

Duas regras de forma que o piloto descobriu na prática:

- **O recorte começa e termina em fronteira de elemento, nunca a N pixels.** A primeira versão da
  captura de recusa de C-18 cortou "Classificação final" ao meio, e uma linha de texto cortada ao
  meio faz o leitor achar que a imagem está quebrada. A faixa de contexto acima é o elemento
  anterior inteiro.
- **O recorte tem uma margem lateral maior do que a inferior.** A lateral é onde os marcadores
  numerados vivem; a inferior só precisa não invadir o elemento seguinte. Em números: 22 px nas
  laterais, 8 px embaixo, e a faixa de contexto acima variando com o elemento.

### 4. Como indicar exatamente onde clicar sem poluir a imagem?

**Retângulo de 2 px na cor de acento, cantos de 3 px, desenhado sobre a imagem por CSS — nunca
gravado no PNG.** A captura permanece legível, o texto permanece pesquisável, e refazer a captura
não obriga a refazer a anotação.

Quatro decisões concretas:

- **A cor de acento é violeta (`#5b3a8f`).** Não é decoração: o produto usa verde para sucesso,
  vermelho para erro e âmbar para aviso, e um retângulo laranja sobre uma faixa vermelha de recusa
  seria lido como parte da tela. O violeta não existe na interface, então nunca é confundido com
  ela. É o mesmo acento do resto do manual — continua sendo **um** acento.
- **Um alvo não recebe número.** Dois ou mais recebem `①②③`, e a legenda os explica em texto.
  A captura da recusa em C-18 tem um alvo e nenhum número; a do critério de desempate tem quatro.
- **Os números seguem a ordem de leitura da imagem — de cima para baixo, da esquerda para a
  direita — e não a ordem de importância na legenda.** A primeira versão da captura da página da
  seleção numerou o PDF como ① e o prazo como ②, com o ② acima do ①, e ficou ilegível. A legenda se
  reescreve; a imagem não.
- **O marcador fica fora do retângulo, acima do canto superior esquerdo.** Encostado no canto, ele
  cobria justamente o primeiro caractere do rótulo que queria apontar.

**E as coordenadas não são estimadas: elas são emitidas pelo próprio script de captura**, a partir
do mesmo DOM que ele recortou, em porcentagem da imagem — o que faz a anotação acompanhar a imagem
em qualquer largura de tela, inclusive quando ela se desloca dentro da moldura em 375 px. Estimar à
mão custou três iterações na primeira captura e zero nas onze seguintes.

### 5. Quais callouts sobrevivem ao uso real?

Os sete sobreviveram, e nenhum ficou sem ocasião. Frequência observada nas quatro páginas:

| Marcador | Usos | Observação |
|---|---|---|
| `👤 Quem faz isto` | 4 — um por página | Confirma a regra "1 por procedimento". Em C-18 ele carrega a segregação de funções, que era conteúdo difícil de colocar em outro lugar |
| `🕒 Quando fazer` | 4 | Aparece duas vezes em C-12, e as duas se justificam: uma é o prazo, outra é a ordem entre escolher modalidade e anexar |
| `💡 Dica` | 5 | O que mais tende a proliferar. Duas das cinco são mitigações de defeito escritas como atalho — ver §2 |
| `⚠️ Atenção` | 5 | Ficou forte porque é raro. Se passar de duas por página, deixa de ser |
| `⛔ Sem retorno` | 3 | Só onde há um dos dez atos. C-08 não tem nenhum, e corretamente não usa |
| `🔎 O que muda depois` | 3 | O mais valioso e o menos óbvio: é ele que carrega "onde o resultado aparece depois" e "ninguém é notificado" |
| `✅ Você terminou quando…` | 4 | Um por página. Só vale se o teste for aplicável sozinho |

**Nenhum oitavo callout faltou, mas faltou um bloco.** Uma capacidade que o sistema oferece e que
não deve ser usada — o caso de `H.2` em C-19 — não é um ato irreversível, e usar `⛔` para as duas
coisas apagaria a única distinção que se pede ao leitor que memorize. Ela ganhou **bloco próprio**,
`Limitação conhecida desta versão`, sem marcador emoji, da mesma família visual de "por trás disto".
Isso **acrescenta um componente ao §G.3; não acrescenta um oitavo callout ao §G.2.** A forma está
fixada e demonstrada na home do piloto, com o texto real que C-19 vai usar.

### 6. Como representar "onde estou no processo"?

**Uma faixa de dezesseis traços, um por fase, com o traço atual mais alto e na cor de acento**, e
acima dela uma linha em texto: `Fase 11 de 16 · Divulgar · o trabalho é do publicador`. Nas pontas,
`1 · Abrir` e `16 · Encerrar`.

Entra **logo abaixo do resumo e antes do primeiro callout**, só nos capítulos da Parte 2. A Parte 1
não a usa: C-03 **é** a linha do tempo inteira, e repeti-la ali seria redundante.

A forma reduzida é texto mais barra, e não dezesseis rótulos, por uma razão medida: dezesseis
rótulos legíveis não cabem em 375 px sem rolagem horizontal, e o quadro que se repete no manual
inteiro é o último lugar onde se pode pedir ao leitor que role de lado. A barra é gerada por
`manual.js` a partir de um único atributo (`data-fase="11"`), o que garante que as dezesseis fases
tenham o mesmo nome em vinte capítulos.

### 7. O tom está simples sem ficar infantil?

Está, e a diferença é uma decisão de cada frase. O teste que aplico: **a frase explica um mecanismo
ou tranquiliza o leitor?** Se tranquiliza sem explicar, é infantil.

Antes e depois, de C-18:

> **Antes** — "Não se preocupe! Se algo mudar enquanto você estiver na tela, o sistema vai avisar
> e você pode tentar de novo. 😊"
>
> **Depois** — "A prévia envelhece: se algo mudar entre abrir e confirmar, a confirmação é recusada
> — e isso é proteção, não erro. Abra a prévia de novo, releia e confirme."

O segundo é mais curto, não usa emoji no corpo, nomeia o mecanismo ("a prévia envelhece"), diz o que
fazer, e trata a recusa como uma decisão do sistema e não como um contratempo. É o mesmo movimento
em toda parte: **nomear a regra, dizer o efeito, dar a saída.** Emoji só como marcador de caixa;
ponto de exclamação em nenhum lugar; nada de "simplesmente", "basta", "é só".

O segundo teste é o inverso, contra o tom burocrático: **nenhum identificador técnico no corpo.**
Onde a tela mostra um resumo criptográfico, o manual escreve "é o registro técnico que permite
provar depois que o arquivo não foi trocado. Você não precisa dele para nada — guarde o protocolo".

### 8. Como a página se comporta em desktop e em 375 px?

**Reflui:** o menu lateral vira um cabeçalho com o botão `Sumário do manual`, que expande e recolhe;
as duas portas da home empilham; o rodapé de progressão empilha; o corpo cai de 17 px para 16 px e a
coluna passa a ocupar a largura toda com 1,25 rem de respiro.

**Rola dentro da própria caixa, nunca a página:** tabelas largas e capturas de tela larga. Este foi o
achado que mais mudou o esqueleto. Uma captura de 1 264 px reduzida para 327 px fica com texto de
tela a 4 px — ilegível, e a legenda passa a ser a única coisa que ensina. Em vez de encolhê-la, ela
**mantém o tamanho e se desloca dentro da moldura**, com a legenda dizendo "Arraste a imagem para o
lado para ler a tela inteira" — e a anotação vai junto, porque está posicionada em porcentagem da
imagem, e não da moldura. Duas páginas estouravam a largura em 375 px por causa das tabelas; a
correção foi `min-width: 0` nos filhos do grid, sem a qual `overflow-x: auto` não contém nada.

**Some:** nada. Nenhum conteúdo é escondido em tela estreita — o que não cabe, desloca-se.

**Fica melhor no celular:** as capturas `mobile 375`, que ganham moldura estreita própria e são
mostradas em tamanho real.

### 9. C-08 continua compreensível na configuração mais densa?

Sim, com duas condições que o espécime demonstrou.

A primeira é **prosa antes de procedimento**. O bloco não abre pelos passos: abre por "O que um
critério de desempate é", que gasta um parágrafo dizendo que o sistema aplica os critérios na ordem
declarada e três marcadores dizendo o que um critério precisa declarar. Sem isso, os quatro campos
da tela são quatro campos; com isso, são a regra que já foi explicada. Os passos ficaram curtos
justamente porque a explicação saiu deles.

A segunda é que **a captura densa precisa de marcadores numerados, não de uma legenda corrida**. O
cartão do critério tem quatro campos e cada um significa uma coisa diferente; `①②③④` com a legenda
explicando cada um é o que evita a legenda-parágrafo que ninguém lê. Foi a única das doze capturas
que precisou de quatro alvos, e é por isso que ela estava no piloto.

O que o espécime também mostrou, e vale para S-07: **onde uma tabela diz melhor, a tabela fica e a
captura encolhe.** Os três critérios gravados aparecem numa captura alta — que rola dentro da
moldura — e logo abaixo numa tabela de quatro colunas. A tabela é a que ensina; a captura só prova
que a tela é aquela. Se S-07 precisar cortar, corta a captura, não a tabela.

---

## 2 · Decisões registradas, inclusive as que contrariam a arquitetura

| # | Decisão | Contraria §? | O que fazer com o documento de arquitetura |
|---|---|---|---|
| D-1 | O acento único do manual é **violeta `#5b3a8f`**, e é o mesmo da anotação de captura | não | registrar em §G.1 |
| D-2 | A anotação é **CSS sobre a imagem**, e as coordenadas são **emitidas pelo script de captura** em porcentagem | complementa §G.6 | acrescentar a §G.6 |
| D-3 | Marcadores numerados seguem a **ordem de leitura da imagem** | complementa §G.6 | acrescentar a §G.6 |
| D-4 | Captura de tela larga **desloca-se dentro da moldura** em 375 px em vez de encolher | complementa §G.6 | acrescentar a §G.6 |
| D-5 | Novo componente **`Limitação conhecida desta versão`**, sem emoji, para a capacidade que não deve ser usada. `⛔` continua reservado a ato irreversível | **acrescenta a §G.3**; preserva §G.2 | acrescentar a §G.3 e ajustar a ficha de C-19 em §C.bis |
| D-6 | O quadro "onde estou" é **barra de 16 traços + uma linha de texto**, gerado de `data-fase` | detalha §G.5 | acrescentar a §G.5 |
| D-7 | Capturas de gestão são tiradas a **1 000 px** de viewport, não 1 280 | **contraria §F.2** | corrigir §F.2 |
| D-8 | **Não existe tela de "Criar Edital"** separada: o Processo nasce com o primeiro Edital, e acrescentar um segundo só existe na API | **contraria §C.bis C-06 e §F (SS-010)** | corrigir a ficha de C-06 e o inventário; acrescentar o fato a `G-03` |
| D-9 | `seed_demo` **não produz o certame do §F.1** e sua elenco colide com o dos personagens | complementa §F.1 | acrescentar a nota de preparação do §F.1 |
| D-10 | A régua de densidade e a de caixas (§1.2) passam a ser critério de revisão de cada capítulo | novo | acrescentar a §G |

### Sobre D-8, que é o achado de produto da sessão

A interface de gestão cria um Processo Seletivo **junto com o seu primeiro Edital**, numa tela só
(`/gestao/processos/criar`, botão `Criar Processo e Edital`). Acrescentar um segundo Edital a um
Processo existente é capacidade que existe no domínio e na API, e **não tem tela**: não há rota, não
há ação no detalhe do Processo, não há botão. A ficha de C-06 em `§C.bis` promete ensinar "um
Processo com vários Editais" e lista uma captura `SS-010 · Criar Edital` que não existe como tela
separada.

Encaminhamento, pela regra do §H.0: o fato **não muda o que o leitor deve fazer agora** — ele cria o
Processo e o Edital de uma vez, e a tela o conduz. Logo, **não é alerta inline**: vai para `G-03`,
em uma linha, junto das outras capacidades sem tela do `H.14`. C-06 passa a ensinar a tela como ela
é, sem prometer o que ela não faz.

**Isto é registro, não decisão de governança.** Se a instituição precisa de dois Editais no mesmo
Processo pela interface, isso é decisão do produto e do usuário — não escopo da produção do manual.

---

## 3 · Como o certame do piloto foi montado

Registrado porque S-01 vai precisar de metade disto, e a outra metade é o que **não** funcionou.

- **Entrada no `.claude/launch.json`**: `manual-s00`, porta 8033, banco `ps_manual_s00` exclusivo,
  `INTERFACE_SELETOR_IDENTIDADE=true`, `LC_ALL=en_US.UTF-8`, `DB_USER`.
- **Correio local**: `DJANGO_EMAIL_BACKEND=…smtp.EmailBackend` apontando para uma caixa de correio
  local na porta 1035. O mecanismo padrão (`console`) imprime o código de acesso no terminal do
  servidor, de onde um roteiro de captura não consegue lê-lo. **Sem isso a jornada do candidato não
  se automatiza** — e ela é 11 das 88 capturas.
- **Captura**: Chrome sem interface, dirigido por CDP, com `deviceScaleFactor: 2`. O roteiro navega,
  preenche, envia arquivo, recorta por seletor e **emite as coordenadas da anotação**. Os arquivos
  saem a 2× e são reduzidos à metade depois — 12 capturas ocupam 2,3 MB.
- **Identidades**: o seletor aceita nome livre, então os personagens do §F.1 são reproduzíveis um a
  um. O Edital do piloto foi publicado por **três pessoas distintas** — Elena submete, Wagner
  homologa, Paula publica —, o que confirma que a segregação do §A.3 é percorrível na interface.
- **Limite de solicitação de código**: pedir um novo código para o mesmo e-mail é recusado por
  cerca de um minuto. Um roteiro de captura precisa pedir **uma vez por candidato** e seguir sem
  reiniciar o navegador, ou usar um e-mail por tentativa.

