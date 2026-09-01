"""O incremento da `012` atravessa o rascunho, o assistente e a publicação (FR-007).

O caso que dá nome a metade destes testes: o assistente reenvia o rascunho **inteiro** a cada passo.
Campo que ele não lê não fica em branco — ele vira `null` na próxima gravação de qualquer outra
Etapa, e o Edital perde silenciosamente uma declaração normativa que alguém já tinha feito.
"""

from decimal import Decimal

import pytest

from processo_seletivo.editais.domain.etapas import StageValidationError, validate_stage
from processo_seletivo.editais.models.etapas import EtapaAvaliacao
from processo_seletivo.interface.forms import etapas_do_edital, etapas_persistidas
from tests.fixtures.snapshot import ETAPA, rascunho_com_etapas

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def declarar(draft, **valores):
    draft["stages"][0].update(valores)
    return draft


@pytest.fixture
def edital_em_elaboracao(api_client, manager_headers, process_payload):
    """Um Edital que ainda aceita rascunho — o `edital_a` da suíte já está publicado."""
    from processo_seletivo.processos.models import Edital

    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    assert criado.status_code == 201, criado.content
    return Edital.objects.get(processo_id=criado.json()["id"])


def gravar(api_client, edital, draft, revisao="1"):
    from tests.fixtures.edital import actor_headers

    return api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        draft,
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"]),
            "HTTP_IF_MATCH": f'"{revisao}"',
        },
    )


def test_o_rascunho_guarda_as_duas_declaracoes(api_client, edital_em_elaboracao):
    draft = declarar(rascunho_com_etapas(), evaluationsPerRegistration=2, maximumScore="100.0000")

    resposta = gravar(
        api_client, edital_em_elaboracao, draft, revisao=str(edital_em_elaboracao.revision)
    )

    assert resposta.status_code == 200, resposta.content
    etapa = EtapaAvaliacao.objects.get(pk=ETAPA["A"])
    assert etapa.evaluations_per_registration == 2
    assert str(etapa.maximum_score) == "100.0000"


def test_o_assistente_preserva_o_que_ja_estava_declarado(api_client, edital_em_elaboracao):
    """A regressão do assistente: salvar outra Etapa não pode apagar declaração alheia."""
    draft = declarar(rascunho_com_etapas(), evaluationsPerRegistration=2, maximumScore="100.0000")
    gravar(api_client, edital_em_elaboracao, draft, revisao=str(edital_em_elaboracao.revision))
    edital_em_elaboracao.refresh_from_db()

    preservadas = etapas_persistidas(edital_em_elaboracao)

    declarada = next(item for item in preservadas if item["id"] == ETAPA["A"])
    assert declarada["evaluationsPerRegistration"] == 2
    assert str(declarada["maximumScore"]) == "100.0000"


def test_o_formulario_exibe_o_que_esta_gravado(api_client, edital_em_elaboracao):
    draft = declarar(rascunho_com_etapas(), evaluationsPerRegistration=3, maximumScore="50.0000")
    gravar(api_client, edital_em_elaboracao, draft, revisao=str(edital_em_elaboracao.revision))
    edital_em_elaboracao.refresh_from_db()

    linhas = etapas_do_edital(edital_em_elaboracao)

    linha = next(item for item in linhas if item["id"] == ETAPA["A"])
    assert linha["evaluationsPerRegistration"] == 3
    assert linha["maximumScore"] == "50.0000"


@pytest.mark.parametrize(
    ("valores", "campo"),
    [
        ({"evaluationsPerRegistration": 0}, "evaluationsPerRegistration"),
        ({"maximumScore": "0.0000"}, "maximumScore"),
    ],
)
def test_a_api_recusa_a_faixa_nomeando_o_campo(api_client, edital_em_elaboracao, valores, campo):
    draft = declarar(rascunho_com_etapas(), **valores)

    resposta = gravar(
        api_client, edital_em_elaboracao, draft, revisao=str(edital_em_elaboracao.revision)
    )

    assert resposta.status_code == 422, resposta.content
    assert campo in resposta.content.decode()


@pytest.mark.parametrize(
    ("valores", "mensagem"),
    [
        ({"evaluationsPerRegistration": 0}, "ao menos uma avaliação"),
        ({"maximumScore": Decimal("0")}, "maior que zero"),
        (
            {"minimumScore": Decimal("90"), "maximumScore": Decimal("50")},
            "não pode superar",
        ),
    ],
)
def test_o_dominio_recusa_a_faixa_no_canal_que_nao_passa_pelo_serializer(valores, mensagem):
    """A interface administrativa invoca o command direto.

    Validar só no serializer deixaria sem verificação justamente o canal onde o dado é digitado —
    e a faixa chegaria ao `CheckConstraint`, virando erro de banco em vez de recusa nomeada.
    """
    etapa = {
        "id": ETAPA["A"],
        "name": "Análise documental",
        "order": 1,
        "minimumScore": Decimal("7"),
        **valores,
    }

    with pytest.raises(StageValidationError, match=mensagem):
        validate_stage(etapa, event_ids=frozenset())
