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
encontraria — FR-067.

## 2. O GET da prévia

Compõe o conteúdo que **seria** publicado, pela mesma função que o POST usará, e não grava nada
(FR-032, FR-034).

Devolve ao template:

| Chave | Conteúdo |
|---|---|
| `publicabilidade` | O retorno de `estado_do_marco` classificado em informação / aviso / impedimento (FR-005) |
| `conteudo` | A projeção composta, já com rótulos resolvidos |
| `confirmacao` | `canonical_sha256(conteudo)` — o que o POST devolverá |
| `naturezas` | `PRELIMINAR`, `DEFINITIVA`; a segunda só quando já existe publicação no marco |
| `autoridades` | O catálogo de `publicacoes/domain/autoridades.py` |
| `sucede` | A publicação vigente do marco, quando existir |

**Havendo impedimento**, a prévia mostra a recusa nomeada e **não** oferece o botão. Não existe
publicar mediante confirmação adicional (D-001).

## 3. O POST

**Campos**

| Campo | Obrigatório | Nota |
|---|---|---|
| `natureza` | sim | Um dos valores oferecidos |
| `autoridade` | sim | A chave do catálogo; o identificador nunca é digitado (FR-028) |
| `confirmacao_da_previa` | sim | A assinatura do conteúdo lido (T-005) |
| `idempotency_key` | sim | Gerada na prévia, no padrão da casa |

**Ordem de execução**

```text
require_permission(actor, "resultado:publicar")     # fora da transação
  ↓
transação
  ↓
reserve(operation="resultado:publicar:<ato_id>")    # repetido → desfecho anterior
  ↓
publicabilidade                                     # três recusas nomeadas
  ↓
compor conteúdo  →  confirmacao_da_previa confere?  # 409 se não
  ↓
gravar PublicacaoResultado (+ documento, da F4 em diante)
  ↓
auditar(...)  →  finish(...)
```

`require_permission` fora da transação e `reserve` antes de executar seguem
`processos/application/commands.py`, e **não** `comando_de_comissao` — a base aqui é capacidade, não
vínculo contextual, e não muda sob os pés (T-006).

## 4. Recusas

| Código | HTTP | Quando |
|---|---|---|
| `forbidden` | 403 | Sem `resultado:publicar` — inclusive quem emitiu o ato (FR-025) |
| `not_found` | 404 | Ato fora do escopo institucional do ator, ou inexistente |
| `publication_act_superseded` | 409 | O ato foi sucedido (FR-004) |
| `publication_act_stale` | 422 | A regra ou o universo mudaram desde a emissão (FR-004) |
| `publication_milestone_removed` | 422 | O marco não existe na norma vigente (FR-004) |
| `publication_preview_stale` | 409 | O conteúdo mudou entre a prévia e a confirmação (FR-030) |
| `publication_authority_required` | 422 | Autoridade signatária ausente ou fora do catálogo |

Cada mensagem nomeia o caminho: as três de obsolescência apontam para emitir o ato sucessor na 015
(FR-006).

## 5. Auditoria

`auditar(actor=…, permissao="resultado:publicar", operation="RESULTADO_PUBLICAR",
aggregate=<publicacao>, now=…, correlation_id=…)`, com a trilha existente
(`avaliacoes/application/trilha.py:28`). Sem `com_ato_administrativo`: publicar não exige motivo — a
sucessão já carrega o dela no ato de origem (FR-064, FR-065).
