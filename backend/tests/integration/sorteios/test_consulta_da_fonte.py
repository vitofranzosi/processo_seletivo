"""A consulta do adaptador da Loteria Federal, sobre as respostas gravadas (116, FR-3628–FR-3631).

`urlopen` responde com o que a Caixa devolveu em 03/11/2026 (`tests/fixtures/caixa/`). O adaptador
real roda: a validação do *payload*, a classificação dos motivos e o número de tentativas são o que
se testa. A observação (`observar`) é outra porta e não muda (FR-3638): o último caso o prende.
"""

import copy
from datetime import UTC, date, datetime
from urllib import error

import pytest
from django.test import override_settings

from processo_seletivo.sorteios.domain import conferencia as dominio
from processo_seletivo.sorteios.infrastructure import fontes
from processo_seletivo.sorteios.infrastructure.fontes import loteria_federal
from processo_seletivo.sorteios.infrastructure.fontes.loteria_federal import (
    FonteDeTeste,
    FonteDeTesteSoData,
    LoteriaFederal,
)
from tests.fixtures.caixa_gravada import Servidor, gravada

AGORA = datetime(2026, 11, 3, 22, 3, tzinfo=UTC)


def _ultimo_com(**campos):
    resposta = copy.deepcopy(gravada("ultimo"))
    resposta["corpo"].update(campos)
    return resposta


def test_o_ultimo_concurso_valido(caixa):
    servidor = Servidor(federal="ultimo")
    caixa.pela_rede(servidor)
    consulta = LoteriaFederal().consultar_ultimo()
    assert consulta.ultimo == dominio.UltimoConcurso(6114, date(2026, 11, 1), proximo=6115)
    assert consulta.motivo == ""
    assert [url for url, _ in servidor.pedidos] == [loteria_federal.ENDERECO_DO_ULTIMO]


@pytest.mark.parametrize(
    ("resposta", "motivo"),
    [
        (_ultimo_com(listaDezenas=[]), dominio.SEM_O_ULTIMO),
        (_ultimo_com(listaDezenas=["056338", "001871"]), dominio.SEM_O_ULTIMO),
        (_ultimo_com(dataApuracao="2026-11-01"), dominio.SEM_O_ULTIMO),
        (_ultimo_com(numero="6114"), dominio.SEM_O_ULTIMO),
        (
            {"status": 200, "corpo": b"<html><body>Acesso negado</body></html>"},
            dominio.SEM_O_ULTIMO,
        ),
        ({"status": 503, "corpo": b"Service Unavailable"}, dominio.COM_ERRO),
        ({"status": 500, "corpo": {"message": "erro"}}, dominio.COM_ERRO),
        (TimeoutError("timed out"), dominio.SEM_RESPOSTA_A_TEMPO),
        (error.URLError(TimeoutError("timed out")), dominio.SEM_RESPOSTA_A_TEMPO),
        (error.URLError("Name or service not known"), dominio.SEM_CONEXAO),
    ],
)
def test_resposta_sem_o_ultimo_concurso_nao_traz_ultimo(caixa, resposta, motivo):
    """Faltando número inteiro, data no formato da Caixa ou os cinco bilhetes: nada (FR-3628)."""
    caixa.pela_rede(Servidor(federal=resposta))
    consulta = LoteriaFederal().consultar_ultimo()
    assert consulta.ultimo is None
    assert consulta.motivo == motivo


def test_a_data_de_um_concurso_realizado(caixa):
    caixa.pela_rede(Servidor(**{"5000": "5000"}))
    assert LoteriaFederal().consultar_data(5000) == date(2015, 8, 26)


def test_o_500_da_caixa_nao_e_excecao_nem_estado(caixa):
    """O 500 do concurso futuro é o mesmo do erro do serviço: só quer dizer "sem data" (FR-3629)."""
    caixa.pela_rede(Servidor(**{"6115": "6115", "0": "0", "99999": "99999"}))
    adaptador = LoteriaFederal()
    assert adaptador.consultar_data(6115) is None
    assert adaptador.consultar_data(0) is None
    assert adaptador.consultar_data(99999) is None


def test_a_data_de_outro_concurso_nao_vale(caixa):
    """A resposta que traz outro número não dá a data do pedido."""
    caixa.pela_rede(Servidor(**{"5000": "6113"}))
    assert LoteriaFederal().consultar_data(5000) is None


@override_settings(SORTEIO_CONFERENCIA_TIMEOUT_SEGUNDOS=3, SORTEIO_FONTE_TENTATIVAS=3)
def test_uma_tentativa_com_tempo_limite(caixa):
    """Uma chamada por consulta, mesmo na falha, com o tempo limite da conferência (FR-3631)."""
    servidor = Servidor(federal=TimeoutError("timed out"), **{"5000": TimeoutError("timed out")})
    caixa.pela_rede(servidor)
    adaptador = LoteriaFederal()
    adaptador.consultar_ultimo()
    adaptador.consultar_data(5000)
    assert [timeout for _, timeout in servidor.pedidos] == [3, 3]


def test_a_observacao_continua_com_tres_tentativas(caixa):
    """`observar` não muda (FR-3638): três tentativas e a falha de acesso de sempre."""
    servidor = Servidor(**{"6115": error.URLError("timed out")})
    caixa.pela_rede(servidor)
    with override_settings(SORTEIO_FONTE_TENTATIVAS=3):
        observacao = LoteriaFederal().observar(fonte="Loteria Federal", referencia="6115")
    assert observacao.falha_de_acesso is True
    assert len(servidor.pedidos) == 3


@pytest.mark.parametrize("classe", [FonteDeTeste, FonteDeTesteSoData])
def test_a_demonstracao_responde_pela_tabela(caixa, classe):
    """5000 realizado, 9998 inconclusivo, o resto ainda não realizado — sem rede (FR-3650)."""

    def recusar(*_args, **_kwargs):
        raise AssertionError("a fonte de demonstração abriu conexão")

    caixa.pela_rede(recusar)
    situacoes = classe().conferir_referencias(
        ["5000", "9998", "6200", "Concurso 5900"], fonte="Fonte de demonstração", agora=AGORA
    )
    assert situacoes["5000"].estado == dominio.REALIZADO
    assert situacoes["5000"].realizada_em == date(2015, 8, 26)
    assert situacoes["9998"].estado == dominio.INCONCLUSIVO
    assert situacoes["6200"].estado == dominio.AINDA_NAO_REALIZADO
    # A forma da demonstração é a de hoje (FR-3625): texto continua aceito, e não é "inválido".
    assert situacoes["Concurso 5900"].estado == dominio.AINDA_NAO_REALIZADO


def test_a_porta_declara_forma_e_conferencia_por_fonte():
    """A forma é propriedade da fonte (FR-3625, D-008)."""
    assert fontes.forma_da_referencia("Loteria Federal") is dominio.FORMA_DO_CONCURSO
    assert fontes.forma_da_referencia("Fonte de demonstração") is None
    assert fontes.sabe_conferir("Loteria Federal") is True
    assert fontes.sabe_conferir("Fonte de demonstração") is True
    assert fontes.sabe_conferir("Random.org") is None


@override_settings(SORTEIO_FONTE_DE_DEMONSTRACAO=False)
def test_em_producao_a_demonstracao_nao_existe():
    assert "Fonte de demonstração" not in fontes.fontes_publicadas()
    assert fontes.sabe_conferir("Fonte de demonstração") is None
    assert fontes.forma_da_referencia("Fonte de demonstração") is None
