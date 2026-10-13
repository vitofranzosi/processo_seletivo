# Data model — 065, conflitos de numeração

**Nenhuma entidade persistida nova, nenhum campo, nenhuma migration** (`FR-1220`). O que existe são
valores derivados do snapshot a cada leitura, e um tipo de achado a mais na estrutura de achados que
já existe (`ValidationFinding`: severidade, código, mensagem, caminho).

## Valores derivados

### Item do documento — `pdf.py` (`D-004`)

| Atributo | O que é |
|---|---|
| número | "5", "5.3", "9.1" — como o documento imprime |
| natureza | seção · Perfil · subseção comum de atribuições · Etapa |
| descrição | o que nomear no achado: o título da seção, "CÓDIGO — nome" do Perfil, os códigos da subseção comum, o nome da Etapa |

Mais um total: **quantas tabelas** o documento terá. Derivado de `_materializaveis`, `numeracao` e
`grupos_de_atribuicoes`; nenhum valor guardado.

### Subitem digitado — `numeracao_digitada.py` (`D-005`, `D-010`)

| Atributo | O que é |
|---|---|
| seção | chave e título da seção textual |
| número da seção | o que o documento imprime para ela; `0` para o preâmbulo |
| parágrafo | ordinal, na divisão do compositor (`D-009`) |
| número digitado | o texto do número, como escrito ("04.1") |
| primeiro grupo | inteiro ("04.1" → 4) |
| trecho | até oitenta caracteres do começo do parágrafo normalizado |
| em conflito | primeiro grupo ≠ número da seção, ou seção sem número |

### Título transcrito — idem

seção, número da seção, parágrafo, número digitado (um grupo), trecho.

### Remissão — idem

| Atributo | O que é |
|---|---|
| onde | caminho do texto e a descrição do lugar (`_textos_impressos`) |
| parágrafo | ordinal, quando o texto é de seção |
| literal | como está no texto ("itens 4.1 a 4.5") |
| números | os números conferidos (as duas pontas de um intervalo) |
| espécie | subitem · seção · tabela · quadro |

## O achado

Seis códigos, com severidade por ato (`D-006`). Mensagem e caminho:

| Código | Caminho | A mensagem nomeia |
|---|---|---|
| `typed_numbering_conflict` / `…_in_retification` | `/sections/id=<uuid>/content` | seção (título e número, ou "o preâmbulo"), cada parágrafo (ordinal, número digitado, trecho), o número por que os subitens começam, "comprovado" |
| `typed_numbering_suspected_title` | idem | seção, parágrafo, a linha, "suspeita" |
| `cross_reference_ambiguous` | caminho do texto | a remissão literal, onde está, cada item com o número, que o sistema não sabe qual foi citado |
| `cross_reference_without_target` | idem | a remissão literal, onde está, que não há item com o número, como explicitar remissão a outro ato |
| `cross_reference_suspected` | idem | a remissão literal, onde está, o motivo (quadro; destino único em conflito), "suspeita" |

## Ciclo de vida

Nenhum. O achado nasce e morre a cada montagem das pendências; mudar o conteúdo muda os achados
(`FR-1202`).
