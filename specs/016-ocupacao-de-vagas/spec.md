# Feature Specification: Ocupação de Vagas entre Listas de Concorrência

**Número:** `016` · **Diretório:** `specs/016-ocupacao-de-vagas`
**Criada:** 2026-09-12
**Estado:** decisões fechadas em 12/09/2026 (§3.0) — pronta para `$speckit-plan`

**Faixa de identificadores desta feature:** `FR-239`+, `SC-078`+, `UX-031`+. A faixa é **global**
desde a `024`: o teto foi medido em `daded41` (`FR-238`, `SC-077`, `UX-030`) e não reinicia.

> **Esta feature não escolhe candidato e não convoca ninguém.** A fronteira está fechada pela
> decisão de fronteira da `014` — tomada pelo usuário em 11/09/2026 — e **não se reabre aqui**:
>
> ```
> "analisar o próximo candidato da ordem"   → 014
> "quantas vagas ainda não foram ocupadas"  → 016
> "convocar e comunicar o candidato"        → 019
> ```

---

## 1. O achado que organiza a feature

**O sistema publica há muito tempo os números de que precisa para ocupar vaga, e nenhuma regra os
lê.** `percentage`, `distribution` e `callRules` viajam no conteúdo publicado desde a `001`
(`publicacoes/application/publish_edital.py:118-123`); `vacancyTable` entrou no **degrau 12** com a
`025`. Conferido em `daded41`: `distribution` e `callRules` são escritos pela publicação, relidos
pelo rascunho e editados pela interface — e **nenhum domínio computa com eles**. O `vacancyTable`
ganhou dois leitores, a conferência da soma e o alvo derivado do corte da `014`, e nada além.

Quer dizer: o sistema sabe quantas vagas cada lista tem, sabe a ordem de cada lista, e **não sabe
dizer quantas dessas vagas estão ocupadas**. É a pergunta que fica entre a ordem publicada e a
convocação, e é a única coisa que falta para três Editais da amostra irem além da ordem.

### 1.1 As cláusulas reais, nas palavras dos Editais

Três Editais da amostra pedem esta feature, e pedem **coisas diferentes**. Lidos em
`~/Downloads`, com `pdftotext -layout`:

| Edital | Cláusula | O que manda |
|---|---|---|
| **77/2026** | 6.3 | analisar a documentação dos primeiros sorteados até o limite de vagas; indeferido um, analisa-se o próximo, *"até que se preencha o número total de vagas ofertadas"* |
| **77/2026** | 6.7 | inscrição indeferida deixa *"a vaga disponível para o próximo candidato habilitado"* |
| **28/2026** | 4.3 | ***em cada polo***, havendo ausência de aprovados na reserva (PPI e PcD), *"o quantitativo de vagas será destinado para a respectiva vaga de ampla concorrência"* |
| **57/2026** | 4.3 | na hipótese do ***não preenchimento total*** das vagas de ações afirmativas, o quantitativo vai para a respectiva ampla concorrência |
| **57/2026** | 4.5 | *"Não haverá remanejamento de vagas remanescentes entre os cursos."* |
| **28/2026** | 4.3.1 e 8.7 | quem se inscreve em vaga reservada concorre **concomitantemente** à reservada e à ampla |
| **28/2026** | 8.8 | sorteado dentro do número de vagas **nas duas listas** → classificado na lista de ampla concorrência |
| **28/2026** | 8.9 | autodeclarado sorteado dentro das vagas de ampla **não é computado** no preenchimento das reservadas, *"abrindo vaga para o próximo suplente autodeclarado"* |
| **28/2026** | 8.8 *in fine* | desistência em vaga reservada → a vaga é preenchida pelo autodeclarado classificado imediatamente após |

**E um quarto que parecia pedir e não pede.** O 14/2026 (4, 6.6 e 9 *b*) manda convocar os 10
melhores do Grupo 1 por código e, *"caso o número de classificados deste grupo seja menor que 10"*,
os do Grupo 2 e do Grupo 3, nesta ordem. O gatilho é contagem de **classificados**, e por isso a
cascata é alvo derivado da `014` — ver `D-006`. A leitura fica registrada aqui porque foi ela que
produziu a decisão.

### 1.2 São três mecanismos distintos, mais um que não é desta feature

A leitura acima separa três coisas que a palavra "remanejamento" junta:

1. **Déficit por recusa** (77/2026 6.3 e 6.7). A vaga continua sendo **da mesma lista**; o que
   falhou foi o candidato. A vaga não muda de recorte, e o que se apura é *quantas faltam*.
2. **Reversão de cota** (28/2026 4.3; 57/2026 4.3). Vaga reservada **não preenchida** muda de
   recorte: passa para a ampla concorrência do mesmo Perfil — e, no 28, do mesmo **polo**.
3. **Concorrência concomitante** (28/2026 4.3.1, 8.7, 8.8, 8.9). A mesma pessoa está em duas
   listas. Ocupar pela ampla **libera** a vaga reservada dela, que volta ao recorte reservado — e
   não à ampla. É movimento em sentido contrário ao da reversão.

E um quarto que a palavra também junta e que **não é desta feature**: a **cascata entre recortes**
do 14/2026 (6.6), cujo gatilho é *"o número de classificados deste grupo seja menor que 10"* — uma
contagem de classificados, não de vagas ocupadas.

**O quarto é o que não se parece com os outros três, e foi decidido em 12/09/2026 (`D-006`).**
A decisão de fronteira da `014` adverte, com estas palavras, contra *"usar 'quantidade de
habilitados' como sinônimo incorreto de 'vagas ocupadas'"*. O gatilho do 14/2026 é exatamente uma
quantidade de classificados; e o
*Out of Scope* da `014` mandou a cascata para cá. As duas frases não podiam estar certas ao mesmo
tempo, e a `D-006` escolheu a primeira.

### 1.3 O 57/2026 proíbe por escrito o que o nome da feature promete

A cláusula 4.5 do 57 — *"não haverá remanejamento de vagas remanescentes entre os cursos"* — é a
prova de que **remanejamento entre Perfis é declarado, nunca presumido**. Um sistema que
remanejasse por conta própria produziria, naquele Edital, exatamente o que ele proíbe. A ausência
de declaração significa **não remaneja**, e não "remaneja do jeito comum".

---

## 2. O que já existe, e que esta feature NÃO reconstrói

| Capacidade | Onde está | O que a `016` faz com ela |
|---|---|---|
| quantas vagas cada lista tem | `vacancyTable` no Perfil publicado, degrau 12 (`025`) | **lê**; nunca reescreve |
| qual Modalidade é a ampla concorrência | `generalCompetitionModalityId` (`014`, `FR-231`) | **lê**; é o que torna a reversão endereçável sem casar nome |
| a ordem de cada lista | ato de ordenação da `015`, recorte Perfil + marco + `lista_id` | **lê**; não reordena nem desempata |
| quem progride, e a faixa | corte da `014` | **causa** nova faixa; não a calcula |
| o percentual que fundamenta a cota | `percentage` | **não deriva quantidade dele** — a `025`, `FR-157`, proíbe |
| a ordem de chamada entre recortes | `callRules` | **lê**, e é o primeiro consumidor que ele tem |
| convocar, comunicar, aceitar, matricular | nada ainda — é a `019` | **não faz** |

---

## 3. Decisões

### 3.0 As três que precediam o planejamento, respondidas em 12/09/2026

As três foram apresentadas ao usuário antes do plano, com as opções e o custo de cada uma, e as
três foram respondidas por ele. Ficam registradas como `D-006`, `D-007` e `D-008`.

### D-006 — A cascata entre recortes é da `014`, e esta feature não a implementa

*Decisão do usuário, 12/09/2026 — opção (B) da `Q-1`.*

A cascata Grupo 1→2→3 do 14/2026 dispara por *"caso o número de classificados deste grupo seja
menor que 10"*, que é contagem de **classificados** e não de vagas ocupadas. Ela passa a ser uma
segunda espécie de **alvo derivado** da `014`, que lê `callRules` e alcança o recorte seguinte.

A decisão segue a advertência da própria fronteira — *"não usar 'quantidade de habilitados' como
sinônimo incorreto de 'vagas ocupadas'"* — contra a letra do *Out of Scope* da `014`, que havia
mandado a cascata para cá. **As duas frases eram incompatíveis, e esta decisão escolhe a primeira.**

Duas consequências, e a segunda é de governança:

1. **O 14/2026 sai da amostra desta feature.** Ele não tem cota, não tem reserva e não tem
   reversão: o que ele precisa é de ordem de chamada entre recortes, que é alvo derivado. Esta
   feature deixa de ter história para ele, e a §8 deixa de prometê-lo.
2. **O *Out of Scope* da `014` ficou contradito, e foi emendado.** Aquela spec está mesclada, e
   corrigir artefato entregue é ato de governança: a emenda foi autorizada pelo usuário em
   12/09/2026 e feita no mesmo dia, registrando a redação anterior e dizendo que a capacidade é da
   linha daquela feature e **não está construída**.

### D-007 — O gatilho da reversão é declarado pelo Edital, em duas espécies

*Decisão do usuário, 12/09/2026 — opção (B) da `Q-2`.*

O 28/2026 (4.3) reverte *"havendo ausência de candidatos aprovados"*; o 57/2026 (4.3) reverte *"na
hipótese do não preenchimento total"*. São gatilhos diferentes, e **o Edital declara qual usa**:

| Espécie | Reverte |
|---|---|
| **por esgotamento** | só quando a lista reservada não tem mais ninguém a ocupar |
| **por saldo** | a quantidade não preenchida, ainda que a lista tenha gente |

A alternativa — uma regra só, a do saldo, tratando a redação do 28 como o mesmo efeito — foi
recusada porque decidiria no plano uma divergência de **norma** entre dois Editais reais, e porque
o erro não teria conserto: vaga revertida sob leitura larga num Edital que manda a estreita é vaga
que saiu do recorte reservado sem fundamento, em ato publicado.

O custo está aceito e é o de sempre para campo normativo novo: mais um campo no conteúdo publicado,
com elevação de versão canônica, caminho de leitura das versões anteriores, presença no documento e
entrada no catálogo de Retificação.

### D-008 — A apuração é ato append-only por recorte, e ler não ocupa

*Decisão do usuário, 12/09/2026 — opção (A) da `Q-3`.*

A apuração de ocupação é **ato**, sucedido a cada mudança, como a ordem da `015` e o corte da `014`
já são — e não projeção calculada sob demanda. É a mesma forma que a `014` fechou para o corte:
*"cortar é emitir um ato, e ler não corta"*.

A projeção foi recusada pelo que ela perde: o número de ontem não é recuperável se os atos-fonte
mudarem de leitura, e ocupação é exatamente o número que alguém vai contestar. A Constituição manda
que nada se exclua, e sucessão é como este sistema corrige sem apagar.

O custo entra **antes** da primeira tela: entidade, migration, privilégio de append-only sobre a
tabela nova, sucessão e obsolescência. A §8 muda por causa disso.

### 3.1 As que já estão fechadas por decisão anterior, e que esta spec apenas herda

### D-001 — A fronteira com a `014` e a `019` é a que a `014` fixou, e esta feature a herda

A decisão de fronteira da `014`, tomada pelo usuário em 11/09/2026 e citada na abertura. Três
consequências que governam os requisitos: a `016` **não** reimplementa ordem, **não** escolhe
candidato, e **não** convoca. O que ela produz é o **déficit** e a **causa** que a `014` consome
para emitir a faixa seguinte — o lugar que aquela feature hoje preenche com motivo textual
declarado por quem emite.

### D-002 — Ausência de declaração significa "não move"

Herdada da cláusula 4.5 do 57/2026 (§1.3) e da mesma disciplina que a `025` aplicou ao quadro
ausente: coleção vazia é "não publicou", não "zero". Edital que não declara reversão **não
reverte**; Edital que não declara remanejamento entre Perfis **não remaneja**.

### D-003 — A quantidade nunca sai do percentual

Herdada da `FR-157` da `025`: o percentual fundamenta a cota e não a calcula. A `016` lê
`vacancyTable`. O `percentage` serve, no máximo, a advertência — nunca a conta.

### D-004 — A reversão é endereçada por identidade declarada, nunca por nome

O destino da reversão é *"a respectiva ampla concorrência"*, e o recorte da ampla é a **linha
geral** do quadro — `modalityId` nulo. Onde o Edital declara uma Modalidade chamada "Ampla
concorrência", quem diz qual é ela é `generalCompetitionModalityId` (`014`, `FR-231`), e não a
grafia do nome. A `R-006` da `025` recusou casar nome por escrito, e esta feature não o
reintroduz.

### D-005 — O recorte da ocupação é o do ato de ordenação

Perfil, marco e lista — o mesmo recorte que a `015` emite e que a `014` corta. **O polo do 28/2026
é um Perfil**, e é por isso que a reversão "em cada polo" não pede dimensão nova: ela é reversão
dentro do Perfil, entre a linha reservada e a linha geral do **mesmo** quadro.

---

## 4. Problema

Um Edital publica 28 vagas de ampla concorrência, 10 de PPI e 2 de PcD em cada um de sete polos. O
sorteio acontece, as três ordens saem, a documentação é analisada. Três candidatos de PPI são
indeferidos e, naquele polo, nenhum outro se inscreveu na reserva. O Edital manda destinar o
quantitativo à ampla concorrência daquele polo.

Hoje o sistema chega até a ordem e para. Ele sabe que a linha de PPI daquele Perfil tem 10 vagas,
sabe quem está na ordem de PPI, sabe quem foi indeferido — e não tem onde registrar que sete vagas
de PPI viraram sete vagas de ampla, nem como dizer à `014` que a faixa da ampla precisa de sete
posições a mais. A operação faz essa conta numa planilha, e o que o sistema publica depois não
guarda por que aquela faixa teve o tamanho que teve.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Ver quantas vagas de cada lista ainda faltam (Priority: P1)

A presidência abre o Perfil e vê, recorte por recorte, quantas vagas o Edital publicou, quantas
estão ocupadas e quantas faltam — com cada número rastreável ao ato que o produziu.

**Por que P1.** É a pergunta que não tem resposta hoje, e todas as outras histórias dependem de ela
existir. Entregue sozinha, já substitui a planilha.

**Percurso independente.** Com um Edital publicado com quadro, ordem emitida e corte emitido, abrir
a tela do Perfil e ler os quatro números por recorte, sem emitir nada.

**Aceitação**

1. **Dado** um Perfil com linha geral de 28 e linha de PPI de 10, **quando** nada foi ocupado,
   **então** a tela diz 28 e 10 faltando, e zero ocupadas.
2. **Dado** que a análise documental recusou 3 de PPI, **quando** a apuração corre, **então** o
   déficit de PPI é dito em número, e a causa de cada vaga não ocupada é legível.
3. **Dado** um Edital publicado **sem** quadro de vagas, **quando** a tela abre, **então** ela diz
   que o Edital não publicou quadro — e **não** afirma zero vaga.

### User Story 2 — Reverter vaga reservada não preenchida para a ampla (Priority: P1)

Apurado o déficit da lista reservada, e declarada a reversão pelo Edital, o quantitativo passa à
linha geral do mesmo Perfil, com registro de quanto passou e por quê.

**Por que P1.** É a cláusula que alcança 57 e 28 — quatro Editais com a dimensão de polo contada.

**Aceitação**

1. **Dado** um Perfil cujo Edital declara reversão, **quando** a lista de PPI esgota com saldo,
   **então** a linha geral ganha aquele saldo e o registro diz origem, destino e quantidade.
2. **Dado** um Perfil cujo Edital **não** declara reversão, **quando** a lista esgota com saldo,
   **então** nada é revertido e a tela diz que aquele Edital não prevê reversão.
3. **Dado** o 57/2026, que proíbe remanejamento entre cursos, **quando** um Perfil esgota,
   **então** nenhuma vaga alcança outro Perfil, por nenhum caminho.

### User Story 3 — Causar a faixa seguinte com déficit apurado (Priority: P1)

Apurado o déficit, a `016` o entrega como causa para a `014` emitir a faixa seguinte — no lugar do
motivo textual que aquela feature hoje exige de quem emite.

**Por que P1.** É o fecho do ciclo do 77/2026, e é o que a decisão de fronteira da `014` descreve
como a travessia da fronteira nos dois sentidos.

**Aceitação**

1. **Dado** um déficit de 3 na linha geral, **quando** a faixa seguinte é emitida, **então** o ato
   guarda o déficit apurado como causa, e não texto digitado.
2. **Dado** déficit zero, **quando** alguém tenta emitir faixa seguinte por ocupação, **então** é
   recusado dizendo que não há vaga a preencher.
3. **Dado** que a ordem foi sucedida, **quando** a apuração corre, **então** ela recusa apurar
   sobre ordem que não é a vigente.

### User Story 4 — Tratar quem ocupa por duas listas ao mesmo tempo (Priority: P2)

Quem concorre concomitantemente e ocupa pela ampla concorrência libera a vaga reservada, que volta
ao recorte reservado e alcança o próximo daquela lista.

**Por que P2.** É a regra do 28/2026 (8.8 e 8.9), e depende das três primeiras histórias existirem.

**Aceitação**

1. **Dado** alguém dentro do número de vagas nas duas listas, **quando** a ocupação é apurada,
   **então** ele ocupa pela ampla e a vaga reservada dele fica disponível.
2. **Dado** esse caso, **quando** a vaga reservada é liberada, **então** ela alcança o próximo da
   **lista reservada**, e nunca a linha geral.
3. **Dado** que ninguém mais existe na lista reservada, **então** o que sobra é déficit reservado —
   e a reversão da História 2 decide o que acontece com ele.

### User Story 5 — Auditar a ocupação de ponta a ponta (Priority: P3)

Cada número exibido tem trilha: qual ato o produziu, sobre qual ordem, com qual quadro publicado.

**Aceitação**

1. **Dado** um Perfil com reversão e liberação, **quando** a auditoria é lida, **então** a
   sequência de movimentos reconstrói o número de hoje a partir do quadro publicado.
2. **Dado** o quadro retificado depois da apuração, **quando** a auditoria é lida, **então** fica
   legível qual versão do quadro cada apuração leu.

### Edge Cases

- **Quadro ausente.** Edital publicado antes do degrau 12 não tem quadro: a apuração **não corre** e
  diz por quê, em vez de tratar ausência como zero.
- **Soma do quadro menor que o total do Perfil.** É o que a `R-006` deixa passar hoje no formato
  normal (ver [achado](../../doc/achado-igualdade-da-soma-sem-a-ampla-declarada.md)). A apuração usa
  a **linha**, nunca o total do Perfil, e por isso não herda a divergência.
- **Reversão que excederia o total do Perfil.** Reverter não cria vaga: a soma depois da reversão é
  igual à de antes, e qualquer resultado diferente é defeito, não arredondamento.
- **Ordem sucedida no meio.** Apuração sobre ordem não vigente é recusada, como o corte da `014` já
  recusa.
- **Corte obsoleto.** Se o corte que produziu a faixa está obsoleto, o déficit apurado sobre ele não
  causa faixa nova.
- **Retificação do quadro depois da apuração.** O número publicado muda; as apurações anteriores
  não se reescrevem. A retificação **obsoleta** a apuração (`FR-263`), e a vigente é a emitida
  depois dela.
- **Recorte sem linha no quadro.** Lista que ordena mas não tem linha de quadro não tem quantidade a
  apurar — e é exatamente o que a `014` já impede de publicar sob alvo derivado, ao exigir linha
  para todo recorte que o marco ordena.
- **Empate na fronteira da vaga revertida.** A vaga revertida entra na ampla e a faixa seguinte é da
  `014`: o desfecho do empate continua sendo o declarado pela `D-001` daquela feature.

---

## Requirements *(mandatory)*

### Functional Requirements

**A apuração**

- **FR-239**: O sistema MUST apurar, por recorte do ato de ordenação (Perfil, marco e lista),
  **quatro** quantidades: quantas vagas o Edital publicou, quantas o recorte tem **efetivamente**
  (as publicadas mais as recebidas, menos as cedidas), quantas estão ocupadas e quantas faltam.
- **FR-239a**: A quantidade publicada MUST permanecer **inalterada** por movimento de vaga: o que a
  reversão muda é a quantidade **efetiva**. *Sem esta separação, reverter faria o sistema afirmar
  que o Edital publicou um número que ele não publicou — e o publicado é intocável.*
- **FR-240**: A quantidade publicada MUST ser lida da **linha** do `vacancyTable` correspondente ao
  recorte, e nunca do total de vagas imediatas do Perfil.
- **FR-241**: O recorte da ampla concorrência MUST ser a linha geral do quadro — `modalityId`
  nulo —, e a Modalidade declarada como ampla concorrência MUST ser identificada por
  `generalCompetitionModalityId`, nunca por nome.
- **FR-242**: A apuração MUST ser recusada quando o Edital não publicou quadro de vagas, dizendo
  que não há quantidade declarada — e MUST NOT tratar ausência como zero.
- **FR-243**: A apuração MUST ser recusada sobre ordem que não é a vigente do recorte.
- **FR-244**: A apuração MUST ser reproduzível: a mesma ordem, o mesmo quadro e os mesmos
  movimentos produzem o mesmo número.

**A reversão de cota**

- **FR-245**: O Edital MUST poder declarar que vaga reservada não preenchida reverte para a ampla
  concorrência do mesmo Perfil. Ausência da declaração significa **não reverte** (`D-002`).
- **FR-246**: A reversão MUST mover quantidade da linha da Modalidade para a linha geral do
  **mesmo** Perfil, e MUST NOT alcançar outro Perfil por nenhum caminho.
- **FR-247**: A soma das quantidades por recorte depois da reversão MUST ser igual à soma antes
  dela. Reverter redistribui; não cria nem destrói vaga.
- **FR-248**: Cada reversão MUST registrar origem, destino, quantidade e a causa que a autorizou.
- **FR-249**: O Edital MUST declarar **qual espécie de gatilho** a reversão usa — por esgotamento
  ou por saldo (`D-007`) —, e o gatilho MUST NOT ser inferido do estado das listas.
- **FR-250**: A declaração da espécie MUST ser conteúdo publicado, com elevação de versão
  canônica, caminho de leitura das versões anteriores, presença no documento e entrada no catálogo
  de Retificação.
- **FR-251**: Declarada a reversão sem a espécie, a publicação MUST ser recusada — a ausência
  MUST NOT virar espécie padrão.

**A concorrência concomitante**

- **FR-252**: Quem ocupa vaga pela ampla concorrência MUST NOT ser computado no preenchimento da
  lista reservada em que também concorre.
- **FR-253**: A vaga reservada liberada por `FR-252` MUST voltar ao recorte **reservado**, e
  MUST NOT ir para a linha geral.
- **FR-254**: Estando alguém dentro do número de vagas nas duas listas, o sistema MUST registrar a
  ocupação pela **ampla concorrência**.

**O efeito na `014`**

- **FR-255**: O déficit apurado MUST poder ser entregue à `014` como causa da faixa seguinte, no
  lugar do motivo textual que aquela feature exige hoje de quem emite.
- **FR-256**: O sistema MUST recusar faixa seguinte por ocupação quando o déficit apurado é zero.
- **FR-257**: A `016` MUST NOT selecionar candidato, ordenar, desempatar ou convocar. Toda seleção
  continua sendo ato da `014`, e toda convocação da `019`.
- **FR-258**: Nenhuma tela, ato ou mensagem da `016` MUST afirmar que alguém foi convocado,
  aceitou ou matriculou-se — esses fatos não existem antes da `019`.

**Auditoria**

- **FR-259**: Cada número apurado MUST ser rastreável ao ato de ordenação, à versão do conteúdo
  publicado e aos movimentos que o produziram.
- **FR-260**: Nenhum registro de ocupação ou reversão MUST ser alterado ou excluído depois de
  gravado; correção é sucessão, como no resto do sistema.
- **FR-261**: A apuração MUST ser um ato emitido, e a leitura da tela MUST NOT produzir apuração
  (`D-008`) — ler não ocupa, como ler não corta.
- **FR-262**: Emitida apuração nova para o mesmo recorte, a anterior MUST ficar **sucedida**, e a
  sucessão MUST nomear a causa.
- **FR-263**: A apuração MUST ficar **obsoleta** quando a ordem do recorte é sucedida, quando o
  corte que a alimentou fica obsoleto, quando o quadro publicado é retificado, ou quando um
  movimento de vaga alcança o recorte depois dela — e apuração obsoleta MUST NOT causar faixa
  seguinte.

### Requisitos de apresentação

- **UX-031**: A tela do Perfil MUST dizer, por recorte, os quatro números — publicadas, efetivas,
  ocupadas e faltando — e MUST NOT exibir um deles sozinho. Onde nenhum movimento alcançou o
  recorte, efetivas e publicadas coincidem, e a tela MAY dizê-lo em um número só; onde divergem,
  MUST dizer os dois. *A redação anterior pedia três números e ficava incoerente depois da
  reversão: publicadas seguiam 28 enquanto o que faltava saía de 35.*
- **UX-032**: Onde o Edital não publicou quadro, a tela MUST dizer isso com estas palavras, e
  MUST NOT mostrar zero.
- **UX-033**: A reversão MUST aparecer nomeada, com origem, destino e quantidade — e não como
  mudança silenciosa do número da linha geral.
- **UX-034**: O vocabulário MUST ser "vaga ocupada", "vaga a ocupar" e "revertida". Termo de
  convocação MUST NOT aparecer nesta feature, e a proibição é verificável por varredura, como a
  `014` já fez com o vocabulário do corte.

### Key Entities

- **Apuração de ocupação** — ato append-only por recorte (`D-008`): quadro lido, ordem lida,
  ocupadas, faltando, instante, autoria, sucessora e causa de obsolescência.
- **Movimento de vaga** — origem, destino, quantidade, causa. Cobre reversão de cota e liberação por
  concorrência concomitante, que são sentidos opostos do mesmo movimento.
- **Declaração de reversão** — conteúdo publicado do Perfil: se reverte, e sob qual das duas
  espécies de gatilho (`D-007`). Alcançável por Retificação, e com degrau canônico próprio.

---

## 5. Invariantes observáveis

1. A soma das quantidades por recorte é **constante** sob reversão e sob liberação.
2. Nenhuma vaga atravessa Perfil.
3. Nenhuma quantidade sai de `percentage`.
4. Nenhuma apuração corre sobre ordem não vigente.
5. Nenhum registro de ocupação é alterado; o histórico reconstrói o número de hoje.
6. A ampla concorrência é sempre a linha geral, e a Modalidade homônima nunca tem linha própria.

---

## 6. Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-078**: A presidência lê, em uma tela, quantas vagas faltam em cada recorte de um Perfil com
  três listas, sem consultar planilha e sem somar à mão.
- **SC-079**: Num Perfil de 28 + 10 + 2 com reversão declarada, o esgotamento da lista de PPI com
  saldo 7 leva a quantidade **efetiva** da linha geral a 35 — com as publicadas seguindo 28 — e
  produz registro que nomeia os 7.
- **SC-080**: Num Edital que proíbe remanejamento entre cursos, nenhuma vaga de um Perfil alcança
  outro em nenhum percurso da interface.
- **SC-081**: O ciclo do 77/2026 fecha pela interface: faixa emitida, documentação recusada,
  déficit apurado, faixa seguinte emitida com o déficit como causa — sem motivo digitado à mão.
- **SC-082**: A apuração de um Edital com **7 Perfis** — os polos, conforme a `D-005` — e 3 listas
  cada, com 1.000 participantes por recorte, responde em **no máximo o dobro** do tempo que a
  emissão da ordem leva no mesmo volume. *A redação anterior dizia "um Perfil com 7 polos", que
  contradiz a `D-005`, e "tempo comparável", que não é limite verificável.*
- **SC-083**: Cem por cento dos números exibidos têm trilha até o ato que os produziu.
- **SC-084**: Recebida a reversão, o recorte de destino cujo número mudou aparece **obsoleto**, com
  a causa nomeada, sem que ninguém emita nada — e passa a vigente na primeira emissão seguinte. É o
  critério que prova a substituição da orquestração por obsolescência.

---

## 7. Out of Scope

- **Convocação, chamada, comunicação, aceite, suplência, posse e matrícula** — é a `019`, e a
  fronteira é a que a `014` fixou.
- **Seleção de quem progride, ordem, desempate e faixa** — continuam da `014` e da `015`. Esta
  feature apura quantidade; não escolhe pessoa.
- **Cascata entre recortes** — o "caso o número de classificados deste grupo seja menor que dez"
  do 14/2026 é **alvo derivado da `014`** por decisão de 12/09/2026 (`D-006`), e não ocupação de
  vaga. O *Out of Scope* daquela feature foi emendado no mesmo dia para dizê-lo, e registra que a
  capacidade **não está construída**: é trabalho de incremento próprio, e não desta spec.
- **Heteroidentificação** — spec própria, e dependente da aplicabilidade da Etapa por modalidade
  (L-2), que esta feature não abre. A cláusula 8.10 do 28/2026 é dela, não desta.
- **Derivar quantidade de percentual** — recusado pela `FR-157` da `025`.
- **Fechar a lacuna da `R-006`** — está registrada em
  [achado próprio](../../doc/achado-igualdade-da-soma-sem-a-ampla-declarada.md) e é decisão de
  usuário. Esta feature lê a linha, e por isso não depende dela.
- **Validade do Edital e prorrogação** — o item 6.11 do 77/2026 fala de convocar suplente em nova
  oferta dentro da validade. É a P-3, e não existe.
- **Recurso contra a apuração** — os objetos atacáveis continuam os que a `018` definiu.
- **Inscrição originada fora** — a P-8, que bloqueia o 76/2026 inteiro, é anterior a esta feature.

## Assumptions

- O polo do 28/2026 é um **Perfil**, e a reversão "em cada polo" é reversão dentro do Perfil
  (`D-005`). Se algum Edital real tratar polo como dimensão **dentro** de um Perfil, esta suposição
  cai e a feature muda de forma.
- A autoridade para apurar ocupação é a mesma cadeia que autoriza emitir a ordem e o corte, até que
  as capacidades constituídas digam outra coisa.
- O volume de referência é o mesmo da ordem e do corte: até 1.000 participantes por recorte.
- Nenhum Edital hoje publicado declara reversão, e portanto nenhuma apuração existe: a feature nasce
  sem migração de dado normativo, e o caminho de leitura das versões anteriores é o que preserva os
  publicados — como a `025` e a `014` fizeram nos degraus 12 e 13.
- A declaração de reversão e a espécie do gatilho (`D-007`) entram na **mesma** elevação de versão
  canônica. São campos de um objeto só, e separá-los seriam duas elevações para uma decisão só —
  foi o que a `014` concluiu ao juntar os quatro campos da regra de corte num degrau.

## 8. Ordem de implementação sugerida

*A ordem abaixo já incorpora a `D-008`: como a apuração é ato, a entidade e o privilégio vêm antes
da primeira tela, e não depois dela.*

1. **O cálculo puro** — ler quadro, ordem e recusas e apurar ocupadas e faltando, sem gravar.
   Determinístico e reproduzível, como a faixa da `014`.
2. **O ato de apuração** — entidade append-only, privilégio sobre a tabela nova, emissão,
   autorização, auditoria, sucessão e as **quatro** causas de obsolescência (`FR-263`) — a quarta
   é o movimento de vaga que alcança o recorte depois da apuração.
3. **A tela dos quatro números** — é a História 1, e é o que substitui a planilha.
4. **A declaração publicada da reversão** — esquema canônico, degrau, caminho de leitura das
   anteriores, elaboração na interface, documento e catálogo de Retificação, com as duas espécies
   da `D-007`.
5. **A reversão** — o movimento, o registro e o invariante da soma constante.
6. **A causa para a `014`** — o déficit apurado substituindo o motivo textual que aquela feature
   hoje exige de quem emite.
7. **A concorrência concomitante** — a liberação em sentido contrário, que é a História 4.

Os passos 1 a 3 e 6 fecham o 77/2026. Os passos 4, 5 e 7 alcançam o 57 e o 28. **Nenhum passo
alcança o 14/2026**, e é a consequência direta da `D-006`.

## 9. Gate de conclusão

A feature está concluída quando, pela interface administrativa e sem manipulação de banco, for
possível: ler os quatro números por recorte de um Perfil com três listas; declarar a reversão e
publicá-la no documento; ver a vaga reservada não preenchida passar à ampla, nomeada; emitir a
faixa seguinte tendo o déficit apurado como causa; ver a vaga liberada por quem ocupou pela ampla
voltar à lista reservada; e reconstruir, pela auditoria, o número de hoje a partir do quadro
publicado.
