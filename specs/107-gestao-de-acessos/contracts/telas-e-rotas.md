# Contrato: telas e rotas da gestão de acessos

Todas sob `/gestao/`. Toda rota de acesso exige sessão institucional; sem ela, a recusa é a da
demonstração (403, `FR-3127`). Falta de capacidade é a recusa explicada (403). "Não encontrado"
(404) só para vínculo de outro escopo, ou inexistente.

## Rotas

| Método | Rota | Nome | Exige | Responde |
|---|---|---|---|---|
| GET | `sem-acesso` | `interface:sem-acesso` | sessão institucional com pessoa autenticada | a tela; sem isso, redireciona à página de acesso |
| GET | `acessos` | `interface:acessos` | `acesso:consultar` na unidade ativa | vigentes e histórico da unidade |
| GET, POST | `acessos/conceder` | `interface:acessos-conceder` | `acesso:gerir` na unidade ativa | busca (`acao=buscar`), confirmação (`acao=conferir`), gravação (`acao=confirmar`) |
| POST | `acessos/vinculos/<uuid>/revogar` | `interface:acessos-revogar` | `acesso:gerir` na unidade ativa | confirmação (`acao=conferir`), gravação (`acao=confirmar`); vínculo de outra unidade, 404 |
| GET | `administracao-de-acessos` | `interface:administracao-de-acessos` | `acesso:administrar` no institucional | administradores vigentes por unidade, e o histórico deles |
| GET, POST | `administracao-de-acessos/conceder` | `interface:administracao-de-acessos-conceder` | idem | idem a `acessos/conceder`, com a unidade escolhida |
| POST | `administracao-de-acessos/vinculos/<uuid>/revogar` | `interface:administracao-de-acessos-revogar` | idem | só vínculo de Administrador de acessos; outro, 404 |

## Campos dos envios

| Envio | Campos | Origem da unidade |
|---|---|---|
| `buscar` | `termo` | — |
| `conferir` (concessão) | `pessoa` (identificador interno, oculto), `papel`, e `unidade` no nível institucional | a ativa, no nível da unidade; o campo, no institucional, conferido contra as unidades registradas e ativas |
| `confirmar` (concessão) | os do `conferir`, mais `motivo` | idem |
| `conferir`, `confirmar` (revogação) | o vínculo, na rota; `motivo` no segundo | a do vínculo, que precisa ser a ativa (ou um Administrador de acessos, no institucional) |

## Recusas na tela

A confirmação recusada volta à própria confirmação, com a mensagem do domínio e o status dele
(422 sem motivo; 403 autoconcessão; 409 já vigente, já revogado, pessoa inativa). A gravação aceita
redireciona à tela do nível com `?feito=concedido` ou `?feito=revogado`.

## Sessão institucional

| Chave | Conteúdo |
|---|---|
| `origem`, `unidade`, `identidade_externa` | os da `106` |
| `entrada_em` | segundos desde a época, gravado na entrada; a troca de unidade não muda |
| `atividade_em` | idem, renovado a cada requisição à gestão sem `Requisicao-Automatica` |

| Configuração | Padrão fora de produção | Produção |
|---|---|---|
| `GESTAO_SESSAO_DURACAO_MAXIMA_MINUTOS` | 480 (proposta) | obrigatória com provedor |
| `GESTAO_SESSAO_INATIVIDADE_MINUTOS` | 30 (proposta) | obrigatória com provedor |

Término: evento `SAIDA` com `detalhe.motivo` em `duracao_maxima` ou `inatividade`; a sessão nova leva
`interface_sessao_encerrada` com o motivo, que a página de acesso mostra uma vez.
