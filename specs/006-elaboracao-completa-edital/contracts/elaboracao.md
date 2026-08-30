# Contrato: Elaboração Completa do Edital

**Feature**: `006-elaboracao-completa-edital` | **Fase**: 1 | **Data**: 2026-08-30

Este documento descreve o **delta** de contrato desta feature: o que o rascunho passa a aceitar, o
que o conteúdo publicado passa a carregar e o que a Retificação passa a poder endereçar. O
`openapi.yaml` da `001` continua sendo a fonte única da API; a seção final lista o que aplicar lá.

A forma canônica dos campos não é repetida aqui — está em [data-model.md](../data-model.md). O que
este documento fixa é o **comportamento observável**: o que é aceito, o que é recusado e com que
resposta.

## 1. Rascunho — o que passa a ser aceito

Endpoint inalterado: `PUT /api/v1/editais/{editalId}/rascunho`. Continua sendo substituição total do
rascunho, e continua exigindo `expectedRevision`.

O corpo ganha duas coleções e uma correção:

| Coleção | Situação |
|---|---|
| `profiles` | inalterada em forma; **cada modalidade passa a aceitar `id` e `normativeRule`** |
| `schedule` | inalterada |
| `stages` | **nova** — Etapas de Avaliação |
| `sections` | **nova** — conteúdo das seções textuais, por chave do catálogo |

### A correção nas modalidades

Hoje o command aceita `competitionModalities` com `code`, `name`, `description` e `normativeRule`,
mas cria a modalidade **sem** o identificador recebido. Passa a criá-la com ele, como já faz com
Perfis e Eventos. O identificador recebido é verificado quanto ao pertencimento, junto dos demais.

Consequência de contrato: **a identidade de uma modalidade é estável entre gravações**. Quem lê o
rascunho e o devolve preserva as modalidades, suas regras e suas identidades.

### `sections` no rascunho

O rascunho envia apenas as seções **textuais** que tiveram o conteúdo editado, identificadas pela
chave do catálogo. Seção gerada não é enviada, e seção textual ausente significa "conteúdo padrão do
catálogo", não "seção vazia".

## 2. Recusas novas

Todas seguem o formato de problema já vigente e o mesmo mapeamento de estado.

| Situação | Código | HTTP |
|---|---|---|
| Percentual fora da faixa — nulo é aceito, zero e valores acima de cem não | `field_constraint_violated` | 422 |
| Etapa sem nome | `field_required` | 422 |
| Nota mínima negativa | `field_constraint_violated` | 422 |
| Etapa referencia Evento inexistente ou de outro Edital | `field_constraint_violated` | 422 |
| Identificador de modalidade pertencente a outro Perfil ou Edital | recusa já existente de identificadores alheios | 422 |
| Chave de seção fora do catálogo, ou de seção gerada | `field_constraint_violated` | 422 |
| Consolidação sobre conteúdo-base de outra versão canônica | código próprio de versão divergente | 409 |

A recusa de percentual e a de Etapa vivem no **domínio**, não no serializer: a interface
administrativa invoca o command diretamente e não atravessa o serializer, de modo que validar apenas
ali deixaria sem verificação justamente o canal onde o dado é digitado.

## 3. Conteúdo publicado — o que passa a carregar

`schemaVersion` passa de `1` para `2`. O conteúdo ganha `stages` e `sections`, descritos em
[data-model.md](../data-model.md).

Duas propriedades do conteúdo publicado são de contrato, e não de implementação:

**Seção gerada não carrega `content`.** Ela declara `source`, e o documento a compõe a partir da
coleção nomeada. Não há cópia do Cronograma, dos Perfis ou das Etapas como texto.

**A chave da seção é o identificador.** `sections` é endereçada por `id` como as demais coleções, e
esse `id` é a chave do catálogo — estável por construção e legível no caminho de Retificação.

## 4. Retificação — o que passa a ser endereçável

Nenhuma mudança na gramática. `/stages` e `/sections` entram no registro declarativo de coleções com
chave, e a partir daí valem as mesmas regras de sempre.

Aceito:

```text
REPLACE /stages/id=<uuid>/name
REPLACE /stages/id=<uuid>/minimumScore
REMOVE  /stages/id=<uuid>
ADD     /stages
REPLACE /sections/id=<chave>/content            # seção textual
REPLACE /profiles/id=<uuid>/competitionModalities/id=<uuid>/normativeRule/percentage
```

Recusado, e por qual mecanismo já existente:

| Caminho | Recusa | Origem |
|---|---|---|
| `/stages/0/name` | endereçamento posicional em coleção com chave | `004` |
| `/sections/id=<gerada>/content` | caminho inexistente — a seção gerada não tem esse campo | `004`, por ausência |
| `REPLACE /stages/id=<uuid>` deixando a Etapa sem nome | resultado malformado | `005` |

A terceira linha é consequência de declarar `ETAPA_PUBLICADA` em `COLECOES_PUBLICADAS`: a
verificação de forma da `005` passa a cobrir Etapas sem código novo.

## 5. Prévia do documento

Não é endpoint público. É recurso da interface administrativa, disponível a quem já tem permissão de
ver o Edital, enquanto ele está em elaboração, submetido ou homologado.

| Propriedade | Contrato |
|---|---|
| Origem | o snapshot atual do Edital, em qualquer dos três estados |
| Efeito | nenhum: não altera estado e não cria `Publicacao`, `RevisaoEdital`, `VersaoConsolidada` nem `DocumentoPublicado` |
| Identificação | marca de prévia em todas as páginas; nome de arquivo de prévia |
| Integridade | **ausente** — sem hash, sem número de publicação, sem afirmação de derivação de versão homologada |
| Equivalência | publicar em seguida, sem alterações, produz documento de mesmo conteúdo normativo |

A ausência da declaração de integridade é requisito, não omissão: um documento administrativo que
parece publicado sem ter sido é risco normativo.

## 6. Delta a aplicar no `openapi.yaml` da `001`

- `RascunhoInput`: acrescentar `stages` e `sections`; declarar `id` e `normativeRule` em
  `ModalidadeInput`.
- Esquemas de saída: acrescentar `EtapaPublicada` e `SecaoPublicada`; referenciá-los em
  `EditalPublicado`.
- `ModalidadePublicada`: declarar `id` como obrigatório.
- `schemaVersion`: passar o valor declarado de `1` para `2`.
- Respostas de erro: registrar o código de versão canônica divergente na consolidação.

Não há endpoint novo. A prévia não entra no `openapi.yaml` por não ser API.
