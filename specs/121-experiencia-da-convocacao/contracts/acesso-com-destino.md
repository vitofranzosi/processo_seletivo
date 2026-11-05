# Contrato: o acesso com destino para a convocação

**Requisitos**: FR-3876 a FR-3881 · **Pesquisa**: R-004, R-005

## GET `/selecoes/inscricoes/<inscricao_id>/convocacao`

| Sessão | Resposta | Consulta antes da resposta |
|---|---|---|
| sem a chave da identidade (ausente, vencida, ou só com o e-mail, sem código provado) | `302` para `/selecoes/acesso?destino=<caminho pedido, com urlencode>` | nenhuma à inscrição, ao Edital ou à convocação |
| identidade titular | `200`, a convocação, como hoje, com a leitura registrada na trilha | as de hoje |
| identidade de outra pessoa, ou inscrição inexistente | a recusa de inexistente, como hoje (FR-1101 da `059`) | as de hoje |

A resposta sem sessão é **byte a byte** a mesma para identificador real, inventado e alheio, salvo o
próprio caminho no `destino`.

**Não mudam:** o POST de envio, o GET do arquivo enviado e as demais rotas do titular, que continuam
respondendo como hoje sem sessão (D-002).

## O destino, do pedido à chegada

1. `acesso` grava o `destino` na sessão depois de `url_has_allowed_host_and_scheme` (camada 1). Esse
   passo é o de hoje.
2. `_entrar` resolve o caminho do destino (camada 2) e confere o nome da rota contra a lista fechada:
   `portal:selecao`, `portal:inscrever`, `portal:convocacao` (camada 3).
3. A chegada é `reverse(<rota>, kwargs=<os da resolução>)`, mais o fragmento fixo que a rota define
   (`#resultados-titulo`, `#vaga-<perfil>`, ou nenhum para a convocação). Consulta e fragmento
   recebidos são descartados (camada 4).
4. Fora da lista, ou com falha de resolução, a chegada é `portal:inscricoes`.

A titularidade **não** é conferida aqui: ela é conferida pela própria convocação, ao abrir (`S4`).

## As telas de acesso

| `destino_e_convocacao` | Título da tela do e-mail | Frase nas duas telas |
|---|---|---|
| verdadeiro | *"Entre para ver a sua convocação"* | *"Depois do código, você vai direto para a convocação."* |
| falso | os de hoje | nenhuma nova |

`destino_e_convocacao` sai **só** de `resolve(path).view_name == "portal:convocacao"`. A
decisão não abre a inscrição e não lê o identificador, e o texto não nomeia o Edital nem a
pessoa (FR-3880).
