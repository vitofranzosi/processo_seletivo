# Feature Specification: A detecção do giro do rosto na gravação do vídeo

**Feature Branch**: `claude/176-deteccao-do-giro-do-rosto`, nascida da `main` em `34e5f8bd` (o merge
da implementação da `174`, #568)

**Created**: 2026-11-15

**Status**: Especificada em 15/11; as quatro perguntas (Q-1 a Q-4) foram decididas pelo usuário no
mesmo dia, pelas recomendações. Planejada, com tarefas e implementada no mesmo dia, sem merge (o merge
é do usuário). Pendentes: a câmera real e o celular de entrada (SC-2753, SC-2757) e a P-13.
Emendada em 15/11, à noite, depois do teste do usuário com câmera real no Safari: o documento passa
a ser percebido (FR-8060 a FR-8066), a frase do passo de frente desce para junto do botão
(FR-8070 a FR-8074) e o medidor do microfone é refeito (FR-8080 a FR-8085); Q-5 e Q-6 decididas pelo
usuário pelas recomendações (D-009 a D-011).

**Input**: em 15/11 o usuário gravou um vídeo real pela página da `166`, no Safari, e pediu que a
gravação ficasse *"como acontece nos bancos — pedem para você ir para um lado, ele já detecta, gira
para o outro, já detecta, e depois pede para você falar"*. A `174` separou esse pedido do polimento
(A-1 da `174`), por envolver dado biométrico e acessibilidade, e esta spec é a que ela pediu.

> **Faixa de identificadores.** Esta spec abre em **FR-8000**, **SC-2750** e **UX-920**, e reserva até
> o requisito oito mil e noventa e nove, o critério dois mil setecentos e setenta e nove e o requisito
> de experiência novecentos e trinta e nove. Os tetos medidos em 15/11/2026 eram, na `main`, o
> requisito sete mil oitocentos e noventa e três, o critério dois mil seiscentos e cinquenta e nove e
> o requisito de experiência oitocentos e setenta e sete, todos da `174`; e, no PR aberto da migração
> do design system (#565, pasta `175`), faixas que começam no requisito sete mil e novecentos, no
> critério dois mil e setecentos e no requisito de experiência novecentos. As decisões reiniciam em
> `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-7150 da `166`"). Uma decisão de outra feature é citada pelo assunto e pela feature.
> As regras do estudo da verificação (`R-1` a `R-24`) e as pendências (`P-0` a `P-12`) são locais a
> ele, em `doc/estudo-verificacao-da-autodeclaracao-2026-11-13/`, e se citam por extenso.

---

## Por que esta feature existe

O roteiro da gravação tem quatro passos — documento, perfil esquerdo, perfil direito e de frente com
a fala — e a pessoa avança cada um tocando em "Próximo" (a FR-7869 da `174`). O toque resolve, mas
pede que a pessoa vire o rosto, olhe para a tela, ache o botão e toque, enquanto ainda tenta manter o
perfil para a câmera. Os aplicativos de banco que o público já conhece fazem diferente: pedem o
giro, percebem quando ele aconteceu, confirmam e passam ao seguinte. Para quem grava com o celular
apoiado, longe da mão, isso é a diferença entre gravar de uma vez e voltar à tela a cada passo.

**O obstáculo é normativo, e não técnico.** A FR-7150 da `166` e a R-19 do estudo dizem que o sistema
não analisa o vídeo de nenhuma forma, e um teste guardião recusa dependência de visão computacional
no projeto. Perceber o giro é estimar a pose do rosto a partir da imagem, e a imagem do rosto é dado
biométrico (LGPD, art. 5º, II, e art. 11). A regra existe para impedir que uma máquina participe do
juízo sobre a aparência da pessoa — a inferência racial é proibida em qualquer forma. Esta spec
revê a regra de forma estreita: **o aparelho pode estimar para onde o rosto aponta, só para guiar a
gravação, e nada dessa leitura sai do aparelho, fica guardado ou chega à comissão.** O servidor
continua sem analisar nada.

### O que esta spec cobre, e o que fica fora

| Cobre | Fica fora, e por quê |
|---|---|
| Perceber, no aparelho, se há um rosto no oval antes de começar | qualquer leitura de luz, nitidez, cor ou "qualidade" (R-19 do estudo) |
| Perceber, no aparelho, o giro para a esquerda e para a direita nos dois passos de perfil, e avançar sozinho | ler o que está no documento, conferir que ele é um documento ou comparar a foto dele com o rosto (reconhecimento facial) |
| Perceber, no aparelho, que a foto do documento apareceu e saiu do quadro, no passo 1, e avançar sozinho (emenda, D-009) | qualquer leitura do documento além de "há mais um rosto no quadro" |
| Dizer, no passo de frente, que o som da fala chegou (o nível que a `174` já mede) | terminar a gravação sozinha depois da fala; reconhecer o que foi dito |
| A revisão estreita da FR-7150 da `166`, da R-19 do estudo e da FR-7890 da `174`, e do guardião | qualquer análise no servidor, que continua proibida |
| A chave própria da detecção e a exceção de política de conteúdo que ela pede | ligar a detecção em produção: espera a P-0 e a validação da LGPD (P-13) |
| A imagem de teste do desenvolvimento, que passa a girar para os dois lados | "prova de vida" ou qualquer conferência de que a pessoa é quem diz ser |

**Nada muda no que é gravado e enviado** (FR-8030): o roteiro e a versão dele, as marcas, o formato,
o teto, o envio em partes, a retomada, o resumo, as rotas e as respostas. A regra de que o vídeo só
confirma (R-11 do estudo) não é tocada, e a Mesa não fica sabendo se um passo avançou pelo giro ou
pelo toque.

---

## Clarifications

### Session 2026-11-15 (restrições do pedido)

- **No aparelho, e só no aparelho.** Nada da análise sai do navegador nem é guardado; o servidor
  recebe o vídeo e as marcas, como hoje. A validação com a CPVA e com o encarregado de dados é
  pendência registrada (P-13), e não decisão desta spec.
- **A detecção é guia, e não portão.** "Próximo" continua sempre disponível. Quem usa Libras, tem
  limitação motora ou aparelho fraco grava como hoje. A detecção não decide nada do mérito e não é
  "prova de vida".
- **Servida pelo próprio sistema.** O modelo e o motor vêm da própria origem, sem rede de entrega de
  terceiros (`script-src 'self'`, `CLAUDE.md`); a página degrada para o toque quando não carregam.
- **A R-11 do estudo não muda**, nem o que é gravado, o envio em partes ou a Mesa.
- **Atrás da chave do vídeo**, recusada em produção, e de uma chave própria (D-004).

### Session 2026-11-15 (decisões do usuário)

- **Q-1 a Q-4: adotadas as recomendações.** Revisão estreita da regra da análise, só no aparelho e só
  no palco (D-001); só os dois perfis avançam sozinhos (D-002); ligado, com aviso e "Prefiro avançar
  só tocando" (D-003); o motor dos pontos do rosto, de cerca de 6,5 MB baixados uma vez (D-006).

### Session 2026-11-15 (emenda: menos texto na gravação)

- Depois do #573, o usuário avaliou a tela da gravação: *"tem muito texto durante a gravação… às vezes
  uma seta indicando já resolve"*. Das duas saídas apresentadas — só limpar e acrescentar a seta, com a
  frase em destaque; ou limpar e recolher a frase depois de alguns segundos, revendo a D-003 da `174` —,
  ele pediu **um meio-termo**: a frase do roteiro continua inteira e sempre à vista, mas nos passos de
  gesto deixa de ser o centro da tela, e o sinal visual passa a ser (FR-8050 a FR-8054, D-008).

### Session 2026-11-15 (emenda: o documento, a fala e o microfone)

- O usuário gravou com câmera real no Safari do macOS, no cenário C19, e pediu três coisas: que o passo
  do documento também avance sozinho; que o texto do passo de frente pare de cobrir o rosto — ele tapa a
  testa e os olhos e corta o fim, "Libras" pela metade —; e que o medidor do microfone se mexa quando a
  pessoa fala.
- **Q-5 e Q-6: adotadas as recomendações.** O documento avança quando a foto dele apareceu como um
  segundo rosto e saiu, ficando o da pessoa (D-009); a frase do roteiro continua inteira, e desce para
  junto do botão, com a frase a dizer em destaque (D-010). O medidor é defeito, e não pergunta: a FR-7873
  da `174` já pedia que ele se mexesse e que ficasse pequeno no selo durante a gravação (D-011).

### Perguntas ao usuário (decididas em 15/11 pelas recomendações abaixo)

#### Q-1 — Como fica a regra de que o sistema não analisa o vídeo?

A FR-7150 da `166` proíbe "detecção de rosto" e exige um guardião contra visão computacional "no
projeto"; a FR-7890 da `174` repete a proibição para o palco. Perceber o giro é exatamente isso.

| Opção | O que é | Implicações |
|---|---|---|
| **A (recomendada)** | Revisão estreita: o **aparelho** pode estimar a direção do rosto **enquanto o palco está aberto**, só para guiar; nada da leitura sai, é guardado ou é mostrado à comissão; o **servidor** continua proibido de analisar. O guardião passa a admitir **um** motor, fixado por versão e resumo, servido só na página da gravação | A garantia que importa — nenhuma máquina participa do juízo — fica intacta e verificável. A palavra "nenhuma análise" deixa de ser absoluta, o que a CPVA precisa conhecer (P-13) |
| B | A detecção só como protótipo em `doc/`, fora do sistema, para levar à CPVA antes de qualquer revisão | Nada muda nas regras agora; o usuário não vê a gravação "como no banco" no GPS até a CPVA responder |
| C | Manter a FR-7150 como está e não fazer a detecção | O A-1 da `174` fecha como recusado; a gravação continua só pelo toque |

#### Q-2 — O que avança sozinho?

A FR-7112 da `166` diz que os passos avançam "pelo toque ou pelo teclado", e a R-21 do estudo, "por
toque ou teclado, e não por relógio". A detecção não é relógio, mas também não é toque.

| Opção | O que é | Implicações |
|---|---|---|
| **A (recomendada)** | **Os dois perfis avançam sozinhos** quando o giro é percebido, depois de um instante de confirmação na tela; o documento e o passo de frente continuam pelo toque, e o passo de frente só mostra que a fala chegou. "Próximo" está sempre lá | É o fluxo do banco que o usuário descreveu, onde ele é seguro. Revê a FR-7112 da `166` e a R-21 do estudo só nos perfis. Ninguém termina a gravação sem querer, e a fala em Libras ou por papel não é apressada |
| B | Nada avança sozinho: o giro percebido só mostra "Perfil visto" e a pessoa toca "Próximo" | Nenhuma regra de avanço muda; o toque continua necessário, que é o incômodo do pedido |
| C | Avançam os perfis **e** a gravação termina sozinha depois da fala | Não recomendado: quem fala em Libras, mostra o papel ou pausa para pensar teria a gravação encerrada no meio |

#### Q-3 — A pessoa escolhe se quer o avanço pelo giro?

A LGPD pede que o tratamento de dado sensível seja informado (art. 9º) e tenha base legal (art. 11).
Nada sai do aparelho, mas a imagem do rosto é lida por uma máquina, ainda que só ali.

| Opção | O que é | Implicações |
|---|---|---|
| **A (recomendada)** | **Ligado, com aviso e desligamento a um toque**: antes de começar, o palco diz o que a tela faz e que nada sai do aparelho, com "Prefiro avançar só tocando" ao lado | Funciona como o banco, sem passo a mais, e quem não quer não usa. Se a CPVA ou o encarregado pedirem consentimento expresso, a troca para a opção B é de padrão, e não de desenho |
| B | **Desligado até a pessoa ligar**: "Quer que a tela avance sozinha quando vir o seu giro?" | Consentimento explícito; um toque a mais, e a maioria tende a não ligar |
| C | Ligado, sem escolha, só com o aviso | Mais simples; quem não quer a leitura do rosto não tem como recusá-la, e precisa ignorar a tela |

#### Q-4 — Qual motor, e quanto ele pesa?

O motor tem duas partes: o programa que roda o modelo (cerca de **2,8 MB** a baixar, comprimido; 14,7
MB no disco, na versão medida antes da pergunta) e o modelo. Os dois candidatos, da mesma família, de
licença Apache 2.0:

| Opção | O que é | Implicações |
|---|---|---|
| **A (recomendada)** | **Os pontos do rosto** (modelo de 3,8 MB): dá o ângulo do giro diretamente, e acompanha o rosto até perto do perfil inteiro | **Cerca de 6,5 MB** baixados uma vez e guardados no navegador. Mais confiável no perfil, que é o que o roteiro pede ("até a câmera ver o seu perfil") |
| B | **O detector de rosto** (modelo de 0,23 MB): seis pontos (olhos, nariz, boca, orelhas), de que se calcula o giro | **Cerca de 3,2 MB**. Perde o rosto antes do perfil inteiro, e o giro sai mais grosseiro; o limiar precisa ser menor que o do roteiro |

Nos dois, o motor só é baixado **depois** que a câmera abriu, enquanto a pessoa se vê no palco, e
nunca quando o aparelho pede economia de dados (FR-8018).

#### Q-5 — Quando o passo do documento avança sozinho? (emenda)

O mesmo motor dos pontos do rosto encontra até dois rostos por quadro, e a foto do documento, perto da
câmera, é um rosto a mais. Nenhum modelo novo. O roteiro diz «Mostre o seu documento de identidade com
foto perto da câmera, e depois o seu rosto».

| Opção | O que é | Implicações |
|---|---|---|
| **A (recomendada)** | **Visto e depois saiu**: um segundo rosto aparece por um instante, depois sai, e fica só o da pessoa; a tela diz "Documento visto" e o passo avança | Cumpre o "e depois o seu rosto". Quem está ao fundo desde o começo não conta, porque o segundo rosto precisa *aparecer*; quem fica não deixa o passo terminar. O documento que cobre o rosto não é percebido, e o toque resolve |
| B | **Assim que aparecer**: avança quando o segundo rosto fica um instante | Mais rápido; o perfil começa com o documento na mão, e uma pessoa ao fundo avança o passo |
| C | **Só confirma**: "Documento visto", e a pessoa toca | Nenhuma regra de avanço muda no documento; o toque que incomoda continua |

#### Q-6 — Onde fica a frase do passo de frente? (emenda)

A frase do passo de frente tem cerca de 250 caracteres (o A-4 da `174`). Sobre o vídeo, no alto, ela
cobre a testa e os olhos — que são o que a comissão olha — e a faixa de altura fixa a corta. A D-003 da
`174` e a FR-8051 exigem a frase inteira e à vista, e encurtá-la é versão nova do roteiro, que muda o
que é enviado (FR-8030).

| Opção | O que é | Implicações |
|---|---|---|
| **A (recomendada)** | **A frase inteira embaixo**: no alto, só "Passo 4 de 4 · De frente"; a frase do roteiro desce inteira para uma faixa junto do botão, fora do rosto, com o que se diz em destaque e altura que acompanha o texto. O "Antes de gravar" ganha uma linha sobre o papel e a Libras | Nenhuma regra muda: a frase é a do roteiro, inteira e à vista. O que muda é o lugar, e a faixa de baixo cresce no celular |
| B | **Uma linha curta**: no alto, "Diga o seu nome e a frase da sua autodeclaração"; embaixo, só a frase a dizer; papel, Libras e CPF só no preparo | Revê a D-003 da `174` e a FR-8051: a pessoa deixaria de ver na gravação o texto que a comissão lê como "o que o candidato viu" |
| C | **Só corrigir o corte**: a frase no alto, menor, sem altura fixa | Para de cortar; continua cobrindo a testa e os olhos |

---

## User Scenarios & Testing *(mandatory)*

Os cenários usam o C18 dos cenários de treinamento (`171`), com a chave do vídeo e a da detecção
ligadas no desenvolvimento, e uma inscrição na Modalidade que a Etapa restrita alcança, dentro do
período.

### User Story 1 — Gravar os perfis sem tocar na tela (Priority: P1)

Uma candidata apoia o celular na mesa, abre o palco, encaixa o rosto no oval e vê "Rosto no oval".
Toca em "Começar a gravar", mostra o documento e toca em "Próximo". A tela pede o perfil esquerdo;
ela vira o rosto, a tela confirma "Perfil esquerdo visto" e passa sozinha ao direito; ela vira para
o outro lado, a tela confirma e passa ao passo de frente; ela fala a frase e toca em "Terminar a
gravação".

**Why this priority**: é o pedido do usuário, e o caminho em que o toque mais atrapalha.

**Independent Test**: no computador, com câmera real e com a imagem de teste, e num celular real,
contando os toques entre "Começar a gravar" e "Terminar a gravação".

**Acceptance Scenarios**:

1. **Given** o palco aberto e o motor carregado, **When** o rosto está dentro do oval, **Then** o oval
   muda de estado e a frase diz "Rosto no oval", sem cor sozinha (FR-8010, UX-922).
2. **Given** o passo "Perfil esquerdo" em curso, **When** a pessoa vira o rosto para a esquerda dela
   e o mantém virado por um instante, **Then** a tela mostra "Perfil esquerdo visto" e, logo depois,
   passa ao passo seguinte, anunciado ao leitor de tela como no toque (FR-8011, FR-8012).
3. **Given** o passo "Perfil direito" em curso, **When** o giro para a direita é percebido, **Then**
   a tela confirma e passa ao passo de frente (FR-8011).
4. **Given** o passo de frente, **When** a pessoa fala, **Then** a tela diz "Estamos ouvindo você", e
   a gravação só termina em "Terminar a gravação" (FR-8013).
5. **Given** a gravação enviada, **When** a comissão a abre na Mesa, **Then** as marcas são as de
   sempre, uma por passo, e nada indica como cada passo avançou (FR-8030, FR-8031).

---

### User Story 2 — Gravar como hoje, quando a detecção não serve (Priority: P1)

Um candidato com limitação motora no pescoço não consegue virar o rosto até o perfil. Outro usa um
celular antigo, em que o motor não carrega a tempo. Uma terceira pessoa prefere não ter o rosto lido
pela tela. Os três gravam como hoje, tocando em "Próximo", sem mensagem de erro e sem esperar.

**Why this priority**: a acessibilidade não pode depender da detecção (R-21 do estudo).

**Independent Test**: o palco com o motor bloqueado, com a detecção desligada pela pessoa e com um
giro parcial, do começo ao envio.

**Acceptance Scenarios**:

1. **Given** o motor que não carregou, **When** o palco abre, **Then** tudo é como na `174`: "Próximo"
   a cada passo, sem aviso de falha (FR-8016).
2. **Given** o passo de perfil, **When** a pessoa não vira o suficiente, **Then** nada a apressa,
   nenhum erro aparece, e "Próximo" avança como sempre (FR-8014).
3. **Given** "Prefiro avançar só tocando" escolhido, **When** a gravação começa, **Then** o motor não
   lê nenhum quadro, e a tela não fala de giro (FR-8005, D-003).
4. **Given** o passo de frente em Libras, **When** a pessoa leva o tempo que precisar, **Then** nada
   avança nem termina sozinho (FR-8013).

---

### User Story 3 — Saber o que a tela faz com o rosto (Priority: P2)

Antes de começar, a candidata lê, no palco, que a tela acompanha o giro do rosto para avançar sozinha,
que isso acontece só no aparelho e que nada dessa leitura é enviado nem guardado — e que pode
desligar.

**Why this priority**: é o dever de informar da LGPD (art. 9º), e é o que dá confiança.

**Independent Test**: o palco antes de começar, a 375 e a 1280 px, com e sem o motor carregado.

**Acceptance Scenarios**:

1. **Given** o palco antes de começar, com a detecção disponível, **When** ele abre, **Then** a frase
   sobre a leitura do rosto e o controle para desligá-la estão à vista, sem rolar no celular (FR-8004,
   FR-8005).
2. **Given** a detecção indisponível (chave desligada ou motor sem carregar), **When** o palco abre,
   **Then** a frase e o controle não aparecem, e o palco é o da `174` (FR-8016).

---

### User Story 4 — Verificar sem câmera, no desenvolvimento (Priority: P3)

Quem desenvolve ou valida usa a imagem de teste: o vulto cinza gira para um lado e para o outro, e a
detecção simulada lê o giro desenhado — e não a imagem —, de modo que a jornada inteira pode ser
conferida sem gravar ninguém.

**Why this priority**: sem isso a detecção só se verifica com rosto real, e a verificação no
navegador da `174` deixaria de cobrir o palco.

**Independent Test**: o palco com a imagem de teste, no navegador do desenvolvimento, do começo ao
envio, sem nenhum toque nos perfis.

**Acceptance Scenarios**:

1. **Given** a imagem de teste, **When** o passo de perfil esquerdo está em curso, **Then** o vulto
   gira e a tela avança sozinha, como com rosto real (FR-8040).
2. **Given** a imagem de teste em produção, **When** se tenta usá-la, **Then** ela não existe — como
   hoje (a `166`).

---

### User Story 5 — Mostrar o documento sem tocar na tela (Priority: P1, emenda)

A candidata começa a gravar, aproxima o documento da câmera, ao lado do rosto, e vê "Documento visto".
Ela abaixa o documento, a câmera volta a ver só o rosto dela, e a tela passa sozinha ao perfil
esquerdo.

**Why this priority**: é o primeiro passo, e era o único gesto da gravação que ainda pedia toque.

**Independent Test**: com câmera real e um documento com foto; com a imagem de teste, cujo ciclo
mostra um segundo vulto pequeno; e com o motor sem rosto, pelo toque.

**Acceptance Scenarios**:

1. **Given** o passo "Documento" em curso, **When** a foto do documento aparece ao lado do rosto por
   um instante, **Then** a tela diz "Documento visto", e o sinal do documento sai (FR-8061, FR-8063).
2. **Given** o documento visto, **When** ele sai do quadro e o rosto da pessoa fica sozinho por um
   instante, **Then** a tela passa ao perfil esquerdo, anunciado como no toque (FR-8062).
3. **Given** uma pessoa ao fundo desde o começo do passo, **When** a candidata mostra o documento,
   **Then** nada avança sozinho, e "Próximo" resolve (FR-8064).
4. **Given** o documento na frente do rosto, cobrindo-o, **When** o passo segue, **Then** nada avança
   e nenhum erro aparece (FR-8064).

---

### User Story 6 — Ler a frase sem cobrir o rosto (Priority: P1, emenda)

No passo de frente, com o celular em pé, o candidato vê o próprio rosto inteiro, com "Passo 4 de 4 ·
De frente" no alto, e lê, embaixo, junto do botão, a frase inteira, com «Eu me autodeclaro pessoa
preta» e «pessoa parda» em destaque.

**Why this priority**: a comissão olha o rosto, e o texto o cobria no passo em que ele mais importa;
e a frase cortada escondia a alternativa da Libras.

**Independent Test**: a 375 px em retrato e a 1280 px, com a imagem de teste, medindo a faixa da
frase contra a altura do palco e conferindo que ela não rola nem corta.

**Acceptance Scenarios**:

1. **Given** o passo de frente em curso, **When** a pessoa olha a tela, **Then** a faixa de cima tem
   só o "Passo 4 de 4 · De frente" e o selo, e a frase inteira está embaixo, sem rolagem (FR-8070,
   FR-8071).
2. **Given** a frase embaixo, **When** se lê o texto, **Then** é o do roteiro, palavra por palavra, e
   as frases entre aspas estão em destaque (FR-8072).

---

### User Story 7 — Ver o microfone responder (Priority: P2, emenda)

Antes de começar, a candidata fala e vê a barra do microfone subir com a voz e passar da marca de
"volume bom"; durante a gravação, um indicador pequeno, junto do selo, continua mostrando que o
som chega.

**Why this priority**: o medidor parado faz a pessoa achar que o microfone não funciona, e gravar
três minutos sem som é perder a tomada.

**Independent Test**: com câmera real no Safari e no Chrome, e com a imagem de teste, cujo tom
sintético move a barra.

**Acceptance Scenarios**:

1. **Given** o palco antes de começar, **When** a pessoa fala em voz normal, **Then** a barra sobe
   rápido, desce devagar e passa da marca, e a frase diz "Estamos ouvindo você" (FR-8080 a FR-8082).
2. **Given** a gravação em curso, **When** a pessoa fala, **Then** o indicador pequeno do selo se
   mexe (FR-8083).

---

### Edge Cases

- **Giro para o lado errado** (a confusão do espelho): a tela diz, sem tom de erro, "Para o outro
  lado", e o leitor de tela também; a espera continua, e nada é registrado. Só depois de o rosto
  passar pela frente: quem acabou de ter um perfil visto ainda está virado para aquele lado quando o
  passo seguinte começa.
- **O rosto sai do oval no meio do passo**: a tela volta a esperar o giro; o "Rosto no oval" não é
  pedido durante a gravação.
- **Duas pessoas no quadro**: a detecção considera só o rosto maior, e não avisa nada; a comissão vê
  o vídeo como ele é.
- **Giro rápido e volta**: o giro precisa ser mantido por um instante (FR-8011); um relance não
  avança.
- **A pessoa toca em "Próximo" ao mesmo tempo em que o giro é percebido**: conta um avanço só, como o
  toque duplo da FR-7870 da `174`.
- **O motor carrega depois que a gravação começou**: ele não aquece nem lê durante aquela tomada —
  o aquecimento congelaria a página por segundos — e passa a guiar a partir do próximo preparo.
- **O aparelho fica lento**: se a leitura de um quadro passar do orçamento (FR-8017), a detecção
  desliga até a página ser recarregada, sem aviso, e a gravação segue pelo toque — o aparelho lento
  numa tomada é lento na seguinte, e tentar de novo custaria outro aquecimento.
- **Óculos, barba, véu, cabelo no rosto, pouca luz**: a detecção pode não perceber; o toque resolve,
  e nenhuma frase culpa a aparência ou a luz da pessoa (R-19 do estudo).
- **A tela some no meio** (troca de aplicativo): a tomada é descartada como hoje (a FR-7115 da `166`),
  e a detecção para com ela.
- **Celular deitado**: o giro é lido do mesmo jeito; a orientação não muda nada da detecção.
- **Movimento reduzido**: a confirmação aparece sem animação (a FR-7879 da `174`).
- **Leitor de tela**: a confirmação "Perfil esquerdo visto" e o passo novo são anunciados como no
  toque (UX-875 da `174`), e o foco continua em "Próximo".
- **Economia de dados ligada no aparelho**: o motor não é baixado; o palco é o da `174`.
- **Regravar**: ao sair do palco o vigia para de ler e esquece as leituras (FR-8003); o motor fica na
  página, e a detecção recomeça do oval, sem baixar nem aquecer de novo.
- **Chave da detecção ligada e a do vídeo desligada**: nada aparece; a do vídeo continua mandando.
- **(emenda) Documento que cobre o rosto**: a câmera vê um rosto só — o da foto —, e nada é percebido;
  "Próximo" resolve. A detecção não sabe qual dos rostos é o do documento e não tenta saber.
- **(emenda) Alguém passa ao fundo durante o documento**: o segundo rosto aparece e sai como um
  documento, e o passo pode avançar. A marca do passo seguinte fica uns segundos antes do que deveria;
  a comissão vê o vídeo inteiro, e a marca só ajuda a achar o trecho.
- **(emenda) Documento sem foto, ou foto pequena demais para o motor**: nada é percebido; o toque
  resolve. Nenhuma frase culpa o documento.
- **(emenda) Microfone mudo ou sem permissão**: a barra fica no zero, e a frase da `174` ("Fale alguma
  coisa…") continua; sem faixa de áudio, a frase de sem microfone, como hoje.

## Requirements *(mandatory)*

### Functional Requirements

#### O que a detecção pode ler, e onde

- **FR-8000**: A estimativa da direção do rosto DEVE acontecer **só no aparelho** da pessoa, na página
  da gravação, enquanto o palco está aberto. Nenhum quadro, ponto do rosto, ângulo, contagem ou
  resultado da detecção DEVE ser enviado ao servidor, guardado no aparelho além da memória da página,
  ou mostrado a qualquer outra pessoa.
- **FR-8001**: A detecção DEVE produzir só quatro leituras: se há um rosto dentro do oval; para que
  lado e quanto ele está virado; se o giro pedido foi mantido; e, no passo do documento, **quantos**
  rostos há no quadro (emenda, FR-8060). NÃO DEVE ler cor, tom de pele, luz, nitidez, expressão,
  idade, gênero, identidade nem qualquer "qualidade" (R-19 do estudo).
- **FR-8002**: O servidor NÃO DEVE analisar o vídeo de nenhuma forma, como hoje (a FR-7150 da `166`).
  A revisão desta spec (Q-1, D-001) alcança só o aparelho e só o palco.
- **FR-8003**: A detecção NÃO DEVE funcionar fora do palco: nem na revisão, nem no "assistir ao
  vídeo" do comprovante, nem na Mesa. Ao sair do palco, o motor DEVE parar de ler quadros e soltar o
  que guardou na memória.

#### O que a pessoa sabe e escolhe

- **FR-8004**: Com a detecção disponível, o palco DEVE dizer, antes de "Começar a gravar": "A tela
  percebe quando você mostra o documento e quando vira o rosto, para passar sozinha aos passos
  seguintes. Ela não lê o documento. Isso acontece só neste aparelho: nada dessa leitura é enviado nem
  guardado." (texto revisto pela emenda, D-009; antes, só o giro).
- **FR-8005**: Ao lado dessa frase, o palco DEVE oferecer "Prefiro avançar só tocando" (Q-3, D-003).
  Escolhido, o motor NÃO DEVE ler nenhum quadro até a página ser recarregada, e o palco DEVE voltar a
  ser o da `174`. A escolha vale para a página, e não é guardada.
- **FR-8006**: Nenhuma frase do candidato DEVE chamar a detecção de "prova de vida", "reconhecimento",
  "verificação facial" ou "biometria", nem sugerir que ela decide algo. A detecção é descrita pelo
  que faz: "a tela acompanha o giro do seu rosto".

#### O guia, passo a passo

- **FR-8010**: Antes de começar, com o motor carregado, o oval DEVE ter dois estados: "Encaixe o rosto
  no oval" e "Rosto no oval". A mudança DEVE ser dita em palavra, e não só por cor. O rosto no oval
  NÃO DEVE ser condição para "Começar a gravar".
- **FR-8011**: Nos passos "Perfil esquerdo" e "Perfil direito", a detecção DEVE perceber o giro para o
  lado da **pessoa** — e não o da imagem espelhada — quando ele passar do limiar do giro e for mantido
  por um instante (D-005). O limiar e o instante DEVEM ser os mesmos para todos, e estar escritos num
  só lugar.
- **FR-8012**: Percebido o giro, a tela DEVE mostrar "Perfil esquerdo visto" ou "Perfil direito visto"
  sobre a prévia e, depois de um instante de confirmação, passar sozinha ao passo seguinte, com a marca
  no instante da passagem, exatamente como o toque (Q-2, D-002). O anúncio ao leitor de tela DEVE ser
  o mesmo do toque (UX-875 da `174`), precedido da confirmação.
- **FR-8013**: O passo de frente NÃO DEVE avançar sozinho; o do documento avança só pela regra da
  FR-8062 (emenda, D-009 — antes, nenhum dos dois avançava). No passo de frente,
  quando o som passar do nível de fala, a tela DEVE dizer "Estamos ouvindo você" — a mesma leitura de
  nível que a `174` já faz antes de começar (a FR-7873 da `174`), sem reconhecer palavras. A gravação
  DEVE terminar só em "Terminar a gravação" ou no teto.
- **FR-8014**: Sem giro percebido, nada DEVE mudar: nenhum erro, nenhuma contagem, nenhum aviso de
  tempo. "Próximo" DEVE estar sempre disponível e avançar como na `174`, inclusive nos perfis. Um toque
  e um giro percebidos a menos de meio segundo DEVEM contar como um avanço (a FR-7870 da `174`).
- **FR-8015**: Giro para o lado oposto ao pedido, mantido pelo mesmo instante, DEVE mostrar "Para o
  outro lado", sem som, sem cor de erro e sem registro, e a espera continua.

#### Quando a detecção não está

- **FR-8016**: O motor DEVE ser baixado **depois** que a câmera abriu, sem atrasar o palco, e só uma
  vez por navegador enquanto não mudar de versão. Se ele não carregar — rede, aparelho sem suporte,
  memória, economia de dados, chave desligada —, o palco DEVE ser o da `174`, sem aviso de falha e
  sem as frases da detecção.
- **FR-8017**: A leitura DEVE ter orçamento: no máximo uma leitura por intervalo fixo, e, se a leitura
  de um quadro passar do teto de tempo várias vezes seguidas, a detecção DEVE desligar até a página
  ser recarregada, sem aviso. A detecção NÃO DEVE degradar a gravação: o vídeo gravado com ela ligada DEVE
  ter a mesma fluidez que sem ela (SC-2753).
- **FR-8018**: Com o aparelho pedindo economia de dados, o motor NÃO DEVE ser baixado.

#### A chave e a política de conteúdo

- **FR-8020**: A detecção DEVE ficar atrás de uma chave própria, desligada por padrão, que só vale com
  a chave do vídeo ligada; desligada, a página DEVE ser a da `174`, byte a byte no que é enviado (D-004).
- **FR-8021**: A produção DEVE recusar subir com a chave da detecção ligada, como recusa a do vídeo,
  até a P-0 e a P-13 serem resolvidas.
- **FR-8022**: Com a chave ligada, a política de conteúdo da página da gravação DEVE acrescentar só o
  que o motor exige para rodar — a compilação de WebAssembly da própria origem — e nada mais: sem
  origem externa, sem script embutido, sem `unsafe-eval`. As demais páginas NÃO DEVEM mudar. Com a
  chave desligada, a política é a de hoje (a FR-7117 da `166`, a FR-7889 da `174`).
- **FR-8023**: O motor e o modelo DEVEM ser servidos pela própria origem, de versão fixada, com o
  resumo de cada arquivo registrado e conferido por teste, e com a licença ao lado.
- **FR-8024**: O guardião da FR-7150 da `166` DEVE continuar recusando visão computacional no servidor
  — no lock, no que se declara e no código — e DEVE passar a recusar também qualquer motor de visão no
  navegador que não seja o desta spec, na versão e no resumo registrados, e em qualquer página além da
  gravação.

#### O sinal do gesto, e menos texto na gravação (emenda de 15/11)

Valem com ou sem a detecção: o sinal é navegação, como o "Passo N de 4", e não leitura do rosto.

- **FR-8050**: Durante a gravação, os passos de gesto DEVEM mostrar sobre a prévia um sinal visual
  grande, com uma palavra ao lado: no perfil esquerdo, uma seta para a esquerda da tela e "Sua
  esquerda"; no perfil direito, uma seta para a direita e "Sua direita"; no documento, o pictograma
  do documento e "Mostre o documento". A prévia é espelhada (a FR-7874 da `174`), e a esquerda da
  tela é a esquerda da pessoa. O passo de frente NÃO DEVE ter sinal: a frase dele é o que a pessoa
  fala.
- **FR-8051**: A frase do roteiro DEVE continuar inteira e à vista em todos os passos, sem recolher
  (a D-003 da `174`). Nos passos de gesto, ela DEVE vir em tamanho de leitura, e não grande: o sinal
  é o destaque, e a frase o apoio. No passo de frente, ela desce para junto do botão, com o que se
  diz em destaque (FR-8070 a FR-8072, emenda). Revê a "texto grande" da
  FR-7868 da `174` só nos passos de gesto (D-008).
- **FR-8052**: O oval NÃO DEVE aparecer durante a gravação: ele é o guia do enquadramento, antes de
  começar, e no meio do giro ocupava o centro da tela sem guiar nada.
- **FR-8053**: Com a detecção, "visto" DEVE substituir o sinal do perfil pela confirmação; e o sinal
  DEVE continuar apontando o lado pedido enquanto a tela diz "Para o outro lado".
- **FR-8054**: O sinal é decorativo para o leitor de tela (`aria-hidden`): o anúncio do passo, com a
  frase inteira, continua o mesmo (a UX-875 da `174`).

#### O documento (emenda de 15/11, Q-5, D-009)

- **FR-8060**: No passo do documento, a detecção DEVE contar quantos rostos o motor encontra no quadro,
  até dois — o mesmo motor e a mesma leitura dos perfis, sem modelo novo. NÃO DEVE ler o documento,
  conferir que ele é um documento, comparar a foto dele com o rosto da pessoa nem guardar a contagem
  além das leituras da FR-8000.
- **FR-8061**: Depois de ver o rosto da pessoa sozinho no passo, um segundo rosto que fique no quadro
  pelo instante da FR-8011 DEVE fazer a tela dizer "Documento visto", com o sinal de feito, no lugar
  do sinal do documento (FR-8053), e o leitor de tela DEVE ouvir a mesma frase.
- **FR-8062**: Visto o documento, quando o rosto da pessoa ficar sozinho no quadro pelo mesmo instante,
  a tela DEVE passar ao passo seguinte, depois do instante de confirmação, pelo mesmo caminho do toque
  e com a mesma marca (FR-8012).
- **FR-8063**: O sinal do documento DEVE continuar até o documento ser visto; e, visto, um segundo rosto
  que volte ao quadro DEVE adiar a passagem até ele sair de novo, sem frase nova.
- **FR-8064**: Sem a sequência inteira — o rosto sozinho, os dois, e o rosto sozinho de novo —, nada
  DEVE acontecer: nenhuma frase, nenhum erro. Dois rostos desde o começo do passo não contam. "Próximo"
  DEVE avançar como sempre, e o toque e a passagem a menos de meio segundo contam como um (FR-8014).
- **FR-8065**: Na imagem de teste, o ciclo DEVE mostrar, de forma previsível, um segundo vulto pequeno
  que aparece e sai, e a detecção simulada DEVE ler a contagem desenhada, e não a imagem (FR-8040).
- **FR-8066**: "Prefiro avançar só tocando" e a detecção indisponível DEVEM valer também para o
  documento: o passo volta a ser só pelo toque, sem frase.

#### A frase do passo de frente (emenda de 15/11, Q-6, D-010)

- **FR-8070**: No passo de frente, a frase do roteiro DEVE ficar **embaixo**, numa faixa junto de
  "Terminar a gravação", e não no alto: o alto, onde ficam a testa e os olhos, DEVE ter só o "Passo 4 de
  4 · De frente", o selo e o tempo. Nos passos de gesto, a frase continua no alto (FR-8051).
- **FR-8071**: A faixa da frase NÃO DEVE ter altura fixa, rolagem nem corte: ela cresce com o texto, em
  tamanho de leitura, e o palco DEVE caber na tela sem rolar a 375 px em retrato.
- **FR-8072**: A frase DEVE ser a do roteiro, inteira e palavra por palavra (a D-003 da `174`); as
  frases entre «aspas», que são o que se diz, DEVEM vir em destaque, maiores e em negrito, pela
  própria marcação das aspas no roteiro, sem texto acrescentado.
- **FR-8073**: O "Antes de gravar" DEVE ganhar, abaixo do teto, uma frase sobre o último passo: "No
  último passo, você diz o seu nome e a frase da sua autodeclaração. Se preferir, mostre a frase
  escrita num papel, ou diga em Libras." Os três itens do preparo continuam três (a FR-7863 da
  `174`).
- **FR-8074**: O anúncio ao leitor de tela DEVE continuar o mesmo, com a frase inteira (a UX-875 da
  `174`): muda o lugar na tela, e não o que se anuncia.

#### O medidor do microfone (emenda de 15/11, D-011)

- **FR-8080**: O medidor DEVE ser uma barra própria da página, e não o `<meter>` do navegador, cuja
  aparência nativa o Safari não redesenha com a altura ajustada pela folha. A largura DEVE mudar pela
  folha de estilo da página, sem estilo escrito no template (a política de conteúdo).
- **FR-8081**: A barra DEVE seguir o pico do som em decibéis, de modo que a fala em voz normal fique no
  meio dela, e não no começo; DEVE subir rápido e descer devagar, para não piscar.
- **FR-8082**: A barra DEVE ter uma marca de "volume bom" no nível em que a página passa a dizer
  "Estamos ouvindo você" (a FR-7873 da `174`), com a mesma régua: o que a marca mostra e o que a frase
  diz não podem divergir.
- **FR-8083**: Durante a gravação, um indicador pequeno do microfone DEVE ficar junto do selo, com a
  mesma leitura (a FR-7873 da `174`, que já o pedia). Ele é decorativo para o leitor de tela.
- **FR-8084**: A página DEVE pedir ao navegador que retome a leitura do som quando ela começar
  suspensa, e de novo no toque em "Começar a gravar".
- **FR-8085**: Nada do medidor DEVE entrar no que é gravado ou enviado: a barra é nível de sinal, lido
  no aparelho (a FR-7890 da `174`).

#### O que não muda

- **FR-8030**: Esta spec NÃO DEVE mudar o que é gravado nem o que é enviado: o roteiro e a versão dele,
  as marcas (uma por passo, na ordem), o formato, o teto, as partes, a retomada, o resumo, as rotas e
  as respostas. Os testes de contrato e de envio da `166` e da `174` DEVEM passar sem mudança.
- **FR-8031**: Nenhum sinal de como um passo avançou — pelo giro ou pelo toque — DEVE chegar ao
  servidor, à Mesa ou à trilha. A comissão julga o vídeo, e a R-11 do estudo continua: na dúvida,
  ao vivo.
- **FR-8032**: O guia NÃO DEVE entrar na gravação (a FR-7114 da `166`): nem o oval, nem a confirmação,
  nem pontos desenhados sobre o rosto. A página NÃO DEVE desenhar os pontos do rosto em nenhum
  momento.
- **FR-8033**: As frases novas DEVEM passar pela varredura de vocabulário do candidato (a FR-7331 da
  `171`).

#### A verificação

- **FR-8040**: No desenvolvimento, a imagem de teste DEVE girar o vulto para os dois lados, de forma
  previsível, e alimentar uma detecção simulada que lê o giro desenhado, e não a imagem, para que a
  jornada se verifique no navegador sem rosto e sem motor.
- **FR-8041**: A entrega DEVE ser verificada no navegador a 375 e a 1280 px com a imagem de teste, e,
  quando possível, com câmera real no computador e num celular; e DEVE registrar em `doc/` o que foi
  medido: o tempo até o motor carregar, o tempo por leitura e o peso baixado.
- **FR-8042**: A documentação da porta do piloto (a FR-7153 da `166`) DEVE ganhar a P-13: a validação
  da detecção com a CPVA e com o encarregado de dados, e o registro dela no relatório de impacto, antes
  de qualquer chave ligada em produção; e a compressão do motor no `nginx` da implantação, que hoje só
  comprime HTML.

### Requisitos de experiência

- **UX-920**: O tom da confirmação é o de um gesto bem feito, e não o de uma aprovação: "Perfil
  esquerdo visto", e não "Aprovado", "Correto" ou "Validado".
- **UX-921**: A confirmação fica sobre a prévia, na faixa da instrução, em texto grande, e dura o
  bastante para ser lida — o instante de confirmação da FR-8012 —, sem piscar.
- **UX-922**: Nenhum estado da detecção é dito só por cor: o oval muda de traço **e** a frase muda.
- **UX-923**: A ausência da detecção é invisível: quem grava sem ela não lê frase sobre ela, nem
  "falhou", nem "não foi possível".
- **UX-924**: Nenhuma frase atribui à pessoa a falha da detecção — luz, óculos, cabelo, véu, pele,
  movimento. Se a tela não percebe, o toque resolve, e é isso que a instrução já diz.
- **UX-925** (emenda): "Documento visto" tem o tom de "Perfil esquerdo visto" (UX-920): o gesto bem
  feito, e não "Documento válido", "conferido" ou "aceito" — a tela não sabe se ele é válido.
- **UX-926** (emenda): No passo de frente, o rosto inteiro — testa, olhos e boca — fica livre de texto
  no celular em pé, com o rosto no meio do quadro.
- **UX-927** (emenda): A barra do microfone se lê sem cor: o comprimento diz o volume, e a marca diz
  onde fica o bom.

### Key Entities

Nenhuma entidade nova, nenhum campo novo, nenhuma migration. A spec lê o roteiro da `166` (os passos
e as chaves deles, para saber quais são de perfil) e a configuração da página.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2750**: Com a detecção, a pessoa grava os quatro passos com **dois** toques além de "Começar a
  gravar" — o "Próximo" do documento e o "Terminar a gravação" —, contra quatro hoje, com câmera real
  e com a imagem de teste. *Revisto pela emenda: com o documento percebido, o toque é um só
  (SC-2760).*
- **SC-2751**: Sem a detecção (chave desligada, motor bloqueado ou "Prefiro avançar só tocando"), a
  jornada é a da `174` com o sinal do gesto da emenda (FR-8050 a FR-8052): os mesmos toques, as
  mesmas frases do roteiro, nenhuma frase da detecção à vista.
- **SC-2752**: O pedido de envio de um vídeo gravado com a detecção tem os mesmos campos, a mesma versão
  do roteiro e uma marca por passo na mesma ordem que o gravado sem ela; o teste compara os dois
  corpos chave a chave.
- **SC-2753**: Num computador de referência e num celular de entrada, a gravação com a detecção ligada
  não perde quadros perceptíveis: a duração do arquivo e o número de quadros por segundo ficam dentro
  de 5% dos da mesma gravação sem ela *(medido; registrado em `doc/`)*.
- **SC-2754**: Durante toda a gravação com a detecção ligada, a página não faz nenhum pedido de rede
  além dos que faz sem ela, fora o download do motor, que acontece no máximo uma vez.
- **SC-2755**: O peso baixado para a detecção não passa de 7 MB com o motor comprimido no transporte,
  como a implantação precisa servi-lo (Q-4, D-006, P-13), nem de 19 MB sem compressão, e o palco aparece no mesmo
  tempo com e sem ela (o motor não está no caminho do palco).
- **SC-2756**: Nenhuma página além da gravação carrega o motor ou tem a exceção de política de
  conteúdo dele; a política da gravação com a chave desligada é a de hoje, diretiva a diretiva.
- **SC-2757**: Num celular real, uma pessoa vira o rosto para os dois lados e a tela avança nos dois
  perfis sem toque *(humano)*.
- **SC-2759**: A 375 px, durante cada perfil, o sinal e a sua palavra ficam à vista sem rolar, o oval
  não aparece, e a frase do roteiro continua inteira na faixa de cima.
- **SC-2758**: Uma pessoa que não vira o rosto grava até o fim pelo toque, sem ver nenhuma frase de
  erro *(humano, ou simulado com o motor carregado e o vulto parado)*.
- **SC-2760** (emenda): Com a detecção, a pessoa grava os quatro passos com **um** toque além de
  "Começar a gravar" — o "Terminar a gravação" —, com a imagem de teste e com câmera real e documento.
- **SC-2761** (emenda): Com a imagem de teste, uma pessoa simulada ao fundo desde o começo do passo do
  documento não faz o passo avançar sozinho.
- **SC-2762** (emenda): A 375 px em retrato, no passo de frente, a faixa de cima não passa de um quarto
  da altura do palco (antes, a frase ocupava cerca de metade), a frase inteira está embaixo sem rolar
  (a altura rolável é igual à visível), e "Terminar a gravação" está à vista. No palco deitado, a
  frase fica ao lado do botão, e a faixa de baixo não passa do terço de baixo.
- **SC-2763** (emenda): Com a imagem de teste, cujo tom é constante e mais baixo que o nível de fala, a
  barra do microfone fica no meio — acima de um terço e abaixo da marca de "volume bom" —, e a frase
  não diz que ouviu: a marca e a frase concordam. Durante a gravação, o indicador do selo mostra a
  mesma leitura.
- **SC-2764** (emenda): Num Safari com câmera real, a barra sobe quando a pessoa fala e volta quando ela
  cala *(humano)*.

## Assumptions

- A `166`, a `171` e a `174` estão na `main` (15/11) e não mudam antes da implementação desta.
- O motor de referência é o da família de visão do MediaPipe, de licença Apache 2.0, que roda no
  navegador em WebAssembly, na versão **0.10.35**, que só busca o que a página lhe dá (D-007). A
  política de conteúdo recusaria de qualquer forma chamada a outra origem (`connect-src 'self'`).
- Os navegadores do público — Safari no iPhone, Chrome no Android e os três do computador, dos
  últimos dois anos — rodam WebAssembly e aceitam a diretiva que libera a compilação dele sem liberar
  `eval`. Onde não aceitarem, o motor não carrega e vale a FR-8016.
- O vídeo continua só fora de produção (P-0); esta spec não muda isso.
- O limiar do giro e o instante de confirmação são decisões de produto calibradas na verificação, e
  não regras do Edital.

## Out of Scope

- Ler o que está no documento, conferir que ele é um documento ou comparar a foto dele com o rosto
  (reconhecimento facial). A emenda percebe só que um rosto a mais apareceu e saiu (D-009).
- Terminar a gravação sozinha, reconhecer a fala ou transcrevê-la.
- Qualquer leitura de luz, enquadramento, nitidez ou "qualidade" (R-19 do estudo).
- "Prova de vida", antifraude ou conferência de identidade.
- Qualquer análise no servidor, na Mesa ou na revisão.
- Ligar o vídeo ou a detecção em produção (P-0, P-13).
- Um roteiro novo (P-8 do estudo).

## Dependências

- **`166`, `171` e `174`**, na `main` (#547, #551, #568).
- **A migração do design system** (#565, pasta `175`): não toca o portal; as duas não colidem.
- **O cenário de treinamento C19** com o vídeo (branch `claude/c19-verificacao-por-video`, em PR por
  outra sessão): não depende desta; com as duas na `main`, o C19 passa a mostrar a detecção quando a
  chave estiver ligada.

## Pendências (registro, e não escopo)

- **P-13 — A validação da detecção na LGPD.** A CPVA e o encarregado de dados precisam conhecer a
  revisão da FR-7150 da `166` (D-001), a base legal do tratamento (art. 11), a escolha da pessoa (Q-3)
  e o registro no relatório de impacto. Até lá, a chave fica recusada em produção (FR-8021). Esta spec
  não decide nada disso. A emenda acrescenta à P-13 a contagem de rostos no passo do documento
  (FR-8060): o motor lê também a foto do documento como rosto, sem comparar nada.

## Achados (registro, e não escopo)

- **A-1 — O motor 1.x manda medidas de uso ao Google.** A partir da 1.0.0, o `@mediapipe/tasks-vision`
  traz um registrador que envia, a cada minuto e ao fechar, o tipo da tarefa, o modo e as medidas de
  tempo a `odml.pa.googleapis.com`, com uma chave embutida. Nada da imagem vai junto. A jornada no
  navegador o pegou em 15/11 pela violação da política de conteúdo, que o recusou; a varredura de
  endereços feita no pacote antes da escolha tinha a saída cortada nas vinte primeiras linhas, e o
  endereço ficou de fora dela. A
  entrega ficou com a 0.10.35 (D-007), e um guardião recusa o registrador. Quem for atualizar o motor
  precisa saber que a versão nova volta a trazê-lo.
- **A-2 — O `nginx` do guia de implantação não comprime o motor.** Sem `gzip_types` para
  `application/wasm` e para o modelo, o navegador baixaria 15,4 MB em vez de cerca de 6,7. Vai para a
  porta do piloto (FR-8042), porque a implantação não liga a chave.

## Decisões

### D-001 — A regra da análise passa a separar o aparelho do servidor

Recomendação da Q-1. A FR-7150 da `166` e a R-19 do estudo protegem uma garantia: nenhuma máquina
participa do juízo sobre a aparência da pessoa. Uma estimativa do giro que nasce e morre na memória
do aparelho, que lê só a direção do rosto e que não chega a ninguém, não participa do juízo — a
comissão nem sabe que ela existiu (FR-8031). O que muda é a palavra "nenhuma": no servidor ela
continua absoluta; no aparelho ela passa a ter uma exceção, nomeada, fixada por versão e resumo, e
cobrada pelo guardião (FR-8024).

### D-002 — Só os perfis avançam sozinhos

*Revista em parte pela D-009 (emenda): o documento passou a avançar sozinho, pela contagem de rostos.
O passo de frente continua só pelo toque.*

Recomendação da Q-2. Nos perfis, o gesto pedido é exatamente o que a detecção percebe, e avançar é o
que o banco faz. No documento, a detecção teria de ler o documento, o que está fora (Out of Scope). No
passo de frente, avançar seria terminar a gravação, e a fala em Libras ou por papel tem a duração da
pessoa. A revisão da FR-7112 da `166` e da R-21 do estudo fica restrita aos dois perfis, e o toque
continua valendo em todos os passos.

### D-003 — Ligado, com aviso e desligamento a um toque

Recomendação da Q-3. O aviso cumpre o dever de informar, e o desligamento dá à pessoa o controle sem
custar um passo a quem quer a detecção. A escolha não é guardada, para não criar um dado novo sobre
a pessoa; quem recarrega a página vê o aviso de novo.

### D-004 — Uma chave própria, debaixo da do vídeo

A detecção tem pendência própria (P-13) e uma exceção de política de conteúdo própria (FR-8022), que
não devem valer só porque o vídeo vale. Com a chave própria, o vídeo pode seguir sem ela, e desligá-la
devolve a página da `174` sem tocar no resto.

### D-005 — O lado é o da pessoa

O roteiro diz "vire o rosto para a sua esquerda". A prévia é espelhada (a FR-7874 da `174`) e o
arquivo não; a detecção lê o giro no referencial da pessoa, e o teste o confere nos dois sentidos.
O giro mantido por um instante evita que um relance avance; o limiar e o instante são parâmetros
únicos, ajustados na verificação, e não uma exigência de amplitude — quem não alcança o perfil
inteiro toca em "Próximo".

### D-006 — O motor dos pontos do rosto

Recomendação da Q-4. O roteiro pede o perfil ("até a câmera ver o seu perfil"), e o detector leve perde
o rosto antes dele. Os pontos do rosto dão o ângulo do giro diretamente, e custam cerca de 6,5 MB a
mais, uma vez por navegador, baixados depois que a câmera abriu e nunca em economia de dados.

### D-007 — A versão 0.10.35 do motor, e não a 1.x

Achado A-1. A promessa é que nada sai do aparelho por causa da detecção (FR-8000), e a 1.x tenta mandar
medidas de uso para fora; a política de conteúdo a recusaria, mas o pedido recusado continuaria sendo
uma tentativa, visível a quem olha a rede, e a garantia passaria a depender de uma barreira só. A
0.10.35, de 27/04/2026, tem a mesma interface, é menor (11,2 MB no disco, cerca de 3,3 MB em gzip) e
só busca o modelo e o grafo, nos endereços que a página lhe dá. A política continua como segunda
barreira, e o guardião recusa o registrador em qualquer versão copiada.

### D-008 — O sinal do gesto à frente, e a frase do roteiro como apoio

O meio-termo pedido pelo usuário (emenda de 15/11). Recolher a frase rompia a D-003 da `174` — o vídeo
guarda a versão do roteiro, e a comissão lê o que o candidato viu —; mantê-la grande deixava o perfil
com oito coisas na tela, e uma pessoa com o rosto virado não lê três linhas. A frase continua inteira
e à vista, em tamanho de leitura; a seta diz o que fazer num relance. O passo de frente fica como
está, porque nele a frase é a fala.

### D-009 — O documento avança quando apareceu e saiu (emenda)

Recomendação da Q-5. A D-002 deixava o documento de fora porque a detecção "teria de ler o documento".
Não tem: a foto do documento é um rosto, e o motor que já roda nos perfis conta até dois. A regra pede
a sequência inteira — o rosto sozinho, os dois, o rosto sozinho de novo — por três razões: é o que o
roteiro pede ("e depois o seu rosto"); quem está ao fundo desde o começo nunca conta, porque o segundo
rosto precisa aparecer; e quem fica no quadro nunca deixa o passo terminar. O que a detecção não sabe
— qual dos rostos é o documento, se ele é um documento, se a foto é da pessoa — ela não tenta saber: isso
seria conferência de identidade, que está fora, e o toque continua resolvendo tudo o que ela não
percebe.

### D-010 — A frase do passo de frente desce para junto do botão (emenda)

Recomendação da Q-6. A garantia da D-003 da `174` é sobre o texto, e não sobre o lugar: o candidato vê,
durante a gravação, o roteiro inteiro, que é o que a comissão lê. No alto, a frase de 250 caracteres
cobria a testa e os olhos, que é o que a comissão olha; embaixo, perto do polegar, ela cobre o peito.
O destaque das frases entre aspas sai da marcação do próprio roteiro, de modo que nenhuma palavra é
acrescentada. Os passos de gesto continuam com a frase no alto, onde ela é curta e o sinal é o
destaque (D-008).

### D-011 — O medidor do microfone é refeito (emenda)

O defeito tem três causas que se somam, e nenhuma muda regra: a escala linear deixava a fala comum no
primeiro quinto da barra; o pico recalculado a cada quadro, sem suavização, piscava; e o `<meter>` do
Safari, com a altura ajustada pela folha, não acompanha o valor. A barra própria, em decibéis, com
subida rápida e descida lenta, resolve as três, e a marca de "volume bom" sai da mesma régua que decide
"Estamos ouvindo você" — a FR-7873 da `174` não muda, só passa a ser visível. O indicador no selo era
pedido pela FR-7873 e não tinha sido feito.
