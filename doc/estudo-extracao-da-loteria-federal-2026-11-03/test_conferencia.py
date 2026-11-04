"""A matriz da POC, sem rede: as respostas são as que a Caixa devolveu em 03/11/2026.

    cd backend && uv run pytest -p no:django -p no:cacheprovider \
        ../doc/estudo-extracao-da-loteria-federal-2026-11-03/test_conferencia.py
"""

import io
import json
import pathlib
import sys
from datetime import date
from urllib import error

import pytest

AQUI = pathlib.Path(__file__).parent
sys.path.insert(0, str(AQUI))

import conferencia as c  # noqa: E402


def gravada(nome):
    return json.loads((AQUI / "respostas" / f"federal_{nome}.json").read_text())


class Caixa:
    """Serve as respostas gravadas por endereço, e conta as chamadas: a carga também é requisito."""

    def __init__(self, **por_endereco):
        self.respostas = por_endereco
        self.chamadas = []

    def __call__(self, url, timeout):
        self.chamadas.append(url)
        chave = url.rsplit("/", 1)[-1] if url != c.ENDERECO_DO_ULTIMO else "ultimo"
        resposta = self.respostas.get(chave, "federal_6115")
        if isinstance(resposta, BaseException):
            raise resposta
        if isinstance(resposta, str):
            resposta = gravada(resposta.removeprefix("federal_"))
        bruto = (
            json.dumps(resposta["corpo"]).encode() if resposta["corpo"] is not None else b"<html>"
        )
        if resposta["status"] != 200:
            raise error.HTTPError(url, resposta["status"], "x", {}, io.BytesIO(bruto))
        return _Corpo(bruto, resposta["status"])


class _Corpo(io.BytesIO):
    def __init__(self, bruto, status):
        super().__init__(bruto)
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def caixa_de_hoje():
    return Caixa(
        ultimo="federal_ultimo",
        **{n: f"federal_{n}" for n in ("6113", "6106", "5000", "1", "6115", "99999")},
        **{"6114": "federal_ultimo"},
    )


DECLARADA = date(2026, 11, 22)


# ---- concurso já realizado: recusa, e com a data ---------------------------------------------


@pytest.mark.parametrize(
    "numero, dia",
    [
        ("5000", date(2015, 8, 26)),
        ("1", date(1962, 9, 15)),
        ("6113", date(2026, 10, 28)),
        ("6114", date(2026, 11, 1)),
        ("006114", date(2026, 11, 1)),
    ],
)
def test_concurso_realizado_e_recusado_com_a_data_em_que_foi(numero, dia):
    caixa = caixa_de_hoje()
    estado = c.situacao(numero, abrir=caixa)
    veredito = c.conferir(estado, declarada_em=DECLARADA)
    assert (estado.estado, estado.realizada_em) == (c.REALIZADA, dia)
    assert veredito.nivel == c.RECUSA and veredito.codigo == "draw_occurrence_already_drawn"
    assert (
        dia.strftime("%d/%m/%Y") in veredito.mensagem and "6114, de 01/11/2026" in veredito.mensagem
    )
    assert len(caixa.chamadas) == 2


def test_realizado_sem_a_segunda_resposta_continua_realizado_sem_data():
    caixa = caixa_de_hoje()
    caixa.respostas["5000"] = error.URLError("timed out")
    estado = c.situacao("5000", abrir=caixa)
    assert estado.estado == c.REALIZADA and estado.realizada_em is None
    assert c.conferir(estado, declarada_em=DECLARADA).nivel == c.RECUSA


# ---- concurso não realizado: conferido, sem afirmar a data -----------------------------------


def test_o_proximo_anunciado_e_conferido_com_uma_chamada_so():
    caixa = caixa_de_hoje()
    estado = c.situacao("6115", abrir=caixa)
    veredito = c.conferir(estado, declarada_em=DECLARADA)
    assert estado.estado == c.NAO_REALIZADA and estado.anunciado_como_proximo is True
    assert veredito.nivel == c.CONFERIDA and "próximo anunciado" in veredito.mensagem
    assert caixa.chamadas == [c.ENDERECO_DO_ULTIMO]


@pytest.mark.parametrize("numero", ["6118", "6200", "9999", "99999"])
def test_o_futuro_distante_nao_e_recusado_nem_confirmado(numero):
    """A sequência não prova a data: o veredito diz a distância e manda conferir o calendário."""
    veredito = c.conferir(c.situacao(numero, abrir=caixa_de_hoje()), declarada_em=DECLARADA)
    assert veredito.nivel == c.CONFERIDA
    assert "não publica a data de concursos futuros" in veredito.mensagem
    assert f"{int(numero) - 6114} concurso(s) adiante" in veredito.mensagem


# ---- forma: recusada sem ir à rede -----------------------------------------------------------


@pytest.mark.parametrize(
    "texto",
    ["6106-9", "Concurso 6115", "6115/2026", "0", "000", "-1", "", "6114.0", "abc", "1234567"],
)
def test_forma_que_a_caixa_nao_aceita_e_recusada_sem_chamada(texto):
    caixa = caixa_de_hoje()
    veredito = c.conferir(c.situacao(texto, abrir=caixa), declarada_em=DECLARADA)
    assert veredito.nivel == c.RECUSA and veredito.codigo == "draw_occurrence_malformed"
    assert caixa.chamadas == []


# ---- a Caixa sem responder: advertência, nunca confirmação -----------------------------------


@pytest.mark.parametrize(
    "principal",
    [
        error.URLError("timed out"),
        TimeoutError("read timed out"),
        "federal_6115",  # 500 no endpoint principal
        {
            "status": 200,
            "corpo": {"numero": 6114, "dataApuracao": "01/11/2026", "listaDezenas": []},
        },
        {
            "status": 200,
            "corpo": {"numero": 6114, "dataApuracao": "2026-11-01", "listaDezenas": ["1"] * 5},
        },
        {
            "status": 200,
            "corpo": {"numero": "6114", "dataApuracao": "01/11/2026", "listaDezenas": ["1"] * 5},
        },
        {"status": 200, "corpo": None},  # HTML no lugar de JSON
        {"status": 503, "corpo": None},
    ],
)
@pytest.mark.parametrize("numero", ["5000", "6115"])
def test_sem_o_ultimo_concurso_nada_se_afirma(principal, numero):
    caixa = caixa_de_hoje()
    caixa.respostas["ultimo"] = principal
    estado = c.situacao(numero, abrir=caixa)
    veredito = c.conferir(estado, declarada_em=DECLARADA)
    assert estado.estado == c.DESCONHECIDA
    assert veredito.nivel == c.ADVERTENCIA and "não confirma" in veredito.mensagem
    assert len(caixa.chamadas) == 1


# ---- no dia do sorteio: mudança de calendário é informada, não decidida aqui -----------------


def test_a_antecipacao_da_6106_e_dita_com_o_sentido():
    """A Caixa antecipou a 6106 de 04/10 para 03/10/2026, pelas eleições (comunicado de 01/10)."""
    estado = c.situacao("6106", abrir=caixa_de_hoje())
    aviso = c.conferir_realizacao(
        numero=6106, realizada_em=estado.realizada_em, declarada_em=date(2026, 10, 4)
    )
    assert aviso.endswith("em 03/10/2026, 1 dia(s) antes.")


def test_realizacao_na_data_declarada_nao_gera_aviso():
    assert (
        c.conferir_realizacao(
            numero=6113, realizada_em=date(2026, 10, 28), declarada_em=date(2026, 10, 28)
        )
        is None
    )
