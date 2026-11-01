"""Conceder e revogar, pelas regras do domínio (106, US3; testes 6 e 7 do pedido).

Exercidos pela camada de aplicação: nesta etapa não há tela de acessos, e as regras são as mesmas
que uma tela chamaria.
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, connection, transaction

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.seguranca import acessos as catalogo
from processo_seletivo.seguranca.application import acessos
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.seguranca.models import RevogacaoDeVinculo, Vinculo
from processo_seletivo.shared.api.problems import DomainError
from tests.seguranca.apoio import AGORA, pessoa, vincular

pytestmark = pytest.mark.django_db

postgresql = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="gatilho só existe no PostgreSQL"
)


def _ator(alguem, escopo, *papeis):
    return Actor(alguem.username, escopo, acessos.permissoes_dos_papeis(papeis))


@pytest.fixture
def admin_cefor():
    alguem = pessoa("admin-cefor")
    vincular(alguem, "cefor", catalogo.ADMINISTRADOR_DE_ACESSOS)
    return _ator(alguem, "cefor", catalogo.ADMINISTRADOR_DE_ACESSOS)


@pytest.fixture
def admin_institucional():
    alguem = pessoa("admin-ifes")
    vincular(alguem, catalogo.ESCOPO_INSTITUCIONAL, catalogo.ADMINISTRADOR_INSTITUCIONAL)
    return _ator(alguem, catalogo.ESCOPO_INSTITUCIONAL, catalogo.ADMINISTRADOR_INSTITUCIONAL)


def _recusa(funcao, **argumentos):
    with pytest.raises(DomainError) as erro:
        funcao(**argumentos)
    return erro.value


def test_concede_papel_operacional_com_trilha(admin_cefor):
    paulo = pessoa("paulo")

    vinculo = acessos.conceder(
        admin_cefor,
        pessoa=paulo,
        escopo="cefor",
        papel="elaborador",
        motivo="Portaria 1",
        now=AGORA,
    )

    assert (vinculo.concedido_por, vinculo.motivo) == (admin_cefor.subject, "Portaria 1")
    evento = RegistroAuditoria.objects.get(operation="ACESSO_CONCEDER")
    assert (evento.actor_subject, evento.permission, evento.institution_scope, evento.reason) == (
        admin_cefor.subject,
        catalogo.GERIR,
        "cefor",
        "Portaria 1",
    )
    assert evento.detalhe == {"pessoa": paulo.username, "escopo": "cefor", "papel": "elaborador"}


# --- Teste 6: sem autoconcessão ------------------------------------------------------------------


def test_ninguem_concede_a_si_mesmo(admin_cefor):
    eu = get_user_model().objects.get(username=admin_cefor.subject)

    recusa = _recusa(
        acessos.conceder,
        ator=admin_cefor,
        pessoa=eu,
        escopo="cefor",
        papel="gestor",
        motivo="quero",
        now=AGORA,
    )

    assert (recusa.code, recusa.status) == (acessos.AUTOCONCESSAO, 403)
    assert Vinculo.objects.filter(pessoa=eu).count() == 1
    assert not RegistroAuditoria.objects.exists()


def test_ninguem_revoga_o_proprio_vinculo(admin_cefor):
    eu = get_user_model().objects.get(username=admin_cefor.subject)
    proprio = vincular(eu, "cefor", "gestor")

    recusa = _recusa(acessos.revogar, ator=admin_cefor, vinculo=proprio, motivo="x", now=AGORA)

    assert recusa.code == acessos.AUTOCONCESSAO
    assert not RevogacaoDeVinculo.objects.exists()


def test_o_institucional_nao_concede_a_si_mesmo(admin_institucional):
    eu = get_user_model().objects.get(username=admin_institucional.subject)

    recusa = _recusa(
        acessos.conceder,
        ator=admin_institucional,
        pessoa=eu,
        escopo="cefor",
        papel=catalogo.ADMINISTRADOR_DE_ACESSOS,
        motivo="x",
        now=AGORA,
    )

    assert recusa.code == acessos.AUTOCONCESSAO


# --- Teste 7: administrador de unidade não concede em outra --------------------------------------


def test_administrador_da_unidade_nao_concede_em_outra(admin_cefor, campus_a):
    recusa = _recusa(
        acessos.conceder,
        ator=admin_cefor,
        pessoa=pessoa("q"),
        escopo="campus-a",
        papel="elaborador",
        motivo="x",
        now=AGORA,
    )

    assert recusa.status == 404
    assert not Vinculo.objects.filter(escopo="campus-a").exists()


def test_administrador_da_unidade_nao_revoga_em_outra(admin_cefor, campus_a):
    alheio = vincular(pessoa("q2"), "campus-a", "elaborador")

    recusa = _recusa(acessos.revogar, ator=admin_cefor, vinculo=alheio, motivo="x", now=AGORA)

    assert recusa.status == 404
    assert not RevogacaoDeVinculo.objects.exists()


def test_administrador_da_unidade_nao_concede_papel_de_acesso(admin_cefor):
    for papel in (catalogo.ADMINISTRADOR_DE_ACESSOS, catalogo.ADMINISTRADOR_INSTITUCIONAL):
        recusa = _recusa(
            acessos.conceder,
            ator=admin_cefor,
            pessoa=pessoa("q3"),
            escopo="cefor",
            papel=papel,
            motivo="x",
            now=AGORA,
        )
        assert recusa.status == 403


def test_o_institucional_concede_o_administrador_de_qualquer_unidade(admin_institucional, campus_a):
    vinculo = acessos.conceder(
        admin_institucional,
        pessoa=pessoa("r"),
        escopo="campus-a",
        papel=catalogo.ADMINISTRADOR_DE_ACESSOS,
        motivo="Portaria 7",
        now=AGORA,
    )

    assert vinculo.escopo == "campus-a"
    assert RegistroAuditoria.objects.get().institution_scope == catalogo.ESCOPO_INSTITUCIONAL


def test_o_institucional_nao_tem_poder_operacional(admin_institucional):
    assert not any(
        p.startswith(("edital:", "processo:", "retificacao:"))
        for p in admin_institucional.permissions
    )
    recusa = _recusa(
        acessos.conceder,
        ator=admin_institucional,
        pessoa=pessoa("s"),
        escopo="cefor",
        papel="gestor",
        motivo="x",
        now=AGORA,
    )
    assert recusa.status == 403


def test_administrador_institucional_nao_se_concede_pela_aplicacao(admin_institucional):
    recusa = _recusa(
        acessos.conceder,
        ator=admin_institucional,
        pessoa=pessoa("t"),
        escopo=catalogo.ESCOPO_INSTITUCIONAL,
        papel=catalogo.ADMINISTRADOR_INSTITUCIONAL,
        motivo="x",
        now=AGORA,
    )

    assert recusa.code == acessos.PAPEL_SO_POR_IMPLANTACAO


@pytest.mark.parametrize(
    ("argumentos", "codigo"),
    [
        ({"papel": "elaborador", "motivo": "  "}, acessos.MOTIVO_OBRIGATORIO),
        ({"papel": "diretor-supremo", "motivo": "x"}, acessos.PAPEL_INEXISTENTE),
    ],
)
def test_concessao_recusa_o_malformado(admin_cefor, argumentos, codigo):
    recusa = _recusa(
        acessos.conceder,
        ator=admin_cefor,
        pessoa=pessoa("u"),
        escopo="cefor",
        now=AGORA,
        **argumentos,
    )

    assert recusa.code == codigo
    assert not Vinculo.objects.filter(pessoa__username=pessoa("u").username).exists()


def test_concessao_em_unidade_nao_registrada_e_recusada(admin_institucional):
    recusa = _recusa(
        acessos.conceder,
        ator=admin_institucional,
        pessoa=pessoa("v"),
        escopo="campus-z",
        papel=catalogo.ADMINISTRADOR_DE_ACESSOS,
        motivo="x",
        now=AGORA,
    )

    assert recusa.code == "unidade_nao_registrada"


def test_o_mesmo_papel_vigente_nao_se_concede_duas_vezes(admin_cefor):
    alguem = pessoa("w")
    acessos.conceder(
        admin_cefor, pessoa=alguem, escopo="cefor", papel="auditor", motivo="x", now=AGORA
    )

    recusa = _recusa(
        acessos.conceder,
        ator=admin_cefor,
        pessoa=alguem,
        escopo="cefor",
        papel="auditor",
        motivo="x",
        now=AGORA,
    )

    assert (recusa.code, recusa.status) == (acessos.VINCULO_JA_VIGENTE, 409)


def test_revogacao_com_trilha_e_uma_vez_so(admin_cefor):
    vinculo = vincular(pessoa("x"), "cefor", "julgador")

    acessos.revogar(admin_cefor, vinculo=vinculo, motivo="Fim do mandato", now=AGORA)
    recusa = _recusa(
        acessos.revogar, ator=admin_cefor, vinculo=vinculo, motivo="de novo", now=AGORA
    )

    assert recusa.code == acessos.VINCULO_JA_REVOGADO
    evento = RegistroAuditoria.objects.get(operation="ACESSO_REVOGAR")
    assert (evento.new_state, evento.reason) == ("revogado", "Fim do mandato")
    # Revogado, o mesmo papel pode ser concedido de novo — vínculo novo, e o antigo fica.
    acessos.conceder(
        admin_cefor,
        pessoa=vinculo.pessoa,
        escopo="cefor",
        papel="julgador",
        motivo="Nova portaria",
        now=AGORA,
    )
    assert Vinculo.objects.filter(pessoa=vinculo.pessoa).count() == 2


def test_a_segunda_revogacao_o_banco_recusa():
    vinculo = vincular(pessoa("y"), "cefor", "julgador")
    RevogacaoDeVinculo.objects.create(
        vinculo=vinculo, revogado_em=AGORA, revogado_por="a", motivo="x"
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        RevogacaoDeVinculo.objects.create(
            vinculo=vinculo, revogado_em=AGORA, revogado_por="b", motivo="y"
        )


def test_a_consulta_dos_vinculos_exige_a_permissao(admin_cefor):
    vincular(pessoa("z"), "cefor", "gestor")

    assert {v.papel for v in acessos.vinculos_vigentes_da_unidade(admin_cefor)} == {
        "gestor",
        catalogo.ADMINISTRADOR_DE_ACESSOS,
    }
    sem = Actor("alguem", "cefor", frozenset({"edital:elaborar"}))
    assert _recusa(acessos.vinculos_vigentes_da_unidade, ator=sem).status == 403


def test_o_catalogo_de_acesso_nao_entra_no_seletor():
    from processo_seletivo.interface.identidade import DESCRICOES, PAPEIS

    assert len(PAPEIS) == 9
    assert set(PAPEIS) == set(DESCRICOES)
    assert not set(PAPEIS) & (set(catalogo.PAPEIS_DE_ACESSO) | set(catalogo.PAPEIS_INSTITUCIONAIS))


def test_a_regra_da_unidade_recusa_o_codigo_reservado():
    """Na semente, no cadastro e na edição: a regra é uma só desde a 110 (`D-005`)."""
    from processo_seletivo.unidades.domain.registro import validar_codigo

    with pytest.raises(DomainError, match="reservado"):
        validar_codigo(catalogo.ESCOPO_INSTITUCIONAL)


# --- As travas do banco --------------------------------------------------------------------------


@postgresql
@pytest.mark.parametrize("tabela", ["seguranca_vinculo", "seguranca_identidadeexterna"])
def test_vinculo_e_identidade_externa_nao_mudam_no_banco(tabela):
    vincular(pessoa("trava"), "cefor", "gestor")

    for comando in (f"UPDATE {tabela} SET id = id", f"DELETE FROM {tabela}"):
        with pytest.raises(Exception, match="imutáveis"), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(comando)


@postgresql
def test_o_identificador_da_pessoa_nao_muda_e_ela_nao_se_exclui():
    alguem = pessoa("trava-2")
    get_user_model().objects.filter(pk=alguem.pk).update(first_name="Outro nome")

    with pytest.raises(Exception, match="imutável"), transaction.atomic():
        get_user_model().objects.filter(pk=alguem.pk).update(username="pessoa-outra")
    with pytest.raises(Exception, match="não se exclui"), transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM auth_user WHERE id = %s", [alguem.pk])


def test_o_save_recusa_reescrever():
    vinculo = vincular(pessoa("trava-3"), "cefor", "gestor")

    with pytest.raises(TypeError):
        vinculo.save()
    with pytest.raises(TypeError):
        vinculo.delete()


# --- O primeiro administrador, pelo comando ------------------------------------------------------


def test_o_comando_concede_o_primeiro_administrador_e_recusa_o_segundo_sem_marca():
    call_command(
        "conceder_administracao_institucional",
        "--provedor",
        "simulado",
        "--identificador",
        "reitoria-1",
        "--motivo",
        "Portaria 100/2026",
    )
    primeira = Vinculo.objects.get(papel=catalogo.ADMINISTRADOR_INSTITUCIONAL)
    assert (primeira.escopo, primeira.concedido_por) == (
        catalogo.ESCOPO_INSTITUCIONAL,
        "implantacao",
    )
    evento = RegistroAuditoria.objects.get()
    assert (evento.actor_subject, evento.institution_scope) == (
        "implantacao",
        catalogo.ESCOPO_INSTITUCIONAL,
    )

    with pytest.raises(CommandError, match="administracao_ja_concedida"):
        call_command(
            "conceder_administracao_institucional",
            "--provedor",
            "simulado",
            "--identificador",
            "reitoria-2",
            "--motivo",
            "Portaria 101/2026",
        )
    assert not get_user_model().objects.filter(identidades_externas__identificador="reitoria-2")

    call_command(
        "conceder_administracao_institucional",
        "--provedor",
        "simulado",
        "--identificador",
        "reitoria-2",
        "--motivo",
        "Portaria 101/2026",
        "--adicional",
    )
    assert Vinculo.objects.filter(papel=catalogo.ADMINISTRADOR_INSTITUCIONAL).count() == 2


def test_o_comando_exige_motivo():
    with pytest.raises(CommandError, match="motivo_obrigatorio"):
        call_command(
            "conceder_administracao_institucional",
            "--provedor",
            "simulado",
            "--identificador",
            "reitoria-3",
            "--motivo",
            " ",
        )
    assert not Vinculo.objects.exists()
