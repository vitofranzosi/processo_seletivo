"""A porta do aviso, por papel × origem × escopo (066, `D-004`, `FR-1274`, `FR-1276`).

**A origem decide a porta.** O aviso de resultado é de quem tem `aviso:enviar` ou preside a
comissão; o de chamada, só de quem tem base de gestão da comissão, como a comunicação da convocação.
E o escopo vem antes de tudo: o Processo de outra unidade responde como inexistente.
"""

import pytest

from processo_seletivo.avisos.application.comando import (
    base_do_aviso,
    comando_de_aviso,
    pode_consultar,
)
from processo_seletivo.avisos.domain import nomes
from processo_seletivo.comissoes.models import Funcao
from processo_seletivo.processos.models import ProcessoSeletivo
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.comissao import constituir

pytestmark = [pytest.mark.django_db, pytest.mark.authorization]

PUBLICADOR = ator_institucional("publica", nomes.PERMISSAO, "resultado:publicar")
GESTOR = ator_institucional("carlos", "comissao:gerir", nomes.PERMISSAO)
PRESIDENTE = ator_institucional("presidenta")
MEMBRO = ator_institucional("membra")
AUDITOR = ator_institucional("auditora", "auditoria:consultar")
OUTRA_UNIDADE = ator_institucional("de-fora", nomes.PERMISSAO, "comissao:gerir", escopo="campus")


@pytest.fixture
def processo(processo_a):
    constituir(
        GESTOR,
        processo_a,
        [("presidenta", Funcao.PRESIDENTE), ("membra", Funcao.MEMBRO)],
        prefixo="aviso-autorizacao",
    )
    return processo_a


@pytest.mark.parametrize(
    ("ator", "resultado", "chamada"),
    [
        (PUBLICADOR, True, False),
        (GESTOR, True, True),
        (PRESIDENTE, True, True),
        (MEMBRO, False, False),
        (AUDITOR, False, False),
        (OUTRA_UNIDADE, False, False),
    ],
    ids=["publicador", "gestor", "presidencia", "membro", "auditor", "outra-unidade"],
)
def test_a_porta_por_origem(processo, ator, resultado, chamada):
    assert (base_do_aviso(ator, processo, origem=nomes.RESULTADO) is not None) is resultado
    assert (base_do_aviso(ator, processo, origem=nomes.CHAMADA) is not None) is chamada


def test_quem_audita_le_o_historico_e_nao_envia(processo):
    assert pode_consultar(AUDITOR, processo)
    assert not pode_consultar(MEMBRO, processo)
    assert not pode_consultar(OUTRA_UNIDADE, processo)


def _abrir(ator, processo, origem=nomes.RESULTADO, chave="k"):
    with comando_de_aviso(
        actor=ator,
        processo_id=processo.id,
        origem=origem,
        operation=nomes.ATO_CONFIRMAR,
        payload={"x": 1},
        idempotency_key=chave,
    ) as ctx:
        return ctx


def test_outra_unidade_e_inexistente(processo):
    with pytest.raises(DomainError) as erro:
        _abrir(OUTRA_UNIDADE, processo)

    assert erro.value.status == 404


def test_publicador_na_chamada_e_inexistente(processo):
    with pytest.raises(DomainError) as erro:
        _abrir(PUBLICADOR, processo, origem=nomes.CHAMADA)

    assert erro.value.status == 404


def test_presidencia_inativa_perde_a_porta(processo):
    from django.utils import timezone

    from processo_seletivo.comissoes.models import MembroComissao

    MembroComissao.objects.filter(processo=processo, identity_subject="presidenta").update(
        ativo=False, inativado_em=timezone.now(), inativado_por="carlos"
    )

    assert base_do_aviso(PRESIDENTE, processo, origem=nomes.RESULTADO) is None


def test_processo_em_estado_final_recusa(processo):
    ProcessoSeletivo.objects.filter(pk=processo.pk).update(status=ProcessoSeletivo.Status.CANCELADO)

    with pytest.raises(DomainError) as erro:
        _abrir(PUBLICADOR, processo)

    assert erro.value.code == nomes.AVISO_PROCESSO_EM_ESTADO_FINAL


def test_chave_desligada_recusa_antes_de_tudo(processo, settings):
    settings.AVISOS_AOS_CANDIDATOS = False

    with pytest.raises(DomainError) as erro:
        _abrir(PUBLICADOR, processo)

    assert erro.value.code == nomes.AVISO_ENVIO_DESABILITADO


def test_o_comando_cede_a_base_que_autorizou(processo):
    assert _abrir(PUBLICADOR, processo).base.permissao == nomes.PERMISSAO
    assert _abrir(PRESIDENTE, processo, chave="k2").base.permissao == "comissao:presidir"
