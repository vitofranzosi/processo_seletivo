# Quickstart — o assistente na página do Edital (074)

Na máquina de desenvolvimento. A pergunta livre vai ao OpenRouter e **custa**: o limite de gasto da
chave, no painel dele, é a única barreira (DP-4 da `071`). As sugestões respondem sem modelo.

## Pré-requisitos

- `uv sync --extra dev --extra assistente` em `backend/` (traz a `tokenizers`).
- O `tokenizer.json` em `~/.config/processo-seletivo/qwen3.8-27b/` e a credencial em
  `~/.config/processo-seletivo/openrouter` — os dois fora do repositório, como no quickstart da `071`.

## 1. O banco

Um banco próprio, sem `seed_demo`, com o corpus do piloto:

```bash
cd backend && createdb -h localhost ps_074_local && make preparar DB_NAME=ps_074_local DB_HOST=localhost DB_PORT=5432 POSTGRES_USER=$USER POSTGRES_PASSWORD= DB_MIGRATION_USER=processo_seletivo_owner DB_MIGRATION_PASSWORD=change-me DB_RUNTIME_USER=processo_seletivo_runtime DB_RUNTIME_PASSWORD=change-me
```

```bash
cd backend && DB_NAME=ps_074_local DB_HOST=localhost DB_ROLE=runtime DB_RUNTIME_USER=processo_seletivo_runtime DB_RUNTIME_PASSWORD=change-me DJANGO_ALLOWED_HOSTS=localhost,testserver uv run python manage.py shell < scripts/publicar_corpus_do_piloto.py
```

**Esperado:** `40 de 40` na segunda provisão, e sete "Publicado:".

## 2. O servidor

A entrada `assistente-074` do `.claude/launch.json` (porta 8074) liga
`ASSISTENTE_NA_PAGINA_DO_EDITAL=true` e o OpenRouter com o provedor fixo do ensaio de 14/10. Sem
seletor de identidade e sem identidade de demonstração: a visão é a do visitante.

## 3. O percurso pelas sugestões (sem custo)

1. <http://localhost:8074/selecoes/> → "Ver a seleção" do 91/2026 (o card com `corpus-piloto-91`).
2. "Dúvidas sobre este Edital" → o painel abre, com o selo "Ambiente local de desenvolvimento".
3. "Que documentos preciso enviar?" → "Para qual opção?" → "Polo Bom Jesus do Norte".
   **Esperado:** a lista de obrigatórios, o facultativo, o que PcD e PPI acrescentam, e "Consultar
   fontes".

## 4. A pergunta livre (com custo)

4. Escreva "Preciso enviar todos?" e "Enviar". **Esperado:** "Consultando as informações deste
   Edital…" e uma resposta conferida, ou uma das três situações do painel ("não foi possível
   confirmar", "não conseguiu responder agora", "chegou ao limite"). 429 do provedor é falha do
   serviço, sem retentativa.
5. "Nova conversa" → o painel volta às sugestões; a conversa anterior continua no registro. Cada
   sessão abre até três conversas por Edital (`ASSISTENTE_CONVERSAS_POR_SESSAO`); na quarta, o
   painel diz que chegou ao limite.

## Desligar

Sem `ASSISTENTE_NA_PAGINA_DO_EDITAL=true`, a página não traz o painel e as rotas respondem 404.
Produção recusa subir com ela.
