"""A etapa `Inscrição` do assistente (US2 da 009, FR-007).

Uma etapa que escreve em duas coleções — a designação vive no Evento, os requisitos são coleção
própria — porque para quem elabora é uma decisão só: como este Edital recebe inscrição.
"""

import pytest
from django.urls import reverse

from processo_seletivo.editais.models import DocumentoExigido, EventoCronograma
from processo_seletivo.processos.models import Edital
from tests.fixtures.edital import actor_headers, identificador
from tests.fixtures.selecao import rascunho_de_selecao
from tests.interface.conftest import identificar


@pytest.fixture
def edital_com_perfis(api_client, manager_headers, process_payload):
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        rascunho_de_selecao(),
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"], key="inscricao-etapa-0001"),
            "HTTP_IF_MATCH": '"1"',
        },
    )
    edital.refresh_from_db()
    return edital


def _campos(edital, **ajustes):
    base = {
        "periodo-inscricoes": identificador(402, 0),
        "documento-0-id": identificador(408, 0),
        "documento-0-key": "identificacao",
        "documento-0-name": "Documento de identificação",
        "documento-0-instructions": "Frente e verso.",
        "documento-0-required": "on",
        "documento-0-order": "1",
        "documento-0-profileId": "",
        "documento-0-modalityId": "",
        "documento-1-id": identificador(409, 0),
        "documento-1-key": "diploma",
        "documento-1-name": "Diploma de graduação",
        "documento-1-instructions": "",
        "documento-1-required": "on",
        "documento-1-order": "2",
        "documento-1-profileId": identificador(401, 0),
        "documento-1-modalityId": "",
    }
    base.update(ajustes)
    return base


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_etapa_existe_no_assistente_e_oferece_os_eventos(
    client, seletor_ligado, edital_com_perfis
):
    identificar(client, "ana.elaboradora", ["elaborador"])

    corpo = client.get(
        reverse("interface:compor-etapa", args=[edital_com_perfis.id, "inscricao"])
    ).content.decode()

    assert "Período de inscrições" in corpo
    assert "Documentos exigidos" in corpo
    assert identificador(402, 0) in corpo, "o Evento do Cronograma é oferecido para designação"
    assert "Este Edital não recebe inscrições pelo sistema" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_gravar_designa_o_periodo_e_cria_os_documentos(client, seletor_ligado, edital_com_perfis):
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = client.post(
        reverse("interface:compor-etapa", args=[edital_com_perfis.id, "inscricao"]),
        _campos(edital_com_perfis),
    )

    assert resposta.status_code == 302
    designados = EventoCronograma.objects.filter(
        cronograma__edital=edital_com_perfis, is_registration_period=True
    )
    assert [str(evento.id) for evento in designados] == [identificador(402, 0)]
    assert list(
        DocumentoExigido.objects.filter(edital=edital_com_perfis)
        .order_by("order")
        .values_list("key", flat=True)
    ) == ["identificacao", "diploma"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_gravar_a_etapa_preserva_perfis_e_cronograma(client, seletor_ligado, edital_com_perfis):
    """`replace_draft` substitui o rascunho inteiro: o que não viajar junto é apagado."""
    identificar(client, "ana.elaboradora", ["elaborador"])

    client.post(
        reverse("interface:compor-etapa", args=[edital_com_perfis.id, "inscricao"]),
        _campos(edital_com_perfis),
    )

    assert edital_com_perfis.perfis.count() == 2
    assert EventoCronograma.objects.filter(cronograma__edital=edital_com_perfis).count() == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_sem_evento_designado_o_edital_continua_gravavel(client, seletor_ligado, edital_com_perfis):
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = client.post(
        reverse("interface:compor-etapa", args=[edital_com_perfis.id, "inscricao"]),
        _campos(edital_com_perfis, **{"periodo-inscricoes": ""}),
    )

    assert resposta.status_code == 302
    assert not EventoCronograma.objects.filter(
        cronograma__edital=edital_com_perfis, is_registration_period=True
    ).exists()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_recusa_do_dominio_preserva_o_que_foi_digitado(client, seletor_ligado, edital_com_perfis):
    """Chave repetida é recusa de domínio; o preenchimento tem de sobreviver a ela (FR-033)."""
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = client.post(
        reverse("interface:compor-etapa", args=[edital_com_perfis.id, "inscricao"]),
        _campos(edital_com_perfis, **{"documento-1-key": "identificacao"}),
    )

    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert "chave" in corpo.lower()
    assert "Diploma de graduação" in corpo, "o que a pessoa digitou não se perde na recusa"
    assert DocumentoExigido.objects.count() == 0


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_linha_nova_conhece_os_perfis_daquele_edital(client, seletor_ligado, edital_com_perfis):
    """O fragmento é escopado ao Edital: sem isso, a linha nasceria com listas vazias."""
    identificar(client, "ana.elaboradora", ["elaborador"])

    corpo = client.get(
        reverse("interface:fragmento-documento", args=[edital_com_perfis.id])
    ).content.decode()

    assert "DOC-INFO" in corpo
    assert "PPP" in corpo
    assert "Todos os Perfis" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_tela_oferece_o_modelo_e_grava_a_escolha(client, seletor_ligado, edital_com_perfis):
    """FR-020 da 020 — o requisito aponta o Anexo que serve de modelo, pela tela de quem elabora.

    Enquanto a tela não desenhava o campo, o vínculo sobrevivia por preservação. Agora ela desenha,
    e preservá-lo passaria a ser o defeito oposto: a escolha nova seria sobrescrita pela antiga a
    cada gravação, e a pessoa veria o formulário aceitar e o banco ignorar.
    """
    from tests.fixtures.anexos import criar_anexo

    identificar(client, "ana.elaboradora", ["elaborador"])
    anexo = criar_anexo(edital_com_perfis, rotulo="ANEXO I — REQUERIMENTO", order=1)

    client.post(
        reverse("interface:compor-etapa", args=[edital_com_perfis.id, "inscricao"]),
        _campos(edital_com_perfis, **{"documento-0-attachmentId": str(anexo.id)}),
    )
    corpo = client.get(
        reverse("interface:compor-etapa", args=[edital_com_perfis.id, "inscricao"])
    ).content.decode()

    assert "Modelo que o Edital fornece" in corpo
    assert "ANEXO I — REQUERIMENTO" in corpo
    documento = DocumentoExigido.objects.get(edital=edital_com_perfis, key="identificacao")
    assert documento.anexo_id == anexo.id


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_desfazer_a_escolha_do_modelo_e_possivel(client, seletor_ligado, edital_com_perfis):
    """ "Não fornece modelo" é escolha legítima, e precisa ser alcançável depois de ter havido um."""
    from tests.fixtures.anexos import criar_anexo

    identificar(client, "ana.elaboradora", ["elaborador"])
    anexo = criar_anexo(edital_com_perfis, rotulo="ANEXO I — REQUERIMENTO", order=1)
    client.post(
        reverse("interface:compor-etapa", args=[edital_com_perfis.id, "inscricao"]),
        _campos(edital_com_perfis, **{"documento-0-attachmentId": str(anexo.id)}),
    )

    client.post(
        reverse("interface:compor-etapa", args=[edital_com_perfis.id, "inscricao"]),
        _campos(edital_com_perfis, **{"documento-0-attachmentId": ""}),
    )

    assert (
        DocumentoExigido.objects.get(edital=edital_com_perfis, key="identificacao").anexo_id is None
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_vinculo_com_o_modelo_sobrevive_a_gravar_outra_etapa(
    client, seletor_ligado, edital_com_perfis
):
    """O segundo caminho de perda, e o mais silencioso: a etapa que nem menciona documentos.

    Ao gravar `conteudo`, a view remonta as cinco coleções a partir do banco e as reenvia inteiras.
    Um campo que `documentos_persistidos` não emitisse voltaria nulo por essa porta.
    """
    from tests.fixtures.anexos import criar_anexo

    identificar(client, "ana.elaboradora", ["elaborador"])
    anexo = criar_anexo(edital_com_perfis, rotulo="ANEXO I — REQUERIMENTO", order=1)
    client.post(
        reverse("interface:compor-etapa", args=[edital_com_perfis.id, "inscricao"]),
        _campos(edital_com_perfis),
    )
    DocumentoExigido.objects.filter(edital=edital_com_perfis, key="identificacao").update(
        anexo=anexo
    )

    client.post(
        reverse("interface:compor-etapa", args=[edital_com_perfis.id, "conteudo"]),
        {"secao-0-key": "objeto", "secao-0-content": "Texto do objeto."},
    )

    documento = DocumentoExigido.objects.get(edital=edital_com_perfis, key="identificacao")
    assert documento.anexo_id == anexo.id
