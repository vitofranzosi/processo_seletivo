# Quickstart: conferir o Centro como página do Edital

## Preparação

Um banco próprio desta worktree (`DB_NAME=ps138`), preparado como o README manda (`make preparar`), e
os cenários de treinamento carregados com a chave ligada. O gerador recusa sem
`ARQUIVOS_CANDIDATOS_RAIZ`, e `--banco` tem de ser o banco conectado:

```bash
cd backend
CENARIOS_DE_TREINAMENTO=true SORTEIO_FONTE_DE_DEMONSTRACAO=true ARQUIVOS_CANDIDATOS_RAIZ=/tmp/ps138-arquivos DB_NAME=ps138 uv run python manage.py carregar_cenarios_de_treinamento --banco ps138 --cenario C06 --cenario C08 --cenario C12
```

Suba o servidor pela entrada `centro-138` do `.claude/launch.json` (porta 8138, seletor ligado).

## O que conferir

1. Como `treino.presidencia`, abra o Edital do C06 pela lista de Processos.
   - A página é o Centro: "Onde estamos", o mapa, "O que fazer agora".
   - Nenhuma faixa "Em validação"; o caminho termina em "Edital N/AAAA".
   - No fim de "Administração e histórico", um link discreto para a página anterior.
2. Siga o link: a página anterior é o detalhe de antes, e o caminho termina em "Edital N/AAAA ›
   Página anterior"; "Edital N/AAAA" leva de volta ao Centro.
3. Abra `/gestao/editais/<id>/centro/?fase=classificacao`: o endereço vira
   `/gestao/editais/<id>/?fase=classificacao`, com Classificação consultada.
4. Um ato do Edital: no C12, como Gestor, encerre (ou, num Edital homologado, publique como
   Publicador). A página de chegada é o Centro, com "Ato registrado: …" no topo.
5. Um Edital em elaboração (crie um Processo novo): a página do Edital é o detalhe, com a trilha.
6. A 375 px, nada rola na horizontal, e o console não registra violação de CSP.

## Testes

```bash
cd backend && DB_NAME=ps138 make lint check test-pg
```

Os desta spec, sozinhos:

```bash
PYTEST_ADDOPTS="tests/interface/test_centro_como_pagina.py tests/interface/test_centro_do_edital.py tests/integration/treinamento/test_centro_nos_cenarios.py tests/performance/test_centro_em_escala.py -q" DB_NAME=ps138 make test-pg PYTEST_WORKERS=0
```
