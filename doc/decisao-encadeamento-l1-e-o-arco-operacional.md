# Decisão de encadeamento — a L-1, o arco operacional e a fronteira `016`/`019`

**Sessão conduzida em 10/09/2026**, sobre `fe9d633` — a `main` com a `021`, a `022` e a `023`
integradas, e com os PRs #87 e #88 mesclados. Nenhuma linha de código foi escrita, nenhuma spec foi
aberta e nenhuma das três features reservadas foi iniciada.

O documento registra **uma tese de encadeamento aprovada** e **duas questões que continuam
abertas**. A tese da §4 foi formulada pelo usuário nesta sessão, depois de uma revisão que corrigiu
quatro pontos de uma formulação anterior minha — os quatro estão na §6, escritos de propósito,
porque é por eles que uma releitura futura saberá o que foi pesado.

> **A tese diz em que ordem as capacidades podem existir. Ela não diz qual construir agora.**
> Prioridade é do usuário e não se deriva de *Out of Scope*: *"limites registrados são insumo de
> priorização, nunca a priorização em si"* (Constituição). Aprovar este encadeamento não autoriza
> abrir spec nenhuma.

---

## 0. O que já está fechado, e não volta a esta mesa

- **O arco existe e está declarado** desde o briefing da `013`: *012 conclui avaliações; 013
  oficializa resultados de Etapa; **014** determina progressão; 015 ordena; **016** ocupa vagas* — e
  a **019** convoca, pela `018`. As três estão reservadas e nenhuma tem pasta em `specs/`.
- **A `015` está construída**, e deixou a ordem, o universo declarado e a modalidade prontos para a
  `014`.
- **A L-1 está diagnosticada**: `ModalidadeConcorrencia` não tem quantidade de vagas, e
  `RegraNormativa.percentage` é um decimal só. É o único bloqueio de autoria de 57, 28 e 173
  ([avaliação de 09/09](avaliacao-de-capacidade-editais-2026-09-09.md)).
- **A numeração não é fila.** Toda vez que um número reservado chegou à vez, ele foi pulado —
  `013 → 015`, `015 → 017`, `018 → 020` —, e as features construídas no lugar vieram da leitura dos
  Editais. Isso é a Constituição funcionando, não desvio.

## 1. O problema desta sessão

Ao olhar a `016` — *ocupação de vagas, cotas, remanejamento, concorrência entre modalidades* — a
pergunta que apareceu foi se ela concorre com a L-1 ou se depende dela. A formulação inicial tratou
as duas como alternativas: **largura** (a L-1 destrava três Editais na autoria) contra
**profundidade** (o par `014`+`016` fecha o 77/2026 de ponta a ponta).

**Esse enquadramento estava errado**, e a §4 diz por quê.

## 2. Quem precisa da L-1, e quem não precisa

A L-1 é uma coisa só: **quantidade de vagas por modalidade de concorrência**. Não é "ter
modalidade", não é "ter grupo", não é "ter cadastro de reserva". A distinção decide a conta, e
confundi-la foi um dos erros corrigidos.

| Edital | Precisa da L-1? | Por quê |
|---|:--:|---|
| **57/2026** | **sim** | quadro absoluto por curso — AC 56 · PcD 4 · PPI 20 |
| **28/2026** | **sim** | quadro absoluto por polo — AC 28 · PcD 2 · PPI 10 |
| **173/2025** | **sim** | quadro por modalidade, hoje impublicável |
| **77/2026** | não | perfil único, **sem cotas** (`specs/021-…/spec.md:127-128`) |
| **76/2026** | não | polos com cadastro de reserva, **sem cotas** (idem) |
| **14/2026** | não | tem três grupos, mas eles são **cascata de chamada**, não vaga reservada; o quadro dele já é publicável hoje |

**Três dos seis Editais no alvo do produto**, e são exatamente os três que a avaliação de 09/09 já
listava como bloqueados por ela. O 14/2026 é o caso que se classifica mal por descuido: o que ele
precisa é de regra de ordem de chamada — `callRules` —, e não de quantidade reservada.

## 3. Quem precisa da L-1 do outro lado: a própria `016`

Uma `016` que trate cotas precisa saber quantas vagas cada lista tem. Sem a L-1 ela atenderia o 77 e
o 76 — os dois sem cotas — e teria de ser refeita quando os outros três chegassem. **A L-1 não é um
desvio no caminho da `016`; é uma entrada dela.**

E é uma entrada que **rende sozinha**: no dia em que fechar, três Editais passam a ser publicáveis,
antes de qualquer discussão sobre ocupar vaga.

## 4. A tese aprovada

> **A L-1 não é concorrente do arco operacional.** É uma capacidade de autoria independente, de
> maior retorno imediato, e uma entrada normativa necessária para que a `016` trate corretamente os
> certames com cotas — que são três dos seis no alvo. Por isso **deve preceder a `016`**, embora
> **não precise bloquear a especificação da `014`**.

O encadeamento, como encadeamento de **produto** e não como cadeia técnica estrita:

```
L-1 ───────────────┐
                   ├── 016 ── 019
015 ── 014 ────────┘
```

**Duas arestas são firmes e uma é frouxa**, e vale registrar qual é qual:

- `L-1 → 016` é **firme** para os certames com cota, pela §3. Para 77 e 76, não existe.
- `016 → 019` é **firme**: não se convoca sem saber quantos cabem.
- `014 → 016` é **frouxa**. Um certame sem Etapa intermediária — o 28 sorteia, publica e ocupa — não
  precisa de progressão nenhuma. A aresta enrijece onde a regra de parada é a própria ocupação, que
  é o caso do 77/2026: *analisar a documentação até o limite de vagas, substituir o indeferido pelo
  próximo sorteado, parar quando as vagas se preencherem*.

## 5. As duas questões que continuam abertas

Nenhuma se decide lendo código, e as duas precedem a abertura de spec.

### Q-1 · A fronteira entre a `016` e a `019`

Há duas frases incompatíveis no repositório, e nenhuma feature existe para forçar a escolha:

| Fonte | O que diz |
|---|---|
| arco da `013`, repetido pela `015` e pela `022` | *"016 ocupa vagas"* — e a `019` convoca |
| `specs/018-…/spec.md:1259` | *"**Ocupação de vagas**, convocação, aceite, posse e matrícula — são da 019"* |

A leitura que sustenta a separação: a `016` é **aritmética determinística** — quantas vagas há, por
lista, e quem cabe nelas —, e a `019` é **ato administrativo com prazo** — convocar, esperar
resposta, chamar o próximo, matricular. A leitura da `018` junta as duas porque, do ponto de vista
do recurso, ocupar e convocar são o mesmo evento na vida do candidato.

**Decidir isto antes de especificar qualquer uma das duas.** Especificar com a fronteira ambígua
produz duas features que se sobrepõem ou uma lacuna entre elas.

### Q-2 · O quadro de vagas: caminho binário ou forma estruturada

Já registrada em
[`descoberta-escopo-sorteio-e-anexos.md`](descoberta-escopo-sorteio-e-anexos.md), que a classificou
como questão que **precede** a `020` e a `021`. As duas foram construídas sem que ela fosse
respondida — o que é legítimo, porque nenhuma delas dependia da resposta, e continua pendente
porque a L-1 depende.

É a primeira decisão que uma spec da L-1 teria de tomar, e não a última.

## 6. A restrição que a `019` herda, e que não é dela desfazer

A `018` decidiu, na D-007, que recurso deferido produz **progressão retroativa de efeito pleno**,
com guarda de publicação e aviso nomeado. É decisão normativa **vigente**.

A fundamentação principal é jurídica: *"é o que restitui o candidato ao estado em que estaria se o
erro não tivesse ocorrido, que é a finalidade do deferimento. Qualquer coisa menos que isso torna o
deferimento simbólico"* ([decisão 018, alternativa 7A](decisao-018-escopo-institucional-do-recurso.md)).
Acompanha-a um argumento de **custo**, e só de custo: *"nenhuma vaga está ocupada. Convocação,
aceite, posse e matrícula são da 019, que não existe. Este é o momento mais barato da vida do
produto para admitir progressão retroativa — depois da 019, ela disputa vaga com quem já foi
convocado."*

**A formulação correta da consequência**, e é ela que fica registrada:

> A `019` terá de confrontar uma decisão da `018`. A progressão retroativa foi definida quando
> nenhuma vaga estava ocupada; a `019` precisa especificar seus efeitos depois de convocação, aceite
> ou matrícula, **preservando a decisão vigente ou propondo formalmente sua revisão**.

Dizer que a `019` "reabre" a `018` é impreciso e foi recusado nesta sessão: uma feature nova não
reabre decisão vigente por existir. Ela a consome, ou propõe alterá-la pelo caminho que a
Constituição prevê.

## 7. As quatro correções desta sessão

Escritas porque a fundamentação de uma tese inclui o que quase a derrubou.

1. **"Três dos quatro Editais de sorteio têm cotas" era falso.** São dois — 57 e 28. O 77 e o 76 são
   declarados *sem cotas* em `specs/021-…/spec.md:127-128`. O erro atingia justamente o número que
   sustentava a tese; o denominador certo não é o subconjunto de sorteio, e sim quem precisa de
   quantidade por modalidade — três dos seis, §2.
2. **A sequência linear `L-1 → 014 → 016 → 019` era rígida demais.** A L-1 não é pré-requisito da
   `014`, e o diagrama da §4 substitui a cadeia.
3. **A fronteira `016`/`019` não é detalhe de escopo**: é a Q-1, e precede as duas.
4. **"A `019` reabre a `018`" foi recusado**, e a §6 traz a formulação que ficou.

E duas formulações ajustadas: a `018` **não** escolheu efeito pleno *porque* nenhuma vaga estava
ocupada — esse fato barateou a escolha, cuja razão principal é jurídica; e "fechar o arco não ajuda
os três Editais" era contraditório com a L-1 dentro do arco. A frase correta é: **fechar apenas as
três features reservadas — `014`, `016` e `019` — não destrava a autoria desses Editais; a L-1,
sim.**

## 8. O que este documento **não** decide

- **Não decide o que construir a seguir.** A tese ordena; ela não prioriza.
- **Não abre spec.** Nenhuma linha daqui vira requisito, tarefa ou migration antes de a spec
  correspondente ser aberta, planejada e analisada pelo fluxo da Constituição.
- **Não responde a Q-1 nem a Q-2.** As duas são de governança e ficam com o usuário.
- **Não trata das lacunas fora deste encadeamento** — heteroidentificação (L-2), barema (D-4), fato
  sem grandeza (L-4), P-6, P-7, P-8. Elas continuam na
  [avaliação de 09/09](avaliacao-de-capacidade-editais-2026-09-09.md), que é o inventário.
