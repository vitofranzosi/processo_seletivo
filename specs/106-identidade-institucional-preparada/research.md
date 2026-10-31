# Research: Identidade institucional preparada

As decisões técnicas desta feature. As de governança estão na spec, em §Propostas ao usuário; o
comparativo inteiro, no [diagnóstico](../../doc/diagnostico-autenticacao-da-gestao-2026-10-30.md).

## D-001 — Django Auth guarda a identidade; o GPS autoriza

- **Decisão**: a pessoa institucional é um `auth.User`. Sessão, rotação, troca de usuário e
  desativação são as do Django (`authenticate`, `login`, `logout`, `get_user`). A autorização é só
  do GPS, por vínculos.
- **Por quê**: o que uma identidade própria escreveria à mão — sessão, `cycle_key`, a sessão de
  outro usuário descartada, `is_active` derrubando a sessão — o Django já entrega e já testou. E a
  integração real com OIDC ou SAML costuma ser um *backend* do Django: o caminho até ela fica mais
  curto.
- **Alternativas**: a Pessoa própria do estudo (uma tabela a mais e o código de sessão à mão); o
  `mozilla-django-oidc` já agora (seria integrar o SSO, que o pedido adia).

## D-002 — O identificador interno é `pessoa-<uuid4>`, no `username`, e não muda

- **Decisão**: o `username` nasce `pessoa-` seguido de um UUID4 na primeira entrada. É o `subject`
  do `Actor`, dos atos e da trilha. Um gatilho recusa `UPDATE` que o mude, e outro recusa `DELETE`
  em `auth_user`.
- **Por quê**: o `id` inteiro é de um banco só; o login institucional muda com o nome; o
  identificador do provedor muda com o provedor. O UUID não carrega dado pessoal, e o prefixo o
  separa de qualquer identidade de demonstração escrita à mão. O `username` já é único, indexado e
  cabe nas colunas de 255.
- **Alternativas**: coluna `subject` numa tabela de perfil (uma tabela a mais para o que o
  `username` já é); UUID sem prefixo (indistinguível, num relatório, de um identificador qualquer).

## D-003 — A identidade externa é append-only, e nunca se associa pelo e-mail

- **Decisão**: `IdentidadeExterna(pessoa, provedor, identificador)`, com `(provedor, identificador)`
  único e `(pessoa, provedor)` único, protegida contra `UPDATE` e `DELETE`. O primeiro acesso cria a
  pessoa e a associação na mesma transação.
- **Por quê**: trocar de provedor vira acrescentar uma associação, e o `subject` não muda. O e-mail
  muda e se recicla: casar conta por ele é a tomada de conta clássica.
- **Alternativas**: o identificador externo no próprio `username` (preso a um provedor).

## D-004 — Os papéis de acesso ficam num catálogo à parte

- **Decisão**: `seguranca/acessos.py` define `PAPEIS_DE_ACESSO` — `integrante` (nenhuma permissão),
  `administrador-de-acessos` (`acesso:gerir`, `acesso:consultar`) — e `PAPEIS_INSTITUCIONAIS` —
  `administrador-institucional` (`acesso:administrar`). O `PAPEIS` não muda.
- **Por quê**: o seletor desenha uma caixa por chave do `PAPEIS`, e a tela tem de continuar a mesma
  (FR-3001). O `integrante` existe porque o avaliador não tem papel sistêmico, e sem vínculo
  nenhum não haveria `Actor` (D-006).
- **Alternativas**: acrescentar ao `PAPEIS` (muda o seletor e o guardião da `075`).

## D-005 — Dois níveis de concessão, e nenhum concede a si mesmo

- **Decisão**: papel operacional (os oito e o `integrante`) se concede com `acesso:gerir` na unidade
  do vínculo; o `administrador-de-acessos`, com `acesso:administrar` no escopo institucional; o
  `administrador-institucional`, só pelo comando `conceder_administracao_institucional`. A comparação
  com o ator é pelo `username`. A pessoa é trancada (`select_for_update`) na concessão e na
  revogação, e a unicidade da revogação recusa a segunda. **A primeira administração institucional
  corre sob uma trava de transação global** (`pg_advisory_xact_lock`): a decisão "já há alguém?"
  é de todas as pessoas, e trancar só a de destino deixava duas execuções simultâneas gravarem dois
  administradores sem `adicional` (revisão do #345). Nada tranca linha append-only: a role de
  runtime não tem `UPDATE` sobre elas, e `FOR UPDATE` o exige.
- **Por quê**: é a regra do estudo, §C.2, sem tela. O comando de implantação é o único ponto que
  cria poder institucional, e grava sob o ator `implantacao`, como a sincronização das unidades.
- **Alternativas**: o institucional concedendo outro institucional (elevação sem ato de implantação).

## D-006 — O `Actor` institucional se calcula a cada requisição, da unidade ativa

- **Decisão**: a sessão guarda `{origem: "institucional", unidade, identidade_externa}` ao lado das
  chaves do Django, e nunca papéis. `ator_da_sessao` resolve o `User` por `get_user` e os vínculos
  vigentes da unidade ativa numa consulta, e guarda o resultado na própria requisição. Sem vínculo
  vigente na unidade ativa, devolve `None`.
- **Por quê**: revogação na requisição seguinte; troca de unidade sem acúmulo; e a presidência de
  comissão, que confere escopo e `subject`, não alcança quem não tem `Actor`. O cache da requisição
  segura o custo em duas consultas, por mais que a página leia o ator (SC-1005).
- **Alternativas**: guardar permissões na sessão (revogação só no próximo login, o L-2 do estudo).

## D-007 — O adaptador tem contrato fixo, e o retorno exige o estado da ida

- **Decisão**: `GESTAO_PROVEDOR_INSTITUCIONAL` aponta uma classe com `nome`, `iniciar(request, *,
  retorno, estado)` e `concluir(request, *, estado)`. A gestão cria o estado, guarda-o na sessão,
  confere-o no retorno e o descarta antes de chamar `concluir`. Só o que `concluir` devolve vira
  identidade; a gestão não lê cabeçalho. **Na fronteira HTTP o estado se chama `state`**, o nome
  do OIDC; um adaptador de outro protocolo diz onde ele volta por `estado_do_retorno(request)`, e a
  comparação com a sessão continua da gestão. A primeira versão lia `estado`, e o simulado, que
  usava o mesmo nome na ida e na volta, mascarava a recusa de todo provedor convencional (revisão
  do #345).
- **Por quê**: é o contrato do estudo, §B.1, com a proteção contra *login CSRF* que todo fluxo de
  redirecionamento precisa. Serve a OIDC na aplicação e a SAML no proxy.
- **Alternativas**: `RemoteUserMiddleware` (confia num cabeçalho; recusado em produção por D-009).

## D-008 — Um *backend* só, e o `User` não autoriza nada

- **Decisão**: `AUTHENTICATION_BACKENDS` tem só `seguranca.autenticacao.BackendInstitucional`, que
  autentica uma `IdentidadeAutenticada` e nunca usuário e senha. O `Actor` lê só vínculos:
  `is_superuser`, `is_staff`, `groups` e `user_permissions` são ignorados. O `admin` não é
  instalado, e nada aqui o pede.
- **Por quê**: o risco próprio do Django Auth é parecer que o `User` dá acesso. Três barreiras
  independentes o fecham, cada uma com teste.

## D-009 — Produção recusa o que não é institucional, no *boot* e em execução

- **Decisão**: `production.py` recusa provedor que se declare de teste (`apenas_para_testes`), que
  esteja em `tests.`, ou que não se importe, e qualquer *backend* além do institucional.
  `seletor_disponivel()` devolve falso sempre que `AMBIENTE_DE_PRODUCAO` é verdadeiro. Sem provedor,
  a gestão continua respondendo 503.
- **Por quê**: o *boot* é a barreira que já existe; a de execução fecha o caso de uma configuração
  que mude depois dele. Nenhuma das duas cai para a demonstração.

## D-010 — A trilha da sessão aponta para a identidade externa

- **Decisão**: `ENTRADA`, `SAIDA` e `TROCA_DE_UNIDADE` têm como agregado a `IdentidadeExterna` usada
  na entrada; `ACESSO_CONCEDER` e `ACESSO_REVOGAR`, o `Vinculo`. O escopo é a unidade ativa (ou o
  institucional, para quem não tem unidade), nunca vazio.
- **Por quê**: a trilha exige UUID, e o `User` tem chave inteira. A identidade externa diz, além de
  quem, por qual provedor a pessoa entrou.

## D-011 — Escopo institucional reservado: `institucional`

- **Decisão**: o escopo dos vínculos e dos eventos institucionais é o texto `institucional`. A
  sincronização das unidades recusa esse código.
- **Por quê**: cabe no formato de código de unidade, e por isso precisa ser recusado lá; e é legível
  numa consulta da trilha.

## D-012 — As rotas novas não têm template

- **Decisão**: três rotas — a ida ao provedor, o retorno e a troca de unidade (POST) — respondem
  redirecionamento, a página de entrada não configurada (503) ou a recusa do domínio (403). Nenhuma
  levanta 404.
- **Por quê**: as telas de acesso estão fora (spec, §O que esta spec cobre); o que as rotas precisam
  provar é o fluxo, e ele se prova pela tela que já existe.
