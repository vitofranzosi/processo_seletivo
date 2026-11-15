"""O documento PDF de um ato da agenda (167, T086, FR-7224, FR-7226, SC-2399, `D-012`).

O texto desenhado diz o que o conteúdo diz — a Etapa, o dia, os horários, as pessoas, as
orientações e a autoridade —, e nada que o conteúdo não tem: nem a sala, nem CPF, e-mail,
telefone, Modalidade ou motivo. Na Etapa restrita, só o protocolo. E o mesmo conteúdo dá o mesmo
arquivo.
"""

from datetime import UTC, date, datetime, time

from processo_seletivo.agendamento.domain import nomes
from processo_seletivo.agendamento.domain.conteudo import Item, compor
from processo_seletivo.agendamento.domain.horarios import zona
from processo_seletivo.agendamento.infrastructure.documento import render_agenda_pdf
from tests.interface.test_fluxo import texto_de_pdf_bytes

SALA = "https://sala.exemplo/secreta-123"
SEG = date(2026, 11, 23)


def _instante(hora, minuto=0):
    return datetime.combine(SEG, time(hora, minuto), tzinfo=zona())


def _conteudo(*, restrita=False, forma=nomes.REMOTA, bancas=(("Banca 1", SALA),)):
    return compor(
        unidade={"cabecalho": ["Centro de Referência"], "local": "", "sigla": "Cefor", "nome": ""},
        edital="Edital 146/2025",
        etapa="Entrevista",
        publicado_em=datetime(2026, 11, 20, 13, 0, tzinfo=UTC),
        signatario={"nome": "Maria Diretora", "cargo": "Diretora-Geral", "atoDeNomeacao": ""},
        veiculo=nomes.VEICULO_GPS,
        veiculo_detalhe="item 7.2 do Edital",
        forma=forma,
        duracao=10,
        bancas=list(bancas),
        itens=[
            Item(_instante(8), _instante(8, 10), bancas[0][0], "Beatriz Souza", "INS-2026-0002"),
            Item(_instante(9), _instante(9, 10), bancas[-1][0], "Carla Dias", "INS-2026-0003"),
        ],
        restrita=restrita,
        orientacoes="Tenha o documento com foto.",
    )


def test_o_documento_diz_o_que_o_conteudo_diz():
    texto = texto_de_pdf_bytes(render_agenda_pdf(_conteudo()))

    for trecho in (
        "AGENDA DA ETAPA",
        "Edital 146/2025",
        "Entrevista",
        "Segunda-feira, 23/11/2026",
        "08:00",
        "09:00",
        "Beatriz Souza",
        "INS-2026-0002",
        "Tenha o documento com foto.",
        "Maria Diretora",
        "item 7.2 do Edital",
        "SHA-256",
    ):
        assert trecho in texto, trecho


def test_nada_de_sala_dado_pessoal_ou_motivo():
    texto = texto_de_pdf_bytes(render_agenda_pdf(_conteudo()))

    for proibido in (SALA, "secreta", "111.444.777-35", "@exemplo", "(27)", "PPI", "Motivo"):
        assert proibido not in texto, proibido


def test_na_etapa_restrita_so_o_protocolo():
    texto = texto_de_pdf_bytes(render_agenda_pdf(_conteudo(restrita=True)))

    assert "INS-2026-0002" in texto and "INS-2026-0003" in texto
    assert "Beatriz" not in texto and "Carla" not in texto


def test_o_local_presencial_entra_e_a_banca_com_mais_de_uma():
    bancas = (("Sala 101", "Bloco B, sala 101"), ("Sala 102", "Bloco B, sala 102"))
    texto = texto_de_pdf_bytes(render_agenda_pdf(_conteudo(forma=nomes.PRESENCIAL, bancas=bancas)))

    assert "Sala 101: Bloco B, sala 101" in texto
    assert "Sala 102" in texto


def test_o_mesmo_conteudo_da_o_mesmo_arquivo():
    assert render_agenda_pdf(_conteudo()) == render_agenda_pdf(_conteudo())
