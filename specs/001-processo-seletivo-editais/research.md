# Research: Processo Seletivo e Editais

## 1. Plataforma de execução

**Decision**: Python 3.13 com Django 5.2 LTS, Django REST Framework e psycopg 3, implantado como
serviço Linux conteinerizado.

**Rationale**: Django 5.2 é uma versão LTS, suporta Python 3.10 a 3.14 e reúne ORM, migrations,
segurança, validação e ferramentas de teste numa base coesa. Python 3.13 está em manutenção ativa e
oferece uma escolha conservadora de ecossistema para o início da implementação. Não existe stack
anterior no repositório a preservar.

**Alternatives considered**:

- Python 3.14: suportado pelo Django 5.2 nas versões de manutenção recentes, mas 3.13 reduz o risco
  inicial de incompatibilidade com dependências periféricas.
- FastAPI: oferece uma camada HTTP enxuta, porém exigiria compor separadamente ORM, migrations,
  administração e convenções de segurança que o Django já integra.

**Sources**: [Django 5.2 release notes](https://docs.djangoproject.com/en/dev/releases/5.2/),
[Django installation FAQ](https://docs.djangoproject.com/en/dev/faq/install/) e
[Python 3.13 documentation](https://docs.python.org/3.13/).

## 2. Forma arquitetural

**Decision**: monólito modular, organizado em apps Django por capacidade de negócio e arquitetura
hexagonal leve dentro de cada app; uma implantação e um banco transacional. Regras de workflow
ficam em domínio/casos de uso, não concentradas em models, serializers, signals ou views.

**Rationale**: Publicação, snapshot, documento e auditoria exigem consistência forte. Uma única
fronteira transacional atende isso com menor risco operacional. Módulos explícitos preservam a
linguagem e evitam um agregado gigante sem introduzir chamadas distribuídas.

**Alternatives considered**:

- Microsserviços: rejeitados porque não há escala ou autonomia de equipes que compense transações
  distribuídas e maior operação.
- Event sourcing/CQRS: rejeitados porque snapshots imutáveis e atos preservados já permitem
  reconstrução jurídica com complexidade menor.
- CRUD em camadas globais: rejeitado porque dilui máquinas de estado e operações administrativas.

## 3. Persistência relacional

**Decision**: PostgreSQL 18, dados editáveis normalizados, migrations Django append-only, constraints
de integridade e snapshots normativos canônicos em JSON estruturado imutável.

**Rationale**: PostgreSQL oferece transações, locks, constraints, JSON e consultas temporais em um
único componente. A versão 18 é suportada até 2030. Estruturas editáveis precisam de integridade
relacional; snapshots completos reduzem custo e ambiguidade das consultas históricas.

**Alternatives considered**:

- Banco documental: rejeitado porque cardinalidades e invariantes persistentes são centrais.
- PostgreSQL 17: fallback suportado quando a infraestrutura ainda não homologar 18.
- Temporalizar todas as tabelas: possível, porém aumenta significativamente joins e risco de
  reconstrução; o snapshot canônico é mais verificável.

**Source**: [PostgreSQL versioning policy](https://www.postgresql.org/support/versioning/).

## 4. Representação de Publicações e Retificações

**Decision**: cada Publicação preserva separadamente o ato, as alterações estruturadas da
Retificação, o snapshot consolidado, o PDF original e seus hashes. Registros publicados são
append-only.

**Rationale**: o delta explica o que o ato alterou; o snapshot completo responde de forma direta
qual conteúdo vigorava; os bytes do PDF provam exatamente o documento divulgado. Uma nova
Publicação nunca atualiza uma anterior.

O hash usa uma representação canônica versionada, com regras explícitas para ordenação, Unicode,
decimais e datas. JSONB é armazenamento consultável, não a fonte dos bytes canônicos.

**Alternatives considered**:

- Somente deltas: exige replay permanente e torna evolução de schema e consulta mais frágeis.
- Somente snapshots: reproduz o conteúdo, mas não explica de forma precisa o efeito de cada ato.
- Regenerar PDFs históricos: rejeitado porque versões de renderizador podem mudar os bytes.

## 5. Consolidação temporal cumulativa

**Decision**: uma Retificação publicada registra `publishedAt`, `effectiveAt`,
`publicationSequence` monotônica por Edital e alterações por caminho normativo estável. Para o
instante T, são elegíveis atos com `publishedAt <= T` e `effectiveAt <= T`; eles são compostos por
`effectiveAt` e, no mesmo instante de vigência, por `publicationSequence`. Alterações em caminhos
distintos acumulam; no mesmo caminho, a maior `publicationSequence` prevalece no empate de vigência.

**Rationale**: implementa FR-039 sem depender de ID, ordem física ou timestamp de criação. A
sequência é atribuída sob lock no momento da Publicação e representa inequivocamente “publicada por
último”, mesmo quando timestamps têm a mesma precisão. Cada mudança de conjunto aplicável produz
snapshot consolidado imutável e hash.

**Alternatives considered**:

- Ordenar somente por Publicação: contradiz FR-039.
- Proibir vigências fora da ordem: contradiz a clarificação.
- Aplicar JSON Patch opaco: não permite detectar conflitos sem semântica de caminhos.
- Recompor sempre em leitura: determinístico, porém menos robusto e mais caro; será usado como
  verificador independente, não como caminho normal de consulta.

## 6. Concorrência e idempotência

**Decision**: optimistic locking em agregados mutáveis e precondição `If-Match`; locks de linha
curtos e revalidação transacional em homologar, publicar, encerrar e cancelar; sequência única por
Edital e chave de idempotência para commands irreversíveis.

**Rationale**: edição comum não deve bloquear usuários, mas Publicação e verificação “todos os
Editais estão finais” não podem sofrer TOCTOU. Constraints únicas impedem dupla Publicação mesmo
após retry. Conflitos retornam `409` ou `412`, nunca last-write-wins.

**Alternatives considered**:

- Somente lock otimista: insuficiente para atribuir sequência e validar conjuntos concorrentes.
- Lock pessimista em toda edição: aumenta contenção sem benefício.
- Lock distribuído: desnecessário enquanto PostgreSQL é a autoridade transacional.

**Django mapping**: casos de uso críticos abrem `transaction.atomic()`, adquirem
`select_for_update()` nas raízes e contadores envolvidos e revalidam as precondições após o lock.
Uma coluna `version` e atualização condicional implementam o controle otimista, pois o Django ORM
não o fornece automaticamente. Violações de unicidade continuam sendo a última linha de defesa.
Para decisões entre agregados, a ordem é Processo e depois Editais por ID; transições relevantes de
Edital também bloqueiam o Processo pai. Isso impede que cancelamento e mudança de estado observem
conjuntos diferentes. Efeitos externos futuros só são disparados com `transaction.on_commit()`.

## 7. Documento publicado

**Decision**: na primeira entrega, guardar o PDF como bytes imutáveis no PostgreSQL junto aos
metadados e SHA-256, atrás de uma porta de armazenamento.

**Rationale**: é a opção mais simples para atomicidade entre ato, snapshot, auditoria e documento.
O volume inicial é desconhecido, mas documentos são poucos em relação às consultas. A porta permite
migração posterior sem contaminar o domínio.

**Alternatives considered**:

- Object storage: adequado para grande volume, mas exige staging/compensação porque não participa
  da transação do banco; reconsiderar após confirmação da infraestrutura institucional.
- Filesystem local: rejeitado por disponibilidade, backup e múltiplas instâncias.

## 8. Autorização e segregação

**Decision**: permissões por operação, combinadas com escopo institucional, recurso, estado e
autores anteriores. Segurança HTTP é primeira barreira; o caso de uso revalida autorização e o
domínio protege invariantes. Elaborador não pode ser simultaneamente o único homologador e
publicador.

**Rationale**: uma role fixa não expressa IDOR, estado ou segregação. Registrar `preparedBy`,
`homologatedBy` e `publishedBy` torna a regra verificável e auditável sem acoplar cargos.

**Alternatives considered**:

- Roles por endpoint: simples, mas insuficientes para autorização contextual.
- ACL completa por registro: prematura sem requisito de delegação individual.

## 9. Auditoria

**Decision**: Registro de Auditoria append-only na mesma transação do command, com ator, permissão,
agregado, instante, estado/revisão anterior e posterior, motivo, correlação e referência ao ato.
Credencial da aplicação não recebe UPDATE/DELETE nessa estrutura.

**Rationale**: logs operacionais não possuem semântica administrativa nem atomicidade. Referenciar
snapshots por ID/hash evita duplicar dados sensíveis.

**Alternatives considered**:

- Logs da aplicação: rejeitados como fonte de auditoria.
- Auditoria automática do ORM: pode complementar diagnóstico, mas não substitui motivo, ato e
  correlação de negócio.

## 10. Contratos HTTP

**Decision**: REST/JSON versionado em `/api/v1`, commands de workflow como sub-recursos, OpenAPI
3.1, `application/problem+json`, ETag/If-Match, Idempotency-Key e superfícies administrativa e
pública separadas.

**Rationale**: ativar, homologar, publicar, encerrar e cancelar possuem semântica própria e não são
atualizações genéricas de status. DTOs independentes impedem que persistência vire contrato.

**Alternatives considered**:

- `PATCH status`: rejeitado por ocultar invariantes e autorização da operação.
- GraphQL: sem necessidade demonstrada e menos direto para commands administrativos e caching de
  documentos públicos.

## 11. Testes

**Decision**: pytest e pytest-django para domínio, aplicação e segurança; Django Test Client e APIClient
do DRF para HTTP; PostgreSQL real para persistência/concorrência; testes de contrato OpenAPI e
aceitação rastreada aos 29 cenários.

**Rationale**: bancos em memória não reproduzem locks, JSON e constraints do PostgreSQL. Suítes
separadas mantêm feedback rápido sem abandonar integração real.

**Alternatives considered**:

- E2E apenas: diagnóstico lento e cobertura insuficiente de invariantes.
- Mocks extensivos de persistência: não verificam as garantias constitucionais do banco.
- SQLite nos testes de integração: rejeitado porque não reproduz locks, tipos, JSON e constraints
  do PostgreSQL. Testes concorrentes usam transações reais e conexões independentes.

Migrations são testadas tanto desde banco vazio quanto como upgrade da versão anterior. A CI roda
`makemigrations --check --dry-run`; testes de locks, commits e `on_commit` usam suíte transacional,
pois o `TestCase` comum pode mascarar esse comportamento.

## 12. Operação e recuperação

**Decision**: logs estruturados correlacionados à auditoria, métricas de latência/conflitos/falhas,
health/readiness, backup com recuperação pontual e testes periódicos de restauração e hashes.
RPO, RTO e disponibilidade devem ser aprovados institucionalmente antes de produção.

**Rationale**: o plano deve permitir diagnóstico e recuperação, mas números sem acordo de serviço
seriam artificiais. A ausência desses números não impede o desenho da feature.

**Alternatives considered**:

- Alta disponibilidade multi-região desde a primeira entrega: rejeitada por falta de requisito.
- Dump eventual sem teste: incompatível com preservação histórica.
