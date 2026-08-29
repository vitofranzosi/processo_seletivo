# Data Model: Endereçamento Normativo por Chave Estável

**Feature**: `004-enderecamento-normativo-estavel` | **Fase**: 1 | **Data**: 2026-08-29

Esta feature **não cria entidade nem coluna**. O que muda é a gramática de um valor já existente —
`AlteracaoNormativa.target_path` —, a declaração de quais coleções têm chave, e a retirada de uma
coluna que deixa de ter função.

## A gramática do segmento

Um `targetPath` continua sendo uma sequência de segmentos separados por `/`, como no RFC 6901. O
que muda é o que um segmento pode ser, e **qual forma vale depende do contêiner**:

| Forma | Contêiner | Significado | Escrita | Leitura |
| --- | --- | --- | --- | --- |
| `nome` | objeto | chave literal | sim | sim |
| `0`, `1`, … | lista | índice posicional | **não**, onde há chave | sim, sempre |
| `-` | lista | posição de acréscimo ao fim | sim, só em `ADD` | sim |
| `id=<valor>` | lista | o elemento cujo `id` é `<valor>` | sim | sim |
| `before=<valor>` | lista | **referência de posição**: imediatamente antes do elemento nomeado | sim, só em `ADD` | — |
| `after=<valor>` | lista | **referência de posição**: imediatamente depois do elemento nomeado | sim, só em `ADD` | — |

**A regra do contêiner é o que preserva expressividade.** Em objeto, `id=algo` é nome de chave e
nada mais. Sem isso, a extensão retiraria do RFC 6901 algo que ele permitia.

**Comparação e escape**: o valor é comparado como texto exato, sem normalização de caixa.
Identificador que contenha `/` ou `~` usa o escape do próprio RFC 6901 (`~1`, `~0`) — a extensão não
introduz escape novo.

Exemplos:

```
/profiles/id=00000000-0000-0000-0000-000000000502/name
/profiles/id=…0502/competitionModalities/id=…0611/normativeRule/percentage
/profiles/before=…0503
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
| `publicacoes_alteracaonormativa` | `target_path` passa a conter a forma por chave nos atos novos e nos convertidos. **Nenhuma coluna nova.** `expected_anchors` é removida na segunda migração. |
| `publicacoes_provenienciaconteudo` | `target_path` registra o caminho **tal como o ato o declarou**, sem conversão. É evidência de qual Publicação originou cada trecho; reescrevê-la faria o registro divergir do ato que documenta. |
| `publicacoes_retificacao` | Nenhuma mudança de esquema. Algumas linhas mudam de estado, quando a conversão devolve para elaboração. |
| `auditoria_registroauditoria` | Nenhuma mudança de esquema. Ganha eventos novos: um por conversão, um por devolução. |
| Demais tabelas | Nenhuma. |

## Migrações

### `0008_converter_caminhos`

Converte `target_path` das Alterações de Retificações em estado **não final**.

**Insumo**: `expected_anchors`, gravada pela `003` — a identidade de cada índice atravessado.

**Critério de inequivocidade** (FR-005c), por segmento posicional de coleção com chave, as três ao
mesmo tempo:

1. existe âncora para o segmento;
2. a âncora é única — sem valor concorrente;
3. a âncora corresponde à mesma entidade encontrada naquele segmento no snapshot-base.

Falhando qualquer uma — ausência, duplicidade, divergência, âncora incompleta — a Retificação é
**devolvida** para elaboração com motivo, e nenhum caminho seu é convertido. Nunca infere.

**Pressuposto declarado** (FR-005d): âncoras completas nos atos criados após a `0006` da `003` e nos
cobertos pelo backfill daquela feature. Ato fora dessas duas origens cai na regra acima. A migração
relata convertidas e devolvidas **por origem**, para que a exceção apareça em vez de passar como
sucesso.

**Lógica congelada** dentro da migração, como a `0006` da `003`: migração aplicada tem de continuar
significando o que significava no dia em que rodou.

**Auditoria**: cada conversão registra caminho antes, caminho depois, momento e a identificação da
migração — não uma pessoa, porque não houve ato humano.

### `0009_remover_ancoras`

Remove `expected_anchors`. **Só executa depois de comprovar** a condição de SC-007: nenhuma
Retificação em estado não final com a coluna preenchida. Se a condição não valer, falha em vez de
apagar a evidência de que a conversão deixou caso para trás.

Separar as duas migrações é deliberado: a `0008` é reversível sem perda de dado; a `0009` não é, e
por isso acontece sobre condição verificada.

## Estados e transições

Nenhuma transição nova. A conversão usa a transição **devolver** que já existe (`HOMOLOGADA` ou
`EM_REVISAO` → `EM_ELABORACAO`), com `return_reason` preenchido pela migração.

Retificação em estado final — `PUBLICADA` ou `CANCELADA` — não é tocada. As triggers de imutabilidade
da `003` recusariam de qualquer forma, o que é a segunda camada funcionando como projetada.

## Invariantes

- Todo `target_path` gravável ou nomeia a entidade (`id=`), ou a referência de posição (`before=`,
  `after=`), ou é atômico. Não existe índice em caminho novo sobre coleção com chave.
- Chave repetida numa coleção é estado impossível, recusado na elaboração e na Publicação.
- Identificador que apareça em duas coleções do mesmo snapshot é irrelevante: a resolução é escopada
  à coleção nomeada no caminho. Unicidade global **não** é pressuposta.
- A precondição de conteúdo por hash continua valendo sobre todos os caminhos, nas duas formas.
