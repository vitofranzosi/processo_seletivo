"""T090 — o comportamento observável não pode divergir de contracts/openapi.yaml.

Cobre os dois sentidos: nenhuma operação especificada fica sem rota e nenhuma rota
exposta fica fora do contrato. As respostas reais são validadas contra o schema
declarado para o status devolvido.
"""

import re
from pathlib import Path

import pytest
import yaml
from django.urls import get_resolver
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from tests.fixtures.edital import actor_headers, caminho_perfil
from tests.fixtures.publicacao import create_retification, publish_original, retify

CONTRACT = (
    Path(__file__).resolve().parents[3]
    / "specs"
    / "001-processo-seletivo-editais"
    / "contracts"
    / "openapi.yaml"
)
API_PREFIX = "api/v1"
CONTRACT_URI = "urn:processo-seletivo:openapi"
# Converte <uuid:processo_id> do Django no {processoId} do contrato.
DJANGO_PARAM = re.compile(r"<(?:[^:>]+:)?([a-z_]+)>")
VACANCIES = caminho_perfil("immediateVacancies")


@pytest.fixture(scope="module")
def contract():
    return yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def validator_for(contract):
    registry = Registry().with_resource(
        CONTRACT_URI, Resource.from_contents(contract, default_specification=DRAFT202012)
    )

    def build(pointer):
        return Draft202012Validator({"$ref": f"{CONTRACT_URI}#{pointer}"}, registry=registry)

    return build


def _camel(snake):
    head, *tail = snake.split("_")
    return head + "".join(part.title() for part in tail)


def _django_routes():
    """Rotas expostas sob /api/v1, no formato de path do contrato."""
    routes = {}
    for pattern in get_resolver().url_patterns:
        prefix = str(pattern.pattern)
        if not prefix.startswith(API_PREFIX):
            continue
        for sub in pattern.url_patterns:
            raw = prefix + str(sub.pattern)
            path = "/" + raw[len(API_PREFIX) :].strip("/")
            path = DJANGO_PARAM.sub(lambda m: "{" + _camel(m.group(1)) + "}", path)
            methods = {
                method
                for method in ("get", "post", "put", "patch", "delete")
                if hasattr(sub.callback.cls, method)
            }
            routes.setdefault(path, set()).update(methods)
    return routes


def _contract_operations(contract):
    return {
        path: {method for method in item if method in {"get", "post", "put", "patch", "delete"}}
        for path, item in contract["paths"].items()
    }


def test_every_specified_operation_has_a_route(contract):
    especificadas = _contract_operations(contract)
    implementadas = _django_routes()
    faltando = {
        f"{method.upper()} {path}"
        for path, methods in especificadas.items()
        for method in methods
        if method not in implementadas.get(path, set())
    }
    assert not faltando, f"operações do contrato sem implementação: {sorted(faltando)}"


def test_no_route_is_exposed_outside_the_contract(contract):
    especificadas = _contract_operations(contract)
    naodeclaradas = {
        f"{method.upper()} {path}"
        for path, methods in _django_routes().items()
        for method in methods
        if method not in especificadas.get(path, set())
    }
    assert not naodeclaradas, f"rotas expostas fora do contrato: {sorted(naodeclaradas)}"


def _response_pointer(contract, path, method, status):
    responses = contract["paths"][path][method]["responses"]
    assert str(status) in responses, f"status {status} não declarado em {method.upper()} {path}"
    return f"/paths/{path.replace('~', '~0').replace('/', '~1')}/{method}/responses/{status}"


def assert_conforms(validator_for, contract, response, *, path, method, media="application/json"):
    """Valida o corpo devolvido contra o schema declarado para aquele status."""
    pointer = _response_pointer(contract, path, method, response.status_code)
    declared = contract["paths"][path][method]["responses"][str(response.status_code)]
    if "$ref" in declared:
        pointer = "/components/responses/" + declared["$ref"].split("/")[-1]
        declared = contract["components"]["responses"][declared["$ref"].split("/")[-1]]
    content = declared.get("content", {})
    media = next(iter(content)) if media not in content else media
    erros = sorted(
        validator_for(f"{pointer}/content/{media.replace('/', '~1')}/schema").iter_errors(
            response.json()
        ),
        key=lambda item: list(item.path),
    )
    assert not erros, "\n".join(
        f"{method.upper()} {path} → {response.status_code}: "
        f"{'/'.join(str(part) for part in erro.path) or '<raiz>'}: {erro.message}"
        for erro in erros
    )


@pytest.fixture
def cenario(api_client, manager_headers, process_payload):
    """Um Edital publicado, uma Retificação publicada e uma em elaboração."""
    edital = publish_original(api_client, manager_headers, process_payload)
    retificada = retify(
        api_client,
        edital,
        [{"targetPath": VACANCIES, "operation": "REPLACE", "newValue": 7}],
        suffix="a",
    )
    rascunho = create_retification(
        api_client,
        edital,
        [{"targetPath": VACANCIES, "operation": "REPLACE", "newValue": 9}],
        suffix="b",
    )
    return {"edital": edital, "publicada": retificada, "rascunho": rascunho}


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
@pytest.mark.parametrize(
    "path",
    [
        "/public/editais/{editalId}/versao-vigente",
        "/public/editais/{editalId}/historico",
        "/public/publicacoes/{publicacaoId}",
        "/public/retificacoes/{retificacaoId}",
        "/public/versoes/{versaoId}",
    ],
)
def test_public_responses_conform_to_the_contract(
    api_client, validator_for, contract, cenario, path
):
    edital = cenario["edital"]
    url = "/api/v1" + path.replace("{editalId}", str(edital.id)).replace(
        "{publicacaoId}", str(Publicacao.objects.filter(edital=edital).first().id)
    ).replace("{retificacaoId}", str(cenario["publicada"].id)).replace(
        "{versaoId}", str(VersaoConsolidada.objects.filter(edital=edital).first().id)
    )
    response = api_client.get(url)
    assert response.status_code == 200, response.content
    assert_conforms(validator_for, contract, response, path=path, method="get")


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
def test_problem_responses_conform_to_the_contract(api_client, validator_for, contract, cenario):
    """Problem Details também é contrato: erros divergentes quebram clientes."""
    ausente = "00000000-0000-0000-0000-0000000009ff"
    response = api_client.get(f"/api/v1/public/publicacoes/{ausente}")
    assert response.status_code == 404
    assert_conforms(
        validator_for, contract, response, path="/public/publicacoes/{publicacaoId}", method="get"
    )

    sem_versao = api_client.get(
        f"/api/v1/public/editais/{cenario['edital'].id}/versao-vigente",
        {"em": "2000-01-01T00:00:00-03:00"},
    )
    assert sem_versao.status_code == 404
    assert_conforms(
        validator_for,
        contract,
        sem_versao,
        path="/public/editais/{editalId}/versao-vigente",
        method="get",
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
def test_admin_creation_responses_conform_to_the_contract(
    api_client, manager_headers, process_payload, validator_for, contract
):
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    assert criado.status_code == 201
    assert_conforms(validator_for, contract, criado, path="/admin/processos", method="post")

    processo = ProcessoSeletivo.objects.get(pk=criado.json()["id"])
    adicionado = api_client.post(
        f"/api/v1/admin/processos/{processo.id}/editais",
        {"number": "02", "year": 2026, "title": "Segundo"},
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "conformance-key-0001"},
    )
    assert adicionado.status_code == 201
    assert_conforms(
        validator_for,
        contract,
        adicionado,
        path="/admin/processos/{processoId}/editais",
        method="post",
    )

    ativado = api_client.post(
        f"/api/v1/admin/processos/{processo.id}/ativacoes",
        {"reason": "Abertura"},
        format="json",
        **{
            **manager_headers,
            "HTTP_IF_MATCH": '"1"',
            "HTTP_IDEMPOTENCY_KEY": "conformance-key-0002",
        },
    )
    assert ativado.status_code == 200
    assert_conforms(
        validator_for,
        contract,
        ativado,
        path="/admin/processos/{processoId}/ativacoes",
        method="post",
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
def test_admin_finalization_responses_conform_to_the_contract(
    api_client, validator_for, contract, cenario
):
    edital = Edital.objects.get(pk=cenario["edital"].pk)
    gestor = ["processo:encerrar", "processo:cancelar", "edital:encerrar", "edital:cancelar"]
    encerrado = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/encerramentos",
        {"reason": "Etapas concluídas"},
        format="json",
        **actor_headers("gestor", gestor, if_match=edital.revision, key="conformance-key-0003"),
    )
    assert encerrado.status_code == 200
    assert_conforms(
        validator_for,
        contract,
        encerrado,
        path="/admin/editais/{editalId}/encerramentos",
        method="post",
    )

    processo = ProcessoSeletivo.objects.get(pk=edital.processo_id)
    bloqueado = api_client.post(
        f"/api/v1/admin/processos/{processo.id}/encerramentos",
        {"reason": "Sem ativação"},
        format="json",
        **actor_headers("gestor", gestor, if_match=processo.revision, key="conformance-key-0004"),
    )
    assert bloqueado.status_code == 409
    assert_conforms(
        validator_for,
        contract,
        bloqueado,
        path="/admin/processos/{processoId}/encerramentos",
        method="post",
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
def test_admin_retification_responses_conform_to_the_contract(
    api_client, validator_for, contract, cenario
):
    rascunho = Retificacao.objects.get(pk=cenario["rascunho"].pk)
    submetida = api_client.post(
        f"/api/v1/admin/retificacoes/{rascunho.id}/submissoes",
        format="json",
        **{
            **actor_headers("retificador", ["retificacao:submeter"], key="conformance-key-0005"),
            "HTTP_IF_MATCH": f'"{rascunho.revision}"',
        },
    )
    assert submetida.status_code == 200
    assert_conforms(
        validator_for,
        contract,
        submetida,
        path="/admin/retificacoes/{retificacaoId}/submissoes",
        method="post",
    )


UNDECLARED_STATUS = "status {} não declarado em {} {}"


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
def test_error_statuses_returned_are_declared_in_the_contract(
    api_client, manager_headers, process_payload, contract, validator_for
):
    """Um status devolvido e não declarado quebra o cliente tanto quanto um corpo divergente."""
    edital = publish_original(api_client, manager_headers, process_payload)
    sem_permissao = actor_headers("intruso", [], key="conformance-key-0006")
    exercicios = [
        # corpo semanticamente inválido → 422
        (
            "post",
            "/admin/processos",
            "/api/v1/admin/processos",
            {"institutionalCode": "X", "title": "Sem Edital"},
            manager_headers,
        ),
        # Idempotency-Key ausente → 400
        (
            "post",
            "/admin/editais/{editalId}/encerramentos",
            f"/api/v1/admin/editais/{edital.id}/encerramentos",
            {"reason": "Sem chave"},
            {"HTTP_AUTHORIZATION": "Bearer gestor|cefor|edital:encerrar", "HTTP_IF_MATCH": '"5"'},
        ),
        # sem permissão → 403
        (
            "post",
            "/admin/editais/{editalId}/cancelamentos",
            f"/api/v1/admin/editais/{edital.id}/cancelamentos",
            {"reason": "Negado"},
            {**sem_permissao, "HTTP_IF_MATCH": '"5"'},
        ),
    ]
    for metodo, path, url, corpo, headers in exercicios:
        resposta = getattr(api_client, metodo)(url, corpo, format="json", **headers)
        declarados = contract["paths"][path][metodo]["responses"]
        assert str(resposta.status_code) in declarados, UNDECLARED_STATUS.format(
            resposta.status_code, metodo.upper(), path
        )
        assert_conforms(validator_for, contract, resposta, path=path, method=metodo)


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
def test_query_parameter_errors_are_declared_and_conform(
    api_client, manager_headers, process_payload, contract, validator_for
):
    edital = publish_original(api_client, manager_headers, process_payload)
    exercicios = [
        (
            "/public/editais/{editalId}/versao-vigente",
            f"/api/v1/public/editais/{edital.id}/versao-vigente",
            {"em": "ontem"},
        ),
        (
            "/public/editais/{editalId}/historico",
            f"/api/v1/public/editais/{edital.id}/historico",
            {"limit": "999"},
        ),
    ]
    for path, url, params in exercicios:
        resposta = api_client.get(url, params)
        assert resposta.status_code == 400
        assert str(resposta.status_code) in contract["paths"][path]["get"]["responses"], (
            UNDECLARED_STATUS.format(resposta.status_code, "GET", path)
        )
        assert_conforms(validator_for, contract, resposta, path=path, method="get")


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
@pytest.mark.parametrize(
    "accept",
    ["text/html,application/xhtml+xml,*/*", "application/json", "*/*", "text/plain"],
)
def test_responses_always_use_the_declared_media_type(
    api_client, manager_headers, process_payload, contract, validator_for, accept
):
    """O contrato só declara application/json; um navegador não pode receber HTML nem 406."""
    edital = publish_original(api_client, manager_headers, process_payload)
    path = "/public/editais/{editalId}/versao-vigente"
    resposta = api_client.get(
        f"/api/v1/public/editais/{edital.id}/versao-vigente", HTTP_ACCEPT=accept
    )
    assert resposta.status_code == 200, resposta.status_code
    assert resposta["Content-Type"].startswith("application/json"), resposta["Content-Type"]
    assert "application/json" in contract["paths"][path]["get"]["responses"]["200"]["content"]
    assert_conforms(validator_for, contract, resposta, path=path, method="get")
