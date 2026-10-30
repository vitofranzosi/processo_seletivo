# Research: Gestão de acessos pela interface

As decisões técnicas da feature. As de governança estão na spec, em §Decisões pendentes, e nenhuma
foi tomada aqui.

## D-001 — As telas pedem capacidade, e não papel

- **Decisão**: "Acessos da unidade" pede `acesso:consultar` para ler e `acesso:gerir` para conceder
  e revogar; "Administração de acessos" pede `acesso:administrar` no escopo institucional. Nenhuma
  view nem template menciona `administrador-de-acessos` como condição.
- **Por quê**: quem concede na unidade é proposta da `106` (proposta 3). Se o usuário decidir que o
  Gestor concede, muda uma linha do catálogo e nenhuma tela.
- **Alternativas**: condicionar pelo papel (a tela mudaria com a decisão).

## D-002 — Um nível parametriza as duas telas

- **Decisão**: `interface/acessos.py` define dois níveis — o da unidade e o institucional — com a
  capacidade de ler, a de conceder, o escopo em que o ator precisa estar, os papéis que o nível
  concede e se a unidade vem da sessão ou da escolha. As mesmas views servem aos dois, pelo nível
  declarado na rota.
- **Por quê**: as duas jornadas são a mesma — buscar, conferir, confirmar com motivo —, e duas cópias
  divergiriam na primeira correção.

## D-003 — A confirmação é uma segunda requisição que reconfere tudo

- **Decisão**: o primeiro envio (`acao=conferir`) só lê: resolve a pessoa pelo identificador interno,
  confere capacidade, escopo, papel, autoconcessão e vigência, e mostra a confirmação. O segundo
  (`acao=confirmar`) traz o motivo e chama `conceder` ou `revogar` da `106`, que reconferem tudo.
  A unidade do nível da unidade nunca vem do formulário: é a ativa.
- **Por quê**: nada grava antes da confirmação (`FR-3116`), e a confirmação não confia no que a
  primeira etapa viu (`FR-3118`). A gravação e a trilha continuam na mesma transação, dentro das
  funções da `106` (`FR-3119`).
- **Alternativas**: um modal com JavaScript (a CSP exige arquivo externo, e a recusa no servidor
  continuaria necessária); gravar e oferecer desfazer (nada se exclui).

## D-004 — A pessoa vai no formulário pelo identificador interno, nunca digitado

- **Decisão**: cada resultado da busca é um botão que envia o `username` (`pessoa-<uuid>`) em campo
  oculto. O servidor o resolve entre as pessoas institucionais ativas, e a recusa de pessoa
  inexistente ou inativa é a mesma.
- **Por quê**: o `username` é o que a `106` já compara na autoconcessão; não é dado pessoal, e
  ninguém o digita (`FR-3129`). Um campo oculto adulterado só alcança outra pessoa institucional
  ativa — o que a busca já alcançaria —, e todas as recusas continuam no servidor.

## D-005 — A busca é por POST, com piso de três caracteres e teto de dez

- **Decisão**: `buscar_pessoas(ator, termo, *, capacidade, escopo)` exige a capacidade no escopo,
  ignora termo com menos de três caracteres, procura `first_name` ou `email` contendo o termo, sem
  diferenciar caixa, entre `is_active` e `username` com o prefixo institucional, exclui o ator, e
  devolve onze linhas para saber se há mais de dez. O formulário é `POST`.
- **Por quê**: o piso e o teto tornam a listagem irrestrita impraticável pela tela (`FR-3113`); o
  `POST` mantém nome e e-mail fora do endereço e dos registros de acesso do servidor (`FR-3115`). O
  universo são as pessoas que já entraram, porque sem diretório é o único que existe.
- **Alternativas**: e-mail exato (impede achar pelo nome, que é como se procura); registrar cada
  busca na trilha (a trilha exige agregado, e a busca não tem; fica para a política de retenção).

## D-006 — A resolução do ator lê os vínculos da pessoa uma vez

- **Decisão**: `_resolucao_institucional` passa a ler, numa consulta, todos os vínculos vigentes da
  pessoa (escopo e papel), e deriva deles os papéis da unidade ativa e os escopos do seletor. Guarda
  também a própria pessoa, para o nome.
- **Por quê**: o seletor da barra precisa dos escopos em toda página; uma consulta a mais por página
  quebraria o teto de duas do `SC-1005` da `106`.

## D-007 — Sem acesso é uma rota própria, e o desvio mora em `pedir_identificacao`

- **Decisão**: `GET /gestao/sem-acesso`. `pedir_identificacao`, que toda porta chama quando não há
  ator, manda para lá a sessão institucional cuja pessoa está autenticada; o resto continua indo à
  página de acesso. A tela lista os escopos com acesso vigente, cada um com o botão de troca.
- **Por quê**: um ponto só, que as 59 telas já chamam. Sem pessoa autenticada, a sessão
  institucional já foi encerrada pela resolução, e o caminho é o de quem não entrou.

## D-008 — O nome da pessoa vem do contexto, e só o modo institucional consulta

- **Decisão**: o processador de contexto entrega `nome_do_ator`: na demonstração, o `subject`, como
  hoje; no institucional, `first_name`, ou o e-mail, ou "pessoa sem nome informado". A barra, as
  iniciais e a página de acesso o usam. Nas telas de acesso, os autores (`concedido_por`,
  `revogado_por`) se traduzem por um mapa lido numa consulta, e `implantacao` aparece como
  "Implantação".
- **Por quê**: `FR-3103` sem custo na demonstração (`SC-1016`). As demais telas que exibem
  `subject` de outras pessoas ficam para o incremento 2.

## D-009 — O prazo da sessão mora na própria sessão, com relógio injetável

- **Decisão**: a sessão institucional guarda `entrada_em` e `atividade_em`, em segundos desde a
  época. A resolução confere os dois contra `GESTAO_SESSAO_DURACAO_MAXIMA_MINUTOS` e
  `GESTAO_SESSAO_INATIVIDADE_MINUTOS` antes de ler vínculos. Vencida, a sessão vai à trilha como
  `SAIDA` com o motivo (`duracao_maxima` ou `inatividade`), encerra-se como a saída, e a sessão nova
  leva a marca do motivo para a página de acesso. Válida, `atividade_em` é renovada se o caminho é
  da gestão e a requisição não traz o cabeçalho `Requisicao-Automatica`. O instante vem de
  `seguranca.relogio.agora()`, que os testes fixam.
- **Por quê**: a contagem precisa ser exata nos testes e independente do `SESSION_COOKIE_AGE`. A
  declaração de requisição automática só **tira** atividade: um cliente que a forjasse encurtaria a
  própria sessão, e nada mais. Hoje nenhuma requisição da gestão é automática.
- **Precisão**: vale o instante do servidor na leitura. A sessão é válida enquanto
  `agora − entrada_em < duração` **e** `agora − atividade_em < inatividade`; no instante igual ao
  limite, já não é.
- **Alternativas**: `set_expiry` do Django (renova com toda requisição, inclusive as automáticas,
  e não conta a duração absoluta).

## D-010 — Produção exige os dois prazos, quando há provedor

- **Decisão**: `production.py`, com `GESTAO_PROVEDOR_INSTITUCIONAL` declarado, recusa subir sem
  `GESTAO_SESSAO_DURACAO_MAXIMA_MINUTOS` e `GESTAO_SESSAO_INATIVIDADE_MINUTOS`, inteiros positivos.
  Fora de produção o padrão é 480 e 30 — a proposta, que o usuário adotou em 30/10 (P4), mandando
  declará-los expressamente em produção, que é o que esta exigência faz.
- **Por quê**: os valores são decisão do usuário (P4). Exigir a declaração impede que a proposta
  vire valor de produção por omissão.

## D-011 — A pessoa inativa não recebe vínculo

- **Decisão**: `conceder` recusa pessoa com `is_active` falso, com `pessoa_inativa` (409), depois de
  trancá-la.
- **Por quê**: a busca não a oferece, mas a confirmação recebe um identificador; e uma pessoa
  desativada não deve acumular acesso para quando voltar. É a única mudança na regra da `106`
  (`FR-3134`).

## D-012 — Testes de navegador com Playwright, num grupo opcional

- **Decisão**: o grupo `navegador` do `pyproject.toml` traz o Playwright. Os testes moram em
  `tests/navegador/`, pulam sem a biblioteca, e usam o `live_server` do pytest-django. O CI instala o
  grupo e o Chromium.
- **Por quê**: o pedido exige navegador de verdade com servidor; o Client do Django não executa a
  página nem segue a ida ao provedor. Opcional pela razão do `assistente`: produção não o instala.
- **Alternativas**: Selenium (pede driver à parte); só o painel do Claude (não é reprodutível nem
  roda no CI).

## D-013 — O provedor, no navegador, é uma página servida pelo próprio teste

- **Decisão**: o provedor simulado da `106` passa a mandar `redirect_uri` junto do `state`, para um
  endereço de autorização que é variável do módulo. Os testes de navegador o apontam para um
  servidor HTTP mínimo, de `tests/navegador/provedor.py`, que o teste sobe e derruba. A página dele
  mostra quem o ambiente preparou para autenticar e um botão "Continuar", que volta ao retorno da
  gestão com o `state` e um bilhete emitido naquele instante.
- **Por quê**: o Chromium não deixa a interceptação do Playwright alcançar o destino de um
  redirecionamento, e `provedor.invalid` não resolve. A página é a resposta do provedor preparada
  pelo ambiente de testes — quem autentica é decidido antes, e o navegador só segue o fluxo. O
  adaptador continua o mesmo, e nada novo existe em execução.
- **Alternativas**: um provedor de execução para a demonstração (proibido pelo pedido); mapear o DNS
  no Chromium (exigiria certificado para `https`).

## D-014 — As views novas entram no inventário de negativas da `033`

- **Decisão**: `interface/acessos.py` entra em `MODULOS_DE_VIEW`, e cada `raise Http404` dele tem
  linha no inventário. O 404 só responde vínculo de outra unidade, ou inexistente; falta de
  capacidade é a recusa explicada, por `require_authorization_base`.

---

# Incremento 2 — decisões técnicas, sobre as respostas do usuário de 30/10

Implementadas nesta branch, depois do "sim, implementar" do usuário. As decisões de governança são
as da spec, §Decisões do usuário.

## D-015 — A suspensão troca o hash da sessão, e é isso que mata as sessões antigas

- **Decisão**: suspender grava a suspensão, marca `is_active` falso e chama `set_unusable_password()`
  de novo, na mesma transação. A senha inutilizável ganha outro valor aleatório, e com ela o
  `get_session_auth_hash()` do Django: toda sessão aberta antes carrega o hash antigo, e o
  `get_user` do framework a apaga na requisição seguinte. Reativar marca `is_active` verdadeiro e
  **não** restaura o hash.
- **Por quê**: é o que a P2 exige — nenhuma sessão anterior volta, mesmo a que não fez requisição
  durante a suspensão. Conferir só `is_active` não basta: a sessão parada durante a suspensão
  voltaria a valer na reativação. O hash é o mecanismo do próprio Django para "sair de todos os
  dispositivos", conferido a cada requisição, sem consulta a mais e sem varrer a tabela de sessões
  (que não tem índice por pessoa).
- **Alternativas**: apagar as linhas de `django_session` da pessoa (exige decodificar todas);
  comparar o instante da entrada com o da última suspensão (uma consulta a mais por requisição,
  contra o teto de duas do `SC-1005` da `106`).

## D-016 — Suspensão e reativação são registros append-only; `is_active` é o efeito

- **Decisão**: `SuspensaoDePessoa(pessoa, suspensa_em, suspensa_por, motivo)` e
  `ReativacaoDePessoa(suspensao OneToOne, reativada_em, reativada_por, motivo)`, append-only nas duas
  camadas; `TABELAS_APPEND_ONLY` passa de 44 a **46**, e a migration `seguranca/0002` só as cria.
  `is_active` é escrito na mesma transação, como efeito, e a fonte da história são os registros.
  A pessoa é trancada (`select_for_update`), como na concessão: duas suspensões ou duas reativações
  simultâneas — a segunda vê a primeira; a reativação dupla, o banco recusa pela unicidade.
- **Por quê**: "quem estava suspenso quando" é pergunta de fiscalização, como "quem tinha o papel".
  `is_active` sozinho perderia a história no primeiro `UPDATE`.

## D-017 — A tela suspende pessoas; a implantação, também o administrador institucional

- **Decisão**: em "Administração de acessos", uma seção "Suspender ou reativar uma pessoa", com a
  busca do incremento 1 (que passa a incluir as suspensas, só nesta seção, marcadas como tal) e a
  confirmação de `FR-3142` e `FR-3145`. A camada de aplicação recusa o próprio ator e quem tem
  Administrador institucional vigente. Os comandos `suspender_pessoa` e `reativar_pessoa`, por
  `--provedor` e `--identificador`, com `--motivo`, gravam sob o ator `implantacao` e alcançam
  qualquer pessoa.
- **Por quê**: é a P1. O comando é o único ponto que alcança o administrador institucional, como o
  que o concede.

## D-018 — Retirar e substituir a administração institucional, pela implantação

- **Decisão**: `retirar_administracao_institucional --provedor --identificador --motivo` revoga o
  vínculo sob o ator `implantacao`. `substituir_administracao_institucional --de-provedor
  --de-identificador --para-provedor --para-identificador --motivo` revoga e concede num
  `transaction.atomic()` só, sob a trava global da primeira administração (`pg_advisory_xact_lock`
  da `106`), com os dois eventos na trilha e o mesmo `correlation_id`.
- **Salvaguarda técnica, revogável pelo usuário**: a retirada que deixaria **nenhum** administrador
  institucional vigente é recusada sem `--sem-administracao`, como a segunda concessão é recusada
  sem `--adicional`. As respostas de 30/10 não tratam desse caso. Foi implementada com o incremento
  2, porque não proíbe nada — com a marca, a última sai — e só impede o engano de terminal; o
  usuário a derruba ou a endurece com uma linha.
- **Por quê**: é a P3 e a proposta 2. A substituição numa transação é o que a P3 pede
  explicitamente: não há instante com dois administradores a mais nem com o anterior ainda ativo.

## D-019 — O nome nas demais telas, por um filtro com uma consulta por página

- **Decisão**: um filtro de template, `nome_de_pessoa`, que devolve o `subject` sem consulta quando
  ele não começa por `pessoa-`, e, quando começa, consulta todos os identificadores institucionais
  da página de uma vez, na primeira chamada, e guarda o mapa na requisição. Os templates que exibem
  `subject` de autor passam a usá-lo; a lista vem da varredura de `ator.subject`, `*_por`,
  `actor_subject` e `identity_subject` nos templates.
- **Por quê**: `FR-3150` e `FR-3151`. A demonstração não consulta nada, e o orçamento de consultas
  das telas existentes não muda.
