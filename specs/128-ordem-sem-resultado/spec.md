# Feature Specification: A ordem por pontuação sem nenhum resultado é recusada

**Feature Branch**: `claude/128-ordem-sem-resultado-9720fd`, sobre a branch da `126`
(`claude/126-orientacao-p0-307906`, PR #414), em `262cf30f`

**Created**: 2026-11-06

**Status**: Draft. **Uma regra de negócio nova**, decidida pelo usuário em 06/11/2026: a emissão da
ordem por pontuação passa a ser recusada num caso que hoje é aceito. Sem migration, tabela, coluna,
permissão ou estado persistido novo.

**Input**: *"Recusar a emissão da ordem por pontuação quando nenhuma inscrição considerada no recorte
tem resultado em nenhuma Etapa enumerada pelo marco (G-01, opção b decidida pelo usuário em
06/11/2026). A ordem parcial e a ordem vazia 'ninguém concorreu' continuam emissíveis; o marco por
sorteio já é recusado. A recusa vale no comando, no gesto 'Ordenar o marco' da condução e na sucessão;
a tela da ordem prevê a recusa e não oferece 'Emitir ordem', dizendo por quê e levando à distribuição;
a conferência do gesto mostra o recorte como impedido. Sem migration; ordens vazias já gravadas
continuam válidas."*

> **Faixa de identificadores.** Esta spec usa a faixa reservada para ela: os requisitos funcionais de
> quatro mil e duzentos a quatro mil duzentos e vinte e nove, os critérios de mil e trezentos a mil
> trezentos e nove e os de experiência de duzentos e sessenta a duzentos e sessenta e quatro; os não
> usados ficam livres. O teto foi medido em 06/11/2026 em `specs/` de todas as worktrees desta máquina:
> o requisito quatro mil cento e vinte e três, o critério mil duzentos e quarenta e cinco e o de
> experiência duzentos e trinta e três; a `127` reservou até o requisito quatro mil cento e noventa e
> nove, o critério mil duzentos e noventa e nove e o de experiência duzentos e cinquenta e nove. As
> decisões reiniciam em `D-001`.
>
> **Origem.** O achado G-01 do estudo de orientação da jornada de 06/11/2026
> (`doc/estudo-orientacao-da-jornada-2026-11-06/`, PR #412) e a seção *Decisão do usuário* da `126`
> (PR #414), em que o usuário escolheu a opção b entre quatro.

## Por que esta feature existe

No Edital 91, o marco por pontuação enumera uma Etapa que ninguém avaliou ainda. A tela da ordem
calcula a ordem — todos sem posição, "Sem pontuação nas Etapas enumeradas" — e oferece "Emitir ordem".
O ato é imutável. Emitido assim, ele nasce com todos sem posição, fica obsoleto assim que o primeiro
resultado chega, e sucedê-lo exige motivo. Não há uso legítimo conhecido para ele: é a ordem emitida
antes de qualquer avaliação.

A `126` fez a confirmação dizer isso, e deixou a recusa ao usuário. **O usuário escolheu recusar
quando nenhuma inscrição considerada tem resultado em nenhuma Etapa enumerada** (opção b). Duas
alternativas mais fortes foram descartadas: recusar quando *alguma* inscrição está sem resultado (c)
travaria o Edital em que uma inscrição nunca terá resultado, e exigir uma declaração de ciência (d)
criaria estado persistido novo.

### O que esta spec cobre, e o que fica fora

Cobre:

1. **A recusa no comando**, que é a porta de gravação, e por isso alcança a tela da ordem, a sucessão e
   o gesto "Ordenar o marco" da condução, que chamam o mesmo comando.
2. **A previsão nas telas**: a tela da ordem não oferece o botão que seria recusado, diz por quê e
   leva à distribuição; a confirmação não abre; a conferência do gesto põe o recorte entre os
   impedidos, com a razão.
3. **A coerência** com a confirmação da `126` e com a derivação do andamento da `127`.

Fica fora, de propósito:

- **A ordem parcial** — algumas inscrições com resultado, outras sem: continua emissível, e a
  confirmação da `126` continua dizendo quantas ficam sem resultado em cada Etapa.
- **A ordem vazia** em que ninguém concorreu (universo sem inscrição, pela decisão da `049` sobre a
  ordem vazia e pela FR-492a da `034`): continua emissível e continua *Feito* na condução.
- **O marco por sorteio**: o comando já o recusa antes (`ordering_milestone_is_drawn`, FR-1318 da
  `067`), e esta recusa nem chega a ser avaliada nele.
- **Trocar *Falta* por *Depois* na célula da ordem da condução** (D7 do estudo): continua P3. A célula
  continua levando à tela da ordem, que agora explica.
- **O cartão "O que fazer agora", o "Andamento da seleção" e o "Próximo nesta lista"**: são da `127`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — O comando recusa a ordem sem nenhum resultado (Priority: P1)

A presidência da comissão do Edital 91 tenta emitir a ordem do marco por pontuação antes de qualquer
avaliação — pela tela, por um formulário antigo ainda aberto, ou pelo gesto "Ordenar o marco". O
sistema recusa, não grava ato nenhum, e diz quantas inscrições estão sem resultado, em quais Etapas, e
o que fazer: distribuir, avaliar e consolidar.

**Why this priority**: é a regra decidida. Fechar só a tela deixaria a porta do comando aberta para
quem tivesse o formulário antigo, e o dano é irreversível.

**Independent Test**: com um marco por pontuação e inscrições sem nenhum Resultado nas Etapas
enumeradas, chamar o comando de emissão com uma confirmação válida e conferir a recusa, a frase e que
nenhum ato foi gravado.

**Acceptance Scenarios**:

1. **Given** um recorte com inscrições consideradas e nenhum Resultado vigente em nenhuma Etapa que o
   marco enumera, **When** a emissão é pedida, **Then** ela é recusada, nenhum ato, posição ou evento de
   trilha de emissão é gravado, e a frase diz o número de inscrições, as Etapas e o caminho.
2. **Given** o mesmo recorte e uma ordem vigente já emitida (do acervo, antes desta regra), **When** a
   sucessão é pedida, com motivo, **Then** ela é recusada da mesma forma.
3. **Given** um recorte em que **uma** inscrição tem Resultado numa Etapa enumerada e as outras não,
   **When** a emissão é pedida, **Then** ela é aceita (ordem parcial).
4. **Given** um recorte sem nenhuma inscrição considerada, **When** a emissão é pedida, **Then** ela é
   aceita (ordem vazia, "ninguém concorreu").
5. **Given** um recorte recusado, **When** um Resultado é consolidado numa Etapa enumerada e a emissão
   é pedida de novo, **Then** ela é aceita.
6. **Given** um recorte em que a única coisa registrada é uma Ocorrência que eliminou uma inscrição numa
   Etapa enumerada, **When** a emissão é pedida, **Then** ela é aceita: a Ocorrência é Resultado.
7. **Given** um marco cuja Etapa de desempate não é enumerada, e Resultados só nela, **When** a emissão
   é pedida, **Then** ela é recusada: o desempate não decide quem tem posição.

---

### User Story 2 — A tela da ordem não oferece o que seria recusado (Priority: P1)

A presidência abre a tela da ordem do Edital 91 antes de qualquer avaliação. A ordem calculada
continua aparecendo — todos sem posição, com o motivo —, mas no lugar do formulário de emissão a tela
diz que a ordem não pode ser emitida ainda, por quê, e leva à distribuição de cada Etapa enumerada.

**Why this priority**: oferecer o que se vai recusar é pior do que não oferecer (FR-476 da `033`).
Com a regra nova, o botão "Emitir ordem" na tela do Edital 91 seria exatamente isso.

**Independent Test**: abrir a tela do recorte sem resultado, como quem emite, e conferir que não há
formulário de emissão nem de sucessão, que a frase da recusa aparece e que cada Etapa enumerada leva à
sua distribuição.

**Acceptance Scenarios**:

1. **Given** o recorte sem nenhum resultado, **When** quem emite abre a tela, **Then** ela não traz o
   formulário de emissão, traz a frase da recusa e um link para a distribuição de cada Etapa enumerada.
2. **Given** o mesmo recorte, **When** alguém sem a base de gestão abre a tela, **Then** ela traz a
   frase, sem os links e sem o pedido "peça a alguém que a emita".
3. **Given** o mesmo recorte com uma ordem vigente do acervo, **When** quem emite abre a tela, **Then**
   o bloco de sucessão também não aparece, e a frase diz por quê.
4. **Given** o recorte sem nenhum resultado, **When** um pedido chega à rota de confirmação, **Then** a
   confirmação não abre: o pedido volta à tela, com a frase da recusa.
5. **Given** um recorte com resultado parcial, **When** quem emite abre a tela e confirma, **Then** o
   formulário e a confirmação da `126` aparecem como antes.

---

### User Story 3 — A conferência do gesto põe o recorte entre os impedidos (Priority: P2)

A presidência abre a condução do marco por pontuação e escolhe "Ordenar o marco". Na conferência, o
recorte sem nenhum resultado aparece entre os **impedidos**, com a mesma frase; os recortes com
resultado continuam a praticar.

**Why this priority**: o gesto chama o mesmo comando, que já recusaria recorte a recorte; sem a
previsão, a conferência prometeria "Emitir N ordens" e a confirmação devolveria recusas.

**Independent Test**: um marco com dois recortes — um sem resultado, outro com — e a conferência do
gesto mostra o primeiro impedido, com a razão, e o segundo a praticar.

**Acceptance Scenarios**:

1. **Given** um recorte sem nenhum resultado, **When** a conferência de "Ordenar o marco" abre,
   **Then** ele aparece entre os impedidos, com a frase da recusa.
2. **Given** um recorte sem inscrição considerada, **When** a conferência abre, **Then** ele continua a
   praticar, com "ninguém concorreu — a ordem vazia é emitida e registra isso".
3. **Given** a conferência lida com resultado e um Resultado superado depois, **When** a confirmação do
   gesto pratica, **Then** o comando recusa aquele recorte e a confirmação o diz entre os não feitos.

---

### Edge Cases

- **A Etapa decisória (porta)**: o Resultado dela não tem pontuação, mas é Resultado. Um marco que
  enumera a porta e uma Etapa pontuada, com a porta consolidada e a outra não, é ordem parcial:
  emissível, e a confirmação diz quantas ficam sem resultado na Etapa pontuada (D-002).
- **Todos eliminados** numa Etapa enumerada: têm Resultado, e a ordem — todos sem posição por
  eliminação — é emissível. É um fato, e não uma ordem precoce.
- **Resultado superado** por recurso: só o vigente conta. O sucessor de um Resultado é Resultado.
- **Resultado só na Etapa de desempate não enumerada**: não conta (D-003).
- **Universo esvaziado pela progressão** (todos eliminados numa Etapa anterior, não enumerada): é
  universo vazio, e a ordem vazia é emissível, como hoje.
- **Repetição de um pedido já atendido** (mesma chave de idempotência): devolve o desfecho do primeiro,
  como hoje, ainda que a regra recusasse um pedido novo.
- **Ordem vazia do acervo**, emitida antes desta regra sem nenhum resultado: continua vigente, válida e
  legível; quando os resultados chegarem ela fica obsoleta, e a sucessão é aceita.
- **Recorte reservado** com autodeclarados e nenhum resultado: recusado como a ampla. Recorte reservado
  sem autodeclarado: universo vazio, emissível.
- **Edital sem regra vigente** (não recomputável): a tela já não oferece o formulário; nada muda.

## Requirements *(mandatory)*

### Functional Requirements

#### A regra

- **FR-4200**: A emissão da ordem de um recorte de marco por pontuação MUST ser recusada quando o
  universo considerado no recorte tem ao menos uma inscrição e **nenhuma** delas tem Resultado vigente
  em **nenhuma** Etapa que o marco enumera.
- **FR-4201**: Conta como Resultado, para esta regra, todo Resultado de Etapa **vigente** de uma Etapa
  que o marco enumera, com ou sem pontuação: o da Etapa decisória e o de eliminação por Ocorrência
  inclusive (D-001, D-002). O Resultado superado não conta.
- **FR-4202**: O Resultado de uma Etapa que o marco **não** enumera — inclusive a que um critério de
  desempate lê — MUST NOT contar (D-003).
- **FR-4203**: O universo considerado MUST ser o mesmo que o cálculo da ordem usa (recorte, progressão,
  faixa do corte), no mesmo instante. A regra MUST NOT montar um segundo universo.
- **FR-4204**: A ordem parcial — ao menos uma inscrição considerada com Resultado — MUST continuar
  emissível.
- **FR-4205**: A ordem de universo vazio MUST continuar emissível, e a condução MUST continuar a dizer
  *Feito*, "ninguém concorreu", depois dela.

#### Onde a regra vale

- **FR-4206**: A recusa MUST acontecer no comando de emissão, dentro da trava do Processo e sobre o
  cálculo que o comando grava, depois da recusa do marco por sorteio e antes da conferência da
  assinatura e do motivo da sucessão.
- **FR-4207**: A recusa MUST valer para a sucessão: havendo ordem vigente no recorte, o sucessor sem
  nenhum Resultado é recusado como o primeiro ato.
- **FR-4208**: A recusa MUST valer para o gesto "Ordenar o marco": o recorte recusado não ganha ato, e
  os outros recortes do gesto seguem, cada um na sua transação.
- **FR-4209**: A repetição de um pedido já atendido MUST continuar devolvendo o desfecho anterior.
- **FR-4210**: A recusa MUST NOT gravar ato, posição, citação de decisão, evento de trilha de emissão
  nem desfecho de idempotência aceito.
- **FR-4211**: A recusa MUST ter código próprio e uma frase em linguagem simples, sem identificador
  técnico, que diz quantas inscrições estão sem resultado, em quais Etapas, pelo nome publicado, e o
  caminho: distribuir as inscrições, avaliar e consolidar os resultados (UX-260).

#### A previsão nas telas

- **FR-4212**: A tela da ordem MUST NOT oferecer o formulário de emissão nem o de sucessão quando a
  emissão seria recusada por esta regra; no lugar dele, MUST dizer a frase da recusa (UX-261).
- **FR-4213**: Para quem tem a base de gestão da comissão, a tela MUST levar à distribuição de cada
  Etapa enumerada; para quem não tem, MUST NOT oferecer o link nem pedir que alguém emita a ordem.
- **FR-4214**: A ordem calculada e a lista dos sem posição, com o motivo, MUST continuar visíveis na
  tela: prever a recusa não esconde a prévia.
- **FR-4215**: A rota da confirmação MUST NOT abrir a confirmação quando a emissão seria recusada:
  volta à tela da ordem com a frase da recusa.
- **FR-4216**: A conferência do gesto "Ordenar o marco" MUST pôr o recorte recusado entre os
  impedidos, com a frase da recusa (UX-262), e MUST NOT contá-lo entre os que serão praticados.
- **FR-4217**: A previsão nas telas e a recusa no comando MUST sair da **mesma** regra, aplicada à
  proposta calculada; a confirmação da `126` MUST ler a mesma regra para dizer "nenhuma inscrição tem
  resultado".

#### Coerência e acervo

- **FR-4218**: A derivação do andamento da seleção (`127`) MUST NOT dizer *Pendente*, para a ordem de
  um recorte, quando esta regra a recusaria.
- **FR-4219**: As ordens já emitidas sem nenhum Resultado MUST continuar vigentes, válidas e legíveis,
  com a proveniência e a reprodução de antes. Esta feature MUST NOT criar migration, tabela, coluna,
  permissão ou estado persistido, e MUST NOT excluir nem alterar ato.
- **FR-4220**: Os testes e fixtures que emitiam ordem sem nenhum Resultado por conveniência MUST passar
  a emitir com Resultado, sem enfraquecer o que provam; cada um MUST ser nomeado, com o motivo, na
  verificação.

### Experiência

- **UX-260**: A frase da recusa, com N inscrições e a Etapa X: *"Nenhuma das N inscrições deste recorte
  tem resultado na Etapa X. Para emitir a ordem, distribua as inscrições, avalie e consolide os
  resultados dessa Etapa."* Com uma inscrição: *"A inscrição deste recorte não tem resultado…"*; com
  mais de uma Etapa: *"…nas Etapas X e Y… dessas Etapas."*
- **UX-261**: Na tela da ordem, no lugar do formulário, um bloco *"A ordem ainda não pode ser
  emitida"* com a frase e, para quem gere a comissão, um link *"Distribuir X"* por Etapa enumerada.
- **UX-262**: Na conferência do gesto, a linha do impedido é *"<recorte> — <frase>"*, como as outras
  recusas.

### Key Entities

Nenhuma entidade nova. A regra lê o que o cálculo da ordem já monta: o universo considerado do recorte
e os Resultados vigentes das Etapas enumeradas de cada inscrição.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1300**: Em **100%** dos pedidos de emissão num recorte sem nenhum Resultado nas Etapas
  enumeradas — pela tela, pela sucessão e pelo gesto —, **zero** atos são gravados e a recusa traz a
  frase com o número de inscrições e as Etapas.
- **SC-1301**: Em **100%** dos casos de ordem parcial, de universo vazio, de todos eliminados e de
  Resultado só por Ocorrência, a emissão continua aceita.
- **SC-1302**: **Zero** telas da ordem oferecem o formulário de emissão ou de sucessão num recorte que
  a regra recusa, e **zero** confirmações abrem nesse caso.
- **SC-1303**: Na conferência do gesto, **100%** dos recortes recusados aparecem entre os impedidos,
  com a razão, e nenhum é contado entre os praticáveis.
- **SC-1304**: **Zero** migrations novas; **100%** das ordens vazias já gravadas continuam legíveis e
  *Feito* (ou *Obsoleto*, quando o universo mudou) na condução.
- **SC-1305**: A suíte contra PostgreSQL fecha sem falha nova em relação à linha de base da branch da
  `126`, e cada teste ajustado está nomeado na verificação.
- **SC-1306**: **Zero** recortes que a regra recusa aparecem como *Pendente* no andamento da `127`.

## Assumptions

- **O Edital 91** do estudo não está num banco disponível: a captura de antes e depois sai de um cenário
  montado pelos helpers dos testes num banco descartável, com um marco por pontuação, uma Etapa
  enumerada e inscrições sem avaliação.
- **A `126` é mergeada antes desta**, ou junto: esta spec parte da confirmação que ela escreveu. Se
  não for, o PR desta depende do #414.
- **A `127` ainda não está na `main`**: a coerência com ela (FR-4218) é verificada por leitura da regra
  dela e, se ela for mergeada antes desta, por teste.
- **O texto das frases** é proposta e passa pela varredura de vocabulário.

## Compatibilidade com regras anteriores

| Regra | O que acontece |
|---|---|
| FR-492a da `034` e a decisão da `049` sobre a ordem vazia | continuam: o universo vazio não é afetado (FR-4205) |
| FR-1318 da `067` (marco por sorteio recusado antes do cálculo) | continua, e vem antes desta recusa (FR-4206) |
| FR-3548 da `114` (a eliminação no desempate não tira da ordem) | estendida: o Resultado do desempate também não conta para esta regra (FR-4202) |
| FR-4035 a FR-4038 da `126` (a confirmação diz quem está sem resultado) | continuam no caso parcial; o caso "nenhuma" deixa de chegar à confirmação (FR-4215, FR-4217) |
| FR-4039 da `126` (a confirmação continua permitindo a emissão) | **revista** no caso de nenhum Resultado: a emissão é recusada, pela decisão do usuário (FR-4200) |
| FR-476 da `033` (oferecer o que se vai recusar é pior do que não oferecer) | aplicada à tela da ordem (FR-4212) |
| FR-818 da `049` (a conferência do gesto diz o impedido, com a razão) | continua, com uma razão a mais (FR-4216) |

## Decisões

### D-001 — "Resultado" é o Resultado de Etapa vigente, e não a pontuação

A opção decidida fala em *resultado*, e não em *pontuação*. Pela pontuação, a Etapa decisória — que
nunca pontua — nunca contaria, e a eliminação por Ocorrência também não. O critério é o mesmo que a
`126` já usa para dizer "sem resultado" na confirmação (a Etapa presente entre as pontuações lidas, com
ou sem valor), e por isso a regra e a confirmação dizem a mesma coisa sobre o mesmo dado.

### D-002 — A Etapa decisória e a Ocorrência contam, e a ordem parcial que sai delas é aceita

Uma Ocorrência elimina e é Resultado (RC-112, `doc/decisao-rc112-portao-da-habilitacao.md`), e a
porta consolidada é Resultado. Com elas, alguém do recorte tem Resultado, e a ordem é parcial: a opção
decidida a mantém emissível, e a `126` diz na confirmação quantos ficam sem resultado na Etapa
pontuada. Recusar também esses casos seria a opção c, descartada.

### D-003 — A Etapa de desempate não enumerada não conta

A FR-3548 da `114` diz que da Etapa do desempate vem só a nota, e não a consequência: ela não decide
quem tem posição. Resultado só nela deixa todos sem posição, "sem pontuação nas Etapas enumeradas", que
é o caso que a regra existe para recusar.

### D-004 — A regra é uma função pura da proposta, chamada em três lugares

O comando, a tela e a conferência do gesto já calculam a mesma proposta. Uma função que lê a proposta
— o universo considerado e os Resultados das Etapas enumeradas — e devolve a recusa é a forma de as
três dizerem a mesma coisa, e de a confirmação da `126` usar o mesmo critério. Uma consulta à parte ao
banco seria um segundo universo, que divergiria do cálculo na primeira regra nova de progressão.

### D-005 — A recusa vem antes da assinatura

Quem tem o formulário antigo aberto, num recorte sem Resultado, mandaria uma assinatura ainda válida;
quem confirmou antes de um Resultado ser superado mandaria uma assinatura velha. Nos dois casos, a
resposta útil é a da regra — "ainda não há resultado" —, e não "a ordem mudou desde a sua leitura",
que convidaria a reler e tentar de novo.

## Decisão do usuário

### G-01 — Opção b

**Decidida em 06/11/2026** (registro na `126`, *Decisão do usuário*): recusar a emissão da ordem por
pontuação quando nenhuma inscrição considerada no recorte tem resultado em nenhuma Etapa enumerada
pelo marco. As opções c (recusar se alguma inscrição está sem resultado) e d (exigir declaração) foram
descartadas.
