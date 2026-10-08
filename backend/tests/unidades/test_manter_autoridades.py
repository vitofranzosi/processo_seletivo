"""Cadastrar, corrigir e encerrar as autoridades da unidade (060, FR-1120 a FR-1123, D-005).

Pelos comandos de aplicação, com o Gestor da própria unidade. A tela está em
`tests/interface/test_tela_de_autoridades.py`; o banco, em `test_registro.py`.
"""

from datetime import date, timedelta

import pytest
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.tempo import ZONA
from processo_seletivo.unidades.application.autoridades import cadastrar, corrigir, encerrar
from processo_seletivo.unidades.domain.vigencia import vigente
from processo_seletivo.unidades.models import AutoridadeHabilitada, Unidade
from tests.conftest import ator_institucional
from tests.fixtures.autoridades import registrar_autoridade, registrar_unidade

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

GERIR = "autoridade:gerir"


def _hoje():
    return timezone.now().astimezone(ZONA).date()


def _gestor(escopo="cefor"):
    return ator_institucional("gabriel", GERIR, escopo=escopo)


def _cadastrar(ator=None, chave="cad-0001", **campos):
    valores = {"cargo": "Diretora-Geral", "inicio_vigencia": _hoje(), **campos}
    return cadastrar(
        actor=ator or _gestor(), idempotency_key=chave, correlation_id="teste", **valores
    )


def test_cadastrar_registra_com_trilha():
    """FR-1116, FR-1123."""
    autoridade = _cadastrar(nome="Maria Exemplo", ato_de_nomeacao="Portaria nº 1/2026")

    assert autoridade.unidade.codigo == "cefor"
    assert (autoridade.cargo, autoridade.nome, autoridade.cadastrada_por) == (
        "Diretora-Geral",
        "Maria Exemplo",
        "gabriel",
    )
    evento = RegistroAuditoria.objects.get(
        operation="CADASTRAR_AUTORIDADE", aggregate_id=autoridade.pk
    )
    assert evento.permission == GERIR
    assert evento.detalhe["depois"]["ato_de_nomeacao"] == "Portaria nº 1/2026"


def test_cadastrar_de_novo_com_a_mesma_chave_devolve_a_mesma():
    assert _cadastrar().pk == _cadastrar().pk
    assert AutoridadeHabilitada.objects.filter(cadastrada_por="gabriel").count() == 1


def test_sem_cargo_e_recusado():
    with pytest.raises(DomainError) as recusa:
        _cadastrar(cargo="  ")
    assert recusa.value.code == "cargo_obrigatorio"


def test_sem_a_permissao_e_recusado():
    """FR-1122: a permissão é própria — publicar não a concede."""
    publicador = ator_institucional("carla", "edital:publicar", "resultado:publicar")
    with pytest.raises(DomainError) as recusa:
        _cadastrar(ator=publicador)
    assert recusa.value.status == 403


def test_escopo_sem_unidade_registrada_nao_cadastra():
    with pytest.raises(DomainError) as recusa:
        _cadastrar(ator=_gestor("sem-unidade"))
    assert recusa.value.code == "unidade_nao_registrada"


def test_unidade_desativada_continua_recebendo_cadastro_correcao_e_encerramento():
    """FR-1110: o certame que segue nela precisa de quem responda pelos atos que faltam."""
    registrar_unidade("serra", ativa=False)
    gestor = _gestor("serra")

    autoridade = _cadastrar(ator=gestor)
    corrigida = corrigir(
        actor=gestor,
        autoridade_id=autoridade.pk,
        cargo="Diretor-Geral",
        inicio_vigencia=autoridade.inicio_vigencia,
        idempotency_key="cor-serra",
        correlation_id="teste",
    )
    encerrada = encerrar(
        actor=gestor,
        autoridade_id=autoridade.pk,
        fim_vigencia=_hoje(),
        idempotency_key="enc-serra",
        correlation_id="teste",
    )
    assert (corrigida.cargo, encerrada.fim_vigencia) == ("Diretor-Geral", _hoje())


def test_unidade_desativada_continua_exigindo_permissao_e_escopo():
    registrar_unidade("serra", ativa=False)
    autoridade = registrar_autoridade(Unidade.objects.get(codigo="serra"))
    with pytest.raises(DomainError) as recusa:
        encerrar(
            actor=_gestor("cefor"),
            autoridade_id=autoridade.pk,
            fim_vigencia=_hoje(),
            idempotency_key="enc-alheia",
            correlation_id="teste",
        )
    assert recusa.value.status == 404


# ---------------------------------------------------------------------------
# Corrigir — só antes do primeiro uso (FR-1121, D-004)
# ---------------------------------------------------------------------------


def test_corrigir_antes_do_uso_grava_antes_e_depois_inclusive_o_inicio():
    autoridade = _cadastrar()
    novo_inicio = _hoje() - timedelta(days=30)

    corrigida = corrigir(
        actor=_gestor(),
        autoridade_id=autoridade.pk,
        cargo="Diretora-Geral",
        nome="Maria Exemplo",
        ato_de_nomeacao="Portaria nº 2/2026",
        inicio_vigencia=novo_inicio,
        idempotency_key="cor-0001",
        correlation_id="teste",
    )

    assert (corrigida.nome, corrigida.inicio_vigencia) == ("Maria Exemplo", novo_inicio)
    evento = RegistroAuditoria.objects.get(
        operation="CORRIGIR_AUTORIDADE", aggregate_id=autoridade.pk
    )
    assert evento.detalhe["antes"]["nome"] == ""
    assert evento.detalhe["depois"]["nome"] == "Maria Exemplo"
    assert evento.detalhe["depois"]["inicio_vigencia"] == novo_inicio.isoformat()


def test_corrigir_depois_do_uso_e_recusado_com_a_orientacao():
    autoridade = registrar_autoridade(Unidade.objects.get(codigo="cefor"), usada_em=timezone.now())
    with pytest.raises(DomainError) as recusa:
        corrigir(
            actor=_gestor(),
            autoridade_id=autoridade.pk,
            cargo="Outro",
            inicio_vigencia=autoridade.inicio_vigencia,
            idempotency_key="cor-usada",
            correlation_id="teste",
        )
    assert recusa.value.code == "autoridade_ja_usada"
    assert "encerre-a e cadastre outra" in recusa.value.detail


# ---------------------------------------------------------------------------
# Encerrar — sem retroagir, com fim inclusivo (FR-1120)
# ---------------------------------------------------------------------------


def _encerrar(autoridade, fim, chave="enc-0001", ator=None):
    return encerrar(
        actor=ator or _gestor(),
        autoridade_id=autoridade.pk,
        fim_vigencia=fim,
        idempotency_key=chave,
        correlation_id="teste",
    )


def test_encerrar_com_fim_hoje_a_oferece_hoje_e_a_retira_amanha():
    autoridade = _cadastrar(inicio_vigencia=_hoje() - timedelta(days=10))

    encerrada = _encerrar(autoridade, _hoje())

    assert vigente(encerrada, _hoje())
    assert not vigente(encerrada, _hoje() + timedelta(days=1))
    assert encerrada.encerrada_por == "gabriel"
    assert RegistroAuditoria.objects.filter(
        operation="ENCERRAR_AUTORIDADE", aggregate_id=autoridade.pk
    ).exists()


def test_encerramento_retroativo_e_recusado():
    autoridade = _cadastrar(inicio_vigencia=_hoje() - timedelta(days=10))
    with pytest.raises(DomainError) as recusa:
        _encerrar(autoridade, _hoje() - timedelta(days=1))
    assert recusa.value.code == "encerramento_retroativo"
    assert "fim de hoje" in recusa.value.detail
    autoridade.refresh_from_db()
    assert autoridade.fim_vigencia is None


def test_fim_antes_do_inicio_e_recusado():
    autoridade = _cadastrar(inicio_vigencia=_hoje() + timedelta(days=10))
    with pytest.raises(DomainError) as recusa:
        _encerrar(autoridade, _hoje() + timedelta(days=5))
    assert recusa.value.code == "vigencia_invertida"


def test_um_fim_futuro_pode_ser_antecipado_mas_a_ja_encerrada_nao_se_reencerra():
    autoridade = _cadastrar(inicio_vigencia=_hoje() - timedelta(days=10))
    _encerrar(autoridade, _hoje() + timedelta(days=30), chave="enc-futuro")
    antecipada = _encerrar(autoridade, _hoje(), chave="enc-hoje")
    assert antecipada.fim_vigencia == _hoje()

    passada = registrar_autoridade(
        Unidade.objects.get(codigo="cefor"),
        inicio=date(2026, 1, 1),
        fim=_hoje() - timedelta(days=2),
    )
    with pytest.raises(DomainError) as recusa:
        _encerrar(passada, _hoje(), chave="enc-passada")
    assert recusa.value.code == "autoridade_ja_encerrada"


def test_autoridade_de_outra_unidade_e_indistinguivel_de_inexistente():
    """FR-1122."""
    da_serra = registrar_autoridade(registrar_unidade("serra"))
    for alvo, chave in ((da_serra.pk, "enc-serra"), ("00000000-0000-0000-0000-00000000dead", "x")):
        with pytest.raises(DomainError) as recusa:
            encerrar(
                actor=_gestor(),
                autoridade_id=alvo,
                fim_vigencia=_hoje(),
                idempotency_key=f"{chave}-0001",
                correlation_id="teste",
            )
        assert (recusa.value.status, recusa.value.code) == (404, "not_found")
