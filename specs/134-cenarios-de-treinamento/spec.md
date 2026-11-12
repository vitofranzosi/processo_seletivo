# Feature Specification: Cenários de treinamento e homologação

**Feature Branch**: `claude/gps-training-staging-scenarios-bc947c`, sobre a `main` em `86cd0ee0`

**Created**: 2026-11-08

**Status**: Implementada em 08/11/2026. Revista em 12/11/2026 pelo provisionamento de treinamento
da formalização (FR-4615, FR-6720 a FR-6729), sem merge. Uma migration (`treinamento/0001`), um app
novo, quatro comandos de gestão e nenhuma tela. Verificação em [verificacao.md](verificacao.md).
Nenhuma carga foi feita no banco compartilhado de homologação: ela é do administrador, pelo
[manual de operação](../../doc/cenarios-de-treinamento/manual-de-operacao.md).

**Input**: o pedido do usuário de 08/11/2026, *"GPS — Implementação de cenários de treinamento e
homologação de processos seletivos"*. O diagnóstico do que existia está no [plano](plan.md); o
catálogo, com o roteiro de cada exercício, no
[guia da equipe](../../doc/cenarios-de-treinamento/guia-da-equipe.md).

> **Faixa de identificadores.** Esta spec abre em **FR-4601** e **SC-1451**. O teto medido em
> 08/11/2026 em `specs/` desta worktree foi o requisito funcional quatro mil quinhentos e cinquenta
> e nove e o critério mil quatrocentos e vinte e oito; a folga é a de costume. As decisões começam
> em `D-001`.

---

## Por que esta feature existe

Para exercitar o sorteio, a equipe precisava criar o Edital, compor, publicar, inscrever, esperar o
fim das inscrições, congelar e esperar a extração da Loteria. Cada etapa avançada do certame só se
alcança percorrendo todas as anteriores, e a homologação já tem dados que a equipe criou à mão e
que não podem ser tocados.

Esta feature entrega um **gerador de cenários**: comandos de gestão que acrescentam ao banco
Editais fictícios já parados em etapas diferentes, prontos para a próxima ação, pelos mesmos
comandos da aplicação que a tela usa.

## Requisitos funcionais

### Ambiente e autorização da operação

- **FR-4601**: Os comandos recusam executar quando `AMBIENTE_DE_PRODUCAO` é verdadeiro, quando
  `DJANGO_SETTINGS_MODULE` aponta para as configurações de produção, ou quando a chave
  `CENARIOS_DE_TREINAMENTO` não está ligada. `production.py` recusa subir com a chave ligada.
- **FR-4602**: Os comandos que gravam exigem o nome do banco de destino por extenso (`--banco`),
  igual ao banco conectado; divergindo ou faltando, nada é gravado.
- **FR-4603**: Nada roda sozinho: nem migration, nem inicialização, nem atualização da aplicação
  criam cenários. A migration da feature só cria a tabela do manifesto.
- **FR-4604**: A carga e a restauração têm pré-visualização (`--dry-run`) que diz o banco, o
  servidor, a configuração, a chave, e o que seria criado, mantido ou recusado, sem gravar nada.
- **FR-4605**: Toda recusa nomeia o motivo e o que fazer, e acontece antes de qualquer escrita.

### Manifesto, propriedade e idempotência

- **FR-4610**: Cada rodada de cenário criada tem uma linha de manifesto com a unidade, o código do
  cenário, a rodada, a versão da receita, o Processo, a correlação, os identificadores de tudo o
  que criou, o retrato do estado inicial, o banco e o instante.
- **FR-4611**: A carga cria só os cenários sem rodada em uso; os que existem são mantidos sem
  nenhuma escrita, nem de trilha.
- **FR-4612**: Cada cenário é criado numa transação, junto com o manifesto: ou nasce inteiro, ou
  não deixa nada. A falha de um cenário não impede os outros. A recusa do domínio sai como
  `FALHOU`, com a frase dela; o defeito do gerador, como `ERRO`, com a pilha na saída de erros.
- **FR-4613**: A propriedade de um Processo pelo gerador se comprova pelo manifesto **e** pela
  trilha (o registro de criação com a correlação da rodada), e não pelo prefixo do código.
- **FR-4614**: Um Processo com o código reservado de um cenário e sem manifesto é relatado como
  conflito e não é reaproveitado, alterado nem restaurado.
- **FR-4615** *(revista em 2026-11-12, por decisão do usuário sobre o achado 06 da reavaliação da
  jornada final — a redação anterior está ao fim desta alínea)*: O gerador não cria nem altera
  configuração institucional: unidade, autoridade ou papel. Não altera usuário nem vínculo que
  existam, e não concede vínculo de papel de condução nem de acesso administrativo. **A única
  exceção** é o provisionamento de treinamento da formalização, das FR-6720 a FR-6729: uma
  identidade fictícia `treino.formalizacao`, o vínculo dela no papel Formalização na unidade do
  cenário, e a designação dela para o Edital do cenário de exportar.

  > **Redação anterior, preservada:** O gerador não cria nem altera configuração institucional:
  > unidade, autoridade, papel, vínculo ou usuário.
  >
  > *Por que mudou:* o fim da jornada não podia ser treinado pela interface (achado 06 da
  > reavaliação da jornada final de 12/11/2026). O papel Formalização do seletor vale só para a
  > sessão e não é vínculo, e por isso o Centro dizia "ninguém designado" com o setor exportando — a
  > designação efetiva da FR-6107 da `153` exige o papel vigente na unidade. Decisão do usuário, em
  > 12/11/2026: *"O cenário destinado a exercitar a formalização deve nascer com pessoa fictícia
  > identificável, vínculo vigente no papel Formalização e designação válida para o Edital."* E a
  > forma: *"permitir o provisionamento controlado das identidades e vínculos fictícios necessários,
  > com as proteções de ambiente, isolamento e idempotência existentes. O exercício de exportar já
  > pode vir pronto; um exercício específico de designar pode partir apenas da pessoa habilitada."*
- **FR-4616**: Sem pedido expresso (`--autoridade`), o gerador só assina com autoridade vigente que
  já foi usada, porque o primeiro uso torna o cadastro dela imutável (a FR-1121 da `060`).
- **FR-4617**: A verificação diz, por cenário: ausente, intacto, exercitado (com as diferenças em
  relação ao retrato inicial), inconsistente ou em conflito; e se o prazo do estado inicial venceu
  ou se a receita mudou de versão.

### Restauração

- **FR-4620**: A restauração é de um cenário por vez e exige `--confirmar` com o código dele.
- **FR-4621**: Restaurar não exclui nada: cria a rodada seguinte do cenário no estado inicial e
  cancela a rodada anterior pelos comandos de cancelamento de Edital e de Processo, com motivo.
- **FR-4622**: A restauração é recusada quando a propriedade não se comprova (FR-4613), quando não
  há rodada em uso, ou quando a rodada nova encontraria conflito.
- **FR-4623**: Antes de restaurar, o comando mostra o que muda: a rodada nova, os Editais e o
  Processo a cancelar, e o que a equipe fez no cenário desde a criação.
- **FR-4624**: A rodada nova, o cancelamento da anterior e a troca no manifesto são uma transação.
  Os Editais a cancelar são relidos sob trava dentro dela, e a rodada anterior precisa continuar
  em uso; se outra restauração passou na frente, nada é alterado.
- **FR-4625**: A restauração não altera outro cenário, Edital real, pessoa, unidade ou autoridade.
- **FR-4626**: A rodada anterior continua consultável, com o histórico do exercício, na aba
  "Cancelados".

### Dados fictícios e efeitos externos

- **FR-4630**: Os identificadores de Perfil, Etapa, marco, Evento, Modalidade e Documento são
  derivados da unidade, do cenário e da rodada, e nunca colidem entre rodadas, entre unidades nem
  com outro Edital. O mesmo vale para os e-mails, os sujeitos e a correlação das pessoas e dos atos.
- **FR-4631**: Os CPFs são calculados, com dígitos verificadores corretos e iniciados por `000`, e
  não se repetem num cenário antes da rodada 500.
- **FR-4632**: Nomes levam o sobrenome "Treinamento" e o código do cenário; e-mails são de
  `treinamento.exemplo.test`, domínio reservado que não entrega.
- **FR-4633**: Título do Processo, título e descrição do Edital, justificativas, pareceres e todo
  PDF anexado levam a marca "TREINAMENTO — DADO FICTÍCIO, SEM VALOR LEGAL".
- **FR-4634**: Durante a montagem o correio é o de memória do Django: comprovante de inscrição e
  comunicação de convocação não saem do processo.

### Fidelidade ao domínio

- **FR-4640**: Todo estado é alcançado pelos comandos da aplicação — os mesmos da tela e do
  portal —, sem SQL e sem gravar linha de domínio pelo ORM. A única exceção é a do `seed_demo`: a
  identidade e o e-mail verificado da pessoa fictícia.
- **FR-4641**: Um estado avançado tem o histórico que o produz: inscrições enviadas, Retificação de
  encerramento, avaliações concluídas e consolidadas, ordem, resultado, corte, apuração.
- **FR-4642**: Cada passo é praticado por um ator com as permissões do papel do seletor que lhe
  corresponde, ou sem permissão nenhuma quando a base é a comissão.
- **FR-4643**: O sorteio usa a Fonte de demonstração com um concurso próprio da rodada e da
  unidade (D-004);
  sem a fonte ligada no ambiente, os cenários de sorteio são recusados na pré-visualização.

### Catálogo

- **FR-4650** *(revista em 2026-11-12, com a FR-4615)*: O catálogo tem dezessete cenários, C01 a
  C17, cada um com nome, objetivo, tipo de seleção, método, estado inicial, pré-condições, papéis,
  próxima ação, resultado esperado, dependências e restauração. Os dois últimos são os da
  formalização (FR-6720).

  > **Redação anterior, preservada:** O catálogo tem quinze cenários, C01 a C15, cada um com nome,
  > objetivo, tipo de seleção, método, estado inicial, pré-condições, papéis, próxima ação,
  > resultado esperado, dependências e restauração.
- **FR-4651**: Os Processos dos cenários se chamam `SIM-TREINAMENTO-NNN` (e `-RN` a partir da
  segunda rodada), com título terminado em "(FICTÍCIO)"; os Editais, `SIMNN/ano`.
- **FR-4652**: As datas são contadas do instante da geração; o cenário com prazo que corre declara
  a validade, e a verificação avisa quando ela venceu.
- **FR-4653**: A comissão de cada cenário é de identidades `treino.*`, que a página de acesso da
  demonstração passa a oferecer sozinha.
- **FR-4654**: A listagem diz, por cenário, a rodada em uso e as substituídas.
- **FR-4655**: Para cada cenário, a próxima ação da ficha é executável pelo ator que ela nomeia.
- **FR-4656**: Os cenários de sorteio (C06 e C07) declaram a cota PPP ao lado da ampla
  concorrência: três dos dez inscritos a declaram na inscrição, sem anexo, e a autodeclaração é
  pedida só aos cotistas, na convocação. O C07 nasce com as duas relações congeladas, e a mesma
  ocorrência semeia os dois sorteios (D-008).

### Provisionamento de treinamento da formalização (revisão de 12/11/2026)

> **Faixa de identificadores.** A revisão abre em **FR-6720** e **SC-2210**. A faixa reservada em
> 12/11/2026 vai até o requisito funcional seis mil setecentos e trinta e nove, o critério dois mil
> duzentos e dezenove e, nos de experiência, de setecentos e dez a setecentos e dezenove, que esta
> revisão não usa. Os vinte requisitos funcionais anteriores a ela ficaram com a revisão da `117`
> em curso no mesmo dia.

- **FR-6720**: O catálogo ganha dois cenários da formalização, que partem do mesmo estado: um Edital
  por notas com três pessoas convocadas, com aceite registrado e, por isso, aptas (a FR-3669 da
  `117`), e a definição dos documentos para a formalização gravada pela presidência.
  - **C16 — Exportação à formalização**: a pessoa do setor nasce habilitada **e** designada para o
    Edital; o exercício é verificar e exportar.
  - **C17 — Designação para a formalização**: a pessoa do setor nasce **só habilitada**, sem
    designação; o exercício é designá-la.
- **FR-6721**: **A identidade fictícia.** O gerador cria, quando ela não existe, uma pessoa só, de
  identificador `treino.formalizacao`, com o nome "Formalização Treinamento" e e-mail de
  `treinamento.exemplo.test`, sem senha utilizável e sem identidade externa. Por isso ela não entra
  pela autenticação institucional, e a busca de pessoas da gestão de acessos não a encontra, porque
  só lê identificadores institucionais. Ela se reaproveita entre cenários, rodadas e unidades, sem
  nenhuma escrita; duas cargas simultâneas que a criem ficam com uma só. O gerador nunca a altera:
  inativa — mesmo suspensa com o vínculo vigente —, o cenário falha com `pessoa_indisponivel`
  (`FALHOU`, FR-4612), e ela não é reativada.
- **FR-6722**: **O vínculo.** O gerador concede à identidade o papel Formalização na unidade do
  cenário, pelo comando de concessão da `107`, com motivo e trilha, só quando ela não o tem vigente
  ali. Nenhum outro papel é concedido, a ela ou a qualquer pessoa, e nenhum vínculo é revogado.
- **FR-6723**: **A designação.** No C16, o gerador designa a identidade para o Edital do cenário,
  sem restringir Perfil, pelo comando de designação da `117`, com motivo. No C17 não designa.
- **FR-6724**: **Quem concede e designa.** Os dois atos são praticados por `treino.acessos`, ator
  só do gerador, com as permissões do papel Administrador de acessos da unidade, em memória. Ele não
  recebe vínculo, não existe como pessoa e não entra pela página de acesso: o gerador não
  provisiona acesso administrativo a ninguém. É a exceção à FR-4642, porque o seletor não oferece
  esse papel.
- **FR-6725**: **As proteções são as mesmas.** O provisionamento só acontece dentro da montagem do
  C16 ou do C17, e por isso está sob a chave e o banco por extenso (FR-4601, FR-4602), na transação
  do cenário (FR-4612) e na idempotência da carga (FR-4611): cenário pronto não provisiona de novo.
  A pré-visualização do C16 e do C17 diz se a identidade e o vínculo seriam criados ou mantidos
  (FR-4604); com os dois no mesmo plano, só o primeiro os cria, e o segundo diz que vêm dele.
- **FR-6726**: **Restaurar não exclui.** A restauração do C16 ou do C17 cria a rodada seguinte, como
  a dos outros (FR-4621), e a identidade e o vínculo são reaproveitados. A restauração de
  **qualquer** cenário revoga, pelo comando de revogação da `117` e com motivo, as designações
  vigentes em **todos** os Editais do Processo da rodada anterior — também o encerrado, que não se
  cancela e continua designável —, e a pré-visualização diz quantas serão revogadas. Sem isso, a
  lista do setor continuaria oferecendo o Edital antigo, e a designação feita pela tela num cenário
  de convocação sairia sem aviso.
- **FR-6727**: **A entrada.** A identidade fica fora das sugestões por papel da página de acesso,
  como todo ator `treino.` (o plano desta spec); a lista das comissões da FR-4653 não a alcança,
  porque ela não integra comissão. A equipe entra pelo campo livre, com `treino.formalizacao`,
  marcando "Formalização"; o guia o diz.
- **FR-6728**: **Os documentos.** O Edital do C16 e do C17 pede a identificação na inscrição e
  nenhum documento na convocação, e a definição leva a identificação. O aceite com documento
  obrigatório da convocação exige conferência *conforme*, que exige a abertura do arquivo pela tela,
  e o gerador não a fabrica (D-007, D-010).
- **FR-6730**: **Só no treinamento.** As identidades `treino.` só são oferecidas para designar, e
  só contam como pessoa com o papel ou designação efetiva (as FR-6107 e FR-6113 da `153`), num Edital
  de Processo que o manifesto registra. Em todo outro Edital da unidade — e na tela de acessos sem
  Edital escolhido — elas não aparecem nem contam, embora o vínculo seja da unidade. A autorização
  da `117` não muda: só a oferta e a contagem. O Processo se reconhece pelo manifesto, lido pelo
  registro de apps, sem que o domínio importe o app de treinamento (D-001).
- **FR-6731**: **Escolher da lista** (decisão do usuário de 12/11/2026). As duas telas de designar
  para a formalização — a seção "Quem acessa os documentos", da presidência, e a de Acessos da
  unidade — resolvem a pessoa enviada **só entre as que a própria tela ofereceu**: quem tem o papel
  Formalização vigente na unidade, ativo, com a regra da FR-6730 para o Edital escolhido. Ninguém
  de fora da lista é designado. Fora dela, a resposta é a de antes: a pessoa institucional ativa sem
  o papel recebe o código da FR-3663 (a FR-6701 da `117`), e todo outro identificador — inexistente,
  inativo, de treino fora do treinamento, adulterado — a recusa única de pessoa indisponível. A
  autorização da `117` (quem designa) e as conferências do comando de designar — papel vigente,
  autodesignação, trava — não mudam. A concessão de papel da `107` continua resolvendo a pessoa
  entre as institucionais.

  > **Redação anterior, preservada** (a prática das duas telas desde a `117`, sem alínea própria, e
  > a decisão da `107` sobre o identificador no formulário): a pessoa enviada se resolvia entre as
  > pessoas institucionais ativas, de identificador `pessoa-`, e a recusa de pessoa inexistente ou
  > inativa era a mesma.
- **FR-6740**: **Sem quem já está designado** (revisão de 12/11/2026, V-N01 da reavaliação da
  jornada final). A lista das duas telas de designar da FR-6731 MUST deixar de fora quem já tem
  designação vigente no Edital escolhido, e a pessoa enviada continua resolvida por essa mesma lista.
  A tela aberta antes da designação de alguém e enviada depois cai fora da lista e recebe a resposta
  de fora dela: a pessoa institucional segue ao comando, que a recusa por designação vigente, como
  antes; a de treino recebe a recusa única de pessoa indisponível. Quando todas as pessoas com o
  papel já estão designadas, a tela MUST dizer isso, e não que ninguém tem o papel; na tela de
  Acessos da unidade, a escolha de outro Edital continua oferecida. Sem Edital escolhido, ninguém sai
  da lista. Nada muda no comando de designar nem na revogação.

  > **Redação anterior, preservada** (a FR-6731, sem esta alínea): a lista era a de quem tem o papel
  > vigente na unidade, ativo, com a FR-6730, e oferecia também quem já estava designado para o
  > Edital — escolhê-lo só levava à recusa de designação vigente.
  >
  > *Por que mudou:* a pessoa de treino não é institucional, de propósito (FR-6721), e a tela a
  > oferecia no Edital de treinamento para recusá-la ao gravar. O usuário escolheu, entre essa saída
  > e dar à pessoa de treino um identificador institucional, a que mantém a pessoa fora da busca de
  > pessoas e da entrada institucional.
- **FR-6729**: **A primeira autoridade.** O provisionamento não usa autoridade: o C16 e o C17 assinam
  os atos do certame com a mesma autoridade dos outros cenários (FR-4616).

## Critérios de sucesso

- **SC-1451**: Sobre um banco já populado, a carga deixa toda linha preexistente idêntica, campo a
  campo, em todas as tabelas.
- **SC-1452**: A segunda carga não grava nenhuma linha.
- **SC-1453**: Exercitar um cenário não muda o retrato de outro.
- **SC-1454**: A restauração do C07 depois de um sorteio feito pela tela muda só as linhas do
  Processo, do Edital e do manifesto da rodada anterior, e a rodada nova sorteia de novo.
- **SC-1455** *(revisto em 2026-11-12, com a FR-4650)*: Os dezessete cenários se criam juntos e a
  próxima ação de cada um é executada na suíte.

  > **Redação anterior, preservada:** Os quinze cenários se criam juntos e a próxima ação de cada
  > um é executada na suíte.
- **SC-1456**: Uma pessoa da comissão identifica o cenário pela lista, entende o exercício pelo
  guia e o executa sem ajuda técnica. **Humano, pendente.**
- **SC-2210**: No C16 carregado, quem entra como `treino.formalizacao` com o papel Formalização
  verifica e exporta, pela tela, o pacote das três pessoas aptas; e o Centro do Edital conta uma
  pessoa designada, e não "ninguém designado".
- **SC-2211**: No C17 carregado, a lista do setor diz a `treino.formalizacao` que ainda não foi
  designada, e o Centro conta uma pessoa com o papel e nenhuma designada, com as três pessoas aptas
  sem quem receba. `treino.presidencia` a designa pela tela (FR-6731), e o setor então exporta.
- **SC-2213**: Num Edital real da mesma unidade, com a pessoa de treino vinculada e até designada,
  o Centro não a conta e nenhuma tela de designar a oferece.
- **SC-2214**: Pelas duas telas de designar, a pessoa institucional com o papel continua designável;
  `treino.formalizacao` é designável no Edital de treinamento e recusada num Edital real; o
  identificador fora da lista e o adulterado são recusados sem gravar nada.
- **SC-2220**: Pelas duas telas de designar, quem já tem designação vigente no Edital não aparece
  na lista; enviado assim mesmo, nada se grava. Com todas designadas, a tela diz que já estão
  designadas (FR-6740).
- **SC-2212**: A carga do C16 e do C17 juntos cria uma pessoa e um vínculo; a segunda carga, e a
  restauração, não criam pessoa nem vínculo. Nenhum vínculo além do Formalização da identidade
  `treino.formalizacao` nasce de carga ou restauração.

## Decisões

#### D-001 — Um app próprio, com uma tabela só

O manifesto mora em `processo_seletivo.treinamento`, que nenhum app do domínio importa. Sai inteiro
sem que o produto perceba. A alternativa — um campo "é treinamento" no Processo — mudaria o modelo
do domínio para uma necessidade de operação.

#### D-002 — Restaurar é criar a rodada seguinte, e não apagar

A Constituição proíbe excluir dado normativo, e as tabelas append-only recusam exclusão por gatilho
e por privilégio. Uma restauração por exclusão é impossível nesta base, e uma que desligasse os
gatilhos seria o contorno que o pedido proíbe. Por isso a rodada anterior fica, cancelada pelos
comandos de cancelamento; sai da aba "Em andamento", e a nova toma o lugar dela.

#### D-003 — Propriedade por manifesto e trilha, não por prefixo

Qualquer pessoa pode digitar `SIM-TREINAMENTO-007` na tela de criação de Processo. O prefixo serve
para a equipe reconhecer o cenário; para o gerador, só o manifesto mais o registro de criação na
trilha, com a correlação da rodada.

#### D-004 — O sorteio usa a Fonte de demonstração

A extração da Loteria é futura: um cenário que dependesse dela faria esperar. Um concurso já
realizado seria conhecido antes do congelamento, e a conferência da `116` o acusa. A Fonte de
demonstração já existe para isto: o nome dela é publicado no Edital e no manifesto do sorteio, ela
só existe onde `SORTEIO_FONTE_DE_DEMONSTRACAO` a liga, e produção recusa subir com a chave. Nenhuma
resposta da Caixa é simulada.

#### D-005 — Os moldes do `seed_demo`, com identificadores remapeados

Os rascunhos do `seed_demo` são os que a suíte prova publicáveis a cada commit. O gerador os
reaproveita e troca os identificadores fixos por UUIDs derivados do cenário e da rodada.

#### D-006 — A inscrição pelo caminho do portal

Ao contrário do `seed_demo`, que grava a inscrição enviada pelo ORM, o gerador abre o rascunho,
escolhe a modalidade, anexa o documento e envia, pelos comandos do portal. Fica mais lento e passa
por todas as conferências do envio.

#### D-007 — Conforme só depois de aberto

Conferir como conforme exige que o conferente tenha aberto o arquivo, e a abertura é registrada
pela tela que o serve. O gerador não fabrica esse registro: nenhum item nasce conforme, e a
primeira conferência conforme de cada cenário é da equipe.

#### D-008 — O sorteio com cota, e a comprovação depois dele

Pedido do setor em 09/11: o sorteio real do Cefor tem reserva de vagas, e a comprovação da cota é
analisada depois do sorteio, na convocação. O molde do `seed_demo` sorteia só a ampla concorrência,
de propósito (uma relação, um ato), e a primeira versão dos cenários o seguiu. Agora o Perfil de
sorteio reparte as quatro vagas em três na ampla e uma na PPP, como o de notas, e o C07 congela as
duas relações — a da ampla com todos, a da cota com quem a declarou (021, D-006 daquela spec). A
conferência do comprovante depois do sorteio **não** ganhou cenário próprio: os cenários de
convocação (C10 a C12) partem de um Edital por notas.

#### D-009 — O provisionamento da formalização é exceção nomeada, e não regra nova

Decisão do usuário de 12/11/2026 (FR-4615). Havia duas formas: um comando de provisionamento
separado, ou o provisionamento dentro da montagem do cenário. A segunda foi a escolhida, porque
herda sem código novo a chave, o banco por extenso, a transação e a idempotência, e porque o que se
provisiona só faz sentido junto do Edital do cenário. A exceção é estreita de propósito: uma
identidade, um papel e as designações do Edital do cenário. Oferecer o Administrador de acessos no
seletor resolveria o mesmo achado, mas daria a qualquer um na demonstração o poder de conceder
papel — e o achado era sobre a formalização, não sobre a gestão de acessos.

#### D-010 — O aceite sem conferência, por um Edital sem documento na convocação

Para nascer apta, a pessoa precisa de aceite, e o aceite exige os obrigatórios da convocação
conferidos *conforme* (a FR-3592 da `115`), o que exige a abertura do arquivo pela tela (D-007).
Fabricar a abertura contrariaria a D-007. Por isso o Edital do C16 e do C17 pede documento só na
inscrição, e é esse documento que vai ao setor, sem conferência, como a `117` prevê para o que vem
da inscrição. O custo é declarado na ficha: o pacote do exercício tem um documento por pessoa, e
não os da convocação.

## Limitações e o que fica de fora

- **Sem Loteria Federal real.** O C07 sorteia com a Fonte de demonstração (D-004). Um cenário com a
  extração real exigiria esperar o sábado seguinte ao congelamento.
- **A rodada anterior fica no banco** (D-002). Restaurar muitas vezes acumula Processos cancelados
  na aba "Cancelados"; a lista "Em andamento" fica com uma rodada por cenário.
- **Validade.** C01 vale 7 dias; C02, C11, C12 e C13, 30; C08, 5. Depois disso o estado inicial
  deixa de ser o da ficha, e a verificação manda restaurar.
- **C09 e C14** chegam ao definitivo por um marco que **não admite recurso**: chegar ao definitivo
  com recurso exigiria esperar o fim do prazo, que é de dias corridos.
- **O correio da homologação** recebe o código de acesso do candidato fictício (`.test`), que não
  entrega. Para exercitar o portal (C02, C08, C11), a equipe se inscreve com o próprio e-mail, ou
  lê o código no mailpit da homologação, com o e-mail do candidato, que segue um padrão (guia).
- **Os PDFs fictícios** são válidos e marcados, mas não imitam documento real.
- **Designar pela demonstração.** Desde a revisão da `117` de 12/11/2026 (a FR-6700 dela), a
  presidência da comissão do Processo também designa, e, desde a FR-6731, a tela aceita a pessoa de
  treino que ela mesma ofereceu: o exercício do C17 se faz pela demonstração, com
  `treino.presidencia`. O Administrador de acessos continua fora do seletor e do gerador (FR-6724).
- **Arquivos.** Os documentos fictícios vão para `ARQUIVOS_CANDIDATOS_RAIZ`. Se a transação de um
  cenário falha depois de gravar um arquivo, o arquivo pode ficar órfão no disco: o banco não
  aponta para ele.
