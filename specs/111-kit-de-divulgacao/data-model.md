# Data Model: Kit de Divulgação do Edital

**Nenhuma tabela nova, nenhuma migration.** O kit tem uma leitura (a ficha), um evento na trilha que
já existe, uma chave de ambiente e uma capacidade.

## Ficha (leitura, sem estado)

`portal/ficha.py`, `Ficha` (dataclass imutável), lida por `ler(edital, *, agora, endereco)`.

| Campo | Tipo | Origem | Regra |
|---|---|---|---|
| `modo` | `com-periodo` \| `neutro` \| `sem-material` | período + desfecho | FR-3410 |
| `motivo` | texto | idem | Dito na tela quando não há material, ou no modo neutro |
| `numero`, `ano`, `identificacao` | texto | `content.number`, `content.year` | Não retificáveis |
| `titulo` | texto | `content.title` | Literal |
| `titulo_sem_numero` | texto | idem | Sai só o prefixo "Edital nº N/AAAA –" deste Edital (EC-13) |
| `titulo_do_processo` | texto | `content.processoTitle` | Literal |
| `unidade_sigla`, `unidade_nome` | texto | `identificacao.do_ato` sobre a `source_publication` da versão | Congelada (EC-18); recaída para Publicação anterior à `060` (EC-17) |
| `referencia` | instante | `agora` | Uma por requisição |
| `situacao_chave`, `situacao_rotulo` | texto | `leitura.situacao_publica` | Só decide o modo; nunca vira frase de material |
| `periodo_estado` | futuro \| aberto \| encerrado \| nao-designado | `periodo_de_inscricoes` | — |
| `inicio`, `fim` | instante \| nulo | idem | Fuso institucional |
| `inicio_data`, `inicio_hora`, `fim_data`, `fim_hora`, `periodo_curto` | texto | idem | Escritos uma vez aqui (FR-3415); `periodo_curto` repete o ano só se mudar (EC-7) |
| `cancelado` | bool | `Periodo.cancelado` | — |
| `prorrogado`, `fim_original_texto` | bool, texto | `prorrogacao(original, vigente)` (`publicacoes/application/selectors.py`) | Só quando o término vigente é posterior ao original; com a mesma data, a hora vai nas duas pontas (FR-3417, EC-25) |
| `ofertas[]` | lista de `Oferta` | `content.profiles[]`, na ordem | Ver abaixo |
| `nomes_iguais` | bool | ofertas | Mais de uma oferta, todas com o mesmo nome |
| `total_de_vagas` | inteiro \| nulo | `vagas_do_conteudo(...).total` | Só se toda oferta tem vaga imediata (EC-11); dito sempre como "N vagas em K opções" (FR-3425) |
| `endereco`, `caminho`, `caminho_curto` | texto \| nulo | rota da seleção + host da requisição | D-011; nulo em host local (FR-3447) |
| `termos_em_valor_oficial` | lista | varredura da FR-3414 sobre os valores literais | Apontados na conferência (EC-26) |
| `versao_id`, `versao_hash`, `versao_desde`, `versao_ato` | texto | `VersaoConsolidada` vigente; ato pela numeração única das Retificações publicadas, por `published_at` | — |
| `retificacao_a_vigorar` | instante \| nulo | `retificacoes_a_vigorar` | **Só o instante**; o conteúdo futuro nunca é lido (FR-3404) |
| `origens[]` | lista de `Origem` | `origens` sobre o `contexto()` da `070` (`duvidas/`), que já aplica `acrescimos` | Campo, valor, caminho 004, **atos** (FR-3408); nunca o caminho exato da `ProvenienciaConteudo` |
| `impressao`, `versao_da_impressao` | SHA-256, inteiro | campos afirmados | FR-3411, FR-3448 (D-018) |

**`Oferta`**: `perfil_id`, `nome`, `localidade`, `vagas_imediatas` (saneadas como em
`vagas_do_conteudo`), `cadastro_reserva` (`reserveType in TIPOS_COM_RESERVA`), `quantidade`
(`leitura.quantidade_da_oferta`), `endereco` (âncora `#vaga-<id>`).

**Campos da impressão** (versão 1), em JSON canônico com chaves ordenadas: `numero`, `ano`, `titulo`,
`titulo_do_processo`, `unidade`, `inicio`, `fim`, `cancelado`, `designado`, `ofertas` (`{perfil_id,
nome, localidade, vagas, reserva}`, **ordenadas por `perfil_id`**) e `caminho` (sem host). Ficam
fora: `referencia`, `situacao_*`, `versao_*`, `retificacao_a_vigorar`, o host e a ordem publicada.

## Evento de exportação (trilha de auditoria existente)

`record_event(actor, permission="material:gerar", operation="EXPORTAR_MATERIAL", aggregate=edital,
previous_state=edital.status, previous_revision=edital.revision, …)`: estado e revisão anteriores
iguais aos atuais, porque não é transição. Rótulo em `OPERACOES` e operação em
`OPERACOES_QUE_NAO_CONTAM` (D-005).

| Chave de `detalhe` | Conteúdo |
|---|---|
| `formato` | `png` \| `svg` \| `md` \| `txt` \| `zip` |
| `referencia` | instante da leitura |
| `versao` | `{id, content_hash, vigente_desde, ato}` |
| `template` | identificador da versão do template, ou nulo sem peça |
| `impressao`, `versao_da_impressao` | SHA-256 e a versão (D-018) |
| `campos` | os campos da impressão, com o `perfil_id` de cada oferta, para o "de → para" (FR-3439) |
| `manchete` | a manchete escolhida na lista fechada, ou nulo (FR-3427) |
| `sha256` | resumo dos bytes entregues |

As exportações de um Edital são lidas por `aggregate_type="Edital", aggregate_id=edital.id,
operation="EXPORTAR_MATERIAL"`, ordenadas por `-occurred_at`, no índice
`(aggregate_type, aggregate_id, occurred_at)`. A faixa agrupa por impressão (FR-3439) e não mostra o
autor. O precedente de ler o `detalhe` é o `APLICAR_A_TODOS` (`interface/views.py`).

## Chave de ambiente

| Chave | `development` | `test` | `production` |
|---|---|---|---|
| `KIT_DE_DIVULGACAO_PECA` | ligada | ligada | **desligada** por padrão; liga depois da SC-1054 (P-6) |

## Capacidade e papel

| Capacidade | Papel | Concedida por padrão a |
|---|---|---|
| `material:gerar` | `comunicacao` — "Comunicação" (P-1) | ninguém |
