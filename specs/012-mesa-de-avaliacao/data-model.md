# Data Model: Mesa de Avaliação

**Feature**: `012-mesa-de-avaliacao` | **Spec**: [spec.md](./spec.md) | **Pesquisa**: [research.md](./research.md)

Quatro entidades novas num app novo, e **dois campos** em conteúdo normativo existente. Nada mais
muda de esquema: nenhuma coluna nova em `comissoes`, `inscricoes`, `publicacoes` ou `auditoria`.

---

## 1. O incremento normativo

É a única parte deste modelo que é conteúdo publicado, e ela acontece uma vez (FR-007, FR-008).

### 1.1 Elaboração — `editais.EtapaAvaliacao`

| campo | tipo | regra |
|---|---|---|
| `evaluations_per_registration` | `PositiveSmallIntegerField`, nulo | nulo significa "não declarado"; a leitura resolve para 1 |
| `maximum_score` | `Decimal(7,4)`, nulo | nulo significa "não declarado"; positivo quando presente |

Dois `CheckConstraint`, pela forma que a Etapa já usa para `weight` e `minimum_score`:
`evaluations_per_registration` nulo ou maior que zero — zero avaliações não é declaração, é
contradição —, e `maximum_score` nulo ou maior que zero.

**Coerência entre campos não entra no banco.** Que `minimum_score` não exceda `maximum_score` é
regra de domínio, verificada na publicação junto com as outras faixas, no mesmo lugar em que a
não-negatividade da nota mínima já é verificada. O banco confere campo a campo, como já faz.

### 1.2 Publicado — a Etapa no snapshot, versão canônica 5

```json
{
  "id": "…", "name": "…", "order": 0,
  "weight": null, "eliminatory": true, "classificatory": false,
  "minimumScore": "70.0000",
  "evaluationsPerRegistration": 2,
  "maximumScore": "100.0000",
  "scheduleEventId": null
}
```

`evaluationsPerRegistration` é inteiro e admite nulo; `maximumScore` é decimal canônico e admite
nulo, na mesma forma dos outros dois decimais da Etapa. A transcrição em `ETAPA_PUBLICADA` e o
esquema `EtapaPublicada` do `openapi.yaml` da 001 mudam **juntos** — o teste de contrato existe para
que não mudem separados (T-014).

`SCHEMA_VERSION` sobe de 4 para 5, uma vez, carregando as duas propriedades. Elas viajam juntas pela
razão que o próprio módulo registra nos incrementos anteriores: subir a versão com uma e acrescentar
a outra depois produziria snapshots da mesma versão com e sem a segunda.

### 1.3 A leitura da ausência

```text
avaliacoes_previstas(etapa_publicada) -> int          # ausente ou nulo => 1
pontuacao_maxima(etapa_publicada)     -> Decimal|None  # ausente ou nulo => None
```

Um lugar só, usado por Mesa, distribuição, validação e documento. Nenhum consumidor testa presença
de chave (T-002).

### 1.4 A elevação

```text
elevar(conteúdo) -> conteúdo'      # função pura, sem autoria, sem proveniência
```

Aplicada na fronteira que carrega conteúdo para **compor ou consolidar Retificação**, e em lugar
nenhum além. Não escreve linha, não altera hash gravado, não cria `ProvenienciaConteudo` (T-001).

---

## 2. `avaliacoes.Atribuicao`

> esta pessoa avalia esta inscrição, nesta Etapa.

| campo | tipo | nota |
|---|---|---|
| `id` | UUID | |
| `membro` | FK `MembroComissao`, PROTECT | **não** FK para a alocação (D-004 da spec) |
| `edital` | FK `Edital`, PROTECT | |
| `etapa_id` | UUID | identidade no conteúdo publicado; não é FK (T-004) |
| `inscricao` | FK `Inscricao`, PROTECT | |
| `ativo` | bool | |
| `criado_em` / `criado_por` | | |
| `inativado_em` / `inativado_por` | nulos | |

**Constraints**

- `UniqueConstraint(membro, edital, etapa_id, inscricao) WHERE ativo` — FR-003. Parcial, para que
  redistribuir depois de remover crie linha nova e o histórico permaneça.
- `CheckConstraint` de completude: ativo sem instante de inativação, inativo com ele — o mesmo par
  que a 011 usa nos dois modelos dela.
- Índices: `(edital, etapa_id, ativo)` para a organização do trabalho e `(membro, edital, etapa_id,
  ativo)` para a Mesa.

**Invariantes verificados no comando**, porque o banco não os expressa sem a FK que T-004 proíbe:

1. `membro` tem alocação ativa em `(edital, etapa_id)` — FR-011.
2. `etapa_id` existe na Versão Consolidada vigente do Edital — a mesma verificação da 011.
3. `inscricao.edital == edital` e `inscricao.status == SUBMETIDA` — FR-002, FR-012.
4. não existe `Impedimento` para `(identity_subject do membro, inscricao)` — FR-040, FR-099.
5. Atribuições ativas de `(inscricao, edital, etapa_id)` < `avaliacoes_previstas(etapa)` — FR-065, e
   a contagem é de **elegíveis**, não de histórico (FR-090).
6. não existe `Avaliacao` concluída de `(identity_subject do membro, etapa_id, inscricao)` —
   FR-074. A identidade é a da **pessoa**, e não a do vínculo, pela razão de T-007.

---

## 3. `avaliacoes.Avaliacao`

> o que esta pessoa afirmou sobre esta inscrição, e sob qual regra.

| campo | tipo | nota |
|---|---|---|
| `id` | UUID | |
| `atribuicao` | `OneToOneField`, PROTECT | FR-005, garantia de banco |
| `identity_subject` / `etapa_id` / `inscricao_id` | cópia | escrita uma vez, na criação; nunca atualizada. **A identidade é a da pessoa, não a do vínculo** (T-007) |
| `estado` | `RASCUNHO` \| `CONCLUIDA` | |
| `pontuacao` | `Decimal(7,4)`, nulo | |
| `parecer` | texto | |
| `versao` | FK `VersaoConsolidada`, PROTECT, nulo | preenchida na conclusão (FR-071) |
| `revision` | inteiro | `compare_and_swap` |
| `concluida_em` / `concluida_por` | nulos | `concluida_por` é o identificador estável (FR-006), e coincide com `identity_subject` |

**Constraints**

- `UniqueIndex(identity_subject, etapa_id, inscricao_id) WHERE estado = 'CONCLUIDA'` — FR-074. É a
  razão da tripla copiada, e está justificada em `Complexity Tracking` do plano. **Não** é
  `membro_id`: vínculo é linha que a remoção inativa e a readmissão recria, e a garantia cairia
  justamente no caso que ela existe para cobrir.
- `CheckConstraint` de completude: `CONCLUIDA` exige `pontuacao`, `versao`, `concluida_em` e
  `concluida_por` presentes — o mesmo padrão de `ck_inscricao_submetida_completa`.
- `CheckConstraint`: parecer não vazio quando `CONCLUIDA` e a Etapa for eliminatória com nota abaixo
  do mínimo — **não vai para o banco**, porque depende do conteúdo publicado e o banco não o lê. É
  regra de comando (FR-034), e está dita aqui para que a ausência seja deliberada e não esquecimento.

**Estados**

```text
                    gravar (revisão avança a cada gravação)
                         ↺
(nasce) ──────────► RASCUNHO ──── concluir ────► CONCLUIDA
                         ▲                            │
                         └────── reabrir ─────────────┘
                              (presidência, com motivo)
```

- `concluir` parte apenas de `RASCUNHO`; `reabrir` parte apenas de `CONCLUIDA` (FR-083).
- `CONCLUIDA` é imutável para o avaliador (FR-035), e a guarda vale no agregado, não só na tela.
- `concluir` grava `versao` com a Versão Consolidada lida **dentro da transação** (FR-096).

---

## 4. `avaliacoes.ConclusaoAvaliacao`

> o que havia sido concluído antes de cada reabertura.

Append-only, como `AtoAdministrativo` e `VersaoConsolidada`: `save` recusa alteração, `delete`
recusa sempre, e a proteção desce ao banco por trigger no mesmo estilo da migration `0007` de
`publicacoes`.

| campo | nota |
|---|---|
| `avaliacao` | FK, PROTECT |
| `ordem` | 1 para a primeira conclusão, 2 para a seguinte… |
| `pontuacao`, `parecer`, `versao` | o conteúdo daquela conclusão |
| `concluida_em`, `concluida_por` | |

`UniqueConstraint(avaliacao, ordem)`.

Existe por FR-094: depois de quantas reaberturas vierem, "o que aquela pessoa havia concluído antes
da terceira" tem de ser uma consulta. A trilha registra que o ato aconteceu; o conteúdo do ato vive
no domínio (FR-054).

---

## 5. `avaliacoes.Impedimento`

> esta pessoa não avalia esta inscrição, e o motivo está escrito.

| campo | nota |
|---|---|
| `identity_subject` | a **pessoa**, não o vínculo (FR-099) |
| `inscricao` | FK `Inscricao`, PROTECT — ela já determina Edital e Processo |
| `motivo` | texto, **obrigatório** (FR-039) |
| `criado_em` / `criado_por` | |

`UniqueConstraint(identity_subject, inscricao)`.

**Sem coluna `ativo`**, e a consulta é "existe Impedimento para este par". Revogar impedimento não
está na spec; criar o campo agora seria inventar ciclo de vida sem caso de uso, e se a operação
real pedir revogação isso volta à spec em vez de virar booleano acrescentado em silêncio.

O comando que registra impedimento faz duas coisas na mesma transação: cria a linha e inativa as
Atribuições ativas do par, uma `AtoAdministrativo` por Atribuição inativada. A confirmação declara
antes quantas serão inativadas (FR-041).

---

## 6. O que a 012 **não** acrescenta

- Nenhuma coluna em `MembroComissao` ou `AlocacaoEtapa`. A Atribuição é derivada da alocação, e a
  revogação é computada — nada da 011 escreve aqui (FR-059, FR-069).
- Nenhuma coluna em `Inscricao` ou `DocumentoSubmetido`. Avaliar não altera o que o candidato
  enviou, e não existe estado de retirada (FR-060, D-006 da spec).
- Nenhuma tabela de resultado, média, quórum ou situação. Isso é da 013 (FR-037).
- Nenhuma tabela de log de negócio: a trilha é `RegistroAuditoria`, e o ato com motivo é
  `AtoAdministrativo` (FR-051, T-008).

---

## 7. Autorização, como consulta

```text
pode_avaliar_inscricao(ator, edital, etapa_id, inscricao_id):
    pode_atuar_na_etapa(ator, edital, etapa_id)          # 011, intocado
    e Atribuicao.filter(membro=membro_ativo(ator, processo),
                        edital=edital, etapa_id=etapa_id,
                        inscricao_id=inscricao_id, ativo=True).exists()
```

Duas condições, e não três: o impedimento age antes, inativando a Atribuição (FR-080). Rota
individual usa esta função; **listagem nunca a usa** — usa `etapas_autorizadas` uma vez e filtra o
conjunto (FR-024, FR-048).

Perder a alocação faz a primeira condição falhar sem que nenhuma linha de Atribuição tenha sido
tocada. É assim que FR-046 e SC-010 se cumprem com zero escritas.
