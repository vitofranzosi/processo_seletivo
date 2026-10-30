# Quickstart: Jornada operacional da Retificação

## Pré-requisitos

- `cd backend && uv sync --extra dev`
- PostgreSQL local (no macOS com Homebrew, com `LC_ALL` exportado)
- `INTERFACE_SELETOR_IDENTIDADE=true` para abrir `/gestao/`

## Automático

```bash
cd backend
TEST_DB_ENGINE=postgresql DB_USER=$USER DB_NAME=ret103 uv run pytest \
  tests/interface/test_jornada_da_retificacao.py \
  tests/interface/test_auditoria_passagem_da_retificacao.py \
  tests/unit/publicacoes/test_fusao_da_edicao.py \
  tests/unit/interface/test_atos_da_retificacao.py -q
```

Esperado: tudo passa, sem `xfail` no arquivo da auditoria.

## Manual (três identidades, três navegadores ou janelas anônimas)

O servidor é a entrada `retificacao-103` do `.claude/launch.json` (porta 8103, banco `ps_demo_103`,
preparado com `migrate`, `sincronizar_unidades` e `seed_demo`).

1. **Ana, elaboradora**: Lista → Edital publicado → Retificar → mude as vagas → "Ver o que vai mudar"
   → "Criar Retificação". Volte à Lista: a linha do Edital diz "Retificação em elaboração ·
   Submeter". Abra, "Editar a Retificação", mude outra vez, grave, e submeta. A confirmação diz que a
   Retificação fica aguardando quem homologa.
2. **Bruno, homologador**: Lista → a linha diz "Retificação em revisão · Homologar" → abra →
   "Devolver para elaboração" com motivo.
3. **Ana**: o detalhe mostra o motivo; "Editar a Retificação", corrija, grave, submeta.
4. **Bruno**: homologue.
5. **Carla, publicadora**: Lista → "Retificação homologada · Publicar Retificação" → publique. A
   marca some da Lista; a Retificação aparece em "Documentos publicados".
6. **Dora, com os três papéis**: componha, submeta e homologue; no detalhe, "Publicar Retificação"
   aparece desabilitado com o motivo.
