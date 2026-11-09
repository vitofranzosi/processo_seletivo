# Quickstart: conferir o Centro de Controle

## Preparação

```bash
cd backend
uv sync --extra dev --extra navegador
uv run playwright install chromium
```

Um banco próprio desta worktree (o `.env` dela tem `DB_NAME=ps136`), preparado como o README manda
(`make preparar`), e os cenários de treinamento carregados com a chave ligada:

```bash
CENARIOS_DE_TREINAMENTO=true SORTEIO_FONTE_DE_DEMONSTRACAO=true uv run python manage.py carregar_cenarios_de_treinamento --cenario C06 C08 C12 --banco ps136
```

Suba o servidor pela entrada `centro-136` do `.claude/launch.json` (porta 8136, seletor ligado).

## O que conferir

1. Entre como `treino.presidencia` (sem papel) e abra o Edital do C06 pelo detalhe; siga
   "Centro de Controle".
   - "Onde estamos" e o mapa sem rolar; Classificação *Em curso* com "1 sua".
   - "Sua próxima ação · Classificação": **Fixar os participantes**, "Por que esta", e "Esperam por
     ela: Obter a semente pública → Realizar o sorteio".
   - Avaliação diz que é paralela ao sorteio.
2. No C12, a mesma pessoa: nenhum destaque, e a frase "o GPS não escolhe a ordem entre elas". Clique
   em Classificação no mapa: o cartão dela muda de realce; a Convocação continua *Em curso*.
3. No C08: o destaque é "Classificar a lista". Com a `135` na `main`, a providência diz que a lista
   PPP não tem inscritos.
4. Troque para o Publicador (papel `publicador`): nenhuma seção "Onde cada lista está", e o detalhe da
   fase diz que o detalhe por lista é de quem conduz ou audita.
5. Troque para o Gestor (`gestor`): Encerrar e Cancelar num bloco recolhido no fim.
6. A 375 px: o mapa vira lista, nada rola na horizontal, e o console não registra violação de CSP.

## Testes

```bash
cd backend && make lint check test-pg
```

Os desta spec, sozinhos:

```bash
PYTEST_ADDOPTS="tests/unit/interface/test_centro_composicao.py tests/interface/test_centro_do_edital.py tests/integration/treinamento/test_centro_nos_cenarios.py tests/performance/test_centro_em_escala.py tests/navegador/test_jornada_do_centro.py -q" make test-pg PYTEST_WORKERS=0
```
