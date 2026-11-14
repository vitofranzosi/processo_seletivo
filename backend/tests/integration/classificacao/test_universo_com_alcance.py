"""O universo da ordem, quando a última Etapa enumerada é restrita (163, FR-6985).

Perguntar só à última devolveria só quem ela alcança: com a Heteroidentificação por última, a ordem
da ampla sairia vazia. Cada inscrição é decidida pela última enumerada que a alcança.
"""

import pytest

from processo_seletivo.classificacao.application.calculo import _universo
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.resultados.application.consolidacao import consolidar
from tests.conftest import ator_institucional
from tests.fixtures.alcance import MODALIDADE_PCD, MODALIDADE_PPI, montar_com_alcance
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import concluir_como, distribuir_para

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

MODALIDADES = {0: MODALIDADE_PPI, 1: MODALIDADE_PPI, 2: MODALIDADE_PCD}


def _consolidar(cenario, etapa, inscricoes, *, chave):
    return consolidar(
        actor=ator_institucional("maria"),
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=etapa,
        inscricao_ids=[i.id for i in inscricoes],
        idempotency_key=chave,
        correlation_id="teste",
    )


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    """Cinco inscrições — duas PPI, uma PCD, duas da ampla.

    Duas reprovadas na Análise documental: a PPI da posição 0 e a da ampla da posição 4. A regra de
    sempre é que quem foi eliminado **na** Etapa que decide continua no universo — a ordem o trata
    como eliminado —, e quem foi eliminado **antes** dela, não. Para a ampla, a Etapa que decide é a
    Análise; para a PPI, a Heteroidentificação. É isso que separa as duas.
    """
    cenario = montar_com_alcance(gestor, api_client, manager_headers, seed=1638, codigo="1638")
    inscricoes = inscrever(
        cenario["edital"], 5, primeiro=1, modalidades=MODALIDADES, perfil=cenario["perfil"]
    )
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="analise-1638")
    for posicao, inscricao in enumerate(inscricoes):
        concluir_como(cenario, "joao", inscricao, pontuacao="10" if posicao in (0, 4) else "80")
    _consolidar(cenario, cenario["analise"], inscricoes, chave="consolidar-analise-1638")
    cenario["inscricoes"] = inscricoes
    return cenario


def _universo_do_marco(cenario, enumeradas):
    conteudo = effective_version(edital_id=cenario["edital"].id).content
    etapas = {str(item["id"]): item for item in conteudo["stages"]}
    perfil = conteudo["profiles"][0]
    ultima = max((etapas[str(e)] for e in enumeradas), key=lambda etapa: etapa["order"])
    return set(
        _universo(
            cenario["edital"],
            perfil,
            etapas,
            ultima,
            enumeradas=[str(e) for e in enumeradas],
        ).values_list("pk", flat=True)
    )


def test_a_restrita_por_ultima_nao_esvazia_a_ordem_da_ampla(cenario):
    """Antes da 163, o universo seria só a PPI habilitada: a única que a Heteroidentificação tem."""
    universo = _universo_do_marco(cenario, [cenario["analise"], cenario["hetero"]])

    assert universo == {i.id for i in cenario["inscricoes"][1:]}


def test_cada_inscricao_e_decidida_pela_ultima_enumerada_que_a_alcanca(cenario):
    """A PPI reprovada na Análise sai (eliminada antes da Etapa que a decide); a da ampla reprovada
    fica (eliminada na Etapa que a decide), como em todo marco de hoje."""
    universo = _universo_do_marco(cenario, [cenario["analise"], cenario["hetero"]])

    assert cenario["inscricoes"][0].id not in universo
    assert cenario["inscricoes"][4].id in universo


def test_sem_restrita_por_ultima_a_leitura_e_a_de_antes(cenario):
    """A contraprova: com a Análise por última, todas estão no universo, reprovadas inclusive."""
    assert _universo_do_marco(cenario, [cenario["analise"]]) == {
        i.id for i in cenario["inscricoes"]
    }


def test_a_eliminacao_em_etapa_fora_do_marco_vale_para_quem_nenhuma_enumerada_alcanca(cenario):
    """Marco que enumera só a Heteroidentificação: a ampla e a PCD não são alcançadas por nenhuma
    enumerada e entram como num marco sem Etapa — mas a da ampla reprovada na Análise, que o marco
    não enumera, continua fora (D-010, FR-6971). A revisão do PR #542 achou a sobra sem essa regra."""
    universo = _universo_do_marco(cenario, [cenario["hetero"]])

    assert universo == {i.id for i in cenario["inscricoes"][1:4]}
