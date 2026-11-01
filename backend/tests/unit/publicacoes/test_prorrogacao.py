"""A regra da prorrogação, presa antes de sair do relatório do Edital (111, T002).

Ela vivia em linha em `fatos_do_edital` (099), e nenhum teste a prendia isolada: as suítes do
relatório a exercitam por cenário, com datas inteiras. O kit de divulgação passa a lê-la também, e a
revisão da 111 atribuiu a ela um defeito — "erra quando só a hora muda" — que era do texto da POC, e
não dela. Este arquivo diz o que ela é, para que a movimentação não a mude sem ninguém ver.
"""

from processo_seletivo.publicacoes.application.selectors import prorrogacao


def _conteudo(fim, *, designado=True):
    return {
        "schedule": [
            {"description": "Outro Evento", "endAt": "2026-12-01T12:00:00-03:00"},
            {
                "description": "Inscrições",
                "isRegistrationPeriod": designado,
                "startAt": "2026-11-01T09:00:00-03:00",
                "endAt": fim,
            },
        ]
    }


def test_termino_posterior_e_prorrogacao():
    lida = prorrogacao(
        _conteudo("2026-11-21T23:59:00-03:00"), _conteudo("2026-11-26T23:59:00-03:00")
    )
    assert lida.prorrogado
    assert lida.termino_original.isoformat() == "2026-11-21T23:59:00-03:00"
    assert lida.termino_vigente.isoformat() == "2026-11-26T23:59:00-03:00"


def test_adiamento_so_da_hora_ja_e_prorrogacao():
    """A comparação é entre instantes: o mesmo dia, mais tarde, é prorrogação."""
    lida = prorrogacao(
        _conteudo("2026-11-21T12:00:00-03:00"), _conteudo("2026-11-21T23:59:00-03:00")
    )
    assert lida.prorrogado


def test_termino_igual_ou_anterior_nao_e_prorrogacao():
    igual = _conteudo("2026-11-21T23:59:00-03:00")
    assert not prorrogacao(igual, igual).prorrogado
    antecipado = prorrogacao(
        _conteudo("2026-11-21T23:59:00-03:00"), _conteudo("2026-11-20T23:59:00-03:00")
    )
    assert not antecipado.prorrogado


def test_sem_termino_ou_sem_periodo_de_um_lado_nao_e_prorrogacao():
    sem_fim = _conteudo(None)
    com_fim = _conteudo("2026-11-21T23:59:00-03:00")
    assert not prorrogacao(sem_fim, com_fim).prorrogado
    assert not prorrogacao(com_fim, sem_fim).prorrogado
    assert not prorrogacao(
        _conteudo(com_fim["schedule"][1]["endAt"], designado=False), com_fim
    ).prorrogado
    assert not prorrogacao(None, com_fim).prorrogado
