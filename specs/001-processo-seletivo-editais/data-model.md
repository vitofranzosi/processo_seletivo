# Data Model: Processo Seletivo e Editais

## Mapeamento para Django

O modelo abaixo permanece orientado ao domínio. Models do Django são adaptadores de persistência,
com `CheckConstraint`, `UniqueConstraint`, índices e migrations espelhando as invariantes que o
banco consegue garantir. Transições, autorização contextual e consolidação temporal permanecem em
serviços de domínio/aplicação; não dependem de `save()`, signals ou serializers. Datas persistidas
são `datetime` conscientes de fuso em UTC, convertidas para `America/Sao_Paulo` apenas nas regras de
calendário e apresentação.

Agregados mutáveis possuem `revision` e são atualizados por compare-and-swap. Commands críticos
usam `transaction.atomic()` e `select_for_update()`; quando Processo e Editais participam da mesma
decisão, o lock ocorre sempre no Processo e depois nos Editais ordenados por ID. Snapshots guardam a
versão do algoritmo de canonicalização junto aos hashes.

## Modeling principles

- Identidade interna opaca e identificação institucional são valores distintos.
- Agregados mutáveis usam revisão otimista; registros normativos publicados são append-only.
- Instantes administrativos são UTC; datas institucionais são interpretadas em
  `America/Sao_Paulo` quando a regra depender de calendário.
- Publicação, início de vigência, encerramento e cancelamento são conceitos separados.
- Dados estruturados da revisão homologada originam snapshot canônico e PDF; o snapshot publicado
  é a fonte histórica autoritativa.
- “Mesmo conteúdo” é identificado por endereço normativo canônico baseado em chaves estáveis, não
  por posição de array ou texto do PDF. Caminhos ancestrais/descendentes são conflitantes.

## Aggregate map

```text
ProcessoSeletivo (aggregate root)
└── referências 1..N Edital

Edital (aggregate root)
├── 1..N PerfilVaga
│   ├── Vaga / CadastroReserva
│   └── 0..N ModalidadeConcorrencia
├── 1 Cronograma
│   └── 0..N EventoCronograma
├── 0..N RevisaoEdital / Homologacao
└── contador de ordem de Publicação

Retificacao (aggregate root)
├── 1..N AlteracaoNormativa
├── RevisaoRetificacao / Homologacao
└── 0..1 Publicacao

Fluxo normativo imutável por Edital
├── Publicacao
├── VersaoConsolidada
├── DocumentoPublicado
└── ProvenienciaConteudo

RegistroAuditoria (append-only, fora dos agregados de negócio)
```

## ProcessoSeletivo

Representa a iniciativa institucional, sem confundir seu ciclo com os Editais.

| Field | Meaning | Rules |
|---|---|---|
| `id` | identidade interna estável | opaca, imutável |
| `institutionalCode` | identificação institucional | única no escopo institucional configurado |
| `title` | identificação legível | obrigatória |
| `status` | ciclo do Processo | enum explícito |
| `revision` | concorrência otimista | incrementada em alteração válida |
| `createdAt/createdBy` | autoria | imutáveis |
| `lastChangedAt` | instante da revisão | mesmo relógio da transação |

### State transitions

```text
EM_ELABORACAO --ativar--> ATIVO --encerrar--> ENCERRADO
      |                    |
      +----cancelar--------+----cancelar----> CANCELADO
```

- Ativação e encerramento são atos explícitos; estados de Editais não os inferem.
- `ENCERRADO` e `CANCELADO` são finais.
- Cancelamento é bloqueado enquanto existir Edital fora de `ENCERRADO|CANCELADO`.
- Constituição formal exige primeiro Edital válido na mesma transação de criação.

## Edital

Raiz do conteúdo em elaboração e do workflow próprio do Edital.

| Field | Meaning | Rules |
|---|---|---|
| `id` | identidade interna | estável e opaca |
| `processoId` | Processo proprietário | obrigatório; exatamente um |
| `number/year` | identificação institucional | unique no escopo institucional aplicável |
| `title/description` | identificação e conteúdo editorial | título obrigatório |
| `status` | ciclo do Edital | enum explícito |
| `revision` | revisão mutável | optimistic lock |
| `nextPublicationOrder` | próxima ordem real de Publicação | monotônica, atribuída sob lock |
| `createdAt/createdBy` | autoria inicial | imutáveis |
| `lastEditedBy` | autor da revisão atual | usado na segregação |

### State transitions

```text
EM_ELABORACAO --> EM_REVISAO --> HOMOLOGADO --> PUBLICADO --> ENCERRADO
      ^               |              |
      +---------------+--------------+  (retornos permitidos somente antes de publicar)

EM_ELABORACAO | EM_REVISAO | HOMOLOGADO | PUBLICADO --cancelar--> CANCELADO
```

- `ENCERRADO`: conclusão regular após etapas; ato explícito e auditado.
- `CANCELADO`: interrupção administrativa; motivo e ato obrigatórios quando aplicável.
- Após `PUBLICADO`, conteúdo muda somente por Retificação.
- Estados finais não retornam a estados anteriores.

## PerfilVaga

Entidade interna ao Edital que delimita requisitos e oportunidades independentes.

| Field | Meaning | Rules |
|---|---|---|
| `id` | identidade estável no Edital | usada em caminhos normativos |
| `editalId` | Edital proprietário | obrigatório |
| `code/name/description` | identificação | código único no Edital |
| `requirements` | requisitos estruturados | não vazios quando exigidos |
| `location/modality` | contexto | opcionais conforme Edital |
| `immediateVacancies` | vagas imediatas | inteiro >= 0 |
| `reserveType` | `NONE`, `LIMITED`, `UNLIMITED` | explícito |
| `reserveLimit` | limite de Cadastro Reserva | obrigatório só para `LIMITED`, >= 0 |

O Perfil possui zero ou mais Modalidades de Concorrência. Vagas e modalidades não se propagam
para outro Perfil sem ação explícita.

## ModalidadeConcorrencia e RegraNormativa

`ModalidadeConcorrencia` associa um Perfil a uma versão de `RegraNormativa` e registra os
parâmetros homologados para aquele contexto. `RegraNormativa` possui identidade, modalidade,
fundamento, vigência, versão e definição estruturada de cálculo/distribuição. Versões publicadas
nunca são alteradas retroativamente. Resultado da aplicação é conceito separado e fica fora desta
feature, salvo projeção necessária ao documento.

## Cronograma e EventoCronograma

Cada Edital possui exatamente um Cronograma, ainda que inicialmente vazio. Evento possui ID
estável, tipo extensível, descrição, `startAt`, `endAt` opcional, sequência lógica e visibilidade.

Invariantes:

- `startAt <= endAt` quando houver término;
- Evento pertence ao Cronograma do mesmo Edital;
- sequência e sobreposições automaticamente incompatíveis são rejeitadas;
- mudança após Publicação ocorre somente por Retificação.

## RevisaoEdital e Homologacao

`RevisaoEdital` identifica a revisão estruturada exata do draft, autor, instante, schema canônico e
hash do conteúdo. `Homologacao` referencia uma única revisão, ator, autoridade/cargo quando
aplicável, instante e estado. Revogar homologação não apaga o registro; cria ato correspondente e
devolve o workflow antes da Publicação.

A Publicação só aceita o mesmo hash/revisão homologado. Alteração posterior do draft invalida sua
elegibilidade e exige nova revisão/homologação.

## Retificacao

Raiz para preparar um ato que pode alterar qualquer conteúdo do Edital.

| Field | Meaning | Rules |
|---|---|---|
| `id` | identidade interna | estável |
| `editalId` | Edital publicado | obrigatório |
| `baseSnapshotId` | versão conhecida ao elaborar | proveniência, não limita composição futura |
| `status` | workflow próprio | enum explícito |
| `justification` | razão administrativa | obrigatória para submissão |
| `requestedEffectiveAt` | vigência futura opcional | se ausente, usa Publicação |
| `revision` | concorrência do draft | optimistic lock |
| `preparedBy/submittedBy` | participantes | auditáveis |

### State transitions

```text
EM_ELABORACAO --> EM_REVISAO --> HOMOLOGADA --> PUBLICADA
      ^               |
      +---------------+

estado não final --cancelar--> CANCELADA
```

Retornos para correção só ocorrem antes da Publicação. `PUBLICADA` e `CANCELADA` são finais.

## AlteracaoNormativa

Operação estruturada imutável após a Publicação da Retificação.

| Field | Meaning | Rules |
|---|---|---|
| `retificacaoId` | ato proprietário | obrigatório |
| `targetPath` | endereço canônico do conteúdo | usa IDs/chaves estáveis |
| `operation` | adicionar, substituir ou remover | vocabulário fechado/versionado |
| `expectedPreviousHash` | conteúdo conhecido na elaboração | detecta base obsoleta/conflito |
| `newValue` | novo valor canônico | conforme schema do caminho |
| `schemaVersion` | interpretação do path/valor | obrigatório |

Caminhos iguais ou com relação ancestral/descendente conflitam. Caminhos independentes compõem.
O PDF/texto não é usado para detectar conflito.

## Publicacao

Registro imutável da efetiva Publicação do Edital original ou de uma Retificação.

| Field | Meaning | Rules |
|---|---|---|
| `id` | identidade da Publicação | imutável |
| `editalId` | fluxo normativo | obrigatório |
| `sourceType/sourceId` | original ou Retificação | uma Publicação por fonte homologada |
| `publicationOrder` | ordem real por Edital | unique e monotônica; atribuída sob lock |
| `publishedAt` | instante do ato | relógio único da transação |
| `effectiveAt` | início da vigência | >= `publishedAt` |
| `preparedBy/homologatedBy/publishedBy` | segregação | não podem ser todos a mesma pessoa |
| `signatory/name/role` | Autoridade Signatária | obrigatórios conforme ato |
| `snapshotAtPublicationId` | snapshot registrado | não antecipa vigência futura |
| `documentId` | bytes publicados | imutável |
| `contentHash/documentHash` | integridade | SHA-256 ou sucessor versionado |

`publicationOrder` é evidência técnica da ordem real do ato e desempata Publicações com o mesmo
timestamp; não substitui `effectiveAt` como precedência primária.

## VersaoConsolidada

Snapshot canônico completo e imutável do conteúdo aplicável em uma fronteira temporal.

| Field | Meaning | Rules |
|---|---|---|
| `id` | identidade da versão | imutável |
| `editalId` | Edital | obrigatório |
| `validFrom` | fronteira de vigência | início inclusivo |
| `materializedAt` | quando foi gerada | não muda `validFrom` |
| `triggerType/triggerKey` | original, Publicação ou início de vigência | idempotência única |
| `canonicalSchemaVersion` | schema do snapshot | obrigatório |
| `content` | snapshot estruturado | imutável |
| `contentHash` | integridade | verificável por recomposição |
| `appliedActSetHash` | conjunto/ordem dos atos | determinismo |

O término lógico é o próximo `validFrom`; não se atualiza destrutivamente o snapshot anterior.
Uma versão futura publicada pode ser registrada sem antecipar efeito. Na primeira consulta ou
materialização agendada da fronteira, a função pura recompõe o conjunto; job é otimização, nunca
fonte de verdade.

### Consolidation function at T

1. Se T precede a Publicação original, não existe conteúdo vigente.
2. Partir do snapshot original.
3. Selecionar Retificações com `publishedAt <= T` e `effectiveAt <= T`.
4. Agrupar por `effectiveAt` crescente.
5. Dentro do grupo, ordenar por `publicationOrder` crescente.
6. Aplicar operações cumulativamente; no conflito do mesmo grupo, a maior ordem vence no conteúdo.
7. Produzir snapshot, hash, conjunto de atos e proveniência.

Essa função deve ser determinística sob qualquer ordem física de leitura.

## ProvenienciaConteudo

Liga `VersaoConsolidada` aos atos aplicados e, para cada caminho alterado, à Publicação vencedora.
Permite explicar qual Retificação produziu o valor sem duplicar o conteúdo completo na auditoria.

## DocumentoPublicado

Bytes exatos divulgados, media type, tamanho, hash, nome e instante. É imutável e não regenerado
como substituto do original. Inicialmente os bytes residem no PostgreSQL; uma `storageKey` abstrata
permite migração controlada para armazenamento institucional.

## AtoAdministrativo

Registra ativação, encerramento, cancelamento, homologação e revogação com tipo, agregado, ator,
autoridade/cargo quando aplicável, instante, motivo e documento relacionado. Não substitui o estado
do agregado nem a auditoria; fornece a representação de negócio do ato.

## RegistroAuditoria

Append-only com `eventId`, `occurredAt`, ator, permissão, contexto institucional, operação, tipo/ID
do agregado, estado e revisão anteriores/posteriores, motivo, correlação, idempotency key e
referências a ato/Publicação/snapshot. Payloads sensíveis são omitidos ou representados por hash.
A credencial comum da aplicação não possui UPDATE/DELETE.

## Transaction boundaries and concurrency

- Criar Processo + primeiro Edital: uma transação; nenhum Processo parcial.
- Editar agregado: revisão esperada obrigatória; stale write falha.
- Homologar/Publicar: lock curto no Edital/Retificação, revalidação de hash, estado, autorização e
  segregação; ordem de Publicação atribuída atomicamente.
- Consolidar: lock lógico por Edital + fronteira, operação idempotente e verificação por hash.
- Encerrar/Cancelar Processo: lock no Processo e leitura bloqueante/set-based dos estados dos
  Editais; qualquer não final bloqueia cancelamento.
- Constraints únicas: identificação institucional, ordem por Edital, fonte publicada uma vez,
  idempotência e trigger de snapshot.
- Exclusão em cascata é proibida para Publicações, versões, documentos, atos e auditoria.

## Required indexes

- identificação institucional e `(processo_id, status)`;
- `(edital_id, publication_order)` unique;
- `(edital_id, effective_at, publication_order)` para composição;
- `(edital_id, valid_from)` para consulta histórica;
- documentos/hash e fonte de Publicação unique;
- auditoria por `(aggregate_type, aggregate_id, occurred_at)` e `correlation_id`.
