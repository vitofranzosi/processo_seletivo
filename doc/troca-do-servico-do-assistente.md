# Trocar o serviço do assistente — OpenRouter ↔ Ollama

Roteiro de uma página para o piloto da [`071`](../specs/071-piloto-assistente-do-edital/quickstart.md),
na máquina da equipe. O quickstart diz **o que** cada roteiro prova (B no OpenRouter, D no Ollama da
L4); este diz **como passar de um ao outro** sem levar a configuração do anterior.

**Em produção não há troca:** `production.py` só aceita `ollama`. Este roteiro é do desenvolvimento.

## Por que um roteiro

As variáveis estão no `R-009` da `071`, os passos no quickstart e o formato do endereço nos
adaptadores. Juntá-las de cabeça erra de três jeitos, todos já vistos:

- **o `export` do serviço anterior sobrevive no shell.** Quem passa ao Ollama no mesmo terminal leva
  `ASSISTENTE_PROVEDOR`, a credencial e o `ASSISTENTE_TOKENS_POR_MENSAGEM=9`, que foi medido num
  provedor do OpenRouter. A verificação acusa a contagem divergente, mas a causa não é óbvia;
- **o endereço muda de forma entre os serviços** (abaixo);
- **o `backend/.env` ganha do `export`** (último item).

## 1. Um arquivo por serviço, fora do repositório

Os dois ficam ao lado do `tokenizer.json` e da credencial, em `~/.config/processo-seletivo/`. **Cada
um traz todas as `ASSISTENTE_*`**: quem troca não depende de lembrar o que desligar, porque a
variável que o serviço não usa vai **vazia** no arquivo dele.

**Vazia só a de texto ou a de sim/não.** As numéricas nunca: o `base.py` as converte com `int()` e
`float()`, e um valor vazio derruba a carga das settings antes de qualquer comando. Todas as
numéricas servem aos dois serviços, e por isso têm valor nos dois arquivos. Os limites repetem os
padrões do `base.py`, para que cada arquivo diga a configuração inteira; quem mudar um limite muda
nos dois.

`PREENCHER` marca o que só a equipe sabe. O que sobrar sem preencher, a verificação acusa: o
endereço não conecta, o modelo não está instalado, a quantização não confere.

`~/.config/processo-seletivo/assistente-openrouter.env`:

```bash
ASSISTENTE_PILOTO=true
ASSISTENTE_SERVICO=openrouter
# Com /api/v1: o adaptador acrescenta /chat/completions.
ASSISTENTE_ENDERECO=https://openrouter.ai/api/v1
ASSISTENTE_MODELO=qwen/qwen3.8-27b
# Lida do arquivo próprio; o valor não aparece aqui nem no histórico do shell.
ASSISTENTE_CREDENCIAL="$(cat "$HOME/.config/processo-seletivo/openrouter")"
ASSISTENTE_PROVEDOR=parasail
ASSISTENTE_ZDR=false
ASSISTENTE_TOKENIZER="$HOME/.config/processo-seletivo/qwen3.8-27b/tokenizer.json"
# Medidos no parasail, no ensaio de 14/10 (R-006 da 071).
ASSISTENTE_TOKENS_POR_MENSAGEM=9
ASSISTENTE_TOKENS_POR_CHAMADA=0
# Do Ollama: vazias.
ASSISTENTE_QUANTIZACAO=
ASSISTENTE_OLLAMA_SEM_CORTE=
# Comuns, com os padrões do base.py.
ASSISTENTE_CONTEXTO_TOKENS=32768
ASSISTENTE_SAIDA_MAXIMA_TOKENS=2048
ASSISTENTE_TEMPO_LIMITE_SEGUNDOS=90
ASSISTENTE_TEMPERATURA=0.2
ASSISTENTE_TOP_P=0.9
ASSISTENTE_SEMENTE=7
ASSISTENTE_RACIOCINIO=false
ASSISTENTE_TOLERANCIA_DE_TOKENS=0.02
ASSISTENTE_TETO_SIMULTANEO=2
ASSISTENTE_TURNOS_POR_CONVERSA=20
ASSISTENTE_PERGUNTA_MAXIMA=800
```

`~/.config/processo-seletivo/assistente-ollama.env`:

```bash
ASSISTENTE_PILOTO=true
ASSISTENTE_SERVICO=ollama
# Na raiz, sem /api: o adaptador acrescenta /api/chat, e a verificação, /api/version e /api/tags.
ASSISTENTE_ENDERECO=http://PREENCHER:11434
# O nome exato que `ollama list` mostra na L4, confirmado com quem a opera.
ASSISTENTE_MODELO=PREENCHER
# Como o Ollama a escreve, por exemplo Q4_K_M. Vazia, a verificação acusa divergência.
ASSISTENTE_QUANTIZACAO=PREENCHER
# Só true depois de quem opera a L4 confirmar que a versão instalada aceita truncate e shift (R-017).
ASSISTENTE_OLLAMA_SEM_CORTE=false
# O mesmo tokenizer se o modelo for o mesmo; outro modelo, outro arquivo.
ASSISTENTE_TOKENIZER="$HOME/.config/processo-seletivo/qwen3.8-27b/tokenizer.json"
# O padrão do base.py, até a verificação medir o da L4: ela imprime o medido contra o configurado.
ASSISTENTE_TOKENS_POR_MENSAGEM=8
ASSISTENTE_TOKENS_POR_CHAMADA=0
# Do OpenRouter: vazias.
ASSISTENTE_CREDENCIAL=
ASSISTENTE_PROVEDOR=
ASSISTENTE_ZDR=
# Comuns, com os padrões do base.py. O contexto é o primeiro valor a medir na L4.
ASSISTENTE_CONTEXTO_TOKENS=32768
ASSISTENTE_SAIDA_MAXIMA_TOKENS=2048
ASSISTENTE_TEMPO_LIMITE_SEGUNDOS=90
ASSISTENTE_TEMPERATURA=0.2
ASSISTENTE_TOP_P=0.9
ASSISTENTE_SEMENTE=7
ASSISTENTE_RACIOCINIO=false
ASSISTENTE_TOLERANCIA_DE_TOKENS=0.02
ASSISTENTE_TETO_SIMULTANEO=2
ASSISTENTE_TURNOS_POR_CONVERSA=20
ASSISTENTE_PERGUNTA_MAXIMA=800
```

**A credencial fica no arquivo dela**, `~/.config/processo-seletivo/openrouter`: uma linha, só a
chave, permissão `600`. Crie-o vazio e cole a chave pelo editor, para que ela não passe pela linha
de comando:

```bash
install -m 600 /dev/null "$HOME/.config/processo-seletivo/openrouter"
```

A chave precisa ter **limite de gasto** no painel do OpenRouter, que é a única barreira de gasto do
piloto; sem ele, a verificação acusa divergência e não manda a conversa sintética.

## 2. A cada troca, um shell novo

Feche o terminal do serviço anterior e abra outro, em `backend/`. Carregue o `.env` do banco e, por
cima, o arquivo do serviço:

```bash
set -a && . ./.env && . "$HOME/.config/processo-seletivo/assistente-ollama.env" && set +a && export DB_NAME=piloto_assistente
```

Para o OpenRouter, o mesmo comando com `assistente-openrouter.env`. O arquivo sobrescreve todas as
`ASSISTENTE_*`, mas o shell novo descarta também o que alguém exportou à mão no meio de um teste.

## 3. Verificar antes de seguir

No mesmo shell:

```bash
uv run python manage.py verificar_servico_de_inferencia
```

A primeira linha diz o serviço e o endereço em uso; a última, `Divergências: nenhuma`. **Com
divergência, o comando sai com código 1, e não se segue**: nem conversa, nem rodada, nem sessão com
o setor. Corrija o arquivo do serviço, e volte ao passo 2 — shell novo.

## 4. Reiniciar o `runserver`

As settings são lidas quando o processo sobe, e o recarregamento automático do `runserver` só olha o
código. Pare o servidor que estiver rodando, em qualquer terminal, e suba de novo **neste** shell:

```bash
make runserver DB_NAME=piloto_assistente
```

Um `runserver` esquecido no terminal antigo continua no serviço antigo, e a tela responde por ele.

## Nunca ponha `ASSISTENTE_*` no `backend/.env`

O `backend/Makefile` faz `include .env` seguido de `export`, e no `make` o arquivo **sobrepõe** a
variável do ambiente. Com uma `ASSISTENTE_*` no `.env`, o `make runserver` volta ao valor do arquivo
sem aviso, enquanto a verificação — chamada por `uv run`, fora do `make` — confere o valor do shell:
ela diz que está tudo certo com um serviço, e a tela atende por outro. A credencial tem uma razão a
mais para ficar fora dele: o `FR-1502` da `071` a quer só do ambiente, e o `.env` entra no ambiente
de todo alvo do `make` e de todo container do `docker compose`.
