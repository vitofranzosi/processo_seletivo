# Data Model — Avisos complementares (066)

*App `avisos`, novo. Seis tabelas append-only e uma mutável. Nenhuma tabela existente ganha
coluna, e nenhuma é alterada. Caminhos relativos a `backend/processo_seletivo/`.*

## 1. Tabelas

### 1.1 `ModeloDeAviso` — mutável, auditada, nunca excluída

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | |
| `institution_scope` | texto | a unidade (`Unidade.codigo` é o escopo, `060`) |
| `nome` | texto ≤ 120 | único por escopo, sem distinção de caixa |
| `assunto` | texto ≤ 150 | variáveis da lista fechada (`FR-1255`) |
| `corpo` | texto ≤ 5.000 | idem |
| `ativo` | booleano | |
| `modelo_inicial` | booleano | marca dos três de `D-008`; nunca muda |
| `criado_por`, `criado_em`, `alterado_por`, `alterado_em` | | |

- **`delete()` recusa sempre**, e o gatilho `BEFORE DELETE` recusa no banco. `UPDATE` é permitido,
  porque o modelo é mutável.
- Cada criação, edição, inativação e reativação passa por `record_event`, com o estado anterior e o
  novo (`FR-1277`).
- **Não entra em `TABELAS_APPEND_ONLY`**: a role de runtime precisa de `UPDATE`, e
  `provisionar_papeis` só sabe revogar `UPDATE` e `DELETE` juntos (`seguranca/papeis.py`, o
  `REVOKE UPDATE, DELETE`). As duas camadas contra a exclusão são o `delete()` do modelo e o gatilho.
  Estender o provisionamento para revogar só `DELETE` de uma tabela não compensa o custo.

### 1.2 `Aviso` — append-only

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | |
| `edital` | FK `Edital`, PROTECT | |
| `institution_scope` | texto | cópia do escopo do Processo, para filtrar sem junção |
| `origem` | `RESULTADO` \| `CHAMADA` | |
| `motivo` | `PRIMEIRO_AVISO` \| `REENVIO_DE_FALHAS` \| `REENVIO_JUSTIFICADO` | `R-011` |
| `aviso_anterior` | FK `self`, nulo, PROTECT | obrigatório quando o motivo é reenvio |
| `justificativa` | texto | obrigatória em `REENVIO_JUSTIFICADO`; vazia no primeiro aviso |
| `perfil_id`, `marco_id` | UUID | o recorte; em `RESULTADO` vem das publicações citadas |
| `lista_id` | UUID nulo | só em `CHAMADA` (o recorte da convocação) |
| `natureza` | `PRELIMINAR` \| `DEFINITIVA`, nulo | só em `RESULTADO` |
| `referencia_da_publicacao` | texto | só em `CHAMADA`: a referência exata que agrupou as convocações (`D-003`) |
| `retificadora` | booleano | alguma publicação citada sucede outra (`FR-1248`) |
| `assunto`, `corpo` | texto | **finais**, com o rodapé e a linha de retificação; só `{nome_do_candidato}` por resolver (`R-007`) |
| `modelo` | FK `ModeloDeAviso`, nulo, PROTECT | de onde o texto partiu |
| `solicitado_por`, `solicitado_em` | | |
| `idempotency_key`, `correlation_id` | texto | |

Constraints:

- `CHECK`: `RESULTADO` exige `natureza` e proíbe `referencia_da_publicacao`; `CHAMADA` exige a
  referência e proíbe `natureza`.
- `CHECK`: motivo de reenvio exige `aviso_anterior`; `REENVIO_JUSTIFICADO` exige justificativa não
  vazia.

### 1.3 `PublicacaoDoAviso` — append-only

| Campo | Regra |
|---|---|
| `aviso` | FK, PROTECT |
| `publicacao` | FK `divulgacao.PublicacaoResultado`, PROTECT |

`UNIQUE (aviso, publicacao)`. Só existe para `origem=RESULTADO`. Índice em `publicacao`, para a
pergunta "esta publicação já foi avisada?" (`FR-1247`, `FR-1262`).

### 1.4 `DestinatarioDoAviso` — append-only

| Campo | Tipo | Regra |
|---|---|---|
| `aviso` | FK, PROTECT | |
| `inscricao` | FK `Inscricao`, PROTECT | |
| `convocacao` | FK `Convocacao`, nulo, PROTECT | só em `CHAMADA`: qual convocação do universo |
| `elegibilidade` | `ELEGIVEL` \| `NAO_ELEGIVEL_DESFECHO` \| `NAO_ELEGIVEL_SUCEDIDA` \| `NAO_ELEGIVEL_VENCIDA` | `D-003`; em `RESULTADO`, sempre `ELEGIVEL` |
| `endereco` | texto | congelado na confirmação; vazio é "sem endereço" (`FR-1252`) |

`UNIQUE (aviso, inscricao)`, que é a deduplicação da `FR-1249`.

Recebe mensagem quem é `ELEGIVEL` **e** tem `endereco`. Os demais existem para que o universo do ato
fique rastreável.

### 1.5 `TentativaDeEnvio` — append-only

| Campo | Regra |
|---|---|
| `destinatario` | FK, PROTECT |
| `numero` | 1, 2, 3… |
| `iniciada_em` | gravada **antes** de chamar o servidor, numa transação já confirmada (`R-003`) |

`UNIQUE (destinatario, numero)`: a última porta contra a tentativa duplicada (`R-002`).

### 1.6 `ResultadoDaTentativa` — append-only

| Campo | Regra |
|---|---|
| `tentativa` | OneToOne, PROTECT |
| `resultado` | `ACEITA` \| `FALHA_TEMPORARIA` \| `FALHA_DEFINITIVA` \| `INDETERMINADA` |
| `registrado_em` | |
| `detalhe_tecnico` | sem endereço nem nome (`FR-1279`) |

### 1.7 `InterrupcaoDoAviso` — append-only

| Campo | Regra |
|---|---|
| `aviso` | OneToOne, PROTECT: um aviso se interrompe uma vez |
| `motivo` | texto não vazio |
| `interrompido_por`, `interrompido_em` | |

## 2. Estado derivado do destinatário

Nenhuma coluna de estado. Para cada `DestinatarioDoAviso`, a partir da última tentativa e do
resultado dela:

| Condição | Estado (`D-005`) |
|---|---|
| não elegível | **Não elegível** (com o motivo) |
| elegível sem endereço | **Sem endereço** |
| sem tentativa, aviso interrompido | **Interrompido antes do envio** |
| sem tentativa começada, e a janela de despacho passou (`R-016`) | **Expirada sem envio** |
| sem tentativa | **Pendente** |
| última tentativa sem resultado | **Em envio**, se for recente; senão **Indeterminada** (R-004) |
| último resultado `ACEITA` | **Aceita pelo servidor** |
| último `FALHA_TEMPORARIA`, abaixo do limite de tentativas, dentro da janela | **Falha temporária** (aguarda nova tentativa) |
| último `FALHA_TEMPORARIA`, abaixo do limite, e a janela passou | **Expirada sem envio** |
| último `FALHA_TEMPORARIA` no limite, ou `FALHA_DEFINITIVA` | **Falha definitiva** |
| último `INDETERMINADA` | **Indeterminada** |

**Elegível ao despacho** é o destinatário elegível, com endereço, de aviso não interrompido, **dentro
da janela de despacho** (`R-016`), que esteja **Pendente**, ou em **Falha temporária** com o
intervalo de retentativa vencido (R-005). Com `AVISOS_AOS_CANDIDATOS` desligada, ninguém é elegível
ao despacho (`R-013`).

O **aviso concluído** é o que não tem destinatário em Pendente, Em envio nem Falha temporária. A
janela vencida conclui o aviso, porque o que sobrou expira. Só o
aviso não concluído pode ser interrompido.

## 3. Universo e elegibilidade, por origem

**Resultado** (`FR-1246`, `FR-1247`)

```
publicações = PublicacaoResultado vigentes (sucessoras vazias) do (edital, perfil, marco),
              com a natureza escolhida,
              sem PublicacaoDoAviso de aviso PRIMEIRO_AVISO
universo    = SituacaoDivulgada dessas publicações, distinta por inscrição
elegível    = todos
```

**Chamada** (`FR-1251`)

```
universo    = Convocacao do recorte (edital, perfil, marco, lista)
              com ComunicacaoEmitida(forma=PUBLICATION, resultado=ENVIADA,
                                     referencia_da_publicacao = a escolhida)
              — inclusive sucedidas, desfechadas e vencidas
elegível    = vigente (sem sucessora) ∧ sem desfecho ∧ não decorrido(vencimento, agora)
```

O estado da convocação é lido pelos seletores que já existem: `desfecho_de`, `estado_de` e
`vigentes_por_inscricao` (`convocacao/application/selectors.py`). Nenhuma regra de convocação é
reescrita aqui.

**Endereço** (`FR-1250`): `destinatario_de` (`convocacao/application/comunicar.py:105`) sai para
um módulo comum, `identidade/application/endereco.py`. `comunicar` e `avisos` passam a importar de
lá, e as duas usam uma implementação só.

## 4. Proteção em duas camadas

As seis tabelas append-only (1.2 a 1.7) têm:

- `save()` que recusa alteração de linha existente, e `delete()` que recusa sempre, no padrão de
  `convocacao/models.py:75-81`;
- gatilho `BEFORE UPDATE OR DELETE` na migration, no padrão de `convocacao/migrations/0001_initial.py:27-47`;
- entrada em `TABELAS_APPEND_ONLY` (`seguranca/papeis.py:26`).

Com isso o `M` do `provisionar_papeis` vai de 34 para 40.

`ModeloDeAviso` tem o `delete()` que recusa e o gatilho `BEFORE DELETE`, e fica fora da lista.
