# Revisão de 02/11/2026 da Visão do Sistema

A documentação descrevia o sistema até a spec 104 (30/10). Entre 30/10 e 02/11 entraram na `main` 23 PRs:

- as specs 105 a 111 e a 113;
- a 112, só especificada;
- as correções da auditoria de prontidão de 31/10 (A-01 a A-12).

Algumas frases ficaram falsas:

- a gestão "só" com a entrada de demonstração;
- a Unidade "sem tela";
- os "oito papéis";
- o reaproveitamento que "não copia o teto nem o Requerimento";
- a Retificação em curso "não barrada pelo desfecho do Edital";
- o encerramento que "só fecha as inscrições";
- as 41 tabelas append-only e os 59 gatilhos.

Esta revisão descreve tudo isso contra a `main` em `4dbc5872`.

## Como foi conferido

- **Três leituras paralelas** confrontaram as specs e os PRs com o código da `main`, e não só com a própria spec:
  - identidade, acessos e unidades (106, 107, 109, 110, e os PRs 343 e 347);
  - documentação, trilha, Kit e a 112 (105, 108, 111, 112);
  - o encerramento e as correções (113, PRs 354 a 363).

  Onde spec e código divergiam, valeu o código.
- **Rótulos conferidos de novo no código** antes de entrar no texto, entre eles:
  - *Entrar com a conta institucional* (`identificar.html`);
  - *Sem acesso vigente* (`sem_acesso.html`);
  - *Atuando em* e *Trocar* (`base.html`);
  - as seções e os grupos da barra (`interface/navegacao.py`, `SECOES` e `SECOES_DE_ACESSO`);
  - os três papéis de acesso (`seguranca/acessos.py`);
  - *Kit de divulgação* (`interface/acoes.py`);
  - *Antes de encerrar, resolva*, *Continuam depois do encerramento* e *Serão atingidos pelo cancelamento* (`confirmar.html`, `interface/encerramento.py`);
  - *Edital em estado final não admite alteração.* (`processos/domain/finalizacao.py`);
  - os comandos `conceder_`, `retirar_` e `substituir_administracao_institucional`.
- **Os números de *Maturidade*** foram recontados pelo método da própria página. Rodado sobre `62824816`, a base da revisão de 30/10, ele reproduz todos os números publicados naquela data.
- **A suíte rodou contra PostgreSQL**, pela primeira vez numa revisão desde 30/09: 14 638 passando, 14 pulados e nenhuma falha (4 workers, 569s). A rodada tinha o grupo `assistente` e não tinha o `navegador`, de modo que os dois arquivos de jornada no navegador pularam e não rodaram aqui. O `AGENTS.md` recebeu a medição e a repartição dos pulados.
- **A página foi aberta no navegador** pela entrada `visao-do-sistema` do `.claude/launch.json` (porta 8090), sem erro no console. As verificações estruturais:
  - todas as âncoras internas têm destino;
  - nenhum `id` se repete;
  - o HTML fecha as tags que abre;
  - `tests/interface/test_documentacao_do_sistema.py`, que cobra a página servida pela gestão, passa (12 casos).

## O que mudou na documentação

- **Seções novas:**
  - *Quem concede acesso, e como* (`#gestao-de-acessos`);
  - *O cadastro de unidades* (`#cadastro-de-unidades`);
  - *O Kit de divulgação do Edital* (`#kit-de-divulgacao`);
  - as subseções *A entrada institucional* (`#entrar-institucional`), *A trilha da unidade* (`#trilha-da-unidade`) e *Encerrar o Edital: só o que é conclusão regular* (`#encerramento-seguro`).
- **Entrar e navegar.** A página de acesso passou a dizer os dois métodos e as frases de fim de sessão. Também mudaram:
  - a barra: três grupos e onze seções possíveis;
  - o caminho no topo;
  - os papéis: nove de operação mais três de acesso, e a Comunicação, que não se atribui antes da 112;
  - a equipe pequena: ninguém concede o próprio acesso;
  - a matriz: a linha da trilha da unidade.
- **Encerramento e correções:**
  - o tutorial, *Encerrei ou cancelei*, o rito de publicação, os estados do Edital e da Retificação e o relatório do Edital dizem o encerramento seguro (113);
  - a Retificação para com o desfecho do Edital (A-09);
  - o reaproveitamento leva o teto e o Requerimento (A-10), e a seção passou de *Parcial* a *Implementado*;
  - a inscrição enviada, a avaliação concluída e a homologação ganharam gatilho (A-03);
  - o julgamento reserva a idempotência antes do impedimento (FR-097);
  - o portal diz o teto da conexão (A-12).
- **Duas lacunas viraram notas de fechamento:** *a Retificação em curso não é barrada* e *dois furos no ciclo*. *Fechados desde 20/09* ganhou sete linhas. *Reuso sem o teto* saiu de *Interface ausente*.
- **Estado do produto:**
  - 114 pastas de especificação;
  - 46 tabelas append-only e 72 gatilhos (em 31 migrations, sobre 60 tabelas);
  - 102 migrations;
  - 488 arquivos Python de aplicação (124,6 mil linhas);
  - 200 templates;
  - 1 005 + 17 arquivos de teste;
  - 153 + 36 rotas;
  - 67 das 114 specs dizem `Draft`.

  A autenticação institucional passou de *Lacuna* a *Parcial*: a gestão está pronta, e falta o adaptador do provedor do Ifes. A maturidade ganhou as linhas *Acessos e unidades* e *Kit de divulgação*. Entrou *Abertas desde 30/10* (`#abertas-desde-30-10`).
- **Catálogo e glossário.** O catálogo passou de 141 a 150 capacidades, e o glossário de 126 a 130 termos: *Administrador institucional*, *Kit de divulgação*, *Trilha da unidade* e *Vínculo de acesso*. O índice de letras ganhou o K, e o A passou a apontar para o primeiro termo.
- **Âncoras.** Nenhuma foi removida. As novas são `#gestao-de-acessos`, `#cadastro-de-unidades`, `#kit-de-divulgacao`, `#entrar-institucional`, `#trilha-da-unidade`, `#encerramento-seguro`, `#abertas-desde-30-10` e as dos quatro termos novos.
- **README e AGENTS.md:**
  - no README, as linhas da 111 (incremento B mergeado) e da 113 (PR 362);
  - no `AGENTS.md`, a medição da suíte, os dois arquivos de jornada que pulam sem o grupo `navegador` e as 102 migrations.

## O que não foi verificado, e o que ficou de fora

- **Nada foi percorrido no produto**, e a entrada institucional não pode ser: o único provedor é o simulado dos testes. Os rótulos vêm dos *templates*; o comportamento, das views e dos testes.
- **As specs aparecem como entregues, e não como validadas.** A 110 (SC-1048) e a 111 (SC-1054) esperam pessoas, e a 106 a 109 deixaram perguntas de governança ao usuário.
- **Dois defeitos registrados, não corrigidos:**
  - o título *“Retificaçãoões”* (`retificar.html`, linha 27), que continua desde 30/10;
  - os 58 links da página para o repositório (`../../backend/…`, `../../specs/…`), que respondem 404 quando ela é aberta dentro da gestão (105). Esse é novo.
- **A divergência do papel Comunicação foi descrita, não resolvida:** a spec manda não atribuí-lo antes da 112, e o código o oferece.
- **O manual (`doc/manual/`) não foi tocado.** Uma Revisão 7 é decisão do usuário.

---

# Revisão de 04/11/2026 da Visão do Sistema

A documentação descrevia o sistema até a 113 (02/11). Entre 02 e 04/11 entraram na `main` 19 PRs:

- as specs 114 a 118 e a 119 (spec e incrementos 1 e 2);
- o incremento C da 111;
- a correção da 029 (#380, #381);
- dois documentos sem código (#367, a auditoria de matrícula e dossiê; #375, a revisão de UX da jornada do convocado) e a correção de um teste intermitente (#379).

Algumas frases ficaram falsas:

- o candidato que "só lê" a convocação;
- "nada acontece por passagem de tempo", sem dizer que o prazo fecha o envio;
- o pacote do Kit que "não existe";
- "Situação registrada" e as três grafias do desfecho no portal;
- o concurso "Concurso 5900" como forma aceita na Loteria Federal;
- os nove papéis, as 46 tabelas append-only, os 72 gatilhos e as 153 + 36 rotas.

Esta revisão descreve tudo isso contra a `main` em `a3e23b1f`.

## Como foi conferido

- **Quatro leituras paralelas** confrontaram as specs e os PRs com o código da `main`, e não só com a própria spec:
  - 115 e 117 (documentos na convocação e formalização);
  - 118 e a correção da 029 (o convocado no portal e o Requerimento com o Processo encerrado);
  - 114 e 116 (desempate por outra Etapa e o concurso conferido na Caixa);
  - 111-C e 119 (o pacote e as famílias do Kit).

  Onde spec e código divergiam, valeu o código.
- **Os números de *Maturidade*** foram recontados pelo método da própria página. Rodado sobre `4dbc5872`, a base da revisão de 02/11, ele reproduz todos os números publicados naquela data. Hoje: 53 tabelas append-only, 83 gatilhos em 33 migrations sobre 67 tabelas, 107 migrations, 23 módulos, 515 arquivos Python de aplicação (135,6 mil linhas), 213 templates, 1 062 arquivos de teste Python e 17 de JavaScript, 166 + 38 rotas.
- **A página foi verificada estruturalmente**: todas as âncoras internas têm destino, nenhum `id` se repete, o HTML fecha as tags que abre, e nada do que entrou usa `style=`, `<style>`, `<script>` ou `on…=`. `tests/interface/test_documentacao_do_sistema.py` passa (12 casos).
- **A suíte rodou contra PostgreSQL**: 15 878 passando, 17 pulados e nenhuma falha (4 workers, 2 184s, com outra suíte no mesmo cluster). Os 17 são 10 do vocabulário, a recusa por vendor, o E2E da Caixa e cinco arquivos de jornada no navegador, que pulam sem o grupo `navegador`.

## O que mudou na documentação

- **Seções novas:**
  - *Documentos e conferência na convocação* (`#documentos-da-convocacao`, 115), com a subseção *Quem confere* (`#alocacao-a-conferencia`);
  - *Entrega documental ao setor da formalização* (`#formalizacao`, 117);
  - *O convocado no portal* (`#convocado-no-portal`, 118);
  - *As famílias e os formatos da peça* (`#kit-familias-e-formatos`, 119);
  - as subseções *Desempatar pela nota de uma Etapa que o marco não soma* (`#desempate-por-outra-etapa`, 114), *O concurso conferido na Caixa antes do compromisso* (`#sorteio-conferencia`, 116), *O Processo encerrado ou cancelado fecha o Requerimento na convocação* (`#requerimento-processo-encerrado`, 029) e *O pacote (.zip)* (`#kit-pacote`, 111-C);
  - *Abertas desde 02/11* (`#abertas-desde-02-11`).
- **Kit:** a tela em cinco passos (a identidade da peça entrou como o terceiro), a ficha versão 2 com carga horária e contato, e o que acende a faixa de desatualização em cada versão.
- **Sorteio:** a forma do concurso na Loteria Federal, a conferência na Caixa nos quatro atos, o botão *Conferir na Caixa*, o reaproveitamento sem a extração e a lacuna da regra de substituição, que não dispara contra a Caixa real.
- **Convocação e Requerimento:** o candidato envia documentos; o prazo fecha o envio sem decidir nada; aceite e regularização exigem os documentos conferidos; o Requerimento na convocação fecha com o Processo encerrado ou cancelado, e o pedido na inscrição continua aberto (decisão pendente).
- **Papéis e barra:** dez papéis de operação, com a Formalização; a seção *Formalização* no grupo Trabalho; o Administrador de acessos também designa para a formalização; a busca do seletor aparece com mais de dez entradas.
- **Matriz de capacidades:** linhas novas para o pacote do Kit, as famílias e formatos, o concurso conferido, a conferência sob demanda e a lacuna da substituição; o desempate por Etapa anotado.

## O que não foi verificado, e o que ficou de fora

- **O produto não foi percorrido**, e as jornadas no navegador não rodaram aqui, por falta do grupo `navegador`. A peça das famílias, o pacote de família e a conferência na Caixa contra o serviço real nunca foram vistos num navegador nesta revisão.
- **Nem todo trecho apontado pelas leituras entrou.** Ficaram para a próxima revisão: as linhas novas da matriz de permissões (conferir documentos, definir e exportar para a formalização), o degrau da alocação à conferência em *Da pessoa à avaliação*, as respostas rápidas sobre convocação, o glossário (*Apto para formalização*, *Conferência de documento*, *Designação para a formalização*), a lista de rotas e os passos 8, 11 e 12 da jornada do candidato. As seções novas descrevem o comportamento; esses trechos são índices e remissões.
- **Achado desta revisão, visto no código e não reproduzido:** todo download do Kit recebe o nome `kit-<n>-<ano>.<extensão>`, sem o formato; post, story e banner em PNG saem com o mesmo nome.
- **As specs não acompanharam o merge:** a 114, a 116 e a 118 dizem `Draft`, e a 119 diz "Não implementada".
- **O `CLAUDE.md`** diz que dois arquivos de jornada no navegador pulam sem o grupo `navegador`, e mede a suíte em 14 638 e 14; hoje são cinco arquivos (107, 110, 115, 117, 118), e a suíte, 15 878 e 17. A correção não foi feita aqui: o `CLAUDE.md` é das instruções de quem trabalha no repositório, e fica para quem o mantém.

# Atualização de 05/11/2026 da Visão do Sistema

Feita na hora do merge, a pedido de 04/11 ("quando for feito o PR, atualize a documentação do sistema"), sobre a `main` em `21b728af`, em duas passadas. Cobre o que entrou nesse dia: a spec 120 (PR #385) e, da 119, os incrementos 3a FIC (#387), 3d Aperfeiçoamento (#389), 3c UAB/bolsista (#386) — documentados no #390 — e 3b Libras (#391), 3f TMD (#392) e 3e Internos (#393), documentados na segunda passada. O estudo da experiência da convocação (#394, `doc/estudo-experiencia-da-convocacao-2026-11-05/`) é só documento, e não muda a descrição do sistema.

## Como foi conferido

- **Leitura direta**, sem leituras paralelas: a spec, a verificação e as decisões da 120; o parcial `_correcao_da_convocacao.html`, `convocar.py` e `fluxo.py` para os rótulos e para o lugar onde cada conferência mora; os módulos das seis famílias em `kit_familias/`, as referências em `kit_referencias/` e as settings para as famílias.
- **A suíte rodou contra PostgreSQL** sobre a árvore que virou a `main` (a integração local dos três PRs, idêntica a `9a459a0e`): 16 136 passando, 18 pulados e nenhuma falha (4 workers, 729 s, com o grupo `assistente` e sem o `navegador`). O 18º pulado é a jornada da 120 no navegador. A UAB entrou depois, sobre essa mesma `main`, com o CI verde no PR (a suíte inteira contra PostgreSQL).

## O que mudou na documentação

- **Convocação:** a lacuna *"corrigir uma convocação não tem tela"* deu lugar à subseção *Corrigir uma convocação em aberto, e dar mais prazo* (`#correcao-da-convocacao`), com a prévia no formulário, o motivo e o vencimento obrigatórios, a assinatura conferida sob a trava, a recusa que volta ao cartão, o impedimento pela apuração superada e o que fica fora por decisão. O aviso *Um prazo só por chamada* aponta para ela.
- **Matriz de capacidades:** a linha *Corrigir convocação ou suceder desfecho* (não operacionalizado) virou duas. *Corrigir convocação em aberto* está implementado. *Suceder desfecho registrado* continua não operacionalizado.
- **Pendências:** a linha da convocação ganhou a correção. Fica a sucessão do desfecho e a chamada sem vencimento.
- **Kit:** a tabela de templates ganhou os dezoito das seis famílias, e a seção ganhou um parágrafo por família e um sobre a Inter (P-2). *O que ainda falta* deixou de listar famílias, e a matriz e as pendências dizem as sete. A suíte da segunda passada, sobre a árvore de `21b728af`: 16 413 passando, 18 pulados, nenhuma falha (701 s).
- **Testes, revisões e rodapé:** a linha da suíte foi atualizada, e a tabela de revisões, o *Onde esta documentação não alcança* e o rodapé ganharam a entrada de 05/11.

## O que não foi verificado, e o que ficou de fora

- **O produto não foi percorrido.** A jornada da 120 no navegador não rodou aqui; a verificação dela é a do PR (4 de 4, com capturas em `specs/120-…/capturas/`).
- **Maturidade não foi recontada:** os números de arquivos, *templates* e testes são os de 04/11. A 120 não acrescenta tabela, gatilho, migration nem rota.
- **A UAB (PR #386) entrou por último.** Integrada depois da FIC, ela reprovava 23 testes do kit: a FIC passou a usar no motor a caixa tipográfica da fonte como altura mínima da linha (`kit_peca.entrelinha`), e a Anton mede 1,5 corpo. A sessão da UAB refez as caixas com a altura nova e regenerou as referências e os resumos, sem tocar nas das outras famílias, e o PR foi mergeado com o CI verde.
- **A spec 120 ainda diz** *"Draft, só documental"* no cabeçalho, embora a implementação tenha entrado no mesmo PR.

## Acréscimo de 05/11: a spec 121, só especificada

O PR #396 mergeou a spec 121 (*A experiência da convocação — incremento 1*), sem código, sobre o estudo do #394. A página ganhou um aviso *Previsto* em *O convocado no portal* com o que ela propõe, e a frase que dizia a 120 "ainda em PR" passou a apontar para a correção já descrita. A revisão de 05/11 e o rodapé apontam para a `main` em `de5df85c`. As decisões D-001 a D-012 da 121 aguardam o usuário; nada da 121 foi descrito como entregue.

## Acréscimo de 05/11: a spec 122, o plano da 121 e o estudo do sorteio

Entraram na `main`, que chegou a `5c3501d3`, a 122 com especificação e implementação (#398), o plano e as tarefas da 121 (#399) e o estudo de caso do sorteio do Edital 35/2026 (#400, `doc/estudo-sorteio-edital-35-2026-11-05.md`). O estudo é só documento e não muda a descrição do sistema.

- **122, os mesmos recortes em toda parte:** a nova subseção `#recortes-alinhados`, no rito do sorteio, substitui a lacuna *"a ampla declarada vira recorte no sorteio"*. Ela descreve a tela do sorteio só com os recortes operacionais e a frase da Modalidade apontada; a recusa `list_is_general_competition_alias` (422) ao congelar, sortear e divulgar; o acervo em *Registros fora da operação atual*, com a frase de origem (nascido ou tornado excedente); a obsolescência por `papel_do_recorte` na Retificação do apontamento; e a Supervisão e o relatório do Edital sem a lista excedente.
- **A ampla e as suas duas grafias:** a lacuna *"o sorteio não normaliza a grafia"* virou nota, e o que dela continua aberto ficou numa lacuna própria: o Edital com uma Modalidade "Ampla concorrência" não apontada.
- **Operar por marco, Receita 1, matriz e rotas:** a página do Edital tem um *divulgar o resultado* por marco, que leva à coluna *Publicação* da condução. A Receita 1 não manda mais "não cadastrar" a AC, e a matriz não diz mais que o sorteio deixa de normalizá-la.
- **121:** o aviso *Previsto* diz que o plano e as tarefas foram mergeados com as decisões aceitas, e registra a D-009 na opção escolhida: o nome do modelo e o SHA-256 dos arquivos gravados em cada comunicação emitida.
- **Revisão, testes e rodapé** apontam para `5c3501d3`. A linha dos testes cita a medição da 122 na worktree dela (16 470 e 19, sem os dois grupos).

**O que não foi verificado:**

- a suíte não rodou de novo; antes dos merges, a integração local dos três PRs passou nos testes de citação e da documentação;
- o percurso humano da 122 (T040) fica com o usuário;
- os números de maturidade não foram recontados.

## Acréscimo de 06/11: a 121 implementada e três estudos

Entraram na `main`, que chegou a `4e6d211f`:

- a implementação da 121 (#404);
- o achado da comunicação ao convocado (#401);
- o estudo de ocupação e dupla vaga do sorteio 35/2026 (#403);
- o guia de condução da jornada do sorteio (#405);
- a auditoria de UX da Retificação (#406).

Os quatro últimos são documentos em `doc/` e não mudam a descrição do sistema.

- **O convocado no portal:** a subseção *Na tela da convocação* deixou de descrever os cinco blocos da 118. Agora descreve a ordem da 121: título por estado, cartão do prazo com o dia da semana e a correção, um único *Ver o que preciso fazer*, *Andamento* e os blocos da 118. Também registra a volta a `#confirmacao` depois do envio. O aviso *Previsto* saiu.
- **Nova subseção `#convocacao-pelo-link`:** o link sem sessão passa pelo acesso e volta à convocação; antes terminava em 404. Também descreve os quatro modelos da mensagem, em HTML e texto, e a gravação do modelo e do SHA-256 em cada envio (D-009, `convocacao/0006`).
- **O que ficou de fora:** QI-7, o redirecionamento no acompanhamento e no Requerimento, e a SC-1164 humana.
- **Matriz:** as linhas do e-mail de convocação e da página de convocação ganharam a 121.
- **Revisão, testes e rodapé** apontam para `4e6d211f`. A linha dos testes cita a medição da 121: 16 730 e 12, com os dois grupos.

**Não verificado:**

- a suíte não rodou aqui;
- o produto não foi percorrido;
- a SC-1164 (clientes de e-mail, SPF, DKIM e DMARC) continua pendente.

## Acréscimo de 06/11: as specs 123 e 124, o guia do sorteio e o estudo da jornada operacional

Entraram na `main`, que chegou a `a1d3bf26`:

- a especificação, o plano e as tarefas da 123, o MVP de UX da Retificação (#409);
- a 124, os textos que o operador do sorteio lê, especificada e implementada (#410);
- a correção de quatro quadros *Atenção* do guia da jornada do sorteio (#408, `doc/guia-jornada-do-sorteio-2026-11-05/`);
- o estudo de orientação da jornada operacional do Edital (#412, `doc/estudo-orientacao-da-jornada-2026-11-06/`).

Os dois últimos são documentos em `doc/` e não mudam a descrição do sistema.

- **123:** um aviso *Previsto* em `#retificacao-lacunas` resume o MVP M1–M4. A busca acha o campo e leva o foco até ele. A conferência separa *na proposta* de *alterados desde a última conferência*. A versão-base é dita pelo que incorpora, sem a coluna “Vigente hoje”. Os impeditivos da criação aparecem já na conferência. As decisões D-001 a D-009 aguardam o usuário.
- **124, no rito do sorteio:**
  - o passo *Indisponibilidade* diz que a falha de acesso à Caixa sai com os motivos da conferência da 116, sem exceção nem código HTTP, e com o detalhe no log;
  - o *Aconteceu não antes de* da fonte que publica só a data diz que 00h00 é o limite inferior, e não a hora da extração;
  - a seção *O que se declara no Edital* registra o item *Ocorrência que fixará a semente* no *Como preencher* da Classificação.
- **Revisão e rodapé** apontam para `a1d3bf26`.

**Não verificado:**

- a suíte não rodou aqui; o #410 fechou em 16 755 passando e 12 pulados na worktree dele;
- o produto não foi percorrido;
- o #411 (125) não entrou: CI vermelho em três jornadas de navegador e conflito com a `main`.

## Acréscimo de 06/11: a 125, a convocação segue o canal

Entrou na `main`, que chegou a `22a722af`, a 125, especificada, planejada e implementada (#411).

- **Nova subseção `#convocacao-segue-o-canal`**, antes da correção da convocação, com três mudanças:
  - a convocação por publicação só aparece ao candidato depois do registro da publicação; toda superfície do portal lê pelo predicado derivado, e o envio de documento antes disso é recusado como item inexistente;
  - o texto digitado que chega ao candidato tem aviso nos sete campos e o passo *Conferir o texto*, sem script, que assina o texto;
  - a palavra segue o canal, por uma tabela única de frases.
- **Os três gestos:** a linha das pendentes diz *Publicações a registrar* na publicação.
- **Revisão e rodapé** apontam para `22a722af`.

**Não verificado:**

- a suíte não rodou aqui; o #411 fechou em 16 770 passando e 21 pulados na worktree dele, sem o grupo `navegador`, e o CI dele ficou verde;
- a SC-1209 é validação humana e está pendente;
- o produto não foi percorrido.

## Acréscimo de 08/11: as specs 126 a 133, a correção da 115 e a tabela de specs do README

Entraram na `main`, que chegou a `86cd0ee0`, as specs 126 a 133 e a correção da 115, todas em PRs de código com CI verde, mais cinco documentos de `doc/`.

- **126, a orientação depois do ato (#414):** nas telas do corte, da ordem, da ocupação e do sorteio, a sucessão do ato vigente fica num bloco `Suceder … (exige motivo)`, aberto só quando o ato está obsoleto, e as mensagens de sucesso nomeiam o recorte e o que foi gravado. No marco de sorteio, a lista que nenhuma inscrição enviada declarou é *Não se aplica* na condução, na conferência dos gestos, na convocação e na ocupação. O relatório, o consolidado e o Encerrar classificam a convocação pelos estados do domínio, com "sem comunicação enviada" como espécie própria. Nova subseção `#orientacao-p0`.
- **127, o andamento da seleção (#415, #416, #417):** depois da publicação, "O que fazer agora" começa pelas providências em aberto do Edital, por papel, derivadas das funções que já decidem cada tela de ato, em todas as famílias de classificação. O cartão "Classificação" vira o "Andamento da seleção", uma linha por Perfil, recolhida, com a matriz composta pela `jornada()` da 094. As mensagens de sucesso dos atos dizem "Próximo nesta lista". Nova subseção `#andamento-da-selecao`.
- **128, a ordem sem resultado (#419):** a ordem por pontuação é recusada (`ordering_without_stage_results`) quando o recorte tem inscrições e nenhuma delas tem Resultado vigente numa Etapa que o marco enumera. A tela da ordem não oferece o botão, a confirmação não abre e a conferência do gesto põe o recorte entre os impedidos. Ordem parcial e universo vazio continuam emissíveis, e as ordens já gravadas valem. Nova subseção `#ordem-sem-resultado`. A decisão P-1 (universo esvaziado pela habilitação) aguarda o usuário.
- **129, a Lista de Processos (#420 spec, #422 implementação):** `/gestao/` abre em "Em andamento", com as abas Encerrados, Cancelados e Todos; a busca procura em todas as situações, inclusive por "N/AAAA"; 20 Processos por página, com aba, busca e página no endereço. A linha deixa de oferecer ações, e a faixa "Ações disponíveis para você" diz, antes dos itens, o que não cobre. Nova subseção `#lista-de-processos-recortada`; as frases da 104 sobre a coluna "O que posso fazer" foram corrigidas.
- **130, o Encerrar Processo (#421):** a confirmação adverte, por Edital final publicado, as providências em aberto, com a regra e as frases do encerramento do Edital (113) e do relatório (099). É advertência, e não impedimento; "Cancelar Processo" não muda. Nova subseção `#encerrar-processo-adverte`.
- **131, a inaplicabilidade documental (#426):** o Documento Exigido obrigatório da convocação ganha a *condição de exigência*, texto que o sistema não avalia; o "não se aplica" da conferência só existe onde ela foi publicada, pede motivo com conteúdo e, havendo arquivo, abertura; o aceite e a regularização pedem a ciência, assinada. Uma migration na `editais` (0025) e o degrau 19 de elevação. Nova subseção `#condicao-de-exigencia`. A SC-1378 (validação humana) e as decisões P-3 e P-4 aguardam o usuário.
- **132, cinco ajustes de leitura (#429):** a Revisão separa os documentos na inscrição e na convocação; a composição somente leitura é de verdade em cinco etapas; a ajuda dos documentos explica momento, aproveitamento, obrigatoriedade e condição; a página pública conta só os obrigatórios a todos e marca o facultativo; o fundamento do indeferimento deixa de sair com "..". Nova subseção `#ajustes-de-leitura-dos-documentos`.
- **133, o marco intermediário (#432):** o marco cujo corte governa uma Etapa que outro marco do Perfil enumera deixa de apurar e de convocar (`apuracao_em_marco_intermediario`, 409); as telas preveem a recusa e o andamento diz *Não se aplica*. A derivação da 127 ganha três correções, e a frase do corte fixo diz "de cada lista de concorrência" quando há lista reservada. Nova subseção `#marco-intermediario`.
- **A correção da 115 (#425):** o gesto "Convocar os titulares num ato só" passa a gravar a lista de documentos de cada convocação, e o aceite e a regularização são recusados, antes das pendências, quando a lista não tem o que a versão da chamada pede (`lista_da_convocacao_incompleta`). Nenhum registro foi reparado: os afetados eram de demonstração. Nova subseção `#lista-no-gesto-de-titulares`.
- **O contrato de mutabilidade foi recontado** por medição: 139 campos, 85 retificáveis, 26 não retificáveis, 24 estruturais e 4 derivados. Os números anteriores (136, 84 e 24) não incluíam os campos da 115 e da 131.
- **O README** passou a dizer, nas linhas das specs 118, 120, 122, 124 a 133, o PR e a data do merge, no lugar de "sem merge".
- **Revisão, aviso de limites e rodapé** apontam para `86cd0ee0`.

Entraram também, sem mudar a descrição do sistema, documentos em `doc/` e um guia: o guia dos documentos no GPS (#423, #424), o estudo da classificação por etapas (#427), o estudo da concorrência concomitante e a revisão dele (#428, #430), o estudo de convergência de UX da condução (#431) e a POC pedagógica "GPS por Dentro" (#433).

**Não verificado:**

- a suíte inteira não rodou aqui; rodaram os 18 testes que leem `specs/` e `doc/`, que passaram. O que vem de execução é o que cada PR registrou;
- as telas não foram percorridas; os rótulos e códigos citados foram conferidos no código por amostragem, e os números de consultas por tela vêm do `verificacao.md` de cada spec;
- ficam abertas a P-1 da 128, a SC-1378, a P-3 e a P-4 da 131, a pendência 11 da 115 e a numeração repetida da 133 (`133-guia-visual-conceitos` e `133-jornada-sem-ato-errado`), que é decisão do usuário.

## Acréscimo de 10/11: o Centro de Controle como página do Edital (136, 138)

A página não descrevia o Centro de Controle do Edital da 136, que entrou em 09/11 numa rota própria e
"em validação". A spec 138 o pôs na rota do Edital, por decisão do usuário em 10/11 (validação com
operadores dispensada; o Centro mora na rota do Edital; os textos deixam de ser provisórios), e
esta atualização vai no mesmo PR que a troca, de modo que chega à `main` com ela.

- Seção nova, *A página do Edital publicado: o Centro de Controle (136, 138)*, depois do *Depois da
  publicação* da 127: as quatro camadas, a escolha da composição pela rota, o retorno do ato, a volta
  da 139, o endereço antigo `/centro/` e a página anterior por um ciclo.
- *Depois da publicação* (127) ganhou uma frase dizendo que os cartões dele continuam na página
  anterior.
- Rótulos conferidos no código da worktree da 138: *Onde estamos*, *Situação administrativa*,
  *Inscrições*, *Seu papel aqui*, *O que fazer agora*, *Por que esta*, *Onde cada lista está*,
  *Administração e histórico*, *Voltar ao Centro de Controle do Edital* (`centro_do_edital.html`,
  `_proximo_nesta_lista.html`).
- Não foi recontada a seção *Maturidade*, e a 137 (o Processo agrega os Editais), que não foi feita,
  não entrou.

