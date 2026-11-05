# Feature Specification: A experiência da convocação — incremento 1

**Feature Branch**: `claude/beautiful-herschel-1c10b5`, sobre a `main` em `21b728af`

**Created**: 2026-11-05

**Status**: Draft, **só documental**. Nenhum código, migration, rota ou tela foi alterado. As
decisões têm duas origens:

- **Do usuário, em 05/11/2026, no parecer sobre o estudo:** as dez decisões da seção 11 do estudo,
  citadas aqui como *1ª a 10ª decisão do estudo*. Não se reabrem.
- **Propostas de desenho desta spec:** D-001 a D-012, abaixo. Elas resolvem o que o estudo deixou
  aberto ou o que a leitura das specs vigentes mostrou que ele não alcançava. **Aguardam o usuário.**

**Input**: o estudo
[`doc/estudo-experiencia-da-convocacao-2026-11-05/README.md`](../../doc/estudo-experiencia-da-convocacao-2026-11-05/README.md),
versão 2, mergeado no PR #394 em 05/11/2026 (`21b728af`): a seção 10, *"MVP em dois incrementos"*, no
que ela chama de **incremento 1**, com as decisões fechadas da seção 11. As maquetes de
[`maquetes/`](../../doc/estudo-experiencia-da-convocacao-2026-11-05/maquetes/) são **evidência**, e
não implementação obrigatória: o que esta spec exige é o que está nos requisitos. Onde os dois
divergem, a divergência está dita numa decisão.

> **Faixa de identificadores.** Esta spec abre em **FR-3858** e **SC-1150**. O teto foi medido em
> 05/11/2026 em `specs/` de todas as worktrees desta máquina e da `main` em `21b728af`: o requisito
> funcional três mil oitocentos e cinquenta e sete e o critério mil cento e quarenta e nove, os dois
> da `120`. A pasta `121` não existe em nenhuma delas, e o único PR aberto (#395) é só da Visão do
> Sistema. **Nenhum `UX-` é aberto aqui.** As decisões reiniciam em `D-001`.
>
> **A SC-1172 fica fora da sequência.** Ela entrou com a decisão da D-009, depois do plano, quando a
> `122` (PR #398, ainda aberto) já tinha tomado os critérios de mil cento e sessenta e cinco a mil
> cento e setenta e um. O teto foi medido de novo em
> 05/11/2026, nas mesmas worktrees e nos PRs abertos.
>
> **Como esta spec cita outras.** Um requisito de outra feature é citado pelo identificador e pela
> feature ("a FR-1104 da `059`"). Uma decisão de outra feature é citada pelo assunto e pela feature,
> nunca pelo número. Os achados e as garantias do estudo (`E1`, `T6`, `A1`, `S1`–`S8`, `R-12`) e a
> questão institucional `QI-7` são citados como estão no estudo.

---

## Por que esta feature existe

**A convocação é a mensagem mais importante que o sistema manda, e hoje ela lê como tela de
administrar documentos.** A `118` pôs o "O que fazer agora" no topo e fez a ação caber na primeira
tela. O estudo de 05/11 percorreu a jornada em cinco bancos de demonstração (C1, F, G, I1 e a
correção) e mostrou que falta o significado:

- **A página não diz o que aconteceu** (`T1`). O título é "Convocação", e a frase "Você foi
  convocada(o)" só existe no ramo sem documento. Nada diz que a convocação ainda não é a matrícula
  antes do aceite (`T2`). O prazo é uma linha entre outras, sem o dia da semana nem quanto falta
  (`T3`).
- **A sucessora não diz que substitui** (`T6`, `E4`). Depois da correção da `120` saem duas
  mensagens idênticas, salvo o prazo, e nenhuma diz qual vale.
- **O e-mail não diz que há documentos** (`E1`, a X3 da `118`), não traz a instituição por extenso
  no assunto (`E2`) e leva à lista, e não à convocação (`E3`).
- **O link direto, sem sessão, responde 404** (`A1`), inclusive ao próprio titular com a sessão
  vencida. E o destino que o acesso já guarda não alcança a convocação (`A2`).
- **Depois do envio, a confirmação fica fora da tela** (`T7`), e a convocação não carrega script
  nenhum (`R-12`): escolhido o PDF, o cartão continua dizendo "Nenhum arquivo escolhido".

Nada disso pede regra nova. É redação, ordem e navegação sobre os serviços que já existem.

### O que esta spec cobre, e o que fica fora

**Cobre**, e nada além:

1. **A página da convocação**: a chamada, o título por estado, a correção dita no cartão do prazo, o
   envio voltando a `#confirmacao` com o foco na confirmação, e os três scripts estáticos que a
   inscrição já carrega.
2. **O prazo**: o dia da semana, a data e a contagem saem de uma função só, no fuso da instalação.
3. **O acesso A**: sem sessão, a convocação redireciona ao acesso com destino, antes de qualquer
   consulta, e o destino sobrevive ao código, com as garantias `S1` a `S8` do estudo.
4. **O e-mail institucional** em HTML com alternativa em texto: a mensagem inicial e a da correção,
   com assunto e frase condicionados ao que a chamada pede.

E as revisões que isso exige, escritas em *Revisões de requisitos anteriores* e aplicadas aos
arquivos das specs revistas neste mesmo PR (D-001).

**Fica fora:**

- **o link mágico** (alternativa C do estudo), por decisão do usuário (3ª decisão do estudo);
- **o aviso de pendência (`QI-7`)**, que continua com a decisão institucional e de privacidade
  própria (5ª decisão do estudo) — a FR-084 da `010` continua com quatro situações;
- **a finalidade da convocação como dado declarado** (10ª decisão do estudo): o texto fica no núcleo
  neutro, e a palavra "matrícula" só aparece quando o Requerimento de Matrícula é pedido (D-003);
- **a duração da sessão** (9ª decisão do estudo), que é revisão com a TI;
- **o `body{font-size:16px}` do portal** (`R-13`), que é do portal inteiro e fica para decisão
  própria;
- **o teste com pessoas** (seção 9 do estudo), que roda **sobre** este incremento, em homologação;
- **a verificação de SPF, DKIM e DMARC** (8ª decisão do estudo), que é pré-requisito do uso real, com
  a TI, e não cabe no código;
- **as outras rotas do titular sem sessão** — o acompanhamento, o Requerimento — que continuam como
  estão (D-002);
- **a troca do rótulo "Espécie" nos dados do ato** (`T5`) e o vocabulário por tipo de seleção (seção
  3 do estudo), salvo o que a espécie já gravada decide e esta spec não usa.

## Clarifications

### Session 2026-11-05 (parecer do usuário sobre o estudo)

- Q: O título da página? → A: **"Você foi convocado!"**, sem afirmar matrícula, contratação, bolsa
  concedida ou vaga garantida, e com o resto da interface coerente com ele (1ª decisão do estudo).
- Q: Para onde aponta o link da mensagem (FR-1104 da `059`)? → A: Para a convocação específica
  (2ª decisão do estudo).
- Q: O acesso? → A: E-mail e código, com o destino preservado, inclusive no primeiro acesso e na
  reconciliação; o link mágico fica fora (3ª decisão do estudo).
- Q: A frase das obrigações e a da correção, no e-mail? → A: Sim, sempre condicionadas às obrigações
  que a chamada tem de fato (4ª decisão do estudo).
- Q: O aviso de pendência? → A: Fora deste incremento (5ª decisão do estudo).
- Q: O nome da pessoa no e-mail? → A: Não, e também nada de CPF, modalidade, motivo de pendência ou
  anexo (6ª decisão do estudo).
- Q: A versão do modelo da mensagem? → A: Manter o versionamento verificável, e só acrescentar
  coluna se o que já se registra não bastar para a auditoria (7ª decisão do estudo; D-009).
- Q: SPF, DKIM e DMARC? → A: Verificação necessária antes do uso real, com a TI (8ª decisão do
  estudo).
- Q: A duração da sessão? → A: Rever com a TI (9ª decisão do estudo); fora daqui.
- Q: A finalidade da convocação? → A: Fora do MVP, sem campo novo (10ª decisão do estudo).
- Q: As revisões da `118` e da `120` além das quatro pedidas (D-011)? → A: Aceitas como estão
  (parecer de 2026-11-05, depois da spec escrita).
- Q: A enviada, a mensagem da correção B falhou, C substitui B: o que diz a mensagem de C (D-008)? →
  A: Cita a última mensagem enviada com sucesso na cadeia, A; sem envio com sucesso na cadeia, sai a
  inicial. Os dados do ato continuam identificando B. Diz *"enviada"*, sem afirmar recebimento.
- Q: As demais propostas? → A: D-001 a D-007, D-010 e D-012 aceitas como estão; a D-009 aceita sob a
  condição de o plano provar a variante **e** a versão exata do modelo usado no envio.
- Q: A prova do plano mostrou que o histórico de implantação não identifica a versão exata do modelo
  (R-001 do plano). Como fica a D-009? → A: **Opção A**: uma coluna em `ComunicacaoEmitida`,
  `modelo_da_mensagem`, com o nome do modelo e o SHA-256 dos arquivos HTML e texto efetivamente
  usados na renderização, numa composição determinística, gravada também na tentativa que falhou. Os
  registros anteriores e a publicação ficam sem identificação, sem versão inferida retroativamente.
  A FR-3891 abre a exceção só para essa coluna e a migration dela. Os arquivos históricos continuam
  recuperáveis pelo Git (decisão de 2026-11-05, sobre o plano).

## User Scenarios & Testing *(mandatory)*

Os cenários são os das fixtures da `118` (`tests/fixtures/jornada_do_convocado.py`): **A**, **C1**,
**C2**, **F**, **G**, **I1**, **I2**, **J**, **K** e o sem documento, mais o cenário **corr** do
estudo, que é o A corrigido pela `120`.

### User Story 1 — Quem abre a convocação entende o que aconteceu e o que fazer (Priority: P1)

A pessoa recebe a mensagem, entra e lê, nesta ordem: que foi convocada, o que esta etapa pede, até
quando, o que ainda falta e um botão que a leva ao primeiro item a fazer. Logo abaixo, o que acontece
se não atender e que isso ainda não é a matrícula.

**Why this priority**: é a pergunta "a vaga está garantida?" — quem acha que já está matriculado não
envia nada, e perde o prazo.

**Independent Test**: no cenário C1, abrir a convocação a 375 × 812 e conferir a ordem e o texto da
chamada, a posição da ação e o destino do botão.

**Acceptance Scenarios**:

1. **Given** C1 (documentos e Requerimento, nada enviado), **When** a pessoa abre a convocação,
   **Then** o título é *"Você foi convocado!"*, a etapa diz *"Nesta etapa, você envia seus documentos
   e o Requerimento de Matrícula para a comissão conferir."*, o cartão do prazo diz a data, o dia da
   semana e quanto falta, o resumo diz o que falta, e *"Ver o que preciso fazer"* leva ao primeiro
   cartão a enviar.
2. **Given** F (um documento pendente, um a enviar, Requerimento enviado), **When** a pessoa abre a
   convocação, **Then** a etapa não pede o Requerimento no imperativo, o resumo diz *"Você ainda
   precisa corrigir 1 documento e enviar 1 documento."*, e o botão leva ao cartão pendente.
3. **Given** C1, **When** a pessoa lê a chamada, **Then** a frase de consequência é só a da FR-1177
   da `063`, e a ressalva diz que a convocação ainda não é a matrícula.
4. **Given** G (prazo vencido sem desfecho), **When** a pessoa abre a convocação, **Then** o título é
   *"O prazo desta convocação terminou"*, sem botão, sem andamento e sem formulário.
5. **Given** I1 (vaga aceita), **When** a pessoa abre a convocação, **Then** o título é *"Resultado
   da sua convocação"*, com o rótulo do desfecho e a frase do aceite.

---

### User Story 2 — A correção diz qual prazo vale (Priority: P1)

Depois da correção da `120`, a pessoa tem duas mensagens e uma página. A página diz, no próprio
cartão do prazo, que a convocação foi corrigida e que aquele é o prazo válido; os dados do ato dizem
qual mensagem foi substituída e com que prazo. A mensagem da correção tem assunto e título próprios
e diz qual mensagem substitui.

**Why this priority**: duas mensagens oficiais com prazos diferentes, sem dizer qual vale, é a
confusão que custa a vaga — e a sucessora pode **antecipar** o prazo (FR-3844 da `120`).

**Independent Test**: no cenário corr, comparar a mensagem inicial e a da correção, e abrir a
convocação pelo link da primeira.

**Acceptance Scenarios**:

1. **Given** corr, **When** a pessoa abre o link da **primeira** mensagem, **Then** chega à
   convocação vigente, e o cartão do prazo diz *"Convocação corrigida: este é o prazo válido."* acima
   da data nova.
2. **Given** corr, **When** a pessoa lê os dados do ato, **Then** eles dizem quando a convocação
   substituída foi comunicada e com que prazo, e que esse prazo não vale mais, sem o motivo.
3. **Given** corr, **When** a mensagem da correção sai, **Then** o assunto começa por *"Ifes ·
   Convocação corrigida no Edital ‹NN/AAAA›"*, o título diz que a convocação foi corrigida, e um
   quadro diz a data e a hora do envio substituído e o prazo que ele informava.
4. **Given** a prévia da correção na gestão, **When** a forma é mensagem individual, **Then** ela diz
   que a mensagem sai dizendo que corrige a anterior.

---

### User Story 3 — O link da mensagem leva direto à convocação, com ou sem sessão (Priority: P1)

Com sessão, o link abre a convocação. Sem sessão — vencida, outro aparelho, primeiro acesso —, ele
leva à tela de acesso, que diz que depois do código a pessoa vai direto para a convocação, e é o que
acontece.

**Why this priority**: hoje o link direto sem sessão dá 404, e o da mensagem passa pela lista; os
dois são o único passo que não serve a ninguém (`A1`, `E3`).

**Independent Test**: abrir o endereço da convocação sem sessão, fazer o acesso por e-mail e código,
e conferir que se chega à convocação sem passar pela lista; repetir com identificador inventado e com
o de outra pessoa.

**Acceptance Scenarios**:

1. **Given** o titular sem sessão, **When** abre o endereço da convocação, **Then** é levado ao
   acesso, a tela diz *"Depois do código, você vai direto para a convocação."*, e, provado o código,
   chega à convocação.
2. **Given** o primeiro acesso ou a reconciliação de uma inscrição antiga, **When** a pessoa termina
   o acesso, **Then** chega à convocação, e não à lista.
3. **Given** ninguém com sessão, **When** abre o endereço com identificador real, inventado ou de
   outra pessoa, **Then** a resposta é a mesma nos três, e nenhuma consulta pelo identificador
   acontece antes dela.
4. **Given** uma sessão de outra pessoa, **When** ela abre a convocação alheia, **Then** recebe o 404
   de hoje, igual ao de inexistente (FR-1101 da `059`).
5. **Given** um destino de outro host, de esquema estranho ou de rota fora da lista fechada, **When**
   o acesso termina, **Then** a pessoa vai para "Minhas inscrições", como hoje.

---

### User Story 4 — A mensagem diz o que a chamada pede, e é reconhecível como do Ifes (Priority: P1)

A mensagem inicial diz, no assunto e no corpo, o que a chamada pede de fato — documentos, o
Requerimento, os dois ou nenhum —, o prazo com o dia da semana, como entrar, que ainda não é a
matrícula e o que o Ifes nunca pede por e-mail. Ela tem HTML e uma alternativa completa em texto.

**Why this priority**: quem lê só a mensagem não sabe que precisa juntar certidão e histórico antes
de o prazo vencer (`E1`).

**Independent Test**: comunicar uma convocação em cada variante de obrigação e conferir assunto,
frase, texto puro e o que não pode ir.

**Acceptance Scenarios**:

1. **Given** uma chamada com documento obrigatório e Requerimento, **When** a mensagem sai, **Then**
   o assunto é *"Ifes · Convocação no Edital ‹NN/AAAA›: envie seus documentos até ‹DD/MM›"* e o corpo
   diz *"Esta convocação pede documentos e o Requerimento de Matrícula."*
2. **Given** qualquer variante, **When** a mensagem sai, **Then** o texto puro contém tudo o que o
   HTML contém, e nenhum dos dois traz nome, CPF, nome de documento, motivo, modalidade, imagem,
   recurso externo ou parâmetro de rastreio.
3. **Given** a repetição com a mesma chave, **When** o envio é pedido de novo, **Then** nada sai, como
   hoje.

---

### User Story 5 — Depois do envio, a pessoa vê o que foi recebido e o próximo passo (Priority: P2)

Quem envia o primeiro de quatro documentos volta à chamada, com o foco numa confirmação que diz qual
documento foi recebido, que ele aguarda a conferência da comissão, e qual é a próxima tarefa.
Escolhido o arquivo, o cartão diz o nome dele; uma recusa aparece no próprio cartão, com o foco nela.

**Why this priority**: hoje a confirmação fica fora da tela e o cartão contradiz a escolha do
arquivo; é a mesma família da `T7`, e o próximo passo some.

**Independent Test**: no cenário C1, enviar um PDF e conferir onde a página para, onde está o foco e
o que a confirmação diz; enviar um arquivo que não é PDF e conferir a recusa.

**Acceptance Scenarios**:

1. **Given** C1, **When** a pessoa envia a certidão, **Then** a página volta a `#confirmacao`, o foco
   está na confirmação, e ela diz *"Recebemos: Certidão de nascimento ou casamento, em ‹data›, às
   ‹hora›. O arquivo aguarda a conferência da comissão."* e *"Próxima tarefa: ‹link›"*.
2. **Given** o último documento a enviar, **When** a pessoa o envia, **Then** a confirmação diz a
   frase de conclusão da FR-3728 da `118`, sem próxima tarefa.
3. **Given** um arquivo que não é PDF, **When** a pessoa tenta enviá-lo, **Then** a recusa fica no
   cartão do item, com o foco nela, e não há confirmação.
4. **Given** o cartão de um item, **When** a pessoa escolhe um arquivo, **Then** o cartão diz o nome
   do arquivo escolhido.

---

### Edge Cases

Cada caso abaixo é requisito, e entra na verificação como os `FR-`.

- **Prazo não iniciado** (cenário K). O título é *"Você foi convocado!"*; o cartão do prazo diz só a
  frase da FR-3749 da `118`, sem data, sem dia da semana e sem contagem; a consequência não aparece
  (FR-1177 da `063`). O e-mail não existe ainda: ele é o que inicia o prazo.
- **Sem vencimento registrado.** O cartão do prazo diz a frase de hoje para esse caso (FR-3737 da
  `118`), sem contagem; o assunto do e-mail não leva data, e o corpo diz *"O prazo para atender é o
  que o Edital publica."*
- **Vencimento hoje, ainda não passado.** A contagem diz *"termina hoje, às HHhMM"*, mesmo a minutos
  do vencimento; nunca *"falta 1 dia"* (FR-3874).
- **Vencimento à meia-noite local.** A data, o dia da semana e a contagem são os do instante no fuso
  da instalação: 00h00 de 11/11 é *quarta-feira, 11/11/2026, às 00h00*, e não "fim de 10/11".
- **Vencimento às 23h30 locais**, que é 02h30 UTC do dia seguinte. A data, o dia e a contagem são os
  do dia local (FR-3873).
- **Chamada só com documento facultativo.** A tela segue a `118` (bloco *O que falta* só com o
  opcional); a etapa diz que a pessoa *pode* enviar documento opcional; o e-mail usa a variante sem
  documentos (D-007).
- **Todos os documentos obrigatórios aproveitados.** A mensagem diz o que a chamada **pede**, e não o
  estado: *"pede documentos"* continua verdadeiro, e a página diz *"Não precisa enviar de novo"*
  (FR-3746 da `118`). Sem tarefa, não há botão; vale a frase de conclusão (FR-3728 da `118`).
- **Cadeia de correções sem nenhuma mensagem enviada com sucesso.** A mensagem é a inicial, porque
  não há mensagem a substituir; a página continua dizendo *"Convocação corrigida"* no cartão do prazo,
  e os dados do ato dizem que a substituída não foi comunicada (D-008).
- **A mensagem da imediatamente anterior falhou, mas outra da cadeia foi enviada.** A convocação A
  teve a mensagem enviada, a mensagem da correção B falhou, e C substitui B: a mensagem de C é a da
  correção e cita **A**, a última mensagem enviada com sucesso na cadeia. Os dados do ato continuam
  identificando **B** como a convocação imediatamente substituída (D-008).
- **Correção da correção, sem falha.** A última mensagem enviada com sucesso é a da imediatamente
  anterior, e é ela que a mensagem cita; os dados do ato também descrevem a imediatamente anterior
  (D-008). A mensagem diz *"enviamos"*, e nunca afirma que a pessoa recebeu (FR-288a da `019`).
- **Convocação por publicação.** Nenhum e-mail sai, como hoje (FR-287 da `019`). A página segue esta
  spec, e a correção é dita no cartão do prazo do mesmo jeito.
- **O mesmo arquivo enviado de novo.** A confirmação diz *"Este arquivo já tinha sido recebido."*, a
  frase de hoje, sem próxima tarefa nova.
- **Vários envios seguidos.** Cada volta mostra só a confirmação do seu envio; o andamento mostra o
  acumulado.
- **Recusa por prazo encerrado no envio.** A recusa fica no cartão, com o núcleo do vencido da
  FR-3748 da `118`; a página, recarregada, já está no estado encerrado.
- **Sessão identificada, mas sem código provado.** Conta como sem sessão: o redirecionamento ao
  acesso vale igual (FR-3876).
- **Pedido sem sessão a uma rota de escrita da convocação** (apresentar documento, abrir rascunho,
  enviar Requerimento). Continua como hoje: nenhum redirecionamento leva a praticar ato (FR-3877).
- **Destino guardado de outra visita.** Um destino antigo na sessão só leva à rota que ele nomeia, e
  a titularidade é conferida de novo ao abrir (FR-3879): ele não carrega autorização.
- **Pessoa com mais de uma inscrição convocada.** O link é da inscrição, e leva à convocação dela;
  as outras ficam em "Minhas inscrições".
- **Estado aguardando ou não convocado na rota da convocação.** O título e o texto continuam os de
  hoje: esta spec só muda a página quando há convocação vigente.

## Requirements *(mandatory)*

### Functional Requirements

#### A. A chamada

- **FR-3858**: Com convocação vigente, o título de primeiro nível da tela da convocação MUST depender
  do estado, com ou sem documento pedido na chamada:

  | Estado | Título |
  |---|---|
  | chamada *aberta*, prazo correndo, sem vencimento ou com a comunicação não enviada | *"Você foi convocado!"* |
  | chamada *encerrada pelo prazo* | *"O prazo desta convocação terminou"* |
  | chamada *encerrada pelo Processo* | *"O envio pelo portal está encerrado"* |
  | desfecho vigente | *"Resultado da sua convocação"* |

  Nenhum título MUST afirmar matrícula, contratação, bolsa concedida ou vaga garantida (FR-3751 da
  `118`; UX-155 a UX-158 da `063`). O título por estado **absorve** o título do bloco 1 da FR-3741 e
  da FR-3742 da `118`, que não se repete abaixo dele (D-005).
- **FR-3859**: Com documento pedido na chamada e a chamada *aberta*, a primeira parte da tela — a
  **chamada** — MUST dizer, nesta ordem: o contexto curto (o Perfil e o Edital, *"‹Perfil› · Edital
  ‹NN/AAAA›"*); o título da FR-3858; a etapa (FR-3860); o cartão do prazo (FR-3861); o resumo do que
  falta (FR-3862); e a ação principal (FR-3863). Logo depois da ação, e ainda antes do andamento, vêm
  a consequência e a ressalva (FR-3864).
- **FR-3860**: A frase da etapa MUST descrever **as obrigações da chamada**, e não o estado: ela sai da
  lista gravada no ato de convocar e da política do Requerimento, e vale igual antes e depois de
  qualquer envio.

  | A chamada pede | Frase |
  |---|---|
  | documento obrigatório e o Requerimento de Matrícula | *"Nesta etapa, você envia seus documentos e o Requerimento de Matrícula para a comissão conferir."* |
  | documento obrigatório, sem o Requerimento | *"Nesta etapa, você envia seus documentos para a comissão conferir."* |
  | só documento facultativo, com o Requerimento | *"Nesta etapa, você envia o Requerimento de Matrícula e pode enviar documento opcional para a comissão conferir."* |
  | só documento facultativo, sem o Requerimento | *"Nesta etapa, você pode enviar documento opcional para a comissão conferir."* |

  A frase MUST NOT estar no imperativo (*"apresente"*, *"envie"*): no imperativo, ela pediria o
  Requerimento a quem já o enviou (cenário F).
- **FR-3861**: O **cartão do prazo** MUST ter o rótulo e o formato da FR-3747 da `118` (*"Prazo desta
  convocação"*, *"até DD/MM/AAAA, às HHhMM"*), com a data como o maior texto do cartão, e, abaixo
  dela, a linha *"‹dia da semana› · ‹contagem›"* da FR-3874, as duas da função da FR-3873. Com a
  comunicação não enviada, o cartão diz só a frase da FR-3749 da `118`; sem vencimento, só a frase da
  FR-3737 da `118` para esse caso. A correção é dita no próprio cartão (FR-3869). O cartão MUST NOT
  encolher a tipografia em tela estreita: a primeira tela cabe pela ordem, e não pelo tamanho (D-006).
- **FR-3862**: O **resumo do que falta** MUST ser a frase da linha 4 da FR-3730 da `118` (*"Você ainda
  precisa ‹tarefas›."*, na ordem da FR-3726); sem tarefa, a frase de conclusão da FR-3728 da `118`.
- **FR-3863**: Com tarefa, a **ação principal** MUST ser **um** link, *"Ver o que preciso fazer"*,
  que leva à **primeira tarefa na ordem da FR-3726 da `118`** — a pendente antes da que falta, e o
  Requerimento quando ele for a única. Ela MUST ser o primeiro controle do conteúdo da página depois
  do título, da etapa, do prazo e do resumo, e vir antes do andamento, dos formulários e dos dados do
  ato. O rótulo MUST NOT começar por "Enviar", porque o link só navega (FR-3730 da `118`). Sem tarefa,
  não há ação principal; com opcional a enviar, vale a linha da `118` com âncora para o bloco *O que
  falta*.
- **FR-3864**: Depois da ação, em texto corrido e sem moldura, a tela MUST mostrar a frase de
  consequência da FR-1177 da `063`, na condição dela e sem acréscimo, e a **ressalva**:
  - com o Requerimento de Matrícula pedido: *"Esta convocação ainda não é a matrícula: a comissão
    confere o que você enviar e registra o resultado."*;
  - sem ele: *"Esta convocação ainda não é o resultado: a comissão confere o que você enviar e
    registra o resultado."* (D-003).

  Nenhuma outra frase de consequência MUST existir na tela (FR-1177 da `063`).
- **FR-3865**: Com documento pedido e a chamada *aberta*, depois da chamada, a tela MUST mostrar o
  **andamento**, com título de segundo nível *"Andamento"*: as contagens da FR-3727 da `118` em palavra
  e número — *a corrigir* (só quando houver), *a enviar*, *aguardando conferência* e *conferidos* —,
  contando só documentos obrigatórios, e sem o Requerimento (D-004). O andamento MUST NOT ter barra,
  percentual nem frase de conclusão: "100 % enviado" leria como aprovado (FR-3728 da `118`).
- **FR-3866**: Depois do andamento, a tela MUST manter os blocos *O que falta*, *O que você já
  apresentou* e *Sobre esta convocação*, com o conteúdo e as regras da FR-3738, da FR-3739, da FR-3740
  (revista) e da FR-3744 a FR-3746 da `118`.
- **FR-3867**: Com a chamada *encerrada* ou com desfecho vigente, a chamada MUST ter o título da
  FR-3858 e, abaixo dele, os textos do bloco 1 da FR-3741 ou da FR-3742 da `118` (a frase do vencido
  ou do Processo e o resumo do que ficou; ou o rótulo do desfecho, o fundamento, a data e a frase do
  aceite). Nesses estados não há etapa, contagem, ação principal, consequência, ressalva nem
  andamento.
- **FR-3868**: Sem documento pedido na chamada, a tela MUST manter a estrutura da FR-3743 da `118`
  (revista), com três mudanças: o título da FR-3858, o cartão do prazo da FR-3861 no lugar da linha do
  prazo, e a correção da FR-3869. A frase *"Você foi convocada(o)"* sai, porque o título a diz.

#### B. A correção no portal

- **FR-3869**: Quando a convocação vigente sucede outra (`convocacao_anterior`) e a chamada está
  *aberta*, o cartão do prazo MUST dizer, acima da data, *"Convocação corrigida: este é o prazo
  válido."* Os dados do ato MUST ter a linha *"Convocação substituída"*, em todos os estados:
  - comunicada: *"Comunicada em ‹data›, às ‹hora›, com prazo até ‹data›, às ‹hora›. Esse prazo não
    vale mais."*;
  - por publicação: *"Publicada em ‹referência›, com prazo até ‹data›, às ‹hora›. Esse prazo não vale
    mais."*;
  - não comunicada: *"Não comunicada. O prazo registrado era até ‹data›, às ‹hora›, e não vale
    mais."*

  O motivo da correção MUST NOT aparecer no portal (a proteção de dados da `120`). A
  tela MUST NOT dizer *"novo prazo"* nem *"prorrogação"*: a sucessora pode antecipar (FR-3856 da
  `120`).

#### C. Depois do envio

- **FR-3870**: O envio aceito de um documento MUST voltar à tela da convocação na âncora
  `#confirmacao`, e não ao cartão do item. A confirmação MUST ser o primeiro elemento da chamada, antes
  do contexto, focável pelo navegador ao seguir a âncora **sem script**, e dizer:

  | Caso | Confirmação |
  |---|---|
  | envio novo, com tarefa restante | *"Recebemos: ‹documento›, em ‹data›, às ‹hora›. O arquivo aguarda a conferência da comissão."* e *"Próxima tarefa: ‹link para a primeira tarefa da FR-3726›"* |
  | envio novo, sem tarefa restante | a mesma primeira frase, e a frase de conclusão da FR-3728 da `118` no lugar da próxima tarefa |
  | o mesmo arquivo de novo | *"Este arquivo já tinha sido recebido."*, sem próxima tarefa |

  A confirmação MUST NOT dizer *"aceito"*, *"aprovado"*, *"conferido"* nem *"atendido"* (FR-3751 da
  `118`), e cada volta mostra só o seu envio (D-010).
- **FR-3871**: O envio recusado — arquivo ausente, que não é PDF, acima do limite, ou fora do prazo —
  MUST voltar ao cartão do item (`#item-‹id›`), com a recusa **no cartão** e o foco nela, e sem
  confirmação. As frases de recusa são as de hoje; a de prazo, com o núcleo da FR-3748 da `118`.
- **FR-3872**: A tela da convocação MUST carregar os três scripts estáticos que a inscrição já carrega
  — o da escolha do arquivo, o do progresso do envio e o da recusa —, e nenhum script novo. Escolhido o
  arquivo, o cartão MUST dizer o nome dele; durante o envio, o progresso e o aviso de não fechar a
  página que o cartão já traz MUST aparecer. Sem script, o envio continua funcionando, e a
  confirmação da FR-3870 continua recebendo o foco.

#### D. O prazo

- **FR-3873**: A data, a hora, o dia da semana e a contagem do prazo MUST sair de **uma função só**,
  que recebe o vencimento e o instante de referência e responde no **fuso da instalação** — e não no do
  servidor nem em UTC. O portal e o e-mail MUST usar a mesma função. Nada do prazo MUST ser escrito à
  mão ao lado da data.
- **FR-3874**: A contagem MUST seguir, no fuso da instalação, a primeira linha que se aplicar:

  | Situação | Linha abaixo da data |
  |---|---|
  | vencimento passado | nenhuma: é o estado encerrado (FR-3748 da `118`) |
  | comunicação não enviada | nenhuma: o cartão diz só a FR-3749 da `118` |
  | sem vencimento registrado | nenhuma |
  | vencimento hoje, ainda não passado | *"termina hoje, às HHhMM"* |
  | vencimento amanhã | *"‹dia da semana› · termina amanhã"* |
  | vencimento em 2 ou mais dias | *"‹dia da semana› · faltam N dias"*, com N em **dias de calendário** entre a data de hoje e a do vencimento |

  A contagem MUST NOT arredondar para cima, nem contar blocos de 24 horas. O dia da semana é por
  extenso e em minúsculas (*"terça-feira"*).
- **FR-3875**: O prazo MUST ter **um** formato de hora em todas as superfícies do candidato, no portal
  e no e-mail: *"às HHhMM"*, nunca *"às HH:MM"* (`E6`). No corpo do e-mail, o prazo é *"até ‹dia da
  semana›, DD/MM/AAAA, às HHhMM"*; no assunto, só *"até DD/MM"*.

#### E. O acesso

- **FR-3876**: Pedida **por GET** a rota da convocação **sem identidade autenticada na sessão** —
  sessão ausente, vencida, ou identificada sem código provado —, a resposta MUST ser o
  redirecionamento à tela de acesso com o destino igual ao **caminho** pedido, **antes de qualquer
  consulta** pela inscrição, pelo Edital ou pela convocação. A resposta MUST ser a mesma — status,
  destino do redirecionamento, corpo — para identificador real, inventado e de outra pessoa (`S1`,
  `S5`).
- **FR-3877**: Com identidade autenticada que não é a titular, a rota da convocação MUST continuar
  respondendo a mesma recusa que um identificador inexistente (FR-1101 da `059`). As rotas de escrita
  da convocação e as demais rotas do titular MUST continuar como hoje (D-002): nenhum
  redirecionamento leva a praticar ato.
- **FR-3878**: O destino MUST ser validado pelo servidor, em quatro camadas, e o que falhar em
  qualquer uma volta para "Minhas inscrições" (`S2`):
  1. mesmo host e esquema admitido (a validação de hoje);
  2. o caminho resolve para uma rota do portal;
  3. a rota está numa **lista fechada**: a vaga, a página do Edital e a convocação;
  4. o endereço de chegada é **reconstruído** a partir da rota e dos parâmetros dela, sem consulta nem
     fragmento vindos de fora.
- **FR-3879**: Provado o código, a pessoa MUST chegar ao destino da convocação, **sem passar pela
  lista**, também depois do primeiro acesso e da reconciliação de inscrição antiga, que terminam no
  mesmo ponto (`S3`, 3ª decisão do estudo). O destino guardado é só um caminho: a titularidade MUST ser
  conferida de novo ao abrir a convocação, a cada requisição (`S4`). A autenticação continua por
  e-mail e código, e nenhum link autentica (P-001 da `010`).
- **FR-3880**: Quando o destino guardado é a rota da convocação, as telas de acesso — a do e-mail e a
  do código — MUST dizer *"Depois do código, você vai direto para a convocação."*, e a do e-mail MUST
  ter o título *"Entre para ver a sua convocação"*. Elas MUST NOT dizer de quem é a convocação nem de
  qual Edital, e MUST NOT ler o identificador para decidir o texto: a decisão sai só do nome da rota,
  e o texto é o mesmo para identificador real, inventado e alheio (FR-020 e FR-021 da `010`).
- **FR-3881**: Nenhum caminho desta seção MUST escrever por GET além do que já se escreve hoje: o
  destino na sessão e a leitura da convocação na trilha (FR-3613 da `115`). Abrir a convocação MUST
  NOT mover prazo (FR-288b da `019`) (`S8`). Com sessão válida, a convocação abre direto, como hoje
  (`S6`); o link é da inscrição, e por isso abre a **vigente** mesmo vindo da primeira mensagem de uma
  convocação corrigida (`S7`).

#### F. O e-mail

- **FR-3882**: A mensagem individual de convocação MUST sair em HTML **e** em texto puro, os dois
  renderizados de modelos, e o texto puro MUST conter tudo o que o HTML diz, com o endereço completo.
- **FR-3883**: A mensagem inicial MUST ter, de cima para baixo:
  - a identificação institucional por extenso, em texto (FR-3887);
  - o título *"Você foi convocado no Edital ‹NN/AAAA›"* e o Processo;
  - a frase das obrigações (FR-3884) e *"Você envia tudo pela sua área do candidato."*;
  - o prazo em destaque, com o dia da semana, *"contado do envio desta mensagem"* (FR-3875);
  - o link *"Acessar minha convocação"* para a convocação da inscrição, com o endereço por extenso
    abaixo;
  - como entrar: o e-mail na tela de acesso e o código de seis dígitos *"numa mensagem separada"*;
  - a ressalva da FR-3864, na variante do Requerimento, sem afirmar direito à vaga (FR-292c da `019`);
  - o canal de atendimento da unidade;
  - o quadro *"Para a sua segurança"*: o Ifes não pede senha, pagamento nem documentos por e-mail; os
    documentos vão só pela área do candidato; o código só chega quando a pessoa o pede, e não se
    repassa;
  - o rodapé: mensagem automática, não responda, e por que a pessoa a recebe.
- **FR-3884**: O assunto e a frase das obrigações MUST seguir o que a chamada pede de fato, lido da
  lista gravada no ato de convocar e da política do Requerimento (4ª decisão do estudo). *Documento*
  aqui é **documento obrigatório** (D-007):

  | A chamada pede | Assunto | Frase |
  |---|---|---|
  | documento e Requerimento | *"Ifes · Convocação no Edital ‹NN/AAAA›: envie seus documentos até ‹DD/MM›"* | *"Esta convocação pede documentos e o Requerimento de Matrícula."* |
  | só documento | o mesmo | *"Esta convocação pede documentos, que você envia pela sua área do candidato."* |
  | só o Requerimento | *"…: preencha o Requerimento até ‹DD/MM›"* | *"Esta convocação pede o Requerimento de Matrícula, que você preenche pela sua área do candidato."* |
  | nenhum dos dois | *"…: prazo até ‹DD/MM›"* | *"Siga as instruções do Edital dentro do prazo. As instruções estão na sua área do candidato."* |
  | sem vencimento registrado | *"Ifes · Convocação no Edital ‹NN/AAAA›"* | a frase da obrigação, e *"O prazo para atender é o que o Edital publica."* |

  Os primeiros caracteres do assunto MUST trazer a instituição, a palavra "Convocação" e o Edital,
  nessa ordem.
- **FR-3885**: Quando a convocação comunicada sucede outra, e alguma convocação da cadeia de
  correções dela teve mensagem **enviada com sucesso**, a mensagem MUST ser a **da correção**, modelo
  próprio:
  - o assunto *"Ifes · Convocação corrigida no Edital ‹NN/AAAA›: prazo válido até ‹DD/MM›"*, com as
    mesmas variantes de obrigação da FR-3884 no corpo;
  - o título *"Sua convocação no Edital ‹NN/AAAA› foi corrigida"*;
  - logo abaixo, o quadro *"Esta mensagem substitui a que enviamos em ‹data›, às ‹hora›. Aquela
    informava prazo até ‹dia da semana›, ‹data›. O prazo que vale é o desta mensagem."*, com a data,
    a hora e o prazo da **última mensagem enviada com sucesso** na cadeia — que não é a da
    imediatamente anterior quando a desta falhou (D-008);
  - o rótulo do prazo *"Prazo válido para atender"*;
  - o resto como a inicial.

  A mensagem MUST NOT trazer o motivo da correção, nem dizer *"novo prazo"* ou *"prorrogação"*
  (FR-3856 da `120`). Sem nenhum envio com sucesso na cadeia, a mensagem é a inicial (D-008). O
  quadro diz *"enviamos"*, e MUST NOT afirmar que a pessoa recebeu (FR-288a da `019`).
- **FR-3886**: Nenhuma das duas mensagens, em nenhuma das duas partes, MUST conter: nome, CPF,
  telefone, número de inscrição, posição na ordem, nome de documento, número de documentos, motivo de
  pendência, modalidade de reserva, anexo, imagem, fonte ou folha externa, pixel de rastreio,
  parâmetro de campanha, nem endereço que não seja o da convocação e o do canal de atendimento
  (6ª decisão do estudo). O identificador da inscrição só vai no link (FR-1102 da `059`).
- **FR-3887**: A identificação institucional MUST sair da identidade da unidade que já se resolve
  para a mensagem (a da `109` e da `110`): o nome da instituição por extenso e, abaixo, a unidade. Ela
  MUST NOT ser escrita no modelo: uma unidade sem sigla se identifica só pela instituição, como a
  assinatura de hoje. A identificação **não** autentica o remetente (8ª decisão do estudo).
- **FR-3888**: O envio MUST preservar o que já vale: a reserva da chave antes do SMTP e a repetição
  concluída que não envia; a trilha *"enviada"*, e nunca *"recebida"* (FR-288a da `019`); o prazo
  contado do envio gravado, e não do texto (FR-269a da `019`); a contagem do retorno do envio; e a
  convocação **por publicação** sem e-mail nenhum. A FR-084 da `010` MUST continuar com quatro
  situações, e o guardião delas MUST NOT mudar.
- **FR-3889** *(revista em 2026-11-05, pela decisão do usuário sobre a D-009 — a redação anterior está
  ao fim desta alínea)*: A escolha entre a mensagem inicial e a da correção, e a variante de obrigação,
  MUST ser **função só de dados já gravados** no instante do envio: a lista da chamada, a política do
  Requerimento do Edital publicado, as convocações anteriores da cadeia e a comunicação delas.

  A versão exata do modelo usado em cada envio MUST ficar **gravada na própria comunicação emitida**,
  na mesma linha e na mesma transação que registra o resultado:
  - o **nome do modelo**, *inicial* ou *correção*;
  - o **resumo SHA-256** do conteúdo dos dois arquivos, HTML e texto, **efetivamente usados na
    renderização** daquele envio, e não lidos de novo do disco depois, numa composição
    **determinística** dos dois: a mesma ordem, os mesmos rótulos e o mesmo separador, de modo que o
    mesmo par de arquivos dê sempre o mesmo resumo.

  Os arquivos de modelo MUST ser versionados no repositório, nunca gerados nem ignorados, de modo que
  o conteúdo de cada versão gravada continue **recuperável pelo Git**.

  A identificação MUST ser gravada também na tentativa que **falhou**, porque ela diz qual texto se
  tentou enviar. A comunicação por publicação não tem modelo, e fica sem identificação. As comunicações
  gravadas antes da `121` ficam **sem identificação**: nenhuma versão lhes MUST ser atribuída
  retroativamente. Uma mudança posterior nos modelos MUST NOT alterar a identificação já gravada, que
  é append-only como o resto da linha (D-009).

  > **Redação anterior, preservada:** A escolha entre a mensagem inicial e a da correção, e a variante
  > de obrigação, MUST ser **função só de dados já gravados** no instante do envio: a lista da
  > chamada, a política do Requerimento do Edital publicado, as convocações anteriores da cadeia e a
  > comunicação delas. A versão exata do modelo usado em cada envio MUST ser identificável depois; a
  > trilha só ganha coluna se o que já se grava, com o histórico de implantação, não o provar (D-009).
- **FR-3890**: A prévia da correção na gestão, com a forma individual, MUST dizer que a mensagem sai
  de novo com o prazo válido **e dizendo que corrige a anterior** (FR-3844 da `120`, revista). É a
  única mudança na gestão.

#### G. Limites

- **FR-3891** *(revista em 2026-11-05, pela decisão do usuário sobre a D-009 — a redação anterior está
  ao fim desta alínea)*: Esta feature MUST NOT criar tabela, rota, endpoint, comando, papel, estado
  gravado, situação de mensagem, tela ou script novo, nem mudar regra de prazo, de autorização, de
  conferência, de desfecho, de disponibilidade do Requerimento ou de idempotência. A **única** coluna
  e a **única** migration admitidas são as da identificação do modelo em `ComunicacaoEmitida`
  (FR-3889). A tabela MUST continuar append-only, com as duas camadas, e o total de tabelas protegidas
  MUST NOT mudar. A FR-1101 da `059`, a FR-3613 e a FR-3614 da `115` e a FR-3729 da `118` continuam.

  > **Redação anterior, preservada:** Esta feature MUST NOT criar tabela, coluna, migration, rota,
  > endpoint, comando, papel, estado gravado, situação de mensagem, tela ou script novo, nem mudar
  > regra de prazo, de autorização, de conferência, de desfecho, de disponibilidade do Requerimento ou
  > de idempotência. A FR-1101 da `059`, a FR-3613 e a FR-3614 da `115` e a FR-3729 da `118`
  > continuam.
- **FR-3892**: Os textos novos — da tela, das telas de acesso e dos dois modelos de mensagem — MUST
  ficar sob as varreduras de vocabulário da `063`, da `115` e da `118`, inclusive os termos da
  FR-3751 da `118`.

### Key Entities

- **Chamada da convocação** (apresentação, sem persistência): o título por estado, a etapa, o cartão
  do prazo, o resumo e a ação, montados das obrigações da convocação da `118` e da convocação
  vigente. Nasce e morre com a requisição.
- **Prazo apresentado** (apresentação, sem persistência): a data, a hora, o dia da semana e a
  contagem de um vencimento, num instante de referência, no fuso da instalação (FR-3873).
- **Modelo de mensagem** (arquivo): a inicial e a da correção, cada uma em HTML e texto, com as
  variantes de obrigação. O arquivo não se persiste; a identificação dele, sim (FR-3889).
- **Comunicação emitida** (existe; ganha uma coluna): a identificação do modelo usado no envio, com
  o nome e o resumo SHA-256, vazia na publicação e nos registros anteriores à `121` (FR-3889).
- **Convocação, convocação anterior, lista da chamada, política do Requerimento** (existem, não
  mudam): as fontes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1150**: Nos cenários C1, F, G, I1 e corr, a chamada responde pelo próprio texto às perguntas P1
  a P8 da seção 9 do estudo: o título por estado, a etapa (abertos), o prazo ou o estado do prazo, o
  resumo ou o desfecho, e, abertos, a consequência e a ressalva; em P7, o selo *"Conferido"* nos
  cartões; em P8, o link da mensagem. A conferência é uma lista de frases por cenário, verificada pela
  suíte.
- **SC-1151**: Em 100 % dos cenários abertos com tarefa (A, C1, C2, F, J e corr), *"Ver o que preciso
  fazer"* é o primeiro controle do conteúdo depois do resumo, vem antes do andamento na ordem do
  documento, e leva à primeira tarefa da FR-3726 da `118` — a pendente em F e J, a primeira a enviar em
  C1, o Requerimento quando ele é a única.
- **SC-1152**: A 375 × 812, com a fonte padrão, nos mesmos cenários, a ação principal termina dentro
  da primeira tela **com folga de pelo menos uma linha de texto corrido**.
- **SC-1153**: Nos mesmos cenários, e em G e I1, nenhuma tela tem rolagem horizontal a 320 px, com a
  fonte do navegador a 150 % e com zoom de 200 % (WCAG 1.4.10). Nada encolhe para caber.
- **SC-1154**: O dia da semana confere com a data em **todos os dias de um ano**, contra o calendário
  da biblioteca padrão; o vencimento às 23h30 locais mostra a data, o dia e a contagem do dia local; a
  contagem é medida a 23h59 e a 00h01 locais e a uma hora do vencimento, e nunca arredonda para cima;
  *"hoje"* e *"amanhã"* aparecem nas condições da FR-3874; o fuso do teste é fixado, e um caso com outro
  fuso de servidor dá o mesmo resultado.
- **SC-1155**: Zero ocorrências de hora no formato *"HH:MM"* no prazo, no portal e nos dois modelos de
  mensagem, em todas as variantes.
- **SC-1156**: O titular sem sessão, pelo link direto, chega à convocação depois do código **sem passar
  pela lista** em 100 % dos três percursos: sessão vencida, primeiro acesso e reconciliação.
- **SC-1157**: Sem sessão, os três pedidos — identificador real, inventado e de outra pessoa — recebem
  a mesma resposta (status, destino, corpo), com **zero** consultas à inscrição, ao Edital e à
  convocação antes dela; com sessão de outra pessoa, a recusa é igual à de inexistente.
- **SC-1158**: Em 100 % dos destinos de outro host, de esquema estranho, de rota fora da lista
  fechada, ou com consulta e fragmento acrescentados, a chegada é "Minhas inscrições" ou o endereço
  reconstruído, nunca o recebido; nenhum destino pratica ato.
- **SC-1159**: Em todas as variantes das duas mensagens, o texto puro contém cada frase do HTML; o
  HTML tem zero `src=`, zero endereço fora do link da convocação e do canal, e zero ocorrências do
  nome, do CPF e dos nomes de documento da fixture.
- **SC-1160**: A mensagem da sucessora tem o assunto e o título da correção, e diz a data e a hora da
  última mensagem enviada com sucesso na cadeia e o prazo que ela informava — com A enviada, a
  mensagem de B falhada e C sucessora de B, os de A, enquanto os dados do ato de C identificam B —; a
  inicial não tem nenhum dos três; nenhuma das duas tem o motivo; sem envio com sucesso na cadeia, C
  sai como inicial.
- **SC-1161**: A repetição com a mesma chave envia zero mensagens; o guardião das quatro situações da
  FR-084 da `010` passa sem mudança.
- **SC-1162**: Depois do envio aceito, num navegador real, o foco está na confirmação, que nomeia o
  documento, diz *"aguarda a conferência"* e a próxima tarefa, com zero ocorrências de *"aceito"*,
  *"aprovado"*, *"conferido"* e *"atendido"*; depois de uma recusa, o foco está na recusa, no cartão
  do item.
- **SC-1163**: Escolhido o arquivo, o cartão diz o nome dele, e zero vezes *"Nenhum arquivo
  escolhido"*.
- **SC-1164**: A matriz de clientes reais da seção 4 do estudo — Gmail web e app (conta Gmail e de
  outro provedor), Outlook de mesa, Outlook.com e app, Apple Mail e o webmail institucional — está
  preenchida, com uma captura por linha, nas colunas que se aplicam. É critério **humano**, sobre o
  SMTP de homologação, e fecha antes do uso real, junto com a verificação de SPF, DKIM e DMARC.
- **SC-1172**: Em 100 % dos envios individuais, inclusive os que falham, a comunicação emitida grava
  o nome do modelo e um resumo igual ao SHA-256 recalculado dos dois arquivos que renderizaram aquele
  envio. Trocado o conteúdo de um modelo, o envio seguinte grava outro resumo, e o já gravado não
  muda. A publicação e as linhas anteriores à `121` têm zero identificações. Os quatro arquivos de
  modelo estão no índice do Git, e o resumo de um commit histórico se recalcula do `git show` dele.

## Assumptions

- **As fixtures da `118` e o cenário corr do estudo bastam.** A montagem do corr é a do roteiro do
  estudo (`montar.py` com `CORRIGIR=1`), e o plano a traz para as fixtures da suíte.
- **O fuso da instalação é `America/Sao_Paulo`** e o idioma `pt-br`, como nas settings de hoje. A
  função da FR-3873 lê o fuso das settings, e não o assume.
- **A lista da chamada é gravada no ato de convocar** (append-only, `115`), e a política do
  Requerimento sai do Edital publicado: as duas são estáveis depois do envio, e por isso reconstroem a
  variante (FR-3889).
- **Os três scripts são os da inscrição** e funcionam fora dela; se um deles depender do contexto da
  inscrição, o plano diz o que se generaliza, sem script novo.
- **O link da mensagem é absoluto**, montado da mesma base de endereço do portal que a mensagem já
  recebe; com a base vazia, como nas fixtures, a recaída é o caminho relativo, e não a frase *"a área
  do candidato, no endereço do certame"*.

## Proteção de dados (LGPD)

Nenhum dado pessoal novo é coletado, guardado ou enviado, e a mensagem perde, e não ganha, dado.

- **O identificador da inscrição no link** não é credencial nem segredo (`S4`): ele não autoriza nada,
  e quem lê a mensagem encaminhada sabe que a inscrição existe. Nenhuma decisão de acesso depende de
  ele ser difícil de adivinhar, e ele não vai a outro lugar que o link (FR-3886).
- **A tela de acesso não nomeia o Edital nem a pessoa** antes do código (FR-3880), para não revelar a
  quem tem o link encaminhado que ali existe uma inscrição.
- **O motivo da correção** continua fora do portal e da mensagem (FR-3869, FR-3885).
- **O número de documentos** não vai na mensagem: a lista pode variar com a modalidade, e a contagem
  diria algo sobre a cota de quem lê (FR-3886).
- **A identificação do modelo** (FR-3889) não é dado pessoal: o resumo é dos arquivos do modelo, e não
  da mensagem renderizada, e por isso é o mesmo para todas as pessoas que receberam a mesma versão.
- **O computador compartilhado** continua o risco que a 9ª decisão do estudo manda rever com a TI:
  esta spec não o muda nem o agrava, porque o código continua obrigatório para quem não tem sessão.

## Compatibilidade com regras anteriores

| Regra | O que acontece |
|---|---|
| P-001 da `010` (não há link que autentica) | continua: o link leva à convocação, e a entrada é por código |
| FR-084 da `010` (quatro situações) | continua; a correção é a mesma situação da convocação |
| FR-020 e FR-021 da `010` (resposta neutra) | continuam, inclusive na frase de destino (FR-3880) |
| FR-287, FR-288, FR-288a, FR-288b, FR-269a, FR-292c da `019` | continuam (FR-3888, FR-3881) |
| FR-290 da `019` | **revista**: a frase das obrigações, a mensagem da correção, HTML e texto |
| FR-1101 e FR-1102 da `059` | continuam; sem sessão, real, inventado e alheio recebem o mesmo redirecionamento |
| FR-1104 da `059` | **revista**: o endereço passa a ser o da convocação, e o texto, o da FR-290 revista |
| FR-1161 da `062` (destino da página do Edital) | continua, e a lista fechada a inclui |
| FR-1177 da `063` | continua: a consequência é a mesma frase, na mesma condição |
| FR-3613 e FR-3614 da `115` | continuam |
| FR-3726 a FR-3730, FR-3738, FR-3739, FR-3744 a FR-3751 da `118` | continuam |
| FR-3735, FR-3736, FR-3737, FR-3740, FR-3741, FR-3742, FR-3743 e SC-1119 da `118` | **revistas** (D-011) |
| FR-3844 da `120` e a decisão da comunicação da `120` | **revistas**: a prévia diz que a mensagem corrige a anterior |

## Revisões de requisitos anteriores

As redações abaixo **já estão aplicadas** aos arquivos das specs revistas, neste mesmo PR, com a marca
*"revista pela `121` em 2026-11-05"* e a redação anterior preservada ao fim da alínea (D-001). Elas
vigoram com a implementação desta spec. Nenhuma muda regra de prazo, autorização, conferência,
desfecho ou idempotência: mudam o que a mensagem e a tela dizem, em que ordem, e para onde o link
leva.

### `019` — a convocação

**FR-290, nova redação.** A mensagem MUST conter o que fazer, o prazo e o canal de atendimento, e MUST
NOT conter dado da inscrição além do necessário para identificar a chamada. Quando a chamada pede
documento obrigatório ou o Requerimento de Matrícula, a mensagem MUST dizê-lo, sem nomear nem contar
os documentos; a mensagem da sucessora de convocação comunicada MUST dizer que a substitui, com a data
do envio substituído e o prazo que ele informava, e sem o motivo. A mensagem sai em HTML com
alternativa completa em texto, e o assunto segue o que a chamada pede (FR-3882 a FR-3887 da `121`).

> *Redação anterior:* "A mensagem MUST conter o que fazer, o prazo e o canal de atendimento, e MUST NOT
> conter dado da inscrição além do necessário para identificar a chamada."
>
> *Por que mudou:* a mensagem não dizia que havia documentos a enviar (`E1`, a X3 da `118`), e a da
> sucessora era idêntica à original, salvo o prazo (`E4`).

### `059` — o acesso à convocação

**FR-1104, nova redação.** O endereço da mensagem de convocação MUST ser o da convocação da inscrição,
e não "Minhas inscrições"; sem sessão, ele leva ao acesso e, depois do código, à convocação (FR-3876 a
FR-3880 da `121`). O texto da mensagem é o da FR-290 da `019`, revista pela `121`.

> *Redação anterior:* "O endereço da mensagem de convocação MUST continuar sendo 'Minhas inscrições',
> que passa a mostrar a convocação; o texto da mensagem MUST NOT mudar."
>
> *Por que mudou:* a lista entre o e-mail e a convocação é um passo que não serve a ninguém, e o link
> direto sem sessão dava 404 ao próprio titular (`E3`, `A1`; 2ª decisão do estudo).

### `118` — a jornada consolidada do convocado

**FR-3735, nova redação.** Com documento pedido na chamada, a tela da convocação MUST ter, nesta
ordem: a **chamada** (FR-3858 a FR-3864 da `121`), que substitui os blocos *O que fazer agora* e
*Prazo*; o **Andamento**, com a chamada aberta (FR-3865 da `121`); **O que falta** — documentos e
Requerimento; sem tarefa, **Documentos opcionais** (FR-3738); **O que você já apresentou** (FR-3739);
e **Sobre esta convocação** (FR-3740). Os blocos *O que falta* e *O que você já apresentou* MUST NOT
aparecer vazios; *O que falta* aparece, com a chamada aberta, quando houver tarefa **ou** opcional a
enviar; sem nenhum dos dois, ele some, e a chamada diz por quê. O opcional MUST NOT ficar
inalcançável por falta de tarefa (FR-3723).

> *Redação anterior:* cinco blocos, nesta ordem — *O que fazer agora* (FR-3736), *Prazo* (FR-3737),
> *O que falta* (FR-3738), *O que você já apresentou* (FR-3739) e *Sobre esta convocação* (FR-3740) —,
> com as mesmas regras de bloco vazio e de opcional.
>
> *Por que mudou:* a página não dizia o que aconteceu (`T1`, `T2`), e o prazo era uma linha entre
> outras (`T3`).

**FR-3736, nova redação.** O conteúdo do bloco *O que fazer agora* passa à chamada da `121`: a frase de
estado é o resumo (FR-3862 da `121`); o botão é *"Ver o que preciso fazer"*, para a primeira tarefa da
FR-3726 (FR-3863 da `121`), e MUST NOT começar por "Enviar"; a lista das tarefas com âncora e a linha
*"Com a comissão: N documento(s)."* saem, porque os cartões vêm logo depois, na ordem da FR-3726, com o
motivo no cartão, e o andamento diz o que está com a comissão (FR-3865 da `121`). Sem tarefa e com
opcional, continua a linha *"Há documento opcional que você pode enviar, se quiser."*, com âncora
para o bloco *O que falta*.

> *Redação anterior:* o bloco trazia a frase de estado, a lista das tarefas com âncora e motivo, um
> botão *"Ver e corrigir os documentos pendentes"* ou *"Ver os documentos que faltam"*, a linha *"Com a
> comissão: N documento(s)."* e, sem tarefa e com opcional, a linha do opcional.
>
> *Por que mudou:* *"Ver os documentos que faltam"* fazia o Requerimento parecer opcional (`R-4` do
> estudo), e a lista repetia os cartões que vêm logo abaixo.

**FR-3737, nova redação.** O prazo é dito no cartão do prazo da chamada (FR-3861 da `121`): o prazo
único da FR-3747, com o dia da semana e a contagem; com o prazo não iniciado, só a frase da FR-3749,
sem data; sem vencimento, que esta convocação não tem prazo registrado. A frase de consequência da
FR-1177 da `063` vem logo depois da ação principal, na mesma condição (FR-3864 da `121`).

> *Redação anterior:* "O bloco **Prazo** MUST dizer o prazo único da FR-3747; com o prazo correndo, a
> frase de consequência da FR-1177 da `063`, na mesma condição; com o prazo não iniciado, só a frase da
> FR-3749, sem data; sem vencimento, que esta convocação não tem prazo registrado."

**FR-3740, acréscimo.** Quando a convocação vigente sucede outra, o bloco ganha a linha *"Convocação
substituída"*, com a comunicação e o prazo da anterior e *"Esse prazo não vale mais."*, sem o motivo
(FR-3869 da `121`). O resto não muda.

> *Redação anterior:* a mesma, sem este acréscimo.

**FR-3741, nova redação do título.** Com a chamada *encerrada*, o título do bloco 1 passa a ser o
título de primeiro nível da página (FR-3858 da `121`): pelo prazo, *"O prazo desta convocação
terminou"*; pelo Processo, *"O envio pelo portal está encerrado"*. As frases e os resumos continuam os
desta alínea.

> *Redação anterior:* o bloco 1 tinha o título *"O prazo terminou"* (pelo prazo) ou *"O envio pelo
> portal está encerrado"* (pelo Processo), abaixo do título *"Convocação"* da página.

**FR-3742, nova redação do título.** Com desfecho vigente, o título de primeiro nível é *"Resultado da
sua convocação"* (FR-3858 da `121`), e o rótulo *"Resultado registrado"* fica como o da linha do
desfecho. O resto da alínea não muda.

> *Redação anterior:* "o bloco 1 se chama *'Resultado registrado'*, com o rótulo da FR-3750, o
> fundamento e a data", abaixo do título *"Convocação"* da página.

**FR-3743, acréscimo.** Sem documento pedido na chamada, mudam também o título da página (FR-3858 da
`121`), o prazo, que passa ao cartão da FR-3861 da `121`, e a correção dita nele (FR-3869 da `121`); a
frase *"Você foi convocada(o)"* sai, porque o título a diz. O resto da estrutura não muda.

> *Redação anterior:* a mesma, sem este acréscimo — *"Mudam só o formato do prazo, a frase do vencido,
> o rótulo do desfecho … e a frase do aceite."*

**SC-1119, nova redação.** Nos cenários A, C1, C2, F, J e corr: (1) a ação principal é o primeiro
controle do conteúdo depois do título, da etapa, do prazo e do resumo, e vem antes do andamento, dos
formulários e dos dados; (2) não há rolagem horizontal a 320 px, com a fonte a 150 % e com zoom de
200 %; (3) a 375 × 812, com a fonte padrão, a ação está na primeira tela com folga de pelo menos uma
linha de texto. O cartão a corrigir se distingue por um selo em texto, verificável sem cor.

> *Redação anterior:* "A 375 × 812 px, nos cenários A, C1, C2, F e J, o bloco *O que fazer agora*, com
> a contagem e o primeiro link de tarefa, termina dentro da primeira tela; o cartão a corrigir se
> distingue por um selo em texto, verificável sem cor."
>
> *Por que mudou:* um botão que cabe por 1 px não é critério, e com fonte a 150 % ou zoom de 200 % ele
> não cabe, nem deve caber por encolhimento (`R-3` do estudo; seção 2.2).

### `120` — a correção da convocação pela gestão

**FR-3844, nova redação do item da forma de comunicação.** A prévia diz a forma de comunicação do
Perfil e o que ela fará no ato: a mensagem individual sai de novo, **como mensagem da correção**, com
o prazo válido, dizendo que substitui a anterior e sem o motivo (FR-3885 da `121`); por publicação, a
comunicação aguarda a publicação, como hoje.

> *Redação anterior:* "a mensagem individual sai de novo, com o texto da convocação e o prazo novo,
> sem dizer que corrige a anterior (a decisão da comunicação da `120`); por publicação, a comunicação aguarda a publicação, como
> hoje".

**A decisão da comunicação da `120`** (*"A comunicação é a de hoje"*), **o item da mensagem da
sucessora em *"Fica fora"*** (linha 81) e **o de *"Registrado, sem desenvolver"*** (linhas 612–614)
ganham a nota de que a redação própria da mensagem da sucessora foi decidida pelo usuário em
05/11/2026 e está na `121`. A linha da proteção de dados que diz *"a mensagem da sucessora é a de
hoje"* ganha a mesma nota; o motivo continua fora.

## Decisões

**Estado em 2026-11-05.** O usuário aceitou D-001 a D-008, D-010, D-011 e D-012 — a D-008 com o caso
da cadeia de correções decidido por ele. A D-009, aceita sob a condição da prova no plano, foi
decidida depois dela: a prova não fechou, e o usuário escolheu gravar a versão (opção A).

### D-001 — As revisões se aplicam neste PR, e não na implementação

A `118` escreveu as revisões na spec e as aplicou aos arquivos das specs revistas na primeira tarefa da
implementação. Aqui elas vão aplicadas já, com a marca *"revista pela `121` em 2026-11-05"* e a
redação anterior preservada, porque o pedido foi registrá-las em cada spec. A marca diz que elas
vigoram com a implementação da `121`: até lá, quem lê a spec revista lê o que vem, e a redação
anterior diz o que está no código.

### D-002 — O redirecionamento sem sessão vale só para a convocação

O estudo fala em "rota do titular", e cita a convocação e o acompanhamento. O e-mail leva só à
convocação, e a lista fechada de destinos tem só a vaga, o Edital e a convocação: redirecionar o
acompanhamento ao acesso e devolver a pessoa à lista, depois do código, trocaria um 404 por um destino
que não é o pedido. Estender o redirecionamento e a lista ao acompanhamento e ao Requerimento é
incremento próprio, e fica registrado.

### D-003 — A palavra "matrícula" só com o Requerimento de Matrícula

A ressalva do estudo diz *"Esta convocação ainda não é a matrícula"*. Num Edital de bolsista, que não
pede Requerimento de Matrícula, isso é falso. A finalidade da convocação está fora (10ª decisão do
estudo), e o dado que já existe é a política do Requerimento. Por isso a ressalva tem duas variantes,
e a sem Requerimento usa o núcleo neutro do estudo (*"ainda não é o resultado"*). A mensagem usa a
mesma regra.

### D-004 — O andamento conta só documentos obrigatórios

A maquete conta o Requerimento entre os *a enviar* ("5"). As contagens da FR-3727 da `118` contam só
documentos obrigatórios, e o Requerimento enviado não fica *"aguardando conferência"* nem
*"conferido"* no sentido da `115`: contá-lo criaria um estado que ele não tem. O resumo, logo acima,
já o nomeia.

### D-005 — O título por estado absorve o título do bloco 1

Com o título *"O prazo desta convocação terminou"* no topo, o bloco 1 da FR-3741 diria de novo *"O
prazo terminou"*. O título de primeiro nível passa a dizer o estado, e o bloco 1 não repete título.
Com o desfecho, *"Resultado registrado"* continua como rótulo da linha do desfecho.

### D-006 — O rótulo e o formato do prazo continuam os da `118`

A maquete escreve *"Prazo para atender"* e a data sem *"até"*. A FR-3747 da `118` fixou *"Prazo desta
convocação"* e *"até DD/MM/AAAA, às HHhMM"* em todas as telas do candidato, e mudar isso só na
convocação desfaria a unificação que a SC-1121 da `118` mede. O e-mail não é tela do portal, e lá o
rótulo é *"Prazo para atender"*, como na maquete.

### D-007 — No e-mail, "documento" é documento obrigatório

Uma chamada só com documento facultativo não pede documento. Dizer *"envie seus documentos até…"* no
assunto convidaria a um envio que não é obrigação. A variante dela é a do Requerimento ou a de nenhum
dos dois; a página, que mostra o opcional, diz que a pessoa *pode* enviá-lo (FR-3860).

### D-008 — A mensagem da correção cita a última mensagem enviada com sucesso na cadeia

O quadro *"Esta mensagem substitui a que enviamos em…"* só é verdadeiro se houve envio com sucesso.
Sem nenhum na cadeia de correções, nada foi enviado à pessoa, e a mensagem da correção a confundiria:
sai a inicial. Havendo, o quadro cita a **última mensagem enviada com sucesso** — que é a da
imediatamente anterior na correção da correção sem falha, e não é quando a mensagem dela falhou: com A
enviada, a mensagem de B falhada e C sucessora de B, C cita A. Os dados do ato, que são outra coisa,
continuam identificando B como a convocação imediatamente substituída (FR-3844 da `120`). A palavra é
*"enviamos"*: a mensagem não afirma que a pessoa recebeu.

**Aceita pelo usuário em 2026-11-05**, com o caso de A, B e C decidido por ele. A redação proposta
antes descrevia a imediatamente anterior, e mandava C sair como inicial.

### D-009 — A versão do modelo se grava na comunicação emitida

**Decidida pelo usuário em 2026-11-05, sobre o plano.** A prova pedida abaixo foi feita (R-001 da
[pesquisa do plano](research.md)). A variante se reconstrói dos registros. A versão exata do modelo não se
reconstrói pelo histórico de implantação, por quatro razões:

- a linha da ativação é gravada depois do *readiness*, o que deixa uma janela a cada implantação;
- a linha de falha não diz qual versão serviu;
- o arquivo está fora do banco e da trilha;
- nenhum teste o alcança.

Entre as três opções do plano, o usuário escolheu a **A**: uma coluna em `ComunicacaoEmitida`, com o
nome do modelo e o SHA-256 dos arquivos HTML e texto efetivamente usados na renderização. Ela é
gravada também na tentativa falhada, e não se atribui versão aos registros anteriores (FR-3889). A
FR-3891 admite essa coluna e essa migration, e só elas. A 7ª decisão do estudo fica cumprida nos
termos dela: o que se gravava não bastava.

> **Redação anterior à decisão, preservada:**
>
> *D-009 — A versão do modelo se reconstrói, e a trilha não ganha coluna.*
>
> A 7ª decisão do estudo manda acrescentar coluna só se o que se grava não bastar. A escolha do modelo e
> da variante é função de dados append-only gravados antes do envio — a lista da chamada, a política do
> Requerimento do Edital publicado, as convocações anteriores da cadeia e a comunicação delas — e o
> texto é o do código em vigor no instante do envio.
>
> Reconstruir a variante não basta: a auditoria precisa identificar também a **versão exata do modelo**
> usado no envio. O plano MUST provar as duas coisas — um teste que, dados os registros, reconstrói a
> variante, e a evidência de que o histórico de implantação diz qual versão do código estava em vigor
> no instante gravado do envio. Se o histórico não oferecer essa evidência, a coluna volta ao usuário
> como decisão, antes das tarefas.
>
> **Aceita pelo usuário em 2026-11-05 sob essa condição**: a decisão só se fecha com a prova no plano.

### D-010 — A confirmação concorda com "arquivo"

A frase do estudo, *"Ela aguarda a conferência da comissão"*, só concorda com documento de nome
feminino (*"Certidão"*); com *"Histórico escolar"* ela erra. *"O arquivo aguarda a conferência da
comissão"* vale para todos.

### D-011 — As revisões da `118` e da `120` vão além das quatro pedidas

O pedido nomeou a FR-290 da `019`, a FR-1104 da `059`, a FR-3735 e a SC-1119 da `118`, e o ponto da
mensagem da sucessora da `120`. A nova ordem da página não cabe na letra de seis alíneas vizinhas da
`118`: o botão da FR-3736, o bloco de prazo da FR-3737, a linha da substituída na FR-3740, os títulos
da FR-3741 e da FR-3742 e o *"Mudam só"* da FR-3743. E a prévia da `120` (FR-3844) diz hoje, com essas
palavras, que a mensagem não corrige a anterior — o que deixa de ser verdade. Revistas em silêncio,
elas contradiriam a `121`; por isso estão escritas por extenso, com a redação anterior.

**Aceita pelo usuário em 2026-11-05**, como está: as revisões vão além das quatro pedidas e vigoram com
a implementação da `121`.

### D-012 — A identificação institucional vem da unidade

A maquete escreve *"Ifes — Instituto Federal do Espírito Santo"* e *"Cefor · Processos Seletivos"*.
Desde a `109` e a `110`, a unidade é registro da aplicação, e a assinatura da mensagem já sai dela.
Escrever "Cefor" no modelo seria a recaída num Cefor implícito que a `110` eliminou.

## Registrado, sem desenvolver

- **O redirecionamento sem sessão no acompanhamento e no Requerimento**, com a lista fechada estendida
  (D-002).
- **O rótulo "Espécie" nos dados do ato** (`T5`): *"1ª chamada, para vaga inicial"* no lugar de
  *"Espécie: Para vaga inicial"*.
- **O vocabulário por espécie** (seção 3 do estudo): suplência e regularização já são ato gravado, e
  decidem a frase sem campo novo.
- **O título *"O que você já enviou"*** da maquete, no lugar de *"O que você já apresentou"* (FR-3739
  da `118`).
- **A frase de destino nas telas de acesso para o acompanhamento**, se a D-002 for estendida.
