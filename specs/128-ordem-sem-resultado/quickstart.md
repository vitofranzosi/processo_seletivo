# Quickstart: A ordem por pontuação sem nenhum resultado é recusada (128)

## Suíte

```bash
cd backend && make lint check
```

```bash
cd backend && DB_NAME=ps_128 make test-pg
```

Os testes desta feature, isolados:

```bash
cd backend && PYTEST_ADDOPTS="tests/unit/classificacao/test_ordem_sem_resultado.py tests/integration/classificacao/test_ordem_sem_resultado.py tests/interface/test_ordem_sem_resultado.py" DB_NAME=ps_128 make test-pg PYTEST_WORKERS=0
```

## Antes e depois no navegador

O Edital 91 do estudo não está num banco disponível. O cenário equivalente — marco por pontuação com uma
Etapa enumerada, inscrições enviadas, ninguém avaliado — sai de `tests.fixtures.corte.montar_cenario_do_corte`
com `pontuacoes=()` e `emitir_a_ordem=False`, num banco descartável:

1. Num banco novo (`createdb`, `make preparar` com `DB_NAME` próprio), monte o cenário pelo shell com os
   helpers dos testes (o roteiro usado está em `verificacao.md`).
2. Suba o `runserver` da worktree com `INTERFACE_SELETOR_IDENTIDADE=true`, entre como presidência e abra
   a tela da ordem do marco.
3. **Antes** (commit da `126`): a tela oferece "Emitir ordem", e a confirmação diz "Nenhuma inscrição
   deste recorte tem resultado…" com o botão "Emitir a ordem".
4. **Depois** (esta branch): no lugar do formulário, *"A ordem ainda não pode ser emitida"*, a frase e
   o link "Distribuir <Etapa>".

As capturas ficam em `capturas/`.
