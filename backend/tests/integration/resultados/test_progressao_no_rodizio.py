"""A progressão vale no caminho automático, e não só no manual.

**Proteger só a distribuição manual deixaria o rodízio como a porta larga.** Ele parte de todas as
inscrições submetidas com vaga, propõe, e a confirmação cria as Atribuições — sem passar por
`_inscricoes_atribuiveis`. Uma inscrição eliminada na Etapa anterior entraria na proposta e
receberia trabalho, com a aparência de organização automática.

A regra é da **Etapa**, e não da forma de distribuir.
"""

import pytest

from processo_seletivo.avaliacoes.application.distribuicao import (
    confirmar_rodizio,
    propor_rodizio,
)
from processo_seletivo.avaliacoes.models import Atribuicao
from processo_seletivo.resultados.application.consolidacao import consolidar
from tests.conftest import ator_institucional
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.resultado import montar_etapa_de_leitura_unica

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def apos_a_primeira_etapa(gestor, api_client, manager_headers):
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1500, codigo="1500"
    )
    inscricoes = inscrever(cenario["edital"], 3, primeiro=1)
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="lote-1500")
    # 75 habilita, 40 elimina, e a terceira fica sem conclusão — os três estados.
    concluir_como(cenario, "joao", inscricoes[0], pontuacao="75")
    concluir_como(cenario, "joao", inscricoes[1], pontuacao="40")
    consolidar(
        actor=ator_institucional("maria"),
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["primeira"],
        inscricao_ids=[inscricoes[0].id, inscricoes[1].id],
        idempotency_key="k-1500",
        correlation_id="teste",
    )
    cenario["habilitada"], cenario["eliminada"], cenario["sem_resultado"] = inscricoes
    return cenario


def test_a_proposta_do_rodizio_ignora_quem_a_etapa_excluiu(apos_a_primeira_etapa, gestor):
    proposta = propor_rodizio(
        actor=gestor,
        processo=apos_a_primeira_etapa["processo"],
        edital_id=apos_a_primeira_etapa["edital"].id,
        etapa_id=apos_a_primeira_etapa["segunda"],
        membro_ids=[apos_a_primeira_etapa["membros"]["joao"].id],
    )
    # A proposta é um plano agregado — quantos cada pessoa recebe —, e o que ela diz aqui é que
    # **uma** inscrição entra: a habilitada. Antes da correção seriam três, porque o rodízio partia
    # de todas as submetidas.
    assert proposta["inscricoes"] == 1
    assert proposta["total"] == 1


def test_a_confirmacao_do_rodizio_nao_cria_atribuicao_para_a_eliminada(
    apos_a_primeira_etapa, gestor
):
    """A prova que importa: propor não grava, confirmar grava — e é aqui que o dano aconteceria."""
    proposta = propor_rodizio(
        actor=gestor,
        processo=apos_a_primeira_etapa["processo"],
        edital_id=apos_a_primeira_etapa["edital"].id,
        etapa_id=apos_a_primeira_etapa["segunda"],
        membro_ids=[apos_a_primeira_etapa["membros"]["joao"].id],
    )
    confirmar_rodizio(
        actor=gestor,
        processo_id=apos_a_primeira_etapa["processo"].id,
        edital_id=apos_a_primeira_etapa["edital"].id,
        etapa_id=apos_a_primeira_etapa["segunda"],
        membro_ids=[apos_a_primeira_etapa["membros"]["joao"].id],
        assinatura=proposta["assinatura"],
        idempotency_key="rod-1500",
        correlation_id="teste",
    )
    atribuidas = set(
        Atribuicao.objects.filter(
            edital=apos_a_primeira_etapa["edital"],
            etapa_id=apos_a_primeira_etapa["segunda"],
            ativo=True,
        ).values_list("inscricao_id", flat=True)
    )
    assert atribuidas == {apos_a_primeira_etapa["habilitada"].id}
