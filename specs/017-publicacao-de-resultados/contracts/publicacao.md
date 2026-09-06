# Contrato — o comando de publicar

Canal HTML institucional de `interface`. **Nenhuma rota de API nova**, e o `openapi.yaml` da 001 não
muda: nada aqui é contrato de API.

## 1. Rotas

| Rota | Método | View | Autorização |
|---|---|---|---|
| `editais/<edital_id>/marcos/<marco_id>/atos/<ato_id>/publicar` | GET | `previa_de_publicacao` | `resultado:publicar` |
| `editais/<edital_id>/marcos/<marco_id>/atos/<ato_id>/publicar` | POST | `publicar_resultado` | `resultado:publicar` |
| `editais/<edital_id>/marcos/<marco_id>/publicacoes` | GET | `publicacoes_do_marco` | `resultado:publicar` **ou** `auditoria:consultar` |

A rota pende do ato pelo mesmo motivo que as da 015 pendem do marco: é dali que ela é alcançada, e é
o ato que a autorização qualifica (`interface/urls.py:172-187`). Consultar o histórico é de dois;
publicar é de um.

**A ação é oferecida na tela do ato** (`views.ato_de_ordenacao`), condicionada à capacidade, no
padrão de `_navegacao` (`interface/acoes.py:65-78`). Sem isso a tela existiria e ninguém a
encontraria — FR-069.

## 2. O GET da prévia

Compõe a projeção que **seria** publicada, pela mesma função que o POST usará, e não grava nada
(FR-035, FR-036).

| Chave | Conteúdo |
|---|---|
| `publicabilidade` | O retorno de `estado_do_marco` classificado em informação / aviso / impedimento (FR-005) |
| `projecao` | As posições compostas, com rótulos resolvidos |
| `confirmacao` | `canonical_sha256({ato_id, publicacao_anterior_id, projecao})` (T-005) |
| `naturezas` | `PRELIMINAR` e `DEFINITIVA`, com a segunda ausente quando o predecessor já é definitivo |
| `autoridades` | O catálogo de `publicacoes/domain/autoridades.py` |
| `sucede` | A publicação vigente do marco, quando existir |

**As duas naturezas são oferecidas desde a primeira publicação.** Um certame pode divulgar
diretamente o resultado definitivo, e condicionar `DEFINITIVA` à existência de uma preliminar
inventaria uma etapa que o Edital não declarou. O que a prévia retira é a `PRELIMINAR` depois de uma
definitiva — a ordem entre naturezas tem sentido único (D-007).

**Havendo impedimento**, a prévia mostra a recusa nomeada e **não** oferece o botão. Não existe
publicar mediante confirmação adicional (D-001).

## 3. O POST

**Campos**

| Campo | Obrigatório | Nota |
|---|---|---|
| `natureza` | sim | Um dos valores oferecidos; validado, não assinado |
| `autoridade` | sim | A chave do catálogo; o identificador nunca é digitado (FR-029) |
| `confirmacao_da_previa` | sim | A assinatura da projeção e da posição na cadeia (T-005) |
| `idempotency_key` | sim | Gerada na prévia, no padrão da casa |

**Ordem de execução**

```text
require_permission(actor, "resultado:publicar")          # fora da transação
  ↓
transação
  ↓
ProcessoSeletivo.objects.select_for_update()             # serializa com emitir_ordem
  ↓
reserve(operation="resultado:publicar:<ato_id>")         # repetido → desfecho anterior
  ↓
publicabilidade                                          # três recusas nomeadas
  ↓
compor projeção  →  confirmacao_da_previa confere?       # 409 se não
  ↓
gravar PublicacaoResultado + SituacaoDivulgada           # (+ documento, da F4 em diante)
  ↓
auditar(...)  →  finish(...)
```

**O bloqueio do `ProcessoSeletivo` não é ornamento.** `emitir_ordem` roda dentro de
`comando_de_comissao`, que faz `select_for_update` na linha do Processo e a mantém por toda a
transação (`comissoes/application/__init__.py:48-63`). Sem tomar a **mesma** linha, publicar e
emitir correm em paralelo: a publicação afere que o ato é vigente, a emissão grava o sucessor, e a
publicação grava a divulgação de um ato que deixou de ser vigente entre a aferição e a gravação.
Revalidar dentro da transação não resolve — a leitura é consistente com o instante em que ocorreu, e
o problema é o que acontece depois dela. Tomar a linha antes de aferir serializa os dois comandos,
e o perdedor encontra o mundo já mudado.

`require_permission` corre fora da transação, e por isso `reserve` pode vir antes de executar — é o
padrão de `processos/application/commands.py`, e não o de `comando_de_comissao`, que reserva depois
porque a base dele é contextual (T-006).

## 4. Recusas

| Código | HTTP | Quando |
|---|---|---|
| `forbidden` | 403 | Sem `resultado:publicar` — inclusive quem emitiu o ato (FR-026) |
| `not_found` | 404 | Ato fora do escopo institucional do ator, ou inexistente |
| `publication_act_superseded` | 409 | O ato foi sucedido (FR-004) |
| `publication_act_stale` | 422 | A regra ou o universo mudaram desde a emissão (FR-004) |
| `publication_milestone_removed` | 422 | O marco não existe na norma vigente (FR-004) |
| `publication_preview_stale` | 409 | A projeção ou a cadeia mudaram entre a prévia e a confirmação |
| `publication_already_exists` | 409 | Este ato já foi publicado nesta natureza (FR-039) |
| `publication_nature_regresses` | 422 | Preliminar não sucede definitiva (D-007) |
| `publication_authority_required` | 422 | Autoridade signatária ausente ou fora do catálogo |

Cada mensagem nomeia o caminho: as três de obsolescência apontam para emitir o ato sucessor na 015
(FR-006).

`publication_already_exists` tem cobertura dupla e deliberada — a idempotência responde ao **mesmo**
pedido repetido, e a constraint `uq_publicacao_por_ato_natureza` responde a **dois pedidos
distintos** sobre o mesmo ato, que é o caso das duas abas com chaves diferentes.

## 5. Auditoria

`auditar(actor=…, permissao="resultado:publicar", operation="RESULTADO_PUBLICAR",
aggregate=<publicacao>, now=…, correlation_id=…)`, com a trilha existente
(`avaliacoes/application/trilha.py:28`). Sem `com_ato_administrativo`: publicar não exige motivo — a
sucessão já carrega o dela no ato de origem (FR-066, FR-067).
