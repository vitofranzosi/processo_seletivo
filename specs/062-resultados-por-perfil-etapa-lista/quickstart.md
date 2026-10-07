# Quickstart: verificar a `062`

## Pré-requisitos

- `backend/.env` presente (copiado do checkout principal) e `uv sync --extra dev` feito.
- PostgreSQL local de pé, com `LC_ALL` exportado.
- `DB_NAME` próprio se outra suíte estiver rodando.

## 1. Os testes da feature

```bash
cd backend && make test-pg DB_NAME=ps_062 PYTEST_ADDOPTS="tests/portal/test_resultados_por_perfil.py tests/portal/test_historico_de_resultados.py tests/portal/test_prazo_recursal_publico.py tests/portal/test_resultado_publico.py"
```

Esperado: todos passando. Cobrem os cenários das US1 a US4, as invariantes do
[contrato](contracts/bloco-de-resultados.md) e o custo constante (D-011 do [research](research.md)).

## 2. A verificação completa

```bash
cd backend && make lint check test-pg DB_NAME=ps_062
```

Esperado: lint e check limpos; a suíte com os mesmos onze pulados do `AGENTS.md` e nenhuma falha.

## 3. A tela, no navegador

Com o servidor do preview, abrir a página pública de um Edital encerrado com resultado divulgado em
mais de uma lista (o seed tem resultado divulgado no segundo Edital; ver a memória "seed_demo precisa
de dois Editais").

Conferir, a 1280 × 900:

- um grupo por Perfil, com o mesmo nome e na mesma ordem da seção Vagas;
- dentro dele, o nome da etapa e as listas, cada uma com natureza e data na própria linha;
- um único "Publicações anteriores" por etapa;
- o convite depois dos grupos, com "Entrar para ver minha situação".

A 375 px: a largura de rolagem do documento igual à da tela, e natureza e data quebrando para baixo
do nome da lista.

Entrar pelo convite com uma pessoa inscrita: depois do código de acesso, a página volta ao Edital,
no bloco de resultados, e o convite passa a ser "Ver minha situação".
