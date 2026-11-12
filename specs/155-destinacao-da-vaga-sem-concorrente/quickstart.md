# Quickstart: verificar a 155

## Preparação

```bash
cd backend && uv sync --extra dev
```

Banco próprio da worktree (`DB_NAME` único). A suíte contra PostgreSQL pede o par
`TEST_DB_ENGINE=postgresql` e `DB_USER`, e o `make test-pg` usa `POSTGRES_USER`.

## A suíte

```bash
cd backend && make lint check test-pg
```

Os casos de cada história, por diretório, enquanto se trabalha:
- `tests/integration/ocupacao/test_destinacao*.py`;
- `tests/integration/ocupacao/test_nao_preenchida*.py`;
- `tests/interface/test_lista_sem_concorrente.py`;
- `tests/interface/test_destinacao_na_ocupacao.py`;
- `tests/portal/test_destinacao_na_selecao.py`.

## No navegador

Uma entrada própria no `.claude/launch.json`, com porta livre, `INTERFACE_SELETOR_IDENTIDADE=true`,
`CENARIOS_DE_TREINAMENTO=true` e o banco da worktree. Não sobrescreva as entradas existentes.

1. **C09 (SIM09/2026, PPP vazia, sem reversão declarada).** Carregue o cenário:
   ```bash
   uv run python manage.py carregar_cenarios_de_treinamento --banco <banco> --cenario C09
   ```
   Entre como `treino.presidencia` e confira cada passo:
   - **Ordenação da PPP**: um gesto só, "Registrar que ninguém concorreu", com a conferência. Antes
     eram três atos.
   - **Publicação do resultado da ampla**: a prévia diz que a PPP entra junto.
   - **Ocupação da PPP**: "Este Edital não declara o que acontece com a vaga reservada não
     preenchida", com dois caminhos: Retificação e declaração de não preenchida.
   - **Declarar não preenchida sem fundamento**: recusada.
   - **Declarar com fundamento**: o Centro deixa de mostrar a PPP na fase Vagas, e a página pública da
     seleção mostra a vaga como não preenchida, com o fundamento.
2. **Reversão por esgotamento.** Um Edital de teste com reversão por esgotamento e um autodeclarado
   que desiste, montado com `levar_a_publicacao` num shell. Confira:
   - a destinação é oferecida depois do desfecho;
   - o "Confira antes" mostra a frase publicada;
   - a ampla fica obsoleta e leva à emissão;
   - o desfazimento é recusado depois que a ampla chama alguém.
3. **Reversão por saldo.** O mesmo Edital com reversão por saldo: até a D-015, a tela não oferece a
   destinação e diz que a regra aguarda decisão. O comportamento antigo da emissão continua — é o
   registro do estado, e não a regra.
4. **Passagem entre cotas.** Um Perfil com a terceira resposta: a ocupação diz a limitação, e nenhum
   ato aparece.

Em cada tela: o console sem violação da CSP, a 1366 px e a 390 px.
