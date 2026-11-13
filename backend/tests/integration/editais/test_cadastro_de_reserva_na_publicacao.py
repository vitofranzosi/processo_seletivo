"""O número do cadastro na gravação, na composição e na publicação (162, T009, T037).

- a gravação não aceita número no limitado, por nenhum caminho (FR-6931);
- o rascunho salvo antes da `162` guarda o dele, e a Revisão o diz ao lado do derivado (FR-6940);
- a composição do conteúdo nunca o leva (`edital_snapshot`, T-003);
- o Edital publicado antes da `162` continua dizendo o número que publicou, e nada o reavalia
  (FR-6944, FR-6948, SC-2301).

**O Edital legado é publicado pelo caminho de antes** (`tests/fixtures/legado.py::antes_da_162`).
Depois da `162` nenhum caminho grava o número no conteúdo; é o único modo de reproduzir o acervo sem
escrever na tabela append-only.
"""

import pytest

from processo_seletivo.editais.application.draft import (
    NUMERO_DIGITADO,
    advertencias_do_numero_digitado,
)
from processo_seletivo.editais.models.perfis import PerfilVaga
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot
from processo_seletivo.publicacoes.infrastructure import pdf
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.edital import actor_headers
from tests.fixtures.legado import antes_da_162, devolver_o_numero_digitado
from tests.fixtures.publicacao import publish_original
from tests.fixtures.snapshot import PERFIL, com_cadastro, rascunho_completo

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def _rascunho(numero=3):
    rascunho = rascunho_completo()
    for perfil in rascunho["profiles"]:
        if perfil["id"] == PERFIL["C"]:
            com_cadastro(perfil, "LIMITED", numero)
    return rascunho


def _criar_edital(api_client, manager_headers, process_payload):
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    assert criado.status_code == 201, criado.content
    return Edital.objects.get(processo_id=criado.json()["id"])


def _gravar(api_client, edital, rascunho):
    edital.refresh_from_db()
    return api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        rascunho,
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"], key="cadastro-162"),
            "HTTP_IF_MATCH": f'"{edital.revision}"',
        },
    )


# --- A gravação (FR-6931) -----------------------------------------------------------------------


def test_a_api_recusa_o_numero_digitado(api_client, manager_headers, process_payload):
    edital = _criar_edital(api_client, manager_headers, process_payload)
    rascunho = _rascunho()
    (perfil,) = [p for p in rascunho["profiles"] if p["id"] == PERFIL["C"]]
    perfil["reserveLimit"] = 6

    resposta = _gravar(api_client, edital, rascunho)

    assert resposta.status_code == 422, resposta.content
    assert "não se digita: ele vem do corte do marco que convoca" in resposta.content.decode()


# --- O rascunho salvo antes e a Revisão (FR-6940, T-003) ----------------------------------------


@pytest.fixture
def rascunho_antigo(api_client, manager_headers, process_payload):
    """Um rascunho com o limitado coerente, e o número que a tela de antes da `162` gravava."""
    edital = _criar_edital(api_client, manager_headers, process_payload)
    assert _gravar(api_client, edital, _rascunho(3)).status_code < 400
    PerfilVaga.objects.filter(id=PERFIL["C"]).update(reserve_limit=6)
    return edital


def test_a_composicao_nunca_leva_o_numero(rascunho_antigo):
    (perfil,) = [p for p in edital_snapshot(rascunho_antigo)["profiles"] if p["id"] == PERFIL["C"]]
    assert perfil["reserveType"] == "LIMITED"
    assert perfil["reserveLimit"] is None


def test_a_revisao_diz_o_digitado_e_o_derivado(rascunho_antigo):
    (achado,) = advertencias_do_numero_digitado(rascunho_antigo, edital_snapshot(rascunho_antigo))
    assert achado.code == NUMERO_DIGITADO
    assert achado.path == f"/profiles/id={PERFIL['C']}/reserveType"
    assert "guardava o cadastro de reserva limitado em 6" in achado.message
    assert "O Edital vai publicar até 3" in achado.message


def test_sem_advertencia_quando_os_numeros_coincidem(rascunho_antigo):
    PerfilVaga.objects.filter(id=PERFIL["C"]).update(reserve_limit=3)
    assert advertencias_do_numero_digitado(rascunho_antigo, edital_snapshot(rascunho_antigo)) == []


def test_regravar_por_outra_etapa_nao_apaga_o_digitado(api_client, rascunho_antigo):
    """Sem isto a advertência sumiria na primeira gravação, antes de quem elabora a ler."""
    assert _gravar(api_client, rascunho_antigo, _rascunho(3)).status_code < 400
    assert PerfilVaga.objects.get(id=PERFIL["C"]).reserve_limit == 6


def test_trocar_a_especie_apaga_o_digitado(api_client, rascunho_antigo):
    rascunho = _rascunho(3)
    (perfil,) = [p for p in rascunho["profiles"] if p["id"] == PERFIL["C"]]
    com_cadastro(perfil, "UNLIMITED")
    assert _gravar(api_client, rascunho_antigo, rascunho).status_code < 400
    assert PerfilVaga.objects.get(id=PERFIL["C"]).reserve_limit is None


# --- O legado (FR-6944, FR-6948, SC-2301) --------------------------------------------------------


@pytest.fixture
def legado(api_client, manager_headers, process_payload):
    """Um Edital publicado pelo caminho de antes da `162`: o número digitado no conteúdo."""
    with antes_da_162():
        return publish_original(
            api_client,
            manager_headers,
            process_payload,
            draft=_rascunho(3),
            antes_de_submeter=lambda edital: devolver_o_numero_digitado(edital, {PERFIL["C"]: 6}),
        )


def test_o_legado_publicou_o_numero_digitado_e_o_documento_o_diz(legado):
    vigente = VersaoConsolidada.objects.filter(edital=legado).latest("materialized_at").content
    (perfil,) = [p for p in vigente["profiles"] if p["id"] == PERFIL["C"]]
    assert perfil["reserveLimit"] == 6
    assert pdf.frase_do_cadastro(perfil).startswith("cadastro de reserva de até 6 (seis)")


def test_o_legado_nao_ganha_achado_novo_na_retificacao(legado):
    from processo_seletivo.editais.domain import cadastro_de_reserva
    from processo_seletivo.editais.domain.validation import (
        ATO_DE_RETIFICACAO,
        validate_for_publication,
    )

    vigente = VersaoConsolidada.objects.filter(edital=legado).latest("materialized_at").content
    codigos = {item.code for item in validate_for_publication(vigente, ato=ATO_DE_RETIFICACAO)}
    assert not codigos & {
        cadastro_de_reserva.LIMITADO_A_NINGUEM,
        cadastro_de_reserva.LIMITADO_COM_MARCOS_DIVERGENTES,
        cadastro_de_reserva.LIMITADO_COM_CONTINUACAO,
        cadastro_de_reserva.LIMITADO_SEM_CORTE,
        cadastro_de_reserva.ILIMITADO_SEM_CONTINUACAO,
    }
