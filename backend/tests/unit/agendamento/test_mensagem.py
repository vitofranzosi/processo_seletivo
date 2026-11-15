"""O texto do aviso de agenda (167, T067, FR-7231, FR-7244, US4 cenário 4).

Os campos da FR-7231 nos três textos — publicação, remarcação e inclusão —; o endereço da sala só na
forma remota, e o de uma pessoa só; a banca só com mais de uma; e nada de CPF, e-mail ou Modalidade,
que a função nem recebe.
"""

from datetime import datetime

import pytest

from processo_seletivo.agendamento.domain import mensagem, nomes
from processo_seletivo.agendamento.domain.horarios import zona

INICIO = datetime(2026, 11, 24, 14, 0, tzinfo=zona())


def _corpo(**mudancas):
    valores = {
        "nome": "Maria Souza",
        "protocolo": "INS-2026-0007",
        "etapa": "Entrevista",
        "edital": "Edital 26/2026",
        "inicio": INICIO,
        "duracao": 20,
        "banca": "Banca 2",
        "forma": nomes.REMOTA,
        "acesso": "https://sala.exemplo/2",
        "orientacoes": "Tenha o documento com foto.",
        "varias": True,
        **mudancas,
    }
    return mensagem.corpo(**valores)


@pytest.mark.parametrize("especie", [nomes.PUBLICACAO, nomes.REMARCACAO, nomes.INCLUSAO])
def test_os_campos_da_fr_7231_em_cada_texto(especie):
    corpo = _corpo(especie=especie)
    assert "Olá, Maria." in corpo
    assert "24/11/2026" in corpo
    assert "14:00" in corpo
    assert "duração prevista de 20 minutos" in corpo
    assert "Banca: Banca 2" in corpo
    assert "Sala virtual: https://sala.exemplo/2" in corpo
    assert "Orientações: Tenha o documento com foto." in corpo
    assert "Inscrição INS-2026-0007." in corpo
    assert "O que vale é a agenda publicada" in corpo


def test_a_remarcacao_diz_que_o_anterior_nao_vale_mais():
    corpo = _corpo(especie=nomes.REMARCACAO)
    assert "remarcou o seu horário" in corpo
    assert "O horário anterior não vale mais" in corpo
    assert "não vale mais" not in _corpo(especie=nomes.PUBLICACAO)
    assert "não vale mais" not in _corpo(especie=nomes.INCLUSAO)
    assert mensagem.assunto("Entrevista", "Edital 26/2026", nomes.REMARCACAO).startswith(
        "Seu horário mudou"
    )


def test_presencial_leva_o_local_e_nunca_sala():
    corpo = _corpo(forma=nomes.PRESENCIAL, acesso="Sala 12, bloco B")
    assert "Local: Sala 12, bloco B" in corpo
    assert "Sala virtual" not in corpo


def test_com_uma_banca_o_nome_dela_nao_aparece():
    assert "Banca:" not in _corpo(varias=False)


def test_o_texto_nao_tem_cpf_email_nem_modalidade():
    corpo = _corpo()
    for proibido in ("111.444.777-35", "@exemplo", "PPI", "Modalidade"):
        assert proibido not in corpo
