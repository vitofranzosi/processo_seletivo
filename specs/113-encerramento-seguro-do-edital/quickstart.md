# Quickstart: validar o encerramento seguro (113)

## Pré-requisitos

- worktree com `uv sync --extra dev`, PostgreSQL de pé (`LC_ALL=C`, ver `CLAUDE.md`);
- `.env` da worktree com `DB_NAME` próprio e `POSTGRES_USER` do cluster.

## 1. A suíte da feature

```bash
cd backend && PYTEST_ADDOPTS="tests/integration/processos/test_encerramento_seguro.py tests/interface/test_confirmacao_do_encerramento.py -q" make test-pg PYTEST_WORKERS=0
```

Esperado: cada impedimento recusado sozinho (SC-1067), cancelamento aceito com tudo junto (SC-1068),
advertências iguais às providências da `099` (SC-1069), concorrência sem Edital encerrado com
impedimento (SC-1070), nenhum dado pessoal (SC-1071), tempo da confirmação (SC-1072).

## 2. A suíte inteira

```bash
cd backend && make lint check test-pg
```

Esperado: verde, com os ajustes de R-008 nos testes que encerravam com período ou prazo em curso. Se
falharem em bloco arquivos que encerram Edital, a causa é a fixture (o período dela) e não o diff
— a memória "regra impeditiva quebra a suíte em bloco".

## 3. Pela interface

1. Banco de demonstração isolado: `createdb ps_113_demo`, `migrate`, `semear_unidades`, `seed_demo`
   (com `DB_NAME=ps_113_demo DB_USER=$USER DB_RUNTIME_USER=$USER`).
2. Entrada temporária no `.claude/launch.json` apontando para esse banco, com
   `INTERFACE_SELETOR_IDENTIDADE=true`; desfazer depois (o arquivo é versionado).
3. Entrar como `gustavo.gestor` e abrir `/gestao/editais/<51/2026>/atos/encerrar`.
   Esperado: "1 convocação aguarda resposta…" entre as que continuam; resultado definitivo não
   publicado; botão de confirmar presente.
4. Abrir `/gestao/editais/<01/2026>/atos/encerrar` (período em curso no seed).
   Esperado: impedimento do período, caminho "Retificar" só para quem pode retificar, sem "Confirmar".
5. Abrir a mesma tela em `cancelar`. Esperado: o período aparece em "Serão atingidos", e o botão está
   presente.
6. Encerrar o 51/2026 e emitir o Relatório do Edital: as providências dele são as advertências do
   passo 3.

## 4. Pelo serviço

`POST /api/v1/admin/editais/<01/2026>/encerramentos` com motivo → 409 `pendencias_impeditivas`, e
`GET` do Edital mostra a mesma `revision`.
