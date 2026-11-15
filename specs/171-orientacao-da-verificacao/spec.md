# Feature Specification: A orientação da verificação da autodeclaração

**Feature Branch**: `claude/spec-orientacao-da-verificacao-8d618e`, nascida da `main` em `7d5c6ade`
(o merge da `166`)

**Created**: 2026-11-14

**Status**: Especificada, esclarecida (Q-1 a Q-5, decididas pelo usuário em 14/11 pelas
recomendações, com dois ajustes: o link para o Edital e a advertência de nome não pressupõem que a
Etapa restrita seja de verificação da autodeclaração, e o degrau depois do prazo diz só o que os dados
permitem afirmar), planejada (o plano estreitou a FR-7321 à Etapa restrita e a FR-7333 e a FR-7334 ao
que um cenário de período único mostra) e implementada em 14/11, no PR #551, sem merge. O merge é do
usuário.

**Numeração**: nasceu como `168`. Na mesma noite, a `main` recebeu outra `168`, a das Novidades do GPS
(#555), e esta passou a `171`, o primeiro número livre: a `167` é do agendamento e a `169` e a `170`
estão em PRs abertos. Os identificadores de requisito não mudaram.

**Input**: a **entrega 4** do plano do estudo da verificação da autodeclaração
(`doc/estudo-verificacao-da-autodeclaracao-2026-11-13/04-plano-de-entregas.md`): *"Orientação: degrau no
portal, natureza no Centro e em Minhas atividades, aviso por e-mail"*, verificada por *"percurso no
navegador nos cenários de treinamento; varredura de vocabulário"*. É o que faz cada pessoa saber que a
verificação existe e o que lhe cabe.

> **Faixa de identificadores.** Esta spec abre em **FR-7300**, **SC-2410** e **UX-790**, e reserva até o
> requisito sete mil trezentos e noventa e nove. Os tetos medidos em 14/11/2026 eram, na `main`, o
> requisito sete mil cento e cinquenta e três, o critério dois mil trezentos e setenta e sete e o
> requisito de experiência setecentos e setenta e quatro, todos da `166`. A `167`, do agendamento da
> Etapa, nos PRs #546 e #548, usa a faixa do requisito sete mil e duzentos ao sete mil duzentos e
> cinquenta e seis. A `168` da `main` (Novidades do GPS) usa a faixa do requisito sete mil e
> quatrocentos e um; a `169` e a `170`, em PRs abertos, as do sete mil e quatrocentos e do sete mil e
> quinhentos. As decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-1243 da `066`"). Uma decisão de outra feature é citada pelo assunto e pela feature. A
> `167` não está na `main` e é citada só pelo assunto. As regras do estudo (`R-1` a `R-24`) e as
> pendências (`P-0` a `P-12`) são locais a ele, e se citam por extenso.

---

## Por que esta feature existe

A camada A do estudo pôs o rito da heteroidentificação dentro do GPS: a Etapa alcança só quem declarou
a Modalidade (`163`), o desfecho desfavorável tem efeito por lista (`164`) e a comissão delibera pela
regra que o Edital escolheu, com pareceres às cegas (`165`). Nada disso diz a ninguém que a verificação
**existe**.

- **O candidato não fica sabendo.** O acompanhamento só mostra uma Etapa quando ela tem Resultado
  visível (a FR-6982 da `163` sai por construção daí). Quem se inscreveu na lista de pretos e pardos
  descobre a verificação pelo texto do Edital, por um e-mail mandado fora do sistema, ou não descobre.
  Não existe degrau de situação que diga "falta um passo seu", nem aviso por e-mail que parta de uma
  Etapa: as três origens da `066` partem de uma publicação de resultado, de uma chamada ou de uma
  pendência documental.
- **A comissão e a presidência veem a Etapa, mas não o que é próprio dela.** O Centro e Minhas
  atividades já mostram distribuir, avaliar e consolidar de qualquer Etapa, contando só as inscrições
  alcançadas (a FR-6978 da `163`). Não mostram de quem são os pareceres que faltam numa Etapa
  colegiada, quem passou do período sem parecer nem ausência registrada, se os alcançados foram
  avisados, nem — com o vídeo ligado — quem espera o encaminhamento à entrevista ao vivo. A linha do
  avaliador em Minhas atividades não traz o prazo.

A `166`, implementada antes desta entrega, pôs no acompanhamento **um cartão de acesso** ao vídeo, fora
do bloco da situação, e disse que o degrau desta entrega o substituiria (a FR-7145 da `166`). Ele só
aparece quando a Etapa admite o vídeo e a chave está ligada — isto é, nunca em produção.

### O que esta spec cobre, e o que fica fora

**Cobre:**

- o degrau **"falta um passo seu"** no acompanhamento, para a inscrição que uma Etapa restrita alcança:
  por que o passo existe, quando acontece, como se faz, o que acontece se faltar, e, depois, que a
  comissão está analisando;
- o **aviso por e-mail** aos alcançados, por uma origem nova dos avisos complementares da `066`, com o
  gesto de quem já confirma avisos;
- a Etapa restrita **no Centro de Controle e em Minhas atividades**, com o que está pendente e de quem:
  os pareceres que faltam por membro, o período vencido sem desfecho, o aviso não dado e, com o vídeo
  ligado, o encaminhamento à entrevista ao vivo;
- o prazo na linha do avaliador em Minhas atividades;
- a substituição do cartão da `166` pelo degrau;
- a varredura de vocabulário do candidato sobre tudo isso, inclusive as páginas da `166`;
- um cenário de treinamento que percorra a orientação.

**Fica fora**, como registro e não como escopo:

- o **agendamento individual** da entrevista (dia, hora e sala por pessoa): é a `167`. Quando ela
  publicar o horário de uma pessoa, o lugar dele no portal é este degrau (*Dependências*);
- o **vídeo** em si, e a habilitação dele por interface: são a `166` e a spec que a sucede;
- o **aviso do encaminhamento** à entrevista ao vivo e o do resultado do vídeo: dependem do vídeo
  sair do desenvolvimento;
- o **relato de falha técnica** e a **desistência do vídeo enviado**, que a `166` adiou por falta de
  leitor no Centro (*Achados*);
- as pendências normativas **P-0, P-7, P-8 e P-10** do estudo.

---

## Clarifications

### Session 2026-11-13 (decisões do usuário, no estudo)

- **P-1, P-2 e P-3** são a `163`, a `164` e a `165`, das quais esta parte.
- **P-0, P-7, P-8 e P-10** continuam abertas e não são desta spec.

### Session 2026-11-14 (restrições do pedido)

- Sem estrutura paralela: nenhuma área, painel, página ou fila nova. A verificação entra onde cada
  pessoa já trabalha — o acompanhamento, o Centro, Minhas atividades, a confirmação de avisos.
- Sem *overengineering*: uma experiência óbvia para o candidato e uma rotina eficiente para a comissão.
- A orientação vale para a verificação **sem vídeo**, que é o caminho real hoje. O vídeo aparece só
  onde a chave `VERIFICACAO_POR_VIDEO` está ligada, e ela continua recusada em produção.
- Na tela do candidato não se escrevem "heteroidentificação" nem "fenótipo" (tabela de linguagem do
  `02-experiencia.md` do estudo).
- Um achado fora do escopo vira registro, e não escopo.

### Session 2026-11-14 (decisões do usuário sobre o PR #551)

- **Q-1 a Q-5: adotadas as recomendações.** A Etapa existente, pelo nome publicado; o nome preservado no
  portal; o degrau só nas Etapas restritas; o aviso pelo gesto humano; o prazo na linha de avaliar de
  toda Etapa com período.
- **Ajuste 1 — toda Etapa restrita, e não só a verificação.** O link para o Edital e a advertência de
  nome não podem pressupor que a Etapa seja verificação da autodeclaração: uma perícia de pessoa com
  deficiência não aponta para "Verificação da autodeclaração". O link vai ao Edital vigente, que já
  existe no portal, e diz qual Etapa procurar (FR-7304); a advertência é contextual, sem campo novo
  (FR-7336).
- **Ajuste 2 — prazo encerrado não é análise iniciada.** Sem parecer nem Resultado, o degrau diz só que o
  período terminou e que a pessoa aguarda a comissão (FR-7306).

### Perguntas ao usuário (decididas em 14/11 pelas recomendações abaixo)

Esta spec foi escrita por uma sessão aberta por outra. As perguntas ficam com o texto original, para a
rastreabilidade; a decisão é a da sessão acima.

- **Q-1 — A "natureza verificação da autodeclaração" é uma natureza nova, ou é a Etapa que já existe,
  pelo nome que o Edital lhe deu?** O GPS não sabe que uma Etapa é de verificação: a `163` e a `164`
  recusaram de propósito um marcador semântico de "cota racial" (o código da Modalidade não tem
  significado para o sistema). Uma natureza própria exigiria esse marcador, ou adivinharia pelo nome.
  **Recomendação: a Etapa que já existe.** A orientação vale para **toda Etapa restrita** — a que
  declara alcance por Modalidade (`163`) —, e cada pessoa a lê pelo nome publicado, que no Edital do
  Ifes é "Verificação da autodeclaração". O mesmo degrau serve, sem uma linha a mais, à perícia de
  pessoa com deficiência ou à análise documental de indígenas quando o Edital as compuser como Etapa
  restrita. Alternativa descartada: um campo "natureza da Etapa" na composição, que seria dado
  normativo novo, com snapshot e mutabilidade, para dizer o que o nome já diz (D-001).
- **Q-2 — E se o Edital chamar a Etapa de "Heteroidentificação"?** O nome é do Edital, e o candidato o
  lê também no documento. **Recomendação: o portal mostra o nome publicado**, e o texto fixo do degrau
  nunca usa os termos técnicos; a composição, ao gravar uma Etapa restrita cujo nome traga um termo
  que a varredura do candidato proíbe, dá uma advertência **não impeditiva** (FR-7336; ajustada
  pela decisão de 14/11 para não sugerir um nome que pressuponha o procedimento). Alternativas descartadas: um "nome para o candidato" à parte (segundo
  campo para a mesma coisa) e recusar a publicação (o nome normativo é decisão do Edital).
- **Q-3 — O degrau "falta um passo seu" vale só para a Etapa restrita, ou para toda Etapa com
  período?** Toda Etapa com período e sem Resultado é, em tese, um passo do candidato. **Recomendação:
  só a restrita**, que é o pedido e o caso em que o candidato não sabe que o passo é dele: a Etapa
  que vale para todos o Edital já anuncia a todos. A generalização fica registrada (*Achados*).
- **Q-4 — O aviso aos alcançados sai sozinho, ou pelo gesto de alguém?** O *wireframe* do Centro no
  estudo diz "aviso automático já saiu". A FR-1243 da `066` diz o contrário: nenhum aviso existe sem o
  gesto de uma pessoa autorizada, com prévia. **Recomendação: pelo gesto**, como os outros avisos; o
  Centro mostra que falta avisar (FR-7323) e leva à confirmação. A frase do *wireframe* fica
  registrada como divergência do estudo (*Achados*).
- **Q-5 — O prazo na linha do avaliador vale para toda Etapa, ou só para a restrita?** **Recomendação:
  para toda Etapa com período.** A linha de avaliar é uma só para todas as Etapas (a FR-6864 da `160`),
  e um prazo só na restrita seria o caso especial que a restrição "sem estrutura paralela" proíbe
  (D-006).

---

## User Scenarios & Testing *(mandatory)*

Os cenários usam o **Edital 90/2026**, de desenvolvimento, com o Perfil "Técnico em Informática" e três
Modalidades: ampla concorrência, `L2` (pretos e pardos de escola pública) e `L6` (pessoa com
deficiência). A Etapa **"Verificação da autodeclaração"** é decisória, alcança só `L2` (`163`), tem
efeito *retirada da reserva* para o desfecho desfavorável e para a ausência (`164`), três avaliações
por inscrição e a regra **confirma só por unanimidade** (`165`). Ela aponta o Evento "Verificação da
autodeclaração", de 01/12 a 05/12, e **não** admite vídeo. Ana, Bruno e Carla são os membros alocados;
Rita preside. Maria e João se inscreveram em `L2`; Pedro, só na ampla. O Edital tem texto na seção
"Verificação da autodeclaração".

### User Story 1 — O candidato fica sabendo, no acompanhamento, que falta um passo dele (Priority: P1)

Maria abre o acompanhamento em 20/11. A situação diz **"Falta um passo seu"**. O porquê é de uma linha:
"Você se inscreveu na vaga para pessoas pretas e pardas de escola pública, e quem se inscreve nela passa
também por esta etapa: Verificação da autodeclaração." O que fazer: "Acontece de 01/12 a 05/12. A
comissão vai informar o dia, a hora e como participar." A consequência vem no mesmo cartão: "Se você não
participar, deixa de concorrer pela reserva de vagas e continua concorrendo pela ampla concorrência." Um
link leva ao Edital vigente, com a frase "No Edital, veja a etapa Verificação da autodeclaração". Pedro,
só na ampla, não vê nada disso.

**Why this priority**: é a lacuna principal. Sem o degrau, a camada A funciona para a comissão e é
invisível para quem ela verifica.

**Independent Test**: com o Edital 90 publicado, renderizar o acompanhamento de Maria, de João e de
Pedro antes, durante e depois do período, e conferir o degrau, as datas, a consequência e a ausência
dele para Pedro.

**Acceptance Scenarios**:

1. **Given** Maria alcançada e o período no futuro, **When** ela abre o acompanhamento, **Then** a
   situação é "Falta um passo seu", com o porquê pela Modalidade, as datas do Evento, a frase de que a
   comissão informa dia, hora e como participar, a consequência da ausência declarada pela Etapa e o
   link para o Edital vigente, que nomeia a Etapa a procurar.
2. **Given** o período em curso, **When** Maria abre o acompanhamento, **Then** o degrau diz que a
   etapa está acontecendo e até quando.
3. **Given** o período encerrado, sem parecer concluído nem Resultado sobre Maria, **When** ela abre o
   acompanhamento, **Then** a situação é "Aguardando a comissão", diz que o período terminou e que ela
   aguarda a comissão, e não diz que a análise começou nem promete data.
3a. **Given** um parecer já concluído ou um Resultado ainda não visível sobre Maria, **When** ela abre o
   acompanhamento, **Then** a situação é "Aguardando o resultado", diz que o resultado aparece no
   acompanhamento quando for publicado, e não diz o sentido de parecer algum nem promete data.
4. **Given** o Resultado da Etapa visível a Maria, **When** ela abre o acompanhamento, **Then** o degrau
   some, e o que ela lê é o que a `164` e a `165` já mostram.
5. **Given** Pedro, só na ampla, **When** ele abre o acompanhamento, **Then** nada sobre a Etapa
   aparece.
6. **Given** a Etapa com efeito *elimina* para a ausência, **When** Maria abre o acompanhamento,
   **Then** a consequência diz que ela é eliminada desta seleção se não participar.

---

### User Story 2 — O candidato recebe um aviso por e-mail, mandado pela comissão (Priority: P1)

Em 25/11, Rita vê no Centro "Avisar 2 inscrições sobre Verificação da autodeclaração". Abre a
confirmação dos avisos, escolhe o modelo, vê a prévia e confirma. Maria e João recebem um e-mail que diz
que há um passo a mais para eles nesta seleção, de 01/12 a 05/12, e que o acompanhamento explica quando
e como. O e-mail não diz em que lista eles se inscreveram.

**Why this priority**: muitos candidatos só voltam ao acompanhamento quando um e-mail os chama.

**Independent Test**: confirmar o aviso no Edital 90 com a chave dos avisos ligada, despachar, ler a
mensagem no terminal, e conferir os destinatários, o texto e a ausência da Modalidade.

**Acceptance Scenarios**:

1. **Given** a Etapa restrita publicada e alcançados sem aviso, **When** quem pode confirmar avisos abre
   a confirmação a partir do Centro, **Then** a prévia lista só as inscrições que a Etapa alcança e que
   ainda participam dela, com o texto do modelo escolhido.
2. **Given** o aviso confirmado e despachado, **When** Maria lê o e-mail, **Then** ele traz o nome da
   Etapa, o período e o caminho para o acompanhamento, e nenhuma menção à Modalidade, à reserva ou à
   lista.
3. **Given** o aviso já confirmado para Maria e João, **When** Rita tenta confirmar o primeiro aviso de
   novo, **Then** os dois aparecem como já avisados, e o reenvio segue as regras da `066`.
4. **Given** a chave dos avisos desligada, **When** Rita tenta confirmar, **Then** a confirmação é
   recusada como os outros avisos (a FR-1282 da `066`).

---

### User Story 3 — A presidência vê, no Centro, o que falta e de quem (Priority: P1)

Rita abre o Centro do Edital 90 em 04/12. A Etapa aparece pelo nome, com "alcança só L2: 2 de 30
inscrições". Abaixo, o que falta: "Faltam 4 pareceres: Bruno 2, Carla 2" e "Consolidar 1 inscrição".
Em 06/12, aparece "Registrar a ausência ou os pareceres de 1 inscrição: o período terminou em 05/12".
Em Minhas atividades, Bruno vê "Avaliar 2 inscrições · até 05/12".

**Why this priority**: é a rotina da comissão. Sem ela, a presidência descobre o atraso perguntando.

**Independent Test**: com as Atribuições e os pareceres do Edital 90 em estados variados, renderizar o
Centro para a presidência e Minhas atividades para cada membro, e conferir as contagens contra a Mesa e
a distribuição.

**Acceptance Scenarios**:

1. **Given** a Etapa colegiada com pareceres pendentes, **When** a presidência abre o Centro, **Then** a
   Etapa mostra os pareceres que faltam, com o nome de cada membro e quantos são dele, e nunca o sentido
   de parecer algum.
2. **Given** o período encerrado e uma inscrição alcançada sem parecer concluído, sem Ocorrência e sem
   Resultado, **When** a presidência abre o Centro, **Then** há uma pendência dela para registrar a
   ausência ou os pareceres, com a data do fim do período.
3. **Given** alcançados que nunca receberam o aviso da Etapa, dentro do período ou antes dele, **When**
   a presidência abre o Centro, **Then** há uma pendência "Avisar N inscrições sobre {Etapa}", que leva
   à confirmação do aviso.
4. **Given** Bruno com duas Atribuições pendentes na Etapa, **When** ele abre Minhas atividades,
   **Then** a linha diz quantas são e até quando vai o período da Etapa.
5. **Given** um membro sem Atribuição pendente, **When** ele abre Minhas atividades, **Then** nada da
   Etapa aparece para ele.
6. **Given** qualquer tela desta história, **When** os números são comparados com a Mesa e a
   distribuição, **Then** coincidem.

---

### User Story 4 — Com o vídeo ligado, o degrau absorve o cartão da `166` (Priority: P2)

Só em desenvolvimento, com `VERIFICACAO_POR_VIDEO` ligada e a Etapa admitindo o vídeo. Maria vê "Falta
um passo seu" com as duas formas, "Gravar um vídeo curto" e "Prefiro entrevista ao vivo", com o mesmo
peso e a frase "as duas formas valem igual". Depois do envio, a situação vira "Aguardando o resultado", com o
comprovante. Se a comissão encaminhar, volta a "Falta um passo seu": "A comissão quer conversar com você
ao vivo. Isso não é reprovação." O cartão separado da `166` não existe mais. No Centro, Rita vê
"Encaminhar 1 inscrição à entrevista ao vivo".

**Why this priority**: o vídeo é só de desenvolvimento; a orientação dele tem de existir para que o
cartão provisório saia, mas não é o caminho real hoje.

**Independent Test**: com a chave ligada e a desligada, renderizar o acompanhamento nos estados do vídeo
da `166` e o Centro com uma inscrição a encaminhar.

**Acceptance Scenarios**:

1. **Given** a chave ligada, a Etapa que admite o vídeo e Maria no período, **When** ela abre o
   acompanhamento, **Then** o degrau oferece as duas formas com o mesmo peso, e leva à página da
   `166`.
2. **Given** o vídeo recebido ou em análise, **When** Maria abre o acompanhamento, **Then** a situação é
   "Aguardando o resultado", com o estado do vídeo dito pela `166` e o acesso ao comprovante.
3. **Given** Maria encaminhada à entrevista ao vivo, **When** ela abre o acompanhamento, **Then** a
   situação é "Falta um passo seu", com a frase da FR-7144 da `166`.
4. **Given** a chave desligada, **When** qualquer candidato abre o acompanhamento, **Then** nenhuma
   palavra sobre vídeo aparece, e o degrau é o da camada A.
5. **Given** a chave ligada e inscrições que o vídeo não confirmou, **When** a presidência abre o
   Centro, **Then** há "Encaminhar N inscrições à entrevista ao vivo", que leva à conferência da
   consolidação.
6. **Given** qualquer estado, **When** o acompanhamento é renderizado, **Then** o cartão separado da
   `166` não aparece.

---

### User Story 5 — A equipe percorre a orientação num cenário de treinamento (Priority: P3)

A equipe carrega um cenário de treinamento com uma Etapa restrita e colegiada, alcançados em estados
diferentes — sem avaliador, com parecer pendente, com os pareceres completos, ninguém ainda
avisado — e percorre, no navegador, o acompanhamento de um candidato, o Centro da presidência e Minhas
atividades de um membro.

**Why this priority**: é como o plano do estudo verifica a entrega, e é como a equipe aprende a rotina
antes de um Edital real.

**Independent Test**: carregar o cenário e percorrer as três telas; o teste do cenário confere os
estados.

**Acceptance Scenarios**:

1. **Given** o cenário carregado, **When** a equipe entra como o candidato alcançado, **Then** vê o
   degrau "Falta um passo seu".
2. **Given** o cenário carregado, **When** a equipe entra como a presidência, **Then** o Centro mostra
   as pendências desta spec com os números do cenário.
3. **Given** o cenário carregado, **When** o teste do cenário roda, **Then** ele confere os estados que
   o cenário promete.

---

### Edge Cases

Cada caso-limite é requisito: a linha cita o requisito que o resolve.

- **A Etapa restrita sem Evento no cronograma**: o degrau diz que a comissão informará quando e como, e
  não inventa data (FR-7305).
- **O Evento retificado** depois do aviso: o degrau lê sempre o período vigente; o aviso já mandado não
  muda, e o reenvio justificado da `066` é o caminho para avisar de novo (FR-7305, FR-7319).
- **Duas Etapas restritas alcançam a mesma inscrição** (`L2` e `L6` no mesmo Perfil, por exemplo): o
  degrau mostra a de período mais próximo ainda sem Resultado visível, e cita a outra numa linha do
  porquê (FR-7309).
- **Inscrição convocada com o passo ainda pendente** (Etapa depois da chamada): a convocação continua a
  situação, porque tem prazo próprio; o passo pendente entra como linha do porquê, com as datas
  (FR-7303).
- **Inscrição eliminada antes, ou não aceita na análise das inscrições**: o degrau de eliminação ou de
  não aceitação prevalece, e o passo não aparece (FR-7303).
- **Inscrição que deixou de participar da Etapa** (a progressão a tirou antes dela): o degrau não
  aparece, e o aviso não a inclui (FR-7302, FR-7318).
- **Resultado deliberado mas ainda não visível ao titular** (a visibilidade da Etapa restrita espera a
  publicação de um marco, pela `164`): o degrau fica em "Aguardando o resultado", sem data (FR-7306).
- **Etapa restrita depois da última Etapa que o marco enumera** (achado da `164`): o Resultado pode
  nunca ficar visível pelo marco, e o degrau não sai de "Aguardando o resultado" por conta própria. O caso é
  registrado, e não resolvido aqui (*Achados*); a spec só garante que o degrau não mente (FR-7306).
- **A Ocorrência de ausência registrada**: é Resultado, e segue a visibilidade dele; até ficar visível,
  o titular vê "Aguardando o resultado" (FR-7306).
- **Recurso contra o Resultado da Etapa**: o degrau já saiu quando o Resultado ficou visível; o recurso
  segue a `018` e a `165`, sem nada desta spec (FR-7307).
- **O aviso confirmado e a inscrição que deixa de participar antes do despacho**: o despacho segue as
  elegibilidades da `066`, e a inscrição sem participação é não elegível (FR-7318).
- **O aviso depois do fim do período**: a pendência de avisar some quando o período termina; avisar
  depois continua possível pela confirmação, mas o Centro não o cobra (FR-7323).
- **Nenhuma inscrição alcançada**: a Etapa aparece no Centro como "nenhuma inscrição alcançada" (a
  FR-6977 da `163`), e nenhuma pendência desta spec existe (FR-7322).
- **Membro exposto aos pareceres alheios** (`165`): a contagem por membro continua a contar as
  Atribuições dele; a redistribuição é da presidência, como hoje (FR-7321).
- **A presidência que também é membro**: vê no Centro a contagem de todos, e em Minhas atividades a
  linha de avaliar só com as dela (FR-7321, FR-7326).
- **Etapa restrita não colegiada** (uma avaliação por inscrição): a contagem por membro também vale;
  não há nada de colegiado nela (FR-7321).
- **O nome da Etapa com termo técnico**: o portal mostra o nome publicado; a composição advertiu antes
  (FR-7336).
- **O candidato sem e-mail válido**: segue as elegibilidades e falhas da `066`; o degrau no
  acompanhamento é o canal que não depende do e-mail (FR-7300, FR-7318).
- **Chave do vídeo desligada depois de vídeos recebidos** (só em desenvolvimento): o portal volta ao
  degrau da camada A para quem não enviou; para quem enviou, "Aguardando o resultado", sem acesso à gravação; a
  Mesa e o encaminhamento continuam, como a `166` decidiu (FR-7313, FR-7325).
- **O acompanhamento de quem nenhuma Etapa restrita alcança**: não custa consulta a mais (FR-7311).

## Requirements *(mandatory)*

### Functional Requirements

#### O degrau no acompanhamento (candidato)

- **FR-7300**: O acompanhamento DEVE mostrar à inscrição alcançada por uma Etapa restrita (a que declara
  alcance por Modalidade, `163`) um degrau de situação próprio, enquanto o Resultado dela naquela Etapa
  não estiver visível ao titular. O degrau tem três rótulos: **"Falta um passo seu"**, **"Aguardando a
  comissão"** e **"Aguardando o resultado"** (FR-7306).
- **FR-7301**: O degrau NÃO DEVE aparecer para a inscrição que a Etapa não alcança, nem para inscrição
  não enviada.
- **FR-7302**: O degrau NÃO DEVE aparecer para a inscrição que deixou de participar da Etapa pela
  progressão das Etapas anteriores.
- **FR-7303**: O degrau DEVE vir abaixo, em precedência, dos desfechos, da convocação, da não aceitação
  na análise das inscrições e da eliminação, e acima de todos os degraus que hoje vêm depois da
  eliminação. Na inscrição convocada com o passo pendente, a convocação continua a situação, e o passo
  DEVE entrar como linha do porquê, com o nome da Etapa e as datas.
- **FR-7304**: "Falta um passo seu" DEVE dizer:
  - por quê, numa linha: a Modalidade em que a pessoa se inscreveu, pelo nome publicado, e que quem se
    inscreve nela passa também pela Etapa, pelo nome publicado;
  - quando: o início e o fim do período da Etapa, ou, durante ele, que está acontecendo e até quando;
  - como: que a comissão vai informar o dia, a hora e como participar;
  - a consequência da ausência, pelo efeito que a Etapa declara (`164`): deixar de concorrer pela
    reserva e continuar na ampla, ou ser eliminado desta seleção;
  - o link para o Edital vigente, pela página da seleção que o portal já tem, com a frase "No Edital,
    veja a etapa {nome publicado}". O link NÃO DEVE apontar para uma seção textual do documento: o
    catálogo de seções não diz qual seção trata de qual Etapa, e uma perícia de pessoa com deficiência
    não pode cair em "Verificação da autodeclaração".
- **FR-7305**: O período DEVE ser lido do Evento que a Etapa aponta, na versão vigente do Edital. Sem
  Evento, ou sem início e fim, o degrau DEVE dizer que a comissão vai informar quando e como, sem data.
- **FR-7306**: Enquanto o Resultado não é visível ao titular, o degrau DEVE dizer só o que os dados
  permitem afirmar:
  - **"Aguardando a comissão"**, quando o período terminou e não há parecer concluído nem Resultado sobre
    a inscrição naquela Etapa: o período terminou em {data} e a pessoa aguarda a comissão. NÃO DEVE dizer
    que a análise começou;
  - **"Aguardando o resultado"**, quando há parecer concluído ou Resultado sobre a inscrição naquela
    Etapa: o resultado aparece no acompanhamento quando for publicado.

  Nenhum dos dois DEVE prometer data nem dizer o sentido de parecer algum, nem se o Resultado é de
  desfecho ou de ausência.
- **FR-7307**: Visível o Resultado, o degrau DEVE sumir; o que o titular lê da Etapa é o que a `164` e a
  `165` já mostram, sem mudança.
- **FR-7308**: O degrau NÃO DEVE criar estado guardado: é derivado do alcance, da participação, do
  período, dos pareceres concluídos, do Resultado e da visibilidade dele, que já existem.
- **FR-7309**: Quando mais de uma Etapa restrita alcança a mesma inscrição sem Resultado visível, o
  degrau DEVE tratar a de período mais próximo (a sem período por último), e citar cada outra numa linha
  do porquê, com nome e datas.
- **FR-7310**: Quando o agendamento individual da Etapa existir para a inscrição (`167`), o degrau é o
  lugar dele; esta spec NÃO DEVE antecipá-lo nem simular um horário.
- **FR-7311**: O acompanhamento de uma inscrição que nenhuma Etapa restrita do Edital alcança NÃO DEVE
  custar consulta a mais ao banco.

#### O vídeo no degrau, só com a chave ligada

- **FR-7312**: Com `VERIFICACAO_POR_VIDEO` ligada e a Etapa admitindo o vídeo, o degrau DEVE absorver os
  estados da `166`:
  - podendo gravar: "Falta um passo seu", com "Gravar um vídeo curto" e "Prefiro entrevista ao vivo"
    com o mesmo peso, a frase "as duas formas valem igual" e o fim do prazo do envio, levando à página
    da `166`;
  - vídeo recebido ou em análise: "Aguardando o resultado", com a frase da `166` para o estado (recebido
    e ainda não aberto, ou em análise pela comissão, que é fato registrado) e o acesso ao comprovante;
  - encaminhada à entrevista ao vivo: "Falta um passo seu", com a frase da FR-7144 da `166`;
  - entrevista ao vivo sem vídeo: o degrau da camada A.
- **FR-7313**: Com a chave desligada, o degrau NÃO DEVE conter palavra sobre vídeo, e DEVE ser o da
  camada A, inclusive na Etapa que admite o vídeo. Quem já enviou vídeo, nesse caso, lê "Aguardando o resultado",
  sem a palavra vídeo.
- **FR-7314**: O cartão de acesso da `166` no acompanhamento (a FR-7145 da `166`) DEVE deixar de
  existir: o acesso à gravação e ao comprovante passa a ser do degrau. As páginas da gravação e do
  comprovante da `166` NÃO mudam.

#### O aviso por e-mail

- **FR-7315**: Os avisos complementares (`066`) DEVEM ganhar uma origem: o **aviso do passo**, que parte
  de uma Etapa restrita publicada, e não de uma publicação de resultado nem de uma chamada.
- **FR-7316**: O aviso do passo DEVE existir só pelo gesto de quem pode confirmar o aviso de resultado na
  `066` (quem tem a permissão de enviar avisos, ou a presidência ativa da comissão), com a prévia antes
  da confirmação, como a FR-1243 e a FR-1259 da `066` exigem. Nada o dispara sozinho.
- **FR-7317**: A chave `AVISOS_AOS_CANDIDATOS` DEVE valer para o aviso do passo como vale para os outros
  (a FR-1282 da `066`).
- **FR-7318**: O universo do aviso do passo DEVE ser as inscrições que a Etapa alcança e que dela ainda
  participam, sem Resultado naquela Etapa. As elegibilidades, os motivos (primeiro aviso, reenvio de
  falhas, reenvio justificado) e o despacho DEVEM ser os da `066`.
- **FR-7319**: O texto do aviso do passo NÃO DEVE mencionar a Modalidade, a reserva, a lista nem o motivo
  do passo: o e-mail pode ser lido por outra pessoa, e a autodeclaração é dado sensível. Ele DEVE trazer
  o nome da Etapa, o período quando houver, e o caminho para o acompanhamento, onde o titular lê o resto
  depois de entrar.
- **FR-7320**: Cada unidade DEVE ter um modelo inicial do aviso do passo, criado uma vez pelo mesmo
  comando que cria os modelos iniciais da `066`, **inclusive na unidade que já tem os três de hoje**. O
  modelo é editável e inativável como os outros, e o comando NÃO DEVE recriá-lo depois. O assunto do
  modelo inicial DEVE ser o assunto neutro da `066`, que a varredura dos modelos iniciais já confere
  ("cota", "reserva", "modalidade", "lista" e "heteroidentificação" fora dele), e a mesma conferência
  DEVE passar a valer para o **corpo** do modelo inicial do aviso do passo (FR-7319).

#### O Centro de Controle e Minhas atividades (comissão e operação)

- **FR-7321**: Na Etapa restrita, colegiada ou não, o Centro DEVE mostrar à presidência os pareceres que faltam,
  por membro alocado: o nome e quantas Atribuições ativas dele estão sem parecer concluído naquela Etapa.
  NUNCA o sentido de parecer algum, nem de quem são os pareceres já concluídos de uma inscrição.
- **FR-7322**: Na Etapa restrita, a Etapa DEVE aparecer no Centro pelo nome publicado, com a frase do
  alcance já usada na distribuição ("N inscrições alcançadas, de M: a Etapa só se aplica a algumas
  Modalidades"), e nenhuma pendência desta spec
  DEVE existir quando nenhuma inscrição é alcançada.
- **FR-7323**: Na Etapa restrita publicada, enquanto o período não termina e há inscrições do universo
  da FR-7318 que nunca receberam o aviso do passo confirmado, o Centro DEVE mostrar a pendência "Avisar N
  inscrições sobre {Etapa}", de quem pode confirmar o aviso, levando à confirmação dele. Terminado o
  período, a pendência DEVE sumir.
- **FR-7324**: Terminado o período da Etapa restrita, as inscrições que dela participam sem parecer
  concluído, sem Ocorrência e sem Resultado DEVEM aparecer como pendência da presidência: "Registrar a
  ausência ou os pareceres de N inscrições", com a data do fim do período, levando à distribuição da
  Etapa.
- **FR-7325**: Com `VERIFICACAO_POR_VIDEO` ligada, as inscrições que a deliberação pelo vídeo não
  confirmou e que não foram encaminhadas DEVEM aparecer como pendência da presidência: "Encaminhar N
  inscrições à entrevista ao vivo", levando à conferência da consolidação (a FR-7138 da `166`), sem a
  contagem dos sentidos. A pendência DEVE aparecer também com a chave desligada, enquanto houver
  inscrição a encaminhar: a chave fecha o portal, e não a Mesa (achado da `166`).
- **FR-7326**: Em Minhas atividades, a linha de avaliar de toda Etapa com período DEVE trazer o fim do
  período ("até dd/mm"), lido como na FR-7305. A contagem continua a da carga da Mesa (a FR-6864 da
  `160`).
- **FR-7327**: As pendências da presidência desta spec DEVEM aparecer em Minhas atividades pela regra
  que já leva as pendências de quem conduz à página pessoal (`160`), sem regra própria.
- **FR-7328**: Toda contagem desta spec DEVE coincidir com a da Mesa e da distribuição da mesma Etapa,
  no mesmo instante.
- **FR-7329**: A orientação da gestão NÃO DEVE criar área, página, painel nem fila: entra como
  pendências da Etapa no Centro e em Minhas atividades, e as ações levam às telas que já existem
  (distribuição, Mesa, conferência da consolidação, confirmação de avisos).

#### Vocabulário

- **FR-7330**: Nenhum texto fixo das telas e do aviso do candidato desta spec, nem das páginas da
  `166`, DEVE conter "heteroidentificação", "fenótipo", "fenotípic", "aferição" ou "indeferid". O que
  vem de dado publicado — o nome da Etapa, o da Modalidade e os rótulos do desfecho — não é texto fixo,
  e segue a Q-2 e a `165`.
- **FR-7331**: A varredura de vocabulário do candidato DEVE alcançar o degrau em todos os seus estados,
  com e sem a chave do vídeo, e as páginas da gravação e do comprovante da `166`, que hoje não estão em
  lista nenhuma. A lista é literal: toda tela nova do candidato desta spec DEVE entrar nela no mesmo
  commit.
- **FR-7332**: A varredura DEVE conferir o texto renderizado com uma Etapa cujo nome não traga termo
  proibido, para que o nome publicado (Q-2) não mascare nem dispare a regra.

#### Cenário de treinamento

- **FR-7333**: O catálogo de cenários de treinamento (`134`) DEVE ganhar um cenário com uma Etapa
  restrita e colegiada, sem vídeo, com o período em curso, e alcançados nos estados que um período só
  permite: sem avaliador, com parecer pendente, com um parecer de dois e com os pareceres completos
  à espera da consolidação, todos ainda não avisados, e um inscrito só na ampla. O avisado, o
  período vencido e o Resultado visível ficam na suíte, e não no cenário: o aviso do passo é um
  gesto sobre todos os que participam, e é ele o exercício da presidência.
- **FR-7334**: Um teste do cenário, no molde dos testes que já conferem os cenários no Centro, DEVE
  conferir os estados que ele promete. O comando de verificação dos cenários não ganha conferência de
  domínio.
- **FR-7335**: O cenário DEVE obedecer às regras dos cenários: nada se exclui, os atores de treino ficam
  fora das sugestões da página de acesso, e o gerador não concede papel além da exceção já registrada.

#### Advertência na composição

- **FR-7336**: Ao gravar uma Etapa restrita cujo nome traga termo que a FR-7330 proíbe ao candidato, a
  composição DEVE dar uma advertência **não impeditiva** e contextual: nomeia o termo encontrado e diz que
  o candidato lê o nome da Etapa no acompanhamento. Ela NÃO DEVE sugerir um nome que pressuponha o
  procedimento (uma perícia de pessoa com deficiência não se chama "Verificação da autodeclaração"), e
  NÃO DEVE exigir campo novo. A publicação NÃO DEVE ser recusada por isso.

### Requisitos de experiência

- **UX-790**: A linguagem do candidato é a da tabela do estudo: "verificação da autodeclaração" quando
  o texto fixo nomeia o procedimento, "não confirmada", "a comissão quer conversar com você", "enviar",
  "assistir". O texto fixo do degrau prefere o nome publicado da Etapa a nomear o procedimento.
- **UX-791**: O porquê do degrau tem uma linha, e explica pela escolha do próprio candidato ("você se
  inscreveu em …"), e não pela norma.
- **UX-792**: No celular, o degrau segue o acompanhamento: coluna única, e o link para o Edital e o
  acesso ao vídeo, quando houver, com largura cheia, sem rolagem lateral a 375 px.
- **UX-793**: No Centro, a pendência diz o que falta e de quem em uma linha ("Faltam 4 pareceres: Bruno
  2, Carla 2"), na ordem decrescente da contagem, e o nome do membro não é link para nada que exponha o
  parecer.
- **UX-794**: A consequência da ausência vem no mesmo cartão do passo, e não escondida num link.

### Key Entities

- **Degrau do passo**: leitura derivada, por inscrição e Etapa restrita — rótulo, porquê, período,
  consequência, link para o Edital vigente e, com o vídeo, o estado da `166`. Não é guardado.
- **Aviso do passo**: um aviso complementar da `066`, com a Etapa como origem no lugar da publicação.
  Imutável como os outros.
- **Modelo do aviso do passo**: um modelo de aviso da unidade, como os da `066`, com a origem nova.
- **Pendências da Etapa restrita**: os pareceres que faltam por membro, o aviso não dado, o período
  vencido sem desfecho e o encaminhamento pendente. Derivadas; não são guardadas.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2410**: No cenário de treinamento, 100% das inscrições alcançadas e sem Resultado visível veem o
  degrau, e 0% das não alcançadas o veem.
- **SC-2411**: Em todos os estados do degrau, com e sem a chave do vídeo, e nas páginas da `166`, o
  texto renderizado tem zero ocorrências dos termos da FR-7330.
- **SC-2412**: O e-mail do aviso do passo, para todo modelo inicial e para o cenário, tem zero menções à
  Modalidade, à reserva ou à lista.
- **SC-2413**: A soma dos pareceres que faltam por membro, no Centro, é igual ao número de pendências da
  Mesa da mesma Etapa em 100% dos casos da suíte.
- **SC-2414**: O acompanhamento de uma inscrição que nenhuma Etapa restrita alcança faz o mesmo número de
  consultas que antes desta spec.
- **SC-2415**: Com a chave do vídeo desligada, o acompanhamento não contém a palavra "vídeo" em nenhum
  estado do degrau.
- **SC-2416**: Uma pessoa da equipe, no cenário de treinamento, chega do Centro à confirmação do aviso
  do passo e do acompanhamento do candidato ao link do Edital sem ajuda, em menos de dois minutos cada.
  *(Humano; fora da suíte.)*

## Assumptions

- A `163`, a `164`, a `165` e a `166` estão na `main` (14/11) e não mudam antes da implementação desta.
- O GPS continua sem marcador semântico de "cota racial" (decisão da `163`); a orientação vale para toda
  Etapa restrita (Q-1).
- A visibilidade do Resultado da Etapa restrita ao titular é a da `164`: depende da publicação de um
  marco cuja última Etapa enumerada vem depois dela. Esta spec a lê, e não a muda.
- O aviso de resultado já existente (`066`, origem resultado) é o canal do desfecho: os modelos iniciais
  não dizem situação, e por isso servem à retirada da reserva sem mudança.
- O aviso de hoje cita uma publicação; a origem nova cita a Etapa. Isso muda a forma do aviso guardado,
  sem modelo de dados novo (o detalhe é do plano).
- A entrevista da camada A acontece fora do GPS, presencial ou por videoconferência, e a comissão marca
  e informa por fora até a `167` existir.

## Out of Scope

- O agendamento individual da entrevista (`167`).
- O vídeo e a habilitação dele por interface; o aviso do encaminhamento e o do resultado do vídeo.
- O relato de falha técnica e a desistência do vídeo enviado (`166`).
- O degrau para Etapas que não são restritas (Q-3).
- As pendências P-0, P-7, P-8 e P-10 do estudo.
- Qualquer mudança no Resultado, na deliberação, no recurso ou na visibilidade da Etapa.

## Dependências

- **`163`, `164`, `165` e `166`**, na `main` (#542, #543, #545, #547).
- **A `166`**: o cartão de acesso dela sai (FR-7314); os estados do vídeo são os dela.
- **A `167`** (#546, #548, sem merge): quando o agendamento existir, o horário individual entra neste
  degrau (FR-7310). Nenhuma das duas bloqueia a outra.
- **A `066`**: a origem nova segue as regras de confirmação, prévia, elegibilidade e despacho dela.
- **A `134`**: o cenário novo entra no catálogo dela.

## Achados (registro, e não escopo)

- **A-1 — O cartão provisório da `166`** promete ao candidato que "a comissão vai informar a data, a
  hora e como entrar", e não há, no GPS, canal para isso antes da `167`. Esta spec mantém a promessa
  (é verdadeira: a comissão informa por fora) e a põe no degrau.
- **A-2 — Dois leitores do período da Etapa.** A Mesa lê o Evento vigente por um leitor da comissão; a
  `166` criou outro, que lê do conteúdo que a tela já tem. O degrau e a linha do avaliador precisam de
  um só, e o plano desta spec escolhe; o da `166` é o caso de algo que esta entrega teria criado de
  forma geral.
- **A-3 — As páginas da `166` fora da varredura.** Nenhuma lista literal de vocabulário inclui as
  páginas da gravação e do comprovante. Esta spec as inclui (FR-7331), porque a varredura do candidato
  é do escopo dela.
- **A-4 — O relato de falha técnica e a desistência do vídeo** foram adiados pela `166` por falta de
  leitor no Centro. Com esta spec, o lugar do leitor existe (as pendências da Etapa), mas os dois
  continuam fora.
- **A-5 — "Aviso automático já saiu"**, no *wireframe* do Centro do estudo, contraria a FR-1243 da
  `066` (Q-4).
- **A-6 — A Etapa restrita depois da última Etapa que o marco enumera** (achado da `164`) deixaria o
  degrau em "Aguardando o resultado" para sempre, porque o Resultado nunca ficaria visível. A spec não resolve; só
  garante que o degrau não diz nada falso.
- **A-7 — O degrau para toda Etapa com período** (Q-3): a mesma leitura serviria a qualquer Etapa que
  peça a presença do candidato. Fica para decisão do usuário.
- **A-8 — A linha de avaliar não tinha prazo** em Etapa nenhuma. Esta spec o põe em todas (Q-5, D-006).
- **A-9 — A matriz por lista do Centro e a Etapa restrita** (visto no navegador, no C18, em 14/11): a
  linha da ampla concorrência mostra a Etapa restrita com o estado do Perfil inteiro ("Pendente ·
  0 de 4 consolidadas"), embora a Etapa não alcance ninguém daquela lista. A célula é da `127` e da
  `163`, e esta spec não a muda.
- **A-10 — A nota de uma providência não aparece em "Com outros papéis"** (visto no navegador): o
  Centro mostra ali só o ato. Por isso os pareceres que faltam por membro entraram no texto do ato, e
  não na nota.

## Decisões

### D-001 — A orientação vale para toda Etapa restrita, pelo nome publicado

Sem marcador semântico novo (Q-1). A Etapa restrita é a que declara alcance (`163`); "verificação da
autodeclaração" é o nome que o Edital dá a ela (FR-7300, FR-7322).

### D-002 — O degrau é derivado, e tem três rótulos

"Falta um passo seu" enquanto há algo do candidato a fazer ou a esperar no período; "Aguardando a
comissão" quando o período terminou sem registro nenhum; "Aguardando o resultado" quando há parecer ou
Resultado ainda não visível. Prazo encerrado não é análise iniciada (decisão do usuário de 14/11).
Nenhum estado guardado (FR-7300, FR-7306, FR-7308).

### D-003 — O degrau fica abaixo da eliminação e da convocação

A eliminação e o desfecho encerram o caminho; a convocação tem prazo próprio e consequência mais grave,
e o passo vira linha do porquê nela (FR-7303).

### D-004 — Uma origem nova nos avisos, pelo gesto, sem a Modalidade no texto

Pelo gesto (Q-4, FR-7316); sem a Modalidade, porque a autodeclaração é dado sensível e o e-mail é canal
sem autenticação (FR-7319). O resultado continua pela origem que já existe.

### D-005 — As pendências da gestão são da Etapa, e não de uma natureza nova

Os pareceres que faltam por membro, o aviso não dado, o período vencido e o encaminhamento entram como
pendências da Etapa, nas telas que já existem (FR-7321 a FR-7329).

### D-006 — O prazo da linha de avaliar vale para toda Etapa

Uma linha só para todas as Etapas (Q-5, FR-7326).

### D-007 — O degrau absorve o cartão da `166`

Uma situação só no acompanhamento; o cartão de acesso separado sai (FR-7312, FR-7314).
