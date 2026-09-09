# Processo Seletivo e Editais — Cefor/IFES

Sistema de gestão de Processos Seletivos e seus Editais: elaboração, homologação, Publicação
imutável, Retificações com vigência temporal e consulta pública histórica — com a interface
administrativa que conduz o fluxo e o portal por onde o candidato se inscreve e acompanha.

O projeto é conduzido por especificação, com [GitHub Spec Kit](https://github.com/github/spec-kit).
A [Constituição](.specify/memory/constitution.md) é a autoridade de engenharia e domínio; em
conflito, ela prevalece.

Para subir o sistema, vá direto a [Como rodar com Docker Compose](#como-rodar-com-docker-compose).
Quem for **mexer** no código — pessoa ou agente — comece por [`AGENTS.md`](AGENTS.md), que registra
as armadilhas que não se descobrem lendo o código.

## O que o sistema garante

- **Publicação é ato imutável.** Um Edital publicado nunca é sobrescrito. Correções ocorrem por
  Retificação, que preserva a Publicação original, cada ato e todas as versões consolidadas.
- **O passado é reproduzível.** A consulta informa o conteúdo vigente em qualquer instante, aplicando
  apenas as Retificações cuja vigência já havia iniciado. A precedência é determinada pelo início da
  vigência, não pela ordem de Publicação.
- **Nada é excluído.** Encerramento e cancelamento são atos de domínio motivados e auditados;
  preservam Publicações, documentos e histórico.
- **Negar por padrão.** Toda operação exige permissão explícita e verificação de escopo
  institucional. Quem elabora um Edital não conclui sozinho elaboração, homologação e Publicação.
- **Auditoria inviolável.** Operações críticas gravam ator, ato, estados anterior e posterior, motivo
  e correlação, em registros que nem a aplicação nem a role de runtime conseguem alterar.

## Arquitetura

Monólito modular em Python 3.13 / Django 5.2 LTS / DRF, sobre PostgreSQL. Cada módulo em
`backend/processo_seletivo/` separa domínio, aplicação, API e persistência:

| Módulo | Responsabilidade |
|---|---|
| `processos` | Processo Seletivo, Edital, atos administrativos e desfecho |
| `editais` | Perfis de Vaga, vagas, modalidades, Cronograma e validação |
| `publicacoes` | Publicação, Retificação, versões consolidadas e consulta pública |
| `seguranca` | Ator autenticado, permissões e autorização por objeto |
| `auditoria` | Registro append-only e idempotência |
| `shared` | Serialização canônica, concorrência otimista, Problem Details e observabilidade |

Operações de workflow são commands explícitos e transacionais. O controle otimista usa `ETag` /
`If-Match`; commands irreversíveis exigem `Idempotency-Key`. Erros usam `application/problem+json`.

## Requisitos

Há duas formas de subir o sistema. A containerizada é a canônica: roda igual em **macOS, Windows e
Linux**, e é a única que o CI verifica a cada push — o que significa que ela não pode apodrecer sem
alguém notar. A nativa continua válida e é mais rápida no dia a dia de quem já a tem montada.

| Caminho | Precisa de | Onde |
|---|---|---|
| **Docker Compose** | Docker Desktop (macOS, Windows) ou Docker Engine com o plugin `compose` (Linux) | as três plataformas |
| **Nativo** | Python 3.13, [uv](https://docs.astral.sh/uv/), PostgreSQL 16+ (a CI valida contra 18), `make` | macOS e Linux — no Windows, dentro do WSL2 |

## Como rodar com Docker Compose

```bash
cp backend/.env.example backend/.env
docker compose up --build
```

No PowerShell do Windows os dois comandos são exatamente estes: `cp` é apelido de `Copy-Item` e a
barra normal funciona como separador. No `cmd.exe`, troque o primeiro por
`copy backend\.env.example backend\.env`.

O que acontece nessa ordem, e por que ela é essa: o PostgreSQL sobe e é esperado até responder;
então a aplicação **provisiona os papéis, aplica as migrations e provisiona de novo**. A segunda
passada não é redundância — papel e privilégio padrão precisam existir antes de qualquer tabela, e
privilégio *sobre* tabela só pode ser concedido depois que ela existe. Ela é a que tranca. O
terminal mostra `18 de 18 tabelas append-only estão sem UPDATE nem DELETE para o runtime` quando
deu certo.

Quando o terminal parar, o sistema está em <http://localhost:8000> — use `localhost`, e não
`127.0.0.1`: o padrão de `DJANGO_ALLOWED_HOSTS` recusa o segundo. Em <http://localhost:8025> fica a
caixa de entrada do coletor de e-mail, por onde se lê o código de acesso do portal do candidato.

Para ter o que olhar, popule a demonstração (o container já está de pé, então `exec`):

```bash
docker compose exec app python manage.py seed_demo
```

Editar o código no seu editor recarrega o servidor: a árvore `backend/` é montada de dentro do
host. Para começar do zero — banco, volumes e tudo —, `docker compose down --volumes`.

**Isto é ambiente de desenvolvimento.** Segredo fraco, `DEBUG` ligado e o seletor de identidade,
que deixa qualquer pessoa declarar quem é. `config.settings.production` recusa iniciar com
qualquer um dos três.

## Como rodar nativamente

```bash
cd backend && make install
cp .env.example .env
```

Ajuste o `.env`: no mínimo `POSTGRES_USER`, que é o superusuário do seu PostgreSQL — em instalação
por Homebrew ele costuma ser o seu próprio usuário do sistema, e não `postgres`.

> **Este arquivo não é lido por mágica.** O projeto não usa `python-dotenv`; quem o carrega são os
> alvos do `Makefile` e o `docker compose`. Um `manage.py` chamado à mão fora do `make` enxerga só
> o que estiver exportado no ambiente.

Crie o banco e prepare-o. No macOS com PostgreSQL do Homebrew, exporte `LC_ALL` antes — sem ele o
`createdb` falha:

```bash
export LC_ALL=en_US.UTF-8
createdb processo_seletivo
cd backend && make preparar
```

`make preparar` faz os três passos na mesma ordem do compose e pela mesma razão. Os três são
idempotentes: rodar de novo sobre banco já preparado não faz mal.

O projeto separa a role de migração da de runtime: a de runtime não recebe `UPDATE` nem `DELETE`
sobre os registros append-only, garantia verificada em
`tests/integration/test_database_permissions.py`. A política vive em
`processo_seletivo/seguranca/papeis.py` e é a mesma que os testes de conformidade verificam. É a
segunda camada da imutabilidade, independente das triggers: a trigger recusa a mutação mesmo de
quem tem privilégio; o privilégio ausente recusa antes, mesmo que a trigger seja removida.
`make provisionar` aceita `--dry-run` pelo comando subjacente, que imprime a política sem
aplicá-la e oculta as senhas.

```bash
cd backend && make runserver
```

### Ver o sistema no ar

Há duas superfícies. A **consulta pública** é anônima: basta abrir as URLs no navegador. A
**interface administrativa** fica em `/gestao/` e conduz o fluxo inteiro — criar Processo e Edital,
compor Perfis e Cronograma, submeter, homologar, publicar, retificar e consultar a auditoria.

A interface exige identidade. Enquanto o diretório institucional não está integrado, o seletor de
identidade a substitui — e **só existe fora de produção**, onde `config.settings.production` recusa
iniciar com ele ligado. Ele vem ligado no `.env.example`; sem ele, `/gestao/` devolve 503.

Para ter o que olhar, popule uma demonstração que percorre o fluxo normativo real, com atores
distintos em cada etapa:

```bash
cd backend && make seed
```

O comando imprime os identificadores criados e as URLs prontas: versão vigente, histórico e
Retificação. Ele cria um Edital publicado com dois Perfis e três Eventos, mais duas Retificações —
uma já vigente e outra com vigência futura —, para que a consulta temporal tenha o que mostrar. Não
há como recriá-la sobre o mesmo código: apagar a demonstração exigiria excluir Publicações, o que a
Constituição proíbe e as triggers de imutabilidade recusam. Use outro `--codigo`.

O portal do candidato envia código de acesso por e-mail. No compose há um coletor de SMTP junto:
a mensagem chega em <http://localhost:8025>, e é de lá que se lê o código. Nativamente o backend de
e-mail é o de console — **a mensagem é impressa no terminal onde o servidor está rodando**, e é
preciso garimpá-la no log.

## Antes de receber dado pessoal real

A `009` abriu o sistema para inscrições, e com elas entram nome, CPF, e-mail, telefone e documentos
comprobatórios. Três precondições, nenhuma delas de código:

- **política institucional de retenção e descarte** — a feature minimiza a coleta e não implementa
  expurgo automático; sem a política, o acervo só cresce, inclusive com rascunhos que ninguém
  enviou;
- **provedor de identidade real** no lugar do de demonstração, que deixa qualquer pessoa declarar
  quem é (produção recusa subir com ele ligado);
- **raiz privada de arquivos** declarada, absoluta, fora da árvore do código, com backup e
  restrição de acesso no sistema operacional.

## Produção

`config.settings.production` trata cada pressuposto de segurança como precondição de
inicialização: chave secreta fraca ou ausente, `DJANGO_ALLOWED_HOSTS` vazio ou `*`, HTTPS
desligado, banco sem senha, seletor de identidade ligado ou o adaptador provisório de
autenticação impedem o processo de subir, com mensagem que nomeia a variável a corrigir.

O adaptador `InstitutionalBearerAuthentication` aceita `subject|escopo|permissões` sem assinatura
— qualquer cliente declara a própria identidade **e as próprias permissões**. Por isso
`API_AUTHENTICATION_CLASSES` é obrigatória e recusa o módulo de autenticação de desenvolvimento
inteiro, os esquemas do DRF que autenticam contra esta aplicação em vez do diretório, e nomes que
não sejam importáveis.

O que a barreira **não** faz: provar que a classe declarada fale com o diretório do Ifes. Nenhuma
configuração prova isso. Ela garante que a escolha seja explícita, exista, e não seja um dos
caminhos conhecidamente inseguros — a responsabilidade pela escolha continua de quem implanta.

```bash
cd backend && DJANGO_SETTINGS_MODULE=config.settings.production uv run python manage.py check --deploy
```

## Verificação

```bash
cd backend && make lint check test-pg
```

No ambiente containerizado, o mesmo de dentro dele, com o banco que já está de pé:

```bash
docker compose exec app make lint check test-pg
```

`test-pg` e não `test`: **a suíte precisa do PostgreSQL.** Sem variável nenhuma ela cai para
SQLite, e nesse modo não é confiável — 182 testes são pulados e **21 falham**, porque executam SQL
de PostgreSQL sob SQLite em casos que deveriam ter sido pulados e não foram. O CI não enxerga isso,
porque só roda contra PostgreSQL. O achado está em
[`doc/achado-suite-em-sqlite.md`](doc/achado-suite-em-sqlite.md).

Contra PostgreSQL a suíte fecha em 3957 passando e 1 pulado. O alvo `test-pg` monta a conexão a
partir do `POSTGRES_USER` do seu `.env`; à mão, fora do `make`, são necessárias as **duas**
variáveis — sem `TEST_DB_ENGINE=postgresql` a suíte cai para SQLite, e sem `DB_USER` ela tenta
conectar como a role de runtime, que não pode criar banco de teste:

```bash
cd backend && TEST_DB_ENGINE=postgresql DB_NAME=processo_seletivo_test DB_USER=postgres DB_PASSWORD=postgres DB_HOST=localhost DB_PORT=5432 uv run pytest
```

Se houver mais de uma worktree rodando a suíte ao mesmo tempo, dê a cada uma seu próprio `DB_NAME`:
elas disputam o mesmo banco de teste e se derrubam.

Suítes por marcador: `acceptance` (cenários rastreados), `contract` (conformidade HTTP/OpenAPI),
`integration` (persistência, locks e concorrência), `authorization` (autorização e anti-IDOR) e
`performance` (custo de consulta e escalabilidade).

O SLO de carga do `plan.md` depende de serviço implantado e não é verificado pela suíte. Meça-o com:

```bash
cd backend && uv run python scripts/carga_publica.py --base-url https://host/api/v1 --edital <uuid> --workers 50 --duracao 60
```

## API

O contrato é [`specs/001-processo-seletivo-editais/contracts/openapi.yaml`](specs/001-processo-seletivo-editais/contracts/openapi.yaml),
em OpenAPI 3.1. `tests/contract/test_openapi_conformance.py` falha se alguma operação especificada
ficar sem rota, se alguma rota for exposta fora do contrato ou se uma resposta divergir do schema.

- `/api/v1/admin/…` — commands administrativos, exigem autorização
- `/api/v1/public/…` — consulta pública anônima, somente conteúdo publicado

A autenticação atual é um adaptador de desenvolvimento: `Bearer <subject>|<escopo>|<permissões>`.
A integração institucional será definida em incremento próprio.

### Endpoints operacionais

Ficam fora de `/api/v1` por não serem contrato institucional:

| Rota | Uso |
|---|---|
| `GET /health` | Liveness — responde sem tocar no banco |
| `GET /readiness` | Readiness — `503` se o banco não responder ou houver migration pendente |
| `GET /metrics` | Contadores de conflito e recusa; exige `observabilidade:consultar` |

Os logs saem em JSON, uma linha por evento, com o `correlationId` que liga log e auditoria. Nenhum
campo carrega token, permissão ou conteúdo normativo.

## Estado do projeto

As sete histórias da feature `001-processo-seletivo-editais` estão implementadas e rastreadas.

- [`traceability.md`](specs/001-processo-seletivo-editais/traceability.md) — 38 requisitos ativos, 29
  cenários e 10 critérios de sucesso, com as lacunas conhecidas
- [`validation-report.md`](specs/001-processo-seletivo-editais/validation-report.md) — execução dos 15
  cenários do quickstart

Todas as tarefas de `tasks.md` estão fechadas e os 38 requisitos ativos estão implementados. Restam
dois pontos antes de declarar a feature concluída: o SLO de carga precisa ser medido em ambiente
implantado, e a Regra Normativa é registrada mas ainda não aplicada — detalhes nos dois artefatos
acima.

O projeto seguiu bastante além dela: a interface administrativa, o portal do candidato, a inscrição,
a avaliação, a classificação, a publicação de resultados e os recursos são incrementos próprios,
listados abaixo. O estado de cada um está na pasta do incremento, e não aqui — este parágrafo
descreve a `001`.

## Documentação

O projeto usa [GitHub Spec Kit](https://github.com/github/spec-kit). Cada incremento tem sua pasta
em `specs/`, com os mesmos artefatos:

| Artefato | Conteúdo |
|---|---|
| `spec.md` | Requisitos, cenários e critérios de sucesso |
| `plan.md` | Decisões técnicas e verificação constitucional |
| `research.md` | O que foi investigado e o que foi descartado |
| `data-model.md` | Entidades, invariantes e regras |
| `tasks.md` | Tarefas por história |
| `quickstart.md` | Guia de validação |
| `checklists/requirements.md` | Análise de consistência entre os artefatos |

Incrementos, na ordem em que foram especificados:

| | |
|---|---|
| [`001`](specs/001-processo-seletivo-editais/spec.md) | backend do ciclo normativo |
| [`002`](specs/002-frontend-administrativo/spec.md) | interface administrativa |
| [`003`](specs/003-integridade-e-prontidao/spec.md) | integridade normativa e prontidão |
| [`004`](specs/004-enderecamento-normativo-estavel/spec.md) | endereçamento por chave estável |
| [`005`](specs/005-integridade-do-snapshot/spec.md) | integridade do snapshot |
| [`006`](specs/006-elaboracao-completa-edital/spec.md) | elaboração completa do Edital |
| [`007`](specs/007-edital-institucional/spec.md) | Edital institucional |
| [`008`](specs/008-composicao-institucional/spec.md) | composição institucional |
| [`009`](specs/009-inscricao-simples-documentos/spec.md) | inscrição e documentos do candidato |
| [`010`](specs/010-area-do-candidato/spec.md) | área do candidato e acesso sem senha |
| [`011`](specs/011-comissao-alocacao/spec.md) | comissão e alocação por Etapa |
| [`012`](specs/012-mesa-de-avaliacao/spec.md) | mesa de avaliação |
| [`012`](specs/012-013-revisao-formas-de-conclusao/spec.md) | revisão de compatibilidade 012–013 |
| [`013`](specs/013-consolidacao-resultado-etapa/spec.md) | consolidação do Resultado da Etapa |
| [`015`](specs/015-ordenacao-e-classificacao/spec.md) | ordenação e classificação |
| [`017`](specs/017-publicacao-de-resultados/spec.md) | publicação de resultados |
| [`018`](specs/018-recursos-e-superacao-de-resultados/spec.md) | recursos e superação de resultados |
| [`020`](specs/020-anexos-do-edital/spec.md) | anexos do Edital |

A [Constituição](.specify/memory/constitution.md) prevalece sobre todos.

### Spec Kit com dois agentes

Os comandos do Spec Kit vivem em **um lugar só**, `.agents/skills/speckit-*/`, instalados pela
integração `codex`. O Claude Code os enxerga por symlinks relativos em `.claude/skills/`, que
apontam para lá — mesma fonte, sem duplicação e sem risco de as duas cópias divergirem.

Depois de `specify integration upgrade`, refaça os symlinks caso alguma skill tenha sido
acrescentada:

```bash
for d in .agents/skills/*/; do n=$(basename "$d"); ln -sfn "../../.agents/skills/$n" ".claude/skills/$n"; done
```

Os scripts auxiliares estão em `.specify/scripts/bash/`. `.specify/scripts/powershell/` continua
no manifesto da ferramenta e é ignorado nesta plataforma — removê-lo à mão faria o
`specify integration status` acusar arquivo gerenciado ausente.

`.specify/feature.json` aponta para a feature ativa e é **por checkout**: não entra no git, e cada
worktree tem o seu.
