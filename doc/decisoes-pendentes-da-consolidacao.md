# Decisões pendentes — o que a auditoria de consolidação deixou para o usuário

**Situação: abertas, menos a `DP-01` a `DP-06`, decididas em 26/09, o item 2 da `DP-08`, decidido na mesma data, a `DP-13` e a `DP-14`, decididas em 27/09, e a `DP-16` e a `DP-17`, decididas em 28/09** — as quatro primeiras com
a proposta que abriu a [`045`](../specs/045-conducao-confiavel-processo/spec.md), a `DP-06` ao especificar a
[`046`](../specs/046-contrato-de-executabilidade/spec.md), e a `DP-05` ao recusar a proposta de uma spec de
cadastro de reserva. Este documento organiza as alternativas e
recomenda; **quem decide é o usuário**.
Nenhuma spec das que dependem destas decisões começa antes delas. Quando uma for tomada, a seção dela
ganha um bloco **"O que foi decidido"**, como a
[decisão do recorte documental](decisao-recorte-documental.md) ganhou em 25/09. Ela não é apagada nem
reescrita.

**Origem:** a §13 da [auditoria de consolidação de 26/09](auditoria-de-consolidacao-2026-09-26.md). Os
identificadores `RC-nn` e `B-nn` são os de lá. Os fatos citados foram conferidos contra a `main` em
`bb774d9`.

**As `DP-13` a `DP-18` têm outra origem:** a reavaliação de 27/09 e a avaliação da priorização dela.
Estão em [Depois da reavaliação de 27/09](#depois-da-reavaliação-de-2709), junto com o critério e a
ordem adotados naquela data, e foram conferidas contra a `main` em `8dd4f942`.

**Duas famílias de decisão não são repetidas aqui**, porque já têm registro próprio, e um segundo
registro criaria duas verdades:

| Decisão | Onde já está registrada |
|---|---|
| Redação no sistema ou transcrição (E10) · conteúdo comum aos Perfis (E2) · conjunto de seções do documento (E5) | [estudo de esforço](estudo-esforco-de-cadastro-2026-09-21.md) §15, "Três decisões, antes de qualquer spec" (a E6 já foi decidida em 25/09). *Desde 28/09, as opções e o custo da E5 e da E10 estão na [`DP-20`](#dp-20--o-pdf-do-sistema-vale-como-edital-oficial-o-que-ele-precisa-ter-e-com-quais-seções); a pergunta continua registrada no estudo, e a decisão, quando vier, entra na `DP-20`.* |
| Âncora da regra do ano (FR-344) · remeter o método comum do sorteio (FR-465/466) · Casas decimais e Arredondamento no marco de sorteio | [estudo de esforço](estudo-esforco-de-cadastro-2026-09-21.md) §12, itens 5, 10 e 13 — "não é quick win… registrado aqui, não tomado" |
| Papel próprio de Diretoria | [spec 040](../specs/040-visao-institucional-dos-processos/spec.md), D-008 e G-010; comentário em `interface/identidade.py:66-70` |

## Índice

| # | Pergunta | O que destrava | Recomendação |
|---|---|---|---|
| DP-01 | O `status` do Evento é declarado ou derivado? | RC-80 · B-1 | derivar a progressão; `CANCELADO` continua declaração |
| DP-02 | O recurso aguardando admissibilidade entra no painel como espécie nova, ou o `UX-064` passa a cobrir as duas fases? | RC-79 · B-1 | ampliar o `UX-064` e o `UX-005` |
| DP-03 | O `UX-001` em Edital publicado é condição de Atenção? | RC-80 · B-1 | aviso na Revisão antes de publicar; fora da Atenção depois |
| DP-04 | O adiamento de "fechar a `038`" foi deliberado? | B-1 · condicionantes C1–C6 | não adiar mais; se foi deliberado, registrar |
| DP-05 | Cadastro de reserva está no alvo do piloto, e o que "limitado em N" significa? | RC-58 · B-5 | validar primeiro; uma fonte só para o limite |
| DP-06 | O Cefor usa dupla leitura? | RC-29 · B-3 | aviso agora; regra de combinação só com Edital real |
| DP-07 | A `D-G2` (três recusas em 403) continua valendo? | RC-94 | manter, com prioridade baixa |
| DP-08 | A `039` está encerrada? Para onde vão a `D-G5` e o alcance da Etapa? | RC-102 · RC-37 · RC-64 | encerrar; `D-G5` com a B-4, alcance com as famílias |
| DP-09 | A `D-011` (sem prova nova no recurso) continua? | RC-89 | manter |
| DP-10 | Quais famílias de Edital entram no alvo? | RC-55 · RC-59 · RC-64 · RC-65 · B-17 | nenhuma agora; decidir por família, com Edital na mão |
| DP-11 | A comissão local enxerga só o seu Perfil ou polo? | RC-61 · B-12 | não agora; coluna e filtro de Perfil já |
| DP-12 | O campo `Status` das specs é mantido ou abolido? | RC-103 | abolir o campo e manter um índice só |
| DP-13 | "Aplicar a todos": o que acontece com o que o Perfil de destino já declarava? | passo 1 · TF-1 da `043` | declarar o efeito por tipo de estrutura, com prévia |
| DP-14 | Quando a inscrição oferece a ampla concorrência? | passo 0 · A-1 da `048` | sempre que o Perfil tiver linha geral com vagas |
| DP-15 | Documento público por marco? | passo 4 | não agora; se vier, documento que reúne os atos |
| DP-16 | O não atendimento pode ser registrado em lote? | passo 3 | um gesto, N registros com autor — **decidida em 28/09: B** |
| DP-17 | A automação explícita entra na Constituição? | passo 1 | emenda ao Princípio IV, só o invariante |
| DP-18 | Quem faz o teste operacional, e quando? | passo 0,5 | depois do passo 0, com o 28/2026 |
| DP-19 | Marcar na composição os campos que não se corrigem depois de publicados é requisito novo? | passo 0 → fora dele | decidir em spec; conciliar com a `026` §7 e a `FR-428` da `030` |
| DP-20 | O PDF do sistema vale como Edital oficial: o que ele precisa ter, e com quais seções? (E5 · E10) | RC-20, RC-21, RC-23 a RC-26 | o RC-20 e o teto já, como correção; assinatura e E10 antes; fecho e seções numa spec só |
| DP-21 | A composição grava coleções maiores que mil campos? | o Edital multicampi da `051` (66 Perfis); o achado de 29/09 | subir o limite, com valor medido; decidir antes do primeiro Edital acima de ~18 Perfis |

---

## DP-01 — O `status` do Evento é declarado ou derivado?

*Decide o `N-06` e, com ele, dois terços do ruído do painel.*

### O problema

Duas specs dizem coisas opostas sobre o mesmo campo, e o código não segue nenhuma das duas:

- **A `022`, D-004**: *"`EventoCronograma.status` é preenchido à mão e nasce `PLANEJADO`… substituí-lo
  por derivação das datas apagaria uma declaração que alguém fez de propósito."* O `UX-002` foi
  desenhado sobre essa premissa. Ele mostra o declarado ao lado da posição no relógio e não arbitra
  (`interface/supervisao.py:635-662`).
- **A `026`**: `("schedule", "status"): derivado()` (`editais/domain/mutabilidade.py:432`). Um campo
  derivado não se retifica, e a convergência de 20/09 vetou pô-lo na Retificação (§21).
- **O código**: ninguém declara nem deriva. O modelo nasce `PLANEJADO`
  (`editais/models/cronograma.py:29`), a composição não oferece o campo (`_evento.html` não tem
  entrada; `interface/forms.py:1330` só o preserva), e a Retificação não o oferece porque é derivado.
  Só a API aceita outro valor (`editais/api/serializers.py:186`). O resultado é um `UX-002` permanente
  para todo Evento cujo início já passou.

### O que já está fixado

- **Publicação é ato imutável.** Se o `status` fosse declarado, cada mudança de fase — planejado, em
  andamento, concluído — seria uma Retificação publicada. Não há Edital que declare "o período de
  inscrições está em andamento" como norma.
- **`CANCELADO` é outra coisa.** Um Evento cancelado é **declaração normativa**: muda o que o Edital
  diz. Nenhuma data o deriva. Hoje ele também é inalcançável pela interface.

### As opções

| | A. Derivar a progressão | B. Declarar, fora do conteúdo normativo | C. Declarar pela Retificação |
|---|---|---|---|
| **O que é** | `PLANEJADO`, `EM_ANDAMENTO` e `CONCLUIDO` passam a ser calculados das datas e do relógio, na leitura. `CANCELADO` continua sendo o único valor declarado. | O `status` sai do conteúdo publicado e vira registro operacional da condução, que a presidência atualiza. | O `status` passa a retificável e a Retificação o oferece. |
| **`UX-002`** | Deixa de disparar por progressão. Só sobra divergência real — um Evento `CANCELADO` com etapa correndo, se isso importar. | Continua como a 022 o desenhou: declarado × relógio. | Continua, com o custo de uma Retificação por mudança de fase. |
| **Contrato** | A `026` já diz derivado. A `022` D-004 é **substituída explicitamente**. | As duas mudam: a 026 perde o campo, e surge um registro novo. | A `026` muda, contra o veto de 20/09. |
| **Custo** | O menor: leitura derivada, e o campo publicado deixa de ser lido. | Um modelo novo, uma tela e uma permissão. | Pequeno em código, absurdo em uso: fase de Evento como ato normativo. |

### Recomendação: **A**

É a única que não pede a ninguém trabalho manual para manter um dado que as datas já contêm. O receio da
`022` era derivar **atraso** e produzir alarme falso. Derivar a **fase** das datas não produz alarme
nenhum: produz o que o relógio diz. `CANCELADO` fica como declaração, e o caminho para declará-lo — uma
Retificação que cancela o Evento — é outra pergunta, que só vale abrir quando houver caso.

**Se decidida:** a spec curta da B-1 registra que a D-004 da `022` foi substituída, e o `UX-002` é
reescrito ou retirado do catálogo, com a `FR-565` da `038`.

### O que foi decidido

Em 26/09/2026, o usuário escolheu a **A**, na proposta que abriu a
[`045`](../specs/045-conducao-confiavel-processo/spec.md): *"a fase ordinária de um Evento será
derivada de suas datas e do instante corrente"*, sem controle manual para planejado, em andamento ou
encerrado, e `CANCELADO` continua declarável. A `D-004` da `022` fica expressamente substituída.

Ao especificar, a conferência contra o código acrescentou duas coisas: o `UX-002` é **retirado**, e
não reescrito — derivada a fase, declarado e relógio não têm como discordar —; e a derivação usa a
régua do vencido da `037` e, para o período de inscrições, a régua do próprio período. Ver a `D-001`
da `045`.

---

## DP-02 — O recurso aguardando admissibilidade entra no painel como espécie nova, ou o `UX-064` passa a cobrir as duas fases?

*Decide o `N-02`: a peça com prazo que hoje não aparece em superfície nenhuma.*

### O problema

`sinais_do_recurso` lê só as peças `AGUARDANDO_JULGAMENTO` (`interface/supervisao.py:1162-1167`). A FR-561
da `038` foi escrita assim. Um recurso recém-interposto fica invisível no painel **exatamente** durante a
fase em que o prazo institucional de resposta corre. E a recuperação lateral, "Recursos recebidos (N)"
na lista de Processos, conta também os já decididos (`interface/acoes.py:120-127`).

### O que já está fixado

- **Admitir e julgar exigem a mesma capacidade**, `recurso:julgar` (`recursos/application/admitir.py:26`),
  **e a mesma regra de impedimento** (`admitir.py:54`). Para o painel, as duas fases têm o mesmo ator,
  o mesmo impedimento e o mesmo destino.
- **O catálogo da `038` é fechado**: *"Cada espécie nova ganha o seu identificador, com a condição que a
  define"* (spec 038, antes da `FR-561`).
- **`UX-005` e `UX-064` são a partição de um mesmo cálculo**: comissão inteira impedida × julgador
  disponível. Nenhuma peça cai nos dois.

### As opções

| | A. Ampliar `UX-064` e `UX-005` | B. Um par de espécies novas para a admissibilidade |
|---|---|---|
| **O que é** | A condição passa de "aguardando julgamento" para "**aguardando decisão** — admissibilidade ou julgamento". A mensagem diz qual fase. | Duas espécies novas, "admissibilidade com julgador disponível" e "admissibilidade com comissão impedida", com identificadores próprios. |
| **Leitor** | Um sinal por peça pendente, com a fase escrita. | Um sinal por peça, em quatro espécies. |
| **Catálogo** | A FR-561 é emendada; o catálogo não cresce. | Cresce em dois; a partição continua valendo em cada fase. |
| **Custo** | Um filtro e uma frase. | Um filtro, duas espécies, testes e textos. |

**Nas duas**, o contador "Recursos recebidos (N)" passa a contar só as peças pendentes, ou a dizer
quantas estão pendentes.

### Recomendação: **A**

Para quem conduz, é o mesmo fato: uma peça espera decisão de quem tem `recurso:julgar`. A distinção entre
as fases mora na tela do recurso, que já a faz bem. Espécies separadas multiplicariam o catálogo por uma
diferença que não muda quem age nem onde.

### O que foi decidido

Em 26/09/2026, o usuário deixou a escolha ao critério *"a solução de menor complexidade que preserve
clareza para o operador"*, evitando dois sinais para a mesma peça. É a **A**: o `UX-064` e o `UX-005`
passam a cobrir *aguardando decisão*, e a mensagem diz a fase. O contador *"Recursos recebidos (N)"*
passa a contar só as pendentes. Ver a `D-002` da
[`045`](../specs/045-conducao-confiavel-processo/spec.md).

---

## DP-03 — O `UX-001` em Edital publicado é condição de Atenção?

*Decide a outra metade do `N-05`, a que derivar o `status` não resolve.*

### O problema

O `UX-001` diz *"A Etapa X está sem marco no cronograma"* e leva à Retificação das Etapas
(`interface/supervisao.py:1273-1274`). Mas `scheduleEventId` é **estrutural**
(`editais/domain/mutabilidade.py:447`), e a Retificação não acrescenta Etapa. Num Edital publicado, o
sinal aponta para uma tela que **nunca** o resolve. O próprio código reconhece que a ausência *"é
publicável e legítima"*, e que torná-la impeditiva *"mudaria o que o sistema aceita publicar"*
(`supervisao.py:604-615`).

### O que já está fixado

- **Não silenciar o `UX-001`** (convergência §21): ele reporta um fato verdadeiro.
- **Não pôr `scheduleEventId` na Retificação** (convergência §21): mascararia o problema.
- **A Atenção é "há trabalho parado"**; os avisos de composição são "a composição tem imperfeição"
  (convergência §21, sobre o `N-08`).

### As opções

| | A. Aviso de composição antes de publicar; fora da Atenção depois | B. Continua na Atenção, sem destino | C. `scheduleEventId` passa a poder nascer por Retificação |
|---|---|---|---|
| **Antes da publicação** | A Revisão avisa, e não impede: "esta Etapa não tem marco no cronograma". | Como hoje. | Como hoje. |
| **Depois** | Sai da Atenção: não há trabalho a fazer. | Fica como fato estrutural, sem link e dito como tal. | Ganha destino real: acrescentar o vínculo. |
| **Contrato** | Não muda. | Não muda. | Muda na `026` (estrutural → pode nascer), e a trilha precisa dizer a que o Evento passou a servir. |
| **Ruído no painel** | Some. | Continua, uma linha por Etapa. | Some, depois que alguém retifica. |

### Recomendação: **A**

O momento em que a ausência pode ser corrigida sem custo é a composição, e é lá que ela deve ser dita. Um
painel de condução que mostra, para sempre, um fato sobre o qual ninguém pode agir treina a pessoa a
ignorá-lo. É o que a convergência mediu: 6 dos 15 sinais do gestor eram `UX-001`. A C é possível, mas é
mudança de contrato para um caso que nenhum Edital da amostra pediu.

### O que foi decidido

Em 26/09/2026, o usuário escolheu a **A**: *"quando uma condição pertence à composição/publicação e não
possui correção operacional naquele momento, ela não deve ser apresentada na Atenção"*, e a informação
vai para a superfície de composição e revisão, como aviso. Sem inventar Retificação para dar destino
ao sinal.

A conferência contra o código mostrou que o aviso **não existe** hoje — a validação confere a Etapa
que referencia Evento inexistente, e não a que não referencia nenhum —, e que o mesmo princípio alcança
o `UX-046` num Edital que já parou. Ver a `D-003` da
[`045`](../specs/045-conducao-confiavel-processo/spec.md).

---

## DP-04 — O adiamento de "fechar a `038`" foi deliberado?

*Não é uma escolha técnica: é o registro de uma priorização.*

### O fato

A convergência de 20/09 terminou com três investimentos em ordem: fechar a `038`, derivar o `status` e a
`D-G5`. E disse: "Não recomendo outro painel". Desde então, os arquivos do painel receberam um commit só,
`4ec1cbb`, que fechou o N-03. O trabalho foi para a `040`–`042`, o estudo de esforço, a `043` e a `044`.
Não há registro de que o adiamento tenha sido decidido.

### Por que importa

A própria convergência mostrou que **quem acumula papéis não encontra o N-01 nem o N-04**. Com a equipe
inicial de 2–3 pessoas, o piloto roda sem tropeçar neles, e é por isso que ele **não serve de prova** para
a operação institucional. Fechar a `038` é condição de saída do piloto (C1–C6).

### As opções

- **A. Foi deliberado.** Registrar a decisão, com a razão, e aceitar que o piloto não mede C1 e C4.
- **B. Não foi.** A B-1 entra primeiro na Onda A.

### Recomendação: **B**

A B-1 é pequena e já tem quase todo o diagnóstico escrito. Com a DP-01, a DP-02 e a DP-03 decididas, ela
cabe numa spec curta.

### O que foi decidido

Em 26/09/2026, o usuário abriu a B-1 como a spec seguinte — a
[`045`](../specs/045-conducao-confiavel-processo/spec.md), *"Condução confiável do Processo vivo"* —,
com o objetivo de fechar as condicionantes `C1`, `C2`, `C4`, `C5` e `C6`. É a **B** na prática. A
proposta não diz se o adiamento desde 20/09 foi deliberado, e este registro não o afirma.

---

## DP-05 — Cadastro de reserva está no alvo do piloto, e o que "limitado em N" significa?

*Decide o RC-58: a lacuna A que mais se parece com o ACH-47 de 16/09 — "aceita, publica e não executa".*

### O problema

Duas perguntas, e a primeira condiciona a segunda.

**Um Edital só de cadastro de reserva é publicável e não convoca ninguém.** O produto aceita
`immediateVacancies = 0` com reserva, e a `040` o trata como "zero legítimo". Mas convocar exige vaga
faltante apurada: `convocacao/application/convocar.py:100-152` recusa sem apuração, e com zero vagas
publicadas o déficit é zero (`DEFICIT_ZERO`). Nem `reserveType` nem `reserveLimit` têm consumidor em
`ocupacao/`, `convocacao/` ou `classificacao/`. O único contorno é retificar as vagas imediatas a cada
chamada, o que usa um ato normativo para registrar um fato operacional.

**O limite publicado não tem efeito.** O #159 (25/09) tornou "Cadastro Reserva limitado" alcançável pela
tela, e o documento imprime *"limitado em 30"* (`publicacoes/infrastructure/pdf.py:1683-1685`). Quem
governa quantos suplentes existem é o `cutRule`: alvo `FIXED`, *"30 suplentes não saem de vaga
nenhuma"* (`classificacao/domain/faixa.py:18-21`). São duas declarações da mesma norma, e nada as
confronta.

### O que já está fixado

- **Única fonte autoritativa** (Constituição, Princípio II): a mesma informação não deve ter duas
  fontes.
- **Nada se exclui** e **a publicação é imutável**. O que já foi publicado com "limitado em N" continua
  dizendo isso.
- **Cadastro de reserva é o caso normal em parte da amostra** (140/2025, 173/2025; P-2 de
  `achados-editais-externos.md`: *"Ocupar sem quantidade é caso normal, não borda"*).

### As opções

**Primeira pergunta, o alvo:**
- **A.** A família entra no alvo do piloto: tutoria da UAB e outros Editais só de reserva.
- **B.** Não entra agora. A publicação de "0 vagas + reserva" passa a **avisar** que a convocação dessa
  oferta acontece fora do sistema. É honesto, e barato.

**Segunda pergunta, se A — a semântica de `reserveLimit`:**

| | 1. O limite é o alvo do corte | 2. O limite é conferido contra o corte | 3. O limite é só texto normativo |
|---|---|---|---|
| **O que é** | `reserveLimit` passa a alimentar o alvo `FIXED` do corte, ou o corte o deriva. | Os dois continuam, e a publicação **avisa** quando divergem. | O limite é publicado e declaradamente não executado; o corte governa. |
| **Fontes** | uma | duas, conferidas | duas, uma sem efeito |
| **Custo** | médio, porque mexe no corte | pequeno | nenhum, mas deixa a dívida à vista |

### Recomendação

**Validar antes de decidir.** Publicar pela tela um Edital com 0 vagas imediatas e cadastro de reserva,
classificar e tentar convocar. Se a lacuna se confirmar:

- **A com 2**, se a família estiver no alvo. É o menor passo que torna o limite verdadeiro sem redesenhar
  o corte. A convocação da reserva é spec própria.
- **B**, se não estiver.

### O que foi decidido

Em 26/09/2026, o usuário escolheu **B para o piloto atual**, depois de a lacuna ser conferida no
código. A conferência mostrou que configurar, publicar, classificar, apurar e divulgar o resultado já
funcionam com 0 vagas imediatas e reserva, sem número fictício. O que falha é só a convocação: com zero
vagas publicadas, a apuração nunca tem déficit, e toda chamada é recusada com `sem_deficit`. Por isso
foi recusada a proposta de uma spec "cadastro de reserva executável", que especificaria o que já
funciona.

**Por que B, e não A.** Tirar a recusa do déficit não tornaria a família executável. Uma convocação
correta da reserva depende ainda de duas capacidades ausentes: a **validade** do Edital e a sua
prorrogação (P-3), e a **ordem de chamada entre modalidades** quando não há quadro quantitativo (P-1).
E os Editais de referência, o 140/2025 sobretudo, trazem heteroidentificação, barema e outras regras
que também estão fora do alvo.

**O que foi feito.** A publicação de Perfil com 0 vagas imediatas e reserva `LIMITED` ou `UNLIMITED`
avisa na Revisão que a classificação e o resultado correm no sistema e a convocação corre fora dele
(`reserve_only_convocation_external`, em `editais/domain/validation.py`). É advertência, e só no ato de
publicação.

**Quando A voltar.** A spec nasce quando houver um Edital de cadastro de reserva escolhido para
operação, e não antes. O nome dela é *"Convocar do cadastro de reserva, na ordem publicada e dentro da
validade"*, e não "publicar com zero vagas". O escopo mínimo:

- a necessidade superveniente de convocação como **fato operacional** auditável e append-only, e não
  como Retificação das vagas;
- o consumo dessa necessidade pela ocupação e pela convocação que já existem;
- a validade e a prorrogação do Edital (P-3);
- a ordem de chamada entre modalidades (P-1, P-2);
- o limite da reserva.

**Sobre o `reserveLimit`, a opção 2 foi recusada como solução definitiva.** Só avisar a divergência
deixa publicáveis duas normas contraditórias. Se o limite significa a quantidade máxima de suplentes, ele
e o corte têm uma fonte só: ou um deriva do outro, ou a divergência impede a publicação. A escolha
entre as duas é da spec que A abrir.

---

## DP-06 — O Cefor usa dupla leitura?

*Decide a forma da correção do RC-29.*

### O problema

O campo "Avaliações por inscrição" aceita qualquer valor maior ou igual a 1, sem aviso
(`editais/domain/validation.py:234`). O Edital publica. A distribuição atribui duas avaliações. E a
consolidação recusa a **Etapa inteira**: *"o Edital prevê N avaliações… e não declara como combiná-las"*
(`resultados/domain/regra.py:71-76`). Não existe campo para declarar a combinação. Os dois impedimentos
irmãos da mesma função — eliminatória pontuada sem nota mínima, e decisória não eliminatória — têm o mesmo
defeito de momento.

### O que já está fixado

- **A D-008 (03/09)** recusou *"proibir na elaboração o que o Edital poderia legitimamente publicar"*. Um
  **IMPEDE** na publicação vai contra ela; um **aviso** não vai.
- **A recusa da consolidação está certa** e não deve ser afrouxada: não inventar média por padrão.

### As opções

| | A. Aviso na Revisão, mais `como-preencher` | B. Retirar o campo da tela até existir regra | C. Spec de regra de combinação publicada |
|---|---|---|---|
| **Quando serve** | sempre | se o Cefor não usa dupla leitura | se o Cefor usa |
| **Custo** | pequeno | pequeno, mas apaga uma capacidade que a distribuição já tem | uma spec inteira |

### Recomendação: **A agora, para as três formas**

- **B**, se a resposta for "não usamos".
- **C** só com um Edital real de dupla leitura na mão.

### O que foi decidido

Em 26/09/2026, o usuário escolheu uma quarta forma, ao especificar a
[`046`](../specs/046-contrato-de-executabilidade/spec.md): **impeditivo na publicação quando o fluxo
publicado exige o Resultado da Etapa, e aviso quando não exige**. O Resultado é exigido quando a Etapa
é eliminatória ou é referenciada por marco — enumerada, governada por regra de corte, ou Etapa de
habilitação de sorteio. A recusa da `013` de 03/09 continua respeitada: nenhuma Etapa decisória precisa
ser eliminatória para publicar, desde que nada no fluxo dependa do Resultado dela. A `A` fica no
`como-preencher`; a `C` continua dependendo de Edital real de dupla leitura. Ver a `D-001` da `046`.

---

## DP-07 — A `D-G2` (três recusas em 403) continua valendo?

### O fato

A `D-G2` (19/09) decidiu que `criar_edital`, `reaproveitar` e `supervisao` passam de 404 para 403, porque
o objeto é visível e falta capacidade. As outras quatro recusas ficam em 404. Nada foi executado:
`interface/views.py:400-403`, `:1460-1461` e `:4020-4021` continuam com `raise Http404`.

**O que mudou depois.** O `4ec1cbb` e as guardas de oferta (`views.py:3973-3975`,
`processo_detalhe.html:14,72`) fizeram a interface **deixar de oferecer** os três caminhos a quem não pode.
Hoje, o 404 só aparece a quem digita a URL.

### As opções

- **A. Manter** e executar numa spec curta, que troque os três `raise` e atualize o inventário da `033` e
  as docstrings no mesmo commit.
- **B. Revogar**, registrando que o ganho de taxonomia não paga a spec.

### Recomendação: **A, com prioridade baixa**

A decisão foi tomada com critério, e o critério continua certo. O impacto é que caiu. Executar quando se
tocar nessas views, e não antes da Onda A.

---

## DP-08 — A `039` está encerrada? Para onde vão a `D-G5` e o alcance da Etapa?

### O fato

A branch local `claude/spec-039-alcance` tem dois commits só de spec, de 19 e 20/09 — nem plano, nem
tarefas, nem PR. A segunda redação propunha o **catálogo de Modalidades do Edital**, e absorvia a `D-G5`.
A primeira tinha o **alcance da Etapa**, que a segunda deixou como "a candidata seguinte". A decisão do
recorte documental de 25/09 declarou *"Mover a propriedade [da Modalidade] para o Edital está fora de
questão"*, e a `043` §2 e a `044` §3 repetem isso. **Não há registro explícito de que a `039` foi
encerrada.**

### O que está em jogo

- **A `D-G5` ficou órfã duas vezes**: decidida em 19/09, absorvida por uma spec que não entrou, e sem
  destino depois. Ela **não depende** do catálogo. Acrescentar Modalidade a um Perfil de Edital publicado
  é um `ADD` com a Modalidade continuando no Perfil.
- **O alcance da Etapa** — uma Etapa que vale só para alguns Perfis, ou para quem declarou uma Modalidade
  — é o que a heteroidentificação e o barema por curso precisam.
- **A natureza da decisão de 25/09.** Ela foi escolha de produto, ou leitura de "Cotas DEVEM ser definidas
  por Perfil"? A `039` lia o mesmo princípio de outro modo: o Perfil continua definindo a cota ao "aderir
  e repartir". A memória do projeto registra que a Constituição preserva **valor**, e não **campo**. Se foi
  leitura do texto, vale confirmar que ela é a leitura pretendida.

### Recomendação

1. **Registrar a `039` como encerrada**, com a razão (a decisão de 25/09). Preservar a branch, apagá-la ou
   convertê-la em tag é escolha do usuário.
2. **A `D-G5` vai para a B-4** — "a Retificação acrescenta o que o contrato já permite" —, junto da janela
   recursal, do corte, da reversão e do critério de desempate.
3. **O alcance da Etapa vai para a B-17**, com o barema e a heteroidentificação, e espera a DP-10.

### O que foi decidido

**Só o item 2**, em 26/09/2026, ao especificar a [`048`](../specs/048-retificacao-que-acrescenta/spec.md):
a `D-G5` foi para a B-4, e a `048` a executa junto da janela recursal, do corte, da reversão e do
critério de desempate. O usuário decidiu também que a Modalidade acrescentada pode ser **qualquer
uma, inclusive cota**, porque a auditoria define o problema como a ausência *"da ampla ou de uma
cota"*, e limitar à ampla deixaria parte do `RC-37` aberta.

**Executado:** a `048` foi mesclada pelo #197 (`0113b782`) em 26/09, e a auditoria registra o `RC-37`
como RESOLVIDO.

Os itens 1 (encerrar a `039`) e 3 (o alcance da Etapa) **continuam abertos**.

---

## DP-09 — A `D-011` (sem prova nova no recurso) continua?

### O fato

A `018` diz: *"Sem anexos na V1. Admitir prova nova em recurso é questão normativa que nenhum Edital lido
declarou, e abri-la pelo botão de anexar seria respondê-la por omissão."* (D-011; FR-007). A convergência
de 20/09 listou "Recurso sem prova — ABERTO" por causa disso. Mas a prova que o recurso costuma citar já é
documento da inscrição, e a `036` a leva ao julgador pelo ato de instrução.

### As opções

- **A. Manter.**
- **B. Revisitar**, com um Edital que declare a admissibilidade de prova nova. Aí ela chega "com o caso
  que a justifica", como a própria D-011 prevê.

### Recomendação: **A**

Não há Edital na amostra que peça o contrário. Registrar que o "ABERTO" da convergência sai da lista.

---

## DP-10 — Quais famílias de Edital entram no alvo?

### O fato

Quatro capacidades faltam, e **cada uma serve a uma família da amostra, e só a ela**:

| Família | Edital da amostra | Capacidade que falta | RC |
|---|---|---|---|
| Prova de títulos com barema | 14/2026, 173/2025, 140/2025 | barema como objeto; alcance da Etapa por Perfil ou curso | RC-64 |
| Cota racial com heteroidentificação | 28/2026, 57/2026 | Etapa aplicável só a quem declarou a Modalidade (L-2); comissão própria; recurso à CPVA | RC-65 |
| Cascata de grupos | 14/2026 | prioridade de chamada entre listas sem reserva (`callRules`) | RC-59 |
| Submodalidades de PPIQ | 140/2025 | submodalidade, reversão entre elas e ordem de convocação | RC-55 |

### O que já está fixado

- **Nada de estrutura antes da regra** (Constituição, §V).
- **A D-4 (04/09) adiou o barema**, e não o recusou. O custo dele está escrito: *"o sistema não demonstra
  que o total está certo"*.
- **A `044` excluiu a submodalidade** por decisão, e deixou três documentos do 140/2025 como facultativos.

### Recomendação

**Nenhuma agora.** Decidir **por família**, quando houver intenção de operá-la no sistema.

- **Heteroidentificação** é a que mais pesa, porque a verificação muda a lista de concorrência do
  candidato, que é dado deste sistema.
- **O alcance da Etapa vem antes** dela, e também serve ao barema por curso.
- Uma leitura estrita de `constitution.md:203-205` ("Perfis PODEM possuir Etapas distintas… critérios,
  pontuação e acumulação DEVEM existir no domínio") tornaria o barema e o alcance lacunas A. **Esta
  leitura também é do usuário.**

---

## DP-11 — A comissão local enxerga só o seu Perfil ou polo?

### O fato

A alocação é `Etapa × avaliador` (`comissoes/models.py:76-83`), e a distribuição não tem coluna nem filtro
de Perfil. `distribuicao.html` e `alocacoes.html` não têm uma ocorrência sequer de "Perfil". Num Edital de
7 polos, a comissão inteira alcança os sete. A convergência de 20/09 disse para não abstrair o polo antes
de ter o Edital real multipolo na mão. **Ele já existe**: o estudo de 21/09 cadastrou o 140/2025 e o
28/2026.

### As opções

| | A. Só leitura | B. Recorte opcional na alocação | C. Comissão por polo |
|---|---|---|---|
| **O que é** | Coluna e filtro de Perfil na distribuição e na alocação. | O membro pode ser alocado a uma Etapa **em um ou mais Perfis**; fora do recorte, nega por padrão. | Várias comissões por Processo, uma por polo. |
| **Autorização** | não muda | muda, com risco de vazamento horizontal a testar | muda muito |
| **Custo** | pequeno | médio | grande |

### Recomendação: **A agora**

A não depende de decisão nenhuma e resolve o que a presidência precisa ver. **B** só quando a instituição
operar comissões locais separadas, o que a equipe inicial de 2–3 pessoas torna improvável no piloto.

---

## DP-12 — O campo `Status` das specs é mantido ou abolido?

### O fato

Das 44 pastas de `specs/`, **41 declaram um estado que não corresponde ao código**. São 38 `Draft`,
inclusive a `040`–`043`, que estão implementadas, e três com outro rótulo. Só a `003` e a `004` estão
certas. O modelo cria o campo como `Draft` (`.specify/templates/spec-template.md:7`), e nada o lê nem o
confere. O custo é de leitura: esta auditoria, e antes dela o longitudinal, precisaram avisar os leitores
de que o campo mente.

### As opções

- **A. Manter** e atualizar no merge de cada feature. É mais um passo manual que já falhou 41 vezes.
- **B. Abolir** o campo nas specs e manter **um** índice — por exemplo, a tabela de incrementos do README
  — com um teste que o confira contra `specs/`.
- **C. Deixar como está**, e registrar no `CLAUDE.md` que o campo não indica nada.

### Recomendação: **B**

O estado real já é recuperável pelo git. Uma fonte só, conferida, é a regra que o projeto aplica a todo
o resto. O README, que também está atrasado (a tabela para na `025`), passa a ter quem o vigie.

---

## Depois da reavaliação de 27/09

*Origem: a [reavaliação pós-consolidação](reavaliacao-pos-consolidacao-2026-09-27.md) e a avaliação da
priorização dela, em 27/09. Os fatos foram conferidos contra a `main` em `8dd4f942`.*

### O que foi adotado

**O critério.** Sobe na fila o que reduz três coisas: as decisões que o operador toma, o que ele precisa
saber do modelo interno e as operações que ele repete para executar um Edital real. Uma lacuna que
responda "sim" a qualquer destas perguntas passa à frente de autenticação, de refinamento do sorteio e
de cobertura de caso específico:

1. O sistema poderia inferir isso, em vez de perguntar?
2. O Edital declara isso uma vez, e o sistema pede N vezes?
3. O operador está decidindo, ou só materializando o que o sistema já sabe?
4. Quando o Edital dobra, esse trabalho dobra?

O contrapeso é a `DP-17`: o que o sistema inferir, derivar ou materializar fica visível antes do ato
irreversível, com a origem e o alcance. Aqui um padrão errado não fica no rascunho; ele é publicado e só
sai por Retificação pública. E, antes de acrescentar capacidade, a pergunta é se há uma decisão, uma
tela, uma repetição ou um conceito a retirar.

**Duas consequências para as specs que vierem.**

- **Padrões não reduzem a validação.** A Retificação, a API e as exceções continuam produzindo qualquer
  configuração, e os validadores continuam necessários. O que diminui é o que o operador vê.
- **"Aplicar a todos" é materialização, não herança.** Um gesto grava N valores nos Perfis, e o conteúdo
  publicado continua por Perfil. Herdar no conteúdo publicado faria uma Retificação do padrão alterar N
  Perfis sem dizer, e mexeria na `024`, na `027` e na `048`. É outra mudança, e não está na fila.

**A ordem.**

| Passo | O quê | Forma | Depende de |
|---|---|---|---|
| 0 | Correções diretas (lista abaixo) | sem spec, contra requisito escrito | `DP-14`, só para a ampla |
| 0,5 | Teste operacional assistido, com o 28/2026 | fora do código | `DP-18` |
| 1 | Padrões e inferência, e "aplicar a todos" na composição e na Retificação | spec | `DP-13`, `DP-17` |
| 2 | Operar por marco: um gesto processa os N recortes, e o ato público continua por recorte | spec | — |
| 3 | Convocação como fluxo: convocar e comunicar num ato, e derivar o que é derivável | spec | `DP-16` |
| 4 | Documento público por marco | spec, só se o setor precisar | `DP-15` |
| 5 | Caminho de produção | spec e decisão institucional | vira P0 quando houver data de piloto |

**O passo 0, com o cuidado de cada item.**

- **A ampla na inscrição** (`inscricoes/application/rascunho.py:280`). A FR-039 da `009` já permite, e a
  `048` registra o defeito como achado A-1. É preciso revisitar o caso-limite da `048` que parte do
  comportamento de hoje: o rascunho com Modalidade assumida num Perfil que passa de uma para duas.
- **A porta da convocação**, a partir da ocupação e da página do Edital. Hoje só se chega pelo endereço.
- **O `?lista=` do `UX-004`**, para que o destino abra o recorte certo.
- **A consolidação como uma decisão humana**, quantos blocos técnicos o servidor precisar. A `013` não
  exige página, mas o ato trava as N inscrições numa transação só: medir com ~600 antes, ou processar em
  blocos sob uma confirmação.
- **A ordem e a ajuda do duplicar.** Os marcos só vêm se a origem já os tiver gravados, e a ajuda promete
  o contrário.
- **`wsgi` e `asgi` caindo na produção**, que recusa subir mal configurada (RC-124).
- ~~**Os campos definitivos visíveis na composição**, como selo de estado~~ — **saiu do passo 0 em
  27/09**: não há requisito escrito a restaurar. Ver a `DP-19`.
- **O dicionário do "O que mudou" completo**, com um guardião contra o contrato de mutabilidade
  (RC-111). Feito em 27/09; ver o [achado](achado-o-que-mudou-cala-campos-retificaveis.md).

*Desfecho (27/09): o passo 0 foi feito no mesmo dia. A ampla, pelo #202; a porta da convocação pela
página do Edital, o `?lista=` do `UX-004`, a ajuda do duplicar e `wsgi`/`asgi`, pelo #204; a
consolidação, pelo #203; o "O que mudou", pelo #201; e as sobras, pelo #205. A ordem das etapas do
duplicar não mudou, e a porta pela ocupação saiu, barrada pela `UX-034` da `016`
([achado](achado-porta-da-convocacao-pela-ocupacao.md); RC-137 da auditoria). O registro por unidade
está na [auditoria de consolidação](auditoria-de-consolidacao-2026-09-26.md), no fim da §1.*

**Os campos sem consumidor não são passo próprio.** `calculation`, `rounding`, `distribution` e
`callRules` da regra normativa, e o `reserveLimit` do Perfil, se decidem na spec que os consumiria: o
`reserveLimit` com a `DP-05`; os três primeiros com o quadro de vagas sugerido pelo percentual, no passo 1;
o `callRules` com a convocação, no passo 3. O que ficar sem consumidor deixa de ser pedido na composição,
e não é apagado do esquema: os Editais publicados guardam o valor.

**O sorteio.** Não se redesenha a semente. Se o setor adotar nos próximos Editais a semente que o
sistema prevê, a divergência com os Editais atuais deixa de ser problema de software, e essa adoção é
decisão do setor. O que entra no passo 1 é a configuração: o instante tirado do Evento do Cronograma, a
prosa gerada da regra escolhida e a pergunta de empate que não ocorre retirada.

---

## DP-13 — "Aplicar a todos": o que acontece com o que o Perfil de destino já declarava?

*Decide antes da spec do passo 1. É a pergunta que a [`043`](../specs/043-duplicar-perfil/spec.md)
deixou aberta (TF-1 e D-005).*

### O problema

Propagar um valor para Perfis que já existem esbarra no que eles já declaram. A resposta muda o valor da
operação: é na manutenção e na Retificação que ela mais rende, e é ali que o destino quase sempre já tem
valor.

### As opções

- **A. Sobrescrever sempre.**
- **B. Acrescentar sempre.** Numa coleção, pode duplicar sentido: dois critérios equivalentes, duas
  Modalidades para a mesma cota.
- **C. Recusar quando o destino já tem valor.** Tira da operação justamente o caso da Retificação.
- **D. Declarar o efeito por tipo de estrutura**, com prévia dos Perfis afetados antes da confirmação.

### Recomendação: **D**

Para valor único (marco, forma de convocação, janela recursal), substituir o correspondente, com a
prévia. Para coleção (Modalidades, critérios de desempate), decidir sobre os objetos concretos da spec, e
não como princípio abstrato. Na Retificação, "acrescentar a ampla a 16 Perfis num gesto" encosta na
FR-802 da `048`, que veda mecanismo novo de acréscimo: precisa de decisão declarada na spec.

### A análise por estrutura

*Pedida pelo usuário em 27/09, para a decisão ser tomada antes da spec do passo 1. Conferida contra a
`main` em `f6efe0dd`. É análise, e nada aqui foi decidido. Os ganhos são estimativas pelos custos
unitários do [anexo A da reavaliação](reavaliacao-pos-consolidacao-2026-09-27/anexo-A-composicao.md), e
não medições: quem os calibra é o teste operacional da `DP-18`.*

**Três fatos do código mudam a pergunta.**

1. **A identidade entre Perfis não é a mesma em toda estrutura.** A Modalidade e o fato têm código único
   no Perfil (`uq_modalidade_perfil_code`, `uq_fato_perfil_code`, em `editais/models/perfis.py`), e o
   código da Modalidade já é identidade do Edital desde a `044`. O marco também tem código único no
   Perfil (`uq_marco_perfil_code`), mas esse código é **derivado do Perfil** (FR-420 da `030`, D-004 da
   `043`): o marco do LP01 chama-se `LP01`, o do LP02, `LP02`. E o marco não tem campo de posição. Com um
   marco por Perfil, o correspondente é "o marco do Perfil"; com dois, não há correspondente. O critério
   de desempate se identifica pela `ordem`, única no marco (`uq_criterio_marco_ordem`), e a ordem é a
   norma. **Isso corrige a recomendação acima num ponto**: o marco não é valor único. É coleção por
   Perfil, e só os campos dele são valores únicos.
2. **O maior ganho não tem conflito nenhum.** No fluxo linear do assistente, os Perfis chegam à
   Classificação sem marco (anexo A, §5.2). Materializar o marco onde não há marco rende ~370 das ~400
   interações do 140/2025, e ali o destino não declara nada. A pergunta desta DP pesa na correção e na
   Retificação. O marco aplicado aos Perfis sem marco também torna indiferente a ordem de compor e
   duplicar, que o passo 0 só pôde explicar na ajuda.
3. **A duplicação remapeia por identidade, e "aplicar a todos" teria de remapear por código.**
   `duplicar_perfil` (`editais/domain/duplicacao.py`) mapeia as identidades da origem para identidades
   novas. Propagar para um Perfil que já existe exige achar, no destino, o fato e a Modalidade **de mesmo
   código**. Nos Perfis nascidos por duplicação os códigos coincidem. Nos compostos do zero podem não
   coincidir, e a correspondência falha. Ela precisa falhar alto, como a FR-641 da `043` já exige para
   referência sem contraparte.

**Dois textos escritos que a spec precisa enfrentar, e não um.**

- **A FR-802 da `048`**: *"A feature MUST NOT criar mecanismo de acréscimo além dos dois que existem"*.
  A letra vincula a `048`, e o que ela protege é o domínio: nenhuma espécie nova de Alteração e nenhum
  acréscimo genérico. Na Retificação, o gesto de aplicar a todos produz N Alterações dos dois caminhos que
  já existem, o nascimento de objeto e o acréscimo de item a coleção, e só sobre as duas coleções que a
  `048` nomeou, a Modalidade e o critério. Tudo sai num ato só, com a mesma versão, o mesmo documento e o
  mesmo histórico (FR-795), conferido no mesmo resumo *antes → depois* (FR-800) e contra o contrato de
  mutabilidade como fonte única (FR-803). Nessa leitura, o gesto é de interface e não esbarra na
  FR-802, e a spec do passo 1 o declara. Se o usuário ler a FR-802 como vedando também o gesto, a
  Retificação sai da primeira spec, e com ela os ~160 e os ~110 do 140/2025 da tabela abaixo.
- **A FR-421 da `030`**: *"Valor padrão e valor derivado NÃO DEVEM ser aplicados a conteúdo já
  declarado de Edital existente, inclusive durante Retificação"*. Aplicar a todos substitui conteúdo já
  declarado. A leitura possível é que o valor aplicado não é padrão nem derivado, porque quem aplica o
  declara, com o alcance à vista. Mas o passo 1 traz os padrões na mesma spec, e a fronteira precisa
  ficar escrita: **o padrão só preenche o vazio; aplicar a todos substitui, e só por gesto com
  prévia.** Código e denominação do marco nunca são substituídos. O código é estrutural, e a
  denominação, onde o destino já a tem, foi declarada ou derivada para ele.

**A tabela.** "Destino" é o Perfil (ou o marco dele) que recebe o valor. "Fora do alcance" quer dizer
que a prévia nomeia o destino e o motivo, e o gesto não o toca. Nunca é exclusão silenciosa.

| Estrutura | Forma | O que o destino pode ter · como se identifica | Efeito proposto | Risco das alternativas | Onde vale · contrato | Ganho estimado: 28/2026 · 140/2025 |
|---|---|---|---|---|---|---|
| **Marco, como objeto** | coleção por Perfil (quase sempre um) | nenhum marco (o fluxo linear), um ou vários · é "o marco do Perfil"; o código difere entre Perfis e não há posição | **acrescentar onde falta**, com código e denominação derivados do destino e os critérios remapeados pelo código do fato; destino com marco fica **fora do alcance**, e se corrige pelas linhas abaixo | substituir o marco inteiro apaga marco divergente e troca as Etapas medidas, que são o que o marco é · acrescentar onde já há marco dá dois marcos finais no Perfil, e duplica sentido · recusar onde há marco perde só o que as linhas de campo cobrem | só composição: marco novo não nasce por Retificação (inventário da `048`), e `stages` não se retifica | ~63 → ~12 · **~400 → ~30**; se o marco leva o corte, somem os dois IMPEDE por Perfil, o da `032` e o da `046`. No multicampi de 66, ~1.650 → ~30 |
| **Campos do marco**: forma da ordem, Etapas que entram, combinação, arredondamento | valor único por marco | valor declarado, igual ou diferente · o marco como acima; Perfil com dois marcos fica fora | **substituir**, com *antes → depois* por destino; destino igual não gera alteração | recusar quando há valor tira toda a correção, porque sempre há · substituir apaga divergência deliberada: a prévia a mostra, e o gesto deixa excluir o destino | ambas. Na Retificação, `stages` é não retificável e sai; nos demais, a ordem emitida de cada marco alcançado fica obsoleta e recomputável, N de uma vez, e a prévia as conta | pequeno isolado, 1–2 por marco: ~7 → ~4 · ~16 → ~4. O ganho está na linha anterior |
| **Janela recursal** | valor único por marco: três campos, e o objeto pode faltar | janela declarada ou ausente | **substituir** onde há; **nascer** onde falta | recusar onde há perde a correção do prazo · substituir encurta, em N marcos, o prazo de ato já divulgado (A-3 da `048`, multiplicado) | ambas. Na Retificação, nasce só concedendo (D-003 da `048`): *"não admite"* sobre marco sem janela fica fora. A prévia aponta os marcos com ato já divulgado | composição: dentro da primeira linha. Retificação: ~14 → ~4 · ~32 → ~4 |
| **Regra de corte** | valor único por marco: seis campos, e o objeto pode faltar (ausente é IMPEDE desde a `046`) | regra declarada ou ausente | **substituir** onde há; **nascer** onde falta. A quantidade fixa (alvo `FIXED`) **não** se propaga por padrão | a quantidade fixa depende das vagas do Perfil: propagá-la iguala Perfis que diferem de propósito · recusar onde há perde a correção | ambas. Na Retificação, espécie do alvo, Etapa governada e continuação não se trocam onde a regra existe, e só nascem. O nascimento leva a guarda da D-002 da `048`: marco com Resultado na Etapa governada fica fora, e a guarda corre de novo na publicação (FR-789) | composição: dentro da primeira linha. Nascimento por Retificação: ~42 → ~9 · ~96 → ~9 |
| **Critérios de desempate** | coleção ordenada por marco, em que a ordem é a norma | nenhum critério, a mesma lista ou outra · o item, pela `ordem`; o equivalente entre Perfis, por tipo + Etapa (do Edital) ou tipo + código do fato (do Perfil) | **substituir a lista inteira**, como unidade: é o que o Edital declara (*"o desempate se dará da seguinte forma: a), b), c)"*, 6.3.2 do 140/2025). Lista idêntica não gera alteração. Fato sem correspondente de mesmo código deixa o Perfil fora | acrescentar põe "mais idoso" duas vezes, ou um critério fora da ordem · substituir item a item por posição casa critérios diferentes que estão na mesma ordem · recusar onde há critério perde a G-001 da `043` e a Retificação | ambas. Na Retificação, tipo, parâmetro e ausência não se retificam no lugar: substituir é remover e acrescentar, e os dois caminhos existem desde a `048` (FR-792). A ordem emitida fica obsoleta em cada marco (FR-794). Fato novo não nasce por Retificação | 0: o 28/2026 sorteia, sem critério · composição: 240 das ~400 da primeira linha; correção depois de duplicado, ~80 → ~8; Retificação que troca um critério nos 16, **~110 → ~10** |
| **Forma de convocação** | valor único por Perfil, de lista fechada; vazio é "não declarou" | vazio, a mesma forma ou a outra | **substituir** | recusar onde há valor perde a Retificação · substituir iguala Perfis que convocam de jeitos diferentes; nenhum dos dois Editais faz isso (28/2026 por e-mail, 10.3; 140/2025 por publicação, 10.6) | ambas; retificável | marginal. Composição: 0, porque a cópia a leva. Retificação: 7 → ~4 · 16 → ~4 |
| **Reversão** | valor único por Perfil, que só existe com Modalidade e quadro | vazio ou uma das duas espécies | **substituir**; **nascer** onde falta; destino sem quadro fica fora, como a validação já recusa | as da forma de convocação · a apuração não fica obsoleta quando a reversão muda (A-2 da `048`), agora em N Perfis de uma vez | ambas; nasce pela FR-791 | marginal, como a linha anterior |
| **Modalidade**, com a regra normativa e a declaração da ampla | coleção por Perfil | sem o código, com o código, ou com Modalidade equivalente sob outro código ("PcD" e "DEF") · pelo **código**. A equivalência sob outro código o sistema não reconhece sem casar nome, o que a R-006 da `025` recusa | **uma Modalidade por vez, e não o conjunto**: acrescentar onde o código falta; substituir os campos onde existe (denominação, descrição, fundamento, versão, percentual), nunca o código; nunca remover. A declaração da ampla aponta a Modalidade do destino de mesmo código. A linha da cota no quadro não se propaga, porque a quantidade é do Perfil | sincronizar o conjunto remove a cota que o destino não tem de propósito, ou a que só ele tem · acrescentar sempre duplica a cota que o destino declarou sob outro código: a prévia mostra, por destino, as Modalidades que ele já tem · recusar onde o código existe perde a correção (G-001 da `043`) | ambas. Na Retificação, acrescentar é a FR-777 da `048` N vezes: é o caso da FR-802. A regra normativa não nasce em Modalidade já publicada (D-001 da `048`), e o destino com o código e sem regra fica fora. O recorte novo nasce sem ordem (FR-781). O documento da Modalidade nova continua na Retificação seguinte | composição: 0 no fluxo com duplicar; Modalidade esquecida na origem, ~40 → ~10 · ~100 → ~10, mais uma quantidade de quadro por Perfil se for cota. Retificação: ver abaixo |
| **Documentos Exigidos** | entidade do Edital, com recorte | nada: o documento não pertence ao Perfil | **nenhum gesto novo.** O "aplicar a todos" do documento já existe, e é o recorte: *"Todos os Perfis"* e o código da Modalidade (`044`) | materializar por Perfil desfaria o 112 → 7 da `044` e voltaria às cópias que precisam ser mantidas iguais (anexo A, §5.1). O que sobra, documento para um subconjunto de Perfis (o item f do 140/2025, *"de acordo com a função pleiteada"*), é pergunta de recorte | nenhum; e documento novo não nasce por Retificação (inventário da `048`) | 0 · 0 sobre o que já existe |

**A Retificação da Modalidade mudou de valor com a `DP-14`.** O caso-tipo da reavaliação, "acrescentar a
ampla a 16 Perfis", custava ~160 interações. Desde a correção da `DP-14`, o Perfil com vaga imediata na
linha geral já oferece a ampla sem Modalidade declarada, e esse caso deixou de precisar de Retificação.
No 28/2026 (40 vagas, 28 na linha geral), o ganho da ampla é ~0. Continua valendo onde não há vaga
imediata, que é o cadastro reserva: no 140/2025, se a ampla tivesse sido esquecida, seria **~160 → ~13**.
A cota esquecida continua valendo nos dois: ~70 → ~20 · ~160 → ~13, mais as quantidades do quadro onde
houver vaga. Renomear a denominação ligada a documento transversal, hoje N edições obrigatórias
(FR-706 da `044`), cai para uma.

**Fora da tabela, de propósito.**

- **O quadro de vagas.** A quantidade é do Perfil, e a divergência é a regra. O caminho do passo 1 é o
  quadro sugerido pelo percentual, que é outra frente.
- **O método próprio do sorteio no marco.** Ele existe para divergir. O comum já é O(1), e propagar uma
  divergência para todos é sinal de que o comum está errado, e é ele que se corrige.
- **Os textos do Perfil** (denominação, atribuições, requisitos, carga horária, remuneração). São valores
  únicos, e substituir seria trivial. Mas é onde a divergência deliberada é regra: o 140/2025 tem 4
  blocos de requisito para 16 Perfis. Na Retificação, cairia de 16 para ~4 edições por campo.
- **Os fatos declarados.** Entram como dependência do critério, pelo código. Fazer o fato nascer é a
  "língua do Edital" do passo 1 (*"maior idade" cria o fato*), e não este gesto.

### Recomendação por estrutura

- **Marco:** materializar só onde falta. O destino que já tem marco fica fora do alcance, e se corrige
  pelos campos.
- **Campos do marco, janela e corte:** substituir, e fazer nascer onde falta. A Retificação obedece às
  exclusões do contrato e às guardas da `048`. A quantidade fixa do corte não vai por padrão.
- **Critérios de desempate:** substituir a lista inteira. O fato é achado pelo código, e o Perfil sem ele
  fica fora do alcance.
- **Forma de convocação e reversão:** substituir. O ganho é marginal. Entram se o teto da spec
  permitir, e são as primeiras a sair.
- **Modalidade:** uma por vez, pelo código: acrescentar ou substituir campos, nunca remover e nunca
  sincronizar o conjunto.
- **Documentos:** nenhum gesto. O recorte da `044` já é o "aplicar a todos" deles.

**Em todas:** materialização, não herança. Cada destino recebe o seu valor, e nada guarda vínculo com a
origem (D-005 e D-006 da `043`). Nenhuma divergência vence em silêncio, que é a pergunta que a D-005 da
`043` deixou: a prévia mostra cada uma, e quem aplica exclui o destino que diverge de propósito. O
alcance padrão é "todos os demais", e não é o único.

### O que entraria na primeira spec

1. **O marco, com os critérios, para os Perfis sem marco**, na composição. É o ganho grande, e não tem
   conflito.
2. **A lista de critérios de desempate**, na composição e na Retificação.
3. **A Modalidade pelo código**, com a declaração da ampla, na composição e na Retificação.
4. **A janela recursal e a regra de corte**, inclusive o nascimento, na composição e na Retificação.
5. **A prévia do alcance, comum a todas (`DP-17`).** Por destino, um de quatro efeitos: *nasce*,
   *substitui* (*antes → depois*), *sem mudança* ou *fora do alcance*, com o motivo. Na Retificação,
   ela mostra também as consequências: as ordens que ficam obsoletas, os recortes que nascem sem ordem e
   os marcos com ato já divulgado cuja janela muda. Na Retificação ela é a conferência que já existe
   (FR-800), agrupada, e não uma prévia em PDF (item 7 da avaliação da `048`).
6. **As duas declarações escritas**: a leitura da FR-802 da `048` e a fronteira com a FR-421 da `030`.
7. **A exclusão de destino no próprio gesto.**

Os campos restantes do marco, a forma de convocação e a reversão entram se couberem. São baratos
depois da prévia, e rendem pouco.

**Fica fora:** documentos; quadro de vagas; método próprio do sorteio; textos do Perfil; substituir
marco inteiro; remover Modalidade ou sincronizar o conjunto; fazer o fato nascer, que vai com a "língua
do Edital".

**O que a spec herda, registrado e não decidido aqui.**

- **Onde a materialização acontece na composição.** Na tela, como o duplicar (D-001 da `043`), mantém
  um só caminho de gravação, mas o rascunho local não recupera marcos (G-006 da `043`). No servidor,
  cria um segundo caminho para o rascunho. É pergunta de plano, e pesa mais aqui do que pesou no
  duplicar, porque a etapa Classificação grava por substituição (`replace_draft`), com os marcos de
  todos os Perfis num formulário só.
- **A A-2 e a A-3 da `048` passam a ser multiplicadas por N** num gesto. Não mudam de natureza, só de
  escala.
- **O "O que mudou" público ganha N linhas iguais** por gesto na Retificação. Não é defeito: cada
  Alteração continua registrada, que é o que a reavaliação pediu. Mas é ruído para quem lê o portal.

### O que foi decidido

Em 27/09/2026, o usuário aprovou a **D**, na forma de **uma regra única**, e autorizou o gesto também na
Retificação. A análise acima fica como estava. Ela passa a ser o inventário que justifica a regra, e
não uma lista de políticas.

**A regra.**

> Nos destinos selecionados, "aplicar a todos" substitui integralmente a declaração correspondente, na
> fronteira que a spec define para cada unidade. Se ela não existir e puder nascer, cria uma cópia
> independente. Fica fora do alcance o destino sem correspondência inequívoca, ou em que o contrato
> não permite criar nem substituir a unidade inteira. O marco inteiro não é unidade substituível: ele
> só é criado onde falta. Antes da confirmação, a prévia mostra cada criação, substituição, ausência de
> mudança ou exclusão, com o motivo.

**As exceções são três, e só três:**

1. não há correspondente seguro;
2. o contrato não permite criar ou substituir;
3. a ação opera sobre um item, e não sobre a coleção inteira. Aplicar a cota PcD não apaga a cota
   racial que só aquele Perfil declara.

**O que a regra fixa, além do texto.**

- **O marco.** Com um marco no Perfil, a correspondência é segura, e a janela, o corte, os critérios e
  os campos do marco se aplicam a ele. O que fica de fora é **o marco inteiro**, que não se substitui:
  substituí-lo trocaria as Etapas medidas e campos que não se retificam. Com dois ou mais marcos no
  Perfil, falta correspondência, e tudo o que mora neles fica fora do alcance.
- **A atomicidade na Retificação.** A substituição é campo a campo, e nunca pela troca do objeto inteiro,
  que é a porta registrada como A-6 da `048`. Se qualquer diferença alcançar campo não retificável, o
  destino **inteiro** fica fora do alcance, sem aplicação parcial.
- **A quantidade fixa do corte vai junto.** É a consequência da regra única, e **substitui** o que a
  tabela acima propunha (não propagar por padrão). A compensação é a prévia: quando o corte tiver
  quantidade fixa, a prévia DEVE destacar em separado a quantidade anterior e a aplicada em cada Perfil,
  e o destino pode ser excluído antes da confirmação. Não há exceção escondida para preservar o
  desenho anterior. Quem aplica escolhe a regra completa e vê a consequência.
- **Estrutura nova** parte da mesma hipótese, mas só entra no alcance quando a spec declarar a unidade
  dela e o contrato autorizar. É o negar por padrão, e o contrato continua sendo a fonte única
  (FR-803 da `048`).
- **O ganho em simplicidade tem limite.** A regra normativa e os testes comuns ficam menores. Os casos por
  estrutura continuam necessários para provar as fronteiras e as exceções.

**O que a próxima spec declara por escrito.**

- **A leitura da FR-802 da `048`.** Ela impede criar espécie nova e genérica de alteração. Não impede uma
  interface em lote que produza várias alterações já admitidas, cada uma validada pelo contrato e
  registrada no mesmo ato.
- **A fronteira com a FR-421 da `030`.** O padrão só preenche o vazio. "Aplicar a todos" substitui, e só
  por gesto com prévia.
- **A fronteira de cada unidade.** Três casos já estão abertos:
  - a Modalidade não leva a linha dela no quadro, porque a quantidade é do Perfil;
  - fica por decidir se a declaração de "esta é a ampla" vai junto, porque ela é valor do Perfil, e
    aplicá-la pode desmarcar outra Modalidade do destino;
  - a Modalidade equivalente sob outro código ("PcD" e "DEF") não cai em nenhuma exceção, e só a
    prévia a protege, mostrando as Modalidades que cada destino já tem.

**A primeira spec** é a da lista acima, [*O que entraria na primeira spec*](#o-que-entraria-na-primeira-spec),
com o gesto valendo na composição e na Retificação. O que a spec herda continua registrado, e não
decidido.

---

## DP-14 — Quando a inscrição oferece a ampla concorrência?

*Decide antes da correção da ampla, no passo 0.*

### O problema

A tela sugere não declarar a ampla (*"Nenhuma — a ampla concorrência é só a linha geral do quadro"*,
`interface/templates/interface/_perfil.html:195`), e a inscrição só oferece as Modalidades declaradas
(`inscricoes/application/rascunho.py:280`). Com uma cota, todo inscrito vira cotista; com duas ou mais,
quem não é cotista não tem o que escolher. A inscrição congela a Modalidade no envio, e não há desfazer.

É o **RC-128** da auditoria, que a `048` registrou como A-1 e que recomenda agir na composição, impedindo
ou advertindo mais forte — a opção B abaixo. O RC-128 cobre só o Perfil de uma cota; esta decisão cobre
também o de duas ou mais.

### O que já está fixado

- **FR-039 da `009`:** a ausência de reserva PODE ser apresentada como ampla concorrência sem entidade
  gravada; havendo Modalidade equivalente declarada, ela DEVE ser usada.
- **O recorte nulo já é a ampla** na divulgação e no sorteio (`divulgacao/models.py:50`).

### As opções

- **A. Oferecer a ampla sempre que o Perfil tiver linha geral com vagas**, como recorte nulo. Se houver
  Modalidade de ampla declarada, usar essa.
- **B. Impedir a publicação** de Perfil com cota e sem ampla declarada, dizendo a consequência na
  inscrição.
- **C. Manter e só avisar**, como hoje.

### Recomendação: **A**

É o que a FR-039 já prevê, e não pede nada a quem compõe. O Perfil sem linha geral com vagas, com tudo em
cota, continua sem ampla. As inscrições já enviadas não mudam.

### O que foi decidido

Em 27/09/2026, o usuário escolheu a **A**, como passo 0 da ordem adotada na mesma data. A inscrição
oferece a ampla concorrência como recorte nulo sempre que o Perfil tiver vaga imediata na linha geral do
quadro e não declarar Modalidade de ampla; declarando uma, é ela que se usa (FR-039, 2ª frase). O Perfil
sem vaga na linha geral continua sem ampla.

**Três pontas pediram decisão na correção**, e foram decididas na mesma data:

1. **A ampla vem marcada.** No Perfil que a oferece ao lado de cotas, o rascunho nasce na ampla, e o
   cotista troca pela cota. O nulo é a ausência de reserva, que a FR-039 manda apresentar como ampla; exigir
   escolha explícita pediria uma coluna nova, porque no banco "não escolheu" e "escolheu a ampla" são o
   mesmo nulo. No Perfil que **declara** a ampla, a escolha continua obrigatória, como antes.
2. **"Com vagas" é vaga imediata.** O Perfil só de cadastro reserva, com a linha geral em zero, uma cota e
   nenhuma ampla declarada, continua assumindo a cota. É a letra desta decisão, e o caso fica registrado
   como achado abaixo; a família já tem a convocação fora do sistema pela `DP-05`.
3. **Os rascunhos abertos com a cota assumida ficam como estão.** Não há como distinguir a cota assumida da
   escolhida, e não há produção. A cota gravada continua sendo a escolha, e a tela passa a oferecer a
   ampla ao lado. É a regra que a `048` já fixou para o caso-limite: *"a pessoa pode trocá-la pela ampla, e
   nada a troca por ela"*.

**O que foi feito.** `oferece_a_ampla_sem_modalidade` decide a oferta, e `modalidade_assumida` e
`_modalidade_escolhida` passam a consultá-la (`inscricoes/application/rascunho.py`). A mesma regra
responde à tela, à gravação, ao envio e ao POST forjado. A tela do candidato põe *"Ampla concorrência"* à
frente das cotas, e a revisão, o comprovante e a página pública da seleção passam a nomeá-la. Os
requisitos restaurados são os da `009`: FR-038, FR-039, FR-040, o cenário 2 da US4 (*"escolho concorrer
sem reserva"*), SC-005 e SC-006. Classificação, sorteio, corte e ocupação não mudaram, porque já liam o
recorte nulo como a ampla: as fixtures deles já montavam inscrições nulas em Perfil com cota, gravadas
direto no banco, e por isso nunca passaram pela porta que as recusava.

**O caso-limite da `048`** (*"Rascunho de inscrição aberto"*) continua valendo onde a assunção é
legítima, o Perfil com tudo em cota, e o teste dele passou a montar esse Perfil. Com vaga na linha geral,
nada é assumido, e o caso não se forma.

**O texto de `_perfil.html` não muda.** *"Nenhuma — a ampla concorrência é só a linha geral do quadro"*
era a promessa que a inscrição não cumpria, e agora cumpre.

**Achados, fora do escopo.** Registro, não escopo.

- **A-14.1 · A tela de Modalidade única trava quem já enviou o documento da cota.** *(RC-131 da auditoria.)* Sem campo de
  Modalidade na tela, a view calcula o descarte contra `None` (`portal/views.py`, em `inscricao`, na
  chamada a `descartes_por_mudanca_de_modalidade`), e *"Revisar inscrição"* abre *"Mudar de modalidade
  descarta documentos"*. Confirmar leva a `discard_not_confirmed`, porque `gravar_dados` assume a
  Modalidade única e não vê descarte algum. Reproduzido em 27/09. Vem de antes desta correção, e depois
  dela só alcança o Perfil com tudo em cota.
  **Corrigido em 27/09, nas sobras do passo 0:** `descartes_por_mudanca_de_modalidade` compara com a
  Modalidade que `gravar_dados` vai gravar (`_modalidade_escolhida`), e não com o vazio do formulário.
  Restaura a FR-031 e a FR-041 da `009`.
- **A-14.2 · A advertência da FR-325 soa para a forma agora correta.** *(RC-132 da auditoria.)* `general_competition_modality_undeclared`
  (`editais/domain/validation.py`, `_ampla_por_declarar`) avisa todo Perfil que declara Modalidade sem
  apontar a ampla, e manda declarar *"qual delas é a da ampla concorrência"*. Para o Perfil que só declara
  cotas, que é o caso que esta decisão resolve, não há qual apontar.
  **Examinado em 27/09 e mantido como registro, por decisão do usuário.** A correção esbarra no texto da
  FR-325 da `027`: *"Perfil que declara Modalidade e não declara qual delas é a da ampla concorrência
  MUST produzir advertência própria"*. O Perfil só de cotas cumpre essa condição ao pé da letra, e o
  sistema não o distingue do caso-armadilha que a advertência existe para pegar — a Modalidade chamada
  "Ampla concorrência" sem ser apontada, o A11 do `quickstart` da `027` — sem casar nome, o que a
  `R-006` da `025` recusa. Calar a advertência ali pede revisar a FR-325, o que é spec; reescrever só a
  mensagem a deixaria soando, como pendência na Revisão e na confirmação (FR-327, FR-328), para a forma
  correta.
- **A-14.3 · A gestão não nomeia nem conta a ampla sem Modalidade.** *(RC-133 da auditoria.)* A lista e o detalhe das inscrições
  (`inscricoes/application/consulta.py`, `_nome_no_conteudo`) e a Mesa (`avaliacoes/application/mesa.py`)
  mostram a Modalidade em branco; a contagem por Modalidade descarta o nulo, e o filtro não o alcança
  (`_contagens`, `_filtrar`). A FR-067 e a FR-068 da `009` pedem a Modalidade. Já valia para o Perfil sem
  Modalidade, e passa a ser o caso comum.
  **Corrigido em 27/09, nas sobras do passo 0:** `nome_da_modalidade` (`inscricoes/application/rascunho.py`)
  é a regra, e a lista, o detalhe e a Mesa passaram a lê-la. O nulo tem nome, e entra na contagem e no
  filtro, **onde ele é a ampla** (`o_nulo_e_a_ampla`): no Perfil sem Modalidade nenhuma, que é o caso
  anterior à DP-14, e no que oferece a ampla sem Modalidade ao lado das cotas. Onde é escolha por
  fazer — ampla declarada ao lado de cota, ou duas cotas sem vaga na linha geral —, continua sem nome.
  O filtro leva o Perfil junto (`ampla:<Perfil>`), porque o nulo existe em todo Perfil, e confere a
  mesma regra que gera a opção: o endereço forjado para onde o nulo não é a ampla não filtra. O portal
  mantém o que é dele: no Perfil sem Modalidade, a revisão continua sem a linha, porque nada foi
  perguntado (FR-038). Restaura a FR-067 e a FR-068 da `009`.
- **A-14.4 · A Modalidade única que nasce por Retificação é atribuída em silêncio no envio.** *(RC-134 da auditoria.)* Se uma
  Retificação zera a linha geral, ou dá a primeira Modalidade a um Perfil sem vaga na linha geral, o
  rascunho no nulo é recusado até o reconhecimento; depois dele, o envio grava a Modalidade única que
  `_modalidade_escolhida` devolve (`inscricoes/application/submissao.py`, eixo 5), com os documentos
  conferidos contra a inscrição sem ela. Vem de antes, pela `048`, e esta correção o estreita.
- **A-14.5 · O Perfil só de cadastro reserva com cota continua pondo todo inscrito na cota.** *(RC-135 da auditoria.)* É a
  consequência declarada do item 2 acima.

---

## DP-15 — Documento público por marco?

*Decide na spec do passo 4, se ela vier.*

Hoje há uma publicação raiz por marco **e por lista** (`divulgacao/models.py:53`), e o recurso republica
só o recorte que ele alcança. O Edital real publica um "Resultado preliminar".

- **A. Manter um documento por recorte.**
- **B. Um documento do marco que reúne os N atos**, que continuam por recorte.
- **C. Um ato único por marco**, com a republicação depois de recurso redesenhada.

**Recomendação: A**, até o setor mostrar a necessidade. Se ela vier, B antes de C, porque B não mexe na
unidade do ato.

---

## DP-16 — O não atendimento pode ser registrado em lote?

*Decide na spec do passo 3.*

Dos sete desfechos, o não atendimento vem "do vencimento informado"
(`convocacao/domain/nomes.py:30-33`). Aceite, indeferimento, regularização e desistência são decisões
sobre uma pessoa. O requerimento de matrícula do portal consulta a convocação, mas nenhum desfecho sai
dele.

- **A. Unitário**, como hoje.
- **B. Um gesto registra o não atendimento de todos os vencidos**: N registros, cada um com autor.
- **C. Derivado, sem ato.**

**Recomendação: B.** Tira a repetição e preserva a autoria de cada registro. C apaga o autor.

### O que foi decidido

Em 28/09/2026, o usuário escolheu a **B**, ao abrir a spec do passo 3 — a
[`050`](../specs/050-convocacao-como-fluxo/spec.md), antecipada para antes do piloto. Um gesto registra o
não atendimento de todas as convocações do recorte com o vencimento decorrido e sem desfecho, e grava
**um desfecho por convocação**, cada um com autor, fundamento, efeito na ocupação e linha própria na
trilha — indistinguível do registrado um a um, porque passa pelo mesmo registro.

**O que fica de fora do gesto, e por quê.** A convocação com o prazo em curso; a com o prazo não
iniciado, porque a comunicação não saiu e o prazo não correu; e a sem vencimento, porque o Edital não
publica prazo e não há vencido a reconhecer — essa continua individual, como antes. Aceite,
indeferimento, regularização, desistência, reclassificação e inércia continuam individuais: são decisão
sobre uma pessoa.

**O que veio junto, na mesma spec.** A convocação dos titulares num ato só, com a comunicação saindo do
próprio ato; espécie e fundamento derivados, e o vencimento informado uma vez por ato, digitado ou
tirado de um Evento do Cronograma; e a apuração seguinte emitida pelo próprio desfecho quando nada além
dele mudou e a conta não move vaga. As três outras escolhas da clarificação — só titulares no gesto,
vencimento uma vez por ato, publicação registrada num segundo gesto — estão na spec.

---

## DP-17 — A automação explícita entra na Constituição?

*Decide antes da spec do passo 1, porque é ela a primeira a inferir e a materializar.*

A proposta é de um invariante, sem forma de tela:

> **Decisões derivadas e ações em lote permanecem explícitas.** Quando o sistema inferir, derivar ou
> materializar valores em nome do operador, DEVE tornar visíveis, antes do ato irreversível, o resultado
> e a sua origem. Quando uma ação humana produzir efeitos sobre múltiplos objetos, DEVE tornar explícito
> o alcance antes da confirmação. A automação NÃO DEVE ocultar consequências nem eliminar a autoria.

- **A. Emenda à Constituição**, como expansão do Princípio IV (Regras Explícitas). Pela seção
  *Governance*, é MINOR (`1.2.0`), com Sync Impact Report e aprovação institucional.
- **B. Só nas specs**, repetido em cada uma.

**Recomendação: A**, só com o invariante. As formas, como o que a Revisão mostra e a prévia dos Perfis
afetados, ficam nas specs.

### O que foi decidido

Em 28/09/2026, o usuário escolheu a **A**: emenda ao Princípio IV (Regras Explícitas), só com o
invariante, e sem forma de tela. A [Constituição](../.specify/memory/constitution.md) passa à
**1.2.0** (MINOR, expansão material), com o texto da proposta ajustado ao estilo dela, sem mudar o
sentido: o título vira sentença normativa (*"DEVEM permanecer explícitas"*), e uma frase final diz
que a forma da exposição é definida nas especificações, que é o "sem forma de tela" da decisão.

**A aprovação institucional foi dada pelo usuário em 28/09/2026**, no PR da emenda
([#219](https://github.com/vitofranzosi/processo_seletivo/pull/219)), como a Governance exige antes
da adoção.

**O que a conferência das specs existentes deu**, registrado por inteiro no Sync Impact Report da
Constituição:

- **Conformes, sem adequação:** a `013` (a conferência do lote declara o alcance e o total por
  consequência, e o ato consolida o conjunto conferido; um evento e um autor por Resultado), a `043`
  (duplicar não grava por si, e a cópia chega à publicação pela mesma Revisão), a `045` (a fase é
  derivada e dita como derivada, sem ato irreversível), a `023`, a `016`, a `030` e a `048`.
- **Uma lacuna, registrada e não corrigida:** na `044`, a conferência da Revisão diz o alcance do
  documento transversal pela regra (*"em todos os Perfis"*), e não pelo número, que a opção de recorte
  diz (UX-080). O conjunto se resolve na leitura, e o número visto ao declarar pode envelhecer até a
  publicação. Mostrar *"n de N Perfis"* na Revisão é requisito novo, e não correção direta: fica como
  proposta, sem escopo atribuído.
- **Uma decisão em aberto que o invariante alcança:** a opção **C** da `DP-16`, *"derivado, sem
  ato"*, elimina a autoria do não atendimento, e passa a precisar de justificativa aprovada. A
  recomendada, **B**, já cumpre o invariante.

**O que isso significa para a spec do passo 1.** Ela é a primeira sob o invariante, e é nela que ele
ganha forma: a prévia da regra da `DP-13`, com cada criação, substituição, ausência de mudança ou
exclusão, e o motivo.

---

## DP-18 — Quem faz o teste operacional, e quando?

*Decide o passo 0,5.*

Só dois números de esforço da reavaliação foram medidos; os demais são estimativas por custo unitário. O
teste calibra esses números antes das specs estruturais.

- **Quando:** depois do passo 0. Antes dele, o teste mediria defeitos já conhecidos.
- **O quê:** o 28/2026, o Edital médio da amostra, que só tem estimativa (~250–310 interações hoje).
  Primeiro a composição; depois um marco com poucas inscrições montadas à mão, porque o `seed_demo` não
  produz o certame.
- **Como:** uma pessoa do setor compõe, e quem observa não ajuda, porque a dúvida é o dado. Registram-se
  o tempo, as interações e cada dificuldade num de quatro tipos: **repetição** ("já fiz isso"),
  **hesitação** ("não sei qual escolher"), **consulta externa** (voltar ao PDF, perguntar a alguém) e
  **recuperação de erro** ("configurei e só descobri depois"). A repetição mede esforço mecânico; as
  outras três, carga cognitiva.
- **Onde:** em ambiente local, sem autenticação, com datas futuras, porque não há cadastro retroativo de
  Edital.
- **Quem:** a decidir.

---

## DP-19 — Marcar na composição os campos que não se corrigem depois de publicados é requisito novo?

*Registrada em 27/09, ao executar o passo 0. Saiu dele por decisão do usuário: o passo 0 é "sem spec,
contra requisito escrito", e este item não tem requisito. É o RC-136 da auditoria.*

### O fato

A reavaliação de 27/09 diz que *"uns 15 campos não se corrigem depois de publicados, e nada avisa na
composição"* (§D.2, item 6) e propõe *"marcados na composição"* (§D.3). A lista de correções diretas
diz que elas *"restauram requisito escrito ou fecham uma porta que falta"*, sem dizer qual das duas
cada item é. Para este, a conferência de 27/09 contra as specs e o histórico deu:

- **Nenhum requisito o exige.** O que existe sobre campos que não se corrigem é da **tela de
  Retificação**, e está atendido: a `FR-312` e o `SC-102` da `026`, conferidos por
  `tests/interface/test_retificar_exclusoes.py`. A `D1` da `044` diz que o código da Modalidade é
  estrutural, e não pede nada à composição.
- **Nada foi removido.** Nenhum cartão do assistente mostrou, em momento algum, que um campo não se
  corrige depois de publicado. O commit que introduziu o teste da ajuda visível (`0268d022`) só
  escondeu *"Identificação estável, sem espaços"* da chave do documento, e o texto continua apontado por
  `aria-describedby`. Os demais textos sobre isso nas parciais são `{% comment %}`.
- **Dois textos escritos apontam contra.** A `026`, §7: *"A tela de composição do Edital. Nada aqui muda
  a elaboração"*. A `FR-428` da `030`: a composição NÃO DEVE apresentar texto de ajuda visível dentro
  dos cartões — é o que `test_nenhum_cartao_do_assistente_carrega_ajuda_visivel` guarda. O "selo de
  estado" do passo 0 era a forma de passar por ela, e isso já é decidir sobre ela.

### O que ficaria por decidir numa spec

- **Se o selo é ajuda.** Um marcador por campo, derivado do contrato, é estado do campo ou explicação
  dele? A resposta decide se a `FR-428` precisa de emenda.
- **Quais naturezas.** `NAO_RETIFICAVEL` tem razão escrita; `ESTRUTURAL` (o código do Perfil e o da
  Modalidade) não tem, e é justamente o caso que a reavaliação cita.
- **Onde a razão mora.** No cartão, no `como-preencher` da etapa (como a `FR-428` já manda fazer com o
  conceito), ou só na Revisão, antes de publicar — que é onde a `DP-03` pôs o aviso do `UX-001`.
- **A fonte única.** Derivar do contrato, como a Retificação já faz em `exclusoes_do_tipo`, e não de
  uma lista na composição — a lição da `026` sobre listas que envelhecem.

### O que foi decidido

Em 28/09/2026, no pedido da spec do passo 1 ([`051`](../specs/051-padroes-e-aplicar-a-todos/spec.md)),
o usuário escolheu **a Revisão, antes de publicar**: os campos que não se corrigem depois de
publicados ficam visíveis ali, e não nos cartões. Com isso a `FR-428` da `030` não precisou de emenda
(o selo não chegou a existir), e as quatro perguntas acima se responderam na spec: as naturezas são a
não retificável e os **códigos** entre as estruturais; a razão mora na Revisão, a do contrato; e a
fonte é o contrato (`FR-936`, `FR-937`, `SC-346` da `051`).

---

## DP-20 — O PDF do sistema vale como Edital oficial: o que ele precisa ter, e com quais seções?

*Registrada em 28/09, depois de o usuário decidir, na mesma data, que no piloto o PDF gerado pelo
sistema **será o documento oficial do Edital**, sem documento próprio do setor em paralelo. Com isso,
o documento deixou de ser acabamento: o que ele omite, erra ou inventa passa a ser norma publicada, e
só sai por Retificação pública. É o único domínio da [auditoria de
consolidação](auditoria-de-consolidacao-2026-09-26.md) (§9, "Documento publicado") sem passo na
[ordem de 27/09](#depois-da-reavaliação-de-2709): o passo 4 é o documento **de resultado** por marco
(`DP-15`), e não o do Edital. O `RC-22` (a hora "às 00h") está em outra sessão, e aqui só é citado.
Conferida contra a `main` em `d65f0136`. É análise; nada foi decidido nem mudado no código.*

### De onde vem

- **A auditoria de 26/09**, §3.2: o RC-20, o RC-21, o RC-23, o RC-24, o RC-25 e o RC-26; a B-9
  ("conferências baratas do documento") e a B-16 ("hora, fecho e seções").
- **O [estudo de esforço](estudo-esforco-de-cadastro-2026-09-21.md)** de 21/09: §9 e §9-bis
  (original × PDF gerado nos cinco Editais), §13/E5 e E10, §15 ("três decisões, antes de qualquer
  spec").
- **As specs**: a `006` (catálogo de seções, `FR-034` a `FR-041`), a `008` (composição institucional,
  `FR-005` a `FR-044`) e a `020` (anexos).
- **O renderizador**, `publicacoes/infrastructure/pdf.py`, e o catálogo, `editais/domain/secoes.py`.
- **Os Editais da amostra**, lidos de novo em 28/09 com `pdftotext -layout`: os **quinze** do Cefor
  que têm texto extraível — 78/2026, 59/2026, 77/2026, 158/2024 e 58/2026 (FIC); 57/2026, 28/2026,
  149/2024 e 35/2026 (pós-graduação e aperfeiçoamento); 140/2025, 173/2025, 14/2026 e 146/2025
  (seleção de bolsista UAB/FAPES); 69/2026 e 76/2026 (chamada pública de curso técnico). O 62/2026 e
  o 73/2026 são imagem, sem texto. Nenhum dado pessoal foi copiado para cá.

### O que o sistema imprime hoje, em ordem

`render_edital_pdf` compõe, nesta ordem: brasão; órgão em quatro linhas (constante, `ORGAO`); o
**anúncio do ato**; a descrição do Edital; o preâmbulo (a seção `apresentacao`, sem número); as
seções numeradas do catálogo, pulando a gerada cuja coleção está vazia; o bloco "Autoridade
responsável pelo ato"; e a verificação de integridade, com o SHA-256.

O catálogo (`secoes.py`) é fixo desde a `006`, com **12 entradas** — 7 textuais, contando a
apresentação, e 5 geradas. Materializado, o documento sai com o preâmbulo e até 11 seções:

> 1. Disposições Preliminares · 2. Requisitos Gerais de Participação · 3. Da Inscrição ·
> 4. Documentos Exigidos para a Inscrição *(gerada)* · 5. Perfis de Vaga *(gerada)* ·
> 6. Etapas de Avaliação *(gerada)* · 7. Critérios de Classificação · 8. Cronograma *(gerada)* ·
> 9. Dos Recursos · 10. Anexos *(gerada: só os rótulos)* · 11. Disposições Finais

Três propriedades do código que o documento oficial herda, e que nenhum RC registra por inteiro:

1. **Seção textual não se esvazia, e a intocada publica a redação padrão.** A `FR-041` da `006`
   recusa seção textual sem conteúdo (`_topologia_das_secoes`), e `ler_secoes`
   (`interface/forms.py`) só grava o texto que difere do padrão: apagar o campo devolve o padrão. A
   Revisão não avisa quando uma seção vai ao ato com a redação do catálogo, que nunca ninguém revisou;
   a tela diz só *"Redação institucional padrão — revise antes de submeter"*. E a redação padrão
   afirma norma: a de "Critérios de Classificação" diz que a classificação *"observará a pontuação
   obtida nas Etapas de Avaliação, respeitados os pesos e as notas mínimas… e as reservas de vaga"* —
   falso num Edital por sorteio, que é o caso do 28/2026, o Edital do teste operacional (`DP-18`). A
   de "Apresentação" abre por *"O Instituto Federal do Espírito Santo… torna pública"*, e não pela
   autoridade que pratica o ato, como os quinze Editais fazem.
2. **O texto é parágrafo corrido.** A seção textual não tem tabela, subitem numerado nem negrito.
   O Quadro 1 do 28/2026 (a matriz curricular) não tem como ser escrito, e o "4.1" que o autor
   digitar no texto é número dele, e não do documento.
3. **O catálogo é conferido também depois de publicado.** A mesma `_topologia_das_secoes` roda na
   Retificação e compara `order`, `title` e `type` com o catálogo **vigente**. Mudar o catálogo
   depois de o primeiro Edital real ser publicado faz a Retificação dele ser recusada, a menos que o
   catálogo passe a ter versão. É por isso que a E5 tem **prazo**: antes da primeira publicação do
   piloto, mudar o catálogo é barato; depois, pede versão de catálogo, e o acervo passa a ter duas
   formas de documento, porque documento publicado não se regenera.

### 1. Os RCs, classificados

| RC | O que é | Classificação | Requisito escrito, ou a pergunta |
|---|---|---|---|
| **RC-20** | A capa imprime o **título** no lugar do ato sempre que o título abre por "Edital" (`pdf.py`, `_cabecalho`); o rodapé e a verificação usam `number`/`year`. O documento pode se identificar com dois números, ou com nenhum, se o título abrir por "Edital de seleção…" | **Correção direta** | `FR-006` da `008`: *"O ato — `EDITAL Nº <número>/<ano>` — DEVE ser destacado"*; `SC-001`, o ato na primeira página. `number` e `year` são a identidade do Edital (`uq_edital_scope_number_year`) e não se retificam; o `title` se retifica. O teste `backend/tests/unit/publicacoes/test_pdf.py:593` prende a leitura atual (`"EDITAL 07/2026 — PROFESSOR SUBSTITUTO"`, `count("EDITAL") == 1`) e é emendado no mesmo commit; a fixture de bytes é refeita junto (`FR-044` da `008`). *O aviso "título × número" na Revisão (B-9) é complemento sem requisito, e opcional depois da correção.* |
| **RC-21** | "ANEXO IV" citado no texto sem anexo publicado com esse rótulo; nada confere | **Precisa de decisão** (pequena) | Nenhum requisito da `020` cobre a remissão no texto; a `FR-006` de lá proíbe derivar ou renumerar rótulo, e não proíbe conferir. **Pergunta:** aviso ou impeditivo? A remissão casa também "Anexo III da Resolução…", de outro ato, e por isso o impeditivo erraria. |
| **RC-22** | a hora "às 00h" | *fora desta DP* | outra sessão |
| **RC-23** | O fecho imprime *"Autoridade responsável pelo ato"*, o **nome** do catálogo e o cargo; sem local, data, portaria de nomeação nem assinatura | **Precisa de decisão** | A letra vigente **proíbe** parte do que falta: `FR-036` da `008`, *"O bloco de autoridade NÃO DEVE conter praça nem data"*; `FR-033` e `FR-037`, registro e não assinatura. O catálogo (`publicacoes/domain/autoridades.py`) tem designação de cargo no campo de nome (*"Diretora do Cefor"*) e identificadores de exemplo; as *Assumptions* da `008` preveem trocá-lo por nome próprio como trabalho editorial, sem mudança no bloco. A portaria não existe na `Publicacao` nem no catálogo. **Perguntas:** como o ato é assinado; e o fecho leva local, data, nome e portaria? |
| **RC-24** | 12 seções fixas; a amostra tem 7 a 22; o que não cabe vira parágrafo em caixa alta dentro de outra seção; a inscrição e os documentos vêm antes dos Perfis | **Precisa de decisão** (E5) | Contra a letra: `FR-034` da `006` (*"O conjunto de seções e a ordem… são definidos pelo sistema; quem elabora… NÃO acrescenta, remove nem reordena"*), `FR-041` (textual não fica vazia) e o *Out of Scope* da `008` (*"subseção arbitrária, tipo novo de seção"*). A opção A abaixo só muda a ordem, que a `FR-034` deixa ao sistema; a B e a C mudam spec. |
| **RC-25** | 0 de 7 atos normativos no documento em dois Editais; nada percebe | **Precisa de decisão** (E10) | Nenhum requisito. É processo do Cefor: quem redige, onde, e quem confere. |
| **RC-26** | Quatro coisas: o **total de vagas** não sai; a **numeração** da tela Conteúdo (1 a 12, pela ordem do catálogo) não é a do PDF (preâmbulo sem número, geradas vazias puladas); o **requisito** do Perfil e a **instrução** do documento exigido são dois textos livres que já se contradisseram (AX-2); o anexo sem destinatário | **Precisa de decisão**, em partes | Total e numeração: nenhum requisito, a favor ou contra; são decisões pequenas, e a numeração muda de qualquer jeito com a E5. Requisito × documento: modelagem, com a E2 (B-17). Anexo sem destinatário: registrado em 08/09 como não defeito ([achado](achado-anexo-sem-destinatario.md)), e continua não sendo. |

**Duas unidades vizinhas entram na mesma conta**, porque são norma que o documento oficial cala:

- **RC-12, o teto de inscrições por candidato.** Executado (`submissao.py`), no conteúdo publicado
  (`maxInscricoesPorCandidato`) e ausente do PDF. **Correção direta** contra a `FR-063` da `015`:
  *"O Edital MUST poder publicar um teto de inscrições por candidato"*. A B-9 já o junta ao RC-20.
- **A declaração do Requerimento de Matrícula** (`matriculationRequest`), que a `029` registrou
  como limite, e não como esquecimento (Q-10): quem lê o Edital não vê a declaração que vai aceitar.
  **Decisão**, e pequena.

### 2. As opções para a E5 e a E10

#### E5 — o conjunto de seções do documento

O que a amostra mostra. As seções numeradas, por família:

| Família | Editais | Seções | O que se repete |
|---|---|---:|---|
| FIC | 78, 59, 77, 158, 58 | 10–11 | Informações gerais sobre o curso · Público-alvo · Requisitos para inscrição · Das vagas · Inscrição · Do processo seletivo · Recurso · Matrícula · [Acesso e informações] · Certificado · Disposições finais |
| Pós e aperfeiçoamento | 57, 28, 149, 35 | 13–15 | as da FIC, mais **Verificação da autodeclaração**, **Procedimento complementar** (heteroidentificação), **Homologação da matrícula** e **Entrevista PcD** |
| Bolsista UAB/FAPES | 140, 173, 14, 146 | 12–22 | Disposições preliminares · Funções · Requisitos · Vagas · Inscrição · Prova de títulos / Entrevista · Recursos · Verificação · Classificação final · **Convocação** · **Mobilidade entre perfis** · **Curso de formação** · **Vinculação à UAB / Pagamento da bolsa** · **Prazo de validade** · Disposições finais |
| Chamada pública técnica | 69, 76 | 7–8 | Sobre o curso · Requisitos · Inscrição · Classificação · Preenchimento das vagas · Disposições finais |

Três regularidades valem para os quinze: **a oferta vem antes da inscrição**; há **Disposições
finais com os casos omissos**; e há **cronograma em tabela** — em doze deles, como **anexo** (I ou II),
depois do fecho, e não como seção do corpo. No 28/2026, o Edital do teste operacional, **8 das 15 seções
não têm lugar** no catálogo: Público-alvo, as duas de verificação, Matrícula, Acesso ao curso,
Homologação da matrícula, Certificado e Entrevista PcD.

| | A. Reordenar e aparar | B. Catálogo ampliado, com textuais opcionais | C. Seções acrescentáveis por quem elabora |
|---|---|---|---|
| **O que é** | O catálogo continua com 12 entradas. Perfis passam para antes da Inscrição; a redação padrão que afirma norma sai, ou vira aviso na Revisão enquanto não for revisada. | O catálogo ganha as seções que se repetem nas famílias da amostra (Público-alvo, Verificação da autodeclaração, Convocação, Matrícula, Certificado, Prazo de validade, Informações sobre o curso…). A textual passa a poder ficar **vazia**, e vazia não sai no documento, como a gerada. As novas nascem **sem** redação padrão. | O autor acrescenta seção textual, com título e posição, entre as do catálogo. As geradas continuam fixas. |
| **O que muda na letra** | nada de requisito; só a ordem, que a `FR-034` já deixa ao sistema | a `FR-041` da `006` (textual sem conteúdo deixa de ser impeditivo) | a `FR-034` e a `FR-041` da `006`, o *Out of Scope* da `008`, a gramática da Retificação (`ADD /sections/-`, hoje recusado pela topologia) e o contrato da `026` |
| **Custo** | Pequeno: a ordem no catálogo, a fixture de bytes, os testes que prendem a numeração. Sem spec, se o usuário decidir a ordem. | Médio: uma spec curta. Catálogo, validação, tela Conteúdo (de 7 para ~15 caixas de texto, e a tela precisa dizer quais a família usa), numeração, reuso. | Grande: identidade da seção (hoje `uuid5` sobre a chave do catálogo), Retificação, "O que mudou", reuso, numeração. E reabre o que a `006` recusou de propósito: *"É o que separa um documento institucional estruturado de um construtor de documentos"*. |
| **Risco** | Não resolve a falta de lugar: a matrícula do 28/2026 continua dentro de "Disposições finais". | Cada família nova pede entrada nova no catálogo — uma linha de código revisada, e não uma escolha do autor. A família de bolsista tem seções idiossincráticas (Mobilidade, Curso de formação), que caberiam numa entrada "Outras disposições". | A norma que o sistema executa foge para texto livre ao lado da estrutura que a executa: é a família (a) do AX-3, *"resolve a publicação e deixa a norma inexecutável"*. |
| **RCs que fecha** | RC-24 só na ordem (M10); RC-26 na numeração, se a tela passar a mostrar o número do PDF | **RC-24** para as quatro famílias da amostra; RC-26 na numeração; e a redação padrão que afirma norma deixa de sair sem revisão | RC-24 inteiro; RC-26 na numeração |

**Três escolhas atravessam as três opções**, e cabem na mesma decisão:

- **Cronograma: seção ou anexo?** Doze dos quinze o publicam como anexo (I ou II), depois do fecho. No
  sistema, "Anexo" é arquivo à parte (`020`, D-002), com rótulo digitado pelo autor, e um "Anexo I"
  gerado colidiria com o "ANEXO I" que o autor escrever. Manter como seção não tira validade de nada.
- **Redação padrão das textuais.** Continua existindo? Se continuar, a Revisão avisa quando uma seção
  vai ao ato sem revisão, e a de "Critérios de Classificação" deixa de afirmar pontuação.
- **A tela mostra o número que o PDF vai imprimir**, derivado da mesma regra (`_materializaveis`), e
  não a ordem do catálogo.

#### E10 — redação no sistema ou transcrição

O estudo mediu a transcrição: um PDF pronto redigitado. Nos dois Editais transcritos de memória, 0 de 7
atos normativos chegaram ao documento; no transcrito com conferência, 11 de 13. **A decisão de 28/09
não responde a E10**: ela diz que o PDF do sistema é o oficial, e não onde o texto nasce.

| | A. Redação no sistema | B. Transcrição, com conferência humana registrada | C. Transcrição, com conferência assistida |
|---|---|---|---|
| **O que é** | O texto normativo é escrito na tela Conteúdo, e não existe original em Word. | O setor continua redigindo no Word, e o texto é transcrito. Antes de homologar, alguém confere a prévia contra o original, com a lista do item 3 abaixo. A homologação já exige uma segunda pessoa, e é o ponto natural. | Como B, e o original é anexado ao rascunho, sem ser publicado. A Revisão lista os atos normativos (Lei, Decreto, Portaria, Resolução nº…) e os "ANEXO X" citados no original que o texto composto não cita. |
| **Custo** | Nenhum no código. No processo, o setor passa a redigir em caixa de texto sem tabela, subitem ou negrito, e isso depende da E5: sem lugar, a norma vai para a seção errada. | Nenhum no código, ou um texto de declaração na homologação, se o usuário quiser o registro no ato. | Spec curta a média: armazenar arquivo não público, extrair texto de PDF e DOCX — o renderizador foi escrito sem dependência externa, e ler esses formatos pede uma —, conferir e avisar. |
| **Risco que sobra** | a redação padrão publicada sem revisão; a prosa herdada no reuso (RC-43) | a conferência depende de quem confere, e o sistema não sabe se ela aconteceu | pega a citação perdida, e não o parágrafo perdido |
| **RCs que fecha** | **RC-25**, por definição: sem fonte, não há fidelidade a perder. O RC-43 continua | RC-25 pelo processo, e não pelo produto | RC-25 na parte medida, as citações; ajuda no RC-21 |

*Excluída pela decisão de 28/09:* o Word continuar como o ato oficial e o PDF do sistema como
extrato — a família (d) do AX-3.

### 3. O mínimo indispensável para o PDF valer como documento oficial no piloto

**Não há, no repositório nem na amostra, norma do Ifes que liste o conteúdo obrigatório de um
Edital.** O que está abaixo é o que os quinze Editais têm **sem exceção**, ou o que o próprio sistema
executa e por isso precisa estar publicado. Confirmar a lista é do Cefor `[VALIDAR com o Cefor]`.

| Elemento | Na amostra | O que o PDF do sistema faz | | Caminho |
|---|---|---|---|---|
| Número do ato na abertura, com o objeto | 15 de 15 | Troca o ato pelo título quando ele abre por "Edital" | **erra** (RC-20) | correção direta |
| Autoridade que pratica o ato, no preâmbulo (*"A Diretora do Cefor… torna público / faz saber"*) | 15 de 15 | Preâmbulo é texto livre; o padrão fala pela instituição, sem a autoridade | **inventa**, se não for revisado | E5 (redação padrão) |
| A oferta antes da inscrição | 15 de 15 | Inscrição e documentos (3, 4) antes dos Perfis (5) | **erra** a ordem (RC-24) | E5 |
| As seções da família | 7 a 22 | 11, fixas; no 28/2026, 8 de 15 sem lugar | **omite** a estrutura (RC-24) | E5 |
| Cronograma, com as datas como declaradas | 15 de 15 | Tabela como seção 8; hora "às 00h" onde ninguém a declarou | **inventa** a hora (RC-22, outra sessão) | outra sessão |
| Disposições finais, com os casos omissos | 15 de 15 | Seção existe; o padrão manda os omissos à *"autoridade responsável"*; os que conferi nomeiam a comissão, o setor de seleção ou a Coordenadoria Geral de Ensino | **inventa**, se não for revisado | E5 (redação padrão) |
| Remissão a anexo que exista | anexos citados de 2 a 39 vezes por Edital | Lista os rótulos; não confere o texto | pode **errar** (RC-21) | decisão pequena |
| Local e data do ato | 15 de 15 | Não imprime: a `FR-036` da `008` proíbe | **omite** (RC-23) | decisão; emendar a `FR-036` |
| Nome de quem assina | 15 de 15 | Imprime a designação do cargo no lugar do nome (*"Diretora do Cefor"*) | **inventa** um nome que não é nome (RC-23) | dado do Cefor no catálogo (*Assumptions* da `008`) |
| Ato de nomeação de quem assina | 15 de 15 | Não existe no modelo | **omite** (RC-23) | decisão; campo na `Publicacao` |
| Como o ato é assinado | nenhum dos 15 traz marca de assinatura eletrônica no texto extraído | Declara-se *"registro, não assinatura"* (`FR-033`, `FR-037`) | pergunta aberta | **decisão institucional**, antes de tudo |
| O teto de inscrições por candidato | onde o Edital o declara | Executa e não publica | **omite** (RC-12) | correção direta (`FR-063` da `015`) |
| A declaração do Requerimento de Matrícula | onde o Edital a exige | Exige o aceite e não publica | **omite** (`029`, Q-10) | decisão pequena |
| O documento consolidado se diz retificado, e de quando | arquivos "retificado em dd/mm" e anexos "(RETIFICADO)" | O consolidado da Retificação sai igual ao original, sem data nem marca; só o SHA-256 os distingue | **omite** | com o fecho: a data do ato |
| A legislação que o Edital cita | 3 a 13 atos, nos cinco do estudo | Depende de quem transcreve; nada confere | **omite** sem aviso (RC-25) | E10 |

**Dois fatos técnicos que baixam o custo do fecho.** A data do ato **existe** no momento da
composição, nos dois fluxos: `published_at=now` em `publish_edital.py` e em `retificacoes.py`, a poucas
linhas de `render_edital_pdf`. Ela chegaria ao compositor pelo mesmo caminho da autoridade, como
contexto do ato e fora do conteúdo (`FR-034` da `008`), e o hash do conteúdo não muda. O obstáculo da
`FR-036` é de decisão, e não de engenharia. E a unidade já é constante do compositor (`ORGAO`); o local
seria outra constante, e não um cadastro.

**Uma letra da `008` que o renderizador já não segue, e não deve voltar a seguir.** A `SC-001` pede
o Processo na primeira página, entre o ato e o título. Desde a `008`, `_cabecalho` não o imprime: o
Processo só sai no bloco de verificação. É o certo para a amostra, que não nomeia Processo algum
(estudo, §7.1). A spec que vier emenda a `SC-001` para dizer o que o documento já faz.

### 4. Recomendação

**Pode ir já, como correção direta, sem spec** (o passo 0 de 27/09 é o precedente):

1. **O RC-20.** O ato sai sempre de `number`/`year` (`FR-006` da `008`), seguido do título; o título
   que repete exatamente o ato perde o prefixo, para o anúncio continuar uma sentença só. Emendar o
   `test_pdf.py:593` e refazer a fixture no mesmo commit.
2. **O RC-12.** O teto por candidato no documento (`FR-063` da `015`), onde a B-9 já o pôs.

**Pode ir já, sem spec, com uma decisão de uma linha do usuário:**

3. **Avisos na Revisão**, e nenhum impeditivo: "ANEXO X" citado sem rótulo correspondente (RC-21); e
   seção textual que vai ao ato com a redação padrão, sem revisão (a propriedade 1 acima).

*Os itens 1 a 3 foram feitos em 28/09, no PR das correções antes do piloto, com a decisão do item 3
tomada pelo usuário no mesmo dia (aviso, sem impeditivo). O campo do teto na composição veio
depois, no mesmo dia, pelo PR 224 — ver o registro pré-piloto de 28/09, "Achados da implementação".*
4. **O nome próprio no catálogo de autoridades**, quando o Cefor o fornecer. As *Assumptions* da
   `008` já dizem que o bloco o exibe sem mudança. Enquanto não houver, o fecho continua dizendo um
   cargo onde o leitor espera um nome.

**Decidir antes da spec, nesta ordem:**

5. **Como o ato é assinado no piloto** `[VALIDAR com o Cefor]`. Se a Diretora assinar o PDF fora do
   sistema, o documento assinado é outro arquivo, e o sistema publica um que ninguém assinou; se o
   Cefor aceitar o PDF com o registro de autoria e o SHA-256, a `FR-037` fica como está. É a pergunta
   que decide se o documento vale, e nenhuma linha de código a responde.
6. **A E10.** Recomendo **B** para o piloto: transcrição com conferência na homologação, pela lista do
   item 3. Custa zero no código e aproveita a segunda pessoa que a homologação já exige. A **C** só se
   o teste operacional mostrar perda de citação mesmo com a conferência. A **A** é o destino, e só é
   viável depois da E5, porque sem lugar a norma vai para a seção errada.
7. **A E5.** Recomendo **B**: o catálogo ampliado pelas famílias que o piloto vai operar, com textual
   opcional e sem redação padrão que afirme norma; a oferta antes da inscrição; a tela com o número do
   PDF; o cronograma como seção. A **A** não fecha o que o 28/2026 precisa. A **C** reabre a recusa
   da `006`, e o custo dela só se paga se aparecer uma família que B não acomoda.

**Uma spec só, depois dessas decisões**, *"O Edital do sistema como ato oficial"*, com: o catálogo
da E5; o fecho (emenda à `FR-036`: local e data do ato, como contexto, fora do conteúdo; a portaria de
nomeação registrada na `Publicacao`); o consolidado da Retificação datado; a declaração do
Requerimento de Matrícula; o total de vagas, se o usuário o quiser; e a emenda da `SC-001`.

**O prazo.** Antes da **primeira publicação real do piloto**. Depois dela, mudar o catálogo pede
versão de catálogo (a propriedade 3 acima), e o acervo fica com duas formas de documento. O teste
operacional da `DP-18` é o lugar barato para conferir esta lista: gerar o PDF do 28/2026 e compará-lo
ao original, item por item, antes de escrever a spec.

### O que foi decidido

Em 28/09/2026, o usuário decidiu três das escolhas acima. A análise fica como estava.

- **E10 = B** — transcrição com conferência na homologação. O setor continua redigindo fora do
  sistema, e quem homologa confere a prévia contra o original, pela lista do item 3. Nada no código.
- **E5 = B** — o catálogo ampliado pelas famílias que o piloto vai operar, com a seção textual
  opcional e **sem redação padrão que afirme norma**. É spec, a *"O Edital do sistema como ato
  oficial"* da recomendação, e o prazo dela continua o de cima: antes da primeira publicação real.
- **Avisos na Revisão = sim** — os dois do item 3 da recomendação, sem impeditivo: *"ANEXO X"* citado
  sem rótulo correspondente (RC-21), e seção textual que vai ao ato com a redação padrão, sem revisão
  (a propriedade 1). Implementados pelo PR 220, com o RC-20 e o RC-12.

**Ficam pendentes, com o Cefor**: como o ato é assinado no piloto (o item 5 da recomendação) e o nome
próprio de quem assina no catálogo de autoridades (o item 4). Nenhum dos dois se resolve no código
antes da resposta do Cefor.

---

## DP-21 — A composição grava coleções maiores que mil campos?

*Registrada em 29/09, a pedido do usuário, a partir do
[achado da etapa Perfis](achado-etapa-perfis-recusa-acima-de-mil-campos.md), encontrado ao medir a
escala da tela para a [análise das coleções repetidas](analise-ux-colecoes-repetidas-2026-09-29.md).
A [`052`](../specs/052-perfis-visao-do-conjunto/spec.md) o deixou fora de escopo de propósito: ela
muda o que se vê, e esconder cartões não diminui o que se envia. Conferida contra a `main` em
`c02ad739`. É análise; nada foi decidido nem mudado no código.*

### O problema

A etapa Perfis grava a coleção inteira num POST, e o Django recusa com **400**, antes da view,
qualquer envio com mais de `DATA_UPLOAD_MAX_NUMBER_FIELDS` campos — mil, o padrão, que o projeto não
altera. Medido: o 27º Perfil de duas Modalidades passa do teto; com três Modalidades e quadro
repartido, o formato do 140/2025, ele cai para perto de **18 Perfis**. O 140/2025 tem 16; o multicampi
que a `051` projeta tem **66**. A Classificação tem o mesmo teto, com ~28 campos por marco e 5 por
critério. A Retificação envia o formulário inteiro do mesmo jeito, e **não foi medida**.

O que a pessoa vê é a página de erro do servidor, sem a tela da etapa e sem dizer o que fazer. Na
etapa Perfis o rascunho local guarda o digitado; na Classificação, que não o declara, não.

### O que já está fixado

- **A gravação da etapa substitui o rascunho inteiro** (`replace_draft`), e três decisões existem por
  causa disso: a seção do quadro no cartão (`UX-020`), a cópia que só existe no formulário até
  gravar (`FR-638`) e o gesto da `051` que lê o digitado e grava pela etapa (a decisão de
  materialização no envio da `051`). Enquanto elas valem, a etapa envia a coleção inteira.
- **O mesmo teto já foi contornado uma vez**, na confirmação da distribuição (27/09), fazendo as
  identidades viajarem num campo só. Lá eram milhares de itens de um campo cada; aqui são dezenas de
  itens de dezenas de campos.

### As opções

| | A. Subir o limite | B. Serializar a coleção num campo | C. Gravar por Perfil |
|---|---|---|---|
| **O que é** | `DATA_UPLOAD_MAX_NUMBER_FIELDS` com um valor medido para o maior Edital previsto, com folga | a tela envia a etapa como um JSON num campo só, como a distribuição | cada Perfil se grava sozinho, por comando próprio |
| **Custo** | uma linha em `config/settings` e um teste que prenda o valor | alto: a leitura da etapa, a recusa que reexibe o digitado, o rascunho local e os fragmentos do htmx leem por nome de campo; a etapa deixa de funcionar sem JavaScript | alto, e reabre a `UX-020`, a `FR-638` e a decisão de materialização da `051` |
| **Risco** | o limite é global — vale para o portal também — e existe contra envio gigante; subi-lo move o teto, não o remove | reescreve o caminho mais testado da composição | perde a atomicidade da etapa e a prévia do gesto sobre o digitado |
| **Resolve** | o multicampi de 66 Perfis, se o valor for medido para ele | qualquer tamanho | qualquer tamanho |

### Recomendação: **A**

Com o valor medido, e não chutado: compor o maior Edital previsto — o multicampi de 66 Perfis, com a
Classificação —, contar os campos da etapa mais pesada e dobrar. A conta do achado dá ~3,6 mil para os
Perfis de três Modalidades e quadro; a Classificação, com um marco de três critérios, ~2,9 mil.
Parsear alguns milhares de campos custa pouco, e o portal continua atrás do seu próprio limite de
tamanho (`DATA_UPLOAD_MAX_MEMORY_SIZE`). **B** e **C** só se pagam se aparecer Edital na casa das
centenas de Perfis, que nenhuma família da amostra tem.

**Duas coisas acompanham qualquer opção**: medir a Retificação de um Edital grande, que não foi
medida; e trocar a página de erro 400 por uma recusa que volte à etapa dizendo o que aconteceu — hoje
ela sai do assistente sem explicação.

**O prazo.** Antes do primeiro Edital real acima de ~18 Perfis com quadro repartido. Os Editais do
piloto conhecidos (78/2026, dois Perfis; 28/2026, sete) estão abaixo dele.
