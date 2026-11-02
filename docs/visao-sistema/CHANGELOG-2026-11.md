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
