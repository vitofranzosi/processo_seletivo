# Data model: A experiência da convocação, incremento 1

**Plano**: [plan.md](plan.md) · **Data**: 2026-11-05

**Nenhuma tabela nova, e uma coluna nova**: a identificação do modelo em `ComunicacaoEmitida`,
decidida pelo usuário na D-009 (FR-3889). As tabelas append-only continuam 53. Fora dessa coluna,
tudo o que esta feature monta é apresentação, derivada de registros que já existem.

## O que se lê

| Registro | Onde | Append-only | Para quê |
|---|---|---|---|
| `Convocacao` | `convocacao/models.py` | sim | a vigente, o `vencimento`, a `versao` citada, a `convocacao_anterior` (a cadeia) |
| `ComunicacaoEmitida` | `convocacao/models.py` | sim | `forma`, `resultado`, `enviado_em` de cada elo: o estado do prazo, a correção e a mensagem citada (R-002) |
| `ItemDaListaDaConvocacao` | `convocacao/models.py` | sim | a lista da chamada, com `situacao` e `gravada_em`: a frase da etapa e a variante da mensagem |
| `VersaoConsolidada.content` (a citada) | `publicacoes` | publicação imutável | `matriculationRequest.moment` pela `momento_declarado`: o Requerimento é pedido na chamada? |
| `ApresentacaoDeDocumento`, `ConferenciaDeDocumento` | `convocacao/models.py` | sim | o andamento e o resumo, já montados pelas obrigações da `118` |
| `DesfechoDaConvocacao` | `convocacao/models.py` | sim | o título *"Resultado da sua convocação"* |
| `Unidade` (a do Edital) | `unidades/models.py` | não (060) | a identificação institucional e o canal da mensagem (FR-3887), como hoje |

## O que se monta, sem gravar

### Prazo apresentado (FR-3873 a FR-3875)

Uma função pura recebe o `vencimento`, o instante de referência e o fuso. O fuso vem de
`settings.TIME_ZONE`, e nunca do servidor. Ela devolve um valor imutável:

| Campo | Exemplo | Regra |
|---|---|---|
| `data` | `12/11/2026` | `DD/MM/AAAA` no fuso |
| `hora` | `17h00` | `HHhMM`, nunca `HH:MM` (SC-1155) |
| `dia_da_semana` | `quinta-feira` | por extenso, minúsculas, de tabela própria em português, e não do *locale* do sistema |
| `data_curta` | `12/11` | só no assunto |
| `contagem` | `faltam 7 dias` · `termina amanhã` · `termina hoje, às 17h00` · vazio | FR-3874, em dias de calendário |
| `vencido` | `False` | o instante de referência já passou do vencimento |

### Chamada (FR-3858 a FR-3869)

Um valor por requisição, montado das obrigações da `118` e da convocação vigente: `titulo`, `etapa`,
`prazo` (o *Prazo apresentado*), `corrigida` (bool), `resumo`, `acao` (rótulo e âncora, ou nada),
`ressalva` e `andamento` (as quatro contagens, só obrigatórios). A linha *"Convocação substituída"*
dos dados do ato fica na leitura da `118`, revista na FR-3740.

### Escolha da mensagem (FR-3884, FR-3885, FR-3889; R-002)

Um valor imutável com três campos:

- `modelo`: `inicial` ou `correcao`;
- `variante`: `documento_e_requerimento`, `so_documento`, `so_requerimento` ou `nenhum`, com o caso
  *sem vencimento* tratado à parte pelo prazo;
- `citada`: na correção, o par `enviado_em` e `vencimento` da última comunicação `ENVIADA` da
  cadeia. Na inicial, nada.

**Regra da cadeia** (D-008): percorre-se `convocacao_anterior` até a raiz, e a citada é a
`ComunicacaoEmitida` `ENVIADA` de maior `enviado_em` entre as dos elos anteriores. `FALHA` e
publicação não contam. Sem nenhuma, `modelo = inicial`.

## Validações e invariantes

- A escolha é **função só de registros append-only e da versão citada**. Chamada depois, sobre os
  mesmos registros, devolve o mesmo valor (SC-1160, teste de reconstrução).
- A variante lê os itens com `gravada_em` até o instante do envio, e não os gravados depois.
- O prazo apresentado nunca lê `datetime.now()` sozinho: o instante de referência é parâmetro, e é o
  da requisição.

## A coluna da versão do modelo (D-009, FR-3889)

Uma coluna em `ComunicacaoEmitida`, em migration própria:

| Coluna | Tipo | Valor | Quando vazia |
|---|---|---|---|
| `modelo_da_mensagem` | `CharField(max_length=100, blank=True, default="")` | `inicial:sha256:<64 hex>` ou `correcao:sha256:<64 hex>`, pela regra da R-009, das fontes que renderizaram o envio | publicação, e as linhas anteriores à `121`, sem valor atribuído depois |

- **Append-only sem mudança.** A migration é só `ADD COLUMN` com `default` constante, que o PostgreSQL
  aplica sem reescrever linha, e o gatilho de `UPDATE` não dispara. A tabela continua na lista, e o
  `N de M` continua `53 de 53`.
- **Gravada também na `FALHA`**: registra qual texto se tentou enviar, sem dado pessoal. A
  renderização vem antes da conferência do destinatário, e por isso até a falha por endereço ausente
  tem modelo.
- **Nunca reescrita**: a mudança posterior de um modelo só altera os envios seguintes (SC-1172).
- **Sem `CheckConstraint` de formato.** A forma é garantida pela função que a calcula e pelo teste. Uma
  constraint por expressão regular recusaria a linha vazia das publicações, ou precisaria de uma
  exceção por forma.
- **Sem dado pessoal**: o resumo é do arquivo do modelo, e não da mensagem renderizada.
