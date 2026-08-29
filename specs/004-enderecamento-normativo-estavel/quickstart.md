# Quickstart: Endereçamento Normativo por Chave Estável

**Feature**: `004-enderecamento-normativo-estavel` | **Fase**: 1 | **Data**: 2026-08-29

Como validar o que esta feature entrega. Cada seção diz o que rodar e **o que precisa acontecer** —
não "deve funcionar", mas o resultado exato. Detalhes de gramática estão em
[contracts/enderecamento.md](./contracts/enderecamento.md).

## Pré-requisitos

A `003` aplicada, com as migrações até `publicacoes/0007`.

```bash
cd backend && TEST_DB_ENGINE=postgresql DB_NAME=processo_seletivo_test DB_USER=postgres DB_PASSWORD=postgres uv run pytest
```

Esperado antes de começar: suíte verde, zero ignorados no PostgreSQL, zero `ResourceWarning`.

## O ganho: duas pessoas em Perfis diferentes

É o que a `003` não podia entregar, e o motivo da feature existir.

1. Publique um Edital com três Perfis.
2. Elabore a Retificação **A**: renomeia o Perfil 2.
3. Elabore a Retificação **B**, sobre a mesma versão: remove o Perfil 1.
4. Publique **B**, depois **A**.

Esperado: **as duas publicam**. Na `003`, A seria recusada com `409 target_identity_mismatch` mesmo
sem ninguém ter tocado no Perfil dela. O conteúdo vigente ao fim tem dois Perfis, e o renomeado é o
que era o Perfil 2.

Repita com A e B alterando **o mesmo campo do mesmo Perfil**. Esperado: a segunda é recusada com
`409 expected_hash_mismatch` — a precondição por hash continua sendo a defesa contra isso, e não
saiu junto com a âncora.

## A escrita posicional deixa de nascer

```bash
curl -X POST .../retificacoes -d '{"changes":[{"targetPath":"/profiles/0/name","operation":"REPLACE","newValue":"X"}]}'
```

Esperado: `422 positional_addressing_refused`, nomeando `/profiles/0/name`. A recusa é na
**elaboração** — o ato não chega a existir.

O mesmo caminho numa coleção **sem** chave é outro caso: `requirements` é atômica, então
`REPLACE /profiles/id=…/requirements` com a lista inteira é o ato válido, e endereçar
`/requirements/2` é recusado por não ser forma admitida.

## As formas admitidas

```
/profiles/id=<uuid>/name                                    → REPLACE, REMOVE
/profiles/id=<uuid>/competitionModalities/id=<uuid>/name     → aninhado
/profiles/-                                                 → ADD, ao fim
/profiles/id=<uuid>/requirements                            → REPLACE da lista inteira
```

Esperado: `id=` com valor que não seja UUID é recusado. `id=` sobre um objeto é nome de chave
literal, não seletor — uma chave chamada `id=algo` continua endereçável.

Não há inserção em posição: acréscimo vai para o fim, e é a única forma de `ADD`.

## A remoção da âncora

```bash
cd backend && DB_ROLE=migration uv run python manage.py migrate publicacoes
```

Esperado: `0008_remover_ancoras` aplica sem conversão de dados e sem condição a comprovar. Depois
dela, `expected_anchors` não existe no esquema e nenhum código a referencia — inclusive
`target_identity_mismatch`, que deixa de ser emitido por caminho algum.

```bash
cd backend && grep -rn 'expected_anchors\|target_identity_mismatch' processo_seletivo/ | grep -v migrations/
```

Esperado: nenhuma linha.

## A interface

```bash
cd backend && DJANGO_SETTINGS_MODULE=config.settings.development INTERFACE_SELETOR_IDENTIDADE=true uv run python manage.py runserver
```

Em `/gestao/editais/<id>/retificar`:

- **Nada muda para quem usa.** Os mesmos campos, os mesmos rótulos.
- O HTML entregue **não contém caminho normativo algum** — é uma das duas condições de FR-019.
- As alterações emitidas usam `id=`. Confira pelo detalhe da Retificação criada.

E a verificação que interessa ao código: acrescentar e remover Perfis na mesma edição, em qualquer
ordem, produz o mesmo ato. A coreografia que a `003` exigia — `REPLACE` primeiro, `REMOVE` em ordem
decrescente, `ADD` por último — deixa de ser necessária, e o teste que a exercitava deve passar sem
ela.

## O que não é verificado aqui

Desempenho da resolução por chave. A spec declara fora de escopo com justificativa: as coleções
normativas têm dezenas de elementos, e meta antes de medida seria ruído.
