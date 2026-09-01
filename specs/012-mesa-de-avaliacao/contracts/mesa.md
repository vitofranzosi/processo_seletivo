# Contrato: Mesa de Avaliação

**Feature**: `012-mesa-de-avaliacao` | **Spec**: [spec.md](../spec.md)

Não há superfície de API nova. Os dois atores são institucionais e o canal é o HTML de `interface`,
como na 011. O que este documento fixa são as **rotas**, os **corpos aceitos**, a **forma das
recusas** e a **forma publicada nova** — porque essa última é contrato de verdade, conferido por
teste contra o `openapi.yaml` da 001.

---

## 1. Rotas

| método | caminho | ator | o que faz |
|---|---|---|---|
| `GET` | `editais/<edital_id>/distribuicao/<etapa_id>` | preside | organização do trabalho: carga por pessoa, déficit por inscrição, invalidadas |
| `POST` | `editais/<edital_id>/distribuicao/<etapa_id>` | preside | o lote (FR-013) |
| `POST` | `editais/<edital_id>/distribuicao/<etapa_id>/remover` | preside | retirar Atribuição sem Avaliação concluída |
| `POST` | `editais/<edital_id>/impedimentos` | preside | registrar impedimento (FR-039) |
| `POST` | `avaliacoes/<avaliacao_id>/reabrir` | preside | reabrir, com motivo (FR-036) |
| `GET` | `minhas-etapas/<edital_id>/<etapa_id>` | avalia | **a Mesa** — a página que a 011 deixou com o aviso |
| `GET` | `minhas-etapas/<edital_id>/<etapa_id>/inscricoes/<inscricao_id>` | avalia | a inscrição como instrumento de trabalho |
| `GET` | `.../inscricoes/<inscricao_id>/documentos/<requirement_id>` | avalia | o documento, mediado e conferido |
| `POST` | `.../inscricoes/<inscricao_id>/avaliacao` | avalia | gravar rascunho |
| `POST` | `.../inscricoes/<inscricao_id>/avaliacao/concluir` | avalia | concluir (FR-032) |

**Vocabulário.** Nenhuma rota usa `etapas/` como segmento — a palavra já significa "passo do
compositor" em `editais/<id>/compor/<slug:etapa>`, e a 011 fixou essa restrição. O caminho
`minhas-etapas/<edital>/<etapa>` **não muda**: muda o nome interno da view e do reverse, de
`atribuicao` para `minha_etapa`, porque `Atribuição` passou a ser entidade (T-012).

---

## 2. Corpos aceitos

### `POST editais/<id>/distribuicao/<etapa_id>`

```text
membro_id        um ou vários
inscricao_id     um ou vários
idempotency_key  obrigatório
```

Uma submissão, N atribuições. As duas formas que a tela oferece — muitas inscrições para um
avaliador, ou um conjunto repartido entre vários — são o mesmo corpo. Nenhuma variante aceita uma
atribuição por submissão como caminho normal (FR-047).

### `POST editais/<id>/impedimentos`

```text
membro_id, inscricao_id, motivo (obrigatório), idempotency_key (obrigatório)
```

### `POST editais/<id>/distribuicao/<etapa_id>/remover`

```text
atribuicao_id (um ou vários), idempotency_key (obrigatório)
```

### `POST .../avaliacao` e `.../avaliacao/concluir`

```text
pontuacao, parecer, expected_revision (obrigatório)
```

`expected_revision` viaja no formulário e é a precondição de FR-081. A conclusão aceita ainda o
reconhecimento explícito da mudança de versão quando houver (FR-073).

### `POST avaliacoes/<id>/reabrir`

```text
motivo (obrigatório), expected_revision (obrigatório), idempotency_key (obrigatório)
```

**`idempotency_key` é obrigatória nos quatro comandos que passam por `comando_de_comissao`** — o
lote, a remoção, o impedimento e a reabertura —, porque a reserva é parte do invólucro e não um
extra da rota mais movimentada. Reenviar qualquer um deles devolve o desfecho original, sem ato novo
e sem evento novo (FR-084, FR-086).

A gravação e a conclusão da Avaliação **não** levam chave de idempotência: são linha própria do
avaliador, protegidas por `expected_revision`, e reenviar com revisão obsoleta é recusa, não
repetição (FR-081).

---

## 3. Respostas

| situação | resposta |
|---|---|
| ator sem alocação na Etapa | **404**, pela convenção do projeto (FR-044) |
| alocado, sem Atribuição, abrindo a **Mesa** | **200**, lista vazia (FR-023) |
| alocado, sem Atribuição, abrindo **uma inscrição** | **404** |
| Atribuição de outra pessoa, por troca de UUID na URL | **404** (FR-045) |
| escopo institucional divergente | **404** |
| revisão obsoleta ao gravar ou concluir | recusa por precondição, com a mensagem dizendo o que mudou (FR-081, FR-082) |
| chave de idempotência repetida, mesmo conteúdo | desfecho original, sem atribuição nem evento novos (FR-084) |
| chave repetida, conteúdo diferente | conflito (FR-084) |
| impedimento, teto atingido, já atribuída | **linha recusada, lote prossegue** (FR-085) |
| Etapa inexistente, avaliador sem alocação, inscrição de outro Edital ou não submetida | **lote inteiro recusado** (FR-085) |
| pontuação acima da máxima publicada | recusa nomeando o limite (FR-033) |
| pontuação abaixo da mínima | **aceita**; torna o parecer obrigatório (FR-033, FR-034) |
| conclusão fora do período previsto | **aceita**, com aviso antes (FR-077, FR-095) |
| remover Atribuição com Avaliação concluída | recusa nomeando os atos que teriam esse efeito (FR-092) |
| divergência de integridade no documento | recusa registrada, como já é na consulta administrativa (FR-029) |

Toda resposta com dado pessoal é marcada como não armazenável pelo navegador (FR-056).

**O resultado do lote é declarado, não inferido** (FR-097): quantas atribuídas, quantas recusadas, e
o motivo de cada recusa nomeando a linha.

---

## 4. A forma publicada nova

Contrato de verdade, e o único desta feature que é conferido por teste automatizado contra
`specs/001-processo-seletivo-editais/contracts/openapi.yaml`.

`EtapaPublicada`, versão canônica **5**, ganha:

```yaml
evaluationsPerRegistration:
  type: [integer, 'null']
  minimum: 1
maximumScore:
  type: [string, 'null']
  format: decimal
  pattern: '^-?(0|[1-9]\d{0,2})\.\d{4}$'
```

`EtapaInput` ganha os dois correspondentes na elaboração, e ali eles são **opcionais** — como
`weight` e `minimumScore` já são. A assimetria é deliberada e é a mesma que o contrato já pratica: o
rascunho admite o Edital pela metade, e o **publicado** exige forma completa. `required` de
`EtapaPublicada` passa a incluí-los, com `null` significando "não declarado".

A faixa — quantidade maior que zero, máxima maior que zero, mínima não superior à máxima — é regra
de domínio, verificada no command que os dois canais atravessam, e não só no serializer da API nem
só no `CheckConstraint`.

**Leitura da ausência**: conteúdo em versão anterior não carrega as chaves. `null` e ausência têm o
mesmo significado, e ele está em um lugar só (`avaliacoes_previstas`, `pontuacao_maxima`).

**Elevação**: conteúdo de versão anterior, ao ser carregado para compor ou consolidar Retificação, é
elevado por função pura — sem escrever linha, sem alterar hash gravado, sem criar proveniência
(T-001). A Publicação original continua sendo byte a byte o que foi publicado.

---

## 5. O que esta feature promete **não** oferecer

- Nenhum endpoint que devolva o acervo de um Edital, em lote ou paginado, para avaliador.
- Nenhuma rota de download múltiplo, exportação ou zip (FR-028).
- Nenhum campo de média, quórum, divergência, situação, apto ou inapto — em resposta alguma
  (FR-037, SC-013).
- Nenhuma rota que distribua automaticamente (FR-017).
- Nenhuma alteração nas rotas da 009 e da 011, além do nome interno de T-012.

---

## 6. O contrato que a 013 herda

```text
avaliacoes_elegiveis(edital, etapa_id, inscricao_id) ->
    Avaliações CONCLUIDA, sob Atribuição ativa,
    cada uma com autoria, instante e a VersaoConsolidada que a governou.
```

O que está fora desse conjunto está fora por **ato nomeado, com autor e motivo** — nunca por efeito
colateral de reorganizar o trabalho (FR-092, FR-093). É essa garantia, e não a existência da tabela,
que a 013 recebe.
