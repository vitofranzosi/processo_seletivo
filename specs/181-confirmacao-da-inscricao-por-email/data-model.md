# Modelo de dados: A confirmação da inscrição por e-mail

**Nenhuma tabela, coluna, estado ou migration.** A tentativa é um registro da trilha de auditoria que
já existe (R1 da pesquisa).

## A tentativa de confirmação — `auditoria.RegistroAuditoria`

| Campo | Valor |
|---|---|
| `operation` | `CONFIRMAR_POR_EMAIL` |
| `aggregate_type`, `aggregate_id` | `Inscricao`, o identificador da inscrição |
| `actor_subject`, `institution_scope` | o candidato titular e o escopo do Edital (`ator_do_candidato`) |
| `permission` | vazio — o candidato não tem permissão institucional |
| `occurred_at` | o instante em que o servidor respondeu |
| `previous_state`, `new_state` | vazios: a inscrição não muda |
| `detalhe` | `{"tentativa": n, "resultado": "ENVIADA" \| "NAO_ENVIADA"}` |
| `reason` | `Tentativa n da confirmação por e-mail: enviada.` (ou `não enviada.`) — sem endereço, nome, protocolo nem erro |
| `correlation_id` | o da requisição |

**Regras**

- `n` é o número de tentativas anteriores da mesma inscrição, mais um, lido sob a trava (R2).
- Uma inscrição tem no máximo uma tentativa `ENVIADA`, e nenhuma tentativa depois dela (FR-8351).
- Entre duas tentativas da mesma inscrição há ao menos um minuto (FR-8363).
- Inscrição sem endereço não tem tentativa.
- `ENVIADA` quer dizer aceita pelo servidor de correio (FR-8359).
- A "última tentativa" é a de maior `occurred_at`, com o número da tentativa como desempate.

## O que a tela lê

`confirmacao.ultima(inscricao)` → `None` (sem tentativa: a tela não diz nada) ou
`Tentativa(numero, em, enviada)`.
