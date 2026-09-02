from pathlib import Path

import pytest
import yaml

from processo_seletivo.processos.models import Edital
from tests.fixtures.edital import actor_headers, complete_draft


@pytest.mark.contract
def test_openapi_declares_structured_draft_contract():
    contract = (
        Path(__file__).resolve().parents[3]
        / "specs/001-processo-seletivo-editais/contracts/openapi.yaml"
    )
    document = yaml.safe_load(contract.read_text(encoding="utf-8"))
    operation = document["paths"]["/admin/editais/{editalId}/rascunho"]["put"]
    assert operation["operationId"] == "atualizarRascunhoEdital"
    assert any(parameter["$ref"].endswith("/IfMatch") for parameter in operation["parameters"])
    schema = document["components"]["schemas"]["EditalDraftRequest"]
    assert set(schema["required"]) == {"profiles", "schedule"}


@pytest.mark.django_db
@pytest.mark.contract
def test_draft_response_has_etag(api_client, manager_headers, process_payload):
    created = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    from processo_seletivo.processos.models import Edital

    edital = Edital.objects.get(processo_id=created.json()["id"])
    response = api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        {
            "profiles": [
                {
                    "id": "00000000-0000-0000-0000-000000000201",
                    "code": "P1",
                    "name": "Perfil 1",
                    "immediateVacancies": 1,
                    "reserveType": "NONE",
                    "competitionModalities": [],
                }
            ],
            "schedule": [],
        },
        format="json",
        HTTP_AUTHORIZATION="Bearer gestor-a|cefor|edital:elaborar",
        HTTP_IF_MATCH='"1"',
    )
    assert response.status_code == 200
    assert response["ETag"] == '"2"'


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
def test_submission_returns_warnings_so_the_responsible_can_decide(
    api_client, manager_headers, process_payload
):
    """FR-019/FR-020: avisos são classificados e permanecem visíveis na decisão de prosseguir."""
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    edital = Edital.objects.get()
    preparador = actor_headers("preparador", ["edital:elaborar", "edital:submeter"])
    api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        complete_draft(),
        format="json",
        **{**preparador, "HTTP_IF_MATCH": '"1"'},
    )
    resposta = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/submissoes",
        format="json",
        **{**preparador, "HTTP_IF_MATCH": '"2"'},
    )
    assert resposta.status_code == 200
    achados = resposta.json()["validationFindings"]
    assert achados, "o rascunho sem descrição deve produzir aviso"
    aviso = next(item for item in achados if item["code"] == "description_missing")
    assert aviso["severity"] == "WARNING"
    assert aviso["path"] == "description"
    assert not [item for item in achados if item["severity"] == "BLOCKING_ERROR"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
def test_blocking_error_stops_submission_and_names_the_cause(
    api_client, manager_headers, process_payload
):
    """FR-020: erro impeditivo bloqueia e é apresentado separadamente dos avisos."""
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    edital = Edital.objects.get()
    preparador = actor_headers("preparador", ["edital:elaborar", "edital:submeter"])
    api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        {**complete_draft(), "schedule": []},
        format="json",
        **{**preparador, "HTTP_IF_MATCH": '"1"'},
    )
    resposta = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/submissoes",
        format="json",
        **{**preparador, "HTTP_IF_MATCH": '"2"'},
    )
    assert resposta.status_code == 422
    corpo = resposta.json()
    assert corpo["code"] == "blocking_findings"
    assert "Evento" in corpo["detail"]
    assert Edital.objects.get(pk=edital.pk).status == Edital.Status.EM_ELABORACAO


@pytest.mark.contract
@pytest.mark.django_db(transaction=True)
def test_campo_nao_reconhecido_no_rascunho_e_recusado(api_client, manager_headers, process_payload):
    """FR-028 da 003: aceitar e descartar em silêncio não é comportamento admissível.

    `editorialContent` era aceito pelo serializer e pelo contrato, e nenhum comando o persistia.
    Quem o enviava recebia 200 e acreditava que o conteúdo editorial estava guardado no Edital.
    """
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])

    resposta = api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        {**complete_draft(), "editorialContent": {"preambulo": "texto livre"}},
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"]),
            "HTTP_IF_MATCH": f'"{edital.revision}"',
        },
    )

    assert resposta.status_code == 422
    assert "editorialContent" in resposta.json()["detail"]


@pytest.mark.contract
def test_o_contrato_nao_anuncia_mais_o_campo_descartado():
    contrato = yaml.safe_load(
        (
            Path(__file__).resolve().parents[3]
            / "specs/001-processo-seletivo-editais/contracts/openapi.yaml"
        ).read_text(encoding="utf-8")
    )
    rascunho = contrato["components"]["schemas"]["EditalDraftRequest"]
    assert "editorialContent" not in rascunho["properties"]
    assert rascunho["additionalProperties"] is False


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
def test_etapa_de_outro_edital_e_recusada_com_conflito(
    api_client, manager_headers, process_payload
):
    """FR-018: `replace_draft` apaga e recria, então sem esta recusa a Etapa seria reparentada.

    A identidade estável passaria a designar outra coisa, em silêncio. A verificação é a mesma que
    já protege Perfis e Eventos, e a resposta é a mesma — 409, e não 422.
    """
    from processo_seletivo.editais.models.etapas import EtapaAvaliacao

    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    api_client.post(
        f"/api/v1/admin/processos/{criado.json()['id']}/editais",
        {"number": "02", "year": 2026, "title": "Segundo"},
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "etapa-alheia-000001"},
    )
    primeiro, segundo = Edital.objects.order_by("number")
    preparador = actor_headers("preparador", ["edital:elaborar"], key="etapa-alheia-000002")
    etapa = {
        "id": "00000000-0000-0000-0000-0000000009e1",
        "name": "Prova didática",
        "order": 1,
    }

    primeira = api_client.put(
        f"/api/v1/admin/editais/{primeiro.id}/rascunho",
        {**complete_draft(), "stages": [etapa]},
        format="json",
        **{**preparador, "HTTP_IF_MATCH": '"1"'},
    )
    assert primeira.status_code == 200, primeira.content

    # O segundo Edital tem Perfil e Evento próprios, e reusa só o identificador da Etapa.
    resposta = api_client.put(
        f"/api/v1/admin/editais/{segundo.id}/rascunho",
        {**complete_draft(seed=1), "stages": [etapa]},
        format="json",
        **{**preparador, "HTTP_IF_MATCH": '"1"'},
    )

    assert resposta.status_code == 409, resposta.content
    assert resposta.json()["code"] == "identifier_belongs_to_another_edital"
    assert not EtapaAvaliacao.objects.filter(edital=segundo).exists()
    assert EtapaAvaliacao.objects.filter(edital=primeiro).count() == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
def test_etapa_que_referencia_evento_inexistente_e_recusada(
    api_client, manager_headers, process_payload
):
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    preparador = actor_headers("preparador", ["edital:elaborar"], key="etapa-evento-00001")

    resposta = api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        {
            **complete_draft(),
            "stages": [
                {
                    "id": "00000000-0000-0000-0000-0000000009e2",
                    "name": "Prova",
                    "order": 1,
                    "scheduleEventId": "00000000-0000-0000-0000-0000000009ff",
                }
            ],
        },
        format="json",
        **{**preparador, "HTTP_IF_MATCH": '"1"'},
    )

    assert resposta.status_code == 422, resposta.content
    assert resposta.json()["code"] == "invalid_stages"


def _dois_editais(api_client, manager_headers, process_payload, chave):
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    api_client.post(
        f"/api/v1/admin/processos/{criado.json()['id']}/editais",
        {"number": "02", "year": 2026, "title": "Segundo"},
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": chave},
    )
    return Edital.objects.order_by("number")


def _com_modalidades(seed, modalidades):
    rascunho = complete_draft(seed)
    rascunho["profiles"][0]["competitionModalities"] = modalidades
    return rascunho


MODALIDADE = {
    "A": "00000000-0000-0000-0000-0000000009c1",
    "B": "00000000-0000-0000-0000-0000000009c2",
}
REGRA = {
    "A": "00000000-0000-0000-0000-0000000009d1",
    "B": "00000000-0000-0000-0000-0000000009d2",
}


def _modalidade(identificador, regra_id, codigo):
    return {
        "id": identificador,
        "code": codigo,
        "name": f"Modalidade {codigo}",
        "normativeRule": {
            "id": regra_id,
            "foundation": "Lei 12.990/2014",
            "version": "2014-06-09",
            "percentage": "20.0000",
        },
    }


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
def test_identidade_de_modalidade_e_de_regra_e_preservada_pela_api(
    api_client, manager_headers, process_payload
):
    """FR-027: sem `id` declarado nos serializers, o identificador nunca chegaria ao command.

    A preservação valeria só pelo caminho da interface administrativa, e a recusa de identificador
    alheio não teria o que recusar.
    """
    from processo_seletivo.editais.models.perfis import ModalidadeConcorrencia, RegraNormativa

    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    preparador = actor_headers("preparador", ["edital:elaborar"], key="identidade-mod-0001")

    resposta = api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        _com_modalidades(0, [_modalidade(MODALIDADE["A"], REGRA["A"], "PPP")]),
        format="json",
        **{**preparador, "HTTP_IF_MATCH": '"1"'},
    )

    assert resposta.status_code == 200, resposta.content
    assert str(ModalidadeConcorrencia.objects.get().id) == MODALIDADE["A"]
    assert str(RegraNormativa.objects.get().id) == REGRA["A"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
@pytest.mark.parametrize(
    "caso",
    [
        "modalidade-de-outro-perfil",
        "modalidade-de-outro-edital",
        "regra-de-modalidade-irma",
        "regra-de-outro-edital",
    ],
)
def test_identificador_de_outro_conteiner_e_recusado_com_conflito(
    api_client, manager_headers, process_payload, caso
):
    """FR-029: cada entidade é verificada no nível do **seu** contêiner, e nenhuma um acima.

    `regra-de-modalidade-irma` é o caso que a verificação até o Perfil deixava passar: duas
    Modalidades do mesmo Perfil trocando a identidade das suas Regras, sem que nada acusasse — e a
    identidade estável passando a designar outra relação normativa.
    """
    primeiro, segundo = _dois_editais(api_client, manager_headers, process_payload, f"conf-{caso}")
    preparador = actor_headers("preparador", ["edital:elaborar"], key=f"conflito-{caso[:8]}-01")

    inicial = api_client.put(
        f"/api/v1/admin/editais/{primeiro.id}/rascunho",
        _com_modalidades(
            0,
            [
                _modalidade(MODALIDADE["A"], REGRA["A"], "PPP"),
                _modalidade(MODALIDADE["B"], REGRA["B"], "PCD"),
            ],
        ),
        format="json",
        **{**preparador, "HTTP_IF_MATCH": '"1"'},
    )
    assert inicial.status_code == 200, inicial.content

    if caso == "modalidade-de-outro-perfil":
        # Mesmo Edital, Perfil novo, reusando o identificador da modalidade do Perfil anterior.
        alvo, seed, revisao = primeiro, 2, '"2"'
        modalidades = [_modalidade(MODALIDADE["A"], REGRA["A"], "PPP")]
    elif caso == "modalidade-de-outro-edital":
        alvo, seed, revisao = segundo, 1, '"1"'
        modalidades = [_modalidade(MODALIDADE["A"], "00000000-0000-0000-0000-0000000009d9", "PPP")]
    elif caso == "regra-de-modalidade-irma":
        # Mesmo Perfil, mesma modalidade — a Regra da irmã.
        alvo, seed, revisao = primeiro, 0, '"2"'
        modalidades = [
            _modalidade(MODALIDADE["A"], REGRA["B"], "PPP"),
            _modalidade(MODALIDADE["B"], REGRA["A"], "PCD"),
        ]
    else:
        alvo, seed, revisao = segundo, 1, '"1"'
        modalidades = [_modalidade("00000000-0000-0000-0000-0000000009c9", REGRA["A"], "PPP")]

    resposta = api_client.put(
        f"/api/v1/admin/editais/{alvo.id}/rascunho",
        _com_modalidades(seed, modalidades),
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"], key=f"conflito-{caso[:8]}-02"),
            "HTTP_IF_MATCH": revisao,
        },
    )

    assert resposta.status_code == 409, resposta.content
    assert resposta.json()["code"] == "identifier_belongs_to_another_edital"


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
@pytest.mark.parametrize("percentual", ["0", "0.0000", "120", "100.0001"])
def test_percentual_fora_da_faixa_e_recusado_pela_api(
    api_client, manager_headers, process_payload, percentual
):
    """A mesma regra que a interface atravessa — porque ela vive no domínio, não no serializer."""
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    modalidade = _modalidade(MODALIDADE["A"], REGRA["A"], "PPP")
    modalidade["normativeRule"]["percentage"] = percentual

    resposta = api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        _com_modalidades(0, [modalidade]),
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"], key="percentual-0000001"),
            "HTTP_IF_MATCH": '"1"',
        },
    )

    assert resposta.status_code == 422, resposta.content
    assert "maior que zero e menor ou igual a cem" in resposta.json()["detail"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
def test_percentual_de_cem_por_cento_e_aceito(api_client, manager_headers, process_payload):
    """O limite é inclusivo: ampla concorrência com cem por cento é declaração legítima."""
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    modalidade = _modalidade(MODALIDADE["A"], REGRA["A"], "AC")
    modalidade["normativeRule"]["percentage"] = "100.0000"

    resposta = api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        _com_modalidades(0, [modalidade]),
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"], key="percentual-0000002"),
            "HTTP_IF_MATCH": '"1"',
        },
    )

    assert resposta.status_code == 200, resposta.content


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
@pytest.mark.parametrize(
    ("chave", "razao"),
    [
        ("secao-inventada", "fora do catálogo: o conjunto de seções é do sistema"),
        ("cronograma", "gerada: o conteúdo dela vem do dado que a origina"),
    ],
)
def test_secao_fora_do_catalogo_ou_gerada_e_recusada_na_gravacao(
    api_client, manager_headers, process_payload, chave, razao
):
    """FR-034 e FR-036, os dois no mesmo lugar.

    Acrescentar seção é o que a spec exclui — é a diferença entre documento institucional
    estruturado e construtor de documentos. E dar texto a uma seção gerada criaria dois endereços
    para o mesmo conteúdo normativo, sem como dizer qual vigora.
    """
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])

    resposta = api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        {**complete_draft(), "sections": [{"key": chave, "content": "Texto qualquer"}]},
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"], key=f"secao-{chave[:8]}-01"),
            "HTTP_IF_MATCH": '"1"',
        },
    )

    assert resposta.status_code == 422, f"{razao}: {resposta.content}"
    assert resposta.json()["code"] == "field_constraint_violated"
    assert chave in resposta.json()["detail"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
def test_secao_textual_do_catalogo_e_aceita(api_client, manager_headers, process_payload):
    from processo_seletivo.editais.domain import secoes as catalogo
    from processo_seletivo.editais.models.secoes import SecaoEdital

    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])

    resposta = api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        {**complete_draft(), "sections": [{"key": "recursos", "content": "Três dias úteis."}]},
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"], key="secao-aceita-000001"),
            "HTTP_IF_MATCH": '"1"',
        },
    )

    assert resposta.status_code == 200, resposta.content
    linha = SecaoEdital.objects.get()
    assert linha.content == "Três dias úteis."
    assert linha.id == catalogo.identidade(edital.id, "recursos")


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
@pytest.mark.parametrize("omitido", ["modalidade", "regra"])
def test_identificador_de_modalidade_e_de_regra_e_exigido(
    api_client, manager_headers, process_payload, omitido
):
    """FR-027: opcional, o identificador reabriria o defeito que a feature veio fechar.

    Um payload sem `id` seria aceito, o servidor geraria um, e a resposta do rascunho devolve
    apenas o resumo do Edital — o cliente não teria como preservar o que nunca recebeu, e a
    gravação seguinte trocaria a identidade de novo. Perfil, Evento e Etapa já exigem o seu; a
    regra aqui é a mesma, e não uma exceção.
    """
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    modalidade = _modalidade(MODALIDADE["A"], REGRA["A"], "PPP")
    if omitido == "modalidade":
        del modalidade["id"]
    else:
        del modalidade["normativeRule"]["id"]

    resposta = api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        _com_modalidades(0, [modalidade]),
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"], key=f"sem-id-{omitido[:6]}-01"),
            "HTTP_IF_MATCH": '"1"',
        },
    )

    assert resposta.status_code == 422, resposta.content
    assert "id" in resposta.json()["detail"]
