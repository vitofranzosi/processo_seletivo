# Feature Specification: Cenários de treinamento e homologação

**Feature Branch**: `claude/gps-training-staging-scenarios-bc947c`, sobre a `main` em `86cd0ee0`

**Created**: 2026-11-08

**Status**: Implementada em 08/11/2026, sem merge. Uma migration (`treinamento/0001`), um app
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
  não deixa nada. A falha de um cenário não impede os outros.
- **FR-4613**: A propriedade de um Processo pelo gerador se comprova pelo manifesto **e** pela
  trilha (o registro de criação com a correlação da rodada), e não pelo prefixo do código.
- **FR-4614**: Um Processo com o código reservado de um cenário e sem manifesto é relatado como
  conflito e não é reaproveitado, alterado nem restaurado.
- **FR-4615**: O gerador não cria nem altera configuração institucional: unidade, autoridade,
  papel, vínculo ou usuário.
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
- **FR-4625**: A restauração não altera outro cenário, Edital real, pessoa, unidade ou autoridade.
- **FR-4626**: A rodada anterior continua consultável, com o histórico do exercício, na aba
  "Cancelados".

### Dados fictícios e efeitos externos

- **FR-4630**: Os identificadores de Perfil, Etapa, marco, Evento, Modalidade e Documento são
  derivados do cenário e da rodada, e nunca colidem entre rodadas nem com outro Edital.
- **FR-4631**: Os CPFs são calculados, com dígitos verificadores corretos e iniciados por `000`.
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
- **FR-4643**: O sorteio usa a Fonte de demonstração com um concurso próprio da rodada (D-004);
  sem a fonte ligada no ambiente, os cenários de sorteio são recusados na pré-visualização.

### Catálogo

- **FR-4650**: O catálogo tem quinze cenários, C01 a C15, cada um com nome, objetivo, tipo de
  seleção, método, estado inicial, pré-condições, papéis, próxima ação, resultado esperado,
  dependências e restauração.
- **FR-4651**: Os Processos dos cenários se chamam `SIM-TREINAMENTO-NNN` (e `-RN` a partir da
  segunda rodada), com título terminado em "(FICTÍCIO)"; os Editais, `SIMNN/ano`.
- **FR-4652**: As datas são contadas do instante da geração; o cenário com prazo que corre declara
  a validade, e a verificação avisa quando ela venceu.
- **FR-4653**: A comissão de cada cenário é de identidades `treino.*`, que a página de acesso da
  demonstração passa a oferecer sozinha.
- **FR-4654**: A listagem diz, por cenário, a rodada em uso e as substituídas.
- **FR-4655**: Para cada cenário, a próxima ação da ficha é executável pelo ator que ela nomeia.

## Critérios de sucesso

- **SC-1451**: Sobre um banco já populado, a carga deixa toda linha preexistente idêntica, campo a
  campo, em todas as tabelas.
- **SC-1452**: A segunda carga não grava nenhuma linha.
- **SC-1453**: Exercitar um cenário não muda o retrato de outro.
- **SC-1454**: A restauração do C07 depois de um sorteio feito pela tela muda só as linhas do
  Processo, do Edital e do manifesto da rodada anterior, e a rodada nova sorteia de novo.
- **SC-1455**: Os quinze cenários se criam juntos e a próxima ação de cada um é executada na suíte.
- **SC-1456**: Uma pessoa da comissão identifica o cenário pela lista, entende o exercício pelo
  guia e o executa sem ajuda técnica. **Humano, pendente.**

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
  entrega. Para exercitar o portal (C02, C08, C11), a equipe se inscreve com o próprio e-mail, ou o
  administrador lê o código no correio do ambiente.
- **Os PDFs fictícios** são válidos e marcados, mas não imitam documento real.
- **Arquivos.** Os documentos fictícios vão para `ARQUIVOS_CANDIDATOS_RAIZ`. Se a transação de um
  cenário falha depois de gravar um arquivo, o arquivo pode ficar órfão no disco: o banco não
  aponta para ele.
