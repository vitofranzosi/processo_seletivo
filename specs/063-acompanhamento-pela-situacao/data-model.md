# Data model — 063 · Acompanhamento pela situação do candidato

**Nenhuma migration, nenhum modelo, nenhuma coluna.** Tudo aqui é projeção de leitura, montada em
memória a partir do que a view já lê ([D-001](research.md), [D-007](research.md)).

## 1. `Situacao` — o topo da tela

Devolvida por `portal.situacao.situacao_da_inscricao(...)`.

| Campo | Tipo | O que é |
|---|---|---|
| `codigo` | texto, do conjunto fechado (§1.1) | o estado, para teste e para a classe de estilo |
| `rotulo` | texto | o que a pessoa lê em "Situação" (FR-1166, UX-155) |
| `provisoria` | booleano | `True` em "Aguardando chamada", "Aguardando resultado definitivo", "Convocado" e "Inscrição enviada"; a tela diz "ainda não", e não "não" (FR-1170) |
| `porque` | lista de `Linha` (§1.2) | os atos de origem, um por linha (FR-1173, FR-1174) |
| `o_que_fazer` | `Acao` (§1.3) | ação, prazo, consequência, canal |

### 1.1 Conjunto fechado, em ordem de precedência ([D-002](research.md))

| `codigo` | Quando | `rotulo` |
|---|---|---|
| `DESFECHO_<ESPECIE>` | convocação vigente com desfecho vigente | tabela da FR-1172 ("Vaga aceita", "Convocação não atendida", …) |
| `CONVOCADO` | convocação vigente sem desfecho | Convocado |
| `ELIMINADO` | algum Resultado de Etapa visível com `habilitada = False` | Eliminado |
| `AGUARDANDO_CHAMADA` | alguma situação divulgada *classificada* em publicação definitiva | Aguardando chamada |
| `AGUARDANDO_DEFINITIVO` | situações *classificadas*, todas em publicação preliminar | Aguardando resultado definitivo |
| `NAO_CLASSIFICADO` | situações divulgadas, todas *sem posição* | Não classificado |
| `INSCRICAO_ENVIADA` | nenhuma das anteriores | Inscrição enviada |

**Entradas que a precedência não lê, por decisão** (Clarifications): a apuração de ocupação (L-1) e
o corte (L-2).

### 1.2 `Linha` do porquê

| Campo | Exemplo |
|---|---|
| `texto` | "Ampla concorrência: 8º lugar no resultado definitivo de Classificação final — Técnico de Laboratório, publicado em 23/09/2026." |
| `link` (opcional) | a publicação vigente, a convocação, a peça de recurso |

Quando há mais de uma lista, o porquê acrescenta uma linha fixa, factual: "Você concorre em mais de
uma lista, e cada lista tem a sua classificação." (FR-1174). Recurso em análise acrescenta uma linha
com o protocolo e o link para a peça (caso-limite da spec).

### 1.3 `Acao`

| Campo | Tipo | Regra |
|---|---|---|
| `principal` | texto | a ação, ou "Nada por enquanto." (FR-1178) |
| `link` | URL opcional | Requerimento (preencher/conferir) ou convocação |
| `prazo` | instante opcional | o vencimento da convocação (FR-1176) |
| `aviso_de_prazo` | texto opcional | "o prazo ainda não começou…" ou "o prazo informado já passou… não decide nada sozinho" (FR-1176, FR-274) |
| `consequencia` | texto opcional | uma das duas frases neutras (FR-1177) |
| `canal` | texto opcional | "As convocações deste Perfil são feitas por …" (FR-1179) |
| `reserva` | texto opcional | "O Edital prevê cadastro reserva …" (FR-1180) |
| `recurso` | lista opcional | `{rotulo, fecha_em}` de cada objeto recorrível, e o link "Recorrer de um resultado" |

Que campos cada situação preenche está no [contrato](contracts/bloco-de-situacao.md).

## 2. `CartaoDeLista` — a evidência

Uma linha de `situacoes_do_candidato`, com duas chaves acrescentadas ([D-006](research.md)):

| Campo | Origem |
|---|---|
| `lista` | `nome_da_lista(cabecalho)` — "Ampla concorrência" quando o ato não tem lista **(novo)** |
| `lista_id` | `publicacao.lista_id` **(novo)** |
| `marco`, `marco_codigo`, `natureza_rotulo` | cabeçalho congelado (como hoje) |
| `classificada`, `posicao`, `compartilhada`, `pontuacao`, `motivo` | `SituacaoDivulgada` (como hoje) |
| `publicacao` | a vigente; dá a data (`publicado_em`) e o caminho (FR-061) |

Ordem: `marco_codigo`, depois `_chave_da_lista` com a ordem das Modalidades do Perfil no conteúdo
vigente.

## 3. Entradas da função

`situacao_da_inscricao(*, inscricao, perfil, cartoes, resultados_das_etapas, convocacao, desfecho,
estado, enviada_em, requerimento, recorriveis, recursos, agora)` — todas já presentes no contexto da
view; `perfil` é o dicionário do Perfil da inscrição no conteúdo vigente (pode faltar se uma
Retificação o retirou: então nem canal nem cadastro reserva são ditos).
