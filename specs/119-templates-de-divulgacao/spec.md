# Feature Specification: Templates de Divulgação por Família e Formato

**Feature Branch**: `claude/119-templates-de-divulgacao`, sobre a `main` em `fb0e1ddc`

**Created**: 2026-11-04

**Status**: Especificada e planejada em 04/11/2026; revista no mesmo dia — inventário de recusas,
ZIP com vários formatos, versão aprovada de cada template, exceção dos valores literais e provas da
impressão v1/v2. `/speckit-analyze` sem achado crítico. **Não implementada.** As decisões T-1 a T-9 do estudo foram aceitas pelo
usuário em 04/11/2026 e entram aqui como regra. O que depende da comunicação — licença e banco de
imagens, fonte substituta, tamanho do banner e aprovação de cada template — está nas pendências
(§Pendências de produto) e bloqueia a **liberação** de cada template, e não o início da
implementação.

**Input**: o pedido de 04/11/2026 de generalizar o kit de divulgação da `111` para os templates que a
comunicação forneceu — 21 arquivos, sete famílias visuais em três formatos —, e o
[estudo de adoção dos templates](../../doc/estudo-templates-de-divulgacao-2026-11-04.md), que os leu
slide a slide, cruzou cada elemento com o que o sistema sabe e propôs o plano.

> **Faixa de identificadores.** Esta spec abre em **FR-3801** e **SC-1131**. O teto medido em
> 04/11/2026 na `main`, nos PRs abertos e nas worktrees desta máquina é o requisito três mil
> setecentos e cinquenta e nove e o critério mil cento e vinte e sete, os dois da `118` (PR aberto).
> A folga é deliberada. **Nenhum `UX-` é aberto aqui.** As decisões técnicas reiniciam em `D-001` e
> moram no [research.md](research.md); as pendências de produto são `P-`; os casos-limite são `EC-`;
> as decisões do estudo são `T-1` a `T-9`.
>
> **Como esta spec cita outras.** Requisito de outra feature pelo identificador e pela feature ("a
> FR-3423 da `111`"). Decisão de outra feature pelo assunto e pela feature.

---

## Por que esta feature existe

**A `111` entregou um desenho só, e a comunicação tem vinte e um.** A peça da `111` é o feed
1080 × 1350 com a marca do Cefor, um desenho neutro feito pelo sistema. A comunicação trabalha com
identidades visuais por tipo de certame — FIC, Libras, Pós Lato Sensu, Aperfeiçoamento, TMD,
UAB/bolsista e Internos —, cada uma em post, story e banner do site. Hoje ela as preenche à mão,
lendo o PDF do Edital: o mesmo trabalho e o mesmo risco que a `111` existe para tirar.

**Os templates foram feitos para preenchimento à mão, e por isso afirmam o que o sistema não
comprova.** "Inscrições abertas", "Inscrições até 09/11" sem ano, "Gratuita e 100% a distância",
"vagas remanescentes". A `111` proíbe as duas primeiras (FR-3414 e FR-3415 da `111`), e as outras não
têm fonte publicada. A spec adota o desenho, e não as frases: a peça continua dizendo só o que a
ficha comprova (FR-3423 da `111`).

**O motor da `111` serve sem troca.** O estudo verificou que tudo o que os templates desenham —
formas livres, padrões, recorte de foto em círculo e losango, gradientes — o rasterizador já desenha,
e que as fontes, salvo a Helvetica Neue, são livres. O que muda é a forma do compositor: hoje um
tamanho, uma fonte e um desenho fixos no código; aqui, **formato × família**, como dados.

### O que é reaproveitado da `111`, sem mudança

| Peça | Nesta spec |
|---|---|
| A ficha, a impressão, a proveniência e a desatualização | Ganham dois campos (FR-3809, FR-3810) e uma versão de impressão (FR-3811) |
| O kit textual | Ganha a carga horária e o contato (FR-3813) |
| A medida e a quebra pela fonte, a recusa sem truncar, o teste geométrico | Valem por template (FR-3824) |
| A conferência peça ⊂ textos | Vale por template, estendida à carga horária e ao contato (FR-3813) |
| Os SVG de referência, a galeria e o pacote do incremento C (mergeado no #377) | A galeria passa a cobrir todo template e a mostrar a versão aprovável (FR-3831, FR-3834); o ZIP passa a levar vários formatos (FR-3829) |
| A exportação registrada na trilha, sem guarda de arquivo | Registra também família, formato, template e imagem (FR-3828) |
| Capacidade, papel, porta, CSP, host local, modo do material | Iguais |

### O que esta spec cobre, e o que fica fora

| Cobre | Fora |
|---|---|
| Três formatos: post 1080 × 1350, story 1080 × 1920, banner do site | Quadrado, carrossel, capa de vídeo, animação |
| Sete famílias da comunicação, mais a família da peça atual | Template por campus ou por unidade além das famílias declaradas; editor gráfico |
| Escolha de família, variante e imagem em lista fechada, por quem gera | Campo de categoria no Processo (T-2: só se a escolha manual errar) |
| Carga horária publicada do Perfil; contato da Unidade | Gratuidade, modalidade, "vagas remanescentes" enquanto não forem dado publicado (T-3) |
| Banco curto de imagens licenciadas por família, versionado | Envio de imagem pela tela (T-4) |
| Fontes livres, com substituta da Helvetica Neue | Fonte proprietária |
| Liberação por template no ambiente | Publicação em rede social, agendamento, geração automática |
| — | Faixa "Informação complementar" para Retificação que não muda o material (P-6) |

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Gerar o post, o story e o banner na identidade da família (Priority: P1) 🎯 MVP

Alguém da comunicação abre o kit de um Edital de pós-graduação lato sensu publicado. Escolhe a
família "Pós Lato Sensu" e uma das fotos do banco dela. A tela mostra a prévia dos três formatos
lado a lado, cada um com o texto alternativo, e a pessoa baixa os três PNG. Nenhum texto foi
digitado: título, número, período com ano, ofertas e chamada vêm da ficha e das frases aprovadas da
família.

**Why this priority**: é o pedido. Sem família e formato não há adoção dos templates.

**Independent Test**: com um Edital de cenário de referência publicado, escolher a família Pós Lato
Sensu e gerar os três formatos. Conferir, em cada um:

- todo texto é valor da ficha, frase fixa aprovada da família ou manchete da lista fechada;
- toda data tem ano e toda data e quantidade está nos textos;
- nenhum texto sai da área útil, invade a zona reservada do story, se sobrepõe a outro texto ou à
  imagem;
- duas gerações dão os mesmos bytes.

**Acceptance Scenarios**:

1. **Given** um Edital publicado com inscrições futuras, **When** a pessoa gera o post da família
   Pós Lato Sensu, **Then** a peça diz "Inscrições até DD/MM/AAAA", com a hora e o início no mesmo
   bloco, e nenhuma frase diz que as inscrições estão abertas.
2. **Given** a mesma família, **When** a pessoa gera o story, **Then** nenhum texto cai nas faixas de
   cima e de baixo que o aplicativo cobre com a sua interface.
3. **Given** a mesma família, **When** a pessoa gera o banner, **Then** a chamada à ação é "Acesse o
   edital", e a busca pelo número com a sigla aparece em todos os três formatos.
4. **Given** um título que cabe no post e não no banner, **When** a pessoa gera os três, **Then** o
   banner segue a ordem de título da `111` (FR-3426 da `111`) sozinho, e a tela diz em qual formato o
   título oficial não coube.

---

### User Story 2 — Ver na peça a carga horária e o contato que o Edital e a unidade declaram (Priority: P1)

A pessoa gera o post da família FIC de um Edital com três cursos. Cada curso aparece com a carga
horária publicada no Perfil ("Assistente Administrativo — 180h"), e embaixo o contato "Dúvidas?"
traz o canal de atendimento declarado pela unidade. A legenda diz o mesmo.

**Why this priority**: a carga horária e o contato estão em quase todos os templates; sem eles, a
comunicação volta a completar a peça à mão.

**Independent Test**: publicar um Edital com Perfis de carga horária declarada, vazia e longa, numa
unidade com e sem atendimento. Conferir que a peça e a legenda trazem exatamente o que está
publicado e registrado, que nada é inferido, e que a mudança do atendimento depois de uma exportação
acende a faixa de desatualização.

**Acceptance Scenarios**:

1. **Given** um Perfil sem carga horária, **When** a peça é gerada, **Then** a linha dele sai só com
   o nome, e nenhuma carga é inferida.
2. **Given** uma unidade sem atendimento declarado, **When** a peça é gerada, **Then** a linha de
   contato não sai, e nenhum outro canal a substitui.
3. **Given** uma exportação registrada e o atendimento da unidade alterado depois, **When** a pessoa
   reabre o kit, **Then** a faixa de desatualização diz "contato: antes → agora".

---

### User Story 3 — Escolher só o que a comunicação aprovou (Priority: P1)

A pessoa vê, numa lista, as famílias da unidade do Edital que têm template liberado no ambiente, e
para a família escolhida, as variantes e as imagens do banco dela. Não há campo de texto, nem envio
de imagem. Quando reabre o kit do mesmo Edital, a tela já traz a família, a variante e a imagem da
última exportação.

**Why this priority**: negar por padrão e afirmar só o comprovado. A escolha manual da família
substitui um dado que o sistema não tem (T-2), e por isso precisa ser fechada e registrada.

**Independent Test**: num Edital do Cefor, a lista traz as famílias liberadas; num Edital de outra
unidade, só a família da peça atual. Um envio com família, variante, formato ou imagem fora da lista
é recusado sem gerar nada.

**Acceptance Scenarios**:

1. **Given** um Edital de unidade sem família declarada, **When** a pessoa abre o kit, **Then** só a
   família da peça atual é oferecida.
2. **Given** um template não liberado no ambiente, **When** a pessoa abre o kit, **Then** o formato
   aparece indisponível, com o motivo "em aprovação pela comunicação", e os demais continuam.
3. **Given** uma exportação anterior com família e imagem, **When** a pessoa reabre o kit, **Then** a
   tela as traz escolhidas; se a imagem saiu do banco, a tela traz a primeira da lista e diz por quê.

---

### User Story 4 — Generalizar o motor sem mudar a peça de hoje (Priority: P1)

Antes de qualquer família nova, o compositor passa a ler formato e família como dados. A peça da
`111` vira a primeira família, e os SVG de referência dela saem idênticos byte a byte.

**Why this priority**: é a prova de que a generalização não quebrou o que está implementado e em
aprovação.

**Independent Test**: gerar os SVG de referência dos cenários da `111` antes e depois da mudança e
compará-los byte a byte.

**Acceptance Scenarios**:

1. **Given** os cenários de referência da `111`, **When** a peça é gerada pelo motor generalizado,
   **Then** cada SVG é idêntico ao de referência e o identificador do template não muda.

---

### User Story 5 — Aprovar cada template na galeria antes de liberá-lo (Priority: P2)

A comunicação abre a galeria do kit e vê cada template — família × formato — aplicado a todos os
cenários de referência e aos casos no limite. Aprova ou pede ajuste; só o aprovado é liberado no
ambiente.

**Why this priority**: são 21 templates com aprovação humana (SC-1135). A galeria da `111` reduz o
custo, mas precisa alcançar todos.

**Independent Test**: gerar a galeria e conferir que cada template liberável aparece em todo cenário
de referência, com a recusa e o motivo onde não couber.

---

### Edge Cases

Cada caso aqui é requisito, e tem tarefa própria em [tasks.md](tasks.md).

- **EC-1 — Edital de unidade sem família.** Só a família da peça atual é oferecida (FR-3805).
- **EC-2 — Carga horária vazia em parte das ofertas.** Sai só nas que a declaram; nada é inferido nem
  completado (FR-3809).
- **EC-3 — Carga horária longa** ("360 horas, das quais 60 presenciais"). É medida como o nome. Se a
  linha não couber no mínimo, o formato é recusado com o motivo nomeando a carga horária; nunca
  truncada (FR-3824).
- **EC-4 — Atendimento longo.** Se a linha de contato não couber no mínimo, ela sai da peça e a tela
  diz em qual formato saiu; os textos a mantêm (FR-3820).
- **EC-5 — Mais de quatro ofertas, em qualquer formato.** O teto da FR-3425 da `111` vale: contagem
  e convite à página.
- **EC-6 — Template sem bloco de ofertas** (o banner, quando declarado assim). Nenhuma quantidade nem
  carga horária aparece nele (FR-3817).
- **EC-7 — Template desligado depois de aberta a tela.** A exportação é recusada com o motivo, e a
  tela reaberta não o oferece (FR-3808).
- **EC-8 — Imagem retirada do banco numa versão nova da família.** A escolha da exportação anterior
  não é mais oferecida; a tela traz a primeira da lista e diz por quê (FR-3806).
- **EC-9 — Envio forjado** com família de outra unidade, variante, formato ou imagem fora da lista.
  Recusa sem gerar nada e sem registrar exportação (FR-3805).
- **EC-10 — Modo neutro** (sem período designado). A chamada fixa da família continua, se não falar
  de inscrição; o destaque é "Edital publicado" (FR-3416 da `111`, FR-3815).
- **EC-11 — Modo sem material.** Nenhum formato de família nenhuma é gerado (FR-3410 da `111`).
- **EC-12 — Host local.** Nenhuma peça em formato nenhum (FR-3447 da `111`).
- **EC-13 — Caractere sem grafia numa das fontes da família.** O template é recusado nomeando o
  caractere e a fonte; os outros formatos que não usam aquela fonte para aquele texto continuam
  (FR-3823).
- **EC-14 — Exportações anteriores à versão nova da impressão.** Nenhuma faixa falsa: a comparação
  recalcula a impressão antiga a partir da ficha atual (FR-3811).
- **EC-15 — Atendimento alterado depois de uma exportação.** Faixa com o contato anterior e o atual
  (FR-3811).
- **EC-16 — Prorrogação comprovada.** O selo "Prazo prorrogado" aparece em todo formato da família,
  no lugar que o template declara (FR-3815).
- **EC-17 — Período que atravessa o ano, ou sem término.** As formas da `111` valem em todo formato:
  ano nas duas pontas; "Inscrições a partir de DD/MM/AAAA" sem término (FR-3815).
- **EC-18 — Título que cabe num formato e não em outro.** Cada formato resolve o título sozinho, pela
  ordem da FR-3426 da `111`; a manchete escolhida vale só onde nenhum oficial cabe (FR-3818).
- **EC-19 — Família com variantes** (Internos: servidores, estudantes). A variante é escolhida na
  lista, e a chamada fixa dela é a única diferença de texto (FR-3806).
- **EC-20 — Família sem banco de imagens.** Nenhuma imagem é pedida, e a peça sai com os ativos fixos
  da família (FR-3807).
- **EC-21 — Valor oficial com termo vedado às frases fixas.** Um título "Especialização a distância
  em …" ou um Perfil "Curso gratuito de …" entram literais na peça e nos textos; a conferência os
  aponta. A vedação da FR-3814 é das frases fixas e da composição, e não do que o Edital publicou
  (FR-3414 da `111`, SC-1131).
- **EC-22 — Ativo, fonte, frase, caixa ou motor alterados sem subir a versão do template.** Se o
  resumo fixado não for atualizado, a suíte reprova; se for regravado na mesma versão, o resumo deixa
  de coincidir com o da configuração e com o do registro de aprovação, e o template fica indisponível
  e a suíte reprova (FR-3833, FR-3834).
- **EC-23 — Versão ou resumo do template no código diferentes dos liberados no ambiente.** O template
  fica indisponível com o motivo "versão nova em aprovação", e o ZIP o lista como não incluído
  (FR-3808, FR-3835).
- **EC-24 — Tela aberta antes da implantação da impressão versão 2.** A exportação enviada com a
  impressão antiga é recusada como "o Edital mudou desde que você abriu o kit" (FR-3446 da `111`); a
  tela reaberta mostra o novo.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Formato, família e template

- **FR-3801**: O kit MUST conhecer três formatos, cada um com tamanho, margem de segurança, zonas
  reservadas e corpo mínimo próprios:
  - **post**: 1080 × 1350; margem de 80 px; corpo mínimo de 24 px;
  - **story**: 1080 × 1920; margem lateral de 80 px; as faixas de 250 px no alto e embaixo, que o
    aplicativo cobre com a sua interface, MUST NOT receber texto; corpo mínimo de 24 px;
  - **banner do site**: proporção do arquivo da comunicação (750 × 425, ≈1,76:1), desenhado ao dobro
    — 1500 × 850 — até a resposta da P-3; margem de 60 px; corpo mínimo de 28 px.
- **FR-3802**: Uma **família** MUST declarar, versionados no código:
  - identificador, nome e versão;
  - a unidade ou as unidades a que pertence;
  - paleta, fontes e ativos fixos (marca, padrões, ilustrações, rodapé de perfis de rede);
  - o banco de imagens, quando houver (FR-3807);
  - as variantes, quando houver, cada uma com a sua chamada fixa (EC-19);
  - as frases fixas aprovadas (FR-3814).
- **FR-3803**: Um **template** MUST ser família × formato: a declaração das caixas — chamada, título,
  ofertas, período, número, chamada à ação, busca, contato, imagem, rodapé e selo da versão —, cada
  uma com posição, corpo máximo e mínimo e a ordem de recaída, e uma versão própria. O compositor
  mede, quebra e recusa como na `111`; nenhuma regra de composição é escrita por template fora
  dessa declaração.
- **FR-3804**: A peça da `111` MUST tornar-se a família "Institucional" (nome provisório), só no
  formato post, com o mesmo identificador de template. Os SVG de referência dela MUST sair idênticos
  byte a byte depois da generalização.
- **FR-3805**: A lista de famílias oferecida MUST ser: as famílias da unidade do ato da versão
  vigente que tenham ao menos um template liberado no ambiente, mais a Institucional. Família de
  outra unidade MUST NOT ser oferecida. Envio com família, variante, formato ou imagem fora da lista
  MUST ser recusado sem gerar e sem registrar (EC-9).
- **FR-3806**: Quem gera MUST escolher a família, a variante quando houver e a imagem quando houver,
  cada uma numa lista fechada. A tela MUST trazer pré-escolhidas as da exportação de peça mais
  recente daquele Edital, lidas da trilha; sem exportação, a Institucional. Escolha anterior que deixou de
  estar na lista MUST ser trocada pela primeira da lista, com o motivo dito (EC-8). Nenhuma escolha
  MUST ser guardada no Edital.
- **FR-3807**: O banco de imagens de uma família MUST ser uma lista curta (três a seis) de imagens
  licenciadas e escolhidas pela comunicação, cada uma com uma descrição aprovada para o texto
  alternativo. MUST NOT haver envio de imagem pela tela. Família sem banco não pede imagem (EC-20).
- **FR-3808**: A liberação MUST ser por template, **por versão e por resumo**, no ambiente: uma
  configuração nomeia cada template liberado como `familia/formato@versao#<resumo curto>` (FR-3833),
  e em produção nenhum vem liberado. Template não liberado, ou cuja versão ou resumo no código
  diferem dos liberados, aparece indisponível, com o motivo, e não é gerado nem exportado (EC-7,
  EC-23); o kit textual e os outros templates continuam. A chave da peça da `111` continua valendo,
  sem mudança, só para a Institucional na versão 1 (FR-3835).

#### Ficha

- **FR-3809**: A ficha MUST trazer a carga horária de cada oferta, literal do campo publicado do
  Perfil, sem espaços nas pontas. Vazia é "não declarada". MUST NOT ser inferida, convertida nem
  completada (EC-2).
- **FR-3810**: A ficha MUST trazer o contato: o canal de atendimento da unidade do ato da versão
  vigente, como registrado no instante da leitura. Não declarado, a ficha não tem contato, e o canal
  da instituição MUST NOT substituí-lo. É a exceção declarada à FR-3404 da `111`: o kit passa a ler
  esse campo do registro da unidade, e nada mais fora do publicado.
- **FR-3811**: A impressão MUST passar à versão 2, que acrescenta a carga horária de cada oferta e o
  contato. Para exportação registrada na versão 1, a comparação MUST recalcular a impressão versão 1
  a partir da ficha atual, e a **diferença** que a faixa mostra MUST ser calculada entre os `campos`
  gravados e os campos versão 1 da ficha atual — nunca com os campos versão 2, para que a faixa não
  liste carga horária nem contato que aquele material não afirmou. Daí:
  - a mudança de versão, sozinha, MUST NOT acender faixa (EC-14);
  - a mudança de um campo da versão 1 (título, unidade, período, ofertas, caminho) depois de uma
    exportação versão 1 MUST continuar acendendo, com o valor anterior lido dos `campos` gravados;
  - a mudança só da carga horária ou do contato depois de uma exportação versão 1 MUST NOT acender,
    porque aquele material não os afirmava;
  - a mudança do contato ou da carga horária depois de uma exportação versão 2 MUST acender, com o
    valor anterior e o atual (EC-15);
  - a faixa MUST listar só as mudanças efetivas: num caso misto (título e contato alterados depois de
    uma exportação versão 1), ela traz o título e não traz o contato.
- **FR-3812**: A conferência MUST mostrar a carga horária de cada oferta com o ato que a deu, pela
  regra da proveniência da `111` (FR-3408 da `111`), e o contato com a origem "cadastro da unidade",
  que não é ato.

#### Textos

- **FR-3813**: A legenda e o texto para mensagens MUST trazer a carga horária de cada oferta listada,
  quando declarada, e o contato, quando declarado. Toda carga horária e todo contato que a peça
  mostra MUST estar também nos textos, e a conferência automática da FR-3423 da `111` MUST cobri-los.

#### Composição

As FR-3815 a FR-3821 valem para os templates das famílias da comunicação. A Institucional mantém o
desenho e as regras de composição da `111` — o período na forma completa, o rodapé com o caminho
curto e a busca, as linhas de oferta sem carga horária —, e por isso as suas referências não mudam
(FR-3804). As FR-3814 e FR-3822 a FR-3827 valem para todas.

- **FR-3814**: As frases fixas de uma família — chamada do alto, rótulos, chamada à ação — MUST ser
  aprovadas pela comunicação, verdadeiras para todo Edital da família e da variante, e passar a lista
  da FR-3414 da `111`. Enquanto não houver dado publicado que os comprove (T-3), MUST NOT conter:
  "inscrições abertas", "gratuito", "gratuita", "a distância", "presencial", "remanescentes". A
  varredura de vocabulário MUST ler as frases de todas as famílias.
- **FR-3815**: O período MUST ocupar o destaque do template, numa das formas fechadas:
  - "Inscrições até DD/MM/AAAA" (T-1), com a hora e "(horário de Brasília)" e com o início, também
    com ano, no mesmo bloco;
  - ou a forma completa da `111`, "Inscrições de DD/MM/AAAA a DD/MM/AAAA".

  Toda data MUST ter ano. As formas da `111` para período sem término, período que atravessa o ano e
  modo neutro valem (EC-10, EC-17). O selo "Prazo prorrogado" MUST aparecer em todo formato quando a
  prorrogação é comprovada (EC-16).
- **FR-3816**: O número do Edital, "Edital nº N/AAAA", MUST aparecer em todo formato.
- **FR-3817**: As ofertas MUST seguir o teto e a regra do total da FR-3425 da `111`, e cada linha
  listada traz a carga horária declarada depois do nome ("Nome — carga horária"). Um template pode
  declarar que não tem bloco de ofertas; então nenhuma quantidade nem carga horária aparece nele
  (EC-6).
- **FR-3818**: O título MUST ser resolvido por formato, pela ordem da FR-3426 da `111`. A manchete da
  FR-3427 da `111` é oferecida quando nenhum título oficial cabe em algum formato liberado da família,
  e é usada só nos formatos em que nenhum oficial cabe (EC-18). A tela MUST dizer em quais formatos o
  título oficial não coube. É a extensão declarada da FR-3427 da `111`, escrita para uma peça só: a
  regra "oferecida só quando nenhum título oficial cabe" passa a ser lida por formato.
- **FR-3819**: A chamada à ação MUST ser fixa por formato (T-6): "Acesse o link na bio" no post e no
  story; "Acesse o edital" no banner. A busca pelo número com a sigla da unidade ("busque por N/AAAA
  – SIGLA", FR-3418 da `111`) MUST aparecer em todo formato, medida, no mínimo legível.
- **FR-3820**: O contato MUST sair como "Dúvidas? <canal>" quando a ficha o tem e o template tem a
  caixa. Se não couber no mínimo, a linha sai da peça e a tela diz em qual formato (EC-4); nunca é
  truncada nem trocada por outro canal.
- **FR-3821**: O rodapé fixo da família (perfis de rede, marca) MUST ser ativo aprovado com o
  template, sem dado variável. O selo da versão (FR-3431 da `111`) MUST aparecer em todo formato.
- **FR-3822**: Nenhum texto MUST se sobrepor à imagem nem a padrão decorativo. O contraste AA MUST
  ser medido contra a cor lisa da caixa que contém o texto. O teste geométrico MUST verificar a não
  sobreposição com a área da imagem.
- **FR-3823**: As fontes MUST ser livres, em subconjunto versionado com a origem, a licença e o
  resumo conferido por teste. A Helvetica Neue dos templates MUST ser substituída pela fonte livre
  aprovada (T-5, P-2). Caractere sem grafia numa fonte usada MUST recusar o template, nomeando o
  caractere e a fonte (EC-13).
- **FR-3824**: As regras de legibilidade e de recusa da `111` (FR-3428, FR-3429 e FR-3434 da `111`)
  MUST valer por template, com o mínimo, a margem e as zonas reservadas do formato. A recusa é por
  template: um formato que não cabe é recusado com o motivo, e os outros continuam (EC-3).
- **FR-3825**: Cada formato MUST ter o seu texto alternativo, em frases, na ordem em que a peça mostra,
  com a descrição aprovada da imagem quando houver (FR-3433 da `111`).
- **FR-3826**: Todo ativo de família — imagem, ilustração, padrão, marca, fonte — MUST constar do
  arquivo de origem da família, com fonte ou autor, licença, quem aprovou, a data e o resumo. Um teste
  MUST conferir o resumo de cada ativo e que nenhum ativo usado fique fora do arquivo. Imagens MUST
  ser reduzidas ao tamanho de uso, com no máximo 400 kB cada.
- **FR-3827**: A mesma ficha, com o mesmo template na mesma versão, a mesma variante, a mesma imagem e
  a mesma manchete, MUST produzir a mesma peça byte a byte, em qualquer instante (FR-3438 da `111`).

#### Exportação, tela e galeria

- **FR-3828**: Cada exportação MUST registrar na trilha, além do que a FR-3436 da `111` pede: a
  família e a sua versão, a variante, e a imagem com o resumo. Para PNG e SVG, também o formato, o
  template, a sua versão e o resumo do template (FR-3833). Para o ZIP, uma entrada **por formato**
  da família — incluído ou não —, com o template, a versão, o resumo, o nome e o resumo de cada
  arquivo incluído, ou o motivo de não estar (FR-3829). A desatualização continua decidida só pela
  impressão: trocar de família ou de imagem MUST NOT acender faixa.
- **FR-3829**: O pacote ZIP do incremento C da `111` (mergeado no #377) MUST, para uma família da
  comunicação, levar a peça de cada formato liberado, em PNG, SVG e texto alternativo, com nomes que
  levam o formato (`peca-<formato>.png`, `peca-<formato>.svg`, `peca-<formato>-alternativo.txt`). O
  manifesto MUST trazer a família com a versão, a variante, a imagem com o resumo, e uma entrada por
  formato da família com: o formato; o template, a versão e o resumo; se foi incluído; os arquivos com
  o resumo de cada um; e, quando não incluído, o motivo — não liberado, versão divergente, recusa da
  composição com o motivo dela, ou falta do rasterizador. As fontes e os ativos listados são os dos
  templates incluídos, com o resumo. Formato com SVG e sem PNG (falta o rasterizador) é incluído, com
  o motivo `sem_rasterizador`. Os campos singulares da `111` — `peca` no manifesto, `template`,
  `manchete` e `sem_peca` no evento — vêm nulos no ZIP de família, e quem lê usa a lista por formato.
  A ordem dos arquivos no ZIP é fixa: os textos, depois post, story e banner, cada um em PNG, SVG e
  alternativo, depois a ficha e o manifesto (FR-3438 da `111`). Para a Institucional, o ZIP MUST
  manter os nomes de arquivo, a estrutura do manifesto e a peça (SVG e PNG) da `111`; a ficha e a
  impressão nele passam a ser as da versão 2.
- **FR-3830**: A tela do kit MUST:
  - oferecer a escolha de família, variante e imagem num formulário que funciona sem script;
  - mostrar a prévia de cada formato liberado, com o texto alternativo e, se recusado, o motivo;
  - oferecer a exportação PNG e SVG por formato;
  - seguir a FR-3444 da `111` (CSP, AA, teclado, 375 px).
- **FR-3831**: A galeria de revisão MUST cobrir todo template liberável aplicado a todos os cenários
  de referência (§Cenários de referência) e aos casos sintéticos no limite, com a recusa e o motivo
  onde não couber.
- **FR-3832**: Nada desta spec MUST alterar o fluxo de publicação ou de Retificação, criar tabela ou
  guardar arquivo gerado (FR-3405 e FR-3441 da `111`).

#### Versão aprovada de cada template

- **FR-3833**: Cada template MUST ter um **resumo**: o SHA-256 da sua declaração canônica (caixas,
  frases, paleta, recortes), dos resumos de todo ativo, imagem do banco e fonte que ele usa, e do
  resumo das suas peças de referência (os SVG dos cenários de referência daquele template). O módulo
  da família MUST fixar, para cada versão, o resumo das referências e o resumo do template, e um
  teste MUST recalcular os dois. Assim, mudar fonte, imagem, ativo, frase, caixa **ou o motor** —
  que muda as referências — muda o resumo do template; quem o regravar na mesma versão muda o resumo
  que a configuração nomeia, e o template deixa de estar liberado (EC-22). A aprovação de um
  conteúdo não se estende a outro.
- **FR-3834**: A galeria MUST mostrar, em cada peça, o identificador do template, a versão e o resumo
  curto (doze caracteres). A aprovação da comunicação (SC-1135) MUST ser registrada no arquivo de
  verificação da spec com esses três dados, quem aprovou e a data, e a liberação no ambiente MUST
  nomear exatamente a versão e o resumo registrados (FR-3808). Um teste MUST conferir que cada
  `RESUMOS` de versão aprovada coincide com o registrado no arquivo de verificação. A liberação é
  procedimento de implantação documentado, sem tabela nem fluxo novo.
- **FR-3835**: Uma versão nova, ou um resumo novo, de template MUST nascer não liberado: a
  configuração que nomeia a versão e o resumo anteriores não o alcança, e o template fica
  indisponível no ambiente até nova aprovação e nova liberação (EC-23). Vale também para a
  Institucional: a versão 1 dela fica congelada por teste (o resumo fixado não muda), e qualquer
  versão nova dela só é liberada pela configuração nova, como as demais; a chave da `111` não a
  alcança.

### Key Entities

- **Formato**: tamanho, margem, zonas reservadas e corpo mínimo. Código.
- **Família**: identidade visual de um tipo de certame — paleta, fontes, ativos, banco de imagens,
  variantes, frases fixas, unidades. Código e ativos versionados.
- **Template**: família × formato, a declaração das caixas, com versão e resumo (FR-3833). É o que se
  libera e o que se aprova, sempre numa versão.
- **Escolha**: família, variante, imagem e manchete de uma exportação. Não é guardada; vai na trilha.
- **Ficha** (da `111`): ganha carga horária por oferta e contato, e a impressão versão 2.

---

## Cenários de referência

Os 16 da `111`, mais estes, todos em todo template liberável:

17. Pós lato sensu de uma oferta, título de 120 caracteres;
18. FIC com três Perfis de carga horária declarada;
19. FIC com carga horária vazia num Perfil e longa noutro;
20. unidade com atendimento declarado;
21. unidade sem atendimento;
22. atendimento de 255 caracteres;
23. Internos, nas duas variantes;
24. Edital de unidade sem família;
25. caractere sem grafia só na fonte de título da família.

---

## Pendências de produto

Nenhuma bloqueia o **início** da implementação. Cada uma bloqueia a **liberação** dos templates que
dela dependem.

| # | Pergunta | Comportamento enquanto não respondida |
|---|---|---|
| **P-1** | Quais imagens entram no banco de cada família, e com que licença? (T-4) | Família sem banco aprovado sai sem imagem, só com ativos fixos de licença conhecida; os templates que pedem foto não são liberados |
| **P-2** | Qual fonte livre substitui a Helvetica Neue? (T-5) | Libras, TMD e Internos não são liberados |
| **P-3** | Qual é o tamanho exato do banner no site do Cefor? (T-8) | 1500 × 850, a proporção do arquivo; nenhum banner é liberado antes da resposta |
| **P-4** | Quem aprova cada template, em nome da comunicação? | A comunicação, sobre a galeria; o registro é o da FR-3834 (identificador, versão, resumo, data), e a liberação da versão aprovada é da operação, pela configuração do ambiente |
| **P-5** | Alguma família ganha uma frase fixa genérica sobre gratuidade ou modalidade, verdadeira para todo Edital dela? (T-3) | Nenhuma; a FR-3814 a proíbe até a comunicação a aprovar e a spec ser emendada |
| **P-6** | A faixa "Informação complementar" dos templates FIC, para Edital retificado sem mudança no material, entra? | Não entra: obrigaria toda Retificação a desatualizar o material, contra a regra da `111` de que Retificação que não muda o material não acende faixa |
| **P-7** | Os perfis de rede do rodapé (@ifescefor, Ifes Cefor) continuam iguais em todas as famílias? | Iguais, como nos arquivos; o rodapé é ativo fixo da família |

### Respostas do responsável pelo produto (04/11/2026)

| # | Resposta | Como a implementação a lê |
|---|---|---|
| **P-1** | "Não se preocupe com licença. Adote o mais próximo do template possível." | O banco de cada família são as imagens dos próprios arquivos da comunicação, reduzidas uma vez; o `ORIGEM.md` da família registra a origem e a licença como "não verificada, adotada pelo responsável pelo produto". Na Pós Lato Sensu, a imagem é o fundo inteiro do slide, com a foto, o padrão e o rodapé |
| **P-2** | "Não sei. Escolha a mais próxima possível; se puder, use a mesma fonte." | A Helvetica Neue não é livre e não se embute. Para Libras, TMD e Internos, a substituta é escolhida na família, a mais próxima entre as livres, e registrada no `ORIGEM.md` das fontes |
| **P-3** | "Adote o tamanho padrão de banner na web" (com um exemplo de 1500 × 850) | O banner continua em 1500 × 850, e deixa de esperar resposta |
| **P-4** | "Apenas adote o template." | A adoção do responsável pelo produto é o registro de aprovação da FR-3834, em [verificacao.md](verificacao.md), com o identificador, a versão e o resumo de cada template; a galeria continua como prova visual, e a liberação em produção continua da operação, pela configuração |

Duas dessas leituras afrouxam o texto da spec, e ficam ditas aqui: a licença da FR-3826 passa a
admitir "não verificada" por decisão registrada, e a aprovação da SC-1135 passa a admitir a adoção
sem a galeria.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1131**: Em 100% dos cenários de referência × templates liberáveis, a peça só contém valores da
  ficha, frases fixas aprovadas da família e manchete da lista; toda data tem ano; nenhuma frase fixa
  nem composição contém termo da FR-3414 da `111` ou da FR-3814. Valores literais da ficha (título,
  nome do Perfil, localidade, carga horária) que contêm um desses termos entram como estão, e a
  conferência os aponta, como na `111` (EC-21). Verificação automática.
- **SC-1132**: Em 100% dos cenários de referência e dos casos no limite × templates liberáveis, nenhum
  texto sai da área útil, invade zona reservada, se sobrepõe a outro texto ou à imagem, fica abaixo do
  mínimo ou parte palavra; o que não cabe é recusado com o motivo.
- **SC-1133**: Os SVG de referência da família Institucional saem idênticos byte a byte antes e
  depois da generalização do motor.
- **SC-1134**: Para a mesma ficha e a mesma escolha, cada template produz a mesma peça em qualquer
  instante; o PNG, no ambiente de implantação.
- **SC-1135**: A comunicação aprova cada template sobre a galeria antes da liberação dele. Validação
  humana.
- **SC-1136**: Uma pessoa da comunicação obtém post, story e banner de uma família para um Edital real
  publicado em menos de três minutos, sem abrir o PDF e sem digitar texto. Validação humana.
- **SC-1137**: No ambiente de implantação, a tela com as prévias dos três formatos responde em menos
  de 2 segundos, e o ZIP com os três formatos em menos de 3 segundos, num lote de 20 gerações.
- **SC-1138**: 100% dos ativos de família usados têm origem, licença e resumo conferidos; nenhuma
  imagem passa de 400 kB.
- **SC-1139**: Depois da mudança para a impressão versão 2, nenhuma exportação versão 1 cujo material
  não mudou acende faixa de desatualização, e 100% das mudanças em campos da versão 1 posteriores a
  uma exportação versão 1 continuam acendendo, com o valor anterior e o atual. Verificação
  automática, com os casos da FR-3811.
- **SC-1140**: 100% dos templates registrados têm o resumo da versão conferido pela suíte e, quando
  aprovados, igual ao do registro de aprovação; nenhum template cuja versão ou resumo no código
  diferem dos liberados é gerado no ambiente.

---

## Assumptions

- As sete famílias são do Cefor: pertencem à unidade Cefor, e as outras unidades ficam com a
  Institucional até terem família própria declarada.
- A escolha manual da família é suficiente (T-2). Se ela errar na prática, um campo de categoria no
  Processo é spec própria.
- Libras é família própria, embora seja FIC de Libras; o estudo sugere entregá-la junto da FIC.
- As medidas do story (faixas de 250 px) seguem a área que o aplicativo cobre hoje; mudança dele é
  ajuste de formato, não de família.
- O volume continua de dezenas de exportações por Edital; três formatos por geração cabem no tempo
  síncrono (a `111` mediu ~45 ms por peça).
- Nenhum dado pessoal entra: as imagens são de banco licenciado, e a pessoa fotografada não é
  candidata.
