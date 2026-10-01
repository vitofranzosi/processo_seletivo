# Feature Specification: Polish das telas de operação

**Feature Branch**: `claude/polish-operation-screens-435f15`

**Created**: 2026-09-30

**Status**: Draft

**Input**: o prompt de sessão autônoma `doc/prompt/057-polish-telas-de-operacao.md`, escrito em
30/09/2026 a partir da auditoria de polish de UI (`doc/auditoria-polish-ui-2026-09-30.md`). É o
**lote 3 de 3** da proposta de execução da auditoria (§9): os itens T1, T2, T3, T4, D2, D5 e F8. O
lote 1 é a `055` (folha e componentes) e o lote 2 é a `056` (assistente de composição), as duas já
na `main`.

> **Faixa de identificadores.** Abre em **FR-1043**, **SC-398** e **UX-140**. O teto medido em
> 30/09/2026 em todas as worktrees, com quatro dígitos, era FR-1042, SC-397 e UX-139 — todos da
> `056`, já mergeada. As decisões desta spec nascem em `D-001` e moram no [research.md](research.md);
> as nove decisões que o prompt trouxe fechadas são **entrada**, e o research as registra como
> "decisões recebidas" (1ª a 9ª) sem reaproveitar a numeração delas.

**A frase que governa:**

> Em cada tela, a ação que se pratica todo dia é a mais visível, a excepcional é a mais discreta, e a
> destrutiva nunca é a mais forte.

**E a frase que mantém o corte:**

> Esta feature reordena, recolhe e formata o que já está na tela. Não acrescenta ação, não remove
> ação, não muda permissão nem o que cada ação faz.

---

## Por que esta feature existe

A auditoria de 30/09 mediu as telas de operação a 1280 × 900 no banco de demonstração e achou a
hierarquia de ações invertida justamente onde se trabalha todo dia:

- **No Detalhe do Edital, "Cancelar" é o único botão preenchido.** Sete ações empilhadas, uma por
  linha, e o gesto excepcional e destrutivo é o elemento mais forte da tela. "Quem atuou", ao lado,
  tem 515 px para ~160 px de conteúdo, esticado pela coluna vizinha.
- **Na Condução do marco, quatro botões primários empilhados**, todos com o mesmo peso.
- **Na Lista de Editais, a coluna "O que posso fazer" tem 5 ou 6 botões iguais**, cada linha com
  125 px, e "Cancelar" cai sozinho numa terceira linha, sem nada que o separe de "Retificar".
- **O mesmo glossário** ("Recorte é…, Faixa é…, Geração é…") abre as telas de marco, de corte, de
  ocupação, de convocação, de sorteio e de matrículas, antes da ação.
- **Caixa dentro de caixa.** A "Atenção" do Processo tem seis cartões com borda dentro de um cartão,
  com a faixa **verde** de sucesso para itens que pedem atenção; cada evento da Auditoria é um
  cartão de ~97 px; cada documento apresentado na inscrição é um cartão de largura total; e as
  fichas da Distribuição e da Minha etapa guardam dois dados em 1.232 px.
- **Números e datas como saída de máquina** na Revisão: "Peso: 2.0000", "20.0000%",
  "versão 2014-06-09", "2 vaga(s) imediata(s)".
- **A matriz de Alocação** faz a página inteira rolar na horizontal (1.398 px em 1.280), com um
  cabeçalho de 174 px que repete o número do Edital em cada coluna.
- **No portal, o envio de documento** quebra seletor e "Enviar" em duas linhas, com a dica de
  formato depois do botão.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — No Detalhe do Edital, a ação do dia é a mais visível e a destrutiva, a mais discreta (Priority: P1)

Quem abre um Edital vê, em "O que fazer agora", **uma** ação em destaque — a que o fluxo pede a
seguir —, as demais em linha, e Encerrar e Cancelar separados, por último, contornados e marcados
como irreversíveis.

**Why this priority**: é a tela mais aberta da gestão, e hoje ensina que o gesto mais forte é o de
cancelar.

**Independent Test**: abrir o Detalhe do Edital 01/2026 com `ana.gestora` a 1280 × 900 e contar as
ações preenchidas, a posição de Encerrar e Cancelar e a altura de "Quem atuou".

**Acceptance Scenarios**:

1. **Given** um Edital publicado, **When** o Detalhe é aberto por quem tem todos os papéis, **Then**
   no máximo uma ação é preenchida, e nenhuma delas é Encerrar ou Cancelar.
2. **Given** o mesmo Edital, **When** as ações são lidas na ordem, **Then** Encerrar e Cancelar vêm
   por último, num grupo separado das demais, contornados, cada um com o marcador "irreversível".
3. **Given** um Edital homologado, **When** o Detalhe é aberto, **Then** "Publicar" é a ação em
   destaque, com o marcador "irreversível".
4. **Given** uma ação indisponível com motivo, **When** renderizada, **Then** ela continua
   desabilitada, com o motivo visível ao lado.
5. **Given** o Detalhe a 1280 px, **When** medido, **Then** "Quem atuou" tem a altura do próprio
   conteúdo, e não a da coluna vizinha.

---

### User Story 2 — Na Condução do marco, um gesto em destaque (Priority: P1)

Quem conduz o marco inteiro vê os gestos disponíveis lado a lado, com o primeiro da ordem das
operações em destaque e os demais secundários.

**Why this priority**: quatro primários empilhados não dizem por onde começar.

**Independent Test**: abrir a Condução de um marco com operações em falta e contar os botões
preenchidos.

**Acceptance Scenarios**:

1. **Given** um marco com mais de um gesto disponível, **When** a Condução é aberta, **Then** só o
   primeiro gesto, na ordem ordem → corte → apuração → publicação, é preenchido.
2. **Given** um marco com um gesto só, **When** aberta, **Then** ele é o preenchido.
3. **Given** os gestos, **When** enviados, **Then** cada um leva à mesma conferência de antes, com os
   mesmos campos.

---

### User Story 3 — Na Lista de Editais, cada linha cabe em pouco espaço (Priority: P1)

Quem abre a página inicial da gestão lê, em cada Edital, as ações frequentes primeiro, as
destrutivas no fim e separadas, e os contadores zerados esmaecidos.

**Why this priority**: é a tela de uso diário, e as linhas altas deixam poucos Editais na dobra.

**Independent Test**: medir a altura de uma linha da Lista com `ana.gestora` a 1280 px.

**Acceptance Scenarios**:

1. **Given** a Lista com um Edital publicado, **When** medida a 1280 px, **Then** a linha tem no
   máximo 90 px.
2. **Given** a mesma linha, **When** lida na ordem, **Then** Encerrar e Cancelar vêm por último,
   separados das demais.
3. **Given** uma ação com contador zero, **When** renderizada, **Then** ela aparece esmaecida, com o
   rótulo e o contador inteiros, e continua levando ao mesmo lugar.

---

### User Story 4 — O glossário está à mão, e não na frente (Priority: P2)

Quem abre uma tela de marco — ordem, corte, ocupação, convocação, sorteio — ou a de matrículas
encontra a ação logo abaixo do título, e o glossário de termos num controle fechado, no mesmo lugar,
que abre com um clique. A faixa "abrir esta tela não pratica nada" continua visível.

**Why this priority**: o glossário serve no primeiro contato e atrapalha em todos os outros.

**Independent Test**: medir o topo do primeiro controle ou da primeira tabela de cada tela, antes e
depois; conferir que a varredura de vocabulário continua verde.

**Acceptance Scenarios**:

1. **Given** uma dessas telas, **When** aberta, **Then** o glossário está num controle fechado, com
   o mesmo texto de antes, e a faixa "não pratica nada" está à vista.
2. **Given** o controle aberto, **When** lido, **Then** cada termo continua definido no primeiro
   uso, com a mesma frase.
3. **Given** o assistente de composição, **When** aberto, **Then** o glossário dele fica como está.

---

### User Story 5 — Atenção, auditoria e documentos sem caixa dentro de caixa (Priority: P2)

Quem lê a "Atenção" do Processo ou da Supervisão vê uma lista com divisores e a faixa âmbar de
aviso; quem lê a trilha de auditoria vê eventos em lista; quem confere uma inscrição vê os
documentos no desenho da mesa do avaliador; quem abre a Distribuição ou a Minha etapa vê a ficha na
largura do que ela diz.

**Why this priority**: o que se lê em sequência não deveria ter uma moldura por item.

**Independent Test**: medir a altura média de evento na Auditoria do Edital 51/2026, e conferir que
nenhuma dessas telas tem caixa com borda dentro de outra.

**Acceptance Scenarios**:

1. **Given** a "Atenção" com sinais, **When** renderizada, **Then** os sinais formam uma lista com
   divisor entre eles e uma faixa âmbar, sem borda própria por sinal.
2. **Given** a Auditoria do Edital 51/2026, **When** medida, **Then** a altura média por evento é de
   no máximo 70 px, e todo dado do evento continua na tela.
3. **Given** o Detalhe de uma inscrição, **When** os documentos são lidos, **Then** cada requisito
   ocupa uma linha da lista, com o arquivo, o tamanho, a data, o resumo SHA-256 e as ações
   "Visualizar" e "Baixar" — ou "Não apresentado.".
4. **Given** a Distribuição ou a Minha etapa, **When** abertas a 1280 px, **Then** a ficha tem a
   largura do conteúdo.

---

### User Story 6 — Números, datas e plurais como uma pessoa os escreve (Priority: P2)

Quem confere a Revisão, a Supervisão ou a Condução lê "Peso: 2", "20%", "versão 09/06/2014" e
"2 vagas imediatas".

**Why this priority**: a mesma tela que exige rigor apresenta o número como saída de máquina.

**Independent Test**: abrir a Revisão do 76/2027 e procurar "2.0000", "(s)" e datas aaaa-mm-dd.

**Acceptance Scenarios**:

1. **Given** a Revisão do 76/2027, **When** lida, **Then** aparecem "Peso: 2", "Nota mínima: 6",
   "20%", "versão 09/06/2014" e "2 vagas imediatas".
2. **Given** um texto composto pela interface que vai para o conteúdo publicado, o PDF ou o "o que
   mudou" de uma Retificação, **When** a feature termina, **Then** ele está como antes.
3. **Given** o envio de uma etapa do assistente, **When** comparado com o de antes, **Then** ele é
   idêntico.

---

### User Story 7 — A matriz de Alocação cabe na janela (Priority: P3)

Quem aloca pessoas em Etapas vê o número de cada Edital uma vez, numa linha de grupo sobre as Etapas
dele, e um cabeçalho compacto; a página não rola na horizontal a 1280 px.

**Why this priority**: incomoda com muitas Etapas, e a decisão do cabeçalho fixo já está tomada.

**Independent Test**: abrir a Alocação do Processo do seed a 1280 px e medir a largura da página e a
altura do cabeçalho.

**Acceptance Scenarios**:

1. **Given** as nove Etapas do seed, **When** a Alocação é aberta a 1280 px, **Then** a página tem no
   máximo 1.280 px de largura e o cabeçalho, no máximo 130 px de altura.
2. **Given** a matriz, **When** se rola a página para baixo, **Then** o cabeçalho continua fixo à
   janela.
3. **Given** a matriz, **When** se lê uma coluna, **Then** ela continua dizendo de qual Edital é a
   Etapa, e as ações "Distribuir", "Todos" e "Nenhum" continuam nela.

---

### User Story 8 — No portal, um documento se envia numa linha (Priority: P3)

O candidato encontra, em cada documento, o seletor, o nome do arquivo e "Enviar" na mesma linha,
com a dica de formato junto do seletor.

**Why this priority**: incômodo de leitura, sem bloqueio.

**Independent Test**: abrir "Sua inscrição" no portal a 1280 px e contar as linhas de controles de
um documento.

**Acceptance Scenarios**:

1. **Given** um documento a enviar, **When** aberto a 1280 px, **Then** seletor e "Enviar" estão na
   mesma linha.
2. **Given** a janela de 375 px, **When** aberta, **Then** a linha pode quebrar, e nada fica cortado.

---

### Edge Cases

Os casos-limite desta feature são requisitos, e estão escritos como tal abaixo — a seção de casos
de borda não entra na matriz de rastreabilidade, e nenhuma ferramenta a cobra:

- o ato que o fluxo pede está indisponível por segregação ou pendência (**FR-1045**);
- Edital sem ação nenhuma para o papel (**FR-1046**);
- marco com um gesto só, e marco sem gesto (**FR-1048**);
- contador zero (**FR-1050**);
- o glossário cuja definição está dentro do subtítulo (**FR-1052**);
- "Atenção" sem sinal (**FR-1054**);
- documento facultativo, documento não apresentado e lista reconstruída (**FR-1056**);
- texto que sai da tela — conteúdo publicado, PDF, "o que mudou" (**FR-1060**);
- busca na Alocação que filtra todas as linhas, e Processo com um Edital só (**FR-1062**);
- janela de 375 px (**FR-1068**).

---

## Requirements *(mandatory)*

### Functional Requirements

**Hierarquia de ações no Detalhe do Edital (T2)**

- **FR-1043**: Em "O que fazer agora" do Detalhe do Edital, no máximo **uma** ação MUST ser
  preenchida: a que o fluxo pede a seguir. A preferência é, nesta ordem: a ação de elaborar, quando
  oferecida; o ato que avança o Edital (submeter, homologar, publicar); e "Inscrições recebidas".
- **FR-1044**: As ações que encerram ou interrompem o Edital — Encerrar e Cancelar — MUST vir por
  último, num grupo separado das demais, **contornadas e nunca preenchidas**, cada uma com o
  marcador "irreversível" que já existe. As demais ações MUST ficar em linha, com quebra, e não uma
  por linha.
- **FR-1045**: Quando a ação que o fluxo pede está indisponível — por segregação de funções ou por
  pendência impeditiva —, ela MUST continuar desabilitada, com o motivo à vista, e nenhuma outra MUST
  ser promovida a preenchida no lugar dela.
- **FR-1046**: Quando não há ação para o papel, a frase "Nenhum ato disponível para seus papéis nesta
  situação." MUST continuar.
- **FR-1047**: As colunas do Detalhe MUST alinhar pelo topo: "Quem atuou" tem a altura do próprio
  conteúdo.

**Hierarquia de gestos na Condução do marco (T2)**

- **FR-1048**: Na Condução do marco, só o primeiro gesto disponível, na ordem das operações, MUST
  ser preenchido; os demais MUST ser secundários, lado a lado, com quebra. Com um gesto só, ele é o
  preenchido; sem gesto, a tela fica como antes.

**A coluna de ações da Lista de Editais (T1)**

- **FR-1049**: Na coluna "O que posso fazer" da Lista, as ações MUST vir em linha, as frequentes
  primeiro — Inscrições recebidas e Recursos aguardando decisão —, e Encerrar e Cancelar no fim,
  separados das demais.
- **FR-1050**: Ação cujo contador é zero MUST aparecer esmaecida, com o rótulo e o contador
  inteiros, e continuar levando ao mesmo lugar. O rótulo de uma ação MUST NOT mudar enquanto algum
  teste o prender; nesse caso só a ordem muda.

**O glossário recolhido (D2)**

- **FR-1051**: Nas telas de ordem, corte, histórico do corte, ocupação, convocação, sorteio e
  condução do marco, e na de matrículas, o bloco de definições ("Recorte é…, Faixa é…,
  Geração é…") MUST ir para um controle de ajuda recolhida no padrão "como preencher", **fechado**,
  no mesmo lugar, com o mesmo texto. O rótulo do controle MUST NOT usar os termos que o bloco define,
  para que a primeira ocorrência de cada termo continue sendo a definição.
- **FR-1052**: Onde a definição é parte do subtítulo, e não bloco próprio, ela MUST ficar como está:
  recolhê-la exigiria mudar o texto.
- **FR-1053**: A faixa "abrir esta tela não pratica nada" e as suas irmãs ("não apura nada", "o
  arquivo não fica guardado") MUST continuar visíveis. O glossário do assistente de composição MUST
  ficar como está.

**Caixa dentro de caixa (T3)**

- **FR-1054**: A "Atenção" do Processo e da Supervisão MUST ser uma lista com divisor entre os
  sinais e a faixa **âmbar** do aviso, sem borda própria por sinal. Sem sinal, a linha de ausência
  MUST continuar.
- **FR-1055**: A trilha de auditoria MUST ser uma lista de eventos com divisor, sem cartão por
  evento, com todos os dados de antes: quando, operação, agregado, alvo, ator, base de autorização,
  transição e motivo.
- **FR-1056**: Os documentos apresentados no Detalhe da inscrição MUST adotar o desenho da lista de
  documentos da mesa do avaliador — uma linha por requisito, numa grade comum —, com os dados de
  antes: nome, a marca de facultativo, a razão, o arquivo, o tamanho, a data, o resumo SHA-256, e
  "Visualizar" e "Baixar"; ou "Não apresentado.". O aviso de lista reconstruída e a seção "Não se
  aplicam" MUST continuar.
- **FR-1057**: As fichas da Distribuição e da Minha etapa MUST ter a largura do conteúdo. As da mesa
  e do recurso MUST ficar como estão.

**Números, datas e plurais (F8)**

- **FR-1058**: Na Revisão, o percentual da Modalidade, o peso e a nota mínima da Etapa MUST sair sem
  zeros à direita e com vírgula decimal, sem arredondar; a data da versão da norma MUST sair em
  dd/mm/aaaa; e "vaga(s)" e as demais marcas de plural com parênteses que a Revisão compõe MUST sair
  no plural certo.
- **FR-1059**: Os textos que a Supervisão e a Condução do marco compõem com "vaga(s)" para a tela
  MUST sair no plural certo.
- **FR-1060**: Texto que a interface compõe e que sai da tela — para o conteúdo publicado, o PDF ou
  o "o que mudou" de uma Retificação — e valor enviado por formulário MUST NOT mudar. O que ficar por
  esse motivo MUST virar registro.

**A matriz de Alocação (T4)**

- **FR-1061**: A matriz MUST trazer o número de cada Edital numa linha de grupo, sobre as Etapas
  dele, e MUST NOT repeti-lo em cada coluna. Os controles do cabeçalho — "Distribuir", "Todos" e
  "Nenhum" — MUST ficar mais compactos, com os mesmos nomes acessíveis.
- **FR-1062**: Em tela larga, a moldura MUST continuar sem rolagem interna, e o cabeçalho MUST
  continuar fixo à janela, inclusive a linha de grupo. Com busca que filtra todas as linhas, e com um
  Edital só, a matriz MUST continuar legível.

**O envio de documento no portal (D5)**

- **FR-1063**: No bloco de cada documento de "Sua inscrição", o seletor, o nome do arquivo e
  "Enviar" MUST ficar numa linha a 1280 px, com a dica de formato junto do seletor. O comportamento
  dos scripts de arquivo e de envio MUST NOT mudar.

**Limites da feature**

- **FR-1064**: Para cada tela tocada, a lista de destinos de ação — `href` dos links de ação e
  `action`/`formaction` dos formulários e botões — MUST ser idêntica antes e depois, por papel,
  medida com `ana.gestora` (todos os papéis) e com `joana.avaliadora`.
- **FR-1065**: A feature MUST NOT acrescentar ação, remover ação, mudar permissão, criar view ou
  recusa nova, nem mudar o que cada ação faz.
- **FR-1066**: O HTML da tela de distribuição MUST continuar abaixo de 120.000 caracteres, com o
  tamanho antes e depois declarado. Comentário novo de folha nasce como comentário do template; as
  regras que a feature torna mortas saem junto; estilo de uma tela só vai para o bloco de estilo
  dela.
- **FR-1067**: A feature MUST NOT tocar o PDF, o conteúdo publicado, o título do `seed_demo` nem o
  assistente de composição além da formatação da Revisão.
- **FR-1068**: A 375 px, a Lista, o Detalhe do Edital, a Alocação e o envio de documento do portal
  MUST NOT ficar piores do que estavam: nenhum controle que se alcançava deixa de se alcançar, e a
  página só rola na horizontal onde já rolava. O que já estava cortado antes da feature vira
  registro, e não escopo.

### Requisitos de experiência

- **UX-140**: Em cada grupo de ações, o peso visual MUST seguir a frequência e a reversibilidade: uma
  ação preenchida, as secundárias contornadas e iguais entre si, e a destrutiva nunca mais forte que
  a ação do dia.
- **UX-141**: Ajuda que serve ao primeiro contato MUST ficar à mão e recolhida; garantia ao operador
  ("não pratica nada") MUST ficar à vista.
- **UX-142**: Item que se lê em sequência MUST se separar por divisor, e não por moldura.

### Key Entities

Não há entidade de domínio nova nem alterada. Os elementos são desenhos da gestão e do portal:

- **Grupo de ações** do Detalhe do Edital e da Lista: o conjunto que `acoes.do_edital` já monta, agora
  em três partes — a principal, as secundárias e as que encerram ou interrompem.
- **Gesto do marco**: as operações de condução em lote, na ordem das operações.
- **Sinal de Atenção**, **evento de auditoria**, **requisito apresentado** e **ficha**.

---

## Success Criteria *(mandatory)*

Medidos no banco `ps_057_polish` (cópia de `ps_polish_audit`, o banco da auditoria), a 1280 × 900,
antes e depois; a tabela vai para [verificacao.md](verificacao.md).

### Measurable Outcomes

- **SC-398**: No Detalhe do Edital 01/2026, no máximo uma ação preenchida; Encerrar e Cancelar por
  último, separados e contornados; "Quem atuou" com a altura do próprio conteúdo (antes: 515 px).
- **SC-399**: Na Condução de um marco com mais de um gesto, um só preenchido (antes: todos).
- **SC-400**: A linha da Lista de Editais tem no máximo 90 px (antes: 125), com as destrutivas no
  fim.
- **SC-401**: Nas telas de marco e na de matrículas, o glossário está fechado, a faixa "não pratica
  nada" à vista, o primeiro controle ou tabela sobe ao menos 120 px, e a varredura de vocabulário
  fica verde.
- **SC-402**: A "Atenção" do Processo e da Supervisão é lista com divisor e faixa âmbar.
- **SC-403**: A Auditoria do Edital 51/2026 tem no máximo 70 px por evento, em média (antes: 97).
- **SC-404**: Os documentos do Detalhe da inscrição seguem o desenho da mesa, e nenhuma das telas de
  T3 tem caixa com borda dentro de outra.
- **SC-405**: A Revisão do 76/2027 mostra "Peso: 2", "Nota mínima: 6", "20%", "versão 09/06/2014" e
  "2 vagas imediatas", e nenhum "(s)".
- **SC-406**: A Alocação, a 1280 px com as nove Etapas do seed, tem a página com no máximo 1.280 px
  de largura (antes: 1.398) e o cabeçalho com no máximo 130 px (antes: 174).
- **SC-407**: No portal, cada documento tem uma linha de controles a 1280 px.
- **SC-408**: A lista de destinos de ação por papel é idêntica antes e depois, em toda tela tocada.
- **SC-409**: A suíte (`make lint check test-pg`, com os testes de JavaScript) fica verde, e o HTML
  da distribuição continua abaixo de 120.000 caracteres, com o tamanho antes e depois registrado.
- **SC-410**: A 375 px, a Lista, o Detalhe, a Alocação e o envio do portal não ficam piores do que
  estavam, controle a controle.

### O que esta feature não cobre, deliberadamente

- a repetição do número do Edital no cabeçalho (D3: é do título do `seed_demo`);
- o tamanho do Retificar e a repetição entre Processo e Supervisão (estruturais, registrados);
- qualquer mudança no PDF ou no conteúdo publicado.

Se um requisito acima prometer isso, está prometendo outra feature.

---

## Assumptions

- A medição "antes" é feita sobre `94cb4914` (a `main` com a `055`, a `056` e a conversão dos
  comentários da folha), no banco `ps_057_polish`, antes de qualquer template ou folha mudar.
- A conversão dos comentários documentais da folha da gestão para comentário do template já está na
  `main` (commit `1c4ae6c4`, da `056`), e por isso não é tarefa deste lote.
- "Idêntica" na lista de ações (**FR-1064**) é a lista ordenada e sem repetição dos destinos de ação
  da página, sem o token de CSRF e sem os links de navegação comuns a toda página (cabeçalho e
  trilha).
- As medidas são do `getBoundingClientRect` na página renderizada no navegador do aplicativo,
  arredondadas ao pixel; as de 375 px, com o viewport emulado.
- Os números-alvo (90 px, 120 px, 70 px, 1.280 px, 130 px) vêm do prompt. Meta numérica fora de
  alcance dentro do escopo não amplia o escopo: o valor alcançado e a justificativa vão para o
  `verificacao.md`.
