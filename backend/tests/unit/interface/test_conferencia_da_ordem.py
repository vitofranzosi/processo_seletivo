"""O resumo que a confirmação da ordem mostra sobre quem fica sem posição (126, FR-4035 a FR-4038).

Função pura sobre a proposta que a confirmação já calculou: nada de banco aqui.
"""

from processo_seletivo.interface.conferencia_da_ordem import resumo

ANALISE = "00000000-0000-4000-8000-0000000000a1"
ENTREVISTA = "00000000-0000-4000-8000-0000000000a2"
ETAPAS = {
    ANALISE: {"id": ANALISE, "name": "Análise curricular"},
    ENTREVISTA: {"id": ENTREVISTA, "name": "Entrevista"},
}
MARCO = {"stages": [ANALISE, ENTREVISTA]}
MOTIVO = "Sem pontuação nas Etapas enumeradas: Análise curricular, Entrevista."


def _sem(protocolo, pontuacoes=None, consequencia="", motivo=MOTIVO):
    return {
        "inscricao_id": protocolo,
        "protocolo": protocolo,
        "pontuacoes": pontuacoes or {},
        "consequencia": consequencia,
        "motivo": motivo,
    }


def _proposta(posicoes=(), sem_posicao=()):
    return {
        "marco": MARCO,
        "etapas": ETAPAS,
        "posicoes": list(posicoes),
        "sem_posicao": list(sem_posicao),
    }


def test_sem_nenhum_resultado_cada_etapa_tem_a_contagem_e_o_destaque():
    """O Edital 91: doze inscrições, nenhuma avaliação."""
    lido = resumo(_proposta(sem_posicao=[_sem(f"INS-{n}") for n in range(12)]))

    assert lido["nenhuma_com_resultado"] is True
    assert lido["sem_resultado"] == 12
    assert lido["consideradas"] == 12
    assert lido["por_etapa"] == [("Análise curricular", 12), ("Entrevista", 12)]


def test_resultado_parcial_conta_so_quem_falta_e_so_na_etapa_que_falta():
    completo = {"posicao": 1, "pontuacoes": {ANALISE: "9", ENTREVISTA: "8"}}
    so_analise = _sem("INS-2", pontuacoes={ANALISE: "7"})

    lido = resumo(_proposta(posicoes=[completo], sem_posicao=[so_analise]))

    assert lido["nenhuma_com_resultado"] is False
    assert lido["sem_resultado"] == 1
    assert lido["consideradas"] == 2
    assert lido["por_etapa"] == [("Entrevista", 1)]


def test_a_eliminada_nao_conta_como_sem_resultado():
    """FR-4038: foi o resultado que a tirou da ordem."""
    eliminada = _sem(
        "INS-3",
        pontuacoes={ANALISE: None},
        consequencia="ELIMINADA",
        motivo="Documentação insuficiente",
    )

    lido = resumo(_proposta(sem_posicao=[eliminada]))

    assert lido["sem_resultado"] == 0
    assert lido["nenhuma_com_resultado"] is False
    assert lido["grupos"] == [
        {
            "motivo": "Documentação insuficiente",
            "consequencia": "ELIMINADA",
            "protocolos": ["INS-3"],
        }
    ]


def test_a_decisoria_com_resultado_sem_pontuacao_conta_como_com_resultado():
    """A chave existe sempre que há Resultado vigente; o motivo gravado diria a mais."""
    porta = _sem("INS-4", pontuacoes={ANALISE: "9", ENTREVISTA: None})

    lido = resumo(_proposta(sem_posicao=[porta]))

    assert lido["sem_resultado"] == 0
    assert lido["por_etapa"] == []


def test_os_grupos_juntam_o_mesmo_motivo_na_ordem_em_que_aparecem():
    lido = resumo(
        _proposta(
            sem_posicao=[
                _sem("INS-1"),
                _sem("INS-2", consequencia="ELIMINADA", motivo="Fora do prazo"),
                _sem("INS-3"),
            ]
        )
    )

    assert [(g["motivo"], g["protocolos"]) for g in lido["grupos"]] == [
        (MOTIVO, ["INS-1", "INS-3"]),
        ("Fora do prazo", ["INS-2"]),
    ]


def test_todos_com_resultado_nao_ha_aviso():
    lido = resumo(_proposta(posicoes=[{"posicao": 1, "pontuacoes": {ANALISE: "9"}}]))

    assert lido["sem_resultado"] == 0
    assert lido["nenhuma_com_resultado"] is False


def test_universo_vazio_nao_e_nenhuma_com_resultado():
    """Ninguém concorreu: a ordem vazia é Feito (049), e não falta de avaliação."""
    lido = resumo(_proposta())

    assert lido["consideradas"] == 0
    assert lido["nenhuma_com_resultado"] is False
