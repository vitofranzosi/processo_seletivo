"""Convocar os titulares num ato só, e comunicar cada um no mesmo gesto (050, US1).

**O cenário é o do 77/2026**: duas vagas, dois titulares e uma suplente. O gesto alcança os dois
titulares e para na suplente — chamar a vaga que vagou continua sendo a chamada individual.
"""

from datetime import timedelta
from unittest import mock

import pytest
from django.core import mail
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.convocacao.application import fluxo
from processo_seletivo.convocacao.domain import alcance, nomes
from processo_seletivo.convocacao.models import ComunicacaoEmitida, Convocacao
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.convocacao import convocar
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID

pytestmark = pytest.mark.django_db(transaction=True)

VENCIMENTO = timezone.now() + timedelta(days=3)


def previa(edital):
    return fluxo.previa_dos_titulares(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)


def confirmar(edital, ator, assinatura, *, chave="lote-titulares", **kwargs):
    argumentos = {
        "actor": ator,
        "processo_id": edital.processo_id,
        "edital_id": edital.id,
        "perfil_id": PROFILE_ID,
        "marco_id": MARCO,
        "alcance_confirmado": assinatura,
        "idempotency_key": chave,
        "vencimento": VENCIMENTO,
    }
    argumentos.update(kwargs)
    return fluxo.convocar_titulares(**argumentos)


def test_a_previa_declara_os_titulares_e_para_na_suplente_sem_praticar_nada(cenario_do_77):
    """`FR-862`: quem, em que ordem, com que espécie — e quem fica de fora, e por quê."""
    edital, _, _ = cenario_do_77

    declarada = previa(edital)

    assert [p["posicao"] for p in declarada["pessoas"]] == [1, 2]
    assert {p["especie"] for p in declarada["pessoas"]} == {nomes.VAGA_INICIAL}
    assert declarada["parada"]["motivo"] == alcance.PARADA_SUPLENTE
    assert declarada["impedimento"] is None
    assert "Convocação para vaga inicial" in declarada["fundamento"]
    assert Convocacao.objects.count() == 0, "abrir a prévia não convoca ninguém"


def test_a_confirmacao_convoca_cada_titular_e_comunica_cada_um(cenario_do_77, gestor):
    """`FR-860`, `FR-866`, `FR-871`: N registros, o mesmo vencimento, N mensagens."""
    edital, _, _ = cenario_do_77
    declarada = previa(edital)

    resultado = confirmar(
        edital, gestor, declarada["assinatura"], complemento="No interesse da Administração."
    )

    assert len(resultado["convocadas"]) == 2
    assert resultado["enviadas"] == 2 and resultado["falhas"] == 0
    assert len(mail.outbox) == 2
    convocacoes = list(Convocacao.objects.order_by("criado_em"))
    assert {c.especie for c in convocacoes} == {nomes.VAGA_INICIAL}
    assert {c.vencimento for c in convocacoes} == {VENCIMENTO}
    for convocacao in convocacoes:
        assert convocacao.fundamento.startswith("Convocação para vaga inicial no Edital nº")
        assert convocacao.fundamento.endswith("Complemento: No interesse da Administração.")
        assert convocacao.criado_por == gestor.subject


def test_a_trilha_tem_uma_linha_por_pessoa_com_a_correlacao_do_gesto(cenario_do_77, gestor):
    """`FR-880`, `SC-324`: cada registro auditado, e o gesto reconstruível pela correlação."""
    edital, _, _ = cenario_do_77

    confirmar(edital, gestor, previa(edital)["assinatura"], chave="trilha")

    linhas = RegistroAuditoria.objects.filter(
        correlation_id=fluxo.correlacao_do_gesto("trilha"), operation="CONVOCACAO_CONVOCAR"
    )
    assert linhas.count() == 2
    assert all("informado neste ato" in linha.reason for linha in linhas)


def test_o_alcance_que_mudou_recusa_sem_gravar_nada(cenario_do_77, gestor):
    """`FR-863`, `SC-325`: entre a prévia e a confirmação, alguém convocou um dos titulares."""
    edital, _, _ = cenario_do_77
    declarada = previa(edital)
    convocar(edital, gestor, declarada["pessoas"][0]["id"], idempotency_key="no-meio")

    with pytest.raises(DomainError) as recusa:
        confirmar(edital, gestor, declarada["assinatura"])

    assert recusa.value.code == nomes.ALCANCE_MUDOU
    assert Convocacao.objects.count() == 1, "só a convocação individual existe"


def test_repetir_a_confirmacao_nao_convoca_nem_comunica_de_novo(cenario_do_77, gestor):
    """`FR-865`: o duplo clique devolve o ato original."""
    edital, _, _ = cenario_do_77
    assinatura = previa(edital)["assinatura"]

    primeira = confirmar(edital, gestor, assinatura, chave="duplo")
    segunda = confirmar(edital, gestor, assinatura, chave="duplo")

    assert segunda["convocadas"] == primeira["convocadas"]
    assert Convocacao.objects.count() == 2
    assert len(mail.outbox) == 2


def test_a_falha_de_um_envio_nao_desfaz_nem_impede_os_outros(cenario_do_77, gestor):
    """`FR-872`, `FR-873`: a convocação continua, e o prazo daquela pessoa não corre."""
    edital, _, _ = cenario_do_77
    alvo = "processo_seletivo.convocacao.application.comunicar.send_mail"

    with mock.patch(alvo, side_effect=[ConnectionError("smtp"), 1]):
        resultado = confirmar(edital, gestor, previa(edital)["assinatura"])

    assert resultado["enviadas"] == 1 and resultado["falhas"] == 1
    assert Convocacao.objects.count() == 2
    assert ComunicacaoEmitida.objects.filter(resultado="FALHA").count() == 1


def test_vencimento_passado_recusa_antes_de_gravar(cenario_do_77, gestor):
    """`FR-269b` no gesto: prazo vencido ao nascer não é prazo."""
    edital, _, _ = cenario_do_77

    with pytest.raises(DomainError) as recusa:
        confirmar(
            edital,
            gestor,
            previa(edital)["assinatura"],
            vencimento=timezone.now() - timedelta(minutes=1),
        )

    assert recusa.value.code == nomes.VENCIMENTO_ANTERIOR_AO_ENVIO
    assert Convocacao.objects.count() == 0


def test_edital_sem_forma_declarada_impede_o_gesto(cenario_sem_forma, gestor):
    """`FR-875`, `D-002`: convocar ali produziria chamadas que nunca poderiam ser comunicadas."""
    edital, _, _ = cenario_sem_forma
    declarada = previa(edital)

    assert declarada["impedimento"]["codigo"] == nomes.FORMA_DE_COMUNICACAO_NAO_DECLARADA
    with pytest.raises(DomainError) as recusa:
        confirmar(edital, gestor, declarada["assinatura"])
    assert recusa.value.code == nomes.FORMA_DE_COMUNICACAO_NAO_DECLARADA
    assert Convocacao.objects.count() == 0


def test_por_publicacao_o_prazo_espera_a_referencia(cenario_por_publicacao, gestor):
    """`FR-876`: o ato convoca, e o gesto das pendentes registra onde a lista foi publicada."""
    edital, _, _ = cenario_por_publicacao

    resultado = confirmar(edital, gestor, previa(edital)["assinatura"])

    assert resultado["aguardandoPublicacao"] == len(resultado["convocadas"]) > 0
    assert ComunicacaoEmitida.objects.count() == 0
    pendentes = fluxo.previa_das_pendentes(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    comum = {
        "actor": gestor,
        "processo_id": edital.processo_id,
        "edital_id": edital.id,
        "perfil_id": PROFILE_ID,
        "marco_id": MARCO,
        "alcance_confirmado": pendentes["assinatura"],
        "idempotency_key": "publicou",
    }
    with pytest.raises(DomainError) as recusa:
        fluxo.emitir_pendentes(**comum)
    assert recusa.value.code == nomes.REFERENCIA_DA_PUBLICACAO_OBRIGATORIA

    emitidas = fluxo.emitir_pendentes(**comum, referencia_da_publicacao="Site do Cefor, 28/09/2026")

    assert emitidas["enviadas"] == len(resultado["convocadas"])
    assert set(ComunicacaoEmitida.objects.values_list("referencia_da_publicacao", flat=True)) == {
        "Site do Cefor, 28/09/2026"
    }


def test_so_um_titular_e_a_suplente_de_fora(cenario_com_suplente, gestor):
    """Quadro de uma vaga: o gesto alcança o titular, e a suplente não entra (`FR-861`)."""
    edital, _, _ = cenario_com_suplente

    resultado = confirmar(edital, gestor, previa(edital)["assinatura"])

    assert len(resultado["convocadas"]) == 1
    assert Convocacao.objects.get().especie == nomes.VAGA_INICIAL


def test_quem_nao_tem_base_de_comissao_recebe_404(cenario_do_77, sem_nada):
    """`FR-887`: os gestos não criam autoridade, e negam como a chamada individual nega."""
    edital, _, _ = cenario_do_77

    with pytest.raises(DomainError) as recusa:
        confirmar(edital, sem_nada, previa(edital)["assinatura"])

    assert recusa.value.status == 404
    with pytest.raises(DomainError) as recusa:
        fluxo.emitir_pendentes(
            actor=sem_nada,
            processo_id=edital.processo_id,
            edital_id=edital.id,
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            alcance_confirmado="",
            idempotency_key="sem-base",
        )
    assert recusa.value.status == 404
