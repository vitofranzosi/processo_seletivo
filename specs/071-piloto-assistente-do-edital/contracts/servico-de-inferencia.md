# Contrato — a porta do serviço de inferência e os dois adaptadores

A porta (`R-008`), a configuração (`R-009`) e o que cada adaptador manda e lê. Os nomes de campo das
APIs foram lidos na documentação oficial e no código dos serviços em 12/10/2026, e **são conferidos
de novo na implementação**: a verificação de conexão (`R-017`) é o teste deles contra o serviço real.

---

## 1. A porta

```text
conversar(mensagens, esquema, parametros) -> Devolucao
```

- `mensagens`: lista de `{"role": "system" | "user" | "assistant", "content": str}`.
- `esquema`: o do [contrato da saída](saida-do-modelo.md) §2.
- `parametros`: temperatura, `top_p`, semente, contexto efetivo, saída máxima, raciocínio.

**Uma chamada por invocação, nenhuma retentativa** (`FR-1505`).

### As falhas

| Exceção (código) | Quando | Estado da troca |
|---|---|---|
| `INDISPONIVEL` | conexão recusada, nome que não resolve, 5xx | `INDISPONIVEL` |
| `TEMPO_ESGOTADO` | `ASSISTENTE_TEMPO_LIMITE_SEGUNDOS` passou | `TEMPO_ESGOTADO` |
| `LIMITE_DO_SERVICO` | 429 | `LIMITE_DO_SERVICO` |
| `ORCAMENTO_ESGOTADO` | 402 | `ORCAMENTO_ESGOTADO` |
| `RESPOSTA_MALFORMADA` | corpo que não é JSON, ou sem os campos lidos | `RESPOSTA_MALFORMADA` |
| `NAO_CONFIGURADO` | serviço, endereço ou modelo vazios | a tela diz "o piloto não está configurado"; nenhuma troca |

A mensagem de cada exceção é composta pelo adaptador, com o código HTTP e o motivo. **Nunca** inclui
o corpo enviado, os cabeçalhos ou a credencial (`R-014`).

### A `Devolucao`

| Campo | Ollama | OpenRouter |
|---|---|---|
| `texto` | `message.content` | `choices[0].message.content` |
| `raciocinio` | `message.thinking` | `choices[0].message.reasoning` |
| `modelo` | `model` | `model` |
| `tokens_de_entrada` | `prompt_eval_count` | `usage.prompt_tokens` |
| `tokens_de_saida` | `eval_count` | `usage.completion_tokens` |
| `termino` | `done_reason` | `choices[0].finish_reason` |
| `custo` | — | `usage.cost` |
| `provedor` | — | `provider` |

`raciocinio` é descartado pela aplicação logo depois de conferido o término: não vai à tela, à
troca nem ao log (`FR-1492`).

---

## 2. O que cada adaptador manda

### Ollama — `POST {ASSISTENTE_ENDERECO}/api/chat`

```json
{
  "model": "<ASSISTENTE_MODELO>",
  "messages": [...],
  "stream": false,
  "format": {<esquema>},
  "think": false,
  "options": {
    "num_ctx": 32768,
    "num_predict": 2048,
    "temperature": 0.2,
    "top_p": 0.9,
    "seed": 7
  },
  "truncate": false,
  "shift": false
}
```

`truncate` e `shift` vão só com `ASSISTENTE_OLLAMA_SEM_CORTE` ligado, depois de quem opera a L4
confirmar que a versão instalada os aceita — a API não o informa, e a verificação de conexão os põe
na lista "a confirmar com a infraestrutura" (`R-017`);
caso contrário, ficam de fora, e a conferência da contagem (`FR-1482`) é a única proteção — o que a
verificação registra.

### OpenRouter — `POST {ASSISTENTE_ENDERECO}/chat/completions`

Cabeçalho `Authorization: Bearer <ASSISTENTE_CREDENCIAL>`.

```json
{
  "model": "<ASSISTENTE_MODELO>",
  "messages": [...],
  "stream": false,
  "max_tokens": 2048,
  "temperature": 0.2,
  "top_p": 0.9,
  "seed": 7,
  "response_format": {"type": "json_schema", "json_schema": {"name": "resposta_do_assistente", "strict": true, "schema": {<esquema>}}},
  "reasoning": {"enabled": false},
  "provider": {
    "allow_fallbacks": false,
    "require_parameters": true,
    "data_collection": "deny",
    "zdr": false
  }
}
```

- **Nenhum vetor `models`**: ele troca de modelo em erro (`FR-1499`).
- Com `ASSISTENTE_PROVEDOR`, `provider.order` leva só esse provedor, e o `allow_fallbacks: false`
  impede qualquer outro: a quantização do ensaio fica conhecida (ensaio de 14/10).
- A recusa traz, no corpo do erro, o provedor que recusou (`error.metadata.provider_name`): é o único
  campo lido dali, e vai ao log da troca, como o provedor da resposta.
- `zdr` vem de `ASSISTENTE_ZDR`. Ligado sem provedor que o ofereça para o modelo, o serviço recusa,
  e a recusa é o estado `INDISPONIVEL`, com o motivo no log.
- O contexto do provedor não se fixa; `ASSISTENTE_CONTEXTO_TOKENS` é só o orçamento da aplicação.

---

## 3. O que a aplicação confere na devolução

Na ordem, antes da conferência da saída — e cada conferência tem uma tarefa só (tasks.md: modelo na
T036, término e contagem na T045):

1. `modelo` igual a `ASSISTENTE_MODELO` — senão `MODELO_DIFERENTE`;
2. `termino` igual a `stop` — senão `INCOMPLETA`;
3. `tokens_de_entrada ≥ tokens_medidos × (1 − tolerância)` — senão `POSSIVEL_CORTE`;
4. a saída, pelo [contrato da saída](saida-do-modelo.md) §3.

---

## 4. Configuração

As variáveis e os padrões estão no `R-009`. Na produção, `ASSISTENTE_PILOTO` ligado exige
`ASSISTENTE_SERVICO = ollama` e `ASSISTENTE_TEMPO_LIMITE_SEGUNDOS ≤ 110`, e a aplicação recusa subir em
caso contrário.
