"""O sistema propõe, a presidência confirma — e o ato registrado é o da confirmação (FR-107).

O que este arquivo protege é a distinção que FR-017, FR-018 e FR-019 existem para manter: o que a
spec recusa é decisão de distribuição **sem autor**, e não decisão tomada com ajuda. Por isso três
coisas precisam continuar verdadeiras, e cada uma tem teste aqui:

- propor não grava nada;
- o que a presidência confirma é exatamente o que executa, conferido sob trava;
- cada Atribuição criada continua tendo o seu evento, com quem confirmou.
"""

import pytest

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.avaliacoes.application.distribuicao import (
    ATRIBUIR,
    confirmar_rodizio,
    propor_rodizio,
)
from processo_seletivo.avaliacoes.application.impedimento import registrar_impedimento
from processo_seletivo.avaliacoes.models import Atribuicao
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.mesa import distribuir_para, inscricoes_de, montar_banca

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    return montar_banca(
        gestor,
        api_client,
        manager_headers,
        seed=31,
        codigo="RD",
        avaliadores=("joao", "ana", "bruno", "carla"),
    )


@pytest.fixture
def dez(cenario):
    return inscricoes_de(cenario, 10, primeiro=3100)


def todos(cenario):
    return [cenario["membros"][nome].id for nome in ("joao", "ana", "bruno", "carla")]


def propor(cenario, gestor, nomes=None):
    return propor_rodizio(
        actor=gestor,
        processo=cenario["processo"],
        edital_id=cenario["edital"].id,
        etapa_id=cenario["etapa"],
        membro_ids=[cenario["membros"][n].id for n in nomes] if nomes else todos(cenario),
    )


def confirmar(cenario, gestor, proposta, *, chave="rodizio"):
    return confirmar_rodizio(
        actor=gestor,
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["etapa"],
        membro_ids=proposta["membro_ids"],
        assinatura=proposta["assinatura"],
        idempotency_key=chave,
        correlation_id="teste",
    )


def test_propor_nao_grava_nada(cenario, gestor, dez):
    """A proposta é leitura. Se ela gravasse, a confirmação não seria o ato — seria enfeite."""
    proposta = propor(cenario, gestor)

    assert proposta["total"] == 20
    assert not Atribuicao.objects.filter(edital=cenario["edital"]).exists()
    assert not RegistroAuditoria.objects.filter(operation=ATRIBUIR).exists()


def test_a_proposta_equilibra_a_carga(cenario, gestor, dez):
    """Dez inscrições, duas avaliações, quatro pessoas: cinco para cada, e não sobra ninguém."""
    proposta = propor(cenario, gestor)

    recebidas = sorted(linha["recebe"] for linha in proposta["por_pessoa"])
    assert recebidas == [5, 5, 5, 5]
    assert proposta["inscricoes"] == 10
    assert not proposta["fora"]


def test_a_proposta_parte_da_carga_que_ja_existe(cenario, gestor, dez):
    """Propor sobre uma banca que já trabalhou não pode ignorar o que ela já recebeu."""
    distribuir_para(cenario, gestor, ["joao"], dez[:4], chave="antes")

    proposta = propor(cenario, gestor)
    por_nome = {linha["membro"].identity_subject: linha for linha in proposta["por_pessoa"]}

    assert por_nome["joao"]["antes"] == 4
    # Quem já tem carga recebe menos, e todos terminam no mesmo lugar.
    assert len({linha["depois"] for linha in proposta["por_pessoa"]}) == 1


def test_a_proposta_respeita_impedimento_e_conclusao_anterior(cenario, gestor, dez):
    """As mesmas regras do lote manual, porque a regra é do domínio e não da tela."""
    registrar_impedimento(
        actor=gestor,
        processo_id=cenario["processo"].id,
        identity_subject="joao",
        inscricao_id=dez[0].id,
        motivo="Parentesco.",
        idempotency_key="rd-imp",
        correlation_id="teste",
    )

    proposta = propor(cenario, gestor)
    confirmar(cenario, gestor, proposta)

    assert not Atribuicao.objects.filter(
        inscricao=dez[0], membro__identity_subject="joao", ativo=True
    ).exists()
    assert Atribuicao.objects.filter(inscricao=dez[0], ativo=True).count() == 2


def test_confirmar_grava_exatamente_a_proposta(cenario, gestor, dez):
    """O que se confirma é o que executa — e cada Atribuição tem o seu evento (FR-016)."""
    proposta = propor(cenario, gestor)

    resultado = confirmar(cenario, gestor, proposta)

    assert resultado["feitas"] == proposta["total"] == 20
    assert Atribuicao.objects.filter(edital=cenario["edital"], ativo=True).count() == 20
    assert RegistroAuditoria.objects.filter(operation=ATRIBUIR).count() == 20
    assert {e.actor_subject for e in RegistroAuditoria.objects.filter(operation=ATRIBUIR)} == {
        gestor.subject
    }


def test_a_proposta_que_mudou_no_intervalo_e_recusada(cenario, gestor, dez):
    """FR-107. Entre ver e confirmar, o mundo anda — e confirmar um plano executando outro é a
    mesma falha de FR-041, distribuída por seiscentas linhas."""
    proposta = propor(cenario, gestor)
    # Alguém recebe uma inscrição nesse intervalo: quem recebe o quê muda, o total não.
    distribuir_para(cenario, gestor, ["ana"], dez[:1], chave="intervalo")

    with pytest.raises(DomainError) as recusa:
        confirmar(cenario, gestor, proposta, chave="tarde")

    assert recusa.value.code == "proposta_mudou"
    assert Atribuicao.objects.filter(edital=cenario["edital"], ativo=True).count() == 1


def test_a_nova_proposta_sobre_o_estado_atual_e_aceita(cenario, gestor, dez):
    """A recusa é para conferir, e não para impedir."""
    distribuir_para(cenario, gestor, ["ana"], dez[:1], chave="antes")

    proposta = propor(cenario, gestor)
    resultado = confirmar(cenario, gestor, proposta, chave="depois")

    assert resultado["feitas"] == 19
    assert Atribuicao.objects.filter(edital=cenario["edital"], ativo=True).count() == 20


def test_confirmar_duas_vezes_com_a_mesma_chave_nao_duplica(cenario, gestor, dez):
    """FR-084: repetir devolve o desfecho original, sem criar nada e sem evento novo."""
    proposta = propor(cenario, gestor)
    primeiro = confirmar(cenario, gestor, proposta, chave="mesma")
    segundo = confirmar(cenario, gestor, proposta, chave="mesma")

    assert primeiro == segundo
    assert Atribuicao.objects.filter(edital=cenario["edital"], ativo=True).count() == 20
    assert RegistroAuditoria.objects.filter(operation=ATRIBUIR).count() == 20


def test_o_que_nao_cabe_na_proposta_e_declarado(cenario, gestor, dez):
    """Duas vagas e uma pessoa elegível: a inscrição fica incompleta, e a proposta diz isso.

    Completar com quem não pode seria o sistema decidindo contra uma regra; ficar calado seria
    entregar uma proposta que não cobre o que promete. Ela declara a lacuna.
    """
    for nome in ("ana", "bruno", "carla"):
        registrar_impedimento(
            actor=gestor,
            processo_id=cenario["processo"].id,
            identity_subject=nome,
            inscricao_id=dez[0].id,
            motivo="Impedimento declarado.",
            idempotency_key=f"rd-{nome}",
            correlation_id="teste",
        )

    proposta = propor(cenario, gestor)

    assert len(proposta["fora"]) == 1
    fora = proposta["fora"][0]
    assert fora["inscricao"] == (dez[0].protocolo or str(dez[0].id))
    assert fora["faltam"] == 1
    assert "Só 1 das 4 pessoas" in fora["motivo"]

    # E o que cabe é distribuído: a inscrição fica com uma avaliação, e não com nenhuma.
    confirmar(cenario, gestor, proposta)
    assert Atribuicao.objects.filter(inscricao=dez[0], ativo=True).count() == 1


def test_o_caminho_manual_continua_intocado(cenario, gestor, dez):
    """O rodízio é uma porta a mais, e não a substituição da escolha inscrição por inscrição."""
    distribuir_para(cenario, gestor, ["joao", "ana"], dez[:2], chave="manual")

    assert Atribuicao.objects.filter(edital=cenario["edital"], ativo=True).count() == 4
