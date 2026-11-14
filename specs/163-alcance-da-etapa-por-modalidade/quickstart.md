# Quickstart: O alcance da Etapa por Modalidade

Roteiro de validação. Caminhos relativos a `backend/`.

## Pré-requisitos

- PostgreSQL local e o par `TEST_DB_ENGINE=postgresql` + `DB_USER` (CLAUDE.md, *As armadilhas
  caras*); `DB_NAME` próprio desta worktree.
- `uv sync --extra dev`.

## 1. A suíte da feature

```bash
PYTEST_ADDOPTS="tests -k alcance" make test-pg PYTEST_WORKERS=0
```

Esperado: os arquivos de `plan.md` (*Source Code*) passam.

## 2. O acervo não muda (SC-2310)

```bash
PYTEST_ADDOPTS="tests/integration/publicacoes tests/unit/publicacoes -k 'elevacao or canonico or recompoe'" make test-pg
```

Esperado: os resumos canônicos e os documentos recompostos dos Editais de fixture são os de antes.

## 3. O Edital de três Perfis, à mão

Num shell (`manage.py shell`) sobre um banco de demonstração, pelos helpers dos testes
(`levar_a_publicacao`), compor o Edital da spec: C1, C2 e C3 com `AC`, `PPI` e `PcD`; Prova,
Heteroidentificação (`modalityCodes = ["PPI"]`), Análise documental (governada pelo corte) e
Entrevista. Inscrever 10 por Perfil, 4 `PPI`.

| Verificação | Esperado |
|---|---|
| Revisão e documento | a Heteroidentificação diz o alcance; as outras três, nada novo (US1) |
| Distribuição da Heteroidentificação | "12 inscrições alcançadas, de 30" (US2, UX-732) |
| Atribuir uma `AC` pelo POST | recusa com o motivo do alcance (FR-6973) |
| Análise documental com a Prova consolidada e a Heteroidentificação sem Resultado | as `AC` e `PcD` habilitadas na Prova participam; as `PPI` aguardam (US3, SC-2312) |
| Acompanhamento de uma `AC` e de uma `PPI` | a Etapa aparece só para a `PPI` (US4) |
| Retificação que tira `PPI` depois de atribuir | recusa `stage_scope_narrowed_over_assigned` (US5) |

## 4. Verificação final

```bash
cd backend && make lint check test-pg
```
