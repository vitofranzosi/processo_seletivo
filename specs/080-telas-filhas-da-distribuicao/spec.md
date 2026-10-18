# Feature Specification: As telas filhas da Distribuição e a auditoria da comissão, quarto incremento

**Feature Branch**: `claude/telas-filhas-da-distribuicao-ea155a`, sobre a `main` em `fbe5bba3`, que traz
a `075`, a `076`, a `077`, a `078` e a `079`

**Created**: 2026-10-17

**Status**: Implementada — PR aberto, merge com o usuário

**Input**: etapa 4 da sequência do [estudo da entrada na gestão](../../doc/estudo-acesso-a-gestao-2026-10-16.md)
(§7) — a modernização por tela, incremental. Quarto incremento, depois de quem avalia
([`077`](../077-telas-de-uso-diario/spec.md)), de quem elabora
([`078`](../078-telas-de-quem-elabora/spec.md)) e das quatro telas da presidência
([`079`](../079-telas-da-presidencia/spec.md)). Fecha o fluxo da presidência: as telas que se abrem a
partir da Distribuição de uma Etapa — Impedimentos, Registrar ocorrência, Resultados da Etapa, Trilha
da avaliação, Conclusões preservadas e a conferência da retirada de atribuições — e a Auditoria da
comissão. A linha de base visual é o [inventário de 16/10](../../doc/inventario-visual-da-gestao-2026-10-16.md),
refeito em 17/10/2026 sobre `fbe5bba3`, nos dois estados da barra.

> **Faixa de identificadores.** Esta spec abre em FR-1800 e SC-700, acima da faixa da `079`
> (FR-1792, SC-696), medida em todas as worktrees e branches em 17/10/2026.

---

## Por que esta feature existe

**Na Distribuição, a presidência lê "onde estou" uma vez; um clique adiante, lê duas.** Desde a `079`,
a Distribuição diz no cabeçalho *GPS › Processos Seletivos › PS-DEMO-2026 › Alocação por Etapa ›
Prova objetiva*. Ao abrir Impedimentos, Registrar ocorrência, Resultados ou Trilha — a faixa logo
abaixo do título —, o cabeçalho volta a dizer só *GPS › Processos Seletivos*, e o caminho reaparece
dentro do conteúdo, numa segunda linha. E reaparece diferente em cada tela: Impedimentos começa pela
Alocação; Registrar ocorrência, Resultados, Trilha, Conclusões preservadas e a conferência da
retirada saltam de "Processos Seletivos" direto para a Etapa, sem o Processo nem a Alocação no meio.
**Medido em 17/10/2026**: das seis filhas, nenhuma leva ao Processo pela trilha, e só uma leva à
Alocação.

**A Auditoria da comissão é vizinha da Comissão e não fala como ela.** A Comissão e a Alocação têm a
trilha no cabeçalho desde a `079`; a auditoria das duas — quem incluiu, alterou, removeu e alocou —
ainda a tem no conteúdo.

**O resultado do último envio aparece depois da explicação.** Na Distribuição e em Impedimentos, o que
acabou de acontecer vem logo abaixo do título (`079`). Em Registrar ocorrência, a frase "1 ocorrência
registrada" vem depois do parágrafo que explica o ato; nas Conclusões preservadas, "Reaberta" vem
depois do parágrafo e do filtro inteiro. É a resposta ao clique que trouxe a pessoa de volta, e ela
está onde a pessoa não olha primeiro.

**Nas consultas, a única ação da tela tem o desenho de ação de linha.** Na Trilha da avaliação, na
Auditoria da comissão e nas Conclusões preservadas, "Filtrar" é o que a tela oferece — e tem o desenho
de "Limpar" ou de "Reabrir" numa linha da tabela. A `055` mediu isso nas Inscrições, na Distribuição e
na Comissão e deu a "Filtrar" o desenho de ação principal (`FR-1008`); nestas três ficou o de antes.

**Impedimentos tem título para o que já foi tirado, e não para o que se faz.** A página tem a seção
"Avaliações fora do conjunto elegível", com título, e o formulário de registrar o impedimento — a
razão de a tela existir — solto entre o título da página e ela.

**O que não muda, e não se negocia aqui:** nenhuma regra de negócio, permissão, semântica de papel —
presidir é vínculo com a comissão, e não papel — ou fluxo. Nenhum endereço, nenhuma view. Nenhum
conteúdo normativo. Nenhuma ação que não se desfaz — registrar a ocorrência, registrar o impedimento
depois da conferência, retirar atribuições, reabrir uma avaliação — muda de lugar, de rótulo ou de
peso. A Distribuição não muda. Nenhuma tela fora destas sete.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Onde estou, dito uma vez só, em todo o fluxo da presidência (Priority: P1)

O presidente abre a Distribuição da Prova objetiva e vai a Impedimentos. No topo, o cabeçalho diz
*GPS › Processos Seletivos › PS-DEMO-2026 › Alocação por Etapa › Prova objetiva › Impedimentos* — a
trilha da Distribuição, com a tela atual no fim —, e cada nível acima leva a ele. O conteúdo começa
pelo título. O mesmo em Registrar ocorrência, Resultados, Trilha da avaliação, Conclusões preservadas
e na conferência da retirada; e, na Auditoria da comissão, *GPS › Processos Seletivos › PS-DEMO-2026 ›
Auditoria da comissão*.

**Why this priority**: é o que a `077`, a `078` e a `079` fizeram nas outras telas de uso diário;
sem isso, o fluxo da presidência diz o caminho no cabeçalho até a Distribuição e o perde um clique
adiante, e cada filha o diz de um jeito.

**Independent Test**: nas sete telas, o caminho está no cabeçalho de contexto, com um link por nível
acima da tela e a tela como página atual; o conteúdo não tem trilha; a página tem uma trilha só.

**Acceptance Scenarios**:

1. **Given** Impedimentos, Registrar ocorrência, Resultados, Trilha da avaliação ou Conclusões
   preservadas de uma Etapa, **When** a página abre, **Then** o cabeçalho mostra *GPS › Processos
   Seletivos › código do Processo › Alocação por Etapa › nome da Etapa › nome da tela*, com os quatro
   níveis do meio como links, e o conteúdo começa pelo título.
2. **Given** a conferência da retirada de atribuições, **When** a página abre, **Then** o cabeçalho
   mostra a mesma trilha, terminando em *Conferir*, com a Etapa como link — como a conferência da
   inclusão na comissão termina em *Comissão › Conferir*.
3. **Given** a Auditoria da comissão de um Processo, **When** a página abre, **Then** o cabeçalho
   mostra *GPS › Processos Seletivos › código › Auditoria da comissão*.
4. **Given** a Auditoria de um Edital, que divide o modelo de página com a Trilha da avaliação e com a
   Auditoria da comissão, **When** a página abre, **Then** o cabeçalho continua o da `076`, e a trilha
   continua no conteúdo.
5. **Given** quem audita, e não preside, **When** abre Resultados, Trilha da avaliação ou Conclusões
   preservadas, **Then** a trilha é a mesma que a presidência lê.

---

### User Story 2 — O que acabou de acontecer, logo abaixo do título (Priority: P2)

A presidente registra a ocorrência de duas faltas na Entrevista. A tela volta com "2 ocorrências
registradas" logo abaixo do título e da Etapa, antes da explicação do ato. Nas Conclusões
preservadas, depois de reabrir uma avaliação, "Reaberta" vem no mesmo lugar, antes da explicação e do
filtro.

**Why this priority**: é a ordem da Distribuição e de Impedimentos — título, Etapa, o que acabou de
acontecer —, e a resposta ao clique é a primeira coisa que a pessoa procura; a P1 tira a duplicação,
esta tira a busca.

**Independent Test**: em Registrar ocorrência e nas Conclusões preservadas, as mensagens do último
envio vêm logo depois do título e da linha da Etapa, antes do texto de ajuda; o erro do filtro
continua junto do filtro.

**Acceptance Scenarios**:

1. **Given** Registrar ocorrência depois de um registro, **When** a página abre, **Then** o resultado,
   e os grupos de recusa dele, vêm antes do parágrafo que diz "Não há desfazer".
2. **Given** Registrar ocorrência com um erro, **When** a página abre, **Then** o erro vem no mesmo
   lugar, e o foco vai a ele, como antes.
3. **Given** as Conclusões preservadas depois de uma reabertura, ou de uma reabertura recusada,
   **When** a página abre, **Then** a mensagem vem antes do parágrafo e do filtro.
4. **Given** as Conclusões preservadas com um filtro inválido, **When** a página abre, **Then** o erro
   do filtro continua dentro do filtro, junto do campo a que se refere.

---

### User Story 3 — Impedimentos com título para o que se faz (Priority: P2)

O presidente abre Impedimentos. Abaixo do título e da Etapa, a seção "Registrar um impedimento" traz o
formulário — quem está impedido, a inscrição, o motivo e o botão —; depois, "Avaliações fora do
conjunto elegível", como antes.

**Why this priority**: dá à página a estrutura que a Comissão ganhou na `079` — título por região —,
sem mudar o que se alcança nem o ato.

**Independent Test**: o formulário de registro está sob um título de seção, antes da seção das
avaliações fora do conjunto elegível; os campos, o botão e a confirmação não mudam.

**Acceptance Scenarios**:

1. **Given** Impedimentos, **When** a página abre, **Then** há uma seção "Registrar um impedimento"
   com o formulário, antes de "Avaliações fora do conjunto elegível".
2. **Given** a conferência de um impedimento, **When** a página abre, **Then** o aviso que declara o
   alcance e "Registrar mesmo assim" continuam antes do formulário, no mesmo desenho.

---

### User Story 4 — Nas consultas, "Filtrar" é a ação principal (Priority: P3)

A auditora abre a Trilha da avaliação, filtra por avaliador e aperta "Filtrar" — o botão com o
desenho de ação principal, como na Distribuição e na Comissão. "Limpar" continua ao lado, com o
desenho de antes.

**Why this priority**: é o desenho que a `055` decidiu para "Filtrar" nas telas que mediu; estas três
consultas ficaram de fora porque não foram medidas, e não por decisão.

**Independent Test**: na Trilha da avaliação, na Auditoria da comissão e nas Conclusões preservadas,
"Filtrar" tem o desenho de ação principal; "Limpar" e "Reabrir" não mudam.

**Acceptance Scenarios**:

1. **Given** qualquer das três consultas, **When** a página abre, **Then** "Filtrar" tem o desenho de
   ação principal.
2. **Given** as Conclusões preservadas com uma conclusão em vigor e a presidência, **When** a página
   abre, **Then** "Reabrir", em cada linha, continua com o desenho de ação de linha.

### Edge Cases

- **Trilha longa no celular.** A das filhas tem seis níveis, e o nome da Etapa pode ser longo. A
  375 px a trilha quebra a linha dentro do cabeçalho; nem ela nem "Trocar identidade" estouram a
  largura.
- **Quem audita sem presidir.** Resultados, Trilha da avaliação e Conclusões preservadas abrem para a
  presidência e para a auditoria (`FR-091` da `012`). A trilha é a mesma para as duas: os níveis
  Alocação por Etapa e Etapa levam a telas da presidência, e a porta delas continua a delas — a
  trilha não concede nem esconde acesso (D-003).
- **Conferência da retirada sem nada que se possa retirar.** A frase "Nenhuma das atribuições
  selecionadas pode ser retirada por aqui." e "Cancelar e voltar" continuam; só a trilha sobe.
- **Registrar ocorrência sem inscrição sem Resultado.** O estado vazio continua; só a trilha sobe e as
  mensagens, se houver, vêm antes da explicação.
- **Registrar ocorrência em conferência.** O aviso que lista as inscrições que serão eliminadas e
  "Registrar mesmo assim" continuam depois da explicação do ato e antes do formulário: são a
  confirmação, e não o resultado de um envio.
- **Auditoria da comissão filtrada sem resultado.** O filtro continua, e o estado vazio é o do filtro.
- **Trilha da avaliação com filtro inválido.** O erro continua dentro do filtro, com o foco nele.
- **Ver atos anteriores.** A paginação por cursor continua no fim da lista, no mesmo desenho.
- **O link de salto.** Continua levando ao conteúdo, que agora começa pelo título.
- **Impressão.** A barra e o cabeçalho de contexto não saem no papel (`076`). O título e a linha de
  baixo dele continuam identificando a Etapa e o Edital impressos.

## Requirements *(mandatory)*

### Functional Requirements

#### A trilha no cabeçalho de contexto

- **FR-1800**: Em Impedimentos, Registrar ocorrência, Resultados da Etapa, Trilha da avaliação,
  Conclusões preservadas, na conferência da retirada de atribuições e na Auditoria da comissão, o
  cabeçalho de contexto MUST mostrar a trilha da tela, como navegação nomeada: o produto, cada nível
  acima da tela como link, e a própria tela como a página atual — como nas telas da `077`, da `078` e
  da `079` (`FR-1780` da `079`).
- **FR-1801**: Nas seis telas que se abrem a partir da Distribuição, os níveis acima da tela MUST ser
  os da trilha da Distribuição — o Processo, a Alocação por Etapa e a Etapa —, e o rótulo da tela MUST
  ser o que ela já mostrava como página atual. Na Auditoria da comissão, o nível acima MUST ser o
  Processo.
- **FR-1802**: Nessas sete telas a trilha MUST NOT aparecer de novo no conteúdo: a página MUST ter uma
  trilha só, e o conteúdo MUST começar pelo título.
- **FR-1803**: A Auditoria de um Edital e as demais telas da gestão — fora das da `077`, da `078`, da
  `079` e destas — MUST continuar com o cabeçalho de contexto da `076` e a trilha no conteúdo
  (`FR-1782` da `079`).
  *Emendada pela [`086`](../086-telas-dos-avisos-aos-candidatos/spec.md) em 18/10/2026*: os Avisos aos
  candidatos, o histórico de um aviso, a prévia, a conferência da interrupção, os Modelos de aviso e a
  edição de um modelo também passaram a ter a trilha no cabeçalho (`FR-1940` da `086`).
- **FR-1804**: A trilha MUST ser a mesma para quem preside e para quem audita: nenhum nível MUST
  aparecer, sumir ou deixar de ser link conforme quem lê.
- **FR-1805**: A 375 px, a trilha do cabeçalho MUST quebrar a linha dentro da largura, e "Trocar
  identidade" MUST continuar alcançável.

#### O que acabou de acontecer

- **FR-1806**: Em Registrar ocorrência e nas Conclusões preservadas, o erro e o resultado do último
  envio MUST vir logo depois do título e da linha da Etapa, antes do texto de ajuda e do formulário,
  com o mesmo texto, o mesmo papel para o leitor de tela e o mesmo foco. O erro do filtro MUST
  continuar dentro do filtro. Em Impedimentos, que já tem essa ordem, nada MUST mudar.

#### Títulos por região

- **FR-1807**: Em Impedimentos, o formulário de registro MUST vir numa seção com o título "Registrar
  um impedimento", antes da seção "Avaliações fora do conjunto elegível"; os campos, o botão e a
  conferência MUST continuar os mesmos.

#### A hierarquia das ações

- **FR-1808**: Na Trilha da avaliação, na Auditoria da comissão e nas Conclusões preservadas,
  "Filtrar" MUST ter o desenho de ação principal (`FR-1008` da `055`); "Limpar" e "Reabrir" MUST
  continuar com o desenho de antes.
- **FR-1809**: As ações que não se desfazem — "Registrar mesmo assim" em Impedimentos e em Registrar
  ocorrência, "Retirar N atribuições" na conferência da retirada e "Reabrir" nas Conclusões
  preservadas — MUST continuar com o rótulo, o desenho, o lugar e as frases que as precedem; nenhuma
  MUST ganhar o desenho de ação principal.

#### O que não pode piorar

- **FR-1810**: Nenhuma variante do inventário visual MUST deixar de carregar, mudar de `status` ou
  passar a estourar a 375 ou a 1280 px, com a barra expandida e com ela recolhida; e só as telas desta
  feature MUST mudar de largura ou de altura.
- **FR-1811**: As telas tocadas MUST passar pelos guardiões de acessibilidade, larguras, vocabulário e
  folha que já varrem a gestão — o link de salto, o `main`, toda classe com regra na folha, todo botão
  de envio com classe.

### Key Entities

Nenhuma. Só apresentação.

## Decisões

### D-001 — A trilha das filhas é a da Distribuição, mais a tela

Nas filhas, os níveis eram diferentes em cada uma, e cinco das seis pulavam o Processo e a Alocação.
Repetir "os níveis que cada tela já mostrava", como a `079` fez nas suas (`FR-1781` da `079`), levaria
ao cabeçalho essa diferença. A trilha de uma filha é a da tela de onde ela se abre, com ela no fim — o
mesmo que a conferência da inclusão faz com a Comissão. Os rótulos da página atual são os que cada
tela já usava ("Ocorrência", "Trilha da avaliação", "Conferir").

### D-002 — A Auditoria do Edital fica com o cabeçalho da 076

A Trilha da avaliação, a Auditoria da comissão e a Auditoria do Edital são o mesmo modelo de página.
O pedido nomeia as duas primeiras; a terceira é tela de quem audita o Edital, e não do fluxo da
presidência. O modelo passa a ter, só para ela, a trilha no conteúdo; fica registrada como o próximo
grupo natural, junto das outras telas do Edital que ainda a têm.

### D-003 — Uma trilha só para quem preside e para quem audita

Resultados, Trilha da avaliação e Conclusões preservadas abrem para as duas bases. A trilha poderia
mostrar a Alocação e a Etapa só para a presidência — mas isso pede à view uma informação que ela não
entrega hoje, e o pedido proíbe mudar view. A trilha no conteúdo já levava quem audita à Etapa, que
é tela da presidência: a trilha nova mantém isso e acrescenta a Alocação, e a porta de cada tela de
destino continua a dela. Fica registrado como achado.

### D-004 — "Filtrar" tem o desenho de ação principal nas três consultas

A `055` decidiu que a ação principal de uma tela não tem o desenho de ação de linha (`FR-1008`), e
aplicou a regra às telas que a auditoria dela mediu. Nestas três consultas, "Filtrar" é a única ação
da tela (na Trilha e na Auditoria) ou a única fora das linhas (nas Conclusões). Aplicar a mesma regra
não reabre a decisão: estende-a, com o mesmo desenho.

### D-005 — O que não muda, por governança

- **Nenhuma ação que não se desfaz ganha peso.** "Registrar mesmo assim" e "Retirar N atribuições"
  continuam com o desenho de perigo, e "Reabrir" com o de ação de linha; nenhuma ganha o de ação
  principal, e nenhuma muda de rótulo ou de lugar. "Registrar impedimento" e "Revisar antes de
  registrar" continuam com o de ação principal: levam à conferência, e não ao ato.
- **A explicação do ato continua antes do ato.** Em Registrar ocorrência, "Não há desfazer." continua
  antes da conferência e do formulário; só o resultado de um envio já feito sobe acima dela.
- **A Distribuição não muda.** A faixa dos lugares da Etapa e as ações dela são as da `079`
  (`FR-1785` e `FR-1786` da `079`). A faixa não se repete nas filhas: a trilha leva de volta à Etapa
  com um clique.
- **"Filtrar" continua `botao` na Comissão e na Distribuição**, pela `FR-1008` da `055`; esta feature
  não toca nelas.

## Success Criteria *(mandatory)*

- **SC-700**: Refeito o inventário visual, **zero** variantes estouram a 375 ou a 1280 px, e
  **nenhuma** muda de `status`, nos dois estados da barra.
- **SC-701**: Fora de Impedimentos, Registrar ocorrência, Resultados, Trilha da avaliação, Conclusões
  preservadas e Auditoria da comissão, **nenhuma** variante muda de largura ou de altura.
- **SC-702**: Nas sete telas, "onde estou" aparece **uma** vez por página, no cabeçalho de contexto, e
  cada nível acima da tela está a **um** clique.
- **SC-703**: Das seis filhas da Distribuição, as que levam ao Processo pela trilha passam de **zero**
  para **seis**, e as que levam à Alocação por Etapa, de **uma** para **seis**.
- **SC-704**: A suíte contra PostgreSQL continua sem falhas.
- **SC-705**: O percurso — da Distribuição a cada filha e de volta pela trilha, e à Auditoria da
  comissão — é feito só pelo teclado, com foco visível, a 1280 e a 375 px.

## Assumptions

- "Telas filhas da Distribuição" são as que a faixa dos lugares da Etapa e as ações da Distribuição
  abrem: Impedimentos, Registrar ocorrência, Resultados, Trilha da avaliação, as Conclusões
  preservadas (pelo link da orientação de reabertura) e a conferência da retirada ("Retirar as
  selecionadas"). A Auditoria da comissão é a do pedido.
- A conferência da retirada não está no inventário visual: ela é a resposta a um envio, e o inventário
  só abre telas pelo endereço. É provada pelos testes e no navegador, como a conferência da inclusão
  na `079`.
- O produto no começo da trilha é a sigla GPS, como da `076` à `079`.
- A tela mais estreita que se considera é a de 375 px, a mesma do inventário.
- A validação com a equipe, recomendada desde a `075`, continua pendente; este incremento não a
  substitui.
