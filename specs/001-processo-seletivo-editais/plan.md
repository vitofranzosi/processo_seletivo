# Implementation Plan: Processo Seletivo e Editais

**Branch**: `001-processo-seletivo-editais` | **Date**: 2026-08-27 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-processo-seletivo-editais/spec.md`

**Status**: Complete — Constitution Check aprovado antes e depois do desenho.

**Note**: Este plano encerra a Fase 1 do `$speckit-plan`; não inclui tarefas nem implementação.

## Summary

Construir um serviço web institucional como monólito modular, com modelo de domínio explícito e
persistência relacional transacional. O núcleo separa Processo Seletivo, Edital e Retificação em
agregados com máquinas de estados próprias. Conteúdo em elaboração permanece estruturado e
editável; cada Publicação materializa, em transação única, um snapshot canônico imutável, seus
metadados, hash e referência ao PDF. Retificações partem da versão vigente, registram o ato de
alteração e originam nova versão consolidada sem sobrescrever Publicações anteriores.

Operações de workflow são commands explícitos, autorizados no backend e auditados. Controle
otimista rejeita gravações e Publicações baseadas em revisões obsoletas. A API separa contratos
administrativos dos contratos públicos, e os testes cobrem invariantes, estados, segregação de
funções, temporalidade, concorrência e cenários de aceitação.

## Technical Context

**Language/Version**: Python 3.13 (último patch estável)

**Primary Dependencies**: Django 5.2 LTS; Django REST Framework; psycopg 3; gerador de PDF a
selecionar por prova de aderência/licença no primeiro incremento; especificação OpenAPI 3.1 como
contrato

**Storage**: PostgreSQL 18.x; PDFs iniciais como bytes imutáveis no mesmo banco para atomicidade,
com porta de armazenamento que permita migração futura para serviço institucional de objetos

**Testing**: pytest, pytest-django, ferramentas de teste do Django/DRF, PostgreSQL real dedicado aos
testes de persistência e concorrência e testes de contrato HTTP derivados de `contracts/openapi.yaml`

**Target Platform**: Serviço Linux conteinerizado; navegador moderno como cliente administrativo e
público (a interface gráfica não integra o primeiro incremento deste plano)

**Project Type**: Web service modular monolith

**Performance Goals**: consultas públicas usuais com p95 de até 2 segundos; reconstrução de versão
com até 20 Retificações em até 10 segundos; commands administrativos comuns com p95 de até 3
segundos, excluída a geração final de PDF

**Constraints**: negar acesso por padrão; horário institucional `America/Sao_Paulo` para regras de
calendário e `datetime` consciente de fuso em UTC para eventos; Publicações e auditoria append-only; nenhuma edição direta
de snapshot publicado; operações normativas transacionais; acessibilidade nos contratos de erro;
sem dependência obrigatória de integração externa na primeira entrega

**Scale/Scope**: escala institucional inicial de até 10 mil Processos, 100 mil Editais/Retificações,
1 milhão de Eventos/Perfis e picos de 500 consultas públicas por segundo; dimensionamento será
validado por testes de carga antes de produção e pode ser revisto com métricas reais

## Constitution Check

*GATE: aprovado antes da pesquisa e reavaliado após o desenho.*

| Princípio constitucional | Evidência no plano | Resultado |
|---|---|---|
| Linguagem e integridade do domínio | Agregados e contratos usam os termos canônicos; identidade interna não concede autorização | PASS |
| Fonte única normativa | Draft estruturado é fonte da homologação; snapshot publicado é a fonte histórica autoritativa | PASS |
| Imutabilidade e temporalidade | Publicações, Retificações, snapshots, PDFs, hashes e vigências são preservados | PASS |
| Segurança e menor privilégio | Commands exigem permissões e verificação de objeto; consultas públicas têm projeção própria | PASS |
| Segregação de funções | Autor da elaboração não conclui sozinho elaboração, homologação e Publicação | PASS |
| Auditoria | Log append-only registra ator, operação, estados, motivo, versão e correlação | PASS |
| Regras críticas no backend | Máquinas incluem `ENCERRADO` distinto de `CANCELADO`; FR-039 rege consolidação temporal | PASS |
| Transações e concorrência | Lock otimista e transações protegem homologação, Publicação e atos finais | PASS |
| Contratos explícitos | OpenAPI separa commands, responses, erros e consultas públicas | PASS |
| Migrations versionadas | Migrations do Django; migration aplicada nunca é reescrita | PASS |
| Qualidade e rastreabilidade | Testes rastreiam 38 FRs ativos, 29 cenários e precedência temporal cumulativa; FR-037 e SC-002/009/010 estão formalmente diferidos para o frontend | PASS |
| Simplicidade | Monólito modular; sem microsserviços, CQRS, mensageria ou event sourcing | PASS |

**Resolução dos gates anteriores**: FR-006 define `ENCERRADO` como conclusão regular distinta de
`CANCELADO`; FR-039 define composição por `effectiveAt`, cumulativa, e desempate por `publishedAt`
mais recente somente em conflitos no mesmo conteúdo. Nenhuma ambiguidade impeditiva permanece.

### Post-design re-check

PASS. `research.md`, `data-model.md`, `contracts/openapi.yaml` e `quickstart.md` preservam as
garantias constitucionais. Não há violação que exija registro em Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/001-processo-seletivo-editais/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openapi.yaml
├── checklists/
│   └── requirements.md
└── tasks.md                 # criado somente por $speckit-tasks
```

### Source Code (repository root)

```text
backend/
├── pyproject.toml
├── manage.py
├── config/                  # settings, URLs, ASGI e WSGI
├── processo_seletivo/
│   ├── processos/           # domínio, aplicação, API e persistência do Processo
│   ├── editais/             # Edital, Perfil, vagas, Cronograma e workflow
│   ├── publicacoes/         # Retificação, versões, documentos e consultas temporais
│   ├── seguranca/           # ator autenticado, permissões e autorização por objeto
│   ├── auditoria/           # eventos append-only e correlação
│   └── shared/              # tipos realmente compartilhados (tempo, erros, IDs)
└── tests/
    ├── unit/
    ├── integration/
    ├── contract/
    ├── authorization/
    └── acceptance/
```

**Structure Decision**: um único backend organizado como projeto Django com apps por capacidade de
negócio. Cada app contém seus próprios módulos de domínio, aplicação, API, infraestrutura e
`migrations`, evitando camadas globais acopladas. Models, serializers e views não concentram as
regras de workflow: casos de uso explícitos coordenam autorização, domínio e persistência.
Interfaces administrativas e públicas são adaptadores do mesmo núcleo transacional. Um frontend
poderá ser planejado separadamente quando houver especificação própria de interface.

FR-037 e SC-002/009/010 estão fora deste incremento e preservados na especificação apenas como
itens diferidos. O backend continua responsável por respostas claras e acessíveis em
`application/problem+json`, mas não implementa confirmação visual, navegação por teclado ou testes
de usabilidade.

## Domain and Application Design

### Aggregate boundaries

- **ProcessoSeletivo**: raiz responsável por identidade institucional, estado e atos de ativação,
  encerramento e cancelamento. Mantém referências aos Editais, não seus conteúdos completos.
- **Edital**: raiz responsável pelo draft normativo, Perfis, vagas, Cadastro Reserva, Modalidades de
  Concorrência e Cronograma. Controla revisão, homologação e elegibilidade para Publicação.
- **Retificacao**: raiz vinculada ao Edital e à Publicação-base; mantém proposta, justificativa,
  fluxo de revisão/homologação e vigência futura opcional.
- **Publicacao**: registro imutável produzido por uma operação de domínio. Contém snapshot canônico,
  hash, artefato PDF, sequência e intervalo de vigência; nunca recebe update/delete comum.
- **RegistroAuditoria**: append-only e separado dos agregados para consulta investigativa, escrito na
  mesma transação das operações sensíveis.

### Publication and version strategy

1. O Edital é elaborado em estruturas normalizadas e versionadas por lock otimista.
2. A homologação fixa a revisão candidata e registra elaborador e homologador.
3. A Publicação bloqueia logicamente a revisão homologada, revalida invariantes e segregação,
   serializa conteúdo canônico determinístico, gera PDF e calcula hashes.
4. A transação persiste Publicação, snapshot, metadados do documento e auditoria; o artefato só é
   divulgado após sucesso integral.
5. Uma Retificação referencia o snapshot conhecido na elaboração, preserva alterações estruturadas
   por caminho normativo e, na Publicação, registra `publishedAt`, `effectiveAt` e sequência.
6. A vigência inicia na Publicação, salvo data futura expressa; `effectiveAt < publishedAt` é
   rejeitado. Publicar não implica vigorar imediatamente quando houver data futura.
7. Para um instante T, o consolidador parte do Edital original e aplica todas as Retificações com
   `publishedAt <= T` e `effectiveAt <= T`, ordenadas por `effectiveAt`, depois `publishedAt` e por
   sequência de Publicação como chave determinística. Alterações não conflitantes acumulam; no
   mesmo `effectiveAt`, conflito no mesmo caminho é vencido pela última Publicação.
8. Cada mudança no conteúdo aplicável materializa snapshot consolidado completo, imutável e
   hasheado. Consultas usam o snapshot correspondente, sem depender do estado atual.

Essa estratégia usa snapshots imutáveis, não event sourcing. O custo adicional de armazenamento é
aceito em troca de reprodução jurídica simples, integridade verificável e consultas públicas
previsíveis.

### State machines

- **Processo**: `EM_ELABORACAO -> ATIVO -> ENCERRADO`; `EM_ELABORACAO|ATIVO -> CANCELADO` somente
  se todos os Editais estiverem `ENCERRADO|CANCELADO`. Ativação, encerramento e cancelamento são
  commands explícitos e auditados; situações dos Editais não propagam transição automática.
- **Edital**: `EM_ELABORACAO -> EM_REVISAO -> HOMOLOGADO -> PUBLICADO -> ENCERRADO`; antes da
  Publicação, revisão pode devolver para elaboração e homologação pode ser revogada para revisão;
  cancelamento autorizado leva estados não finais a `CANCELADO`. Conteúdo publicado só muda por
  Retificação.
- **Retificação**: `EM_ELABORACAO -> EM_REVISAO -> HOMOLOGADA -> PUBLICADA`; retornos para correção
  apenas antes da Publicação; cancelamento autorizado leva estado não final a `CANCELADA`.
- **Publicação**: registro imutável criado como `PUBLICADA`; sua aplicabilidade em T é derivada de
  `publishedAt`, `effectiveAt` e da precedência normativa, sem alterar seu estado histórico.

### Authorization and segregation

Permissões são ações (`processo:ativar`, `edital:elaborar`, `edital:homologar`,
`edital:publicar`, `retificacao:publicar`, `ato:cancelar`, `auditoria:consultar`) avaliadas em
conjunto com o recurso e seu estado. O ator autenticado e seu contexto institucional são passados
ao command; a camada de aplicação aplica autorização e o domínio protege invariantes.

Na Publicação, o sistema compara o ator com a autoria da revisão homologada. Se o mesmo ator tiver
executado a elaboração, outro ator autorizado deve constar como homologador ou publicador. A
evidência dos participantes integra a Publicação e a auditoria. Cargos são metadados institucionais,
não condições codificadas.

### Audit strategy

Cada command sensível produz um `RegistroAuditoria` com identificador de correlação, ator,
permissão exercida, agregado, ID, instante único da transação, estado/revisão anterior e posterior,
motivo, Publicação/Retificação relacionada e origem. Conteúdos sensíveis não são copiados para o
log; snapshots são referenciados por ID e hash. A função de aplicação só insere; privilégios do
banco impedem update/delete pela credencial da aplicação.

## Persistence and Concurrency

- Esquema relacional normalizado para drafts, relacionamentos e regras; snapshots canônicos em
  formato estruturado versionado e imutável para reprodução exata.
- Chaves internas opacas; constraints para cardinalidades, estados, datas, sequências, unicidade
  institucional e vínculos; índices para busca pública, vigência e auditoria.
- Coluna de revisão/versão em agregados mutáveis. Commands exigem revisão esperada; conflito retorna
  erro explícito sem merge silencioso.
- Casos de uso normativos executam em `transaction.atomic()`. Após `select_for_update()`, revalidam
  estado, revisão e participantes; a revisão esperada também é aplicada como comparação condicional
  para impedir gravação obsoleta. Django ORM não é tratado como mecanismo automático de lock otimista.
- Publicação, Retificação, cancelamento e encerramento executam em transação com revalidação após
  aquisição de lock apropriado. Restrição única impede duas Publicações com a mesma sequência.
- Locks seguem ordem estável: Processo primeiro e Editais relacionados por ID. Transições de Edital
  que afetam a situação final também bloqueiam o Processo pai, evitando TOCTOU no cancelamento.
- Hashes são calculados sobre bytes canônicos produzidos por serializador versionado; não dependem
  da representação interna de `JSONField`/JSONB.
- PDF é gerado, hasheado e gravado como bytes imutáveis na mesma transação normativa na primeira
  entrega; falha não pode expor Publicação parcial. Uma porta de armazenamento evita acoplamento e
  permite futura migração para object storage com staging/compensação formalmente planejados.
- Backup, restauração pontual, cópia imutável dos PDFs e teste periódico de recuperação são
  requisitos operacionais; RPO/RTO definitivos dependem do acordo institucional registrado como
  risco.

## API and Contracts

O contrato em `contracts/openapi.yaml` separa:

- resources e commands administrativos de Processo, Edital, Perfil, Cronograma e Retificação;
- endpoints explícitos de submissão, homologação, Publicação, ativação, encerramento e cancelamento;
- consultas públicas de versão vigente, linha histórica e conteúdo vigente em um instante;
- consulta administrativa de auditoria;
- paginação por cursor/limite e filtros documentados;
- `ETag`/revisão esperada para detectar atualização obsoleta;
- erros consistentes em `application/problem+json`, sem detalhes internos.

Models do Django não atravessam a fronteira. Serializers de entrada representam intenção e
serializers/projeções de saída são específicos. Permissions do DRF fazem a barreira HTTP e os casos
de uso repetem a autorização contextual. Operações de domínio não são reduzidas a atualização
genérica de status.

## Test Strategy

- **Unitários de domínio**: todas as transições, invariantes temporais, Cadastro Reserva, cotas,
  segregação, elegibilidade para Publicação e cancelamento do Processo.
- **Aplicação/autorização**: matriz por command, recurso e estado; negação padrão, IDOR e participantes
  distintos da Publicação.
- **Persistência**: constraints, migrations, consultas de vigência, append-only, hash/snapshot e
  concorrência com PostgreSQL real; testes transacionais usam `TransactionTestCase` ou
  `pytest.mark.django_db(transaction=True)`, nunca SQLite como substituto.
- **Integração**: transações de Publicação/Retificação, geração/falha de PDF, armazenamento de
  artefatos e reconstrução após até 20 Retificações.
- **Migrations**: criação do zero, upgrade desde a versão anterior e verificação de que não existem
  alterações de models sem migration; migrations aplicadas são append-only.
- **Contrato/API**: requests, responses, paginação, `ETag`, erros e separação público/administrativo
  conforme OpenAPI.
- **Aceitação**: os 29 cenários Given/When/Then do spec, incluindo múltiplos Editais/Cronogramas,
  vigência futura fora de ordem, empate com conflito, encerramento, segregação e cancelamento.
- **Concorrência**: homologações simultâneas, duas Publicações da mesma revisão, Retificação baseada
  em versão obsoleta e cancelamento concorrente.
- **Não funcionais**: carga das consultas públicas, acessibilidade dos erros, restauração e
  verificação periódica de hashes.

## Risks and Follow-ups

- **RPO/RTO institucional**: definir antes de produção; até lá, planejar teste de restauração e não
  assumir disponibilidade contratual.
- **Armazenamento institucional de documentos**: confirmar serviço e política de retenção antes de
  superar a estratégia inicial no PostgreSQL; a porta interna evita acoplamento.
- **Gerador de PDF**: validar fidelidade, acessibilidade, determinismo e licença antes de escolher.
- **Identidade institucional**: integrar provedor apenas após contrato de autenticação; autorização
  permanece baseada em permissões do sistema.
- **Regras legais de cotas**: cada versão deve ser fornecida e homologada pela instituição; nenhuma
  fórmula padrão será tratada como interpretação jurídica.
- **Escala estimada**: validar volumes e picos do Technical Context com dados institucionais antes
  de definir capacidade de produção; isso não altera o modelo funcional.

## Complexity Tracking

Não aplicável. O desenho não viola a Constituição nem introduz complexidade arquitetural que exija
exceção.
