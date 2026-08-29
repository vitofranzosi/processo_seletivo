# Quickstart: Endereçamento Normativo por Chave Estável

**Feature**: `004-enderecamento-normativo-estavel` | **Fase**: 1 | **Data**: 2026-08-29

Como validar o que esta feature entrega. Cada seção diz o que rodar e **o que precisa acontecer** —
não "deve funcionar", mas o resultado exato. Detalhes de gramática estão em
[contracts/enderecamento.md](./contracts/enderecamento.md); o que muda em cada tabela, em
[data-model.md](./data-model.md).

## Pré-requisitos

A `003` aplicada, com as migrações até `publicacoes/0007` e os papéis provisionados. A conversão
desta feature consome `expected_anchors`, que a `003` grava — sem ela não há insumo.

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

## A leitura das duas formas

Sobre um Edital com Retificações publicadas **antes** da feature:

```bash
curl ".../public/editais/<id>/versao-vigente"
curl ".../public/editais/<id>/historico"
```

Esperado: idênticos ao que produziam antes. É SC-002 e SC-003 — verificáveis comparando o hash
canônico de cada Versão Consolidada antes e depois da migração, e consultando as fronteiras de
vigência, um segundo antes e um depois de cada.

Nenhum ato publicado é reescrito: `target_path` dos atos antigos continua posicional no banco.

## A conversão dos atos em curso

É a validação que mais dá errado, porque depende de dados nos três estados não finais.

Prepare, antes de migrar: uma Retificação em elaboração, uma em revisão e uma homologada, todas com
caminhos posicionais e âncoras completas; mais uma com âncora ausente ou divergente.

```bash
cd backend && DB_ROLE=migration uv run python manage.py migrate publicacoes
```

Esperado, no relatório da migração:

- as três com âncora completa: **convertidas**, mantendo o estado — a homologada continua homologada;
- a quarta: **devolvida** para elaboração, com motivo que nomeia a alteração e a condição que falhou;
- contagem **por origem**, para que ato fora das duas origens previstas apareça em vez de passar
  como sucesso.

Confira a auditoria: cada conversão registra caminho antes, caminho depois, momento e a
identificação da migração — não uma pessoa, porque não houve ato humano.

Sobre Edital sem Retificação em curso: no-op explícito, relatando zero e zero, sem falhar.

## A aposentadoria da âncora

Só depois da conversão, e sob condição comprovada:

```bash
cd backend && uv run python manage.py migrate publicacoes 0009
```

Esperado: aplica **apenas** se nenhuma Retificação em estado não final tiver `expected_anchors`
preenchido. Falha, em vez de apagar, se houver caso pendente — a evidência de que a conversão deixou
algo para trás não pode desaparecer no mesmo movimento que remove a coluna.

Depois dela, `target_identity_mismatch` não é mais emitido por caminho algum.

## A interface

```bash
cd backend && DJANGO_SETTINGS_MODULE=config.settings.development INTERFACE_SELETOR_IDENTIDADE=true uv run python manage.py runserver
```

Em `/gestao/editais/<id>/retificar`:

- **Nada muda para quem usa.** Os mesmos campos, os mesmos rótulos.
- O HTML entregue **não contém caminho normativo algum** — é uma das duas condições de FR-007.
- As alterações emitidas usam `id=`. Confira pelo detalhe da Retificação criada.

E a verificação que interessa ao código: acrescentar e remover Perfis na mesma edição, em qualquer
ordem, produz o mesmo ato. A coreografia que a `003` exigia — `REPLACE` primeiro, `REMOVE` em ordem
decrescente, `ADD` por último — deixa de ser necessária, e o teste que a exercitava deve passar sem
ela.

## O que não é verificado aqui

Desempenho da resolução por chave. A spec declara fora de escopo com justificativa: as coleções
normativas têm dezenas de elementos, e meta antes de medida seria ruído. Se um Edital com centenas
de Perfis aparecer, é aí que a pergunta passa a valer.
