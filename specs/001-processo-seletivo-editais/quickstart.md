# Quickstart Validation Guide: Processo Seletivo e Editais

Este guia descreve como validar futuramente a implementação contra [spec.md](./spec.md),
[data-model.md](./data-model.md) e [OpenAPI](./contracts/openapi.yaml). Ele não pressupõe que o
serviço já exista e não contém implementação.

## Prerequisites after implementation

- Python 3.13, Django 5.2 LTS e dependências declaradas em `pyproject.toml`;
- Docker/Podman ou serviço dedicado para PostgreSQL 18 de teste;
- tokens de teste para elaborador A, homologador B, publicador C, gestor e consulente de auditoria;
- relógio controlável nos testes para fronteiras de Publicação/vigência;
- ferramenta HTTP que preserve headers `ETag`, `If-Match` e `Idempotency-Key`.

## Planned verification commands

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python manage.py check
python manage.py makemigrations --check --dry-run
python -m pytest
python -m pytest -m acceptance
python -m pytest -m contract
```

Os testes de contrato devem validar `contracts/openapi.yaml` como OpenAPI 3.1 e comparar status,
headers e corpos observados na API com o contrato. Os testes de concorrência devem usar PostgreSQL,
transações e conexões independentes; SQLite e o isolamento automático de `TestCase` não substituem
essa suíte.

As suítes devem iniciar PostgreSQL real de teste, aplicar todas as migrations do zero e falhar se o
contrato OpenAPI divergir do comportamento. Perfis de carga/recuperação serão executados
separadamente quando os SLOs institucionais forem aprovados.

## Common acceptance setup

1. Definir `BASE_URL` para `/api/v1`.
2. Usar correlação única por cenário e Idempotency-Key nova por command irreversível.
3. Capturar IDs e ETags retornados; não reutilizar ETag após alteração bem-sucedida.
4. Fixar os instantes do cenário em UTC e converter datas institucionais usando
   `America/Sao_Paulo`.
5. Ao final, verificar o Registro de Auditoria pelo ator autorizado e os hashes dos documentos.

## Scenario 1 — Create Processo and first Edital atomically

- Executar `POST /admin/processos` com identificação institucional e primeiro Edital.
- Esperar `201`, IDs distintos, vínculo correto, ambos em elaboração e ETag.
- Repetir com dado inválido e confirmar `422` sem Processo parcial.
- Rastreia US1 e FR-001–FR-004.

## Scenario 2 — Add independent second Edital

- Criar outro Edital em `POST /admin/processos/{processoId}/editais`.
- Configurar Cronogramas diferentes e alterar somente o segundo.
- Confirmar que estado, revisão e Cronograma do primeiro não mudaram.
- Rastreia US1/US3, FR-002 e FR-015–FR-018.

## Scenario 3 — Elaborate profiles, vacancies and schedule

- Atualizar `/admin/editais/{editalId}/rascunho` com If-Match.
- Incluir múltiplos Perfis, vagas imediatas, Cadastro Reserva limitado/ilimitado, modalidades e
  Eventos pontuais/períodos.
- Confirmar rejeição de limite incompatível, período invertido e Evento de outro Edital.
- Rastreia US2/US3 e FR-009–FR-018.

## Scenario 4 — Submit and homologate

- Ator A submete o Edital; ator B homologa a mesma revisão/hash.
- Alterar o draft depois da revisão e confirmar que a Publicação da homologação antiga é rejeitada.
- Revogar homologação antes da Publicação e confirmar retorno permitido para revisão.
- Rastreia FR-006, FR-019–FR-021 e FR-036.

## Scenario 5 — Publish original Edital

- Com revisão homologada, executar command `publicacoes` com If-Match e Idempotency-Key.
- Esperar Publicação com `publicationOrder`, `publishedAt`, `effectiveAt`, hashes e documento.
- Verificar snapshot = revisão homologada e PDF = bytes preservados; edição direta deve falhar.
- Rastreia US4 e FR-019–FR-024.

## Scenario 6 — Immediate Retificação

- Criar Retificação com alteração semântica e sem `effectiveAt` futuro; submeter, homologar e
  publicar.
- Confirmar `effectiveAt = publishedAt`, snapshot consolidado novo e preservação do original.
- Rastreia US5, FR-025–FR-030 e FR-039.

## Scenario 7 — Future Retificação

- Publicar Retificação com `effectiveAt = T2`, onde T2 > Publicação.
- Consultar em T1 entre Publicação e T2: conteúdo anterior continua vigente.
- Consultar exatamente em T2: novo conteúdo passa a compor a versão.
- Tentar `effectiveAt < publishedAt` e esperar `422`.

## Scenario 8 — Publications outside effective order

- Publicar A em 01/09 com vigência 10/09; publicar B em 05/09 com vigência 08/09.
- Em 07/09, esperar versão anterior; em 08/09, esperar B; em 10/09, esperar composição A+B,
  preservando alterações vigentes não substituídas.
- Confirmar proveniência de cada caminho e hash determinístico.

## Scenario 9 — Same effective time without conflict

- Publicar duas Retificações com o mesmo `effectiveAt`, alterando caminhos independentes.
- Na fronteira, esperar ambas as alterações no mesmo snapshot consolidado.
- Reordenar fisicamente os dados de entrada no teste e confirmar conteúdo/hash iguais.

## Scenario 10 — Same effective time with conflict

- Publicar duas Retificações com o mesmo `effectiveAt` que alterem o mesmo caminho canônico.
- Confirmar que a maior `publicationOrder` vence somente nesse conteúdo e alterações independentes
  continuam acumuladas.
- Executar com timestamps de Publicação artificialmente iguais para provar que ID/ordem física não
  participam do resultado.

## Scenario 11 — Historical reconstruction

- Consultar antes do Edital original, entre atos, em cada fronteira e após até 20 Retificações.
- Esperar ausência clara antes da primeira Publicação e snapshot/proveniência corretos nos demais.
- Recomputar a função temporal e comparar seu hash ao snapshot materializado.
- Confirmar que original, atos, consolidados e PDFs permanecem públicos e imutáveis.

## Scenario 12 — Regular Edital closure

- Com etapas concluídas, executar command `encerramentos` no Edital Publicado.
- Esperar `ENCERRADO`, ato/auditoria e histórico preservado.
- Confirmar que a resposta não apresenta cancelamento e que transição posterior inválida falha.
- Rastreia US7, FR-006 e FR-035.

## Scenario 13 — Invalid Processo cancellation

- Manter ao menos um Edital não final e solicitar cancelamento do Processo.
- Esperar `409/422` com código de domínio e lista autorizada de impedimentos, sem transição parcial.
- Encerrar ou cancelar explicitamente cada Edital, repetir e confirmar o ato do Processo.
- Rastreia FR-005, FR-034 e FR-035.

## Scenario 14 — Segregation of duties and authorization

- Ator A elabora, homologa e tenta publicar sozinho: operação deve ser negada.
- Ator A elabora e submete; B homologa; A ou C publica: operação pode prosseguir se todas as demais
  permissões e invariantes forem satisfeitas.
- Manipular ID fora do escopo e confirmar negação sem revelar o recurso.
- Verificar participantes na Publicação e auditoria, sem acoplamento a cargos.

## Scenario 15 — Concurrency and retries

- Duas edições usam a mesma ETag: uma vence, a segunda recebe `412`.
- Duas Publicações da mesma homologação concorrem: existe somente uma Publicação.
- Retry com mesma Idempotency-Key/payload retorna o resultado original; payload diferente retorna
  `409`.
- Publicação e materialização no mesmo `effectiveAt` recebem lock comum e produzem um snapshot.
- Cancelamento do Processo concorrente com transição de Edital preserva a invariante de estados
  finais ou falha integralmente.

## Cross-cutting assertions

- Todas as operações críticas têm auditoria na mesma transação e correlation ID.
- Publicação, snapshot, documento e auditoria não aceitam update/delete comum.
- Erros usam `application/problem+json`, não expõem stack trace nem dados sensíveis e são legíveis.
- Consultas públicas nunca retornam draft, revisão, autorização interna ou auditoria restrita.
- Migrations são aplicáveis do zero e nunca reescrevem uma migration já aplicada.
- Os 38 requisitos funcionais ativos e 29 cenários mantêm rastreabilidade nos nomes/metadados dos
  testes; FR-037 e SC-002/009/010 permanecem registrados como diferidos para o frontend.
