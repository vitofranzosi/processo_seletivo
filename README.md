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
| `editais` | Perfis de Vaga, quadro de vagas, Modalidades, Cronograma, Etapas, documentos exigidos, Anexos e validação |
| `publicacoes` | Publicação, Retificação, versões consolidadas, documento publicado e consulta pública |
| `identidade` | Identidade do candidato, acesso sem senha por código enviado ao e-mail e reconciliação com a participação anterior |
| `inscricoes` | Inscrição, período de inscrições, documentos enviados e fatos declarados pelo candidato |
| `comissoes` | Comissão do Processo e alocação dos membros às Etapas |
| `avaliacoes` | Distribuição das atribuições, Mesa de avaliação, impedimento e conclusão |
| `resultados` | Resultado da Etapa: consolidação, Ocorrência e progressão entre Etapas |
| `classificacao` | Ordenação, corte entre Etapas e o ato de classificação |
| `sorteios` | Relação de habilitados congelada, ocorrência da fonte externa e o sorteio auditável |
| `ocupacao` | Apuração da ocupação e movimento de vagas entre listas de concorrência |
| `divulgacao` | Publicação de resultado, a porta da definitividade, a situação individual divulgada e o documento dela |
| `recursos` | Recurso, juízo de admissibilidade, instrução e decisão |
| `convocacao` | Convocação, chamada, suplência e desfecho |
| `requerimentos` | Requerimento de Matrícula e base local de referência de CEP |
| `matriculas` | Exportação para o Registro Acadêmico — registra a geração, e não guarda o arquivo |
| `unidades` | Unidades institucionais e autoridades habilitadas: o que o documento diz da unidade e quem pode responder pelos atos dela |
| `avisos` | Avisos complementares aos candidatos sobre atos publicados: destinatários tirados do ato, modelos da unidade e o despacho periódico, que registra o que o servidor de correio aceitou |
| `duvidas` | Fonte de consulta do assistente de dúvidas: respostas às perguntas sugeridas sobre o Edital vigente, com a versão, a natureza e o ato de origem de cada informação, só de leitura. E o piloto interno do assistente: a pergunta livre ao modelo sobre essas fontes, conferida pela aplicação antes de aparecer, com as trocas registradas para a avaliação numa tabela que se exclui por prazo |
| `interface` | Interface administrativa, em `/gestao/`: composição, Retificação e condução do Processo |
| `portal` | Consulta pública e área do candidato, em `/selecoes/`: vitrine, inscrição, acompanhamento e recurso |
| `seguranca` | Ator autenticado, permissões, autorização por objeto e papéis do banco |
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
terminal mostra `N de N tabelas append-only estão sem UPDATE nem DELETE para o runtime`, com os dois
números iguais, quando deu certo. O total cresce a cada tabela append-only nova — por isso nenhum
número vai escrito aqui —, e o que denuncia a segunda passada que não rodou é o primeiro vir `0`.

Quando o terminal parar, o sistema está em <http://localhost:8000>. Prefira `localhost`: o
`.env.example` aceita também `127.0.0.1`, mas o padrão do código, sem `.env`, aceita só o primeiro —
e é `localhost` que o `seed_demo` imprime. Em <http://localhost:8025> fica a caixa de entrada do
coletor de e-mail, por onde se lê o código de acesso do portal do candidato.

Para ter o que olhar, popule a demonstração (o container já está de pé, então `exec`):

```bash
docker compose exec app python manage.py seed_demo
```

Editar o código no seu editor recarrega o servidor: a árvore `backend/` é montada de dentro do
host. Para começar do zero — banco, volumes e tudo —, `docker compose down --volumes`.

**Isto é ambiente de desenvolvimento.** Segredo fraco, `DEBUG` ligado e três substitutos de
demonstração: o seletor de identidade da gestão e o provedor de identidade do portal, que deixam
qualquer pessoa declarar quem é, e a fonte de sorteio de semente fixa. `config.settings.production`
desliga o `DEBUG` e recusa iniciar com a chave fraca ou com qualquer um dos três substitutos.

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

`make preparar` faz os três passos na mesma ordem do compose e pela mesma razão, e depois
sincroniza o registro de Unidades declarado em `unidades/unidades.json` (060). Os quatro são
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

A base local de referência de CEP, que o Requerimento de Matrícula consulta, **não entra no
`preparar`**, e de propósito: são 379 MB que não cabem em cada máquina de desenvolvimento nem em
cada banco de teste. Sem ela nada bloqueia: o candidato digita o endereço inteiro, o código IBGE do
município fica vazio, e o envio conclui. Quem precisa dela roda `make ceps` uma vez, com o arquivo da base em `CEPS_ZIP`; a
origem do arquivo, a atualização mensal e a conferência estão em
[`doc/runbook-base-de-cep.md`](doc/runbook-base-de-cep.md).

### Ver o sistema no ar

Há duas superfícies. O **portal**, em `/selecoes/`, é onde o público consulta Editais, resultados
e sorteios sem autenticação, e onde o candidato entra com código enviado ao e-mail para se
inscrever, recorrer e requerer matrícula. A **interface administrativa** fica em `/gestao/` e conduz
o fluxo inteiro — criar Processo e Edital, compor Perfis e Cronograma, submeter, homologar,
publicar, retificar, avaliar, classificar, divulgar resultados, julgar recursos, convocar, exportar
matrículas e consultar a auditoria.

A interface exige identidade. Enquanto o diretório institucional não está integrado, o seletor de
identidade a substitui — e **só existe fora de produção**, onde `config.settings.production` recusa
iniciar com ele ligado. Ele vem ligado no `.env.example`; sem ele, `/gestao/` devolve 503.

Para ter o que olhar, popule uma demonstração que percorre o fluxo normativo real, com atores
distintos em cada etapa:

```bash
cd backend && make seed
```

O comando imprime os identificadores criados e as URLs prontas. Cada Edital mostra um momento do
certame, porque inscrição aberta e resultado divulgado não cabem no mesmo:

- o **primeiro**, publicado e com inscrições abertas, traz Anexos, o Requerimento de Matrícula
  declarado e duas Retificações — uma já vigente e outra com vigência futura —, para que a consulta temporal tenha o
  que mostrar;
- o **segundo**, com inscrições encerradas, percorre avaliação, classificação, resultado
  divulgado, corte, ocupação, convocação e Requerimento de Matrícula;
- o **terceiro** ordena por sorteio, com a relação congelada, a ocorrência observada e o sorteio
  verificável;
- o **quarto**, reaproveitado do segundo num Processo do ano seguinte, fica em elaboração: o
  Cronograma copiado já venceu, e o sistema recusa publicá-lo.

`--dias-atras N` roda a demonstração como se tivesse ocorrido há N dias, para exibir um prazo
recursal já encerrado. Não há como recriá-la sobre o mesmo código: apagar a demonstração exigiria
excluir Publicações, o que a Constituição proíbe e as triggers de imutabilidade recusam. Use outro
`--codigo` — e, para o quarto Edital, outro `--numero` ou `--ano`.

O portal do candidato envia código de acesso por e-mail. No compose há um coletor de SMTP junto:
a mensagem chega em <http://localhost:8025>, e é de lá que se lê o código. Nativamente o backend de
e-mail é o de console — **a mensagem é impressa no terminal onde o servidor está rodando**, e é
preciso garimpá-la no log.

Os avisos complementares aos candidatos (066) **não saem no clique**. A confirmação grava o aviso e
responde; quem envia é `manage.py despachar_avisos`, que em produção roda num timer a cada minuto e
em desenvolvimento ninguém roda por você. Depois de confirmar um aviso, rode-o à mão. O `make` não
tem alvo para ele, e o `.env` precisa ser exportado antes:

```bash
cd backend && set -a && . ./.env && set +a && uv run python manage.py despachar_avisos
```

No compose, `docker compose exec app python manage.py despachar_avisos`. Nativamente a mensagem sai
no terminal **do comando**, e não no do servidor; no compose, chega em <http://localhost:8025>.

## Antes de receber dado pessoal real

A `009` abriu o sistema para inscrições, e com elas entram nome, CPF, e-mail, telefone e documentos
comprobatórios; a `029` acrescentou endereço e os dados do Requerimento de Matrícula, e a `031` os
entrega ao Registro Acadêmico num arquivo que o sistema monta e não guarda. Precondições, nenhuma
delas de código:

- **política institucional de retenção e descarte** — o sistema minimiza a coleta e não implementa
  expurgo automático; sem a política, o acervo só cresce, inclusive com rascunhos que ninguém
  enviou;
- **autenticação institucional real** na gestão, no lugar do seletor de identidade, que deixa
  qualquer pessoa declarar quem é (produção recusa subir com ele ligado). O candidato já não se
  declara: desde a `010`, prova o controle do endereço de e-mail — o que exige um servidor de
  correio que entregue;
- **raiz privada de arquivos** declarada, absoluta, fora da árvore do código, com backup e
  restrição de acesso no sistema operacional.

## Produção

`config.settings.production` trata cada pressuposto de segurança como precondição de
inicialização, e recusa subir com mensagem que nomeia a variável a corrigir:

- chave secreta fraca ou ausente, `DJANGO_ALLOWED_HOSTS` vazio ou `*`, HTTPS ou HSTS desligados,
  banco sem senha;
- qualquer substituto de demonstração ligado — seletor de identidade da gestão, provedor de
  identidade do portal, fonte de sorteio de semente fixa;
- raiz de arquivos do candidato ausente, relativa ou dentro da árvore do código;
- backend de e-mail que não entrega (console, arquivo, memória ou nulo), remetente vazio, ou o
  backend SMTP sem `EMAIL_HOST` — sem entrega, o código de acesso iria para o log do servidor, e sem
  servidor só o primeiro envio acusaria;
- `PORTAL_ATRAS_DE_PROXY` não declarado, porque o limite de solicitações por origem depende da
  topologia, e `PORTAL_ATENDIMENTO` vazio, porque duas telas do candidato mandam procurá-lo;
- `API_AUTHENTICATION_CLASSES` ausente ou apontando para o adaptador provisório.

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

**Configurar o correio e o Ollama, e comprovar que funcionam**, é a §10.4 do
[guia de implantação](doc/implantacao-em-producao-ubuntu.md#104-configurar-verificar-e-testar-o-correio-e-o-ollama).
Ela usa só o que a release já traz, em níveis que não se confundem:

- ler a configuração, sem imprimir segredo;
- conexão, segurança e conta do correio, sem enviar;
- versão e modelo do Ollama, sem inferência;
- o envio de teste e a inferência efetiva.

Os mesmos exemplos rodam em desenvolvimento por `uv run python manage.py shell -v 0 -c '…'`. Lá a
primeira linha diz `config.settings.development`, o correio é o de console (ou o coletor do
compose) e o OpenRouter é admitido. A troca entre OpenRouter e Ollama na máquina da equipe está em
[`doc/troca-do-servico-do-assistente.md`](doc/troca-do-servico-do-assistente.md).

O passo a passo de implantação numa VM Ubuntu — arquitetura, hardening, backup e restauração,
atualização, rollback, runbook e checklist de go-live —, com os bloqueadores que ainda impedem a
entrada em produção, está em [`doc/implantacao-em-producao-ubuntu.md`](doc/implantacao-em-producao-ubuntu.md).

## Verificação

```bash
cd backend && make lint check test-pg
```

No ambiente containerizado, o mesmo de dentro dele, com o banco que já está de pé:

```bash
docker compose exec app make lint check test-pg
```

`test-pg` e não `test`: **a suíte precisa do PostgreSQL.** Sem variável nenhuma ela cai para
SQLite, e nesse modo não é confiável — uma parte dos casos falha, em vez de ser pulada: uns executam
SQL que só o PostgreSQL entende, outros esperam mensagem de constraint que o SQLite não escreve,
outros ainda contam com gatilho e trancamento de linha que ele não tem. O CI não enxerga isso,
porque só roda contra PostgreSQL. O achado original está em
[`doc/achado-suite-em-sqlite.md`](doc/achado-suite-em-sqlite.md).

Contra PostgreSQL a suíte fecha sem falha, e os pulados são deliberados. **As contagens medidas dos
dois modos, e a repartição das causas, ficam num lugar só: o [`AGENTS.md`](AGENTS.md).** Este
arquivo as repetia com números de semanas antes, e o README, o `Makefile` e as instruções dos
agentes chegaram a dizer três coisas diferentes ao mesmo tempo.
O alvo `test-pg` monta a conexão a partir do `POSTGRES_USER` do seu `.env`; à mão, fora do `make`,
são necessárias as **duas** variáveis — sem `TEST_DB_ENGINE=postgresql` a suíte cai para SQLite, e
sem `DB_USER` ela tenta conectar como a role de runtime, que não pode criar banco de teste. Isso vale
com `DB_RUNTIME_USER` fora do ambiente: quando ele está definido, as settings o preferem a `DB_USER`
(`config/settings/base.py`), e é ele que precisa apontar para o superusuário — é o que o `make` faz:

**As jornadas da gestão de acessos rodam num navegador de verdade** (107): os testes de
`backend/tests/navegador/` sobem o servidor da suíte e dirigem um Chromium pelo Playwright, do grupo
opcional `navegador` — sem ele, pulam. Para assistir a elas, com o navegador na tela:

```bash
cd backend && uv sync --extra dev --extra navegador && uv run playwright install chromium && make test-navegador
```

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

As rodadas de avaliação e as medições do piloto do assistente (`071`) também ficam fora da suíte,
contra o serviço real: o roteiro está no
[quickstart da `071`](specs/071-piloto-assistente-do-edital/quickstart.md).

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
a avaliação, a classificação, a publicação de resultados, os recursos, o sorteio, a convocação, o
Requerimento de Matrícula e a condução do Processo publicado são incrementos próprios, listados
abaixo. O estado de cada um está na pasta do incremento, e não aqui — este parágrafo descreve a
`001`. Auditorias, achados e decisões que atravessam incrementos ficam em [`doc/`](doc/).

**O sistema não está em produção.** A gestão não tem autenticação institucional — sem o seletor de
identidade de desenvolvimento, `/gestao/` responde 503 — e ainda não existe a política de retenção que
a seção [Antes de receber dado pessoal real](#antes-de-receber-dado-pessoal-real) exige. O retrato
mais recente do que está pronto, do que falta e do que depende de decisão é a
[auditoria de consolidação de 15/10/2026](doc/auditoria-de-consolidacao-2026-10-15.md), com a matriz
de pendências, o roadmap proposto e as decisões pendentes.

## Documentação

**Para quem usa o sistema:** a [Visão do Sistema](docs/visao-sistema/index.html) é o material de uso
vigente — tutorial, papéis, o que se configura, perguntas frequentes —, revisado por ciclos. Dentro do
sistema, ela abre pelo item "Documentação do Sistema" da barra da gestão, em `/gestao/documentacao/`
(`105`): servida sob a política de conteúdo, ela não pode ter estilo nem script embutidos, e todo
arquivo novo que pedir precisa entrar na lista de `interface/documentacao.py`. O manual
de operação por papel está planejado em [`doc/manual/`](doc/manual/00-arquitetura-do-manual.md) e
ainda não foi produzido. A implantação está em
[`doc/implantacao-em-producao-ubuntu.md`](doc/implantacao-em-producao-ubuntu.md).

**Para quem desenvolve:**

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
| [`012-013`](specs/012-013-revisao-formas-de-conclusao/spec.md) | revisão de compatibilidade 012–013 |
| [`013`](specs/013-consolidacao-resultado-etapa/spec.md) | consolidação do Resultado da Etapa |
| [`014`](specs/014-corte-e-progressao-entre-etapas/spec.md) | corte e progressão entre Etapas |
| [`015`](specs/015-ordenacao-e-classificacao/spec.md) | ordenação e classificação |
| [`016`](specs/016-ocupacao-de-vagas/spec.md) | ocupação de vagas entre listas de concorrência |
| [`017`](specs/017-publicacao-de-resultados/spec.md) | publicação de resultados |
| [`018`](specs/018-recursos-e-superacao-de-resultados/spec.md) | recursos e superação de resultados |
| [`019`](specs/019-convocacao-chamada-suplencia/spec.md) | convocação, chamada e suplência |
| [`020`](specs/020-anexos-do-edital/spec.md) | anexos do Edital |
| [`021`](specs/021-sorteio-publico-auditavel/spec.md) | sorteio público auditável |
| [`022`](specs/022-supervisao-do-processo/spec.md) | supervisão do Processo |
| [`023`](specs/023-criar-a-partir-de-edital-anterior/spec.md) | criar Edital a partir de Edital anterior |
| [`024`](specs/024-descoberta-e-transparencia-no-portal/spec.md) | descoberta e transparência no portal público |
| [`025`](specs/025-quadro-de-vagas-por-modalidade/spec.md) | quadro de vagas por modalidade |
| [`026`](specs/026-contrato-de-mutabilidade-normativa/spec.md) | contrato de mutabilidade normativa |
| [`027`](specs/027-estrutural-de-vagas/spec.md) | estrutural de vagas numa declaração só |
| [`028`](specs/028-cronograma-reaproveitado-vencido/spec.md) | Cronograma reaproveitado não nasce publicável |
| [`029`](specs/029-requerimento-de-matricula/spec.md) | Requerimento de Matrícula |
| [`030`](specs/030-composicao-que-se-explica/spec.md) | composição que se explica |
| [`031`](specs/031-exportacao-de-matriculas/spec.md) | exportação de matrículas para o Registro Acadêmico |
| [`032`](specs/032-executabilidade-antes-de-publicar/spec.md) | executabilidade antes de publicar |
| [`033`](specs/033-navegacao-por-capacidade/spec.md) | navegação por capacidade |
| [`034`](specs/034-ordem-por-recorte/spec.md) | ordem por recorte em marco computado |
| [`035`](specs/035-sorteio-executavel/spec.md) | sorteio executável |
| [`036`](specs/036-instrucao-do-recurso/spec.md) | instrução do recurso |
| [`037`](specs/037-quatro-becos-conhecidos/spec.md) | quatro becos que o sistema já conhecia |
| [`038`](specs/038-painel-de-conducao/spec.md) | painel de condução do Processo vivo |
| [`039`](specs/039-catalogo-de-modalidades/spec.md) | catálogo de Modalidades do Edital — só especificada, não implementada |
| [`040`](specs/040-visao-institucional-dos-processos/spec.md) | visão institucional dos Processos |
| [`041`](specs/041-perfil-na-visao-institucional/spec.md) | Perfil de Vaga na visão institucional |
| [`042`](specs/042-hierarquia-do-detalhe-do-perfil/spec.md) | hierarquia do detalhe do Perfil |
| [`043`](specs/043-duplicar-perfil/spec.md) | duplicar Perfil |
| [`044`](specs/044-recorte-transversal-documental/spec.md) | recorte transversal do documento exigido |
| [`045`](specs/045-conducao-confiavel-processo/spec.md) | condução confiável do Processo vivo |
| [`046`](specs/046-contrato-de-executabilidade/spec.md) | contrato de executabilidade do Processo publicado |
| [`047`](specs/047-situacao-publica-do-edital/spec.md) | situação pública e histórico oficial do Edital |
| [`048`](specs/048-retificacao-que-acrescenta/spec.md) | Retificação que acrescenta |
| [`049`](specs/049-operar-por-marco/spec.md) | condução do resultado por marco: indicador e gestos sobre todos os recortes |
| [`050`](specs/050-convocacao-como-fluxo/spec.md) | a convocação como fluxo: titulares num ato, não atendimento dos vencidos num gesto |
| [`051`](specs/051-padroes-e-aplicar-a-todos/spec.md) | padrões do Edital e "aplicar a todos" na composição, com a prévia do alcance e a origem na Revisão, e na Retificação, campo a campo, num ato só e com a conferência agrupada |
| [`052`](specs/052-perfis-visao-do-conjunto/spec.md) | Perfis de Vaga: a tabela do conjunto e um cartão à vista por vez, sobre o mesmo formulário |
| [`053`](specs/053-classificacao-visao-do-conjunto/spec.md) | Classificação: a tabela dos Perfis com os marcos, a origem do "aplicar a todos" e um Perfil à vista por vez, sobre o mesmo formulário |
| [`054`](specs/054-edital-como-ato-oficial/spec.md) | O Edital do sistema como ato oficial: o catálogo de 22 seções das famílias do Cefor, sem redação padrão; o fecho com local, data e ato de nomeação; o consolidado datado; a declaração do Requerimento; o total de vagas |
| [`055`](specs/055-polish-folha-e-componentes/spec.md) | Polish da folha e dos componentes (lote 1 da auditoria de polish): os números da Ocupação e do Corte em blocos; célula de tabela mais justa; uma altura para botões, ações de barra e controles; títulos em escala; a barra de filtro alinhada pelo topo; a seleção sem o vão do sorteio; campos com a largura do conteúdo |
| [`056`](specs/056-polish-assistente-de-composicao/spec.md) | Polish do assistente de composição (lote 2 da auditoria de polish): o stepper numa linha; as ações do cartão na linha da legenda, e a legenda dizendo qual item é; o Evento com as datas lado a lado; o Conteúdo do Edital compacto; a Revisão com os rótulos numa coluna; texto longo em área de texto; Anexos na largura das outras etapas; o Perfil do Retificar na ordem do Compor |
| [`057`](specs/057-polish-telas-de-operacao/spec.md) | Polish das telas de operação (lote 3 da auditoria de polish): uma ação em destaque no Detalhe do Edital e na Condução do marco, com Encerrar e Cancelar por último e só contornados; a Lista de Editais com as ações frequentes primeiro; o glossário das telas de marco recolhido; Atenção, Auditoria e documentos da inscrição sem caixa dentro de caixa; números, datas e plurais como gente escreve; a matriz de Alocação cabendo na janela; o envio de documento do portal numa linha |
| [`058`](specs/058-polish-residuos/spec.md) | Polish, os resíduos dos três lotes: os atos irreversíveis do Processo contornados e à parte, como os do Edital; a Lista de Editais e a Condução do marco com moldura que rola em tela estreita; a seção das Matrículas empilhada; a nota dos Resultados à direita; plurais de tela no número deles; os números das Etapas sem zeros; a coluna de rótulos da Revisão com largura única; o motivo de sucessão com o mesmo controle nas quatro telas |
| [`059`](specs/059-acesso-a-convocacao/spec.md) | O caminho do candidato até a convocação e o Requerimento de Matrícula: "Minhas inscrições" indica a convocação aberta e leva a ela com "Ver convocação"; o acompanhamento ganha a seção da convocação, aberta ou concluída; a convocação e essa seção oferecem "Preencher Requerimento de Matrícula" quando o Edital o pede na convocação; a recusa uniforme da titularidade provada nos caminhos novos |
| [`060`](specs/060-unidades-e-autoridades/spec.md) | Unidades institucionais e autoridades de publicação: o escopo institucional ganha Unidade registrada, o documento oficial diz a unidade do Edital no cabeçalho e no local, e a autoridade é escolhida entre as habilitadas e vigentes da unidade, cadastradas pelo Gestor da unidade, sem mudar o código e sem excluir nada |
| [`061`](specs/061-corte-apos-recurso/spec.md) | O corte emitido depois do recurso não nasce obsoleto: o reingresso que obsoleta a faixa é o de Resultado sucessor que o ato de ordenação lido ainda não cita; o deferimento já considerado pela ordem sucessora deixa de travar a Etapa governada e a publicação, e o recurso deferido depois do corte continua obsoletando-o |
| [`062`](specs/062-resultados-por-perfil-etapa-lista/spec.md) | Resultados divulgados por Perfil, etapa e lista: a página pública do Edital agrupa os resultados como a seção Vagas, com natureza e data na linha de cada lista, um histórico recolhido por etapa e o nome acessível de cada link levando etapa e Perfil; um convite separado leva à situação individual, e voltar ao Edital depois de entrar não pede nome e CPF |
| [`063`](specs/063-acompanhamento-pela-situacao/spec.md) | Acompanhamento pela situação do candidato: o topo da área da inscrição diz a situação, de que ato ela decorre e o que fazer — "Aguardando chamada", "Convocado", "Vaga aceita" —, derivada só de convocação, desfecho, resultado de etapa e classificação divulgada, nunca da posição; cada lista ganha cartão próprio com a posição oficial, e nenhuma frase promete perda ou vaga que o ato não declarou |
| [`064`](specs/064-atribuicoes-consolidadas/spec.md) | As atribuições idênticas saem uma vez no documento do Edital: Perfis de texto integralmente igual remetem a uma subseção comum ao fim da seção de Perfis, que nomeia os códigos; a numeração dos Perfis, das seções e das tabelas não muda, e nenhum dado, tela ou documento já publicado muda |
| [`065`](specs/065-conflitos-de-numeracao/spec.md) | Conflitos de numeração no Edital: o subitem digitado com número de outra seção impede a submissão e a publicação, e a etapa Conteúdo e a Revisão o acusam com seção, parágrafo e trecho, levando à legenda da seção; a remissão que aponta para mais de um item, para nenhum ou para o lugar errado é aviso, em todo texto impresso; na Retificação tudo é aviso; nada é renumerado, o PDF não muda e nenhum Edital publicado é reavaliado |
| [`066`](specs/066-avisos-complementares/spec.md) | Avisos complementares aos candidatos, vinculados a ato oficial: a seleção avisa por e-mail quem um resultado publicado, sua retificação ou uma chamada comunicada por publicação alcançou — os destinatários saem do ato, e ninguém acrescenta nem tira —, com texto próprio e modelos da unidade; o aviso não produz efeito sobre prazo, situação ou direito, sai por despacho periódico fora da requisição, com a tentativa gravada antes do servidor de correio e o resultado indeterminado nunca reenviado sozinho, e fica desligado em produção até a validação de LGPD |
| [`067`](specs/067-correcoes-de-norma-do-edital/spec.md) | Correções de norma do Edital em PDF (ED-02, ED-03 e ED-12 da auditoria de 08/10): a frase de recurso do marco nomeia o resultado de que se recorre, e a Revisão avisa — sem impedir — com os prazos dos marcos ao lado dos Eventos de recurso do Cronograma; sob sorteio, o arredondamento deixa de ser exigido e, com o empate no corte, de ser impresso; o Perfil sem vaga imediata não imprime quadro de zeros nem reversão; nenhum documento já publicado muda |
| [`068`](specs/068-consolidacao-por-perfil/spec.md) | O que se repete por Perfil sai uma vez no Edital em PDF (ED-04 e ED-11 da auditoria de 08/10): com dois ou mais Perfis, as vagas numa tabela Perfil × lista e as modalidades em tabelas agrupadas, na ordem do quadro; reversão e convocação uma vez; requisitos e marcos idênticos em subseções comuns depois do último Perfil, com a frase que aplica os marcos a cada Perfil separadamente; o método comum do sorteio uma vez. Nenhuma regra muda, e a equivalência é provada Perfil a Perfil; a numeração das tabelas muda; o Edital de um Perfil e os documentos já publicados não mudam |
| [`069`](specs/069-edital-linguagem-simples/spec.md) | O Edital oficial em linguagem simples, lote 1: as frases geradas na redação 2, sem rótulos internos, e a redação gravada no ato para a página do ato de ordenação; os Editais novos organizados pelas perguntas do candidato (catálogo com títulos e ordem novos, as chaves iguais), com seções reunidas, resumo feito só de dado, sumário e agrupamento por identidade; fonte embutida (Edital Sans, OFL), hierarquia tipográfica, paginação com equilíbrio e a última seção junto do fecho; título, idioma, marcadores, links e nome do arquivo. Os publicados antes não mudam, e os consolidados deles mantêm a estrutura do original; o PDF continua sem marcação |
| [`070`](specs/070-fonte-de-consulta-do-edital/spec.md) | Fase A do assistente de dúvidas do Edital: na gestão, a validação interna das respostas a doze perguntas sugeridas sobre o Edital vigente no instante consultado — com a versão, o tipo da resposta, cartões que separam texto do Edital, dado e explicação, e cada valor ligado ao documento do ato que o fixou (e nunca ao "Edital completo", que pode não conter a versão vigente). Ausente, dependente da leitura e canais divergentes aparecem como tais; os pontos para revisão antes da abertura pública ficam por Edital. Sem modelo de linguagem, sem rota pública, sem gravação |
| [`071`](specs/071-piloto-assistente-do-edital/spec.md) | Fase B do assistente de dúvidas do Edital, o piloto interno — implementada; a avaliação no Ollama da L4, as medições e a sessão com o setor aguardam o acesso à L4: na gestão, para participantes com capacidade própria, a pergunta livre e de continuação sobre a fonte da `070`, com a versão conferida a cada pergunta; o serviço de inferência por configuração (OpenRouter para avaliação, Ollama na L4 para a execução local), sem troca automática nem retentativa; o contexto medido em tokens, sem corte silencioso; a resposta conferida pela aplicação contra as fontes entregues; e a avaliação em dois ambientes, com a fidelidade julgada por humanos |
| [`072`](specs/072-jornada-publica-do-portal/spec.md) | A jornada pública do portal — encontrar, começar, preparar e acompanhar (alternativa A da auditoria de UX de 12/10): a vitrine titula o cartão pelo Edital, diz a oferta por Perfil e o lugar, recolhe os filtros no celular com a busca à vista e resume resultado e prazo de recurso sem fazer um prazo valer para todos; a página da seleção resume a oferta com atalho para as vagas e anuncia o Requerimento pedido na inscrição; as telas de acesso nomeiam a vaga do destino, e a volta à vaga explica a confirmação, que continua sendo POST. Sem domínio novo, sem instrumentação; percurso com cinco pessoas e texto de finalidade de nome e CPF pendentes de validação humana |
| [`073`](specs/073-configurar-e-verificar-implantacao/spec.md) | Configurar, verificar e testar o correio e o Ollama na implantação — implementada, com validação operacional pendente, a partir da [auditoria de configurações](doc/auditoria-configuracoes-do-sistema-2026-10-14.md): uma seção única no guia de implantação, só com comandos que já existem, que separa ler a configuração, testar conexão e conta sem efeito, e a ação real; mais a recusa do backend SMTP sem servidor e a mensagem do serviço de inferência desconhecido. Sem comando novo; a sessão conduzida com a TI em homologação e o teste contra a L4 ficam pendentes; a página "Configuração e diagnóstico" fica para depois da autenticação da gestão |
| [`074`](specs/074-assistente-na-pagina-do-edital-local/spec.md) | O assistente do Edital na página pública da seleção, **só no desenvolvimento local**: com a chave `ASSISTENTE_NA_PAGINA_DO_EDITAL`, o visitante abre o painel do protótipo da Fase C e conversa sem a identidade da gestão — sugestões pela `070`, pergunta livre pela `perguntar` da `071`, conversa por sessão e Edital. Desligada por padrão, recusada por produção; autenticação, `073`, L4 e os requisitos da abertura ao público registrados como pendências da implantação |
| [`075`](specs/075-entrada-da-gestao/spec.md) | A entrada da gestão, no conceito A do [estudo de 16/10](doc/estudo-acesso-a-gestao-2026-10-16.md): a página de acesso em duas colunas no lugar da tela técnica de identificação, a escolha de identidades de demonstração em etapa própria — comissões e responsabilidades descritas, sem código de permissão, com busca acima de oito —, o retorno ao endereço pedido nas 90 portas, a sessão de demonstração que cai com o seletor desligado, e no portal "Minhas inscrições" e, só com método de entrada, "Área de gestão". O produto passa a se chamar *Gestão de Processos Seletivos (GPS)* |
| [`076`](specs/076-shell-da-gestao/spec.md) | O shell da gestão, etapa 2 do [estudo de 16/10](doc/estudo-acesso-a-gestao-2026-10-16.md): barra lateral em toda tela da gestão, com *Trabalho* (Processos Seletivos, Minhas Etapas, Visão Geral) e *Unidade* (Autoridades da unidade, Modelos de aviso), cada item só para quem o destino aceita, pelos mesmos predicados da lista; a pessoa e "Sair" no pé; cabeçalho de contexto com a seção e "Trocar identidade". Na tela larga a barra recolhe a uma faixa de ícones, com o nome como dica, e a escolha fica guardada no navegador; no celular ela vira um painel nativo, sem script; na Alocação por Etapa ela fica no topo, para a matriz caber a 1280 px. Nenhuma tela muda de conteúdo; o [inventário visual](doc/inventario-visual-da-gestao-2026-10-16.md) refeito não acusa regressão |
| [`077`](specs/077-telas-de-uso-diario/spec.md) | As telas de uso diário, primeiro incremento da etapa 4 do [estudo de 16/10](doc/estudo-acesso-a-gestao-2026-10-16.md): a lista de Processos fica só com "Novo Processo Seletivo", porque as outras três seções já estão na barra; os cinco estouros a 375 px do inventário são corrigidos, cada um na folha da própria tela, sem mudar o conteúdo; na lista, em Minhas Etapas e na Mesa, a trilha sai do conteúdo e vai para o cabeçalho de contexto, uma só por página. O [inventário](doc/inventario-visual-da-gestao-2026-10-16.md) refeito tem zero estouros, e só as nove telas tocadas mudam |
| [`078`](specs/078-telas-de-quem-elabora/spec.md) | As telas de quem elabora, segundo incremento da etapa 4 do [estudo de 16/10](doc/estudo-acesso-a-gestao-2026-10-16.md): as duas causas de estouro que a `077` corrigiu tela a tela — a moldura que rola sem posição e o grupo de campos que não encolhe — passam à folha comum, medido antes que a regra geral não move caixa em tela nenhuma; no detalhe do Processo, no do Edital e nas nove etapas da composição, a trilha vai para o cabeçalho de contexto e "O que fazer agora" vem antes do resto; os Editais do Processo viram a tabela da lista, com o estado vazio comum. O [inventário](doc/inventario-visual-da-gestao-2026-10-16.md) refeito tem zero estouros, e só as telas de quem elabora mudam de medida |
| [`079`](specs/079-telas-da-presidencia/spec.md) | As telas da presidência da comissão, terceiro incremento da etapa 4 do [estudo de 16/10](doc/estudo-acesso-a-gestao-2026-10-16.md): na Comissão, na conferência da inclusão, na Alocação por Etapa e na Distribuição, a trilha vai para o cabeçalho de contexto; na Distribuição, os lugares da Etapa — Impedimentos, Registrar ocorrência, Resultados, Trilha — sobem para logo abaixo do título, e nenhuma ação sai do lugar; a Comissão ganha título para os membros e, vazia, o estado vazio que leva à inclusão; o botão da Alocação passa a dizer "Salvar alocação". A barra da Alocação continua recolhida, e o [inventário](doc/inventario-visual-da-gestao-2026-10-16.md) refeito tem zero estouros, com só as telas da presidência mudando de medida |
| [`080`](specs/080-telas-filhas-da-distribuicao/spec.md) | As telas filhas da Distribuição e a auditoria da comissão, quarto incremento da etapa 4 do [estudo de 16/10](doc/estudo-acesso-a-gestao-2026-10-16.md), que fecha o fluxo da presidência: em Impedimentos, Registrar ocorrência, Resultados, Trilha da avaliação, Conclusões preservadas, na conferência da retirada e na Auditoria da comissão, a trilha vai para o cabeçalho de contexto — a das filhas é a da Distribuição com a tela no fim, e a Auditoria do Edital fica com a da `076`; o resultado do último envio sobe para logo abaixo do título em Registrar ocorrência e nas Conclusões; Impedimentos ganha título para o registro; e "Filtrar" tem o desenho de ação principal nas três consultas. Nenhuma ação que não se desfaz muda de peso, e o [inventário](doc/inventario-visual-da-gestao-2026-10-16.md) refeito tem zero estouros, com só as seis telas do escopo mudando de medida |
| [`081`](specs/081-achados-das-revisoes-077-079/spec.md) | Os achados que as revisões da `077` e da `079` registraram e não corrigiram, cada um com destino escrito: na Distribuição, "Consolidar as selecionadas" deixa de pesar o mesmo que "Distribuir as selecionadas" e, com "Consolidar as N prontas", ganha o desenho secundário e a marca "irreversível" dos atos do Processo, anunciada com o botão; na Alocação, o aviso diz "antes de alocar"; o cenário da presidência deixa de ser importado de um módulo de teste para outro, e um guardião confere a abertura da trilha em toda tela que a sobrescreve. Os outros sete achados ficam como decisão — três já corrigidos pela `078` e pela `080`, dois que contrariam requisito escrito e esperam o produto, dois que pedem ferramenta —, e o [inventário](doc/inventario-visual-da-gestao-2026-10-16.md) refeito tem zero estouros, com só a Distribuição mudando de medida |
| [`082`](specs/082-trilha-da-conferencia-da-consolidacao/spec.md) | A trilha da conferência da consolidação — a tela que "Consolidar as selecionadas" e "Consolidar as N prontas" abrem — no cabeçalho de contexto: a da Distribuição com "Conferir" no fim, como a conferência da retirada desde a `080`, que não a listou entre as filhas. Era a última tela aberta pela Distribuição com a trilha no conteúdo, e a dizia sem o Processo nem a Alocação. Só apresentação: o alcance declarado e o botão que consolida não mudam |
| [`083`](specs/083-telas-do-edital/spec.md) | As telas do Edital que a `078` não cobriu, quinto incremento da etapa 4 do [estudo de 16/10](doc/estudo-acesso-a-gestao-2026-10-16.md): em Novo Edital, Retificar, no detalhe da Retificação e na conferência de cada ato, na Prévia, em Partir de um Edital anterior e na conferência da troca, na Condução do marco e na conferência do gesto, na Prévia de publicação, nos Resultados divulgados e na Auditoria do Edital, a trilha vai para o cabeçalho de contexto, com o Processo entre a seção e o Edital — e o nível da classificação continua sem link para quem não a alcança; a recusa do último envio sobe para logo abaixo do título em Retificar e na Prévia de publicação; no detalhe da Retificação, "O que fazer agora" vem antes da Vigência; e "Filtrar", em Partir de um Edital anterior, tem o desenho das Inscrições. Nenhuma consulta a mais, nenhuma ação que não se desfaz muda de peso, e o [inventário](doc/inventario-visual-da-gestao-2026-10-16.md) refeito tem zero estouros, com só as telas do escopo mudando de medida |
| [`084`](specs/084-telas-de-resultado-e-atos/spec.md) | As telas de resultado e dos atos depois da inscrição, incremento da etapa 4 do [estudo de 16/10](doc/estudo-acesso-a-gestao-2026-10-16.md): na Classificação, na conferência da emissão, no Ato de classificação, no Sorteio, no Corte e no corte histórico, na Ocupação e na Convocação e nos históricos delas, e em Exportar para matrícula, a trilha vai para o cabeçalho de contexto — a do Edital, com os níveis que cada tela já tinha e a tela no fim. Nada mais muda: nenhum texto, e nenhum botão, que um guardião congela — são as telas dos atos que não se desfazem. O [inventário](doc/inventario-visual-da-gestao-2026-10-16.md) refeito tem zero estouros, com só as dez telas do escopo que ele abre mudando de altura |
| [`085`](specs/085-telas-de-inscricoes-e-recursos/spec.md) | As telas de inscrições e de recursos, sétimo incremento da etapa 4 do [estudo de 16/10](doc/estudo-acesso-a-gestao-2026-10-16.md): nas Inscrições, na Inscrição recebida, nos Recursos e no Recurso, a trilha vai para o cabeçalho de contexto — a do Edital com a tela no fim, agora passando pelo Processo, sem consulta a mais e sem dado pessoal além do protocolo; sem inscrição recebida, a lista mostra o estado vazio, e os rascunhos são região nomeada. A tela de recusa, que responde por toda a gestão, fica com o cabeçalho da `076`. Nenhuma ação muda de peso, e o [inventário](doc/inventario-visual-da-gestao-2026-10-16.md) refeito tem zero estouros, com só as cinco variantes do escopo mudando de medida |
| [`086`](specs/086-telas-dos-avisos-aos-candidatos/spec.md) | As telas dos avisos aos candidatos da `066`, grupo da etapa 4 do [estudo de 16/10](doc/estudo-acesso-a-gestao-2026-10-16.md): nos Avisos aos candidatos, no histórico de um aviso, na prévia, na conferência da interrupção, nos Modelos de aviso e na edição de um modelo, a trilha vai para o cabeçalho de contexto — as telas de um Edital passam pelo Processo, a prévia diz a porta por onde se chegou (resultado, chamada ou reenvio) e os modelos começam na seção da barra; os estados vazios, o rodapé dos formulários e a faixa de ações são os comuns. O aviso continua saindo pelo despacho, nenhuma ação que não se desfaz muda de peso, e o [inventário](doc/inventario-visual-da-gestao-2026-10-16.md) refeito tem zero estouros, com só as telas do escopo mudando de medida |
| [`087`](specs/087-paineis-e-telas-de-apoio/spec.md) | Os painéis e as telas de apoio da gestão, último grupo da etapa 4 do [estudo de 16/10](doc/estudo-acesso-a-gestao-2026-10-16.md): na Visão Geral e nas Autoridades da unidade (a seção, como página atual), na Supervisão, nas Respostas do assistente de dúvidas, no Assistente do Edital, em Criar Processo Seletivo e nas conferências dos atos do Processo e do Edital, a trilha vai para o cabeçalho de contexto — a das telas do Edital passa pelo Processo; e "Perguntar" tem o desenho de ação principal no Assistente. Nenhum número entra nos painéis, nenhuma ação que não se desfaz muda de peso, e o [inventário](doc/inventario-visual-da-gestao-2026-10-16.md) refeito tem zero estouros, com só as telas do escopo mudando de medida; a contagem das telas que ainda não têm a trilha no cabeçalho fecha a etapa |
| [`088`](specs/088-decisoes-da-etapa-4/spec.md) | As quatro decisões do usuário de 18/10/2026 sobre a etapa 4 da gestão: a trilha do cabeçalho de contexto passa a sair no papel, e a tela impressa volta a dizer de onde é; o landmark de trilha sem link da lista de Processos e de Minhas Etapas fica até haver autenticação; o rótulo do aviso na trilha ganha a hora, e dois avisos do mesmo dia deixam de ter o mesmo nome; e "Classificação", na trilha do Ato, leva ao recorte do ato, e não à ampla concorrência. Nenhuma regra de negócio, permissão ou ato muda |
| [`089`](specs/089-folha-estatica-da-gestao/spec.md) | A folha comum da gestão em arquivo estático, sem mudar regra nenhuma (passo 1 de 3): as regras do `<style>` do modelo comum vão, na mesma ordem, para `interface/static/interface/gestao.css`, e os tokens para `shared/static/shared/tokens.css`, carregados por `<link>` com a versão do conteúdo no endereço; cada resposta HTML da gestão perde ≈ 54 KB, e a folha passa a ficar no cache. Os 23 arquivos de teste que liam a folha foram repontados e provados por mutação; o [inventário](doc/inventario-visual-da-gestao-2026-10-16.md) refeito não muda medida, pixel fora do ruído nem regra aplicada em variante nenhuma |
| [`090`](specs/090-limpeza-dos-achados-da-etapa-4/spec.md) | A limpeza dos quatro achados menores da etapa 4 da gestão: a marca "irreversível" passa a ser anunciada pelo leitor de tela nos atos do Processo, do Edital e da Retificação; nas consultas da Etapa, a Alocação e a Etapa da trilha são texto para quem não pode abri-las; o rodapé dos formulários quebra a linha entre os botões a 375 px; e a prévia do aviso aberta pelos Resultados divulgados volta a eles. Nenhuma regra de negócio ou permissão muda |
| [`091`](specs/091-folha-por-area-e-csp/spec.md) | A folha da gestão por área, o estilo de cada tela em arquivo e a política de segurança de conteúdo (passos 2 e 3 da `089`): a folha comum em sete arquivos de `interface/gestao/`, sem trocar de ordem regra que disputa propriedade (prova em `doc/inventario-visual-da-gestao-2026-10-16/depois-da-091/`); os parciais e o estilo de 16 telas em `interface/grupos/` e `interface/telas/`, carregados só por quem os usa; os `style=""` da gestão em classe; e a CSP por middleware próprio, em recusa na gestão e na página de acesso, em observação no portal até a folha dele sair do documento. O [inventário](doc/inventario-visual-da-gestao-2026-10-16.md) refeito não muda medida, regra aplicada nem pixel fora do ruído, e nenhuma tela da gestão registra violação |
| [`092`](specs/092-folha-estatica-do-portal-e-csp/spec.md) | A folha do portal em arquivo e o portal sob a política de segurança de conteúdo (o passo que a `091` deixou registrado): o `<style>` de ≈ 66 KB do `portal/base.html` vai, na mesma ordem e provado igual byte a byte, para `portal/static/portal/portal.css`; o `style=""` da barra de documentos vira classe por percentual; os guardiões que liam a folha no modelo passam a ler o arquivo, provados por mutação; e a política vale em recusa em toda resposta HTML, sem modo de observação. Cada página do portal perde 66.724 bytes; o [inventário](doc/inventario-visual-da-gestao-2026-10-16/depois-da-092/) de 103 telas do portal, das bases e do papel não muda medida, regra aplicada nem pixel fora do ruído, e nenhuma tela registra violação |
| [`093`](specs/093-falha-de-csrf-na-moldura/spec.md) | A recusa da verificação anti-falsificação na moldura do sistema (o resíduo que a `091` e a `092` registraram): a página de falha de CSRF do Django, com estilo embutido e por isso sem desenho sob a política, dá lugar a `erros.falha_de_csrf`, que serve a recusa da gestão sob `/gestao/` e a do portal no resto, com 403, "Nada foi gravado" e o que fazer. O motivo técnico vai ao registro, e não à página; o link de reabrir só aponta para página do próprio sistema. A política e o que a verificação recusa não mudam |
| [`094`](specs/094-previa-da-classificacao/spec.md) | **Implementada; a validação com elaboradores está pendente.** A prévia interativa da classificação, fatia 1: o botão "Simular classificação" no cartão do marco por pontuação abre, fora do cartão, um painel com candidatos fictícios calculados pelo motor oficial. Ele abre na jornada do Perfil — as Etapas e os marcos na ordem, com o marco escolhido calculado e o resto como contexto ou indeterminado — e o detalhe, a um clique, diz por que cada um ficou na posição, se alcança o corte e se avança, com as duas recusas que o [achado de 19/10](https://github.com/vitofranzosi/processo_seletivo/pull/315) mostrou que ninguém prevê. Recalcula sobre o que está digitado, nos mesmos candidatos, e diz o que mudou. Não grava nada. A equivalência com o caminho oficial — ordem, ato, corte e apuração — é provada por teste com sentinela. O [roteiro de compreensão](specs/094-previa-da-classificacao/roteiro-de-compreensao.md) roda na interface real (entrada `interface-094` do `.claude/launch.json`) |
| [`095`](specs/095-previa-cotas-e-vagas/spec.md) | A prévia interativa da classificação, fatia 2, sobre a `094`: um recorte por Modalidade — a ampla como universo inteiro e cada reservada com a sua ordem e o seu corte —, a concorrência concomitante aplicada sempre, as quatro quantidades da ocupação de cada recorte numa rodada, sob hipóteses declaradas, e a reversão declarada, ou a frase de que não reverte. Sem efeito oficial. O [protótipo de cálculo](specs/095-previa-cotas-e-vagas/prototipo/reproducao.py) roda o motor oficial e mostrou o que nenhuma tela diz: o alvo fixo e os suplentes valem em todo recorte, a faixa da reservada conta quem ocupa pela ampla e deixa vaga sem ocupante com autodeclarado classificado, e a reversão por esgotamento conta essas pessoas como "quem ocupar" — as duas últimas registradas como decisões pendentes do usuário, e não corrigidas. Na implementação, a rodada de ocupação mora na `ocupacao` e chega à prévia injetada; a validação com elaboradores (SC-870) espera o relato do usuário |
| [`096`](specs/096-cadastro-de-reserva-como-cr/spec.md) | **Implementada.** O Perfil de cadastro de reserva sem vaga imediata continua guardando `0`, e o documento do Edital imprime `CR` no lugar do zero — na tabela de Perfis, na ficha do Perfil único e nas tabelas da apresentação por perguntas —, com a nota "CR: cadastro de reserva." abaixo de toda tabela que usa a sigla, como a equipe escreve à mão (o 76/2026). No portal, a oferta continua por extenso, e a linha "0 vagas imediatas agora" sai. Nenhuma decisão anterior tinha escolhido o `0` contra o `CR`: ele era resíduo da `027`, do "Total 0" de 30/09 e da `067`. A nota acordou um defeito latente da `069` — a última seção saltava com o fecho do ato só no publicado —, e a prévia passou a reservar o espaço real do fecho, medido pelas autoridades vigentes, para paginar o corpo normativo como o publicado (D-012, decisão do usuário). Documentos publicados não mudam |
| [`097`](specs/097-convocar-do-cadastro-de-reserva/spec.md) | **Implementada; a demonstração está em [verificacao.md](specs/097-convocar-do-cadastro-de-reserva/verificacao.md).** A volta da opção A da `DP-05`, com o primeiro caso real: o Edital de vagas remanescentes do TMD, por sorteio e só de cadastro de reserva, cujas vagas surgem depois da publicação, conforme as matrículas do Edital regular não se efetivam. A vaga liberada lá entra aqui como fato operacional append-only, com origem, fundamento e autor, e não como Retificação — pela ocupação, com conferência que diz quem a ordem alcança pelo nome; a apuração a soma, o próprio ato emite a apuração seguinte, e a convocação que já existe chama o próximo da ordem. O acréscimo errado se desfaz por ato contrário, e a Revisão deixa de dizer que a convocação é feita fora do sistema. O prazo final das chamadas fica com a equipe, sem trava no sistema. Só a ampla concorrência: a ordem entre modalidades, o limite da reserva e os Editais de bolsista ficam fora |
| [`098`](specs/098-previa-do-sorteio/spec.md) | **Implementada; a validação com elaboradores espera o relato do usuário.** A prévia do marco por sorteio, que a `094` deixava de fora: uma semente fictícia — gerada na interface, porque o app do sorteio não pode ter gerador —, o algoritmo oficial sobre uma relação fictícia de cada recorte, o corte e a rodada de ocupação da `095`, e o resumo de 1.000 rodadas. A equivalência com o caminho oficial injeta o resumo da relação publicada e compara ordem, faixa, ocupação e reversão. O [protótipo](specs/098-previa-do-sorteio/prototipo/medicao.py) mediu que, no sorteio, sobrar vaga de cota sem ocupante é a regra (72% das rodadas na população da história), e a equivalência achou que a lista reservada vazia não é sorteada nem apurada, e por isso não reverte nem "por saldo" — [registrado](doc/achado-reservada-vazia-nao-reverte.md), não decidido. Na tela: o botão "Simular sorteio" no cartão, a semente com selo de fictícia, "Sortear de novo", a população por lista, a ordem de cada lista com a posição na ampla, a ocupação da `095` e o resumo das rodadas |
| [`099`](specs/099-relatorio-do-edital/spec.md) | **Implementada; a conversa com destinatários (SC-932) espera o usuário.** O relatório do Edital para quem não opera a seleção: página de gestão e PDF com a camada executiva — duas situações (a do Edital no GPS e a das providências), visão geral escrita por regras, seis indicadores e pontos de atenção — e o anexo técnico. A espécie é derivada (acompanhamento, encerramento ou interrupção), e a de encerramento não afirma o que o GPS não acompanha, como a matrícula. Fato não público só por Perfil; cada emissão registrada na auditoria com o resumo do arquivo. Desde 24/10 o PDF segue a maquete v2 pelo compositor de blocos da `100` — cartões, procura em barras por dia, paginação por grupos —, e só leva endereço quando emitido de host público. Estudo e maquetes em [`doc/`](doc/estudo-relatorio-de-execucao-do-edital-2026-10-24.md) |
| [`100`](specs/100-relatorio-consolidado/spec.md) | **Implementada; produção não autorizada, e a conversa com destinatários (SC-945) espera o piloto.** O relatório consolidado da unidade: a partir da Visão Geral, um conjunto de Editais escolhido pela primeira publicação (ano ou semestre), pelo ano do número ou à mão, com a camada executiva — oferta, procura, resultados e providências — e o anexo técnico, em página e PDF com emissão auditada. Os números são a soma dos fatos de cada relatório do Edital (`099`), separados da redação; cancelados ficam fora de todo número. Corrige na `099` a supressão por diferença entre totais e a pendência de Perfil sem inscrição. Estudo e maquete em [`doc/`](doc/estudo-relatorio-consolidado-de-gestao-2026-10-24.md) |
| [`101`](specs/101-agenda-dos-editais/spec.md) | **Implementada; a sessão observada com quem gere (SC-948) espera o usuário.** A Agenda dos Editais, em `/gestao/agenda`, para toda identidade da gestão: os cronogramas publicados e vigentes de todos os Editais da unidade, numa grade do mês — contagem por dia, destaque para dia com mais de um marco, períodos listados como intervalos — e numa lista dos próximos 7 ou 30 dias. Só leitura, projeção da versão vigente, sem cadastro nem sincronização; datas sempre ditas previstas. Estudo em [`doc/`](doc/estudo-calendario-institucional-2026-10-29.md) |
| [`102`](specs/102-sorteio-viavel-desde-a-publicacao/spec.md) | **Implementada; o roteiro com quem conduz o certame (SC-958) espera o usuário.** A publicação é impedida quando o método tem extração inviável: com fonte que publica só a data, como a Loteria Federal, uma extração no dia do fim das inscrições (ou antes) nunca sorteia. A granularidade passa a ser declarada por fonte, e só a fonte que publica só a data é conferida. A Retificação só adverte, a tela do sorteio avisa antes de congelar uma relação condenada (o botão continua disponível), uma segunda fonte de demonstração reproduz o caso sem rede e a recusa por precedência passa a dizer a saída: retificar o método e suceder a relação, nessa ordem. Achado em [`doc/`](doc/achado-sorteio-com-extracao-no-dia-do-congelamento.md) |
| [`103`](specs/103-jornada-da-retificacao/spec.md) | **Implementada; a jornada com três pessoas reais (SC-978) espera o usuário.** A jornada operacional da Retificação pela navegação comum, a partir da auditoria de 29/10 (AUD-RET-01 a 04): a Retificação em curso aparece no detalhe do Edital ("Retificações em curso") e como marca na linha do Edital na Lista, com a situação e quem age a seguir; o detalhe diz quem age a seguir, quem já atuou e o motivo da devolução, e mostra desabilitado, com o motivo, o "Publicar" que a segregação recusaria; a devolvida volta a ser editada no mesmo registro pela tela, com a revisão conferida e a edição na trilha. Nenhuma permissão, estado ou fila nova. Auditoria em [`doc/`](doc/auditoria-retificacao-passagem-e-sorteio-2026-10-29.md) |
| [`104`](specs/104-acoes-disponiveis/spec.md) | **Implementada sobre a `103`; o roteiro com três pessoas (SC-990) espera o usuário.** A Lista de Processos Seletivos passa a abrir com "Ações disponíveis para você": um item por objeto em que a pessoa pode atuar agora — Edital, Retificação, recursos e avaliação de comissão —, derivado das mesmas regras dos detalhes, sem fila nem estado novo. A coluna "O que posso fazer" deixa de negar ação ao lado da Retificação, troca "Submeter" e "Publicar" do Edital por "Conferir e…" (a pendência só a validação revela) e mostra a segregação; o detalhe do Edital nomeia a Retificação que espera a pessoa; devolvida e reenviada se reconhecem; a confirmação de homologar mostra o que muda e recolhe os avisos que já valiam; Minhas Etapas diz o que cobre. A Lista passou de duas consultas por Edital publicado a um número constante. Diagnóstico em <https://claude.ai/artifact/GqXFAReaxgwMuZLApgUf3z> |
| [`105`](specs/105-documentacao-na-gestao/spec.md) | **Implementada.** A Visão do Sistema dentro da gestão, pedida na PR #329: o grupo "Ajuda" da barra leva toda identidade a `/gestao/documentacao/`, que serve o manual de `docs/visao-sistema/` sob a política de conteúdo, por lista literal de arquivos — o resto é 404 —, e o manual ganha no pé da barra dele o "Voltar" à gestão. A suíte passa a cobrar do manual que todo arquivo que ele pede esteja na lista e que nada nele seja embutido. |
| [`106`](specs/106-identidade-institucional-preparada/spec.md) | **Implementada; o SSO real não foi integrado, e três propostas de governança esperam o usuário.** A gestão fica pronta para a autenticação institucional sem tocar no seletor de demonstração, que continua igual em desenvolvimento e homologação. O Django Auth guarda a pessoa, com um identificador interno `pessoa-<uuid>` que o banco não deixa mudar; o GPS autoriza por vínculos pessoa × unidade × papel append-only, e o `Actor` é recalculado a cada requisição a partir da unidade ativa — revogação vale na seguinte, e a presidência de comissão não alcança quem perdeu o acesso. Um adaptador de contrato fixo entrega a identidade; nos testes, um provedor simulado sem rede. Produção recusa o seletor também em execução, recusa provedor de teste e, sem provedor, mantém a gestão em 503. Diagnóstico e ADR em `doc/`. |
| [`107`](specs/107-gestao-de-acessos/spec.md) | **Implementada em dois incrementos, sobre a `106` (PR empilhado); o segundo — suspensão, reativação, retirada e substituição do administrador institucional, e o nome nas demais telas — segue as decisões do usuário de 30/10.** A gestão de acessos ganha tela: quem entra pelo provedor sem acesso vê o próprio nome e a quem pedir; a barra mostra o nome, e não o identificador, e troca a unidade ativa; "Acessos da unidade" e "Administração de acessos" consultam, concedem e revogam com busca de pessoas, confirmação, motivo e histórico; a sessão institucional ganha duração máxima e inatividade, com valores que produção exige declarados. As jornadas se provam num navegador de verdade, com o servidor, as identidades e a página do provedor preparados pelos testes (`make test-navegador`). O seletor de demonstração não muda, e não alcança as telas de acesso. |
| [`108`](specs/108-trilha-da-unidade/spec.md) | **Implementada; três decisões de governança esperam o usuário (quem audita o nível institucional, as sessões na trilha, o Gestor lendo a trilha).** A trilha da unidade: os atos administrativos que só se liam pelo `psql` — o registro e a alteração da unidade, as autoridades, os modelos de aviso, os avisos confirmados e interrompidos e os acessos concedidos e revogados — ganham uma página só de leitura, paginada e filtrável por assunto, para quem tem `auditoria:consultar` na unidade ativa. Quem praticou aparece pelo nome, e a sincronização como "Implantação"; nada de candidato, nem o texto do aviso ou do modelo. O Auditor do seletor a alcança pela barra. Nada se grava e nenhuma migration entra. |

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
