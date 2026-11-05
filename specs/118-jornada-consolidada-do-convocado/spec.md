# Feature Specification: A jornada consolidada do candidato convocado

**Feature Branch**: `claude/sweet-blackwell-dc658d`, sobre a `main` em `fb0e1ddc`

**Created**: 2026-11-04 · **Revista**: 2026-11-04, com a revisão do PR #376

**Status**: Draft, **só documental**. Nenhum código, migration, rota ou tela foi alterado. As
decisões têm três origens:

- **Do usuário, em 04/11/2026, sobre o diagnóstico do PR vitofranzosi/processo_seletivo#375:**
  D-001 a D-006. Não se reabrem.
- **Propostas de desenho desta spec:** D-007 a D-014, e D-015 a D-018, que vieram da revisão do PR
  em 04/11/2026. **Arquitetura e escopo aprovados pelo usuário em 04/11/2026**, no encerramento da
  spec.
- **Do usuário, no encerramento da spec (04/11/2026):** D-019, a exceção informativa do Requerimento
  não enviado sem documento.
- **Do usuário, depois do merge (04/11/2026):** D-020, o Processo em estado final fecha o
  Requerimento *na convocação*.
- **Do usuário, na revisão da implementação (PR #384, 04/11/2026):** D-021, o acompanhamento sem
  documento pode pagar uma consulta a mais; a SC-1128 foi revista.
- **Revisões de requisitos de outras specs** (`063`, `115`, `059`, `029`): estão escritas por
  extenso em *Revisões de requisitos anteriores*. Elas se aplicam aos arquivos daquelas specs na
  **primeira tarefa da implementação** (T001), com a redação anterior preservada, como a `117` fez
  com a FR-069 da `009` (D-011).

**Input**: a revisão de UX da jornada do convocado,
[`doc/revisao-ux-jornada-do-convocado-2026-11-04/README.md`](../../doc/revisao-ux-jornada-do-convocado-2026-11-04/README.md),
com as capturas, as maquetes e o roteiro de captura dos cenários A–K. Ela está no PR #375 (branch
`claude/hopeful-feistel-13dbd9`), lida integralmente em `9cedcc6b` e **mergeada em 04/11/2026**
(`b512e70a`). Ela partiu do achado do PR #374 (`doc/achado-jornada-do-candidato-na-convocacao.md`),
encerrado no mesmo dia como superado por ela; a branch dele fica como referência.

O relatório é **evidência**, e não implementação obrigatória: as maquetes mostram uma forma possível,
e o que esta spec exige é o que está nos requisitos.

> **Faixa de identificadores.** Esta spec abre em **FR-3721** e **SC-1117**. O teto foi medido em
> 04/11/2026 em `specs/` de todas as branches locais e remotas e de todas as worktrees desta máquina
> (26): o requisito funcional três mil setecentos e vinte e o critério mil cento e dezesseis, os dois
> da emenda da `116`. A pasta `118` não existe em nenhuma delas. **Nenhum `UX-` é aberto aqui.** As
> decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-1175 da `063`"). Uma decisão de outra feature é citada pelo assunto e pela feature,
> nunca pelo número. As falhas do relatório (`F1` a `F12`), os ajustes (`B1`, `R3`, `X1`…) e as
> questões institucionais (`QI-7`) são citados como estão nos documentos de origem.

---

## Por que esta feature existe

**A `115` ensinou o portal a pedir documentos na convocação, mas o resto do portal não ficou
sabendo.** A lista em si é clara: um cartão por documento, a instrução do Edital, o motivo da
pendência e o reenvio já aberto. O problema está em volta dela.

- **A falsa conclusão (F1).** Quando o Edital pede o Requerimento de Matrícula e documentos, o
  acompanhamento diz *"Seu Requerimento de Matrícula foi enviado."*, com o botão verde para
  conferi-lo, enquanto quatro documentos obrigatórios estão em *"Falta enviar"* (cenário C2). A ação
  principal só conhece três possibilidades (FR-1175 da `063`), e nenhuma delas é "documento".
- **A lista continua pedindo depois do desfecho (F2).** *"Envie até…"*, *"aguardando conferência"* e
  *"Falta enviar"* seguem na tela quando a comissão já não confere (FR-3588 da `115`) e o candidato
  já não envia (cenário I2).
- **"Atendido" antes da conferência.** *"Atendido pelo documento enviado na inscrição"* aparece com o
  item ainda à espera da comissão (cenário D). É a mesma falsa conclusão, num item só.
- **O prazo é um instante, dito de seis formas (F4)**, com três formatos de data e hora e três
  redações para o vencido. A tela do Requerimento não o mostra.
- **O Requerimento não enviado some depois do vencimento (F3).** Nenhuma tela diz que ele não foi
  enviado, e quem abre o endereço dele cai numa recusa técnica.

Polish solto não resolve: a FR-1175 da `063`, a FR-3612 da `115` e a FR-1096/FR-1097 da `059` fixam
os textos e o caminho de hoje, e testes os prendem. Mudá-los sem spec seria contrariar requisito
escrito.

**O objetivo.** Alguém que não conhece o GPS abre o portal e responde, sem ajuda:

1. *Preciso enviar mais alguma coisa?*
2. *O que está com a comissão?*
3. *Qual é o prazo?*
4. *O que acontece depois?*

### O que esta spec cobre, e o que fica fora

Cobre, numa entrega só (D-001):

- **A.** uma projeção das obrigações da convocação, derivada do que já existe, sem nada gravado;
- **B.** a ação do acompanhamento, que passa a representar o conjunto;
- **C.** a ordem da tela da convocação, com o que fazer agora no topo;
- **D.** a linguagem dos estados, do prazo e do desfecho, num formato só;
- **E.** a página do Requerimento: o caminho de volta, o prazo e o vencido;
- **F.** os seis ajustes de polish do relatório (§9): destaque da pendência, "Envie o arquivo" sem
  envio anterior, "Voltar à convocação", o texto "se você for convocado", nomes acessíveis e o fim
  do "Envie até…" depois do desfecho.

**Fica fora:**

- **Segunda tela, wizard, painel, estado persistente, migration, endpoint ou notificação** (D-002).
- **Qualquer regra de convocação, de conferência ou de prazo.** Nenhum desfecho, prazo ou recusa
  muda (FR-3756).
- **A gestão.** A FR-3591, a FR-3607 e a FR-3610 da `115` ficam como estão (FR-3758).
- **"Minhas inscrições".** A nota de pendência na lista (X1) pede leitura em lote e medida de custo
  da FR-1092 da `059`; fica registrada para decisão (FR-3759, D-012).
- **O aviso de pendência (QI-7).** É decisão institucional. A recomendação está em *Registrado, sem
  desenvolver*.
- **A mensagem de convocação da `019`** (X3) e a variante da sucessora.
- **A correção da convocação por sucessão pela gestão** (X4). A verificação desta spec confirmou a
  lacuna, e ela está registrada à parte como achado operacional:
  [`doc/achado-correcao-da-convocacao-pela-gestao-2026-11-04.md`](../../doc/achado-correcao-da-convocacao-pela-gestao-2026-11-04.md).
- **O teste com candidatos reais** (X5). É do produto, e diria mais do que qualquer leitura de quem
  revisa.

### Vocabulário fixo

Os três termos da `115` continuam com uma fonte só, e o portal não usa nenhum deles como promessa:

| Termo | Onde vive | No portal |
|---|---|---|
| **Apto para formalização** | a gestão, pelo desfecho que inclui na ocupação (FR-3610 da `115`) | **não aparece**: para o candidato é jargão e soaria como promessa (D-014) |
| **Encaminhado** | registro de entrega, que nenhuma spec do portal cria | não aparece |
| **Matrícula efetivada, bolsa concedida, contrato celebrado** | o setor do vínculo, fora do GPS | não aparece; o aceite diz que **não** é isso (FR-3750) |

E três limites do desenho: o GPS não é GED; nada acontece por vencimento ou por pendência; a
comissão confere e decide. Não há máquina de estados nova.

## Clarifications

### Session 2026-11-04

Decisões do usuário, trazidas no pedido, que não se reabrem:

- Q: O diagnóstico do PR #375 está aprovado? → A: Sim (D-003).
- Q: Spec e polish em entregas separadas? → A: Não. Uma entrega só, com os seis ajustes do §9 do
  relatório. PR de polish separado, só com impedimento técnico demonstrado (D-001).
- Q: Cabe tela nova, wizard, painel, estado gravado, migration, endpoint ou notificação? → A: Não
  (D-002).
- Q: O botão que leva à lista pode dizer "Enviar os N documentos que faltam", como na maquete? → A:
  Não. Botão que só navega não diz "Enviar…". Algo como *"Ver e corrigir os documentos pendentes"*
  (D-004).
- Q: A frase de conclusão pode ser *"Você enviou tudo o que esta convocação pede pelo portal"*? → A:
  Não. O documento aproveitado não foi reenviado, e a frase apagaria a diferença. Algo como *"Você
  não tem mais documentos para enviar agora. A comissão ainda vai concluir a análise."* (D-005).
- Q: O vocabulário muda? → A: Não. "Apto para formalização" ≠ "encaminhado" ≠ vínculo efetivado; o
  GPS não é GED; nada automático; a comissão confere e decide; nenhuma máquina de estados nova
  (D-006).

### Session 2026-11-04 (revisão do PR #376)

Uma revisão do PR apontou cinco contradições e dois excessos do plano. O usuário mandou aplicá-los
("Sim, aplique"). Cada um tem decisão e teste (tabela *Ajustes da revisão*, no plano):

- Q: Os opcionais somem quando não há tarefa? → A: Não. O bloco 3 existe também só com opcionais, e
  o facultativo tem classificação própria em cada estado (D-018; FR-3722, FR-3735, FR-3738).
- Q: O Processo em estado final é "o prazo terminou"? → A: Não. A causa do fechamento é derivada, e
  cada causa tem o seu texto; com o Processo, nada promete conferência (D-015; FR-3741, FR-3748).
- Q: "Indisponível agora" é "não pedido"? → A: Não. A exigência e a situação vêm antes da
  disponibilidade (D-016; FR-3725).
- Q: O prazo não iniciado vale também nos cartões e no opcional? → A: Sim, e prevalece (FR-3749).
- Q: Sem documento e com o Requerimento enviado, qual é a ação? → A: A de hoje (D-017; FR-3732).
- Q: A FR-3756 proíbe mudar as views? → A: Não. Proíbe escrita, rota, comando e regra novos; as
  views passam a ler a projeção, com titularidade, recusas e resposta privada iguais (FR-3756).

### Session 2026-11-04 (encerramento da spec)

- Q: Num Edital só com Requerimento, o não enviado depois do prazo ou do desfecho aparece no
  acompanhamento e na convocação? → A: Sim, como linha estritamente informativa, sem ação, sem
  consulta nova, e só quando a política já não admite o preenchimento; B e B2 continuam como hoje
  (D-019).
- Q: O Requerimento preenchível com o Processo encerrado se resolve aqui? → A: Não. É encaminhamento
  separado, de alta prioridade, sem mudar a regra durante a `118`
  (`doc/encaminhamento-requerimento-com-processo-encerrado-2026-11-04.md`).
- Q: (depois do merge) O Requerimento *na convocação* deixa de aceitar escrita com o Processo
  encerrado ou cancelado? → A: Sim, preservando a leitura (D-020). A `029` foi revista; a `118` foi
  ajustada na FR-3725, na FR-3730, na FR-3732, na FR-3741, na FR-3748 e na FR-3754.

### Session 2026-11-04 (revisão da implementação, PR #384)

- Q: Em G0, N0 e M0, o acompanhamento pode pagar a consulta à lista da chamada, que é como ele sabe
  que ela não pede documento? → A: Sim, no máximo uma em relação à linha de base; a convocação não
  pode aumentar a sua contagem, e sem convocação nada muda (D-021; SC-1128 revista).

## User Scenarios & Testing *(mandatory)*

Os cenários são os do relatório, com a mesma letra. Todos são percorridos pelo portal, num navegador
de verdade, a 375 px e em desktop, sem banco nem shell para ver a tela.

### User Story 1 — Quem tem documentos e Requerimento sabe que ainda falta (Priority: P1)

O Edital pede o Requerimento de Matrícula e quatro documentos na convocação. A convocada preenche e
envia o Requerimento primeiro (cenário C2). Ao voltar ao acompanhamento, ela lê que ainda faltam
quatro documentos, e o botão principal a leva à convocação, e não ao Requerimento. O Requerimento
enviado aparece numa linha secundária, com o caminho para conferi-lo.

**Why this priority**: é a falha que pesa (F1). A pessoa tem motivo para achar que terminou, e o
prazo passa com os documentos sem envio.

**Independent Test**: montar o cenário C2 pelas fixtures da `115` e abrir o acompanhamento e a
convocação. Nenhuma das duas telas diz que algo foi concluído, e as duas dizem quantos documentos
faltam.

**Acceptance Scenarios**:

1. **Given** documentos e Requerimento na chamada e nada enviado (C1), **When** a convocada abre o
   acompanhamento, **Then** a ação diz o que falta, com os documentos e o Requerimento, e o link
   principal leva à convocação.
2. **Given** o Requerimento enviado e quatro obrigatórios sem envio (C2), **When** ela abre o
   acompanhamento, **Then** a ação diz que faltam quatro documentos, o link principal leva à
   convocação, e *"✓ Requerimento de Matrícula enviado."* aparece como linha secundária, com o link
   para conferi-lo.
3. **Given** o mesmo C2, **When** ela abre a convocação, **Then** o primeiro bloco diz o que fazer
   agora, lista os quatro documentos com âncora para cada um e o prazo, numa primeira tela a 375 px.
4. **Given** o Requerimento é a única obrigação e a chamada não pede documento (B), **When** ela abre
   o acompanhamento, **Then** a ação e o link continuam os de hoje: *"Preencher o Requerimento de
   Matrícula."*, direto à tela dele.
5. **Given** o Requerimento já enviado e a chamada sem documento (B2), **When** ela abre o
   acompanhamento, **Then** a ação principal continua a de hoje, *"Seu Requerimento de Matrícula foi
   enviado."*, com o link para conferi-lo.

---

### User Story 2 — A pendência salta aos olhos, e o motivo vem junto (Priority: P1)

A comissão marcou o histórico como pendente. A convocada abre o acompanhamento e lê que precisa
corrigir um documento (cenário F). Na convocação, o topo diz qual, com o motivo, e leva ao cartão. O
cartão pendente tem destaque visual e um selo em texto, distinto de *"Falta enviar"*.

**Why this priority**: a pendência é o único estado em que a comissão espera algo da pessoa, e hoje
ela tem o mesmo cartão neutro e o mesmo marcador de *"Falta enviar"* (F5).

**Independent Test**: cenários F e J. O cartão pendente se distingue sem cor (selo em texto) e com
cor; a pendência sem envio anterior diz *"Envie o arquivo"*, e não *"outro"*.

**Acceptance Scenarios**:

1. **Given** um obrigatório pendente e um a enviar, com o prazo em curso (F), **When** a convocada
   abre o acompanhamento, **Then** a ação diz que ela precisa corrigir um documento e enviar outro,
   e o link diz *"Ver e corrigir os documentos pendentes"*.
2. **Given** o mesmo F, **When** ela abre a convocação, **Then** o item pendente vem primeiro na lista
   do topo, com o motivo, e o cartão dele tem o selo *"Precisa de correção"*.
3. **Given** uma pendência registrada sobre item que nunca recebeu arquivo (J), **When** ela lê o
   cartão, **Then** ele diz *"Envie o arquivo até…"*, e não *"Envie outro arquivo"* nem *"um novo
   arquivo"*.
4. **Given** um leitor de tela, **When** ela navega pelos formulários, **Then** cada botão de escolher
   e de enviar diz o nome do documento.

---

### User Story 3 — O que está com a comissão não parece tarefa, e o aproveitado não parece pronto (Priority: P1)

A candidata enviou o certificado na inscrição, e o Edital o aproveita na convocação (cenário D).
Outros três documentos foram enviados pelo portal e esperam conferência (E). Ela lê que não precisa
enviar nada agora e que a comissão ainda vai conferir. O certificado aparece como *"Você já enviou
este documento na inscrição"*, com o selo *"Aguardando conferência"*, e não como *"atendido"*.

**Why this priority**: as duas leituras erradas são simétricas. Em E, *"Siga as instruções do
Edital"* induzia uma ação inexistente; em D, *"Atendido"* dava por concluído o que a comissão nem
abriu.

**Independent Test**: cenários D, E e H. Nenhuma tela diz "atendido", "aprovado", "aceito" ou "tudo
enviado" antes do desfecho; nenhuma frase diz que a pessoa reenviou o aproveitado.

**Acceptance Scenarios**:

1. **Given** o item aproveitado da inscrição, sem conferência (D), **When** a convocada abre a
   convocação, **Then** o item diz que ela já o enviou na inscrição, na data, que não precisa enviar
   de novo e que a comissão vai conferir.
2. **Given** todos os obrigatórios recebidos ou aproveitados, sem conferência (E), **When** ela abre o
   acompanhamento, **Then** a ação é *"Nada por enquanto."*, seguida de *"Você não tem mais documentos
   para enviar agora. A comissão ainda vai concluir a análise."*
3. **Given** todos os obrigatórios *conformes* e o Requerimento enviado, sem desfecho (H), **When** ela
   abre as duas telas, **Then** a frase é a mesma da cena anterior, e nenhum item diz "Conforme"
   sozinho: diz *"Conferido: de acordo com o Edital."*
4. **Given** o item aproveitado e conferido, **When** ela o lê, **Then** o texto diz que é o arquivo
   enviado na inscrição, e não que ela o reenviou.
5. **Given** só um documento facultativo sem envio, e nenhuma tarefa (L), **When** ela abre a
   convocação, **Then** o bloco *Documentos opcionais* aparece com o envio, a frase de conclusão vale,
   e o opcional não entra em contagem nenhuma.

---

### User Story 4 — Depois do prazo, e depois do resultado, a tela só conta o que houve (Priority: P1)

O prazo da chamada terminou sem desfecho (cenário G). A convocada lê, numa frase só e igual em toda
parte, quando o prazo terminou, que não dá mais para enviar pelo portal, que o fim do prazo não
decide nada sozinho e que quem registra o resultado é a comissão. Ela vê o que ficou sem envio,
inclusive o Requerimento. Mais tarde, a comissão registra o resultado (I1, I2), e a página vira
histórico: o que foi enviado, o que não foi, e o que não foi conferido antes do resultado.

**Why this priority**: é onde a tela convida a um ato que não existe (F2) ou omite o que não foi
feito (F3).

**Independent Test**: cenários G, I1 e I2. Zero formulários, zero *"Envie até"*, zero *"Falta
enviar"* e zero *"aguardando conferência"* depois do desfecho; o Requerimento não enviado aparece no
resumo do vencido; o endereço do Requerimento não cai na recusa técnica.

**Acceptance Scenarios**:

1. **Given** o vencimento decorrido sem desfecho e o Requerimento não enviado (G), **When** a
   convocada abre a convocação, **Then** o topo diz *"O prazo terminou"*, com a frase única, e o
   resumo *"Até o prazo, ficou assim"* inclui o Requerimento não enviado, sem botão de enviar.
2. **Given** o mesmo G, **When** ela abre o endereço do Requerimento, **Then** a página diz *"O prazo
   terminou"*, com a mesma frase e *"Voltar à convocação"*, e nenhum rascunho é criado.
3. **Given** o indeferimento registrado com itens não enviados e um recebido sem conferência (I2),
   **When** ela abre a convocação, **Then** o topo diz o resultado registrado, e a lista *"O que você
   enviou nesta convocação"* diz *"Não enviado"* e *"Enviado em DD/MM/AAAA; não foi conferido antes
   do resultado"*.
4. **Given** o aceite registrado (I1), **When** ela abre o acompanhamento e a convocação, **Then** as
   duas dizem *"Vaga aceita"* e a frase de que o registro não é matrícula, bolsa nem contrato.
5. **Given** o Processo encerrado com a chamada em aberto e o prazo ainda correndo (M), **When** ela
   abre a convocação, **Then** o topo diz *"O envio pelo portal está encerrado"*, sem dizer que o
   prazo venceu e sem prometer conferência, e nenhum formulário de documento aparece.
6. **Given** o indeferimento registrado e o Requerimento pedido na convocação e nunca enviado (N),
   **When** ela abre a convocação, **Then** a página diz *"Requerimento de Matrícula: não enviado."*,
   e não o omite.

---

### User Story 5 — O prazo é um só, e se lê do mesmo jeito em toda parte (Priority: P2)

O prazo aparece no acompanhamento, na convocação, nos cartões e no Requerimento, sempre no formato
*"até 09/11/2026, às 13h27"*. Com a comunicação ainda não enviada (cenário K), nenhuma tela mostra a
data como prazo: a tela diz que o prazo ainda não começou a correr e que a pessoa já pode enviar.

**Why this priority**: o instante já é o mesmo em toda parte, pela mesma regra da `019`; falta dizê-lo
de um jeito só (F4, F12).

**Independent Test**: em cada cenário, coletar o texto de todas as ocorrências do prazo nas três
telas e no Requerimento. O formato é um só; a frase do vencido tem um núcleo só.

**Acceptance Scenarios**:

1. **Given** o prazo em curso, **When** a convocada abre as quatro telas, **Then** o prazo aparece no
   mesmo formato em todas, e a tela do Requerimento o mostra.
2. **Given** a comunicação não enviada (K), **When** ela abre a convocação, **Then** a tela diz que o
   prazo ainda não começou e que ela já pode enviar, e o vencimento registrado só aparece entre os
   dados da convocação, dito como dado do ato.
3. **Given** a comunicação não enviada, com um item pendente e um opcional (K2), **When** ela lê os
   cartões, **Then** nenhum deles diz *"até ‹data›"*.

---

### Edge Cases

Cada caso aponta o requisito que o rege. Os casos com letra são cenários da validação (plano).

- **Chamada sem documento e sem Requerimento.** A ação continua *"Siga as instruções do Edital para
  esta convocação."*, e a tela da convocação mantém a estrutura de hoje (FR-3732, FR-3743).
- **Chamada com Requerimento e sem documento, a preencher (B).** O caminho direto ao Requerimento
  continua (FR-3732).
- **Chamada com Requerimento e sem documento, já enviado (B2).** A ação principal continua *"Seu
  Requerimento de Matrícula foi enviado."*, como hoje; a linha secundária da FR-3731 só existe com
  documento (FR-3732, D-017).
- **Requerimento coletado na inscrição.** Ele está *enviado* desde a inscrição: com documento na
  chamada, aparece como linha secundária com *conferir e atualizar*; nunca como obrigação da
  convocação (FR-3725, FR-3731).
- **Requerimento pedido na convocação, nunca enviado, depois do desfecho, com documento na chamada
  (N).** A política o diz "ainda indisponível", mas a projeção o mostra como *não enviado*, e não
  como *não pedido* (FR-3725, linha 3; FR-3742). A página do Requerimento diz que ele não foi enviado,
  e não *"Ainda não é a hora"* (FR-3754).
- **O mesmo, sem documento na chamada (N0).** A página do Requerimento é a da FR-3754, haja ou não
  documento. O acompanhamento e a convocação mantêm a ação de hoje e acrescentam só a linha
  informativa *"Requerimento de Matrícula: não enviado."*, sem link (FR-3732, FR-3743, D-019).
- **Requerimento pedido na convocação, não enviado, prazo decorrido, sem documento (G0).** A ação
  continua a de hoje, com a linha *"Requerimento de Matrícula: não enviado até o prazo. Não é mais
  possível enviá-lo pelo portal."*, sem link, com e sem rascunho (FR-3732, FR-3743, D-019).
- **Requerimento com rascunho e prazo decorrido.** *Não enviado até o prazo*; o rascunho continua
  legível, como a `029` já garante (FR-3725, linha 4).
- **Só facultativos sem envio, com a chamada aberta (L).** Não há tarefa: a frase de conclusão vale,
  com a linha do opcional, e o bloco 3 aparece como *Documentos opcionais*, com o envio (FR-3723,
  FR-3728, FR-3735, FR-3738).
- **Facultativo pendente.** Mostra o motivo, como opcional, com o envio enquanto a chamada estiver
  aberta, e não entra na contagem do que falta (FR-3723, FR-3746).
- **Facultativo recebido.** Fica com a comissão, com o selo *"Opcional"* (FR-3722, FR-3739).
- **Obrigatório *não se aplica* por conferência.** Fica entre os conferidos, com o motivo; não é
  tarefa (FR-3722).
- **Item complementado.** Fica com a comissão, com o texto do novo arquivo (FR-3722, FR-3746).
- **Item aproveitado da chamada anterior.** Fica com a comissão; nunca dito como reenviado (FR-3724).
- **Convocação corrigida por sucessão.** A projeção lê a lista da chamada e o prazo da vigente, como a
  `115` (FR-3721).
- **Convocação sem vencimento.** Não há prazo a mostrar; *"até ‹prazo›"* sai das frases, e a escrita
  continua aberta enquanto a chamada estiver em aberto (FR-3737, FR-3746).
- **Prazo não iniciado com pendência, tarefa e opcional (K2).** Nenhum cartão, opcional ou frase de
  conclusão mostra a data como prazo (FR-3749).
- **Processo em estado final com chamada em aberto (M).** A escrita de documentos está fechada pelo
  Processo, e não pelo prazo: o topo diz *"O envio pelo portal está encerrado"*, sem dizer que o prazo
  venceu e sem prometer conferência; os itens com a comissão dizem que não foram conferidos antes do
  encerramento (FR-3741, FR-3746). O Requerimento *na convocação* não enviado aparece como não
  enviado, sem link (FR-3725, linha 3a; D-020).
- **Processo em estado final, sem documento na chamada, Requerimento não enviado (M0).** A linha
  informativa da FR-3732, sem o chamado *"Preencher"* (D-020).
- **Processo em estado final e Requerimento enviado.** Continua *enviado*, legível, com o link de
  conferir (FR-3725, linha 2; FR-3731). *Conferir e atualizar* segue a política da `029`: fechado
  para o *na convocação* pela FR-408 revista; para o *na inscrição*, decisão pendente.
- **Processo em estado final e vencimento decorrido, juntos.** Vale o Processo (FR-3721).
- **Pendência registrada depois do vencimento.** Aparece como *"Precisava de correção"*, sem convite a
  enviar (FR-3746).
- **Conferência que chega enquanto a pessoa está na página.** A tela mostra o que leu ao abrir; a
  recusa do envio já é a da `115` (FR-3756).
- **Desfecho que não inclui (indeferimento, não atendimento, desistência, inércia, reclassificação).**
  Rótulo de `DESFECHOS`, fundamento e data; a frase do aceite não aparece (FR-3750).
- **Regularização registrada.** Recebe a frase do aceite, porque também inclui na ocupação (FR-3750).
- **Inscrição sem convocação.** Nenhuma consulta nova e nenhum elemento novo (FR-3734).
- **Inscrição alheia ou inexistente.** A mesma recusa de hoje, nas três telas (FR-3756).

## Requirements *(mandatory)*

### Functional Requirements

#### A. A projeção das obrigações

- **FR-3721**: As obrigações da convocação vigente MUST ser uma **projeção derivada**, sem
  armazenamento, calculada num único lugar fora do template, e a mesma que os testes consultam (molde
  da FR-1167 da `063`). Ela MUST receber, já derivados pelas views:
  - a leitura documental da chamada: os itens pedidos, com a situação (obrigatório ou facultativo)
    e o estado da FR-3590 da `115`, e de onde veio a apresentação vigente (portal, inscrição ou
    chamada anterior);
  - as três leituras do Requerimento de Matrícula da FR-3725, todas da política da `029` que a tela
    dele consulta (FR-1099 da `059`);
  - o estado do prazo, pela leitura da `019` (`estado_de`: prazo não iniciado, em curso, vencimento
    decorrido ou desfechado), e o vencimento registrado — *sem vencimento* é `vencimento` vazio, e não
    um estado de `estado_de`;
  - a **causa** do fechamento da escrita de documentos, quando ela estiver fechada, pela mesma
    condição que recusa o envio (FR-3578 e FR-3582 da `115`): *vencimento decorrido* ou *Processo em
    estado final* (encerrado ou cancelado). Com as duas, vale o Processo, porque com ele ninguém
    confere nem desfecha;
  - o desfecho vigente, quando houver.
  
  Ela MUST NOT ler relógio, consultar o banco, gravar nada nem contar o prazo de novo. A causa é
  derivada a cada leitura, e não gravada. A lista e o prazo são os da chamada, inclusive na
  convocação corrigida por sucessão.
- **FR-3722**: A projeção MUST situar a chamada num **momento**, pela primeira linha que se aplicar:

  | Momento | Quando |
  |---|---|
  | *decidida* | há desfecho vigente |
  | *encerrada pelo Processo* | sem desfecho, com o Processo em estado final |
  | *encerrada pelo prazo* | sem desfecho, com o vencimento decorrido |
  | *aberta* | os demais casos, inclusive o prazo não iniciado e a convocação sem vencimento |

  E MUST pôr cada item pedido em **exatamente uma** categoria, primeiro pela situação e depois pelo
  estado:

  | Estado do item (FR-3590 da `115`) | Obrigatório | Facultativo |
  |---|---|---|
  | *a apresentar* | **a enviar** | opcional |
  | *pendente*, com apresentação anterior | **a corrigir** | opcional |
  | *pendente*, sem apresentação | **a enviar**, com o motivo | opcional |
  | *recebido*, pelo portal ou por aproveitamento | com a comissão | com a comissão, marcado como opcional |
  | *complementado* | com a comissão | com a comissão, marcado como opcional |
  | *conforme* ou *não se aplica* | conferido | conferido |

  A categoria não muda com o momento. O que muda é o texto (FR-3746) e se há convite: **só com a
  chamada aberta** as categorias em negrito são tarefas e o opcional pode ser enviado.
- **FR-3723**: O **facultativo** MUST NOT contar como pendência, nem entrar no total do que falta,
  nem impedir a frase de conclusão (FR-3728). A pendência registrada num facultativo MUST mostrar o
  motivo e dizer que o documento é opcional. Com a chamada aberta, o opcional a enviar MUST
  continuar alcançável para envio, **haja ou não tarefa** (FR-3735, FR-3738).
- **FR-3724**: O que está **com a comissão** MUST NOT ser apresentado como tarefa do candidato. O
  item aproveitado MUST NOT ser dito como reenviado pela pessoa, nem como atendido, conferido ou
  aceito antes da conferência *conforme*. Com a chamada encerrada pelo Processo, nenhuma frase MUST
  prometer conferência ou resultado futuros.
- **FR-3725**: O Requerimento de Matrícula MUST entrar na projeção a partir de **três leituras
  separadas**, todas já existentes na política da `029`:
  - a **exigência**: o momento declarado pelo Edital (*na inscrição*, *na convocação* ou nenhum);
  - a **situação**: enviado ou não enviado (com ou sem rascunho);
  - a **disponibilidade atual**: se a política admite preencher agora.

  O estado na projeção MUST ser o da primeira linha que se aplicar. **A exigência e a situação vêm
  antes da disponibilidade**: depois do desfecho, a política diz "ainda indisponível" a quem nunca
  enviou, e isso não pode apagar que ele foi pedido.

  | # | Quando | Estado | É tarefa? |
  |---|---|---|---|
  | 1 | o Edital não declara Requerimento | *não pedido* | não |
  | 2 | enviado, na inscrição ou na convocação | *enviado* | não |
  | 3 | declarado (em qualquer momento), não enviado, com desfecho vigente | *não enviado* | não |
  | 3a | declarado *na convocação*, não enviado, com a chamada *encerrada pelo Processo* | *não enviado, envio encerrado* | não |
  | 4 | declarado, não enviado, com o prazo da chamada decorrido pela política (`prazo_decorrido`) | *não enviado até o prazo* | não |
  | 5 | a política o diz disponível ou em preenchimento, sem prazo decorrido, e a chamada não está *encerrada pelo Processo* | *a preencher* | **sim** |
  | 6 | os demais casos | *sem chamado* | não |

  As linhas 3 e 4 leem o desfecho e o prazo **da política do Requerimento**. A linha 3a lê a causa do
  fechamento da FR-3721 e aplica a FR-373 da `029`, revista em 04/11/2026 por decisão do usuário
  (D-020): com o Processo encerrado ou cancelado, o Requerimento *na convocação* não aceita mais
  escrita. Ela vem antes da linha 4, como nos documentos: com o Processo em estado final e o prazo
  decorrido juntos, vale o Processo (D-015). A linha 3a não alcança o Requerimento *na inscrição*,
  cuja regra não muda. A linha 6 é a proteção contra um chamado que o comando recusaria (FR-1098 da
  `059`). Esta spec não implementa a revisão da `029`, que é PR próprio: até ele, o comando ainda
  aceita a escrita que a tela já não oferece.
- **FR-3726**: A ordem do que o candidato precisa fazer MUST ser: primeiro o que tem pendência
  registrada — *a corrigir* e *a enviar* com motivo —, depois *a enviar*, depois o Requerimento *a
  preencher*; dentro de cada grupo, a ordem do Edital. A precedência da
  FR-3591 da `115`, que põe *para conferir* antes de *com pendência*, serve a quem confere, e MUST
  NOT ser usada para o candidato.
- **FR-3727**: A projeção MUST oferecer os totais por categoria — a corrigir, a enviar, com a
  comissão, conferidos — contando só obrigatórios, e se o Requerimento é tarefa.
- **FR-3728**: Com a chamada *aberta*, documentos pedidos e nenhuma tarefa, a projeção MUST oferecer
  a **frase de conclusão**: *"Você não tem mais documentos para enviar agora. A comissão ainda vai
  concluir a análise."* Havendo opcional sem envio, MUST seguir-se *"Se quiser, você ainda pode
  enviar o documento opcional até ‹prazo›."*; com o prazo não iniciado ou sem vencimento, sem
  *"até ‹prazo›"* (FR-3749). Nenhuma frase MUST dizer que a pessoa enviou tudo, que está tudo certo,
  aceito, aprovado ou concluído.
- **FR-3729**: A projeção MUST NOT produzir decisão. Ela MUST NOT inferir desfecho, perda de vaga,
  nova chamada, prazo novo nem prazo de complementação; o fim do prazo e o estado final do Processo
  só fecham a escrita (FR-3593 e FR-3618 da `115`).

#### B. O acompanhamento

- **FR-3730**: Quando a chamada vigente pede documento, a ação do bloco *"O que fazer"* MUST vir da
  projeção, pela primeira linha que se aplicar:

  | # | Quando | Ação principal | Link principal |
  |---|---|---|---|
  | 1 | chamada *decidida* | *"Nada por enquanto."* (FR-1178 da `063`) | *"Ver o que você enviou nesta convocação"* → convocação |
  | 2 | chamada *encerrada pelo Processo* | a frase do Processo (FR-3741) e, quando houver, *"Até o encerramento do Processo, ficaram sem envio: ‹lista curta›."* | *"Ver como ficou a convocação"* → convocação |
  | 3 | chamada *encerrada pelo prazo* | a frase do vencido (FR-3748) e, quando houver, *"Até o prazo, ficaram sem envio: ‹lista curta›."* | *"Ver como ficou a convocação"* → convocação |
  | 4 | chamada *aberta*, com tarefa | *"Você ainda precisa ‹tarefas›."*, com as tarefas na ordem da FR-3726 (por exemplo, *"Você ainda precisa corrigir 1 documento, enviar 2 documentos e preencher o Requerimento de Matrícula."*) | com algo *a corrigir*: *"Ver e corrigir os documentos pendentes"*; sem: *"Ver o que falta na convocação"* → convocação |
  | 5 | chamada *aberta*, sem tarefa | *"Nada por enquanto."*, seguida da frase de conclusão (FR-3728) | *"Ver a convocação"* → convocação |

  O link principal MUST levar à tela da convocação em todas as linhas, **mesmo com o Requerimento
  enviado ou a preencher**. Nenhum rótulo de link que só navega MUST começar por "Enviar" (D-004).
  O prazo, o aviso de prazo não iniciado e a consequência continuam vindo da FR-1176 e da FR-1177 da
  `063`, revistas. Na linha 2, o Requerimento *na convocação* não enviado entra no que ficou sem
  envio, sem link (FR-3725, linha 3a).
- **FR-3731**: Com documento pedido na chamada e o Requerimento *enviado*, aberta ou não a chamada, o
  bloco *"O que fazer"* MUST mostrar a linha secundária *"✓ Requerimento de Matrícula enviado."*, com o
  link *"Conferir o Requerimento de Matrícula enviado"* (FR-1097 da `059`), abaixo da ação principal e
  nunca no lugar dela.
- **FR-3732**: Quando a chamada **não** pede documento, a ação MUST ser **exatamente a de hoje**:
  - Requerimento a preencher: *"Preencher o Requerimento de Matrícula."*, com o link direto a ele;
  - Requerimento enviado: *"Seu Requerimento de Matrícula foi enviado."* como ação principal, com
    *"Conferir o Requerimento de Matrícula enviado"* — não há outra obrigação no portal que ele
    esconda (D-017);
  - sem Requerimento: *"Siga as instruções do Edital para esta convocação."*, com *"Ver convocação"*;
  - com desfecho: *"Nada por enquanto."*, com o link de conferir quando houver Requerimento enviado.
  
  Mudam só os textos comuns a todas as telas: o formato do prazo, a frase do vencido, o rótulo do
  desfecho e a frase do aceite (FR-3747 a FR-3750).

  **Exceção estritamente informativa** (D-019). Com o Requerimento declarado *na convocação* e não
  enviado, rascunho incluído, o bloco *"O que fazer"* MUST acrescentar, abaixo da ação principal, que
  continua a de hoje:
  - com o prazo da chamada decorrido pela política (FR-3725, linha 4) e sem desfecho: *"Requerimento
    de Matrícula: não enviado até o prazo. Não é mais possível enviá-lo pelo portal."*;
  - com desfecho vigente (FR-3725, linha 3): *"Requerimento de Matrícula: não enviado."*, como
    histórico;
  - com o Processo em estado final (FR-3725, linha 3a; D-020): *"Requerimento de Matrícula: não
    enviado. O envio pelo portal está encerrado."*, e o chamado *"Preencher"* não aparece.
  
  A linha MUST NOT ter link nem botão de preenchimento, e MUST NOT aparecer enquanto a política
  admitir o preenchimento e a chamada não estiver encerrada pelo Processo: com a chamada aberta, B e
  B2 ficam exatamente como hoje. No Processo em estado final, sem o chamado, a ação principal é a de
  hoje para quem não tem Requerimento a preencher (*"Siga as instruções do Edital para esta
  convocação."*). Ela sai da mesma
  `Disponibilidade` que o chamado ao Requerimento já lê (momento, situação, prazo decorrido) e do
  desfecho que a tela já lê, **sem consulta nova**, e não muda disponibilidade, prazo, desfecho nem
  autorização.
- **FR-3733**: Com a chamada *encerrada*, por qualquer das duas causas, o acompanhamento MUST mostrar
  o que ficou sem envio — documentos obrigatórios e, encerrada pelo prazo, o Requerimento *não enviado
  até o prazo* — e MUST NOT oferecer link, botão ou frase que convide a enviar documento. O
  Requerimento segue a FR-3725.
- **FR-3734**: Ler a projeção MUST NOT acrescentar consulta ao acompanhamento de inscrição sem
  convocação vigente. Com convocação, MUST acrescentar um número fixo de consultas, o mesmo com um
  ou com muitos itens (molde da leitura em lote da `115`). A projeção, sozinha, roda sem consulta.

#### C. A tela da convocação

- **FR-3735**: Com documento pedido na chamada, a tela da convocação MUST ter cinco blocos, nesta
  ordem, cada um com título de segundo nível:
  1. **O que fazer agora** (FR-3736);
  2. **Prazo** (FR-3737);
  3. **O que falta** — documentos e Requerimento; sem tarefa, **Documentos opcionais** (FR-3738);
  4. **O que você já apresentou** — com a comissão e conferidos (FR-3739);
  5. **Sobre esta convocação** — fundamentos e metadados (FR-3740).

  Os blocos 3 e 4 MUST NOT aparecer vazios. O bloco 3 aparece, com a chamada aberta, quando houver
  tarefa **ou** opcional a enviar; sem nenhum dos dois, ele some, e o bloco 1 diz por quê.
  O opcional MUST NOT ficar inalcançável por falta de tarefa (FR-3723).
- **FR-3736**: O bloco **O que fazer agora** MUST trazer:
  - a frase de estado: a mesma ação principal do acompanhamento (FR-3730, linhas 4 e 5);
  - a lista das tarefas na ordem da FR-3726, cada uma com âncora para o cartão dela — e, no
    Requerimento, o link *"Preencher o Requerimento de Matrícula"*; no item com pendência registrada
    (*a corrigir* ou *a enviar* com motivo), o motivo;
  - com documento a corrigir ou a enviar, **um** botão de navegação ao primeiro cartão da lista, com
    rótulo que diga o que se vê ao chegar: *"Ver e corrigir os documentos pendentes"* ou *"Ver os
    documentos que faltam"*. MUST NOT começar por "Enviar" (D-004);
  - a linha *"Com a comissão: N documento(s)."* quando houver, sem verbo de tarefa;
  - sem tarefa e com opcional, a linha *"Há documento opcional que você pode enviar, se quiser."*,
    com âncora para o bloco 3.
- **FR-3737**: O bloco **Prazo** MUST dizer o prazo único da FR-3747; com o prazo correndo, a frase de
  consequência da FR-1177 da `063`, na mesma condição; com o prazo não iniciado, só a frase da
  FR-3749, sem data; sem vencimento, que esta convocação não tem prazo registrado.
- **FR-3738**: O bloco **O que falta** MUST conter os cartões das tarefas, na ordem da FR-3726, com o
  envio de arquivo da `115` e o cartão do Requerimento *a preencher*. Os opcionais a enviar
  — *a apresentar* ou *pendentes* — MUST vir no fim do bloco, sob o título de terceiro nível
  *"Opcional"*, com o mesmo envio, fora de qualquer contagem. Sem tarefa, o bloco tem só eles.
- **FR-3739**: O bloco **O que você já apresentou** MUST conter, na ordem do Edital, os cartões com
  a comissão (o facultativo com o selo *"Opcional"*), depois os conferidos, e a linha do Requerimento
  *enviado* (FR-3731). O cartão com a comissão MUST oferecer *"Enviar outro arquivo"* recolhido, como
  a `115` já oferece, enquanto a chamada estiver aberta.
- **FR-3740**: O bloco **Sobre esta convocação** MUST continuar visível, sem `details`: espécie,
  chamada, comunicação enviada em, vencimento registrado, fundamento e atendimento. É o ato que a
  pessoa tem direito de ler; ele só desce de posição.
- **FR-3741**: Com a chamada *encerrada*, nenhum formulário de envio de documento MUST aparecer, e os
  blocos 3 e 4 viram leitura, com os textos da coluna da causa na FR-3746. O bloco 1 MUST depender
  da causa:
  - **pelo prazo**: título *"O prazo terminou"*, a frase da FR-3748 e o resumo *"Até o prazo, ficou
    assim"*, que inclui o Requerimento *não enviado até o prazo*;
  - **pelo Processo**: título *"O envio pelo portal está encerrado"*, com *"Este Processo Seletivo
    foi ‹encerrado / cancelado›, e não é mais possível enviar documentos pelo portal. Se você enviou
    algo que não aparece aqui, fale com o atendimento: ‹canal›."* e o resumo *"Até o encerramento do
    Processo, ficou assim"*. Esta frase MUST NOT dizer que um prazo venceu, nem que a comissão vai
    conferir ou decidir. O Requerimento *na convocação* não enviado entra no resumo como *"Requerimento
    de Matrícula: não enviado. O envio pelo portal está encerrado."*, sem link (FR-3725, linha 3a;
    D-020). Nenhum bloco oferece o preenchimento. A frase de abertura passa a *"…e não é mais
    possível enviar documentos nem o Requerimento de Matrícula pelo portal"* quando a chamada pede os
    dois.
- **FR-3742**: Com desfecho vigente, a página MUST ser **só histórico**:
  - o bloco 1 se chama *"Resultado registrado"*, com o rótulo da FR-3750, o fundamento e a data;
  - os blocos 3 e 4 dão lugar a um só, *"O que você enviou nesta convocação"*, na ordem do Edital,
    com os textos da coluna *decidida* da FR-3746;
  - MUST NOT aparecer formulário, *"Envie até…"*, *"Falta enviar"*, *"aguardando conferência"* nem
    convite a corrigir;
  - o Requerimento enviado continua com o link de conferir (FR-1097 da `059`); o pedido e não
    enviado aparece como *"Requerimento de Matrícula: não enviado."* (FR-3725, linha 3).
- **FR-3743**: Sem documento pedido na chamada, a tela da convocação MUST manter a estrutura de hoje
  (FR-3574 da `115`): os dados, *"O que fazer"* e o chamado ao Requerimento. Mudam só o formato do
  prazo, a frase do vencido, o rótulo do desfecho — *"Resultado registrado: ‹rótulo da FR-3750›"*, no
  lugar de *"Situação registrada: ‹espécie›"* — e a frase do aceite (FR-3747 a FR-3750). A exceção
  informativa da FR-3732 vale também aqui, com as mesmas frases, no lugar onde hoje fica o chamado ao
  Requerimento, e com as mesmas condições.
- **FR-3744**: O cartão com pendência registrada — *a corrigir*, ou *a enviar* com motivo (cenário J)
  — MUST ter destaque visual de aviso (borda e fundo) **e** o selo em texto *"Precisa de correção"*.
  O cartão com a comissão MUST ter o selo *"Aguardando conferência"*; o conferido, *"Conferido"*; o
  facultativo, também *"Opcional"*. O estado MUST NOT ser dito só por cor ou símbolo, e o marcador do
  cartão MUST NOT lembrar um botão de opção. O estilo mora na folha do portal, porque a política de
  conteúdo recusa estilo no template.
- **FR-3745**: Cada cartão MUST ter título de terceiro nível com o nome do documento. O botão de
  escolher arquivo e o de enviar MUST ter nome acessível com o nome do documento (por exemplo,
  *"Enviar: Certidão de nascimento ou casamento"*), por texto visualmente oculto, e a descrição
  acessível do campo MUST incluir a situação do item, além do limite do arquivo. A ordem do Tab
  MUST seguir a ordem visual, com foco visível em todo controle e nas âncoras.

#### D. A linguagem

- **FR-3746**: Os textos de cada item MUST ser estes, em linguagem simples (a da `069`), com o mesmo
  sentido jurídico da `115`. ‹data› é DD/MM/AAAA; ‹hora› é HHhMM; *"até ‹prazo›"* é o da FR-3747.

  | Item | Aberta | Encerrada pelo prazo | Encerrada pelo Processo | Decidida |
  |---|---|---|---|---|
  | obrigatório *a apresentar* | *"Falta enviar."* | *"Não enviado até o prazo."* | *"Não enviado."* | *"Não enviado."* |
  | *pendente*, com apresentação anterior | *"Precisa de correção: ‹motivo›. Envie um novo arquivo até ‹prazo›."* | *"Precisava de correção: ‹motivo›. Nenhum novo arquivo foi enviado até o prazo."* | *"Precisava de correção: ‹motivo›."* | *"Precisava de correção: ‹motivo›."* |
  | *pendente*, sem apresentação | *"Precisa de correção: ‹motivo›. Envie o arquivo até ‹prazo›."* | *"Precisava de correção: ‹motivo›. Nenhum arquivo foi enviado até o prazo."* | *"Precisava de correção: ‹motivo›."* | *"Precisava de correção: ‹motivo›."* |
  | *recebido* (pelo portal) | *"Recebido em ‹data›, às ‹hora›. A comissão vai conferir; você não precisa fazer nada agora."* | *"Recebido em ‹data›, às ‹hora›. A comissão vai conferir."* | *"Recebido em ‹data›, às ‹hora›; não foi conferido antes do encerramento do Processo."* | *"Enviado em ‹data›; não foi conferido antes do resultado."* |
  | aproveitado da inscrição, sem conferência | *"Você já enviou este documento na inscrição, em ‹data›. Não precisa enviar de novo. A comissão vai conferir."* | *"Enviado na inscrição, em ‹data›. A comissão vai conferir."* | *"Enviado na inscrição, em ‹data›; não foi conferido antes do encerramento do Processo."* | *"Enviado na inscrição, em ‹data›; não foi conferido antes do resultado."* |
  | aproveitado da chamada anterior, sem conferência | *"Aproveitado da chamada anterior, enviado em ‹data›. Não precisa enviar de novo. A comissão vai conferir de novo."* | *"Aproveitado da chamada anterior, enviado em ‹data›. A comissão vai conferir de novo."* | *"Aproveitado da chamada anterior, enviado em ‹data›; não foi conferido antes do encerramento do Processo."* | *"Aproveitado da chamada anterior, enviado em ‹data›; não foi conferido antes do resultado."* |
  | *complementado* | *"Novo arquivo recebido em ‹data›, às ‹hora›, depois da correção pedida. A comissão vai conferir."* | idem à coluna *aberta* | *"Novo arquivo recebido em ‹data›; não foi conferido antes do encerramento do Processo."* | *"Novo arquivo enviado em ‹data›; não foi conferido antes do resultado."* |
  | *conforme* | *"Conferido: de acordo com o Edital."* | idem | idem | idem |
  | *conforme*, aproveitado | *"Conferido: de acordo com o Edital. É o arquivo enviado na inscrição, em ‹data›."* (ou *"…na chamada anterior, em ‹data›."*) | idem | idem | idem |
  | *não se aplica* | *"Não se aplica: ‹motivo›."* | idem | idem | idem |
  | facultativo *a apresentar* | *"Opcional: envie se quiser."* | *"Opcional, não enviado."* | *"Opcional, não enviado."* | *"Opcional, não enviado."* |
  | facultativo *pendente* | *"Opcional. A comissão apontou: ‹motivo›. Se quiser, envie um novo arquivo até ‹prazo›."* (sem apresentação: *"…envie o arquivo até ‹prazo›."*) | *"Opcional. A comissão apontou: ‹motivo›."* | idem | idem |

  O facultativo recebido, aproveitado, complementado ou conferido usa a linha do estado dele, com o
  selo *"Opcional"* (FR-3744). **O prazo não iniciado e a convocação sem vencimento prevalecem sobre
  esta tabela**: neles, *"até ‹prazo›"* sai de toda frase da coluna *aberta* (FR-3749). O motivo é o
  de quem conferiu, sem o nome de quem conferiu (FR-3584 da `115`). *"Conferido: de acordo com o
  Edital"* significa conforme ao exigido, nunca autêntico (FR-3589 da `115`).
- **FR-3747**: O prazo MUST ter **um** formato em todas as telas do candidato sobre a convocação — o
  acompanhamento, a convocação, os cartões e o Requerimento: *"até DD/MM/AAAA, às HHhMM"* (por
  exemplo, *"até 09/11/2026, às 13h27"*). O rótulo é *"Prazo desta convocação"* (FR-1176 da `063`).
  *"Contado do envio da comunicação"* só aparece no bloco *Sobre esta convocação*, junto do
  vencimento registrado.
- **FR-3748**: A frase do vencido MUST ter um **núcleo** só, usado em todas as telas **e** nas
  recusas de envio de documento e de Requerimento por prazo (FR-3622 da `115`): *"O prazo terminou
  em DD/MM/AAAA, às HHhMM. O fim do prazo não decide nada sozinho: quem registra o resultado é a
  comissão."* Nas telas, o núcleo MUST ser seguido, quando couber, de *"Não é mais possível enviar
  ‹documentos / o Requerimento de Matrícula / documentos nem o Requerimento de Matrícula› pelo
  portal."* e de *"Se você enviou algo que não aparece aqui, fale com o atendimento: ‹canal›."* O
  núcleo MUST ser usado **só** com o vencimento decorrido e sem o Processo em estado final, para os
  documentos e para o Requerimento (FR-3725, linhas 3a e 4; D-015, D-020). Nunca sem vencimento
  registrado. Nenhuma frase MUST afirmar perda (FR-274 da `019`).
- **FR-3749**: Com a comunicação ainda não enviada, as telas MUST dizer *"O prazo ainda não começou a
  correr: ele conta a partir do envio da comunicação."*, seguido de *"Você já pode enviar."* **só**
  quando a escrita estiver aberta e houver tarefa ou opcional a enviar. Esta regra **prevalece** sobre
  toda menção ao prazo: a data do vencimento MUST NOT aparecer como prazo em nenhum bloco, cartão,
  opcional ou frase de conclusão; ela fica só no bloco *Sobre esta convocação*.
- **FR-3750**: O desfecho MUST ter, na tela da convocação e no acompanhamento, o mesmo rótulo: o da
  tabela da FR-1172 da `063` (por exemplo, *"Vaga aceita"*). Com aceite ou regularização, as duas
  telas MUST dizer *"Este registro não é matrícula, bolsa nem contrato: ele registra o resultado desta
  convocação. Os próximos passos são os que o Edital indica."* É a frase que a User Story 2 da `115`
  prometia, e que não existia em tela nenhuma.
- **FR-3751**: Nenhum texto desta feature MUST dizer *"apto para formalização"*, *"encaminhado"*,
  *"matriculado"*, *"matrícula efetivada"*, *"bolsa concedida"*, *"vinculado"*, *"contratado"*,
  *"autêntico"*, *"aprovado"*, *"atendido"* ou *"aceito"* sobre documento, nem *"você enviou tudo"*.
  As varreduras de vocabulário da `115` e da `063` MUST alcançar os arquivos novos.

#### E. O Requerimento de Matrícula

- **FR-3752**: A página do Requerimento *enviado*, com convocação vigente, MUST oferecer *"Voltar à
  convocação"*. A explicação do estado MUST depender da convocação:
  - sem convocação vigente: a de hoje (*"Enviado não é alterado. Se algo mudar e você for convocado,
    esta página oferece a atualização."*);
  - com a atualização admitida pela política (FR-410 da `029`): *"Enviado não é alterado. Se algo
    mudou, a atualização cria uma nova versão, e esta continua registrada."*;
  - com a atualização não admitida (prazo decorrido ou desfecho): *"Enviado não é alterado."*
- **FR-3753**: Com o Requerimento declarado *na convocação* e o preenchimento admitido pela política,
  a página dele MUST mostrar o prazo da FR-3747, ou, com o prazo não iniciado, a frase da FR-3749.
- **FR-3754**: Aberto o endereço do Requerimento com o **prazo da chamada decorrido** e **nenhum**
  requerimento vigente — o caso em que a política recusa abrir o rascunho —, a página MUST mostrar o
  estado *"O prazo terminou"*, com a frase da FR-3748 e *"Voltar à convocação"*, e MUST NOT mostrar a
  recusa genérica. Nenhum rascunho MUST ser criado: a regra de disponibilidade não muda (FR-374 da
  `029`), só a resposta da leitura.
  
  Pelo mesmo motivo, aberto o endereço do Requerimento declarado *na convocação*, não enviado, com
  **desfecho vigente** na convocação, a página MUST NOT dizer *"Ainda não é a hora"* nem *"quando você
  for convocado"*, que são falsos para quem foi convocado. Ela MUST dizer *"Requerimento de Matrícula
  não enviado"*, com *"Esta convocação já tem resultado registrado, e o Requerimento não foi enviado.
  Não é mais possível enviá-lo pelo portal."* e *"Voltar à convocação"*. O rascunho, se houver,
  continua como a FR-411 da `029` o deixa. *"Ainda não é a hora"* continua só para quem não tem
  convocação (cenário N, com e sem rascunho).

  E, com o Requerimento *na convocação* não enviado e a chamada *encerrada pelo Processo* (FR-3725,
  linha 3a), a página MUST dizer *"O envio pelo portal está encerrado"*, com *"Este Processo Seletivo
  foi ‹encerrado / cancelado›, e não é mais possível enviar o Requerimento de Matrícula pelo portal."*
  e *"Voltar à convocação"*, sem formulário, e o GET MUST NOT criar rascunho. O rascunho que houver
  continua legível (FR-373 da `029`, revista; D-020).
- **FR-3755**: Enviado o Requerimento numa chamada que pede documento, o aviso do envio MUST ser
  *"Requerimento de Matrícula enviado. Veja na convocação se ainda falta algum documento."*, com
  *"Voltar à convocação"* na mesma página. Sem documento, o aviso continua o de hoje.

#### F. Limites

- **FR-3756**: Esta feature MUST NOT criar tabela, coluna, migration, rota, endpoint, comando,
  estado gravado, tela, passo, painel ou envio de mensagem, nem mudar regra de convocação, de
  conferência, de prazo, de disponibilidade do Requerimento ou de autorização. As views do
  acompanhamento, da convocação e do Requerimento **podem** passar a ler e entregar a projeção, a
  responder a FR-3754 e a fazer a leitura da FR-3755. Nesses caminhos:
  - nenhuma requisição de leitura MUST gravar nada além do que já grava hoje (a leitura da
    convocação na trilha, FR-3613 da `115`), e o GET da FR-3754 MUST NOT criar rascunho;
  - a titularidade, a recusa indistinguível de inexistente (FR-1101 da `059`; FR-399 da `029`) e a
    resposta privada da página do Requerimento MUST continuar as mesmas.
- **FR-3757**: A FR-3614 da `115` continua: apresentação, conferência e pendência não disparam
  mensagem, e a FR-084 da `010` continua com quatro situações.
- **FR-3758**: A gestão MUST NOT mudar: o estado documental da FR-3591, a condução da FR-3607 e o
  *"Apto para formalização"* da FR-3610, todos da `115`, ficam como estão.
- **FR-3759**: "Minhas inscrições" MUST NOT mudar, e MUST NOT ler documentos da convocação: a ação
  continua *"Ver convocação"* (FR-1090 da `059`, revista), e o custo continua o da FR-1092 da `059`.

### Key Entities

- **Obrigações da convocação** (projeção nova, sem persistência): para a chamada vigente de uma
  inscrição, o momento (*aberta*, *encerrada pelo prazo*, *encerrada pelo Processo*, *decidida*) e a causa do fechamento, as tarefas em ordem, os itens com a
  comissão, os conferidos, os opcionais, o estado do Requerimento, os totais e as frases. Nasce das
  entradas da FR-3721 e morre com a requisição.
- **Leitura documental, estado do prazo, desfecho e política do Requerimento** (existem, não mudam):
  as fontes da projeção.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1117**: Nos cenários A–K, com documento pedido na chamada, o link principal do acompanhamento
  leva à tela da convocação em 100% dos casos, e nenhuma obrigação de documento fica sem menção no
  acompanhamento quando o Requerimento foi enviado (C2, F, H).
- **SC-1118**: Zero falsas conclusões: em nenhum cenário com tarefa a frase de conclusão ou o
  Requerimento enviado aparece como ação principal; em nenhum cenário anterior ao *conforme* aparece
  "atendido"; em nenhum cenário aparece frase de que a pessoa enviou ou reenviou tudo.
- **SC-1119**: A 375 × 812 px, nos cenários A, C1, C2, F e J, o bloco *O que fazer agora*, com a
  contagem e o primeiro link de tarefa, termina dentro da primeira tela; o cartão a corrigir se
  distingue por um selo em texto, verificável sem cor.
- **SC-1120**: Nos cenários I1 e I2, a tela da convocação tem zero formulários e zero ocorrências de
  *"Envie até"*, *"Falta enviar"*, *"aguardando conferência"* e *"Envie um novo arquivo"*.
- **SC-1121**: Em cada cenário, todas as ocorrências do prazo no acompanhamento, na convocação, nos
  cartões e no Requerimento têm o mesmo formato; no G, a frase do vencido tem o mesmo núcleo nas
  telas e nas recusas; no K, nenhuma tela mostra a data como prazo.
- **SC-1122**: Pelo teclado, a 375 px, a ordem do Tab segue a ordem visual, todo controle tem foco
  visível, e nenhum nome acessível de botão de envio ou de escolha de arquivo se repete na mesma
  página. Nenhuma tela tem rolagem horizontal, e o console não registra violação da política de
  conteúdo.
- **SC-1123**: Nos cenários B e B2 e num Edital sem documento e sem Requerimento, a estrutura das três
  telas e a ação principal do acompanhamento são as de hoje — inclusive *"Seu Requerimento de
  Matrícula foi enviado."* em B2 —, e os testes da `059` e da `063` sobre esses casos passam editando
  só as expectativas de texto comum nomeadas no plano (formato do prazo, frase do vencido, rótulo do
  desfecho, frase do aceite). Nenhum deles mostra a linha informativa da FR-3732.
- **SC-1124**: Para cada cenário A–K, a verificação registra, citando o texto literal da tela, a
  resposta às quatro perguntas: *preciso enviar mais alguma coisa?*, *o que está com a comissão?*,
  *qual é o prazo?* e *o que acontece depois?*. Nenhuma fica sem resposta, e nenhuma resposta
  contradiz outra tela do mesmo cenário.
- **SC-1125**: O acompanhamento de inscrição sem convocação tem o mesmo número de consultas de antes;
  com convocação, o número é o mesmo com um e com seis itens pedidos.
- **SC-1126**: O teste da projeção cobre 100% das combinações de estado do item × situação
  (obrigatório, facultativo) × momento (os quatro da FR-3722) × estado do Requerimento, e
  cada combinação cai em exatamente uma categoria.
- **SC-1127**: Nos cenários de controle L, M, N e K2, todos com documento na chamada: em L, o opcional se envia sem nenhuma tarefa
  pendente; em M, nenhuma tela diz que o prazo venceu nem promete conferência; em N, o Requerimento
  pedido e não enviado aparece como *não enviado* depois do desfecho, na convocação e na página dele;
  em K2, nenhuma data aparece como
  prazo. Em todos, nenhuma requisição de leitura grava linha nova além da leitura da convocação na
  trilha, e a inscrição alheia recebe a mesma recusa de inexistente.
- **SC-1128** *(revisado pela `118` em 2026-11-04, na revisão da implementação — a redação anterior
  está ao fim desta alínea)*: Nos cenários G0, N0 e M0 — chamada sem documento, Requerimento pedido
  na convocação e não enviado, com e sem rascunho —, o acompanhamento e a convocação mostram a linha
  informativa da FR-3732, sem nenhum link ou botão de preenchimento, com a ação principal de hoje
  (em M0, a de quem não tem Requerimento a preencher); e nenhuma linha é gravada. Quanto às
  consultas, em relação à linha de base:
  - o acompanhamento acrescenta **no máximo uma** — a leitura da lista da chamada (D-021);
  - a convocação **não aumenta** a sua contagem;
  - sem convocação, o acompanhamento continua com a mesma contagem;
  - com convocação, o custo das duas telas continua independente da quantidade de documentos
    (FR-3734).

  > **Redação anterior, preservada:** "Nos cenários G0, N0 e M0 — chamada sem documento,
  > Requerimento pedido na convocação e não enviado, com e sem rascunho —, o acompanhamento e a
  > convocação mostram a linha informativa da FR-3732, sem nenhum link ou botão de preenchimento,
  > com a ação principal de hoje (em M0, a de quem não tem Requerimento a preencher); o número de
  > consultas das duas telas é o mesmo de antes; e nenhuma linha é gravada."
  >
  > *Por que mudou:* a redação anterior contradizia a FR-3734, que admite número fixo de consultas
  > com convocação. Para saber que a chamada não pede documento, o acompanhamento lê a lista gravada
  > nela (D-021).

## Assumptions

- A `115` está na `main` (#368, #369), e a leitura documental, as views do portal e a política do
  Requerimento são as de `fb0e1ddc`.
- O PR #375, mergeado em 04/11/2026, é a evidência; o roteiro de captura dele
  (`doc/revisao-ux-jornada-do-convocado-2026-11-04/roteiro-de-captura.py`) serve à validação.
- O volume é o da `115`: dezenas de convocados por chamada e poucos documentos por pessoa.
- Ninguém de fora do projeto leu estas telas. A validação desta spec é a leitura de quem implementa
  e os testes; o teste com candidatos reais (X5) continua recomendado e fora daqui.

## Proteção de dados (LGPD)

Nada novo é coletado, guardado ou enviado. O motivo da pendência continua só no portal, atrás da
autenticação (FR-3584 da `115`), e não vai a e-mail, log ou trilha. Nenhum endereço novo carrega dado
pessoal (FR-1102 da `059`). Ler a projeção não registra leitura além da que a tela da convocação já
registra (FR-3613 da `115`).

## Revisões de requisitos anteriores

As redações abaixo se aplicam aos arquivos das specs revistas na T001, com a marca *"revisada pela
`118` em ‹data›"* e a redação anterior preservada ao fim da alínea, como a FR-084 da `010` faz.
Nenhuma muda regra de convocação, de conferência ou de prazo: mudam o que a tela diz e para onde o
botão leva.

### `063` — acompanhamento pela situação

**FR-1175, nova redação.** A ação DEVE vir do Edital ou do ato: o recurso, quando houver objeto
recorrível com prazo aberto (com data e hora de encerramento); e, na convocação vigente:

- com documento pedido na chamada, a tabela da FR-3730 da `118`, que lê as obrigações da convocação
  (documentos e Requerimento de Matrícula) e leva à tela da convocação;
- sem documento, como antes: o Requerimento de Matrícula, quando a política da `029` disser que ele
  está disponível, em preenchimento ou enviado; e, sem Requerimento, "siga as instruções do Edital
  para esta convocação" (FR-3732 da `118`).

Com documento pedido na chamada, o Requerimento enviado é linha secundária, com o caminho para
conferi-lo (FR-3731 da `118`).

> *Redação anterior:* "A ação DEVE vir do Edital ou do ato: o Requerimento de Matrícula, quando a
> política da `029` disser que ele está disponível, em preenchimento ou enviado; o recurso, quando
> houver objeto recorrível com prazo aberto (com data e hora de encerramento); e, na convocação sem
> Requerimento, 'siga as instruções do Edital para esta convocação'."
>
> *Por que mudou:* a `115` passou a pedir documentos na convocação, e com o Requerimento enviado a
> ação dizia "enviado" com documentos obrigatórios sem envio (F1 da revisão de 04/11/2026).

**FR-1176, nova redação.** O prazo da convocação DEVE ser o vencimento registrado nela, chamado
"prazo desta convocação", no formato da FR-3747 da `118`. Sem comunicação enviada com sucesso, a tela
DEVE dizer que o prazo não começou, pela frase da FR-3749 da `118`, sem mostrar a data como prazo.
Com vencimento decorrido sem desfecho, a situação DEVE continuar "Convocado", e a tela DEVE dizer, pela
frase da FR-3748 da `118`, a data em que o prazo terminou e que quem registra o resultado é a
comissão, sem afirmar perda (FR-274).

> *Redação anterior:* "O prazo da convocação DEVE ser o vencimento registrado nela, com data e hora,
> e DEVE ser chamado 'prazo desta convocação'. Sem comunicação enviada com sucesso, a tela DEVE dizer
> que o prazo não começou. Com vencimento decorrido sem desfecho, a situação DEVE continuar
> 'Convocado', e a tela DEVE dizer a data em que o prazo terminou e que o resultado da convocação
> ainda não foi registrado, sem afirmar perda (FR-274)."
>
> *Por que mudou:* o mesmo instante era dito em três formatos e em três redações do vencido (F4).

**FR-1177, acréscimo ao fim.** As frases que dizem quem age e que o fim do prazo não decide nada
sozinho — *"A comissão ainda vai concluir a análise."*, *"quem registra o resultado é a comissão"* —
não são frases de consequência: elas negam a consequência automática, e não a preveem. A segunda
frase neutra pode aparecer também na tela da convocação, na mesma condição (FR-3737 da `118`). As
duas continuam sendo as únicas que falam de consequência.

> *Redação anterior:* a mesma, sem este acréscimo.

**FR-1178, nova redação.** "Nada por enquanto" DEVE ser a ação quando nenhum ato pede algo da pessoa.
Na convocação com documento pedido e nada a fazer, ela DEVE vir seguida da frase de conclusão da
FR-3728 da `118`, que diz que a comissão ainda vai concluir a análise.

> *Redação anterior:* "'Nada por enquanto' DEVE ser a ação quando nenhum ato pede algo da pessoa."

### `115` — documentos na convocação

**FR-3577, nova redação.** O titular da inscrição MUST ver a lista na tela da convocação da `059`,
para a convocação vigente, organizada pelos blocos da FR-3735 da `118`: o que fazer agora, prazo, o
que falta, o que já apresentou e os dados da convocação. Cada item mostra:

- nome, instrução e obrigatoriedade;
- o modelo anexo, para baixar, quando houver;
- o estado (FR-3590), com os textos da FR-3746 da `118`.

Os itens que não se aplicam MUST NOT ser mostrados. O vencimento é o prazo único da FR-3747 da
`118`, dito uma vez no bloco *Prazo*.

> *Redação anterior:* "O titular da inscrição MUST ver a lista na tela da convocação da `059`, para a
> convocação vigente. Cada item mostra: nome, instrução e obrigatoriedade; o modelo anexo, para
> baixar, quando houver; o vencimento e o estado (FR-3590). Os itens que não se aplicam MUST NOT ser
> mostrados."
>
> *Por que mudou:* a 375 px, a lista começava no fim da primeira tela, e o Requerimento ficava na
> terceira (ponto 3 do achado do PR #374).

**FR-3612, nova redação.** Os textos do portal MUST seguir a linguagem simples da `069`, caber em
375 px sem rolagem horizontal e ser os da FR-3746 da `118`, por item e por momento da chamada. Depois
do vencimento, o núcleo da frase é o da FR-3748 da `118`. Nenhum texto diz matrícula, bolsa ou
contratação como fato.

> *Redação anterior:* "Os textos do portal MUST seguir a linguagem simples da `069` e caber em 375 px
> sem rolagem horizontal: 'Falta enviar'; 'Recebido em DD/MM, às HH:MM, aguardando conferência';
> 'Pendente: ‹motivo›. Envie outro arquivo até ‹vencimento›'; 'Conforme'; 'Atendido pelo documento
> enviado na inscrição em DD/MM'; 'Aproveitado da chamada anterior, enviado em DD/MM. A comissão vai
> conferir de novo'; e, depois do vencimento, 'O prazo terminou em ‹vencimento›. A comissão vai
> decidir.' Nenhum texto diz matrícula, bolsa ou contratação."
>
> *Por que mudou:* "Atendido" aparecia antes da conferência; "Envie outro arquivo", sem um primeiro;
> e a lista seguia pedindo depois do desfecho (F2, F6 e o ponto 4 do achado).
>
> *Nota:* "Nenhum texto diz matrícula" ganhou "como fato": a frase do aceite (FR-3750 da `118`) cita
> a matrícula para dizer que o registro **não** é ela.

**User Story 2, cenário 2, nova redação.** *Given* a Ficha apresentada e conferida *conforme*,
*When* o aceite é registrado, *Then* a gestão mostra *"Apto para formalização"*, e o portal mostra
*"Vaga aceita"* e a frase de que o registro não é matrícula, bolsa nem contrato (FR-3750 da `118`).

> *Redação anterior:* "… Then a gestão mostra 'Apto para formalização' e o portal mantém a frase
> atual de que nenhum ato do GPS confirma matrícula ou contratação."
>
> *Por que mudou:* a "frase atual" não existia em tela nenhuma do portal; estava só num comentário de
> `portal/situacao.py` (F8).

### `059` — o caminho até a convocação

**FR-1090, acréscimo ao fim.** A ação continua *"Ver convocação"* haja ou não documento ou
Requerimento na chamada, e a lista MUST NOT dizer o que falta na convocação: isso pediria ler
documentos de cada inscrição, e a FR-1092 continua valendo. A nota de pendência na lista fica para
decisão própria (X1 da revisão de 04/11/2026).

> *Redação anterior:* a mesma, sem este acréscimo.

**FR-1096, nova redação.** Quando o Edital pede o requerimento, ele está **disponível** ou **em
preenchimento**, e a chamada **não pede documento**, a tela da convocação e a seção "Convocação" do
acompanhamento MUST oferecer "Preencher Requerimento de Matrícula" como ação principal, levando à
tela do requerimento da inscrição. Quando a chamada pede documento, o Requerimento entra nas
obrigações da convocação (FR-3725 da `118`), com o link próprio no bloco *O que fazer agora*, e a
ação principal leva à tela da convocação (FR-3730 da `118`).

> *Redação anterior:* "Quando o Edital pede o requerimento e ele está disponível ou em preenchimento,
> a tela da convocação e a seção 'Convocação' do acompanhamento MUST oferecer 'Preencher Requerimento
> de Matrícula' como ação principal, levando à tela do requerimento da inscrição."

**FR-1097, nova redação.** Quando o requerimento foi **enviado**, os mesmos dois lugares MUST oferecer
o caminho para conferir o que foi enviado — com a convocação aberta ou concluída —, e MUST NOT
oferecer o chamado para preencher. Quando a chamada pede documento, esse caminho é linha secundária,
e o enviado MUST NOT ser a ação principal (FR-3730 e FR-3731 da `118`); sem documento, continua como
antes (FR-3732 da `118`).

> *Redação anterior:* "Quando o requerimento foi enviado, os mesmos dois lugares MUST oferecer o
> caminho para conferir o que foi enviado — com a convocação aberta ou concluída —, e MUST NOT
> oferecer o chamado para preencher."

### `029` — Requerimento de Matrícula

As frases do Requerimento não são requisito da `029`: moram em `requerimentos/application/selectors.py`,
e a varredura da SC-132 as lê. A revisão entra como acréscimo à FR-405 e à FR-406.

**FR-405, acréscimo ao fim.** A explicação do estado *enviado* MUST depender da convocação, pela
FR-3752 da `118`: quem já foi convocado não lê "se você for convocado". Com o prazo da chamada
decorrido e nenhum requerimento vigente, a tela MUST mostrar "O prazo terminou", e não a recusa genérica
(FR-3754 da `118`).

> *Redação anterior:* a mesma, sem este acréscimo.

**FR-406, acréscimo ao fim.** Com convocação vigente, a tela do enviado MUST oferecer o caminho de
volta à convocação (FR-3752 da `118`).

> *Redação anterior:* a mesma, sem este acréscimo.

## Compatibilidade e conflitos com regras anteriores

| Regra | Conflito | Resolução |
|---|---|---|
| **FR-1175 da `063`** | Três ações só; o Requerimento enviado como ação principal | **Revista** (acima): com documento, a ação vem da projeção e leva à convocação |
| **FR-1176 da `063`** | Formato e frase do vencido livres | **Revista**: formato e núcleo únicos |
| **FR-1177 da `063`** e **SC-453 da `063`** | As frases novas sobre quem decide podiam ser lidas como consequência | **Acréscimo**: elas negam a consequência automática; as duas neutras continuam as únicas de consequência, e o SC-453 continua lendo os dicionários do módulo |
| **FR-1178 da `063`** | "Nada por enquanto" sozinho, com documentos com a comissão | **Revista**: seguida da frase de conclusão |
| **FR-1172 da `063`** | Nenhum: o rótulo continua o da tabela | A tela da convocação passa a usá-lo (FR-3750); "Minhas inscrições" continua com a espécie (FR-1091 da `059`), **diferença residual registrada** |
| **SC-454 da `063`** | Ler a projeção podia somar consultas | A projeção roda sem consulta; a view lê em número fixo, e nada sem convocação (FR-3734) |
| **FR-3577 e FR-3612 da `115`** | Ordem e textos literais | **Revistas** (acima) |
| **User Story 2 da `115`, cenário 2** | Cita frase que não existe | **Revista**: a frase passa a existir (FR-3750) |
| **FR-3574 da `115`** ("exatamente como antes" sem documento) | O formato do prazo, a frase do vencido e o rótulo do desfecho mudam em toda tela | **Compatível, nomeado**: a FR-3574 protege contra elementos da `115` aparecendo sem documento; a estrutura sem documento continua a de hoje, e a unificação de texto é desta spec (FR-3743) |
| **FR-3582 da `115`** e **FR-373 e FR-408 da `029`** | Com o Processo em estado final, o envio e a conferência de documento recusavam, e a política do Requerimento não fechava | **Decidido pelo usuário em 04/11/2026** (D-020): a FR-373 e a FR-408 da `029` foram revistas para fechar o Requerimento *na convocação*; a implementação é PR próprio. Esta spec não oferece a escrita (FR-3725, linha 3a) e não muda o comando (FR-3756) |
| **FR-1096 e FR-1097 da `059`**, sem documento | O enviado como ação principal | **Mantido como hoje** (FR-3732, D-017): sem documento, não há outra obrigação no portal que ele esconda |
| **FR-3591 da `115`** | A precedência serve à gestão | **Sem mudança**; o candidato tem ordem própria (FR-3726, FR-3758) |
| **FR-3622 da `115`** | A mesma frase nos documentos e no Requerimento | **Preservada**: o núcleo único vale para as duas recusas (FR-3748) |
| **FR-3614 da `115`** e **FR-084 da `010`** | Nenhum | **Sem mudança** (FR-3757); a QI-7 fica registrada |
| **FR-1090, FR-1096 e FR-1097 da `059`** | O Requerimento como ação principal escondia os documentos | **Revistas** (acima) |
| **FR-1092 da `059`** | Nenhum | "Minhas inscrições" não lê documentos (FR-3759) |
| **FR-1105 da `059`** ("não mudar o conteúdo da tela da convocação além do chamado ao requerimento") | Era o corte da `059`, e a `115` já o ultrapassou | **Sem revisão**: a regra delimitava aquela feature; esta spec muda a tela por requisito próprio |
| **FR-374, FR-405 e FR-406 da `029`** | O enviado dizia "se você for convocado" a quem foi; o vencido sem rascunho caía na recusa genérica | **Acréscimos** à FR-405 e à FR-406; a FR-374 não muda: nenhum rascunho nasce (FR-3754) |
| **SC-132 da `029`** e as varreduras de vocabulário da `063` e da `115` | Os textos novos precisam passar por elas | Os arquivos novos entram nas listas literais das varreduras (FR-3751) |
| **FR-290 da `019`** (mensagem) | Nenhum nesta spec | **Sem mudança**; a frase "esta convocação pede documentos" fica para decisão própria (X3) |
| **FR-272 da `019`** e **FR-3618 da `115`** | A correção por sucessão não é alcançável pela gestão | **Fora desta spec**; achado operacional em `doc/` |
| **Constituição, V** (necessidade demonstrável) | A projeção é entidade nova | É consumida por duas telas e pela guarda das frases; nada é gravado |

## Decisões

### D-001 — Uma entrega só, com o polish

**Decisão do usuário (04/11/2026).** Spec e os seis ajustes de polish do §9 do relatório numa
entrega só. PR de polish separado só com impedimento técnico demonstrado.

### D-002 — Nenhuma tela, estado ou canal novo

**Decisão do usuário (04/11/2026).** Nada de segunda tela, wizard, painel, estado persistente,
migration, endpoint desnecessário ou notificação. É a FR-3756.

### D-003 — O diagnóstico do PR #375 está aprovado

**Decisão do usuário (04/11/2026).** As falhas F1 a F12 e os pontos do achado são a base desta spec,
e o relatório é evidência, não implementação obrigatória.

### D-004 — O botão que só navega não diz "Enviar"

**Decisão do usuário (04/11/2026), corrigindo a maquete.** *"Enviar os N documentos que faltam"*
prometia um ato que o clique não pratica. O rótulo diz o que se vê ao chegar: *"Ver e corrigir os
documentos pendentes"*, *"Ver os documentos que faltam"*. "Enviar" fica para o botão que envia.

### D-005 — A frase de conclusão não apaga o aproveitado

**Decisão do usuário (04/11/2026), corrigindo a proposta.** *"Você enviou tudo o que esta convocação
pede pelo portal"* é falso para quem teve um documento aproveitado da inscrição. A frase é *"Você não
tem mais documentos para enviar agora. A comissão ainda vai concluir a análise."* (FR-3728).

### D-006 — O vocabulário e os limites não mudam

**Decisão do usuário (04/11/2026).** "Apto para formalização" ≠ "encaminhado" ≠ vínculo efetivado; o
GPS não é GED; nada automático por vencimento ou pendência; a comissão confere e decide; nenhuma
máquina de estados nova.

### D-007 — A projeção é função pura, no molde da situação da `063`

*Proposta de desenho.* A view da convocação já lê tudo o que a projeção precisa: a leitura
documental, o estado do prazo, o desfecho, o estado do Processo e a política do Requerimento. A do
acompanhamento lê o prazo, o desfecho e o Requerimento, e passa a ler também a leitura documental e o
estado do Processo, em número fixo de consultas e só com convocação (FR-3734). Uma função pura sobre essas entradas é testável por
tabela, não acrescenta consulta e não pode discordar da tela da convocação, que lê as mesmas fontes.
*Alternativa recusada*: estender `_acao_da_convocacao` com consultas dentro dela — misturaria o
relógio e o banco na derivação, que a `063` mantém sem os dois.

### D-008 — Com documento, o destino principal é a convocação

*Proposta de desenho.* Uma regra só para o link: com documento pedido na chamada, ele leva à tela da
convocação, onde estão todas as obrigações; sem documento, nada muda. É o que impede o Requerimento de
esconder os documentos, e mantém o cenário B como está. *Alternativa recusada*: o link ao primeiro
item pendente — levaria a uma âncora que some quando a pessoa envia, e esconderia o Requerimento.

### D-009 — O prazo vencido tem um núcleo e complementos

*Proposta de desenho.* A FR-3622 da `115` exige a mesma frase nas recusas de documento e de
Requerimento. As telas precisam dizer mais: o que não se envia mais e o canal. Um núcleo constante,
usado nas recusas e em toda tela, mais complementos por contexto, preserva a regra e acaba com as três
redações (FR-3748).

### D-010 — A tela da convocação se ordena pelo que falta

*Proposta de desenho.* A lista da `115` seguia a ordem do Edital, e a pendência ficava no segundo
cartão. Separar *o que falta* de *o que já apresentou* põe as tarefas na primeira tela sem esconder
nada: os dois blocos seguem a ordem do Edital por dentro. Depois do desfecho, volta a ser uma lista
só, porque não há mais tarefa (FR-3735, FR-3742).

### D-011 — As revisões se aplicam na primeira tarefa da implementação

*Proposta de desenho.* Aplicar agora faria as specs da `063`, da `115`, da `059` e da `029`
descreverem telas que o código ainda não tem. Escrever a nova redação aqui e aplicá-la na T001, com a
anterior preservada, segue o caminho da `117` para a FR-069 da `009`. Se a revisão do PR preferir,
aplicam-se neste PR.

**Precedência na transição.** Do merge desta spec até a T001, onde a redação de uma spec revista
divergir desta, **prevalece a `118`**, e quem implementa lê a redação nova daqui. Os testes de hoje
continuam valendo até a T001, que os revê junto do código (plano, *Testes que prendem os textos de
hoje*).

### D-012 — "Minhas inscrições" fica como está

*Proposta de desenho.* Dizer "2 documentos a enviar" na lista exigiria ler documentos de cada
inscrição; a leitura em lote existe, mas a FR-1092 da `059` pede o custo medido. Com o acompanhamento
e a convocação corrigidos, quem abre "Ver convocação" vê a pendência na primeira tela. A nota fica
para decisão (X1), e o rótulo do desfecho na lista também (FR-1091 da `059`).

### D-013 — A frase do aceite vale para toda convocação

*Proposta de desenho.* A frase de que o registro não é matrícula, bolsa nem contrato não depende de
haver documento: o aceite sem documento é o mesmo ato. Ela aparece no aceite e na regularização, os
dois desfechos que incluem na ocupação, em toda convocação (FR-3750).

### D-014 — "Apto para formalização" não vai ao portal

*Proposta de desenho.* O termo é da gestão (FR-3610 da `115`). Para o candidato seria jargão, e
"apto" soaria como promessa de vínculo. A frase do aceite diz o mesmo limite sem nomear o termo.

### D-015 — A causa do fechamento é derivada, e o Processo prevalece

*Proposta de desenho, da revisão do PR (04/11/2026).* A escrita de documentos fecha por duas causas
que dizem coisas diferentes à pessoa: o vencimento (a comissão ainda confere e decide) e o Processo em
estado final (ninguém mais confere nem desfecha). Uma frase só para as duas afirmaria um vencimento que
não houve, ou prometeria uma conferência que o sistema recusa. A causa sai da mesma condição que recusa
o envio, a cada leitura, sem estado gravado. Com as duas juntas, vale o Processo, porque é a que fecha
mais (FR-3721, FR-3741).

### D-016 — No Requerimento, a exigência e a situação vêm antes da disponibilidade

*Proposta de desenho, da revisão do PR (04/11/2026).* A política da `029` responde se é possível
escrever **agora**. Depois do desfecho, ela diz "ainda indisponível" a quem nunca enviou, e ler essa
resposta como "não pedido" apagaria uma obrigação que existiu. A projeção lê as três coisas que a
política já expõe — momento declarado, situação e disponibilidade — nessa ordem, sem decidir
disponibilidade por conta própria (FR-3725).

### D-017 — Sem documento, a ação fica exatamente a de hoje

*Proposta de desenho, da revisão do PR (04/11/2026).* A falsa conclusão de C2 vem de o Requerimento
esconder documentos. Sem documento na chamada, não há o que esconder no portal, e *"Seu Requerimento
de Matrícula foi enviado."* é verdadeiro e completo. Mudá-lo seria regressão sem ganho, contra o pedido
do usuário de deixar o caminho direto como está (FR-3732). *Alternativa recusada*: a linha secundária
também sem documento, que deixaria a ação principal vazia ou diria "Siga as instruções do Edital" a
quem já fez o que o portal pede.

### D-018 — O opcional tem lugar próprio, e nunca some

*Proposta de desenho, da revisão do PR (04/11/2026).* A primeira redação punha os opcionais no bloco
*O que falta* e escondia o bloco sem tarefa — o opcional ficava sem formulário justamente quando nada
mais faltava. O bloco 3 passa a existir também só com opcionais, com outro título, e o facultativo
ganha classificação própria em cada estado, fora de toda contagem (FR-3722, FR-3735, FR-3738).

### D-019 — Sem documento, o Requerimento não enviado é dito, sem ação

**Decisão do usuário (04/11/2026), no encerramento da spec.** A primeira redação mantinha o caminho
sem documento intacto e deixava registrada a omissão: num Edital só com Requerimento, depois do prazo
ou do desfecho, nenhuma tela além da do Requerimento dizia que ele não foi enviado — a F3 do relatório.
O usuário decidiu uma exceção **estritamente informativa**: uma linha, sem link, só quando a política
já não admite o preenchimento, com a ação principal de hoje e sem consulta nova (FR-3732, FR-3743). B
e B2 não mudam.

### D-020 — O Processo em estado final fecha o Requerimento na convocação

**Decisão do usuário (04/11/2026), sobre o encaminhamento do Processo encerrado.** Com o Processo
encerrado ou cancelado, o GPS já recusava documento, conferência e desfecho, e o Requerimento *na
convocação* seguia aberto — escrita que nenhum ato poderia considerar (FR-035 da `001`). Ele passa a
fechar também, com a leitura e o rascunho preservados (FR-373 e FR-408 da `029`, revistas). Nesta
spec, a projeção o mostra como não enviado, sem ação, antes da linha do prazo (FR-3725, linha 3a), e
nenhuma tela oferece o preenchimento. O Requerimento *na inscrição* não muda. A implementação da
recusa é PR próprio; a `118` não muda comando (FR-3756).

### D-021 — O acompanhamento sem documento pode pagar a leitura da lista

**Decisão do usuário (04/11/2026), na revisão da implementação (PR #384).** Para saber se a chamada
pede documento, o acompanhamento lê a lista gravada nela no ato de convocar — a mesma que a tela da
convocação já lia. Em toda convocação sem documento, isso é uma consulta a mais em relação à linha de
base; a convocação, que já a pagava, não aumenta. O custo é fixo, e a leitura usa os documentos
registrados na chamada, de modo que o histórico se preserva diante de uma Retificação posterior que
tire o documento do Edital. *Alternativa descartada na implementação*: decidir pelo conteúdo vigente
do Edital, sem ler a lista — economizaria a consulta, mas uma Retificação que retirasse o documento
depois da convocação esconderia itens que a chamada pediu. Não se demonstrou que ela seja a única
alternativa; é a troca aceita. A SC-1128 foi revista (redação anterior preservada nela).

## Registrado, sem desenvolver

### QI-7 — aviso de pendência: recomendação para decisão institucional

**Hoje** a pessoa só fica sabendo de uma pendência se voltar ao portal por conta própria. Esta spec
faz a pendência aparecer na primeira tela de quem volta, e não resolve quem não volta. Avisar é a
quinta situação da FR-084 da `010`, que exige revisar aquela regra, e é a mesma decisão da validação
de LGPD que mantém `AVISOS_AOS_CANDIDATOS` desligada em produção.

**Recomendação, se a instituição admitir o aviso:**

1. **Por gesto humano, e nunca automático.** Quem confere decide *"Avisar a pessoa das pendências
   desta chamada"*, uma vez por lote de conferências, nunca a cada clique. Aviso disparado por
   pendência ou por vencimento próximo seria o lembrete que a FR-084 exclui pelo nome.
2. **Sem dado sensível.** O e-mail diz só que *"há documento da convocação que precisa de atenção"* e
   aponta a área do candidato. O nome do documento, o motivo e a modalidade não vão ao e-mail: podem
   revelar saúde, renda ou cota. O motivo continua só no portal (FR-3584 da `115`).
3. **Distinto da comunicação oficial.** Assunto que não comece por "Convocação"; rodapé fixo, no
   molde da FR-1257 da `066`: *"Este aviso não é a convocação nem altera o seu prazo. O prazo é o da
   convocação: até ‹vencimento›. A referência é a sua área do candidato."* O aviso não grava
   comunicação de convocação (FR-1242 da `066`).
4. **Não move prazo.** Nada no aviso cria prazo de complementação; dar mais prazo continua sendo a
   correção por sucessão (FR-3618 da `115`).

**O que pede a decisão:** a revisão da FR-084 da `010`, a validação de LGPD e uma spec própria.

### Correção da convocação por sucessão pela gestão — achado operacional

A verificação desta spec confirmou: o domínio corrige a convocação vigente por sucessão, com motivo e
vencimento novo (`convocacao/application/convocar.py`), e a view lê `motivo` do POST; mas nenhum
formulário da gestão envia `motivo`, e a fila exclui quem tem chamada em aberto. Pela tela, a
comissão não dá mais prazo. Afeta a FR-3618 e a FR-3622 da `115`, a FR-272 da `019` e a FR-870 da
`050`. Registro, reprodução e requisitos:
[`doc/achado-correcao-da-convocacao-pela-gestao-2026-11-04.md`](../../doc/achado-correcao-da-convocacao-pela-gestao-2026-11-04.md).
**Não é escopo desta spec** (D-002), e a priorização é do usuário.

### O Requerimento com o Processo em estado final — decidido, implementação à parte

O usuário decidiu em 04/11/2026 (D-020) que o Requerimento *na convocação* deixa de aceitar escrita
com o Processo encerrado ou cancelado, e a FR-373 e a FR-408 da `029` foram revistas. A implementação
no comando e na política é **PR próprio**, pelo encaminhamento
`doc/encaminhamento-requerimento-com-processo-encerrado-2026-11-04.md`, que também registra a decisão
ainda pendente sobre o sucessor do Requerimento *na inscrição*.

### Outros, fora desta spec

- **X1** — a nota de pendência em "Minhas inscrições" e o rótulo do desfecho na lista (D-012).
- **X3** — a frase dos documentos e a variante da sucessora na mensagem de convocação (FR-290 da
  `019`).
- **R11 do relatório** — o prazo restante na conferência da gestão, perto do vencimento. É tela da
  gestão (FR-3758).
- **X5** — o teste com candidatos reais.
