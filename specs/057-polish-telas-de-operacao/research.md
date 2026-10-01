# Research: Polish das telas de operação

As decisões desta feature. As nove que o prompt trouxe fechadas são **entrada**: entram como
recebidas, e não como perguntas a reabrir. As que esta sessão tomou nascem em `D-001`.

## Decisões recebidas (do prompt)

| | Decisão | Critério |
|---|---|---|
| 1ª | Escopo: T1, T2, T3, T4, D2, D5 e F8. D3 não entra (é do título do `seed_demo`) | Está na lista? Entra. Não está? É registro |
| 2ª | Nenhuma ação acrescentada nem removida, nenhuma permissão mudada | A lista de `href` e `formaction` de ações, por papel, é idêntica antes e depois |
| 3ª | T2: uma primária por estado; secundárias em linha; Encerrar e Cancelar separados, por último, contornados, com "IRREVERSÍVEL"; colunas pelo topo | Nenhuma tela com destrutivo preenchido ao lado de ação não destrutiva; "Quem atuou" na altura do conteúdo |
| 4ª | T1: a mesma regra, em linha; rótulo encurta só se nenhum teste o prender; contador zero esmaecido | Linha da Lista de 125 para ≤ 90 px a 1280 px |
| 5ª | D2: glossário num `details` fechado no padrão `como-preencher`, nos templates de marco e no de matrículas; `compor_perfis.html` fica; a faixa "não pratica nada" fica visível; o texto não muda | Primeiro controle ou tabela sobe ≥ 120 px; `test_vocabulario_da_composicao` verde |
| 6ª | T3: "Atenção" em lista com divisor e faixa âmbar; Auditoria em lista de eventos; documentos da inscrição no desenho da mesa; fichas na largura do conteúdo | Auditoria do 51/2026 com ≤ 70 px por evento (antes 97); nenhuma caixa com borda dentro de outra |
| 7ª | F8: `pontuacao` e `plural`; dd/mm/aaaa; só texto composto para a tela | Revisão do 76/2027 com "Peso: 2", "Nota mínima: 6", "20%", "versão 09/06/2014", "2 vagas imediatas"; POST das etapas idêntico |
| 8ª | T4: sem rolagem interna em tela larga, cabeçalho fixo; Edital como linha de grupo, controles compactos | Página de 1.398 para ≤ 1.280 px; `thead` de 174 para ≤ 130 px |
| 9ª | D5: seletor, nome do arquivo e "Enviar" numa linha; dica junto do seletor; scripts inalterados | Uma linha de controles a 1280 px; a 375 px pode quebrar |

---

## D-001 — O orçamento de caracteres já tem margem

**Decisão**: a conversão dos comentários documentais da folha da gestão para `{% comment %}` **já
está na `main`** (`1c4ae6c4`, na `056`), e por isso não é tarefa deste lote. A folha tem um único
`/* */` restante, de 5 caracteres, dentro de uma frase de comentário do template — não é regra
desativada, e fica.

**Rationale**: o prompt mandava fazer a conversão como primeira tarefa "se ainda não estiver na
`main`". Está. A distribuição foi medida antes de qualquer mudança (ver
[verificacao.md](verificacao.md)), e a margem passa de 30.000 caracteres.

**Alternativas**: refazer a conversão — não há o que converter.

## D-002 — A ação principal é escolhida por uma função, e não pelo template

**Decisão**: `acoes.py` ganha uma função pura, `hierarquia(conjunto)`, que reparte o conjunto que
`do_edital` já monta em três partes: a **principal**, as **secundárias** e as **terminais**
(Encerrar e Cancelar). A principal é, nesta ordem de preferência: a ação de elaborar; o ato que
avança o Edital (`submeter`, `homologar`, `publicar`); e "Inscrições recebidas". Se a preferida
existe mas está **indisponível**, ela continua no lugar dela, desabilitada, e nenhuma outra é
promovida (FR-1045). O conjunto, a ordem relativa das secundárias, os rótulos e os destinos não
mudam.

**Rationale**: o template não deveria decidir o que é "o próximo passo"; a lista e o detalhe
precisam da mesma resposta, e a `acoes.py` existe justamente para ser o lugar único dessa pergunta
(o achado 08 que a criou). Devolver e Revogar homologação são retrocessos, e por isso não entram na
preferência.

**Alternativas**: mudar o `estilo` de cada `Acao` em `do_edital` — afetaria a Lista, que desenha
ações de linha, e testes que leem o estilo; promover a próxima disponível quando a preferida está
impedida — faria "Visualizar Edital" parecer o próximo passo de um Edital homologado que espera
outra pessoa para publicar, que é exatamente a leitura que o motivo ao lado desmente.

## D-003 — As terminais são contornadas em vermelho, só no grupo

**Decisão**: Encerrar e Cancelar vão num grupo próprio, depois de um filete, e o desenho
contornado em vermelho vale **dentro do grupo** (`.terminais`), e não para todo `.botao.perigoso`. As
telas de confirmação — onde o botão destrutivo é a ação que a pessoa veio praticar — ficam como
estão.

**Rationale**: "a destrutiva nunca é a mais forte" é sobre a tela onde ela convive com as ações do
dia. Na confirmação do Cancelar, ela é a única ação, e o vermelho cheio é o aviso de que se está
prestes a praticá-la.

**Alternativas**: mudar `.botao.perigoso` globalmente — alcançaria dez telas de confirmação fora do
escopo.

## D-004 — Na Lista, nenhuma ação preenchida

**Decisão**: a coluna da Lista continua com ações de linha (`.acao`), sem preenchida: a 4ª decisão
pede "a mesma regra em linha" — frequentes primeiro, destrutivas no fim e separadas —, e uma ação
cheia por linha numa tabela de dez Editais seria dez ações principais na mesma tela. As frequentes
são "Inscrições recebidas" e "Recursos aguardando decisão", nessa ordem; o resto mantém a ordem de
`do_edital`.

**Rationale**: a regra que governa é a da frase: a ação do dia é a mais visível. Na Lista, isso é
posição, e não preenchimento.

**Alternativas**: preencher a primeira de cada linha — repete a ação principal em todas as linhas.

## D-005 — Os rótulos da Lista não encurtam

**Decisão**: "Inscrições recebidas (N)" e "Recursos aguardando decisão (N)" são presos por testes
(`test_inscricoes_recebidas.py`, `test_hardening_pos_auditoria.py`, sobre a Lista e o cartão). Pela
4ª decisão, o texto fica e só a ordem muda.

## D-006 — Contador zero: a ação diz quanto, e a folha esmaece

**Decisão**: `Acao` ganha um campo opcional, `quantidade`, preenchido só pelas duas ações que
contam. A Lista acrescenta a classe `zerada` quando ele é zero, e a folha a desenha com a cor de
texto fraco e a borda neutra. O link e o rótulo continuam inteiros.

**Rationale**: o template não pode extrair o número do rótulo sem parsear texto, e o rótulo é preso
por teste. Um campo a mais na `Acao` não muda o conjunto nem o destino.

**Alternativas**: envolver o número num `span` — quebraria a substring presa pelos testes.

## D-007 — A altura da linha da Lista depende da largura da coluna

**Decisão**: a coluna de ações passa a usar `flex-wrap` com o grupo terminal numa segunda faixa só
quando não couber; a meta de 90 px é medida e, se não for alcançável sem mudar a largura das outras
colunas (o título do Edital é longo no seed), o valor alcançado vai para o
[verificacao.md](verificacao.md), pela regra das metas fora de alcance.

## D-008 — Na Condução, o primeiro gesto é o preenchido

**Decisão**: os gestos já vêm na ordem das operações (ordem → corte → apuração → publicação); o
primeiro é `botao`, os outros `botao secundario`, e os formulários ficam lado a lado com quebra. O
formulário de publicar, que tem dois campos, continua com eles.

## D-009 — O glossário vai para um `details` cujo rótulo não usa os termos

**Decisão**: o parágrafo `p.definicoes` vai, inteiro e com o mesmo texto, para dentro de
`<details class="como-preencher">`, fechado, com o rótulo **"Termos desta tela"**.

**Rationale**: `test_vocabulario_da_composicao` exige que a **primeira** ocorrência visível de
"recorte", "faixa" e "geração" esteja dentro de um `<dfn>`. Um rótulo como "O que é recorte,
faixa e geração" seria a primeira ocorrência, fora do `<dfn>`, e reprovaria as onze telas. A
varredura lê o `summary` como texto visível — e é bom que leia: o rótulo é o que a pessoa vê.

**Alternativas**: o rótulo "Como preencher" do assistente — estas telas não têm campo a preencher.

## D-010 — Onde a definição é o subtítulo, ela fica

**Decisão**: `convocacao_historico.html` (e `ocupacao_historico.html`, que nem estava na lista)
definem o recorte **dentro da frase do subtítulo** ("Todos os atos deste recorte — que é a lista em
que a pessoa concorre…"). Recolher a definição exigiria reescrever o subtítulo, e a 5ª decisão diz
que o texto não muda. Ficam como estão (FR-1052); o ganho de altura ali seria de uma linha.

## D-011 — "Atenção": uma faixa âmbar para a lista, e não uma por sinal

**Decisão**: `.sinais` passa a ser a lista com a faixa âmbar à esquerda; cada sinal perde a borda
própria e ganha um filete em cima, a partir do segundo. A cor é a **mesma** para todos os sinais.

**Rationale**: a regra da `022` (UX-006) proíbe cor de severidade — pintar uns e não outros. Uma
faixa âmbar uniforme não ordena nada: diz "isto pede atenção", que é o nome da seção; a verde dizia
"deu certo".

## D-012 — A trilha de auditoria perde o cartão, e não dado nenhum

**Decisão**: `.auditoria li` perde fundo, borda e raio, e ganha filete embaixo; o preenchimento
vertical cai. Cabeça, corpo e motivo continuam em três faixas, com os mesmos elementos.

## D-013 — Os documentos da inscrição usam a grade de `ul.documentos`

**Decisão**: a lista de documentos apresentados passa a ser `ul.documentos`, a mesma grade da mesa
do avaliador: o requisito à esquerda — com a razão, o arquivo, o tamanho, a data e o resumo
SHA-256 embaixo do nome —, a marca de facultativo numa coluna, e as ações "Visualizar" e "Baixar" à
direita; ou "Não apresentado.". As duas colunas da mesa que não existem aqui (modelo e leitura)
ficam como células vazias, como a mesa já faz quando o requisito não fornece modelo. As regras de
`.requisitos-apresentados`, `.requisito-nome` e `.acoes-do-documento` saem da folha comum, e a do
resumo do arquivo vai para o estilo da página.

**Rationale**: é o mesmo conceito nas duas telas, e o desenho da mesa já foi medido e refinado.

## D-014 — A ficha curta é uma variante, e não a regra

**Decisão**: `dl.ficha.curta` tem a largura do conteúdo; a Distribuição e a Minha etapa a usam. A
mesa e o recurso ficam como estão: a ficha da mesa divide a altura com a barra do painel ao lado.

## D-015 — F8: o que muda e o que fica

**Decisão**: mudam, por `pontuacao` e por um plural escrito por extenso:

- `revisao.py`: percentual da Modalidade, Peso, Nota mínima e Pontuação máxima; a data da versão da
  norma, quando é uma data; "vaga(s)" no quadro, nas vagas do Perfil e "nesse(s) recorte(s)";
- `supervisao.py`: o "vaga(s) imediata(s)" da mensagem do sinal;
- `conducao_do_marco.py`: "vaga(s) publicada(s)" e "posição(ões) divulgada(s)";
- `retificacao.py`: as duas linhas "N vaga(s)" do resumo de acréscimo, que só a tela de
  conferência mostra.

**Ficam, e viram registro** ([doc/achado-f8-textos-que-saem-da-tela.md](../../doc/achado-f8-textos-que-saem-da-tela.md)):

- `retificacao.objeto_legivel` ("dia(s) corrido(s)", "vaga(s)"): alimenta a impressão de cada destino
  do gesto, que `aplicacao_na_retificacao.registro` grava no registro do ato — sai da tela;
- o valor dos campos numéricos da etapa Etapas ("2.0000", que o navegador mostra "2,0000"): é valor
  enviado por formulário, e a 7ª decisão exige o POST idêntico;
- `revisao._leitura_do_marco`, que `aplicacao.py` reaproveita: não é tocado.

## D-016 — A matriz fixa o `thead`, e não cada `th`

**Decisão**: com duas linhas no cabeçalho — a de grupo, com o número do Edital, e a das Etapas —,
`position:sticky` em cada `th` com `top:0` sobreporia as duas. O cabeçalho inteiro fica fixo:
`.distribuicao thead{position:sticky;top:0}`. A moldura continua `overflow-x:visible` em tela larga,
que é a decisão registrada. O número do Edital sai de cada coluna e vai para a linha de grupo,
montada por `{% regroup %}` sobre as colunas, que a seleção já devolve agrupadas por Edital.
"Distribuir", "Todos" e "Nenhum" vão para uma faixa só, com o desenho de ligação.

**Alternativas**: calcular o `top` da segunda linha — dependeria da altura da primeira, que muda
com a fonte.

## D-017 — O que conta como "a lista de ações" da 2ª decisão

**Decisão**: para cada tela, a lista é o conjunto ordenado e sem repetição de: o `href` de todo link
dentro do `main`, o `action` de todo formulário (o endereço da página quando vazio), o `formaction`
de todo botão, e o `name=value` de todo botão de envio — medido com `ana.gestora` (todos os papéis) e
com `joana.avaliadora`, por JavaScript na página renderizada.

**Rationale**: é mais estrito que "links de ação": inclui navegação, e por isso qualquer link
perdido ou acrescentado aparece. O `name=value` pega o "Todos/Nenhum" da matriz, que distingue o
gesto pelo valor do botão.

## D-018 — No portal, a dica vai sob o seletor, numa coluna dele

**Decisão**: seletor e nome do arquivo à esquerda, com a dica de formato logo abaixo deles, e
"Enviar" na mesma linha, à direita do nome. É uma linha de **controles**; a dica é texto. Os
atributos que `arquivo.js` e `envio.js` leem (`data-arquivo`, `data-nome-do-arquivo`, `.progresso`)
não mudam.

---

## Decisões tomadas na implementação

## D-019 — As asserções que prendiam a grafia antiga do F8 foram reescritas

**Decisão**: sete asserções prendiam exatamente o texto que a 7ª decisão manda trocar ("2.0000",
"20.0000%", "vaga(s)") — `test_revisao.py` (três), `test_advertencias_do_quadro.py`,
`test_retificar_modalidade.py`, `test_sinal_do_acervo_sem_quadro.py` e
`test_us1_declaracao_unica_de_vagas.py`. Foram reescritas para a grafia nova, e o que cada uma
verifica — o número aparece, o quadro é mencionado, a linha nova tem quantidade — continua o mesmo.

**Rationale**: a condição de parada "um teste existente exige mudar texto" é sobre texto **fora** do
item; aqui o texto é o próprio item, e o prompt traz as grafias novas como critério. Asserções sobre
texto que sai da tela (o motivo do ato da ocupação, as pendências do domínio) não foram tocadas, e o
texto delas também não.

## D-020 — O glossário recolhido sobe de 32 a 53 px, e não 120

**Decisão**: a meta de "≥ 120 px" do primeiro controle é **fora de alcance dentro do escopo**. O
bloco do glossário tem de 63 a 84 px, mais 20 de margem; recolhido, o `summary` ocupa 31 px e 16 de
margem. Recolher o bloco inteiro, sem `summary`, daria no máximo 104 px — e o glossário deixaria de
estar à mão, que é o que a 5ª decisão pede. Alcançar 120 exigiria mexer no título, no subtítulo ou
na navegação dos recortes, que estão fora do item. Valores em [verificacao.md](verificacao.md).

## D-021 — Na Alocação, o Edital em texto, e "Distribuir" como ligação

**Decisão**: a linha de grupo diz "Edital 01/2026" em texto com peso, e não numa pastilha: a pastilha
somava 6 px à linha, e era a diferença entre 135 e 127 px de cabeçalho. "Distribuir" deixa o desenho
de botão e vai para o bloco de "Todos · Nenhum", em negrito e numa linha própria — numa linha
comum, "Distribuir Todos" se lia como um comando. O desenho de ligação dos três era a condição para
caber em 130 px. O destino, o rótulo e o nome acessível dos três não mudam. O padding
lateral das células do cabeçalho cai de 0,75 para 0,35 rem, e a coluna dos nomes de 14 para 12 rem:
é o que faz a matriz, com as nove Etapas, terminar exatamente na borda da coluna de conteúdo
(x = 1.256) a 1.280 px. "Todos · Nenhum" pode quebrar entre as duas palavras: segurá-los numa linha
alargava cada coluna e devolvia a página a 1.293 px.

**Alternativas**: tirar a caixa-alta do nome da Etapa — ganhava 13 px de largura e nenhum de altura;
deixar a pastilha "sem ninguém" quebrar — estreitava as colunas e aumentava o cabeçalho para 198 px.

## D-022 — A coluna de ações da Lista vai de 24 para 30 rem

**Decisão**: a ordem nova sozinha não baixa a linha: em 24 rem, cinco ações de um Edital publicado
quebram em três faixas (118 px). Em 30 rem quebram em duas, e quem passa a ditar a altura é o
título (82 px). É uma mudança de valor numa regra existente, e não regra nova.

A 375 px nada muda: a tabela tem 531 px num cartão de 325, com 24 ou com 30 rem, e o cartão recorta
a coluna de ações. É defeito anterior, medido igual antes e depois, e virou registro
([doc/achado-lista-e-conducao-a-375px.md](../../doc/achado-lista-e-conducao-a-375px.md)).

## D-023 — A asserção que prendia `class="ficha"` aceita a variante

**Decisão**: `test_jornada_da_presidente.py::test_a_confirmacao_de_atribuicao_nao_usa_estilo_de_alerta`
procurava `class="ficha"` exato perto de "Alocado nesta Etapa". A ficha passou a ser
`class="ficha curta"` (D-014), e a asserção passou a aceitar o prefixo. O que ela protege — a frase
mora na ficha, e não numa faixa de aviso ou de erro — continua o mesmo.

## D-024 — As regras de uma tela só vão para o estilo dela

**Decisão**: depois da revisão de código, as regras que só o Detalhe do Edital desenha
(`.lista-acoes.em-linha`, o filete das terminais, `.terminais .botao`, `.colunas.ao-topo`), as que só
a Lista desenha (`.acao.zerada`, o filete das terminais em linha) e as que só a Alocação desenha (o
`thead` fixo, a linha de grupo, o cabeçalho compacto, "Distribuir" em linha própria) saíram da folha
comum para o `{% block estilo_da_pagina %}` de cada tela, como o prompt pede. O filete passou a ter
seletor de irmão (`.lista-acoes+.terminais`, `.acoes>*+.terminais`): sem grupo acima, as terminais
não desenham divisor. As declarações de `flex` de `.coluna-toda` saíram, porque o
`thead th>*{display:block}` as vencia e nenhuma valia.

## D-025 — Um filtro só para "N vaga(s)"

**Decisão**: `contagem` em `interface_extras`, ao lado de `plural`, devolve o número e as palavras no
número dele. Revisão, Supervisão, Condução e o resumo do Retificar passam por ele; saem os dois
auxiliares locais que a primeira versão criara.

## D-026 — Três colunas nos documentos da inscrição

**Decisão**: as duas células vazias que completavam a grade de cinco colunas da mesa saíram, e a
página declara três colunas. Abaixo de 34 rem as células vazias viravam faixas em branco, porque a
mesa as põe em linha própria. O nome do arquivo tem classe própria (`.arquivo`), e não a da instrução
do Edital.
