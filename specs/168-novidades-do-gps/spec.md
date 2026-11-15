# Feature Specification: Novidades do GPS

**Feature Branch**: `claude/gps-novidades-feature-16ea57`, sobre a `main` em `cf6327c8`

**Created**: 2026-11-14

**Status**: Draft. Especificada a pedido do usuário em 14/11/2026, a partir de uma proposta de
produto que ele trouxe ("Novidades do GPS"). As decisões abaixo são as que esta spec toma para
chegar ao MVP; as que são de governança estão em *Perguntas ao usuário*, e nenhuma delas bloqueia a
primeira entrega.

**Input**: a proposta do usuário, de 14/11/2026: uma área "Novidades do GPS" inspirada nas notas de
versão dos produtos SaaS, com linha do tempo, linguagem de quem opera, descoberta discreta e um
resumo "desde sua última visita"; as notas mantidas em arquivo versionado, alimentadas pelos PRs, sem
consulta ao GitHub durante a navegação, com revisão humana antes de publicar.

> **Faixa de identificadores.** Esta spec abre em **FR-7401**, **SC-2501** e **UX-801**. O teto
> medido em 14/11/2026, na `main` e nas branches remotas abertas (`166`, `167`), era o requisito sete
> mil duzentos e cinquenta e seis, o critério dois mil trezentos e noventa e oito e o requisito de
> experiência setecentos e setenta e quatro. As pastas `166` e `167` estão em PRs abertos. O
> intervalo até a abertura fica livre para specs paralelas. As decisões começam em `D-001`.
>
> **A revisão editorial de 14/11 abre em FR-7601, SC-2511 e UX-821.** A `169`, especificada e
> mergeada depois da `168`, tomou a faixa FR-7400 a 7435 e UX-800 a 803, que se sobrepõe à desta spec
> (FR-7401 a 7427, UX-801 a 806): os mesmos identificadores estão definidos em duas specs. Qual delas
> renumera é decisão do usuário (P-5); os requisitos novos desta revisão foram para uma faixa livre,
> acima do teto medido em 14/11 na `main` e nas branches abertas (FR-7537, SC-2506, UX-814).

---

## Por que esta feature existe

O ritmo de entrega passou a capacidade de absorção da equipe. Entre 14/10 e 14/11/2026 entraram na
`main` cerca de **150 PRs de produto**, 35 deles num único dia (12/11). Cada um é descrito com
cuidado em três lugares, e nenhum deles é para quem opera:

- a **spec**, para quem desenvolve;
- a **Visão do Sistema** (`docs/visao-sistema/index.html`), servida dentro da gestão desde a `105`
  como "Documentação do Sistema": o retrato do sistema inteiro, com uma seção por capacidade, mas sem
  dizer o que mudou nem quando;
- o **`CHANGELOG-AAAA-MM.md`** da Visão do Sistema, que registra as revisões *da documentação*, para
  quem a mantém.

Quem integra uma comissão e volta ao GPS na segunda-feira não tem onde ler, em poucos minutos, "o que
mudou desde sexta, para que serve e por onde começo". Hoje isso depende de alguém apresentar cada
melhoria pessoalmente.

### O que o diagnóstico encontrou (14/11/2026)

- **Não há versão nem release.** O repositório tem uma tag só, de preservação
  (`155-destinacao-completa`), e nenhuma release no GitHub. O guia de implantação implanta **pelo SHA
  completo** de um commit da `main`, numa release imutável que guarda o commit em `REVISION`, e
  registra cada ativação em `implantacoes.log`, **fora do repositório** (§8 de
  `doc/implantacao-em-producao-ubuntu.md`). Nenhum dado do repositório diz o que está implantado em
  homologação ou em produção, nem desde quando.
- **PR integrado não é capacidade entregue.** Boa parte dos PRs é só de especificação (`spec`,
  `plan`, `tasks`) ou de documentação; outros entregam parte de uma spec (a `152` tem cinco de seis
  histórias; a `156`, três de oito). A auditoria de consolidação de 13/11
  (`doc/auditoria-consolidacao-gps-2026-11-13/`) e a Visão do Sistema, com os selos *Implementado* e
  *Parcial*, são a evidência mais confiável do que está no código.
- **Algumas capacidades dependem do ambiente.** Os avisos por e-mail aos candidatos estão ligados em
  desenvolvimento e desligados em produção até a validação de LGPD; os cenários de treinamento só
  existem com a chave própria; a gestão de acessos e o cadastro de unidades só existem no modo
  institucional, que o seletor de demonstração não alcança.

### O que esta spec cobre, e o que fica fora

**Cobre:**
- a página **Novidades do GPS** na gestão, em linha do tempo, da mais recente para a mais antiga, com
  filtro por categoria;
- o item **Novidades** na barra, com a contagem discreta do que a pessoa ainda não viu;
- o bloco **Desde sua última visita** no topo da página;
- o arquivo versionado das notas, a validação dele e o histórico inicial, de 15/09 a 14/11/2026 (`D-010`);
- um roteiro assistido, fora da aplicação, que prepara o rascunho das notas a partir dos PRs
  mergeados desde a última atualização.

**Fica fora:**
- **"Em preparação" (roadmap).** Não se mistura o entregue com o planejado (`D-009`).
- **CMS, tela de edição ou cadastro de notas pela interface.** A nota é revisada no PR, como o código.
- **Imagens e demonstrações gravadas.** O formato admite orientação em passos; imagem fica para uma
  segunda entrega, se a primeira mostrar que falta.
- **Novidades no portal do candidato.** Esta spec é da gestão.
- **Chamada ao GitHub ou a modelo de linguagem em execução.** O roteiro assistido roda na máquina de
  quem cura, nunca no servidor.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Quem volta ao GPS entende o que mudou (Priority: P1)

Uma servidora da comissão usou o GPS na sexta-feira e volta na segunda. A barra mostra **Novidades**
com um número pequeno ao lado. Ela abre a página e lê, no topo, **Desde sua última visita**: os
títulos do que chegou desde então, cada um com a categoria. Abaixo, a linha do tempo, agrupada por
mês. Em cada cartão ela vê o que mudou, para que serve e, quando a mudança pede, como começar e um
link para a tela.

**Why this priority**: é o critério de sucesso que o usuário definiu. Sem isso não há feature.

**Independent Test**: com duas novidades publicadas depois da última visita registrada de uma
identidade, abrir a gestão e a página, e conferir a contagem na barra, o bloco do topo e os cartões.

**Acceptance Scenarios**:

1. **Given** uma identidade que viu todas as novidades menos duas, **When** ela abre qualquer tela da
   gestão, **Then** o item Novidades da barra mostra `2`, com texto acessível "2 novidades não
   vistas".
2. **Given** a mesma identidade, **When** ela abre Novidades do GPS, **Then** o topo diz "Desde sua
   última visita" com as duas, na ordem da linha do tempo, cada uma levando ao seu cartão.
3. **Given** que ela abriu a página, **When** ela volta a outra tela da gestão, **Then** o número
   some da barra.
4. **Given** que ela recarrega a página na mesma sessão, **When** a página abre de novo, **Then** o
   bloco "Desde sua última visita" continua com as mesmas duas: a visita é a sessão, e não o
   carregamento.
5. **Given** uma nova sessão, dias depois, sem novidade nova, **When** ela abre a página, **Then** não
   há bloco "Desde sua última visita", e a página diz que não há nada novo desde a última visita.

---

### User Story 2 — A nota diz o que a pessoa ganha, e não o que o código fez (Priority: P1)

Cada novidade é uma capacidade, e não um PR. Vários PRs da mesma capacidade viram uma nota só. A nota
diz, em linguagem de quem opera: o que mudou, o benefício, onde encontrar e, quando necessário, dois
ou três passos. "Saiba mais" leva à seção da Documentação do Sistema que já descreve a capacidade, em
vez de repeti-la.

**Why this priority**: uma página de log técnico seria só mais um lugar para não ler.

**Independent Test**: a validação do arquivo recusa a nota com jargão de desenvolvimento no texto
visível, e a revisão do conteúdo inicial confere cada nota contra a tela real.

**Acceptance Scenarios**:

1. **Given** a nota "Centro de Controle do Edital", que reúne cinco PRs, **When** a página é lida,
   **Then** aparece um cartão só, e nenhum texto visível cita número de PR, spec, requisito ou commit.
2. **Given** uma nota com destino numa tela que a pessoa não alcança, **When** ela lê o cartão,
   **Then** o cartão aparece sem o link "Abrir", e continua dizendo onde a capacidade mora.
3. **Given** uma nota com "Saiba mais", **When** a pessoa a segue, **Then** chega à seção correspondente
   da Documentação do Sistema.

---

### User Story 3 — A página não anuncia o que este ambiente não tem (Priority: P1)

A homologação e a produção rodam commits diferentes, e algumas capacidades dependem de configuração.
A página só mostra o que existe no código que está rodando e está ligado ali.

**Why this priority**: anunciar o que não existe destrói a confiança na página na primeira semana.

**Independent Test**: com a configuração dos avisos aos candidatos desligada, a nota do aviso de
pendência documental não aparece na página nem conta na barra; ligada, aparece.

**Acceptance Scenarios**:

1. **Given** uma nota condicionada a uma configuração desligada neste ambiente, **When** qualquer
   pessoa abre a página, **Then** a nota não aparece, não conta na barra nem no filtro.
2. **Given** uma nota reservada a quem tem uma capacidade (por exemplo, administrar acessos), **When**
   quem não a tem abre a página, **Then** a nota não aparece para ela.
3. **Given** um servidor que roda um commit anterior à nota, **When** a página abre, **Then** a nota não
   existe ali: ela viaja com o código.

---

### User Story 4 — Filtrar e chegar ao histórico antigo (Priority: P2)

Quem quer só as correções filtra por categoria. Quem procura algo de semanas atrás passa às páginas
anteriores.

**Why this priority**: necessário quando o histórico crescer; com o conteúdo inicial, é conforto.

**Independent Test**: com o conteúdo inicial, o filtro "Correções" mostra só as correções, com a
contagem certa, e a segunda página continua a linha do tempo.

**Acceptance Scenarios**:

1. **Given** a página, **When** a pessoa escolhe "Correções", **Then** só as correções aparecem, o
   filtro escolhido fica marcado e o endereço guarda a escolha.
2. **Given** mais notas do que cabem numa página, **When** a pessoa segue "Novidades anteriores",
   **Then** a linha do tempo continua do ponto em que parou, com o mês repetido no topo se ele
   continuar.

---

### User Story 5 — Publicar uma nota nova é editar um arquivo e abrir um PR (Priority: P2)

Quem cura as novidades roda um roteiro que lista os PRs mergeados desde a última nota, agrupados pela
spec, e escreve um rascunho. Ela traduz, agrupa, descarta o que é só técnico, e abre o PR. A
validação do arquivo recusa o que está malformado, e a revisão do PR recusa o que é enganoso.

**Why this priority**: sem um caminho barato, a página para de ser atualizada em um mês.

**Independent Test**: rodar o roteiro sobre o repositório e conferir que ele lista só os PRs mergeados
depois da referência mais recente do arquivo, sem tocar o arquivo das notas.

**Acceptance Scenarios**:

1. **Given** o arquivo com a última referência no PR 545, **When** o roteiro roda, **Then** ele lista
   os PRs mergeados depois, agrupados por spec, marcando os que são só de documentação.
2. **Given** uma nota com categoria desconhecida, data inválida, identificador repetido ou destino que
   não existe, **When** a suíte roda, **Then** a validação falha dizendo qual nota e qual campo.

---

### Edge Cases

- **Primeira visita de uma identidade.** Não há "desde a última visita". A página não mostra o bloco
  e diz, numa frase, desde quando reúne as mudanças. A barra conta todas as notas, com teto
  de exibição "9+".
- **Identidade de demonstração compartilhada.** O seletor permite que duas pessoas declarem a mesma
  identidade; elas compartilham o que foi visto. É a natureza da demonstração, e não se corrige aqui.
- **Nota retirada do arquivo.** Uma nota que deixa de existir some da página e da contagem; o
  registro de que foi vista fica, inerte.
- **Nota corrigida depois de publicada.** Corrigir o texto não a torna "não vista" de novo. Para
  avisar de novo, publica-se outra nota.
- **Sessão aberta antes da implantação desta feature.** A barra não mostra número até a próxima
  entrada na gestão; a página funciona.
- **Arquivo das notas inválido em execução.** Não acontece em release que passou no CI. Se acontecer,
  a página diz que as novidades estão indisponíveis, a barra não mostra número, e as outras telas da
  gestão não são afetadas.
- **Nota sem data de integração confirmada.** Não entra: a data é obrigatória.

---

## Requirements *(mandatory)*

### Functional Requirements

**A página**

- **FR-7401**: A gestão DEVE ter a página **Novidades do GPS**, alcançável por toda identidade da
  gestão, que lista as notas disponíveis para quem a abre, da mais recente para a mais antiga.
- **FR-7402**: A página DEVE agrupar as notas por mês da data de integração, com o mês e o ano como
  título do grupo.
- **FR-7403**: Cada cartão DEVE mostrar a categoria, a data, o título e o resumo; e, quando a nota os
  tiver, o benefício, o lugar onde a capacidade mora, os passos de uso (recolhidos), o link para a
  tela e o link "Saiba mais" para a Documentação do Sistema.
- **FR-7404**: As categorias DEVEM ser três: **Novidade** (capacidade que não existia), **Melhoria**
  (capacidade existente que ficou melhor) e **Correção** (comportamento errado que deixou de
  acontecer).
- **FR-7405**: A página DEVE oferecer filtro por categoria, com a contagem de cada uma entre as notas
  disponíveis para quem lê, e guardar a escolha no endereço.
- **FR-7406**: A página DEVE paginar a linha do tempo a cada 12 notas, com acesso às anteriores.
- **FR-7407**: O texto visível de uma nota NÃO DEVE citar número de PR, identificador de requisito,
  número de spec, commit, branch ou nome de arquivo do código. Essas referências DEVEM existir no
  arquivo, fora do que se mostra.
- **FR-7408**: A página DEVE dizer, uma vez e no rodapé, que as datas são as de chegada ao GPS, e que
  cada ambiente recebe as mudanças na sua própria implantação.

**O que cada ambiente mostra**

- **FR-7409**: A nota DEVE viajar com o código: as notas que um ambiente mostra são as do arquivo da
  release que ele roda, sem consulta a serviço externo em execução.
- **FR-7410**: A nota PODE declarar uma configuração de que depende; se ela estiver desligada no
  ambiente, a nota NÃO DEVE aparecer, nem contar na barra ou no filtro.
- **FR-7411**: A nota PODE declarar uma ou mais capacidades de quem a lê, e basta uma; a quem não
  tem nenhuma, a nota NÃO DEVE aparecer, nem contar.
- **FR-7412**: O destino do link DEVE ser uma seção da barra, e o link DEVE aparecer só a quem
  alcança essa seção; sem isso, o cartão continua com o texto de onde a capacidade mora. Tela que não
  é seção da barra se diz no texto de onde, sem link (revisão de 14/11, `D-004`).

**Descoberta**

- **FR-7413**: A barra da gestão DEVE ter o item **Novidades**, no grupo Ajuda, antes de
  Documentação do Sistema.
- **FR-7414**: O item DEVE mostrar a quantidade de notas disponíveis para a identidade que ela ainda
  não viu, com teto de exibição "9+", e nenhum número quando for zero.
- **FR-7415**: A contagem NÃO DEVE acrescentar consulta ao banco às telas da gestão: ela se calcula na
  entrada da sessão e na abertura da página, e se guarda na sessão.
- **FR-7416**: Abrir a página DEVE registrar como vistas, para aquela identidade, todas as notas
  disponíveis para ela naquele momento, qualquer que seja o filtro ou a página aberta.
- **FR-7417**: O bloco **Desde sua última visita** DEVE listar, no topo, as notas que eram não vistas
  quando a página foi aberta pela primeira vez na sessão, e DEVE permanecer igual enquanto a sessão
  durar.
- **FR-7418**: A descoberta NÃO DEVE usar janela, modal, aviso que se repete ou qualquer elemento que
  interrompa o trabalho em outra tela.
- **FR-7419**: O registro do que foi visto DEVE se guardar por identidade (o identificador da sessão
  da gestão), com o instante da última visita, e NÃO DEVE guardar outro dado pessoal.

**O arquivo das notas**

- **FR-7420**: As notas DEVEM morar num arquivo de texto estruturado, versionado no repositório e
  empacotado com a aplicação, uma entrada por nota.
- **FR-7421**: Cada nota DEVE ter identificador estável e único, título, data de integração, categoria,
  resumo e ao menos uma referência a PR mergeado; PODE ter benefício, onde, passos, destino (seção da
  barra), âncora da Documentação do Sistema, configuração de que depende e capacidades de quem a lê.
- **FR-7422**: A suíte DEVE validar o arquivo: campos obrigatórios, categorias, datas, identificadores
  únicos, ordem, destinos que existem entre as rotas da gestão, âncoras que existem na Documentação do
  Sistema, configurações e capacidades conhecidas, specs citadas que existem, e o vocabulário proibido
  pela FR-7407.
- **FR-7423**: Uma nota NÃO DEVE entrar no arquivo antes de todos os PRs que ela cita estarem na
  `main`. A nota de spec parcialmente entregue DEVE descrever só a parte mergeada.
- **FR-7424**: Todo PR mergeado na `main` desde o início da janela DEVE ter um destino, e um só:
  citado por uma nota, registrado como sem nota com o motivo, ou só de documentação. O repositório
  DEVE ter um roteiro, fora da aplicação, que seleciona os PRs **pela data do merge** — e não pelo
  número —, lista como pendente o que não tem destino, agrupado por spec, e escreve um rascunho sem
  alterar arquivo nenhum do repositório. *Revista em 14/11: a primeira versão cortava pelo maior
  número citado, e perdia o PR aberto antes e mergeado depois.*
- **FR-7425**: O repositório DEVE ter um guia curto de curadoria: o que vira nota, o que não vira, como
  agrupar, como escrever, e a lista de conferência da revisão.

**O conteúdo inicial**

- **FR-7426**: O arquivo DEVE nascer com as notas das capacidades entregues entre 15/09 e
  14/11/2026, conferidas contra o código da `main` e contra a Documentação do Sistema, sem nota de PR
  só de especificação ou documentação, e sem PR de produto da janela sem destino.

- **FR-7427**: A nota DEVE ser escrita como anúncio para quem opera, e não como relatório técnico:
  título que promete o ganho (até 70 caracteres), resumo de duas frases curtas em "você" (até 300),
  sem palavras do sistema ("marco", "recorte", "derivação", "apuração") nem siglas internas, e um
  **exemplo** — uma cena concreta, mostrada como "Na prática" (até 300) —, obrigatório na categoria
  Novidade. *Revista em 14/11 (`D-012`): o ajuste miúdo é uma nota incremental de uma linha, e não um
  pacote "Pequenas melhorias" com assuntos distintos.* A suíte cobra
  os tamanhos, o vocabulário e o exemplo; o guia `doc/curadoria-das-novidades.md` traz a diretriz com
  antes e depois (`D-011`).

**A vitrine das capacidades** *(revisão editorial de 14/11, `D-012`, `D-013`; faixa própria — ver
"Faixa de identificadores")*

- **FR-7601**: Toda nota DEVE declarar a **relevância** para quem opera — *transformadora* (cria uma
  capacidade ou elimina uma operação trabalhosa), *relevante* (melhora uma jornada existente) ou
  *incremental* (ajuste, legibilidade, correção pontual) —, medida pelo benefício e nunca pelo número
  de PRs. A relevância decide o peso do cartão: a incremental é uma linha enxuta, sem exemplo nem
  "Como usar".
- **FR-7602**: A página DEVE abrir, antes do histórico, a seção **"Descubra o que o GPS já faz"**, com
  as capacidades do produto — no máximo dez, seis à vista e o resto recolhido —, só na primeira
  página e sem filtro. Cada cartão traz ícone, título, duas frases, "Veja como funciona" recolhido
  (por onde começar, até três passos, quantas atualizações a construíram e desde quando, e os links)
  e nenhuma data de lançamento.
- **FR-7603**: A nota que faz parte de uma capacidade DEVE dizer "faz parte de" com o link para o
  cartão dela; a nota pertence a uma capacidade no máximo.
- **FR-7604**: O bloco "Desde sua última visita" DEVE abrir pela mudança de maior relevância, e não
  pela mais recente; as demais vêm contadas por tipo, e só três delas nomeadas, com o resto apontando
  para o histórico.
- **FR-7605**: A capacidade DEVE ser escrita pela ordem "o que agora é possível", "por que isso
  facilita" e "por onde começar": título até 70 caracteres, resumo até 240, até três passos, sem
  palavra do sistema nem jargão.
- **FR-7606**: A capacidade DEVE obedecer às mesmas regras de disponibilidade da nota (configuração e
  público) e só entrar no arquivo quando o que ela promete estiver disponível; o que está em
  desenvolvimento, só no desenvolvimento local, ou atrás de chave desligada por padrão não é
  anunciado como entregue. A matriz das capacidades, com a disponibilidade e a evidência de cada uma,
  está em [capacidades.md](capacidades.md).

### Requisitos de experiência

- **UX-801**: A página DEVE usar a moldura, a tipografia, as cores e os componentes da gestão; nenhuma
  linguagem visual nova.
- **UX-802**: O cartão DEVE ser compacto: título, uma linha de categoria e data, e o resumo cabem sem
  rolagem num notebook de 1.280 px; o detalhe fica recolhido.
- **UX-803**: A categoria DEVE se distinguir por texto, e não só por cor.
- **UX-804**: A página DEVE funcionar sem rolagem horizontal a 375 px, 1.280 px e 1.440 px, e não
  pressupor tela ultralarga.
- **UX-821**: A vitrine é uma grade de cartões compactos, sem cor nova nem selo; o detalhe fica em
  "Veja como funciona", e o excesso, em "Ver mais N capacidades", para o histórico não ir para longe
  da primeira tela.
- **UX-822**: O peso visual segue a relevância, e não a cor: a transformadora ganha filete e marcador
  cheio; a relevante, o cartão de sempre; a incremental, uma linha sem moldura.
- **UX-806**: O exemplo aparece logo abaixo do resumo, rotulado "Na prática", destacado por um filete
  e pelo fundo neutro da gestão, sem competir com o título.
- **UX-805**: A contagem da barra DEVE ser discreta (um número pequeno ao lado do rótulo, e um ponto na
  barra recolhida), com texto para leitor de tela.

### Key Entities

- **Nota de novidade**: a comunicação de uma capacidade entregue. Mora no arquivo versionado, e não no
  banco. Atributos em FR-7421.
- **Leitura das novidades**: por identidade da gestão, o conjunto de identificadores de nota já vistos
  e o instante da última visita. Não é ato do certame nem dado normativo.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-2501**: Uma pessoa da comissão que volta ao GPS depois de três dias identifica, em até dois
  minutos, o que mudou, o que é novo, o que foi corrigido e por onde começar. *Validação humana,
  pendente.*
- **SC-2502**: 100% das notas do conteúdo inicial citam PR mergeado e descrevem capacidade presente no
  código da `main`, conferida contra a Documentação do Sistema ou a tela; nenhuma nota vem de PR só de
  especificação.
- **SC-2503**: As telas da gestão fazem o mesmo número de consultas ao banco com e sem esta feature,
  fora a entrada da sessão e a própria página.
- **SC-2504**: A página abre sem erro no console e sem rolagem horizontal a 375, 1.280 e 1.440 px.
- **SC-2505**: Publicar uma nota nova é editar um arquivo e abrir um PR; nota malformada reprova a
  suíte antes do merge.
- **SC-2511**: Teste de descoberta: em cinco capacidades da vitrine, alguém da comissão que não
  acompanhou o desenvolvimento responde, em até 15 segundos cada, o que agora consegue fazer, por que
  isso facilita o trabalho e onde encontra. *Validação humana, pendente; a avaliação desta revisão é
  heurística, e nenhum teste com operador foi feito.*
- **SC-2506**: Nenhum texto visível de nota cita PR, requisito, spec, commit ou arquivo de código.

---

## Assumptions

- A data de integração na `main` é a única data que o repositório conhece com certeza; a data de
  implantação em cada ambiente fica fora do repositório (`D-002`).
- O identificador da identidade da gestão, o mesmo que a trilha usa, é estável entre sessões para a
  mesma pessoa, no seletor e no modo institucional.
- Quem cura as notas é quem desenvolve, ou alguém por quem a pessoa responsável pelo produto responda,
  e a aprovação é a do PR.
- O conteúdo inicial começa em 15/09/2026, 60 dias antes da primeira entrega (`D-010`).

---

## Decisões

### D-001 — A nota viaja com o código

A nota mora num arquivo do repositório, empacotado na release como o resto do `backend/`. Como a
implantação constrói a release de um commit da `main`, um ambiente só mostra uma nota se roda um commit
que a contém, e só a contém se os PRs que ela cita já estavam na `main` quando ela entrou (FR-7423). É
o que impede, sem saber nada da implantação, de anunciar o que não existe no código que roda. A
alternativa — ler o GitHub ou o `implantacoes.log` em execução — acrescenta dependência externa e
leitura de arquivo fora da release para resolver o que a ordem dos merges já resolve.

### D-002 — A data mostrada é a de chegada ao GPS; o "não visto" não depende dela

O repositório não sabe quando cada ambiente foi implantado. A página mostra a data de integração, e diz
isso uma vez (FR-7408). O que é "novo para você" é decidido pelo identificador da nota, e não pela data:
uma nota integrada na segunda e implantada na sexta aparece como não vista na sexta, mesmo com data
anterior à última visita. Comparar datas perderia justamente esse caso.

### D-003 — A configuração do ambiente esconde a nota

Uma nota sobre capacidade que depende de configuração declara a configuração, e some onde ela está
desligada (FR-7410). Assim a nota dos avisos aos candidatos aparece na homologação e não em produção,
até a validação de LGPD ligar a chave.

### D-004 — A nota pode ser de um público; o link, de quem alcança a tela

Uma nota sobre a administração de acessos não interessa a quem não administra acessos; ela declara as
capacidades de quem a lê, e basta uma (FR-7411) — quem administra na unidade e quem administra na
instituição têm capacidades diferentes, e os dois usam a tela. A maioria das notas não declara nada e
é para todos. O link segue a barra: o destino é uma seção dela, e só quem alcança a seção vê "Abrir"
(FR-7412). Oferecer um destino que a autorização recusa é o defeito que a barra da `076` foi desenhada
para não ter; uma capacidade própria do link seria uma segunda regra de autorização, fora da barra, e
a revisão de código de 14/11 a retirou da spec em vez de implementá-la.

### D-005 — A contagem não custa consulta às telas

A barra da gestão "não consulta o banco": as capacidades vêm da sessão, e a barra se monta só quando o
template a lê. A contagem segue a mesma regra: calcula-se na entrada da sessão e na abertura da página,
e a barra lê da sessão (FR-7415). O preço é a contagem não acompanhar, na mesma sessão, uma visita feita
noutro navegador; volta a ficar certa na próxima entrada.

### D-006 — Abrir a página é ver; a visita é a sessão

Abrir a página marca como vistas todas as notas disponíveis para a pessoa (FR-7416). Marcar cartão a
cartão, ou exigir "marcar como lida", transforma a página numa caixa de entrada. Para o bloco "Desde sua
última visita" não sumir ao recarregar, ele é guardado na sessão em que a visita aconteceu (FR-7417).

### D-007 — Arquivo TOML, sem dependência nova

O formato é TOML: o Python do projeto o lê sem biblioteca nova, ele admite texto longo em várias linhas e
comentários, e a revisão no PR o lê como texto. JSON (o precedente das Unidades) não tem comentário nem
texto em várias linhas; YAML pediria dependência; Markdown com cabeçalho pediria um interpretador. Não há
tela de edição: a nota é revisada no PR, como o código que ela descreve.

### D-008 — O roteiro assistido roda fora da aplicação, e só rascunha

O roteiro lê os PRs pelo `gh` na máquina de quem cura, agrupa pela spec, marca os só de documentação e
escreve um rascunho num arquivo à parte (FR-7424). Não escreve no arquivo das notas, não chama modelo de
linguagem e não publica: traduzir para a linguagem de quem opera e decidir o que é capacidade entregue é
curadoria humana. Um agente pode ajudar a redigir na mesma sessão em que o roteiro roda; a revisão do PR
é a barreira.

### D-009 — "Em preparação" fica fora

Misturar o entregue com o planejado na mesma página é o que faria a página anunciar o que não existe. Um
roadmap, se vier, será outra página, com outra fonte (as specs aprovadas), e outra spec.

### D-010 — O conteúdo inicial cobre 60 dias, descritos como o produto é hoje

O usuário pediu 60 a 90 dias. A primeira versão começou em 17/10, com a moldura atual da gestão, e a
segunda revisão de 14/11 apontou que a troca da moldura não basta para deixar de fora as capacidades
daquele período que ainda existem. O usuário decidiu estender (P-4). O conteúdo inicial cobre de 15/09
a 14/11/2026, e a página o diz na primeira visita.

**A nota de setembro descreve a capacidade como ela existe hoje**, e não a tela em que ela nasceu:
boa parte daquelas telas foi refeita a partir de 17/10. A capacidade que foi depois substituída ou
removida não ganha nota; o PR dela vai para o registro, com o motivo.

### D-011 — A nota é um anúncio, com exemplo

O usuário leu a primeira versão do conteúdo e teve dificuldade de entender: as notas estavam escritas
como relatório — termos internos, frases longas, nenhuma cena do dia a dia. A decisão dele, em 14/11:
"tem que ser algo simples, interessante e que mostre o valor daquela novidade — quase propaganda —,
com exemplos". A nota passa a ter título que promete o ganho, resumo de duas frases em "você", e o
campo `exemplo`, mostrado como "Na prática" (FR-7427, UX-806). O detalhe técnico continua onde já
morava: na Documentação do Sistema, pelo "Saiba mais". A diretriz fica no guia de curadoria, e a suíte
cobra o que dela é verificável — tamanho, vocabulário e exemplo —, para que as próximas notas sigam o
padrão sem depender de quem lembra dele.

---

### D-012 — A unidade editorial é a capacidade, e não o PR

O usuário leu a página reescrita e a achou um changelog bem apresentado: títulos como "Pequenas
melhorias no Edital, nos e-mails e nas páginas" descreviam pacotes de PRs, e uma capacidade que
substitui planilha tinha o mesmo peso de um ajuste de alinhamento. A avaliação que ele trouxe pedia o
"aha moment" — "eu não sabia que o GPS já fazia isso". A página passa a ter duas camadas: a vitrine das
capacidades (FR-7602), que reúne as notas que as construíram, e o histórico, com peso pela relevância
(FR-7601). A categoria continua dizendo o que a mudança é, e "Novidade" passa a se chamar "Nova
funcionalidade", porque o filtro "Novidades" dentro da página Novidades não dizia o que separava. As
notas "Pequenas melhorias" que juntavam assuntos distintos foram desfeitas: cada assunto é uma nota
incremental, e a linha enxuta é o que impede o histórico de pesar.

### D-013 — Só se anuncia o que está disponível, e sem data inventada

A auditoria das capacidades (`capacidades.md`) separou o que existe no código e sem chave do que não
pode ser anunciado: o assistente para candidatos (a página pública é só do desenvolvimento local), o
vídeo da autodeclaração (só no desenvolvimento) e as peças visuais do kit (atrás da lista de modelos
aprovados, vazia por padrão — a nota delas declara a chave, e a capacidade do kit promete só os
textos). O agendamento da Etapa estava em PRs abertos no começo da revisão e entrou na `main` durante
ela; só então ganhou nota e cartão. A capacidade não tem data de lançamento: o cartão diz quantas
atualizações a construíram e a mais antiga que a página conhece.

---

## Perguntas ao usuário

Nenhuma bloqueia o MVP; todas são de governança.

- **P-1 — Quem cura e quem aprova.** A proposta é que quem desenvolve redija junto com o PR da
  capacidade (ou num PR de curadoria semanal), e que você aprove. Outra pessoa da equipe deve aprovar?
- **P-2 — Cadência.** Uma curadoria por semana, antes da implantação na homologação? Ou a cada
  implantação?
- **P-4 — O período do histórico inicial.** *Respondida em 14/11: estender.* O histórico cobre de
  15/09 a 14/11 (`D-010`).
- **P-5 — A faixa repetida com a 169.** A `169` define FR-7400 a 7435 e UX-800 a 803, e a `168`,
  mergeada antes, FR-7401 a 7427 e UX-801 a 806. Qual das duas renumera? A `169` é só especificação,
  sem código que a cite.
- **P-3 — Versão.** O guia de implantação recomenda uma tag anotada por release (`vAAAA.MM.N`). Se ela
  for adotada, a página pode agrupar por versão em vez de mês. Adotar?
