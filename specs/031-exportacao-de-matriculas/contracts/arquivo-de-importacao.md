# Contrato do arquivo de importação — as 34 colunas e seus serializadores

**Isto é o contrato de saída da `029` com uma coluna a mais: o nome da função que produz o valor.**
Aquele documento respondia *"de onde sairia"*; este responde *"quem produz, e o que devolve quando
não há"*.

**Um serializador por coluna, e nunca `legivel()`** (`FR-445`). A função de leitura da `029` serve às
duas telas daquela feature: ela formata data em `dd/mm/aaaa` para quem lê e traduz código em texto de
gente. Metade disso é o que o destino quer, e a outra metade não — e a metade errada só apareceria
depois da matrícula. Trinta e quatro funções pequenas são mais longas de escrever e impossíveis de
errar em silêncio.

Todas moram em `matriculas/domain/colunas.py`. Toda célula é **texto**, com formato `@` (`FR-437`).

## Estrutura física

| | |
|---|---|
| Arquivo | `.xlsx`, uma aba só |
| Aba | `Import_ModeloCefor` |
| Cabeçalhos | `A1:AH1`, na grafia exata — `ENDEREÇO` e `NÚMERO` acentuados |
| Dados | a partir da linha 2, uma por convocado |
| Ordem das linhas | `CLASSIF_CURSO_FINAL`, e no empate o protocolo (`FR-446`) |
| Persistência | **nenhuma** (`FR-456`) |

## As 34 colunas

| # | Coluna | Serializador | Origem | Ausência |
|---|---|---|---|---|
| 1 | `INSC` | `inscricao_protocolo` | `Inscricao.protocolo` | lacuna se `Q-3` recusar o protocolo opaco |
| 2 | `NOME` | `nome` | `CandidateIdentity.nome` | nunca vazio |
| 3 | `CLASSIF_CURSO_FINAL` | `classificacao` | fonte da `Q-2` | **vazia até `Q-2`** (`FR-448`) |
| 4 | `COD_CURSO` | `vazio_externo` | — | **sempre vazia** (`D-001`) |
| 5 | `COD_TURNO` | `vazio_externo` | — | **sempre vazia** (`D-001`) |
| 6 | `COD_FORMA_INGRESSO` | `forma_de_ingresso` | Modalidade, ou **ausência → `AC`** | recusa a geração se o `code` for desconhecido (`FR-441`) |
| 7 | `CPF` | `cpf` | identidade, 11 dígitos sem pontuação | nunca vazio |
| 8 | `SEXO` | `sexo` | `F` / `M` | vazia |
| 9 | `ESTADO_CIVIL` | `estado_civil_flexionado` | tabela da `D-004`, por `SEXO` | vazia |
| 10 | `EMAIL` | `email` | credencial principal | nunca vazio |
| 11 | `DATA_NASCIMENTO` | `data` | `data_de_nascimento` | vazia |
| 12 | `COR` | `cor` | `cor_raca` | **vazia e nominal** se *indígena* (`FR-440`) |
| 13 | `NOME_MAE` | `texto` | `nome_da_mae` | vazia — ausência **declarada** |
| 14 | `NOME_PAI` | `texto` | `nome_do_pai` | idem |
| 15 | `CIDADE_NATAL` | `texto` | `municipio_natal` | vazia |
| 16 | `COD_NACIONALIDADE` | `nacionalidade` | Brasil → `BR` | **vazia e nominal** para outros países (`FR-453`) |
| 17 | `RG` | `texto` | `rg` | vazia |
| 18 | `EMISSOR` | `texto` | `rg_orgao_emissor` | vazia |
| 19 | `IDENTIDADE_DATA` | `data` | `rg_expedido_em` | vazia |
| 20 | `TITULO_ELE` | `titulo_eleitoral` | três blocos de quatro | vazia |
| 21 | `ZONA_ELE` | `zona` | três dígitos, zeros à esquerda | vazia |
| 22 | `SECAO_ELE` | `secao` | quatro dígitos, zeros à esquerda | vazia |
| 23 | `CEP` | `cep` | guardado sem pontuação, **emitido com hífen** | vazia |
| 24 | `ENDEREÇO` | `texto` | `logradouro` | vazia |
| 25 | `NÚMERO` | `texto` | `numero` | vazia — *"s/n"* existe |
| 26 | `COMPLEMENTO` | `texto` | `complemento` | vazia — nem todo endereço tem |
| 27 | `BAIRRO` | `texto` | `bairro` | vazia |
| 28 | `CIDADE` | `texto` | `municipio` | vazia |
| 29 | `ESTADO` | `texto` | `uf` | vazia |
| 30 | `CELULAR` | `telefone` | sem pontuação | vazia |
| 31 | `RENDA_PER_CAPITA_PNP` | `renda_da_familia` | `renda_familiar_faixa`, **sem conversão** | vazia; **aviso obrigatório** em toda geração (`FR-452`) |
| 32 | `NECESSIDADES_ESPECIAIS` | `texto` | `necessidade_especifica` | vazia |
| 33 | `NOME_POLO` | `texto` | `PerfilVaga.locality` | vazia |
| 34 | `COD_POLO` | `vazio_externo` | — | **sempre vazia** (`D-001`) |

## A conta

| Situação | Colunas |
|---|---|
| Fluem do requerimento, identidade, oferta e inscrição | 26 |
| **Sempre vazias** — `vazio_externo` | 3 |
| Vazias **condicionalmente**, com a pessoa nomeada | 3 — `COR`, `COD_NACIONALIDADE`, `CLASSIF_CURSO_FINAL` |
| Preenchida **com divergência declarada** | 1 — `RENDA_PER_CAPITA_PNP` |
| Recusa a geração quando não sabe | 1 — `COD_FORMA_INGRESSO` |
| **Total** | **34** |

## As três formas de não ter valor, e por que são distintas

**`vazio_externo`** — o valor é vocabulário de outro sistema. Este nunca o teve, e o relatório diz
*"preencher no destino"*. Não é falha de ninguém.

**Lacuna nominal** — o sistema **tem** um valor declarado e o destino não o comporta, ou não foi
confirmado. Sai vazia **e a pessoa é nomeada**, porque apagar uma declaração em silêncio é o defeito
que esta feature existe para não cometer.

**Recusa** — a geração inteira para. Reservada ao caso em que continuar exigiria **inventar**: uma
grafia de Modalidade que o destino não reconhece não pode ser traduzida sem alguém decidir a
correspondência, e essa decisão não é da exportação.

## O que o serializador NÃO faz

| Tentação | Por quê não |
|---|---|
| Converter a faixa de renda para per capita | os limites coincidem, o denominador não. `D-002` |
| Reescrever `PPP` como `PPI` | o `code` publicado é ato imutável. `D-003`, `FR-441` |
| Emitir `PT` por Portugal | uma amostra com um valor não prova ISO 3166. `D-008`, `Q-7` |
| Tornar o protocolo sequencial | ele é opaco por decisão de privacidade. `Q-3` |
| Numerar as linhas em `CLASSIF_CURSO_FINAL` | é **uma das duas** leituras possíveis, e a `Q-2` não respondeu. `FR-448` |
| Mapear *indígena* para *parda* | é o `R-1`, e a contradição é do destino: a Modalidade `PPP` reserva vaga para quem a coluna `COR` não sabe registrar |
