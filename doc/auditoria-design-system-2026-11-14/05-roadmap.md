# F. Plano de convergência

*Proposta de sequência. Nada aqui foi iniciado: cada frente vira spec própria depois da decisão sobre
a direção visual. O piloto, os critérios de aceite e as decisões foram reescritos em duas rodadas
de revisão, em 14/11 ([registro](06-revisao.md)).*

Esforço relativo: **P** cabe numa sessão, **M** numa spec de alguns dias, **G** pede mais de uma
spec. O alcance é em rotas que rendem tela (135 no total).

## O menor conjunto com o maior avanço

Seis mudanças explicam a maior parte da fragmentação medida, e nenhuma delas é de uma tela só:

| # | Mudança | Resolve | Alcance |
|---|---|---|---|
| 1 | Tokens de escala (fonte, espaço, raio, controle) e os neutros num lugar só | S3, S7, S11 | todas |
| 2 | Parcial de cabeçalho de página | S1 | 89 telas da gestão |
| 3 | Três composições de página: cheia, com trilho, centrada | S2 | todas |
| 4 | `.acao` com altura única, e uma barra de ações | S5 | cerca de 40 telas; global, só depois do piloto |
| 5 | Indicador e aviso como componentes | S4, S6 | cerca de 45 telas |
| 6 | Contratos de componente, com os guardiões que o piloto justificar | dificulta a volta | todas as futuras |

## P0. Correções críticas

Independem da direção visual. **São uma entrega própria, anterior ao piloto, e não parte dele:**
mexem na Visão Geral e em avisos de telas que o piloto não toca, e a P0.3 mexe na própria
confirmação de ato, que é tela do piloto. Juntas com o piloto, contradiriam o critério de que nada
fora dele muda.

| Item | O que é | Evidência | Esf. | Risco |
|---|---|---|---|---|
| P0.1 | Visão Geral: contraste abaixo de 4,5:1 em 155 trechos | S7, E1 | P | baixo: trocar a paleta local pelos tokens |
| P0.2 | Visão Geral: transbordo a 768 px | S8, E1 | P | baixo: usar a moldura comum de tabela |
| P0.3 | Confirmação de ato irreversível com linha de 176 caracteres em monitor largo | S2, E8 | P | baixo: medida de leitura nos blocos de consequência |
| P0.4 | Aviso que só se distingue pela cor | S6 | P | baixo: marca de espécie no texto ("Atenção", "Impede") onde ainda não há |

**Critério de aceite:** `telas.csv` regenerado mostra zero trecho abaixo do contraste na Visão Geral,
zero transbordo a 768 px e nenhuma linha acima de 100 caracteres nas confirmações; a suíte fecha
verde.

**Ao fim da P0, o instrumento roda de novo e o resultado vira a referência do piloto**: um
`telas.csv` e um conjunto de capturas tirados depois do merge das correções, no mesmo banco de
cenários. É contra essa referência, e não contra as medidas de 14/11, que o piloto se compara.

## P1. Padrões estruturais

A fundação. **Dois itens mudam telas que não os adotam**, e por isso não entram no piloto na forma
global: o P1.4, que altera `.acao` em cerca de 40 telas, e o P1.1 na variante que aponta os tokens
antigos para os novos. No piloto, os dois valem só dentro das telas escolhidas (ver *O piloto*).

| Item | O que é | Depende de | Esf. | Risco |
|---|---|---|---|---|
| P1.1 | Tokens: os 14 de `acesso.css` sobem para `tokens.css`; entram as escalas `--t-*`, `--e-*`, `--raio*`, `--controle*` e o `--azul` | decisão 1 | P | baixo: só acrescenta |
| P1.2 | Parcial `_cabecalho_da_pagina.html` e a regra `.cabecalho-da-pagina` | P1.1 | M | baixo |
| P1.3 | Composições `.com-trilho` e `.centrada` em `moldura.css`; `--formulario`, `--trilho`, `--coluna` | P1.1 | M | médio: `test_larguras.py` aprende as medidas novas |
| P1.4 | `.acao` com 32 px e `line-height` fixo; `.botao.discreto`; `.barra-de-acoes` | P1.1 | P | médio: na forma global muda 1 a 5 px em cerca de 40 telas, e só entra depois do piloto, com captura de todas |
| P1.5 | `.indicador` e `.indicadores`; `.aviso` com quatro tons e ícone | P1.1 | M | baixo |
| P1.6 | Guardiões dos contratos confirmados, cada um com a lista do que existe hoje | o piloto | M | baixo: nascem verdes; quais nascem é decisão posterior ao piloto |
| P1.7 | Instrumento de medida como alvo do `Makefile` | nenhuma | P | nenhum |

**Decisão embutida em P1.1.** Subir os neutros da entrada para oficiais pode ser feito de dois
jeitos: *acrescentar* os tokens e deixar `--texto`, `--borda` e `--fundo` como estão (nenhuma tela
muda), ou *apontar* os antigos para os novos (todas as telas mudam um pouco, de uma vez). A
recomendação é acrescentar no piloto e apontar no começo da P2, com captura de todas as telas antes
e depois.

## P2. Convergência das telas

Por arquétipo, e não por tela: cada família é uma spec. **Só começa depois do piloto**, e com o que
ele confirmar: as hipóteses que não passarem saem deste plano. Onde houver guardião, a família
termina tirando itens da lista dele. A ordem vai do maior alcance com menor risco para o contrário.

| Ordem | Família | Rotas | O que muda | Esf. | Risco |
|---|---|---:|---|---|---|
| P2.1 | Confirmação de ato | 35 | página centrada, um aviso por tom, barra de ações | M | baixo: poucos templates servem muitas rotas |
| P2.2 | Lista administrativa, registro e histórico | 22 | cabeçalho, barra de filtros, tabela em cartão, moldura única | M | baixo |
| P2.3 | Jornada do candidato e portal público | 20 | página centrada, alturas de controle, envio de arquivo | M | médio: scripts do portal e impressão do comprovante |
| P2.4 | Formulário de configuração | 14 | passos, grade de campos, trilho de apoio, barra de ações fixa | G | médio: os guardiões do assistente leem os templates |
| P2.5 | Central de trabalho e página de entidade | 15 | cabeçalho, indicadores, trilho; Lista de Processos em tabela | M | médio: orçamento de consulta da lista |
| P2.6 | Operação com etapas, avaliação e conferência | 17 | indicadores, gesto em destaque, contexto no trilho | G | alto: texto e ordem fixados em spec; uma spec por tela |

O Centro de Controle e a Página do Processo entram na P2.5 só com a troca de tokens: são as
referências, e a composição delas fica.

As 12 rotas restantes: o acesso (8) é referência e só recebe os tokens; os dois relatórios seguem
a P2.2; o guia incorporado está na P3.5.

## P3. Refinamento

| Item | O que é | Esf. |
|---|---|---|
| P3.1 | Um conjunto de ícones; saída gradual dos glifos de texto | M |
| P3.2 | Fonte embarcada, se a decisão 3 for por ela | P |
| P3.3 | Estados vazios com a ação seguinte | P |
| P3.4 | Transição de cor e de borda nos controles | P |
| P3.5 | Guia incorporado (Documentação do Sistema) com os tokens | M |
| P3.6 | Folha de impressão revista contra a nova escala | P |

## O piloto

**Recomendação: três telas, com o estilo novo delimitado a elas, depois da P0 e da nova
referência.** A ordem é: correções críticas, medição de referência, piloto. O piloto existe para
responder a uma pergunta que o estudo deixou aberta: com o mesmo conteúdo e o
mesmo comportamento, a composição nova opera melhor?

### O que entra, e como fica delimitado

| Item | No piloto | Fora do piloto |
|---|---|---|
| P0 | não: é a entrega anterior, já na `main` quando o piloto começa | entrega própria |
| P1.1 Tokens | os novos são **acrescentados**; `--texto`, `--borda` e `--fundo` ficam como estão | apontar os antigos para os novos |
| P1.2 Cabeçalho de página | nas três telas | nas demais |
| P1.3 Composições | nas três telas | nas demais |
| P1.4 Botão | a altura única e a barra de ações, **só dentro do escopo do piloto** | a mudança global de `.acao` |
| P1.5 Indicador e aviso | nas três telas | nas demais |
| P1.6 Guardiões | nenhum guardião novo; o piloto entrega o levantamento do que cada um protegeria | todos |
| Redução tipográfica | não: as telas mantêm os tamanhos de hoje | decisão posterior |
| Recolher ou cortar texto | não: todo texto continua visível e igual | decisão posterior |

**A delimitação é por construção, e não por cuidado.** As regras novas moram numa folha de grupo
(`interface/grupos/`), carregada só pelas telas do piloto pelo bloco `estilo_da_pagina`, que é o
mecanismo que o produto já usa para estilo de grupo de telas. Todas as regras ficam sob uma classe
de escopo, num contêiner que envolve o conteúdo das três telas; o `main` da base não tem bloco de
classe, e a base não precisa mudar. Nenhuma regra de `componentes.css`, `formularios.css` ou
`telas.css` muda de valor. Assim o `.acao` das outras telas não se altera, e o critério "nada fora
do piloto muda" deixa de contradizer o item P1.4.

### As três telas, e os estados que cada uma precisa cobrir

| Tela | Por quê | Estados a cobrir |
|---|---|---|
| **Confirmação de ato do Edital** (`confirmar.html`) | um template serve seis rotas: submeter, homologar, devolver, publicar, encerrar e cancelar. Prova a página centrada, o aviso e a barra de ações | cada um dos seis atos; com e sem impedimento; com e sem o que "continua depois"; recusa de validação (motivo vazio), com o foco na recusa |
| **Ocupação de vagas** | prova o indicador e o trilho numa tela de operação de tamanho médio | ver abaixo |
| **Lista de Processos Seletivos**, sem a coluna nova | é a porta de entrada: prova o cabeçalho de página e a tabela em cartão, e todo perfil vê | cada aba; busca com e sem resultado; lista vazia; paginação; Processo com um e com vários Editais; com e sem o painel de ações; quem preside e quem não preside |

**A Ocupação pratica atos, ao contrário do que a primeira versão deste plano dizia.** A tela tem
sete formulários de operação: apurar a ocupação, emitir nova apuração (a sucessão, com motivo),
pedir a faixa seguinte, conferir o acréscimo de vaga, conferir o desfazimento dele, declarar a vaga
não preenchida e desfazer essa declaração. Os dois últimos estão na parcial
`_situacao_da_vaga.html`, e a versão anterior deste plano contava cinco. O piloto precisa cobrir,
por recorte:

- sem quadro de vagas; não apurado, com e sem ordem emitida; recorte sem inscrito;
- apuração vigente, com e sem vaga a ocupar; apuração obsoleta, com a sucessão aberta;
- com vagas acrescidas e com movimento de vaga entre recortes;
- a vaga sem quem a ocupe: o Edital silente, a declaração de não preenchida e a que não se desfaz;
- o marco intermediário, que não apura; e o próximo passo depois de um ato;
- a recusa de cada gesto e o retorno de sucesso de cada um;
- quem pode emitir e quem só lê.

**O levantamento das fixtures foi feito** ([07-fixtures-da-ocupacao.md](07-fixtures-da-ocupacao.md)):
a suíte já desenha 51 dos 63 ramos visíveis da tela, em 54 testes, e todos os estados desta lista
têm teste de tela que os monta. As ressalvas são a apuração obsoleta, desenhada por uma só das sete
causas, e o recorte sem quadro, desenhado só para quem não retifica. Dos 12 ramos sem teste de
tela, 7 já são montados em teste de domínio. O custo que sobra é fotografar: as fixtures vivem no
banco de teste, nenhuma jornada de `tests/navegador/` passa pela Ocupação, e os cenários de
treinamento chegam a um estado só. A spec do piloto decide também se as duas telas de conferência
(`ocupacao_acrescimo.html` e `ocupacao_nao_preenchida.html`) entram.

A alternativa continua sendo o Histórico da ocupação ou o Corte histórico, que só leem e não
testam indicador, contexto e ação juntos. Com o levantamento em mãos, a escolha é do usuário
(decisão 2).

Ficam de fora do piloto, de propósito: a Convocação (risco de domínio), o assistente (muitos
guardiões) e o portal (scripts próprios). Entram na P2, cada um com a sua spec.

### A primeira comparação

Antes de qualquer conclusão, cada tela do piloto é comparada consigo mesma em condição equivalente:

- o mesmo estado, no mesmo banco, com os mesmos registros;
- o mesmo papel e as mesmas permissões;
- **os mesmos textos, por inteiro e visíveis**: nada recolhido, nada resumido, nada movido para
  dentro de um `details`. O que pode mudar é a posição de um bloco na página;
- os mesmos links, formulários, nomes de campo e destinos.

Só a composição muda: posição, agrupamento, componente e cor. Com isso, o que a medida mostrar é do
design, e não de conteúdo cortado.

### Critérios de aceite do piloto

1. **Nada fora do piloto muda.** Garantido pelo escopo, e conferido contra a referência tirada
   depois da P0: no `telas.csv`, só as linhas das telas do piloto têm diferença; as capturas das
   demais são conferidas por amostra de 20.
2. **Conteúdo e comportamento preservados, sem exigir a mesma sequência.** Comparar o texto do
   `main` como uma sequência única reprovaria a mudança de posição, que é o que o piloto existe para
   testar. O que se confere, em cada estado, é:
   - *textos:* todo bloco de texto visível antes existe depois, com as mesmas palavras; nenhum
     bloco novo aparece. A comparação é de conjunto, bloco a bloco, e não de ordem;
   - *quantidades:* todo número exibido antes aparece depois, com o mesmo rótulo;
   - *associações:* cada rótulo continua junto do seu valor, cada campo junto da sua ajuda e da sua
     recusa, cada aviso junto do controle ou do bloco a que se refere;
   - *ações:* a lista de destinos de link e de formulário, por papel, com os mesmos nomes de campo,
     é idêntica (lida pelo cliente de teste, como na `057`). Nenhum texto de ato muda.
3. **Ordem conferida à parte.** Antes de implementar, a spec de cada tela declara as sequências que
   não podem se inverter, e o aceite as confere na ordem do documento, que é a que o teclado e o
   leitor de tela seguem, e na ordem visual. No mínimo:
   - o fundamento vem antes da consequência, e a consequência antes da confirmação;
   - o que impede vem antes do que só informa;
   - a condição de um gesto vem antes do botão que o pratica;
   - a recusa aparece antes do formulário a que se refere.

   Fora dessas sequências, a ordem pode mudar, e a mudança fica registrada na comparação.
4. **Estados cobertos.** Cada estado da tabela acima foi aberto antes e depois, inclusive a recusa e
   o retorno de sucesso.
5. **Acessibilidade conferida à mão**, além do instrumento:
   - teclado: ordem de tabulação igual à ordem visual, todo controle alcançável, nada preso;
   - foco: visível em todo controle, e não coberto pela barra de ações fixa;
   - zoom de 200% e de 400%, e largura de 320 px, sem perda de conteúdo nem rolagem em dois eixos;
   - erro: a recusa recebe o foco, cita o campo, e o campo aponta para ela;
   - rótulo: visível e associado em todo campo, conferido no navegador, e não só pela presença de
     atributo;
   - leitor de tela, se houver quem possa conferir.
6. **Legibilidade e localização da ação**, no lugar da meta de ocupação da largura:
   - nenhuma linha de prosa acima de 80 caracteres;
   - quando o estado tem ação principal, ela aparece sem rolagem a 1280 × 800, ou a tela diz acima
     da dobra que ela existe;
   - o dado de que a ação depende fica à vista junto dela;
   - no celular, pendência e ajuda de preenchimento aparecem antes da ação de avançar.

   A ocupação da metade direita é registrada como diagnóstico, **sem valor de aprovação**.
7. **Suíte e `lint` verdes**, com os guardiões que já existem intactos. Nenhum guardião novo é
   exigido.
8. **Leitura com a equipe.** Duas ou três pessoas da equipe de seleção fazem as mesmas tarefas nas
   telas antigas e nas novas: achar a ação principal, dizer o que acontece ao confirmar, localizar
   um número. Fica registrado o que cada uma disse. É conferência, e não teste formal.

### O que o piloto devolve para decisão

| Hipótese | Como o piloto a informa |
|---|---|
| Redução tipográfica (seis tamanhos, tabela em 14 px) | não informa, a menos que o experimento opcional abaixo seja feito |
| Recolher e deslocar explicações | a equipe diz o que lê e o que pula; nada é recolhido antes disso |
| Um botão cheio por tela | os estados da Ocupação e da confirmação mostram se a regra cabe |
| Um aviso por tom | a confirmação com vários impedimentos mostra se cabe |
| Quatro pontos de quebra | as três telas dizem se quebram nos quatro |
| Trilho no celular | a ordem no estreito é decidida tela a tela |
| Guardiões novos | o levantamento diz quais contratos valem proteger, e com que exceções |

### Experimento opcional: a escala tipográfica

**Fica fora do piloto e fora do aceite.** O piloto mantém os tamanhos de hoje, e nenhum critério
acima depende de tipografia.

Se o usuário quiser adiantar a decisão 4, dá para montar, depois do aceite do piloto, uma variante
das três telas com a escala proposta e mostrá-la à equipe ao lado da versão aceita. É uma
comparação à parte, com resultado próprio, que não entra na `main` e não altera o que foi aceito.
Sem esse experimento, a redução tipográfica fica inteira para depois, com spec própria.

## Riscos que valem para todas as frentes

| Risco | De onde vem | Como tratar |
|---|---|---|
| Guardião que lê a folha como texto | 34 arquivos de teste leem CSS; renomear classe ou mover regra reprova | manter os nomes; mudar valor, e não seletor; rodar o diretório `tests/interface` a cada passo |
| Classe citada sem regra | `test_nenhuma_classe_citada_deixa_de_existir_na_folha` | toda classe nova nasce com regra, no mesmo commit |
| Texto fixado em spec | cada frase de tela de operação tem FR | o design move e recolhe; não reescreve. Corte de texto é spec |
| Script que depende de classe | `rascunho.js`, `remocao.js`, `visualizador.js`, `envio.js` selecionam por classe | conferir os seletores antes de mexer no template; os testes de `tests/javascript` cobrem |
| Teto de caracteres da Distribuição | a página tem limite provado por teste | parcial novo não pode engordar o HTML repetido por linha |
| Orçamento de consulta | a lista e o Centro têm teto de consultas | componente novo não lê banco |
| Política de conteúdo | sem `style=` e sem `<style>` | largura e altura dinâmicas continuam por classe (`altura-N`) |
| Impressão | o comprovante e o resultado têm folha de impressão | conferir a impressão em toda família do portal |
| Várias sessões na mesma folha | frentes paralelas tocando `componentes.css` | uma família por vez, em série |
| Estilo do piloto vazando | regra nova escrita fora da classe de escopo | folha de grupo própria; o critério 1 do piloto acusa pelo `telas.csv` |
| Reorganizar e perder sentido | um bloco muda de lugar e deixa de anteceder o que explicava | as sequências que não se invertem são declaradas na spec e conferidas no critério 3 |
| Otimizar a medida, e não a tela | tratar ocupação de largura ou contagem de regra como meta | os números são diagnóstico; a aprovação é por conteúdo equivalente, acessibilidade conferida e leitura da equipe |

## Decisões que ficam com o usuário

A revisão de 14/11 recomenda dividir as decisões em duas levas. A recomendação é de quem revisou; a
decisão continua sendo do usuário.

**Agora, para começar o piloto:**

1. **Direção experimental.** Os neutros da tela de entrada, a hierarquia (cabeçalho de página e
   composições) e os componentes (botão, indicador, aviso, cartão) valem como experimento, só nas
   telas do piloto?
2. **Piloto.** As três telas propostas, com os estados listados? O segundo parecer recomenda manter
   a Ocupação, porque ela testa indicadores, contexto e ações em condições que uma tela de
   histórico não testa. O levantamento que ele pedia está em
   [07-fixtures-da-ocupacao.md](07-fixtures-da-ocupacao.md): a suíte já monta os estados listados,
   e o custo que sobra é fotografá-los.
3. **Fonte.** A pilha do sistema, declarada como a fonte do produto, ou Open Sans embarcada? Pode
   esperar, se o piloto mantiver a pilha de hoje.

**Depois do piloto, com o que a equipe disser:**

4. **Redução tipográfica.** Seis tamanhos, e a tabela em 14 px (hoje 15). O experimento opcional
   pode adiantar a evidência; a decisão é posterior de qualquer modo.
5. **Texto explicativo.** Recolher ou deslocar os parágrafos permanentes das telas de operação. Cada
   caso vira item de spec.
6. **Limites.** Um botão cheio por tela, um aviso por tom, quatro pontos de quebra, um nível de
   caixa: quais viram regra, e com que exceções.
7. **Guardiões.** Quais contratos ganham teste.
8. **Neutros.** Apontar os tokens antigos para os novos, o que muda todas as telas de uma vez.
9. **"Fase e próximo passo" na Lista de Processos.** É informação nova na listagem.

## Como medir o avanço

O critério do pedido, navegar por dez telas e sentir o mesmo produto, se acompanha com o que já está
medido. **Os números abaixo descrevem variação. Reduzi-los não é o objetivo, e nenhum deles prova,
sozinho, que a tela ficou melhor de usar:** a prova é a do piloto, com conteúdo equivalente e com a
equipe. Os alvos das escalas ficam em aberto até o piloto.

| Indicador | Hoje | Depois da P2 |
|---|---:|---|
| Aberturas de página distintas (gestão) | 71 em 89 | uma por arquétipo, cerca de 11 |
| Regras de caixa nas folhas | 63 | muito menos; o número sai do contrato do cartão |
| Regras de faixa de aviso | 28 | as variantes do componente de aviso |
| Alturas do `.acao` | 4 | 1 |
| Cores literais fora dos tokens | 41 | 0 |
| Telas com contraste baixo detectado | 1 | 0, com conferência manual |
| Tamanhos de fonte com mais de 1% do texto | 11 | a decidir depois do piloto |
| Condições de `@media` | 19 | a decidir depois do piloto |
| Metade direita ocupada, mediana a 1440 px | 27% | acompanhada como diagnóstico, sem meta |
| Classes de uma tela só | 576 de 1.214 | em queda a cada família |
