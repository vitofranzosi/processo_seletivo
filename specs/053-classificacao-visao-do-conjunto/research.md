# Research — 053 · Classificação: a visão do conjunto e um Perfil por vez

O ponto de partida é a [research da `052`](../052-perfis-visao-do-conjunto/research.md). O que ela
decidiu e o navegador confirmou — esconder com `hidden`, o `invalid` em captura, o fragmento do
endereço, a rolagem depois do `load` — vale aqui sem mudança, e não se repete. Esta registra o que a
Classificação tem de diferente, e o que muda no código que as duas telas passam a dividir.

## R-001 — O que se extrai do `perfis.js`, e o que fica

**Decisão**: um script novo, `vista-do-conjunto.js`, com o que as duas telas fazem **igual**: a tabela
(legenda, cabeçalhos, linha por cartão, *Editar*), o cabeçalho do editor (título, *Anterior*,
*Próximo*, *Voltar à lista*), um cartão à vista por vez, o fragmento do endereço, o ouvinte de
`invalid`, o `hashchange`, a rolagem ao carregar, e a observação da lista (cartão que entra, que sai,
subcoleção que muda). E as regras puras que já eram das duas: `situacao`, `cartaoAAbrir`,
`controleAlterado`. Cada tela passa a ser uma **declaração**: onde está a lista, quais colunas, e como
ler um cartão — o `perfis.js` com o que já tinha (`resumo`, `percentual`, `lerCartao`), o
`classificacao.js` com o seu.

**Por quê**: a `052` disse que o código comum se extrairia quando a segunda tela entrasse. As duas
diferem só no que a linha lê; tudo o que custou percurso no navegador — o `invalid`, o fragmento, a
rolagem — é o mesmo, e duas cópias divergiriam na primeira correção.

**O que não é**: um componente de coleção. Não há API para criar, remover ou reordenar item, nem
estado paralelo, nem nada que a Classificação não use. A leitura do cartão é função da tela; o
script comum não conhece Perfil, marco ou Modalidade.

**Compatibilidade**: o `perfis.js` continua exportando para o `node` as mesmas regras, com os mesmos
resultados — `perfis.test.js` não muda. O guardião de que o script não cria campo
(`test_o_script_nao_cria_remove_nem_renomeia_campo`) passa a varrer os três arquivos, e não só o
`perfis.js`, que deixaria de conter o que ele procura.

**No navegador**, o comum se carrega antes, com `defer` nos dois, que preserva a ordem. **No node**, o
`perfis.js` o obtém por `require`; no navegador, por `window.VistaDoConjunto`.

## R-002 — A linha é o Perfil, e as colunas de marco têm um valor por marco

**Decisão**: `D-002` da spec. A célula de cada coluna de marco é uma lista, e cada item vira um bloco
próprio dentro da célula — um por marco, na ordem do cartão (a de `perfis_do_edital`: por código). Com
um marco, a célula tem um bloco, e a tabela é a da `052`. Sem marco, a coluna *Marcos* diz
*"sem marco"* e as demais ficam vazias.

**Medido**: os cinco Editais da `D-002`. O caso que decide é o 14/2026 (7 Perfis, 14 marcos): por
marco, 14 linhas e dois *Editar* por Perfil abrindo o mesmo cartão; por Perfil, 7 linhas, e cada
coluna com dois blocos alinhados — o 1º marco sobre o 2º, a comparação por posição da Revisão
(`revisao._marcos_agrupados`).

**As colunas**: Código (cabeçalho de linha) · Perfil (denominação · localidade) · Marcos (código de
cada) · Ordem · Corte · Desempate · Recurso · Origem · Situação · ação.

## R-003 — As frases da linha moram no template, e são as dos resumos dos blocos

**Decisão**, como a `R-005` da `052`: cada controle que a linha lê leva as frases curtas em
`data-resumo-<valor>`, e o script lê a do valor escolhido.

| Coluna | Controle | Frases (as do cartão) |
|---|---|---|
| Ordem | `select …-orderProduction` | *pela pontuação*, *por sorteio*, *não escolhida* |
| Ordem, sorteio | o bloco *Método do sorteio*, `data-resumo-proprio/comum/nenhum` | *método próprio*, *método comum*, *sem método declarado* — próprio quando algum campo do bloco tem valor; comum quando algum campo do método do Edital tem |
| Corte | `select …-cutTargetKind` + `…-cutTargetCount` | *quantidade fixa de N*, *o que o quadro de vagas publicar*, *este marco não corta* — as do `resumo-do-bloco` |
| Recurso | rádios `…-appealDeclaration` + `…-appealDurationDays` | *admite, prazo de N dias*, *não admite por esta via*, *nada declarado* — as do `resumo-do-bloco` |
| Desempate | `select …-type` + `select …-target` | *maior nota em*, *maior*, *menor* + o rótulo da opção escolhida do alvo |

O alvo do critério é o **rótulo da opção** escolhida, que o servidor já escreve com o nome da Etapa ou
do fato. O critério sem alvo diz só o sentido.

**Método próprio.** A frase do resumo do bloco é *"próprio — diverge do comum do Edital"*. A linha lê
o fato do mesmo modo que o servidor decide o resumo — algum campo do método preenchido no cartão —, e
não por regra: *"marco com qualquer campo preenchido diverge"* é a definição que o template da `030`
escreveu (`FR-430`). Sob pontuação o bloco não existe, e a coluna diz só a forma.

## R-004 — A origem, pelo cálculo da Revisão

**Decisão**: uma função nova em `origens.py`, `origem_dos_marcos(perfis, alcance)`, que para cada
Perfil do conteúdo canônico chama `gesto_do_marco` — a mesma que `revisao._marcos_agrupados` chama — e
devolve `{id do Perfil: frase_do_gesto(registro)}`. A view a chama com o snapshot do Edital e os
registros `APLICAR_A_TODOS`, como a Revisão; o cartão leva `data-origem`.

**Por quê**: `gesto_do_marco` já decide as duas coisas que a `FR-964` pede — que o gravado é o que o
gesto gravou (a impressão), e que o Perfil tem um marco só. A frase é a da Revisão.

**Custo**: o snapshot já é montado para as pendências da mesma tela; `_pendencias` passa a aceitá-lo
de quem chama, e a etapa o monta uma vez para as duas. Mais uma consulta, a dos registros do gesto.

## R-005 — "Difere do gravado", no servidor

**Decisão**: `_marcos_alterados(digitados, perfis)` na view, ao lado de `_reexibir_classificacao`.
Para cada Perfil, compara os marcos digitados com os gravados (`forms.marcos_persistidos`) **depois de
passar os dois pela mesma `_reexibir_marco`** — que é exatamente o que o cartão desenha —,
normalizando o que a gravação e a leitura escrevem diferente (inteiro × texto, `None` × vazio, a ordem
das Etapas, a ordem dos marcos e dos critérios). Perfil com marco que não tem par gravado, ou que
perdeu um, é alterado.

**Por quê**: a `052` pagou pelo falso positivo com a comparação de campos que o cartão não mostra. Aqui
a mesma função desenha os dois lados, e o que ela não desenha não entra. O guardião é o mesmo:
**devolver o formulário que a tela mostrou, sem mudança, não acusa Perfil nenhum**.

**Na tela**, como na `052`: o controle que difere do `defaultValue`, e o marco ou o critério que entrou
ou saiu — inclusive a reconstrução do marco pela forma da ordem, que troca o cartão inteiro.

## R-006 — A âncora da recusa

**Decisão**: `_recusa` ganha o ramo da Classificação. `digitados` ali é `{Perfil: [marcos]}`, e a tela
devolvida desenha cada marco em `sub = posição` (`forloop.counter0`), e cada critério em `n = posição`.
A identidade da recusa se procura nos marcos e nos critérios digitados:

- marco: `marco-<Perfil>-<sub>-<campo>` quando o campo é um dos que o cartão sempre desenha com `id`
  (`code`, `name`, `orderProduction`, `scale`, `mode`; `rounding` vai para `scale`); senão, o cartão do
  marco, `marco-<Perfil>-<sub>`, que sempre existe;
- critério: `criterio-<Perfil>-<sub>-<n>-<campo>`, com `parameters` indo para `target` — os quatro
  controles do critério sempre existem;
- Perfil: o cartão do Perfil, `cartao-<Perfil>`.

**O domínio não dizia, e passa a dizer.** A primeira redação desta decisão partia de que a recusa já
trazia `campo` e `identidade`, como nas outras etapas. Não trazia: `validate_classification_milestones`
levantava as sete recusas do marco e do critério sem nenhum dos dois — e a Retificação, pela
`validar_criterio` da `048`, já os dava com as mesmas frases. A correção é de metadado: as quatro
recusas escritas ali ganham o campo e a identidade do marco ou do critério, e as três dos blocos
(janela, método, corte), que não sabem de que marco são, recebem a do marco de quem as chama. Nenhuma
mensagem muda, nenhuma regra muda, e o `DomainError` não os leva à API.

**Por quê**: sem a identidade não há âncora, e é o que as demais etapas fazem. O recuo para o cartão do marco é o que garante a `SC-357` — a âncora sempre aponta um elemento
que existe —, porque os campos opcionais podem não estar desenhados (o método sob pontuação, a
combinação com uma Etapa).

**E o script**: o Perfil recusado é o do primeiro elemento que o resumo da recusa aponta, e não mais
só o que traz `.recusa` dentro do cartão. Na etapa Perfis os dois apontam o mesmo Perfil.

## R-007 — O campo inválido num bloco fechado

**Decisão**: o ouvinte de `invalid` da `052` passa a abrir, além do cartão, todo `details` fechado
entre o controle e o cartão.

**Por quê**: a `030` tirou dos blocos que fecham todo campo `required`, mas não os limites — o prazo do
recurso tem `min=1`, o alvo e os suplentes do corte têm `min=0`. Um `-1` digitado com o bloco aberto e
o bloco fechado depois é o mesmo envio recusado em silêncio. O princípio da `030`
(`test_acessibilidade_da_classificacao.py`) continua: ele proíbe `required` ali, e nada disso o
afrouxa.

**A verificar no navegador real**: que o Chrome foca o controle depois de o `details` abrir dentro do
evento, como fez com o `hidden`.

## R-008 — As pendências da etapa

**Decisão**: o bloco `_pendencias.html` no alto da etapa, com `pendencias_aqui`, como nas outras
cinco; e `data-pendencias` no cartão do Perfil, contado por `_pendencias_por_perfil` — a função da
`052` — sobre a mesma lista.

**Por quê**: a expressão regular da `052` casa o começo do caminho, `/profiles/id=<Perfil>`, e o achado
de marco começa por ele (`D-003` da spec). Nenhuma função nova.

## R-009 — O rascunho local

**Decisão**: o formulário declara `data-rascunho` e `data-lista`, como as outras quatro, e a etapa
carrega o `rascunho.js`. `data-lista` aponta o contêiner dos cartões, `#classificacao-perfis`.

**Por quê**: a metade do servidor já atende (`D-007`). O `rascunho.js` guarda por nome de campo o que
não casa `prefixo-número-campo`, e os nomes da Classificação levam a identidade do Perfil, que não é
número — ficam como campos simples, que é o que se quer: o nome já identifica o marco.

**O que `data-lista` faz aqui**: o `rascunho.js` observa a lista só no primeiro nível, e os Perfis da
Classificação não entram nem saem. Marco e critério acrescentados sem digitação posterior entram no
guardado na próxima digitação — o mesmo alcance que a Modalidade tem na etapa Perfis.

## R-010 — A ordem da etapa

**Decisão**: `h2` → pendências → a ajuda e as definições de hoje → o bloco *Como preencher o marco* →
o aviso sem Etapa classificatória → **a tabela** → o método do sorteio comum → os cartões. O contêiner
dos cartões ganha `id="classificacao-perfis"`, e cada cartão, `id="cartao-<Perfil>"`.

**Por quê**: `UX-127`. O método é do Edital, como o controle da `052`; entre a tabela e o editor, ele é
lido como o que vale para todas as linhas.

## R-011 — A folha

**Decisão**: as regras da vista saem de `compor_perfis.html` para um `_estilo_da_vista.html`, incluído no
`estilo_da_pagina` das duas etapas; a Classificação acrescenta a do bloco por marco dentro da célula.

**Por quê**: continua fora de `base.html` (o teto de bytes), e uma cópia por etapa divergiria.

## O que o percurso no navegador ensinou

Medido no preview em 29/09/2026, a 1280×900 e a 375×812, sobre o Edital em elaboração do `seed_demo`
com 7 Perfis compostos pelo gesto da `051`. Quatro coisas que o plano não previa, todas corrigidas
antes do PR:

1. **O rascunho local perdia Etapas.** O `rascunho.js` guardava cada campo pelo `value`, e numa lista
   de escolha múltipla ele é só a primeira opção marcada. Nenhuma etapa com rascunho tinha lista
   múltipla até esta — as Etapas que o marco enumera —, e a tela restaurada voltava com uma Etapa a
   menos em cada marco; a gravação seguinte a apagaria. Quem acusou foi a própria vista: as sete
   linhas disseram *"alterado — não salvo"* depois de restaurar só duas alterações, e a comparação do
   servidor (R-005) estava certa. O script passou a guardar e a comparar a lista pelas opções.
2. **O domínio não dava identidade à recusa do marco** (R-006, corrigido acima). A âncora dependia
   dela, e a recusa voltava como texto solto.
3. **O endereço que aponta o cartão centralizava o cartão.** Com 1,6 mil px, o centro dele deixava o
   título do editor 350 px acima da tela ao voltar de um envio que não gravou. Quando o alvo do
   endereço é o próprio cartão, o que se mostra agora é o título, no alto. O código é o comum, e a
   etapa Perfis leva a correção junto.
4. **O código quebrava no hífen** (*"DOC-INFO-02"* em três linhas), e a classe que o impediria,
   `codigo`, já tem regra em `base.html` — fundo e fonte de outra tela. O código do Perfil e o do marco
   não quebram, com uma classe própria.

E um cuidado de verificação, e não de produto: o `runserver` serve os estáticos com cache, e a página
que volta de um POST reusa o script antigo. Medir depois de mudar o script pede atualizar o cache
(`fetch(…, {cache: "reload"})`) — a primeira medição da rolagem, com o script velho, parecia dizer
que a correção não funcionava.
