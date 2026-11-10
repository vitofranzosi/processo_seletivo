# Quickstart: 143

1. Banco descartável com os cenários da `134` (ver `doc/cenarios-de-treinamento/manual-de-operacao.md`):
   `createdb ps143 && make preparar`, a autoridade da suíte e
   `CENARIOS_DE_TREINAMENTO=true manage.py carregar_cenarios_de_treinamento --banco ps143 --autoridade …`.
2. Servidor pela entrada `convocacao-143` do `.claude/launch.json` (porta 8143).
3. Passeio: `cd backend && uv run python ../specs/143-convocacao-e-documentos/passeio/passeio.py
   treino.presidencia '<passos>'` — ver `verificacao.md` para os roteiros e as capturas.
4. Esperado: o índice no alto da convocação (C10, C11, C12, C15), as vagas em dois grupos, o passo
   de cada chamada, a situação do aviso da pendência (C11, antes e depois do gesto e de
   `despachar_avisos`), e a página dos documentos com contexto, situação e navegação.
5. Verificação: `cd backend && DB_NAME=ps143_teste make lint check test-pg`.
