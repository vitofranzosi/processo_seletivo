"""A Etapa decisória só enumerada pelo marco não impede a publicação (RC-114; 046, `D-001`).

**A Etapa decisória enumerada é porta, e não parcela** (015, `FR-074`): `combinar` a salta, e quem
não tem Resultado nela não é eliminado por ela. A `046` contava a enumeração entre as três maneiras
de um marco consumir o Resultado de uma Etapa, e recusava a publicação dizendo que *"ninguém é
posicionado"* por ele — o que é verdade para a Etapa pontuada, cuja pontuação ausente faz o marco
não posicionar ninguém, e falso para a decisória. A recusa impedia na elaboração o que a `013`
decidiu, em 03/09, não proibir (`FR-047`).

O teste da `046` que prendia a recusa lia só a própria tela; este percorre o que ela afirmava —
publica, consolida a Etapa pontuada, e pergunta à classificação quem ela posiciona.
"""

import pytest

from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.processos.models import Edital
from tests.fixtures.corte import ENTREVISTA, MARCO, montar_cenario_do_corte, rascunho
from tests.fixtures.edital import PROFILE_ID

pytestmark = pytest.mark.django_db(transaction=True)

PORTA = "00000000-0000-4000-8000-000000000469"


def rascunho_com_porta(cut=None):
    """O rascunho do 14/2026 com uma Etapa decisória, não eliminatória, que o marco enumera.

    Ela entra **entre** a pontuada e a Entrevista, e não governada: governar é outra maneira de
    consumir o Resultado, e continua impedindo a publicação — com razão, porque sem Resultado ali
    ninguém seria convocado.
    """
    base, pontuada = rascunho(cut=cut)
    for etapa in base["stages"]:
        if etapa["id"] == ENTREVISTA:
            etapa["order"] = 4
    base["stages"].append(
        {
            "id": PORTA,
            "name": "Heteroidentificação",
            "order": 3,
            "forma": "DECISORIA",
            "rotuloFavoravel": "Apto",
            "rotuloDesfavoravel": "Inapto",
            "eliminatory": False,
            "classificatory": True,
            "minimumScore": None,
            "maximumScore": None,
            "evaluationsPerRegistration": 1,
            "weight": "1.0000",
            "scheduleEventId": None,
        }
    )
    base["profiles"][0]["classificationMilestones"][0]["stages"] = [pontuada["id"], PORTA]
    return base, pontuada


def test_a_porta_so_enumerada_publica_e_a_ordem_posiciona(
    gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
):
    edital, _, inscricoes = montar_cenario_do_corte(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="rc-114",
        draft_factory=rascunho_com_porta,
    )

    assert edital.status == Edital.Status.PUBLICADO
    proposta = calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    posicionados = [str(item["inscricao_id"]) for item in proposta["posicoes"]]
    # Os três que a pontuada avaliou, na ordem das notas — 90, 80, 70 —, sem Resultado na porta.
    assert posicionados == [str(i.id) for i in inscricoes[:3]]
