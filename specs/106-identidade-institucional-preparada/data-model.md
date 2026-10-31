# Data Model: Identidade institucional preparada

Três tabelas novas no app `seguranca`, append-only nas duas camadas (gatilho e privilégio ausente),
e dois gatilhos sobre a `auth_user`. Nenhuma tabela existente muda de esquema.

## Pessoa — `auth_user` (do Django, sem coluna nova)

| Campo | Uso |
|---|---|
| `id` | chave estrangeira dos vínculos e das identidades externas |
| `username` | **o identificador interno estável**, `pessoa-<uuid4>` (D-002). Gatilho `pessoa_identificador_imutavel` recusa mudá-lo |
| `first_name`, `email` | nome e e-mail do provedor, atualizados a cada entrada; o nome, truncado em 150 |
| `is_active` | falso derruba a sessão na requisição seguinte (FR-3021) |
| `password` | sempre inutilizável |
| `is_superuser`, `is_staff`, `groups`, `user_permissions` | **ignorados** (D-008) |

Gatilho `pessoa_nao_se_exclui`: recusa `DELETE`.

## `seguranca_identidadeexterna`

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | agregado dos eventos de sessão (D-010) |
| `pessoa` | FK `auth_user`, `PROTECT` | |
| `provedor` | texto 64 | o `nome` do adaptador |
| `identificador` | texto 255 | o que o provedor diz ser estável |
| `associada_em` | instante | |

Únicos: `(provedor, identificador)`; `(pessoa, provedor)`. Gatilho `identidade_externa_append_only`.

## `seguranca_vinculo`

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | agregado de `ACESSO_*` |
| `pessoa` | FK `auth_user`, `PROTECT` | |
| `escopo` | texto 100 | código de unidade registrada e ativa, ou `institucional` (D-011) |
| `papel` | texto 64 | chave do `PAPEIS`, de `PAPEIS_DE_ACESSO` ou de `PAPEIS_INSTITUCIONAIS` |
| `concedido_em` | instante | |
| `concedido_por` | texto 255 | `subject` de quem concedeu, ou `implantacao` |
| `motivo` | texto | não vazio |

Índice `(pessoa, escopo)`. Gatilho `vinculo_append_only`. **Vigente** = sem revogação.

## `seguranca_revogacaodevinculo`

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | |
| `vinculo` | OneToOne `seguranca_vinculo`, `PROTECT` | uma por vínculo: a segunda é recusada pelo banco |
| `revogado_em` | instante | |
| `revogado_por` | texto 255 | |
| `motivo` | texto | não vazio |

Gatilho `revogacao_de_vinculo_append_only`.

## Sessão (chave `interface_identidade`)

| Origem | Conteúdo |
|---|---|
| `demonstracao` | `{subject, escopo, papeis, origem}` — **como hoje** |
| `institucional` | `{origem, unidade, identidade_externa}`, mais as chaves do `login()` do Django; **sem papéis** |

## Trilha

| Operação | Agregado | Permissão | Escopo |
|---|---|---|---|
| `ENTRADA`, `SAIDA`, `TROCA_DE_UNIDADE` | `IdentidadeExterna` | `sessao:institucional` | a unidade ativa (o institucional, se não há unidade) |
| `ACESSO_CONCEDER`, `ACESSO_REVOGAR` | `Vinculo` | `acesso:gerir` ou `acesso:administrar` | o do ator |
| `ACESSO_CONCEDER` pelo comando | `Vinculo` | `implantacao` | `institucional`, ator `implantacao` |

## Contagem

`TABELAS_APPEND_ONLY` passa de 41 a **44**.
