# Data Model — O piloto interno do assistente conversacional do Edital (071)

*Phase 1 de [plan.md](plan.md). Uma tabela nova; o resto é em memória, derivado da `070`.*

---

## 1. O que o piloto lê, e o que não lê

Lê **só** pela `070`: `duvidas.application.consultar.contexto()` (a versão vigente, as futuras já
publicadas, os atos, a proveniência, o desfecho, o canal institucional, os links). Nenhuma leitura
nova de tabela de Edital, de publicação, de rascunho, de inscrição ou de resultado (`FR-1469`,
`FR-1470`).

Lê e escreve a tabela própria, `TrocaDoPiloto` (§3).

Lê da sessão do Django o identificador da conversa de cada Edital (`R-011`).

---

## 2. Em memória

Todas congeladas, como as da `070` (`duvidas/domain/estruturas.py`).

### `Fonte`

| Campo | Tipo | Origem |
|---|---|---|
| `id` | `str` — `F1`, `F2`, … | A ordem canônica de `fontes_completas` (`R-002`) |
| `natureza` | `TEXTO`, `DADO` ou `CALCULADA` | `TEXTO` e `DADO` da `070`; `CALCULADA` para situação, desfecho, Retificação futura, canal institucional e documentos por Perfil e lista |
| `lugar` | `str` | A `localizacao` do cartão da `070`, pelo título (`FR-1431` da `070`) |
| `rotulo` | `str` | O rótulo do valor, quando houver |
| `conteudo` | `str` | O conteúdo do cartão, inteiro e **sem acréscimo**. Nas `CALCULADA` de Retificação futura: "Retificação publicada em …, vigente a partir de …, altera {lugar da fonte Fn}: passa a valer …" |
| `caminho`, `posicao` | `str`, `int \| None` | Do cartão; para rastreio e para a chave de colisão |
| `origens` | `tuple[AtoPublicado, ...]` | Do cartão (`FR-1437` da `070`) |
| `futuro` | `tuple[ValorFuturo, ...]` | Do cartão. **Não vai ao modelo dentro da fonte**: gera as fontes `CALCULADA` de Retificação futura e o aviso que a aplicação acrescenta às fontes citadas (`FR-1490`) |
| `altera` | `str \| None` | Só nas `CALCULADA` de Retificação futura: o `id` da fonte vigente que o ato altera |
| `links` | `tuple[Link, ...]` | Do cartão (`FR-1438` da `070`) |
| `anexo` | `bool` | Verdadeiro para o cartão "Anexo vinculado" e os de anexo da `P-12` |

**Invariantes.**

- Nenhuma fonte `TEXTO` tem conteúdo diferente do conteúdo publicado no caminho (`SC-534` da `070`).
- Nenhuma chave `(natureza, caminho, posicao)` aparece com dois conteúdos (`R-002`).
- `CALCULADA` traz o instante no conteúdo ("Situação em 20/10/2026, às 14h00: …").
- **Nenhuma fonte `TEXTO` ou `DADO` carrega valor de outra versão** (`FR-1467`, `FR-1472`). A
  Retificação futura já publicada é uma afirmação da aplicação sobre um ato publicado, rotulada como
  calculada, e não conteúdo da versão vigente; é por isso que ela não fere o `SC-550`.

### `Mensagens`

A lista de mensagens de uma chamada (`R-003`), com:

- `impressao_das_fontes`: SHA-256 da serialização das fontes (`R-004`);
- `tokens_medidos`: pelo tokenizer, com o acréscimo por mensagem (`R-006`);
- `historico_desde`: a ordem do turno mais antigo incluído, ou `None` quando não há histórico.

### `SaidaDoModelo`

O objeto do contrato [saida-do-modelo.md](contracts/saida-do-modelo.md): `tipo` e `trechos`, cada
trecho com `natureza` (`explicacao`, `dado`, `citacao`), `texto` e `fontes`.

### `Conferencia`

| Campo | Tipo |
|---|---|
| `aprovada` | `bool` |
| `motivos` | `tuple[Motivo, ...]` — cada um com o código da regra (`FORMA`, `FONTE_INEXISTENTE`, `CITACAO_NAO_LITERAL`, `VALOR_SEM_FONTE`, `TIPO_SEM_FONTE`, `NEGATIVA_NAO_DECLARADA`), o trecho e o valor |

### `Devolucao`

O que a porta devolve (`R-008`): `texto`, `modelo`, `tokens_de_entrada`, `tokens_de_saida`,
`termino`, `custo`, `provedor`, `raciocinio`. O `raciocinio` é descartado logo depois de conferido o
término, antes da gravação, da tela e do log (`FR-1492`). Tokens e custo vão só para o log
(`FR-1508`).

---

## 3. A tabela `TrocaDoPiloto`

**Uma linha por pergunta**, aprovada ou não. É o histórico da conversa e o registro da avaliação
(`R-011`). **Não é append-only** e **não é dado normativo**: é excluída 90 dias depois do relatório
final (`R-021`).

| Coluna | Tipo | Nulo | Para quê |
|---|---|---|---|
| `id` | UUID | não | |
| `conversa` | UUID, com índice | não | Agrupa os turnos; vem da sessão |
| `ordem` | inteiro positivo | não | A posição na conversa |
| `edital` | FK `processos.Edital`, `PROTECT` | não | A seleção da conversa (`FR-1465`) |
| `criada_em` | instante | não | Quando a troca foi gravada |
| `instante` | instante | não | O instante em que a versão foi determinada: o de `criada_em` na tela; o do caso, na avaliação (princípio II) |
| `origem` | texto, `TELA` ou `AVALIACAO` | não | Separa as conversas da tela das rodadas da avaliação; não identifica pessoa |
| `versao` | UUID da `VersaoConsolidada` | sim | A versão vigente no `instante`; nula se a recusa veio antes da leitura |
| `versao_curta` | texto | não | O identificador curto da `070` |
| `pergunta` | texto | não | **Mascarada** (`R-015`) |
| `estado` | texto, valores fechados (§4) | não | `RESPONDIDA_E_CONFERIDA` ou o estado de recusa ou falha |
| `tipo` | texto, valores fechados | sim | Um dos oito tipos (`FR-1486`), quando a saída tem forma |
| `trechos` | JSON | sim | Os trechos da saída, com o CPF mascarado |
| `fontes_citadas` | JSON | sim | O conteúdo das fontes citadas, como foram entregues — para a análise sem rederivar |
| `conferencia` | JSON | sim | Os motivos da recusa |
| `historico_desde` | inteiro | sim | A ordem do turno mais antigo enviado (`FR-1481`) |
| `chamou_o_servico` | booleano | não | Se houve chamada |
| `servico` | texto | não | `ollama` ou `openrouter` |
| `modelo_configurado` | texto | não | |
| `modelo_que_respondeu` | texto | sim | |
| `parametros` | JSON | não | Temperatura, `top_p`, semente, contexto efetivo, saída máxima, raciocínio |
| `impressao_das_fontes` | texto | sim | A versão da fonte (`FR-1515`) |
| `versao_das_instrucoes` | texto | não | A versão do prompt |

**Restrições.** Única `(conversa, ordem)`. `ordem ≥ 1`. `estado`, `tipo` e `origem` em `CHECK` com os
valores fechados.

**A `ordem` sob concorrência.** Duas perguntas da mesma conversa — duas abas — podem chegar juntas. A
`ordem` é alocada **na gravação**, e não antes da chamada: numa transação curta, com
`pg_advisory_xact_lock` pela conversa, lê o máximo e grava o seguinte. A chamada ao serviço acontece
fora de qualquer transação. As duas trocas ficam gravadas, na ordem em que terminaram; o histórico de
cada uma é o que estava gravado quando ela começou.

**O que não tem, de propósito.**

- Nenhuma coluna de identidade, papel, sessão ou origem do participante (14º; `FR-1509`).
- Tokens, tempo e custo: vão ao log e ao relatório da rodada (`FR-1510`).
- O raciocínio do modelo (`FR-1492`).
- A credencial, em qualquer forma (`FR-1502`).

**O histórico** de uma conversa é `TrocaDoPiloto.filter(conversa=…, edital=…)` por `ordem`. Entram
no contexto só as linhas com `estado = RESPONDIDA_E_CONFERIDA` e `versao` igual à da pergunta atual
(`FR-1495`).

**O gasto no serviço externo não se conta nesta tabela** (`FR-1507`, emendado em 14/10): quem o
limita é o limite de gasto da credencial, no próprio serviço. A `origem` continua separando as
conversas da tela das rodadas da avaliação, para a exportação e a análise.

**O limite da conversa** conta as linhas da conversa (`FR-1496`).

---

## 4. Os estados de uma troca

| Estado | Houve chamada? | Quando |
|---|---|---|
| `RESPONDIDA_E_CONFERIDA` | sim | A saída passou em todas as regras |
| `NAO_PASSOU_NA_CONFERENCIA` | sim | `Conferencia.aprovada` falso |
| `INCOMPLETA` | sim | Término por limite de saída, ou sem término normal (`FR-1483`) |
| `POSSIVEL_CORTE` | sim | Tokens informados abaixo dos medidos, além da tolerância (`FR-1482`) |
| `MODELO_DIFERENTE` | sim | O modelo que respondeu não é o configurado (`FR-1499`) |
| `RESPOSTA_MALFORMADA` | sim | Sem JSON, ou JSON fora da forma |
| `INDISPONIVEL` | tentou | Conexão recusada ou serviço fora |
| `TEMPO_ESGOTADO` | tentou | Passou do tempo-limite |
| `LIMITE_DO_SERVICO` | tentou | 429 |
| `ORCAMENTO_ESGOTADO` | tentou | 402: o serviço recusou pelo limite de gasto da credencial |
| `LIMITE_DE_USO` | não | Teto global sem vaga, ou limite da conversa |
| `EXCEDE_O_CONTEXTO` | não | Sem histórico, ainda não cabe (`FR-1481`) |
| `PERGUNTA_RECUSADA` | não | Tamanho, ou padrão pessoal com serviço externo |
| `SEM_TOKENIZER` | não | Sem a biblioteca ou o arquivo (`FR-1479`) |

"Tentou" conta como chamada (`chamou_o_servico = true`): o serviço pode ter cobrado.

Nenhuma transição: a troca nasce no estado final, numa gravação só.

---

## 5. A sessão

`request.session["assistente"]` é um dicionário `edital_id → conversa`. "Nova conversa" troca o
valor. A sessão não guarda pergunta, resposta nem histórico.

---

## 6. A migration

`duvidas/migrations/0001_initial.py`, a primeira do pacote: cria a tabela, o índice de `conversa`, a
restrição única e os `CHECK`. Caminho de volta: apaga a tabela — e só é aplicável numa máquina sem
registros a preservar, como toda migration de tabela nova. Nenhum gatilho, porque a tabela não é
append-only.
