# Feature Specification: O barema da Etapa — critérios publicados, pontuação por critério na Mesa

**Feature Branch**: `claude/gps-barema-investigation-1750ab`, sobre a `main` em `d184fcee`

**Created**: 2026-11-10

**Status**: Spec, plano e tarefas escritos em 10/11/2026 (PR #460) e revisados no mesmo dia pela
avaliação do usuário — seis ajustes, listados em [research.md](research.md) §4. **Incremento A
implementado em 11/11/2026** (T001–T015); B e C não iniciados. Sete questões (P-1 a P-7, ao fim) esperam validação institucional, e nenhuma delas bloqueia
o incremento A.

**Uma regra muda, e as outras ficam.** Hoje a comissão soma o barema fora do sistema — no Anexo IV
do Edital, numa planilha — e lança na Mesa o total. Esta feature traz a ficha para dentro: a Etapa
pontuada pode publicar uma lista de **Critérios de Avaliação**, e quando publica o avaliador pontua
critério a critério e o sistema calcula o total. **O total continua sendo o mesmo número de hoje**,
gravado no mesmo campo, e daí em diante nada muda: a consolidação copia, a classificação combina, a
publicação divulga e o recurso supera exatamente como já fazem.

**Input**: *"Investigar o código real, identificar o que já existe, determinar a menor evolução
necessária e produzir uma spec completa e implementável para configuração e aplicação de baremas
(análise de títulos, formação, experiência), sem motor de regras, sem DSL, sem biblioteca de
baremas, sem segundo mecanismo de classificação nem de recursos. O operador configura critérios e
pontuações; o candidato conhece os critérios e comprova; a comissão avalia e fundamenta; o GPS
consolida e usa os mecanismos existentes."* O pedido completo, com os cinco cenários, está resumido
em [research.md](research.md) §1.

> **Faixa de identificadores.** Esta spec usa:
>
> - os requisitos funcionais de cinco mil e duzentos a cinco mil duzentos e quarenta e nove;
> - os critérios de mil seiscentos e vinte a mil seiscentos e trinta e nove;
> - os requisitos de experiência de quatrocentos e vinte a quatrocentos e vinte e nove.
>
> Os números não usados ficam livres. As decisões reiniciam em `D-001`.
>
> O teto foi medido em 10/11/2026, nas `specs/` da `main`, das worktrees desta máquina e de todas as
> branches remotas: requisito cinco mil cento e sessenta e dois, critério mil seiscentos e três e UX
> quatrocentos e dois, todos da `145` (PR #459, aberto). Por isso esta é a `146`, e a faixa começa
> com folga sobre a dela.
>
> **Como esta spec cita outras.** Requisito de outra feature, pelo identificador e pela feature;
> decisão de outra feature, pelo assunto, nunca pelo identificador.

## Por que esta feature existe

O barema foi **adiado, e não recusado**. A decisão de 04/09 que o tirou do primeiro vertical escreveu
o custo: *o sistema não demonstra que o total está certo, porque não conhece as parcelas*
(`doc/decisoes-pre-vertical.md`, "Barema fica fora do primeiro vertical"). A `012`, a `013` e a `015`
o deixaram fora pelo mesmo motivo, e a reavaliação de 27/09 mediu o preço: na família de títulos, a
Mesa leva de 10 a 20 minutos por inscrição **com o barema somado fora**.

Três Editais reais da amostra têm a mesma ficha — 14/2026, 140/2025 e 90/2026 —, e o 173/2025 tem a
mesma forma sem a coluna de quantidade. Em todos, cada linha é **um título, um valor por unidade e um
teto**, e a soma dos tetos é a pontuação máxima da Etapa (100 nos quatro). É essa forma, e só ela,
que esta spec constrói ([research.md](research.md) §3).

**O que esta spec atende, e o que não.** Ela atende a ficha cujas linhas se pontuam **cada uma por
si** — critérios independentes, total igual à soma das parcelas. Ela **não** demonstra que os
títulos dos Editais da amostra sejam cumulativos: nenhum deles escreve acumulação nem exclusividade,
e a soma dos tetos dar 100 é compatível com as duas leituras (P-1). Por Edital:

| Edital | Atendido? | Condição ou limite |
|---|---|---|
| 14/2026 — Prova de Títulos e Entrevista | **Sim, se** a comissão confirmar que os títulos se pontuam independentemente | A Entrevista (faixas por categoria) é pontuação direta |
| 90/2026 — Prova de Títulos | **Sim, se** a mesma confirmação vier | — |
| 173/2025 — Prova de Títulos | **Em parte** | O teto pela expectativa declarada pelo candidato continua sendo aplicado pela comissão, fora do sistema (P-4) |
| 140/2025 — Prova de Títulos | **Não** | O teto do Doutorado varia por curso (P-5); o Edital continua lançando o total |

Edital que exija "só o maior título" não é atendido por esta spec: ele continua lançando o total, ou
espera uma regra de exclusividade validada.

O diagnóstico do código ([research.md](research.md) §2) mostrou que quase tudo já existe:
pontuação validada contra a máxima publicada, conclusão imutável e preservada, consolidação por
cópia, classificação, publicação, recurso por correção fixada e por reavaliação, documentos da
inscrição visíveis na Mesa, trilha e isolamento por escopo. **Falta uma coisa: as parcelas.** A
Etapa não sabe quais são os critérios, e a Avaliação não sabe quanto cada um valeu.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Configurar e publicar o barema de uma Etapa (Priority: P1)

Quem elabora o Edital abre a etapa **Etapas de Avaliação** do assistente e, no cartão da "Prova de
Títulos", encontra a seção **Barema**, opcional. Acrescenta cinco critérios — Doutorado (20 pontos,
1 diploma), Mestrado (15), Especialização (5 por certificado, até 10), Curso de formação (15) e
Exercício de docência (1 por mês, até 40) —, liga os três primeiros ao Documento Exigido "Títulos
acadêmicos" e o último a "Declaração de exercício de docência". A prévia abaixo mostra a ficha como
o Edital a imprimirá, com o total de 100, e a pontuação máxima da Etapa passa a ser esse total.
Publicado o Edital, o PDF traz a tabela dentro da descrição da Etapa.

**Why this priority**: sem o barema publicado, nada mais existe — ele é a regra contra a qual a
comissão pontua e o candidato comprova. Sozinho, já entrega valor: o PDF passa a sair do sistema com
a ficha, em vez de um anexo digitalizado.

**Independent Test**: configurar o barema do 14/2026, publicar, conferir o conteúdo publicado e o
texto extraído do PDF; nenhum avaliador precisa existir.

**Acceptance Scenarios**:

1. **Given** uma Etapa pontuada sem barema, **When** a pessoa acrescenta critérios e grava, **Then**
   os critérios são gravados na ordem do formulário, a pontuação máxima da Etapa é a soma dos
   máximos, e a prévia mostra a mesma tabela.
2. **Given** um critério "por quantidade" com 5 pontos por certificado e máximo 10, **When** a
   pessoa grava, **Then** a prévia diz "5 pontos por certificado, até 10".
3. **Given** uma Etapa decisória, **When** a pessoa abre o cartão, **Then** a seção Barema não é
   oferecida; **and** um conteúdo que chegue pela API com critérios numa Etapa decisória é recusado.
4. **Given** um Edital com barema, **When** é publicado, **Then** o conteúdo publicado traz a lista
   de critérios da Etapa, e o PDF a imprime como tabela.
5. **Given** um Edital sem barema algum, **When** é publicado, **Then** o PDF é o mesmo de antes da
   feature, e o conteúdo traz a lista vazia.

---

### User Story 2 — Pontuar critério a critério na Mesa (Priority: P1)

A avaliadora abre a inscrição na Mesa. Onde hoje há um campo "Pontuação", há a ficha: uma linha por
critério, com o máximo, a comprovação esperada e, quando o critério está ligado a um documento, o
link "Abrir" que mostra o PDF no painel ao lado — o mesmo de hoje. Ela informa "1" no Doutorado,
"0" no Mestrado, "3" certificados de Especialização (o sistema mostra 10, "limitado ao máximo") e
"52" meses de docência (40). O total, 70, aparece ao pé da ficha à medida que ela digita. Salva o
rascunho, volta depois, conclui.

**Why this priority**: é onde o barema paga o que custa — a soma, o limite e a conferência saem da
planilha e passam a ser do sistema, provados.

**Independent Test**: com o barema publicado da US1 e uma inscrição atribuída, pontuar, salvar,
concluir; conferir a Avaliação, a Conclusão preservada e o Resultado consolidado.

**Acceptance Scenarios**:

1. **Given** uma Etapa com barema, **When** a avaliadora conclui com todos os critérios
   respondidos, **Then** a Avaliação guarda o detalhamento e o total calculado, e a Conclusão
   preservada guarda os dois.
2. **Given** um critério em branco, **When** ela salva o rascunho, **Then** grava; **When** ela
   conclui, **Then** a conclusão é recusada nomeando os critérios pendentes.
3. **Given** um critério com pontuação direta e máximo 15, **When** ela informa 16, **Then** a
   conclusão é recusada nomeando o critério e o máximo.
4. **Given** um PDF de títulos que comprova só o Doutorado, ligado também ao Mestrado e à
   Especialização, **When** ela atribui zero aos dois sem justificativa, **Then** a conclusão é
   aceita — zero é resposta, e o arquivo comum não é reivindicação de todos os critérios que ele
   pode comprovar. **When** ela quer registrar por que recusou um título apresentado, **Then**
   escreve na justificativa daquele critério ou no parecer, que o candidato verá.
5. **Given** a Avaliação concluída, **When** a presidência consolida, **Then** o Resultado da Etapa
   recebe o total — o mesmo caminho, a mesma cópia, a mesma regra de nota mínima.

---

### User Story 3 — O candidato sabe como será avaliado e o que recebeu (Priority: P2)

Antes de se inscrever, o candidato lê no PDF a ficha da Prova de Títulos. Ao anexar documentos, vê
junto de "Títulos acadêmicos" que ele comprova Doutorado, Mestrado e Especialização, com o máximo de
cada um. Divulgado o resultado da Etapa, o acompanhamento mostra, sob a nota que já mostra hoje, a
pontuação reconhecida em cada critério e a justificativa, quando houver.

**Why this priority**: é o que o candidato precisa para recorrer com objeto — saber qual parcela
contestar. Depende da US2 para ter o que mostrar.

**Independent Test**: com um Resultado consolidado e publicado sob barema, entrar como o titular e
conferir a tabela; entrar como outro candidato e não vê-la.

**Acceptance Scenarios**:

1. **Given** um Documento Exigido ligado a critérios, **When** o candidato anexa documentos, **Then**
   a linha do documento diz quais critérios ele comprova e até quanto valem.
2. **Given** um Resultado de Etapa com barema visível ao titular, **When** ele abre o acompanhamento,
   **Then** vê critério, máximo, pontuação reconhecida e justificativa.
3. **Given** um Resultado ainda não divulgado, **When** ele abre o acompanhamento, **Then** não vê o
   detalhamento — a regra de visibilidade é a mesma da nota.

---

### User Story 4 — Corrigir a pontuação de um critério por recurso (Priority: P2)

O candidato recorre do Resultado da Prova de Títulos dizendo que a declaração de docência comprova
60 meses, e não 52. Quem julga vê, na tela de julgamento, o detalhamento do Resultado atacado,
decide pela correção fixada e informa o novo detalhamento — só o critério da docência muda, mas ele
já estava no teto, e o total segue 70. Num segundo caso, a Especialização reconhecida passa de 1 para
2 certificados, e o total sobe de 65 para 70: o Resultado sucessor nasce com o detalhamento novo, a
ordem vigente aparece desatualizada como hoje, e a presidência a reemite.

**Why this priority**: sem isto, a correção fixada gravaria um total que não bate com o detalhamento
que o candidato vê — dois números para a mesma parcela.

**Independent Test**: julgar um recurso por correção fixada numa Etapa com barema e conferir o
Resultado sucessor, a decisão e o acompanhamento do titular.

**Acceptance Scenarios**:

1. **Given** um recurso contra Resultado de Etapa com barema, **When** quem julga escolhe correção
   fixada, **Then** informa o detalhamento por critério, e o total é calculado pela mesma função da
   Mesa.
2. **Given** uma correção que reduziria o total, **When** quem julga confirma, **Then** é recusada
   pela vedação de piora que já existe.
3. **Given** a reavaliação determinada, **When** outro avaliador conclui na Mesa, **Then** ele pontua
   pela ficha, e a consolidação produz o sucessor como hoje.

### A jornada inteira

Configurar (US1) → publicar → o candidato comprova (US3) → a comissão pontua (US2) → consolidar,
ordenar e publicar como hoje → o candidato vê o detalhamento (US3) → recorrer e corrigir (US4) →
reemitir a ordem como hoje.

### Edge Cases

- **Etapa sem barema.** Tudo como hoje: o campo único de pontuação na Mesa, a máxima digitada, o
  conteúdo com a lista vazia. Os Editais de sorteio não têm Etapa avaliada e não são tocados.
- **Etapa com barema e mais de uma avaliação por inscrição.** Continua bloqueada na consolidação pela
  regra de combinação ausente, como hoje; o barema não a resolve nem a agrava.
- **Quantidade maior que o necessário.** "52 meses" num critério de 1 ponto por mês até 40 é aceito, e
  a parcela é 40, com a marca "limitado ao máximo" na Mesa e no acompanhamento.
- **Critério sem documento.** Pontuado da mesma forma, e não aparece na lista de documentos do
  candidato.
- **Documento ligado a vários critérios.** Um arquivo só, como hoje; a linha dele lista os critérios
  que comprova. O candidato não envia o mesmo título duas vezes, e o arquivo comum não obriga a
  comissão a justificar cada critério que ele não comprovou.
- **Documento ligado com aplicabilidade restrita** (a um Perfil, a uma modalidade ou a uma condição).
  Recusado na elaboração: o barema vale para toda inscrição da Etapa, e o documento que o comprova
  também precisa valer. Assim não existe candidato a quem se peça pontuar um critério cujo documento
  ele não podia apresentar.
- **Documento não apresentado.** A linha mostra "não apresentado"; zero é a resposta esperada.
- **Retificação do barema depois de conclusões.** A conclusão aberta sob a versão anterior é recusada
  ("o Edital foi retificado enquanto você avaliava"), e a conclusão feita antes não consolida até ser
  reaberta — os dois mecanismos que já existem para a máxima publicada.
- **Retificação de nome, descrição, unidade ou documento ligado.** Também bloqueia a consolidação das
  conclusões anteriores: a descrição é onde mora a condição ("só experiência em EaD"), e o sistema não
  distingue redação de regra. Só a troca de **ordem** não bloqueia.
- **Avaliação reaberta.** O rascunho volta com o detalhamento da conclusão anterior; a conclusão
  anterior fica preservada. Se o barema vigente mudou, a Mesa o mostra pela versão vigente: o valor
  de critério que continua é mantido para reconfirmação, o de critério removido sai, e critério novo
  fica pendente.
- **Leitura depois de Retificação.** Conclusão preservada, Resultado e decisão de recurso mostram
  nome, descrição e máxima **da versão que cada um cita**, e não os da vigente.
- **Conteúdo publicado em versão anterior.** Elevado com a lista vazia: nenhuma Etapa antiga ganha
  barema por elevação.
- **Reaproveitamento de Edital.** Os critérios viajam com a Etapa, com identidades novas, e o
  documento ligado é remapeado para o documento novo correspondente.
- **Remover o Documento Exigido ligado.** O vínculo do critério é desfeito na gravação, e a prévia
  avisa; o critério continua.
- **Soma dos máximos acima do que a coluna comporta** (999,9999). Recusada com frase legível.

## Requirements *(mandatory)*

### Functional Requirements

**Incremento A — o barema na elaboração, na publicação e no PDF**

- **FR-5200**: Uma Etapa de forma pontuada MAY ter um **Barema**: uma lista ordenada de **Critérios de
  Avaliação**. Sem critérios, a Etapa MUST se comportar exatamente como hoje, em todos os canais.
- **FR-5201**: Cada Critério de Avaliação MUST ter identidade estável, ordem, nome (obrigatório, único
  na Etapa), descrição (opcional — onde vão exigências como "na área da Educação" e as observações
  com asterisco dos Editais), pontuação máxima (obrigatória, maior que zero, `decimal(7,4)`), pontos
  por unidade (opcional, maior que zero e não maior que a máxima), nome da unidade (obrigatório quando
  há pontos por unidade, ex.: "certificado", "mês") e documento comprobatório (opcional).
- **FR-5202**: A forma de pontuar MUST ser deduzida dos pontos por unidade, sem campo de tipo:
  **por quantidade**, quando declarados — a parcela é `min(quantidade × pontos por unidade, máxima)`;
  **direta**, quando ausentes — a parcela é o valor atribuído, de zero à máxima. O critério de valor
  fixo ("Doutorado, 20 pontos") é o por quantidade com pontos por unidade igual à máxima.
- **FR-5203**: Com barema, a pontuação máxima da Etapa MUST ser igual à soma das máximas dos
  critérios. A tela MUST calculá-la e mostrá-la no lugar do campo digitável; a validação de
  publicação MUST tratar divergência como erro impeditivo, para o conteúdo que chegue por outro
  caminho.
- **FR-5204**: Barema em Etapa de forma decisória MUST ser erro impeditivo de publicação, e a tela
  MUST não oferecer a seção nessa forma.
- **FR-5205**: O documento comprobatório MUST referenciar um Documento Exigido do mesmo Edital, do
  momento da inscrição, **aplicável a toda inscrição** — sem restrição de Perfil, de modalidade ou de
  condição. Referência a documento inexistente, de outro Edital, da convocação ou de aplicabilidade
  restrita MUST ser recusada na gravação e na validação de publicação, inclusive quando a restrição
  chega depois, pela edição do próprio documento. A aplicabilidade é lida pela função que já a decide
  para o candidato (`aplicaveis`), sem regra paralela.
- **FR-5206**: A etapa Etapas de Avaliação do assistente MUST oferecer, dentro do cartão de cada Etapa
  pontuada, a seção Barema: acrescentar, remover e mover critérios, com os campos de FR-5201 e a
  escolha do documento entre os Documentos Exigidos da inscrição (UX-420).
- **FR-5207**: A seção MUST mostrar uma prévia tabular — critério, pontuação, máxima, comprovação — e
  o total, refletindo o formulário antes de gravar (UX-421).
- **FR-5208**: O barema MUST viajar no conteúdo canônico publicado, como lista `criteria` de cada
  Etapa, num degrau novo de elevação cuja ausência é a lista vazia. Conteúdo publicado em versão
  anterior MUST ser elevado sem critério.
- **FR-5209**: O PDF do Edital MUST imprimir o barema como tabela dentro da descrição da Etapa, nas
  redações que já descrevem a Etapa, pelo compositor existente. Etapa sem barema MUST produzir o mesmo
  texto de antes.
- **FR-5210**: Os critérios MUST ser retificáveis — acrescentar, remover e alterar cada campo — pela
  tela de Retificação existente, como coleção com chave dentro da Etapa. A igualdade de FR-5203 MUST
  valer também para o conteúdo consolidado.
- **FR-5211**: A conferência antes de publicar MUST mostrar o barema de cada Etapa.
- **FR-5212**: O reaproveitamento de Edital MUST copiar os critérios com identidades novas e remapear
  o documento ligado para o documento correspondente do Edital novo.
- **FR-5213**: A API do rascunho MUST aceitar e devolver `criteria` em cada Etapa; Etapa enviada sem a
  chave MUST ser gravada sem critérios.

**Incremento B — a pontuação na Mesa, a consolidação e o candidato**

- **FR-5214**: Na Mesa, para Etapa com barema, o formulário MUST oferecer uma linha por critério no
  lugar do campo único de pontuação: quantidade (por quantidade) ou pontos (direta), uma justificativa
  opcional, a máxima, a comprovação esperada e, quando houver documento ligado, o acesso ao arquivo
  apresentado pelo painel que a Mesa já usa (UX-422).
- **FR-5215**: O total da Avaliação MUST ser calculado pelo servidor como a soma das parcelas, cada
  uma limitada pela sua máxima, em `decimal(7,4)`, independentemente da ordem. O cliente MUST NOT
  enviar o total; um total enviado junto com o detalhamento MUST ser recusado.
- **FR-5216**: A quantidade MUST ser inteiro de zero a 9999; os pontos diretos MUST ter no máximo
  quatro casas, de zero à máxima do critério. Quantidade além da necessária para a máxima MUST ser
  aceita, e a parcela MUST ser mostrada como "limitada ao máximo".
- **FR-5217**: O rascunho MUST aceitar critérios em branco. A conclusão MUST exigir todos respondidos
  — zero é resposta — e a recusa MUST nomear os pendentes.
- **FR-5218**: A justificativa do critério MUST ser opcional, e zero MUST ser resposta válida sem ela:
  o arquivo apresentado não diz quais dos critérios ligados o candidato reivindicou, e exigir
  justificativa por presença de arquivo produziria fundamentação artificial. A fundamentação do
  indeferimento MUST continuar no parecer, sob as regras de obrigatoriedade que já existem sobre o
  total, e a justificativa de critério, quando escrita, MUST chegar ao candidato junto com a parcela.
- **FR-5219**: O detalhamento MUST ser gravado na Avaliação e copiado para a Conclusão preservada, junto
  com a versão que o governou. A imutabilidade da Avaliação concluída, garantida por gatilho, MUST
  cobrir o detalhamento.
- **FR-5220**: Consolidação, classificação, desempate, publicação de resultado e reemissão de ordem
  MUST permanecer inalterados: recebem o total, pelo campo de hoje.
- **FR-5221**: A conferência de compatibilidade entre a norma que governou a conclusão e a vigente MUST
  comparar o barema de forma conservadora: o conjunto dos critérios e, de cada um, nome, descrição,
  máxima, pontos por unidade, unidade e documento ligado. Só a ordem fica de fora. Qualquer outra
  diferença bloqueia a consolidação da conclusão anterior, que se resolve reabrindo e concluindo de
  novo sob o barema vigente.
- **FR-5222**: Reabrir MUST devolver ao rascunho o detalhamento da conclusão reaberta. A Mesa MUST
  mostrá-lo pelo barema vigente: valor de critério que continua é mantido, de critério removido é
  descartado, e critério novo fica pendente. A reavaliação determinada por recurso MUST usar a mesma
  ficha.
- **FR-5223**: As telas que mostram uma avaliação concluída — a Mesa e as conclusões preservadas —
  MUST mostrar o detalhamento.
- **FR-5224**: No portal, a linha de cada Documento Exigido ligado a critérios MUST dizer quais
  critérios ele comprova e as máximas deles.
- **FR-5225**: No acompanhamento do candidato, onde o Resultado da Etapa já é visível hoje, MUST
  aparecer o detalhamento por critério com a justificativa, só ao titular e sob a mesma regra de
  visibilidade da nota (UX-423).
- **FR-5232**: Enquanto o incremento C não estiver entregue, o julgamento por correção fixada de
  recurso contra Resultado de Etapa com barema MUST ser recusado, com frase que oriente a reavaliação
  determinada — que já percorre a ficha. Nenhum Resultado de Etapa com barema MUST nascer com total sem
  detalhamento. O incremento C remove a recusa.
- **FR-5233**: Todo detalhamento MUST ser lido com o barema **da versão que o ato cita** — a da
  Conclusão preservada, a do Resultado, a da Decisão de recurso —, e não com o da versão vigente; nome,
  descrição e máxima mostrados à comissão e ao candidato MUST ser os daquela versão. Só o rascunho se lê
  pela vigente (FR-5222).

**Incremento C — o recurso**

- **FR-5226**: A tela de julgamento de recurso contra Resultado de Etapa com barema MUST mostrar o
  detalhamento do Resultado atacado.
- **FR-5227**: A correção fixada em Etapa com barema MUST ser informada como detalhamento por critério,
  pelo mesmo componente da Mesa; o total MUST ser calculado pela mesma função de FR-5215, e a decisão
  MUST guardar o detalhamento. A vedação de piora MUST continuar aplicada sobre o total.
- **FR-5228**: O detalhamento mostrado ao titular (FR-5225) MUST ser o do Resultado vigente — o da
  decisão, quando o Resultado veio de correção fixada —, com os critérios alterados marcados.

**Transversal**

- **FR-5229**: Nenhuma permissão nova: configurar é de quem elabora e retifica o Edital; pontuar, do
  avaliador atribuído; julgar, de quem julga recurso. A autorização e o isolamento por escopo
  existentes MUST valer sem mudança.
- **FR-5230**: A trilha MUST registrar gravar, concluir, reabrir e julgar pelos eventos que já existem,
  e MUST continuar sem guardar nota ou detalhamento.
- **FR-5231**: Edital sem barema e Edital de sorteio MUST NOT mudar de comportamento: a suíte existente
  MUST passar sem alteração de expectativa além da lista vazia no conteúdo publicado.

### Requisitos de experiência

- **UX-420**: A seção Barema fica dentro do cartão da Etapa, abaixo da pontuação máxima, com a frase
  "Opcional. Sem barema, a comissão lança o total." Com critérios, a máxima vira leitura com "soma
  dos critérios".
- **UX-421**: A prévia tem as colunas da ficha dos Editais — natureza do título, pontuação, máxima,
  comprovação — e a linha de total; não há página nem modal próprio.
- **UX-422**: Na Mesa, a ficha é uma tabela única com o total ao pé, atualizado ao digitar por arquivo
  estático (a CSP recusa script em linha); critério pendente marcado em texto, não só em cor; nenhuma
  navegação além do painel do documento que já existe.
- **UX-423**: No portal, a tabela tem critério, máxima, pontuação reconhecida e justificativa, com
  "limitada ao máximo" em texto quando for o caso.

### Key Entities

- **Critério de Avaliação** — termo da Constituição. Uma linha do barema de uma Etapa: nome,
  descrição, máxima, pontos por unidade e unidade, documento ligado. Pertence à Etapa, e por ela ao
  Edital e ao escopo. Distinto de **Critério de Desempate**, que ordena empatados.
- **Barema** — a lista de Critérios de uma Etapa. Não é entidade: é o nome do conjunto, como os
  Editais o chamam ("ficha de avaliação").
- **Detalhamento** — o que o avaliador afirmou por critério: quantidade ou pontos, parcela,
  justificativa. Vive na Avaliação, na Conclusão preservada e na Decisão de recurso por correção
  fixada; não é entidade com ciclo de vida próprio.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1620**: Cenário 1, títulos — com Doutorado (10), Mestrado (6) e Especialização (3), por
  quantidade e máxima igual ao valor, o barema publicado tem máxima 19; um candidato com mestrado e
  especialização reconhecidos recebe 9; o PDF contém a tabela. O caso vale para o Edital cujos títulos
  se pontuam independentemente; o que exige "só o maior título" não é atendido (P-1).
- **SC-1621**: Cenário 2, experiência — 2 pontos por ano, máxima 10: 3 anos dão 6; 7 anos dão 10,
  "limitada ao máximo"; zero dá zero. Nenhum cálculo de duração é feito pelo sistema.
- **SC-1622**: Cenário 3, avaliação e revisão — a avaliadora conclui com um critério indeferido e a
  justificativa escrita, que o candidato lê junto da parcela; a correção fixada por recurso produz um
  Resultado sucessor com o detalhamento da decisão, a ordem vigente aparece desatualizada, e a ordem
  reemitida usa o total novo.
- **SC-1623**: A reavaliação determinada é cumprida por outro avaliador pela ficha, e a consolidação
  produz o sucessor com o detalhamento novo.
- **SC-1624**: Cenário 4, sem barema — a suíte existente passa; o conteúdo publicado de um Edital de
  sorteio e de um Edital com Etapa sem barema difere do de antes só pela lista vazia; a Mesa de uma
  Etapa sem barema mostra o campo único.
- **SC-1625**: Cenário 5, configuração compartilhada — um Edital com três Perfis e uma Etapa com
  barema aplica a mesma ficha às inscrições dos três, configurada uma vez; reaproveitar o Edital copia
  o barema com identidades novas.
- **SC-1626**: Limites — nenhum total gravado excede a máxima da Etapa; pontos diretos acima da
  máxima do critério são recusados; soma das máximas diferente da máxima da Etapa é recusada na
  publicação.
- **SC-1627**: Avaliação incompleta — o rascunho grava critérios em branco; a conclusão os recusa,
  nomeando cada um.
- **SC-1628**: Retificação do barema depois de conclusões — concluir sob a versão anterior é recusado;
  consolidar conclusão anterior é bloqueado até a reabertura, tanto por mudança de máxima quanto por
  mudança só da descrição; reordenar os critérios não bloqueia.
- **SC-1629**: Determinismo — o mesmo detalhamento, em qualquer ordem, produz o mesmo total com quatro
  casas.
- **SC-1630**: Imutabilidade — alterar o detalhamento de uma Avaliação concluída por SQL direto é
  recusado pelo banco.
- **SC-1631**: Privacidade — o detalhamento aparece só ao titular, e só quando a nota dele já
  apareceria.
- **SC-1632**: Proporção — a comissão do 14/2026 configura o barema numa tela que já existe e pontua
  numa tela que já existe; nenhuma rota, permissão, tabela append-only ou mecanismo de classificação
  novo é criado (contagem verificável no diff do plano).
- **SC-1633**: Reprodutibilidade — depois de uma Retificação que renomeia um critério e muda a
  descrição de outro, a Conclusão preservada, o Resultado e a Decisão de recurso anteriores mostram os
  nomes e as descrições da versão que citam, à comissão e ao candidato; a avaliação reaberta mostra os
  da vigente, com o valor do critério que continuou.
- **SC-1634**: Documento por Perfil — ligar a critério um Documento Exigido restrito a um Perfil, a
  uma modalidade ou a uma condição é recusado, na gravação e na publicação, inclusive quando a
  restrição é acrescentada ao documento depois do vínculo.
- **SC-1635**: Consistência entre B e C — com o incremento B entregue e o C não, a correção fixada
  contra Resultado de Etapa com barema é recusada, e nenhum Resultado de Etapa com barema existe sem
  detalhamento; a reavaliação determinada continua disponível.

## Decisões

As decisões estão com a razão e as alternativas descartadas em [research.md](research.md). O resumo:

- **D-001** — o barema mora na Etapa, e não no Perfil nem numa biblioteca.
- **D-002** — duas formas de pontuar, deduzidas de um campo opcional; nada de tipo, fórmula ou grupo.
- **D-003** — a máxima da Etapa é a soma das máximas dos critérios.
- **D-004** — o detalhamento é JSON na Avaliação, na Conclusão e na Decisão; o total segue no campo
  de hoje.
- **D-005** — o total é calculado no servidor por uma função só, usada pela Mesa e pelo recurso.
- **D-006** — a mudança de barema depois de conclusões é tratada pelos mecanismos de versão e
  compatibilidade que já existem, sem trava nova, e a comparação é conservadora: tudo menos a ordem.
- **D-007** — a comprovação é um vínculo opcional a Documento Exigido; nenhum envio novo.
- **D-008** — a justificativa de critério é opcional; a fundamentação obrigatória continua no
  parecer.
- **D-009** — três incrementos em três PRs; B e C são uma entrega só para produção, e o B recusa a
  correção fixada até o C.
- **D-010** — o documento ligado a critério precisa valer para toda inscrição.
- **D-011** — o detalhamento se lê com o barema da versão que o ato cita.

## Questões para validação institucional

Nenhuma bloqueia o incremento A. A recomendação de cada uma é a que a spec já adota.

- **P-1 — Títulos acumulam?** **Não está demonstrado.** Os quatro Editais não escrevem acumulação
  nem exclusividade, e a soma dos tetos dar 100 é compatível com as duas leituras — um teto total é
  só um teto. A spec trata cada critério como independente, e por isso atende só o Edital cuja ficha
  se pontua assim (tabela em "O que esta spec atende"). A exclusividade não é construída sem regra
  validada; Edital que a exija continua lançando o total. **Confirmar, Edital a Edital, com a
  CPS/Cefor, antes de operar um deles pelo barema.**
- **P-2 — Quando a justificativa é obrigatória?** A spec não a torna obrigatória por critério: sem a
  expectativa do candidato (P-4), o sistema não distingue "não reivindicou" de "reivindicou e foi
  recusado". A obrigatoriedade continua sendo a do parecer, que já existe. Se a CPS/Cefor quiser
  fundamentação por critério em todo indeferimento, o caminho é coletar a reivindicação, e isso é P-4.
- **P-3 — O detalhamento é público?** A spec o mostra só ao titular. A lista pública continua com o
  total.
- **P-4 — Autopontuação vinculante.** O 173/2025 proíbe pontuar acima da expectativa declarada pelo
  candidato. **Fora**: pede coleta na inscrição e regra de teto por candidato; o candidato continua
  entregando a ficha preenchida como documento, e a comissão a respeita.
- **P-5 — Barema por Perfil.** O 140/2025 varia o teto do Doutorado por curso (25 ou 20). **Fora**:
  depende de a Etapa poder variar por Perfil, que é a decisão de alcance da Etapa ainda pendente
  (`doc/decisoes-pendentes-da-consolidacao.md`, DP-10). Até lá, um Edital assim publica um barema por
  Edital separado ou mantém o lançamento do total.
- **P-6 — Desempate por critério.** O 14/2026 desempata por "mais experiência em EaD (em meses)", que
  é um critério do barema. **Fora** (lacuna L-3): o detalhamento em JSON não fecha a porta, mas o
  desempate continua lendo a nota da Etapa ou um fato declarado.
- **P-7 — Mais de um avaliador por inscrição.** Continua bloqueado pela regra de combinação ausente,
  com ou sem barema.

## Assumptions

- A forma de ficha dos quatro Editais da amostra — linha, valor por unidade, teto — é a dos próximos
  processos de títulos do Cefor; se os títulos se pontuam independentemente é questão de cada Edital
  (P-1). Ficha de entrevista por faixas ("Fracos 0 a 5, Bons 6 a 10") é
  atendida pela pontuação direta, com as faixas na descrição.
- O candidato junta num PDF os títulos de cada Documento Exigido, como os Editais já pedem ("arquivo
  único"); um arquivo por documento continua sendo a regra.
- Contar meses, frações e vínculos concomitantes é juízo da comissão, que informa a quantidade.

## Fora do escopo

- Motor de regras, fórmula, DSL, editor visual, grupos de critérios, exclusividade, pesos internos.
- Biblioteca institucional ou modelo reutilizável de barema; versionamento próprio do barema.
- Autopontuação do candidato e coleta de expectativa (P-4); barema por Perfil (P-5); desempate por
  critério (P-6); combinação de avaliadores (P-7).
- Distribuição automática, dupla avaliação, avaliação cega.
- Cálculo de duração a partir de datas; leitura do conteúdo dos documentos.
- Painel analítico; acompanhamento por critério (a Distribuição continua medindo por inscrição).
- Seleção de critério contestado no formulário de recurso: o candidato o nomeia no texto, e quem
  julga vê o detalhamento.
