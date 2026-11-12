# Data Model: Prevenção de erro nos atos irreversíveis da convocação

**Nenhuma tabela, coluna, constraint, gatilho nem migration.** O provisionamento continua com o
mesmo número de tabelas append-only. O que muda são as leituras e o que o comando aceita.

## Leitura documental da chamada (`LeituraDocumental`, `ItemLido`)

| Leitura | Tipo | Regra | Requisito |
|---|---|---|---|
| `ItemLido.apresentado_pela_pessoa` | bool | alguma apresentação do item nesta chamada tem arquivo | FR-5809 |
| `LeituraDocumental.houve_apresentacao` | bool | algum item apresentado pela pessoa | FR-5800, FR-5809 |
| `motivos_do_atalho(prazo_decorrido)` | lista de itens | `PENDENTE`; e, com o prazo decorrido e `houve_apresentacao`, obrigatório em `A_APRESENTAR` | FR-5800 |
| `aguardando_conferencia` | lista de itens | `RECEBIDO` ou `COMPLEMENTADO` | FR-5802 |
| `fundamento_do_atalho(prazo_decorrido)` | texto | pendente com o motivo; não apresentado com "não apresentado no prazo" | FR-5801 |

`pendencias_para_incluir` e `fundamento_do_indeferimento` continuam como estão.

## Desfechos cabíveis (domínio puro)

**Entrada**: espécie da chamada, `enviado_em`, vencimento, agora, se há atestado, se a pessoa ocupa
vaga no recorte, as pendências para incluir e o canal.

**Saída**:

- `cabem`: as espécies, na ordem de `ESPECIES_DE_DESFECHO`;
- `ainda_nao`: `(especie, codigo, frase, a_partir_de)`, cada uma com o código e a frase da recusa
  do comando.

| Espécie | Nunca cabe em | Ainda não cabe quando | Código |
|---|---|---|---|
| Aceite | chamada para regularizar | obrigatório por conferir | `documentos_nao_conferidos` |
| Regularização | chamada para vaga | obrigatório por conferir | `documentos_nao_conferidos` |
| Não atendimento | — | sem envio, ou vencimento por vir | `nao_atendimento_antes_do_vencimento` |
| Cancelamento por inércia | chamada para regularizar | sem atestado; pessoa não ocupando | `atestado_obrigatorio`, `inercia_sem_ocupacao` |
| Indeferimento, Desistência, Reclassificação | — | — | — |

O indeferimento sempre cabe, e a ciência do prazo é exigência dele, e não impedimento (FR-5808).
`admite_inercia(especie_da_chamada)` decide o gesto do atestado.

## Desfecho: a ciência do prazo

- **Entrada nova do comando**: `ciencia_do_prazo: bool` (formulário: `ciencia_do_prazo=1`).
- **Exigida quando**: a espécie é `INDEFERIMENTO`, há obrigatório não atendido e o prazo não
  decorreu pela regra de `prazo.decorrido` (R-002).
- **Recusa**: `ciencia_do_prazo_em_curso`, 422, campo `ciencia_do_prazo`. Nada é gravado.
- **Registro** (FR-5806), no evento `CONVOCACAO_DESFECHAR` da trilha:
  - `reason` com a frase "Com ciência do prazo em curso, vencendo em DD/MM/AAAA HH:MM" (ou "sem
    vencimento informado");
  - `detalhe.cienciaDoPrazo = {"vencimento": ISO ou null, "enviadoEm": ISO ou null, "pendentes":
    [nomes]}`.

## Corte: a faixa seguinte

- **Entrada nova do comando**: `confirmacao_do_calculo` opcional em `continuar_corte`. Quando vem, é
  conferida por `assinatura_da_proposta(proposta, geracao=vigente)`, e a divergente é recusada com
  `calculo_divergente`. Quando não vem, nada muda: é o caminho da `016`.

## Idempotência

`gesto_ja_concluido` passa a receber a operação: `convocacao:convocar_titulares` (o lote) ou
`convocacao:convocar` (a chamada individual e a para regularizar). O corte usa a operação de hoje do
comando dele, que a confirmação repetida reencontra pela chave.

## Sessão

| Chave | Quem grava | Quem consome | Conteúdo |
|---|---|---|---|
| `recusa_do_desfecho` | `desfechar_view`, na recusa | a tela da convocação, ao renderizar | convocação, espécie, fundamento, atestado, ciência, frase |

Nenhuma conferência grava na sessão (FR-5815, FR-5830). A `conferencia_do_texto` deixa de ser
usada pela chamada individual e pela regularização, e continua na correção e no desfecho.
