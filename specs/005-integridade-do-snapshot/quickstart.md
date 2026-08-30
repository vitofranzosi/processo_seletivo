# Quickstart: Integridade do Snapshot Normativo

**Feature**: `005-integridade-do-snapshot` | **Fase**: 1 | **Data**: 2026-08-29

Como validar o que esta feature entrega. Cada seção diz o que rodar e **o que precisa acontecer** —
não "deve funcionar", mas o resultado exato. As quatro dimensões e os dois momentos estão em
[contracts/integridade.md](./contracts/integridade.md); a forma declarada, em
[data-model.md](./data-model.md).

## Pré-requisitos

A `004` integrada — a `main` a partir de `ad983da`.

```bash
cd backend && TEST_DB_ENGINE=postgresql DB_NAME=processo_seletivo_test DB_USER=$USER DB_PASSWORD= uv run pytest
```

Esperado antes de começar: suíte verde e zero `ResourceWarning`. No PostgreSQL fica **um** ignorado
— `test_database_permissions.py`, cuja recusa por vendor só existe fora do PostgreSQL.

## O defeito, antes de corrigi-lo

Vale rodar isto primeiro: é o que a feature fecha, e serve de linha de base.

```bash
cd backend && uv run python - <<'PY'
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")
django.setup()
from processo_seletivo.publicacoes.domain.changes import apply_change
from processo_seletivo.editais.domain.validation import validate_for_publication, blocking_findings
from tests.fixtures.snapshot import PERFIL, conteudo_normativo
alvo = f"/profiles/id={PERFIL['C']}"
for rotulo, ch in [
    ("REPLACE parcial", {"targetPath": alvo, "operation": "REPLACE",
                         "newValue": {"id": PERFIL["C"], "code": "X"}}),
    ("REMOVE de campo", {"targetPath": f"{alvo}/name", "operation": "REMOVE"}),
    ("tipo trocado",    {"targetPath": f"{alvo}/name", "operation": "REPLACE", "newValue": []}),
]:
    c = conteudo_normativo(); apply_change(c, ch)
    print(rotulo, "→", [f.message for f in blocking_findings(validate_for_publication(c))] or "NENHUM")
PY
```

Esperado **antes**: `NENHUM` nas três. Esperado **depois**: um achado impeditivo em cada, nomeando o
caminho do campo.

## A recusa na elaboração

```bash
curl -X POST .../retificacoes -d '{"changes":[{"targetPath":"/profiles/id=<uuid>/name","operation":"REMOVE"}]}'
```

Esperado: `422 blocking_findings`, com `/profiles/id=<uuid>/name` no detalhe. A Retificação **não é
criada** — o ato não chega a existir.

O mesmo vale para o rascunho: `PUT .../rascunho` com o mesmo conteúdo responde igual.

## A recusa na Publicação

Este é o portão que o caminho normal não alcança, porque a elaboração já recusou. O roteiro parte de
uma Retificação malformada **já homologada, gravada diretamente** — o padrão que a `003` usa para a
linha restaurada de backup ou criada por importação.

Esperado: `422 blocking_findings`, e ao fim da operação:

```
Publicacao.objects.filter(edital=edital).count()        → inalterado
DocumentoPublicado.objects.count()                      → inalterado
VersaoConsolidada.objects.filter(edital=edital).count() → inalterado
```

O conteúdo vigente continua sendo o de antes. Recusar não pode deixar efeito parcial.

## A fronteira posterior

O caso que o singular de FR-003 deixava passar.

1. Publique uma Retificação com **vigência futura** — o Edital passa a ter duas fronteiras.
2. Prepare um ato homologado que deixe íntegra a versão de hoje e malformada a da fronteira seguinte.
3. Publique.

Esperado: `422`, com a mensagem nomeando **a fronteira** em que o conteúdo ficaria malformado. Sem
isto, a versão de hoje seria materializada e o Edital vigoraria malformado semanas depois, sem
ninguém ter publicado nada naquele dia.

## O que continua passando

O risco de uma verificação nova é recusar o que é legítimo. FR-014 exige que a Retificação bem
formada siga publicável, e FR-015 que nada da `003` e da `004` mude. Todos estes precisam publicar:

- alterar valores de campos existentes;
- acrescentar Perfil pela tela, com `ADD /profiles/-`;
- remover Perfil por `REMOVE /profiles/id=<uuid>`;
- substituir a lista de requisitos inteira, inclusive por lista vazia;
- deixar `reserveLimit` e `endAt` nulos — o contrato admite nulo neles;
- um Perfil sem Modalidades.

E um que **não** deve ser recusado, apesar de estranho: `immediateVacancies: -3`. Faixa de valor
ficou fora por decisão (FR-009), e o roteiro verifica isso de propósito — para que a garantia não
seja lida como maior do que é.

## A declaração não pode divergir do contrato

```bash
cd backend && uv run pytest tests/contract -q -k forma_declarada
```

Esperado: a forma declarada no domínio confere com `PerfilInput` e `EventoInput` do `openapi.yaml`
nas quatro dimensões. Alterar o contrato sem alterar a declaração faz este teste falhar — é o que
substitui a leitura do contrato em tempo de execução.

## A tela de composição não regride

```bash
cd backend && uv run pytest tests/interface -q
```

Esperado: a lista de pendências de um Edital em elaboração continua igual. Os achados novos não
aparecem lá porque o snapshot em composição é montado do ORM e traz as entidades completas — o
teste existe para que esse pressuposto falhe alto se deixar de valer.

## Cobertura

```bash
cd backend && uv run pytest -q --cov --cov-report=term
```

Esperado: suíte verde nas duas execuções, e cobertura com ramos **integral** do código escrito nesta
feature.
