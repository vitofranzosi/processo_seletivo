# Data Model: Endereçamento Normativo por Chave Estável

**Feature**: `004-enderecamento-normativo-estavel` | **Fase**: 1 | **Data**: 2026-08-29

Esta feature **não cria entidade nem coluna** — remove uma. O que muda é a gramática de um valor já
existente, `AlteracaoNormativa.target_path`, e a declaração de quais coleções têm chave.

## A gramática do segmento

Um `targetPath` continua sendo uma sequência de segmentos separados por `/`, como no RFC 6901. O
que muda é o que um segmento pode ser, e **qual forma vale depende do contêiner**:

| Forma | Contêiner | Significado | Escrita |
| --- | --- | --- | --- |
| `nome` | objeto | chave literal | sim |
| `0`, `1`, … | lista | índice posicional | **não**, onde há chave |
| `-` | lista | acréscimo ao fim | sim, em `ADD` |
| `id=<uuid>` | lista | o elemento cujo `id` é `<uuid>` | sim |

**A regra do contêiner é o que preserva expressividade.** Em objeto, `id=algo` é nome de chave e
nada mais. Sem isso, a extensão retiraria do RFC 6901 algo que ele permitia.

**Comparação**: o valor é um UUID, comparado como texto exato e sem normalização de caixa. O
seletor não aceita identificador de outra natureza — as entidades endereçáveis carregam UUID, e
generalizar seria construir para um caso que não existe.

Exemplos:

```
/profiles/id=00000000-0000-0000-0000-000000000502/name
/profiles/id=…0502/competitionModalities/id=…0611/normativeRule/percentage
/profiles/-
/profiles/id=…0502/requirements          ← coleção atômica: substituída inteira
```

## Coleções com e sem chave

Declaração explícita no domínio, em `publicacoes/domain/colecoes.py`, verificada por teste contra um
snapshot real.

| Caminho da coleção | Elemento tem `id`? | Endereçamento |
| --- | --- | --- |
| `/profiles` | sim | por chave |
| `/schedule` | sim | por chave |
| `/profiles/*/competitionModalities` | sim | por chave |
| `/profiles/*/requirements` | **não** | valor atômico: `REPLACE` da lista inteira |

`normativeRule` tem `id` mas **é objeto**, não item de lista: continua endereçada pelo nome da
chave. Ter identificador não a torna elemento de coleção.

`applied_publications`, da Versão Consolidada, é controle interno e não é endereçável por Alteração
Normativa em forma alguma.

**Por que declarar e não detectar**: introspecção — "é dict e tem `id`" — acerta hoje e falha em
silêncio quando uma coleção nova nascer sem identificador. Com a declaração verificada, esse dia
vira falha de suíte.

## O que muda em cada tabela

| Tabela | Mudança |
| --- | --- |
| `publicacoes_alteracaonormativa` | `target_path` passa a conter a forma por chave. **A coluna `expected_anchors` é removida.** |
| Demais tabelas | Nenhuma. |

`ProvenienciaConteudo.target_path` continua registrando o caminho tal como o ato o declarou — o que
muda é a forma que os atos passam a declarar, não o comportamento do registro.

## Migração

### `0008_remover_ancoras`

`RemoveField` sobre `AlteracaoNormativa.expected_anchors`. **Sem conversão de dados, sem condição a
comprovar, sem relatório.**

O sistema não está em produção e não há ato a preservar. Tudo o que a versão anterior deste
documento previa — converter caminhos existentes a partir das âncoras, devolver o que não
resolvesse, auditar cada conversão, relatar por origem — deixou de ter objeto.

A função inversa reintroduz o campo vazio, como exige a regra permanente do projeto de que toda
migration declare caminho de volta.

## Estados e transições

Nenhuma transição nova, nenhuma linha muda de estado. A feature não toca no ciclo de vida da
Retificação.

## Invariantes

- Todo `target_path` ou nomeia a entidade (`id=`), ou acrescenta ao fim (`-`), ou é atômico. Não
  existe índice sobre coleção com chave.
- Em lista, `ADD` aceita **apenas** a folha `-`. Não há inserção em posição.
- Todo elemento de coleção com chave carrega `id` UUID. A regra é verificada quando o elemento
  entra, e não só quando o snapshot é montado: `ADD` sem identificador utilizável é recusado.
- Chave repetida numa coleção é estado impossível, recusado na elaboração e na Publicação, e
  verificado **depois de cada alteração** — senão acrescentar sob a chave de outro e remover o
  original em seguida terminaria íntegro e teria trocado a entidade em silêncio.
- Identificador que apareça em duas coleções do mesmo snapshot é irrelevante: a resolução é escopada
  à coleção nomeada no caminho. Unicidade global **não** é pressuposta.
- A precondição de conteúdo por hash continua valendo sobre todos os caminhos.
