# Decisões pendentes — o que a auditoria de consolidação deixou para o usuário

**Situação: abertas, menos a `DP-01` a `DP-06`, decididas em 26/09, o item 2 da `DP-08`, decidido na mesma data, e a `DP-14`, decidida em 27/09** — as quatro primeiras com
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
| Redação no sistema ou transcrição (E10) · conteúdo comum aos Perfis (E2) · conjunto de seções do documento (E5) | [estudo de esforço](estudo-esforco-de-cadastro-2026-09-21.md) §15, "Três decisões, antes de qualquer spec" (a E6 já foi decidida em 25/09) |
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
| DP-16 | O não atendimento pode ser registrado em lote? | passo 3 | um gesto, N registros com autor |
| DP-17 | A automação explícita entra na Constituição? | passo 1 | emenda ao Princípio IV, só o invariante |
| DP-18 | Quem faz o teste operacional, e quando? | passo 0,5 | depois do passo 0, com o 28/2026 |
| DP-19 | Marcar na composição os campos que não se corrigem depois de publicados é requisito novo? | passo 0 → fora dele | decidir em spec; conciliar com a `026` §7 e a `FR-428` da `030` |

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

- **A-14.1 · A tela de Modalidade única trava quem já enviou o documento da cota.** Sem campo de
  Modalidade na tela, a view calcula o descarte contra `None` (`portal/views.py`, em `inscricao`, na
  chamada a `descartes_por_mudanca_de_modalidade`), e *"Revisar inscrição"* abre *"Mudar de modalidade
  descarta documentos"*. Confirmar leva a `discard_not_confirmed`, porque `gravar_dados` assume a
  Modalidade única e não vê descarte algum. Reproduzido em 27/09. Vem de antes desta correção, e depois
  dela só alcança o Perfil com tudo em cota.
- **A-14.2 · A advertência da FR-325 soa para a forma agora correta.** `general_competition_modality_undeclared`
  (`editais/domain/validation.py`, `_ampla_por_declarar`) avisa todo Perfil que declara Modalidade sem
  apontar a ampla, e manda declarar *"qual delas é a da ampla concorrência"*. Para o Perfil que só declara
  cotas, que é o caso que esta decisão resolve, não há qual apontar.
- **A-14.3 · A gestão não nomeia nem conta a ampla sem Modalidade.** A lista e o detalhe das inscrições
  (`inscricoes/application/consulta.py`, `_nome_no_conteudo`) e a Mesa (`avaliacoes/application/mesa.py`)
  mostram a Modalidade em branco; a contagem por Modalidade descarta o nulo, e o filtro não o alcança
  (`_contagens`, `_filtrar`). A FR-067 e a FR-068 da `009` pedem a Modalidade. Já valia para o Perfil sem
  Modalidade, e passa a ser o caso comum.
- **A-14.4 · A Modalidade única que nasce por Retificação é atribuída em silêncio no envio.** Se uma
  Retificação zera a linha geral, ou dá a primeira Modalidade a um Perfil sem vaga na linha geral, o
  rascunho no nulo é recusado até o reconhecimento; depois dele, o envio grava a Modalidade única que
  `_modalidade_escolhida` devolve (`inscricoes/application/submissao.py`, eixo 5), com os documentos
  conferidos contra a inscrição sem ela. Vem de antes, pela `048`, e esta correção o estreita.
- **A-14.5 · O Perfil só de cadastro reserva com cota continua pondo todo inscrito na cota.** É a
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
contra requisito escrito", e este item não tem requisito.*

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
