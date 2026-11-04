"""A conferência da referência, pura e sem banco (116, FR-3623, FR-3627–FR-3630, FR-3639–FR-3642).

**A matriz é a da POC do estudo de 03/11/2026**, com as respostas que a Caixa de fato devolveu: o
último concurso realizado era o 6114, de 01/11/2026, e o próximo anunciado, o 6115. As divergências
deliberadas da POC estão no plan, §2: a situação "ainda não realizado" é informação, e não
"conferida"; o I/O saiu daqui; e a mensagem depende do ato.
"""

import re
from datetime import UTC, date, datetime

import pytest

from processo_seletivo.shared.tempo import ZONA
from processo_seletivo.sorteios.domain import conferencia as c

LF = "Loteria Federal"
# O instante da consulta em UTC de propósito: a mensagem e o registro precisam dizê-lo no fuso
# institucional (FR-3642), e 22h03 UTC são 19h03 em Vitória — outra hora, e o mesmo dia.
CONSULTADA_EM = datetime(2026, 11, 3, 22, 3, tzinfo=UTC)
ULTIMO = c.ConsultaDoUltimo(c.UltimoConcurso(numero=6114, em=date(2026, 11, 1), proximo=6115))
DATAS = {1: date(1962, 9, 15), 5000: date(2015, 8, 26), 6113: date(2026, 10, 28)}


def _situacao(referencia, consulta=ULTIMO, *, com_data=True):
    numero = c.numero_do_concurso(referencia)
    return c.situacao(
        fonte=LF,
        referencia=referencia,
        consulta=consulta,
        consultada_em=CONSULTADA_EM,
        data_da_referencia=DATAS.get(numero) if com_data else None,
    )


# --- a situação ------------------------------------------------------------------------------


@pytest.mark.parametrize("referencia", ["5000", "1", "6113", "6114"])
def test_menor_ou_igual_ao_ultimo_e_realizado(referencia):
    situacao = _situacao(referencia)
    assert situacao.estado == c.REALIZADO
    assert situacao.ultimo == 6114
    assert situacao.ultimo_em == date(2026, 11, 1)


@pytest.mark.parametrize("referencia", ["6115", "6118", "6200", "9999", "99999"])
def test_maior_que_o_ultimo_e_ainda_nao_realizado(referencia):
    assert _situacao(referencia).estado == c.AINDA_NAO_REALIZADO


def test_realizado_sem_data_continua_realizado():
    """A consulta pelo número só acrescenta a data; a falta dela não desfaz o fato (FR-3629)."""
    situacao = _situacao("6113", com_data=False)
    assert situacao.estado == c.REALIZADO
    assert situacao.realizada_em is None
    assert "data não informada pela Caixa" in c.mensagem(situacao, c.PUBLICACAO)


@pytest.mark.parametrize(
    "referencia",
    ["6106-9", "Concurso 6115", "6115/2026", "0", "000", "-1", "", "6114.0", "abc", "1234567"],
)
def test_fora_da_forma_e_referencia_invalida_sem_consulta(referencia):
    """A forma se decide sem rede: a situação nasce inválida mesmo sem resposta da Caixa."""
    situacao = c.situacao(
        fonte=LF, referencia=referencia, consulta=None, consultada_em=CONSULTADA_EM
    )
    assert situacao.estado == c.REFERENCIA_INVALIDA
    assert c.numero_do_concurso(referencia) is None


def test_zeros_a_esquerda_sao_o_mesmo_concurso():
    assert c.numero_do_concurso("006114") == 6114
    assert c.normalizar("006114") == "6114"
    # Nada além dos zeros: o dígito verificador e o texto nunca viram outro número em silêncio.
    assert c.normalizar("6106-9") == "6106-9"
    assert c.normalizar(" 6114") == " 6114"


def test_sem_o_ultimo_e_inconclusivo_com_o_motivo():
    consulta = c.ConsultaDoUltimo(None, motivo=c.SEM_O_ULTIMO)
    situacao = _situacao("5000", consulta)
    assert situacao.estado == c.INCONCLUSIVO
    assert situacao.motivo == "a Caixa respondeu sem o último concurso"


def test_o_futuro_distante_informa_a_distancia_e_nao_recusa():
    situacao = _situacao("9999")
    assert situacao.estado == c.AINDA_NAO_REALIZADO
    assert c.decisao(situacao, c.PUBLICACAO) == c.INFORMA
    mensagem = c.mensagem(situacao, c.PUBLICACAO, declarada_em=date(2030, 1, 1))
    assert "3885 concurso(s) adiante" in mensagem
    assert f"{(date(2030, 1, 1) - date(2026, 11, 1)).days} dia(s) depois" in mensagem


# --- a decisão por ato -----------------------------------------------------------------------

ATOS_DO_EDITAL = (c.SUBMISSAO, c.PUBLICACAO, c.RETIFICACAO)


@pytest.mark.parametrize(
    ("referencia", "consulta", "ato", "esperada"),
    [
        *[("5000", ULTIMO, ato, c.IMPEDE) for ato in (*ATOS_DO_EDITAL, c.CONGELAMENTO)],
        *[("6116", ULTIMO, ato, c.INFORMA) for ato in (*ATOS_DO_EDITAL, c.CONGELAMENTO)],
        *[
            ("6116", c.ConsultaDoUltimo(None, c.SEM_RESPOSTA_A_TEMPO), ato, c.ADVERTE)
            for ato in (*ATOS_DO_EDITAL, c.CONGELAMENTO)
        ],
        *[("6106-9", ULTIMO, ato, c.IMPEDE) for ato in ATOS_DO_EDITAL],
        # O acervo publicado antes desta feature: no congelamento a forma adverte (D-005).
        ("Concurso 6100", ULTIMO, c.CONGELAMENTO, c.ADVERTE),
    ],
)
def test_a_tabela_de_decisao_por_ato(referencia, consulta, ato, esperada):
    assert c.decisao(_situacao(referencia, consulta), ato) == esperada


# --- as mensagens (contracts/mensagens.md) ---------------------------------------------------


def test_mensagem_de_realizado_nos_atos_do_edital():
    mensagem = c.mensagem(_situacao("5000"), c.SUBMISSAO)
    for parte in ("5000", "já foi realizado", "26/08/2015", "6114", "01/11/2026", "posterior"):
        assert parte in mensagem
    assert "fim das inscrições" in mensagem


def test_mensagem_de_realizado_no_congelamento():
    mensagem = c.mensagem(_situacao("6113"), c.CONGELAMENTO)
    for parte in ("Não é possível congelar", "6113", "28/10/2026", "retifique", "só então"):
        assert parte in mensagem


def test_mensagem_da_referencia_invalida():
    mensagem = c.mensagem(_situacao("6106-9"), c.SUBMISSAO)
    assert '"6106-9"' in mensagem
    assert "só pelo número" in mensagem
    assert "informe só o número do concurso, como 6106 — sem dígito verificador, texto ou ano" in (
        mensagem
    )
    assert c.mensagem_da_forma("6106-9") == mensagem


def test_mensagem_da_referencia_invalida_no_congelamento_adverte():
    mensagem = c.mensagem(_situacao("Concurso 6100"), c.CONGELAMENTO)
    assert '"Concurso 6100"' in mensagem
    assert "Retifique o método antes do dia do sorteio" in mensagem


def test_mensagem_de_ainda_nao_realizado():
    mensagem = c.mensagem(_situacao("6116"), c.PUBLICACAO, declarada_em=date(2026, 11, 8))
    for parte in (
        "ainda não realizado na consulta de",
        "03/11/2026 às 19:03",
        "6114",
        "2 concurso(s) adiante",
        "não é verificada pela Caixa",
        "08/11/2026",
        "7 dia(s) depois",
    ):
        assert parte in mensagem


def test_o_proximo_anunciado_e_dito():
    mensagem = c.mensagem(_situacao("6115"), c.PUBLICACAO, declarada_em=date(2026, 11, 5))
    assert "(o próximo anunciado pela Caixa)" in mensagem
    assert "(o próximo anunciado" not in c.mensagem(_situacao("6116"), c.PUBLICACAO)


PROIBIDAS = re.compile(r"validad|confirmad|conferid", re.IGNORECASE)


@pytest.mark.parametrize("ato", [*ATOS_DO_EDITAL, c.CONGELAMENTO, c.SOB_DEMANDA])
@pytest.mark.parametrize("referencia", ["6115", "6116", "9999"])
@pytest.mark.parametrize("declarada_em", [None, date(2026, 11, 8)])
def test_ainda_nao_realizado_nunca_diz_validado_confirmado_ou_conferido(
    ato, referencia, declarada_em
):
    """SC-1095: nem na mensagem, nem no registro, nem no rótulo da situação."""
    situacao = _situacao(referencia)
    textos = [
        c.mensagem(situacao, ato, declarada_em=declarada_em),
        c.ROTULOS[situacao.estado],
        repr(c.registro(situacao, c.decisao(situacao, ato))),
    ]
    for texto in textos:
        assert not PROIBIDAS.search(texto), texto


@pytest.mark.parametrize(
    "motivo",
    [c.SEM_RESPOSTA_A_TEMPO, c.SEM_CONEXAO, c.SEM_O_ULTIMO, c.COM_ERRO],
)
def test_mensagem_de_inconclusivo_com_cada_motivo(motivo):
    situacao = _situacao("6116", c.ConsultaDoUltimo(None, motivo))
    mensagem = c.mensagem(situacao, c.PUBLICACAO)
    assert motivo in mensagem
    assert "não confirma nem recusa" in mensagem
    assert "resultado oficial" in mensagem
    assert "A relação foi publicada." not in mensagem
    assert "A relação foi publicada." in c.mensagem(situacao, c.CONGELAMENTO)


def test_os_quatro_motivos_sao_os_do_contrato():
    assert set(c.MOTIVOS) == {
        "a Caixa não respondeu a tempo",
        "não foi possível falar com a Caixa",
        "a Caixa respondeu sem o último concurso",
        "a Caixa respondeu com um erro",
    }


def test_instantes_no_fuso_institucional():
    situacao = _situacao("6116")
    assert "03/11/2026 às 19:03" in c.mensagem(situacao, c.SOB_DEMANDA)
    registrado = c.registro(situacao, c.INFORMA)
    assert registrado["consultadaEm"] == CONSULTADA_EM.astimezone(ZONA).isoformat()
    assert registrado["consultadaEm"].endswith("-03:00")


# --- o registro ------------------------------------------------------------------------------


def test_o_registro_responde_as_seis_perguntas_e_nada_da_resposta_crua():
    """FR-3647 e FR-3648: só tipos JSON, e nada que tenha vindo do corpo da Caixa."""
    realizado = c.registro(_situacao("5000"), c.IMPEDE)
    assert realizado == {
        "fonte": LF,
        "referencia": "5000",
        "consultadaEm": "2026-11-03T19:03:00-03:00",
        "ultimo": 6114,
        "ultimoEm": "2026-11-01",
        "realizadaEm": "2015-08-26",
        "situacao": c.REALIZADO,
        "conclusiva": True,
        "decisao": "RECUSOU",
        "motivo": "",
    }
    inconclusivo = c.registro(
        _situacao("6116", c.ConsultaDoUltimo(None, c.SEM_RESPOSTA_A_TEMPO)), c.ADVERTE
    )
    assert inconclusivo["conclusiva"] is False
    assert inconclusivo["decisao"] == "PROSSEGUIU_COM_ADVERTENCIA"
    assert inconclusivo["motivo"] == "a Caixa não respondeu a tempo"
    assert inconclusivo["ultimo"] is None
    assert c.registro(_situacao("6116"), c.INFORMA)["decisao"] == "PROSSEGUIU"
