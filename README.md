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
| `identidade` | Identidade do candidato e acesso sem senha, por código enviado ao e-mail |
| `inscricoes` | Inscrição, documentos submetidos e fatos declarados pelo candidato |
| `comissoes` | Comissão do Processo e alocação dos membros às Etapas |
| `avaliacoes` | Atribuição, avaliação e impedimento |
| `resultados` | Resultado da Etapa |
| `classificacao` | Ordem classificatória e corte entre Etapas |
| `sorteios` | Relação de habilitados congelada, ocorrência da fonte externa e o sorteio auditável |
| `ocupacao` | Apuração da ocupação e movimento de vagas entre listas de concorrência |
| `divulgacao` | Publicação de resultado, situação individual divulgada e o documento dela |
| `recursos` | Recurso, juízo de admissibilidade, instrução e decisão |
| `convocacao` | Convocação, chamada, suplência e desfecho |
| `requerimentos` | Requerimento de Matrícula e base local de referência de CEP |
| `matriculas` | Exportação para o Registro Acadêmico — registra a geração, e não guarda o arquivo |
| `unidades` | Unidades institucionais e autoridades habilitadas: o que o documento diz da unidade e quem pode responder pelos atos dela |
| `interface` | Interface administrativa, em `/gestao/` |
| `portal` | Consulta pública e área do candidato, em `/selecoes/` |
| `seguranca` | Ator autenticado, permissões, autorização por objeto e papéis do banco |
| `auditoria` | Registro append-only e idempotência |
| `shared` | Serialização canônica, concorrência otimista, Problem Details e observabilidade |
| `interface` | Interface administrativa da gestão: composição, Retificação e condução do Processo |
| `portal` | Portal do candidato: vitrine, inscrição, acompanhamento e recurso |
| `identidade` | Identidade do candidato, acesso por código e reconciliação com a participação anterior |
| `inscricoes` | Inscrição, documentos enviados e período de inscrições |
| `comissoes` | Comissão, alocação por Etapa e impedimentos |
| `avaliacoes` | Distribuição, Mesa de avaliação e conclusão |
| `resultados` | Resultado da Etapa: consolidação, Ocorrência e progressão entre Etapas |
| `classificacao` | Corte, ordenação e o ato de classificação |
| `ocupacao` | Ocupação de vagas entre as listas de concorrência |
| `divulgacao` | Publicação de resultados e a porta da definitividade |
| `recursos` | Recurso, instrução, admissibilidade e julgamento |
| `convocacao` | Convocação, chamada e suplência |
| `requerimentos` | Requerimento de Matrícula |
| `matriculas` | Exportação de matrículas para o Registro Acadêmico |

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
- backend de e-mail que não entrega (console, arquivo, memória ou nulo) ou remetente vazio — sem
  entrega, o código de acesso iria para o log do servidor;
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
sem `DB_USER` ela tenta conectar como a role de runtime, que não pode criar banco de teste:

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
a avaliação, a classificação, a publicação de resultados, os recursos, o sorteio, a convocação, o
Requerimento de Matrícula e a condução do Processo publicado são incrementos próprios, listados
abaixo. O estado de cada um está na pasta do incremento, e não aqui — este parágrafo descreve a
`001`. Auditorias, achados e decisões que atravessam incrementos ficam em [`doc/`](doc/).

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
