"""O Edital publicado não é julgado como se ainda fosse publicar (046, `FR-755`, `SC-278`).

**O `RC-32` da auditoria de consolidação**, reproduzido em 26/09/2026: a tela de um Edital
`PUBLICADO` cujo período de inscrições já terminou dizia *"Impede — O período de inscrições encerrou…
corrija a data do Evento na etapa Cronograma antes de publicar"*, e avisava que *"o Edital será
publicado com esta data"*. Nada disso bloqueava operação — os atos de submeter e publicar não existem
num Edital publicado —, mas a tela instruía a corrigir antes de publicar o que já é ato imutável.

**Os fatos ficam; o gate sai** (`D-003`). A Etapa sem Evento é fato sobre o conteúdo publicado, e a
`045` a levou para esta página (`FR-739`); ela continua dita. O que some é o juízo de
publicabilidade — e é por isso que este arquivo afirma os dois lados na mesma página.

**O relógio é adiantado só para a view.** `mock.patch` sobre `django.utils.timezone.now` adiantaria
também a sessão, e a identidade expiraria antes de a página abrir: o nome é trocado no módulo da
interface, e o resto do sistema continua no presente.
"""

from datetime import timedelta
from unittest import mock

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.interface.views import CHAVES_ETAPA
from processo_seletivo.processos.models import Edital
from tests.fixtures.edital import actor_headers, complete_draft
from tests.fixtures.publicacao import levar_a_publicacao
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

ETAPA_SEM_EVENTO = "aaaaaaaa-0000-4000-8000-0000000046a1"
PERIODO_ENCERRADO = "O período de inscrições encerrou"
SERA_PUBLICADO = "O Edital será publicado"
AVISO_DA_ETAPA = "não está vinculada a nenhum Evento do Cronograma"


def _rascunho():
    """Inscrições designadas, que terminam em dois dias; e uma Etapa que não vincula Evento."""
    rascunho = complete_draft()
    termino = timezone.localtime() + timedelta(days=2)
    rascunho["schedule"][0].update(
        {"isRegistrationPeriod": True, "endAt": termino.isoformat(timespec="seconds")}
    )
    rascunho["stages"] = [
        {
            "id": ETAPA_SEM_EVENTO,
            "name": "Prova didática",
            "order": 1,
            "eliminatory": False,
            "classificatory": True,
        }
    ]
    return rascunho


def _criar(api_client, manager_headers, process_payload):
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    assert criado.status_code == 201, criado.content
    return Edital.objects.get(processo_id=criado.json()["id"])


def _em_elaboracao(api_client, manager_headers, process_payload):
    edital = _criar(api_client, manager_headers, process_payload)
    gravado = api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        _rascunho(),
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"], key="046-sem-pendencias-rascunho"),
            "HTTP_IF_MATCH": f'"{edital.revision}"',
        },
    )
    assert gravado.status_code == 200, gravado.content
    return Edital.objects.get(pk=edital.pk)


def _publicado(api_client, manager_headers, process_payload):
    edital = _criar(api_client, manager_headers, process_payload)
    return levar_a_publicacao(api_client, edital, draft=_rascunho())


def _paginas(client, edital):
    """A tela do Edital e as etapas do assistente, com o relógio da view trinta dias adiante."""
    depois_do_termino = timezone.now() + timedelta(days=30)
    with mock.patch("processo_seletivo.interface.views.timezone", wraps=timezone) as relogio:
        relogio.now.return_value = depois_do_termino
        paginas = {"detalhe": client.get(reverse("interface:detalhe", args=[edital.id]))}
        for chave in CHAVES_ETAPA:
            paginas[chave] = client.get(reverse("interface:compor-etapa", args=[edital.id, chave]))
    for chave, resposta in paginas.items():
        assert resposta.status_code == 200, (chave, resposta.status_code)
    return {chave: resposta.content.decode() for chave, resposta in paginas.items()}


def test_o_edital_publicado_nao_diz_impede_nem_sera_publicado(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    edital = _publicado(api_client, manager_headers, process_payload)
    identificar(client, "ana.elaboradora", ["elaborador"])

    for chave, pagina in _paginas(client, edital).items():
        assert PERIODO_ENCERRADO not in pagina, f"{chave}: o juízo de publicabilidade voltou"
        assert SERA_PUBLICADO not in pagina, f"{chave}: aviso que fala do ato de publicar"
        assert 'class="p-erro"' not in pagina, f"{chave}: impeditivo em Edital publicado"


def test_o_fato_da_etapa_sem_evento_continua_dito_no_edital_publicado(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """A contraprova de que a lista funciona, e não de que a seção sumiu (`045`, `FR-739`)."""
    edital = _publicado(api_client, manager_headers, process_payload)
    identificar(client, "ana.elaboradora", ["elaborador"])

    detalhe = _paginas(client, edital)["detalhe"]

    assert "Validação do conteúdo" in detalhe
    assert AVISO_DA_ETAPA in detalhe


def test_o_mesmo_conteudo_em_elaboracao_continua_impedido(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """Antes da publicação nada muda: é ali que o impeditivo tem remédio."""
    edital = _em_elaboracao(api_client, manager_headers, process_payload)
    identificar(client, "ana.elaboradora", ["elaborador"])

    paginas = _paginas(client, edital)

    assert PERIODO_ENCERRADO in paginas["detalhe"]
    assert PERIODO_ENCERRADO in paginas["revisao"]


@pytest.mark.parametrize("estado", [Edital.Status.ENCERRADO, Edital.Status.CANCELADO])
def test_encerrado_e_cancelado_se_leem_como_o_publicado(
    estado, client, seletor_ligado, api_client, manager_headers, process_payload
):
    edital = _publicado(api_client, manager_headers, process_payload)
    # O estado muda por `update` porque o que se afere é a leitura, e não o ato de encerrar ou
    # cancelar, que tem testes próprios.
    Edital.objects.filter(pk=edital.pk).update(status=estado)
    identificar(client, "ana.elaboradora", ["elaborador"])

    detalhe = _paginas(client, Edital.objects.get(pk=edital.pk))["detalhe"]

    assert PERIODO_ENCERRADO not in detalhe
    assert AVISO_DA_ETAPA in detalhe
