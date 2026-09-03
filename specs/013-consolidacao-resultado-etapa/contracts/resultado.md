# Contrato: Resultado da Etapa

**Feature**: `013-consolidacao-resultado-etapa` | **Spec**: [spec.md](../spec.md)

Não há superfície de API nova, e não há forma publicada nova. O ator é institucional — presidência
e auditoria — e o canal é o HTML de `interface`, como na 011 e na 012. O que este documento fixa são
as **rotas**, os **corpos aceitos**, a **forma do desfecho**, a **forma das recusas** e as
**mudanças de comportamento em rotas que já existem**, que é onde esta feature toca terreno alheio.

---

## 1. Rotas

Duas novas, ambas penduradas no caminho que a 012 já usa para a organização do trabalho. Nenhuma
usa `etapas/` como segmento: a restrição de vocabulário da 011 continua valendo.

| método | caminho | ator | o que faz |
|---|---|---|---|
| `POST` | `editais/<edital_id>/distribuicao/<etapa_id>/consolidar` | preside | o lote (FR-018) |
| `GET` | `editais/<edital_id>/distribuicao/<etapa_id>/resultados` | preside, audita | Resultados da Etapa, paginados, com proveniência (US4) |

E uma que **muda de conteúdo sem mudar de caminho**:

| método | caminho | mudança |
|---|---|---|
| `GET` | `editais/<edital_id>/distribuicao/<etapa_id>` | o resumo passa a declarar participação e prontidão; a listagem ganha o filtro de prontidão (D-004) |

---

## 2. Corpos aceitos

### `POST .../distribuicao/<etapa_id>/consolidar`

```text
inscricao_id     um ou vários
idempotency_key  obrigatório
```

Uma submissão, N Resultados. Não há campo de pontuação, de consequência nem de justificativa: a
presidência confirma um cálculo, não o informa (FR-016, FR-017). Um corpo que trouxesse nota seria
recusado como campo desconhecido, e não ignorado silenciosamente.

Seleção vazia é **erro sobre o pedido** — `selecao_vazia`, 422 —, e não um lote de zero itens: a
tela não deveria tê-lo oferecido, e responder "0 consolidadas" afirmaria um ato que não aconteceu.
É a mesma classificação que a distribuição da 012 faz.

### `GET .../distribuicao/<etapa_id>/resultados`

```text
pagina        opcional
consequencia  opcional: habilitada | eliminada
```

Sem construtor de consulta. Duas perguntas, que são as que a operação faz.

---

## 3. A forma do desfecho

A de `resultado_declarado(criados, recusas, "consolidada")`, sem variante:

```text
{
  "feitas": 973,
  "verbo": "consolidada",
  "recusadas": 27,
  "ids": ["<uuid do Resultado>", ...],
  "motivos": [{"inscricao": "<protocolo>", "motivo": "<frase>"}, ...],
  "agrupados": [{"motivo": "<frase>", "inscricoes": ["<protocolo>", ...]}, ...]
}
```

`agrupados` é o que a tela mostra: vinte e sete recusas por três causas são três linhas, e não vinte
e sete repetições da mesma frase. Os números do exemplo respeitam o teto de mil inscrições por envio
declarado em SC-002. O desfecho é **serializável de propósito** — fica no
`result_payload` da reserva, e a repetição da mesma chave o devolve inteiro (FR-021, FR-022).

---

## 4. A forma das recusas

Recusa **de item**, dentro de um lote que segue: cada uma nomeia sua causa em frase exibível, e a
lista de causas é fechada (FR-012).

| causa | frase |
|---|---|
| sem conclusão elegível | "ainda não há avaliação concluída para esta inscrição" |
| conclusões demais | "há N avaliações concluídas onde o Edital prevê uma" |
| incompatibilidade normativa | "a avaliação foi concluída sob regra da Etapa diferente da vigente" |
| Resultado anterior ausente | "aguardando o resultado da Etapa anterior" |
| eliminada antes | "eliminada na Etapa <nome>" — a Etapa em que a eliminação ocorreu, que não é necessariamente a imediatamente anterior |
| já consolidada | "esta inscrição já possui Resultado nesta Etapa" |

Recusa **do pedido inteiro**, que impede qualquer criação (FR-019):

| código | status | quando |
|---|---|---|
| `selecao_vazia` | 422 | nenhuma inscrição enviada |
| `regra_de_combinacao_ausente` | 422 | a Etapa prevê mais de uma avaliação (FR-015) |
| `regra_insuficiente` | 422 | Etapa eliminatória sem nota mínima publicada (FR-011) |
| `inscricao_nao_consolidavel` | 422 | id enviado que não é inscrição submetida deste Edital |
| `inscricao_fora_da_etapa` | 422 | id enviado de inscrição excluída da Etapa por eliminação anterior ou por falta de habilitação |
| — | 404 | Edital, Etapa ou Processo fora do escopo do ator, ou Etapa ausente do vigente |
| — | 409 | mesma chave de idempotência com conteúdo diferente |

A distinção entre as duas classes é a mesma da 012: o que a tela não deveria ter oferecido é erro
sobre o pedido; o que o caminho normal encontra é recusa de linha.

---

## 5. O que muda em rotas da 012

Esta é a parte do contrato que exige teste de não regressão, porque altera comportamento entregue.

### `POST .../distribuicao/<etapa_id>/reabrir`

Passa a recusar com **409** quando a Avaliação fundamenta Resultado:

```text
codigo:  avaliacao_fundamenta_resultado
frase:   "Esta avaliação fundamenta o Resultado da Etapa para esta inscrição e não pode ser
          reaberta."
```

Nenhum registro é alterado antes da recusa (FR-030). A frase nomeia inscrição e Etapa e **não**
mostra pontuação — a recusa é legível por quem não pode ver a nota (FR-033).

### `POST .../distribuicao/<etapa_id>/impedimentos`

**Não** passa a recusar, e **não** passa a preservar Atribuição alguma. O impedimento continua sendo
registrado e continua inativando tudo o que alcança, inclusive a Atribuição cuja Avaliação fundamenta
Resultado — porque a cadeia de autorização não consulta Impedimento, e preservar a Atribuição
manteria o acesso da pessoa impedida à inscrição e aos documentos dela.

O que muda é só o desfecho, que passa a **declarar** o que ficou contestado:

```text
{
  "impedimento": "<uuid>",
  "pessoa": "<subject>",
  "inativadas": 4,
  "resultados_contestados": [{"inscricao": "<protocolo>", "resultado": "<uuid>"}],
  "concluidas_inelegiveis": 1
}
```

`resultados_contestados` é campo novo, e é **declaração, não decisão**: nenhum Resultado é alterado,
recalculado ou invalidado. A confirmação de alcance continua com uma lista só, e
`alcance_confirmado` não muda de forma.

### `POST .../distribuicao/<etapa_id>` — a distribuição

Passa a recusar a inscrição excluída da Etapa, e a recusa é **erro sobre o pedido** (422,
`inscricao_fora_da_etapa`), e não recusa de linha. É a mesma classificação que
`_inscricoes_atribuiveis` já aplica a inscrição não submetida, e pelo mesmo motivo: uma seleção que
a tela não deveria ter oferecido não é o caminho normal esbarrando numa regra.

### `GET minhas-etapas/...` — a Mesa, a inscrição e o documento

Três superfícies do avaliador passam a consultar o mesmo conjunto: a listagem da Mesa, a inscrição
como instrumento de trabalho com seus documentos, e a navegação de **próxima pendente** — esta
última importa porque entregaria a inscrição excluída sem que ninguém a pedisse pelo identificador.
A contagem de `Minhas Etapas` acompanha, para não anunciar trabalho que não existe mais.

### O conjunto oferecido, em todas as superfícies acima

Duas regras, e só a segunda tem gate:

1. inscrição **eliminada em qualquer Etapa anterior** está fora, sempre, mesmo que a Etapa
   imediatamente anterior ainda não tenha Resultado nenhum;
2. **depois do primeiro Resultado da Etapa imediatamente anterior**, exige-se também `HABILITADA`
   nela. Antes disso essa exigência fica dormente, e é esse gate que impede a feature de esvaziar a
   Etapa seguinte de um Edital que a V1 não consolida.

Em toda superfície do avaliador, a inscrição fora do conjunto responde **404 uniforme**, e nunca
403 — a mesma resposta que a 012 dá para inscrição não atribuída, pelo mesmo motivo (FR-038).

---

## 6. Cabeçalhos e proteção de dados

Toda resposta que carrega Resultado individual ou dado de inscrição é marcada não armazenável, pelo
mesmo utilitário que a 009 e a 012 usam (`shared/http.py`, `SEM_ARMAZENAMENTO`). O desfecho do lote
carrega **protocolos**, e nunca nome, CPF ou pontuação: quem lê o desfecho está autorizado à
operação, não necessariamente ao dado pessoal de cada inscrição (FR-039, FR-040).

---

## 7. O que este contrato não cria

Nenhum endpoint público. Nenhuma alteração no `openapi.yaml` da 001 — o Resultado é administrativo,
e publicá-lo ao candidato é decisão de outra feature (§5 da spec). Nenhuma exportação, nenhum acesso
em lote a documentos.
