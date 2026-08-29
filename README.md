# Processo Seletivo e Editais — Cefor/IFES

Serviço backend para gestão de Processos Seletivos e seus Editais: elaboração, homologação,
Publicação imutável, Retificações com vigência temporal e consulta pública histórica.

O projeto é conduzido por especificação, com [GitHub Spec Kit](https://github.com/github/spec-kit).
A [Constituição](.specify/memory/constitution.md) é a autoridade de engenharia e domínio; em
conflito, ela prevalece.

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

- Python 3.13
- [uv](https://docs.astral.sh/uv/)
- PostgreSQL 16 ou superior (a CI valida contra 18)

## Como rodar

```bash
cd backend && make install
```

Copie `backend/.env.example` para `backend/.env` e ajuste as credenciais. O projeto separa a role de
migração da role de runtime: a de runtime não recebe `UPDATE` nem `DELETE` sobre os registros
append-only, garantia verificada em `tests/integration/test_database_permissions.py`.

```bash
cd backend && DJANGO_SETTINGS_MODULE=config.settings.development uv run python manage.py migrate
```

```bash
cd backend && DJANGO_SETTINGS_MODULE=config.settings.development uv run python manage.py runserver
```

### Ver o sistema no ar

Não há interface gráfica — ela está fora do escopo deste incremento. O sistema é uma API, e a
consulta pública é anônima, então basta abrir as URLs no navegador. Para ter o que olhar, popule
uma demonstração que percorre o fluxo normativo real, com atores distintos em cada etapa:

```bash
cd backend && DJANGO_SETTINGS_MODULE=config.settings.development uv run python manage.py seed_demo
```

O comando imprime os identificadores criados e as URLs prontas: versão vigente, histórico e
Retificação. Ele cria um Edital publicado com dois Perfis e três Eventos, mais duas Retificações —
uma já vigente e outra com vigência futura —, para que a consulta temporal tenha o que mostrar.

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
cd backend && make lint check test
```

A suíte roda em SQLite por padrão e ignora os testes que exigem garantias reais do banco. Para
executar tudo, aponte para um PostgreSQL de teste:

```bash
cd backend && TEST_DB_ENGINE=postgresql DB_NAME=processo_seletivo_test DB_USER=postgres DB_PASSWORD=postgres DB_HOST=localhost DB_PORT=5432 uv run pytest
```

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
acima. A interface administrativa e pública é uma especificação futura, não parte deste incremento.

## Documentação

| Artefato | Conteúdo |
|---|---|
| [`spec.md`](specs/001-processo-seletivo-editais/spec.md) | Requisitos, cenários e critérios de sucesso |
| [`plan.md`](specs/001-processo-seletivo-editais/plan.md) | Decisões técnicas e verificação constitucional |
| [`data-model.md`](specs/001-processo-seletivo-editais/data-model.md) | Entidades, invariantes e regras |
| [`tasks.md`](specs/001-processo-seletivo-editais/tasks.md) | Tarefas por história |
| [`quickstart.md`](specs/001-processo-seletivo-editais/quickstart.md) | Guia de validação |
