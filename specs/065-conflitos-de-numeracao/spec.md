# Feature Specification: Detecção de conflitos de numeração no Edital

**Feature Branch**: `claude/065-conflitos-de-numeracao` — criada sobre a `main` `fd18add4`, com a
auditoria que fundamenta a feature no primeiro commit.

**Created**: 2026-10-08

**Status**: Implementado — decisões fechadas pelo responsável pelo produto em 08/10/2026 (ver *Decisões*); verificação em [verificacao.md](verificacao.md)

**Input**: o achado **ED-01** da [auditoria do Edital em PDF de 08/10/2026](../../doc/auditoria-edital-pdf-2026-10-08.md)
e o pedido do responsável pelo produto, na mesma data, de tratá-lo como a próxima feature, com estes
limites — aqui citados como 1º a 6º:

1. detectar a numeração de subitens incompatível com a seção calculada;
2. apresentar seção, trecho, motivo e orientação de correção;
3. distinguir conflito comprovado de suspeita;
4. propor a severidade de cada achado, separando requisito existente de decisão ainda necessária;
5. avaliar remissões só até onde a estrutura disponível permitir, dizendo os limites;
6. não renumerar nem reescrever texto, não afirmar que uma remissão está certa porque o item citado
   existe, e não incluir numeração automática, mudança em recursos nem reformulação do PDF.

E as respostas do responsável pelo produto às perguntas desta spec, na mesma data — a origem de
`D-001` a `D-003`:

7. **Q1: A** — o conflito comprovado de numeração é impeditivo na submissão e na publicação do Edital;
8. **Q2: A** — na Retificação, todos os achados desta feature são avisos, inclusive o conflito que a
   própria Retificação introduz;
9. remissões e suspeitas são avisos, e a remissão é procurada em todo texto livre impresso — sem que
   achar um destino único prove que a referência está correta.

> **Faixa de identificadores.** Abre em **FR-1198**, **SC-462** e **UX-159**. O teto medido em
> 08/10/2026 em todas as worktrees e nos PRs abertos, com quatro dígitos, era `FR-1197` e `SC-461`
> (da `064`, já na `main`) e cento e cinquenta e oito para os requisitos de experiência — este da `063`,
> em PR aberto, e por isso escrito por extenso. As decisões são as três de *Decisões*, `D-001` a
> `D-003`.

**A frase que governa:**

> O número que quem elabora digita tem de ser o número que o documento imprime — e, quando não é, o
> sistema diz onde, sem corrigir por conta própria.

**E a frase que mantém o corte:**

> Esta feature lê o texto e avisa. Ela não muda texto, não muda o PDF, não muda Edital publicado e não
> afirma que remissão alguma está correta.

---

## Por que esta feature existe

### O problema

O catálogo de seções do Edital tem numeração **calculada**: cada seção que sai no documento recebe o
número pela mesma regra na etapa Conteúdo, na Revisão, na Retificação e no PDF (`054`, `FR-985`). A
seção textual vazia não sai e não recebe número (`FR-982`), e as seguintes avançam.

O texto das seções textuais, porém, é **transcrito** do Word do setor (a decisão E10 = B da `DP-20`,
28/09/2026), e os Editais do Cefor numeram todo subitem — "4.1", "4.2" — para que o próprio Edital,
o candidato e a comissão possam citá-los. O número que o autor digita é texto, e o sistema não o
confere. Quando a seção do catálogo sai com outro número que a seção do original, o documento oficial
passa a imprimir subitens que não pertencem à seção em que estão, e as remissões do texto ("conforme o
item 8.1") passam a apontar para outro lugar.

É a "propriedade 2" da `DP-20` (`doc/decisoes-pendentes-da-consolidacao.md`) — *"o '4.1' que o autor
digitar no texto é número dele, e não do documento"* —, registrada como **RC-141** na auditoria de
consolidação de 26/09 e deixada fora da `054` ("subitem numerado" está no *Out of Scope* dela). Desde
28/09 o PDF do sistema é o ato oficial do piloto: o que ele imprime errado só sai por Retificação.

### As evidências

| # | Evidência | Onde se verifica |
|---|---|---|
| 1 | No cenário B da auditoria (cadastro de reserva de tutores, com a numeração transcrita como no Word), **15 parágrafos em 5 seções** começam por número de outra seção: "Da Inscrição" sai como **4** e seus parágrafos começam por 3.1 a 3.4; "Da Verificação da Autodeclaração" sai como **6**, com 4.1 a 4.3; "Dos Recursos" sai como **11**, com 8.1 a 8.3; "Da Convocação" sai como **12**, com 11.1 e 11.2; "Disposições Finais" sai como **15**, com 14.1 a 14.3. As duas seções que saem com o número do original (1 e 2, com 8 parágrafos) não têm conflito. | `doc/auditoria-edital-pdf-2026-10-08/pdf/B-publicado.pdf`, pp. 39–44; conferido parágrafo a parágrafo sobre o conteúdo publicado, pela mesma regra de numeração do documento |
| 2 | No mesmo documento, "Dos Recursos" diz *"…qualquer forma distinta da prevista no item 8.1"*. O documento tem **dois** itens 8.1: a Etapa "Prova de títulos…" (subseção gerada da seção 8, p. 41) e o primeiro parágrafo da própria seção de recursos, digitado como 8.1 (p. 43). **O item citado existe — e a remissão está errada**: é o caso exato em que conferir só a existência daria um falso "correto". | idem, pp. 41 e 43 |
| 3 | No cenário A (pós-graduação EaD, texto sem numeração digitada), **nenhum** parágrafo começa por número de subitem, e nenhum achado seria esperado. | `pdf/A-publicado.pdf` |
| 4 | Na transcrição real do Edital 89/2026 (30/09), os subitens 6.x saíram sob "8. Critérios de Classificação", e 12.x, 8.x, 11.x e 13.x sob "11. Da Convocação". | `doc/achado-edital-89-2026-bolsista-no-catalogo.md`, §1 |
| 5 | Na verificação do 28/2026 contra o catálogo da `054`, a numeração do original e a do documento divergem a partir da seção 9. | `DP-20`; `doc/achado-edital-89-2026-bolsista-no-catalogo.md` |
| 6 | Nenhuma validação compara a numeração digitada com a calculada. A etapa Conteúdo mostra o número calculado na legenda de cada seção (`054`, `FR-985`), mas não avisa quando o texto digitado diz outro. A submissão do cenário B passou sem achado algum sobre numeração. | código de validação da publicação; log da submissão do cenário B |
| 7 | Nos nove Editais reais da amostra lidos para esta spec, há **77 remissões internas** do tipo "item/itens/subitem N.N" e 15 a "Quadro N" — a remissão é parte normal do texto que se transcreve, e não exceção. | amostra em `~/Downloads`, extraída para texto (contagem aproximada, por linha) |

### Por que agora, e por que só isto

É o primeiro P0 da auditoria, e o mais barato de fechar sem decisão de produto grande: a detecção
lê o que já existe. A alternativa estrutural — o sistema numerar os parágrafos das seções textuais — é
maior, muda o que o autor escreve e o documento, e fica para evolução posterior (*O que esta feature
não cobre*).

---

## User Scenarios & Testing *(mandatory)*

**Atores.** Quem elabora o Edital (etapa Conteúdo e Revisão), quem homologa (que confere a prévia
contra o original, pela E10 = B) e quem publica. O candidato é o beneficiário: ele lê o documento em
que a numeração e as remissões passam a ter sido conferidas. As permissões são as de hoje.

### User Story 1 — Quem elabora descobre o subitem com número de outra seção (Priority: P1)

Quem elabora transcreve o Edital do Word. A seção "Da Inscrição" do original é a 3, mas no catálogo
ela sai como 4, porque a seção de Perfis vem antes. Ao abrir a etapa Conteúdo ou a Revisão, a pessoa
vê um achado que diz: a seção «Da Inscrição» sai no documento como 4, e os parágrafos 1 a 4 começam
por 3.1 a 3.4 — com o começo de cada parágrafo, para encontrá-lo no campo —, e que a numeração
digitada precisa começar por 4.

**Why this priority**: é o ED-01 inteiro. Sem isto, o ato oficial publica subitens fora da sua seção,
e o defeito só é visto por quem compara o PDF com o original linha a linha.

**Independent Test**: compor o rascunho do cenário B, abrir a etapa Conteúdo e a Revisão, e conferir
que cada uma das 5 seções em conflito tem um achado que nomeia a seção, o número impresso, os
parágrafos, o número digitado em cada um e o começo literal de cada parágrafo.

**Acceptance Scenarios**:

1. **Given** uma seção textual que sai como 4 e cujos parágrafos começam por 3.1, 3.2, 3.3 e 3.4,
   **When** quem elabora abre a etapa Conteúdo ou a Revisão, **Then** vê um achado de **conflito
   comprovado** daquela seção, com os quatro parágrafos identificados, o número digitado em cada um, o
   começo literal de cada parágrafo e a orientação de que os subitens desta seção começam por 4.
2. **Given** o achado do cenário anterior, **When** a pessoa segue o link do achado, **Then** chega
   ao campo daquela seção na etapa Conteúdo, cuja legenda mostra o mesmo número 4 que o achado nomeia.
3. **Given** uma seção que sai como 2 e cujos parágrafos começam por 2.1 a 2.4, **When** a Revisão é
   aberta, **Then** nenhum achado de numeração é exibido para ela.
4. **Given** o preâmbulo — que sai sem número — com um parágrafo que começa por 1.1, **When** a
   Revisão é aberta, **Then** há um conflito comprovado que diz que o preâmbulo não tem número e o
   parágrafo não pode carregar subitem.
5. **Given** as seções corrigidas e sem achado, **When** quem elabora esvazia uma seção anterior a
   elas e salva, **Then** as seguintes passam a sair com número menor, e os achados reaparecem com os
   números novos — a conferência é sempre contra o documento de agora.
6. **Given** um conflito comprovado, **When** quem elabora salva o texto, **Then** o sistema não
   muda nem uma letra do que foi escrito.

---

### User Story 2 — Quem elabora descobre a remissão que não aponta para um item só (Priority: P1)

O texto de "Dos Recursos" diz "conforme o item 8.1". No documento, há duas coisas numeradas 8.1. Ou
há nenhuma. A pessoa vê um aviso que diz quais itens têm aquele número no documento — ou que nenhum
tem — e que o sistema não sabe qual item o texto quis citar.

**Why this priority**: a remissão é a forma como o Edital, a comissão e o candidato citam a norma —
77 nos nove Editais da amostra —, e ela quebra junto com a numeração. Mas é também onde a detecção
tem limite: o sistema não sabe o que o autor quis dizer, e por isso o achado é mais estreito.

**Independent Test**: no rascunho do cenário B, conferir que "item 8.1" em "Dos Recursos" produz um
aviso de remissão ambígua que nomeia a Etapa 8.1 e o parágrafo digitado como 8.1; e que, depois de a
numeração da seção ser corrigida e a remissão reescrita como "item 11.1", nada é exibido — e nada
afirma que ela está certa.

**Acceptance Scenarios**:

1. **Given** um texto que cita "item 8.1" e um documento com dois itens 8.1, **When** a Revisão é
   aberta, **Then** há um aviso de **remissão ambígua** que nomeia cada um dos itens 8.1 do documento,
   e diz que o sistema não sabe a qual deles o texto se refere.
2. **Given** um texto que cita "item 7.3" e um documento sem item 7.3, **When** a Revisão é aberta,
   **Then** há um aviso de **remissão sem destino neste documento**, que diz como deixar explícita a
   remissão a outro ato, se for o caso.
3. **Given** um texto que cita "item 4.1 da Resolução CS nº 10/2017" ou "item 2.3 do Anexo II",
   **When** a Revisão é aberta, **Then** nenhum aviso é exibido para essa remissão.
4. **Given** um texto que cita "item 4.2" e um documento com exatamente um item 4.2, **When** a
   Revisão é aberta, **Then** nenhum achado é exibido **e** nenhuma superfície diz que a remissão foi
   conferida, verificada ou está correta.
5. **Given** um texto que cita "Quadro 2", **When** a Revisão é aberta, **Then** há um aviso de
   **suspeita** que diz que as tabelas do documento se chamam "Tabela N" e que, se o quadro está num
   Anexo, a remissão deve citar o Anexo.

---

### User Story 3 — Quem homologa e quem publica não deixam passar o conflito (Priority: P2)

O conflito comprovado de numeração impede a submissão e a publicação do Edital (`D-001`), como os
demais impeditivos do sistema: o ato oficial não sai com subitem fora da sua seção. Os avisos —
remissões e suspeitas — não impedem, e quem homologa os vê com o mesmo texto que quem elabora viu
(E10 = B).

**Why this priority**: a E10 = B põe a conferência na homologação, mas a conferência humana não é
garantia; o impeditivo é. A jornada da elaboração (User Stories 1 e 2) entrega valor antes desta.

**Independent Test**: submeter o rascunho do cenário B sem correções e conferir que a submissão é
recusada pelos 5 conflitos; depois corrigir, submeter, homologar e publicar, e conferir no PDF
publicado que todo parágrafo numerado começa pelo número da sua seção.

**Acceptance Scenarios**:

1. **Given** um rascunho com conflito comprovado de numeração, **When** quem elabora submete,
   **Then** a submissão é recusada, e a recusa nomeia a seção, os parágrafos e os números, como a
   Revisão.
2. **Given** um rascunho só com avisos desta feature (remissão ambígua, sem destino, suspeita),
   **When** quem elabora submete, **Then** a submissão é aceita, e quem homologa vê os avisos com o
   mesmo texto que quem elabora viu.
3. **Given** um Edital homologado sem conflito, **When** a publicação é conferida de novo,
   **Then** a mesma regra é aplicada, e um conflito comprovado impediria a publicação.
4. **Given** o cenário B corrigido segundo os achados, **When** é publicado, **Then** o documento
   publicado tem, em cada seção, todos os parágrafos numerados começando pelo número da seção, e a
   remissão "item 11.1" aponta para um item só.

---

### User Story 4 — O que já foi publicado não muda (Priority: P2)

Um Edital publicado antes desta feature, com numeração digitada em conflito, continua exatamente
como está: o documento não é recomposto, a página dele não passa a mostrar achados de numeração, e o
conteúdo não muda. Se ele for retificado, a numeração do consolidado é conferida e acusada só como
aviso (`D-002`): retificar um ato antigo não exige corrigir toda a numeração dele.

**Why this priority**: a Constituição (Princípio II) não admite corrigir ato publicado senão por
Retificação; uma regra nova não pode passar a acusar o ato antigo onde ninguém pode corrigi-lo.

**Independent Test**: com um Edital publicado no cenário B sem correção, implantar a feature e
conferir que o documento publicado tem os mesmos bytes e que a página do Edital publicado não exibe
achado de numeração.

**Acceptance Scenarios**:

1. **Given** um Edital publicado com conflitos de numeração, **When** a feature entra em produção,
   **Then** o documento publicado tem os mesmos bytes e o mesmo resumo criptográfico de antes.
2. **Given** o mesmo Edital publicado, **When** alguém abre a página dele na gestão, **Then** nenhum
   achado de numeração é exibido.
3. **Given** uma Retificação em composição sobre esse Edital, **When** quem retifica confere, **Then**
   os achados de numeração e de remissão do consolidado aparecem como avisos, e a Retificação pode ser
   publicada.
4. **Given** uma Retificação que esvazia uma seção textual e desloca a numeração das seguintes,
   **When** quem retifica confere, **Then** os conflitos que ela mesma cria aparecem como avisos — e
   **não** impedem a publicação (`D-002`): o consolidado sai com eles se ninguém os corrigir.

---

### Edge Cases

*Os casos abaixo são requisitos, e não ilustração (ver a nota em Assumptions).*

**Números legítimos que não podem gerar achado** — começo de parágrafo:

| Forma | Exemplo | Por que não é subitem |
|---|---|---|
| Data | "20/10/2026, às 9h…", "24.08.2026 — …" | barra, ou grupo de quatro algarismos |
| Número de lei, decreto, portaria | "13.146/2015, que considera…", "8.112/1990" (comum quando o texto colado traz quebra de linha no meio da frase) | grupo de três algarismos, ou barra em seguida |
| Valor | "1.000,00 (mil reais)…", "R$ 1.500,00" | vírgula decimal; grupo de três algarismos |
| Carga horária e hora | "30h", "1.000 horas", "14h30", "08:00" | unidade ou dois-pontos em seguida |
| Percentual | "25% das vagas…" | "%" em seguida |
| Ordinal | "1º …", "2ª chamada…" | "º"/"ª" em seguida |
| Decimal com unidade | "7.5 pontos", "6.0 (seis) pontos" | palavra de unidade em seguida |
| Decimal com multiplicador ou grandeza | "1.2 mil candidatos", "3.5 vezes o valor", "1.5 salário mínimo" | palavra de unidade em seguida (`D-017`) |
| Intervalo de horas | "8.30 às 12.00 – atendimento", "13.00 às 17.30h" | a expressão inteira é intervalo de horas (`FR-1199`, `D-017`) |
| Intervalo de datas | "10.10 a 20.10 – período de recurso", "25.10 a 05.11.2026", "10.10 até 20.10" | a expressão inteira é intervalo de datas (`FR-1199`, `D-017`) |
| Número de processo, CEP, telefone | "23185.000123/2026-11", "29.000-000", "(27) 3198-0925" | grupos com mais de dois algarismos, hífen ou parêntese |
| Ano solto | "2026. Fica…" | um grupo só |
| Lista de um nível | "1. Ler o Edital", "1) …", "I – …", "a) …" | não é número de subitem (dois ou mais grupos) |
| Invisível colado do Word | "4.1​ A inscrição…" (com espaço de largura zero depois do número), numa seção que sai como 4 | a conferência é sobre o texto que o documento imprime, já normalizado — não há conflito |
| Zero à esquerda | "04.1 …" numa seção que sai como 4 | comparação numérica, como o anúncio do ato já faz com o número do Edital |

**Numeração e composição:**

- **Subitem de três ou quatro níveis.** "4.2.1" pertence à seção 4: conta o primeiro grupo.
- **Separadores depois do número.** "4.1.", "4.1 –", "4.1 -", "4.1)" e "4.1" no fim do parágrafo são
  números de subitem.
- **Marcador antes do número.** "• 4.1 …" e espaços iniciais são ignorados na leitura do começo do
  parágrafo.
- **Parágrafo como o documento o compõe.** Cada quebra de linha separa parágrafo, e linhas em branco
  não contam (é como o documento compõe hoje): o ordinal do parágrafo no achado é o desta contagem.
- **Seção misturada.** Uma seção que sai como 11 com parágrafos 12.x, 8.x e 11.x (o caso do 89/2026)
  tem conflito nos 12.x e 8.x, e não nos 11.x.
- **Seção vazia.** Não sai no documento, não tem número e não é conferida.
- **Seção com norma acrescentada pelo sistema** (o teto na Inscrição, a declaração na Matrícula). Só
  o texto de quem elabora é conferido; a frase do sistema não tem número.
- **Título do original colado no texto.** "11. DA CONVOCAÇÃO", em caixa alta, como primeiro parágrafo
  de uma seção que sai como 12: **suspeita**, e não conflito comprovado — "11." sozinho também pode
  abrir lista. Com o mesmo número da seção, não é conflito de numeração (é título repetido) e fica
  fora desta feature.
- **Edital criado a partir de outro** (`023`). O texto copiado é conferido como qualquer outro, contra
  a numeração do Edital novo.

**Remissões:**

- **Formas reconhecidas.** "item", "itens", "subitem", "subitens" seguidos de número de subitem; lista
  ("itens 4.1, 4.2 e 4.3") e intervalo ("itens 4.1 a 4.5", conferindo as duas pontas); "Tabela N";
  "Quadro N". Qualquer outra forma não é lida (*Limitações*).
- **Remissão a outro ato ou a anexo.** Quando, logo depois do número, o texto nomeia outro ato ("do
  Edital nº…", "da Resolução", "da Portaria", "da Lei", "do Decreto", "do art.", "da Instrução
  Normativa") ou um Anexo ("do Anexo II"), a remissão não é deste documento e não é conferida. "Deste
  Edital" mantém a remissão como interna.
- **Remissão a número que só existe como subitem em conflito.** Se o único item com aquele número é um
  parágrafo digitado fora da sua seção, o aviso diz isso — o número existe no documento, mas no lugar
  errado.
- **Remissão a nível único** ("item 5", "seção 9"): não é conferida, salvo quando o número passa do
  total de seções do documento (sem destino).
- **Número maior que o de subitem** ("item 10.1.1.1.1", "item 4.123"): a remissão é ignorada
  inteira, e não lida como remissão ao prefixo ("10.1.1.1", "4") — que seria um item que o texto não
  citou. Numa lista, só o número maior sai dela (`D-017`).
- **"Tabela N"** existente: nenhum achado. Acima do número de tabelas do documento: sem destino. A
  numeração das tabelas muda com o número de Perfis, e é por isso que ela entra.
- **Mesma remissão repetida** na mesma seção: um achado só.
- **Onde se procura remissão.** Em todo texto livre que o documento imprime — seções textuais, nome e
  instruções dos documentos exigidos, descrição, atribuições e requisitos dos Perfis, descrição e local
  dos Eventos —, porque a remissão aparece também ali (a alínea "e" dos documentos do 28/2026 remete ao
  item 5.14). O conflito de **numeração** só é procurado nas seções textuais, que são as que têm
  subitens.

**Ciclo de vida:**

- **Achados refeitos a cada leitura.** Mudar qualquer coisa que mude a numeração — esvaziar ou
  preencher uma seção textual, mudar o número de Perfis ou de Etapas — refaz os achados.
- **Prévia e documento.** Nenhuma marca no PDF, nem na prévia nem no publicado.
- **Edital publicado fora de Retificação.** Não é conferido (`046`, `FR-755`).
- **Retificação que introduz conflito.** Esvaziar ou preencher uma seção textual, ou reescrever um
  texto, pode criar conflito no consolidado. Ele é acusado como aviso, e não impede a Retificação
  (`D-002`). É a consequência aceita da decisão, e o aviso é a única proteção.

---

## Requirements *(mandatory)*

### Functional Requirements

**A numeração digitada**

- **FR-1198**: Em cada seção textual que sai no documento, o sistema MUST ler o começo de cada
  parágrafo, contado como o documento o compõe, sobre o texto já normalizado como o documento o
  imprime.
- **FR-1199**: É **número de subitem** o começo de parágrafo formado por dois a quatro grupos de um ou
  dois algarismos separados por ponto, seguido de espaço, ponto, parêntese de fechamento, hífen,
  travessão ou do fim do parágrafo — e **não** seguido de algarismo, barra, vírgula, dois-pontos,
  "%", "º", "ª" ou palavra de unidade. Os casos legítimos da tabela de *Edge Cases* MUST NOT ser
  números de subitem. O primeiro grupo é comparado como número, e não como texto. **Também não é
  número de subitem** o começo de parágrafo que forma, inteiro, um **intervalo de horas** — duas
  horas "H.MM" (hora até 23, minutos de dois algarismos até 59) ligadas por "às" — ou um **intervalo
  de datas** — dois "D.MM" (dia de 1 a 31, mês de dois algarismos de 01 a 12, dias diferentes) ligados
  por "a" ou "até", com o ano opcional na segunda ponta. A exclusão é da expressão inteira, e não do
  número seguido de "a" ou "às": o intervalo de subitens ("1.1 a 1.3", "10.10 a 10.12") continua
  número de subitem (`D-017`).
- **FR-1200**: É **conflito comprovado de numeração** o parágrafo cujo número de subitem tem o
  primeiro grupo diferente do número com que a seção sai no documento, e qualquer número de subitem no
  preâmbulo, que sai sem número.
- **FR-1201**: É **suspeita de título transcrito** o parágrafo que começa por um número de um grupo
  seguido de ponto ou hífen e de texto inteiramente em caixa alta, quando esse número é diferente do da
  seção.
- **FR-1202**: O número da seção usado na comparação MUST ser o que o documento imprimiria naquele
  momento, pela mesma regra de `FR-985` da `054`; uma mudança no conteúdo que mude a numeração MUST
  refazer os achados.
- **FR-1203**: O sistema MUST NOT renumerar, reescrever, retirar ou substituir texto, nem oferecer
  ação que o faça. A correção é sempre de quem elabora.

**As remissões**

- **FR-1204**: É **remissão interna** a menção, em texto livre que o documento imprime, a "item",
  "itens", "subitem" ou "subitens" seguidos de número de subitem (inclusive em lista e intervalo), a
  "Tabela N" e a "Quadro N" — salvo quando o texto, logo depois do número, nomeia outro ato ou um
  Anexo, nas formas dos *Edge Cases*.
- **FR-1205**: Os **itens do documento** são os números que o documento imprime como identificação: o
  das seções, o das subseções que o sistema gera (Perfis, subseções comuns de atribuições, Etapas), o
  dos parágrafos das seções textuais que começam por número de subitem, e o das legendas "Tabela N" —
  todos da mesma composição que produz o documento.
- **FR-1206**: É **remissão ambígua** a remissão interna cujo número corresponde a mais de um item do
  documento. O achado MUST nomear cada um desses itens.
- **FR-1207**: É **remissão sem destino neste documento** a remissão interna cujo número não
  corresponde a item algum do documento.
- **FR-1208**: É **suspeita de remissão** a remissão a "Quadro N", que o documento não tem, e a
  remissão cujo único destino é um parágrafo em conflito comprovado de numeração.
- **FR-1209**: A remissão cujo número corresponde a exatamente um item do documento, fora do caso de
  `FR-1208`, MUST NOT gerar achado, e nenhuma superfície MUST dizer que ela foi conferida, verificada
  ou está correta — nem contá-la entre "remissões conferidas".

**A classificação e onde os achados aparecem**

- **FR-1210**: O conflito comprovado de numeração MUST ser **impeditivo** no Edital: ele impede a
  submissão e a publicação (`D-001`).
- **FR-1211**: A remissão ambígua, a remissão sem destino e as suspeitas MUST ser **avisos**, e nunca
  impeditivos — pela mesma razão da remissão a anexo sem rótulo (RC-21, decisão do usuário de
  28/09/2026): a remissão pode ser a outro ato, e o sistema não tem como distinguir sempre (`D-003`).
- **FR-1212**: Os achados MUST aparecer nas mesmas superfícies em que as pendências do Edital em
  elaboração já aparecem — a etapa Conteúdo, a Revisão, a página do Edital e a submissão —, e o achado
  sobre texto de seção MUST levar ao campo daquela seção na etapa Conteúdo (`UX-160`). O
  impeditivo MUST impedir a submissão e a publicação como os demais, e a recusa MUST trazer a mesma
  mensagem da Revisão.
- **FR-1213**: Na Retificação, todos os achados desta feature sobre o conteúdo consolidado MUST ser
  **avisos**, inclusive o conflito comprovado e o que a própria Retificação introduz, e nenhum deles
  MUST impedir a Retificação (`D-002`). Os avisos MUST aparecer onde a Retificação já mostra os seus
  achados antes de ser submetida e publicada.

**O que cada achado diz**

- **FR-1214**: Cada achado de numeração MUST identificar a seção pelo título e pelo número com que sai
  no documento (ou "o preâmbulo"), cada parágrafo afetado pelo ordinal, o número digitado em cada um,
  o começo literal de cada parágrafo — até oitenta caracteres, o bastante para encontrá-lo por busca
  no campo — e a orientação de correção, que diz por qual número os subitens da seção começam.
- **FR-1215**: Os parágrafos de uma mesma seção com conflito MUST sair num achado só, que os enumera,
  e não num achado por parágrafo.
- **FR-1216**: Cada achado de remissão MUST citar a remissão literalmente, identificar a seção ou o
  campo e o parágrafo em que está, dizer o motivo (quais itens têm o número, ou que nenhum tem) e dizer
  que o sistema não sabe qual item o texto quis citar.
- **FR-1217**: Cada achado MUST dizer se é **conflito comprovado** ou **suspeita**.

**O que não muda**

- **FR-1218**: O Edital publicado MUST NOT ser conferido por esta regra fora de uma Retificação em
  composição, e nenhum documento publicado MUST ser recomposto.
- **FR-1219**: O documento — prévia e publicado — MUST NOT mudar por esta feature: a mesma versão
  produz os mesmos bytes de antes.
- **FR-1220**: A conferência MUST NOT criar dado novo nem alterar o conteúdo do Edital; ela é lida a
  cada vez sobre o conteúdo que seria publicado.

### Requisitos de experiência

- **UX-159**: As mensagens MUST usar a linguagem de quem elabora — "seção", "parágrafo", "número",
  "remissão" — e o título da seção como a tela o mostra; nenhum código interno, caminho ou nome de
  campo.
- **UX-160**: O número da seção que o achado nomeia MUST ser o mesmo que a legenda da seção mostra na
  etapa Conteúdo naquele momento.
- **UX-161**: Os achados de numeração e de remissão de uma seção MUST ficar juntos, na ordem das
  seções do documento, para que quem corrige percorra o texto uma vez.

### Exemplos de mensagem

Exemplos normativos do tom e do conteúdo; a redação final é do plano, desde que cumpra `FR-1214` a
`FR-1217` e `UX-159` a `UX-161`. O primeiro e o terceiro vêm do cenário B, com os trechos literais; os demais são ilustrativos.

| Tipo | Mensagem |
|---|---|
| Conflito comprovado (subitem) | **Conflito de numeração — comprovado.** A seção «Da Inscrição» sai no documento como **4**, e 4 parágrafos começam por número de outra seção: parágrafo 1, «3.1 A inscrição será realizada exclusivamente pelo sistema de inscrições…»; parágrafo 2, «3.2 O candidato deverá anexar, em arquivo PDF único…»; parágrafo 3, «3.3 Não haverá conferência de documentação…»; parágrafo 4, «3.4 O candidato que enviar documentação com quantidade…». No documento, os subitens desta seção começam por 4. Corrija a numeração no texto da seção. |
| Conflito comprovado (preâmbulo) | **Conflito de numeração — comprovado.** O preâmbulo sai no documento sem número, e o parágrafo 2 começa por «1.1 …». Subitem numerado não cabe no preâmbulo: leve o parágrafo para a seção a que ele pertence ou retire o número. |
| Remissão ambígua | **Remissão ambígua.** A seção «Dos Recursos» (11) cita o «item 8.1» no parágrafo 3. Este documento tem dois itens 8.1: a Etapa «Prova de títulos, conforme a Ficha de Avaliação do Anexo IV…» e o parágrafo 1 desta mesma seção, digitado como 8.1. O sistema não sabe a qual deles o texto se refere: confira a remissão e a numeração da seção. |
| Remissão sem destino | **Remissão sem destino neste documento.** A seção «Da Convocação» (12) cita o «item 7.3» no parágrafo 1, e este documento não tem item 7.3. Se a remissão é a outro ato, deixe isso explícito no texto (por exemplo, «item 7.3 do Edital nº …»); se é a este Edital, corrija o número. |
| Suspeita (quadro) | **Remissão a conferir — suspeita.** A seção «Da Inscrição» (4) cita o «Quadro 2» no parágrafo 3. As tabelas deste documento se chamam «Tabela N», e nenhuma se chama «Quadro». Se o quadro está num Anexo, cite o Anexo («Quadro 2 do Anexo III»); se é uma tabela deste documento, use o nome com que ela sai. |
| Suspeita (remissão a subitem em conflito) | **Remissão a conferir — suspeita.** A seção «Disposições Finais» (15) cita o «item 9.4». O único item 9.4 deste documento é o parágrafo 4 da seção «Dos Recursos», que sai como 11 — o número existe, mas fora da sua seção. Corrija a numeração da seção e confira a remissão. |
| Suspeita (título transcrito) | **Numeração a conferir — suspeita.** O parágrafo 1 da seção «Da Convocação» (12) parece o título de uma seção do original: «11. DA CONVOCAÇÃO». O documento já imprime o título da seção; confira se a linha deve sair do texto. |

### Severidade — o que estava decidido e o que esta spec decidiu

| Achado | Severidade proposta | Base | Precisa de decisão? |
|---|---|---|---|
| Conflito comprovado de numeração, no Edital | **Impeditivo** | Constituição, Princípio IV (classificar em informação, aviso ou impeditivo e bloquear diante do impeditivo); com a definição estreita de `FR-1199` e `FR-1200`, "3.1" dentro da seção 4 sempre se lê como o item 3.1 deste Edital | Decidida — `D-001` |
| Remissão ambígua | Aviso | precedente do RC-21 (decisão do usuário de 28/09): a remissão pode ser a outro ato | Decidida — `D-003` |
| Remissão sem destino neste documento | Aviso | idem | Decidida — `D-003` |
| Suspeitas (título transcrito, quadro, remissão a subitem em conflito) | Aviso | por definição, o sistema não tem como comprovar | Decidida — `D-003` |
| Qualquer achado desta feature na Retificação | Aviso | retificar um ato antigo não pode exigir corrigir toda a numeração dele; o RC-21 nem roda na Retificação, e aqui o aviso roda porque só a Retificação desloca a numeração do consolidado | Decidida — `D-002` |

### Key Entities

Nenhuma entidade nova. A feature lê:

- **Seção textual do Edital** — o texto que quem elabora escreve, dividido em parágrafos como o
  documento o compõe.
- **Numeração do documento** — o número com que cada seção sai, e os números das subseções geradas e
  das tabelas, pela regra única de `FR-985`.
- **Achado de validação** — a pendência que já existe, com severidade, mensagem e o destino de
  correção; esta feature acrescenta tipos, e não estrutura.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-462**: No rascunho do cenário B da auditoria, **15 de 15** parágrafos em conflito são acusados,
  agrupados em **5** achados (um por seção), cada um com o número impresso da seção, o número digitado
  e o começo literal de cada parágrafo; as **2** seções coerentes (8 parágrafos) não têm achado.
- **SC-463**: No mesmo rascunho, a remissão "item 8.1" de "Dos Recursos" é acusada como ambígua,
  nomeando os **2** itens 8.1 do documento.
- **SC-464**: **Zero** achados no cenário A da auditoria e num conjunto de prova com ao menos **40**
  parágrafos legítimos, cobrindo cada linha da tabela de números legítimos dos *Edge Cases* — datas,
  números de lei, valores, horas, percentuais, ordinais, decimais com unidade, números de processo, CEP,
  telefone, ano, listas de um nível, invisível colado e zero à esquerda.
- **SC-465**: Corrigido o cenário B pelos achados — e só pelo que eles dizem —, a Revisão não exibe
  nenhum achado de numeração; publicado, o documento tem **100%** dos parágrafos numerados começando
  pelo número da própria seção, e o mesmo número de páginas da versão sem correção.
- **SC-466**: **Nenhum** documento publicado muda: os resumos criptográficos de todos os documentos
  gravados são iguais antes e depois da implantação, e os conteúdos congelados da auditoria (cenários
  A e B) produzem, com o código novo, os mesmos bytes de antes.
- **SC-467**: Em **nenhuma** superfície uma remissão é apresentada como conferida, verificada ou
  correta.
- **SC-468**: Para cada achado de numeração do cenário B, quem elabora localiza o parágrafo no campo
  da seção usando só o trecho da mensagem (busca de texto), sem ler a seção inteira — **5 de 5**
  achados.
- **SC-469**: O rascunho do cenário B sem correção tem a submissão **recusada**, e a recusa nomeia as
  **5** seções em conflito; um rascunho só com avisos desta feature tem a submissão aceita.
- **SC-470**: Uma Retificação sobre o cenário B corrigido que esvazia uma seção textual e desloca a
  numeração das seguintes é **publicada**, com os conflitos que ela cria exibidos como avisos antes
  da publicação.

### O que esta feature não cobre, deliberadamente

- **Numeração automática** dos parágrafos das seções textuais pelo sistema — a solução estrutural do
  ED-01, para evolução posterior.
- **Renumerar ou corrigir** texto, inclusive como sugestão aplicável com um clique.
- **Verificar se uma remissão é normativamente correta.** A feature só acusa o que a estrutura prova
  (ambiguidade, ausência) ou o que é suspeito; o conteúdo do item citado nunca é comparado com a
  intenção do texto.
- **Sequência interna** dos subitens (lacuna, repetição, ordem: 4.1, 4.3; 4.2 duas vezes) e título
  repetido com o mesmo número da seção.
- **Alíneas** ("alínea a do item 5.4" é conferida só pelo "item 5.4"), incisos, artigos e remissões
  sem a palavra "item" ("conforme o 4.2").
- **O conteúdo dos Anexos**, que são arquivos à parte.
- **Mudanças em recursos, no PDF e no catálogo de seções**, e os demais achados da auditoria.

---

## Decisões

Fechadas pelo responsável pelo produto em 08/10/2026, depois da primeira redação desta spec (7º a 9º
do cabeçalho). As alternativas descartadas ficam escritas, porque são a razão da escolha.

#### D-001 — O conflito comprovado de numeração é impeditivo no Edital

Impede a submissão e a publicação. **Por quê:** com a definição estreita de número de subitem e de
conflito (`FR-1199`, `FR-1200`), o defeito é certo no documento impresso, e o ato oficial não pode
sair com subitem fora da sua seção. **Descartadas:** o aviso, como o RC-21 — deixaria o defeito
chegar ao ato se a homologação não o tratasse —; e o impeditivo com dispensa justificada por quem
homologa — mecanismo novo, maior que esta feature. **Consequência aceita:** o número de subitem
legítimo numa forma não prevista (uma tabela de pontos colada como texto) obriga a reescrever o
trecho. Atende `FR-1210` e `FR-1212`.

#### D-002 — Na Retificação, todo achado desta feature é aviso

Inclusive o conflito comprovado e o que a própria Retificação introduz. **Por quê:** a Retificação de
um Edital publicado antes desta feature — uma prorrogação urgente, por exemplo — não pode ser travada
por numeração que já estava no ato. **Descartadas:** impeditivo só para o que a Retificação cria —
mais preciso, e mais complexo de explicar e de implementar —; e deixar a Retificação de fora, como o
RC-21 — sem aviso justamente para o deslocamento que só a Retificação produz. **Consequência aceita,
e explícita:** um conflito introduzido pela própria Retificação **também não é bloqueado**; o
consolidado sai com ele se ninguém o corrigir, e o aviso é a única proteção. Atende `FR-1213`.

#### D-003 — Remissões e suspeitas são avisos, e a remissão é procurada em todo texto livre impresso

**Por quê:** a remissão pode ser a outro ato, e o sistema não tem como distinguir sempre — o mesmo
fundamento da decisão do RC-21, de 28/09 —; e a remissão aparece também fora das seções textuais (a
alínea "e" dos documentos do 28/2026 remete ao item 5.14). **Limite mantido:** achar um destino único
não prova que a referência está correta, e nada no sistema diz que está (`FR-1209`). Atende
`FR-1204` e `FR-1211`.

#### D-017 — Intervalos de hora e de data, multiplicadores, e a remissão acima de quatro níveis

Fechada pelo responsável pelo produto em 09/10/2026, na revisão do PR. A revisão reproduziu cinco
começos de parágrafo legítimos lidos como subitem — "8.30 às 12.00 – …", "10.10 a 20.10 – …", "1.5
salário mínimo", "1.2 mil candidatos", "3.5 vezes o valor" —, e cada um, numa seção de outro número,
impedia a submissão com a orientação de "corrigir a numeração". **Decidido:** ampliar as unidades
(mil, milhão, milhões, vez, vezes, salário, salários), como *Assumptions* já previa; e reconhecer
os intervalos de hora e de data **pela expressão inteira**, explicitado em `FR-1199`. **Descartada:**
excluir qualquer número seguido de "a" ou "às" — tiraria do impeditivo o intervalo de subitens e
conflitos reais. **Erro aceito:** "10.10 a 10.12" é ambíguo (de 10/10 a 10/12, ou dos itens 10.10 a
10.12) e continua subitem; um dia.mês sozinho ("12.10 Feriado") também. **Na mesma revisão:** o
número de remissão acima de quatro níveis virava remissão ao seu prefixo ("item 10.1.1.1.1" → "item
10.1.1.1"); passa a ser ignorado inteiro, mantido o limite de quatro níveis. O conflito comprovado
continua impeditivo (`D-001`).

## Limitações remanescentes

- A feature prova **incoerência**, nunca **correção**: uma remissão a um item único pode estar
  errada, e nada a acusará (`FR-1209`).
- Remissão a outro ato sem designação explícita depois do número ("conforme o item 5.4", querendo
  dizer o de outro Edital) sai como **sem destino** ou, pior, casa com um item deste documento e não sai
  — o aviso não substitui a conferência de quem homologa.
- O reconhecimento é por forma: um número de subitem legítimo numa forma não prevista (uma tabela de
  pontuação colada como texto, "1.1 Doutorado — 10 pontos", numa seção que não é a 1) será acusado e,
  pela `D-001`, impedirá a submissão. A saída é reescrever o trecho (por exemplo, "Item 1.1 da Ficha —
  Doutorado") ou levar a tabela para um Anexo.
- Na Retificação nada desta feature impede (`D-002`): o conflito que a Retificação introduz pode
  chegar ao consolidado.
- O ordinal do parágrafo é o da composição do documento; um texto colado com quebras de linha no meio
  das frases tem mais "parágrafos" do que parece na tela.
- Editais já publicados com conflito continuam com ele até uma Retificação — e só se corrigem por ela,
  que os acusará como aviso.

## Assumptions

- O documento continua compondo cada quebra de linha como parágrafo; se isso mudar (o registro das
  quebras rígidas do texto colado, deixado fora da `064`), a contagem de parágrafos dos achados muda
  junto.
- A numeração calculada continua sendo a regra única de `FR-985` da `054`, e o catálogo de seções não
  muda nesta feature.
- Os nove Editais da amostra em `~/Downloads` representam as formas de numeração e de remissão do
  Cefor; a lista de números legítimos foi calibrada neles e pode crescer na implementação, sem mudar
  a regra.
- Os casos-limite desta spec são requisitos e entram na matriz de rastreabilidade com teste próprio,
  como os `FR-` e os `SC-`.
- Componentes afetados, complexidade e plano de validação estão em
  [insumos-para-o-plano.md](insumos-para-o-plano.md), que não é normativo.
