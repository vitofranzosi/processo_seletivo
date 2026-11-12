# Data Model: O desfecho da convocação comunicado ao candidato (156)

Duas tabelas novas na app `convocacao`, uma coluna e uma origem na app `avisos`. Nenhuma tabela
existente perde dado, e nenhuma linha gravada muda.

## `convocacao.PedidoDeDesistencia` *(nova, append-only)*

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | chave |
| `chamada` | FK `Convocacao` (`PROTECT`) | a convocação **raiz** da chamada (D-009) |
| `inscricao` | FK `Inscricao` (`PROTECT`) | a do titular |
| `protocolo` | texto, 12 | `DES-` + 8 hexadecimais; `UNIQUE` |
| `solicitado_por` | texto | `subject` da identidade autenticada no portal (R-007) |
| `solicitado_em` | instante | do comando |
| `ciencia` | booleano | sempre verdadeiro; `CHECK (ciencia)` — sem a ciência não há linha (FR-6419) |

Índices: `(chamada, solicitado_em)`.

Sem campo de motivo nem texto livre (D-007). Sem endereço de e-mail.

## `convocacao.CancelamentoDoPedidoDeDesistencia` *(nova, append-only)*

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | chave |
| `pedido` | OneToOne `PedidoDeDesistencia` (`PROTECT`) | um cancelamento por pedido |
| `cancelado_por` | texto | `subject` da identidade |
| `cancelado_em` | instante | do comando; posterior ao pedido |

## O estado do pedido *(derivado, não gravado)*

```text
cancelado                    se há CancelamentoDoPedidoDeDesistencia
homologado                   senão, se o desfecho vigente da chamada é DESISTENCIA_EXPRESSA
encerrado por outro desfecho senão, se a chamada tem desfecho vigente de outra espécie
pendente                     senão
```

Invariantes, garantidas pelo comando sob a trava (R-008):

- no máximo um pedido **pendente** por chamada;
- nenhum pedido é gravado para chamada com desfecho, nem com o Processo em estado final, nem para
  convocação fora do portal (`visivel_ao_candidato`);
- nenhum cancelamento é gravado depois do desfecho.

Leitura: `convocacao.application.desistencia.pedidos_pendentes(chamadas)` em consulta única, para o
cartão, o índice, o lote, o "O que fazer agora" e a advertência do encerramento.

## `avisos.DestinatarioDoAviso.desfecho` *(coluna nova, anulável)*

| Campo | Tipo | Regra |
|---|---|---|
| `desfecho` | FK `convocacao.DesfechoDaConvocacao` (`PROTECT`), nula | preenchida só na origem `DESFECHO` |

A tabela continua append-only; a coluna nasce nula para as linhas existentes.

## `avisos.Aviso.origem = DESFECHO` *(origem nova)*

- `ck_aviso_origem_conhecida` passa a admitir `DESFECHO`.
- `ck_aviso_ato_da_origem` ganha o ramo `DESFECHO`: natureza e referência da publicação vazias, como
  a pendência.
- `motivo = PRIMEIRO_AVISO`; sem reenvio pela tela da `066` (como a pendência).
- `assunto` e `corpo` congelados no aviso, pelo texto de `avisos/domain/desfecho.py`.
- `perfil_id`, `marco_id` e `lista_id` vêm da convocação.

## Migrations

| App | Migration | O que faz |
|---|---|---|
| `convocacao` | `0008_pedido_de_desistencia` | as duas tabelas, os gatilhos `BEFORE UPDATE OR DELETE` e a função de recusa, no molde da `0007` |
| `avisos` | `0003_origem_desfecho` | a coluna `desfecho` e as duas *constraints*, no molde da `0002` |

`seguranca.papeis.TABELAS_APPEND_ONLY` ganha as duas tabelas: o provisionamento passa a informar `N de
60`. Atualizam-se o guardião da contagem (`tests/seguranca/test_homologacao_preservada.py`), a tupla
de `tests/unit/convocacao/test_append_only.py`, `TRIGGERS_POR_APP` de `tests/migrations/test_migrations.py`
e as citações do número no README e no `doc/implantacao-em-producao-ubuntu.md`.

## Chaves de configuração

| Chave | Base | `development` | `test` | Produção |
|---|---|---|---|---|
| `AVISOS_AOS_CANDIDATOS` (existente) | `false` | `true` | `true` | herda `false` |
| `AVISOS_DE_DESFECHO` (nova) | `false` | `true` | `true` | herda `false`; liga-se só depois de PI-1 a PI-6 |
