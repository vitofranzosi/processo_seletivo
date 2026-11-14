"""Habilitar e desabilitar o assistente pela interface: os atos e a regra de quem atende (170).

Prende, sem tela:
- o ato grava autor, motivo e ordem, e vai à trilha na mesma transação (FR-7527 a FR-7529);
- o ato que não muda nada, sem motivo ou sem configuração completa é recusado sem gravar
  (FR-7504, FR-7528, FR-7530);
- fora de produção a habilitação basta, sem chave de demonstração (FR-7508);
- em produção a página pública não abre, nem com ato gravado (FR-7518, FR-7519);
- habilitar de novo muda a marca da conversa (FR-7525, R-5);
- o registro é append-only no banco (FR-7527).
"""

import pytest
from django.db import DatabaseError, connection, transaction
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.duvidas.application import habilitacao
from processo_seletivo.duvidas.domain import habilitacao as nomes
from processo_seletivo.duvidas.models import HabilitacaoDoAssistente
from processo_seletivo.processos.models import Edital
from processo_seletivo.seguranca.acessos import ESCOPO_INSTITUCIONAL
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.corpus import publicar_do_corpus

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="o gatilho append-only existe só no PostgreSQL"
)

ADMINISTRADORA = Actor("pessoa-administradora", ESCOPO_INSTITUCIONAL, frozenset({nomes.HABILITAR}))


@pytest.fixture(autouse=True)
def _sem_atalhos(settings):
    """O percurso da interface não depende dos atalhos (FR-7508): os casos daqui os desligam."""
    settings.ASSISTENTE_PILOTO = False
    settings.ASSISTENTE_NA_PAGINA_DO_EDITAL = False


@pytest.fixture
def edital_91(api_client):
    edital, _ = publicar_do_corpus(api_client, "91", chave="habilitacao91")
    return edital


@pytest.fixture
def edital_92(api_client):
    edital, _ = publicar_do_corpus(api_client, "92", chave="habilitacao92")
    return edital


def _recusa(funcao, **kwargs):
    with pytest.raises(DomainError) as recusa:
        funcao(ADMINISTRADORA, **kwargs)
    return recusa.value


# --- O piloto -----------------------------------------------------------------------------------


def test_habilitar_o_piloto_basta_fora_de_producao_sem_o_atalho(configuracao_completa):
    """FR-7508, FR-7514, FR-7515: o ato basta, e nenhum atalho está ligado."""
    assert habilitacao.piloto_atende() is False

    ato = habilitacao.habilitar(ADMINISTRADORA, frente=nomes.PILOTO, motivo="Sessão de teste")

    assert (ato.frente, ato.edital_id, ato.ordem, ato.habilitada) == (nomes.PILOTO, None, 1, True)
    assert (ato.autor, ato.motivo) == ("pessoa-administradora", "Sessão de teste")
    assert habilitacao.piloto_atende() is True


def test_desabilitar_e_ato_novo_e_o_estado_e_o_ultimo(configuracao_completa):
    """FR-7526, FR-7527, FR-7532: desabilitar não apaga o ato anterior."""
    habilitacao.habilitar(ADMINISTRADORA, frente=nomes.PILOTO, motivo="Abrir")
    habilitacao.desabilitar(ADMINISTRADORA, frente=nomes.PILOTO, motivo="Fechar")

    atos = list(
        HabilitacaoDoAssistente.objects.order_by("ordem").values_list("ordem", "habilitada")
    )
    assert atos == [(1, True), (2, False)]
    assert habilitacao.piloto_atende() is False


def test_o_ato_vai_a_trilha_com_o_motivo_e_a_situacao(configuracao_completa):
    """FR-7529: o evento na mesma transação; o piloto no escopo institucional (R-8)."""
    ato = habilitacao.habilitar(ADMINISTRADORA, frente=nomes.PILOTO, motivo="Sessão de teste")

    evento = RegistroAuditoria.objects.get(aggregate_id=ato.id)
    assert (evento.operation, evento.permission) == ("HABILITAR_ASSISTENTE", nomes.HABILITAR)
    assert (evento.institution_scope, evento.reason) == (ESCOPO_INSTITUCIONAL, "Sessão de teste")
    assert (evento.previous_state, evento.new_state) == ("", "HABILITADA")


def test_sem_motivo_recusa_e_nada_e_gravado(configuracao_completa):
    """FR-7528."""
    recusa = _recusa(habilitacao.habilitar, frente=nomes.PILOTO, motivo="   ")

    assert (recusa.code, recusa.status) == (nomes.MOTIVO_OBRIGATORIO, 422)
    assert not HabilitacaoDoAssistente.objects.exists()


def test_o_ato_que_nao_muda_nada_e_recusado(configuracao_completa):
    """FR-7530: habilitar o habilitado, desabilitar o desabilitado — e o nunca habilitado."""
    assert _recusa(habilitacao.desabilitar, frente=nomes.PILOTO, motivo="x").code == (
        nomes.JA_DESABILITADO
    )
    habilitacao.habilitar(ADMINISTRADORA, frente=nomes.PILOTO, motivo="Abrir")

    assert _recusa(habilitacao.habilitar, frente=nomes.PILOTO, motivo="x").code == (
        nomes.JA_HABILITADO
    )
    assert HabilitacaoDoAssistente.objects.count() == 1


def test_sem_configuracao_completa_nao_habilita_e_diz_o_que_falta(settings):
    """FR-7501, FR-7504, FR-7514: o serviço da suíte é vazio, e a recusa o nomeia."""
    settings.ASSISTENTE_SERVICO = ""

    recusa = _recusa(habilitacao.habilitar, frente=nomes.PILOTO, motivo="x")

    assert (recusa.code, recusa.status) == (nomes.CONFIGURACAO_INCOMPLETA, 409)
    assert nomes.FALTAS["servico"] in recusa.detail
    assert not HabilitacaoDoAssistente.objects.exists()


def test_desabilitar_nao_depende_da_configuracao(configuracao_completa, settings):
    """FR-7504: retirar a configuração não impede fechar o que está aberto."""
    habilitacao.habilitar(ADMINISTRADORA, frente=nomes.PILOTO, motivo="Abrir")
    settings.ASSISTENTE_SERVICO = ""

    habilitacao.desabilitar(ADMINISTRADORA, frente=nomes.PILOTO, motivo="Fechar")

    assert habilitacao.piloto_atende() is False


def test_o_atalho_atende_sem_ato_fora_de_producao_e_nunca_em_producao(settings):
    """FR-7506: o atalho dispensa o registro, e só fora de produção."""
    settings.ASSISTENTE_PILOTO = True
    assert habilitacao.piloto_atende() is True
    assert habilitacao.marca(nomes.PILOTO) == nomes.MARCA_DA_DEMONSTRACAO

    settings.AMBIENTE_DE_PRODUCAO = True
    assert habilitacao.piloto_atende() is False


def test_o_piloto_se_habilita_em_producao(configuracao_completa, settings):
    """Q-1, FR-7514: em produção, o piloto continua habilitável; só a página pública fecha."""
    settings.AMBIENTE_DE_PRODUCAO = True

    habilitacao.habilitar(ADMINISTRADORA, frente=nomes.PILOTO, motivo="Sessão acompanhada")

    assert habilitacao.piloto_atende() is True


# --- A página pública ----------------------------------------------------------------------------


def test_a_pagina_publica_se_habilita_por_edital(configuracao_completa, edital_91, edital_92):
    """FR-7517, FR-7520: o 91 abre, o 92 continua fechado."""
    habilitacao.habilitar(
        ADMINISTRADORA, frente=nomes.PAGINA_PUBLICA, edital_id=edital_91.id, motivo="Teste no 91"
    )

    assert habilitacao.pagina_publica_atende(edital_91.id) is True
    assert habilitacao.pagina_publica_atende(edital_92.id) is False


def test_o_ato_do_edital_vai_a_trilha_da_unidade(configuracao_completa, edital_91):
    """FR-7529, R-8: o escopo do evento é o da unidade do Edital, com o rótulo do Edital."""
    ato = habilitacao.habilitar(
        ADMINISTRADORA, frente=nomes.PAGINA_PUBLICA, edital_id=edital_91.id, motivo="Teste"
    )

    evento = RegistroAuditoria.objects.get(aggregate_id=ato.id)
    assert evento.institution_scope == edital_91.institution_scope
    assert evento.detalhe["rotulo"] == f"Edital {edital_91.number}/{edital_91.year}"


def test_edital_sem_pagina_publica_nao_se_habilita(configuracao_completa, edital_91):
    """FR-7517: sem seleção pública agora, não há onde abrir o assistente."""
    rascunho = Edital.objects.create(
        processo=edital_91.processo,
        institution_scope=edital_91.institution_scope,
        number="999",
        year=2026,
        title="Rascunho",
        created_at=timezone.now(),
    )

    recusa = _recusa(
        habilitacao.habilitar, frente=nomes.PAGINA_PUBLICA, edital_id=rascunho.id, motivo="x"
    )

    assert recusa.code == nomes.SEM_PAGINA_PUBLICA
    assert not HabilitacaoDoAssistente.objects.exists()


def test_em_producao_a_pagina_publica_e_recusada_nomeando_os_doze(
    configuracao_completa, edital_91, settings
):
    """FR-7518, FR-7533, SC-2453: a recusa lista RA-1 a RA-12, e nada é gravado."""
    settings.AMBIENTE_DE_PRODUCAO = True

    recusa = _recusa(
        habilitacao.habilitar, frente=nomes.PAGINA_PUBLICA, edital_id=edital_91.id, motivo="x"
    )

    assert (recusa.code, recusa.status) == (nomes.ABERTURA_PUBLICA_EM_PRODUCAO, 409)
    for codigo, _, _ in nomes.REQUISITOS_DA_ABERTURA:
        assert f"{codigo} —" in recusa.detail
    assert len(nomes.REQUISITOS_DA_ABERTURA) == 12
    assert not HabilitacaoDoAssistente.objects.exists()


def test_em_producao_o_ato_gravado_nao_abre_a_pagina(configuracao_completa, edital_91, settings):
    """FR-7519: o banco de testes levado à produção não abre o painel, nem com o atalho."""
    habilitacao.habilitar(
        ADMINISTRADORA, frente=nomes.PAGINA_PUBLICA, edital_id=edital_91.id, motivo="Teste"
    )
    settings.AMBIENTE_DE_PRODUCAO = True
    settings.ASSISTENTE_NA_PAGINA_DO_EDITAL = True

    assert habilitacao.pagina_publica_atende(edital_91.id) is False
    assert habilitacao.estado_do_edital(edital_91.id) is None


def test_habilitar_de_novo_muda_a_marca_da_conversa(configuracao_completa, edital_91):
    """FR-7525, R-5: ato novo, conversa nova."""
    kwargs = {"frente": nomes.PAGINA_PUBLICA, "edital_id": edital_91.id}
    habilitacao.habilitar(ADMINISTRADORA, motivo="Abrir", **kwargs)
    primeira = habilitacao.marca(**kwargs)
    habilitacao.desabilitar(ADMINISTRADORA, motivo="Fechar", **kwargs)
    habilitacao.habilitar(ADMINISTRADORA, motivo="Abrir de novo", **kwargs)

    assert habilitacao.marca(**kwargs) not in (primeira, nomes.MARCA_DA_DEMONSTRACAO)


# --- O registro ----------------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
@postgresql_only
def test_o_registro_recusa_alterar_e_excluir_no_banco(configuracao_completa):
    """FR-7527, SC-2452: o gatilho, além do privilégio ausente que `test_database_permissions`
    confere pela lista de `TABELAS_APPEND_ONLY`."""
    ato = habilitacao.habilitar(ADMINISTRADORA, frente=nomes.PILOTO, motivo="Abrir")

    for mudar in (
        lambda: HabilitacaoDoAssistente.objects.filter(pk=ato.pk).update(motivo="outro"),
        lambda: HabilitacaoDoAssistente.objects.filter(pk=ato.pk).delete(),
    ):
        with pytest.raises(DatabaseError, match="append-only"), transaction.atomic():
            mudar()
    assert HabilitacaoDoAssistente.objects.get(pk=ato.pk).motivo == "Abrir"
