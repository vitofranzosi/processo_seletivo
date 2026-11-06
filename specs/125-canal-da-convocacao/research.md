# Research: A convocação segue o canal

**Feature**: [spec.md](spec.md) · **Plano**: [plan.md](plan.md) · **Data**: 2026-11-06, sobre a `main`
em `250efe97`

Cada decisão abaixo é **técnica**, e serve às decisões de desenho da spec (D-001 a D-008), aceitas
pelo usuário em 2026-11-06. Onde uma delas mudar, a decisão técnica correspondente muda junto, e o plano diz
qual.

## R-001 — A visibilidade mora num seletor só, da `019`

**Decisão:** uma função `visiveis_ao_candidato(convocacoes)` em
`convocacao/application/selectors.py`, que recebe convocações já lidas e devolve o conjunto das
visíveis (FR-3981). O portal nunca decide por conta própria: `vigentes_por_inscricao` passa a escolher
a vigente mais recente **entre as visíveis** (FR-1100 da `059`, revista), e a tela, a lista e o
acompanhamento continuam lendo dela. `chamada_em_aberto`, que o Requerimento consulta, ganha o mesmo
filtro (R-004).

**Por quê:** a `059` pôs a escolha da convocação num seletor para que lista, acompanhamento e tela
mostrassem a mesma (FR-1100). A visibilidade é a mesma pergunta, um passo antes: decidida em cada
view, divergiria na primeira mudança, como a `029` já pagou com *"em aberto"* e *"vigente"*.

**Alternativas descartadas:**
- *Coluna `visivel_ao_candidato` na convocação:* a convocação é append-only, e a visibilidade muda com
  o registro da publicação, que é outro ato. Coluna pediria `UPDATE` em tabela imutável. É derivada,
  como o estado do prazo.
- *Filtrar no template:* a recusa do envio e a do Requerimento precisam do mesmo predicado no
  comando (FR-3985, FR-3986), e o template não é o comando.

## R-002 — A cadeia se lê por conjunto, e só quando há convocação sem comunicação

**Decisão:** o predicado da FR-3981, com a D-001, em três passos e número fixo de consultas:

1. Toda convocação com comunicação bem-sucedida já é visível. As comunicações vêm no *prefetch* que
   `vigentes_por_inscricao` já faz: **zero** consultas novas no caso comum.
2. Para as que não têm, uma consulta traz a cadeia das inscrições em questão — `id` e
   `convocacao_anterior_id` de todas as convocações delas — e outra, os `id` das que têm comunicação
   bem-sucedida. A cadeia se percorre em memória, pelos `convocacao_anterior_id`, até a raiz.
3. Para as que nem a cadeia comunicou, uma consulta traz só `profiles` das versões citadas
   (`values_list("id", "content__profiles")`), e `forma_declarada` decide.

**Por quê:** a FR-1092 da `059` e o número fixo da `118` são medidos em
`tests/performance/test_area_do_candidato.py` e `test_lista_com_convocacao.py`. O caso comum, de
convocação comunicada, não paga nada; o caso K-pub paga **até três** consultas, independentemente
de quantas inscrições ou convocações (FR-3990, SC-1204).

**Alternativas descartadas:**
- *Ler a cadeia por `convocacao_anterior` com `select_related` em profundidade fixa:* a cadeia de
  correções não tem profundidade máxima (correção da correção, na `121`).
- *Considerar visível quem teve qualquer convocação comunicada no mesmo recorte:* uma convocação
  para regularizar, nova e sem cadeia, apareceria antes da publicação dela por causa da chamada
  anterior da mesma pessoa.
- *Ler `content` inteiro da versão:* o conteúdo publicado é o Edital todo, e só o `callForm` do Perfil
  importa.

## R-003 — *"Houve convocação no recorte"* conta só as visíveis

**Decisão:** a tela da convocação, sem convocação para a pessoa, pergunta se o recorte tem convocação
**visível** (FR-3984). A consulta passa de `exists()` a: existe convocação do recorte com comunicação
bem-sucedida, **ou** existe convocação do recorte cuja forma citada não é publicação. A segunda parte
lê as versões distintas citadas no recorte, que são poucas (uma por Retificação).

**Por quê:** contar as invisíveis diria a todo inscrito que a convocação começou, e ao próprio
convocado em K-pub que ele não foi chamado. É o vazamento que a 1ª decisão fecha.

## R-004 — O Requerimento lê a chamada visível

**Decisão:** `requerimentos/application/preencher.py` consulta `chamada_em_aberto` só no momento *na
convocação* e para o Requerimento já enviado. O filtro de visibilidade entra em `chamada_em_aberto`
(D-003): a página, o chamado e o envio leem a mesma política (FR-1099 da `059`), e por isso a recusa do
envio sai no comando sem código novo — com a chamada invisível, o Requerimento *na convocação* está
*"ainda indisponível"*, como para quem não foi convocado.

`chamada_em_aberto` só tem esse chamador fora da `019`; o `_em_aberto_da_pessoa` de `convocar.py`, que
impede convocar duas vezes, é outra função e **não** muda: a gestão continua vendo toda convocação
(FR-3989).

**Se o usuário recusar a D-003:** o filtro não entra em `chamada_em_aberto`, e o Requerimento continua
abrindo em K-pub.

## R-005 — A recusa do envio reusa o 404 que já existe

**Decisão:** `convocacao/application/documentos.py::apresentar` e a consulta do arquivo apresentado
recusam a convocação invisível com `nao_encontrado()`, logo depois de achar o item — o mesmo código, a
mesma mensagem e o mesmo status do item inexistente (FR-3985).

**Por quê:** o inventário de negativas da `033` cobra `raise Http404` **novo**; esta recusa é a mesma
que já está inventariada, por outra causa, e a resposta não revela que a convocação existe. A tela da
convocação não usa 404: com a convocação invisível ela é a de quem não tem convocação (FR-3983), como
já é para quem nunca foi chamado.

## R-006 — A prévia é um passo do servidor, e assina o texto

**Decisão (D-004):** os seis formulários da tela de condução com texto que chega ao candidato — os
titulares, a individual, para regularizar, os vencidos, o desfecho e o indeferimento — ganham um
campo `etapa`. Com texto digitado e sem `etapa=confirmar`, a view não pratica o ato: renderiza a tela
com o bloco *"Conferir o texto"* no lugar do formulário, com a prévia, o número de pessoas, os mesmos
campos ocultos (chave, alcance, lista, escolhas) e o texto, e o botão que pratica o ato. O bloco grava
também um resumo do **texto composto**; a confirmação recompõe e, se o resumo divergir — o fundamento
derivado mudou entre a prévia e o clique —, recusa com a prévia nova à vista, como a `120` faz com a
prévia assinada.

A composição é a de `convocacao/domain/fundamento.py` (`com_complemento`), a mesma que o ato grava; o
número é o do alcance assinado que a confirmação já confere (FR-3994, FR-3996). Na correção, o texto
entraria na prévia que a `120` já mostra (FR-3997), sem passo novo — na implementação, a correção com
complemento passa pela mesma conferência (ajuste da D-004, aceito pelo usuário em 2026-11-06).

**Por quê:** a CSP da `091`/`092` recusa script no template, e a prévia precisa funcionar sem script
(FR-3995). Um passo do servidor é o padrão já usado pela correção, e não grava nada até a confirmação.

**Alternativas descartadas:**
- *Prévia ao vivo, por arquivo de script:* não atende quem não tem script, e o texto mostrado seria
  composto no navegador — uma segunda composição, que a FR-3993 proíbe.
- *Passo sempre, mesmo sem complemento:* um clique a mais em toda convocação, para mostrar um texto que
  já está na tela.

**Se o usuário recusar a D-004** pelo passo sempre: muda só a condição, de *"com texto digitado"* para
*"sempre"*.

## R-007 — O vocabulário do canal sai de uma tabela só

**Decisão:** `convocacao/domain/vocabulario_do_canal.py`, com as frases por forma — rótulo da data da
comunicação, *"contado de"*, prazo não iniciado, pastilha e situação da gestão, confirmação do
registro, títulos e botões da seção das pendentes, recusas. Portal e gestão recebem a forma e a
referência pela leitura que já fazem: no portal, `comunicacao_de(convocacao)` substitui `envio_de` nas
telas e devolve forma, instante e referência da última comunicação bem-sucedida, das comunicações do
*prefetch*; sem comunicação, a forma lida em R-002. Na gestão, por linha, pelas `comunicacoes` que os
cartões já carregam.

`envio_de` continua existindo para o prazo: o instante que inicia o prazo não muda (FR-4005).

**Por quê:** a FR-4004 pede uma fonte só por canal, e a varredura do inventário de 06/11 achou 8 frases
no portal, 25 na gestão e 5 recusas, quase todas sem decidir a forma. Uma tabela permite ao teste
varrer as telas nas duas formas e reprovar *envio* na publicação e *publicação* na mensagem.

## R-008 — O inventário das frases

O inventário de 06/11/2026, feito sobre a `main` em `250efe97`, está no
[contrato do vocabulário](contracts/vocabulario-do-canal.md), por superfície, com a frase de hoje e a
do canal. Três achados entram no escopo por serem a mesma 3ª decisão:

- *"A comunicação sai no mesmo ato."*, na convocação individual, é **falsa** na publicação: lá a
  convocação fica aguardando o registro.
- A confirmação do registro em lote (`_resultado_da_comunicacao.html`) diz *"comunicações enviadas"*
  quando a referência foi informada, porque o fluxo conta o registro como envio e não devolve a forma.
- A linha *"Convocação substituída"* da `121` diz *"Comunicada em"* na mensagem (D-008).

A trilha do Edital grava *"Comunicação ENVIADA ... na forma PUBLICATION"*. Os registros **novos**
passam a dizer *"Publicação da convocação registrada: ‹referência›"*; os antigos ficam como estão,
porque a trilha só acrescenta (FR-4006).

## R-009 — Nenhuma migration, e o que muda na instalação no dia da implantação

**Decisão:** nenhuma migration, tabela ou coluna (FR-4006). A implantação muda o que o portal mostra a
quem tem convocação por publicação sem registro: ela some do portal até o registro, com documentos
já enviados preservados na gestão (caso-limite da spec).

**Por quê:** a regra é derivada do que já está gravado. O efeito na instalação é o que a 1ª decisão
pede, e por isso o quickstart traz a consulta que conta essas convocações antes da implantação, para o
usuário decidir se registra as publicações pendentes antes.

## R-010 — Os testes que mudam

- **Visibilidade:** testes de seletor (as quatro combinações de forma × comunicação, a cadeia de três,
  a forma trocada por Retificação, a forma não declarada e o desfecho antes da publicação); testes de
  view nas sete superfícies do portal, em K-pub, K-msg e depois do registro; o *"houve convocação"* com
  recorte só de invisíveis.
- **Contagem de consultas:** `test_area_do_candidato.py` e `test_lista_com_convocacao.py` ganham o
  cenário K-pub com N inscrições, e o número não cresce com N.
- **Prévia:** um caso por formulário — o aviso visível e ligado por `aria-describedby`, o passo com
  texto, o direto sem texto, o número no lote, a recusa com alcance mudado, a recusa com texto
  composto divergente, a volta com os campos preservados e o texto do portal igual ao da prévia.
- **Vocabulário:** um teste que renderiza as telas do portal e da gestão nas duas formas e varre as
  frases da tabela; as varreduras de vocabulário existentes, que têm lista literal de telas, recebem as
  telas tocadas.
- **Os que mudam por decisão:** os testes que prendem *"conta a partir do envio da comunicação"* para a
  publicação, os que esperam a convocação visível em K-pub (`019`, `059`, `118`, `121`) e os que
  esperam *"Comunicada em"* na linha da substituída. Cada um muda citando a revisão.
