# Modelo de dados: A data de nascimento entra no cadastro do candidato

Dois acréscimos de coluna, ambos anuláveis, sem preenchimento retroativo.

## CandidateIdentity (`identidade`)

| Campo | Tipo | Regra |
|---|---|---|
| `data_nascimento` | data, anulável | declarada pelo titular; obrigatória para o núcleo (`falta_o_nucleo`); congela quando já preenchida e o CPF congelou (R2) |

- **Migration**: `identidade/0005_data_nascimento` — `AddField`, nulo. Nenhuma linha é tocada.
- **Validação** (FR-8305, R4): data existente, ano com quatro dígitos, anterior a hoje (Brasília),
  idade até 120 anos. Sem idade mínima (FR-8306).
- **Não é chave de nada**: nenhum índice, nenhuma unicidade, nenhuma busca por ela (FR-8310).

## Inscricao (`inscricoes`)

| Campo | Tipo | Regra |
|---|---|---|
| `data_nascimento` | data, anulável | escrita uma vez, no ato do envio, com a data do cadastro naquele instante (FR-8308, R3) |

- **Migration**: `inscricoes/0009_data_nascimento` — `AddField`, nulo. O gatilho de imutabilidade da
  `0007` já recusa qualquer mudança numa enviada, coluna nova inclusive; nada a mudar nele.
- **Sem restrição de banco** que exija a data na enviada: as enviadas antes da `180` não a têm
  (FR-8304). A exigência é do comando (FR-8303).
- **Leitores**: só a conferência de identidade da gestão (FR-8312). O comprovante, a consulta, as
  publicações e a exportação **não** a leem.

## RequerimentoDeMatricula (`requerimentos`) — sem mudança de esquema

- `data_de_nascimento` já existe. Muda só o preenchimento inicial na criação (FR-8313, R6).

## Trilha (`auditoria`) — sem mudança de esquema

- Operação nova `CONFERIR_IDENTIDADE`, com permissão `inscricao:consultar`, agregado = a inscrição e
  `reason` = "Conferência de identidade da inscrição <protocolo>: <motivo>". Nunca CPF nem data
  (FR-8316). A trilha do Edital a reúne pela operação (R8).

## Contagem de migrations

`tests/migrations/test_migrations.py` conta as migrations por app: `identidade` e `inscricoes` sobem
uma cada, com um comentário que diz que foi a `180`.
