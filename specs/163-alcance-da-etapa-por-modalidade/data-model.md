# Data Model: O alcance da Etapa por Modalidade

## EtapaAvaliacao (alterada)

| Campo | Tipo | Regra |
|---|---|---|
| `alcance` | `JSONField`, anulável | `NULL` = todas as inscrições. Lista de textos não vazia, sem repetição, cada um com até 100 caracteres (o tamanho de `ModalidadeConcorrencia.code`) |

**Constraint nova**: `ck_etapa_alcance_nao_vazio` — `Q(alcance__isnull=True) | ~Q(alcance=[])`.

**Migration**: `editais/0029_alcance_da_etapa`, aditiva, sem preenchimento: toda linha existente
fica `NULL`, que é o que ela significava.

**Não é append-only.** Muda até publicar e depois só por Retificação, como o resto da Etapa. Não
entra em `TABELAS_APPEND_ONLY`, e o `M` da preparação do banco continua 59.

## Conteúdo publicado: `stages[]` (degrau 22)

```text
stages[]:
  ...campos de hoje...
  modalityCodes: null | [string, ...]   # ordenada, sem repetição, não vazia
```

- Elevação: `DEGRAUS[22] = {"modalityCodes": None}`.
- Mutabilidade: `("stages", "modalityCodes"): retificavel()`.

## Relações lidas, e não gravadas

```text
EtapaAvaliacao.alcance (códigos)
        │  por código, em cada Perfil do conteúdo publicado
        ▼
profiles[].competitionModalities[] {id, code, name}
        │  identidade
        ▼
Inscricao.modality_id  (NULL = ampla, nunca alcançada por Etapa restrita)
```

## Estado novo na partição da Etapa

`FORA_DO_ALCANCE` (`"fora-do-alcance"`), em `resultados/application/prontidao.py`, ao lado de
`FORA_DO_CORTE`. Precedência: a inscrição fora do alcance ocupa este estado antes de qualquer outro,
porque nenhuma outra regra da Etapa se aplica a ela.

| Estado | Conta como participante? |
|---|---|
| `fora-do-alcance` | não |
| `fora-do-corte` | não |
| `eliminada-antes` | não |
| `aguardando-anterior` | sim |
| `pronta`, não consolidável, `consolidada` | sim |
