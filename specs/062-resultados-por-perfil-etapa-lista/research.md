# Research: Resultados divulgados por Perfil, etapa e lista

**Feature**: `062` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

As decisões de produto (recebidas 1ª a 9ª, e D-001 a D-004) estão na spec. Aqui ficam as técnicas,
a partir de `D-005`. Nenhuma pergunta ficou aberta: o código já tinha todos os dados.

---

## O que o código já oferece

- `historico_publico_do_edital(edital)` (`divulgacao/application/selectors.py`) devolve as vigentes
  do Edital, cada uma com as `anteriores` da própria cadeia, agrupadas por `(marco_id, lista_id)` —
  o eixo da lista da `021`. São **duas consultas** para o Edital inteiro, e a cadeia já fica ligada
  em memória.
- Cada linha traz a `PublicacaoResultado`, que tem `perfil_id`, `marco_id`, `lista_id`, `natureza` e
  `publicado_em` em coluna, e os rótulos lidos do cabeçalho congelado: `marco`, `marco_codigo`,
  `titulo` e, desde o #255, `lista` (`nome_da_lista`).
- O cabeçalho congelado também tem `perfil` (o nome do dia da publicação), que `_rotulos` ainda não
  devolve.
- A view `selecao` já carrega a versão vigente do Edital (`versao.content`), com `profiles` em ordem
  e, em cada Perfil, `competitionModalities` em ordem.
- A view já lê as inscrições da pessoa conectada naquele Edital (`_inscricoes_iniciadas`), e não lê
  nada quando não há sessão.
- A volta depois da identificação passa por um único ajudante, `_de_volta_a_vaga`, que hoje só
  reconhece a vaga (`portal:inscrever`) e manda todo o resto para "Minhas inscrições".

---

### D-005 — A árvore é montada em `portal/leitura.py`, e o convite na view

**Decisão**: uma função pura em `portal/leitura.py` recebe as vigentes já lidas e o conteúdo vigente,
e devolve a árvore Perfil → etapa → lista → vigente, com o histórico de cada etapa. A decisão do
convite fica em `views.selecao`, ao lado do convite de cada vaga.

**Por quê**: `leitura.py` já se define como "conteúdo publicado entra, estrutura de tela sai; nada
aqui sabe quem está lendo". A árvore é exatamente isso. O convite, ao contrário, depende de quem
está lendo, e o módulo diz de si que não sabe.

**Alternativas**: montar a árvore no template, com `regroup` — descartado: o `regroup` exige a lista
já ordenada pela chave, e a ordem aqui vem de três fontes (conteúdo vigente, `marco_codigo`, ordem
declarada das Modalidades); o template ficaria com regra. Montar dentro de
`historico_publico_do_edital` — descartado: ela serve uma pergunta de divulgação ("as vigentes e o
que sucederam"), e a forma da página do portal não é dela.

### D-006 — O nome acessível por texto oculto dentro do link, e não por `aria-label`

**Decisão**: o link tem o nome da lista como texto visível e, dentro dele, um `<span class="oculto">`
com " — <etapa> — <Perfil>" (no histórico, também natureza e data). A classe `.oculto` entra na
folha do portal com a mesma regra que a gestão já usa (`interface/base.html`).

**Por quê**: o nome acessível tem de **começar** pelo texto visível (a decisão do *Clarifications*
de 07/10): quem usa comando de voz diz o que vê. Texto oculto concatenado garante isso por
construção. Um `aria-label` substitui o texto inteiro, e nada impediria a frase dele de divergir do
que está na tela numa edição futura.

**Alternativas**: `aria-describedby` apontando o título da etapa — descartado: descrição não entra
no nome, e a lista de links do leitor de tela continuaria com dois "Ampla concorrência".

### D-007 — A volta depois da identificação passa a reconhecer a página do Edital

**Decisão**: `_de_volta_a_vaga` aceita também `portal:selecao` e devolve a página do Edital na
âncora do bloco de resultados. O convite de quem não está conectado leva a `portal:acesso` com
`destino` igual à página do Edital.

**Por quê**: é o que `FR-1161` pede, e o ajudante é o único ponto de decisão. A restrição que ele
guarda é contra **praticar ato** a partir de um endereço compartilhado — por isso `inscrever` é
POST —, e a página do Edital é pública, GET, e não pratica ato nenhum. O destino continua conferido
contra o próprio host por `_destino_seguro`, e qualquer outra rota continua indo para "Minhas
inscrições".

**Alternativas**: não passar destino e deixar a pessoa em "Minhas inscrições" — descartado: a
lista não mostra classificação, e quem veio do Edital perderia o lugar. Mandar direto à inscrição
depois da identificação — descartado: antes de entrar não se sabe qual é, e o destino teria de
carregar regra.

### D-008 — A ordem das listas sai do Perfil no conteúdo vigente

**Decisão**: dentro da etapa, o recorte sem lista (a ampla concorrência) vem primeiro; depois as
listas na ordem de `competitionModalities` do Perfil no conteúdo vigente; uma lista que o vigente
não conhece vai para o fim, pela ordem alfabética do nome gravado.

**Por quê**: é a ordem em que o Edital declara as Modalidades, e é a que a seção Vagas usa para a
linha "Concorrência". O recorte sem lista é a ampla concorrência por definição (o mesmo do sorteio
— e não a Modalidade "Ampla concorrência" eventualmente declarada, que é outra grafia).

### D-009 — O nome do Perfil vem do vigente, com o gravado de reserva

**Decisão**: `_rotulos` passa a devolver também `perfil` (o nome congelado). A árvore usa o nome do
Perfil no conteúdo vigente quando o `perfil_id` existe lá, e o congelado da publicação mais recente
do grupo quando não existe. Perfis ausentes do vigente vão para o fim, pela data da publicação
mais recente.

**Por quê**: é D-004 da spec, e a única fonte que falta é o nome congelado, que já está nos bytes
lidos — nenhuma leitura nova.

### D-010 — O título da etapa é o da vigente mais recente da etapa

**Decisão**: as listas de uma etapa podem ter sido publicadas sob versões diferentes; o título é o
`marco` gravado na vigente mais recente daquela etapa, sem corte (decisão recebida 4). A ordem entre
etapas é `marco_codigo`, e depois o nome.

**Por quê**: a ordem do certame já é a que `situacoes_do_candidato` usa (`marco_codigo` gravado);
uma segunda régua de ordem seria uma segunda verdade.

### D-011 — Nenhuma leitura nova ao banco, provada por contagem

**Decisão**: o teste de custo abre a mesma página com N e com 2N publicações e exige o mesmo número
de consultas; e o teste existente das publicações (`test_prazo_recursal_publico.py`) continua
exigindo uma única consulta à tabela de publicações.

**Por quê**: `SC-448`. Tudo o que a árvore precisa já está em memória: colunas da publicação,
cabeçalho congelado (já decodificado por `_rotulos`) e conteúdo vigente.

### D-012 — Os testes que leem a marcação antiga mudam junto, sem afrouxar

**Decisão**: três arquivos localizam o bloco pela marcação de hoje (`<ul class="resultados-divulgados">`,
`<details class="publicacoes-anteriores">` e `<li><a href=...`): `test_historico_de_resultados.py`,
`test_prazo_recursal_publico.py` e `test_resultado_publico.py`. Eles passam a localizar pela
marcação nova descrita no [contrato](contracts/bloco-de-resultados.md), e cada asserção continua
cobrando o que cobrava — vigente fora do histórico, histórico de uma lista fora da outra, prazo só
na lista que o tem.

**Por quê**: a mudança de marcação é a feature; a garantia de cada teste não é.
