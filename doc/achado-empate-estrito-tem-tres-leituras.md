# O empate estrito tem três leituras — a da tela, a do Edital e a do motor

**Encontrado em**: 19/10/2026, ao avaliar uma análise de usabilidade da etapa Classificação feita
fora do repositório, contra a `main` em `745f115f`.

**Estado**: **aberto**. Registro, não correção: nada no código, nas telas ou no documento foi
alterado.

---

## Como apareceu

A análise trazia uma tabela ilustrativa para alvo 10 com 5 suplentes: a Daniela e o Eduardo
empatados na 10ª posição, o Eduardo marcado *"avança por empate"*, e os seguintes como suplentes.
Rodado no motor, o exemplo não é esse. Com 10 + 5, a faixa tem quinze pessoas: o Eduardo é a 11ª
dela e entra pela contagem comum, sem empate nenhum. O desfecho do empate só se aplica na 15ª. A
análise foi escrita por quem acompanha o desenvolvimento, e montou o exemplo pelo que o rótulo diz.

## O que se vê

O mesmo valor de `cutRule.tieOutcome` aparece em quatro lugares, e cada um diz uma coisa:

| Onde | O que diz de `STRICT` | Fonte |
|---|---|---|
| Composição, cartão do marco | *"A faixa para no alvo"* | `interface/templates/interface/_marco.html`, opção de `cutTieOutcome` |
| Documento publicado e Revisão | *"Se houver empate na última posição, esse número não é ultrapassado."* | `EMPATE_NO_CORTE_2`, `publicacoes/infrastructure/pdf.py`; a Revisão importa a frase |
| Narrativa da `014` | *"alvo estrito, e o corte para no alvo"* | `specs/014-corte-e-progressao-entre-etapas/spec.md`, na decisão de 11/09 |
| Motor do corte | **recusa a emissão** enquanto houver empate residual na última posição de `alvo + excedente` | `faixa.calcular` → `EmpateAtravessaOCorte`; `classificacao/application/corte.py` o traduz em `empate_atravessa_o_corte`, 409 |

O motor faz o que a `FR-195` da `014` manda — *"MUST recusar a emissão, nomeando as posições
empatadas"* —, e a `FR-181` fala da última posição **da faixa**, que a `FR-180` define como alvo mais
excedente. Quem diverge é o texto à volta:

1. **"Para no alvo" é a fronteira errada sempre que há suplentes.** O motor confere o empate na
   15ª posição de uma faixa de 10 + 5, e não na 10ª. O rótulo da tela e a narrativa da `014` nomeiam
   o alvo.
2. **Nenhum dos textos diz que o corte é recusado.** *"Para no alvo"* e *"não é ultrapassado"* leem-se
   como **"entram só os que cabem"**, quando o que acontece é não sair corte nenhum até alguém julgar
   o desempate ou retificar o desfecho. Quem escolhe `STRICT` acreditando que o sistema corta não
   sabe que escolheu uma parada.
3. **O "esse número" do documento não diz qual número.** A frase anterior acabou de publicar dois:
   *"os 10 (dez) primeiros classificados, mais 5 (cinco) suplentes"*. O motor usa quinze. Um
   candidato que lê o Edital pode entender dez.

## Uma quarta fronteira, que nenhum texto declara

A apuração da ocupação tem a sua própria recusa, `EmpateNaFronteiraDoAlvo`
(`ocupacao/domain/apuracao.py`, `R-002` da `019`): empate residual que deixa parte do grupo dentro e
parte fora das primeiras **vagas efetivas** da sequência que progrediu. O docstring é explícito —
*"para essa a norma publicada não diz nada"* — e ela dispara **qualquer que seja o `tieOutcome`**.

Quem escolheu *"Todos os empatados progridem"* acredita ter resolvido o empate. Resolveu o da faixa.
O da última vaga continua parando a apuração, e nem a tela nem o documento avisam.

## Reprodução

`faixa.calcular` e `apuracao.titulares_iniciais`, chamados direto, com todos habilitados, vagas
efetivas iguais ao alvo e o empate tratado como residual (os critérios publicados já esgotados):

| Cenário | `ADMITS_SURPLUS` | `STRICT` |
|---|---|---|
| Alvo 10, 5 suplentes, empate de dois na 10ª | corte com 15, nenhum por empate; ocupação **recusa** na posição 10 | idem: o corte sai, e a ocupação **recusa** na posição 10 |
| Alvo 10, 5 suplentes, empate de dois na 15ª | corte com 16, um por empate; ocupação com 10 titulares | corte **recusado** na posição 15 |
| Alvo 10, sem suplentes, empate de dois na 10ª | corte com 11, um por empate; ocupação **recusa** na posição 10 | corte **recusado** na posição 10 |

A primeira linha é o exemplo da análise. O desfecho declarado não muda nada nela: o corte sai igual
nos dois, e a recusa vem depois, numa fronteira que o elaborador nunca declarou.

As frases do documento foram geradas por `frases_do_corte` com o mesmo marco (alvo fixo 10, 5
suplentes, Etapa governada *Entrevista*, continuação `NONE`, sem cadastro de reserva).

## Por que importa

- **Princípio I da Constituição**: conceitos *"DEVEM possuir significado inequívoco e equivalente em
  especificações, código, [...] documentação e interfaces"*. Aqui o mesmo valor tem três
  significados.
- **O documento é o ato legal.** O que o Edital diz do empate é o que o candidato pode invocar. Se ele
  lê *"esse número"* como dez, e o sistema decide em quinze, a divergência é normativa, e não de
  redação.
- **A consequência só aparece na execução.** A publicação aceita qualquer das duas escolhas, e a
  recusa chega no dia de emitir o corte ou de apurar a ocupação, com o certame em andamento. É o
  risco que a análise de usabilidade descrevia em abstrato: configurar, acreditar que está certo e
  descobrir depois.
- **A ajuda não alcança quem vê a tela.** A explicação do campo, *"Não há padrão: sem esta
  declaração o Edital não publica"*, é `class="oculto"` — só para leitor de tela, pela `FR-428` da
  `030` — e não fala do efeito. O bloco *Como preencher* da etapa também não.

## O que não se decidiu aqui

- **Qual texto se corrige.** O rótulo e o documento podem passar a dizer o que o motor faz, ou o motor
  pode estar aplicando uma leitura que o produto não quer. A `FR-195` sustenta o motor; a narrativa da
  `014` diz outra coisa, e a decisão de 11/09 é do usuário.
- **O referente de "esse número".** Dizer *"a última das quinze posições"* mudaria a redação que a
  `069` fixou (K1 a K10), e as frases do corte são unidade indivisível (`FR-1375` e `R-009` da
  `069`, como o docstring de `frases_do_corte` as cita).
- **Se a fronteira das vagas merece declaração.** Hoje ela é recusa sem norma, de propósito
  (`R-002` da `019`). Declará-la seria campo novo no conteúdo canônico, e portanto spec.
- **O acervo.** Editais já publicados não se regeneram (Princípio II): o que eles dizem do empate
  continua dito. Mudar a redação muda o que os próximos publicam, e a prévia de um Edital antigo
  passaria a mostrar o texto novo.
- **A relação entre suplentes e cadastro de reserva**, que o documento não explica quando há cadastro
  (`DP-05`, citada em `frases_do_corte`). Ela confunde a leitura do mesmo bloco, e não é este achado.

Registro, não escopo.
