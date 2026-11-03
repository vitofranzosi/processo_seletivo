# Data Model: Documentos e conferência na convocação

Caminhos relativos a `backend/processo_seletivo/`. "Append-only" quer dizer em duas camadas: gatilho
`BEFORE UPDATE OR DELETE` e entrada em `TABELAS_APPEND_ONLY`, com o privilégio revogado pelo
provisionamento. O modelo também recusa `save` de linha existente e `delete`.

## Documento Exigido (`editais.DocumentoExigido`, existe)

| Campo novo | Tipo | Regra |
|---|---|---|
| `momento` | `CharField(20)`, choices `NA_INSCRICAO` / `NA_CONVOCACAO`, default `NA_INSCRICAO` | FR-3563; forma publicada `moment`: `AT_ENROLLMENT` / `AT_CALL` (o vocabulário do Requerimento) |
| `aproveita` | `UUIDField(null=True)` | FR-3566; id de outro Documento Exigido do mesmo Edital, `NA_INSCRICAO`; não FK (R-001); forma publicada `reusesRequirementId` |

- Check `ck_documento_aproveita_so_na_convocacao`: `aproveita IS NULL OR momento = 'NA_CONVOCACAO'`.
- A coerência entre linhas (o aproveitado existe, é do Edital e é da inscrição) é conferida na
  validação da publicação, porque as linhas se recriam a cada gravação do rascunho.
- Contrato de mutabilidade: `(documentRequirements, moment)` e
  `(documentRequirements, reusesRequirementId)` são não retificáveis (D-014).
- Elevação: degrau 18, `{"moment": "AT_ENROLLMENT", "reusesRequirementId": None}`.

## Item da lista da convocação (`convocacao.ItemDaListaDaConvocacao`, novo, append-only)

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | |
| `chamada` | FK `Convocacao`, `PROTECT` | sempre a **raiz** (sem `convocacao_anterior`) — R-002 |
| `inscricao` | FK `inscricoes.Inscricao`, `PROTECT` | igual à da chamada (gatilho) |
| `versao` | FK `VersaoConsolidada`, `PROTECT` | a vigente no instante da convocação |
| `requisito_id` | UUID | id do Documento Exigido publicado |
| `chave` | `CharField(100)` | `key` publicada |
| `situacao` | choices `OBRIGATORIO` / `FACULTATIVO` / `NAO_SE_APLICA` | |
| `forma_do_recorte`, `perfil_id`, `modalidade_id`, `modalidade_codigo` | como em `ItemDaListaExigida` | |
| `aproveita_requisito_id` | UUID null | o declarado no publicado |
| `gravada_em` | DateTime | = `chamada.criado_em` (gatilho) |

- Unique `(chamada, requisito_id)`.
- Gatilho de coerência no INSERT: a chamada é raiz, a inscrição é a dela e `gravada_em` coincide.
- Sem evento de trilha: faz parte do ato de convocar (FR-3572).

## Apresentação (`convocacao.ApresentacaoDeDocumento`, novo, append-only)

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | |
| `item` | FK `ItemDaListaDaConvocacao`, `PROTECT` | |
| `numero` | PositiveInteger | 1, 2, 3… por item; unique `(item, numero)` |
| `arquivo` | `FileField(ArmazenamentoPrivado)`, blank | `convocacoes/<chamada_id>/<uuid4>.pdf` |
| `nome_original`, `tamanho`, `content_hash` | como em `DocumentoSubmetido` | o hash é sempre preenchido, inclusive na referência (cópia do hash do envio) |
| `documento_da_inscricao` | FK `inscricoes.DocumentoSubmetido`, null, `PROTECT` | a referência à inscrição (FR-3576, e FR-3619 quando a origem era da inscrição); nunca CASCADE (MAT-16) |
| `apresentacao_de_origem` | FK self, null, `PROTECT` | a referência a chamada anterior (FR-3619): sempre uma apresentação **com arquivo** |
| `apresentado_por` | `CharField(255)` | subject do titular, ou `"convocacao:<id>"` para a referência criada pelo ato |
| `unidade_de_atuacao` | `CharField(100)` | R-008 |
| `apresentado_em` | DateTime | |

- Check `ck_apresentacao_arquivo_ou_referencia`: exatamente um entre `arquivo` não vazio,
  `documento_da_inscricao` e `apresentacao_de_origem`.
- Gatilho de coerência no INSERT:
  - `documento_da_inscricao`: é da mesma inscrição do item, e o requisito dele é o
    `aproveita_requisito_id` do item, ou o mesmo requisito vindo de chamada anterior;
  - `apresentacao_de_origem`: tem arquivo (nunca referência a referência), é de item da mesma
    inscrição, do mesmo `requisito_id` e de outra chamada raiz anterior;
  - `content_hash` é o da origem.
- **Vigente** = maior `numero` do item. Nenhuma coluna de vigência.

## Conferência (`convocacao.ConferenciaDeDocumento`, novo, append-only)

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | |
| `item` | FK `ItemDaListaDaConvocacao`, `PROTECT` | |
| `apresentacao` | FK `ApresentacaoDeDocumento`, null, `PROTECT` | a julgada; nula só para pendente ou não se aplica sem apresentação |
| `hash_conferido` | `CharField(64)`, blank | cópia do hash da apresentação (prova depois de o arquivo sair; §6 do complemento) |
| `resultado` | choices `CONFORME` / `PENDENTE` / `NAO_SE_APLICA` | |
| `motivo` | Text | obrigatório para `PENDENTE` e `NAO_SE_APLICA` |
| `conferencia_anterior` | FK self, null, `PROTECT` | a que esta substitui |
| `motivo_da_substituicao` | Text | obrigatório quando a anterior julgou a **mesma** apresentação |
| `conferido_por` | `CharField(255)` | subject |
| `unidade_de_atuacao` | `CharField(100)` | R-008 |
| `conferido_em` | DateTime | |

Checks:
- `ck_conferencia_motivo`: motivo não vazio se o resultado não é `CONFORME`;
- `ck_conferencia_conforme_com_apresentacao`: `CONFORME` exige `apresentacao`;
- `ck_conferencia_hash`: hash não vazio se há `apresentacao`.

Gatilho de coerência no INSERT: a apresentação é do mesmo item, e `hash_conferido` é o dela.

**Vigente** = a mais recente do item. As recusas de versão superada, de "conforme" sem abertura e de
chamada fechada são do serviço (R-005), sob trava.

## Alocação à conferência (`comissoes.AlocacaoAConferencia`, novo; molde da `AlocacaoEtapa`)

| Campo | Tipo |
|---|---|
| `id` | UUID |
| `membro` | FK `MembroComissao`, `PROTECT` |
| `edital` | FK `Edital`, `PROTECT` |
| `perfil_id` | UUID null (nulo = todos os Perfis) |
| `ativo` | Boolean |
| `criado_em`, `criado_por`, `inativado_em`, `inativado_por` | como na `AlocacaoEtapa` |
| `unidade_de_atuacao` | `CharField(100)` |

- Unique parcial `(membro, edital, perfil_id) WHERE ativo`.
- **Não é append-only.** Segue a `AlocacaoEtapa`, que inativa por flag, e cada mudança tem trilha.
  Não entra no `M` do provisionamento.

## Estado derivado (sem tabela)

`convocacao/domain/documentos.py`, puro:

- `estado_do_item(item, apresentacoes, conferencias)` devolve um valor da FR-3590;
- `estado_da_convocacao(itens…, desfecho)` devolve um valor da FR-3591, na precedência escrita lá;
- `pendencias_para_incluir(itens…)` devolve os obrigatórios que impedem aceite e regularização
  (FR-3592);
- `origem_aproveitavel(item_anterior, apresentacoes, conferencias)` devolve o arquivo de origem, ou
  `None` se o item anterior é *pendente* ou não tem apresentação (FR-3619).

## Requerimento de Matrícula (`requerimentos`, existe, sem mudança de forma)

Nenhum campo novo. `apurar()` recebe `prazo_decorrido`, injetado pela aplicação a partir da função de
prazo da `019` (FR-3622).
Nenhuma linha se apaga e o rascunho se preserva.

## Contagens

- `TABELAS_APPEND_ONLY`: **46 → 49**. A linha do `CLAUDE.md` sobre o `N de M` ganha "**49** com os
  documentos da convocação da `115`".
- Migrations por app (`tests/migrations/test_migrations.py`): `editais` +1, `convocacao` +1,
  `comissoes` +1.
- `SCHEMA_VERSION`: 17 → 18.
- Campos retificáveis do contrato: 84, inalterado.
