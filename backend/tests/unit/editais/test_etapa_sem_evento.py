"""A Etapa sem Evento é aviso de composição, e só da publicação (045, `FR-739`, `UX-086`).

Era sinal da Atenção — o `UX-001` —, e apontava para uma Retificação que não alcança o vínculo:
`scheduleEventId` é estrutural. Seis dos quinze sinais do gestor, em 20/09. O fato continua dito,
na superfície onde tem remédio.
"""

from processo_seletivo.editais.domain.validation import (
    ATO_DE_PUBLICACAO,
    ATO_DE_RETIFICACAO,
    ETAPA_SEM_EVENTO,
    Severity,
    blocking_findings,
    validate_for_publication,
)

ETAPA = "00000000-0000-0000-0000-000000000901"
EVENTO = "00000000-0000-0000-0000-000000000902"


def _conteudo(vinculo):
    return {
        "schemaVersion": 17,
        "schedule": [{"id": EVENTO, "type": "MARCO", "description": "Prova"}],
        "stages": [{"id": ETAPA, "name": "Prova didática", "order": 1, "scheduleEventId": vinculo}],
    }


def _da_etapa(achados):
    return [achado for achado in achados if achado.code == ETAPA_SEM_EVENTO]


def test_a_etapa_sem_evento_e_aviso_na_publicacao():
    achados = _da_etapa(validate_for_publication(_conteudo(None), ato=ATO_DE_PUBLICACAO))

    assert len(achados) == 1
    assert achados[0].severity == Severity.WARNING
    assert achados[0].path == f"/stages/id={ETAPA}/scheduleEventId"
    # Dita nesses termos, e nunca como atraso ou espera (`UX-086`).
    mensagem = achados[0].message.lower()
    for proibido in ("atras", "aguard", "pendente", "%"):
        assert proibido not in mensagem


def test_a_etapa_vinculada_nao_produz_o_aviso():
    assert _da_etapa(validate_for_publication(_conteudo(EVENTO))) == []


def test_na_retificacao_o_aviso_nao_aparece():
    """O vínculo não se retifica: ali o aviso seria o beco que a `D-003` tira da Atenção."""
    assert _da_etapa(validate_for_publication(_conteudo(None), ato=ATO_DE_RETIFICACAO)) == []


def test_o_aviso_nunca_impede_e_tem_codigo_proprio():
    """Publicável e legítimo (`022`, `FR-026`) — e o código não coincide com o de impeditivo nenhum.

    Com código de impeditivo, `advertencias_do_ato` o descartaria, e o invariante da declaração
    única reprovaria.
    """
    achados = validate_for_publication(_conteudo(None))

    assert all(achado.code != ETAPA_SEM_EVENTO for achado in blocking_findings(achados))
    assert ETAPA_SEM_EVENTO not in {achado.code for achado in blocking_findings(achados)}
