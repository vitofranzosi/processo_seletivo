# Data Model: A distribuição coerente com a agenda e a programação de quem avalia

**O Incremento 1 não tem migration.** Tudo o que ele mostra e confere é derivado de tabelas que já
existem. O Incremento 2 tem uma migration, `avisos/0005_origem_programacao`, que acrescenta uma
origem e duas colunas a tabelas que já existem. Nenhuma tabela nova nos dois: o `M` da preparação do
banco continua **69**.

## 1. O que já existe e é lido

| Entidade | App | Campos que esta feature lê | Para quê |
|---|---|---|---|
| `MembroComissao` | `comissoes` | `identity_subject`, `display_label`, `ativo` | a pessoa (T-003) e o nome na gestão |
| `AlocacaoEtapa` | `comissoes` | `membro`, `edital`, `etapa_id`, `ativo` | quem pode atuar (autorização da Mesa) |
| `Atribuicao` | `avaliacoes` | `membro`, `edital`, `etapa_id`, `inscricao`, `ativo` | quem avalia cada inscrição |
| `AgendaDaEtapa` | `agendamento` | `edital`, `etapa_id`, `forma` | se a Etapa tem agenda |
| `Agendamento` | `agendamento` | `inscricao`, `banca`, `inicio`, `fim` | o horário antes da publicação (fonte `MONTAGEM`) |
| `HorarioPublicado` (vigente) | `agendamento` | `inscricao`, `banca`, `banca_nome`, `inicio`, `fim`, `ato` | o horário depois (fonte `PUBLICADO`) |
| `BancaDaAgenda` | `agendamento` | `nome`, `acesso` | o local ou a sala, na Programação |
| `auth.User` | Django | `username`, `email`, `first_name` | o e-mail do avaliador (Inc. 2) |
| `SuspensaoDePessoa` / `ReativacaoDePessoa` | `seguranca` | via `suspensas()` | quem não recebe (Inc. 2) |

## 2. O que é derivado, e nunca gravado

### Horário (T-002) — `HorarioMarcado`, em `agendamento/application/leitura.py`

`(etapa_id, inscricao_id) → HorarioMarcado(inicio, fim, banca_id, banca_nome, fonte, remarcado_em)`

- `fonte = PUBLICADO` quando a agenda da Etapa tem ato de publicação; senão `MONTAGEM`.
- Um por inscrição e Etapa: a `167` garante um agendamento por inscrição por agenda e um vigente por
  inscrição por agenda.

### Compromisso e conflito (T-003)

- **Compromisso** de uma pessoa: um `HorarioMarcado` de uma inscrição em que ela tem Atribuição ativa, em
  qualquer Etapa do Edital.
- **Conflito**: dois compromissos da mesma pessoa com `a.inicio < b.fim and b.inicio < a.fim`.
  Atributos: pessoa, os dois horários e bancas, as duas inscrições, `passado` (os dois já
  terminaram).

### Programação (FR-8200, FR-8211)

A lista dos compromissos de uma pessoa **numa Etapa**, só com fonte `PUBLICADO`, agrupada por dia
na zona institucional, em ordem de início; mais as Atribuições da Etapa sem horário publicado, à
parte. Cada item: início, fim, candidato (nome, protocolo), banca, acesso, `remarcado_em`, situação
da avaliação da própria pessoa.

### Coerência de uma Etapa (FR-8208)

- inscrições com horário e menos Atribuições ativas do que `avaliacoes_previstas(etapa)`;
- conflitos das pessoas alocadas à Etapa;
- por inscrição, os nomes de quem avalia (só na gestão, `D-007`).

### Resumo da programação (Inc. 2, T-017)

`sha256(canonical_json(sorted([(inscricao_id, inicio_iso, fim_iso, banca_id), ...])))`, 64
caracteres. Igual a hoje ⇔ nada mudou para aquela pessoa.

## 3. O que muda no banco (Incremento 2)

### `avisos.Aviso`

| Mudança | Detalhe |
|---|---|
| `origem` aceita `PROGRAMACAO` | `nomes.ORIGENS` e `ck_aviso_origem_conhecida` |
| `ck_aviso_ato_da_origem` | ramo `Q(origem=PROGRAMACAO, natureza="", referencia_da_publicacao="")` |
| `ck_aviso_marco_da_origem` | `PROGRAMACAO` entra na lista das que não têm marco |
| `ck_aviso_etapa_da_origem` | ramo `Q(origem=PROGRAMACAO, etapa_id__isnull=False, marco_id__isnull=True, perfil_id__isnull=True)` |

### `avisos.DestinatarioDoAviso`

| Mudança | Detalhe |
|---|---|
| `inscricao` | passa a `null=True` (continua `PROTECT`) |
| `membro` (novo) | `ForeignKey("comissoes.MembroComissao", null=True, PROTECT, related_name="avisos_de_programacao")` |
| `resumo_da_programacao` (novo) | `CharField(max_length=64, blank=True, default="")` |
| `ck_destinatario_inscricao_ou_membro` (novo) | `(inscricao NOT NULL AND membro NULL) OR (inscricao NULL AND membro NOT NULL)` |
| `ck_destinatario_resumo_so_do_membro` (novo) | `(membro NULL AND resumo = '') OR (membro NOT NULL AND resumo <> '')` |
| `uq_destinatario_membro` (novo) | `UNIQUE (aviso, membro)` |
| `ix_destinatario_membro` (novo) | `(membro)`, para "o último aviso desta pessoa nesta Etapa" |

As tentativas, os resultados e a interrupção não mudam: são do destinatário, qualquer que seja ele.

**Append-only preservado.** As duas tabelas continuam nas três camadas (`save`, gatilho, privilégio
ausente); a migration só acrescenta colunas e constraints. Linhas existentes: `membro` nulo e
`resumo` vazio, que satisfazem as constraints novas sem reescrita.

## 4. Estados derivados do avaliador (Inc. 2, FR-8228)

Decididos nesta ordem, para cada pessoa alocada com ao menos uma entrevista publicada na Etapa:

```text
suspenso            ← a pessoa institucional está suspensa
sem e-mail          ← sem pessoa institucional com o identificador, ou sem e-mail nela
com conflito        ← conflito não passado envolvendo esta Etapa
nunca avisado       ← nenhum destinatário PROGRAMACAO desta pessoa nesta Etapa
mudou               ← resumo de hoje ≠ resumo do último destinatário
na fila / avisado / não entregue   ← estado de entrega do último destinatário (066)
```

"Pronta para avisar" (a Etapa): agenda publicada e ao menos uma pessoa em "nunca avisado" ou "mudou".
