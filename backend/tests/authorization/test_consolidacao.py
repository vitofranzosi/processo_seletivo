"""T036 — quem consolida, e o que acontece com quem não pode.

A base é a mesma da reabertura, e não há capacidade nova. A reavaliação **dentro** do ato protegido
é o que o invólucro da 011 já faz: bloqueia o Processo, e só então pergunta de novo.
"""

import pytest

from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.resultado import montar_etapa_de_leitura_unica

pytestmark = [pytest.mark.authorization, pytest.mark.django_db]


@pytest.fixture
def pronto(gestor, api_client, manager_headers):
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1370, codigo="1370"
    )
    inscricao = inscrever(cenario["edital"], 1, primeiro=1)[0]
    distribuir_para(cenario, gestor, ["joao"], [inscricao], chave="lote-1370")
    concluir_como(cenario, "joao", inscricao, pontuacao="75")
    cenario["inscricao"] = inscricao
    return cenario


def tentar(cenario, ator, *, chave):
    return consolidar(
        actor=ator,
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["primeira"],
        inscricao_ids=[cenario["inscricao"].id],
        idempotency_key=chave,
        correlation_id="teste",
    )


def test_quem_preside_consolida(pronto):
    assert tentar(pronto, ator_institucional("maria"), chave="p1")["feitas"] == 1


def test_o_avaliador_alocado_nao_consolida(pronto):
    """Avaliar não é decidir a consequência: a Mesa não concede a porta da presidência."""
    with pytest.raises(DomainError) as recusa:
        tentar(pronto, ator_institucional("joao"), chave="p2")
    assert recusa.value.status == 404
    assert ResultadoEtapa.objects.count() == 0


def test_a_auditoria_le_e_nao_consolida(pronto):
    """Reconstruir a decisão não concede o poder de tomá-la."""
    with pytest.raises(DomainError) as recusa:
        tentar(pronto, ator_institucional("iris", "auditoria:consultar"), chave="p3")
    assert recusa.value.status == 404


def test_ator_de_outro_escopo_institucional_recebe_a_resposta_uniforme(pronto):
    alheio = ator_institucional("maria", escopo="outra-casa")
    with pytest.raises(DomainError) as recusa:
        tentar(pronto, alheio, chave="p4")
    assert recusa.value.status == 404
