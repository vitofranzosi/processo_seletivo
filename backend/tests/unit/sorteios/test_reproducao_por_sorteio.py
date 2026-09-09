"""A reprodução usa relação, semente e método — e **ignora** as posições gravadas (FR-040, FR-041).

Uma reprodução que lesse as posições publicadas e as comparasse consigo mesmas sempre concordaria:
provaria que o banco é consistente, e não que a ordem é a que o algoritmo produz. O teste que
importa aqui é o terceiro: com as posições **apagadas**, a reprodução continua devolvendo a mesma
ordem.
"""

import pytest

from processo_seletivo.classificacao.models import PosicaoNaOrdem
from processo_seletivo.sorteios.application.verificacao import reproduzir
from tests.unit.sorteios.test_manifesto import sorteado  # noqa: F401 — fixture compartilhada

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def test_a_reproducao_devolve_a_ordem_publicada(sorteado):  # noqa: F811
    _certame, sorteio = sorteado

    ordem, chaves, metodo, semente = reproduzir(sorteio)

    numero_por_inscricao = {
        p.inscricao_id: p.numero_publico for p in sorteio.relacao.participantes.all()
    }
    publicada = [
        numero_por_inscricao[p.inscricao_id]
        for p in PosicaoNaOrdem.objects.filter(ato=sorteio.ato).order_by("posicao")
    ]
    assert ordem == publicada
    assert semente == sorteio.semente_normalizada
    assert metodo["algorithm"] == "IFES-SORTEIO-SHA256-v1"
    assert len(chaves) == sorteio.relacao.quantidade


def test_a_reproducao_nao_consulta_conteudo_vigente(sorteado, api_client):  # noqa: F811
    """Retificar o Edital depois do ato não altera o que a reprodução devolve (FR-039)."""
    certame, sorteio = sorteado
    antes, _c, _m, _s = reproduzir(sorteio)

    from tests.fixtures.publicacao import retify

    retify(
        api_client,
        certame["edital"],
        [
            {
                "targetPath": (
                    f"/profiles/id={certame['perfil']}"
                    f"/classificationMilestones/id={certame['marco']}/drawMethod/substitutionRule"
                ),
                "operation": "REPLACE",
                "newValue": {"rule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE", "text": "outra frase"},
            }
        ],
    )

    depois, _c, _m, _s = reproduzir(sorteio)
    assert depois == antes


def test_a_reproducao_nao_toca_nas_posicoes_gravadas(sorteado, monkeypatch):  # noqa: F811
    """**A prova que separa reproduzir de reler.**

    As posições são append-only e não podem ser apagadas para testar a ausência delas — a trigger
    recusa, e é ela funcionando. A prova equivalente é tornar a leitura delas impossível: se
    `reproduzir` as consultasse, o teste estouraria aqui em vez de devolver a mesma ordem.
    """
    _certame, sorteio = sorteado
    esperada, _c, _m, _s = reproduzir(sorteio)

    def recusar(*_args, **_kwargs):
        raise AssertionError("a reprodução leu as posições gravadas em vez de recalcular")

    monkeypatch.setattr(PosicaoNaOrdem.objects, "filter", recusar)
    obtida, _c2, _m2, _s2 = reproduzir(sorteio)

    assert obtida == esperada
    assert obtida, "a reprodução não devolveu ordem alguma"
