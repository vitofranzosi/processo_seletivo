# Quickstart: conferir a 135

## A suíte

```bash
cd backend && make DB_NAME=ps135 lint check test-pg
```

Os casos desta spec, isolados:

```bash
PYTEST_ADDOPTS="tests/unit/interface/test_andamento_o_que_cada_providencia_e.py tests/integration/classificacao/test_listas_sem_concorrente.py tests/integration/treinamento/test_andamento_dos_cenarios.py -q" make DB_NAME=ps135 test-pg PYTEST_WORKERS=0
```

## No navegador, sobre os cenários da `134`

Um banco próprio, com os geradores da `134` (o roteiro completo está no
`04-prototipos.md` do estudo de 09/11, PR #439):

```bash
export LC_ALL=pt_BR.UTF-8 && createdb ps135_cenarios
```

```bash
cd backend && DB_NAME=ps135_cenarios DB_USER=$USER DB_RUNTIME_USER=$USER uv run python manage.py migrate && DB_NAME=ps135_cenarios DB_USER=$USER DB_RUNTIME_USER=$USER uv run python manage.py semear_unidades
```

Crie uma autoridade fictícia (o gerador exige uma já usada, e aceita a que se passa por extenso) e
carregue os cenários com `CENARIOS_DE_TREINAMENTO=true … carregar_cenarios_de_treinamento --banco
ps135_cenarios --autoridade <pk>`. Sirva com `INTERFACE_SELETOR_IDENTIDADE=true` e entre como
`treino.presidencia`.

| Cenário | O que conferir |
|---|---|
| C08 | "O que fazer agora" e a matriz: a ordem da PPP diz que ninguém concorreu nesta lista; a espera do definitivo diz o prazo e **não** "publique como resultado preliminar" |
| C12 | a espera do definitivo, idem; a ordem da PPP, idem |
| C04 | a ordem da PPP (com inscritos) sem menção a lista vazia |
| C06 | o resumo do Perfil diz "em aberto nos marcos"; o cartão continua com o total do Edital |
| C14 | a ordem da PPP diz que ninguém concorreu nesta lista |

Na prévia de publicação do marco do C08, a mensagem da aferição do definitivo é a de antes.
