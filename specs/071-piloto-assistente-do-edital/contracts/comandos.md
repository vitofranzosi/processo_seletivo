# Contrato — os comandos da equipe

Três comandos de gestão e um script, todos fora da suíte, todos de uso da equipe na máquina dela
(`R-016` a `R-018`, `R-021`). Nenhum tem tela.

---

## 1. `avaliar_assistente`

```text
manage.py avaliar_assistente --saida DIR [--repeticoes 5] [--casos CA-01,CB-03,…]
                             [--deslocamento-dias N]
                             [--rodada-anterior CAMINHO] [--exportar-conversas]
```

- O gasto é limitado pela credencial no serviço, e não pelo comando (`FR-1507`, emendado em 14/10).
  Na primeira recusa do serviço pelo limite de gasto, a rodada para, e o resumo diz quantos casos
  ficaram por rodar. As trocas gravam `origem = AVALIACAO`.
- `--deslocamento-dias` aplica aos instantes e às datas esperadas dos casos o deslocamento com que o
  corpus foi publicado no banco — o número que `scripts/publicar_corpus_do_piloto.py` imprime (T048).
- O custo de cada troca não é gravado (`FR-1510`): o comando o lê da linha de log da própria troca,
  durante a rodada, só para o total do `resumo.md`.
- `--rodada-anterior` compara a impressão das fontes e a versão das instruções, caso a caso, e marca
  no `resumo.md` os de outra versão da fonte (`FR-1515`).
- Cada repetição é uma conversa nova, pela mesma `perguntar` da tela. As trocas ficam gravadas como
  as da tela, e são excluídas com elas (`R-021`).
- `--exportar-conversas` acrescenta ao diretório as conversas das sessões com o setor, do banco da
  máquina, mascaradas como estão, para a revisão. Não roda caso nenhum.

### A matriz — `duvidas/avaliacao/matriz.json`

```json
{
  "casos": [
    {
      "id": "CB-01",
      "categoria": "Continuidade",
      "edital": {"numero": "91", "ano": 2026},
      "instante": null,
      "perguntas": ["Quantas vagas tem o polo de Bom Jesus do Norte?", "E no polo de Iúna?"],
      "esperado": {"tipo": "RESPONDIDA", "valores": ["40", "28", "10", "2"], "nenhum_valor": [], "texto": "40: 28 de ampla concorrência, 10 PPI, 2 PcD; fonte do INF-IUN"}
    }
  ]
}
```

- `edital` é procurado pelo número e ano entre os publicados no banco; não achado, o caso sai "não
  rodado". Os Editais de teste têm número próprio — 901 (instrução escondida), 902 (dois canais),
  903 (cláusula dos FIC), 904 (cancelado) —, porque a unicidade de número e ano não deixa uma cópia
  do 91/2026 no mesmo banco (T048).
- `instante` nulo é o `instante_padrao` da matriz, e **não** o presente: a fonte calculada traz o
  instante da situação, e o presente mudaria a impressão das fontes a cada minuto — toda rodada
  seria "outra versão da fonte" (`FR-1515`) — e levaria os casos, com os dias, para depois do fim das
  inscrições do corpus. Os casos de fronteira dão o instante.
- `"versao:N"` é o início da vigência da N-ésima versão consolidada do Edital no banco: o instante
  real da publicação, e por isso não deslocado.
- `"rodar": false`, com o `motivo`, marca os casos que não se medem contra o serviço (`CA-30`,
  `CA-31`, `CB-09`, `CB-10`): saem "não rodados", e a suíte os cobre. `"servico"` restringe o caso a
  um serviço (`CB-11`, só no externo).
- `esperado.tipo` nulo: o tipo fica para a revisão. `esperado.estado`, quando o esperado não é
  `RESPONDIDA_E_CONFERIDA` (`CB-11`).
- `esperado.valores` e `esperado.nenhum_valor` são conferidos automaticamente, na **última**
  resposta; `esperado.texto` é para o revisor.
- `referencia_070`: nos casos das doze perguntas (`CP-<edital>-<pergunta>`, um Perfil por Edital, e a
  `P-05` com cada lista dele — uma amostra dos parâmetros, decidida na matriz), `{"pergunta": "P-03", "perfil": "INF-BJN",
  "modalidade": null}`, que liga a comparação com a resposta determinística (`R-016`).
- `CB-03` e `CB-04` pedem uma Retificação entre as perguntas, ou dois instantes. O caso declara
  `"instantes": [...]`, um por pergunta, e roda sobre um Edital cuja Retificação já está publicada
  com a vigência certa.

### A saída

| Arquivo | Conteúdo |
|---|---|
| `rodada.json` | `configuracao` (sem credencial), `commit`, `versao_das_instrucoes`, e por caso e repetição: `impressao_das_fontes`, o `instante`, as perguntas, as saídas, o estado, a conferência e as comparações automáticas. **Sem tokens, tempo nem custo por troca** (`FR-1510`): eles vão ao log e ao relatório das medições |
| `revisao.csv` | Uma linha por trecho de resposta `RESPONDIDA_E_CONFERIDA`: caso, repetição, trecho, fontes citadas com o conteúdo, e as colunas vazias `julgamento` (sustentada, sustentada em parte, não sustentada, contrária à fonte), `omissao`, `origem_da_falha` (fonte da 070, montagem, conferência, modelo, caso) e `nota` |
| `resumo.md` | Por caso: estados, tipo esperado × obtido, valores esperados presentes e ausentes, comparação com a `070`, e a marca "outra versão da fonte" quando há `--rodada-anterior`; as recusas da conferência por motivo; e os **totais operacionais** da rodada — chamadas, estados por código, custo total informado pelo serviço (`SC-560`) |

---

## 2. `verificar_servico_de_inferencia`

```text
manage.py verificar_servico_de_inferencia
```

Lê do serviço configurado o que o `R-017` lista, faz **uma** conversa sintética, e imprime:

```text
Serviço: ollama em http://…:11434
Versão do Ollama: …
Modelo configurado: qwen3.8:27b — instalado: sim
  família: …   parâmetros: …   quantização: …   contexto do modelo: …
Conversa sintética: entrada 41 tokens (medidos 33 + 2 × 4 por mensagem)  saída 12  término stop  2,8 s
ASSISTENTE_TOKENS_POR_MENSAGEM sugerido: 4 (configurado: 8)
Modelo carregado: sim, 100% na GPU (… GB)
truncate/shift: enviados (ASSISTENTE_OLLAMA_SEM_CORTE) | não enviados — a conferência da contagem é a única proteção
A confirmar com a infraestrutura: OLLAMA_NUM_PARALLEL, OLLAMA_MAX_QUEUE, OLLAMA_KV_CACHE_TYPE,
  outros serviços na GPU, modo de raciocínio em uso, rede, e se a versão instalada aceita truncate e shift.
Divergências: nenhuma
```

Sai com código 1 se houver divergência entre o serviço e a configuração. Não grava nada. São
divergências: o modelo não instalado; a quantização diferente de `ASSISTENTE_QUANTIZACAO`, ou ela
vazia; o contexto do modelo menor que `ASSISTENTE_CONTEXTO_TOKENS`; o modelo fora da GPU, no todo ou
em parte; na conversa sintética, outro modelo, término diferente de `stop`, tokens não informados, o
acréscimo por mensagem configurado menor que o medido, e a falta do tokenizer. No OpenRouter, a
chave sem limite de gasto — e, sem ele, a conversa sintética não sai, porque ela também é uma
chamada paga (`FR-1507`).

---

## 3. `excluir_registros_do_piloto`

```text
manage.py excluir_registros_do_piloto --relatorio-final-em AAAA-MM-DD
```

Recusa antes de a data mais 90 dias. Depois, apaga as trocas criadas até a data e imprime
"N trocas excluídas". Nenhuma outra tabela é tocada.

---

## 4. `backend/scripts/carga_do_assistente.py`

```text
uv run python scripts/carga_do_assistente.py --edital 92/2026 --simultaneas 1,2,4 --repeticoes 10
                                             [--carga-publica https://…/api/v1 --edital-publico <uuid>]
```

Monta as mensagens de uma pergunta fixa sobre cada Edital pela aplicação, chama o serviço
diretamente, e imprime p50 e p95 do tempo, os tokens e os términos, por nível de simultaneidade, com
os instantes de início e fim de cada nível — para casar com as leituras de GPU feitas na L4. Com
`--carga-publica`, roda o `carga_publica.py` em paralelo e imprime os dois resultados lado a lado.
