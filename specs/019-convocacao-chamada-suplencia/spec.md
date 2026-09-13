# Feature Specification: Convocação, Chamada e Suplência

**Número:** `019` · **Diretório:** `specs/019-convocacao-chamada-suplencia`
**Feature Branch:** `claude/avaliar-implementacoes-recentes-9c284e`
**Criada:** 2026-09-12
**Estado:** decisões fechadas em 12/09/2026 — `D-006` a `D-010` pelo `$speckit-clarify`, e a
`D-011` depois de o `$speckit-plan` achar a contradição da §1.0. Pronta para replanejamento.

**Faixa de identificadores desta feature:** `FR-264`+, `SC-085`+, `UX-035`+. A faixa é global desde
a `024`: o teto foi medido em `c746adf` (`FR-263`, `SC-084`, `UX-034`) e não reinicia.

> **Esta feature não conta vaga e não escolhe candidato.** A fronteira é a **decisão de fronteira**
> da `014`, tomada pelo usuário em 11/09/2026, que a `016` herdou como primeira decisão sua:
>
> ```
> "analisar o próximo candidato da ordem"   → 014
> "quantas vagas ainda não foram ocupadas"  → 016
> "convocar e comunicar o candidato"        → 019
> ```
>
> A `016` entrega o déficit; a `014` entrega a faixa e o teto de suplentes; a `015` entrega a ordem.
> Esta feature pratica o ato que alcança a pessoa, registra o que ela respondeu, e chama o próximo
> quando a vaga vaga.

---

## 1. O achado que organiza a feature

**O sistema já sabe dizer quantas vagas faltam, e não tem como chamar ninguém para nenhuma delas.**
A `016` fechou o cálculo em 12/09/2026: a apuração diz `publicadas / efetivas / ocupadas / faltando`
por recorte, e o déficit causa a faixa seguinte pela `014`. Mas "ocupada", lá, é uma leitura de
conjunto — *dentro da faixa* ∩ *habilitada*, em `ocupacao/domain/apuracao.py` — e nenhum fato do
mundo participa dela: ninguém foi chamado, ninguém aceitou, ninguém desistiu.

**Onze Editais da amostra param exatamente aqui.** A avaliação de 12/09
([documento](../../doc/avaliacao-de-capacidade-editais-2026-09-12.md)) mede *condução* em 10 de 11 e
*corte* em 8 de 11 — e **convocação em 0 de 11**. É a única lacuna comum a todos eles, e a única que
não tem nenhuma parte construída.

**E há uma consequência de fronteira que esta feature não pode empurrar para frente.** Enquanto
desistência não existe, a contagem da `016` é verdadeira; no instante em que existir, um habilitado
dentro da faixa que desistiu continuaria sendo contado como ocupante de vaga. **A `Q-1` fechou isso
em 12/09/2026** (`D-006`): a contagem continua sendo uma só, a da `016`, e o desfecho entra nela
como exclusão — na emissão seguinte, nunca retroativamente.

### 1.0 E a exclusão sozinha não move o número — medido

**O `$speckit-plan` achou uma contradição funcional nesta spec, e ela se mede.** A apuração da `016`
calcula `ocupadas = min(|faixa ∩ habilitadas|, efetivas)`, e o `min` **satura**: num recorte de 40
vagas com faixa de 70 e 67 habilitadas, excluir o desistente do conjunto não muda nada, porque
sobram 66 para saturar o mesmo 40. Chamando a função real:

```
40 vagas, faixa de 70, 67 habilitadas        ocupadas=40  faltando=0
uma titular desiste (excluída do conjunto)   ocupadas=40  faltando=0
cinco titulares desistem                     ocupadas=40  faltando=0
vinte e sete desistem                        ocupadas=40  faltando=0
vinte e oito desistem                        ocupadas=39  faltando=1
```

**São necessárias 28 desistências para o número se mover**, e cada uma das 27 primeiras é uma
suplente promovida em silêncio — contada como ocupante de vaga sem ter sido convocada. Isso tornava
inertes a `FR-275`, a `FR-279` e a `SC-085`: a vaga nunca se liberava, ninguém era chamado, e o
ciclo que a `SC-085` promete não fechava.

**A causa não é o `min`; é a definição.** `|faixa ∩ habilitadas|` conta *capacidade* — quantos
habilitados existem para preencher —, e o que a feature precisa contar é *ocupação por pessoa
identificada*. O comentário do próprio `apuracao.py` já dizia a intenção certa — *"o excedente **é**
o suplente: ele está na faixa, habilitou, e não ocupa vaga nenhuma até que uma vagueie"* — e a
cardinalidade saturada a contradizia. A `D-011` corrige isso.

### 1.1 As cláusulas reais, nas palavras dos Editais

Lidas em `~/Downloads` com `pdftotext -layout`. **Seis Editais, cinco mecanismos distintos** — e a
palavra "convocação" cobre todos eles sem distinguir nenhum:

| Edital | Cláusula | O que manda |
|---|---|---|
| **77/2026** | 6.9 | havendo desistentes *"antes ou após a publicação do Resultado Final"*, haverá chamada dos próximos habilitados *"conforme a ordem de classificação do sorteio"* |
| **77/2026** | 6.10 | análise documental de até **30 suplentes** *"para chamada imediata, em caso de desistência de alunos matriculados"*; suplente indeferido pode recorrer |
| **28/2026** | 8.12 | o mesmo, com **15 suplentes por código de vaga** |
| **28/2026** | 8.8 *in fine* | desistente em vaga reservada → a vaga é preenchida *"pelo candidato autodeclarado sorteado e classificado imediatamente após este"* |
| **77/2026** | 8.2 | *"No interesse da Administração"*, quando as matrículas deferidas forem menos que as vagas, convocar quem teve a matrícula **indeferida**, na ordem, *"para regularizar a sua situação de indeferimento"* |
| **77/2026** | 8.3 | o convocado *"receberá um e-mail"* e tem **2 dias úteis** *"contado a partir da data do recebimento do e-mail"*; não regularizou → *"o próximo suplente será convocado"* |
| **58/2026, 59/2026** | 8.2–8.3 | idênticas às duas acima, palavra por palavra |
| **69/2026** | 7.2 | vagas não ocupadas → suplentes convocados *"por meio de publicação no site do Cefor"* |
| **69/2026** | 7.3 | o contato individual é direito **reservado**, e o Cefor *"não se responsabilizará pelo não contato"* por falha de telefone, e-mail ou dado errado |
| **69/2026** | 6.3 | o classificado que não entrega documentos na data *"será RECLASSIFICADO e poderá ser convocado novamente após o esgotamento da lista de suplentes"* |
| **77/2026** | 9.2 | quem não acessa a sala virtual em **6 dias corridos** do início *"será considerado desistente"*, matrícula cancelada, próximo suplente convocado |
| **28/2026** | 11.3 | o mesmo com **5 dias** contados do início **da primeira disciplina** |
| **59/2026** | 8.4 | quem não comparece *"às aulas da primeira semana"* sem justificativa legal → desistente |
| **158/2024** | 8.1 | o mesmo com 6 dias, e o ambiente é de **outra instituição** (LAB-TIME/UFG) |

**As duas formas de comunicar são incompatíveis entre si, e as duas são normais.** No 77, no 58 e no
59 o prazo corre *do recebimento do e-mail* — o que faz do recebimento um fato juridicamente
relevante. No 69 a convocação **é** a publicação, e o contato individual é cortesia declarada sem
responsabilidade. Um sistema que só saiba uma das duas publica o que o Edital não disse.

### 1.2 São cinco mecanismos, e a palavra é a mesma

1. **Chamada de quem está na faixa** para a vaga que a `016` apurou como faltante.
2. **Chamada do suplente** quando uma vaga vaga — *dentro do mesmo recorte* (28, 8.8 *in fine*).
3. **Convocação para regularizar** o próprio indeferimento (77/58/59, 8.2) — a Administração
   desfazendo ato desfavorável **sem que ninguém tenha recorrido**.
4. **Reclassificação** (69, 6.3) — o ausente não é eliminado: vai para o fim da fila.
5. **Desistência por inércia** (77 9.2; 28 11.3; 59 8.4; 158 8.1) — o silêncio ou a ausência, num
   ambiente que **não é o deste sistema**, cancelam a matrícula.

O quinto é o que mais diverge do resto do produto: **o fato que o dispara não é observável aqui.**
Acesso a AVA, presença na primeira semana e entrega presencial acontecem fora, e a `P-12`
([achados](../../doc/achados-editais-externos.md)) já nomeou a classe. Ver `D-004`.

---

## 2. O que já existe, e que esta feature NÃO reconstrói

| Capacidade | Onde está | O que a `019` faz com ela |
|---|---|---|
| a ordem de cada lista | ato de ordenação da `015`, recorte Perfil + marco + `lista_id` | **lê**; não reordena nem desempata |
| quem progride, a faixa e o teto de suplentes | corte da `014` | **lê**; não seleciona e não emite faixa |
| quantas vagas faltam no recorte | apuração da `016`, quatro números | **lê**; não recalcula — e a definição de *ocupada* passa a ser a da `D-011` |
| a causa da faixa seguinte | `causar_faixa_seguinte` da `016` | **não usa** — pedir faixa continua sendo ato de quem conduz |
| quantas vagas cada lista tem | `vacancyTable`, degrau 12 (`025`) | **não lê direto** — chega pela apuração |
| o resultado da Etapa e sua vigência | `013` e `017` | **lê** o deferimento que fundamenta a convocação |
| o canal de e-mail e a área do candidato | `010` (`FR-080` a `FR-084`) | **exige revisão escrita da `FR-084`** antes de existir mensagem individual (`D-009`) |
| recurso e superação de resultado | `018` — progressão retroativa e superação append-only | **reusa** a superação para a regularização (`D-008`); não cria objeto recursal (`D-010`) |

---

## Clarifications

### Session 2026-09-12

- Q: Quando alguém desiste, tem a matrícula cancelada por inércia ou é reclassificado, quem passa a
  dizer que aquela vaga voltou a estar livre? → A: **opção A** — a `019` registra o desfecho de
  forma append-only, ele torna obsoleta a apuração vigente, e **na emissão seguinte** a `016`
  exclui essas inscrições e produz o número novo. Até essa emissão, nenhum número novo é afirmado.
- Q: Quando um recurso é deferido e a pessoa reaparece na ordem acima de alguém já convocado ou já
  matriculado, o que acontece com a vaga provida? → A: **opção B** — o deferimento preserva efeito
  pleno sobre resultados, progressão e ordem; antes da convocação a ordem corrigida governa o
  próximo ato; depois dela a convocação não é desfeita, a matrícula efetivada não é cancelada, e o
  beneficiado passa ao primeiro lugar da fila de suplência do seu recorte.
- Q: A regularização de um indeferimento deve produzir Resultado novo pela superação da `018`, ou
  ser ato próprio da `019`? → A: **opção B** — a regularização **sucede** o Resultado desfavorável,
  pelo mecanismo existente e com origem nova; reclassificação e desistência por inércia permanecem
  atos próprios da `019`.
- Q: O decurso do prazo produz o desfecho por si? → A: **não** — o decurso apenas indica vencimento;
  quem registra o não atendimento ou a inércia é pessoa autorizada. O sistema não emite o desfecho
  automaticamente.
- Q: Que fato o sistema trata como o recebimento que inicia o prazo? → A: **opção A** — o marco é o
  **envio individual registrado com sucesso**, e ele não é apresentado como prova de leitura ou de
  entrega: a interface diz *"enviado em"*, nunca *"recebido em"*. Falha no envio não inicia prazo, e
  o acesso autenticado do candidato fica apenas na auditoria.
- Q: Os atos desta feature se tornam objeto de recurso da `018`? → A: **opção A** — nesta entrega,
  convocação, reclassificação, desistência e cancelamento por inércia **não** são objetos de
  recurso; permanece recorrível o Resultado que fundamenta a posição ou o indeferimento. A hipótese
  futura fica registrada no *Out of Scope*.
- Q: a exclusão da `D-006` basta para liberar a vaga? → A: **não** (achado do `$speckit-plan`,
  §1.0). A `016` passa a contar **titulares iniciais habilitados**; o desfecho exclui uma ocupação
  e o aceite ou a regularização **inclui** a suplente convocada, pela mesma porta append-only. Vaga
  individual não é modelada, o vencimento em dias úteis é informado por quem convoca, e não
  atendimento à convocação e cancelamento por inércia são desfechos distintos (`D-011`).
---

## 3. Decisões

### 3.0 As cinco que precediam o planejamento, respondidas em 12/09/2026

Nenhuma era detalhe de implementação: as cinco mudavam requisito, fronteira ou norma, e três delas
alcançavam feature já entregue. As cinco foram apresentadas ao usuário com opções e custo, e as
cinco foram respondidas por ele — ficam registradas como `D-006` a `D-010`.

**E uma sexta decisão veio depois delas**, quando o `$speckit-plan` mostrou que a `D-006` não
bastava: é a `D-011`, e o defeito que a motivou está medido na §1.0.

#### `Q-1` — O que "ocupada" passa a significar depois da desistência · **respondida** (`D-006`)

**O que estava em jogo.** Hoje `ocupadas = |faixa ∩ habilitadas| − ocupantes da ampla`, limitado às
efetivas. Quem desistiu, teve matrícula cancelada por inércia ou foi reclassificado continuaria nos
dois conjuntos. **Escolhida a opção A**, com a disciplina de obsolescência da `016` preservada — ver
`D-006`.

#### `Q-2` — O efeito da progressão retroativa depois da convocação · **respondida** (`D-007`)

**O que estava em jogo.** A decisão de progressão retroativa da `018` fixou **efeito pleno** quando
nenhuma vaga estava ocupada, e o recurso deferido meses depois alcança um certame onde há gente
matriculada. **Escolhida a opção B**: o efeito pleno é preservado onde a `018` o produz —
resultados, progressão e ordem — e o que se limita é o alcance sobre **atos posteriores desta
feature**. Ver `D-007`.

#### `Q-3` — Os três desfechos da `P-11`: mecanismo próprio ou da `018`? · **respondida** (`D-008`)

**O que estava em jogo.** **Reclassificação**, **regularização** e **desistência por inércia** — e a
regularização é a mais pesada, porque é a Administração desfazendo ato desfavorável **sem recurso**,
sobre o elo que a
[decisão C da `018`](../../doc/descoberta-018-decisao-c-superacao-de-resultado.md) já resolveu por
superação append-only. **Escolhida a opção B**, e a sub-pergunta do decurso de prazo foi confirmada
no sentido da `D-003`. Ver `D-008`.

#### `Q-4` — O que conta como recebimento, e a `FR-084` da `010` · **respondida** (`D-009`)

**O que estava em jogo.** No 77/58/59 o prazo corre do *recebimento do e-mail*; no 69 a convocação
**é** a publicação, e o contato individual não gera responsabilidade. Duas normas incompatíveis, as
duas normais — e "recebimento" é fato que este sistema não observa. Sobre isso há um obstáculo
escrito: a **`FR-084` da `010`** diz que o sistema envia mensagem em *exatamente duas* situações, e
que *"acrescentar uma terceira situação exige revisar esta regra"*. A convocação é essa terceira.
**Escolhida a opção A**, com o marco no envio e a recusa explícita de apresentá-lo como prova de
entrega. Ver `D-009`.

#### `Q-5` — Recurso contra a convocação e contra o desfecho · **respondida** (`D-010`)

**O que estava em jogo.** A `018` excluiu recurso contra convocação com a razão explícita de ser
*"ato que ainda não existe no produto"*, e esta feature cria o ato. Mas a amostra pede o contrário
de um objeto novo: o 77 (7.1) diz *"Caberá recurso somente quanto ao resultado preliminar"*, e o
recurso que o 77 (6.10) e o 28 (8.12) garantem ao suplente é contra a **documentação indeferida**,
que é Resultado e já é atacável. **Escolhida a opção A**. Ver `D-010`.

### As decisões do usuário, de 12/09/2026

#### D-006 — Uma contagem só, e ela é a da `016`: o desfecho exclui na emissão seguinte

*Decisão do usuário, 12/09/2026 — opção (A) da `Q-1`.*

> A `019` registra, de forma append-only, o desfecho que encerra ou impede a ocupação e torna
> obsoleta a apuração vigente. Na emissão seguinte, a `016` exclui essas inscrições e produz o novo
> número. Até essa emissão, nenhum número novo é afirmado.

Quatro consequências que governam os requisitos:

1. **A pergunta *"quantas vagas estão ocupadas"* continua tendo uma resposta só.** A `019` não conta
   vaga; ela produz o fato que a contagem exclui — a mesma forma que a `FR-252` já deu à
   concorrência concomitante, que é exclusão e não transferência.
2. **Nenhuma apuração é reescrita.** O desfecho torna o recorte obsoleto, e obsolescência é
   calculada, não gravada — a apuração de ontem continua dizendo o que leu.
3. **Nada é recalculado sozinho.** Entre o desfecho e a emissão seguinte o sistema exibe o número
   apurado **marcado como obsoleto**, e não um número que ninguém emitiu.
4. **A seta de dependência não se inverte.** A `016` declarou que `ocupacao` importa
   `classificacao` e nunca o contrário, e a `019` já lê o déficit da `016`. A exclusão, portanto,
   chega por porta que a `016` define e a `019` preenche — a `016` não passa a importar a feature
   nova. É restrição de desenho que o plano tem de respeitar, e não uma quinta opção da pergunta.

> **Refinada pela `D-011`.** A exclusão desta decisão é necessária e **não é suficiente**: sobre a
> definição de ocupada que a `016` tinha, excluir o desistente não movia o número (§1.0). A `D-011`
> conserta a definição e acrescenta a inclusão; o que esta decisão fixou — uma contagem só, na
> emissão seguinte, por porta que a `016` define — continua valendo inteiro.

#### D-007 — O deferimento não desfaz ato praticado, e passa ao primeiro lugar da suplência

*Decisão do usuário, 12/09/2026 — opção (B) da `Q-2`, pelo texto dela.*

> O deferimento preserva efeito pleno sobre resultados, progressão e ordem. Se ainda não houve
> convocação, a ordem corrigida governa o próximo ato. Depois de praticada a convocação, ela não é
> desfeita: o candidato beneficiado passa ao primeiro lugar da fila de suplência do seu recorte e
> nenhuma pessoa abaixo dele pode ser convocada antes. Matrícula já efetivada também não é
> cancelada. A correção exige atos humanos autorizados; nada é emitido automaticamente.

Três consequências, e a terceira é de vocabulário:

1. **A decisão da `018` não é desfeita, e o que se limita é outra coisa.** O efeito pleno sobre
   resultado, progressão e ordem continua inteiro; esta decisão governa apenas o alcance dele sobre
   atos **posteriores** da `019`. Não é revisão do que aquela feature produz.
2. **Nenhuma vaga adicional é prometida.** O quadro publicado é intocável, e a saída não passa por
   criar vaga que o Edital não publicou.
3. **O recurso não julga direito a uma vaga.** Ele corrige Resultado, progressão e ordem — e é por
   isso que nenhuma superfície desta feature pode dizer que alguém teve *"direito à vaga
   reconhecido"*. O que o deferimento produz aqui é **posição na fila**, e a posição é a primeira.

#### D-008 — A regularização sucede o Resultado; reclassificação e inércia são atos desta feature

*Decisão do usuário, 12/09/2026 — opção (B) da `Q-3`, com a confirmação da sub-pergunta.*

> A regularização sucede o Resultado desfavorável, pelo mecanismo existente e com origem nova.
> Reclassificação e inércia permanecem atos próprios da `019`. O decurso do prazo apenas indica
> vencimento; quem registra o não atendimento ou a inércia é pessoa autorizada. O sistema não emite
> o desfecho automaticamente.

Quatro consequências:

1. **Há um caminho só para alguém passar a estar habilitado**, e ele é o Resultado. Um ato próprio
   da `019` criaria o segundo, fora de `resultados` — e é justamente a leitura que a apuração da
   `016` usa para contar ocupação. Sem isto, quem regularizasse ocuparia vaga que o sistema
   continuaria chamando de faltante.
2. **A `018` ganha origem que não é recurso.** O sucessor por recurso hoje exige decisão recursal
   como fonte jurídica, e a regularização terá fonte própria: é linha nova no conjunto de formas
   legítimas do Resultado, com migration de constraint e gatilho conferidos — não dado reescrito.
3. **Reclassificação e inércia não superam Resultado nenhum.** Uma muda posição na fila; a outra
   cancela matrícula. Nenhuma das duas afirma que a pessoa deixou de estar habilitada.
4. **Nenhum desfecho nasce do relógio**, e a `D-003` deixa de ser suposição desta spec para ser
   decisão confirmada.

#### D-009 — O marco é o envio registrado, e a tela diz "enviado em", não "recebido em"

*Decisão do usuário, 12/09/2026 — opção (A) da `Q-4`, pelo texto dela.*

> O marco é o envio individual registrado com sucesso. Não deve ser apresentado como prova técnica
> de leitura ou entrega: a interface diz "enviado em", não "recebido em". Falha no envio não inicia
> prazo. O acesso autenticado fica apenas na auditoria, e o vencimento continua dependendo do ato
> humano já decidido na `D-003`.

Quatro consequências, e a terceira é um estado que a tela precisa ter:

1. **A presunção é declarada, e não disfarçada.** Os Editais sustentam a atribuição de
   responsabilidade — o 77 (9.3) manda o candidato acompanhar o e-mail *"e verificar também sua
   caixa de Spam"*, e o 69 (7.3) declara que a instituição *"não se responsabilizará pelo não
   contato"*.
   Nada disso autoriza o sistema a afirmar que a mensagem chegou, e é por isso que a palavra na tela
   é **enviado**.
2. **Falha de envio não inicia prazo, e o ato praticado continua registrado.** São coisas separadas:
   a convocação existe desde que foi praticada; o relógio só começa quando houver envio com sucesso.
3. **Existe, portanto, o estado "convocado, prazo não iniciado"** — e ele tem de ser legível, sob
   pena de alguém tratar como silêncio o que é falha de infraestrutura.
4. **O acesso autenticado é fato de auditoria.** Ele entra na trilha, e não move o relógio nem vira
   prova de ciência.

#### D-010 — Nenhum ato desta feature é objeto de recurso; o recorrível é o Resultado

*Decisão do usuário, 12/09/2026 — opção (A) da `Q-5`, pelo texto dela.*

> Nesta entrega, convocação, reclassificação, desistência e cancelamento por inércia não são objetos
> de recurso da `018`; permanece recorrível o Resultado que fundamenta a posição ou o indeferimento.
> A possibilidade futura fica apenas no *Out of Scope*: um Edital que preveja expressamente recurso
> contra chamada exigirá incremento próprio.

Três consequências:

1. **A `018` não ganha objeto atacável nenhum**, e esta feature não nasce com janela recursal,
   publicação de julgamento nem cadeia de decisão própria.
2. **O suplente indeferido continua com a via que os Editais lhe dão.** O que o 77 (6.10) e o 28
   (8.12) garantem é recurso contra a documentação indeferida, que é Resultado — e a `D-008` lhe
   acrescenta a via administrativa da regularização, que não depende de recurso.
3. **A hipótese futura é limite registrado, não escopo.** Ela fica na §7, e a Constituição é
   explícita: limite registrado é insumo de priorização, nunca a priorização em si.

#### D-011 — A `016` conta titulares iniciais; o desfecho exclui e o aceite inclui

*Decisão do usuário, 12/09/2026, depois de o `$speckit-plan` achar a contradição da §1.0.*

> A `016` conta somente titulares iniciais habilitados. Um desfecho da `019` exclui uma ocupação.
> Aceite ou regularização inclui a suplente convocada. Esses efeitos entram por uma porta
> append-only definida pela `016`; não é necessário modelar vagas individualmente. Para dias úteis,
> a comissão informa o vencimento explícito — nada de criar calendário de feriados. "Não atendimento
> à convocação" e "cancelamento de matrícula por inércia" ficam como desfechos distintos.

Seis consequências, e a segunda é a que faltava:

1. **Ocupada passa a ser pessoa, não capacidade.** Titular inicial é a Inscrição que está entre as
   primeiras `efetivas` posições da ordem do recorte; suplente é o excedente, e ele **não ocupa
   nada** até ser convocado e aceitar. É o que o comentário do `apuracao.py` já afirmava.
2. **Sem a inclusão, o número nunca voltava a subir.** Exclusão sozinha faria a apuração cair a cada
   desistência e nunca recompor, ainda que o suplente aceitasse — a chamada não teria efeito
   observável. Medido com a regra proposta: titular desiste → 39; suplente convocada aceita → 40.
3. **Ninguém é promovido sem ato.** Nenhuma suplente entra na contagem por cardinalidade; entra por
   aceite ou regularização registrados, que são atos de pessoas autorizadas.
4. **Uma porta, append-only, e definida pela `016`.** Exclusões e inclusões chegam por ela, e a seta
   de dependência continua sendo a da `D-006`. **Vaga individual não é modelada** — não há entidade
   "vaga nº 7"; há quantidade e conjunto de pessoas.
5. **O sistema não conta dias úteis.** Quem convoca informa o vencimento explícito, e o sistema o
   registra, exibe e confere contra o envio. Calendário de feriados e contagem em dias úteis ficam
   fora, como a `018` já os deixou.
6. **Dois desfechos, e não um.** *Não atendimento à convocação* alcança quem foi chamado e não
   respondeu; *cancelamento de matrícula por inércia* alcança quem já ocupava e desapareceu. Os dois
   excluem ocupação, e os fundamentos, os atores e os prazos são diferentes.

### As decisões que esta spec toma sozinha

#### D-001 — A fronteira é a que a `014` fixou, e esta feature a herda

A decisão de fronteira da `014` governa esta feature inteira: a `019` **não** conta ocupação,
**não** ordena, **não** desempata e **não** emite faixa. O que ela
produz é o fato: chamado, respondido, liberado. A contagem continua sendo leitura da `016`, e a
seleção continua sendo ato da `014`.

#### D-002 — A suplência não atravessa recorte

A vaga liberada numa lista é chamada para o próximo **daquela** lista (28, 8.8 *in fine*: *"o
candidato autodeclarado sorteado e classificado imediatamente após este"*). É a mesma disciplina da
`SC-080` da `016` — nenhuma vaga atravessa Perfil — aplicada agora entre listas do mesmo Perfil.

#### D-003 — Nenhum desfecho desfavorável é automático

O decurso do prazo é **observável** pelo sistema, e o ato de dar a convocação por não atendida é de
quem conduz, com fundamento registrado. Cancelar matrícula por relógio é ato que alcança pessoa sem
ninguém o ter praticado, e a Constituição exige ato motivado e auditado. **Confirmada pelo usuário
em 12/09/2026** junto com a `Q-3` (`D-008`).

#### D-004 — Fato que acontece fora não é inferido: é atestado

Acesso a ambiente virtual de outra instituição, presença na primeira semana e entrega presencial de
documentos não são observáveis aqui. O sistema registra **quem atestou, o que concluiu e quando** —
nunca deduz o fato. É a `P-12` aplicada, e não sua solução: esta feature não passa a deter o
artefato.

#### D-005 — O recorte é o do ato de ordenação

Perfil, marco e lista — o mesmo que a `015` emite, a `014` corta e a `016` apura. Nenhuma dimensão
nova. A turma da `P-10` fica de fora (§7).

---

## 4. Problema

Um Edital de sorteio publica 40 vagas. A ordem sai, a faixa progride, 40 documentações são
analisadas, 37 são deferidas e a apuração da `016` diz `40 / 40 / 37 / 3`. **Daqui em diante o
sistema não tem mais nada a oferecer.** Quem conduz precisa: chamar os três próximos habilitados da
ordem, esperar dois dias úteis contados do recebimento do e-mail de cada um, registrar que o
primeiro aceitou, o segundo não respondeu e o terceiro pediu para regularizar o indeferimento
anterior, chamar o suplente do segundo, e — três semanas depois — cancelar a matrícula de quem nunca
acessou a sala virtual e chamar mais um. Hoje isso acontece em planilha e caixa de e-mail, e o único
registro do que foi prometido a quem é a memória de quem prometeu.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Chamar para a vaga que falta, e registrar o que a pessoa respondeu (Priority: P1)

Quem conduz abre o recorte, vê o déficit apurado pela `016` e convoca, na ordem, tantos habilitados
quantos couberem nele. Cada convocação nasce com prazo. Quando a pessoa responde — aceite,
indeferimento, desistência expressa — o desfecho é registrado como ato, e a vaga fica ocupada ou
volta a faltar.

**Why this priority**: é o mínimo que fecha a lacuna comum aos onze Editais, e é o que hoje mora em
planilha. Sem ela nenhuma das outras histórias tem objeto.

**Independent Test**: com um certame até a apuração, convocar três candidatos, registrar três
desfechos diferentes e ler o recorte — tudo pela interface administrativa, sem shell.

**Acceptance Scenarios**:

1. **Given** apuração vigente dizendo `40 / 40 / 37 / 3`, **When** quem conduz convoca os três
   próximos da ordem, **Then** as três convocações ficam registradas com prazo, e a tela diz quantas
   vagas continuam sem resposta.
2. **Given** uma convocação vigente, **When** o desfecho é aceite, **Then** a vaga é ocupada e a
   convocação não admite segundo desfecho.
3. **Given** uma convocação vigente, **When** o prazo decorre sem resposta, **Then** o sistema
   **mostra** o decurso e recusa tratá-lo como desfecho até que alguém o pratique com fundamento.
4. **Given** apuração obsoleta no recorte, **When** alguém tenta convocar, **Then** o sistema recusa
   e nomeia a causa da obsolescência.
5. **Given** um habilitado fora da faixa vigente, **When** alguém tenta convocá-lo, **Then** o
   sistema recusa — convocar fora da faixa é selecionar, e seleção é da `014`.

---

### User Story 2 - Chamar o suplente quando a vaga vaga (Priority: P1)

Registrado um desfecho que não ocupa, a vaga volta a faltar e quem conduz chama o próximo da ordem
**do mesmo recorte**. Esgotada a lista alcançada pelo teto publicado, o sistema diz que se esgotou —
e pedir mais faixa continua sendo ato da `014`.

**Why this priority**: é a metade do 77 e do 28 que a `016` explicitamente deixou para cá — *"quem
chama para a vaga vaga é a `019`"*. Sem ela, a primeira desistência para o certame.

**Independent Test**: liberar uma vaga reservada e verificar que o chamado é o próximo daquela
lista, nunca o da ampla; esgotar o teto e ler a recusa.

**Acceptance Scenarios**:

1. **Given** desistência em vaga reservada, **When** a vaga é chamada, **Then** o convocado é o
   próximo da **mesma** lista, e nenhuma quantidade muda de recorte.
2. **Given** o teto de 30 suplentes alcançados pela faixa, **When** o trigésimo primeiro seria
   necessário, **Then** o sistema recusa dizendo que a lista alcançada se esgotou e que a faixa
   seguinte é ato da `014`.
3. **Given** uma vaga liberada, **When** a apuração vigente é lida, **Then** ela se declara
   **obsoleta** — o número de antes não vale mais.

---

### User Story 3 - Convocar para regularizar o indeferimento (Priority: P2)

Quando as matrículas deferidas são menos que as vagas, quem conduz convoca, na ordem, quem teve a
própria matrícula indeferida, para corrigir o que faltava. Regularizada, a matrícula se efetiva; não
regularizada no prazo, o próximo suplente é chamado.

**Why this priority**: está em quatro Editais da amostra com redação idêntica, e é o único caso em
que a Administração desfaz ato desfavorável sem que ninguém tenha recorrido — e por isso ela sucede
o Resultado, em vez de criar caminho próprio para habilitar alguém (`D-008`).

**Independent Test**: com três indeferidos e vagas sobrando, convocar o primeiro da ordem para
regularizar, registrar a regularização e ver a vaga ocupada sem reabrir a ordem.

**Acceptance Scenarios**:

1. **Given** deferidas 37 de 40 vagas e três indeferidos, **When** quem conduz convoca para
   regularizar, **Then** a convocação respeita a ordem de classificação e registra o fundamento
   *"no interesse da Administração"*.
2. **Given** uma convocação para regularizar, **When** a situação é regularizada no prazo, **Then**
   a matrícula se efetiva e a ordem não é reaberta.
3. **Given** o mesmo caso, **When** o prazo decorre sem regularização, **Then** o próximo suplente
   fica chamável.

---

### User Story 4 - Reclassificar quem não compareceu (Priority: P3)

O classificado que não entrega documentos na data não é eliminado: vai para o fim da fila do recorte
e volta a ser chamável depois que os suplentes se esgotarem.

**Why this priority**: um Edital da amostra (69, 6.3). É ato próprio desta feature, e não superação
de Resultado: quem é reclassificado continua habilitado (`D-008`).

**Independent Test**: reclassificar um convocado, esgotar a fila e verificar que ele volta a ser
chamável — nessa ordem, e não antes.

**Acceptance Scenarios**:

1. **Given** um convocado que não entregou documentos, **When** o desfecho é reclassificação,
   **Then** ele deixa a posição atual e passa a constar depois do último suplente do recorte.
2. **Given** a fila de suplentes não esgotada, **When** alguém tenta chamar o reclassificado,
   **Then** o sistema recusa e diz o que falta esgotar.

---

### User Story 5 - Registrar a desistência que aconteceu fora daqui (Priority: P3)

Quem tem competência atesta que a pessoa não acessou o ambiente virtual no prazo declarado, ou não
compareceu à primeira semana. O ato registra quem atestou e o que concluiu; a matrícula é cancelada
e o próximo suplente fica chamável.

**Why this priority**: está em quatro Editais, e é o único mecanismo cujo fato o sistema não
observa. Entregar sem ele deixa o certame parado no primeiro aluno que desaparece.

**Independent Test**: atestar a inércia de um matriculado e verificar que o cancelamento registra o
atestante, não o relógio.

**Acceptance Scenarios**:

1. **Given** um matriculado e o prazo de acesso declarado no Edital, **When** quem tem competência
   atesta a inércia, **Then** o cancelamento fica registrado com atestante, instante e fundamento.
2. **Given** nenhum atestado, **When** o prazo decorre, **Then** o sistema **não** cancela nada.

---

### User Story 6 - O candidato vê que foi convocado, e até quando (Priority: P2)

Quem foi convocado abre a própria área e lê que foi chamado, para qual vaga, o que precisa fazer e
até quando.

**Why this priority**: a Constituição exige jornada alcançável pelo canal do ator, e o ator desta
comunicação é o candidato. A forma é a que o Edital declarar, e o prazo corre do envio (`D-009`).

**Independent Test**: convocar e ler a convocação na área do candidato, com prazo visível.

**Acceptance Scenarios**:

1. **Given** uma convocação vigente, **When** o candidato abre sua área, **Then** vê a chamada, o
   que fazer e o prazo, sem depender de e-mail.
2. **Given** nenhuma convocação, **When** ele abre a área, **Then** a tela distingue *"não há
   convocação"* de *"você não foi chamado"*.

### Edge Cases

- **Duas convocações para a mesma pessoa no mesmo recorte** — recusadas: uma vaga, uma convocação
  vigente.
- **Convocação e Retificação do quadro no mesmo dia** — a apuração fica obsoleta; a convocação já
  praticada **não** se desfaz, porque ato praticado não se apaga (`FR-282`).
- **Desfecho registrado sobre convocação já desfechada** — recusado.
- **Recurso deferido depois da matrícula de terceiro** — a convocação não se desfaz e a matrícula
  não se cancela; o deferido vai ao primeiro lugar da fila do recorte (`D-007`).
- **Reclassificado que também desiste** — o desfecho posterior prevalece, e o histórico guarda os
  dois.
- **Edital sem prazo de resposta declarado** — não há prazo a contar, e a tela não pode inventar um:
  o recorte fica sem vencimento, e o desfecho continua dependendo de ato humano (`D-003`, `D-009`).
- **Convocação praticada e envio com falha** — estado *"convocado, prazo não iniciado"*: o ato vale,
  o relógio não começou, e tratá-lo como silêncio é o defeito que a `FR-269a` impede.
- **Vencimento informado antes do envio** — recusado (`FR-269b`).
- **Todos os titulares iniciais desistem** — a apuração seguinte diz zero ocupadas e o déficit é o
  total; nenhuma suplente entra sem convocação, e a faixa seguinte continua sendo ato da `014`.
- **A suplente convocada também desiste** — a exclusão dela não desconta nada, porque ela nunca
  entrou na contagem: só entra quem aceitou ou regularizou (`FR-278d`).
- **Certame sem apuração emitida** — convocar é recusado: chamar para vaga que ninguém apurou é
  prometer o que não se sabe existir.
- **Vaga liberada no último dia da validade do Edital** — a `P-3` (validade e prorrogação) não
  existe no produto, e o 77 (6.11) a pratica. Fora de escopo (§7).

## Requirements *(mandatory)*

### Functional Requirements

**O ato de convocação**

- **FR-264**: O sistema MUST registrar a convocação de uma Inscrição para um recorte — Perfil, marco
  e lista —, fundada na ordem vigente daquele recorte e na faixa vigente da `014`.
- **FR-265**: A convocação MUST ser recusada quando a Inscrição está fora da faixa vigente do
  recorte. Convocar fora da faixa é selecionar, e seleção é ato da `014`.
- **FR-266**: A convocação MUST ser recusada quando o recorte não tem apuração vigente da `016`, e
  quando a apuração vigente está obsoleta — nomeando a causa, como a `FR-263` já as nomeia.
- **FR-267**: A convocação MUST respeitar a ordem: MUST NOT convocar quem é precedido, no mesmo
  recorte, por habilitado ainda sem convocação e sem desfecho, salvo fundamento registrado no ato.
- **FR-268**: Uma Inscrição MUST NOT ter duas convocações vigentes no mesmo recorte.
- **FR-269**: A convocação MUST registrar o **vencimento explícito** informado por quem convoca, e o
  sistema MUST NOT calculá-lo em dias úteis nem manter calendário de feriados (`D-011`).
- **FR-269b**: O vencimento informado MUST ser posterior ao envio, e o sistema MUST recusar
  vencimento anterior a ele — prazo que vence antes de a pessoa poder saber não é prazo.
- **FR-269a**: Falha no envio MUST NOT iniciar o prazo, e MUST NOT desfazer a convocação praticada:
  o recorte MUST exibir o estado *"convocado, prazo não iniciado"* enquanto não houver envio com
  sucesso.
- **FR-270**: Cada convocação MUST alcançar exatamente uma vaga, e MUST NOT mover quantidade entre
  recortes — mover quantidade é a reversão da `016`.
- **FR-271**: Toda convocação MUST exigir permissão explícita e verificação de escopo, e MUST
  registrar ator, instante, fundamento e correlação.

**O desfecho**

- **FR-272**: Convocação e desfecho MUST ser append-only: nenhum é alterado ou excluído depois de
  gravado, e correção é sucessão com motivo.
- **FR-273**: Cada convocação MUST admitir no máximo um desfecho, entre os nomeados: aceite,
  indeferimento, desistência expressa, **não atendimento à convocação**, reclassificação,
  regularização e **cancelamento de matrícula por inércia**. Os dois últimos da lista de exclusão
  são distintos entre si, e MUST NOT ser colapsados num só (`D-011`).
- **FR-274**: O decurso do prazo MUST ser observável na leitura do recorte, e MUST NOT produzir
  desfecho por si — dar a convocação por não atendida é ato de quem conduz (`D-003`).
- **FR-275**: Desfecho que não ocupa vaga MUST liberá-la para chamada no mesmo recorte.
- **FR-276**: A liberação MUST tornar obsoleta a apuração vigente do recorte, acrescentando causa à
  lista da `FR-263`. É o efeito sobre a **vigência**; o da **contagem** está na `FR-278`, e os dois
  não se substituem.
- **FR-277**: Fato que ocorre fora deste sistema — acesso a ambiente virtual, presença em aula,
  entrega presencial — MUST ser registrado como atestado, com quem atestou e o que concluiu, e MUST
  NOT ser inferido (`D-004`).
- **FR-278**: O desfecho que encerra ou impede a ocupação MUST excluir a Inscrição da contagem de
  ocupadas **na emissão seguinte** da apuração, e MUST NOT alterar apuração já emitida (`D-006`).
- **FR-278a**: Enquanto não houver emissão nova, o sistema MUST NOT afirmar número de ocupação
  diferente do apurado — MUST exibir o apurado com a obsolescência declarada.
- **FR-278b**: O aceite e a regularização de quem foi convocado MUST **incluir** a Inscrição na
  contagem, pela mesma porta e na mesma emissão seguinte (`D-011`). Sem a inclusão, a chamada do
  suplente não tem efeito observável.
- **FR-278c**: Exclusões e inclusões MUST chegar à apuração por porta append-only definida pela
  `016`, e MUST NOT exigir entidade de vaga individual.
- **FR-278d**: Nenhuma Inscrição MUST passar a ser contada como ocupante por cardinalidade: fora dos
  titulares iniciais, só entra quem foi convocado e teve aceite ou regularização registrados.

**A chamada do suplente**

- **FR-279**: Liberada a vaga, o sistema MUST indicar o próximo da ordem do mesmo recorte, ainda sem
  convocação e sem desfecho que o exclua.
- **FR-280**: A chamada MUST NOT atravessar recorte: vaga reservada liberada é do próximo daquela
  lista (`D-002`).
- **FR-281**: A chamada MUST respeitar o teto de suplentes publicado que a faixa da `014` alcançou;
  esgotado, o sistema MUST dizer que a lista alcançada terminou, e MUST NOT emitir faixa por conta
  própria.
- **FR-282**: Retificação, nova apuração ou nova faixa MUST NOT desfazer convocação já praticada.
- **FR-283**: O reclassificado MUST passar a constar depois do último suplente do recorte, e MUST
  NOT ser chamável antes do esgotamento. A reclassificação é ato próprio desta feature, e MUST NOT
  afirmar que a pessoa deixou de estar habilitada (`D-008`).

**A regularização**

- **FR-284**: O sistema MUST permitir convocar para regularização, na ordem de classificação, quem
  teve a matrícula indeferida, quando as matrículas deferidas do recorte são menos que as vagas — e
  MUST registrar esse fundamento.
- **FR-285**: A regularização deferida MUST ocupar a vaga sem reabrir a ordem nem produzir nova
  faixa.
- **FR-286**: A regularização MUST produzir Resultado sucessor do indeferido, pelo mecanismo de
  superação append-only da `018`, com origem própria e fonte jurídica própria — e MUST NOT ser um
  segundo caminho para habilitar alguém fora de `resultados` (`D-008`).
- **FR-286a**: A desistência por inércia MUST ser ato próprio desta feature, e MUST NOT superar
  Resultado: ela cancela matrícula, não desfaz habilitação (`D-008`).

**A comunicação**

- **FR-287**: A forma de comunicar a convocação MUST ser a que o Edital declarar, entre publicação e
  mensagem individual (`D-009`).
- **FR-288**: A emissão MUST ser registrada com instante, destinatário e resultado do envio, e MUST
  NOT apagar o ato praticado quando o envio falha.
- **FR-288a**: Nenhuma superfície MUST afirmar que a comunicação foi recebida, lida ou entregue: o
  que o sistema sabe é que **enviou** (`D-009`).
- **FR-288b**: O acesso autenticado do convocado à própria convocação MUST ser registrado na trilha,
  e MUST NOT alterar o início nem o fim do prazo.
- **FR-289**: Mensagem individual de convocação MUST NOT existir antes da revisão escrita da
  `FR-084` da `010`, que limita o canal a duas situações nominais e manda revisar-se para admitir
  uma terceira.
- **FR-290**: A mensagem MUST conter o que fazer, o prazo e o canal de atendimento, e MUST NOT
  conter dado da inscrição além do necessário para identificar a chamada.

**O recurso**

- **FR-291**: Convocação, reclassificação, desistência e cancelamento por inércia MUST NOT ser
  objeto de recurso nesta entrega; o recorrível MUST continuar sendo o Resultado que fundamenta a
  posição ou o indeferimento (`D-010`). O recurso do suplente com documentação indeferida, que o 77
  (6.10) e o 28 (8.12) preveem, é contra o **Resultado**, e não contra a chamada.

- **FR-292**: Deferimento que reabilita uma Inscrição MUST governar o próximo ato enquanto não
  houver convocação praticada no recorte (`D-007`).
- **FR-292a**: Praticada a convocação, o deferimento MUST NOT desfazê-la, e matrícula efetivada MUST
  NOT ser cancelada por ele.
- **FR-292b**: A Inscrição reabilitada MUST passar ao primeiro lugar da fila de suplência do seu
  recorte, e o sistema MUST recusar convocar quem esteja abaixo dela antes disso.
- **FR-292c**: Nenhuma superfície desta feature MUST afirmar que o deferimento reconheceu direito a
  uma vaga: o que ele corrige é Resultado, progressão e ordem, e o que ele produz aqui é posição na
  fila.

**A leitura e a auditoria**

- **FR-293**: A leitura do recorte MUST mostrar, ao lado dos quatro números da `016`: quantos foram
  convocados, quantos responderam, quantas vagas voltaram a faltar e se a lista alcançada se
  esgotou.
- **FR-294**: A leitura MUST distinguir *"nenhuma convocação emitida"* de *"zero convocados"*, pela
  mesma razão que a `UX-032` distingue apuração ausente de zero vaga.
- **FR-295**: O histórico MUST reconstruir cada convocação com a proveniência que a fundamentou —
  ato de ordenação, corte e apuração vigentes no instante do ato.
- **FR-296**: Cada ato desta feature MUST constar da trilha de auditoria do Edital, em linguagem
  humana.

### Key Entities

- **Convocação** — ato que chama uma Inscrição para uma vaga de um recorte. Guarda o recorte, a
  proveniência (ordem, corte e apuração lidos), o prazo e o fundamento. Append-only.
- **Desfecho da convocação** — ato que registra o que a pessoa respondeu, ou o que a Administração
  concluiu. Um por convocação, com ator, instante e fundamento. Append-only.
- **Atestado de fato externo** — registro de que alguém com competência concluiu que um fato
  ocorrido fora deste sistema aconteceu. Não detém o artefato (`D-004`).
- **Comunicação emitida** — registro de que a convocação foi comunicada, na forma que o Edital
  declarou, com instante e destinatário.

## 5. Invariantes observáveis

1. Uma vaga, uma convocação vigente.
2. Nenhuma convocação fora da faixa vigente do recorte.
3. Nenhuma vaga atravessa recorte na suplência.
4. Nenhum registro de convocação ou desfecho é alterado; o histórico reconstrói o estado de hoje.
5. Nenhuma contagem de ocupação é produzida aqui — a conta é da `016`.
6. Nenhum fato externo é inferido; todo fato externo tem atestante.
7. Nenhum desfecho desfavorável nasce do relógio.
8. **Nenhuma suplente é promovida sem ato**: fora dos titulares iniciais, ocupa quem foi convocado e
   aceitou ou regularizou.
9. A desistência de um titular **move o número** na emissão seguinte, e move exatamente um.

## 6. Success Criteria *(mandatory)*

- **SC-085**: O ciclo do 77/2026 fecha pela interface, sem shell e sem banco: apuração com déficit →
  convocação dos que faltam → um indeferimento → vaga liberada → suplente convocado → apuração nova.
- **SC-086**: Em 100% dos casos de vaga reservada liberada, o convocado é do mesmo recorte.
- **SC-087**: O esgotamento da lista alcançada é dito na tela, e nunca silencioso.
- **SC-088**: Para qualquer convocação, o histórico responde *quem chamou, com base em qual ordem,
  qual corte e qual apuração* — sem consulta ao banco.
- **SC-089**: Nenhum desfecho registrado deixa a apuração do recorte parecendo vigente.
- **SC-090**: A tela do recorte abre em menos de 3 s com 1.000 participantes, e o custo de abri-la é
  do conjunto — não uma consulta por convocação.
- **SC-091**: Quem foi convocado lê, na própria área, a chamada e o prazo.
- **SC-092**: Nenhuma tela, ato ou mensagem desta feature afirma quantidade de vagas ocupadas por
  conta própria — verificado por varredura, como a `UX-034` verifica o simétrico na `016`.
- **SC-093**: Num recorte de 40 vagas com faixa de 70 e 67 habilitadas, **uma** desistência faz a
  emissão seguinte dizer 39 ocupadas e 1 faltando; o aceite da suplente convocada devolve 40. É o
  teste que prende o defeito da §1.0, e ele reprova qualquer contagem que sature.
- **SC-094**: Nenhuma Inscrição fora dos titulares iniciais aparece como ocupante sem convocação com
  aceite ou regularização registrados.

### Requisitos de interface

- **UX-035**: O vocabulário desta feature MUST ser verificável por varredura: ela **pode** dizer
  convocado, aceite e matrícula — são fatos dela — e **não pode** afirmar ocupação apurada.
- **UX-036**: Toda ação irreversível MUST confirmar antes de praticar, e a mensagem de sucesso MUST
  nomear o ato praticado — o defeito `E2E16-004` da `016` era exatamente isto.
- **UX-037**: A tela MUST distinguir os estados do recorte sem colapsar nenhum em zero.
- **UX-038**: O prazo MUST aparecer como data e hora locais, e MUST dizer de que referência corre.
- **UX-039**: A tela MUST escrever *"enviado em"*, e MUST NOT escrever *"recebido em"*, *"lido em"*
  nem *"entregue em"* — verificável por varredura, como a `UX-035` verifica o vocabulário da
  fronteira.

## Assumptions

- O recorte é o do ato de ordenação (`D-005`); nenhuma dimensão nova, e a turma da `P-10` fica fora.
- A autoridade para convocar é a mesma cadeia que autoriza emitir ordem, corte e apuração, até que
  as capacidades constituídas digam outra coisa.
- O volume de referência é o da ordem, do corte e da apuração: até 1.000 participantes por recorte.
- Nenhum Edital hoje publicado tem convocação registrada: a feature nasce sem migração de dado
  normativo. O campo normativo da forma de comunicar (`D-009`) entra com degrau canônico próprio e
  caminho de leitura das versões anteriores, como a `025` e a `014` fizeram.
- A ordem por lista só existe em certame de sorteio (`emitir_ordem` fixa `lista_id` nulo por decisão
  declarada), e portanto a suplência **por lista** só é demonstrável em sorteio — a mesma suposição
  que a `016` registrou para a reversão.
- **Não há calendário de dias úteis, feriados ou expediente neste sistema**, e a `018` já o deixou
  fora. Quem convoca informa o vencimento, e a conferência possível é contra o envio (`D-011`).
- **Vaga individual não é entidade.** O que existe é quantidade por recorte e conjunto de pessoas; a
  ocupação é contada, não alocada a um número de vaga.
- Matrícula, neste sistema, é o desfecho registrado da convocação — não integração com sistema
  acadêmico. O 77 (8.1a) diz que a matrícula é efetivada no Sistema Acadêmico do Cefor, e essa
  integração não é desta feature.

## 7. Out of Scope

- **Contar vagas ocupadas, reverter cota, ordenar, desempatar e emitir faixa** — são da `016`, da
  `015` e da `014`.
- **Integração com sistema acadêmico** para efetivar matrícula — o desfecho é registrado aqui; o
  lançamento acadêmico é de outro sistema, e a `P-8` já nomeia a classe do problema.
- **Calendário de feriados e contagem em dias úteis** — o vencimento é informado por quem convoca
  (`D-011`), e criar o calendário é incremento próprio, como a `018` registrou.
- **Vaga como entidade individual** — a `D-011` a recusa por escrito: não há "vaga nº 7" a alocar.
- **Turma como recorte** (`P-10`) — a repartição por turma só tem consequência quando alguém for
  alocado a uma delas, e nenhum Edital lido diz como.
- **Validade do Edital e prorrogação** (`P-3`) — o 77 (6.11) convoca suplente para nova turma dentro
  de seis meses; o `Edital` não tem prazo de validade, e criá-lo é incremento próprio.
- **Heteroidentificação** (28, 8.10) — spec própria, dependente da `L-2`.
- **Elegibilidade alternativa** (`P-13`) e **entrega presencial como acervo** (`P-12`) — esta
  feature registra atestado de fato externo (`D-004`), e não passa a deter documento.
- **Recurso contra a chamada** — nenhum ato desta feature é atacável (`D-010`). Edital que preveja
  expressamente recurso contra a convocação ou contra o desfecho exigirá **incremento próprio**;
  fica registrado como limite, e não como escopo diferido desta spec.
- **Segunda instância recursal** — recusada por decisão vigente da `018`, e esta spec não a reabre.
- **Cascata entre recortes por contagem de classificados** — é alvo derivado da `014` pela decisão
  de 12/09/2026 registrada na `016`, e continua não construída.

## 8. Ordem de implementação sugerida

*Esta ordem é a leitura da spec. A sequência executável é a do [tasks.md](tasks.md), que põe a
correção da contagem e o degrau canônico numa fase bloqueante; onde as duas divergirem, vale o
`tasks.md`.*

*A §3.0 está fechada, e três decisões alcançam feature entregue — a quarta exclusão na `016`
(`D-006`), a origem nova de sucessor na `018` (`D-008`) e a revisão da `FR-084` da `010` (`D-009`).
O plano precisa orçá-las explicitamente, e nenhuma é efeito colateral de um passo desta lista.*

1. **A convocação como ato** — entidade append-only, privilégio sobre a tabela nova, emissão,
   autorização, auditoria e as recusas da faixa e da apuração obsoleta.
2. **O desfecho** — um por convocação, com os nomeados, e a liberação da vaga.
3. **A tela do recorte** — os quatro números da `016` com o que esta feature acrescenta; é a US1 e a
   US2, e é o que substitui a planilha.
4. **A conciliação com a `016`** — a definição de titular inicial, mais a porta append-only de
   exclusão **e inclusão** (`D-006`, `D-011`), com o teste da `SC-093` prendendo a contagem. É o
   passo que mexe em feature entregue, e o que o `$speckit-plan` mostrou não ser opcional.
5. **A comunicação** — a forma declarada pelo Edital, o marco no envio e a recusa de afirmar
   entrega (`D-009`), precedida da revisão escrita da `FR-084` da `010`.
6. **A área do candidato** — a US6, pelo canal do ator.
7. **A regularização e a reclassificação** — a primeira sucedendo o Resultado com origem nova, a
   segunda como ato próprio (`D-008`).
8. **O atestado de fato externo** — a US5.

Os passos 1 a 3 fecham o essencial do 77 e do 28. O 69 depende do 7.

## 9. Gate de conclusão

- As três consequências em feature entregue implementadas e testadas onde estão: a contagem de
  titulares com exclusão e inclusão na `016`, a origem de sucessor na `018` e a `FR-084` da `010`
  revisada por escrito.
- A `SC-093` medida contra o cenário da §1.0 — uma desistência movendo o número em exatamente um.
- Percurso conduzido pela interface, com o ciclo da `SC-085` inteiro, e relatório em `doc/e2e/`.
- `make lint check test-pg` verde, com as tabelas novas contadas no provisionamento (`N de M`).
- Varredura de vocabulário nos dois sentidos: esta feature não afirma contagem de ocupação, e a
  `016` continua não afirmando convocação.
- Varredura provando que nenhuma superfície afirma recebimento, leitura ou entrega (`UX-039`).
