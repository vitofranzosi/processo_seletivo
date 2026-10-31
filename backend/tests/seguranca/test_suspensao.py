"""Suspender e reativar uma pessoa em todas as unidades (107, incremento 2, US6 e US7).

As regras são as decisões P1 e P2 do usuário (30/10): suspensão global, sem revogar vínculo, com o
fim de todas as sessões; reativação que devolve os vínculos ainda vigentes e nenhuma sessão.
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, connection, transaction
from django.test import Client
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.seguranca import acessos as catalogo
from processo_seletivo.seguranca.application import acessos, suspensao
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.seguranca.models import (
    ReativacaoDePessoa,
    RevogacaoDeVinculo,
    SuspensaoDePessoa,
    Vinculo,
)
from tests.fixtures import provedor_simulado
from tests.seguranca.apoio import AGORA, ator_do_cliente, entrar, pessoa, vincular

pytestmark = pytest.mark.django_db

LISTA = reverse("interface:lista")


@pytest.fixture
def rita(client, provedor):
    """A administradora institucional, com a sessão aberta neste cliente."""
    alguem = pessoa("rita", nome="Rita Reitoria")
    vincular(
        alguem,
        catalogo.ESCOPO_INSTITUCIONAL,
        catalogo.ADMINISTRADOR_INSTITUCIONAL,
        por="implantacao",
    )
    entrar(client, "rita", nome="Rita Reitoria")
    return alguem


@pytest.fixture
def ana(campus_a):
    alguem = pessoa("ana", nome="Ana Souza", email="ana@ifes.edu.br")
    vincular(alguem, "cefor", "elaborador")
    vincular(alguem, "campus-a", "gestor")
    return alguem


ANA = {"nome": "Ana Souza", "email": "ana@ifes.edu.br"}


def _cliente_de(identificador, **dados):
    # O provedor reinforma nome e e-mail a cada entrada; sem eles, a entrada os apagaria.
    dados = dados or (ANA if identificador == "ana" else {})
    outro = Client()
    entrar(outro, identificador, **dados)
    return outro


def _suspender(client, alvo, motivo="Processo 23.000/2026"):
    rota = reverse("interface:administracao-de-acessos-suspender", args=[alvo.username])
    return client.post(rota, {"acao": "confirmar", "motivo": motivo})


def _reativar(client, alvo, motivo="Fim do afastamento"):
    rota = reverse("interface:administracao-de-acessos-reativar", args=[alvo.username])
    return client.post(rota, {"acao": "confirmar", "motivo": motivo})


# --- US6: suspender -----------------------------------------------------------------------------


def test_a_suspensao_encerra_todas_as_sessoes_sem_revogar_vinculo(client, rita, ana):
    no_escritorio, em_casa = _cliente_de("ana"), _cliente_de("ana")
    assert no_escritorio.get(LISTA).status_code == 200
    assert em_casa.get(LISTA).status_code == 200

    resposta = _suspender(client, ana)

    assert resposta.status_code == 302
    for sessao in (no_escritorio, em_casa):
        assert sessao.get(LISTA)["Location"].startswith(reverse("interface:identificar"))
        assert ator_do_cliente(sessao) is None
    assert not RevogacaoDeVinculo.objects.exists()
    assert Vinculo.objects.filter(pessoa=ana).count() == 2
    evento = RegistroAuditoria.objects.get(operation="PESSOA_SUSPENDER")
    assert (evento.actor_subject, evento.reason) == (rita.username, "Processo 23.000/2026")


def test_a_confirmacao_mostra_o_que_deixa_de_valer_e_nao_grava(client, rita, ana):
    rota = reverse("interface:administracao-de-acessos-suspender", args=[ana.username])
    corpo = client.post(rota, {"acao": "conferir"}).content.decode()

    for esperado in ("Ana Souza", "Unidade campus-a", "Gestor", "Elaborador", "Todas as sessões"):
        assert esperado in corpo, esperado
    assert not SuspensaoDePessoa.objects.exists()


def test_sem_motivo_nada_e_suspenso(client, rita, ana):
    resposta = _suspender(client, ana, motivo=" ")

    assert resposta.status_code == 422
    assert not SuspensaoDePessoa.objects.exists()
    assert get_user_model().objects.get(pk=ana.pk).is_active


def test_a_suspensa_nao_entra_e_ve_a_quem_pedir_sem_o_motivo(client, rita, ana):
    _suspender(client, ana, motivo="Conta comprometida")
    outra = Client()

    resposta = entrar(outra, "ana", **ANA)

    assert resposta.status_code == 403
    corpo = resposta.content.decode()
    assert "acesso à gestão está suspenso" in corpo
    assert "Conta comprometida" not in corpo
    assert "Rita" not in corpo


def test_a_suspensa_nao_aparece_na_busca_nem_recebe_vinculo(client, rita, ana):
    _suspender(client, ana)
    admin = pessoa("admin-cefor", nome="Carlos")
    vincular(admin, "cefor", catalogo.ADMINISTRADOR_DE_ACESSOS)
    ator = Actor(
        admin.username, "cefor", acessos.permissoes_dos_papeis(["administrador-de-acessos"])
    )

    assert acessos.buscar_pessoas(ator, "ana", permissao=catalogo.GERIR, escopo="cefor") == (
        [],
        False,
    )
    with pytest.raises(acessos.DomainError) as recusa:
        acessos.conceder(
            ator, pessoa=ana, escopo="cefor", papel="homologador", motivo="x", now=AGORA
        )
    assert recusa.value.code == acessos.PESSOA_INDISPONIVEL


def test_a_tela_da_unidade_marca_a_suspensa(client, rita, ana):
    _suspender(client, ana)
    admin = pessoa("admin-cefor", nome="Carlos")
    vincular(admin, "cefor", catalogo.ADMINISTRADOR_DE_ACESSOS)
    cliente_do_admin = _cliente_de("admin-cefor", nome="Carlos")

    corpo = cliente_do_admin.get(reverse("interface:acessos")).content.decode()
    linha = corpo.split("Ana Souza")[1].split("</td>")[0]
    assert "suspensa" in linha


def test_ninguem_se_suspende_nem_suspende_a_administracao_institucional(client, rita):
    outra = pessoa("rosa", nome="Rosa Reitoria")
    vincular(
        outra,
        catalogo.ESCOPO_INSTITUCIONAL,
        catalogo.ADMINISTRADOR_INSTITUCIONAL,
        por="implantacao",
    )

    assert _suspender(client, rita).status_code == 403
    assert _suspender(client, outra).status_code == 403
    assert not SuspensaoDePessoa.objects.exists()


def test_so_o_institucional_suspende(client, provedor, ana):
    admin = pessoa("admin-cefor", nome="Carlos")
    vincular(admin, "cefor", catalogo.ADMINISTRADOR_DE_ACESSOS)
    entrar(client, "admin-cefor", nome="Carlos")

    assert _suspender(client, ana).status_code == 403
    assert client.get(reverse("interface:administracao-de-acessos-pessoas")).status_code == 403
    assert not SuspensaoDePessoa.objects.exists()


def test_suspender_quem_ja_esta_suspenso_e_recusado(client, rita, ana):
    _suspender(client, ana)

    assert _suspender(client, ana).status_code == 409
    assert SuspensaoDePessoa.objects.count() == 1


def test_identificador_que_nao_e_de_pessoa_e_nao_encontrado(client, rita):
    rota = reverse("interface:administracao-de-acessos-suspender", args=["gustavo.gestor"])

    assert client.post(rota, {"acao": "conferir"}).status_code == 404


def test_a_implantacao_suspende_e_reativa_a_administracao_institucional(provedor):
    rosa = pessoa("rosa", nome="Rosa")
    vincular(
        rosa, catalogo.ESCOPO_INSTITUCIONAL, catalogo.ADMINISTRADOR_INSTITUCIONAL, por="implantacao"
    )
    sessao = _cliente_de("rosa")
    argumentos = ["--provedor", provedor_simulado.NOME, "--identificador", "rosa"]

    call_command("suspender_pessoa", *argumentos, "--motivo", "Portaria 40")

    assert ator_do_cliente(sessao) is None
    evento = RegistroAuditoria.objects.get(operation="PESSOA_SUSPENDER")
    assert (evento.actor_subject, evento.permission) == ("implantacao", "implantacao")
    call_command("reativar_pessoa", *argumentos, "--motivo", "Portaria 41")
    assert get_user_model().objects.get(pk=rosa.pk).is_active
    with pytest.raises(CommandError, match=suspensao.NAO_SUSPENSA):
        call_command("reativar_pessoa", *argumentos, "--motivo", "Portaria 42")


# --- US7: reativar --------------------------------------------------------------------------------


def test_a_reativacao_devolve_os_vigentes_e_nao_os_revogados(client, rita, ana):
    _suspender(client, ana)
    gestor_no_campus = Vinculo.objects.get(pessoa=ana, escopo="campus-a")
    admin = pessoa("admin-campus", nome="Cida")
    vincular(admin, "campus-a", catalogo.ADMINISTRADOR_DE_ACESSOS)
    acessos.revogar(
        Actor(admin.username, "campus-a", frozenset({catalogo.GERIR})),
        vinculo=gestor_no_campus,
        motivo="Saiu do campus",
        now=AGORA,
    )

    rota = reverse("interface:administracao-de-acessos-reativar", args=[ana.username])
    conferencia = client.post(rota, {"acao": "conferir"}).content.decode()
    assert "Elaborador" in conferencia
    assert "Gestor" not in conferencia.split("Acessos que voltam a valer")[1].split("</section>")[0]
    assert _reativar(client, ana).status_code == 302

    nova = _cliente_de("ana")
    ator = ator_do_cliente(nova)
    assert ator.institution_scope == "cefor"
    assert ator.can("edital:elaborar")
    assert acessos.escopos_vigentes(ana.pk) == ["cefor"]
    assert RegistroAuditoria.objects.filter(operation="PESSOA_REATIVAR").count() == 1


def test_a_sessao_parada_durante_a_suspensao_nao_volta(client, rita, ana):
    """`FR-3144`: sem requisição nenhuma durante a suspensão, a sessão continua morta."""
    antiga = _cliente_de("ana")
    assert antiga.get(LISTA).status_code == 200

    _suspender(client, ana)
    _reativar(client, ana)

    assert antiga.get(LISTA)["Location"].startswith(reverse("interface:identificar"))
    assert ator_do_cliente(antiga) is None


def test_reativar_quem_nao_esta_suspenso_e_recusado(client, rita, ana):
    assert _reativar(client, ana).status_code == 409
    assert not ReativacaoDePessoa.objects.exists()


def test_a_tela_lista_as_suspensas_para_reativar(client, rita, ana):
    _suspender(client, ana)

    corpo = client.get(reverse("interface:administracao-de-acessos-pessoas")).content.decode()
    suspensas = corpo.split('id="suspensas-titulo"')[1]
    assert "Ana Souza" in suspensas
    assert reverse("interface:administracao-de-acessos-reativar", args=[ana.username]) in suspensas
    busca = client.post(
        reverse("interface:administracao-de-acessos-pessoas"), {"acao": "buscar", "termo": "souza"}
    ).content.decode()
    assert "Reativar Ana Souza" in busca


# --- Registros append-only (FR-3149) ------------------------------------------------------------


@pytest.mark.skipif(connection.vendor != "postgresql", reason="gatilho só existe no PostgreSQL")
def test_suspensao_e_reativacao_nao_se_alteram_nem_se_excluem(client, rita, ana):
    _suspender(client, ana)
    _reativar(client, ana)

    for tabela in ("seguranca_suspensaodepessoa", "seguranca_reativacaodepessoa"):
        for instrucao in (f"UPDATE {tabela} SET motivo = 'outro'", f"DELETE FROM {tabela}"):
            with pytest.raises(Exception, match="imutáveis"), transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(instrucao)


def test_uma_reativacao_por_suspensao(client, rita, ana):
    _suspender(client, ana)
    _reativar(client, ana)
    aberta = SuspensaoDePessoa.objects.get()

    with pytest.raises(IntegrityError), transaction.atomic():
        ReativacaoDePessoa.objects.create(
            suspensao=aberta, reativada_em=AGORA, reativada_por="x", motivo="x"
        )


def test_a_tela_nao_suspende_quem_virou_administracao_institucional_no_meio(
    client, rita, ana, monkeypatch
):
    """A corrida da revisão do #346: a conferência roda antes da trava, e a concessão chega entre
    as duas. Sem a segunda conferência, sob a trava, a tela suspendia uma administradora
    institucional (`FR-3136`)."""
    original = suspensao._e_administracao_institucional
    chamadas = []

    def concessao_no_meio(pessoa):
        resposta = original(pessoa)
        if not chamadas:
            # A implantação concede entre a primeira conferência e a trava da pessoa.
            vincular(
                pessoa,
                catalogo.ESCOPO_INSTITUCIONAL,
                catalogo.ADMINISTRADOR_INSTITUCIONAL,
                por="implantacao",
            )
        chamadas.append(resposta)
        return original(pessoa) if len(chamadas) > 1 else resposta

    monkeypatch.setattr(suspensao, "_e_administracao_institucional", concessao_no_meio)

    assert _suspender(client, ana).status_code == 403
    assert not SuspensaoDePessoa.objects.exists()
    assert get_user_model().objects.get(pk=ana.pk).is_active
