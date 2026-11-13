# Feature Specification: Achar, conferir e voltar — o MVP de UX da Retificação

**Feature Branch**: `claude/upbeat-haslett-9d4178`, sobre a `main` em `250efe97`

**Created**: 2026-11-06

**Status**: Draft, **só documental**. Nenhum código, migration, rota ou tela foi alterado. As
decisões têm três origens:

- **Do revisor do produto, recebidas com o pedido desta spec:** o MVP é M1–M4 da auditoria de
  05/11/2026, cada um com o cuidado que ele pediu (*Clarifications*). Não se reabrem aqui.
- **Do usuário, e que continuam com ele:** as quatro perguntas da seção 9 da auditoria — a
  coerência temporal do cronograma, o "antes" de hoje ao lado do da base, a prévia do documento
  consolidado e o reapontamento da base. Esta spec **não as toma**; chama-as de *1ª a 4ª pergunta
  da auditoria*.
- **Propostas de desenho desta spec:** D-001 a D-009, abaixo. Resolvem o que o pedido deixou
  aberto e **aguardam a aprovação do usuário**.

**Input**: *"MVP de UX da Retificação de Editais do GPS (M1–M4 da auditoria): busca por campo com
resultado que leva ao campo; marcação persistente com dois estados e linhas do resumo ligadas ao
cartão; versão-base nomeada com honestidade; impeditivos da criação já na conferência, pelas mesmas
regras, sem regra nova e mantendo a validação final."*

> **Faixa de identificadores.** Esta spec abre em **FR-3917** e **SC-1173**. O teto foi medido em
> 06/11/2026 em `specs/` de todas as worktrees desta máquina e da `main` em `250efe97`: o requisito
> funcional três mil novecentos e dezesseis e o critério mil cento e setenta e dois. A pasta `123`
> não existe em nenhuma delas, e não há PR aberto. **Nenhum `UX-` é aberto aqui.** As decisões
> reiniciam em `D-001`.
>
> **Como esta spec cita outras.** Requisito de outra feature, pelo identificador e pela feature
> ("a FR-019 da `002`"). Decisão de outra feature, pelo assunto e pela feature, nunca pelo número.
> Os achados da auditoria se citam pelo código dela (`RU-01` a `RU-12`), e as propostas por `M1` a
> `M4` e `P1` a `P4`.

## Por que esta feature existe

A auditoria de 05/11/2026 (`doc/auditoria-ux-retificacao-2026-11-05/`, PR #406) mostrou que o GPS
**já** retifica por diferença, numa tela própria: só vira Alteração Normativa o campo que a pessoa
mudou, com caminho por identidade, e há índice, busca, marca "alterada", barra fixa e a tabela "O
que vai mudar". O que falha é o que ajuda a pessoa a **achar** o campo, a **voltar** a ele depois de
conferir e a **saber antes do último clique** que o ato será recusado:

1. **A busca lê só o nome do cartão** (`RU-01`). «vagas», «remuneração» e «prazo» não acham o campo;
   «requisito» acha uma Seção vazia e não os Requisitos de participação do Perfil.
2. **A conferência apaga a memória do formulário** (`RU-02`). Depois de «Ver o que vai mudar», a
   marca «alterada» some de todos os cartões, «Só o que eu alterei» não acha nada, e as linhas do
   resumo não levam de volta ao campo.
3. **«Vigente hoje» mostra o que ainda não vigora** (`RU-04`). Com Retificação publicada de vigência
   futura, a coluna exibe o valor dela.
4. **A recusa chega no último clique** (`RU-03`). A incoerência entre as vagas do Perfil e o quadro
   só aparece em «Criar Retificação», sem caminho até a linha.

O Edital de demonstração rende 14.852 px de formulário a 1280 px; o ampliado ao porte dos Editais
57 e 59/2026 rende 26.517 px, com o Cronograma começando a 15.804 px. Quanto maior o Edital, mais
caro cada um dos quatro defeitos.

### Revisão crítica dos quatro itens, antes de especificar

O pedido trouxe M1–M4 com um cuidado cada. A leitura do código, em 06/11/2026, confirmou os quatro
diagnósticos e acrescentou o que o pedido não sabia. É isso que muda o que esta spec escreve:

**M1 — busca por campo.**

- Confirmado: `aplicar()` em `retificacao.js` compara só `data-nome`, e o filtro nasce só com 12 ou
  mais cartões. A divergência entre `data-nome` e a legenda visível («Linha do quadro» contra «LINHA
  DO QUADRO DE VAGAS») também é real: a busca precisa ler **o que a pessoa vê**.
- **«prazo recursal» não leva ao prazo do marco sem sinônimo.** O campo do Marco se chama «Prazo em
  dias» (ou «Prazo de recurso, em dias corridos», no marco ainda sem janela), e o cartão, pelo nome do
  marco; nenhum dos dois contém «recursal». A expressão inteira acha, pelo valor, a descrição de um
  Evento como "Resultado final e abertura do prazo recursal" — que é o Cronograma, e não o prazo do
  marco. O critério da auditoria («prazo» encontra o prazo do Marco) se cumpre pelo rótulo; levar
  «prazo recursal» ao marco só por equivalência de termos, que o revisor condicionou a teste. Esta
  spec **não** cria sinônimo (D-003) e registra o caso como candidato.
- **O valor precisa de corte por tipo, e não só por tamanho.** O conteúdo de um Edital tem 17
  Seções de texto, descrições e atribuições longas; buscar dentro delas por «candidato» devolveria
  dezenas de campos. E números, datas e «Sim/Não» casariam com quase tudo. Só o valor curto e
  nominal entra (D-002).
- O limiar de 12 cartões não muda: as 17 Seções do texto bastam para que todo Edital publicado o
  passe.

**M2 — marcação persistente.**

- Confirmado: `recontar()` compara com o `default*` do DOM, e o servidor reexibe o digitado como
  declarado; a marca zera por construção.
- **A tela de edição (103) tem o mesmo defeito na abertura, e pior.** Ela parte do conteúdo
  *proposto*: ao abrir a Retificação devolvida, que já tem N Alterações, **nenhum** cartão está
  marcado, e a contagem diz "Nenhum campo alterado ainda". É exatamente quem mais precisa da marca —
  quem corrige o que o homologador devolveu. O estado "na proposta" precisa existir desde o GET da
  edição.
- **A unidade de contagem precisa ser uma só.** "Alterações" é ambíguo na tela atual: o título do
  resumo conta linhas, o botão com gesto conta Alterações Normativas, e uma troca de arquivo produz
  uma linha e duas Alterações. A marca é por cartão; a contagem da proposta também (D-001).
- **Remoção já declarada não tem cartão** na edição (a entidade não está no proposto). Ela precisa
  entrar na contagem e no caminho de volta pelo bloco «Remoções já declaradas».
- **Conferência recusada** (uma linha que não se monta, por exemplo) não produz proposta. A tela não
  pode dizer "nenhuma alteração na proposta" nesse caso (D-008).
- As linhas do resumo não têm hoje a referência do cartão: o servidor sabe o grupo, mas entrega só o
  título dele. O `id="cartao-<ref>"` já existe; falta a linha saber o `<ref>`.

**M3 — versão-base.**

- Confirmado: `_versao_vigente` (`interface/views.py:4377`) devolve a de maior `valid_from`, mesmo
  futura. Compor sobre ela é correto — é a mesma base que a precondição da publicação espera — e
  **não muda** (FR-3936).
- **"Vigente" aparece em mais três lugares da mesma tela**: no «Como funciona» ("Abaixo está o
  conteúdo *vigente*"), no título do modo somente leitura ("Conteúdo vigente") e no nome da função.
- **Na edição, a coluna «Vigente hoje» nem é a base**: o resumo da edição compara com o *rascunho*
  ("O que muda em relação ao rascunho"), e a coluna mostra o valor que a própria Retificação já
  declara. O rótulo erra duas vezes (D-007).
- **"Quando foi publicada" não sai de um campo só.** Depois de uma publicação fora de ordem de
  vigência, as versões de fronteira são rematerializadas, e a publicação que as gerou
  (`source_publication`) não é a que a pessoa conhece como "a da base". O que diz sem ambiguidade é
  a lista do que a versão incorpora — a Publicação original e as Retificações, cada uma com a data
  de publicação —, que `applied_publications` já guarda e que a consolidação do documento (054) já
  usa (D-006).
- **Há três situações de vigência, e não duas**: a base vigora; a base ainda não vigora; a base já
  vigorou e foi sucedida — o caso da Retificação em edição cuja base ficou para trás. A terceira é
  fato, e dizê-la não é reapontar (a 4ª pergunta continua com o usuário).
- As telas de homologar, devolver e publicar e o detalhe da Retificação dizem «Antes», que é o valor
  da base da Retificação. A auditoria pediu o mesmo cuidado ali; o rótulo «Antes» é neutro e fica, e
  a frase da base passa a acompanhá-lo.

**M4 — impeditivos na conferência.**

- **Não é só `_coerencia_do_quadro_de_vagas`.** Toda a conferência de conteúdo da criação —
  `validate_for_publication` com o ato de Retificação, mais as guardas do que o ato acrescenta, a
  troca do objeto inteiro e as precondições — roda só no «Criar» e no «Gravar». A conferência atual
  chama apenas a derivação das diferenças e os gestos.
- **Os parâmetros importam tanto quanto a função.** A criação passa a topologia publicada do Edital
  e **não** passa `situacoes` (a consulta à Loteria, que é de rede, é da publicação — FR-3644 da
  `116`) nem `marcos_sorteados`. A conferência MUST passar os mesmos, para que o que ela diz seja o
  que a criação diria.
- **Na edição, o conteúdo conferido é o ato inteiro**, depois da fusão com o que a Retificação já
  declara e das remoções desfeitas — e não o proposto mais a diferença da tela.
- **Há regras dependentes do banco** — a regra de corte que nasce governando Etapa já avaliada
  consulta se há Resultado — e, entre conferir e criar, outra pessoa pode registrá-lo. Por isso a
  validação final continua obrigatória, e um teste o prende. *(Corrigido em 06/11, na implementação:
  a primeira redação citava também o Evento vencido e o período de inscrições encerrado, mas no ato
  de Retificação essas regras não se aplicam — `_eventos_vencidos` e
  `_periodo_de_inscricoes_encerrado` só valem na publicação do Edital, e a extração inviável é
  advertência. Nenhuma regra impeditiva do ato de Retificação depende do relógio hoje.)*
- **Advertências não são impeditivos.** A criação as descarta; as telas de submeter e homologar as
  mostram (`advertencias_do_ato`, 104). Trazê-las à conferência seria uma terceira superfície de
  aviso, com outra base de cálculo (o conteúdo em vigor na fronteira, e não a base). Fica fora
  (D-005).

### O que se descarta

- **Segundo editor, passo obrigatório "o que você precisa retificar?", cartões recolhidos.** A
  auditoria descartou os três para o MVP; nada do que se mediu os pede antes de M1–M4.
- **Mudar a base da composição.** Compor sobre a última versão publicada está certo; o defeito é o
  nome.
- **Desabilitar «Criar Retificação» quando há impeditivo.** O impeditivo vale para o instante da
  conferência, e a criação confere de novo (D-004).

### O que esta spec cobre, e o que fica fora

**Cobre** M1–M4, na tela Retificar (criação e edição) e, para M3, no detalhe da Retificação e nas
confirmações de homologar, devolver e publicar.

**Fica fora**, e não se resolve por implicação:

- a 1ª pergunta da auditoria (coerência temporal do cronograma) e qualquer regra nova de cronograma;
- a 2ª (mostrar também o "antes" da versão que vigora hoje), a 3ª (prévia do documento) e a 4ª
  (reapontar a base);
- P1 a P4: vocabulário único entre elaboração, gestão e portal; índice fixo com nível por Perfil;
  Submeter com a lista; contexto na homologação; cartões recolhidos;
- editor novo, mudança no versionamento, no modelo de Alteração Normativa e qualquer mudança
  normativa.

## Clarifications

### Session 2026-11-06 (pedido do revisor do produto, recebido pela sessão de origem)

- Q: Qual é o escopo? → A: O MVP M1–M4 da auditoria, aprovado pelo revisor com quatro cuidados. A
  homologação contextual (P1/P3) é a entrega seguinte, e não esta.
- Q: Qual é o cuidado de M1? → A: A busca acha o **campo**, e não só o cartão; o resultado diz onde
  ele está e leva até ele com o foco no campo; funciona pelo teclado; preserva o digitado; a busca
  por valor é delimitada; termos equivalentes só entram se testes os justificarem.
- Q: Qual é o cuidado de M2? → A: Dois estados separados — o que compõe a Retificação (a diferença
  em relação à base) e o que mudou desde a última conferência —, ditos separadamente na tela. Não
  basta manter o marcador ligado depois do POST. As linhas do resumo levam ao cartão.
- Q: Qual é o cuidado de M3? → A: Dizer sem ambiguidade qual é a versão-base, quando foi publicada e
  desde quando vigora, preservando as regras de composição. Mostrar também a versão que de fato
  vigora fica para a 2ª pergunta.
- Q: Qual é o cuidado de M4? → A: Reaproveitar **integralmente** as regras de
  `editais/domain/validation.py`, sem duplicar regra nem criar restrição temporal nova. A validação
  final na criação continua obrigatória.
- Q: A 1ª pergunta (coerência temporal) bloqueia esta spec? → A: Não. A posição preliminar do
  revisor — impedir só a incoerência interna de um período, avisar das relações suspeitas entre
  Eventos, e impedir entre Eventos só com regra normativa aprovada — fica registrada e não é
  decidida aqui.
- Q: O que precisa ter nos critérios? → A: Testes de regressão; testes de navegador no grupo
  `navegador`; cenários com Edital extenso; e um critério de decisão para a segunda etapa (índice
  fixo com nível por Perfil).

## User Scenarios & Testing *(mandatory)*

Os atores são os da auditoria: **quem elabora** a Retificação (`retificacao:elaborar`), **quem
homologa** e **quem publica**. Os cenários A a G são os da seção 5 da auditoria, e o Edital é o
01/2026 do `seed_demo` ou o ampliado do cenário E (4 Perfis com 2 Modalidades cada, 11 Eventos).

### User Story 1 — Quem elabora acha o campo pelo nome do assunto (Priority: P1)

A pessoa abre Retificar para mudar as vagas de um Perfil, a remuneração ou o prazo de recurso de um
marco. Ela digita o assunto em «Encontrar» e recebe a lista dos **campos** que correspondem, cada um
dizendo onde está (seção e cartão), o rótulo e o valor atual. Ela ativa um resultado — pelo mouse ou
pelo teclado — e o foco vai para o campo, com o cartão visível. Nada do que ela já tinha digitado
muda.

**Why this priority**: É a mudança de maior impacto e menor custo da auditoria (`RU-01`, gravidade
A): sem ela, o cenário B exigiu seis ações e saber que as vagas por lista moram em "Linha do quadro".

**Independent Test**: No navegador, num Edital de demonstração e no ampliado, digitar «vagas»,
«remuneração», «prazo» e «requisito» e conferir a lista e o foco depois de ativar cada resultado.

**Acceptance Scenarios**:

1. **Given** a tela Retificar do Edital 01/2026, **When** a pessoa digita «vagas», **Then** a lista
   mostra o campo «Vagas imediatas» de cada Perfil e de cada linha do quadro de vagas, cada um com
   seção, cartão e valor; nenhum outro campo; e, além deles, só os cartões cujo nome contém
   «vagas» e que não têm campo com «vagas» no rótulo, um resultado de cartão cada.
2. **Given** a lista de «vagas», **When** a pessoa ativa o resultado da linha do quadro do Perfil
   DOC-INFO, **Then** o foco está no campo «Vagas imediatas» daquela linha, e o cartão está visível.
3. **Given** a pessoa já alterou o término das inscrições, **When** ela busca «remuneração» e ativa o
   resultado, **Then** o término continua com o valor digitado, e a remuneração está em foco.
4. **Given** a tela, **When** a pessoa digita «requisito», **Then** a lista inclui o campo
   «Requisitos de participação» de cada Perfil, e não só a Seção «Requisitos gerais».
5. **Given** o cursor em «Encontrar» com um termo que tem resultados, **When** a pessoa tecla Enter,
   **Then** o formulário não é enviado e o foco vai para o primeiro resultado; Tab percorre os
   resultados e Enter num deles leva ao campo.
6. **Given** a tela, **When** a pessoa digita «candidato», **Then** nenhuma Seção do texto entra na
   lista pelo que o texto dela diz.

---

### User Story 2 — Quem elabora confere e volta sem perder o que fez (Priority: P1)

A pessoa altera três campos em três seções e clica «Ver o que vai mudar». A tela volta com o resumo
e com os três cartões marcados como **na proposta**. A barra diz, separadamente, quanto a proposta
contém e que nada mudou desde a conferência. Cada linha do resumo leva ao campo. Se ela muda mais um
campo, a barra passa a dizer que há alteração nova desde a última conferência, e o cartão novo ganha
a marca «alterada» — distinta da de «na proposta».

Quem reabre uma Retificação devolvida para correção encontra, desde a abertura, os cartões que o ato
já altera marcados como na proposta.

**Why this priority**: `RU-02`, gravidade A na Retificação múltipla: esquecer ou desfazer uma
alteração ao corrigir outra.

**Independent Test**: Por cliente HTTP, a resposta da conferência traz a marca nos cartões certos e
a referência em cada linha do resumo; no navegador, as duas frases da barra, «Só o que eu alterei»
e o caminho de cada linha ao campo.

**Acceptance Scenarios**:

1. **Given** três campos alterados em Cronograma, Perfis e Seções do texto, **When** a pessoa confere,
   **Then** exatamente esses três cartões estão marcados «na proposta», a barra diz "3 cartões com
   alteração na proposta" e "Nenhuma alteração nova desde a última conferência".
2. **Given** a conferência do cenário anterior, **When** a pessoa marca «Só o que eu alterei», **Then**
   só os três cartões ficam visíveis.
3. **Given** a conferência, **When** a pessoa ativa «Ir ao campo» na linha do término das inscrições,
   **Then** o foco está no campo «Término» daquele Evento.
4. **Given** a conferência, **When** a pessoa altera mais um campo, **Then** o cartão dele ganha
   «alterada», a barra diz "1 campo alterado desde a última conferência", e a contagem da proposta
   continua 3 até a próxima conferência.
5. **Given** uma Retificação devolvida com Alterações em dois cartões e uma remoção declarada,
   **When** quem elabora abre «Editar a Retificação», **Then** os dois cartões estão marcados «na
   proposta» e a barra diz "2 cartões com alteração na proposta e 1 remoção já declarada".

---

### User Story 3 — Quem elabora, homologa ou publica sabe de que versão é o «antes» (Priority: P1)

Com uma Retificação publicada de vigência futura, a tela não chama de "vigente hoje" o que ainda não
vigora. Ela diz qual é a versão-base — o que ela incorpora e quando cada ato foi publicado — e em que
situação de vigência ela está. O mesmo vale para o «Antes» que quem homologa e quem publica leem.

**Why this priority**: `RU-04`, gravidade A: ler como em vigor o que ainda não está, no cenário G das
Retificações sucessivas.

**Independent Test**: Por cliente HTTP, com a base nas três situações de vigência, conferir a frase
da base e a ausência de "Vigente hoje" nas cinco telas.

**Acceptance Scenarios**:

1. **Given** um Edital com as Retificações nº 2 (vigente) e nº 3 (publicada, vigência futura em
   20/11), **When** quem elabora confere uma alteração, **Then** a coluna se chama «Na versão-base»,
   e a tela diz que a base incorpora a Publicação original e as Retificações nº 2 e nº 3, com as
   datas de publicação, e que ela **ainda não vigora** — passa a vigorar em 20/11.
2. **Given** um Edital sem Retificação de vigência futura, **When** quem elabora confere, **Then** a
   tela diz que a base **vigora desde** a data de início da vigência dela.
3. **Given** uma Retificação em edição cuja base já foi sucedida por versão posterior, **When** quem
   elabora abre a edição, **Then** a tela diz que a base **vigorou a partir de** tal data e já não é
   a versão em vigor, e a coluna do resumo se chama «No rascunho».
4. **Given** a Retificação do cenário 1 submetida, **When** quem homologa abre a confirmação de
   homologar, **Then** a frase da base acompanha a coluna «Antes».

---

### User Story 4 — Quem elabora vê o impeditivo antes de «Criar» e chega até ele (Priority: P1)

A pessoa aumenta as vagas de um Perfil de 3 para 4 sem mexer no quadro e clica «Ver o que vai
mudar». A conferência já mostra o que impede criar a Retificação — a mesma frase que «Criar»
mostraria — com um link até a linha do quadro. Ela corrige a linha, confere de novo, e o impeditivo
some. «Criar» continua conferindo tudo de novo.

**Why this priority**: `RU-03`: a recusa no último clique, sem caminho até a linha, depois de a
pessoa já ter escrito a Justificativa.

**Independent Test**: Por cliente HTTP, a conferência com o impeditivo do quadro devolve a frase e o
link sem criar nada; a criação com o mesmo formulário recusa com a mesma frase.

**Acceptance Scenarios**:

1. **Given** as vagas do Perfil DOC-INFO de 3 para 4 e o quadro inalterado, **When** a pessoa
   confere, **Then** a tela mostra o impeditivo do quadro com a mesma frase que compõe a recusa
   de «Criar», um link à primeira linha do quadro daquele Perfil, e nenhuma Retificação foi criada.
2. **Given** o impeditivo na conferência, **When** a pessoa ativa o link, **Then** o foco está no
   cartão da linha do quadro.
3. **Given** a linha do quadro corrigida para somar 4, **When** a pessoa confere de novo, **Then**
   nenhum impeditivo é mostrado.
4. **Given** uma conferência sem impeditivo de uma regra de corte que nasce governando uma Etapa, e
   um Resultado registrado nessa Etapa entre a conferência e o «Criar», **When** a pessoa clica
   «Criar Retificação», **Then** a criação recusa pela regra que já existe, e nada é gravado.
5. **Given** uma Retificação em edição, **When** a pessoa confere uma alteração que deixaria o ato
   inteiro com impeditivo, **Then** a conferência o mostra, calculado sobre o ato inteiro.

---

### User Story 5 — As Retificações de hoje continuam funcionando (Priority: P1)

Retificação simples, múltipla e sucessiva; acrescentar e remover; trocar anexo; aplicar aos demais
Perfis; editar a devolvida; submeter, homologar, devolver e publicar — tudo continua como está.

**Why this priority**: O MVP mexe na tela por onde passa toda Retificação do acervo; uma regressão
ali é ato errado.

**Independent Test**: As suítes existentes da Retificação passam sem alteração de asserção, e a
jornada de navegador cobre criar, conferir, editar a devolvida e publicar.

**Acceptance Scenarios**:

1. **Given** as suítes de Retificação existentes, **When** a feature é implementada, **Then** elas
   passam sem que nenhuma asserção sobre comportamento seja removida ou afrouxada.
2. **Given** uma Retificação múltipla criada pela tela, **When** ela é submetida, homologada e
   publicada, **Then** o conteúdo consolidado é o mesmo que seria antes desta feature.

### Edge Cases

Cada caso abaixo é requisito, e tem linha própria na matriz de rastreabilidade do plano.

- **Termo com 1 caractere.** Não filtra cartão nem lista campo.
- **Termo com várias palavras.** Todas precisam aparecer no mesmo campo (no conjunto seção + cartão +
  rótulo + valor elegível), em qualquer ordem, com ao menos uma no rótulo ou no valor: «término
  inscrições» acha o Término do Evento «Inscrições».
- **Termo que só casa com o nome do cartão.** Um resultado de cartão, e não um por campo.
- **Acento e caixa.** «remuneracao» e «REMUNERAÇÃO» acham «Remuneração».
- **Mais resultados que o teto.** A lista mostra os primeiros pela ordem do documento e diz quantos
  há no total; os cartões que correspondem continuam todos visíveis.
- **Campo de cartão escondido por «Só o que eu alterei».** Não entra na lista enquanto a marca
  estiver ligada.
- **Linha acrescentada nesta tela** (Perfil, Evento, Anexo, linha do quadro, Modalidade, critério,
  ainda sem conferência). Continua sempre visível, como hoje, e não entra na lista de resultados.
- **Resultado num cartão que o filtro escondeu.** Ativá-lo mostra o cartão e a seção, e põe o foco no
  campo.
- **Campo de arquivo.** O foco vai para o seletor de arquivo, e o arquivo já escolhido não se perde.
- **Justificativa e vigência.** Não entram na busca nem nas contagens, como hoje.
- **Conferência recusada** (a tela volta com recusa e sem proposta calculada). Nenhum cartão é
  marcado «na proposta», e a barra diz que a proposta não pôde ser conferida — e não que ela está
  vazia (D-008).
- **Campo que volta ao valor da base depois da conferência.** Ganha «alterada» (mudou desde a
  conferência) e continua «na proposta» até a próxima conferência, quando deixa de estar.
- **Remoção marcada na criação.** O cartão marcado para remover entra «na proposta».
- **Gesto de aplicar aos demais Perfis.** Os cartões de destino que o gesto altera entram «na
  proposta».
- **Troca de arquivo.** Conta um cartão, embora produza duas Alterações Normativas.
- **Impeditivo sem cartão identificável** (uma coleção inteira vazia, por exemplo). Aparece com a
  frase e sem link, ou com link à seção quando a seção está na página. O achado de um campo da raiz
  (o método do sorteio comum, por exemplo) leva ao cartão da Identificação.
- **Impeditivo numa linha acrescentada nesta tela** (o Evento novo sem início). Leva à linha nova.
- **Linha do quadro, Modalidade ou critério acrescentado.** Marca a linha nova, e não o Perfil.
- **Recusa de guarda antes dos achados** (Modalidade ou critério acrescentado inválido, corte sobre
  Etapa avaliada, troca do objeto inteiro, precondição). A conferência mostra a mesma recusa que a
  criação mostraria, e só ela, como a criação.
- **Base de vigência exatamente agora** (início da vigência igual ao instante da tela). Vigora.
- **Base que é a Publicação original**, sem Retificação. A frase diz só "a Publicação original de
  DD/MM/AAAA".
- **Modo somente leitura** (sem `retificacao:elaborar`). A frase da base aparece, e o título deixa de
  dizer "Conteúdo vigente".
- **375 px.** Nenhum dos elementos novos produz rolagem lateral.

## Requirements *(mandatory)*

### Functional Requirements

#### A. Achar o campo (M1)

- **FR-3917**: A busca «Encontrar» MUST comparar o termo, para cada campo editável de cada cartão
  filtrável, com o **texto de busca do campo**: o título da seção, a legenda visível do cartão
  (categoria e nome), o nome do cartão já usado hoje, o rótulo do campo e o valor atual do campo
  quando ele for elegível (FR-3918). A comparação MUST ignorar caixa e acento. Há dois tipos de
  resultado, e um cartão produz um **ou** outro:
  - **resultado de campo**, quando cada palavra do termo está no texto de busca do campo **e** ao
    menos uma delas está no rótulo ou no valor elegível do próprio campo;
  - **resultado de cartão**, um só por cartão, quando cada palavra está na seção, na legenda ou no
    nome do cartão e nenhum campo dele produziu resultado de campo.
  O termo que só casa com o nome do cartão MUST NOT listar cada campo do cartão (um Marco tem 22).
- **FR-3918**: São elegíveis para a busca por valor **só** o campo de texto curto e a opção escolhida
  de uma lista de referência (Modalidade, lista de concorrência, Perfil, forma). MUST NOT ser lidos
  pelo valor: texto longo e lista de texto (Seções, descrições, atribuições, instruções, requisitos),
  número, data e hora, Sim/Não e arquivo. Esses continuam achados pelo rótulo e pelo cartão (D-002).
- **FR-3919**: A busca MUST começar a filtrar e a listar a partir de **2** caracteres, descontados os
  espaços das pontas. Abaixo disso, nenhum cartão é escondido e nenhuma lista aparece.
- **FR-3920**: Com termo, a tela MUST listar os resultados (FR-3917), na ordem do documento, até
  **25**. O resultado de campo MUST dizer a seção, o cartão, o rótulo e o valor atual (truncado em 80
  caracteres, com reticências, quando for longo) e oferecer «Ir ao campo»; o de cartão MUST dizer a
  seção e o cartão e oferecer «Ir ao cartão», que põe o foco no primeiro campo dele. Acima de 25, a
  lista MUST dizer quantos resultados há no total e pedir para refinar. A contagem MUST ser anunciada
  de forma educada a leitor de tela, como a de hoje.
- **FR-3921**: Os cartões continuam filtrados como hoje — esconder, nunca remover —, e o cartão MUST
  ficar visível quando **algum** campo dele corresponder. A seção sem cartão visível continua
  desaparecendo, e `Sobre esta Retificação` nunca desaparece.
- **FR-3922**: «Ir ao campo» MUST mostrar o cartão e a seção, se estiverem escondidos, trazer o campo
  à vista e pôr o foco **no controle** do campo. MUST funcionar sem mouse: é alcançável por Tab e
  ativável por Enter.
- **FR-3923**: Enter em «Encontrar» MUST NOT enviar o formulário (como hoje) e, havendo resultado,
  MUST levar o foco ao primeiro item da lista.
- **FR-3924**: A busca MUST NOT alterar valor de campo, MUST NOT enviar dado (o termo não tem
  `name`), e o campo escondido MUST continuar sendo enviado.
- **FR-3925**: A busca MUST NOT usar lista de termos equivalentes nesta feature (D-003).
- **FR-3926**: Com «Só o que eu alterei» ligado, a lista MUST considerar só os cartões que a marca
  deixa visíveis.

#### B. Conferir e voltar (M2)

- **FR-3927**: A tela MUST distinguir dois estados de um cartão, cada um com **palavra** própria além
  da cor (WCAG 1.4.1):
  - **«na proposta»**: o cartão tem conteúdo alterado pela proposta, segundo o servidor, na última
    conferência — ou, na edição, desde a abertura;
  - **«alterada»**: algum campo do cartão mudou nesta tela desde a última conferência ou desde a
    abertura (o comportamento de hoje).
- **FR-3928**: A **proposta** MUST ser, na criação, o conjunto de Alterações que «Criar Retificação»
  gravaria com o mesmo formulário (as digitadas e as dos gestos); na edição, o conjunto que
  «Gravar a Retificação» deixaria no ato inteiro, depois da fusão com o que ele já declara e das
  remoções desfeitas. O servidor MUST calculá-la com o mesmo código que deriva a gravação, e MUST
  NOT haver um segundo cálculo de diferença.
- **FR-3929**: O cartão MUST estar «na proposta» quando alguma Alteração da proposta incide sobre o
  conteúdo dele ou o remove. A linha acrescentada que a proposta faz nascer MUST estar «na proposta»
  ao voltar da conferência. Acrescentar ou remover uma entidade **aninhada** (linha do quadro,
  Modalidade, critério) MUST marcar só o cartão dela — ou a linha nova —, e nunca o do Perfil que a
  contém; o Perfil só se marca se um campo dele mudar (como «Modalidade que é a ampla concorrência»,
  que a Modalidade nova pode alterar). Na edição, a remoção já declarada MUST ser contada à parte
  (FR-3930), porque a entidade não tem cartão, e a contagem MUST ser a mesma do bloco «Remoções já
  declaradas» sem as desfeitas.
- **FR-3930**: A barra de ações MUST dizer os dois estados em frases separadas:
  - proposta: "N cartões com alteração na proposta" (ou "1 cartão…", ou "Nenhuma alteração na
    proposta"); na edição, acrescido de "e K remoções já declaradas" quando houver; na criação antes
    da primeira conferência, "Proposta ainda não conferida";
  - desde a conferência: "Nenhuma alteração nova desde a última conferência" ou "N campos alterados
    desde a última conferência"; antes da primeira conferência, as frases de hoje ("Nenhum campo
    alterado ainda", "N campos alterados"); na edição antes de conferir, "Nenhuma alteração nova
    nesta edição" ou "N campos alterados nesta edição".
  A contagem da proposta MUST ser por cartão (D-001), e a do segundo estado continua por campo, como
  hoje.
- **FR-3931**: «Só o que eu alterei» MUST mostrar os cartões em **qualquer** dos dois estados.
- **FR-3932**: Cada linha de «O que vai mudar» (e de «O que muda em relação ao rascunho», na edição)
  MUST oferecer «Ir ao campo», que leva ao campo da linha como em FR-3922; a linha que fala do cartão
  inteiro (remoção, acréscimo) MUST levar ao cartão. Os gestos continuam com «Ir ao cartão de origem»
  (051).
- **FR-3933**: As referências que ligam linha, marca e cartão MUST ser as opacas que a tela já usa
  (`cartao-<ref>`, `c-<ref>`); o HTML MUST NOT passar a conter caminho normativo (a FR-019 da `002`).
- **FR-3934**: Quando a conferência é recusada e não há proposta calculada, MUST NOT haver cartão «na
  proposta», e a barra MUST dizer "Proposta não conferida — veja a recusa acima" (D-008).

#### C. Nomear a versão-base (M3)

- **FR-3935**: Onde a tela compara com a versão-base, ela MUST declarar a base numa frase que diz:
  - o que a versão incorpora — "a Publicação original de DD/MM/AAAA" e, quando houver, "as
    Retificações nº X (DD/MM/AAAA) e nº Y (DD/MM/AAAA)", na ordem de publicação, lidas do que a
    versão registra ter aplicado (D-006);
  - a situação de vigência no instante da tela, no fuso institucional: **"vigora desde DD/MM/AAAA
    HH:MM"**, quando ela é a versão em vigor; **"ainda não vigora: passa a vigorar em DD/MM/AAAA
    HH:MM; até lá vigora uma versão anterior"**, quando o início é futuro; **"vigorou a partir de
    DD/MM/AAAA HH:MM e já não é a versão em vigor"**, quando ela foi sucedida.
- **FR-3936**: A escolha da versão-base MUST NOT mudar: na criação é a de hoje (a de maior início de
  vigência e, no empate, a materializada por último); na edição, a da Retificação. As referências
  dos campos, o campo oculto `base` e as precondições continuam como estão.
- **FR-3937**: Na tela Retificar, a frase da base MUST aparecer no «Como funciona» e acima da tabela
  do resumo. O texto MUST NOT chamar a base de "vigente" quando ela não vigora, e MUST NOT conter
  "Vigente hoje". A coluna MUST se chamar **«Na versão-base»** na criação e **«No rascunho»** na
  edição (D-007). No modo somente leitura, o título MUST deixar de ser "Conteúdo vigente" e a frase
  MUST aparecer.
- **FR-3938**: No detalhe da Retificação e nas confirmações de homologar, devolver e publicar, a
  coluna «Antes» MUST vir acompanhada da frase da base **daquela** Retificação.
- **FR-3939**: Esta feature MUST NOT mostrar o valor da versão que vigora hoje ao lado do da base (2ª
  pergunta da auditoria) nem oferecer reapontar a base (4ª).

#### D. Impeditivos na conferência (M4)

- **FR-3940**: «Ver o que vai mudar», na criação e na edição, quando a proposta tem ao
  menos uma Alteração, MUST conferir o conteúdo que a proposta produziria com **as mesmas funções, na
  mesma ordem e com os mesmos parâmetros** que «Criar Retificação» (ou «Gravar a Retificação») usa:
  as guardas do ato e `validate_for_publication` com o ato de Retificação e a topologia publicada,
  sem consulta à fonte do sorteio e sem marcos sorteados. MUST NOT haver regra nova, cópia de regra
  nem restrição temporal nova; o instante é o da conferência.
- **FR-3941**: A conferência MUST mostrar, numa seção própria antes do resumo, cada impeditivo com a
  **mesma frase** que compõe a recusa da criação (a criação as junta numa recusa só; a conferência as
  mostra uma por item), e, quando a criação pararia numa guarda de conteúdo antes dos achados, só a
  recusa dessa guarda, com o mesmo texto. As recusas que não são do conteúdo — estado do Edital ou do
  Processo, revisão da edição mudada, edição que esvaziaria o ato — continuam só na criação e na
  gravação, como hoje.
- **FR-3942**: Cada impeditivo MUST levar ao cartão onde ele mora quando a localização dele
  corresponder a um cartão, inclusive a linha acrescentada nesta tela; à primeira linha da coleção quando corresponder a uma coleção (as
  linhas do quadro de um Perfil, por exemplo); à seção quando só a seção for identificável; e a
  nenhum lugar, com a frase só, nos demais casos.
- **FR-3943**: A conferência MUST NOT gravar nada: nem Retificação, nem Alteração, nem evento de
  trilha, nem reserva de idempotência. (O artefato de arquivo enviado continua sendo guardado na
  conferência, como hoje — FR-035 da `020`.)
- **FR-3944**: «Criar Retificação» e «Gravar a Retificação» MUST continuar conferindo tudo, e MUST
  recusar quando o conteúdo tiver impeditivo, mesmo que a conferência anterior não o tenha mostrado.
  O botão MUST continuar oferecido quando há impeditivo, e a seção MUST dizer que a criação será
  recusada enquanto ele existir (D-004). Quando «Criar» ou «Gravar» é recusado por conteúdo, a tela
  que volta MUST mostrar a mesma seção, com os links, além da recusa no alto que já existe hoje.
- **FR-3945**: As advertências (achados não impeditivos) MUST NOT entrar na conferência; elas
  continuam nas confirmações de submeter e homologar (D-005).

#### E. Preservação, acessibilidade e verificação

- **FR-3946**: Retificação simples, múltipla e sucessiva, criação e edição, acrescentar, remover,
  troca de anexo, gestos de aplicar aos demais, modo somente leitura, idempotência, revisão da edição,
  submeter, homologar, devolver e publicar MUST funcionar como antes; as suítes existentes MUST passar
  sem afrouxar asserção.
- **FR-3947**: Todo estilo novo MUST morar em folha estática (a da tela Retificar), todo script novo
  em arquivo estático, e toda classe nova MUST ter regra na folha; nenhuma página da jornada MUST
  produzir violação da política de conteúdo.
- **FR-3948**: Nenhum elemento novo MUST produzir rolagem lateral a 375 px, e todos os controles novos
  MUST ter nome acessível que diga o destino ("Ir ao campo Vagas imediatas — Perfil DOC-INFO").
- **FR-3949**: A feature MUST ter jornada de navegador no grupo `navegador` cobrindo os cenários A,
  B, C, D e G da auditoria no Edital de demonstração e a localização do cenário E no Edital ampliado,
  com ao menos um percurso feito só pelo teclado.
- **FR-3950**: Depois da implementação, a medição da segunda etapa (*Critério de decisão da segunda
  etapa*, abaixo) MUST ser feita e registrada, e o resultado MUST ser apresentado ao usuário como
  insumo, sem virar escopo.

### Key Entities

- **Cartão da Retificação**: a linha editável (`fieldset.linha`) de uma entidade do conteúdo, com a
  referência opaca da posição. Ganha o estado «na proposta» do servidor.
- **Proposta**: o conjunto de Alterações Normativas que o ato gravaria agora. Não é persistida pela
  conferência; é recalculada a cada envio.
- **Versão-base**: a Versão Consolidada sobre a qual a tela compõe (criação) ou a Retificação foi
  composta (edição). Tem início de vigência e a lista do que aplicou. Nada se acrescenta a ela.
- **Impeditivo**: achado de conteúdo que a criação recusaria, com mensagem e localização. A
  localização vira, na tela, o caminho até um cartão — nunca o caminho normativo.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1173**: Nos cenários A (término das inscrições), B (vagas de uma linha do quadro) e C
  (requisitos de um Perfil), no Edital de demonstração **e** no ampliado, a pessoa leva o foco ao
  campo-alvo em **no máximo 2 ações** a partir da tela aberta (digitar o termo; ativar o resultado),
  sem rolar a página à mão. Na auditoria, o B levou 6.
- **SC-1174**: Para «vagas», «remuneração», «prazo» e «requisito» no Edital de demonstração, a lista
  da tela é **igual** à que as regras de FR-3917 e FR-3918 dão sobre o conteúdo, e contém o
  campo-alvo de cada cenário: «Vagas imediatas» de cada Perfil e de cada linha do quadro;
  «Remuneração» de cada Perfil; o prazo de recurso de cada marco; «Requisitos de participação» de
  cada Perfil. Há **zero** campos de texto longo achados pelo valor e **zero** cartões listados campo a
  campo só pelo nome. No ampliado, nenhum desses termos passa de 25 itens.
- **SC-1175**: No cenário D (três alterações em três seções), depois de «Ver o que vai mudar»:
  **3 de 3** cartões marcados «na proposta»; «Só o que eu alterei» mostra exatamente os 3; e cada
  uma das 3 linhas do resumo leva o foco ao campo dela em **1** ação.
- **SC-1176**: Nas mesmas condições, a barra mostra **duas** frases distintas, uma por estado, e
  nenhuma tela da jornada diz "Nada alterado desde a conferência" ao lado de uma proposta não vazia.
- **SC-1177**: Ao abrir a edição de uma Retificação devolvida, **100%** dos cartões que o ato altera
  estão marcados «na proposta», sem nenhuma ação.
- **SC-1178**: Com uma Retificação publicada de vigência futura, **nenhuma** das cinco telas
  (Retificar, detalhe da Retificação, homologar, devolver, publicar) contém "Vigente hoje", e todas
  dizem a data em que a base passa a vigorar; nas três situações de vigência, a frase é a de
  FR-3935.
- **SC-1179**: No cenário B, o impeditivo do quadro aparece na conferência com a **mesma frase** que
  compõe a recusa de «Criar», leva à linha do quadro em 1 ação, e **zero** Retificações são criadas
  pela conferência. Para cada formulário com impeditivo coberto pelos testes, o conjunto de frases da
  conferência é igual ao que a recusa da criação junta.
- **SC-1180**: A criação recusa em **100%** dos casos de teste em que o impeditivo surge entre a
  conferência e o «Criar» (Resultado registrado no intervalo), e a criação chama a mesma conferência
  de conteúdo de novo, mesmo depois de uma conferência sem impeditivo.
- **SC-1181**: As suítes existentes da Retificação passam sem asserção afrouxada; as jornadas de
  navegador registram **zero** violações da política de conteúdo e **zero** pixels de rolagem
  lateral a 375 px.
- **SC-1182**: A medição da segunda etapa está registrada com os números de *Critério de decisão da
  segunda etapa*, e a recomendação que sai da regra foi apresentada ao usuário.

## Critério de decisão da segunda etapa

O índice fixo ao lado, com um nível por Perfil (P2, `RU-09`), não entra no MVP. A pergunta que o
decide é se, **depois** de M1 e M2, ainda custa caro chegar a um lugar **sem saber um termo** para
buscar.

**O que se mede**, pelo mesmo roteiro automatizado da auditoria, no Edital ampliado, a 1280×900 e a
375 px:

1. **E1 — ir ao 3º Perfil**: da tela aberta até o primeiro campo do 3º Perfil, sem usar a busca.
2. **E2 — ir ao Cronograma depois de editar o último Perfil**: do último campo do último Perfil até o
   primeiro Evento, sem usar a busca.
3. **E3 — voltar ao resumo**: do último cartão editado até a tabela «O que vai mudar» depois de
   conferir.

Para cada um: o número de ações e a distância rolada à mão, em telas (altura da janela).

**A regra.** Se **algum** de E1 a E3 exigir mais de **3 ações** ou mais de **2 telas** de rolagem à
mão a 1280 px, a recomendação é especificar o índice fixo com nível por Perfil como a etapa
seguinte à homologação contextual. Se nenhum exceder, a recomendação é não fazê-lo, e repetir a
medição quando um Edital real maior que o ampliado entrar em Retificação. Em qualquer caso a decisão
é do usuário, e o relatório traz os números, e não só o veredito.

## Assumptions

- O Edital ampliado da auditoria (4 Perfis com 2 Modalidades cada, 11 Eventos) representa o porte
  dos Editais 57 e 59/2026; o 57 tem quadros com três Modalidades, de modo que é conservador.
- A política de conteúdo, o grupo `navegador` e o seletor de identidade da suíte são os de hoje.
- A conferência roda as mesmas leituras do banco que a criação roda; o custo dela cresce em uma
  passada de validação, e não em leitura por item (o plano mede).
- O limiar de 12 cartões para a busca existir continua; todo Edital publicado o passa.

## Compatibilidade com regras anteriores

- **A FR-019 da `002`** (o HTML não contém caminho): preservada; tudo se liga por referência opaca.
- **A conferência sem justificativa** (`formnovalidate`): preservada; M4 não exige Justificativa.
- **A edição da `103`** (revisão, fusão, remoções desfeitas): preservada; a proposta da edição é o
  resultado da mesma fusão.
- **Os gestos da `051`**: preservados, inclusive «Ir ao cartão de origem» e o número do título com
  gesto.
- **As advertências da `104`** nas confirmações: preservadas e não duplicadas.
- **A conferência da fonte do sorteio da `116`**: continua só na publicação (FR-3644 da `116`).

## Decisões

Propostas de desenho desta spec. **Aguardam a aprovação do usuário.**

### D-001 — A proposta se conta por cartão

"Alterações" tem três unidades na tela de hoje (linha do resumo, Alteração Normativa, campo). A marca
é por cartão, «Só o que eu alterei» filtra por cartão, e o caminho de volta chega a um cartão; contar
a proposta por cartão faz os três dizerem o mesmo número. A troca de arquivo (duas Alterações) e o
método do sorteio que nasce (uma Alteração, muitas linhas) deixam de produzir números que não batem.
O segundo estado continua por campo, porque é o que a pessoa acabou de digitar.

### D-002 — Valor só do campo curto e nominal; 2 caracteres; 25 itens

Texto longo inunda (17 Seções, descrições); números, datas e Sim/Não casam com quase tudo. O valor que
alguém procura pelo nome — a remuneração "R$ 4.000", a localidade, o nome do Documento, a Modalidade
escolhida — é curto. O teto de 25 cabe a lista de «vagas» do ampliado (12) com folga. Buscar dentro
de texto longo fica registrado, para depois da medição.

### D-003 — Nenhum termo equivalente no MVP

O revisor condicionou sinônimos a teste. Os candidatos que a auditoria mostrou — «recursal» → prazo do
recurso do marco (hoje a expressão «prazo recursal» acha a descrição do Evento de resultado, e não o
marco); «quadro» → linha do quadro de vagas — ficam registrados. A jornada de navegador mede se os
termos sem sinônimo bastam; a lista só nasce, em spec própria, se um cenário falhar por falta dela.

### D-004 — «Criar» continua oferecido com impeditivo

O impeditivo vale para o instante da conferência, e há regras que mudam de resposta com o tempo e
com o banco. Desabilitar o botão criaria um estado que pode estar velho nos dois sentidos. A criação
confere de novo e recusa com a mesma frase; a conferência avisa que isso vai acontecer.

### D-005 — Advertência fica fora da conferência

A criação não as usa; as telas de submeter e homologar já as mostram, calculadas sobre o conteúdo em
vigor na fronteira, que é outra base. Trazê-las aqui seria uma terceira superfície de aviso com outro
cálculo. **É a decisão desta spec que mais merece o olhar do usuário**: a auditoria falava em
"achados", e o revisor em "impeditivos".

### D-006 — A base se descreve pelo que incorpora

`source_publication` é a publicação que materializou a versão, que depois de uma publicação fora de
ordem de vigência não é "a Retificação da base". A lista do que a versão aplicou é a mesma que a
consolidação do documento da `054` já usa para dizer "retificado em".

**A numeração é a do detalhe do Edital**, que a pessoa tem ao lado: "Retificação nº N" com N a ordem
da publicação no Edital (a Publicação original é a nº 1, e a primeira Retificação, a nº 2). É a
numeração que a auditoria usou ("Retificação nº 3"). O relatório do Edital numera de outro jeito (a
primeira Retificação é a nº 1); a divergência é anterior a esta feature e fica registrada abaixo.

### D-007 — Na edição, a coluna é «No rascunho»

O resumo da edição compara com o rascunho, e a coluna mostra o que a própria Retificação já declara.
Chamá-la de base também seria falso.

### D-008 — Conferência recusada não marca nada

Sem proposta calculada, qualquer marca seria palpite. A frase da barra diz por que não há marca, e a
recusa está no alto da tela, como hoje.

### D-009 — A seção de impeditivos vem antes do resumo

É a resposta à pergunta "posso criar?", e vem antes de "o que vai mudar", como na revisão do Compor.
Sem impeditivo, a seção não aparece.

## Registrado, sem desenvolver

- **Duas numerações de Retificação.** O detalhe do Edital chama a primeira Retificação de "nº 2" (a
  ordem da publicação), e o relatório do Edital, de "nº 1". Esta spec segue o detalhe (D-006); unificar
  é decisão do usuário.
- Contagem «na proposta» por seção no índice «Ir para» (a maquete a mostra; é parte do P2).
- O cartão "Documentos publicados" do Edital não distingue "vigora" de "vigorará" (cap. G1 da
  auditoria); é a 2ª pergunta.
- Destaque do termo no resultado, Esc para limpar e "voltar à busca" depois de «Ir ao campo».
- A página que volta da conferência continua no topo (`RU-09b`); o resumo está lá.
- Busca dentro de texto longo e os sinônimos de D-003.
- A confirmação de Submeter sem a lista (`RU-10`), a prévia do documento (`RU-11`) e o conflito entre
  Retificações em curso (`RU-12`).
