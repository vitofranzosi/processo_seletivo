# Fase 1 — Modelo de dados: Gestão da Comissão e Alocação por Etapa

**Feature**: [spec.md](./spec.md) | **Plano**: [plan.md](./plan.md) | **Decisões**: [research.md](./research.md)

## 1. O que **não** muda

Nada. `ProcessoSeletivo`, `Edital`, `EtapaAvaliacao`, `Cronograma`, `EventoCronograma`, `PerfilVaga`,
`SecaoEdital`, `DocumentoExigido`, `Publicacao`, `VersaoConsolidada`, `Retificacao`,
`AlteracaoNormativa`, `Inscricao`, `DocumentoSubmetido`, `RegistroAuditoria` e `IdempotencyRecord`
seguem exatamente como estão. Nenhuma coluna nova em tabela existente, nenhuma migration fora do app
`comissoes`.

A única mudança fora dele é a **assinatura** de `record_event`, que ganha dois parâmetros opcionais e
não toca esquema (§7).

Não existe cadastro de pessoa. A identidade institucional é uma referência a um provedor externo, do
mesmo modo que a identidade do candidato é na 009.

## 2. `MembroComissao` — quem integra a comissão do Processo

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | Identidade estável |
| `processo` | FK `ProcessoSeletivo`, `PROTECT` | O contêiner, e é dele que vem o escopo institucional (D-004) |
| `identity_subject` | texto | O identificador institucional. É a chave da pessoa e nunca o nome (`FR-002`) |
| `display_label` | texto, pode ser vazio | Rótulo de leitura humana. **Não** é identidade: não é pesquisável, não entra em comparação nenhuma e não vai para a trilha (`FR-019`, D-003) |
| `funcao` | texto, escolhas `PRESIDENTE` / `MEMBRO` | Taxonomia fechada (`FR-011`) |
| `ativo` | booleano, padrão verdadeiro | Presença, não estado de workflow (D-013) |
| `criado_em` / `criado_por` | datetime / texto | |
| `inativado_em` / `inativado_por` | datetime nulo / texto vazio | Preenchidos na remoção |

**Por que `PROTECT`**: apagar um Processo com comissão apagaria o vínculo que a trilha de auditoria
referencia pelo `id`. O projeto já protege `Edital.processo` do mesmo jeito.

### Invariantes persistentes

```python
UniqueConstraint(
    fields=["processo", "identity_subject"],
    condition=Q(ativo=True),
    name="uq_membro_ativo_por_processo",
)
CheckConstraint(
    condition=Q(ativo=True, inativado_em__isnull=True)
      | Q(ativo=False, inativado_em__isnull=False),
    name="ck_membro_inativacao_completa",
)
```

A primeira é `FR-003` e `EC-001`: dois vínculos ativos da mesma pessoa no mesmo Processo são
recusados pelo banco, não por conferência sujeita a corrida. Ela é **parcial**, então readicionar
alguém que saiu cria linha nova e o histórico permanece.

A segunda diz no banco o que "inativo" significa: sem instante de inativação, o estado não é
alcançável.

**O escopo institucional não é coluna.** Ele vem de `processo.institution_scope`, e toda consulta
filtra por ele — como a `Inscricao` faz com o Edital (D-004). Duplicá-lo criaria a possibilidade de
divergir do contêiner.

## 3. `AlocacaoEtapa` — quem atua em qual Etapa

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | Identidade estável |
| `membro` | FK `MembroComissao`, `PROTECT`, `related_name="alocacoes"` | A alocação existe **através** do vínculo, nunca ao lado dele (`FR-034`) |
| `edital` | FK `Edital`, `PROTECT` | Referência real: o Edital existe como linha e não é recriado |
| `etapa_id` | UUID | A identidade da Etapa **no conteúdo publicado**. Não é chave estrangeira (D-002) |
| `ativo` | booleano, padrão verdadeiro | |
| `criado_em` / `criado_por` | datetime / texto | |
| `inativado_em` / `inativado_por` | datetime nulo / texto vazio | |

### Invariantes persistentes

```python
UniqueConstraint(
    fields=["membro", "edital", "etapa_id"],
    condition=Q(ativo=True),
    name="uq_alocacao_ativa_por_membro_e_etapa",
)
CheckConstraint(  # simétrica à do membro
    condition=Q(ativo=True, inativado_em__isnull=True)
      | Q(ativo=False, inativado_em__isnull=False),
    name="ck_alocacao_inativacao_completa",
)
```

### O que o banco **não** garante, e por quê

Três invariantes ficam no comando, e é decisão registrada, não omissão:

| Invariante | Por que não é constraint |
|---|---|
| `etapa_id` existe na Versão Consolidada vigente | A Etapa vive num JSON versionado, não numa tabela. Uma FK designaria a linha de elaboração — que pode não existir para Etapa criada por Retificação (D-002) |
| `edital.processo == membro.processo` (`FR-004`) | Exigiria desnormalizar o Processo na alocação. O comando percorre `etapa → edital → processo` numa consulta, com o Edital já carregado |
| Comissão tem presidente ativo quando há alocação (`FR-029`, `FR-030`) | Invariante entre linhas de duas tabelas. Verificado sob `select_for_update` no Processo (D-016) |

A integridade referencial que a Constituição exige é preservada — no comando, verificada a cada
operação **e a cada acesso**, e não só na escrita. É o mesmo desenho de `Inscricao.profile_id`.

## 4. O resolvedor de Etapas — a fonte única

```python
def etapas_vigentes(edital, *, at=None) -> dict[UUID, dict]:
    """As Etapas do conteúdo vigente, por identidade. A única leitura de Etapa da 011."""
    versao = effective_version(edital_id=edital.id, at=at)   # publicacoes/application/selectors.py:26
    return {UUID(e["id"]): e for e in versao.content.get("stages", [])}
```

Chamam esta função, e nada mais: criar alocação, listar a organização administrativa, montar
`Minhas Etapas` e autorizar o acesso a uma atribuição. É o que torna `SC-021` verdadeiro por
construção — uma Etapa alocável é exatamente uma Etapa que aparecerá para quem foi alocado.

`effective_version` levanta `no_effective_version` (404) quando o Edital nunca foi publicado: é
assim que `FR-032` e `EC-014` são atendidos sem consultar `Edital.status` no domínio.

**Alocação órfã é derivada, nunca persistida** (`FR-047`, `EC-011`):

```text
alocacao.ativo and alocacao.etapa_id not in etapas_vigentes(alocacao.edital)
```

Sem campo, sem sincronizador, sem cópia da Etapa. Alterar nome, peso ou nota mínima preservando o
`id` não produz órfã.

## 5. As duas perguntas de autorização

```python
def pode_gerir_comissao(ator, processo) -> Base | None:
    """Devolve a base usada — para a trilha — ou None."""

def pode_atuar_na_etapa(ator, edital, etapa_id) -> bool:
    """Vínculo ativo no Processo do Edital + alocação ativa para esta Etapa + Etapa vigente."""
```

`pode_gerir_comissao` responde por **uma de duas bases**, cada uma suficiente sozinha (`FR-016`,
D-011): a permissão sistêmica `comissao:gerir`, ou vínculo ativo como `PRESIDENTE` daquele Processo.
Devolve qual delas autorizou, porque é isso que a trilha registra.

`pode_atuar_na_etapa` **não** consulta função nem permissão: presidência não concede atuação, e
privilégio administrativo não injeta Etapa em `Minhas Etapas` (`FR-012`, D-006). As duas portas são
essas duas funções, e nenhuma view decide por conta própria.

## 6. Transação e ordem das operações

Todo comando mutável desta feature segue a mesma ordem, e a ordem é a regra (D-016):

```text
command_context()                      # transação
  ↓
ProcessoSeletivo.objects.select_for_update().get(...)    # bloqueia o contêiner
  ↓
pode_gerir_comissao(ator, processo)    # reavalia a base DEPOIS do bloqueio
  ↓
verifica invariantes que leem várias linhas (presidência)
  ↓
grava, e audita com a base que autorizou
```

**A reavaliação depois do bloqueio não é redundante.** A base contextual é dado mutável desta mesma
feature: entre a verificação da view e a gravação, outro gestor pode ter rebaixado o presidente, e
ele executaria a alteração com autorização que já não existe.

**Remover membro inativa as alocações dele na mesma transação.** Alocação ativa sob membro inativo é
relação contraditória, deixaria o acesso sobrevivendo à remoção por uma janela e atrapalharia a
própria regra do último presidente, que pergunta se há alocação ativa na comissão (`FR-025`,
`EC-003`).

## 7. Estados

Não há máquina de estados. `MembroComissao` e `AlocacaoEtapa` têm **presença**, não ciclo de vida:
existem ativos, deixam de existir ativos, e a linha permanece para a trilha. A Constituição pede
estados explícitos para workflow — inventar `status` e `revision` aqui seria deixar a persistência
determinar o domínio, que é o oposto do que ela quer (D-008, D-013).

A transição possível é uma só, e é irreversível na mesma linha:

```text
ativo=True  ──remover──▶  ativo=False   (readicionar cria linha nova)
```

## 8. A adaptação de `record_event`

```python
_UNSET = object()

def record_event(*, actor, permission, operation, aggregate, now, correlation_id,
                 reason="", previous_state="", previous_revision=None, idempotency_key="",
                 new_state=_UNSET, new_revision=_UNSET):
    ...
    new_state=aggregate.status if new_state is _UNSET else new_state,
    new_revision=aggregate.revision if new_revision is _UNSET else new_revision,
```

Dois parâmetros opcionais; quem já chama não muda. É a menor adaptação que evita dar estado e
revisão a agregados que não os têm (D-014).

**A sentinela não é preciosismo.** `None` é valor legítimo — `new_revision` é coluna anulável — e
usá-lo também como marcador de "leia do agregado" tornaria impossível gravar revisão nula de
propósito: a chamada cairia em `aggregate.revision`, que `MembroComissao` não tem, e o defeito
apareceria como `AttributeError`. Os comandos desta feature passam `new_state=""` e
`new_revision=None` explicitamente.

### O que cada evento grava

| Operação | `aggregate` | `permission` | `reason` |
|---|---|---|---|
| `COMISSAO_INCLUIR_MEMBRO` | `MembroComissao` | base usada | identificador da pessoa e função |
| `COMISSAO_ALTERAR_FUNCAO` | `MembroComissao` | base usada | função anterior → nova |
| `COMISSAO_REMOVER_MEMBRO` | `MembroComissao` | base usada | identificador da pessoa |
| `ALOCACAO_INCLUIR` | `AlocacaoEtapa` | base usada | Edital, Etapa e pessoa |
| `ALOCACAO_REMOVER` | `AlocacaoEtapa` | base usada | Edital, Etapa e pessoa |

`permission` recebe `comissao:gerir` ou `comissao:presidir` (`FR-016`). **Só a primeira existe em
`PAPEIS`**; a segunda é rótulo de trilha, e acrescentá-la a um papel desfaria D-011.

`institution_scope` e `actor_subject` vêm do ator, como em todo evento. O `display_label` nunca é
gravado: não é identidade (`FR-075`).

### A consulta, e a tela

```python
def trilha_da_comissao(*, actor, processo, cursor=None, limit=LIMITE_PADRAO):
    """Tudo que aconteceu com a comissão deste Processo, membros e alocações na mesma linha."""
```

Reúne os identificadores dos membros do Processo e de suas alocações e chama o `consultar` existente
por conjunto de agregados — o mesmo caminho de `trilha_do_edital` (`auditoria/selectors.py:64`),
sem consulta nova.

Ela é servida por `/gestao/processos/<uuid:processo_id>/auditoria`, sob `auditoria:consultar`,
reusando `interface/auditoria.html`. Sem essa tela a auditoria da 011 só seria verificável por
consulta ao banco, e o princípio VI da Constituição não a consideraria entregue (D-018).

## 9. Permissão

Uma entrada nova no papel `gestor` de `interface/identidade.py`:

```python
"gestor": ("Gestor", [..., "comissao:gerir"]),
```

Nada mais. Nenhum papel novo, nenhum grupo, nenhuma permissão por Processo ou por Etapa (`P-003`).
