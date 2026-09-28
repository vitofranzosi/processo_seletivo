# Feature Specification: Operar o resultado por marco, e não por recorte

**Feature Branch**: `claude/nova-spec-049-marco-048300`

**Created**: 2026-09-28

**Status**: Draft

**Input**: pedido do usuário de 28/09/2026 — *"operar o resultado por marco, e não por recorte"*. É o
**passo 2** da ordem adotada em 27/09 ([decisões pendentes](../../doc/decisoes-pendentes-da-consolidacao.md),
*Depois da reavaliação de 27/09*), antecipado para antes do piloto por decisão do usuário: o piloto
deve começar com o operacional enxuto. Fontes lidas: a mesma seção e a `DP-15`; a
[reavaliação de 27/09](../../doc/reavaliacao-pos-consolidacao-2026-09-27.md), §E.2, §F.2 e o item 3 da
Priorização; o [anexo B](../../doc/reavaliacao-pos-consolidacao-2026-09-27/anexo-B-operacao.md), §7, §9,
§13, §14 e §17; e a `DP-17`, o invariante de automação explícita que está entrando na Constituição.

> **Faixa de identificadores.** Abre em **FR-810**, **SC-300** e **UX-090**, contíguos, por
> determinação do usuário: outras specs em paralelo usam outras faixas. O teto medido nesta árvore em
> 28/09 é 803, 294 e 088. As **decisões** reiniciam em `D-001` e moram na seção
> [*Decisões*](#decisões); decisão de outra spec é citada pelo requisito que a registra, e nunca pelo
> número local dela.

---

## Por que esta feature existe

**Ordem, corte, apuração e publicação são um ato por recorte, e nada diz quais recortes faltam.** O
recorte é o par (Perfil, Modalidade de Concorrência) sobre o qual se ordena, se corta, se apura e se
convoca, derivado num lugar só (`editais/domain/recortes.py`, `FR-491`). Cada um desses atos é
praticado numa tela aberta **por recorte**, com o recorte no endereço. A tela do marco já navega entre
os recortes, mas o ato continua sendo um por visita.

| Onde | O que custa hoje | Conferido em 28/09, em `28b3815b` |
|---|---|---|
| Ordem | uma tela e dois passos por recorte | `interface/views.py:5891`, `:6136` |
| Corte | uma tela e um envio por recorte | `interface/views.py:6367`, `:6921` |
| Apuração | um botão por recorte, na tela do marco | `interface/views.py:6554` |
| Publicação | uma prévia e uma confirmação por ato, e há um ato por recorte | `interface/views.py:7077`, `:7181`; `divulgacao/models.py:52-56` |
| O que falta | nenhum lugar diz: recorte sem ato "não é sinal" | `interface/supervisao.py:842-846`; anexo B §17, item 3 |

**A escala.** No 140/2025 são **64 recortes**: 16 Perfis, cada um com o seu marco, e 4 recortes por
marco. Ordenar e publicar duas vezes custa ~200–300 atos e ~400–600 cliques em 64 × 3 telas, sem
sinal que diga quais recortes faltam (anexo B, §15.3). No 28/2026 são 21 (§15.2).

**O unitário aqui não protege decisão nenhuma.** O sistema é unitário onde a decisão é sobre uma
pessoa: a Mesa, o recurso, o desfecho. Isso é coerente com "decisão tem autor". Ordenar, cortar,
apurar e publicar um marco é **uma** decisão, e a mesma pessoa a confirma R vezes, em R telas (anexo
B, §14, "Leitura de conjunto"). A tela do sorteio já prova o contrário: lista os recortes juntos
*"para que ninguém publique dois e esqueça o terceiro"* (`interface/views.py:8201`), mas mantém um
botão por recorte.

**O que esta feature não muda.** A unidade do ato continua o recorte. Cada recorte continua com a
sua ordem, a sua faixa, a sua apuração e a sua publicação, com raiz, sucessão, autor e documento
próprios. O que muda é **quantas vezes a pessoa confirma**, e **o que ela vê antes e depois**.

## Clarifications

### Session 2026-09-28

- Q: O gesto processa os recortes de um marco (o marco mora no Perfil) ou junta os marcos homônimos
  de todos os Perfis? → A: Um marco, como o Edital o publica (`D-001`).
- Q: Recorte com ato vigente obsoleto entra no gesto, com motivo único, ou a sucessão continua na
  tela do recorte? → A: Só o que falta; a sucessão continua por recorte (`D-002`).
- Q: Recorte em que ninguém concorreu recebe a ordem vazia e a publicação da lista vazia? → A: Entra
  nos dois, declarado na conferência como "ninguém concorreu" (`D-003`).
- Q: Onde ficam o indicador completo e os gestos? → A: Numa tela nova por marco, com o resumo na
  página do Edital; as telas por recorte continuam (`D-005`).

---

## User Scenarios & Testing *(mandatory)*

> **Prioridade é valor, e não ordem de execução.** A ordem de implementação fica com o
> [plano](plan.md).

> **Vocabulário.** *Gesto* é a confirmação humana única que dispara os atos de um marco. *Alcance* é
> o conjunto de recortes sobre os quais o gesto vai praticar o ato, declarado antes da confirmação.
> *Desfecho* é o que aconteceu em cada recorte depois dela: **feito**, **recusado** (com o motivo) ou
> **fora do alcance** (com a razão). *Marco* é o marco classificatório como o Edital o publica, e ele
> mora dentro de um Perfil (`D-001`).

### User Story 1 - Saber, por marco, quais recortes faltam (Priority: P1)

Quem conduz o certame abre a página do Edital e vê, em cada marco, quantos recortes já estão
ordenados, cortados, apurados e publicados, e quantos faltam. Abre o marco e vê a tabela inteira:
cada recorte, nomeado como o Edital o publica, e o estado de cada uma das quatro operações.

**Why this priority**: é a lacuna que nenhum outro lugar cobre. A Supervisão vê o que envelheceu, e
não o que ainda não começou (`interface/supervisao.py:842-846`). Sem o indicador, o gesto em lote
desta feature não tem como mostrar o que fez, nem o que resta. E o indicador tem valor sozinho: num
Edital de 64 recortes, ele troca 64 visitas por uma leitura.

**Independent Test**: publicar um Edital com dois Perfis, um com ampla e duas cotas, outro só com a
ampla. Emitir a ordem de dois dos três recortes do primeiro pela tela de hoje, e cortar um deles.
Abrir a página do Edital e a tela do marco, e conferir o que cada uma diz de cada recorte.

**Acceptance Scenarios**:

1. **Given** um marco de três recortes com ordem vigente em dois, **When** quem conduz abre a página
   do Edital, **Then** o marco mostra *ordenados 2 de 3*, e o mesmo para as demais operações.
2. **Given** o mesmo marco, **When** quem conduz abre a tela do marco, **Then** cada recorte aparece
   numa linha, com o rótulo da derivação única, e cada operação numa coluna, com o estado dela e o
   caminho para a tela do recorte.
3. **Given** um marco sem regra de corte, **When** a tela do marco é aberta, **Then** a coluna do
   corte diz que o marco não corta, e o corte não conta como falta.
4. **Given** um recorte com ordem vigente que ficou obsoleta, **When** a tela do marco é aberta,
   **Then** a célula diz que a ordem está obsoleta, e não que está feita.
5. **Given** um recorte cujo resultado foi publicado para um ato anterior ao vigente, **When** a tela
   do marco é aberta, **Then** a célula da publicação diz que o público lê um ato anterior.
6. **Given** um marco de sorteio, **When** a tela do marco é aberta, **Then** a coluna da ordem lê os
   atos do sorteio, e o caminho dela leva à tela do sorteio, e não à da ordenação.
7. **Given** um recorte reservado em que ninguém concorreu e cuja ordem vazia foi emitida, **When** a
   tela do marco é aberta, **Then** a célula diz *ordenado — ninguém concorreu*, e não pendência.

---

### User Story 2 - Emitir a ordem de todos os recortes do marco num gesto (Priority: P1)

Na tela do marco, quem gere a comissão pede para ordenar o marco. A conferência lista cada recorte:
os que vão receber ordem, com quantos recebem posição e quantos ficam sem; os que já têm ordem e
ficam de fora; os que ninguém concorreu, que recebem a ordem vazia. A pessoa confirma uma vez. O
sistema emite uma ordem por recorte, cada uma com o seu autor e o seu registro na trilha, e mostra o
desfecho de cada recorte.

**Why this priority**: a ordem é o primeiro dos quatro atos, e os outros três dependem dela. É também
o ato com dois passos por recorte: é onde o laço de hoje mais custa.

**Independent Test**: publicar um Edital de três recortes sem ordem, com Resultados consolidados.
Ordenar o marco num gesto. Conferir três atos, três registros na trilha com o mesmo autor, e o
indicador em *ordenados 3 de 3*.

**Acceptance Scenarios**:

1. **Given** um marco computado de três recortes sem ordem, **When** quem gere a comissão pede para
   ordenar, **Then** a conferência lista os três, com o alcance de cada um, e nada é gravado.
2. **Given** a conferência, **When** a pessoa confirma, **Then** três atos de ordenação são emitidos,
   um por recorte, cada um com a pessoa como autora, e a tela mostra *feito* nos três.
3. **Given** um marco com ordem vigente em um dos três recortes, **When** a pessoa pede para ordenar,
   **Then** a conferência mostra esse recorte fora do alcance, porque já tem ordem, e o gesto emite só
   os outros dois.
4. **Given** um recorte cuja ordem vigente está obsoleta, **When** a pessoa pede para ordenar o
   marco, **Then** esse recorte fica fora do alcance, e a conferência diz que a sucessão se faz na
   tela do recorte, com motivo (`D-002`).
5. **Given** a conferência lida, **When** outra pessoa emite a ordem de um dos recortes antes da
   confirmação, **Then** esse recorte é recusado, com o motivo, e os outros são emitidos.
6. **Given** um marco de sorteio, **When** a tela do marco é aberta, **Then** ela não oferece ordenar:
   a ordem desse marco nasce do sorteio público, na tela do sorteio.
7. **Given** um recorte em que o cálculo recusa, por empate a julgar ou por outra razão do domínio,
   **When** a conferência é composta, **Then** o recorte aparece como impedido, com a razão, e não
   entra no alcance.

---

### User Story 3 - Publicar o resultado de todos os recortes do marco num gesto (Priority: P1)

Quem tem a capacidade de publicar resultado abre a tela do marco e pede para publicar. Escolhe uma
vez a natureza, preliminar ou definitiva, e a autoridade signatária. A conferência lista cada recorte:
o que vai ser divulgado, os avisos de cada um, os que ficam de fora e por quê. A pessoa confirma uma
vez. O sistema publica um resultado por recorte, cada um com o seu documento, a sua página pública e o
seu registro, e mostra o desfecho de cada recorte.

**Why this priority**: é o ato público, e o que o anexo B mais conta: 64 publicações preliminares e 64
definitivas no 140/2025. É também o ato de outra autoridade. Quem publica não é quem ordena, e o
gesto tem de respeitar a separação.

**Independent Test**: com os três recortes ordenados, publicar o marco como preliminar num gesto.
Conferir três publicações, três documentos, três páginas públicas e o indicador em *publicados 3 de
3*. Publicar depois como definitiva com um recurso pendente num dos recortes, e conferir que só ele é
recusado, pelo motivo da definitividade.

**Acceptance Scenarios**:

1. **Given** um marco com três atos vigentes nunca divulgados, **When** quem publica pede para
   publicar como preliminar, **Then** a conferência lista os três, com o cabeçalho e a quantidade de
   posições de cada um, e nada é gravado.
2. **Given** a conferência, **When** a pessoa confirma, **Then** três publicações são feitas, uma por
   recorte, cada uma com documento próprio e com a pessoa e a autoridade escolhida registradas.
3. **Given** um recorte cujo ato vigente está impedido de ser divulgado, **When** a conferência é
   composta, **Then** o recorte aparece como impedido, com a mesma razão que a prévia de hoje daria, e
   não entra no alcance.
4. **Given** um recorte cujo ato vigente já foi divulgado na natureza escolhida, **When** a pessoa
   pede para publicar, **Then** esse recorte fica fora do alcance, porque já está publicado.
5. **Given** um pedido de definitiva num marco sem janela recursal computável, **When** a pessoa
   confirma, **Then** a declaração de encerramento do prazo é pedida uma vez e gravada em cada
   publicação do gesto.
6. **Given** quem gere a comissão sem a capacidade de publicar, **When** abre a tela do marco,
   **Then** vê o indicador e não vê o gesto de publicar, e a tela diz a quem pedir.
7. **Given** quem publica sem vínculo com a comissão, **When** abre a tela do marco, **Then** vê o
   indicador e o gesto de publicar, e não vê os gestos de ordenar, cortar e apurar.

---

### User Story 4 - Cortar e apurar todos os recortes do marco num gesto (Priority: P2)

Na tela do marco, quem gere a comissão pede para cortar o marco, e depois para apurar a ocupação
dele. Em cada caso, a conferência lista o alcance recorte a recorte, a pessoa confirma uma vez e o
sistema pratica um ato por recorte.

**Why this priority**: o corte só existe nos marcos que o declaram, e a apuração depende do quadro de
vagas. São os dois atos de menos repetição hoje. Mas, sem eles, o marco fica pela metade: ordenado e
publicado por gesto, e cortado e apurado recorte a recorte.

**Independent Test**: com os três recortes ordenados num marco que corta, cortar num gesto e conferir
três faixas. Apurar num gesto e conferir três apurações. Repetir com um recorte sem linha no quadro de
vagas e conferir que só ele é recusado na apuração, com o motivo.

**Acceptance Scenarios**:

1. **Given** um marco com regra de corte e três recortes ordenados sem faixa, **When** a pessoa
   confirma o gesto de cortar, **Then** três faixas são emitidas, uma por recorte.
2. **Given** um recorte com faixa vigente, **When** a pessoa pede para cortar o marco, **Then** esse
   recorte fica fora do alcance. A faixa seguinte continua na tela do recorte, porque pede quantidade
   e motivo próprios.
3. **Given** um marco sem regra de corte, **When** a tela do marco é aberta, **Then** ela não oferece
   cortar.
4. **Given** três recortes ordenados sem apuração, um deles sem linha no quadro de vagas, **When** a
   pessoa confirma o gesto de apurar, **Then** dois são apurados, e o terceiro aparece como impedido
   desde a conferência, com o motivo que a apuração de hoje daria.
5. **Given** um recorte sem ordem vigente, **When** a pessoa pede para cortar ou apurar, **Then** ele
   aparece como impedido pela falta da ordem, com o caminho para ordená-lo.

---

### User Story 5 - Uma falha não apaga nem esconde o que deu certo (Priority: P1)

Durante um gesto, um dos recortes é recusado na confirmação: o mundo mudou desde a conferência, ou o
domínio recusa por uma razão que só aparece na gravação. Os demais recortes são praticados. A tela
diz o que foi feito, o que foi recusado e por quê. O indicador mostra a mesma coisa, e continua a
mostrá-la depois que a tela do desfecho for fechada.

**Why this priority**: é a garantia que torna o gesto seguro. Sem ela, um lote que falha num recorte
ou desfaz os outros, que é trabalho perdido, ou se cala sobre eles, que é trabalho escondido.

**Independent Test**: preparar um gesto de três recortes e, entre a conferência e a confirmação,
emitir por fora a ordem de um deles. Confirmar. Conferir dois *feitos*, um *recusado* com a razão, e
o indicador em *ordenados 3 de 3*, com o ato que veio de fora.

**Acceptance Scenarios**:

1. **Given** um gesto de três recortes em que o segundo é recusado, **When** a confirmação termina,
   **Then** o primeiro e o terceiro estão feitos, e o segundo aparece como recusado, com a razão.
2. **Given** o mesmo gesto, **When** a pessoa volta à tela do marco depois, **Then** o indicador mostra
   os dois atos feitos e o recorte que falta.
3. **Given** um gesto confirmado, **When** o mesmo envio é repetido, por duplo clique ou por reenvio
   do navegador, **Then** nenhum ato é praticado duas vezes, e o desfecho devolvido é o do primeiro
   envio.
4. **Given** um gesto que parou no meio por falha de infraestrutura, **When** a pessoa pede de novo o
   mesmo gesto, **Then** a conferência nova mostra como fora do alcance os recortes já feitos, e o
   gesto pratica só os que faltam.

---

### Edge Cases

Os casos-limite são requisitos: cada um tem requisito ou decisão que o cobre.

- **Marco de um recorte só**, num Perfil sem reserva. A tela do marco funciona igual, com uma linha;
  o gesto de um recorte é o mesmo ato de hoje, com a mesma conferência. Nada fica mais caro
  (`FR-829`).
- **Recorte em que ninguém concorreu.** A ordem vazia é estado legítimo desde a `034` (`FR-492a`), e
  o gesto a emite e a publica, dizendo na conferência que ninguém concorreu (`D-003`).
- **Recorte com ordem vigente obsoleta, faixa obsoleta ou apuração obsoleta.** Fora do alcance: a
  sucessão exige motivo e continua na tela do recorte (`D-002`, `FR-816`).
- **Marco que uma Retificação removeu**, com atos antigos. Não aparece na tela do marco, que é
  derivada da norma vigente; os atos continuam alcançáveis pelas telas de histórico de hoje
  (`FR-813`).
- **Recorte acrescentado por Retificação** a um marco já operado. Aparece no indicador como falta,
  e o gesto seguinte o inclui no alcance.
- **Modalidade que o Perfil aponta como sendo a ampla.** Não é recorte, pela derivação única, e não
  aparece nem no indicador nem no alcance (`FR-812`).
- **Marco de sorteio.** A ordem vem do sorteio: o indicador a lê e o gesto de ordenar não é
  oferecido; corte, apuração e publicação funcionam como nos demais (`FR-817`).
- **Recurso deferido depois da publicação.** Torna obsoleta a ordem **do recorte que alcança**. O
  indicador marca aquele recorte, a sucessão continua na tela dele, e o gesto seguinte de publicar
  divulga só o ato novo, porque os outros recortes já estão publicados na natureza pedida
  (`FR-826`).
- **Definitiva pedida com o preliminar ainda não feito num recorte.** A definitiva pode ser a
  primeira publicação, como hoje. O recorte entra no alcance, se nada o impedir.
- **Preliminar pedido num recorte que já tem definitiva.** Fora do alcance: a ordem das naturezas tem
  sentido único, e a razão é dita.
- **Conferência aberta por muito tempo.** Cada recorte é conferido de novo na confirmação, contra o
  que a conferência mostrou. O que mudou é recusado, e o resto é praticado (`FR-821`).
- **Duas pessoas confirmam o mesmo gesto ao mesmo tempo.** A segunda encontra os recortes já feitos
  pela primeira e recebe a recusa deles, e nenhum ato é praticado duas vezes (`FR-822`).

## Requirements *(mandatory)*

### Functional Requirements

**O indicador**

- **FR-810**: O sistema MUST derivar, para cada marco classificatório do Edital publicado, o estado de
  cada recorte em quatro operações: ordem, corte, apuração e publicação.
- **FR-811**: O estado de cada operação num recorte MUST ser um destes, lido dos atos vigentes: *feito*;
  *obsoleto*, quando o sistema já sabe que o ato ficou para trás; *falta*; e *não se aplica*, quando o
  marco não declara a operação, como o corte sem regra, ou quando o recorte não tem linha no quadro
  de vagas e por isso não há quantidade a apurar. Na publicação, *feito* MUST dizer a natureza,
  preliminar ou definitiva, e o estado MUST distinguir *falta* de *o público lê um ato anterior*.
- **FR-812**: Os recortes do indicador e do alcance MUST vir da derivação única
  (`editais/domain/recortes.py`), com os mesmos rótulos e na mesma ordem. A feature MUST NOT criar
  segunda lista de recortes.
- **FR-813**: O indicador MUST seguir a versão normativa vigente. Marco removido por Retificação não
  aparece; recorte acrescentado aparece como falta.
- **FR-814**: *Falta* MUST contar só o que se aplica. Um marco está completo numa operação quando nenhum
  recorte está em *falta* nem *obsoleto* nela.
- **FR-815**: O estado da ordem num marco de sorteio MUST ser lido dos atos que o sorteio produziu, e o
  caminho da célula MUST levar à tela do sorteio.

**O gesto**

- **FR-816**: Para cada operação, o sistema MUST oferecer um gesto que pratica o ato em todos os
  recortes do marco que estejam em *falta* naquela operação e que o domínio admita. Recorte com ato
  vigente, obsoleto ou não, fica fora do alcance, e a sucessão continua na tela do recorte (`D-002`).
- **FR-817**: O gesto de ordenar MUST NOT ser oferecido em marco de sorteio. O gesto de cortar MUST NOT
  ser oferecido em marco sem regra de corte.
- **FR-818**: Antes da confirmação, o sistema MUST mostrar o alcance do gesto recorte a recorte, sem
  gravar nada: o que será praticado em cada recorte do alcance, com os números que a tela do recorte
  mostraria hoje; os recortes fora do alcance, com a razão; e os impedidos, com a recusa do domínio
  (`DP-17`).
- **FR-819**: A confirmação MUST dizer quantos atos serão praticados. Com alcance vazio, o sistema MUST
  NOT oferecer confirmação, e MUST dizer por quê.
- **FR-820**: Cada recorte do alcance MUST produzir o ato que a tela do recorte produziria, pelo mesmo
  comando de domínio, com as mesmas validações, a mesma autoria, a mesma trilha e o mesmo documento. O
  gesto MUST NOT criar caminho de gravação paralelo.
- **FR-821**: A conferência de cada recorte MUST ser verificada de novo na confirmação, contra o que foi
  mostrado. Recorte que mudou desde a conferência MUST ser recusado com a razão, e MUST NOT ser
  praticado sobre o estado novo sem nova conferência.
- **FR-822**: O gesto MUST ser idempotente: repetir o mesmo envio MUST NOT praticar ato algum de novo, e
  MUST devolver o desfecho do primeiro.
- **FR-823**: A recusa de um recorte MUST NOT desfazer nem impedir os atos dos demais. Cada recorte MUST
  ser praticado de forma independente, e o que foi gravado continua gravado.
- **FR-824**: Depois da confirmação, o sistema MUST mostrar o desfecho de cada recorte do alcance:
  *feito*, com o caminho para o ato; ou *recusado*, com a razão e o caminho para a tela do recorte.
- **FR-825**: Os atos de um mesmo gesto MUST carregar, na trilha de auditoria, uma identificação comum
  do gesto, de modo que se possa ler quais atos nasceram da mesma confirmação.

**A publicação**

- **FR-826**: O gesto de publicar MUST pedir uma vez a natureza e a autoridade signatária, e aplicá-las
  a cada publicação do alcance. Entram no alcance os recortes cujo ato vigente ainda não está
  divulgado na natureza escolhida; a publicação de cada um continua um ato próprio, com documento e
  página pública próprios (`D-004`).
- **FR-827**: Na definitiva, o gesto MUST pedir uma vez a declaração de encerramento do prazo quando
  algum ato do alcance não tiver janela recursal computável, e MUST gravá-la só nas publicações
  desses atos. A janela é **do ato** — a da versão que ele cita, salvo o que a vigente concede
  (RC-121, 28/09) —, e a conferência MUST dizer, por recorte, quais publicações levam a declaração.
- **FR-828**: A conferência da publicação MUST mostrar, por recorte, os avisos e os impedimentos que a
  prévia de hoje mostraria para aquele ato, na natureza escolhida.

**Autoridade e alcance**

- **FR-829**: Cada gesto MUST exigir a mesma autoridade do ato unitário: gerir a comissão para ordenar,
  cortar e apurar, e publicar resultado para publicar. A tela do marco MUST oferecer a cada pessoa só
  os gestos que ela pratica, e MUST dizer a quem pedir os demais.
- **FR-830**: A tela do marco MUST abrir para quem abre hoje qualquer das telas de recorte daquele marco,
  e só para essas pessoas. Quem só consulta vê o indicador, e nenhum gesto.
- **FR-831**: As telas por recorte de hoje MUST continuar existindo e funcionando como hoje. O gesto
  por marco é caminho a mais, e não substituto.

### Experiência

- **UX-090**: A página do Edital MUST mostrar, em cada marco, o resumo do indicador — por operação,
  quantos recortes feitos de quantos se aplicam — e o caminho para a tela do marco.
- **UX-091**: A tela do marco MUST mostrar o indicador como tabela, com um recorte por linha e uma
  operação por coluna, e cada célula MUST levar à tela daquele recorte e daquela operação.
- **UX-092**: A conferência do gesto MUST separar, com títulos próprios, os recortes que serão
  praticados, os que ficam fora e os impedidos, e o botão de confirmar MUST nomear a operação e a
  quantidade, como em *"Emitir 3 ordens"*.
- **UX-093**: O desfecho do gesto MUST começar pela contagem — quantos feitos, quantos recusados — e só
  depois listar os recortes. Os recusados vêm primeiro.

### Key Entities

- **Marco classificatório**: o marco como o Edital o publica, dentro de um Perfil. É a unidade do
  gesto e do indicador. Não é entidade nova.
- **Recorte**: o par (Perfil, Modalidade), pela derivação única. É a unidade do ato. Não muda.
- **Estado do recorte no marco**: leitura derivada, nunca gravada. É o par (recorte, operação) com um
  dos estados da `FR-811`.
- **Gesto**: a confirmação humana única. Não é ato e não tem tabela: deixa rastro nos N atos que
  produz, pela identificação comum da `FR-825`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-300**: Num marco de 4 recortes, ordenar, cortar, apurar e publicar como preliminar e como
  definitiva custa **5 confirmações**, contra **20** hoje, e as telas visitadas caem de ~16 para 1. No
  140/2025, os 64 recortes passam de 320 confirmações a 80, uma por marco e por operação.
- **SC-301**: Quem abre um marco sabe, **sem abrir nenhuma tela de recorte**, quais recortes faltam em
  cada uma das quatro operações.
- **SC-302**: Em **100%** dos gestos com recusa parcial, os recortes feitos continuam gravados e
  aparecem no desfecho e no indicador.
- **SC-303**: **0** atos são praticados sem terem sido mostrados na conferência, e **0** são praticados
  duas vezes pelo mesmo gesto repetido.
- **SC-304**: Cada ato produzido por um gesto é indistinguível, na autoria, no documento e na página
  pública, do mesmo ato praticado pela tela do recorte, salvo pela identificação do gesto na trilha.
- **SC-305**: A página do Edital com 16 marcos de 4 recortes abre com número de consultas ao banco
  que não cresce com o número de recortes.

## Decisões

### D-001 — O gesto é do marco como o Edital o publica, e não do conjunto de marcos homônimos

O marco mora dentro do Perfil (`classificationMilestones`), e cada Perfil tem os seus. No 140/2025 são
16 marcos de 4 recortes. O gesto processa os recortes **de um marco**. Juntar marcos de Perfis
diferentes pelo nome seria inferir uma equivalência que o Edital não declara.
*Confirmada pelo usuário em 28/09.*

### D-002 — O gesto pratica o primeiro ato do recorte; a sucessão continua por recorte

A sucessão de ordem, faixa ou apuração exige motivo, e a de ordem cita as decisões de recurso que
executa. Um motivo único para N sucessões diria a mesma razão para fatos diferentes. E o recurso
republica só o recorte que alcança: o gesto não pode suceder o que o recurso não tocou.
*Confirmada pelo usuário em 28/09.*

### D-003 — O recorte em que ninguém concorreu entra no alcance

A ordem vazia é estado legítimo desde a `034` (`FR-492a`), e deixar o recorte de fora o manteria em
*falta* para sempre no indicador. Vale para a ordem e para a publicação: a lista vazia divulgada diz
ao público que aquela lista não teve concorrentes. A conferência diz que ninguém concorreu.
*Confirmada pelo usuário em 28/09.*

### D-004 — O documento público continua por recorte

É a recomendação A da `DP-15`: o documento único do marco é o passo 4, e está fora de escopo.

### D-005 — O gesto mora numa tela nova, do marco

Uma tela por marco reúne o indicador inteiro e os quatro gestos, e a página do Edital leva a ela com o
resumo. Um botão "para todos" em cada tela de recorte obrigaria a pessoa a abrir um recorte para agir
sobre o marco, e espalharia o indicador por quatro lugares. As telas por recorte continuam sendo o
lugar da sucessão, do histórico e do ato isolado (`FR-831`).
*Confirmada pelo usuário em 28/09.*

## Fora de escopo

- Documento público único por marco (`DP-15`, passo 4).
- Gesto sobre vários marcos do Edital de uma vez (`D-001`).
- Suceder, em lote, ordem, faixa ou apuração obsoletas (`D-002`).
- Faixa seguinte do corte, que pede quantidade e motivo por recorte.
- Sorteio em lote: publicar a relação e realizar continuam por recorte, na tela do sorteio, e o
  congelamento do sorteio não muda.
- Convocação, comunicação e desfecho, que são o passo 3 (`DP-16`).
- Sinal novo na Supervisão para o recorte que ainda não começou: o indicador fica na página do Edital
  e na tela do marco.

## Invariantes que não mudam

- As tabelas append-only e a imutabilidade da publicação: nada é corrigido, tudo é sucedido.
- A derivação única do recorte (`editais/domain/recortes.py`).
- O congelamento do sorteio.
- O recurso republica só o recorte que alcança.
- A autoria: cada ato tem autor, e o autor de cada ato de um gesto é quem confirmou o gesto.

## Proteção de dados

Nenhum dado pessoal novo é coletado, gravado ou exposto. A tela do marco e a conferência mostram
contagens e rótulos de recorte, e não nomes: quem precisa das pessoas abre a tela do recorte, que já
tem a porta dela. Os atos gravados pelo gesto são os mesmos de hoje, com o mesmo conteúdo.

## Assumptions

- A `DP-17` é tratada como regra desta feature, esteja ou não já na Constituição quando ela for
  mesclada: o alcance é declarado antes da confirmação, e a automação não elimina a autoria.
- O número de recortes por marco é pequeno, até ~5 nos Editais da amostra. Um gesto pratica os atos
  em sequência na mesma requisição, sem fila de trabalho.
- As telas por recorte continuam sendo o lugar da sucessão, do histórico e do ato isolado.
