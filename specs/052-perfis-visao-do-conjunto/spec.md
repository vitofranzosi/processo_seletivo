# Feature Specification: Perfis de Vaga — a visão do conjunto e um editor por vez

**Feature Branch**: `claude/052-perfis-visao-do-conjunto`

**Created**: 2026-09-29

**Status**: Draft

**Input**: pedido do usuário de 29/09/2026, depois da
[análise das coleções repetidas](../../doc/analise-ux-colecoes-repetidas-2026-09-29.md) e do
contraponto dele à análise: a etapa Perfis apresenta a coleção como N cartões completos abertos ao
mesmo tempo, e isso não escala. O contraponto fixou três ajustes que esta spec adota — a Situação
enxuta, o limiar de dois Perfis decidido por medição e a Classificação fora — e manteve fora o teto
de mil campos, registrado em
[achado próprio](../../doc/achado-etapa-perfis-recusa-acima-de-mil-campos.md).

> **Faixa de identificadores.** Abre em **FR-944**, **SC-348** e **UX-116**, contíguos. O teto medido
> em 29/09/2026 em todas as worktrees e branches remotas era 943, 347 e 115, da `051`, já na `main`.
> As decisões reiniciam em `D-001`.

> **Teto proporcional.** Esta feature muda **o que se vê**, e nada do que se grava: nenhum campo,
> nenhuma rota de gravação, nenhuma regra de validação, nenhuma espécie de Alteração. Cada requisito
> abaixo nomeia uma pergunta que a tela passa a responder ou um modo de falha que ela passa a evitar;
> o que não fizer nenhum dos dois é nota de tarefa.

---

## Por que esta feature existe

**A etapa Perfis é a soma dos cartões.** Medido no sistema rodando, a 1280×900, com a `051`:

| Perfis | Altura da página | Controles visíveis |
|---:|---:|---:|
| 1 | ~3,1 mil px | 30 |
| 7 (28/2026) | **14,5 mil px** | 212 |
| 16 (140/2025) | ~31 mil px | 482 |

Cada Perfil custa 1.898 px, mais de duas telas. O primeiro começa a 912 px, **abaixo da dobra**: quem
abre a etapa não vê Perfil nenhum. *Salvar* fica depois do último.

**E nenhum cartão diz de quem é.** A legenda de todos é *"Perfil de Vaga"*; o código e a localidade
moram no valor de um campo, que a busca do navegador não encontra e que o leitor de tela, navegando
por grupos, anuncia sete vezes igual.

**O que o operador precisa comparar está a sete mil pixels de distância.** As vagas do polo 1 e do
polo 5; a Modalidade que falta numa cópia — o `G-001` da `043`, que motivou metade da `051` —; a forma
de convocação que falta num Perfil que corta, que a `051` tornou impeditiva. O controle do Edital diz
*"Varia entre os Perfis"* e não diz quais.

**O que não muda.** A etapa continua sendo **um formulário**, gravado inteiro a cada envio, como
decidiram a `027` (a seção do quadro no cartão, e não em tela à parte), a `043` (o duplicar que copia
o digitado) e a `051` (o gesto que lê o digitado e grava pela gravação da etapa). Esta feature não
toca nisso: todos os Perfis continuam no formulário e em todo envio; só um fica à vista.

---

## Clarifications

### Session 2026-09-29

- Q: A partir de quantos Perfis a tabela aparece? → A: **Dois** (`D-002`). Com um Perfil, o cartão
  aparece sozinho, como hoje. O contraponto do usuário pediu que o limiar fosse decidido por medição
  e não por doutrina; a medição está na decisão.
- Q: Quantos estados a Situação tem? → A: **Dois fatos, três leituras** (`D-003`): *"sem pendência"*
  ou *"N pendências"*, e, independente disso, *"alterado — não salvo"*. *"Em edição"* é seleção, e não
  situação.
- Q: A Classificação entra? → A: **Não.** Ela tem o mesmo problema e é a candidata seguinte, depois
  que esta ensinar foco, campo obrigatório escondido e sincronização da tabela.
- Q: *"Salvar e editar próximo"*? → A: **Não existe.** Trocar de Perfil não perde nada, porque o
  Perfil que sai continua no formulário; ir ao próximo é *"Próximo"*, sem ida ao servidor, e gravar
  continua sendo *Salvar*, da etapa inteira (`D-001`).

---

## User Scenarios & Testing *(mandatory)*

**Ator.** Quem elabora o Edital, na etapa Perfis da composição — as mesmas permissões de hoje. Esta
feature não cria papel, permissão nem capacidade.

**Unidade.** O Perfil de Vaga, como linha da tabela e como cartão do editor. O cartão é o de hoje,
inteiro.

### User Story 1 — Ver o conjunto e trabalhar num Perfil de cada vez (Priority: P1)

Quem elabora abre a etapa Perfis de um Edital com sete polos e vê, antes de qualquer campo, a tabela
dos sete: código, denominação e localidade, vagas, cadastro reserva, Modalidades, forma de convocação
e situação. Escolhe *Editar* no polo de Viana, corrige as vagas, passa ao seguinte com *Próximo*,
corrige outra coisa, volta à lista e salva uma vez.

**Why this priority**: é a feature. As outras histórias existem para que esta não quebre nada.

**Independent Test**: num Edital em elaboração com 7 Perfis, abrir a etapa, conferir a tabela com 7
linhas e nenhum cartão visível; editar o 2º, passar ao 3º por *Próximo*, alterar um campo em cada,
voltar à lista, salvar; conferir que os dois ficaram gravados e os outros cinco intactos.

**Acceptance Scenarios**:

1. **Given** um Edital com 7 Perfis, **When** quem elabora abre a etapa, **Then** a tabela lista os
   7 na ordem do Edital, e nenhum cartão está à vista.
2. **Given** a tabela, **When** quem elabora escolhe *Editar* num Perfil, **Then** o cartão daquele
   Perfil — e só ele — aparece, com o título *"Editando P02 — Viana"*, e a linha fica marcada como em
   edição.
3. **Given** um Perfil em edição com uma alteração, **When** quem elabora escolhe *Próximo*, **Then**
   o cartão seguinte aparece, nada é enviado ao servidor, nenhuma pergunta é feita, e a linha deixada
   diz *"alterado — não salvo"*.
4. **Given** alterações em dois Perfis, nenhum à vista, **When** quem elabora salva, **Then** os dois
   são gravados, pelo mesmo envio de hoje, e a tela volta com a tabela e nenhum cartão aberto.
5. **Given** um Perfil em edição, **When** quem elabora escolhe *Voltar à lista*, **Then** nenhum cartão
   fica à vista, o que foi digitado continua no formulário, e o foco volta ao *Editar* daquela linha.
6. **Given** um Edital com um Perfil só, **When** a etapa abre, **Then** não há tabela, e o cartão
   aparece aberto, como hoje.
7. **Given** um Perfil em edição, **When** quem elabora altera a Localidade, as vagas ou uma
   Modalidade, **Then** a linha dele acompanha a alteração, sem envio.

---

### User Story 2 — Nunca travar em silêncio (Priority: P1)

Quem elabora apaga o código de uma Modalidade do polo 5, passa ao polo 6 e clica *Salvar*. Em vez de
nada acontecer, o polo 5 abre, com o foco no campo vazio e a mensagem do navegador junto dele. Da
mesma forma, a recusa do servidor abre o Perfil recusado, e o link que aponta um campo de um Perfil
abre esse Perfil.

**Why this priority**: esconder um cartão que tem campo obrigatório é o modo de falha mais provável
desta feature, e o mais silencioso: o navegador recusa o envio e não consegue mostrar o campo. A
`030` já pagou por ele uma vez, nos blocos do marco.

**Independent Test**: com 3 Perfis, esvaziar um campo obrigatório do 1º, abrir o 3º, clicar *Salvar*;
conferir, num navegador real, que o 1º abriu, que o foco está no campo e que nada foi enviado.

**Acceptance Scenarios**:

1. **Given** um campo obrigatório vazio num Perfil fora de vista, **When** quem elabora salva ou
   avança, **Then** aquele Perfil passa a ser o visível, o foco vai ao campo, e a mensagem de validação
   aparece junto dele.
2. **Given** a validação da tela marcando um campo como inválido — o limite do cadastro reserva, a
   soma do quadro, dois Perfis com o mesmo código —, **Then** o mesmo acontece.
3. **Given** um envio que o servidor recusa com o erro num campo de um Perfil, **When** a tela volta,
   **Then** aquele Perfil está aberto e o erro está à vista junto do campo.
4. **Given** um endereço que aponta um campo ou o cartão de um Perfil, **When** a etapa abre por ele,
   **Then** aquele Perfil está aberto e o elemento apontado, à vista.
5. **Given** um envio sem validação — *Conferir aplicação*, *Aplicar aos demais Perfis*, *Preencher
   pelo percentual* —, **Then** nada muda em relação a hoje.

---

### User Story 3 — Criar, duplicar, remover e aplicar como antes (Priority: P1)

Quem elabora acrescenta um Perfil, duplica o polo de Serra para Guarapari, remove um polo que saiu do
Edital, aplica a PcD do primeiro aos demais e preenche o quadro pelo percentual. Cada gesto faz o que
faz hoje; a diferença é onde o resultado aparece.

**Why this priority**: são os ganhos da `043` e da `051`. Uma tela mais curta que custe esses gestos
é a falsa melhoria que o contraponto do usuário pediu para evitar.

**Independent Test**: com 7 Perfis, acrescentar um, duplicar o 1º, remover o 4º, aplicar uma
Modalidade do 1º aos demais, confirmar a prévia, salvar; conferir o resultado gravado igual ao que o
mesmo roteiro produz sem esta feature.

**Acceptance Scenarios**:

1. **Given** a tabela, **When** quem elabora escolhe *Acrescentar Perfil*, **Then** o cartão novo
   aparece como o visível, com o foco no Código, e a tabela ganha a linha dele, *"alterado — não
   salvo"*.
2. **Given** um Perfil em edição, **When** quem elabora o duplica, **Then** a cópia entra logo depois
   da origem, na tabela e no formulário, passa a ser o cartão visível, e traz o aviso da `043` sobre o
   que levou e o que não levou.
3. **Given** um Perfil em edição, **When** quem elabora o remove e confirma, **Then** o cartão e a
   linha saem, nenhum cartão fica à vista, e o foco vai ao *Editar* da linha seguinte — ou da
   anterior, se era a última.
4. **Given** dois Perfis, **When** um é removido, **Then** a tabela sai e o que restou aparece aberto;
   **Given** um Perfil, **When** outro é acrescentado ou duplicado, **Then** a tabela aparece.
5. **Given** *Aplicar aos demais Perfis* numa Modalidade de um Perfil em edição, **When** a prévia
   volta, **Then** ela está no alto da etapa, como hoje, e alcança os Perfis fora de vista tanto
   quanto o visível; **When** confirmada, **Then** a tela volta com a tabela, e a coluna das
   Modalidades mostra o efeito em cada linha.
6. **Given** a escolha no controle do Edital (*"Declarado uma vez para todos os Perfis"*), **Then** o
   controle, a conferência, a prévia e a recusa de *Salvar* com escolha não aplicada funcionam como
   hoje, e a coluna *Convocação* mostra quais Perfis variam.
7. **Given** *Preencher pelo percentual*, **When** a tela volta preenchida, **Then** as linhas dos
   Perfis alcançados dizem *"alterado — não salvo"*.

---

### User Story 4 — Ver onde está o problema sem abrir cada Perfil (Priority: P1)

Quem elabora olha a tabela e vê que o polo de Viana tem uma pendência de publicação e que dois polos
foram alterados e não salvos. Não precisa abrir sete cartões para descobrir onde está a
inconsistência.

**Why this priority**: detectar anomalia é a terceira das cinco perguntas que a tabela existe para
responder, e é a que hoje custa mais.

**Independent Test**: com 7 Perfis gravados, um deles sem forma de convocação num marco que corta;
conferir a linha dele com *"1 pendência"* e as outras com *"sem pendência"*; alterar dois Perfis e
conferir *"alterado — não salvo"* nos dois.

**Acceptance Scenarios**:

1. **Given** pendências de publicação cujo objeto é um Perfil, **Then** a linha daquele Perfil diz
   quantas, em texto; as demais dizem *"sem pendência"*.
2. **Given** um Perfil cujo conteúdo na tela difere do gravado — digitado agora, novo, ou devolvido
   pelo servidor sem gravar —, **Then** a linha diz *"alterado — não salvo"*, junto da contagem de
   pendências.
3. **Given** uma pendência sobre o conjunto dos Perfis, e não sobre um deles, **Then** ela continua
   no bloco de pendências da etapa, e não em linha nenhuma.

---

### Edge Cases

- **Perfil sem código.** A linha aparece com *"sem código"* no lugar do código, e continua editável.
  É o caso do Perfil recém-acrescentado.
- **Dois Perfis com o mesmo código.** As duas linhas aparecem; o envio é barrado pela validação de
  hoje e abre o primeiro dos dois (US2).
- **Pendência de Perfil alterado.** A pendência vem do que está gravado; a linha diz as duas coisas,
  e a pendência pode já estar resolvida no que ainda não foi salvo.
- **Pendência de Perfil removido na tela.** A linha sai com o cartão; a pendência continua no bloco
  da etapa até a gravação, como hoje.
- **Restauração do rascunho local.** A tela volta montada pelo servidor, como hoje, e as linhas que
  diferem do gravado dizem *"alterado — não salvo"*.
- **Salvar com um Perfil aberto.** A tela volta com nenhum aberto; o *"Rascunho salvo"* de hoje é o
  que diz que gravou.
- **Envio que volta sem gravar** (recusa, prévia, cancelamento da prévia, preenchimento). O Perfil
  que estava aberto volta aberto, salvo quando a recusa aponta outro, que tem precedência.
- **Endereço que aponta o título da etapa** (o *Revisar* da Revisão). Nenhum Perfil abre.
- **Sem script.** A etapa é a de hoje — todos os cartões à vista, sem tabela —, com a legenda que
  identifica cada Perfil.
- **Tela estreita.** A tabela não provoca rolagem horizontal da página.
- **Edital que não está em elaboração.** A etapa é leitura; a tabela e o editor valem igual, sem os
  gestos de escrita, como hoje.

---

## Requirements *(mandatory)*

### O cartão diz de quem é

- **FR-944**: A legenda de cada cartão de Perfil MUST identificá-lo pelo código e pela localidade — ou
  pela denominação, sem localidade declarada —, e MUST dizer *"Perfil novo"* enquanto não houver
  código. Isto MUST valer também sem script.

### A vista do conjunto

- **FR-945**: Com dois ou mais Perfis na etapa, a tela MUST apresentar, antes de qualquer cartão, uma
  tabela com uma linha por Perfil, na ordem do Edital, sem reordenação pela tabela. Com um Perfil, MUST
  NOT haver tabela, e o cartão MUST estar à vista.
- **FR-946**: Cada linha MUST trazer: o código; a denominação e a localidade; as vagas imediatas; o
  cadastro reserva, com o limite quando limitado; as Modalidades, pelo código e pelo percentual; a
  forma de convocação; a situação (`FR-948`); e a ação *Editar*.
- **FR-947**: A linha MUST refletir o que está nos campos do cartão, inclusive o que ainda não foi
  gravado, e MUST acompanhar a digitação sem envio. A linha MUST NOT calcular regra de domínio — soma,
  suficiência, impeditivo —: o que é regra chega pela situação.
- **FR-948**: A situação MUST dizer, em texto, dois fatos independentes: quantas pendências de
  publicação têm aquele Perfil por objeto (*"sem pendência"*, *"1 pendência"*, *"N pendências"*); e se
  o conteúdo na tela difere do gravado (*"alterado — não salvo"*). Pendência sobre o conjunto dos
  Perfis MUST NOT ser atribuída a linha nenhuma.
- **FR-949**: *"Alterado — não salvo"* MUST valer sempre que o Perfil na tela diferir do gravado:
  digitado depois de a tela abrir, acrescentado ou duplicado e não gravado, ou devolvido pelo servidor
  sem gravação (recusa, prévia, cancelamento, preenchimento pelo percentual, restauração).

### Um editor por vez

- **FR-950**: Com a tabela presente, **no máximo um** cartão MUST estar à vista. Os cartões fora de
  vista MUST continuar no formulário, com todo o conteúdo, e MUST ser enviados em **todo** envio da
  etapa, exatamente como hoje; o conjunto de campos enviados MUST ser o mesmo com e sem a vista.
- **FR-951**: *Editar* MUST pôr à vista o cartão daquele Perfil, com um título que o identifique pelo
  código e pela localidade ou denominação, e MUST marcar a linha como em edição.
- **FR-952**: O editor MUST oferecer *Anterior* e *Próximo*, na ordem da tabela, e *Voltar à lista*.
  Nenhum dos três MUST enviar o formulário, perguntar confirmação ou descartar conteúdo.
- **FR-953**: Ao abrir a etapa, nenhum cartão MUST estar à vista, salvo: (a) o Perfil único
  (`FR-945`); (b) o Perfil do primeiro campo recusado pelo servidor; (c) o Perfil que o endereço
  aponta; (d) quando a tela volta de um envio que não gravou, o Perfil que estava à vista. Nessa ordem
  de precedência. Depois de uma gravação bem-sucedida, nenhum.
- **FR-954**: Quando um envio for barrado pela validação do navegador ou da tela por um campo de um
  Perfil fora de vista, esse Perfil MUST passar a ser o visível **antes** de a mensagem ser
  apresentada, de modo que o campo receba o foco e a mensagem apareça junto dele.
- **FR-955**: Sem script, a etapa MUST ser a de hoje, com todos os cartões à vista e sem tabela.

### Os gestos existentes

- **FR-956**: *Acrescentar Perfil* MUST pôr o cartão novo à vista, com o foco no primeiro campo.
- **FR-957**: A cópia de *Duplicar* MUST entrar logo depois da origem, na tabela e no formulário, e
  MUST passar a ser o cartão visível, com o aviso da `043`.
- **FR-958**: *Remover* MUST continuar pedindo a confirmação de hoje; confirmado, o cartão e a linha
  MUST sair, nenhum cartão MUST ficar à vista, e o foco MUST ir ao *Editar* da linha seguinte, ou da
  anterior quando não houver seguinte. A passagem de dois para um Perfil e de um para dois MUST seguir
  a `FR-945`.
- **FR-959**: O controle do Edital, *Preencher pelo percentual*, *Aplicar aos demais Perfis*, a prévia
  e a confirmação da `051`, o duplicar da `043` e o rascunho local MUST produzir o mesmo resultado
  gravado que produzem hoje, para o mesmo conteúdo.

### A tela

- **UX-116**: A tabela MUST ter cabeçalho de coluna, e o código MUST ser o cabeçalho de cada linha. O
  número de Perfis MUST estar no título dela.
- **UX-117**: O nome acessível de cada *Editar* MUST incluir o código do Perfil (*"Editar P03"*).
- **UX-118**: A linha em edição MUST ser marcada por texto visível e pelo estado de item atual para
  tecnologia assistiva, e nunca só por cor. A situação MUST NOT depender de cor ou ícone.
- **UX-119**: *Editar*, *Anterior* e *Próximo* MUST levar o foco ao título do editor; *Voltar à lista*
  MUST devolvê-lo ao *Editar* da linha de onde saiu.
- **UX-120**: O controle *"Declarado uma vez para todos os Perfis"* e *Preencher pelo percentual* MUST
  vir depois da tabela e antes do editor: são gestos sobre o conjunto, e a tabela é o conjunto.
- **UX-121**: Em tela estreita a tabela MUST NOT provocar rolagem horizontal da página.
- **UX-122**: Nenhum cartão MUST passar a trazer ajuda visível (`FR-428` da `030`); o que a tabela e o
  editor dizem mora fora do cartão.

### Key Entities

- **Linha do Perfil**: o resumo de um Perfil na tabela — identificação, os valores de comparação, a
  situação e a ação. Não é gravada: é leitura do cartão.
- **Situação do Perfil**: a contagem de pendências de publicação que o têm por objeto e o fato de o
  conteúdo na tela diferir do gravado.
- **Perfil em edição**: o único cartão à vista, ou nenhum. É estado da tela, e não do rascunho.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-348**: Com 7 Perfis, a 1280×900, a tabela começa na primeira tela, e a página com um cartão
  aberto mede **no máximo um quarto** dos 14,5 mil px de hoje; com nenhum aberto, cabe em duas telas.
- **SC-349**: Em 100% dos casos de teste num navegador real, o envio barrado por campo de Perfil fora
  de vista abre esse Perfil e põe o foco no campo — nos campos obrigatórios do Perfil, da Modalidade e
  do fato, e nas marcas da validação da tela.
- **SC-350**: Para o mesmo conteúdo, o conjunto de campos que a etapa envia é **idêntico** com a vista
  e sem ela, em Salvar, Avançar, na prévia e no preenchimento pelo percentual.
- **SC-351**: O roteiro de compor os 7 polos do 28/2026 pela duplicação não custa mais cliques que hoje,
  e editar dois Perfis e salvar, num Edital de dois, custa no máximo dois cliques a mais que hoje e
  nenhuma rolagem além de uma tela.
- **SC-352**: 100% das linhas se identificam e dizem a situação sem cor, e a tabela é percorrível por
  cabeçalho de linha e de coluna na árvore de acessibilidade.
- **SC-353**: Nenhum teste da `027`, da `043`, da `051` e do rascunho local muda de resultado, e
  nenhum conteúdo gravado por esses gestos muda.

---

## Assumptions

### D-001 — A vista não é formulário

O editor é o cartão de hoje, e *"estar em edição"* é **estar à vista**: os demais continuam no mesmo
formulário e em todo envio. Um editor que carregasse e gravasse um Perfil por vez resolveria o teto de
mil campos e reabriria as três decisões que o proíbem — a seção do quadro no cartão da `027`, o
duplicar que copia o digitado da `043`, o gesto que lê o digitado da `051` —, todas escritas porque a
gravação da etapa substitui o rascunho e apaga o que não é reenviado. Por isso não há *"Salvar e
editar próximo"*, nem pergunta de alterações não salvas ao trocar de Perfil: nada se perde ao trocar,
e gravar é da etapa inteira.

O mecanismo já existe em produção: a Retificação esconde linhas do mesmo formulário com o filtro e
continua enviando todas.

### D-002 — A tabela nasce no segundo Perfil, e a medição é esta

O contraponto do usuário pediu que o limiar fosse medido antes de congelado. A geometria medida da
etapa (cartão de 1.898 px, o primeiro a 912 px, *Salvar* depois do último) dá, para um Edital de dois
Perfis:

| Tarefa | Hoje | Com a tabela |
|---|---|---|
| Compor os dois, pela duplicação | acrescentar, preencher, duplicar, preencher, rolar ~2 telas até *Salvar* | o mesmo, com *Salvar* logo abaixo do cartão |
| Corrigir um campo em cada e salvar | rolar ~2 telas até o 2º, ~2 de volta ao 1º, ~4 até *Salvar* | *Editar*, *Anterior*, *Salvar*: 2 cliques, sem rolagem longa |
| Comparar as vagas dos dois | rolar ~2 telas entre eles | nenhuma ação |
| Saber qual se está editando | ler o código dentro do campo | o título do editor |

Com dois Perfis a tabela troca rolagem de duas telas por um clique a cada troca, e não acrescenta
clique ao compor. Três seria esperar a pergunta *"qual estou editando?"* aparecer duas vezes para
respondê-la uma. A `SC-351` confere no preview, depois de implementado; se o caso de dois piorar, a
decisão volta ao usuário com a medição.

### D-003 — A situação são dois fatos, e *"em edição"* não é um deles

O contraponto do usuário alertou para a tabela virar um pequeno sistema de estados. A situação diz
duas coisas, das duas fontes que já existem: as pendências de publicação que o servidor já calcula
para a etapa, atribuídas ao Perfil que o caminho do achado nomeia; e a diferença entre o que está na
tela e o que está gravado. *"Recusado"*, *"quadro a repartir"* e *"campo inválido"* não entram: a
recusa e o campo inválido já abrem o Perfil (`FR-953`, `FR-954`), e o quadro já é pendência quando é
regra. *"Em edição"* é seleção, marcada na linha (`UX-118`), e não uma situação a mais.

### D-004 — A tabela é montada pela tela, lendo o formulário

A linha é leitura do cartão, e o cartão é a única fonte: uma linha montada no servidor e atualizada na
tela seriam dois desenhos do mesmo Perfil, que envelhecem separados. O servidor entrega só o que a
tela não sabe — as pendências de cada Perfil e se o que ele devolveu difere do gravado. Sem script,
não há tabela, e a etapa é a de hoje (`FR-955`): é a mesma escolha do filtro da Retificação, que só
existe onde o script existe.

### D-005 — *Voltar à lista* não descarta

Não há *Cancelar* por Perfil. Voltar os campos ao gravado é trivial para um campo de texto e não é para
uma Modalidade acrescentada na tela, que leva junto a linha do quadro. Descartar tudo continua sendo
recarregar a etapa, que é o que o rascunho local já protege. Se o uso pedir, é feature própria.

### Outras premissas

- **O teto de mil campos continua**: esconder cartões não reduz o envio. Registrado em achado próprio,
  com os caminhos de correção; a escolha é do usuário.
- **Mesmo vocabulário**: as frases da linha — cadastro reserva, forma de convocação — são as da tela e
  da Revisão, e não o nome do campo no conteúdo canônico.

---

## Out of Scope

- Gravar por Perfil, mudar a gravação da etapa, e o teto de mil campos.
- Editar na própria linha — inclusive as vagas, que o relatório deixou como candidata a medir.
- *Duplicar* e *Remover* na linha; *Cancelar* por Perfil (`D-005`).
- Filtro, busca e ordenação pela tabela.
- A Classificação, o Cronograma, a Retificação e as demais etapas.
- Componente genérico de coleção: o que servir à Classificação será extraído quando ela entrar.
