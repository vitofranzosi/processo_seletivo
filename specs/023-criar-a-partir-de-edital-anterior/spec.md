# Feature Specification: Criar Edital a partir de Edital anterior

**Feature Branch**: `claude/edital-template-creation-1960e2`

> **A numeração.** A proposta de origem pedia a `014`. A `014` está reservada no arco aberto pela
> `013` — *012 conclui avaliações; 013 oficializa resultados de Etapa; 014 determina progressão;
> 015 ordena; 016 ocupa vagas* —, e assim também a `016` e a `019`. `specs/` fecha em `022`; esta é
> a `023`.

**Created**: 2026-09-09

**Status**: Draft

**Input**: Editais são recorrentes. Hoje, quando uma oferta se repete, a comissão reaproveita o
Edital anterior **fora do sistema** — abre o documento publicado, copia o que serve, ajusta datas,
vagas e requisitos, e redigita no assistente de composição o que já estava elaborado. A prática já
existe; o que não existe é o caminho estruturado para ela. A `006` adiou explicitamente essa
capacidade — *"Primeiro um Edital completo; depois se descobre se reutilização é problema real"*
(`006`, P-006) — e o Edital completo existe desde então.

> **Frase que governa:** um Edital anterior pode ser o **ponto de partida** de um novo Edital;
> nunca sua **continuação**.

> **E a frase que mantém o corte:** reaproveita-se o que **descreve como a oferta se organiza**;
> nunca o que **aconteceu** na oferta anterior.

> **A frase da interface:** *Reaproveite o que já foi elaborado. Atualize o que mudou.*

---

## 1. Problema

A configuração de um Edital recorrente é substancialmente a mesma da edição anterior: perfis,
modalidades de concorrência, regras normativas, requisitos, documentos exigidos, etapas de
avaliação, estrutura do cronograma, critérios de classificação, seções textuais e anexos. O que
muda é identificação, calendário, quantidade de vagas e pontos localizados do texto.

Mesmo assim, iniciar a nova oferta custa o cadastro inteiro de novo. O efeito não é só tempo:

- o conteúdo volta a ser composto **fora** do sistema, onde nada o valida;
- edições semelhantes divergem por acidente, não por decisão;
- o esquecimento é silencioso — ninguém percebe o requisito que ficou de fora.

A feature traz a prática para dentro do fluxo de elaboração, **sem** inventar comportamento novo:
quem elabora parte de um Edital que já existe e atualiza o que mudou.

---

## 2. A régua de tamanho

Esta feature é pequena por construção, e a régua é parte do requisito. Ela **não cria**:

| Não cria | Porque |
|---|---|
| `ModeloEdital` | o acervo de Editais já é a biblioteca de modelos; uma terceira representação do mesmo conteúdo exige necessidade comprovada (Princípio V) |
| `ReusoEdital`, ou qualquer aresta Edital → Edital | P-6 de `doc/achados-editais-externos.md` — *um processo pode derivar de outro* — é **derivação normativa** e está aberta; duas arestas do mesmo desenho com sentidos incompatíveis serão lidas uma pela outra |
| estado persistido de revisão | a atestação humana já existe: `EM_REVISAO` → `HOMOLOGADO`, com segregação de funções |
| permissão nova | o ato é de elaboração, e `edital:elaborar` já o nomeia (D-001) |
| recusa de publicação nova | nenhum gate desta feature; ver D-006 |
| seleção parcial de conteúdo | D-004 |
| sincronização com a origem | FR-018 |
| migration | nenhuma coluna, nenhuma tabela, nenhum degrau de esquema canônico |

**Se a implementação exigir qualquer um destes itens, o desenho está errado e a spec volta para
revisão.** A verificação é objetiva: `makemigrations --check` limpo, nenhum modelo novo, nenhuma
entrada nova em `PAPEIS`, nenhum achado impeditivo novo em `validate_for_publication`.

---

## 3. O que o repositório já entrega, e que esta feature NÃO constrói

| Já entregue | Onde | Consequência para a `023` |
|---|---|---|
| Assistente de composição com nove etapas e estado derivado do conteúdo | `interface/views.py` | a cópia **não** tem tela de edição própria; o destino cai no assistente que já existe |
| Gravação que substitui o rascunho inteiro, com validação de perfis, cronograma, etapas e documentos | `editais/application/draft.py` | a cópia entra por esse caminho; uma segunda porta de escrita para as mesmas invariantes é o defeito que este repositório mais evita |
| Versão vigente consolidada, e elevação de esquema antigo | `publicacoes/`, `publicacoes/domain/elevacao.py` | é a **fonte** da cópia (D-003) |
| Anexo com artefato em rascunho e artefato congelado, e as regras de cada um | `editais/application/anexos.py`, `editais/models/anexos.py` | a cópia reusa as **regras** e os modelos, **sem chamar os comandos** — `N` comandos seriam `N` saltos de revisão e `N` registros para uma operação (`T-003`) |
| Trilha append-only com ator, operação, agregado e área | `auditoria/` | é onde a origem mora (D-005) |
| Idempotência por chave, atravessando o reenvio do formulário | `shared/application/commands.py`, telas de criação | a cópia segue a mesma forma; não é item de escopo |
| Atestação humana com segregação de funções | `interface/acoes.py` | nenhum gate novo (D-006) |

**Uma proteção que já existe — e a linha exata até onde ela vai.** A gravação do rascunho recusa
identidade que pertença a **outro contêiner**: Perfil, Evento e Etapa alheios
(`_reject_identifiers_of_other_editais`), modalidade que não é do Perfil declarado e Documento
Exigido que aponta Perfil que não é deste Edital (`editais/domain/documentos.py`). A identidade da
Seção é melhor ainda: derivada de `(edital, chave)`, ela se remapeia sozinha.

**E o que ela NÃO confere, que é mais do que parece.** A validação de elaboração do Perfil *"enxerga
só o Perfil"* (`editais/domain/validation.py`) — confere a coerência **interna** do marco, e não a
existência do que ele aponta fora dele. Escapam da gravação e só são impedidas na **publicação**:

| Referência | Onde falha hoje |
|---|---|
| Documento Exigido → Anexo (`attachmentId`) | publicação, como referência pendurada |
| marco → Etapas que ele enumera (`stages`) | publicação — *"Etapa enumerada que não existe no mesmo conteúdo"* |
| critério de desempate → Etapa e → fato declarado | publicação — *"é **aqui** que o critério pendurado é impedido"* |
| método do sorteio → Etapa de habilitação (`drawMethod.qualifyingStageId`) | na gravação é conferido **apenas contra as Etapas que o próprio marco enumera** |

O último é o mais traiçoeiro, e explica os outros: **a cópia preserva a coerência interna**. Um
conjunto de identificadores da origem, não remapeado, continua consistente **consigo mesmo** — o
`qualifyingStageId` segue estando entre as `stages` do marco, e a gravação passa. O erro só aparece
quando alguém tenta publicar, ou nunca aparece, e o Edital novo passa a somar Etapa que não é dele.

**Consequência para esta feature:** cada uma dessas quatro referências precisa de **teste próprio**
de remapeamento (FR-010, SC-003). Não há guarda de domínio a herdar aqui — a guarda é o teste.

---

## 4. Decisões fechadas antes do planejamento

### D-001 — Copiar configuração é elaborar, e a permissão é `edital:elaborar`

A proposta de origem punha a escolha na criação do Processo. Não cabe: `processo:criar` é do
**Gestor** e `edital:elaborar` é do **Elaborador** (`interface/identidade.py`, `PAPEIS`), e escrever
a configuração do Edital é inequivocamente o segundo ato. Pôr a cópia no comando de criação faria o
Gestor autorar conteúdo normativo, ou exigiria conceder-lhe `edital:elaborar` — as duas coisas
desfazem a segregação que a `002` construiu.

**Consequência boa, e é o que fecha o escopo:** o ponto de entrada passa a ser o **assistente de
composição de um Edital vazio**. Um só, e ele serve igualmente ao primeiro Edital de um Processo
novo e a um Edital acrescentado a Processo existente — sem tocar em
`create_process_with_first_edital` nem em `add_edital`.

### D-002 — Só em rascunho vazio

`replace_draft` substitui o rascunho inteiro: o que não é reenviado é apagado. Oferecer a cópia
sobre um Edital que já tem conteúdo destruiria trabalho em silêncio — e nenhum diálogo de
confirmação compra isso de volta.

A oferta aparece, e o comando aceita, **apenas** quando o Edital de destino não tem Perfil, Evento,
Etapa, Documento Exigido, Seção redigida nem Anexo. Fora disso o caminho é o de sempre: editar.

### D-003 — A fonte é a versão vigente da origem, não o estado relacional dela

Este é o ponto em que a leitura ingênua erra, e erra caro. **A Retificação não reescreve as tabelas
relacionais** — ela opera sobre o conteúdo canônico e produz nova versão consolidada
(`publicacoes/application/retificacoes.py`). Logo, para um Edital publicado, `PerfilVaga`,
`EventoCronograma` e companhia guardam o estado **do dia da publicação**, anterior a toda Retificação
posterior.

Copiar o estado relacional reproduziria, em silêncio, uma configuração que **não vigora** — e
justamente nos campos que mais se retificam: datas e quantidade de vagas.

A cópia lê, portanto, a **versão vigente consolidada** da origem, elevada ao esquema corrente por
`elevar`. Isso fixa também a elegibilidade: só é origem quem tem versão publicada.

### D-004 — Cópia integral do que a composição desenha

Sem seleção por blocos, sem pré-visualização do que virá, sem marca por campo.

Os blocos não são independentes: a Etapa referencia Evento do Cronograma, o Documento Exigido
referencia Perfil, modalidade e Anexo, o marco referencia Etapa e o critério referencia Etapa e
fato declarado. Dez caixas de seleção são mil combinações, a maioria estruturalmente inválida — e
o assistente **já é** o editor: não reaproveitar um Perfil é apagá-lo no passo dos Perfis, onde
quem elabora ia entrar de todo modo.

**A lista branca é definida por referência, e não enumerada:** copia-se o que as etapas de composição
**desenham** — e o verbo é esse, não *gravam*, pela razão do segundo item abaixo. Três
consequências, as três desejadas:

- **identificação não é copiada** — número, ano, título e descrição são entrada da criação, que já
  aconteceu; e `(escopo, número, ano)` é único, de modo que copiar o número seria impossível antes
  de ser indesejável;
- **o que não tem tela não é copiado.** *Persistir* não é *desenhar*: `replace_draft` preserva
  campos que nenhuma etapa do assistente oferece, justamente para que gravar uma etapa não apague em
  silêncio o que outra decidiu (`PRESERVADO_DA_ETAPA`). Copiá-los entregaria ao novo Edital
  conteúdo normativo que quem elabora não tem como revisar nem remover — um beco sem saída na
  jornada, que é o defeito que a `006` existiu para fechar. A ausência é o comportamento de todo
  Edital criado do zero pelo assistente, e é o lado seguro.

  **Não são copiados**, e a lista é fechada: `maxInscricoesPorCandidato` (`015`, FR-063),
  `classificationInformation` e `callInformation` do Perfil — *"os dois objetos normativos do Perfil
  que nenhuma tela desenha"*. Se um Edital de origem os trouxer, a prévia do destino mostra a
  ausência, e fechar a lacuna é da feature que der tela a eles, não desta.

**E uma terceira consequência, que é de execução e não de tela: o `status` do Evento reinicia.**
`EventoCronograma.status` é preservado pela gravação e não é editável no Cronograma, e ele descreve
o que **aconteceu** — `EM_ANDAMENTO`, `CONCLUIDO`, `CANCELADO`. Carregá-lo faria a oferta nova
nascer com o calendário da anterior já cumprido, contra a frase que governa. Todo Evento copiado
nasce `PLANEJADO`.

A designação do período de inscrições (`isRegistrationPeriod`) é o contrário disso — é configuração,
tem tela no passo `Inscrição` — e é copiada.

### D-005 — A origem só na trilha, e é a **versão** que ela nomeia

Um evento na trilha, que nomeia a origem, o ator e o instante. Nenhuma coluna, nenhuma tabela,
nenhuma chave estrangeira — pela razão da régua (§2) e por uma segunda, de conteúdo: **o Edital novo
não publica que foi copiado de outro.** Origem de autoria não é norma, e não entra no conteúdo
canônico.

**O que se registra é a versão consolidada, e não o Edital.** A Constituição exige, de quem
incorpora conteúdo reutilizável, que *"estas DEVEM preservar independência **e versão**"*
(*Restrições e Invariantes do Domínio*) — e a razão é prática: a origem pode ser retificada depois da
cópia, e aí *de qual configuração partimos* deixa de ter resposta se o registro só nomear o Edital. A
versão responde as duas perguntas de uma vez, porque o Edital deriva dela.

**E o termo é `origem`, não `proveniência`.** *Proveniência* já designa, neste domínio, a relação
`caminho normativo → Publicação` de `VersaoConsolidada.proveniencias` (`004`, `005`). Dois sentidos
para a mesma palavra — ambos sobre *de onde isto veio* — é o que o princípio I recusa.

A trilha é append-only e indexada por agregado (`auditoria/models.py`), então a pergunta *de onde
este Edital partiu* é respondida onde as outras perguntas de autoria de ato já são.

### D-009 — Trocar a origem é permitido sempre, e o que se perde é dito antes

A primeira redação fechava a porta: escolhida a origem, a afordância sumia e o comando recusava. O
caminho de volta era refazer à mão — ou cancelar o Edital, **que queima o número**, porque
`uq_edital_scope_number_year` não tem condição e o cancelado continua ocupando `(escopo, número,
ano)` para sempre. Errar a escolha custava caro, e o custo não aparecia na hora de escolher.

**A troca é a mesma operação, com uma precondição diferente.** `replace_draft` já substitui o
rascunho inteiro; o que precisa de cuidado são os Anexos, que não viajam nele e colidiriam em
`uq_anexo_edital_order` — eles saem antes, e os artefatos junto, pelo critério que a `020` já
escreveu: artefato que nenhuma versão publicou é rascunho substituível.

**Permitir sempre, e não proibir depois da primeira gravação.** A alternativa considerada era
bloquear a troca assim que alguém gravasse — derivável da trilha, sem estado novo. Foi recusada
porque tranca a saída justamente para quem mais precisa dela: um "Avançar" no assistente bastaria
para prender a pessoa à origem errada.

**O que a substitui é a lista.** Descartar em silêncio e reaproveitar em silêncio são os dois erros
simétricos, e enumerar o que se perde **antes** de perder é o que evita os dois — é a decisão que o
portal já tomou para a mudança de modalidade (`009`, FR-031), aplicada aqui.

**A confirmação é a recusa apresentada**, e não uma segunda verificação da precondição: a tela chama
o comando, e é `draft_not_empty` que ela traduz em pergunta. Perguntar antes faria a repetição
conhecida — mesma chave, cópia já feita — cair na pergunta em vez de terminar onde a primeira
terminou.

### D-006 — Nenhum gate novo, e o stepper fica como está

Não existe *"você ainda não revisou as seções reaproveitadas"*. Seria o primeiro impedimento
fundado em estado **não normativo** de elaboração; seria satisfeito abrindo e gravando sem ler — a
mesma fraqueza que `interface/views.py` já nomeia ao recusar persistir visita; e há duas atestações
humanas no caminho, com atores distintos.

**Resíduo declarado, e é consciente.** O estado das etapas do assistente é derivado do conteúdo:
etapa com conteúdo é *concluída*. Depois da cópia, todas aparecem concluídas — e ninguém as compôs
para esta oferta. O aviso persistente de FR-014 é o que responde por isso na V1. Um quarto estado
(*reaproveitada*, que vira *concluída* quando a etapa é gravada) é derivável sem estado novo, porque
a trilha já guarda **qual área** mudou em cada gravação (`006`, FR-042) — mas é evolução, e só se
justifica depois de observar que alguém se confundiu.

### D-007 — Anexo: artefato próprio, em rascunho

Apontar o Edital novo para o artefato **congelado** da origem seria seguro quanto aos bytes e errado
quanto ao ciclo de vida: `congelado_em` não nulo significa publicado e imutável por trigger, e o
rascunho do destino não poderia substituir o próprio anexo.

A cópia cria artefato próprio, com `congelado_em` nulo — substituível, como todo anexo de rascunho.
Resumo criptográfico repetido é legítimo por decisão já tomada (`020`, FR-011).

**Preço dito em voz alta:** os bytes são duplicados, e o limite por anexo é de 5 MB. É o custo de
não compartilhar ciclo de vida, e a V1 o aceita.

### D-008 — Origem: Editais publicados ou encerrados do mesmo escopo

Restrição que resolve a autorização sem inventar permissão: o conteúdo de um Edital publicado **já é
público** — existe consulta pública dele —, e seus anexos congelados também o são, *"porque é
norma"* (`020`). Ler para copiar não concede nada que o portal já não conceda.

Ficam fora: rascunho de terceiro (não é conteúdo institucional, e ler o de outra comissão exigiria
permissão que ninguém tem hoje) e Edital cancelado (não se parte de ato desfeito).

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Partir da edição anterior (Priority: P1)

Quem elabora cria o Edital da nova oferta como sempre — Processo novo com o primeiro Edital, ou
Edital acrescentado a um Processo — e, ao abrir a composição de um Edital ainda vazio, escolhe um
Edital anterior como ponto de partida. O assistente abre preenchido com a configuração que vigora na
origem, e a pessoa segue editando o que mudou.

**Why this priority**: é a feature. Sem ela não há nada a demonstrar.

**Independent Test**: criar um Edital, escolher uma origem publicada, e percorrer o assistente
encontrando em cada etapa o conteúdo da origem, editável.

**Acceptance Scenarios**:

1. **Given** um Edital `EM_ELABORACAO` sem nenhum conteúdo e um Edital publicado no mesmo escopo,
   **When** quem elabora escolhe esse Edital como ponto de partida, **Then** o Edital de destino
   passa a ter os Perfis, modalidades, regras, fatos, marcos, critérios, Eventos, Etapas, Documentos
   Exigidos, Seções textuais e Anexos da versão vigente da origem, todos com identidade própria.
2. **Given** a cópia concluída, **When** quem elabora abre qualquer etapa do assistente, **Then**
   edita e grava pelo caminho normal, sem tela nova e sem etapa nova.
3. **Given** a cópia concluída, **When** se consulta a origem, **Then** ela está inalterada —
   conteúdo, situação e revisão.
4. **Given** um Edital que já tem qualquer conteúdo, **When** se tenta partir de outro Edital,
   **Then** o sistema recusa e diz por quê, sem apagar nada.

---

### User Story 2 — O novo Edital não carrega o certame anterior (Priority: P1)

Quem elabora precisa saber, sem conferir tabela por tabela, que o Edital novo não trouxe nada do
certame da origem: nem candidato, nem inscrição, nem documento enviado, nem avaliação, nem
resultado, nem recurso, nem sorteio.

**Why this priority**: é a condição de legitimidade da operação. Um Edital que nascesse com execução
alheia seria inutilizável e indefensável.

**Independent Test**: depois da cópia, as telas de inscrições, distribuição, resultados e recursos
do Edital novo mostram certame vazio.

**Acceptance Scenarios**:

1. **Given** uma origem com inscrições, avaliações, resultados e recursos, **When** a cópia termina,
   **Then** o Edital de destino tem zero de cada um deles.
2. **Given** uma origem cujo Documento Exigido aponta um Anexo, **When** a cópia termina, **Then** o
   Documento Exigido do destino aponta o Anexo **do destino**, e baixá-lo entrega o arquivo do
   destino.
3. **Given** uma origem que usa as outras três referências que a gravação do rascunho não confere —
   marco que enumera Etapas, critério de desempate que aponta Etapa e fato declarado, e método de
   sorteio com Etapa de habilitação —, **When** a cópia termina, **Then** as três apontam objetos do
   destino, e nenhuma alcança a origem (FR-010a).

---

### User Story 3 — Saber de onde este Edital partiu (Priority: P2)

Quem elabora, quem homologa e quem audita identificam que o Edital foi iniciado a partir de outro, e
qual.

**Why this priority**: sem isso a operação é invisível depois de feita — e quem homologa precisa
saber que está diante de conteúdo herdado, não redigido para esta oferta.

**Independent Test**: abrir a composição e a trilha do Edital novo e encontrar a origem nas duas.

**Acceptance Scenarios**:

1. **Given** um Edital criado a partir de outro, **When** quem elabora abre a composição, **Then** vê
   aviso permanente que nomeia a origem e pede a atualização das informações desta oferta.
2. **Given** o mesmo Edital, **When** se abre a trilha, **Then** há registro que nomeia a origem, o
   ator e o instante.
3. **Given** o mesmo Edital já publicado, **When** se abre a trilha, **Then** o registro continua
   lá.

---

### Edge Cases

- **Origem com Seções geradas.** O conteúdo canônico descreve as doze Seções do catálogo, e as
  geradas não têm texto persistido (`006`, FR-034 e FR-036). A cópia reproduz **só as textuais**;
  tentar gravar uma gerada é recusado pelo domínio, e com razão.
- **Origem retificada depois de publicada.** Copia-se a versão **vigente**, e não a primeira — é o
  que D-003 existe para garantir.
- **Origem publicada em esquema antigo.** O conteúdo é elevado ao esquema corrente antes de ser
  copiado; a elevação não inventa dado, declara ausência.
- **Origem sem anexo, sem Etapa ou sem Documento Exigido.** Todas as três são configurações
  legítimas. A cópia reproduz a ausência, sem recusa.
- **Origem em outro Processo, ou em Processo encerrado.** Indiferente: a origem é lida, nunca
  alterada, e Processo encerrado não impede leitura.
- **Duas submissões da mesma operação.** O Edital de destino já existe — não é ele que a operação
  cria. A segunda submissão não executa segunda cópia, não acrescenta nada ao que a primeira gravou
  **e não é recusada por rascunho não vazio**, ainda que o rascunho já esteja cheio — foi a primeira
  cópia que o encheu (`FR-017a`).
- **Falha no meio da cópia.** Não existe meio: ou o destino recebe tudo, ou nada.
- **Nenhum Edital elegível no escopo.** A oferta não aparece, ou aparece dizendo que não há origem
  disponível — nunca uma lista vazia sem explicação.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Na composição de um Edital em elaboração cujo rascunho está **vazio**, o sistema DEVE
  oferecer iniciá-lo a partir de um Edital anterior.
- **FR-002**: A oferta NÃO DEVE aparecer quando o rascunho já tiver qualquer conteúdo, e a operação
  DEVE ser recusada nesse caso, com mensagem que diz o motivo e sem alterar nada (D-002).
- **FR-003**: A operação DEVE exigir `edital:elaborar` e NÃO DEVE introduzir permissão nova (D-001).
- **FR-004**: A escolha da origem DEVE listar apenas Editais do escopo institucional do ator em
  situação publicada ou encerrada, identificados por número, ano, título e Processo, e DEVE permitir
  localizá-los por esses atributos (D-008).
- **FR-004a**: A lista de origens DEVE informar, para cada uma, **o que ela traz** — quantos Perfis,
  Etapas, Eventos, Documentos Exigidos e Anexos — e quando o Edital foi publicado. A contagem DEVE
  ser feita sobre o **conteúdo que vigora**, e não sobre o estado relacional: a coluna promete o que
  a cópia entrega, e contar noutro lugar faria a promessa divergir dela (`D-003`). A lista DEVE ser
  paginada, porque o acervo de Editais publicados só cresce.
- **FR-004b**: A lista DEVE oferecer, para cada origem, o caminho até o **Edital publicado** dela,
  para que a escolha seja feita depois de ler e não antes. NÃO DEVE haver segunda renderização do
  conteúdo: a página pública daquele Edital já o mostra inteiro, com o documento e os anexos.
- **FR-002a**: Com o rascunho **não vazio**, a escolha de uma origem DEVE ser oferecida como
  **substituição**: o sistema DEVE enumerar o que será descartado — Perfis, Eventos, Etapas,
  Documentos Exigidos, Seções redigidas e Anexos — e só substituir depois de confirmado (`D-009`).
  Sem confirmação, a recusa de `FR-002` permanece.
- **FR-002b**: A substituição DEVE remover os Anexos do destino e os arquivos deles antes de criar
  os novos, e NÃO DEVE tocar em nenhuma das origens.
- **FR-005**: A origem da cópia DEVE ser a **versão vigente consolidada** do Edital escolhido,
  elevada ao esquema canônico corrente (D-003).
- **FR-006**: A operação DEVE copiar para o destino a configuração que as etapas de composição
  desenham: Perfis de Vaga com modalidades de concorrência, regras normativas, fatos declarados,
  marcos classificatórios e critérios de desempate; Eventos do Cronograma, inclusive a designação do
  período de inscrições; Etapas de Avaliação; Documentos Exigidos; Seções textuais; e Anexos
  (D-004). O que o conteúdo publicado carrega como **texto** por ser forma canônica — os três
  instantes (início e término de Evento, vigência da regra normativa) e os três decimais da Etapa
  (peso, nota mínima, pontuação máxima) — DEVE voltar a ser instante e decimal na cópia. Não é
  polimento: a validação da gravação compara e inspeciona esses valores, e sobre texto ela **estoura**
  em vez de recusar.
- **FR-007**: A identificação do Edital — número, ano, título e descrição — NÃO DEVE ser copiada.
- **FR-008**: Campo normativo que nenhuma etapa de composição **desenha** NÃO DEVE ser copiado, ainda
  que a gravação o preserve: `maxInscricoesPorCandidato`, `classificationInformation` e
  `callInformation` (D-004).
- **FR-008a**: Todo Evento do Cronograma copiado DEVE nascer com situação `PLANEJADO`,
  independentemente da situação que tinha na origem (D-004).
- **FR-009**: Cada objeto criado no destino DEVE receber identidade própria; nenhuma identidade
  persistente DEVE ser compartilhada entre origem e destino.
- **FR-010**: Toda referência interna DEVE ser remapeada para os objetos do destino — Etapa para
  Evento, Documento Exigido para Perfil, para modalidade e para Anexo, marco para Etapa, critério
  para Etapa e para fato declarado, marco para as Etapas que enumera, e método do sorteio para a
  Etapa de habilitação. Nenhuma referência do destino PODE alcançar objeto da origem.
- **FR-010a**: As quatro referências que a gravação do rascunho **não** confere — Documento Exigido
  para Anexo, marco para as Etapas que enumera, critério para Etapa e para fato, e
  `drawMethod.qualifyingStageId` — DEVEM ter verificação própria, porque a cópia preserva a
  coerência interna e um identificador não remapeado atravessa a gravação sem recusa (§3).
- **FR-011**: Os Anexos DEVEM ser copiados como artefatos próprios do destino, em rascunho e
  substituíveis (D-007).
- **FR-012**: A operação NÃO DEVE alterar a origem — nem conteúdo, nem situação, nem revisão, nem
  versão vigente.
- **FR-013**: O destino NÃO DEVE receber nenhum dado de execução: inscrição, rascunho de inscrição,
  documento enviado, pagamento, membro de comissão, alocação, distribuição, avaliação, parecer,
  resultado, classificação, recurso, sorteio, semente, divulgação ou notificação.
- **FR-014**: Enquanto o Edital criado por esta operação estiver em elaboração, a composição DEVE
  exibir aviso permanente que nomeia a origem e pede a atualização das informações da nova oferta.
- **FR-014a**: **Na entrada desta operação**, a trilha de auditoria DEVE identificar a origem em
  forma legível — o Edital pelo número e ano, e a versão — em vez do identificador que o registro
  guarda. A versão DEVE ser nomeada de modo a **distinguir duas versões do mesmo Edital**: publicar
  uma Retificação rematerializa uma versão por fronteira temporal, e uma data não as separa. O registro guarda identificador para não envelhecer (`FR-015a`); quem o lê é pessoa, e
  capacidade que nenhuma interface alcança não está entregue (Princípio VI). *O alcance é **esta**
  entrada, e não a trilha inteira: outras operações gravam identificador no motivo, e uniformizá-las
  é decisão de quem for dono delas (`T-010`).*
- **FR-015**: A operação DEVE registrar na trilha de auditoria evento que nomeia a origem, o ator e
  o instante, e esse registro DEVE permanecer consultável depois da publicação do novo Edital
  (D-005).
- **FR-015a**: O evento DEVE identificar a origem pelo **identificador da versão consolidada** de
  onde o conteúdo saiu — que é o que preserva *independência e versão*, e de onde o Edital de origem
  deriva. O aviso de FR-014 DEVE ser montado a partir desse identificador, nunca da interpretação de
  texto livre da trilha.
- **FR-016**: A origem NÃO DEVE ser persistida como vínculo entre Editais nem entrar no conteúdo
  canônico publicado.
- **FR-017**: A operação DEVE ser atômica e idempotente por chave. O destino **já existe** quando ela
  começa: o que a repetição não pode produzir é uma **segunda cópia** sobre ele. Falha em qualquer
  ponto NÃO DEVE deixar o destino com conteúdo parcial — inclusive quando o que falha é a etapa dos
  Anexos, que na mesma transação precede a dos Documentos Exigidos.
- **FR-017a**: A repetição conhecida DEVE ser reconhecida **antes** das precondições que a própria
  operação altera. Depois da primeira cópia o rascunho não está mais vazio: conferir a precondição
  antes da chave transformaria toda repetição numa recusa, e a operação deixaria de ser idempotente
  exatamente no caso em que a idempotência existe para servir.
- **FR-018**: Não DEVE existir sincronização entre origem e destino: alteração posterior em qualquer
  um dos dois NÃO DEVE alcançar o outro.
- **FR-019**: O conteúdo copiado DEVE passar pelas mesmas validações de rascunho que a composição
  exige, e a recusa DEVE nomear o que impediu.
- **FR-020**: O Edital de destino DEVE permanecer na situação em que foi criado e NÃO DEVE herdar
  situação da origem.

### Key Entities

Nenhuma entidade nova. A feature opera sobre as que existem:

- **Edital de origem**: Edital com versão publicada, lido e nunca alterado. Não ganha campo, relação
  nem estado por esta feature.
- **Edital de destino**: Edital em elaboração com rascunho vazio, que recebe a configuração copiada.
- **Registro de auditoria**: onde a origem mora, no formato append-only que já existe.

---

## 5. Invariantes observáveis

- **I1** — a origem sai da operação idêntica a como entrou.
- **I2** — o destino é Edital novo, com identidade própria, em elaboração.
- **I3** — nenhuma identidade persistente é compartilhada entre origem e destino.
- **I4** — nenhuma referência do destino alcança objeto da origem.
- **I5** — execução nunca é copiada.
- **I6** — a origem é consultável, nomeia a **versão**, e não é norma.
- **I7** — não existe sincronização posterior.
- **I8** — o fato de a origem ter sido publicada não confere validade ao destino: ele percorre os
  mesmos atos, com os mesmos atores.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Um Edital recorrente é iniciado a partir do anterior em **uma** operação, sem
  recadastro manual de nenhum dos blocos de configuração, e quem elabora passa a trabalhar apenas
  sobre o que muda de uma oferta para a outra.
- **SC-002**: Origem e destino não compartilham **nenhum** objeto: a contagem de identidades em comum
  entre os dois é zero, em todas as coleções copiadas.
- **SC-003**: **100%** das referências internas do destino apontam para objetos do destino,
  **inclusive as quatro que a gravação do rascunho não confere** — nenhum Documento Exigido do novo
  Edital entrega o anexo da oferta anterior, nenhum marco soma Etapa que não é dele, nenhum critério
  de desempate aponta Etapa ou fato da origem, e nenhum método de sorteio habilita por Etapa alheia.
- **SC-004**: A origem permanece inalterada em **100%** das operações: mesma versão vigente, mesmo
  conteúdo canônico, mesma revisão.
- **SC-005**: Para **100%** dos Editais criados por esta operação, a trilha responde de qual Edital e
  de qual **versão** partiram, por quem e quando — inclusive depois de publicados, e inclusive depois
  de a origem ser retificada.
- **SC-006**: O Edital criado nasce com zero inscrições, zero documentos de candidato, zero membros
  de comissão, zero avaliações, zero resultados, zero recursos e zero sorteios.
- **SC-007**: A entrega não acrescenta migration, modelo, permissão, estado persistido de revisão nem
  impedimento de publicação (§2).
- **SC-008**: Um Edital cuja origem foi retificada depois de publicada é iniciado com a configuração
  **que vigora**, e não com a da primeira publicação.

---

## Assumptions

- A demanda é operacional e conhecida: a reutilização de Editais anteriores já acontece fora do
  sistema. A feature não a descobre, internaliza. Comparar duas reedições reais segue útil para
  decidir **o que** destacar na interface, e não é condição para especificar.
- Quem elabora consegue identificar o Edital de origem pelo número e ano — é como a instituição se
  refere a eles.
- A origem típica é a edição do ciclo anterior, publicada e encerrada.
- O Edital de destino é criado pelos caminhos que já existem; esta feature não altera a criação.
- O segundo ponto de entrada possível — reaproveitar dentro de um Processo já existente — é atendido
  pelo mesmo caminho, porque a escolha mora na composição e não na criação (D-001).

---

## 6. Out of Scope

Fora, e cada item com a razão:

- **Ler PDF ou Word de Edital externo.** Outra classe de problema — extração, conferência humana,
  risco de inventar norma. Registrado como capacidade futura, e nunca como efeito desta.
- **Interpretação por IA, OCR, conversão de documento em entidades do domínio.** Mesma razão.
- **`ModeloEdital` e biblioteca de modelos.** §2.
- **Seleção parcial do que reaproveitar.** D-004. Se aparecer demanda real, entra depois, sobre o
  mesmo serviço.
- **Reaproveitar comissão.** Comissão é do Processo, não do Edital: esta feature não clona Processo,
  então não há o que proibir. Facilitar a composição da comissão é da gestão de comissão.
- **Quarto estado do assistente (*reaproveitada*).** D-006. Evolução, com caminho já mapeado.
- **Recusar publicação de Edital com período de inscrições vencido.** É regra de **todo** Edital, e
  não remendo desta cópia. Se a instituição a quiser, ela tem spec própria e protege o acervo
  inteiro.
- **Editar o teto de inscrições por candidato.** Lacuna anterior a esta feature (`015`, FR-063 sem
  tela), e a cópia não a resolve nem a agrava.
- **Derivação normativa entre Editais** — *este Edital preenche as vagas que aquele não preencheu*.
  É P-6 de `doc/achados-editais-externos.md`, e esta feature deliberadamente não lhe toca.

---

## 7. Ordem

São **duas** ordens, e confundi-las foi um defeito desta spec na primeira redação.

### 7.1 A ordem da operação — obrigatória

```text
uma transação, do começo ao fim

  1. autorizar; resolver destino e origem — 404 para o que o ator não alcança
  2. reservar a chave; repetição conhecida devolve o destino e ENCERRA aqui
  3. só agora recusar as precondições mutáveis — rascunho não vazio à frente
  4. ler a versão vigente da origem e elevá-la
  5. montar o mapa  identidade da origem → identidade do destino
  6. criar os ANEXOS do destino                    ← antes do conteúdo, sempre
  7. gravar o conteúdo com as referências remapeadas — os Documentos Exigidos
     já encontram os Anexos do destino para apontar
  8. registrar a origem — a versão consolidada de onde o conteúdo saiu
```

**O passo 2 antes do 3 é `FR-017a`**, e não estilo: a operação altera justamente a precondição que
seria conferida, porque depois da primeira cópia o rascunho não está mais vazio. É a ordem que
`add_edital` já pratica — *"reenviar a requisição que já criou o Edital continua devolvendo o mesmo
Edital, mesmo com o Processo já encerrado"*. O passo 1 antes do 2 pela razão simétrica: repetição
conhecida não é passe para quem não alcança o objeto.

**O passo 6 precede o 7** porque `attachmentId` é referência a objeto que precisa existir, e os dois
estão na mesma transação porque `FR-017` não admite destino pela metade — anexo criado sem o requisito
que o usa é conteúdo órfão, e requisito sem o anexo é referência pendurada que só a publicação
denuncia.

[contracts/copia.md](./contracts/copia.md) detalha esta mesma sequência, com a separação entre ler a
versão e elevá-la.

### 7.2 A ordem de entrega — sugerida

1. **O serviço de cópia inteiro**, na ordem de §7.1, com o remapeamento e os testes das quatro
   referências que a gravação não confere. É onde está o risco técnico real (FR-009, FR-010,
   FR-010a, FR-011).
2. **A escolha da origem na composição**, com a recusa sobre rascunho não vazio (FR-001, FR-002,
   FR-004).
3. **O aviso e a trilha** (FR-014, FR-015, FR-015a).

Cada passo é demonstrável pela interface administrativa, que é o canal de quem elabora
(Princípio VI).

---

## 8. Gate de conclusão

- O cenário de ponta a ponta é navegável: criar Edital, escolher origem publicada, encontrar a
  configuração no assistente, alterar vagas e cronograma, e seguir pelo fluxo normal até publicar.
- Teste de isolamento: nenhuma identidade em comum, nenhuma referência cruzada, origem inalterada.
- **Um teste por referência que a gravação não confere** (§3): Documento Exigido → Anexo, marco →
  Etapas enumeradas, critério → Etapa e → fato declarado, e `drawMethod.qualifyingStageId`. Cada um
  parte de uma origem que **usa** aquela referência, ou não prova nada.
- Teste do reinício: Evento cujo `status` na origem era `CONCLUIDO` nasce `PLANEJADO` no destino.
- Teste da exclusão: origem com `maxInscricoesPorCandidato`, `classificationInformation` ou
  `callInformation` preenchidos produz destino sem eles.
- Teste da versão: origem retificada é copiada pela versão vigente.
- Teste da transação: falha ao criar o último Anexo não deixa Anexo nenhum nem conteúdo no destino.
- `makemigrations --check` limpo, e nenhum item da régua de §2 violado.
