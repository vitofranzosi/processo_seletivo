# Contrato — cálculo, emissão e consulta da ordem

Canal HTML institucional de `interface`. Nenhuma rota de API nova.

## 1. Rotas

| Rota | Método | View | Autorização |
|---|---|---|---|
| `editais/<edital_id>/marcos/<marco_id>` | GET | `ordenacao` | presidência **ou** `auditoria:consultar` |
| `editais/<edital_id>/marcos/<marco_id>/emitir` | POST | `emitir_ordenacao` | base de gestão |
| `editais/<edital_id>/marcos/<marco_id>/atos/<ato_id>` | GET | `ato_de_ordenacao` | presidência **ou** `auditoria:consultar` |

A rota pende do Edital e do marco pelo mesmo motivo que a consequência da 013 pende da Etapa: é dali
que ela é alcançada e a autorização é a mesma (`interface/urls.py:111-112`). Consultar é de dois,
emitir é de um.

## 2. O GET do marco

Calcula e **não grava** (FR-022). Devolve, num render só:

- a ordem calculada agora, com posição, participante, pontuação combinada e modalidade declarada;
- os considerados sem posição, com consequência e motivo;
- os grupos de empate residual, identificados como tais (FR-027);
- o ato vigente, se houver, e a **divergência** entre ele e o computado, posição a posição (FR-039);
- quando o marco não existe mais no conteúdo vigente, a marca de **obsoleto e não recomputável**,
  dizendo que não há regra vigente com que comparar — e não que o ato deixou de ser reproduzível
  (FR-040, FR-041, FR-042);
- `chave_idempotencia` fresca por render, no molde de `views.py:2372-2375`.

A resposta é `marcar_como_privada`: carrega posição, pontuação e fatos de desempate.

## 3. O POST de emissão

Corpo aceito:

```
chave_idempotencia   obrigatório
motivo               obrigatório quando já existe ato vigente no marco
confirmacao_do_calculo  identidade do cálculo conferido na tela
```

**Não existe campo de posição, pontuação, desempate ou ordem.** A ausência é a regra, como em
`distribuicao.html:335-342`: quem emite confirma um cálculo, não digita um resultado.

`confirmacao_do_calculo` é o que sustenta FR-034: suceder exige que a ordem confirmada seja a
calculada depois do ato vigente, e não uma leitura anterior a ele.

**A sucessão grava linha nova.** O ato sucessor declara qual ato ele sucede e traz o motivo; nenhuma
linha anterior é tocada, e o vigente é derivado — é o ato que ninguém sucedeu (FR-032, FR-033). O
desenho não é preferência: o papel de runtime não tem `UPDATE` nas tabelas append-only
(`seguranca/papeis.py:129`).

### Desfecho

`201` com o desfecho declarado no molde de `resultado_declarado`
(`avaliacoes/application/distribuicao.py:81-95`), preservado em `result_payload` — repetir o mesmo
pedido devolve o mesmo desfecho, sem emitir de novo.

### Recusas

| Situação | Status | Motivo |
|---|---|---|
| já existe ato vigente emitido depois da leitura confirmada | 409 | emissão concorrente recusada (FR-031) |
| sucessão sem `motivo` | 422 | erro do pedido |
| sucessão sem recálculo confirmado | 422 | FR-034 |
| marco sem regra publicada vigente | 422 | não há o que executar |
| marco removido do conteúdo vigente | 422 | não há regra sob a qual emitir; o ato anterior permanece (FR-040) |
| ator sem autorização, ou escopo divergente | 404 | recusa uniforme |
| marco, Edital ou ato inexistente | 404 | recusa uniforme |

O 409 é a diferença de desenho desta feature em relação à 013: lá a concorrência resolvia por
idempotência; aqui chaves diferentes são pedidos diferentes, e a recusa nasce da unicidade sobre
`ato_anterior` — duas sucessões do mesmo ato bifurcariam a cadeia (T-002).

## 4. O GET do ato

A proveniência **inteira**, para conferência humana (FR-048): Resultados que entraram, versão
normativa que governou, e — por posição — os valores usados em cada critério de desempate, com o
critério que separou cada par de vizinhas (FR-050).

Não existe rota de "reproduzir": a reprodução é garantia verificada por teste, e transformá-la em
operação criaria autoridade para recalcular o passado (FR-047).

## 5. Trilha

Um evento por **ato**, e não por posição: `operation="CLASSIFICACAO_EMITIR"`, com
`permissao=ctx.base.permissao`, motivo obrigatório, correlação e chave de idempotência. A assinatura
de `auditar` não tem por onde pontuação caber, e a omissão serve a FR-053.

## 6. O que este contrato não cria

- rota pública, de candidato ou de consulta aberta — publicação é da 017;
- rota de corte, alvo ou progressão — é da 014;
- rota de recálculo do passado;
- alteração em rota alguma da 012 ou da 013.
