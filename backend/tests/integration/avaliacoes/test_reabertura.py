"""Reabrir é ato da presidência, com motivo, registrado — e não destrói o que foi concluído."""

import pytest

from processo_seletivo.avaliacoes.application.avaliacao import REABRIR, concluir, gravar
from processo_seletivo.avaliacoes.application.avaliacao import reabrir as reabrir_avaliacao
from processo_seletivo.avaliacoes.models import Avaliacao, ConclusaoAvaliacao
from processo_seletivo.processos.models import AtoAdministrativo
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.mesa import concluir_como, distribuir_para, inscricoes_de, montar_banca

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

MOTIVO = "Recurso deferido: o diploma apresentado atende ao item 4.2."


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    return montar_banca(gestor, api_client, manager_headers, seed=10, codigo="A1")


@pytest.fixture
def concluida(cenario, gestor):
    inscricao = inscricoes_de(cenario, 1, primeiro=1000)[0]
    distribuir_para(cenario, gestor, ["joao"], [inscricao])
    return concluir_como(cenario, "joao", inscricao, pontuacao="60", parecer="Insuficiente")


def reabrir(gestor, cenario, avaliacao, *, motivo=MOTIVO, chave="reabrir", revisao=None):
    return reabrir_avaliacao(
        actor=gestor,
        processo_id=cenario["processo"].id,
        avaliacao_id=avaliacao.id,
        motivo=motivo,
        expected_revision=avaliacao.revision if revisao is None else revisao,
        idempotency_key=chave,
        correlation_id="teste",
    )


def test_a_reabertura_exige_motivo(gestor, cenario, concluida):
    """É o motivo que separa recurso e erro material de reabertura silenciosa (FR-036)."""
    with pytest.raises(DomainError) as recusa:
        reabrir(gestor, cenario, concluida, motivo="  ")

    assert recusa.value.code == "motivo_obrigatorio"


def test_reabrir_devolve_a_avaliacao_ao_rascunho_e_registra_o_ato(gestor, cenario, concluida):
    reaberta = reabrir(gestor, cenario, concluida)

    assert reaberta.estado == Avaliacao.Estado.RASCUNHO
    assert reaberta.concluida_em is None
    assert reaberta.versao_id is None
    ato = AtoAdministrativo.objects.get(operation=REABRIR)
    assert ato.reason == MOTIVO
    assert ato.actor_subject == "carlos"


def test_reabrir_nao_destroi_o_que_havia_sido_concluido(gestor, cenario, concluida):
    """FR-094: "o que aquela pessoa havia concluído antes" é uma consulta, e não arqueologia."""
    reabrir(gestor, cenario, concluida)

    preservada = ConclusaoAvaliacao.objects.get(avaliacao=concluida)
    assert str(preservada.pontuacao) == "60.0000"
    assert preservada.parecer == "Insuficiente"
    assert preservada.versao_id is not None
    assert preservada.concluida_por == "joao"


def test_cada_conclusao_soma_uma_linha_preservada(gestor, cenario, concluida):
    """Depois de quantas reaberturas vierem, cada conclusão continua respondível."""
    reabrir(gestor, cenario, concluida, chave="r1")
    atual = Avaliacao.objects.get(pk=concluida.pk)
    concluir(
        ator=ator_institucional("joao"),
        edital=cenario["edital"],
        etapa_id=cenario["etapa"],
        inscricao_id=atual.inscricao_id,
        pontuacao="85",
        parecer="Revisto após o recurso.",
        expected_revision=atual.revision,
        versao_reconhecida=cenario["edital"].versoes_consolidadas.latest("materialized_at").id,
        correlation_id="teste",
    )

    conclusoes = ConclusaoAvaliacao.objects.filter(avaliacao=concluida).order_by("ordem")
    assert [c.ordem for c in conclusoes] == [1, 2]
    assert [str(c.pontuacao) for c in conclusoes] == ["60.0000", "85.0000"]


def test_concluir_numa_aba_aberta_desde_antes_e_recusado(gestor, cenario, concluida):
    """FR-082: o avaliador nunca conclui sobre um estado que deixou de existir."""
    revisao_antiga = concluida.revision
    reabrir(gestor, cenario, concluida)

    with pytest.raises(DomainError) as recusa:
        concluir(
            ator=ator_institucional("joao"),
            edital=cenario["edital"],
            etapa_id=cenario["etapa"],
            inscricao_id=concluida.inscricao_id,
            pontuacao="99",
            parecer="Da aba antiga",
            expected_revision=revisao_antiga,
            versao_reconhecida=cenario["edital"].versoes_consolidadas.latest("materialized_at").id,
            correlation_id="teste",
        )

    assert recusa.value.code == "stale_revision"


def test_reabrir_o_que_nao_esta_concluido_e_transicao_invalida(gestor, cenario):
    """FR-083. Responder sucesso faria a tela afirmar um ato que não aconteceu."""
    inscricao = inscricoes_de(cenario, 1, primeiro=1010)[0]
    distribuir_para(cenario, gestor, ["joao"], [inscricao], chave="rascunho")
    avaliacao, _ = gravar(
        ator=ator_institucional("joao"),
        edital=cenario["edital"],
        etapa_id=cenario["etapa"],
        inscricao_id=inscricao.id,
        pontuacao="70",
        parecer="",
        expected_revision=1,
        correlation_id="teste",
    )

    with pytest.raises(DomainError) as recusa:
        reabrir(gestor, cenario, avaliacao, chave="r-rascunho")

    assert recusa.value.code == "transicao_invalida"


def test_depois_de_reaberta_o_avaliador_volta_a_gravar(gestor, cenario, concluida):
    """A reabertura devolve o trabalho — senão ela seria só um carimbo."""
    reabrir(gestor, cenario, concluida)
    atual = Avaliacao.objects.get(pk=concluida.pk)

    avaliacao, _ = gravar(
        ator=ator_institucional("joao"),
        edital=cenario["edital"],
        etapa_id=cenario["etapa"],
        inscricao_id=atual.inscricao_id,
        pontuacao="88",
        parecer="Reavaliando",
        expected_revision=atual.revision,
        correlation_id="teste",
    )

    assert avaliacao.estado == Avaliacao.Estado.RASCUNHO
    assert str(avaliacao.pontuacao) == "88.0000"


def test_quem_nao_gere_a_comissao_nao_reabre(cenario, concluida):
    """Reabrir é ato da presidência — o avaliador não desfaz a própria conclusão."""
    joao = ator_institucional("joao")

    with pytest.raises(DomainError) as recusa:
        reabrir_avaliacao(
            actor=joao,
            processo_id=cenario["processo"].id,
            avaliacao_id=concluida.id,
            motivo=MOTIVO,
            expected_revision=concluida.revision,
            idempotency_key="joao-tenta",
            correlation_id="teste",
        )

    assert recusa.value.status == 404


def test_a_mesma_chave_com_outro_motivo_e_conflito(gestor, cenario, concluida):
    """O motivo entra no conteúdo da chave (FR-084).

    Num ato cujo motivo é a sua própria justificativa, tratar motivos diferentes como repetição
    registraria uma reabertura que ninguém pediu.
    """
    reabrir(gestor, cenario, concluida, chave="mesma", motivo="Recurso deferido.")

    with pytest.raises(DomainError) as recusa:
        reabrir(gestor, cenario, concluida, chave="mesma", motivo="Erro material.")

    assert recusa.value.code == "idempotency_conflict"


def test_a_mesma_chave_com_outra_revisao_e_conflito(gestor, cenario, concluida):
    """A revisão também: ela é a precondição do ato, e não um detalhe do envio."""
    reabrir(gestor, cenario, concluida, chave="rev")

    with pytest.raises(DomainError) as recusa:
        reabrir(gestor, cenario, concluida, chave="rev", revisao=concluida.revision + 5)

    assert recusa.value.code == "idempotency_conflict"
