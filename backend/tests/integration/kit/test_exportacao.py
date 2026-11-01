"""A exportação e a desatualização (111, FR-3435, FR-3436, FR-3439, FR-3440, FR-3445, FR-3446).

O registro é o evento `EXPORTAR_MATERIAL` na trilha do Edital, e a desatualização é a comparação da
ficha de agora com as exportações registradas. Abrir a tela não registra.
"""

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.portal import ficha as fichas
from processo_seletivo.processos.application.finalizacao import cancel_edital
from tests.fixtures import editais_do_piloto, kit
from tests.interface.conftest import identificar

pytestmark = pytest.mark.django_db


def _tela(client, edital):
    return client.get(reverse("interface:kit-de-divulgacao", args=[edital.id]))


def _impressao(edital):
    return fichas.ler(edital, agora=timezone.now(), base_url=None).impressao


def _exportar(client, edital, formato="md", impressao=None):
    return client.post(
        reverse("interface:kit-de-divulgacao-exportar", args=[edital.id, formato]),
        {"impressao": impressao or _impressao(edital)},
    )


def _eventos(edital):
    return RegistroAuditoria.objects.filter(
        aggregate_id=edital.id, operation="EXPORTAR_MATERIAL"
    ).order_by("occurred_at")


@pytest.fixture
def comunicacao(client, seletor_ligado):
    identificar(client, "cora.comunicacao", ["comunicacao"])
    return client


def test_md_e_txt_registram_e_abrir_nao(api_client, comunicacao):
    edital = kit.publicar(api_client, ate=1, chave="exp-registra")
    _tela(comunicacao, edital)
    assert not _eventos(edital).exists()

    md = _exportar(comunicacao, edital, "md")
    txt = _exportar(comunicacao, edital, "txt")
    assert md.status_code == txt.status_code == 200
    assert md["Content-Disposition"] == 'attachment; filename="kit-91-2026.md"'
    assert md["X-Content-Type-Options"] == "nosniff"
    assert "## Legenda para rede social" in md.content.decode()
    assert txt.content.decode().startswith("INFORMAÇÕES OFICIAIS")
    assert [e.detalhe["formato"] for e in _eventos(edital)] == ["md", "txt"]


def test_detalhe_do_evento_e_nao_e_transicao(api_client, comunicacao):
    edital = kit.publicar(api_client, ate=1, chave="exp-detalhe")
    _exportar(comunicacao, edital)
    evento = _eventos(edital).get()
    assert evento.previous_state == evento.new_state == "PUBLICADO"
    assert evento.permission == "material:gerar"
    detalhe = evento.detalhe
    assert set(detalhe) >= {"formato", "versao", "impressao", "versao_da_impressao", "campos"}
    assert detalhe["impressao"] == _impressao(edital)
    assert all("perfil_id" in oferta for oferta in detalhe["campos"]["ofertas"])


def test_o_kit_nao_grava_nada_alem_do_evento(api_client, comunicacao):
    edital = kit.publicar(api_client, ate=1, chave="exp-so-evento")
    antes = RegistroAuditoria.objects.count()
    revisao = edital.revision
    _exportar(comunicacao, edital)
    edital.refresh_from_db()
    assert RegistroAuditoria.objects.count() == antes + 1
    assert edital.revision == revisao


def test_sem_exportacao_sem_faixa(api_client, comunicacao):
    edital = kit.publicar(api_client, ate=1, chave="exp-sem-faixa")
    assert "desatualizado" not in _tela(comunicacao, edital).content.decode()


def test_prorrogacao_gera_a_faixa_e_a_exportacao_antiga_continua_listada(api_client, comunicacao):
    edital = kit.publicar(api_client, ate=1, chave="exp-prorroga")
    _exportar(comunicacao, edital)
    kit.retificar(api_client, edital, "91", 2, chave="exp-prorroga")
    corpo = _tela(comunicacao, edital).content.decode()
    assert "desatualizado" in corpo
    assert "término das inscrições:" in corpo
    assert "→" in corpo

    _exportar(comunicacao, edital)  # a nova exportação não apaga o aviso da antiga
    corpo = _tela(comunicacao, edital).content.decode()
    assert corpo.count("desatualizado.") == 1


def test_retificacao_de_secao_nao_gera_faixa(api_client, comunicacao):
    edital = kit.publicar(api_client, "92", ate=1, chave="exp-secao")
    _exportar(comunicacao, edital)
    kit.retificar_secao(api_client, edital, suffix="exp-secao")
    assert "desatualizado" not in _tela(comunicacao, edital).content.decode()


def test_edital_mudado_entre_tela_e_exportacao(api_client, comunicacao):
    edital = kit.publicar(api_client, ate=1, chave="exp-mudou")
    conferida = _impressao(edital)
    kit.retificar(api_client, edital, "91", 2, chave="exp-mudou")
    resposta = _exportar(comunicacao, edital, impressao=conferida)
    assert resposta.status_code == 409
    assert "O Edital mudou desde que você abriu o kit" in resposta.content.decode()
    assert not _eventos(edital).exists()


def test_desfecho_depois_da_exportacao(api_client, comunicacao):
    edital = kit.publicar(api_client, ate=1, chave="exp-desfecho")
    _exportar(comunicacao, edital)
    edital.refresh_from_db()
    cancel_edital(
        actor=editais_do_piloto.GESTORA,
        edital_id=edital.id,
        expected_revision=edital.revision,
        reason="Cancelamento para o teste do kit.",
        idempotency_key=f"cancelar-kit-{edital.id}",
        correlation_id="111-desfecho",
    )
    corpo = _tela(comunicacao, edital).content.decode()
    assert "O material exportado deve sair de circulação." in corpo
    assert "Edital cancelado" in corpo
    assert _exportar(comunicacao, edital).status_code == 409


def test_retificacao_a_vigorar_e_anunciada(api_client, comunicacao):
    edital = kit.publicar(api_client, "01", chave="exp-a-vigorar")
    assert (
        "Há Retificação publicada que passa a valer em"
        in _tela(comunicacao, edital).content.decode()
    )


def test_impressao_de_versao_anterior(api_client, comunicacao):
    edital = kit.publicar(api_client, ate=1, chave="exp-versao")
    _exportar(comunicacao, edital)
    evento = _eventos(edital).get()
    # A trilha é append-only: a versão antiga se simula numa cópia do detalhe.
    antigo = dict(evento.detalhe, versao_da_impressao=0, impressao="outra")
    ficha = fichas.ler(edital, agora=timezone.now(), base_url=None)
    comparavel, _ = fichas.desatualizacoes([dict(antigo, exportado_em="x")], ficha)
    assert comparavel == []  # mesmos campos, recalculados: nada mudou
    sem_campos, _ = fichas.desatualizacoes(
        [{"versao_da_impressao": 0, "impressao": "outra", "exportado_em": "x"}], ficha
    )
    assert [item.comparavel for item in sem_campos] == [False]
