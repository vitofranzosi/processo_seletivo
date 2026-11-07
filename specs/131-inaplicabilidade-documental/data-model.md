# Data Model: A inaplicabilidade documental tem fundamento publicado

**Feature**: [spec.md](spec.md) · **Pesquisa**: [research.md](research.md)

Uma coluna nova no rascunho, uma chave nova no conteúdo publicado, nenhuma tabela nova e nenhum campo
novo nas tabelas append-only. O resto é regra de comando e projeção.

## 1. Documento Exigido — a condição de exigência

| Camada | Nome | Tipo | Regra |
|---|---|---|---|
| Rascunho | `DocumentoExigido.condicao` | `TextField(blank=True, default="")` | aparado; vazio = sem condição |
| Publicado | `requiredWhen` | texto ou `null` | `null` quando vazio; **sempre presente** (R-002) |
| Esquema | `DocumentoExigidoPublicado.requiredWhen` | `string`, `nullable`, máx. 300 | `required` como os demais campos |
| Mutabilidade | — | **retificável** | alcança as chamadas seguintes (FR-4456) |
| Elevação | degrau 19 | `{"requiredWhen": None}` | aditivo, sem invenção (R-003) |

**Validação** (`problemas_da_condicao`, rascunho e publicação, código
`document_requirement_condition_incoherent`, impeditivo):

| Documento | Condição | Resultado |
|---|---|---|
| obrigatório, `AT_CALL` | qualquer texto até 300 | aceito: **condicional** |
| obrigatório, `AT_CALL` | vazia | aceito: **incondicional** |
| facultativo, qualquer momento | texto | **impede** (FR-4453) |
| qualquer, `AT_ENROLLMENT` | texto | **impede** (FR-4453) |

## 2. As quatro figuras

| Figura | Representação | Derivação |
|---|---|---|
| A — excluído pelo recorte | `ItemDaListaDaConvocacao.situacao = NAO_SE_APLICA` | `aplicabilidade(...)` no ato de convocar (FR-3572 da `115`) |
| B — incondicional | item `OBRIGATORIO`, requisito da versão do item com `requiredWhen` nulo ou ausente | leitura da versão |
| C — condicional | item `OBRIGATORIO`, requisito da versão do item com `requiredWhen` texto | leitura da versão |
| D — dispensa excepcional | **nenhuma** | — |

Item `FACULTATIVO` não é figura desta spec: não tem condição nem *"não se aplica"*.

## 3. Os resultados admitidos por figura (o contrato de estados da conferência)

| Item | Apresentação vigente | *conforme* | *pendente* | *não se aplica* |
|---|---|---|---|---|
| A (fora do recorte) | nunca há | **inexistente** (404) | **inexistente** (404) | **inexistente** (404) |
| B (incondicional) | não | recusa `conforme_sem_apresentacao` | motivo com conteúdo | recusa `nao_se_aplica_sem_condicao` |
| B (incondicional) | sim | exige abertura | motivo com conteúdo | recusa `nao_se_aplica_sem_condicao` |
| C (condicional) | não | recusa `conforme_sem_apresentacao` | motivo com conteúdo | motivo com conteúdo |
| C (condicional) | sim | exige abertura | motivo com conteúdo | **exige abertura** e motivo com conteúdo |
| facultativo | não | recusa `conforme_sem_apresentacao` | motivo com conteúdo | recusa `nao_se_aplica_sem_condicao` |
| facultativo | sim | exige abertura | motivo com conteúdo | recusa `nao_se_aplica_sem_condicao` |

**Ordem das recusas no comando**, a primeira que se aplicar:

1. o resultado fora dos três;
2. o item inexistente, **ou fora do recorte** (FR-4464);
3. a autorização (FR-3595 da `115`);
4. o Processo em estado final;
5. a chamada fechada;
6. a versão superada;
7. `nao_se_aplica_sem_condicao`;
8. o *conforme* sem apresentação ou sem abertura;
9. o *"não se aplica"* sem abertura;
10. o motivo ausente;
11. `motivo_sem_conteudo`;
12. o motivo de substituição (FR-3586 da `115` e FR-4462).

**Substituição** (FR-4462): o motivo de substituição é exigido quando há conferência anterior **e**
(a anterior ou a nova é *"não se aplica"*, **ou** as duas julgam a mesma apresentação).

## 4. O estado do item e o que atende

`estado_do_item` não muda: *não se aplica* continua o estado da conferência vigente *"não se aplica"*.
Muda o que **atende** (FR-4470):

| Estado do item | Figura | Atende ao aceite |
|---|---|---|
| *conforme* | B ou C | sim |
| *não se aplica* | C | sim, **com ciência** (FR-4468) |
| *não se aplica* | B (gravado antes da feature) | **não** (11ª decisão) |
| demais | qualquer | não |

## 5. A ciência

`assinatura_das_inaplicabilidades(convocacao_id, ids)` =
`canonical_sha256({"gesto": "inaplicabilidades", "convocacao": id, "conferencias": sorted(ids)})`.

`ids` são as conferências vigentes *"não se aplica"* dos itens obrigatórios da chamada, na leitura
feita sob a trava do desfecho. Conjunto vazio: nenhuma ciência é pedida.

## 6. Rastreabilidade — o que já existe e o que falta

| Pergunta | Onde está hoje | Falta |
|---|---|---|
| Resultado | `ConferenciaDeDocumento.resultado` | — |
| Origem automática ou manual | automática: `ItemDaListaDaConvocacao.situacao`; manual: existência da conferência | só projeção: condução, formalização (FR-4466, FR-4473) |
| Fundamentação | `ConferenciaDeDocumento.motivo` + `requiredWhen` da versão do item (`item.versao`) | só projeção: página, confirmação (FR-4459, FR-4467) |
| Autor | `conferido_por`, `unidade_de_atuacao` | — |
| Momento | `conferido_em` | — |
| Documento e versão | `item`, `apresentacao`, `hash_conferido` | — |
| Relação com a exigência publicada | `item.versao` + `item.requisito_id` | — |
| Quem desfechou sabendo | **não existe** | a trilha do desfecho cita os `id` (FR-4469) |
| Trilha da conferência | `CONVOCACAO_CONFERIR`, com resultado, requisito e chamada; **sem motivo** por regra (FR-3603 da `115`) | — |

## 7. Formalização

| Situação (FR-3672 da `117`, revista) | Quando | Coluna do instante da conferência | Torna incompleta |
|---|---|---|---|
| *não se aplica* | item fora do recorte (figura A), ou documento da inscrição que não se aplica | vazia | não |
| ***não se aplica após análise*** (nova) | conferência vigente *"não se aplica"* | `conferido_em` | não |

Nenhuma coluna nova no manifesto. Nenhum motivo no manifesto (FR-3687 da `117`).

## 8. O que não muda

- As tabelas append-only da `115` (lista, apresentação, conferência), as constraints delas e os
  gatilhos.
- O desfecho e a constraint dele.
- `M` do `N de M` do provisionamento: **nenhuma tabela append-only nova**.
