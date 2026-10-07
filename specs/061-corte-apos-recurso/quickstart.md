# Quickstart: verificar o corte emitido depois do recurso

**Feature**: [spec.md](spec.md)

## 1. A suíte

```bash
cd backend && make lint check test-pg DB_NAME=ps_061
```

Worktree nova: `uv sync --extra dev` uma vez antes. `test-pg` e não `test` (ver `CLAUDE.md`).

Os testes desta feature e os da `014` que guardam a outra cronologia, isolados:

```bash
cd backend && TEST_DB_ENGINE=postgresql DB_USER=$USER DB_RUNTIME_USER=$USER DB_NAME=ps_061 uv run pytest -q tests/integration/classificacao/test_corte_apos_recurso.py tests/integration/classificacao/test_corte_obsoleto.py
```

## 2. Num banco com o achado

Num banco em que o corte foi emitido depois da ordem sucessora por recurso — o
`ps_apresentacao_grafico` do Edital 72/2026 é um —, abra a tela de Corte da lista de ampla
concorrência do marco. Antes da correção: *"A faixa emitida está obsoleta… Um participante
reingressou"*. Depois: a faixa em dia, sem ato nenhum emitido no meio.

Pelo shell, só leitura:

```python
from processo_seletivo.classificacao.application.corte import estado_do_corte
estado_do_corte(edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=None)
# {"obsoleto": False, "causas": [], ...}
```

## 3. O que não pode ter mudado

Emita o corte, **depois** defira um recurso sobre Resultado de uma Etapa que produziu a ordem: a
faixa fica obsoleta com *participante reingressou*, a Etapa governada recusa trabalho novo com
`corte-obsoleto`, e a publicação dependente é impedida.
