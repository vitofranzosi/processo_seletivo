# Feature Specification: Conferência com o documento à vista

**Feature Branch**: `claude/confident-borg-92ee89`, sobre a `main` em `d1ec1e0a`

**Created**: 2026-11-11

**Status**: Draft — a Questão 4 respondida pelo usuário em 11/11/2026 (D-008); as Questões 1 a 3
abertas (ao fim, em "Questões para o usuário")

**Nenhuma regra nova.** Quem confere, o que o "conforme" exige, a recusa, a idempotência, os estados
e a trilha continuam os da `115`, da `131` e da `143`. Muda **onde** o arquivo aparece e **o que a
página faz** depois do registro: o arquivo ao lado do formulário, a conferência registrada sem
recarregar a página inteira, e o caminho ao próximo documento. Não há tabela, permissão, estado nem
evento de trilha novos. A única regra que muda é a do aviso de pendência, por decisão do usuário
na Questão 4: o gesto da `134` passa a admitir o recorte de uma pessoa, oferecido quando a
conferência dela termina, e a `134` é revista para isso, com a redação anterior preservada (D-008).

**Acréscimo de 11/11.** A sessão que coordena as specs do estudo pediu, depois da primeira versão,
que o achado 09 entrasse como questão, porque mexe no mesmo formulário: registrar a pendência não
avisa o candidato, e o aviso é outro gesto, na tela da convocação, seguido do despacho. A decisão do
usuário de 08/11 registrada na `134` — o aviso sai por gesto da comissão, nunca por evento — **não se
reverte aqui**. O usuário respondeu em 11/11 onde o gesto aparece (Questão 4, D-008).

**Input**: orientação do usuário, literal: *"escreva a spec para conferir o documento mantendo os
dados e os controles de análise visíveis, incluindo uso em telas pequenas e alternativa para arquivos
sem prévia."* A sessão que abriu esta acrescentou: o arquivo visível ao lado do formulário em tela
larga; o arranjo a 390 px sem perder os controles; a alternativa para o navegador que não renderiza
PDF, o arquivo grande e o arquivo corrompido, mantendo o registro de abertura; registrar sem
recarregar a página toda; passar ao próximo documento ou à próxima pessoa; teclado e leitor de tela;
reaproveitar o visualizador da Mesa; e nenhuma conferência em lote.

> **Faixa de identificadores.** Esta spec usa:
>
> - os requisitos funcionais de seis mil e quinhentos a seis mil quinhentos e quarenta e nove;
> - os critérios de dois mil cento e quarenta a dois mil cento e cinquenta e nove;
> - os requisitos de experiência de seiscentos e quarenta a seiscentos e cinquenta e nove.
>
> Os números não usados ficam livres. As decisões reiniciam em `D-001`. A reserva está nas notas
> compartilhadas das sessões de 11/11, ao lado das da `152` a `156`.
>
> **Como esta spec cita outras.** Requisito de outra feature, pelo identificador e pela feature ("a
> FR-3611 da `115`"); decisão de outra feature, pelo assunto, nunca pelo identificador.
>
> **Origem.** O
> [estudo da jornada final de 11/11/2026](../../doc/estudo-jornada-final-2026-11-11/index.html)
> (PR #472), achado 10 do inventário e passo C2 do percurso, sobre o cenário de treinamento C09 da
> `134`, com as capturas C03 e C04; e o achado 09 e o passo C3, com as capturas C10, C12 e D01. No
> estudo os achados levam o prefixo dos requisitos de experiência; aqui eles se escrevem "achado 10",
> para que a varredura de citações não os leia como requisitos desta spec.
>
> **O estado de partida.** Desde o #473, a recusa da conferência aparece no cartão do documento, com o
> que foi marcado e digitado, e o aviso *"Você ainda não abriu a versão N"* aparece antes do clique,
> ligado às opções que ele condiciona. A `154` (#479, mergeada em 11/11, ainda sem código) dá ao
> documento reenviado o nome *"Reenviado — aguardando nova conferência"* (FR-6211 da `154`). Esta spec
> **não nomeia estado**: o cartão mostra o rótulo vigente, o de hoje até a `154` ser implementada e o
> dela depois.

## Por que esta feature existe

Na página **Documentos da convocação** (FR-3608 da `115`, FR-5019 a FR-5024 da `143`), conferir um
documento custa quatro passos: *"Abrir"*, que leva o arquivo a uma aba nova; voltar à aba da
conferência; marcar *Conforme* ou *Pendente*; e *"Registrar conferência"*, que recarrega a página
inteira e devolve a pessoa ao cartão. No C09, Alice tem dois documentos; numa convocação com dezenas
de pessoas, são centenas de trocas de aba, e cada uma é ocasião de conferir o arquivo de uma pessoa
com a aba de outra. A página não ajuda a perceber o erro: a aba do arquivo não diz de quem ele é.

O "conforme" só se registra depois que o próprio conferente abriu, nesta chamada, a versão vigente
(FR-3611 da `115`; o "não se aplica", pela FR-4460 da `131`). Abrir é, portanto, mais que ler: é o
que autoriza o juízo. Isso pesa em tudo o que segue.

**A Mesa já resolveu metade disto** (FR-112 da `012`, telas da `077` e da `080`). Na Mesa do
avaliador, em tela larga, o documento abre num painel à esquerda, ao lado do formulário, com o nome do
documento, *"Abrir em aba própria"* e *"Fechar"* na barra. Três coisas que ela aprendeu valem aqui:

- **a abertura continua sendo um ato** — nada carrega sozinho ao entrar na página; é o clique sobre o
  documento que a trilha registra;
- **a entrega é a mesma** — a moldura carrega exatamente a resposta do link, com a conferência do
  resumo antes de sair um byte;
- **a aba própria fica à mão**, porque o visualizador do navegador encolhe a própria barra dentro da
  moldura, e girar ou ampliar é dele.

E duas coisas ela não resolve, e esta página precisa:

- **abaixo da tela larga, e sem script, a Mesa volta à aba própria.** Aqui o usuário pediu o uso em
  tela pequena sem perder os controles;
- **na Mesa, a abertura só informa; aqui ela autoriza.** Se a moldura pedir o arquivo a um navegador
  que não o desenha, o servidor registra a entrega, e a pessoa nada viu. Na Mesa isso é uma marca
  "aberto" imprecisa; aqui seria um "conforme" autorizado sobre um arquivo não visto.

**O que o código diz hoje**, lido em 11/11 na `main`:

- a rota do arquivo da convocação entrega sempre como PDF, `inline`, sem cache; confere o resumo
  antes de entregar; grava a consulta sob a apresentação quando confere, a recusa por integridade
  quando diverge, e o arquivo indisponível quando não lê (FR-3605 e FR-3606 da `115`, FR-3695 da
  `117`);
- **a rota não se deixa emoldurar**: a da Mesa declara a exceção da própria origem, e esta não;
- o envio aceita o arquivo pela assinatura de PDF, pelo tamanho — até 10 MB — e por não estar vazio.
  Um PDF truncado ou danificado passa, e só falha quando o navegador tenta desenhá-lo; o servidor não
  tem como saber;
- a política de conteúdo já permite moldura e objeto da própria origem, por causa da prévia do Edital
  e da Mesa; script e estilo escritos no template continuam recusados.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Conferir com o arquivo ao lado, em tela larga (Priority: P1)

A presidente abre os documentos de Alice. Clica em *"Abrir"* no diploma; o arquivo aparece num painel
ao lado da lista, com o nome do documento, a versão, o instante da apresentação e o nome de Alice na
barra. O cartão do diploma, com o formulário, continua à vista do outro lado. O aviso *"Você ainda não
abriu a versão 1"* dá lugar a *"aberto por você"*. Ela marca *Conforme* e registra — sem trocar de
aba.

**Why this priority**: é o achado 10 inteiro. Sem isto, nada do resto tem onde morar.

**Independent Test**: no C09, em janela de 1280 × 800, conferir o diploma de Alice sem sair da
página e sem trocar de aba; a trilha tem uma consulta à versão 1, e a conferência é aceita.

**Acceptance Scenarios**:

1. **Given** a página dos documentos de Alice, recém-aberta, **When** nada é clicado, **Then** nenhum
   arquivo é pedido ao servidor e a trilha não ganha consulta a apresentação.
2. **Given** a página em tela larga, **When** a presidente clica em *"Abrir"* no diploma, **Then** o
   arquivo aparece ao lado, a barra diz *"Diploma de graduação — versão 1, apresentada em 11/11/2026
   17:52"* e *"Alice Treinamento C09-01 · INS-2026-JM7DFQTG"*, o foco vai para o título do painel, e
   o cartão do diploma, com o formulário, fica à vista.
3. **Given** o diploma aberto no painel, **When** a entrega termina, **Then** o aviso de abertura do
   cartão dá lugar a *"aberto por você"*, lido da trilha, sem recarregar a página.
4. **Given** o diploma aberto no painel, **When** a presidente clica em *"Abrir"* no comprovante,
   **Then** o painel passa ao comprovante, a barra muda junto, e só o comprovante fica marcado como o
   aberto na lista.
5. **Given** o painel aberto, **When** a presidente clica em *"Fechar"*, **Then** o painel some e o
   foco volta ao formulário do documento que estava aberto.

---

### User Story 2 — Registrar sem recarregar a página (Priority: P1)

Com o diploma no painel, a presidente marca *Conforme* e registra. O cartão do diploma passa a
mostrar a conferência — autor, instante, resultado —, o resumo no alto conta um conforme, e a
*"Situação desta convocação"* diz o passo seguinte. O arquivo continua no painel.

**Why this priority**: a recarga é o quarto passo do achado 10, e com ela o painel aberto se perderia
a cada registro.

**Independent Test**: no C09, registrar o diploma de Alice e comparar o cartão, o resumo e a
situação com o que a página mostra recarregada; são iguais, e o painel não fechou.

**Acceptance Scenarios**:

1. **Given** o diploma aberto e *Conforme* marcado, **When** a presidente registra, **Then** a
   conferência é gravada pelo mesmo comando de hoje, o cartão, o resumo e a situação se atualizam, e
   a confirmação é anunciada.
2. **Given** o diploma **não** aberto e *Conforme* marcado, **When** a presidente registra, **Then** a
   recusa aparece no cartão com a frase de hoje, o que foi marcado e digitado continua, e o foco vai
   para a recusa.
3. **Given** uma versão nova enviada por Alice depois que a página abriu, **When** a presidente
   registra sobre a versão antiga, **Then** a recusa de versão superada aparece no cartão, o
   resultado marcado é desfeito, o motivo digitado fica, e o cartão oferece abrir a versão nova.
4. **Given** um desfecho registrado por outra pessoa depois que a página abriu, **When** a presidente
   registra, **Then** a recusa aparece no alto, e os formulários que deixaram de valer somem.
5. **Given** o clique duplo em *"Registrar conferência"*, **When** os dois pedidos chegam, **Then**
   existe uma conferência só.
6. **Given** o navegador sem script, **When** a presidente registra, **Then** a página funciona como
   hoje: grava, recarrega e volta ao cartão.

---

### User Story 3 — Quando o arquivo não aparece na página (Priority: P1)

Bernardo enviou um PDF danificado; Cecília enviou um de 9 MB; o conferente usa um navegador que não
mostra PDF dentro da página. Em todos os casos, a página diz o que aconteceu, oferece o que resta, e o
registro de abertura continua dizendo a verdade: o arquivo foi entregue a quem o abriu.

**Why this priority**: sem a alternativa, o painel transforma o registro de abertura em afirmação
falsa — e é esse registro que autoriza o "conforme".

**Independent Test**: com o navegador declarando que não mostra PDF embutido, o gesto de abrir não
pede o arquivo para a moldura; a página oferece a aba própria e o download; aberto por um deles, a
marca do cartão é relida ao voltar.

**Acceptance Scenarios**:

1. **Given** um navegador que não declara mostrar PDF dentro da página, **When** o conferente clica em
   *"Abrir"*, **Then** nenhuma moldura pede o arquivo, e o painel — ou o cartão, em tela pequena — diz
   que este navegador não mostra o documento dentro da página e oferece *"Abrir em aba própria"* e
   *"Baixar"*.
2. **Given** o documento aberto em aba própria pela alternativa, **When** o conferente volta à página,
   **Then** o cartão mostra *"aberto por você"*, relido da trilha, sem recarregar.
3. **Given** um arquivo cujo resumo diverge do guardado, **When** o conferente o abre no painel,
   **Then** o painel mostra, em texto, a frase da recusa por integridade de hoje, nenhuma consulta é
   registrada, o evento de integridade é registrado como hoje, e o aviso de abertura do cartão
   continua.
4. **Given** um arquivo indisponível, **When** o conferente o abre, **Then** o painel mostra a frase
   da FR-3695 da `117`, e o evento de arquivo indisponível é registrado, como hoje.
5. **Given** um arquivo de 9 MB, **When** o conferente o abre, **Then** o link já dizia o tamanho, e
   o painel diz que o documento está carregando até a moldura terminar.
6. **Given** um PDF danificado que o navegador não consegue desenhar, **When** o conferente o abre,
   **Then** a entrega é registrada — o servidor não distingue —, a barra continua oferecendo a aba
   própria e o download, e a ajuda do formulário diz que arquivo que não abre é motivo de pendência.

---

### User Story 4 — Conferir numa tela pequena (Priority: P2)

O conferente usa o celular, a 390 px. Abre o diploma de Alice, lê, e encontra o formulário do diploma
logo ali, com os dados de Alice e do documento à vista, sem perder o lugar.

**Why this priority**: o usuário pediu. A conferência é trabalho de mesa na maior parte das vezes, e
por isso não é P1.

**Independent Test**: a 390 px, no C09, conferir o diploma de Alice do começo ao fim sem rolagem
horizontal, sem que o arquivo cubra o formulário, e com a abertura registrada.

**Acceptance Scenarios** (o arranjo depende da Questão 2; os cenários abaixo valem para a proposta):

1. **Given** a 390 px e um navegador que mostra PDF dentro da página, **When** o conferente clica em
   *"Abrir"*, **Then** o arquivo aparece dentro do cartão do diploma, acima do formulário, com altura
   limitada, e o resultado e o botão de registrar continuam alcançáveis sem rolar o arquivo até o fim.
2. **Given** a 390 px e um navegador que não mostra PDF dentro da página, **When** o conferente clica
   em *"Abrir"*, **Then** o arquivo abre no visualizador do aparelho, e, ao voltar, o cartão do diploma
   está onde estava, com *"aberto por você"* e o foco no formulário dele.
3. **Given** a 390 px, **When** o conferente rola o cartão aberto, **Then** o nome do documento, a
   versão e o nome de Alice continuam identificáveis junto do arquivo, e nenhum controle fica atrás
   dele.
4. **Given** a janela que passa de larga a estreita com o painel aberto, **When** a largura cruza a
   fronteira, **Then** o arquivo passa ao arranjo estreito sem perder o que foi marcado e digitado, e
   sem pedir o arquivo de novo ao servidor.

---

### User Story 5 — Passar ao próximo documento ou à próxima pessoa (Priority: P2)

Registrado o diploma, a confirmação oferece *"Abrir o próximo a conferir: Comprovante de residência"*.
Registrado o comprovante, Alice não tem mais nada a conferir, e a confirmação oferece *"Próxima com
documento a conferir: Bernardo Treinamento C09-02"*.

**Why this priority**: tira o caminho de volta à lista, mas o achado 10 se resolve sem ele.

**Independent Test**: no C09, conferir os dois documentos de Alice e chegar aos de Bernardo só pelos
gestos oferecidos na confirmação, sem que nenhuma abertura aconteça sem clique.

**Acceptance Scenarios**:

1. **Given** o diploma registrado e o comprovante a conferir, **When** a confirmação aparece, **Then**
   ela oferece abrir o comprovante, nomeado, num gesto; o comprovante **não** abre sozinho.
2. **Given** o gesto de abrir o próximo, **When** ele é usado, **Then** o comprovante aparece no
   painel, e o foco vai ao título do painel com o formulário do comprovante à vista.
3. **Given** nada mais a conferir em Alice, **When** a confirmação aparece, **Then** ela oferece a
   próxima pessoa com documento a conferir, nomeada, pelo mesmo critério da FR-5024 da `143`; o gesto
   leva à página dela, com o painel fechado.
4. **Given** nada mais a conferir no recorte, **When** a confirmação aparece, **Then** ela diz que não
   há outro documento a conferir neste recorte e leva à convocação.
5. **Given** qualquer confirmação, **When** a presidente usa o gesto do próximo, **Then** nenhuma
   conferência é registrada por ele: cada conferência continua sendo um registro sobre um item.

---

### User Story 6 — Teclado e leitor de tela (Priority: P1)

Uma conferente que usa leitor de tela e só teclado confere os dois documentos de Alice. Ela ouve qual
documento abriu, ouve quando a abertura foi registrada, ouve a confirmação ou a recusa, e nunca perde
o foco para o alto da página.

**Why this priority**: a Constituição exige teclado e acessibilidade em toda interface, e a troca de
conteúdo sem recarga é justamente onde leitores de tela se perdem.

**Independent Test**: percorrer a US1, a US2 e a US5 no C09 só com teclado e com leitor de tela; o
roteiro de verificação humana registra o que foi ouvido em cada passo.

**Acceptance Scenarios**:

1. **Given** o foco em *"Abrir"*, **When** a conferente aciona com Enter, **Then** o foco vai ao
   título do painel, que diz o documento, a versão e a pessoa.
2. **Given** o painel aberto, **When** a conferente tabula, **Then** a ordem segue a ordem visual — o
   painel, depois a lista — e o foco nunca fica preso na moldura nem no painel.
3. **Given** um registro aceito ou recusado, **When** a página se atualiza, **Then** o leitor de tela
   anuncia uma vez a confirmação, ou a recusa recebe o foco, e o foco nunca cai no início da página.
4. **Given** o estado do item ou a marca do aberto, **When** lidos, **Then** eles se distinguem por
   texto, e não só por cor.

---

### User Story 7 — A pendência registrada, e o aviso à vista (Priority: P3)

O presidente confere os dois documentos de Bernardo: o comprovante, conforme; o "diploma", pendente,
porque é outro comprovante. Ao registrar a pendência, a confirmação diz que nenhum aviso foi pedido e
que Bernardo vê a pendência no portal. Terminada a conferência de Bernardo, a página mostra a situação
do aviso e oferece *"Pedir aviso para Bernardo"*. Ninguém sai da página achando que Bernardo foi
avisado.

**Why this priority**: é o achado 09, que a sessão coordenadora pediu para tratar aqui por tocar o
mesmo formulário. A `134` e a `143` já dão o gesto e a situação do envio; o ganho é de lugar e de
clareza, e o achado 10 se resolve sem ele.

**Independent Test**: no C09, registrar a pendência do diploma de Bernardo sem recarregar a página;
nenhum aviso é gravado pelo registro, a confirmação diz que nenhum aviso foi pedido, e a situação do
aviso na página é a mesma do cartão da convocação.

**Acceptance Scenarios**:

1. **Given** o diploma de Bernardo aberto, *Pendente* marcado e o motivo digitado, **When** o
   presidente registra, **Then** a conferência é gravada, nenhum aviso é gravado por ela, e a
   confirmação diz que nenhum aviso foi pedido e que Bernardo vê a pendência no portal.
2. **Given** a conferência de Bernardo terminada com uma pendência, **When** a confirmação aparece,
   **Then** a seção *"Situação desta convocação"* diz, sem recarga, que nenhum aviso foi registrado
   desde a pendência e se o gesto do aviso alcançaria Bernardo agora, ou por que não (FR-5017 da
   `143`).
3. **Given** um aviso registrado para Bernardo, **When** a página é lida antes do despacho, **Then**
   ela diz que o aviso foi registrado e ainda não foi enviado; depois do despacho, a situação do envio
   com as palavras da `066`, nunca "entregue" nem "lido" (FR-5016 da `143`).
4. **Given** a conferência de Bernardo terminada com pendência elegível, **When** a confirmação
   oferece *"Pedir aviso para Bernardo"* e o presidente o usa, **Then** é gravado um aviso pela regra
   da `134`, com todas as pendências elegíveis de Bernardo naquele instante, e a resposta diz *"Aviso
   solicitado; aguardando envio"*.
5. **Given** Bernardo já avisado hoje nesta chamada, **When** a conferência dele termina com nova
   pendência, **Then** a confirmação não oferece o gesto e diz por quê, e que o pedido poderá ser
   feito a partir de amanhã; nada é agendado.
6. **Given** a convocação de Bernardo com o vencimento decorrido, **When** a conferência termina com
   pendência, **Then** a confirmação diz que o aviso não cabe mais, sem data para tentar de novo.
7. **Given** o aviso pedido, **When** a página é lida depois do despacho, **Then** ela diz se o aviso
   foi enviado — aceito pelo servidor de correio — ou falhou, com o estado da `066`.
8. **Given** o gesto em lote da tela da convocação, **When** usado depois do pedido individual no
   mesmo dia, **Then** Bernardo fica de fora por já ter sido avisado hoje, como a `134` já faz.

### Edge Cases

- **Abrir um documento não autoriza outro.** A abertura do diploma não conta para o comprovante, nem a
  da versão 1 para a versão 2, nem a de uma referência noutra chamada (FR-3611 da `115`). Abrir os dois
  documentos com o mesmo arquivo — o caso de Bernardo, achado 11 do estudo — conta como duas
  aberturas, uma por apresentação.
- **Apresentação por referência** (o documento da inscrição aproveitado): abre no mesmo painel, e a
  abertura vale para ela nesta chamada.
- **Versão superada com o painel aberto.** A barra passa a dizer que a versão aberta foi substituída, e
  o cartão oferece abrir a vigente.
- **Item já julgado.** As versões anteriores e a vigente conferida continuam abríveis no painel, para
  leitura; o formulário recolhido, como hoje.
- **Página só de leitura** (chamada decidida, Processo encerrado, quem consulta sem poder conferir): o
  painel funciona para ler, e não há formulário.
- **Sessão expirada ou identidade trocada no meio.** O registro sem recarga diz que nada foi
  registrado, mantém à vista o que foi marcado e digitado, e oferece entrar de novo; nada se perde em
  silêncio.
- **Quem perdeu a alocação no meio** (FR-3597 da `115`): a recusa é a de hoje, no cartão.
- **Abrir no painel e depois em aba própria**: duas consultas na trilha, que é o que aconteceu.
- **Baixar**: continua ação secundária individual e registrada (FR-3606 da `115`); conta como
  abertura, como hoje.
- **Arquivo protegido por senha.** O navegador pede a senha ou não desenha; é o caso do arquivo que
  não abre, e o juízo é do conferente.
- **Navegador que não diz se mostra PDF embutido.** Na dúvida, a alternativa (FR-6502).
- **Janela redimensionada com texto digitado no motivo.** O texto fica.
- **Dois conferentes no mesmo item.** O segundo registro é recusado ou aceito como hoje; o cartão do
  primeiro, sem recarga, só sabe disso no próximo registro ou ao recarregar — o que já é verdade hoje
  entre dois registros.

## Requirements *(mandatory)*

### Functional Requirements

#### A abertura e o registro dela

- **FR-6500**: Abrir o arquivo no painel MUST ser a mesma entrega de hoje — conferência do resumo
  antes de sair um byte, sem cache, e o mesmo registro de consulta sob a apresentação (FR-3605 e
  FR-3606 da `115`). Essa abertura MUST valer para a FR-3611 da `115` e para a FR-4460 da `131`
  exatamente como a abertura em aba própria. Nenhum evento de trilha novo é criado (D-002).
- **FR-6501**: Nenhum arquivo MUST ser pedido ao servidor sem um gesto da pessoa sobre aquela
  apresentação: entrar na página, registrar uma conferência, receber a confirmação, passar ao
  próximo item, redimensionar a janela e voltar à aba MUST NOT abrir arquivo (D-001).
- **FR-6502**: A página MUST NOT carregar o arquivo numa moldura quando o navegador declara que não
  mostra PDF dentro da página, nem quando não declara nada. Nesses casos o gesto de abrir leva à
  alternativa (FR-6510). Na dúvida, a alternativa (D-002).
- **FR-6503**: A marca *"aberto por você"* e o aviso de abertura do cartão MUST refletir a trilha.
  Depois de uma abertura pela página — no painel, em aba própria ou por download —, a página MUST
  relê-los do servidor e atualizar o cartão daquele item sem recarregar. A entrega recusada, por
  integridade ou por arquivo indisponível, MUST deixar o aviso como estava.
- **FR-6504**: O arquivo da convocação MUST ser emoldurável pela própria origem, e por nenhuma outra,
  como o da Mesa (FR-112 da `012`). A proteção contra emolduramento por outra origem continua.

#### O painel em tela larga

- **FR-6505**: Em tela larga — a mesma fronteira da Mesa —, o arquivo aberto MUST aparecer num painel
  ao lado da lista de documentos, e o cartão do item aberto, com o formulário, MUST ficar à vista ao
  mesmo tempo. Ao abrir, a página MUST levar o cartão do item à vista, se ele não estava.
- **FR-6506**: A barra do painel MUST identificar o documento (o nome do requisito), a versão, o
  instante da apresentação e a pessoa (nome e inscrição). O painel MUST NOT mostrar arquivo sem dizer
  de quem e de qual versão ele é.
- **FR-6507**: A barra MUST oferecer *"Abrir em aba própria"*, *"Baixar"* e *"Fechar"*. As duas
  primeiras são o mesmo endereço do painel, e cada uma conta como abertura, como hoje.
- **FR-6508**: O item cujo arquivo está no painel MUST ser marcado na lista, por texto ou forma além
  da cor. Um arquivo por vez.
- **FR-6509**: O painel MUST NOT cobrir os dados da página: a pessoa, o resumo e a situação da
  convocação continuam alcançáveis pela rolagem da página.

#### Quando o arquivo não aparece na página

- **FR-6510**: Quando o arquivo não pode ser mostrado na página — navegador sem visualizador
  embutido, entrega recusada por integridade (FR-3605 da `115`) ou por arquivo indisponível (FR-3695
  da `117`) —, a página MUST dizer em texto o que aconteceu, com a frase da recusa de hoje quando
  houver recusa, e oferecer o que resta: *"Abrir em aba própria"* e *"Baixar"* quando a entrega é
  possível; nenhuma das duas quando ela foi recusada.
- **FR-6511**: A abertura pela alternativa MUST registrar o que se registra hoje, e, quando a pessoa
  voltar à página, a marca e o aviso do item MUST ser relidos (FR-6503).
- **FR-6512**: O gesto de abrir MUST dizer o tamanho do arquivo, como na Mesa. Enquanto o arquivo
  carrega no painel, o painel MUST dizer que ele está carregando.
- **FR-6513**: A barra MUST oferecer a aba própria e o download em todo arquivo aberto, inclusive
  quando ele parece ter sido mostrado: o PDF danificado é entregue e registrado, e só o navegador
  sabe que não o desenhou. A ajuda recolhida do formulário MUST dizer que arquivo que não abre, ou
  abre em branco, é motivo de pendência, com o motivo dito à pessoa convocada.

#### Registrar sem recarregar

- **FR-6514**: Registrar a conferência MUST atualizar, sem recarregar a página: o cartão do item
  (estado, conferências), o resumo (FR-5020 da `143`), a seção *"Situação desta convocação"* (FR-5021
  da `143`) e os links à próxima pessoa com documento a conferir. O painel e o arquivo nele MUST
  continuar como estavam.
- **FR-6515**: A conferência registrada sem recarga MUST ser a mesma do caminho de hoje: o mesmo
  comando, a mesma autorização, a mesma recusa, a mesma chave de idempotência por formulário e o
  mesmo registro (FR-3585 da `115`). O envio duplicado MUST produzir uma conferência. Depois de um
  registro aceito, o próximo formulário daquele item MUST ter chave nova.
- **FR-6516**: A recusa MUST aparecer no cartão do item, com a frase de hoje e com o que foi marcado
  e digitado preservado — exceto o resultado, na versão superada (FR-3587 da `115`). A recusa sem
  cartão onde morar — desfecho registrado, Processo encerrado — MUST aparecer no alto, e os
  formulários que deixaram de valer MUST sumir.
- **FR-6517**: Sem script, a página MUST funcionar como hoje: abrir em aba própria, registrar com
  recarga, voltar ao cartão.
- **FR-6518**: Se o registro não chegar ao comando — sessão expirada, identidade ausente, falha de
  rede —, a página MUST dizer que nada foi registrado e manter à vista o que foi marcado e digitado.

#### O próximo documento e a próxima pessoa

- **FR-6519**: Depois de um registro aceito, a confirmação MUST oferecer o passo seguinte da
  conferência, nomeado: o próximo documento desta pessoa com versão a conferir, na ordem da página;
  sem nenhum, a próxima pessoa com documento a conferir, pelo critério da FR-5024 da `143`; sem
  nenhuma, a frase de que não há outro documento a conferir neste recorte, com o caminho à convocação.
- **FR-6520**: O gesto do próximo documento MUST abri-lo — no painel, ou pela alternativa — e levar o
  foco ao painel com o formulário dele à vista. A abertura acontece porque a pessoa usou o gesto,
  nunca porque o registro anterior terminou (D-003).
- **FR-6521**: O gesto da próxima pessoa MUST carregar a página dela, com o painel fechado; nenhum
  arquivo dela é aberto por chegar.
- **FR-6522**: Nenhum gesto MUST registrar mais de uma conferência, nem registrar a do item atual ao
  passar ao próximo. A FR-3609 da `115` continua de pé.

#### Teclado e leitor de tela

- **FR-6523**: Tudo MUST ser operável só por teclado, e a ordem de tabulação MUST seguir a ordem
  visual. Ao abrir, o foco MUST ir ao título do painel; ao fechar, ao formulário do item que estava
  aberto.
- **FR-6524**: O painel MUST ser uma região nomeada, não modal: ele não prende o foco. A moldura MUST
  ter nome acessível com o documento, a versão e a pessoa.
- **FR-6525**: Cada mudança sem recarga — a abertura registrada, o carregamento, a confirmação — MUST
  ser anunciada a leitor de tela uma vez, em texto curto; a recusa MUST receber o foco, como hoje.
- **FR-6526**: A página MUST caber a 320 px de largura, e com o texto ampliado a 200 %, sem rolagem
  horizontal.

#### Telas pequenas

- **FR-6527**: Abaixo da tela larga, o arquivo mostrado na página MUST aparecer dentro do cartão do
  item, acima do formulário, com altura limitada, de modo que o resultado, o motivo e o botão de
  registrar fiquem alcançáveis sem rolar o arquivo até o fim (proposta, pendente da Questão 2).
- **FR-6528**: Onde o arquivo não se mostra na página (FR-6502), o gesto MUST abri-lo no visualizador
  do próprio aparelho; ao voltar, o cartão do item MUST estar onde estava, com a marca relida e o foco
  no formulário dele.
- **FR-6529**: A 390 px, nenhum controle da conferência — resultado, motivo, registrar — nem a
  identificação da pessoa e do documento MUST ficar atrás do arquivo ou fora da página.
- **FR-6530**: Cruzar a fronteira da tela larga com um arquivo aberto MUST levá-lo ao outro arranjo
  sem perder o que foi marcado e digitado e sem pedir o arquivo de novo.

#### A pendência e o aviso

- **FR-6534**: Registrar uma conferência pendente MUST NOT gravar aviso de pendência, como a FR-4604
  da `134` exige. O pedido de aviso é sempre um gesto à parte.
- **FR-6535**: A confirmação de uma conferência pendente MUST dizer que nenhum aviso foi pedido por
  ela e que a pessoa vê a pendência no portal. Nenhum texto MUST tratar a pendência registrada como
  comunicação ao candidato (FR-5018 da `143`).
- **FR-6536**: A situação do aviso da pessoa — nenhum aviso desde a pendência, com o alcance do gesto
  agora (FR-5017 da `143`), ou aviso registrado com a situação do envio (FR-5016 da `143`) — MUST se
  atualizar na página sem recarga depois de cada registro, e MUST aparecer na confirmação quando a
  conferência da pessoa termina com pendência.
- **FR-6537**: Terminada a conferência da pessoa — nenhum documento dela a conferir — com ao menos
  uma pendência elegível pela FR-4606 da `134`, a confirmação MUST oferecer o gesto *"Pedir aviso
  para ‹nome›"*, só dela. O gesto MUST NOT ser oferecido por documento, nem no meio da conferência da
  pessoa (D-008).
- **FR-6539**: O aviso pedido pelo gesto da FR-6537 MUST considerar todas as pendências elegíveis da
  pessoa no instante do pedido, pelas mesmas regras do gesto em lote: o texto da FR-4614 da `134`
  compõe todos os itens pendentes da lista, e não só o documento recém-conferido.
- **FR-6540**: O gesto da FR-6537 MUST reaproveitar, sem exceção, as regras da `134`: quem pode
  (FR-4603 da `134`), as exclusões (FR-4606 a FR-4608 da `134`), a chave de envio e o Processo em
  estado final (FR-4610 da `134`), a trava e a idempotência (FR-4611 da `134`), o limite de um aviso
  por pessoa, por chamada, por dia, o texto e o despacho. MUST NOT haver exceção ao limite diário, nem
  agendamento automático do pedido para o dia seguinte.
- **FR-6541**: Quando o gesto não alcançaria a pessoa, a confirmação MUST dizer o motivo, pela mesma
  regra da prévia do gesto em lote (FR-4605 da `134`), e, quando houver, a partir de quando o pedido
  poderá ser feito: no *"já avisada hoje nesta chamada"*, a partir do dia seguinte, no dia local da
  instalação; nos demais motivos — vencimento decorrido, desfecho, item reenviado, sem endereço,
  envio desabilitado, Processo encerrado —, sem data, porque o tempo sozinho não os resolve.
- **FR-6542**: O gesto em lote *"Avisar as pessoas com pendência nesta chamada"* MUST continuar na
  tela da convocação, como hoje. Os dois gestos gravam o mesmo aviso, e um conta para o limite do
  outro.
- **FR-6543**: A situação do aviso pedido MUST distinguir, com as palavras da `066`: *solicitado,
  aguardando envio* (pendente, em envio, ou em falha temporária com nova tentativa automática);
  *enviado*, isto é, aceito pelo servidor de correio, nunca "entregue", "recebido" nem "lido" (FR-5016
  da `143`); e *não enviado*, com o estado que o explica — falha definitiva, indeterminada, expirada
  sem envio ou interrompido antes do envio, com o motivo da interrupção.
- **FR-6538**: Nenhum gesto desta spec MUST enviar a mensagem na requisição: o aviso sai pelo
  despacho da `066`, e a página diz isso.

#### Comum

- **FR-6531**: Nada desta spec MUST usar estilo ou script escrito no template, nem afrouxar a política
  de conteúdo: script e estilo continuam só de arquivo, e moldura e objeto, só da própria origem.
- **FR-6532**: Nada desta spec MUST mudar quem pode conferir, o comando da conferência, a FR-3611 da
  `115`, a FR-4460 da `131`, os estados e os rótulos deles, a trilha, nem o portal do candidato. A
  única exceção é o gesto individual do aviso (FR-6537 a FR-6543), pela revisão da `134` decidida na
  Questão 4.
- **FR-6533**: O painel da conferência MUST ter o mesmo desenho e os mesmos rótulos comuns do painel
  da Mesa — a barra, *"Abrir em aba própria"*, *"Fechar"*, o foco ao abrir. O que a Mesa ganha desta
  spec depende da Questão 3.

### Requisitos de experiência

- **UX-640**: A barra do painel MUST dizer, em duas linhas, o documento e a pessoa: *"Diploma de
  graduação — versão 2, apresentada em 11/11/2026 17:52"* e *"Alice Treinamento C09-01 ·
  INS-2026-JM7DFQTG"*. Na versão substituída: *"versão 1, substituída pela versão 2"*.
- **UX-641**: O botão do cartão continua *"Abrir"*, com o tamanho ao lado, e o nome acessível MUST
  começar pelo texto visível: *"Abrir Diploma de graduação, versão 2"*.
- **UX-642**: A confirmação MUST nomear o que foi registrado e o próximo passo: *"Conferência
  registrada: Diploma de graduação, conforme."*, seguida de *"Próximo a conferir: Comprovante de
  residência"* com o gesto *"Abrir"*; ou *"Não há outro documento de Alice a conferir."*, seguida de
  *"Próxima com documento a conferir: Bernardo Treinamento C09-02"*; ou *"Não há outro documento a
  conferir neste recorte."*, com *"Voltar à convocação"*.
- **UX-643**: O texto da alternativa MUST dizer o fato e o caminho, sem culpar o navegador: *"Este
  navegador não mostra o documento dentro da página. Abra em aba própria ou baixe o arquivo; a
  abertura fica registrada do mesmo jeito."*
- **UX-644**: O carregamento MUST dizer o tamanho: *"Carregando o documento (8,4 MB)…"*.
- **UX-645**: A ajuda da FR-6513 MUST ficar no *"como preencher"* recolhido do formulário, e não na
  barra: *"O arquivo não abre, ou abre em branco? Registre como pendente e diga no motivo que o
  arquivo não pôde ser lido."*
- **UX-646**: A falha da FR-6518 MUST dizer *"A conferência não foi registrada."* e a razão, quando
  conhecida: *"Sua sessão terminou; entre de novo. O que você marcou continua aqui."*
- **UX-647**: A confirmação da pendência MUST dizer: *"Conferência registrada: Diploma de graduação,
  pendente. Nenhum aviso foi pedido; Bernardo vê a pendência no portal."*
- **UX-648**: O gesto da FR-6537 MUST dizer *"Pedir aviso para Bernardo"*, com a frase da `134` antes
  do botão — o aviso não muda o prazo e não é a convocação. A resposta MUST dizer *"Aviso solicitado;
  aguardando envio. A mensagem sai pelo despacho dos avisos, e não neste clique."*
- **UX-649**: A situação do aviso MUST usar três começos de frase, um por grupo da FR-6543: *"Aviso
  solicitado em ‹data›; aguardando envio."*, *"Aviso enviado em ‹data›: aceito pelo servidor de
  correio."* e *"Aviso não enviado: ‹estado da `066`›."*
- **UX-650**: A recusa antecipada da FR-6541 MUST dizer o motivo e, quando houver, a data: *"Bernardo
  já foi avisado hoje nesta chamada. Um novo pedido poderá ser feito a partir de 12/11/2026."*

### Key Entities

Nenhuma entidade nova. A **apresentação** (a versão do documento que a pessoa enviou), a
**consulta** registrada sob ela (a abertura que o "conforme" lê) e a **conferência** são as da `115`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2140**: No C09, em tela larga, conferir cada documento de Alice custa no máximo três gestos —
  abrir, marcar, registrar —, sem troca de aba e sem recarregar a página; hoje são quatro, com
  recarga.
- **SC-2141**: Em 100% dos casos do teste, o "conforme" e o "não se aplica" registrados sem recarga
  são aceitos e recusados exatamente quando o caminho de hoje os aceitaria e recusaria, com o mesmo
  código de recusa.
- **SC-2142**: Em 100% das entradas na página, dos registros, das confirmações e dos redimensionamentos
  do teste, nenhuma consulta a apresentação é registrada sem um gesto sobre ela.
- **SC-2143**: Com o navegador declarando que não mostra PDF embutido, ou sem declarar, nenhuma
  moldura pede arquivo; a alternativa aparece em 100% dos gestos de abrir.
- **SC-2144**: Na divergência de resumo e no arquivo indisponível, a página mostra a frase de hoje em
  texto, nenhuma consulta é registrada e o evento de hoje é.
- **SC-2145**: O envio duplicado do mesmo formulário produz exatamente uma conferência.
- **SC-2146**: Depois de cada registro do teste, o cartão, o resumo e a situação mostrados sem recarga
  são iguais, em texto, aos da página recarregada.
- **SC-2147**: A 1440 px, 1280 px, 390 px e 320 px, a página não tem rolagem horizontal nem violação
  da política de conteúdo, e a 390 px o resultado, o motivo e o botão de registrar do item aberto são
  alcançáveis com a identificação da pessoa e do documento à vista.
- **SC-2148**: Sem script, a conferência dos dois documentos de Alice se completa como hoje.
- **SC-2149** *(verificação humana)*: Só com teclado, e com um leitor de tela, uma pessoa confere os
  dois documentos de Alice e chega aos de Bernardo; o roteiro registra o anúncio de cada passo, e o
  foco nunca cai no início da página.
- **SC-2150** *(verificação humana)*: Num celular com iOS e noutro com Android, a 390 px, uma pessoa
  confere o diploma de Alice do começo ao fim, com a abertura registrada e a marca *"aberto por você"*
  visível ao final.
- **SC-2151** *(verificação humana)*: Uma pessoa que conduz convocações confere os documentos do C09
  antes e depois desta feature; o roteiro registra o tempo e os gestos dos dois percursos, e nenhum
  arquivo conferido é de uma pessoa diferente da do formulário.
- **SC-2152**: Em 100% dos registros de conferência pendente do teste, nenhum aviso de pendência é
  gravado pelo registro; o gesto da FR-6537 grava, para a pessoa, exatamente o aviso — com o mesmo
  texto — que o gesto em lote da `134` gravaria para ela no mesmo instante, e nenhum no dia em que ela
  já foi avisada, por qualquer dos dois gestos.
- **SC-2154**: Em 100% das exclusões do teste, a confirmação diz o motivo, e só o *"já avisada hoje"*
  traz data para novo pedido; nenhum pedido é gravado ou agendado para o dia seguinte.
- **SC-2153**: Depois de cada registro do teste, a situação do aviso mostrada sem recarga é, em
  texto, a do cartão da pessoa na tela da convocação.

## Revisões de requisitos anteriores

- **FR-4603 da `134`** — revista pela `157` em 2026-11-11: o gesto do aviso admite o recorte de uma
  pessoa, com as mesmas regras (D-008).
- **FR-4605 da `134`** — acrescida pela `157` em 2026-11-11: a prévia do recorte individual diz se
  alcança, o motivo e, no *"já avisada hoje"*, a partir de quando.
- **FR-4620 da `134`** — acrescida pela `157` em 2026-11-11: o gesto individual é distinguível na
  trilha.

A redação anterior de cada uma fica ao fim da alínea, na `134`. A FR-4604 da `134` não muda.

## Decisões

### D-001 — O padrão da Mesa, e não um visualizador novo

*Proposta.* O painel da conferência segue o da Mesa (FR-112 da `012`): moldura da própria origem, a
abertura como ato, a barra com o nome, *"Abrir em aba própria"* e *"Fechar"*, o foco no título ao
abrir. O que esta página acrescenta — a identificação da pessoa e da versão, a alternativa e o
arranjo estreito — é acréscimo ao padrão, e não um segundo padrão.

**Por quê**: a Mesa já pagou as lições — o limite de largura que encolhia o PDF, a barra do
visualizador que some na moldura, o `hidden` vencido pelo `display` —, e dois visualizadores na mesma
gestão se desencontrariam no primeiro ajuste.

### D-002 — A abertura continua sendo a entrega; nenhum "vi" declarado pela página

*Proposta.* O registro que autoriza o "conforme" continua sendo a entrega do arquivo verificado a
quem o pediu. A página não ganha um sinal de "o documento apareceu", e por isso não carrega a moldura
onde sabe — ou não sabe — se o navegador o desenha (FR-6502). O PDF danificado continua sendo juízo
do conferente (FR-6513).

**Por quê**: o servidor só sabe o que entregou. Um sinal de "apareceu" mandado pela página seria
autodeclaração, falsificável por qualquer um que a altere, e a regra da FR-3611 da `115` passaria a
depender dele. O custo é o caso raro do arquivo que passou pela assinatura e não se desenha: a
entrega fica registrada, e o conferente vê que não abriu.

### D-003 — O próximo documento abre por gesto, nunca sozinho

*Proposta.* A confirmação oferece o próximo documento num gesto que o abre, e o registro anterior não
o abre por si (FR-6520). A próxima pessoa abre a página dela com o painel fechado (FR-6521).

**Por quê**: é o mesmo princípio da FR-112 da `012`. Abrir sozinho faria *"abriu o documento"* virar
*"registrou o anterior"* — o mesmo evento dizendo outra coisa —, e, aqui, autorizaria o "conforme" de
um arquivo que a pessoa pode não ter olhado. Um gesto a mais por documento é o preço.

### D-004 — Sem recarga dentro da pessoa; a próxima pessoa é outra página

*Proposta.* Registrar e passar ao próximo documento acontecem sem recarga; passar à próxima pessoa
carrega a página dela (FR-6521).

**Por quê**: a página da pessoa tem o passo, o resumo, a situação e os vizinhos dela, e o endereço é
dela. Trocar a pessoa sem trocar a página faria o endereço, o *"Voltar"* do navegador e o registro de
consulta à página (FR-3604 da `115`) mentirem sobre quem está sendo conferido.

### D-005 — O "conforme" continua oferecido antes da abertura, com o aviso ligado a ele

*Proposta, pendente da Questão 1.* As opções do resultado continuam disponíveis antes da abertura,
com o aviso *"Você ainda não abriu a versão N"* ligado a elas, como desde o #473; ao abrir, o aviso dá
lugar a *"aberto por você"* sem recarga (FR-6503).

**Por quê**: o estudo propôs habilitar o *Conforme* só depois da abertura. Desabilitar uma opção a
tira da ordem de tabulação, e quem usa leitor de tela deixa de encontrá-la e de ouvir a razão; e a
regra continua no comando, que recusa de qualquer jeito. Com o painel, o aviso troca de estado na
hora da abertura, e o erro que o estudo viu — marcar e só descobrir na recusa — deixa de custar uma
recarga.

### D-006 — Telas pequenas pela capacidade do navegador, e não só pela largura

*Proposta, pendente da Questão 2.* Abaixo da tela larga, o arquivo aparece dentro do cartão, acima
do formulário, quando o navegador mostra PDF embutido; quando não mostra — a maioria dos celulares —,
abre no visualizador do aparelho, e a volta relê o cartão (FR-6527, FR-6528).

**Por quê**: a Mesa, abaixo da tela larga, simplesmente abre em aba própria. Aqui o usuário pediu o
uso em tela pequena sem perder os controles, e um tablet ou uma janela estreita num computador
mostram o PDF muito bem. Decidir só pela largura poria a moldura num celular que não desenha o PDF —
e registraria uma abertura sem nada visto (D-002).

### D-007 — A Mesa fica como está nesta entrega

*Proposta, pendente da Questão 3.* A Mesa não ganha a alternativa, o arranjo estreito nem a
identificação da versão; só compartilha o desenho comum (FR-6533). O que se viu nela vai para os
achados registrados.

**Por quê**: o usuário pediu a conferência da convocação. Na Mesa a abertura só informa, e o risco
da D-002 é menor; mudá-la aqui alargaria o escopo de uma feature de outra tela.

### D-008 — O aviso continua gesto, oferecido quando a conferência da pessoa termina

**Decisão do usuário (11/11/2026), Questão 4, opção A, com ajustes.** O registro da pendência não
grava aviso (FR-6534). Quando não resta documento da pessoa a conferir e há pendência elegível, a
confirmação oferece *"Pedir aviso para ‹nome›"*, só para aquela pessoa (FR-6537), com todas as
pendências elegíveis dela no instante do pedido (FR-6539) e as autorizações, exclusões e limite
diário da `134`, sem exceção nem agendamento (FR-6540). A recusa diz o motivo e, quando houver, a
partir de quando (FR-6541). O gesto em lote fica (FR-6542). A situação distingue solicitado, enviado
e não enviado (FR-6543). A `134` é revista expressamente para admitir o recorte individual, com a
FR-4604 dela preservada.

O rótulo é *"Pedir aviso"*, e não *"Avisar agora"*, por decisão do usuário: o clique solicita, e quem
envia é o despacho.

**Por quê**: a decisão do usuário de 08/11 na `134` é que o aviso sai por gesto da comissão, e nunca
por evento — e o gesto continua sendo gesto. Oferecê-lo no fim da pessoa, e não por documento, segue
a regra de um aviso por pessoa, por chamada, por dia: avisar a primeira pendência gastaria o aviso
do dia, e a segunda, registrada minutos depois, só seria avisada no dia seguinte se a mensagem já
tivesse saído. O custo é acrescentar à `134` o recorte de uma pessoa a um gesto que ela desenhou em
lote; o texto, as exclusões e o despacho são os dela.

## Questões para o usuário

Cada questão traz a proposta da spec em primeiro lugar. As decisões D-005 a D-007 seguem a
proposta até a resposta. A Questão 4 foi respondida, e está em "Questões respondidas".

### Questão 1 — O *Conforme* fica disponível antes de abrir o arquivo?

- **A (proposta)**: sim, como desde o #473, com o aviso ligado às opções; ao abrir, o aviso vira
  *"aberto por você"* na hora, sem recarga, e o comando continua recusando o "conforme" sem abertura.
  Preserva a ordem de tabulação e o anúncio do aviso ao leitor de tela.
- **B**: não; *Conforme* e *Não se aplica* ficam desabilitados até a abertura, como o estudo propôs.
  Elimina a recusa da tela, mas as opções desabilitadas somem da tabulação, e a razão precisa ser dita
  fora delas. Sem script, a opção desabilitada não pode ser habilitada, e a página teria de mantê-las
  disponíveis nesse caso.

### Questão 2 — Como fica a conferência a 390 px?

- **A (proposta)**: pela capacidade do navegador. Com PDF embutido, o arquivo aparece dentro do
  cartão, acima do formulário, com altura limitada; sem ele, abre no visualizador do aparelho e a
  volta relê o cartão e devolve o foco ao formulário (D-006).
- **B**: como a Mesa, sempre pelo visualizador do aparelho abaixo da tela larga, com a volta relida e
  o foco devolvido. Mais simples e previsível; um tablet ou uma janela estreita perdem o arquivo na
  página.

### Questão 3 — A Mesa do avaliador ganha o mesmo nesta spec?

- **A (proposta)**: não. A Mesa só compartilha o desenho comum, e os achados dela ficam registrados
  para spec própria (D-007).
- **B**: sim. A Mesa ganha a alternativa sem prévia, a mensagem de recusa dentro do painel e o
  arranjo estreito, com requisitos acrescentados aqui e o escopo alargado à `012`.

## Questões respondidas

- **Questão 4 — O aviso de pendência aparece junto da conferência?** Respondida pelo usuário em
  11/11/2026: opção A, com ajustes (D-008). O gesto *"Pedir aviso para ‹nome›"*, só daquela pessoa,
  quando a conferência dela termina com pendência elegível; todas as pendências elegíveis dela no
  pedido; as regras da `134` sem exceção ao limite diário e sem agendamento; a recusa com o motivo e,
  quando houver, a data; o gesto em lote mantido; a situação em solicitado, enviado e não enviado; e a
  `134` revista para admitir o recorte individual, preservando a FR-4604 dela. Descartados: a marca no
  formulário da pendência, que revia a FR-4604 da `134` e gastava o aviso do dia na primeira
  pendência; e nenhum gesto novo.

## Achados registrados

Encontrados ao escrever esta spec, fora do escopo dela. Governança é do usuário.

- **A recusa dentro da moldura da Mesa provavelmente aparece como página bloqueada.** A exceção de
  emolduramento da rota da Mesa vale para a resposta de sucesso da view; a recusa por integridade e a
  de arquivo indisponível saem como exceção, e a resposta montada depois dela recebe a proibição de
  emolduramento do resto do sistema. Pela leitura do código, o painel mostraria o aviso de bloqueio do
  navegador, e não a frase da recusa. Não reproduzido.
- **A Mesa registra a abertura em navegador que não desenha o PDF.** Em tela larga, com o visualizador
  de PDF desligado, a moldura da Mesa pede o arquivo, o servidor registra a consulta, e nada aparece.
  Na Mesa a abertura só informa, e o efeito é uma marca *"aberto"* imprecisa. Não reproduzido.
- **O envio aceita PDF danificado.** A aceitação confere a assinatura, o tamanho e o arquivo vazio;
  um PDF truncado passa e só falha na conferência, onde custa uma rodada de pendência. Validar a
  estrutura do PDF no envio é mudança do portal e da `117`, e não desta spec.

## Assumptions

- Todo arquivo da convocação é PDF de até 10 MB: o envio só aceita a assinatura de PDF, e a entrega
  responde sempre como PDF.
- Os navegadores em uso declaram se mostram PDF dentro da página. O que não declarar recebe a
  alternativa (FR-6502).
- A página continua emitindo uma chave de idempotência por formulário, e a recusa continua sendo
  devolvida com o código do comando.
- O C09 da `134` serve de caso de verificação; o resultado do estudo nele é o "antes".
- A implementação da `154`, antes ou depois desta, só muda os rótulos dos estados, que esta spec não
  nomeia.

## Fora do escopo

- Conferência em lote, "conferir todos" ou registrar vários itens num gesto (FR-3609 da `115`).
- Controles próprios de zoom e rotação: são do visualizador do navegador, como decidiu a Mesa.
- Converter, reparar ou validar arquivos; ler imagens; reconhecimento de texto.
- O envio de vários documentos pelo portal (`150`) e o alerta de arquivo repetido (achado 11 do
  estudo).
- O texto do aviso de pendência, as exclusões, o limite por dia e o despacho, que são da `134` e da
  `066`; o envio do aviso dentro do clique.
- Os nomes dos estados de documento, que são da `154`.
- A Mesa do avaliador além do desenho comum, salvo resposta B à Questão 3.
- O portal do candidato.
