"""O que cada lista faz com a retirada da reserva, até o horizonte do marco (164, US2).

O Edital da `163`: Análise documental (1), Heteroidentificação só `PPI` (2), Prova (3). Maria
(`PPI`) é retirada na Heteroidentificação; Ana (`PPI`) é confirmada; Bia é da ampla.

```text
FR-7012  ordem       Etapa antes da última enumerada → fora do universo reservado;
                     na última enumerada → fica, e `preparar` a deixa sem posição;
                     depois da última enumerada → nenhum efeito. Na ampla, nunca.
FR-7014  ocupação    a reserva não conta quem foi retirado até o horizonte (a Etapa governada)
FR-7027  horizonte   a retirada depois da Etapa governada não alcança as listas do marco
FR-7030  sorteio     a relação da reserva não traz quem foi retirado antes da Etapa de habilitação
```
"""

from types import SimpleNamespace

import pytest

from processo_seletivo.classificacao.application.calculo import _sem_retirada_anterior, _universo
from processo_seletivo.classificacao.domain import universo_classificavel
from processo_seletivo.ocupacao.application.selectors import (
    habilitadas_pelo_corte,
    retiradas_da_reserva,
)
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.sorteios.application.habilitacao import para_o_recorte
from tests.conftest import ator_institucional
from tests.fixtures.alcance import MODALIDADE_PPI, montar_com_alcance
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import concluir_como, distribuir_para

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


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
    cenario = montar_com_alcance(gestor, api_client, manager_headers, seed=1651, codigo="1651")
    maria, ana, bia = inscrever(
        cenario["edital"],
        3,
        primeiro=1,
        modalidades={0: MODALIDADE_PPI, 1: MODALIDADE_PPI},
        perfil=cenario["perfil"],
    )
    todas = [maria, ana, bia]
    distribuir_para(cenario, gestor, ["joao"], todas, chave="analise-1651")
    for inscricao in todas:
        concluir_como(cenario, "joao", inscricao, pontuacao="80")
    _consolidar(cenario, cenario["analise"], todas, chave="consolidar-analise-1651")
    na_hetero = {**cenario, "etapa": cenario["hetero"]}
    distribuir_para(na_hetero, gestor, ["joao"], [maria, ana], chave="hetero-1651")
    concluir_como(na_hetero, "joao", maria, sentido="DESFAVORAVEL")
    concluir_como(na_hetero, "joao", ana, sentido="FAVORAVEL")
    _consolidar(cenario, cenario["hetero"], [maria, ana], chave="consolidar-hetero-1651")
    conteudo = effective_version(edital_id=cenario["edital"].id).content
    return {
        **cenario,
        "maria": maria,
        "ana": ana,
        "bia": bia,
        "conteudo": conteudo,
        "etapas": {str(item["id"]): item for item in conteudo["stages"]},
    }


def _universo_reservado(cenario, ultima):
    etapas = cenario["etapas"]
    perfil = cenario["conteudo"]["profiles"][0]
    etapa_do_marco = etapas[str(ultima)]
    consulta = _universo(cenario["edital"], perfil, etapas, etapa_do_marco)
    return (
        set(consulta.values_list("pk", flat=True)),
        set(
            _sem_retirada_anterior(
                consulta.filter(modality_id=MODALIDADE_PPI), etapas, etapa_do_marco
            ).values_list("pk", flat=True)
        ),
    )


def test_retirada_antes_da_ultima_enumerada_sai_so_da_reservada(cenario):
    """FR-7012: marco que termina na Prova; a Heteroidentificação vem antes."""
    ampla, reservada = _universo_reservado(cenario, cenario["prova"])

    assert cenario["maria"].id in ampla
    assert cenario["maria"].id not in reservada
    assert cenario["ana"].id in reservada


def test_retirada_depois_da_ultima_enumerada_nao_muda_a_ordem(cenario):
    """FR-7012, FR-7027: marco que termina na Análise; a retirada vem depois, e não a alcança."""
    _ampla, reservada = _universo_reservado(cenario, cenario["analise"])

    assert cenario["maria"].id in reservada


def test_retirada_na_ultima_enumerada_fica_sem_posicao_so_na_reservada(cenario):
    """FR-7012: a retirada na Etapa enumerada tira da ordem reservada, como a eliminação; na ampla,
    não tira nada."""
    resultado = ResultadoEtapa.vigentes.get(etapa_id=cenario["hetero"], inscricao=cenario["maria"])
    marco = {"stages": [str(cenario["hetero"])]}
    inscrito = {
        "inscricao_id": str(cenario["maria"].id),
        "protocolo": "P",
        "nome": "Maria",
        "identity_subject": "",
        "modalidade_id": MODALIDADE_PPI,
        "fatos": {},
        "resultados": [
            {
                "id": resultado.id,
                "etapa_id": resultado.etapa_id,
                "pontuacao": None,
                "consequencia": resultado.consequencia,
                "motivo": resultado.motivo,
            }
        ],
    }

    _, sem_posicao = universo_classificavel.preparar(
        marco, cenario["etapas"], [inscrito], recorte=MODALIDADE_PPI
    )
    assert sem_posicao[0]["consequencia"] == ResultadoEtapa.Consequencia.RETIRADA_DA_RESERVA
    assert "continua na ampla concorrência" in sem_posicao[0]["motivo"]

    _, sem_posicao_na_ampla = universo_classificavel.preparar(
        marco, cenario["etapas"], [inscrito], recorte=None
    )
    assert all(
        item["consequencia"] != ResultadoEtapa.Consequencia.RETIRADA_DA_RESERVA
        for item in sem_posicao_na_ampla
    )


def _corte(cenario, *, lista, governada):
    marco = cenario["conteudo"]["profiles"][0]["classificationMilestones"][0]
    return SimpleNamespace(
        lista_id=lista,
        perfil_id=cenario["perfil"],
        marco_id=marco["id"],
        etapa_governada_id=governada,
    )


def test_a_reserva_nao_conta_a_retirada_ate_o_horizonte(cenario):
    """FR-7014: o corte reservado governa a Prova; Maria foi retirada antes dela."""
    corte = _corte(cenario, lista=MODALIDADE_PPI, governada=cenario["prova"])

    assert retiradas_da_reserva(edital=cenario["edital"], corte=corte) == {cenario["maria"].id}
    habilitadas = habilitadas_pelo_corte(
        edital=cenario["edital"], corte=corte, progrediram=[cenario["maria"].id]
    )
    assert cenario["maria"].id not in habilitadas


def test_a_ampla_conta_a_retirada_como_qualquer_inscricao(cenario):
    """FR-7014: na ampla, a subtração não existe."""
    corte = _corte(cenario, lista=None, governada=cenario["prova"])

    assert retiradas_da_reserva(edital=cenario["edital"], corte=corte) == set()


def test_a_retirada_depois_do_horizonte_nao_alcanca_a_reserva(cenario):
    """FR-7027: o corte governa a Análise, que vem antes da Heteroidentificação."""
    corte = _corte(cenario, lista=MODALIDADE_PPI, governada=cenario["analise"])

    assert retiradas_da_reserva(edital=cenario["edital"], corte=corte) == set()


def test_a_relacao_do_sorteio_da_reserva_nao_traz_a_retirada(cenario):
    """FR-7030: a Etapa de habilitação é a Prova; Maria foi retirada antes dela."""
    metodo = {"qualifyingStageId": str(cenario["prova"])}
    habilitadas = {str(cenario["maria"].id), str(cenario["ana"].id), str(cenario["bia"].id)}

    reservada = para_o_recorte(cenario["edital"], metodo, habilitadas, MODALIDADE_PPI)
    ampla = para_o_recorte(cenario["edital"], metodo, habilitadas, None)

    assert str(cenario["maria"].id) not in reservada
    assert ampla == habilitadas


def test_sem_etapa_de_habilitacao_a_relacao_nao_muda(cenario):
    """FR-7030: sem Etapa de habilitação, a relação não lê retirada, como não lê eliminação."""
    assert para_o_recorte(cenario["edital"], {}, None, MODALIDADE_PPI) is None
