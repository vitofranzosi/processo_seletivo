# Data Model: A correção da convocação pela gestão

**Nenhuma tabela, coluna, migration, estado ou desfecho novo.** Este arquivo diz o que a correção lê,
o que ela grava — pelas tabelas que já existem —, o que viaja no formulário e na sessão, e as recusas.

## O que se grava

| Registro | Já existe? | O que a correção põe nele |
|---|---|---|
| `Convocacao` (append-only) | sim | uma linha nova, a **sucessora**: `convocacao_anterior` = a corrigida; `motivo_da_sucessao` = o motivo; `chamada` = a da corrigida; `vencimento` = o novo; `especie`, `fundamento`, `apuracao`, `versao`, `ato_de_ordenacao`, `corte` = os do ato; `criado_por`, `criado_em` |
| lista, apresentações e conferências da chamada | sim | **nada**: a sucessora usa as da chamada (FR-3573 da `115`) |
| comunicação da convocação | sim | a emissão da sucessora, pelo `comunicar` de sempre, quando a forma a emite |
| evento de trilha do ato de convocar | sim | um, com a razão de hoje acrescida da convocação corrigida e do vencimento dela |
| reserva de idempotência | sim | a do ato, com o payload acrescido de `corrige` e `previa` |

A corrigida **não muda**: ela deixa de ser vigente porque a sucessora aponta para ela, e é assim que o
domínio já decide vigência.

## O que viaja no formulário

| Campo | Origem | Conferido onde |
|---|---|---|
| `lista` | o recorte da tela | view (`_recorte_pedido`) |
| `chave` | `‹chave da tela›-corrigir-‹convocação›`, nascida no GET | comando (reserva) |
| `inscricao` | a inscrição do cartão | comando: a nomeada tem de ser dela |
| `corrige` | o id da convocação vigente do cartão | comando, sob a trava (FR-3843) |
| `previa` | `assinatura_da_correcao(...)` calculada na montagem do cartão | comando, sob a trava (FR-3857) |
| `motivo` | digitado, obrigatório | comando (`campo="motivo"`) |
| `vencimento` ou `evento` | digitado ou escolhido; um dos dois, obrigatório | fluxo, antes do comando (`campo="vencimento"`), com a recusa de vencimento passado |
| `complemento` | digitado, opcional | — |

`especie` **não** viaja: ela é derivada no ato e conferida pela assinatura.

## A assinatura da prévia

```text
assinatura_da_correcao = canonical_sha256({
    "gesto": "correcao",
    "convocacao": <id da convocação corrigida>,
    "apuracao": <id da apuração vigente>,
    "versao": <id da versão vigente do Edital>,
    "forma": <forma de comunicação vigente do Perfil, ou null>,
    "especie": <espécie da sucessora>,
})
```

**Invariante.** Com os cinco fixados e o complemento do formulário, o fundamento gravado é o mostrado:
`com_complemento(da_convocacao(especie, rótulos(versão), data(apuração)), complemento)`.

## A espécie da sucessora

```text
especie_da_sucessora(inscricao, *, ocupando, alcancados, regularizaveis, anterior) =
    derivada(inscricao, ocupando, alcancados, regularizaveis)   — a da posição, quando há
    ou anterior.especie                                          — a da raiz, quando a posição não a dá
```

É a regra que o comando já aplica em linha, posta numa função para que a tela e o comando cheguem à
mesma (R-004).

## O que a tela monta por cartão

Para cada linha **em aberto** (`desfecho is None`) e **com vencimento**, a partir da leitura que a
página já faz, sem consulta (FR-3855):

| Campo | De onde |
|---|---|
| `especie`, `especieDifere` | `especie_da_sucessora`; comparada à da vigente |
| `fundamento`, `fundamentoDifere` | `fundamentos_por_especie[especie]`; difere quando a apuração ou a versão da vigente não são as vigentes |
| `forma`, `fraseDaComunicacao` | `forma_vigente(versao, perfil)` — individual: *"A mensagem da convocação sai de novo, com o prazo novo. Ela não diz que corrige a anterior."*; por publicação: *"A comunicação aguarda a publicação da chamada."* |
| `venceu` | `estado == CONVOCADO_VENCIMENTO_DECORRIDO` — liga o *"o que reabre"* |
| `vencimentoAtual` | `convocacao.vencimento`, no formato do `datetime-local`, para o script |
| `assinatura` | `assinatura_da_correcao(...)` |
| `recusa` | a `recusa_da_correcao` da sessão, quando é desta inscrição |

E, uma vez por página: `impedimento` = apuração ausente, apuração superada (com as causas) ou ordem
não vigente.

## A sessão

| Chave | Quem grava | Quem consome | Conteúdo |
|---|---|---|---|
| `acao_da_convocacao` = `"correcao"` | `convocar_view`, no sucesso | `convocacao` | — |
| `resultado_da_convocacao` | `convocar_view`, no sucesso | `convocacao` | o resultado de hoje, acrescido de `protocolo`, `vencimentoAnterior`, `vencimentoNovo` e `efeito` (`estendido`, `antecipado`, `mantido`) |
| `recusa_da_correcao` | `convocar_view`, na `DomainError` com `corrige` | `convocacao` | `convocacao`, `inscricao`, `codigo`, `detalhe`, `campo`, `campos` {`motivo`, `vencimento`, `evento`, `complemento`}, `cartaoMudou` |

As três são lidas por `pop`: a tela seguinte as consome e elas somem.

## As recusas

Os códigos novos moram em `convocacao/domain/nomes.py`. As frases são as do domínio; a tela as mostra
como vêm.

| Código | Novo? | Quando | Status | Campo | Onde aparece | Campos |
|---|---|---|---|---|---|---|
| `motivo_da_correcao_obrigatorio` | sim | motivo vazio ou só espaços | 422 | `motivo` | no cartão, junto do motivo | preservados |
| `vencimento_da_correcao_obrigatorio` | sim | nenhum vencimento nem Evento | 422 | `vencimento` | no cartão, junto do vencimento | preservados |
| `vencimento_anterior_ao_envio` | não | vencimento passado ou no instante | 409 | `vencimento` | no cartão | preservados |
| `correcao_sem_vencimento` | sim | a nomeada não tem vencimento (só por POST montado; a tela não oferece) | 409 | — | no cartão | preservados |
| `convocacao_corrigida_sucedida` | sim | a nomeada foi sucedida no intervalo | 409 | — | no cartão da chamada, que mostra a sucessora | motivo **citado**, formulário vazio |
| `convocacao_corrigida_com_desfecho` | sim | a nomeada teve desfecho no intervalo | 409 | — | no cartão, que mostra o desfecho | motivo **citado**, sem formulário |
| `previa_da_correcao_superada` | sim | a assinatura não casa | 409 | — | no cartão, com a prévia nova | preservados |
| `apuracao_obsoleta`, `apuracao_ausente`, `ordem_nao_vigente` | não | impedimento surgido no intervalo | 409 | — | no cartão, com a orientação da FR-3839 | preservados |
| `fora_da_faixa`, `sem_deficit` | não | a posição da pessoa mudou | 409 | — | no cartão | preservados |
| `idempotency_conflict` | não | a mesma chave com outro conteúdo | 409 | — | no cartão | preservados |
| autorização ausente | não | sem base de convocar | 403 | — | resposta de recusa explicada; nada na sessão | — |
| `nao_encontrado` | não | Edital de outra unidade, ou nomeada de outro recorte ou inscrição | 404 | — | resposta 404; nada na sessão | — |

A recusa em estado indeterminado da **comunicação** (`emissao_em_estado_indeterminado`) não é recusa do
ato: a sucessora existe, e ela aparece na contagem do resultado, como na chamada individual.
