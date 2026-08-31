# Feature Specification: Inscrição Simples e Documentos do Candidato

**Feature Branch**: `009-inscricao-simples-documentos`

**Created**: 2026-08-30

**Status**: Draft

**Input**: Jornada do candidato externo de ponta a ponta — encontrar a oportunidade, identificar-se,
preencher o mínimo, enviar os documentos exigidos, revisar, enviar e receber protocolo — mais a
consulta administrativa do que chegou. Inclui o contrato operacional mínimo que o Edital precisa
para governar inscrições. Redação consolidada após duas rodadas de avaliação da proposta original,
verificadas contra o repositório em `main` (`897b750`).

## A frase que governa esta feature

> **A burocracia pode estar no Edital; não precisa estar na inscrição.**

E a contrapartida institucional, que tem o mesmo peso:

> **O que chega, chega já ligado ao Edital, ao Perfil e ao requisito que atende** — não a uma pasta
> chamada `arquivos_do_candidato_123`.

Todo requisito abaixo responde a uma de duas perguntas: *isto tira atrito de quem se inscreve?* ou
*isto elimina a reorganização manual de quem recebe?* O que não responde a nenhuma das duas não
pertence a esta spec.

## Contexto

O sistema sabe compor, homologar, publicar e retificar um Edital. Não sabe receber uma inscrição.
Hoje, nas seleções conduzidas institucionalmente, o candidato se inscreve por fora, a equipe baixa
arquivo por arquivo depois do encerramento, reorganiza em armazenamento local ou Drive, e passa a
controlar candidatos, documentos e avaliações em planilhas. A 009 elimina a **primeira metade**
desse problema: inscrição, recebimento organizado, armazenamento e consulta dentro do sistema. A
avaliação pela comissão é jornada posterior.

**O que já existe e será consumido, não recriado.** Perfil de Vaga e Modalidade de Concorrência
(`editais/models/perfis.py`), Cronograma e Evento (`editais/models/cronograma.py`), o snapshot
publicado e seu hash (`publicacoes/application/publish_edital.py`), a versão consolidada vigente e a
Retificação (`publicacoes/models_retificacao.py`), a idempotência de comando
(`shared/idempotency.py`), a auditoria append-only (`auditoria/`), o padrão de imutabilidade por
`save()` que recusa update, e o padrão de acessibilidade da interface administrativa
(`interface/templates/interface/base.html`: link de pular, foco visível, contraste comentado com
WCAG 2.1 AA).

**O que não existe e esta feature inaugura.** Não há canal público em HTML — o público hoje é JSON
sob `/api/v1/public` e todo HTML vive sob `/gestao/`. Não há identidade de candidato: o modelo de
ator é institucional, com escopo e permissões (`seguranca/domain.py`), e o seletor de identidade é
proibido em produção. Não há armazenamento de arquivo: nenhum `FileField`, nenhuma raiz de mídia
configurada, e o único binário persistido é o documento publicado, em coluna binária. E o Edital não
sabe dizer qual dos seus Eventos é o período de inscrições nem quais documentos exige — o `type` do
Evento é texto livre.

**A 008.** A `008 — Composição Institucional do Edital` é responsável por terminar o documento. A
009 não entra nela: o contrato operacional de inscrição existe **porque alguém vai se inscrever**, e
alargar a feature anterior para hospedá-lo é exatamente o padrão que o princípio VI da Constituição
proíbe. A relação entre as duas é de artefato, não de escopo, e está declarada abaixo.

## Precondição de implantação

Três condições que não são requisitos de tela e precisam estar declaradas antes de a feature tocar
dados reais.

1. **Incremento canônico.** Esta feature incrementa `SCHEMA_VERSION` **uma única vez** (US2).
   `_assert_versao_canonica` recusa consolidar conteúdo cuja versão divirja da vigente
   (`publicacoes/application/retificacoes.py:483-500`), e a decisão registrada ali é deliberada: não
   converter conteúdo antigo, não atualizar snapshots em massa. Consequência assumida: **Editais
   publicados sob a versão anterior deixam de ser retificáveis**, e os dados de demonstração são
   recriados pela seed — como já ocorreu na `007`. A demonstração de retificação concorrente (US5)
   só é encenável sobre Edital publicado após o incremento.
2. **Barreira com a 008, verificada.** A `008 — Composição Institucional do Edital` já está
   especificada, planejada e decomposta em tarefas, e o plano dela declara que **não toca domínio,
   snapshot, hash nem migration**: a feature inteira vive em `publicacoes/infrastructure/pdf.py`
   mais os dois pontos que chamam o renderizador antes de criar a Publicação
   (`publish_edital.py:364` e `retificacoes.py:580`). Logo a 008 **não incrementa** a versão
   canônica, e o incremento desta feature é o único das duas. O que resta entre elas é **conflito
   textual no compositor**: a entrega 2 escreve nesse mesmo arquivo (FR-010) e DEVE partir da 008 já
   integrada, para que o documento não seja reescrito duas vezes.
3. **Gate de dados reais.** Antes de o sistema receber inscrição de pessoa real, deve existir
   política institucional de retenção e descarte de rascunhos abandonados e de documentos. Esta
   feature minimiza a coleta e declara o gate; **não** implementa rotina automática de descarte.

## Princípios desta feature

### P-001 — O processo seletivo pode ser burocrático; a interface não

Toda informação pedida ao candidato responde a pelo menos uma pergunta: é necessária para
identificá-lo? é exigida pelo Edital? é necessária para executar a seleção depois? Se não for
nenhuma das três, o campo não entra.

### P-002 — Não perguntar o que o sistema já sabe

Dado que venha da identidade autenticada, do Edital, do Perfil, do Cronograma, da modalidade ou da
seleção escolhida não é redigitado.

### P-003 — Divulgação progressiva

O candidato vê apenas o que se aplica à sua inscrição. Quem concorre sem reserva não vê campo nem
documento de modalidade reservada — não desabilitado, não cinza: ausente.

### P-004 — Duas telas antes da confirmação

Depois de identificado: `Sua inscrição` e `Revisar e enviar`. Não existe assistente de sete etapas
para o candidato. O assistente é da autoria; a inscrição é outra coisa.

### P-005 — Ninguém precisa entender a persistência do sistema

Não há botão `Salvar` nem rascunho a carregar. Cada arquivo válido persiste no momento do envio, e
os campos são gravados na passagem para a revisão. Quem volta encontra **Continuar inscrição**.

### P-006 — Um documento é o requisito que ele atende

Arquivo é sempre `Inscrição → Documento Exigido → Documento Submetido`. Essa é a decisão que depois
permitirá à comissão abrir *Diploma exigido → documento apresentado*, e é a razão de a feature
existir do jeito que existe.

### P-007 — O candidato não é um papel institucional

Identidade externa é eixo próprio. Não se acrescenta `CANDIDATO` ao mapa de papéis, e não se concede
permissão institucional a ninguém para conseguir registrar auditoria ou abrir um documento.

### P-008 — Sem motor genérico

Sem construtor de formulários, sem expressão condicional configurável, sem plataforma de upload,
sem máquina de estados genérica, sem motor de avaliação. Quando a solução específica de inscrição e
a solução genérica de "qualquer fluxo documental" atenderem igualmente, a específica vence.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A oportunidade se encontra e se entende (Priority: P1)

Uma pessoa de fora da instituição encontra a seleção publicada, entende para que serve, para quais
vagas pode concorrer e o que precisa apresentar, sem passar por nenhuma tela de gestão e sem se
identificar.

**Why this priority**: é a porta — nenhuma outra história acontece se a pessoa não chegar. Ela se
divide em duas partes de dependência diferente, e a divisão governa a ordem de entrega:

- **Parte consultável (cenários 1 e 2; FR-012, FR-014, FR-017 e FR-018, e a listagem de FR-013 sem
  as colunas de período e situação)** — a seleção, os Perfis e o documento oficial, derivados da
  versão vigente. Não depende de nada que a US2 acrescente, e é a entrega 1.
- **Parte temporal e convite (cenários 3, 4 e 5; FR-015, FR-016, FR-019 e as duas colunas restantes
  de FR-013)** — situação futura, aberta ou encerrada, com data, e o convite por vaga. Dependem do
  período apontado, que só existe depois da US2, e por isso chegam na entrega 2.

*A US1 se conclui na entrega 2. A entrega 1 é uma fatia navegável dela, não a história inteira — e
esta spec diz isso em vez de afirmar independência que não existe.*

**Independent Test**: na entrega 1, publicar um Edital com dois Perfis, abrir a página pública em
uma janela anônima e ler título, unidade, Perfis, vagas, localidade e requisitos, além do documento
oficial publicado — tudo derivado da versão consolidada vigente, sem `/gestao/` e sem identificação.
Na entrega 2, o mesmo percurso passa a informar a situação com a data correspondente e a oferecer a
vaga.

**Acceptance Scenarios**:

1. **Given** um Edital publicado, **When** abro a listagem pública sem estar identificado, **Then**
   encontro a seleção com identificação, título, unidade e situação das inscrições.
2. **Given** essa seleção, **When** abro o detalhe, **Then** leio resumo, Perfis, vagas por Perfil,
   localidade quando houver, requisitos e o link para o documento oficial.
3. **Given** um Edital cujo período de inscrições ainda não começou, **When** leio a página,
   **Then** leio a data de início e não encontro convite para inscrever-me.
4. **Given** um Edital cujo período terminou, **When** leio a página, **Then** ela continua
   consultável e informa que as inscrições estão encerradas.
5. **Given** um Perfil dessa seleção, **When** aciono `Inscrever-se nesta vaga`, **Then** a
   inscrição começa com aquele Perfil já escolhido, sem me pedir para escolhê-lo de novo.

---

### User Story 2 - O Edital governa a inscrição (Priority: P1)

Quem elabora declara, no próprio Edital, qual Evento do Cronograma é o período de inscrições e quais
documentos o candidato precisa apresentar — para todos, para um Perfil, para uma modalidade, ou para
a combinação dos dois. O documento publicado passa a enunciar isso.

**Why this priority**: é o contrato sem o qual o sistema não sabe quando abre, quando fecha nem o
que pedir. É a única história que toca a camada canônica, e por isso concentra o incremento inteiro
numa entrega só.

**Independent Test**: declarar o período e três documentos exigidos (um para todos, um por Perfil,
um por modalidade), publicar, e verificar que os três aparecem no snapshot com identidade estável,
no documento publicado em linguagem normativa, e que uma Retificação consegue endereçá-los pela
gramática existente.

**Acceptance Scenarios**:

1. **Given** um Edital em elaboração com Cronograma, **When** abro a superfície de inscrição da
   composição, **Then** escolho um Evento existente como período de inscrições, numa lista dos
   Eventos daquele Cronograma.
2. **Given** o mesmo Edital, **When** declaro documentos exigidos, **Then** posso acrescentar,
   editar, remover, ordenar e indicar aplicabilidade — sem escrever condição, fórmula ou expressão.
3. **Given** esse Edital publicado, **When** leio o documento oficial, **Then** encontro os
   documentos exigidos enunciados na seção normativa de inscrição, incluindo os adicionais por
   modalidade, derivados dos dados estruturados.
4. **Given** esse Edital publicado, **When** consulto o conteúdo publicado, **Then** cada documento
   exigido tem identidade estável e o período aponta o Evento, sem duplicar datas.
5. **Given** uma Retificação sobre esse Edital, **When** endereço um documento exigido pela
   gramática existente, **Then** a alteração é aceita sem que a gramática precise mudar.
6. **Given** um Edital publicado que não aponta período de inscrições, **When** o consulto,
   **Then** ele permanece consultável e não recebe inscrições, e a publicação avisou disso sem
   impedi-la.

---

### User Story 3 - Identificar-se e continuar de onde parou (Priority: P1)

O candidato se identifica, volta exatamente para a vaga onde estava e, se já tinha começado,
continua de onde parou.

**Why this priority**: é a fronteira entre visitante e titular de uma inscrição. Sem ela não há
propriedade do rascunho, não há retomada e não há a quem atribuir o que foi enviado.

**Independent Test**: começar pela vaga, identificar-se, verificar o retorno à mesma vaga com os
dados da identidade já preenchidos; sair, voltar, e encontrar `Continuar inscrição` levando à mesma
inscrição.

**Acceptance Scenarios**:

1. **Given** que aciono `Inscrever-se nesta vaga` sem estar identificado, **When** me identifico,
   **Then** volto para aquela vaga — não para a página inicial.
2. **Given** que me identifiquei, **When** abro `Sua inscrição`, **Then** nome, CPF e e-mail vindos
   da identidade já estão lá, apresentados como informação quando não são editáveis.
3. **Given** um rascunho meu naquele Perfil, **When** volto à seleção, **Then** leio `Continuar
   inscrição` e chego à mesma inscrição, com o que eu já havia enviado.
4. **Given** que estou identificado como candidato, **When** tento abrir uma tela de gestão,
   **Then** não sou reconhecido como ator institucional.
5. **Given** um ambiente de produção, **When** o sistema sobe, **Then** ele recusa subir se o
   provedor de identidade de demonstração estiver habilitado.

---

### User Story 4 - Fazer a inscrição em uma tela (Priority: P1)

Numa única tela, o candidato confere seus dados, indica a modalidade quando houver escolha e envia
os documentos que o Edital exige dele — vendo, o tempo todo, quanto falta.

**Why this priority**: é o coração da feature e o ponto onde a desistência acontece. É também onde o
vínculo semântico entre arquivo e requisito é criado.

**Independent Test**: com um Perfil que exige três documentos, sendo um só para a modalidade
reservada, verificar que o candidato de ampla concorrência recebe dois pedidos, envia dois PDFs, vê
`2 de 2`, e que um envio recusado não apaga o que já estava válido.

**Acceptance Scenarios**:

1. **Given** um Perfil sem modalidades reservadas aplicáveis, **When** abro a inscrição, **Then**
   não me é perguntada modalidade nenhuma.
2. **Given** um Perfil com modalidade reservada, **When** escolho concorrer sem reserva, **Then**
   os documentos exclusivos daquela modalidade não me são pedidos nem exibidos.
3. **Given** a lista de documentos, **When** envio um PDF válido, **Then** ele fica gravado
   imediatamente, associado ao requisito que atende, e a contagem avança sem que eu salve nada.
4. **Given** um envio recusado por formato ou tamanho, **When** leio a recusa, **Then** os arquivos
   e campos já válidos continuam lá.
5. **Given** que fotografei um documento com o celular, **When** tento enviá-lo, **Then** a recusa
   me diz que o arquivo é imagem e que preciso convertê-lo em PDF — não apenas que é inválido.
6. **Given** um arquivo de vários megabytes em rede lenta, **When** o envio está em curso, **Then**
   vejo que está em curso e sou avisado de não fechar a página, até a confirmação.
7. **Given** um documento já enviado, **When** envio outro no mesmo requisito, **Then** fica claro
   qual arquivo passou a valer.
8. **Given** que mudo a modalidade e isso torna um documento já enviado inaplicável, **When**
   confirmo a mudança, **Then** o sistema me diz antes o que será descartado — e nada some em
   silêncio.

---

### User Story 5 - Revisar, enviar e receber protocolo (Priority: P1)

O candidato confere um resumo legível, aceita as declarações, envia e recebe um protocolo que pode
imprimir.

**Why this priority**: é o ato que produz efeito administrativo. É onde a versão normativa aceita
fica registrada e onde a duplicidade precisa ser impossível.

**Independent Test**: enviar uma inscrição completa e obter protocolo; repetir o mesmo envio e não
produzir segunda inscrição; retificar o Edital com um rascunho aberto e verificar que o envio
seguinte avisa antes de concluir.

**Acceptance Scenarios**:

1. **Given** uma inscrição completa, **When** abro a revisão, **Then** leio oportunidade, dados e
   documentos, com `Editar` em cada bloco, e voltar não apaga nada.
2. **Given** um documento obrigatório faltando, **When** tento enviar, **Then** o envio é impedido e
   eu leio exatamente o que falta.
3. **Given** a revisão, **When** aceito as duas declarações e envio, **Then** recebo protocolo
   único e legível, com Edital, Perfil, modalidade, data e hora, numa página imprimível pelo
   navegador.
4. **Given** que aciono o envio duas vezes, **When** o segundo aciona, **Then** continua existindo
   uma única inscrição enviada.
5. **Given** que uma Retificação passou a vigorar enquanto eu preenchia, **When** envio, **Then**
   sou avisado de que o Edital mudou e preciso confirmar de novo, preservados meus dados e os
   arquivos ainda aplicáveis.
6. **Given** que o período terminou enquanto eu preenchia, **When** envio, **Then** o envio é
   recusado, e ter aberto a inscrição antes do fechamento não me dá direito de enviá-la depois.
7. **Given** uma inscrição enviada, **When** tento alterá-la ou substituir um arquivo, **Then** não
   existe caminho para isso nesta versão.

---

### User Story 6 - A equipe consulta o que chegou (Priority: P1)

Quem conduz a seleção abre o Edital, vê quantas inscrições chegaram, encontra uma pessoa e abre cada
documento apresentado — dentro do sistema.

**Why this priority**: é a metade institucional do objetivo. Sem ela, o sistema recebe e a equipe
continua baixando para o Drive, que é exatamente o que a feature existe para eliminar.

**Independent Test**: com inscrições recebidas, abrir `Inscrições` no contexto do Edital, localizar
uma candidata pela lista, abrir o detalhe e visualizar cada documento no navegador, sem baixar nada
e sem tocar em banco, shell ou API manual.

**Acceptance Scenarios**:

1. **Given** inscrições recebidas, **When** abro o Edital, **Then** encontro `Inscrições` com o
   total.
2. **Given** a lista, **When** a leio, **Then** vejo protocolo, candidato, CPF mascarado, Perfil,
   modalidade, quantos documentos chegaram dos esperados e a data de envio.
3. **Given** uma inscrição, **When** abro o detalhe, **Then** cada documento aparece sob o requisito
   que atende, com o nome original do arquivo.
4. **Given** um documento, **When** o abro, **Then** ele é exibido no navegador, e baixar é ação
   secundária individual.
5. **Given** a tela administrativa, **When** a leio inteira, **Then** não existe deferimento, nota,
   parecer, classificação nem `Baixar todos`.
6. **Given** o endereço direto de um documento, **When** o acesso sem autorização, **Then** ele não
   é entregue.

---

### User Story 7 - Voltar depois (Priority: P2)

Quem já enviou volta à seleção e reencontra seu comprovante; quem não terminou reencontra sua
inscrição.

**Why this priority**: melhora real e barata, mas a jornada se completa sem ela — o comprovante já
foi exibido e é imprimível no ato do envio.

**Independent Test**: enviar uma inscrição, sair, voltar à seleção identificado, e reencontrar o
comprovante; repetir com um rascunho e reencontrar `Continuar inscrição`.

**Acceptance Scenarios**:

1. **Given** uma inscrição enviada, **When** volto à seleção identificado, **Then** leio que já me
   inscrevi e alcanço o comprovante.
2. **Given** um rascunho e o período encerrado, **When** volto, **Then** encontro o rascunho como
   consulta, sem caminho para enviá-lo.

---

### Edge Cases

- **O Edital muda no meio.** Retificação publicada durante o preenchimento: aviso antes de concluir,
  dados preservados, arquivos ainda aplicáveis preservados, descarte confirmado dos que deixaram de
  ser aplicáveis.
- **Um documento exigido deixa de existir por Retificação.** O que já foi enviado para ele não é
  cobrado nem contado como pendência.
- **O prazo termina no meio.** Rascunho aberto antes do fechamento não pode ser enviado depois.
- **Edital publicado sob versão canônica anterior.** Não é retificável — limite conhecido do
  incremento, não defeito a corrigir nesta feature.
- **Perfil único.** Não se pede escolha de Perfil.
- **Perfil sem modalidade declarada.** Não se pergunta modalidade, e nenhuma entidade de ampla
  concorrência é inventada para preencher a lacuna.
- **Imagem renomeada para `.pdf`.** Recusada pela verificação de conteúdo, com recusa instrutiva.
- **Arquivo grande em rede móvel.** Progresso visível; interrupção não corrompe o que já estava
  válido.
- **Duas abas, dois envios.** Uma inscrição enviada, sempre.
- **Duas inscrições no mesmo Perfil.** Impossível, em qualquer estado, para a mesma identidade.
- **Trocar de Perfil no meio.** Não existe: volta-se à seleção e inicia-se outra inscrição.
- **Documento de outra pessoa pelo endereço direto.** Não entregue; a titularidade é verificada a
  cada requisição.

## Requirements *(mandatory)*

### Contrato de inscrição no Edital (US2)

- **FR-001**: O Edital DEVE apontar explicitamente **um Evento já existente do seu próprio
  Cronograma** como período de inscrições. O apontamento é escolha do elaborador numa lista dos
  Eventos daquele Cronograma. *Hoje o tipo do Evento é texto livre (`editais/models/cronograma.py`),
  e é por isso que a regra é apontar, não classificar: criar taxonomia de tipos resolveria um
  problema maior do que o que existe.*
- **FR-002**: O sistema NÃO DEVE inferir o período procurando texto no Evento, nem por nome, nem por
  tipo, nem por ordem.
- **FR-003**: Início e término do período DEVEM vir do Evento apontado. Datas de inscrição NÃO DEVEM
  ser duplicadas na Inscrição nem em campo novo do Edital.
- **FR-004**: Um Edital publicado sem período apontado permanece consultável e **não recebe
  inscrições**. A ausência DEVE ser sinalizada na publicação como aviso, não como erro impeditivo —
  nem todo Edital abre inscrição por este sistema nesta versão.
- **FR-005**: `Documento Exigido` DEVE possuir exatamente: chave estável, nome, instrução curta,
  obrigatoriedade, ordem, Perfil aplicável (opcional) e modalidade aplicável (opcional). Nada além.
- **FR-006**: A aplicabilidade DEVE admitir exatamente quatro casos — todos; um Perfil; uma
  modalidade; um Perfil e uma modalidade. NÃO DEVE existir operador booleano, expressão, fórmula
  nem condição configurável.
- **FR-007**: A composição do Edital DEVE oferecer uma superfície compacta de inscrição onde o
  elaborador aponta o Evento e acrescenta, edita, remove, ordena e indica a aplicabilidade dos
  documentos exigidos. NÃO DEVE ser criada etapa nova do assistente se a capacidade couber
  coerentemente numa etapa existente; o `/plan` DEVE preferir a alteração menor.
- **FR-008**: O apontamento do período e os documentos exigidos DEVEM integrar o conteúdo publicado,
  cada documento com identidade estável. O incremento da versão canônica DEVE ocorrer **uma vez só**
  nesta feature, reunindo as duas mudanças.
- **FR-009**: A Retificação DEVE alcançar o apontamento e os documentos exigidos pela gramática de
  endereçamento existente. A gramática NÃO DEVE ser redesenhada.
- **FR-010**: O documento oficial publicado DEVE enunciar os documentos exigidos na seção normativa
  de inscrição, em linguagem corrente e derivados dos dados estruturados, incluindo os adicionais
  por modalidade. NÃO DEVE ser criada linguagem documental nova.
- **FR-011**: **Tudo o que o candidato vê e tudo o que a submissão valida DEVE derivar do conteúdo
  da versão consolidada vigente — nunca das tabelas de elaboração.** *Este é o requisito mais fácil
  de violar sem que nada quebre: ler o rascunho do Edital funciona em desenvolvimento e destrói a
  reprodutibilidade histórica que o princípio II exige de cada Inscrição.*

### Consulta pública (US1)

- **FR-012**: DEVE existir canal público em HTML, separado do administrativo, que não exija
  identidade institucional e não ofereça nenhuma capacidade de gestão.
- **FR-013**: A listagem pública DEVE apresentar, por seleção: identificação institucional, título,
  unidade, período de inscrições e situação. NÃO DEVE exibir dado administrativo interno.
- **FR-014**: O detalhe público DEVE apresentar título, resumo, Perfis, vagas por Perfil, localidade
  quando houver, requisitos, modalidades, período e o documento oficial publicado.
- **FR-015**: A situação DEVE ser exibida em três estados explícitos, com data legível: inscrições
  futuras (com a data de início), abertas (com a data e hora de término) e encerradas.
- **FR-016**: Cada Perfil DEVE oferecer o convite direto para inscrever-se naquela vaga, e a
  inscrição iniciada por ele DEVE começar com aquele Perfil escolhido. Havendo um único Perfil, o
  candidato NÃO DEVE ser levado a escolhê-lo.
- **FR-017**: A página DEVE continuar consultável após o encerramento.
- **FR-018**: Perfil, vagas, modalidades e período NÃO DEVEM ser duplicados em modelo próprio da
  inscrição; a fonte é a publicação vigente (FR-011).
- **FR-019**: O período DEVE ser verificado ao iniciar a inscrição e novamente ao enviá-la, no
  servidor. Conhecer o endereço NÃO DEVE permitir iniciar nem enviar fora do período.

### Identidade do candidato (US3)

- **FR-020**: A identidade do candidato DEVE ser eixo próprio, distinto do ator institucional. NÃO
  DEVE ser criado papel de candidato no mapa de papéis institucionais, e o candidato NÃO DEVE
  receber nenhuma permissão institucional.
- **FR-021**: A sessão do candidato DEVE usar chave distinta da institucional. Estar identificado
  num eixo NÃO DEVE identificar no outro, em nenhuma direção.
- **FR-022**: A Inscrição DEVE referenciar a identidade por um identificador estável do provedor.
  A propriedade da inscrição NÃO DEVE depender do nome digitado nem de qualquer dado editável.
- **FR-023**: Enquanto não houver provedor institucional real, DEVE existir provedor de demonstração
  explicitamente rotulado como tal na interface, impossível de confundir com autenticação de
  produção.
- **FR-024**: A subida em produção DEVE ser recusada se o provedor de demonstração estiver
  habilitado, no mesmo padrão de guarda já aplicado ao seletor de identidade institucional
  (`config/settings/production.py`).
- **FR-025**: Concluída a identificação, o candidato DEVE retornar exatamente ao ponto de onde saiu
  — a vaga ou a inscrição —, nunca à página inicial.
- **FR-026**: Trocar o provedor de demonstração pelo real NÃO DEVE alterar a semântica da Inscrição.
  Isso NÃO autoriza construir arcabouço genérico de identidade.

### Rascunho, unicidade e estados (US3)

- **FR-027**: A Inscrição DEVE possuir exatamente dois estados: `RASCUNHO` e `SUBMETIDA`. Uma
  Inscrição enviada NÃO DEVE retornar a rascunho. NÃO DEVE ser criada máquina de estados genérica.
- **FR-028**: DEVE existir no máximo **uma Inscrição por identidade, Edital e Perfil, em qualquer
  estado**, garantida por invariante persistente. *Uma regra e uma restrição para os dois casos:
  rascunho duplicado e envio duplicado são a mesma violação.*
- **FR-029**: Reabrir o mesmo Perfil DEVE levar à inscrição existente, anunciada como `Continuar
  inscrição`.
- **FR-030**: O Perfil NÃO DEVE ser alterado dentro de uma inscrição. Concorrer a outro Perfil é
  iniciar outra inscrição a partir da seleção. *Isso elimina, por desenho, a reconciliação de
  documentos por troca de Perfil.*
- **FR-031**: Alterar a modalidade de forma que documentos já enviados deixem de ser aplicáveis DEVE
  exigir confirmação que enumere o que será descartado. Nada DEVE ser descartado nem reaproveitado
  em silêncio. NÃO DEVE ser criado mecanismo de reconciliação.
- **FR-032**: Encerrado o período, um rascunho NÃO DEVE poder ser enviado, e DEVE permanecer
  acessível ao próprio titular apenas para consulta.
- **FR-033**: A Inscrição DEVE possuir estado e revisão próprios, de modo a integrar os mecanismos
  existentes de concorrência e de auditoria sem que nenhum deles precise ser alterado.

### A tela da inscrição (US4)

- **FR-034**: Depois de identificado, o candidato NÃO DEVE atravessar mais de **duas telas** antes
  da confirmação: a inscrição e a revisão.
- **FR-035**: A tela da inscrição DEVE manter visível, o tempo todo, para qual Edital e Perfil a
  inscrição é, e o que ainda falta para poder ser enviada.
- **FR-036**: Os dados pessoais coletados nesta versão DEVEM ser exatamente: nome, CPF, e-mail e
  telefone (opcional). NÃO DEVEM ser coletados endereço, filiação, estado civil ou equivalentes,
  salvo se um Processo real escolhido para piloto demonstrar obrigatoriedade.
- **FR-037**: Dado fornecido pela identidade autenticada NÃO DEVE ser redigitado. Quando não for
  editável, DEVE ser apresentado como informação legível — nunca como campo desabilitado sem
  explicação.
- **FR-038**: O bloco de concorrência só DEVE aparecer quando houver escolha relevante. Não havendo
  modalidade aplicável, nada DEVE ser perguntado.
- **FR-039**: A ausência de reserva PODE ser apresentada como *ampla concorrência / sem reserva* sem
  exigir que exista entidade persistida correspondente. Havendo no conteúdo publicado modalidade
  equivalente já declarada, ela DEVE ser usada, e nenhuma outra criada.
- **FR-040**: Só DEVEM ser solicitados e exibidos os documentos aplicáveis à combinação de Perfil e
  modalidade daquela inscrição.
- **FR-041**: O candidato NÃO DEVE precisar acionar `Salvar`. Cada arquivo válido DEVE persistir no
  momento do envio, em requisição própria; os campos DEVEM ser gravados na passagem para a revisão.
  NÃO DEVE ser construído mecanismo de gravação automática contínua.
- **FR-042**: Nenhum dado pessoal do candidato DEVE ser persistido no navegador. *O rascunho local
  do assistente existe para quem elabora e caduca em 24 h precisamente porque a máquina de um órgão
  público é compartilhada (`interface/static/interface/rascunho.js`); com CPF e documentos o risco
  não se compensa em nenhum prazo.*

### Documentos, envio e armazenamento (US4)

- **FR-043**: Cada `Documento Exigido` DEVE aceitar **um** arquivo por inscrição, com unicidade
  garantida por invariante persistente sobre Inscrição e Documento Exigido. Exigências compostas
  são resolvidas declarando um requisito que descreve o conteúdo esperado, não agrupando arquivos.
- **FR-044**: Um arquivo submetido DEVE pertencer a uma Inscrição e corresponder a um Documento
  Exigido **aplicável àquela inscrição**. Arquivo para requisito de outro Perfil ou de outra
  modalidade NÃO DEVE ser aceito.
- **FR-045**: Somente PDF DEVE ser aceito, verificado por extensão **e** pelo conteúdo do arquivo,
  não apenas pelo nome. A verificação de conteúdo DEVE ser a mínima suficiente. NÃO DEVE haver OCR,
  conversão, compactação nem validação semântica do documento.
- **FR-046**: O limite DEVE ser de 10 MB por arquivo, definido como configuração da aplicação. NÃO
  DEVE ser configurável por documento exigido.
- **FR-047**: A recusa de um arquivo DEVE ensinar o caminho. Um arquivo de imagem — o que um celular
  produz ao fotografar um documento — DEVE receber recusa que diga que é imagem e que é preciso
  convertê-la em PDF, e não apenas que o arquivo é inválido.
- **FR-048**: Durante o envio de um arquivo o candidato DEVE ver que o envio está em curso e ser
  avisado de não fechar a página, até a confirmação. *Dez megabytes em rede móvel levam dezenas de
  segundos, e é nesse silêncio que a pessoa reenvia ou desiste.*
- **FR-049**: A recusa de um envio NÃO DEVE apagar arquivos já aceitos nem campos já preenchidos.
- **FR-050**: O candidato DEVE poder substituir um arquivo antes do envio da inscrição, e a
  interface DEVE deixar claro qual arquivo passou a valer.
- **FR-051**: Arquivos de candidatos NÃO DEVEM possuir endereço público direto nem previsível, NÃO
  DEVEM residir na árvore de arquivos estáticos e NÃO DEVEM ser entregues diretamente pelo servidor
  web. Todo acesso DEVE ser mediado pela aplicação.
- **FR-052**: O nome físico do arquivo NÃO DEVE ser o nome enviado pelo candidato; o nome original
  DEVE ser preservado apenas como metadado exibível.
- **FR-053**: O registro do documento submetido DEVE conter Inscrição, Documento Exigido, referência
  de armazenamento, nome original, tamanho, instante do envio e o resumo criptográfico do conteúdo.
  *A finalidade do resumo é integridade: permitir afirmar depois que o arquivo consultado é o mesmo
  que foi recebido, inclusive quando houve substituição antes do envio.*
- **FR-053a**: O resumo DEVE ser **verificado, não apenas guardado**: ao entregar o arquivo na
  consulta administrativa, o sistema DEVE recalculá-lo sobre o conteúdo armazenado e compará-lo com
  o registrado; divergindo, o arquivo NÃO DEVE ser entregue como íntegro e o fato DEVE ser
  registrado. *Guardar um resumo que nunca se compara não demonstra integridade nenhuma.* NÃO DEVE
  ser criada varredura periódica sobre todo o acervo nesta versão.
- **FR-054**: Enviada a inscrição, ela e seus arquivos DEVEM ser imutáveis nesta versão, no mesmo
  padrão dos demais registros normativos do sistema. O candidato NÃO DEVE poder substituir, excluir,
  alterar nem cancelar.

### Revisão, declarações e envio (US5)

- **FR-055**: A revisão DEVE apresentar oportunidade, dados pessoais, documentos e o estado de cada
  requisito, com retorno para correção em cada bloco. Voltar NÃO DEVE apagar informação.
- **FR-056**: Requisito obrigatório sem documento DEVE impedir o envio, indicando o que falta.
- **FR-057**: As duas declarações — veracidade das informações e ciência do Edital e atos vigentes —
  DEVEM ser obrigatórias, pedidas **uma vez só**, no envio, e o aceite DEVE ser registrado no ato.
  NÃO DEVE ser criado gestor configurável de termos.
- **FR-058**: A Inscrição DEVE registrar a versão consolidada do Edital vigente no ato do envio, e o
  servidor DEVE revalidá-la no momento de enviar.
- **FR-059**: Havendo Retificação vigente desde o início do preenchimento, o envio NÃO DEVE ocorrer
  em silêncio: o candidato DEVE ser avisado e confirmar novamente, preservados seus dados e os
  arquivos ainda aplicáveis, com descarte confirmado dos que deixaram de ser (FR-031). NÃO DEVE ser
  implementada comparação textual de versões.
- **FR-059a**: O rascunho DEVE registrar **qual versão consolidada o candidato reconheceu**,
  atualizada a cada confirmação. O aviso de FR-059 DEVE ser disparado quando a versão vigente
  diferir da reconhecida, e a confirmação vale até que outra versão passe a vigorar — o candidato
  NÃO DEVE ser avisado repetidamente da mesma alteração. Essa versão reconhecida NÃO DEVE ser
  confundida com a registrada no envio (FR-058): uma é o que o candidato viu enquanto preenchia, a
  outra é aquela sob a qual ele se inscreveu.
- **FR-060**: No envio o servidor DEVE revalidar integralmente: período, Edital publicamente válido,
  versão, Perfil, modalidade, aplicabilidade dos documentos, presença dos obrigatórios, formato e
  tamanho dos arquivos, unicidade e declarações. NÃO DEVE confiar no que a tela anterior validou.
- **FR-061**: O envio DEVE ser idempotente, apoiado no mecanismo de idempotência já existente e na
  invariante persistente de FR-028. A proteção NÃO DEVE depender de comportamento do navegador.
- **FR-062**: A inscrição enviada DEVE receber protocolo único, legível e opaco, com unicidade
  garantida no armazenamento. NÃO DEVE haver sequência numérica global. O ano que compõe o protocolo
  é o do envio.
- **FR-063**: A conclusão DEVE exibir protocolo, Edital, Perfil, modalidade, data e hora e o nome do
  candidato, numa página imprimível pelo navegador. NÃO DEVE ser gerado PDF de comprovante.
- **FR-064**: O instante do envio DEVE ser imutável.
- **FR-065**: De volta à seleção, o candidato identificado DEVE encontrar `Continuar inscrição`
  quando houver rascunho e o comprovante quando já tiver enviado. NÃO DEVE ser construído portal do
  candidato.

### Consulta administrativa (US6)

- **FR-066**: O contexto administrativo do Edital DEVE oferecer `Inscrições`, com o total recebido.
- **FR-067**: A lista DEVE apresentar protocolo, candidato, CPF mascarado, Perfil, modalidade,
  situação, quantos documentos foram recebidos dos esperados e a data de envio.
- **FR-068**: O detalhe DEVE apresentar os dados da inscrição, Perfil, modalidade, versão do Edital
  aceita e os documentos **sob o requisito que cada um atende**, com o nome original do arquivo.
- **FR-069**: Cada documento DEVE poder ser aberto pela interface, exibido no navegador quando o
  formato permitir; baixar DEVE existir apenas como ação secundária individual. NÃO DEVE existir
  download em lote, exportação, planilha nem painel.
- **FR-070**: A tela administrativa NÃO DEVE apresentar deferimento, indeferimento, nota, parecer,
  checklist de banca, homologação de inscrição nem classificação.

### Acesso, proteção de dados e auditoria

- **FR-071**: O acesso do candidato à sua inscrição e aos seus documentos DEVE ser decidido por
  **titularidade da identidade**, verificada no servidor a cada requisição. Conhecer o identificador
  NÃO DEVE autorizar. *A verificação de permissão existente decide o que um ator pode fazer, não de
  quem é o registro; titularidade é eixo novo e precisa ser escrita, não herdada.*
- **FR-072**: O acesso administrativo à inscrição e aos documentos DEVE exigir permissão e escopo
  institucional do Processo, negando por padrão.
- **FR-073**: O CPF NÃO DEVE aparecer em endereço de página, DEVE ser exibido mascarado em
  listagens e DEVE ser armazenado também em forma normalizada, para comparação. A máscara é
  **`***.456.789-**`** — ocultos os três primeiros dígitos e os dois verificadores, visíveis os seis
  do meio. *Fixar o formato é decisão de produto: sem ele, implementação e teste concordam entre si
  sem que ninguém tenha decidido quanto do documento aparece na tela de quem consulta.*
- **FR-074**: Registros de diagnóstico e de auditoria NÃO DEVEM conter CPF completo, conteúdo de
  documento nem dado pessoal desnecessário à investigação.
- **FR-075**: A entrega de um arquivo de candidato DEVE usar cabeçalhos próprios de conteúdo
  privado, sem armazenamento em cache compartilhado.
- **FR-075a**: Toda resposta que contenha dado pessoal do candidato — a tela da inscrição, a
  revisão, o comprovante, a lista e o detalhe administrativos, além do próprio arquivo — DEVE
  instruir o navegador a não armazená-la. *FR-042 impede a persistência que a aplicação escreveria;
  esta impede a que o navegador escreve sozinho. Num computador compartilhado as duas produzem
  exatamente o mesmo vazamento.*
- **FR-076**: A coleta DEVE limitar-se ao declarado em FR-036 e aos documentos que o Edital exige,
  sob a finalidade de processar a inscrição. Política de retenção e descarte é precondição de
  implantação declarada; NÃO DEVE ser implementada rotina automática de expurgo nesta feature.
- **FR-077**: DEVEM ser auditados a criação da Inscrição, o envio e a substituição ou remoção de
  arquivo antes do envio. NÃO DEVE ser auditada a consulta pública.
- **FR-078**: O registro de auditoria de ato praticado pelo candidato DEVE ter como autor a
  identidade externa e como escopo o escopo institucional do Processo alvo, e DEVE permitir
  responder qual Inscrição, qual Edital e versão, qual Perfil e em que instante. NÃO DEVE ser
  concedida permissão institucional ao candidato para viabilizar o registro, e o registro NÃO DEVE
  duplicar CPF completo nem conteúdo de documento.

### Experiência, transversal a todas as histórias

- **FR-079**: Todo o fluxo do candidato DEVE ser utilizável em tela de 375 px de largura, sem
  rolagem horizontal. *A folha de estilo atual do produto não tem nenhuma regra responsiva; herdar
  os tokens visuais é decisão do `/plan`, mas a ausência de rolagem é requisito, não consequência.*
- **FR-080**: Todo o fluxo principal DEVE ser realizável por teclado e herdar o padrão de
  acessibilidade já vigente na interface administrativa: link de pular para o conteúdo, foco
  visível, contraste conforme WCAG 2.1 AA, rótulo associado a cada campo, erro associado ao campo
  que o originou e estado que não dependa apenas de cor.
- **FR-081**: Cada tela DEVE ter uma ação principal inequívoca — `Inscrever-se`, `Revisar
  inscrição`, `Enviar inscrição` —, sem chamadas concorrentes disputando a mesma decisão.
- **FR-082**: Nenhuma recusa de validação DEVE exigir repetir campo ou arquivo já válido.

### Key Entities

- **Período de Inscrições**: não é entidade nova. É o apontamento, feito pelo Edital, para um Evento
  já existente do seu Cronograma, que passa a integrar o conteúdo publicado.
- **Documento Exigido**: o que o Edital exige que o candidato apresente. Chave estável, nome,
  instrução, obrigatoriedade, ordem e aplicabilidade por Perfil e/ou modalidade. Nasce na elaboração
  e vive no conteúdo publicado, que é a fonte para o candidato.
- **Identidade do Candidato**: pessoa externa autenticada por provedor, referenciada por
  identificador estável. Não é ator institucional, não tem papel nem permissão.
- **Inscrição**: o vínculo entre uma identidade e um Perfil de um Edital, em estado `RASCUNHO` ou
  `SUBMETIDA`. Guarda os dados pessoais mínimos, a modalidade escolhida quando houver, a versão
  consolidada reconhecida durante o preenchimento, a versão aceita no envio, o instante do envio e
  o protocolo. Única por identidade, Edital e Perfil.
- **Documento Submetido**: o arquivo que o candidato apresentou **para um Documento Exigido
  específico** da sua Inscrição. Guarda referência de armazenamento, nome original, tamanho, resumo
  criptográfico e instante. Um por requisito.
- **Protocolo**: identificação legível e opaca da inscrição enviada, única, entregue ao candidato.

## Success Criteria *(mandatory)*

### Resultados funcionais

- **SC-001**: Uma pessoa sem identificação consulta a seleção publicada, seus Perfis e o documento
  oficial, sem passar por nenhuma tela de gestão.
- **SC-002**: A situação das inscrições — futura, aberta ou encerrada, com a data correspondente —
  é derivada do Evento apontado no Edital, e nenhuma tela obtém essa informação lendo texto.
- **SC-003**: Quem chega pelo convite de um Perfil não escolhe Perfil nenhum; quem chega a um Edital
  de Perfil único também não.
- **SC-004**: Nenhuma informação fornecida pela identidade autenticada é solicitada de novo.
- **SC-005**: Um candidato sem reserva não vê, em nenhuma tela, campo ou documento exclusivo de
  modalidade reservada.
- **SC-006**: Num Edital que exige um documento de todos, um do Perfil e um da modalidade reservada,
  o candidato da modalidade recebe exatamente três pedidos e o de ampla concorrência exatamente
  dois.
- **SC-007**: Um envio recusado — por formato, por tamanho ou por ser imagem — não apaga nenhum
  arquivo nem campo já válido, e a recusa de imagem diz ao candidato o que fazer.
- **SC-008**: Quem sai e volta encontra a mesma inscrição, com os arquivos válidos preservados, sem
  reenviar nada e sem ter salvo nada.
- **SC-009**: Toda inscrição enviada registra a versão consolidada aceita; e uma Retificação vigente
  durante o preenchimento produz aviso e nova confirmação, nunca envio silencioso.
- **SC-009a**: Quem foi avisado de uma Retificação e confirmou não volta a ser avisado da mesma
  alteração; passa a ser avisado de novo quando outra versão entra em vigor.
- **SC-010**: Acionar o envio mais de uma vez produz uma única inscrição enviada, e a mesma
  identidade não consegue ter duas inscrições no mesmo Perfil do mesmo Edital em nenhum estado.
- **SC-011**: Faltando documento obrigatório, o envio é recusado e o candidato lê exatamente o que
  falta.
- **SC-012**: A inscrição enviada produz protocolo único e legível e um comprovante imprimível pelo
  navegador.
- **SC-013**: Quem conduz a seleção encontra uma inscrição específica pela interface administrativa,
  sem exportar nada.
- **SC-014**: Cada documento apresentado abre no navegador **sob o requisito que atende**, com o
  nome original do arquivo visível.
- **SC-014a**: Ao abrir um documento apresentado é possível afirmar que o arquivo exibido é
  exatamente o que foi recebido, e uma divergência impede a entrega como íntegro.
- **SC-015**: Nenhum documento é entregue a quem conhece apenas seu endereço, nem a outro candidato,
  nem a ator sem permissão no Processo.
- **SC-016**: Verificar que os documentos de uma seleção chegaram corretamente não exige Drive,
  planilha, download em lote, banco, shell nem API manual.
- **SC-017**: **Critério emblemático.** Com dois atores e apenas o navegador: o gestor publica um
  Edital com um Perfil, uma modalidade reservada, período de inscrições e três documentos exigidos
  com aplicabilidades distintas; o candidato chega pela vaga, identifica-se, volta à mesma vaga,
  encontra seus dados preenchidos, recebe exatamente os documentos que lhe cabem, envia os PDFs,
  revisa, envia a inscrição e recebe o protocolo; o gestor abre `Inscrições`, encontra a pessoa e
  visualiza cada documento sob o requisito que ele atende.

### Resultados de experiência

- **SC-UX-001**: Na inscrição de referência — candidato identificado, Perfil com dois documentos
  obrigatórios, arquivos prontos — o caminho até o protocolo custa no máximo: **duas telas**, **zero
  campos redigitados** que a identidade já forneceu, **um** campo próprio a preencher quando o
  telefone for informado, **dois** envios de arquivo e **três** acionamentos de ação principal. *O
  alvo de produto é concluir em menos de cinco minutos, excluída a rede; ele é aferido uma vez, na
  demonstração da entrega final, e registrado no roteiro da feature — os limites acima são o que se
  verifica a cada mudança.*
- **SC-UX-002**: Entre a identificação e a confirmação não existe mais de uma tela além da revisão.
- **SC-UX-003**: A tela da inscrição informa, sem rolagem adicional, para qual Edital e Perfil a
  inscrição é e quantos documentos faltam.
- **SC-UX-004**: Todo o fluxo do candidato é operável em 375 px de largura sem rolagem horizontal.
- **SC-UX-005**: Todo o fluxo principal do candidato é percorrível por teclado, com leitor de tela,
  alcançando a obrigatoriedade de cada campo, o motivo de cada recusa e a confirmação de descarte —
  sem depender de cor para distinguir estado.
- **SC-UX-006**: Durante o envio de um arquivo grande o candidato vê o progresso e o aviso de não
  fechar a página, e uma interrupção não invalida o que já estava enviado.
- **SC-UX-007**: Nenhuma recusa de validação obriga a repetir campo ou arquivo já válido, em nenhum
  ponto do fluxo.
- **SC-UX-008**: Nenhuma tela do candidato apresenta duas chamadas de ação disputando a mesma
  decisão.

## Assumptions

- A interface permanece renderizada no servidor, com fragmentos, como o restante do produto;
  nenhuma dependência nova de frontend é introduzida por esta feature.
- O canal público reaproveita a identidade visual do produto. Se os tokens visuais serão extraídos
  para compartilhamento ou deliberadamente duplicados é decisão do `/plan`; a folha atual não tem
  regra responsiva, então o comportamento em 375 px é trabalho novo em qualquer das duas hipóteses.
- O incremento de `SCHEMA_VERSION` invalida os dados de demonstração publicados, que são recriados
  pela seed, e torna não retificáveis os Editais publicados sob a versão anterior. É limite
  conhecido e aceito, no mesmo termo já registrado pela `007`.
- O incremento da versão canônica desta feature é o único entre a 008 e a 009: o plano da 008
  declara que ela não toca a camada canônica. A relação entre as duas é de conflito textual no
  compositor do documento, e está tratada na precondição 2.
- O provedor de identidade de demonstração basta para toda a feature; a integração real é jornada
  posterior e não altera nenhum requisito acima.
- Papéis e permissões institucionais existentes bastam para a consulta administrativa; nenhum papel
  novo é criado.
- O volume esperado por seleção é de centenas a poucos milhares de inscrições, com um punhado de
  arquivos cada. Nada nesta spec pressupõe escala além disso.
- O primeiro Processo real escolhido para piloto pode revelar campo pessoal obrigatório que esta
  versão não coleta; a revisão desse ponto é explícita e não automática.

## Out of Scope

Desta feature inteira, e sem exceção:

- **Avaliação**: comissão, banca, distribuição de candidatos, deferimento e indeferimento,
  pontuação, checklist, parecer, notas, divergência entre avaliadores, recursos, classificação,
  resultado e convocação.
- **Documentos**: OCR, extração automática, validação semântica, conferência de diploma, antivírus
  corporativo, assinatura eletrônica, reconhecimento facial, conversão, compactação e versões
  posteriores ao envio.
- **Comunicação**: e-mail, SMS, aplicativos de mensagem e notificação por push.
- **Identidade**: integração real com provedor governamental, cadastro local completo, recuperação
  de conta, segundo fator e diretório próprio de candidatos.
- **Administração**: exportação, planilha, painel, relatório, filtro avançado, download em lote e
  portal completo do candidato.
- **Edital**: anexos do Edital, construtor de formulários, campos arbitrários, condição
  configurável, taxonomia de Eventos e nova engine normativa.
- **Arquitetura**: motor genérico de fluxo, plataforma genérica de upload, motor genérico de
  formulários, event sourcing, microsserviços e armazenamento em nuvem introduzido sem necessidade
  concreta.
- **Ciclo de vida da inscrição**: cancelamento, retificação e substituição de documento pelo
  candidato após o envio; rotina automática de retenção e descarte.

> **Uma necessidade futura da comissão não autoriza implementá-la na 009**, e nada nesta lista gera
> automaticamente a prioridade da feature seguinte.

## Ordem de entrega

Cada linha é uma entrega demonstrável no navegador. A condição de merge é a demonstração, não a
contagem de testes.

| Entrega | O que se abre no navegador | Toca a camada canônica? |
|---|---|---|
| 1 | Canal público: listagem e detalhe da seleção, Perfis, vagas e documento oficial, derivados da versão vigente — **sem situação temporal e sem convite por vaga** (US1, parte consultável) | Não |
| 2 | Contrato de inscrição: Evento apontado e documentos exigidos, na composição, no conteúdo publicado e no documento — **e a US1 se completa**: a página passa a dizer futura, aberta ou encerrada, com data, e a oferecer a vaga | Sim, uma vez |
| 3 | Identidade do candidato, retorno ao ponto de origem e a tela `Sua inscrição` com dados e modalidade, retomável | Não |
| 4 | Envio de documentos com armazenamento privado, progresso, substituição e contagem do que falta | Não |
| 5 | Revisão, declarações, envio, protocolo e comprovante imprimível | Não |
| 6 | `Inscrições` no contexto do Edital e cada documento aberto sob o seu requisito | Não |

A entrega 1 não toca a camada canônica nem o compositor do documento, e pode começar imediatamente,
com a 008 ainda em curso. A entrega 2 é a única que incrementa a versão canônica e a única que
escreve no compositor — é ela, e só ela, que observa a barreira da precondição 2. A ordem de
execução é esta; a ordem de dependência começa na 2, e é por isso que a entrega 1 é explicitamente
uma fatia da US1, não a US1 inteira.

## Instruções para o `/plan`

**Objetivo: chegar à implementação pelo menor caminho.** Não introduzir repositório, serviço, DTO,
objeto de valor, comando ou interface adicional se a capacidade puder ser implementada de forma
coerente com a arquitetura existente. Não refatorar o que os cenários acima não exijam. Não
generalizar mecanismo introduzido para um caso único. Havendo solução simples que atende
integralmente e outra mais genérica, usar a simples. Preferir migração direta e regeneração de seed
a mecanismo de compatibilidade.

Seis avisos específicos, derivados do que esta spec verificou no repositório:

1. **Reutilizar, nominalmente, quatro mecanismos que já existem**: a idempotência de comando para o
   envio; a auditoria, que lê estado e revisão do agregado — daí FR-033; o padrão de imutabilidade
   por `save()` que recusa atualização, para a inscrição enviada e seus arquivos; e o padrão de
   guarda de configuração de produção, para FR-024 e para a raiz privada de armazenamento. Nenhum
   deles precisa ser alterado para servir ao candidato.
2. **Armazenamento é decisão desta feature, não herança.** Não existe armazenamento de arquivo no
   projeto; o único binário persistido hoje é o documento publicado, em coluna binária, e ele é um
   caso diferente — imutável, único por publicação, pequeno. Para documentos de candidato, o
   caminho previsto é o mecanismo de arquivos do próprio framework com raiz privada, fora da árvore
   estática e não servida pelo servidor web. Não introduzir armazenamento em nuvem nesta feature.
3. **Titularidade não é permissão.** A verificação de permissão existente decide o que um ator pode
   fazer e em que escopo; ela não sabe de quem é um registro. FR-071 é regra nova e precisa ser
   escrita e testada como tal. Representar o candidato como ator institucional com conjunto vazio de
   permissões pode ser conveniente para reaproveitar idempotência e auditoria — mas não substitui a
   verificação de titularidade, e não pode abrir caminho para comando administrativo.
4. **A fonte do que se pede ao candidato é o conteúdo publicado.** FR-011 é o requisito mais fácil
   de violar sem quebrar nada: ler as tabelas de elaboração funciona em desenvolvimento e destrói a
   reprodutibilidade histórica. Se a implementação da tela da inscrição consultar Perfil, modalidade
   ou documento exigido fora do conteúdo consolidado vigente, o requisito foi lido errado.
5. **Um incremento canônico, uma entrega.** O apontamento do período e os documentos exigidos viajam
   juntos. A 008 não incrementa a versão canônica — seu plano é explícito quanto a isso —, então
   este é o único incremento das duas features. A barreira que resta é o compositor do documento,
   onde as duas escrevem: a entrega 2 parte da 008 já integrada.
6. **A experiência é requisito.** FR-079 a FR-082 e os `SC-UX` não são acabamento e não são
   negociáveis contra prazo dentro desta feature. Em particular, o progresso de envio (FR-048) e a
   recusa instrutiva (FR-047) existem porque é ali que a inscrição é abandonada.

Nenhuma questão de desenho permanece aberta. A dúvida sobre coordenar o incremento canônico com a
008 foi respondida pelos artefatos dela: a 008 não toca a camada canônica, e a relação entre as duas
features é a do compositor compartilhado, tratada na precondição 2 e no aviso 5 acima.
