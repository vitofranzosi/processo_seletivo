# Diagnóstico — Autenticação da gestão: Django Auth × identidade própria

*Auditoria arquitetural de 30/10/2026, sobre a `main` em `4d93c1f8` (depois da `105`), feita como
primeiro passo da spec [`106`](../specs/106-identidade-institucional-preparada/spec.md). Parte do
[estudo do B-1](estudo-identidade-e-acessos-2026-10-30.md) e do
[parecer do usuário](auditoria-administracao-institucional-2026-10-30.md#parecer-do-usuário-30102026),
e confere de novo, no código, o que os dois afirmavam. Caminhos relativos a
`backend/processo_seletivo/`, salvo os que começam por `backend/`, `specs/` ou `doc/`.*

Marcas: **[F]** fato lido no código; **[I]** inferência; **[H]** hipótese.

**A pergunta.** O pedido de 30/10 manda preparar a autenticação institucional sem integrar o SSO e
sem tocar no seletor de demonstração, e manda comparar duas formas de guardar a identidade:
**A**, o Django Auth com a autorização do GPS por cima; **B**, uma identidade própria (a Pessoa, o
Vínculo e a Revogação do estudo) com um adaptador institucional. A escolha é a de menor
complexidade total, maior segurança e menor custo futuro.

**A resposta.** **A**, com a autorização inteiramente do GPS. O Django Auth guarda **quem é** a
pessoa e mantém a sessão; o GPS decide **o que ela pode**, numa tabela de vínculos própria. As duas
coisas coexistem porque têm responsabilidades distintas, e o `Actor` continua sendo o único lugar
onde a autorização é lida. A decisão está na
[ADR](decisao-identidade-e-autorizacao-da-gestao.md).

---

## 1. O que existe, conferido

### 1.1 Construção do `Actor`

- `Actor(subject, institution_scope, permissions)` é um *dataclass* congelado de quinze linhas,
  sem banco e sem sessão (`seguranca/domain.py`) [F].
- A gestão o constrói **num ponto só**: `ator_da_sessao` (`interface/identidade.py`). Ele lê a chave
  `interface_identidade` da sessão — `{subject, escopo, papeis, origem}` — e calcula as permissões
  pelo `PAPEIS` **a cada leitura** [F]. Há 60 ocorrências dele em 8 módulos da aplicação, e todas
  recebem um `Actor` ou `None` [F, `grep -rn`].
- A API o constrói em `seguranca/api/authentication.py`, a partir de um *token* de desenvolvimento
  `subject|escopo|permissões` sem assinatura [F]. Produção recusa esse módulo inteiro
  (`config/settings/production.py`, `MODULO_DE_DESENVOLVIMENTO`) [F]. Nenhuma tela da gestão
  depende da API [F, pelo estudo, §C.7].

### 1.2 Sessão

- A sessão é a do Django (`SessionMiddleware`), em banco. O mesmo *cookie* serve ao portal do
  candidato, que guarda as próprias chaves e faz `cycle_key()` na entrada (`portal/identidade.py`)
  [F].
- **A gestão não roda a sessão na entrada** [F]: `identidade.identificar` grava a chave e mais
  nada. Fixação de sessão é aceitável no seletor, que não é autenticação; não seria no modo
  institucional.
- `django.contrib.auth` está instalado e a tabela `auth_user` existe em todo banco [F,
  `config/settings/base.py`, `INSTALLED_APPS`]. **Não** há `AuthenticationMiddleware`, `admin`,
  `AUTH_USER_MODEL` próprio nem `AUTHENTICATION_BACKENDS` declarado [F]: o padrão do Django, o
  `ModelBackend`, aceitaria usuário e senha se alguém chamasse `authenticate()` — ninguém chama.

### 1.3 `PAPEIS`

- Oito papéis, cada permissão com a sua justificativa normativa ao lado (`interface/identidade.py`)
  [F]. `DESCRICOES` tem as mesmas chaves, e um guardião da `075` cobra isso [F].
- O seletor desenha uma caixa por chave de `PAPEIS` [F]. **Acrescentar papel ao `PAPEIS` muda a
  tela de identificação** — e o pedido manda que ela continue exatamente como hoje [I].

### 1.4 O usuário nos atos e na trilha

- O `subject` é gravado como texto em dezenas de colunas `CharField(255)`, muitas em tabelas
  append-only (`published_by`, `prepared_by`, `homologated_by`, `actor_subject` da trilha,
  `identity_subject` da comissão) [F, pelo estudo, §A]. Nenhuma tem chave estrangeira para
  usuário algum [F].
- A segregação compara esses textos (`publicacoes/application/publish_edital.py`, `retificacoes.py`)
  [F]. **Por isso o valor do `subject` institucional precisa nunca mudar para a mesma pessoa** — e
  é isso, e não o protocolo, que torna a escolha irreversível em produção.
- A trilha (`RegistroAuditoria`) exige `aggregate_id` UUID [F, `auditoria/models.py`]. Um agregado
  com chave inteira — como o `auth_user` — não pode ser o agregado de um evento [F].

### 1.5 Comissões e presidências

- Presidência e participação **não são papéis**: vêm de `MembroComissao`, procurado por
  `identity_subject == ator.subject` e `processo` (`comissoes/domain/autorizacao.py`) [F].
- `pode_gerir_comissao` exige que o escopo do ator seja o do Processo antes de olhar a presidência
  [F]. Esse é o ponto em que a revogação precisa morder: **quem perdeu todo vínculo na unidade não
  pode continuar presidindo por esse caminho** [I].

### 1.6 Produção

- `production.py` recusa subir com o seletor, com o provedor de demonstração do portal, com a fonte
  de demonstração do sorteio e com o adaptador provisório da API [F].
- Sem método de entrada, a gestão responde **503** com `sem_autenticacao.html` (`075`, `FR-1691`)
  [F]. É o comportamento certo para "produção sem autenticação institucional válida": bloqueado,
  sem cair para a demonstração.
- **A barreira é de inicialização, e só dela** [F]: em execução, `seletor_disponivel()` lê a chave
  sem conferir o ambiente. Uma configuração que trocasse o valor depois do *boot* — um
  `override_settings`, um *settings* de terceiros — reabriria o seletor sem que nada recusasse [I].

### 1.7 Testes que dependem do seletor

- 260 arquivos de teste identificam pela tela, pelo auxiliar `identificar` de
  `tests/interface/conftest.py`, com a chave ligada por *fixture* [F]. Nenhum deles muda nesta
  spec, e nenhum resultado esperado muda.

---

## 2. As duas alternativas

**A — Django Auth + autorização do GPS.** A pessoa é um `auth.User`. O GPS acrescenta duas coisas
que o Django não tem: a associação com identificadores externos, e o vínculo pessoa × unidade ×
papel, append-only. O `User` é **só identidade**: `is_superuser`, `is_staff`, `groups` e
`user_permissions` não autorizam nada, e não há senha utilizável.

**B — Identidade própria + adaptador.** Uma tabela `Pessoa` com UUID, o subject estável, o nome, o
e-mail e a situação; o vínculo e a revogação append-only; a sessão e a rotação dela escritas à mão,
como o portal fez com o candidato.

| Critério | **A** | **B** |
|---|---|---|
| Tabelas novas | **3**: identidade externa, vínculo, revogação | **4**: as mesmas e a Pessoa |
| Sessão, rotação na entrada, troca de usuário na mesma sessão | `login()`, que já faz `cycle_key()` e limpa a sessão de outro usuário | escrito à mão, como em `portal/identidade.py` |
| Sessão invalidada quando a pessoa é desativada | `get_user()` devolve anônimo quando `is_active` é falso (`ModelBackend.user_can_authenticate`) | escrito à mão |
| Última entrada, data de cadastro, situação | `last_login`, `date_joined`, `is_active`, nativos | colunas próprias |
| Integração futura com OIDC ou SAML | **as bibliotecas do ecossistema** (`mozilla-django-oidc`, `djangosaml2`) entregam um `User` por um *backend*; o adaptador do GPS vira um *backend* a mais [I] | Authlib, ou adaptação das mesmas bibliotecas a um modelo que elas não conhecem [I] |
| O identificador gravado nos atos | o `username`, gerado pelo GPS e tornado imutável por gatilho | a coluna `subject` da Pessoa, imutável por gatilho |
| Riscos próprios | um `createsuperuser` ou um `is_superuser=True` parecer dar acesso; o `ModelBackend` aceitar senha; alguém instalar o `admin` | código de sessão próprio, com os defeitos que o Django já corrigiu |
| Mitigação | o *backend* do GPS é o único declarado; o `Actor` ignora `is_superuser`; um teste prova que superusuário sem vínculo não entra; o `admin` não é instalado | revisão e testes do código de sessão |
| Trilha | o evento de entrada aponta para a identidade externa usada (UUID), já que o `User` tem chave inteira | o evento aponta para a Pessoa |
| Custo de troca de provedor | uma linha nova de identidade externa para a mesma pessoa | o mesmo |

**Leitura.**

- **A vence em complexidade total.** As peças que custam caro de acertar — sessão, rotação,
  desativação, troca de usuário — já estão prontas e testadas no Django. O que B escreveria à mão,
  A recebe.
- **A vence em custo futuro.** A integração real com o SSO é o próximo passo, e o caminho mais
  curto até ela passa por um *backend* de autenticação do Django. B obrigaria a adaptar a biblioteca
  ao modelo, ou a escrever o cliente OIDC.
- **Em segurança, empatam depois das mitigações.** O risco próprio de A é a aparência de que o
  `User` autoriza. Ele se fecha com três barreiras independentes: só o *backend* do GPS é
  declarado, o `Actor` é calculado só dos vínculos, e o `admin` não existe. Cada uma tem teste.
- **O que o estudo temia no Django Auth não se aplica aqui.** A rejeição do estudo era ao
  `django.contrib.admin` com `auth.User` como **fonte de autorização** — "segunda identidade, sem
  trilha do domínio". Em A, o `User` não autoriza nada, e a concessão vai à trilha pelo domínio.

## 3. Identidade interna estável

| Pergunta do pedido | Resposta |
|---|---|
| Reutilizar o ID nativo do Django? | **Não como `subject`.** O `id` inteiro é sequencial e de um banco só: o `1` da homologação não é o `1` da produção, e um `subject` "1" nos atos não diz nada fora do banco que o gerou. Ele continua sendo a chave estrangeira dos vínculos. |
| UUID? | **Sim, gerado pelo GPS, no `username`**: `pessoa-<uuid4>`. Estável, sem dado pessoal, sem depender do provedor, e de um formato que nenhuma identidade de demonstração usa. Gatilho no PostgreSQL recusa mudá-lo. |
| Associação a identificadores externos | Tabela `IdentidadeExterna`: `(provedor, identificador)` único, e uma por pessoa e provedor. **Trocar de provedor é acrescentar uma linha**, e o `subject` dos atos não muda. |
| Qual identificador do provedor usar | É a decisão 2 do estudo, e **deixou de ser irreversível**: o que vai aos atos é o identificador interno; o externo só localiza a pessoa. A recomendação continua a do estudo — o identificador imutável do provedor (`sub` do OIDC, `objectGUID`) —, e fica proposta ao usuário. |
| Preservação dos identificadores históricos | Nada nos atos muda. Os `subject` de demonstração gravados na homologação continuam os mesmos, e nenhum vira `User`. |
| Duplicidade | `(provedor, identificador)` único impede duas pessoas para a mesma conta. **Associar pelo e-mail é recusado**: o e-mail muda e se recicla, e casar contas por ele é a tomada de conta clássica. Uma segunda identidade externa para a mesma pessoa só entra por ato explícito. |
| Identidades de demonstração | **Não se convertem.** A demonstração não cria `User`; a resolução institucional nunca procura pelo texto do `subject`. As duas origens não se cruzam. |

## 4. Modos

| | Demonstração | Institucional |
|---|---|---|
| Liga por | `INTERFACE_SELETOR_IDENTIDADE=true` (como hoje) | `GESTAO_PROVEDOR_INSTITUCIONAL=<classe>` |
| Quem diz quem é | a pessoa, na tela | o provedor, por um adaptador |
| Onde moram os papéis | na sessão, escolhidos na entrada | nos vínculos, lidos a cada requisição |
| Revogação vale | no próximo login | na próxima requisição |
| Desenvolvimento e homologação | sim | sim, quando houver provedor; hoje só nos testes |
| Produção | **recusado** na inicialização e em execução | o único admitido |

## 5. Incompatibilidades encontradas

Nenhuma exige mudar a estrutura existente. Três pedem cuidado e estão tratadas na spec:

1. **A trilha exige UUID.** O agregado dos eventos de sessão é a identidade externa usada, e não o
   `User` (§1.4).
2. **Papel novo no `PAPEIS` aparece no seletor.** Os papéis de acesso ficam num catálogo próprio,
   ao lado, e o seletor continua com os oito (§1.3).
3. **Os templates mostram o `subject` cru.** Com o identificador opaco, "Continuar como
   pessoa-1b4e…" e "por pessoa-1b4e…" passam a aparecer na gestão institucional. A exibição do nome
   é pendência da ativação, e não deste incremento: ela não muda nada no seletor, e o modo
   institucional ainda não abre fora dos testes ([pendências](ativacao-do-sso-institucional.md)).
