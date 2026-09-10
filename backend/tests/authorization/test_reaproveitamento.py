"""Quem pode partir de qual Edital (023, FR-003, FR-004, T-007).

Duas fronteiras, e as duas importam. A **permissão** é a de elaborar, porque copiar configuração é
elaborar — e não a de criar, que é do Gestor: fosse a de criar, quem conduz o Processo autoraria
conteúdo normativo, e a segregação que a `002` construiu se desfaria.

A **elegibilidade da origem** é o que resolve a autorização de leitura sem inventar permissão: o
conteúdo de um Edital publicado já é público, e ler para copiar não concede nada que o portal não
conceda. Inexistente, fora do escopo e inelegível respondem igual — distinguir já seria informação.
"""

import pytest

from processo_seletivo.editais.application.reaproveitamento import (
    origens_elegiveis,
    reaproveitar_edital,
)
from processo_seletivo.processos.models import Edital
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.integration.editais.test_reaproveitamento import rascunho_rico

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def origem(api_client, manager_headers, process_payload):
    from tests.fixtures.publicacao import publish_original

    return publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_rico(), anexos=1
    )


@pytest.fixture
def destino(api_client, manager_headers, origem):
    criado = api_client.post(
        "/api/v1/admin/processos",
        {
            "institutionalCode": "PS-2027-001",
            "title": "Processo Seletivo 2027",
            "firstEdital": {"number": "77", "year": 2027, "title": "Edital da nova oferta"},
        },
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "destino-key-0001"},
    )
    assert criado.status_code == 201, criado.content
    return Edital.objects.get(processo_id=criado.json()["id"])


def tentar(ator, destino, origem_id, *, chave="autorizacao-0001"):
    return reaproveitar_edital(
        actor=ator,
        edital_id=destino.id,
        origem_id=origem_id,
        expected_revision=destino.revision,
        idempotency_key=chave,
        correlation_id="autorizacao",
    )


@pytest.mark.authorization
def test_quem_nao_elabora_nao_copia(destino, origem):
    """O Gestor cria o Edital; quem copia configuração para dentro dele é quem elabora."""
    gestor = ator_institucional("gestor-a", "processo:criar", "edital:criar")

    with pytest.raises(DomainError) as recusa:
        tentar(gestor, destino, origem.id)

    assert recusa.value.code in ("forbidden", "permission_denied")


@pytest.mark.authorization
def test_origem_inexistente_fora_do_escopo_e_inelegivel_respondem_igual(destino, origem):
    """A recusa é indistinguível: dizer "existe, mas você não pode" revelaria a existência."""
    elaborador = ator_institucional("preparadora", "edital:elaborar")
    de_outro_escopo = ator_institucional("preparadora", "edital:elaborar", escopo="outra-unidade")

    inexistente = "00000000-0000-0000-0000-0000000000ff"
    em_elaboracao = destino
    Edital.objects.filter(pk=origem.pk).update(status=Edital.Status.CANCELADO)

    recusas = []
    for indice, (ator, alvo) in enumerate(
        (
            (elaborador, inexistente),
            (elaborador, em_elaboracao.id),
            (elaborador, origem.id),
            (de_outro_escopo, origem.id),
        )
    ):
        with pytest.raises(DomainError) as recusa:
            tentar(ator, destino, alvo, chave=f"autorizacao-{indice}")
        recusas.append((recusa.value.code, recusa.value.status, recusa.value.detail))

    assert len(set(recusas)) == 1, recusas
    assert recusas[0][1] == 404


@pytest.mark.authorization
def test_a_fronteira_tem_dois_lados(destino, origem):
    """Publicado e encerrado são aceitos — e a cópia acontece de verdade (FR-004)."""
    elaborador = ator_institucional("preparadora", "edital:elaborar")

    assert list(origens_elegiveis(elaborador)) == [origem]

    Edital.objects.filter(pk=origem.pk).update(status=Edital.Status.ENCERRADO)
    origem.refresh_from_db()
    assert list(origens_elegiveis(elaborador)) == [origem]

    copiado = tentar(elaborador, destino, origem.id)

    assert copiado.perfis.count() == 1


@pytest.mark.authorization
def test_o_destino_de_outro_escopo_nao_e_alcancavel(destino, origem):
    de_outro_escopo = ator_institucional("preparadora", "edital:elaborar", escopo="outra-unidade")

    with pytest.raises(DomainError) as recusa:
        tentar(de_outro_escopo, destino, origem.id)

    assert recusa.value.status == 404
