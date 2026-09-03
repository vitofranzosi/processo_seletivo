"""T032 e T033 — repetir o lote, e disputá-lo.

Três formas de repetição, e elas respondem coisas diferentes: a mesma chave com o mesmo conteúdo é
**repetição** e devolve o desfecho original; a mesma chave com conteúdo diferente é **conflito**; e
chave nova sobre par já consolidado é **recusa nomeada** — nunca sucesso silencioso, que faria a
tela afirmar um ato que não aconteceu.
"""

from uuid import UUID, uuid4

import pytest

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.resultados.application.consolidacao import CONSOLIDAR, consolidar
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.resultado import montar_etapa_de_leitura_unica

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def pronto(gestor, api_client, manager_headers):
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1350, codigo="1350"
    )
    inscricoes = inscrever(cenario["edital"], 2, primeiro=1)
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="lote-1350")
    concluir_como(cenario, "joao", inscricoes[0], pontuacao="75")
    cenario["inscricoes"] = inscricoes
    return cenario


def consolidar_como(cenario, presidente, inscricoes, *, chave):
    return consolidar(
        actor=presidente,
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["etapa"],
        inscricao_ids=[i.id for i in inscricoes],
        idempotency_key=chave,
        correlation_id="teste",
    )


@pytest.fixture
def presidente():
    return ator_institucional("maria")


def test_o_lote_cria_as_prontas_e_recusa_as_demais(pronto, presidente):
    desfecho = consolidar_como(pronto, presidente, pronto["inscricoes"], chave="c1")
    assert desfecho["feitas"] == 1
    assert desfecho["recusadas"] == 1
    assert "ainda não há avaliação concluída" in desfecho["motivos"][0]["motivo"]


def test_a_mesma_chave_com_o_mesmo_conteudo_devolve_o_desfecho_original(pronto, presidente):
    """Zero Resultados e zero eventos adicionais — e o desfecho **idêntico**, não um vazio."""
    primeiro = consolidar_como(pronto, presidente, pronto["inscricoes"], chave="c2")
    eventos = RegistroAuditoria.objects.filter(operation=CONSOLIDAR).count()

    repetido = consolidar_como(pronto, presidente, pronto["inscricoes"], chave="c2")
    assert repetido == primeiro
    assert ResultadoEtapa.objects.count() == 1
    assert RegistroAuditoria.objects.filter(operation=CONSOLIDAR).count() == eventos


def test_a_mesma_chave_com_conteudo_diferente_e_conflito(pronto, presidente):
    consolidar_como(pronto, presidente, pronto["inscricoes"][:1], chave="c3")
    with pytest.raises(DomainError) as recusa:
        consolidar_como(pronto, presidente, pronto["inscricoes"], chave="c3")
    assert recusa.value.status == 409


def test_chave_nova_sobre_par_consolidado_recusa_o_item(pronto, presidente):
    """Recusa nomeada, e não sucesso silencioso: o ato pedido não aconteceu."""
    consolidar_como(pronto, presidente, pronto["inscricoes"][:1], chave="c4")
    desfecho = consolidar_como(pronto, presidente, pronto["inscricoes"][:1], chave="c5")
    assert desfecho["feitas"] == 0
    assert "já possui Resultado" in desfecho["motivos"][0]["motivo"]


def test_cada_resultado_criado_gera_exatamente_um_evento(pronto, presidente):
    consolidar_como(pronto, presidente, pronto["inscricoes"], chave="c6")
    eventos = RegistroAuditoria.objects.filter(operation=CONSOLIDAR)
    assert eventos.count() == 1
    # A trilha diz o ato e o agregado, e **não** carrega pontuação nem parecer (FR-040).
    evento = eventos.first()
    assert evento.aggregate_type == "ResultadoEtapa"
    assert "75" not in evento.reason


def test_selecao_vazia_e_erro_do_pedido(pronto, presidente):
    with pytest.raises(DomainError) as recusa:
        consolidar_como(pronto, presidente, [], chave="c7")
    assert recusa.value.code == "selecao_vazia"


def test_dois_lotes_concorrentes_produzem_no_maximo_um_resultado(pronto, presidente):
    """O invólucro serializa por Processo; a unicidade é o cinto que sobra.

    O segundo lote não disputa: ele espera o bloqueio e depois **encontra** o Resultado, recusando
    o item com frase — que é o desfecho explícito que a spec pede, e não uma exceção de
    integridade vazando para a tela.
    """
    consolidar_como(pronto, presidente, pronto["inscricoes"][:1], chave=uuid4().hex)
    segundo = consolidar_como(pronto, presidente, pronto["inscricoes"][:1], chave=uuid4().hex)
    assert segundo["feitas"] == 0
    assert ResultadoEtapa.objects.filter(inscricao=pronto["inscricoes"][0]).count() == 1


def test_a_pontuacao_e_a_consequencia_saem_da_fonte_e_da_regra(pronto, presidente):
    consolidar_como(pronto, presidente, pronto["inscricoes"][:1], chave="c8")
    resultado = ResultadoEtapa.objects.get(inscricao=pronto["inscricoes"][0])
    assert str(resultado.pontuacao) == "75.0000"
    assert resultado.consequencia == ResultadoEtapa.Consequencia.HABILITADA
    assert UUID(str(resultado.etapa_id)) == UUID(str(pronto["etapa"]))
