# Data Model: O Edital oficial em linguagem simples — lote 1

Nenhuma entidade de domínio nova, e nenhum campo novo no Edital. Uma coluna nova na `Publicacao`, uma
mudança no catálogo de seções e três estruturas transitórias do compositor.

## Persistente

### `Publicacao.redacao_do_documento` (nova coluna)

| Campo | Tipo | Regra |
|---|---|---|
| `redacao_do_documento` | inteiro pequeno positivo, padrão `1` | gravado no ato, com a redação com que o documento foi composto; `2` desde esta feature; nunca muda (a tabela é append-only) |

- **Publicações existentes**: `1`, pelo padrão da migration. A coluna é acrescentada sem UPDATE de
  linha, como as da `060`.
- **Leitores**: a página do ato de ordenação, pela versão citada (`ato.versao.source_publication`),
  para exibir o desempate na redação daquele ato (FR-1397).

### Catálogo de seções (`editais/domain/secoes.py`)

| O que muda | O que não muda |
|---|---|
| `title` e `order` de cada seção, pelo *Catálogo apresentado* | `key`, `type`, `source`, a identidade uuid5 por chave |

Os snapshots dos Editais submetidos depois levam os títulos e a ordem novos, e é por eles que a
apresentação é reconhecida (R-001). Os snapshots existentes não mudam.

### Rótulos de `PerfilVaga.forma_de_convocacao`

Os rótulos das `choices` passam à redação 2 (R-004). A migration é um `AlterField` sem efeito no banco,
e os valores gravados (`PUBLICATION`, `INDIVIDUAL_MESSAGE`) não mudam.

## Transitório (compositor)

### Apresentação

| Elemento | O que é |
|---|---|
| Assinatura | o conjunto `(key, title, order)` das seções de um catálogo |
| Registro | assinatura → apresentação; padrão: plana |
| Entrada | título apresentado; chaves-membro na ordem; lugares do conteúdo gerado |
| Numeração apresentada | chave → `"N"` ou `"N.k"`; `None` para a seção que não sai; `0` para o preâmbulo |

### Redação

| Elemento | O que é |
|---|---|
| Versão | `1` (a de hoje) ou `2` (desta feature) |
| Frase | função da regra declarada e da versão; as variantes estão em [`contracts/redacao.md`](contracts/redacao.md) |

### Métrica

| Elemento | O que é |
|---|---|
| Helvetica (padrão) | a tabela de larguras de hoje, que o comprovante e a divulgação continuam usando |
| Fonte embutida | as larguras da Liberation Sans, lidas do subconjunto versionado, usadas só pelo Edital |

## Arquivos versionados novos

- O subconjunto WinAnsi da Liberation Sans Regular e Bold, o texto da OFL 1.1 e o SHA-256 dos
  arquivos de origem.
- As fixtures de bytes do comprovante e do documento de divulgação (R-005).
- Em `specs/069-…/demonstracao/`: os PDFs dos cenários A e B e da variante, as páginas e a conferência
  por enunciado.
