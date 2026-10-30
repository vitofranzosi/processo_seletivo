"""Retirar e substituir a administração institucional, pela implantação (107, US8, decisão P3).

Fecha a lacuna da `106`: o comando só concedia, e a aplicação recusa o papel nos dois sentidos. A
substituição é uma operação só; a retirada da última pessoa pede marca explícita (`D-018`).
"""

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.seguranca import acessos as catalogo
from processo_seletivo.seguranca.application import acessos
from processo_seletivo.seguranca.models import RevogacaoDeVinculo, Vinculo
from tests.fixtures import provedor_simulado
from tests.seguranca.apoio import ator_do_cliente, entrar, pessoa, vincular

pytestmark = pytest.mark.django_db


def _administradora(identificador):
    alguem = pessoa(identificador, nome=identificador.capitalize())
    vincular(
        alguem,
        catalogo.ESCOPO_INSTITUCIONAL,
        catalogo.ADMINISTRADOR_INSTITUCIONAL,
        por="implantacao",
    )
    return alguem


def _da(identificador):
    return ["--provedor", provedor_simulado.NOME, "--identificador", identificador]


def _institucionais():
    return set(
        acessos.vigentes()
        .filter(papel=catalogo.ADMINISTRADOR_INSTITUCIONAL)
        .values_list("pessoa__username", flat=True)
    )


def test_a_retirada_tira_o_papel_na_requisicao_seguinte(client, provedor):
    rita, _rosa = _administradora("rita"), _administradora("rosa")
    entrar(client, "rita")
    assert ator_do_cliente(client).can(catalogo.ADMINISTRAR)

    call_command("retirar_administracao_institucional", *_da("rita"), "--motivo", "Portaria 50")

    assert ator_do_cliente(client) is None
    assert rita.username not in _institucionais()
    evento = RegistroAuditoria.objects.get(operation="ACESSO_REVOGAR")
    assert (evento.actor_subject, evento.reason) == ("implantacao", "Portaria 50")


def test_a_retirada_da_ultima_pede_marca_explicita(provedor):
    rita = _administradora("rita")

    with pytest.raises(CommandError, match=acessos.ULTIMA_ADMINISTRACAO):
        call_command("retirar_administracao_institucional", *_da("rita"), "--motivo", "P 51")
    assert rita.username in _institucionais()

    call_command(
        "retirar_administracao_institucional",
        *_da("rita"),
        "--motivo",
        "P 51",
        "--sem-administracao",
    )
    assert _institucionais() == set()


def test_retirar_de_quem_nao_tem_e_recusado(provedor):
    pessoa("bea")

    with pytest.raises(CommandError, match=acessos.SEM_ADMINISTRACAO):
        call_command("retirar_administracao_institucional", *_da("bea"), "--motivo", "P 52")


def test_a_substituicao_e_uma_operacao_so(provedor):
    rita = _administradora("rita")

    call_command(
        "substituir_administracao_institucional",
        "--de-provedor",
        provedor_simulado.NOME,
        "--de-identificador",
        "rita",
        "--para-provedor",
        provedor_simulado.NOME,
        "--para-identificador",
        "nova",
        "--para-nome",
        "Nova Reitoria",
        "--motivo",
        "Portaria 60",
    )

    nova = Vinculo.objects.get(papel=catalogo.ADMINISTRADOR_INSTITUCIONAL, revogacao__isnull=True)
    assert nova.pessoa.first_name == "Nova Reitoria"
    assert rita.username not in _institucionais()
    eventos = RegistroAuditoria.objects.filter(operation__in=["ACESSO_REVOGAR", "ACESSO_CONCEDER"])
    assert sorted(eventos.values_list("operation", flat=True)) == [
        "ACESSO_CONCEDER",
        "ACESSO_REVOGAR",
    ]
    assert len(set(eventos.values_list("correlation_id", flat=True))) == 1


def test_substituir_por_quem_ja_administra_nao_muda_nada(provedor):
    _administradora("rita")
    _administradora("rosa")

    with pytest.raises(CommandError, match=acessos.VINCULO_JA_VIGENTE):
        call_command(
            "substituir_administracao_institucional",
            "--de-provedor",
            provedor_simulado.NOME,
            "--de-identificador",
            "rita",
            "--para-provedor",
            provedor_simulado.NOME,
            "--para-identificador",
            "rosa",
            "--motivo",
            "P 61",
        )
    assert not RevogacaoDeVinculo.objects.exists()


def test_se_a_concessao_falha_a_revogacao_nao_fica(provedor, monkeypatch):
    """`SC-1019`: zero estados com só a revogação, mesmo com a falha no meio da operação."""
    rita = _administradora("rita")
    nova = pessoa("nova")
    original = acessos._registrar

    def falhar_na_concessao(ator, permissao, operacao, *args, **kwargs):
        if operacao == "ACESSO_CONCEDER":
            raise RuntimeError("falha forçada entre a revogação e a concessão")
        return original(ator, permissao, operacao, *args, **kwargs)

    monkeypatch.setattr(acessos, "_registrar", falhar_na_concessao)

    with pytest.raises(RuntimeError):
        acessos.substituir_administracao_institucional(
            de=rita, para=nova, motivo="P 62", now=rita.date_joined
        )
    assert not RevogacaoDeVinculo.objects.exists()
    assert _institucionais() == {rita.username}
