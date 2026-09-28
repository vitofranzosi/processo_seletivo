# Data Model — 049

**Nenhuma tabela, nenhuma coluna, nenhuma migration.** Tudo abaixo é leitura derivada dos atos que já
existem, e nada é gravado fora dos comandos de hoje.

## Leituras

### Recorte do marco

`(lista_id, rótulo)` pela derivação única (`editais/domain/recortes.py`, `recortes_do_perfil`), na
ordem dela: a ampla primeiro. `lista_id` nulo é a ampla (`FR-812`).

### Estado de uma operação num recorte (`FR-811`)

| Estado | Ordem | Corte | Apuração | Publicação |
|---|---|---|---|---|
| `feito` | ato vigente, não obsoleto | geração vigente, não obsoleta | apuração vigente, sem causa de obsolescência | publicação vigente **do ato vigente**; diz a natureza |
| `obsoleto` | `estado_do_marco(...)["obsoleto"]` | `estado_do_corte(...)["obsoleto"]` | `causas_de_obsolescencia(apuração)` não vazia | `divulgacao_do_ato(...)["defasadas"]`: o público lê um ato anterior |
| `falta` | sem ato vigente | sem geração vigente | sem apuração vigente | ato vigente nunca divulgado |
| `nao_se_aplica` | — | marco sem `cutRule` | recorte sem linha no quadro e sem apuração | sem ato vigente não há o que publicar: a célula diz *"falta a ordem"* e conta como falta |

Na tela do marco o estado é completo; no resumo da página do Edital é só presença (`R-6`).
*Ninguém concorreu* é nota da célula da ordem, e não estado: a ordem vazia está `feito`.

### Alcance de um gesto (`FR-816`, `FR-818`)

Um item por recorte do marco:

| Campo | Significado |
|---|---|
| `lista_id`, `rotulo` | o recorte |
| `situacao` | `praticar` · `fora` · `impedido` |
| `razao` | por que está fora ou impedido — a frase do domínio, quando é recusa dele |
| `resumo` | o que será praticado: posições e sem posição (ordem); alcançados pela faixa (corte); vagas publicadas e ordem lida (apuração); cabeçalho, posições e avisos (publicação) |
| `assinatura` | só em `praticar`; é o que a confirmação devolve (`R-3`, `R-4`) |

Regras: `fora` quando o recorte já tem o ato (vigente, obsoleto ou não); `impedido` quando o domínio
recusa agora (cálculo, publicabilidade, falta de quadro, falta de ordem); `praticar` nos demais.

### Desfecho de um gesto (`FR-824`)

Um item por recorte **do alcance confirmado**: `feito` com o caminho para o ato, ou `recusado` com a
razão. Vive na sessão até ser mostrado (`R-10`).

### Rastro do gesto (`FR-825`)

`correlation_id = "gesto-<chave>"` em cada `RegistroAuditoria` dos N atos. A chave de idempotência de
cada recorte é `marco:<chave>:<operação>:<recorte>` (`R-5`).
