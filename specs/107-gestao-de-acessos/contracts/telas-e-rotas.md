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
| `GESTAO_SESSAO_DURACAO_MAXIMA_MINUTOS` | 480 (decidido em 30/10, P4) | obrigatória com provedor; a decisão é 480 |
| `GESTAO_SESSAO_INATIVIDADE_MINUTOS` | 30 (decidido em 30/10, P4) | obrigatória com provedor; a decisão é 30 |

Término: evento `SAIDA` com `detalhe.motivo` em `duracao_maxima` ou `inatividade`; a sessão nova leva
`interface_sessao_encerrada` com o motivo, que a página de acesso mostra uma vez.

## Incremento 2

| Método | Rota ou comando | Exige | Faz |
|---|---|---|---|
| POST | `administracao-de-acessos/pessoas/<identificador>/suspender` | `acesso:administrar` no institucional; não o próprio ator; não administrador institucional | confirmação (`acao=conferir`), gravação (`acao=confirmar`, com `motivo`) |
| POST | `administracao-de-acessos/pessoas/<identificador>/reativar` | idem | idem, com a lista do que volta a valer |
| comando | `suspender_pessoa --provedor --identificador --motivo` | quem implanta | a suspensão sob o ator `implantacao`, a qualquer pessoa |
| comando | `reativar_pessoa --provedor --identificador --motivo` | idem | a reativação |
| GET, POST | `administracao-de-acessos/pessoas` | `acesso:administrar` no institucional | a busca (inclusive das suspensas) e as suspensas agora |
| comando | `retirar_administracao_institucional --provedor --identificador --motivo [--sem-administracao]` | idem | a revogação do vínculo institucional; a última só com a marca |
| comando | `substituir_administracao_institucional --de-provedor --de-identificador --para-provedor --para-identificador --motivo` | idem | revogação e concessão numa transação |

Trilha: `PESSOA_SUSPENDER` e `PESSOA_REATIVAR`, com a suspensão como agregado e o escopo
`institucional`; a retirada e a substituição como `ACESSO_REVOGAR` e `ACESSO_CONCEDER`, sob a
permissão `implantacao`.
