"""T035 — o que é erro do pedido, e portanto impede qualquer criação.

A distinção não é estética. Recusa de item é o caminho normal esbarrando numa regra: o lote segue e
a linha é nomeada. Erro do pedido é uma seleção que a tela não deveria ter oferecido — e responder
"0 consolidadas" a ele faria a tela afirmar um ato que não aconteceu (FR-019).
"""

import pytest

from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.resultado import montar_etapa_de_leitura_unica

pytestmark = [pytest.mark.contract, pytest.mark.django_db]


def consolidar_como(cenario, inscricoes, *, chave, ator=None, etapa=None):
    return consolidar(
        actor=ator or ator_institucional("maria"),
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=etapa or cenario["primeira"],
        inscricao_ids=[getattr(i, "id", i) for i in inscricoes],
        idempotency_key=chave,
        correlation_id="teste",
    )


def test_etapa_de_leitura_multipla_e_erro_do_pedido(gestor, api_client, manager_headers):
    """Impedimento da Etapa inteira: nenhuma criação, e a frase nomeia a quantidade publicada."""
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1360, codigo="1360", avaliacoes=2
    )
    inscricoes = inscrever(cenario["edital"], 1, primeiro=1)
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="lote-1360")
    concluir_como(cenario, "joao", inscricoes[0], pontuacao="75")

    with pytest.raises(DomainError) as recusa:
        consolidar_como(cenario, inscricoes, chave="x1")
    assert recusa.value.code == "regra_de_combinacao_ausente"
    assert ResultadoEtapa.objects.count() == 0


def test_inscricao_de_outro_edital_e_erro_do_pedido(gestor, api_client, manager_headers):
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1361, codigo="1361"
    )
    outro = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1362, codigo="1362"
    )
    alheia = inscrever(outro["edital"], 1, primeiro=1)[0]

    with pytest.raises(DomainError) as recusa:
        consolidar_como(cenario, [alheia], chave="x2")
    assert recusa.value.code == "inscricao_nao_consolidavel"
    assert ResultadoEtapa.objects.count() == 0


def test_etapa_fora_do_vigente_responde_como_inexistente(gestor, api_client, manager_headers):
    """Identificador não concede acesso, e não existe 403 aqui: a resposta é uniforme."""
    from uuid import uuid4

    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1363, codigo="1363"
    )
    inscricoes = inscrever(cenario["edital"], 1, primeiro=1)
    with pytest.raises(DomainError) as recusa:
        consolidar_como(cenario, inscricoes, chave="x3", etapa=uuid4())
    assert recusa.value.status == 404
