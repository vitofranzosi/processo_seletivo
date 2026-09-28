"""O não atendimento de todos os vencidos, num gesto — N registros, cada um com autor (050, US3).

**O relógio é adiantado por `mock`**, e só depois dos envios: o prazo corre do envio, e um
vencimento que decorre antes de a mensagem sair não é vencimento nenhum (`FR-269a`).
"""

from datetime import timedelta
from unittest import mock

import pytest
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.convocacao.application import fluxo, selectors
from processo_seletivo.convocacao.application.desfechar import desfechar
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.convocacao.models import DesfechoDaConvocacao
from processo_seletivo.ocupacao.application import selectors as ocupacao_selectors
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID

pytestmark = pytest.mark.django_db(transaction=True)

RECORTE = {"perfil_id": PROFILE_ID, "marco_id": MARCO}


def titulares_convocados(edital, gestor, *, falhar_o_segundo=False):
    """Os dois titulares do 77, com vencimento em uma hora; o segundo envio falha, se pedido."""
    previa = fluxo.previa_dos_titulares(edital=edital, **RECORTE)
    envios = [1, ConnectionError("smtp")] if falhar_o_segundo else [1, 1]
    with mock.patch(
        "processo_seletivo.convocacao.application.comunicar.send_mail", side_effect=envios
    ):
        return fluxo.convocar_titulares(
            actor=gestor,
            processo_id=edital.processo_id,
            edital_id=edital.id,
            alcance_confirmado=previa["assinatura"],
            idempotency_key="titulares-venc",
            vencimento=timezone.now() + timedelta(hours=1),
            **RECORTE,
        )


def depois_do_vencimento():
    adiante = timezone.now() + timedelta(hours=2)
    return mock.patch("django.utils.timezone.now", return_value=adiante)


def gesto(edital, gestor, assinatura, chave="vencidos"):
    return fluxo.registrar_nao_atendimento_dos_vencidos(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        alcance_confirmado=assinatura,
        idempotency_key=chave,
        **RECORTE,
    )


def test_so_o_vencido_com_envio_entra_e_o_nao_iniciado_e_contado(cenario_do_77, gestor):
    """`FR-878`: prazo não iniciado não vence, por mais antiga que seja a data."""
    edital, _, _ = cenario_do_77
    titulares_convocados(edital, gestor, falhar_o_segundo=True)

    with depois_do_vencimento():
        previa = fluxo.previa_dos_vencidos(edital=edital, **RECORTE)

    assert len(previa["linhas"]) == 1
    assert previa["fora"]["naoIniciado"] == 1


def test_o_gesto_registra_um_desfecho_por_pessoa_com_efeito_e_trilha(cenario_do_77, gestor):
    """`FR-877`, `FR-880`, `SC-322`: iguais aos registrados um a um, e reconstruíveis juntos."""
    edital, _, _ = cenario_do_77
    titulares_convocados(edital, gestor)

    with depois_do_vencimento():
        previa = fluxo.previa_dos_vencidos(edital=edital, **RECORTE)
        resultado = gesto(edital, gestor, previa["assinatura"])

    assert len(resultado["desfechos"]) == 2
    desfechos = DesfechoDaConvocacao.objects.all()
    assert {d.especie for d in desfechos} == {nomes.NAO_ATENDIMENTO}
    assert {d.registrado_por for d in desfechos} == {gestor.subject}
    assert all(d.efeito_id for d in desfechos)
    assert all(d.fundamento.startswith("Não atendimento à convocação") for d in desfechos)
    assert (
        RegistroAuditoria.objects.filter(
            correlation_id=fluxo.correlacao_do_gesto("vencidos"),
            operation="CONVOCACAO_DESFECHAR",
        ).count()
        == 2
    )


def test_o_gesto_emite_a_apuracao_seguinte_e_a_suplente_e_a_proxima(cenario_do_77, gestor):
    """`FR-882`, `SC-323`: nenhuma visita à ocupação entre o gesto e a chamada seguinte."""
    edital, _, _ = cenario_do_77
    titulares_convocados(edital, gestor)

    with depois_do_vencimento():
        previa = fluxo.previa_dos_vencidos(edital=edital, **RECORTE)
        resultado = gesto(edital, gestor, previa["assinatura"])
        contexto = selectors.contexto_do_recorte(edital=edital, lista_id=None, **RECORTE)

    assert resultado["apuracaoSeguinte"]["faltando"] == 2
    assert resultado["apuracaoPendente"] is None
    assert contexto["causasDeObsolescencia"] == []
    assert len(contexto["fila"]) == 1, "a suplente é a única chamável"


def test_desfecho_individual_depois_da_previa_muda_o_alcance(cenario_do_77, gestor):
    """`FR-879`, US3 cenário 3: a confirmação é recusada, e nada é gravado."""
    edital, _, _ = cenario_do_77
    convocadas = titulares_convocados(edital, gestor)["convocadas"]

    with depois_do_vencimento():
        previa = fluxo.previa_dos_vencidos(edital=edital, **RECORTE)
        desfechar(
            actor=gestor,
            processo_id=edital.processo_id,
            convocacao_id=convocadas[0]["id"],
            especie=nomes.ACEITE,
            fundamento="Compareceu no prazo.",
            idempotency_key="aceite-no-meio",
            correlation_id="teste",
        )
        with pytest.raises(DomainError) as recusa:
            gesto(edital, gestor, previa["assinatura"])

    assert recusa.value.code == nomes.ALCANCE_MUDOU
    assert DesfechoDaConvocacao.objects.count() == 1


def test_sem_vencida_o_gesto_nao_acontece(cenario_do_77, gestor):
    """Antes do vencimento ninguém está vencido, e o gesto vazio é recusado — não é ato vazio."""
    edital, _, _ = cenario_do_77
    titulares_convocados(edital, gestor)
    previa = fluxo.previa_dos_vencidos(edital=edital, **RECORTE)

    assert previa["linhas"] == []
    assert previa["fora"]["emCurso"] == 2
    with pytest.raises(DomainError) as recusa:
        gesto(edital, gestor, previa["assinatura"])
    assert recusa.value.code == nomes.NENHUMA_CONVOCACAO_VENCIDA


def test_as_outras_especies_continuam_individuais(cenario_do_77, gestor):
    """`FR-881`: o aceite do gesto não existe; o individual continua com o fundamento de quem o
    registra, e a apuração seguinte sai com ele."""
    edital, _, _ = cenario_do_77
    convocadas = titulares_convocados(edital, gestor)["convocadas"]

    resultado = desfechar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocadas[1]["id"],
        especie=nomes.DESISTENCIA_EXPRESSA,
        fundamento="Desistência por escrito, protocolo 123.",
        idempotency_key="desiste",
        correlation_id="teste",
    )

    assert resultado["apuracaoSeguinte"]["faltando"] == 1
    vigente = ocupacao_selectors.apuracao_vigente(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )
    assert vigente.emitida_por == gestor.subject
    assert "Efeito de 1 desfecho" in vigente.motivo_da_sucessao
