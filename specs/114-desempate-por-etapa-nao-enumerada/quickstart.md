# Quickstart: Desempate pela nota de Etapa que o marco não enumera

## Pré-requisitos

PostgreSQL local com o par `TEST_DB_ENGINE=postgresql` e `DB_USER` (ver `CLAUDE.md`), e um `DB_NAME`
próprio desta worktree.

## Os testes da feature

```bash
cd backend
PYTEST_ADDOPTS="tests/integration/classificacao/test_desempate_por_etapa_nao_enumerada.py" \
  DB_NAME=ps_114 make test-pg PYTEST_WORKERS=0
```

Esperado: todos passam, e nenhum é `xfail`.

| Teste | Requisito |
|---|---|
| a nota de Etapa não enumerada desfaz o empate (o do A11) | FR-3546, SC-1073 |
| eliminado na Entrevista continua classificado pela Prova | FR-3548, SC-1074 |
| sem nota na Entrevista, vale o "quando o valor falta" e a emissão sai | FR-3553 |
| emitir, deferir recurso na Entrevista, ordem obsoleta; sucessora inverte | FR-3549, FR-3550, SC-1075 |
| a reprodução do ato emitido não diverge | FR-3552 |
| a proveniência grava a nota da Entrevista | FR-3554 |
| a trigger recusa Resultado de Etapa não citada | FR-3551 |

A equivalência da prévia (FR-3555, FR-3556, SC-1076) está em
`tests/integration/classificacao/test_previa_equivale_ao_oficial.py`, no caso
`desempate-por-etapa-nao-enumerada`.

## A suíte inteira

```bash
cd backend && DB_NAME=ps_114 make lint check test-pg
```

## O percurso pela tela (Princípio VI)

1. Elabore um Edital com duas Etapas classificatórias, Prova e Entrevista. No marco do Perfil, enumere
   só a Prova, e acrescente o critério de desempate "Maior pontuação numa Etapa → Entrevista", com
   "quem não tem fica por último".
2. Publique, inscreva três candidatos, lance e consolide Prova (80, 80, 70) e Entrevista (70 e 90 para os
   dois primeiros).
3. Abra o marco na área de gestão: a ordem calculada põe o de 90 em 1º, o de 70 em 2º, e diz que a
   Entrevista os separou. Antes desta feature, os dois apareciam empatados em 1º.
