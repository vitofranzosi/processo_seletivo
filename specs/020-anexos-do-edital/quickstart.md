# Quickstart — verificar os Anexos do Edital

Como provar que a feature está de pé. Os sete passos do teste de aceitação da spec, cada um pelo
canal do seu ator: nada aqui se demonstra por shell ou por escrita direta no banco.

## Pré-requisitos

```bash
cd backend && uv sync
```

Banco próprio desta árvore de trabalho, para não disputar o de outra sessão:

```bash
TEST_DB_ENGINE=postgresql DB_USER="$USER" DB_NAME=test_anexos_020 uv run pytest
```

A suíte cai para SQLite em silêncio, pulando os testes que dependem de trigger e de papel, se
`TEST_DB_ENGINE` não for passado. Se aparecer `relation ... does not exist` num arquivo sorteado, o
banco está com migration por aplicar.

Interface administrativa e portal, com dados de demonstração:

```bash
uv run python manage.py migrate && uv run python manage.py seed_demo
```

```bash
INTERFACE_SELETOR_DE_IDENTIDADE=1 uv run python manage.py runserver
```

Sem o seletor de identidade ligado, `/gestao/` responde 503.

## Os sete passos

| # | Ator | Canal | O que fazer | O que provar |
|---|---|---|---|---|
| 1 | Elaborador | `/gestao/editais/<id>/compor/anexos` | Subir três PDFs, rotular, ordenar; submeter, homologar, publicar | O documento publicado lista os três; a página pública da seleção oferece os três para download |
| 2 | Autoridade | `/gestao/editais/<id>/retificar` | Substituir o artefato de um deles, com justificativa; homologar e publicar a Retificação | A versão vigente referencia o artefato novo; a anterior continua referenciando o antigo |
| 3 | Candidato | portal, fluxo de inscrição | Abrir o requisito que tem modelo | O modelo vigente é oferecido ao lado do campo de envio |
| 4 | Candidato | portal | Enviar o arquivo preenchido | Vira `DocumentoSubmetido`; nada do conteúdo é lido nem comparado |
| 5 | Banca | `/gestao/` mesa de avaliação | Abrir o requisito da inscrição | O modelo mostrado é o vigente **sob a versão aceita**, não o de agora |
| 6 | Público | `GET /api/v1/public/editais/<id>/versao-vigente?em=<instante anterior>` | Perguntar por um instante anterior ao efeito da Retificação | `attachments` traz o `artifactId` de então |
| 7 | Público | `GET /api/v1/public/anexos/<artifactId>` nos dois ids | Baixar o antigo e o novo | Bytes diferentes, `ETag` diferentes, os dois respondem 200 |

O passo 7 é o emblemático: é ele que separa esta feature de um gerenciador de arquivos, e é
exatamente o que a prática atual perde ao substituir o arquivo no mesmo caminho.

## Suítes que precisam passar

```bash
TEST_DB_ENGINE=postgresql DB_USER="$USER" DB_NAME=test_anexos_020 uv run pytest \
  tests/unit/publicacoes tests/contract tests/interface tests/portal \
  tests/authorization tests/migrations tests/acceptance/test_us_anexos.py
```

**Executado em 07/09/2026, com a feature completa**: as suítes acima passam, `migrate` e
`makemigrations --check` não acusam nada, e o `seed_demo` publica dois Anexos — a autodeclaração,
que é modelo do requisito de todos, e a anuência da chefia —, com os dois artefatos congelados pela
publicação. A demonstração pelo navegador não foi feita nesta sessão: o `preview` desta árvore de
trabalho serve o checkout principal, e não este.

Os alarmes abaixo pertencem ao percurso da implementação. Ficam registrados porque quem repetir a
fase os encontrará na mesma ordem, e nenhum deles é regressão:

- `tests/contract/test_forma_publicada.py` — a coleção nova não tem esquema no contrato, e o
  snapshot de um Edital publicado de verdade não a emite;
- os testes que afirmam a versão canônica vigente por literal — `test_elevacao_degrau_8`,
  `test_forma_publicada`, `test_contrato_de_inscricao`, `test_elevacao_de_versao`,
  `test_quickstart` e `test_elevacao` das avaliações —, que sobem de 8 para 9 junto com o degrau;
- `tests/migrations/test_migrations.py` — o guarda que conta migrations por app, que sobe de 11
  para 13 em `editais` com a justificativa ao lado;
- `tests/unit/interface/test_revisao.py` — a coleção nova não está declarada na tela de revisão.

**`tests/contract/test_documento_publicado.py` não está nesta lista, e é de propósito.**
`snapshot_publicado.json` é um literal congelado — está em `schemaVersion: 7` — e não acompanha
`SCHEMA_VERSION`. A fixture de bytes só muda quando a **composição** do documento muda, que é a
T027, e regenerá-la antes disso apagaria a evidência que ela guarda.

## O que **não** deve funcionar

Verificações negativas, tão parte da entrega quanto as positivas:

- baixar artefato de Edital não publicado pela rota pública devolve **404**, e não 403;
- publicar Edital cujo requisito aponta anexo removido é recusado com erro impeditivo que nomeia o
  vínculo;
- alterar ou apagar artefato congelado é recusado **pelo banco**, e não pela aplicação;
- remover o quarto de seis anexos não muda o rótulo de nenhum dos outros cinco;
- retificar por posição — `/attachments/3` — é recusado; só `id=<uuid>` é aceito.
