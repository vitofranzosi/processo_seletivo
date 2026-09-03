"""T056 e T058 — a porta que fecha, e a que continua aberta.

A assimetria é o conteúdo deste arquivo. **Reabrir** muda a pontuação, e o Resultado a afirma: é
recusado por inteiro, antes de qualquer efeito. **Impedir** não muda pontuação nenhuma: aplica-se
por inteiro, inativa até a Atribuição da fonte, e o Resultado permanece — declarado como
contestado, e não alterado.
"""

import pytest

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.avaliacoes.application.avaliacao import reabrir
from processo_seletivo.avaliacoes.application.impedimento import registrar_impedimento
from processo_seletivo.avaliacoes.models import Atribuicao, Avaliacao
from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.resultado import montar_etapa_de_leitura_unica

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def consolidado(gestor, api_client, manager_headers):
    """Duas inscrições avaliadas pela mesma pessoa; **uma** delas consolidada."""
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1430, codigo="1430"
    )
    inscricoes = inscrever(cenario["edital"], 2, primeiro=1)
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="lote-1430")
    avaliacoes = [concluir_como(cenario, "joao", i, pontuacao="75") for i in inscricoes]
    consolidar(
        actor=ator_institucional("maria"),
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["primeira"],
        inscricao_ids=[inscricoes[0].id],
        idempotency_key="k-1430",
        correlation_id="teste",
    )
    cenario["inscricoes"] = inscricoes
    cenario["avaliacoes"] = avaliacoes
    return cenario


def tentar_reabrir(cenario, avaliacao, *, chave):
    return reabrir(
        actor=ator_institucional("maria"),
        processo_id=cenario["processo"].id,
        avaliacao_id=avaliacao.id,
        motivo="Erro material apontado em recurso.",
        expected_revision=avaliacao.revision,
        idempotency_key=chave,
        correlation_id="teste",
    )


def test_reabrir_a_fonte_de_um_resultado_e_recusado_sem_efeito(consolidado):
    fonte = consolidado["avaliacoes"][0]
    fonte.refresh_from_db()
    revisao, eventos = fonte.revision, RegistroAuditoria.objects.count()

    with pytest.raises(DomainError) as recusa:
        tentar_reabrir(consolidado, fonte, chave="r1")
    assert recusa.value.code == "avaliacao_fundamenta_resultado"
    assert recusa.value.status == 409

    fonte.refresh_from_db()
    assert fonte.estado == Avaliacao.Estado.CONCLUIDA
    assert fonte.revision == revisao
    # Nenhum efeito parcial: nem estado, nem revisão, nem trilha.
    assert RegistroAuditoria.objects.count() == eventos


def test_a_recusa_nao_expoe_a_pontuacao(consolidado):
    """Quem organiza o trabalho não é necessariamente quem pode ver a nota (FR-033)."""
    with pytest.raises(DomainError) as recusa:
        tentar_reabrir(consolidado, consolidado["avaliacoes"][0], chave="r2")
    assert "75" not in recusa.value.detail


def test_reabrir_avaliacao_nao_consolidada_continua_funcionando(consolidado):
    """A não regressão que mais importa: a 012 não fechou junto."""
    solta = consolidado["avaliacoes"][1]
    solta.refresh_from_db()
    tentar_reabrir(consolidado, solta, chave="r3")
    solta.refresh_from_db()
    assert solta.estado == Avaliacao.Estado.RASCUNHO


def test_o_impedimento_se_aplica_por_inteiro_e_declara_o_contestado(consolidado):
    """Inativa **todas** as alcançadas, inclusive a fonte — e não toca o Resultado."""
    resultado = ResultadoEtapa.objects.get(inscricao=consolidado["inscricoes"][0])
    desfecho = registrar_impedimento(
        actor=ator_institucional("maria"),
        processo_id=consolidado["processo"].id,
        identity_subject="joao",
        inscricao_id=consolidado["inscricoes"][0].id,
        motivo="Parentesco descoberto depois da consolidação.",
        idempotency_key="i1",
        correlation_id="teste",
    )

    assert desfecho["inativadas"] == 1
    assert desfecho["resultados_contestados"] == [
        {
            "inscricao": consolidado["inscricoes"][0].protocolo,
            "resultado": str(resultado.id),
        }
    ]
    # A Atribuição da fonte foi inativada: é ela que a cadeia de autorização consulta.
    assert not Atribuicao.objects.filter(pk=resultado.avaliacao.atribuicao_id, ativo=True).exists()
    # E o Resultado permanece exatamente como estava.
    resultado.refresh_from_db()
    assert resultado.consequencia == ResultadoEtapa.Consequencia.HABILITADA
    assert str(resultado.pontuacao) == "75.0000"
