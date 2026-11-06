# Data Model: o MVP de UX da Retificação (123)

**Nenhuma tabela, coluna, índice ou migration.** Tudo abaixo é estrutura em memória, calculada a cada
requisição, ou atributo de HTML. O que persiste continua sendo `Retificacao`, `AlteracaoNormativa`,
`VersaoConsolidada` e `Publicacao`, como estão.

## ConferenciaDoConteudo (domínio, `publicacoes/application/retificacoes.py`)

O resultado de `conferir_conteudo(edital, base_content, changes)` (R-001).

| Campo | Tipo | O que é |
|---|---|---|
| `content` | `dict \| None` | O conteúdo que o ato produziria; `None` se a aplicação recusou. |
| `recusa` | `DomainError \| None` | A primeira guarda que recusou, com o código, a mensagem e o status que a criação levantaria. |
| `impeditivos` | `list[ValidationFinding]` | Os achados impeditivos de `validate_for_publication` com o ato de Retificação. Vazia quando há `recusa`. |

**Invariante.** Para o mesmo `(edital, base_content, changes)` e o mesmo instante, `_apply_declared_changes`
levanta a `recusa`, ou, sem ela, uma recusa cuja mensagem é a junção das `impeditivos[i].message`; e
não levanta nada por conteúdo quando as duas estão vazias.

## Proposta (tela, `interface/views._compor_retificacao`)

| Campo | O que é |
|---|---|
| `alteracoes` | As Alterações que o ato gravaria agora: `todas` na criação; a fusão na edição (R-003). |
| `cartoes` | `set[str]` de referências de grupo (`g12`) e de linha nova (`novo-perfil-1`) — R-005; `ADD`/`REMOVE` só casam a própria entidade. |
| `novas` | Mapa identidade da entidade nova → `novo-<prefixo>-<indice>`, só desta requisição (R-006). |
| `remocoes` | Na edição, quantas remoções já declaradas e não desfeitas ficam no ato. |
| `estado` | `NAO_CONFERIDA` (GET da criação), `RECUSADA` (envio sem proposta calculada), `CONFERIDA`. |

Não é persistida. Na edição, o GET a calcula de `alteracoes_declaradas(item)`.

## Item do resumo (tela, `interface/retificacao.diferencas`)

Os campos de hoje — `grupo`, `rotulo`, `antes`, `depois` — mais:

| Campo | Exemplo | O que é |
|---|---|---|
| `cartao` | `g12`, `novo-evento-2` | A referência opaca do cartão da linha. |
| `campo` | `g12c3` ou `None` | A referência opaca do campo; `None` quando a linha fala do cartão inteiro. |

Nenhum caminho normativo (a FR-019 da `002`).

## Impeditivo na tela

| Campo | O que é |
|---|---|
| `mensagem` | `ValidationFinding.message`, ou `DomainError.detail` da guarda. Texto idêntico ao da criação. |
| `destino` | `cartao-<ref>`, `s-<secao>` ou `None` (R-004). |

## DescricaoDaVersaoBase (tela, R-009)

| Campo | O que é |
|---|---|
| `original_em` | Data de publicação da Publicação original. |
| `retificacoes` | Lista de `(numero, publicada_em)`, de `applied_publications` sem revisão, por `publication_order`; `numero = publication_order`, como no detalhe do Edital (D-006). |
| `situacao` | `VIGORA`, `FUTURA` ou `SUCEDIDA`, no instante da tela; `SUCEDIDA` inclui a versão rematerializada com o mesmo início (R-009). |
| `inicio` | `valid_from`, no fuso institucional. |

**Transições de `situacao`** (só pelo relógio e por publicação nova; nada nesta feature as provoca):

```
FUTURA ──(chega valid_from)──► VIGORA ──(outra versão passa a vigorar)──► SUCEDIDA
FUTURA ──(publicação fora de ordem rematerializa o mesmo início)─────────────► SUCEDIDA
```

## Atributos de HTML (contrato com o script)

| Onde | Atributo | Valores |
|---|---|---|
| `form#formulario-da-retificacao` | `data-conferido` | o de hoje, sem mudança (vem antes dos novos) |
| idem | `data-modo` | `edicao`, ou ausente na criação |
| idem | `data-enviado` | presente em toda resposta a POST |
| idem | `data-proposta` | `nao-conferida`, `recusada`, `conferida` |
| idem | `data-proposta-cartoes` | inteiro ≥ 0 (com `conferida`) |
| idem | `data-proposta-remocoes` | inteiro ≥ 0 (só na edição) |
| `fieldset.linha` | `data-na-proposta` | presente ou ausente |
| idem | `data-alterado` | o de hoje, posto pelo script |

O detalhe de cada tela, com os textos, está em [contracts/tela-retificar.md](contracts/tela-retificar.md).
