# Contrato das telas: formulários, etapas e recusas

Nenhuma rota nova. As rotas abaixo já existem, e cada uma ganha uma etapa ou um campo. As recusas
citam os códigos de `convocacao/domain/nomes.py` e da emissão do corte.

## `interface:convocar` — chamada individual e chamada para regularizar

`POST editais/<edital>/marcos/<marco>/convocacao/convocar`

| Campo | De onde vem | Etapa |
|---|---|---|
| `lista`, `chave`, `inscricao`, `vencimento`, `evento`, `complemento`, `justifica_precedencia` | tela da convocação (hoje) | as duas |
| `especie` | oculto, só na regularização (hoje) | as duas |
| `etapa` | `conferir` (padrão) ou `confirmar` | — |
| `texto_conferido` | a conferência | `confirmar` |
| `corrige`, `previa`, `motivo` | correção (`120`) | **fora** desta spec: segue a prévia assinada dela |

**Respostas:**

| Pedido | Resposta |
|---|---|
| Sem `corrige` e sem `etapa=confirmar` | 200, `convocacao_conferir.html` no modo de uma pessoa; nada gravado (FR-5815) |
| `etapa=confirmar` e chave já concluída (`convocacao:convocar`) | comando: repete o resultado e redireciona (FR-5818) |
| `etapa=confirmar` e `texto_conferido` igual ao recomposto | comando de hoje e redirecionamento para a tela da convocação |
| `etapa=confirmar` e resumo diferente | 200, conferência com o texto de agora e o aviso de texto mudado (FR-5816) |
| Verificação recusa | 200, página só com a razão e "Voltar"; sem formulário (FR-5817, UX-534) |
| Sem autorização | a recusa de hoje (FR-5819) |

O resumo assinado (`conferencia_do_texto.resumo`) cobre a pessoa, a espécie, o fundamento composto,
o assunto e o corpo da mensagem (ou a frase da publicação) e a frase do prazo, com uma pessoa.

## `interface:emitir-corte` — emissão e sucessão

`POST editais/<edital>/marcos/<marco>/corte/emitir`

| Campo | Etapa |
|---|---|
| `chave_idempotencia`, `confirmacao_do_calculo`, `lista`, `motivo` (sucessão) | as duas (hoje) |
| `confirmar` | `1` só no botão da conferência |

| Pedido | Resposta |
|---|---|
| Sem `confirmar=1` | 200, `corte_confirmar.html`: faixa, progride e fica fora, avisos, motivo, assinatura recomposta, `calculo_mudou`; nada gravado (FR-5826 a FR-5828, FR-5830) |
| Proposta recusada (ordem obsoleta, marco sem corte) | redirecionamento para a tela do corte com a frase, como hoje |
| `confirmar=1` | `emitir_corte` de hoje: `confirmacao_do_corte_exigida`, `calculo_divergente`, `corte_ja_emitido`, `sucessao_sem_motivo` |

## `interface:continuar-corte` — faixa seguinte

`POST editais/<edital>/marcos/<marco>/corte/continuar`

| Campo | Etapa |
|---|---|
| `chave_idempotencia`, `lista`, `quantidade`, `motivo` | as duas (hoje) |
| `confirmar` | `1` só no botão da conferência |
| `confirmacao_do_calculo` | **novo**: a assinatura da prévia da continuação |

| Pedido | Resposta |
|---|---|
| Sem `confirmar=1` | 200, `corte_confirmar.html` no modo da faixa seguinte, com as posições e pessoas alcançadas; ou a página com a recusa de `previa_da_continuacao` (`continuacao_sem_motivo`, `sem_faixa_anterior`, `continuacao_sem_quantidade`, `continuacao_ja_emitida`, `continuacao_nao_publicada`, `continuacao_sobre_ordem_sucedida`) (FR-5829) |
| `confirmar=1` | `continuar_corte` com a assinatura; divergente → `calculo_divergente` (FR-5831) |

## `interface:desfechar` — desfecho e atalho do indeferimento

`POST editais/<edital>/marcos/<marco>/convocacao/<convocacao>/desfecho`

| Campo | Novo? | Regra |
|---|---|---|
| `especie`, `fundamento`, `atestado`, `chave`, `lista`, `inaplicabilidades`, `ciencia_das_inaplicabilidades` | não | como hoje |
| `ciencia_do_prazo` | **sim** | `1` quando marcada; exigida pela regra da R-002 |

| Recusa nova | HTTP | Quando |
|---|---|---|
| `ciencia_do_prazo_em_curso` | 422 | indeferimento com obrigatório não atendido, prazo não decorrido e sem `ciencia_do_prazo=1` (FR-5805) |

**Na recusa**, a tela reabre o formulário da linha com o fundamento, a espécie, o atestado e a marca
como vieram, mais a frase da recusa (`recusa_do_desfecho`, R-009).

## A tela da convocação (`interface:convocacao`, GET) — o que cada linha passa a oferecer

| Elemento | Condição | Requisito |
|---|---|---|
| Atalho "Indeferir pelas pendências de documento" | `motivos_do_atalho` não vazio | FR-5800 |
| Fundamento pré-redigido do atalho | `fundamento_do_atalho` | FR-5801 |
| "Aguardam conferência: …" nos dois formulários | `aguardando_conferencia` não vazio | FR-5802 |
| Aviso do prazo e marca de ciência | `exige_ciencia_do_prazo` no atalho; no desfecho geral, sempre que a linha a exige, ligada à opção "Indeferimento" pelo texto (sem script) | FR-5803, FR-5804, UX-532 |
| Passo "nada apresentado no prazo" | vencida, com exigência, sem apresentação | FR-5809, UX-535 |
| Opções do seletor | `desfechos.cabem` | FR-5835, FR-5839 |
| Nota "Ainda não cabem nesta chamada" | `desfechos.ainda_nao` não vazio | FR-5836, UX-533 |
| "Atestar fato externo" | `admite_atestado` | FR-5840 |
| Botão da chamada individual e da regularização | "Conferir antes de convocar" | FR-5822, UX-530 |

No desfecho geral, sem script, a marca de ciência aparece sempre que a linha a exige, com a frase
"Exigida se o desfecho for indeferimento". O comando a ignora nas outras espécies.
