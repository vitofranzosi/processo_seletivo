# Contrato — o corte e a regra que o governa

Dois contratos, e o primeiro não é novo: a regra entra no `openapi.yaml` da `001`, nos **dois**
lugares em que o marco aparece, como `appealWindow` e `drawMethod` já estão.

---

## 1. `cutRule` no marco

### `MarcoInput` — o rascunho

```yaml
cutRule:
  type: object
  nullable: true
  required: [targetKind, tieOutcome, governedStage, continuation]
  properties:
    targetKind:    { type: string, enum: [FIXED, FROM_VACANCY_TABLE] }
    targetCount:   { type: integer, minimum: 0, nullable: true }
    surplusCount:  { type: integer, minimum: 0 }
    tieOutcome:    { type: string, enum: [ADMITS_SURPLUS, STRICT] }
    governedStage: { type: string, description: "uuid da Etapa governada, ou a palavra NONE" }
    continuation:  { type: string, enum: [ALLOWED, NONE] }
```

`targetCount` é obrigatório em `FIXED` e **recusado** em `FROM_VACANCY_TABLE`. A recusa é do domínio,
e não do serializer: a interface invoca o command diretamente, e uma validação que vivesse só no DRF
não alcançaria o caminho da tela.

`governedStage` e `continuation` **não têm default**, e a ausência de qualquer um dos dois impede a
publicação. `governedStage: "NONE"` é afirmação — o marco declara que o corte dele não alimenta Etapa
alguma —, e nunca se conclui isso de um `null`.

### `MarcoPublicado` — o snapshot

Mesma forma, com `cutRule: null` no marco que não corta. **Todo** Edital publicado antes do degrau 13
é lido assim.

**A emissão é normalizada**: `surplusCount` sai sempre, inclusive `0`, e `targetCount` sai `null` em
`FROM_VACANCY_TABLE` — nunca ausente. Duas regras idênticas gravadas com bytes diferentes fariam a
comparação de obsolescência acusar diferença onde não há, e cada falso positivo custa uma geração
sucessora emitida à toa.

### Recusas da elaboração

| Código | Quando | HTTP |
|---|---|---|
| `cut_rule_malformada` | `targetKind` ausente ou desconhecido | 422 |
| `cut_rule_com_alvo_duplicado` | `targetCount` declarado em `FROM_VACANCY_TABLE` | 422 |
| `cut_rule_com_alvo_ausente` | `targetCount` ausente em `FIXED` | 422 |
| `cut_rule_com_quantidade_negativa` | `targetCount` ou `surplusCount` < 0 | 422 |

### Achados da publicação

| Código | Quando | Classe |
|---|---|---|
| `cut_rule_sem_desfecho_de_empate` | `tieOutcome` ausente | impeditivo |
| `cut_rule_sem_etapa_governada` | nem Etapa declarada, nem `NONE` | impeditivo |
| `cut_rule_com_etapa_inexistente` | a Etapa declarada não existe na versão, ou não sucede a ordem do marco | impeditivo |
| `cut_rule_sem_politica_de_continuacao` | `continuation` não declarada | impeditivo |
| `cut_rule_sem_linha_de_quadro` | `FROM_VACANCY_TABLE` e **algum** recorte que o marco ordena sem linha | impeditivo |
| `cut_rule_em_dois_marcos_da_mesma_etapa` | dois marcos declarando governar a mesma Etapa | impeditivo |

A mensagem nomeia o marco; no caso da linha de quadro, o **recorte** que ficou sem ela; e no último,
os **dois** marcos e a Etapa disputada (`UX-025`).

---

## 2. O corte — rotas da interface administrativa

O corte pende do marco, como a ordem e o sorteio.

### `GET editais/{edital_id}/marcos/{marco_id}/corte`

Calcula e mostra. **Não grava, não emite e não substitui** (`FR-190`). Aceita `?lista=<uuid>` para o
recorte; sem ele, a ampla concorrência.

Devolve, por recorte: alvo declarado, alvo apurado e sua origem, excedente, a faixa calculada com
quem progride e quem fica fora, a última posição alcançada, o estado do corte vigente quando existe,
e a obsolescência com a causa quando houver.

| Recusa | Quando | HTTP |
|---|---|---|
| `sem_ato_vigente` | o recorte não tem ordem emitida | 409 |
| `marco_sem_regra_de_corte` | o marco não declara `cutRule` | 409 |

### `POST editais/{edital_id}/marcos/{marco_id}/corte/emitir`

```json
{ "lista": "…|null", "confirmacao": "<sha256 do cálculo conferido>", "motivo": "" }
```

`motivo` é obrigatório quando já existe geração vigente no recorte — a emissão então é **sucessão de
geração**, e alcança a raiz anterior e todas as continuações dela.

A faixa emitida é `alvo + excedente`: quem o Edital manda analisar para chamada imediata entra aqui, e
não numa continuação.

| Recusa | Quando | HTTP |
|---|---|---|
| `sem_ato_vigente` | não há ordem | 409 |
| `ato_obsoleto` | a ordem citada já está para trás (`FR-198`) | 409 |
| `empate_atravessa_o_corte` | `STRICT` e empate residual na fronteira (`FR-195`) | 422 |
| `calculo_divergente` | a confirmação não corresponde ao cálculo atual | 409 |
| `sucessao_sem_motivo` | há geração vigente e o motivo veio vazio | 422 |
| `corte_ja_emitido` | corrida: a geração já existe (`FR-201`) | 409 |
| `marco_sem_regra_de_corte` | o marco não declara `cutRule` | 409 |

A resposta é o corte criado, com `id`, universo, alvo apurado, primeira e última posição, e as
contagens.

### `POST editais/{edital_id}/marcos/{marco_id}/corte/continuar`

```json
{ "lista": "…|null", "quantidade": 10, "motivo": "indeferimento de seis inscrições da 1ª faixa" }
```

| Recusa | Quando | HTTP |
|---|---|---|
| `continuacao_nao_publicada` | a regra declara `continuation: NONE` (`FR-204`, `FR-226`) | 422 |
| `continuacao_sem_motivo` | motivo vazio (`FR-203`) | 422 |
| `continuacao_sobre_ordem_sucedida` | a ordem da faixa anterior não é mais a vigente (`FR-205`) | 409 |
| `sem_faixa_anterior` | não há geração vigente no recorte | 409 |
| `continuacao_ja_emitida` | a faixa anterior já tem continuação | 409 |

**A `quantidade` é pedida e conferida, nunca inferida.** O sistema não sabe quantas vagas foram
ocupadas, e a `FR-206` proíbe que ele decida sozinho quantos chamar.

**E a continuação admitida não tem teto numérico publicado.** O Edital diz *"até que se preencha"*, e
quantas vagas foram preenchidas é conta da `016`. O que a limita é o motivo declarado, a autorização,
a auditoria e o fim da ordem — inventar um teto aqui seria publicar norma que ninguém escreveu.

### `GET editais/{edital_id}/marcos/{marco_id}/cortes/{corte_id}`

O corte histórico, lido com os nomes da versão que ele congelou. Sucedido ou vigente, a leitura é a
mesma — é o que torna a auditoria possível meses depois.

---

## 3. Idempotência, autorização e auditoria

Os dois `POST` percorrem o `comando_de_comissao` que `emitir_ordem` já percorre:

- **idempotência** por chave, com o desfecho anterior devolvido na repetição;
- **autorização** por `classificacao:emitir`, sem permissão nova (`FR-220`);
- **auditoria** com ator, ação, recorte, ato citado, alvo apurado, quantidade alcançada, instante e
  motivo (`FR-222`).

Ler não autoriza emitir, e identificador conhecido não alcança Edital fora do escopo do ator
(`FR-221`).

---

## 4. O que este contrato não expõe

Nenhuma rota de exclusão, nenhuma de edição, e nenhum campo que afirme vaga ocupada, vaga preenchida
ou déficit (`FR-207`). A ausência é verificada por teste (`SC-066`), e é assim que a fronteira com a
`016` deixa de ser promessa de prosa.
