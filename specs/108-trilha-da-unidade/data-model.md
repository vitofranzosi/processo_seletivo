# Data Model: Trilha da unidade

**Nenhuma entidade nova, nenhum campo novo, nenhuma migration.** A feature lê o que já se grava.

## Lido

### RegistroAuditoria (`auditoria`, append-only)

| Campo | Uso na página |
|---|---|
| `occurred_at`, `event_id` | ordem decrescente e cursor (desempate pelo identificador) |
| `institution_scope` | o escopo: o da unidade ativa; o institucional só pela condição de `D-002` |
| `aggregate_type` | o assunto (tabela abaixo) |
| `aggregate_id` | a ligação com o aviso e a interrupção |
| `operation` | o rótulo do ato |
| `actor_subject` | quem praticou: o nome, pela tradução da `107`; "Implantação" para `implantacao` |
| `previous_state`, `new_state` | a situação, traduzida |
| `reason` | o motivo; na autoridade, o rótulo dela |
| `detalhe` | só as chaves de `D-005`: `depois.nome`, `antes`/`depois` da unidade, `pessoa` e `papel` do vínculo, as contagens da exclusão do piloto. **Nunca** `assunto` nem `corpo` |
| `correlation_id`, `idempotency_key`, `permission`, revisões | **não** mostrados |

### Os assuntos

Derivados de `aggregate_type`; não são gravados.

| Assunto (`?assunto=`) | Rótulo | Tipos | Operações |
|---|---|---|---|
| `unidade` | Unidade | `Unidade` | `REGISTRAR_UNIDADE`, `ALTERAR_UNIDADE`, `EXCLUIR_REGISTROS_DO_PILOTO` |
| `autoridades` | Autoridades | `AutoridadeHabilitada` | `CADASTRAR_AUTORIDADE`, `CORRIGIR_AUTORIDADE`, `ENCERRAR_AUTORIDADE` |
| `modelos` | Modelos de aviso | `ModeloDeAviso` | `AVISO_MODELO` |
| `avisos` | Avisos | `Aviso`, `InterrupcaoDoAviso` | `AVISO_CONFIRMAR`, `AVISO_INTERROMPER` |
| `acessos` | Acessos | `Vinculo` | `ACESSO_CONCEDER`, `ACESSO_REVOGAR` |

### O critério

```text
(institution_scope = U  E  aggregate_type ∈ tipos do assunto)
OU
(assunto inclui acessos  E  institution_scope = 'institucional'
                          E  aggregate_type = 'Vinculo'  E  detalhe.escopo = U)
```

`U` é a unidade ativa do ator, e nunca o institucional (D-003).

### Aviso, InterrupcaoDoAviso (`avisos`, append-only)

Lidos só pelos identificadores da página, com o Edital junto, para "Edital NN/AAAA" e a origem.
A interrupção tem chave inteira, e a trilha a grava como `UUID(int=pk)`; a volta é pelo `.int`
(achado registrado na spec).

### Situações traduzidas

| Gravado | Mostrado |
|---|---|
| `ATIVA`, `DESATIVADA` | Ativa, Desativada (unidade) |
| `ATIVO`, `INATIVO` | Ativo, Inativo (modelo) |
| `FUTURA`, `VIGENTE`, `ENCERRADA` | Futura, Vigente, Encerrada (autoridade) |
| `vigente`, `revogado` | Vigente, Revogado (vínculo) |
