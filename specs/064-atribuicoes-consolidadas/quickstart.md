# Quickstart: conferir a consolidação das atribuições

**Feature**: [spec.md](spec.md) · **Contrato**: [contracts/documento.md](contracts/documento.md)

## 1. Os testes da feature

Contra PostgreSQL, como o repositório exige (ver as instruções do repositório, *As armadilhas
caras*), com banco próprio da worktree:

```bash
cd backend && make test-pg DB_NAME=test_ps_064
```

Para só os arquivos da feature, o `make` não repassa argumentos ao `pytest`; o alvo é a linha
dele com os arquivos no fim, e as variáveis do `.env` exportadas:

```bash
cd backend && set -a && . ./.env && set +a && TEST_DB_ENGINE=postgresql DB_NAME=test_ps_064 DB_RUNTIME_USER="$POSTGRES_USER" DB_RUNTIME_PASSWORD="$POSTGRES_PASSWORD" uv run pytest tests/unit/publicacoes/test_atribuicoes_consolidadas.py tests/contract/test_documento_publicado.py tests/integration/publicacoes/test_retificacoes.py
```

Esperado: tudo verde, e **a fixture `documento_publicado_v1.pdf` sem regeneração** — o Edital dela tem
um Perfil só (FR-1194).

## 2. A prévia, pela interface

1. Suba o ambiente com `INTERFACE_SELETOR_IDENTIDADE=true` e entre como quem elabora.
2. Num Edital em elaboração, crie três Perfis; cole o **mesmo** texto de atribuições, em várias
   linhas, nos dois primeiros, e um texto diferente no terceiro.
3. Abra **Ver o Edital**.

Esperado:

- os dois primeiros Perfis trazem **"Atribuições:** as descritas no item `{s}.4`.";
- o terceiro traz o próprio texto, como antes;
- depois do terceiro Perfil, a subseção `{s}.4` *Atribuições comuns aos Perfis A e B* traz o texto
  uma vez;
- as subseções `{s}.1` a `{s}.3`, os números das seções seguintes e as legendas de tabela são os
  mesmos de antes.

4. Acrescente uma vírgula no texto do segundo Perfil, grave e reabra a prévia: a subseção comum
   some, e os três Perfis trazem o próprio texto.

## 3. Documento já publicado

Abra o documento de uma Publicação feita antes desta feature: ele é o mesmo arquivo de antes, porque
os bytes ficam guardados e não são regerados (FR-1196).
