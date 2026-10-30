# Revisão de 30/10/2026 da Visão do Sistema

A documentação descrevia o sistema até a spec 097 (21/10). Desde então entraram na `main` sete specs,
entre 21 e 30/10, e o PR 335: a prévia do sorteio com semente fictícia (098), o relatório do Edital (099)
e o consolidado da unidade (100), a Agenda dos Editais (101), a extração do sorteio inviável impedida na
publicação (102), a Retificação em curso pela navegação comum (103) e as ações disponíveis no topo da
Lista (104). Algumas frases ficaram falsas: a prévia que *“não simula o sorteio”*, na seção da prévia,
na pergunta frequente e na maturidade; a Retificação devolvida que *“não se edita pela tela”*, na ficha,
na lacuna, no catálogo e na lista de evoluções; e a linha de *Auditoria* da maturidade, que ainda dizia
40 tabelas e 58 gatilhos. Esta revisão descreve tudo isso contra a `main` em `62824816`.

## Como foi conferido

- Três leituras paralelas confrontaram as specs com o código da `main`, e não só com a própria spec:
  098 e 102 com o PR 335; 099 e 100 com os PRs 332 a 334; e 101, 103 e 104. Onde spec e código
  divergiam, valeu o código. Os rótulos citados foram conferidos de novo no código antes de entrar no
  texto, entre eles:
  - `_marco.html` (*Simular sorteio*), `_previa_do_sorteio.html`, `_semente_ficticia.html` e
    `RODADAS` em `sorteios/application/simulacao.py`;
  - `EXTRACAO_INVIAVEL` e `EXTRACAO_INVIAVEL_NA_RETIFICACAO` em `editais/domain/validation.py`, os
    avisos de `sorteio.html` e a *Fonte de demonstração (só a data)* em `sorteios/infrastructure/fontes/`;
  - `INDISPONIVEL` em `interface/relatorio.py`, `MINIMO_PARA_DETALHAR` e as três espécies em
    `interface/relatorio_do_edital.py`, e o critério do conjunto em `relatorio_consolidado_escolha.html`;
  - a seção *Agenda* em `interface/navegacao.py`;
  - os itens da faixa em `interface/trabalho.py` e `interface/atos_retificacao.py`,
    `_acoes_disponiveis.html`, *Retificações em curso* em `detalhe.html` e *Editar a Retificação* em
    `retificacao_detalhe.html`.
- Os números de *Maturidade* foram recontados pelo método da própria página. Rodado sobre `e869d7a2`, a
  base da revisão de 21/10, ele reproduz todos os números publicados naquela data.
- **Não se rodou a suíte nem se percorreu o produto.** O total da suíte (12 775 passando, 12 pulados)
  continua o de 21/10, e a página diz agora que ele não inclui os testes das sete specs. Nenhum teste lê
  `docs/`.
- A própria página foi aberta no navegador pela entrada `visao-do-sistema` do `.claude/launch.json`
  (porta 8090). Todas as âncoras internas têm destino, nenhum `id` se repete, e o HTML fecha as tags que
  abre.

## O que mudou na documentação

- **A prévia do sorteio (098).** Entrou a subseção *A prévia do sorteio, com semente fictícia*
  (`#previa-do-sorteio`), dentro de *Simular a classificação antes de publicar*. Ela traz:
  - o botão *Simular sorteio*, a semente fictícia e o que a troca;
  - a população por lista, a ordem de cada lista e a ocupação;
  - o resumo de 1.000 rodadas, como hipótese.

  *“O sorteio”* saiu do que a prévia não simula, e a pergunta frequente, a maturidade e o catálogo
  passaram a dizê-lo.
- **A extração inviável (102, PR 335).** Entrou a subseção *A extração inviável: impedida na publicação,
  avisada antes de congelar* (`#sorteio-viavel`), em *O rito, passo a passo*. Ela traz:
  - o impeditivo de publicação;
  - a advertência na Retificação;
  - o aviso da tela do sorteio;
  - a recusa que diz a saída, no fuso da tela;
  - a granularidade declarada por fonte.

  *Quando pode ser aplicado?*, o aviso *Congele antes do dia da extração* (que passou a valer também
  para a relação sucessora), a Receita 1 e as fontes de demonstração apontam para ela.
- **A Retificação em curso (103).** Entrou *Encontrar e retomar a Retificação em curso*
  (`#retificacao-em-curso`), em *Retificação*. Ela traz:
  - as portas da Retificação ainda não publicada;
  - quem age a seguir;
  - a edição da devolvida no mesmo registro;
  - a segregação mostrada antes do clique.

  A lacuna *a Retificação devolvida não se edita pela tela* virou *reapontar a Retificação para a versão
  vigente*, que continua só pela API. A ficha, o catálogo, *Interface ausente* e o *Não confunda* de
  *Publicação ≠ Retificação* foram acertados. A confirmação de homologar (104) entrou no passo do rito.
- **Ações disponíveis, Agenda e relatórios (104, 101, 099, 100).** *Acompanhar e operar em escala*
  ganhou quatro seções:
  - *Ações disponíveis para você* (`#acoes-disponiveis`);
  - *A Agenda dos Editais* (`#agenda`, com a ficha `#c-agenda`);
  - *O relatório do Edital* (`#relatorio-do-edital`, com a ficha `#c-relatorio-do-edital`);
  - *O relatório consolidado da unidade* (`#relatorio-consolidado`), com selo *Parcial*, porque não
    tem autorização de produção.

  A Visão Geral aponta para o consolidado. A barra da gestão, a matriz de permissões (três linhas), *Onde
  fica cada coisa* (quatro linhas), *Dados pessoais*, os cartões de *Recursos disponíveis* e de
  *Navegação por perspectiva* passaram a mencioná-los.
- **Estado do produto:**
  - 105 pastas de especificação, 461 arquivos Python de aplicação (117,0 mil linhas), 185 templates,
    944 + 16 arquivos de teste e 128 + 36 rotas; tabelas append-only, gatilhos, migrations, módulos e
    espécies de sinal não mudaram;
  - 66 das 105 specs dizem `Draft`, agora também a 100, a 101 e a 102; a 099, a 103 e a 104 dizem que o
    merge não foi feito ou não foi autorizado;
  - *Fechados desde 20/09* ganhou três linhas: a Retificação em curso sem porta, a extração no dia do fim
    das inscrições e a coluna que negava ação ao lado da Retificação;
  - entrou a subseção *Abertas desde 21/10* (`#abertas-desde-21-10`), com seis itens: as sete validações
    com pessoas, a lista reservada vazia que não reverte, as decisões deixadas ao usuário, o consolidado
    sem autorização de produção, o título *“Retificaçãoões”* e as specs que não acompanharam o merge;
  - a maturidade ganhou duas linhas, *Ações disponíveis e Agenda* e *Relatórios gerenciais*, e a de
    *Auditoria* passou a dizer 41 tabelas e 59 gatilhos.
- **Catálogo e glossário.** O catálogo passou de 134 a 141 capacidades, e o glossário de 121 a 126
  termos: *Ações disponíveis*, *Agenda dos Editais*, *Relatório consolidado*, *Relatório do Edital* e
  *Semente fictícia*.
- **Âncoras.** Nenhuma foi removida. As novas são `#previa-do-sorteio`, `#sorteio-viavel`,
  `#retificacao-em-curso`, `#acoes-disponiveis`, `#agenda`, `#c-agenda`, `#relatorio-do-edital`,
  `#c-relatorio-do-edital`, `#relatorio-consolidado`, `#abertas-desde-21-10` e as dos cinco termos do
  glossário.
- **README.** As linhas da 100 à 104 deixaram de dizer que o merge não foi autorizado; a da 100 mantém
  que a produção não foi autorizada.

## O que não foi verificado, e o que ficou de fora

- Nada foi percorrido no produto. Os rótulos vêm dos *templates* e do código, e o comportamento, das
  views e dos testes.
- As sete specs aparecem como entregues, e não como validadas: todas dizem que a validação com pessoas
  só fecha com o relato do usuário.
- Um defeito encontrado nesta revisão foi registrado, e não corrigido: com duas ou mais Retificações em
  curso, o título da tela Retificar sai *“Retificaçãoões”* (`retificar.html`, linha 27).
- O manual (`doc/manual/`) não foi tocado: a Revisão 6, de 15/10, cobre até a 072, e uma Revisão 7 é
  decisão do usuário.

# Revisão de 21/10/2026 da Visão do Sistema

A documentação descrevia o sistema até a spec 092 (19/10). Desde então entraram na `main` cinco specs,
entre 20 e 21/10: a recusa do formulário expirado na moldura da área (093), a prévia da classificação
na composição (094) e por recorte (095), o Perfil só de cadastro de reserva impresso como `CR` (096) e a
vaga acrescida depois da publicação, que convoca do cadastro de reserva (097). Algumas frases ficaram
falsas: a página de falha de CSRF *“sem desenho”*, registrada como aberta; o cadastro de reserva
*“sem execução”* e o Perfil só de reserva que *“não convoca pelo sistema”*, repetidos pela página inteira;
e a advertência da Revisão, cuja frase a 097 trocou. Esta revisão descreve tudo isso contra a `main`
em `e869d7a2`. A 097 já tinha acertado, no próprio PR, as duas definições de *Cadastro de reserva* em
*Comece por aqui* e *Antes de começar*; elas não foram duplicadas, e só o selo mudou de cor.

## Como foi conferido

- Quatro leituras paralelas, uma por spec da 094 à 097, confrontaram cada spec com o código da `main`,
  e não só com a própria spec; a 093 foi lida diretamente. Onde spec e código divergiam, valeu o código.
  Os rótulos citados foram conferidos de novo no código antes de entrar no texto, entre eles:
  - `falha_de_csrf` em `interface/erros.py` e o `CSRF_FAILURE_VIEW` em `config/settings/base.py`;
  - `_marco.html`, `_previa_da_classificacao.html`, `_ocupacao_da_previa.html` e
    `interface/previa_da_classificacao.py`;
  - `ROTULO_DA_AMPLA` em `editais/domain/recortes.py`;
  - `SIGLA_DO_CADASTRO` e `NOTA_DO_CADASTRO` em `publicacoes/infrastructure/pdf.py`, e o comentário da
    `096` em `portal/selecao.html`;
  - `impedimento` em `ocupacao/application/acrescimo.py`, `ocupacao.html` e `ocupacao_acrescimo.html`;
  - os avisos `reserve_only_convocation_external` e `reserve_only_with_reserved_lines` em
    `editais/domain/validation.py`.
- Os números de *Maturidade* foram recontados pelo método da própria página. Rodado sobre `745f115f`, a
  base da revisão de 19/10, ele reproduz todos os números publicados naquela data.
- **Não se rodou a suíte nem se percorreu o produto.** O total da suíte (12 775 passando, 12 pulados) é
  o medido em 21/10 sobre a árvore da `main` em `e869d7a2`, que o PR 325 leva ao `AGENTS.md`. Aquela
  rodada teve uma falha, que não é defeito: o teste de tempo da ocupação, que oscila com 4 workers. Nenhum
  teste lê `docs/`.
- A própria página foi aberta no navegador pela entrada `visao-do-sistema` do `.claude/launch.json`
  (porta 8090). Todas as âncoras internas têm destino, nenhum `id` se repete, e o HTML fecha as tags que
  abre.

## O que mudou na documentação

- **A prévia da classificação (094, 095).** Entrou a seção nova *Simular a classificação antes de
  publicar* (`#previa-da-classificacao`), na página *Marcos, classificação e ocupação*. Ela traz:
  - o botão *Simular classificação* no cartão do marco pela pontuação, e o painel que ele abre;
  - a jornada do Perfil, o detalhe do marco, os candidatos fictícios e o recálculo sem salvar;
  - o seletor *Recorte*, a concorrência concomitante, a ocupação por recorte como hipótese e a
    reversão declarada;
  - o que a prévia não simula, e a validação pendente.

  A ficha do marco, a maturidade da classificação, o catálogo, as perguntas, *Onde fica cada coisa* e o
  glossário passaram a apontar para ela.
- **A vaga acrescida depois da publicação (097).** Entrou a subseção *A vaga acrescida depois da
  publicação* (`#vaga-acrescida`), em *Ocupação de vagas*: quem pode, os campos, a conferência, o que se
  grava, por que não é publicada, o que a convocação faz com ela e como se desfaz. As efetivas e as
  causas de obsolescência da apuração ganharam a vaga acrescida. Ficaram corrigidas as frases que diziam
  que o cadastro de reserva não tem execução e que o Perfil só de reserva não convoca, em *Como as peças
  se encaixam*, no tutorial, em *O que eu consigo configurar?*, em *Se eu mudar isso*, nos exemplos de
  configuração, no cartão do Perfil, na seção *Cadastro de reserva*, no *Não confunda* do corte, na
  convocação, na matriz de permissões e na maturidade. O selo do cadastro de reserva passou de
  *Implementado, não operacionalizado* a *Parcial*: a espécie autoriza a vaga acrescida, e o limite
  continua sem leitor.
- **O `CR` no documento (096).** A seção *Cadastro de reserva* diz que o Perfil só de reserva sai com
  `CR` e a nota *“CR: cadastro de reserva.”*, e que o portal não diz o zero.
- **A recusa de CSRF (093).** A política de segurança de conteúdo, em *Segurança*, diz o que vê quem
  envia um formulário expirado. O item que a dava por aberta saiu de *Abertas desde 15/10* e foi para
  *Fechados desde 20/09*.
- **Estado do produto:**
  - 98 pastas de especificação, 41 tabelas append-only, 59 gatilhos (em 25 migrations, sobre 48
    tabelas), 95 migrations, 447 arquivos Python de aplicação, 169 templates, 900 + 15 arquivos de teste e
    121 + 36 rotas; módulos e espécies de sinal não mudaram;
  - 63 das 98 specs dizem `Draft`, entre elas a 097; dezoito ainda dizem *“PR aberto”*, e a 094 diz
    *“Especificada”*, com a implementação *“não iniciada”*;
  - *Fechados desde 20/09* ganhou três linhas: a recusa de CSRF, o `0` do Perfil só de reserva e,
    em parte, o RC-58;
  - a lacuna *Edital só de cadastro de reserva não convoca* passou a lacuna em parte, e o item da
    RC-58 em *Encontradas desde 30/09* passou a falar só do limite;
  - entrou a subseção *Abertas desde 19/10*, com quatro itens: a validação da prévia com elaboradores
    (T039 da 094, SC-870 e T032 da 095), as três divergências da prévia por recorte com a própria spec, o
    que a 096 deixou de fora e o que a 097 deixou para spec própria;
  - *Decisões pendentes* ganhou a linha da prévia, e a lista das decididas diz que a DP-05 foi revista.
- **Catálogo e glossário.** O catálogo passou de 129 a 134 capacidades, e o glossário de 118 a 121
  termos: *CR*, *Prévia da classificação* e *Vaga acrescida*.
- **Âncoras.** Nenhuma foi removida. As novas são `#previa-da-classificacao`, `#vaga-acrescida`,
  `#abertas-desde-19-10` e as dos três termos do glossário.

## O que não foi verificado, e o que ficou de fora

- Nada foi percorrido no produto. Os rótulos vêm dos *templates* e do código, e o comportamento, das
  views e dos testes.
- A prévia aparece como entregue, e não como validada: as duas specs dizem que a validação com quem
  elabora só fecha com o relato do usuário.
- Ficaram fora os achados internos que não mudam o que o usuário vê: a extração de duas decisões da
  ocupação para funções puras (095, citada só numa linha), a reserva do fecho na prévia do documento
  (096, citada só como limitação) e os guardiões de teste.

# Revisão de 19/10/2026 da Visão do Sistema

A documentação descrevia o sistema até a spec 072 (15/10), e a 073 só como especificada. Desde então
entraram na `main` a implementação da 073, o lote de correções da auditoria de 15/10 (PR 285) e as specs
074 a 092 — a maior parte delas o redesenho da gestão. Quem abria a gestão encontrava uma página de
acesso, uma barra lateral e um caminho no topo de cada tela que a documentação não mencionava, e
algumas frases ficaram falsas: o botão *Visão Geral* na lista de Processos, que virou item da barra; o
*Salvar distribuição* da Alocação, que se chama *Salvar alocação*; a Revisão de um Edital publicado,
que mostrava a norma de antes da Retificação e desde 15/10 mostra a vigente; e o assistente, que tinha
*“nenhuma rota pública”* e desde a 074 tem três, só no desenvolvimento local. Esta revisão descreve
tudo isso contra a `main` em `745f115f`.

## Como foi conferido

- Seis leituras paralelas confrontaram cada grupo de specs com o código da `main`, e não só com a
  própria spec: 073 com o PR 285 e a 074; 075 e 076; 077 a 082; 083 a 087; 088 a 092 com o portal; e a
  recontagem dos números e das rotas. Onde spec e código divergiam, valeu o código. Os rótulos novos
  foram conferidos de novo nos *templates* antes de entrar no texto, entre eles:
  - `identificar.html`, `identificar_demonstracao.html` e o cabeçalho do portal;
  - `SECOES` e `TELAS_LARGAS` em `interface/navegacao.py`, e o início da barra em `shell.js`;
  - `alocacoes.html`, `comissao.html`, `impedimentos.html`, `processo_detalhe.html` e
    `consolidacao_confirmar.html`;
  - `aviso.html`, `retificar.html`, `previa_de_publicacao.html` e `retificacao_detalhe.html`;
  - `compor_revisao.html` e a recusa do SMTP sem servidor em `config/settings/production.py`;
  - as diretivas e o lugar do middleware em `shared/politica_de_conteudo.py`;
  - o desenho dos botões dos atos irreversíveis em `sorteio.html`, `corte.html`, `ocupacao.html` e
    `convocacao.html`.
- Os números de *Maturidade* foram recontados pelo método da própria página. Rodado sobre `db428b30`,
  a base da revisão de 15/10, ele reproduz todos os números publicados naquela data. Uma regra do
  método mudou: o `interface` ganhou `apps.py` na 089 e passou a ser excluído da contagem de módulos
  de domínio, que continua 22.
- **Não se rodou a suíte nem se percorreu o produto.** O total da suíte (12 268 passando, 11 pulados)
  é o medido em 18/10 e registrado no `AGENTS.md`. Nenhum teste lê `docs/`.
- A própria página foi aberta no navegador, servida pela entrada nova `visao-do-sistema` do
  `.claude/launch.json` (porta 8090): sem erro no console, sem rolagem horizontal a 375 px, e a busca
  encontra os termos novos. Todas as âncoras internas têm destino, nenhum `id` se repete, e o HTML
  fecha as tags que abre.

## O que mudou na documentação

- **Entrada e navegação da gestão (075, 076, 077 a 088).** Entrou a seção nova *Entrar na gestão e
  navegar nela* (`#entrar-e-navegar`), em *Quem pode fazer o quê*. Ela traz:
  - os quatro passos da entrada: a *Área de gestão* do portal, a página de acesso, a escolha da
    identidade e o destino;
  - o que cada entrada concede: a de comissão, nenhum papel; a de responsabilidade, aquele papel e só
    ele;
  - o que acontece sem método de entrada, inclusive a sessão de demonstração que cai;
  - a barra lateral, o que cada papel vê nela e como ela fica em cada largura;
  - o caminho no topo de cada tela, e o que sai na impressão.

  O tutorial, *Papéis*, *Conceitos que o domínio não tem*, *Segurança*, *Maturidade* e *Onde fica cada
  coisa* passaram a apontar para ela. As linhas *“Gestão › …”* do tutorial ficaram, e a seção diz que
  elas descrevem o mesmo caminho, mais curto.
- **Telas redesenhadas (077 a 087).** Foram corrigidos os rótulos e a ordem que a página citava:
  - *Salvar alocação*, e o aviso de presidência ausente;
  - a seção *Membros (N)* da comissão, com *Só quem está sem Etapa*;
  - os blocos da página do Processo, na ordem nova;
  - a tela de distribuição, com os lugares da Etapa no topo e os botões de consolidar contornados;
  - o impedimento, com *“Confirme antes de registrar.”*;
  - a ordem do detalhe da Retificação e onde as recusas aparecem;
  - o rótulo do aviso com a hora, a interrupção, o reenvio e a volta da prévia;
  - *Visão Geral* e *Autoridades da unidade* como itens da barra.
- **Implantação (073).** A linha *Implantação* da maturidade, o piloto do assistente, *Segurança* e o
  caso do código de acesso dizem agora o que o §10.4 do guia ensina e as duas correções de código.
  Entraram também uma pergunta e uma linha no catálogo.
- **Correções da auditoria de 15/10 (PR 285).** A Revisão de um Edital publicado lê a versão vigente,
  e isso foi corrigido nos sete lugares que diziam o contrário. A descrição da Modalidade não se
  perde mais, e a linha dela saiu de *Configuração sem consumidor*. A advertência da Retificação não é
  mais apagada por impeditivo de outro Perfil. O Requerimento sem protocolo não mostra a linha vazia.
  Os identificadores ED- da auditoria de 15/10 colidem com os da auditoria do PDF de 08/10, que a
  página já usava, e por isso não foram citados.
- **O assistente na página da seleção (074).** Entrou a subseção *Na página da seleção, só no
  desenvolvimento local*. As frases *“nenhuma rota pública”* e *“Nenhuma rota do portal os alcança”*
  foram corrigidas em todos os lugares em que apareciam, sempre dizendo que nenhum candidato real vê o
  painel, e por quê.
- **Política de segurança de conteúdo (089, 091, 092).** Entrou a subseção em *Segurança*, com o que
  ela recusa, de onde sai e o que fica de fora — a página de falha de CSRF do Django.
- **Portal.** O topo, com o nome novo e *Minhas inscrições*, entrou na área do candidato, e o
  Requerimento diz quando a linha *Protocolo* aparece.
- **Estado do produto:**
  - 93 pastas de especificação, 439 arquivos Python de aplicação, 165 templates, 871 + 15 arquivos de
    teste e 117 + 36 rotas; migrations, tabelas append-only, gatilhos e módulos não mudaram;
  - 62 das 93 specs dizem `Draft`, e dezesseis das novas ainda dizem *“PR aberto”*;
  - *Domínio a domínio* ganhou a linha *Entrada e navegação da gestão*;
  - *Fechados desde 20/09* ganhou onze linhas;
  - entrou a subseção *Abertas desde 15/10*, com nove itens, entre eles a validação do redesenho com
    a equipe, os atos irreversíveis com botão comum e a página de CSRF sem desenho;
  - *Superadas por decisão* ganhou as duas decisões da 081 respondidas em 18/10.
- **Catálogo e glossário.** O catálogo passou de 123 a 129 capacidades e o glossário de 115 a 118
  termos: *Ambiente de demonstração*, *Barra lateral* e *GPS*. O índice alfabético ganhou o B.
- **Âncoras.** Nenhuma foi removida. As novas são `#entrar-e-navegar`, `#entrar`,
  `#barra-da-gestao`, `#caminho-no-topo` e as dos três termos do glossário.

## O que não foi verificado, e o que ficou de fora

- Nada foi percorrido no produto. Os rótulos vêm dos *templates*, e o comportamento, das views e dos
  testes.
- Os achados internos das specs 081 a 092 que não mudam o que o usuário vê ficaram fora: os
  guardiões de teste, as fixtures, as cópias de regras de folha e o inventário visual.
- A página não diz que o nome do produto mudou. O título continua *Sistema de Processos Seletivos e
  Editais*, e só o glossário (*GPS*) e o portal falam do nome novo.

# Revisão de 15/10/2026 da Visão do Sistema

A documentação descrevia o sistema até a spec 068 (10/10). Desde então entraram na `main` quatro
specs implementadas e uma só especificada, e nenhuma delas aparecia no texto. Esta revisão descreve
como entregues as specs 069 a 072, contra a `main` em `db428b30`, cada uma com o que ainda espera
validação humana. A 073 é citada só como especificada. Também passa a dizer, no início e no estado do
produto, que o sistema não está em produção.

## Como foi conferido

- Cada spec foi lida e confrontada com o código da `main`, e não só com a própria spec. Onde as duas
  divergiam, vale o código. Quatro leituras paralelas, uma por spec, levantaram o que foi entregue, os
  rótulos exatos dos *templates* e as tarefas abertas. As afirmações centrais foram conferidas de novo
  antes de entrar no texto, entre elas:
  - os oito papéis de `PAPEIS` em `interface/identidade.py`;
  - as sete rotas novas em `interface/urls.py`, comparadas com `0edc0f8d`;
  - a guarda `_edital_do_piloto` em `interface/assistente.py`;
  - o comando `excluir_registros_do_piloto` e o prazo de 90 dias;
  - o catálogo `CATALOGO_DA_069`, a `APRESENTACAO` e `APRESENTACOES` em `editais/domain/secoes.py`;
  - o resumo em `publicacoes/infrastructure/apresentacao.py` e as frases da redação 2 em `pdf.py`;
  - os rótulos da vitrine, da página da seleção, do acesso e de `meus_dados.html`;
  - o `503` de `identificar` em `interface/views.py:628-629` e `sem_autenticacao.html`;
  - a ausência de código de LDAP em `backend/`, contra a resposta de 28/08 na spec 002 (T056
    aberta), e o §1 de `doc/implantacao-em-producao-ubuntu.md`.
- Os números de *Maturidade* foram recontados pelo método descrito na própria página. Rodado sobre
  `0edc0f8d`, a base da revisão de 10/10, o método reproduz todos os números publicados naquela
  data. O mesmo vale para a contagem de `Status: Draft`: 58 de 69 em `0edc0f8d`, 63 de 74 hoje.
- **Esta revisão não rodou a suíte, não percorreu o produto no navegador e não chamou o serviço de
  inferência.** A auditoria de consolidação de 15/10, que a encomendou, fez as duas primeiras coisas
  na mesma `main`: a suíte fechou em 11 297 passando e 11 pulados (`db428b30`, com o grupo
  `assistente`, 1312s), e é esse o número que a página traz; e o percurso pelo navegador está no
  relatório da auditoria. Nenhum teste lê `docs/`.
- Todas as âncoras internas têm destino, nenhum `id` se repete, e o HTML fecha as tags que abre.

## O que mudou na documentação

- **Edital em linguagem simples (069).** Entrou nos seguintes lugares:
  - a ficha da Publicação: a descrição administrativa fora do ato, o *“Resumo deste Edital”*, o
    *“Sumário”*, a redação 2 das frases, a fonte embutida, e título, idioma e marcadores no arquivo;
  - *As seções de conteúdo*: os títulos novos das mesmas 22 seções, e as seções reunidas sob as
    perguntas do candidato.

  Também foram corrigidas a lista do que o ato imprime (*“a descrição”* saiu) e duas citações aos
  nomes antigos das seções. A SC-517 entrou como pendente: as frases novas esperam a aprovação do
  responsável pelo produto antes do primeiro Edital real.
- **Fonte de consulta do Edital (070) e piloto do assistente (071).** Entrou a seção nova *O assistente
  de dúvidas do Edital*, no fim de *Processo, Edital e publicação* (âncora `#assistente-do-edital`),
  com o selo *Parcial*. Ela separa as três coisas:
  - a validação interna, sem modelo e sem gravação;
  - o piloto, com papel próprio, chave, conferência da resposta e registros que se excluem 90 dias
    depois do relatório final;
  - o protótipo da Fase C, sem link e sem spec.

  Ela diz também que nada disso é alcançável pelo candidato, e traz as dependências fora do
  repositório, os dois comandos e as tarefas abertas (T046 da 070; T058 a T060 e T065 da 071).
- **Papéis.** São oito: o *Participante do piloto do assistente* entrou na tabela, no glossário
  (*Papel*) e numa nota da matriz.
- **Jornada pública do portal (072).** Os passos 1, 3 e 12 da jornada e a tabela da página pública
  ganharam o que a 072 mudou:
  - o título e os filtros recolhidos da vitrine;
  - o cartão pelo Edital, com a oferta e o prazo de recurso;
  - a volta, o resumo *“O que esta seleção oferece”* e a frase do Requerimento;
  - o acesso que nomeia a vaga e volta a ela;
  - o texto de finalidade de nome e CPF.

  A SC-605 e a FR-1627 entraram como pendentes de validação humana. Ficou falsa, e foi corrigida, a
  lacuna que punha *“Unidade: CEFOR”* na vitrine: a vitrine usa a sigla, e a página da seleção
  ainda não. A rota `/selecoes/` passou a se chamar *Processos seletivos*.
- **O sistema não está em produção.** Agora é dito, sem dramatizar, em cinco lugares:
  - um aviso em *Estado atual do sistema*;
  - o veredito de *Maturidade*;
  - as linhas *Autenticação institucional* e *Implantação*;
  - a fragilidade de autenticação em *Segurança*;
  - a lacuna *Autenticação institucional real* e uma pergunta nova.

  Em todos vão os mesmos três fatos: o `503` sem o seletor de identidade, o LDAP respondido em 28/08 e
  nunca implementado, e a falta de política de retenção.
- **073.** Citada só na linha *Implantação* da maturidade, como especificada e sem implementação na
  `main`.
- **Estado do produto:**
  - 74 pastas de especificação, 94 migrations, 22 módulos (o novo é `duvidas`), 432 arquivos Python de
    aplicação, 166 templates, 849 arquivos de teste e 116 rotas da gestão; o portal segue com 33;
  - as 40 tabelas append-only e os 58 gatilhos não mudaram: os registros do piloto se excluem e não
    entram;
  - 63 das 74 specs dizem `Draft`;
  - *Domínio a domínio* ganhou a linha *Assistente de dúvidas do Edital* e atualizou *Inscrição* e
    *Documento como ato oficial*;
  - *Fechados desde 20/09* ganhou três linhas (ED-05, ED-08 e a sigla da vitrine);
  - entrou a subseção *Abertas desde 10/10*;
  - *Decisões pendentes* ganhou três linhas: as frases da 069, a validação da 072 e a revisão da 070;
  - *Divergências* ganhou a contagem nova de `Draft` e duas linhas sobre a 071: o cabeçalho
    desatualizado e a exclusão parcial.
- **Recursos disponíveis e perspectivas.** Entraram dois cartões, *Edital em linguagem simples* e
  *Assistente de dúvidas, só interno*. O cartão do assistente de nove passos passou a se chamar
  *Composição do Edital*, para não se confundir com o assistente de dúvidas. Entraram também a
  perspectiva *Participante do piloto do assistente* e um *Quero saber…*.
- **Catálogo e glossário.** O catálogo passou de 119 a 123 capacidades, e o glossário de 110 a 115
  termos:
  - Apresentação por perguntas;
  - Assistente de dúvidas;
  - Piloto do assistente;
  - Redação do documento;
  - Resumo do Edital.
- **Perguntas, rotas, dados pessoais e *Quem vê o quê*:**
  - três perguntas novas: produção, assistente e o PDF novo;
  - as sete rotas novas da gestão;
  - a linha das perguntas do piloto em *Dados pessoais*;
  - as trocas do piloto em *Existe só internamente*.

  De passagem, foi corrigida a contagem de rotas da evidência, que dizia 98 desde 30/09.
- **Âncoras.** Nenhuma foi removida. São novas `#assistente-do-edital` e as dos cinco termos do
  glossário.

## O que não foi verificado, e o que ficou de fora

- Nada foi exercitado no navegador nem no serviço de inferência. Ficaram sem reprodução:
  - o comportamento do piloto e do protótipo;
  - a conferência das respostas;
  - o modo simulado.
- Não se conferiu, além do que a 072 registra, a disposição em tela estreita. A 072 registra que, a
  320 px, o resumo da oferta não cabe.
- A 074 não está na `main` e não é mencionada. A implementação da 073 também não está, e não foi
  descrita.
- Achados que ficaram só registrados, sem virar texto próprio:
  - a 070 nunca produz o tipo *“Detalhe em anexo”*, só o aviso;
  - o painel do protótipo não mostra o aviso de serviço externo que a FR-1503 pede da tela do piloto;
  - a produção não exige a `tokenizers` com o piloto ligado (a página diz só que a imagem de
    contêiner não instala o grupo `assistente`).

# Revisão de 10/10/2026 da Visão do Sistema

A documentação descrevia o sistema até a spec 054 (30/09), e contradizia o que entrou depois, em
especial com a 059 e a 066. Esta revisão descreve como entregues as specs 055 a 068, contra a `main`
em `0edc0f8d`. A anterior está em [CHANGELOG-2026-09.md](CHANGELOG-2026-09.md).

## Como foi conferido

- Cada spec foi lida e confrontada com o código da `main`, e não só com a própria spec. Onde as duas
  divergiam, vale o código. Seis leituras paralelas, uma por grupo de specs, levantaram os trechos
  falsos ou incompletos com a evidência no código. As afirmações centrais foram conferidas de novo
  antes de entrar no texto, entre elas:
  - `_reingressou` em `classificacao/application/corte.py`;
  - os papéis e permissões em `interface/identidade.py`;
  - as rotas em `interface/urls.py`;
  - os códigos de `editais/domain/validation.py`;
  - os modelos iniciais e o rodapé do aviso;
  - os rótulos dos *templates* do portal e da gestão.
- Os números de *Maturidade* foram recontados pelo método descrito na própria página. O mesmo método
  rodado sobre `86bbf49`, a base da revisão de 30/09, reproduz os números publicados naquela data. A
  exceção são os arquivos de teste, que tinham sido contados em 29/09.
- **Não se rodou a suíte nem se percorreu o produto no navegador.** O total da suíte (10 408 passando,
  11 pulados) é o medido em 09/10 e registrado no `AGENTS.md`. Nenhum teste lê `docs/`.
- Todas as âncoras internas têm destino, e o HTML fecha as tags que abre.

## O que mudou na documentação

- **Convocação e Requerimento com porta no portal (059).** Ficaram falsas as lacunas que diziam que o
  candidato só chegava à própria convocação e ao Requerimento pedido nela pelo endereço. Elas estavam
  na jornada, na área do candidato, em *Quem vê o quê*, no catálogo, nas perguntas, na maturidade, nas
  lacunas e no tutorial. As caixas vermelhas do diagrama da jornada viraram caixas comuns.
- **Acompanhamento pela situação (063).** O passo 8 da jornada, *O que o candidato vê* em
  Resultados e o glossário citavam frases que o portal não escreve mais: *“Resultado divulgado”* e
  *“Você não foi classificado neste marco.”*. Agora descrevem a situação (rótulo, por quê, o que
  fazer), a *Classificação por lista* e o prazo de recurso de Resultado de Etapa no topo.
- **Resultados por Perfil, etapa e lista (062, PR 255, PR 262).** A lacuna *“o resultado não diz de
  qual lista é”* virou **Parcial**: o portal a diz em toda parte, e a gestão (o histórico e a prévia)
  ainda não. A frase da publicação vigente agora é *“Esta é a versão que vale.”*.
- **Unidades e autoridades (060).** Era falso o *catálogo fixo* de autoridades, com as três entradas
  só de cargo, e `publicacoes/domain/autoridades.py` não existe mais. Entraram:
  - a Unidade, com cabeçalho e local do ato;
  - as autoridades habilitadas com vigência;
  - a tela *Autoridades da unidade* e a permissão `autoridade:gerir`;
  - o quarto passo do `make preparar`.

  A divergência de cargo registrada na 054 deixou de ser de código.
- **Avisos aos candidatos (066).** Eram falsas as afirmações de que o sistema não manda e-mail de
  resultado e de que *“um quinto aviso exige rever a regra”*: a regra foi revista em 09/10. Entraram:
  - o aviso complementar, na tabela de e-mails e em Segurança;
  - o despacho;
  - a chave `AVISOS_AOS_CANDIDATOS`, desligada em produção até a LGPD;
  - a seção *Avisar os candidatos* em Resultados;
  - o *Não confunda* comunicação × aviso;
  - a permissão `aviso:enviar` do Publicador e do Gestor;
  - linhas na matriz, rotas e uma linha em *Operar em escala*.
- **Corte depois do recurso (061).** A obsolescência por *participante reingressou* foi qualificada:
  só o que a ordem lida ainda não cita. O corte emitido sobre a ordem sucessora nasce em dia, e o
  corte obsoleto bloqueia distribuir, concluir e consolidar.
- **O documento do Edital (064, 065, 067, 068).** O que entrou:
  - o que sai idêntico entre Perfis é impresso uma vez, o que corrige o *AX-11* em achados e lacunas;
  - o conflito de numeração impede o Edital e só avisa na Retificação;
  - a remissão sem destino gera aviso;
  - a frase de recurso nomeia o marco;
  - o marco por sorteio não pede nem imprime arredondamento;
  - o Perfil sem vaga imediata não imprime quadro nem reversão;
  - o aviso *“Prazos de recurso a conferir”*.

  A tabela de famílias da validação ganhou duas linhas. A linha *“Casas decimais e Arredondamento
  num marco de sorteio”* saiu de *Configuração sem consumidor*.
- **Polimento (055–058).** Três citações tinham *“(s)”* que a interface não escreve mais. A lacuna
  dos números *“espremidos”* da Ocupação ficou falsa. A ordem dos campos do Perfil na Retificação
  mudou. Corrigido também, de passagem, o *“7 seções textuais”* que a revisão de 30/09 deixou.
- **Produção.** A fragilidade *“não há caminho de produção”* passou a dizer que o caminho está
  escrito em `doc/implantacao-em-producao-ubuntu.md` (30/09) e não está no ar. A própria peça
  declara dois bloqueadores: a autenticação e a política de retenção.
- **Estado do produto:**
  - 69 pastas de especificação, 90 migrations, 40 tabelas append-only, 58 gatilhos (em 24
    migrations, sobre 47 tabelas), 21 módulos, 109 rotas da gestão e 33 do portal;
  - 58 das 69 specs dizem `Draft`;
  - *Fechados desde 20/09* ganhou onze linhas;
  - *Lacunas antigas* ganhou cinco resolvidas e duas parciais;
  - entrou a subseção *Encontradas desde 30/09*;
  - *Decisões pendentes* ganhou três linhas, e a DP-20 encolheu para *como o ato é assinado*.
- **Catálogo e glossário.** O catálogo passou de 102 a 119 capacidades, e o glossário de 101 a 110
  termos:
  - Atribuições do Perfil;
  - Aviso complementar;
  - Conflito de numeração;
  - Despacho;
  - Modelo de aviso;
  - Remissão interna;
  - Situação da inscrição;
  - Subseção comum aos Perfis;
  - Unidade.
- **Âncoras.** Nenhuma foi removida, e as novas são as dos nove termos do glossário.

## O que continua em aberto

Está registrado nas próprias páginas, sobretudo em *Lacunas e decisões em aberto*:

- a reabilitação de quem foi eliminado antes da última Etapa do marco não alcança o corte
  (achado de 07/10, com três saídas para decisão);
- a gestão não diz a lista no histórico de resultados nem na prévia;
- três grafias para o desfecho *Aceite* no portal;
- o reenvio da convocação sugere prazo novo;
- a convocação para heteroidentificação, entrevista e títulos não tem ato;
- a marca do Cefor fora do documento;
- os itens ED-* ainda abertos da auditoria do PDF;
- a regra da reserva no cadastro (RC-58);
- a validação de LGPD que liga os avisos em produção;
- a numeração automática dos parágrafos.
