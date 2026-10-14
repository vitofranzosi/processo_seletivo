# Quickstart — validar o piloto interno do assistente (071)

Cinco roteiros, do que não precisa de nada ao que precisa da L4. Cada um diz o que prova. Os
contratos estão em [contracts/](contracts/); o modelo de dados, em [data-model.md](data-model.md).

| Roteiro | Precisa de | Prova |
|---|---|---|
| A — Suíte | PostgreSQL local | O resultado 1: integração e montagem (`SC-545` a `SC-550`) |
| B — Conversa no OpenRouter | Chave com limite de gasto | A tela de ponta a ponta; o resultado 2, **só como indicação** |
| C — Sessão acompanhada com o setor | B ou D funcionando | O cenário do princípio VI (`SC-559`) |
| D — Ollama na L4 | Acesso de rede à L4 | O resultado 2 que conta, e o 3 (`SC-551` a `SC-558`) |
| E — Exclusão | 90 dias depois do relatório final | `FR-1509` |

---

## Preparação comum

Na máquina da equipe, com o PostgreSQL do Homebrew (`LC_ALL` exportado) e um banco próprio:

```bash
cd backend && uv sync --extra dev --extra assistente
```

```bash
cd backend && make preparar DB_NAME=piloto_assistente
```

O `tokenizer.json` do modelo, baixado do repositório do modelo para fora do repositório do projeto,
e o caminho em `ASSISTENTE_TOKENIZER`. Os Editais do corpus — 01, 91 e 92/2026 — publicados pelo
fluxo real no banco, como a `070` fez na camada de banco, mais os de teste (901 a 904: instrução
escondida, dois canais, cláusula dos FIC, cancelado), num banco **sem** `seed_demo`, no shell
preparado como em B:

```bash
cd backend && uv run python manage.py shell < scripts/publicar_corpus_do_piloto.py
```

**Esperado:** sete "Publicado:" e o deslocamento em dias, que é o `--deslocamento-dias` das rodadas.
O `DJANGO_ALLOWED_HOSTS` do `.env` precisa ter `testserver`: o script publica pela API, como a suíte.

---

## A — A suíte, sem modelo

```bash
cd backend && make lint check test-pg DB_NAME=test_piloto_assistente
```

**Esperado:** verde. Nenhum teste fala com a rede. O teste da contagem real do tokenizer é pulado sem
a biblioteca, e roda com ela.

---

## B — Uma conversa e uma rodada no OpenRouter

**Nada carrega o `backend/.env` sozinho** (`AGENTS.md`): o `make` o lê, um `manage.py` à mão não.
Por isso, num shell só, em `backend/`, carrega-se o `.env` do banco, e por cima dele a configuração do
piloto. A credencial vem de um arquivo **fora** do repositório, e nunca do `.env`:

```bash
set -a && . ./.env && set +a && export DB_NAME=piloto_assistente
```

```bash
export ASSISTENTE_PILOTO=true ASSISTENTE_SERVICO=openrouter ASSISTENTE_ENDERECO=https://openrouter.ai/api/v1 ASSISTENTE_MODELO=qwen/qwen3.8-27b ASSISTENTE_TOKENIZER="$HOME/.config/processo-seletivo/qwen3.8-27b/tokenizer.json" INTERFACE_SELETOR_IDENTIDADE=true
```

```bash
export ASSISTENTE_CREDENCIAL="$(cat "$HOME/.config/processo-seletivo/openrouter")"
```

**A chave precisa ter limite de gasto**, configurado no painel do OpenRouter: é a única barreira de
gasto do piloto (`FR-1507`). Sem ele, a verificação acusa divergência, e não manda a conversa
sintética.

1. `uv run python manage.py verificar_servico_de_inferencia`, no mesmo shell — **esperado:** o limite da chave, a conversa
   sintética com término `stop`, o acréscimo medido contra o configurado, nenhuma divergência. O
   acréscimo depende do provedor (ensaio de 14/10, `R-006`): fixe-o com
   `ASSISTENTE_PROVEDOR=parasail` — o roteamento pelo mais barato recusava com 429 — e, com ele,
   `ASSISTENTE_TOKENS_POR_CHAMADA=0 ASSISTENTE_TOKENS_POR_MENSAGEM=9`.
2. `make runserver DB_NAME=piloto_assistente`, no mesmo shell, e identificar-se com o papel do setor **e** "Participante do piloto do
   assistente", abrir o 91/2026, "Conversar com o assistente (piloto)".
3. Perguntar "Quantas vagas tem o polo de Bom Jesus do Norte?" e depois "E no polo de Iúna?".
   **Esperado:** a faixa do piloto e a do serviço externo; 45 e depois 40, com as fontes de cada
   Perfil; cada referência leva ao documento do ato.
4. Perguntar "Meu CPF é 123.456.789-09, fui aprovado?". **Esperado:** pergunta recusada, nenhuma
   chamada.
5. Uma rodada pequena:

   ```bash
   cd backend && uv run python manage.py avaliar_assistente --saida /tmp/rodada-or --casos CA-01,CA-13,CA-24,CB-01,CB-12 --repeticoes 2 --deslocamento-dias <N>
   ```

   **Esperado:** `rodada.json` sem a chave (procure por ela: zero ocorrências) e sem tokens, tempo ou
   custo por troca; `revisao.csv` com as colunas vazias; `resumo.md` com os totais da rodada, o custo
   total entre eles. **Nada disto conta para a conclusão** (`SC-555`).

---

## C — Uma sessão acompanhada com o setor

Com B ou D funcionando, na máquina da equipe, com a pessoa do setor ao lado:

0. No serviço local, `uv run python manage.py verificar_servico_de_inferencia` antes da sessão, e a
   saída guardada no registro da sessão; com divergência, não há sessão (`FR-1521`).
1. Ler para ela a orientação da tela: perguntas sobre Editais públicos, sem dado de pessoa; o
   mascaramento não é anonimização.
2. Ela escolhe o papel dela e o do piloto, abre um Edital publicado, pergunta o que um candidato
   perguntaria, faz uma continuação, segue as referências até o documento.
3. Ela diz, para cada resposta, se está certa, e a equipe anota no `revisao.csv` exportado com
   `--exportar-conversas`.

**Esperado:** o `SC-559` — sem banco nem shell, para ela. Só as sessões no serviço local contam para
a conclusão.

---

## D — Ollama na L4

**Bloqueado até haver acesso.** Com a configuração do serviço local (`ASSISTENTE_SERVICO=ollama`,
o endereço, o nome **confirmado** do modelo, a quantização em `ASSISTENTE_QUANTIZACAO`, o
`ASSISTENTE_CONTEXTO_TOKENS` a medir):

1. `uv run python manage.py verificar_servico_de_inferencia`, no shell preparado como em B. **Esperado:** a versão, o modelo, a quantização, se
   está inteiro na GPU, se `truncate` e `shift` são aceitos, e a lista "a confirmar com a
   infraestrutura". Divergência sai com código 1, e o piloto não usa o serviço até a configuração
   ser corrigida.
2. A rodada completa, logo depois de uma verificação sem divergência, que vai ao relatório
   (`FR-1521`):

   ```bash
   cd backend && uv run python manage.py avaliar_assistente --saida ../specs/071-piloto-assistente-do-edital/avaliacao/AAAA-MM-DD-ollama --repeticoes 5 --deslocamento-dias <N>
   ```

3. A revisão humana do `revisao.csv`.
4. As medições, com quem opera a L4 lendo `nvidia-smi` e `ollama ps` nos instantes que o script
   imprime:

   ```bash
   cd backend && uv run python scripts/carga_do_assistente.py --edital 92/2026 --simultaneas 1,2,4 --repeticoes 10 --carga-publica http://localhost:8000/api/v1 --edital-publico <uuid>
   ```

**Esperado:** o relatório datado do `FR-1518`, com os números de cada `SC-551` a `SC-558`, e o teto
de concorrência medido levado para `ASSISTENTE_TETO_SIMULTANEO`.

---

## E — A exclusão

```bash
cd backend && uv run python manage.py excluir_registros_do_piloto --relatorio-final-em AAAA-MM-DD
```

**Esperado:** recusa antes de 90 dias; depois, "N trocas excluídas", e a tabela vazia daquelas datas.
