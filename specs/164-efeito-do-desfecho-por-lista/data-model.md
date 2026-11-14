# Data Model: O efeito do desfecho da Etapa por lista

## EtapaAvaliacao (alterada)

| Campo | Tipo | Regra |
|---|---|---|
| `efeito_desfavoravel` | `CharField(20)`, `choices`, `default=""` | `""` = não declarado; `RETIRA_DA_RESERVA`; `ELIMINA` |
| `efeito_da_ausencia` | `CharField(20)`, `choices`, `default=""` | `""` = o mesmo efeito; `RETIRA_DA_RESERVA`; `ELIMINA` |

**Constraints novas**:

- `ck_etapa_efeito_desfavoravel`: o valor é `""`, `RETIRA_DA_RESERVA` ou `ELIMINA`;
- `ck_etapa_efeito_da_ausencia`: o valor é `""`, `RETIRA_DA_RESERVA` ou `ELIMINA`.

**Migration**: `editais/0030_efeito_do_desfecho`, aditiva, sem preenchimento. Não é append-only.

A coerência com o alcance e com o caráter eliminatório **não** é constraint. Ela é achado de
publicação (`efeito_sem_reserva`, FR-7002): o rascunho pode estar no meio da composição.

## Conteúdo publicado: `stages[]` (degrau 23)

```text
stages[]:
  ...campos de hoje, inclusive modalityCodes (degrau 22, da 163)...
  unfavorableOutcomeEffect: null | "RESERVE_REMOVAL" | "ELIMINATION"
  absenceEffect:            null | "RESERVE_REMOVAL" | "ELIMINATION"   # null = o mesmo efeito
```

- **Elevação**: `DEGRAUS[23] = {"unfavorableOutcomeEffect": None, "absenceEffect": None}`.
- **Mutabilidade**: `("stages", "unfavorableOutcomeEffect")` e `("stages", "absenceEffect")` são
  `retificavel()`, com a recusa da FR-7020 no ato.
- **Publicação**: grava o valor explícito só na Etapa com `modalityCodes` não nulo e
  `eliminatory: true`. Com o rascunho em `""`, grava `RESERVE_REMOVAL` (FR-7001). Nas demais Etapas,
  grava `null`.

### Leitura (`resultados/domain/efeito.py`)

| Etapa | `unfavorableOutcomeEffect` | Efeito do desfavorável |
|---|---|---|
| alcança todas, ou não eliminatória | qualquer | nenhum: a regra de hoje (`ELIMINADA` se eliminatória) |
| restrita e eliminatória | `null` (acervo, antes do degrau 23) | `ELIMINA` (D-002) |
| restrita e eliminatória | explícito | o explícito |

O efeito da ausência é o `absenceEffect` explícito ou, com `null`, o do desfavorável.

## ResultadoEtapa (alterado)

| Mudança | Detalhe |
|---|---|
| `Consequencia.RETIRADA_DA_RESERVA` | `"RETIRADA_DA_RESERVA"`, terceira consequência |
| `ck_resultado_consequencia` | `consequencia IN ('HABILITADA', 'ELIMINADA', 'RETIRADA_DA_RESERVA')` |

**Migration**: `resultados/0007_retirada_da_reserva`. Ela só troca a constraint. As triggers
append-only e a de coerência com a fonte não leem o valor, e por isso não mudam.

**Gravidade**: `HABILITADA` (0) < `RETIRADA_DA_RESERVA` (1) < `ELIMINADA` (2). É lida pela vedação de
piora (`recursos/domain/pejus.py`) e pelos painéis.

## DecisaoRecurso (alterada)

`ck_decisao_consequencia` passa a admitir `""`, `HABILITADA`, `ELIMINADA` e `RETIRADA_DA_RESERVA`.
**Migration**: `recursos/0004_retirada_da_reserva`.

## PosicaoNaOrdem e SituacaoDivulgada

Sem migration. As duas guardam `consequencia` como texto, sem `choices` (`max_length=20`), e o valor
novo, com 19 caracteres, cabe.

## O horizonte (derivado, sem coluna)

```text
horizonte(marco) =
    Etapa governada pelo corte do marco      se o corte governa uma
    última Etapa enumerada pelo marco        se não há corte, ou o corte declara não governar

a retirada na Etapa E alcança a lista reservada do marco M quando:
    ordem do marco:                         order(E) <= order(última enumerada)
    participação na Etapa G:                order(E) <  order(G)
    ocupação, fila, situação da vaga,
    convocados:                             order(E) <  order(G), ou <= order(última enumerada)
    relação do sorteio:                     order(E) <  order(Etapa de habilitação)
```
