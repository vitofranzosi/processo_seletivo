# Feature Specification: Andamento da seleção — o que está em aberto depois da publicação, e de quem é

**Feature Branch**: `claude/127-andamento-da-selecao-ac9d30`, sobre a `main` em `250efe97`

**Created**: 2026-11-06

**Status**: Implementada e mergeada: B1 (#415), B2 (#416) e o complemento do #417. *Atualizado em 13/11/2026 pela auditoria de consolidação.*

**Status anterior** (até 13/11/2026): Especificada. Dois incrementos, cada um num PR: **B1** (P1, as providências por papel em
"O que fazer agora") e **B2** (P2, o "Andamento da seleção" no lugar do cartão "Classificação").

**Input**: o estudo "O GPS orienta quem conduz a jornada do Edital?" de 06/11/2026 (PR #412, ainda
aberto, em `doc/estudo-orientacao-da-jornada-2026-11-06/`), na versão 3: o relatório, o mapa da
jornada, o mapa das Etapas, a matriz de lacunas, o contrato de derivação, as alternativas e a
proposta, o roteiro de validação e o complemento de generalidade, com os cinco ajustes do §10 dele.
Esta é a "Spec B" do estudo. A "Spec A" é a `126`, que corre em paralelo noutra sessão.

> **Faixa de identificadores.** Esta spec abre em **FR-4050**, **SC-1230** e **UX-230**, e não passa
> do requisito quatro mil cento e noventa e nove, do critério mil duzentos e noventa e nove e do
> identificador de UX duzentos e cinquenta e nove. O teto medido em 06/11/2026 nas `specs/` de todas as worktrees desta
> máquina era o requisito quatro mil e seis, o critério mil duzentos e nove e o identificador de UX
> duzentos e vinte e dois. A `126` reservou a faixa de quatro mil e dez a quatro mil e quarenta e
> nove, de mil duzentos e dez a mil duzentos e vinte e nove, e de UX duzentos e vinte e três a
> duzentos e vinte e nove. As decisões reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Requisito de outra feature pelo identificador e pela feature ("a
> FR-2819 da `104`"); decisão de outra feature pelo assunto e pela feature. As decisões do estudo
> são citadas pelo número dele, por extenso ("a decisão 9 do estudo"); os achados, pelo código dele
> (`J-01`, `G-04`).

---

## Por que esta feature existe

Até a publicação o GPS orienta bem: a trilha de situação, "O próximo ato é seu" e a Validação dizem
o que fazer, quem faz e por que não dá ainda. **Depois da publicação a orientação acaba**, e é aí que
acontece quase todo o trabalho: congelar, observar a semente, sortear, distribuir, avaliar,
consolidar, ordenar, cortar, apurar, divulgar, convocar, conferir e decidir. O cartão "O que fazer
agora" é o mesmo num Edital que espera a semente e num em convocação (`J-01`); o quadro da seleção
está espalhado por marco e por recorte (`J-03`, sete telas para dizer o que falta no 35); o resumo
do cartão "Classificação" não vê o sorteio, as Etapas nem a convocação (`J-04`); e as transições
confirmam sem dizer o próximo passo (`J-08`).

**O domínio já deriva quase tudo; falta um lugar que leia junto.** Esta feature não cria regra,
estado nem máquina de fluxo: ela pergunta às funções que já decidem cada tela de ato e mostra a
resposta em dois níveis — as providências por papel, no cartão que já existe, e o andamento por
Perfil, recolhido, no lugar do cartão "Classificação".

### O que foi reconferido no código em 06/11/2026

Sobre a `main` em `250efe97`, sem refazer a auditoria. Tudo o que o estudo afirma e esta spec usa
foi conferido; os itens marcados **(correção)** mudam a proposta do estudo.

- **O bastão para em *Homologado*.** `acoes.PROXIMO_RESPONSAVEL` só tem as três situações da
  pré-publicação; depois dela o cartão mostra a ação "Inscrições recebidas" como principal e, para
  quem não a tem, "Nenhum ato disponível para seus papéis nesta situação" (`J-01`, `J-09`).
- **A faixa da `104` não tem objeto para a presidência.** `trabalho.do_ator` emite Edital,
  Retificação, recursos e a avaliação **do avaliador** (`_das_avaliacoes`); distribuir e consolidar
  não existem como objeto (`G-04`).
- **O resumo do cartão "Classificação" conta presença de ordem, corte, apuração e publicação**
  (`conducao_do_marco.resumo_dos_marcos`, quatro consultas) e nada do sorteio, das Etapas nem da
  convocação (`J-04`).
- **A ordem dos passos de cada Perfil já é derivada da configuração** por
  `classificacao/domain/jornada.jornada()` (094), função pura que hoje só a prévia da classificação
  chama. Ela precisa de um marco "selecionado", que aqui não tem papel: os estados de simulação que
  ela devolve são ignorados, e só a sequência e os tipos de ponto são lidos.
- **(correção) A `jornada()` põe no começo o marco por sorteio que não enumera Etapa, mesmo quando
  ele declara Etapa de habilitação** (`qualifyingStageId`). Na família S3 a relação é *Depois* da
  Etapa de habilitação, e a sequência ficaria invertida. A composição desta feature reposiciona esse
  marco logo depois da Etapa de habilitação, sem alterar a `jornada()` nem a prévia da `094`
  (D-011).
- **(correção) A Etapa de desempate não enumerada (114) não aparece em `_quem_exige_o_resultado`
  nem é distinguida pela `jornada()`,** mas a ordem a lê (`desempate.etapas_que_a_ordem_le`). Pela
  regra da Etapa sem efeito (decisão 9 do estudo), ela seria mostrada como "nada depende dela", o
  que é falso. A expectativa desta feature a conta como esperada (D-012). O complemento deixava o
  ponto "a verificar" (§5).
- **A expectativa de cada Etapa já é declarada num lugar:** `editais/domain/validation.
  _quem_exige_o_resultado` diz, para a publicação, quais Etapas um marco consome (enumerada e não
  porta, governada pelo corte, de habilitação do sorteio). A derivação a pergunta, e acrescenta a
  progressão e o desempate (D-012).
- **O panorama da Etapa é por Etapa sobre o Edital inteiro** (`prontidao.panorama_da_etapa`), e é a
  mesma leitura que a tela da distribuição faz, com `resumo_da_etapa(panorama=…)`. A quebra por
  Perfil sai do mesmo panorama (`estados`, por inscrição) cruzado com o Perfil de cada inscrição, numa
  consulta para o Edital (D-013).
- **No marco por pontuação, nada recusa a ordem sem nenhuma avaliação** (`emitir_ordem`; o `G-01`,
  que é da `126`). Esta feature não muda a regra: ela diz *Depois* das Etapas enumeradas, e não
  *Pendente*.
- **No Perfil com Etapa governada pelo corte, a apuração antes da consolidação dela é aceita pelo
  domínio,** mas conta como habilitado só quem tem `HABILITADA` vigente nela, e por isso apuraria
  ninguém. A derivação diz *Depois* da Etapa governada, sem recusar nada (D-014).
- **A convocação tem quatro estados no domínio** (`convocacao/domain/prazo.estado`), e a tela da
  convocação decide o que oferecer por três prévias (`fluxo.previa_dos_titulares`,
  `previa_dos_vencidos`, `previa_das_pendentes`) sobre a mesma `leitura_do_recorte`. A derivação lê
  as mesmas.
- **O sorteio decide a tela por `previa.recortes_do_marco`**: congelada, projetados, inscrições em
  curso, congelamento inviável, ocorrência da vez, recusa da ocorrência, sorteio vigente e
  diagnóstico da relação. A derivação lê a mesma função.
- **O resultado definitivo pendente é a regra do relatório** (`DEFINITIVO_NAO_PUBLICADO`, da `099` e
  da `113`), e a publicabilidade da definitiva é `publicabilidade.aferir(natureza="DEFINITIVA")`.

### A matriz de compatibilidade (o complemento, §8, conferido)

As peças combináveis do GPS dão sete famílias. Cada uma está coberta pelos dois níveis desta
feature, e o critério de aceitação cobre uma por linha (SC-1237).

| Família | Configuração | No banco | Atos e dependências | Nível 1 | Nível 2 |
|---|---|---|---|---|---|
| **S1** | Sorteio que não enumera Etapa; Etapas declaradas que nada consome | 35, 57 | inscrições → relação → semente → sorteio → corte → apuração → resultado → convocação | providências do sorteio, da ordem em diante e da convocação; as Etapas como "Atenção" | relação, semente e sorteio no lugar da ordem; as Etapas com "sem efeito no GPS" |
| **S2** | Sorteio que enumera Etapa (visibilidade e recurso, não ordem) | 72, 26 | idem S1; a Etapa enumerada é esperada só se consolidável | idem, mais a Etapa, se consolidável; "Atenção" se não (a decisória não eliminatória do 72) | idem, com a coluna da Etapa |
| **S3** | Sorteio com Etapa de habilitação | nenhum; cenário composto | Etapa de habilitação → relação → … | distribuir, avaliar e consolidar a habilitação; a relação *Depois* dela | a Etapa antes do marco (D-011) |
| **P1** | Pontuação que enumera Etapas pontuadas | 91 | Etapas → ordem → corte → apuração → resultado → convocação | distribuir, avaliar e consolidar; a ordem *Depois* das Etapas | as Etapas antes da ordem |
| **P2** | Pontuação com Etapa governada pelo corte | 51 | … → ordem → corte → Etapa governada → apuração → convocação | idem P1; a Etapa governada *Depois* do corte; a apuração *Depois* da governada | coluna "governada pela faixa" depois do corte |
| **P3** | Vários marcos no Perfil | nenhum; cenário composto | Etapas → marco 1 → corte → Etapa governada → marco 2 | idem, por marco | um grupo de colunas por marco |
| **CR** | Qualquer das anteriores, sem vaga imediata | 91, 72, 51 | sem linha no quadro: apuração e convocação não se aplicam | nada a apurar nem a convocar | *Não se aplica*, com a razão |
| **Mista** | Perfis de famílias diferentes no mesmo Edital | 51 | cada Perfil com a sua sequência | providências de famílias diferentes na mesma lista | uma linha por Perfil, cada uma com a sua composição |

**Incompatibilidades encontradas e corrigidas antes do plano**: a posição do marco de S3 (D-011) e a
Etapa de desempate (D-012). Nenhuma outra: as sete situações servem às duas famílias de ordem, e o
nível 1 não depende de colunas.

### O que esta spec cobre, e o que fica fora

**Cobre**: uma derivação de leitura do andamento do Edital publicado; as providências por papel em
"O que fazer agora" (B1); a trilha de situação que sai depois da publicação; os objetos da
presidência (distribuir, consolidar); a Etapa que nada consome como "Atenção"; o "Próximo nesta
lista" nas mensagens de sucesso das telas de ato (B1, feito por último, depois da `126`); o
"Andamento da seleção" no lugar do cartão "Classificação" (B2); o custo fixo por Edital; os testes de
derivação, de coerência com o backend, de autorização, de transição e de orçamento.

**Fica fora**: tudo da `126` (sucessão recolhida, *Não se aplica* na condução do marco, o rótulo da
convocação, o aviso de congelamento, a mensagem da Caixa e o `G-01`); a condução do marco estendida
e a contagem na Lista (P3 do estudo); barra de fases, percentual, "próximo passo" único, notificação;
estado persistido, tabela, migration; mudança de regra, de permissão, de vigência ou de quem vê o quê
no nível 2; a Agenda; a matrícula; o `G-05` e o `G-07`, que são de configuração e de governança.

---

## Clarifications

### Session 2026-11-06

As perguntas foram respondidas no pedido da feature e pelas decisões do estudo, adotadas como ele as
recomenda, salvo onde o código as contradisse (marcado). Não houve pergunta aberta ao usuário.

- Q: Uma spec ou duas? → A: Uma, com dois incrementos e dois PRs: B1 (o nível 1) e B2 (o nível 2).
  Os incrementos escalonam níveis, e não famílias (decisão 6 do estudo, opção c; D-001).
- Q: A trilha de situação continua depois da publicação? → A: Não; o selo ao lado do título diz a
  situação (decisão 1 do estudo, opção c; D-002).
- Q: O que entra nas providências? → A: Só o que tem caminho no GPS. A matrícula é nota fixa no
  nível 2 quando toda convocação de um Perfil tem desfecho (decisão 2 do estudo, opção a; D-003).
- Q: Quem vê cada nível? → A: O nível 1, todo papel que abre o Edital; o nível 2, quem hoje vê o
  cartão "Classificação" (decisão 3 do estudo, opção c; D-004).
- Q: A Lista muda? → A: Não (decisão 4 do estudo, opção a; D-005).
- Q: Os nomes? → A: O nível 1 continua "O que fazer agora"; o nível 2 é "Andamento da seleção"
  (decisão 5 do estudo; D-006).
- Q: *Depois* no lugar de *Falta* na condução do marco? → A: No andamento, sim, desde já; na tela de
  condução do marco, fica para o P3, junto da condução estendida (decisão 7 do estudo; D-008).
- Q: O preliminar é feito ou pendente? → A: Segue a pendência que já existe
  (`DEFINITIVO_NAO_PUBLICADO`) (decisão 8 do estudo, opção a; D-009).
- Q: A Etapa que nada consome? → A: Mostrada sem ser cobrada: "Atenção" no nível 1, "sem efeito no
  GPS" no nível 2 (decisão 9 do estudo, opção b; D-010).
- Q: E as transições, que tocam os templates da `126`? → A: Por último, sobre a `126` mergeada ou
  sobre a branch dela (D-015).

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Quem conduz sabe o que é seu, e o que espera o mundo (Priority: P1) — B1

Carla é gestora e conduz o Edital 35/2026, por sorteio. Ela abre o detalhe e lê, logo abaixo do
título, "O que fazer agora · 2 providências em aberto · 1 é sua": primeiro "Emitir a comunicação —
Cefor · Ampla concorrência", como link para a convocação daquela lista; depois "Quem publica
resultado: publicar o resultado definitivo — Cefor"; e, abaixo, "Atenção: Análise da documentação e
Verificação da autodeclaração estão declaradas no Edital, e nenhum ato do GPS depende do resultado
delas". O Polo Vitória, sem inscrito, não aparece. No 57, as duas providências dela são de Perfis
diferentes e em situações diferentes: uma lista aguarda a extração, a outra precisa congelar.

**Why this priority**: é o `J-01`, o achado central do estudo. Sem isto, a pessoa precisa saber o
rito de cor.

**Independent Test**: no 35, 57 e 51 do banco de estudo, quem conduz lê as providências na ordem
fixa, e cada uma leva à tela do ato.

**Acceptance Scenarios**:

1. **Given** o 35 publicado, com uma convocação sem comunicação na ampla do Cefor, **When** quem
   conduz abre o detalhe, **Then** a primeira providência é a dele, "Emitir a comunicação", e leva à
   convocação daquela lista.
2. **Given** o mesmo Edital, **When** quem conduz lê o cartão, **Then** a providência de quem publica
   resultado aparece com o papel no lugar do link, e o Polo Vitória não aparece como providência.
3. **Given** o 57, com a relação de Design congelada e a extração por acontecer, e a de Tecnologias
   não congelada, **When** quem conduz abre o detalhe, **Then** lê "Congelar a relação —
   Tecnologias Digitais" como sua e "Observar a extração — Design Educacional" como aguardando, com a
   data declarada.
4. **Given** um Edital publicado sem nenhuma providência em aberto, **When** qualquer papel abre o
   detalhe, **Then** o cartão diz "Nada em aberto" e por quê, e não "Nenhum ato disponível".

---

### User Story 2 — A presidência de um Edital por pontuação vê as Etapas (Priority: P1) — B1

Paulo preside a comissão do 91/2026, por pontuação, e é avaliador alocado da Prova de Títulos. No
detalhe ele lê "Avaliar 12 inscrições — Prova de Títulos" como sua, "Distribuir 12 inscrições sem
avaliador — Prova de Desempenho Didático" como sua, e "Atenção: Entrevista está declarada no Edital,
e nenhum ato do GPS depende do resultado dela". A ordem do marco não aparece como providência: ela
espera as duas Etapas.

**Why this priority**: o complemento de generalidade condicionou a aprovação a que o nível 1 sirva a
todas as famílias, e o `G-04` mostrou que a presidência não tinha objeto de trabalho.

**Independent Test**: no 91, a presidência lê as duas providências, a "Atenção" da Entrevista, e
nenhuma providência de ordem.

**Acceptance Scenarios**:

1. **Given** o 91, com 12 inscrições sem avaliação na Prova de Títulos atribuídas à presidência,
   **When** ela abre o detalhe, **Then** lê "Avaliar" como sua, levando à mesa da Etapa.
2. **Given** a Prova de Desempenho Didático sem avaliador, **When** a presidência abre o detalhe,
   **Then** lê "Distribuir" como sua, levando à distribuição da Etapa.
3. **Given** uma Etapa com inscrições prontas para consolidar, **When** a presidência abre o
   detalhe, **Then** lê "Consolidar N prontas" como sua, levando à distribuição.
4. **Given** as Etapas enumeradas ainda não consolidadas, **When** a presidência abre o detalhe,
   **Then** a ordem do marco não é providência *Pendente*.

---

### User Story 3 — Cada papel sabe a quem cabe o resto (Priority: P1) — B1

Beatriz publica resultados. No 35 ela lê "Publicar o resultado definitivo — Cefor" como sua, e as
providências de quem conduz com o papel nomeado. Ana elabora: ela lê as providências em aberto, todas
de outros papéis, sem link para telas que não abre, e não vê o nível 2. O auditor vê as providências
de quem conduz como de outro papel, porque lê as telas e não pratica os atos. O julgador lê "Decidir
N recursos" como sua.

**Acceptance Scenarios**:

1. **Given** o 35 com o definitivo publicável, **When** quem publica resultado abre o detalhe,
   **Then** lê a providência como sua, com link à prévia de publicação, e o cartão não diz "Nenhum
   ato disponível".
2. **Given** o mesmo Edital, **When** quem elabora abre o detalhe, **Then** lê as providências como
   de outros papéis, sem link, e não vê o "Andamento da seleção".
3. **Given** um auditor, **When** abre o detalhe, **Then** nenhuma providência de quem conduz é dita
   "sua".
4. **Given** recursos aguardando decisão, **When** quem julga abre o detalhe, **Then** lê "Decidir
   recursos (N)" como sua.

---

### User Story 4 — O que a orientação diz, o backend confirma (Priority: P1) — B1

Toda providência *Pendente* da pessoa abre uma tela que oferece aquele ato habilitado; toda
*Aguarda* ou *Impedido* abre uma tela que o recusa, ou o anuncia como impossível, pela mesma razão.
Se as duas divergirem, a derivação está errada.

**Acceptance Scenarios**:

1. **Given** cada Edital do cenário de teste e cada papel, **When** a derivação diz *Pendente* para a
   pessoa, **Then** o GET da tela de destino, com a identidade daquela pessoa, mostra o controle do
   ato habilitado.
2. **Given** a derivação diz *Aguarda* ou *Impedido*, **When** a tela é aberta, **Then** ela mostra a
   mesma razão, ou não oferece o ato.

---

### User Story 5 — O andamento da seleção, por Perfil, recolhido (Priority: P2) — B2

No lugar do cartão "Classificação", Carla lê "Andamento da seleção": a linha das inscrições ("Encerradas
em 20/10/2026 · 14 enviadas"), e uma linha por Perfil, recolhida, com o resumo em palavras ("Por
sorteio · 3 listas · sorteadas, cortadas e apuradas · resultado preliminar · convocação: 1
comunicação a emitir"). Aberta, a linha do Cefor mostra a matriz daquele Perfil: uma linha por lista
e uma coluna por ponto da jornada — Relação, Semente, Sorteio, Corte, Apuração, Resultado, Convocação
e, no fim, as duas Etapas "sem efeito no GPS". No 91 a matriz começa pelas Etapas, que ocupam todas as
listas, e a ordem vem depois delas. O Polo Vitória é uma linha só: "Não se aplica: nenhuma inscrição
enviada".

**Why this priority**: é o `J-03` e o `J-04`, o quadro espalhado. Vem depois da B1 porque a matriz
não é o lugar onde se descobre o que fazer (`R9b` do estudo).

**Acceptance Scenarios**:

1. **Given** o 35, **When** quem conduz abre o detalhe, **Then** o "Andamento da seleção" está no
   lugar do cartão "Classificação", com uma linha por Perfil, recolhida, e o resumo em palavras.
2. **Given** o 91, **When** a presidência abre o Perfil, **Then** as colunas vêm da configuração: as
   Etapas antes da ordem, e nenhuma coluna de relação, semente ou sorteio.
3. **Given** o 51, **When** quem conduz abre o Perfil P2, **Then** a Etapa governada aparece depois
   do corte, agrupada como "governada pela faixa".
4. **Given** a matriz mais larga do que a moldura, **When** a página é lida a 1280 px ou a 375 px,
   **Then** a matriz rola dentro da moldura, e a página não rola de lado.
5. **Given** quem elabora, **When** abre o detalhe, **Then** não vê o "Andamento da seleção", como
   não via o cartão "Classificação".

---

### User Story 6 — Depois do ato, a tela diz o próximo passo da lista (Priority: P2) — B1, por último

Carla emite o corte da ampla do 26. A mensagem diz "Corte emitido." e, logo abaixo, "Próximo nesta
lista: apurar a ocupação" com o link, e "Ainda neste marco: a lista PPP espera a relação". O mesmo
nas mensagens de sucesso da ordem, da relação, da semente, do sorteio, da apuração, da convocação, da
comunicação e da conferência.

**Acceptance Scenarios**:

1. **Given** o corte recém-emitido, **When** a tela do corte volta com a mensagem de sucesso,
   **Then** ela diz o próximo passo daquela lista pela mesma derivação, e o que falta nas outras
   listas do mesmo marco.
2. **Given** um ato depois do qual nada falta na lista, **When** a mensagem aparece, **Then** ela diz
   que nada mais está em aberto nesta lista, e não inventa passo.

---

### Edge Cases

Cada caso é requisito, e tem teste (rastreabilidade).

- **Perfil sem inscrito**: nenhuma providência; no nível 2, uma linha só, *Não se aplica*, com a
  razão. Se algum ato já existir nele (ordem vazia emitida), ele aparece como *Feito*, "ninguém
  concorreu".
- **Lista não constituída** (sem inscrito naquela lista, num marco por sorteio): a cadeia inteira da
  lista é *Não se aplica* — congelar seria recusado —, e nenhum gesto é sugerido.
- **Dependência futura**: a extração declarada para depois de hoje é *Aguarda*, com a data; a Etapa
  governada antes do corte é *Depois*; a ordem por pontuação antes das Etapas enumeradas é *Depois*.
- **Operação bloqueada**: congelar hoje condenaria o sorteio, a cadeia de substituição foi consumida,
  a regra da Etapa é insuficiente, a forma de convocação não foi declarada — *Impedido*, com a frase
  da tela do ato e quem resolve (quase sempre quem elabora Retificações).
- **Concurso indisponível**: a falha de acesso à fonte não muda a situação (nada foi gravado); a
  semente continua *Pendente*.
- **Ato obsoleto**: ordem, corte, apuração ou publicação que o sistema sabe estar para trás é
  *Obsoleto*, e é providência de quem refaz.
- **Retificação**: em curso, ela é providência de quem age nela (a `103`); publicada, o que ela
  tornou obsoleto aparece *Obsoleto*.
- **Resultado ainda não publicável**: o definitivo que espera a janela recursal ou um recurso é
  *Aguarda*, com a razão e a data.
- **Convocação com prazo futuro**: o prazo em curso é *Aguarda* até o vencimento; o prazo não iniciado
  é *Pendente* (emitir a comunicação); o vencido é *Pendente* (registrar o não atendimento).
- **Listas em estágios diferentes**: cada lista tem as suas providências; o Edital não tem "a etapa
  atual".
- **Nova chamada**: vaga a ocupar com gente na fila e nenhum titular a convocar é *Pendente*
  condicional ("chamar a próxima da fila"); fila esgotada com vaga a ocupar e marco que corta é
  "pedir a faixa seguinte" na ocupação.
- **Inscrições em curso**: congelar e distribuir *Aguarda* o fim do período, com a data.
- **Mais de cinco providências**: as cinco primeiras e "mais N", sem página nova.
- **Mesmo ato pendente em várias listas do mesmo marco**: uma providência, com as listas nomeadas.
- **Segregação**: quem a segregação impede não é "você"; a razão é dita.
- **Pessoa de outro escopo**: o detalhe já é 404; nada muda.
- **Edital encerrado**: as providências que continuam (convocação aberta, definitivo) aparecem; o
  Encerrar nunca é providência.
- **Edital em elaboração, em revisão, homologado ou cancelado**: nada desta feature aparece; o cartão
  é o de hoje.
- **Etapa enumerada por marco de sorteio que não consolida** (decisória não eliminatória do 72):
  "Atenção", e não providência.
- **Etapa só de desempate**: esperada, porque a ordem a lê.
- **Avaliador alocado sem inscrição atribuída**: não é providência dele (a regra da `104`).

---

## Requirements *(mandatory)*

### Functional Requirements

#### A derivação (os dois incrementos)

- **FR-4050**: O sistema MUST ter uma derivação de leitura do andamento do Edital publicado ou
  encerrado que, a partir das funções que já decidem cada tela de ato, devolve para cada Perfil a
  situação de cada ponto da jornada em cada lista, e o conjunto de providências do Edital. Ela MUST
  NOT autorizar, praticar nem gravar coisa alguma, e MUST NOT ter estado persistido, tabela nem
  migration.
- **FR-4051**: A derivação MUST NOT escolher um próximo passo único. Ela devolve um conjunto; a
  ordem de apresentação é regra fixa da tela (FR-4082).
- **FR-4052**: Cada ponto de cada lista MUST estar numa de sete situações de apresentação — *Feito*,
  *Obsoleto*, *Pendente*, *Aguarda*, *Impedido*, *Depois*, *Não se aplica* —, e a ausência de ato
  MUST NOT ser apresentada como pendência: uma célula sem ato vigente é *Depois*, *Aguarda*,
  *Impedido*, *Não se aplica* ou *Pendente*, pela regra do ato (FR-4060 a FR-4076).
- **FR-4053**: A derivação MUST manter separadas: a situação; a aplicabilidade e a expectativa
  (esperada, condicional, facultativa, sem efeito); a dependência (o ponto anterior que falta); o
  responsável (o papel); a permissão (se a pessoa que olha pratica o ato); a disponibilidade (se a
  tela do ato o oferece agora); e o prazo (desde quando, até quando).
- **FR-4054**: Cada providência MUST ter natureza, onde (Perfil, marco, lista ou Etapa), o ato com o
  verbo da tela, a situação, o responsável, a expectativa, a razão (para *Aguarda*, *Impedido* e
  *Obsoleto*), o caminho até a tela do ato (nunca a confirmação) e, quando houver, desde quando e até
  quando.
- **FR-4055**: A providência MUST ser "sua" só se a pessoa que olha pratica o ato pela mesma porta que
  a tela do ato aplica (a gestão da comissão, `resultado:publicar`, `recurso:julgar`, a alocação de
  avaliação, a da conferência, `retificacao:elaborar`), e a segregação de funções MUST valer como no
  bastão. Quem só consulta (auditoria) MUST NOT ler providência de condução como sua.
- **FR-4056**: O caminho da providência MUST existir só para quem abre a tela de destino; para quem
  não abre, a providência nomeia o papel, e não oferece link.
- **FR-4057**: A derivação MUST reaproveitar os objetos de trabalho da `104` para recurso, Retificação
  e avaliação, sem regra paralela, e MUST acrescentar os objetos da presidência da comissão:
  distribuir e consolidar.
- **FR-4058**: A facultativa (aviso aos candidatos, definição dos documentos da formalização) MUST
  NOT entrar nas providências.
- **FR-4059**: O Encerrar MUST NOT ser providência; continua sendo ação do cartão.

#### A expectativa e as Etapas de avaliação

- **FR-4060**: A expectativa de cada Etapa MUST vir da ligação dela com os marcos do conteúdo vigente:
  esperada se for enumerada e consolidável por marco de pontuação, governada pelo corte, de
  habilitação do sorteio, lida pelo desempate de um marco, ou consolidável e anterior, pela ordem, a
  uma Etapa que um ato consome (D-019); enumerada por marco de sorteio, esperada só se consolidável;
  sem nenhuma dessas ligações, "sem efeito no GPS".
- **FR-4061**: A Etapa "sem efeito no GPS" MUST NOT gerar providência; MUST aparecer no nível 1 como
  "Atenção", que diz que ela está declarada no Edital e que nenhum ato do GPS depende do resultado
  dela, e no nível 2 como célula "sem efeito no GPS".
- **FR-4062**: A Etapa esperada MUST ter as situações lidas do mesmo panorama e do mesmo resumo que a
  tela da distribuição lê: *Aguarda* com as inscrições em curso; *Impedido* com a regra da Etapa
  insuficiente ou o corte que a governa obsoleto; *Depois* se governada e sem corte vigente que a
  alimente; *Não se aplica* sem participante; *Pendente* "distribuir" com inscrição sem avaliador
  suficiente, "avaliar" com avaliação a concluir, "consolidar" com inscrição pronta; *Obsoleto* com
  reavaliação determinada; *Feito* com todos os participantes consolidados. Uma Etapa MAY ter mais de
  uma providência ao mesmo tempo.
- **FR-4063**: "Avaliar" MUST ser providência da pessoa só quando ela é avaliadora alocada com
  inscrição pendente (a carga de Minhas Etapas); para os demais, MUST nomear "os avaliadores alocados".
- **FR-4064**: A contagem MUST acompanhar a providência da Etapa ("12 sem avaliador suficiente",
  "8 de 12 consolidadas"), e não virar estado novo.

#### O sorteio

- **FR-4065**: A relação de cada lista MUST ser: *Depois* se o método declara Etapa de habilitação que
  não está feita; *Não se aplica* se ninguém a projetaria e ela não está congelada; *Aguarda* com as
  inscrições em curso; *Impedido* se congelar hoje condenaria o sorteio; *Pendente* "congelar a
  relação" se não congelada; *Obsoleto* se o diagnóstico diz que a relação congelada nunca sorteará;
  *Feito* nos demais casos.
- **FR-4066**: A semente do marco MUST ser: *Depois* sem relação congelada; *Feito* com a ocorrência
  da vez observada; *Impedido* com a cadeia de substituição consumida; *Aguarda* se o instante
  declarado ainda não chegou, com a data; *Pendente* "observar a extração" nos demais casos — e a
  falha de acesso à fonte MUST NOT mudar a situação.
- **FR-4067**: O sorteio de cada lista MUST ser: *Não se aplica* se a relação não se aplica;
  *Depois* sem relação congelada ou sem semente; *Impedido* se a extração é anterior ao congelamento;
  *Pendente* "realizar o sorteio" sem sorteio vigente; *Feito* ou *Obsoleto* com sorteio vigente.

#### A ordem por pontuação e o que vem depois da ordem

- **FR-4068**: A ordem do marco por pontuação, em cada lista, MUST ser *Depois* enquanto alguma Etapa
  que ela lê (enumerada ou de desempate) não estiver feita para o Perfil; *Pendente* "emitir a ordem"
  sem ato vigente e com as Etapas feitas; *Feito* (com a nota "ninguém concorreu" quando vazia) ou
  *Obsoleto* com ato vigente.
- **FR-4069**: O corte, a apuração e a publicação de cada lista MUST partir do indicador da condução
  do marco (049), na forma que ele estiver na `main`: *Feito*, *Obsoleto* e *Não se aplica* como ele
  diz; a falta, *Depois* se o ponto anterior da lista não estiver feito, e *Pendente* se estiver.
- **FR-4070**: No Perfil cujo corte governa uma Etapa, a apuração e a convocação MUST ser *Depois*
  enquanto a Etapa governada tiver trabalho em aberto para o Perfil (D-014); no marco que corta, a
  apuração MUST ser *Depois* enquanto o corte da lista não estiver vigente (D-018).
- **FR-4071**: O resultado de cada lista MUST ser *Pendente* de quem publica resultado quando nunca
  divulgado ou defasado; publicado só como preliminar, MUST ser *Pendente* se a definitiva é
  publicável agora e *Aguarda* se a definitiva espera a janela recursal ou um recurso, com a razão e
  a data (D-009).
- **FR-4072**: A célula sem ordem na publicação MUST ser *Depois*, e não *Falta*, no andamento; a
  tela de condução do marco não muda nesta feature (D-008).

#### A convocação

- **FR-4073**: A convocação de cada lista MUST ser *Depois* sem apuração vigente ou com a apuração
  obsoleta (a apuração é que é a providência); *Impedido* sem forma de comunicação declarada; e, com
  apuração vigente, MUST ler as mesmas prévias que a tela da convocação lê: titulares a convocar,
  comunicações a emitir e vencidas sem desfecho são *Pendente* de quem conduz; prazos em curso são
  *Aguarda* até o vencimento mais próximo.
- **FR-4074**: Vaga a ocupar com gente na fila e nenhum titular a convocar MUST ser *Pendente*
  condicional "chamar a próxima da fila"; vaga a ocupar com a fila esgotada, com corte vigente na
  lista e com linha no quadro, MUST ser *Pendente* condicional "pedir a faixa seguinte", com o
  caminho da ocupação (D-018).
- **FR-4075**: Documento apresentado e não conferido MUST ser *Pendente* "conferir documentos", de
  quem conduz ou de quem está alocado à conferência daquele Perfil.
- **FR-4076**: Sem vaga a ocupar e sem convocação, a convocação MUST ser *Não se aplica*; sem vaga a
  ocupar e com toda convocação desfechada, *Feito*.

#### O nível 1: "O que fazer agora" depois da publicação (B1)

- **FR-4080**: No Edital publicado ou encerrado, "O que fazer agora" MUST começar pelas providências em
  aberto do Edital (*Pendente*, *Obsoleto*, *Aguarda* e *Impedido*), com uma contagem e de quem são
  ("2 providências em aberto · 1 é sua"), sem percentual e sem fase.
- **FR-4081**: O nível 1 MUST ser visível a todo papel que abre o detalhe do Edital; ele não mostra
  candidato, nota nem convocado, só atos, contagens e papéis.
- **FR-4082**: A ordem MUST ser fixa: primeiro as da pessoa, *Pendente* ou *Obsoleto*, as que têm
  prazo pelo prazo mais próximo e depois pela espera mais antiga; depois as de outros papéis,
  agrupadas por papel; depois as que aguardam ou estão impedidas, com a razão. *Não se aplica* MUST
  NOT aparecer no nível 1.
  *Revista pela `153` em 11/11/2026:* dois papéis novos, quem administra os acessos da unidade e o
  setor da formalização, ficam depois dos de hoje, nessa ordem (FR-6114 da `153`).
- **FR-4083**: O nível 1 MUST mostrar até cinco providências e "mais N", que mostra as demais na
  própria página.
- **FR-4084**: A providência da pessoa MUST ser link com o verbo da tela do ato; a de outro papel MUST
  nomear o papel e não ter link; a que aguarda ou está impedida MUST dizer a razão com a frase da tela
  do ato, e, no impedimento, quem o resolve.
- **FR-4085**: O mesmo ato, na mesma situação e do mesmo responsável, em várias listas do mesmo marco
  ou em vários marcos da mesma Etapa, MUST ser uma providência só, com as listas nomeadas.
- **FR-4086**: "O que fazer agora" MUST NOT dizer "Nenhum ato disponível" quando há providência da
  pessoa (estende a FR-2819 da `104`). Sem providência em aberto, MUST dizer "Nada em aberto" e o
  porquê.
- **FR-4087**: As Etapas sem efeito MUST aparecer no pé do nível 1, como "Atenção", separadas das
  providências e sem contar nelas.
- **FR-4088**: As ações de hoje (Inscrições, Relatório, Formalização, Encerrar, Cancelar, Retificar)
  MUST continuar no cartão, sem nenhuma cheia quando a pessoa tiver providência: a ação principal
  passa a ser a providência dela.
- **FR-4089**: Depois da publicação, a trilha de situação MUST NOT aparecer, e o aviso de conteúdo
  imutável MUST ocupar uma linha no pé do cartão (D-002).

#### As transições: "Próximo nesta lista" (B1, por último)

- **FR-4090**: A mensagem de sucesso do corte, da ordem, da relação, da semente, do sorteio, da
  apuração, da convocação, da comunicação e da conferência MUST dizer, pela mesma derivação, o
  próximo passo daquela lista (a primeira providência em aberto dela) e o que falta nas outras listas
  do mesmo marco.
- **FR-4091**: Sem nada em aberto na lista, a mensagem MUST dizer isso, e MUST NOT inventar passo; o
  próximo passo de outro papel MUST nomear o papel, sem link.
- **FR-4092**: As transições MUST NOT mudar o que a `126` decidiu sobre a sucessão nessas telas.

#### O nível 2: "Andamento da seleção" (B2)

- **FR-4100**: O cartão "Classificação" MUST dar lugar ao "Andamento da seleção", na mesma posição
  relativa, para quem hoje vê o cartão "Classificação", e só para essas pessoas (D-004).
- **FR-4101**: O cartão MUST ter a linha das inscrições (abertas até, ou encerradas em; quantas
  enviadas) e uma linha por Perfil, recolhida por padrão, com o nome, a forma ("por pontuação", "por
  sorteio") e um resumo em palavras.
- **FR-4102**: O Perfil sem inscrição MUST ser uma linha só, *Não se aplica*, com a razão.
- **FR-4103**: Aberta, a linha do Perfil MUST mostrar uma matriz com uma linha por lista e uma coluna
  por ponto da jornada, na sequência da `jornada()` da `094` (com o reposicionamento da D-011), sem
  colunas fixas: cada Etapa ocupa todas as listas do Perfil; o marco por sorteio abre a ordem em
  relação, semente e sorteio; o marco por pontuação tem a ordem; corte, apuração, resultado e
  convocação são por lista.
- **FR-4104**: As colunas MUST ter grupos que dizem de onde vêm ("Etapas · valem para o Perfil",
  "Marco · por pontuação", "Marco · por sorteio", "Etapa governada pela faixa", "Sem efeito no GPS").
- **FR-4105**: Cada célula MUST dizer a situação em palavra e sinal, e a nota quando houver, e MUST ser
  link para a tela do ato só para quem a abre.
- **FR-4106**: A matriz MUST rolar dentro da própria moldura em qualquer largura; a página MUST NOT
  rolar de lado.
- **FR-4107**: Nenhuma providência MUST ser descoberta só pela matriz: tudo o que a matriz diz
  *Pendente*, *Obsoleto*, *Aguarda* ou *Impedido* MUST estar também no nível 1.
- **FR-4108**: Os destinos que o cartão "Classificação" oferecia (sorteio ou ordenação, conduzir o
  marco, corte, ocupação, convocação, divulgar) MUST continuar alcançáveis a partir do nível 2, para
  as mesmas pessoas.
- **FR-4109**: Quando toda convocação de um Perfil tem desfecho e nada falta ocupar, o nível 2 MUST
  dizer, numa nota fixa, que a matrícula acontece fora do GPS (D-003).
- **FR-4110**: Recolhido, o nível 2 MUST NOT deixar a página mais alta do que o cartão
  "Classificação" que substitui, no mesmo Edital e papel, a 1280 px.

#### Custo, acessibilidade e o que não muda

- **FR-4120**: O número de consultas do detalhe do Edital MUST NOT crescer com o número de
  inscrições, de convocações nem de avaliações; MAY crescer com o tamanho da configuração (Perfis,
  marcos, listas, Etapas), e MUST ter teto fixado por teste para os cenários do banco.
- **FR-4121**: O nível 1 MUST ser uma lista, com "sua" dito em texto, e não só por cor; o nível 2 MUST
  usar elementos nativos de abrir e fechar e tabela com legenda e cabeçalhos; as situações MUST ter
  palavra e sinal.
- **FR-4122**: Estilo e script MUST ir para arquivo estático; nada inline (a CSP da `091`).
- **FR-4123**: Nenhuma permissão, papel, situação de domínio, transição, tabela, fila ou notificação
  MUST ser criada, e nenhuma tela de ato MUST mudar de regra.

### Os identificadores de UX

- **UX-230**: Situação em palavra e sinal: Feito ✓, Obsoleto ↺, Pendente ●, Aguarda ◷, Impedido ⊘,
  Depois ·, Não se aplica —. A cor acompanha, nunca substitui.
- **UX-231**: A providência da pessoa leva o rótulo "Sua", em texto, antes do verbo; a de outro papel
  começa pelo papel ("Quem publica resultado:").
- **UX-232**: A lista das providências termina antes de 500 px do topo, a 1280 px, nos Editais do
  banco de estudo com até três providências; com mais, as da pessoa terminam antes de 500 px.
- **UX-233**: A linha recolhida do Perfil tem uma linha de texto de resumo; aberta, a matriz fica numa
  moldura com rolagem própria e legenda.

### Key Entities

- **Andamento** (derivado): para um Edital e um ator, os Perfis com a sequência de pontos e a situação
  de cada ponto em cada lista, as providências e as atenções.
- **Ponto da jornada** (derivado): uma Etapa, a relação, a semente, o sorteio, a ordem, o corte, a
  apuração, o resultado ou a convocação de um marco, na posição que a `jornada()` lhe dá.
- **Célula** (derivada): a situação de um ponto numa lista, com nota, razão, caminho e expectativa.
- **Providência** (derivada): o que precisa acontecer, com o ato, o responsável, se é da pessoa, a
  situação, a razão e o caminho; a forma é a do objeto de trabalho da `104`, com quatro campos a mais.
- **Atenção** (derivada): uma Etapa declarada que nada no GPS consome.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1230**: Nos Editais do cenário de teste e para cada papel (elaborador, homologador, publicador,
  gestor, presidência, avaliador, julgador, auditor), 100% das providências *Pendente* da pessoa levam
  a uma tela cujo GET, com a identidade dela, mostra o controle do ato habilitado; e 100% das
  *Aguarda* e *Impedido* levam a uma tela que o recusa ou anuncia a mesma razão.
- **SC-1231**: No 35, quem conduz lê "1 é sua", com a comunicação da convocação primeiro; quem publica
  resultado lê o definitivo como seu; o Polo Vitória não é providência; as duas Etapas são
  "Atenção".
- **SC-1232**: No 57, as providências de quem conduz são de Perfis diferentes, em situações
  diferentes (uma *Pendente*, outra *Aguarda*).
- **SC-1233**: No 91, a presidência lê "Avaliar" e "Distribuir" como suas, a Entrevista como
  "Atenção", e nenhuma providência de ordem.
- **SC-1234**: Nenhum detalhe de Edital publicado diz "Nenhum ato disponível" ao lado de uma
  providência da pessoa.
- **SC-1235**: Nenhuma célula sem ato vigente é apresentada como pendência sem ser *Pendente* pela
  regra do ato (os testes de derivação cobrem as sete situações).
- **SC-1236**: Depois de corte, apuração, publicação e convocação, a próxima leitura do detalhe muda a
  providência daquela lista (testes de transição).
- **SC-1237**: Uma família por linha da matriz de compatibilidade é coberta por teste: S1, S2, P1, P2
  e CR com dados equivalentes aos do banco; S3 e P3 com cenários compostos.
- **SC-1238**: Depois do corte, a mensagem de sucesso diz o próximo passo da lista e o que falta nas
  outras listas do marco.
- **SC-1239**: O número de consultas do detalhe do Edital é o mesmo com 3 e com 30 inscrições, nos
  cenários de teste, e fica abaixo do teto fixado.
- **SC-1240**: A 1280 px, o nível 1 termina antes de 500 px do topo nos Editais 35, 57, 51 e 91 do
  banco de estudo.
- **SC-1241**: A 1280 e a 375 px, a página do detalhe não rola de lado, com qualquer Perfil aberto.
- **SC-1242**: Recolhido, o "Andamento da seleção" não deixa a página mais alta do que o cartão
  "Classificação" no mesmo Edital e papel.
- **SC-1243**: No nível 2, as colunas do 91 começam pelas Etapas, e as do 35 pela relação; nenhum
  Perfil tem coluna vazia por construção.
- **SC-1244**: Sem migration e sem tabela nova; a suíte contra PostgreSQL não tem regressão.
- **SC-1245**: No roteiro de validação do estudo, com cinco pessoas, ninguém toma o Polo Vitória como
  pendente, e quatro de cinco acertam o primeiro clique da tarefa 2 (validação humana, que espera o
  usuário: inspeção não substitui teste com pessoas).

---

## Assumptions

- O banco de demonstração do estudo (`processo_seletivo_guia`, clonado) é a referência visual; os
  testes automatizados montam cenários equivalentes, porque a suíte não lê aquele banco.
- "Quem conduz" é a gestão da comissão: `comissao:gerir` no escopo, ou a presidência da comissão do
  Processo (`pode_gerir_comissao`). O auditor lê as telas, mas não pratica.
- A presidência não avalia por presidir: só é avaliadora quem está alocado à Etapa e atribuído à
  inscrição (011).
- O custo do detalhe cresce com o tamanho da configuração, como a tela de condução do marco já
  cresce. O teto é medido nos cenários de teste.
- A `126` muda células da condução do marco (*Não se aplica* em lista sem inscrito, entre outras).
  A derivação lê o indicador na forma em que ele estiver, e a mudança dela passa a valer aqui sem
  regra paralela.

---

## Decisões

### D-001 — Uma spec, dois incrementos que escalonam níveis

B1 entrega o nível 1 para todas as famílias, e B2 o nível 2 para todas. É a opção c da decisão 6 do
estudo: escalonar por família (sorteio primeiro, Etapas depois) obrigaria a refazer um nível 2
desenhado para o sorteio, e deixaria a presidência sem providência no P1. A derivação nasce inteira no
B1, porque é dela que as providências saem; o B2 é apresentação.

### D-002 — A trilha de situação sai depois da publicação

Opção c da decisão 1 do estudo. A trilha só orienta enquanto há passos de documento a dar; depois da
publicação ela informa o que o selo ao lado do título já diz, e sugere que falta pouco quando a
seleção nem começou (`J-02`). *Encerrado* e *Cancelado* continuam visíveis pelo selo. O aviso de
conteúdo imutável vai para uma linha no pé do cartão, com a mesma condução da `037`.

### D-003 — Só o que tem caminho no GPS é providência

Opção a da decisão 2 do estudo. Uma providência sem caminho ensina a ignorar a lista. A matrícula,
que acontece fora, é nota fixa no nível 2 quando a convocação do Perfil termina, com a frase do
relatório da `099`.

### D-004 — O nível 1 para todos; o nível 2 para quem via o cartão "Classificação"

Opção c da decisão 3 do estudo. Dizer a quem elabora que "quem publica resultado precisa publicar o
definitivo" é orientação, e não acesso: não mostra candidato, nota nem convocado. A matriz por lista
expõe contagens de convocação que hoje só quem conduz, publica ou audita alcança; mudar isso seria
decisão de acesso, e "negar por padrão" pede que ela não venha de carona.

### D-005 — A Lista não muda

Opção a da decisão 4 do estudo. A contagem por linha custaria por Edital o que o detalhe custa uma
vez, e depende de a derivação estar provada no detalhe. Fica para o P3.

### D-006 — Os nomes

O nível 1 continua "O que fazer agora", que é a pergunta que o cartão já promete responder; o nível 2
é "Andamento da seleção", como a revisão preferiu (decisão 5 do estudo, v3).

### D-007 — As sete situações são de apresentação

Nenhuma é coluna nem estado do domínio. "Depende de outra pessoa" não é situação, é responsável. A
derivação é uma função de leitura sobre os selectors; não importa modelo para decidir situação.

### D-008 — *Depois* no andamento, e a condução do marco fica como está

A `049` decidiu que o resultado sem ordem conta como *Falta* na tela de condução. O andamento o lê
como *Depois*, sem mudar a contagem. Mudar a palavra na condução é o P3 do estudo (decisão 7), junto
da condução estendida, e a `126` mexe nela agora: mexer também aqui seria conflito sem ganho.

### D-009 — O preliminar segue a pendência que já existe

Opção a da decisão 8 do estudo. Preliminar sem definitivo é providência de quem publica, como o
relatório e o encerramento já dizem. A publicabilidade da definitiva decide entre *Pendente* e
*Aguarda*.

### D-010 — A Etapa que nada consome é mostrada sem ser cobrada

Opção b da decisão 9 do estudo. Cobrar mandaria distribuir e avaliar o que não muda nada no sistema;
esconder sumiria com uma etapa que o Edital publicou. A decisão de fundo, se ela deve ter efeito, é
de configuração (`G-07`) e não desta feature.

### D-011 — O marco por sorteio com Etapa de habilitação vem depois dela

A `jornada()` põe no começo o marco que não enumera Etapa, para o caso da `030` (o sorteio que
precede a análise documental). Com `qualifyingStageId`, a relação lê o `HABILITADA` da Etapa de
habilitação, e o marco vem **depois** dela. A composição do andamento reposiciona o ponto do marco
logo depois do ponto que contém essa Etapa. A `jornada()` e a prévia da `094` não mudam: a prévia
não simula sorteio, e mexer nela seria escopo de outra feature.

### D-012 — A expectativa pergunta a quem já sabe, e acrescenta duas ligações

A fonte é `_quem_exige_o_resultado` da validação (enumerada e não porta, governada, de habilitação),
a mesma que impede publicar Edital com Etapa que nunca consolidaria. A ela se somam a Etapa lida só
pelo desempate (`desempate.etapas_do_desempate`, 114), que a ordem lê, e a progressão: a Etapa
consolidável anterior a uma Etapa esperada filtra quem segue. A enumerada por marco de sorteio que
não consolida (decisória não eliminatória) é "sem efeito". A leitura é exposta por um nome público na
validação, e não copiada.

### D-013 — A Etapa é lida como a distribuição a lê, e o Perfil vem do mesmo panorama

As providências da Etapa usam o panorama e o resumo da tela da distribuição, para o Edital inteiro:
a tela de destino mostra os mesmos números. A célula do nível 2, por Perfil, conta a partição do
mesmo panorama, cruzada com o Perfil de cada inscrição numa consulta para o Edital. A partição por
Perfil diz consolidadas e participantes; distribuir e avaliar ficam no nível 1, que é Edital-amplo
como a distribuição.

### D-014 — A apuração espera a Etapa governada

Com corte que governa Etapa, ocupação e convocação contam como habilitado só quem tem `HABILITADA`
vigente nela. Apurar antes apura ninguém, e a apuração envelhece quando os resultados chegam. A
derivação diz *Depois* da Etapa governada, com a razão; não recusa nada, e a tela da ocupação
continua oferecendo o ato a quem quiser praticá-lo.

### D-015 — As transições por último, sobre a `126`

As mensagens de sucesso moram em `corte.html`, `ocupacao.html`, `ordenacao.html`, `sorteio.html` e
`convocacao.html`, que a `126` também muda. Elas entram depois da derivação e do nível 1, sobre a
`126` mergeada ou sobre a branch dela, combinado com a sessão dela; o "Próximo nesta lista" é uma
linha a mais no aviso de sucesso, e não mexe na sucessão.

### D-016 — Uma providência por ato, não por célula

O mesmo ato pendente em três listas do mesmo marco é uma coisa a fazer numa tela só (o sorteio e a
convocação navegam entre as listas); três linhas iguais empurrariam as outras providências para o
"mais N". A providência agrupa por natureza, marco (ou Etapa), situação e responsável, e nomeia as
listas.

### D-017 — A Retificação continua dita pelas frases da `104`

A Retificação em curso é trabalho sobre o documento, e o cartão já a diz desde a `104` (a FR-2819 e
a FR-2820 dela): "Uma Retificação deste Edital aguarda você", ou quem ela aguarda. Ela não entra na
lista das providências, que é do andamento da seleção, e continua logo abaixo dela. Repeti-la nas
duas faria o mesmo trabalho aparecer duas vezes no mesmo cartão. O recurso entra, porque é ato
sobre o resultado da seleção, e o objeto da `104` é o mesmo.

### D-018 — No marco que corta, a apuração espera o corte

O domínio aceita apurar antes de cortar, mas os titulares saem de quem a faixa alcançou: sem corte
não há faixa, a apuração conta todas as vagas como faltando, e a convocação manda "pedir a faixa
seguinte" de um corte que não existe. No banco do estudo, a lista PcD do 35 estava apurada sem corte,
e a primeira versão da derivação mandava pedir a faixa seguinte ali. A derivação diz *Depois* do
corte, e "pedir a faixa seguinte" só aparece sobre um corte vigente. Nada é recusado: é orientação.

### D-019 — A progressão parte só das Etapas que um ato consome

A Etapa consolidável anterior a uma esperada filtra quem segue nela. Mas a Etapa enumerada por marco
de sorteio (S2) é esperada só pela visibilidade e pelo recurso, e nenhum ato a lê: as que vêm antes
dela só a filtrariam. Cobrá-las mandava distribuir 7 inscrições na Prova objetiva do 26, que nada lê.
A progressão parte da ordem por pontuação (enumerada ou desempate), do corte que governa e da
habilitação do sorteio.

### D-020 — O lugar da providência é curto

Na linha da providência, o Perfil vem pelo nome e a lista pelo código que o Edital publica ("PCD",
"PPI"), e a ampla como "Ampla concorrência". O rótulo da derivação única ("Ampla concorrência (linha
geral do quadro)", "Pessoa com Deficiência (PcD) (PCD)") é o certo na matriz e nas telas de ato, e ao
lado do nome do Perfil dobrava a linha. A semente é do marco, e o lugar dela é o Perfil.

### D-021 — Com o Processo encerrado ou cancelado, nada é "seu"

Todo comando da comissão confere que o Processo aceita mudança, e recusa no Processo em estado final.
O andamento continua legível — o que está feito, o que ficou para trás —, mas nenhuma providência é
dita da pessoa nem leva a um ato. E, fora do Edital publicado, o impedimento não diz que quem resolve
é quem elabora Retificações: só o Edital publicado se retifica. Os dois achados são da revisão
independente do B1, como os demais registrados em `verificacao.md`.
