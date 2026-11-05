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

Feita na hora do merge, a pedido de 04/11 ("quando for feito o PR, atualize a documentação do sistema"), sobre a `main` em `7a4f7aec`. Cobre o que entrou nesse dia: a spec 120 (PR #385) e os incrementos 3a, FIC (PR #387), 3d, Aperfeiçoamento (PR #389), e 3c, UAB/bolsista (PR #386), da 119.

## Como foi conferido

- **Leitura direta**, sem leituras paralelas: a spec, a verificação e as decisões da 120; o parcial `_correcao_da_convocacao.html`, `convocar.py` e `fluxo.py` para os rótulos e para o lugar onde cada conferência mora; os módulos `kit_familias/fic.py`, `uab.py` e `aperfeicoamento.py`, as referências em `kit_referencias/` e as settings para as famílias.
- **A suíte rodou contra PostgreSQL** sobre a árvore que virou a `main` (a integração local dos três PRs, idêntica a `9a459a0e`): 16 136 passando, 18 pulados e nenhuma falha (4 workers, 729 s, com o grupo `assistente` e sem o `navegador`). O 18º pulado é a jornada da 120 no navegador. A UAB entrou depois, sobre essa mesma `main`, com o CI verde no PR (a suíte inteira contra PostgreSQL).

## O que mudou na documentação

- **Convocação:** a lacuna *"corrigir uma convocação não tem tela"* deu lugar à subseção *Corrigir uma convocação em aberto, e dar mais prazo* (`#correcao-da-convocacao`), com a prévia no formulário, o motivo e o vencimento obrigatórios, a assinatura conferida sob a trava, a recusa que volta ao cartão, o impedimento pela apuração superada e o que fica fora por decisão. O aviso *Um prazo só por chamada* aponta para ela.
- **Matriz de capacidades:** a linha *Corrigir convocação ou suceder desfecho* (não operacionalizado) virou duas. *Corrigir convocação em aberto* está implementado. *Suceder desfecho registrado* continua não operacionalizado.
- **Pendências:** a linha da convocação ganhou a correção. Fica a sucessão do desfecho e a chamada sem vencimento.
- **Kit:** a tabela de templates ganhou os nove da FIC, da UAB e da Aperfeiçoamento, e a seção ganhou um parágrafo por família. *O que ainda falta* passou a três famílias: Libras, Internos e TMD. A matriz diz 4 das 7, e as pendências foram atualizadas.
- **Testes, revisões e rodapé:** a linha da suíte foi atualizada, e a tabela de revisões, o *Onde esta documentação não alcança* e o rodapé ganharam a entrada de 05/11.

## O que não foi verificado, e o que ficou de fora

- **O produto não foi percorrido.** A jornada da 120 no navegador não rodou aqui; a verificação dela é a do PR (4 de 4, com capturas em `specs/120-…/capturas/`).
- **Maturidade não foi recontada:** os números de arquivos, *templates* e testes são os de 04/11. A 120 não acrescenta tabela, gatilho, migration nem rota.
- **A UAB (PR #386) entrou por último.** Integrada depois da FIC, ela reprovava 23 testes do kit: a FIC passou a usar no motor a caixa tipográfica da fonte como altura mínima da linha (`kit_peca.entrelinha`), e a Anton mede 1,5 corpo. A sessão da UAB refez as caixas com a altura nova e regenerou as referências e os resumos, sem tocar nas das outras famílias, e o PR foi mergeado com o CI verde.
- **A spec 120 ainda diz** *"Draft, só documental"* no cabeçalho, embora a implementação tenha entrado no mesmo PR.
