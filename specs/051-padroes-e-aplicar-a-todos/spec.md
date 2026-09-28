# Feature Specification: Padrões do Edital e "aplicar a todos"

**Feature Branch**: `claude/nova-051-edital-patterns-499aa7`

**Created**: 2026-09-28

**Status**: Draft

**Input**: pedido do usuário de 28/09/2026. É o **passo 1** da ordem adotada em 27/09
([decisões pendentes](../../doc/decisoes-pendentes-da-consolidacao.md), *"Depois da reavaliação de
27/09"*), feito antes do piloto por decisão do usuário: o piloto deve começar com o operacional
enxuto. Executa a `DP-13` (decidida em 27/09: a regra única do "aplicar a todos"), a forma que a
`DP-17` deixou para as specs (Constituição 1.2.0, Princípio IV) e a `DP-19` (o `RC-136`). Evidência:
[reavaliação de 27/09](../../doc/reavaliacao-pos-consolidacao-2026-09-27.md), §D.2, §D.3, §E.1 e item 1
da *Priorização*; anexos A e D. Fecha a `TF-1` e a `G-001` da `043`.

> **Faixa de identificadores.** Abre em **FR-910**, **SC-340** e **UX-110**, contíguos, por indicação do
> usuário. O teto medido em 28/09/2026 em todas as worktrees e branches remotas era 890, 327 e 104, da
> `050`. As **decisões** reiniciam em `D-001`; decisão de outra spec é citada pelo requisito que a
> registra.

> **Teto proporcional.** O que esta feature acrescenta é **um gesto** — aplicar uma declaração aos
> demais Perfis, com prévia — e **padrões** que só preenchem o vazio. Nenhuma espécie de Alteração e
> nenhum campo no conteúdo publicado. Uma regra de validação sai — o empate no marco de sorteio, que
> é pergunta sem efeito (`FR-928`) — e uma entra, a forma de convocação de quem corta (`FR-943`). O que
> não nomear uma interação a menos, uma decisão a menos ou uma consequência exposta é nota de tarefa.

---

## Por que esta feature existe

**O operador declara Perfil por Perfil o que o Edital declara uma vez.** O marco, os critérios de
desempate, a forma de convocação, a reversão e a janela recursal moram no Perfil, e o Edital os escreve
uma vez: *"o desempate se dará da seguinte forma: a), b), c)"* (140/2025, 6.3.2); *"as convocações
serão feitas por e-mail"* (28/2026, 10.3). O duplicar da `043` só ajuda se o operador inverter a ordem
do assistente, compondo o marco antes de duplicar — e o assistente, na ordem dele, leva os Perfis à
Classificação sem marco nenhum (anexo A, §5.2).

| Edital | Classificação hoje, na ordem do assistente | Com o marco aplicado aos demais |
|---|---:|---:|
| 28/2026 — 7 polos, sorteio | ~72 | ~18 |
| 140/2025 — 16 Perfis, 3 critérios | **~400** | ~30 |
| Multicampi projetado — 66 Perfis | **~1.650** | ~30 |

*Estimativas por custo unitário (anexo A, §3); a verificação desta feature mede a primeira linha.*

**E o operador decide coisas que o sistema sabe.** Declara um corte para dizer que não corta; responde
a pergunta de empate numa ordem que não empata; digita em RFC 3339 o instante que o Cronograma já tem;
escreve duas vezes a mesma regra de sorteio, uma como código e outra como prosa; faz à mão a conta do
quadro que a validação refaz para conferir; e a Etapa decisória nasce na única combinação que a
consolidação sempre recusa (reavaliação, §D.2 e §D.3).

**A correção custa O(N).** Uma Modalidade errada na origem é copiada quinze vezes (`G-001` da `043`) e
se corrige Perfil a Perfil; a Retificação de dado comum é item a item.

**O contrapeso é a Constituição 1.2.0** (Princípio IV): o que o sistema inferir, derivar ou
materializar fica visível antes do ato irreversível, com a origem; e o gesto que alcança N objetos
declara o alcance antes da confirmação. Aqui um padrão errado não fica no rascunho: é publicado, e só
sai por Retificação pública.

**O que não muda.** O conteúdo publicado continua por Perfil, e nada herda de nada: cada destino
recebe o seu valor. A validação da publicação continua a mesma para o que existe; a Retificação, a API
e as exceções continuam produzindo qualquer configuração, e os validadores continuam necessários.

---

## Clarifications

### Session 2026-09-28

- Q: Ao aplicar uma Modalidade aos demais, a declaração *"esta é a ampla concorrência"* vai junto? → A:
  **Sempre, substituindo.** Ela é parte da unidade Modalidade: se a origem a aponta como a ampla, o
  destino passa a apontar a de mesmo código, mesmo que apontasse outra; se a origem não a aponta e o
  destino sim, o destino deixa de apontá-la. A prévia mostra o *antes → depois* (`FR-925`).
- Q: O marco aplicado leva o método **próprio** do sorteio? → A: **Não leva, e o destino fica fora.**
  Marco com método próprio — na origem ou no destino — fica fora do alcance, com o motivo: o método
  próprio existe para divergir (`DP-13`, *fora da tabela*), e aplicar o resto deixaria o destino
  sorteando por outro método sem que a prévia o mostrasse (`FR-922`).
- Q: Como a Revisão diz a origem de um valor materializado? → A: **Pelo registro do gesto**: autor,
  instante, origem, destinos e valor aplicado, fora do conteúdo publicado. A Revisão o atribui ao
  gesto enquanto o valor do destino for o gravado; padrões e derivações saem por comparação
  (`FR-934`, `FR-935`).
- Q: Que quantidade o quadro sugere quando o percentual não dá inteiro? → A: **A que a regra
  normativa declarar**: o campo `rounding` da regra normativa ganha consumidor, é pedido uma vez por
  Modalidade na composição, e governa a sugestão. Sem ele declarado, a sugestão mostra a faixa e não
  preenche (`FR-932`, `FR-933`).
- Q: O Perfil que corta e não declara forma de convocação é cobrado na publicação? → A: **Impede
  publicar** (`FR-943`). Com a forma declarada uma vez no Edital, cumprir custa um gesto; é a porta
  que a `050` (`D-002`) deixou para depois do ato imutável.

---

## User Scenarios & Testing *(mandatory)*

**Ator.** Quem elabora o Edital (composição) e quem o retifica (Retificação) — as mesmas permissões de
hoje. Esta feature não cria papel, permissão nem capacidade de autoridade nova.

**Unidade.** O Perfil de Vaga é o destino do gesto. A **origem** é uma declaração de um Perfil — o
marco, a Modalidade, a forma de convocação, a reversão — e o **alcance** é o conjunto de Perfis
destino, por padrão *"todos os demais"*.

### User Story 1 — O marco de um Perfil aplicado aos demais, na composição (Priority: P1)

Quem elabora compõe o marco do primeiro Perfil — forma da ordem, Etapas, arredondamento, recurso,
corte, critérios de desempate — e pede para aplicá-lo aos demais. Antes de qualquer gravação, a tela
mostra, Perfil a Perfil, o que acontece: o marco **nasce** onde não há marco; os campos são
**substituídos** onde há um marco, com o *antes → depois*; **nada muda** onde já é igual; e o Perfil
fica **fora do alcance**, com o motivo, onde não há correspondência segura. Quem elabora exclui o
Perfil que diverge de propósito, e confirma uma vez.

**Why this priority**: é o maior laço humano que restou na composição — ~400 das ~690 interações do
140/2025 no fluxo linear, e cinco vezes a etapa de Perfis no Edital de 66 Perfis. Sozinha, esta
história torna indiferente a ordem de compor e duplicar.

**Independent Test**: num Edital em elaboração com 7 Perfis sem marco, compor o marco do primeiro,
pedir a aplicação, conferir na prévia 6 *nasce*, confirmar, e conferir 7 marcos independentes, cada
um com o código e a denominação derivados do próprio Perfil e os critérios apontando os fatos do
próprio Perfil.

**Acceptance Scenarios**:

1. **Given** 7 Perfis, só o primeiro com marco, **When** quem elabora pede para aplicar esse marco aos
   demais, **Then** a tela declara os 6 destinos com o efeito *"nasce"*, o código e a denominação que
   cada marco terá, **e nada é gravado**.
2. **Given** a mesma prévia, **When** quem elabora confirma, **Then** cada destino ganha um marco
   próprio, com identidade própria, código e denominação derivados do destino, e os critérios de
   desempate apontando o fato **de mesmo código** do destino; editar um marco depois não altera os
   outros.
3. **Given** um destino que já tem um marco, **When** a prévia é mostrada, **Then** o destino aparece
   com *"substitui"* e, campo a campo, o *antes → depois* de cada campo que muda; o código e a
   denominação do destino não mudam.
4. **Given** um destino cujo marco já é igual ao da origem, **Then** ele aparece com *"sem mudança"*.
5. **Given** um destino com dois marcos, **Then** ele aparece *"fora do alcance"*, com o motivo — não
   há como saber qual dos dois corresponde —, e a confirmação não o toca.
6. **Given** uma origem cujo critério compara o fato `NASC` e um destino que não declara fato de código
   `NASC`, **Then** o destino fica *"fora do alcance"*, com o fato que falta nomeado.
7. **Given** um corte de quantidade fixa na origem, **Then** a prévia destaca em separado, em cada
   destino, a quantidade anterior e a aplicada.
8. **Given** a prévia aberta, **When** quem elabora desmarca dois destinos e confirma, **Then** os dois
   ficam exatamente como estavam.
9. **Given** a prévia aberta, **When** o que está digitado na origem ou num destino muda antes da
   confirmação, **Then** a confirmação é recusada, nada é gravado, e a tela mostra a prévia de agora.

---

### User Story 2 — O que o Edital declara uma vez é pedido uma vez (Priority: P1)

A forma de convocação, a reversão e a Modalidade de Concorrência são declaradas no Perfil, e o Edital
as declara uma vez. Na etapa Perfis, quem elabora declara a forma de convocação e a reversão num
controle do Edital, que as aplica aos Perfis pela mesma prévia; e, numa Modalidade, pede para
aplicá-la aos demais Perfis pelo **código**: ela nasce onde o código falta, e tem os campos
substituídos onde ele existe, sem nunca remover Modalidade nenhuma.

**Why this priority**: é a correção depois de duplicar (`G-001` da `043`) — a Modalidade esquecida ou
errada na origem, que hoje custa ~40 interações no 28/2026 e ~100 no 140/2025 —, e a forma de
convocação que o 28/2026 e o 140/2025 declaram uma vez cada.

**Independent Test**: num Edital com 7 Perfis duplicados, sem a PcD, acrescentar a PcD no primeiro e
aplicá-la aos demais; conferir 6 *nasce* na prévia, com as Modalidades que cada destino já tem;
confirmar; conferir a PcD nos 7, cada uma com identidade própria, e o quadro de cada Perfil intocado.

**Acceptance Scenarios**:

1. **Given** 7 Perfis sem forma de convocação, **When** quem elabora declara *"por mensagem
   individual"* no controle do Edital e confirma a prévia, **Then** os 7 Perfis passam a declarar a
   forma; **Given** um Perfil novo acrescentado depois, **Then** ele nasce com a forma que todos os
   demais declaram, e a Revisão diz de onde ela veio.
2. **Given** a Modalidade `PCD` no primeiro Perfil e um destino sem ela, **Then** a prévia diz
   *"nasce"* nele, e lista as Modalidades que ele já tem — é o que protege o destino que declarou a mesma
   cota sob outro código.
3. **Given** um destino que já declara `PCD` com outro percentual, **Then** a prévia diz *"substitui"*
   com o percentual *antes → depois*; o código não muda, e a linha do quadro do destino não é tocada.
4. **Given** um destino com uma Modalidade que a origem não tem, **Then** ela continua lá depois da
   confirmação: a ação opera sobre uma Modalidade, e não sobre o conjunto.

---

### User Story 3 — Padrões que valem também para o Edital pequeno (Priority: P1)

O marco único nasce com o corte que diz *"convoca quantas vagas o quadro publicar"*; o marco de
sorteio não pergunta o empate que não ocorre; o instante do sorteio é escolhido entre os Eventos do
Cronograma; a prosa das regras do sorteio é gerada da regra escolhida; a Etapa decisória nasce
eliminatória; e o quadro de vagas é sugerido pelo percentual. Todo padrão só preenche o que está vazio,
fica editável, e aparece na Revisão com a origem.

**Why this priority**: o 78/2026 não ganha nada com "aplicar a todos" — tem dois Perfis — e é o
Edital que o piloto mais provavelmente começa. Os padrões são o que o reduz, e eliminam as decisões
que o operador não tem como acertar sozinho.

**Independent Test**: num Edital em elaboração com um Perfil de sorteio, acrescentar o marco; conferir
o corte já declarado com o alvo do quadro, sem suplentes e sem Etapa governada; não responder empate;
escolher o Evento do sorteio no método comum; escolher as duas regras sem digitar a prosa; publicar;
conferir que o documento traz a prosa gerada e o instante do Evento.

**Acceptance Scenarios**:

1. **Given** um Perfil sem marco, **When** quem elabora acrescenta o marco, **Then** o corte já vem
   declarado: alvo *"quantas vagas o quadro publicar"*, zero suplentes, *"não governa Etapa alguma"*; o
   empate e a faixa seguinte continuam perguntados, porque não têm padrão (`FR-182`, `FR-226` da
   `014`).
2. **Given** um Perfil com um marco, **When** quem elabora acrescenta o segundo, **Then** o segundo
   nasce **sem** corte: um marco intermediário não é o final.
3. **Given** um marco que ordena por sorteio, **Then** a pergunta *"Empate na última posição"* não é
   feita, e o marco publica sem ela; **Given** um marco de sorteio publicado antes desta feature, com o
   empate declarado, **Then** o valor publicado continua lá.
4. **Given** um Cronograma com o Evento *"Sorteio eletrônico"*, **When** quem elabora o escolhe como o
   instante do sorteio, **Then** o método grava o instante de início do Evento, e a Revisão diz que ele
   veio daquele Evento.
5. **Given** a regra de normalização escolhida e a prosa em branco, **When** o passo é gravado, **Then**
   a prosa gravada é a frase canônica da regra; **Given** a prosa digitada, **Then** o digitado vale.
6. **Given** uma Etapa nova, **When** quem elabora escolhe *"Com decisão, sem nota"*, **Then** ela vem
   marcada eliminatória — a combinação que a consolidação aceita —, e continua editável.
7. **Given** um Perfil de 40 vagas com Modalidades de 25% e 5%, **Then** a etapa Perfis sugere 10 e 2
   nas linhas do quadro, com a conta à vista, e o operador aceita a sugestão num gesto; **Given** 7
   vagas e 25% com *"a fração vira vaga"*, **Then** a sugestão é 2; **Given** o mesmo sem arredondamento
   declarado, **Then** a tela diz *"entre 1 e 2"* e não preenche.
9. **Given** um Perfil com corte e sem forma de convocação, **Then** a Revisão impede a publicação e
   aponta o controle do Edital na etapa Perfis.
8. **Given** um Edital publicado, **When** ele é retificado, **Then** nenhum padrão é aplicado a
   conteúdo algum (`FR-421` da `030`).

---

### User Story 4 — A Revisão mostra a origem e o que não se corrige depois (Priority: P1)

Antes de submeter, a Revisão mostra, junto de cada valor que o sistema inferiu, derivou ou
materializou, de onde ele veio — *"padrão do sistema"*, *"do Evento Sorteio eletrônico"*, *"aplicado a
partir do Perfil LP01"* — e reúne num bloco os campos que **não se corrigem depois de publicados**, com
os valores deste Edital e a razão escrita no contrato de mutabilidade.

**Why this priority**: é a forma que a Constituição 1.2.0 exige para as duas histórias anteriores, e
sem ela nenhuma das duas pode entrar. É também o `RC-136`: uns 15 campos não se corrigem depois de
publicados, e hoje o operador só descobre isso na Retificação.

**Independent Test**: compor um Edital com um marco aplicado a 6 Perfis, o corte padrão, o instante
do Evento e a prosa gerada; abrir a Revisão; conferir a origem de cada um; conferir o bloco dos campos
definitivos com os códigos dos Perfis e das Modalidades, o tipo dos Eventos e a espécie do corte;
editar à mão um dos marcos aplicados e conferir que a Revisão deixa de chamá-lo de aplicado.

**Acceptance Scenarios**:

1. **Given** 7 Perfis cujos marcos foram materializados de LP01 e não mudaram, **Then** a Revisão, no
   grupo dos 7, diz que eles foram aplicados a partir de LP01, por quem e quando.
2. **Given** um desses marcos editado à mão depois, **Then** a Revisão não o atribui mais ao gesto.
3. **Given** um corte igual ao padrão, **Then** a Revisão diz *"padrão do sistema"* ao lado dele.
4. **Given** qualquer Edital em elaboração, **Then** a Revisão lista os campos que não se corrigem
   depois de publicados, com os valores declarados, e a lista é derivada do contrato de mutabilidade —
   campo novo não retificável aparece nela no dia em que entra no contrato.
5. **Given** os cartões da composição, **Then** nenhum passa a trazer ajuda visível (`FR-428` da
   `030`): o aviso mora na Revisão.

---

### User Story 5 — "Aplicar a todos" na Retificação, campo a campo (Priority: P2)

Quem retifica um Edital publicado corrige o critério de desempate, a janela recursal, o corte, a forma
de convocação, a reversão ou uma Modalidade num Perfil, e pede para aplicar a mesma alteração aos
demais. A conferência antes da confirmação agrupa as N Alterações do gesto, com o *antes → depois* de
cada destino e as consequências: as ordens que ficam obsoletas, os recortes que nascem sem ordem, os
marcos com ato já divulgado cuja janela muda. Tudo sai num ato, com uma versão e um documento.

**Why this priority**: é a parte difícil — o contrato de mutabilidade, as guardas da `048`, a
atomicidade —, e a composição pode ser entregue sem esperá-la. Rende na correção pós-publicação: trocar
um critério nos 16 Perfis do 140/2025 passa de ~110 para ~10 interações.

**Independent Test**: num Edital publicado de 7 Perfis, retificar a janela recursal do marco do
primeiro de 2 para 3 dias, aplicar aos demais, conferir 6 substituições e a lista dos marcos com ato
divulgado, publicar a Retificação, e conferir 7 Alterações num ato só.

**Acceptance Scenarios**:

1. **Given** um critério trocado no primeiro Perfil, **When** aplicado aos demais, **Then** cada destino
   recebe a remoção e o acréscimo que a `048` já admite (`FR-792`), e a ordem emitida de cada marco
   alcançado fica obsoleta, contada na conferência.
2. **Given** um destino em que a diferença alcançaria um campo não retificável — a espécie do alvo do
   corte, a Etapa governada, as Etapas do marco —, **Then** o destino inteiro fica fora do alcance, com
   o campo nomeado, e nenhum campo dele é aplicado.
3. **Given** a janela aplicada a marcos em que uma já foi divulgada, **Then** a conferência os nomeia
   antes da confirmação.
4. **Given** o gesto confirmado, **Then** sai **um** ato de Retificação, com uma versão, um documento e
   uma Alteração por destino e campo.

---

### Edge Cases

- **Origem que é a única.** Um Edital de um Perfil não oferece o gesto: não há destino.
- **Origem com dois marcos.** O gesto é do marco, e não do Perfil: aplicar o segundo marco de LP01
  alcança os destinos pela mesma regra — onde há um marco, ele é substituído pelo segundo de LP01; é o
  que a prévia mostra, e é por isso que ela mostra.
- **Perfil novo, ainda não gravado.** Destino que só existe na tela entra no gesto como qualquer outro,
  e é gravado junto.
- **Fato com o mesmo código e outro tipo.** Um critério *"maior idade"* aponta um fato de data; o
  destino que declara `NASC` como número fica fora do alcance, com o motivo — correspondência que muda o
  sentido do critério não é correspondência.
- **Modalidade com o mesmo código e outra denominação.** É o caso da correção, e é substituição.
- **Modalidade equivalente sob outro código** (`PCD` e `DEF`). Não é reconhecida sem casar nome
  (`R-006` da `025`); só a prévia a protege, listando as Modalidades de cada destino.
- **A Modalidade apontada como ampla na origem.** O destino passa a apontar a de mesmo código,
  substituindo a que apontasse — e a prévia mostra, porque é a única unidade do gesto que muda um
  valor do Perfil fora da própria Modalidade.
- **Marco com método próprio de sorteio.** Fica fora do alcance, na origem ou no destino.
- **Reversão num destino sem lista reservada.** Fica fora do alcance: a validação já a recusa ali.
- **Destino já publicado com recorte novo.** Na Retificação, a Modalidade que nasce produz recorte sem
  ordem (`FR-781` da `048`), e a conferência conta.
- **O padrão e o Edital publicado.** Nada deste texto alcança conteúdo publicado nem Retificação: os
  padrões nascem no cartão novo, ou preenchem o vazio do rascunho, e a Retificação não os vê chegar.
- **O Evento do sorteio que muda de data depois.** O instante gravado é o do dia em que foi escolhido.
  A Revisão compara: se o Evento mudou, deixa de dizer que o instante veio dele, e a pendência que
  compara os dois continua sendo a da publicação.
- **Duas pessoas compondo o mesmo Edital.** A gravação por substituição já tem o risco; o gesto não o
  amplia, porque grava pelo mesmo caminho e com a mesma revisão esperada.

---

## Requirements *(mandatory)*

### A regra única (`DP-13`)

- **FR-910**: "Aplicar a todos" MUST ser **materialização**: o gesto grava em cada destino um valor
  próprio, com identidade própria, e nada guarda vínculo com a origem (`D-005` e `D-006` da `043`). O
  conteúdo publicado MUST continuar por Perfil, e nenhum destino MUST herdar valor de outro objeto no
  conteúdo publicado.
- **FR-911**: Nos destinos selecionados, o gesto MUST substituir integralmente a declaração
  correspondente, na fronteira que esta spec define para cada unidade; se a declaração não existir e
  puder nascer, MUST criar uma cópia independente. O destino MUST ficar **fora do alcance** quando (a)
  não há correspondente inequívoco, (b) o contrato não permite criar nem substituir a unidade inteira,
  ou (c) a ação opera sobre um item e o destino tem outros: estes ficam, e nunca são removidos.
- **FR-912**: O marco inteiro MUST NOT ser unidade substituível: ele só nasce onde falta. Com um marco no
  destino, os campos do marco são substituídos; com dois ou mais, o destino MUST ficar fora do
  alcance.
- **FR-913**: O código e a denominação do marco MUST NOT ser substituídos; o código da Modalidade MUST
  NOT ser substituído; o marco que nasce MUST ter código e denominação derivados do destino
  (`FR-420` da `030`).
- **FR-914**: Um critério de desempate que aponta fato do Perfil MUST encontrar, no destino, o fato de
  **mesmo código e mesmo tipo**; sem ele, o destino MUST ficar fora do alcance, com o fato nomeado.
  Etapa é do Edital, e a referência a ela MUST ser mantida.
- **FR-915**: A fronteira com a `FR-421` da `030` MUST valer por escrito e no código: **o padrão só
  preenche o vazio** — cartão novo ou campo sem declaração, nunca conteúdo publicado nem Retificação —;
  **aplicar a todos substitui**, e só por gesto com prévia.

### A prévia e a confirmação (Constituição 1.2.0, Princípio IV)

- **FR-916**: Antes de gravar, o gesto MUST mostrar, para cada Perfil do Edital que não é a origem,
  exatamente um de quatro efeitos — **nasce**, **substitui**, **sem mudança** ou **fora do alcance** —,
  e, em *substitui*, cada campo que muda com o valor anterior e o aplicado; em *fora do alcance*, o
  motivo.
- **FR-917**: Quando a unidade traz quantidade fixa de corte, a prévia MUST destacar em separado, em cada
  destino, a quantidade anterior e a aplicada.
- **FR-918**: O alcance padrão MUST ser *"todos os demais Perfis"* em que o efeito não é *fora do
  alcance*, e quem aplica MUST poder excluir destinos antes da confirmação; destino excluído MUST NOT
  ser tocado.
- **FR-919**: A confirmação MUST aplicar exatamente o que a prévia mostrou: ela MUST carregar a
  identidade do que foi mostrado, e o sistema MUST recusá-la, sem gravar nada, quando o efeito de agora
  diverge, mostrando a prévia de agora.
- **FR-920**: O gesto MUST ser atômico: grava todos os destinos confirmados ou nenhum, pelo mesmo caminho
  de gravação da etapa e sob a mesma revisão esperada.
- **FR-921**: O gesto MUST ser registrado com autor, instante, a unidade de origem e os destinos
  alcançados com o efeito de cada um.

### As unidades, na composição

- **FR-922**: **Marco** (etapa Classificação). A unidade MUST ser o marco sem a identidade: a forma da
  ordem, as Etapas enumeradas, a combinação, a normalização, o arredondamento, a janela recursal, a
  regra de corte e a lista de critérios de desempate. A ausência na origem de um bloco opcional —
  janela, corte — MUST ser aplicada como ausência, e a prévia MUST mostrá-la como *"antes → nada
  declarado"*. Marco com método **próprio** de sorteio — na origem ou no destino — MUST ficar fora do
  alcance, com o motivo; o método próprio nunca é levado nem apagado pelo gesto.
- **FR-923**: **Critérios de desempate**. A lista MUST ser substituída inteira, como unidade: é o que o
  Edital declara. Lista idêntica MUST produzir *sem mudança*.
- **FR-924**: **Modalidade** (etapa Perfis), pelo código. MUST nascer onde o código falta e MUST ter
  substituídos, onde existe, a denominação, a descrição e a regra normativa declarada na tela
  (percentual, fundamento, versão); MUST NOT remover Modalidade nem sincronizar o conjunto; MUST NOT
  levar a linha dela no quadro, porque a quantidade é do Perfil. A prévia MUST listar, por destino, as
  Modalidades que ele já tem.
- **FR-925**: A declaração de *"esta é a ampla concorrência"* MUST fazer parte da unidade Modalidade:
  se a origem aponta a Modalidade como a ampla, o destino MUST passar a apontar a sua de mesmo código,
  substituindo a que apontasse; se a origem não a aponta e o destino a aponta, o destino MUST deixar
  de apontá-la. A prévia MUST mostrar o *antes → depois* da ampla de cada destino.
- **FR-926**: **Forma de convocação** e **reversão**. A etapa Perfis MUST oferecê-las num controle do
  Edital, que as aplica aos Perfis pela prévia desta feature; a reversão MUST deixar fora do alcance o
  Perfil sem lista reservada. O Perfil novo MUST nascer com a forma de convocação e a reversão que
  **todos** os Perfis do Edital declaram iguais, e sem nenhuma quando divergem.

### Os padrões (§D.3 da reavaliação)

- **FR-927**: O marco acrescentado a um Perfil **sem marco** MUST nascer com a regra de corte declarada:
  alvo *"quantas vagas o quadro publicar"*, zero suplentes, *"não governa Etapa alguma"*. O desfecho do
  empate e a faixa seguinte MUST continuar sem padrão. O segundo marco de um Perfil MUST nascer sem
  corte.
- **FR-928**: O marco que ordena por sorteio MUST NOT perguntar o desfecho do empate na última posição,
  e a validação da publicação MUST NOT exigi-lo desse marco; o valor já declarado MUST continuar sendo
  preservado, lido e publicado.
- **FR-929**: O instante da ocorrência do sorteio — do método comum e do método próprio — MUST poder ser
  escolhido entre os Eventos do Cronograma do Edital; escolhido um Evento e sem instante digitado, o
  valor gravado MUST ser o início do Evento, no formato publicado de hoje. Digitar continua possível, e
  o digitado vale.
- **FR-930**: A prosa da regra de normalização e a da regra de substituição do sorteio MUST ser geradas da
  regra escolhida quando não digitadas; a frase gerada MUST ser a mesma que o documento publicado
  usaria para a regra.
- **FR-931**: A Etapa acrescentada MUST nascer numa configuração que a consolidação aceita: ao escolher
  *"Com decisão, sem nota"*, ela MUST vir marcada eliminatória, e continuar editável.
- **FR-932**: A etapa Perfis MUST sugerir, em cada linha de lista reservada do quadro, a quantidade que
  o percentual declarado produz sobre as vagas imediatas, arredondada pela regra de arredondamento
  que a Modalidade declara, com a conta à vista, e MUST oferecer preencher com a sugestão as linhas
  vazias do Perfil num gesto. Sem arredondamento declarado, a sugestão MUST mostrar a faixa entre o
  piso e o teto e MUST NOT preencher nada quando eles diferem.
- **FR-933**: O `rounding` da regra normativa MUST ser pedido uma vez por Modalidade na composição, numa
  lista fechada — *a fração vira vaga*, *fração de meio ou mais vira vaga*, *a fração é desprezada* —,
  opcional, e MUST ser o consumidor da sugestão da `FR-932`; continua não retificável, como o contrato
  já diz. Os campos `calculation`, `distribution` e `callRules` MUST continuar não pedidos na
  composição nem na Retificação. Nos quatro, o valor que um Edital publicado ou um rascunho guarda
  MUST continuar preservado — inclusive quando a etapa Perfis é gravada —, e nenhuma migration MUST
  apagá-lo; valor que não é da lista fechada MUST ser preservado e lido como *"declarado fora da
  lista"*, sem sugestão.
- **FR-943**: O Perfil que declara regra de corte em algum marco e não declara forma de convocação MUST
  produzir achado **impeditivo** na publicação, que diga a consequência — a convocação daquele Perfil
  seria recusada — e aponte o controle do Edital na etapa Perfis. Edital já publicado não é
  revalidado por isso.

### A Revisão (Constituição 1.2.0; `DP-19`)

- **FR-934**: A Revisão MUST mostrar, junto de cada valor que coincide com o que um padrão, uma
  derivação ou um gesto de aplicação produziria, a origem desse valor: *"padrão do sistema"*, o Evento
  de onde veio, a regra de onde a prosa foi gerada, a sugestão pelo percentual, a forma de convocação
  e a reversão que o Perfil novo recebeu dos demais, ou o Perfil de onde foi aplicado, com quem e
  quando.
- **FR-935**: A origem *"aplicado a partir de"* MUST valer só enquanto o valor do destino for o que o
  gesto gravou; editado depois, a Revisão MUST deixar de atribuí-lo ao gesto.
- **FR-936**: A Revisão MUST reunir, antes da submissão, os campos que **não se corrigem depois de
  publicados** — os de natureza não retificável e os estruturais do contrato de mutabilidade —, com o
  valor que este Edital declara em cada um e a razão escrita no contrato. A lista MUST ser derivada do
  contrato, e não de uma lista própria.
- **FR-937**: Nenhum cartão da composição MUST passar a trazer ajuda visível sobre isso (`FR-428` da
  `030`).

### A Retificação (P2)

- **FR-938**: A Retificação MUST oferecer o gesto para as unidades retificáveis — critérios de desempate,
  janela recursal, regra de corte, os campos retificáveis do marco, forma de convocação, reversão e
  Modalidade —, **campo a campo**: o gesto produz, em cada destino, as Alterações das espécies que já
  existem, e MUST NOT substituir objeto inteiro.
- **FR-939**: Quando qualquer diferença num destino alcançar campo não retificável, o destino **inteiro**
  MUST ficar fora do alcance, com o campo nomeado; MUST NOT haver aplicação parcial.
- **FR-940**: O nascimento por Retificação MUST obedecer às guardas da `048`: a janela nasce só
  concedendo (`FR-787`); o corte nasce com a guarda da Etapa com Resultado (`FR-789`); a regra normativa
  não nasce em Modalidade publicada (`D-001` da `048`).
- **FR-941**: O gesto MUST produzir **um** ato de Retificação, com uma versão, um documento e o mesmo
  histórico (`FR-795` da `048`), e a conferência antes da confirmação (`FR-800` da `048`) MUST agrupar as
  Alterações do gesto e declarar as consequências: as ordens que ficam obsoletas, os recortes que nascem
  sem ordem e os marcos com ato divulgado cuja janela muda.
- **FR-942**: O contrato de mutabilidade MUST continuar sendo a única fonte do que se retifica
  (`FR-803` da `048`). A leitura da `FR-802` da `048` que esta feature adota MUST ficar escrita: ela
  impede espécie nova e genérica de Alteração, e não impede uma interface em lote que produza várias
  Alterações já admitidas, cada uma validada pelo contrato e registrada no mesmo ato.

### A tela

- **UX-110**: O gesto MUST estar no cartão da unidade de origem, com o alcance padrão no rótulo —
  *"Aplicar aos demais Perfis (6)"* —, e MUST NOT ser oferecido quando não há destino.
- **UX-111**: A prévia MUST listar os destinos na ordem dos Perfis, com o código e a denominação de cada
  um, o efeito em palavras e uma caixa de inclusão marcada por padrão; *fora do alcance* MUST aparecer
  sem caixa, com o motivo.
- **UX-112**: O *antes → depois* MUST usar os rótulos e as frases da Revisão e do documento, e nunca o
  caminho do conteúdo canônico.
- **UX-113**: A prévia MUST dizer, antes do botão, quantos destinos serão tocados e com que efeito —
  *"6 nascem, 1 muda"* —, e o botão MUST repetir o número.
- **UX-114**: A origem na Revisão MUST aparecer ao lado do valor, em texto, e MUST NOT depender de cor
  ou ícone.
- **UX-115**: O bloco dos campos definitivos MUST vir antes do botão de submeter, e cada linha MUST dizer
  o campo, o valor e por que não se corrige.

### Key Entities

- **Unidade aplicável**: a declaração de um Perfil que o gesto leva — marco (sem identidade), lista de
  critérios, Modalidade (pelo código), forma de convocação, reversão; cada uma com a sua fronteira.
- **Efeito por destino**: *nasce*, *substitui* (com os campos e o *antes → depois*), *sem mudança*,
  *fora do alcance* (com o motivo). Não é gravado; é a prévia.
- **Registro do gesto**: autor, instante, unidade de origem, destinos alcançados e o valor aplicado a
  cada um — o que a Revisão lê para dizer a origem enquanto o valor não mudar. Fica fora do conteúdo
  publicado.
- **Arredondamento da reserva**: a regra, declarada na Modalidade, que transforma o percentual em
  quantidade de vagas — o que a sugestão do quadro aplica.
- **Origem de valor**: o que a Revisão diz ao lado de um valor — padrão, derivação (Evento, regra),
  gesto de aplicação.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-340**: Na etapa Classificação de um Edital com a estrutura do 28/2026 (7 polos idênticos, marco
  de sorteio), compor os 7 marcos custa **no máximo 1/3** das interações de hoje, medidas pelo mesmo
  roteiro, antes e depois, no preview.
- **SC-341**: Num Edital de 16 Perfis com marco de 3 critérios, compor os 16 marcos a partir de um custa
  um gesto de aplicação e uma confirmação a mais que compor o primeiro: a curva deixa de crescer com o
  número de Perfis.
- **SC-342**: Em 100% dos casos de teste, nenhum destino é alterado sem ter aparecido na prévia com o
  efeito que recebeu, e nenhum destino excluído ou fora do alcance é alterado.
- **SC-343**: Em 100% das divergências provocadas entre prévia e confirmação, a confirmação é recusada
  e nada é gravado.
- **SC-344**: Nenhum conteúdo publicado muda por efeito desta feature: os Editais publicados antes dela
  produzem o mesmo conteúdo, o mesmo documento e a mesma validação.
- **SC-345**: O Edital de um Perfil com marco de sorteio publica sem responder o empate, sem digitar o
  instante nem a prosa das regras, e com o corte vindo do padrão — **ao menos 5 respostas a menos** que
  hoje no marco: o empate, o instante, as duas prosas e a espécie do alvo, os suplentes e a Etapa
  governada do corte, que hoje são sete.
- **SC-346**: 100% dos campos não retificáveis e estruturais do contrato de mutabilidade que o Edital
  declara aparecem no bloco dos campos definitivos da Revisão.
- **SC-347**: Na Retificação, trocar um critério de desempate em N Perfis custa um gesto e uma
  confirmação, qualquer que seja N, e produz N Alterações num ato só.

---

## Assumptions

### D-001 — A materialização acontece no envio da etapa, e não num segundo caminho

O gesto lê o que está **digitado** na etapa — como o duplicar (`D-002` da `043`) —, mostra a prévia e,
confirmado, grava pela mesma gravação por substituição da etapa. Gravar no servidor por um caminho
próprio daria duas maneiras de um marco entrar no rascunho, e a gravação seguinte da etapa apagaria o
que o formulário não reenviasse (a mesma razão da `D-001` da `043`).

### D-002 — A origem de um padrão é lida por comparação; a de um gesto, pelo registro do gesto

O padrão e a derivação são funções do contexto: a Revisão sabe se o corte é o padrão, se o instante é
o de um Evento e se a prosa é a da regra, comparando. O gesto não é função do contexto, e por isso é
registrado; a Revisão atribui o valor ao gesto só enquanto ele for o valor gravado pelo gesto. Nenhum
registro de proveniência entra no conteúdo publicado (`D-006` da `043`).

### D-003 — A forma de convocação do Edital não é campo do Edital

"Declarada uma vez no Edital" é um controle na etapa Perfis que aplica a forma aos Perfis, e não um
campo novo na raiz do conteúdo. Um campo na raiz, lido pelos Perfis, seria herança no conteúdo
publicado — o que o usuário tirou do escopo.

### Outras premissas

- **O teste operacional da `DP-18` não foi feito.** As estimativas são as do anexo A; o que o teste
  poderia mudar está registrado no plano.
- **A classificatória derivada de o marco enumerar a Etapa** (§D.3) não entra: muda a validação de
  conteúdo existente (`milestone_stage_not_classificatory`) e não reduz interação na composição.
- **A "língua do Edital" no critério** (*"maior idade" cria o fato*) não entra: fazer o fato nascer é
  outra frente (`DP-13`, *fora da tabela*).

---

## Out of Scope

- Herança no conteúdo publicado.
- Modelos de Edital por família.
- A spec do documento oficial (`DP-20`).
- Documentos Exigidos: o recorte da `044` já é o "aplicar a todos" deles.
- Quadro de vagas por gesto de aplicação, método próprio do sorteio aplicado isoladamente, textos do
  Perfil, fatos declarados (`DP-13`, *fora da tabela*).
- Remover Modalidade, sincronizar o conjunto, substituir o marco inteiro.
