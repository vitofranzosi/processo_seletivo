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

## Acréscimo de 10/11: as specs 134 a 141 e o estudo de continuidade operacional

Entraram na `main`, que chegou a `daba322f`, sete specs implementadas, em PRs de código, mais dois estudos de `doc/`. Há **duas specs 134** e, antes delas, duas 133; a numeração é decisão do usuário, e esta Visão diz "134, aviso" e "134, cenários".

- **134, aviso de pendência documental (#435):** a comissão aciona, na condução da convocação, *Avisar as pessoas com pendência nesta chamada*; o gesto grava um aviso da 066 por pessoa, com origem nova (`avisos/0002`), e o despacho o envia. É a quinta situação em que o sistema escreve (a FR-084 da 010 foi revista de quatro para cinco): o e-mail traz o nome publicado dos documentos pendentes, nunca o motivo, e o de modalidade vira "um documento da sua modalidade de concorrência". No máximo um por pessoa, por chamada, por dia; o despacho relê a pendência antes de enviar e interrompe se ela já não existe. A chave `AVISOS_AOS_CANDIDATOS` segue desligada em produção. A QI-7 deixou de ser pendência nas páginas que a citavam.
- **134, cenários de treinamento e homologação (#436, #438):** o app `treinamento`, quatro comandos de gestão e nenhuma tela. Cria quinze Processos fictícios, `SIM-TREINAMENTO-001` a `015`, parados em etapas diferentes, pelos mesmos comandos da aplicação; três barreiras (ambiente, chave `CENARIOS_DE_TREINAMENTO` e `--banco`). A #438 deu aos cenários de sorteio C06 e C07 a cota PPP. Uma seção nova, "Cenários de treinamento e homologação". Nada foi carregado na homologação compartilhada.
- **135, o andamento diz o que cada providência é (#440, #441):** quatro correções de linguagem da derivação da 127, sem regra nova: a ordem de uma lista em que ninguém concorre diz isso; o que foi divulgado do resultado vira dado; a espera do definitivo não oferece publicar como preliminar quando o preliminar já está publicado (a prévia e o comando mantêm a mensagem de antes); o resumo do Perfil conta "nos marcos".
- **136, o Centro de Controle do Edital (#442, #443):** página nova de leitura, que entrou em `/gestao/editais/<id>/centro/`, ao lado do detalhe, e que a 138 (#451) pôs na rota do Edital — a seção da Visão descreve os dois estados, com oito fases em três grupos, andamento separado do que cada fase oferece, uma ação em destaque por três regras e o detalhe da fase consultada. Em validação: nomes e textos provisórios.
- **139, a chegada ao ato e a volta (#447):** a providência leva ao lugar do ato por fragmento no endereço, e o bloco "Próximo nesta lista" termina em "Voltar ao Centro de Controle do Edital". Sem rota, regra ou migration.
- **140, a conferência antes de convocar (#448):** "Conferir e convocar as N" abre sempre a página "Confira antes de convocar", que não grava nada; só o botão dela pratica o ato, e o rótulo diz se mensagens saem.
- **141, a sucessora espera o reabilitado (#449):** a ordem sucessora e o corte são *Depois* enquanto a Etapa de quem um recurso reabilitou está por fazer; o Centro mostra a fase *Em curso*; a tela do corte avisa e o botão continua.
- **A tabela de revisões, o aviso de limites e o rodapé** apontam para `daba322f`.

Entraram também, sem mudar a descrição do sistema, o estudo do Centro de Controle (#439, `doc/estudo-centro-de-controle-2026-11-09/`), o estudo de continuidade operacional (#445 e #446, `doc/estudo-continuidade-operacional-2026-11-10/`), a correção de um teste que fixava uma data (#444) e a correção da Classificação com o método que espera a extração (#437).

**Corrigido no README:** a linha da 141 dizia "sem merge".

**Não verificado:**

- a suíte inteira não rodou aqui; rodaram os guardiões que leem `specs/` e `doc/`. Os números de teste e de consulta vêm do `verificacao.md` de cada spec, e nenhum mede a `main` com as sete entregas juntas;
- as telas não foram percorridas; os rótulos, as rotas e os códigos citados foram conferidos no código por três leituras paralelas, e as divergências entre spec e código foram resolvidas a favor do código;
- a *Maturidade* não foi recontada (migrations, rotas, módulos, testes), e as tabelas de estados não citam a espera da sucessora;
- ficam abertas a SC-1456 (um cenário percorrido só com o guia), a validação do Centro com operadores e as decisões 2 a 7 do estudo, a validação de LGPD e de SPF/DKIM do aviso, o texto da lista vazia da 135 sem teste no Centro, e as tarefas desmarcadas em `tasks.md` da 139 e da 140, cujas specs seguem como rascunho.

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

## Acréscimo de 10/11: as specs 142 e 143, e a 144 como Previsto

Entraram na `main`, que chegou a `b202a7c0`, duas specs implementadas (#452, #453) e uma só especificada (#454). Três leituras paralelas, uma por spec, conferiram no código os rótulos, as rotas e os códigos citados; onde spec e código divergiram, valeu o código.

- **142, a tela do sorteio como a jornada de quem o conduz (#452):** seção nova, *A tela do sorteio como a jornada de quem o conduz (142)*, em `#jornada-do-sorteio`, antes de *A extração inviável*. Quatro passos (*Fixar os participantes*, *Obter a semente pública*, *Realizar o sorteio*, *Consultar a ordem sorteada*), a marca *Agora* só para quem conduz, a auditoria sem formulário, a ordem sorteada pela primeira vez na tela de gestão, e as âncoras novas da ida pelo Centro. Os botões mudaram de rótulo: *Fixar os N participantes desta lista* e *Realizar o sorteio desta lista*. Nenhuma regra, migration, tabela ou permissão.
- **143, a convocação e a conferência documental pelas perguntas de quem conduz (#453):** seção nova, `#convocacao-pelas-perguntas`, ao fim de *Convocar como fluxo*. O índice *Neste recorte, agora*, as vagas separadas da apuração e das chamadas praticadas, as três áreas, o passo e a situação do aviso por chamada, e a página dos documentos com a pessoa seguinte. Só leitura: o passo e a situação do aviso são derivados, e nunca gravados.
- **144, o Cronograma (#454):** *Previsto*, em `#cronograma-pdf-ordem-previa`, dentro da página do Cronograma. Só a especificação foi mergeada: ocultar o Evento da tabela do PDF, ordenar por data de início e uma prévia compacta. Nada foi implementado, e as seções que listam os campos do passo não mudaram.
- **Corrigido na Visão:** os rótulos dos botões do sorteio em cinco lugares (o rito, *A extração inviável*, os cenários de treinamento, a lista de atos sem conferência e a ida da 139); a frase da 127 que dizia que abrir uma tela não paga a derivação, que a tela do sorteio deixou de cumprir; a ordem dos dois avisos da convocação em *O aviso de pendência*; a lacuna desse aviso, que a 143 percorreu no navegador; os arquivos de evidência da tela da convocação.
- **Corrigido no README:** as linhas da 138, da 141, da 142 e da 143 já diziam "mergeada" pela #450; a da 144 dizia "PR sem merge".

**Não verificado:**

- a suíte inteira não rodou aqui; rodaram os guardiões que leem `specs/` e `doc/`. Os números de teste vêm do `verificacao.md` de cada spec, e nenhum mede a `main` com as três entregas juntas; a 143 não registra a suíte inteira depois das correções da revisão;
- as telas não foram percorridas, e a *Maturidade* não foi recontada;
- ficam abertas a conferência em dois passos do congelamento do sorteio, a observação da semente antes de fixar a primeira lista, o aviso da 143 de que a providência de conferir documentos leva ao título e não à primeira chamada, e a decisão de passar a chamada individual pela conferência da 140.

## Acréscimo de 10/11: o incremento A da 144, a visibilidade do Evento no PDF

Entraram na `main`, que chegou a `d184fcee`, o incremento A da 144 (#456) e um ajuste de largura do Cronograma (#457). Leitura direta do código, sem agentes: o olho, a Revisão, a numeração do PDF e a regra de omissão da seção foram conferidos nos arquivos.

- **144, incremento A (#456):** a seção `#cronograma-pdf-ordem-previa` deixou de ser só *Previsto*. Descreve como *Implementado* o olho **Ocultar do PDF**, a marca *Oculto do PDF*, o efeito no PDF (numeração de 1 a k, a remissão do período que some, a seção que não sai com todos ocultos), a frase da Revisão, a visibilidade retificável (e o Evento acrescentado por Retificação nasce exibido), os seis outros canais que continuam mostrando todos os Eventos e o custo, `editais/0026` e o degrau 20 da versão canônica. A ordenação por data (B) e a prévia (C) seguem como *Previsto*.
- **#457:** só a folha do Cronograma (datas na largura do controle, o Evento numa linha a 1.600 px); citado na lacuna, sem seção própria.
- **Corrigido na Visão:** a ficha do Cronograma (*Na interface*), o tutorial *Montar o cronograma*, a tabela *Cronograma e inscrição* e a linha da Retificação em *Cronograma e Etapas*, que não diziam nada do olho nem da visibilidade retificável.

**Não verificado:**

- a suíte inteira não rodou aqui; rodaram os guardiões que leem `specs/` e `doc/`. O número de testes vem do `verificacao.md` da spec, que registra 17.923 passando e 3 falhas corrigidas, sem repetir a suíte inteira;
- a tela não foi percorrida, e a *Maturidade* não foi recontada;
- ficam abertos o Cronograma a 375 px, o rótulo *“(vazia — não sai no documento)”* da etapa Conteúdo com todos os Eventos ocultos, e os incrementos B e C.

## Acréscimo de 11/11: o sorteio no cartão da vaga (145) e o barema da Etapa (146)

Entraram na `main`, que chegou a `04797399`, a 145 (#459) e a 146 inteira: a spec (#460) e os incrementos A (#461), B (#462) e C (#463). Leitura das specs e do código, sem agentes.

- **145:** nova seção `#sorteio-no-cartao-da-vaga`, dentro do Sorteio. O sorteio de cada vaga passou para o cartão dela na página pública do Edital (estado dito uma vez por marco, acesso à relação, verificação depois do sorteio, controle de abrir com duas ou mais listas); o bloco *Sorteio público* ficou com o andamento do Edital. Corrigidos a linha *Sorteio público* e a linha *Vagas* de *O que a página pública do Edital mostra*, a pergunta *Há link público?* e a tabela *O que é público, e onde*.
- **146:** nova seção `#barema-da-etapa`, dentro de *A Etapa de Avaliação*, com as regras (`#barema-regras`), a Mesa com a ficha (`#barema-na-mesa`) e o recurso contra nota com barema (`#recurso-com-barema`). Registra o que não faz e o que espera validação institucional (P-1 a P-7), e que **só vale a ficha de critérios independentes** — o Edital que exija “só o maior título” não é atendido.
- **Corrigidas as frases que diziam que o barema não existe:** a Receita 4 (*Limites*), a tabela de famílias do alvo, a nota do custo da Mesa, as linhas do catálogo e de *Lacunas antigas*, a lista do que o sistema ainda não faz, a síntese do certame, DP-10 e a lista do que não criar. Atualizados o cartão da Etapa, a tabela *O que uma Etapa declara* (linha *Barema*), a Mesa (*Na interface*) e a tabela das espécies de decisão do recurso.
- **Fora do que a spec diz:** a Visão afirma só o que o código mostra — os rótulos são os dos templates, e a ficha vira cartões em espaço estreito, como a folha dela declara.

**Não verificado:**

- a suíte inteira não rodou aqui; rodaram os guardiões que leem `specs/` e `doc/`, e a Visão passou pela conferência de ids, links e tags;
- nenhuma tela foi percorrida; a jornada do barema no navegador está registrada em `specs/146-barema-da-etapa/capturas/jornada/`;
- ficam abertos a medida de tempo da Mesa com o barema, a confirmação com a CPS/Cefor de que os títulos de cada Edital se pontuam independentemente (P-1), e as sete questões da spec;
- as seções `#cronograma-pdf-ordem-previa` (144, B e C) e as demais pendências anteriores não mudaram.

## Acréscimo de 13/11: as specs 147 a 161

Entraram na `main`, que chegou a `60f9ff24`, as implementações da 147, 148, 149, 150, 152 (parcial), 153, 154 (parcial), 155 (entrega mínima), 157, 159 e 160, as specs 156, 158 e 161, a designação pela presidência (117, D-025) e as frentes de trabalho dos cenários (134). Leitura das specs, dos corpos dos PRs e do código, em quatro frentes que escreveram fichas de fatos (gestão e treino; publicações; a convocação do candidato e da conferência; atos irreversíveis, vaga sem ocupante e passagem ao setor); os rótulos são os dos templates.

- **Novas seções:** `#pagina-do-processo` (147, reescreve o h3 que descrevia a página antiga), `#minhas-atividades` (160) e `#quem-faz-o-que` (161, Previsto), `#publicacao-das-inscricoes` (148), `#publicacao-das-convocacoes` (149 e 159), `#conferencia-nos-atos-irreversiveis` (152, Parcial), `#conferencia-com-o-documento-a-vista` (157), `#envio-de-varios-documentos` (150), `#convocacao-depois-do-envio` (154, Parcial), `#desfecho-comunicado` (156, Previsto), `#passagem-ao-setor` (153), `#vaga-sem-ocupante` (155, Parcial) e `#passagem-entre-cotas` (158, Previsto).
- **Corrigido:** o rótulo *Minhas Etapas*, que virou *Minhas atividades* em 21 pontos (a descrição histórica de 16/10 ficou); a página do Processo antiga e o botão *Novo Edital neste Processo*; a tabela *por publicação — não publica*, os rótulos do botão de convocar e as frases do aviso de pendência; a lacuna do botão *Pedir a faixa seguinte* (corrigida pelo #477); a frase de *Sair* do portal; a designação para a formalização (a presidência também designa, D-025) e a frase de que a demonstração não a alcança; os cenários (17, não 15, com C16 e C17 e a exceção ao “o gerador não cria papel”); e a contagem de tabelas append-only (53 para 59).
- **Previsto, e dito como previsto:** a frase de conclusão da 154 (US2), a ciência do prazo da 152 (história 2), tudo o que a 155 deixou de fora (a destinação por ato próprio, a reversão por saldo — bloqueada pela D-015) e, inteiras, a 156, a 158 e a 161.
- **README:** as linhas de 147, 149, 150, 152, 153, 154, 155, 157, 158, 159, 160 e 161 passaram a dizer o que foi mergeado e o número do PR; as de 150, 152, 154 e 157 estavam defasadas em relação ao código.

**Não verificado:**

- a suíte inteira não rodou; rodaram os guardiões que leem `specs/` e `doc/`, e a Visão passou pela conferência de ids, links e tags;
- nenhuma tela foi percorrida; a validação humana de 149, 150, 157, 159 e 160 (SC-1805, SC-2149 a SC-2151, SC-2159, SC-2281) segue aberta;
- o seletor de demonstração oferece a presidência sem os cenários? a designação pela presidência vem do vínculo com a comissão, e não de um papel do seletor;
- em que grupo do Centro de Controle aparece a Ação *Publicações das inscrições*;
- a contagem de 83 gatilhos e 67 tabelas no resumo do provisionamento é de quando as append-only eram 53; não foi recontada;
- as specs 149 e 159 ainda dizem *Em implementação*, a 134 ainda diz *sem merge* e o `tasks.md` da 160 deixa T002, T036 e T037 sem marca, embora mergeadas.

## Acréscimo de 13/11: a vitrine separa em andamento de encerrado, e pagina (PRs 524 e 526)

O PR 524 entrou na `main` (`e815aeb5`) com a paginação das encerradas e a ordem da mais recente para a mais antiga. O PR 526, onde este acréscimo viaja, sobre a `main` em `26748113`, separa o grupo em dois. Nenhum dos dois tem spec: foram pedidos como correção e polimento da vitrine.

- **Novo trecho:** `#vitrine-em-andamento-e-paginas`, no passo *1 · Descoberta* da jornada do candidato — os cinco grupos, a regra do desfecho, a etiqueta, a ordem de cada grupo e a paginação.
- **Corrigido:** a lista dos grupos, que dizia quatro e nomeava *Inscrições encerradas*; a linha *Situação* da página pública do Edital, que não dizia a etiqueta; o parágrafo do cartão, que ganhou o pé alinhado e o corte do título.
- **Lacuna registrada:** *Seleções encerradas* só enche quando a gestão encerra o Edital por ato; e a mudança contraria a 024 (quatro grupos, FR-146) e a 047 (o desfecho não seria um quinto, FR-763) sem spec nova.

**Como foi conferido:** rótulos lidos no código (`portal/leitura.py`: `GRUPOS`, `MARCA_EM_ANDAMENTO`, `estado_na_vitrine`; `vitrine.html`, `_paginacao.html`, `_consulta.html`); a tela percorrida no navegador em 390 e 1280 px, num banco de demonstração com 6 seleções abertas, 27 em andamento e 1 encerrada.

**Não verificado:**

- a suíte inteira não rodou; rodaram `tests/unit`, o portal, a interface, os contratos, a aceitação, o kit e as publicações contra PostgreSQL (13 201 passando, 2 pulados);
- quantos Editais reais têm o ato de encerramento — é o que decide o tamanho do grupo *Em andamento*;
- os números de *Maturidade* não foram recontados;
- a volta da página do Edital abre a página certa da vitrine, mas no topo, sem a âncora da lista.

## Acréscimo de 13/11: a seção "O que ainda precisa evoluir" refeita

A seção listava o que faltava em 20/09, e crescera por camadas de datas. Em 13/11, sobre a `main` em `95904252`, os 186 itens que ela trazia foram conferidos de novo no código, nas specs e no histórico, e a seção foi reescrita em quatro grupos, pelo que pode fechá-los.

- **Placar:** 29 resolvidos, 20 parciais, 69 abertos no código, 68 que dependem de decisão, validação ou terceiros. O placar de 28/09 (160 unidades, 69 abertas, duas de grupo A) saiu.
- **Novos trechos:** `#evolucoes-placar`, `#evolucoes-codigo` (bloqueia a produção, atrapalha quem opera, polimento, sem impacto hoje), `#evolucoes-decisoes`, `#evolucoes-validacao`, `#evolucoes-externo` (com quem bloqueia a produção), `#evolucoes-resolvidas` e `#evolucoes-higiene`. Os ids `#abertas-desde-*` e `#evolucoes-revistas`, `#evolucoes-novas` saíram; os dois links que os usavam foram repontados.
- **Saíram por terem fechado:** as famílias do Kit (hoje oito), a janela de impasse da 113, a A-03, os `pessoa-<uuid>` dos históricos, as duas grafias do desfecho no portal (156), o texto do `CR` do portal, a sucessão da convocação (120), "qual Edital precisa de atenção" (147), o aviso de pendência por e-mail (134).
- **Entraram:** a apuração da ocupação, que tem sete causas de obsolescência e nenhuma de reversão; a história 2 da 152 (ciência do prazo), não entregue; o papel Comunicação atribuível antes da 112 (0 de 35 tarefas); a vaga de cota sem concorrente (155) só com a entrega mínima; 73 specs em `Draft`, eram 67 de 114.

**Como foi conferido:** leitura do código, das specs e do histórico por quatro frentes, e releitura minha dos itens de maior peso (o adaptador de autenticação, o papel Comunicação e a 112, as causas de obsolescência, a contagem de `Draft`). Os guardiões de documentação rodaram.

**Não verificado:**

- a suíte não rodou e nenhuma tela foi percorrida;
- o número atual de consultas do acompanhamento por publicação;
- se a *"Tabela N"* renumerada numa Retificação é acusada;
- as três grafias dos rótulos da Retificação e o Perfil no nível do marco do caminho do topo;
- as lacunas L-2 e L-4 a L-7 da 063, uma a uma;
- o ponto exato em que a falta de autoridade vigente recusa a publicação;
- o item *"cadastro de reserva limitado em N"* sem regra, e o de a Retificação da reversão ser mesmo uma causa ausente: vêm das fichas da conferência, sem releitura minha;
- os números do bloco *Estado atual* (pastas, tabelas, gatilhos, rotas) não foram recontados: continuam os da revisão de 02/11.

## Acréscimo de 13/11: dois itens de polimento corrigidos

Dois itens de *Polimento que se vê na tela*, ambos registrados como de correção curta, foram corrigidos e passaram a *O que já fechou*. O placar de 13/11 não mudou: os dois fecharam depois da conferência.

- **“Retificaçãoões”** (desde 30/10). O título da tela Retificar acrescentava `pluralize:"ões"` à palavra no singular. Agora o plural troca a palavra inteira (`retificar.html`). Um teste abre a tela com duas Retificações em curso (`test_jornada_da_retificacao.py`). A nota em *O que a 103 deixou aberto* saiu.
- **Os links para o repositório** (desde 02/11). Eram 59, e não 58: 54 para `backend/`, 3 para `specs/`, mais `AGENTS.md` e `.specify`. Apontam agora para `https://github.com/vitofranzosi/processo_seletivo` (`blob/main/…`, e `tree/main/…` para a pasta de contratos da 031), e valem tanto com a página aberta do disco quanto em `/gestao/documentacao/`. A lista literal da 105 (D-002) não mudou: servir o repositório pela gestão era justamente o que ela recusa. Um guardião novo (`test_documentacao_do_sistema.py`) recusa link relativo que não seja âncora, o voltar à gestão ou arquivo da lista.

- **Na revisão do PR**, dois acréscimos:
  - **O mesmo defeito noutra tela.** `_perfis_do_edital.html` tinha `pluralize:"m,"`, o que punha *pertencem* no singular e *pertence* no plural desde que a tela existe. Foi corrigido, e uma varredura nova (`tests/test_plural_dos_templates.py`) recusa nos templates o plural vazio e os sufixos que trocam a terminação (`ões`, `ães`, `is`) colados ao singular.
  - **Os links conferidos.** Os links apontam para a `main`, e não para o commit que a página descreve. Por isso um guardião confere que cada `blob/main/…` é arquivo e cada `tree/main/…` é pasta na árvore do próprio PR: mover um arquivo citado sem acertar o manual reprova a suíte.

**Não verificado:** a tela dos Perfis com inscrições de Perfil retirado não foi aberta no navegador. A correção foi conferida no filtro do Django.

## Revisão de 13/11: a visão do produto consolidada

Base: `main` em `214c8cd7`. A pergunta desta revisão foi outra: não *"o que entrou desde a última?"*, mas *"um novo integrante entende o GPS lendo esta página?"*.

### O diagnóstico

A página vinha sendo mantida spec a spec, e o conteúdo de referência estava em dia até a 161. O que envelhecia era a camada de entrada.

- **O Início era um portal, e não uma visão.** Tinha a ideia dos atos, o fluxo e doze conceitos. Não dizia por que o sistema existe, para quem, sob quais princípios, nem como a gestão e o portal se ligam.
- **Os números do Início eram de 02/11:** 114 pastas, 53 append-only, 14 638 testes. Contradiziam a própria página, que noutro lugar dizia 59 tabelas e 17 698 testes.
- **A trilha do topo parava em 02/11** (105–113).
- **O nome do produto não era o das telas.** O título, a marca e o rodapé diziam *"Processos Seletivos e Editais"*, e as telas dizem *GPS — Gestão de Processos Seletivos* desde a 075.
- **O fluxo geral e o mapa paravam no Requerimento.** Faltavam a publicação das inscrições (148), os documentos e a conferência na convocação (115, 157), a entrega à formalização (117), a publicação das convocações (149) e o encerramento. Os cartões de recursos não tinham o Centro de Controle, Minhas atividades nem as conferências.
- **A 156 estava como Previsto, com "nada dela está no código".** Os PRs 525, 529 e 533 levaram três histórias (US2, US3, US8). Também ficou aberta, em *Falta código*, a lacuna da mensagem de reenvio, que o 533 fechou.
- **O veredito era um diário** (*"Em 02/11… Em 15/10, nada mudou…"*), e não um estado.
- **A Maturidade mostrava números de duas datas,** apresentados como *"contra os de 30/10"*.
- **Duas contradições internas:**
  - a seção dos e-mails dizia *"além do código de acesso, cinco situações"*, mas o guardião (`test_situacoes_de_mensagem.py`) conta o código como uma das cinco;
  - *Para quem for atualizar* dizia que só um teste lê esta pasta, e são dois.
- **A tabela de revisões estava fora de ordem** (05/11 e 06/11 depois de 13/11).

### O que mudou

O Início foi reescrito como a visão do produto, mantendo as âncoras antigas:

- `#inicio`, `#fluxo-geral`, `#fundamentos`, `#recursos-disponiveis`, `#estado-atual` e `#perspectivas` continuam valendo;
- entraram `#proposta`, `#publicos`, `#principios`, `#jornadas`, `#governanca`, `#transparencia` e `#referencias`;
- o Início deixou de ter contagens: elas ficam só na Maturidade.

Fora do Início:

- a 156 passou a Parcial, com o que entrou e o que falta (18 de 54 tarefas), e a frase da área do candidato que ainda dizia *"Resultado registrado: … — {fundamento}"* foi acertada;
- a lacuna da mensagem de reenvio foi para *O que já fechou*;
- as contagens da Maturidade foram refeitas pelo método da página;
  - o método reproduz em `a3e23b1f` todos os números publicados em 04/11, menos as pastas de spec (120, e a página dizia 114);
  - hoje são 162 pastas, 59 append-only, 91 gatilhos em 36 migrations sobre 73 tabelas, 118 migrations, 24 módulos, 580 arquivos Python, 259 templates, 1 220 + 25 arquivos de teste e 180 + 42 rotas;
- o veredito foi reescrito como estado presente;
- o mapa em texto ganhou a unidade, os documentos da convocação e a formalização, e a tabela de conceitos ganhou Unidade, Documento da convocação e Entrega à formalização;
- *Sobre esta documentação* ganhou o papel do Início e *Quando a visão precisa mudar*: três perguntas ao fechar uma entrega;
- a tabela de revisões foi posta em ordem;
- o título da aba, que o roteador (`assets/app.js`) reescreve a cada página, passou a dizer *GPS · Gestão de Processos Seletivos*.

**Preservado:** todo o conteúdo de referência (Aprender a operar e Consultar), *O que ainda precisa evoluir*, a auditoria de consistência, os selos e o método.

### Como os fatos foram conferidos

Os fatos novos do Início foram conferidos no código por duas leituras paralelas:

- a navegação, a Lista, a página do Processo, o Centro de Controle, Minhas atividades, as conferências e as publicações;
- o portal, os e-mails, a identidade, os papéis, as integrações e as contagens.

As 156, 158, 161, 123 e 144 B/C foram procuradas pelas FRs e pelos textos. Delas, só a 156 tem código.

**Não verificado:**

- a suíte não rodou: só os guardiões que leem esta página;
- nenhuma tela foi percorrida;
- a repartição dos 91 gatilhos por espécie não foi refeita.

## Acréscimo de 13/11: a lista na gestão (#534) e o resto do reenvio (#533)

O #534 fechou um item de *Atrapalha quem opera*, e a consolidação da Visão (#535) já tinha levado o item da mensagem da convocação (#533) a *O que já fechou*. O placar de 13/11 não mudou: eles fecharam depois da conferência.

- **A lista, na gestão** (#534). A prévia de publicação nomeia a lista e o histórico *Resultados divulgados* ganhou a coluna *Lista*. O aviso da seção *Resultado* e a linha da matriz passaram de *Parcial* a *Implementado*. A frase *"Este marco ainda não pode ser publicado como definitivo"* ficou como estava, de propósito.
- **O resto do reenvio.** A #535 tirou o item inteiro do grupo 1, mas o achado tem uma segunda oportunidade aberta: o cartão da convocação mostra só o último envio, e as frases do portal que dizem *"contado do envio da comunicação"* (FR-3998 da 125) ficaram fora da 156 de propósito. O item voltou ao grupo 1 com esse resto.

**Não verificado:** as telas não foram abertas, e a suíte não rodou; a leitura é dos corpos dos PRs e do código.

## Acréscimo de 13/11: a 162, o limite do cadastro de reserva lido do corte

A spec 162 viaja no PR #537, sobre a `main` em `84cbeeb5`, e esta atualização vai junto, no mesmo PR: a página passa a descrever a `main` quando ele for mergeado. O número do cadastro de reserva limitado deixa de ser digitado e passa a ser o que o corte do marco que convoca alcança além das vagas, por lista.

- **Reescrito:** `#cadastro-de-reserva` — a frase, o exemplo, o que se pode e o que não se pode, a nova subseção *De onde vem o número*, a tabela *Onde ele aparece* (agora com a Retificação), o aviso dos Editais publicados antes da 162 e o porquê do selo, que continua *Parcial*: a convocação sem vaga imediata segue só na ampla sem Modalidade (097).
- **O tutorial:** o INF-VIT passa a ter o cadastro limitado *pelo corte* — 10 suplentes por lista, **sem** continuação. Com a continuação do exemplo anterior, a publicação recusaria. Mudaram o resumo do exemplo, o passo 4 (a opção limitada sem número e o aviso *O número do cadastro vem do corte*), o passo 8 (*Faixa seguinte* em *Não admite*) e a lista do que impede publicar.
- **Corrigido:** a Receita 7 (que mandava "manter os dois iguais — nada os confere"); as tabelas de configuração e de capacidades (*limitar o cadastro de reserva a N* virou ✓); *Alterei o cadastro de reserva*, que perdeu a lacuna da espécie × limite na Retificação (o campo só existe no Perfil legado, e o Perfil acrescentado nasce sem ele); o exemplo do conceito Perfil e a árvore de configuração; a tabela de campos; os campos da Retificação; as duas perguntas e o glossário; o histórico de achados (096 e 097); os *Campos gravados que nenhuma regra lê* (o `reserveLimit` saiu da lista); a nota do `CR` em zero; e o exemplo do selo *Implementado, não operacionalizado*, que era o limite do cadastro.
- **Placar:** o item *O limite do cadastro de reserva não é aplicado* saiu do grupo 1 e foi para *O que já fechou*: 30 resolvidos e 68 abertos no código (eram 29 e 69). As pastas de spec passaram a 163, e 160 têm a linha de `Status`.

**Como foi conferido:** as frases e os rótulos vêm do código da branch (`editais/domain/cadastro_de_reserva.py`, `publicacoes/infrastructure/pdf.py`, `interface/templates/interface/_perfil.html`, as recusas de `incoerencias`); a suíte inteira rodou contra PostgreSQL (19 564 passando, 24 pulados); a página passou pelos guardiões de documentação.

**Não verificado:**

- nenhuma tela foi percorrida, e o roteiro manual da 162 (T046) não rodou;
- os números de *Maturidade* não foram recontados: o selo do cadastro de reserva não mudou, e a tabela de capacidades ganhou um ✓;
- o SC-2304, humano, segue aberto.
