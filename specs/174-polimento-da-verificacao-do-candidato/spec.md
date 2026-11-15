# Feature Specification: O polimento das telas do candidato na verificação por vídeo

**Feature Branch**: `claude/174-polimento-da-verificacao-do-candidato`, nascida da `main` em
`499491be` (o merge da spec da `172`, #563)

**Created**: 2026-11-15

**Status**: Especificada em 15/11; as quatro perguntas (Q-1 a Q-4) foram decididas pelo usuário no
mesmo dia, pelas recomendações. Planejada e com tarefas em 15/11, sem código. O merge é do usuário.

**Input**: em 15/11 o usuário gravou um vídeo real pela página da `166`, no Safari do macOS, num
ambiente local, e julgou a interface do candidato *"com cara de desenvolvimento, não de produção"*.
Pediu o polimento completo das telas do candidato, pensando no perfil amplo de quem se inscreve e no
celular. Os nove problemas que ele viu estão em *Por que esta feature existe*.

> **Faixa de identificadores.** Esta spec abre em **FR-7850**, **SC-2650** e **UX-870**, e reserva até
> o requisito sete mil oitocentos e noventa e nove, o critério dois mil seiscentos e sessenta e nove e
> o requisito de experiência oitocentos e oitenta e nove. Os tetos medidos em 15/11/2026, na `main` e
> nos PRs abertos (#564 e #565, ambos do design system), eram o requisito sete mil setecentos e quarenta
> e um, o critério dois mil seiscentos e nove e o requisito de experiência oitocentos e cinquenta e
> cinco, todos da `172`. A faixa entre o sete mil setecentos e cinquenta e o sete mil oitocentos e
> quarenta e nove fica livre para a spec da migração do design system, que tomou a pasta `173` na
> branch do #565. As decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-7112 da `166`"). Uma decisão de outra feature é citada pelo assunto e pela feature.
> As regras do estudo da verificação (`R-1` a `R-24`) e as pendências (`P-0` a `P-12`) são locais a
> ele, em `doc/estudo-verificacao-da-autodeclaracao-2026-11-13/`, e se citam por extenso. Os itens do
> estudo de design system (`P2.3`, as composições, os componentes) são do
> `doc/auditoria-design-system-2026-11-14/`.

---

## Por que esta feature existe

A `166` pôs a gravação do vídeo na página do GPS e a `171` pôs o passo no acompanhamento. As duas
resolveram o que o candidato **pode** fazer e o que a comissão recebe. Nenhuma das duas foi vista
num celular, e a única gravação real, a do usuário em 15/11, mostrou que a forma não acompanha o
conteúdo. O que ele viu:

1. **No computador, uma coluna estreita à esquerda.** As telas param em 68 caracteres de largura,
   encostadas na margem, e a metade direita da janela fica vazia. É o desenho de uma tela de
   desenvolvimento.
2. **"Falta um passo seu" numa caixa tracejada**, que parece marcador de depuração. O prazo fica no
   meio de um parágrafo, e o botão "Ver como funciona" não diz para onde leva.
3. **A escolha são dois botões iguais** que não dizem o que cada forma é: quanto tempo leva, se é de
   casa, se a data é marcada pela comissão.
4. **"Antes de gravar" é uma parede de seis itens**, e o erro "Escolha uma das duas respostas" aparece
   em vermelho antes de qualquer tentativa. É defeito: a regra de exibição da recusa vence o atributo
   que a esconde (A-2).
5. **O teste da câmera pede dois cliques** ("Abrir a câmera", depois "Ir para a gravação"), o oval é
   fixo e não acompanha o rosto, e o medidor de som é minúsculo.
6. **Na gravação, a instrução fica abaixo do vídeo.** A pessoa precisa olhar a câmera e ler embaixo,
   o roteiro inteiro repete a instrução atual, e avançar exige clicar "Próximo passo" enquanto vira o
   rosto. O usuário quer instruções sobre o vídeo, com o progresso ("1 de 4"), como nos aplicativos
   de banco.
7. **O comprovante põe o número do envio e o resumo SHA-256 em destaque**, para um público leigo. O
   centro deveria ser a confirmação de que deu certo.
8. **A página do vídeo tem texto fixo** ("Verificação da autodeclaração", "vaga para pessoas pretas e
   pardas") em vez do nome publicado da Etapa e da Modalidade, o que contraria a regra da `171`
   (UX-790 da `171`).
9. **O celular não foi pensado como primeiro aparelho.** Câmera frontal em retrato, o vídeo ocupando
   a tela, os botões ao alcance do polegar e a tela que não apaga durante a gravação. Ninguém testou
   isso num celular ainda — e a tela que apaga **descarta a tomada** (a FR-7115 da `166`).

O público é amplo: gente que nunca gravou um vídeo para um órgão público, que tem só o celular, que
lê pouco, que usa leitor de tela ou se comunica em Libras. A página é a única do sistema que pede
câmera, e a primeira impressão dela decide se a pessoa confia o rosto ao GPS.

### O que esta spec cobre, e o que fica fora

| Cobre | Fica fora, e por quê |
|---|---|
| O bloco "Sua situação" do acompanhamento quando há passo da Etapa restrita (`171`) | o resto do acompanhamento, que é da `P2.3` do estudo de design system |
| As telas da `166` no portal: escolha, entrevista ao vivo, "Antes de gravar", menor de idade, câmera, permissão, "não consigo", gravação, revisão, envio | a Mesa e todas as telas da gestão |
| O comprovante e o "assistir ao vídeo" do titular | o conteúdo dos estados do vídeo, que é da `166` |
| A página da situação quando não se pode gravar (análise iniciada, encaminhada, fora do período) | qualquer estado novo |
| O pedido de tela acesa durante a câmera e a gravação | qualquer permissão nova do navegador além dela |
| As capturas antes e depois e a verificação em aparelhos reais | um teste formal de usabilidade |
| O registro da detecção automática do giro do rosto (A-1) | a própria detecção: processamento biométrico no aparelho, que pede spec própria |

**Nada muda no que é gravado e enviado** (FR-7887): o roteiro e a versão dele, as marcas, o formato,
o teto, o envio em partes, a retomada, o resumo, as rotas e as respostas. A regra de que o vídeo só
confirma (R-11 do estudo) não é tocada. Tudo continua atrás da chave `VERIFICACAO_POR_VIDEO`, ou do
nome que a `169` lhe der quando for implementada.

---

## Clarifications

### Session 2026-11-15 (restrições do pedido)

- O polimento é **completo**: as nove queixas, todas as telas do candidato da verificação.
- **Celular primeiro.** O celular é o aparelho de referência; o computador é a adaptação.
- **Alinhar com a `172`** e com a auditoria de design system: a composição centrada da jornada do
  candidato, os tokens da direção experimental, a ação principal de 48 px (`--controle-g`).
- **CSP sem estilo nem script embutido** (`CLAUDE.md`, `091` e `092`).
- **Nada muda** no que é gravado, no envio em partes nem na R-11 do estudo; tudo atrás da chave.
- **A detecção automática do giro fica fora**, como registro (A-1). Nesta spec, o avanço automático
  *pode* ser só por tempo, com "Próximo" manual sempre disponível — mas a acessibilidade (Libras,
  limitação motora) não pode depender de detecção. A Q-1 trata disso.

### Session 2026-11-15 (decisões do usuário sobre o PR #566)

- **Q-1 a Q-4: adotadas as recomendações.** O avanço continua só pelo gesto, com "Próximo" grande sobre
  o vídeo (D-001); o selo provisório muda no acompanhamento inteiro (D-008); os dados para conferência
  ficam no fim do comprovante, visíveis (D-009); a validação no celular é da equipe, num iPhone e num
  Android reais, e de três pessoas de fora da equipe técnica (SC-2655, SC-2658).

### Perguntas ao usuário (decididas em 15/11 pelas recomendações abaixo)

#### Q-1 — Como a gravação avança de um passo ao outro?

A FR-7112 da `166` diz que os passos avançam *"pelo toque ou pelo teclado, sem tempo mínimo e sem
cronômetro por passo"*, e a R-21 do estudo diz *"por toque ou teclado, e não por relógio"*. O avanço
por tempo, que o pedido admite, contraria as duas.

| Opção | O que é | Implicações |
|---|---|---|
| **A (recomendada)** | Só pelo gesto, com o alvo certo: "Próximo" grande, sobre o vídeo, no terço de baixo, ao alcance do polegar; o foco fica nele, e Espaço ou Enter avançam no computador | Nenhuma regra da `166` muda. Resolve "clicar enquanto vira o rosto" pela posição e pelo tamanho do alvo, e não pelo relógio. Não é "como o banco" |
| B | Automático por tempo **só nos dois perfis**, com contagem visível (por exemplo, 5 segundos) e "Próximo" sempre disponível; documento e fala continuam pelo gesto | Revê a FR-7112 da `166` e a R-21 do estudo. Quem vira o rosto devagar vê a instrução mudar no meio do giro, o que contradiz o "não há pressa" da tela anterior |
| C | Automático por tempo em todos os passos | Não recomendado: o documento e a fala (sobretudo em Libras) têm duração que depende da pessoa |

#### Q-2 — O selo de situação provisória muda só no passo, ou em todo o acompanhamento?

O tracejado de "Falta um passo seu" é o mesmo de **todas** as situações provisórias do acompanhamento
(dez rótulos, de "Inscrição enviada" a "Aguardando o resultado"). Ele existe porque a UX-155 da `063`
exige que o provisório se distinga do registrado sem depender da cor.

| Opção | O que é | Implicações |
|---|---|---|
| **A (recomendada)** | Muda o componente: selo em pílula, com ícone e a palavra, em todos os rótulos provisórios; a distinção sem cor passa do tracejado ao ícone | Uma forma só para a mesma coisa. Muda a aparência do topo do acompanhamento para todo candidato, não só para quem tem passo |
| B | Muda só quando o rótulo é do passo | Dois desenhos para o mesmo conceito ("provisório"), até a `P2.3` |

#### Q-3 — Onde ficam o número do envio e o resumo no comprovante?

A FR-7123 da `166` exige que o comprovante **mostre** o número do envio, a data e a hora, a duração, o
formato e o resumo.

| Opção | O que é | Implicações |
|---|---|---|
| **A (recomendada)** | No fim da página, em "Dados para conferência", visíveis e em texto menor; o topo é a confirmação | A FR-7123 da `166` continua literal, e o comprovante impresso leva os dados |
| B | Num recolhido "Ver dados técnicos" | Menos ruído, mas o recolhido fechado não sai na impressão, e a FR-7123 da `166` passa a valer "ao abrir" |

#### Q-4 — Quem valida no celular?

| Opção | O que é | Implicações |
|---|---|---|
| **A (recomendada)** | A equipe num iPhone e num Android reais (SC-2655) **e** três pessoas de fora da equipe técnica, no próprio celular, com roteiro de tarefa (SC-2658) | É a única forma de saber se "parece produção" para o público amplo. Pede recrutar três pessoas; o vídeo delas é de teste, num ambiente local, e se descarta |
| B | Só a equipe, nos dois aparelhos | Mais rápido; a percepção do público amplo fica sem medida |

---

## User Scenarios & Testing *(mandatory)*

Os cenários usam o C18 dos cenários de treinamento (`171`), com a chave do vídeo ligada no
desenvolvimento, e uma inscrição na Modalidade que a Etapa restrita alcança, dentro do período.

### User Story 1 — Gravar o vídeo inteiro no celular (Priority: P1)

Uma candidata abre o acompanhamento no celular, toca na ação do passo, escolhe o vídeo, prepara-se,
grava os quatro passos com a câmera frontal em retrato, assiste, envia e vê a confirmação — sem
rolar a tela durante a gravação, sem alcançar o topo da tela com o polegar e sem a tela apagar.

**Why this priority**: é o caminho mais provável do público, e o único que ninguém testou.

**Independent Test**: num iPhone (Safari) e num Android (Chrome) reais, do acompanhamento ao
comprovante, contando os toques e observando a tela.

**Acceptance Scenarios**:

1. **Given** a candidata no "Antes de gravar", **When** toca "Continuar", **Then** o navegador pede a
   câmera e o microfone, e, concedidos, ela se vê no palco, ocupando a tela, com o guia e o medidor de
   som, e a ação principal é "Começar a gravar" — sem outro botão no caminho (FR-7866).
2. **Given** a gravação em curso, **When** ela olha o celular, **Then** vê sobre o vídeo, no terço de
   cima, "Passo 1 de 4", o título e a instrução do passo, e, no terço de baixo, "Próximo" ao alcance
   do polegar (FR-7868, FR-7869).
3. **Given** a gravação em curso, **When** ela não toca a tela por três minutos, **Then** a tela não
   apaga (FR-7877).
4. **Given** o último passo, **When** ela toca "Terminar a gravação", **Then** a revisão mostra o vídeo
   grande, a duração em minutos e segundos e quanto o envio vai gastar da internet dela (FR-7880).
5. **Given** o envio concluído, **When** o comprovante abre, **Then** a primeira tela diz que o vídeo
   foi enviado, com data e hora, e o que acontece agora; os dados para conferência ficam no fim
   (FR-7882).

---

### User Story 2 — Gravar pelo computador (Priority: P1)

Um candidato abre a página no computador. A página fica centrada, o vídeo da webcam aparece grande e
em paisagem, e a instrução do passo fica sobre a parte de cima do vídeo, perto da câmera. Ele avança
com o mouse, com Espaço ou com Enter.

**Why this priority**: é o caminho em que o usuário viu os problemas, e o de quem não tem celular com
câmera boa.

**Independent Test**: no Safari, no Chrome e no Firefox do computador, a 1280 e a 1920 px, com câmera
real e com a imagem de teste do desenvolvimento.

**Acceptance Scenarios**:

1. **Given** qualquer tela da verificação a 1280 px, **When** ela abre, **Then** o conteúdo fica numa
   coluna centrada, com margens iguais dos dois lados (FR-7850).
2. **Given** a gravação em curso, **When** o candidato aperta Espaço, **Then** a gravação passa ao passo
   seguinte e a nova instrução é anunciada ao leitor de tela (FR-7869, UX-875).
3. **Given** a gravação em curso, **When** ele lê a instrução, **Then** ela está sobre o vídeo, e a lista
   inteira dos passos não aparece (FR-7867, FR-7868).

---

### User Story 3 — Saber, no acompanhamento, o que falta e até quando (Priority: P1)

A candidata abre o acompanhamento e entende, na primeira tela do celular, que falta um passo dela,
até quando, e que a ação a leva a escolher entre vídeo e entrevista ao vivo.

**Why this priority**: é a porta de tudo; sem ela, a pessoa não chega à gravação.

**Independent Test**: o acompanhamento do C18 nos três estados do passo, a 375 e a 1280 px.

**Acceptance Scenarios**:

1. **Given** o passo pendente com o vídeo disponível, **When** o acompanhamento abre, **Then** o selo
   diz "Falta um passo seu" com ícone, sem tracejado (FR-7856), o prazo vem numa linha própria antes
   da explicação (FR-7857), e a ação diz "Escolher entre vídeo e entrevista ao vivo" (FR-7858).
2. **Given** o vídeo enviado e ainda não aberto, **When** o acompanhamento abre, **Then** a ação é
   "Ver o comprovante", como hoje.
3. **Given** a chave desligada, **When** o acompanhamento abre, **Then** o degrau é o da `171`, sem
   ação de vídeo, e só o selo muda (FR-7888).

---

### User Story 4 — Escolher a forma e preparar-se (Priority: P2)

O candidato lê, em dois cartões de igual peso, o que é cada forma: o vídeo, gravado agora, de casa,
em poucos minutos; a entrevista, com dia e hora informados pela comissão. Escolhe, e, no vídeo, lê
três itens do que preparar — inclusive o documento com foto em mãos — antes de dizer a idade.

**Why this priority**: decide a confiança e evita a gravação que falha no primeiro passo por falta do
documento.

**Independent Test**: a página da verificação nas telas de escolha, ao vivo, preparo e menor de
idade, a 375 e a 1280 px, com e sem vídeo enviado.

**Acceptance Scenarios**:

1. **Given** a escolha, **When** ela abre, **Then** cada cartão diz o que a forma é, quanto leva, onde
   acontece e o que acontece depois, e nenhum é mais destacado que o outro (FR-7860).
2. **Given** o "Antes de gravar", **When** ele abre, **Then** nenhuma recusa aparece (FR-7854, FR-7865).
3. **Given** o "Antes de gravar", **When** o candidato toca "Continuar" sem responder a idade, **Then** a
   recusa aparece junto da pergunta e o foco vai para ela (FR-7865).
4. **Given** o "Antes de gravar", **When** ele lê a tela, **Then** as seis informações de hoje continuam
   todas lá, em dois blocos: o que preparar e quem vê o vídeo (FR-7863, FR-7864).

---

### User Story 5 — Conferir o comprovante e assistir ao próprio vídeo (Priority: P2)

Depois de enviar, ou mais tarde pelo acompanhamento, o candidato abre o comprovante, vê que deu
certo, entende o que vem agora, assiste ao vídeo que enviou e, se quiser, troca-o enquanto a comissão
não o abriu.

**Why this priority**: o comprovante é a prova que a pessoa guarda; hoje ele fala com a comissão.

**Independent Test**: o comprovante nos estados recebido, em análise, encaminhado e arquivo eliminado,
a 375 e a 1280 px, e impresso.

**Acceptance Scenarios**:

1. **Given** o vídeo recebido, **When** o comprovante abre a 375 px, **Then** a confirmação e a data
   estão no primeiro quadro, e "E agora?" vem logo depois (FR-7882, SC-2659).
2. **Given** o comprovante, **When** ele é impresso, **Then** cabe numa folha e leva os dados para
   conferência (FR-7884).
3. **Given** o arquivo eliminado, **When** o comprovante abre, **Then** a frase da eliminação continua, e
   não há "assistir" (FR-7885).

---

### User Story 6 — Gravar com leitor de tela, teclado ou em Libras (Priority: P3)

Uma pessoa cega ou com baixa visão grava com o leitor de tela; outra, com limitação motora, usa só o
teclado; uma pessoa surda faz a fala em Libras, que leva mais tempo que a frase falada.

**Why this priority**: a gravação não pode depender de uma única forma de interação (R-21 do estudo).

**Independent Test**: VoiceOver no iPhone e no macOS e NVDA no Windows, de "Antes de gravar" ao envio;
só teclado no computador.

**Acceptance Scenarios**:

1. **Given** o passo que muda, **When** a pessoa avança, **Then** o leitor anuncia "Passo 2 de 4: Perfil
   esquerdo" e a instrução (UX-875).
2. **Given** o último passo em Libras, **When** a pessoa leva o tempo que precisar, **Then** nada avança
   sozinho e nada a apressa (FR-7869, D-001).

---

### Edge Cases

- **A permissão da câmera negada** leva à tela "A câmera não abriu", com o caminho de liberação do
  aparelho, como hoje; "Tentar de novo" pede de novo sem outro passo.
- **Câmera sem microfone**: o medidor diz que o microfone não foi encontrado, e a gravação continua
  possível, porque a fala pode ser substituída pelo papel escrito ou por Libras (o passo 4 do roteiro
  já diz isso).
- **O navegador não sabe manter a tela acesa**: o palco diz, antes de "Começar a gravar", "Mantenha a
  tela acesa: se ela apagar, a gravação para e você grava de novo" (FR-7877).
- **A tela apaga ou a pessoa troca de aplicativo no meio**: a tomada é descartada, com a explicação, como
  hoje (a FR-7115 da `166`); o palco volta ao estado de antes de começar.
- **Celular deitado**: o palco se adapta à paisagem — instrução no topo, controles à direita — e sugere
  o retrato, sem impedir (FR-7878).
- **Tela de 320 px** (zoom de 400% ou celular pequeno): nada transborda, e "Próximo" e "Não consigo
  usar a câmera" continuam alcançáveis sem rolagem lateral.
- **A instrução do passo 4 é longa** (cerca de 250 caracteres): sobre o vídeo, ela ocupa no máximo o
  terço de cima; o que passar disso rola dentro da faixa, e o rosto continua visível no centro.
- **Toque duplo em "Próximo"**: dois toques quase juntos contam como um, para ninguém pular um perfil
  sem querer (FR-7870).
- **Toque sem querer em "Parar e recomeçar"**: o controle fica longe de "Próximo" e é menor (FR-7871);
  a tomada descartada não sai do aparelho, e gravar de novo é o mesmo gesto do começo.
- **O período termina no meio da gravação**: nada muda; o envio iniciado no período pode concluir até
  uma hora depois (a FR-7126 da `166`).
- **Movimento reduzido** no sistema: nenhuma transição se anima (FR-7879).
- **Vídeo já enviado e ainda não aberto**: a escolha continua avisando que o novo substitui o anterior,
  agora num aviso informativo acima dos cartões.
- **Menor de 18 anos**: a tela própria continua, na mesma composição, sem a opção do vídeo (a FR-7109
  da `166`).
- **iPad** em retrato ou paisagem: é tratado pela largura, como o computador ou o celular.

## Requirements *(mandatory)*

### Functional Requirements

#### A composição de todas as telas

- **FR-7850**: As telas da verificação no portal — a página da gravação em todas as suas telas, o
  comprovante e a página da situação sem gravação — DEVEM usar a composição centrada da jornada do
  candidato do estudo de design system: uma coluna de no máximo 44rem, centrada na página. A 1280 e a
  1920 px, nenhuma DEVE deixar o conteúdo encostado à esquerda com a área à direita vazia.
- **FR-7851**: Cada tela DEVE ter **uma** ação principal, em botão de pelo menos 48 px de altura
  (`--controle-g`), com largura cheia no celular; as outras ações DEVEM vir abaixo dela, como
  secundárias ou discretas. A escolha entre vídeo e entrevista ao vivo é a exceção: dois gestos de
  igual peso (a FR-7108 da `166`).
- **FR-7852**: O título da página DEVE ser o nome publicado da Etapa, e o topo DEVE dizer onde a pessoa
  está, em três momentos nomeados e sem número — "Preparar", "Gravar", "Conferir e enviar" —, para não
  competir com o "Passo N de 4" do roteiro.
- **FR-7853**: Nenhum texto fixo das telas DEVE nomear a Modalidade nem o procedimento. Onde hoje se lê
  "a vaga para pessoas pretas e pardas", DEVE vir o nome publicado da Modalidade, como no degrau da
  `171`; onde se lê "Verificação da autodeclaração" como título, o nome publicado da Etapa. O texto do
  roteiro é exceção, porque é versionado e viaja com o vídeo (D-003).
- **FR-7854**: Em repouso, nenhuma tela DEVE mostrar recusa, erro ou aviso que dependa de um gesto. Todo
  elemento que a página esconde DEVE continuar escondido até o script o mostrar, qualquer que seja a
  regra de exibição da classe dele (A-2).
- **FR-7855**: As cores, os espaços, os raios e as alturas DEVEM vir dos tokens da `172` e do
  `--controle-g` (D-007), sem cor literal nova; nenhum template DEVE ter estilo ou script embutido.

#### O passo no acompanhamento

- **FR-7856**: O rótulo das situações provisórias do acompanhamento DEVE deixar o contorno tracejado e
  passar a selo em pílula, com ícone e a palavra; a distinção entre provisório e registrado DEVE
  continuar visível sem cor (a UX-155 da `063`), agora pelo ícone (Q-2, D-008).
- **FR-7857**: Quando o vídeo pode ser gravado e o período tem fim, o prazo DEVE ter linha própria, em
  destaque, antes do texto explicativo: "Prazo: até {data} às {hora}". Sem fim de período, a linha não
  aparece.
- **FR-7858**: A ação do passo com o vídeo disponível DEVE dizer o que a pessoa encontra ao chegar:
  "Escolher entre vídeo e entrevista ao vivo", no lugar de "Ver como funciona". As outras ações do
  degrau não mudam.
- **FR-7859**: O que o degrau diz (a FR-7304 da `171`: o porquê, o quando, o como, a consequência e o
  Edital) NÃO DEVE mudar; esta spec muda só a ordem e o destaque.

#### A escolha

- **FR-7860**: A escolha DEVE apresentar as duas formas como cartões do mesmo tamanho, com o mesmo
  desenho, cada um dizendo o que a forma é, quanto leva, onde acontece e o que acontece depois:
  - o vídeo: gravado agora, pelo celular ou pelo computador, de onde a pessoa estiver; até
    {teto} minutos; ela assiste antes de enviar e pode gravar de novo;
  - a entrevista ao vivo: a comissão informa o dia, a hora e como participar; nada a fazer agora.

  "As duas formas valem igual" DEVE continuar acima dos cartões.
- **FR-7861**: O prazo e o aviso de substituição do vídeo já enviado DEVEM aparecer acima dos cartões,
  o prazo na mesma forma da FR-7857.
- **FR-7862**: A tela "Entrevista ao vivo", a do menor de idade e a "Sem câmera, sem problema" DEVEM
  ter, como ação principal, "Voltar ao acompanhamento", e manter o texto de hoje.

#### Antes de gravar

- **FR-7863**: O "Antes de gravar" DEVE abrir com **três** itens do que preparar, cada um com pictograma
  e uma frase: lugar claro; rosto sem óculos escuros, boné ou filtro; o documento de identidade com
  foto em mãos. Abaixo deles, o teto: "O vídeo tem até {teto} minutos. Não há pressa em nenhum passo."
- **FR-7864**: As informações de hoje sobre o que a comissão olha, quem assiste, a guarda e o
  encaminhamento ("isso não é reprovação") DEVEM continuar na tela, visíveis e sem recolher, num bloco
  próprio "Quem vê o seu vídeo", depois do preparo. Nenhuma frase delas DEVE sair (D-010).
- **FR-7865**: A pergunta da idade DEVE oferecer as duas respostas como opções grandes, com a área
  inteira clicável. A recusa DEVE aparecer só depois de "Continuar" sem resposta, junto da pergunta, com
  o foco nela. A declaração e o que ela decide não mudam (a FR-7109 da `166`).

#### O palco: a câmera e a gravação

- **FR-7866**: O teste da câmera e a gravação DEVEM ser uma tela só, o palco. "Continuar", no "Antes de
  gravar", DEVE pedir a câmera e o microfone sem outro clique; concedidos, o palco mostra a prévia com o
  guia e o medidor, e a ação principal é "Começar a gravar". "Abrir a câmera" e "Ir para a gravação"
  DEVEM sair (D-004). Negada a permissão, a tela "A câmera não abriu" continua.
- **FR-7867**: Antes de começar, o palco DEVE mostrar, uma vez, o que a pessoa vai fazer: os títulos dos
  quatro passos e o teto. Durante a gravação, a lista NÃO DEVE aparecer; aparece só o passo atual.
- **FR-7868**: Durante a gravação, a instrução do passo atual DEVE ficar **sobre a prévia**, no terço de
  cima — perto da câmera frontal —, em texto grande sobre uma faixa que garanta o contraste, com
  "Passo N de 4" e o título do passo. O texto DEVE ser o do roteiro vigente, sem resumo (D-003).
- **FR-7869**: "Próximo" DEVE ficar sobre a prévia, no terço de baixo, ao alcance do polegar no celular,
  com pelo menos 48 px de altura; no último passo, ele diz "Terminar a gravação". O foco DEVE ficar nele
  durante a gravação, para que Espaço e Enter avancem no computador. O avanço DEVE ser só pelo gesto,
  sem tempo mínimo e sem avanço por relógio (a FR-7112 da `166`; Q-1, D-001).
- **FR-7870**: Dois toques em "Próximo" separados por menos de meio segundo DEVEM contar como um. Isso
  protege contra o toque duplo, e não impõe ritmo: não há tempo mínimo por passo.
- **FR-7871**: Durante a gravação, o palco DEVE mostrar, sobre a prévia, o selo "Gravando" com a palavra
  por extenso e o tempo ("0:42 de 3:00"). "Parar e recomeçar" DEVE ficar no canto oposto a "Próximo",
  menor que ele.
- **FR-7872**: O guia de enquadramento DEVE ser proporcional ao palco, com a frase "Encaixe o rosto no
  oval. Ele não aparece no vídeo." O guia NÃO DEVE acompanhar o rosto (a FR-7150 da `166`, D-002) e NÃO
  DEVE entrar na gravação (a FR-7114 da `166`).
- **FR-7873**: Antes de começar, o medidor de som DEVE ser uma barra larga, com a frase "Fale alguma
  coisa para testar o microfone", que passa a "Estamos ouvindo você" depois que o som passa do nível de
  fala. Sem microfone, ele diz isso, e a gravação continua possível. Durante a gravação, o medidor fica
  pequeno, no selo.
- **FR-7874**: A prévia continua espelhada, e o palco DEVE dizer, antes de começar: "Você se vê como num
  espelho. O vídeo enviado fica na posição normal, e o documento pode ser lido."
- **FR-7875**: No celular, o palco DEVE ocupar a altura visível da tela, sem o cabeçalho do portal e sem
  rolagem, em retrato, pela composição da página e não pelo modo de tela cheia do navegador (D-005).
  "Não consigo usar a câmera" DEVE continuar no palco, alcançável sem rolar (a UX-772 da `166`), e,
  antes de começar, "Voltar" DEVE levar ao "Antes de gravar".
- **FR-7876**: No computador, o palco DEVE mostrar a prévia em paisagem, na largura da coluna, centrada,
  com a mesma instrução sobre a prévia e os mesmos controles.
- **FR-7877**: Enquanto o palco está aberto, a página DEVE pedir ao aparelho que a tela não apague, e
  soltar o pedido ao sair do palco. Onde o navegador não oferecer isso, o palco DEVE dizer, antes de
  "Começar a gravar": "Mantenha a tela acesa: se ela apagar, a gravação para e você grava de novo." O
  descarte da tomada quando a página some (a FR-7115 da `166`) NÃO DEVE mudar.
- **FR-7878**: Com o celular deitado, o palco DEVE continuar usável — instrução no topo da prévia,
  controles ao lado — e sugerir o retrato, sem impedir a gravação.
- **FR-7879**: Nenhuma transição do palco DEVE se animar quando o sistema pede movimento reduzido, e
  nenhuma DEVE piscar mais de três vezes por segundo.

#### A revisão e o envio

- **FR-7880**: A revisão DEVE mostrar a tomada no tamanho do palco, a duração em minutos e segundos e
  quanto o envio vai gastar da internet ("cerca de {N} MB"), as três perguntas de autoconferência, e
  as ações "Enviar este vídeo" (principal) e "Gravar de novo" (secundária). A frase "só o vídeo que
  você enviar chega à comissão" continua (a UX-773 da `166`).
- **FR-7881**: O envio DEVE mostrar a barra de progresso larga, com a porcentagem por extenso, e "Não
  feche esta página enquanto o envio não terminar". A retomada, as três tentativas e a sugestão da
  entrevista ao vivo não mudam (R-20 do estudo).

#### O comprovante

- **FR-7882**: O comprovante DEVE abrir pela confirmação: ícone de sucesso, "Seu vídeo foi enviado" e a
  data e a hora do recebimento. Depois, nesta ordem: "E agora?", "Assistir ao vídeo que você enviou",
  "Gravar outro vídeo" quando a troca é permitida, e, no fim, "Dados para conferência", com o número do
  envio, a duração, o formato e o resumo, visíveis e em texto menor (Q-3, D-009). O rótulo do resumo
  DEVE explicar para que serve: "Código de conferência do arquivo (SHA-256)".
- **FR-7883**: A duração DEVE aparecer em minutos e segundos ("1 min 12 s"), e não em segundos com casa
  decimal.
- **FR-7884**: O comprovante impresso DEVE caber numa folha A4 e levar a confirmação, o "E agora?" e os
  dados para conferência, sem o reprodutor de vídeo.
- **FR-7885**: Com o arquivo eliminado, o comprovante DEVE manter a frase da eliminação logo abaixo da
  confirmação, e não oferecer "assistir" (a FR-7149 da `166`).
- **FR-7886**: A página da situação quando não se pode gravar (análise iniciada, encaminhada, ao vivo,
  período encerrado ou não aberto) DEVE usar a mesma composição, com o estado como centro e a ação
  "Ver o comprovante" quando houver vídeo.

#### O que não muda

- **FR-7887**: Esta spec NÃO DEVE mudar o que é gravado nem o que é enviado: o roteiro e a versão dele,
  as marcas, o formato, o teto, as partes de no máximo 8 MiB, a retomada, o resumo, as rotas, as
  respostas e a regra de que o vídeo só confirma (R-11 do estudo). Os testes de contrato e de envio da
  `166` DEVEM passar sem mudança.
- **FR-7888**: Tudo DEVE continuar atrás da chave do vídeo; desligada, as rotas continuam respondendo
  como inexistentes (a FR-7100 e a FR-7110 da `166`), e o degrau sem vídeo da `171` muda só no selo
  (FR-7856).
- **FR-7889**: A exceção de política de conteúdo DEVE continuar só na página da gravação (a FR-7117 da
  `166`), sem diretiva nova e sem origem externa. Manter a tela acesa NÃO DEVE exigir permissão nova
  declarada.
- **FR-7890**: O palco NÃO DEVE analisar a imagem de nenhuma forma para guiar a pessoa: nem rosto, nem
  luz, nem enquadramento (a FR-7150 da `166`). O medidor de som é técnico e local, e não entra no que
  se envia.
- **FR-7891**: As frases novas DEVEM passar pela varredura de vocabulário do candidato, que já alcança
  as páginas da gravação e do comprovante (a FR-7331 da `171`).

#### A verificação

- **FR-7892**: A entrega DEVE ser verificada em aparelhos reais — um iPhone com Safari e um Android
  com Chrome — e no computador, no Safari, no Chrome e no Firefox, de "Antes de gravar" ao comprovante.
- **FR-7893**: A entrega DEVE guardar, em `doc/`, as capturas de cada tela antes e depois, a 375, a 768,
  a 1280 e a 1920 px, com a imagem de teste do desenvolvimento no lugar do rosto.

### Requisitos de experiência

- **UX-870**: A linguagem é a do candidato da `166` e da `171`, em "você", com frases curtas. Termo
  técnico só nos dados para conferência, e sempre com o que significa.
- **UX-871**: Celular primeiro: coluna única, botões de largura cheia, o gesto da tela no terço de baixo,
  e nada que exija alcançar o topo da tela com o polegar durante a gravação.
- **UX-872**: Durante a gravação, a pessoa não precisa desviar os olhos da câmera para ler: a instrução
  fica sobre o vídeo, no lado da câmera.
- **UX-873**: Nenhuma cor sozinha diz estado: "Gravando" é palavra, o passo atual é "Passo N de 4", o
  provisório tem ícone.
- **UX-874**: Alvo de pelo menos 48 px na ação principal e de 32 px em qualquer outro controle, com o
  rótulo inteiro clicável nas opções.
- **UX-875**: Cada mudança de passo DEVE ser anunciada ao leitor de tela como "Passo N de 4: {título}.
  {instrução}", e o foco não sai de "Próximo".
- **UX-876**: O tom tranquiliza nos pontos de tensão: "Não há pressa", "Isso não é reprovação", "Este
  vídeo não sai do seu aparelho" — onde a `166` já os diz, sem frase nova de garantia.
- **UX-877**: A primeira impressão é de produto público: nenhum elemento com aparência de depuração —
  contorno tracejado, texto de desenvolvimento, controle sem estilo — fora do que só aparece no
  desenvolvimento (a imagem de teste).

### Key Entities

Nenhuma entidade nova. A spec lê o que a `166` e a `171` já têm: o vídeo e o estado dele, o roteiro e a
versão, o passo e o período da Etapa, e os nomes publicados da Etapa e da Modalidade.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2650**: A 1280 e a 1920 px, em todas as telas da verificação, a coluna de conteúdo fica centrada:
  a diferença entre as margens esquerda e direita é de no máximo 1 px.
- **SC-2651**: A 375×667 e a 390×844 px, durante toda a gravação, o palco ocupa a altura visível sem
  rolagem, e a instrução, "Próximo" e "Não consigo usar a câmera" ficam à vista.
- **SC-2652**: De "Continuar", no "Antes de gravar", a "Começar a gravar" à vista, a pessoa faz zero
  gestos além de conceder a permissão do navegador (hoje são dois).
- **SC-2653**: Em repouso, nenhuma tela da verificação mostra recusa, erro ou aviso de gesto: a conferência
  de cada elemento escondido no carregamento dá zero visíveis.
- **SC-2654**: O pedido de envio de um vídeo gravado pela página nova tem a mesma versão do roteiro, uma
  marca por passo na mesma ordem, o mesmo formato e as mesmas rotas que o de hoje; os testes da `166`
  passam sem mudança.
- **SC-2655**: Num iPhone e num Android reais, a pessoa grava os quatro passos tocando só em "Começar a
  gravar", três vezes em "Próximo" e uma em "Terminar a gravação", e a tela não apaga em três minutos
  sem toque *(humano)*.
- **SC-2656**: A instrução sobre o vídeo tem contraste de pelo menos 4,5:1 no pior caso, medido sobre
  um quadro branco puro e sobre um preto puro.
- **SC-2657**: Nenhum template da verificação tem estilo ou script embutido, e a política de conteúdo da
  página de gravação é a mesma de hoje, diretiva a diretiva.
- **SC-2658**: Três pessoas de fora da equipe técnica, cada uma no próprio celular, chegam ao comprovante
  sem ajuda, e nenhuma descreve a tela como "de teste" ou "inacabada" na conversa depois da tarefa
  *(humano; Q-4)*.
- **SC-2659**: A 375 px, a confirmação e a data do comprovante ficam no primeiro quadro, e os dados para
  conferência ficam abaixo de "E agora?".

## Assumptions

- A `166` e a `171` estão na `main` (15/11) e não mudam antes da implementação desta.
- Os tokens da direção experimental da `172` entram na `main` com o #564; esta spec os usa e acrescenta
  só o `--controle-g` (48 px), que o estudo previu para o portal (D-007).
- O roteiro de referência continua o mesmo; mudá-lo é versão nova (P-8 do estudo), e não polimento.
- Os navegadores de referência são os do público: Safari no iPhone, Chrome no Android e os três
  principais no computador, nas versões dos últimos dois anos.
- "Manter a tela acesa" é oferecido pela maior parte desses navegadores; onde não for, o aviso da
  FR-7877 basta, porque o descarte já é explicado.
- O ambiente da validação é local, com a chave ligada no desenvolvimento; nenhum vídeo de teste vai
  para produção.

## Out of Scope

- A detecção automática do giro do rosto, ou qualquer leitura da imagem no aparelho (A-1).
- A leitura da instrução em voz alta pelo aparelho (D-006).
- Um roteiro novo, mais curto ou por unidade (P-8 do estudo).
- O resto do portal e do acompanhamento: é a `P2.3` do estudo de design system.
- A Mesa e todas as telas da gestão da verificação.
- O relato de falha técnica e a desistência do vídeo enviado (registros da `166` e da `171`).
- Qualquer mudança nas rotas, nos contratos, no armazenamento ou na habilitação (`169`).

## Dependências

- **`166` e `171`**, na `main` (#547, #551): as telas e os estados que esta spec redesenha.
- **`172`** (#563 a spec, #564 a implementação, sem merge): os tokens e a composição. A implementação
  desta espera o merge do #564 (D-007).
- **`169`** (só spec, #552): se for implementada antes, a chave muda de nome; esta spec segue o nome que
  estiver no código.
- **A migração do design system** (#565, pasta `173`): não toca o portal; as duas não colidem.

## Achados (registro, e não escopo)

- **A-1 — A detecção automática do giro do rosto.** Avançar sozinho quando a câmera vê o perfil, como
  nos aplicativos de banco, pede processamento facial no aparelho. É dado biométrico (LGPD, art. 11), a
  FR-7150 da `166` e a R-19 do estudo o proíbem hoje, e mudá-las pede a validação da CPVA e do
  encarregado de dados, e o relatório de impacto. Fica como decisão pendente do usuário, para uma spec
  própria. A acessibilidade não pode depender dela: o gesto continua sempre disponível.
- **A-2 — A recusa da idade aparece em repouso.** A classe da recusa declara exibição em bloco, e isso
  vence o atributo que a esconde: é o mesmo defeito que o `.progresso` do envio de arquivos já teve e
  corrigiu com uma linha. Esta spec o corrige nas telas da verificação (FR-7854); outras telas do portal
  que escondem `.recusa` pelo atributo podem ter o mesmo defeito, e não foram conferidas.
- **A-3 — O preparo não pedia o documento.** O primeiro passo do roteiro é mostrar o documento com foto,
  e o "Antes de gravar" de hoje não diz para tê-lo em mãos. Esta spec o põe no preparo (FR-7863).
- **A-4 — A instrução do passo 4 tem cerca de 250 caracteres.** Sobre o vídeo, ela ocupa mais que as
  outras. Encurtá-la é versão nova do roteiro (P-8 do estudo); esta spec a mostra inteira (D-003).
- **A-5 — Nenhum envio em partes foi feito por rede móvel.** As partes de 8 MiB e a retomada só foram
  exercitadas em rede local. A validação em aparelho real (FR-7892) vai exercitá-las; um defeito que
  aparecer ali é da `166`, e vira registro.
- **A-6 — A duração do comprovante sai como "72.3 segundos"**, com ponto decimal e sem conversão para
  minutos. Esta spec a corrige (FR-7883).

## Decisões

### D-001 — O avanço continua pelo gesto

Recomendação da Q-1. O problema que o usuário viu — clicar enquanto vira o rosto — é de posição e de
tamanho do alvo, e se resolve com "Próximo" grande, sobre o vídeo, ao alcance do polegar, e com o foco
nele no computador. O avanço por relógio contraria a FR-7112 da `166` e a R-21 do estudo, e muda a
instrução no meio do giro de quem vira devagar.

### D-002 — O guia não acompanha o rosto

Acompanhar o rosto é detectar o rosto, o que a FR-7150 da `166` proíbe. O guia fica fixo, proporcional
ao palco, e diz o que é. A queixa do usuário fica respondida pelo tamanho e pela explicação, e o resto
é o A-1.

### D-003 — O texto do passo é o do roteiro, sem resumo

O vídeo guarda a versão do roteiro para que a comissão leia os passos que o candidato viu (a FR-7113
da `166`). Mostrar sobre o vídeo um texto diferente do roteiro romperia essa garantia sem mudar a
versão. O título do passo e o "Passo N de 4" são acréscimos de navegação, e o texto da instrução é o
do roteiro, inteiro.

### D-004 — O teste da câmera e a gravação numa tela só

O teste existia para a pessoa se ver antes de gravar. No palco, ela se vê antes de "Começar a gravar",
com o guia e o medidor, e o mesmo fluxo de câmera continua aberto ao começar. Saem dois cliques e uma
troca de tela, e a câmera não fecha e reabre entre o teste e a gravação.

### D-005 — A tela inteira pela composição, e não pelo modo de tela cheia

No iPhone, o modo de tela cheia do navegador só vale para o elemento de vídeo, e entrega o vídeo ao
reprodutor do sistema, que esconde a instrução e os controles. O palco ocupa a tela pela composição da
página, em todos os aparelhos do mesmo jeito.

### D-006 — Sem voz sintetizada

Ler a instrução em voz alta ajudaria quem lê pouco, mas a voz do aparelho seria captada pelo microfone e
entraria no vídeo enviado — o que muda o que é gravado. Fica fora desta spec.

### D-007 — Os tokens da `172`, mais o controle grande

A spec usa os tokens que a `172` acrescenta (neutros, espaços, raios, a coluna de 44rem) e acrescenta
só o `--controle-g`, de 48 px, que o estudo de design system previu para a ação principal do candidato.
A implementação espera o merge do #564, para não declarar os mesmos tokens em dois lugares.

### D-008 — O selo provisório muda no acompanhamento inteiro

Recomendação da Q-2. O tracejado é o mesmo componente em todas as situações provisórias; mudá-lo só no
passo criaria dois desenhos para o mesmo conceito. A distinção sem cor da UX-155 da `063` passa do
contorno ao ícone.

### D-009 — Os dados para conferência ficam visíveis, no fim

Recomendação da Q-3. O comprovante é guardado e impresso, e a FR-7123 da `166` diz que ele mostra os
dados. No fim e em texto menor, eles deixam de disputar a atenção com a confirmação, e continuam no
papel.

### D-010 — Nada do que a `166` decidiu dizer é cortado ou recolhido

Cada frase das telas da `166` foi decidida em spec. Esta spec reordena, agrupa e dá destaque; não corta
nem recolhe. É a mesma condição que a `172` adotou para o piloto. A única frase que muda de lugar
sem continuar visível é a lista inteira do roteiro durante a gravação, que aparece antes de começar
(FR-7867) e volta a cada passo, um por vez (FR-7868).
