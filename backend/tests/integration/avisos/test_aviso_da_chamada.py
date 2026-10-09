"""O aviso da chamada comunicada por publicação (066, US3, `D-003`, `FR-1245`, `FR-1251`).

**O universo é histórico, e a elegibilidade é de agora.** O aviso registra todas as convocações que
a publicação fez, e manda a mensagem só a quem segue convocado. Dizer "você está entre as
convocadas" a quem já desistiu, ou a quem o prazo já passou, induziria a pessoa a crer que a
convocação encerrada continua valendo.

**E no Perfil que convoca por mensagem individual, não há aviso** (`D-001`): ali a mensagem que
conta já saiu, e é dela que o prazo corre.
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.avisos.domain import nomes
from processo_seletivo.avisos.models import Aviso, DestinatarioDoAviso
from processo_seletivo.convocacao.application import selectors
from processo_seletivo.convocacao.application.comunicar import comunicar
from processo_seletivo.convocacao.application.desfechar import desfechar
from processo_seletivo.convocacao.domain import nomes as nomes_da_convocacao
from processo_seletivo.convocacao.models import ComunicacaoEmitida, Convocacao
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import FORMA_POR_PUBLICACAO
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.avisos import avisar_chamada
from tests.fixtures.convocacao import convocar, montar_cenario_da_convocacao
from tests.fixtures.corte import MARCO, regra
from tests.fixtures.edital import PROFILE_ID

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

REFERENCIA = "Site do Cefor, 09/10/2026, 2ª chamada do Edital."


def _fila(edital):
    return selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )["fila"]


def _convocar_e_publicar(edital, gestor, inscricao, chave, *, referencia=REFERENCIA):
    convocada = convocar(
        edital,
        gestor,
        inscricao,
        vencimento=timezone.now() + timedelta(days=3),
        idempotency_key=f"{chave}-conv",
    )
    comunicar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocada["id"],
        idempotency_key=f"{chave}-com",
        correlation_id="teste-066",
        referencia_da_publicacao=referencia,
    )
    return convocada


@pytest.fixture
def chamada_publicada(gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Duas vagas, dois titulares convocados na mesma publicação — e um deles desistiu depois."""
    edital, _, _ = montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="aviso-066-chamada",
        forma=FORMA_POR_PUBLICACAO,
        geral=2,
        cut=regra(surplusCount=1),
    )
    fila = _fila(edital)
    primeira = _convocar_e_publicar(edital, gestor, fila[0], "titular-1")
    segunda = _convocar_e_publicar(edital, gestor, fila[1], "titular-2")
    desfechar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=segunda["id"],
        especie=nomes_da_convocacao.DESISTENCIA_EXPRESSA,
        fundamento="Desistência registrada em processo.",
        idempotency_key="titular-2-desiste",
        correlation_id="teste-066",
    )
    ancora = ComunicacaoEmitida.objects.filter(convocacao_id=primeira["id"]).get()
    return edital, primeira, segunda, ancora


def test_o_universo_e_a_publicacao_inteira_e_a_mensagem_vai_a_quem_segue(chamada_publicada, gestor):
    edital, primeira, segunda, ancora = chamada_publicada

    declarado = avisar_chamada(edital, MARCO, ancora.id, ator=gestor, agora=timezone.now())

    aviso = Aviso.objects.get(pk=declarado["aviso"])
    assert aviso.origem == nomes.CHAMADA
    assert aviso.referencia_da_publicacao == REFERENCIA
    linhas = {
        str(d.convocacao_id): d.elegibilidade
        for d in DestinatarioDoAviso.objects.filter(aviso=aviso)
    }
    assert linhas == {
        str(primeira["id"]): nomes.ELEGIVEL,
        str(segunda["id"]): nomes.NAO_ELEGIVEL_DESFECHO,
    }
    assert declarado["destinatarios"] == 1


def test_o_rodape_diz_que_o_prazo_nao_corre_do_aviso(chamada_publicada, gestor):
    edital, _, _, ancora = chamada_publicada

    declarado = avisar_chamada(edital, MARCO, ancora.id, ator=gestor, agora=timezone.now())

    corpo = Aviso.objects.get(pk=declarado["aviso"]).corpo
    assert "e não do recebimento deste aviso" in corpo
    assert REFERENCIA in corpo


def test_nenhum_registro_de_convocacao_muda(chamada_publicada, gestor):
    edital, primeira, segunda, ancora = chamada_publicada
    antes = list(Convocacao.objects.order_by("id").values())
    comunicacoes = ComunicacaoEmitida.objects.count()

    avisar_chamada(edital, MARCO, ancora.id, ator=gestor, agora=timezone.now())

    assert list(Convocacao.objects.order_by("id").values()) == antes
    assert ComunicacaoEmitida.objects.count() == comunicacoes, "o aviso não toca a comunicação"


def test_todas_vencidas_e_recusado(chamada_publicada, gestor, monkeypatch):
    edital, _, _, ancora = chamada_publicada
    real = timezone.now
    monkeypatch.setattr(timezone, "now", lambda: real() + timedelta(days=4))

    with pytest.raises(DomainError) as erro:
        avisar_chamada(edital, MARCO, ancora.id, ator=gestor, agora=timezone.now())

    assert erro.value.code == nomes.AVISO_SEM_ELEGIVEL


def test_avisar_de_novo_exige_justificativa(chamada_publicada, gestor):
    edital, _, _, ancora = chamada_publicada
    avisar_chamada(edital, MARCO, ancora.id, ator=gestor, agora=timezone.now(), chave="primeiro")

    with pytest.raises(DomainError) as erro:
        avisar_chamada(edital, MARCO, ancora.id, ator=gestor, agora=timezone.now(), chave="segundo")

    assert erro.value.code == nomes.AVISO_JUSTIFICATIVA_OBRIGATORIA


def test_o_publicador_sem_base_de_comissao_nao_alcanca(chamada_publicada):
    edital, _, _, ancora = chamada_publicada
    publicador = ator_institucional("so-publica", nomes.PERMISSAO, "resultado:publicar")

    with pytest.raises(DomainError) as erro:
        avisar_chamada(edital, MARCO, ancora.id, ator=publicador, agora=timezone.now())

    assert erro.value.status == 404


def test_mensagem_individual_nao_tem_aviso(
    gestor, api_client, manager_headers, process_payload, raiz_de_arquivos, settings
):
    """`FR-1245`: no Perfil que convoca por mensagem individual, o aviso é recusado."""
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    edital, _, _ = montar_cenario_da_convocacao(
        gestor, api_client, manager_headers, process_payload, prefixo="aviso-066-individual"
    )
    convocada = convocar(
        edital,
        gestor,
        _fila(edital)[0],
        vencimento=timezone.now() + timedelta(days=3),
        idempotency_key="individual-conv",
    )
    comunicar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocada["id"],
        idempotency_key="individual-com",
        correlation_id="teste-066",
    )
    comunicacao = ComunicacaoEmitida.objects.get(convocacao_id=convocada["id"])

    with pytest.raises(DomainError) as erro:
        avisar_chamada(edital, MARCO, comunicacao.id, ator=gestor, agora=timezone.now())

    assert erro.value.code == nomes.AVISO_CHAMADA_POR_MENSAGEM_INDIVIDUAL


def test_a_tela_da_convocacao_oferece_o_aviso_por_publicacao(chamada_publicada, client, settings):
    """`UX-174`: uma linha por referência, e não um botão por convocação."""
    from django.urls import reverse

    from tests.interface.conftest import identificar

    settings.INTERFACE_SELETOR_IDENTIDADE = True
    edital, _, _, _ = chamada_publicada
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(reverse("interface:convocacao", args=[edital.id, MARCO])).content.decode()

    assert corpo.count("Avisar os convocados desta publicação") == 1
    assert REFERENCIA in corpo
    assert "2 convocações" in corpo
